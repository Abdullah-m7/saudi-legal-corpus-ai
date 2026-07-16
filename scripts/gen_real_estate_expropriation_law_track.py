#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Law on Expropriation of Real Estate for Public Interest and
Temporary Seizure of Real Estate (نظام نزع ملكية العقارات للمصلحة العامة
ووضع اليد المؤقت على العقارات).

Source: the official MOJ legal-portal text (Royal Decree M/56, 12/03/1447H),
fetched article-by-article (get-Section-Changes, 0 divergences from
statuteStructure) and cross-verified against the official MOJ PDF. 39
articles across 6 chapters (الباب الأول..السادس: تعريفات وأحكام عامة /
إجراءات نزع ملكية العقارات / الحصر والتقييم / التعويض والإخلاء / وضع اليد
المؤقت على العقارات / أحكام ختامية); section_ar carries each article's
chapter heading, matching this corpus's convention for chaptered
instruments. This PDF's raw text layer exhibits the known RTL word-order
glyph-extraction artifact seen elsewhere in this corpus, but the 300dpi
tesseract-ara OCR channel and the word-reversed text-layer channel together
cleared 38 of 39 articles outright; the other 1 (art_022, a long
4-paragraph article spanning a page-internal paragraph run) was visually
adjudicated against the rendered PDF page, confirming verbatim match. This
law is IN FORCE. FRESH FULL ISSUANCE: all 39 اصلية (0 معدلة / 0 ملغاة / 0
مضافة). Per its own art 37 (closing provisions), this law replaces and
repeals the older 1424H expropriation law (Royal Decree M/15), independently
confirmed ملغي on the portal.

SOURCE-LEVEL CLEANUP (already applied to official_source.json before this
generator runs): 1 decorative in-word tatweel character (not immediately
preceded by heh) stripped from art_027 — confirmed present identically in
the portal DB and the official PDF's own typesetting.

DOCUMENTED SOURCE ANOMALY: art_039's ordinal heading reads "المادة التاسعة
الثلاثون" (missing the conjunction و before الثلاثون, which every other
compound ordinal in this instrument carries), confirmed identical in both
official sources, preserved verbatim, not corrected.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "real_estate_expropriation", "law", "official_source",
                   "real_estate_expropriation_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "real_estate_expropriation", "law", "verified")
RECORDS = os.path.join(OUT_VER, "real_estate_expropriation_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "real_estate_expropriation_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "real_estate_expropriation_arabic_legal_llm",
                        "real_estate_expropriation_law_legal_llm_001_039.json")

LAW_ID = "sa-real-estate-expropriation-law-1447"
LAW_AR = "نظام نزع ملكية العقارات للمصلحة العامة ووضع اليد المؤقت على العقارات"
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
KEY_RE = r"real_estate_expropriation_art_(\d{3})$"
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
        section = a.get("section_ar", "")
        ver.append({"law_key": "real_estate_expropriation", "law_component": "law", "language": "ar",
                    "record_layer": "REAL_ESTATE_EXPROPRIATION_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": False, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": section,
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "pdf_similarity": a.get("pdf_similarity"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; official MOJ portal text cross-verified "
                                              "against the official MOJ PDF (verbatim; 38 of 39 "
                                              "articles matched the >=0.90 floor outright via the "
                                              "300dpi tesseract-ara OCR channel and/or the "
                                              "word-reversed text-layer channel, the raw PDF text "
                                              "layer alone exhibiting the known RTL word-order "
                                              "glyph-extraction artifact seen elsewhere in this "
                                              "corpus and scoring very low; mean 0.9794, min 0.7807; "
                                              "the remaining 1 article (art_022, a long 4-paragraph "
                                              "article spanning a page-internal paragraph run) was "
                                              "read directly off the rendered 200dpi/400dpi official "
                                              "PDF page as a direct visual cross-check and confirmed "
                                              "verbatim, including 1 documented character-level "
                                              "cleanup: a decorative in-word tatweel in art_027, "
                                              "stripped per corpus convention and confirmed present "
                                              "identically in the portal DB and the official PDF's "
                                              "own typesetting; all 39 articles across all 8 pages "
                                              "were visually read in full)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": section,
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "real-estate-expropriation-law-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "real_estate_expropriation/law/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نزع ملكية العقارات" % n],
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
    json.dump({"law_key": "real_estate_expropriation",
               "layer": "REAL_ESTATE_EXPROPRIATION_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "visually_adjudicated": src["stats"]["visually_adjudicated"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-real-estate-expropriation-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (39 مادة؛ إصدار جديد كامل: 39 أصلية)",
               "title_en": "Law on Expropriation of Real Estate for Public Interest and Temporary Seizure — Arabic LLM-ready layer (39 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 39], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Real Estate Expropriation Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
