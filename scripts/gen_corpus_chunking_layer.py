#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a derived, additive text-chunking layer over the unified corpus index.

Purpose
-------
`data/corpus_unified_index/corpus_unified_llm_index.jsonl` is a deterministic
lexical/keyword retrieval index (one record per article). It is not yet
"embeddings-ready": embedding models have effective context limits, and Saudi
legal articles vary hugely in length -- most are one or two sentences, but a
minority (e.g. customs_regulation Article 1's أولاً..ثامناً valuation
methodology, or several environmental/labor/zakat Article 1's) run to
thousands of words.

This script produces a purely mechanical TEXT SEGMENTATION layer on top of the
unified index: one chunk per article for the overwhelming majority of
records, and multiple ordered, overlapping, sentence-boundary-respecting
chunks for the minority that exceed the chosen target size. It performs NO
summarization, NO translation, NO re-derivation, and -- critically -- NO
embedding/vector computation of any kind. It is read-only over the unified
index and every other corpus input.

Chunk sizing is WORD-based, not tokenizer-based: this corpus does not commit
to a specific embedding provider/model, so chunk boundaries are deliberately
computed in whitespace-delimited Arabic words rather than any particular
model's token counts. Computing actual embeddings is out of scope for this
deliverable; this is the step immediately before an embeddings pipeline would
run.

Parameter justification (see docstring at bottom of `build()` / summary JSON)
------------------------------------------------------------------------------
Surveyed the full 8,649-record unified index's word-count distribution:
    median = 38 words, p75 = 72, p90 = 128, p95 = 177, p97 = 222,
    p99 = 345, p99.9 = 799, max = 6,797 (customs_regulation Article 1).
Only 81 of 8,649 records (0.94%) exceed 350 words -- i.e. choosing 350 words
as both the "must this be split?" threshold and the per-chunk target leaves
99.06% of the corpus as a single chunk = one article, matching the drafting
reality that Saudi statutory articles are usually short/medium, while still
capping chunk size in the embedding-friendly ~200-500 word band conventional
for RAG pipelines.

Read-only over its inputs; deterministic and idempotent over its output.
"""

from __future__ import annotations

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNIFIED_INDEX = os.path.join(ROOT, "data", "corpus_unified_index", "corpus_unified_llm_index.jsonl")

OUT_DIR = os.path.join(ROOT, "data", "corpus_chunking_layer")
CHUNKS_OUT = os.path.join(OUT_DIR, "corpus_chunking_layer.jsonl")
SUMMARY_OUT = os.path.join(OUT_DIR, "corpus_chunking_layer_summary.json")

# ---------------------------------------------------------------------------
# Chunking parameters (word-based; NOT tied to any embedding model's tokenizer)
# ---------------------------------------------------------------------------
# An article at or below this word count is NEVER split: one article = one
# chunk. This threshold doubles as the *target* size for chunks produced when
# an article does need to be split (see module docstring for the corpus
# length-distribution evidence backing this number: ~99.06% of records are
# at or under this size).
CHUNK_TARGET_WORDS = 350

# Overlap (in words) carried from the tail of one chunk into the head of the
# next, so no clause is stranded at a chunk boundary. ~20% of the target.
CHUNK_OVERLAP_WORDS = 70

# Absolute ceiling no chunk may ever exceed. Gives limited slack over the
# target so a single indivisible sentence/clause is not forced to shed words;
# oversized atoms are further split (comma-level, then hard word-boundary
# level as a last resort) to stay under this ceiling.
CHUNK_HARD_MAX_WORDS = 500

# Primary sentence/clause boundary characters (Arabic + Latin terminators).
# Splitting happens *after* the character, never mid-word, since these are
# punctuation, not part of any Arabic word token.
PRIMARY_BOUNDARY_CHARS = set(".!?؟؛\n")

# Secondary boundary characters, used only to further break an atom that by
# itself still exceeds CHUNK_HARD_MAX_WORDS words.
SECONDARY_BOUNDARY_CHARS = set("،,:")

TOKEN_RE = re.compile(r"\S+\s*", re.UNICODE)


def _word_count(s):
    return len(s.split())


def _split_on_chars_with_offsets(text, chars, base_offset=0):
    """Split text right after any character in `chars`, keeping offsets.

    Guarantees: concatenating all returned spans' text reproduces `text`
    exactly (no characters dropped, no re-ordering). Never splits inside a
    word because the split points are always punctuation characters.
    """
    spans = []
    start = 0
    for i, ch in enumerate(text):
        if ch in chars:
            end = i + 1
            if end > start:
                spans.append((base_offset + start, base_offset + end))
            start = end
    if start < len(text):
        spans.append((base_offset + start, base_offset + len(text)))
    return spans


def _hard_word_split_with_offsets(text, base_offset, max_words):
    """Last-resort split at whitespace boundaries only, capping word count.

    Used only when a punctuation-delimited atom still exceeds the hard max
    (e.g. a long run with no commas/periods). Splits strictly between
    whitespace-delimited tokens, so no word is ever cut.
    """
    tokens = list(TOKEN_RE.finditer(text))
    if not tokens:
        return [(base_offset, base_offset + len(text))] if text else []
    spans = []
    group_start_char = 0
    group_word_count = 0
    last_end = 0
    for tok in tokens:
        group_word_count += 1
        last_end = tok.end()
        if group_word_count >= max_words:
            spans.append((base_offset + group_start_char, base_offset + last_end))
            group_start_char = last_end
            group_word_count = 0
    if group_start_char < len(text):
        spans.append((base_offset + group_start_char, base_offset + len(text)))
    return spans


def _atomize(text):
    """Break article text into small, ordered, offset-tracked "atoms".

    An atom is the smallest unit we allow a chunk boundary to fall between.
    Atoms are produced by primary sentence/clause boundaries; any atom still
    over CHUNK_HARD_MAX_WORDS is recursively broken by secondary boundaries,
    then (last resort) by hard whitespace splitting. The concatenation of all
    atom texts, in order, is always character-identical to the input text.
    """
    primary_spans = _split_on_chars_with_offsets(text, PRIMARY_BOUNDARY_CHARS, base_offset=0)
    if not primary_spans and text:
        primary_spans = [(0, len(text))]

    atoms = []
    for (s, e) in primary_spans:
        piece = text[s:e]
        if _word_count(piece) <= CHUNK_HARD_MAX_WORDS:
            atoms.append((s, e))
            continue
        secondary_spans = _split_on_chars_with_offsets(piece, SECONDARY_BOUNDARY_CHARS, base_offset=s)
        if not secondary_spans:
            secondary_spans = [(s, e)]
        for (s2, e2) in secondary_spans:
            sub = text[s2:e2]
            if _word_count(sub) <= CHUNK_HARD_MAX_WORDS:
                atoms.append((s2, e2))
            else:
                atoms.extend(_hard_word_split_with_offsets(sub, s2, CHUNK_HARD_MAX_WORDS))
    return atoms


def _pack_atoms_into_chunks(text, atoms):
    """Greedily pack ordered atoms into overlapping chunks.

    Each chunk is a contiguous run of atoms (by original text offset). When a
    chunk would exceed CHUNK_TARGET_WORDS, it is closed off and a new chunk
    is opened, carrying over trailing atoms from the just-closed chunk worth
    up to CHUNK_OVERLAP_WORDS words, so consecutive chunks overlap and no
    clause is stranded at a boundary. Returns a list of
    (char_start, char_end, word_count, overlap_words_with_previous).
    """
    if not atoms:
        return []

    chunks = []
    cur_atoms = []  # list of (s, e, wc)
    cur_words = 0

    def close_chunk(overlap_words_with_previous):
        s = cur_atoms[0][0]
        e = cur_atoms[-1][1]
        wc = sum(a[2] for a in cur_atoms)
        chunks.append((s, e, wc, overlap_words_with_previous))

    pending_overlap = 0
    carry_count = 0   # leading atoms of cur_atoms that are duplicated overlap
    for (s, e) in atoms:
        piece_wc = _word_count(text[s:e])
        if cur_atoms and (cur_words + piece_wc) > CHUNK_TARGET_WORDS:
            close_chunk(pending_overlap)
            # carry trailing atoms as overlap seed for next chunk
            carry = []
            carry_words = 0
            for a in reversed(cur_atoms):
                if carry_words >= CHUNK_OVERLAP_WORDS:
                    break
                carry.insert(0, a)
                carry_words += a[2]
            cur_atoms = carry
            cur_words = carry_words
            pending_overlap = carry_words
            carry_count = len(carry)
        # Enforce the absolute ceiling. An atom may itself be as large as
        # CHUNK_HARD_MAX_WORDS, so seeding a chunk with carried overlap could
        # push it past the ceiling -- which is how nine chunks in the corpus
        # ended up between 501 and 572 words. Shed carried atoms (they are pure
        # duplication of the previous chunk's tail, so coverage is unaffected
        # and the chunks stay contiguous) until the atom fits.
        while carry_count > 0 and (cur_words + piece_wc) > CHUNK_HARD_MAX_WORDS:
            dropped = cur_atoms.pop(0)
            carry_count -= 1
            cur_words -= dropped[2]
            pending_overlap -= dropped[2]
        cur_atoms.append((s, e, piece_wc))
        cur_words += piece_wc

    if cur_atoms:
        close_chunk(pending_overlap)

    return chunks


def chunk_article_text(text):
    """Return ordered chunk spans for one article's text.

    If the article is at/under CHUNK_TARGET_WORDS, returns a single chunk
    spanning the whole text (article == chunk, per spec). Otherwise returns
    multiple overlapping chunks covering the full text with no gaps.
    """
    total_words = _word_count(text)
    if total_words == 0:
        return []
    if total_words <= CHUNK_TARGET_WORDS:
        return [(0, len(text), total_words, 0)]
    atoms = _atomize(text)
    return _pack_atoms_into_chunks(text, atoms)


def load_unified_index():
    rows = []
    with open(UNIFIED_INDEX, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def build():
    records = load_unified_index()
    chunk_rows = []
    multi_chunk_records = 0
    word_counts_per_record = []

    for r in records:
        text = r.get("text_ar") or ""
        spans = chunk_article_text(text)
        total_chunks = len(spans)
        word_counts_per_record.append(_word_count(text))
        if total_chunks > 1:
            multi_chunk_records += 1
        for idx, (s, e, wc, overlap_words) in enumerate(spans):
            chunk_text = text[s:e]
            chunk_rows.append({
                "chunk_id": "%s#c%02d" % (r["record_id"], idx),
                "source_record_id": r["record_id"],
                "corpus": r.get("corpus"),
                "law_id": r.get("law_id"),
                "law_component": r.get("law_component"),
                "law_title_ar": r.get("law_title_ar"),
                "article_number": r.get("article_number"),
                "article_path": r.get("article_path"),
                "llm_title_ar": r.get("llm_title_ar"),
                "retrieval_title_ar": r.get("retrieval_title_ar"),
                "keywords_ar": r.get("keywords_ar", []),
                "search_queries_ar": r.get("search_queries_ar", []),
                "chunk_index": idx,
                "total_chunks_for_this_article": total_chunks,
                "char_start": s,
                "char_end": e,
                "word_count": wc,
                "overlap_words_with_previous": overlap_words,
                "is_full_article": total_chunks == 1,
                "text_ar": chunk_text,
                "text_status": r.get("text_status"),
                "source_layer": r.get("source_layer"),
            })

    return records, chunk_rows, multi_chunk_records, word_counts_per_record


def _percentile(sorted_vals, p):
    if not sorted_vals:
        return 0
    idx = min(len(sorted_vals) - 1, int(len(sorted_vals) * p))
    return sorted_vals[idx]


def main():
    records, chunk_rows, multi_chunk_records, word_counts_per_record = build()

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(CHUNKS_OUT, "w", encoding="utf-8") as f:
        for c in chunk_rows:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    sorted_wc = sorted(word_counts_per_record)
    n = len(sorted_wc)
    chunk_word_counts = sorted(c["word_count"] for c in chunk_rows)

    distribution_stats = {
        "source_record_word_counts": {
            "n_records": n,
            "min": sorted_wc[0] if n else 0,
            "max": sorted_wc[-1] if n else 0,
            "mean": round(sum(sorted_wc) / n, 2) if n else 0,
            "median_p50": _percentile(sorted_wc, 0.50),
            "p75": _percentile(sorted_wc, 0.75),
            "p90": _percentile(sorted_wc, 0.90),
            "p95": _percentile(sorted_wc, 0.95),
            "p97": _percentile(sorted_wc, 0.97),
            "p99": _percentile(sorted_wc, 0.99),
            "p999": _percentile(sorted_wc, 0.999),
        },
        "records_exceeding_chunk_target_words": multi_chunk_records,
        "pct_records_exceeding_chunk_target_words": round(100.0 * multi_chunk_records / n, 3) if n else 0,
        "resulting_chunk_word_counts": {
            "n_chunks": len(chunk_word_counts),
            "min": chunk_word_counts[0] if chunk_word_counts else 0,
            "max": chunk_word_counts[-1] if chunk_word_counts else 0,
            "mean": round(sum(chunk_word_counts) / len(chunk_word_counts), 2) if chunk_word_counts else 0,
        },
    }

    top_split_examples = sorted(
        (r for r in records if _word_count(r.get("text_ar") or "") > CHUNK_TARGET_WORDS),
        key=lambda r: -_word_count(r.get("text_ar") or ""),
    )[:10]
    examples = [
        {
            "record_id": r["record_id"],
            "corpus": r["corpus"],
            "law_component": r.get("law_component"),
            "article_number": r.get("article_number"),
            "word_count": _word_count(r.get("text_ar") or ""),
        }
        for r in top_split_examples
    ]

    summary = {
        "layer": "CORPUS_CHUNKING_LAYER",
        "purpose": (
            "Additive, derived text-segmentation layer over the unified retrieval "
            "index, sized for feeding a future embedding pipeline. Chunk boundaries "
            "are computed in whitespace-delimited WORDS, deliberately NOT tied to "
            "any specific embedding model's tokenizer (this corpus does not commit "
            "to one embedding provider). No embeddings/vectors are computed anywhere "
            "in this layer or this generator -- that is a separate, later step. "
            "This is pure text segmentation, one step before an embeddings pipeline "
            "would run."
        ),
        "source_index": os.path.relpath(UNIFIED_INDEX, ROOT),
        "total_source_records": len(records),
        "total_chunks": len(chunk_rows),
        "source_records_needing_multiple_chunks": multi_chunk_records,
        "source_records_single_chunk": len(records) - multi_chunk_records,
        "pct_single_chunk_records": round(100.0 * (len(records) - multi_chunk_records) / len(records), 3) if records else 0,
        "parameters": {
            "chunk_target_words": CHUNK_TARGET_WORDS,
            "chunk_overlap_words": CHUNK_OVERLAP_WORDS,
            "chunk_hard_max_words": CHUNK_HARD_MAX_WORDS,
            "primary_boundary_chars": sorted(PRIMARY_BOUNDARY_CHARS),
            "secondary_boundary_chars": sorted(SECONDARY_BOUNDARY_CHARS),
            "justification": (
                "Surveyed word-count distribution across all %d unified-index "
                "records: median=%s, p75=%s, p90=%s, p95=%s, p97=%s, p99=%s words "
                "(see distribution_stats below). Choosing %d words as both the "
                "split threshold and per-chunk target means only %d records "
                "(%.2f%%) require splitting -- consistent with Saudi statutory "
                "drafting practice where articles are typically short/medium, "
                "while keeping split-chunk sizes in the conventional ~200-500 "
                "word band used by embedding/RAG pipelines. Overlap of %d words "
                "(20%% of target) prevents clauses from being stranded at a "
                "chunk boundary. Splitting prefers primary sentence/clause "
                "punctuation (. ! ? ؟ ؛ newline), falling back to "
                "secondary punctuation (، , :) and finally hard "
                "whitespace-boundary splitting only for an indivisible run that "
                "would otherwise exceed the %d-word hard ceiling -- a word "
                "boundary is never crossed at any splitting level."
            ) % (n, sorted_wc[len(sorted_wc)//2] if n else 0,
                 _percentile(sorted_wc, 0.75), _percentile(sorted_wc, 0.90),
                 _percentile(sorted_wc, 0.95), _percentile(sorted_wc, 0.97),
                 _percentile(sorted_wc, 0.99), CHUNK_TARGET_WORDS,
                 multi_chunk_records, 100.0 * multi_chunk_records / n if n else 0,
                 CHUNK_OVERLAP_WORDS, CHUNK_HARD_MAX_WORDS),
        },
        "distribution_stats": distribution_stats,
        "top_examples_requiring_split": examples,
        "embeddings_scope_note": (
            "Out of scope for this layer: no embedding model or vector-database "
            "call of any kind is made here. This generator only performs text "
            "segmentation (chunking) so that a later, separate embeddings step "
            "has appropriately-sized, traceable input units. Each chunk carries "
            "source_record_id, article_number, chunk_index and "
            "total_chunks_for_this_article so any future vector hit can be "
            "traced back to its full source article."
        ),
        "fields": [
            "chunk_id", "source_record_id", "corpus", "law_id", "law_component",
            "law_title_ar", "article_number", "article_path", "llm_title_ar",
            "retrieval_title_ar", "keywords_ar", "search_queries_ar",
            "chunk_index", "total_chunks_for_this_article", "char_start",
            "char_end", "word_count", "overlap_words_with_previous",
            "is_full_article", "text_ar", "text_status", "source_layer",
        ],
        "note": (
            "Derived, additive layer projected from corpus_unified_llm_index.jsonl. "
            "No legal text altered, summarized, translated, or re-derived -- "
            "char_start/char_end/text_ar exactly slice the source article's "
            "text_ar. Read-only over the unified index and all upstream track "
            "files. Arabic governs."
        ),
    }

    with open(SUMMARY_OUT, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("Wrote chunking layer: %d chunks from %d source records -> %s"
          % (len(chunk_rows), len(records), os.path.relpath(CHUNKS_OUT, ROOT)))
    print("  records needing >1 chunk: %d (%.3f%%)"
          % (multi_chunk_records, 100.0 * multi_chunk_records / len(records) if records else 0))


if __name__ == "__main__":
    main()
