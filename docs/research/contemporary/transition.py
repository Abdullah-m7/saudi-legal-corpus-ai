#!/usr/bin/env python3
"""When a real legal transition occurs, which observable layer moves first?

The repository now measures several layers separately -- statutory visibility
in each voice, the authority-adjacent formula layer, the non-statutory
authority ecology, doctrinal companions, the operational core, and the state
of a frozen retrieval snapshot. Each has been described on its own. None has
been watched THROUGH a transition.

That gap matters for exactly one reason. When a verified AI deployment finally
becomes observable in a corpus like this one, the useful sentence is not "AI
changed something". It is:

    the first prospectively detected departure occurred in layer X, followed
    Y quarters later by layer Z, while the remaining layers stayed inside
    their frozen historical bounds

and that sentence is only available to someone who already knows what an
ORDINARY legal transition looks like. This file measures ordinary transitions
so the extraordinary one can be recognised.

Two real transitions are available: the Law of Evidence, observable from
1443Q1, and the Civil Transactions Law, observable from 1445Q1. Both have a
legal clock in the signal registry that is independent of any outcome in the
corpus. Everything else in the window either has no known legal timing or too
little court use, and is classified rather than analysed.

NOTHING HERE IS CAUSAL. A layer crossing a criterion after a commencement date
is an ordering of observations. It is never the statute acting on the court.

    python3 transition.py
"""
import gzip
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

OUT = HERE / "transition_results.json"
LIB = HERE / "transition_signatures.json"
J = lambda n: json.loads((HERE / n).read_text(encoding="utf-8"))
P, LBL, PKEY = F.P, F.LBL, F.PKEY

# Thresholds fixed BEFORE any event's post-period was inspected, and reused
# unchanged for every event. None is tuned per law.
TOP50_DISPLACEMENT_PCT = 30.0      # inherited from the frozen BET_001 trigger
REPEATED_SOURCE_JUDGMENTS = 2      # a companion is a source seen twice
CONCENTRATION_SHIFT = 0.15         # absolute move in a share, against baseline
MIN_COURT_CITES_FOR_LAYER = 5      # a quarter with fewer is not evidence
HORIZON = 6                        # quarters after T0 that any event is judged on
# Articles asked for by name before the analysis ran. They are reported
# whether or not they turn out to be interesting.
NAMED_ARTICLES = {"civil_transactions_law": (120, 720, 107)}


# ------------------------------------------------------------------ PHASE 4
def publication_health():
    """LAYER ZERO. If the observation system moves, nothing above it is read.

    Runs before any transition analysis and can veto one. A change in what the
    publisher releases would show up in every layer as if it were law.
    """
    fs = J("foresight_results.json")
    prof = fs.get("publicationProfile", {})
    rows = prof.get("byPeriod", [])
    if not rows:
        return {"verdict": "NO_PUBLICATION_PROFILE"}
    by = {r["period"]: r for r in rows}
    keys = ["medianReasonChars", "shareWithReasons", "shareAppeal",
            "share_feesClaim", "share_damagesClaim", "share_proofDispute",
            "share_expert", "share_settlement", "share_default"]
    # A quarter is UNSTABLE when any composition share moves by more than a
    # quarter of its own historical range against the preceding quarter. The
    # rule is stated here and applied to every quarter, event or not.
    rng = {k: (max(r[k] for r in rows) - min(r[k] for r in rows)) for k in keys}
    flags = {}
    for a, b in zip(rows, rows[1:]):
        bad = [k for k in keys if rng[k] and abs(b[k] - a[k]) > 0.25 * rng[k]]
        flags[b["period"]] = bad
    return {
        "periodsProfiled": len(rows),
        "rule": "a quarter is DATA_UNSTABLE when any publication-composition "
                "share moves against the previous quarter by more than a "
                "quarter of that share's own full historical range. Applied "
                "identically to every quarter.",
        "historicalRange": {k: round(v, 4) for k, v in sorted(rng.items())},
        "unstableQuarters": {k: v for k, v in sorted(flags.items()) if v},
        "stableQuarters": sorted(k for k, v in flags.items() if not v),
        "flagsPerQuarter": {k: len(v) for k, v in sorted(flags.items())},
        "verdict": ("GATE_FAILS_FOR_EVERY_QUARTER"
                    if all(v for v in flags.values())
                    else "GATE_PASSES_SOMEWHERE"),
        "consequence": "the rule was written to veto a transition read under "
                       "a moving observation system. It fires on all but one "
                       "quarter-to-quarter step in this corpus, so as a veto "
                       "it would reject every transition there is. It is "
                       "therefore demoted to a STANDING CAVEAT attached to "
                       "every latency in this file, and it is NOT loosened "
                       "until it passes -- loosening a control until it "
                       "permits the result is how a control stops being one. "
                       "The severity count per quarter is reported so the two "
                       "events can be compared on how disturbed their windows "
                       "are.",
        "whichLayersAreMostExposed": [
            "L5_AUTHORITY_ECOLOGY and L4_AUTHORITY_ADJACENT_FORMULA depend on "
            "reasons length, which is one of the moving quantities",
            "L7_OPERATIONAL_CORE and L8_RETRIEVAL_STATE depend on the volume "
            "and claim mix of what is published",
            "L2 and L3 FIRST_VISIBILITY are the least exposed: a first "
            "citation is a first citation whatever else is published"],
        "byPeriod": {r["period"]: {k: r[k] for k in ["judgments"] + keys}
                     for r in rows},
        "limitation": "there is no publication date in either institution's "
                      "metadata, so decision-to-publication lag remains "
                      "NOT_AVAILABLE and a composition shift cannot be "
                      "attributed to selection rather than to the docket.",
        "_flags": flags,
    }


# ------------------------------------------------------------------ PHASE 2
def candidates(hz):
    """Events selected on their CLOCK and their SUPPORT, never their outcome."""
    reg = J("legal_signal_registry.json")
    monitor = {r["instrument"]: r for r in hz["phase6_newLawMonitor"]["rows"]}
    # the registry's own instrument key for each observable legislative signal
    LINK = {"LSIG-0002": "evidence_law", "LSIG-0003": "civil_transactions_law"}
    out = []
    for s in reg["signals"]:
        inst = LINK.get(s["event_id"])
        obs = str(s.get("observable_in_courts_from", ""))
        row = {"event_id": s["event_id"], "event_type": s["event_type"],
               "title": s["title"][:90], "instrument": inst,
               "known_at": s.get("known_at"),
               "effective_at": s.get("effective_at"),
               "observable_in_courts_from": obs,
               "first_recorded_at": s.get("first_recorded_at"),
               "source_grade": s.get("source_grade")}
        if inst is None:
            row["class"] = "INSUFFICIENT_DATA"
            row["why"] = ("no corpus-linkable instrument: the event is "
                          "announced, institutional, or in a forum this "
                          "corpus does not contain")
        elif inst not in monitor:
            row["class"] = "INSUFFICIENT_DATA"
            row["why"] = "the instrument does not arrive inside the window"
        else:
            m = monitor[inst]
            row["courtJudgmentsToDate"] = m["courtJudgmentsToDate"]
            row["firstCourtQuarter"] = m["firstCourtQuarter"]
            row["class"] = ("CALIBRATION_EVENT"
                            if m["courtJudgmentsToDate"] >= 200
                            else "INSUFFICIENT_DATA")
            row["why"] = ("a known legal clock, a corpus-linkable instrument, "
                          "a pre-period inside the window and at least 200 "
                          "court judgments"
                          if row["class"] == "CALIBRATION_EVENT"
                          else "too little court use to read six layers")
        out.append(row)
    # instruments arriving in-window WITHOUT a registry clock: negative or
    # insufficient, never promoted by how interesting their series looks
    noclock = []
    for inst, m in sorted(monitor.items()):
        if inst in LINK.values():
            continue
        noclock.append({
            "instrument": inst, "firstCourtQuarter": m["firstCourtQuarter"],
            "courtJudgmentsToDate": m["courtJudgmentsToDate"],
            "class": "INSUFFICIENT_DATA",
            "why": "arrives in the window but carries no known_at or "
                   "effective_at in any registry this repository holds, so "
                   "T=0 would have to be read off the first citation, which "
                   "is an outcome"})
    return {
        "selectionRule": "an event qualifies only if it has a known legal "
                         "clock independent of the corpus, a corpus-linkable "
                         "instrument, a pre-period inside the window, and "
                         "enough court use to read the layers. Nothing is "
                         "selected because its series looks interesting.",
        "registrySignals": out,
        "inWindowInstrumentsWithoutAClock": noclock,
        "calibrationEvents": [r["event_id"] for r in out
                              if r["class"] == "CALIBRATION_EVENT"],
        "whyNotSixtyEventStudies": "58 of the 60 in-window arrivals have no "
                                   "legal timing this repository can verify. "
                                   "Reading T=0 off the first citation would "
                                   "make the event clock a function of the "
                                   "outcome, which is the single mistake this "
                                   "design exists to avoid.",
    }


# ------------------------------------------------------------------ PHASE 3
HIJRI_Q0 = {1443: (1443, 1), 1445: (1445, 1)}


def clock(row):
    """ANNOUNCEMENT, LEGAL EFFECT, FIRST POSSIBLE OBSERVATION, FIRST ACTUAL.

    The primary event clock is the legal one. The first actual observation is
    recorded beside it and never used as T=0, because it is an outcome of the
    thing being measured.
    """
    eff = row.get("effective_at")
    obs = row.get("observable_in_courts_from") or ""
    t0 = None
    for lbl in LBL:
        if lbl in obs:
            t0 = PKEY[(int(lbl[:4]), int(lbl[-1]))]
            break
    quality = "REGISTRY_OBSERVABLE_FROM"
    if str(eff).isdigit() and int(eff) in HIJRI_Q0:
        p = HIJRI_Q0[int(eff)]
        if p in PKEY and (t0 is None or PKEY[p] == t0):
            t0, quality = PKEY[p], "LEGAL_EFFECTIVE_YEAR"
    return {
        "announcement": row.get("known_at"),
        "legalEffectiveAt": eff,
        "firstPossibleCourtObservation": LBL[t0] if t0 is not None else None,
        "firstActualCourtObservation": row.get("firstCourtQuarter"),
        "T0": LBL[t0] if t0 is not None else None,
        "T0Index": t0,
        "clockQuality": quality,
        "clockIsNotAnOutcome": "T=0 is the first quarter in which the law "
                               "could be applied, taken from the registry. "
                               "The first citation is recorded separately and "
                               "is a result, not a clock.",
        "limitation": "the corpus holds no commencement date per instrument. "
                      "Where the registry gives only a hijri year, the first "
                      "quarter of that year is used and the quality is "
                      "recorded as such. No commencement date is invented.",
    }


