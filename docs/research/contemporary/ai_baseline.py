#!/usr/bin/env python3
"""The state of the corpus at the moment before we claim to know the future.

This is not a PRE-AI baseline. Legal AI already exists and is already in use
somewhere in Saudi legal practice; nobody in this repository knows where or
how much. What can be recorded honestly is the state of the measurable
variables at a stated data cutoff, so that a future session -- with more
corpus, and possibly with a registry of verified adoption events -- can ask
whether any of them moved, and by how much, against a number that was written
down first.

So the name is AI-TRANSITION BASELINE, and its content is deliberately dull:
seven families of metric, every one of them a rate, a share, a rank or an
entropy, each traceable to the analysis that produced it.

    python3 ai_baseline.py
"""
import hashlib
import json
import math
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import foresight as F                     # noqa: E402

OUT = HERE / "ai_baseline_results.json"
J = lambda n: json.loads((HERE / n).read_text(encoding="utf-8"))
PIPELINE_VERSION = "contemporary/2026-08-companion+foresight"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]


def head():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE,
                              capture_output=True, text=True,
                              timeout=20).stdout.strip()[:40] or "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def entropy(counts):
    n = sum(counts)
    return -sum((c / n) * math.log(c / n) for c in counts if c > 0) if n else 0.0


def hhi(counts):
    n = sum(counts)
    return round(sum((c / n) ** 2 for c in counts), 5) if n else None


def spearman(a, b):
    ks = sorted(set(a) | set(b), key=str)
    ra = {k: i for i, k in enumerate(sorted(ks, key=lambda k: (-a.get(k, 0), str(k))))}
    rb = {k: i for i, k in enumerate(sorted(ks, key=lambda k: (-b.get(k, 0), str(k))))}
    n = len(ks)
    if n < 3:
        return None
    d = sum((ra[k] - rb[k]) ** 2 for k in ks)
    return round(1 - 6 * d / (n * (n * n - 1)), 4)


