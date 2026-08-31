# What is actually recurring when a legal formula reappears

The last programme ended on a result that was reported, frozen, and not
explained. Remove every mention whose ±90-character wording fingerprint recurs
in ten or more judgments — 218 of them — and the matched doctrinal first-mover
verdict flips from a court-first advantage to `BAR_FIRST_NOT_WORSE`.

The tempting reading is *templates caused the effect*. Nothing established
that. A recurring form of words can be an empty procedural shell; it can
equally be the observable carrier of a stable legal proposition, in which case
the control deleted the signal it existed to protect. So the recurring wording
is not called a **template** here. It is a **recurring legal formula** until
measurement says what it is.

**It turns out the control does not identify wording at all.** That is this
file's headline, and it is a correction to this repository's own claim.

> **SCOPE CORRECTIONS, entered after the transition-sequencing programme.**
> Three narrowings, and not one of them changes a number.
>
> 1. The unit is an **AUTHORITY-ADJACENT RECURRING FORMULA**: an exact
>    normalised ±90-character window around an authority mention. It is *not* a
>    representation of a judgment's language, and nothing here is a finding
>    about judicial writing in general. The full term is used wherever
>    precision matters.
> 2. "The wording layer will move first if AI changes Saudi legal reasoning"
>    is withdrawn. Historical mobility is not a prediction about response to a
>    future event. Section 10 states what was measured; the prospective form
>    is a hypothesis and is registered as one.
> 3. "Source and formula are inseparable" overstates the measurement. The
>    measured statement is: **at the current exact-fingerprint resolution, no
>    circulating formula is observed with more than one canonical authority
>    identity.** Near-family equivalence remains unresolved — the family layer
>    that would catch a shell varying by one word was built and found
>    unstable.

---

## 0. What one fingerprint scientifically is

Read off the code that built it, before changing anything.

| property | what the existing unit does |
|---|---|
| context | ±90 characters around the matched authority string |
| normalisation | diacritics stripped, whitespace collapsed, أ إ آ → ا, ى → ي, ة → ه |
| digits | **deleted**, so numeric article references were already invisible |
| punctuation | **deleted**, so a fingerprint may straddle two sentences |
| short words | every 1–2 character word removed — most particles are gone |
| source names | **kept**: the unit is source-preserving by construction |
| court and city names | not removed by any rule |
| matching | **exact.** A hash has no neighbourhood |

Median window: 29 tokens, p10 26, p90 33. Only **0.0309** of authority windows
contain a statutory citation at all — a fact that matters twice below.

One fingerprint is therefore a claim that two passages, stripped of numbers,
punctuation and short words, are the same ~29-word neighbourhood of an
authority. It is a statement about wording, not about meaning, and never about
copying.

## 1. Exact, or near-exact?

A banded minhash over token 3-shingles — 8 bands of 4, seeded, no embedding
model — groups the 218 circulating formulas into families. At Jaccard 0.7
there are 130 co-grouped pairs; only **0.5462** of them survive at 0.8.

`FAMILY_GROUPING_UNSTABLE_USE_EXACT_ONLY`. The family layer was built, tested
and set aside. Every count below is exact-match and is therefore a floor.

## 2. Does the SOURCE recur, or a shell that receives sources?

This was the methodological centre of the programme, and the answer is
unusually clean. Masking the matched authority string before hashing takes the
corpus from **14958** distinct fingerprints to **14941** — a difference of
seventeen.

**Zero of the 218 circulating formulas carry more than one canonical source.**

`RECURRENCE_IS_LARGELY_SOURCE_BOUND`, read at exactly its measured meaning:
**at the current exact-fingerprint resolution, no circulating formula is
observed with more than one canonical authority identity.** Near-family
equivalence is unresolved — a shell differing by one surviving word is a
different fingerprint here, and the family layer that would have caught it is
unstable (section 1). At this resolution the corpus shows answer C and answer D
of the original list — source quotation and judicial paraphrase *of a
particular source* — with answer E, the citation shell, **unobserved rather
than disproved**.

## 3. Article formula, code formula, or neither?

Masking the article ordinal collapses **nothing** (0.0); masking the instrument
title collapses nothing; masking everything collapses **0.0011** of
fingerprints. That is not a null result about legal language — it follows from
the 3 per cent citation rate above. The recurring formulas are almost never in
the neighbourhood of a statutory citation.

Classified by where they actually appear:

| locus | n |
|---|---:|
| GENERAL_JUDICIAL_FORMULA (≥2 codes) | 69 |
| NO_LOCAL_CODE | 57 |
| CODE_FORMULA | 50 |
| ARTICLE_FORMULA | 42 |

