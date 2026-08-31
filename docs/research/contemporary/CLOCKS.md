# When did the law actually start, and what did that do to our results?

The transition programme ended on one binding constraint: 59 statutory
arrivals inside the window and only two with a legal clock independent of the
corpus. Everything else would have had to take T=0 from the first citation,
which is the outcome.

This builds the missing layer — and it needed **no new source**. The
repository already holds official enacted texts for 277 instruments, captured
from the Ministry of Justice legal portal and verified against official PDFs.
Those texts carry the decree, its date, and in the final article the
commencement rule in the legislature's own words:

> «يعمل بهذا النظام بعد (مائة وثمانين) يوماً من تاريخ نشره في الجريدة الرسمية»
> — نظام الإثبات، المادة التاسعة والعشرون بعد المائة

What was missing was not evidence. It was the arithmetic that turns a
commencement provision into a corpus quarter.

**And the arithmetic broke the previous era's headline.** Both parts of that
sentence matter.

---

## 1. What a clock is made of

Nine components, and they are not synonyms.

`ROYAL_DECREE_DATE` · `COUNCIL_DECISION_DATE` · `OFFICIAL_PUBLICATION_DATE` ·
`GAZETTE_ISSUE` · `COMMENCEMENT_RULE` · `DELAY_FROM_PUBLICATION` ·
`TRANSITIONAL_PERIOD` · `FIRST_POSSIBLE_APPLICATION_DATE` ·
`FIRST_OBSERVABLE_QUARTER`

A statute that commences 180 days after **publication** does not commence 180
days after its decree. The gap between the two is measurable: across 25 locally
held official texts that carry both dates, the gazette lag runs **1 to 87
days**, median **16**, p90 **42**. That range is used to bound a missing
publication date. It is never substituted for one.

Commencement rules found in the enacted texts: 41 say *N days after
publication*, 11 say *on publication*, 2 anchor N days to something unstated,
and 23 carry no commencement article this pass could find.

## 2. Clock quality across 77 instruments the corpus cites

| grade | n | meaning |
|---|--:|---|
| C0_NO_CLOCK | 23 | no commencement article, no publication date |
| C1_YEAR_ONLY | 8 | a rule but nothing to anchor it to |
| C2_APPROX_QUARTER | 42 | a bounded quarter from decree + rule + gazette-lag range |
| C3_EXACT_EFFECTIVE_DATE | 2 | exact date, publication from a source we could not fetch |
| C4_EXACT_EFFECTIVE_AND_PUBLICATION | 2 | both dates held locally |

**Access, stated honestly.** `laws.boe.gov.sa` closes our TLS tunnel
mid-exchange and Umm Al-Qura's older permalinks 404 on its redesigned site.
Both are **our** failures to reach a source, not evidence that the source is
unavailable, and neither is worked around. Two publication dates therefore
carry grade S3 — a search summary of an official portal page — while the
commencement **rule** and the decree date for the same laws are S1 and local.

## 3. The falsification that had to be run

Is corpus arrival anywhere near legal commencement? Across the 25 instruments
with both a clock and corpus use:

**Median gap between first court citation and legal effective date: 28
quarters.** Seven years.

That is the whole case for this layer. An event clock read off the first
citation would not have been slightly wrong; for most instruments it would
have been wrong by the better part of a decade, because their "arrival" is
when a Ministry of Justice commercial corpus starting in 1442 first happened
to cite a law from 1424.

The event-type distribution says the same thing: **34 of 77** are
`FIRST_CORPUS_APPEARANCE_OF_OLD_LAW`, 2 commence after the window, and only 7
are new instruments.

## 4. Citation before commencement, verified

Three instruments are cited before their effective date, and the classes were
written before the counts were read.

| instrument | effective | first court use | pre-effective citations | share | class |
|---|---|---|--:|--:|---|
| Law of Evidence | 1443Q4 | 1443Q1 | 16 | 0.0016 | PRE_EFFECTIVE_REFERENCE |
| Civil Transactions Law | 1445Q2 | 1445Q1 | 8 | 0.0165 | PRE_EFFECTIVE_REFERENCE |
| Telecommunications Law | 1444Q2 (bounded) | 1443Q3 | — | 0.4737 | UNKNOWN_LIKELY_IDENTITY_COLLISION |

The third is the control on the first two. Nearly half of the telecom law's
citations fall before its effective date — the extractor matches an instrument
by **title**, and a replacement keeps its predecessor's title, so the reading
is that the corpus is citing the old telecommunications law under the new
one's clock. Not anticipatory practice.

For the other two the share is under 2 per cent and the reading is different:
**a small number of judgments cite a new law before it takes effect.** And for
the Law of Evidence the voices split — the bench's first use is 3 quarters
before commencement, the bar's is 1 quarter *after* it. On this evidence, when
anticipation happens it is the bench that anticipates. One law, sixteen
citations; recorded, not claimed.

