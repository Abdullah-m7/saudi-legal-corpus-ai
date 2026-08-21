#!/usr/bin/env python3
"""Generate the article highlights, and enforce the journal's limits.

Elsevier requires 3 to 5 bullet points, each at most 85 characters including
spaces, in a separate editable file whose name contains "highlights". Eighty-
five characters is tight enough that a sentence written to fit will quietly
lose a qualifier, so the count is checked here rather than in a word processor,
and the numbers come from the analysis like every other figure in this paper.

    python3 docs/research/comparison_paper/make_highlights.py
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "uk_analysis_results.json"
OUT = HERE / "highlights.txt"
LIMIT = 85


def main():
    r = json.loads(RESULTS.read_text(encoding="utf-8"))
    u = r["unincorporated"]
    st = u["flagged_effects_by_state"]
    flagged = sum(st.values())
    factor = round(flagged / u["effects_requiring_application"])
    prospective = st["prospective"] / flagged * 100

    lines = [
        f"{flagged:,} UK amendments flagged as unapplied; only "
        f"{st['in_force']} are actually in force.",
        f"Reading the flag alone overstates the backlog {factor}-fold.",
        f"{prospective:.0f}% are enacted but not yet commenced, so withholding "
        f"them is correct.",
        f"No amendment has gone unapplied beyond the publisher's "
        f"3-month target.",
        "The correcting field is published, but costs more to reach than the "
        "misleading one.",
    ]
    over = [(i + 1, len(l), l) for i, l in enumerate(lines) if len(l) > LIMIT]
    for i, n, l in over:
        print(f"  highlight {i}: {n} characters, {n - LIMIT} over\n    {l}")
    if over:
        sys.exit(f"{len(over)} highlight(s) exceed {LIMIT} characters")
    if not 3 <= len(lines) <= 5:
        sys.exit(f"{len(lines)} highlights; the journal requires 3 to 5")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for i, l in enumerate(lines, 1):
        print(f"  {i}. [{len(l):>2}] {l}")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
