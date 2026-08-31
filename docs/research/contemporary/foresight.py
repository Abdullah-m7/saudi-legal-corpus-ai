#!/usr/bin/env python3
"""Can this repository say anything about next period, and be scored for it?

The programme so far describes what happened and what is happening. This asks
the third question -- what is likely to happen next -- under one rule: no
forecast that cannot later be scored, and no claim of predictive skill without
a baseline that a lazy forecaster would have used anyway.

Everything here is TEMPORAL. There is no random split anywhere in this file.
Every evaluation is rolling-origin: fit on periods strictly before p, predict
p, move the origin forward. A model that beats `last period` on one fold and
loses on the next has not shown skill, so mean AND worst-fold skill are
reported for every target.

PERIODS. Hijri quarters, from 1442Q1 to 1446Q2. The corpus carries judgments
dated later, and they are excluded: 1446Q3 has 184 judgments and 1446Q4 has 7,
against a median quarter of about 1,500. That is publication lag, not a
collapse in Saudi litigation, and forecasting into it would be forecasting the
publisher.

WHAT IS DELIBERATELY NOT HERE. No detection of AI-written text from style, no
prediction of any judge or any case outcome, no causal claim from a
before-and-after comparison, and no forecast issued for a target whose
backtest did not beat its baseline.

    python3 foresight.py
"""
import gzip
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
MENTIONS = HERE / "authority_mentions.jsonl.gz"
COMPANIONS = HERE / "companion_layer.jsonl.gz"
BACKFILL = HERE / "companion_layer_backfill.jsonl.gz"
INSTREG = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
DATES = HERE / "judgment_dates.json.gz"
DOCKET = HERE / "docket_layer.jsonl.gz"
OUT = HERE / "foresight_results.json"

# 1442Q1 .. 1446Q2. The tail is excluded for publication lag, not for taste:
# the counts that justify the cut are reported in the results file.
FIRST, LAST_P = (1442, 1), (1446, 2)
MIN_TRAIN = 4          # quarters of history before the first forecast fold
COURT = "court_reasoning"
PARTY = "party_argument"
WIDE_PARTY = ("party_argument", "recital")
NAMED_FIQH = ("fiqh.jurist", "fiqh.book")
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")


def periods():
    out, y, q = [], FIRST[0], FIRST[1]
    while (y, q) <= LAST_P:
        out.append((y, q))
        q += 1
        if q == 5:
            y, q = y + 1, 1
    return out


P = periods()
PKEY = {p: i for i, p in enumerate(P)}
LBL = [f"{y}Q{q}" for y, q in P]