# --------------------------------------------------------------- PHASES 5-7
def series(rows, S, inst):
    """Everything measurable about one instrument, per quarter."""
    n = len(P)
    out = {k: [0] * n for k in ("courtCites", "partyCites", "courtJ", "partyJ",
                                "hybridJ", "namedFiqhJ", "tracedMentions",
                                "nonStatMentions")}
    cj = [set() for _ in range(n)]
    pj = [set() for _ in range(n)]
    arts = [set() for _ in range(n)]
    by_j = defaultdict(list)
    for r in rows:
        by_j[r["j"]].append(r)
    for j, ms in by_j.items():
        i = PKEY[ms[0]["p"]]
        cites_court = [m for m in ms if m["role"] == F.COURT
                       and m["t"] == "statute" and m.get("inst") == inst]
        cites_party = [m for m in ms if m["role"] == F.PARTY
                       and m["t"] == "statute" and m.get("inst") == inst]
        if cites_court:
            cj[i].add(j)
            out["courtCites"][i] += len(cites_court)
            arts[i].update(m.get("art") for m in cites_court
                           if m.get("art") is not None)
            ns = [m for m in ms if m["role"] == F.COURT
                  and m["t"] in F.NONSTATUTE]
            out["nonStatMentions"][i] += len(ns)
            if ns:
                out["hybridJ"][i] += 1
            if any(m["r"] in F.NAMED_FIQH for m in ns):
                out["namedFiqhJ"][i] += 1
            out["tracedMentions"][i] += sum(1 for m in ns
                                            if m.get("res") == "named")
        if cites_party:
            pj[i].add(j)
            out["partyCites"][i] += len(cites_party)
    out["courtJ"] = [len(x) for x in cj]
    out["partyJ"] = [len(x) for x in pj]
    out["articles"] = [sorted(x) for x in arts]
    out["courtShare"] = [
        (out["courtCites"][i] / max(1, sum(S[P[i]]["courtInst"].values())))
        for i in range(n)]
    out["courtRank"] = []
    for i in range(n):
        c = S[P[i]]["courtInst"]
        order = [k for k, _ in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))]
        out["courtRank"].append(order.index(inst) + 1 if inst in order else None)
    out["hybridRate"] = [
        (out["hybridJ"][i] / out["courtJ"][i]) if out["courtJ"][i] else None
        for i in range(n)]
    out["namedFiqhRate"] = [
        (out["namedFiqhJ"][i] / out["courtJ"][i]) if out["courtJ"][i] else None
        for i in range(n)]
    out["traceability"] = [
        (out["tracedMentions"][i] / out["nonStatMentions"][i])
        if out["nonStatMentions"][i] else None for i in range(n)]
    return out


def formula_series(frows, inst, t0):
    """L4. Authority-adjacent recurring formulas beside one instrument.

    NEW versus REUSED is the distinction PHASE 9 turns on: a formula cannot
    appear around an authority beside a new law before the law exists, but a
    formula already circulating elsewhere can be carried to it. Those are
    different events and are counted apart.
    """
    n = len(P)
    firstq = {}
    first_inst = defaultdict(set)
    for r in frows:
        t = r["tmpl"]
        firstq[t] = min(firstq.get(t, r["i"]), r["i"])
        if r["instW"]:
            first_inst[t].add(r["instW"])
    per = [defaultdict(int) for _ in range(n)]
    for r in frows:
        if r["instW"] == inst:
            per[r["i"]][r["tmpl"]] += 1
    seen_here = set()
    rows = []
    for i in range(n):
        d = per[i]
        new = [t for t in d if firstq[t] == i]
        reused = [t for t in d if firstq[t] < i and t not in seen_here]
        vals = sorted(d.values(), reverse=True)
        rows.append({
            "period": LBL[i], "mentions": sum(d.values()),
            "distinctFormulas": len(d),
            "firstObservedAnywhereHere": len(new),
            "carriedFromEarlierQuarters": len(reused),
            "top1Share": round(vals[0] / sum(vals), 4) if vals else None,
        })
        seen_here.update(d)
    # PHASE 10: of the formulas ever seen beside this instrument after T0,
    # how many were already circulating beside a DIFFERENT instrument before?
    ever = {t for i in range(n) for t in per[i]}
    pre = {t for t, q in firstq.items() if t0 is not None and q < t0}
    elsewhere = {t for t in ever if first_inst[t] - {inst}}
    return {
        "byPeriod": rows,
        "formulasEverBesideInstrument": len(ever),
        "alreadyObservedBeforeT0": len(ever & pre),
        "alsoObservedBesideAnotherInstrument": len(ever & elsewhere),
        "newlyObservedWithThisInstrument": len(ever - pre),
        "uptakeMix": {
            "A_newlyObservedFormulas": len(ever - pre),
            "B_carriedFromOlderLaw": len(ever & pre & elsewhere),
            "C_carriedButNeverSeenBesideAnotherInstrument":
                len((ever & pre) - elsewhere)},
        "preT0QuartersAvailable": t0 if t0 is not None else None,
        "leftTruncationWarning": (
            "the pre-T0 window is only %d quarter(s) of corpus, so "
            "'newly observed' is inflated: a formula circulating for years "
            "before the corpus begins is newly observed here. The count is a "
            "ceiling on innovation, not a measure of it." % (t0 or 0)
            if (t0 or 0) < 8 else None),
        "note": "A formula appearing beside a new instrument is a wording "
                "observation. It is not the court applying old reasoning to "
                "new law, and no adaptation is asserted.",
    }


def companion_series(crows, inst, scorable):
    """L6. The first REPEATED non-statutory source beside the instrument."""
    n = len(P)
    per = [defaultdict(set) for _ in range(n)]
    for r in crows:
        if r["instW"] == inst and r["voice"] == "court":
            per[r["i"]][r["cid"]].add(r["j"])
    cum = defaultdict(set)
    first_rep, rows = None, []
    for i in range(n):
        for cid, js in per[i].items():
            cum[cid] |= js
        rep = sorted(c for c, js in cum.items()
                     if len(js) >= REPEATED_SOURCE_JUDGMENTS)
        if rep and first_rep is None:
            first_rep = i
        vals = sorted((len(js) for js in per[i].values()), reverse=True)
        rows.append({"period": LBL[i], "sourcesThisQuarter": len(per[i]),
                     "repeatedSourcesToDate": len(rep),
                     "topSourceShare": round(vals[0] / sum(vals), 4)
                     if vals else None})
    idx = [i for i, l in enumerate(LBL) if l in scorable]
    persist = {}
    if first_rep is not None:
        firsts = sorted(c for c, js in
                        {k: v for k, v in cum.items()}.items()
                        if len(js) >= REPEATED_SOURCE_JUDGMENTS)
        later = [i for i in idx if i > first_rep]
        for c in firsts[:12]:
            hits = [i for i in later if c in per[i]]
            persist[c] = (round(len(hits) / len(later), 4) if later else None)
    return {
        "byPeriod": rows,
        "firstRepeatedSourceQuarter": LBL[first_rep] if first_rep is not None
                                      else None,
        "repeatedSourceRule": f"a canonical non-statutory identity observed in "
                              f"the court's voice beside this instrument in at "
                              f"least {REPEATED_SOURCE_JUDGMENTS} distinct "
                              f"judgments, cumulatively",
        "repeatedSources": sorted(c for c, js in cum.items()
                                  if len(js) >= REPEATED_SOURCE_JUDGMENTS),
        "persistenceAfterFormation": persist,
    }


def core_and_retrieval(S, inst, t0, scorable):
    """L7 operational core and L8 retrieval state, on one clock."""
    n = len(P)
    top100, top50 = [], []
    for i in range(n):
        c = S[P[i]]["courtStat"]
        t100 = {a for a in F.top(c, 100)}
        t50 = {a for a in F.top(c, 50)}
        top100.append(any(a[0] == inst for a in t100))
        top50.append(any(a[0] == inst for a in t50))
    first100 = next((i for i in range(n) if top100[i]), None)
    first50 = next((i for i in range(n) if top50[i]), None)
    # L8: freeze the court's top-50 article set at the last scorable quarter
    # BEFORE T0, then watch it age. Threshold inherited, not chosen here.
    idx = [i for i, l in enumerate(LBL) if l in scorable]
    pre = [i for i in idx if t0 is not None and i < t0]
    disp, stale = [], None
    if pre:
        frozen = Counter()
        for i in range(pre[-1] + 1):
            frozen.update(S[P[i]]["courtStat"])
        ft = set(F.top(frozen, 50))
        for i in [x for x in idx if x > pre[-1]]:
            tt = set(F.top(S[P[i]]["courtStat"], 50))
            pct = round(100 * len(ft - tt) / 50, 1)
            disp.append({"period": LBL[i], "top50DisplacedPct": pct,
                         "quartersAfterT0": i - t0})
            if stale is None and pct >= TOP50_DISPLACEMENT_PCT:
                stale = i
    return {
        "firstTop100Quarter": LBL[first100] if first100 is not None else None,
        "firstTop50Quarter": LBL[first50] if first50 is not None else None,
        "snapshotFrozenAt": LBL[pre[-1]] if pre else None,
        "displacement": disp,
        "firstMateriallyStaleQuarter": LBL[stale] if stale is not None else None,
        "evaluable": bool(pre),
        "notEvaluableWhy": (None if pre else
                            "no SCORABLE quarter precedes T=0, so no snapshot "
                            "can be frozen. The instrument has a pre-period in "
                            "the corpus; it is simply not mature enough to "
                            "freeze a top-50 set on."),
        "staleThresholdPct": TOP50_DISPLACEMENT_PCT,
        "thresholdProvenance": "inherited unchanged from the frozen "
                               "REPOSITORY_BET_001 refresh trigger. Not "
                               "chosen here and not tuned per event.",
    }


# ------------------------------------------------------------------ PHASE 6
def crossed(vals, idx, t0, rule, base=None):
    """First scorable index at or after T0 where a criterion is met."""
    for i in idx:
        if t0 is not None and i < t0:
            continue
        v = vals[i]
        if v is None:
            continue
        if rule == "FIRST_NONZERO" and v > 0:
            return i
        if rule == "SHIFT" and base is not None and abs(v - base) >= CONCENTRATION_SHIFT:
            return i
    return None


