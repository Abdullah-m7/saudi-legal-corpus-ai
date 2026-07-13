#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Municipal Real Estate Disposal Regulation track (لائحة التصرف بالعقارات البلدية).

Source: the official MOJ legal-portal text (High Order أمر سامي 40152, 29/6/1441H,
implementing the Municipal Real Estate Disposal Law M/64), fetched
article-by-article (get-Section-Changes) and cross-verified against the official
MOJ PDF (31/35 MATCHES_PDF outright, mean 0.953; the 4 articles 6, 13, 14 and 33
had their PDF text-layer reorder/split clauses — every word present, zero missing
unigrams — and were adjudicated visually verbatim on the rendered pages). This
regulation is IN FORCE. CONSOLIDATED AMENDED: 31 اصلية / 3 معدلة (arts 10, 13, 21)
/ 0 ملغاة / 1 مضافة (art 13 مكرر); each amended/added article carries its full
version history. The section-API status equals the statuteStructure/PDF status for
every article (no dual-status divergence).

Articles are numbered by their ordinal position in the official statute structure
(1..34) plus one مكرر article (13 مكرر). number_label_ar preserves each article's
official label verbatim.
No legal text is altered. Arabic governs; no translation/paraphrase/
interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "municipal_realestate", "implementing_regulation", "official_source",
                   "municipal_realestate_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "municipal_realestate", "implementing_regulation", "verified")
RECORDS = os.path.join(OUT_VER, "municipal_realestate_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "municipal_realestate_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "municipal_realestate_arabic_legal_llm",
                        "municipal_realestate_regulation_legal_llm_001_035.json")

LAW_ID = "sa-municipal-realestate-regulation-40152-1441"
LAW_AR = "لائحة التصرف بالعقارات البلدية"
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
KEY_RE = r"municipal_realestate_reg_art_(\d{3})(_mukarrar)?$"
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
    m = re.match(KEY_RE, key)
    return (int(m.group(1)), 1 if m.group(2) else 0)


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        m = re.match(KEY_RE, key)
        n, is_muk = int(m.group(1)), bool(m.group(2))
        ls = a.get("legal_status_ar")
        text = a["text"]
        ver.append({"law_key": "municipal_realestate", "law_component": "implementing_regulation", "language": "ar",
                    "record_layer": "MUNICIPAL_REALESTATE_REG_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_muk, "article_key": key,
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
                                              "the official MOJ PDF (verbatim; low-similarity long articles "
                                              "adjudicated visually on the rendered pages)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "implementing_regulation", "article_number": n,
                    "is_mukarrar": is_muk, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": ls == "ملغاة",
                    "is_amended": ls == "معدلة", "is_added": ls == "مضافة",
                    "record_id": "municipal-realestate-reg-llm-art-%03d%s" % (n, "-mukarrar" if is_muk else ""),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s" % (LAW_AR, a["number_label_ar"]),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "municipal_realestate/implementing_regulation/articles/%03d%s" % (n, "_mukarrar" if is_muk else ""),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d لائحة التصرف بالعقارات البلدية" % n],
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
    json.dump({"law_key": "municipal_realestate", "layer": "MUNICIPAL_REALESTATE_REG_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "visually_adjudicated": src["stats"]["visually_adjudicated"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-municipal-realestate-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "implementing_regulation",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (35 مادة؛ 31 أصلية / 3 معدلة / 1 مضافة)",
               "title_en": "Saudi Municipal Real Estate Disposal Regulation — Arabic LLM-ready layer (35 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 34], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Municipal Real Estate Disposal Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
