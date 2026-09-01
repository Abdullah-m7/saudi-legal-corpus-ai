# What Preprocessing Does to Legal Retrieval

### A matched-volume control for corpus interventions, tested on 105575 statutory citations

*Evidence from 50666 Saudi commercial judgments*

**Abstract.** Legal AI systems are built on corpora of published judgments
that are cleaned first, and the cleaning is validated by whether it changes a
downstream result. We show that this validation is not sound, and give the
experiment that makes it sound. On a legal retrieval task built entirely from
what Saudi commercial courts actually cited — given the court's reasoning
before a statutory citation, retrieve the article it then cited, 105575
resolved citations, 976 candidate articles, temporally fenced — we compare
the same BM25 retriever across four treatments of the same corpus. Removing
every recurring legal formula takes 31.4 per cent of the index and costs
0.0241 MRR@10; removing the same number of contexts at random costs 0.0089.
The targeted removal is 2.7 times the price of the volume it removes, it
falls outside the spread of 20 size-matched random draws in five of nine
folds, and in the last five folds it beats 0 of 20 draws every time — so in
this corpus the recurring wording is above-average retrieval evidence, and
deleting it as boilerplate deletes the better half of the index. The same
control run on the corpus-level analysis that motivated the intervention
gives the opposite answer, which is exactly why it has to be run: the same
removal is special for one downstream task and not for another, and nothing
short of the control tells a practitioner which case they are in. We apply
the same logic to index staleness, where freezing an index makes it both
older and smaller: of the MRR lost at one, two and four quarters of age,
70, 64 and 62 per cent survives a matched-volume control and is age rather
than size. We state the contribution as a domain-specific validity
requirement rather than as a new ablation concept, which it is not: **when a
preprocessing step removes substantial evidentiary volume from a legal
corpus, its effect on legal-AI evaluation must be compared with a
matched-volume random-removal control before the change is attributed to the
class of text removed.**

**Keywords.** legal information retrieval; corpus construction; deduplication;
temporal generalisation; evaluation validity; Saudi law

---

## 1. Introduction

Between a corpus of published judgments and a legal AI system built on it sit
preprocessing decisions that are made once, justified briefly, and then
inherited by everything downstream. The most common of them is the removal of
recurring text. It is justified by a reasonable-sounding rule: the removed
material is boilerplate, and boilerplate is noise.

The usual evidence for that rule is that removing the text changes a
downstream result. **That evidence is not sound, and the reason is arithmetic
rather than legal.** Removing recurring passages removes a large volume of
data. Removing a large volume of data changes downstream results on its own.
Any experiment that reports the first without controlling for the second has
measured the two together.

The control is one experiment: remove the same *number* of items at random and
see whether the change survives. It is not our idea — matched-budget random
subsets are standard in the data-selection literature (§2) — and we make no
claim to it. What we claim is that in a legal corpus, where the removed
material is evidence rather than web noise, the control has to be a
requirement rather than an option, and that when you actually run it the
answer is not the one either side of the argument expects.

**The question.** Does targeted removal of recurring legal wording change
legal retrieval performance beyond what removing the same amount of corpus
material does anyway? And separately: how much of what a stale index costs is
age, rather than the stale index simply being smaller?

**The instrument.** A legal retrieval task built from what courts actually
did: given the court's own reasoning in the run-up to a statutory citation,
retrieve the article it then cited (§5). 105575 resolved citations, 976
candidate articles, one relevant article per query, temporally fenced, with
every citation span inside a query masked. The task is deliberately standard
and the retriever is deliberately dull — BM25 — because the independent
variable is the corpus, and a change in the score must not be attributable to
anything else.

**What we find.**

- **De-boilerplating is not volume-equivalent here, and it is worse than
  random.** Removing every circulating formula costs 2.7 times what removing
  the same number of contexts at random costs, and lands outside the spread of
  20 size-matched random draws in the five largest-removal folds (§6). The
  recurring wording is above-average retrieval evidence.
- **And on a different downstream task in the same corpus, the same removal
  *is* volume-equivalent** (§6.4). Two tasks, one intervention, opposite
  answers. This is the paper's central methodological point: the control is
  not a formality that confirms what you expected, it is the only thing that
  tells you which of the two worlds you are in.
- **Two thirds of the cost of a stale index is age and one third is size**
  (§7), a decomposition that requires the same control and that we did not
  find reported in the temporal-retrieval literature.
- **Adding the parties' own citations to the index grows it by 11 per cent,
  raises the recall ceiling, and lowers MRR** (§7.3).

**What we contribute**, stated so a reviewer can check the boundary:

1. A domain-specific validity requirement for legal-corpus preprocessing, with
   the experiment that shows what it catches (§6.5).
2. Two measured results on a real legal retrieval task, with their controls
   (§6, §7).
