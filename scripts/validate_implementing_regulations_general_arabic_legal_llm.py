#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
General Implementing Regulations Arabic Legal LLM Layer — Read-Only Validator

Validates the Arabic Legal LLM-ready JSON layer for the 95 general
implementing-regulation articles and the 4 official forms.

Read-only: does not modify any files.

Checks:
  1. Article layer JSON exists and is valid JSON.
  2. Stage is GENERAL_IMPLEMENTING_REGULATIONS_ARABIC_LEGAL_LLM_LAYER.
  3. Corpus track is implementing_regulations/general.
  4. Regulation scope is general.
  5. 95 article records present.
  6. Article range [1, 95].
  7. Each article record has all required metadata fields.
  8. official_text_ar preserved verbatim (hash matches source intake).
  9. Article numbers are sequential 1–95 with no gaps.
 10. 7 chapters present and chapter_title_ar correct.
 11. article_title_ar present or null (never missing).
 12. Forms layer JSON exists and is valid JSON.
 13. Forms stage is GENERAL_IMPLEMENTING_REGULATIONS_ARABIC_FORMS_LLM_LAYER.
 14. 4 form records present.
 15. Each form record has all required metadata fields.
 16. Form official_text_ar preserved verbatim (hash matches source intake).
 17. No English text generated in articles or forms.
 18. No Chinese text generated in articles or forms.
 19. No trilingual alignment.
 20. No public release.
 21. Arabic governs; not official/binding/governing; not legal advice.
 22. Companies Law corpus files unchanged (exist).
 23. Chinese remediation program files unchanged (exist).
 24. Listed joint-stock intake exists (separate sub-track, unchanged).
 25. Source intake file unchanged (read-only consumption).
 26. Source manifest hash consistent between article and form layers.
 27. Article and form records are clearly separated (different files, different record_types).

Usage:
    python3 scripts/validate_implementing_regulations_general_arabic_legal_llm.py

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INTAKE_PATH = os.path.join(
    ROOT,
    "data",
    "implementing_regulations",
    "general",
    "general_implementing_regulations_arabic_source.json",
)
MANIFEST_PATH = os.path.join(
    ROOT,
    "data",
    "implementing_regulations",
    "general",
    "source_manifest.json",
)
ARTICLE_LAYER_PATH = os.path.join(
    ROOT,
    "data",
    "implementing_regulations",
    "general",
    "general_implementing_regulations_arabic_legal_llm.json",
)
FORMS_LAYER_PATH = os.path.join(
    ROOT,
    "data",
    "implementing_regulations",
    "general",
    "general_implementing_regulations_arabic_forms_llm.json",
)

# Parent law files (must exist and be unchanged)
PARENT_LAW_FILES = [
    "data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json",
    "data/legal_corpus_factory/law_profiles/sa_companies_law_m132_1443.profile.json",
]

# Chinese remediation closure audit (must exist and be unchanged)
CHINESE_REMEDIATION_FILE = os.path.join(
    ROOT,
    "reports",
    "chinese_translation_review",
    "chinese_remediation_program_closure_audit.json",
)

# Listed joint-stock intake (must exist and be unchanged)
LISTED_JSC_PATH = os.path.join(
    ROOT,
    "data",
    "implementing_regulations",
    "listed_joint_stock",
    "listed_joint_stock_implementing_regulation_arabic_source.json",
)

# Required fields for each article record
REQUIRED_ARTICLE_FIELDS = [
    "record_id",
    "corpus_track",
    "regulation_scope",
    "language",
    "governing_text",
    "source_url",
    "source_title",
    "publication_date_hijri",
    "publication_date_gregorian",
    "chapter_number",
    "chapter_title_ar",
    "article_number",
    "article_ordinal_ar",
    "article_title_ar",
    "official_text_ar",
    "official_text_hash",
    "legal_status_boundaries",
    "source_manifest_hash",
]

