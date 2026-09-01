# Not Independent, Not Stable, Not Stationary

### Three measured failure modes in building legal AI on a published court corpus

*Evidence from 50666 Saudi commercial judgments*

**Abstract.** Legal AI is built on corpora of published judgments, and four
assumptions are usually made silently: that a citation count is a count of
independent observations, that removing recurring passages removes
boilerplate, that a retrieval index built today will still rank correctly
tomorrow, and that a chronological evaluation split is a valid test. We test
all four on a corpus of 50666 Saudi commercial judgments and find that each
fails in a way that can be measured. First, authority support is inflated by
recurring wording that document-level deduplication cannot see: counting each
recurring formula once per authority rather than once per mention reduces
total support by a factor of 1.296 overall and up to 2.429 for a single
authority, moves 21 of 34 authorities in the ranking, and leaves the temporal
shape of support untouched (r = 0.9976). Second, and this is the result we
consider most important, the standard remedy does not do what it claims:
removing every recurring passage changes a downstream verdict, but eleven
class-specific removals do not reproduce that change while a size-matched
random removal reproduces it in 0.9 of seeded draws — so recurring-passage
removal is a volume operation, not a wording operation. Third, an index
decays on a clock rather than on legal events: recall ages slowly
(0.0437 citation share to never-seen articles at one quarter) while ranking
ages fast (34.9231 per cent top-50 displacement over the same horizon), and a
staleness criterion fires in 15 of 15 pseudo-events with no legal event at
all. Fourth, the corpus is not one stationary process — 6 multi-layer
candidate breaks against a permutation null that never exceeded 3 in 200
redraws — but not one candidate survives removing the two metric families
that describe what the publisher released rather than what courts did. We
give a size-matched random-removal control that any deduplication claim can
be tested against, a drift-based comparison of five index architectures, and
a permutation-calibrated regime monitor. The setting is not incidental: the
forum whose corpus we measure already permits artificial intelligence in its
own procedure by four explicit provisions, while artificial intelligence is
the subject of 0 of the 50666 judgments scanned. Permission is present;
consequence is untested; and the systems built under that permission will be
built on this corpus.

**Keywords.** legal information retrieval; corpus construction; near-duplicate
detection; temporal generalisation; citation analysis; Saudi law

---

## 1. Introduction

A legal AI system — a retrieval index, a citation recommender, a
fine-tuned model, an evaluation benchmark — is usually built from a corpus of
published judgments. Between the corpus and the system sit four assumptions
that are rarely stated and, so far as we can find, never jointly tested:

1. **Independence.** A citation count over judgments is a count of independent
   observations, so that an authority appearing 3000 times is better
   supported than one appearing 300.
2. **Deduplication.** Recurring passages are boilerplate, and removing them
   removes boilerplate.
3. **Stability.** An index built on the corpus as of today will rank
   acceptably tomorrow, so that maintenance is an operational concern rather
   than a measurement one.
4. **Exchangeability.** A chronological train/test split is a valid test of
   temporal generalisation, because the data-generating process is the same on
   both sides of the cut.

Each is testable. This paper tests all four on one corpus and finds that each
fails, that the failures are of different kinds, and that three of them are
quantifiable in units an engineer can act on. The fourth — exchangeability —
fails in a way that is worse than a quantity: the part of the corpus that
moves is the part a text-only pipeline cannot see.

Our contributions are:

- **A unit and a measurement for authority-adjacent redundancy.** We define a
  recurring legal formula as an exact fingerprint of a normalised window
  around an authority mention, measure how much apparent support it inflates,
  and show the inflation is invisible to document-level deduplication because
  the formulas recur *across* documents rather than within them (§4).
- **A negative result with a reusable control.** Removing recurring passages
  is not validated as a de-boilerplating operation by the fact that it changes
  a downstream result. We show a case where it changes the result, where no
  class-specific removal reproduces the change, and where a size-matched
  random removal does. We propose the size-matched random-removal control as a
  standard test for any deduplication claim (§5).
