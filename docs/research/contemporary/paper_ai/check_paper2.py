#!/usr/bin/env python3
"""Every figure in the second manuscript must come from a results file.

paper/check_paper.py does this for the speaker-attribution paper. This is the
same guard for the corpus-properties paper: it re-reads the JSON the analyses
wrote and asserts the string is present in the markdown, so a hand-typed or
drifted number fails the build rather than reaching a reviewer.

    python3 check_paper2.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
C = HERE.parent
MS = (HERE / "MANUSCRIPT.md").read_text(encoding="utf-8")
# emphasis is a typesetting choice and must not decide whether a figure
# traces, so table rows are matched against a bold-stripped copy
MSB = MS.replace("**", "")


def load(name):
    return json.loads((C / name).read_text(encoding="utf-8"))


FA = load("formula_analysis_results.json")
FOR = load("foresight_results.json")
HOR = load("horizon_results.json")
NOW = load("nowcast_results.json")
TR = load("transition_results.json")
REG = load("regimes_results.json")
RAD = load("ai_radar_results.json")
WIN = load("windows_results.json")
MAP = load("ai_law_map.json")
ADO = load("adoption_registry.json")

checks = []


def want(label, value):
    checks.append((label, str(value), str(value) in MS))


# ---------------------------------------------------------------- section 3
want("judgments scanned", RAD["judgmentsScanned"])
want("judgments with reasons, 1442-1446",
     WIN["views"]["contemporary_5y"]["withReasons"])
want("non-statutory mentions",
     FA["phase32_35_contaminationAndRetrieval"]
       ["phase32_rawVersusAdjustedFrequency"]["totalRawMentions"])
MAT = HOR["phase3_maturityRule"]
want("mature quarters",
     sum(1 for p in MAT["byPeriod"] if p["verdict"] == "SCORABLE"))
want("first quarter tested", MAT["byPeriod"][0]["period"].replace("Q", "Q"))
want("last quarter tested", MAT["byPeriod"][-1]["period"])
for crit, token in ((0, "800"), (1, "200"), (3, "40 per cent")):
    assert token.split()[0] in MAT["criteria"][crit], MAT["criteria"][crit]
want("maturity: judgments", "800")
want("maturity: court citations", "200")

# -------------------------------------------------------------- section 4.1
U = FA["phase2_unitSpecification"]
want("context radius", U["contextRadius"])
want("window tokens median", U["windowTokens"]["median"])
want("window tokens p10", U["windowTokens"]["p10"])
want("window tokens p90", U["windowTokens"]["p90"])
F3 = FA["phase3_exactVersusFamily"]
want("minhash pairs at 0.7", F3["stability"]["pairsAt70"])
want("share surviving at 0.8", F3["stability"]["shareSurvivingAt80"])

# -------------------------------------------------------------- section 4.2
F4 = FA["phase4_sourceMasking"]
want("distinct formulas", F4["distinctFormulas"]["sourcePreserving"])
want("distinct formulas, source masked", F4["distinctFormulas"]["sourceMasked"])
want("circulating formulas", F3["exactFormulas"])
want("mentions in circulating formulas", F3["mentionsInCirculatingFormulas"])
want("multi-source shells", F4["shellsWithMoreThanOneSource"])

# -------------------------------------------------------------- section 4.3
P32 = FA["phase32_35_contaminationAndRetrieval"]["phase32_rawVersusAdjustedFrequency"]
want("authorities ranked", P32["sources"])
want("total raw", P32["totalRawMentions"])
want("total adjusted", P32["totalAdjusted"])
want("overall inflation", P32["overallInflation"])
want("max source inflation", P32["maxSourceInflation"])
ROW = {r["source"]: r for r in P32["table"]}
for src, label in (("J.IBN_TAYMIYYA", "Ibn Taymiyya"),
                   ("B.INSAF", "al-Insaf"),
                   ("GENERIC.fiqh.unattributed", "unattributed fiqh"),
                   ("GENERIC.hadith.untraced", "untraced hadith")):
    r = ROW[src]
    want(f"{label} raw", r["rawSupport"])
    want(f"{label} adjusted", r["formulaAdjustedSupport"])
    want(f"{label} inflation", r["inflation"])
assert ROW["H.BAYHAQI"]["inflation"] == P32["maxSourceInflation"], \
    "the worst-inflated authority named in the table is no longer al-Bayhaqi"

# -------------------------------------------------------------- section 4.4
P34 = FA["phase32_35_contaminationAndRetrieval"]["phase34_retrievalRanking"]
want("authorities moving at least one place", P34["rankChangesAtLeastOnePlace"])
want("largest displacement",
     max(abs(d["places"]) for d in P34["largestDisplacements"]))
want("top-10 stability", P34["top10Stability"])
P35 = FA["phase32_35_contaminationAndRetrieval"]["phase35_temporalAgeing"]
want("raw vs adjusted correlation", P35["correlationRawVersusAdjusted"])
want("inflation, first mature quarter", P35["inflationTrend"]["first"])
want("inflation, last mature quarter", P35["inflationTrend"]["last"])

# ---------------------------------------------------------------- section 5
CL = FA["phase6_formulaClasses"]["byClass"]
NAMES = {"AUTHORITY_INTRODUCTION_FRAME": "authority introduction frame",
         "GENERIC_REASONING": "generic reasoning",
         "AUTHORITY_QUOTATION": "authority quotation",
         "COMPENSATION_HARM": "compensation and harm",
         "BURDEN_PRESUMPTION": "burden and presumption",
         "DOCTRINAL_RULE": "doctrinal rule",
         "DISPOSITION": "disposition",
         "PROCEDURAL_OPERATION": "procedural operation",
         "CONTRACT": "contract",
         "JURISDICTION": "jurisdiction",
         "FACT_RECITAL": "fact recital"}
for key, label in NAMES.items():
    row = f"| {label} | {CL[key]} |"
    checks.append((f"class row: {label}", row, row in MSB))
want("procedural class size", CL["PROCEDURAL_OPERATION"])
AB = FA["phase9_classSpecificAblation"]
want("single-class ablations",
     sum(1 for a in AB["arms"] if a.startswith("ONLY_")))
want("ablations reproducing the flip",
     len(AB["singleClassRemovalsThatReproduceTheFlip"]))
VC = FA["phase9b_volumeControl"]["arms"]
for pct, arm in ((25, "remove25pct"), (50, "remove50pct"),
                 (75, "remove75pct"), (90, "remove90pct")):
    a = VC[arm]
    want(f"random removal {pct}%: mentions", a["meanMentionsRemoved"])
    want(f"random removal {pct}%: flip share", a["flipShare"])
pairs = {v for a in VC.values()
         for v in (a["matchedPairs"]["min"], a["matchedPairs"]["max"])}
assert pairs == {6, 7}, f"matched-pair range moved: {sorted(pairs)}"
CD = FA["phase24_codeFormulaDependence"]
want("codes with at least 50 mentions", len(CD["byCode"]))
want("authority identities lost if circulating removed",
     sum(v["sourcesLostIfCirculatingRemoved"] for v in CD["byCode"].values()))

# -------------------------------------------------------------- section 6.1
TM = FOR["temporalMisalignment"]
for h, label in (("h1", "1 quarter"), ("h2", "2 quarters"), ("h4", "4 quarters")):
    d = TM[h]
    want(f"{label}: folds", d["folds"])
    want(f"{label}: content gap", d["meanCitationShareToNeverSeenArticles"])
    want(f"{label}: top-50 displaced", d["meanTop50DisplacedPct"])
    want(f"{label}: rank displacement", d["meanRankDisplacementTop200"])
TRG = {t["trigger"]: t for t in HOR["phase22_refreshTriggers"]["triggers"]}
want("displacement threshold", int(TRG["TOP50_DISPLACEMENT"]["threshold"]))
want("rank-gap threshold", int(TRG["RANK_GAP"]["threshold"]))
assert TRG["TOP50_DISPLACEMENT"]["firstHorizonCrossed"] == 1, "trigger order moved"
assert TRG["RANK_GAP"]["firstHorizonCrossed"] == 2, "trigger order moved"
assert TRG["CONTENT_GAP"]["firstHorizonCrossed"] == 4, "trigger order moved"
assert TRG["CONTENT_GAP"]["threshold"] == 0.1, "content threshold moved"

# -------------------------------------------------------------- section 6.2
PE = TR["phase19_pseudoEventControls"]
want("pseudo-events", PE["pseudoEvents"])
want("staleness firings",
     PE["shiftCriteriaFalsePositives"]["L8_RETRIEVAL_STALENESS"]["events"])
assert PE["shiftCriteriaFalsePositives"]["L8_RETRIEVAL_STALENESS"]["rate"] == 1.0, \
    "the staleness criterion no longer fires on every pseudo-event"
want("staged vector share", PE["stagedVectorShare"])

# -------------------------------------------------------------- section 6.3
AR = NOW["part18_retrievalArchitectures"]["architectures"]
LABEL = {"STATUTE_PLUS_DOCTRINAL_COMPANIONS": "statute + doctrinal companions",
         "STATUTE_PLUS_CURRENT_ARTICLE_ECOLOGY": "statute + current article ecology",
         "TIME_AWARE_RECENT_WINDOW": "time-aware recent window",
         "STATUTE_ONLY": "statute only",
         "SPEAKER_AWARE_HYBRID": "speaker-aware hybrid"}
for key, label in LABEL.items():
    a = AR[key]
    row = f"| {label} | {a['meanCitationCoverage']} | {a['coverageDrift']} |"
    checks.append((f"architecture row: {label}", row, row in MSB))
    want(f"{label}: drift", a["coverageDrift"])
want("architecture folds", AR["STATUTE_ONLY"]["folds"])
assert NOW["part18_retrievalArchitectures"]["leastDrift"] == \
    "STATUTE_PLUS_DOCTRINAL_COMPANIONS", "the least-drifting architecture changed"
SA = FOR["speakerAwareRetrieval"]
want("speaker-aware folds", SA["folds"])
want("universe growth", SA["meanUniverseGrowthPct"])
want("coverage added by party-only", SA["meanCoverageAddedByPartyOnly"])
want("party-only precision", SA["meanPartyOnlyPrecision"])
want("coverage points per 10 per cent growth",
     SA["coveragePointsPer10pctUniverseGrowth"])
want("speaker-aware verdict", SA["verdict"])

# ---------------------------------------------------------------- section 7
CO = REG["phase24_coherence"]
FAL = REG["phase21_falseAlarm"]
want("metrics tested", CO["metricsTested"])
want("metrics with a break", CO["metricsWithAnySignificantMethod"])
want("families", len(CO["families"]))
want("null draws", FAL["draws"])
want("metric false-alarm rate", FAL["metricFalseAlarmRate"])
want("mean metrics firing per draw", FAL["meanMetricsFiringPerDraw"])
want("multi-layer candidates", len(CO["multiLayerCandidates"]))
want("mean multi-layer quarters per draw", FAL["meanMultiLayerQuartersPerDraw"])
want("max multi-layer quarters in a draw", FAL["maxMultiLayerQuartersInADraw"])
assert not CO["candidatesSurvivingWithoutTheObservationSystem"], \
    "a candidate now survives removing the observation system"
want("contiguous candidate block", len(CO["clustering"]))
want("docket appears in",
     sum(1 for c in CO["multiLayerCandidates"] if "DOCKET" in c["families"]))
FAM = {"DOCKET": "docket composition", "FORMULA": "formula layer",
       "PUBLICATION": "publication", "STATUTORY": "statutory salience",
       "ECOLOGY": "authority ecology"}
for key, label in FAM.items():
    f = CO["byFamily"][key]
    row = f"| {label} | {f['metricsTested']} | {f['metricsFiring']} |"
    checks.append((f"family row: {label}", row, row in MSB))
    want(f"{label}: share", f["share"])
assert CO["stationaryFamilies"] == ["ECOLOGY"], "the stationary family changed"
SEG = REG["phase15_withinRegimeForecastability"]
want("series where segmentation wins", len(SEG["seriesWhereSegmentationWins"]))
want("series tested for segmentation", SEG["seriesTested"])

# ---------------------------------------------------------------- section 8
EXPLICIT = [a for a in MAP["anchors"] if a["class"] == "EXPLICIT_RULE"]
AI_PERMISSION = [a for a in EXPLICIT if "الذكاء الاصطناعي" in a["quote_ar"]]
want("explicit AI-permission provisions", len(AI_PERMISSION))
for a in AI_PERMISSION:
    if a["anchor_id"] in ("ANCH-CCL-REG-24", "ANCH-EVID-PROC-23"):
        # the two quoted verbatim in the body, checked word by word
        body = " ".join(a["quote_ar"].split())
        quoted = " ".join(
            line.lstrip("> ").strip() for line in MS.splitlines()
            if line.startswith(">") and "الذكاء" in line)
        checks.append((f"quote {a['anchor_id']}", a["article"],
                       all(w in quoted for w in body.split()[:6])))
        want(f"article of {a['anchor_id']}", a["article"])
want("AI-material disputes", RAD["L3_count"])
want("AI-relevant technology, status not established", RAD["byLevel"]["L2"])
want("explicit AI reference anywhere", RAD["byLevel"]["L1"])
want("adoption events", len(ADO["events"]))
assert not [e for e in ADO["events"]
            if e["corpus_linkability"].startswith("L3")], \
    "an adoption event now reaches the adjudicatory workflow"

bad = [c for c in checks if not c[2]]
print(f"{len(checks) - len(bad)} of {len(checks)} manuscript figures "
      f"trace to a results file")
for label, val, _ in bad:
    print(f"  MISSING  {label:<48}{val}")
sys.exit(1 if bad else 0)
