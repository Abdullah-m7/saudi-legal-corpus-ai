#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-derive the Arabic text of the CMA Rules on the Offer of Securities and
Continuing Obligations from the Authority's own PDF, so that this track's
"verbatim" claim can be independently re-checked rather than merely asserted.

This is a REPRODUCIBILITY tool, not part of the corpus build. The committed
corpus artifact is
    sources/cma_securities_offering_rules/law/official_source/
    cma_securities_offering_rules_official_source.json
and scripts/gen_cma_securities_offering_rules_track.py reads only that file.

WHY A SPECIAL EXTRACTOR IS NEEDED
    A plain `pdftotext` (or any ordinary extractor) of this file produces
    unusable Arabic. The PDF places every glyph individually in VISUAL
    (left-to-right) order, and its fonts use Arabic ligature glyphs whose
    ToUnicode entries expand to 2-3 letters. When an extractor reverses the
    visual run to recover logical order it also reverses the letters INSIDE
    each ligature, so المملكة comes out اململكة, المالية comes out املالية and
    والالتزامات comes out وااللتزامات. Combining marks (zero advance) and
    digit runs are scattered at the same time.

WHAT THIS SCRIPT DOES (all of it from the file's own data, nothing guessed)
    Working from MuPDF's raw glyph trace, which reports for each glyph drawn
    its Unicode expansion, its glyph id and its true ink box:
      1. LIGATURES  A ligature's continuation characters carry glyph id -1 and
         a degenerate box at the lead glyph's origin. They are rejoined to the
         lead glyph in the order the font's OWN ToUnicode declares, which is
         logical order. (14 ToUnicode streams in this file declare 50 distinct
         multi-character mappings: لا لأ لإ لآ لم لح له لج لخ لى لمح لمج تم
         سم بح تح تخ مج مح يخ ين حم في ير ...)
      2. TASHKEEL   Zero-advance combining marks are re-attached to the base
         glyph whose ink their ink overlaps (max horizontal overlap; nearest
         centre if none). Where the fonts draw the same mark twice on one base
         (a combined shadda+tanween glyph plus a standalone tanween glyph at
         the same origin) the exact duplicate is collapsed.
      3. DIRECTION  Clusters are ordered right-to-left by x, then maximal
         Latin/digit runs are re-reversed to left-to-right.
      4. JUSTIFICATION FILLERS  The fonts pad justified lines with elongation
         glyphs. Some map to U+0640 TATWEEL; others map (wrongly) to U+0627
         ALEF while drawing at ~0.10em against ~0.19-0.24em for a real alef.
         Both are dropped -- 173 glyphs over the 296-page file. Without this,
         المشاركين is stored as المشااركين.
      5. HEADINGS   Part / Chapter / Article headings are the only lines the
         PDF sets in CMA blue or at 20pt, so heading lines are marked with a
         leading U+0001 in the output. That is what lets multi-line article
         titles be reassembled without guessing.

    No word list, no dictionary, no spell-correction, and no use of the English
    edition of the same instrument. Every character emitted is the font's own
    ToUnicode value for a glyph actually drawn on the page.

VERIFICATION THIS OUTPUT ALREADY PASSED
    All 112 articles were compared word-by-word against the Umm Al-Qura
    official gazette text; 105 came out word-identical after a normalisation
    that strips tashkeel, unifies alef/ya/ta-marbuta and ignores punctuation
    and numeral presentation. The 7 that differ are recorded individually in
    the source artifact's known_unresolved_discrepancies.

USAGE
    Fetch the source PDF (not stored in this repository):
      curl -L -o rules_ar.pdf \\
        https://cma.gov.sa/RulesRegulations/Regulations/Documents/\\
RULES_ON_THE_OFFER_OF_SECURITIES_AND_CONTINUING_OBLIGATIONS_ar2026.pdf
    then
      python scripts/extract_cma_securities_offering_rules_pdf_text.py \\
        rules_ar.pdf -o rules_ar.txt

    Articles live on pages 11-98; pages 99-296 are the 38 annexes, which this
    track does not ingest.

REQUIREMENTS
    PyMuPDF (optional dependency; the corpus build does not need it). Note that
    PyMuPDF 1.28's get_texttrace() has a refcount bug that aborts the
    interpreter after enough pages of this file, so pages are processed in
    small subprocess batches; that is a workaround, not part of the method.
"""
from __future__ import annotations

import argparse
import collections
import os
import re
import subprocess
import sys

MARK_LO, MARK_HI = 0x064B, 0x0652
EXTRA_MARKS = {0x0670, 0x0653, 0x0654, 0x0655, 0x06DF, 0x06E2}
LTR = re.compile(r"[0-9A-Za-z]")
HEADING_MARK = "\x01"
KASHIDA_MAX_EM = 0.15
BATCH = 20

_dropped: list[str] = []


def _is_mark(u: int) -> bool:
    return MARK_LO <= u <= MARK_HI or u in EXTRA_MARKS


def _clusters(page):
    """Glyph clusters as (y, text, x0, x1, kind, colour, size)."""
    out, seen = [], set()
    trace = page.get_texttrace()
    spans = []
    for sp in trace:
        size = float(sp["size"]) or 1.0
        col = (tuple(round(float(x), 3) for x in sp["color"])
               if sp.get("color") else (0.0, 0.0, 0.0))
        row = []
        for c in sp["chars"]:
            u, gid = int(c[0]), int(c[1])
            x0, x1 = float(c[3][0]), float(c[3][2])
            if u == 0x0627 and gid != -1 and (x1 - x0) / size < KASHIDA_MAX_EM:
                _dropped.append("alef-shaped kashida")
                continue
            if u == 0x0640 and gid != -1:
                _dropped.append("tatweel")
                continue
            row.append((u, gid, float(c[2][1]), x0, x1))
        spans.append((col, size, row))
    del trace
    for col, size, chars in spans:
        i, n = 0, len(chars)
        while i < n:
            u, _gid, oy, x0, x1 = chars[i]
            txt = chr(u)
            j = i + 1
            while j < n and chars[j][1] == -1:      # ligature continuation
                txt += chr(chars[j][0])
                j += 1
            y = round(oy, 1)
            kind = "mark" if all(_is_mark(ord(ch)) for ch in txt) else "base"
            key = (y, round(x0, 2), round(x1, 2), txt)
            if key not in seen:                      # headings are drawn twice
                seen.add(key)
                out.append((y, txt, x0, x1, kind, col, size))
            i = j
    return out


def _rows(clusters, tol=1.2):
    rows = collections.defaultdict(list)
    canon, cur = {}, None
    for y in sorted({c[0] for c in clusters}):
        if cur is None or abs(y - cur) > tol:
            cur = y
        canon[y] = cur
    for c in clusters:
        rows[canon[c[0]]].append(c)
    return rows


def _is_heading(items) -> bool:
    bases = [c for c in items if c[4] == "base" and c[1].strip()]
    if not bases:
        return False
    blue = sum(1 for c in bases if c[5] != (0.0, 0.0, 0.0))
    big = sum(1 for c in bases if c[6] >= 18.0)
    return blue > 0.6 * len(bases) or big > 0.6 * len(bases)


def _line(items) -> str:
    bases = [c for c in items if c[4] == "base"]
    marks = [c for c in items if c[4] == "mark"]
    bases.sort(key=lambda c: -c[2])
    texts = [c[1] for c in bases]
    for m in marks:
        centre = (m[2] + m[3]) / 2.0
        best, best_score = None, None
        for idx, b in enumerate(bases):
            overlap = min(m[3], b[3]) - max(m[2], b[2])
            score = ((0, -overlap) if overlap > 0
                     else (1, min(abs(centre - b[2]), abs(centre - b[3]))))
            if best_score is None or score < best_score:
                best_score, best = score, idx
        if best is None:
            continue
        cur = texts[best]
        for ch in m[1]:
            if ch not in cur[1:]:                    # collapse duplicate marks
                cur += ch
        texts[best] = cur
    out, i, n = [], 0, len(texts)
    while i < n:
        if LTR.match(texts[i]):
            j, last = i, i
            while j < n:
                if LTR.match(texts[j]):
                    last, j = j, j + 1
                elif texts[j] in "/-.,:" and j + 1 < n and LTR.match(texts[j + 1]):
                    j += 1
                else:
                    break
            out.extend(reversed(texts[i:last + 1]))
            i = last + 1
        else:
            out.append(texts[i])
            i += 1
    return "".join(out)


def page_text(page) -> str:
    rows = _rows(_clusters(page))
    lines = []
    for y in sorted(rows):
        t = _line(rows[y]).strip()
        if t:
            lines.append((HEADING_MARK if _is_heading(rows[y]) else "") + t)
    return "\n".join(lines)


def _run_range(pdf, out, lo, hi):
    import fitz
    doc = fitz.open(pdf)
    hi = min(hi, doc.page_count)
    with open(out, "w", encoding="utf-8") as f:
        for pno in range(lo, hi):
            one = fitz.open()
            one.insert_pdf(doc, from_page=pno, to_page=pno)
            f.write("===== PAGE %d =====\n%s\n\n" % (pno + 1, page_text(one[0])))
            one.close()
    sys.stderr.write("DROPPED %s\n" % dict(collections.Counter(_dropped)))


def main() -> int:
    ap = argparse.ArgumentParser(description="Re-derive the Arabic text of the CMA "
                                             "securities-offering rules from the "
                                             "Authority's own PDF.")
    ap.add_argument("pdf")
    ap.add_argument("-o", "--out", default="cma_securities_offering_rules_ar.txt")
    ap.add_argument("--from-page", type=int, default=0, help="0-based, inclusive")
    ap.add_argument("--to-page", type=int, default=10 ** 6, help="0-based, exclusive")
    ap.add_argument("--worker", nargs=2, metavar=("LO", "HI"),
                    help=argparse.SUPPRESS)
    args = ap.parse_args()

    if not os.path.exists(args.pdf):
        print("PDF not found: %s" % args.pdf, file=sys.stderr)
        return 2
    try:
        import fitz  # noqa: F401
    except Exception:
        print("PyMuPDF is not installed. Install with: pip install pymupdf\n"
              "(This is an optional reproducibility tool; the corpus build does "
              "not depend on it.)", file=sys.stderr)
        return 3

    if args.worker:
        _run_range(args.pdf, args.out, int(args.worker[0]), int(args.worker[1]))
        return 0

    import fitz
    total = min(fitz.open(args.pdf).page_count, args.to_page)
    parts, tally = [], collections.Counter()
    lo = args.from_page
    while lo < total:
        hi = min(lo + BATCH, total)
        part = "%s.part%04d" % (args.out, lo)
        spans = [(lo, hi)]
        r = subprocess.run([sys.executable, os.path.abspath(__file__), args.pdf,
                            "-o", part, "--worker", str(lo), str(hi)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            # PyMuPDF 1.28 refcount abort: retry this batch one page per process.
            spans = [(k, k + 1) for k in range(lo, hi)]
            open(part, "w", encoding="utf-8").close()
            for a, b in spans:
                sub = "%s.p%04d" % (args.out, a)
                r = subprocess.run([sys.executable, os.path.abspath(__file__), args.pdf,
                                    "-o", sub, "--worker", str(a), str(b)],
                                   capture_output=True, text=True)
                if r.returncode != 0:
                    print("FAILED on page %d:\n%s" % (a + 1, r.stderr[-800:]),
                          file=sys.stderr)
                    return 4
                with open(part, "a", encoding="utf-8") as f:
                    f.write(open(sub, encoding="utf-8").read())
                os.remove(sub)
                for m in re.finditer(r"DROPPED (\{.*\})", r.stderr):
                    tally.update(eval(m.group(1)))  # noqa: S307 - our own output
        else:
            for m in re.finditer(r"DROPPED (\{.*\})", r.stderr):
                tally.update(eval(m.group(1)))      # noqa: S307
        parts.append(part)
        lo = hi

    with open(args.out, "w", encoding="utf-8") as f:
        for p in parts:
            f.write(open(p, encoding="utf-8").read())
            os.remove(p)
    print("wrote %s (%d pages); justification-filler glyphs dropped: %s"
          % (args.out, total - args.from_page, dict(tally)))
    print("Heading lines are prefixed with U+0001. Articles: pages 11-98.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
