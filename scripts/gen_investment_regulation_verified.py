#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the verified Arabic text records for the Investment Law Implementing
Regulations (37 articles).

Source: the official Ministry of Investment (MISA) Arabic Implementing
Regulations PDF (``inputs/investment_official_pdfs/investment_regulation_misa_ar.pdf``).
The PDF's designed font corrupts direct text extraction, so the Arabic was
produced by rendering each page and Arabic-OCR'ing it, then correcting the OCR
verbatim against the rendered images and cross-checking article boundaries/titles
against the official English edition of the same regulation.  That verified
transcription lives, with provenance, in
``investment_regulation_official_misa_source.json``; this generator emits
per-article records from it.

Arabic is the governing source.  No translation, paraphrase, or interpretation.

Read-only over its input; deterministic and idempotent over its output.
"""

from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "sources", "investment", "regulation", "official_source",
                      "investment_regulation_official_misa_source.json")
OUT_DIR = os.path.join(ROOT, "sources", "investment", "regulation", "verified")
RECORDS = os.path.join(OUT_DIR, "investment_regulation_verified_records.jsonl")
SUMMARY = os.path.join(OUT_DIR, "investment_regulation_verified_summary.json")

EXPECTED = 37


def build_records():
    src = json.load(open(SOURCE, encoding="utf-8"))
    arts = src["articles"]
    records = []
    for n in range(1, EXPECTED + 1):
        a = arts[str(n)]
        records.append({
            "law_key": "investment",
            "law_component": "implementing_regulation",
            "language": "ar",
            "record_layer": "INVESTMENT_REGULATION_ARABIC_VERIFIED_TEXT",
            "article_number": n,
            "article_key": "investment_reg_art_%03d" % n,
            "arabic_title": a["title_ar"],
            "article_text_verified": a["text_ar"],
            "official_text_status": "VERIFIED_TRANSCRIBED_FROM_OFFICIAL_MISA_PDF",
            "verification_method": (
                "Arabic-OCR of the rendered official MISA Arabic PDF, corrected verbatim "
                "against the rendered page images; article boundaries/titles cross-checked "
                "against the official English edition."
            ),
            "source_authority_ar": src["source_authority_ar"],
            "source_pdf_sha256": src["source_pdf_sha256"],
            "governing_source_note": (
                "Arabic is the governing source. article_text_verified is the official MISA "
                "Investment Implementing Regulations text."
            ),
            "translation_performed": False,
            "legal_interpretation_performed": False,
            "summarized_or_paraphrased": False,
            "english_used_for_correction": False,
        })
    return records


def main():
    records = build_records()
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(RECORDS, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    summary = {
        "law_key": "investment",
        "law_component": "implementing_regulation",
        "layer": "INVESTMENT_REGULATION_ARABIC_VERIFIED_TEXT",
        "title_ar": "اللائحة التنفيذية لنظام الاستثمار",
        "record_count": len(records),
        "article_number_range": [1, EXPECTED],
        "official_text_status": "VERIFIED_TRANSCRIBED_FROM_OFFICIAL_MISA_PDF",
        "source_artifact": os.path.relpath(SOURCE, ROOT),
        "source_pdf": "inputs/investment_official_pdfs/investment_regulation_misa_ar.pdf",
        "boundaries": {
            "arabic_governs": True,
            "translation_performed": False,
            "legal_interpretation_performed": False,
            "summarized_or_paraphrased": False,
            "english_used_for_correction": False,
        },
        "recommended_next_stage": "INVESTMENT_REGULATION_ARABIC_LEGAL_LLM",
    }
    with open(SUMMARY, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Wrote %d verified investment-regulation records -> %s"
          % (len(records), os.path.relpath(RECORDS, ROOT)))


if __name__ == "__main__":
    main()