3. A measurement of what the removed material actually is — its unit, its
   volume, and what it does to authority support (§4) — which is what makes
   the intervention worth testing at all.
4. Not the task, not the retriever, and not the concept of a matched-size
   random ablation. All three are borrowed on purpose (§2).

Everything is computed from a public repository with a determinism check, a
figure-tracing guard and frozen baselines; §11 gives the reproduction path.

## 2. Related work and positioning

Four lines of work meet here.

*Deduplication of training corpora.* Removing exact and near duplicates is
standard practice, motivated by memorisation and by the distortion of
frequency statistics [Lee et al., 2022]. The unit is usually the document or a
long span, and the validation is usually intrinsic. The most important
neighbour of this paper is the finding that removing **near** duplicates can
hurt a language model at a cost quantified as equivalent to training on
5-10 per cent less data [(Near) Duplicate Subwords, 2024] — the same
suspicion this paper tests, in a different modality and without a retrieval
task attached.

*Data selection with matched-budget controls.* Comparing a curated subset
against a randomly drawn subset **of the same size** is established
methodology in data-selection work [DataComp-LM, 2024, and the
quality-filtering literature it collects]. We state plainly that the control
in §6 is imported from there and not invented here. What we contribute is the
argument that it should be a **requirement** in a domain where the removed
material is evidence, and the demonstration of what it catches when it is
applied.

*Legal citation-context retrieval.* Retrieving a cited authority from the text
around the citation is an established task [Huang et al., 2021, for case
citations], with temporally-fenced variants that measure exactly the leakage
we control for [Fenced Citation-Context Retrieval, 2026]. For this
jurisdiction, ALARB [2025] already defines regulation identification over
13K Saudi commercial cases. Our task is therefore an **instrument, not a
contribution**: it is deliberately standard, because the independent variable
is the corpus and the retriever must not be interesting.

*Temporal drift and index maintenance.* Persistence of retrieval systems over
a moving corpus has its own evaluation infrastructure [CLEF LongEval] and its
own recent benchmark work [Still Fresh?, 2026]. In law it appears as temporal
validity: retrieving the provision in force at the material date rather than
the one in force now [Temporal Misgrounding in Legal RAG, 2026]. Ageing is not
a new axis. What we did not find is an ageing measurement that controls for
the index also being **smaller** when it is frozen, which is what §7 adds.

Our position is that these four are one problem seen from four distances. All
four treat the corpus as a sample of legal material. It is a sample of what a
publisher released, containing wording that repeats for reasons unrelated to
evidence, changing under a process that is not stationary. This paper measures
those properties and then measures what they do to a retrieval system built on
the same corpus.

> **Note on references.** Citations above are given by name and year rather
> than as a formatted list. Every one of them is recorded in
> `REFERENCES_TODO.md` with its reading status, and almost all are currently
> `ABSTRACT` or `SNIPPET`. None may be cited in a submitted version before it
> has been read in full, and if reading changes what is written here, this
> section changes.

## 3. Data and setting

**The corpus.** Published first-instance and appellate commercial judgments of
the Saudi Ministry of Justice. The AI-subject scan covers **50666** judgments;
the measurement layers used here cover the hijri years 1442–1446, from which
we extract **25213** non-statutory authority mentions across **27027**
judgments carrying a reasoning section, and **105575** resolved statutory
citations with a usable preceding context — **47492** of them in the court's
own reasoning, over **976** distinct (instrument, article) targets across
**68** instruments. The last three figures are the retrieval task of §5.

This corpus family is not unexplored. A published dataset of Saudi commercial
rulings from the same Ministry gateway exists, and ALARB defines a
regulation-identification task over 13K such cases (§2). We do not claim a new
dataset; we claim controlled measurements on one.

**Why this setting.** Saudi commercial judgments carry an unusually wide range
of authority in one document — statute, the parties' contract, named works of
fiqh, maxims of fiqh, Qur'an, hadith, settled judicial principle, commercial
custom, and the court's own named discretion — and the published documents
carry structural headings that separate the recital of the parties' claims
from the court's reasons. Both properties are instrumentally useful: the first
gives a rich authority space in which redundancy is visible; the second lets
every measurement be computed in the court's own voice rather than over a
blend of voices.

**Layers.** Five derived layers are used, and none of them stores judgment
text: a statutory citation layer (instrument and article, by speaker), an
authority mention layer (nine authority types, by speaker), a canonical
identity layer for non-statutory authority (28 canonical identities plus
generic classes), the formula layer defined in §4, and the retrieval layer
defined in §5. The first four record counts and identifiers only. The fifth
records the material BM25 consumes — an unordered bag of hashed tokens per
context, word order destroyed and no token recoverable — which is the weakest
representation that supports the experiment and still cannot be read back as
a passage.

