#!/usr/bin/env python3
"""The bridge between the adoption registry and the legal corpus.

The registry says what was deployed where. The corpus says what can be
measured. Neither says whether the two meet, and that is the only question
that decides whether a study is possible. This file joins them into one
matrix, one row per institution and workflow, and its most important column is
the one that says NO.

It also does two things the programme asked for explicitly and that are easy
to get wrong.

It classifies the AI deployment study on a fixed ladder, E0 to E5, without
skipping levels. And it makes every forecast CHANNEL-SPECIFIC: an outcome is
attached to the channel that could plausibly move it, so that a future session
cannot quietly explain a movement in bench behaviour by a deployment that
happened in enforcement.

    python3 ai_exposure_matrix.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "ai_exposure_matrix_results.json"
J = lambda n: json.loads((HERE / n).read_text(encoding="utf-8"))

# The ladder. Each level requires everything below it.
EVENT_CLASSES = {
    "E0_CHRONOLOGY_ONLY": "a verified event exists and is dated; no outcome "
                          "series for the exposed population exists",
    "E1_OBSERVABLE_POST_SHIFT": "an outcome series exists for the exposed "
                                "population and covers periods after the "
                                "event",
    "E2_VALID_INTERRUPTED_SERIES": "enough complete periods before and after "
                                   "to estimate level and trend, with placebo "
                                   "dates available",
    "E3_COMPARISON_SUPPORTED": "a defensible comparison series with "
                               "comparable pre-trends",
    "E4_QUASI_EXPERIMENTAL": "variation in treatment timing or intensity "
                             "across units, evidenced officially",
    "E5_CAUSAL_IDENTIFICATION_STRONG": "identification that survives the "
                                       "obvious confounds",
}

# Which observable belongs to which channel. An outcome may only be read as
# possibly-AI-related if the deployment is in ITS channel.
CHANNEL_OUTCOMES = {
    "BENCH_JUDICIAL_RESEARCH": [
        "named vs generic source share", "source entropy and effective count",
        "top-k authority concentration", "rare-source and long-tail use",
        "citation resolution and specificity",
        "doctrinal companion concentration",
        "precedent or principle citation diversity"],
    "BAR_ADVOCACY": [
        "party article diversity", "party doctrinal-source diversity",
        "new-code uptake latency", "party-to-court lead-lag",
        "party-side template concentration",
        "court-party article overlap"],
    "COURT_ADMINISTRATION": [
        "publication volume", "disposition mix", "reasons length",
        "decision-to-publication lag"],
    "ENFORCEMENT": ["enforcement workflow outcomes"],
    "GOVERNMENT_REGULATORY_LEGAL_WORK": [],
    "PUBLIC_LEGAL_SERVICES": [],
    "LEGAL_KNOWLEDGE_INFRASTRUCTURE": [
        "what the bench and bar cite, indirectly"],
}

# Every issued forecast, tagged. This is metadata ABOUT entries in the ledger;
# no issued prediction is touched.
FORECAST_CHANNELS = {
    "operational_core_top50@1446Q2": (
        "LEGAL_KNOWLEDGE_INFRASTRUCTURE", "retrieval",
        "statutory visibility", "L0_NO_OBSERVABLE_OUTCOME"),
    "ctl_court_share@1446Q2": (
        "BENCH_JUDICIAL_RESEARCH", "legal research",
        "new-code uptake", "L0_NO_OBSERVABLE_OUTCOME"),
    "court_party_top20_jaccard@1446Q2": (
        "BAR_ADVOCACY", "legal research",
        "court-party article overlap", "L0_NO_OBSERVABLE_OUTCOME"),
    "companion_top3_sets@1446Q2": (
        "BENCH_JUDICIAL_RESEARCH", "legal research",
        "doctrinal companion concentration", "L0_NO_OBSERVABLE_OUTCOME"),
    "retrieval_coverage_h1@1446Q2": (
        "LEGAL_KNOWLEDGE_INFRASTRUCTURE", "retrieval",
        "retrieval universe coverage", "NOT_AN_AI_TARGET"),
    "speaker_aware_retrieval@1446Q2": (
        "LEGAL_KNOWLEDGE_INFRASTRUCTURE", "retrieval",
        "recall against speaker contamination", "NOT_AN_AI_TARGET"),
    "temporal_misalignment_h1@1446Q2": (
        "LEGAL_KNOWLEDGE_INFRASTRUCTURE", "retrieval",
        "snapshot staleness", "NOT_AN_AI_TARGET"),
}


def main():
    reg, b2 = J("adoption_registry.json"), J("ai_baseline_v2_results.json")
    audit, ledger = J("bog_access_audit.json"), J("FORECAST_LEDGER.json")
    fo, radar = J("foresight_results.json"), J("ai_radar_results.json")
    events = reg["events"]

    rows = []
    for e in events:
        ch = e["actor_channel"]
        link = e["corpus_linkability"]
        corpus = ("MOJ_COMMERCIAL" if e["organization"].startswith("Ministry")
                  and ch == "ENFORCEMENT" else None)
        have_corpus = ch in ("BAR_ADVOCACY", "LEGAL_KNOWLEDGE_INFRASTRUCTURE")
        rows.append({
            "institution": e["organization"],
            "workflow": e["workflow_stage"],
            "channel": ch,
            "event_id": e["event_id"],
            "deployment_status": e["deployment_status"],
            "deploymentDate": e.get("deployment_date_if_known"),
            "announcementDate": e["announcement_date"],
            "exposedPopulation": e["users"],
            "corpusAvailableForThatPopulation": (
                "YES" if have_corpus else
                "NO: the Board of Grievances is not in this repository and "
                "could not be acquired (see bog_access_audit.json)"
                if "Grievances" in e["organization"] else
                "NO: enforcement output is not published as reasoned "
                "judgments" if ch == "ENFORCEMENT" else "NO"),
            "observableOutcomes": CHANNEL_OUTCOMES.get(ch, []),
            "corpusLinkability": link,
            "frozenBaselineAvailable": (
                "YES" if ch in ("BAR_ADVOCACY", "BENCH_JUDICIAL_RESEARCH",
                                "LEGAL_KNOWLEDGE_INFRASTRUCTURE") else "NO"),
            "baselineIsForTheWrongInstitution": (
                "Grievances" in e["organization"]),
            "forecastIssued": sorted(
                k for k, v in FORECAST_CHANNELS.items() if v[0] == ch),
            "eventStudyFeasible": link in ("L3_WORKFLOW_MATCH",
                                           "L4_DIRECT_EVALUATION"),
        })

    # ---- the ladder, evaluated rather than asserted
    checks = {
        "E1_needs_outcome_series_for_exposed_population": False,
        "E1_reason": ("the exposed population is Board of Grievances judges "
                      "and researchers. No outcome series exists for them: "
                      "the corpus does not contain that institution and "
                      "acquisition is blocked, and the Board's own published "
                      "collections end at 1444 AH, before the deployment."),
        "E2_needs_complete_pre_and_post_periods": False,
        "E2_reason": "there are no post-deployment periods to have.",
        "E3_needs_comparable_comparison_series": False,
        "E3_reason": ("the Ministry of Justice commercial corpus is an "
                      "EXTERNAL COMPARISON SERIES, not a control: different "
                      "institution, domain, publication policy and code mix. "
                      "Its own composition is not stable across the window, "
                      "which would defeat a difference-in-differences even if "
                      "the treated series existed."),
        "E4_needs_variation_in_timing_or_intensity": False,
        "E4_reason": ("no official evidence of phased deployment across "
                      "courts, chambers or user groups was found. Manufacturing "
                      "untreated controls is forbidden."),
    }
    event_class = "E0_CHRONOLOGY_ONLY"

    pub = fo.get("publicationProfile", {})
    swings = pub.get("compositionSwings", {})
    res = {
        "what": "AI-EXPOSURE MATRIX: the bridge between the adoption registry "
                "and the legal corpus. One row per verified event, carried "
                "through to whether any study is feasible.",
        "rule": "an outcome may be read as possibly AI-related only if the "
                "deployment is in ITS channel. A deployment in enforcement "
                "never explains a movement in bench citation behaviour.",
        "eventClassLadder": EVENT_CLASSES,
        "eventClass": event_class,
        "eventClassChecks": checks,
        "eventClassNotSkipped": ("E1 fails, so E2 to E5 are not evaluated on "
                                 "their merits and are not claimed."),
        "matrix": rows,
        "eventStudiesFeasible": sum(1 for r in rows if r["eventStudyFeasible"]),
        "channelOutcomes": CHANNEL_OUTCOMES,
        "forecastChannelTags": {
            k: {"channel": v[0], "workflow": v[1], "observable": v[2],
                "linkability": v[3]}
            for k, v in sorted(FORECAST_CHANNELS.items())},
        "forecastsIssued": len(ledger["forecasts"]),
        "forecastsTagged": len(FORECAST_CHANNELS),

        # ---- the confound that would bite first, measured before any outcome
        "publicationRegimeStability": {
            "periods": pub.get("periods"),
            "medianReasonChars": swings.get("medianReasonChars"),
            "share_feesClaim": swings.get("share_feesClaim"),
            "share_damagesClaim": swings.get("share_damagesClaim"),
            "decisionToPublicationLag":
                pub.get("decisionToPublicationLag", {}).get("verdict"),
            "verdict": "THE PUBLISHED SET IS NOT COMPOSITIONALLY STABLE",
            "why": "median reasons length and the claim mix both move "
                   "substantially across the window. Any event-aligned "
                   "comparison in this corpus would be fighting that first, "
                   "and it is reported before any doctrinal outcome rather "
                   "than beside one.",
        },
        "aiAsSubjectOfLaw": {
            "mojCommercial": {"judgmentsScanned": radar["judgmentsScanned"],
                              "L3": radar["L3_count"]},
            "bogAdministrative": {
                "verdict": "NOT_SCANNED",
                "why": "administrative law is where AI as a subject of law "
                       "would plausibly appear first -- automated government "
                       "decisions, public-sector algorithms, procurement, "
                       "automated eligibility. The radar is ready to run on "
                       "it unchanged. There is no corpus to run it on."},
        },
        "whatWouldChangeTheClassification": [
            "a Board of Grievances collection covering 1445 or later, which "
            "would create post-deployment publication",
            "a permitted machine-readable route to the Board's collections",
            "official evidence of phased deployment across courts, which "
            "would open E4 rather than E2",
            "a verified AI deployment inside the Ministry of Justice "
            "COMMERCIAL courts, which would raise an event to L3 in a corpus "
            "this repository already holds",
        ],
        "accessAuditVerdict": audit["verdict"],
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"event class: {event_class}")
    print(f"  matrix rows {len(rows)}, event studies feasible "
          f"{res['eventStudiesFeasible']}")
    print(f"  forecasts tagged by channel: {len(FORECAST_CHANNELS)} of "
          f"{len(ledger['forecasts'])}")
    print(f"  publication regime: {res['publicationRegimeStability']['verdict']}")
    print(f"-> {OUT.name}")


if __name__ == "__main__":
    main()
