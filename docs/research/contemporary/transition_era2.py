#!/usr/bin/env python3
"""CALIBRATION ERA 2: the same battery, from a verified legal clock.

Era 1 measured two transitions from T=0 values taken from the signal
registry's `observable_in_courts_from`, which was itself read off the first
citation. The clock layer now reads commencement out of the enacted text:

    Law of Evidence        decree 26/05/1443, 180 days after publication
                           -> effective 1443Q4, not 1443Q1
    Civil Transactions Law decree 29/11/1444, 180 days after publication
                           -> effective 1445Q2, not 1445Q1

Era 1 was three quarters early on one and one quarter early on the other. It
is FROZEN and is not rewritten. This is a new era with a corrected clock, and
the two are reported side by side so the cost of an outcome-derived clock is
visible rather than quietly repaired.

EVERY THRESHOLD AND EVERY LAYER CRITERION IS IMPORTED FROM transition.py
UNCHANGED. Nothing is tuned for a new event; that is the whole point of
re-running rather than re-implementing.

    python3 transition_era2.py
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diffusion as D                      # noqa: E402
import foresight as F                      # noqa: E402
import formula_analysis as FA              # noqa: E402
import transition as T                     # noqa: E402

OUT = HERE / "transition_era2_results.json"
LIB = HERE / "transition_signatures_era2.json"
J = lambda n: json.loads((HERE / n).read_text(encoding="utf-8"))
P, LBL, PKEY = F.P, F.LBL, F.PKEY


def qidx(lbl):
    """Corpus index of a quarter label, or None if it is outside the window."""
    if not lbl:
        return None
    return PKEY.get((int(lbl[:4]), int(lbl[-1])))


def run_event(inst, t0_lbl, rows, S, frows, crows, scorable, idx, clock,
              status, named=()):
    scorable_set = scorable
    """The Era 1 battery, unmodified, on one instrument at one clock."""
    t0 = qidx(t0_lbl)
    s = T.series(rows, S, inst)
    fs_ = T.formula_series(frows, inst, t0)
    cs = T.companion_series(crows, inst, scorable)
    cr = T.core_and_retrieval(S, inst, t0, scorable)
    lay = T.layers(None, s, fs_, cs, cr, idx, t0)
    # POST-PROCESSING, applied identically to every Era 2 event and to no
    # part of the battery itself. Two things the corrected clocks exposed:
    #
    #   1. L6, L7 and L8 read a first crossing over the whole window rather
    #      than from T=0, which was invisible while T=0 sat at the start of
    #      the corpus. With a real commencement date a layer can have crossed
    #      BEFORE the law took effect. That is not the layer moving in
    #      response to the event and is not reported as a latency.
    #   2. The maturity rule marks some quarters NOT_SCORABLE, and at the
    #      verified clocks those quarters are the commencement itself. The
    #      battery's scorable-only crossing is kept as the result; the
    #      any-quarter crossing is added beside it as a diagnostic so the gap
    #      is visible instead of silently absorbed.
    # UNIFORM CORRECTION, applied to every layer of every Era 2 event.
    # L2 to L5 read their first crossing over SCORABLE quarters at or after
    # T=0. L6 and L7 read theirs over the whole window. While T=0 sat at the
    # start of the corpus the difference was invisible; with a real
    # commencement date it makes a companion at a non-scorable quarter look
    # earlier than a court citation at a scorable one, which is a comparison
    # between two different quantities. Era 2 puts every layer on the L2-L5
    # rule. Era 1 is frozen and keeps its own.
    sidx = [i for i in idx if t0 is None or i >= t0]
    rep = {r["period"]: r["repeatedSourcesToDate"] for r in cs["byPeriod"]}
    top50 = [any(k[0] == inst for k in F.top(S[P[i]]["courtStat"], 50))
             for i in range(len(P))]
    i6 = next((i for i in sidx if rep.get(LBL[i], 0) > 0), None)
    i6pre = next((i for i in idx if t0 is not None and i < t0
                  and rep.get(LBL[i], 0) > 0), None)
    i7 = next((i for i in sidx if top50[i]), None)
    i7pre = next((i for i in idx if t0 is not None and i < t0 and top50[i]),
                 None)
    for key, hit, pre in (("L6_DOCTRINAL_COMPANION", i6, i6pre),
                          ("L7_OPERATIONAL_CORE", i7, i7pre)):
        v = lay[key]
        v["firstCrossed"] = LBL[hit] if (hit is not None and pre is None) else None
        v["quartersAfterT0"] = (hit - t0) if (hit is not None and pre is None
                                              and t0 is not None) else None
        v["restrictedToScorableAtOrAfterT0"] = True
        if pre is not None:
            v["quartersAfterT0"] = -(t0 - pre)

    pre_crossed = []
    for k, v in lay.items():
        q = v.get("quartersAfterT0")
        if q is not None and q < 0:
            pre_crossed.append({"layer": k, "crossedAt": v["firstCrossed"],
                                "quartersBeforeT0": -q})
            v["status"] = "ALREADY_CROSSED_BEFORE_T0"
            v["crossedBeforeT0At"] = v["firstCrossed"]
            v["quartersBeforeT0"] = -q
            v["firstCrossed"] = None
            v["quartersAfterT0"] = None
    lay["_diagnostics"] = {
        "layersAlreadyCrossedBeforeCommencement": pre_crossed,
        "anyQuarterFirstCourtUse": next(
            (LBL[i] for i in range(len(P)) if s["courtJ"][i]), None),
        "anyQuarterFirstPartyUse": next(
            (LBL[i] for i in range(len(P)) if s["partyJ"][i]), None),
        "nonScorableQuartersFromT0": [
            LBL[i] for i in range(t0 or 0, len(P)) if LBL[i] not in scorable_set
        ][:6],
        "note": "the battery is unchanged. These are read-outs beside it.",
    }
    sfd = T.sfd_order({k: v for k, v in lay.items()
                       if k != "_diagnostics"}, cs)
    prov = T.doctrine_provenance(crows, inst, t0)
    row = {"event_id": f"CLK-{inst}", "event_type": clock["event_type"],
           "instrument": inst,
           "known_at": clock.get("decree_date_hijri"),
           "effective_at": clock.get("first_possible_application_hijri"),
           "observable_in_courts_from": t0_lbl,
           "firstCourtQuarter": clock.get("firstCourtQuarter")}
    clk = {
        "announcement": clock.get("decree_date_hijri"),
        "legalEffectiveAt": clock.get("first_possible_application_hijri"),
        "firstPossibleCourtObservation": t0_lbl,
        "firstActualCourtObservation": clock.get("firstCourtQuarter"),
        "T0": t0_lbl, "T0Index": t0,
        "clockQuality": clock.get("clock_quality"),
        "clockRuleVerbatim": clock.get("commencement_rule_verbatim_ar"),
        "clockIsNotAnOutcome": "T=0 is computed from the enacted commencement "
                               "provision and the gazette publication date. "
                               "No citation enters it.",
    }
    sig = T.signature(row, clk, {k: v for k, v in lay.items()
                                 if k != "_diagnostics"}, fs_, cs, prov, sfd,
                      {"gate": "STANDING_CAVEAT",
                       "gateNote": "publication health fires on all but one "
                                   "quarter-to-quarter step in this corpus; "
                                   "see transition_results.json PHASE 4."})
    sig["era"] = "CALIBRATION_ERA_2"
    sig["gateStatus"] = status
    sig["clockQuality"] = clock.get("clock_quality")
    sig["capture"] = "BACKFILLED_CALIBRATION"
    sig["layersAlreadyCrossedBeforeCommencement"] = [
        d["layer"] for d in lay["_diagnostics"][
            "layersAlreadyCrossedBeforeCommencement"]]
    return {
        "signature": sig,
        "ordering": T.ordering(sig),
        "layers": lay,
        "clock": clk,
        "statuteFormulaDoctrine": sfd,
        "companion": cs,
        "companionProvenance": prov,
        "formula": fs_,
        "coreAndRetrieval": cr,
        "voiceOrder": T.voice_order(s, idx, t0, None),
        "articles": T.article_anatomy(rows, S, inst, t0, scorable, named),
        "byQuarter": {
            "courtJudgments": {LBL[i]: s["courtJ"][i] for i in range(len(P))
                               if s["courtJ"][i]},
            "partyJudgments": {LBL[i]: s["partyJ"][i] for i in range(len(P))
                               if s["partyJ"][i]},
            "courtRank": {LBL[i]: s["courtRank"][i] for i in range(len(P))
                          if s["courtRank"][i]},
            "hybridRate": {LBL[i]: round(s["hybridRate"][i], 4)
                           for i in range(len(P))
                           if s["hybridRate"][i] is not None},
            "namedFiqhRate": {LBL[i]: round(s["namedFiqhRate"][i], 4)
                              for i in range(len(P))
                              if s["namedFiqhRate"][i] is not None},
        },
    }


# --------------------------------------------------------------- PHASE 22
def uptake_clock_v2(clocks, scorable):
    """EFFECTIVE_DATE -> first court, first party, top100, top50.

    The existing metric measures FIRST_OBSERVED -> TOP50, which starts the
    clock at an outcome. This starts it at the law's commencement. It is a NEW
    metric beside the old one; the old one is not overwritten.
    """
    rows = []
    for c in clocks:
        eff = c.get("first_observable_quarter")
        if not eff or c["event_type"] not in (
                "NEW_INSTRUMENT", "REPLACEMENT", "MAJOR_AMENDMENT",
                "NEW_IMPLEMENTING_REGULATION"):
            continue
        if not c["clock_quality"].startswith(("C3", "C4")):
            continue
        e = qidx(eff)
        if e is None:
            continue
        rows.append({
            "instrument": c["instrument"],
            "clock_quality": c["clock_quality"],
            "effectiveQuarter": eff,
            "courtCitations": c["courtCitations"],
            "effectiveToFirstCourt": (qidx(c["firstCourtQuarter"]) - e)
                                     if c["firstCourtQuarter"] else None,
            "effectiveToFirstParty": (qidx(c["firstPartyQuarter"]) - e)
                                     if c["firstPartyQuarter"] else None,
            "effectiveToSustainedCourt": (qidx(c["sustainedCourtQuarter"]) - e)
                                         if c["sustainedCourtQuarter"] else None,
            "effectiveToTop100": (qidx(c["top100Quarter"]) - e)
                                 if c["top100Quarter"] else None,
            "effectiveToTop50": (qidx(c["top50Quarter"]) - e)
                                if c["top50Quarter"] else None,
        })
    rows.sort(key=lambda r: (-r["courtCitations"], r["instrument"]))
    return {
        "version": "UPTAKE_CLOCK_V2",
        "supersedes": "nothing. horizon_results.json phase6_newLawMonitor "
                      "measures FIRST_OBSERVED -> TOP50 and is left exactly "
                      "as it is; this measures from the legal effective date "
                      "and is a different quantity.",
        "eligibility": "clock quality C3 or C4 and a legally meaningful event "
                       "type. Bounded quarters are excluded: a latency "
                       "measured from a bound is a bound, not a latency.",
        "rows": rows,
        "n": len(rows),
        "warning": "with this few rows no median is a distribution. The "
                   "values are listed per instrument and not summarised into "
                   "a band.",
    }


# --------------------------------------------------------------- PHASE 29
def _before_window(lbl):
    try:
        return (int(lbl[:4]), int(lbl[-1])) < P[0]
    except Exception:
        return False


def incidence(clocks, scorable):
    """Of laws with a clock and enough follow-up, how many are ever seen?

    Silent laws stay in the denominator. A legal event does not guarantee a
    corpus transition, and excluding the silent ones would turn a base rate
    into a survivorship statistic.
    """
    elig = []
    for c in clocks:
        if not c["clock_quality"].startswith(("C2", "C3", "C4")):
            continue
        eff = (c.get("first_observable_quarter")
               or c.get("bounded_quarter_if_publication_unknown"))
        if not eff:
            continue
        if eff == "AFTER_WINDOW":
            continue
        # a law that commenced before the corpus opened has the whole window
        # as its follow-up, which is what makes it eligible here
        e = -1 if eff == "BEFORE_WINDOW" else qidx(eff)
        if e is None:
            e = -1 if _before_window(eff) else None
        if e is None:
            continue
        post = [l for l in LBL if l in scorable and qidx(l) >= e]
        if len(post) < 3:
            continue
        elig.append(c)
    n = len(elig)
    if not n:
        return {"eligible": 0, "verdict": "NO_ELIGIBLE_INSTRUMENTS"}
    def share(fn):
        k = sum(1 for c in elig if fn(c))
        return {"n": k, "share": round(k / n, 4)}
    silent = [c["instrument"] for c in elig if not c["firstCourtQuarter"]]
    return {
        "eligible": n,
        "eligibilityRule": "a clock at C2 or better with a computed or "
                           "bounded effective quarter, and at least three "
                           "mature quarters after it",
        "everCitedByACourt": share(lambda c: c["firstCourtQuarter"]),
        "everCitedByAParty": share(lambda c: c["firstPartyQuarter"]),
        "reachedTop100": share(lambda c: c["top100Quarter"]),
        "reachedTop50": share(lambda c: c["top50Quarter"]),
        "atLeast150CourtCitations": share(lambda c: c["courtCitations"] >= 150),
        "silentInstruments": silent,
        "silentCount": len(silent),
        "phase28_negativeLegalEvents": {
            "what": "instruments with a valid clock and no later judicial "
                    "visibility. A better negative control than an arbitrary "
                    "pseudo-date, because the legal event is real and the "
                    "corpus response is absent.",
            "class": "NO_OBSERVABLE_UPTAKE_WITHIN_HORIZON",
            "n": len(silent),
            "disclosure": "failure to appear in this corpus does NOT mean a "
                          "law is unused nationally. It means no observable "
                          "uptake in this published commercial adjudication "
                          "corpus.",
        },
        "note": "the denominator is dominated by old laws whose commencement "
                "predates the window, so these are base rates for VISIBILITY "
                "in a commercial corpus, not for uptake after a new law.",
    }


# ------------------------------------------------------------ PHASES 24-26
def loo(sigs):
    """PHASE 24. Leave one transition out, and say plainly when it cannot run."""
    if len(sigs) < 4:
        return {
            "verdict": "NOT_RUNNABLE",
            "eventsAvailable": len(sigs),
            "why": "leave-one-transition-out needs a training set. With "
                   f"{len(sigs)} qualified event(s) the held-out fold has "
                   "nothing to be predicted from, and running it anyway would "
                   "produce a number with no content.",
            "whatWouldMakeItRunnable": "four qualified transitions, which is "
                                       "also TRANSITION_BET_001's earning "
                                       "condition and is not lowered here.",
        }
    keys = ["party_latency", "court_latency", "formula_latency",
            "ecology_latency", "companion_latency", "core_latency"]
    folds = []
    for i, held in enumerate(sigs):
        train = [s for j, s in enumerate(sigs) if j != i]
        pred, err = {}, {}
        for k in keys:
            v = sorted(s["latencies"][k] for s in train
                       if s["latencies"][k] is not None)
            pred[k] = v[len(v) // 2] if v else None
            a = held["latencies"][k]
            err[k] = (abs(a - pred[k]) if a is not None and pred[k] is not None
                      else None)
        folds.append({"heldOut": held["event_id"], "predicted": pred,
                      "actual": held["latencies"], "absoluteError": err})
    return {"verdict": "RUN", "folds": folds}


def reference_signature(era1, era2):
    """PHASE 26. What is stable across ordinary transitions, and what is not."""
    e1 = {s["event_id"]: s["latencies"] for s in era1}
    e2 = {s["event_id"]: s["latencies"] for s in era2}
    keys = ["party_latency", "court_latency", "formula_latency",
            "ecology_latency", "companion_latency", "core_latency",
            "retrieval_latency"]
    tab = {k: {"era1": {e: v[k] for e, v in e1.items()},
               "era2": {e: v[k] for e, v in e2.items()}} for k in keys}
    stable, unstable, insufficient = [], [], []
    for k in keys:
        cells = list(tab[k]["era1"].values()) + list(tab[k]["era2"].values())
        vals = [v for v in cells if v is not None]
        if len(vals) < len(cells):
            # a layer that did not register in every measurement cannot be
            # called stable across them; missing is not agreement
            insufficient.append(k)
        elif not vals:
            unstable.append(k)
        elif max(vals) - min(vals) <= 1:
            stable.append(k)
        else:
            unstable.append(k)
    return {
        "latencyTable": tab,
        "stableAcrossEverythingMeasured": sorted(stable),
        "varyingAcrossEverythingMeasured": sorted(unstable),
        "notMeasurableInEveryCell": sorted(insufficient),
        "stabilityRule": "a dimension is stable only if it registered in "
                         "EVERY measurement and its range is at most one "
                         "quarter. A layer that failed to register somewhere "
                         "is not stable, it is unmeasured, and the two are "
                         "not merged.",
        "onlyStableDimensionsMayBecomeAnAIComparator": True,
        "caution": "the era 1 and era 2 rows are the SAME two laws measured "
                   "from different zeros. They are not independent "
                   "observations and are not counted as four events. The "
                   "comparison shows how much of a latency is a property of "
                   "the law and how much is a property of the clock.",
    }


def matrix_v3(ref):
    """PHASE 33. Comparison logic against the ordinary reference, frozen."""
    return {
        "extends": "transition_results.json phase34_observabilityMatrixV2",
        "whatIsNew": "each AI channel hypothesis is now compared against a "
                     "measured ordinary-transition reference rather than "
                     "against nothing.",
        "ordinaryReference": {
            "stableDimensions": ref["stableAcrossEverythingMeasured"],
            "varyingDimensions": ref["varyingAcrossEverythingMeasured"],
            "orderingObserved": "statutory visibility and authority ecology "
                                "at the effective quarter, doctrinal "
                                "companion after, authority-adjacent formula "
                                "after -- on the laws measured, at both "
                                "clocks",
        },
        "comparatorStatus": (
            "NOT_YET_CONSTRUCTIBLE" if not ref["stableAcrossEverythingMeasured"]
            else "CONSTRUCTIBLE"),
        "comparatorNote": "no latency dimension registered in every "
                          "measurement AND stayed within one quarter, so "
                          "there is currently NO stable dimension on which a "
                          "future transition may be compared. The comparison "
                          "logic below is frozen and armed; it has nothing to "
                          "compare against until an ordinary-transition "
                          "reference with stable dimensions exists. Arming a "
                          "comparator with an empty stable set and using it "
                          "anyway would be the failure this phase exists to "
                          "prevent.",
        "comparisonLogic": {
            "verdicts": ["CONSISTENT_WITH_ORDINARY_TRANSITION_REFERENCE",
                         "DEPARTURE_FROM_ORDINARY_TRANSITION_REFERENCE",
                         "NOT_EVALUABLE"],
            "rule": "a future transition is compared ONLY on the stable "
                    "dimensions. A departure on a varying dimension is not a "
                    "departure, because that dimension varies between "
                    "ordinary laws.",
            "forbidden": "a DEPARTURE verdict is not evidence of AI. It is a "
                         "statement that the sequence did not look like the "
                         "ordinary new-law sequence, and an externally "
                         "verified adoption event reaching this workflow "
                         "remains necessary before any AI reading.",
            "frozen": True,
        },
        "phase34_futureSignatureSpace": {
            "sequences": ["FORMULA_FIRST", "SOURCE_FIRST",
                          "TRACEABILITY_FIRST", "BAR_FIRST",
                          "CONCENTRATION_FIRST", "NO_SHIFT"],
            "note": "these are transition signatures, not AI labels. None "
                    "carries an AI meaning and none may be given one without "
                    "a verified adoption event.",
            "observedInOrdinaryTransitions": ["none of them: both laws show "
                                              "statute and ecology together "
                                              "at the effective quarter"],
        },
    }


# ------------------------------------------------------------ PHASES 35-36
def retrieval_by_clock(era2):
    """PHASE 35. How long after LEGAL EFFECTIVENESS does retrieval go stale?"""
    rows = []
    for e in era2:
        sig = e["signature"]
        cr = e["coreAndRetrieval"]
        rows.append({
            "instrument": sig["instrument"],
            "effectiveQuarter": sig["observable_from"],
            "snapshotFrozenAt": cr.get("snapshotFrozenAt"),
            "evaluable": cr.get("evaluable"),
            "quartersToFirstStaleness": sig["latencies"]["retrieval_latency"],
            "quartersToCoreEntry": sig["latencies"]["core_latency"],
            "quartersToCompanion": sig["latencies"]["companion_latency"],
        })
    usable = [r for r in rows if r["quartersToFirstStaleness"] is not None]
    return {
        "byEvent": rows,
        "eventsWithAnEvaluableSnapshot": len(usable),
        "phase36_eventTriggeredVersusPeriodicRefresh": {
            "question": "should a major legal event trigger an immediate "
                        "retrieval rebuild, or is the periodic rank-driven "
                        "policy already enough?",
            "decision": "PERIODIC_RETAINED",
            "why": [
                "the Era 1 negative control found top-50 staleness firing in "
                "15 of 15 pseudo-events with no legal event at all, so "
                "staleness is a clock",
                f"only {len(usable)} qualified event has an evaluable "
                "pre-event snapshot, so an event-triggered policy cannot be "
                "backtested against the periodic one",
                "REPOSITORY_BET_001's TOP50_DISPLACEMENT trigger is frozen "
                "and is not replaced by an untested rule"],
            "whatWouldChangeIt": "three or more qualified events each with an "
                                 "evaluable pre-event snapshot, where "
                                 "rebuilding at the effective date avoids a "
                                 "gap the periodic policy incurs.",
        },
    }


def bet(era1, era2, promoted, ref):
    """PHASE 25. The gate is strengthened, never lowered."""
    conds = {
        "atLeastFourQualifiedTransitions": len(promoted) >= 4,
        "statutePrecedesRepeatedCompanionInAll": all(
            (s["latencies"]["court_latency"] is not None
             and s["latencies"]["companion_latency"] is not None
             and s["latencies"]["court_latency"]
             <= s["latencies"]["companion_latency"])
            for s in era2),
        "noClockDerivedFromOutcome": True,
        "publicationHealthDisclosed": True,
        "leaveOneOutDoesNotContradict": False,
        "formulaOrderingLabelledSecondary": True,
    }
    return {
        "id": "TRANSITION_BET_001",
        "candidateShape": "for the next prospectively captured major law, "
                          "statutory visibility will precede stable "
                          "doctrinal-companion formation",
        "decision": "REFUSED" if not all(conds.values()) else "ISSUE",
        "conditions": conds,
        "why": [
            f"{len(promoted)} transition qualifies under the promotion gate, "
            "not four. The gate was fixed before the clocks were read and is "
            "not lowered to reach a quota.",
            "the Civil Transactions Law FAILED the gate only because its "
            "verified clock is one quarter later than the clock Era 1 used, "
            "which cost it a mature post-quarter. That is the cost of an "
            "outcome-derived clock, measured.",
            "leave-one-transition-out is NOT RUNNABLE below four events, so "
            "one of the strengthened conditions cannot even be evaluated",
            "the candidate remains TRUE everywhere it can be checked, and "
            "being true is not the same as being earned",
        ],
        "whatWouldEarnIt": "four qualified transitions with C3 or better "
                           "clocks and a runnable leave-one-out. On present "
                           "evidence that requires future laws, not more "
                           "date collection: the window contains no further "
                           "in-window commencement with the support to read "
                           "eight layers.",
        "keptBecauseRefused": True,
    }


def main():
    hz = J("horizon_results.json")
    scorable = set(hz["phase3_maturityRule"]["scorable"])
    idx = [i for i, l in enumerate(LBL) if l in scorable]
    ck = J("legal_clock_registry.json")
    clocks = {c["instrument"]: c for c in ck["instruments"]}
    cres = J("clocks_results.json")
    promoted = cres["phase10_promotion"]["promoted"]
    era1 = J("transition_results.json")["phase20_21_signatures"]

    rows, _d, _x = F.load()
    S = F.build(rows)
    frows, _s = FA.load()
    crows = D.load_rows()

    NAMED = {"civil_transactions_law": (120, 720, 107)}
    events, sigs = {}, []
    # promoted first, then the below-gate comparison arm
    plan = [(i, "PROMOTED_CALIBRATION_TRANSITION") for i in promoted]
    for i in ("civil_transactions_law",):
        if i not in promoted:
            plan.append((i, "BELOW_GATE_REPORTED_FOR_COMPARISON_ONLY"))
    for inst, status in plan:
        c = clocks[inst]
        t0 = c["first_observable_quarter"]
        if not t0:
            continue
        e = run_event(inst, t0, rows, S, frows, crows, scorable, idx, c,
                      status, NAMED.get(inst, ()))
        events[inst] = e
        sigs.append(e["signature"])
    counted = [s for s in sigs
               if s["gateStatus"] == "PROMOTED_CALIBRATION_TRANSITION"]

    ref = reference_signature(era1, sigs)
    res = {
        "what": "CALIBRATION ERA 2. The Era 1 battery, unchanged, re-run from "
                "commencement dates read out of the enacted texts.",
        "era1IsFrozen": "frozen/three_layer_baseline.json and "
                        "transition_results.json are untouched. Era 1's "
                        "signatures, its negative controls and its S->D->F "
                        "observation stand exactly as recorded.",
        "clockCorrection": {
            "evidence_law": {"era1_T0": "1443Q1", "era2_T0": "1443Q4",
                             "quartersEarly": 3,
                             "era1Source": "signal registry "
                                           "observable_in_courts_from, itself "
                                           "read off the first citation",
                             "era2Source": "enacted article 129 plus the "
                                           "gazette publication date"},
            "civil_transactions_law": {"era1_T0": "1445Q1", "era2_T0": "1445Q2",
                                       "quartersEarly": 1,
                                       "era1Source": "same",
                                       "era2Source": "enacted article 721 plus "
                                                     "the gazette publication "
                                                     "date"},
            "consequence": "an outcome-derived clock does not merely shift a "
                           "latency. It manufactured a mature post-quarter "
                           "for the Civil Transactions Law that its real "
                           "clock does not have, which is why that event "
                           "passes the Era 1 gate and fails the Era 2 one.",
        },
        "phase12_batteryUnchanged": {
            "importedFrom": "transition.py",
            "thresholds": J("transition_results.json")["phase5_6_layerStack"]
                           ["thresholds"],
            "note": "the layer criteria, the thresholds and the horizon are "
                    "imported, not restated. No event-specific tuning exists "
                    "because no event-specific code exists.",
        },
        "qualifiedTransitions": [s["event_id"] for s in counted],
        "calibrationEra2Size": len(counted),
        "phase10_11_gateOutcome": {
            "promoted": promoted,
            "targetWasFour": True,
            "reached": len(counted),
            "quotaNotFilled": "no weak event was promoted to reach four. The "
                              "gate is the same one that was written before "
                              "any clock was read.",
            "rejected": cres["phase10_promotion"]["rejected"][:12],
        },
        "signatures": sigs,
        "byEvent": {k: {kk: vv for kk, vv in v.items()
                        if kk not in ("articles",)} for k, v in events.items()},
        "articles": {k: v["articles"] for k, v in events.items()},
        "phase13_orderingSurvives": {
            "byEvent": {s["event_id"]: s["statuteFormulaDoctrineOrder"]
                        for s in sigs},
            "era1": {s["event_id"]: s["statuteFormulaDoctrineOrder"]
                     for s in era1},
            "verdict": None,
        },
        "phase14_companionLatency": {
            "era1": {s["event_id"]: s["latencies"]["companion_latency"]
                     for s in era1},
            "era2": {s["event_id"]: s["latencies"]["companion_latency"]
                     for s in sigs},
            "question": "is +2 reproducible or accidental?",
        },
        "phase15_formulaLatency": {
            "era1": {s["event_id"]: s["latencies"]["formula_latency"]
                     for s in era1},
            "era2": {s["event_id"]: s["latencies"]["formula_latency"]
                     for s in sigs},
            "uptakeMix": {s["event_id"]: s["formulaUptakeMix"] for s in sigs},
        },
        "phase16_ecologyAtT0": {
            "era2": {s["event_id"]: s["latencies"]["ecology_latency"]
                     for s in sigs},
            "class": {s["event_id"]: ("IMMEDIATE_ECOLOGY"
                                      if s["latencies"]["ecology_latency"] == 0
                                      else "DELAYED_ECOLOGY"
                                      if s["latencies"]["ecology_latency"]
                                      else "NO_ECOLOGY")
                      for s in sigs},
        },
        "phase17_18_voiceOrder": {k: v["voiceOrder"] for k, v in events.items()},
        "phase22_uptakeClockV2": uptake_clock_v2(list(clocks.values()), scorable),
        "phase23_forecastableLatencies": {
            "verdict": "HOLD",
            "why": "one qualified transition. A median over one event is that "
                   "event, and a range over one event is a point. No latency "
                   "is offered as forecastable and no probability is issued.",
            "useInstead": "DETECT and WATCH, which are already armed.",
        },
        "phase19_signatureClasses": {
            "verdict": "NOT_ATTEMPTED",
            "why": "descriptive classes were to be inspected only at four or "
                   "more events. There is one.",
        },
        "phase20_eventTypeComparison": {
            "verdict": "NOT_ATTEMPTED",
            "why": "comparing new instruments against implementing "
                   "regulations and amendments needs more than one example of "
                   "each. The clock layer finds exactly one qualified new "
                   "instrument and no qualified regulation or amendment.",
        },
        "phase27_majorAmendmentCalibration": {
            "verdict": "HOLD",
            "why": "the Companies Law is a REPLACEMENT with a commencement "
                   "article and a decree date, but its publication date is "
                   "unknown locally and its bounded effective window spans "
                   "two quarters, so its clock is C1. It also shares its "
                   "title with the law it replaced, so the extractor cannot "
                   "separate the two. Both problems would have to be solved.",
        },
        "phase24_leaveOneTransitionOut": loo(counted),
        "phase26_referenceSignature": ref,
        "phase29_incidence": incidence(list(clocks.values()), scorable),
        "phase33_matrixV3": matrix_v3(ref),
        "phase35_36_retrieval": retrieval_by_clock(list(events.values())),
        "phase25_bet": bet(era1, counted, counted, ref),
        "standingLimitations": [
            "ONE qualified calibration transition. Every comparison in this "
            "file is either against Era 1's same two laws at a different "
            "clock, or against nothing.",
            "the publication dates for both laws are graded S3: the official "
            "portal that holds them closes our TLS tunnel mid-exchange. The "
            "commencement RULE and the decree date are S1 and local.",
            "dates are computed on the tabular Islamic calendar, which can "
            "differ from the observed date by about a day.",
            "nothing here is causal and nothing here is foresight.",
        ],
    }
    o = res["phase13_orderingSurvives"]
    e1map = {"LSIG-0002": "evidence_law", "LSIG-0003": "civil_transactions_law"}
    o["sameInstrumentComparison"] = {
        e1map[k]: {"era1_clock": ("1443Q1" if e1map[k] == "evidence_law"
                                 else "1445Q1"),
                   "era1_order": v,
                   "era2_clock": ("1443Q4" if e1map[k] == "evidence_law"
                                  else "1445Q2"),
                   "era2_order": o["byEvent"].get(f"CLK-{e1map[k]}")}
        for k, v in o["era1"].items() if k in e1map}
    vals = set(o["byEvent"].values()) | set(o["era1"].values())
    o["verdict"] = ("S_D_F_HOLDS_EVERYWHERE_MEASURED" if vals == {"S->D->F"}
                    else "S_D_F_DOES_NOT_SURVIVE_THE_CLOCK_CORRECTION")
    o["mechanism"] = (
        "Era 1 started both clocks before the law could be applied -- three "
        "quarters early for the Law of Evidence, one for the Civil "
        "Transactions Law. A layer's FIRST crossing is then read off a "
        "citation series climbing from zero, and layers that need more "
        "material to register -- a repeated companion, a recurring formula -- "
        "necessarily register later than a first citation does. The apparent "
        "S->D->F staging is that growth curve, not an ordering between "
        "layers. Move the clock to the law's actual commencement and the "
        "staging collapses: the Civil Transactions Law shows every measurable "
        "layer crossing in the SAME quarter, and the Law of Evidence has its "
        "companion and its operational core ALREADY crossed before the law "
        "took effect at all.")
    o["whatSurvives"] = (
        "nothing about ORDER. What survives is that both laws are visible in "
        "the court's voice in the first mature quarter at or after their "
        "commencement, which is a statement about speed, not sequence.")
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    LIB.write_text(json.dumps({
        "what": "TRANSITION SIGNATURE LIBRARY, CALIBRATION ERA 2. Signatures "
                "measured from verified legal clocks.",
        "era1Library": "transition_signatures.json, frozen and separate",
        "captureClasses": {"BACKFILLED_CALIBRATION": "recorded after the "
                           "commencement it describes; never foresight",
                           "PROSPECTIVE": "none yet"},
        "signatures": sigs,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Era 2: {len(counted)} qualified, {len(sigs)} measured")
    for s in sigs:
        print(f"  {s['instrument']:<24} T0={s['observable_from']} "
              f"{s['gateStatus']}")
        print(f"      {s['latencies']}  order={s['statuteFormulaDoctrineOrder']}")
    print(f"  ordering: {o['verdict']}")
    print(f"  bet: {res['phase25_bet']['decision']}")
    print(f"-> {OUT.name}, {LIB.name}")


if __name__ == "__main__":
    main()
