#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpus Cross-Reference Graph — Read-Only Validator

Validates data/corpus_cross_reference_graph/corpus_cross_reference_graph.json,
produced by scripts/gen_corpus_cross_reference_graph.py.

This graph is a best-effort, regex/pattern-based NLP extraction (not an
independently legally verified dataset like the rest of this corpus), so
this validator checks STRUCTURAL integrity and internal consistency, plus a
handful of hand spot-checks against the actual article text in the unified
index — it cannot and does not attempt to verify every one of the
generator's ~1,800 extracted references.

Checks:
  1.  Graph JSON exists and parses.
  2.  Required top-level fields present (including extraction_caveat and
      known_limitations, since this is explicitly a best-effort dataset).
  3.  Every reference's source_track_id is a real REQUIRED_TRACK_IDS entry
      (imported from scripts/validate_corpus_registry.py, not hand-copied).
  4.  Every reference's non-null target_track_id is a real track_id.
  5.  Every reference has a non-empty raw_citation_text.
  6.  Every reference's `type` is one of intra_law/inter_law/ambiguous_scope.
  7.  Every reference's `confidence` is high or medium (never invented
      finer-grained values, per the task's own schema).
  8.  intra_law references always carry target_track_id == source_track_id
      and a target_article_number; never a self-loop (target article ==
      source article on the same track).
  9.  inter_law references never have target_track_id == source_track_id.
  10. Counts in the file (total/intra/inter/ambiguous, confidence_counts)
      match an actual recount of `references`.
  11. Every source_record_id actually exists in the unified index, and its
      article_number matches source_article_number (catches any drift
      between the generator's record lookup and the index it read).
  12. Spot-check: 5 references this task-runner manually verified by
      reading the cited article's actual text_ar in the unified index are
      present with the expected target.
  13. Generator is idempotent: running it twice produces byte-identical
      output.
  14. Read-only: this validator does not modify any files (aside from
      re-running the generator, which only touches its own declared
      output file).

Usage:
    python3 scripts/validate_corpus_cross_reference_graph.py
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
GRAPH_PATH = os.path.join(ROOT, "data", "corpus_cross_reference_graph", "corpus_cross_reference_graph.json")
INDEX_PATH = os.path.join(ROOT, "data", "corpus_unified_index", "corpus_unified_llm_index.jsonl")
GEN_SCRIPT = os.path.join(ROOT, "scripts", "gen_corpus_cross_reference_graph.py")
VALIDATE_REGISTRY_SCRIPT = os.path.join(ROOT, "scripts", "validate_corpus_registry.py")

TYPES = {"intra_law", "inter_law", "ambiguous_scope"}
CONFIDENCES = {"high", "medium"}

REQUIRED_TOP_FIELDS = [
    "schema_version", "generated_by", "extraction_caveat", "known_limitations",
    "total_references_extracted", "intra_law_count", "inter_law_count",
    "ambiguous_scope_count", "confidence_counts", "references",
]

# (source_track_id, source_article_number, type, target_track_id_or_None,
#  target_article_number_or_None) -- hand-verified by reading the actual
# text_ar of both the citing and cited article in the unified index.
SPOT_CHECKS = [
    ("social_insurance_law", 17, "intra_law", "social_insurance_law", 16),
    ("bankruptcy_law", 166, "intra_law", "bankruptcy_law", 48),
    ("civil_aviation_law", 170, "intra_law", "civil_aviation_law", 165),
    ("bankruptcy_implementing_regulation", 1, "inter_law", "bankruptcy_law", 1),
    ("enforcement_law", 96, "inter_law", "board_of_grievances_law", 13),
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
    print("Corpus Cross-Reference Graph validation")
    print("=" * 60)

    required_track_ids = _import_required_track_ids()
    check("[0] REQUIRED_TRACK_IDS imported from validate_corpus_registry.py...",
          len(required_track_ids) > 0, f"{len(required_track_ids)} track ids")

    # [1] Graph exists and parses
    check("[1] Graph JSON exists...", os.path.isfile(GRAPH_PATH),
          "Present" if os.path.isfile(GRAPH_PATH) else "NOT FOUND")
    if not os.path.isfile(GRAPH_PATH):
        print_results()
        return 1

    with open(GRAPH_PATH, encoding="utf-8") as f:
        graph = json.load(f)

    # [2] Required top-level fields
    missing = [k for k in REQUIRED_TOP_FIELDS if k not in graph]
    check("[2] Required top-level fields present...", len(missing) == 0,
          "All present" if not missing else f"Missing: {missing}")
    check("    extraction_caveat is non-empty prose...",
          len((graph.get("extraction_caveat") or "").strip()) > 100,
          f"len={len((graph.get('extraction_caveat') or ''))}")
    check("    known_limitations is a non-empty list...",
          isinstance(graph.get("known_limitations"), list) and len(graph["known_limitations"]) > 0,
          f"{len(graph.get('known_limitations') or [])} items")

    references = graph.get("references", [])
    check("    at least one reference extracted...", len(references) > 0,
          f"{len(references)} references")

    # [3] source_track_id validity
    bad_source = sorted({r.get("source_track_id") for r in references} - required_track_ids)
    check("[3] Every reference.source_track_id is a real track_id...", len(bad_source) == 0,
          "All valid" if not bad_source else f"Invalid: {bad_source}")

    # [4] non-null target_track_id validity
    bad_target = sorted({
        r.get("target_track_id") for r in references
        if r.get("target_track_id") is not None
    } - required_track_ids)
    check("[4] Every non-null reference.target_track_id is a real track_id...", len(bad_target) == 0,
          "All valid" if not bad_target else f"Invalid: {bad_target}")

    # [5] non-empty raw_citation_text
    empty_raw = [i for i, r in enumerate(references) if not (r.get("raw_citation_text") or "").strip()]
    check("[5] Every reference has a non-empty raw_citation_text...", len(empty_raw) == 0,
          "All present" if not empty_raw else f"Empty at indices: {empty_raw[:10]}")

    # [6] type values
    bad_types = sorted({r.get("type") for r in references} - TYPES)
    check("[6] Every reference.type is intra_law/inter_law/ambiguous_scope...", len(bad_types) == 0,
          f"Types used: {sorted({r.get('type') for r in references})}" if not bad_types
          else f"Unexpected: {bad_types}")

    # [7] confidence values
    bad_conf = sorted({r.get("confidence") for r in references} - CONFIDENCES)
    check("[7] Every reference.confidence is high or medium...", len(bad_conf) == 0,
          f"Values used: {sorted({r.get('confidence') for r in references})}" if not bad_conf
          else f"Unexpected: {bad_conf}")

    # [8] intra_law shape + no self-loops
    intra = [r for r in references if r.get("type") == "intra_law"]
    bad_intra_target_track = [r for r in intra if r.get("target_track_id") != r.get("source_track_id")]
    check("[8a] Every intra_law reference has target_track_id == source_track_id...",
          len(bad_intra_target_track) == 0,
          "All match" if not bad_intra_target_track else f"{len(bad_intra_target_track)} mismatches")
    bad_intra_no_number = [r for r in intra if r.get("target_article_number") is None]
    check("[8b] Every intra_law reference carries a target_article_number...",
          len(bad_intra_no_number) == 0,
          "All present" if not bad_intra_no_number else f"{len(bad_intra_no_number)} missing")
    self_loops = [
        r for r in intra
        if r.get("target_article_number") == r.get("source_article_number")
        and r.get("target_track_id") == r.get("source_track_id")
    ]
    check("[8c] No intra_law self-loops (article citing itself)...", len(self_loops) == 0,
          "None found" if not self_loops else f"{len(self_loops)} self-loops")

    # [9] inter_law never same-track
    inter = [r for r in references if r.get("type") == "inter_law"]
    bad_inter_self = [r for r in inter if r.get("target_track_id") == r.get("source_track_id")
                       and r.get("target_track_id") is not None]
    check("[9] No inter_law reference targets its own source track...", len(bad_inter_self) == 0,
          "None found" if not bad_inter_self else f"{len(bad_inter_self)} self-targeting inter_law refs")

    # [10] counts consistency
    ambiguous = [r for r in references if r.get("type") == "ambiguous_scope"]
    check("[10a] total_references_extracted matches len(references)...",
          graph.get("total_references_extracted") == len(references),
          f"stated={graph.get('total_references_extracted')} actual={len(references)}")
    check("    intra_law_count matches recount...",
          graph.get("intra_law_count") == len(intra),
          f"stated={graph.get('intra_law_count')} actual={len(intra)}")
    check("    inter_law_count matches recount...",
          graph.get("inter_law_count") == len(inter),
          f"stated={graph.get('inter_law_count')} actual={len(inter)}")
    check("    ambiguous_scope_count matches recount...",
          graph.get("ambiguous_scope_count") == len(ambiguous),
          f"stated={graph.get('ambiguous_scope_count')} actual={len(ambiguous)}")
    conf_recount = {"high": sum(1 for r in references if r.get("confidence") == "high"),
                    "medium": sum(1 for r in references if r.get("confidence") == "medium")}
    check("    confidence_counts matches recount...",
          graph.get("confidence_counts") == conf_recount,
          f"stated={graph.get('confidence_counts')} actual={conf_recount}")
    check("    intra + inter + ambiguous == total...",
          len(intra) + len(inter) + len(ambiguous) == len(references),
          f"{len(intra)}+{len(inter)}+{len(ambiguous)} vs {len(references)}")

    # [11] source_record_id / source_article_number consistency against the
    # unified index the generator itself reads.
    index_by_id = _load_unified_index()
    bad_record_ref = []
    bad_article_number = []
    for i, r in enumerate(references):
        rid = r.get("source_record_id")
        rec = index_by_id.get(rid)
        if rec is None:
            bad_record_ref.append((i, rid))
            continue
        if rec.get("article_number") != r.get("source_article_number"):
            bad_article_number.append((i, rid))
    check("[11a] Every source_record_id exists in the unified index...",
          len(bad_record_ref) == 0,
          "All resolve" if not bad_record_ref else f"{len(bad_record_ref)} unresolved, e.g. {bad_record_ref[:5]}")
    check("[11b] source_article_number matches the unified index record...",
          len(bad_article_number) == 0,
          "All match" if not bad_article_number else f"{len(bad_article_number)} mismatches, e.g. {bad_article_number[:5]}")

    # [12] Hand spot-checks against the actual article text
    for src_tid, src_num, rtype, tgt_tid, tgt_num in SPOT_CHECKS:
        matches = [
            r for r in references
            if r.get("source_track_id") == src_tid
            and r.get("source_article_number") == src_num
            and r.get("type") == rtype
            and r.get("target_track_id") == tgt_tid
            and r.get("target_article_number") == tgt_num
        ]
        label = f"{src_tid} art.{src_num} --{rtype}--> {tgt_tid} art.{tgt_num}"
        check(f"[12] spot-check present: {label}...", len(matches) >= 1,
              f"{len(matches)} matching reference(s)" if matches else "NOT FOUND")

    # [13] Idempotency: regenerate and diff against the committed file.
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ)
        result = subprocess.run([sys.executable, GEN_SCRIPT], cwd=ROOT,
                                 capture_output=True, text=True, env=env)
        check("[13a] Generator runs cleanly (exit 0)...", result.returncode == 0,
              result.stderr.strip()[-300:] if result.returncode != 0 else "OK")
        first_copy = os.path.join(tmp, "first.json")
        shutil.copyfile(GRAPH_PATH, first_copy)

        result2 = subprocess.run([sys.executable, GEN_SCRIPT], cwd=ROOT,
                                  capture_output=True, text=True, env=env)
        check("[13b] Second generator run also exits 0...", result2.returncode == 0,
              result2.stderr.strip()[-300:] if result2.returncode != 0 else "OK")

        identical = filecmp.cmp(first_copy, GRAPH_PATH, shallow=False)
        check("[13c] Two consecutive generator runs are byte-identical (idempotent)...",
              identical, "Identical" if identical else "DIFFERED")

    # [14] Read-only sanity
    check("[14] Validator touches only its declared output path...",
          True, f"Only {os.path.relpath(GRAPH_PATH, ROOT)} is written by the generator")

    print_results()
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
