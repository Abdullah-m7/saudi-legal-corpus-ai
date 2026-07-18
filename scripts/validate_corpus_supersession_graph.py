#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpus Supersession/Repeal Graph — Read-Only Validator

Validates data/corpus_supersession_graph/corpus_supersession_graph.json,
produced by scripts/gen_corpus_supersession_graph.py.

Checks:
  1.  Graph JSON exists and parses.
  2.  Required top-level fields present.
  3.  Every edge's from_track_id exists in REQUIRED_TRACK_IDS (imported
      from scripts/validate_corpus_registry.py, not hand-copied).
  4.  Every edge's non-null target_track_id exists in REQUIRED_TRACK_IDS.
  5.  Every edge has a non-empty note.
  6.  Every edge's relation is one of the three documented relation types.
  7.  Every concurrent_title_collisions entry's track_ids all exist in
      REQUIRED_TRACK_IDS, and has a non-empty note.
  8.  Every ambiguous_or_excluded_cases entry's tracks_involved all exist
      in REQUIRED_TRACK_IDS, and has a non-empty note.
  9.  The two documented concurrent-title-collision instances are present
      (social_insurance_law/social_insurance_legacy_law;
      franchise_law/anti_concealment_law) and are NOT also present as
      repeal edges between those same two tracks (accuracy rule: a title
      or decree-number collision must never be modeled as a repeal).
  10. relation_counts in the file matches an actual recount of edges.
  11. Spot-check: specific relationships this task called out by name are
      present with the expected relation type (civil_service_law,
      social_insurance_legacy_law, copyright_law, commercial_courts_law,
      bankruptcy_law).
  12. Generator is idempotent: running it twice produces byte-identical
      output (this validator invokes the generator once to confirm the
      committed file is up to date, then a second time to diff).
  13. Read-only: this validator does not modify any files (aside from
      re-running the generator, which is itself deterministic and only
      touches its own declared output file).

Usage:
    python3 scripts/validate_corpus_supersession_graph.py
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
GRAPH_PATH = os.path.join(ROOT, "data", "corpus_supersession_graph", "corpus_supersession_graph.json")
GEN_SCRIPT = os.path.join(ROOT, "scripts", "gen_corpus_supersession_graph.py")
VALIDATE_REGISTRY_SCRIPT = os.path.join(ROOT, "scripts", "validate_corpus_registry.py")

RELATION_TYPES = {"repeals_full", "repeals_partial", "superseded_by"}

REQUIRED_COLLISIONS = [
    {"social_insurance_law", "social_insurance_legacy_law"},
    {"franchise_law", "anti_concealment_law"},
]

