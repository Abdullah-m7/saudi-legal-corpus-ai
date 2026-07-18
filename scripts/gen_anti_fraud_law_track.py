#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Anti-Commercial Fraud Law track (نظام مكافحة الغش التجاري,
Royal Decree M/19, 23/4/1429H, approving Council of Ministers Decision
No. 119, 22/4/1429H). Repeals the prior system, Royal Decree M/11,
29/5/1404H (per this law's own Article 29). Administered by the Ministry
of Commerce's Consumer Protection Agency (الإدارة العامة لمكافحة الغش
التجاري).

SOURCING TIER — SECONDARY_MULTI_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE:
laws.boe.gov.sa (the first-party government legal portal) was attempted
directly and returned HTTP 503 both times it was retried (two different
URL forms), matching this corpus's established BOE-egress-blocked pattern.
This track instead rests on three independent secondary sources
(nezams.com, mustsharik.com, mohamah.net), cross-verified against each
other article-by-article, plus a fresh WebFetch re-check of a 5-article
sample (1, 5, 13, 23, 25) against nezams.com and mustsharik.com directly.
See sources/anti_fraud/law/official_source/anti_fraud_law_official_source.json's
verification_methodology_note and known_unresolved_discrepancies for the
full caveat, including the genuinely disputed citation for Article 5's
second amendment (Council of Ministers Resolution 508 vs. Royal Decree
M/76) and the mechanically-spliced (not single-source-verbatim) current
text of Article 5.

30 articles across 5 فصول: التعريفات (1); المخالفات (2-4); الضبط والتحقيق
والمحاكمة (5-15); العقوبات (16-27); أحكام ختامية (28-30). 25 اصلية / 5
معدلة (Articles 5 [amended twice], 13, 23, 25, 27) / 0 ملغاة / 0 مضافة.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation, and no English or Chinese text is produced for this
track. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "anti_fraud", "law", "official_source",
                   "anti_fraud_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "anti_fraud", "law", "verified")
RECORDS = os.path.join(OUT_VER, "anti_fraud_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "anti_fraud_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "anti_fraud_arabic_legal_llm",
                        "anti_fraud_law_legal_llm_001_030.json")

LAW_ID = "sa-anti-fraud-law-m19-1429"
LAW_AR = "نظام مكافحة الغش التجاري"
STATUS = "SECONDARY_MULTI_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE"
KEY_RE = r"anti_fraud_art_(\d{3})$"
AMENDED_KEYS = {"anti_fraud_art_005", "anti_fraud_art_013",
                "anti_fraud_art_023", "anti_fraud_art_025",
                "anti_fraud_art_027"}
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك أنه إنه التي الذين اللذين هذه هؤلاء").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    m = re.match(KEY_RE, key)
    return int(m.group(1))


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for idx, key in enumerate(keys, start=1):
        a = arts[key]
        n = _sort_key(key)
        ls = a.get("legal_status_ar")
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        is_repealed = ls == "ملغاة"
        text = a["text"]
        ver.append({"law_key": "anti_fraud", "law_component": "law", "language": "ar",
                    "record_layer": "ANTI_FRAUD_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": a.get("history"),
                    "original_1429h_text": a.get("original_1429h_text"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track's governing current "
                                              "text rests on three cross-verified secondary "
                                              "sources (nezams.com, mustsharik.com, "
                                              "mohamah.net) since laws.boe.gov.sa is confirmed "
                                              "unreachable this pass -- see "
                                              "verification_methodology_note in the source "
                                              "artifact for the full caveat, including the "
                                              "disputed Article 5 second-amendment citation "
                                              "and its mechanically-spliced current text."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "anti-fraud-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "anti_fraud/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام مكافحة الغش التجاري" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree — cross-verified "
                                                          "secondary sources (nezams.com, "
                                                          "mustsharik.com, mohamah.net); "
                                                          "laws.boe.gov.sa confirmed "
                                                          "unreachable this pass (HTTP 503)"),
                                     "source_authority_ar": "مرسوم ملكي — مصادر ثانوية متعددة متقاطعة (نزامز، مستشارك، محاماة نت)، مع تعذر الوصول المؤكد لبوابة هيئة الخبراء (BOE)",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "anti_fraud",
               "layer": "ANTI_FRAUD_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-anti-fraud-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (30 مادة؛ نص موحّد: 25 أصلية، 5 معدّلة)",
               "title_en": "Saudi Anti-Commercial Fraud Law (M/19) — Arabic LLM-ready layer (30 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 30], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Anti-Commercial Fraud Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
