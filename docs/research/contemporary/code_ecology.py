#!/usr/bin/env python3
"""The code ecology layer: one row per statute book.

The article layer (`article_function.csv`) answers questions about provisions.
This answers questions about codes, which is where the largest single effect
in the programme turned out to live. Predictor columns come from the enacted
text and the registry; outcome columns come from the mention layer; nothing
crosses.

    python3 code_ecology.py
"""
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
INST = HERE / "instruments_results.json"
EFF = HERE / "instrument_effect_results.json"
DOC = HERE / "docket_test_results.json"
OUT = HERE / "code_ecology.csv"

FEAT = ["articlesInRegistry", "medianArticleWords", "crossRefPerArticle",
        "shariaReferenceSharePct", "customReferenceSharePct",
        "discretionarySharePct", "openTexturedSharePct",
        "delegationSharePct", "subparagraphsPerArticle", "definitionSharePct",
        "commencement", "commencementYear", "yearsObservedTo1446",
        "domain", "codificationRelation"]
ECO = ["judgments", "citations", "distinctArticles", "statuteOnlyPct",
       "hybridPct", "named_fiqh", "maxim", "scripture",
       "judicial_principle", "custom", "top10ConcentrationPct",
       "supplementaryNamedSourcePct"]


def main():
    r = json.loads(INST.read_text(encoding="utf-8"))
    e = json.loads(EFF.read_text(encoding="utf-8"))
    dk = json.loads(DOC.read_text(encoding="utf-8"))
    dstd = dk["standardised"]["byInstrument"]
    dcomp = dk["docketComposition"]
    loc = {w: dk["locality"][w]["byCode"] for w in ("w500", "w1000", "block")}
    strat = e["stratified"]["byInstrument"]
    marg = e["marginalEffect"]["byInstrument"]
    var = r["varianceDecomposition"]["perInstrument"]
    rows = []
    for i in r["instruments"]:
        eco, f = r["ecology"][i], r["features"].get(i, {})
        pw = r["voices"][i]["party_wide"] or {}
        ps = r["voices"][i]["party_strict"] or {}
        st = r["stability"][i]
        rows.append({
            "instrument_id": i,
            "window": "1444-1446",
            **{f"feature_{k}": f.get(k, "") for k in FEAT},
            **{f"court_{k}": eco.get(k, "") for k in ECO},
            "party_wide_judgments": pw.get("judgments", ""),
            "party_wide_hybridPct": pw.get("hybridPct", ""),
            "party_wide_named_fiqh": pw.get("named_fiqh", ""),
            "party_strict_judgments": ps.get("judgments", ""),
            "party_strict_hybridPct": ps.get("hybridPct", ""),
            "court_minus_party_wide_pts": (
                round(eco["hybridPct"] - pw["hybridPct"], 1) if pw else ""),
            "hybrid_standardised_for_citation_load":
                strat.get(i, {}).get("standardisedPct", ""),
            "marginal_effect_pts": marg.get(i, {}).get("marginalPts", ""),
            "marginal_effect_within_CCL_pts":
                marg.get(i, {}).get("withinCCL_marginalPts", ""),
            "article_rate_sd": var.get(i, {}).get("sdPct", ""),
            "article_rate_min": var.get(i, {}).get("minPct", ""),
            "article_rate_max": var.get(i, {}).get("maxPct", ""),
            "years_with_n40": ";".join(
                f"{y}:{v['hybridPct']}" for y, v in sorted(st.items())),
            "hybrid_docket_standardised": dstd.get(i, {}).get("standardisedPct", ""),
            "docket_standardisation_delta_pts":
                dstd.get(i, {}).get("deltaPts", ""),
            "docket_strata_coverage_pct":
                dstd.get(i, {}).get("strataCoveragePct", ""),
            "docket_claimmix_distance_from_corpus":
                dcomp.get(i, {}).get("claimFamilyDistanceFromCorpus", ""),
            "docket_contested_pct": dcomp.get(i, {}).get("CONTESTED", ""),
            "docket_median_reason_chars":
                dcomp.get(i, {}).get("medianReasonChars", ""),
            "local_coauthority_w500_pct":
                (loc["w500"].get(i) or {}).get("localCoAuthorityPct", ""),
            "local_coauthority_block_pct":
                (loc["block"].get(i) or {}).get("localCoAuthorityPct", ""),
            "local_mentions_in_multicode_judgments":
                (loc["w500"].get(i) or {}).get("mentions", ""),
            "provenance": (
                "outcomes are scans of authority_mentions.jsonl.gz; features "
                "are computed from the enacted text in the corpus registry "
                "except domain and codificationRelation, which are hand "
                "fields assigned from the registry note and the statute's "
                "own chapter headings, never from behaviour. Docket columns "
                "are read from the recital only, which precedes the reasoning; "
                "local co-authority is co-occurrence inside a character window "
                "in judgments citing two or more codes, and is not a claim "
                "that the authority supplements the code"),
        })
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} instruments -> {OUT.name}")


if __name__ == "__main__":
    main()