## 4. A coarse taxonomy, and it separates

Mechanical keyword markers, a fixed priority written before any outcome was
read, and a merge rule for classes the markers cannot separate. **No merges
were required.** Ambiguous assignments: **0.0029** of mentions. No marker at
all: **0.2444**.

The 218 circulating formulas, by modal class:

| class | formulas |
|---|---:|
| AUTHORITY_INTRODUCTION_FRAME | 46 |
| GENERIC_REASONING | 46 |
| AUTHORITY_QUOTATION | 43 |
| COMPENSATION_HARM | 36 |
| BURDEN_PRESUMPTION | 21 |
| DOCTRINAL_RULE | 9 |
| DISPOSITION | 5 |
| PROCEDURAL_OPERATION | 5 |
| CONTRACT | 4 |
| JURISDICTION | 2 |
| FACT_RECITAL | 1 |

Modal-class purity is **0.8303** fully pure, median 1.0. And note what the
table says: **procedural boilerplate is 5 of 218.** Answer A — "procedural
boilerplate" — is the smallest category but one.

## 5. Quotation or the court's own words?

Of the 5,981 mentions inside a circulating formula: 2598 sit in an introductory
frame, 2344 in unmarked judicial wording, 747 open a quotation, 292 sit near
one. **0.1835** of circulating formulas are mixed — the same wording sometimes
introduces a quotation and sometimes does not.

Quotation is detected from quotation characters, not by comparing text to a
source. An unmarked quotation reads as judicial wording here, and there is no
way to find it without the sources, which this repository does not hold.

## 6. How source and formula are coupled

| archetype | n |
|---|---:|
| MANY_FORMULAS_ONE_SOURCE | 215 |
| ONE_TO_ONE | 3 |
| ONE_FORMULA_MANY_SOURCES | 0 |

Ibn Taymiyya carries **53** distinct circulating formulas. The courts do not
have one way of invoking a source; they have many settled ways of invoking each
one, and each way stays attached to that source.

## 7. The falsification — one class at a time

Instead of deleting all 218 formulas at once, delete each class separately and
re-run the doctrinal first-mover result.

| arm | mentions removed | matched verdict |
|---|---:|---|
| nothing removed | 0 | court-first advantage, low support |
| **all circulating** | **5981** | **BAR_FIRST_NOT_WORSE** |
| only AUTHORITY_INTRODUCTION_FRAME | 1503 | court-first advantage |
| only AUTHORITY_QUOTATION | 1067 | court-first advantage |
| only GENERIC_REASONING | 999 | court-first advantage |
| only COMPENSATION_HARM | 767 | court-first advantage |
| only BURDEN_PRESUMPTION | 492 | court-first advantage |
| only PROCEDURAL_OPERATION | 351 | court-first advantage |
| only DOCTRINAL_RULE | 114 | court-first advantage |
| … and four smaller classes | | court-first advantage |

**Not one of the eleven single-class ablations reproduces the flip.**

The interpretation rule was written before the numbers were read: if the flip
reproduces for every class, it is about volume, not wording. It reproduces for
none of them — so the volume hypothesis gets its own control.

## 8. The volume control, and the correction

Remove a *random* set of circulating formulas of the same size, twenty seeded
draws per level:

| removed | flip share |
|---|---:|
| 25 per cent | 0.1 |
| 50 per cent | 0.3 |
| 75 per cent | 0.7 |
| **90 per cent** | **0.9** |

Matched pairs across every arm of every experiment: **6 or 7**.

`FLIP_TRACKS_REMOVAL_VOLUME_NOT_WORDING_CLASS`.

The de-boilerplating control removes about a quarter of the evidence, and a
matched comparison resting on six pairs moves when a quarter of the evidence
leaves — whatever leaves. The flip is real and reproducible; what it is *not*
is a demonstration that circulating wording carried the court-first doctrinal
advantage.

**This corrects a claim in DIFFUSION.md.** The frozen numbers stand exactly as
frozen. What changes is what they were measuring: the second control was
weaker than it looked, and the first control — six matched pairs — was always
the binding one.

## 9. The formula layer as a layer of its own

**First-mover and crossing.** Of 195 eligible circulating formulas, 193 are
court-origin and 1 is bar-origin. Court-origin formulas reach the bar's voice
in **0.0518** of cases, at a median lag of **6** quarters. Circulating legal
formulas are a bench phenomenon that the bar essentially does not take up.

