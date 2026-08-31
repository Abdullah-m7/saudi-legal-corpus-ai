#!/usr/bin/env python3
"""The same discipline as check_docs.py, one directory down.

`check_docs.py` guards the Arabic notes of the earlier papers and
`paper/check_paper.py` guards the manuscript. The contemporary notes had no
guard, and they are now the documents most likely to drift: they carry the
decomposition, the article-level seams and the profile, all of which are read
from result files that get re-run.

Every headline figure in these notes is declared here with the result file
and key it comes from, and checked as it is written in the prose. The script
does not rewrite prose -- a number in a sentence usually needs the sentence
changed too -- it says which figure moved and where.

    python3 check_notes.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
J = lambda n: json.loads((HERE / n).read_text(encoding="utf-8"))


def facts():
    ov, hy = J("overlap_results.json"), J("hybrid_results.json")
    ret, cf = J("retrieval_results.json"), J("core_function.json")
    fg, pg = J("function_gold.json"), J("pairs_gold.json")
    hg = J("hybrid_gold.json")
    cp, cd = J("completeness_results.json"), J("codes_results.json")
    si, ap = J("silence_results.json"), J("appellate_results.json")
    rg, hr = J("rag_gap_results.json"), J("hybrid_roles_gold.json")
    tl, ec = J("twolayers_results.json"), J("ecology_results.json")
    tr, af = J("traceability_results.json"), J("adjudicative_function_gold.json")
    ins, ief = J("instruments_results.json"), J("instrument_effect_results.json")
    S, C = ov["specs"]["strict"], ov["conditional"]["strict"]
    W = ov["conditional"]["wide"]
    y, seam = hy["years"], hy["seams"]
    art = {(r["instrument"], r["article"]): r for r in seam["articles"]}
    out = [
        ("art_all no-overlap", f"{S['art_all']['noOverlapPct']}",
         ["DECOMPOSITION.md", "contemporary_commercial_adjudication_profile.md"]),
        ("art_nostruct no-overlap", f"{S['art_nostruct']['noOverlapPct']}",
         ["DECOMPOSITION.md", "BACKLOG.md"]),
        ("art_dispute no-overlap", f"{S['art_dispute']['noOverlapPct']}",
         ["DECOMPOSITION.md", "BACKLOG.md"]),
        ("P(shared instrument)", f"{C['sharedInstrumentPct']}",
         ["DECOMPOSITION.md", "BACKLOG.md"]),
        ("P(shared article | instrument)",
         f"{C['sharedArticleGivenInstrumentPct']}",
         ["DECOMPOSITION.md", "BACKLOG.md"]),
        ("P(shared article | instrument), wide",
         f"{W['sharedArticleGivenInstrumentPct']}", ["DECOMPOSITION.md"]),
        ("Spearman court/party", f"{ret['spearman']['court_vs_party']}",
         ["DECOMPOSITION.md",
          "contemporary_commercial_adjudication_profile.md"]),
        ("top-50 structural share",
         f"{cf['contemporary_3y_top50']['class']['STRUCTURAL_PROCEDURAL']}",
         ["DECOMPOSITION.md",
          "contemporary_commercial_adjudication_profile.md"]),
        ("top-10 structural share",
         f"{cf['contemporary_3y_top10']['class']['STRUCTURAL_PROCEDURAL']}",
         ["DECOMPOSITION.md"]),
        ("fiqh prevalence 1444",
         f"{y['1444']['authority']['fiqh_source']['prevalencePct']}",
         ["NEXT_PROGRAMME.md", "CONTEMPORARY_MAP.md"]),
        ("fiqh prevalence 1446",
         f"{y['1446']['authority']['fiqh_source']['prevalencePct']}",
         ["NEXT_PROGRAMME.md", "CONTEMPORARY_MAP.md"]),
        ("fiqh intensity 1446",
         f"{y['1446']['authority']['fiqh_source']['intensity']}",
         ["NEXT_PROGRAMME.md", "CONTEMPORARY_MAP.md"]),
        ("statute prevalence 1446",
         f"{y['1446']['authority']['statute']['prevalencePct']}",
         ["NEXT_PROGRAMME.md", "CONTEMPORARY_MAP.md"]),
        ("statute intensity 1446",
         f"{y['1446']['authority']['statute']['intensity']}",
         ["NEXT_PROGRAMME.md", "CONTEMPORARY_MAP.md"]),
        ("seam base rate", f"{seam['basePct']}", ["NEXT_PROGRAMME.md"]),
        ("CCL 29 seam rate",
         f"{art[('commercial_courts_law', 29)]['nonStatutePct']}",
         ["NEXT_PROGRAMME.md", "DECOMPOSITION.md"]),
        ("CCL-IR 164 seam rate",
         f"{art[('commercial_courts_implementing_regulation', 164)]['nonStatutePct']}",
         ["NEXT_PROGRAMME.md"]),
        ("CCL-IR 58 seam rate",
         f"{art[('commercial_courts_implementing_regulation', 58)]['nonStatutePct']}",
         ["NEXT_PROGRAMME.md", "DECOMPOSITION.md"]),
        ("Evidence 3 seam rate",
         f"{art[('evidence_law', 3)]['nonStatutePct']}", ["NEXT_PROGRAMME.md"]),
        ("seam rate, structural class",
         f"{seam['byClass']['STRUCTURAL_PROCEDURAL']['nonStatutePct']}",
         ["NEXT_PROGRAMME.md"]),
        ("seam rate, dispute class",
         f"{seam['byClass']['DISPUTE_SPECIFIC']['nonStatutePct']}",
         ["NEXT_PROGRAMME.md"]),
        ("structural precision, gold",
         f"{fg['labels']['structuralPrecision']['correct']} of "
         f"{fg['labels']['structuralPrecision']['n']}", []),
        ("pairs answered on other law",
         f"{pg['labels']['counts']['ANSWERED_ON_OTHER_LAW']}", []),
        ("hybrid sample ornament count",
         f"{hg['counts']['ORNAMENT']}", []),
        # --- the completeness programme
        ("open-textured pooled",
         f"{cp['byClass']['OPEN_TEXTURED_STANDARD']['judgmentLevelPct']}",
         ["COMPLETENESS.md"]),
        ("open-textured median",
         f"{cp['byClass']['OPEN_TEXTURED_STANDARD']['articleMedianPct']}",
         ["COMPLETENESS.md"]),
        ("institutional median",
         f"{cp['byClass']['INSTITUTIONAL_DIRECTIVE']['articleMedianPct']}",
         ["COMPLETENESS.md"]),
        ("institutional median, unseen",
         f"{cp['byClassUnseenOnly']['INSTITUTIONAL_DIRECTIVE']['articleMedianPct']}",
         ["COMPLETENESS.md"]),
        ("external referral pooled, unseen",
         f"{cp['byClassUnseenOnly']['EXTERNAL_REFERRAL']['judgmentLevelPct']}",
         ["COMPLETENESS.md"]),
        ("matched pairs median delta",
         f"{cp['matchedPairs']['medianDeltaPts']}", ["COMPLETENESS.md"]),
        ("matched pairs sign test",
         f"{cp['matchedPairs']['signTestP']}", ["COMPLETENESS.md"]),
        ("judicial principle, open-textured",
         f"{cp['byClassByAuthority']['OPEN_TEXTURED_STANDARD']['judicial_principle']}",
         ["COMPLETENESS.md"]),
        ("judicial principle, institutional",
         f"{cp['byClassByAuthority']['INSTITUTIONAL_DIRECTIVE']['judicial_principle']}",
         ["COMPLETENESS.md"]),
        ("bench-bar delta, institutional, strict",
         f"{cp['benchVsBar_party']['byClass']['INSTITUTIONAL_DIRECTIVE']}",
         ["COMPLETENESS.md"]),
        ("CTL pooled non-statutory",
         f"{cd['civilTransactionsLaw']['pooledNonStatutePct']}",
         ["COMPLETENESS.md"]),
        ("Evidence pooled non-statutory",
         f"{cd['evidenceLaw']['pooledNonStatutePct']}", ["COMPLETENESS.md"]),
        ("fiqh per statutory citation 1446",
         f"{cd['denominators']['1446']['fiqhPerStatutoryCitation']}",
         ["COMPLETENESS.md"]),
        ("fiqh per 1k reasoned 1446",
         f"{cd['denominators']['1446']['fiqhCitationsPer1000Reasoned']}",
         ["COMPLETENESS.md"]),
        ("silent share", f"{si['silentPct']}", ["COMPLETENESS.md"]),
        ("silent median reason chars",
         f"{si['silent']['medianReasonChars']:,}", ["COMPLETENESS.md"]),
        ("silence in the shortest decile",
         f"{si['byLengthDecile'][0]['silentPct']}", ["COMPLETENESS.md"]),
        ("paired appellate share", f"{ap['pairedShare']}", ["COMPLETENESS.md"]),
        ("disturbed, non-statute only",
         f"{ap['byShape']['nonstatute_only']['disturbedPct']}",
         ["COMPLETENESS.md"]),
        ("statute-only retrieval omission",
         f"{rg['estimateReasonedJudgmentsWhereStatuteOnlyRetrievalOmitsPct']}",
         ["COMPLETENESS.md"]),
        ("named fiqh with a source",
         f"{rg['namedFiqhWithASourcePct']}", ["COMPLETENESS.md"]),
        ("deletable share of codeable",
         f"{hr['deletionTest']['deletablePctOfCodeable']}",
         ["COMPLETENESS.md"]),
        ("supplies the decision rule",
         f"{hr['counts']['SUPPLIES_THE_DECISION_RULE']}", ["COMPLETENESS.md"]),
        # --- the two-layer programme
        ("rule-label agreement",
         f"{af['agreementWithRuleLabels']['pctWhereRuleDecisive']}",
         ["TWO_LAYERS.md"]),
        ("institutional median",
         f"{tl['byClass']['INSTITUTIONAL_OPERATION']['medianPct']}",
         ["TWO_LAYERS.md"]),
        ("dispute median",
         f"{tl['byClass']['DISPUTE_DECISION']['medianPct']}",
         ["TWO_LAYERS.md"]),
        ("mixed pooled", f"{tl['byClass']['MIXED']['pooledPct']}",
         ["TWO_LAYERS.md"]),
        ("institutional median, rule labels",
         f"{tl['byClassRuleLabels']['INSTITUTIONAL_OPERATION']['medianPct']}",
         ["TWO_LAYERS.md"]),
        ("core top10 institutional",
         f"{tl['coreAnatomy']['top10']['INSTITUTIONAL_OPERATION']}",
         ["TWO_LAYERS.md"]),
        ("core top100 institutional",
         f"{tl['coreAnatomy']['top100']['INSTITUTIONAL_OPERATION']}",
         ["TWO_LAYERS.md"]),
        ("core top100 jurisdiction subtype",
         f"{tl['coreAnatomy']['top100']['institutionalSubtypesPctOfAll']['jurisdiction']}",
         ["TWO_LAYERS.md"]),
        ("court dispute share",
         f"{tl['courtVsParty']['court']['DISPUTE_DECISION']}",
         ["TWO_LAYERS.md"]),
        ("party strict institutional share",
         f"{tl['courtVsParty']['party']['INSTITUTIONAL_OPERATION']}",
         ["TWO_LAYERS.md"]),
        ("eta2, procedural/substantive",
         f"{tl['explanatoryPower']['A_procedural_substantive']['etaSquared']}",
         ["TWO_LAYERS.md"]),
        ("eta2, institutional/dispute",
         f"{tl['explanatoryPower']['C_institutional_dispute']['etaSquared']}",
         ["TWO_LAYERS.md"]),
        ("eta2, instrument identity",
         f"{tl['explanatoryPower']['D_instrument']['etaSquared']}",
         ["TWO_LAYERS.md"]),
        ("hold-out MAE, instrument",
         f"{tl['explanatoryPower']['D_instrument']['holdoutMAE']}",
         ["TWO_LAYERS.md"]),
        ("arbitration hybrid rate",
         f"{ec['profiles']['arbitration_law']['hybridPct']}",
         ["TWO_LAYERS.md"]),
        ("law practice hybrid rate",
         f"{ec['profiles']['law_practice_law']['hybridPct']}",
         ["TWO_LAYERS.md"]),
        ("CTL maxim rate",
         f"{ec['profiles']['civil_transactions_law']['maxim']}",
         ["TWO_LAYERS.md"]),
        ("CCIR named fiqh rate",
         f"{ec['profiles']['commercial_courts_implementing_regulation']['named_fiqh']}",
         ["TWO_LAYERS.md"]),
        # --- traceability and retrieval
        ("statute book full coverage",
         f"{tr['retrievalUniverses']['A_statute_book']['judgmentsFullyCoveredPct']}",
         ["TRACEABILITY.md"]),
        ("whole-judgment precision",
         f"{tr['retrievalUniverses']['B_whole_judgments']['precisionPct']}",
         ["TRACEABILITY.md"]),
        ("unnamed share of court authority",
         f"{tr['overall']['UNNAMED']}", ["TRACEABILITY.md"]),
        ("named source share",
         f"{tr['overall']['NAMED_SOURCE']}", ["TRACEABILITY.md"]),
        ("fiqh unnamed share",
         f"{tr['byAuthorityType']['fiqh_source']['UNNAMED']}",
         ["TRACEABILITY.md"]),
        ("fully traceable judgments",
         f"{tr['perJudgment']['fullyTraceablePct']}", ["TRACEABILITY.md"]),
        # --- the code-ecology programme
        ("arbitration hybrid", f"{ins['ecology']['arbitration_law']['hybridPct']}",
         ["ECOLOGIES.md"]),
        ("law practice hybrid",
         f"{ins['ecology']['law_practice_law']['hybridPct']}", ["ECOLOGIES.md"]),
        ("law practice concentration",
         f"{ins['ecology']['law_practice_law']['top10ConcentrationPct']}",
         ["ECOLOGIES.md"]),
        ("largest profile distance",
         f"{max(ins['profileDistance'].values())}", ["ECOLOGIES.md"]),
        ("between-instrument variance",
         f"{ins['varianceDecomposition']['byInstrument']['betweenSharePct']}",
         ["ECOLOGIES.md"]),
        ("within-instrument variance",
         f"{ins['varianceDecomposition']['byInstrument']['withinSharePct']}",
         ["ECOLOGIES.md"]),
        ("arbitration article sd",
         f"{ins['varianceDecomposition']['perInstrument']['arbitration_law']['sdPct']}",
         ["ECOLOGIES.md"]),
        ("arbitration standardised",
         f"{ief['stratified']['byInstrument']['arbitration_law']['standardisedPct']}",
         ["ECOLOGIES.md"]),
        ("CCL+arbitration both",
         f"{ief['coCitation']['pairs']['commercial_courts_law | arbitration_law']['bothPct']}",
         ["ECOLOGIES.md"]),
        ("SPL+law practice both",
         f"{ief['coCitation']['pairs']['sharia_procedure_law | law_practice_law']['bothPct']}",
         ["ECOLOGIES.md"]),
        ("arbitration marginal within CCL",
         f"{ief['marginalEffect']['byInstrument']['arbitration_law']['withinCCL_marginalPts']}",
         ["ECOLOGIES.md"]),
        ("leave-one-out MAE",
         f"{ief['leaveOneInstrumentOut']['meanAbsoluteErrorPts']}",
         ["ECOLOGIES.md"]),
        ("leave-one-out null",
         f"{ief['leaveOneInstrumentOut']['nullMeanAbsoluteErrorPts']}",
         ["ECOLOGIES.md"]),
        ("arbitration named-source share",
         f"{ins['ecology']['arbitration_law']['supplementaryNamedSourcePct']}",
         ["ECOLOGIES.md"]),
        ("evidence 1446 hybrid",
         f"{ins['stability']['evidence_law']['1446']['hybridPct']}",
         ["ECOLOGIES.md"]),
        ("CTL party strict hybrid",
         f"{ins['voices']['civil_transactions_law']['party_strict']['hybridPct']}",
         ["ECOLOGIES.md"]),
        ("CTL party wide named fiqh",
         f"{ins['voices']['civil_transactions_law']['party_wide']['named_fiqh']}",
         ["ECOLOGIES.md"]),
    ]
    return out


def main():
    bad = []
    cache = {}
    for label, value, docs in facts():
        for doc in docs:
            text = cache.setdefault(
                doc, (HERE / doc).read_text(encoding="utf-8"))
            if value not in text:
                bad.append(f"  {label} = {value} is not in {doc}")
    checked = sum(len(d) for _, _, d in facts())
    if bad:
        print(f"{len(bad)} figure(s) in the contemporary notes no longer "
              f"match the results:")
        print("\n".join(bad))
        return 1
    print(f"all {checked} guarded figures in the contemporary notes match "
          f"the results files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
