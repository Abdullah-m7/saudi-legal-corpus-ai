#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the implementing regulations intake scaffold.

Read-only validator: verifies the scaffold JSON structure, metadata
placeholders, legal-status boundaries, and that no actual content
(Arabic/English/Chinese text, trilingual alignment, public release)
has been created. Does not modify any files.

Checks:
  1. Scaffold JSON exists and is valid JSON.
  2. Stage is IMPLEMENTING_REGULATIONS_INTAKE_SCAFFOLD.
  3. Corpus track is implementing_regulations, separate from parent law.
  4. Parent law is sa_companies_law_m132_1443 and unchanged.
  5. Source provenance status is not_yet_ingested (no intake performed).
  6. Article numbering is unknown (total_articles is null).
  7. Arabic layer status is not_yet_ingested, governing=true.
  8. English layer status is not_yet_added, governing=false.
  9. Chinese layer status is not_yet_added, governing=false.
 10. No prohibited content: no_new_chinese_text, no_new_english_text,
     no_trilingual_alignment, public_release_created=false.
 11. Legal-status boundaries: Arabic governs, not official/binding/governing,
     not legal advice, separate corpus track.
 12. Companies Law corpus files unchanged (spot-check existence).
 13. No implementing-regulations content files exist beyond scaffold/README.

Usage: validate_implementing_regulations_intake_scaffold.py
Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAFFOLD = os.path.join(
    ROOT, "data", "implementing_regulations", "intake_scaffold.json"
)
SCAFFOLD_README = os.path.join(
    ROOT, "data", "implementing_regulations", "README.md"
)
ARABIC_REPORT = os.path.join(
    ROOT,
    "reports",
    "implementing_regulations",
    "IMPLEMENTING_REGULATIONS_INTAKE_SCAFFOLD_AR.md",
)

# Companies Law files to spot-check (unchanged)
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
        "official_english_legal_llm",
        "companies_law_m132_1443_official_english_legal_llm_001_281.json",
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

