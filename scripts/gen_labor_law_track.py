#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Labor Law (نظام العمل م/51) track outputs.

Source: the official Ministry of Human Resources consolidated Labor Law PDF
(all amendment decrees merged, latest م/44), extracted article-by-article and
cross-verified against the repository's independently captured BOE official
base texts (worksheets/labor_law): 142 articles match the BOE base verbatim
(two official sources), 65 differ exactly where the amendment tracking says
they were amended (official amended wording), 38 are officially deleted
placeholders in the ministry PDF itself, 4 are مكرر articles — and ZERO
differences are unexplained. Emits verified records (249) and the Arabic
LLM-ready layer. Deleted articles are flagged and carry the placeholder as
printed. Arabic governs; no translation/paraphrase/interpretation.
Read-only over input; deterministic/idempotent over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "labor", "law", "official_source",
                   "labor_law_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "labor", "law", "verified")
RECORDS = os.path.join(OUT_VER, "labor_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "labor_law_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "labor_arabic_legal_llm",
                        "labor_law_legal_llm_001_245.json")

LAW_ID = "sa-labor-law-m51-1426"
LAW_AR = "نظام العمل"
STATUS = "HRSD_CONSOLIDATED_CROSS_CHECKED_BOE"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [LAW_AR]


def _sort_key(key):
    m = re.match(r"labor_law_art_(\d{3})(_mukarrar)?$", key)
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
        m = re.match(r"labor_law_art_(\d{3})(_mukarrar)?$", key)
        n, is_muk = int(m.group(1)), bool(m.group(2))
        suffix = "-mukarrar" if is_muk else ""
        label = a["number_label_ar"] + (" مكرر" if is_muk and "مكرر" not in a["number_label_ar"] else "")
        deleted = a["status"] == "DELETED"
        text = a["text"]
        ver.append({"law_key": "labor", "law_component": "law", "language": "ar",
                    "record_layer": "LABOR_LAW_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_muk, "is_deleted": deleted,
                    "article_key": key, "number_label_ar": label,
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "boe_similarity": a.get("boe_similarity"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; official HRSD consolidated text "
                                              "cross-verified against independent BOE captures "
                                              "(see source artifact)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "law", "article_number": n,
                    "is_mukarrar": is_muk, "is_deleted": deleted, "article_key": key,
                    "article_title_ar": label,
                    "record_id": "labor-law-llm-art-%03d%s" % (n, suffix),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "llm_title_ar": "%s — %s%s" % (LAW_AR, label, " (ملغاة)" if deleted else ""),
                    "retrieval_title_ar": "%s - %s" % (LAW_AR, label),
                    "article_path": "labor/law/articles/%03d%s" % (n, suffix),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, LAW_AR),
                                          "%s المادة %d" % (LAW_AR, n),
                                          "المادة %d نظام العمل السعودي" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Ministry of Human Resources and Social Development (HRSD)",
                                     "source_authority_ar": "وزارة الموارد البشرية والتنمية الاجتماعية",
                                     "source_status": "hrsd_consolidated_cross_checked_boe",
                                     "source_document_ar": LAW_AR,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "labor", "layer": "LABOR_LAW_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["stats"]["status_counts"],
               "deleted_article_numbers": src["stats"]["deleted_article_numbers"],
               "mukarrar_articles": src["stats"]["mukarrar_articles"],
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-labor-law-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "law",
               "title_ar": LAW_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (249 سجلًّا: 245 مادة + 4 مكرر؛ منها 38 ملغاة)",
               "title_en": "Saudi Labor Law — Arabic LLM-ready layer (249 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 245], "text_status": STATUS,
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Labor Law records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
