#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Unified Model Work Organization Regulation track (Labor Annex 1).

Source: annex 1 of the official HRSD PDF (اللائحة التنفيذية لنظام العمل
وملحقاتها) — the Ministry's model bylaw adopted by regulation article (3).
72 articles (all active, OCR-verified >= 0.93) + the 3 violation/penalty
tables (50 rows, every cell checked against the rendered page images).
Emits two LLM-ready layers: the articles layer (72 records) and the
violation-tables layer (3 records whose text is a deterministic mechanical
linearization of the printed table — every cell verbatim, separators only).
Arabic governs; no translation, paraphrase, or legal interpretation.
Read-only over input; deterministic over outputs.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "labor", "annex1", "official_source",
                   "labor_annex1_official_source.json")
OUT_VER = os.path.join(ROOT, "sources", "labor", "annex1", "verified")
RECORDS = os.path.join(OUT_VER, "labor_annex1_verified_records.jsonl")
SUMMARY = os.path.join(OUT_VER, "labor_annex1_verified_summary.json")
LLM_ART = os.path.join(ROOT, "data", "labor_arabic_legal_llm",
                       "labor_annex1_legal_llm_001_072.json")
LLM_TAB = os.path.join(ROOT, "data", "labor_arabic_legal_llm",
                       "labor_annex1_violation_tables_llm.json")

LAW_ID = "sa-labor-model-work-regulation"
DOC_AR = "النموذج الموحد للائحة تنظيم العمل"
STATUS = "HRSD_OFFICIAL_PDF_OCR_IMAGE_CROSS_CHECKED"
STOP = set(("من في على عن إلى أو و أن التي الذي ما غير قبل بعد عند لدى هذه هذا به بها لها له أي كل "
            "ذلك تلك ذات ذوات بأي بما فيها فيه مع ومن وأي وفي وعلى أما إذا كان كانت يكون تكون وقد قد "
            "لا إلا بين حسب وفق وفقا بحسب فإن وإن المادة النظام اللائحة أحكام يجب يجوز عليه دون فيما "
            "منه منها وإذا حال وله ولها الآتية يأتي يلي مرة").split())


def _kw(text, k=6):
    freq, order = {}, []
    for w in re.sub(r"[^ء-ي]+", " ", text).split():
        if len(w) >= 3 and w not in STOP:
            if w not in freq:
                order.append(w)
            freq[w] = freq.get(w, 0) + 1
    return sorted(order, key=lambda w: (-freq[w], order.index(w)))[:k] or [DOC_AR]


def _table_text(t):
    """Deterministic mechanical linearization of a printed penalty table.

    Every cell verbatim from the source artifact; only labels/separators added.
    """
    cols = t["columns"]  # م, نوع المخالفة, أول مرة, ثاني مرة, ثالث مرة, رابع مرة
    notes = t.get("row_notes", {})
    lines = [t["section_ar"]]
    for row in t["rows"]:
        cells = ["%s: %s" % (cols[i], row[i]) for i in range(len(cols)) if str(row[i]).strip()]
        line = " | ".join(cells)
        note = notes.get(str(row[0]))
        if note:
            line += " | " + note
        lines.append(line)
    return "\n".join(lines)


