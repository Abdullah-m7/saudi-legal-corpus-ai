#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the High-Risk Professions Work Organization Regulation track
(لائحة تنظيم العمل في المهن ذات المخاطر العالية), issued by the Minister of
Human Resources and Social Development in his capacity as Chairman of the
National Committee/Council for Occupational Safety and Health (NCOSH),
adopted per NCOSH Council's 13th meeting (27/12/1446H = 23/6/2025G) and
published in the Umm Al-Qura Official Gazette (uqn.gov.sa, entry p=28771)
with a dateline of 20/7/1447H = 9/1/2026G -- a VERY RECENT instrument, one
of the newest in this corpus.

VERIFICATION TIER -- see this track's own official_source.json for the full
account (verification_methodology_note / known_unresolved_discrepancies).
Summary:

TIER: TIER_1_PRIMARY_MULTI_SOURCE. Two independently-produced official/
primary government sources were reached and agree this pass: (1) NCOSH's own
direct Arabic PDF (https://ncosh.gov.sa/media/gwwhsqoc/rowhro-25-ar.pdf, HTTP
200, 88 pages, born-digital); and (2) the Umm Al-Qura Official Gazette
(uqn.gov.sa/details?p=28771, HTTP 200), an entirely separate government
portal, whose own entry reproduces the Minister's adoption-decision text
verbatim and independently confirms this Regulation's existence, issuing
chain, and Article 19's own 180-day effective-date rule.

ARTICLE TEXT -- INDEPENDENT VISUAL RE-EXTRACTION OF THE SAME PDF: this track
discovered that the ncosh.gov.sa PDF's own embedded text layer (both via
poppler's pdftotext AND PyMuPDF/fitz -- both tools agree) contains a
systematic, silent character-transposition bug reversing the mandatory
Arabic 'لا' (lam-alef) ligature into 'ال' wherever it occurs inside a word
(e.g. the Regulation's own title 'لائحة' extracts as 'الئحة'), plus similar
transpositions at certain word endings -- consistent with a known category
of Microsoft-Word-exported-PDF ToUnicode defects (matching this file's own
creator metadata). This corruption is NOT safely auto-correctable (word-
medial 'ال' is unambiguously wrong, but word-initial 'ال' is genuinely
ambiguous between a correct definite article and a corrupted 'لا'). NONE of
the 19 article texts were taken from that text layer: every article was
rendered as a 300dpi page image from the SAME official PDF and independently
transcribed by direct visual reading of the rendered glyphs -- i.e. the
"independent OCR / rendered-page-image pass of the SAME official document"
standard this corpus uses elsewhere for Tier 1. The buggy text layer was
used only to navigate chapter/article boundaries, never as a source of
final Arabic wording.

19 articles across 6 substantive chapters (chapter_structure), all اصلية
(first, single edition; no amendment found this pass). Chapter Seven
(الملحقات/Appendix, PDF pages 19-88 of 88) carries NO numbered article at
all -- a 222-profession classification table plus per-profession bilingual
medical-fitness-examination schedules -- and is NOT ingested article-by-
article this pass (out of scope; see appendix_note_ar and
known_unresolved_discrepancies in the source artifact).

The specific citation "Ministerial Decision No. 64762, dated 13/5/1447H"
supplied in this track's own commissioning brief could NOT be independently
corroborated on any of the four sources actually reached this pass (the
ncosh.gov.sa PDF itself, the uqn.gov.sa gazette entry, qanoonsa.com, or
ajel.sa) -- documented honestly as an unresolved discrepancy rather than
silently asserted as confirmed fact.

Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "high_risk_professions_regulation", "law",
                   "official_source", "high_risk_professions_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "high_risk_professions_regulation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "high_risk_professions_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "high_risk_professions_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "high_risk_professions_regulation_arabic_legal_llm",
                        "high_risk_professions_regulation_legal_llm_001_019.json")