**Time index.** Hijri quarters, 1442Q1–1446Q2, of which ten satisfy a maturity
rule fixed before any outcome was inspected: at least 800 judgments carrying
court authority, at least 200 court statutory citations, a later quarter must
exist, and volume at least 40 per cent of the median of the preceding four
quarters. All time-indexed results below are computed on mature quarters only.

**What the corpus is not.** It is published commercial adjudication. Absence
from it is absence from that record, never absence from Saudi law. Two of the
most active current legal frontiers in the jurisdiction — AI governance and
data protection — are regulated in forums this corpus does not contain, a
point we return to in §9.

## 4. What recurs, and what it is worth before anything is built

The intervention tested in §6 removes recurring wording. This section says
what that wording is, how much of the corpus it is, and what removing it
does to a frequency count — the corpus-level facts that make the
intervention worth testing, and that a practitioner would use to justify it.

### 4.1 The unit

We define an **authority-adjacent recurring formula** as the first 12 hex
characters of the SHA-1 of a normalised window of **90** characters on each
side of a matched authority mention. Normalisation removes diacritics, folds
orthographic variants, collapses whitespace, deletes every character outside
the Arabic letter class — so digits and punctuation are removed — and deletes
words of one or two characters. The surviving token string has a median length
of **29** tokens (p10 **26**, p90 **33**).

Three properties of this unit matter and are stated because they bound every
count below. It is **exact**: a cryptographic hash has no neighbourhood, so a
single differing surviving word is a different formula. It is
**source-preserving**: the matched authority string lies inside the window. And
it is **not a representation of a judgment's language**: it is a fixed-width
neighbourhood of an authority mention, and no claim in this paper is about
judicial writing in general.

We also built a near-duplicate layer — a banded minhash over token 3-shingles,
8 bands of 4 — and set it aside: of 130 pairs grouped at Jaccard 0.7, only
**0.5462** survive at 0.8. The grouping does not survive a change of
threshold at this corpus size, so every count below is exact-match and is
therefore a floor.

### 4.2 How much redundancy there is

Across 25213 mentions there are **14958** distinct formulas. **218** of them
recur in ten or more judgments, accounting for **5981** mentions.

Masking the matched authority string before hashing reduces the distinct count
only from 14958 to **14941**, and **0** of the 218 circulating formulas carry
more than one canonical authority identity. At this resolution, recurrence is
source-bound: there is no observed shell that recurs ten times and receives
different authorities. We record this as an absence of observation rather than
a demonstrated impossibility, since the near-family layer that would catch a
shell varying by one word is the layer we could not stabilise.

### 4.3 What the redundancy does to support

Define **raw support** for an authority as its mention count, and
**formula-adjusted support** as the count in which each circulating formula
contributes once per authority and every non-recurring mention contributes
once. Adjusted support is a floor on the number of independent contexts, not
an estimate of it.

| | raw | adjusted | inflation |
|---|--:|--:|--:|
| all 34 authorities | 25213 | 19450 | **1.296** |
| Ibn Taymiyya | 3129 | 1660 | **1.885** |
| al-Insaf | 884 | 413 | **2.14** |
| unattributed fiqh | 4783 | 3601 | 1.328 |
| untraced hadith | 5009 | 4088 | 1.225 |
| worst single authority (al-Bayhaqi) | — | — | **2.429** |

A frequency-trained or frequency-ranked system over-weights the most
formulaically cited authorities by up to a factor of **2.429**, and by
**1.296** on average.

**This is invisible to document-level deduplication**, which is the standard
remedy. The formulas recur *across* documents, not within them: each judgment
contains the passage once, and the judgments are not duplicates of one
another. No document-level or near-duplicate-document filter removes any of
it.

### 4.4 What it does to ranking, and what it does not do to trend

Ranking authorities by adjusted rather than raw support moves **21** of 34 at
least one place; the largest displacement is 5 places (al-Bayhaqi). Top-10
stability is **0.9**: one authority enters the top ten under deduplication
(muttafaq ʿalayh) and one leaves it (al-Insaf).

The temporal shape, by contrast, is essentially untouched: the raw and
adjusted quarterly series correlate at **0.9976**, and the inflation ratio
moves only from **1.0846** in the first mature quarter to **1.099** in the
last.

The engineering reading is specific. **Formula redundancy changes the level
and the ranking of apparent support and not its shape over time.** A system
that ranks authorities is affected; a system that reports a trend is not. A
practitioner who needs only the trend can ignore this; one who ranks, weights
or retrieves cannot.

### 4.5 What the recurring formulas are

Each circulating formula is assigned a class from a coarse mechanical taxonomy
built from keyword markers with a fixed priority — no model, no learned
labels, and no reading of any passage. The classes are dominated not by
procedural boilerplate but by the framing of authority:

| class | formulas |
|---|--:|
| authority introduction frame | 46 |
| generic reasoning | 46 |
| authority quotation | 43 |
| compensation and harm | 36 |
| burden and presumption | 21 |
| doctrinal rule | 9 |
| disposition | 5 |
| procedural operation | 5 |
| contract | 4 |
| jurisdiction | 2 |
| fact recital | 1 |

