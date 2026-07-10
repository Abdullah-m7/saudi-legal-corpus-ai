#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Civil Transactions Law Arabic LLM-ready enrichment layer (721 articles).

LLM/RAG retrieval layer over the verified Civil Transactions Law text.  The law's
articles carry ordinal headings only (no descriptive titles), so keywords are
extracted mechanically from each article's text by term frequency (function-word
stoplist removed) — an index operation, not a summary.  The structural section
context (كتاب/باب/فصل) captured at parse time is carried as a retrieval signal.
No summary, paraphrase, translation, or interpretation.  Arabic governs.

Read-only over its input; deterministic and idempotent over its output.
"""

from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFIED = os.path.join(ROOT, "sources", "civil", "law", "verified",
                        "civil_transactions_law_verified_records.jsonl")
OUT_DIR = os.path.join(ROOT, "data", "civil_arabic_legal_llm")
OUT_PATH = os.path.join(OUT_DIR, "civil_transactions_law_legal_llm_001_721.json")
SCHEMA_REL = "schemas/civil_transactions_law_legal_llm.schema.json"

LAW_ID = "sa-civil-transactions-law-m191-1444"
LAW_AR = "نظام المعاملات المدنية"

STOPWORDS = {
    "من", "في", "على", "عن", "إلى", "أو", "و", "أن", "التي", "الذي", "ما",
    "غير", "قبل", "بعد", "عند", "لدى", "هذه", "هذا", "به", "بها", "لها", "له",
    "أي", "كل", "ذلك", "تلك", "ذات", "ذوات", "بأي", "بما", "فيها", "فيه", "مع",
    "ومن", "وأي", "وفي", "وعلى", "أما", "إذا", "كان", "كانت", "يكون", "تكون",
    "وقد", "قد", "لا", "إلا", "بين", "حسب", "وفق", "وفقا", "بحسب", "فإن", "وإن",
    "المادة", "النظام", "أحكام", "حكم", "وجب", "يجب", "جاز", "يجوز", "عليه",
    "ولو", "دون", "فيما", "منه", "منها", "وإذا", "حال", "وله", "ولها",
}


def _keywords(text, k=6):
    freq = {}
    order = []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOPWORDS:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    ranked = sorted(order, key=lambda w: (-freq[w], order.index(w)))
    return ranked[:k] if ranked else [LAW_AR]


def _search_queries(num):
    return [
        "المادة %d %s" % (num, LAW_AR),
        "%s المادة %d" % (LAW_AR, num),
        "المادة %d القانون المدني السعودي" % num,
    ]


def build_records():
    rows = [json.loads(l) for l in open(VERIFIED, encoding="utf-8") if l.strip()]
    rows.sort(key=lambda r: r["article_number"])
    records = []
    for r in rows:
        num = r["article_number"]
        text = r["article_text_verified"]
        records.append({
            "law_id": LAW_ID,
            "law_component": "law",
            "article_number": num,
            "article_key": r["article_key"],
            "article_title_ar": "المادة %d" % num,
            "record_id": "civil-law-llm-art-%03d" % num,
            "record_type": "official_arabic_article",
            "language": "ar",
            "governing_text_language": "ar",
            "section_context_ar": r.get("section_context_ar", ""),
            "article_text_ar": text,
            "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "llm_title_ar": "%s — المادة %d" % (LAW_AR, num),
            "retrieval_title_ar": "%s - المادة %d" % (LAW_AR, num),
            "article_path": "civil/law/articles/%03d" % num,
            "keywords_ar": _keywords(text),
            "search_queries_ar": _search_queries(num),
            "text_status": "OWNER_PROVIDED_OFFICIAL_TEXT",
            "source_trust": {
                "source_authority": "Bureau of Experts at the Council of Ministers",
                "source_authority_ar": "هيئة الخبراء بمجلس الوزراء",
                "source_status": "owner_provided_official_text",
                "source_document_ar": LAW_AR,
                "royal_decree": r["royal_decree"],
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
        "layer_id": "sa-civil-transactions-law-arabic-legal-llm-full",
        "law_id": LAW_ID,
        "law_component": "law",
        "title_ar": "نظام المعاملات المدنية — الطبقة العربية الجاهزة للنماذج اللغوية (721 مادة)",
        "title_en": "Civil Transactions Law — Arabic LLM-ready layer (721 articles)",
        "record_type": "official_arabic_article",
        "language": "ar",
        "governing_text_language": "ar",
        "record_count": len(records),
        "article_range": [1, 721],
        "source_verified_file": os.path.relpath(VERIFIED, ROOT),
        "schema": SCHEMA_REL,
        "text_status": "OWNER_PROVIDED_OFFICIAL_TEXT",
        "not_legal_advice": True,
        "disclaimer_ar": (
            "طبقة استرجاعية جاهزة للنماذج اللغوية مبنية على النص الرسمي الكامل لنظام "
            "المعاملات المدنية المقدَّم من المالك من المصدر الرسمي. لا تلخيص ولا إعادة "
            "صياغة ولا ترجمة ولا تفسير قانوني. العربية هي المصدر الحاكم. ليست استشارة قانونية."
        ),
        "records": records,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(layer, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("Wrote %d LLM-ready civil-law records -> %s"
          % (len(records), os.path.relpath(OUT_PATH, ROOT)))


if __name__ == "__main__":
    main()
