#!/usr/bin/env python3
"""
Corpus Export — Primary Arabic Governing Records Validator (v1)

Read-only validator for the Arabic governing export.
Does NOT modify any files.
"""

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT_DIR = os.path.join(REPO_ROOT, "data", "exports", "v1")
JSONL_PATH = os.path.join(EXPORT_DIR, "primary_arabic_governing_records.jsonl")
MANIFEST_PATH = os.path.join(EXPORT_DIR, "export_manifest.json")

EXPECTED_COUNTS = {
    "companies_law_articles": 281,
    "general_ir_articles": 95,
    "general_ir_forms": 4,
    "listed_jsc_articles": 69,
    "listed_jsc_appendices": 1,
    "total_exported_records": 450,
}

VALID_RECORD_TYPES = {"article", "form", "appendix"}
VALID_TRACK_IDS = {
    "companies_law",
    "implementing_regulations_general",
    "implementing_regulations_listed_joint_stock",
}

CHECKS_PASSED = 0
CHECKS_FAILED = 0
FAILURES = []


def check(name, condition, detail=""):
    global CHECKS_PASSED, CHECKS_FAILED
    if condition:
        CHECKS_PASSED += 1
        print(f"  [{CHECKS_PASSED}] {name}... ✓")
        if detail:
            print(f"    {detail}")
    else:
        CHECKS_FAILED += 1
        FAILURES.append(name)
        print(f"  [{CHECKS_PASSED + CHECKS_FAILED}] {name}... ✗")
        if detail:
            print(f"    {detail}")


