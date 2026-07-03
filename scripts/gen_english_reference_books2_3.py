#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Official English guidance REFERENCE layer — Books Two and Three.

Extends the Book One English reference pilot to:
  Book Two  / Part 2 — General Partnerships (Articles 35–50, 16 records)
  Book Three / Part 3 — Limited Partnership (Articles 51–57,  7 records)

The risky extraction/segmentation/cleaning logic is REUSED from
`gen_english_reference_book1.py` (single source of truth); this script only adds
per-book parameters and the record shape. Consistent with that module:
- The English is an `official_guidance_translation`; the GOVERNING text is Arabic.
- `manual_review_status = needs_manual_check`.
- No model-written summaries — the text is the source's own wording.
- No network; does not read or modify Arabic canonical or Chinese data; creates no
  English Legal LLM records.

Reads : inputs/companies_law_official_english_guidance.pdf  (via pypdf; aid fallback)
Writes: data/english_reference/book2_en_reference.json (+ .jsonl)
        data/english_reference/book3_en_reference.json (+ .jsonl)

Fails loudly if any Article 35–57 is missing from the source extraction.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# Reuse the shared extraction/segmentation/cleaning + provenance constants.
import gen_english_reference_book1 as base  # noqa: E402

OUT_DIR = os.path.join(ROOT, "data", "english_reference")

BOOKS = [
    {
        "book": 2,
        "part_number_en": 2,
        "part_title_en": "General Partnerships",
        "part_heading_en": "Part 2: General Partnerships",
        "scope": "book2_part2_general_partnerships",
        "article_range": "35-50",
        "articles": list(range(35, 51)),
        "out_json": os.path.join(OUT_DIR, "book2_en_reference.json"),
        "out_jsonl": os.path.join(OUT_DIR, "book2_en_reference.jsonl"),
    },
    {
        "book": 3,
        "part_number_en": 3,
        "part_title_en": "Limited Partnership",
        "part_heading_en": "Part 3: Limited Partnership",
        "scope": "book3_part3_limited_partnership",
        "article_range": "51-57",
        "articles": list(range(51, 58)),
        "out_json": os.path.join(OUT_DIR, "book3_en_reference.json"),
        "out_jsonl": os.path.join(OUT_DIR, "book3_en_reference.jsonl"),
    },
]


def _record(book, part_number_en, part_title_en, n, heading, body):
    return {
        "book": book,
        "article_number": n,
        "part_number_en": part_number_en,
        "part_title_en": part_title_en,
        "article_heading_en": heading,
        "english_reference_text": body,
        "english_source_status": "official_guidance_translation",
        "governing_text_language": "ar",
        "alignment_status": "article_heading_extracted",
        "manual_review_status": "needs_manual_check",
        "source": {
            "source_file": base.SOURCE_FILE_REL,
            "source_authority": base.SOURCE_AUTHORITY,
            "department": base.DEPARTMENT,
            "extraction_method": "pypdf text extraction + heading segmentation",
            "official_guidance_note": base.OFFICIAL_NOTE,
        },
        "llm": {
            "chunk_id": "sa-companies-book%d-en-art%03d" % (book, n),
            "retrieval_title_en": "Article %d — %s" % (n, heading),
            "keywords_en": base._keywords(heading),
        },
        "risk_flags": ["needs_manual_check", "english_is_guidance_arabic_governs"],
    }


def main():
    text, method = base._raw_text()
    seen = base._segment(text)

    os.makedirs(OUT_DIR, exist_ok=True)
    for spec in BOOKS:
        arts = spec["articles"]
        missing = [n for n in arts if n not in seen]
        if missing:
            raise SystemExit("ERROR: missing Article(s) in source extraction (book %d): %s"
                             % (spec["book"], missing))
        records = []
        for n in arts:
            heading, body = seen[n]
            if not heading.strip():
                raise SystemExit("ERROR: empty heading for Article %d" % n)
            if not body.strip():
                raise SystemExit("ERROR: empty reference text for Article %d" % n)
            records.append(_record(spec["book"], spec["part_number_en"],
                                   spec["part_title_en"], n, heading, body))

        got = [r["article_number"] for r in records]
        assert got == arts, (spec["book"], got)

        payload = {
            "layer_id": "sa-companies-english-reference",
            "scope": spec["scope"],
            "book": spec["book"],
            "part_number_en": spec["part_number_en"],
            "part_title_en": spec["part_title_en"],
            "part_heading_en": spec["part_heading_en"],
            "article_range": spec["article_range"],
            "articles": arts,
            "english_source_status": "official_guidance_translation",
            "governing_text_language": "ar",
            "source_authority": base.SOURCE_AUTHORITY,
            "department": base.DEPARTMENT,
            "source_file": base.SOURCE_FILE_REL,
            "extraction_method": method,
            "disclaimer_en": ("Official guidance translation only; the governing/binding text is "
                              "the Arabic original. Not legal advice."),
            "records": records,
        }
        with open(spec["out_json"], "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        with open(spec["out_jsonl"], "w", encoding="utf-8") as fh:
            for r in records:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print("wrote %s (%d records) and %s" % (spec["out_json"], len(records), spec["out_jsonl"]))
    print("source: %s" % method)


if __name__ == "__main__":
    main()
