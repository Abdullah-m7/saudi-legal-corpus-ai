#!/usr/bin/env python3
"""Is it the books, or is it the disputes?

Everything the instrument effect has survived so far has been a property of
the text or of the citation. This is the last large competitor: the codes may
simply be invoked in different kinds of case. Five tests, in ascending order
of how hard they are to explain away.

  6/7  COMPOSITION AND STANDARDISATION. Describe the docket profile of the
       judgments citing each code, then standardise every code to a common
       profile and see how much of the fourteen-fold spread survives.
  9    MATCHED DOCKETS. Compare judgments that look alike -- same year, same
       contestedness, same claim family, same reasons-length band -- but cite
       different codes.
  10-12 WITHIN-JUDGMENT LOCAL CO-AUTHORITY. The strongest thing this corpus
       can do. Where one judgment cites two codes, the dispute, the chamber,
       the year, the parties and the document are all held fixed by
       construction. The whole-judgment flag cannot see that -- it marks every
       code the moment one jurist is quoted anywhere -- so the measure is
       whether a NON-STATUTORY mention falls within a window of each code's
       own citations. It is called LOCAL NON-STATUTORY CO-AUTHORITY, never
       supplementation: it is co-occurrence at a distance, and three distances
       are reported so the reader can see whether the answer depends on the
       window.
  13-16 The stress tests: arbitration, the fee article, whether the Evidence
       Law's ecology belongs to the code or to proof disputes, and whether the
       Civil Transactions Law's bench-bar gap survives its claim mix.
  20/21 Variance comparison, then a deliberate attempt to kill the result.

No causal language. Standardisation over observed strata is a description of
what the rates would be under a common docket mix, not an effect.

    python3 docket_test.py
"""
import collections
import gzip
import itertools
import json
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
from map import wilson                        # noqa: E402

DOCKET = HERE / "docket_layer.jsonl.gz"
LAYER = HERE / "authority_mentions.jsonl.gz"
OUT = HERE / "docket_test_results.json"
RECENT = {1444, 1445, 1446}
CODES = ["commercial_courts_law", "evidence_law", "sharia_procedure_law",
         "commercial_courts_implementing_regulation", "companies_law",
         "civil_transactions_law", "law_practice_law", "arbitration_law",
         "bankruptcy_law"]
# PHASE 5 verdicts, from the construct check against citations the flags were
# never built from. Lift is the percentage-point gap between flagged and
# unflagged judgments on an independent target.
VALIDITY = {
    "arbitrationPlea": ("VALID", 63.2), "default": ("VALID", 30.4),
    "expert": ("VALID", 15.1), "feesClaim": ("VALID", 9.5),
    "corporateClaim": ("VALID", 9.1), "settlement": ("VALID", 8.9),
    "damagesClaim": ("VALID", 8.6), "insolvencyClaim": ("VALID", 5.7),
    "appeared": ("VALID", -13.5),
    "priceClaim": ("COARSE_ONLY", 12.5), "proofDispute": ("COARSE_ONLY", 7.5),
    "admission": ("COARSE_ONLY", 6.0),
    "jurisdictionChallenge": ("UNUSABLE", 3.0),
}
USABLE = [k for k, (v, _) in VALIDITY.items() if v == "VALID"]


def lenband(n):
    return 0 if n < 900 else 1 if n < 1600 else 2 if n < 2600 else 3


def contested(r):
    if r["appeared"] and not r["default"]:
        return "CONTESTED"
    if r["default"] and not r["appeared"]:
        return "DEFAULT"
    return "UNCLEAR"


def stratum(r):
    return (r["claimFamily"], contested(r), lenband(r["reasonChars"]))