def load():
    with gzip.open(DATES, "rt", encoding="utf-8") as fh:
        dates = {k: tuple(v) for k, v in json.load(fh)["dates"].items()}
    rows, excluded = [], Counter()
    with gzip.open(MENTIONS, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r.get("q"):
                continue
            d = dates.get(r["j"])
            if not d:
                continue
            p = (d[0], (d[1] - 1) // 3 + 1)
            if p not in PKEY:
                excluded[f"{d[0]}Q{(d[1] - 1) // 3 + 1}"] += 1
                continue
            r["p"] = p
            rows.append(r)
    return rows, dates, excluded


# ------------------------------------------------------------------ models
def ma(h, k):
    return sum(h[-k:]) / len(h[-k:]) if h else None


def predictors():
    """Every predictor sees only the history up to, not including, the fold."""
    return {
        "LAST": lambda h: h[-1] if h else None,
        "MA2": lambda h: ma(h, 2),
        "MA3": lambda h: ma(h, 3),
        "MEAN": lambda h: ma(h, len(h)) if h else None,
        "DRIFT": lambda h: (h[-1] + (h[-1] - h[-2])) if len(h) >= 2
                 else (h[-1] if h else None),
        "SHRINK": lambda h: (0.5 * h[-1] + 0.5 * ma(h, 3)) if h else None,
    }


BASELINES = ("LAST", "MA2", "MA3", "MEAN")
MODELS = ("DRIFT", "SHRINK")


def scalar_backtest(series, label, min_train=MIN_TRAIN):
    """series: list of values aligned to P, None where the period is empty."""
    fns = predictors()
    err = defaultdict(list)
    folds = []
    for i in range(min_train, len(series)):
        h = [v for v in series[:i] if v is not None]
        y = series[i]
        if y is None or len(h) < min_train:
            continue
        row = {"period": LBL[i], "actual": round(y, 5)}
        for name, f in fns.items():
            pv = f(h)
            if pv is None:
                continue
            err[name].append(abs(pv - y))
            row[name] = round(pv, 5)
        folds.append(row)
    if len(folds) < 5:
        return {"target": label, "verdict": "INSUFFICIENT_TEMPORAL_DEPTH",
                "folds": len(folds),
                "series": {LBL[i]: (round(v, 5) if v is not None else None)
                           for i, v in enumerate(series)}}
    mae = {k: sum(v) / len(v) for k, v in err.items()}
    best_base = min(BASELINES, key=lambda k: (mae.get(k, 9e9), k))
    out = {"target": label, "folds": len(folds), "periods": [f["period"] for f in folds],
           "mae": {k: round(v, 5) for k, v in sorted(mae.items())},
           "bestBaseline": best_base, "bestBaselineMae": round(mae[best_base], 5),
           "series": {LBL[i]: (round(v, 5) if v is not None else None)
                      for i, v in enumerate(series)}}
    skill = {}
    for m in MODELS:
        if m not in mae:
            continue
        per = [1 - (abs(f[m] - f["actual"]) /
                    abs(f[best_base] - f["actual"]))
               if f.get(m) is not None and f.get(best_base) is not None
               and abs(f[best_base] - f["actual"]) > 1e-12 else None
               for f in folds]
        per = [x for x in per if x is not None]
        skill[m] = {
            "meanSkillVsBestBaseline": round(1 - mae[m] / mae[best_base], 4)
                                       if mae[best_base] else None,
            "worstFoldSkill": round(min(per), 4) if per else None,
            "foldsBeatingBaseline": sum(1 for x in per if x > 0),
            "foldsScored": len(per),
        }
    out["modelSkill"] = skill
    best_model = max(MODELS, key=lambda m: (skill.get(m, {}).get(
        "meanSkillVsBestBaseline") or -9, m))
    ms = skill.get(best_model, {})
    out["verdict"] = (
        "FORECASTABLE" if (ms.get("meanSkillVsBestBaseline") or 0) > 0.05
        and (ms.get("foldsBeatingBaseline") or 0) > len(folds) / 2
        else "PERSISTENCE_NOT_BEATEN")
    out["bestModel"] = best_model
    return out


# --------------------------------------------------- the period aggregates
def build(rows):
    """Everything downstream reads these per-period counters."""
    S = {p: {"courtStat": Counter(), "partyStat": Counter(),
             "wideStat": Counter(), "courtInst": Counter(),
             "courtType": Counter(), "courtRule": Counter(),
             "partyRule": Counter(),
             "judgments": set(), "courtJ": defaultdict(set),
             "partyJ": defaultdict(set)} for p in P}
    for r in rows:
        s = S[r["p"]]
        s["judgments"].add(r["j"])
        role, t = r["role"], r["t"]
        key = (r.get("inst"), r.get("art"))
        if role == COURT:
            s["courtType"][t] += 1
            s["courtRule"][r["r"]] += 1
            if t == "statute" and r.get("inst") and r.get("art") is not None:
                s["courtStat"][key] += 1
                s["courtInst"][r["inst"]] += 1
                s["courtJ"][key].add(r["j"])
        if role == PARTY:
            s["partyRule"][r["r"]] += 1
            if t == "statute" and r.get("inst") and r.get("art") is not None:
                s["partyStat"][key] += 1
                s["partyJ"][key].add(r["j"])
        if role in WIDE_PARTY and t == "statute" and r.get("inst") \
                and r.get("art") is not None:
            s["wideStat"][key] += 1
    return S


def share(c, key):
    n = sum(c.values())
    return c[key] / n if n else None


def top(c, k):
    return [x for x, _ in sorted(c.items(), key=lambda kv: (-kv[1], str(kv[0])))[:k]]


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if (a | b) else None


# ------------------------------------------- TARGET FAMILY 1: article rank
def article_backtest(S, k=50, min_train=MIN_TRAIN):
    """Predict next period's top-k court article set, and the shares.

    The universe is rebuilt inside every fold from the training periods only.
    """
    folds = []
    for i in range(min_train, len(P)):
        train = [S[P[x]] for x in range(i)]
        test = S[P[i]]
        if sum(test["courtStat"].values()) < 200:
            continue
        hist = Counter()
        for s in train:
            hist.update(s["courtStat"])
        uni = [a for a, v in hist.items() if v >= 5]
        if len(uni) < k * 2:
            continue
        prev = top(train[-1]["courtStat"], k)
        ma3 = Counter()
        for s in train[-3:]:
            n = sum(s["courtStat"].values()) or 1
            for a, v in s["courtStat"].items():
                ma3[a] += v / n
        actual = top(test["courtStat"], k)
        # share-level MAE over the training universe
        def sh(c):
            n = sum(c.values()) or 1
            return {a: c[a] / n for a in uni}
        y = sh(test["courtStat"])
        preds = {"LAST": sh(train[-1]["courtStat"]),
                 "MA3": {a: ma3[a] / len(train[-3:]) for a in uni},
                 "ALLHIST": sh(hist)}
        mae = {m: sum(abs(preds[m][a] - y[a]) for a in uni) / len(uni)
               for m in preds}
        folds.append({
            "period": LBL[i], "universe": len(uni),
            "courtCitations": sum(test["courtStat"].values()),
            "topKJaccard_prevPeriod": round(jaccard(prev, actual), 4),
            "topKJaccard_ma3": round(jaccard(top(ma3, k), actual), 4),
            "shareMae": {m: round(v, 6) for m, v in sorted(mae.items())},
            "newEntrants": len(set(actual) - set(prev)),
        })
    if len(folds) < 3:
        return {"verdict": "INSUFFICIENT_TEMPORAL_DEPTH", "folds": len(folds)}
    m = lambda f, key: sum(x[key] for x in folds) / len(folds)
    return {
        "k": k, "folds": len(folds), "periods": [f["period"] for f in folds],
        "meanTopKJaccard_prevPeriod": round(m(folds, "topKJaccard_prevPeriod"), 4),
        "worstTopKJaccard_prevPeriod": round(
            min(f["topKJaccard_prevPeriod"] for f in folds), 4),
        "meanTopKJaccard_ma3": round(m(folds, "topKJaccard_ma3"), 4),
        "meanNewEntrantsPerPeriod": round(m(folds, "newEntrants"), 2),
        "shareMaeMean": {k2: round(sum(f["shareMae"][k2] for f in folds)
                                   / len(folds), 6)
                         for k2 in sorted(folds[0]["shareMae"])},
        "byFold": folds,
        "verdict": ("MA3_BEATS_PERSISTENCE"
                    if m(folds, "topKJaccard_ma3") > m(folds, "topKJaccard_prevPeriod")
                    else "PERSISTENCE_NOT_BEATEN"),
    }


# ------------------------------------------- TARGET FAMILY 2: new entrants
def entrant_backtest(S, k=50, min_train=MIN_TRAIN):
    """Which articles ENTER the top-k next period, and does the bar know first?

    Every candidate is an article outside the current top-k. Three signals are
    scored against the base rate: how much the court already cites it, how
    much the BAR cites it, and its momentum. This is the hardest target in the
    file and the one where a lazy baseline is hardest to beat.
    """
    ev = []
    for i in range(min_train, len(P)):
        train, test = [S[P[x]] for x in range(i)], S[P[i]]
        if sum(test["courtStat"].values()) < 200:
            continue
        cur = set(top(train[-1]["courtStat"], k))
        nxt = set(top(test["courtStat"], k))
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
        for a in sorted(cand, key=str):
            ev.append({
                "period": LBL[i], "entered": a in nxt,
                "courtShare": train[-1]["courtStat"][a] / cn,
                "partyShare": train[-1]["partyStat"][a] / pn,
                "momentum": train[-1]["courtStat"][a] / cn - prev2[a] / p2n,
            })
    if not ev:
        return {"verdict": "INSUFFICIENT_TEMPORAL_DEPTH"}
    base = sum(1 for e in ev if e["entered"]) / len(ev)
    out = {"candidates": len(ev), "baseRate": round(base, 4),
           "periods": sorted({e["period"] for e in ev})}
    for sig in ("courtShare", "partyShare", "momentum"):
        byp = []
        for per in out["periods"]:
            rows = [e for e in ev if e["period"] == per]
            n_true = sum(1 for e in rows if e["entered"])
            if not n_true:
                continue
            rows.sort(key=lambda e: (-e[sig], str(e)))
            hit = sum(1 for e in rows[:n_true] if e["entered"])
            byp.append(hit / n_true)
        out[sig] = {
            "precisionAtNTrue": round(sum(byp) / len(byp), 4) if byp else None,
            "periodsScored": len(byp),
            "liftOverBaseRate": round((sum(byp) / len(byp)) / base, 2)
                                if byp and base else None,
        }
    best = max(("courtShare", "partyShare", "momentum"),
               key=lambda s: (out[s]["precisionAtNTrue"] or 0, s))
    out["bestSignal"] = best
    out["verdict"] = ("SIGNAL_ABOVE_BASE_RATE"
                      if (out[best]["precisionAtNTrue"] or 0) > base * 1.5
                      else "NO_USABLE_SIGNAL")
    return out


# --------------------------------------------- TARGET FAMILY 3: lead - lag
def leadlag(S, min_train=MIN_TRAIN):
    """PARTY_USE(article, t) -> COURT_USE(article, t+1), against court
    persistence. Association only: the word influence is not used, and a
    shared cause -- a new statute both sides discover at once -- is not
    excluded by anything measured here."""
    folds = []
    for i in range(min_train, len(P)):
        prev, test = S[P[i - 1]], S[P[i]]
        if sum(test["courtStat"].values()) < 200:
            continue
        hist = Counter()
        for x in range(i):
            hist.update(S[P[x]]["courtStat"])
        uni = sorted([a for a, v in hist.items() if v >= 5], key=str)
        if len(uni) < 50:
            continue
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
        # does the bar add anything to the bench's own persistence?
        rc, rp = r(xc, y), r(xp, y)
        resid = None
        rcp = r(xc, xp)
        if None not in (rc, rp, rcp) and abs(1 - rcp ** 2) > 1e-9:
            # partial correlation of party signal with next-period court use,
            # holding this period's court use fixed
            resid = (rp - rc * rcp) / math.sqrt((1 - rc ** 2) * (1 - rcp ** 2))
        folds.append({"period": LBL[i], "articles": len(uni),
                      "courtPersistenceR": round(rc, 4) if rc else None,
                      "partyLeadR": round(rp, 4) if rp else None,
                      "partyPartialR": round(resid, 4) if resid else None})
    if len(folds) < 3:
        return {"verdict": "INSUFFICIENT_TEMPORAL_DEPTH", "folds": len(folds)}
    mp = [f["partyPartialR"] for f in folds if f["partyPartialR"] is not None]
    return {
        "folds": len(folds),
        "meanCourtPersistenceR": round(
            sum(f["courtPersistenceR"] for f in folds) / len(folds), 4),
        "meanPartyLeadR": round(
            sum(f["partyLeadR"] for f in folds) / len(folds), 4),
        "meanPartyPartialR": round(sum(mp) / len(mp), 4) if mp else None,
        "worstPartyPartialR": round(min(mp), 4) if mp else None,
        "foldsWithPositivePartial": sum(1 for x in mp if x > 0),
        "byFold": folds,
        "verdict": ("PARTY_ADDS_ABOVE_COURT_PERSISTENCE"
                    if mp and sum(mp) / len(mp) > 0.05
                    and sum(1 for x in mp if x > 0) > len(mp) / 2
                    else "NO_LEAD_LAG_ASSOCIATION_ABOVE_PERSISTENCE"),
        "note": "LEAD-LAG ASSOCIATION, not influence. A provision both sides "
                "discover at the same time produces this pattern too.",
    }


# ------------------------------------- TARGET FAMILY 4: retrieval ageing
def decay(S, comp, min_train=MIN_TRAIN):
    """Freeze a retrieval universe at t; how much of t+h does it still cover?

    Five architectures, all built from the same corpus and differing only in
    what they are allowed to remember. No language model is involved: this is
    a coverage measurement, and coverage is the ceiling on any system built on
    that universe.
    """
    out = {}
    for h in (1, 2, 4):
        arch = defaultdict(list)
        for i in range(min_train, len(P) - h):
            train = [S[P[x]] for x in range(i + 1)]
            test = S[P[i + h]]
            tn = sum(test["courtStat"].values())
            if tn < 200:
                continue
            court, whole, recent = set(), set(), set()
            for s in train:
                court |= set(s["courtStat"])
                whole |= set(s["courtStat"]) | set(s["wideStat"]) | set(s["partyStat"])
            for s in train[-2:]:
                recent |= set(s["courtStat"])
            cov = lambda U: sum(v for a, v in test["courtStat"].items()
                                if a in U) / tn
            arch["COURT_REASONING"].append(cov(court))
            arch["WHOLE_JUDGMENT"].append(cov(whole))
            arch["RECENT_COURT_2Q"].append(cov(recent))
            arch["STATUTE_ONLY_TOP50"].append(cov(set(top(train[-1]["courtStat"], 50))))
            arch["STATUTE_ONLY_TOP200"].append(cov(set(top(train[-1]["courtStat"], 200))))
        if arch:
            out[f"h{h}"] = {
                "folds": len(next(iter(arch.values()))),
                "meanCoverage": {k: round(sum(v) / len(v), 4)
                                 for k, v in sorted(arch.items())},
                "worstCoverage": {k: round(min(v), 4)
                                  for k, v in sorted(arch.items())},
            }
    # the doctrinal-companion half of the universe, on the years it exists
    if comp:
        cp = defaultdict(Counter)
        for r in comp:
            if r["voice"] == "court":
                cp[r["p"]][r["cid"]] += 1
        ks = [p for p in P if sum(cp[p].values()) >= 100]
        rows = []
        for a, b in zip(ks, ks[1:]):
            uni = set(cp[a])
            tot = sum(cp[b].values())
            rows.append({"from": LBL[PKEY[a]], "to": LBL[PKEY[b]],
                         "coverage": round(sum(v for s, v in cp[b].items()
                                               if s in uni) / tot, 4),
                         "top3Coverage": round(
                             sum(v for s, v in cp[b].items()
                                 if s in set(top(cp[a], 3))) / tot, 4)})
        out["doctrinalCompanionUniverse"] = {
            "periods": [LBL[PKEY[p]] for p in ks], "byStep": rows,
            "meanCoverage": round(sum(r["coverage"] for r in rows) / len(rows), 4)
                            if rows else None,
            "note": "the identity universe exists for 1444-1446 only and is "
                    "bounded by authority.py's vocabulary, so this is an "
                    "upper bound on how well a frozen companion set ages",
        }
    return out


# ----------------------------- TARGET FAMILY 5: doctrinal companion sets
def companion_backtest(comp, k=3, min_n=60):
    """Does this quarter's top-k companion set predict next quarter's?

    Two periods of history is not a backtest, so this is reported with its
    fold count in the open and is the weakest evidence in the file. The
    identity layer exists for 1444-1446 only.
    """
    if not comp:
        return {"verdict": "NO_IDENTITY_LAYER"}
    per = defaultdict(lambda: defaultdict(Counter))
    for r in comp:
        if r["voice"] != "court" or not r["instW"]:
            continue
        per[r["instW"]][r["p"]][r["cid"]] += 1
    out = {}
    for code in sorted(per):
        ps = [p for p in P if sum(per[code][p].values()) >= min_n]
        if len(ps) < 4:
            out[code] = {"verdict": "INSUFFICIENT_TEMPORAL_DEPTH",
                         "periodsWithSupport": len(ps)}
            continue
        steps = []
        for a, b in zip(ps, ps[1:]):
            ta, tb = top(per[code][a], k), top(per[code][b], k)
            steps.append({"from": LBL[PKEY[a]], "to": LBL[PKEY[b]],
                          "jaccard": round(jaccard(ta, tb), 4),
                          "sameSet": set(ta) == set(tb),
                          "sameOrder": ta == tb,
                          "top1Held": ta[0] == tb[0]})
        out[code] = {
            "periodsWithSupport": len(ps),
            "steps": len(steps),
            "meanTopKJaccard": round(sum(x["jaccard"] for x in steps) / len(steps), 4),
            "worstTopKJaccard": round(min(x["jaccard"] for x in steps), 4),
            "sameSetShare": round(
                100 * sum(1 for x in steps if x["sameSet"]) / len(steps), 1),
            "sameOrderShare": round(
                100 * sum(1 for x in steps if x["sameOrder"]) / len(steps), 1),
            "top1HeldShare": round(
                100 * sum(1 for x in steps if x["top1Held"]) / len(steps), 1),
            "byStep": steps,
            "verdict": ("TOP_K_PERSISTENT" if
                        sum(x["jaccard"] for x in steps) / len(steps) >= 0.6
                        else "TOP_K_UNSTABLE"),
        }
    return out


# ------------------------------- TARGET FAMILY 6: a new code arriving live
def uptake(S, code="civil_transactions_law"):
    """The Civil Transactions Law enters the corpus inside the window.

    This is the one uptake curve the corpus actually contains, and it is worth
    stating on its own because it is the empirical anchor for every future
    claim about whether legal AI accelerates the discovery of new provisions:
    it is what uptake looked like WITHOUT any verified AI involvement.
    """
    rows = []
    firstC = firstP = firstTop50 = firstTop100 = None
    for i, p in enumerate(P):
        s = S[p]
        cn = sum(s["courtStat"].values())
        pn = sum(s["partyStat"].values())
        c = sum(v for (inst, _a), v in s["courtStat"].items() if inst == code)
        pv = sum(v for (inst, _a), v in s["partyStat"].items() if inst == code)
        arts = sorted({a for (inst, a) in s["courtStat"] if inst == code}, key=str)
        if c and firstC is None:
            firstC = LBL[i]
        if pv and firstP is None:
            firstP = LBL[i]
        if cn >= 200:
            t50 = {k for k in top(s["courtStat"], 50) if k[0] == code}
            t100 = {k for k in top(s["courtStat"], 100) if k[0] == code}
            if t50 and firstTop50 is None:
                firstTop50 = LBL[i]
            if t100 and firstTop100 is None:
                firstTop100 = LBL[i]
        rows.append({"period": LBL[i],
                     "courtShare": round(c / cn, 5) if cn else None,
                     "partyShare": round(pv / pn, 5) if pn else None,
                     "distinctArticlesCourt": len(arts)})
    return {"code": code, "firstCourtQuarter": firstC,
            "firstPartyQuarter": firstP,
            "firstQuarterInCourtTop50": firstTop50,
            "firstQuarterInCourtTop100": firstTop100,
            "quartersFromFirstCourtUseToTop50":
                (LBL.index(firstTop50) - LBL.index(firstC))
                if firstC and firstTop50 else None,
            "byPeriod": rows,
            "note": "commencement dates are not in the registry, so this is "
                    "latency inside the published corpus, not latency from "
                    "the day the code took effect."}


def speaker_aware(S, min_train=MIN_TRAIN):
    """High recall from the whole judgment, or precision from the bench?

    `decay` showed the whole-judgment universe covering slightly more of the
    next period than the court's own history. The speaker programme spent the
    whole project separating those voices, so the honest question is not which
    universe covers more -- it is what the extra coverage COSTS. So this
    measures the party-only remainder on its own: how many articles it adds,
    how much coverage they buy, and what share of them the court never cites.
    """
    out = []
    for i in range(min_train, len(P) - 1):
        train = [S[P[x]] for x in range(i + 1)]
        test = S[P[i + 1]]
        tn = sum(test["courtStat"].values())
        if tn < 200:
            continue
        court, whole = set(), set()
        for s in train:
            court |= set(s["courtStat"])
            whole |= set(s["courtStat"]) | set(s["wideStat"]) | set(s["partyStat"])
        party_only = whole - court
        cov = lambda U: sum(v for a, v in test["courtStat"].items()
                            if a in U) / tn
        hit = {a for a in party_only if a in test["courtStat"]}
        out.append({
            "period": LBL[i + 1],
            "courtUniverse": len(court),
            "partyOnlyAdded": len(party_only),
            "universeGrowthPct": round(100 * len(party_only) / len(court), 1),
            "coverageCourt": round(cov(court), 4),
            "coverageWhole": round(cov(whole), 4),
            "coverageAddedByPartyOnly": round(cov(whole) - cov(court), 4),
            "partyOnlyPrecision": round(len(hit) / len(party_only), 4)
                                  if party_only else None,
        })
    if len(out) < 3:
        return {"verdict": "INSUFFICIENT_TEMPORAL_DEPTH"}
    m = lambda k: sum(r[k] for r in out) / len(out)
    return {
        "folds": len(out), "byFold": out,
        "meanUniverseGrowthPct": round(m("universeGrowthPct"), 1),
        "meanCoverageAddedByPartyOnly": round(m("coverageAddedByPartyOnly"), 4),
        "meanPartyOnlyPrecision": round(m("partyOnlyPrecision"), 4),
        "coveragePointsPer10pctUniverseGrowth": round(
            100 * m("coverageAddedByPartyOnly") / (m("universeGrowthPct") / 10), 3),
        # the trade has to be priced, not just observed: two points of recall
        # for a fifth more index is a different bargain from half a point for
        # forty per cent more
        "verdict": ("HIGH_RECALL_WORTH_ITS_COST"
                    if m("coverageAddedByPartyOnly") >= 0.02
                    and m("partyOnlyPrecision") >= 0.15
                    else "HIGH_RECALL_COSTS_MORE_THAN_IT_BUYS"),
        "note": "coverage is recall over the court's own later citations. "
                "It is NOT a recommendation to retrieve whole judgments "
                "without role separation: the speaker programme measured what "
                "advocacy contributes to a whole-document count, and that "
                "contamination is exactly what partyOnlyPrecision prices.",
    }


def misalignment(S, comp, min_train=MIN_TRAIN):
    """How fast does a frozen legal-AI snapshot go stale, beyond recall?

    Recall decay asks what a frozen universe still contains. Staleness asks
    what it gets WRONG: articles it never heard of, a ranking that has moved,
    a top-50 that is no longer the top 50, companions it does not carry.
    """
    out = {}
    for h in (1, 2, 4):
        rows = []
        for i in range(min_train, len(P) - h):
            train = [S[P[x]] for x in range(i + 1)]
            test = S[P[i + h]]
            tn = sum(test["courtStat"].values())
            if tn < 200:
                continue
            uni = set()
            for s in train:
                uni |= set(s["courtStat"])
            frozen = Counter()
            for s in train:
                frozen.update(s["courtStat"])
            unseen = {a: v for a, v in test["courtStat"].items() if a not in uni}
            ft, tt = top(frozen, 50), top(test["courtStat"], 50)
            ranks_f = {a: r for r, a in enumerate(top(frozen, 200))}
            ranks_t = {a: r for r, a in enumerate(top(test["courtStat"], 200))}
            both = sorted(set(ranks_f) & set(ranks_t), key=str)
            disp = (sum(abs(ranks_f[a] - ranks_t[a]) for a in both) / len(both)
                    if both else None)
            rows.append({
                "period": LBL[i + h],
                "articlesNeverSeen": len(unseen),
                "citationShareToNeverSeenArticles": round(
                    sum(unseen.values()) / tn, 4),
                "top50Displaced": len(set(ft) - set(tt)),
                "top50DisplacedPct": round(100 * len(set(ft) - set(tt)) / 50, 1),
                "meanRankDisplacementTop200": round(disp, 2) if disp else None,
                "top10Held": len(set(top(frozen, 10)) & set(top(test["courtStat"], 10))),
            })
        if len(rows) >= 3:
            m = lambda k: round(sum(r[k] for r in rows if r[k] is not None)
                                / max(1, sum(1 for r in rows if r[k] is not None)), 4)
            out[f"h{h}"] = {
                "folds": len(rows),
                "meanCitationShareToNeverSeenArticles":
                    m("citationShareToNeverSeenArticles"),
                "meanTop50DisplacedPct": m("top50DisplacedPct"),
                "meanRankDisplacementTop200": m("meanRankDisplacementTop200"),
                "meanTop10Held": m("top10Held"),
                "byFold": rows,
            }
    # companions the frozen snapshot would not carry
    if comp:
        cp = defaultdict(lambda: defaultdict(Counter))
        for r in comp:
            if r["voice"] == "court" and r["instW"]:
                cp[r["instW"]][r["p"]][r["cid"]] += 1
        miss = []
        for code in sorted(cp):
            ps = [p for p in P if sum(cp[code][p].values()) >= 60]
            for a, b in zip(ps, ps[1:]):
                seen = set(cp[code][a])
                tot = sum(cp[code][b].values())
                new = sum(v for s, v in cp[code][b].items() if s not in seen)
                miss.append(new / tot)
        out["companionsNotInFrozenSet"] = {
            "steps": len(miss),
            "meanShareOfNextPeriodMentions": round(sum(miss) / len(miss), 4)
                                             if miss else None,
            "note": "small because the identity universe has 28 members, not "
                    "because doctrine is static",
        }
    out["articleVersionSupersession"] = {
        "verdict": "NOT_AVAILABLE",
        "why": "the corpus registry carries publication dates per INSTRUMENT, "
               "not per article version. Whether the text of article 16 at "
               "the time of a 1443 judgment differs from its text today "
               "cannot be answered from the metadata we hold, and this "
               "session does not reconstruct it.",
    }
    return out


def instrument_validity(S, dates):
    """The half of effective-law dating the registry can actually support."""
    try:
        reg = json.loads(INSTREG.read_text(encoding="utf-8"))
    except Exception:
        return {"verdict": "REGISTRY_UNREADABLE"}
    pub = {}
    for t in reg.get("tracks", []):
        h = t.get("publication_date_hijri") or ""
        m = re.match(r"^(\d{4})", str(h))
        if m:
            pub[t.get("track_id")] = int(m.group(1))
    rows = []
    for i, p in enumerate(P):
        n = ahead = 0
        for (inst, _a), v in S[p]["courtStat"].items():
            n += v
            y = pub.get(inst)
            if y and y > p[0]:
                ahead += v
        if n >= 200:
            rows.append({"period": LBL[i], "citations": n,
                         "toInstrumentsPublishedLater": ahead,
                         "pct": round(100 * ahead / n, 3)})
    if len(pub) < 10:
        return {"verdict": "INSUFFICIENT_REGISTRY_COVERAGE",
                "instrumentsWithPublicationYear": len(pub),
                "why": "only %d of the registry's tracks carry a parseable "
                       "hijri publication year, so the check would be "
                       "computed over almost nothing. Reported as unsupported "
                       "rather than as a zero." % len(pub),
                "limit": "instrument level only. Article-version history is "
                         "not held."}
    return {
        "instrumentsWithPublicationYear": len(pub),
        "byPeriod": rows,
        "meanPctToInstrumentsPublishedLater": round(
            sum(r["pct"] for r in rows) / len(rows), 3) if rows else None,
        "use": "a retrieval snapshot frozen at time t cannot contain an "
               "instrument published after t. This measures how much of a "
               "later period's citation traffic goes to instruments that did "
               "not yet exist, which is the part of temporal staleness the "
               "registry can support.",
        "limit": "instrument level only. Article-version history is not held.",
    }


def publication_profile():
    """Before any doctrinal outcome, does the PUBLISHED SET itself move?

    AI can change what gets published, how fast, and which cases are selected,
    without changing a line of reasoning. Those shifts would show up in every
    doctrinal series as if they were doctrine. So they are measured first and
    reported first.

    One thing that cannot be measured: the decision-to-publication lag. The
    corpus carries a decision date and our own retrieval timestamp, and no
    publication date at all, for either institution. That is recorded as
    NOT_AVAILABLE rather than approximated from the retrieval date.
    """
    if not DOCKET.exists():
        return {"verdict": "NO_DOCKET_LAYER"}
    with gzip.open(DATES, "rt", encoding="utf-8") as fh:
        dates = {k: tuple(v) for k, v in json.load(fh)["dates"].items()}
    per = defaultdict(list)
    with gzip.open(DOCKET, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r:
                continue
            d = dates.get(r["j"])
            if not d:
                continue
            q = (d[0], (d[1] - 1) // 3 + 1)
            if q in PKEY:
                per[q].append(r)
    FAM = ("feesClaim", "damagesClaim", "expert", "arbitrationPlea",
           "proofDispute", "settlement", "default")
    rows = []
    for p_ in P:
        rs = per.get(p_, [])
        if len(rs) < 100:
            continue
        n = len(rs)
        lens = sorted(r["reasonChars"] for r in rs)
        rows.append({
            "period": LBL[PKEY[p_]], "judgments": n,
            "medianReasonChars": lens[n // 2],
            "shareWithReasons": round(
                sum(1 for r in rs if r["reasonChars"] > 0) / n, 4),
            "shareAppeal": round(sum(1 for r in rs if r.get("appeal")) / n, 4),
            **{f"share_{k}": round(sum(1 for r in rs if r.get(k)) / n, 4)
               for k in FAM},
        })
    if len(rows) < 4:
        return {"verdict": "INSUFFICIENT_TEMPORAL_DEPTH"}

    def swing(key):
        vals = [r[key] for r in rows]
        return {"min": min(vals), "max": max(vals),
                "first": vals[0], "last": vals[-1],
                "maxQuarterOnQuarterChange": round(
                    max(abs(b - a) for a, b in zip(vals, vals[1:])), 4)}
    return {
        "periods": len(rows), "byPeriod": rows,
        "compositionSwings": {k: swing(k) for k in
                              ["medianReasonChars", "shareWithReasons",
                               "shareAppeal"] + [f"share_{k}" for k in FAM]},
        "decisionToPublicationLag": {
            "verdict": "NOT_AVAILABLE",
            "why": "the corpus carries a decision date and our own retrieval "
                   "timestamp. No publication date is held for any judgment, "
                   "so the lag cannot be computed and is not approximated.",
        },
        "warning": "a shift in any of these near a deployment date is a "
                   "publication-regime confound and must be reported BEFORE "
                   "any doctrinal outcome, not alongside it.",
    }


def main():
    rows, dates, excluded = load()
    S = build(rows)
    comp = []
    for src in (COMPANIONS, BACKFILL):
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

    counts = {LBL[i]: len(S[p]["judgments"]) for i, p in enumerate(P)}
    res = {
        "periods": LBL, "judgmentsWithAuthorityByPeriod": counts,
        "mentionsUsed": len(rows),
        "excludedOutsideWindow": dict(sorted(excluded.items())),
        "compositionWarning":
            "quarterly judgment counts range from "
            f"{min(counts.values())} to {max(counts.values())}, a factor of "
            f"{max(counts.values()) / max(1, min(counts.values())):.1f}. "
            "Every target below is a RATE, a SHARE or a RANK for that reason; "
            "no count is forecast, and a shift in what the publisher releases "
            "would still move a rate.",
    }

    # ---- scalar targets
    def ser(f):
        return [f(S[p]) if S[p]["judgments"] else None for p in P]

    named = ser(lambda s: (sum(s["courtRule"][r] for r in NAMED_FIQH) /
                           (sum(s["courtRule"][r] for r in NAMED_FIQH)
                            + s["courtRule"]["fiqh.unattributed"])
                           if sum(s["courtRule"][r] for r in NAMED_FIQH)
                           + s["courtRule"]["fiqh.unattributed"] else None))
    nonstat = ser(lambda s: (sum(s["courtType"][t] for t in NONSTATUTE) /
                             sum(s["courtType"].values())
                             if sum(s["courtType"].values()) else None))
    overlap = ser(lambda s: jaccard(top(s["courtStat"], 20),
                                    top(s["partyStat"], 20))
                  if sum(s["partyStat"].values()) >= 50 else None)
    hhi_art = ser(lambda s: (sum((v / sum(s["courtStat"].values())) ** 2
                                 for v in s["courtStat"].values())
                             if sum(s["courtStat"].values()) >= 200 else None))
    inst_top = ser(lambda s: share(s["courtInst"], "commercial_courts_law")
                   if sum(s["courtInst"].values()) >= 200 else None)
    ctl = ser(lambda s: (sum(v for (i, _a), v in s["courtStat"].items()
                             if i == "civil_transactions_law")
                         / sum(s["courtStat"].values())
                         if sum(s["courtStat"].values()) >= 200 else None))
    # Evidence Law named fiqh needs the identity layer, which starts at 1444
    evq = defaultdict(Counter)
    for r in comp:
        if r["voice"] == "court" and r["instW"] == "evidence_law" \
                and r["type"] == "fiqh_source":
            evq[r["p"]]["named" if r["rule"] in ("fiqh.jurist", "fiqh.book")
                        else "generic"] += 1
    evfiqh = [(evq[p]["named"] / sum(evq[p].values())
               if sum(evq[p].values()) >= 40 else None) for p in P]
    res["scalarTargets"] = {
        "civilTransactionsLawShareOfCourtCitations": scalar_backtest(
            ctl, "civilTransactionsLawShareOfCourtCitations"),
        "evidenceLawNamedFiqhShare": scalar_backtest(
            evfiqh, "evidenceLawNamedFiqhShare"),
        "namedFiqhShareOfFiqh": scalar_backtest(named, "namedFiqhShareOfFiqh"),
        "nonStatutoryShareOfCourtMentions": scalar_backtest(
            nonstat, "nonStatutoryShareOfCourtMentions"),
        "courtPartyTop20Jaccard": scalar_backtest(
            overlap, "courtPartyTop20Jaccard"),
        "courtArticleHHI": scalar_backtest(hhi_art, "courtArticleHHI"),
        "commercialCourtsLawShareOfInstruments": scalar_backtest(
            inst_top, "commercialCourtsLawShareOfInstruments"),
    }
    res["articleVisibility"] = article_backtest(S, 50)
    res["articleVisibilityTop10"] = article_backtest(S, 10)
    res["newEntrants"] = entrant_backtest(S, 50)
    res["leadLag"] = leadlag(S)
    res["retrievalDecay"] = decay(S, comp)
    res["companionPersistence"] = companion_backtest(comp, 3)
    res["newCodeUptake"] = uptake(S)
    res["publicationProfile"] = publication_profile()
    res["speakerAwareRetrieval"] = speaker_aware(S)
    res["temporalMisalignment"] = misalignment(S, comp)
    res["instrumentTemporalValidity"] = instrument_validity(S, dates)
    res["companionBackfill"] = {
        "what": "FORECAST_CALIBRATION_BACKFILL",
        "purpose": "fold count for companion persistence backtesting only. "
                   "No historical claim is made across it and DOCTRINE.md "
                   "still reads 1444-1446 alone.",
        "backfillRows": sum(1 for r in comp if r["y"] < 1444),
        "mainRows": sum(1 for r in comp if r["y"] >= 1444),
    }

    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"{len(rows):,} mentions over {len(P)} quarters "
          f"({LBL[0]}..{LBL[-1]})")
    for k, v in res["scalarTargets"].items():
        print(f"  {k:42s} {v.get('verdict')} "
              f"(folds {v.get('folds')}, best baseline {v.get('bestBaseline')})")
    print(f"  top-50 Jaccard, persistence "
          f"{res['articleVisibility'].get('meanTopKJaccard_prevPeriod')}")
    print(f"  lead-lag: {res['leadLag'].get('verdict')}")
    for c, v in res["companionPersistence"].items():
        print(f"  companions {c:44s} {v.get('verdict')} "
              f"(mean top-3 Jaccard {v.get('meanTopKJaccard')})")
    print(f"-> {OUT.name}")


if __name__ == "__main__":
    main()
