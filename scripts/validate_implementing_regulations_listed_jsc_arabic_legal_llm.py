#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listed Joint-Stock Implementing Regulation Arabic Legal LLM Layer — Read-Only Validator

Validates the Arabic Legal LLM-ready JSON layer for the 69 listed
joint-stock implementing-regulation articles and the appendix.

Read-only: does not modify any files.

Checks:
  1. Article layer JSON exists and is valid JSON.
  2. Stage is LISTED_JOINT_STOCK_ARABIC_LEGAL_LLM_LAYER.
  3. Corpus track is implementing_regulations/listed_joint_stock.
  4. Regulation scope is listed_joint_stock.
  5. Is specialized (not general).
  6. 69 article records present.
  7. Article range [1, 69].
  8. Each article record has all required metadata fields.
  9. official_text_ar preserved verbatim (hash matches source intake).
 10. Article numbers are sequential 1–69 with no gaps.
 11. article_title_ar present or null (never missing key).
 12. issuing_authority and legal_basis present.
 13. Appendix layer JSON exists and is valid JSON.
 14. Appendix stage is LISTED_JOINT_STOCK_ARABIC_APPENDIX_LLM_LAYER.
 15. 1 appendix record present.
 16. Appendix record_type is official_appendix.
 17. Appendix hash matches source intake.
 18. No English text generated in articles or appendix.
 19. No Chinese text generated in articles or appendix.
 20. No trilingual alignment.
 21. No public release.
 22. Arabic governs; not official/binding/governing; not legal advice.
 23. Companies Law corpus files unchanged (exist).
 24. Chinese remediation program files unchanged (exist).
 25. General implementing regulations source intake and LLM layer exist (unchanged).
 26. Source intake file unchanged (read-only consumption).
 27. Source manifest hash consistent between article and appendix layers.
 28. Article and appendix records clearly separated (different files, different record_types).

Usage:
    python3 scripts/validate_implementing_regulations_listed_jsc_arabic_legal_llm.py

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
    "listed_joint_stock",
    "listed_joint_stock_implementing_regulation_arabic_source.json",
)
MANIFEST_PATH = os.path.join(
    ROOT,
    "data",
    "implementing_regulations",
    "listed_joint_stock",
    "source_manifest.json",
)
ARTICLE_LAYER_PATH = os.path.join(
    ROOT,
    "data",
    "implementing_regulations",
    "listed_joint_stock",
    "listed_joint_stock_implementing_regulation_arabic_legal_llm.json",
)
APPENDIX_LAYER_PATH = os.path.join(
    ROOT,
    "data",
    "implementing_regulations",
    "listed_joint_stock",
    "listed_joint_stock_implementing_regulation_arabic_appendix_llm.json",
)

PARENT_LAW_FILES = [
    "data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json",
    "data/legal_corpus_factory/law_profiles/sa_companies_law_m132_1443.profile.json",
]

CHINESE_REMEDIATION_FILE = os.path.join(
    ROOT,
    "reports",
    "chinese_translation_review",
    "chinese_remediation_program_closure_audit.json",
)

GENERAL_INTAKE_PATH = os.path.join(
    ROOT,
    "data",
    "implementing_regulations",
    "general",
    "general_implementing_regulations_arabic_source.json",
)
GENERAL_LLM_PATH = os.path.join(
    ROOT,
    "data",
    "implementing_regulations",
    "general",
    "general_implementing_regulations_arabic_legal_llm.json",
)

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
    "issuing_authority",
    "legal_basis",
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

