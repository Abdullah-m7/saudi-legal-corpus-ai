# Claim delta: what this session's measurements do to Papers 7–10

Three new measurements were made: GSTC_TEST2 (a zero-shot held-out estimate
for the committees' digests), the full-corpus recomputation of citation uptake
by voice, and the extraction audit's finding of a fourth corruption family.
This table says, for each paper, what moved.

The `uptake_by_voice.py` pipeline reproduces **every published article-level
share exactly** in its `ALL_TEXT` column — Commercial Courts Law 99.0,
Civil Transactions 27.5, Companies 71.2, Bankruptcy 51.9, Evidence 90.7 —
so the new column is a like-for-like extension of the published measurement
and not a different measurement that happens to disagree.

## The delta

| # | old measure | new measure | delta | interpretation | manuscript | action |
|---|---|---|---|---|---|---|
| **8** | Commercial Courts Law: **99.0 %** of articles cited | court's own reasoning only: **77.1 %** | −21.9 pt | the procedural half of the title is a whole-text figure | **submitted**, JELS MS 4582420, *In Screening* | **NUMERIC_REVISION** — revision note drafted below; nothing edited |
| **8** | Civil Transactions Law: **27.5 %** | court's own reasoning only: **12.5 %** | −15.0 pt, a halving | the code half of the title is a whole-text figure | same | **NUMERIC_REVISION** |
| **8** | the contrast the title states: 99 vs 27, a ratio of **3.6×** | 77.1 vs 12.5, a ratio of **6.2×** | +2.6× | the paper's thesis is *strengthened*: the gap it reports is wider in the court's own voice | same | **NUMERIC_REVISION**, direction unchanged |
| **8** | procedural share **89.2 %** | **94.5 %** | +5.3 pt | as above | same | **WORDING_TIGHTENING** |
| **10** | articles cited at least once: **11.7 %** of the statute book | **5.71 %** | −6.0 pt, a halving | the central quantity of Paper 10 | **not submitted** (HILJ window Sept–Nov) | **CENTRAL_CLAIM_AFFECTED** — fix before submission, free |
| **10** | reasoning-only procedural share 94.5 %, 68 instruments | unchanged | 0 | already computed and reported by this paper | — | **NO_CHANGE** |
| **9** | appellate 95.6 % procedural vs first instance 93.2 %, p < .001 | 95.5 vs 93.2 under the permissive bound; gap +2.4 → +2.3 | −0.1 pt | now measured on both exposures, see below | not submitted | **NO_CHANGE** — was NOT_YET_MEASURED |
| **7** | shares the same measurements | same deltas as 8 and 10 | — | Arabic concept, no manuscript to correct | concept only | **NUMERIC_REVISION** before drafting |
| all | citation extractor accuracy: 68.8 % exact, held out, ministry judgments | unchanged | 0 | GSTC_TEST2 measures a *different* source | — | **NO_CHANGE** |
| all | — | committees' digests: **60.9 %** exact [55.8, 65.7], zero-shot | new | bounds any future claim about the committees; no paper makes one | — | **NO_CHANGE** to 7–10 |
| all | the extractor sees every citation worth counting | it misses **64,123** more, 55 % again on top of the 116,216 it finds | +55 % in volume | but see the sensitivity bound below: composition barely moves | — | **NO_CHANGE** to 7–10 |

## The extractor's blind spots do not move the claims

Reading 32 whole judgments (`gstc_pilot/MOJ_ARTICLE_GOLD.md`) found seven
citation forms `V.CITE` never matches, chief among them «المادة (59) من ذات
اللائحة» — a modifier between «من» and the instrument word defeats the
pattern outright, and `match_instruments`' anaphora resolver is never
reached. `coverage_sensitivity.py` puts an upper bound on what that costs, by
re-counting the corpus with a deliberately permissive pattern that accepts
all seven forms and resolves anaphora to the last instrument named:

|                                  | published | permissive bound |     move |
| -------------------------------- | --------: | ---------------: | -------: |
| citations                        |   116,216 |          180,339 | **+55 %** |
| instruments ever cited           |       106 |              107 |       +1 |
| procedural share of citations    |    89.2 % |           89.7 % | +0.5 pt |
| top-10 instruments' share        |    96.9 % |           96.9 % |       0 |
| distinct articles ever cited     |     1,849 |            1,981 |    +132 |
| share of the statute book cited  |   11.66 % |          12.49 % | +0.83 pt |

The published column is not a re-statement: it is recomputed here from the
corpus in the same pass and reproduces `UPTAKE.md`'s ALL_TEXT column to the
digit — 116,216 citations, 89.2 %, 1,849 articles, 11.66 %.

**Fifty-five per cent more citations move the concentration claims by half a
point and the coverage claim by eight-tenths of one.** The reason is
structural rather than lucky: the forms the pattern misses are overwhelmingly
anaphoric back-references — «ذات النظام», «هذه اللائحة», «لائحته
التنفيذية», the second member of a list — and a back-reference points at an
instrument the judgment has *already* named. The arithmetic is stark: 64,123
recovered citations add **132** articles that were not already counted, one
new article per 486 recovered citations. The missing citations are missing
where the counted ones already are.

So this is `NO_CHANGE` for Papers 7–10, and it is a stronger `NO_CHANGE` than
"we did not check". Paper 10's `CENTRAL_CLAIM_AFFECTED` above stands on its
own footing: it comes from the *voice* filter, which removes citations, and
this bound only adds them. The two move the same figure in opposite
directions, and neither cancels the other — 11.66 % becomes 5.71 % when
parties' citations are dropped, and at most 12.49 % when the missed forms are
added back.

## Every instrument, three columns

| instrument | own articles | ALL_TEXT | segmentable only | court's reasoning |
|---|---|---|---|---|
| Commercial Courts Law | 96 | 99.0 % | 96.9 % | **77.1 %** |
| Evidence Law | 129 | 90.7 % | 90.7 % | **76.7 %** |
| Arbitration Law | 58 | 93.1 % | 74.1 % | 51.7 % |
| Sharia Procedure Law | 243 | 81.5 % | 70.0 % | 42.4 % |
| Companies Law | 281 | 71.2 % | 61.2 % | 45.6 % |
| Commercial Courts Implementing Regulation | 281 | 65.8 % | 53.7 % | 40.2 % |
| Bankruptcy Law | 231 | 51.9 % | 22.5 % | 14.7 % |
| **Civil Transactions Law** | 721 | **27.5 %** | 24.4 % | **12.5 %** |

The middle column is the control: it holds the segment filter's *sample*
constant so that the difference between it and the third column is voice
alone. For the Bankruptcy Law almost the whole fall is in the first step —
bankruptcy judgments largely do not carry the three headings — and that is
selection, not the parties' voice. For every other instrument the larger fall
is in the second step.

## Paper 9 was exposed twice, and survives both

The `NOT_YET_MEASURED` above was right to refuse `NO_CHANGE` on assumption.
Two things could have moved a *difference* between two levels of court, and
both have now been checked.

**Voice.** Paper 9 turns out to have been in the court's own voice from the
start: `appeal_vs_first.py` confines each level to the span between
«الأسباب:» and «حكمت الدائرة» of that level's own judgment, segmented
document by document. The recomputation that moved Paper 8's figures moved
ALL_TEXT numbers into COURT_REASONING_ONLY, and Paper 9 was already there.
Re-running it reproduces 93.2 and 95.6 exactly.

**The extractor's blind spots.** A uniform miss rate cannot move a
difference, but there was a specific reason to expect a non-uniform one: an
appellate bench restates the instrument named below and then refers back to
it — «من ذات النظام» — and anaphoric back-reference is exactly the form
`V.CITE` misses. If appellate reasons carry more of it, the two levels are
being counted on unequal footing. `appeal_bound.py` re-runs the paired design
unchanged with the permissive pattern added:

| level         | published citations | with the bound | procedural, published | procedural, bound |
| ------------- | ------------------: | -------------: | --------------------: | ----------------: |
| first instance |              4,397 |          6,898 |                93.2 % |            93.2 % |
| appeal         |              2,219 |          3,529 |                95.6 % |            95.5 % |
| **gap**        |                  — |              — |            **+2.4 pt** |       **+2.3 pt** |

The suspicion was correct in direction — the bound adds 59 % to the appellate
side against 57 % to the first-instance side — and immaterial in size. The
gap moves one-tenth of a point.

## Parser v2: two representation repairs, and no claim moves

Two defects found after the held-out sets were opened — Arabic Presentation
Forms, and combining marks on the head noun — are now repaired and frozen as
parser v2 (`gstc_pilot/PARSER_V2.md`). No held-out set was re-opened: 27.7,
68.8 and 60.9 per cent exact stay attached to v1, the code that produced them.
Every corpus analysis that depends on `CITE` was re-run.

| figure the papers quote | v1 | v2 | move |
|---|---:|---:|---:|
| citations found, whole corpus | 121,207 | 123,535 | +2,328 (+1.9 %) |
| procedural share, all text | 89.2 % | 89.3 % | +0.1 pt |
| procedural share, court's reasons | 94.5 % | 94.5 % | 0 |
| distinct articles, all text | 1,849 | 1,854 | +5 |
| share of the statute book, all text | 11.66 % | 11.69 % | +0.03 pt |
| share of the statute book, court's reasons | 5.71 % | 5.71 % | 0 |
| appellate vs first-instance procedural gap | +2.36 pt | +2.34 pt | −0.02 pt |

`check_docs.py` re-run after all of it: **all 77 guarded figures still
match**. Every move is below the precision at which the papers state their
numbers. `NO_CHANGE` for Papers 7–10 on this axis, and the classification
above is untouched.

The article-level gold returns *identical* v1 and v2 figures — precision
88.1 %, recall 67.6 % — because none of its 32 hand-read judgments carries a
mark or a shaped glyph inside a citation.

## Classification, and why not stronger

Nothing here says a published number is **wrong**. Every one of them is a
correct count of citations in judgment text. What the new column adds is that
they are counts *including the parties' arguments as the court reports them*,
and the papers' sentences are about what courts apply.

For Paper 8 that is a `NUMERIC_REVISION` and not a `CENTRAL_CLAIM_AFFECTED`,
because the thesis — an applied law that is overwhelmingly procedural, and a
civil code the courts have barely reached — is *more* true in the court's own
voice than in the whole text. A revision that changed 99/27 to 77/12 would
argue the same case with a wider gap.

For Paper 10 it is `CENTRAL_CLAIM_AFFECTED`, because that paper's central
quantity *is* the article-level uptake share, and 11.7 versus 5.71 is a factor
of two in the number it argues from. It is not submitted, so this costs
nothing but the recomputation.

## Revision note — DRAFT, NOT SENT

The manuscript is with a journal. **It has not been edited, and this note has
not been sent.** Whether to send it, and when, is the author's decision. It is
drafted here so that the decision is made against a text rather than from
memory.

> **To:** Journal of Empirical Legal Studies, editorial office
> **Re:** MS 4582420, *99 Per Cent of the Procedure, 27 Per Cent of the Code*
>
> Since submission I have completed a measurement that the manuscript itself
> identifies as outstanding: the article-level counts restricted to the
> segment of each judgment in which the court gives its own reasons, rather
> than the whole text.
>
> The manuscript's figures are correct as stated — they count every citation
> in a judgment. The new measurement reports the same quantities restricted to
> the court's own voice, on the 27,321 of 50,666 judgments (53.9 per cent)
> whose headings allow the segmentation. Restricted that way, the Commercial
> Courts Law share falls from 99.0 to 77.1 per cent and the Civil Transactions
> Law share from 27.5 to 12.5 per cent, so the contrast the title states
> widens from 3.6-fold to 6.2-fold. The corpus-wide procedural share rises
> from 89.2 to 94.5 per cent. A control column holding the segmentable sample
> constant separates this from any selection effect, and the code that
> produces the new column reproduces every published figure exactly in its
> unrestricted setting.
>
> The direction of every finding is unchanged and the contrast is wider, so I
> do not believe the paper's argument is affected. I would rather the record
> show that I reported it than that a reviewer found it. I am happy to supply
> a revised manuscript at whatever point in the process the editors prefer, or
> to leave the submitted version standing and note the measurement in a
> response to reviewers.

## What must not happen

* The submitted PDF is not edited. The figures in `applied_law_paper/` stay as
  submitted until the author decides otherwise.
* `numbers.tex` is not rewritten to the new column. `check_numbers.py` guards
  the published figures against hand-typing, and silently changing what it
  guards would defeat it.
* Nothing is sent to any journal from this repository.
