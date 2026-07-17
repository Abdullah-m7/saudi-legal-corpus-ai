#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Trademark Law track (قانون (نظام) العلامات التجارية لدول
مجلس التعاون لدول الخليج العربية, Royal Decree M/51, 26/7/1435H).

DISTINCT VERIFICATION TIER — laws.boe.gov.sa's live portal was unreachable
this research pass (503/connection-reset). Full text instead rests on
WIPO Lex's own hosted Arabic PDF, which embeds an official "بطاقة النظام"
(law status card) sourced from the Saudi National Center for Documents and
Archives confirming "ساري" (in force) — the functional equivalent of a
direct BOE-portal confirmation via a different retrieval path. The
amending Royal Decree M/49 (Article 1's two redefinitions) was a
scanned/non-text PDF, recovered via two independent Arabic-language OCR
passes that agreed verbatim.

See sources/trademark/law/official_source/trademark_law_official_source.json
for the full methodology note and all documented unresolved discrepancies,
including a materially conflicting claim from two secondary sources
(misa.gov.sa, nezams.com) that still present the SUPERSEDED 2002 law
(Royal Decree M/21) as if currently in force — this track proceeds on the
primary BOE-status-card-confirmed current law instead.

52 records: 51 اصلية / 1 معدلة (Article 1 — two of five definitions
replaced by Royal Decree M/49, 26/6/1442H, reflecting the transfer of
administering authority to SAIP; the other three definitions and the
remaining 51 articles are unamended). NO chapter (فصل) divisions — a flat
sequence, verified by full-text search of the source.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "trademark", "law", "official_source",
                   "trademark_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "trademark", "law", "verified")
RECORDS = os.path.join(OUT_VER, "trademark_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "trademark_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "trademark_arabic_legal_llm",
                        "trademark_law_legal_llm_001_052.json")

LAW_ID = "sa-trademark-law-m51-1435"
LAW_AR = "قانون (نظام) العلامات التجارية لدول مجلس التعاون لدول الخليج العربية"
STATUS = "WIPO_LEX_PRIMARY_PDF_X_BOE_STATUS_CARD_CROSS_VERIFIED"
KEY_RE = r"trademark_art_(\d{3})$"
AMENDED_KEYS = {"trademark_art_001"}
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
        is_amended = ls == "معدلة"
        text = a["text"]
        ver.append({"law_key": "trademark", "law_component": "law", "language": "ar",
                    "record_layer": "TRADEMARK_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": False,
                    "amendment_history": a.get("history"),
                    "original_1435h_text": a.get("original_1435h_text"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track uses a distinct "
                                              "verification tier — WIPO Lex's hosted primary "
                                              "PDF (which embeds an official BOE/National "
                                              "Archives Center status card confirming ساري/"
                                              "in force), because laws.boe.gov.sa's live "
                                              "portal was unreachable this research pass — see "
                                              "verification_methodology_note in the source "
                                              "artifact for the full caveat, including a "
                                              "documented conflict with secondary sources that "
                                              "still present the superseded 2002 law as current."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": False,
                    "record_id": "trademark-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "trademark/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام العلامات التجارية" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree — WIPO Lex primary "
                                                          "PDF with embedded BOE/National "
                                                          "Archives status card confirming "
                                                          "ساري (in force)"),
                                     "source_authority_ar": "مرسوم ملكي — ملف PDF من قاعدة بيانات WIPO Lex يتضمن بطاقة حالة رسمية من هيئة الخبراء/مركز الوثائق والمحفوظات الوطني تؤكد أن النظام ساري",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "trademark",
               "layer": "TRADEMARK_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-trademark-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (52 مادة؛ نص موحّد: 51 أصلية، 1 معدّلة)",
               "title_en": "Saudi Trademark Law (GCC unified law) — Arabic LLM-ready layer (52 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 52], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Trademark Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