## 5. The two clocks, corrected

| | Era 1 T=0 | Era 2 T=0 | early by |
|---|---|---|--:|
| Law of Evidence | 1443Q1 | **1443Q4** | 3 quarters |
| Civil Transactions Law | 1445Q1 | **1445Q2** | 1 quarter |

Era 1 took T=0 from the signal registry's `observable_in_courts_from`, which
was itself read off the first citation. Era 2 computes it from enacted article
129 (and 721) plus the gazette publication date.

**Era 1 is frozen and is not rewritten.** It stands in
`frozen/three_layer_baseline.json` exactly as recorded.

## 6. The promotion gate, and what got through

Eight conditions, fixed before any clock was read: C3 or better, a legally
meaningful event type, commencement inside the window, at least three mature
post-quarters, at least 150 court citations, not the collection edge, a clock
not derived from the outcome, and a mature pre-quarter for baselines.

**One instrument passes: the Law of Evidence.**

And the way the Civil Transactions Law fails is the finding. It fails on
exactly one condition — three mature post-quarters — because its verified
clock is one quarter later than the clock Era 1 used, and that quarter was the
difference. **An outcome-derived clock did not merely shift a latency; it
manufactured a mature post-quarter the law does not have.** It is reported here
below the gate, for comparison only, and is not counted in Era 2.

The target was four events. Four was not reached and no weak event was
promoted to reach it: `TRANSITION_BET_001` named four as its earning
condition, and lowering the bar to clear it would be the opposite of earning.

## 7. Calibration Era 2, same battery, corrected clocks

Every threshold and every layer criterion is imported from `transition.py`
unchanged. Latency in quarters after T=0.

| layer | Law of Evidence @1443Q4 | Civil Transactions Law @1445Q2 |
|---|---|---|
| L2 bar statutory visibility | 1 | 2 |
| L3 court statutory visibility | **0** | 2 |
| L4 authority-adjacent formula | **0** | 2 |
| L5 authority ecology | **0** | 2 |
| L6 doctrinal companion | ALREADY CROSSED | 2 |
| L7 operational core | ALREADY CROSSED | 2 |
| L8 retrieval staleness | 1 | 2 |

Two corrections were applied uniformly to every Era 2 event, and neither is
event-specific tuning.

**One.** L6, L7 and L8 read their first crossing over the whole window while
L2–L5 read theirs over scorable quarters at or after T=0. With T=0 at the
corpus edge the difference was invisible; with a real commencement date it made
a companion at a non-scorable quarter look earlier than a court citation at a
scorable one. Era 2 puts every layer on the same rule.

**Two.** A layer that had already crossed before the law took effect is
reported as `ALREADY_CROSSED_BEFORE_T0`, not as a latency. The Law of Evidence
had a repeated doctrinal companion and a top-50 article **before it was
capable of governing**.

## 8. S→D→F does not survive

| instrument | Era 1 clock | Era 1 order | Era 2 clock | Era 2 order |
|---|---|---|---|---|
| Law of Evidence | 1443Q1 | S→D→F | 1443Q4 | **NO_DOCTRINE** |
| Civil Transactions Law | 1445Q1 | S→D→F | 1445Q2 | **SIMULTANEOUS** |

`S_D_F_DOES_NOT_SURVIVE_THE_CLOCK_CORRECTION`.

And the mechanism is not mysterious. Era 1 started both clocks before the law
could be applied. A layer's *first* crossing is then read off a citation series
climbing from zero, and layers that need more material to register — a repeated
companion, a recurring formula — necessarily register later than a first
citation does. **The apparent staging was that growth curve, not an ordering
between layers.** Move the clock to the actual commencement and it collapses:
the Civil Transactions Law shows every measurable layer crossing in the *same*
quarter, and the Law of Evidence has two layers already crossed before it took
effect.

The +2 companion latency reproduced across both Era 1 events does not
reproduce either: at verified clocks it is `ALREADY_CROSSED` for one law and +2
for the other, where +2 is also the value of every other layer.

**What survives is nothing about order.** What survives is that both laws are
visible in the court's voice in the first mature quarter at or after their
commencement — a statement about speed, not sequence.

## 9. Ecology at T=0, and the reference signature

`IMMEDIATE_ECOLOGY` for the Law of Evidence, `DELAYED_ECOLOGY` for the Civil
Transactions Law. So even that splits.

Testing every dimension across all four measurements — two laws at two clocks —
under the rule that a dimension is stable only if it registered *everywhere*
and varies by at most one quarter:

- **stable: none.**
- varying: court, bar, formula and ecology latency.
- not measurable in every cell: companion, core and retrieval latency.

