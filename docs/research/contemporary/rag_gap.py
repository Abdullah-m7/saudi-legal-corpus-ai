#!/usr/bin/env python3
"""What would a statute-only retriever miss?

Not a benchmark and not a system. One estimate, built from things already
measured, of a quantity that matters to anyone grounding a Saudi legal
assistant on the statute book: how often the authority that completes the
court's reasoning is not in the statute book at all.

Three factors, each from its own source:

    P(hybrid)          share of reasoned judgments whose court voice cites
                       both a statute and something else       [hybrid.py]
    P(load-bearing)    share of those where the non-statutory sentence
                       cannot be deleted without changing the reasoning
                       [hybrid_roles_gold.json, 40 judgments, one reader]
    P(retrievable)     share of the court's named-fiqh mentions that name a
                       source at all -- a book, a jurist, a page. An
                       «المقرر فقهاً وقضاءً» names nothing and cannot be
                       retrieved from any corpus, however complete.
                                                            [mention layer]

The middle factor rests on hand labels and is an interpretive layer: written
rules, an UNCLEAR class, per-item provenance, and a deletion test in place of
an intuition. The outer two are mechanical.

    python3 rag_gap.py
"""
import collections
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
from map import wilson                    # noqa: E402

LAYER = HERE / "authority_mentions.jsonl.gz"
ROLES = HERE / "hybrid_roles_gold.json"
HYB = HERE / "hybrid_results.json"
OUT = HERE / "rag_gap_results.json"
YEARS = (1444, 1445, 1446)


def main():
    hy = json.loads(HYB.read_text(encoding="utf-8"))["years"]
    n = sum(hy[str(y)]["n"] for y in YEARS)
    hybrid = sum(round(hy[str(y)]["hybridPrevalencePct"] * hy[str(y)]["n"]
                       / 100) for y in YEARS)
    roles = json.loads(ROLES.read_text(encoding="utf-8"))
    d = roles["deletionTest"]
    load = d["codeable"] - d["counts"]["yes"]

    rules = collections.Counter()
    kinds = collections.Counter()
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for r_ in fh:
            r = json.loads(r_)
            if "_schema" in r or r.get("q") or r["role"] != "court_reasoning":
                continue
            if r["y"] not in YEARS:
                continue
            kinds[r["t"]] += 1
            if r["t"] in ("fiqh_source", "legal_maxim", "judicial_principle",
                          "custom", "quran", "hadith"):
                rules[(r["t"], r["r"])] += 1
    fiqh = {k[1]: v for k, v in rules.items() if k[0] == "fiqh_source"}
    named = sum(v for k, v in fiqh.items() if k != "fiqh.unattributed")
    tot_fiqh = sum(fiqh.values())

    p_hybrid = 100 * hybrid / n
    p_load = 100 * load / d["codeable"]
    res = {
        "window": list(YEARS),
        "reasonedJudgments": n,
        "hybridJudgments": hybrid,
        "hybridPct": round(p_hybrid, 1),
        "loadBearingOfCodeable": f"{load}/{d['codeable']}",
        "loadBearingPct": round(p_load, 1),
        "loadBearingCI": wilson(load, d["codeable"]),
        "loadBearingStatus": "INTERPRETIVE_LAYER",
        "loadBearingBasis": "explicit rules in ANNOTATION_GUIDE.md, an UNCLEAR class used 4 times in 40, provenance recorded per item, and a deletion test that replaces the reader's intuition with an answerable question",
        "estimateReasonedJudgmentsWhereStatuteOnlyRetrievalOmitsPct":
            round(p_hybrid * p_load / 100, 1),
        "namedFiqhMentions": tot_fiqh,
        "namedFiqhWithASourcePct": round(100 * named / tot_fiqh, 1),
        "fiqhRuleBreakdown": dict(sorted(fiqh.items(), key=lambda kv: -kv[1])),
        "authorityTypeCounts": dict(kinds.most_common()),
        "note": "the estimate is a product of three independently measured "
                "shares, not a single measurement, and it assumes the 40 "
                "labelled judgments are representative of hybrid judgments "
                "in the window. It is an order of magnitude, not a rate.",
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(f"reasoned judgments {n:,}; hybrid {hybrid:,} ({res['hybridPct']} %)")
    print(f"load-bearing in the hand sample {res['loadBearingOfCodeable']} "
          f"= {res['loadBearingPct']} % (95% CI {res['loadBearingCI']})")
    print(f"=> statute-only retrieval would omit an authority the court used "
          f"to complete its reasoning in about "
          f"{res['estimateReasonedJudgmentsWhereStatuteOnlyRetrievalOmitsPct']}"
          f" % of reasoned judgments")
    print(f"\nof {tot_fiqh:,} court fiqh mentions, "
          f"{res['namedFiqhWithASourcePct']} % name a source that could be "
          f"retrieved at all:")
    for k, v in list(res["fiqhRuleBreakdown"].items())[:6]:
        print(f"   {k:<26}{v:>7,}")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
