#!/usr/bin/env python3
"""What is visible in Saudi law-in-action NOW, and what is moving.

The repository's mission changes here. Reconstructing the past stops being the
object; it becomes baseline, calibration and negative control. The question is
what the corpus shows at its current endpoint, what is rising into that
endpoint, and what has been committed to before the answer arrives.

ONE THING HAS TO BE SAID BEFORE ANY NUMBER. "Now" here means the latest MATURE
quarter of the published record, which is 1446Q1. The tabular Gregorian
equivalent is roughly mid-2024, and the session clock reads 2026. So this is a
nowcast of an OBSERVATION SYSTEM THAT LAGS REAL TIME BY ABOUT TWO YEARS, and
every "current" statement below is current-as-published, not current-as-decided.
That lag is the single largest limitation on the whole programme and it is
stated first rather than last.

    python3 nowcast.py
"""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diffusion as D                      # noqa: E402
import foresight as F                      # noqa: E402
import formula_analysis as FA              # noqa: E402
import hijri as H                          # noqa: E402

OUT = HERE / "nowcast_results.json"
ASSET = HERE / "current_state.json"
J = lambda n: json.loads((HERE / n).read_text(encoding="utf-8"))
P, LBL, PKEY = F.P, F.LBL, F.PKEY

TOPN = 25
RISE_MIN = 5        # a movement rule needs a floor, or noise is "momentum"


def windows(scorable):
    """CURRENT_MATURE_PERIOD, CURRENT_12_MONTHS, CURRENT_24_MONTHS."""
    sq = [l for l in LBL if l in scorable]
    cur = sq[-1]
    y, q = int(cur[:4]), int(cur[-1])
    jd = H.h2jd(y, (q - 1) * 3 + 1, 1)
    return {
        "CURRENT_MATURE_PERIOD": [cur],
        "CURRENT_12_MONTHS": sq[-4:],
        "CURRENT_24_MONTHS": sq[-8:],
        "PRIOR_12_MONTHS": sq[-8:-4],
        "scorableQuarters": sq,
        "collectionEdge": LBL[-1],
        "collectionEdgeNote": f"{LBL[-1]} exists in the corpus but is not "
                              "mature and is excluded from every current-state "
                              "figure.",
        "currentPeriodGregorianApprox": H.fmt_g(jd),
        "observationLag": "the latest mature quarter is "
                          f"{cur}, approximately {H.fmt_g(jd)}. Every "
                          "statement here is CURRENT-AS-PUBLISHED, not "
                          "current-as-decided, and the gap between the two is "
                          "not measurable because no publication date exists "
                          "per judgment.",
    }


def _agg(S, qs, key):
    c = Counter()
    for l in qs:
        c.update(S[P[PKEY[(int(l[:4]), int(l[-1]))]]][key])
    return c


