#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Real Estate Brokerage Law track (نظام الوساطة العقارية م/130).

Source: REGA's own hosted copy (rega.gov.sa/media/f4xblyha/...) of the official
Bureau-of-Experts-sealed instrument (Royal Decree M/130, 30/11/1443H) — a
12-page scanned PDF with no text layer. Every page was rendered at 300dpi and
read directly (visual transcription, verbatim) since the live laws.boe.gov.sa
portal (lawId f1bfd1f1-0c50-468e-b9a5-aeee008e493a) returned persistent HTTP
503 across repeated attempts. A tesseract-ara OCR pass of the same renders was
run as a corroborating digital channel, and two independent secondary
full-text sources (qanoonsa.com, nezams.com) were fetched directly (raw HTML)
and cross-verified word-for-word (differing only in diacritics/digit script).
All 24 articles اصلية (FRESH FULL ISSUANCE; 0 معدلة / 0 ملغاة / 0 مضافة).
Article 22 is a genuine named repeal of the 1398H Real Estate Offices
Regulation (Council of Ministers Resolution No. 334, 7/3/1398H) — that older
instrument is not itself tracked in this corpus, so no supersession edge is
required. Article 24: in force 180 days after publication in Umm al-Qura
Gazette (4940), 22 July 2022 — settled current law, not pending.

Articles are numbered by their ordinal position in the official statute
structure (1..24; no مكرر). number_label_ar preserves each article's official
label verbatim. No legal text is altered. Arabic governs; no translation/
paraphrase/interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "real_estate_brokerage", "law", "official_source",
                   "real_estate_brokerage_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "real_estate_brokerage", "law", "verified")
RECORDS = os.path.join(OUT_VER, "real_estate_brokerage_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "real_estate_brokerage_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "real_estate_brokerage_arabic_legal_llm",
                        "real_estate_brokerage_law_legal_llm_001_024.json")

LAW_ID = "sa-real-estate-brokerage-law-m130-1443"
LAW_AR = "نظام الوساطة العقارية"
STATUS = "MATCHES_OFFICIAL_SCAN_VISUALLY_VERIFIED"
KEY_RE = r"real_estate_brokerage_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    return int(re.match(KEY_RE, key).group(1))


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        n = int(re.match(KEY_RE, key).group(1))
        ls = a.get("legal_status_ar")
        text = a["text"]
        ver.append({"law_key": "real_estate_brokerage", "law_component": "law", "language": "ar",
                    "record_layer": "REAL_ESTATE_BROKERAGE_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "secondary_cross_check": a.get("secondary_cross_check"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; text visually transcribed verbatim from "
                                              "REGA's hosted copy of the official Bureau-of-Experts-sealed "
                                              "scanned PDF (no text layer), corroborated by an independent "
                                              "tesseract-ara OCR pass of the same document and cross-"
                                              "verified word-for-word against two independent secondary "
                                              "full-text sources (qanoonsa.com, nezams.com)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "real-estate-brokerage-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "real_estate_brokerage/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام الوساطة العقارية" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "General Real Estate Authority (REGA) — hosted copy of the Bureau of Experts (BOE) official instrument",
                                     "source_authority_ar": "الهيئة العامة للعقار — نسخة رسمية من مستند هيئة الخبراء بمجلس الوزراء",
                                     "source_status": "rega_hosted_boe_sealed_pdf_visually_verified",
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "real_estate_brokerage", "layer": "REAL_ESTATE_BROKERAGE_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "visually_adjudicated": src["stats"]["visually_adjudicated"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-real-estate-brokerage-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (24 مادة؛ إصدار جديد كامل: 24 أصلية)",
               "title_en": "Saudi Real Estate Brokerage Law — Arabic LLM-ready layer (24 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 24], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Real Estate Brokerage Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
