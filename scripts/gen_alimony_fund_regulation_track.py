#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Alimony Fund Regulation (تنظيم صندوق النفقة).

Source: the official MOJ legal-portal text (Council of Ministers Decision
679, 15/11/1438H, published 03/12/1438H), fetched article-by-article
(get-Section-Changes) and cross-verified against the official MOJ PDF. This
PDF's text layer exhibits the known RTL/ligature extraction-artifact family
seen elsewhere in this corpus (per-line word order and a few ligature glyph
substitutions), which caps automated similarity scoring below the 0.90 floor
for 10 of 17 records (mean 0.7767, min 0.3987) despite the underlying text
being verbatim-correct; those 10 records were visually adjudicated against
the rendered PDF pages, and all 17 were visually read in full. This
regulation is IN FORCE. NOTE ON ISSUING AUTHORITY: although classified under
"القضاء" on the MOJ portal and the Fund is administratively linked to the
Minister of Justice (art 2), the Regulation itself was issued directly by a
Council of Ministers Decision, not a Minister of Justice decision — the Fund
is a semi-independent body with its own legal personality and budget. FRESH
FULL ISSUANCE: all 17 اصلية (0 معدلة / 0 ملغاة / 0 مضافة); no prior version
exists. The section-API status equals the statuteStructure status for every
article (no dual-status divergence).

Articles are numbered by their ordinal position in the official statute
structure (1..17; no مكرر), flat structure with no chapter/section wrapper
(section_ar empty for every article). number_label_ar preserves each
article's official label verbatim. No legal text is altered. Arabic governs;
no translation/paraphrase/interpretation. Read-only over input; deterministic
over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "alimony_fund", "regulation", "official_source",
                   "alimony_fund_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "alimony_fund", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "alimony_fund_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "alimony_fund_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "alimony_fund_arabic_legal_llm",
                        "alimony_fund_regulation_legal_llm_001_017.json")

LAW_ID = "sa-alimony-fund-regulation-1438"
LAW_AR = "تنظيم صندوق النفقة"
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
KEY_RE = r"alimony_fund_art_(\d{3})$"
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
        ver.append({"law_key": "alimony_fund", "law_component": "regulation", "language": "ar",
                    "record_layer": "ALIMONY_FUND_REGULATION_ARABIC_VERIFIED_TEXT",
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
                                              "against the official MOJ PDF (verbatim; the PDF text "
                                              "layer's RTL/ligature extraction artifact caps automated "
                                              "similarity scoring below the 0.90 floor for 10 of 17 "
                                              "records, so those were confirmed verbatim by direct visual "
                                              "inspection of the rendered PDF pages; the remaining 7 "
                                              "scored >=0.90 automatically and were also visually "
                                              "spot-checked)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "alimony-fund-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "alimony_fund/regulation/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d تنظيم صندوق النفقة" % n],
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
    json.dump({"law_key": "alimony_fund", "layer": "ALIMONY_FUND_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "visually_adjudicated": src["stats"]["visually_adjudicated"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-alimony-fund-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (17 مادة؛ إصدار جديد كامل: 17 أصلية)",
               "title_en": "Saudi Alimony Fund Regulation — Arabic LLM-ready layer (17 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 17], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Alimony Fund Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
