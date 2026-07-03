#!/usr/bin/env python3
"""Build data/articles/book4_provisions_121_137.jsonl (one line per provision)."""

from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "articles", "book4_provisions_121_137.json")
OUT = os.path.join(ROOT, "data", "articles", "book4_provisions_121_137.jsonl")


def main() -> int:
    with open(SRC, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    provisions = doc["provisions"]
    with open(OUT, "w", encoding="utf-8") as fh:
        for p in provisions:
            chunk = {
                "chunk_id": p["llm"]["chunk_id"],
                "book": 4,
                "provision_id": p["provision_id"],
                "source_article_numbers": p["source_article_numbers"],
                "thematic_section": p["thematic_section"],
                "retrieval_title": p["llm"]["retrieval_title"],
                "provision_title_ar": p["provision_title_ar"],
                "provision_title_zh": p["provision_title_zh"],
                "arabic_reference_summary": p["arabic_reference_summary"],
                "chinese_translation": p["chinese_translation"],
                "summary_en": p["llm"].get("summary_en", ""),
                "keywords_ar": p["llm"]["keywords_ar"],
                "keywords_zh": p["llm"]["keywords_zh"],
                "legal_risk_tags": p.get("risk_flags", []),
                "translation_mode": p["translation_mode"],
                "official_text_check": p["source"]["official_text_check"],
                "source_coverage_status": p["source"]["source_coverage_status"],
                "source": {"input_pdf": p["source"]["input_pdf"], "book": 4,
                           "note": "Book Four model 1b — thematic provision (Section 5)"},
                "disclaimer": {"is_official": False, "is_legal_advice": False},
            }
            fh.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    print(f"wrote {os.path.relpath(OUT, ROOT)} with {len(provisions)} provision chunks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