def current_state(S, rows, crows, frows, w, scorable):
    """PART 1. The reproducible current-state asset."""
    cur, y12, y24 = (w["CURRENT_MATURE_PERIOD"], w["CURRENT_12_MONTHS"],
                     w["CURRENT_24_MONTHS"])
    out = {}
    for name, qs in (("CURRENT_MATURE_PERIOD", cur), ("CURRENT_12_MONTHS", y12),
                     ("CURRENT_24_MONTHS", y24)):
        cs = _agg(S, qs, "courtStat")
        ps = _agg(S, qs, "partyStat")
        ci = _agg(S, qs, "courtInst")
        n = sum(cs.values())
        ranked = sorted(cs.values(), reverse=True)
        idx = {PKEY[(int(l[:4]), int(l[-1]))] for l in qs}
        # ecology over judgments in the window
        byj = defaultdict(list)
        for r in rows:
            if PKEY[r["p"]] in idx:
                byj[r["j"]].append(r)
        hyb = nf = ns = docs = 0
        for j, ms in byj.items():
            court = [m for m in ms if m["role"] == F.COURT]
            if not court:
                continue
            docs += 1
            nsm = [m for m in court if m["t"] in F.NONSTATUTE]
            ns += len(nsm)
            if nsm:
                hyb += 1
            if any(m["r"] in F.NAMED_FIQH for m in nsm):
                nf += 1
        src = Counter(r["cid"] for r in crows
                      if r["i"] in idx and r["voice"] == "court")
        # TRACEABILITY, defined on the layer that can carry it. The mention
        # layer's `res` field resolves STATUTE citations only, so a share of
        # non-statutory mentions computed from it is identically zero. The
        # companion layer canonicalises each non-statutory authority, so the
        # measure is the share of court non-statutory mentions whose identity
        # is a NAMED jurist, book, maxim text or hadith collection rather than
        # a generic class or an unresolved raw string.
        named = sum(v for k, v in src.items()
                    if k.startswith(("J.", "B.", "M.", "H.")))
        trace = round(named / sum(src.values()), 4) if src else None
        stot = sum(src.values())
        fsel = [r for r in frows if r["i"] in idx]
        circ = FA.circulating(frows, "tmpl")
        out[name] = {
            "quarters": qs,
            "judgmentsWithCourtAuthority": docs,
            "courtStatutoryCitations": n,
            "partyStatutoryCitations": sum(ps.values()),
            "mostVisibleInstruments": [
                {"instrument": k, "courtCitations": v,
                 "share": round(v / sum(ci.values()), 4)}
                for k, v in sorted(ci.items(),
                                   key=lambda kv: (-kv[1], kv[0]))[:12]],
            "mostVisibleArticles": [
                {"instrument": k[0], "article": k[1], "courtCitations": v,
                 "share": round(v / n, 4)}
                for k, v in sorted(cs.items(),
                                   key=lambda kv: (-kv[1], str(kv[0])))[:TOPN]],
            "operationalCore": {
                "top50Share": round(sum(ranked[:50]) / n, 4) if n else None,
                "top100Share": round(sum(ranked[:100]) / n, 4) if n else None,
                "articleHHI": round(sum((v / n) ** 2 for v in cs.values()), 6)
                              if n else None,
                "distinctArticlesCited": len(cs)},
            "courtVersusBar": {
                "top50Overlap": round(F.jaccard(F.top(cs, 50),
                                                F.top(ps, 50)) or 0.0, 4),
                "partyToCourtCitationRatio": round(
                    sum(ps.values()) / n, 4) if n else None},
            "hybridReasoning": {
                "hybridRate": round(hyb / docs, 4) if docs else None,
                "namedFiqhRate": round(nf / docs, 4) if docs else None,
                "nonStatutoryMentionsPerJudgment": round(ns / docs, 4)
                                                   if docs else None},
            "traceability": trace,
            "traceabilityDefinition": "share of court non-statutory mentions "
                                      "whose canonical identity is a named "
                                      "jurist, book, maxim text or hadith "
                                      "collection. Generic classes and "
                                      "unresolved raw strings are not "
                                      "traceable.",
            "traceableMentions": named,
            "doctrinalCompanions": [
                {"source": k, "courtMentions": v,
                 "share": round(v / stot, 4)}
                for k, v in sorted(src.items(),
                                   key=lambda kv: (-kv[1], kv[0]))[:12]],
            "sourceConcentration": {
                "distinctSources": len(src),
                "sourceHHI": round(sum((v / stot) ** 2 for v in src.values()), 6)
                             if stot else None},
            "formulaLayer": {
                "mentions": len(fsel),
                "inACirculatingFormula": sum(1 for r in fsel
                                             if r["tmpl"] in circ),
                "circulatingShare": round(
                    sum(1 for r in fsel if r["tmpl"] in circ) / len(fsel), 4)
                    if fsel else None,
                "distinctFormulas": len({r["tmpl"] for r in fsel})},
        }
    return out


