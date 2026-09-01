# Legal retrieval under four corpus treatments

`retrieval_layer.py` → `retrieval_layer.jsonl.gz`
`retrieval_experiment.py` → `retrieval_experiment_results.json`

The formula programme ended on a corpus-level negative: removing recurring
wording flipped a matched doctrinal verdict, no class-specific removal
reproduced the flip, and a size-matched random removal did. That result is
about a 6-or-7-pair comparison. It could not settle what recurring wording is
worth, because nothing was built on the corpus.

This pass builds something.

## The task

> Given the court's own reasoning in the 600 characters before a statutory
> citation, retrieve the article the court then cited.

Nothing is synthetic. The query is text a Saudi commercial court wrote; the
label is the citation that court then made, resolved by `match_instruments`;
relevance is never judged by us. One relevant article per query.

**105,575** resolved statutory citations carry a usable context window.
**47,492** of them are in the court's own reasoning, over **976** distinct
(instrument, article) targets across **68** instruments.

## The retriever

BM25, k1 = 1.2, b = 0.75, one pseudo-document per article pooled from the
contexts in which earlier judgments cited it. Deliberately dull: the
independent variable is the corpus, so the retriever must be simple enough
that a change in the score can only have come from the corpus. The idf floor
that exists to keep the postings lists short **never fired** — the dropped
share is 0.0 in every fold — so no approximation is in force.

## Leakage

Six controls, five of them structural rather than statistical.

1. The query window ends where the citation begins. The answer is never in
   its own query.
2. Every statutory citation span **inside** a query window is masked, so a
   second citation of the same article nearby cannot leak it and the
   instrument's name cannot either.
3. The window is clipped to its segment: a citation in the reasons never
   reads the recital.
4. Temporal split. The index holds strictly earlier quarters, so a query's own
   judgment is never in the index.
5. Circulating formulas are recomputed **on each fold's own index**, never on
   the whole corpus. Reading recurrence off the full corpus would let a fold
   see its own future.
6. `RAW_NO_FP_LEAK` prices what verbatim overlap is worth: drop every index
   context whose fingerprint also occurs in a query this fold.

Control 6 is not a formality. Dropping shared fingerprints costs
**0.0643** MRR — more than de-boilerplating costs. Verbatim recurrence between
index and query is a real part of what BM25 is scoring here, and any figure
in this note should be read as including it unless it is the
`RAW_NO_FP_LEAK` row.

## Ten folds, identical queries

The maturity rule is `horizon.py`'s, unchanged: the same ten SCORABLE
quarters every other time-indexed result here uses. Queries are capped at
**1000** per fold, sampled once with seed **20260901** and **shared by every
arm**, so arms are compared on identical queries.

## What each arm scores

Means over 10 folds. `goldInIndex` is the share of queries whose gold article
is in the index at all — the ceiling on recall for that arm.

| arm | R@1 | R@5 | R@10 | MRR@10 | goldInIndex | contexts | articles |
|---|--:|--:|--:|--:|--:|--:|--:|
| RAW | 0.5026 | 0.7556 | 0.8105 | **0.6136** | 0.9248 | 18673 | 504 |
| FORMULA_DEDUP | 0.4708 | 0.7462 | 0.8093 | **0.5895** | 0.9229 | 12805 | 498 |
| MATCHED_RANDOM | 0.4946 | 0.7492 | 0.8027 | **0.6047** | 0.9188 | 12805 | 446 |
| PLUS_PARTY | 0.4994 | 0.7542 | 0.8115 | 0.6102 | 0.9318 | 20712 | 612 |
| RAW_NO_FP_LEAK | 0.4278 | 0.7115 | 0.7789 | 0.5493 | 0.9089 | 15992 | 501 |
| FROZEN_1Q | 0.4422 | 0.6921 | 0.7474 | 0.5491 | 0.8915 | 15059 | 432 |
| FROZEN_1Q_VOLUME | 0.4857 | 0.7374 | 0.7923 | 0.5942 | 0.9086 | 15059 | 450 |
| FROZEN_2Q | 0.3872 | 0.6224 | 0.6759 | 0.4875 | 0.821 | 11964 | 361 |
| FROZEN_2Q_VOLUME | 0.4619 | 0.7085 | 0.7654 | 0.5685 | 0.882 | 11964 | 391 |
| FROZEN_4Q | 0.3202 | 0.5394 | 0.5929 | 0.4146 | 0.7232 | 7685 | 267 |
| FROZEN_4Q_VOLUME | 0.4282 | 0.6841 | 0.7431 | 0.5373 | 0.8582 | 7685 | 307 |

