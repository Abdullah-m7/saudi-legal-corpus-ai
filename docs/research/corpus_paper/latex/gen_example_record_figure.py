#!/usr/bin/env python3
"""Render Figure 1 (an example unified-index record) as a PNG.

pdfLaTeX cannot typeset Arabic script, so the example record — whose field
values are verbatim Arabic — is rendered to an image with proper RTL shaping
(arabic_reshaper + python-bidi, Noto fonts) and included via
\\includegraphics. Deterministic over its inputs. Run from the repository
root:

    python3 docs/research/corpus_paper/latex/gen_example_record_figure.py
"""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features

assert features.check("raqm"), "Pillow must be built with libraqm for RTL shaping"

REPO_ROOT = Path(__file__).resolve().parents[4]
INDEX = REPO_ROOT / "data" / "corpus_unified_index" / "corpus_unified_llm_index.jsonl"
OUT = Path(__file__).resolve().parent / "example_record.png"

RECORD_ID = "aawan-regulation-llm-art-001"  # short article: fits a figure

ARABIC_FONT = "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf"
MONO_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

SIZE = 22
LINE_H = 34
PAD = 20
WIDTH = 1100


def find_record():
    with open(INDEX, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            if rec["record_id"] == RECORD_ID:
                return rec
    raise SystemExit(f"record {RECORD_ID} not found")


# Pillow is built with libraqm (asserted above), which shapes and reorders
# Arabic itself from logical-order text via the `direction` argument — no
# presentation-form reshaping is needed (Noto fonts omit those glyphs).


def main():
    rec = find_record()
    # Keep the figure compact: drop the longer generated-metadata lists.
    shown = {
        "record_id": rec["record_id"],
        "corpus": rec["corpus"],
        "law_id": rec["law_id"],
        "law_component": rec["law_component"],
        "law_title_ar": rec["law_title_ar"],
        "article_number": rec["article_number"],
        "keywords_ar": rec["keywords_ar"][:3] + ["..."],
        "search_queries_ar": [rec["search_queries_ar"][0], "..."],
        "text_ar": rec["text_ar"],
        "text_status": rec["text_status"],
        "source_layer": rec["source_layer"],
    }

    mono = ImageFont.truetype(MONO_FONT, SIZE)
    arabic = ImageFont.truetype(ARABIC_FONT, SIZE)

    def has_arabic(s):
        return any("؀" <= ch <= "ۿ" for ch in s)

    height = PAD * 2 + LINE_H * (len(shown) + 2)
    img = Image.new("RGB", (WIDTH, height), "white")
    d = ImageDraw.Draw(img)

    def draw_segments(x, y, segments):
        # segments: list of (text, font, color, direction) laid out
        # left-to-right; raqm shapes each segment internally.
        for text, font, color, direction in segments:
            d.text((x, y), text, font=font, fill=color, direction=direction)
            x += d.textlength(text, font=font, direction=direction)

    y = PAD
    d.text((PAD, y), "{", font=mono, fill="black")
    y += LINE_H
    items = list(shown.items())
    blue = (0, 90, 160)
    for i, (key, value) in enumerate(items):
        comma = "," if i < len(items) - 1 else ""
        prefix = f'  "{key}": '
        if isinstance(value, list):
            joined = "، ".join(str(v) for v in value)
        else:
            joined = str(value)
        if has_arabic(joined):
            # Draw JSON punctuation in mono (LTR) and the Arabic value as its
            # own RTL segment, so bidi reordering never crosses the quotes.
            segments = [
                (prefix, mono, blue, "ltr"),
                ('"', mono, "black", "ltr"),
                (joined, arabic, "black", "rtl"),
                ('"' + comma, mono, "black", "ltr"),
            ]
        else:
            raw = json.dumps(value, ensure_ascii=False)
            segments = [(prefix, mono, blue, "ltr"),
                        (raw + comma, mono, "black", "ltr")]
        draw_segments(PAD, y, segments)
        y += LINE_H
    d.text((PAD, y), "}", font=mono, fill="black")

    img.save(OUT)
    print(f"wrote {OUT} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