# ------------------------------------------------------------- PARTS 11-14
def momentum(cur_c, prior_c, label, min_now=RISE_MIN, top=TOPN):
    """RISING / STABLE / FALLING / NEWLY_VISIBLE on two adjacent windows.

    A transparent rule, stated once and applied to articles, instruments,
    doctrinal sources and formula classes alike: compare the object's share of
    its own universe in the current window against the preceding one, require
    a floor of observations in the current window so that noise cannot be
    momentum, and call a move only past a stated relative threshold.
    """
    n_now, n_before = sum(cur_c.values()), sum(prior_c.values())
    rows = []
    for k in set(cur_c) | set(prior_c):
        a, b = cur_c.get(k, 0), prior_c.get(k, 0)
        sa = a / n_now if n_now else 0.0
        sb = b / n_before if n_before else 0.0
        if a < min_now and b < min_now:
            continue
        if b == 0:
            cls = "NEWLY_VISIBLE" if a >= min_now else "STABLE"
        elif a == 0:
            cls = "FALLING"
        else:
            rel = (sa - sb) / sb if sb else 0.0
            cls = ("RISING" if rel >= 0.25 else
                   "FALLING" if rel <= -0.25 else "STABLE")
        rows.append({"key": k if isinstance(k, str) else list(k),
                     "now": a, "before": b,
                     "shareNow": round(sa, 5), "shareBefore": round(sb, 5),
                     "relativeChange": round((sa - sb) / sb, 4) if sb else None,
                     "class": cls})
    rows.sort(key=lambda r: (-(r["relativeChange"] if r["relativeChange"]
                               is not None else 9e9), -r["now"], str(r["key"])))
    return {
        "unit": label,
        "rule": f"share of the object's own universe in the current window "
                f"against the preceding one; at least {min_now} observations "
                f"in one of the two windows; RISING at +25 per cent relative, "
                f"FALLING at -25 per cent, NEWLY_VISIBLE when absent before.",
        "counts": dict(sorted(Counter(r["class"] for r in rows).items())),
        "rising": [r for r in rows if r["class"] == "RISING"][:top],
        "newlyVisible": [r for r in rows if r["class"] == "NEWLY_VISIBLE"][:top],
        "falling": [r for r in rows if r["class"] == "FALLING"][-top:],
        "tracked": len(rows),
    }


def momentum_all(S, rows, crows, frows, fclass, w):
    """PARTS 11, 12, 13, 14 on one shared rule."""
    now, before = w["CURRENT_12_MONTHS"], w["PRIOR_12_MONTHS"]
    i_now = {PKEY[(int(l[:4]), int(l[-1]))] for l in now}
    i_bef = {PKEY[(int(l[:4]), int(l[-1]))] for l in before}
    art = momentum(_agg(S, now, "courtStat"), _agg(S, before, "courtStat"),
                   "court-cited (instrument, article)")
    code = momentum(_agg(S, now, "courtInst"), _agg(S, before, "courtInst"),
                    "instrument, court voice")
    party = momentum(_agg(S, now, "partyStat"), _agg(S, before, "partyStat"),
                     "party-cited (instrument, article)")
    src_n = Counter(r["cid"] for r in crows
                    if r["i"] in i_now and r["voice"] == "court")
    src_b = Counter(r["cid"] for r in crows
                    if r["i"] in i_bef and r["voice"] == "court")
    doc = momentum(src_n, src_b, "canonical non-statutory identity, court voice")
    fn = Counter(fclass.get(r["tmpl"], "NOT_CIRCULATING") for r in frows
                 if r["i"] in i_now)
    fb = Counter(fclass.get(r["tmpl"], "NOT_CIRCULATING") for r in frows
                 if r["i"] in i_bef)
    form = momentum(fn, fb, "authority-adjacent formula class", min_now=20)
    fnv = Counter(f"{r['voice']}" for r in frows if r["i"] in i_now)
    fbv = Counter(f"{r['voice']}" for r in frows if r["i"] in i_bef)
    voice = momentum(fnv, fbv, "formula mentions by voice", min_now=20)
    return {
        "windows": {"now": now, "before": before},
        "part11_articleMomentum": art,
        "part11b_partyArticleMomentum": party,
        "part12_codeMomentum": code,
        "part13_doctrinalMomentum": doc,
        "part14_formulaClassMomentum": form,
        "part14b_formulaVoiceMomentum": voice,
        "notAForecast": "momentum is a description of two adjacent windows. "
                        "It is not an extrapolation and nothing here says a "
                        "rising object keeps rising.",
    }


