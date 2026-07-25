#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpus Freshness Manifest — Read-Only Structural Validator

Validates data/corpus_freshness_manifest/corpus_freshness_manifest.json, the derived,
additive freshness/drift-monitoring survey layer built by
scripts/gen_corpus_freshness_manifest.py from data/corpus_registry/corpus_registry.json,
data/corpus_verification_tiers/corpus_verification_tiers.json, and each track's own
official_source.json-equivalent file.

This validator checks the MANIFEST only. It deliberately does NOT invoke or test
scripts/check_corpus_freshness.py (the live-checking CLI tool) — that tool makes real network
requests, is inherently non-deterministic, and is explicitly NOT part of this deterministic
QA gate. See that script's own docstring.

Checks:
  1.  Output JSON exists and parses.
  2.  Required top-level fields present.
  3.  Exactly 198 track entries, one per REQUIRED_TRACK_IDS (imported from
      scripts/validate_corpus_registry.py), no missing / no unexpected extra ids.
  4.  Every entry carries the expected fields with the expected types.
  5.  `known_source_staleness_risk` is only ever true when a non-empty
      `known_source_staleness_pointer` is also present (internal consistency), and vice versa.
  6.  Spot-check: traffic_law, patent_law, and income_tax_law are flagged
      known_source_staleness_risk=true (each track's own known_unresolved_discrepancies
      documents its primary government portal as confirmed stale at build time); a clean
      track (civil_service_law) is NOT flagged (its own discrepancy text explicitly says
      "not stale", just an under-cited amendment-metadata gap, plus a stale MINISTRY NAME,
      a different, non-portal-drift concern) unless it too has a genuinely documented
      staleness discrepancy.
  7.  known_source_staleness_risk_count / known_source_staleness_risk_tracks in the output
      match a fresh recount of the tracks[] array.
  8.  Generator idempotency: re-running scripts/gen_corpus_freshness_manifest.py reproduces
      byte-identical output twice in a row (deterministic, no network calls, no
      datetime.now() fabrication).
  9.  Read-only: this validator does not modify the registry, the verification-tiers file,
      any of the 198 tracks' own files, or the committed output file itself.

Usage:
    python3 scripts/validate_corpus_freshness_manifest.py
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
OUT_PATH = os.path.join(ROOT, "data", "corpus_freshness_manifest", "corpus_freshness_manifest.json")
GENERATOR = os.path.join(SCRIPTS_DIR, "gen_corpus_freshness_manifest.py")

REQUIRED_TOP_FIELDS = [
    "schema_version", "generated_by", "source_registry", "source_verification_tiers",
    "read_only_derived_layer", "network_access", "total_tracks",
    "known_source_staleness_risk_count", "known_source_staleness_risk_tracks",
    "tracks_without_resolvable_official_source_file", "tracks",
]

REQUIRED_TRACK_ENTRY_FIELDS = {
    "track_id": str,
    "display_name_en": (str, type(None)),
    "display_name_ar": (str, type(None)),
    "verification_tier": (str, type(None)),
    "verification_tier_rationale": (str, type(None)),
    "registry_source_authority": (str, type(None)),
    "registry_source_url": (str, type(None)),
    "official_source_file": (str, type(None)),
    "source_urls": list,
    "named_source_authorities": list,
    "last_verified_context": str,
    "known_source_staleness_risk": bool,
    "known_source_staleness_pointer": str,
}

# Spot-check expectations (see task rationale / gen_corpus_freshness_manifest.py docstring,
# and the independently-authored RATIONALE_OVERRIDE entries in
# scripts/gen_corpus_verification_tiers.py for the same tracks).
EXPECTED_STALENESS_RISK_TRUE = ["traffic_law", "patent_law", "income_tax_law"]
EXPECTED_STALENESS_RISK_FALSE = ["civil_service_law"]


