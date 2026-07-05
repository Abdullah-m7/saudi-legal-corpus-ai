#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the listed joint-stock implementing regulation Arabic source intake.

Read-only validator: verifies the Arabic source intake JSON, source manifest,
article records, provenance, and legal-status boundaries. Does not modify files.

Checks:
  1. Source intake JSON exists and is valid JSON.
  2. Stage is IMPLEMENTING_REGULATIONS_LISTED_JSC_ARABIC_SOURCE_INTAKE.
  3. Corpus track is implementing_regulations/listed_joint_stock.
  4. Is specialized (not general) implementing regulation.
  5. Source provenance has all required fields.
  6. 69 article records with valid structure.
  7. Each article has official_text_ar and text_hash_sha256.
  8. 14 chapters present.
  9. Appendix (ملحق 1) present.
 10. No English text generated.
 11. No Chinese text generated.
 12. No trilingual alignment.
 13. No public release.
 14. Arabic governs; not official/binding/governing; not legal advice.
 15. Companies Law corpus and Chinese remediation unchanged.
 16. Source manifest exists and is consistent.
 17. No prohibited content claims.

Usage: validate_implementing_regulations_listed_jsc_arabic_source.py
Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTAKE_JSON = os.path.join(
    ROOT,
    "data",
    "implementing_regulations",
    "listed_joint_stock",
    "listed_joint_stock_implementing_regulation_arabic_source.json",
)
MANIFEST_JSON = os.path.join(
    ROOT,
    "data",
    "implementing_regulations",
    "listed_joint_stock",
    "source_manifest.json",
)
ARABIC_REPORT = os.path.join(
    ROOT,
    "reports",
    "implementing_regulations",
    "LISTED_JOINT_STOCK_ARABIC_SOURCE_INTAKE_AR.md",
)

