#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Procedural Guide for the Electronic Litigation Service
(الدليل الإجرائي لخدمة التقاضي الإلكتروني).

Source: the official MOJ legal-portal text (Minister of Justice Decision
8056, 05/10/1441H), fetched item-by-item (get-Section-Changes, 0
divergences from statuteStructure) and cross-verified against the official
MOJ PDF. Item 1 is labeled "مقدمة" (Preamble); items 2-5 are labeled with
the portal's own full-heading "sequence" field combining an Arabic ordinal
word and a description (e.g. "أولاً: أحكام عامة"), not bare مادة numbering.
The MOJ portal's own legalType classification for this instrument is
"لائحة", hence law_component="regulation" per this corpus's convention.
This PDF's raw text layer exhibits the known RTL word-order
glyph-extraction artifact seen elsewhere in this corpus (scores very low,
~0.15-0.30), but the 300dpi tesseract-ara OCR channel cleared 3 of 5 items
outright (1, 2, 4); the other 2 (items 3, 5 — the shortest items) scored
0.8815-0.8982 — below floor due to short absolute length amplifying minor
OCR artifacts — and were visually adjudicated against the rendered PDF
pages, confirming verbatim match. This regulation is IN FORCE. FRESH FULL
ISSUANCE: all 5 اصلية (0 معدلة / 0 ملغاة / 0 مضافة).

POST-CAPTURE NORMALIZATION (source-level, already applied to
official_source.json before this generator runs): this document exhibits
pervasive full-justification decorative kashida (typesetting
stretch-justification baked into the portal HTML/PDF source) across items
1, 2, 3, 5 (356 tatweel characters total across those four items, 0 in item
4) — a formatting artifact of the source document, not legal content; per
this corpus's standing convention (matching the judiciary_bog_mechanism
track precedent), all in-word decorative tatweel between two Arabic
letters was normalized/removed prior to ingestion, restoring the words to
their standard spelling (e.g. "اسـتكمالا" -> "استكمالا", "عليهـا" ->
"عليها"). This did not touch any content, only justification-stretch
characters; the automated PDF-similarity scores are unaffected since the
scoring pipeline already strips tatweel during normalization before
comparison.

DOCUMENTED SOURCE ANOMALY: item 4's first numbered sub-point under "النوع
الأول: الجلسة الكتابية" reads "تبدأ الجلسة الكتابية) بافتتاح..." — a
missing opening parenthesis (the term is written "(الجلسة الكتابية)"
consistently elsewhere in the same item and document) — confirmed present
identically in both official sources, a genuine minor typographical
anomaly in the source's own text, preserved verbatim, not corrected.

Items are numbered by their ordinal position (1..5; no مكرر), flat
structure with no chapter/section wrapper. No legal text is altered.
Arabic governs; no translation/paraphrase/interpretation. Read-only over
input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "elitigation_guide", "regulation", "official_source",
                   "elitigation_guide_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "elitigation_guide", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "elitigation_guide_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "elitigation_guide_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "elitigation_guide_arabic_legal_llm",
                        "elitigation_guide_regulation_legal_llm_001_005.json")

LAW_ID = "sa-elitigation-guide-regulation-1441"
LAW_AR = "الدليل الإجرائي لخدمة التقاضي الإلكتروني"
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
KEY_RE = r"elitigation_guide_art_(\d{3})$"
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
        ver.append({"law_key": "elitigation_guide", "law_component": "regulation", "language": "ar",
                    "record_layer": "ELITIGATION_GUIDE_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "pdf_similarity": a.get("pdf_similarity"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; official MOJ portal text cross-verified "
                                              "against the official MOJ PDF (verbatim; 3 of 5 items "
                                              "matched the >=0.90 floor outright via the 300dpi "
                                              "tesseract-ara OCR channel, the raw PDF text layer alone "
                                              "exhibiting the known RTL word-order glyph-extraction "
                                              "artifact seen elsewhere in this corpus and scoring very "
                                              "low; mean 0.938, min 0.8815; the remaining 2 items (3, 5) "
                                              "were read directly off the rendered 200dpi PDF pages as "
                                              "a direct visual cross-check and confirmed verbatim; all "
                                              "5 items / all 3 pages were visually read in full)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "elitigation-guide-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "elitigation_guide/regulation/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["%s %s" % (a["number_label_ar"], LAW_AR),
                                          "%s %s" % (LAW_AR, a["number_label_ar"]),
                                          "التقاضي الإلكتروني %s" % a["number_label_ar"]],
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
    json.dump({"law_key": "elitigation_guide", "layer": "ELITIGATION_GUIDE_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "visually_adjudicated": src["stats"]["visually_adjudicated"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-elitigation-guide-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (5 بنود؛ إصدار جديد كامل: 5 أصلية)",
               "title_en": "Procedural Guide for the Electronic Litigation Service — Arabic LLM-ready layer (5 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 5], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Electronic Litigation Procedural Guide records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
