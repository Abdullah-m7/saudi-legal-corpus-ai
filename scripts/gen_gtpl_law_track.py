#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the GTPL (نظام المنافسات والمشتريات الحكومية م/128) track outputs.

From the committed source artifacts (Arabic governing text, cross-checked
against the official Ministry of Finance PDF; official BOE English translation
as reference-only), emits:
  * verified Arabic records (99) -> sources/gtpl/law/verified/
  * the Arabic LLM-ready enrichment layer -> data/gtpl_arabic_legal_llm/

Arabic governs; English is reference only and is never used to alter the
Arabic. No translation, summary, paraphrase, or interpretation.
Read-only over inputs; deterministic and idempotent over outputs.
"""

from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "gtpl", "law", "official_source",
                   "gtpl_m128_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "gtpl", "law", "verified")
RECORDS = os.path.join(OUT_VER, "gtpl_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "gtpl_law_verified_summary.json")
OUT_LLM = os.path.join(ROOT, "data", "gtpl_arabic_legal_llm")
LLM_PATH = os.path.join(OUT_LLM, "gtpl_law_legal_llm_001_099.json")

LAW_ID = "sa-gtpl-m128-1440"
LAW_AR = "نظام المنافسات والمشتريات الحكومية"
STATUS = "MIRROR_TEXT_CROSS_CHECKED_AGAINST_OFFICIAL_MOF_PDF"

STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(OUT_LLM, exist_ok=True)

    ver, llm = [], []
    for n in range(1, 100):
        text = arts[str(n)]
        ver.append({
            "law_key": "gtpl", "law_component": "law", "language": "ar",
            "record_layer": "GTPL_LAW_ARABIC_VERIFIED_TEXT",
            "article_number": n, "article_key": "gtpl_law_art_%03d" % n,
            "article_text_verified": text,
            "official_text_status": STATUS,
            "royal_decree": src["royal_decree"],
            "governing_source_note": ("Arabic is the governing source; text cross-checked against "
                                      "the official MOF consolidated PDF. English (BOE official "
                                      "translation) is reference only."),
            "translation_performed": False, "legal_interpretation_performed": False,
            "summarized_or_paraphrased": False, "english_used_for_correction": False,
        })
        llm.append({
            "law_id": LAW_ID, "law_component": "law", "article_number": n,
            "article_key": "gtpl_law_art_%03d" % n, "article_title_ar": "المادة %d" % n,
            "record_id": "gtpl-law-llm-art-%03d" % n, "record_type": "verified_arabic_article",
            "language": "ar", "governing_text_language": "ar",
            "article_text_ar": text,
            "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "llm_title_ar": "%s — المادة %d" % (LAW_AR, n),
            "retrieval_title_ar": "%s - المادة %d" % (LAW_AR, n),
            "article_path": "gtpl/law/articles/%03d" % n,
            "keywords_ar": _kw(text),
            "search_queries_ar": ["المادة %d %s" % (n, LAW_AR), "%s المادة %d" % (LAW_AR, n),
                                  "المادة %d نظام المشتريات الحكومية" % n],
            "text_status": STATUS,
            "source_trust": {"source_authority": "Ministry of Finance (official PDF cross-check)",
                             "source_authority_ar": "وزارة المالية",
                             "source_status": "mirror_text_cross_checked_against_official_mof_pdf",
                             "source_document_ar": LAW_AR, "royal_decree": src["royal_decree"]},
            "translation_performed": False, "legal_interpretation_performed": False,
            "english_used_for_correction": False, "text_summarized_or_paraphrased": False,
        })

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "gtpl", "layer": "GTPL_LAW_ARABIC_VERIFIED_TEXT", "record_count": 99,
               "official_text_status": STATUS, "source_artifact": os.path.relpath(SRC, ROOT),
               "boundaries": src["boundaries"]},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-gtpl-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law", "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (99 مادة)",
               "title_en": "Government Tenders and Procurement Law — Arabic LLM-ready layer (99 articles)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": 99, "article_range": [1, 99],
               "text_status": STATUS, "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote 99 verified + 99 LLM-ready GTPL records")


if __name__ == "__main__":
    main()
