#!/usr/bin/env python3
"""Is the shape of the first-instance reasons associated with what the
appellate circuit does with it?

Two things have to be right before the question is even askable, and the
second is why this is a separate script rather than a scan of the mention
layer.

    SELECTION.  Only judgments that were appealed AND published with both
    documents in one record can carry an outcome. That is a slice, not the
    corpus, and it is described here rather than assumed away.

    LEVEL.  `role=court_reasoning` in the mention layer covers the reasons of
    BOTH documents in a paired record. Using it would let the appellate
    circuit's own authorities into the predictor that is supposed to describe
    the judgment below -- reverse causation by construction. So the mentions
    are recomputed here and kept only where they fall inside the first
    document's span.

What is reported is an association inside a selected slice. Nothing here
identifies an effect of reasoning on survival, and the wording says so.

    python3 appellate.py
"""
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
import appellate_outcome as AO        # noqa: E402
import authority as A                 # noqa: E402
import match_instruments as M         # noqa: E402
import voice_attribution as V         # noqa: E402
from map import wilson                # noqa: E402
from windows import judgments, year_of   # noqa: E402

REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
OUT = HERE / "appellate_results.json"
YEARS = {1444, 1445, 1446}
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")
DISTURBED = {"reversed", "substituted", "varied"}


def shape_of(types):
    st = types["statute"] > 0
    ns = any(types[t] for t in NONSTATUTE)
    return ("hybrid" if st and ns else "statute_only" if st else
            "nonstatute_only" if ns else "none")


def main():
    index, order = M.build(REGISTRY)
    rows = []
    seen = paired = 0
    for rec in judgments():
        y = year_of(rec)
        if y not in YEARS:
            continue
        seen += 1
        s = rec.get("sections") or {}
        if not (s.get("judgmentTextofRulling") and s.get("appealTextofRulling")):
            continue
        text = rec["text"]
        spans = V.parts(text, s)
        if len(spans) < 2:
            continue
        paired += 1
        lo, hi = spans[0]
        types = collections.Counter()
        for m in A.mentions(text, s, index, order):
            if m.get("inQuote") or not (lo <= m["at"] < hi):
                continue
            if A.voice(m) != "court_reasoning":
                continue
            types[m["type"]] += 1
        outcome = AO.outcome(s["appealTextofRulling"])[0]
        rows.append({"year": y, "shape": shape_of(types),
                     "outcome": outcome,
                     "chars": len(s["judgmentTextofRulling"]),
                     "authorities": sum(types.values())})

    tab = collections.Counter((r["shape"], r["outcome"]) for r in rows)
    shapes = ("statute_only", "hybrid", "nonstatute_only", "none")
    outcomes = sorted({r["outcome"] for r in rows})
    res = {
        "window": sorted(YEARS),
        "judgmentsInWindow": seen,
        "pairedRecords": paired,
        "pairedShare": round(100 * paired / seen, 1),
        "selection": {
            "note": "every figure below is conditional on the dispute having "
                    "been appealed and published as one record carrying both "
                    "documents. Judgments never appealed have no outcome and "
                    "are not in the denominator.",
        },
        "byShape": {},
        "crossTab": {f"{a}|{b}": c for (a, b), c in sorted(tab.items())},
        "outcomes": outcomes,
    }
    for sh in shapes:
        sub = [r for r in rows if r["shape"] == sh]
        if not sub:
            continue
        dist = sum(1 for r in sub if r["outcome"] in DISTURBED)
        aff = sum(1 for r in sub if r["outcome"] == "affirmed")
        res["byShape"][sh] = {
            "n": len(sub),
            "disturbedPct": round(100 * dist / len(sub), 1),
            "disturbedCI": wilson(dist, len(sub)),
            "affirmedPct": round(100 * aff / len(sub), 1),
            "medianChars": sorted(r["chars"] for r in sub)[len(sub) // 2],
            "meanAuthorities": round(
                sum(r["authorities"] for r in sub) / len(sub), 2),
        }
    # the shape mix of the appealed slice against the shape mix of everything
    # in the same window: if they differ, the association is inside a slice
    # that does not look like the corpus, and that has to be visible.
    res["shapeMixAppealed"] = {
        sh: round(100 * sum(1 for r in rows if r["shape"] == sh) / len(rows), 1)
        for sh in shapes}
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(f"{paired:,} paired records of {seen:,} judgments in the window "
          f"({res['pairedShare']} %)\n")
    print(f"{'first-instance shape':<20}{'n':>7}{'disturbed':>12}"
          f"{'95% CI':>16}{'affirmed':>11}{'median chars':>14}")
    for sh, v in res["byShape"].items():
        print(f"  {sh:<18}{v['n']:>7,}{v['disturbedPct']:>11.1f}%"
              f"{str(v['disturbedCI']):>16}{v['affirmedPct']:>10.1f}%"
              f"{v['medianChars']:>14,}")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
