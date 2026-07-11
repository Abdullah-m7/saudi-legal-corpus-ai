#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Labor Annex 2 track (workplace accessibility arrangements).

Source: annex 2 of the official HRSD Labor implementing-regulation PDF —
جدول الترتيبات والخدمات التيسيرية في بيئة العمل للعمال ذوي الإعاقات: 8 tables
/ 40 rows across 6 disability sections, recovered from the PDF's own
structure-tree /ActualText (the table pages are raster images) and verified
row-by-row against OCR and the rendered page images (see the source
artifact). Emits one LLM-ready record per table as a deterministic mechanical
linearization — every cell verbatim, separators only. Arabic governs; no
translation, paraphrase, or legal interpretation. Read-only over input;
deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "labor", "annex2", "official_source",
                   "labor_annex2_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "labor", "annex2", "verified")
RECORDS = os.path.join(OUT_VER, "labor_annex2_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "labor_annex2_verified_summary.json")
LLM_PATH = os.path.join(ROOT, "data", "labor_arabic_legal_llm",
                        "labor_annex2_accessibility_tables_llm.json")

LAW_ID = "sa-labor-accessibility-arrangements"
DOC_AR = "جدول الترتيبات والخدمات التيسيرية في بيئة العمل للعمال ذوي الإعاقة"
STATUS = "HRSD_OFFICIAL_PDF_ACTUALTEXT_OCR_IMAGE_CROSS_CHECKED"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي حالة").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [DOC_AR]


def _table_text(t):
    """Deterministic mechanical linearization: every cell verbatim."""
    cols = t["columns"]
    lines = [t["section_ar"] + ((" — " + t["sub_section_ar"]) if t.get("sub_section_ar") else "")]
    for row in t["rows"]:
        lines.append(" | ".join("%s: %s" % (cols[i], row[i]) for i in range(len(cols))
                                if str(row[i]).strip()))
    return "\n".join(lines)


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    tables = src["tables"]
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_PATH), exist_ok=True)

    ver, llm = [], []
    for i, t in enumerate(tables, start=1):
        text = _table_text(t)
        key = "labor_annex2_table_%d" % i
        label = t["section_ar"] + ((" — " + t["sub_section_ar"]) if t.get("sub_section_ar") else "")
        ver.append({"law_key": "labor", "law_component": "accessibility_arrangements",
                    "language": "ar",
                    "record_layer": "LABOR_ANNEX2_ACCESSIBILITY_TABLE_VERIFIED",
                    "article_number": i, "article_key": key,
                    "number_label_ar": label,
                    "article_text_verified": text,
                    "verification_status": "ACTIVE",
                    "row_count": len(t["rows"]),
                    "table_linearization_note": ("Mechanical linearization of the printed table: "
                                                 "every cell verbatim; only column labels and "
                                                 "separators added."),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; recovered from the PDF's own "
                                              "/ActualText and verified against OCR and the "
                                              "rendered page images (see source artifact)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm.append({"law_id": LAW_ID, "law_component": "accessibility_arrangements",
                    "article_number": i, "article_key": key,
                    "article_title_ar": label,
                    "record_id": "labor-annex2-llm-table-%d" % i,
                    "record_type": "verified_arabic_table", "language": "ar",
                    "governing_text_language": "ar", "article_text_ar": text,
                    "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "row_count": len(t["rows"]),
                    "llm_title_ar": "%s — %s" % (DOC_AR, label),
                    "retrieval_title_ar": "%s - جدول %d" % (DOC_AR, i),
                    "article_path": "labor/annex2/tables/%d" % i,
                    "keywords_ar": _kw(text),
                    "search_queries_ar": ["الترتيبات التيسيرية في بيئة العمل لذوي الإعاقة",
                                          t["section_ar"].strip(" :"),
                                          "مواءمة بيئة العمل للعمال ذوي الإعاقة"],
                    "text_status": STATUS,
                    "source_trust": {"source_authority": "Ministry of Human Resources and Social Development (HRSD)",
                                     "source_authority_ar": "وزارة الموارد البشرية والتنمية الاجتماعية",
                                     "source_status": "hrsd_official_pdf_actualtext_ocr_image_cross_checked",
                                     "source_document_ar": DOC_AR,
                                     "verification_status": "ACTIVE"},
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "labor", "layer": "LABOR_ANNEX2_ACCESSIBILITY_TABLES_VERIFIED",
               "record_count": len(ver),
               "table_rows": sum(len(t["rows"]) for t in tables),
               "official_text_status": STATUS,
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-labor-annex2-accessibility-tables-legal-llm", "law_id": LAW_ID,
               "law_component": "accessibility_arrangements",
               "title_ar": DOC_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (8 جداول، 40 صفًّا)",
               "title_en": "Workplace accessibility arrangements tables (Labor Annex 2) — Arabic LLM-ready layer (8 records)",
               "record_type": "verified_arabic_table", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm),
               "text_status": STATUS,
               "not_legal_advice": True, "records": llm},
              open(LLM_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified + %d LLM-ready Labor Annex 2 table records" % (len(ver), len(llm)))


if __name__ == "__main__":
    main()
