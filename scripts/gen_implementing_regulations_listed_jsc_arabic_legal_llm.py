#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Listed Joint-Stock Implementing Regulation — Arabic Legal LLM-ready Layer Generator

Creates a structured Arabic Legal LLM-ready JSON layer for the 69 listed
joint-stock implementing-regulation articles and the appendix of the
Saudi Companies Law (M/132, 1443H).

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
  data/implementing_regulations/listed_joint_stock/listed_joint_stock_implementing_regulation_arabic_source.json
  data/implementing_regulations/listed_joint_stock/source_manifest.json

Output:
  data/implementing_regulations/listed_joint_stock/listed_joint_stock_implementing_regulation_arabic_legal_llm.json
  data/implementing_regulations/listed_joint_stock/listed_joint_stock_implementing_regulation_arabic_appendix_llm.json

Idempotent: re-running produces identical output (deterministic JSON with
sorted keys and fixed separators).

Usage:
    python3 scripts/gen_implementing_regulations_listed_jsc_arabic_legal_llm.py
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
OUTPUT_ARTICLES_PATH = os.path.join(
    ROOT,
    "data",
    "implementing_regulations",
    "listed_joint_stock",
    "listed_joint_stock_implementing_regulation_arabic_legal_llm.json",
)
OUTPUT_APPENDIX_PATH = os.path.join(
    ROOT,
    "data",
    "implementing_regulations",
    "listed_joint_stock",
    "listed_joint_stock_implementing_regulation_arabic_appendix_llm.json",
)


