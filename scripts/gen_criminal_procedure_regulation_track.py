#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Criminal Procedure implementing-regulation track.

Source: the official MOJ legal-portal consolidated text of the Implementing
Regulation of the Law of Criminal Procedure (Cabinet decision 142, 21/3/1436H),
fetched article-by-article and cross-verified against the official MOJ PDF
(181/181 MATCHES_PDF). This regulation is IN FORCE and lightly amended: 174
articles are اصلية and 7 are معدلة (arts 21, 71, 92, 93, 157, 163, 179, by
Cabinet decision 860), each carrying its amendment history; no articles are
repealed or added, and the section-API status equals the PDF status for every
article (no dual-status divergence). It uses sequential ordinal labels (1..181),
so it is keyed like a law. Every record carries legal_status_ar plus
is_repealed/is_amended/is_added flags. Arabic governs; no translation/
paraphrase/interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "criminal_procedure", "regulation", "official_source",
                   "criminal_procedure_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "criminal_procedure", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "criminal_procedure_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "criminal_procedure_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "criminal_procedure_arabic_legal_llm",
                        "criminal_procedure_regulation_legal_llm_001_181.json")

LAW_ID = "sa-criminal-procedure-regulation-142-1436"
REG_AR = "اللائحة التنفيذية لنظام الإجراءات الجزائية"
REG_SHORT_AR = "لائحة الإجراءات الجزائية"
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
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
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [REG_SHORT_AR]


def _sort_key(key):
    m = re.match(r"jza_reg_art_(\d{3})(_mukarrar)?$", key)
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
        m = re.match(r"jza_reg_art_(\d{3})(_mukarrar)?$", key)
        n, is_muk = int(m.group(1)), bool(m.group(2))
        suffix = "-mukarrar" if is_muk else ""
        ls = a.get("legal_status_ar")
        is_repealed = ls == "ملغاة"
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        text = a["text"]
        hist = a.get("history")
        ver.append({"law_key": "criminal_procedure", "law_component": "implementing_regulation",
                    "language": "ar",
                    "record_layer": "CRIMINAL_PROCEDURE_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_muk, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "legal_status_ar": ls,
                    "is_repealed": is_repealed, "is_amended": is_amended, "is_added": is_added,
                    "amendment_history": hist,
                    "pdf_similarity": a.get("pdf_similarity"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; official MOJ consolidated regulation "
                                              "cross-verified against the official MOJ PDF; "
                                              "amendment status flagged (see source artifact)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "implementing_regulation", "article_number": n,
                    "is_mukarrar": is_muk, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "criminal-procedure-regulation-llm-art-%03d%s" % (n, suffix),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s%s" % (REG_SHORT_AR, a["number_label_ar"],
                                                   " (ملغاة)" if is_repealed else ""),
                    "retrieval_title_ar": "%s - %s" % (REG_SHORT_AR, a["number_label_ar"]),
                    "article_path": "criminal_procedure/regulation/articles/%03d%s" % (n, suffix),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, REG_SHORT_AR),
                                          "%s المادة %d" % (REG_SHORT_AR, n),
                                          "المادة %d لائحة الإجراءات الجزائية" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Ministry of Justice (MOJ) — official legal portal",
                                     "source_authority_ar": "وزارة العدل — المنصة القانونية الرسمية",
                                     "source_status": "moj_portal_api_cross_checked_official_pdf",
                                     "source_document_ar": REG_AR,
                                     "legal_status_ar": ls,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "criminal_procedure",
               "layer": "CRIMINAL_PROCEDURE_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-criminal-procedure-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "implementing_regulation",
               "title_ar": REG_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (181 مادة؛ نص موحّد: 174 أصلية، 7 معدّلة)",
               "title_en": "Implementing Regulation of the Law of Criminal Procedure — Arabic LLM-ready layer (181 records, consolidated)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 181], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Criminal Procedure Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
