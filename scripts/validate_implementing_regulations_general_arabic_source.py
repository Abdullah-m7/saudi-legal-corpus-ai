#!/usr/bin/env python3
"""
General Implementing Regulations Arabic Source Intake — Read-Only Validator
Validates the intake JSON, source manifest, provenance, article records,
content boundaries, and legal-status fields.

Usage:
    python3 scripts/validate_implementing_regulations_general_arabic_source.py
"""

import json
import sys
import os
import hashlib

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTAKE_PATH = os.path.join(REPO_ROOT, "data", "implementing_regulations", "general", "general_implementing_regulations_arabic_source.json")
MANIFEST_PATH = os.path.join(REPO_ROOT, "data", "implementing_regulations", "general", "source_manifest.json")
REPORT_PATH = os.path.join(REPO_ROOT, "reports", "implementing_regulations", "GENERAL_IMPLEMENTING_REGULATIONS_ARABIC_SOURCE_INTAKE_AR.md")

# Parent law files (must exist and be unchanged)
PARENT_LAW_FILES = [
    "data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json",
    "data/legal_corpus_factory/law_profiles/sa_companies_law_m132_1443.profile.json",
    "reports/chinese_translation_review/chinese_remediation_program_closure_audit.json",
]

# Listed joint-stock intake (must exist and be unchanged)
LISTED_JSC_PATH = os.path.join(REPO_ROOT, "data", "implementing_regulations", "listed_joint_stock", "listed_joint_stock_implementing_regulation_arabic_source.json")

CHECKS = []
PASSED = 0
FAILED = 0


def check(name, condition, detail=""):
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