nDCG is not reported. With exactly one relevant document per query it is a
monotone transform of the reciprocal rank and would carry no information
MRR@10 does not already carry.

## RESULT 1 · de-boilerplating costs more than its volume

Removing the circulating formulas takes the mean index from 18673 contexts to
12805 — **31.4 %** of it — and costs **0.0241** MRR. Removing the same number of contexts at random
costs **0.0089**. The targeted removal is **2.7 times** the price of the
volume it removes.

The per-fold test is stronger than the difference of two means. Each fold has
its own distribution of 20 size-matched random draws, and the question is
whether the targeted removal lands outside it:

| fold | circulating | contexts removed | share | inside the random spread? | draws it beats, of 20 |
|---|--:|--:|--:|---|--:|
| 1443Q1 | 0 | 0 | 0.0 | — (removed nothing) | — |
| 1443Q3 | 7 | 101 | 0.1132 | yes | 6 |
| 1443Q4 | 33 | 690 | 0.2286 | yes | 1 |
| 1444Q1 | 64 | 1402 | 0.2675 | yes | 13 |
| 1444Q2 | 133 | 3203 | 0.2808 | **no** | 0 |
| 1444Q3 | 228 | 5921 | 0.2959 | yes | 1 |
| 1444Q4 | 307 | 8178 | 0.3099 | **no** | 0 |
| 1445Q1 | 372 | 10416 | 0.321 | **no** | 0 |
| 1445Q4 | 479 | 13973 | 0.3297 | **no** | 0 |
| 1446Q1 | 500 | 14792 | 0.3313 | **no** | 0 |

`DEDUP_EFFECT_EXCEEDS_VOLUME_EFFECT`. It sits inside the spread in 4 of the 9
folds where it removed anything — and those are the four smallest removals.
In the last five folds it beats **0 of 20** random draws every time, and
across live folds it beats **2.3333** on average.

**The recurring wording is above-average retrieval evidence.** Deleting it is
not cleaning; it is deleting the better half of the index. Note the shape of
the disagreement: dedup keeps **498** of 504 articles while random removal
keeps **446**, so the targeted removal preserves the article inventory and
still loses more — the loss is in the evidence per article, not in coverage.

### This does not contradict the corpus-level result, and the pair is the point

`formula_analysis_results.json` PHASE 9b found that a random removal of the
same size flipped the doctrinal verdict as often as the targeted one. Here
the targeted removal is clearly worse than random. Same corpus, same removal,
two downstream tasks, opposite answers about whether the removal is special.

That is the argument for the control, not against it. **Neither result is
knowable without running the matched-volume arm**, and a practitioner who
runs the intervention and reports the change has no way to tell which of
these two worlds they are in.

## RESULT 2 · index age, with the shrinkage taken out

Freezing an index makes it both older and smaller. Reported together, the two
are confounded; here they are separated by removing the same number of
contexts at random from the live index.

| frozen by | MRR loss vs RAW | of which volume | of which age | age share |
|---|--:|--:|--:|--:|
| 1 quarter | 0.0645 | 0.0194 | 0.0451 | 70 % |
| 2 quarters | 0.1261 | 0.0451 | 0.081 | 64 % |
| 4 quarters | 0.199 | 0.0763 | 0.1227 | 62 % |

Roughly two thirds of the cost of a stale index is age and one third is size.
The age component is the part no amount of index-building fixes; only a
refresh does. Recall ceiling falls with it: `goldInIndex` drops 0.9248 →
0.8915 → 0.821 → 0.7232, while the volume controls hold at 0.9086, 0.882 and
0.8582.

## RESULT 3 · adding the parties' citations does not pay

`PLUS_PARTY` grows the index by **11 %** (18673 → 20712 contexts, 504 → 612
articles), raises the recall ceiling from 0.9248 to 0.9318 — and **lowers**
MRR from 0.6136 to 0.6102. The speaker programme's finding survives being
made operational: party-side material widens the universe faster than it
helps the court's own citations be found.

## Limitations

- **One retriever.** BM25 only. A dense retriever would answer a different
  question and is not run: nothing here is a claim about what a neural system
  would do, only about what the corpus does to a transparent one.
- **The task is not novel and is not meant to be.** Citation-context
  retrieval is established. It is used here as an instrument.
- **1000 queries per fold.** A compute budget, not a design choice. The
  sample is seeded and shared across arms, so it cannot favour an arm, but a
  full-query run would narrow the fold-level intervals.
- **The article inventory is the extractor's.** 976 targets, bounded by what
  `match_instruments` resolves.
- **Nothing here is causal.** An arm scoring lower is an arm scoring lower.