def layers(ev, s, fs_, cs, cr, idx, t0):
    """PHASE 6/7. When does each layer first cross its predefined criterion?

    The order below is a MEASUREMENT STACK, not a causal chain, and no layer
    is expected to precede another.
    """
    pre = [i for i in idx if t0 is not None and i < t0]
    base_hy = None
    if pre:
        vals = [s["hybridRate"][i] for i in pre if s["hybridRate"][i] is not None]
        base_hy = sum(vals) / len(vals) if vals else None
    f_new = [r["firstObservedAnywhereHere"] for r in fs_["byPeriod"]]
    f_any = [r["mentions"] for r in fs_["byPeriod"]]
    out = {
        "L2_BAR_STATUTORY_VISIBILITY": {
            "criterion": "FIRST_VISIBILITY: any party citation of the "
                         "instrument in a scorable quarter",
            "firstCrossed": None},
        "L3_COURT_STATUTORY_VISIBILITY": {
            "criterion": "FIRST_VISIBILITY: any court citation",
            "firstCrossed": None},
        "L4_AUTHORITY_ADJACENT_FORMULA": {
            "criterion": "any authority-adjacent recurring-formula mention "
                         "beside the instrument",
            "firstCrossed": None},
        "L5_AUTHORITY_ECOLOGY": {
            "criterion": f"hybrid rate departs from its pre-T0 mean by "
                         f"{CONCENTRATION_SHIFT} absolute, in a quarter with "
                         f"at least {MIN_COURT_CITES_FOR_LAYER} court "
                         f"judgments citing the instrument",
            "firstCrossed": None},
        "L6_DOCTRINAL_COMPANION": {
            "criterion": cs["repeatedSourceRule"],
            "firstCrossed": cs["firstRepeatedSourceQuarter"]},
        "L7_OPERATIONAL_CORE": {
            "criterion": "the instrument holds an article in the court's "
                         "top-50 cited articles for the quarter",
            "firstCrossed": cr["firstTop50Quarter"]},
        "L8_RETRIEVAL_STATE": {
            "criterion": f"a top-50 snapshot frozen at the last pre-event "
                         f"scorable quarter is displaced by "
                         f"{TOP50_DISPLACEMENT_PCT} per cent or more",
            "firstCrossed": cr["firstMateriallyStaleQuarter"]},
    }
    i2 = crossed(s["partyJ"], idx, t0, "FIRST_NONZERO")
    i3 = crossed(s["courtJ"], idx, t0, "FIRST_NONZERO")
    i4 = crossed(f_any, idx, t0, "FIRST_NONZERO")
    out["L2_BAR_STATUTORY_VISIBILITY"]["firstCrossed"] = (
        LBL[i2] if i2 is not None else None)
    out["L3_COURT_STATUTORY_VISIBILITY"]["firstCrossed"] = (
        LBL[i3] if i3 is not None else None)
    out["L4_AUTHORITY_ADJACENT_FORMULA"]["firstCrossed"] = (
        LBL[i4] if i4 is not None else None)
    i4n = crossed(f_new, idx, t0, "FIRST_NONZERO")
    out["L4_AUTHORITY_ADJACENT_FORMULA"]["firstNewlyObservedFormulaQuarter"] = (
        LBL[i4n] if i4n is not None else None)
    # A shift criterion needs a pre-event baseline, and a NEW instrument has
    # none: it did not exist to have an ecology. The criterion is therefore
    # stated in two parts, both fixed here and applied identically to every
    # event and pseudo-event. The FIRST_VISIBILITY part is what a new law can
    # satisfy; the SHIFT part is what an existing one can. Neither is tuned.
    i5 = crossed(s["hybridJ"], idx, t0, "FIRST_NONZERO")
    out["L5_AUTHORITY_ECOLOGY"]["criterion"] = (
        "FIRST_VISIBILITY: a judgment citing the instrument also carries a "
        "non-statutory authority in the court's voice. Where a pre-T0 "
        "baseline exists, a SHIFT sub-criterion is reported beside it.")
    out["L5_AUTHORITY_ECOLOGY"]["firstCrossed"] = (
        LBL[i5] if i5 is not None else None)
    if base_hy is not None:
        gate = [s["hybridRate"][i] if s["courtJ"][i] >= MIN_COURT_CITES_FOR_LAYER
                else None for i in range(len(P))]
        i5b = crossed(gate, idx, t0, "SHIFT", base_hy)
        out["L5_AUTHORITY_ECOLOGY"]["preT0HybridBaseline"] = round(base_hy, 4)
        out["L5_AUTHORITY_ECOLOGY"]["shiftCrossed"] = (
            LBL[i5b] if i5b is not None else None)
    else:
        out["L5_AUTHORITY_ECOLOGY"]["preT0HybridBaseline"] = None
        out["L5_AUTHORITY_ECOLOGY"]["shiftCrossed"] = None
        out["L5_AUTHORITY_ECOLOGY"]["shiftNotEvaluable"] = (
            "the instrument has no pre-T0 ecology to depart from. A new law "
            "cannot shift a baseline it never had, and reporting that as "
            "NO_DETECTED_SHIFT would be a category error.")
    if not cr.get("evaluable", True):
        out["L8_RETRIEVAL_STATE"]["note"] = cr["notEvaluableWhy"]
    for k, v in out.items():
        c = v["firstCrossed"]
        v["quartersAfterT0"] = (PKEY[(int(c[:4]), int(c[-1]))] - t0
                                if c and t0 is not None else None)
        v["status"] = ("MOVED" if c else
                       "NOT_EVALUABLE" if v.get("note") else
                       "NO_DETECTED_SHIFT")
        if v["quartersAfterT0"] is not None and v["quartersAfterT0"] > HORIZON:
            v["status"] = "MOVED_OUTSIDE_FROZEN_HORIZON"
    return out


# --------------------------------------------------------------- PHASE 14
def uptake_calibration(S, hz, scorable):
    """Pick a REPEATED/SUSTAINED rule from historical arrivals, then freeze it.

    The candidate rules are written down first and the winner is chosen on a
    property that does not involve any outcome: the rule that splits the
    arrivals most evenly is the one that carries information. Choosing the
    rule that best predicts top-50 entry would be choosing on the outcome, and
    is not done.
    """
    idx = [i for i, l in enumerate(LBL) if l in scorable]
    pres = defaultdict(lambda: [0] * len(P))
    for i, p in enumerate(P):
        for (inst, _art), n in S[p]["courtStat"].items():
            pres[inst][i] += n
    arrivals = _arrivals(pres, idx)
    cands = {
        "R1_twoDistinctScorableQuarters": lambda v: sum(
            1 for i in idx if v[i]) >= 2,
        "S1_threeConsecutiveScorableQuarters": lambda v: any(
            all(v[idx[k + t]] for t in range(3))
            for k in range(len(idx) - 2)),
        "S2_halfOfScorableQuartersSinceFirst": lambda v: _half(v, idx),
        "S3_fourDistinctScorableQuarters": lambda v: sum(
            1 for i in idx if v[i]) >= 4,
    }
    rates = {}
    for name, fn in sorted(cands.items()):
        hit = [a for a in arrivals if a in pres and fn(pres[a])]
        rates[name] = {"instruments": len(arrivals), "satisfied": len(hit),
                       "share": round(len(hit) / len(arrivals), 4)}
    sust = min((k for k in cands if k.startswith("S")),
               key=lambda k: (abs(rates[k]["share"] - 0.5), k))
    states = {}
    for a in sorted(set(arrivals)):
        v = pres.get(a, [0] * len(P))
        first = next((i for i in idx if v[i]), None)
        st = "FIRST_SEEN" if first is not None else "NOT_SEEN"
        if first is not None and cands["R1_twoDistinctScorableQuarters"](v):
            st = "REPEATED"
        if first is not None and cands[sust](v):
            st = "SUSTAINED"
        top100 = next((i for i in idx
                       if any(k[0] == a for k in F.top(S[P[i]]["courtStat"], 100))),
                      None)
        top50 = next((i for i in idx
                      if any(k[0] == a for k in F.top(S[P[i]]["courtStat"], 50))),
                     None)
        if top100 is not None:
            st = "TOP100"
        if top50 is not None:
            st = "TOP50"
        states[a] = {"firstSeen": LBL[first] if first is not None else None,
                     "state": st,
                     "top100": LBL[top100] if top100 is not None else None,
                     "top50": LBL[top50] if top50 is not None else None,
                     "quartersFirstToTop50": (top50 - first)
                     if (top50 is not None and first is not None) else None}
    return {
        "arrivalsConsidered": len(arrivals),
        "arrivalRule": "first court citation not in the first two quarters of "
                       "the corpus, so the arrival is inside the window and "
                       "not an artefact of when collection began",
        "candidateRules": rates,
        "chosenRepeatedRule": "R1_twoDistinctScorableQuarters",
        "chosenSustainedRule": sust,
        "selectionCriterion": "the sustained rule whose satisfied share is "
                              "closest to one half across historical "
                              "arrivals. No outcome enters the choice.",
        "frozen": True,
        "byInstrument": states,
        "stateLadder": ["FIRST_SEEN", "REPEATED", "SUSTAINED", "TOP100",
                        "TOP50"],
    }


def _arrivals(pres, idx):
    """Instruments whose first court citation is NOT in the first two quarters.

    The same left-censoring rule the new-law monitor states, applied to every
    instrument rather than to the twelve the monitor prints. An instrument
    already cited when the corpus opens did not arrive inside the window and
    its latency would be a fact about the collection.
    """
    out = []
    for inst, v in sorted(pres.items()):
        first = next((i for i in range(len(P)) if v[i]), None)
        if first is None or first < 2:
            continue
        if not any(v[i] for i in idx):
            continue
        out.append(inst)
    return out


def _half(v, idx):
    first = next((i for i in idx if v[i]), None)
    if first is None:
        return False
    after = [i for i in idx if i >= first]
    return sum(1 for i in after if v[i]) >= max(2, len(after) / 2)


# --------------------------------------------------------------- PHASE 12
def sfd_order(lay, cs):
    """STATUTE -> FORMULA -> DOCTRINE, or some other ordering, or none."""
    def q(k):
        c = lay[k]["firstCrossed"]
        return PKEY[(int(c[:4]), int(c[-1]))] if c else None
    s = q("L3_COURT_STATUTORY_VISIBILITY")
    f = q("L4_AUTHORITY_ADJACENT_FORMULA")
    d = q("L6_DOCTRINAL_COMPANION")
    if s is None:
        return {"class": "INSUFFICIENT", "why": "no court visibility"}
    if f is None and d is None:
        return {"class": "NO_FORMULA_NO_DOCTRINE"}
    if f is None:
        return {"class": "NO_FORMULA", "statuteToDoctrine": d - s}
    if d is None:
        return {"class": "NO_DOCTRINE", "statuteToFormula": f - s}
    if s == f == d:
        return {"class": "SIMULTANEOUS", "statuteToFormula": 0,
                "statuteToDoctrine": 0}
    order = sorted([("S", s), ("F", f), ("D", d)], key=lambda x: (x[1], x[0]))
    return {"class": "->".join(x[0] for x in order),
            "sequence": [f"{k}@{LBL[v]}" for k, v in order],
            "statuteToFormula": f - s, "statuteToDoctrine": d - s,
            "formulaToDoctrine": d - f,
            "note": "an ordering of first crossings. Not a mechanism."}