**Procedural boilerplate is 5 of 218.** Anyone deleting this material as
boilerplate is mostly deleting the sentences in which courts introduce, quote
and apply authority. §6 measures what that costs a retriever.

## 5. The experiment

### 5.1 The task

> Given the court's own reasoning in the 600 characters before a statutory
> citation, retrieve the article the court then cited.

Nothing in it is synthetic. The query is text a Saudi commercial court wrote.
The label is the citation that court then made, resolved by the same
instrument matcher every other measurement in this paper uses. Relevance is
never judged by us, and there is exactly one relevant article per query.

A corpus pass over the five hijri years yields **105575** resolved statutory
citations carrying a usable context window, of which **47492** are in the
court's own reasoning, over **976** distinct (instrument, article) targets
across **68** instruments. No judgment text is stored: the context is written
out as an unordered bag of hashed tokens, which is all BM25 consumes and which
cannot be read back as a passage.

The task is **not a contribution**. Retrieving a cited authority from its own
local context is established (§2), and a regulation-identification task
already exists for this jurisdiction. It is used here as an instrument,
because a standard task is what makes four corpus treatments comparable.

### 5.2 The retriever

BM25, k1 = 1.2, b = 0.75, over one pseudo-document per article, pooled from
the contexts in which earlier judgments cited that article. Deliberately dull.
The independent variable is the corpus, so the retriever must be simple enough
that a change in the score cannot have come from anywhere else. A dense
retriever would answer a different question and is not run; nothing here is a
claim about what a neural system would do.

One efficiency device exists — postings whose idf falls below a floor are
dropped — and it is reported because it **never fired**: the dropped share is
0.0 in every fold, so no approximation is in force in any number below.

### 5.3 Leakage

Five controls are structural, applied when the layer is extracted and before
any split exists, and one is an experiment in its own right.

1. The query window ends where the citation begins, so the answer is never
   inside its own query.
2. Every statutory citation span **inside** a query window is masked. A second
   citation of the same article nearby cannot leak it, and the instrument's
   name cannot either.
3. The window is clipped to its segment: a citation in the reasons never reads
   the recital.
4. The split is temporal. The index holds strictly earlier quarters, so a
   query's own judgment can never be in the index.
5. Circulating formulas are recomputed **on each fold's own index**, never on
   the whole corpus — reading recurrence off the full corpus would let a fold
   see its own future.
6. `RAW_NO_FP_LEAK` prices what remains: drop every index context whose
   fingerprint also occurs in a query this fold.

Control 6 is not a formality. It costs **0.0643** MRR@10 — more than
de-boilerplating costs. Verbatim recurrence between index and query is a real
part of what this retriever scores, and every figure below should be read as
including it except the `RAW_NO_FP_LEAK` row itself.

### 5.4 Folds and metrics

Ten folds, on `horizon.py`'s SCORABLE quarters — the maturity rule fixed
before any outcome here was inspected and reused unchanged. Queries are capped
at **1000** per fold, sampled once with seed **20260901**, and **shared by
every arm**, so arms are compared on identical queries.

Recall@1, @5, @10 and MRR@10, micro-averaged within a fold and then averaged
over folds, reported beside the index size and the share of queries whose gold
article is in the index at all — the ceiling on recall for that arm. nDCG is
omitted deliberately: with one relevant document per query it is a monotone
transform of the reciprocal rank.

### 5.5 What is varied

Only the index.

| arm | index |
|---|---|
| RAW | every court-reasoning context from earlier quarters |
| FORMULA_DEDUP | minus contexts sitting in a circulating formula |
| MATCHED_RANDOM | minus the same *number* of contexts, at random, 20 seeded draws |
| FROZEN_kQ | cut back k quarters — corpus ageing |
| FROZEN_kQ_VOLUME | minus the number of contexts freezing removed, at random, 10 seeded draws |
| PLUS_PARTY | court contexts plus the parties' own citation contexts |
| RAW_NO_FP_LEAK | RAW minus any context whose fingerprint occurs in a query |

### 5.6 Every arm, every metric

Means over folds, so that nothing quoted later has to be taken on trust.
`gold in index` is the share of queries whose gold article is in the index at
all — the ceiling on recall for that arm.

