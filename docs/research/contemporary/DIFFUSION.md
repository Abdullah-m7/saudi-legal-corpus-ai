# How an authority enters, and what becomes of it

The statutory half of this question is answered and frozen. Party-side use of
statutory provisions does not generally lead their later appearance in court
reasoning, and provisions first observed in the court's voice persist better
than provisions first observed in the bar's. That result is about **articles**.

Doctrine was untested — and doctrine is where a research tool, human or
machine, would most plausibly change what gets found. So: jurists, books,
maxims, scripture, settled practice. When is each first observed, in whose
voice, beside which code, and what becomes of it.

**The answer reproduces the statutory one and then dissolves under the second
control.** Both halves matter.

---

## 0. What "first" means, and only that

The repository cannot know when a jurist was first cited in Saudi law. It
knows five things and says them: first observed in this corpus, beside a code,
beside an article, in the court's voice, in the party's voice. **The word
"discovery" is not used.** Ibn Taymiyya was not discovered in 1444Q2.

And code-local is the unit that matters. With 28 canonical identities almost
every source is globally visible in the opening quarter, so the global level is
left-censored by construction. Beside a particular code it is not.

## 1. Eligibility, fixed before any outcome

A unit enters the science only if it appears more than once, its first quarter
is mature and is not the collection edge, a mature follow-up quarter exists,
and its identity is canonical rather than a raw string.

| level | units | eligible |
|---|---:|---:|
| GLOBAL | 34 | 14 |
| **CODE** | **237** | **117** |
| ARTICLE | 2195 | 676 |

Excluded units stay in the inventory. They do not enter a survival comparison.

## 2. First-mover typology, code-local

| type | n |
|---|---:|
| COURT_FIRST | 51 |
| COURT_ONLY | 30 |
| BAR_FIRST | 14 |
| SAME_PERIOD | 12 |
| BAR_ONLY | 10 |

## 3. Survival by first mover — the headline

| first mover | n | survive 1Q | survive 2Q | survive 4Q | persistent |
|---|---:|---:|---:|---:|---:|
| **COURT_FIRST** | 51 | **0.7174** | **0.8** | **0.8627** | **0.5882** |
| SAME_PERIOD | 12 | 0.7273 | 0.75 | 0.8333 | 0.4167 |
| COURT_ONLY | 30 | 0.5714 | 0.7 | 0.8667 | 0.1333 |
| **BAR_FIRST** | 14 | **0.2727** | **0.4615** | **0.5** | **0.2857** |
| BAR_ONLY | 10 | 0.0 | 0.0 | 0.0 | 0.0 |

A doctrinal source first observed in the court's voice survives the next
quarter at **2.6 times** the rate of one first observed in the bar's, and
persists at **2.1 times** the rate. The statutory gap was 1.6 times. **The
doctrinal pattern is the same shape and larger.**

## 4. And then the two controls

**Matching.** Court-first against bar-first on code, source type and a coarse
support band — nothing matched on any outcome. It leaves **6 pairs**. On those
six the bar-first unit is never the better of the pair (sign test 0.0 at both
2Q and 4Q), so the direction holds; but the verdict is recorded as
`COURT_FIRST_ADVANTAGE_SURVIVES_BUT_LOW_SUPPORT`, because six pairs is six
pairs.

**De-boilerplating.** Remove every mention whose wording fingerprint
circulates in ten or more judgments — 218 fingerprints — and re-run
everything:

| | full | de-boilerplated |
|---|---:|---:|
| COURT_FIRST survive 1Q | 0.7174 | 0.6304 |
| BAR_FIRST survive 1Q | 0.2727 | 0.3636 |
| COURT_FIRST persistent | 0.5882 | 0.5098 |
| BAR_FIRST persistent | 0.2857 | 0.4286 |
| matched verdict | court-first advantage | **BAR_FIRST_NOT_WORSE** |

**The matched verdict flips.** The gap narrows from both ends and the matched
comparison no longer favours the bench. A meaningful part of the court-first
doctrinal advantage travels with circulating judicial wording rather than with
the authority itself.

That is the second control doing its job, and it is why no bet was placed on
this result.

## 5. Which direction does authority cross?

