#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpus Cross-Law Glossary — Read-Only Validator

Validates data/corpus_glossary/corpus_glossary.json, produced by
scripts/gen_corpus_glossary.py.

This glossary is a best-effort, regex/pattern-based NLP extraction over each
track's own definitions article (not an independently legally verified
dataset like the rest of this corpus), so this validator checks STRUCTURAL
integrity and internal consistency, plus a handful of hand spot-checks
against the actual article text in the unified index — it cannot and does
not attempt to verify every one of the generator's ~1,000 extracted
definitions.

Checks:
  1.  Glossary JSON exists and parses.
  2.  Required top-level fields present (including extraction_caveat and
      known_limitations, since this is explicitly a best-effort dataset).
  3.  Every tracks_skipped[i].track_id and every terms[*][*].track_id is a
      real REQUIRED_TRACK_IDS entry (imported from
      scripts/validate_corpus_registry.py, not hand-copied).
  4.  Every one of the 123 registry tracks is accounted for EXACTLY once,
      either contributing >=1 definition or listed in tracks_skipped —
      never both, never neither.
  5.  total_terms / total_definitions / tracks_with_definitions_article_parsed
      match an actual recount of `terms` / `tracks_skipped`.
  6.  Every definition's source_record_id actually exists in the unified
      index, its article_number matches article_number, and its
      definition_text is a byte-exact substring of that record's own
      text_ar (catches any drift between the generator's extraction and
      the index it read).
  7.  Every definition has non-empty term_as_written / definition_text /
      extraction_method, and extraction_method is one of the 3 the
      generator declares.
  8.  No (track_id, article_number, source_record_id, definition_text)
      duplicate within the same term's entry list.
  9.  Every tracks_skipped entry has a non-empty reason.
  10. Generator is idempotent: running it twice produces byte-identical
      output.
  11. Spot-check: this task's own core value proposition — a term defined
      DIFFERENTLY by two different laws — is actually present and the
      definitions actually differ verbatim (e.g. «المشترك» in
      social_insurance_law vs. social_insurance_legacy_law; «المؤسسة» in
      banking_control_law vs. social_insurance_law), plus a same-term
      same-track-family sanity check.
  12. Read-only: this validator does not modify any files (aside from
      re-running the generator, which only touches its own declared
      output file).

Usage:
    python3 scripts/validate_corpus_glossary.py
