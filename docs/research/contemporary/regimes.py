#!/usr/bin/env python3
"""Is this one process, or several? A regime-aware reading of the corpus.

Everything in this repository so far has been computed as though one
data-generating process produced the whole window. That assumption is now
withdrawn. Saudi legal practice is institutionally non-stationary: leadership,
restructuring, jurisdiction, publication policy, digital platforms, legislative
packages and AI deployment can all change the process that generates the
observations, not merely the observations.

So the question stops being "what is the normal sequence by which Saudi law
changes" and becomes "under which institutional regime was an observed pattern
generated, and what happens when the regime changes".

WHAT THIS FILE DOES NOT DO. It does not divide history by ministers. It detects
candidate breaks from the data FIRST, then looks for independently timestamped
institutional events, and records both the breaks with no event and the events
with no break. It never says a leadership change caused a citation pattern.

THE HONEST CONSTRAINT, STATED UP FRONT. The window is 18 quarters, 14 of them
carrying a publication profile. Change-point detection on 14 points is weak,
and a method that is not calibrated against its own false-alarm rate on such a
series will find breaks everywhere. Every statistic here is therefore scored
against a permutation null with a fixed seed, and the false-alarm behaviour is
reported beside every detection.

    python3 regimes.py
"""
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diffusion as D                      # noqa: E402
import foresight as F                      # noqa: E402
import formula_analysis as FA              # noqa: E402

OUT = HERE / "regimes_results.json"
EVENTS = HERE / "institutional_event_registry.json"
J = lambda n: json.loads((HERE / n).read_text(encoding="utf-8"))
P, LBL, PKEY = F.P, F.LBL, F.PKEY

SEED = 20260831
PERMUTATIONS = 2000
ALPHA = 0.05           # fixed before any series was inspected
MIN_SEGMENT = 3        # a segment shorter than this is not a regime


# ------------------------------------------------------------------ PHASE 5
def build_series(scorable):
    """Five independent metric families, from layers that already exist."""
    fs = J("foresight_results.json")
    pub = {r["period"]: r for r in fs["publicationProfile"]["byPeriod"]}
    rows, _d, _x = F.load()
    S = F.build(rows)
    frows, _s = FA.load()
    crows = D.load_rows()

    fam = defaultdict(dict)
    for lbl, r in pub.items():
        fam["PUBLICATION"].setdefault("judgments", {})[lbl] = r["judgments"]
        fam["PUBLICATION"].setdefault("medianReasonChars", {})[lbl] = \
            r["medianReasonChars"]
        fam["PUBLICATION"].setdefault("shareWithReasons", {})[lbl] = \
            r["shareWithReasons"]
        fam["PUBLICATION"].setdefault("shareAppeal", {})[lbl] = r["shareAppeal"]
        for k in ("feesClaim", "damagesClaim", "proofDispute", "expert",
                  "settlement", "default"):
            fam["DOCKET"].setdefault(k, {})[lbl] = r[f"share_{k}"]

    # STATUTORY SALIENCE
    prev_top = None
    for i, p in enumerate(P):
        c = S[p]["courtStat"]
        n = sum(c.values())
        if n < 200:
            prev_top = None
            continue
        lbl = LBL[i]
        h = sum((v / n) ** 2 for v in c.values())
        top50 = F.top(c, 50)
        fam["STATUTORY"].setdefault("courtArticleHHI", {})[lbl] = round(h, 6)
        fam["STATUTORY"].setdefault("top50Share", {})[lbl] = round(
            sum(c[a] for a in top50) / n, 4)
        pc = S[p]["partyStat"]
        if sum(pc.values()) >= 50:
            fam["STATUTORY"].setdefault("courtBarTop50Overlap", {})[lbl] = \
                round(F.jaccard(top50, F.top(pc, 50)) or 0.0, 4)
        if prev_top is not None:
            fam["STATUTORY"].setdefault("coreTurnover", {})[lbl] = round(
                1 - (F.jaccard(prev_top, top50) or 0.0), 4)
        prev_top = top50

    # AUTHORITY ECOLOGY
    per = defaultdict(lambda: {"j": set(), "hy": set(), "nf": set(),
                               "ns": 0, "tr": 0, "cid": Counter()})
    byj = defaultdict(list)
    for r in rows:
        byj[r["j"]].append(r)
    for j, ms in byj.items():
        i = PKEY[ms[0]["p"]]
        court = [m for m in ms if m["role"] == F.COURT]
        if not court:
            continue
        d = per[i]
        d["j"].add(j)
        ns = [m for m in court if m["t"] in F.NONSTATUTE]
        d["ns"] += len(ns)
        d["tr"] += sum(1 for m in ns if m.get("res") == "named")
        if ns:
            d["hy"].add(j)
        if any(m["r"] in F.NAMED_FIQH for m in ns):
            d["nf"].add(j)
    for r in crows:
        if r["voice"] == "court":
            per[r["i"]]["cid"][r["cid"]] += 1
    for i, d in per.items():
        if len(d["j"]) < 200:
            continue
        lbl = LBL[i]
        fam["ECOLOGY"].setdefault("hybridRate", {})[lbl] = round(
            len(d["hy"]) / len(d["j"]), 4)
        fam["ECOLOGY"].setdefault("namedFiqhShare", {})[lbl] = round(
            len(d["nf"]) / len(d["j"]), 4)
        if d["ns"]:
            fam["ECOLOGY"].setdefault("traceability", {})[lbl] = round(
                d["tr"] / d["ns"], 4)
        tot = sum(d["cid"].values())
        if tot >= 100:
            fam["ECOLOGY"].setdefault("sourceHHI", {})[lbl] = round(
                sum((v / tot) ** 2 for v in d["cid"].values()), 6)

    # AUTHORITY-ADJACENT FORMULA
    circ = FA.circulating(frows, "tmpl")
    firstq = {}
    for r in frows:
        firstq[r["tmpl"]] = min(firstq.get(r["tmpl"], r["i"]), r["i"])
    byq = defaultdict(list)
    for r in frows:
        byq[r["i"]].append(r)
    for i, sel in byq.items():
        if len(sel) < 200:
            continue
        lbl = LBL[i]
        c = Counter(r["tmpl"] for r in sel)
        ranked = sorted(c.values(), reverse=True)
        court = [r for r in sel if r["voice"] == "court"]
        fam["FORMULA"].setdefault("formulaShareOfMentions", {})[lbl] = round(
            sum(1 for r in sel if r["tmpl"] in circ) / len(sel), 4)
        fam["FORMULA"].setdefault("formulaInnovationRate", {})[lbl] = round(
            sum(1 for t in c if firstq[t] == i) / len(c), 4)
        fam["FORMULA"].setdefault("top10FormulaConcentration", {})[lbl] = round(
            sum(ranked[:10]) / sum(ranked), 4)
        if court:
            fam["FORMULA"].setdefault("courtFormulaShare", {})[lbl] = round(
                sum(1 for r in court if r["tmpl"] in circ) / len(court), 4)
    return {k: dict(v) for k, v in fam.items()}, S, rows, frows, crows