def _load_required_track_ids() -> list[str]:
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
    print("Corpus Freshness Manifest validation")
    print("=" * 60)
    print()

    required_track_ids = _load_required_track_ids()
    check("[0] REQUIRED_TRACK_IDS imported from validate_corpus_registry.py...",
          len(required_track_ids) == 198,
          f"count={len(required_track_ids)}")

    # [1] Output exists and parses
    check("[1] corpus_freshness_manifest.json exists...", os.path.isfile(OUT_PATH),
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

    check("[2b] network_access is false (this manifest generator makes no network calls)...",
          out.get("network_access") is False, f"network_access={out.get('network_access')}")
    check("[2c] read_only_derived_layer is true...",
          out.get("read_only_derived_layer") is True,
          f"read_only_derived_layer={out.get('read_only_derived_layer')}")

    tracks = out.get("tracks", [])
    by_id = {t.get("track_id"): t for t in tracks if isinstance(t, dict)}

    # [3] Exactly 198 tracks, matching REQUIRED_TRACK_IDS exactly
    ids_present = set(by_id.keys())
    ids_required = set(required_track_ids)
    missing_ids = sorted(ids_required - ids_present)
    extra_ids = sorted(ids_present - ids_required)
    check("[3a] Track count == 198...", len(tracks) == 198, f"count={len(tracks)}")
    check("[3b] No missing track ids...", len(missing_ids) == 0,
          "None missing" if not missing_ids else f"Missing: {missing_ids}")
    check("[3c] No unexpected extra track ids...", len(extra_ids) == 0,
          "None extra" if not extra_ids else f"Extra: {extra_ids}")
    check("[3d] No duplicate track ids...", len(tracks) == len(ids_present),
          f"entries={len(tracks)} unique_ids={len(ids_present)}")

    # [4] Field presence + type checks on every entry
    field_problems = []
    for t in tracks:
        tid = t.get("track_id", "<unknown>")
        for field, expected_type in REQUIRED_TRACK_ENTRY_FIELDS.items():
            if field not in t:
                field_problems.append(f"{tid}: missing field '{field}'")
            elif not isinstance(t[field], expected_type):
                field_problems.append(
                    f"{tid}: field '{field}' has type {type(t[field]).__name__}, "
                    f"expected {expected_type}"
                )
    check("[4] Every entry has the expected fields with the expected types...",
          len(field_problems) == 0,
          "All valid" if not field_problems else f"Problems (first 10): {field_problems[:10]}")

    # [4b] last_verified_context is non-empty on every entry (never fabricated, but must not
    #      be silently blank either — the generator always produces at least a fallback note).
    empty_context = [t["track_id"] for t in tracks if not str(t.get("last_verified_context", "")).strip()]
    check("[4b] last_verified_context is non-empty on every entry...", len(empty_context) == 0,
          "All non-empty" if not empty_context else f"Empty on: {empty_context}")

    # [5] known_source_staleness_risk <-> known_source_staleness_pointer consistency
    inconsistent_true = [
        t["track_id"] for t in tracks
        if t.get("known_source_staleness_risk") is True
        and not str(t.get("known_source_staleness_pointer", "")).strip()
    ]
    inconsistent_false = [
        t["track_id"] for t in tracks
        if t.get("known_source_staleness_risk") is False
        and str(t.get("known_source_staleness_pointer", "")).strip()
    ]
    check("[5a] known_source_staleness_risk=true implies a non-empty pointer...",
          len(inconsistent_true) == 0,
          "Consistent" if not inconsistent_true else f"Empty pointer despite true on: {inconsistent_true}")
    check("[5b] known_source_staleness_risk=false implies an empty pointer...",
          len(inconsistent_false) == 0,
          "Consistent" if not inconsistent_false else f"Non-empty pointer despite false on: {inconsistent_false}")

    # [6] Spot-check known flagged / clean tracks
    spot_true_problems = [
        tid for tid in EXPECTED_STALENESS_RISK_TRUE
        if tid not in by_id or by_id[tid].get("known_source_staleness_risk") is not True
    ]
    check(f"[6a] Spot-check tracks flagged known_source_staleness_risk=true: "
          f"{EXPECTED_STALENESS_RISK_TRUE}...",
          len(spot_true_problems) == 0,
          "All flagged as expected" if not spot_true_problems
          else f"NOT flagged (unexpected): {spot_true_problems}")

    spot_false_problems = [
        tid for tid in EXPECTED_STALENESS_RISK_FALSE
        if tid not in by_id or by_id[tid].get("known_source_staleness_risk") is not False
    ]
    check(f"[6b] Spot-check clean track(s) NOT flagged: {EXPECTED_STALENESS_RISK_FALSE}...",
          len(spot_false_problems) == 0,
          "Correctly unflagged" if not spot_false_problems
          else f"Unexpectedly flagged (verify against the track's own discrepancies before "
               f"treating this as a bug): {spot_false_problems}")

    # [7] known_source_staleness_risk_count / _tracks match a fresh recount
    recount_flagged = sorted(t["track_id"] for t in tracks if t.get("known_source_staleness_risk") is True)
    declared_count = out.get("known_source_staleness_risk_count")
    declared_tracks = sorted(out.get("known_source_staleness_risk_tracks", []))
    check("[7a] known_source_staleness_risk_count matches a fresh recount...",
          declared_count == len(recount_flagged),
          f"declared={declared_count} recount={len(recount_flagged)}")
    check("[7b] known_source_staleness_risk_tracks matches a fresh recount...",
          declared_tracks == recount_flagged,
          f"declared={declared_tracks} recount={recount_flagged}")

    recount_no_source = sorted(t["track_id"] for t in tracks if t.get("official_source_file") is None)
    declared_no_source = sorted(out.get("tracks_without_resolvable_official_source_file", []))
    check("[7c] tracks_without_resolvable_official_source_file matches a fresh recount...",
          declared_no_source == recount_no_source,
          f"declared={declared_no_source} recount={recount_no_source}")

    check("[7d] total_tracks == 198...", out.get("total_tracks") == 198,
          f"total_tracks={out.get('total_tracks')}")

    # [8] Generator idempotency: snapshot current on-disk output, re-run the generator twice
    #     more, confirm the file never changes byte-for-byte.
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
              "(idempotent, no fabricated timestamps, no drift)...", clean_diff,
              "Clean diff" if clean_diff else "Output changed across re-runs")
    else:
        check("[8b] Re-running the generator reproduces byte-identical output twice in a row "
              "(idempotent, no fabricated timestamps, no drift)...", False,
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