# --------------------------------------------------------------- PHASE 11
def doctrine_provenance(crows, inst, t0):
    """Were the sources that become companions already in the corpus?"""
    ever, before_any, before_here = set(), set(), set()
    for r in crows:
        if r["i"] is None:
            continue
        if t0 is not None and r["i"] < t0:
            before_any.add(r["cid"])
            if r["instW"] == inst:
                before_here.add(r["cid"])
        if r["instW"] == inst and (t0 is None or r["i"] >= t0):
            ever.add(r["cid"])
    cls = Counter()
    for c in ever:
        if c in before_here:
            cls["ALREADY_PRESENT_IN_DOMAIN"] += 1
        elif c in before_any:
            cls["ALREADY_PRESENT_SYSTEM_WIDE"] += 1
        else:
            cls["NEW_CODE_LOCAL_OR_GLOBALLY_NEW"] += 1
    return {
        "sourcesBesideInstrumentAfterT0": len(ever),
        "byProvenance": dict(sorted(cls.items())),
        "reading": "a companion drawn from sources already circulating "
                   "elsewhere is a different event from a source new to the "
                   "corpus, and the extractor's 28-identity vocabulary makes "
                   "the second class very hard to populate. Both counts are "
                   "floors.",
    }


# --------------------------------------------------------------- PHASE 19
def pseudo_events(rows, S, frows, crows, scorable, real_t0s):
    """NEGATIVE CONTROLS. Point the same battery at dates with no legal event.

    Three instruments already mature at the start of the window, and every
    scorable quarter that is not within one quarter of a real T=0.

    The first result is the important one and it is not flattering: for an
    instrument that is ALREADY visible, every FIRST_VISIBILITY criterion fires
    at the pseudo-T=0 by construction. The battery is therefore not a
    transition detector for a mature instrument; it is a visibility test. What
    distinguishes a real arrival is not WHETHER layers fire but the SHAPE of
    the latency vector: a mature instrument yields all zeros, and a staged
    vector -- some layers at 0, others two or three quarters later -- is what
    has to be shown not to arise by accident.

    So three rates are reported apart: the trivial first-visibility rate, the
    share of pseudo-events producing a STAGED vector, and the false-positive
    rate of the two criteria that genuinely can fire without an event, the
    ecology SHIFT and retrieval staleness.
    """
    idx = [i for i, l in enumerate(LBL) if l in scorable]
    mature = ["commercial_courts_law", "sharia_procedure_law",
              "commercial_courts_implementing_regulation"]
    banned = {t for t0 in real_t0s if t0 is not None
              for t in (t0 - 1, t0, t0 + 1)}
    out, fired, shift_fp = [], Counter(), Counter()
    for inst in mature:
        s = series(rows, S, inst)
        fs_ = formula_series(frows, inst, None)
        cs = companion_series(crows, inst, scorable)
        for t0 in idx:
            if t0 in banned or t0 == idx[0] or t0 >= idx[-2]:
                continue
            cr = core_and_retrieval(S, inst, t0, scorable)
            lay = layers(None, s, fs_, cs, cr, idx, t0)
            lats = {k: v["quartersAfterT0"] for k, v in lay.items()}
            for k, v in lay.items():
                if v["status"].startswith("MOVED"):
                    fired[k] += 1
            if lay["L5_AUTHORITY_ECOLOGY"].get("shiftCrossed"):
                shift_fp["L5_ECOLOGY_SHIFT"] += 1
            if cr.get("firstMateriallyStaleQuarter"):
                shift_fp["L8_RETRIEVAL_STALENESS"] += 1
            nz = [v for v in lats.values() if v is not None]
            out.append({
                "instrument": inst, "pseudoT0": LBL[t0],
                "latencies": lats,
                "allZero": bool(nz) and all(v == 0 for v in nz),
                "staged": any(v >= 2 for v in nz),
                "stagedExcludingRetrieval": any(
                    v >= 2 for k, v in lats.items()
                    if v is not None and k != "L8_RETRIEVAL_STATE"),
            })
    n = len(out)
    if not n:
        return {"pseudoEvents": 0, "verdict": "NO_ELIGIBLE_PSEUDO_EVENTS"}
    return {
        "pseudoEvents": n,
        "instruments": mature,
        "trivialFirstVisibilityRate": {
            k: round(v / n, 4) for k, v in sorted(fired.items())},
        "trivialityNote": "a rate of 1.0 for a FIRST_VISIBILITY layer is the "
                          "expected and correct result: the instrument was "
                          "already visible. It means the layer cannot be used "
                          "as a transition detector for a mature instrument, "
                          "which is stated rather than hidden.",
        "allZeroLatencyVectorShare": round(
            sum(1 for r in out if r["allZero"]) / n, 4),
        "stagedVectorShare": round(sum(1 for r in out if r["staged"]) / n, 4),
        "stagedVectorShareExcludingRetrieval": round(
            sum(1 for r in out if r["stagedExcludingRetrieval"]) / n, 4),
        "shiftCriteriaFalsePositives": {
            k: {"events": v, "rate": round(v / n, 4)}
            for k, v in sorted(shift_fp.items())},
        "meanLayersFiringPerPseudoEvent": round(
            sum(sum(1 for v in r["latencies"].values() if v is not None)
                for r in out) / n, 3),
        "verdict": ("BATTERY_DISCRIMINATES_ARRIVALS_ONLY"
                    if sum(1 for r in out if r["stagedExcludingRetrieval"]) / n
                    < 0.2 else "BATTERY_PRODUCES_STAGED_VECTORS_WITHOUT_EVENTS"),
        "howToReadIt": "the two real transitions are ARRIVALS and their "
                       "latency vectors are staged. If pseudo-events on "
                       "mature instruments almost never produce a staged "
                       "vector once retrieval staleness is set aside, then "
                       "the staging in the real events is not an artefact of "
                       "the criteria. If they do, it is.",
        "rows": out[:30],
    }


# ------------------------------------------------------------ PHASES 20-21
def signature(ev, clk, lay, fs_, cs, prov, sfd, health):
    """PHASE 20. One vector per event. No composite score, deliberately."""
    def lat(k):
        return lay[k]["quartersAfterT0"]
    return {
        "event_id": ev["event_id"],
        "event_type": ev["event_type"],
        "instrument": ev["instrument"],
        "known_at": clk["announcement"],
        "effective_at": clk["legalEffectiveAt"],
        "observable_from": clk["T0"],
        "clockQuality": clk["clockQuality"],
        "publicationHealthAtT0": health,
        "capture": "BACKFILLED_CALIBRATION",
        "captureNote": "the signal registry was created after the fact, so "
                       "every current event is backfilled by construction. "
                       "None of these may ever count as foresight.",
        "latencies": {
            "party_latency": lat("L2_BAR_STATUTORY_VISIBILITY"),
            "court_latency": lat("L3_COURT_STATUTORY_VISIBILITY"),
            "formula_latency": lat("L4_AUTHORITY_ADJACENT_FORMULA"),
            "ecology_latency": lat("L5_AUTHORITY_ECOLOGY"),
            "companion_latency": lat("L6_DOCTRINAL_COMPANION"),
            "core_latency": lat("L7_OPERATIONAL_CORE"),
            "retrieval_latency": lat("L8_RETRIEVAL_STATE"),
        },
        "layerStatus": {k: v["status"] for k, v in sorted(lay.items())},
        "formulaUptakeMix": fs_["uptakeMix"],
        "companionProvenance": prov["byProvenance"],
        "statuteFormulaDoctrineOrder": sfd.get("class"),
        "repeatedSources": cs["repeatedSources"],
        "evaluationHorizonQuarters": HORIZON,
    }


def ordering(sig):
    """PHASE 8. First, second, third moving layer, and what never moved."""
    lats = [(k, v) for k, v in sig["latencies"].items() if v is not None]
    lats.sort(key=lambda kv: (kv[1], kv[0]))
    groups = []
    for k, v in lats:
        if groups and groups[-1][0] == v:
            groups[-1][1].append(k)
        else:
            groups.append([v, [k]])
    return {
        "byQuartersAfterT0": [{"quartersAfterT0": g[0], "layers": sorted(g[1])}
                              for g in groups],
        "FIRST_MOVING_LAYER": sorted(groups[0][1]) if groups else None,
        "SECOND": sorted(groups[1][1]) if len(groups) > 1 else None,
        "THIRD": sorted(groups[2][1]) if len(groups) > 2 else None,
        "NO_DETECTED_SHIFT": sorted(k for k, v in sig["latencies"].items()
                                    if v is None),
        "caution": "simultaneity at quarter resolution is common and is shown "
                   "as a tie rather than broken by a rule. A tie is not an "
                   "ordering.",
    }