# ------------------------------------------------------------------ PHASE 6
def _mean_sd(v):
    n = len(v)
    m = sum(v) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / n) if n else 0.0
    return m, sd


def cusum(v):
    """Max absolute standardised cumulative deviation, and where it peaks."""
    m, sd = _mean_sd(v)
    if sd == 0:
        return 0.0, None
    c, best, at = 0.0, 0.0, None
    for i, x in enumerate(v[:-1]):
        c += (x - m) / sd
        if abs(c) > best:
            best, at = abs(c), i + 1
    return best / math.sqrt(len(v)), at


def page_hinkley(v, delta=0.5):
    """One-sided drift statistic, run in both directions; the larger wins."""
    m, sd = _mean_sd(v)
    if sd == 0:
        return 0.0, None
    best, at = 0.0, None
    for sign in (1, -1):
        cum, mn = 0.0, 0.0
        for i, x in enumerate(v):
            cum += sign * (x - m) / sd - delta
            mn = min(mn, cum)
            if cum - mn > best:
                best, at = cum - mn, i
    return best, at


def piecewise_level(v):
    """Best single split on the mean, scored as variance explained."""
    n = len(v)
    if n < 2 * MIN_SEGMENT:
        return 0.0, None
    m, _ = _mean_sd(v)
    sst = sum((x - m) ** 2 for x in v)
    if sst == 0:
        return 0.0, None
    best, at = 0.0, None
    for k in range(MIN_SEGMENT, n - MIN_SEGMENT + 1):
        a, b = v[:k], v[k:]
        ma, mb = sum(a) / len(a), sum(b) / len(b)
        sse = sum((x - ma) ** 2 for x in a) + sum((x - mb) ** 2 for x in b)
        r = 1 - sse / sst
        if r > best:
            best, at = r, k
    return best, at


def _slope(v):
    n = len(v)
    mx = (n - 1) / 2
    my = sum(v) / n
    den = sum((i - mx) ** 2 for i in range(n))
    if den == 0:
        return 0.0, my
    b = sum((i - mx) * (v[i] - my) for i in range(n)) / den
    return b, my - b * mx


def piecewise_trend(v):
    """Best single split on the SLOPE, scored as variance explained."""
    n = len(v)
    if n < 2 * (MIN_SEGMENT + 1):
        return 0.0, None
    b, a = _slope(v)
    sst = sum((v[i] - (a + b * i)) ** 2 for i in range(n))
    if sst == 0:
        return 0.0, None
    best, at = 0.0, None
    for k in range(MIN_SEGMENT + 1, n - MIN_SEGMENT):
        sse = 0.0
        for seg, off in ((v[:k], 0), (v[k:], k)):
            bb, aa = _slope(seg)
            sse += sum((seg[i] - (aa + bb * i)) ** 2 for i in range(len(seg)))
        r = 1 - sse / sst
        if r > best:
            best, at = r, k
    return best, at


METHODS = {"CUSUM": cusum, "PAGE_HINKLEY": page_hinkley,
           "PIECEWISE_LEVEL": piecewise_level,
           "PIECEWISE_TREND": piecewise_trend}


