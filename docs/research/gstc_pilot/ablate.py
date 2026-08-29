#!/usr/bin/env python3
"""Apportion the score between the canonicalisation layer and the grammar.

The extractor scored 0.0 per cent on this source and 90.9 on the ministry's.
The obvious explanations -- "the parser is tuned to one publisher", "the PDFs
are bad" -- are both plausible and neither was measured. This switches each
canonicalisation rule and each grammar stage off in turn and reports what the
score does, so the gap is apportioned rather than asserted.

Read the rows as contribution, not as importance: a rule whose removal costs
nothing here may still matter on a source not yet seen.

    python3 ablate.py            # table
    python3 ablate.py --json     # for numbers.tex
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "canon"))
sys.path.insert(0, str(HERE.parent / "citation"))
sys.path.insert(0, str(HERE))
import canonical                                          # noqa: E402
import grammar                                            # noqa: E402
from evaluate import score                                # noqa: E402

REPORTED = ("detection", "article", "paragraph", "instrument", "segment",
            "exact")


def run(verbose=False):
    rows = []

    def add(name, result):
        rows.append((name, result))
        if verbose:
            m = result["metrics"]
            print(f"  {name:38} exact {m['exact']['pct']}", flush=True)

    full = score(list(grammar.STAGES), None)
    add("baseline: everything on", full)

    for rule in canonical.RULES:
        kept = [r for r in canonical.RULES if r != rule]
        add(f"canonicalisation without {rule}",
            score(list(grammar.STAGES), kept))
    add("canonicalisation off entirely", score(list(grammar.STAGES), []))

    for stage in grammar.STAGES:
        if stage in ("detection", "article"):
            continue        # switching these off leaves nothing to score
        kept = [s for s in grammar.STAGES if s != stage]
        add(f"grammar without {stage}", score(kept, None))
    return rows


def table(rows):
    base = rows[0][1]["metrics"]
    width = max(len(name) for name, _ in rows)
    head = " ".join(f"{k[:9]:>9}" for k in REPORTED)
    print(f"{'':{width}}  {head}   exact vs baseline")
    for name, result in rows:
        m = result["metrics"]
        cells = " ".join(
            f"{(m[k]['pct'] if m[k]['pct'] is not None else 0):9.1f}"
            for k in REPORTED)
        delta = (m["exact"]["pct"] or 0) - (base["exact"]["pct"] or 0)
        mark = "" if name.startswith("baseline") else f"{delta:+6.1f}"
        print(f"{name:{width}}  {cells}   {mark}")


if __name__ == "__main__":
    rows = run(verbose="--json" not in sys.argv)
    if "--json" in sys.argv:
        print(json.dumps(
            [{"condition": n,
              "metrics": {k: r["metrics"][k] for k in REPORTED}}
             for n, r in rows], ensure_ascii=False, indent=1))
    else:
        table(rows)
