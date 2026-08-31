#!/usr/bin/env python3
"""Forecast what is forecastable; detect early what is not.

`foresight.py` found that nothing beats persistence on any scalar target. The
wrong lesson to draw is that forecasting has failed. The right one is that a
prospective instrument needs TWO functions, and the programme has so far built
only one:

    FORECASTING              where predictive skill exists
    CHANGE DETECTION         where it does not, but a structural break can be
                             caught quickly under rules frozen in advance

They answer different sentences. "We predicted this" and "we did not predict
this, but the detector we froze beforehand caught it at the first mature
observation" are both scientific results; only the first is a forecast.

This file builds the first half and the measurements the second half needs:
the forecastability boundary, the maturity rule that decides when a quarter
may be scored at all, the entrant model that is the one place a signal beat
its base rate, a generic new-law uptake monitor, the heterogeneity search that
the failed bar-leads-bench result deserves before it is closed, the
rich-get-richer baseline any future feedback claim has to clear, and the
retrieval architecture comparison as a Pareto surface rather than a single
score.

    python3 horizon.py
"""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import foresight as F                      # noqa: E402

OUT = HERE / "horizon_results.json"
J = lambda n: json.loads((HERE / n).read_text(encoding="utf-8"))
P, LBL, PKEY = F.P, F.LBL, F.PKEY


# ------------------------------------------------------------------ PHASE 1
def forecastability_map(fs):
    """The boundary, stated once, so nobody tries to rescue a dead target."""
    rows = []
    for name, t in sorted(fs["scalarTargets"].items()):
        if t.get("verdict") == "INSUFFICIENT_TEMPORAL_DEPTH":
            rows.append({"target": name, "kind": "scalar",
                         "folds": t.get("folds", 0), "verdict": t["verdict"],
                         "status": "WATCH",
                         "reason": "too few rolling folds to evaluate at all"})
            continue
        sk = t.get("modelSkill", {})
        best = max(sk, key=lambda m: (sk[m].get("meanSkillVsBestBaseline")
                                      or -9, m)) if sk else None
        mean = sk.get(best, {}).get("meanSkillVsBestBaseline") if best else None
        rows.append({
            "target": name, "kind": "scalar", "folds": t["folds"],
            "bestBaseline": t["bestBaseline"],
            "bestBaselineMae": t["bestBaselineMae"],
            "bestModel": best, "meanSkill": mean,
            "worstFoldSkill": sk.get(best, {}).get("worstFoldSkill"),
            "verdict": t["verdict"],
            "status": "DETECT",
            "reason": "persistence not beaten; the level is monitorable but "
                      "not predictable beyond its own last value",
        })
    av, a10 = fs["articleVisibility"], fs["articleVisibilityTop10"]
    en, cp = fs["newEntrants"], fs["companionPersistence"]
    rows += [
        {"target": "top50_membership", "kind": "set", "folds": av["folds"],
         "bestBaseline": "previous period's set",
         "baselineJaccard": av["meanTopKJaccard_prevPeriod"],
         "worstFold": av["worstTopKJaccard_prevPeriod"],
         "verdict": av["verdict"], "status": "FORECAST",
         "reason": "the set is predictable at Jaccard "
                   f"{av['meanTopKJaccard_prevPeriod']} with a characterised "
                   "worst fold; no model beats persistence but persistence "
                   "itself is a usable forecast with known error"},
        {"target": "top10_membership", "kind": "set", "folds": a10["folds"],
         "baselineJaccard": a10["meanTopKJaccard_prevPeriod"],
         "worstFold": a10["worstTopKJaccard_prevPeriod"],
         "verdict": a10["verdict"], "status": "FORECAST",
         "reason": "same, at a smaller and noisier k"},
        {"target": "top50_new_entrants", "kind": "binary",
         "folds": len(en["periods"]), "baseRate": en["baseRate"],
         "bestSignal": en["bestSignal"],
         "precisionAtNTrue": en[en["bestSignal"]]["precisionAtNTrue"],
         "lift": en[en["bestSignal"]]["liftOverBaseRate"],
         "verdict": en["verdict"], "status": "FORECAST",
         "reason": "the only target where a signal beats its base rate by "
                   "more than a factor of five"},
        {"target": "retrieval_universe_coverage", "kind": "coverage",
         "folds": fs["retrievalDecay"]["h1"]["folds"],
         "verdict": "CHARACTERISED", "status": "FORECAST",
         "reason": "a frozen universe's coverage decays at a stable rate "
                   "across 13 folds"},
    ]
    for c, v in sorted(cp.items()):
        if v.get("verdict") != "TOP_K_PERSISTENT":
            continue
        rows.append({
            "target": f"companion_top3_set::{c}", "kind": "set",
            "folds": v["steps"], "baselineJaccard": v["meanTopKJaccard"],
            "worstFold": v["worstTopKJaccard"],
            "sameSetShare": v["sameSetShare"],
            "orderHeld": v["sameOrderShare"],
            "verdict": v["verdict"], "status": "FORECAST",
            "reason": "the SET persists; the ORDER does not and is not "
                      "forecast"})
    counts = Counter(r["status"] for r in rows)
    return {"rows": rows, "counts": dict(sorted(counts.items())),
            "rule": "FORECAST where a predictor beats an uninformed "
                    "reference with a characterised error; DETECT where the "
                    "level is measurable but persistence is unbeaten; WATCH "
                    "where there is not enough temporal depth to evaluate. "
                    "No target is rescued with a larger model."}


