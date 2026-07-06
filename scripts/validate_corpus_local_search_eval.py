#!/usr/bin/env python3
"""
Validate local search evaluation fixtures against the existing lexical search CLI.

Deterministic, offline, no network, no embeddings, no API.
Not legal advice. Not official translation. Arabic official source governs.

Usage:
  python3 scripts/validate_corpus_local_search_eval.py
  make corpus-local-search-eval-validate
"""

import json
import os
import sys
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES_PATH = os.path.join(REPO_ROOT, "data", "search_eval", "local_search_queries_v1.json")
JSONL_PATH = os.path.join(REPO_ROOT, "data", "exports", "v1", "primary_arabic_governing_records.jsonl")
SEARCH_SCRIPT = os.path.join(REPO_ROOT, "scripts", "search_primary_arabic_export.py")

# Add scripts dir to path for direct import
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
from search_primary_arabic_export import load_records, search, format_json  # noqa: E402

REQUIRED_FIELDS = {
    "fixture_id",
    "query",
    "description_ar",
    "expected_min_matches",
    "expected_language",
    "boundary_note",
    "evaluation_type",
}

VALID_EVAL_TYPES = {
    "broad_term",
    "legal_phrase",
    "track_filter",
    "record_type_filter",
    "json_output",
    "no_result_or_low_result",
    "normalization",
}


def run_cli_json(query, track=None, record_type=None, limit=500):
    """Run the search CLI and return parsed JSON output."""
    cmd = [sys.executable, SEARCH_SCRIPT, query, "--json", "--limit", str(limit)]
    if track:
        cmd.extend(["--track", track])
    if record_type:
        cmd.extend(["--record-type", record_type])
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=30,
    )
    if result.returncode != 0:
        return None, result.stderr
    try:
        return json.loads(result.stdout), None
    except json.JSONDecodeError as e:
        return None, str(e)


def validate_fixture_schema(fixture):
    """Validate a single fixture's schema. Returns list of errors."""
    errors = []
    fid = fixture.get("fixture_id", "???")

    # Check required fields
    missing = REQUIRED_FIELDS - set(fixture.keys())
    if missing:
        errors.append(f"[{fid}] missing required fields: {sorted(missing)}")

    # Check no extra English/Chinese source content fields
    forbidden = {"english_text", "chinese_text", "en_text", "zh_text", "translation_en"}
    present_forbidden = forbidden & set(fixture.keys())
    if present_forbidden:
        errors.append(f"[{fid}] forbidden non-Arabic fields: {sorted(present_forbidden)}")

    # Check expected_language is ar
    if fixture.get("expected_language") != "ar":
        errors.append(f"[{fid}] expected_language must be 'ar', got '{fixture.get('expected_language')}'")

    # Check evaluation_type is valid
    etype = fixture.get("evaluation_type")
    if etype and etype not in VALID_EVAL_TYPES:
        errors.append(f"[{fid}] invalid evaluation_type: '{etype}'")

    # Check numeric fields
    min_m = fixture.get("expected_min_matches")
    if not isinstance(min_m, int) or min_m < 0:
        errors.append(f"[{fid}] expected_min_matches must be non-negative integer, got {min_m}")

    max_m = fixture.get("expected_max_matches")
    if max_m is not None and (not isinstance(max_m, int) or max_m < 0):
        errors.append(f"[{fid}] expected_max_matches must be non-negative integer or absent, got {max_m}")

    # Check top_k contains any is a list of strings if present
    top_k = fixture.get("expected_top_k_contains_any")
    if top_k is not None:
        if not isinstance(top_k, list) or not all(isinstance(x, str) for x in top_k):
            errors.append(f"[{fid}] expected_top_k_contains_any must be list of strings")

    return errors