Which means the AI observability matrix v3 has a comparator status of
`NOT_YET_CONSTRUCTIBLE`. The comparison logic is written and frozen; it has
nothing to compare against. Arming a comparator with an empty stable set and
using it anyway is precisely the failure that phase exists to prevent.

## 10. UPTAKE_CLOCK_V2

A new metric beside the old one, never overwriting it. The existing monitor
measures FIRST_OBSERVED → TOP50; this measures from the legal effective date.

| | effective→first court | →first party | →sustained court | →top100 | →top50 |
|---|--:|--:|--:|--:|--:|
| Law of Evidence | -3 | 1 | 0 | -3 | -3 |
| Civil Transactions Law | -1 | -1 | 3 | 2 | 2 |

Negative values are not errors. They are the pre-effective citations of
section 4, and they are exactly why a first-citation clock flatters an event
study: it starts the clock at the anomaly.

## 11. Incidence, with the silent laws kept in

Of 43 instruments with a usable clock and at least three mature quarters after
it: **0.8372** are ever cited by a court, **0.6744** by a party, **0.3256**
reach the top-100, **0.1860** the top-50, and **0.1395** exceed 150 court
citations.

Seven are `NO_OBSERVABLE_UPTAKE_WITHIN_HORIZON` — a real legal event with no
corpus response. They stay in the denominator, and they are a better negative
control than any pseudo-date, because the event is real and the silence is the
observation.

**And the disclosure that travels with every one of them:** failure to appear
in this corpus does not mean a law is unused nationally. It means no observable
uptake in this published commercial adjudication corpus.

## 12. Retrieval, finally on a legal clock

A frozen top-50 snapshot goes materially stale **1 quarter** after the Law of
Evidence takes effect and **2** after the Civil Transactions Law. The clock
correction is what made the first of these measurable at all — at Era 1's T=0
there was no mature quarter before the event to freeze a snapshot on.

`PERIODIC_RETAINED` for refresh policy. Era 1's negative control found
staleness firing in 15 of 15 pseudo-events with no legal event at all, so
staleness is a clock; one qualified event with an evaluable snapshot cannot
backtest an event-triggered policy against the periodic one; and
`TOP50_DISPLACEMENT` is frozen in REPOSITORY_BET_001.

## 13. Refused

**TRANSITION_BET_001 — REFUSED again**, and against a *strengthened* gate. One
qualified transition, not four. Leave-one-transition-out is `NOT_RUNNABLE`
below four events, so one of the strengthened conditions cannot even be
evaluated. The candidate — statutory visibility precedes stable
doctrinal-companion formation — remains true everywhere it can be checked, and
being true is not the same as being earned.

Not attempted, with reasons rather than silence: signature classes (PHASE 19),
event-type comparison (PHASE 20), major-amendment calibration (PHASE 27 —
the Companies Law is a `REPLACEMENT` with a commencement article and a decree
date, but its publication date is unknown locally, its bounded effective window
spans two quarters, and it shares its title with the law it replaced).

---

## The question, answered

> Once we know when a Saudi law actually became legally effective, how long
> before that change is visible in advocacy, court reasoning, supplementary
> doctrine, recurring formulations, the operational core, and the retrieval
> systems built on top?

On the one law that qualifies: **court reasoning, recurring formulation and
the non-statutory ecology are all visible in the effective quarter itself;
advocacy and retrieval staleness follow one quarter later; and the doctrinal
companion and the operational core were already there before the law could be
applied.** On the law that misses the gate by one quarter, every measurable
layer arrives together, two quarters after commencement, in the first mature
quarter the corpus offers.

> Is S→D→F a real transition pattern, or a coincidence observed twice?

**Neither. It was an artefact of the clock.** It was observed twice because
both clocks were early, and it disappears from both laws when the clock is read
out of the enacted text instead of off a citation. The instruction was to try
to kill it. It died.

## Standing limitations

- **One qualified calibration transition.** Every comparison here is either
  against the same two laws at a different clock, or against nothing.
- The two publication dates are grade S3 because the official portal that
  holds them closes our tunnel. The commencement rule and the decree date are
  S1 and local.
- Dates are computed on the tabular Islamic calendar, which can differ from the
  observed Umm al-Qura date by about a day. At quarter resolution that matters
  only at a quarter edge, which is flagged as `quarterBoundaryRisk`.
- At the verified clocks the maturity rule marks the commencement quarters
  themselves NOT_SCORABLE for the Civil Transactions Law, so its latencies are
  measured from the first mature quarter after commencement, which is not the
  first quarter of effect.
- 31 instruments remain `UNKNOWN` event type and 23 have no clock at all.
- Nothing here is causal, and nothing here is foresight: every clock was
  recorded after the commencement it describes.
