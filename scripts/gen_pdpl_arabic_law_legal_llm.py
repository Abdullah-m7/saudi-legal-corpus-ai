#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the PDPL Law Arabic LLM-ready enrichment layer (43 articles).

Builds an LLM/RAG retrieval layer over the *verified* PDPL law text
(``pdpl_arabic_law_verified_records.jsonl`` — the official SDAIA-published text,
cross-checked against the repo's independent OCR).  Each record carries the
verified article text plus mechanical retrieval metadata: llm_title /
retrieval_title / article_path / keywords / search_queries / a text hash /
source_trust.

The PDPL law articles have ordinal headings only (no descriptive titles), so
keywords are extracted mechanically from the article text by term frequency
(function-word stoplist removed) — an index operation, not a summary.  Nothing
here summarizes, paraphrases, translates, or interprets.  Article 32 is repealed
(``مُلغاة``) and flagged as such.

record_type is ``verified_arabic_article`` and text_status is
``VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT``.  Arabic governs.

Read-only over its input; deterministic and idempotent over its output.
"""

from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFIED = os.path.join(ROOT, "sources", "pdpl", "verified",
                        "pdpl_arabic_law_verified_records.jsonl")
OUT_DIR = os.path.join(ROOT, "data", "pdpl_arabic_legal_llm")
OUT_PATH = os.path.join(OUT_DIR, "pdpl_arabic_law_legal_llm_001_043.json")
SCHEMA_REL = "schemas/pdpl_arabic_law_legal_llm.schema.json"

LAW_ID = "sa-pdpl-law-m19-1443"
LAW_AR = "نظام حماية البيانات الشخصية"
REPEALED = {32}

STOPWORDS = {
    "من", "في", "على", "عن", "إلى", "أو", "و", "أن", "التي", "الذي", "ما",
    "غير", "قبل", "بعد", "عند", "لدى", "هذه", "هذا", "به", "بها", "لها", "له",
    "أي", "كل", "ذلك", "تلك", "ذات", "ذوات", "بأي", "بما", "فيها", "فيه", "مع",
    "أو", "ومن", "وأي", "وفي", "وعلى", "أما", "إذا", "كان", "كانت", "يكون",
    "تكون", "وقد", "قد", "لا", "إلا", "بين", "حسب", "وفق", "وفقاً", "بحسب",
    "المادة", "النظام", "اللائحة", "اللوائح", "هذه", "هذا", "عليها", "عليه",
    "التالية", "الآتية", "يلي", "يأتي", "الأولى", "الثانية", "الثالثة",
}


def _short_heading_topic(article_number):
    return "المادة %d" % article_number


def _keywords(text, k=6):
    freq = {}
    order = []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOPWORDS:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    # sort by frequency desc, then first-appearance order (stable, deterministic)
    ranked = sorted(order, key=lambda w: (-freq[w], order.index(w)))
    return ranked[:k] if ranked else [text.strip()[:20] or LAW_AR]


def _search_queries(num, repealed):
    q = [
        "المادة %d %s" % (num, LAW_AR),
        "%s المادة %d" % (LAW_AR, num),
        "%s نظام البيانات الشخصية" % ("المادة %d" % num),
    ]
    if repealed:
        q.append("المادة %d ملغاة %s" % (num, LAW_AR))
    return q


def build_records():
    rows = [json.loads(l) for l in open(VERIFIED, encoding="utf-8") if l.strip()]
    rows.sort(key=lambda r: r["article_number"])
    records = []
    for r in rows:
        num = r["article_number"]
        text = r["article_text_verified"]
        repealed = num in REPEALED
        title = _short_heading_topic(num)
        llm_title = "%s — المادة %d%s" % (LAW_AR, num, " (ملغاة)" if repealed else "")
        records.append({
            "law_id": LAW_ID,
            "law_component": "law",
            "article_number": num,
            "article_key": r["article_key"],
            "article_title_ar": title,
            "record_id": "pdpl-law-llm-art-%03d" % num,
            "record_type": "verified_arabic_article",
            "language": "ar",
            "governing_text_language": "ar",
            "is_repealed": repealed,
            "article_text_ar": text,
            "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "llm_title_ar": llm_title,
            "retrieval_title_ar": "%s - المادة %d" % (LAW_AR, num),
            "article_path": "pdpl/law/articles/%03d" % num,
            "keywords_ar": _keywords(text),
            "search_queries_ar": _search_queries(num, repealed),
            "text_status": "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT",
            "source_trust": {
                "source_authority": "Saudi Data and AI Authority (SDAIA)",
                "source_authority_ar": "الهيئة السعودية للبيانات والذكاء الاصطناعي",
                "source_status": "verified_against_official_sdaia_published_text",
                "source_document_ar": LAW_AR,
                "royal_decree": "م/19، المعدل بـ م/148",
                "source_url": r["verification_source_url"],
                "ocr_corroboration_similarity": r["corroboration"]["ocr_token_similarity"],
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
        "layer_id": "sa-pdpl-law-arabic-legal-llm-full",
        "law_id": LAW_ID,
        "law_component": "law",
        "title_ar": "نظام حماية البيانات الشخصية — الطبقة العربية الجاهزة للنماذج اللغوية (43 مادة)",
        "title_en": "PDPL Law — Arabic LLM-ready layer (43 articles)",
        "record_type": "verified_arabic_article",
        "language": "ar",
        "governing_text_language": "ar",
        "record_count": len(records),
        "article_range": [1, 43],
        "repealed_articles": sorted(REPEALED),
        "source_verified_file": os.path.relpath(VERIFIED, ROOT),
        "schema": SCHEMA_REL,
        "text_status": "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT",
        "not_legal_advice": True,
        "disclaimer_ar": (
            "طبقة استرجاعية جاهزة للنماذج اللغوية مبنية على النص الرسمي المنشور للنظام "
            "من الهيئة السعودية للبيانات والذكاء الاصطناعي، مُتحقَّق منه مقابل نص OCR "
            "المستقل في المستودع. لا تلخيص ولا إعادة صياغة ولا ترجمة ولا تفسير قانوني. "
            "العربية هي المصدر الحاكم. ليست استشارة قانونية."
        ),
        "records": records,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(layer, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Wrote %d LLM-ready law records -> %s" % (len(records), os.path.relpath(OUT_PATH, ROOT)))
    s = records[0]
    print("Sample art 1 keywords:", json.dumps(s["keywords_ar"], ensure_ascii=False))
    print("Art 32 repealed:", records[31]["is_repealed"], "| title:", records[31]["llm_title_ar"])


if __name__ == "__main__":
    main()
