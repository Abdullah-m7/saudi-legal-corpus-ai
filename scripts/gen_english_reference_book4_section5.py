#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Official English guidance REFERENCE layer — Book Four, Section 5
(finance_profits_and_capital_changes).

Adds English guidance reference records ONLY for the Book Four Section 5
provision-covered articles: 123, 124, 126, 127, 128, 129, 130, 132, 133 (Part 4 —
Joint-Stock Company). English reference records are PER ARTICLE (the source renders
each under its own `Article N:` heading).

Articles 134 & 135 ("Issuance of a Capital Decrease Decision" / "Capital Decrease
Procedures") EXIST in the official English source, but the Book Four model-1b source
treats them as CROSS-REFERENCE ONLY in Section 5 (they appear only as a reference in
the capital-reduction block) — so they are deliberately OUT OF SCOPE and get no record.
No records are created for the other uncovered Section-5 articles (121, 122, 125, 131,
136, 137).

Reuses the shared extraction/segmentation/cleaning logic from
`gen_english_reference_book1.py`.

Reads : inputs/companies_law_official_english_guidance.pdf (via pypdf; aid fallback)
        data/articles/book4_provisions_121_137.json (guardrail cross-check only)
Writes: data/english_reference/book4_section5_en_reference.json (+ .jsonl)

Fails loudly if any of Articles 123, 124, 126, 127, 128, 129, 130, 132, 133 is missing.
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
OUT_JSON = os.path.join(OUT_DIR, "book4_section5_en_reference.json")
OUT_JSONL = os.path.join(OUT_DIR, "book4_section5_en_reference.jsonl")
PROVISIONS = os.path.join(ROOT, "data", "articles", "book4_provisions_121_137.json")

BOOK = 4
PART_NUMBER_EN = 4
PART_TITLE_EN = "Joint-Stock Company"
PART_HEADING_EN = "Part 4: Joint-Stock Company"
COVERED = [123, 124, 126, 127, 128, 129, 130, 132, 133]   # provision-covered
EXCLUDED_UNCOVERED = [121, 122, 125, 131, 134, 135, 136, 137]
# Articles 134 & 135 are excluded even though they exist in the English source
# (the model-1b source treats them as cross-reference only — see module docstring).
FORBIDDEN = set(EXCLUDED_UNCOVERED) | set(range(58, 121))


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
    # Guardrail: English coverage must equal the Section 5 provision set.
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
    assert not ({134, 135} & set(got)), "Articles 134/135 must be excluded"
    assert not (set(got) & FORBIDDEN), got  # nothing uncovered / nothing outside section

    payload = {
        "layer_id": "sa-companies-english-reference",
        "scope": "book4_section5_part4_finance_profits_and_capital_changes",
        "book": BOOK,
        "part_number_en": PART_NUMBER_EN,
        "part_title_en": PART_TITLE_EN,
        "part_heading_en": PART_HEADING_EN,
        "section_key": "finance_profits_and_capital_changes",
        "article_range": "121-137",
        "explicit_articles": COVERED,
        "uncovered_articles_excluded": EXCLUDED_UNCOVERED,
        "coverage_model": "book_four_model_1b (provision-covered articles only)",
        "articles_134_135_note": ("Articles 134 ('Issuance of a Capital Decrease Decision') and 135 "
                                  "('Capital Decrease Procedures') exist in the official English source "
                                  "but are out of scope: the Book Four model-1b source treats them as "
                                  "cross-reference only in the capital-reduction block."),
        "articles": COVERED,
        "english_source_status": "official_guidance_translation",
        "governing_text_language": "ar",
        "source_authority": base.SOURCE_AUTHORITY,
        "department": base.DEPARTMENT,
        "source_file": base.SOURCE_FILE_REL,
        "extraction_method": method,
        "disclaimer_en": ("Official guidance translation only; the governing/binding text is the "
                          "Arabic original. Not legal advice. Follows Book Four model 1b coverage "
                          "(other Section-5 articles, incl. 134 & 135, remain uncovered)."),
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
