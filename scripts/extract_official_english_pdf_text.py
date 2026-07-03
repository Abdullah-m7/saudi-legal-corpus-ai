#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lightweight text extractor for the OFFICIAL ENGLISH GUIDANCE translation PDF.

Source: Bureau of Experts at the Council of Ministers / Official Translation
Department — "Companies Law" (Royal Decree No. M/132). This PDF is an
`official_guidance_translation`; the governing / binding legal text remains the
Arabic original. This script only extracts text for downstream planning — it does
NOT create any English Legal LLM records and does NOT alter Arabic or Chinese
content.

Reads : inputs/companies_law_official_english_guidance.pdf
Writes: data/extracted/official_english_companies_law_text.txt

Behaviour:
- No network calls.
- Graceful fallback: if no PDF library is installed, it prints guidance and exits
  0 WITHOUT writing output, unless extraction is explicitly requested with
  --require (then it exits non-zero). This keeps the optional dependency from
  breaking the default test suite.
"""

from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PDF = os.path.join(ROOT, "inputs", "companies_law_official_english_guidance.pdf")
OUT_DIR = os.path.join(ROOT, "data", "extracted")
OUT = os.path.join(OUT_DIR, "official_english_companies_law_text.txt")

_HEADER = (
    "OFFICIAL ENGLISH GUIDANCE TRANSLATION — Companies Law (Royal Decree M/132)\n"
    "Source: Bureau of Experts at the Council of Ministers / Official Translation Department.\n"
    "Trust: official_guidance_translation. Governing/binding text: Arabic. Not legal advice.\n"
    "This file is an extracted text aid for alignment planning only; it is NOT a legal record.\n"
    + ("=" * 78) + "\n\n"
)


def _extract_with_pypdf(path):
    from pypdf import PdfReader  # optional dependency (extra: extract)
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append("----- PAGE %d -----\n%s\n" % (i, text))
    return len(reader.pages), "\n".join(pages)


def extract(require: bool = False) -> int:
    if not os.path.exists(PDF):
        msg = "PDF not found: %s" % PDF
        print(msg)
        return 1 if require else 0

    try:
        n_pages, body = _extract_with_pypdf(PDF)
    except ImportError:
        print("pypdf not installed; skipping extraction (install extras: pip install -e \".[extract]\").")
        print("Extraction is OPTIONAL — the intake metadata/docs do not depend on it.")
        return 1 if require else 0
    except Exception as exc:  # pragma: no cover - defensive
        print("extraction failed: %s" % exc)
        return 1 if require else 0

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(_HEADER)
        fh.write(body)
    print("wrote %s (%d pages extracted)" % (OUT, n_pages))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--require", action="store_true",
                    help="Fail (exit 1) if extraction cannot be performed.")
    args = ap.parse_args()
    return extract(require=args.require)


if __name__ == "__main__":
    raise SystemExit(main())
