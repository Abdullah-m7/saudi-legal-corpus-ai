#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpus Registry Index Foundation — Read-Only Validator

Validates the canonical corpus registry JSON.

Checks:
  1.  Registry JSON exists and parses.
  2.  Required top-level fields present.
  3.  4 tracks present.
  4.  companies_law track exists with correct counts.
  5.  implementing_regulations_general track exists with 95 articles + 4 forms.
  6.  implementing_regulations_listed_joint_stock track exists with 69 articles + 1 appendix.
  7.  implementing_regulations_arabic_program_closure track exists with 169 total.
  8.  All referenced data_paths exist on filesystem.
  9.  All referenced report_paths exist.
  10. listed_joint_stock is marked is_specialized=True, is_general=False.
  11. Legal boundaries present in all tracks.
  12. No official translation claim.
  13. No legal advice claim.
  14. No public release claim.
  15. No trilingual alignment claim.
  16. English is reference/guidance only where mentioned.
  17. Chinese is internal/reference only where mentioned.
  18. Registry is read-only (validator does not modify files).

Usage:
    python3 scripts/validate_corpus_registry.py
Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(ROOT, "data", "corpus_registry", "corpus_registry.json")

REQUIRED_TOP_FIELDS = [
    "registry_version", "generated_date", "repository", "baseline_commit",
    "legal_status_boundaries", "total_tracks",
    "total_primary_arabic_governing_records", "total_reference_records",
    "total_internal_reference_records", "total_implementing_regulations_records",
    "total_registry_counted_records", "count_policy",
    "validation_status", "tracks",
]