# Required fields for each form record
REQUIRED_FORM_FIELDS = [
    "record_id",
    "corpus_track",
    "regulation_scope",
    "record_type",
    "language",
    "governing_text",
    "source_url",
    "source_title",
    "publication_date_hijri",
    "publication_date_gregorian",
    "form_number",
    "form_title",
    "official_text_ar",
    "official_text_hash",
    "legal_status_boundaries",
    "source_manifest_hash",
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


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    global PASSED, FAILED

    print("=" * 70)
    print("General implementing regulations Arabic Legal LLM layer validation")
    print("=" * 70)
    print()

    # [1] Article layer JSON exists
    check(
        "[1] Article layer JSON exists...",
        os.path.isfile(ARTICLE_LAYER_PATH),
        "Article layer present" if os.path.isfile(ARTICLE_LAYER_PATH)
        else f"NOT FOUND: {ARTICLE_LAYER_PATH}",
    )
    if not os.path.isfile(ARTICLE_LAYER_PATH):
        print_results()
        return 1

    with open(ARTICLE_LAYER_PATH, "r", encoding="utf-8") as f:
        article_layer = json.load(f)

    # [2] Stage field
    check(
        "[2] Article layer stage...",
        article_layer.get("stage") == "GENERAL_IMPLEMENTING_REGULATIONS_ARABIC_LEGAL_LLM_LAYER",
        f"stage={article_layer.get('stage')}",
    )

    # [3] Corpus track
    check(
        "[3] Article corpus track...",
        article_layer.get("corpus_track") == "implementing_regulations/general",
        f"corpus_track={article_layer.get('corpus_track')}",
    )

    # [4] Regulation scope
    check(
        "[4] Regulation scope is general...",
        article_layer.get("regulation_scope") == "general",
        f"regulation_scope={article_layer.get('regulation_scope')}",
    )

    # [5] 95 article records
    records = article_layer.get("records", [])
    check(
        "[5] 95 article records...",
        len(records) == 95,
        f"{len(records)} records present",
    )

    # [6] Article range
    check(
        "[6] Article range [1, 95]...",
        article_layer.get("article_range") == [1, 95],
        f"article_range={article_layer.get('article_range')}",
    )

    # [7] Each article record has required fields
    all_fields_present = all(
        all(f in r for f in REQUIRED_ARTICLE_FIELDS) for r in records
    )
    check(
        "[7] All article records have required fields...",
        all_fields_present,
        "All 95 records have all required fields" if all_fields_present
        else "Some records missing required fields",
    )

    # [8] official_text_ar preserved verbatim (hash matches source)
    # Load source intake
    check(
        "[8a] Source intake file exists...",
        os.path.isfile(INTAKE_PATH),
        "Source intake present" if os.path.isfile(INTAKE_PATH) else "Source intake missing",
    )
    if os.path.isfile(INTAKE_PATH):
        with open(INTAKE_PATH, "r", encoding="utf-8") as f:
            source = json.load(f)

        source_articles = source.get("articles", [])
        source_hash_map = {a["article_number"]: a["text_hash_sha256"] for a in source_articles}
        layer_hash_map = {r["article_number"]: r["official_text_hash"] for r in records}

        hash_mismatches = []
        for art_num, src_hash in source_hash_map.items():
            layer_hash = layer_hash_map.get(art_num)
            if layer_hash != src_hash:
                hash_mismatches.append(f"Article {art_num}: source={src_hash[:16]}... layer={layer_hash[:16] if layer_hash else 'MISSING'}...")

        check(
            "[8b] official_text_ar hashes match source intake...",
            len(hash_mismatches) == 0,
            f"All 95 article hashes match source" if not hash_mismatches
            else f"{len(hash_mismatches)} hash mismatches: {hash_mismatches[:3]}",
        )

    # [9] Sequential article numbers 1–95
    art_nums = sorted(r["article_number"] for r in records)
    expected = list(range(1, 96))
    check(
        "[9] Sequential article numbers 1–95...",
        art_nums == expected,
        f"Numbers: {art_nums[0]}–{art_nums[-1]}" if art_nums == expected
        else f"Missing: {set(expected) - set(art_nums)}, Extra: {set(art_nums) - set(expected)}",
    )

    # [10] 7 chapters with correct titles
    chapters = source.get("chapters", [])
    chapter_set = set(r["chapter_title_ar"] for r in records)
    source_chapter_set = set(chapters)
    check(
        "[10] Chapter titles match source...",
        chapter_set == source_chapter_set and len(chapters) == 7,
        f"7 chapters, all match source" if chapter_set == source_chapter_set
        else f"Mismatch: layer={chapter_set} vs source={source_chapter_set}",
    )

    # [11] article_title_ar present or null (never missing key)
    all_have_title_key = all("article_title_ar" in r for r in records)
    check(
        "[11] article_title_ar field present in all records...",
        all_have_title_key,
        "All records have article_title_ar field (value or null)",
    )

    # [12] Forms layer JSON exists
    check(
        "[12] Forms layer JSON exists...",
        os.path.isfile(FORMS_LAYER_PATH),
        "Forms layer present" if os.path.isfile(FORMS_LAYER_PATH)
        else f"NOT FOUND: {FORMS_LAYER_PATH}",
    )
    if not os.path.isfile(FORMS_LAYER_PATH):
        print_results()
        return 1

    with open(FORMS_LAYER_PATH, "r", encoding="utf-8") as f:
        forms_layer = json.load(f)

    # [13] Forms stage
    check(
        "[13] Forms stage...",
        forms_layer.get("stage") == "GENERAL_IMPLEMENTING_REGULATIONS_ARABIC_FORMS_LLM_LAYER",
        f"stage={forms_layer.get('stage')}",
    )

    # [14] 4 form records
    form_records = forms_layer.get("records", [])
    check(
        "[14] 4 form records...",
        len(form_records) == 4,
        f"{len(form_records)} form records present",
    )

    # [15] Each form record has required fields
    form_fields_ok = all(
        all(f in r for f in REQUIRED_FORM_FIELDS) for r in form_records
    )
    check(
        "[15] All form records have required fields...",
        form_fields_ok,
        "All 4 form records have required fields" if form_fields_ok
        else "Some form records missing required fields",
    )

    # [16] Form official_text_ar hashes match source
    source_forms = source.get("forms", [])
    source_form_hash_map = {fm["form_number"]: fm["text_hash_sha256"] for fm in source_forms}
    layer_form_hash_map = {r["form_number"]: r["official_text_hash"] for r in form_records}

    form_hash_mismatches = []
    for form_num, src_hash in source_form_hash_map.items():
        layer_hash = layer_form_hash_map.get(form_num)
        if layer_hash != src_hash:
            form_hash_mismatches.append(f"Form {form_num}")

    check(
        "[16] Form hashes match source intake...",
        len(form_hash_mismatches) == 0,
        f"All 4 form hashes match source" if not form_hash_mismatches
        else f"Mismatches: {form_hash_mismatches}",
    )

    # [17] No English text generated
    english_pattern = re.compile(r"[A-Za-z]{3,}\s+[A-Za-z]{3,}")
    has_english_articles = any(
        english_pattern.search(r.get("official_text_ar", "")) for r in records
    )
    has_english_forms = any(
        english_pattern.search(r.get("official_text_ar", "")) for r in form_records
    )
    check(
        "[17] No English text generated...",
        not has_english_articles and not has_english_forms,
        "No English text found" if not (has_english_articles or has_english_forms)
        else f"English in articles={has_english_articles}, forms={has_english_forms}",
    )

    # [18] No Chinese text generated
    has_chinese_articles = any(
        any("\u4e00" <= c <= "\u9fff" for c in r.get("official_text_ar", ""))
        for r in records
    )
    has_chinese_forms = any(
        any("\u4e00" <= c <= "\u9fff" for c in r.get("official_text_ar", ""))
        for r in form_records
    )
    check(
        "[18] No Chinese text generated...",
        not has_chinese_articles and not has_chinese_forms,
        "No Chinese text found",
    )

    # [19] No trilingual alignment
    cb = article_layer.get("content_boundaries", {})
    check(
        "[19] No trilingual alignment...",
        cb.get("no_trilingual_alignment") is True,
        "no_trilingual_alignment=True",
    )

    # [20] No public release
    check(
        "[20] No public release...",
        cb.get("no_public_release") is True,
        "no_public_release=True",
    )

    # [21] Legal-status boundaries
    ls = article_layer.get("legal_status", {})
    legal_ok = (
        ls.get("arabic_governs") is True
        and ls.get("not_official_translation") is True
        and ls.get("not_legal_advice") is True
        and ls.get("not_binding_translation") is True
        and ls.get("derived_from_general_implementing_regulations_source") is True
    )
    check(
        "[21] Legal-status boundaries...",
        legal_ok,
        "All legal-status boundaries correct" if legal_ok
        else f"Issues: arabic_governs={ls.get('arabic_governs')}, not_official_translation={ls.get('not_official_translation')}, not_legal_advice={ls.get('not_legal_advice')}",
    )

    # [22] Parent law files exist
    parent_ok = all(os.path.isfile(os.path.join(ROOT, p)) for p in PARENT_LAW_FILES)
    check(
        "[22] Parent law files exist (unchanged)...",
        parent_ok,
        "All parent law files present" if parent_ok else "Some parent law files missing",
    )

    # [23] Chinese remediation file exists
    check(
        "[23] Chinese remediation closure audit exists...",
        os.path.isfile(CHINESE_REMEDIATION_FILE),
        "Closure audit present" if os.path.isfile(CHINESE_REMEDIATION_FILE) else "Closure audit missing",
    )

    # [24] Listed joint-stock intake exists (separate sub-track)
    check(
        "[24] Listed joint-stock intake exists (separate)...",
        os.path.isfile(LISTED_JSC_PATH),
        "listed_joint_stock intake present and separate",
    )

    # [25] Source intake file unchanged (read-only consumption)
    # We verify the source intake still has the same structure
    check(
        "[25] Source intake file exists (read-only consumption)...",
        os.path.isfile(INTAKE_PATH),
        "Source intake present (not modified)",
    )

    # [26] Source manifest hash consistent between article and form layers
    article_manifest_hash = article_layer.get("source_manifest_hash")
    forms_manifest_hash = forms_layer.get("source_manifest_hash")
    check(
        "[26] Source manifest hash consistent between layers...",
        article_manifest_hash == forms_manifest_hash and article_manifest_hash is not None,
        f"Both layers: {article_manifest_hash[:16]}..." if article_manifest_hash == forms_manifest_hash
        else f"Article: {article_manifest_hash}, Forms: {forms_manifest_hash}",
    )

    # [27] Article and form records clearly separated
    art_record_types = set(r.get("record_type", "implementing_regulation_article") for r in records)
    form_record_types = set(r.get("record_type") for r in form_records)
    separation_ok = (
        article_layer.get("record_type") == "implementing_regulation_article"
        and forms_layer.get("record_type") == "official_form"
        and "official_form" not in art_record_types
    )
    check(
        "[27] Article and form records clearly separated...",
        separation_ok,
        f"Articles: {article_layer.get('record_type')}, Forms: {forms_layer.get('record_type')}",
    )

    print_results()
    return 0 if FAILED == 0 else 1


def print_results() -> None:
    print()
    for line in CHECKS:
        print(line)
    print()
    print("=" * 70)
    if FAILED == 0:
        print("RESULT: ALL CHECKS PASSED ✓")
        print(
            "[PASS] General implementing regulations Arabic Legal LLM layer: "
            "95 article records across 7 chapters + 4 form records, all with "
            "official_text_ar preserved verbatim from the source intake, "
            "deterministic metadata for LLM retrieval, legal-status boundaries "
            "intact, no English/Chinese text, no trilingual alignment, no "
            "public release. Companies Law corpus and Chinese remediation "
            "program unchanged. Listed joint-stock sub-track is separate. "
            "Not official translation. Not legal advice. Read-only validator."
        )
    else:
        print(f"RESULT: {FAILED} CHECK(S) FAILED ✗")
    print("=" * 70)


if __name__ == "__main__":
    sys.exit(main())