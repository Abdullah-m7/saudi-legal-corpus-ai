#!/usr/bin/env python3
"""Refuse to build a manuscript that types a number the analysis owns.

numbers.py removes the class of defect where a figure in prose drifts from the
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
SRC = HERE / "main.tex"

# A measurement, in the shapes results take: 1,234 / 1{,}234 / 35.1 per cent /
# 12.5\%. Years and plain small integers are left alone.
SUSPECT = re.compile(
    r"(?<![\\A-Za-z0-9])"
    r"(\d{1,3}(?:[,{]\S?,?\}?\d{3})+"      # thousands-separated
    r"|\d+\.\d+"                            # any decimal
    r"|\d+\s*(?:per cent|%|\\%))"           # any percentage
)

# Lines that legitimately carry digits: the generated macros are not here, but
# citations and DOIs are.
EXEMPT = re.compile(r"zenodo|doi|orcid|github|ukpga|nisi|http", re.I)


def main():
    if not SRC.exists():
        print("main.tex does not exist yet --- nothing to check")
        return 0
    bad = []
    for n, line in enumerate(SRC.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.split("%")[0]
        if EXEMPT.search(stripped):
            continue
        for m in SUSPECT.finditer(stripped):
            bad.append((n, m.group(1), line.strip()[:78]))
    if bad:
        print(f"{len(bad)} typed measurement(s) in main.tex --- use a macro "
              f"from numbers.tex instead:")
        for n, value, context in bad:
            print(f"  line {n}: {value!r}\n    {context}")
        return 1
    print("no typed measurements in main.tex")
    return 0


if __name__ == "__main__":
    sys.exit(main())
