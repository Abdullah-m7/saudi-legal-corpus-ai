#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Notarization Law Implementing Regulation track.

Source: the official MOJ legal-portal text of the Implementing Regulation of the
Notarization Law (اللائحة التنفيذية لنظام التوثيق), issued by Minister of Justice
Decision No. 1948 dated 1/6/1442H (legalStatus Active), fetched article-by-article
(get-Section-Changes) and cross-verified against the official MOJ PDF. 31 records:
30 numbered articles (1..30) plus the official fee schedule «جدول المقابل المالي»
(record 31). FRESH FULL ISSUANCE: all 31 اصلية (0 معدلة / 0 ملغاة / 0 مضافة).

VERIFICATION: 21/31 matched the PDF outright (>=0.90). The OCR channel was
unavailable in the build environment (tesseract-ara did not complete on this PDF's
page images), and this PDF's text layer reorders/splits clauses and drops some
ligature/digit glyphs on 10 multi-clause/list articles (arts 1, 2, 4, 11, 18, 23,
24, 26, 27, 28); each of those 10 was adjudicated VISUALLY VERBATIM on the rendered
official PDF pages (every clause confirmed present and matching the portal text).
The section-API status equals the statuteStructure/PDF status for every article (no
dual-status divergence).

No legal text is altered. Arabic governs; no translation/paraphrase/interpretation.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "tawtheeq", "regulation", "official_source",
                   "tawtheeq_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "tawtheeq", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "tawtheeq_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "tawtheeq_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "tawtheeq_arabic_legal_llm",
                        "tawtheeq_regulation_legal_llm_001_031.json")

LAW_ID = "sa-tawtheeq-regulation-mojd1948-1442"
LAW_AR = "اللائحة التنفيذية لنظام التوثيق"
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
KEY_RE = r"tawtheeq_reg_art_(\d{3})$"
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
        is_fee = bool(a.get("is_fee_schedule"))
        text = a["text"]
        ver.append({"law_key": "tawtheeq", "law_component": "implementing_regulation", "language": "ar",
                    "record_layer": "TAWTHEEQ_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_fee_schedule": is_fee, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": ls == "ملغاة", "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "amendment_history": a.get("history"),
                    "pdf_similarity": a.get("pdf_similarity"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; official MOJ text cross-verified against "
                                              "the official MOJ PDF (verbatim; low-similarity list articles "
                                              "adjudicated visually on the rendered pages)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "implementing_regulation", "article_number": n,
                    "is_fee_schedule": is_fee, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "tawtheeq-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "tawtheeq/regulation/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d اللائحة التنفيذية لنظام التوثيق" % n],
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
    json.dump({"law_key": "tawtheeq", "layer": "TAWTHEEQ_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "visually_adjudicated": src["stats"]["visually_adjudicated"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-tawtheeq-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "implementing_regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (31 سجلًّا؛ إصدار جديد كامل: 31 أصلية)",
               "title_en": "Implementing Regulation of the Saudi Notarization Law — Arabic LLM-ready layer (31 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 31], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Notarization Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
