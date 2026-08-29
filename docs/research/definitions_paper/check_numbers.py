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
    # a pinpoint in a footnote citing a treatise --- «ss 21.3 and 24.3» in
    # OSCOLA, «\S\S~21.3, 24.3» in Bluebook --- is a citation, not a result
    r"|\bedn\b|\bss?\s\d|\\S\\?S?~?\d|LexisNexis|Butterworths"
    r"|\bed\.\s\d{4}|\(\d{4}\)\.?$", re.I)


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


def generated_values():
    """Every value numbers.tex carries, as it would be typed in prose.

    The pattern above catches a measurement by its shape --- a separator, a
    decimal, a percent sign. It cannot catch «290 instruments», because that
    looks like an article number or a year. But if a bare integer in prose
    equals a figure the analysis owns, it is that figure, typed. This rule
    found a cover letter still carrying 290 after the manuscript had been
    corrected to 291 --- the letter's own guard had passed twice.
    """
    src = HERE / "numbers.tex"
    if not src.exists():
        return set()
    out = set()
    for raw in re.findall(r"\\newcommand\{\\\w+\}\{([^{}]*(?:\{,\}[^{}]*)*)\}",
                          src.read_text(encoding="utf-8")):
        plain = raw.replace("{,}", "")
        if plain.isdigit() and len(plain) >= 3:
            out.add(plain)
            out.add(f"{int(plain):,}")
    return out


# «article 721» is a provision's number and «106 J. Pol. Econ.» is a volume,
# and both can coincide with a real measurement --- the civil code's last
# article is its 721st, and the corpus cites 106 instruments. A number
# introduced by an article or section word, or sitting in a citation, is not a
# result however much it looks like one.
CITATION_CONTEXT = re.compile(r"\\bjournal\{|\\bbook\{|\\btitle\{")
NOT_A_RESULT = re.compile(
    r"(?:art|arts|article|articles|s|ss|sec|secs|section|sections|para|paras|"
    r"no|nos|number|reg|regs|rule|rules|ch|chs|chapter|clause)\.?~?\s*$", re.I)

BARE = re.compile(r"(?<![\\A-Za-z0-9.,])([\d,]{3,})(?![A-Za-z0-9.])")


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
    owned = generated_values()
    for n, line in enumerate(lines[start:], start + 1):
        body = line.split("%")[0]
        if EXEMPT.search(body):
            continue
        if CITATION_CONTEXT.search(body):
            continue
        for m in BARE.finditer(body):
            if m.group(1) in owned and not NOT_A_RESULT.search(body[:m.start()]):
                bad.append((n, m.group(1), line.strip()[:78]))
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
