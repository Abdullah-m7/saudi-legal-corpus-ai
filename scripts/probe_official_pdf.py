#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Decide whether an official PDF's Arabic can be read verbatim.

WHY THIS EXISTS. The gazette is the only source that hands this corpus clean,
server-rendered Arabic at scale, and its archive is exhausted. Everything the
issuing authorities publish below it — the CMA's regulations, the ministries'
decisions and circulars, the municipal requirements — is published as PDF. So
whether the corpus can grow further is, concretely, whether those PDFs can be
read verbatim. That is not a matter of opinion and it is not uniform across
files, so it is measured here, per file.

THREE INDEPENDENT DEFECTS. A file can carry any combination of them, and keeping
them apart is the whole point of this probe:

  LAM-MEEM  the definite article's ligature. Sound maps put «المادة» on the page
            as «المادة»; broken ones give «املادة», «املتطلبات», «العشرني».
  LAM-ALEF  the other ligature Arabic cannot do without. Sound maps give «لائحة»
            and «الالتزام»; broken ones give «الئحة» and «االلتزام».
  ORDER     the order the runs come out in. Sound order reads a justified Arabic
            line right-to-left as printed; broken order interleaves the runs, so
            every character is correct and the sentence is not.

Verdicts:

  READABLE       both ligatures sound AND order sound — the plain text layer IS
                 the text, and may be quoted
  BROKEN_ORDER   ligatures sound, runs interleaved
  BROKEN_CMAP    a ligature map transposes characters (order is not separately
                 judged, because a transposed reading cannot be ordered against
                 anything)
  IMAGE_SCAN     no text layer at all; the page is a picture of the document.
                 Only OCR could read it, and OCR is a visual reading — this
                 corpus admits those only with an explicit per-record disclosure.
  UNDECIDED      too little Arabic to judge

THREE MEASUREMENT MISTAKES WORTH KEEPING, because each would have produced a
confident wrong answer.

1. The first version looked for «املادة», the transposed form of the commonest
   word in a law, and pronounced six municipal files clean that are not. They
   simply do not use the word «المادة»: they are drafted in «متطلبات» and
   «اشتراطات», and their damage shows as «املتطلبات». A marker check is only ever
   as good as its marker. So the map test below names no words — it measures the
   DEFINITE ARTICLE, which every Arabic legal document is full of: in sound text
   a token opening on «ا» has «ل» at position 1; where the lam ligature maps to
   the wrong pair the «ل» lands at position 2. The ratio does not depend on the
   drafter's vocabulary.

2. The second version stopped at the lam-meem test and would have called four CMA
   files admissible. One of them — «لائحة الإبلاغ عن مخالفات نظام السوق المالية» — is a
   regulation this corpus ALREADY holds verbatim from the gazette, so it can
   SCORE a reading instead of arguing about one. Its maps are sound (transposed
   ratio 0.063). Its plain text layer nevertheless reproduces the corpus's own
   articles at median 0.62, and PyMuPDF's position-sorted reading at 0.75,
   because the runs are interleaved. Only a geometry-aware reading reaches 0.99
   — and 0.99 is not 1.00. Sound maps are not readability. Hence the order test:
   read the page a second time from its own geometry (runs sharing a baseline
   are one visual line; within it the rightmost run is read first) and require
   the two readings to agree. Two independent readings agreeing is evidence;
   one reading alone is not.

3. The third version added the order test and still passed two CMA files whose
   text says «الئحة» for «لائحة» and «االستثمار» for «الاستثمار». The LAM-ALEF
   ligature was transposed, and the lam-meem test cannot see it: both the sound
   and the transposed reading of «الاستثمار» open on «ا», so neither counts as
   normal or as transposed. It is caught instead by the fact that sound Arabic is
   full of «لا» and a transposed file has almost none — measured, sound files
   score 0.000-0.016 and damaged ones 0.203-1.000.

The pattern across all three mistakes is the same: every one was found by reading
the extracted text and not by trusting a ratio. A ratio only ever answers the
question it was built to ask.

Usage:  python3 scripts/probe_official_pdf.py [--json] FILE.pdf [FILE.pdf ...]

