#!/usr/bin/env python3
"""Render dist/book2.html (and content/*/book2 Markdown) from canonical data."""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from saudi_law_corpus.render_html import render  # noqa: E402
from saudi_law_corpus.render_markdown import render_all as render_md  # noqa: E402


def main() -> int:
    for path in render_md(book=2):
        print(f"wrote {os.path.relpath(path, ROOT)}")
    out = render(book=2)
    print(f"wrote {os.path.relpath(out, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
