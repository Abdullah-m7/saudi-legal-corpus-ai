#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the PDPL Implementing Regulation Arabic LLM-ready enrichment layer.

Builds an LLM / RAG retrieval layer over the *cleaned* Arabic text produced by
``gen_pdpl_implementing_regulation_arabic_cleaned.py`` (38 articles).  Each
record carries the cleaned article text plus mechanical retrieval metadata —
llm_title / retrieval_title / article_path / keywords / search_queries / a text
hash / a source-trust block — mirroring the Companies Law
``official_arabic_legal_llm`` layer field-for-field in spirit.

Honesty boundaries (this is the key difference from the Companies Law layer):
the underlying text is a de-noised PDF extraction, NOT a certified official
transcription.  So the record_type is ``cleaned_extracted_arabic_article`` (not
``official_arabic_article``) and ``text_status`` stays
``EXTRACTED_TEXT_NOT_VERIFIED_OFFICIAL_TEXT``.  Nothing here summarizes,
paraphrases, translates, or legally interprets the text; retrieval metadata is
derived deterministically from the article title and number only.

Arabic is the governing source.  Read-only over its input; deterministic and
idempotent over its output.
"""

from __future__ import annotations

import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANED = os.path.join(
    ROOT, "sources", "pdpl", "regulation", "cleaned",
    "pdpl_implementing_regulation_arabic_cleaned_records.jsonl",
)
OUT_DIR = os.path.join(ROOT, "data", "pdpl_arabic_legal_llm")
OUT_PATH = os.path.join(
    OUT_DIR, "pdpl_implementing_regulation_arabic_legal_llm_001_038.json")
SCHEMA_REL = "schemas/pdpl_implementing_regulation_arabic_legal_llm.schema.json"

LAW_ID = "sa-pdpl-implementing-regulation"
SOURCE_PDF_SHA256 = "4b4b24e3bcb744a04a39a65d890454fc63ea282be85501af125d5f36134919df"
REGULATION_AR = "اللائحة التنفيذية لنظام حماية البيانات الشخصية"

# Arabic function words dropped from title-derived keywords (retrieval only).
STOPWORDS = {
    "من", "في", "على", "عن", "إلى", "أو", "و", "أن", "التي", "الذي", "ما",
    "غير", "قبل", "بعد", "عند", "لدى", "هذه", "هذا", "به", "بها", "لها", "له",
    "المادة", "الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة", "السادسة",
    "السابعة", "الثامنة", "التاسعة", "العاشرة", "عشرة", "الحادية", "عشر",
    "العشرون", "والعشرون", "الثلاثون", "والثلاثون",
}


def _short_title(arabic_heading: str) -> str:
    """Title text after the 'المادة N:' prefix."""
    if ":" in arabic_heading:
        return arabic_heading.split(":", 1)[1].strip()
    if "：" in arabic_heading:
        return arabic_heading.split("：", 1)[1].strip()
    return arabic_heading.strip()


def _keywords(short_title: str):
    kws = []
    for w in short_title.replace("،", " ").split():
        w = w.strip("().,:؛،")
        if len(w) >= 3 and w not in STOPWORDS and w not in kws:
            kws.append(w)
    return kws


def _search_queries(num: int, short_title: str):
    return [
        "المادة %d %s" % (num, REGULATION_AR),
        "%s المادة %d" % (REGULATION_AR, num),
        "%s %s" % (short_title, REGULATION_AR),
        short_title,
    ]


def build_records():
    rows = [json.loads(l) for l in open(CLEANED, encoding="utf-8") if l.strip()]
    rows.sort(key=lambda r: r["article_number"])
    records = []
    for r in rows:
        num = r["article_number"]
        short_title = _short_title(r["arabic_heading"])
        text = r["article_text_cleaned"]
        records.append({
            "law_id": LAW_ID,
            "law_component": "implementing_regulation",
            "article_number": num,
            "article_key": r["article_key"],
            "article_title_ar": short_title,
            "record_id": "pdpl-reg-llm-art-%03d" % num,
            "record_type": "cleaned_extracted_arabic_article",
            "language": "ar",
            "governing_text_language": "ar",
            "article_text_ar": text,
            "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "llm_title_ar": "المادة %d: %s" % (num, short_title),
            "retrieval_title_ar": "%s - المادة %d - %s" % (REGULATION_AR, num, short_title),
            "article_path": "pdpl/implementing_regulation/articles/%03d" % num,
            "keywords_ar": _keywords(short_title),
            "search_queries_ar": _search_queries(num, short_title),
            "text_status": "EXTRACTED_TEXT_NOT_VERIFIED_OFFICIAL_TEXT",
            "source_trust": {
                "source_authority": "Saudi Data and AI Authority (SDAIA)",
                "source_authority_ar": "الهيئة السعودية للبيانات والذكاء الاصطناعي",
                "source_status": "extracted_from_pdf_not_verified_official",
                "source_document_ar": REGULATION_AR,
                "source_pdf_sha256": SOURCE_PDF_SHA256,
                "source_cleaned_file": os.path.relpath(CLEANED, ROOT),
                "spot_verified_articles": [3],
                "spot_verify_source": (
                    "https://dgp.sdaia.gov.sa/wps/portal/pdp/knowledgecenter/details/PDPL2"),
            },
            "translation_performed": False,
            "legal_interpretation_performed": False,
            "english_used_for_correction": False,
            "text_summarized_or_paraphrased": False,
        })
    return records


def main():
    records = build_records()
    os.makedirs(OUT_DIR, exist_ok=True)
    layer = {
        "layer_id": "sa-pdpl-implementing-regulation-arabic-legal-llm-full",
        "law_id": LAW_ID,
        "law_component": "implementing_regulation",
        "title_ar": "اللائحة التنفيذية لنظام حماية البيانات الشخصية — الطبقة العربية الجاهزة للنماذج اللغوية (38 مادة)",
        "title_en": "PDPL Implementing Regulation — Arabic LLM-ready layer (38 articles)",
        "record_type": "cleaned_extracted_arabic_article",
        "language": "ar",
        "governing_text_language": "ar",
        "record_count": len(records),
        "article_range": [records[0]["article_number"], records[-1]["article_number"]],
        "source_cleaned_file": os.path.relpath(CLEANED, ROOT),
        "source_pdf_sha256": SOURCE_PDF_SHA256,
        "schema": SCHEMA_REL,
        "text_status": "EXTRACTED_TEXT_NOT_VERIFIED_OFFICIAL_TEXT",
        "not_legal_advice": True,
        "disclaimer_ar": (
            "هذه طبقة استرجاعية جاهزة للنماذج اللغوية مبنية على نص عربي مُنظَّف "
            "مُستخرَج من ملف PDF للائحة التنفيذية، وليست نسخة رسمية مُتحقَّقًا منها "
            "سطرًا بسطر. لا تلخيص ولا إعادة صياغة ولا ترجمة ولا تفسير قانوني. "
            "العربية هي المصدر الحاكم. ليست استشارة قانونية."
        ),
        "records": records,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(layer, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Wrote %d LLM-ready records -> %s" % (len(records), os.path.relpath(OUT_PATH, ROOT)))
    print("Sample:")
    s = records[2]
    for k in ("llm_title_ar", "retrieval_title_ar", "article_path", "keywords_ar", "search_queries_ar"):
        print("  %-20s %s" % (k, json.dumps(s[k], ensure_ascii=False)))


if __name__ == "__main__":
    main()
