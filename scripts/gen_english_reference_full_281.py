#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the FULL official English BOE guidance reference alignment (all 281 articles).

Segments the official English guidance-translation PDF (Bureau of Experts / Official Translation
Department) into 281 per-article reference records by `Article N:` headings, preserving the
official English text verbatim as `english_reference_text` (minimal whitespace normalization only,
identical to the existing English-reference extraction policy). This is a REFERENCE/ALIGNMENT layer
only — it does NOT translate, summarize, paraphrase, or rewrite; it does NOT create the English
Legal LLM-ready layer; and English is guidance only (Arabic governs). Not legal advice.

Text source policy (same as the existing English reference generators): prefer the PDF via pypdf;
fall back to the regenerable extracted text aid.

Reads : inputs/companies_law_official_english_guidance.pdf
        (fallback: data/extracted/official_english_companies_law_text.txt)
Writes: data/english_reference/companies_law_m132_1443_en_reference_001_281.json
"""

from __future__ import annotations

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "inputs", "companies_law_official_english_guidance.pdf")
EXTRACTED = os.path.join(ROOT, "data", "extracted", "official_english_companies_law_text.txt")
OUT = os.path.join(ROOT, "data", "english_reference",
                   "companies_law_m132_1443_en_reference_001_281.json")

TARGET = 281
ARTICLES = list(range(1, TARGET + 1))
SOURCE_FILE_REL = "inputs/companies_law_official_english_guidance.pdf"
SOURCE_AUTHORITY = "Bureau of Experts at the Council of Ministers"
DEPARTMENT = "Official Translation Department"
EXTRACTION_METHOD = "official_english_pdf_text_layer_segmentation"
OFFICIAL_NOTE = ("This translation is provided for guidance. The governing text is the "
                 "Arabic text.")
# Conservative single mechanical grouping for the full-law file. We do NOT reuse the old repo
# book4 convention and do NOT claim any book model covers the whole law; per-part/book
# segmentation is deferred to manual review (see risk flag + manual_review_status).
BOOK = 1
PART_NUMBER_EN = 1
PART_TITLE_EN = ("Companies Law (full 281-article official English guidance translation; "
                 "per-part segmentation pending manual review)")

_STOP = {"the", "of", "a", "an", "and", "or", "to", "in", "on", "for", "by", "with", "from",
         "as", "at", "into", "this", "that", "shall", "be", "is", "are"}

_HEAD = re.compile(r'Article\s+(\d+)\s*:\s*([^\n]*)')


def _raw_text():
    """Return the source text. Prefer the PDF via pypdf; fall back to the extracted aid."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(PDF)
        return "\n".join((p.extract_text() or "") for p in reader.pages), "pypdf(PDF)"
    except ImportError:
        if os.path.exists(EXTRACTED):
            with open(EXTRACTED, "r", encoding="utf-8") as fh:
                return fh.read(), "extracted_text_aid"
        raise SystemExit(
            "ERROR: pypdf is not installed and no extracted aid found. "
            "Install extras: pip install -e \".[extract]\" (or run "
            "`make official-english-source-extract` where pypdf is available).")


def _clean_body(segment: str) -> str:
    """Strip running headers / page numbers / structural headings; collapse space.

    Identical policy to the existing English-reference generators so the full file's text is
    consistent with the committed 87-record split layer.
    """
    s = re.sub(r'^\s*Article\s+\d+\s*:[^\n]*', ' ', segment, count=1)
    s = re.sub(r'Companies Law\s+\d+', ' ', s)
    s = re.sub(r'(?m)^[ \t]*Companies Law[ \t]*$', ' ', s)
    s = re.sub(r'Preliminary Chapter', ' ', s)
    s = re.sub(r'(Chapter|Part|Section)\s+\d+\s*:[^\n]*', ' ', s)
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
    """Return {article_number: (heading, body)} for the first occurrence of each heading."""
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
            "extraction_method": EXTRACTION_METHOD,
            "official_guidance_note": OFFICIAL_NOTE,
        },
        "llm": {
            "chunk_id": "en-ref-companies-art-%03d" % n,
            "retrieval_title_en": "Companies Law - Article %d - %s" % (n, heading),
            "keywords_en": _keywords(heading),
        },
        "risk_flags": [
            "needs_manual_check",
            "english_is_guidance_arabic_governs",
            "part_segmentation_pending_manual_review",
        ],
    }


def build():
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

    assert [r["article_number"] for r in records] == ARTICLES

    payload = {
        "layer_id": "sa-companies-english-reference-full",
        "scope": "companies_law_full_articles_001_281",
        "law_id": "sa-companies-law-m132-1443",
        "title_en": "Companies Law — full official English guidance reference alignment (281 articles)",
        "article_range": "1-281",
        "record_count": len(records),
        "articles": ARTICLES,
        "english_source_status": "official_guidance_translation",
        "governing_text_language": "ar",
        "source_authority": SOURCE_AUTHORITY,
        "department": DEPARTMENT,
        "source_file": SOURCE_FILE_REL,
        "extraction_method": EXTRACTION_METHOD,
        "text_source_method": method,
        "separate_from": "the existing 87-record split English reference layer (book1-3 + repo "
                         "book4 sections); those files are left untouched",
        "part_book_mapping_note": "Conservative single mechanical grouping (book=1, "
                                  "part_number_en=1) for the full-law file. The old repo book4 "
                                  "convention is NOT reused and no book model is claimed to cover "
                                  "the whole law; per-part/book segmentation is deferred to "
                                  "manual review.",
        "not_legal_advice": True,
        "disclaimer_en": "Official English guidance translation (Bureau of Experts / Official "
                         "Translation Department). English is guidance only; the Arabic text is "
                         "governing. Reference/alignment layer only — not the English Legal "
                         "LLM-ready layer, and not legal advice.",
        "records": records,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("wrote full English reference alignment: %d records (articles %d..%d) via %s -> %s"
          % (len(records), records[0]["article_number"], records[-1]["article_number"],
             method, os.path.relpath(OUT, ROOT)))


def main():
    build()


if __name__ == "__main__":
    main()