Cross-voice local adoption, counted with the never-crossed units in the
denominator — otherwise the share is 1.0 by construction:

| direction | n | crossed | share | within 1Q | within 4Q | median lag |
|---|---:|---:|---:|---:|---:|---:|
| bar → bench | 24 | 14 | 0.5833 | 0.1667 | 0.375 | 2 quarters |
| bench → bar | 81 | 51 | 0.6296 | 0.1852 | 0.5185 | 3 quarters |

**`BIDIRECTIONAL_OR_INDEPENDENT`.** Crossing rates are within five points of
each other and neither direction is fast. 30 court-only sources never reach the
bar; 10 bar-only sources never reach the bench.

This is a different finding from the statutory one and worth keeping separate.
For articles the bench clearly leads. For doctrine, beside a given code,
neither voice systematically precedes the other — they mostly do not cross at
all, and when they do it takes two to three quarters either way.

## 6. Does the article arrive before its doctrine?

| state | n |
|---|---:|
| **NO_COMPANION** | **697** |
| ARTICLE_FIRST | 48 |
| SAME_PERIOD | 18 |
| SOURCE_FIRST | 1 |

Two facts. **Most articles never acquire a locally attached non-statutory
authority at all** — 697 of 764. And when one forms, the article is there
first, 48 times to 1.

**Companion formation latency** is measurable after all — the previous session
called it unmeasurable for want of depth, and the 1442–1443 backfill changed
that. Over 48 articles: median **3 quarters**, p25 2, p75 4, longest 8.

## 7. Which kinds of authority travel fastest?

| kind | n | median quarters to a 2nd code | to a 2nd city | to both voices | mean codes ever |
|---|---:|---:|---:|---:|---:|
| SCRIPTURE | 2 | 1 | 2 | 1 | 16.5 |
| UNATTRIBUTED_FIQH | 1 | 2 | 1 | 4 | 16.0 |
| HADITH_SOURCE | 10 | 4 | 1 | 2 | 3.3 |
| BOOK | 8 | 5 | 2 | 4 | 5.5 |
| JURIST | 4 | 5 | 2 | 3 | 8.75 |
| **MAXIM** | 6 | **6** | **4** | 2 | 6.5 |

Against the intuition that maxims are the portable form of doctrine, **named
maxim texts are the slowest to reach a second code and a second city** of any
named type. Jurists reach more codes than books (8.75 against 5.5) and both
lag scripture, which is everywhere almost immediately. Small n throughout —
these are 6 maxims and 4 jurists, not a population.

## 8. Is some of this the spread of wording rather than authority?

218 circulating fingerprints, each in ten or more judgments. Median **1 code**,
median **2 cities**, median **6 quarters** present, and only **0.055** (5.5 per cent) appear
in both voices.

So circulating wording is overwhelmingly single-code, geographically narrow and
single-voice: it is judicial formula, not shared legal vocabulary. That is
consistent with section 4 — the court-first advantage partly rides on court
formulas that the bar never uses.

## 9. Doctrine is more rigid than statute, not less

| | articles | doctrinal sources |
|---|---:|---:|
| rank autocorrelation | 0.6541 | **0.8954** |
| top-group persistence | 0.7023 (decile) | **0.937** (quartile) |
| bottom-half mobility | 0.0017 | **0.0** |
| universe | ~2,000 | 34 |

**Comparability warning, and it is not decoration.** The universes differ by
two orders of magnitude, so persistence is a decile for articles and a
quartile for sources. The numbers are **not** directly comparable; only the
direction is read, and the direction is consistent across all three measures.

The reading matters for everything downstream: if doctrine is the *more* rigid
layer, then a hypothesis that AI will diversify legal authority has to move
the most immobile thing in the system, and a hypothesis that AI will
concentrate it is proposing to concentrate something already at
0.937 persistence with zero upward mobility.

## 10. Global novelty versus code-local novelty

112 code-local novelty units against **5** global. Nearly everything called
"new" here is a known source arriving beside a new code. A long-tail discovery
hypothesis is about the other five, and five is what a 28-identity extractor
can produce. The two are counted apart because they are different claims.