REQUIRED_TRACK_IDS = [
    "companies_law",
    "implementing_regulations_general",
    "implementing_regulations_listed_joint_stock",
    "implementing_regulations_arabic_program_closure",
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


def main() -> int:
    print("=" * 60)
    print("Corpus Registry Index Foundation validation")
    print("=" * 60)
    print()

    # [1] Registry exists
    check("[1] Registry JSON exists...", os.path.isfile(REGISTRY_PATH),
          "Present" if os.path.isfile(REGISTRY_PATH) else "NOT FOUND")
    if not os.path.isfile(REGISTRY_PATH):
        print_results()
        return 1

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)

    # [2] Top-level fields
    missing = [f for f in REQUIRED_TOP_FIELDS if f not in registry]
    check("[2] Required top-level fields...", len(missing) == 0,
          "All present" if not missing else f"Missing: {missing}")

    # [3] 4 tracks
    track_ids = [t.get("track_id", "") for t in registry.get("tracks", [])]
    check("[3] 4 tracks present...", len(track_ids) == 4 and all(tid in track_ids for tid in REQUIRED_TRACK_IDS),
          f"Tracks: {track_ids}")

    tracks_by_id = {t["track_id"]: t for t in registry.get("tracks", [])}

    # [4] companies_law
    cl = tracks_by_id.get("companies_law", {})
    cl_counts = cl.get("record_counts", {})
    check("[4] companies_law: 281 Arabic articles...", cl_counts.get("arabic_articles") == 281,
          f"arabic_articles={cl_counts.get('arabic_articles')}")
    check("    companies_law: 281 English articles...", cl_counts.get("english_articles") == 281,
          f"english_articles={cl_counts.get('english_articles')}")

    # [5] general IR
    gen = tracks_by_id.get("implementing_regulations_general", {})
    gen_counts = gen.get("record_counts", {})
    check("[5] general IR: 95 articles...", gen_counts.get("articles") == 95, f"articles={gen_counts.get('articles')}")
    check("    general IR: 4 forms...", gen_counts.get("forms") == 4, f"forms={gen_counts.get('forms')}")

    # [6] listed JSC
    ljs = tracks_by_id.get("implementing_regulations_listed_joint_stock", {})
    ljs_counts = ljs.get("record_counts", {})
    check("[6] listed JSC: 69 articles...", ljs_counts.get("articles") == 69, f"articles={ljs_counts.get('articles')}")
    check("    listed JSC: 1 appendix...", ljs_counts.get("appendices") == 1, f"appendices={ljs_counts.get('appendices')}")

    # [7] closure audit
    closure = tracks_by_id.get("implementing_regulations_arabic_program_closure", {})
    closure_counts = closure.get("record_counts", {})
    check("[7] closure: 169 total records...", closure_counts.get("total_records") == 169,
          f"total_records={closure_counts.get('total_records')}")
    check("    closure: 164 article records...", closure_counts.get("total_article_records") == 164,
          f"total_article_records={closure_counts.get('total_article_records')}")

    # [8] data_paths exist
    all_data_paths_exist = True
    missing_paths = []
    for track in registry.get("tracks", []):
        for p in track.get("data_paths", []):
            full = os.path.join(ROOT, p)
            if not os.path.isfile(full):
                all_data_paths_exist = False
                missing_paths.append(p)
    check("[8] All referenced data_paths exist...", all_data_paths_exist,
          "All exist" if all_data_paths_exist else f"Missing: {missing_paths[:3]}")

    # [9] report_paths exist
    all_report_paths_exist = True
    missing_reports = []
    for track in registry.get("tracks", []):
        for p in track.get("report_paths", []):
            full = os.path.join(ROOT, p)
            if not os.path.isfile(full):
                all_report_paths_exist = False
                missing_reports.append(p)
    check("[9] All referenced report_paths exist...", all_report_paths_exist,
          "All exist" if all_report_paths_exist else f"Missing: {missing_reports[:3]}")

    # [10] listed JSC specialized
    ljs_b = ljs.get("boundaries", {})
    check("[10] listed JSC is_specialized=True...", ljs_b.get("is_specialized") is True, "True")
    check("     listed JSC is_general=False...", ljs_b.get("is_general") is False, "False")

    # [11-17] Boundaries across all tracks
    all_arabic_governs = all(t.get("boundaries", {}).get("arabic_governs") is True for t in registry.get("tracks", []))
    check("[11] Arabic governs in all tracks...", all_arabic_governs, "All True")

    all_not_translation = all(t.get("boundaries", {}).get("not_official_translation") is True for t in registry.get("tracks", []))
    check("[12] No official translation claim...", all_not_translation, "All True")

    all_not_advice = all(t.get("boundaries", {}).get("not_legal_advice") is True for t in registry.get("tracks", []))
    check("[13] No legal advice claim...", all_not_advice, "All True")

    all_no_public = all(t.get("boundaries", {}).get("no_public_release") is True for t in registry.get("tracks", []))
    check("[14] No public release claim...", all_no_public, "All True")

    all_no_trilingual = all(t.get("boundaries", {}).get("no_trilingual_alignment") is True for t in registry.get("tracks", []))
    check("[15] No trilingual alignment claim...", all_no_trilingual, "All True")

    # [16] English reference only
    cl_en = cl.get("language_layers", {}).get("english", {})
    check("[16] English is reference/guidance only...", cl_en.get("role") == "reference_guidance_only" and cl_en.get("governing") is False,
          f"role={cl_en.get('role')}, governing={cl_en.get('governing')}")

    # [17] Chinese internal only
    cl_cn = cl.get("language_layers", {}).get("chinese", {})
    check("[17] Chinese is internal/reference only...", cl_cn.get("role") == "internal_reference_only" and cl_cn.get("governing") is False,
          f"role={cl_cn.get('role')}, governing={cl_cn.get('governing')}")

    # [18] Read-only validator
    check("[18] Validator is read-only...", True, "Does not modify any files")

    # [19] Count semantics: explicit count fields
    check("[19a] total_primary_arabic_governing_records == 450...",
          registry.get("total_primary_arabic_governing_records") == 450,
          f"Value: {registry.get('total_primary_arabic_governing_records')}")

    check("[19b] total_reference_records == 281...",
          registry.get("total_reference_records") == 281,
          f"Value: {registry.get('total_reference_records')}")

    check("[19c] total_internal_reference_records == 281...",
          registry.get("total_internal_reference_records") == 281,
          f"Value: {registry.get('total_internal_reference_records')}")

    check("[19d] total_implementing_regulations_records == 169...",
          registry.get("total_implementing_regulations_records") == 169,
          f"Value: {registry.get('total_implementing_regulations_records')}")

    check("[19e] total_registry_counted_records == 1012...",
          registry.get("total_registry_counted_records") == 1012,
          f"Value: {registry.get('total_registry_counted_records')}")

    # [20] count_policy exists and has required keys
    cp = registry.get("count_policy", {})
    required_cp = [
        "counting_method", "primary_arabic_governing_records_included",
        "english_reference_records_included", "chinese_internal_reference_records_included",
        "forms_and_appendices_counted", "closure_audit_aggregate_not_counted_separately",
        "closure_audit_total_duplicates_underlying_ir_records",
        "formula_total_primary_arabic_governing", "formula_total_reference",
        "formula_total_internal_reference", "formula_total_implementing_regulations",
        "formula_total_registry_counted", "note",
    ]
    missing_cp = [f for f in required_cp if f not in cp]
    check("[20] count_policy has all required fields...", len(missing_cp) == 0,
          "All present" if not missing_cp else f"Missing: {missing_cp}")

    # [21] count_policy formulas are consistent with values
    check("[21] total_registry == primary + reference + internal...",
          registry.get("total_registry_counted_records") ==
          registry.get("total_primary_arabic_governing_records", 0)
          + registry.get("total_reference_records", 0)
          + registry.get("total_internal_reference_records", 0),
          f"450 + 281 + 281 = 1012")

    check("[22] No total_known_records field (replaced)...",
          "total_known_records" not in registry,
          "Field removed — replaced by explicit count fields")

    print_results()
    return 0 if FAILED == 0 else 1


def print_results() -> None:
    print()
    for line in CHECKS:
        print(line)
    print()
    print("=" * 60)
    if FAILED == 0:
        print("RESULT: ALL CHECKS PASSED ✓")
        print("[PASS] Corpus Registry Index Foundation: 4 tracks (companies_law, "
              "implementing_regulations_general, implementing_regulations_listed_joint_stock, "
              "implementing_regulations_arabic_program_closure). All counts correct, all "
              "referenced paths exist, all boundaries enforced. Arabic governs; no official "
              "translation; no legal advice; no trilingual; no public release. English "
              "reference only; Chinese internal only. Read-only.")
    else:
        print(f"RESULT: {FAILED} CHECK(S) FAILED ✗")
    print("=" * 60)


if __name__ == "__main__":
    sys.exit(main())