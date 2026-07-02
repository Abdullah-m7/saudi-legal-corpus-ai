#!/usr/bin/env python3
"""Render dist/book1.pdf from dist/book1.html using WeasyPrint.

PDF is the print/share-ready *visual* output; the HTML remains the canonical
searchable/copyable text view. WeasyPrint is an optional dependency — if it (or
its native libraries) are unavailable, this script prints clear guidance and
exits non-zero without breaking the rest of the pipeline.
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "dist", "book1.html")
PDF = os.path.join(ROOT, "dist", "book1.pdf")


def main() -> int:
    if not os.path.exists(HTML):
        print(f"{HTML} not found. Run: python scripts/render_book_html.py first",
              file=sys.stderr)
        return 2
    try:
        from weasyprint import HTML as WeasyHTML  # type: ignore
    except Exception as exc:  # pragma: no cover
        print("WeasyPrint is not available:", exc, file=sys.stderr)
        print("\nWeasyPrint is OPTIONAL. Install it (and native deps: "
              "libpango, libcairo, libgdk-pixbuf) with:", file=sys.stderr)
        print("    pip install weasyprint", file=sys.stderr)
        print("The HTML book (dist/book1.html) is the canonical searchable "
              "output and does not require WeasyPrint.", file=sys.stderr)
        return 3

    WeasyHTML(filename=HTML).write_pdf(PDF)
    print(f"wrote {os.path.relpath(PDF, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