| arm | R@1 | R@5 | R@10 | MRR@10 | gold in index | contexts | articles | folds |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| RAW | 0.5026 | 0.7556 | 0.8105 | 0.6136 | 0.9248 | 18673 | 504 | 10 |
| FORMULA_DEDUP | 0.4708 | 0.7462 | 0.8093 | 0.5895 | 0.9229 | 12805 | 498 | 10 |
| MATCHED_RANDOM | 0.4946 | 0.7492 | 0.8027 | 0.6047 | 0.9188 | 12805 | 446 | 10 |
| PLUS_PARTY | 0.4994 | 0.7542 | 0.8115 | 0.6102 | 0.9318 | 20712 | 612 | 10 |
| RAW_NO_FP_LEAK | 0.4278 | 0.7115 | 0.7789 | 0.5493 | 0.9089 | 15992 | 501 | 10 |
| FROZEN_1Q | 0.4422 | 0.6921 | 0.7474 | 0.5491 | 0.8915 | 15059 | 432 | 10 |
| FROZEN_1Q_VOLUME | 0.4857 | 0.7374 | 0.7923 | 0.5942 | 0.9086 | 15059 | 450 | 10 |
| FROZEN_2Q | 0.3872 | 0.6224 | 0.6759 | 0.4875 | 0.821 | 11964 | 361 | 10 |
| FROZEN_2Q_VOLUME | 0.4619 | 0.7085 | 0.7654 | 0.5685 | 0.882 | 11964 | 391 | 10 |
| FROZEN_4Q | 0.3202 | 0.5394 | 0.5929 | 0.4146 | 0.7232 | 7685 | 267 | 9 |
| FROZEN_4Q_VOLUME | 0.4282 | 0.6841 | 0.7431 | 0.5373 | 0.8582 | 7685 | 307 | 9 |

`FROZEN_4Q` and its control score 9 folds rather than 10: the earliest fold has
no index left four quarters back.

## 6. Result 1: de-boilerplating costs more than its volume

### 6.1 The headline

| arm | R@1 | R@5 | R@10 | MRR@10 | gold in index | contexts | articles |
|---|--:|--:|--:|--:|--:|--:|--:|
| RAW | 0.5026 | 0.7556 | 0.8105 | **0.6136** | 0.9248 | 18673 | 504 |
| FORMULA_DEDUP | 0.4708 | 0.7462 | 0.8093 | **0.5895** | 0.9229 | 12805 | 498 |
| MATCHED_RANDOM | 0.4946 | 0.7492 | 0.8027 | **0.6047** | 0.9188 | 12805 | 446 |

Removing the circulating formulas takes the mean index from 18673 contexts to
12805 — **31.4** per cent of it — and costs **0.0241** MRR@10. Removing the
same number of contexts at random costs **0.0089**. The targeted removal is
**2.7 times** the price of the volume it removes.

### 6.2 The per-fold test

A difference of two means is the weak version of this. Each fold has its own
distribution of 20 size-matched random draws, and the question is whether the
targeted removal lands outside it.

| fold | circulating formulas | contexts removed | share | outside the random spread | draws beaten, of 20 |
|---|--:|--:|--:|---|--:|
| 1443Q1 | 0 | 0 | 0.0 | removed nothing | — |
| 1443Q3 | 7 | 101 | 0.1132 | no | 6 |
| 1443Q4 | 33 | 690 | 0.2286 | no | 1 |
| 1444Q1 | 64 | 1402 | 0.2675 | no | 13 |
| 1444Q2 | 133 | 3203 | 0.2808 | **yes** | 0 |
| 1444Q3 | 228 | 5921 | 0.2959 | no | 1 |
| 1444Q4 | 307 | 8178 | 0.3099 | **yes** | 0 |
| 1445Q1 | 372 | 10416 | 0.321 | **yes** | 0 |
| 1445Q4 | 479 | 13973 | 0.3297 | **yes** | 0 |
| 1446Q1 | 500 | 14792 | 0.3313 | **yes** | 0 |

`DEDUP_EFFECT_EXCEEDS_VOLUME_EFFECT`. The targeted removal sits inside the
random spread in 4 of the 9 folds in which it removed anything, and those are
the four smallest removals; in the last five folds it beats **0 of 20** draws
every time. Across live folds it beats **2.3333** draws on average out of 20.

There is a dose-response shape here that we did not design for: as the index
grows and the removal share rises from 0.113 to 0.331, the targeted removal
moves from indistinguishable from random to worse than every draw.

### 6.3 What that means about the removed text

**The recurring wording is above-average retrieval evidence.** Removing it is
not cleaning; on this task it is deleting the better half of the index.

The shape of the disagreement is worth one sentence more, because it is the
opposite of what a practitioner would guess. Deduplication keeps **498** of
504 articles while random removal keeps **446** — the targeted removal
*preserves the article inventory better* and still loses more. What it takes
is not coverage. It is the evidence per article.

This is consistent with what §4 measured: the circulating formulas are
dominated by authority-introduction frames and quotations rather than by
procedural boilerplate, with procedural operation only 5 of 218. Removing them
removes the sentences in which courts introduce and apply authority, which is
exactly the material a retriever built on citation contexts needs.

### 6.4 The same removal, a different task, the opposite answer