**Travel.** Median 1 city, 1 code, 2 articles; median **2** quarters to a
second city and 2 to a second code; **0.0505** reach both voices.

**Variation.** Over 19 sources present in both halves of the window, the median
Jaccard between the early and late sets of formulas attached to a source is
**0.8333**, and 7 sources have identical sets. The courts keep phrasing a
source the way they phrase it.

**Concentration.** Whole corpus entropy **12.8584** bits, top-10 share
**0.0652**. Inside the circulating set, top-10 share **0.2747**. The procedural
group is where concentration lives: top-10 share **0.9557** over 13 distinct
formulas.

**Diversity, court against bar.** At an equal sample of 6,543 mentions the
bench produces an expected **3967.15** distinct formulas and the bar
**5705.0**. The bar is the more varied voice; the bench is the formulaic one.

## 10. Three layers on one scale

| layer | universe | rank autocorrelation | top-group persistence | bottom-half mobility |
|---|---:|---:|---:|---:|
| doctrinal sources | 34 | 0.8954 | 0.937 | 0.0 |
| statutory articles | ~2,000 | 0.6541 | 0.7023 | 0.0017 |
| **circulating formulas** | **218** | **0.2194** | **0.3921** | **0.0379** |

Same comparability warning as before, and it is not decoration: three universes
of very different size, so only the *direction* is read. The direction is
unambiguous and it is the same across all three measures. **The wording layer
is by far the most mobile and doctrine is the most rigid.**

## 11. What this means for a code's doctrinal environment

Formula dependence — the share of a code's non-statutory mentions sitting
inside a circulating formula — runs from **0.0226** (law practice law) to
**0.4064** (the commercial courts implementing regulation). But across all
seven codes reported, removing every circulating formula costs **2** source
identities in total, all of them beside the implementing regulation.

De-boilerplating removes evidence volume. It removes almost no sources.

Re-reading the 114 doctrinal companion pairs with formulas visible:

| class | n |
|---|---:|
| CODE_ASSOCIATED | 44 |
| GENERIC_FIELD | 42 |
| SOURCE_QUOTATION_REUSE | 10 |
| FORMULA_ASSOCIATED_SOURCE_ENVIRONMENT | 7 |
| ARTICLE_ASSOCIATED | 6 |
| MIXED | 5 |

Seven of 114 are one recurring passage counted many times. The rest are not.

## 12. What a legal AI would absorb

Counting each circulating formula once per source instead of once per mention:
overall inflation **1.296**, worst source **2.429** (al-Bayhaqi). Under
de-duplication 21 sources change rank by at least one place, top-10 stability
**0.9**, and one source enters the top ten while B.INSAF leaves it.

The ageing curve is unaffected: raw and adjusted quarterly series correlate
**0.9976**. **Formula de-duplication changes the level of apparent support and
not its shape over time.** A frequency-trained system would over-weight the
sources with the most settled phrasing by up to a factor of two and a half; it
would not misread the trend.

## 13. Can formula persistence be forecast?

Base rate 0.022 over 12114 formulas. Features are read from the **first
scorable quarter only** — an earlier draft read them from the whole window and
produced a lift above 20, which is the outcome restated.

| feature | folds | mean lift | folds above 1 | median cohort support | verdict |
|---|---:|---:|---:|---:|---|
| court origin | 8 | **1.4634** | 8 | 1104 | weak but consistent |
| multi-city at first observation | 7 | **10.7077** | 6 | **14** | signal, low support |
| multi-code at first observation | 5 | 14.6823 | 4 | 3 | signal, low support |

A formula observed in more than one city in its first quarter persists at
**0.2521** against a base rate of **0.022**. That is the largest lift this
repository has ever measured on rolling folds — and it fires on a median of
fourteen formulas per fold, so it is recorded as a near miss and not as a bet.
Court origin is the trustworthy one and its lift is 1.46.

## 14. FORMULA_DETECTOR_ERA_1

Four metrics armed on Era 1's contract — rolling median baseline, MAD × 1.4826,
k = 3, confirmation at two consecutive scorable periods — with **no historical
replay to borrow**, so Era 1's alarm rate does not transfer.

| metric | baseline | state |
|---|---:|---|
| formula share of mentions | 0.23711 | NORMAL |
| court formula share | 0.32452 | NORMAL |
| top-10 formula concentration | 0.10123 | NORMAL |
| formula innovation rate | 0.88392 | WATCH |

**Prospective Detector Era 1 and Doctrinal Detector Era 2 are untouched.**
Their series, alarm budgets and pending scores stand exactly as frozen.

## 15. The AI hypotheses, frozen with their competitors

