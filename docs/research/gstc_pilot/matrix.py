#!/usr/bin/env python3
"""The evaluation matrix: every stage, every source, one run.

This is the artefact the claims rest on. A single number for "the extractor"
is what let a 90.9 per cent on one publisher stand in for a capability, and
what made a 0.0 per cent on another look like a fact about tribunals rather
than a fact about PDFs.

    python3 matrix.py            # table
    python3 matrix.py --json     # matrix.json, for numbers.tex
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import evaluate                                          # noqa: E402

ROWS = ("detection", "article", "paragraph", "instrument", "segment", "exact")


def run():
    out = {}
    for name in sorted(evaluate.SETS):
        spec = json.loads(evaluate.SETS[name].read_text(encoding="utf-8"))
        result = evaluate.score(which=name)
        out[name] = {
            "source": spec.get("source", "GSTC tax and customs digests"),
            "documents": len(spec["documents"]),
            "frameSize": spec["frameSize"],
            "sampled": spec["sampled"],
            "splitUnit": spec["splitUnit"],
            "metrics": {k: result["metrics"][k] for k in ROWS},
        }
    return out


if __name__ == "__main__":
    m = run()
    if "--json" in sys.argv:
        (HERE / "matrix.json").write_text(
            json.dumps(m, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(m, ensure_ascii=False, indent=1))
    else:
        names = sorted(m)
        width = max(len(r) for r in ROWS) + 2
        print(f"{'':{width}}" + "".join(f"{n:>26}" for n in names))
        for n in names:
            pass
        for row in ROWS:
            cells = ""
            for n in names:
                d = m[n]["metrics"][row]
                cells += (f"{d['correct']:>4}/{d['of']:<4} {d['pct']:5.1f} "
                          f"[{d['ci95'][0]:4.1f},{d['ci95'][1]:5.1f}]")
            print(f"{row:{width}}{cells}")
        print()
        for n in names:
            d = m[n]
            print(f"{n}: {d['documents']} documents ({d['splitUnit']} split), "
                  f"frame {d['frameSize']:,}, sampled {d['sampled']}")
