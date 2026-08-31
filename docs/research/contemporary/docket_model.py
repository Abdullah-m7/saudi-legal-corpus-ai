#!/usr/bin/env python3
"""How much does knowing the code add, once the case is known?

The standardisation and matching in `docket_test.py` compare codes to each
other. This asks the prediction question instead, which is the one PHASE 8 of
the programme actually poses: given a judgment, how much better can its
supplementation be anticipated when the codes it cites are known, over and
above what the kind of case already tells you?

Two models, both fitted as group means so that every number can be read
straight off the data rather than out of a solver.

    MODEL 0   the docket alone: the mean rate of the judgment's stratum
              (claim family x contestedness x reasons-length band), backing
              off to the grand mean where a stratum is unseen.
    MODEL 1   the docket plus an additive adjustment for each code the
              judgment cites, fitted as that code's mean residual from
              MODEL 0 on the training half.

A judgment cites several codes, so the code adjustments are summed and the
prediction clipped to [0, 1]. That is the multi-exposure design the data
requires; treating one judgment as one code would double-count.

Uncertainty is a cluster bootstrap over JUDGMENTS -- resampling judgments,
not rows -- because the same judgment supplies the outcome for every code it
cites and resampling rows would understate the spread.

Scored on a held-out half by Brier score, which is the mean squared error of
a probability and needs no calibration argument.

    python3 docket_model.py
"""
import collections
import gzip
import json
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
DOCKET = HERE / "docket_layer.jsonl.gz"
OUT = HERE / "docket_model_results.json"
RECENT = {1444, 1445, 1446}
CODES = ["commercial_courts_law", "evidence_law", "sharia_procedure_law",
         "commercial_courts_implementing_regulation", "companies_law",
         "civil_transactions_law", "law_practice_law", "arbitration_law",
         "bankruptcy_law"]
SEED = 20260831
BOOT = 400


def lenband(n):
    return 0 if n < 900 else 1 if n < 1600 else 2 if n < 2600 else 3


def contested(r):
    if r["appeared"] and not r["default"]:
        return "CONTESTED"
    if r["default"] and not r["appeared"]:
        return "DEFAULT"
    return "UNCLEAR"


def load():
    rows = []
    with gzip.open(DOCKET, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r["y"] not in RECENT:
                continue
            rows.append({
                "j": r["j"], "y": r["y"],
                "stratum": (r["claimFamily"], contested(r),
                            lenband(r["reasonChars"])),
                "codes": [c for c in r["local"] if c in CODES],
                "hybrid": r["hybrid"]})
    return rows


def fit(train):
    grand = statistics.mean(r["hybrid"] for r in train)
    g = collections.defaultdict(list)
    for r in train:
        g[r["stratum"]].append(r["hybrid"])
    m0 = {k: statistics.mean(v) for k, v in g.items() if len(v) >= 10}
    res = collections.defaultdict(list)
    for r in train:
        p = m0.get(r["stratum"], grand)
        for c in r["codes"]:
            res[c].append(r["hybrid"] - p)
    adj = {c: statistics.mean(v) for c, v in res.items() if len(v) >= 30}
    return grand, m0, adj


def predict(r, grand, m0, adj, with_codes):
    p = m0.get(r["stratum"], grand)
    if with_codes:
        p += sum(adj.get(c, 0.0) for c in r["codes"])
    return min(1.0, max(0.0, p))


def brier(rows, grand, m0, adj, with_codes):
    return statistics.mean(
        (predict(r, grand, m0, adj, with_codes) - r["hybrid"]) ** 2
        for r in rows)


def main():
    rows = load()
    rng = random.Random(SEED)
    ids = sorted({r["j"] for r in rows})
    rng.shuffle(ids)
    half = set(ids[:len(ids) // 2])
    train = [r for r in rows if r["j"] in half]
    test = [r for r in rows if r["j"] not in half]
    grand, m0, adj = fit(train)

    b_null = statistics.mean((grand - r["hybrid"]) ** 2 for r in test)
    b0 = brier(test, grand, m0, adj, False)
    b1 = brier(test, grand, m0, adj, True)

    # cluster bootstrap over held-out judgments
    byj = collections.defaultdict(list)
    for r in test:
        byj[r["j"]].append(r)
    keys = list(byj)
    diffs = []
    for _ in range(BOOT):
        s = [byj[rng.choice(keys)] for _ in range(len(keys))]
        flat = [r for group in s for r in group]
        diffs.append(brier(flat, grand, m0, adj, False)
                     - brier(flat, grand, m0, adj, True))
    diffs.sort()
    lo, hi = diffs[int(0.025 * BOOT)], diffs[int(0.975 * BOOT) - 1]

    res = {
        "window": sorted(RECENT),
        "judgments": len(rows),
        "trainJudgments": len(train), "testJudgments": len(test),
        "strataFitted": len(m0),
        "grandMeanHybrid": round(grand, 4),
        "brier": {
            "grandMeanOnly": round(b_null, 5),
            "model0_docketOnly": round(b0, 5),
            "model1_docketPlusCodes": round(b1, 5)},
        "improvement": {
            "docketOverGrandMean": round(b_null - b0, 5),
            "codesOverDocket": round(b0 - b1, 5),
            "codesOverDocketCI95": [round(lo, 5), round(hi, 5)],
            "bootstrap": "cluster bootstrap over held-out judgments, "
                         f"{BOOT} replications",
            "relativeShareOfTotalImprovementPct": round(
                100 * (b0 - b1) / (b_null - b1), 1) if b_null > b1 else None},
        "codeAdjustments": {c: round(v, 4) for c, v in
                            sorted(adj.items(), key=lambda kv: -kv[1])},
        "note": "Brier score, lower is better. The code adjustments are mean "
                "residuals from the docket-only model on the training half; "
                "they are descriptive, and a judgment citing several codes "
                "receives the sum of them.",
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(f"train {len(train):,} / test {len(test):,} judgments; "
          f"{len(m0)} strata fitted\n")
    print(f"  grand mean only        Brier {b_null:.5f}")
    print(f"  MODEL 0 docket only    Brier {b0:.5f}   "
          f"improvement {b_null - b0:+.5f}")
    print(f"  MODEL 1 docket + codes Brier {b1:.5f}   "
          f"improvement {b0 - b1:+.5f}  95% CI [{lo:+.5f}, {hi:+.5f}]")
    print(f"\n  codes carry {res['improvement']['relativeShareOfTotalImprovementPct']}"
          f" % of the total improvement over the grand mean")
    print("\n  code adjustments (mean residual from the docket-only model):")
    for c, v in res["codeAdjustments"].items():
        print(f"    {c:<44}{v:+.4f}")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
