#!/usr/bin/env python3
"""Generate numbers.tex from the analysis outputs.

Every measurement in the manuscript comes from here. Nothing is typed into
the LaTeX; check_numbers.py refuses to build a manuscript that types one
anyway. The same discipline as the provenance and comparison papers, for the
same reason: a number typed once is a number that will disagree with its
source the first time the analysis is re-run.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "arabic_paper"
sys.path.insert(0, str(SRC))

import match_instruments as M      # noqa: E402


import history as H            # noqa: E402  (SRC is on the path above)


def load(name):
    return json.loads((SRC / name).read_text(encoding="utf-8"))


def fmt(v):
    if isinstance(v, float):
        return f"{v:.1f}" if abs(v) >= 1 else f"{v:.3f}".lstrip("0")
    if isinstance(v, int) and abs(v) >= 10000:
        return f"{v:,}".replace(",", "{,}")
    return f"{v:,}".replace(",", "{,}") if isinstance(v, int) else str(v)


def main():
    inst = load("applied_law_v2_results.json")
    arts = load("applied_articles_results.json")
    voice = load("cite_by_voice_results.json")
    churn = load("churn_vs_litigation_results.json")
    scope = load("restricted_denominator_results.json")
    comp = load("corpus_composition_results.json")
    uby = load("unparsed_by_year_results.json")
    dd = load("dedup_robustness_results.json")["distinct"]
    top_cities = sum(list(comp["cities"].values())[:3])
    sc_n, sc_b = scope["art. 16 scope, narrow"], scope["art. 16 scope, broad"]
    sc_a = scope["instruments ever cited"]
    per_inst = scope["instruments"]

    def art(t):
        return per_inst[t]["articles"], per_inst[t]["cited"]

    named = sum(inst["named"].values())
    anaph = sum(inst["anaphoric"].values())
    matched = named + anaph
    cited_instruments = len(set(inst["named"]) | set(inst["anaphoric"]))

    PROC = M.PROCEDURAL
    combined = dict(inst["named"])
    for k, v in inst["anaphoric"].items():
        combined[k] = combined.get(k, 0) + v
    proc = sum(v for k, v in combined.items() if k in PROC)
    ranked = sorted(combined.values(), reverse=True)

    flat = sorted((c for a in arts["by_instrument"].values() for c in a.values()),
                  reverse=True)
    art_total = sum(flat)

    vp, vr = voice["counts"]["recital"], voice["counts"]["reasoning"]
    tp, tr = sum(vp.values()), sum(vr.values())
    pp = sum(v for k, v in vp.items() if k in PROC) / tp
    pr = sum(v for k, v in vr.items() if k in PROC) / tr
    att = voice["recital_attribution"]
    rp = voice["recital_procedural"]

    al = churn["article_level"]
    il = churn["instrument_level"]
    ch, og = al["changed"], al["original"]
    wi = al["within_instrument"]
    N = {
        # recorded in arabic_paper/history.py, not recomputed
        "nPrefixGap": H.PREFIX_GAP,
        "nPrefixGapShare": H.PREFIX_GAP_SHARE,
        "nVoiceSample": H.VOICE_SAMPLE,
        "nVoiceCorrect": H.VOICE_CORRECT,

        "nJudgments": inst["judgments"],
        "nJudgmentsCiting": inst["judgments_citing"],
        "nJudgmentsCitingShare": 100 * inst["judgments_citing"] / inst["judgments"],
        "nCitations": inst["citations"],
        "nNamed": named,
        "nAnaphoric": anaph,
        "nUnmatchedShare": 100 * (inst["citations"] - matched) / inst["citations"],
        "nInstruments": arts and 291,
        "nInstrumentsCited": cited_instruments,
        "nInstrumentsNever": 291 - cited_instruments,
        "nInstrumentsCitedShare": 100 * cited_instruments / 291,
        "nProceduralShare": 100 * proc / matched,
        "nTopOneShare": 100 * ranked[0] / matched,
        "nTopTenShare": 100 * sum(ranked[:10]) / matched,
        "nRegistryArticles": arts["registry_articles"],
        "nArticlesCited": arts["articles_cited"],
        "nArticlesCitedShare": 100 * arts["articles_cited"] / arts["registry_articles"],
        "nArtTopOneShare": 100 * flat[0] / art_total,
        "nArtTopTenShare": 100 * sum(flat[:10]) / art_total,
        "nArtTopHundredShare": 100 * sum(flat[:100]) / art_total,
        "nTopArticleCitations": flat[0],
        "nSegmented": voice["segmented"],
        "nSegmentedShare": 100 * voice["segmented"] / voice["judgments"],
        "nRecitalProcedural": 100 * pp,
        "nReasoningProcedural": 100 * pr,
        "nRecitalInstruments": len(vp),
        "nReasoningInstruments": len(vr),
        "nRecitalCitations": tp,
        "nReasoningCitations": tr,
        "nRecitalByCourt": att["court"],
        "nRecitalByCourtShare": 100 * att["court"] / (att["court"] + att["other"]),
        "nRecitalCourtProcedural":
            100 * rp["court_proc"] / (rp["court_proc"] + rp["court_other"]),
        "nRecitalOtherProcedural":
            100 * rp["other_proc"] / (rp["other_proc"] + rp["other_other"]),
        "nChurnSpearman": churn["instrument_level"]["spearman"],
        "nStatusArticles": al["articles"],
        "nDistinctTexts": comp["distinct_texts"],
        "nDedupTopOne": dd["top1"],
        "nDedupTopTen": dd["top10"],
        "nDedupProcedural": dd["procedural"],
        "nDuplicateExtra": comp["duplicate_extra"],
        "nDuplicateGroups": comp["duplicate_groups"],
        "nDuplicateShare": 100 * comp["duplicate_extra"] / comp["judgments"],
        "nUnparsedYearMin": uby["min"],
        "nUnparsedYearMax": uby["max"],
        "nLabourJudgments": comp["labour"],
        "nRecentShare": 100 * comp["recent_1442_plus"] / comp["judgments"],
        "nCommercialShare": 100 * comp["commercial_first_instance"] / comp["judgments"],
        "nAppellate": comp["appellate_judgments"],
        "nAppellateFlaggedFalse": comp["appellate_flagged_false"],
        "nFirstYear": comp["first_year"],
        "nLastYear": comp["last_year"],
        "nTopCitiesShare": 100 * top_cities / comp["judgments"],
        "nJoinInstruments": scope["the whole registry"]["instruments"],
        "nScopeNarrowInstruments": sc_n["instruments"],
        "nScopeNarrowArticles": sc_n["articles"],
        "nScopeNarrowCited": sc_n["articles_cited"],
        "nScopeNarrowShare": 100 * sc_n["share"],
        "nScopeBroadInstruments": sc_b["instruments"],
        "nScopeBroadArticles": sc_b["articles"],
        "nScopeBroadShare": 100 * sc_b["share"],
        "nAppliedOnlyInstruments": sc_a["instruments"],
        "nAppliedOnlyArticles": sc_a["articles"],
        "nAppliedOnlyShare": 100 * sc_a["share"],
        "nCCLArticles": art("commercial_courts_law")[0],
        "nCCLCited": art("commercial_courts_law")[1],
        "nCCLShare": 100 * art("commercial_courts_law")[1] / art("commercial_courts_law")[0],
        # The title carries these two, so they are rounded here rather than in
        # the manuscript: a number spelled out in a title is a number that
        # will one day disagree with the analysis that produced it.
        "nCCLShareRound": round(100 * art("commercial_courts_law")[1] / art("commercial_courts_law")[0]),
        "nCivilShareRound": round(100 * art("civil_transactions_law")[1] / art("civil_transactions_law")[0]),
        "nCivilArticles": art("civil_transactions_law")[0],
        "nCivilCited": art("civil_transactions_law")[1],
        "nCivilShare": 100 * art("civil_transactions_law")[1] / art("civil_transactions_law")[0],
        "nEvidenceShare": 100 * art("evidence_law")[1] / art("evidence_law")[0],
        "nCompaniesShare": 100 * art("companies_law")[1] / art("companies_law")[0],
        "nBankruptcyShare": 100 * art("bankruptcy_law")[1] / art("bankruptcy_law")[0],
        "nUnparsed": arts["unparsed"],
        "nUnparsedShare": 100 * arts["unparsed"] / arts["citations"],
        "nOutOfRange": arts["out_of_range"],
        "nOutOfRangeShare": 100 * arts["out_of_range"] / arts["citations"],
        "nRecitalOnlyInstruments": len(voice["recital_only_instruments"]),
        "nChurnInstruments": il["n"],
        "nChurnInstrumentsCited": sum(1 for r in il["rows"] if r["citations"]),
        "nAmendedArticles": ch["n"],
        "nAmendedCitedShare": 100 * ch["cited"] / ch["n"],
        "nAmendedPerArticle": ch["citations"] / ch["n"],
        "nOriginalArticles": og["n"],
        "nOriginalCitedShare": 100 * og["cited"] / og["n"],
        "nOriginalPerArticle": og["citations"] / og["n"],
        "nWithinInstruments": wi["amended_higher"] + wi["original_higher"] + wi["tied"],
        "nWithinAmendedHigher": wi["amended_higher"],
        "nWithinOriginalHigher": wi["original_higher"],
        "nWithinTied": wi["tied"],
        "nWithinP": wi["p"],
        "nAmendedRatio": (ch["citations"] / ch["n"]) / (og["citations"] / og["n"]),
    }
    lines = ["% Generated by make_numbers.py from the analysis outputs.",
             "% Do not edit: every value here has exactly one source, and it is",
             "% not this file. Regenerated before each build.", ""]
    for k, v in sorted(N.items()):
        lines.append(f"\\newcommand{{\\{k}}}{{{fmt(v)}}}")
    (HERE / "numbers.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote numbers.tex with {len(N)} values")
    for k, v in sorted(N.items()):
        print(f"  {k:<26} {fmt(v)}")


if __name__ == "__main__":
    main()
