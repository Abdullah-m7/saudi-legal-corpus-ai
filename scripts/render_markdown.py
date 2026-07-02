#!/usr/bin/env python3
"""Render content/{ar,zh,bilingual} Markdown books from canonical data."""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from saudi_law_corpus.render_markdown import render_all  # noqa: E402


def main() -> int:
    for path in render_all():
        print(f"wrote {os.path.relpath(path, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