- **A drift-based, rather than coverage-based, comparison of index
  architectures**, and the finding that recall and ranking decay at very
  different rates, with the consequence that staleness is a clock and not an
  event signal (§6).
- **A permutation-calibrated regime monitor** that measures its own
  false-alarm rate, and the finding that the non-stationarity it detects is
  anchored in the publication system rather than in legal content (§7).
- **The legal setting as a live constraint rather than a backdrop**: the forum
  we measure already permits AI in its own procedure by four explicit
  provisions, quoted in §8, while AI is the subject of none of its published
  disputes.

Everything is computed from a public repository with a determinism check, a
figure-tracing guard, and frozen baselines; §10 gives the reproduction path.

## 2. Related work and positioning

Three lines of work meet here and, in our reading, do not currently talk to
one another.

*Corpus construction and deduplication for language models.* Removing exact
and near duplicates from training corpora is now standard practice, motivated
by memorisation and by the distortion of frequency statistics. The unit is
almost always the document or a long n-gram span, and the validation is
usually intrinsic — how many duplicates were removed — rather than a
demonstration that what was removed is the thing the practitioner intended to
remove.

*Legal information retrieval and maintenance.* Work on statutory and case
retrieval reports coverage, recall and ranking metrics at a point in time.
Maintenance — when an index must be rebuilt, and on what trigger — is treated
as an engineering matter rather than an empirical question with a measurable
answer.

*Temporal generalisation.* Chronological splits are the accepted remedy for
leakage in legal NLP evaluation. The remedy assumes that the two sides of the
cut are draws from the same process, which is an assumption about the
publisher as much as about the courts.

Our position is that these three are the same problem seen from three
distances. All three assume that the corpus is a sample of legal reasoning.
It is a sample of what a publisher released, containing wording that repeats
for reasons that have nothing to do with evidence, changing under a process
that is not stationary. This paper measures each of those three properties in
one corpus and reports what each does downstream.

> **Note on references.** This draft carries no citation list. The empirical
> content is complete and traceable; the bibliography must be assembled by the
> author against the current literature rather than generated, and is marked
> as outstanding in `REFERENCES_TODO.md`.

## 3. Data and setting

**The corpus.** Published first-instance and appellate commercial judgments of
the Saudi Ministry of Justice. The AI-subject scan covers **50666** judgments;
the measurement layers used here cover the hijri years 1442–1446, from which
we extract **25213** non-statutory authority mentions across **27027**
judgments carrying a reasoning section.

**Why this setting.** Saudi commercial judgments carry an unusually wide range
of authority in one document — statute, the parties' contract, named works of
fiqh, maxims of fiqh, Qur'an, hadith, settled judicial principle, commercial
custom, and the court's own named discretion — and the published documents
carry structural headings that separate the recital of the parties' claims
from the court's reasons. Both properties are instrumentally useful: the first
gives a rich authority space in which redundancy is visible; the second lets
every measurement be computed in the court's own voice rather than over a
blend of voices.

**Layers.** Four derived layers are used, all of which record counts and
identifiers and none of which stores judgment text: a statutory citation layer
(instrument and article, by speaker), an authority mention layer (nine
authority types, by speaker), a canonical identity layer for non-statutory
authority (28 canonical identities plus generic classes), and the formula
layer defined in §4.

**Time index.** Hijri quarters, 1442Q1–1446Q2, of which ten satisfy a maturity
rule fixed before any outcome was inspected: at least 800 judgments carrying
court authority, at least 200 court statutory citations, a later quarter must
exist, and volume at least 40 per cent of the median of the preceding four
quarters. All time-indexed results below are computed on mature quarters only.

**What the corpus is not.** It is published commercial adjudication. Absence
from it is absence from that record, never absence from Saudi law. Two of the
most active current legal frontiers in the jurisdiction — AI governance and
data protection — are regulated in forums this corpus does not contain, a
point we return to in §8.

## 4. Failure mode 1: support counts are not independent observations

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

## 5. Failure mode 2: removing recurring passages is not de-boilerplating

This is the result we consider most consequential for practice, and it is
negative.

