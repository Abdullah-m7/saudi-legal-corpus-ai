#!/usr/bin/env python3
"""The evaluation matrix: every stage, every set, one table.

This is the artefact the claims rest on. A single number for "the extractor"
is what let 90.9 per cent on one publisher stand in for a capability, and what
made 0.0 on another look like a fact about tribunals rather than about PDFs.

    python3 matrix.py                # from the per-set evaluation files
    python3 matrix.py --recompute    # re-derive them first
    python3 matrix.py --json         # matrix.json, for numbers.tex
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import evaluate                                          # noqa: E402

ROWS = ("detection", "article", "paragraph", "instrument", "segment", "exact")
ORDER = ("gstc", "gstc_test", "moj", "moj_test")
CACHED = {"gstc": "dev_evaluation.json",
          "gstc_test": "gstc_test_evaluation.json",
          "moj": "moj_evaluation.json",
          "moj_test": "moj_test_evaluation.json"}

# What each number is. gstc_test was a held-out estimate once, at freeze
# 3412fdf, where it read 27.7 per cent exact. It then informed the fix to the
# gazetteer's name-trimming rule, and the figure it carries now is a
# development number wearing a held-out set's clothes. Recording that in the
# artefact is the only thing that keeps the distinction alive after the
# session that drew it.
STATUS = {
    "gstc": "development",
    "gstc_test": "NO LONGER HELD OUT -- informed the name-frequency fix; the "
                 "held-out estimate was 27.7 exact at freeze 3412fdf",
    "moj": "development",
    "moj_test": "held out; opened once at freeze 8f55561",
}


def run(recompute=False):
    """Read the per-set evaluations, or re-derive them.

    Recomputing all four in one process parses 200 ministry judgments and five
    megabyte-scale digests, to restate numbers each set has already written
    down. The cached files come from `evaluate.py --set X --json`.
    """
    out = {}
    for name in ORDER:
        spec = json.loads(evaluate.SETS[name].read_text(encoding="utf-8"))
        cached = HERE / CACHED[name]
        if recompute or not cached.exists():
            result = evaluate.score(which=name)
        else:
            result = json.loads(cached.read_text(encoding="utf-8"))
        out[name] = {
            "source": spec.get("source", "GSTC tax and customs digests"),
            "status": STATUS[name],
            "documents": len(spec["documents"]),
            "frameSize": spec["frameSize"],
            "sampled": spec["sampled"],
            "splitUnit": spec["splitUnit"],
            "metrics": {k: result["metrics"][k] for k in ROWS},
        }
    return out


def table(m):
    width = max(len(r) for r in ROWS) + 2
    print(f"{'':{width}}" + "".join(f"{n:>26}" for n in m))
    for row in ROWS:
        cells = ""
        for n in m:
            d = m[n]["metrics"][row]
            cells += (f"{d['correct']:>4}/{d['of']:<4} {d['pct']:5.1f} "
                      f"[{d['ci95'][0]:4.1f},{d['ci95'][1]:5.1f}]")
        print(f"{row:{width}}{cells}")
    print()
    for n in m:
        d = m[n]
        print(f"{n}: {d['documents']} documents ({d['splitUnit']} split), "
              f"frame {d['frameSize']:,}, sampled {d['sampled']}")
        print(f"{' ' * (len(n) + 2)}{d['status']}")


if __name__ == "__main__":
    m = run("--recompute" in sys.argv)
    if "--json" in sys.argv:
        (HERE / "matrix.json").write_text(
            json.dumps(m, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
        print(json.dumps(m, ensure_ascii=False, indent=1))
    else:
        table(m)