The same corpus supports a second downstream question with a binary verdict:
among non-statutory authorities first observed beside a given code, do those
first observed in the court's voice persist better than those first observed
in the parties'? On the full data the matched comparison returns a court-first
advantage; removing the **5981** mentions in circulating formulas flips it.

We ran the same two controls there. Eleven class-specific removals — one class
of formula at a time — reproduce the flip **not once**. And a size-matched
random removal reproduces it at every level tested, 20 seeded draws each:

| removed | mean mentions removed | flip share |
|---|--:|--:|
| 25 per cent | 1527.2 | 0.1 |
| 50 per cent | 3017.1 | 0.3 |
| 75 per cent | 4514.0 | 0.7 |
| 90 per cent | 5407.1 | 0.9 |

On that task the
targeted removal is volume-equivalent: the matched comparison rests on 6 or 7
pairs in every arm, and a comparison that thin moves when a quarter of the
evidence leaves, whatever leaves.

So: one corpus, one intervention, two downstream tasks, opposite answers about
whether the intervention is special.

**This is the paper's central methodological point, and it is not a
contradiction.** A control that always confirmed the intervention was special
would be worthless, and so would one that never did. The pair shows that
whether removal is volume-equivalent is a property of the *intervention and
the task together*, not of the intervention alone — and therefore that it
cannot be reasoned about in advance. It has to be measured, per task, with the
matched-volume arm.

### 6.5 The requirement

We state the contribution at the level the literature leaves open. Matched-
budget random subsets are established methodology in data selection (§2); we
are importing the control, not inventing it. What is missing is the obligation
to run it where the removed material is evidence:

> **When a preprocessing intervention removes substantial evidentiary volume
> from a legal corpus, its effect on legal-AI evaluation should be compared
> with a matched-volume random-removal control before the change is
> attributed to the semantic class of text removed.**

The cost is one extra arm and a seed. The benefit is the difference between
§6.1 and §6.4 — between a finding and an artefact — and there is no way to
know in advance which one you have.

## 7. Result 2: what index age costs, once shrinkage is taken out

### 7.1 The confound

Freezing an index makes it two things at once: older and smaller. Reported
together they cannot be told apart, and every measurement of staleness we
found reports them together. The fix is the same control as §6: remove the
same number of contexts at random from the live index and see what is left of
the loss.

| index frozen by | MRR@10 loss vs RAW | of which volume | of which age | age share |
|---|--:|--:|--:|--:|
| 1 quarter | 0.0645 | 0.0194 | 0.0451 | **70 %** |
| 2 quarters | 0.1261 | 0.0451 | 0.081 | **64 %** |
| 4 quarters | 0.199 | 0.0763 | 0.1227 | **62 %** |

Roughly two thirds of what a stale index costs is age; one third is the index
being smaller. The two thirds are the part that no amount of index-building
fixes and that only a refresh recovers.

The recall ceiling moves with it. `gold in index` falls 0.9248 → **0.8915** →
**0.821** → **0.7232** as the index is frozen by one, two and four quarters,
while the matched-volume controls hold at **0.9086**, **0.882** and
**0.8582** — so most of the vanishing coverage is articles the court had not
yet begun to cite, not articles thinned out by a smaller index.

### 7.2 Ranking ages faster than recall

The same ageing seen from the ranking side, on the retrieval snapshots the
foresight layer freezes rather than on this BM25 index:

| horizon | citation share to never-seen articles | top-50 displacement (%) | mean rank displacement, top 200 |
|---|--:|--:|--:|
| 1 quarter | **0.0437** | **34.9231** | 33.1885 |
| 2 quarters | 0.0612 | 39.1667 | 36.3225 |
| 4 quarters | 0.1191 | 46.4 | 40.513 |

At one quarter the index is still covering the law — only 4.37 per cent of
citation mass goes to articles it has never seen — while more than a third of
its top fifty is no longer in the court's top fifty. Against thresholds fixed
in advance (30 per cent displacement, 35 rank places, 10 per cent content
gap), the displacement trigger crosses at one quarter, the rank-gap trigger at
two, and the content trigger at four. **A maintenance policy calibrated on
coverage refreshes far too late.**

### 7.3 Staleness is a clock, and party-side material does not pay

Two negative results that a builder can act on.

*Refresh triggers.* Applying the same staleness criterion at pseudo-event
dates on instruments already mature when the window opened, the criterion
fires in **15 of 15** pseudo-events with no legal event at all, and no staged
multi-layer pattern appears in them (share **0.0**). Staleness is a property of
elapsed time. Event-triggered refresh cannot be justified against periodic
refresh on this evidence, and we record the proposal as held rather than
adopted.

*High recall.* Adding the parties' own citation contexts to the index grows it
by **11** per cent (18673 → 20712 contexts, 504 → 612 articles), raises the
recall ceiling from 0.9248 to **0.9318**, and **lowers** MRR@10 from 0.6136 to
**0.6102**. Measured a second way over 13 folds, the party-only remainder
grows the universe by **40.6** per cent, adds **0.0064** of coverage, and
**0.0956** of what it adds is ever cited by a court — **0.157** coverage
points per 10 per cent of universe growth.
`HIGH_RECALL_COSTS_MORE_THAN_IT_BUYS`.