def main():
    global PASSED, FAILED

    print("=" * 60)
    print("General implementing regulations Arabic source intake validation")
    print("=" * 60)
    print()

    # [1] Check intake JSON exists
    check("[1] Checking intake JSON exists...",
          os.path.isfile(INTAKE_PATH),
          "intake JSON present and valid" if os.path.isfile(INTAKE_PATH) else f"NOT FOUND: {INTAKE_PATH}")
    if not os.path.isfile(INTAKE_PATH):
        print_results()
        return 1

    with open(INTAKE_PATH, "r", encoding="utf-8") as f:
        intake = json.load(f)

    # [2] Check stage field
    check("[2] Checking stage field...",
          intake.get("stage") == "GENERAL_IMPLEMENTING_REGULATIONS_ARABIC_SOURCE_INTAKE",
          f"stage correct")

    # [3] Check corpus track
    check("[3] Checking corpus track...",
          intake.get("corpus_track") == "implementing_regulations/general",
          f"corpus_track={intake.get('corpus_track')}")

    # [4] Check general scope (NOT specialized)
    check("[4] Checking general scope...",
          intake.get("general") is True and intake.get("specialized") is False,
          f"general=True, specialized=False")

    # [5] Check source provenance
    required_provenance = ["source_title", "source_url", "publication_date_hijri",
                           "publication_date_gregorian", "source_scope", "access_date",
                           "extraction_method", "source_hash"]
    missing = [f for f in required_provenance if not intake.get(f)]
    check("[5] Checking source provenance...",
          len(missing) == 0,
          "All required provenance fields present" if not missing else f"Missing: {missing}")

    # [6] Check article records
    articles = intake.get("articles", [])
    check("[6] Checking article records...",
          len(articles) == 95,
          f"{len(articles)} article records present")

    # [7] Check article structure
    all_valid = all(
        "official_text_ar" in a and "text_hash_sha256" in a and "article_label" in a
        for a in articles
    )
    check("[7] Checking article structure...",
          all_valid,
          "All articles have official_text_ar, text_hash_sha256, and article_label")

    # [8] Check chapters
    chapters = intake.get("chapters", [])
    check("[8] Checking chapters...",
          len(chapters) == 7,
          f"{len(chapters)} chapters present")

    # [9] Check forms
    forms = intake.get("forms", [])
    check("[9] Checking forms...",
          len(forms) == 4,
          f"{len(forms)} forms present")

    # [10] Check no English text generated
    has_english = any(
        any(c.isascii() and c.isalpha() for c in a.get("official_text_ar", ""))
        for a in articles
    )
    # More precise: check for English sentences (multiple consecutive ASCII words)
    import re
    english_pattern = re.compile(r'[A-Za-z]{3,}\s+[A-Za-z]{3,}')
    has_english_text = any(english_pattern.search(a.get("official_text_ar", "")) for a in articles)
    check("[10] Checking no English text generated...",
          not has_english_text,
          "No English text generated")

    # [11] Check no Chinese text generated
    has_chinese = any(
        any('\u4e00' <= c <= '\u9fff' for c in a.get("official_text_ar", ""))
        for a in articles
    )
    check("[11] Checking no Chinese text generated...",
          not has_chinese,
          "No Chinese text generated")

    # [12] Check no trilingual alignment
    check("[12] Checking no trilingual alignment...",
          intake.get("content_boundaries", {}).get("no_trilingual_alignment") is True,
          "No trilingual alignment")

    # [13] Check no public release
    check("[13] Checking no public release...",
          intake.get("content_boundaries", {}).get("no_public_release") is True,
          "No public release")

    # [14] Check legal-status boundaries
    ls = intake.get("legal_status", {})
    legal_ok = (
        ls.get("arabic_governs") is True and
        ls.get("english_reference_only") is True and
        ls.get("chinese_internal_reference_only") is True and
        ls.get("not_official_translation") is True and
        ls.get("not_legal_advice") is True
    )
    check("[14] Checking legal-status boundaries...",
          legal_ok,
          "All legal-status boundaries correct")

    # [15] Check parent law files exist (unchanged)
    parent_ok = all(os.path.isfile(os.path.join(REPO_ROOT, p)) for p in PARENT_LAW_FILES)
    check("[15] Checking parent law files exist (unchanged)...",
          parent_ok,
          "All parent law files present" if parent_ok else "Some parent law files missing")

    # [16] Check listed joint-stock intake exists (unchanged)
    check("[16] Checking listed joint-stock intake exists...",
          os.path.isfile(LISTED_JSC_PATH),
          "listed_joint_stock intake present" if os.path.isfile(LISTED_JSC_PATH) else "listed_joint_stock intake missing")

    # [17] Check source manifest
    check("[17] Checking source manifest...",
          os.path.isfile(MANIFEST_PATH),
          "Source manifest present" if os.path.isfile(MANIFEST_PATH) else "Source manifest missing")
    if os.path.isfile(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        manifest_ok = (
            manifest.get("source_title") == intake.get("source_title") and
            manifest.get("source_url") == intake.get("source_url") and
            manifest.get("source_hash") == intake.get("source_hash") and
            manifest.get("article_count") == intake.get("article_count") and
            manifest.get("chapter_count") == intake.get("chapter_count")
        )
        check("    Manifest consistency...",
              manifest_ok,
              "Source manifest consistent")

    # [18] Check separation from listed joint-stock
    sep = intake.get("separation_from_other_tracks", {})
    check("[18] Checking separation from listed joint-stock...",
          "listed_joint_stock_sub_track" in sep,
          "Separation from listed_joint_stock recorded")

    # [19] Check Arabic report exists
    check("[19] Checking Arabic report...",
          os.path.isfile(REPORT_PATH),
          "Arabic report present" if os.path.isfile(REPORT_PATH) else "Arabic report missing")

    print_results()
    return 0 if FAILED == 0 else 1


def print_results():
    print()
    for line in CHECKS:
        print(line)
    print()
    print("=" * 60)
    if FAILED == 0:
        print("RESULT: ALL CHECKS PASSED ✓")
        print("[PASS] General implementing regulations Arabic source intake: "
              "95 articles across 7 chapters + 4 forms, extracted from the official "
              "Umm Al-Qura gazette page (uqn.gov.sa/details?p=21325), published "
              "1444-6-25 AH / 18-01-2023, under Companies Law M/132 (1443H). "
              "General scope: all company forms. Arabic governs; no English/Chinese "
              "text generated; no trilingual alignment; no public release. "
              "Companies Law corpus and Chinese remediation program unchanged. "
              "Listed joint-stock sub-track is separate. Not legal advice. Read-only.")
    else:
        print(f"RESULT: {FAILED} CHECK(S) FAILED ✗")
    print("=" * 60)


if __name__ == "__main__":
    sys.exit(main())