def main():
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    tables = src["violation_tables"]
    os.makedirs(OUT_VER, exist_ok=True)
    os.makedirs(os.path.dirname(LLM_ART), exist_ok=True)

    ver, llm_a, llm_t = [], [], []
    for key in sorted(arts, key=lambda k: int(re.match(r"labor_annex1_art_(\d{3})", k).group(1))):
        a = arts[key]
        n = int(re.match(r"labor_annex1_art_(\d{3})", key).group(1))
        text = a["text"]
        ver.append({"law_key": "labor", "law_component": "model_work_regulation",
                    "language": "ar",
                    "record_layer": "LABOR_ANNEX1_ARABIC_VERIFIED_TEXT",
                    "article_number": n, "article_key": key,
                    "number_label_ar": a["number_label_ar"],
                    "section_ar": a.get("section_ar", ""),
                    "article_text_verified": text,
                    "verification_status": a["status"],
                    "ocr_similarity": a.get("ocr_similarity"),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; annex 1 of the official HRSD PDF, "
                                              "verified against rendered-page OCR (see source "
                                              "artifact)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm_a.append({"law_id": LAW_ID, "law_component": "model_work_regulation",
                      "article_number": n, "article_key": key,
                      "article_title_ar": a["number_label_ar"],
                      "section_ar": a.get("section_ar", ""),
                      "record_id": "labor-annex1-llm-art-%03d" % n,
                      "record_type": "verified_arabic_article", "language": "ar",
                      "governing_text_language": "ar", "article_text_ar": text,
                      "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                      "llm_title_ar": "%s — %s (%s)" % (DOC_AR, a["number_label_ar"],
                                                        a.get("section_ar", "")),
                      "retrieval_title_ar": "%s - %s" % (DOC_AR, a["number_label_ar"]),
                      "article_path": "labor/annex1/articles/%03d" % n,
                      "keywords_ar": _kw(text),
                      "search_queries_ar": ["المادة %d %s" % (n, DOC_AR),
                                            "%s المادة %d" % (DOC_AR, n),
                                            "المادة %d من لائحة تنظيم العمل النموذجية" % n],
                      "text_status": STATUS,
                      "source_trust": {"source_authority": "Ministry of Human Resources and Social Development (HRSD)",
                                       "source_authority_ar": "وزارة الموارد البشرية والتنمية الاجتماعية",
                                       "source_status": "hrsd_official_pdf_ocr_image_cross_checked",
                                       "source_document_ar": DOC_AR,
                                       "verification_status": a["status"]},
                      "translation_performed": False, "legal_interpretation_performed": False,
                      "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    for i, t in enumerate(tables, start=1):
        text = _table_text(t)
        key = "labor_annex1_violation_table_%d" % i
        ver.append({"law_key": "labor", "law_component": "model_work_regulation",
                    "language": "ar",
                    "record_layer": "LABOR_ANNEX1_VIOLATION_TABLE_VERIFIED",
                    "article_number": i, "article_key": key,
                    "number_label_ar": t["section_ar"],
                    "section_ar": "جداول المخالفات والجزاءات",
                    "article_text_verified": text,
                    "verification_status": "ACTIVE",
                    "row_count": len(t["rows"]),
                    "table_linearization_note": ("Mechanical linearization of the printed table: "
                                                 "every cell verbatim; only column labels and "
                                                 "separators added."),
                    "official_text_status": STATUS,
                    "governing_source_note": ("Arabic governs; every row checked against the "
                                              "rendered page images (see source artifact)."),
                    "translation_performed": False, "legal_interpretation_performed": False,
                    "summarized_or_paraphrased": False, "english_used_for_correction": False})
        llm_t.append({"law_id": LAW_ID, "law_component": "model_work_regulation",
                      "article_number": i, "article_key": key,
                      "article_title_ar": t["section_ar"],
                      "section_ar": "جداول المخالفات والجزاءات",
                      "record_id": "labor-annex1-llm-violation-table-%d" % i,
                      "record_type": "verified_arabic_table", "language": "ar",
                      "governing_text_language": "ar", "article_text_ar": text,
                      "article_text_hash_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                      "row_count": len(t["rows"]),
                      "llm_title_ar": "%s — جدول المخالفات والجزاءات — %s" % (DOC_AR, t["section_ar"]),
                      "retrieval_title_ar": "%s - جدول المخالفات والجزاءات %d" % (DOC_AR, i),
                      "article_path": "labor/annex1/violation_tables/%d" % i,
                      "keywords_ar": _kw(text),
                      "search_queries_ar": ["جدول المخالفات والجزاءات لائحة تنظيم العمل",
                                            t["section_ar"].strip(" :"),
                                            "جزاءات المخالفات في لائحة تنظيم العمل النموذجية"],
                      "text_status": STATUS,
                      "source_trust": {"source_authority": "Ministry of Human Resources and Social Development (HRSD)",
                                       "source_authority_ar": "وزارة الموارد البشرية والتنمية الاجتماعية",
                                       "source_status": "hrsd_official_pdf_ocr_image_cross_checked",
                                       "source_document_ar": DOC_AR,
                                       "verification_status": "ACTIVE"},
                      "translation_performed": False, "legal_interpretation_performed": False,
                      "english_used_for_correction": False, "text_summarized_or_paraphrased": False})

    with open(RECORDS, "w", encoding="utf-8") as f:
        for r in ver:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump({"law_key": "labor", "layer": "LABOR_ANNEX1_ARABIC_VERIFIED_TEXT",
               "record_count": len(ver), "articles": len(llm_a),
               "violation_tables": len(llm_t),
               "violation_table_rows": sum(len(t["rows"]) for t in tables),
               "official_text_status": STATUS,
               "source_artifact": os.path.relpath(SRC, ROOT)},
              open(SUMMARY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump({"layer_id": "sa-labor-annex1-arabic-legal-llm-full", "law_id": LAW_ID,
               "law_component": "model_work_regulation",
               "title_ar": DOC_AR + " — الطبقة العربية الجاهزة للنماذج اللغوية (72 مادة)",
               "title_en": "Unified Model Work Organization Regulation — Arabic LLM-ready layer (72 records)",
               "record_type": "verified_arabic_article", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm_a),
               "article_range": [1, 72], "text_status": STATUS,
               "not_legal_advice": True, "records": llm_a},
              open(LLM_ART, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"layer_id": "sa-labor-annex1-violation-tables-legal-llm", "law_id": LAW_ID,
               "law_component": "model_work_regulation",
               "title_ar": DOC_AR + " — جداول المخالفات والجزاءات (3 جداول، 50 صفًّا)",
               "title_en": "Unified Model Work Organization Regulation — violation/penalty tables (3 tables, 50 rows)",
               "record_type": "verified_arabic_table", "language": "ar",
               "governing_text_language": "ar", "record_count": len(llm_t),
               "text_status": STATUS,
               "not_legal_advice": True, "records": llm_t},
              open(LLM_TAB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Wrote %d verified (72 articles + %d tables) + LLM layers" % (len(ver), len(llm_t)))


if __name__ == "__main__":
    main()
