#!/usr/bin/env python3
"""The layer before the judgment: external legal signals and early indicators.

A judgment is a late observation. By the time a provision appears in the
court's reasoning, the statute has been enacted, commenced, argued and
decided. The Horizon Scanner watches the corpus; this watches the things that
happen BEFORE the corpus moves, and freezes what each of them should imply
before the later data arrives.

    EXTERNAL LEGAL SIGNAL -> known at -> expected observables -> forecast or
    watch -> later court data -> score

Nothing here retunes a frozen detector, changes the maturity rule, or touches
the forecast ledger's issued entries. PROSPECTIVE_DETECTOR_ERA_1 is closed.

The hard rule of this file is about credit. An event discovered today about
2024 is a BACKFILLED_EVENT: it may calibrate a method and it may never support
a claim that the observatory anticipated anything. Only events first recorded
after the registry's own creation date are PROSPECTIVE_CAPTURE, and the
distinction is computed from timestamps rather than asserted.

    python3 leading.py
"""
import gzip
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import foresight as F                      # noqa: E402

OUT = HERE / "leading_results.json"
REG = HERE / "legal_signal_registry.json"
J = lambda n: json.loads((HERE / n).read_text(encoding="utf-8"))
P, LBL, PKEY = F.P, F.LBL, F.PKEY


# ------------------------------------------------------------------ PHASE 7
def ablation(S, k=50, min_train=F.MIN_TRAIN):
    """Does any feature add stable skill beyond court share alone?

    Complexity has to earn itself. Each candidate is tested as court share
    PLUS one feature, by rank-sum, against court share alone, on the same
    temporal folds. Nothing is kept because it is clever.
    """
    feats = ("partyShare", "rankAcceleration", "momentum", "judgments",
             "courtBarRatio", "instrumentAge", "coCitationBreadth",
             "newInstrument")
    per = {f: [] for f in feats}
    solo = []
    for i in range(min_train, len(P)):
        train, test = [S[P[x]] for x in range(i)], S[P[i]]
        if sum(test["courtStat"].values()) < 200:
            continue
        cur = set(F.top(train[-1]["courtStat"], k))
        nxt = set(F.top(test["courtStat"], k))
        hist = Counter()
        for s in train:
            hist.update(s["courtStat"])
        cand = [a for a, v in hist.items() if v >= 5 and a not in cur]
        if len(cand) < 30:
            continue
        cn = sum(train[-1]["courtStat"].values()) or 1
        pn = sum(train[-1]["partyStat"].values()) or 1
        prev2 = train[-2]["courtStat"] if len(train) >= 2 else Counter()
        p2n = sum(prev2.values()) or 1
        rank_now = {a: r for r, a in enumerate(F.top(train[-1]["courtStat"], 10 ** 6))}
        rank_prev = {a: r for r, a in enumerate(F.top(prev2, 10 ** 6))}
        first = defaultdict(lambda: len(P))
        for x in range(i):
            for (inst, _a) in S[P[x]]["courtStat"]:
                first[inst] = min(first[inst], x)
        # co-citation breadth: how many distinct articles share a judgment
        breadth = Counter()
        for a in cand:
            js = train[-1]["courtJ"].get(a, set())
            breadth[a] = len(js)
        rows = []
        for a in sorted(cand, key=str):
            cs = train[-1]["courtStat"][a] / cn
            ps = train[-1]["partyStat"][a] / pn
            rows.append({
                "a": a, "courtShare": cs, "partyShare": ps,
                "rankAcceleration": rank_prev.get(a, 9999) - rank_now.get(a, 9999),
                "momentum": cs - prev2[a] / p2n,
                "judgments": len(train[-1]["courtJ"].get(a, ())),
                "courtBarRatio": cs / ps if ps else (1.0 if cs else 0.0),
                "instrumentAge": i - first[a[0]],
                "coCitationBreadth": breadth[a],
                "newInstrument": 1 if first[a[0]] >= i - 4 else 0,
                "entered": a in nxt})
        n_true = sum(1 for r in rows if r["entered"])
        if not n_true:
            continue

        def rk(key):
            rs = sorted(rows, key=lambda r: (-r[key], str(r["a"])))
            return {r["a"]: j for j, r in enumerate(rs)}

        base_rank = rk("courtShare")
        solo.append(sum(1 for r in sorted(
            rows, key=lambda r: (base_rank[r["a"]], str(r["a"])))[:n_true]
            if r["entered"]) / n_true)
        for f in feats:
            fr = rk(f)
            order = sorted(rows, key=lambda r: (base_rank[r["a"]] + fr[r["a"]],
                                                str(r["a"])))
            per[f].append(sum(1 for r in order[:n_true] if r["entered"]) / n_true)
    if len(solo) < 4:
        return {"verdict": "INSUFFICIENT_TEMPORAL_DEPTH"}
    m = lambda v: sum(v) / len(v)
    base = m(solo)
    rows = []
    for f in feats:
        if not per[f]:
            continue
        d = [b - a for a, b in zip(solo, per[f])]
        rows.append({
            "feature": f, "meanPrecision": round(m(per[f]), 4),
            "deltaVsCourtShareAlone": round(m(per[f]) - base, 4),
            "foldsImproved": sum(1 for x in d if x > 0),
            "folds": len(d),
            "worstFoldDelta": round(min(d), 4)})
    rows.sort(key=lambda r: (-r["deltaVsCourtShareAlone"], r["feature"]))
    kept = [r for r in rows
            if r["deltaVsCourtShareAlone"] > 0.02
            and r["foldsImproved"] > r["folds"] / 2]
    return {
        "folds": len(solo),
        "courtShareAlone": round(base, 4),
        "candidates": rows,
        "featuresThatEarnTheirPlace": [r["feature"] for r in kept],
        "verdict": ("COURT_SHARE_REMAINS_THE_RULE" if not kept
                    else "A_FEATURE_ADDS_STABLE_SKILL"),
        "rule": "a feature is kept only if it improves mean precision by more "
                "than 2 points AND improves a majority of folds. Neither test "
                "alone is enough.",
    }