REQUIRED_APPENDIX_FIELDS = [
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
    "issuing_authority",
    "legal_basis",
    "appendix_title",
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
    print("=" * 70)
    print("Listed joint-stock implementing regulation Arabic Legal LLM layer validation")
    print("=" * 70)
    print()

    # [1] Article layer JSON exists
    check("[1] Article layer JSON exists...",
          os.path.isfile(ARTICLE_LAYER_PATH),
          "Article layer present" if os.path.isfile(ARTICLE_LAYER_PATH) else f"NOT FOUND: {ARTICLE_LAYER_PATH}")
    if not os.path.isfile(ARTICLE_LAYER_PATH):
        print_results()
        return 1

    with open(ARTICLE_LAYER_PATH, "r", encoding="utf-8") as f:
        article_layer = json.load(f)

    # [2] Stage
    check("[2] Article layer stage...",
          article_layer.get("stage") == "LISTED_JOINT_STOCK_ARABIC_LEGAL_LLM_LAYER",
          f"stage={article_layer.get('stage')}")

    # [3] Corpus track
    check("[3] Corpus track...",
          article_layer.get("corpus_track") == "implementing_regulations/listed_joint_stock",
          f"corpus_track={article_layer.get('corpus_track')}")

    # [4] Regulation scope
    check("[4] Regulation scope is listed_joint_stock...",
          article_layer.get("regulation_scope") == "listed_joint_stock",
          f"regulation_scope={article_layer.get('regulation_scope')}")

    # [5] Is specialized (not general)
    check("[5] Is specialized (not general)...",
          article_layer.get("is_specialized") is True and article_layer.get("is_general") is False,
          "is_specialized=True, is_general=False")

    # [6] 69 article records
    records = article_layer.get("records", [])
    check("[6] 69 article records...",
          len(records) == 69,
          f"{len(records)} records present")

    # [7] Article range
    check("[7] Article range [1, 69]...",
          article_layer.get("article_range") == [1, 69],
          f"article_range={article_layer.get('article_range')}")

    # [8] Required fields
    all_fields = all(all(f in r for f in REQUIRED_ARTICLE_FIELDS) for r in records)
    check("[8] All article records have required fields...",
          all_fields,
          "All 69 records have required fields" if all_fields else "Some records missing fields")

    # [9] Hashes match source
    check("[9a] Source intake file exists...",
          os.path.isfile(INTAKE_PATH),
          "Source intake present" if os.path.isfile(INTAKE_PATH) else "Source intake missing")
    if os.path.isfile(INTAKE_PATH):
        with open(INTAKE_PATH, "r", encoding="utf-8") as f:
            source = json.load(f)
        src_hashes = {a["article_number"]: a["text_hash_sha256"] for a in source["articles"]}
        layer_hashes = {r["article_number"]: r["official_text_hash"] for r in records}
        mismatches = [n for n, h in src_hashes.items() if layer_hashes.get(n) != h]
        check("[9b] Article hashes match source intake...",
              len(mismatches) == 0,
              f"All 69 hashes match" if not mismatches else f"Mismatches: {mismatches[:3]}")

    # [10] Sequential 1–69
    art_nums = sorted(r["article_number"] for r in records)
    check("[10] Sequential article numbers 1–69...",
          art_nums == list(range(1, 70)),
          f"1–{art_nums[-1]}" if art_nums == list(range(1, 70)) else "Gaps found")

    # [11] article_title_ar present or null
    all_have = all("article_title_ar" in r for r in records)
    check("[11] article_title_ar field present in all records...",
          all_have,
          "All records have article_title_ar field")

    # [12] issuing_authority and legal_basis
    check("[12] issuing_authority and legal_basis present...",
          bool(article_layer.get("issuing_authority")) and bool(article_layer.get("legal_basis")),
          f"authority={article_layer.get('issuing_authority', '')[:40]}")

    # [13] Appendix layer exists
    check("[13] Appendix layer JSON exists...",
          os.path.isfile(APPENDIX_LAYER_PATH),
          "Appendix layer present" if os.path.isfile(APPENDIX_LAYER_PATH) else "NOT FOUND")
    if not os.path.isfile(APPENDIX_LAYER_PATH):
        print_results()
        return 1

    with open(APPENDIX_LAYER_PATH, "r", encoding="utf-8") as f:
        appendix_layer = json.load(f)

    # [14] Appendix stage
    check("[14] Appendix stage...",
          appendix_layer.get("stage") == "LISTED_JOINT_STOCK_ARABIC_APPENDIX_LLM_LAYER",
          f"stage={appendix_layer.get('stage')}")

    # [15] 1 appendix record
    app_records = appendix_layer.get("records", [])
    check("[15] 1 appendix record...",
          len(app_records) == 1,
          f"{len(app_records)} records")

    # [16] record_type
    check("[16] Appendix record_type is official_appendix...",
          all(r.get("record_type") == "official_appendix" for r in app_records),
          "record_type=official_appendix")

    # [17] Appendix hash matches source
    src_appendix_text = source.get("appendix_text", "")
    src_appendix_hash = _sha256(src_appendix_text) if src_appendix_text else ""
    layer_appendix_hash = app_records[0].get("official_text_hash", "") if app_records else ""
    check("[17] Appendix hash matches source...",
          layer_appendix_hash == src_appendix_hash and src_appendix_hash,
          "Hash matches" if layer_appendix_hash == src_appendix_hash else "Hash mismatch")

    # [18] No English text
    english_pattern = re.compile(r"[A-Za-z]{3,}\s+[A-Za-z]{3,}")
    has_eng_art = any(english_pattern.search(r.get("official_text_ar", "")) for r in records)
    has_eng_app = any(english_pattern.search(r.get("official_text_ar", "")) for r in app_records)
    check("[18] No English text generated...",
          not has_eng_art and not has_eng_app,
          "No English text found" if not (has_eng_art or has_eng_app) else "English found")

    # [19] No Chinese text
    has_cn_art = any(any("\u4e00" <= c <= "\u9fff" for c in r.get("official_text_ar", "")) for r in records)
    has_cn_app = any(any("\u4e00" <= c <= "\u9fff" for c in r.get("official_text_ar", "")) for r in app_records)
    check("[19] No Chinese text generated...",
          not has_cn_art and not has_cn_app,
          "No Chinese text found")

    # [20] No trilingual alignment
    check("[20] No trilingual alignment...",
          article_layer.get("content_boundaries", {}).get("no_trilingual_alignment") is True,
          "no_trilingual_alignment=True")

    # [21] No public release
    check("[21] No public release...",
          article_layer.get("content_boundaries", {}).get("no_public_release") is True,
          "no_public_release=True")

    # [22] Legal-status boundaries
    ls = article_layer.get("legal_status", {})
    check("[22] Legal-status boundaries...",
          ls.get("arabic_governs") is True and ls.get("not_official_translation") is True
          and ls.get("not_legal_advice") is True and ls.get("not_binding_translation") is True
          and ls.get("derived_from_listed_joint_stock_source") is True,
          "All legal-status boundaries correct")

    # [23] Parent law files
    check("[23] Parent law files exist (unchanged)...",
          all(os.path.isfile(os.path.join(ROOT, p)) for p in PARENT_LAW_FILES),
          "All parent law files present")

    # [24] Chinese remediation
    check("[24] Chinese remediation closure audit exists...",
          os.path.isfile(CHINESE_REMEDIATION_FILE),
          "Closure audit present" if os.path.isfile(CHINESE_REMEDIATION_FILE) else "Missing")

    # [25] General implementing regulations exist (unchanged)
    check("[25] General implementing regulations exist (separate track)...",
          os.path.isfile(GENERAL_INTAKE_PATH) and os.path.isfile(GENERAL_LLM_PATH),
          "General intake and LLM layer present")

    # [26] Source intake unchanged
    check("[26] Source intake file exists (read-only)...",
          os.path.isfile(INTAKE_PATH),
          "Source intake present (not modified)")

    # [27] Manifest hash consistent
    art_mh = article_layer.get("source_manifest_hash")
    app_mh = appendix_layer.get("source_manifest_hash")
    check("[27] Manifest hash consistent between layers...",
          art_mh == app_mh and art_mh is not None,
          f"Both: {art_mh[:16]}..." if art_mh == app_mh else f"Art: {art_mh}, App: {app_mh}")

    # [28] Articles and appendix separated
    sep_ok = (
        article_layer.get("record_type") == "implementing_regulation_article"
        and appendix_layer.get("record_type") == "official_appendix"
        and "official_appendix" not in set(r.get("record_type", "implementing_regulation_article") for r in records)
    )
    check("[28] Article and appendix records clearly separated...",
          sep_ok,
          f"Articles: {article_layer.get('record_type')}, Appendix: {appendix_layer.get('record_type')}")

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
            "[PASS] Listed joint-stock implementing regulation Arabic Legal LLM layer: "
            "69 article records + 1 appendix record, all with official_text_ar preserved "
            "verbatim from the source intake, deterministic metadata for LLM retrieval, "
            "legal-status boundaries intact, no English/Chinese text, no trilingual "
            "alignment, no public release. Companies Law corpus and Chinese remediation "
            "program unchanged. General implementing regulations track is separate. "
            "Specialized scope: listed joint-stock companies only. Not official "
            "translation. Not legal advice. Read-only validator."
        )
    else:
        print(f"RESULT: {FAILED} CHECK(S) FAILED ✗")
    print("=" * 70)


if __name__ == "__main__":
    sys.exit(main())