### 5.1 The setup

The corpus supports a downstream question with a binary verdict: among
non-statutory authorities first observed beside a given code, do those first
observed in the court's voice persist better than those first observed in the
parties'? On the full data the matched comparison returns a court-first
advantage. Removing every mention sitting in one of the 218 circulating
formulas — **5981** mentions, about a quarter of the layer — flips the matched
verdict.

The natural reading is that boilerplate was carrying the effect. That reading
is what we test.

### 5.2 Class-specific ablation

We assign each circulating formula a class from a coarse mechanical taxonomy
built from keyword markers with a fixed priority, no model and no learned
labels. The classes are dominated not by procedural boilerplate but by the
framing of authority:

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

**Procedural boilerplate is 5 of 218.** If the flip were a de-boilerplating
effect, removing the procedural class should reproduce some of it.

We ran **11** ablations, removing one class at a time and re-running the
downstream verdict. **Not one reproduces the flip.**

### 5.3 The size-matched random-removal control

If no class reproduces the flip but the whole set does, the operative variable
may be quantity. We test it directly: remove a *random* subset of the
circulating formulas of a given size, 20 seeded draws per level, and re-run.

| removed | mean mentions removed | flip share |
|---|--:|--:|
| 25 per cent | 1527.2 | 0.1 |
| 50 per cent | 3017.1 | 0.3 |
| 75 per cent | 4514.0 | 0.7 |
| **90 per cent** | **5407.1** | **0.9** |

Random removal of the same size reproduces the flip in **0.9** of draws. The
matched comparison rests on 6 or 7 pairs in every arm, and a comparison that
thin moves when a quarter of the evidence leaves — whatever leaves.

### 5.4 The claim, and the control we propose

At this corpus size, **removing recurring passages is a volume operation, not
a wording operation**. It is not established to be de-boilerplating, and the
fact that it changes a downstream result is not evidence that it is.

We therefore propose a minimum standard, which costs one experiment:

> **A deduplication or de-boilerplating step should be reported with a
> size-matched random-removal control.** If removing a random subset of the
> same size produces the same downstream change, the step has been shown to
> remove a quantity of data and not a kind of text.

The control is cheap, it is model-free, and in our case it is the difference
between a finding and an artefact. We are not aware of it being standard.

A second, weaker corollary follows from §4.2: because zero circulating
formulas carry a second authority, removing recurring wording in this corpus
also removes the authorities inside it. Across seven codes with at least 50
mentions, removing every circulating formula costs **2** authority identities
in total — so the operation destroys evidence volume while barely touching
the identity inventory, which is the opposite of what a practitioner deleting
"boilerplate" usually intends.

## 6. Failure mode 3: an index decays on a clock, and recall and ranking decay differently

### 6.1 Recall ages slowly, ranking ages fast

We freeze a retrieval snapshot at each fold and score it against the court's
citations one, two and four mature quarters later, over 13, 12 and 10 rolling
folds.

| horizon | citation share to never-seen articles | top-50 displacement (%) | mean rank displacement, top 200 |
|---|--:|--:|--:|
| 1 quarter | **0.0437** | **34.9231** | 33.1885 |
| 2 quarters | 0.0612 | 39.1667 | 36.3225 |
| 4 quarters | 0.1191 | 46.4 | 40.513 |

At one quarter the index is still *covering* the law — only 4.37 per cent of
citation mass goes to articles it has never seen — while more than a third of
its top fifty is no longer in the court's top fifty. **Coverage and ranking
age at different rates, and a maintenance policy calibrated on coverage will
refresh far too late.** Against thresholds fixed in advance (30 per cent
displacement, 35 rank places, 10 per cent content gap), the displacement
trigger crosses at one quarter, the rank-gap trigger at two, and the content
trigger at four.

### 6.2 Staleness is a clock, not an event signal

The natural inference is that a legal event should trigger a rebuild. We test
it with a negative control: apply the same staleness criterion at pseudo-event
dates on instruments that were already mature when the window opened, at every
mature quarter more than one quarter from a real commencement.

