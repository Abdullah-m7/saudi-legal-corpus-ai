#!/usr/bin/env python3
"""Is the paired comparison reading a biased slice?

appeal_vs_first.py compares the reasons of the two levels inside the same
dispute, and finds appellate reasons more procedural and drawn from fewer
instruments. But only 22.3 per cent of paired records carry reasons on both
levels: most appellate judgments affirm «محمولاً على أسبابه» and write none
of their own. If a circuit writes its own reasons mainly when it disturbs the
judgment below, the comparison is between ordinary first-instance reasoning
and the unusual appeals — and the finding is an artefact of who writes.

The threat is testable, so it is tested rather than acknowledged. Two ways:

  1. Does writing reasons go with the outcome? Cross-tabulate.
  2. Does the finding survive inside each outcome? Recompute the procedural
     shares separately for affirmances and for disturbed judgments. A result
     that holds in both strata is not produced by the mix between them.
"""

import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
REGISTRY = REPO / "data" / "corpus_registry" / "corpus_registry.json"
sys.path.insert(0, str(HERE))

import appellate_outcome as AO    # noqa: E402
import match_instruments as M     # noqa: E402
import voice_attribution as V     # noqa: E402

DISTURBED = {"reversed", "substituted", "varied"}


def reasons_span(text, a, b):
    r = V.REASONS.search(text, a, b)
    k = V.RULING.search(text, r.end() if r else a, b)
    return (r.end(), k.start()) if r and k else None


def main():
    index, order = M.build(REGISTRY)
    wrote = collections.Counter()          # (outcome, wrote reasons?)
    cited = collections.defaultdict(collections.Counter)   # (stratum, level)

    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            s = r.get("sections") or {}
            if not (s.get("judgmentTextofRulling") and
                    s.get("appealTextofRulling")):
                continue
            text = r["text"]
            spans = V.parts(text, s)
            if len(spans) < 2:
                continue
            outcome = AO.outcome(s["appealTextofRulling"])[0]
            fr = reasons_span(text, *spans[0])
            ar_ = reasons_span(text, *spans[-1])
            wrote[(outcome, bool(ar_))] += 1
            if not fr or not ar_:
                continue
            stratum = ("disturbed" if outcome in DISTURBED
                       else "affirmed" if outcome == "affirmed" else "other")
            last = M.Recent()
            for m in V.CITE.finditer(text):
                tid, kind = M.match(m.group(2), index, order, last)
                if kind == "named":
                    last.note(tid)
                if not tid:
                    continue
                i = m.start()
                if fr[0] <= i < fr[1]:
                    cited[(stratum, "first")][tid] += 1
                elif ar_[0] <= i < ar_[1]:
                    cited[(stratum, "appeal")][tid] += 1

    print("does the appeal court write its own reasons?\n")
    print(f"{'outcome':<20}{'wrote':>8}{'did not':>10}{'share writing':>15}")
    out = {"writing": {}, "strata": {}}
    for label in ("affirmed", "reversed", "substituted", "not_admitted",
                  "other_disposition", "unclear"):
        yes, no = wrote[(label, True)], wrote[(label, False)]
        if yes + no == 0:
            continue
        print(f"{label:<20}{yes:>8,}{no:>10,}{yes/(yes+no):>14.1%}")
        out["writing"][label] = {"wrote": yes, "did_not": no}

    print("\nand within each outcome, the comparison again:\n")
    print(f"{'stratum':<12}{'level':<9}{'citations':>10}{'instruments':>13}"
          f"{'procedural':>12}")
    for stratum in ("affirmed", "disturbed"):
        for level in ("first", "appeal"):
            c = cited[(stratum, level)]
            tot = sum(c.values())
            if not tot:
                continue
            proc = sum(v for k, v in c.items() if k in M.PROCEDURAL)
            print(f"{stratum:<12}{level:<9}{tot:>10,}{len(c):>13}"
                  f"{proc/tot:>11.1%}")
            out["strata"][f"{stratum}_{level}"] = {
                "citations": tot, "instruments": len(c),
                "procedural": 100 * proc / tot}

    (HERE / "appeal_selection_results.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nwrote appeal_selection_results.json")


if __name__ == "__main__":
    main()
