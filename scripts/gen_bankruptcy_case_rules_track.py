#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Bankruptcy Case Rules track (القواعد المنظمة لإجراءات قضايا الإفلاس).

Source: the official MOJ legal-portal consolidated text of the Rules Organizing
Bankruptcy Case Procedures before the Commercial Courts (Minister of Justice
Decision No. 6421, published 9/4/1441H), fetched article-by-article
(get-Section-Changes) and cross-verified against the official MOJ PDF (24/24
MATCHES_PDF outright, mean 0.960, min 0.912; no article required visual
adjudication). This is a FRESH full issuance IN FORCE: 24 اصلية / 0 معدلة /
0 ملغاة / 0 مضافة. The section-API status equals the statuteStructure/PDF status
for every article (no dual-status divergence). Every record carries
legal_status_ar plus is_repealed/is_amended/is_added flags. Arabic governs; no
translation/paraphrase/interpretation. Read-only over input; deterministic over
outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "bankruptcy", "case_rules", "official_source",
                   "bankruptcy_case_rules_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "bankruptcy", "case_rules", "verified")
RECORDS = os.path.join(OUT_VER, "bankruptcy_case_rules_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "bankruptcy_case_rules_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "bankruptcy_arabic_legal_llm",
                        "bankruptcy_case_rules_legal_llm_001_024.json")

LAW_ID = "sa-bankruptcy-case-rules-6421-1441"
LAW_AR = "القواعد المنظمة لإجراءات قضايا الإفلاس"
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
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    m = re.match(r"bankruptcy_rules_art_(\d{3})(_mukarrar)?$", key)
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
        m = re.match(r"bankruptcy_rules_art_(\d{3})(_mukarrar)?$", key)
        n, is_muk = int(m.group(1)), bool(m.group(2))
        suffix = "-mukarrar" if is_muk else ""
        ls = a.get("legal_status_ar")
        is_repealed = ls == "ملغاة"
        is_amended = ls == "معدلة"
        is_added = ls == "مضافة"
        text = a["text"]
        hist = a.get("history")
        ver.append({"law_key": "bankruptcy", "law_component": "case_procedure_rules", "language": "ar",
                    "record_layer": "BANKRUPTCY_CASE_RULES_ARABIC_VERIFIED_TEXT",
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
                    "governing_source_note": ("Arabic governs; official MOJ consolidated text "
                                              "cross-verified against the official MOJ PDF; "
                                              "amendment status flagged (see source artifact)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "case_procedure_rules", "article_number": n,
                    "is_mukarrar": is_muk, "article_key": key,
                    "article_title_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "legal_status_ar": ls, "is_repealed": is_repealed,
                    "is_amended": is_amended, "is_added": is_added,
                    "record_id": "bankruptcy-case-rules-llm-art-%03d%s" % (n, suffix),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s%s" % (LAW_AR, a["number_label_ar"],
                                                   " (ملغاة)" if is_repealed else ""),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, a["number_label_ar"]),
                    "article_path": "bankruptcy/case_rules/articles/%03d%s" % (n, suffix),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d قواعد إجراءات قضايا الإفلاس" % n],
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
    json.dump({"law_key": "bankruptcy", "layer": "BANKRUPTCY_CASE_RULES_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["status_counts"],
               "decree": src["decree"], "decree_date_hijri": src["decree_date_hijri"],
               "consolidated_amended_law": True,
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-bankruptcy-case-rules-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "case_procedure_rules",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (24 مادة؛ إصدار كامل: 24 أصلية)",
               "title_en": "Rules Organizing Bankruptcy Case Procedures before the Commercial Courts — Arabic LLM-ready layer (24 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 24], "text_status": STATUS,
               "consolidated_amended_law": True, "status_counts": src["status_counts"],
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Bankruptcy Case Rules records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
