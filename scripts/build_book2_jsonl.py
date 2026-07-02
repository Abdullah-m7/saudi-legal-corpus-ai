#!/usr/bin/env python3
"""Build data/articles/book2_articles_035_050.jsonl from the canonical JSON."""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from saudi_law_corpus.render_jsonl import build_jsonl  # noqa: E402
from saudi_law_corpus import books  # noqa: E402


def main() -> int:
    n = build_jsonl(book=2)
    out = books.get_book(2).articles_jsonl
    print(f"wrote {os.path.relpath(out, ROOT)} with {n} article chunks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
