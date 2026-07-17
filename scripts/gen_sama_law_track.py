#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Saudi Central Bank Law track (نظام البنك المركزي السعودي,
Royal Decree M/36, 11/4/1442H).

DISTINCT VERIFICATION TIER — laws.boe.gov.sa's LIVE portal returned HTTP 503
on every attempt this research pass (direct and r.jina.ai-proxied). Full text
instead rests on TWO-SOURCE AGREEMENT: SAMA's own official PDF (the
administering government agency's own publication, current/in-force text)
as primary source A, cross-checked against a Wayback Machine archive
snapshot of the BOE portal's law-detail page dated 24 Jan 2022 — before the
sole amending instrument — as primary source B for the original/
pre-amendment wording. Secondary corroboration: qistas.com, nezams.com,
ajel.sa. See sources/sama/law/official_source/sama_law_official_source.json
for the full methodology note and documented unresolved discrepancies.

27 articles, 6 chapters (Chapter 2 has 3 lettered subsections: (a) Board of
Directors arts 8-12, (b) Governor/Deputy Governors/Staff arts 13-15, (c)
Conflict of Interest art 16). 24 اصلية / 3 معدلة (articles 8, 11, 14,
amended by Council of Ministers Resolution 412, 28/7/1443H, restructuring
the Governor's deputies from one to two). Articles 9, 10, and 12 carry
documented known_unresolved_discrepancies: genuine uncorrected cross-
references and a lettering-convention divergence present in the primary
source itself, preserved verbatim per this corpus's zero-fabrication
policy — never silently "fixed".

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "sama", "law", "official_source",
                   "sama_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "sama", "law", "verified")
RECORDS = os.path.join(OUT_VER, "sama_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "sama_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "sama_arabic_legal_llm",
                        "sama_law_legal_llm_001_027.json")

LAW_ID = "sa-sama-law-m36-1442"
LAW_AR = "نظام البنك المركزي السعودي"
STATUS = "GOVERNMENT_AGENCY_OFFICIAL_PDF_PRIMARY_SOURCE_BOE_ARCHIVE_CROSS_VERIFIED"
KEY_RE = r"sama_art_(\d{3})$"
AMENDED_KEYS = {"sama_art_008", "sama_art_011", "sama_art_014"}
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
        ver.append({"law_key": "sama", "law_component": "law", "language": "ar",
                    "record_layer": "SAMA_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": False,
                    "amendment_history": a.get("history"),
                    "original_1442h_text": a.get("original_1442h_text"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track uses a distinct "
                                              "verification tier — SAMA's own official PDF "
                                              "(current text) cross-checked against a BOE portal "
                                              "Wayback archive snapshot (original text), because "
                                              "laws.boe.gov.sa's live portal returned HTTP 503 on "
                                              "every attempt this research pass — see "
                                              "verification_methodology_note in the source "
                                              "artifact for the full caveat."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": is_amended, "is_added": False,
                    "record_id": "sama-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "sama/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام البنك المركزي" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree — SAMA's own official PDF "
                                                          "(current text), cross-checked against a "
                                                          "BOE portal Wayback archive snapshot "
                                                          "(original text); BOE live portal returned "
                                                          "HTTP 503 this pass"),
                                     "source_authority_ar": "مرسوم ملكي — بيان البنك المركزي السعودي الرسمي (النص الحالي)، مطابقة أرشيف بوابة هيئة الخبراء (النص الأصلي)",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "sama",
               "layer": "SAMA_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-sama-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (27 مادة؛ نص موحّد: 24 أصلية، 3 معدّلة)",
               "title_en": "Saudi Central Bank Law — Arabic LLM-ready layer (27 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 27], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready SAMA Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
