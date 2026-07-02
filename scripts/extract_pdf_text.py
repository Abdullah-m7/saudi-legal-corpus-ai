#!/usr/bin/env python3
"""Extract raw text from the source PDF for inspection.

This is a *diagnostic* tool only. The PDF's Arabic layer extracts in a garbled
form and MUST NOT be treated as canonical source (see data/metadata/
source_provenance.json). Canonical Arabic lives in data/articles/*.json as
manually reconstructed text.

Requires ``pypdf`` (optional dependency). Falls back with a clear message if it
is not installed.

Usage:
    python scripts/extract_pdf_text.py [inputs/bab1_source.pdf] [-o out.txt]
"""

from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PDF = os.path.join(ROOT, "inputs", "bab1_source.pdf")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", nargs="?", default=DEFAULT_PDF)
    ap.add_argument("-o", "--out", default=None, help="write extracted text to file")
    args = ap.parse_args()

    if not os.path.exists(args.pdf):
        print(f"PDF not found: {args.pdf}", file=sys.stderr)
        return 2

    try:
        from pypdf import PdfReader
    except Exception:
        print("pypdf is not installed. Install with: pip install pypdf",
              file=sys.stderr)
        print("(This is an optional diagnostic tool; the corpus does not depend "
              "on it.)", file=sys.stderr)
        return 3

    reader = PdfReader(args.pdf)
    chunks = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        chunks.append(f"===== PAGE {i + 1} =====\n{text}")
    output = "\n\n".join(chunks)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(output)
        print(f"wrote {args.out} ({len(reader.pages)} pages)")
    else:
        print(output)
    print("\nNOTE: Arabic extraction is garbled and is NOT canonical. "
          "See data/metadata/source_provenance.json.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