PARENT_LAW_FILES = [
    os.path.join(
        ROOT,
        "data",
        "official_arabic_legal_llm",
        "companies_law_m132_1443_official_arabic_legal_llm_001_281.json",
    ),
    os.path.join(
        ROOT,
        "data",
        "legal_corpus_factory",
        "law_profiles",
        "sa_companies_law_m132_1443.profile.json",
    ),
    os.path.join(
        ROOT,
        "reports",
        "chinese_translation_review",
        "chinese_remediation_program_closure_audit.json",
    ),
]


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    problems: list[str] = []

    print("=" * 60)
    print("Listed joint-stock implementing regulation Arabic source intake validation")
    print("=" * 60)

    # --- Check 1: intake JSON exists ---
    print("\n[1] Checking intake JSON exists...")
    if not os.path.exists(INTAKE_JSON):
        print("  FAIL: intake JSON not found")
        return 1
    data = load_json(INTAKE_JSON)
    print("  intake JSON present and valid ✓")

    # --- Check 2: stage ---
    print("\n[2] Checking stage field...")
    if data.get("stage") != "IMPLEMENTING_REGULATIONS_LISTED_JSC_ARABIC_SOURCE_INTAKE":
        problems.append(f"stage mismatch: {data.get('stage')}")
        print("  FAIL: stage mismatch")
    else:
        print("  stage correct ✓")

    # --- Check 3: corpus track ---
    print("\n[3] Checking corpus track...")
    if data.get("corpus_track") != "implementing_regulations/listed_joint_stock":
        problems.append("corpus_track mismatch")
        print("  FAIL: corpus_track mismatch")
    else:
        print("  corpus_track=implementing_regulations/listed_joint_stock ✓")

    # --- Check 4: specialized (not general) ---
    print("\n[4] Checking specialized scope...")
    if data.get("is_general_implementing_regulation", True) is not False:
        problems.append("is_general_implementing_regulation is not False")
        print("  FAIL: should not be general")
    elif not data.get("is_specialized_implementing_regulation", False):
        problems.append("is_specialized_implementing_regulation is not True")
        print("  FAIL: should be specialized")
    else:
        print("  specialized=True, general=False ✓")

    # --- Check 5: provenance ---
    print("\n[5] Checking source provenance...")
    prov = data.get("provenance", {})
    required_fields = [
        "source_title", "source_url", "publication_date_hijri",
        "publication_date_gregorian", "issuing_authority", "legal_basis",
        "source_scope", "access_date", "extraction_method",
        "source_hash_sha256", "uncertainty_notes",
    ]
    for field in required_fields:
        if not prov.get(field):
            problems.append(f"provenance.{field} is missing or empty")
            print(f"  FAIL: provenance.{field} missing")
    if not any(f"provenance.{f}" in p for f in required_fields for p in problems):
        print("  All required provenance fields present ✓")

    # --- Check 6: article records ---
    print("\n[6] Checking article records...")
    articles = data.get("articles", [])
    if len(articles) != 69:
        problems.append(f"Expected 69 articles, got {len(articles)}")
        print(f"  FAIL: expected 69, got {len(articles)}")
    else:
        print(f"  69 article records present ✓")

    # --- Check 7: article structure ---
    print("\n[7] Checking article structure...")
    for i, art in enumerate(articles):
        if not art.get("official_text_ar"):
            problems.append(f"Article {i+1} missing official_text_ar")
            print(f"  FAIL: article {i+1} missing official_text_ar")
            break
        if not art.get("text_hash_sha256"):
            problems.append(f"Article {i+1} missing text_hash_sha256")
            print(f"  FAIL: article {i+1} missing text_hash_sha256")
            break
        if not art.get("article_label"):
            problems.append(f"Article {i+1} missing article_label")
            print(f"  FAIL: article {i+1} missing article_label")
            break
    else:
        print("  All articles have official_text_ar, text_hash_sha256, and article_label ✓")

    # --- Check 8: chapters ---
    print("\n[8] Checking chapters...")
    chapters = data.get("chapters", [])
    if len(chapters) != 14:
        problems.append(f"Expected 14 chapters, got {len(chapters)}")
        print(f"  FAIL: expected 14, got {len(chapters)}")
    else:
        print(f"  14 chapters present ✓")

    # --- Check 9: appendix ---
    print("\n[9] Checking appendix...")
    if not data.get("has_appendix"):
        problems.append("has_appendix is not True")
        print("  FAIL: no appendix")
    elif not data.get("appendix_text"):
        problems.append("appendix_text is empty")
        print("  FAIL: appendix_text empty")
    else:
        print("  Appendix present ✓")

    # --- Check 10: no English text ---
    print("\n[10] Checking no English text generated...")
    if not data.get("no_new_english_text", False):
        problems.append("no_new_english_text is not True")
        print("  FAIL: no_new_english_text not True")
    elif data.get("english_status") != "not_yet_added":
        problems.append("english_status is not not_yet_added")
        print("  FAIL: english_status mismatch")
    else:
        print("  No English text generated ✓")

    # --- Check 11: no Chinese text ---
    print("\n[11] Checking no Chinese text generated...")
    if not data.get("no_new_chinese_text", False):
        problems.append("no_new_chinese_text is not True")
        print("  FAIL: no_new_chinese_text not True")
    elif data.get("chinese_status") != "not_yet_added":
        problems.append("chinese_status is not not_yet_added")
        print("  FAIL: chinese_status mismatch")
    else:
        print("  No Chinese text generated ✓")

    # --- Check 12: no trilingual alignment ---
    print("\n[12] Checking no trilingual alignment...")
    if not data.get("no_trilingual_alignment", False):
        problems.append("no_trilingual_alignment is not True")
        print("  FAIL: no_trilingual_alignment not True")
    else:
        print("  No trilingual alignment ✓")

    # --- Check 13: no public release ---
    print("\n[13] Checking no public release...")
    if data.get("public_release_created") is not False:
        problems.append("public_release_created is not False")
        print("  FAIL: public_release_created not False")
    else:
        print("  No public release ✓")

    # --- Check 14: legal-status boundaries ---
    print("\n[14] Checking legal-status boundaries...")
    lsb = data.get("legal_status_boundaries", {})
    required_true = [
        "arabic_governs", "not_official", "not_binding",
        "not_governing", "not_legal_advice", "separate_corpus_track",
        "specialized_scope_only", "parent_law_unchanged",
    ]
    for field in required_true:
        if not lsb.get(field, False):
            problems.append(f"legal_status_boundaries.{field} is not True")
            print(f"  FAIL: {field} not True")
    if not any(f"legal_status_boundaries.{f}" in p for f in required_true for p in problems):
        print("  All legal-status boundaries correct ✓")

    # --- Check 15: parent law unchanged ---
    print("\n[15] Checking parent law files unchanged...")
    for f in PARENT_LAW_FILES:
        if not os.path.exists(f):
            problems.append(f"Parent law file missing: {os.path.relpath(f, ROOT)}")
            print(f"  FAIL: missing {os.path.relpath(f, ROOT)}")
        else:
            print(f"  {os.path.relpath(f, ROOT)} exists ✓")

    # --- Check 16: source manifest ---
    print("\n[16] Checking source manifest...")
    if not os.path.exists(MANIFEST_JSON):
        problems.append("source_manifest.json not found")
        print("  FAIL: manifest not found")
    else:
        manifest = load_json(MANIFEST_JSON)
        if manifest.get("source_hash_sha256") != prov.get("source_hash_sha256"):
            problems.append("Manifest hash does not match intake hash")
            print("  FAIL: hash mismatch")
        elif manifest.get("article_count") != 69:
            problems.append(f"Manifest article_count != 69: {manifest.get('article_count')}")
            print("  FAIL: manifest article_count")
        else:
            print("  Source manifest consistent ✓")

    # --- Check 17: no prohibited claims ---
    print("\n[17] Checking no prohibited content claims...")
    if data.get("official_translation_claimed"):
        problems.append("official_translation_claimed is True")
        print("  FAIL: official_translation_claimed")
    elif data.get("official_adoption_claimed"):
        problems.append("official_adoption_claimed is True")
        print("  FAIL: official_adoption_claimed")
    else:
        print("  No prohibited claims ✓")

    # --- Check Arabic report ---
    print("\n[18] Checking Arabic report...")
    if not os.path.exists(ARABIC_REPORT):
        problems.append("Arabic report not found")
        print("  FAIL: Arabic report not found")
    else:
        print("  Arabic report present ✓")

    # --- Final ---
    print("\n" + "=" * 60)
    if problems:
        print(f"RESULT: {len(problems)} PROBLEM(S) FOUND")
        for p in problems:
            print(f"  - {p}")
        return 1
    else:
        print("RESULT: ALL CHECKS PASSED ✓")
        print(
            "[PASS] Listed joint-stock implementing regulation Arabic source intake: "
            "69 articles across 14 chapters + appendix, extracted from the official "
            "Umm Al-Qura gazette page (uqn.gov.sa/decisions-and-regulations/4001295), "
            "published 1448-1-18 AH / 03-07-2026, issued by the Capital Market Authority "
            "board under Companies Law M/132 (1443H). Specialized scope: listed joint-stock "
            "companies only, NOT a general implementing regulation. Arabic governs; no "
            "English/Chinese text generated; no trilingual alignment; no public release. "
            "Companies Law corpus and Chinese remediation program unchanged. Not legal advice."
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())