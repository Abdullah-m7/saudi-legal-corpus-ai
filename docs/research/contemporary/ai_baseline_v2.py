#!/usr/bin/env python3
"""Was the AI-transition baseline a pre-adoption baseline? No.

`ai_baseline.py` froze the measurable state of the corpus at 1446Q2 and called
it an AI-transition baseline rather than a pre-AI baseline, on the reasoning
that legal AI already exists somewhere in Saudi practice and this repository
does not know where. That reasoning was right and the follow-through was
wrong: the adoption registry was left empty, which made an unexamined baseline
look like a clean one.

A bounded search of official Saudi sources found seven events. Three of them
PRECEDE the cutoff. So this file adds the interpretive layer the frozen
baseline needs: for each of seven entry channels, what verified AI activity
was already underway when the baseline was taken, and -- separately, because
they are different questions -- whether this corpus could observe it.

The frozen baseline is not touched. Nothing here rewrites a number; this is
metadata about what those numbers were measured on top of.

    python3 ai_baseline_v2.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "ai_baseline_v2_results.json"
MAP = HERE / "ai_transition_map.json"
J = lambda n: json.loads((HERE / n).read_text(encoding="utf-8"))

# 1446Q2 runs approximately 4 October to 31 December 2024.
CUTOFF_GREGORIAN = "2024-12-31"

# The seven channels through which AI can enter legal work. The correction
# this file exists to make is that the programme's earlier writing treated
# channel 1 as the path, and it is one path of seven.
CHANNELS = {
    "BAR_ADVOCACY": "legal research, drafting, source discovery, case "
                    "preparation by advocates",
    "BENCH_JUDICIAL_RESEARCH": "precedent and legislation retrieval, case "
                               "similarity, judicial knowledge systems, "
                               "decision support",
    "COURT_ADMINISTRATION": "case classification, triage, workflow, "
                            "scheduling, document processing",
    "ENFORCEMENT": "automated execution workflow, verification, "
                   "classification, settlement support",
    "GOVERNMENT_REGULATORY_LEGAL_WORK": "government legal research, "
                                        "administrative adjudication, "
                                        "compliance, regulatory analysis",
    "PUBLIC_LEGAL_SERVICES": "public-facing assistance and settlement tools",
    "LEGAL_KNOWLEDGE_INFRASTRUCTURE": "search engines, retrieval systems, "
                                      "legal databases, doctrinal retrieval",
}
# Which channels this corpus -- published Ministry of Justice commercial
# judgments -- could ever observe an effect in. This is the sentence the
# registry exists to make sayable.
OBSERVABLE = {
    "BAR_ADVOCACY": ("PARTIALLY: party citations are visible where the "
                     "publisher reproduces them, at two speaker "
                     "specifications"),
    "BENCH_JUDICIAL_RESEARCH": ("YES IN PRINCIPLE for MoJ commercial courts, "
                                "NO for the Board of Grievances, whose "
                                "judgments are not in this corpus and where "
                                "every verified judicial deployment is"),
    "COURT_ADMINISTRATION": ("BARELY: publication timing and disposition mix "
                             "are confounded with the publisher's own "
                             "release policy"),
    "ENFORCEMENT": "NO: enforcement output is not in this corpus",
    "GOVERNMENT_REGULATORY_LEGAL_WORK": "NO",
    "PUBLIC_LEGAL_SERVICES": "NO",
    "LEGAL_KNOWLEDGE_INFRASTRUCTURE": ("INDIRECTLY: only through what the "
                                       "bench and bar cite"),
}
RANK = {"NO_VERIFIED_EVENT": 0, "DISCUSSION_ONLY": 1, "TRAINING": 2,
        "PARTNERSHIP": 3, "GOVERNANCE": 4, "PILOT": 5, "DEPLOYED": 6,
        "EXPANDED": 7}
STATUS_FROM_EVENT = {"DISCUSSION": "DISCUSSION_ONLY", "TRAINING": "TRAINING",
                     "PARTNERSHIP": "PARTNERSHIP", "GOVERNANCE": "GOVERNANCE",
                     "PILOT": "PILOT", "DEPLOYED": "DEPLOYED",
                     "EXPANDED": "EXPANDED", "PLANNED": "DISCUSSION_ONLY",
                     "UNKNOWN": "NO_VERIFIED_EVENT"}


def main():
    reg = J("adoption_registry.json")
    radar = J("ai_radar_results.json")
    base = json.loads((HERE / "frozen" / "ai_transition_baseline.json")
                      .read_text(encoding="utf-8"))
    events = reg["events"]

    channels = {}
    for ch, desc in sorted(CHANNELS.items()):
        mine = [e for e in events if e["actor_channel"] == ch]
        before = [e for e in mine if e["relation_to_baseline_cutoff"] == "BEFORE"]
        after = [e for e in mine if e["relation_to_baseline_cutoff"] == "AFTER"]

        def status(es):
            if not es:
                return "NO_VERIFIED_EVENT"
            return max((STATUS_FROM_EVENT.get(e["deployment_status"],
                                              "NO_VERIFIED_EVENT")
                        for e in es), key=lambda k: RANK[k])
        channels[ch] = {
            "description": desc,
            "statusAtBaselineCutoff": status(before),
            "statusNow": status(mine),
            "eventsBeforeCutoff": [e["event_id"] for e in before],
            "eventsAfterCutoff": [e["event_id"] for e in after],
            "bestLinkability": (max((e["corpus_linkability"] for e in mine),
                                    default="L0_NO_OBSERVABLE_OUTCOME")),
            "observableInThisCorpus": OBSERVABLE[ch],
        }

    started = [c for c, v in channels.items()
               if RANK[v["statusAtBaselineCutoff"]] >= RANK["PILOT"]]
    linkable = [e["event_id"] for e in events
                if e["corpus_linkability"] in ("L3_WORKFLOW_MATCH",
                                               "L4_DIRECT_EVALUATION")]

    res = {
        "what": "AI-TRANSITION BASELINE v2: an interpretive layer over the "
                "frozen baseline, saying what AI activity was already "
                "underway when it was taken.",
        "doesNotModify": "frozen/ai_transition_baseline.json is untouched. No "
                         "number in it is restated, corrected or replaced "
                         "here.",
        "baselineCutoff": base["dataCutoff"],
        "baselineCutoffGregorianApprox": CUTOFF_GREGORIAN,
        "verdict": (
            "THE BASELINE IS NOT A PRE-ADOPTION BASELINE. A judicial "
            "legal-research AI was already deployed in a Saudi court, and a "
            "cross-government generative-AI principles document was already "
            "in force, before the cutoff. What makes the baseline still "
            "usable is a different fact: the court in question is the Board "
            "of Grievances, whose judgments are not in this corpus, and no "
            "verified AI deployment was found in the Ministry of Justice "
            "commercial courts that this corpus does observe."),
        "channelsWithAdoptionAlreadyUnderwayAtCutoff": sorted(started),
        "channels": channels,
        "eventCounts": {
            "total": len(events),
            "byDeploymentStatus": dict(sorted(Counter(
                e["deployment_status"] for e in events).items())),
            "byCorpusLinkability": dict(sorted(Counter(
                e["corpus_linkability"] for e in events).items())),
            "beforeCutoff": sum(1 for e in events
                                if e["relation_to_baseline_cutoff"] == "BEFORE"),
        },
        "eventsSupportingACausalEventStudy": linkable,
        "causalPosition": (
            "NONE. No event reaches L3_WORKFLOW_MATCH, so no before-and-after "
            "comparison in this repository can be given a causal reading, and "
            "none is attempted. The registry's value today is chronology, "
            "channel identification, and an anchor for measurement that "
            "becomes possible only if a deployment ever lands in the workflow "
            "this corpus observes."),

        # ---- AI as a subject of law, frozen at zero
        "aiAsSubjectOfLaw": {
            "judgmentsScanned": radar["judgmentsScanned"],
            "L3_AI_LEGAL_ISSUE": radar["L3_count"],
            "L2_AI_RELEVANT_TECHNOLOGY": radar["byLevel"].get("L2", 0),
            "L1_EXPLICIT_AI_REFERENCE": radar["byLevel"].get("L1", 0),
            "CONTEXT_only": radar["byLevel"].get("CONTEXT", 0),
            "firstL3": radar["firstL3"],
            "frozenZero": (
                "As of this cutoff, across %s published judgments, this "
                "repository finds ZERO judgments in which an artificial "
                "intelligence or algorithmic feature is materially part of "
                "the legal question. That zero is the measurement: the first "
                "entry is only detectable against a recorded absence."
                % f"{radar['judgmentsScanned']:,}"),
            "recallLimit": radar["method"]["recall"],
            "whatWouldCountAsAChange": [
                "any L3 judgment at all, which is a FIRST_ENTRY event",
                "L3 appearing in more than one year, which is persistence",
                "L3 appearing under more than one code, which is domain spread",
                "an L3 family recurring with its own statutory companions, "
                "which is the beginning of doctrine",
            ],
        },
        "fourRolesOfAI": {
            "ACTOR": "AI changes how legal work is done. Registry + channels "
                     "above. Currently unobservable in this corpus.",
            "SUBJECT": "AI generates disputes and doctrine. ai_radar.py. "
                       "Currently zero.",
            "FORECASTER": "AI systems predict legal patterns. "
                          "FORECAST_LEDGER.json forecaster tournament. "
                          "Currently unscored by construction.",
            "FEEDBACK": "AI retrieval changes what humans cite, which changes "
                        "future retrieval. THEORY_LOG.md H1. First link "
                        "currently absent.",
            "rule": "these four are never mixed. A finding about one is not "
                    "evidence about another.",
        },
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1),
                   encoding="utf-8")

    # ------------------------------------------- the AI-LAW TRANSITION MAP
    # One row per verified event, carried all the way through to whether this
    # repository could ever score anything about it. The column that matters
    # most is the one that says no.
    fs = J("foresight_results.json")
    ledger = J("FORECAST_LEDGER.json")
    OBSERVABLES = {
        "BENCH_JUDICIAL_RESEARCH": [
            "named vs generic fiqh share", "source diversity and entropy",
            "citation concentration", "rare authority discovery",
            "doctrinal companion concentration"],
        "BAR_ADVOCACY": [
            "party article diversity", "party doctrinal-source diversity",
            "new-code uptake latency", "party to court lead-lag",
            "party-side template concentration"],
        "COURT_ADMINISTRATION": [
            "disposition mix", "reasons length", "publication timing"],
        "ENFORCEMENT": ["enforcement workflow outcomes"],
        "GOVERNMENT_REGULATORY_LEGAL_WORK": ["none in this corpus"],
        "PUBLIC_LEGAL_SERVICES": ["none in this corpus"],
        "LEGAL_KNOWLEDGE_INFRASTRUCTURE": [
            "what the bench and bar cite, indirectly"],
    }
    BASELINE_KEY = {
        "BENCH_JUDICIAL_RESEARCH": "C_doctrinalDiversity, D_traceability",
        "BAR_ADVOCACY": "B_courtVsBar, G_uptakeVelocity",
        "COURT_ADMINISTRATION": "none frozen; the publisher confounds it",
        "ENFORCEMENT": "none: outcome not in this corpus",
        "GOVERNMENT_REGULATORY_LEGAL_WORK": "none",
        "PUBLIC_LEGAL_SERVICES": "none",
        "LEGAL_KNOWLEDGE_INFRASTRUCTURE": "A_statutoryUse",
    }
    rows = []
    for e in events:
        ch = e["actor_channel"]
        link = e["corpus_linkability"]
        eligible = link in ("L3_WORKFLOW_MATCH", "L4_DIRECT_EVALUATION")
        rows.append({
            "event_id": e["event_id"],
            "organization": e["organization"],
            "channel": ch,
            "workflow_stage": e["workflow_stage"],
            "deployment_status": e["deployment_status"],
            "observablesThatCouldMove": OBSERVABLES.get(ch, []),
            "dataAvailableHere": OBSERVABLE[ch],
            "corpus_linkability": link,
            "frozenBaselineFamily": BASELINE_KEY.get(ch, "none"),
            "forecastOrWatchTarget": (
                "watch: verified_moj_commercial_ai_deployment@1446Q2"
                if ch in ("BENCH_JUDICIAL_RESEARCH", "COURT_ADMINISTRATION")
                else "none"),
            "eventStudyPermitted": eligible,
            "whyNot": (None if eligible else
                       "linkability below L3: an event study here would "
                       "measure the wrong output"),
        })
    MAP.write_text(json.dumps({
        "what": "AI-LAW TRANSITION MAP: verified event -> channel -> workflow "
                "-> observables that could move -> data we hold -> "
                "linkability -> frozen baseline -> forecast or watch target "
                "-> future score.",
        "rule": "evidence and hypothesis are kept in different columns. "
                "deployment_status is what a source establishes; "
                "observablesThatCouldMove is a hypothesis and is never read "
                "as a finding.",
        "eventStudiesPermittedToday": sum(1 for r in rows
                                          if r["eventStudyPermitted"]),
        "openForecasts": len(ledger["forecasts"]),
        "openWatchTargets": len(ledger["watchTargets"]),
        "aiAsSubjectOfLawL3": radar["L3_count"],
        "rows": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"baseline cutoff {res['baselineCutoff']} "
          f"(~{CUTOFF_GREGORIAN}); {res['eventCounts']['total']} events, "
          f"{res['eventCounts']['beforeCutoff']} before the cutoff")
    for c, v in channels.items():
        print(f"  {c:34s} at cutoff {v['statusAtBaselineCutoff']:18s} "
              f"now {v['statusNow']}")
    print(f"  AI as a subject of law: L3 = {radar['L3_count']} of "
          f"{radar['judgmentsScanned']:,} judgments")
    print(f"-> {OUT.name}, {MAP.name}")


if __name__ == "__main__":
    main()