def main():
    rows, dates, _ = F.load()
    S = F.build(rows)
    P, LBL = F.P, F.LBL
    cutoff = LBL[-1]
    last = S[P[-1]]
    prev = S[P[-2]]
    # a full trailing year, so the baseline is not one thin quarter
    year = {"courtStat": Counter(), "partyStat": Counter(),
            "courtInst": Counter(), "courtType": Counter(),
            "courtRule": Counter(), "partyRule": Counter()}
    for p in P[-4:]:
        for k in year:
            year[k].update(S[p][k])

    core = J("core_view.json")["views"]["contemporary_3y"]
    comp = J("companion_analysis_results.json")
    ov = J("overlap_results.json")
    claim = J("claim_results.json")["views"]["contemporary_3y"]
    tr = J("traceability_results.json")
    eco = J("ecology_results.json")["profiles"]
    fs = J("foresight_results.json")

    cs = year["courtStat"]
    ps = year["partyStat"]
    cw = comp["loc_w500"]

    # ---- G: uptake velocity, measured as first OBSERVED use. Enactment dates
    # are not in the registry, so this is visibility latency inside the
    # corpus, not latency from commencement, and it is left-censored: an
    # article already in use before 1442Q1 has no observable first use.
    firstC, firstP = {}, {}
    for i, p in enumerate(P):
        for a in S[p]["courtStat"]:
            firstC.setdefault(a, i)
        for a in S[p]["partyStat"]:
            firstP.setdefault(a, i)
    both = [a for a in sorted(firstC, key=str)
            if a in firstP and min(firstC[a], firstP[a]) >= 2]
    lead = [firstC[a] - firstP[a] for a in both]
    lead.sort()

    res = {
        "what": "AI-TRANSITION BASELINE: the measurable state of published "
                "Saudi commercial adjudication at a stated cutoff, recorded "
                "so that a future session can ask whether anything moved.",
        "notPreAi": "Legal AI already exists and is already in use somewhere "
                    "in Saudi legal practice. This baseline makes no claim "
                    "about how much, and nothing here is evidence that any "
                    "document was produced with or without it.",
        "dataCutoff": cutoff,
        "windowUsed": [LBL[0], LBL[-1]],
        "repositoryHead": head(),
        "pipelineVersion": PIPELINE_VERSION,
        "dataHashes": {n: sha(HERE / n) for n in sorted(
            ("authority_mentions.jsonl.gz", "companion_layer.jsonl.gz",
             "judgment_dates.json.gz", "authority.py", "companions.py",
             "foresight.py"))},
        "compositionWarnings": [
            fs["compositionWarning"],
            "the corpus is published commercial judgments; it is not the "
            "Saudi judiciary, and the publisher's release policy is itself a "
            "time-varying quantity that no metric here separates out",
            "quarters after 1446Q2 are excluded for publication lag "
            "(1446Q3 = 184 judgments, 1446Q4 = 7)",
            "the doctrinal identity universe is authority.py's vocabulary, so "
            "every diversity figure in family C is a floor and a change in "
            "the extractor would move it without anything moving in the law",
        ],

        # ---------------------------------------------------- A statutory use
        "A_statutoryUse": {
            "trailingYear": [LBL[-4], LBL[-1]],
            "courtArticleHHI": hhi(list(cs.values())),
            "courtArticleEntropy": round(entropy(list(cs.values())), 4),
            "effectiveArticles": round(math.exp(entropy(list(cs.values()))), 2),
            "distinctArticlesCited": len(cs),
            "courtInstrumentHHI": hhi(list(year["courtInst"].values())),
            "distinctInstruments": len(year["courtInst"]),
            "articlesFor50pctOfCitations": core["articlesFor50"],
            "articlesFor75pctOfCitations": core["articlesFor75"],
            "articlesFor90pctOfCitations": core["articlesFor90"],
            "top10ShareOfCourtCitations": round(
                100 * sum(v for _a, v in sorted(cs.items(), key=lambda kv: (-kv[1], str(kv[0])))[:10])
                / sum(cs.values()), 2),
            "top50ShareOfCourtCitations": round(
                100 * sum(v for _a, v in sorted(cs.items(), key=lambda kv: (-kv[1], str(kv[0])))[:50])
                / sum(cs.values()), 2),
            "top100ShareOfCourtCitations": round(
                100 * sum(v for _a, v in sorted(cs.items(), key=lambda kv: (-kv[1], str(kv[0])))[:100])
                / sum(cs.values()), 2),
            "quarterOnQuarterRankSpearman": spearman(last["courtStat"],
                                                     prev["courtStat"]),
            "meanTop50EntrantsPerQuarter":
                fs["articleVisibility"]["meanNewEntrantsPerPeriod"],
        },

        # -------------------------------------------------- B court vs bar
        "B_courtVsBar": {
            "authorityFamilyMedianJaccard": ov["specs"]["strict"]["fam"]["medianJaccard"],
            "articleMedianJaccard": ov["specs"]["strict"]["art_all"]["medianJaccard"],
            "instrumentMedianJaccard": ov["specs"]["strict"]["inst_all"]["medianJaccard"],
            "P_sharedInstrumentGivenBothCiteStatute":
                ov["conditional"]["strict"]["sharedInstrumentPct"],
            "P_sharedArticleGivenSharedInstrument":
                ov["conditional"]["strict"]["sharedArticleGivenInstrumentPct"],
            "courtTop20VsPartyTop20Jaccard": round(
                F.jaccard(F.top(cs, 20), F.top(ps, 20)), 4),
            "courtStatuteShareOfCourtMentions": round(
                100 * year["courtType"]["statute"] / sum(year["courtType"].values()), 2),
            "partyStatutoryMentionsTrailingYear": sum(ps.values()),
            "courtStatutoryMentionsTrailingYear": sum(cs.values()),
        },

        # ---------------------------------------------- C doctrinal diversity
        "C_doctrinalDiversity": {
            "note": "court voice, nearest statutory citation within 500 "
                    "characters, 1444-1446; bounded by the extractor",
            "distinctCanonicalIdentities":
                comp["phase4_resolution"]["uniqueCanonicalIdentities"],
            "byCode": {c: {
                "units": v["units"],
                "distinctSources": v["distinctSources"],
                "entropy": v["entropy"],
                "effectiveSources": v["effectiveSources"],
                "hhi": v["hhi"],
                "coverageTop1": v["coverageTop1"],
                "coverageTop3": v["coverageTop3"],
                "coverageTop5": v["coverageTop5"],
                "namedShare": v["namedShare"],
                "fiqhNamedShareOfFiqh": v["fiqhNamedShareOfFiqh"],
            } for c, v in sorted(cw["phase5_8_9_profiles"].items())
                if v.get("verdict") == "PROFILED"},
            "namedMaximTextPctByCode": {c: v["namedMaximTextPct"]
                                        for c, v in sorted(cw["phase18_maxims"].items())},
            "corpusNamedFiqhShareOfFiqhTrailingYear": round(
                100 * sum(year["courtRule"][r] for r in F.NAMED_FIQH)
                / max(1, sum(year["courtRule"][r] for r in F.NAMED_FIQH)
                      + year["courtRule"]["fiqh.unattributed"]), 2),
        },

        # -------------------------------------------------- D traceability
        "D_traceability": {
            "courtMentionsClassified": tr["overall"]["mentions"],
            "resolvedStatutePct": tr["overall"]["RESOLVED_STATUTE"],
            "unresolvedStatutePct": tr["overall"]["UNRESOLVED_STATUTE"],
            "namedSourcePct": tr["overall"]["NAMED_SOURCE"],
            "unnamedPct": tr["overall"]["UNNAMED"],
            "medianPerJudgmentTraceablePct":
                tr["perJudgment"].get("medianPct"),
            "namedDoctrinalAuthorityResolvedPct":
                comp["phase4_resolution"]["resolvedPct"],
            "untracedHadithPct": comp["phase4_resolution"]["untracedHadithPct"],
            "untraceableShareOfLocalMentionsByCode": {
                c: v["untraceablePct"] for c, v in
                sorted(cw["phase29_untraceable"].items())},
            "byYear": {y: v["RESOLVED_STATUTE"] + v["NAMED_SOURCE"]
                       for y, v in sorted(tr["byYear"].items())},
        },

        # ----------------------------------------------- E hybrid reasoning
        "E_hybridReasoning": {
            "statuteOnlyPct": claim["shape"]["statute_only"],
            "hybridPct": claim["shape"]["hybrid"],
            "nonStatuteOnlyPct": claim["shape"]["non_statute_only"],
            "noExplicitAuthorityPct": claim["shape"]["none"],
            "nonStatutoryShareOfCourtMentionsTrailingYear": round(
                100 * sum(year["courtType"][t] for t in F.NONSTATUTE)
                / sum(year["courtType"].values()), 2),
            "codeSpecificHybridRate": {
                c: v["hybridPct"] for c, v in sorted(eco.items())
                if isinstance(v, dict) and "hybridPct" in v},
            "codeSpecificNamedFiqhRate": {
                c: v["named_fiqh"] for c, v in sorted(eco.items())
                if isinstance(v, dict) and "named_fiqh" in v},
        },

        # ------------------------------------------- F template concentration
        "F_templateConcentration": {
            "scope": "court-voice authority CONTEXTS only -- a hash of the "
                     "wording around a non-statutory mention. This is not a "
                     "measure of whole-judgment templating and must not be "
                     "read as one.",
            "distinctFingerprints": comp["phase17_propositions"]["distinctFingerprints"],
            "shareInARepeatedFamily":
                comp["phase17_propositions"]["sharePartOfARepeatedFamily"],
            "shareInFamiliesOf5Plus":
                comp["phase17_propositions"]["shareInFamiliesWith5plus"],
            "circulatingFingerprints":
                cw["phase16b_deboilerplated"]["circulatingFingerprints"],
            "courtMentionsInCirculatingWordingPct":
                cw["phase16b_deboilerplated"]["courtMentionsRemovedPct"],
            "topFingerprintShareByCodeTopSource": {
                c: v[0]["topFingerprintShare"] for c, v in
                sorted(cw["phase16_templates"].items()) if v},
            "attribution": "these templates are HUMAN AND INSTITUTIONAL as "
                           "measured; nothing here attributes any of them to "
                           "any tool.",
        },

        # ------------------------------------------------- G uptake velocity
        "G_uptakeVelocity": {
            "definition": "first OBSERVED quarter of use inside the corpus. "
                          "Enactment dates are not in the registry, so this "
                          "is not latency from commencement, and it is "
                          "left-censored at 1442Q1.",
            "articlesWithBothFirstUsesObserved": len(both),
            "medianCourtMinusPartyFirstUseQuarters":
                (lead[len(lead) // 2] if lead else None),
            "shareFirstSeenInPartyVoice": round(
                100 * sum(1 for x in lead if x > 0) / len(lead), 2) if lead else None,
            "shareFirstSeenInCourtVoice": round(
                100 * sum(1 for x in lead if x < 0) / len(lead), 2) if lead else None,
            "shareFirstSeenSameQuarter": round(
                100 * sum(1 for x in lead if x == 0) / len(lead), 2) if lead else None,
            "leadLagVerdict": fs["leadLag"]["verdict"],
            "meanCourtPersistenceR": fs["leadLag"]["meanCourtPersistenceR"],
            "meanPartyPartialR": fs["leadLag"]["meanPartyPartialR"],
        },
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"AI-transition baseline at {cutoff}, head {res['repositoryHead'][:8]}")
    print(f"  A: {res['A_statutoryUse']['distinctArticlesCited']} articles, "
          f"HHI {res['A_statutoryUse']['courtArticleHHI']}, "
          f"top-50 {res['A_statutoryUse']['top50ShareOfCourtCitations']} %")
    print(f"  B: court/party top-20 Jaccard "
          f"{res['B_courtVsBar']['courtTop20VsPartyTop20Jaccard']}")
    print(f"  G: first use in the bar for "
          f"{res['G_uptakeVelocity']['shareFirstSeenInPartyVoice']} % of articles, "
          f"{res['G_uptakeVelocity']['leadLagVerdict']}")
    print(f"-> {OUT.name}")


if __name__ == "__main__":
    main()
