#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Official English guidance REFERENCE layer — Book Four, Section 3 (general_assemblies).

Adds English guidance reference records ONLY for the owner-reconciled Book Four
Section 3 provision-covered articles: 85, 87, 92, 93, 99, 101, 102 (Part 4 —
Joint-Stock Company). English reference records are PER ARTICLE (the source renders
each under its own `Article N:` heading).

Article 100 ("Issuing a Decision by Circulation") EXISTS in the official English
source, but the owner-reconciled Book Four model-1b source maps the circulation
provision to Article 101 only — so Article 100 is deliberately OUT OF SCOPE and gets
no record. No records are created for the other uncovered Section-3 articles
(84, 86, 88, 89, 90, 91, 94–98) or for Articles 103–137.

Reuses the shared extraction/segmentation/cleaning logic from
`gen_english_reference_book1.py`.

Reads : inputs/companies_law_official_english_guidance.pdf (via pypdf; aid fallback)
        data/articles/book4_provisions_084_102.json (guardrail cross-check only)
Writes: data/english_reference/book4_section3_en_reference.json (+ .jsonl)

Fails loudly if any of Articles 85, 87, 92, 93, 99, 101, 102 is missing.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import gen_english_reference_book1 as base  # noqa: E402

OUT_DIR = os.path.join(ROOT, "data", "english_reference")
OUT_JSON = os.path.join(OUT_DIR, "book4_section3_en_reference.json")
OUT_JSONL = os.path.join(OUT_DIR, "book4_section3_en_reference.jsonl")
PROVISIONS = os.path.join(ROOT, "data", "articles", "book4_provisions_084_102.json")

BOOK = 4
PART_NUMBER_EN = 4
PART_TITLE_EN = "Joint-Stock Company"
PART_HEADING_EN = "Part 4: Joint-Stock Company"
COVERED = [85, 87, 92, 93, 99, 101, 102]              # provision-covered (reconciled)
EXCLUDED_UNCOVERED = [84, 86, 88, 89, 90, 91, 94, 95, 96, 97, 98, 100]
# Article 100 is excluded even though it exists in the English source (see module docstring).
FORBIDDEN = set(EXCLUDED_UNCOVERED) | set(range(103, 138))


def _record(n, heading, body):
    return {
        "book": BOOK,
        "article_number": n,
        "part_number_en": PART_NUMBER_EN,
        "part_title_en": PART_TITLE_EN,
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
            "chunk_id": "sa-companies-book4-en-art%03d" % n,
            "retrieval_title_en": "Article %d — %s" % (n, heading),
            "keywords_en": base._keywords(heading),
        },
        "risk_flags": ["needs_manual_check", "english_is_guidance_arabic_governs"],
    }


def main():
    # Guardrail: English coverage must equal the reconciled Section 3 provision set.
    with open(PROVISIONS, "r", encoding="utf-8") as fh:
        prov_arts = sorted({a for p in json.load(fh)["provisions"] for a in p["source_article_numbers"]})
    assert prov_arts == COVERED, "provision-covered set %s != %s" % (prov_arts, COVERED)

    text, method = base._raw_text()
    seen = base._segment(text)

    missing = [n for n in COVERED if n not in seen]
    if missing:
        raise SystemExit("ERROR: missing Article(s) in source extraction: %s" % missing)

    records = []
    for n in COVERED:
        heading, body = seen[n]
        if not heading.strip() or not body.strip():
            raise SystemExit("ERROR: empty heading/text for Article %d" % n)
        records.append(_record(n, heading, body))

    got = [r["article_number"] for r in records]
    assert got == COVERED, got
    assert 100 not in got, "Article 100 must be excluded"
    assert not (set(got) & FORBIDDEN), got  # nothing uncovered / nothing 103-137

    payload = {
        "layer_id": "sa-companies-english-reference",
        "scope": "book4_section3_part4_general_assemblies",
        "book": BOOK,
        "part_number_en": PART_NUMBER_EN,
        "part_title_en": PART_TITLE_EN,
        "part_heading_en": PART_HEADING_EN,
        "section_key": "general_assemblies",
        "article_range": "84-102",
        "explicit_articles": COVERED,
        "uncovered_articles_excluded": EXCLUDED_UNCOVERED,
        "coverage_model": "book_four_model_1b (owner-reconciled; provision-covered articles only)",
        "article_100_note": ("Article 100 ('Issuing a Decision by Circulation') exists in the "
                             "official English source but is out of scope: the owner-reconciled "
                             "Book Four source maps circulation to Article 101 only."),
        "articles": COVERED,
        "english_source_status": "official_guidance_translation",
        "governing_text_language": "ar",
        "source_authority": base.SOURCE_AUTHORITY,
        "department": base.DEPARTMENT,
        "source_file": base.SOURCE_FILE_REL,
        "extraction_method": method,
        "disclaimer_en": ("Official guidance translation only; the governing/binding text is the "
                          "Arabic original. Not legal advice. Follows Book Four model 1b coverage "
                          "(other Section-3 articles, incl. 84/89/100, remain uncovered)."),
        "records": records,
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    with open(OUT_JSONL, "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("wrote %s (%d records: %s) and %s [source: %s]" % (
        OUT_JSON, len(records), COVERED, OUT_JSONL, method))


if __name__ == "__main__":
    main()
