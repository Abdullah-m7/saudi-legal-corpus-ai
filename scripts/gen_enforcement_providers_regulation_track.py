#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Regulation on Enforcement Service Providers (لائحة مقدمي خدمات التنفيذ).

Source: the official MOJ legal-portal text (Minister of Justice Decision 2268,
20/08/1443H, published 04/09/1443H), fetched article-by-article
(get-Section-Changes) and cross-verified against the official MOJ PDF. This
PDF's text layer uses a consistent per-line word-order-reversal RTL
extraction convention that caps automated similarity scoring below the 0.90
floor for every record (18/18 landed between 0.5973 and 0.786, mean 0.7476)
despite the underlying text being verbatim-correct; all 18 records were
therefore visually adjudicated verbatim against the rendered PDF pages
(200dpi, all 8 pages), including embedded anomalous characters. This
regulation is IN FORCE, implementing the Enforcement Law (نظام التنفيذ) and
its Implementing Regulation. Per its own article 18, it supersedes the prior
regulation issued under Ministerial Decision 11326 (14/5/1437H), which is not
ingested. FRESH FULL ISSUANCE: all 18 اصلية (0 معدلة / 0 ملغاة / 0 مضافة).
The section-API status equals the statuteStructure status for every article
(no dual-status divergence).

Articles are numbered by their ordinal position in the official statute
structure (1..18; no مكرر). number_label_ar preserves each article's
official label verbatim. DOCUMENTED SOURCE ANOMALIES (confirmed identically
in both official sources): (1) art 8's "وللوکیل" uses Persian keheh/farsi-yeh
instead of standard Arabic kaf/yeh; (2) art 9's "ترخيصه" is spelled
inconsistently within the same article (Farsi yeh then standard Arabic yeh);
(3) art 10 item 8 uses a Western ASCII digit "8." instead of the Eastern
Arabic-Indic "٨." used by the rest of that list; (4) art 15 item 2 uses the
Extended Arabic-Indic/Persian digit "۲" instead of standard "٢". All four
preserved verbatim, not corrected.

No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "enforcement_providers", "regulation", "official_source",
                   "enforcement_providers_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "enforcement_providers", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "enforcement_providers_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "enforcement_providers_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "enforcement_providers_arabic_legal_llm",
                        "enforcement_providers_regulation_legal_llm_001_018.json")

LAW_ID = "sa-enforcement-providers-regulation-1443"
LAW_AR = "لائحة مقدمي خدمات التنفيذ"
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
KEY_RE = r"enforcement_providers_art_(\d{3})$"
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
        ver.append({"law_key": "enforcement_providers", "law_component": "regulation", "language": "ar",
                    "record_layer": "ENFORCEMENT_PROVIDERS_REGULATION_ARABIC_VERIFIED_TEXT",
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
                                              "the official MOJ PDF (verbatim; the PDF text layer uses a "
                                              "per-line word-order-reversal RTL extraction convention that "
                                              "caps automated similarity scoring below the 0.90 floor for "
                                              "every record, so all records were confirmed verbatim by "
                                              "direct visual inspection of the rendered PDF pages)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "regulation", "article_number": n,
                    "is_mukarrar": False, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "enforcement-providers-regulation-llm-art-%03d" % n,
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "enforcement_providers/regulation/articles/%03d" % n,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d لائحة مقدمي خدمات التنفيذ" % n],
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
    json.dump({"law_key": "enforcement_providers", "layer": "ENFORCEMENT_PROVIDERS_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": False,
               "visually_adjudicated": src["stats"]["visually_adjudicated"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-enforcement-providers-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (18 مادة؛ إصدار جديد كامل: 18 أصلية)",
               "title_en": "Saudi Regulation on Enforcement Service Providers — Arabic LLM-ready layer (18 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 18], "text_status": STATUS,
               "consolidated_amended_law": False, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Regulation on Enforcement Service Providers records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