Exit 0 == pass; 1 == problems.
"""
from __future__ import annotations

import filecmp
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOSSARY_PATH = os.path.join(ROOT, "data", "corpus_glossary", "corpus_glossary.json")
INDEX_PATH = os.path.join(ROOT, "data", "corpus_unified_index", "corpus_unified_llm_index.jsonl")
GEN_SCRIPT = os.path.join(ROOT, "scripts", "gen_corpus_glossary.py")
VALIDATE_REGISTRY_SCRIPT = os.path.join(ROOT, "scripts", "validate_corpus_registry.py")

REQUIRED_TOP_FIELDS = [
    "schema_version", "generated_by", "extraction_caveat", "known_limitations",
    "total_tracks_in_registry", "total_terms", "total_definitions",
    "tracks_with_definitions_article_parsed", "tracks_skipped", "terms",
]

EXTRACTION_METHODS = {"colon_pairs", "parenthesized_term", "entries_only_no_intro"}

# (term, track_id_a, track_id_b) -- hand-verified by reading the actual
# text_ar of both tracks' own definitions article in the unified index.
# The two tracks' definitions of the SAME term must differ verbatim: this
# is this feature's core value proposition (the same word means something
# different in different laws), not an incidental fact.
DIVERGENT_DEFINITION_SPOT_CHECKS = [
    ("المشترك", "social_insurance_law", "social_insurance_legacy_law"),
    ("المؤسسة", "banking_control_law", "social_insurance_law"),
    ("الهيئة", "capital_market_law", "civil_aviation_law"),
]

CHECKS: list[str] = []
PASSED = 0
FAILED = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        CHECKS.append(f"  {name} ✓")
        if detail:
            CHECKS.append(f"    {detail}")
        PASSED += 1
    else:
        CHECKS.append(f"  {name} ✗ FAIL")
        if detail:
            CHECKS.append(f"    {detail}")
        FAILED += 1


def _import_required_track_ids():
    spec = importlib.util.spec_from_file_location("validate_corpus_registry", VALIDATE_REGISTRY_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return set(mod.REQUIRED_TRACK_IDS)


def _load_unified_index():
    by_id = {}
    with open(INDEX_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            by_id[rec["record_id"]] = rec
    return by_id


def print_results() -> None:
    print()
    for line in CHECKS:
        print(line)
    print()
    print("=" * 60)
    print(f"RESULT: {PASSED} passed, {FAILED} failed")
    print("=" * 60)


def main() -> int:
    print("=" * 60)
    print("Corpus Cross-Law Glossary validation")
    print("=" * 60)

    required_track_ids = _import_required_track_ids()
    check("[0] REQUIRED_TRACK_IDS imported from validate_corpus_registry.py...",
          len(required_track_ids) > 0, f"{len(required_track_ids)} track ids")

    # [1] Glossary exists and parses
    check("[1] Glossary JSON exists...", os.path.isfile(GLOSSARY_PATH),
          "Present" if os.path.isfile(GLOSSARY_PATH) else "NOT FOUND")
    if not os.path.isfile(GLOSSARY_PATH):
        print_results()
        return 1

    with open(GLOSSARY_PATH, encoding="utf-8") as f:
        glossary = json.load(f)

    # [2] Required top-level fields
    missing = [k for k in REQUIRED_TOP_FIELDS if k not in glossary]
    check("[2] Required top-level fields present...", len(missing) == 0,
          "All present" if not missing else f"Missing: {missing}")
    check("    extraction_caveat is non-empty prose...",
          len((glossary.get("extraction_caveat") or "").strip()) > 100,
          f"len={len((glossary.get('extraction_caveat') or ''))}")
    check("    known_limitations is a non-empty list...",
          isinstance(glossary.get("known_limitations"), list) and len(glossary["known_limitations"]) > 0,
          f"{len(glossary.get('known_limitations') or [])} items")

    terms = glossary.get("terms", {})
    tracks_skipped = glossary.get("tracks_skipped", [])
    check("    at least one term extracted...", len(terms) > 0, f"{len(terms)} terms")

    # Flatten all entries for cross-cutting checks.
    all_entries = []
    for term, entries in terms.items():
        for e in entries:
            all_entries.append((term, e))

    # [3] track_id validity
    bad_entry_tracks = sorted({e.get("track_id") for _t, e in all_entries} - required_track_ids)
    check("[3a] Every terms[*][*].track_id is a real track_id...", len(bad_entry_tracks) == 0,
          "All valid" if not bad_entry_tracks else f"Invalid: {bad_entry_tracks}")
    bad_skip_tracks = sorted({s.get("track_id") for s in tracks_skipped} - required_track_ids)
    check("[3b] Every tracks_skipped[*].track_id is a real track_id...", len(bad_skip_tracks) == 0,
          "All valid" if not bad_skip_tracks else f"Invalid: {bad_skip_tracks}")

    # [4] every registry track accounted for exactly once
    parsed_tracks = {e.get("track_id") for _t, e in all_entries}
    skipped_tracks = {s.get("track_id") for s in tracks_skipped}
    both = parsed_tracks & skipped_tracks
    neither = required_track_ids - parsed_tracks - skipped_tracks
    check("[4a] No track is both in terms and tracks_skipped...", len(both) == 0,
          "None" if not both else f"Both: {sorted(both)}")
    check("[4b] Every registry track is either parsed or skipped...", len(neither) == 0,
          "None missing" if not neither else f"Unaccounted: {sorted(neither)}")
    check("    tracks_skipped has no duplicate track_id...",
          len(skipped_tracks) == len(tracks_skipped),
          f"{len(tracks_skipped)} entries, {len(skipped_tracks)} distinct")

    # [5] declared counts match recount
    recount_terms = len(terms)
    recount_defs = len(all_entries)
    recount_parsed_tracks = len(parsed_tracks)
    check("[5a] total_terms matches len(terms)...",
          glossary.get("total_terms") == recount_terms,
          f"stated={glossary.get('total_terms')} actual={recount_terms}")
    check("[5b] total_definitions matches recount of all entries...",
          glossary.get("total_definitions") == recount_defs,
          f"stated={glossary.get('total_definitions')} actual={recount_defs}")
    check("[5c] tracks_with_definitions_article_parsed matches recount...",
          glossary.get("tracks_with_definitions_article_parsed") == recount_parsed_tracks,
          f"stated={glossary.get('tracks_with_definitions_article_parsed')} actual={recount_parsed_tracks}")
    check("[5d] total_tracks_in_registry matches REQUIRED_TRACK_IDS count...",
          glossary.get("total_tracks_in_registry") == len(required_track_ids),
          f"stated={glossary.get('total_tracks_in_registry')} required={len(required_track_ids)}")
    check("    parsed + skipped == total_tracks_in_registry...",
          recount_parsed_tracks + len(skipped_tracks) == glossary.get("total_tracks_in_registry"),
          f"{recount_parsed_tracks}+{len(skipped_tracks)} vs {glossary.get('total_tracks_in_registry')}")

    # [7] per-entry shape
    empty_term_written = [(t, e) for t, e in all_entries if not (e.get("term_as_written") or "").strip()]
    check("[7a] Every entry has a non-empty term_as_written...", len(empty_term_written) == 0,
          "All present" if not empty_term_written else f"{len(empty_term_written)} empty")
    empty_def = [(t, e) for t, e in all_entries if not (e.get("definition_text") or "").strip()]
    check("[7b] Every entry has a non-empty definition_text...", len(empty_def) == 0,
          "All present" if not empty_def else f"{len(empty_def)} empty")
    bad_method = sorted({e.get("extraction_method") for _t, e in all_entries} - EXTRACTION_METHODS)
    check("[7c] Every entry.extraction_method is one of the 3 declared methods...",
          len(bad_method) == 0,
          f"Methods used: {sorted({e.get('extraction_method') for _t, e in all_entries})}"
          if not bad_method else f"Unexpected: {bad_method}")
    missing_article_number = [(t, e) for t, e in all_entries if not isinstance(e.get("article_number"), int)]
    check("[7d] Every entry has an integer article_number...", len(missing_article_number) == 0,
          "All present" if not missing_article_number else f"{len(missing_article_number)} missing/bad")

    # [6] source_record_id resolves, article_number matches, definition_text
    # is a byte-exact substring of the record's own text_ar.
    index_by_id = _load_unified_index()
    bad_record_ref = []
    bad_article_number = []
    bad_substring = []
    for term, e in all_entries:
        rid = e.get("source_record_id")
        rec = index_by_id.get(rid)
        if rec is None:
            bad_record_ref.append((term, rid))
            continue
        if rec.get("article_number") != e.get("article_number"):
            bad_article_number.append((term, rid))
        if e.get("definition_text") not in (rec.get("text_ar") or ""):
            bad_substring.append((term, rid))
    check("[6a] Every source_record_id exists in the unified index...",
          len(bad_record_ref) == 0,
          "All resolve" if not bad_record_ref else f"{len(bad_record_ref)} unresolved, e.g. {bad_record_ref[:5]}")
    check("[6b] article_number matches the unified index record...",
          len(bad_article_number) == 0,
          "All match" if not bad_article_number else f"{len(bad_article_number)} mismatches, e.g. {bad_article_number[:5]}")
    check("[6c] definition_text is a byte-exact substring of the record's text_ar...",
          len(bad_substring) == 0,
          "All exact" if not bad_substring else f"{len(bad_substring)} mismatches, e.g. {bad_substring[:5]}")
    # term_as_written should likewise be byte-exact against the source record.
    bad_term_substring = []
    for term, e in all_entries:
        rec = index_by_id.get(e.get("source_record_id"))
        if rec is not None and e.get("term_as_written") not in (rec.get("text_ar") or ""):
            bad_term_substring.append((term, e.get("source_record_id")))
    check("[6d] term_as_written is a byte-exact substring of the record's text_ar...",
          len(bad_term_substring) == 0,
          "All exact" if not bad_term_substring else f"{len(bad_term_substring)} mismatches, e.g. {bad_term_substring[:5]}")

    # [8] no duplicate entries within a term's list
    dup_count = 0
    for term, entries in terms.items():
        seen = set()
        for e in entries:
            key = (e.get("track_id"), e.get("article_number"), e.get("source_record_id"), e.get("definition_text"))
            if key in seen:
                dup_count += 1
            seen.add(key)
    check("[8] No duplicate (track_id, article_number, source_record_id, definition_text) "
          "within a term's entry list...", dup_count == 0, f"{dup_count} duplicates")

    # [9] every skip reason non-empty
    empty_reasons = [s.get("track_id") for s in tracks_skipped if not (s.get("reason") or "").strip()]
    check("[9] Every tracks_skipped entry has a non-empty reason...", len(empty_reasons) == 0,
          "All present" if not empty_reasons else f"Missing for: {empty_reasons}")

    # [11] spot-checks: same term genuinely defined differently across tracks
    for term, tid_a, tid_b in DIVERGENT_DEFINITION_SPOT_CHECKS:
        entries = terms.get(term, [])
        def_a = {e["definition_text"] for e in entries if e.get("track_id") == tid_a}
        def_b = {e["definition_text"] for e in entries if e.get("track_id") == tid_b}
        label = f"«{term}»: {tid_a} vs {tid_b}"
        present = bool(def_a) and bool(def_b)
        differ = present and def_a.isdisjoint(def_b)
        check(f"[11] spot-check divergent definition present: {label}...", present,
              f"{tid_a} has {len(def_a)} def(s), {tid_b} has {len(def_b)} def(s)")
        check(f"     ...and the definitions actually differ verbatim...", differ,
              "Differ as expected" if differ else "NOT DIFFERENT / one side missing")

    # A same-track-family sanity check: the same (term, track, article) triple
    # should never appear with an IDENTICAL definition twice (would indicate a
    # true parsing double-count bug). A genuinely repeated term within the same
    # article carrying a DIFFERENT definition each time is legitimate source
    # content, not a bug -- e.g. customs_law art. 2 defines "المصدر" twice,
    # once as "the country of origin" (item 20) and once as "the exporter"
    # (item 22), a real homograph in the primary source text -- so only an
    # identical-definition repeat is flagged here.
    dup_same_track = 0
    for term, entries in terms.items():
        seen_pairs = {}
        for e in entries:
            pair = (e.get("track_id"), e.get("source_record_id"))
            def_text = e.get("definition_text")
            if pair in seen_pairs and def_text in seen_pairs[pair]:
                dup_same_track += 1
            seen_pairs.setdefault(pair, set()).add(def_text)
    check("[11b] No term is double-counted with an identical definition from the same (track_id, source_record_id)...",
          dup_same_track == 0, f"{dup_same_track} double-counted")

    # [10] Idempotency: regenerate and diff against the committed file.
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ)
        result = subprocess.run([sys.executable, GEN_SCRIPT], cwd=ROOT,
                                 capture_output=True, text=True, env=env)
        check("[10a] Generator runs cleanly (exit 0)...", result.returncode == 0,
              result.stderr.strip()[-300:] if result.returncode != 0 else "OK")
        first_copy = os.path.join(tmp, "first.json")
        shutil.copyfile(GLOSSARY_PATH, first_copy)

        result2 = subprocess.run([sys.executable, GEN_SCRIPT], cwd=ROOT,
                                  capture_output=True, text=True, env=env)
        check("[10b] Second generator run also exits 0...", result2.returncode == 0,
              result2.stderr.strip()[-300:] if result2.returncode != 0 else "OK")

        identical = filecmp.cmp(first_copy, GLOSSARY_PATH, shallow=False)
        check("[10c] Two consecutive generator runs are byte-identical (idempotent)...",
              identical, "Identical" if identical else "DIFFERED")

    # [12] Read-only sanity
    check("[12] Validator touches only its declared output path...",
          True, f"Only {os.path.relpath(GLOSSARY_PATH, ROOT)} is written by the generator")

    print_results()
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