# --------------------------------------------------------------- PART 19
def article_readiness(S, rows, crows, frows, w, art_mom):
    """PART 19. The current empirical state of each operationally important
    article, so a future change is detectable immediately. No score."""
    now = w["CURRENT_12_MONTHS"]
    i_now = {PKEY[(int(l[:4]), int(l[-1]))] for l in now}
    cs, ps = _agg(S, now, "courtStat"), _agg(S, now, "partyStat")
    n = sum(cs.values())
    top = [k for k, _ in sorted(cs.items(),
                                key=lambda kv: (-kv[1], str(kv[0])))[:30]]
    mom = {tuple(r["key"]) if isinstance(r["key"], list) else r["key"]:
           r["class"] for r in
           art_mom["rising"] + art_mom["newlyVisible"] + art_mom["falling"]}
    comp = defaultdict(Counter)
    for r in crows:
        if r["i"] in i_now and r["voice"] == "court" and r["instW"] and r["artW"]:
            comp[(r["instW"], r["artW"])][r["cid"]] += 1
    out = []
    for k in top:
        c = comp.get(k, Counter())
        out.append({
            "instrument": k[0], "article": k[1],
            "courtCitations": cs[k], "partyCitations": ps.get(k, 0),
            "courtShareOfAllCourtCitations": round(cs[k] / n, 5),
            "speakerSplit": round(ps.get(k, 0) / cs[k], 4) if cs[k] else None,
            "companionSet": [s for s, _ in sorted(
                c.items(), key=lambda kv: (-kv[1], kv[0]))[:5]],
            "companionMentions": sum(c.values()),
            "namedCompanionShare": round(
                sum(v for cid, v in c.items()
                    if cid.startswith(("J.", "B.", "M.", "H."))) / sum(c.values()),
                4) if c else None,
            "momentum": mom.get(k, "STABLE"),
            "aiIssueRelevance": None,
        })
    return {
        "articlesCovered": len(out),
        "window": now,
        "noScore": "each article carries its current state, not a rating. The "
                   "point is that a future change is detectable against a "
                   "recorded present, not that articles can be ranked.",
        "aiIssueRelevanceNote": "left null here and filled only from the AI "
                                "anchor map, so that no article is labelled "
                                "AI-relevant by this file's own guesswork.",
        "articles": out,
    }


# --------------------------------------------------------------- PART 15
def forecasts(S, w, scorable):
    """PART 15. Issue only what earns skill on rolling origins.

    Two targets that matter to anyone maintaining a legal system: which
    articles enter the top-50, and whether the current top-50 holds. Both are
    backtested against the baseline that has beaten everything else in this
    repository -- persistence -- and abstention is a permitted answer.
    """
    sq = [l for l in LBL if l in scorable]
    idx = [PKEY[(int(l[:4]), int(l[-1]))] for l in sq]
    folds_hold, folds_entry = [], []
    for a in range(4, len(idx) - 1):
        cur = Counter()
        for i in idx[:a + 1]:
            cur.update(S[P[i]]["courtStat"])
        nxt = S[P[idx[a + 1]]]["courtStat"]
        if sum(nxt.values()) < 200:
            continue
        t_now, t_next = set(F.top(cur, 50)), set(F.top(nxt, 50))
        folds_hold.append(len(t_now & t_next) / 50)
        # entrants: articles outside the cumulative top-50 that enter it
        cand = [k for k, v in cur.items() if k not in t_now and v >= 3]
        if cand:
            got = [k for k in cand if k in t_next]
            ranked = sorted(cand, key=lambda k: (-cur[k], str(k)))[:20]
            folds_entry.append({
                "period": LBL[idx[a + 1]],
                "baseRate": len(got) / len(cand),
                "precisionTop20": sum(1 for k in ranked if k in t_next) / 20,
            })
    hold = round(sum(folds_hold) / len(folds_hold), 4) if folds_hold else None
    base = (round(sum(f["baseRate"] for f in folds_entry) / len(folds_entry), 4)
            if folds_entry else None)
    prec = (round(sum(f["precisionTop20"] for f in folds_entry)
                  / len(folds_entry), 4) if folds_entry else None)
    lift = round(prec / base, 4) if (prec and base) else None
    cur = Counter()
    for l in sq:
        cur.update(S[P[PKEY[(int(l[:4]), int(l[-1]))]]]["courtStat"])
    t_now = set(F.top(cur, 50))
    cand = sorted([k for k, v in cur.items() if k not in t_now and v >= 3],
                  key=lambda k: (-cur[k], str(k)))[:20]
    return {
        "issuedAt": sq[-1],
        "SIX_MONTH": {
            "target": "share of the current top-50 court articles still in "
                      "the top-50 two mature quarters later",
            "backtest": {"folds": len(folds_hold), "meanHoldRate": hold},
            "forecast": hold,
            "scoringRule": "compare the realised hold rate at the second "
                           "mature quarter after 1446Q1 against this value; "
                           "the forecast is wrong if it misses by more than "
                           "0.10.",
            "status": "ISSUED" if folds_hold else "ABSTAIN",
            "regimeAssumption": "no material detected regime break before "
                                "target maturity, per REGIME_DETECTOR_ERA_1",
        },
        "TWELVE_MONTH": {
            "target": "which articles outside the current top-50 enter it",
            "backtest": {"folds": len(folds_entry), "baseRate": base,
                         "precisionOfATop20List": prec, "lift": lift},
            "rankedList": [{"instrument": k[0], "article": k[1],
                            "cumulativeCourtCitations": cur[k]} for k in cand],
            "probabilities": "NONE. RANK_ONLY, as the forecasting programme "
                             "already established: fold-to-fold precision "
                             "varies too widely for a calibrated number.",
            "status": ("ISSUED_AS_RANKED_LIST" if lift and lift > 1.2
                       else "ABSTAIN"),
            "regimeAssumption": "no material detected regime break before "
                                "target maturity",
        },
        "TWENTY_FOUR_MONTH": {
            "status": "ABSTAIN",
            "why": "the corpus holds ten mature quarters. A 24-month horizon "
                   "is eight of them, so a backtest would have at most two "
                   "non-overlapping folds. Temporal depth does not justify "
                   "the horizon and no forecast is issued at it.",
        },
        "baseline": "persistence. Nothing in this repository has beaten it and "
                    "nothing here claims to.",
    }


