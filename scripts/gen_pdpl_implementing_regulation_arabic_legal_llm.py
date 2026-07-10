#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the PDPL Implementing Regulation Arabic LLM-ready enrichment layer.

Builds an LLM / RAG retrieval layer over the *verified* Arabic text produced by
``gen_pdpl_implementing_regulation_arabic_verified.py`` (38 articles) — the
official SDAIA-published regulation text, cross-checked against the repository's
independent cleaned extraction.  Each record carries the verified article text
plus mechanical retrieval metadata: llm_title / retrieval_title / article_path /
keywords / search_queries / a text hash / a source-trust block.

record_type is ``verified_arabic_article`` and text_status is
``VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT``.  Retrieval metadata is derived
deterministically from the article title and number only — no summary,
paraphrase, translation, or legal interpretation.  Arabic governs.

Read-only over its input; deterministic and idempotent over its output.
"""

from __future__ import annotations

import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFIED = os.path.join(
    ROOT, "sources", "pdpl", "regulation", "verified",
    "pdpl_implementing_regulation_arabic_verified_records.jsonl",
)
OUT_DIR = os.path.join(ROOT, "data", "pdpl_arabic_legal_llm")
OUT_PATH = os.path.join(
    OUT_DIR, "pdpl_implementing_regulation_arabic_legal_llm_001_038.json")
SCHEMA_REL = "schemas/pdpl_implementing_regulation_arabic_legal_llm.schema.json"

LAW_ID = "sa-pdpl-implementing-regulation"
REGULATION_AR = "اللائحة التنفيذية لنظام حماية البيانات الشخصية"

# Arabic function words dropped from title-derived keywords (retrieval only).
STOPWORDS = {
    "من", "في", "على", "عن", "إلى", "أو", "و", "أن", "التي", "الذي", "ما",
    "غير", "قبل", "بعد", "عند", "لدى", "هذه", "هذا", "به", "بها", "لها", "له",
    "المادة", "الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة", "السادسة",
    "السابعة", "الثامنة", "التاسعة", "العاشرة", "عشرة", "الحادية", "عشر",
    "العشرون", "والعشرون", "الثلاثون", "والثلاثون",
}


def _short_title(arabic_heading):
    if ":" in arabic_heading:
        return arabic_heading.split(":", 1)[1].strip()
    if "：" in arabic_heading:
        return arabic_heading.split("：", 1)[1].strip()
    return arabic_heading.strip()


def _keywords(short_title):
    kws = []
    for w in short_title.replace("،", " ").split():
        w = w.strip("().,:؛،")
        if len(w) >= 3 and w not in STOPWORDS and w not in kws:
            kws.append(w)
    return kws


def _search_queries(num, short_title):
    return [
        "المادة %d %s" % (num, REGULATION_AR),
        "%s المادة %d" % (REGULATION_AR, num),
        "%s %s" % (short_title, REGULATION_AR),
        short_title,
    ]


def build_records():
    rows = [json.loads(l) for l in open(VERIFIED, encoding="utf-8") if l.strip()]
    rows.sort(key=lambda r: r["article_number"])
    records = []
    for r in rows:
        num = r["article_number"]
        short_title = _short_title(r["arabic_heading"])
        text = r["article_text_verified"]
        records.append({
            "law_id": LAW_ID,
            "law_component": "implementing_regulation",
            "article_number": num,
            "article_key": r["article_key"],
            "article_title_ar": short_title,
            "record_id": "pdpl-reg-llm-art-%03d" % num,
            "record_type": "verified_arabic_article",
            "language": "ar",
            "governing_text_language": "ar",
            "article_text_ar": text,
            "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "llm_title_ar": "المادة %d: %s" % (num, short_title),
            "retrieval_title_ar": "%s - المادة %d - %s" % (REGULATION_AR, num, short_title),
            "article_path": "pdpl/implementing_regulation/articles/%03d" % num,
            "keywords_ar": _keywords(short_title),
            "search_queries_ar": _search_queries(num, short_title),
            "text_status": "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT",
            "source_trust": {
                "source_authority": "Saudi Data and AI Authority (SDAIA)",
                "source_authority_ar": "الهيئة السعودية للبيانات والذكاء الاصطناعي",
                "source_status": "verified_against_official_sdaia_published_text",
                "source_document_ar": REGULATION_AR,
                "source_url": r["verification_source_url"],
                "cleaned_corroboration_similarity": r["corroboration"]["cleaned_token_similarity"],
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
        "record_type": "verified_arabic_article",
        "language": "ar",
        "governing_text_language": "ar",
        "record_count": len(records),
        "article_range": [records[0]["article_number"], records[-1]["article_number"]],
        "source_verified_file": os.path.relpath(VERIFIED, ROOT),
        "schema": SCHEMA_REL,
        "text_status": "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT",
        "not_legal_advice": True,
        "disclaimer_ar": (
            "طبقة استرجاعية جاهزة للنماذج اللغوية مبنية على النص الرسمي المنشور للائحة "
            "من الهيئة السعودية للبيانات والذكاء الاصطناعي، مُتحقَّق منه مقابل النص المُنظَّف "
            "المستقل في المستودع. لا تلخيص ولا إعادة صياغة ولا ترجمة ولا تفسير قانوني. "
            "العربية هي المصدر الحاكم. ليست استشارة قانونية."
        ),
        "records": records,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(layer, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Wrote %d LLM-ready records -> %s" % (len(records), os.path.relpath(OUT_PATH, ROOT)))


if __name__ == "__main__":
    main()
