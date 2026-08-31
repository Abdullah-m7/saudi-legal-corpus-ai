#!/usr/bin/env python3
"""Who makes a legal authority visible first, and what happens to it after?

The statutory half of this question is answered and frozen: party-side use of
statutory provisions does not generally lead their later appearance in court
reasoning, and provisions first seen in the court's voice persist better than
provisions first seen in the bar's. That result is about ARTICLES. It says
nothing about doctrine, and doctrine is where a research tool -- human or
machine -- would plausibly change what gets found.

So: jurists, books, maxims, scripture, settled judicial practice. For each,
when it is first observed, in whose voice, beside which code, and what becomes
of it.

WHAT "FIRST" MEANS HERE, AND ONLY HERE. The repository cannot know when a
jurist was first cited in Saudi law. It knows five things and says them:

    FIRST_OBSERVED_IN_THIS_CORPUS
    FIRST_OBSERVED_BESIDE_CODE
    FIRST_OBSERVED_BESIDE_ARTICLE
    FIRST_OBSERVED_IN_COURT_VOICE
    FIRST_OBSERVED_IN_PARTY_VOICE

The word "discovery" is not used for any of them. Ibn Taymiyya was not
discovered in 1444Q2; he was first observed beside the implementing regulation
in this corpus in some quarter, which is a fact about a corpus.

CODE-LOCAL IS THE UNIT THAT MATTERS. With 28 canonical identities, almost
every source is globally visible in the first quarter, so the global level is
left-censored by construction. Beside a particular code it is not.

    python3 diffusion.py
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

OUT = HERE / "diffusion_results.json"
ASSET = HERE / "authority_diffusion.json"
J = lambda n: json.loads((HERE / n).read_text(encoding="utf-8"))
P, LBL, PKEY = F.P, F.LBL, F.PKEY

TYPE_OF = {"J.": "JURIST", "B.": "BOOK", "M.": "MAXIM", "H.": "HADITH_SOURCE"}
GENERIC_TYPE = {
    "GENERIC.fiqh.unattributed": "UNATTRIBUTED_FIQH",
    "GENERIC.quran.citation": "SCRIPTURE",
    "GENERIC.hadith.untraced": "SCRIPTURE",
    "GENERIC.principle.settled": "JUDICIAL_PRACTICE",
    "GENERIC.custom.trade": "CUSTOM",
    "GENERIC.maxim.named": "MAXIM_LABEL",
}


def kind(cid):
    for p, k in TYPE_OF.items():
        if cid.startswith(p):
            return k
    return GENERIC_TYPE.get(cid, "OTHER")


def load_rows():
    dates = None
    with gzip.open(HERE / "judgment_dates.json.gz", "rt", encoding="utf-8") as fh:
        dates = {k: tuple(v) for k, v in json.load(fh)["dates"].items()}
    rows = []
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
                    r["i"] = PKEY[p]
                    rows.append(r)
    return rows


# ------------------------------------------------------------ PHASES 3 & 4
def units(rows, level, scorable, boiler=None):
    """Build (identity, locus) units with their per-quarter voice presence."""
    seen = defaultdict(lambda: defaultdict(set))
    for r in rows:
        if boiler is not None and r["tmpl"] in boiler:
            continue
        if level == "GLOBAL":
            locus = "*"
        elif level == "CODE":
            locus = r["instW"]
        else:
            locus = (r["instW"], r["artW"]) if r["instW"] and r["artW"] else None
        if locus is None:
            continue
        seen[(r["cid"], locus)][r["i"]].add(r["voice"])
    out = {}
    idx_scor = {i for i, l in enumerate(LBL) if l in scorable}
    for key, per in seen.items():
        qs = sorted(per)
        first = qs[0]
        # ELIGIBILITY, fixed before any outcome is read
        checks = {
            "appearsMoreThanOnce": len(qs) > 1 or sum(
                1 for i in qs for _ in per[i]) > 1,
            "firstQuarterNotCollectionEdge": first < len(LBL) - 1,
            "firstQuarterIsMature": first in idx_scor,
            "hasFollowUp": any(i > first for i in idx_scor),
            "identityIsCanonical": not key[0].startswith("RAW."),
        }
        out[key] = {"perQuarter": {i: sorted(v) for i, v in per.items()},
                    "first": first, "checks": checks,
                    "eligible": all(checks.values())}
    return out


def typology(u):
    """COURT_FIRST / BAR_FIRST / SAME_PERIOD / COURT_ONLY / BAR_ONLY."""
    for key, d in u.items():
        fc = min((i for i, v in d["perQuarter"].items() if "court" in v),
                 default=None)
        fp = min((i for i, v in d["perQuarter"].items() if "party" in v),
                 default=None)
        d["firstCourt"], d["firstParty"] = fc, fp
        if fc is None:
            d["type"] = "BAR_ONLY"
        elif fp is None:
            d["type"] = "COURT_ONLY"
        elif fc < fp:
            d["type"] = "COURT_FIRST"
        elif fp < fc:
            d["type"] = "BAR_FIRST"
        else:
            d["type"] = "SAME_PERIOD"
    return u


# ------------------------------------------------------------------ PHASE 5
def survival(u, scorable):
    """Survival at 1, 2 and 4 quarters, with right-censoring kept apart."""
    idx = [i for i, l in enumerate(LBL) if l in scorable]
    for key, d in u.items():
        f = d["first"]
        present = {i for i, v in d["perQuarter"].items() if "court" in v}
        for h in (1, 2, 4):
            window = [i for i in idx if f < i <= f + h]
            if not window:
                d[f"survive{h}q"] = None          # right-censored
            else:
                d[f"survive{h}q"] = any(i in present for i in window)
        later = [i for i in idx if i > f]
        hits = [i for i in later if i in present]
        d["laterMatureQuarters"] = len(later)
        d["laterPresent"] = len(hits)
        d["state"] = (
            "RIGHT_CENSORED" if len(later) < 2 else
            "PERSISTENT" if len(later) and len(hits) / len(later) >= 0.5 else
            "REPEATED" if hits else "DISAPPEARED")
    return u


def by_type(u, keys=("survive1q", "survive2q", "survive4q")):
    out = {}
    for t in sorted({d["type"] for d in u.values() if d["eligible"]}):
        g = [d for d in u.values() if d["eligible"] and d["type"] == t]
        row = {"n": len(g)}
        for k in keys:
            v = [d[k] for d in g if d[k] is not None]
            row[k] = round(sum(v) / len(v), 4) if len(v) >= 5 else None
            row[k + "_n"] = len(v)
        row["persistentShare"] = round(
            sum(1 for d in g if d["state"] == "PERSISTENT") / len(g), 4) if g else None
        out[t] = row
    return out


# ------------------------------------------------------------------ PHASE 7
def matched(u):
    """Match court-first against bar-first on code, type and initial support.

    A famous source appearing court-first beside a busy code is not the
    comparison anyone wants. Matching is on the code, the source type and a
    coarse first-quarter support band; nothing is matched on any outcome.
    """
    elig = [dict(d, key=k) for k, d in u.items() if d["eligible"]]
    for d in elig:
        d["code"] = d["key"][1] if isinstance(d["key"][1], str) else d["key"][1][0]
        d["kind"] = kind(d["key"][0])
        n0 = len(d["perQuarter"].get(d["first"], []))
        d["band"] = 0 if n0 <= 1 else 1
    pool = defaultdict(list)
    for d in elig:
        if d["type"] == "COURT_FIRST":
            pool[(d["code"], d["kind"], d["band"])].append(d)
    pairs = []
    for d in elig:
        if d["type"] != "BAR_FIRST":
            continue
        ms = pool.get((d["code"], d["kind"], d["band"]), [])
        if ms:
            pairs.append((d, ms))
    out = {"barFirstEligible": sum(1 for d in elig if d["type"] == "BAR_FIRST"),
           "courtFirstEligible": sum(1 for d in elig if d["type"] == "COURT_FIRST"),
           "matchedPairs": len(pairs)}
    for h in (1, 2, 4):
        k = f"survive{h}q"
        diffs = []
        for b, ms in pairs:
            if b[k] is None:
                continue
            cs = [m[k] for m in ms if m[k] is not None]
            if not cs:
                continue
            diffs.append((1.0 if b[k] else 0.0) - sum(cs) / len(cs))
        if len(diffs) >= 5:
            mu = sum(diffs) / len(diffs)
            out[k] = {"pairs": len(diffs),
                      "meanBarFirstMinusCourtFirst": round(mu, 4),
                      "barFirstBetterPairs": sum(1 for x in diffs if x > 0),
                      "signTestShare": round(
                          sum(1 for x in diffs if x > 0) / len(diffs), 4)}
        else:
            out[k] = {"pairs": len(diffs), "verdict": "LOW_SUPPORT"}
    ok = [h for h in (1, 2, 4)
          if isinstance(out.get(f"survive{h}q"), dict)
          and out[f"survive{h}q"].get("meanBarFirstMinusCourtFirst") is not None
          and out[f"survive{h}q"]["meanBarFirstMinusCourtFirst"] > 0]
    out["verdict"] = ("BAR_FIRST_NOT_WORSE_AFTER_MATCHING" if ok
                      else "COURT_FIRST_ADVANTAGE_SURVIVES_MATCHING"
                      if out["matchedPairs"] >= 10 else
                      "COURT_FIRST_ADVANTAGE_SURVIVES_BUT_LOW_SUPPORT"
                      if out["matchedPairs"] >= 5 else "LOW_SUPPORT")
    out["supportWarning"] = ("matching on code, source type and support band "
                             "leaves very few pairs. The unmatched contrast "
                             "is large; the matched contrast rests on "
                             f"{out['matchedPairs']} pairs and is reported as "
                             "such.")
    return out


# ------------------------------------------------------------- PHASES 8-10
def crossing(u):
    """Cross-voice local adoption, measured in both directions."""
    out = {"BAR_TO_COURT": {}, "COURT_TO_BAR": {}}
    # The denominator has to include the units that NEVER crossed, or the
    # share is 1.0 by construction: BAR_FIRST already means a court
    # appearance exists. Bar-origin is BAR_FIRST plus BAR_ONLY; court-origin
    # is COURT_FIRST plus COURT_ONLY.
    bar_first = [d for d in u.values() if d["eligible"]
                 and d["type"] in ("BAR_FIRST", "BAR_ONLY")]
    court_first = [d for d in u.values() if d["eligible"]
                   and d["type"] in ("COURT_FIRST", "COURT_ONLY")]
    for name, group, other in (("BAR_TO_COURT", bar_first, "firstCourt"),
                               ("COURT_TO_BAR", court_first, "firstParty")):
        lags = [d[other] - d["first"] for d in group if d[other] is not None]
        out[name] = {
            "n": len(group),
            "crossed": len(lags),
            "crossedShare": round(len(lags) / len(group), 4) if group else None,
            "within1q": round(sum(1 for x in lags if x <= 1) / len(group), 4)
                        if group else None,
            "within2q": round(sum(1 for x in lags if x <= 2) / len(group), 4)
                        if group else None,
            "within4q": round(sum(1 for x in lags if x <= 4) / len(group), 4)
                        if group else None,
            "medianLagQuarters": (sorted(lags)[len(lags) // 2] if lags else None),
        }
    never = [d for d in u.values()
             if d["eligible"] and d["type"] in ("COURT_ONLY", "BAR_ONLY")]
    out["NEVER_CROSSED"] = {
        "n": len(never),
        "byType": dict(sorted(Counter(d["type"] for d in never).items()))}
    b, c = out["BAR_TO_COURT"]["crossedShare"], out["COURT_TO_BAR"]["crossedShare"]
    out["dominantDirection"] = (
        "INSUFFICIENT" if b is None or c is None else
        "BENCH_TO_BAR" if c - b > 0.15 else
        "BAR_TO_BENCH" if b - c > 0.15 else "BIDIRECTIONAL_OR_INDEPENDENT")
    out["note"] = ("CROSS-VOICE LOCAL ADOPTION. A source crossing from one "
                   "voice to the other beside the same code is a measurable "
                   "transition and is not evidence that either side "
                   "influenced the other.")
    return out


# --------------------------------------------------------- PHASES 11 & 12
def article_source_order(rows, S, scorable):
    """Does the article arrive before its doctrinal environment, or after?"""
    first_art = {}
    for i, p in enumerate(P):
        for (inst, a) in S[p]["courtStat"]:
            first_art.setdefault((inst, str(a)), i)
    first_src = {}
    for r in rows:
        if r["voice"] != "court" or not r["instW"] or not r["artW"]:
            continue
        k = (r["instW"], str(r["artW"]))
        first_src[k] = min(first_src.get(k, 10 ** 6), r["i"])
    idx = {i for i, l in enumerate(LBL) if l in scorable}
    rows_out, lags = [], []
    for k, fa in sorted(first_art.items(), key=lambda kv: str(kv[0])):
        fs = first_src.get(k)
        if fa >= len(LBL) - 1 or fa not in idx:
            continue
        if fs is None:
            rows_out.append({"article": f"{k[0]}:{k[1]}", "state": "NO_COMPANION"})
            continue
        st = ("ARTICLE_FIRST" if fa < fs else
              "SOURCE_FIRST" if fs < fa else "SAME_PERIOD")
        rows_out.append({"article": f"{k[0]}:{k[1]}", "state": st,
                         "articleQuarter": LBL[fa], "sourceQuarter": LBL[fs],
                         "latencyQuarters": fs - fa})
        if st == "ARTICLE_FIRST":
            lags.append(fs - fa)
    c = Counter(r["state"] for r in rows_out)
    lags.sort()
    return {
        "articlesConsidered": len(rows_out),
        "byState": dict(sorted(c.items())),
        "companionFormationLatency": {
            "n": len(lags),
            "median": lags[len(lags) // 2] if lags else None,
            "p25": lags[len(lags) // 4] if lags else None,
            "p75": lags[3 * len(lags) // 4] if lags else None,
            "distribution": dict(sorted(Counter(lags).items()))},
        "note": "the previous session called this unmeasurable for want of "
                "depth. With the 1442-1443 backfill it is measurable, thinly. "
                "NO_COMPANION is the majority state and that is the finding: "
                "most articles never acquire a locally attached non-statutory "
                "authority at all.",
    }


# -------------------------------------------------------- PHASES 13, 14, 18, 19
def milestones(rows, scorable):
    """Diffusion milestones as a set, not a ladder."""
    per = defaultdict(lambda: {"j": defaultdict(set), "art": defaultdict(set),
                               "code": defaultdict(set),
                               "city": defaultdict(set),
                               "voice": defaultdict(set)})
    for r in rows:
        d = per[r["cid"]]
        d["j"][r["i"]].add(r["j"])
        d["voice"][r["i"]].add(r["voice"])
        d["city"][r["i"]].add(r["city"])
        if r["instW"]:
            d["code"][r["i"]].add(r["instW"])
            if r["artW"]:
                d["art"][r["i"]].add((r["instW"], str(r["artW"])))
    out = []
    for cid, d in sorted(per.items()):
        qs = sorted(d["j"])
        f = qs[0]

        def reach(key, n):
            acc = set()
            for i in qs:
                acc |= d[key][i]
                if len(acc) >= n:
                    return i - f
            return None
        out.append({
            "source": cid, "kind": kind(cid), "firstQuarter": LBL[f],
            "toSecondJudgment": reach("j", 2),
            "toSecondArticle": reach("art", 2),
            "toSecondCode": reach("code", 2),
            "toThirdCode": reach("code", 3),
            "toSecondCity": reach("city", 2),
            "toBothVoices": reach("voice", 2),
            "codesEver": len({c for i in qs for c in d["code"][i]}),
            "citiesEver": len({c for i in qs for c in d["city"][i]}),
            "articlesEver": len({a for i in qs for a in d["art"][i]}),
            "judgmentsEver": len({x for i in qs for x in d["j"][i]}),
        })
    bykind = defaultdict(list)
    for r in out:
        bykind[r["kind"]].append(r)

    def med(g, k):
        v = sorted(x[k] for x in g if x[k] is not None)
        return v[len(v) // 2] if v else None
    return {
        "sources": out,
        "byKind": {k: {"n": len(g),
                       "medianToSecondCode": med(g, "toSecondCode"),
                       "medianToSecondCity": med(g, "toSecondCity"),
                       "medianToBothVoices": med(g, "toBothVoices"),
                       "meanCodesEver": round(
                           sum(x["codesEver"] for x in g) / len(g), 2),
                       "meanCitiesEver": round(
                           sum(x["citiesEver"] for x in g) / len(g), 2)}
                   for k, g in sorted(bykind.items())},
        "note": "milestones are a SET, not a ladder. A source can reach three "
                "codes without ever reaching both voices, and the states are "
                "recorded independently for that reason.",
    }


# --------------------------------------------------------------- PHASE 17
def templates(rows, scorable, min_j=10):
    """Is some of this diffusion the spread of judicial WORDING?"""
    by = defaultdict(lambda: {"j": set(), "q": set(), "city": set(),
                              "code": set(), "voice": set()})
    for r in rows:
        d = by[r["tmpl"]]
        d["j"].add(r["j"])
        d["q"].add(r["i"])
        d["city"].add(r["city"])
        d["voice"].add(r["voice"])
        if r["instW"]:
            d["code"].add(r["instW"])
    circ = {t: d for t, d in by.items() if len(d["j"]) >= min_j}
    rows_out = []
    for t, d in sorted(circ.items(), key=lambda kv: (-len(kv[1]["j"]), kv[0])):
        qs = sorted(d["q"])
        rows_out.append({
            "fingerprint": t, "judgments": len(d["j"]),
            "firstQuarter": LBL[qs[0]], "lastQuarter": LBL[qs[-1]],
            "quartersSpanned": qs[-1] - qs[0] + 1,
            "quartersPresent": len(qs),
            "cities": len(d["city"]), "codes": len(d["code"]),
            "voices": sorted(d["voice"])})
    both = [r for r in rows_out if len(r["voices"]) > 1]
    return {
        "circulatingFingerprints": len(circ),
        "minJudgments": min_j,
        "medianCities": (sorted(r["cities"] for r in rows_out)[len(rows_out) // 2]
                         if rows_out else None),
        "medianCodes": (sorted(r["codes"] for r in rows_out)[len(rows_out) // 2]
                        if rows_out else None),
        "medianQuartersPresent": (
            sorted(r["quartersPresent"] for r in rows_out)[len(rows_out) // 2]
            if rows_out else None),
        "appearInBothVoices": len(both),
        "appearInBothVoicesShare": round(len(both) / len(rows_out), 4)
                                   if rows_out else None,
        "top": rows_out[:10],
        "question": "is some authority diffusion actually the diffusion of "
                    "judicial wording? A formula present in both voices and "
                    "many cities is a circulating form of words, whatever "
                    "authority it carries.",
    }


# --------------------------------------------------------------- PHASE 20
def source_mobility(rows, scorable):
    """The doctrine analogue of article salience mobility."""
    per = defaultdict(Counter)
    for r in rows:
        if r["voice"] == "court":
            per[r["i"]][r["cid"]] += 1
    idx = [i for i, l in enumerate(LBL) if l in scorable
           and sum(per[i].values()) >= 100]
    auto, topp, mob, surv = [], [], [], []
    for a, b in zip(idx, idx[1:]):
        A, B = per[a], per[b]
        ra = {k: r for r, k in enumerate(F.top(A, 10 ** 6))}
        rb = {k: r for r, k in enumerate(F.top(B, 10 ** 6))}
        both = sorted(set(ra) & set(rb), key=str)
        if len(both) < 8:
            continue
        n = len(both)
        mu_a = sum(ra[k] for k in both) / n
        mu_b = sum(rb[k] for k in both) / n
        sa = math.sqrt(sum((ra[k] - mu_a) ** 2 for k in both))
        sb = math.sqrt(sum((rb[k] - mu_b) ** 2 for k in both))
        if sa and sb:
            auto.append(sum((ra[k] - mu_a) * (rb[k] - mu_b) for k in both)
                        / (sa * sb))
        d = max(1, n // 4)                      # quartile, the universe is small
        topp.append(len(set(F.top(A, d)) & set(F.top(B, d))) / d)
        bottom = {k for k in both if ra[k] >= n / 2}
        mob.append(len(bottom & set(F.top(B, d))) / len(bottom) if bottom else 0.0)
        new = set(B) - set(A)
        if new:
            surv.append(len(new & set(per[b])) / len(new))
    m = lambda v: round(sum(v) / len(v), 4) if v else None
    return {"steps": len(auto), "rankAutocorrelation": m(auto),
            "topQuartilePersistence": m(topp),
            "bottomHalfToTopQuartileMobility": m(mob),
            "universeSize": len({r["cid"] for r in rows}),
            "note": "the doctrinal universe has 28 identities against roughly "
                    "2,000 articles, so a decile is meaningless and a "
                    "quartile is used. The two mobility figures are NOT "
                    "directly comparable for that reason, and the comparison "
                    "below says so."}


# --------------------------------------------------------------- PHASE 25
def entrant_forecast(u, scorable):
    """Can persistence be forecast from what is visible at emergence?"""
    elig = [dict(d, key=k) for k, d in u.items() if d["eligible"]
            and d["state"] in ("PERSISTENT", "REPEATED", "DISAPPEARED")]
    if len(elig) < 20:
        return {"verdict": "LOW_SUPPORT", "n": len(elig)}
    for d in elig:
        d["persisted"] = d["state"] == "PERSISTENT"
        d["firstVoices"] = len(d["perQuarter"].get(d["first"], []))
        d["courtOrigin"] = 1 if "court" in d["perQuarter"].get(d["first"], []) else 0
        d["kind"] = kind(d["key"][0])
    base = sum(1 for d in elig if d["persisted"]) / len(elig)
    feats = ("firstVoices", "courtOrigin")
    out = {"n": len(elig), "baseRate": round(base, 4), "features": {}}
    n_true = sum(1 for d in elig if d["persisted"])
    for f in feats:
        rs = sorted(elig, key=lambda d: (-d[f], str(d["key"])))
        out["features"][f] = round(
            sum(1 for d in rs[:n_true] if d["persisted"]) / n_true, 4)
    best = max(out["features"], key=lambda f: (out["features"][f], f))
    out["bestFeature"] = best
    out["liftOverBaseRate"] = round(out["features"][best] / base, 2) if base else None
    out["verdict"] = ("SIGNAL_ABOVE_BASE_RATE"
                      if out["features"][best] > base * 1.3
                      else "NO_USABLE_SIGNAL_USE_DETECT_OR_WATCH")
    out["temporalFolds"] = ("NOT RUN: with %d eligible units across the whole "
                            "window there are not enough per-quarter cohorts "
                            "to build rolling folds. This is a single-sample "
                            "ranking check, not a backtest, and it may not "
                            "support a forecast." % len(elig))
    return out


# --------------------------------------------------------------- PHASE 24
def novelty_kind(u_code, u_global):
    """Global novelty and code-local novelty are different objects."""
    gfirst = {k[0]: d["first"] for k, d in u_global.items()}
    rows = []
    for k, d in u_code.items():
        if not d["eligible"]:
            continue
        cid, code = k
        g = gfirst.get(cid)
        rows.append({"source": cid, "code": code,
                     "codeLocalFirst": LBL[d["first"]],
                     "globalFirst": LBL[g] if g is not None else None,
                     "class": ("GLOBAL_NOVELTY" if g is not None and g == d["first"]
                               else "CODE_LOCAL_NOVELTY")})
    return {"units": len(rows),
            "byClass": dict(sorted(Counter(r["class"] for r in rows).items())),
            "why": "an AI-discovery hypothesis is about the long tail -- "
                   "sources new to the system. Code-companion formation is "
                   "about a known source arriving beside a new code. They are "
                   "different claims and are counted apart.",
            "rows": rows[:20]}


def main():
    rows = load_rows()
    hz = J("horizon_results.json")
    scorable = set(hz["phase3_maturityRule"]["scorable"])
    _r, dates, _e = F.load()
    S = F.build(_r)

    # circulating wording, for the de-boilerplated repeat
    byt = defaultdict(set)
    for r in rows:
        byt[r["tmpl"]].add(r["j"])
    boiler = {t for t, js in byt.items() if len(js) >= 10}

    u_glob = survival(typology(units(rows, "GLOBAL", scorable)), scorable)
    u_code = survival(typology(units(rows, "CODE", scorable)), scorable)
    u_art = survival(typology(units(rows, "ARTICLE", scorable)), scorable)
    u_code_db = survival(typology(units(rows, "CODE", scorable, boiler)), scorable)

    def elig_report(u, name):
        e = sum(1 for d in u.values() if d["eligible"])
        fails = Counter()
        for d in u.values():
            for k, v in d["checks"].items():
                if not v:
                    fails[k] += 1
        return {"level": name, "units": len(u), "eligible": e,
                "excluded": len(u) - e,
                "exclusionReasons": dict(sorted(fails.items()))}

    res = {
        "what": "AUTHORITY DISCOVERY AND DIFFUSION OBSERVATORY. Who makes a "
                "doctrinal authority visible first, beside which code, and "
                "what becomes of it.",
        "firstMeans": {
            "FIRST_OBSERVED_IN_THIS_CORPUS": "the earliest quarter the "
                                             "extractor saw the identity",
            "FIRST_OBSERVED_BESIDE_CODE": "the earliest quarter it was "
                                          "attached to that instrument",
            "FIRST_OBSERVED_BESIDE_ARTICLE": "the same, for an article",
            "FIRST_OBSERVED_IN_COURT_VOICE": "earliest court-voice quarter",
            "FIRST_OBSERVED_IN_PARTY_VOICE": "earliest party-voice quarter",
            "notDiscovery": "the word discovery is not used. Nothing here is "
                            "a claim about when a jurist entered Saudi law.",
        },
        "rows": len(rows),
        "eligibility": {
            "rule": ["appears more than once", "first quarter is not the "
                     "collection edge", "first quarter is mature",
                     "at least one mature follow-up quarter exists",
                     "identity is canonical, not a raw string"],
            "levels": [elig_report(u_glob, "GLOBAL"),
                       elig_report(u_code, "CODE"),
                       elig_report(u_art, "ARTICLE")]},
        "phase3_typology": {
            "GLOBAL": dict(sorted(Counter(
                d["type"] for d in u_glob.values() if d["eligible"]).items())),
            "CODE": dict(sorted(Counter(
                d["type"] for d in u_code.values() if d["eligible"]).items())),
            "ARTICLE": dict(sorted(Counter(
                d["type"] for d in u_art.values() if d["eligible"]).items()))},
        "phase5_6_survivalByFirstMover": {
            "CODE": by_type(u_code), "ARTICLE": by_type(u_art),
            "GLOBAL": by_type(u_glob)},
        "phase7_matched": matched(u_code),
        "phase16_deBoilerplated": {
            "circulatingFingerprintsRemoved": len(boiler),
            "typology": dict(sorted(Counter(
                d["type"] for d in u_code_db.values() if d["eligible"]).items())),
            "survival": by_type(u_code_db),
            "matched": matched(u_code_db)},
        "phase8_9_10_crossing": crossing(u_code),
        "phase11_12_articleSourceOrder": article_source_order(rows, S, scorable),
        "phase13_14_18_19_milestones": milestones(rows, scorable),
        "phase17_templatePropagation": templates(rows, scorable),
        "phase20_sourceMobility": source_mobility(rows, scorable),
        "phase24_noveltyKind": novelty_kind(u_code, u_glob),
        "phase25_entrantForecastability": entrant_forecast(u_code, scorable),
    }

    # ------------------------------------------------- PHASE 21 comparison
    art = hz["phase19_20_salienceBaseline"]
    doc = res["phase20_sourceMobility"]
    res["phase21_statuteVsDoctrine"] = {
        "articles": {"rankAutocorrelation": art["rankAutocorrelation"],
                     "topDecilePersistence": art["topDecilePersistence"],
                     "bottomHalfMobility": art["bottomHalfToTopDecileMobility"],
                     "universeSize": "about 2,000 cited articles"},
        "doctrinalSources": {"rankAutocorrelation": doc["rankAutocorrelation"],
                             "topQuartilePersistence": doc["topQuartilePersistence"],
                             "bottomHalfMobility": doc["bottomHalfToTopQuartileMobility"],
                             "universeSize": doc["universeSize"]},
        "comparabilityWarning": "the two universes differ by two orders of "
                                "magnitude, so persistence is measured on a "
                                "decile for articles and a quartile for "
                                "sources. The numbers are NOT directly "
                                "comparable and the direction is all that is "
                                "read from them.",
        "reading": ("doctrinal rank autocorrelation "
                    f"{doc['rankAutocorrelation']} against articles' "
                    f"{art['rankAutocorrelation']}"),
    }

    # -------------------------------------------------- PHASE 35: the asset
    ms = {r["source"]: r for r in res["phase13_14_18_19_milestones"]["sources"]}
    asset = []
    for k, d in sorted(u_code.items(), key=lambda kv: str(kv[0])):
        cid, code = k
        m = ms.get(cid, {})
        asset.append({
            "authority_id": f"{cid}@{code}",
            "authority_type": kind(cid),
            "canonical_identity": cid,
            "locus_code": code,
            "first_observed_global": m.get("firstQuarter"),
            "first_observed_beside_code": LBL[d["first"]],
            "first_court": LBL[d["firstCourt"]] if d["firstCourt"] is not None else None,
            "first_party": LBL[d["firstParty"]] if d["firstParty"] is not None else None,
            "first_mover": d["type"],
            "eligible": d["eligible"],
            "survival_1q": d["survive1q"], "survival_2q": d["survive2q"],
            "survival_4q": d["survive4q"], "state": d["state"],
            "codes_reached": m.get("codesEver"),
            "articles_reached": m.get("articlesEver"),
            "cities_reached": m.get("citiesEver"),
            "judgments": m.get("judgmentsEver"),
            "quarters_to_second_code": m.get("toSecondCode"),
            "quarters_to_second_city": m.get("toSecondCity"),
            "quarters_to_both_voices": m.get("toBothVoices"),
            "prospective_status": "BACKFILLED_OBSERVATION",
        })
    ASSET.write_text(json.dumps({
        "what": "AUTHORITY DIFFUSION ASSET: one row per (canonical identity, "
                "code) with how it entered and how far it spread. No judgment "
                "text.",
        "prospectiveStatus": "every row is a BACKFILLED_OBSERVATION. The "
                             "asset was built today over past quarters and "
                             "supports no claim of anticipation.",
        "firstMeans": res["firstMeans"],
        "rows": asset}, ensure_ascii=False, indent=1), encoding="utf-8")
    res["phase35_asset"] = {"rows": len(asset), "file": ASSET.name}

    # --------------------------------------------- PHASE 36: the flow model
    res["phase36_flowModel"] = {
        "relations": ["OBSERVED_BEFORE", "OBSERVED_AFTER", "CO_OCCURS",
                      "CROSSES_VOICE", "DIFFUSES_TO"],
        "forbidden": "CAUSES, INFLUENCES, LEADS_TO",
        "observedTransitions": {
            "ARTICLE_BEFORE_ITS_COMPANION":
                res["phase11_12_articleSourceOrder"]["byState"].get(
                    "ARTICLE_FIRST", 0),
            "COMPANION_BEFORE_ITS_ARTICLE":
                res["phase11_12_articleSourceOrder"]["byState"].get(
                    "SOURCE_FIRST", 0),
            "ARTICLE_WITH_NO_COMPANION":
                res["phase11_12_articleSourceOrder"]["byState"].get(
                    "NO_COMPANION", 0),
            "SOURCE_CROSSES_BAR_TO_COURT":
                res["phase8_9_10_crossing"]["BAR_TO_COURT"]["crossed"],
            "SOURCE_CROSSES_COURT_TO_BAR":
                res["phase8_9_10_crossing"]["COURT_TO_BAR"]["crossed"]},
        "note": "stages are stored as observed orderings between timestamped "
                "appearances. Nothing in this model is an arrow of causation.",
    }

    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"{len(rows):,} identity rows")
    for e in res["eligibility"]["levels"]:
        print(f"  {e['level']:8s} units {e['units']:5d} eligible {e['eligible']}")
    print(f"  CODE typology: {res['phase3_typology']['CODE']}")
    sv = res["phase5_6_survivalByFirstMover"]["CODE"]
    for t, v in sv.items():
        print(f"    {t:14s} n={v['n']:3d} 1q={v['survive1q']} "
              f"2q={v['survive2q']} 4q={v['survive4q']} "
              f"persistent={v['persistentShare']}")
    print(f"  matched: {res['phase7_matched']['verdict']} "
          f"(pairs {res['phase7_matched']['matchedPairs']})")
    print(f"  crossing: {res['phase8_9_10_crossing']['dominantDirection']}")
    print(f"  article/source order: {res['phase11_12_articleSourceOrder']['byState']}")
    print(f"  entrant forecastability: "
          f"{res['phase25_entrantForecastability'].get('verdict')}")
    print(f"-> {OUT.name}, {ASSET.name}")


if __name__ == "__main__":
    main()