# --------------------------------------------------------------- PART 18
def retrieval_architectures(S, crows, w, scorable):
    """PART 18. Which retrieval components survive law changing?

    Evaluated as pseudo-future: build each architecture on everything up to a
    fold, score it on the NEXT mature quarter's court citations, and report
    coverage. The question is not which is best today but which decays least.
    """
    sq = [l for l in LBL if l in scorable]
    idx = [PKEY[(int(l[:4]), int(l[-1]))] for l in sq]
    comp = defaultdict(set)
    for r in crows:
        if r["voice"] == "court" and r["instW"]:
            comp[r["instW"]].add(r["cid"])
    archs = {}
    for name in ("STATUTE_ONLY", "STATUTE_PLUS_CURRENT_ARTICLE_ECOLOGY",
                 "STATUTE_PLUS_DOCTRINAL_COMPANIONS", "SPEAKER_AWARE_HYBRID",
                 "TIME_AWARE_RECENT_WINDOW"):
        cov, decay = [], []
        for a in range(4, len(idx) - 1):
            hist = idx[:a + 1]
            cum, party = Counter(), Counter()
            for i in hist:
                cum.update(S[P[i]]["courtStat"])
                party.update(S[P[i]]["partyStat"])
            recent = Counter()
            for i in hist[-4:]:
                recent.update(S[P[i]]["courtStat"])
            if name == "STATUTE_ONLY":
                index = set(F.top(cum, 200))
            elif name == "STATUTE_PLUS_CURRENT_ARTICLE_ECOLOGY":
                index = set(F.top(cum, 200)) | {k for k in cum if cum[k] >= 5}
            elif name == "STATUTE_PLUS_DOCTRINAL_COMPANIONS":
                index = set(F.top(cum, 200)) | {
                    k for k in cum if k[0] in comp and cum[k] >= 3}
            elif name == "SPEAKER_AWARE_HYBRID":
                index = set(F.top(cum, 200)) | set(F.top(party, 50))
            else:
                index = set(F.top(recent, 200))
            nxt = S[P[idx[a + 1]]]["courtStat"]
            tot = sum(nxt.values())
            if tot < 200:
                continue
            hit = sum(v for k, v in nxt.items() if k in index)
            cov.append(hit / tot)
            if len(cov) > 1:
                decay.append(cov[-1] - cov[0])
        if cov:
            archs[name] = {
                "folds": len(cov),
                "meanCitationCoverage": round(sum(cov) / len(cov), 4),
                "firstFold": round(cov[0], 4), "lastFold": round(cov[-1], 4),
                "coverageDrift": round(cov[-1] - cov[0], 4),
                "indexSizeProxy": "not comparable across architectures; "
                                  "coverage is reported without a size "
                                  "penalty and must be read with that in mind",
            }
    best = min(archs, key=lambda k: (abs(archs[k]["coverageDrift"]), k)) \
        if archs else None
    return {
        "design": "pseudo-future. Each architecture is built on history up to "
                  "a fold and scored on the next mature quarter's court "
                  "citations. Historical folds are calibration only.",
        "architectures": archs,
        "leastDrift": best,
        "reading": "coverage alone favours whichever index is largest, so the "
                   "column that matters is DRIFT: how much coverage an "
                   "architecture loses as the law moves under it. A "
                   "time-aware index that keeps coverage while staying small "
                   "is the one that protects against future staleness.",
        "notAProductRecommendation": True,
    }


