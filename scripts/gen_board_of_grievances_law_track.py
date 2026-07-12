#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Board of Grievances Law track (نظام ديوان المظالم م/78).

Source: the Board of Grievances' own official certified text (Royal Decree
M/78, 19/9/1428H) — the certified PDF (صورة طبق الأصل / هيئة الخبراء بمجلس
الوزراء) published on bog.gov.sa, with the Board's machine-readable DOCX used
as the text channel and independently corroborated by WIPO Lex (the same
official scan). The administrative judiciary sits under a separate authority
and is NOT on the MOJ legal portal, and the BOE consolidated database
(laws.boe.gov.sa) is network-unreachable here, so this track was sourced via
the user-approved Board + Umm Al-Qura gazette route: all 26 articles were
adjudicated VISUALLY, page-by-page, against the certified official PDF.

This law is IN FORCE and lightly amended: 25 articles are اصلية and exactly
ONE (Article 4) is معدلة — amended by قرار مجلس الوزراء 594 / المرسوم الملكي
م/180 (17/8/1446H), published in Umm Al-Qura issue 5072 (21 Feb 2025), which
added a fifth member category (عضوان من ذوي الخبرة والاختصاص) plus a 4-year
renewable royal-order tenure for items 4 and 5. The amendment scope (Article 4
only) and substance are officially confirmed by the SPA Council-of-Ministers
announcement; its verbatim wording is from a secondary rendering of gazette
5072 (BOE unreachable) and is flagged accordingly. Article 4 carries both its
current amended body and its original 1428 body in amendment_history; no
articles are repealed or added.

Every record carries legal_status_ar plus is_repealed/is_amended/is_added
flags. Arabic governs; no translation/paraphrase/interpretation. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "board_of_grievances", "law", "official_source",
                   "board_of_grievances_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "board_of_grievances", "law", "verified")
RECORDS = os.path.join(OUT_VER, "board_of_grievances_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "board_of_grievances_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "board_of_grievances_arabic_legal_llm",
                        "board_of_grievances_law_legal_llm_001_026.json")

LAW_ID = "sa-board-of-grievances-law-m78-1428"
LAW_AR = "نظام ديوان المظالم"
STATUS = "BOARD_OFFICIAL_PDF_VISUALLY_ADJUDICATED_GAZETTE_CONFIRMED"
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
    m = re.match(r"bog_law_art_(\d{3})(_mukarrar)?$", key)
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
        m = re.match(r"bog_law_art_(\d{3})(_mukarrar)?$", key)
        n, is_muk = int(m.group(1)), bool(m.group(2))
        suffix = "-mukarrar" if is_muk else ""
        ls = a.get("legal_status_ar")
        is_repealed = ls == "ملغاة"
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        text = a["text"]
        hist = a.get("history")
        ver.append({"law_key": "board_of_grievances", "law_component": "law", "language": "ar",
                    "record_layer": "BOARD_OF_GRIEVANCES_LAW_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; Board of Grievances official certified text "
                                              "adjudicated visually against the official Board PDF; the sole "
                                              "amended article (4) is flagged with its gazette-5072 amendment "
                                              "history (see source artifact)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_muk, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "board-of-grievances-law-llm-art-%03d%s" % (n, suffix),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s%s" % (LAW_AR, a["number_label_ar"],
                                                   " (ملغاة)" if is_repealed else ""),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "board_of_grievances/law/articles/%03d%s" % (n, suffix),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d ديوان المظالم" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Board of Grievances (bog.gov.sa) — official certified PDF; "
                                                         "amendment via Umm Al-Qura gazette, SPA-confirmed",
                                     "source_authority_ar": "ديوان المظالم — النسخة الرسمية المعتمدة؛ التعديل من جريدة أم القرى بتأكيد واس",
                                     "source_status": "board_official_pdf_visually_adjudicated_gazette_confirmed",
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "board_of_grievances", "layer": "BOARD_OF_GRIEVANCES_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-board-of-grievances-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (26 مادة؛ نص موحّد: 25 أصلية، 1 معدّلة)",
               "title_en": "Saudi Law of the Board of Grievances — Arabic LLM-ready layer (26 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 26], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Board of Grievances Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