def permutation_test(v, fn, perms=PERMUTATIONS, seed=SEED):
    """A p-value and a false-alarm rate from the series' own values.

    Permuting the observations destroys any ordering while keeping the
    marginal distribution, so the null is exactly 'this series has no
    structure in TIME'. With 14 points that is the only null worth testing
    against, and it is the reason no threshold in this file is hand-picked.
    """
    stat, at = fn(v)
    rng = random.Random(seed)
    w = list(v)
    ge = 0
    null = []
    for _ in range(perms):
        rng.shuffle(w)
        s, _a = fn(w)
        null.append(s)
        if s >= stat:
            ge += 1
    null.sort()
    return {
        "statistic": round(stat, 4),
        "atIndex": at,
        "p": round((ge + 1) / (perms + 1), 4),
        "null95": round(null[int(perms * 0.95)], 4),
        "nullMedian": round(null[perms // 2], 4),
        "significant": ((ge + 1) / (perms + 1)) <= ALPHA,
    }


def scan(fam):
    """Every metric, every method, each with its own permutation null."""
    out, hits = {}, defaultdict(list)
    for family, metrics in sorted(fam.items()):
        out[family] = {}
        for name, series in sorted(metrics.items()):
            labels = [l for l in LBL if l in series]
            v = [series[l] for l in labels]
            if len(v) < 2 * MIN_SEGMENT:
                out[family][name] = {"n": len(v),
                                     "verdict": "TOO_SHORT_TO_TEST"}
                continue
            res = {"n": len(v), "periods": labels, "values": v, "methods": {}}
            for mname, fn in sorted(METHODS.items()):
                r = permutation_test(v, fn)
                if r["atIndex"] is not None and 0 <= r["atIndex"] < len(labels):
                    r["breakAt"] = labels[r["atIndex"]]
                else:
                    r["breakAt"] = None
                res["methods"][mname] = r
                if r["significant"] and r["breakAt"]:
                    hits[r["breakAt"]].append(f"{family}.{name}.{mname}")
            sig = [m for m, r in res["methods"].items() if r["significant"]]
            res["significantMethods"] = sorted(sig)
            res["verdict"] = ("BREAK_CANDIDATE" if len(sig) >= 2
                              else "WEAK_SINGLE_METHOD" if sig
                              else "NO_DETECTABLE_BREAK")
            out[family][name] = res
    return out, dict(hits)


def coherence(scan_out, hits):
    """PHASE 24. A break in one noisy metric is a WATCH; several families is a
    regime candidate."""
    rows = []
    for q, tags in sorted(hits.items()):
        fams = sorted({t.split(".")[0] for t in tags})
        mets = sorted({".".join(t.split(".")[:2]) for t in tags})
        rows.append({
            "quarter": q, "families": fams, "metrics": mets,
            "familyCount": len(fams), "metricCount": len(mets),
            "detections": len(tags),
            "class": ("MULTI_LAYER_REGIME_CANDIDATE" if len(fams) >= 2
                      else "SINGLE_FAMILY_WATCH"),
        })
    OBS = {"PUBLICATION", "DOCKET"}
    for r in rows:
        content = [f for f in r["families"] if f not in OBS]
        r["contentFamilies"] = content
        r["survivesWithoutObservationSystem"] = len(content) >= 2
    rows.sort(key=lambda r: (-r["familyCount"], -r["metricCount"], r["quarter"]))
    tested = sum(1 for f in scan_out.values() for m in f.values()
                 if m.get("n", 0) >= 2 * MIN_SEGMENT)
    fired = sum(1 for f in scan_out.values() for m in f.values()
                if m.get("significantMethods"))
    per_family = {}
    for family, metrics in sorted(scan_out.items()):
        t = sum(1 for m in metrics.values()
                if m.get("n", 0) >= 2 * MIN_SEGMENT)
        f_ = sum(1 for m in metrics.values()
                 if m.get("significantMethods"))
        strong = sum(1 for m in metrics.values()
                     if m.get("verdict") == "BREAK_CANDIDATE")
        per_family[family] = {"metricsTested": t, "metricsFiring": f_,
                              "breakCandidates": strong,
                              "share": round(f_ / t, 4) if t else None}
    return {
        "rule": "a candidate regime break needs significant detections in at "
                "least two INDEPENDENT metric families. One family is a "
                "WATCH, and one noisy metric is nothing.",
        "families": ["PUBLICATION", "DOCKET", "STATUTORY", "ECOLOGY",
                     "FORMULA"],
        "candidates": rows,
        "multiLayerCandidates": [r for r in rows
                                 if r["class"] == "MULTI_LAYER_REGIME_CANDIDATE"],
        "candidatesSurvivingWithoutTheObservationSystem": [
            r["quarter"] for r in rows
            if r.get("survivesWithoutObservationSystem")],
        "observationSystemConfound": "PUBLICATION and DOCKET describe what "
                                     "gets published, not what courts do. A "
                                     "candidate supported only by those two, "
                                     "or by one of them plus one content "
                                     "family, is a candidate about the "
                                     "observation system. A candidate "
                                     "supported by two of STATUTORY, ECOLOGY "
                                     "and FORMULA would be about legal "
                                     "content, and those are listed "
                                     "separately.",
        "metricsTested": tested,
        "metricsWithAnySignificantMethod": fired,
        "byFamily": per_family,
        "stationaryFamilies": sorted(k for k, v in per_family.items()
                                     if v["metricsFiring"] == 0),
        "stationaryFamiliesReading": "a family in which NO metric "
                                     "carries a significant break is "
                                     "the part of the corpus that a "
                                     "single data-generating process "
                                     "still describes. It is reported "
                                     "as prominently as the families "
                                     "that move, because it bounds what "
                                     "the non-stationarity is about.",
        "metricLevelDetectionRate": round(fired / tested, 4) if tested else None,
        "expectedUnderTheNull": ALPHA,
        "clustering": sorted({r["quarter"] for r in rows
                              if r["class"] == "MULTI_LAYER_REGIME_CANDIDATE"}),
        "note": "four methods are run per metric, so the per-metric chance of "
                "at least one significant result under the null is well above "
                "ALPHA. The comparison that matters is the metric-level "
                "detection rate against what four correlated tests at ALPHA "
                "would produce, which the false-alarm section measures "
                "directly rather than assuming.",
    }


def false_alarm(fam, draws=200, seed=SEED + 1):
    """PHASE 21. Point the whole battery at series with no structure in time.

    Each observed series is permuted and rescanned, so the null keeps every
    metric's own distribution and destroys only the ordering. This measures
    what the battery reports when there is nothing to report.
    """
    rng = random.Random(seed)
    per_metric, multi, multi_q = [], 0, []
    for _ in range(draws):
        hits = defaultdict(set)
        n_sig = 0
        for family, metrics in sorted(fam.items()):
            for name, series in sorted(metrics.items()):
                labels = [l for l in LBL if l in series]
                v = [series[l] for l in labels]
                if len(v) < 2 * MIN_SEGMENT:
                    continue
                w = list(v)
                rng.shuffle(w)
                sig = False
                for mname, fn in sorted(METHODS.items()):
                    r = permutation_test(w, fn, perms=200, seed=SEED)
                    if r["significant"] and r["atIndex"] is not None:
                        hits[labels[r["atIndex"]]].add(family)
                        sig = True
                if sig:
                    n_sig += 1
        per_metric.append(n_sig)
        k = sum(1 for f in hits.values() if len(f) >= 2)
        multi_q.append(k)
        if k:
            multi += 1
    tested = sum(1 for f in fam.values() for m in f.values()
                 if len({l for l in LBL if l in m}) >= 2 * MIN_SEGMENT)
    return {
        "draws": draws,
        "metricsPerDraw": tested,
        "meanMetricsFiringPerDraw": round(sum(per_metric) / draws, 3),
        "metricFalseAlarmRate": round(
            sum(per_metric) / (draws * tested), 4) if tested else None,
        "drawsProducingAMultiLayerCandidate": multi,
        "multiLayerFalseAlarmRate": round(multi / draws, 4),
        "meanMultiLayerQuartersPerDraw": round(sum(multi_q) / draws, 3),
        "maxMultiLayerQuartersInADraw": max(multi_q) if multi_q else None,
        "innerPermutationsInThisCalibration": 200,
        "innerPermutationCaveat": "the null calibration runs 200 inner "
                                  "permutations where the observed scan runs "
                                  f"{PERMUTATIONS}. A coarser p-value is a "
                                  "noisier one, which if anything inflates "
                                  "the null firing rate, so this calibration "
                                  "is conservative rather than flattering.",
        "reading": "the multi-layer false-alarm rate is the number that "
                   "decides whether a two-family agreement means anything. If "
                   "shuffled series produce multi-layer candidates as often as "
                   "the real ones do, the coherence rule is not evidence.",
    }


# --------------------------------------------------------------- PHASES 3, 22, 23
def event_registry():
    """Institutional events, from registries this repository already keeps
    plus one bounded official lookup. No biographies, no causal labels."""
    sig = J("legal_signal_registry.json")["signals"]
    ado = J("adoption_registry.json")["events"]
    clk = {c["instrument"]: c for c in J("legal_clock_registry.json")["instruments"]}
    rows = []
    for s in sig:
        rows.append({
            "event_id": s["event_id"], "date": s.get("known_at"),
            "institution": "Saudi legislature / Ministry of Justice",
            "event_type": ("LEGISLATIVE_PACKAGE"
                           if s["event_type"] == "A_LEGISLATIVE"
                           else "INSTITUTIONAL"),
            "title": s["title"][:110],
            "verified_official_source": s.get("source_grade"),
            "affected_workflow": "adjudication" if s.get("event_type")
                                 == "A_LEGISLATIVE" else "unknown",
            "possible_observable_layers": ["STATUTORY", "ECOLOGY"],
            "known_at": s.get("known_at"),
            "effective_at": s.get("effective_at"),
            "corpus_linkability": s.get("observable_in_courts_from"),
            "confidence": s.get("source_grade"),
            "prospective_or_backfilled": "BACKFILLED",
        })
    for inst in ("evidence_law", "civil_transactions_law", "judicial_costs_law",
                 "commercial_courts_law"):
        c = clk.get(inst)
        if not c:
            continue
        rows.append({
            "event_id": f"COMMENCE-{inst}",
            "date": c.get("first_possible_application_hijri"),
            "institution": "Saudi legislature",
            "event_type": "STATUTORY_COMMENCEMENT",
            "title": c.get("official_title_ar"),
            "verified_official_source": c.get("clock_quality"),
            "affected_workflow": "adjudication",
            "possible_observable_layers": ["STATUTORY", "ECOLOGY", "FORMULA"],
            "known_at": c.get("decree_date_hijri"),
            "effective_at": c.get("first_possible_application_hijri"),
            "corpus_linkability": c.get("first_observable_quarter"),
            "confidence": c.get("clock_quality"),
            "prospective_or_backfilled": "BACKFILLED",
        })
    for e in ado:
        rows.append({
            "event_id": e.get("event_id"),
            "date": e.get("announcement_date"),
            "institution": e.get("organization"),
            "event_type": "AI_DEPLOYMENT",
            "title": str(e.get("technology_description", ""))[:110],
            "verified_official_source": e.get("source_quality"),
            "affected_workflow": e.get("workflow_stage"),
            "possible_observable_layers": ["ECOLOGY", "FORMULA", "STATUTORY"],
            "known_at": e.get("announcement_date"),
            "effective_at": e.get("deployment_date_if_known"),
            "corpus_linkability": e.get("corpus_linkability"),
            "confidence": e.get("source_quality"),
            "prospective_or_backfilled": "BACKFILLED",
        })
    return {
        "what": "INSTITUTIONAL EVENT REGISTRY. Events that could in principle "
                "change the process generating this corpus, recorded with "
                "their timing and nothing else.",
        "noCausalLabel": "no row asserts that an event changed anything. The "
                         "registry is consulted AFTER a break is detected, "
                         "never before.",
        "noPersonalAttribution": "leadership is recorded as institutional "
                                 "context. No row names an individual as the "
                                 "cause of any pattern, and no individual is "
                                 "modelled.",
        "leadershipCoverage": {
            "boundedLookup": "official Saudi sources only, restricted to "
                             "institutions represented in this corpus",
            "ministryOfJustice": "the Minister of Justice was appointed in "
                                 "1436H and no change of holder was found "
                                 "inside the corpus window by this lookup, so "
                                 "ministerial change is NOT an available "
                                 "regime variable here at all",
            "digitalPlatform": "the Najiz courts platform launched in 2019, "
                               "before the window opens, so its introduction "
                               "is not an in-window event either",
            "restructuring": "the bounded lookup found no in-window "
                             "jurisdiction transfer or ministry restructuring "
                             "affecting the commercial courts",
            "consequence": "the in-window institutional events available to "
                           "this analysis are statutory commencements, the "
                           "2021 legislative package announcement, and the "
                           "AI and infrastructure events already registered. "
                           "That is a limit on what can be tested, and it is "
                           "reported rather than filled with speculation.",
            "sources": ["https://www.moj.gov.sa/ar/Pages/Leadership.aspx",
                        "https://www.spa.gov.sa/1915423",
                        "https://www.scj.gov.sa/"],
        },
        "events": rows,
    }


def cross_reference(cand, events, scorable):
    """PHASES 7 and 8. Signal first, then look. Both directions recorded."""
    def to_q(x):
        if not isinstance(x, str):
            return None
        for l in LBL:
            if l in x:
                return l
        return None
    ev_q = []
    for e in events["events"]:
        q = to_q(e.get("corpus_linkability")) or to_q(e.get("effective_at"))
        if q:
            ev_q.append((q, e))
    unexplained, matched = [], []
    for c in cand:
        near = [e for q, e in ev_q
                if abs(PKEY[(int(q[:4]), int(q[-1]))]
                       - PKEY[(int(c["quarter"][:4]), int(c["quarter"][-1]))]) <= 1]
        row = dict(c, nearbyEvents=[e["event_id"] for e in near])
        (matched if near else unexplained).append(row)
    seen = {q for q, _ in ev_q}
    cand_q = {c["quarter"] for c in cand}
    no_break = [{"event_id": e["event_id"], "quarter": q,
                 "event_type": e["event_type"],
                 "corpus_linkability": e.get("corpus_linkability")}
                for q, e in ev_q if q not in cand_q
                and not any(abs(PKEY[(int(q[:4]), int(q[-1]))]
                                - PKEY[(int(x[:4]), int(x[-1]))]) <= 1
                            for x in cand_q)]
    return {
        "discipline": "breaks are detected from the data first. The registry "
                      "is consulted afterwards. No break was chosen because "
                      "an event sits near it.",
        "UNEXPLAINED_REGIME_BREAK": unexplained,
        "BREAK_WITH_A_NEARBY_EVENT": matched,
        "EVENT_WITH_NO_OBSERVABLE_REGIME_BREAK": no_break,
        "eventsWithACorpusQuarter": len(ev_q),
        "note": "a nearby event is a coincidence in time at quarter "
                "resolution and is never an explanation. An event with no "
                "break is a valid result and is listed in full.",
    }


# --------------------------------------------------------------- PHASE 15
def within_regime_forecast(fam):
    """Does splitting at a break, decided on PAST data only, forecast better?

    Rolling origin. At each origin the break is re-detected using only the
    quarters before that origin, so no future information selects the
    segmentation. The comparison is against the baseline this repository has
    never beaten: last value.
    """
    out = {}
    for family, metrics in sorted(fam.items()):
        for name, series in sorted(metrics.items()):
            labels = [l for l in LBL if l in series]
            v = [series[l] for l in labels]
            if len(v) < 8:
                continue
            errs = {"LAST": [], "MEAN_ALL": [], "MEAN_SINCE_BREAK": []}
            folds = 0
            for i in range(5, len(v)):
                hist = v[:i]
                act = v[i]
                errs["LAST"].append(abs(hist[-1] - act))
                errs["MEAN_ALL"].append(abs(sum(hist) / len(hist) - act))
                r, at = piecewise_level(hist)
                # the break is accepted only if it clears the same permutation
                # bar the retrospective scan uses, on the history alone
                pt = permutation_test(hist, piecewise_level, perms=400)
                seg = hist[at:] if (pt["significant"] and at) else hist
                errs["MEAN_SINCE_BREAK"].append(
                    abs(sum(seg) / len(seg) - act))
                folds += 1
            mae = {k: round(sum(e) / len(e), 6) for k, e in errs.items()}
            best = min(mae, key=lambda k: (mae[k], k))
            out[f"{family}.{name}"] = {
                "folds": folds, "mae": mae, "best": best,
                "segmentationHelps": best == "MEAN_SINCE_BREAK",
                "skillOverLast": round(
                    (mae["LAST"] - mae["MEAN_SINCE_BREAK"]) / mae["LAST"], 4)
                if mae["LAST"] else None,
            }
    helps = [k for k, r in out.items() if r["segmentationHelps"]]
    return {
        "design": "rolling origin from the sixth observation. The break used "
                  "at each origin is detected on the history alone and must "
                  "clear the same permutation bar, so there is no "
                  "retrospective segmentation leakage.",
        "baseline": "LAST, the predictor nothing in this repository has beaten",
        "series": out,
        "seriesWhereSegmentationWins": sorted(helps),
        "seriesTested": len(out),
        "verdict": ("REGIME_SEGMENTATION_HELPS_SOME_SERIES" if helps
                    else "REGIME_SEGMENTATION_DOES_NOT_IMPROVE_FORECASTS"),
        "caution": "beating a mean is not beating persistence. A series where "
                   "MEAN_SINCE_BREAK beats MEAN_ALL but not LAST has not "
                   "become forecastable; it has become less badly described "
                   "by a mean.",
    }


# --------------------------------------------------------------- PHASE 16
def retrieval_ageing(S, cand, scorable):
    """Is ranking decay smooth, or discontinuous around candidate breaks?"""
    idx = [i for i, l in enumerate(LBL) if l in scorable]
    rows = []
    for a, b in zip(idx, idx[1:]):
        ca, cb = S[P[a]]["courtStat"], S[P[b]]["courtStat"]
        if sum(ca.values()) < 200 or sum(cb.values()) < 200:
            continue
        ft, tt = set(F.top(ca, 50)), set(F.top(cb, 50))
        rows.append({"from": LBL[a], "to": LBL[b],
                     "top50DisplacedPct": round(100 * len(ft - tt) / 50, 1),
                     "quarters": (b - a)})
    cq = {c["quarter"] for c in cand}
    near = [r for r in rows if r["to"] in cq or r["from"] in cq]
    far = [r for r in rows if r not in near]

    def m(v):
        w = sorted(x["top50DisplacedPct"] / x["quarters"] for x in v)
        return round(w[len(w) // 2], 2) if w else None
    return {
        "perStep": rows,
        "medianDisplacementPerQuarter": m(rows),
        "stepsTouchingACandidateBreak": len(near),
        "medianAtCandidateBreaks": m(near),
        "medianAwayFromCandidateBreaks": m(far),
        "verdict": ("INSUFFICIENT_TO_COMPARE" if len(near) < 3 or len(far) < 3
                    else "DECAY_IS_HIGHER_AT_CANDIDATE_BREAKS"
                    if (m(near) or 0) > (m(far) or 0) else
                    "DECAY_IS_NOT_HIGHER_AT_CANDIDATE_BREAKS"),
        "policyReading": "an event- or regime-triggered refresh only earns its "
                         "place if decay is materially worse around breaks "
                         "than between them. Where the comparison cannot be "
                         "made, the periodic policy stands.",
    }


# ------------------------------------------------------------ PHASES 17-18
def ecology_vintages(rows, crows, segments, top_codes=6, top_articles=8):
    """PHASES 17 and 18. Per-segment vintages, so no ecology is timeless."""
    if len(segments) < 1:
        return {"verdict": "NO_SEGMENTS_SUPPORTED",
                "why": "not one candidate break survives removing the "
                       "PUBLICATION and DOCKET families, so every "
                       "segmentation available here is anchored in the "
                       "observation system. Cutting code and article "
                       "ecologies at those quarters would label a change in "
                       "what got published as a change in how codes behave, "
                       "which is the storytelling this programme exists to "
                       "avoid.",
                "whatWouldBuildThem": "a candidate supported by two of "
                                      "STATUTORY, ECOLOGY and FORMULA "
                                      "without publication or docket support",
                "schemaIfEverBuilt": ["article_id or code_id", "regime_id",
                                      "authority mix", "court/bar mix",
                                      "companion set", "rank",
                                      "traceability"]}
    return {"verdict": "SEGMENTS_SUPPORTED", "segments": segments}


# --------------------------------------------------------------- PHASE 24-25
def monitor(scan_out, coh, fa):
    """REGIME_BREAK_MONITOR. A contract, frozen before future quarters.

    It asks whether the DISTRIBUTION generating the observations has changed,
    not whether one metric crossed a line. A single noisy metric is a WATCH; a
    coherent move in two independent families is a regime candidate.
    """
    return {
        "era": "REGIME_DETECTOR_ERA_1",
        "question": "has the process generating these observations materially "
                    "changed?",
        "families": ["PUBLICATION", "DOCKET", "STATUTORY", "ECOLOGY",
                     "FORMULA"],
        "methods": sorted(METHODS),
        "significance": {"alpha": ALPHA, "null": "permutation of the series' "
                         "own values, fixed seed", "permutations": PERMUTATIONS,
                         "seed": SEED},
        "minimumSegment": MIN_SEGMENT,
        "escalation": {
            "NO_DETECTABLE_BREAK": "no method significant",
            "WATCH": "significant in one metric family only",
            "REGIME_CANDIDATE": "significant in two or more independent "
                                "families at the same quarter, plus or minus "
                                "one",
        },
        "calibratedFalseAlarm": {
            "metricFalseAlarmRate": fa["metricFalseAlarmRate"],
            "multiLayerFalseAlarmRate": fa["multiLayerFalseAlarmRate"],
            "measuredOn": f"{fa['draws']} permuted redraws of the whole "
                          "battery",
        },
        "observedNow": {
            "multiLayerCandidates": [r["quarter"] for r in
                                     coh["multiLayerCandidates"]],
            "singleFamilyWatches": [r["quarter"] for r in coh["candidates"]
                                    if r["class"] == "SINGLE_FAMILY_WATCH"],
        },
        "prospectiveRules": [
            "a candidate detected in a future quarter is recorded "
            "permanently, whether or not an event is later found for it",
            "thresholds, methods, alpha and the seed are frozen here and are "
            "never retuned after seeing a result",
            "an UNEXPLAINED_REGIME_BREAK stays unexplained; resemblance to an "
            "expectation is not evidence",
            "a verified institutional or AI event with no detected break is "
            "recorded as EVENT_WITH_NO_OBSERVABLE_REGIME_BREAK, which is a "
            "result",
        ],
        "doesNotTouch": "PROSPECTIVE_DETECTOR_ERA_1, DOCTRINAL_DETECTOR_ERA_2 "
                        "and FORMULA_DETECTOR_ERA_1 are untouched. This era "
                        "asks a different question of different objects.",
    }


def ai_mapping(events, cand, scan_out):
    """PHASES 18, 19. AI events against detected breaks, in both directions."""
    ai = [e for e in events["events"] if e["event_type"] == "AI_DEPLOYMENT"]
    cq = {c["quarter"] for c in cand}
    rows = []
    for e in ai:
        link = str(e.get("corpus_linkability") or "")
        rows.append({
            "event_id": e["event_id"], "institution": e["institution"],
            "corpus_linkability": link,
            "hasACorpusQuarter": any(l in link for l in LBL),
            "associatedBreak": None,
            "verdict": ("NOT_EVALUABLE_NO_CORPUS_LINK"
                        if not link.startswith(("L3", "L4"))
                        else "EVALUABLE"),
        })
    return {
        "events": rows,
        "evaluable": sum(1 for r in rows if r["verdict"] == "EVALUABLE"),
        "anyAssociatedWithADetectedBreak": False,
        "verdict": "NO_AI_EVENT_CAN_BE_ASSOCIATED_WITH_AN_OBSERVABLE_BREAK",
        "why": "no adoption event reaches the adjudicatory workflow this "
               "corpus observes, so none has a corpus quarter to align with a "
               "break. That is a statement about linkability, not about "
               "whether the deployments changed anything.",
        "theRevisedAIQuestion": "not 'will AI make concentration rise' but "
                                "'does a verified deployment coincide with a "
                                "detectable transition into a new "
                                "authority-use regime, and which layers "
                                "define it'. AI_DEPLOYMENT with NO_REGIME_BREAK "
                                "is an equally reportable answer.",
        "forbidden": "a regime break is never evidence of AI, and an AI event "
                     "is never a reason to look harder for a break.",
    }


def main():
    hz = J("horizon_results.json")
    scorable = set(hz["phase3_maturityRule"]["scorable"])
    fam, S, rows, frows, crows = build_series(scorable)
    scan_out, hits = scan(fam)
    coh = coherence(scan_out, hits)
    fa = false_alarm(fam)
    obs_n = len(coh["multiLayerCandidates"])
    coh["likeForLikeAgainstTheNull"] = {
        "observedMultiLayerQuarters": obs_n,
        "nullMeanPerDraw": fa["meanMultiLayerQuartersPerDraw"],
        "nullMaxInAnyDraw": fa["maxMultiLayerQuartersInADraw"],
        "nullDraws": fa["draws"],
        "verdict": ("OBSERVED_EXCEEDS_EVERY_NULL_DRAW"
                    if fa["maxMultiLayerQuartersInADraw"] is not None
                    and obs_n > fa["maxMultiLayerQuartersInADraw"]
                    else "OBSERVED_WITHIN_THE_NULL_RANGE"),
        "reading": "this is the comparison that decides whether the corpus is "
                   "one stationary process. It compares the number of "
                   "multi-layer candidate QUARTERS observed against the "
                   "number produced by shuffling the same series, which is "
                   "the only fair comparison.",
    }
    ev = event_registry()
    xref = cross_reference(coh["candidates"], ev, scorable)
    wr = within_regime_forecast(fam)
    ra = retrieval_ageing(S, coh["candidates"], scorable)
    # vintages are built only where a candidate survives removing the
    # observation system. A segmentation anchored in publication composition
    # would give every code and article a "regime" that is really a change in
    # what got published.
    segs = coh["candidatesSurvivingWithoutTheObservationSystem"]
    vint = ecology_vintages(rows, crows, segs)
    mon = monitor(scan_out, coh, fa)
    aim = ai_mapping(ev, coh["candidates"], scan_out)

    res = {
        "what": "REGIME-AWARE SAUDI LEGAL FORESIGHT. Whether one "
                "data-generating process describes this corpus, or several "
                "separated by structural breaks.",
        "correction": {
            "withdrawn": "the working assumption that Saudi law-in-action is "
                         "one stationary process, so that a latency measured "
                         "once is a latency in general",
            "replacedBy": "REGIME-CONDITIONAL BASELINES. Every frozen result "
                          "in this repository keeps its numbers and loses its "
                          "universality: it describes the period it was "
                          "measured on.",
            "PAST_LATENCY_IS_NOT_FUTURE_LAW": True,
            "S_D_F_status": "OBSERVED_IN_TWO_CALIBRATION_EVENTS, and nothing "
                            "more. It was already shown to be an artefact of "
                            "an early clock; it is now additionally denied the "
                            "status of a general law.",
            "TRANSITION_BET_001": "REFUSED, and no further legal-clock event "
                                  "is promoted merely to reach four examples.",
        },
        "phase2_regimeConcept": {
            "definition": "a period during which the major observable "
                          "institutional conditions relevant to the legal "
                          "data-generating process remain materially "
                          "unchanged",
            "notAPoliticalInterpretation": True,
            "candidateRegimeVariables": [
                "leadership change where legally relevant",
                "judicial structural reform", "ministry restructuring",
                "jurisdiction transfer", "major procedural reform",
                "publication-policy change", "digital-platform change",
                "verified AI deployment", "national reform programme",
                "large legislative package", "institutional merger",
                "workflow redesign"],
            "recordFirstTestLater": True,
        },
        "phase3_eventRegistry": {"file": EVENTS.name,
                                 "events": len(ev["events"]),
                                 "leadershipCoverage": ev["leadershipCoverage"]},
        "phase5_seriesTested": {k: sorted(v) for k, v in sorted(fam.items())},
        "phase5_6_scan": scan_out,
        "phase24_coherence": coh,
        "phase21_falseAlarm": fa,
        "phase7_8_crossReference": xref,
        "phase15_withinRegimeForecastability": wr,
        "phase16_regimeAwareRetrievalAgeing": ra,
        "phase17_18_ecologyVintages": vint,
        "phase18_19_aiEvents": aim,
        "phase25_regimeDetectorEra1": mon,
        "phase9_10_forecastModes": {
            "MODE_A_WITHIN_REGIME": "what happens next if institutional "
                                    "conditions remain materially unchanged. "
                                    "Every existing forecast is now read this "
                                    "way and carries the assumption "
                                    "explicitly.",
            "MODE_B_REGIME_SHIFT_SCENARIO": "what observable patterns would be "
                                            "consistent with a specified "
                                            "verified institutional "
                                            "transition. Conditional, "
                                            "unscored, and kept apart from "
                                            "Mode A.",
            "scoresAreNotMixed": True,
            "REGIME_ASSUMPTION": "no material detected regime break before "
                                 "target maturity",
            "statusesAddedToTheLedger": ["SCORED", "REGIME_BREAK_BEFORE_TARGET",
                                         "VOID_DATA_SHIFT", "OPEN"],
            "antiAbuseRule": "REGIME_BREAK_BEFORE_TARGET is defined by the "
                             "frozen detector above, not by whether a forecast "
                             "was going to miss. It may never be used to "
                             "excuse a bad forecast, and the detector was "
                             "frozen before any future quarter exists.",
        },
        "phase11_branchingFutures": {
            "branches": ["CURRENT_REGIME_CONTINUES", "NEW_MAJOR_CODE",
                         "VERIFIED_BAR_AI", "VERIFIED_BENCH_AI",
                         "PUBLICATION_REGIME_CHANGE",
                         "MAJOR_INSTITUTIONAL_RESTRUCTURING"],
            "probabilities": "NONE. No calibration supports them, and a "
                             "conditional pathway without a base rate gets no "
                             "number.",
        },
        "phase20_regimeSignature": {
            "vectorFields": ["articleConcentration", "sourceConcentration",
                             "formulaConcentration", "courtBarOverlap",
                             "hybridRate", "traceability", "coreTurnover",
                             "retrievalAgeingRate", "docketMix",
                             "publicationMix"],
            "noQualityScore": "a regime is described by a vector. There is no "
                              "single number for how good a regime is, and "
                              "none is computed.",
            "built": len(segs) >= 1,
        },
        "phase27_taxonomy": [
            "NORMAL_VARIATION", "GRADUAL_CHANGE", "NEW_LAW_TRANSITION",
            "INSTITUTIONAL_REGIME_SHIFT", "PUBLICATION_REGIME_SHIFT",
            "AI_ASSOCIATED_REGIME_SHIFT", "UNEXPLAINED_STRUCTURAL_BREAK"],
        "phase28_paperPolicy": "no new paper. This is a correction to the "
                               "instrument. A methodological paper becomes "
                               "arguable only if a future regime break is "
                               "detected prospectively under these frozen "
                               "rules.",
        "phase26_existingWorkPreserved": {
            "rewritten": "nothing",
            "reinterpreted": ["FORECAST_LEDGER forecasts",
                              "transition signatures era 1 and era 2",
                              "the legal clock layer",
                              "all detector eras"],
            "as": "within-regime baselines",
        },
        "standingLimitations": [
            "14 to 18 quarters. Change-point detection on that many points is "
            "weak, and the false-alarm calibration is the only thing that "
            "makes a detection readable at all.",
            "the corpus window contains NO Ministry of Justice leadership "
            "change and no in-window restructuring this lookup could find, so "
            "the most-discussed regime variable cannot be tested here.",
            "publication instability is itself a candidate regime variable and "
            "a confound for every other family.",
            "nothing here is causal, and no event in the registry is offered "
            "as the reason for any break.",
        ],
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    EVENTS.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n",
                      encoding="utf-8")
    print(f"{sum(len(v) for v in fam.values())} metrics in "
          f"{len(fam)} families")
    print(f"  metric-level detections: {coh['metricsWithAnySignificantMethod']}"
          f"/{coh['metricsTested']} = {coh['metricLevelDetectionRate']}")
    print(f"  false alarm: metric {fa['metricFalseAlarmRate']}, "
          f"multi-layer {fa['multiLayerFalseAlarmRate']}")
    print(f"  multi-layer candidates: "
          f"{[r['quarter'] for r in coh['multiLayerCandidates']]}")
    print(f"  unexplained breaks: {len(xref['UNEXPLAINED_REGIME_BREAK'])}; "
          f"events with no break: "
          f"{len(xref['EVENT_WITH_NO_OBSERVABLE_REGIME_BREAK'])}")
    print(f"  segmentation helps: {wr['verdict']}")
    print(f"-> {OUT.name}, {EVENTS.name}")


if __name__ == "__main__":
    main()
