#!/usr/bin/env python3
"""Freeze the hybrid-reasoning baseline before the next programme touches it.

The completeness programme will re-run `hybrid.py`, re-cut the samples and add
a classifier. If any of that moves the figures the previous session reported,
the movement has to be visible rather than absorbed. So this writes one
snapshot of the six results that session stood on, with the code hash that
produced them, and refuses to overwrite an existing snapshot.

The snapshot is a record, not a source: nothing reads it to compute anything.

    python3 freeze_hybrid.py          # write, if absent
    python3 freeze_hybrid.py --check  # compare the live results against it
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "frozen" / "hybrid_baseline.json"
YEARS = ("1442", "1443", "1444", "1445", "1446")


def snapshot():
    hy = json.loads((HERE / "hybrid_results.json").read_text(encoding="utf-8"))
    hg = json.loads((HERE / "hybrid_gold.json").read_text(encoding="utf-8"))
    y, seam = hy["years"], hy["seams"]

    def traj(field, kind):
        return {k: y[k]["authority"][kind][field] for k in YEARS}

    exemplars = {}
    for r in seam["articles"]:
        key = f"{r['instrument']}:{r['article']}"
        exemplars[key] = {"n": r["n"], "nonStatutePct": r["nonStatutePct"]}
    return {
        "what": "the hybrid-reasoning baseline as of the session that found it",
        "codeHash": hashlib.sha256(
            (HERE / "hybrid.py").read_bytes()).hexdigest()[:16],
        "reasonedByYear": {k: y[k]["n"] for k in YEARS},
        "statutePrevalenceByYear": traj("prevalencePct", "statute"),
        "statuteIntensityByYear": traj("intensity", "statute"),
        "fiqhPrevalenceByYear": traj("prevalencePct", "fiqh_source"),
        "fiqhIntensityByYear": traj("intensity", "fiqh_source"),
        "fiqhShareOfCourtMentionsByYear": traj(
            "shareOfCourtMentionsPct", "fiqh_source"),
        "articleRates": exemplars,
        "seamBasePct": seam["basePct"],
        "handSample": {
            "status": "EXPLORATORY hand-read sample, one reader, n=14",
            "seed": hg["seed"], "n": hg["n"], "counts": hg["counts"],
            "notClaimed": "The 0 ornamental cases are 0 of 14. With one "
                          "reader and fourteen judgments the 95 per cent "
                          "Wilson interval on an ornamental rate of 0/14 "
                          "runs to 21.5 per cent, so the sample rules out a "
                          "COMMON ornamental use and nothing narrower.",
        },
    }


def main():
    live = snapshot()
    if "--check" in sys.argv:
        if not OUT.exists():
            print("no snapshot; run without --check first")
            return 1
        was = json.loads(OUT.read_text(encoding="utf-8"))
        moved = [k for k in live if k != "codeHash" and was.get(k) != live[k]]
        if moved:
            print("the baseline has moved since it was frozen:")
            for k in moved:
                print(f"  {k}")
            return 1
        print("hybrid baseline unchanged since it was frozen")
        return 0
    if OUT.exists():
        print(f"{OUT.name} already exists; a frozen baseline is not rewritten")
        return 1
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(live, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(f"froze the hybrid baseline -> frozen/{OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
