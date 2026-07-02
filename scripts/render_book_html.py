#!/usr/bin/env python3
"""Render dist/book1.html from canonical data.

Rebuilds the JSONL first (cheap) so derived artifacts stay in sync, then renders
the HTML book. Uses Jinja2 if available, otherwise a pure-Python fallback.
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from saudi_law_corpus.render_html import render  # noqa: E402


def main() -> int:
    out = render()
    print(f"wrote {os.path.relpath(out, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