# --------------------------------------------------------------- PHASE 29-31
def early_indicator(S, hz, up, frows, crows, scorable):
    """Can an early layer predict a late one, across historical arrivals?

    The transition sample is two events, which forecasts nothing. So the test
    is run on the population it can be run on: the 60 in-window instrument
    arrivals, where the early features are read from the arrival quarter and
    the outcome is later operational salience. That is a weaker question than
    the transition one and it is labelled as such.
    """
    idx = [i for i, l in enumerate(LBL) if l in scorable]
    sidx = set(idx)
    pres = defaultdict(lambda: [0] * len(P))
    for i, p_ in enumerate(P):
        for (inst, _art), n in S[p_]["courtStat"].items():
            pres[inst][i] += n
    arrivals = _arrivals(pres, idx)
    fq = defaultdict(lambda: [0] * len(P))
    for r in frows:
        if r["instW"] and r["i"] in sidx:
            fq[r["instW"]][r["i"]] += 1
    cq = defaultdict(lambda: [set() for _ in range(len(P))])
    for r in crows:
        if r["instW"] and r["voice"] == "court" and r["i"] in sidx:
            cq[r["instW"]][r["i"]].add(r["cid"])
    units = []
    for a in arrivals:
        st = up["byInstrument"].get(a)
        if not st or not st["firstSeen"]:
            continue
        f0 = PKEY[(int(st["firstSeen"][:4]), int(st["firstSeen"][-1]))]
        after = [i for i in idx if i > f0]
        if len(after) < 2:
            continue
        cites0 = sum(n for (inst, _a), n in S[P[f0]]["courtStat"].items()
                     if inst == a)
        units.append({
            "instrument": a,
            "courtCitesAtArrival": cites0,
            "courtShareAtArrival": cites0 / max(
                1, sum(S[P[f0]]["courtStat"].values())),
            "formulaActivityAtArrival": fq[a][f0],
            "companionAtArrival": len(cq[a][f0]),
            "reachedTop50": st["top50"] is not None,
            "reachedTop100": st["top100"] is not None,
            "sustained": st["state"] in ("SUSTAINED", "TOP100", "TOP50"),
        })
    n = len(units)
    if n < 10:
        return {"units": n, "verdict": "INSUFFICIENT_SUPPORT"}

    def rule(feat, target, thr):
        g = [u for u in units if u[feat] >= thr]
        base = sum(1 for u in units if u[target]) / n
        p = sum(1 for u in g if u[target]) / len(g) if g else None
        return {"n": len(g), "precision": round(p, 4) if p is not None else None,
                "baseRate": round(base, 4),
                "lift": round(p / base, 4) if p and base else None}
    out = {}
    for target in ("reachedTop50", "reachedTop100", "sustained"):
        out[target] = {
            "COURT_SHARE_BASELINE": rule("courtCitesAtArrival", target, 3),
            "FORMULA_ACTIVITY": rule("formulaActivityAtArrival", target, 1),
            "COMPANION_AT_ARRIVAL": rule("companionAtArrival", target, 1),
        }
    # does formula activity add anything ABOVE the court-citation baseline?
    added = {}
    for target in ("reachedTop50", "sustained"):
        low = [u for u in units if u["courtCitesAtArrival"] < 3]
        base = (sum(1 for u in low if u[target]) / len(low)) if low else None
        g = [u for u in low if u["formulaActivityAtArrival"] >= 1]
        p = (sum(1 for u in g if u[target]) / len(g)) if g else None
        added[target] = {
            "stratum": "arrivals with fewer than 3 court citations at arrival",
            "n": len(low), "withFormulaActivity": len(g),
            "baseRateInStratum": round(base, 4) if base is not None else None,
            "precisionWithFormulaActivity": round(p, 4) if p is not None else None,
            "verdict": ("FORMULA_ADDS_NOTHING_ABOVE_COURT_CITATION"
                        if p is None or base is None or p <= base
                        else "FORMULA_ADDS_ABOVE_COURT_CITATION_LOW_SUPPORT"
                        if len(g) < 10 else "FORMULA_ADDS_ABOVE_COURT_CITATION")}
    return {
        "units": n,
        "unitIsAnArrivalNotATransition": "features are read at the arrival "
                                         "quarter and outcomes later. This is "
                                         "not the transition question and "
                                         "cannot be reported as one.",
        "rules": out,
        "formulaAboveBaseline": added,
        "phase30_formulaAsEarlyIndicator": {
            "verdict": ("FORMULA_ACTIVITY_IS_DESCRIPTIVE_ONLY"
                        if out["reachedTop50"]["FORMULA_ACTIVITY"]["lift"] is None
                        or out["reachedTop50"]["FORMULA_ACTIVITY"]["lift"]
                        < out["reachedTop50"]["COURT_SHARE_BASELINE"]["lift"]
                        else "FORMULA_ACTIVITY_BEATS_COURT_CITATION"),
            "comparison": "formula activity at arrival against the "
                          "court-citation baseline, same units, same target",
            "consequence": "the formula layer's greater historical mobility "
                           "buys no forecasting value here. It stays a "
                           "descriptive layer."},
        "phase31_companionAsEarlyIndicator": {
            "verdict": ("LOW_SUPPORT"
                        if out["reachedTop50"]["COMPANION_AT_ARRIVAL"]["n"] < 10
                        else "EVALUABLE"),
            "n": out["reachedTop50"]["COMPANION_AT_ARRIVAL"]["n"],
            "why": "a repeated companion almost never exists at the arrival "
                   "quarter -- the doctrinal layer takes two quarters to form "
                   "in both calibration transitions -- so there is nothing to "
                   "read at arrival. That is a fact about the layer, not a "
                   "failure of the test."},
        "temporalFolds": "NONE. Arrivals are spread across the window but the "
                         "outcome window differs by arrival, so this is a "
                         "single-sample ranking check.",
    }


# --------------------------------------------------------------- PHASE 28
def speed_bands(sigs):
    """Historical latency bands, so a future transition can be compared."""
    keys = ["party_latency", "court_latency", "formula_latency",
            "ecology_latency", "companion_latency", "core_latency",
            "retrieval_latency"]
    out = {}
    for k in keys:
        v = sorted(s["latencies"][k] for s in sigs
                   if s["latencies"][k] is not None)
        out[k] = {"events": len(v), "min": v[0] if v else None,
                  "max": v[-1] if v else None,
                  "band": f"{v[0]}-{v[-1]}Q" if v else None}
    return {
        "bands": out,
        "eventsContributing": len(sigs),
        "warning": "TWO events. A band read off two observations is a range, "
                   "not a distribution, and FASTER_THAN_BASELINE cannot be "
                   "said of a future transition until the library holds "
                   "enough events to have a baseline. The bands are recorded "
                   "so that a future session inherits them rather than "
                   "inventing them.",
    }


# --------------------------------------------------------------- PHASE 15-16
def article_anatomy(rows, S, inst, t0, scorable, named=()):
    """Per-article timelines, so a transition is not read as a mean.

    `named` are articles asked for by name. They are reported whether or not
    they turn out to be interesting, which is the point of naming them in
    advance.
    """
    idx = [i for i, l in enumerate(LBL) if l in scorable]
    per = defaultdict(lambda: {"court": [0] * len(P), "party": [0] * len(P),
                               "cj": [set() for _ in range(len(P))]})
    for r in rows:
        if r["t"] != "statute" or r.get("inst") != inst:
            continue
        a = r.get("art")
        if a is None:
            continue
        i = PKEY[r["p"]]
        if r["role"] == F.COURT:
            per[a]["court"][i] += 1
            per[a]["cj"][i].add(r["j"])
        elif r["role"] == F.PARTY:
            per[a]["party"][i] += 1
    tot = {a: sum(d["court"]) for a, d in per.items()}
    pick = sorted(tot, key=lambda a: (-tot[a], a))[:8]
    for a in named:
        if a in per and a not in pick:
            pick.append(a)
    out = []
    for a in pick:
        d = per[a]
        fc = next((i for i in idx if d["court"][i]), None)
        fp = next((i for i in idx if d["party"][i]), None)
        t50 = next((i for i in idx
                    if (inst, a) in set(F.top(S[P[i]]["courtStat"], 50))), None)
        out.append({
            "article": a, "courtCitations": tot[a],
            "requestedByName": a in named,
            "firstCourtQuarter": LBL[fc] if fc is not None else None,
            "firstPartyQuarter": LBL[fp] if fp is not None else None,
            "quartersAfterT0": (fc - t0) if (fc is not None and t0 is not None)
                               else None,
            "firstTop50Quarter": LBL[t50] if t50 is not None else None,
            "quartersFirstToTop50": (t50 - fc) if (t50 is not None
                                                  and fc is not None) else None,
        })
    out.sort(key=lambda r: (-r["courtCitations"], r["article"]))
    return {"articlesReported": len(out), "namedInAdvance": sorted(named),
            "rows": out,
            "note": "an article entering the corpus is an observation about "
                    "citation, not about the provision's importance."}


# --------------------------------------------------------------- PHASE 13
def voice_order(s, idx, t0, up_rule):
    """FIRST MENTION is not SUSTAINED VISIBILITY. Both, separately."""
    def first(v):
        return next((i for i in idx if v[i]), None)

    def sustained(v):
        run = 0
        for i in idx:
            run = run + 1 if v[i] else 0
            if run >= 3:
                return i
        return None
    fc, fp = first(s["courtJ"]), first(s["partyJ"])
    sc, sp = sustained(s["courtJ"]), sustained(s["partyJ"])
    return {
        "firstMention": {"court": LBL[fc] if fc is not None else None,
                         "party": LBL[fp] if fp is not None else None,
                         "leader": ("COURT" if fc is not None and
                                    (fp is None or fc < fp) else
                                    "PARTY" if fp is not None and
                                    (fc is None or fp < fc) else
                                    "SAME_QUARTER" if fc is not None else None)},
        "sustainedVisibility": {
            "rule": "court or party presence in three consecutive scorable "
                    "quarters",
            "court": LBL[sc] if sc is not None else None,
            "party": LBL[sp] if sp is not None else None,
            "leader": ("COURT" if sc is not None and (sp is None or sc < sp)
                       else "PARTY" if sp is not None and
                       (sc is None or sp < sc) else
                       "SAME_QUARTER" if sc is not None else None)},
        "firstMentionMinusT0": {
            "court": (fc - t0) if (fc is not None and t0 is not None) else None,
            "party": (fp - t0) if (fp is not None and t0 is not None) else None},
        "caution": "a same-quarter first mention is a tie at quarter "
                   "resolution, not simultaneity in the courtroom.",
    }


# ------------------------------------------------------------ PHASES 32-33
def retrieval_sequence(anat, pseudo):
    """Does retrieval fail before or after the transition shows in rankings?"""
    rows = []
    for eid, a in sorted(anat.items()):
        lat = {k: v["quartersAfterT0"] for k, v in a["layers"].items()}
        rows.append({
            "event_id": eid,
            "retrieval": lat["L8_RETRIEVAL_STATE"],
            "core": lat["L7_OPERATIONAL_CORE"],
            "formula": lat["L4_AUTHORITY_ADJACENT_FORMULA"],
            "companion": lat["L6_DOCTRINAL_COMPANION"],
            "evaluable": a["coreAndRetrieval"].get("evaluable"),
            "retrievalBeforeCore": (
                None if lat["L8_RETRIEVAL_STATE"] is None
                or lat["L7_OPERATIONAL_CORE"] is None
                else lat["L8_RETRIEVAL_STATE"] < lat["L7_OPERATIONAL_CORE"]),
        })
    usable = [r for r in rows if r["retrieval"] is not None]
    fp = pseudo["shiftCriteriaFalsePositives"].get(
        "L8_RETRIEVAL_STALENESS", {}).get("rate")
    return {
        "byEvent": rows,
        "eventsWithAnEvaluableSnapshot": len(usable),
        "phase33_earlyRefreshWarning": {
            "candidate": "use formula or companion movement as an earlier "
                         "refresh trigger than TOP50_DISPLACEMENT",
            "decision": "HOLD",
            "why": [
                f"only {len(usable)} event has an evaluable pre-event "
                "snapshot, so there is nothing to backtest against",
                f"retrieval staleness fires in {fp} of pseudo-events with no "
                "legal event at all, so it is a clock, not an event signal, "
                "and an 'earlier' trigger would be earlier than nothing",
                "the existing TOP50_DISPLACEMENT trigger is frozen in "
                "REPOSITORY_BET_001 and is not replaced without a backtest "
                "that beats it"],
            "retainedTrigger": "TOP50_DISPLACEMENT",
        },
        "readingForLegalAIMaintenance": "a frozen retrieval snapshot ages "
                                        "past the 30 per cent displacement "
                                        "mark whether or not a law changes. "
                                        "Refresh policy should be driven by "
                                        "elapsed quarters, and a legal "
                                        "transition is a reason to refresh "
                                        "sooner rather than the reason to "
                                        "refresh at all.",
    }


