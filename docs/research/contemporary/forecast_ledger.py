#!/usr/bin/env python3
"""Issue forecasts that can be scored, and never let one be rewritten.

A repository that only explains the past cannot be wrong. This file is how
this one becomes able to be wrong: it writes predictions about periods that do
not exist yet, with the scoring rule fixed before the outcome is observable,
and it refuses to modify an entry once written.

WHAT QUALIFIES AS A FORECAST HERE. Three things are kept apart and never
mixed. A FORECAST is a statement about an observable future variable with a
scoring rule. A CONDITIONAL FORECAST is a statement of the form "if the
adoption threshold defined in adoption_registry.json is met, then Y moves by
Z" -- it is scored only if the condition is met and observable. A SCENARIO is
a mechanical what-if; it carries no scoring rule, enters no skill statistic,
and is stored in its own section so it cannot be mistaken for either.

ON SKILL. The backtests in `foresight.py` found that NO model beats the naive
baselines on any scalar target. That is not a reason to withhold forecasts; it
is a reason to forecast WITH the baseline and to say so. Every entry names its
model, and where the model is a baseline the entry says so in the model field.
The uncertainty attached to each prediction is the backtested error of that
same predictor over the rolling folds: not a guess, and not a confidence
interval from a distributional assumption nobody checked.

    python3 forecast_ledger.py          # append any forecast not yet issued
    python3 forecast_ledger.py --check  # verify nothing already issued moved
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
LEDGER = HERE / "FORECAST_LEDGER.json"
J = lambda n: json.loads((HERE / n).read_text(encoding="utf-8"))
CREATED = "2026-08-31"
CUTOFF = "1446Q2"
PIPELINE = "contemporary/2026-08-companion+foresight"
TARGET = ("NEXT_ELIGIBLE_QUARTER: the earliest hijri quarter after 1446Q2 "
          "that carries at least 800 judgments with court authority in a "
          "future rebuild of this corpus. Defined this way because 1446Q3 "
          "and 1446Q4 are publication-lagged (184 and 7 judgments), and a "
          "forecast into them would be a forecast about the publisher. If no "
          "quarter reaches 800 by 1449Q4, every entry below becomes "
          "VOID_DATA_SHIFT rather than being scored.")


def head():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE,
                              capture_output=True, text=True,
                              timeout=20).stdout.strip()[:40] or "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def build():
    fs, ab = J("foresight_results.json"), J("ai_baseline_results.json")
    ca = J("companion_analysis_results.json")
    sc = fs["scalarTargets"]
    av, cp = fs["articleVisibility"], fs["companionPersistence"]
    rd = fs["retrievalDecay"]["h1"]

    def base(t):
        b = sc[t]["bestBaseline"]
        return b, sc[t]["mae"][b], sc[t]["series"]

    common = {"created_at": CREATED, "data_cutoff": CUTOFF,
              "target_period": TARGET, "repository_head": head(),
              "pipeline_version": PIPELINE,
              "data_hashes": ab["dataHashes"],
              "training_window": "1442Q1..1446Q2, rolling origin",
              "status": "OPEN"}
    out = []

    # ---- 1. the operational core
    out.append(dict(common, **{
        "forecast_id": f"operational_core_top50@{CUTOFF}",
        "target_definition":
            "the 50 (instrument, article) pairs most cited by the COURT in "
            "the target quarter, ranked by citation count, ties broken on the "
            "key. Scored against the frozen set stored as frozenTop50.",
        "model": "PERSISTENCE (the cutoff quarter's own top 50). This is a "
                 "BASELINE: no model beat it over 10 rolling folds, and MA3 "
                 f"was worse (mean Jaccard {av['meanTopKJaccard_ma3']} "
                 f"against {av['meanTopKJaccard_prevPeriod']}).",
        "prediction": {"expectedJaccardWithFrozenSet":
                       av["meanTopKJaccard_prevPeriod"],
                       "expectedNewEntrants": av["meanNewEntrantsPerPeriod"],
                       "frozenSet": "frozenTop50"},
        "uncertainty": {"backtestedJaccardWorstFold":
                        av["worstTopKJaccard_prevPeriod"],
                        "folds": av["folds"],
                        "intervalIsBacktestedRangeNotAModelInterval": True},
        "baseline_prediction": "identical: the model IS the baseline",
        "scoring_rule":
            "Jaccard(frozen top 50, observed top 50). SCORED_WELL if at least "
            f"{av['worstTopKJaccard_prevPeriod']} (the worst backtested "
            "fold); SCORED_POORLY otherwise. Report the value either way.",
    }))

    # ---- 2. the Civil Transactions Law
    b, mae, series = base("civilTransactionsLawShareOfCourtCitations")
    last = series[CUTOFF]
    out.append(dict(common, **{
        "forecast_id": f"ctl_court_share@{CUTOFF}",
        "target_definition":
            "the share of the court's statutory citations in the target "
            "quarter that name the Civil Transactions Law.",
        "model": f"{b} (a BASELINE; no model beat it over "
                 f"{sc['civilTransactionsLawShareOfCourtCitations']['folds']} "
                 "folds)",
        "prediction": {"pointEstimate": last,
                       "direction": "CONTINUED_PRESENCE_NEAR_CURRENT_LEVEL"},
        "uncertainty": {"backtestedMae": mae,
                        "interval": [round(max(0.0, last - 2 * mae), 5),
                                     round(last + 2 * mae, 5)],
                        "intervalIsPlusMinusTwoBacktestedMae": True},
        "baseline_prediction": last,
        "scoring_rule": "absolute error against the observed share; interval "
                        "coverage recorded as HIT or MISS. This is the only "
                        "new code whose arrival the corpus contains, so a "
                        "large miss is scientifically more interesting than a "
                        "hit.",
    }))

    # ---- 3. court and bar
    b, mae, series = base("courtPartyTop20Jaccard")
    vals = [v for v in series.values() if v is not None]
    pt = round(sum(vals[-3:]) / 3, 5)
    out.append(dict(common, **{
        "forecast_id": f"court_party_top20_jaccard@{CUTOFF}",
        "target_definition":
            "Jaccard between the court's top-20 and the strict party voice's "
            "top-20 (instrument, article) pairs in the target quarter.",
        "model": f"{b} (a BASELINE)",
        "prediction": {"pointEstimate": pt, "direction": "STABILITY"},
        "uncertainty": {"backtestedMae": mae,
                        "interval": [round(max(0.0, pt - 2 * mae), 5),
                                     round(pt + 2 * mae, 5)]},
        "baseline_prediction": pt,
        "scoring_rule":
            "absolute error, plus a direction call: CONVERGENCE if the "
            "observed value is above the interval, DIVERGENCE if below, "
            "STABILITY if inside. STABILITY is the prediction.",
    }))

    # ---- 4. doctrinal companions
    codes = {c: v for c, v in sorted(cp.items())
             if v.get("verdict") == "TOP_K_PERSISTENT"}
    prof = ca["loc_w500"]["phase5_8_9_profiles"]
    sets = {c: [r["source"] for r in prof[c]["top"][:3]]
            for c in codes if c in prof}
    out.append(dict(common, **{
        "forecast_id": f"companion_top3_sets@{CUTOFF}",
        "target_definition":
            "for each code below, the three non-statutory source identities "
            "most often attached to it in the court's voice within 500 "
            "characters, in the target quarter.",
        "model": "PERSISTENCE of the SET, not of the order. The backtest "
                 "separates them: the set holds, the ranking does not.",
        "prediction": {"frozenTop3": sets,
                       "expectedSetJaccard": {c: v["meanTopKJaccard"]
                                              for c, v in codes.items()},
                       "expectedTop1Held": {c: v["top1HeldShare"]
                                            for c, v in codes.items()},
                       "orderIsNotPredicted": True},
        "uncertainty": {"worstBacktestedJaccard": {c: v["worstTopKJaccard"]
                                                   for c, v in codes.items()},
                        "steps": {c: v["steps"] for c, v in codes.items()}},
        "baseline_prediction": "identical: the model IS the baseline",
        "scoring_rule": "per code, Jaccard(frozen top 3, observed top 3), and "
                        "separately whether the top-1 held. Abstain for any "
                        "code with fewer than 60 attached court mentions in "
                        "the target quarter (LOW_SUPPORT).",
    }))

    # ---- 5. retrieval ageing
    out.append(dict(common, **{
        "forecast_id": f"retrieval_coverage_h1@{CUTOFF}",
        "target_definition":
            "the share of the target quarter's court statutory citations "
            "whose (instrument, article) already appears in the frozen "
            "COURT_REASONING universe: every article the court cited anywhere "
            "in 1442Q1 to 1446Q2.",
        "model": "FROZEN_UNIVERSE_COVERAGE, backtested at horizon 1 over "
                 f"{rd['folds']} folds",
        "prediction": {"pointEstimate": rd["meanCoverage"]["COURT_REASONING"],
                       "alsoPredicted": {
                           "WHOLE_JUDGMENT":
                               rd["meanCoverage"]["WHOLE_JUDGMENT"],
                           "STATUTE_ONLY_TOP50":
                               rd["meanCoverage"]["STATUTE_ONLY_TOP50"]},
                       "orderingClaim":
                           "WHOLE_JUDGMENT at least COURT_REASONING, and both "
                           "above STATUTE_ONLY_TOP200, which is above "
                           "STATUTE_ONLY_TOP50"},
        "uncertainty": {"worstBacktestedFold":
                        rd["worstCoverage"]["COURT_REASONING"]},
        "baseline_prediction": rd["meanCoverage"]["STATUTE_ONLY_TOP50"],
        "scoring_rule": "absolute error on the point estimate, and whether "
                        "the ordering claim holds. The ordering is the part "
                        "worth being wrong about: it is the claim that a "
                        "retrieval universe should be built from what the "
                        "whole judgment cites, not from the operational core.",
    }))
    return out


def conditionals():
    """Scored ONLY if the registry's threshold is met and observable."""
    ab = J("ai_baseline_results.json")
    c = ab["C_doctrinalDiversity"]["corpusNamedFiqhShareOfFiqhTrailingYear"]
    a = ab["A_statutoryUse"]["courtArticleHHI"]
    return [
        {"conditional_forecast_id": f"named_fiqh_under_research_ai@{CUTOFF}",
         "created_at": CREATED, "data_cutoff": CUTOFF, "status": "OPEN",
         "condition": "adoption_registry.json threshold T_RESEARCH_DEPLOYED "
                      "is met, with all qualifying events dated before the "
                      "forecast window",
         "target_definition": "named fiqh as a share of all court fiqh "
                              "mentions, corpus-wide, trailing four quarters",
         "baseline_at_cutoff": c,
         "prediction": "an INCREASE of at least 5 percentage points against "
                       "the frozen baseline, sustained over four quarters",
         "direction_is_not_assumed":
             "the opposite is a live possibility and is stated as the "
             "falsifier: if source-resolving research tools are deployed and "
             "this share does not rise, the mechanism 'better retrieval makes "
             "citation more traceable' is wrong for this corpus.",
         "scoring_rule": "difference in percentage points against the frozen "
                         "baseline, with a same-length pre-window from the "
                         "baseline period as the comparison. SCORED only if "
                         "the condition is met; otherwise NEVER_TRIGGERED.",
         "confounders_to_record": ["a change in authority.py's vocabulary",
                                   "a change in the publisher's release mix",
                                   "new legislation displacing fiqh citation",
                                   "any judicial drafting guidance issued in "
                                   "the same window"]},
        {"conditional_forecast_id":
             f"article_concentration_under_research_ai@{CUTOFF}",
         "created_at": CREATED, "data_cutoff": CUTOFF, "status": "OPEN",
         "condition": "adoption_registry.json threshold T_RESEARCH_DEPLOYED "
                      "is met",
         "target_definition": "HHI of the court's article citations, trailing "
                              "four quarters",
         "baseline_at_cutoff": a,
         "prediction": "NO DIRECTION IS PREDICTED. Two mechanisms point "
                       "opposite ways and both are live: retrieval that "
                       "surfaces what is already cited concentrates "
                       "(homogenisation), retrieval that reaches the long "
                       "tail disperses. The forecast is that the ABSOLUTE "
                       "change exceeds 0.01, that is, that something moves.",
         "scoring_rule": "absolute change above 0.01 scores as MOVED; the "
                         "sign is recorded but was not predicted, and no "
                         "credit is taken for it.",
         "confounders_to_record": ["new legislation entering the core, as the "
                                   "Civil Transactions Law did in 1445",
                                   "publication mix", "docket composition"]},
    ]


