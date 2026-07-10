#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the verified Arabic text records for the Civil Transactions Law (721 articles).

Source: the owner-provided full official Arabic text of نظام المعاملات المدنية
(Royal Decree M/191, 29/11/1444H), committed with provenance in
``civil_transactions_law_official_source.json``.  The text was parsed
deterministically into 721 articles by Arabic-ordinal header matching (sequence
verified complete), structural section headings separated as ``section_context``,
and spot-corroborated verbatim against an independent public mirror (Articles 1
and 70).  Arabic is the governing source.  No translation, paraphrase, or
interpretation.

Read-only over its input; deterministic and idempotent over its output.
"""

from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "sources", "civil", "law", "official_source",
                      "civil_transactions_law_official_source.json")
OUT_DIR = os.path.join(ROOT, "sources", "civil", "law", "verified")
RECORDS = os.path.join(OUT_DIR, "civil_transactions_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_DIR, "civil_transactions_law_verified_summary.json")

EXPECTED = 721


def build_records():
    src = json.load(open(SOURCE, encoding="utf-8"))
    arts = src["articles"]
    records = []
    for n in range(1, EXPECTED + 1):
        a = arts[str(n)]
        records.append({
            "law_key": "civil",
            "law_component": "law",
            "language": "ar",
            "record_layer": "CIVIL_TRANSACTIONS_LAW_ARABIC_VERIFIED_TEXT",
            "article_number": n,
            "article_key": "civil_law_art_%03d" % n,
            "section_context_ar": a.get("section_context", ""),
            "article_text_verified": a["text"],
            "official_text_status": "OWNER_PROVIDED_OFFICIAL_TEXT",
            "verification_method": (
                "Owner-provided official law text parsed deterministically into 721 articles "
                "(complete 1..721 sequence); spot-corroborated verbatim against an independent "
                "public mirror (Articles 1 and 70)."
            ),
            "source_authority_ar": src["source_authority_ar"],
            "royal_decree": src["royal_decree"],
            "governing_source_note": (
                "Arabic is the governing source. article_text_verified is the official Civil "
                "Transactions Law text as provided by the owner from the official source."
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
        "law_key": "civil",
        "law_component": "law",
        "layer": "CIVIL_TRANSACTIONS_LAW_ARABIC_VERIFIED_TEXT",
        "title_ar": "نظام المعاملات المدنية",
        "record_count": len(records),
        "article_number_range": [1, EXPECTED],
        "official_text_status": "OWNER_PROVIDED_OFFICIAL_TEXT",
        "source_artifact": os.path.relpath(SOURCE, ROOT),
        "spot_corroborated_articles": [1, 70],
        "boundaries": {
            "arabic_governs": True,
            "translation_performed": False,
            "legal_interpretation_performed": False,
            "summarized_or_paraphrased": False,
            "english_used_for_correction": False,
        },
        "recommended_next_stage": "CIVIL_TRANSACTIONS_LAW_ARABIC_LEGAL_LLM",
    }
    with open(SUMMARY, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Wrote %d verified civil-law records -> %s"
          % (len(records), os.path.relpath(RECORDS, ROOT)))


if __name__ == "__main__":
    main()
