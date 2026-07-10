#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the verified Arabic text records for the Saudi Investment Law (16 articles).

Source: the official Ministry of Investment (MISA) bilingual Investment Law PDF
(``inputs/investment_official_pdfs/investment_law_misa.pdf``).  The PDF's designed
font corrupts direct text extraction (its ToUnicode maps letters to wrong
glyphs), so the Arabic was transcribed verbatim from the visually-rendered pages
and cross-checked article-by-article against the official English column printed
in the same document.  That transcription lives, with provenance, in
``investment_law_official_misa_source.json``; this generator emits per-article
verified records from it.

Arabic is the governing source; the English is reference only.  No translation,
paraphrase, or interpretation is performed.

Read-only over its input; deterministic and idempotent over its output.
"""

from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "sources", "investment", "law", "official_source",
                      "investment_law_official_misa_source.json")
OUT_DIR = os.path.join(ROOT, "sources", "investment", "law", "verified")
RECORDS = os.path.join(OUT_DIR, "investment_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_DIR, "investment_law_verified_summary.json")

EXPECTED = 16


def build_records():
    src = json.load(open(SOURCE, encoding="utf-8"))
    arts = src["articles"]
    records = []
    for n in range(1, EXPECTED + 1):
        a = arts[str(n)]
        records.append({
            "law_key": "investment",
            "law_component": "law",
            "language": "ar",
            "record_layer": "INVESTMENT_LAW_ARABIC_VERIFIED_TEXT",
            "article_number": n,
            "article_key": "investment_law_art_%03d" % n,
            "arabic_title": a["title_ar"],
            "article_text_verified": a["text_ar"],
            "article_text_en_reference": a.get("text_en", ""),
            "official_text_status": "VERIFIED_TRANSCRIBED_FROM_OFFICIAL_MISA_PDF",
            "verification_method": (
                "Transcribed verbatim from the visually-rendered official MISA PDF "
                "(font-corrupt extraction bypassed) and cross-checked against the official "
                "English column in the same document."
            ),
            "source_authority_ar": src["source_authority_ar"],
            "source_pdf_sha256": src["source_pdf_sha256"],
            "governing_source_note": (
                "Arabic is the governing source. article_text_verified is the official MISA "
                "Investment Law text; the English is reference only."
            ),
            "english_is_reference_only": True,
            "translation_performed": False,
            "legal_interpretation_performed": False,
            "summarized_or_paraphrased": False,
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
        "law_component": "law",
        "layer": "INVESTMENT_LAW_ARABIC_VERIFIED_TEXT",
        "title_ar": "نظام الاستثمار",
        "record_count": len(records),
        "article_number_range": [1, EXPECTED],
        "official_text_status": "VERIFIED_TRANSCRIBED_FROM_OFFICIAL_MISA_PDF",
        "source_artifact": os.path.relpath(SOURCE, ROOT),
        "source_pdf": "inputs/investment_official_pdfs/investment_law_misa.pdf",
        "boundaries": {
            "arabic_governs": True,
            "english_is_reference_only": True,
            "translation_performed": False,
            "legal_interpretation_performed": False,
            "summarized_or_paraphrased": False,
        },
        "recommended_next_stage": "INVESTMENT_LAW_ARABIC_LEGAL_LLM",
    }
    with open(SUMMARY, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Wrote %d verified investment-law records -> %s" % (len(records), os.path.relpath(RECORDS, ROOT)))


if __name__ == "__main__":
    main()