*Which index composition drifts least.* Compared on drift rather than
point-in-time coverage over 5 pseudo-future folds:

| architecture | mean coverage | drift |
|---|--:|--:|
| statute + doctrinal companions | **0.953** | **-0.0108** |
| statute + current article ecology | 0.9417 | -0.0169 |
| time-aware recent window | 0.9287 | -0.0225 |
| statute only | 0.9273 | -0.0308 |
| speaker-aware hybrid | 0.9284 | **-0.0343** |

Adding the non-statutory companion layer to a statutory index both raises
coverage and roughly thirds the drift of a statute-only index; the index
enlarged with party-side material drifts most.

## 8. Why the temporal fence in §5 is not enough

The experiment splits on time, which is the accepted remedy for temporal
leakage. The remedy assumes the two sides of the cut are draws from one
process. On this corpus they are not, and the part that moves is not in the
text.

Twenty-two series in five independent metric families — publication, docket
composition, statutory salience, authority ecology and the formula layer —
were scanned with four transparent change-point methods, every statistic
scored against a permutation null built from the series' own values, 2000
permutations, fixed seed, α = 0.05. The whole battery was then pointed at
**200** shuffled redraws of itself to measure what it reports when there is
nothing to report.

| | observed | null (200 shuffled redraws) |
|---|--:|--:|
| metrics with a significant break | **12** of 22 | 0.11 per metric; mean **2.42** metrics per draw |
| multi-layer candidate quarters | **6** | mean **0.365**; **maximum 3** in any draw |

Six multi-layer candidate quarters lies outside the entire null distribution.
`OBSERVED_EXCEEDS_EVERY_NULL_DRAW`. A chronological split on this corpus is
not a split of one process.

And the moving part is the one a text-only pipeline cannot see. Asked whether
any of the six candidates survives removing the two families that describe
*what the publisher released* rather than *what courts did*: **none of six**.

| family | metrics tested | firing | share |
|---|--:|--:|--:|
| docket composition | 6 | 5 | **0.8333** |
| formula layer | 4 | 3 | 0.75 |
| publication | 4 | 2 | 0.5 |
| statutory salience | 4 | 2 | 0.5 |
| **authority ecology** | 4 | **0** | **0.0** |

The authority ecology — hybrid rate, named-source share, source concentration,
traceability — carries no significant break at all. The standard hope that a
target unstable across a window is stable within regimes does not survive
testing either: with rolling origins where the break is re-detected on history
alone at each origin, segmentation improves forecasting on **0 of 22** series
against a last-value baseline.

For this paper the consequence is narrow and should be read narrowly. Our
temporal fence prevents a query's own judgment from being indexed; it does not
make the folds exchangeable, and the ageing decomposition in §7 is measured
across a publication-composition shift that we can detect and cannot remove.
Every fold-level figure carries that.

## 9. The setting: AI is permitted in this procedure and absent from these disputes

This section is context, and we mark it as context. **It does not carry the
paper's claim to a venue** — §5 to §7 do that, and would stand if this section
were deleted. What it establishes is that the systems the preceding sections
are about are not hypothetical in this jurisdiction. Both facts are quoted
from enacted instruments rather than asserted.

**The forum already permits AI in its own procedure.** The implementing
regulation of the very statute governing the courts whose judgments we measure
provides:

> «يجوز الاستفادة من تقنيات الذكاء الاصطناعي في الإجراءات الإلكترونية،
> ويستغنى عن أي إجراء تحققت غايته باستخدام تلك التقنية.»
> — اللائحة التنفيذية لنظام المحاكم التجارية، المادة الرابعة والعشرون

and the procedural manuals of the Law of Evidence provide:

> «يجوز الاستعانة بالتقنيات الحديثة في إجراءات الإثبات، بما في ذلك الذكاء
> الاصطناعي، ويُستغنى عن أي إجراء تحققت غايته باستخدام هذه التقنيات.»
> — الأدلة الإجرائية لنظام الإثبات، المادة الثالثة والعشرون

Two further instruments permit AI in notarisation and in the delivery of
enforcement services. These are permissions to use AI *in the procedure that
produces the record we measure*.

**And AI is the subject of none of the disputes.** An AI-subject radar over all
**50666** judgments returns **0** at the materiality level — no judgment in
which an algorithmic or AI feature is shown to be at issue in the dispute —
against **28** judgments in which an AI-relevant technology appears without
being shown to be at issue, and **12** carrying an explicit AI term anywhere
in the document.

