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
            "provenance": (
                "outcomes are scans of authority_mentions.jsonl.gz; features "
                "are computed from the enacted text in the corpus registry "
                "except domain and codificationRelation, which are hand "
                "fields assigned from the registry note and the statute's "
                "own chapter headings, never from behaviour"),
        })
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} instruments -> {OUT.name}")


if __name__ == "__main__":
    main()