BANNED_PHRASES = (
    "official chinese translation",
    "chinese is binding",
    "chinese is governing",
    "full verified chinese translation",
    "chinese governs",
    "official english translation",
    "english is binding",
    "english is governing",
)


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    problems: list[str] = []

    print("=" * 60)
    print("Implementing regulations intake scaffold validation")
    print("=" * 60)

    # --- Check 1: scaffold JSON exists ---
    print("\n[1] Checking scaffold JSON exists...")
    if not os.path.exists(SCAFFOLD):
        print("  FAIL: intake_scaffold.json not found")
        return 1
    data = load_json(SCAFFOLD)
    print("  intake_scaffold.json present and valid JSON ✓")

    # --- Check 2: stage ---
    print("\n[2] Checking stage field...")
    if data.get("stage") != "IMPLEMENTING_REGULATIONS_INTAKE_SCAFFOLD":
        problems.append(f"stage != IMPLEMENTING_REGULATIONS_INTAKE_SCAFFOLD (got {data.get('stage')})")
        print(f"  FAIL: stage={data.get('stage')}")
    else:
        print("  stage=IMPLEMENTING_REGULATIONS_INTAKE_SCAFFOLD ✓")

    # --- Check 3: corpus track separate from parent law ---
    print("\n[3] Checking corpus track separation...")
    if data.get("corpus_track") != "implementing_regulations":
        problems.append("corpus_track != implementing_regulations")
        print("  FAIL: corpus_track mismatch")
    elif not data.get("separate_from_parent_law", False):
        problems.append("separate_from_parent_law != True")
        print("  FAIL: separate_from_parent_law not True")
    else:
        print("  corpus_track=implementing_regulations, separate from parent law ✓")

    # --- Check 4: parent law and unchanged ---
    print("\n[4] Checking parent law reference and unchanged...")
    if data.get("parent_law") != "sa_companies_law_m132_1443":
        problems.append("parent_law != sa_companies_law_m132_1443")
        print("  FAIL: parent_law mismatch")
    elif not data.get("parent_law_corpus_unchanged", False):
        problems.append("parent_law_corpus_unchanged != True")
        print("  FAIL: parent_law_corpus_unchanged not True")
    else:
        print("  parent_law=sa_companies_law_m132_1443, corpus_unchanged=True ✓")

    # --- Check 5: source provenance not yet ingested ---
    print("\n[5] Checking source provenance status...")
    sp = data.get("source_provenance", {})
    if sp.get("status") != "not_yet_ingested":
        problems.append("source_provenance.status != not_yet_ingested")
        print("  FAIL: source_provenance.status mismatch")
    else:
        print("  source_provenance.status=not_yet_ingested ✓")

    # Verify all provenance fields are null
    null_fields = [
        "official_source_url", "official_source_gazette",
        "official_source_gazette_date", "official_source_gazette_issue",
        "intake_method", "intake_date", "intake_by",
        "source_file_hash_sha256",
    ]
    for field in null_fields:
        if sp.get(field) is not None:
            problems.append(f"source_provenance.{field} is not null (should be null for scaffold)")
            print(f"  FAIL: source_provenance.{field} is not null")
    if not any(f"source_provenance.{f}" in p for f in null_fields for p in problems):
        print("  all provenance fields are null ✓")

    # --- Check 6: article numbering unknown ---
    print("\n[6] Checking article numbering is unknown...")
    an = data.get("article_numbering", {})
    if an.get("total_articles") is not None:
        problems.append("article_numbering.total_articles is not null (should be null for scaffold)")
        print("  FAIL: article_numbering.total_articles not null")
    elif an.get("scheme") != "unknown_until_ingested":
        problems.append("article_numbering.scheme != unknown_until_ingested")
        print("  FAIL: article_numbering.scheme mismatch")
    else:
        print("  article_numbering: scheme=unknown_until_ingested, total_articles=null ✓")

    # --- Check 7: Arabic layer ---
    print("\n[7] Checking Arabic layer status...")
    ar = data.get("language_layers", {}).get("arabic", {})
    if ar.get("status") != "not_yet_ingested":
        problems.append("language_layers.arabic.status != not_yet_ingested")
        print("  FAIL: arabic.status mismatch")
    elif not ar.get("governing", False):
        problems.append("language_layers.arabic.governing != True")
        print("  FAIL: arabic.governing not True")
    else:
        print("  arabic: status=not_yet_ingested, governing=True ✓")

    # --- Check 8: English layer ---
    print("\n[8] Checking English layer status...")
    en = data.get("language_layers", {}).get("english", {})
    if en.get("status") != "not_yet_added":
        problems.append("language_layers.english.status != not_yet_added")
        print("  FAIL: english.status mismatch")
    elif en.get("governing", True):
        problems.append("language_layers.english.governing != False")
        print("  FAIL: english.governing not False")
    elif en.get("role") != "reference_guidance_only":
        problems.append("language_layers.english.role != reference_guidance_only")
        print("  FAIL: english.role mismatch")
    else:
        print("  english: status=not_yet_added, governing=False, role=reference_guidance_only ✓")

    # --- Check 9: Chinese layer ---
    print("\n[9] Checking Chinese layer status...")
    zh = data.get("language_layers", {}).get("chinese", {})
    if zh.get("status") != "not_yet_added":
        problems.append("language_layers.chinese.status != not_yet_added")
        print("  FAIL: chinese.status mismatch")
    elif zh.get("governing", True):
        problems.append("language_layers.chinese.governing != False")
        print("  FAIL: chinese.governing not False")
    elif zh.get("role") != "internal_reference_only":
        problems.append("language_layers.chinese.role != internal_reference_only")
        print("  FAIL: chinese.role mismatch")
    elif not zh.get("official", True) is False:
        problems.append("language_layers.chinese.official != False")
        print("  FAIL: chinese.official not False")
    elif not zh.get("binding", True) is False:
        problems.append("language_layers.chinese.binding != False")
        print("  FAIL: chinese.binding not False")
    else:
        print("  chinese: status=not_yet_added, governing=False, role=internal_reference_only, official=False, binding=False ✓")

    # --- Check 10: no prohibited content ---
    print("\n[10] Checking no prohibited content flags...")
    required_false = [
        "no_new_chinese_text", "no_new_english_text", "no_trilingual_alignment",
    ]
    for flag in required_false:
        if not data.get(flag, False):
            problems.append(f"{flag} is not True")
            print(f"  FAIL: {flag} not True")

    release = data.get("public_release_created")
    if release is not False:
        problems.append("public_release_created is not False")
        print("  FAIL: public_release_created not False")

    if not any(flag in p for flag in required_false for p in problems):
        print("  no_new_chinese_text=True, no_new_english_text=True, no_trilingual_alignment=True ✓")
        print("  public_release_created=False ✓")

    # --- Check 11: legal-status boundaries ---
    print("\n[11] Checking legal-status boundaries...")
    lsb = data.get("legal_status_boundaries", {})
    required_true = [
        "arabic_governs", "english_reference_only",
        "chinese_internal_reference_only", "not_official",
        "not_binding", "not_governing", "not_legal_advice",
        "separate_corpus_track", "parent_law_unchanged",
    ]
    for field in required_true:
        if not lsb.get(field, False):
            problems.append(f"legal_status_boundaries.{field} is not True")
            print(f"  FAIL: legal_status_boundaries.{field} not True")
    if not any(f"legal_status_boundaries.{f}" in p for f in required_true for p in problems):
        print("  All legal-status boundaries correct ✓")

    # --- Check 12: Companies Law corpus files unchanged ---
    print("\n[12] Checking Companies Law corpus files exist (unchanged)...")
    for f in PARENT_LAW_FILES:
        if not os.path.exists(f):
            problems.append(f"Parent law file missing: {os.path.relpath(f, ROOT)}")
            print(f"  FAIL: missing {os.path.relpath(f, ROOT)}")
        else:
            print(f"  {os.path.relpath(f, ROOT)} exists ✓")

    # --- Check 13: no content files beyond scaffold/README at top level ---
    print("\n[13] Checking no implementing-regulations content beyond scaffold at top level...")
    impl_reg_dir = os.path.join(ROOT, "data", "implementing_regulations")
    top_level_files = []
    for f in os.listdir(impl_reg_dir):
        full_path = os.path.join(impl_reg_dir, f)
        if os.path.isfile(full_path):
            top_level_files.append(f)
    allowed = {"intake_scaffold.json", "README.md"}
    unexpected = [f for f in top_level_files if f not in allowed]
    if unexpected:
        problems.append(f"Unexpected top-level files in implementing_regulations: {unexpected}")
        print(f"  FAIL: unexpected top-level files: {unexpected}")
    else:
        print(f"  Only scaffold files at top level ({sorted(top_level_files)}) ✓")

    # --- Check artifact files ---
    print("\n[14] Checking report and README artifacts...")
    if not os.path.exists(SCAFFOLD_README):
        problems.append("data/implementing_regulations/README.md not found")
        print("  FAIL: scaffold README not found")
    else:
        print("  data/implementing_regulations/README.md ✓")
    if not os.path.exists(ARABIC_REPORT):
        problems.append("Arabic report not found")
        print("  FAIL: Arabic report not found")
    else:
        print("  reports/implementing_regulations/IMPLEMENTING_REGULATIONS_INTAKE_SCAFFOLD_AR.md ✓")

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
            "[PASS] Implementing regulations intake scaffold: clean scaffold "
            "with metadata placeholders for source provenance, article numbering, "
            "language layers (Arabic governing not-yet-ingested, English/Chinese "
            "not-yet-added), validation status, and legal-status boundaries. "
            "No Arabic/English/Chinese text ingested or generated. No trilingual "
            "alignment. No public release. Companies Law corpus and Chinese "
            "remediation program unchanged. Arabic governs; not official/binding/"
            "governing; not legal advice. Read-only."
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())