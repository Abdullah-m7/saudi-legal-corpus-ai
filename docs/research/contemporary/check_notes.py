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
