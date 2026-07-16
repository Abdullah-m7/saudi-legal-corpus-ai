#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Council of Ministers Law track (نظام مجلس الوزراء, Royal Order
A/13, 3/3/1414H).

DISTINCT VERIFICATION TIER — laws.boe.gov.sa was confirmed COMPLETELY
UNREACHABLE from the build environment across two separate research passes
this session (a WAF "Request Rejected" block on the first pass, then a fresh
retry on a dedicated confirmation pass hit 503/422/timeout — different
failure signatures each time, confirming the block is genuine and current,
not a one-off transient error). Neither of this corpus's two established
verification methods (MOJ portal DB x official PDF, or BOE-portal-via-Wayback
byte-identical cross-snapshot) was available. Instead, full text rests on
CROSS-VERIFIED AGREEMENT BETWEEN TWO INDEPENDENT ARABIC SECONDARY SOURCES:
ar.wikisource.org's transcription and nezams.com's transcription, which
agree word-for-word across all 32 articles. A third source, FAOLEX's English
PDF (faolex.fao.org/docs/pdf/sau213444.pdf), was used only for STRUCTURAL
cross-check (chapter count, article count, general subject-matter match per
chapter), not for wording. This is a distinct, clearly-flagged tier: dual
independent Arabic secondary sources standing in for a primary official
source that could not be reached, rather than a primary-source verification.

See sources/council_of_ministers/law/official_source/
council_of_ministers_law_official_source.json for the full methodology note
and documented unresolved discrepancies.

Consolidated amended law: 31 اصلية / 1 معدلة (article 30, amended by Royal
Order أ/151, 3/9/1432H) / 0 مضافة / 0 ملغاة (32 total articles). Articles are
numbered by ordinal position 1..32, no مكرر, organized under 8 chapters with
section_ar carrying each article's chapter heading. Article 7 carries a
companion_instrument_note documenting a related-but-non-textual exception
order (Royal Order أ/45, 4/2/1446H) that does not amend the article's text.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "council_of_ministers", "law", "official_source",
                   "council_of_ministers_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "council_of_ministers", "law", "verified")
RECORDS = os.path.join(OUT_VER, "council_of_ministers_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "council_of_ministers_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "council_of_ministers_arabic_legal_llm",
                        "council_of_ministers_law_legal_llm_001_032.json")

LAW_ID = "sa-council-of-ministers-law-a13-1414"
LAW_AR = "نظام مجلس الوزراء"
STATUS = "DUAL_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE"
KEY_RE = r"council_of_ministers_art_(\d{3})$"
AMENDED_KEYS = {"council_of_ministers_art_030"}
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
        ver.append({"law_key": "council_of_ministers", "law_component": "law", "language": "ar",
                    "record_layer": "COUNCIL_OF_MINISTERS_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": False, "is_amended": is_amended, "is_added": False,
                    "amendment_history": a.get("history"),
                    "original_1414h_text": a.get("original_1414h_text"),
                    "companion_instrument_note": a.get("companion_instrument_note"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; this track uses a distinct "
                                              "verification tier — dual independent Arabic "
                                              "secondary sources (ar.wikisource.org x nezams.com), "
                                              "not a primary BOE-portal source, because "
                                              "laws.boe.gov.sa was confirmed completely "
                                              "unreachable across two research passes — see "
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
                    "record_id": "council-of-ministers-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "council_of_ministers/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام مجلس الوزراء" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Royal Order — dual independent Arabic "
                                                          "secondary sources (BOE portal "
                                                          "confirmed unreachable, see "
                                                          "verification_methodology_note)"),
                                     "source_authority_ar": "أمر ملكي — مصدران عربيان ثانويان مستقلان متطابقان (بوابة هيئة الخبراء غير متاحة)",
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "council_of_ministers",
               "layer": "COUNCIL_OF_MINISTERS_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "chapter_structure": src["chapter_structure"],
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-council-of-ministers-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (32 مادة؛ نص موحّد: 31 أصلية، 1 معدّلة)",
               "title_en": "Saudi Council of Ministers Law — Arabic LLM-ready layer (32 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 32], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Council of Ministers Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
