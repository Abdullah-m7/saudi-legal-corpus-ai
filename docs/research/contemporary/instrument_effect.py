#!/usr/bin/env python3
"""Is the instrument effect a property of the code, or of the cases?

The outcome throughout this programme is a property of the JUDGMENT: does the
court's reasoning carry a non-statutory authority. It is then attributed to
every article the judgment cites. That means a judgment citing both art. 16 of
the Commercial Courts Law and art. 29 of the Evidence Law contributes the same
outcome to both, and the entire between-instrument difference has to come from
WHICH JUDGMENTS cite which code -- from the case mix -- and not from anything
inside the article.

Saying that plainly changes what "the authority ecology of a code" can mean,
so it is tested rather than asserted, in four steps that get progressively
harder to explain away:

  1. EXPOSURE. A judgment that cites ten authorities is likelier to include a
     non-statutory one than a judgment that cites two, for arithmetic reasons.
     If codes differ in how much a chamber cites when it reaches for them,
     part of the ecology is counting.
  2. STRATIFIED. Recompute every code's rate inside bands of citation count.
     What survives is not exposure.
  3. CO-CITATION. Compare a code's rate in judgments that also cite a second
     code against the same code alone. If the rate tracks the company it
     keeps, the code is not carrying it.
  4. LEAVE-ONE-INSTRUMENT-OUT. Predict a held-out code's rate from the
     textual and functional features of the others. If that works, the
     ecology is a function of what kind of code it is; if it does not, code
     identity is irreducible with what is measured here.

    python3 instrument_effect.py
"""
import collections
import gzip
import itertools
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
from map import wilson                        # noqa: E402

LAYER = HERE / "authority_mentions.jsonl.gz"
INST = HERE / "instruments_results.json"
FUNC = HERE / "adjudicative_function_gold.json"
OUT = HERE / "instrument_effect_results.json"
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")
RECENT = {1444, 1445, 1446}
BANDS = ((1, 1), (2, 2), (3, 3), (4, 5), (6, 8), (9, 99))


def scan():
    docs = collections.defaultdict(
        lambda: {"c": collections.Counter(), "ca": set(), "y": 0})
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r.get("q"):
                continue
            if r["role"] != "court_reasoning":
                continue
            d = docs[r["j"]]
            d["y"] = r["y"]
            d["c"][r["t"]] += 1
            if r.get("inst") and r.get("art") is not None:
                d["ca"].add((r["inst"], r["art"]))
    return {j: d for j, d in docs.items() if d["y"] in RECENT and d["ca"]}


def band_of(n):
    for lo, hi in BANDS:
        if lo <= n <= hi:
            return f"{lo}-{hi}" if lo != hi else str(lo)
    return "9-99"


