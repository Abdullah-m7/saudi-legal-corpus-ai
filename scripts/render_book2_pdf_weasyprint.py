#!/usr/bin/env python3
"""Render dist/book2.pdf from dist/book2.html using WeasyPrint (optional).

PDF is the print/share-ready visual output; HTML remains the canonical
searchable/copyable text view. WeasyPrint is optional — if unavailable, this
prints guidance and exits non-zero without breaking the pipeline.
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from saudi_law_corpus import books  # noqa: E402

HTML = books.get_book(2).html_out
PDF = books.get_book(2).pdf_out


def main() -> int:
    if not os.path.exists(HTML):
        print(f"{HTML} not found. Run: python scripts/render_book2_html.py first",
              file=sys.stderr)
        return 2
    try:
        from weasyprint import HTML as WeasyHTML  # type: ignore
    except Exception as exc:  # pragma: no cover
        print("WeasyPrint is not available:", exc, file=sys.stderr)
        print("\nWeasyPrint is OPTIONAL. Install with: pip install weasyprint",
              file=sys.stderr)
        print("The HTML book (dist/book2.html) is the canonical searchable output.",
              file=sys.stderr)
        return 3

    WeasyHTML(filename=HTML).write_pdf(PDF)
    print(f"wrote {os.path.relpath(PDF, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