# ------------------------------------------------------------------ PHASE 8
def rare_discovery(S, min_train=4, party_min=1):
    """Does a rare provision's first party appearance precede court uptake?

    A cohort test, not a regression over every rare article. Treatment is a
    first party appearance -- at least one party citation in a quarter with
    none in the two before. The threshold was set at three and produced ZERO
    treated units: the strict party voice carries 11,794 mentions across 18
    quarters, so a rare provision almost never reaches three in one quarter.
    One is what the data supports, and the weakness of the treatment is
    reported rather than hidden. Controls are rare articles in the
    same prior-court-visibility band and the same instrument with no party
    appearance that quarter. Outcome is the court's own share one, two and
    four quarters later.
    """
    treated, control = [], []
    for i in range(min_train, len(P) - 1):
        prev = [S[P[x]] for x in range(i)]
        now = S[P[i]]
        if sum(now["courtStat"].values()) < 200:
            continue
        hist = Counter()
        for s in prev:
            hist.update(s["courtStat"])
        rank = {a: r for r, a in enumerate(F.top(hist, 10 ** 6))}
        # "rare" means the bottom half OF THE ELIGIBLE POOL, not the bottom
        # half of every string the extractor ever saw. Ranking against the
        # full universe put the threshold near 1,000 and left the cohort
        # empty, because an article with five cumulative citations is already
        # in the top quarter of everything. This matches the definition the
        # lead-lag subset used.
        eligible = [a for a, v in hist.items() if v >= 5]
        cut = len(eligible) / 2
        rare = [a for a in eligible if rank[a] >= cut]
        if len(rare) < 40:
            continue
        cn0 = sum(now["courtStat"].values()) or 1
        pn0 = sum(now["partyStat"].values()) or 1
        nz = sorted(now["courtStat"][a] / cn0 for a in rare
                    if now["courtStat"][a] > 0)
        rare_med = nz[len(nz) // 2] if nz else 0.0

        def future(a, h):
            if i + h >= len(P):
                return None
            s = S[P[i + h]]
            tot = sum(s["courtStat"].values())
            return s["courtStat"][a] / tot if tot >= 200 else None

        for a in sorted(rare, key=str):
            pa = now["partyStat"][a]
            before = sum(S[P[x]]["partyStat"][a] for x in range(max(0, i - 2), i))
            # a BAND, not a value: rounding a continuous share to four
            # decimals matched almost nothing. Three coarse strata --
            # invisible, below the rare median, above it -- are what a
            # matched comparison can actually fill.
            share = now["courtStat"][a] / cn0
            band = (0 if share == 0 else 1 if share <= rare_med else 2)
            rec = {"article": f"{a[0]}:{a[1]}", "instrument": a[0],
                   "period": LBL[i], "priorCourtShare": now["courtStat"][a] / cn0,
                   "band": band,
                   "h1": future(a, 1), "h2": future(a, 2), "h4": future(a, 4)}
            if pa >= party_min and before == 0:
                treated.append(rec)
            elif pa == 0:
                control.append(rec)
    if len(treated) < 10:
        return {"verdict": "LOW_SUPPORT", "treated": len(treated)}
    # match on (instrument, band); a treated unit with no match is dropped
    pool = defaultdict(list)
    for c in control:
        pool[(c["instrument"], c["band"], c["period"])].append(c)
    pairs = []
    for t in treated:
        ms = pool.get((t["instrument"], t["band"], t["period"]), [])
        if ms:
            pairs.append((t, ms))
    out = {"treatedTotal": len(treated), "controlPool": len(control),
           "matchedTreated": len(pairs)}
    for h in ("h1", "h2", "h4"):
        d, tv, cv = [], [], []
        for t, ms in pairs:
            if t[h] is None:
                continue
            cs = [m[h] for m in ms if m[h] is not None]
            if not cs:
                continue
            c = sum(cs) / len(cs)
            tv.append(t[h])
            cv.append(c)
            d.append(t[h] - c)
        if len(d) >= 8:
            mu = sum(d) / len(d)
            sd = math.sqrt(sum((x - mu) ** 2 for x in d) / len(d))
            out[h] = {"pairs": len(d),
                      "meanTreatedCourtShare": round(sum(tv) / len(tv), 6),
                      "meanMatchedControl": round(sum(cv) / len(cv), 6),
                      "meanDifference": round(mu, 6),
                      "sd": round(sd, 6),
                      "positivePairs": sum(1 for x in d if x > 0),
                      "signTestShare": round(
                          sum(1 for x in d if x > 0) / len(d), 4)}
        else:
            out[h] = {"pairs": len(d), "verdict": "LOW_SUPPORT"}
    sig = [h for h in ("h1", "h2", "h4")
           if isinstance(out.get(h), dict) and out[h].get("signTestShare")
           and out[h]["signTestShare"] > 0.6 and out[h]["meanDifference"] > 0]
    out["verdict"] = ("BAR_DISCOVERY_SIGNAL_SURVIVES_MATCHING" if sig
                      else "NO_BAR_DISCOVERY_SIGNAL_AFTER_MATCHING")
    out["horizonsSurviving"] = sig
    out["note"] = ("the aggregate lead-lag result found a positive partial "
                   "correlation in the bottom half. This is the cohort test "
                   "that correlation deserves before it is believed.")
    return out


# ------------------------------------------------------------------ PHASE 9
def first_mover(S, min_train=2):
    """Does WHO cites an authority first predict what happens to it?"""
    firstc, firstp = {}, {}
    for i, p in enumerate(P):
        for a in S[p]["courtStat"]:
            firstc.setdefault(a, i)
        for a in S[p]["partyStat"]:
            firstp.setdefault(a, i)
    rows = []
    for a in sorted(set(firstc) | set(firstp), key=str):
        fc, fp = firstc.get(a), firstp.get(a)
        if (fc is None or fc < min_train) and (fp is None or fp < min_train):
            continue                      # left-censored
        if fc is None:
            typ = "BAR_ONLY"
            start = fp
        elif fp is None:
            typ = "COURT_ONLY"
            start = fc
        elif fc < fp:
            typ = "COURT_FIRST"
            start = fc
        elif fp < fc:
            typ = "BAR_FIRST"
            start = fp
        else:
            typ = "SAME_PERIOD"
            start = fc
        later = [x for x in range(start + 1, len(P))
                 if sum(S[P[x]]["courtStat"].values()) >= 200]
        alive = sum(1 for x in later if S[P[x]]["courtStat"][a] > 0)
        core = any(a in set(F.top(S[P[x]]["courtStat"], 100)) for x in later)
        rows.append({"article": f"{a[0]}:{a[1]}", "type": typ,
                     "startPeriod": LBL[start],
                     "laterPeriods": len(later),
                     "survivalShare": alive / len(later) if later else None,
                     "reachedTop100": core})
    out = {}
    for typ in sorted({r["type"] for r in rows}):
        g = [r for r in rows if r["type"] == typ and r["survivalShare"] is not None]
        if len(g) < 10:
            out[typ] = {"n": len(g), "verdict": "LOW_SUPPORT"}
            continue
        out[typ] = {
            "n": len(g),
            "meanSurvivalShare": round(
                sum(r["survivalShare"] for r in g) / len(g), 4),
            "reachedTop100Share": round(
                sum(1 for r in g if r["reachedTop100"]) / len(g), 4)}
    best = max((t for t in out if "meanSurvivalShare" in out[t]),
               key=lambda t: (out[t]["meanSurvivalShare"], t), default=None)
    return {"byType": out, "articlesTyped": len(rows),
            "highestSurvival": best,
            "question": "does who discovers an authority first predict what "
                        "happens to it? This is not the aggregate lead-lag "
                        "test and does not answer it.",
            "limit": "left-censored articles -- first seen in the opening two "
                     "quarters -- are excluded, and party visibility depends "
                     "on the publisher reproducing submissions."}


# ---------------------------------------------------------- PHASES 10 & 11
def source_dynamics(comp, scorable):
    """Which newly appearing doctrinal sources persist, and which diffuse?"""
    per = defaultdict(lambda: defaultdict(Counter))
    seen_where = defaultdict(lambda: defaultdict(set))
    jcount = defaultdict(lambda: defaultdict(set))
    cities = defaultdict(lambda: defaultdict(set))
    for r in comp:
        if r["voice"] != "court":
            continue
        p = r["p"]
        per[r["cid"]][p][r["instW"] or "NONE"] += 1
        seen_where[r["cid"]][p].add(r["artW"] or "NONE")
        jcount[r["cid"]][p].add(r["j"])
        cities[r["cid"]][p].add(r["city"])
    idx = {p: i for i, p in enumerate(P)}
    rows = []
    for cid in sorted(per):
        ps = [p for p in P if sum(per[cid][p].values()) > 0]
        if not ps:
            continue
        p0 = ps[0]
        i0 = idx[p0]
        # features available AT EMERGENCE only
        f = {"source": cid, "firstPeriod": LBL[i0],
             "firstQuarterJudgments": len(jcount[cid][p0]),
             "firstQuarterCodes": len([k for k in per[cid][p0] if k != "NONE"]),
             "firstQuarterArticles": len(
                 [k for k in seen_where[cid][p0] if k != "NONE"]),
             "firstQuarterCities": len(cities[cid][p0])}
        later = [p for p in P[i0 + 1:] if LBL[idx[p]] in scorable]
        present = [p for p in later if sum(per[cid][p].values()) > 0]
        f["laterScorablePeriods"] = len(later)
        f["periodsPresent"] = len(present)
        f["persistenceShare"] = (round(len(present) / len(later), 4)
                                 if later else None)
        f["state"] = ("PERSISTENT" if (f["persistenceShare"] or 0) >= 0.8
                      else "EMERGING" if (f["persistenceShare"] or 0) >= 0.4
                      else "DISAPPEARED" if later else "TOO_NEW")
        # diffusion: codes, articles and cities reached by +1, +2, +4
        for h in (1, 2, 4):
            j = i0 + h
            if j < len(P):
                f[f"codesAtPlus{h}"] = len(
                    {k for x in range(i0, j + 1) for k in per[cid][P[x]]
                     if k != "NONE"})
                f[f"citiesAtPlus{h}"] = len(
                    {c for x in range(i0, j + 1) for c in cities[cid][P[x]]})
        rows.append(f)
    persistent = [r for r in rows if r["state"] == "PERSISTENT"]
    gone = [r for r in rows if r["state"] == "DISAPPEARED"]

    def mean(g, k):
        v = [r[k] for r in g if r.get(k) is not None]
        return round(sum(v) / len(v), 3) if v else None
    return {
        "sourcesTracked": len(rows),
        "byState": dict(sorted(Counter(r["state"] for r in rows).items())),
        "emergenceFeaturesByOutcome": {
            "PERSISTENT": {k: mean(persistent, k) for k in
                           ("firstQuarterJudgments", "firstQuarterCodes",
                            "firstQuarterArticles", "firstQuarterCities")},
            "DISAPPEARED": {k: mean(gone, k) for k in
                            ("firstQuarterJudgments", "firstQuarterCodes",
                             "firstQuarterArticles", "firstQuarterCities")}},
        "diffusion": sorted(
            [{k: r[k] for k in r if k != "state"} | {"state": r["state"]}
             for r in rows],
            key=lambda r: (-(r.get("periodsPresent") or 0), r["source"]))[:12],
        "frozenRuleForFutureEntrants": (
            "a new code-local source with more first-quarter judgments, more "
            "articles and more cities at emergence is predicted to persist. "
            "The direction is read off the table above; no threshold is "
            "issued as a forecast until a future entrant can score it."),
        "limit": "the identity universe has 28 members, so 'new' means new "
                 "beside that code in this window, never new to Saudi law. "
                 "Diffusion is spread, not influence.",
    }


# --------------------------------------------------------------- PHASE 18
def velocity(hz):
    """Components, not a composite. How fast does a rule become practice?"""
    rows = hz["phase6_newLawMonitor"]["rows"]
    inw = [r for r in rows if r.get("censoringRisk") == "IN_WINDOW"]
    got = [r for r in inw if r["quartersToTop50"] is not None]

    def med(v):
        v = sorted(v)
        return v[len(v) // 2] if v else None
    return {
        "components": {
            "BAR_UPTAKE_LATENCY": "quarters from first court citation to "
                                  "first party citation, signed",
            "COURT_UPTAKE_LATENCY": "quarters from the instrument's first "
                                    "appearance anywhere to its first court "
                                    "citation",
            "CORE_ENTRY_LATENCY": "quarters from first court citation to "
                                  "top-50 entry",
            "COMPANION_FORMATION_LATENCY": "quarters from first court "
                                           "citation to a persistent local "
                                           "companion",
            "STATUTORY_UPTAKE_LATENCY": "quarters from COMMENCEMENT to first "
                                        "court citation"},
        "measurableNow": ["CORE_ENTRY_LATENCY", "BAR_UPTAKE_LATENCY"],
        "notMeasurable": {
            "STATUTORY_UPTAKE_LATENCY": "commencement dates are not held per "
                                        "instrument in the registry, so "
                                        "latency is measured from first "
                                        "OBSERVED use, not from the day the "
                                        "rule took effect",
            "COMPANION_FORMATION_LATENCY": "the identity layer starts at 1443 "
                                           "and only four codes carry enough "
                                           "local attachment"},
        "inWindowInstruments": len(inw),
        "reachedTop50": len(got),
        "medianCoreEntryLatencyQuarters": med(
            [r["quartersToTop50"] for r in got]),
        "medianBarUptakeLatencyQuarters": med(
            [r["partyBeforeCourtQuarters"] for r in inw
             if r.get("partyBeforeCourtQuarters") is not None]),
        "referenceCase": next((r for r in inw
                               if r["instrument"] == "civil_transactions_law"),
                              None),
    }


# --------------------------------------------------------------- PHASE 20
def publication_gate(fs):
    """Frozen rules for voiding a score when the observation system breaks."""
    pub = fs.get("publicationProfile", {})
    rows = pub.get("byPeriod", [])
    if not rows:
        return {"verdict": "NO_PROFILE"}
    hist = rows[:-1] if len(rows) > 4 else rows

    def band(key):
        v = [r[key] for r in hist]
        v.sort()
        return {"min": v[0], "max": v[-1],
                "median": v[len(v) // 2]}
    keys = ["medianReasonChars", "shareWithReasons", "share_feesClaim",
            "share_damagesClaim", "share_proofDispute"]
    return {
        "what": "observation-system health. A forecast is not scored in a "
                "quarter whose publication regime broke, and the decision "
                "uses these frozen bands rather than the forecast's own "
                "error.",
        "historicalBands": {k: band(k) for k in keys},
        "voidRules": [
            "VOID_DATA_SHIFT if judgments with authority fall below the "
            "maturity rule's floor",
            "VOID_DATA_SHIFT if median reasons length falls outside the "
            "historical band by more than 50 per cent of the band's own width",
            "VOID_DATA_SHIFT if any claim-family share moves more than 0.20 "
            "in a single quarter, which is above every move observed",
            "otherwise the quarter is scored, and a miss is a miss"],
        "decisionRule": "the void decision is made from these bands BEFORE "
                        "the forecast error is computed, and never after.",
        "largestObservedQuarterMove": {
            k: pub["compositionSwings"][k]["maxQuarterOnQuarterChange"]
            for k in keys if k in pub.get("compositionSwings", {})},
    }


# --------------------------------------------------------------- PHASE 21
def refresh_window(fs):
    """Not a detector: a forecast of WHEN a snapshot needs rebuilding."""
    mis = fs["temporalMisalignment"]
    rows = []
    for h in ("h1", "h2", "h4"):
        if h in mis:
            m = mis[h]
            rows.append({"h": int(h[1:]),
                         "top50Displaced": m["meanTop50DisplacedPct"],
                         "rankGap": m["meanRankDisplacementTop200"],
                         "contentGap": m["meanCitationShareToNeverSeenArticles"],
                         "folds": m["folds"]})
    first = {}
    for name, key, thr in (("TOP50_DISPLACEMENT", "top50Displaced", 30.0),
                           ("RANK_GAP", "rankGap", 35.0),
                           ("CONTENT_GAP", "contentGap", 0.10)):
        first[name] = next((r["h"] for r in rows if r[key] >= thr), None)
    due = min([v for v in first.values() if v], default=None)
    return {
        "profile": rows, "firstCrossing": first,
        "REFRESH_DUE_WINDOW": (f"{due}Q" if due else "ABSTAIN"),
        "drivingTrigger": min(
            (k for k, v in first.items() if v), key=lambda k: (first[k], k),
            default=None),
        "calibration": "read off 13, 12 and 10 rolling folds at horizons 1, 2 "
                       "and 4. It is a historical rate, not a promise about "
                       "any one snapshot.",
        "issuedAs": "a forecast with a band, not a detector: a snapshot taken "
                    "at 1446Q2 is predicted to need refresh within one "
                    "quarter, and the claim is wrong if displacement stays "
                    "below 30 per cent for two.",
    }


# --------------------------------------------------------------- PHASE 22
def companion_refresh(comp, scorable):
    """Different legal objects need different refresh policies."""
    per = defaultdict(lambda: defaultdict(Counter))
    for r in comp:
        if r["voice"] == "court" and r["instW"]:
            per[r["instW"]][r["p"]][r["cid"]] += 1
    out = {}
    for code in sorted(per):
        ps = [p for p in P if sum(per[code][p].values()) >= 60
              and LBL[PKEY[p]] in scorable]
        if len(ps) < 4:
            out[code] = {"periods": len(ps), "class": "LOW_SUPPORT"}
            continue
        js = []
        for a, b in zip(ps, ps[1:]):
            ta = set(F.top(per[code][a], 3))
            tb = set(F.top(per[code][b], 3))
            js.append(len(ta & tb) / len(ta | tb))
        m = sum(js) / len(js)
        out[code] = {
            "periods": len(ps), "steps": len(js),
            "meanTop3Jaccard": round(m, 4),
            "minTop3Jaccard": round(min(js), 4),
            "class": ("STABLE" if m >= 0.85 else
                      "VARIABLE" if m >= 0.6 else "FAST_MOVING"),
            "suggestedRefresh": ("annual" if m >= 0.85 else
                                 "two quarters" if m >= 0.6 else "quarterly")}
    return {"byCode": out,
            "use": "a retrieval system does not need one refresh policy. A "
                   "STABLE companion set can be rebuilt annually; a "
                   "FAST_MOVING one cannot.",
            "noProductBuild": "this is a measurement, not an implementation."}


# ---------------------------------------------------------- PHASES 26 & 32
def calibration(S, hz):
    """Bands only if they map to observed hit rates; otherwise rank only."""
    en = hz["phase4_5_entrants"]
    folds = en.get("byFold", [])
    if len(folds) < 5:
        return {"verdict": "INSUFFICIENT_FOLDS_USE_RANK_ONLY"}
    ps = [f["precision"]["courtShare"] for f in folds]
    ps.sort()
    lo, mid, hi = ps[len(ps) // 4], ps[len(ps) // 2], ps[3 * len(ps) // 4]
    spread = ps[-1] - ps[0]
    return {
        "target": "top-50 entrants, ranked by court share",
        "foldPrecisionQuartiles": {"p25": round(lo, 4), "median": round(mid, 4),
                                   "p75": round(hi, 4)},
        "range": [round(ps[0], 4), round(ps[-1], 4)],
        "verdict": ("RANK_ONLY" if spread > 0.35 else "BANDS_PERMITTED"),
        "why": ("fold-to-fold precision ranges from "
                f"{round(ps[0], 4)} to {round(ps[-1], 4)}. A HIGH/MEDIUM/LOW "
                "label would have to map onto hit rates that are stable "
                "enough to mean something, and these are not. The forecast "
                "therefore issues a RANKED LIST and no probabilities."),
        "forbidden": "intuitive confidence labels with no empirical mapping.",
    }


def event_backtest(S, hz):
    """PHASE 31-32: retrospective pseudo-prospective calibration.

    Two instruments whose arrival is dated by legislation rather than by us.
    Pretend the cutoff is their first observed court quarter, apply the same
    rules, and ask what the scanner would have said. Labelled clearly: these
    are RETROSPECTIVE PSEUDO-PROSPECTIVE folds. They calibrate a method and
    are not prospective successes.
    """
    rows = {r["instrument"]: r for r in hz["phase6_newLawMonitor"]["rows"]}
    med = hz["phase6_newLawMonitor"]["medianQuartersToTop50"]
    out = {}
    for inst in ("civil_transactions_law", "evidence_law"):
        r = rows.get(inst)
        if not r:
            continue
        i0 = LBL.index(r["firstCourtQuarter"])
        s0 = S[P[i0]]
        cn = sum(s0["courtStat"].values()) or 1
        pn = sum(s0["partyStat"].values()) or 1
        c0 = sum(v for (ins, _a), v in s0["courtStat"].items() if ins == inst) / cn
        p0 = sum(v for (ins, _a), v in s0["partyStat"].items() if ins == inst) / pn
        arts = len({a for (ins, a) in s0["courtStat"] if ins == inst})
        pred = ("WITHIN_2_QUARTERS" if med is not None and med <= 2
                else "WITHIN_4_QUARTERS")
        actual = r["quartersToTop50"]
        out[inst] = {
            "cutoffQuarter": r["firstCourtQuarter"],
            "knownAtCutoff": {"courtShare": round(c0, 5),
                              "partyShare": round(p0, 5),
                              "distinctArticles": arts,
                              "courtBarRatio": round(c0 / p0, 3) if p0 else None},
            "ruleApplied": "median core-entry latency of in-window arrivals "
                           f"({med} quarters)",
            "prediction": pred,
            "actualQuartersToTop50": actual,
            "hit": (actual is not None and
                    (actual <= 2 if pred == "WITHIN_2_QUARTERS" else actual <= 4)),
            "label": "RETROSPECTIVE_PSEUDO_PROSPECTIVE",
        }
    return {
        "cases": out,
        "hits": sum(1 for v in out.values() if v["hit"]),
        "cases_n": len(out),
        "label": "RETROSPECTIVE_PSEUDO_PROSPECTIVE",
        "notForesight": "these folds calibrate the rule. They are not "
                        "prospective evidence and may never be cited as the "
                        "observatory having anticipated anything.",
        "leakageNote": "the median latency used as the rule is computed over "
                       "in-window arrivals INCLUDING these two, so the "
                       "calibration is optimistic. With two clean cases there "
                       "is no honest way to hold them out and still have a "
                       "rule.",
    }


def registry_audit():
    """PHASE 3/35: prospective versus backfilled, computed from timestamps."""
    if not REG.exists():
        return {"verdict": "NO_REGISTRY"}
    reg = json.loads(REG.read_text(encoding="utf-8"))
    cut = reg["prospectiveFrom"]
    rows = []
    for e in reg["signals"]:
        cls = ("PROSPECTIVE_CAPTURE" if e["first_recorded_at"] > cut
               else "BACKFILLED_EVENT")
        rows.append({"event_id": e["event_id"], "type": e["event_type"],
                     "known_at": e["known_at"],
                     "first_recorded_at": e["first_recorded_at"],
                     "declared": e["capture_class"], "computed": cls,
                     "agrees": cls == e["capture_class"],
                     "sourceGrade": e["source_grade"]})
    bad = [r for r in rows if not r["agrees"]]
    return {
        "prospectiveFrom": cut,
        "signals": len(rows),
        "byComputedClass": dict(sorted(Counter(
            r["computed"] for r in rows).items())),
        "bySourceGrade": dict(sorted(Counter(
            r["sourceGrade"] for r in rows).items())),
        "declarationMismatches": bad,
        "enforcement": "capture class is COMPUTED from first_recorded_at "
                       "against the registry's own creation date, not "
                       "declared. A mismatch is a bug and is listed above.",
        "consequence": ("every seed entry is BACKFILLED by construction, "
                        "because the registry was created today. The first "
                        "PROSPECTIVE_CAPTURE will be the first signal "
                        "recorded after this commit, and only those may ever "
                        "support a claim that the observatory anticipated "
                        "something."),
        "rows": rows,
    }


def main():
    rows, dates, _ = F.load()
    S = F.build(rows)
    comp = []
    for src in (F.COMPANIONS, F.BACKFILL):
        if not src.exists():
            continue
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
    fs, hz = J("foresight_results.json"), J("horizon_results.json")
    scorable = set(hz["phase3_maturityRule"]["scorable"])
    res = {
        "what": "SAUDI LEGAL LEADING-INDICATOR OBSERVATORY: the layer that "
                "sits before the judgment corpus in time.",
        "doesNotTouch": "PROSPECTIVE_DETECTOR_ERA_1 is frozen. No detector is "
                        "retuned, no threshold moved, no issued forecast "
                        "changed, and the maturity rule is used as it stands.",
        "phase7_featureAblation": ablation(S),
        "phase8_rareArticleDiscovery": rare_discovery(S),
        "phase9_firstMoverTypology": first_mover(S),
        "phase10_11_sourceDynamics": source_dynamics(comp, scorable),
        "phase18_transitionVelocity": velocity(hz),
        "phase20_publicationGate": publication_gate(fs),
        "phase21_refreshWindow": refresh_window(fs),
        "phase22_companionRefresh": companion_refresh(comp, scorable),
        "phase26_calibration": calibration(S, hz),
        "phase31_32_eventBacktest": event_backtest(S, hz),
        "phase3_35_registryAudit": registry_audit(),
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"ablation: {res['phase7_featureAblation'].get('verdict')}")
    print(f"rare-article discovery: "
          f"{res['phase8_rareArticleDiscovery'].get('verdict')}")
    fm = res["phase9_firstMoverTypology"]["byType"]
    print("first mover: " + ", ".join(
        f"{k} n={v.get('n')} survival={v.get('meanSurvivalShare')}"
        for k, v in fm.items()))
    print(f"source states: {res['phase10_11_sourceDynamics']['byState']}")
    print(f"refresh window: {res['phase21_refreshWindow']['REFRESH_DUE_WINDOW']}")
    print(f"calibration: {res['phase26_calibration'].get('verdict')}")
    print(f"registry: {res['phase3_35_registryAudit'].get('byComputedClass')}")
    print(f"-> {OUT.name}")


if __name__ == "__main__":
    main()