- **H_FORMULA_HOMOGENISATION** — drafting assistance concentrates wording:
  entropy falls, top-10 share rises, innovation falls. Against
  **H_FORMULA_VARIATION** (more phrasings, not fewer), **H_FORMULA_DISCOVERY**
  (the wording layer is untouched and the sources move), and **H_NO_CHANGE**,
  which wins by default.
- **H_SHELL_STANDARDISATION** — AI changes *how* authority is introduced before
  it changes *which*. Recorded with its own problem: at the current
  fingerprint resolution no circulating formula carries a second authority
  identity, so shell and source cannot be told apart here, and this hypothesis
  may not be distinguishable from the first. Better to write that down now than
  discover it later.
- **H_REINFORCEMENT** — retrieval concentrates the source layer further. Stated
  with the reason to doubt it: the doctrinal layer is already at 0.937
  persistence with zero upward mobility.
- **H_ADVOCACY_IMPORT** — a bar-side tool raises the court's use of bar-origin
  formulas. Baseline: **1** circulating formula was first observed in the bar's
  voice, and it never reached the bench. Not armed — the base rate is small
  enough that the dispersion floor would dominate, which is exactly the failure
  the positive control exposed in the first detector era.

No retrospective attribution. No adoption event reaches L3_WORKFLOW_MATCH, so
none of this is evidence about any deployment that has occurred.

## 16. Issued and refused

**REPOSITORY_BET_003 — REFUSED.** The candidate was that the *class* of
recurring wording decides the de-boilerplated verdict. Eleven single-class
ablations, none flips; random removal of the same size flips 0.9 of draws;
every arm rests on six or seven pairs. Thirty matched pairs would earn it, and
that needs more corpus, not more analysis.

**Three watches, no probabilities:** the first circulating formula observed
carrying a second source; near-exact grouping becoming stable across
thresholds; ONE_FORMULA_MANY_SOURCES appearing at all.

**Paper: ASSET_ONLY_FOR_NOW.** The strongest output is a negative
methodological result resting on six or seven pairs, and the claim it corrects
is this repository's own. Correcting yourself in your own repository is not a
paper.

---

## The question, answered

> When legal doctrine appears to spread through contemporary Saudi
> adjudication, is the thing actually spreading the authority itself, a legal
> proposition, a recurring judicial formulation, or some combination?

**All three, but they are not independent, and one of them barely moves.**

The authority and the formulation travel together at the resolution measured
— zero circulating formulas carry a second canonical authority identity, so no
"wording that spreads by itself" is observed here. Near-family equivalence is
unresolved, so this is an absence of observation, not a demonstrated
impossibility. The legal proposition is present but is the smallest
measured class: 9 of 218 formulas are doctrinal-rule wording and 5 are
procedural. What recurs most is how a court *introduces* an authority — 46
introduction frames and 43 quotation formulas of 218.

And the layers are ordered by rigidity: doctrine 0.8954, articles 0.6541,
wording 0.2194. Authority is the immovable part; the wording around it is the
part that turns over.

> If AI eventually changes Saudi legal reasoning, which layer moves first?

**This file cannot answer that, and the answer it first gave is withdrawn.**
What is measured here is historical mobility, not response to a future event.
The permitted statement is: *among the three measured layers,
authority-adjacent recurring formulas show the greatest historical mobility;
whether this layer responds first to future AI adoption is a prospective
hypothesis.* The innovation rate sits at 0.88392 and doctrine at 0.937
persistence with zero upward mobility — both are descriptions of the past.
Ordering around an actual transition is tested in `TRANSITIONS.md`.

Two cautions attached to that answer. First, this repository would see a
wording shift as a detector alarm, and it could not attribute it — no adoption
event reaches the workflow this corpus observes. Second, the bench is already
the formulaic voice and the bar the varied one (3967.15 against 5705.0
expected distinct formulas at equal sample); so a homogenisation hypothesis
about the bench is proposing to concentrate what is already concentrated, and a
variation hypothesis is proposing to loosen it.

## Standing limitations

- 28 canonical identities. Every source-level count is a floor.
- Exact matching only; near-exact grouping is not stable at this corpus size.
- Quotation is detected from quotation characters, not by comparison to source
  texts.
- **Six or seven matched pairs in every arm.** This is the binding constraint
  on the entire question and no amount of further analysis relaxes it.
- Only 3 per cent of authority windows contain a statutory citation, so the
  article and code masks act on a small sub-population.
- Nothing here is causal. A shared fingerprint is shared wording — never
  copying, never influence, never one court reading another.
