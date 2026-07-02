#!/usr/bin/env python3
"""Build data/articles/book1_articles_001_034.jsonl from the canonical JSON."""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from saudi_law_corpus.render_jsonl import build_jsonl, OUT_JSONL  # noqa: E402


def main() -> int:
    n = build_jsonl()
    print(f"wrote {os.path.relpath(OUT_JSONL, ROOT)} with {n} article chunks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
