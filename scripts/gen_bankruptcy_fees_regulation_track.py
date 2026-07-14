#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Rules for Determining the Fees of Experts and Trustees under
the Bankruptcy Law (قواعد تحديد أتعاب الخبراء والأمناء في نظام الإفلاس).

Source: the official MOJ legal-portal text (Minister of Justice Decision 2514,
02/08/1442H, published 27/08/1442H), fetched article-by-article
(get-Section-Changes) and cross-verified against the official MOJ PDF. This
PDF's text layer mixes inconsistent RTL extraction conventions (per-line
word-order reversal for most runs, full character-order reversal for others
within the same block) and the OCR channel misreads embedded Hindi-Arabic
numerals, so only 6/20 records matched the automated >=0.90 similarity floor
outright (arts 4, 7, 10, 11, 12, 17); the other 14 (arts 1,2,3,5,6,8,9,
13,14,15,16 + all 3 fee-schedule tables) were visually adjudicated verbatim
against the rendered PDF pages (mean 0.8217, min 0.5822). This regulation is
IN FORCE, implementing the Bankruptcy Law (Royal Decree M/50, 28/05/1439H).
FRESH FULL ISSUANCE: all 20 اصلية (0 معدلة / 0 ملغاة / 0 مضافة). The
section-API status equals the statuteStructure/PDF status for every record
(no dual-status divergence).

20 records = 17 numbered articles (1..17, no مكرر) + 3 appendix fee-schedule
tables (arts 18-20, flagged is_fee_schedule=True, already linearized as plain
text in the source layer). number_label_ar preserves each record's official
label verbatim, including two documented anomalies: (1) the three tables'
labels are formatted inconsistently ("الجدول رقم(١)" / "الجدول رقم (٢)" /
"جدول رقم (٣)"); (2) inside art 19 (شرائح الديون), the second sub-table's
header cell literally reads "الأصول" instead of "الديون" — a genuine
copy-paste error in the source document, confirmed in both official sources
and preserved verbatim.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "bankruptcy_fees", "regulation", "official_source",
                   "bankruptcy_fees_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "bankruptcy_fees", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "bankruptcy_fees_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "bankruptcy_fees_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "bankruptcy_fees_arabic_legal_llm",
                        "bankruptcy_fees_regulation_legal_llm_001_020.json")

LAW_ID = "sa-bankruptcy-fees-regulation-1442"
LAW_AR = "قواعد تحديد أتعاب الخبراء والأمناء في نظام الإفلاس"
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
KEY_RE = r"bankruptcy_fees_art_(\d{3})$"
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
        is_fee = bool(a.get("is_fee_schedule"))
        ver_rec = {"law_key": "bankruptcy_fees", "law_component": "regulation", "language": "ar",
                   "record_layer": "BANKRUPTCY_FEES_REGULATION_ARABIC_VERIFIED_TEXT",
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
                   "governing_source_note": ("Arabic governs; official MOJ text cross-verified against "
                                             "the official MOJ PDF (verbatim; the PDF text layer mixes "
                                             "inconsistent RTL extraction conventions and the OCR channel "
                                             "misreads embedded numerals, so most records were confirmed "
                                             "verbatim by direct visual inspection of the rendered PDF "
                                             "pages rather than automated similarity scoring alone)."),
                   "translation_performed": False, "legal_interpretation_performed": False,
                   "summarized_or_paraphrased": False, "english_used_for_correction": False}
        if is_fee:
            ver_rec["is_fee_schedule"] = True
        ver.append(ver_rec)

        llm_rec = {"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                   "is_mukarrar": False, "article_key": key,
                   "article_title_ar": a["number_label_ar"],
                   "section_ar": a.get("section_ar", ""),
                   "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                   "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                   "record_id": "bankruptcy-fees-regulation-llm-art-%03d" % n,
                   "record_type": "verified_arabic_article", "language": "ar",
                   "governing_text_language": "ar", "article_text_ar": text,
                   "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                   "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                   "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                   "article_path": "bankruptcy_fees/regulation/articles/%03d" % n,
                   "keywords_ar": _kw(text),
                   "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                         "%s المادة %d" % (LAW_AR, n),
                                         "المادة %d قواعد تحديد أتعاب الخبراء والأمناء في نظام الإفلاس" % n],
                   "text_status": STATUS,
                   "source_trust": {"source_authority": "Ministry of Justice (MOJ) — official legal portal",
                                    "source_authority_ar": "وزارة العدل — المنصة القانونية الرسمية",
                                    "source_status": "moj_portal_api_cross_checked_official_pdf",
                                    "source_document_ar": LAW_AR,
                                    "legal_status_ar": ls,
                                    "verification_status": a["status"]},
                   "translation_performed": False, "legal_interpretation_performed": False,
                   "english_used_for_correction": False, "text_summarized_or_paraphrased": False}
        if is_fee:
            llm_rec["is_fee_schedule"] = True
        llm.append(llm_rec)

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "bankruptcy_fees", "layer": "BANKRUPTCY_FEES_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "visually_adjudicated": src["stats"]["visually_adjudicated"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-bankruptcy-fees-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (20 سجلاً؛ إصدار جديد كامل: 20 أصلية)",
               "title_en": "Saudi Rules for Determining the Fees of Experts and Trustees under the Bankruptcy Law — Arabic LLM-ready layer (20 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 20], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Bankruptcy Fees Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
