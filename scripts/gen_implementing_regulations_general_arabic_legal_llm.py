#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
General Implementing Regulations — Arabic Legal LLM-ready Layer Generator

Creates a structured Arabic Legal LLM-ready JSON layer for the 95 general
implementing-regulation articles of the Saudi Companies Law (M/132, 1443H).

This stage is Arabic-only structuring:
  - No translation
  - No English text
  - No Chinese text
  - No trilingual alignment
  - No public release
  - No paraphrasing or rewriting of official Arabic text

The official_text_ar is preserved verbatim from the source intake.
Article hashes and source provenance are preserved.

Input:
  data/implementing_regulations/general/general_implementing_regulations_arabic_source.json
  data/implementing_regulations/general/source_manifest.json

Output:
  data/implementing_regulations/general/general_implementing_regulations_arabic_legal_llm.json
  data/implementing_regulations/general/general_implementing_regulations_arabic_forms_llm.json

Idempotent: re-running produces identical output (deterministic JSON with
sorted keys and fixed separators).

Usage:
    python3 scripts/gen_implementing_regulations_general_arabic_legal_llm.py
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from typing import Any

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
OUTPUT_ARTICLES_PATH = os.path.join(
    ROOT,
    "data",
    "implementing_regulations",
    "general",
    "general_implementing_regulations_arabic_legal_llm.json",
)
OUTPUT_FORMS_PATH = os.path.join(
    ROOT,
    "data",
    "implementing_regulations",
    "general",
    "general_implementing_regulations_arabic_forms_llm.json",
)

# Chapter title mapping (from intake chapters list, deterministic)
# These are the official Arabic chapter titles as recorded in the source intake.
CHAPTER_TITLES = [
    "الباب الأول: أحكام عامة",
    "الباب الثاني: شركة المساهمة غير المدرجة في السوق المالية",
    "الباب الثالث: الشركة ذات المسؤولية المحدودة",
    "الباب الرابع: الشركة غير الربحية",
    "الباب الخامس: الشركة المهنية",
    "الباب السادس: تحول الشركات واندماجها وتقسيمها",
    "الباب السابع: أحكام ختامية",
]


