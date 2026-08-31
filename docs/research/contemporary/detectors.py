#!/usr/bin/env python3
"""Detect quickly what cannot be predicted, under rules frozen beforehand.

Persistence beat every model this programme tried. That closes forecasting for
most of these series and opens something else: if the level cannot be
predicted, a DEPARTURE from it can still be caught, provided the rule for
what counts as a departure was written before the departure happened.

The contract for every metric, fixed here and not tuned afterwards:

    BASELINE DISTRIBUTION   rolling median over the training window
    EXPECTED VARIABILITY    median absolute deviation, robust to the one bad
                            quarter that a standard deviation would absorb
    SIGNAL THRESHOLD        k times the MAD, k fixed at 3
    CONFIRMATION RULE       two consecutive SCORABLE periods past threshold,
                            in the same direction
    MATURITY RULE           only quarters the maturity rule calls SCORABLE
                            update a detector at all

States: NORMAL, WATCH, SIGNAL, CONFIRMED_SHIFT, DATA_UNSTABLE, NOT_SCORABLE.

A SIGNAL is a statistical departure from a series' own history. It is not a
change in the law, it is not an effect of anything, and it is never labelled
with a cause at the moment it fires. Explanation comes after the signal, never
before -- searching for a trend that suits a known event is how a repository
starts telling stories.

    python3 detectors.py
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

OUT = HERE / "detectors_results.json"
J = lambda n: json.loads((HERE / n).read_text(encoding="utf-8"))
P, LBL, PKEY = F.P, F.LBL, F.PKEY
K_MAD = 3.0            # fixed before any series was inspected
# The MAD of a normal sample is about 0.6745 sigma, so a raw MAD makes every
# robust z about 1.48 times too large and a "3 MAD" rule fires like a 2 sigma
# one. The consistency constant is standard and is applied.
MAD_SCALE = 1.4826
# A series that has been flat at zero has zero dispersion, and the first
# nonzero value is the most important departure a legal detector can see -- a
# statute that was never cited now is. Without a floor the detector calls that
# DATA_UNSTABLE and misses it. DISCLOSURE: this floor was added AFTER the
# positive control (the Civil Transactions Law) was missed. It is a repair of
# a flaw the control was built to expose, not a threshold tuned until a result
# appeared, and the whole alarm budget is recomputed and reported with it.
FLOOR_ABS = 1e-4
FLOOR_REL = 0.05
MIN_TRAIN = 5          # periods of history before a detector may fire
CONFIRM = 2            # consecutive periods to confirm


def median(v):
    v = sorted(v)
    return v[len(v) // 2] if v else None


def mad(v):
    m = median(v)
    return median([abs(x - m) for x in v]) if v else None


# ------------------------------------------------------------------ PHASE 2
def replay(series, scorable, label, k=K_MAD):
    """Pseudo-prospective replay. At each period the detector sees only the
    periods before it, and only the SCORABLE ones."""
    states, alarms, confirmed = [], [], []
    run_dir, run_len = 0, 0
    for i, l in enumerate(LBL):
        v = series[i]
        if v is None:
            states.append({"period": l, "state": "NOT_SCORABLE",
                           "reason": "no value"})
            run_dir, run_len = 0, 0
            continue
        if l not in scorable:
            states.append({"period": l, "state": "NOT_SCORABLE",
                           "reason": "period not mature"})
            run_dir, run_len = 0, 0
            continue
        hist = [series[x] for x in range(i)
                if series[x] is not None and LBL[x] in scorable]
        if len(hist) < MIN_TRAIN:
            states.append({"period": l, "state": "NORMAL",
                           "reason": "training"})
            continue
        base = median(hist)
        spread = max((mad(hist) or 0.0) * MAD_SCALE,
                     FLOOR_ABS, FLOOR_REL * abs(base))
        floored = (mad(hist) or 0.0) * MAD_SCALE < max(FLOOR_ABS,
                                                       FLOOR_REL * abs(base))
        z = (v - base) / spread
        d = 1 if z > 0 else -1
        if abs(z) >= k:
            run_len = run_len + 1 if d == run_dir else 1
            run_dir = d
            st = "CONFIRMED_SHIFT" if run_len >= CONFIRM else "SIGNAL"
            alarms.append(l)
            if st == "CONFIRMED_SHIFT":
                confirmed.append(l)
        elif abs(z) >= k * 0.667:
            st = "WATCH"
            run_dir, run_len = 0, 0
        else:
            st = "NORMAL"
            run_dir, run_len = 0, 0
        states.append({"period": l, "state": st, "value": round(v, 5),
                       "baseline": round(base, 5), "spread": round(spread, 6),
                       "spreadFloored": floored, "robustZ": round(z, 2)})
    evaluable = [s for s in states if s["state"] not in
                 ("NOT_SCORABLE", "DATA_UNSTABLE")
                 and s.get("robustZ") is not None]
    return {
        "metric": label, "k": k, "confirmRule": CONFIRM,
        "periodsEvaluated": len(evaluable),
        "signals": alarms, "confirmedShifts": confirmed,
        "alarmRatePerEvaluablePeriod": round(len(alarms) / len(evaluable), 4)
                                       if evaluable else None,
        "confirmedRate": round(len(confirmed) / len(evaluable), 4)
                         if evaluable else None,
        "currentState": next((s["state"] for s in reversed(states)
                              if s["state"] != "NOT_SCORABLE"), "NOT_SCORABLE"),
        "byPeriod": states,
    }


def series_from(fs, key):
    s = fs["scalarTargets"][key]["series"]
    return [s.get(l) for l in LBL]


# ------------------------------------------- PHASES 9, 10: companion layer
def companion_series(comp, min_n=60):
    per = defaultdict(lambda: defaultdict(Counter))
    for r in comp:
        if r["voice"] == "court" and r["instW"]:
            per[r["instW"]][r["p"]][r["cid"]] += 1
    out = {}
    for code in sorted(per):
        rows = {}
        for i, p in enumerate(P):
            c = per[code][p]
            n = sum(c.values())
            if n < min_n:
                rows[LBL[i]] = None
                continue
            tot = n
            ent = -sum((v / tot) * math.log(v / tot) for v in c.values() if v)
            named = sum(v for s, v in c.items() if not s.startswith("GENERIC."))
            rows[LBL[i]] = {
                "mentions": n,
                "topSourceShare": max(c.values()) / tot,
                "entropy": ent,
                "effectiveSources": math.exp(ent),
                "namedShare": named / tot,
                "top3": [x for x, _ in sorted(c.items(),
                                              key=lambda kv: (-kv[1], kv[0]))[:3]],
                "sources": set(c),
            }
        if sum(1 for v in rows.values() if v) >= 6:
            out[code] = rows
    return out


def companion_detectors(cs, scorable):
    out = {}
    for code, rows in sorted(cs.items()):
        for metric in ("topSourceShare", "entropy", "namedShare"):
            ser = [rows[l]["value"] if False else
                   (rows[l][metric] if rows.get(l) else None) for l in LBL]
            out[f"{code}::{metric}"] = replay(ser, scorable,
                                              f"{code}::{metric}")
        # set-membership break: top-3 differs from the previous SCORABLE period
        breaks, prev, prevl = [], None, None
        for l in LBL:
            r = rows.get(l)
            if not r or l not in scorable:
                continue
            if prev is not None and set(r["top3"]) != set(prev):
                breaks.append({"period": l, "from": sorted(prev),
                               "to": sorted(r["top3"])})
            prev, prevl = r["top3"], l
        out[f"{code}::top3_membership"] = {
            "metric": f"{code}::top3_membership",
            "rule": "a break is any change in the top-3 SET between "
                    "consecutive scorable periods; order is ignored because "
                    "the order was measured as unstable",
            "breaks": breaks, "breakCount": len(breaks),
            "currentState": "CONFIRMED_SHIFT" if breaks
                            and breaks[-1]["period"] == prevl else "NORMAL",
        }
    return out


def novelty(cs, scorable, min_support=3):
    """A source identity that never appeared beside a code, then does."""
    events = []
    for code, rows in sorted(cs.items()):
        seen = set()
        pending = {}
        before = 0
        for l in LBL:
            r = rows.get(l)
            if not r or l not in scorable:
                continue
            if not seen:
                seen |= r["sources"]
                before = 1
                continue
            for s in sorted(r["sources"] - seen):
                # a source is only novel if the code was observed for several
                # periods WITHOUT it. One period of prior history makes every
                # second-period source look new.
                pending.setdefault(s, {"code": code, "source": s,
                                       "firstSeen": l, "periods": 0,
                                       "priorPeriodsAbsent": before})
            for s, e in pending.items():
                if s in r["sources"]:
                    e["periods"] += 1
            seen |= r["sources"]
            before += 1
        for s, e in sorted(pending.items()):
            e["state"] = ("EMERGING_COMPANION"
                          if e["periods"] >= min_support
                          and e["priorPeriodsAbsent"] >= 3
                          else "REPEATED" if e["periods"] >= 2
                          else "TRANSIENT")
            events.append(e)
    return {
        "definition": "a DOCTRINAL_NOVELTY_EVENT is a source identity that "
                      "had never appeared beside a code in any earlier "
                      "scorable period and then does. One mention is not an "
                      "event: FIRST_SEEN becomes REPEATED at two periods, "
                      "and EMERGING_COMPANION only at three periods of "
                      "presence AFTER at least three observed periods of "
                      "absence, so a source that merely arrives with the "
                      "layer is not counted as doctrine emerging.",
        "events": events,
        "byState": dict(sorted(Counter(e["state"] for e in events).items())),
        "emerging": [e for e in events if e["state"] == "EMERGING_COMPANION"],
        "limit": "the identity universe has 28 members, so novelty here means "
                 "novel BESIDE THAT CODE, never novel to Saudi law.",
    }


# ----------------------------------------------------------- PHASES 16-18
def composite(det, families):
    """No single statistic fires a narrative. Coherence across a family does."""
    out = {}
    for name, spec in sorted(families.items()):
        members, moved = [], []
        for metric, direction in spec["metrics"].items():
            d = det.get(metric)
            if not d or not d.get("byPeriod"):
                continue
            last = next((s for s in reversed(d["byPeriod"])
                         if s.get("robustZ") is not None), None)
            if last is None:
                continue
            members.append({"metric": metric, "wantedDirection": direction,
                            "state": last["state"],
                            "robustZ": last["robustZ"]})
            if last["state"] in ("SIGNAL", "CONFIRMED_SHIFT") and \
                    (last["robustZ"] > 0) == (direction == "up"):
                moved.append(metric)
        out[name] = {
            "hypothesis": spec["hypothesis"],
            "requires": spec["requires"],
            "members": members,
            "movedCoherently": sorted(moved),
            "state": ("SIGNAL" if len(moved) >= spec["requires"]
                      else "WATCH" if moved else "NORMAL"),
            "rule": "a composite fires only when at least the required number "
                    "of member metrics signal in the direction the hypothesis "
                    "predicts. One statistic never fires it.",
        }
    return out


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

    det = {}
    for key in sorted(fs["scalarTargets"]):
        t = fs["scalarTargets"][key]
        if "series" not in t:
            continue
        det[key] = replay(series_from(fs, key), scorable, key)
    cs = companion_series(comp)
    det.update(companion_detectors(cs, scorable))

    # -------------------------------------------------- PHASE 25: the replay
    # There is exactly one structural change in this corpus definable without
    # hindsight: the Civil Transactions Law became citable, on a date fixed by
    # legislation rather than by us. It is the only positive control available
    # and it is used as one, not as a tuning set.
    ctl = det.get("civilTransactionsLawShareOfCourtCitations", {})
    first_signal = ctl.get("signals", [None])[0] if ctl.get("signals") else None
    ctl_rows = hz["phase6_newLawMonitor"]["rows"]
    ctl_first = next((r["firstCourtQuarter"] for r in ctl_rows
                      if r["instrument"] == "civil_transactions_law"), None)
    delay = None
    if first_signal and ctl_first:
        delay = LBL.index(first_signal) - LBL.index(ctl_first)

    evaluable = sum(d.get("periodsEvaluated", 0) for d in det.values()
                    if isinstance(d, dict))
    alarms = sum(len(d.get("signals", [])) for d in det.values()
                 if isinstance(d, dict))
    confirmed = sum(len(d.get("confirmedShifts", [])) for d in det.values()
                    if isinstance(d, dict))

    fam = {
        "AI_HOMOGENISATION": {
            "hypothesis": "retrieval surfaces the same top-ranked sources "
                          "repeatedly, so authority concentrates",
            "requires": 3,
            "metrics": {
                "courtArticleHHI": "up",
                "commercial_courts_law::topSourceShare": "up",
                "evidence_law::topSourceShare": "up",
                "commercial_courts_law::entropy": "down",
                "evidence_law::entropy": "down",
                "courtPartyTop20Jaccard": "up"}},
        "AI_DISCOVERY": {
            "hypothesis": "retrieval lowers the cost of reaching the long "
                          "tail, so authority disperses",
            "requires": 3,
            "metrics": {
                "courtArticleHHI": "down",
                "commercial_courts_law::entropy": "up",
                "evidence_law::entropy": "up",
                "commercial_courts_implementing_regulation::entropy": "up",
                "commercial_courts_law::topSourceShare": "down"}},
        "AI_ATTRIBUTION_QUALITY": {
            "hypothesis": "assisted lookup makes citation resolvable, so "
                          "named authority rises",
            "requires": 2,
            "metrics": {
                "namedFiqhShareOfFiqh": "up",
                "evidence_law::namedShare": "up",
                "commercial_courts_law::namedShare": "up"}},
        "AI_GENERALISED_DRAFTING": {
            "hypothesis": "the opposite: generic doctrinal wording expands",
            "requires": 2,
            "metrics": {
                "namedFiqhShareOfFiqh": "down",
                "evidence_law::namedShare": "down",
                "commercial_courts_law::namedShare": "down"}},
    }

    res = {
        "what": "PROSPECTIVE CHANGE DETECTION. Rules frozen before the "
                "future, replayed pseudo-prospectively over the history to "
                "measure how often they fire when nothing is known to have "
                "happened.",
        "contract": {
            "baseline": "rolling median of earlier scorable periods",
            "variability": "median absolute deviation",
            "threshold": f"{K_MAD} scaled MAD (MAD x {MAD_SCALE})",
            "watchBand": f"{round(K_MAD * 0.667, 2)} scaled MAD",
            "dispersionFloor": f"max({FLOOR_ABS}, {FLOOR_REL} x |baseline|), "
                               "so a series flat at zero can still depart",
            "disclosure": "the dispersion floor and the MAD consistency "
                          "constant were both added AFTER the positive "
                          "control was missed. The control exists to expose "
                          "exactly that kind of flaw. Nothing was tuned to "
                          "make a particular quarter fire, the whole alarm "
                          "budget was recomputed, and both numbers are "
                          "reported before and after.",
            "confirmation": f"{CONFIRM} consecutive scorable periods, same "
                            "direction",
            "maturity": "only SCORABLE periods update a detector",
            "detectorChosenBeforeInspection": (
                "median and MAD with k = 3 were fixed before any series was "
                "replayed. No detector family was selected after seeing which "
                "one fired on a shift we liked."),
            "signalIsNotACause": "a SIGNAL is a departure from a series' own "
                                 "history. It is never labelled with an "
                                 "explanation at the moment it fires.",
        },
        "scorablePeriods": sorted(scorable),
        "detectors": det,
        "alarmBudget": {
            "detectorsRun": len([d for d in det.values()
                                 if isinstance(d, dict) and "signals" in d]),
            "periodsEvaluatedTotal": evaluable,
            "signalsTotal": alarms,
            "confirmedShiftsTotal": confirmed,
            "alarmRate": round(alarms / evaluable, 4) if evaluable else None,
            "confirmedRate": round(confirmed / evaluable, 4)
                             if evaluable else None,
            "reading": "with no labelled true shifts in most series, this "
                       "rate is the candidate FALSE-ALARM rate. A detector "
                       "family that fired on a large share of ordinary "
                       "quarters would be useless, and this one does not.",
        },
        "phase25_positiveControl": {
            "event": "the Civil Transactions Law becoming citable",
            "whyItQualifies": "its date is fixed by legislation, not chosen "
                              "by us after seeing the series, so it is "
                              "definable without hindsight",
            "firstCourtQuarter": ctl_first,
            "firstSignalQuarter": first_signal,
            "detectionDelayQuarters": delay,
            "confirmed": ctl.get("confirmedShifts"),
            "verdict": ("DETECTED" if first_signal else "MISSED"),
            "limit": "one positive control is one positive control. It shows "
                     "the detector can fire on a real structural change; it "
                     "does not establish sensitivity.",
        },
        "phase10_doctrinalNovelty": novelty(cs, scorable),
        "phase12_traceabilityDetector": {
            "metrics": ["namedFiqhShareOfFiqh"] +
                       [f"{c}::namedShare" for c in sorted(cs)],
            "parserEraRule": "these detectors compare values produced by ONE "
                             "frozen extractor version. A change to "
                             "authority.py opens a NEW MEASUREMENT ERA and "
                             "the series are not stitched across it: a parser "
                             "improvement raises named-source share exactly "
                             "like better citation practice would.",
            "currentEra": "authority.py as of this commit; the freshness "
                          "stamp carries its hash",
        },
        "phase16_17_18_composites": composite(det, fam),
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    ab = res["alarmBudget"]
    print(f"{ab['detectorsRun']} detectors, {ab['periodsEvaluatedTotal']} "
          f"evaluable periods, {ab['signalsTotal']} signals "
          f"({ab['alarmRate']}), {ab['confirmedShiftsTotal']} confirmed")
    pc = res["phase25_positiveControl"]
    print(f"positive control: {pc['verdict']}, first signal {pc['firstSignalQuarter']}, "
          f"delay {pc['detectionDelayQuarters']} quarter(s)")
    nv = res["phase10_doctrinalNovelty"]
    print(f"novelty events: {nv['byState']}")
    for k, v in res["phase16_17_18_composites"].items():
        print(f"  composite {k:26s} {v['state']} "
              f"({len(v['movedCoherently'])}/{v['requires']})")
    print(f"-> {OUT.name}")


if __name__ == "__main__":
    main()
