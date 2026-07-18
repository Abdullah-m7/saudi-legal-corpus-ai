#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Structural validator for the corpus chunking layer.

Checks, independent of the generator's own internal logic:

  1. Every chunk's `source_record_id` exists in the unified index.
  2. For every multi-chunk article (and, trivially, a sample of single-chunk
     ones), concatenating that article's chunks in `chunk_index` order,
     stripping the documented `char_start`/`char_end` overlap between
     consecutive chunks, exactly reconstructs the source record's `text_ar`
     -- i.e. no silent truncation or data loss, every word survives somewhere
     in the chunk set.
  3. No chunk's `word_count` exceeds the documented `chunk_hard_max_words`
     ceiling (read from the summary JSON, not hardcoded twice).
  4. The generator is idempotent: re-running
     `scripts/gen_corpus_chunking_layer.py` into a scratch directory produces
     byte-identical output to what's committed under
     `data/corpus_chunking_layer/`.

This script is read-only over the unified index and the chunking layer,
except for the idempotency check, which invokes the generator against a
temporary output directory (never touching the real one) via a monkeypatched
OUT_DIR/CHUNKS_OUT/SUMMARY_OUT.

Exit code 0 + "PASS" line on success; non-zero + "FAIL" details otherwise.
"""

from __future__ import annotations

import filecmp
import importlib.util
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNIFIED_INDEX = os.path.join(ROOT, "data", "corpus_unified_index", "corpus_unified_llm_index.jsonl")
CHUNK_DIR = os.path.join(ROOT, "data", "corpus_chunking_layer")
CHUNKS_FILE = os.path.join(CHUNK_DIR, "corpus_chunking_layer.jsonl")
SUMMARY_FILE = os.path.join(CHUNK_DIR, "corpus_chunking_layer_summary.json")
GENERATOR = os.path.join(ROOT, "scripts", "gen_corpus_chunking_layer.py")

MULTI_CHUNK_SAMPLE_CAP = None  # None = validate ALL multi-chunk articles (cheap: <100 of them)
SINGLE_CHUNK_SAMPLE_SIZE = 300  # sample of single-chunk articles to sanity-check too


def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def check_source_record_ids_exist(unified_by_id, chunks, errors):
    missing = []
    for c in chunks:
        if c["source_record_id"] not in unified_by_id:
            missing.append(c["chunk_id"])
    if missing:
        errors.append(
            "%d chunk(s) reference a source_record_id not present in the "
            "unified index, e.g. %s" % (len(missing), missing[:5])
        )
    else:
        print("[OK] all %d chunks' source_record_id resolve into the unified index"
              % len(chunks))


def _reconstruct(chunks_sorted):
    """Reconstruct original text from ordered chunks using char_start/char_end
    overlap accounting. Returns the reconstructed string."""
    full = chunks_sorted[0]["text_ar"]
    for i in range(1, len(chunks_sorted)):
        prev = chunks_sorted[i - 1]
        cur = chunks_sorted[i]
        overlap_len = prev["char_end"] - cur["char_start"]
        if overlap_len > 0:
            full += cur["text_ar"][overlap_len:]
        else:
            # no overlap (or a gap, which would be a bug we want to catch by
            # comparing final reconstruction against the original below)
            full += cur["text_ar"]
    return full


def check_reconstruction(unified_by_id, by_record, errors):
    multi = {rid: cs for rid, cs in by_record.items() if len(cs) > 1}
    single = {rid: cs for rid, cs in by_record.items() if len(cs) == 1}

    checked_multi = 0
    failed_multi = []
    items = list(multi.items())
    if MULTI_CHUNK_SAMPLE_CAP:
        items = items[:MULTI_CHUNK_SAMPLE_CAP]
    for rid, cs in items:
        cs_sorted = sorted(cs, key=lambda c: c["chunk_index"])
        orig = unified_by_id[rid]["text_ar"]
        recon = _reconstruct(cs_sorted)
        checked_multi += 1
        if recon != orig:
            failed_multi.append(rid)
    if failed_multi:
        errors.append(
            "%d/%d multi-chunk article(s) failed full-text reconstruction, "
            "e.g. %s" % (len(failed_multi), checked_multi, failed_multi[:5])
        )
    else:
        print("[OK] all %d multi-chunk articles reconstruct byte-identically "
              "to their unified-index text_ar (accounting for documented "
              "char overlap)" % checked_multi)

    # Sanity-check a sample of single-chunk articles too (trivial case: the
    # one chunk's text must equal the article's full text exactly).
    sample_ids = list(single.keys())[:SINGLE_CHUNK_SAMPLE_SIZE]
    failed_single = []
    for rid in sample_ids:
        c = single[rid][0]
        orig = unified_by_id[rid]["text_ar"]
        if c["text_ar"] != orig or c["char_start"] != 0 or c["char_end"] != len(orig):
            failed_single.append(rid)
    if failed_single:
        errors.append(
            "%d/%d sampled single-chunk article(s) do not exactly equal their "
            "source text_ar, e.g. %s" % (len(failed_single), len(sample_ids), failed_single[:5])
        )
    else:
        print("[OK] sampled %d single-chunk articles match their source "
              "text_ar exactly" % len(sample_ids))

    return len(multi), checked_multi


def check_max_chunk_size(chunks, params, errors):
    hard_max = params["chunk_hard_max_words"]
    over = [(c["chunk_id"], c["word_count"]) for c in chunks if c["word_count"] > hard_max]
    if over:
        errors.append(
            "%d chunk(s) exceed the documented chunk_hard_max_words=%d, e.g. %s"
            % (len(over), hard_max, over[:5])
        )
    else:
        max_seen = max((c["word_count"] for c in chunks), default=0)
        print("[OK] no chunk exceeds chunk_hard_max_words=%d (max observed: %d words)"
              % (hard_max, max_seen))


def check_no_gaps_or_backwards_overlap(by_record, errors):
    """Additional structural sanity check: within one article's chunks,
    ordered by chunk_index, offsets must be monotonically non-decreasing and
    must not leave a gap (char_start of chunk i+1 must be <= char_end of
    chunk i, i.e. touching or overlapping, never a gap)."""
    bad = []
    for rid, cs in by_record.items():
        cs_sorted = sorted(cs, key=lambda c: c["chunk_index"])
        for i in range(1, len(cs_sorted)):
            prev, cur = cs_sorted[i - 1], cs_sorted[i]
            if cur["char_start"] > prev["char_end"]:
                bad.append(rid)
                break
    if bad:
        errors.append(
            "%d article(s) have a gap between consecutive chunks (char_start "
            "of one chunk begins after the previous chunk's char_end), e.g. %s"
            % (len(bad), bad[:5])
        )
    else:
        print("[OK] no gaps between consecutive chunks within any article")


def check_idempotent(errors):
    with tempfile.TemporaryDirectory() as tmp:
        spec = importlib.util.spec_from_file_location("gen_corpus_chunking_layer_check", GENERATOR)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        tmp_chunks = os.path.join(tmp, "corpus_chunking_layer.jsonl")
        tmp_summary = os.path.join(tmp, "corpus_chunking_layer_summary.json")
        mod.OUT_DIR = tmp
        mod.CHUNKS_OUT = tmp_chunks
        mod.SUMMARY_OUT = tmp_summary
        mod.main()

        chunks_match = filecmp.cmp(CHUNKS_FILE, tmp_chunks, shallow=False)

        # Compare summary JSON ignoring nothing -- it should be fully
        # deterministic too (no timestamps/random ids in this generator).
        summary_match = filecmp.cmp(SUMMARY_FILE, tmp_summary, shallow=False)

        if not chunks_match:
            errors.append("re-running the generator produced a DIFFERENT corpus_chunking_layer.jsonl (not idempotent)")
        if not summary_match:
            errors.append("re-running the generator produced a DIFFERENT corpus_chunking_layer_summary.json (not idempotent)")
        if chunks_match and summary_match:
            print("[OK] generator is idempotent: re-run output is byte-identical "
                  "to committed corpus_chunking_layer.jsonl and "
                  "corpus_chunking_layer_summary.json")


def main():
    errors = []

    if not os.path.exists(UNIFIED_INDEX):
        print("FAIL: unified index not found at %s" % UNIFIED_INDEX)
        sys.exit(1)
    if not os.path.exists(CHUNKS_FILE) or not os.path.exists(SUMMARY_FILE):
        print("FAIL: chunking layer not found -- run scripts/gen_corpus_chunking_layer.py first")
        sys.exit(1)

    unified_rows = load_jsonl(UNIFIED_INDEX)
    unified_by_id = {r["record_id"]: r for r in unified_rows}

    chunks = load_jsonl(CHUNKS_FILE)
    with open(SUMMARY_FILE, encoding="utf-8") as f:
        summary = json.load(f)
    params = summary["parameters"]

    by_record = {}
    for c in chunks:
        by_record.setdefault(c["source_record_id"], []).append(c)

    print("Loaded %d unified-index records, %d chunks (%d source records)"
          % (len(unified_rows), len(chunks), len(by_record)))

    check_source_record_ids_exist(unified_by_id, chunks, errors)
    check_max_chunk_size(chunks, params, errors)
    check_no_gaps_or_backwards_overlap(by_record, errors)
    n_multi, n_checked = check_reconstruction(unified_by_id, by_record, errors)
    check_idempotent(errors)

    # Cross-check: every unified-index record_id has at least one chunk, and
    # no chunk set is missing/short (total_chunks_for_this_article matches
    # actual count for that record).
    missing_records = [rid for rid in unified_by_id if rid not in by_record]
    if missing_records:
        errors.append("%d unified-index record(s) have NO chunk at all, e.g. %s"
                       % (len(missing_records), missing_records[:5]))
    else:
        print("[OK] every unified-index record has at least one chunk")

    mismatched_totals = []
    for rid, cs in by_record.items():
        declared = cs[0]["total_chunks_for_this_article"]
        if any(c["total_chunks_for_this_article"] != declared for c in cs) or declared != len(cs):
            mismatched_totals.append(rid)
    if mismatched_totals:
        errors.append("%d record(s) have a total_chunks_for_this_article that "
                       "doesn't match their actual chunk count, e.g. %s"
                       % (len(mismatched_totals), mismatched_totals[:5]))
    else:
        print("[OK] total_chunks_for_this_article is consistent with actual chunk counts")

    print()
    print("Multi-chunk source records: %d (validated reconstruction for %d of them)"
          % (n_multi, n_checked))

    if errors:
        print()
        print("FAIL:")
        for e in errors:
            print("  - " + e)
        sys.exit(1)

    print()
    print("PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
