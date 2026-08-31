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

    # ---- 6. the entrant forecast, the one target with a real signal
    hz = J("horizon_results.json")
    en = hz["phase4_5_entrants"]
    if en.get("frozenCandidateList"):
        best = en["bestFeature"]
        out.append(dict(common, **{
            "forecast_id": f"top50_entrants@{CUTOFF}",
            "target_definition":
                "which (instrument, article) pairs OUTSIDE the top 50 at "
                "1446Q2 enter the court's top 50 in the target quarter. "
                "Scored against the frozen ranked list below.",
            "model": f"rank candidates by {best}; the additive rule combining "
                     "three features scored WORSE "
                     f"({en['meanPrecisionAtNTrue']['combined']} against "
                     f"{en['meanPrecisionAtNTrue'][best]}) and is not used",
            "prediction": {
                "rankedCandidates": en["frozenCandidateList"],
                "expectedEntrantsInPeriod": hz["phase1_forecastabilityMap"] and
                    J("foresight_results.json")["articleVisibility"][
                        "meanNewEntrantsPerPeriod"],
                "expectedPrecisionAtNTrue": en["meanPrecisionAtNTrue"][best],
                "baseRate": en["meanBaseRate"],
                "difficultySplit": {
                    "meanNearBoundaryEntrants": en["meanNearBoundaryEntrants"],
                    "meanLongJumpEntrants": en["meanLongJumpEntrants"]}},
            "uncertainty": {"folds": en["folds"],
                            "worstFoldPrecision": en["worstFoldForBest"],
                            "note": "one backtest fold produced zero correct "
                                    "candidates. The signal is real on "
                                    "average and fails completely sometimes."},
            "baseline_prediction": en["meanBaseRate"],
            "scoring_rule":
                "precision at n, where n is the number of articles that "
                "actually entered. Report separately for NEAR_BOUNDARY and "
                "LONG_JUMP candidates: predicting an article ranked 52 into "
                "the top 50 is not the same achievement as predicting one "
                "ranked 300.",
        }))

    # ---- 5b. the speaker-aware correction
    sa = fs["speakerAwareRetrieval"]
    mis = fs["temporalMisalignment"]["h1"]
    out.append(dict(common, **{
        "forecast_id": f"speaker_aware_retrieval@{CUTOFF}",
        "target_definition":
            "over the target quarter, for a universe frozen at 1446Q2: the "
            "size of the party-only remainder as a percentage of the court's "
            "own universe, the coverage it adds, and the share of it the "
            "court actually cites.",
        "model": "backtested over 13 rolling folds",
        "prediction": {"universeGrowthPct": sa["meanUniverseGrowthPct"],
                       "coverageAddedByPartyOnly":
                           sa["meanCoverageAddedByPartyOnly"],
                       "partyOnlyPrecision": sa["meanPartyOnlyPrecision"],
                       "claim": "high recall costs more than it buys: the "
                                "party-only remainder grows the index by "
                                "about two fifths and adds well under a "
                                "point of coverage"},
        "uncertainty": {"folds": sa["folds"],
                        "coveragePointsPer10pctUniverseGrowth":
                            sa["coveragePointsPer10pctUniverseGrowth"]},
        "baseline_prediction": "no growth, no added coverage",
        "scoring_rule": "absolute error on each of the three quantities. The "
                        "claim scores as HELD if universe growth exceeds 25 "
                        "per cent while added coverage stays below 2 points.",
    }))
    out.append(dict(common, **{
        "forecast_id": f"temporal_misalignment_h1@{CUTOFF}",
        "target_definition":
            "for the universe and ranking frozen at 1446Q2, measured on the "
            "target quarter: the share of court citations going to articles "
            "the snapshot never saw, and the share of its top 50 no longer in "
            "the observed top 50.",
        "model": "backtested over 13 rolling folds at horizon 1",
        "prediction": {
            "citationShareToNeverSeenArticles":
                mis["meanCitationShareToNeverSeenArticles"],
            "top50DisplacedPct": mis["meanTop50DisplacedPct"],
            "claim": "recall ages slowly and RANKING ages fast: a snapshot "
                     "one quarter old still contains almost everything and "
                     "already orders about a third of its core wrongly"},
        "uncertainty": {"folds": mis["folds"],
                        "meanRankDisplacementTop200":
                            mis["meanRankDisplacementTop200"]},
        "baseline_prediction": "no displacement",
        "scoring_rule": "absolute error on both quantities; the claim scores "
                        "as HELD if displacement exceeds the never-seen share "
                        "by more than a factor of three.",
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


SCORABLE = {
    "what": "A quarter is SCORABLE only when it is mature enough that a miss "
            "measures the forecast rather than the publisher. Defined here, "
            "before any outcome is observable, and not revised afterwards.",
    "criteria": [
        "at least 800 judgments carrying court authority in that quarter",
        "at least 200 court statutory citations in that quarter",
        "the quarter is followed by at least one further quarter in the "
        "rebuilt corpus, so that its own publication is demonstrably "
        "complete rather than still arriving",
        "the quarter's judgment count is at least 40 per cent of the median "
        "of the four quarters preceding it, which catches a collapse in "
        "release volume that is not publication lag",
    ],
    "forbidden": "the outcome itself may never be used to decide maturity. A "
                 "quarter is not declared unscorable because the forecast "
                 "missed in it.",
    "ifNeverScorable": "a forecast whose target period never becomes SCORABLE "
                       "by 1449Q4 is closed as VOID_DATA_SHIFT, not scored "
                       "and not deleted.",
}

REVIEW = {
    "operational_core_top50@1446Q2": {
        "verdict": "KEEP",
        "why": "definition and scoring rule were valid before any outcome "
               "was observable, and remain so.",
    },
    "ctl_court_share@1446Q2": {
        "verdict": "KEEP",
        "why": "the one new code the corpus contains; a large miss is more "
               "informative than a hit and the entry says so.",
    },
    "court_party_top20_jaccard@1446Q2": {
        "verdict": "KEEP",
        "why": "valid as defined. Its interpretation is now sharper: this is "
               "the one channel-1 observable, and the registry records no "
               "verified advocacy-side deployment, so a move in it would need "
               "an explanation other than AI.",
    },
    "companion_top3_sets@1446Q2": {
        "verdict": "KEEP",
        "why": "the backfill added folds and did not move the verdict: the "
               "set persists, the order does not.",
    },
    "retrieval_coverage_h1@1446Q2": {
        "verdict": "REFRAME",
        "why": "NOT void: the target was defined, backtested and scoreable "
               "before any outcome, and voiding it because its reading was "
               "wrong would be exactly the move the ledger forbids. What was "
               "wrong was the gloss placed on it in the report. Coverage is "
               "RECALL. The speaker programme established that a whole "
               "judgment carries substantial advocacy and recital material, "
               "so a whole-judgment universe buys recall with contamination. "
               "The entry stands and is scored as written; "
               "speaker_aware_retrieval@1446Q2 now carries the question the "
               "gloss should have asked.",
        "supersededInterpretation":
            "the claim that a retrieval universe should be built from what "
            "the whole judgment cites is WITHDRAWN. The measurement that "
            "withdrew it: the party-only remainder grows the universe by 40.6 "
            "per cent, adds 0.64 coverage points, and 90 per cent of what it "
            "adds the court never cites.",
    },
}

WATCH = [
    {"watch_target_id": "first_ai_legal_issue@1446Q2",
     "not_a_forecast": "a watch target carries no probability and never "
                       "enters a skill statistic. Forcing a probability onto "
                       "a rare emerging event would be false precision.",
     "definition": "the first judgment in this corpus at LEVEL 3 of "
                   "ai_radar.py: an artificial-intelligence or algorithmic "
                   "feature materially part of the legal question.",
     "baselineAtCutoff": "0 of 50,666 judgments scanned",
     "recordOnOccurrence": ["judgment identifier and date", "the court's own "
                            "words, quoted", "which concept family matched",
                            "the codes cited beside it", "whether it appears "
                            "in the court's voice or a party's",
                            "whether the AI feature is the claim, the "
                            "defence, the evidence, or the reasoning"],
     "escalationRule": "one L3 judgment is an occurrence. Three in one year, "
                       "or two under one code, is a FAMILY and earns its own "
                       "measurement; below that it stays a watch target."},
    {"watch_target_id": "first_ai_generated_evidence@1446Q2",
     "not_a_forecast": "as above",
     "definition": "the first judgment where material said to be produced by "
                   "an automated or generative system is offered as, or "
                   "challenged as, evidence.",
     "baselineAtCutoff": "0; the generated.content family has no L3 match",
     "recordOnOccurrence": ["how the court treats it under the Evidence Law",
                            "which Evidence Law article is cited beside it",
                            "whether any non-statutory authority is attached"],
     "whyThisOneMatters": "the Evidence Law is the code whose doctrinal "
                          "companions this repository can measure best, so an "
                          "AI-evidence issue is the single most measurable "
                          "form the subject-of-law question could take."},
    {"watch_target_id": "verified_moj_commercial_ai_deployment@1446Q2",
     "not_a_forecast": "as above",
     "definition": "the first verified, officially sourced AI deployment in "
                   "the Ministry of Justice COMMERCIAL courts, as opposed to "
                   "enforcement or the Board of Grievances.",
     "baselineAtCutoff": "none found; every verified judicial deployment is "
                         "in an institution this corpus does not contain",
     "whyThisOneMatters": "it is the only event that would raise any registry "
                          "entry to L3_WORKFLOW_MATCH and make a "
                          "before-and-after comparison meaningful at all."},
]


def tournament():
    """F0 to F3, frozen together, scored identically, never edited."""
    fs = J("foresight_results.json")
    sc = fs["scalarTargets"]["civilTransactionsLawShareOfCourtCitations"]
    last = sc["series"][CUTOFF]
    vals = [v for v in sc["series"].values() if v is not None]
    return {
        "what": "CAN AN AI FORECASTER BEAT PERSISTENCE AT SAUDI "
                "LAW-IN-ACTION? Four forecasters, frozen together, scored by "
                "the same rule, on targets whose outcomes none of them has "
                "seen.",
        "leakageRule":
            "F3 is a reasoned forecast produced by a language model. A "
            "language model cannot be backtested on a period inside its own "
            "training data, and the target quarter immediately after this "
            "cutoff falls inside it. So F3 is issued ONLY for hijri 1449, "
            "which begins well after the assistant's knowledge cutoff. F0 to "
            "F2 are mechanical and are issued for both horizons.",
        "targets": [
            {"target_id": "ctl_court_share@1449",
             "definition": "the share of the court's statutory citations "
                           "naming the Civil Transactions Law, over the four "
                           "SCORABLE quarters of hijri 1449",
             "F0_BASELINE": {"model": "LAST", "prediction": last},
             "F1_STATISTICAL": {"model": "mean of the four quarters since the "
                                         "code became visible",
                                "prediction": round(sum(vals[-4:]) / 4, 5)},
             "F2_RULE_BASED": {
                 "model": "an uptake rule read off the one observed arrival: "
                          "a new code rises for about four quarters after "
                          "reaching the operational core and then plateaus",
                 "prediction": "plateau: between 0.06 and 0.12, no further "
                               "step change"},
             "F3_AI_REASONED": {
                 "model": "reasoned forecast, issued once, never edited",
                 "prediction": 0.10,
                 "interval": [0.06, 0.16],
                 "probabilityAbove0_12": 0.35,
                 "reasoningAtCutoff":
                     "The Civil Transactions Law is a general civil code "
                     "displacing uncodified fiqh reasoning in exactly the "
                     "contract and damages disputes that dominate this "
                     "corpus, so its ceiling is higher than the plateau the "
                     "first six quarters show. Against that: the Commercial "
                     "Courts Law and its regulation carry the procedural "
                     "spine of every commercial judgment and will not be "
                     "displaced, the observed share already flattened between "
                     "1446Q1 and 1446Q2, and the bar cites the code two to "
                     "three times more heavily than the bench without the "
                     "bench following, which is evidence against rapid "
                     "further adoption. Net: continued slow rise rather than "
                     "a plateau, but well short of the procedural codes.",
                 "evidenceAvailableAtCutoff": [
                     "the six-quarter uptake curve, 0.00155 to 0.07743",
                     "party share running 2 to 3 times court share",
                     "no lead-lag association above court persistence",
                     "49 distinct CTL articles cited by the court at peak"],
                 "immutable": True},
             "scoring_rule": "absolute error against the observed share, "
                             "identical for all four; interval coverage "
                             "recorded for F3 separately; no forecaster is "
                             "called skilled until scored."},
        ],
        "F3_notIssuedFor": "every other target. One reasoned forecast that "
                           "can be scored cleanly is worth more than five "
                           "that cannot.",
    }


PREREGISTRATION = {
    "id": "bog_judicial_research_ai@preregistered",
    "what": "A preregistered analysis plan for the Board of Grievances "
            "judicial-research AI deployment, frozen BEFORE any data exists. "
            "It is not a forecast and carries no probability; it is the set "
            "of choices that would otherwise be made after seeing the answer.",
    "status": "DORMANT_AWAITING_DATA",
    "triggerConditions": [
        "a Board of Grievances judgment collection covering 1445 AH or later "
        "is published, creating post-deployment observations",
        "AND a permitted, machine-readable acquisition route exists, or the "
        "publisher grants one",
        "AND decision dates are present and classified DATE_VALID",
    ],
    "designName": "EVENT_ALIGNED_OBSERVATIONAL_DESIGN",
    "designNameRule": "the phrase 'natural experiment' is not used, and the "
                      "word 'caused' is not used, unless the event class "
                      "reaches E4 with variation in treatment timing "
                      "evidenced officially.",
    "exposure": {
        "population": "Board of Grievances judges and judicial researchers",
        "treatmentIsNotBinary": "the registry records an event VERSION "
                                "sequence: partnership (2024-03), deployed "
                                "and awarded (2024), governance policy "
                                "(2026). Treatment intensity changes at each, "
                                "and the analysis aligns on the DEPLOYMENT "
                                "date where verified, not the announcement.",
        "unverified": "how many judges used it, how often, in which courts, "
                      "and whether use was optional or integrated. None of "
                      "that is established by any source we could read, so "
                      "exposure is institution-level and is labelled that way.",
    },
    "primaryOutcomes": [
        "named vs generic source share",
        "source entropy and effective number of sources",
        "top-1, top-3 and top-5 authority concentration",
        "rare-source and long-tail authority use",
        "new source entrants and entrant survival",
        "citation resolution and article specificity",
        "doctrinal companion set persistence and concentration",
        "precedent or principle citation diversity, if identities are exposed",
        "source-template concentration",
    ],
    "outcomesDeliberatelyExcluded": [
        "disposition and outcome mix: not in the deployed workflow",
        "reasons length on its own: it moves with publication policy",
        "anything about an individual judge",
        "anything inferred from writing style",
    ],
    "competingHypotheses": {
        "HOMOGENISATION": {
            "mechanism": "retrieval surfaces the same top-ranked sources "
                         "repeatedly",
            "predicts": ["authority HHI rises", "source entropy falls",
                         "top-k concentration rises",
                         "source and template reuse rises"]},
        "DISCOVERY": {
            "mechanism": "retrieval lowers the cost of reaching the long tail",
            "predicts": ["source entropy rises", "rare-source use rises",
                         "new source entrants rise",
                         "top-k dominance falls"]},
        "TRACEABILITY": {
            "mechanism": "assisted lookup makes a citation resolvable",
            "predicts": ["named source share rises",
                         "generic and unresolved authority falls"]},
        "NULL": {
            "mechanism": "no measurable discontinuity beyond the existing "
                         "trend and the publication composition",
            "predicts": ["no level shift and no trend change survives the "
                         "placebo dates"]},
        "noneIsPrivileged": "HOMOGENISATION and DISCOVERY predict opposite "
                            "signs on the same statistics. TRACEABILITY is "
                            "orthogonal to both and can move with either. "
                            "NULL is a live outcome and is not a failure.",
    },
    "specification": {
        "model": "segmented series: baseline level, pre-event trend, "
                 "post-event level shift, post-event trend change",
        "granularity": "quarterly, and monthly only if volume supports it. "
                       "Sparse periods are not segmented.",
        "eventWindows": ["sharp date", "plus or minus one quarter",
                         "plus or minus two quarters"],
        "windowRule": "if the conclusion depends on one exact announcement "
                      "day, it is reported as weak.",
        "placebo": "event dates drawn from every pre-period quarter. If many "
                   "placebo dates reproduce the result, the event reading is "
                   "weakened and that is reported, not buried.",
        "confoundsCheckedFirst": [
            "publication volume and selection", "decision-to-publication lag "
            "if both dates ever exist", "text-length composition",
            "case-type composition", "court composition", "pre-trend",
            "other reforms in the window", "extraction-method changes"],
        "reportingRule": "with no credible counterfactual the language is "
                         "POST-DEPLOYMENT SHIFT, TEMPORAL ASSOCIATION or "
                         "EVENT-ALIGNED CHANGE. Never causal effect.",
    },
    "comparisonSeries": {
        "series": "Ministry of Justice commercial judgments, this repository's "
                  "existing corpus",
        "label": "EXTERNAL COMPARISON SERIES",
        "notAControl": "different institution, domain, publication policy and "
                       "code mix. Difference-in-differences is permitted only "
                       "if pre-trends and measurement comparability are "
                       "demonstrated first; otherwise side-by-side trends only.",
        "knownProblem": "the comparison series is not compositionally stable "
                        "across the observed window, which is measured in "
                        "foresight_results.json publicationProfile.",
    },
    "transportTestsToRunFirst": [
        "statutory citation detection", "article resolution",
        "non-statutory authority detection", "source identity resolution",
        "named vs generic fiqh", "traceability components",
        "section and speaker structure, only if the documents support it"],
    "transportRule": "if the documents do not separate voices with "
                     "confidence, NO speaker labels are produced. "
                     "Decision-level authority use, source traceability, "
                     "concentration, identity and template concentration are "
                     "measured instead. The science follows observability.",
}


def horizon_release():
    """The first Horizon release: one forecast, five detectors, five watch
    targets, and two competing AI hypotheses that are not forecasts."""
    hz, det = J("horizon_results.json"), J("detectors_results.json")
    en = hz["phase4_5_entrants"]
    fam = det["phase16_17_18_composites"]
    D = det["detectors"]

    detectors = []
    for m in ("courtArticleHHI", "namedFiqhShareOfFiqh",
              "commercial_courts_law::namedShare",
              "evidence_law::entropy",
              "commercial_courts_implementing_regulation::topSourceShare"):
        d = D.get(m, {})
        detectors.append({
            "detector_id": f"{m}@{CUTOFF}",
            "metric": m,
            "contract": det["contract"],
            "baselineAtCutoff": next(
                (s.get("baseline") for s in reversed(d.get("byPeriod", []))
                 if s.get("baseline") is not None), None),
            "spreadAtCutoff": next(
                (s.get("spread") for s in reversed(d.get("byPeriod", []))
                 if s.get("spread") is not None), None),
            "historicalAlarmRate": d.get("alarmRatePerEvaluablePeriod"),
            "stateAtCutoff": d.get("currentState"),
            "evaluation": "a future SCORABLE quarter updates the detector. A "
                          "SIGNAL is recorded in SURPRISE_LEDGER.json with no "
                          "explanation attached; the explanation is sought "
                          "afterwards and may never be found.",
            "status": "ARMED"})

    watch = [
        {"watch_id": f"first_ai_legal_issue@{CUTOFF}",
         "definition": "the first LEVEL 3 judgment in ai_radar.py",
         "baseline": "0 of 50,666", "probability": None,
         "why": "forcing a probability onto a rare emerging event is false "
                "precision"},
        {"watch_id": f"bog_post_deployment_corpus@{CUTOFF}",
         "definition": "an official Board of Grievances collection covering "
                       "1445 AH or later",
         "baseline": "latest published collection covers 1444 AH",
         "probability": None,
         "why": "the single condition that converts the AI study from E0 to "
                "E1"},
        {"watch_id": f"moj_commercial_ai_deployment@{CUTOFF}",
         "definition": "a verified AI deployment in MoJ commercial courts",
         "baseline": "none found", "probability": None,
         "why": "the only condition that would produce an L3 event in a "
                "corpus already held"},
        {"watch_id": f"new_major_code@{CUTOFF}",
         "definition": "a new instrument's first court citation in a SCORABLE "
                       "quarter",
         "baseline": "the Civil Transactions Law: 2 quarters from first court "
                     "citation to the top 50",
         "probability": None,
         "why": "the uptake monitor needs an arrival to profile"},
        {"watch_id": f"parser_era_change@{CUTOFF}",
         "definition": "a change to authority.py or companions.py that alters "
                       "what counts as an authority",
         "baseline": "current era hash in the freshness stamp",
         "probability": None,
         "why": "every traceability detector must stop at that boundary "
                "rather than stitch across it"},
    ]

    hyp = [
        {"hypothesis_id": "H_AI_HOMOGENISATION",
         "notAForecast": "a competing hypothesis. No point is scored for "
                         "holding both; the future adjudicates.",
         "statement": "after a verified research-AI deployment in a workflow "
                      "this repository observes, article and source "
                      "concentration moves ABOVE the frozen detector bounds",
         "wouldShowAs": fam["AI_HOMOGENISATION"]["metrics"]
                        if "metrics" in fam["AI_HOMOGENISATION"] else
                        [m["metric"] for m in fam["AI_HOMOGENISATION"]["members"]],
         "requires": fam["AI_HOMOGENISATION"]["requires"],
         "stateAtCutoff": fam["AI_HOMOGENISATION"]["state"]},
        {"hypothesis_id": "H_AI_DISCOVERY",
         "notAForecast": "as above, and it predicts the opposite sign",
         "statement": "the same deployment instead moves long-tail and "
                      "entropy measures above the frozen bounds",
         "wouldShowAs": [m["metric"]
                         for m in fam["AI_DISCOVERY"]["members"]],
         "requires": fam["AI_DISCOVERY"]["requires"],
         "stateAtCutoff": fam["AI_DISCOVERY"]["state"]},
    ]
    return {
        "release": "HORIZON_1",
        "cutoff": CUTOFF,
        "created_at": CREATED,
        "rule": "every future metric is FORECAST, DETECT or WATCH. Nothing is "
                "forced into a probability model.",
        "counts": {"forecasts": 1, "detectors": len(detectors),
                   "watchTargets": len(watch),
                   "competingHypotheses": len(hyp)},
        "detectors": detectors,
        "watchTargets": watch,
        "competingAiHypotheses": hyp,
        "entrantForecastSummary": {
            "bestFeature": en.get("bestFeature"),
            "meanPrecisionAtNTrue": en.get("meanPrecisionAtNTrue", {}).get(
                en.get("bestFeature")),
            "meanBaseRate": en.get("meanBaseRate"),
            "worstFold": en.get("worstFoldForBest")},
    }


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
    old["scorableQuarter"] = SCORABLE
    if "preregistrations" not in old:
        old["preregistrations"] = []
    if not any(x["id"] == PREREGISTRATION["id"]
               for x in old["preregistrations"]):
        old["preregistrations"].append(PREREGISTRATION)
    old["bogForecastFeasibility"] = {
        "verdict": "INFEASIBLE",
        "why": "no Board of Grievances data exists in this repository and "
               "none could be lawfully acquired. A forecast needs a series to "
               "forecast from.",
        "whatWouldMakeItFeasible": "any complete Board period at all, at "
                                   "which point the targets are already "
                                   "specified in the preregistration above.",
    }
    old["reviewOfIssuedForecasts"] = REVIEW
    if "watchTargets" not in old:
        old["watchTargets"] = WATCH
    if "forecasterTournament" not in old:
        old["forecasterTournament"] = tournament()
    if "horizonRelease" not in old:
        old["horizonRelease"] = horizon_release()
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