def _load_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _dump_json(obj: Any, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _clean_title(title: str) -> str:
    """Strip trailing colons and decorative punctuation from a title for metadata."""
    title = title.rstrip(":：").strip()
    return title


def _build_article_record(
    article: dict[str, Any],
    source: dict[str, Any],
    manifest_hash: str,
) -> dict[str, Any]:
    """Build a single LLM-ready article record."""
    article_number = article["article_number"]
    official_text = article["official_text_ar"]
    text_hash = article["text_hash_sha256"]

    # article_title: use the source's article_title field if present
    # The source intake already has an explicit article_title for each article
    raw_title = article.get("article_title")
    if raw_title:
        article_title_ar = _clean_title(raw_title)
        if not article_title_ar:
            article_title_ar = None
    else:
        article_title_ar = None

    # chapter info: the source intake does not map articles to chapters
    # The chapters list is ordinal-only (no descriptive titles)
    # Set chapter_number and chapter_title_ar to null (faithful to source)
    chapter_number = None
    chapter_title_ar = None

    record_id = f"ir-ljs-art-{article_number:03d}"

    prov = source.get("provenance", {})

    record = {
        "record_id": record_id,
        "corpus_track": "implementing_regulations/listed_joint_stock",
        "regulation_scope": "listed_joint_stock",
        "language": "ar",
        "governing_text": "arabic_official_source",
        "source_url": prov.get("source_url", ""),
        "source_title": prov.get("source_title", ""),
        "publication_date_hijri": prov.get("publication_date_hijri", ""),
        "publication_date_gregorian": prov.get("publication_date_gregorian", ""),
        "issuing_authority": prov.get("issuing_authority", ""),
        "legal_basis": prov.get("legal_basis", ""),
        "chapter_number": chapter_number,
        "chapter_title_ar": chapter_title_ar,
        "article_number": article_number,
        "article_ordinal_ar": article["article_label"],
        "article_title_ar": article_title_ar,
        "official_text_ar": official_text,
        "official_text_hash": text_hash,
        "legal_status_boundaries": {
            "arabic_governs": True,
            "not_official_translation": True,
            "not_legal_advice": True,
            "not_binding_translation": True,
            "derived_from_listed_joint_stock_source": True,
            "general_implementing_regulations_are_separate_track": True,
        },
        "source_manifest_hash": manifest_hash,
    }
    return record


def _build_appendix_record(
    source: dict[str, Any],
    manifest_hash: str,
) -> dict[str, Any]:
    """Build a single LLM-ready appendix record."""
    appendix_text = source.get("appendix_text", "")
    appendix_title = source.get("appendix_title", "")
    appendix_hash = _sha256(appendix_text)

    prov = source.get("provenance", {})

    record = {
        "record_id": "ir-ljs-appendix-001",
        "corpus_track": "implementing_regulations/listed_joint_stock",
        "regulation_scope": "listed_joint_stock",
        "record_type": "official_appendix",
        "language": "ar",
        "governing_text": "arabic_official_source",
        "source_url": prov.get("source_url", ""),
        "source_title": prov.get("source_title", ""),
        "publication_date_hijri": prov.get("publication_date_hijri", ""),
        "publication_date_gregorian": prov.get("publication_date_gregorian", ""),
        "issuing_authority": prov.get("issuing_authority", ""),
        "legal_basis": prov.get("legal_basis", ""),
        "appendix_title": appendix_title,
        "official_text_ar": appendix_text,
        "official_text_hash": appendix_hash,
        "legal_status_boundaries": {
            "arabic_governs": True,
            "not_official_translation": True,
            "not_legal_advice": True,
            "not_binding_translation": True,
            "derived_from_listed_joint_stock_source": True,
            "general_implementing_regulations_are_separate_track": True,
        },
        "source_manifest_hash": manifest_hash,
    }
    return record


def main() -> int:
    if not os.path.isfile(INTAKE_PATH):
        print(f"ERROR: Intake file not found: {INTAKE_PATH}")
        return 1
    if not os.path.isfile(MANIFEST_PATH):
        print(f"ERROR: Manifest file not found: {MANIFEST_PATH}")
        return 1

    source = _load_json(INTAKE_PATH)
    manifest = _load_json(MANIFEST_PATH)

    manifest_json = json.dumps(manifest, sort_keys=True, ensure_ascii=False)
    manifest_hash = _sha256(manifest_json)

    # Build article records
    articles = source.get("articles", [])
    if len(articles) != 69:
        print(f"ERROR: Expected 69 articles, got {len(articles)}")
        return 1

    article_records = []
    for article in articles:
        record = _build_article_record(article, source, manifest_hash)
        article_records.append(record)

    # Build appendix record
    appendix_record = None
    if source.get("has_appendix") and source.get("appendix_text"):
        appendix_record = _build_appendix_record(source, manifest_hash)

    # Build article layer JSON
    prov = source.get("provenance", {})
    article_layer = {
        "layer_id": "sa-listed-jsc-implementing-regulation-arabic-legal-llm",
        "stage": "LISTED_JOINT_STOCK_ARABIC_LEGAL_LLM_LAYER",
        "corpus_track": "implementing_regulations/listed_joint_stock",
        "regulation_scope": "listed_joint_stock",
        "parent_law": "sa_companies_law_m132_1443",
        "source_title": prov.get("source_title", ""),
        "source_url": prov.get("source_url", ""),
        "source_intake_file": "data/implementing_regulations/listed_joint_stock/listed_joint_stock_implementing_regulation_arabic_source.json",
        "source_manifest_file": "data/implementing_regulations/listed_joint_stock/source_manifest.json",
        "source_manifest_hash": manifest_hash,
        "source_hash": prov.get("source_hash_sha256", ""),
        "language": "ar",
        "governing_text": "arabic_official_source",
        "record_type": "implementing_regulation_article",
        "record_count": len(article_records),
        "article_range": [1, 69],
        "chapter_count": len(source.get("chapters", [])),
        "issuing_authority": prov.get("issuing_authority", ""),
        "legal_basis": prov.get("legal_basis", ""),
        "publication_date_hijri": prov.get("publication_date_hijri", ""),
        "publication_date_gregorian": prov.get("publication_date_gregorian", ""),
        "access_date": prov.get("access_date", ""),
        "extraction_method": prov.get("extraction_method", ""),
        "instrument_type": source.get("instrument_type", ""),
        "instrument_type_ar": source.get("instrument_type_ar", ""),
        "specialized_scope": source.get("specialized_scope", ""),
        "is_specialized": True,
        "is_general": False,
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
            "derived_from_listed_joint_stock_source": True,
        },
        "separation": {
            "companies_law_corpus_unchanged": True,
            "chinese_remediation_program_unchanged": True,
            "general_implementing_regulations_are_separate_track": True,
            "listed_joint_stock_source_intake_read_only_consumption": True,
        },
        "disclaimer_ar": (
            "هذه طبقة عربية جاهزة للنماذج اللغوية مشتقة من نص اللائحة التنفيذية "
            "لنظام الشركات الخاصة بشركات المساهمة المدرجة الصادرة عن مجلس هيئة "
            "السوق المالية. النص العربي محفوظ حرفيًّا من المصدر الرسمي بلا تلخيص "
            "ولا إعادة صياغة. العربية هي اللغة الحاكمة. ليست ترجمة رسمية وليست "
            "استشارة قانونية. اللائحة التنفيذية العامة مسار منفصل."
        ),
        "records": article_records,
    }

    # Build appendix layer JSON
    appendix_records = [appendix_record] if appendix_record else []
    appendix_layer = {
        "layer_id": "sa-listed-jsc-implementing-regulation-arabic-appendix-llm",
        "stage": "LISTED_JOINT_STOCK_ARABIC_APPENDIX_LLM_LAYER",
        "corpus_track": "implementing_regulations/listed_joint_stock",
        "regulation_scope": "listed_joint_stock",
        "parent_law": "sa_companies_law_m132_1443",
        "source_title": prov.get("source_title", ""),
        "source_url": prov.get("source_url", ""),
        "source_intake_file": "data/implementing_regulations/listed_joint_stock/listed_joint_stock_implementing_regulation_arabic_source.json",
        "source_manifest_file": "data/implementing_regulations/listed_joint_stock/source_manifest.json",
        "source_manifest_hash": manifest_hash,
        "source_hash": prov.get("source_hash_sha256", ""),
        "language": "ar",
        "governing_text": "arabic_official_source",
        "record_type": "official_appendix",
        "record_count": len(appendix_records),
        "issuing_authority": prov.get("issuing_authority", ""),
        "legal_basis": prov.get("legal_basis", ""),
        "publication_date_hijri": prov.get("publication_date_hijri", ""),
        "publication_date_gregorian": prov.get("publication_date_gregorian", ""),
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
            "derived_from_listed_joint_stock_source": True,
        },
        "separation": {
            "companies_law_corpus_unchanged": True,
            "chinese_remediation_program_unchanged": True,
            "general_implementing_regulations_are_separate_track": True,
        },
        "disclaimer_ar": (
            "هذه طبقة الملحق العربي الجاهزة للنماذج اللغوية مشتقة من نص اللائحة "
            "التنفيذية لنظام الشركات الخاصة بشركات المساهمة المدرجة. النص العربي "
            "محفوظ حرفيًّا من المصدر الرسمي. العربية هي اللغة الحاكمة. ليست ترجمة "
            "رسمية وليست استشارة قانونية."
        ),
        "records": appendix_records,
    }

    _dump_json(article_layer, OUTPUT_ARTICLES_PATH)
    print(f"[OK] Article layer written: {OUTPUT_ARTICLES_PATH}")
    print(f"     {len(article_records)} article records, {len(source.get('chapters', []))} chapters")

    _dump_json(appendix_layer, OUTPUT_APPENDIX_PATH)
    print(f"[OK] Appendix layer written: {OUTPUT_APPENDIX_PATH}")
    print(f"     {len(appendix_records)} appendix records")

    return 0


if __name__ == "__main__":
    sys.exit(main())