def scenarios():
    return [{
        "scenario_id": "ctl_uptake_repeat",
        "not_a_forecast": "mechanical what-if. No scoring rule, no skill "
                          "statistic, never counted as right or wrong.",
        "assumption": "a future code enters the corpus with the same uptake "
                      "shape the Civil Transactions Law showed: first court "
                      "citation and first party citation in the same quarter, "
                      "top-100 two quarters later, top-50 the quarter after.",
        "mechanical_consequence": "such a code would displace roughly the "
                                  "number of articles the observed top-50 "
                                  "turnover already moves each quarter, so "
                                  "the operational core absorbs one new code "
                                  "without a visible break in its churn rate.",
        "why_this_is_not_a_forecast": "it assumes the event rather than "
                                      "predicting it, and the corpus contains "
                                      "exactly one such event, which is not a "
                                      "sample."}]


def main():
    new = build()
    if LEDGER.exists():
        old = json.loads(LEDGER.read_text(encoding="utf-8"))
    else:
        old = {"what": "Every forecast this repository has issued, kept "
                       "whether it aged well or badly. Entries are "
                       "append-only: a prediction is never edited after the "
                       "period it predicts becomes observable, and a failed "
                       "forecast is never deleted. Status moves from OPEN to "
                       "SCORED, VOID_DATA_SHIFT or VOID_TARGET_REDEFINED, and "
                       "nothing else in an entry changes, ever.",
               "forecasts": [], "conditionalForecasts": [], "scenarios": []}
    byid = {f["forecast_id"]: f for f in old["forecasts"]}
    if "--check" in sys.argv:
        moved = []
        for f in new:
            o = byid.get(f["forecast_id"])
            if o and json.dumps(o.get("prediction"), sort_keys=True) != \
                    json.dumps(f.get("prediction"), sort_keys=True):
                moved.append(f["forecast_id"])
        if moved:
            print("issued forecasts no longer reproduce from current results. "
                  "That is EXPECTED once the corpus grows, and the ledger "
                  "entry stands unchanged:")
            for b in moved:
                print(f"  {b}")
            return 0
        print(f"{len(byid)} issued forecast(s) still reproduce from the "
              f"current results")
        return 0
    added = []
    for f in new:
        if f["forecast_id"] not in byid:
            old["forecasts"].append(f)
            added.append(f["forecast_id"])
    have = {c["conditional_forecast_id"] for c in old["conditionalForecasts"]}
    for c in conditionals():
        if c["conditional_forecast_id"] not in have:
            old["conditionalForecasts"].append(c)
            added.append(c["conditional_forecast_id"])
    hs = {s["scenario_id"] for s in old["scenarios"]}
    for s in scenarios():
        if s["scenario_id"] not in hs:
            old["scenarios"].append(s)
    if "frozenTop50" not in old:
        import foresight as F
        rows, _d, _e = F.load()
        S = F.build(rows)
        last = S[F.P[-1]]["courtStat"]
        old["frozenTop50"] = [f"{i}:{a}" for i, a in F.top(last, 50)]
        old["frozenTop50Note"] = ("the court's 50 most cited articles in "
                                  "1446Q2, the set that "
                                  "operational_core_top50@1446Q2 predicts "
                                  "will still be the top 50 next period")
    old["ledgerHash"] = hashlib.sha256(json.dumps(
        old["forecasts"], sort_keys=True, ensure_ascii=False
    ).encode()).hexdigest()[:16]
    LEDGER.write_text(json.dumps(old, ensure_ascii=False, indent=1),
                      encoding="utf-8")
    print(f"{len(old['forecasts'])} forecast(s), "
          f"{len(old['conditionalForecasts'])} conditional, "
          f"{len(old['scenarios'])} scenario(s); added {len(added)}")
    for a in added:
        print(f"  + {a}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
