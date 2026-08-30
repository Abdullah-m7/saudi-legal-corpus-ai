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
| **9** | appellate 95.6 % procedural vs first instance 93.2 %, p < .001 | not recomputed by voice | — | a uniform +5.3 pt shift would not move a *difference*; a non-uniform one might | not submitted | **NOT_YET_MEASURED** — do not assume NO_CHANGE |
| **7** | shares the same measurements | same deltas as 8 and 10 | — | Arabic concept, no manuscript to correct | concept only | **NUMERIC_REVISION** before drafting |
| all | citation extractor accuracy: 68.8 % exact, held out, ministry judgments | unchanged | 0 | GSTC_TEST2 measures a *different* source | — | **NO_CHANGE** |
| all | — | committees' digests: **60.9 %** exact [55.8, 65.7], zero-shot | new | bounds any future claim about the committees; no paper makes one | — | **NO_CHANGE** to 7–10 |

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
