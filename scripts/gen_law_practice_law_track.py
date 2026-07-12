#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Code of Law Practice track (نظام المحاماة م/38).

Source: the official MOJ legal-portal consolidated text (Royal Decree M/38,
28/7/1422H), fetched article-by-article (get-Section-Changes) and cross-verified
against the official MOJ PDF (55/56 MATCHES_PDF outright, mean 0.968; art 41
visually adjudicated verbatim on the rendered page). This law is IN FORCE and
substantially consolidated: 35 اصلية / 8 معدلة / 12 مضافة / 1 ملغاة (art 25).
The amendment history spans decrees M/52, M/61, M/66 (1443H), M/191 and M/21
(1447H); the 12 added articles are chiefly the new chapter on licensing foreign
law firms (arts 44-55) plus art 21-mukarrar. Each amended/added/repealed article
carries its version history; the repealed article retains its full body and is
FLAGGED, not deleted, and its LLM title gets a '(ملغاة)' suffix. The section-API
status equals the statuteStructure/PDF status for every article (no dual-status
divergence). Every record carries legal_status_ar plus is_repealed/is_amended/
is_added flags. Arabic governs; no translation/paraphrase/interpretation.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "law_practice", "law", "official_source",
                   "law_practice_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "law_practice", "law", "verified")
RECORDS = os.path.join(OUT_VER, "law_practice_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "law_practice_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "law_practice_arabic_legal_llm",
                        "law_practice_law_legal_llm_001_056.json")

LAW_ID = "sa-law-practice-m38-1422"
LAW_AR = "نظام المحاماة"
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    m = re.match(r"law_practice_art_(\d{3})(_mukarrar)?$", key)
    return (int(m.group(1)), 1 if m.group(2) else 0)


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        m = re.match(r"law_practice_art_(\d{3})(_mukarrar)?$", key)
        n, is_muk = int(m.group(1)), bool(m.group(2))
        suffix = "-mukarrar" if is_muk else ""
        ls = a.get("legal_status_ar")
        is_repealed = ls == "ملغاة"
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        text = a["text"]
        hist = a.get("history")
        ver.append({"law_key": "law_practice", "law_component": "law", "language": "ar",
                    "record_layer": "LAW_PRACTICE_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_muk, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": hist,
                    "pdf_similarity": a.get("pdf_similarity"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; official MOJ consolidated text "
                                              "cross-verified against the official MOJ PDF; "
                                              "amendment status flagged (see source artifact)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_muk, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "law-practice-law-llm-art-%03d%s" % (n, suffix),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s%s" % (LAW_AR, a["number_label_ar"],
                                                   " (ملغاة)" if is_repealed else ""),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "law_practice/law/articles/%03d%s" % (n, suffix),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام المحاماة" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Ministry of Justice (MOJ) — official legal portal",
                                     "source_authority_ar": "وزارة العدل — المنصة القانونية الرسمية",
                                     "source_status": "moj_portal_api_cross_checked_official_pdf",
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "law_practice", "layer": "LAW_PRACTICE_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-law-practice-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (56 مادة؛ نص موحّد: 35 أصلية، 8 معدّلة، 12 مضافة، 1 ملغاة)",
               "title_en": "Saudi Code of Law Practice — Arabic LLM-ready layer (56 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 55], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Code of Law Practice records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
