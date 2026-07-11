#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Labor Law Implementing Regulation (اللائحة التنفيذية لنظام العمل) track.

Source: the official HRSD PDF (اللائحة التنفيذية لنظام العمل وملحقاتها), core
regulation articles extracted from the text layer and verified two ways —
tesseract-ara OCR of the rendered pages (all active articles >= 0.91) and the
PDF's own verbatim Labor Law quotes cross-checked against the repository's
verified Labor Law track (all >= 0.95, 39/45 exact). 45 records: articles
(1)-(40) + 5 mukarrar; 3 officially deleted placeholders (2, 36, 37) flagged.
Each record carries implements_law_articles linking it to the Labor Law
articles it implements. The PDF's five annexes are NOT ingested here (see the
source artifact's scope_note). Arabic governs; no translation, paraphrase, or
legal interpretation. Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "labor", "regulation", "official_source",
                   "labor_regulation_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "labor", "regulation", "verified")
RECORDS = os.path.join(OUT_VER, "labor_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "labor_regulation_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "labor_arabic_legal_llm",
                        "labor_regulation_legal_llm_001_040.json")

LAW_ID = "sa-labor-implementing-regulation"
REG_AR = "اللائحة التنفيذية لنظام العمل"
STATUS = "HRSD_OFFICIAL_PDF_OCR_CROSS_CHECKED_LAW_QUOTES"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي تنفيذ").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [REG_AR]


def _sort_key(key):
    m = re.match(r"labor_reg_art_(\d{3})(?:_mukarrar(?:_(\d))?)?$", key)
    n = int(m.group(1))
    if "_mukarrar" not in key:
        return (n, 0)
    return (n, int(m.group(2)) if m.group(2) else 1)


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    keys = sorted(arts, key=_sort_key)
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for key in keys:
        a = arts[key]
        m = re.match(r"labor_reg_art_(\d{3})(_mukarrar(?:_\d)?)?$", key)
        n, is_muk = int(m.group(1)), bool(m.group(2))
        suffix = (m.group(2) or "").replace("_", "-")
        deleted = a["status"] == "DELETED"
        text = a["text"]
        implements = a.get("implements_law_articles", [])
        ver.append({"law_key": "labor", "law_component": "implementing_regulation",
                    "language": "ar",
                    "record_layer": "LABOR_REGULATION_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "is_mukarrar": is_muk, "is_deleted": deleted,
                    "article_key": key, "number_label_ar": a["number_label_ar"],
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "ocr_similarity": a.get("ocr_similarity"),
                    "implements_law_articles": implements,
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; official HRSD PDF text verified "
                                              "against rendered-page OCR and against the repo's "
                                              "verified Labor Law track via the PDF's own law "
                                              "quotes (see source artifact)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "implementing_regulation",
                    "article_number": n, "is_mukarrar": is_muk, "is_deleted": deleted,
                    "article_key": key, "article_title_ar": a["number_label_ar"],
                    "record_id": "labor-reg-llm-art-%03d%s" % (n, suffix),
                    "record_type": "verified_arabic_article", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "implements_law_articles": implements,
                    "llm_title_ar": "%s — %s%s" % (REG_AR, a["number_label_ar"],
                                                   " (ملغاة)" if deleted else ""),
                    "retrieval_title_ar": "%s - %s" % (REG_AR, a["number_label_ar"]),
                    "article_path": "labor/regulation/articles/%03d%s" % (n, suffix),
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["المادة %d %s" % (n, REG_AR),
                                          "%s المادة %d" % (REG_AR, n),
                                          "المادة %d من اللائحة التنفيذية لنظام العمل" % n],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Ministry of Human Resources and Social Development (HRSD)",
                                     "source_authority_ar": "وزارة الموارد البشرية والتنمية الاجتماعية",
                                     "source_status": "hrsd_official_pdf_ocr_cross_checked_law_quotes",
                                     "source_document_ar": REG_AR,
                                     "verification_status": a["status"]},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "labor", "layer": "LABOR_REGULATION_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "official_text_status": STATUS,
               "status_counts": src["stats"]["status_counts"],
               "deleted_article_numbers": src["stats"]["deleted_article_numbers"],
               "mukarrar_article_keys": [k for k in keys if "_mukarrar" in k],
               "annexes_not_ingested": True,
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-labor-regulation-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "implementing_regulation",
               "title_ar": REG_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (45 سجلًّا: المواد 1-40 + 5 مكرر؛ منها 3 ملغاة)",
               "title_en": "Saudi Labor Law Implementing Regulation — Arabic LLM-ready layer (45 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "article_range": [1, 40], "text_status": STATUS,
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Labor Regulation records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
