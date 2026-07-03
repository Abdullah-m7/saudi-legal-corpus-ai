#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Official English guidance REFERENCE layer — Book One (Part 1, Articles 1–34).

Segments the official English guidance translation PDF (Bureau of Experts /
Official Translation Department) by its `Article N:` headings and writes one
reference record per article for Book One (Articles 1–34 only).

This is an English REFERENCE/alignment layer:
- The English is an `official_guidance_translation`; the GOVERNING text is Arabic.
- `manual_review_status = needs_manual_check` (article-level alignment not yet
  human-verified).
- It does NOT create the English Legal LLM-ready layer and does NOT generate any
  model-written English summaries — the text is the source's own wording.
- It does NOT read or modify any Arabic canonical or Chinese data.

Reads : inputs/companies_law_official_english_guidance.pdf   (via pypdf)
        or the extracted aid data/extracted/official_english_companies_law_text.txt
Writes: data/english_reference/book1_en_reference.json
        data/english_reference/book1_en_reference.jsonl

No network access. Fails loudly if any Article 1–34 is missing.
"""

from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PDF = os.path.join(ROOT, "inputs", "companies_law_official_english_guidance.pdf")
EXTRACTED = os.path.join(ROOT, "data", "extracted", "official_english_companies_law_text.txt")
OUT_DIR = os.path.join(ROOT, "data", "english_reference")
OUT_JSON = os.path.join(OUT_DIR, "book1_en_reference.json")
OUT_JSONL = os.path.join(OUT_DIR, "book1_en_reference.jsonl")

BOOK = 1
PART_NUMBER_EN = 1
PART_TITLE_EN = "General Provisions"
ARTICLES = list(range(1, 35))  # 1..34

SOURCE_AUTHORITY = "Bureau of Experts at the Council of Ministers"
DEPARTMENT = "Official Translation Department"
SOURCE_FILE_REL = "inputs/companies_law_official_english_guidance.pdf"
OFFICIAL_NOTE = ("This translation is provided for guidance. The governing text is the "
                 "Arabic text. Not legal advice.")

_STOP = {"of", "a", "an", "the", "and", "or", "to", "in", "for", "on", "against",
         "by", "with", "into", "from", "at", "as"}


def _raw_text():
    """Return the source text. Prefer the PDF via pypdf; fall back to the aid file."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(PDF)
        return "\n".join((p.extract_text() or "") for p in reader.pages), "pypdf(PDF)"
    except ImportError:
        if os.path.exists(EXTRACTED):
            with open(EXTRACTED, "r", encoding="utf-8") as fh:
                return fh.read(), "extracted_text_aid"
        raise SystemExit(
            "ERROR: pypdf is not installed and no extracted aid found.\n"
            "Install extras: pip install -e \".[extract]\" (or run "
            "`make official-english-source-extract` where pypdf is available)."
        )


_HEAD = re.compile(r'Article\s+(\d+)\s*:\s*([^\n]*)')


def _clean_body(segment: str) -> str:
    """Strip running headers / page numbers / structural headings; collapse space."""
    # Drop the leading "Article N: Title" line.
    s = re.sub(r'^\s*Article\s+\d+\s*:[^\n]*', ' ', segment, count=1)
    # Page footer: running header immediately followed by a page number. This is
    # restricted to the header+number form so legitimate inline content such as
    # the Article 1 definition "Law: Companies Law." is preserved.
    s = re.sub(r'Companies Law\s+\d+', ' ', s)
    # A line that is ONLY the running header (no page number on the line).
    s = re.sub(r'(?m)^[ \t]*Companies Law[ \t]*$', ' ', s)
    # Structural headings that leak from adjacent sections.
    s = re.sub(r'Preliminary Chapter', ' ', s)
    s = re.sub(r'(Chapter|Part|Section)\s+\d+\s*:[^\n]*', ' ', s)
    # Collapse all whitespace to single spaces.
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def _keywords(heading: str):
    words = re.findall(r"[A-Za-z][A-Za-z\-]+", heading)
    kw = []
    for w in words:
        lw = w.lower()
        if lw not in _STOP and lw not in [k.lower() for k in kw]:
            kw.append(w)
    return kw[:6]


def _segment(text):
    """Return {article_number: (heading, body)} for the first occurrence of each."""
    hits = [(m.start(), int(m.group(1)), m.group(2).strip()) for m in _HEAD.finditer(text)]
    starts = sorted({s for s, _, _ in hits})
    seen = {}
    for start, num, heading in hits:
        if num not in seen:
            nxt = min([s for s in starts if s > start], default=len(text))
            seen[num] = (heading, _clean_body(text[start:nxt]))
    return seen


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
            "source_file": SOURCE_FILE_REL,
            "source_authority": SOURCE_AUTHORITY,
            "department": DEPARTMENT,
            "extraction_method": "pypdf text extraction + heading segmentation",
            "official_guidance_note": OFFICIAL_NOTE,
        },
        "llm": {
            "chunk_id": "sa-companies-book1-en-art%03d" % n,
            "retrieval_title_en": "Article %d — %s" % (n, heading),
            "keywords_en": _keywords(heading),
        },
        "risk_flags": ["needs_manual_check", "english_is_guidance_arabic_governs"],
    }


def main():
    text, method = _raw_text()
    seen = _segment(text)

    missing = [n for n in ARTICLES if n not in seen]
    if missing:
        raise SystemExit("ERROR: missing Article(s) in source extraction: %s" % missing)

    records = []
    for n in ARTICLES:
        heading, body = seen[n]
        if not heading.strip():
            raise SystemExit("ERROR: empty heading for Article %d" % n)
        if not body.strip():
            raise SystemExit("ERROR: empty reference text for Article %d" % n)
        records.append(_record(n, heading, body))

    got = [r["article_number"] for r in records]
    assert got == ARTICLES, got

    payload = {
        "layer_id": "sa-companies-english-reference",
        "scope": "book1_part1_general_provisions",
        "book": BOOK,
        "part_number_en": PART_NUMBER_EN,
        "part_title_en": PART_TITLE_EN,
        "part_heading_en": "Part 1: General Provisions",
        "article_range": "1-34",
        "articles": ARTICLES,
        "english_source_status": "official_guidance_translation",
        "governing_text_language": "ar",
        "source_authority": SOURCE_AUTHORITY,
        "department": DEPARTMENT,
        "source_file": SOURCE_FILE_REL,
        "extraction_method": method,
        "disclaimer_en": ("Official guidance translation only; the governing/binding text is the "
                          "Arabic original. Not legal advice."),
        "records": records,
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    with open(OUT_JSONL, "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    print("wrote %s (%d records) and %s [source: %s]" % (
        OUT_JSON, len(records), OUT_JSONL, method))


if __name__ == "__main__":
    main()