Read-only. Requires PyMuPDF; exits 2 with a clear message if it is absent.
"""
from __future__ import annotations

import json
import re
import sys

# A page with less Arabic than this is not carrying a text layer worth reading.
MIN_ARABIC_PER_PAGE = 40
# Above this share of transposed definite articles the font's maps are wrong.
# The measured separation is wide — sound files score 0.000-0.063 and damaged
# ones 0.372-0.568 — so the threshold sits in a gap far wider than it needs.
TRANSPOSED_RATIO = 0.25
# Fewer definite articles than this and the ratio is not evidence of anything.
MIN_ARTICLE_TOKENS = 30
# Above this share of «اا» against «لا» the lam-alef ligature is transposed.
# Sound files measure 0.000-0.016; damaged ones 0.203-1.000.
LAM_ALEF_RATIO = 0.10
# Fewer of either form than this and the ratio is not evidence of anything.
MIN_LAM_ALEF_TOKENS = 20
# Two readings this close are the same reading; below it the order is ambiguous
# and the file cannot be quoted from.
ORDER_AGREEMENT = 0.99
# Baseline tolerance, in points, for calling two runs one visual line.
Y_TOL = 6.0

ARABIC = re.compile(r"[ء-ي]")
TOKEN = re.compile(r"[ء-ي]{3,}")


def _norm(s):
    for a, b in (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ى", "ي"), ("ة", "ه")):
        s = s.replace(a, b)
    return re.sub(r"[^ء-ي]", "", s)


def _geometric_text(page):
    """The page read from its own geometry: RTL within each baseline."""
    runs = []
    for block in page.get_text("rawdict")["blocks"]:
        if block.get("type"):
            continue
        for line in block.get("lines", []):
            for span in line["spans"]:
                txt = "".join(c["c"] for c in span.get("chars", []))
                if txt.strip():
                    x0, y0, x1, y1 = span["bbox"]
                    runs.append(((y0 + y1) / 2.0, x1, txt))
    runs.sort(key=lambda r: r[0])
    out, cur = [], []
    for r in runs:
        if cur and r[0] - cur[0][0] > Y_TOL:
            cur.sort(key=lambda x: -x[1])
            out.append("".join(x[2] for x in cur))
            cur = []
        cur.append(r)
    if cur:
        cur.sort(key=lambda x: -x[1])
        out.append("".join(x[2] for x in cur))
    return "\n".join(out)


def classify(path):
    """-> {kind, pages, arabic_chars, transposed_ratio, order_agreement}"""
    import fitz                                                   # noqa: PLC0415

    doc = fitz.open(path)
    plain = "\n".join(p.get_text() for p in doc)
    pages = len(doc)
    arabic = len(ARABIC.findall(plain))
    row = {"pages": pages, "arabic_chars": arabic,
           "transposed_ratio": 0.0, "lam_alef_ratio": 0.0, "order_agreement": None}
    if arabic < MIN_ARABIC_PER_PAGE * pages:
        return dict(row, kind="IMAGE_SCAN")

    normal = transposed = 0
    for tok in TOKEN.findall(plain):
        if tok[0] != "ا":
            continue
        if tok[1] == "ل":
            normal += 1
        elif tok[2] == "ل":
            transposed += 1
    total = normal + transposed
    if total < MIN_ARTICLE_TOKENS:
        return dict(row, kind="UNDECIDED")
    ratio = transposed / total
    row["transposed_ratio"] = round(ratio, 3)
    if ratio > TRANSPOSED_RATIO:
        return dict(row, kind="BROKEN_CMAP")

    # A test that cannot decide must not be read as a pass. «تعليمات تصريح تجربة
    # التقنية المالية» carries 19 lam-alef tokens, one short of the floor, and
    # twelve of them are transposed — skipping the test would have declared it
    # readable on no evidence at all.
    lam_alef = len(re.findall("لا", plain))
    alef_alef = len(re.findall("اا", plain))
    if lam_alef + alef_alef < MIN_LAM_ALEF_TOKENS:
        return dict(row, kind="UNDECIDED")
    la_ratio = alef_alef / (lam_alef + alef_alef)
    row["lam_alef_ratio"] = round(la_ratio, 3)
    if la_ratio > LAM_ALEF_RATIO:
        return dict(row, kind="BROKEN_CMAP")

    # Both ligatures are sound. Now ask whether the ORDER is, by reading the page again
    # from its geometry and requiring the two readings to agree.
    a = _norm(plain)
    b = _norm("\n".join(_geometric_text(p) for p in doc))
    if not a or not b:
        return dict(row, kind="UNDECIDED")
    import difflib                                                # noqa: PLC0415
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    agree = sum(m.size for m in sm.get_matching_blocks()) / max(len(a), len(b))
    row["order_agreement"] = round(agree, 4)
    return dict(row, kind="READABLE" if agree >= ORDER_AGREEMENT else "BROKEN_ORDER")


def main(argv):
    try:
        import fitz                                               # noqa: F401,PLC0415
    except ImportError:
        print("probe_official_pdf: PyMuPDF is required (pip install pymupdf)",
              file=sys.stderr)
        return 2
    as_json = "--json" in argv
    paths = [a for a in argv if a != "--json"]
    if not paths:
        print(__doc__.strip().splitlines()[0])
        print("usage: probe_official_pdf.py [--json] FILE.pdf ...")
        return 1
    out = []
    for p in paths:
        try:
            row = dict(classify(p), path=p)
        except Exception as exc:                                  # noqa: BLE001
            row = {"path": p, "kind": "ERROR", "error": str(exc)}
        out.append(row)
        if not as_json:
            print("%-13s pages=%-4s arabic=%-7s lam-meem=%-6s lam-alef=%-6s order=%-7s %s"
                  % (row.get("kind"), row.get("pages", "-"),
                     row.get("arabic_chars", "-"), row.get("transposed_ratio", "-"),
                     row.get("lam_alef_ratio", "-"), row.get("order_agreement"), p))
    if as_json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