## 11. Can doctrinal persistence be forecast?

No. Base rate 0.3772; the best emergence feature (court origin) reaches 0.4419,
lift **1.17**. Verdict `NO_USABLE_SIGNAL_USE_DETECT_OR_WATCH`, and the honest
addendum: with 114 eligible units across the whole window there are not enough
per-quarter cohorts to build rolling folds at all. This was a single-sample
ranking check, not a backtest.

## 12. What was issued, and what was refused

**DOCTRINAL_DETECTOR_ERA_2 — armed, and separate.** Era 1's novelty detector
knows that a source appeared beside a code and not which voice it appeared in;
section 3 shows voice is the informative part. Era 2 arms one new metric — the
share of newly eligible code-local units whose first observation is in the
court's voice, baseline **0.4359** — using Era 1's contract shape. **Era 1 is
untouched:** its detectors stay armed, its alarm budget stands, its false
alarms and misses will still be scored. Era 2 carries an honest caveat: it has
no historical replay, so Era 1's alarm rate does not transfer to it.

**Three watch targets**, no probabilities: the first bar-first source crossing
to the bench within one quarter; the first persistent new CCIR companion; the
first globally novel source.

**REPOSITORY_BET_002 — REFUSED.** The candidate was the largest unmatched
contrast in the programme, and it fails the two tests the ledger requires:
matching leaves six pairs, and de-boilerplating flips the matched verdict.
Persistence is also unforecastable at lift 1.17 with no temporal folds
available. The repository is better off refusing this bet than placing it —
and this is exactly the kind of result that would have looked strong in a
paper and dissolved in replication.

---

## The pathway, measured rather than told

> **Do new legal authorities enter through advocacy, through the bench,
> independently, or by different routes depending on what kind of authority
> they are?**

By different routes, and the kind matters:

- **Statutory articles** enter through the **bench**. Court-first provisions
  persist at 1.6 times the bar-first rate; the bar's citations add nothing
  above the court's own persistence; a matched cohort test kills the one
  positive subset.
- **Doctrinal sources**, taken at face value, look the same but stronger —
  2.6 times at one quarter. **Under de-boilerplating the advantage does not
  hold up**, and a meaningful part of it is the spread of judicial wording.
- **Crossing between voices is bidirectional and slow**, two to three quarters
  in both directions, and most sources never cross beside a given code at all.
- **Doctrine is the more rigid layer**, not the more fluid one.
- **Most articles never acquire a doctrinal companion**; when they do, the
  article comes first, 48 to 1, with a median latency of three quarters.

The honest summary: in this corpus the bench is where authority becomes
visible first, for statutes clearly and for doctrine partly; but a large share
of what looks like doctrinal leadership is a formula circulating among courts,
and neither voice systematically hands doctrine to the other.

## What this implies for the two AI pathways

Stated as implications of measured dynamics, not as predictions.

**A bar-side research AI** would be amplifying a pathway this corpus finds
weak for statutes and non-directional for doctrine. Bar-origin sources cross
to the bench in 58 per cent of cases at a median of two quarters, so the
channel exists — but nothing in it currently leads.

**A bench-side research AI** would be amplifying the stronger pathway, and it
would be doing so on the most rigid layer in the system: doctrinal rank
autocorrelation 0.8954, top-quartile persistence 0.937, zero upward mobility.
If AI changes what the bench reaches for, it has to displace that.

And one mechanism deserves its own name, because section 4 and section 8 point
at it together: whatever propagates court-first doctrinal advantage is
substantially **circulating wording**, single-code and single-voice. An AI
drafting or research tool that spreads formulations would act on that channel
before it acted on doctrine.

## Standing limitations

- 28 canonical identities. Every "new" and every diffusion figure is bounded
  by the extractor's vocabulary, and 5 global-novelty units is what such a
  vocabulary can produce.
- Matching leaves six pairs. The unmatched contrast is large and the matched
  one is thin; both are reported.
- Small n by kind: 6 maxims, 4 jurists, 2 scripture identities.
- Article-level units are sparse and the article/source ordering rests on 48
  companion formations.
- Nothing here is causal. Crossing is an observed ordering between
  timestamped appearances, never influence.
