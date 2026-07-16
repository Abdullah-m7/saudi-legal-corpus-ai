#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Electronic Transactions Law track (نظام التعاملات الإلكترونية,
Royal Decree M/18, 8/3/1428H).

DISTINCT VERIFICATION TIER — laws.boe.gov.sa was unreachable this research
pass by every method tried (direct curl TLS reset; r.jina.ai timed out
repeatedly and then rate-limited the IP with a 401; WebFetch via the same
proxy 422'd). PRIMARY SOURCE USED INSTEAD: the official Bureau of Experts/
Council of Ministers "Official Translation Division" bilingual PDF
(sdb.gov.sa-hosted, first edition 1431H) — the same booklet BOE itself
distributes for this law. EXTRACTION HAZARD: this PDF's embedded text has a
systematic, deterministic lam+alef ligature-reversal bug confirmed via two
independent extraction libraries giving identical corruption, and the PDF
renders as entirely blank pages (ruling out OCR as a cross-check); text was
corrected via direct native-fluency reading rather than blind regex
substitution. CROSS-VERIFIED structurally against the complete official
WIPO Lex English translation (100% of articles, no discrepancies) and via
wording spot-checks against independent clean-Unicode Arabic sources
(ramilawyer.sa, qanoniah.com, lexismiddleeast.com, uqn.gov.sa). The 2023
amendment text (Council of Ministers Resolution 293, 9/4/1445H) came from a
fourth independent, cleanly-encoded HTML source (nezams.com), never
PDF-sourced.

See sources/electronic_transactions/law/official_source/
electronic_transactions_law_official_source.json for the full methodology
note and documented unresolved discrepancies (most importantly: the exact
post-Chapter-6-abolition article renumbering could not be confirmed, so
this track preserves the ORIGINAL 1-31 numbering with articles 16-17
flagged ملغاة rather than guessing a renumbering).

Consolidated amended law: 24 اصلية / 5 معدلة / 2 ملغاة / 0 مضافة (31 total
articles). Articles are numbered by ordinal position 1..31, no مكرر,
organized under 10 original chapters with section_ar carrying each
article's chapter heading (Chapter 5's heading reflects its 2023-amended
title; Chapter 6 is abolished but its 2 articles are still ingested,
flagged ملغاة, not deleted).

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "electronic_transactions", "law", "official_source",
                   "electronic_transactions_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "electronic_transactions", "law", "verified")
RECORDS = os.path.join(OUT_VER, "electronic_transactions_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "electronic_transactions_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "electronic_transactions_arabic_legal_llm",
                        "electronic_transactions_law_legal_llm_001_031.json")

LAW_ID = "sa-electronic-transactions-law-m18-1428"
LAW_AR = "نظام التعاملات الإلكترونية"
STATUS = "SINGLE_PRIMARY_SOURCE_WIPO_STRUCTURAL_CROSS_CHECK_MANUAL_LIGATURE_CORRECTION"
KEY_RE = r"electronic_transactions_art_(\d{3})$"
AMENDED_KEYS = {"electronic_transactions_art_%03d" % n for n in (1, 3, 15, 29, 30)}
REPEALED_KEYS = {"electronic_transactions_art_%03d" % n for n in (16, 17)}
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
        is_repealed = ls == "ملغاة"
        text = a["text"]
        ver.append({"law_key": "electronic_transactions", "law_component": "law", "language": "ar",
                    "record_layer": "ELECTRONIC_TRANSACTIONS_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": False,
                    "amendment_history": a.get("history"),
                    "original_2007_text": a.get("original_2007_text"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track uses a distinct "
                                              "verification tier — single primary source (the "
                                              "official BOE/CoM translation-bureau PDF, manually "
                                              "corrected for a systematic ligature-extraction "
                                              "bug) structurally cross-checked against WIPO Lex's "
                                              "full English translation and spot-checked against "
                                              "independent clean-Unicode Arabic fragments, because "
                                              "laws.boe.gov.sa was unreachable this research pass "
                                              "— see verification_methodology_note in the source "
                                              "artifact for the full caveat."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": False,
                    "record_id": "electronic-transactions-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "electronic_transactions/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام التعاملات الإلكترونية" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree — official BOE/CoM "
                                                          "translation-bureau PDF (primary "
                                                          "source), WIPO Lex structural "
                                                          "cross-check, laws.boe.gov.sa "
                                                          "unreachable this pass"),
                                     "source_authority_ar": "مرسوم ملكي — نسخة رسمية من إدارة الترجمة الرسمية بهيئة الخبراء (المصدر الأساسي)، تحقق هيكلي مقارنة بـ WIPO Lex",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "electronic_transactions",
               "layer": "ELECTRONIC_TRANSACTIONS_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-electronic-transactions-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (31 مادة؛ نص موحّد: 24 أصلية، 5 معدّلة، 2 ملغاة)",
               "title_en": "Saudi Electronic Transactions Law — Arabic LLM-ready layer (31 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 31], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Electronic Transactions Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