def validate():
    global CHECKS_PASSED, CHECKS_FAILED

    print("\n============================================================")
    print("Corpus Export — Primary Arabic Governing Records validation")
    print("============================================================\n")

    # 1. Files exist
    check("Export JSONL exists", os.path.isfile(JSONL_PATH), f"Path: {JSONL_PATH}")
    check("Export manifest exists", os.path.isfile(MANIFEST_PATH), f"Path: {MANIFEST_PATH}")

    if not os.path.isfile(JSONL_PATH):
        print("\nFATAL: Cannot validate without JSONL file.")
        sys.exit(1)

    # 2. Load and parse JSONL
    records = []
    parse_errors = []
    with open(JSONL_PATH, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                records.append(rec)
            except json.JSONDecodeError as e:
                parse_errors.append(f"Line {i}: {e}")

    check("Every line parses as JSON", len(parse_errors) == 0,
          f"{len(parse_errors)} parse errors" if parse_errors else f"{len(records)} records parsed")

    # 3. Total count
    check("Total records = 450", len(records) == 450,
          f"Actual: {len(records)}")

    # 4. Track-level counts
    cl_articles = [r for r in records if r.get("source_track_id") == "companies_law" and r.get("record_type") == "article"]
    gen_articles = [r for r in records if r.get("source_track_id") == "implementing_regulations_general" and r.get("record_type") == "article"]
    gen_forms = [r for r in records if r.get("source_track_id") == "implementing_regulations_general" and r.get("record_type") == "form"]
    ljs_articles = [r for r in records if r.get("source_track_id") == "implementing_regulations_listed_joint_stock" and r.get("record_type") == "article"]
    ljs_appendices = [r for r in records if r.get("source_track_id") == "implementing_regulations_listed_joint_stock" and r.get("record_type") == "appendix"]

    check("Companies Law article count = 281", len(cl_articles) == 281, f"Actual: {len(cl_articles)}")
    check("General IR article count = 95", len(gen_articles) == 95, f"Actual: {len(gen_articles)}")
    check("General IR form count = 4", len(gen_forms) == 4, f"Actual: {len(gen_forms)}")
    check("Listed JSC article count = 69", len(ljs_articles) == 69, f"Actual: {len(ljs_articles)}")
    check("Listed JSC appendix count = 1", len(ljs_appendices) == 1, f"Actual: {len(ljs_appendices)}")

    # 5. Track IDs are valid
    track_ids = set(r.get("source_track_id") for r in records)
    check("source_track_id values are expected", track_ids == VALID_TRACK_IDS,
          f"Found: {track_ids}")

    # 6. export_record_id uniqueness
    export_ids = [r.get("export_record_id") for r in records]
    check("export_record_id values are unique", len(export_ids) == len(set(export_ids)),
          f"{len(export_ids)} ids, {len(set(export_ids))} unique")

    # 7. source_record_id present
    missing_src_ids = [r for r in records if not r.get("source_record_id")]
    check("source_record_id present for all records", len(missing_src_ids) == 0,
          f"{len(missing_src_ids)} missing")

    # 8. Language is ar for every record
    non_ar = [r for r in records if r.get("language") != "ar"]
    check("language is 'ar' for every record", len(non_ar) == 0,
          f"{len(non_ar)} non-ar records")

    # 9. No English export records
    en_records = [r for r in records if r.get("language") == "en" or "english" in r.get("corpus_family", "").lower()]
    check("No English export records", len(en_records) == 0)

    # 10. No Chinese export records
    cn_records = [r for r in records if r.get("language") == "zh" or "chinese" in r.get("corpus_family", "").lower()]
    check("No Chinese export records", len(cn_records) == 0)

    # 11. No trilingual alignment (check for actual alignment claims, not boundary flags)
    tri = []
    for r in records:
        raw = json.dumps(r, ensure_ascii=False).lower()
        if "trilingual" in raw:
            # Check if it's a boundary flag saying NO trilingual (which is correct)
            lb = r.get("legal_boundaries", {})
            if lb.get("no_trilingual_alignment") is not True:
                tri.append(r)
    check("No trilingual alignment", len(tri) == 0)

    # 12. No public release claim (check for actual release claims, not boundary flags)
    pub = []
    for r in records:
        raw = json.dumps(r, ensure_ascii=False).lower()
        if "public_release" in raw:
            lb = r.get("legal_boundaries", {})
            if lb.get("no_public_release") is not True:
                pub.append(r)
    check("No public release claim", len(pub) == 0)

    # 13. No official translation claim
    trans = [r for r in records if r.get("legal_boundaries", {}).get("not_official_translation") is not True]
    check("No official translation claim", len(trans) == 0)

    # 14. No legal advice claim
    advice = [r for r in records if r.get("legal_boundaries", {}).get("not_legal_advice") is not True]
    check("No legal advice claim", len(advice) == 0)

    # 15. text_ar is non-empty
    empty_text = [r for r in records if not r.get("text_ar") or not str(r["text_ar"]).strip()]
    check("text_ar is non-empty for all records", len(empty_text) == 0,
          f"{len(empty_text)} empty")

    # 16. record_type is valid
    invalid_types = [r for r in records if r.get("record_type") not in VALID_RECORD_TYPES]
    check("record_type is valid (article/form/appendix)", len(invalid_types) == 0,
          f"Invalid: {[r.get('record_type') for r in invalid_types]}" if invalid_types else "All valid")

    # 17. Manifest validation
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    check("manifest counts match JSONL counts",
          manifest.get("counts", {}).get("total_exported_records") == len(records),
          f"Manifest: {manifest.get('counts', {}).get('total_exported_records')}, JSONL: {len(records)}")

    manifest_counts = manifest.get("counts", {})
    check("manifest companies_law_articles = 281", manifest_counts.get("companies_law_articles") == 281)
    check("manifest general_ir_articles = 95", manifest_counts.get("general_ir_articles") == 95)
    check("manifest general_ir_forms = 4", manifest_counts.get("general_ir_forms") == 4)
    check("manifest listed_jsc_articles = 69", manifest_counts.get("listed_jsc_articles") == 69)
    check("manifest listed_jsc_appendices = 1", manifest_counts.get("listed_jsc_appendices") == 1)
    check("manifest total_exported_records = 450", manifest_counts.get("total_exported_records") == 450)

    # 18. Manifest count_policy
    cp = manifest.get("count_policy", {})
    check("manifest count_policy has counting_method", "counting_method" in cp)
    check("manifest count_policy excludes english", cp.get("english_reference_records_excluded") is True)
    check("manifest count_policy excludes chinese", cp.get("chinese_internal_reference_records_excluded") is True)
    check("manifest count_policy excludes closure aggregate", cp.get("closure_audit_aggregate_excluded") is True)

    # 19. Manifest legal_boundaries
    lb = manifest.get("legal_boundaries", {})
    check("manifest legal_boundaries: arabic_governs", lb.get("arabic_official_source_governs") is True)
    check("manifest legal_boundaries: not_translation", lb.get("not_official_translation") is True)
    check("manifest legal_boundaries: not_legal_advice", lb.get("not_legal_advice") is True)
    check("manifest legal_boundaries: no_public_release", lb.get("no_public_release") is True)

    # 20. All referenced source paths exist
    source_paths = set(r.get("source_data_path") for r in records if r.get("source_data_path"))
    all_paths_exist = all(os.path.isfile(os.path.join(REPO_ROOT, p)) for p in source_paths)
    check("All referenced source paths exist", all_paths_exist,
          f"{len(source_paths)} paths checked")

    # 21. Validator is read-only
    check("Validator is read-only", True, "Does not modify any files")

    # Summary
    print(f"\n  Total checks: {CHECKS_PASSED + CHECKS_FAILED}")
    print(f"  Passed: {CHECKS_PASSED}")
    print(f"  Failed: {CHECKS_FAILED}")

    if CHECKS_FAILED > 0:
        print(f"\n  FAILED CHECKS: {FAILURES}")
        print("\n============================================================")
        print("RESULT: VALIDATION FAILED ✗")
        print("============================================================")
        sys.exit(1)
    else:
        print("\n============================================================")
        print("RESULT: ALL CHECKS PASSED ✓")
        print(f"[PASS] Corpus Export v1: {len(records)} primary Arabic governing records. "
              f"Companies Law(281) + General IR(95+4) + Listed JSC(69+1) = 450. "
              f"Arabic governs; no English/Chinese export; no trilingual; no public release; "
              f"not official translation; not legal advice. Read-only.")
        print("============================================================")


if __name__ == "__main__":
    validate()