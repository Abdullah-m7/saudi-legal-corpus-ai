#!/usr/bin/env python3
"""Refuse to build a manuscript that types a number the analysis owns.

make_numbers.py removes the class of defect where a figure in prose drifts from the
figure in the data. It only removes it if the manuscript actually uses the
macros, so this looks for bare digits in the text and asks whether each one is
allowed.

Not every digit is a defect. Years, article and section numbers, footnote
markers and the like are part of citations, not results. What is not allowed is
a digit sequence that looks like a measurement --- a thousands-separated count,
a percentage, or a decimal --- because those are exactly the values that have a
single source, and it is not the manuscript.

    python3 docs/research/comparison_paper/check_numbers.py
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = (HERE / "main.tex", HERE / "cover_letter.tex")

# A measurement, in the shapes results take: 1,234 / 1{,}234 / 35.1 per cent /
# 12.5\%. Years and plain small integers are left alone.
# A LaTeX length is a layout dimension, not a result. `1.5em` inside a
# hangparas environment tripped this check once; excluding lengths keeps the
# guard aimed at prose, which is the only place a measurement can be typed.
LENGTH = re.compile(r"\d*\.?\d+\s*(?:em|ex|pt|bp|cm|mm|in|pc|sp|\\[a-zA-Z]+)")

SUSPECT = re.compile(
    r"(?<![\\A-Za-z0-9])"
    r"(\d{1,3}(?:[,{]\S?,?\}?\d{3})+"      # thousands-separated
    r"|\d+\.\d+"                            # any decimal
    r"|\d+\s*(?:per cent|%|\\%))",          # any percentage
    re.I)   # «98 Per Cent» in a title is still a measurement: an early cover
            # letter kept a stale 98 through a rebuild that moved it to 99,
            # because the pattern was case-sensitive and the title was not.

# Lines that legitimately carry digits: the generated macros are not here, but
# citations and DOIs are.
EXEMPT = re.compile(
    r"zenodo|doi|orcid|github|ukpga|nisi|http"
    # an OSCOLA or Bluebook pinpoint --- «ss 21.3 and 24.3» in a footnote
    # citing a treatise --- is a citation, not a result.
    r"|\bedn\b|\bss?\s\d|LexisNexis|Butterworths", re.I)


# A table cell is where a bare integer is a measurement. `129` in prose is
# probably an article number or a year; `129` in a tabular row is a count that
# something computed, and it belongs in a macro. This was found the way most
# things here were found --- by typing three article counts into a table and
# noticing that every guard passed.
TABLE = re.compile(r"\\begin\{tabular\}.*?\\end\{tabular\}", re.S)
CELL_INT = re.compile(r"(?<![\\A-Za-z0-9.])(\d{2,})(?![A-Za-z0-9.])")


def check_tables(SRC, lines):
    """Bare integers inside a tabular environment, which macros should supply."""
    text = "\n".join(lines)
    bad = []
    for table in TABLE.finditer(text):
        start = text[:table.start()].count("\n") + 1
        for n, line in enumerate(table.group(0).splitlines(), start):
            body = line.split("%")[0]
            if EXEMPT.search(body):
                continue
            # only the value columns. The first field of a row is its label,
            # and «Article 16's field» is a name, not a count.
            for cell in body.split("&")[1:]:
                for m in CELL_INT.finditer(cell):
                    bad.append((n, m.group(1), line.strip()[:78]))
    return bad


def check(SRC):
    if not SRC.exists():
        print(f"{SRC.name} does not exist yet --- nothing to check")
        return 0
    lines = SRC.read_text(encoding="utf-8").splitlines()
    # Only the body. Package options carry lengths --- `margin=2.5cm` is a
    # layout setting, not a result --- and flagging them trains the author to
    # ignore the check, which is worse than not having one.
    start = next((i for i, l in enumerate(lines)
                  if l.strip().startswith("\\begin{document}")), 0)
    bad = []
    for n, line in enumerate(lines[start:], start + 1):
        stripped = line.split("%")[0]
        if EXEMPT.search(stripped):
            continue
        lengths = {m.group(0).strip() for m in LENGTH.finditer(stripped)}
        for m in SUSPECT.finditer(stripped):
            value = m.group(1)
            if any(value in length for length in lengths):
                continue
            bad.append((n, value, line.strip()[:78]))
    bad += check_tables(SRC, lines[start:])
    if bad:
        print(f"{len(bad)} typed measurement(s) in {SRC.name} --- use a macro "
              f"from numbers.tex instead:")
        for n, value, context in bad:
            print(f"  line {n}: {value!r}\n    {context}")
        return 1
    print(f"no typed measurements in {SRC.name}")
    return 0


def main():
    """The letter quotes the paper, so it is checked with the same rule.

    An earlier draft of the cover letter carried two figures from a stale run
    of the analysis. The manuscript could not, because it is typeset from
    generated macros; the letter could, because nothing was watching it.
    """
    return max(check(src) for src in SOURCES)


if __name__ == "__main__":
    sys.exit(main())
