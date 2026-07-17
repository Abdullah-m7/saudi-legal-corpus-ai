#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Banking Control Law track (نظام مراقبة البنوك, Royal Decree
M/5, 22/2/1386H).

DISTINCT VERIFICATION TIER — laws.boe.gov.sa was unreachable for raw text
this research pass (HTTP 503 live; HTTP 422 via r.jina.ai; a Wayback Machine
snapshot exists but returned HTTP 403 to direct fetch and was unreachable
via WebFetch entirely). Only BOE's own tool-side SUMMARIZATION (not raw
text) was obtainable, confirming metadata but not usable as a primary
verbatim-text source. Full text instead rests on CROSS-VERIFIED AGREEMENT
BETWEEN TWO INDEPENDENT ARABIC SOURCES: alsayrfah.com's reproduction and
bfc.gov.sa's reproduction (a Saudi finance-sector regulator's own copy,
which uniquely preserves the Umm al-Qura Gazette masthead and the sole
amendment's footnote), agreeing word-for-word on all 26 articles. Further
corroborated structurally by Saudipedia.com and BOE's own tool-side summary.

See sources/banking_control/law/official_source/
banking_control_law_official_source.json for the full methodology note and
documented unresolved discrepancies.

Distinct from the Saudi Central Bank Law (نظام البنك المركزي السعودي,
Royal Decree M/36, 1442H, already in this corpus) — not conflated. NO
chapter (فصل) divisions — a flat sequence of 26 articles, 25 اصلية / 1
معدلة (article 13, amended by Royal Decree M/2, 6/1/1391H — only the
current wording could be recovered; the pre-1391H original is an
irrecoverable gap, documented not guessed). Article 16 carries a genuine
source-text irregularity (uses "مؤسسة النقد" instead of the term "المؤسسة"
defined and used elsewhere), preserved verbatim.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "banking_control", "law", "official_source",
                   "banking_control_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "banking_control", "law", "verified")
RECORDS = os.path.join(OUT_VER, "banking_control_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "banking_control_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "banking_control_arabic_legal_llm",
                        "banking_control_law_legal_llm_001_026.json")

LAW_ID = "sa-banking-control-law-m5-1386"
LAW_AR = "نظام مراقبة البنوك"
STATUS = "DUAL_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE"
KEY_RE = r"banking_control_art_(\d{3})$"
AMENDED_KEYS = {"banking_control_art_013"}
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
        ver.append({"law_key": "banking_control", "law_component": "law", "language": "ar",
                    "record_layer": "BANKING_CONTROL_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": False,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track uses a distinct "
                                              "verification tier — dual independent Arabic "
                                              "secondary sources (alsayrfah.com x bfc.gov.sa), "
                                              "not a primary BOE-portal source, because "
                                              "laws.boe.gov.sa was unreachable for raw text this "
                                              "research pass — see verification_methodology_note "
                                              "in the source artifact for the full caveat."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": False,
                    "record_id": "banking-control-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "banking_control/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام مراقبة البنوك" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree — dual independent "
                                                          "Arabic secondary sources "
                                                          "(alsayrfah.com x bfc.gov.sa), "
                                                          "laws.boe.gov.sa unreachable for raw "
                                                          "text this pass"),
                                     "source_authority_ar": "مرسوم ملكي — مصدران عربيان ثانويان مستقلان متطابقان (بوابة هيئة الخبراء غير متاحة كنص خام)",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "banking_control",
               "layer": "BANKING_CONTROL_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-banking-control-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (26 مادة؛ نص موحّد: 25 أصلية، 1 معدّلة)",
               "title_en": "Saudi Banking Control Law — Arabic LLM-ready layer (26 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 26], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Banking Control Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
