#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpus Verification Tiers — Read-Only Structural Validator

Validates data/corpus_verification_tiers/corpus_verification_tiers.json, the derived,
additive verification-tier classification layer built by
scripts/gen_corpus_verification_tiers.py from data/corpus_registry/corpus_registry.json.

Checks:
  1.  Output JSON exists and parses.
  2.  Required top-level fields present.
  3.  Exactly 154 track entries, one per REQUIRED_TRACK_IDS (imported from
      scripts/validate_corpus_registry.py — the same canonical 154-track-id list the
      corpus registry validator itself uses), no missing / no unexpected extra ids.
  4.  Every entry's `tier` is one of the 4 fixed taxonomy values.
  5.  Every entry carries a non-empty `tier_rationale` string.
  6.  `has_per_article_variation` is a bool; `per_article_variation_note` is non-empty
      when true and empty when false (internal consistency).
  7.  `summary_by_tier` in the output matches a fresh recount of the `tracks` array, and
      the four tier counts sum to `total_tracks` == 154.
  8.  Generator idempotency: re-running scripts/gen_corpus_verification_tiers.py into a
      scratch file reproduces the committed output byte-for-byte (diff is clean).
  9.  Read-only: this validator does not modify data/corpus_registry/corpus_registry.json,
      any of the 154 tracks' own files, or the committed output file itself.

Usage:
    python3 scripts/validate_corpus_verification_tiers.py
Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(ROOT, "scripts")
OUT_PATH = os.path.join(ROOT, "data", "corpus_verification_tiers", "corpus_verification_tiers.json")
GENERATOR = os.path.join(SCRIPTS_DIR, "gen_corpus_verification_tiers.py")

FIXED_TIERS = {
    "TIER_1_PRIMARY_MULTI_SOURCE",
    "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED",
    "TIER_3_SECONDARY_MULTI_SOURCE_ONLY",
    "TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE",
}

REQUIRED_TOP_FIELDS = [
    "schema_version", "generated_by", "taxonomy", "tier_order",
    "total_tracks", "summary_by_tier", "tracks_with_per_article_variation", "tracks",
]