def main():
    hz = J("horizon_results.json")
    scorable = set(hz["phase3_maturityRule"]["scorable"])
    rows, _d, _x = F.load()
    S = F.build(rows)
    crows = D.load_rows()
    frows, _s = FA.load()
    fa = J("formula_analysis_results.json")
    tax, merged = FA.taxonomy(frows)
    fclass, _fr = FA.formula_classes(frows, merged)

    w = windows(scorable)
    cs = current_state(S, rows, crows, frows, w, scorable)
    mom = momentum_all(S, rows, crows, frows, fclass, w)
    ready = article_readiness(S, rows, crows, frows, w,
                             mom["part11_articleMomentum"])
    fc = forecasts(S, w, scorable)
    arch = retrieval_architectures(S, crows, w, scorable)

    res = {
        "what": "SAUDI LEGAL NOWCAST. What is visible in the published record "
                "at its current endpoint, and what is moving into it.",
        "missionChange": {
            "from": "reconstructing the past",
            "to": "current state, current pressure, and expectations frozen "
                  "before the answer arrives",
            "historyIsNow": ["BASELINE", "CALIBRATION", "NEGATIVE_CONTROL"],
            "retrospectiveWorkStopped": [
                "no reconstruction of historical publication dates",
                "no further historical commencement dates",
                "no further historical regime breaks",
                "no expansion of 1442 or 1443 analysis",
                "no attempt to explain every past quarter"],
            "preserved": "every frozen era, forecast, signature and registry "
                         "stands untouched and is now read as baseline.",
        },
        "part1_windows": w,
        "part1_currentState": cs,
        "part11_14_momentum": mom,
        "part19_articleReadiness": ready,
        "part15_forecasts": fc,
        "part18_retrievalArchitectures": arch,
        "standingLimitations": [
            "THE OBSERVATION LAG. The latest mature quarter is "
            f"{w['CURRENT_MATURE_PERIOD'][0]}, roughly "
            f"{w['currentPeriodGregorianApprox']}, while the session clock "
            "reads 2026. Every current-state figure is current-as-published, "
            "not current-as-decided.",
            "PUBLICATION TIMING REMAINS UNRESOLVED and is now a permanent "
            "standing limitation rather than a research programme: no "
            "publication date exists per judgment, so decision-to-publication "
            "lag cannot be separated from legal change. Recorded and moved "
            "past.",
            "momentum compares two adjacent four-quarter windows and is a "
            "description, not an extrapolation.",
            "the corpus is published Ministry of Justice commercial "
            "adjudication. Absence here is absence from that record, never "
            "absence from Saudi law.",
        ],
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    ASSET.write_text(json.dumps({
        "what": "CURRENT STATE ASSET. A reproducible snapshot of Saudi "
                "law-in-action as published, at the latest mature quarter.",
        "generatedFrom": "nowcast.py",
        "windows": w,
        "currentState": cs,
        "articleReadiness": ready,
        "disclosure": "current-as-published, not current-as-decided. Absence "
                      "from this corpus is absence from published Ministry of "
                      "Justice commercial adjudication, never absence from "
                      "Saudi law.",
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    c = cs["CURRENT_12_MONTHS"]
    print(f"current mature period {w['CURRENT_MATURE_PERIOD'][0]} "
          f"(~{w['currentPeriodGregorianApprox']})")
    print(f"  12m: {c['judgmentsWithCourtAuthority']} judgments, "
          f"{c['courtStatutoryCitations']} court citations, "
          f"hybrid {c['hybridReasoning']['hybridRate']}, "
          f"traceability {c['traceability']}")
    print(f"  momentum: articles {mom['part11_articleMomentum']['counts']}")
    print(f"  codes {mom['part12_codeMomentum']['counts']}")
    print(f"  doctrine {mom['part13_doctrinalMomentum']['counts']}")
    print(f"  6m {fc['SIX_MONTH']['status']} hold={fc['SIX_MONTH']['forecast']}"
          f"; 12m {fc['TWELVE_MONTH']['status']} "
          f"lift={fc['TWELVE_MONTH']['backtest']['lift']}")
    print(f"  retrieval least drift: {arch['leastDrift']}")
    print(f"-> {OUT.name}, {ASSET.name}")


if __name__ == "__main__":
    main()
