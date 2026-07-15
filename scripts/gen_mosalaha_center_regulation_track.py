#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Regulation of the Conciliation Center (تنظيم مركز المصالحة).

Source: the official MOJ legal-portal text (Council of Ministers Decision
103, 08/04/1434H, published in Umm Al-Qura 02/06/1434H), fetched
article-by-article (get-Section-Changes, 0 divergences from statuteStructure)
and cross-verified against the official MOJ PDF. This PDF's text layer
exhibits the known RTL/ligature extraction artifact seen elsewhere in this
corpus (raw text-layer channels score low), but the 300dpi tesseract-ara OCR
channel is clean and all 10 articles matched the >=0.90 floor outright (mean
0.9897, min 0.968); all 10 were additionally read in full against the
rendered PDF pages as a direct visual cross-check. This regulation is IN
FORCE. FRESH FULL ISSUANCE: all 10 اصلية (0 معدلة / 0 ملغاة / 0 مضافة).

This is the Conciliation Center's constitutive/establishing regulation
(creation of the center, its director-general's duties, confidentiality) —
a companion to the already-ingested سources/muslaha/regulation/ track (26
articles, Minister of Justice Decision 5595, the operational rules for
conciliation offices issued in implementation of this regulation's own
article 9). Kept as a fully separate track (law_key mosalaha_center, not
muslaha); the sibling track's files are untouched.

Articles are numbered by their ordinal position (1..10; no مكرر), flat
structure with no chapter/section wrapper (section_ar empty for every
article). DOCUMENTED SOURCE ANOMALY: article 1 item 2 ("الوزارة") reads
"الوزارة: ىوزارة العدل." — an anomalous character precedes "وزارة العدل"
where "الوزارة: وزارة العدل." would be grammatically expected. Confirmed
present independently in both the portal DB text and the rendered official
PDF glyphs (different anomalous characters in each channel, corroborating a
genuine typo in the original 1434H decree rather than an extraction
artifact) — preserved verbatim, not corrected.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "mosalaha_center", "regulation", "official_source",
                   "mosalaha_center_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "mosalaha_center", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "mosalaha_center_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "mosalaha_center_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "mosalaha_center_arabic_legal_llm",
                        "mosalaha_center_regulation_legal_llm_001_010.json")

LAW_ID = "sa-mosalaha-center-regulation-1434"
LAW_AR = "تنظيم مركز المصالحة"
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
KEY_RE = r"mosalaha_center_art_(\d{3})$"
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
        ver.append({"law_key": "mosalaha_center", "law_component": "regulation", "language": "ar",
                    "record_layer": "MOSALAHA_CENTER_REGULATION_ARABIC_VERIFIED_TEXT",
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
                                              "against the official MOJ PDF (verbatim; matched outright "
                                              "via 300dpi tesseract-ara OCR channel, the PDF text layer's "
                                              "RTL/ligature extraction artifact making the raw text-layer "
                                              "channels score low, consistent with other tracks in this "
                                              "corpus; all 10 articles additionally read in full against "
                                              "the rendered PDF page images as a direct visual "
                                              "cross-check)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "mosalaha-center-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "mosalaha_center/regulation/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d تنظيم مركز المصالحة" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Council of Ministers / مجلس الوزراء — official legal portal (laws.moj.gov.sa)",
                                     "source_authority_ar": "مجلس الوزراء — المنصة القانونية الرسمية",
                                     "source_status": "moj_portal_api_cross_checked_official_pdf",
                                     "source_document_ar": LAW_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "mosalaha_center", "layer": "MOSALAHA_CENTER_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "visually_adjudicated": src["stats"]["visually_adjudicated"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-mosalaha-center-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (10 مواد؛ إصدار جديد كامل: 10 أصلية)",
               "title_en": "Saudi Regulation of the Conciliation Center — Arabic LLM-ready layer (10 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 10], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Regulation of the Conciliation Center records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