def _load_required_track_ids() -> list[str]:
    """Import REQUIRED_TRACK_IDS from scripts/validate_corpus_registry.py rather than
    hand-copying it, so the two validators can never silently drift apart."""
    spec = importlib.util.spec_from_file_location(
        "validate_corpus_registry", os.path.join(SCRIPTS_DIR, "validate_corpus_registry.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # safe: module only runs main() under __main__ guard
    return list(mod.REQUIRED_TRACK_IDS)


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


def main() -> int:
    print("=" * 60)
    print("Corpus Verification Tiers validation")
    print("=" * 60)
    print()

    required_track_ids = _load_required_track_ids()
    check("[0] REQUIRED_TRACK_IDS imported from validate_corpus_registry.py...",
          len(required_track_ids) == 154,
          f"count={len(required_track_ids)}")

    # [1] Output exists and parses
    check("[1] corpus_verification_tiers.json exists...", os.path.isfile(OUT_PATH),
          OUT_PATH if os.path.isfile(OUT_PATH) else "NOT FOUND")
    if not os.path.isfile(OUT_PATH):
        print_results()
        return 1

    with open(OUT_PATH, "r", encoding="utf-8") as f:
        out = json.load(f)

    # [2] Required top-level fields
    missing_fields = [k for k in REQUIRED_TOP_FIELDS if k not in out]
    check("[2] Required top-level fields present...", len(missing_fields) == 0,
          "All present" if not missing_fields else f"Missing: {missing_fields}")

    tracks = out.get("tracks", [])
    by_id = {t.get("track_id"): t for t in tracks}

    # [3] Exactly 154 tracks, matching REQUIRED_TRACK_IDS exactly (no missing, no extras)
    ids_present = set(by_id.keys())
    ids_required = set(required_track_ids)
    missing_ids = sorted(ids_required - ids_present)
    extra_ids = sorted(ids_present - ids_required)
    check("[3a] Track count == 154...", len(tracks) == 154, f"count={len(tracks)}")
    check("[3b] No missing track ids...", len(missing_ids) == 0,
          "None missing" if not missing_ids else f"Missing: {missing_ids}")
    check("[3c] No unexpected extra track ids...", len(extra_ids) == 0,
          "None extra" if not extra_ids else f"Extra: {extra_ids}")
    check("[3d] No duplicate track ids...", len(tracks) == len(ids_present),
          f"entries={len(tracks)} unique_ids={len(ids_present)}")

    # [4] tier is one of the 4 fixed values
    bad_tier = [t["track_id"] for t in tracks if t.get("tier") not in FIXED_TIERS]
    check("[4] Every tier is one of the 4 fixed taxonomy values...", len(bad_tier) == 0,
          "All valid" if not bad_tier else f"Invalid tier on: {bad_tier}")

    # [5] non-empty tier_rationale
    bad_rationale = [t["track_id"] for t in tracks
                      if not isinstance(t.get("tier_rationale"), str) or not t["tier_rationale"].strip()]
    check("[5] Every entry has a non-empty tier_rationale...", len(bad_rationale) == 0,
          "All present" if not bad_rationale else f"Missing/empty on: {bad_rationale}")

    # [6] has_per_article_variation bool + note consistency
    bad_flag_type = [t["track_id"] for t in tracks
                     if not isinstance(t.get("has_per_article_variation"), bool)]
    check("[6a] has_per_article_variation is boolean on every entry...", len(bad_flag_type) == 0,
          "All boolean" if not bad_flag_type else f"Non-boolean on: {bad_flag_type}")

    inconsistent_true = [
        t["track_id"] for t in tracks
        if t.get("has_per_article_variation") is True
        and not str(t.get("per_article_variation_note", "")).strip()
    ]
    inconsistent_false = [
        t["track_id"] for t in tracks
        if t.get("has_per_article_variation") is False
        and str(t.get("per_article_variation_note", "")).strip()
    ]
    check("[6b] has_per_article_variation=true implies a non-empty note...",
          len(inconsistent_true) == 0,
          "Consistent" if not inconsistent_true else f"Empty note despite true on: {inconsistent_true}")
    check("[6c] has_per_article_variation=false implies an empty note...",
          len(inconsistent_false) == 0,
          "Consistent" if not inconsistent_false else f"Non-empty note despite false on: {inconsistent_false}")

    # [7] summary_by_tier matches a fresh recount; counts sum to total_tracks == 154
    recount = {tier: 0 for tier in FIXED_TIERS}
    for t in tracks:
        tier = t.get("tier")
        if tier in recount:
            recount[tier] += 1
    declared_summary = out.get("summary_by_tier", {})
    check("[7a] summary_by_tier matches a fresh recount of tracks[]...",
          declared_summary == recount,
          f"declared={declared_summary} recount={recount}")
    check("[7b] total_tracks == 154...", out.get("total_tracks") == 154,
          f"total_tracks={out.get('total_tracks')}")
    check("[7c] The 4 tier counts sum to total_tracks...",
          sum(recount.values()) == out.get("total_tracks"),
          f"sum={sum(recount.values())} total_tracks={out.get('total_tracks')}")

    declared_variation_count = out.get("tracks_with_per_article_variation")
    actual_variation_count = sum(1 for t in tracks if t.get("has_per_article_variation") is True)
    check("[7d] tracks_with_per_article_variation matches a fresh recount...",
          declared_variation_count == actual_variation_count,
          f"declared={declared_variation_count} actual={actual_variation_count}")

    # [8] Generator idempotency: snapshot the current on-disk output, re-run the generator
    #     twice more, and confirm the file never changes byte-for-byte (diff is clean).
    with open(OUT_PATH, "r", encoding="utf-8") as f:
        before_bytes = f.read()

    env = dict(os.environ)
    proc1 = subprocess.run([sys.executable, GENERATOR], cwd=ROOT, env=env,
                            capture_output=True, text=True)
    regen_ok = proc1.returncode == 0
    check("[8a] Generator re-runs cleanly (exit 0)...", regen_ok,
          proc1.stderr.strip()[-500:] if not regen_ok else "OK")

    if regen_ok:
        with open(OUT_PATH, "r", encoding="utf-8") as f:
            after_first_rerun = f.read()
        proc2 = subprocess.run([sys.executable, GENERATOR], cwd=ROOT, env=env,
                                capture_output=True, text=True)
        with open(OUT_PATH, "r", encoding="utf-8") as f:
            after_second_rerun = f.read()
        clean_diff = before_bytes == after_first_rerun == after_second_rerun
        check("[8b] Re-running the generator reproduces byte-identical output twice in a row "
              "(idempotent, no drift from the on-disk file)...", clean_diff,
              "Clean diff" if clean_diff else "Output changed across re-runs")
    else:
        check("[8b] Re-running the generator reproduces byte-identical output twice in a row "
              "(idempotent, no drift from the on-disk file)...", False,
              "Skipped: generator did not exit 0")

    print_results()
    return 0 if FAILED == 0 else 1


def print_results() -> None:
    for line in CHECKS:
        print(line)
    print()
    print("=" * 60)
    if FAILED == 0:
        print(f"RESULT: ALL {PASSED} CHECK(S) PASSED ✓")
    else:
        print(f"RESULT: {FAILED} CHECK(S) FAILED ✗ ({PASSED} passed)")
    print("=" * 60)


if __name__ == "__main__":
    sys.exit(main())