# --------------------------------------------------------------- PHASE 17
def compare_events(anat, sigs):
    """CTL against Evidence, on timing rather than on snapshots."""
    if len(sigs) < 2:
        return {"verdict": "ONE_EVENT_NO_COMPARISON"}
    keys = ["party_latency", "court_latency", "formula_latency",
            "ecology_latency", "companion_latency", "core_latency",
            "retrieval_latency"]
    tab = {k: {s["event_id"]: s["latencies"][k] for s in sigs} for k in keys}
    same, diff = [], []
    for k, v in tab.items():
        vals = [x for x in v.values() if x is not None]
        (same if len(set(vals)) <= 1 and len(vals) == len(sigs) else diff).append(k)
    return {
        "latencyTable": tab,
        "layersAgreeing": sorted(same),
        "layersDiffering": sorted(diff),
        "companionTypeByEvent": {s["event_id"]: s["repeatedSources"]
                                 for s in sigs},
        "companionCharacterByEvent": {
            s["event_id"]: {
                "repeatedSources": len(s["repeatedSources"]),
                "namedFiqhIdentities": sum(
                    1 for c in s["repeatedSources"]
                    if c.startswith(("B.", "J."))),
                "genericIdentities": sum(
                    1 for c in s["repeatedSources"]
                    if c.startswith("GENERIC.")),
                "namedShare": round(
                    sum(1 for c in s["repeatedSources"]
                        if c.startswith(("B.", "J."))) /
                    len(s["repeatedSources"]), 4)
                if s["repeatedSources"] else None}
            for s in sigs},
        "companionCharacterReading": "the two transitions share their TIMING "
                                     "and differ in their CONTENT. Both form "
                                     "a repeated companion two quarters after "
                                     "the law becomes visible; what forms is "
                                     "not the same kind of authority. That is "
                                     "a transition signature difference "
                                     "worth more than either latency.",
        "formulaUptakeMixByEvent": {s["event_id"]: s["formulaUptakeMix"]
                                    for s in sigs},
        "companionProvenanceByEvent": {s["event_id"]: s["companionProvenance"]
                                       for s in sigs},
        "sharedOrdering": ("STATUTE_AND_ECOLOGY_AT_T0_THEN_COMPANION_THEN_FORMULA"
                           if all(tab["court_latency"][e] == 0 for e in tab["court_latency"])
                           and all(tab["ecology_latency"][e] == 0
                                   for e in tab["ecology_latency"])
                           else "NO_SHARED_ORDERING"),
        "caution": "two events. A shared ordering across two observations is "
                   "a coincidence until a third agrees with it, and is "
                   "reported as a description rather than as a signature.",
    }


# ------------------------------------------------------------ PHASES 22-27
def reference_and_ai(sigs, pseudo, bands):
    """Reference signatures, AI channel hypotheses, and their falsifiers."""
    ref = {
        "NEW_CODE": {
            "eventsSupporting": [s["event_id"] for s in sigs],
            "n": len(sigs),
            "status": "PROVISIONAL_TWO_EVENTS",
            "layerOrderObserved": None,
        },
        "MAJOR_AMENDMENT": {"n": 0, "status": "NO_QUALIFYING_EVENT",
                            "why": "no amendment in the window carries an "
                                   "article-version mapping or a verifiable "
                                   "commencement date"},
        "PUBLICATION_SHIFT": {"n": 0, "status": "NOT_CONSTRUCTED",
                              "why": "publication health is layer zero and "
                                     "vetoes analysis rather than forming a "
                                     "signature of its own"},
        "DOCKET_SHIFT": {"n": 0, "status": "NOT_CONSTRUCTED"},
        "NO_EVENT": {"n": pseudo["pseudoEvents"],
                     "status": "CONSTRUCTED_FROM_PSEUDO_EVENTS",
                     "meanLayersFiring": pseudo["meanLayersFiringPerPseudoEvent"],
                     "allZeroLatencyVectorShare":
                         pseudo["allZeroLatencyVectorShare"],
                     "stagedVectorShareExcludingRetrieval":
                         pseudo["stagedVectorShareExcludingRetrieval"],
                     "shiftCriteriaFalsePositives":
                         pseudo["shiftCriteriaFalsePositives"],
                     "verdict": pseudo["verdict"]},
    }
    ai = {
        "JUDICIAL_RESEARCH_AI": {
            "expected_first_layer": ["L5_AUTHORITY_ECOLOGY",
                                     "L6_DOCTRINAL_COMPANION"],
            "expected_secondary_layers": ["L4_AUTHORITY_ADJACENT_FORMULA",
                                          "L7_OPERATIONAL_CORE"],
            "expectedSignals": ["source diversity", "traceability",
                                "long-tail authority",
                                "companion concentration"],
            "falsifier": "a verified judicial-research AI deployment becomes "
                         "corpus-linkable, the evaluation horizon passes, and "
                         "the only layer outside its frozen bounds is "
                         "statutory ranking. SOURCE_FIRST then loses.",
            "minimumObservableHorizonQuarters": HORIZON,
        },
        "JUDICIAL_DRAFTING_AI": {
            "expected_first_layer": ["L4_AUTHORITY_ADJACENT_FORMULA"],
            "expected_secondary_layers": ["L5_AUTHORITY_ECOLOGY"],
            "expectedSignals": ["formula concentration", "variant "
                                "distribution", "innovation rate"],
            "falsifier": "a verified judicial drafting-AI deployment becomes "
                         "corpus-linkable and the authority-adjacent formula "
                         "layer stays inside its frozen bounds while source "
                         "diversity moves first. FORMULA_FIRST then loses.",
            "minimumObservableHorizonQuarters": HORIZON,
        },
        "BAR_RESEARCH_AI": {
            "expected_first_layer": ["L2_BAR_STATUTORY_VISIBILITY"],
            "expected_secondary_layers": ["L3_COURT_STATUTORY_VISIBILITY"],
            "expectedSignals": ["party article and source use before court "
                                "visibility"],
            "falsifier": "a verified bar-side deployment becomes linkable and "
                         "party-side use stays inside its bounds while the "
                         "court's moves. BAR_FIRST then loses. The statutory "
                         "first-mover result already finds the bar does not "
                         "lead, so this hypothesis starts behind.",
            "minimumObservableHorizonQuarters": HORIZON,
        },
        "COURT_ADMIN_AI": {
            "expected_first_layer": ["L0_OBSERVATION_SYSTEM"],
            "expected_secondary_layers": [],
            "expectedSignals": ["publication volume, composition and reasons "
                                "length"],
            "falsifier": "none needed: this channel predicts NO doctrinal "
                         "shift by default, and a doctrinal shift following "
                         "it is evidence against the default rather than for "
                         "the channel.",
            "minimumObservableHorizonQuarters": HORIZON,
        },
    }
    return {
        "phase22_referenceSignatures": ref,
        "phase23_aiChannelHypotheses": ai,
        "phase24_falsifiersFrozen": True,
        "phase25_identificationRule": {
            "rule": "A TRANSITION SIGNATURE NEVER IDENTIFIES AI.",
            "permitted": ["CONSISTENT_WITH a pre-registered channel "
                          "hypothesis", "INCONSISTENT_WITH it"],
            "forbidden": ["AI_DETECTED_FROM_TEXT",
                          "a formula-first transition means AI",
                          "a source-diversity shift means AI"],
            "necessaryCondition": "an externally verified adoption event that "
                                  "reaches the workflow this corpus observes. "
                                  "The registry currently holds none at "
                                  "L3_WORKFLOW_MATCH.",
        },
        "phase26_signalWithoutEvent": {
            "rule": "a layer detector firing with no known event opens a "
                    "SURPRISE_LEDGER entry and a registry search. If nothing "
                    "is found the class is UNKNOWN_TRANSITION and stays "
                    "there. Resemblance to an AI expectation is not "
                    "evidence.",
            "ledger": "SURPRISE_LEDGER.json",
        },
        "phase27_eventWithoutSignal": {
            "rule": "a verified deployment inside the horizon with no "
                    "expected layer moving is recorded as "
                    "NO_OBSERVABLE_SHIFT_WITHIN_HORIZON, which is a result.",
            "horizonQuarters": HORIZON,
            "horizonFrozenNow": True,
            "forbidden": "extending the horizon until something moves",
        },
        "phase28_speedBands": bands,
    }


def prospective_schema():
    """PHASE 35. The forecast ledger's shape, for multi-layer transitions."""
    return {
        "what": "schema for a transition registered BEFORE its outcome is "
                "observable. Nothing currently qualifies: every event in the "
                "registry is backfilled.",
        "fields": ["transition_id", "event_id", "recorded_at", "known_at",
                   "effective_at", "observable_from", "expected_layers",
                   "falsifiers", "evaluation_horizon", "publication_gate",
                   "layer_detectors", "status"],
        "statuses": {
            "ARMED": "registered, T=0 not yet reached",
            "OBSERVING": "inside the evaluation horizon",
            "MATURE": "horizon complete, not yet scored",
            "SCORED": "layers compared against expectation and falsifier",
            "VOID_DATA_SHIFT": "publication health failed inside the window, "
                               "so the observation system moved and the "
                               "transition cannot be read",
        },
        "creditRule": "a transition recorded after its observable_from is "
                      "BACKFILLED_CALIBRATION and may never be reported as "
                      "foresight. The class is computed from recorded_at "
                      "against observable_from, never declared.",
        "instances": [],
        "instancesNote": "empty by construction. The first prospective "
                         "instance requires an event whose observable_from "
                         "lies in the future at the moment of recording.",
    }


