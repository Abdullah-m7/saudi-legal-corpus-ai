#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Telecommunications and Information Technology Act track
(نظام الاتصالات وتقنية المعلومات, Royal Decree M/106, 2/11/1443H).

FRESH REPLACEMENT LAW — this Royal Decree replaces the prior Telecommunications
Law (M/12, 12/3/1422H) in its entirety; all 41 articles are اصلية (no confirmed
enacted amendments since promulgation). laws.boe.gov.sa WAS reachable this
research pass (via the r.jina.ai proxy fallback) and served as the PRIMARY
source; the Ministry of Communications and Information Technology's own
official PDF was used as a structural/textual cross-check, which resolved one
digit-transcription artifact in Article 6. A 2024 public consultation
(istitlaa.ncc.gov.sa) proposed amendments to Articles 20, 24, 25 and 27, but
enactment could NOT be confirmed as of this build — the CONFIRMED BOE
"in force" text is ingested for all four, each flagged via
known_unresolved_discrepancies for periodic re-verification. Article 41's
Gregorian effective-date computation carries a minor (~3 day) unresolved
discrepancy across secondary sources, immaterial to the article's own Arabic
text. A companion Implementing Regulation exists but was not extracted this
pass (candidate for a follow-up companion track).

See sources/telecommunications/law/official_source/
telecommunications_law_official_source.json for the full methodology note and
documented unresolved discrepancies.

41 articles, all اصلية, organized under 10 chapters with section_ar carrying
each article's chapter heading. No مكرر articles.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "telecommunications", "law", "official_source",
                   "telecommunications_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "telecommunications", "law", "verified")
RECORDS = os.path.join(OUT_VER, "telecommunications_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "telecommunications_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "telecommunications_arabic_legal_llm",
                        "telecommunications_law_legal_llm_001_041.json")

LAW_ID = "sa-telecommunications-law-m106-1443"
LAW_AR = "نظام الاتصالات وتقنية المعلومات"
STATUS = "BOE_PORTAL_PRIMARY_SOURCE_MCIT_PDF_CROSS_CHECKED"
KEY_RE = r"telecommunications_art_(\d{3})$"
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
        text = a["text"]
        ver.append({"law_key": "telecommunications", "law_component": "law", "language": "ar",
                    "record_layer": "TELECOMMUNICATIONS_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": False, "is_added": False,
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; laws.boe.gov.sa served as the "
                                              "primary source this research pass (via the "
                                              "r.jina.ai proxy fallback), cross-checked against "
                                              "the Ministry of Communications and Information "
                                              "Technology's own official PDF — see "
                                              "verification_methodology_note in the source "
                                              "artifact for the full caveat and the resolved "
                                              "Article 6 digit-transcription artifact."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": False,
                    "is_amended": False, "is_added": False,
                    "record_id": "telecommunications-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "telecommunications/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام الاتصالات" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Decree — laws.boe.gov.sa primary "
                                                          "source, cross-checked against MCIT's "
                                                          "own official PDF"),
                                     "source_authority_ar": "مرسوم ملكي — بوابة هيئة الخبراء (مصدر أساسي)، مطابقة نص وزارة الاتصالات وتقنية المعلومات",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "telecommunications",
               "layer": "TELECOMMUNICATIONS_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-telecommunications-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (41 مادة؛ نظام جديد كامل: 41 أصلية)",
               "title_en": "Saudi Telecommunications and Information Technology Act — Arabic LLM-ready layer (41 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 41], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Telecommunications Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