def main():
    docs = scan()
    res_i = json.loads(INST.read_text(encoding="utf-8"))
    insts = [i for i in res_i["instruments"]
             if res_i["ecology"][i]["judgments"] >= 80]

    for d in docs.values():
        d["nstat"] = d["c"]["statute"]
        d["mixed"] = any(d["c"][t] for t in NONSTATUTE)
        d["insts"] = {a[0] for a in d["ca"]}

    # 1. EXPOSURE
    bands = collections.defaultdict(lambda: [0, 0])
    for d in docs.values():
        b = bands[band_of(d["nstat"])]
        b[0] += 1
        b[1] += d["mixed"]
    exposure = {k: {"judgments": v[0],
                    "hybridPct": round(100 * v[1] / v[0], 1),
                    "ci": wilson(v[1], v[0])}
                for k, v in sorted(bands.items(),
                                   key=lambda kv: int(kv[0].split("-")[0]))}
    inst_exposure = {
        i: round(statistics.mean(
            [d["nstat"] for d in docs.values() if i in d["insts"]]), 2)
        for i in insts}

    # 2. STRATIFIED --- the rate inside each citation band, then a
    # direct-standardised rate using the corpus band mix as the standard.
    total = collections.Counter()
    for d in docs.values():
        total[band_of(d["nstat"])] += 1
    grand_n = sum(total.values())
    strat = {}
    for i in insts:
        sub = [d for d in docs.values() if i in d["insts"]]
        rows, std, wt = {}, 0.0, 0.0
        for b in total:
            s = [d for d in sub if band_of(d["nstat"]) == b]
            if len(s) < 15:
                continue
            r = sum(d["mixed"] for d in s) / len(s)
            rows[b] = {"judgments": len(s), "hybridPct": round(100 * r, 1)}
            std += r * total[b]
            wt += total[b]
        strat[i] = {
            "crudePct": round(
                100 * sum(d["mixed"] for d in sub) / len(sub), 1),
            "standardisedPct": round(100 * std / wt, 1) if wt else None,
            "coverageOfItsJudgmentsPct": round(100 * wt / grand_n, 1),
            "byBand": rows}

    # 3. CO-CITATION
    co = {}
    for a, b in itertools.combinations(insts, 2):
        both = [d for d in docs.values() if a in d["insts"] and b in d["insts"]]
        only_a = [d for d in docs.values()
                  if a in d["insts"] and b not in d["insts"]]
        only_b = [d for d in docs.values()
                  if b in d["insts"] and a not in d["insts"]]
        if len(both) < 40 or len(only_a) < 40 or len(only_b) < 40:
            continue
        f = lambda s: round(100 * sum(x["mixed"] for x in s) / len(s), 1)
        co[f"{a} | {b}"] = {
            "bothN": len(both), "bothPct": f(both),
            "onlyFirstN": len(only_a), "onlyFirstPct": f(only_a),
            "onlySecondN": len(only_b), "onlySecondPct": f(only_b),
            "gapAloneVsAlonePts": round(f(only_a) - f(only_b), 1),
            "bothMinusMaxAlonePts": round(
                f(both) - max(f(only_a), f(only_b)), 1)}
    co = dict(sorted(co.items(),
                     key=lambda kv: -abs(kv[1]["gapAloneVsAlonePts"])))

    # 4. LEAVE-ONE-INSTRUMENT-OUT, on the features that exist for a code.
    FEATS = ["medianArticleWords", "crossRefPerArticle",
             "shariaReferenceSharePct", "customReferenceSharePct",
             "discretionarySharePct", "openTexturedSharePct",
             "subparagraphsPerArticle", "articlesInRegistry",
             "yearsObservedTo1446"]
    have = [i for i in insts
            if res_i["features"].get(i, {}).get("medianArticleWords")]
    y = {i: res_i["ecology"][i]["hybridPct"] for i in have}
    X = {i: [res_i["features"][i][f] or 0 for f in FEATS] for i in have}

    def fit(train):
        """One-feature-at-a-time least squares, then the best single feature.

        With eight instruments a multivariate fit would be fitting noise with
        ceremony. The honest question is whether ANY code-level feature
        carries the rate, so each is fitted alone and the best one on the
        training set is the model.
        """
        best = None
        for k in range(len(FEATS)):
            xs = [X[i][k] for i in train]
            ys = [y[i] for i in train]
            mx, my = statistics.mean(xs), statistics.mean(ys)
            var = sum((x - mx) ** 2 for x in xs)
            if var == 0:
                continue
            b = sum((x - mx) * (t - my) for x, t in zip(xs, ys)) / var
            a = my - b * mx
            sse = sum((t - (a + b * x)) ** 2 for x, t in zip(xs, ys))
            if best is None or sse < best[0]:
                best = (sse, k, a, b)
        return best

    loo = {}
    for held in have:
        train = [i for i in have if i != held]
        sse, k, a, b = fit(train)
        pred = a + b * X[held][k]
        loo[held] = {"observedPct": y[held],
                     "predictedPct": round(pred, 1),
                     "errorPts": round(pred - y[held], 1),
                     "featureChosen": FEATS[k]}
    base = statistics.mean(y.values())
    mae = statistics.mean(abs(v["errorPts"]) for v in loo.values())
    null = statistics.mean(
        abs(statistics.mean([y[j] for j in have if j != i]) - y[i])
        for i in have)

    # 5. MARGINAL EFFECT, unconditional and inside a fixed procedural
    # posture. Almost every commercial judgment cites the Commercial Courts
    # Law, so "judgments that also cite CCL" is the closest thing this corpus
    # has to holding the kind of case fixed while the other code varies.
    marg = {}
    ccl = [d for d in docs.values() if "commercial_courts_law" in d["insts"]]
    for i in insts:
        with_i = [d for d in docs.values() if i in d["insts"]]
        without = [d for d in docs.values() if i not in d["insts"]]
        cw = [d for d in ccl if i in d["insts"]]
        cn = [d for d in ccl if i not in d["insts"]]
        f = lambda s: 100 * sum(x["mixed"] for x in s) / len(s) if s else None
        row = {"withN": len(with_i), "withPct": round(f(with_i), 1),
               "withoutPct": round(f(without), 1),
               "marginalPts": round(f(with_i) - f(without), 1)}
        if len(cw) >= 40 and cn:
            row.update({"withinCCL_withN": len(cw),
                        "withinCCL_withPct": round(f(cw), 1),
                        "withinCCL_withoutPct": round(f(cn), 1),
                        "withinCCL_marginalPts": round(f(cw) - f(cn), 1)})
        marg[i] = row
    marg = dict(sorted(marg.items(),
                       key=lambda kv: -kv[1]["marginalPts"]))

    res = {
        "window": sorted(RECENT),
        "marginalEffect": {
            "note": "the change in a judgment's hybrid rate that goes with "
                    "citing this code, unconditionally and then inside the "
                    "judgments that also cite the Commercial Courts Law -- "
                    "the closest this corpus comes to holding the kind of "
                    "case fixed. A marginal effect that survives that "
                    "conditioning is not simply the case mix.",
            "byInstrument": marg},
        "judgments": len(docs),
        "exposure": {
            "note": "hybrid rate by how many statutory citations the court's "
                    "reasons carry. A rising column is arithmetic before it "
                    "is anything else.",
            "byBand": exposure,
            "meanStatutoryCitationsInJudgmentsCitingThisCode": inst_exposure},
        "stratified": {
            "note": "direct standardisation to the corpus-wide distribution "
                    "of citation counts. crudePct is the ecology as first "
                    "reported; standardisedPct is what is left of it once "
                    "codes are compared at equal citation load.",
            "byInstrument": strat},
        "coCitation": {
            "note": "each pair needs 40 judgments in all three cells. "
                    "gapAloneVsAlonePts is the difference between the two "
                    "codes where each is cited without the other; "
                    "bothMinusMaxAlonePts asks whether citing both is higher "
                    "than either alone, which exposure alone would produce.",
            "pairs": co},
        "leaveOneInstrumentOut": {
            "note": "predict a held-out code's hybrid rate from code-level "
                    "features fitted on the others. Eight instruments carry "
                    "features, so the model is the single best feature on "
                    "the training set rather than a multivariate fit.",
            "instruments": have,
            "meanAbsoluteErrorPts": round(mae, 1),
            "nullMeanAbsoluteErrorPts": round(null, 1),
            "grandMeanPct": round(base, 1),
            "byInstrument": loo},
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")

    print("1. EXPOSURE --- hybrid rate by the court's statutory citation count")
    for b, v in exposure.items():
        print(f"   {b:>6} citations  n={v['judgments']:>6,}  "
              f"hybrid {v['hybridPct']:>5.1f}%  {v['ci']}")
    print("\n2. STRATIFIED --- crude against citation-count-standardised")
    for i, v in sorted(strat.items(), key=lambda kv: -kv[1]["crudePct"]):
        print(f"   {i[:44]:<44}crude {v['crudePct']:>5.1f}%   "
              f"standardised {str(v['standardisedPct']):>5}%   "
              f"(bands covering {v['coverageOfItsJudgmentsPct']}% of the corpus)")
    print("\n3. CO-CITATION --- the four largest gaps")
    for k, v in list(co.items())[:4]:
        a, b = k.split(" | ")
        print(f"   {a[:30]} alone {v['onlyFirstPct']}% (n={v['onlyFirstN']:,})  "
              f"vs {b[:30]} alone {v['onlySecondPct']}% (n={v['onlySecondN']:,})"
              f"   both {v['bothPct']}% (n={v['bothN']:,})")
    print("\n5. MARGINAL EFFECT --- unconditional, then within CCL-citing "
          "judgments")
    for i, v in marg.items():
        w = (f"{v['withinCCL_marginalPts']:>+6.1f} (n={v['withinCCL_withN']:,})"
             if "withinCCL_marginalPts" in v else "     --")
        print(f"   {i[:44]:<44}{v['marginalPts']:>+7.1f} pts   within CCL {w}")
    print(f"\n4. LEAVE-ONE-INSTRUMENT-OUT   MAE {mae:.1f} pts against a null "
          f"of {null:.1f}")
    for i, v in sorted(loo.items(), key=lambda kv: -abs(kv[1]["errorPts"])):
        print(f"   {i[:44]:<44}observed {v['observedPct']:>5.1f}%   "
              f"predicted {v['predictedPct']:>6.1f}%   "
              f"error {v['errorPts']:>6.1f}   via {v['featureChosen']}")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
