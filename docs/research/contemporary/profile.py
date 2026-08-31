#!/usr/bin/env python3
"""One generated profile of contemporary published commercial adjudication.

Every number is read from a results file written by the analysis that
produced it; nothing here is typed. It is a profile of *published commercial
judgments of 1444-1446*, and it is named that way on purpose: it is not a
profile of the Saudi judiciary and cannot be made into one.

    python3 profile.py > contemporary_commercial_adjudication_profile.md
"""
import json
from pathlib import Path

H = Path(__file__).resolve().parent
J = lambda n: json.loads((H / n).read_text(encoding="utf-8"))
win, claim = J("windows_results.json"), J("claim_results.json")
ov, ret = J("overlap_results.json"), J("retrieval_results.json")
core, hyb = J("core_view.json"), J("hybrid_view.json")
lia, cf = J("lawinaction_results.json"), J("core_function.json")
V, O = claim["views"]["contemporary_3y"], ov["specs"]["strict"]
C3, W = win["views"]["contemporary_3y"], "contemporary_3y"
T = ["statute", "contract", "fiqh_source", "legal_maxim", "quran", "hadith",
     "judicial_principle", "custom", "discretion"]
p = print

p("# Contemporary commercial adjudication: a generated profile\n")
p("Published Saudi commercial judgments, 1444–1446 AH. Every figure is read")
p("from a results file, by `profile.py`. **Not a profile of the Saudi**")
p("**judiciary**: 95 per cent of this corpus is commercial and it is published")
p("judgments only.\n")

p("## Corpus\n")
p(f"| judgments | {C3['judgments']:,} |")
p("|---|---:|")
p(f"| carrying reasons | {C3['withReasons']:,} ({C3['withReasonsShare']} %) |")
p(f"| median reasons length | {C3['medianReasoningChars']:,} chars |")
p(f"| authority mentions, bench | {V['strict_courtN']:,} |")
p(f"| authority mentions, parties (strict / wide) | "
  f"{V['strict_partyN']:,} / {V['wide_partyN']:,} |\n")

p("## Who invokes what\n")
p("| authority | bench | party (strict) | party (wide) |")
p("|---|---:|---:|---:|")
for t in T:
    p(f"| {t} | {V['strict_court'][t]:.2f} % | {V['strict_party'][t]:.2f} % | "
      f"{V['wide_party'][t]:.2f} % |")

p("\n## How the bench reasons\n")
p("| shape of the reasons | judgments | share |")
p("|---|---:|---:|")
# claim_results carries the shape as a dict with its own denominators;
# map_results states the same four rates without the counts, so read the
# one that lets the reader recompute the percentage.
for k in ("statute_only", "hybrid", "none", "non_statute_only"):
    p(f"| {k.replace('_', ' ')} | {V['shapeN'][k]:,} | {V['shape'][k]} % |")
h45 = hyb["combinations"]["1445"]
p("\nWithin hybrid reasoning, the commonest combinations (1445):\n")
for k, v in list(h45.items())[:5]:
    p(f"- {k} — {v} %")

p("\n## Where the two sides meet\n")
p("| level | median Jaccard | no overlap | identical |")
p("|---|---:|---:|---:|")
for key, lab in (("fam", "authority family"), ("inst_all", "instrument"),
                 ("art_all", "article"),
                 ("art_nostruct", "article, structural removed"),
                 ("art_dispute", "article, dispute-specific only")):
    m = O[key]
    p(f"| {lab} | {m['medianJaccard']:.3f} | {m['noOverlapPct']} % | "
      f"{m['exactMatchPct']} % |")
c = ov["conditional"]["strict"]
p(f"\n- P(shared instrument | both cite statute) = **{c['sharedInstrumentPct']} %**")
p(f"- P(shared article | shared instrument) = **{c['sharedArticleGivenInstrumentPct']} %**")
p(f"- P(shared article | both cite statute) = {c['sharedArticleGivenStatutePct']} %")

p("\n## The operational core\n")
cv = core["views"][W]
p(f"- **{cv['articlesFor50']} articles** carry 50 % of the bench's statutory "
  f"citations; {cv['articlesFor75']} carry 75 %; {cv['articlesFor90']} carry "
  f"90 %; {cv['distinct']:,} distinct articles in all")
k = f"{W}_top50"
p(f"- the top 50 is **{cf[k]['class']['STRUCTURAL_PROCEDURAL']} % structural "
  f"procedural**, {cf[k]['class']['DISPUTE_SPECIFIC']} % dispute-specific, "
  f"{cf[k]['class'].get('AMBIGUOUS', 0)} % ambiguous")
p(f"- by function: " + ", ".join(f"{a} {b} %"
                                 for a, b in list(cf[k]["function"].items())[:5]))
p(f"\n| rank | article | citations | cumulative |")
p("|---:|---|---:|---:|")
for r in cv["top50"][:8]:
    p(f"| {r['rank']} | {r['instrument']} art. {r['article']} | "
      f"{r['citations']:,} | {r['cumulative']} % |")

p("\n## Enacted against operational\n")
inst = lia["instruments"]
p("| instrument | enacted | ever cited by the bench | % |")
p("|---|---:|---:|---:|")
for k2, d in sorted(inst.items(), key=lambda kv: -kv[1]["citations"]):
    p(f"| {k2} | {d['enacted']} | {d['cited']} | {d['share']} % |")

p("\n## What a retrieval system would learn\n")
p(f"Ranking {ret['articlesTotal']:,} articles three ways:\n")
p("| | full ∩ court | full ∩ party | court ∩ party |")
p("|---|---:|---:|---:|")
for k2 in ("10", "50", "100"):
    o = ret[f"overlap@{k2}"]
    p(f"| top {k2} | {o['full_vs_court']} | {o['full_vs_party']} | "
      f"{o['court_vs_party']} |")
p(f"\nSpearman: full/court {ret['spearman']['full_vs_court']}, "
  f"court/party **{ret['spearman']['court_vs_party']}**.\n")
p("## Standing limitations\n")
p("- commercial and published; not the Saudi judiciary")
p("- party attribution is bracketed by two specifications, not solved")
p("- the operational core measures adjudicatory visibility, not legal importance")
p("- six citation forms remain invisible to the extractor, bounded at half a")
p("  point of composition")
p("- one primary annotator; no inter-annotator agreement is claimed")