LAW_ID = "sa-high-risk-professions-regulation-1447"
LAW_AR = "لائحة تنظيم العمل في المهن ذات المخاطر العالية"
STATUS = "NCOSH_OFFICIAL_PDF_PRIMARY_VISUAL_REEXTRACTION_UQN_GAZETTE_CROSS_VERIFIED"
KEY_RE = r"high_risk_professions_regulation_art_(\d{3})$"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا وفقاً بحسب فإن وإن المادة اللائحة أحكام يجب يجوز عليه دون "
            "فيما منه منها وإذا حال وله ولها الآتية يأتي يلي ذلك خلال وعلى وذلك وهذا وهذه غير أنه إليها "
            "إليه عليها منهم بينهم العامل الموظف").split())


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
        section = a.get("section_ar", "")
        title = a.get("article_title_ar", "")
        label = a["number_label_ar"] + ((": " + title) if title else "")
        ver.append({"law_key": "high_risk_professions_regulation", "law_component": "regulation",
                    "language": "ar",
                    "record_layer": "HIGH_RISK_PROFESSIONS_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "article_title_ar": title,
                    "section_ar": section,
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": is_amended,
                    "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; PRIMARY source is the "
                                              "official ncosh.gov.sa PDF "
                                              "(media/gwwhsqoc/rowhro-25-ar.pdf), "
                                              "cross-checked against the Umm Al-Qura "
                                              "Official Gazette (uqn.gov.sa, entry "
                                              "p=28771) -- two independent official "
                                              "sources. This article's own text was "
                                              "independently re-extracted by direct "
                                              "visual reading of a 300dpi rendered page "
                                              "image of the SAME official PDF, NOT from "
                                              "that PDF's own buggy text layer (which "
                                              "silently reverses the 'لا' ligature and "
                                              "certain word-final letter pairs -- see "
                                              "verification_methodology_note and "
                                              "known_unresolved_discrepancies in the "
                                              "source artifact before relying on this "
                                              "track's text)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": label,
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": is_amended, "is_added": ls == "مضافة",
                    "record_id": "high-risk-professions-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, label),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, label),
                    "article_path": "high_risk_professions_regulation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "%s من لائحة تنظيم العمل في المهن ذات المخاطر العالية"
                                          % a["number_label_ar"]],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": ("Ministerial decision adopting "
                                                          "the Regulation, cross-verified "
                                                          "via ncosh.gov.sa (issuing/"
                                                          "administering authority's own "
                                                          "PDF) and the Umm Al-Qura Official "
                                                          "Gazette (uqn.gov.sa, entry "
                                                          "p=28771, dateline 20/7/1447H = "
                                                          "9/1/2026G)"),
                                     "source_authority_ar": ("قرار معالي وزير الموارد البشرية "
                                                            "والتنمية الاجتماعية رئيس المجلس "
                                                            "الوطني للسلامة والصحة المهنية "
                                                            "باعتماد اللائحة -- تم التحقق "
                                                            "عبر ncosh.gov.sa (الجهة المصدرة/"
                                                            "المشرفة) وجريدة أم القرى الرسمية "
                                                            "(uqn.gov.sa, p=28771, بتاريخ "
                                                            "نشر مؤكَّد 20/7/1447هـ الموافق "
                                                            "9/1/2026م)"),
                                     "source_status": STATUS.lower(),
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "high_risk_professions_regulation",
               "layer": "HIGH_RISK_PROFESSIONS_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "decree_date_gregorian": src.get("decree_date_gregorian"),
               "administering_authority_en": src.get("administering_authority_en"),
               "consolidated_amended_law": False,
               "chapter_structure": src["chapter_structure"],
               "appendix_note_ar": src.get("appendix_note_ar"),
               "amendment_history": src.get("amendment_history"),
               "verification_methodology_note": src["verification_methodology_note"],
               "known_unresolved_discrepancies": src["known_unresolved_discrepancies"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-high-risk-professions-regulation-arabic-legal-llm-full",
               "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (19 مادة، "
                           "اصلية جميعها)",
               "title_en": ("High-Risk Professions Work Organization Regulation — Arabic "
                            "LLM-ready layer (19 records, all original/اصلية)"),
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 19], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready High-Risk Professions Regulation records"
          % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