def load():
    rows = {}
    with gzip.open(DOCKET, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r["y"] not in RECENT:
                continue
            r["codes"] = set(r["local"])
            r["stratum"] = stratum(r)
            rows[r["j"]] = r
    return rows


def std_rate(sub, standard, key="hybrid"):
    """Direct standardisation to a reference distribution over strata."""
    num = den = 0.0
    bystr = collections.defaultdict(list)
    for r in sub:
        bystr[r["stratum"]].append(r[key])
    for s, w in standard.items():
        v = bystr.get(s)
        if not v or len(v) < 5:
            continue
        num += statistics.mean(v) * w
        den += w
    return (round(100 * num / den, 1), round(100 * den / sum(standard.values()), 1)) \
        if den else (None, 0.0)


def main():
    rows = load()
    allr = list(rows.values())
    standard = collections.Counter(r["stratum"] for r in allr)
    res = {"window": sorted(RECENT), "judgments": len(allr),
           "validity": {k: {"verdict": v, "constructLiftPts": l}
                        for k, (v, l) in VALIDITY.items()},
           "usableVariables": USABLE}

    # ---- PHASE 6: docket composition by code
    comp = {}
    base = {f: round(100 * sum(r[f] for r in allr) / len(allr), 1)
            for f in USABLE}
    base["CONTESTED"] = round(
        100 * sum(contested(r) == "CONTESTED" for r in allr) / len(allr), 1)
    base["medianReasonChars"] = statistics.median(
        r["reasonChars"] for r in allr)
    base["claimFamily"] = {k: round(100 * v / len(allr), 1) for k, v in
                           collections.Counter(
                               r["claimFamily"] for r in allr).most_common()}
    comp["ALL"] = base
    for c in CODES:
        sub = [r for r in allr if c in r["codes"]]
        if len(sub) < 60:
            continue
        d = {f: round(100 * sum(r[f] for r in sub) / len(sub), 1)
             for f in USABLE}
        d["CONTESTED"] = round(
            100 * sum(contested(r) == "CONTESTED" for r in sub) / len(sub), 1)
        d["medianReasonChars"] = statistics.median(
            r["reasonChars"] for r in sub)
        d["claimFamily"] = {k: round(100 * v / len(sub), 1) for k, v in
                            collections.Counter(
                                r["claimFamily"] for r in sub).most_common()}
        d["n"] = len(sub)
        # total-variation distance from the corpus claim-family mix
        d["claimFamilyDistanceFromCorpus"] = round(sum(
            abs(d["claimFamily"].get(k, 0) - base["claimFamily"].get(k, 0))
            for k in set(d["claimFamily"]) | set(base["claimFamily"])) / 200, 3)
        comp[c] = d
    res["docketComposition"] = comp

    # ---- PHASE 7: standardise every code to the corpus docket profile
    std = {}
    for c in CODES:
        sub = [r for r in allr if c in r["codes"]]
        if len(sub) < 60:
            continue
        raw = 100 * sum(r["hybrid"] for r in sub) / len(sub)
        s, cov = std_rate(sub, standard)
        std[c] = {"n": len(sub), "rawPct": round(raw, 1),
                  "standardisedPct": s,
                  "deltaPts": round(s - raw, 1) if s is not None else None,
                  "strataCoveragePct": cov}
    res["standardised"] = {
        "strata": "claim family x contestedness x reasons-length band",
        "nStrata": len(standard),
        "byInstrument": std}

    # ---- PHASE 9: matched cross-code comparison
    def matched(a, b, minimum=25):
        sa = [r for r in allr if a in r["codes"] and b not in r["codes"]]
        sb = [r for r in allr if b in r["codes"] and a not in r["codes"]]
        ga = collections.defaultdict(list)
        gb = collections.defaultdict(list)
        for r in sa:
            ga[(r["stratum"], r["y"])].append(r["hybrid"])
        for r in sb:
            gb[(r["stratum"], r["y"])].append(r["hybrid"])
        cells = [k for k in set(ga) & set(gb)
                 if len(ga[k]) >= 3 and len(gb[k]) >= 3]
        if not cells or sum(len(ga[k]) for k in cells) < minimum:
            return None
        w = {k: len(ga[k]) + len(gb[k]) for k in cells}
        tw = sum(w.values())
        ma = sum(statistics.mean(ga[k]) * w[k] for k in cells) / tw
        mb = sum(statistics.mean(gb[k]) * w[k] for k in cells) / tw
        return {"cells": len(cells),
                "nA": sum(len(ga[k]) for k in cells),
                "nB": sum(len(gb[k]) for k in cells),
                "rawA": round(100 * sum(r["hybrid"] for r in sa) / len(sa), 1),
                "rawB": round(100 * sum(r["hybrid"] for r in sb) / len(sb), 1),
                "matchedA": round(100 * ma, 1), "matchedB": round(100 * mb, 1),
                "rawGapPts": round(100 * (sum(r["hybrid"] for r in sa) / len(sa)
                                          - sum(r["hybrid"] for r in sb) / len(sb)), 1),
                "matchedGapPts": round(100 * (ma - mb), 1)}

    pairs = {}
    for a, b in itertools.combinations(CODES, 2):
        m = matched(a, b)
        if m:
            pairs[f"{a} | {b}"] = m
    res["matchedDockets"] = dict(sorted(
        pairs.items(), key=lambda kv: -abs(kv[1]["matchedGapPts"])))

    # ---- PHASES 10-12: within-judgment local co-authority
    multi = [r for r in allr if len(r["codes"]) >= 2
             and r["courtNonStatuteMentions"] > 0]
    loc = {}
    for w in ("w500", "w1000", "block"):
        per = collections.defaultdict(lambda: [0, 0])
        contrast = collections.defaultdict(lambda: [0, 0, 0])
        for r in multi:
            for c, d in r["local"].items():
                if c in CODES:
                    per[c][0] += d["mentions"]
                    per[c][1] += d[w]
            for a, b in itertools.combinations(sorted(r["local"]), 2):
                if a not in CODES or b not in CODES:
                    continue
                da, db = r["local"][a], r["local"][b]
                ra = da[w] / da["mentions"]
                rb = db[w] / db["mentions"]
                k = (a, b)
                contrast[k][0] += 1
                if ra > rb:
                    contrast[k][1] += 1
                elif rb > ra:
                    contrast[k][2] += 1
        loc[w] = {
            "judgments": len(multi),
            "byCode": {c: {"mentions": v[0],
                           "localCoAuthorityPct": round(100 * v[1] / v[0], 1),
                           "ci": wilson(v[1], v[0])}
                       for c, v in sorted(per.items(),
                                          key=lambda kv: -kv[1][0]) if v[0]},
            "pairwiseWithinJudgment": {
                f"{a} | {b}": {"judgments": v[0], "firstHigher": v[1],
                               "secondHigher": v[2],
                               "firstHigherPctOfDecided":
                                   round(100 * v[1] / (v[1] + v[2]), 1)
                                   if v[1] + v[2] else None}
                for (a, b), v in sorted(contrast.items(),
                                        key=lambda kv: -kv[1][0])
                if v[1] + v[2] >= 25},
        }
    res["locality"] = loc

    # ---- PHASE 13: arbitration through all four layers
    arb = {"raw": std.get("arbitration_law", {}).get("rawPct"),
           "standardised": std.get("arbitration_law", {}).get("standardisedPct"),
           "matchedAgainstCCL": pairs.get(
               "commercial_courts_law | arbitration_law"),
           "localVsCCLInSameJudgment": {
               w: loc[w]["pairwiseWithinJudgment"].get(
                   "arbitration_law | commercial_courts_law")
               for w in loc},
           "localRate": {w: loc[w]["byCode"].get("arbitration_law")
                         for w in loc}}
    res["arbitrationStressTest"] = arb

    # ---- PHASE 15: the Evidence Law, or disputes about proof?
    ev = {}
    for lab, sel in (("cites Evidence Law, proof dispute in recital",
                      lambda r: "evidence_law" in r["codes"] and r["proofDispute"]),
                     ("cites Evidence Law, no proof marker",
                      lambda r: "evidence_law" in r["codes"] and not r["proofDispute"]),
                     ("proof dispute, does NOT cite Evidence Law",
                      lambda r: "evidence_law" not in r["codes"] and r["proofDispute"]),
                     ("neither",
                      lambda r: "evidence_law" not in r["codes"] and not r["proofDispute"])):
        sub = [r for r in allr if sel(r)]
        k = sum(r["hybrid"] for r in sub)
        ev[lab] = {"n": len(sub), "hybridPct": round(100 * k / len(sub), 1),
                   "ci": wilson(k, len(sub))}
    res["evidenceCodeOrProofDispute"] = ev

    # ---- PHASE 14: the fee article against fee disputes generally
    fee = {}
    for lab, sel in (("fee claim, cites law practice law",
                      lambda r: r["feesClaim"] and "law_practice_law" in r["codes"]),
                     ("fee claim, no law practice law",
                      lambda r: r["feesClaim"] and "law_practice_law" not in r["codes"]),
                     ("no fee claim, cites law practice law",
                      lambda r: not r["feesClaim"] and "law_practice_law" in r["codes"]),
                     ("no fee claim, no law practice law",
                      lambda r: not r["feesClaim"] and "law_practice_law" not in r["codes"])):
        sub = [r for r in allr if sel(r)]
        if len(sub) < 20:
            fee[lab] = {"n": len(sub)}
            continue
        k = sum(r["hybrid"] for r in sub)
        fee[lab] = {"n": len(sub), "hybridPct": round(100 * k / len(sub), 1),
                    "ci": wilson(k, len(sub))}
    res["feeArticleStressTest"] = fee

    # ---- PHASE 18: length bands, as exposure not explanation
    bands = {}
    for c in CODES:
        sub = [r for r in allr if c in r["codes"]]
        if len(sub) < 60:
            continue
        bands[c] = {}
        for b in range(4):
            s = [r for r in sub if lenband(r["reasonChars"]) == b]
            if len(s) >= 20:
                bands[c][b] = round(100 * sum(r["hybrid"] for r in s) / len(s), 1)
    res["byReasonsLengthBand"] = {
        "bands": "0: <900 chars, 1: 900-1599, 2: 1600-2599, 3: 2600+",
        "byInstrument": bands,
        "corpus": {b: round(100 * statistics.mean(
            [r["hybrid"] for r in allr if lenband(r["reasonChars"]) == b]), 1)
            for b in range(4)}}

    # ---- PHASE 19: statutory breadth, a mediator not a control
    breadth = collections.defaultdict(lambda: [0, 0])
    for r in allr:
        k = min(len(r["codes"]), 4)
        breadth[k][0] += 1
        breadth[k][1] += r["hybrid"]
    res["statutoryBreadth"] = {
        "warning": "the number of distinct codes a judgment cites is downstream "
                   "of how much the chamber reasons, so this is reported as a "
                   "mediator-like sensitivity and never as a docket control",
        "byBreadth": {str(k): {"judgments": v[0],
                               "hybridPct": round(100 * v[1] / v[0], 1)}
                      for k, v in sorted(breadth.items())}}

    # ---- PHASE 20: where does the variation live
    def share(keyf):
        g = collections.defaultdict(list)
        for r in allr:
            g[keyf(r)].append(r["hybrid"])
        gm = statistics.mean(r["hybrid"] for r in allr)
        t = sum((r["hybrid"] - gm) ** 2 for r in allr)
        b = sum(len(v) * (statistics.mean(v) - gm) ** 2 for v in g.values())
        return round(100 * b / t, 2), len(g)

    def chance(keyf, reps=120, seed=5):
        sizes = collections.Counter(keyf(r) for r in allr)
        vals = [r["hybrid"] for r in allr]
        gm = statistics.mean(vals)
        t = sum((v - gm) ** 2 for v in vals)
        rng = random.Random(seed)
        out = []
        for _ in range(reps):
            rng.shuffle(vals)
            i, b = 0, 0.0
            for _k, m in sizes.items():
                g = vals[i:i + m]
                i += m
                b += m * (statistics.mean(g) - gm) ** 2
            out.append(100 * b / t)
        return round(statistics.mean(out), 2)

    var = {}
    for lab, keyf in (("year", lambda r: r["y"]),
                      ("city", lambda r: r["city"]),
                      ("claim family", lambda r: r["claimFamily"]),
                      ("contestedness", contested),
                      ("reasons-length band",
                       lambda r: lenband(r["reasonChars"])),
                      ("docket stratum (all three)", lambda r: r["stratum"]),
                      ("set of codes cited", lambda r: frozenset(r["codes"]))):
        s, g = share(keyf)
        c = chance(keyf)
        var[lab] = {"groups": g, "betweenSharePct": s,
                    "chanceSharePct": c, "excessPts": round(s - c, 2)}
    res["judgmentLevelVariance"] = {
        "note": "judgment-level, so an instrument cannot appear as a single "
                "grouping -- a judgment cites several. The set of codes is "
                "the nearest equivalent and is reported as such.",
        "chanceNote": "a grouping with more cells explains more by chance; "
                      "the excess is the share above what the same cell sizes "
                      "reach on shuffled outcomes over 120 shuffles",
        "byGrouping": dict(sorted(var.items(),
                                  key=lambda kv: -kv[1]["excessPts"]))}

    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")

    print(f"{len(allr):,} judgments with reasons, 1444-1446\n")
    print("PHASE 7 --- raw against docket-standardised")
    print(f"  {'instrument':<44}{'n':>7}{'raw':>8}{'std':>8}{'delta':>8}{'cover':>8}")
    for c, v in sorted(std.items(), key=lambda kv: -(kv[1]["rawPct"])):
        print(f"  {c[:42]:<44}{v['n']:>7,}{v['rawPct']:>7.1f}%"
              f"{v['standardisedPct'] if v['standardisedPct'] is not None else 0:>7.1f}%"
              f"{v['deltaPts'] if v['deltaPts'] is not None else 0:>+8.1f}"
              f"{v['strataCoveragePct']:>7.1f}%")
    print("\nPHASE 12 --- local co-authority, within-judgment, by window")
    for w in ("w500", "w1000", "block"):
        r = loc[w]["byCode"]
        print(f"  [{w}] " + "  ".join(
            f"{c.split('_')[0][:9]} {v['localCoAuthorityPct']}%"
            for c, v in list(r.items())[:6]))
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
