#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Investment Regulations Arabic LLM-ready enrichment layer (37 articles).

LLM/RAG retrieval layer over the verified Investment Implementing Regulations
text (``investment_regulation_verified_records.jsonl``).  Each record carries the
verified article text plus mechanical retrieval metadata: llm_title /
retrieval_title / article_path / keywords / search_queries / a text hash / a
source-trust block.  record_type is ``verified_arabic_article``; text_status is
``VERIFIED_TRANSCRIBED_FROM_OFFICIAL_MISA_PDF``.  Retrieval metadata is derived
from the article title and number only — no summary, paraphrase, translation, or
interpretation.  Arabic governs.

Read-only over its input; deterministic and idempotent over its output.
"""

from __future__ import annotations

import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFIED = os.path.join(ROOT, "sources", "investment", "regulation", "verified",
                        "investment_regulation_verified_records.jsonl")
OUT_DIR = os.path.join(ROOT, "data", "investment_arabic_legal_llm")
OUT_PATH = os.path.join(OUT_DIR, "investment_regulation_legal_llm_001_037.json")
SCHEMA_REL = "schemas/investment_regulation_legal_llm.schema.json"

LAW_ID = "sa-investment-law-1446"
REG_AR = "اللائحة التنفيذية لنظام الاستثمار"

STOPWORDS = {
    "من", "في", "على", "عن", "إلى", "أو", "و", "أن", "التي", "الذي", "ما",
    "غير", "قبل", "بعد", "عند", "لدى", "هذه", "هذا", "به", "بها", "لها", "له",
    "المادة", "النظام", "اللائحة", "بين",
}


def _keywords(title_ar):
    kws = []
    for w in title_ar.replace("،", " ").split():
        w = w.strip("().,:؛،")
        if len(w) >= 3 and w not in STOPWORDS and w not in kws:
            kws.append(w)
    return kws or [title_ar.strip()]


def _search_queries(num, title_ar):
    return [
        "المادة %d %s" % (num, REG_AR),
        "%s المادة %d" % (REG_AR, num),
        "%s %s" % (title_ar, REG_AR),
        title_ar,
    ]


def build_records():
    rows = [json.loads(l) for l in open(VERIFIED, encoding="utf-8") if l.strip()]
    rows.sort(key=lambda r: r["article_number"])
    records = []
    for r in rows:
        num = r["article_number"]
        title = r["arabic_title"]
        text = r["article_text_verified"]
        records.append({
            "law_id": LAW_ID,
            "law_component": "implementing_regulation",
            "article_number": num,
            "article_key": r["article_key"],
            "article_title_ar": title,
            "record_id": "inv-reg-llm-art-%03d" % num,
            "record_type": "verified_arabic_article",
            "language": "ar",
            "governing_text_language": "ar",
            "article_text_ar": text,
            "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "llm_title_ar": "المادة %d: %s" % (num, title),
            "retrieval_title_ar": "%s - المادة %d - %s" % (REG_AR, num, title),
            "article_path": "investment/regulation/articles/%03d" % num,
            "keywords_ar": _keywords(title),
            "search_queries_ar": _search_queries(num, title),
            "text_status": "VERIFIED_TRANSCRIBED_FROM_OFFICIAL_MISA_PDF",
            "source_trust": {
                "source_authority": "Ministry of Investment (MISA)",
                "source_authority_ar": "وزارة الاستثمار",
                "source_status": "verified_transcribed_from_official_misa_pdf",
                "source_document_ar": REG_AR,
                "source_pdf_sha256": r["source_pdf_sha256"],
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
        "layer_id": "sa-investment-regulation-arabic-legal-llm-full",
        "law_id": LAW_ID,
        "law_component": "implementing_regulation",
        "title_ar": "اللائحة التنفيذية لنظام الاستثمار — الطبقة العربية الجاهزة للنماذج اللغوية (37 مادة)",
        "title_en": "Investment Law Implementing Regulations — Arabic LLM-ready layer (37 articles)",
        "record_type": "verified_arabic_article",
        "language": "ar",
        "governing_text_language": "ar",
        "record_count": len(records),
        "article_range": [1, 37],
        "source_verified_file": os.path.relpath(VERIFIED, ROOT),
        "schema": SCHEMA_REL,
        "text_status": "VERIFIED_TRANSCRIBED_FROM_OFFICIAL_MISA_PDF",
        "not_legal_advice": True,
        "disclaimer_ar": (
            "طبقة استرجاعية جاهزة للنماذج اللغوية مبنية على نص اللائحة التنفيذية لنظام "
            "الاستثمار الرسمي من وزارة الاستثمار. لا تلخيص ولا إعادة صياغة ولا ترجمة ولا "
            "تفسير قانوني. العربية هي المصدر الحاكم. ليست استشارة قانونية."
        ),
        "records": records,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(layer, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Wrote %d LLM-ready investment-regulation records -> %s"
          % (len(records), os.path.relpath(OUT_PATH, ROOT)))


if __name__ == "__main__":
    main()