# ------------------------------------------------------------------ PHASE 3
def maturity(S, fs):
    """When may a quarter be scored at all? Decided before the future."""
    counts = fs["judgmentsWithAuthorityByPeriod"]
    vals = [counts[l] for l in LBL]
    rows = []
    for i, l in enumerate(LBL):
        n = vals[i]
        stat = sum(S[P[i]]["courtStat"].values())
        prior = vals[max(0, i - 4):i]
        med = sorted(prior)[len(prior) // 2] if prior else None
        checks = {
            "judgmentsAtLeast800": n >= 800,
            "courtStatuteCitationsAtLeast200": stat >= 200,
            "notTheCollectionEdge": i < len(LBL) - 1,
            "atLeast40pctOfPriorFourQuarterMedian":
                (med is None or n >= 0.4 * med),
        }
        rows.append({"period": l, "judgments": n, "courtCitations": stat,
                     "priorFourQuarterMedian": med,
                     "checks": checks,
                     "verdict": "SCORABLE" if all(checks.values())
                                else "NOT_SCORABLE",
                     "failed": [k for k, v in checks.items() if not v]})
    return {
        "criteria": [
            "at least 800 judgments carrying court authority",
            "at least 200 court statutory citations",
            "at least one later quarter exists in the corpus, so the quarter "
            "is not the collection edge",
            "volume at least 40 per cent of the median of the four preceding "
            "quarters",
        ],
        "forbidden": "the outcome itself may never be used to decide "
                     "maturity. A quarter is not declared immature because a "
                     "forecast missed in it.",
        "byPeriod": rows,
        "scorable": [r["period"] for r in rows if r["verdict"] == "SCORABLE"],
        "notScorable": [r["period"] for r in rows
                        if r["verdict"] != "SCORABLE"],
    }


# --------------------------------------------------------------- PHASES 4-5
def entrants(S, k=50, min_train=F.MIN_TRAIN):
    """Which present-period features identify next-period top-k entrants?

    Every feature is one number a reader can compute by hand. There is no
    model here beyond ranking candidates by a feature, and one additive rule
    that sums standardised ranks -- deliberately, because the point is a
    usable signal, not an accuracy contest.
    """
    folds = []
    frozen = None
    for i in range(min_train, len(P)):
        train, test = [S[P[x]] for x in range(i)], S[P[i]]
        if sum(test["courtStat"].values()) < 200:
            continue
        cur = F.top(train[-1]["courtStat"], k)
        curset = set(cur)
        nxt = set(F.top(test["courtStat"], k))
        hist = Counter()
        for s in train:
            hist.update(s["courtStat"])
        cand = [a for a, v in hist.items() if v >= 5 and a not in curset]
        if len(cand) < 30:
            continue
        cn = sum(train[-1]["courtStat"].values()) or 1
        pn = sum(train[-1]["partyStat"].values()) or 1
        prev2 = train[-2]["courtStat"] if len(train) >= 2 else Counter()
        p2n = sum(prev2.values()) or 1
        rank_now = {a: r for r, a in enumerate(F.top(train[-1]["courtStat"],
                                                     10000))}
        rank_prev = {a: r for r, a in enumerate(F.top(prev2, 10000))}
        # an instrument first seen in the last four quarters is "new"
        seen = defaultdict(lambda: len(P))
        for x in range(i):
            for (inst, _a) in S[P[x]]["courtStat"]:
                seen[inst] = min(seen[inst], x)
        rows = []
        for a in sorted(cand, key=str):
            r_now = rank_now.get(a, 9999)
            r_prev = rank_prev.get(a, 9999)
            rows.append({
                "article": f"{a[0]}:{a[1]}",
                "key": a,
                "courtShare": train[-1]["courtStat"][a] / cn,
                "partyShare": train[-1]["partyStat"][a] / pn,
                "rank": r_now,
                "rankAcceleration": r_prev - r_now,
                "momentum": train[-1]["courtStat"][a] / cn - prev2[a] / p2n,
                "judgments": len(train[-1]["courtJ"].get(a, ())),
                "newInstrument": 1 if seen[a[0]] >= i - 4 else 0,
                "entered": a in nxt,
            })
        n_true = sum(1 for r in rows if r["entered"])
        if not n_true:
            continue

        def prec(key, rev=True):
            rs = sorted(rows, key=lambda r: (-r[key] if rev else r[key],
                                             r["article"]))
            return sum(1 for r in rs[:n_true] if r["entered"]) / n_true

        # the additive rule: standardised rank position on three features
        def zrank(key, rev=True):
            rs = sorted(rows, key=lambda r: (-r[key] if rev else r[key],
                                             r["article"]))
            return {r["article"]: j for j, r in enumerate(rs)}
        zc, zr, zm = (zrank("courtShare"), zrank("rank", rev=False),
                      zrank("rankAcceleration"))
        for r in rows:
            r["combined"] = -(zc[r["article"]] + zr[r["article"]]
                              + zm[r["article"]])
        base = n_true / len(rows)
        # difficulty split: was the candidate already just outside the top k?
        near = [r for r in rows if r["rank"] <= k + 20]
        far = [r for r in rows if r["rank"] > k + 20]
        folds.append({
            "period": LBL[i], "candidates": len(rows), "entrants": n_true,
            "baseRate": round(base, 4),
            "precision": {key: round(prec(key), 4) for key in
                          ("courtShare", "partyShare", "rank",
                           "rankAcceleration", "momentum", "judgments",
                           "combined")},
            "nearBoundaryEntrants": sum(1 for r in near if r["entered"]),
            "longJumpEntrants": sum(1 for r in far if r["entered"]),
        })
        if i == len(P) - 1:
            frozen = sorted(rows, key=lambda r: (-r["combined"], r["article"]))
    if len(folds) < 4:
        return {"verdict": "INSUFFICIENT_TEMPORAL_DEPTH"}
    keys = list(folds[0]["precision"])
    mean = {key: round(sum(f["precision"][key] for f in folds) / len(folds), 4)
            for key in keys}
    baseRate = round(sum(f["baseRate"] for f in folds) / len(folds), 4)
    best = max(keys, key=lambda key: (mean[key], key))
    out = {
        "folds": len(folds), "periods": [f["period"] for f in folds],
        "meanBaseRate": baseRate,
        "meanPrecisionAtNTrue": mean,
        "liftOverBaseRate": {key: round(mean[key] / baseRate, 2)
                             for key in keys},
        "bestFeature": best,
        "worstFoldForBest": round(min(f["precision"][best] for f in folds), 4),
        "meanNearBoundaryEntrants": round(
            sum(f["nearBoundaryEntrants"] for f in folds) / len(folds), 2),
        "meanLongJumpEntrants": round(
            sum(f["longJumpEntrants"] for f in folds) / len(folds), 2),
        "byFold": folds,
        "verdict": ("SIGNAL_ABOVE_BASE_RATE" if mean[best] > baseRate * 1.5
                    else "NO_USABLE_SIGNAL"),
    }
    if frozen:
        out["frozenCandidateList"] = [
            {"rank": j + 1, "article": r["article"], "currentRank": r["rank"],
             "courtShare": round(r["courtShare"], 5),
             "rankAcceleration": r["rankAcceleration"],
             "difficulty": ("NEAR_BOUNDARY" if r["rank"] <= k + 20
                            else "LONG_JUMP")}
            for j, r in enumerate(frozen[:10])]
    return out


# ------------------------------------------------------------------ PHASE 6
def newlaw_monitor(S):
    """A generic uptake profile for any instrument that arrives in-window."""
    first_court, first_party = {}, {}
    court_j, top100, top50 = defaultdict(set), {}, {}
    for i, p in enumerate(P):
        s = S[p]
        cn = sum(s["courtStat"].values())
        for (inst, a), v in s["courtStat"].items():
            first_court.setdefault(inst, i)
            court_j[inst] |= s["courtJ"].get((inst, a), set())
        for (inst, _a) in s["partyStat"]:
            first_party.setdefault(inst, i)
        if cn >= 200:
            for kk, store in ((100, top100), (50, top50)):
                for (inst, _a) in F.top(s["courtStat"], kk):
                    store.setdefault(inst, i)
    rows = []
    for inst in sorted(first_court):
        fc = first_court[inst]
        if fc <= 1:
            continue                     # left-censored: already in use
        n = len(court_j[inst])
        rows.append({
            "instrument": inst,
            "firstCourtQuarter": LBL[fc],
            "firstPartyQuarter": (LBL[first_party[inst]]
                                  if inst in first_party else None),
            "partyBeforeCourtQuarters": (fc - first_party[inst]
                                         if inst in first_party else None),
            "quartersToTop100": (top100[inst] - fc if inst in top100 else None),
            "quartersToTop50": (top50[inst] - fc if inst in top50 else None),
            "courtJudgmentsToDate": n,
            # an instrument first seen in the corpus's opening year may have
            # been in use long before the window; its "arrival" is ours, not
            # the law's
            "censoringRisk": "POSSIBLY_CENSORED" if fc <= 4 else "IN_WINDOW",
        })
    reached = [r for r in rows if r["quartersToTop50"] is not None]
    return {
        "milestones": ["FIRST_PARTY", "FIRST_COURT", "TOP100_ENTRY",
                       "TOP50_ENTRY"],
        "instrumentsArrivingInWindow": len(rows),
        "reachedTop50": len(reached),
        "medianQuartersToTop50": (sorted(r["quartersToTop50"]
                                         for r in reached)[len(reached) // 2]
                                  if reached else None),
        "rows": sorted(rows, key=lambda r: (-r["courtJudgmentsToDate"],
                                            r["instrument"]))[:12],
        "note": "left-censored instruments -- already cited in the first two "
                "quarters -- are excluded, because their arrival is not in "
                "the window. This is a velocity profile, not a forecast: the "
                "corpus contains one clean arrival and one is not a sample.",
    }


# ------------------------------------------------------------------ PHASE 7
def leadlag_subsets(S, min_train=F.MIN_TRAIN):
    """The bar does not lead the bench overall. Does it anywhere?"""
    def partial(pairs_prev, pairs_test, keyset):
        uni = sorted(keyset, key=str)
        if len(uni) < 25:
            return None
        prev, test = pairs_prev, pairs_test
        cn = sum(prev["courtStat"].values()) or 1
        pn = sum(prev["partyStat"].values()) or 1
        tn = sum(test["courtStat"].values()) or 1
        y = [test["courtStat"][a] / tn for a in uni]
        xc = [prev["courtStat"][a] / cn for a in uni]
        xp = [prev["partyStat"][a] / pn for a in uni]

        def r(u, v):
            n = len(u)
            mu, mv = sum(u) / n, sum(v) / n
            su = math.sqrt(sum((x - mu) ** 2 for x in u))
            sv = math.sqrt(sum((x - mv) ** 2 for x in v))
            return (sum((a - mu) * (b - mv) for a, b in zip(u, v)) / (su * sv)
                    if su and sv else None)
        rc, rp, rcp = r(xc, y), r(xp, y), r(xc, xp)
        if None in (rc, rp, rcp) or abs(1 - rcp ** 2) < 1e-9 \
                or abs(1 - rc ** 2) < 1e-9:
            return None
        return (rp - rc * rcp) / math.sqrt((1 - rc ** 2) * (1 - rcp ** 2))

    subsets = {}
    for i in range(min_train, len(P)):
        prev, test = S[P[i - 1]], S[P[i]]
        if sum(test["courtStat"].values()) < 200:
            continue
        hist = Counter()
        for x in range(i):
            hist.update(S[P[x]]["courtStat"])
        uni = {a for a, v in hist.items() if v >= 5}
        if len(uni) < 50:
            continue
        rank = {a: r for r, a in enumerate(F.top(hist, 100000))}
        groups = {
            "ALL": uni,
            "CIVIL_TRANSACTIONS_LAW": {a for a in uni
                                       if a[0] == "civil_transactions_law"},
            "EVIDENCE_LAW": {a for a in uni if a[0] == "evidence_law"},
            "COMMERCIAL_COURTS_LAW": {a for a in uni
                                      if a[0] == "commercial_courts_law"},
            "RARE_ARTICLES_BOTTOM_HALF": {a for a in uni
                                          if rank.get(a, 0) >= len(uni) / 2},
            "CORE_ARTICLES_TOP_50": {a for a in uni if rank.get(a, 9e9) < 50},
        }
        for g, ks in groups.items():
            v = partial(prev, test, ks)
            if v is not None:
                subsets.setdefault(g, []).append(v)
    out = {}
    for g, vals in sorted(subsets.items()):
        if len(vals) < 4:
            out[g] = {"folds": len(vals), "verdict": "LOW_SUPPORT"}
            continue
        mean = sum(vals) / len(vals)
        out[g] = {
            "folds": len(vals), "meanPartialR": round(mean, 4),
            "worst": round(min(vals), 4), "best": round(max(vals), 4),
            "foldsPositive": sum(1 for v in vals if v > 0),
            "verdict": ("PARTY_ADDS" if mean > 0.05
                        and sum(1 for v in vals if v > 0) > len(vals) / 2
                        else "NO_LEAD_LAG_ABOVE_PERSISTENCE"),
        }
    any_pos = [g for g, v in out.items()
               if v.get("verdict") == "PARTY_ADDS"]
    return {"bySubset": out, "subsetsWherePartyAdds": sorted(any_pos),
            "verdict": ("ROBUST_NEGATIVE" if not any_pos
                        else "HETEROGENEOUS_DO_NOT_GENERALISE"),
            "note": "a subset result is reported as a subset result. It is "
                    "never generalised to the corpus, and the corpus-level "
                    "negative is not overturned by one group."}


# --------------------------------------------------------------- PHASES 19-20
def salience(S, min_train=2):
    """Does legal salience already concentrate, before any AI is observable?"""
    auto, top_persist, mobility, survival, hhi = [], [], [], [], []
    entrant_alive = []
    for i in range(min_train, len(P)):
        a, b = S[P[i - 1]]["courtStat"], S[P[i]]["courtStat"]
        if sum(a.values()) < 200 or sum(b.values()) < 200:
            continue
        ra = {k: r for r, k in enumerate(F.top(a, 100000))}
        rb = {k: r for r, k in enumerate(F.top(b, 100000))}
        both = sorted(set(ra) & set(rb), key=str)
        if len(both) < 50:
            continue
        n = len(both)
        mu_a = sum(ra[k] for k in both) / n
        mu_b = sum(rb[k] for k in both) / n
        sa = math.sqrt(sum((ra[k] - mu_a) ** 2 for k in both))
        sb = math.sqrt(sum((rb[k] - mu_b) ** 2 for k in both))
        if sa and sb:
            auto.append(sum((ra[k] - mu_a) * (rb[k] - mu_b) for k in both)
                        / (sa * sb))
        d = max(1, n // 10)
        ta, tb = set(F.top(a, d)), set(F.top(b, d))
        top_persist.append(len(ta & tb) / d)
        bottom = {k for k in both if ra[k] >= n / 2}
        mobility.append(len(bottom & tb) / len(bottom) if bottom else 0.0)
        tot = sum(b.values())
        hhi.append(sum((v / tot) ** 2 for v in b.values()))
        # entrant survival: new to top-50 at i, still there at i+1
        if i + 1 < len(P) and sum(S[P[i + 1]]["courtStat"].values()) >= 200:
            new = set(F.top(b, 50)) - set(F.top(a, 50))
            later = set(F.top(S[P[i + 1]]["courtStat"], 50))
            if new:
                entrant_alive.append(len(new & later) / len(new))
    m = lambda v: round(sum(v) / len(v), 4) if v else None
    return {
        "folds": len(auto),
        "rankAutocorrelation": m(auto),
        "topDecilePersistence": m(top_persist),
        "bottomHalfToTopDecileMobility": m(mobility),
        "newEntrantSurvivalOneQuarter": m(entrant_alive),
        "articleHhiMean": m(hhi),
        "articleHhiRange": [round(min(hhi), 5), round(max(hhi), 5)]
                           if hhi else None,
        "verdict": ("RICH_GET_RICHER_ALREADY_PRESENT"
                    if (m(top_persist) or 0) >= 0.7
                    and (m(mobility) or 1) <= 0.05
                    else "MOBILE_ENOUGH_TO_NOTICE_A_CHANGE"),
        "whyThisMatters": "any future claim that AI concentrated legal "
                          "authority has to clear this baseline. If the "
                          "system already concentrates strongly without "
                          "observable AI, a later concentration is not "
                          "evidence of AI; if it is mobile now, a later "
                          "freeze would be.",
    }


# --------------------------------------------------------------- PHASES 23-24
def architectures(S, comp, min_train=F.MIN_TRAIN):
    """Retrieval architectures as a Pareto surface, not one score.

    The hybrid is the one the previous report should have tested: discover
    candidates from the whole document, KEEP SPEAKER PROVENANCE, and rank by
    court attestation, spending the same index budget as the court-only
    universe. If high recall is worth anything, it is worth it here.
    """
    cid_by_code = defaultdict(Counter)
    for r in comp:
        if r["voice"] == "court" and r["instW"]:
            cid_by_code[r["instW"]][r["cid"]] += 1
    folds = []
    for i in range(min_train, len(P) - 1):
        train = [S[P[x]] for x in range(i + 1)]
        test = S[P[i + 1]]
        tn = sum(test["courtStat"].values())
        if tn < 200:
            continue
        court, whole = Counter(), set()
        for s in train:
            court.update(s["courtStat"])
            whole |= set(s["courtStat"]) | set(s["wideStat"]) | set(s["partyStat"])
        budget = len(court)
        cov = lambda U: sum(v for a, v in test["courtStat"].items()
                            if a in U) / tn
        # The hybrid has to be a genuinely intermediate point or it is not a
        # third architecture. Court-first ranking truncated to the court
        # budget just recovers the court universe -- that was the first
        # version and it was degenerate. So: the whole court universe, plus
        # the most frequently cited party-only candidates, at a stated 25 per
        # cent larger index. Speaker provenance is what makes the ordering
        # possible; it is not thrown away at ingestion.
        partyc = Counter()
        for s in train:
            partyc.update(s["partyStat"])
            partyc.update(s["wideStat"])
        extra = [a for a in F.top(partyc, 10 ** 9) if a not in court]
        hybrid = set(court) | set(extra[:max(0, int(0.25 * budget))])
        arch = {
            "STATUTE_ONLY_TOP50": set(F.top(train[-1]["courtStat"], 50)),
            "STATUTE_ONLY_TOP200": set(F.top(train[-1]["courtStat"], 200)),
            "COURT_REASONING": set(court),
            "WHOLE_JUDGMENT": whole,
            "SPEAKER_AWARE_HYBRID": hybrid,
        }
        row = {"period": LBL[i + 1]}
        for name, U in sorted(arch.items()):
            never = sum(1 for a in U if a not in court)
            row[name] = {
                "courtAuthorityRecall": round(cov(U), 4),
                "universeSize": len(U),
                "partyContamination": round(never / len(U), 4) if U else None,
            }
        folds.append(row)
    if len(folds) < 4:
        return {"verdict": "INSUFFICIENT_TEMPORAL_DEPTH"}
    names = sorted(k for k in folds[0] if k != "period")
    summary = {}
    for n in names:
        summary[n] = {
            "meanCourtAuthorityRecall": round(
                sum(f[n]["courtAuthorityRecall"] for f in folds) / len(folds), 4),
            "meanUniverseSize": round(
                sum(f[n]["universeSize"] for f in folds) / len(folds), 1),
            "meanPartyContamination": round(
                sum(f[n]["partyContamination"] for f in folds) / len(folds), 4),
        }
    # Pareto: not dominated on (recall high, size low, contamination low)
    def dominated(a, b):
        A, B = summary[a], summary[b]
        return (B["meanCourtAuthorityRecall"] >= A["meanCourtAuthorityRecall"]
                and B["meanUniverseSize"] <= A["meanUniverseSize"]
                and B["meanPartyContamination"] <= A["meanPartyContamination"]
                and (B["meanCourtAuthorityRecall"] > A["meanCourtAuthorityRecall"]
                     or B["meanUniverseSize"] < A["meanUniverseSize"]
                     or B["meanPartyContamination"] < A["meanPartyContamination"]))
    pareto = [a for a in names if not any(dominated(a, b) for b in names
                                          if b != a)]
    return {
        "folds": len(folds), "summary": summary,
        "paretoFront": sorted(pareto),
        "noCompositeScore": "the components are not summed. A weight on "
                            "recall against contamination is a legal "
                            "judgement about what a wrong citation costs, and "
                            "this file does not make it.",
        "byFold": folds,
    }


# ------------------------------------------------------------------ PHASE 22
def refresh_triggers(fs):
    """When should a frozen retrieval snapshot be rebuilt?"""
    mis = fs["temporalMisalignment"]
    rows = []
    for h in ("h1", "h2", "h4"):
        if h not in mis:
            continue
        m = mis[h]
        rows.append({
            "horizonQuarters": int(h[1:]),
            "top50DisplacedPct": m["meanTop50DisplacedPct"],
            "citationShareToNeverSeenArticles":
                m["meanCitationShareToNeverSeenArticles"],
            "meanRankDisplacementTop200": m["meanRankDisplacementTop200"],
        })
    trig = [
        {"trigger": "TOP50_DISPLACEMENT", "threshold": 30.0,
         "unit": "per cent of the frozen top 50 no longer in the observed "
                 "top 50",
         "firstHorizonCrossed": next(
             (r["horizonQuarters"] for r in rows
              if r["top50DisplacedPct"] >= 30.0), None)},
        {"trigger": "CONTENT_GAP", "threshold": 0.10,
         "unit": "share of court citations going to articles the snapshot "
                 "never saw",
         "firstHorizonCrossed": next(
             (r["horizonQuarters"] for r in rows
              if r["citationShareToNeverSeenArticles"] >= 0.10), None)},
        {"trigger": "RANK_GAP", "threshold": 35.0,
         "unit": "mean rank displacement in the top 200",
         "firstHorizonCrossed": next(
             (r["horizonQuarters"] for r in rows
              if r["meanRankDisplacementTop200"] >= 35.0), None)},
    ]
    crossed = [t for t in trig if t["firstHorizonCrossed"] is not None]
    earliest = min((t["firstHorizonCrossed"] for t in crossed), default=None)
    return {
        "profile": rows, "triggers": trig,
        "earliestTriggeredHorizonQuarters": earliest,
        "recommendation": (
            f"a snapshot crosses its first refresh trigger at horizon "
            f"{earliest} quarter(s)" if earliest else
            "no trigger crossed within the measured horizons"),
        "whichTriggerFiresFirst": (
            sorted(crossed, key=lambda t: (t["firstHorizonCrossed"],
                                           t["trigger"]))[0]["trigger"]
            if crossed else None),
        "note": "RANK_GAP and TOP50_DISPLACEMENT fire long before CONTENT_GAP. "
                "A maintenance policy written around missing content would "
                "refresh far too late.",
    }


def main():
    rows, dates, _ = F.load()
    S = F.build(rows)
    comp = []
    for src in (F.COMPANIONS, F.BACKFILL):
        if not src.exists():
            continue
        import gzip
        with gzip.open(src, "rt", encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                if "_schema" in r:
                    continue
                d = dates.get(r["j"])
                if not d:
                    continue
                p = (d[0], (d[1] - 1) // 3 + 1)
                if p in PKEY:
                    r["p"] = p
                    comp.append(r)
    fs = J("foresight_results.json")
    res = {
        "what": "SAUDI LEGAL HORIZON SCANNER: the forecastable half. What can "
                "be predicted, when a period may be scored, and the baselines "
                "any future claim about change has to clear.",
        "phase1_forecastabilityMap": forecastability_map(fs),
        "phase3_maturityRule": maturity(S, fs),
        "phase4_5_entrants": entrants(S, 50),
        "phase6_newLawMonitor": newlaw_monitor(S),
        "phase7_leadLagHeterogeneity": leadlag_subsets(S),
        "phase19_20_salienceBaseline": salience(S),
        "phase23_24_architectures": architectures(S, comp),
        "phase22_refreshTriggers": refresh_triggers(fs),
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    fm = res["phase1_forecastabilityMap"]["counts"]
    print(f"forecastability: {fm}")
    print(f"scorable quarters: "
          f"{len(res['phase3_maturityRule']['scorable'])} of {len(LBL)}")
    e = res["phase4_5_entrants"]
    print(f"entrants: best feature {e.get('bestFeature')} "
          f"precision {e.get('meanPrecisionAtNTrue', {}).get(e.get('bestFeature'))} "
          f"vs base {e.get('meanBaseRate')}")
    print(f"lead-lag heterogeneity: {res['phase7_leadLagHeterogeneity']['verdict']}")
    print(f"salience: {res['phase19_20_salienceBaseline']['verdict']}")
    print(f"pareto front: {res['phase23_24_architectures'].get('paretoFront')}")
    print(f"-> {OUT.name}")


if __name__ == "__main__":
    main()