def validate_fixture_search(fixture, records):
    """Run the search for a fixture and check expectations. Returns (errors, info)."""
    errors = []
    info = {}
    fid = fixture.get("fixture_id", "???")

    query = fixture["query"]
    track = fixture.get("track_filter")
    record_type = fixture.get("record_type_filter")

    # Run search using imported functions (deterministic, offline)
    all_results = search(records, query, limit=len(records), track=track, record_type=record_type)
    total_matches = len(all_results)
    top_results = all_results[:10]

    info["total_matches"] = total_matches
    info["top_ids"] = [r["export_record_id"] for r in top_results]

    # Check min matches
    min_expected = fixture.get("expected_min_matches", 0)
    if total_matches < min_expected:
        errors.append(
            f"[{fid}] expected_min_matches={min_expected} but got {total_matches}"
        )

    # Check max matches
    max_expected = fixture.get("expected_max_matches")
    if max_expected is not None and total_matches > max_expected:
        errors.append(
            f"[{fid}] expected_max_matches={max_expected} but got {total_matches}"
        )

    # Check top_k contains any
    top_k_expected = fixture.get("expected_top_k_contains_any")
    if top_k_expected:
        top_ids_set = set(r["export_record_id"] for r in top_results)
        found = top_k_expected if isinstance(top_k_expected, list) else [top_k_expected]
        matched = [x for x in found if x in top_ids_set]
        if not matched:
            errors.append(
                f"[{fid}] expected_top_k_contains_any={found} "
                f"but top-10 IDs were {sorted(top_ids_set)}"
            )

    # Check track filter consistency
    if track:
        wrong_track = [r for r in all_results if r.get("source_track_id") != track]
        if wrong_track:
            errors.append(
                f"[{fid}] track_filter={track} but {len(wrong_track)} results "
                f"from other tracks"
            )

    # Check record_type filter consistency
    if record_type:
        wrong_type = [r for r in all_results if r.get("record_type") != record_type]
        if wrong_type:
            errors.append(
                f"[{fid}] record_type_filter={record_type} but {len(wrong_type)} results "
                f"from other record types"
            )

    # Check language is ar for all results
    for r in all_results:
        rec = r.get("_record", {})
        lang = rec.get("language", "ar")
        if lang != "ar":
            errors.append(f"[{fid}] result {r['export_record_id']} has language={lang}, expected ar")
            break

    # JSON output validation
    if fixture.get("json_output"):
        json_output, err = run_cli_json(query, track=track, record_type=record_type, limit=10)
        if json_output is None:
            errors.append(f"[{fid}] JSON output failed: {err}")
        else:
            required_json_fields = {"query", "normalized_query", "total_matches", "returned", "results"}
            missing_json = required_json_fields - set(json_output.keys())
            if missing_json:
                errors.append(f"[{fid}] JSON output missing fields: {sorted(missing_json)}")
            for r in json_output.get("results", []):
                required_result_fields = {
                    "score", "export_record_id", "source_track_id",
                    "source_record_id", "record_type", "title_ar", "snippet",
                }
                missing_r = required_result_fields - set(r.keys())
                if missing_r:
                    errors.append(
                        f"[{fid}] JSON result {r.get('export_record_id','?')} "
                        f"missing fields: {sorted(missing_r)}"
                    )
                    break

    return errors, info


def main():
    # ─── Step 1: Check fixture file exists ───
    if not os.path.isfile(FIXTURES_PATH):
        print(f"FAIL: Fixture file not found: {FIXTURES_PATH}")
        sys.exit(1)

    # ─── Step 2: Parse fixture file ───
    with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
        try:
            fixtures = json.load(f)
        except json.JSONDecodeError as e:
            print(f"FAIL: Fixture file is not valid JSON: {e}")
            sys.exit(1)

    # ─── Step 3: Check fixture count ───
    count = len(fixtures)
    if count < 8 or count > 12:
        print(f"FAIL: Fixture count {count} is outside range [8, 12]")
        sys.exit(1)

    print(f"Fixture count: {count}")
    print()

    # ─── Step 4: Validate schemas ───
    schema_errors = []
    for fx in fixtures:
        schema_errors.extend(validate_fixture_schema(fx))

    if schema_errors:
        print("SCHEMA ERRORS:")
        for e in schema_errors:
            print(f"  {e}")
        print()
        print(f"FAIL: {len(schema_errors)} schema error(s)")
        sys.exit(1)

    print("Schema validation: PASS")

    # ─── Step 5: Check export JSONL exists ───
    if not os.path.isfile(JSONL_PATH):
        print(f"FAIL: Export JSONL not found: {JSONL_PATH}")
        sys.exit(1)

    # ─── Step 6: Load records and run search checks ───
    records = load_records(JSONL_PATH)
    print(f"Records loaded: {len(records)}")
    print()

    all_errors = []
    all_info = []

    for fx in fixtures:
        errors, info = validate_fixture_search(fx, records)
        all_errors.extend(errors)
        all_info.append((fx, info))

    # ─── Step 7: Print results ───
    print("=" * 60)
    print("FIXTURE RESULTS")
    print("=" * 60)
    for fx, info in all_info:
        fid = fx["fixture_id"]
        etype = fx["evaluation_type"]
        query = fx["query"]
        total = info["total_matches"]
        status = "PASS" if not any(e.startswith(f"[{fid}]") for e in all_errors) else "FAIL"
        print(f"  {fid} [{etype}] \"{query}\" → {total} matches → {status}")
    print()

    if all_errors:
        print("SEARCH ERRORS:")
        for e in all_errors:
            print(f"  {e}")
        print()
        print(f"FAIL: {len(all_errors)} search error(s)")
        sys.exit(1)

    print(f"All {count} fixtures: PASS")
    print()
    print("SUMMARY: PASS — all evaluation fixtures passed")
    print("  - No network used")
    print("  - No embeddings/vector DB/API dependency")
    print("  - All results are Arabic (ar)")
    print("  - Deterministic and locally reproducible")


if __name__ == "__main__":
    main()