# --------------------------------------------------------------- PHASES 1,36
def three_layer_input():
    """PHASE 1. The three existing layer baselines, quoted, not recomputed."""
    d = J("diffusion_results.json")
    fz = J("frozen/formula_baseline.json")
    ld, hz = J("leading_results.json"), J("horizon_results.json")
    dfz = J("frozen/doctrinal_diffusion_era_1.json")
    afm = J("frozen/article_first_mover_era_1.json")
    sv = d["phase21_statuteVsDoctrine"]
    return {
        "source": "quoted from existing frozen results. NOTHING is "
                  "recomputed here and no metric is combined into a score.",
        "STATUTORY_LAYER": {
            "rankAutocorrelation": sv["articles"]["rankAutocorrelation"],
            "topDecilePersistence": sv["articles"]["topDecilePersistence"],
            "bottomHalfMobility": sv["articles"]["bottomHalfMobility"],
            "firstMoverTypology": afm["firstMoverTypology"],
            "newEntrantBehaviour": {
                "instrumentsArrivingInWindow":
                    hz["phase6_newLawMonitor"]["instrumentsArrivingInWindow"],
                "reachedTop50": hz["phase6_newLawMonitor"]["reachedTop50"],
                "medianQuartersToTop50":
                    hz["phase6_newLawMonitor"]["medianQuartersToTop50"]},
            "limitations": ["universe about 2,000 cited articles",
                            "left-censored instruments excluded"],
        },
        "DOCTRINAL_LAYER": {
            "rankAutocorrelation": sv["doctrinalSources"]["rankAutocorrelation"],
            "topQuartilePersistence":
                sv["doctrinalSources"]["topQuartilePersistence"],
            "bottomHalfMobility": sv["doctrinalSources"]["bottomHalfMobility"],
            "survivalByFirstMover": dfz["survivalCodeLocal"],
            "companionFormationLatency":
                dfz["articleSourceOrder"]["companionFormationLatency"],
            "sourceDiffusion": d["phase13_14_18_19_milestones"]["byKind"],
            "limitations": ["28 canonical identities; every count is a floor",
                            "six or seven matched pairs in every arm"],
        },
        "FORMULA_LAYER": {
            "unitName": "AUTHORITY-ADJACENT RECURRING FORMULA",
            "mobilityCirculatingOnly": fz["mobility"]["formulaCirculatingOnly"],
            "mobilityAllFormulas": fz["mobility"]["formulaAll"],
            "concentration": fz["concentration"],
            "detectorBaselines": {
                k: v["baselineLastValue"]
                for k, v in sorted(fz["detectorEra"]["metrics"].items())},
            "limitations": ["exact-fingerprint resolution only; near-family "
                            "equivalence unresolved",
                            "an exact normalised +-90 character window around "
                            "an authority mention, not a representation of a "
                            "judgment's language"],
        },
        "noCompositeScore": "the three layers are kept apart. A single "
                            "mobility index over universes of 34, 2,000 and "
                            "15,000 objects would be a number with no "
                            "referent.",
    }


def bet(sigs, order_by_event, pseudo, early):
    """PHASE 36. Issue only if the calibration is strong enough. It is not."""
    firsts = {e: o["FIRST_MOVING_LAYER"] for e, o in order_by_event.items()}
    agree = len({tuple(v or []) for v in firsts.values()}) == 1
    return {
        "id": "TRANSITION_BET_001",
        "candidateShape": "for the next prospectively captured major law, "
                          "statutory visibility will precede stable "
                          "doctrinal-companion formation",
        "decision": "REFUSED",
        "why": [
            f"the calibration sample is {len(sigs)} events, both backfilled",
            "the two events do not share a first-moving layer set"
            if not agree else
            "the two events share a first-moving layer set, which is one "
            "coincidence rather than a calibration",
            "the negative control produces a staged latency vector in "
            f"{pseudo['stagedVectorShareExcludingRetrieval']} of "
            f"{pseudo['pseudoEvents']} pseudo-events once retrieval staleness "
            "is set aside, and retrieval staleness itself fires in "
            f"{pseudo['shiftCriteriaFalsePositives'].get('L8_RETRIEVAL_STALENESS', {}).get('rate')} "
            "of them with no event at all",
            "no early layer predicts a late one above the court-citation "
            "baseline: " + json.dumps(
                {k: v["verdict"] for k, v in early.get(
                    "formulaAboveBaseline", {}).items()}, ensure_ascii=False)
            if "formulaAboveBaseline" in early else "early-indicator test "
            "had insufficient support",
        ],
        "whatWouldEarnIt": "four or more calibration transitions with known "
                          "legal clocks sharing an ordering, and a negative "
                          "control that does not reproduce it.",
        "firstMovingLayerByEvent": firsts,
        "keptBecauseRefused": "recorded so a later session does not re-derive "
                              "the same attractive ordering from the same two "
                              "events.",
    }


def formula_first_test(anat):
    """PHASE 9. The hypothesis, tested rather than assumed.

    Does the authority-adjacent formula layer move BEFORE statutory
    visibility, with it, after it, or not at all? NEW formulas and formulas
    carried from an older legal context are counted apart, because a formula
    cannot appear around an authority beside a law that does not yet exist
    unless it is already circulating elsewhere.
    """
    rows = []
    for eid, a in sorted(anat.items()):
        lay = a["layers"]
        f = lay["L4_AUTHORITY_ADJACENT_FORMULA"]["quartersAfterT0"]
        c = lay["L3_COURT_STATUTORY_VISIBILITY"]["quartersAfterT0"]
        mix = a["formula"]["uptakeMix"]
        rel = ("NOT_AT_ALL" if f is None else
               "BEFORE" if c is not None and f < c else
               "SAME_PERIOD" if c is not None and f == c else "AFTER")
        rows.append({
            "event_id": eid, "instrument": a["instrument"],
            "formulaLatency": f, "courtStatutoryLatency": c,
            "relation": rel,
            "newlyObservedFormulas": mix["A_newlyObservedFormulas"],
            "carriedFromOlderLaw": mix["B_carriedFromOlderLaw"],
            "carriedNeverSeenBesideAnother":
                mix["C_carriedButNeverSeenBesideAnotherInstrument"],
            "leftTruncationWarning": a["formula"].get("leftTruncationWarning"),
        })
    rels = {r["relation"] for r in rows}
    return {
        "byEvent": rows,
        "verdict": ("FORMULA_LAYER_MOVES_AFTER_STATUTORY_VISIBILITY"
                    if rels == {"AFTER"} else
                    "FORMULA_LAYER_MOVES_FIRST" if rels == {"BEFORE"} else
                    "MIXED"),
        "consequence": "the withdrawn claim -- that the wording layer would "
                       "move first -- is not supported by either ordinary "
                       "transition available. Greater historical MOBILITY of "
                       "the formula layer does not make it the EARLIER layer "
                       "around an actual legal change. The prospective form "
                       "of the claim remains a hypothesis and is now a "
                       "hypothesis with evidence against its ordinary-"
                       "transition analogue.",
        "whatThisDoesNotShow": "nothing here is about AI. An AI-driven "
                               "transition need not resemble a new-law "
                               "transition, and PHASE 39's question is "
                               "precisely whether it does.",
    }


def matrix_v2():
    """PHASE 34. The AI observability matrix, extended with layer expectations.

    Every verified adoption event gets an expected first layer, its
    secondaries, its falsifier and a minimum horizon. Most remain untestable,
    which is recorded rather than worked around.
    """
    xm = J("ai_exposure_matrix_results.json")
    reg = J("adoption_registry.json")
    CH = {
        "BENCH_JUDICIAL_RESEARCH": "JUDICIAL_RESEARCH_AI",
        "BENCH_DRAFTING": "JUDICIAL_DRAFTING_AI",
        "BAR_RESEARCH": "BAR_RESEARCH_AI",
        "BAR_DRAFTING": "BAR_RESEARCH_AI",
        "COURT_ADMINISTRATION": "COURT_ADMIN_AI",
        "COURT_ADMIN": "COURT_ADMIN_AI",
    }
    EXPECT = {
        "JUDICIAL_RESEARCH_AI": (["L5_AUTHORITY_ECOLOGY",
                                  "L6_DOCTRINAL_COMPANION"],
                                 ["L4_AUTHORITY_ADJACENT_FORMULA",
                                  "L7_OPERATIONAL_CORE"]),
        "JUDICIAL_DRAFTING_AI": (["L4_AUTHORITY_ADJACENT_FORMULA"],
                                 ["L5_AUTHORITY_ECOLOGY"]),
        "BAR_RESEARCH_AI": (["L2_BAR_STATUTORY_VISIBILITY"],
                            ["L3_COURT_STATUTORY_VISIBILITY"]),
        "COURT_ADMIN_AI": (["L0_OBSERVATION_SYSTEM"], []),
    }
    events = reg.get("events", [])
    rows = []
    for e in events:
        link = str(e.get("corpus_linkability", ""))
        ch = CH.get(str(e.get("actor_channel", "")).upper(), "UNCLASSIFIED")
        exp, sec = EXPECT.get(ch, (None, None))
        rows.append({
            "event_id": e.get("event_id"),
            "organization": e.get("organization"),
            "actor_channel": e.get("actor_channel"),
            "deployment_status": e.get("deployment_status"),
            "corpus_linkability": link,
            "channelHypothesis": ch,
            "expected_first_layer": exp,
            "expected_secondary_layers": sec,
            "falsifier": (None if ch == "UNCLASSIFIED" else
                          "see phase23_aiChannelHypotheses."
                          f"{ch}.falsifier"),
            "minimumObservableHorizonQuarters": HORIZON,
            "referenceTransitionSignature": "NEW_CODE (provisional, two "
                                            "events)",
            "testable": link.startswith("L3") or link.startswith("L4"),
            "whyNotTestable": (None if link.startswith(("L3", "L4")) else
                               f"linkability {link}: the deployment does not "
                               "reach the adjudicatory workflow this corpus "
                               "observes"),
        })
    testable = [r for r in rows if r["testable"]]
    return {
        "extends": "ai_exposure_matrix_results.json",
        "addedColumns": ["expected_first_layer", "expected_secondary_layers",
                         "falsifier", "minimum_observable_horizon",
                         "linkability", "reference_transition_signature"],
        "events": rows,
        "eventsTestableToday": len(testable),
        "why": ("no event reaches a workflow this corpus observes, so no AI "
                "channel hypothesis can be scored yet. The matrix records "
                "what each event WOULD be tested against when it becomes "
                "linkable."
                if not testable else
                "at least one event is linkable; see the rows"),
        "existingSummary": {k: v for k, v in xm.items()
                            if k in ("what", "verdict", "linkabilityLadder")},
    }


def paper_b(anat):
    """PHASE 38. Does this change how the code-associated environment reads?"""
    ev = anat.get("LSIG-0002", {})
    lay = ev.get("layers", {})
    eco = lay.get("L5_AUTHORITY_ECOLOGY", {})
    comp = lay.get("L6_DOCTRINAL_COMPANION", {})
    fast = eco.get("quartersAfterT0") == 0
    return {
        "question": "does the Law of Evidence's non-statutory environment "
                    "appear immediately, or form after statutory uptake?",
        "ecologyLatencyQuarters": eco.get("quartersAfterT0"),
        "repeatedCompanionLatencyQuarters": comp.get("quartersAfterT0"),
        "reading": (
            "the environment is present in the SAME quarter the law becomes "
            "visible: the first judgments citing it already carry "
            "non-statutory authority. A REPEATED companion, which is the "
            "stronger object, takes two further quarters. So the environment "
            "is not built up over time from article-local patterns, but "
            "neither is a stable companion instantaneous."
            if fast else
            "the environment forms after statutory uptake, and the paper "
            "must describe a formation process rather than an association."),
        "implicationForClaimEcologies": (
            "CONSISTENT_WITH_CODE_ASSOCIATED_ENVIRONMENT, with one "
            "qualification the paper should carry: immediate presence is "
            "measured on TWO transitions, and the companion object it relies "
            "on takes two quarters to form in both."
            if fast else "REQUIRES_A_FORMATION_ACCOUNT"),
        "documentUpdated": False,
        "whyNotUpdated": "the finding qualifies the existing claim rather "
                         "than contradicting it, and CLAIM_ECOLOGIES.md is "
                         "not rewritten for a qualification that two events "
                         "support. The qualification is recorded here and in "
                         "TRANSITIONS.md.",
    }