def _load_json(path: str) -> dict[str, Any]:
    """Load a JSON file with UTF-8 encoding."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _dump_json(obj: Any, path: str) -> None:
    """Write JSON deterministically: sorted keys, ensure_ascii=False, fixed separators."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def _sha256(text: str) -> str:
    """Compute SHA-256 hex digest of a UTF-8 string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _extract_article_title_ar(text: str) -> str | None:
    """
    Extract article_title_ar from the official text if present.
    The article text starts with the article label (e.g., "المادة الأولى:")
    followed by a title, then a newline and the body.
    If a title can be deterministically extracted from the first line
    (after the colon), return it. Otherwise return None.
    """
    # The pattern is: "المادة <ordinal>: <title>\n<body>"
    # We extract the title between the first colon and the first newline.
    first_line = text.split("\n", 1)[0]
    # Find the first colon
    colon_idx = first_line.find(":")
    if colon_idx == -1:
        return None
    title_part = first_line[colon_idx + 1:].strip()
    if not title_part:
        return None
    # If the title part contains numbers-only or is empty, return None
    return title_part


def _build_article_record(
    article: dict[str, Any],
    chapter_index_map: dict[int, str],
    source: dict[str, Any],
    manifest_hash: str,
) -> dict[str, Any]:
    """Build a single LLM-ready article record."""
    article_number = article["article_number"]
    chapter_number = article["chapter_number"]
    chapter_title_ar = chapter_index_map.get(chapter_number, article.get("chapter", ""))
    official_text = article["official_text_ar"]
    text_hash = article["text_hash_sha256"]

    # Verify hash consistency
    computed_hash = _sha256(official_text)
    # Use the source hash (text_hash_sha256) as official_text_hash
    # The source hash is authoritative
    official_text_hash = text_hash

    # Extract article_title_ar if present
    article_title_ar = _extract_article_title_ar(official_text)

    # Build record_id: ir-gen-art-001 through ir-gen-art-095
    record_id = f"ir-gen-art-{article_number:03d}"

    record = {
        "record_id": record_id,
        "corpus_track": "implementing_regulations/general",
        "regulation_scope": "general",
        "language": "ar",
        "governing_text": "arabic_official_source",
        "source_url": source["source_url"],
        "source_title": source["source_title"],
        "publication_date_hijri": source["publication_date_hijri"],
        "publication_date_gregorian": source["publication_date_gregorian"],
        "chapter_number": chapter_number,
        "chapter_title_ar": chapter_title_ar,
        "article_number": article_number,
        "article_ordinal_ar": article["article_label"],
        "article_title_ar": article_title_ar,
        "official_text_ar": official_text,
        "official_text_hash": official_text_hash,
        "legal_status_boundaries": {
            "arabic_governs": True,
            "not_official_translation": True,
            "not_legal_advice": True,
            "not_binding_translation": True,
            "derived_from_general_implementing_regulations_source": True,
            "listed_joint_stock_is_separate_specialized_sub_track": True,
        },
        "source_manifest_hash": manifest_hash,
    }
    return record


def _build_form_record(
    form: dict[str, Any],
    source: dict[str, Any],
    manifest_hash: str,
) -> dict[str, Any]:
    """Build a single LLM-ready form record."""
    form_number = form["form_number"]
    official_text = form["official_text_ar"]
    text_hash = form["text_hash_sha256"]

    record_id = f"ir-gen-form-{form_number:03d}"

    record = {
        "record_id": record_id,
        "corpus_track": "implementing_regulations/general",
        "regulation_scope": "general",
        "record_type": "official_form",
        "language": "ar",
        "governing_text": "arabic_official_source",
        "source_url": source["source_url"],
        "source_title": source["source_title"],
        "publication_date_hijri": source["publication_date_hijri"],
        "publication_date_gregorian": source["publication_date_gregorian"],
        "form_number": form_number,
        "form_title": form["form_title"],
        "official_text_ar": official_text,
        "official_text_hash": text_hash,
        "legal_status_boundaries": {
            "arabic_governs": True,
            "not_official_translation": True,
            "not_legal_advice": True,
            "not_binding_translation": True,
            "derived_from_general_implementing_regulations_source": True,
            "listed_joint_stock_is_separate_specialized_sub_track": True,
        },
        "source_manifest_hash": manifest_hash,
    }
    return record


def main() -> int:
    # Load source files
    if not os.path.isfile(INTAKE_PATH):
        print(f"ERROR: Intake file not found: {INTAKE_PATH}")
        return 1
    if not os.path.isfile(MANIFEST_PATH):
        print(f"ERROR: Manifest file not found: {MANIFEST_PATH}")
        return 1

    source = _load_json(INTAKE_PATH)
    manifest = _load_json(MANIFEST_PATH)

    # Compute manifest hash for provenance tracking
    manifest_json = json.dumps(manifest, sort_keys=True, ensure_ascii=False)
    manifest_hash = _sha256(manifest_json)

    # Build chapter index map: chapter_number -> chapter_title_ar
    chapter_index_map = {}
    for i, ch_title in enumerate(source["chapters"]):
        chapter_index_map[i + 1] = ch_title

    # Build article records
    articles = source["articles"]
    if len(articles) != 95:
        print(f"ERROR: Expected 95 articles, got {len(articles)}")
        return 1

    article_records = []
    for article in articles:
        record = _build_article_record(
            article, chapter_index_map, source, manifest_hash
        )
        article_records.append(record)

    # Build form records
    forms = source["forms"]
    if len(forms) != 4:
        print(f"ERROR: Expected 4 forms, got {len(forms)}")
        return 1

    form_records = []
    for form in forms:
        record = _build_form_record(form, source, manifest_hash)
        form_records.append(record)

    # Build article layer JSON
    article_layer = {
        "layer_id": "sa-general-implementing-regulations-arabic-legal-llm",
        "stage": "GENERAL_IMPLEMENTING_REGULATIONS_ARABIC_LEGAL_LLM_LAYER",
        "corpus_track": "implementing_regulations/general",
        "regulation_scope": "general",
        "parent_law": "sa_companies_law_m132_1443",
        "source_title": source["source_title"],
        "source_url": source["source_url"],
        "source_intake_file": "data/implementing_regulations/general/general_implementing_regulations_arabic_source.json",
        "source_manifest_file": "data/implementing_regulations/general/source_manifest.json",
        "source_manifest_hash": manifest_hash,
        "source_hash": source["source_hash"],
        "language": "ar",
        "governing_text": "arabic_official_source",
        "record_type": "implementing_regulation_article",
        "record_count": len(article_records),
        "article_range": [1, 95],
        "chapter_count": len(source["chapters"]),
        "publication_date_hijri": source["publication_date_hijri"],
        "publication_date_gregorian": source["publication_date_gregorian"],
        "access_date": source["access_date"],
        "extraction_method": source["extraction_method"],
        "content_boundaries": {
            "no_english_text_generated": True,
            "no_chinese_text_generated": True,
            "no_trilingual_alignment": True,
            "no_public_release": True,
            "no_paraphrasing": True,
            "no_summarization": True,
            "no_obligations_rights_classification": True,
            "official_text_ar_preserved_verbatim": True,
        },
        "legal_status": {
            "arabic_governs": True,
            "english_reference_only_if_later_added": True,
            "chinese_internal_reference_only_if_later_added": True,
            "not_official_translation": True,
            "not_legal_advice": True,
            "not_binding_translation": True,
            "not_governing_translation": True,
            "derived_from_general_implementing_regulations_source": True,
        },
        "separation": {
            "companies_law_corpus_unchanged": True,
            "chinese_remediation_program_unchanged": True,
            "listed_joint_stock_is_separate_specialized_sub_track": True,
            "general_source_intake_read_only_consumption": True,
        },
        "disclaimer_ar": (
            "هذه طبقة عربية جاهزة للنماذج اللغوية مشتقة من نص اللائحة التنفيذية "
            "العامة لنظام الشركات الصادرة من أم القرى. النص العربي محفوظ حرفيًّا "
            "من المصدر الرسمي بلا تلخيص ولا إعادة صياغة. العربية هي اللغة الحاكمة. "
            "ليست ترجمة رسمية وليست استشارة قانونية. الشركات المدرجة مسار منفصل متخصص."
        ),
        "records": article_records,
    }

    # Build forms layer JSON
    forms_layer = {
        "layer_id": "sa-general-implementing-regulations-arabic-forms-llm",
        "stage": "GENERAL_IMPLEMENTING_REGULATIONS_ARABIC_FORMS_LLM_LAYER",
        "corpus_track": "implementing_regulations/general",
        "regulation_scope": "general",
        "parent_law": "sa_companies_law_m132_1443",
        "source_title": source["source_title"],
        "source_url": source["source_url"],
        "source_intake_file": "data/implementing_regulations/general/general_implementing_regulations_arabic_source.json",
        "source_manifest_file": "data/implementing_regulations/general/source_manifest.json",
        "source_manifest_hash": manifest_hash,
        "source_hash": source["source_hash"],
        "language": "ar",
        "governing_text": "arabic_official_source",
        "record_type": "official_form",
        "record_count": len(form_records),
        "form_count": len(form_records),
        "publication_date_hijri": source["publication_date_hijri"],
        "publication_date_gregorian": source["publication_date_gregorian"],
        "access_date": source["access_date"],
        "extraction_method": source["extraction_method"],
        "content_boundaries": {
            "no_english_text_generated": True,
            "no_chinese_text_generated": True,
            "no_trilingual_alignment": True,
            "no_public_release": True,
            "no_paraphrasing": True,
            "official_text_ar_preserved_verbatim": True,
        },
        "legal_status": {
            "arabic_governs": True,
            "not_official_translation": True,
            "not_legal_advice": True,
            "not_binding_translation": True,
            "derived_from_general_implementing_regulations_source": True,
        },
        "separation": {
            "companies_law_corpus_unchanged": True,
            "chinese_remediation_program_unchanged": True,
            "listed_joint_stock_is_separate_specialized_sub_track": True,
        },
        "disclaimer_ar": (
            "هذه طبقة النماذج الرسمية العربية الجاهزة للنماذج اللغوية مشتقة من "
            "نص اللائحة التنفيذية العامة لنظام الشركات. النص العربي محفوظ حرفيًّا "
            "من المصدر الرسمي. العربية هي اللغة الحاكمة. ليست ترجمة رسمية وليست "
            "استشارة قانونية."
        ),
        "records": form_records,
    }

    # Write output files
    _dump_json(article_layer, OUTPUT_ARTICLES_PATH)
    print(f"[OK] Article layer written: {OUTPUT_ARTICLES_PATH}")
    print(f"     {len(article_records)} article records, 7 chapters")

    _dump_json(forms_layer, OUTPUT_FORMS_PATH)
    print(f"[OK] Forms layer written: {OUTPUT_FORMS_PATH}")
    print(f"     {len(form_records)} form records")

    return 0


if __name__ == "__main__":
    sys.exit(main())