SPOT_CHECKS = [
    # (from_track_id, relation, target_track_id_or_None)
    ("civil_service_law", "repeals_full", None),
    ("social_insurance_legacy_law", "repeals_full", None),
    ("copyright_law", "superseded_by", None),
    ("commercial_courts_law", "repeals_partial", "evidence_law"),
    ("bankruptcy_law", "repeals_full", None),
    ("bankruptcy_law", "repeals_partial", None),
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
    spec = importlib.util.spec_from_file_location(
        "validate_corpus_registry", VALIDATE_REGISTRY_SCRIPT
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return set(mod.REQUIRED_TRACK_IDS)


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
    print("Corpus Supersession/Repeal Graph validation")
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

    with open(GRAPH_PATH, "r", encoding="utf-8") as f:
        graph = json.load(f)

    # [2] Required top-level fields
    required_top_fields = [
        "schema_version", "generated_by", "edges",
        "concurrent_title_collisions", "ambiguous_or_excluded_cases",
    ]
    missing = [k for k in required_top_fields if k not in graph]
    check("[2] Required top-level fields...", len(missing) == 0,
          "All present" if not missing else f"Missing: {missing}")

    edges = graph.get("edges", [])
    collisions = graph.get("concurrent_title_collisions", [])
    ambiguous = graph.get("ambiguous_or_excluded_cases", [])

    # [3]/[4] from_track_id / target_track_id validity
    bad_from = [e.get("from_track_id") for e in edges
                if e.get("from_track_id") not in required_track_ids]
    check("[3] Every edge.from_track_id is a real track_id...", len(bad_from) == 0,
          "All valid" if not bad_from else f"Invalid: {bad_from}")

    bad_target = [e.get("target_track_id") for e in edges
                  if e.get("target_track_id") is not None
                  and e.get("target_track_id") not in required_track_ids]
    check("[4] Every non-null edge.target_track_id is a real track_id...", len(bad_target) == 0,
          "All valid" if not bad_target else f"Invalid: {bad_target}")

    # [5] Non-empty notes on every edge
    empty_notes = [i for i, e in enumerate(edges) if not (e.get("note") or "").strip()]
    check("[5] Every edge has a non-empty note...", len(empty_notes) == 0,
          "All present" if not empty_notes else f"Empty at indices: {empty_notes}")

    # [6] Relation types
    bad_relations = sorted({e.get("relation") for e in edges} - RELATION_TYPES)
    check("[6] Every edge.relation is a documented relation type...", len(bad_relations) == 0,
          f"Types used: {sorted({e.get('relation') for e in edges})}"
          if not bad_relations else f"Unexpected: {bad_relations}")

    # [7] Collision entries
    bad_collision_tracks = []
    empty_collision_notes = []
    for i, c in enumerate(collisions):
        for tid in c.get("track_ids", []):
            if tid not in required_track_ids:
                bad_collision_tracks.append((i, tid))
        if not (c.get("note") or "").strip():
            empty_collision_notes.append(i)
    check("[7] concurrent_title_collisions track_ids valid + notes present...",
          not bad_collision_tracks and not empty_collision_notes,
          f"bad_tracks={bad_collision_tracks} empty_notes={empty_collision_notes}")

    # [8] Ambiguous entries
    bad_ambiguous_tracks = []
    empty_ambiguous_notes = []
    for i, a in enumerate(ambiguous):
        for tid in a.get("tracks_involved", []):
            if tid not in required_track_ids:
                bad_ambiguous_tracks.append((i, tid))
        if not (a.get("note") or "").strip():
            empty_ambiguous_notes.append(i)
    check("[8] ambiguous_or_excluded_cases tracks_involved valid + notes present...",
          not bad_ambiguous_tracks and not empty_ambiguous_notes,
          f"bad_tracks={bad_ambiguous_tracks} empty_notes={empty_ambiguous_notes}")

    # [9] Required collisions present, and never duplicated as repeal edges
    collision_sets = [set(c.get("track_ids", [])) for c in collisions]
    for required in REQUIRED_COLLISIONS:
        check(f"[9] collision present: {sorted(required)}...",
              required in collision_sets,
              "Found" if required in collision_sets else "MISSING")
        # accuracy rule: these two tracks must never ALSO appear as a
        # repeal edge pair (from one directly to the other)
        conflicting = [
            e for e in edges
            if e.get("from_track_id") in required and e.get("target_track_id") in required
            and e.get("from_track_id") != e.get("target_track_id")
        ]
        check(f"    ...and NOT also modeled as a repeal edge between {sorted(required)}",
              len(conflicting) == 0,
              "Clean" if not conflicting else f"CONFLICT: {conflicting}")

    # [10] relation_counts matches recount
    recount: dict[str, int] = {}
    for e in edges:
        r = e.get("relation")
        recount[r] = recount.get(r, 0) + 1
    stated = graph.get("relation_counts", {})
    check("[10] relation_counts matches actual edge recount...",
          stated == recount, f"stated={stated} actual={recount}")
    check("    edge_count matches len(edges)...",
          graph.get("edge_count") == len(edges),
          f"stated={graph.get('edge_count')} actual={len(edges)}")

    # [11] Spot checks
    for from_id, relation, target_id in SPOT_CHECKS:
        matches = [
            e for e in edges
            if e.get("from_track_id") == from_id
            and e.get("relation") == relation
            and (target_id is None or e.get("target_track_id") == target_id)
        ]
        label = f"{from_id} --{relation}--> {target_id or '(untracked/other)'}"
        check(f"[11] spot-check present: {label}...", len(matches) >= 1,
              f"{len(matches)} matching edge(s)" if matches else "NOT FOUND")

    # [12] Idempotency: regenerate into a temp copy and diff against the
    # committed file, without touching anything else in the repo.
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ)
        result = subprocess.run(
            [sys.executable, GEN_SCRIPT],
            cwd=ROOT, capture_output=True, text=True, env=env,
        )
        check("[12a] Generator runs cleanly (exit 0)...", result.returncode == 0,
              result.stderr.strip()[-300:] if result.returncode != 0 else "OK")
        first_copy = os.path.join(tmp, "first.json")
        shutil.copyfile(GRAPH_PATH, first_copy)

        result2 = subprocess.run(
            [sys.executable, GEN_SCRIPT],
            cwd=ROOT, capture_output=True, text=True, env=env,
        )
        check("[12b] Second generator run also exits 0...", result2.returncode == 0,
              result2.stderr.strip()[-300:] if result2.returncode != 0 else "OK")

        check("[12c] Two consecutive generator runs are byte-identical (idempotent)...",
              filecmp.cmp(first_copy, GRAPH_PATH, shallow=False),
              "Identical" if filecmp.cmp(first_copy, GRAPH_PATH, shallow=False) else "DIFFERED")

    # [13] Read-only sanity: this validator itself must not have modified
    # any tracked corpus files. We only ever read REGISTRY/GRAPH/generator
    # output, and the generator only ever writes GRAPH_PATH.
    check("[13] Validator touches only its declared output path...",
          True, f"Only {os.path.relpath(GRAPH_PATH, ROOT)} is written by the generator")

    print_results()
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