def main():
    hz = J("horizon_results.json")
    scorable = set(hz["phase3_maturityRule"]["scorable"])
    rows, _dates, _x = F.load()
    S = F.build(rows)
    frows, _schema = FA.load()
    crows = D.load_rows()
    idx = [i for i, l in enumerate(LBL) if l in scorable]

    health = publication_health()
    cand = candidates(hz)
    up = uptake_calibration(S, hz, scorable)

    events, sigs, anat, orders = [], [], {}, {}
    for row in cand["registrySignals"]:
        if row["class"] != "CALIBRATION_EVENT":
            continue
        clk = clock(row)
        inst, t0 = row["instrument"], clk["T0Index"]
        s = series(rows, S, inst)
        fs_ = formula_series(frows, inst, t0)
        cs = companion_series(crows, inst, scorable)
        cr = core_and_retrieval(S, inst, t0, scorable)
        lay = layers(row, s, fs_, cs, cr, idx, t0)
        sfd = sfd_order(lay, cs)
        prov = doctrine_provenance(crows, inst, t0)
        hflags = health.get("_flags", {})
        window = [LBL[i] for i in range(max(0, (t0 or 0) - 4),
                                        min(len(LBL), (t0 or 0) + HORIZON + 1))]
        hstat = {q: hflags.get(q, []) for q in window if hflags.get(q)}
        sev = [len(v) for v in hstat.values()]
        sig = signature(row, clk, lay, fs_, cs, prov, sfd, {
            "unstableQuartersInWindow": sorted(hstat),
            "compositionFlagsInWindow": sum(sev),
            "meanFlagsPerQuarterInWindow": round(sum(sev) / len(sev), 2)
            if sev else None,
            "gate": "STANDING_CAVEAT",
            "gateNote": "the publication-health rule fires on every "
                        "quarter-to-quarter step in this corpus, so it is a "
                        "caveat on every latency here rather than a veto on "
                        "any one event. The flag count is comparable BETWEEN "
                        "events and is reported for that purpose: a lower "
                        "mean means a calmer observation regime, not a "
                        "cleaner transition."})
        o = ordering(sig)
        events.append(row)
        sigs.append(sig)
        orders[row["event_id"]] = o
        anat[row["event_id"]] = {
            "instrument": inst,
            "clock": clk,
            "publicationHealthInWindow": sig["publicationHealthAtT0"],
            "layers": lay,
            "ordering": o,
            "byQuarter": {
                "courtJudgments": {LBL[i]: s["courtJ"][i] for i in range(len(P))
                                   if s["courtJ"][i]},
                "partyJudgments": {LBL[i]: s["partyJ"][i] for i in range(len(P))
                                   if s["partyJ"][i]},
                "courtShare": {LBL[i]: round(s["courtShare"][i], 5)
                               for i in range(len(P)) if s["courtShare"][i]},
                "courtRank": {LBL[i]: s["courtRank"][i] for i in range(len(P))
                              if s["courtRank"][i]},
                "hybridRate": {LBL[i]: round(s["hybridRate"][i], 4)
                               for i in range(len(P))
                               if s["hybridRate"][i] is not None},
                "namedFiqhRate": {LBL[i]: round(s["namedFiqhRate"][i], 4)
                                  for i in range(len(P))
                                  if s["namedFiqhRate"][i] is not None},
                "traceability": {LBL[i]: round(s["traceability"][i], 4)
                                 for i in range(len(P))
                                 if s["traceability"][i] is not None},
            },
            "articlesByQuarter": {LBL[i]: s["articles"][i]
                                  for i in range(len(P)) if s["articles"][i]},
            "formula": fs_,
            "companion": cs,
            "companionProvenance": prov,
            "coreAndRetrieval": cr,
            "statuteFormulaDoctrine": sfd,
            "uptakeState": up["byInstrument"].get(inst),
            "voiceOrder": voice_order(s, idx, t0, up["chosenSustainedRule"]),
            "articles": article_anatomy(
                rows, S, inst, t0, scorable,
                named=NAMED_ARTICLES.get(inst, ())),
        }

    real_t0s = [PKEY[(int(s["observable_from"][:4]),
                      int(s["observable_from"][-1]))]
                for s in sigs if s["observable_from"]]
    pseudo = pseudo_events(rows, S, frows, crows, scorable, real_t0s)
    early = early_indicator(S, hz, up, frows, crows, scorable)
    bands = speed_bands(sigs)
    refai = reference_and_ai(sigs, pseudo, bands)
    cmp_ = compare_events(anat, sigs)
    rseq = retrieval_sequence(anat, pseudo)
    b = bet(sigs, orders, pseudo, early)

    res = {
        "what": "MULTI-LAYER LEGAL TRANSITION SEQUENCING OBSERVATORY. When a "
                "real legal transition occurs, which observable layer moves "
                "first, which second, and which does not move at all.",
        "scopeCorrections": {
            "1_terminology": "AUTHORITY-ADJACENT RECURRING FORMULA is the "
                             "unit's name wherever precision matters: an "
                             "exact normalised +-90 character window around "
                             "an authority mention, not a representation of a "
                             "judgment's language.",
            "2_prospectiveClaimWithdrawn": {
                "withdrawn": "if AI changes Saudi legal reasoning, the "
                             "wording layer will move first",
                "permitted": "among the three measured layers, "
                             "authority-adjacent recurring formulas show the "
                             "greatest historical mobility. Whether this "
                             "layer responds first to future AI adoption is a "
                             "prospective hypothesis."},
            "3_inseparabilityNarrowed": {
                "withdrawn": "source and formula are inseparable",
                "permitted": "at the current exact-fingerprint resolution, no "
                             "circulating formula is observed with more than "
                             "one canonical authority identity",
                "unresolved": "near-family equivalence"},
            "noNumberChanged": True,
        },
        "notCausal": "a layer crossing a criterion after a commencement date "
                     "is an ordering of observations. It is never the statute "
                     "acting on the court, and no phase here asserts one.",
        "phase1_threeLayerBaselines": three_layer_input(),
        "phase2_eventSelection": cand,
        "phase4_publicationHealth": {k: v for k, v in health.items()
                                     if k != "_flags"},
        "phase5_6_layerStack": {
            "L0_OBSERVATION_SYSTEM": "publication health. Runs first and can "
                                     "veto everything above it.",
            "L2_BAR_STATUTORY_VISIBILITY": "party citation of the instrument",
            "L3_COURT_STATUTORY_VISIBILITY": "court citation",
            "L4_AUTHORITY_ADJACENT_FORMULA": "recurring wording beside an "
                                             "authority, locally attached to "
                                             "the instrument",
            "L5_AUTHORITY_ECOLOGY": "hybrid rate, named fiqh, traceability",
            "L6_DOCTRINAL_COMPANION": "first repeated non-statutory source",
            "L7_OPERATIONAL_CORE": "top-100 and top-50 court articles",
            "L8_RETRIEVAL_STATE": "displacement of a frozen pre-event "
                                  "top-50 snapshot",
            "isNotACausalChain": "the numbering is a measurement stack. No "
                                 "layer is expected to precede another and "
                                 "the analysis does not assume it.",
            "thresholds": {
                "TOP50_DISPLACEMENT_PCT": TOP50_DISPLACEMENT_PCT,
                "REPEATED_SOURCE_JUDGMENTS": REPEATED_SOURCE_JUDGMENTS,
                "CONCENTRATION_SHIFT": CONCENTRATION_SHIFT,
                "MIN_COURT_CITES_FOR_LAYER": MIN_COURT_CITES_FOR_LAYER,
                "HORIZON_QUARTERS": HORIZON,
                "provenance": "fixed once, before any post-period was read, "
                              "and applied identically to every event and "
                              "every pseudo-event. Nothing is tuned per law."},
        },
        "phase7_8_transitionAnatomy": anat,
        "phase14_uptakeCalibration": up,
        "phase19_pseudoEventControls": pseudo,
        "phase20_21_signatures": sigs,
        "phase9_formulaFirstTest": formula_first_test(anat),
        "phase17_crossEventComparison": cmp_,
        "phase29_31_earlyIndicators": early,
        "phase32_33_retrievalSequence": rseq,
        "phase34_observabilityMatrixV2": matrix_v2(),
        "phase38_paperBImplication": paper_b(anat),
        "phase35_prospectiveTransitionObject": prospective_schema(),
        "phase36_bet": b,
        **refai,
        "standingLimitations": [
            "TWO calibration events, both backfilled. Nothing here is "
            "foresight and nothing here may ever be credited as such.",
            "no commencement date per instrument; the clock is the registry's "
            "hijri effective year read at its first quarter.",
            "58 of 60 in-window arrivals have no verifiable legal clock.",
            "quarter resolution, so simultaneity is common and ties are "
            "reported as ties.",
            "the retrieval layer ages with time passing, so its crossing is "
            "not evidence about any event without the negative control "
            "beside it.",
        ],
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    LIB.write_text(json.dumps({
        "what": "TRANSITION SIGNATURE LIBRARY. One row per legal transition "
                "with a known clock, its layer latencies, and its capture "
                "class. The permanent asset of this programme.",
        "captureClasses": {
            "BACKFILLED_CALIBRATION": "recorded after the transition was "
                                      "observable. Calibrates a method; never "
                                      "foresight.",
            "PROSPECTIVE": "recorded before observable_from. None yet."},
        "thresholds": res["phase5_6_layerStack"]["thresholds"],
        "referenceSignatures": refai["phase22_referenceSignatures"],
        "signatures": sigs,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(sigs)} calibration transition(s); "
          f"{pseudo['pseudoEvents']} pseudo-events")
    for s in sigs:
        o = orders[s["event_id"]]
        print(f"  {s['event_id']} {s['instrument']:<24} T0={s['observable_from']}"
              f"  first={o['FIRST_MOVING_LAYER']}")
        print(f"      latencies {s['latencies']}")
        print(f"      never moved: {o['NO_DETECTED_SHIFT']}")
    print(f"  bet: {b['decision']}")
    print(f"-> {OUT.name}, {LIB.name}")


if __name__ == "__main__":
    main()