The conjunction is the point. **Permission is present; consequence is
untested.** A retrieval layer inside this court's own workflow is a permitted
thing to build, and §5 to §7 measure what building it on this corpus costs:
support inflated by up to 2.429 before anything is cleaned, a cleaning step
that removes 2.7 times its own volume in retrieval performance, an index
losing 0.0451 MRR@10 to age alone in a single quarter, and a train/test split
that straddles a publication-composition break.

We make no claim about whether any deployed system is affected. Seven verified
AI adoption events in this jurisdiction were classified on a linkability
ladder and **none** reaches the adjudicatory workflow this corpus observes, so
no deployment can be associated with any observable change here. That is a
statement about linkability and not about effect, and it is precisely why the
corpus-level properties are the part that can be measured today.

## 10. Limitations

**One retriever.** BM25 only. A dense retriever would answer a different
question — how a learned representation responds to the same corpus
treatments — and it is not run. Nothing here is a claim about what a neural
system would do.

**One jurisdiction, one forum.** Published Ministry of Justice commercial
adjudication. The dose-response shape in §6.2 is one corpus's, and the
direction of the §6 result may not hold elsewhere; the *requirement* in §6.5
is what we claim transfers, precisely because the direction does not.

**1000 queries per fold.** A compute budget, not a design choice. The sample
is seeded and shared across arms so it cannot favour one, but a full-query run
would narrow the fold-level intervals.

**The candidate universe is the extractor's.** 976 (instrument, article)
targets, bounded by what the instrument matcher resolves; 28 canonical
identities bound §4.

**Exact-fingerprint resolution.** The redundancy unit is exact; the
near-duplicate layer built to soften it is unstable at this corpus size
(0.5462 pair survival across thresholds). Every redundancy count is a floor,
so §6 removes *less* than a fuzzy de-boilerplating step would, and the price
it measures is a lower bound on that step's price.

**The §6.4 comparison is thin.** The matched doctrinal verdict rests on 6 or 7
pairs in every arm. Its thinness is part of the finding — it is why a quarter
of the evidence leaving moves it — but it means the volume-equivalent side of
the pair is a demonstration that the control is necessary, not a measurement
of how often deduplication misleads.

**No publication date.** The corpus carries a decision date and a retrieval
timestamp, and neither institution publishes a per-judgment publication date.
Decision-to-publication lag cannot be separated from legal change, which is
the confound §8 identifies and cannot remove. It sits underneath §7's ageing
figures.

**Observation lag.** The latest mature quarter is roughly two years behind the
time of writing. Every "current" statement is current-as-published.

**Nothing is causal.** An arm scoring lower is an arm scoring lower.
Co-occurrence of wording is not copying.

**The taxonomy is mechanical.** Formula classes come from keyword presence in
a 180-character neighbourhood. No class is a reading of a passage.

## 11. Reproducibility

All results are computed by scripts in a public repository. Two scripts carry
this paper's experiment: one corpus pass writes the retrieval layer, and one
analysis runs every arm. No judgment text is stored anywhere: the retrieval
layer holds unordered bags of hashed tokens, which is what BM25 consumes and
which cannot be read back as a passage. Three guarantees are enforced in code
rather than asserted:

- **Determinism.** Every analysis is verified byte-identical across runs; all
  output orderings break ties on a stable key.
- **Figure tracing.** Every figure quoted in this manuscript is declared in a
  guard script with the results file and key it comes from, and matched as an
  exact string. The guard fails if any figure drifts.
- **Freshness.** A stamp file hashes the code each result depends on
  transitively, so a result that predates the code that produced it is
  refused.

Baselines used in this paper are frozen with the repository head at which they
were computed, and the freeze scripts refuse to overwrite. Every random arm —
the 20 matched-random draws per fold, the 10 volume-control draws per freeze
horizon, and the query sample itself — is drawn from a seed recorded in the
results file, and the whole experiment was re-run from scratch and verified to
produce byte-identical output.

## 12. Conclusion

We set out to find whether a standard corpus-cleaning step does anything a
random deletion of the same size would not do. On a legal retrieval task built
from 105575 citations Saudi commercial courts actually made, it does: removing
recurring legal wording costs 2.7 times what removing the same volume at
random costs, and in the five folds with the largest removals it is worse than
every one of 20 matched draws. The recurring wording is above-average
retrieval evidence, and it is removed by the operation that calls it
boilerplate.

On a different downstream task in the same corpus, the same removal is
indistinguishable from random. That pair is the result we would most like a
reader to take away. Whether an intervention is special is a property of the
intervention *and the task*, it cannot be reasoned out in advance, and the
only thing that settles it costs one extra arm and a seed.

The same control applied to index staleness separates age from shrinkage and
leaves roughly two thirds of the loss as age at every horizon we tested.

We are not proposing a new ablation technique; matched-budget random subsets
are established elsewhere and we say so. We are proposing that in a domain
where the deleted text is evidence, running the control stops being optional.
