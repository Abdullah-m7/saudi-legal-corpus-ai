#!/usr/bin/env python3
"""Generate numbers.tex for the HILJ article.

The measurements are the same measurements. Only the article is new, so this
does not recompute anything: it re-runs the generator that paper 7 owns and
copies its output. One source for a figure, and it is still not this file.

Copying rather than re-deriving is the point. Two scripts computing «the same»
share from the same JSON is how two papers come to disagree in print.
"""

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "applied_law_paper"


def main():
    r = subprocess.run([sys.executable, str(SRC / "make_numbers.py")],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"the paper 7 generator failed:\n{r.stdout[-2000:]}{r.stderr[-2000:]}")
    shutil.copy2(SRC / "numbers.tex", HERE / "numbers.tex")
    n = (HERE / "numbers.tex").read_text(encoding="utf-8").count("newcommand")
    print(f"numbers.tex: {n} values, regenerated from the analysis and copied")


if __name__ == "__main__":
    main()