The staleness criterion fires in **15 of 15** pseudo-events, with no legal
event at all. In the same 15 pseudo-events, no staged multi-layer pattern
appears (share **0.0**), so the control is not simply firing on everything.

Staleness is therefore a property of elapsed time. Event-triggered refresh
cannot be justified against periodic refresh on this evidence, and we record
the proposal as held rather than adopted. **A legal transition is a reason to
refresh sooner; it is not the reason to refresh at all.**

### 6.3 Which index architecture drifts least

Coverage alone rewards whichever index is largest, so we compare five
architectures on **drift** — how much coverage each loses across folds as the
law moves under it — over 5 pseudo-future folds.

| architecture | mean coverage | drift |
|---|--:|--:|
| statute + doctrinal companions | **0.953** | **-0.0108** |
| statute + current article ecology | 0.9417 | -0.0169 |
| time-aware recent window | 0.9287 | -0.0225 |
| statute only | 0.9273 | -0.0308 |
| speaker-aware hybrid | 0.9284 | **-0.0343** |

Adding the non-statutory companion layer to a statutory index both raises
coverage and roughly thirds the drift of a statute-only index. The
speaker-aware hybrid — an index enlarged with articles that only the parties
cite — drifts most.

That last row deserves its own number, because enlarging an index with
party-side material is an intuitive move. Over 13 folds, the party-only
remainder grows the index by **40.6** per cent, adds **0.0064** of coverage,
and **0.0956** of what it adds is ever cited by a court. The trade is
**0.157** coverage points per 10 per cent of universe growth.
`HIGH_RECALL_COSTS_MORE_THAN_IT_BUYS`.

## 7. Failure mode 4: the corpus is not one stationary process, and the part that moves is the publisher

### 7.1 The test

Twenty-two series in five independent metric families — publication, docket
composition, statutory salience, authority ecology, and the formula layer —
scanned with four transparent change-point methods (CUSUM, Page-Hinkley,
piecewise level, piecewise trend). No threshold is hand-picked: every
statistic is scored against a permutation null built from the series' own
values, 2000 permutations, fixed seed, α = 0.05. The whole battery is then
pointed at **200** shuffled redraws of itself to measure what it reports when
there is nothing to report.

### 7.2 The corpus is not stationary

| | observed | null (200 shuffled redraws) |
|---|--:|--:|
| metrics with a significant break | **12** of 22 | 0.11 per metric; mean **2.42** metrics per draw |
| multi-layer candidate quarters | **6** | mean **0.365**; **maximum 3** in any draw |

Six multi-layer candidate quarters lies outside the entire null distribution.
`OBSERVED_EXCEEDS_EVERY_NULL_DRAW`. A chronological split on this corpus is
not a split of one process.

### 7.3 And the part that moves is the one a text pipeline cannot see

The six candidates form a contiguous block of six quarters rather than a clean
break, and the docket family appears in five of them. Asked whether any
candidate survives removing the two families that describe *what the publisher
released* rather than *what courts did*:

**None of six.**

| family | metrics tested | firing | share |
|---|--:|--:|--:|
| docket composition | 6 | 5 | **0.8333** |
| formula layer | 4 | 3 | 0.75 |
| publication | 4 | 2 | 0.5 |
| statutory salience | 4 | 2 | 0.5 |
| **authority ecology** | 4 | **0** | **0.0** |

Not one candidate break is supported by two content families alone, and the
authority ecology — hybrid rate, named-source share, source concentration,
traceability — carries no significant break at all.

Two consequences follow for anyone building on such a corpus. First, a
temporal evaluation split inherits a publication-composition shift, and the
shift is not visible in the text: it lives in which cases were released and
what claims they carried. Second, the standard hope that a target unstable
across the whole window might be stable within regimes does not survive
testing here. With rolling origins where the break is re-detected on the
history alone at each origin, segmentation improves forecasting on **0 of 22**
series against a last-value baseline.

## 8. Why this is a problem for AI and law specifically

The three preceding sections would be corpus-engineering results in any
domain. Two facts about this domain make them immediately operative, and both
are quoted from enacted instruments rather than asserted.

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
untested.** A system built under those permissions — a drafting aid, a
research assistant, a retrieval layer inside the court's own workflow — will
be built on a corpus in which authority support is inflated by up to 2.429,
in which the standard deduplication remedy removes volume rather than
boilerplate, in which a third of the top-fifty ranking turns over per quarter,
and in which the observable process is non-stationary in its publication
layer. Each of the four failure modes is a property the builder inherits.

We make no claim about whether any deployed system is affected. Seven verified
AI adoption events in this jurisdiction were classified on a linkability
ladder and **none** reaches the adjudicatory workflow this corpus observes, so
no deployment can be associated with any observable change here. That is a
statement about linkability and not about effect, and it is precisely why the
corpus-level properties are the part that can be measured today.

## 9. Limitations

**One jurisdiction, one forum.** Published Ministry of Justice commercial
adjudication. Nothing here is claimed to hold elsewhere, and the two most
active AI-adjacent legal frontiers in the same jurisdiction are regulated in
forums this corpus does not contain.

**Exact-fingerprint resolution.** The redundancy unit is exact; the
near-duplicate layer built to soften it is unstable at this corpus size
(0.5462 pair survival across thresholds). Every redundancy count is a floor.

**The downstream verdict in §5 is thin.** The matched comparison rests on 6 or
7 pairs in every arm. That thinness is itself part of the finding — it is why
a quarter of the data leaving moves the verdict — but it means the negative
result is a demonstration that the control is necessary, not a measurement of
how often deduplication misleads.

**No publication date.** The corpus carries a decision date and a retrieval
timestamp, and neither institution publishes a per-judgment publication date.
Decision-to-publication lag therefore cannot be separated from legal change,
which is exactly the confound §7 identifies and cannot remove.

**Observation lag.** The latest mature quarter is roughly two years behind the
time of writing. Every "current" statement is current-as-published.

**Nothing is causal.** Co-occurrence of wording is not copying. A layer
crossing a criterion after a date is an ordering of observations, never one
thing acting on another.

**The taxonomy is mechanical.** Formula classes come from keyword presence in
a 180-character neighbourhood, with a merge rule for classes the markers
cannot separate. No class is a reading of a passage.

## 10. Reproducibility

All results are computed by scripts in a public repository, from derived
layers that record counts and identifiers and store no judgment text. Three
guarantees are enforced in code rather than asserted:

- **Determinism.** Every analysis is verified byte-identical across runs; all
  output orderings break ties on a stable key.
- **Figure tracing.** Every figure quoted in this manuscript is declared in a
  guard script with the results file and key it comes from, and matched as an
  exact string. The guard fails if any figure drifts.
- **Freshness.** A stamp file hashes the code each result depends on
  transitively, so a result that predates the code that produced it is
  refused.

Baselines used in this paper are frozen with the repository head at which they
were computed, and the freeze scripts refuse to overwrite. The negative
controls in §5 and §6 are seeded and reproducible from the seed recorded in
the results files.

## 11. Conclusion

We set out to test four assumptions that sit between a published judgment
corpus and a legal AI system built on it. All four fail on this corpus, and
they fail differently.

Support counts are not independent observations, by a factor of 1.296 on
average and 2.429 at worst, and the redundancy is of a kind that
document-level deduplication cannot reach. The standard remedy is not
validated: removing recurring passages changed a downstream verdict here, but
eleven class-specific removals did not reproduce the change and a size-matched
random removal did in 0.9 of draws, which makes it a volume operation. An
index decays on a clock rather than on legal events, with ranking ageing about
eight times faster than recall at one quarter, and the architecture that
drifts least is the one that adds the non-statutory companion layer. And the
corpus is not one stationary process, but the non-stationarity is anchored in
the publication system, where a text-only pipeline cannot see it.

The most portable output is the smallest: **report a deduplication step with a
size-matched random-removal control.** We would not have known that our own
de-boilerplating step was measuring quantity rather than wording without it,
and we can see no reason to expect other corpora to be kinder.

