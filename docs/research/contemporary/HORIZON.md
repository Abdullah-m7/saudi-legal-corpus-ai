# Predict what is predictable; catch the rest at the first mature observation

The forecasting programme returned a negative that is easy to misread.
Persistence beat every model on every scalar target. Read as a verdict on
forecasting, that ends the work. Read correctly, it says a prospective
instrument needs **two** functions, and the repository had built one.

> **FORECAST** where a predictor beats an uninformed reference with a
> characterised error.
> **DETECT** where the level cannot be predicted but a departure from it can
> be caught, under rules frozen before the departure.
> **WATCH** where there is not enough temporal depth to do either.

Those produce different sentences, and only the first is a forecast. *"We
predicted this"* and *"we did not predict this, but the detector we froze
beforehand caught it at the first mature observation"* are both scientific
results. A repository that can only say the first is much less useful than one
that can say either honestly.

---

## 1. The forecastability boundary

`horizon_results.json` classifies every target: **8 FORECAST, 6 DETECT, 1
WATCH**. No failed target is rescued with a larger model.

| status | targets |
|---|---|
| FORECAST | top-50 and top-10 membership; new top-50 entrants; retrieval universe coverage; the top-3 companion set for four codes |
| DETECT | named-fiqh share, non-statutory share, court article HHI, court-party overlap, the two instrument-share series |
| WATCH | Evidence Law named-fiqh trend — 3 folds, refused rather than estimated |

The DETECT row is where the negative result becomes an instrument. Those six
series have a measurable level and an unbeatable persistence baseline. They
cannot be forecast; they can be monitored.

## 2. When may a quarter be scored at all?

Decided before the future, in `phase3_maturityRule`, from the data's own
shape rather than the calendar:

- at least 800 judgments carrying court authority
- at least 200 court statutory citations
- at least one later quarter exists, so the quarter is not the collection edge
- volume at least 40 per cent of the median of the four preceding quarters

**10 of 18 quarters are SCORABLE.** The rule disqualifies 1442's four opening
quarters, 1443Q2, 1445Q2, 1445Q3 and 1446Q2 — and the last of those is the
edge case the rule exists for: a quarter that looks complete on the calendar
and is not.

The forbidden move is written into the file: *the outcome itself may never be
used to decide maturity.* A quarter is not declared immature because a
forecast missed in it. The rule applies prospectively; the published backtests
were computed before it existed and are not retrofitted.

## 3. The one target with a real signal

Entry into the operational core, backtested over 10 folds against a base rate
of **0.066**:

| feature | precision at n | lift |
|---|---:|---:|
| court citation share | 0.2857 | **4.33** |
| judgments citing it | 0.2857 | **4.33** |
| momentum | 0.1363 | 2.07 |
| combined additive rule | 0.1402 | 2.12 |
| party citation share | 0.1206 | 1.83 |
| rank acceleration | 0.0947 | 1.43 |
| rank alone | 0.01 | 0.15 |

Two things worth saying plainly. **The combined rule is worse than its own
best ingredient** — summing standardised ranks across three features halves
the precision. And the worst fold is **0.0**: the signal is real on average
and fails completely sometimes.

The frozen candidate list is in `FORECAST_LEDGER.json` as
`top50_entrants@1446Q2`, with each candidate labelled NEAR_BOUNDARY or
LONG_JUMP. Scoring is reported separately for the two, because predicting an
article ranked 52 into the top 50 is not the achievement that predicting one
ranked 300 would be. Historically each period brings about **4.8** near-boundary
entrants and **5.6** long jumps — the harder half is the bigger half.

## 4. New law, and how fast it arrives

`phase6_newLawMonitor` gives every instrument that arrives inside the window a
milestone profile: first party citation, first court citation, top-100 entry,
top-50 entry. **60 instruments arrive in window, 8 reach the top 50, median
2 quarters** from first court citation.

Instruments first seen in the corpus's opening year are flagged
`POSSIBLY_CENSORED`: their arrival may be ours rather than the law's. The
Civil Transactions Law is the clean case and remains the reference profile —
2 quarters to the core, both voices seeing it in the same quarter.

## 5. Does the bar lead the bench anywhere?

The corpus-level answer was no. Before closing it, the subsets:

| subset | folds | mean partial r | folds positive | verdict |
|---|---:|---:|---:|---|
| all articles | 11 | -0.0107 | 4 | no lead-lag |
| core, top 50 | 11 | -0.0051 | 5 | no lead-lag |
| Evidence Law | 8 | -0.0233 | 3 | no lead-lag |
| Commercial Courts Law | 11 | 0.0197 | 7 | no lead-lag |
| **rare articles, bottom half** | 11 | **0.0638** | **7** | **party adds** |

One subset survives: **in the long tail, the bar's citations do add
information about what the court will cite next quarter**, above the court's
own persistence. It is a small effect on a noisy subset, and it is reported as
a subset result. The corpus-level negative is not overturned by it, and it is
not generalised — but it is exactly where a discovery mechanism would show
first, which is why it is recorded rather than buried.

## 6. Does legal salience already concentrate?

This is the baseline any future claim that AI concentrated authority must
clear. Over 12 folds:

| | |
|---|---:|
| rank autocorrelation, quarter to quarter | 0.6541 |
| top-decile persistence | 0.7023 |
| bottom-half to top-decile mobility | **0.0017** |
| new top-50 entrant survival, one quarter | 0.5554 |
| mean article HHI | 0.0682 |

**RICH_GET_RICHER_ALREADY_PRESENT.** Stated only as the measurement
supports it: published Saudi commercial adjudication shows **high top-decile
persistence and extremely low bottom-half-to-top-decile mobility**, and barely
half of new entrants survive a quarter. It showed that before any AI is
observable in this corpus. An earlier draft said the system "concentrates
almost as hard as it could"; that is a claim about a ceiling nothing here
measures, and it is withdrawn. The numbers are unchanged.

That cuts against the easy story rather than for it. A system whose top decile
already persists at 0.7023 and whose bottom half reaches it at 0.0017 leaves
little room for a concentration increase to be noticed, so a later rise is weak
evidence of anything, and an AI-homogenisation claim has to clear a baseline
this high before it means anything at all.

## 7. Change detection, and what it costs

The contract in `detectors.py`, fixed before replay: rolling median baseline,
scaled MAD dispersion, threshold 3, confirmation at two consecutive scorable
periods in the same direction, and only SCORABLE quarters update anything.
States: NORMAL, WATCH, SIGNAL, CONFIRMED_SHIFT, DATA_UNSTABLE, NOT_SCORABLE.

Replayed pseudo-prospectively — each period sees only what came before it:

| | |
|---|---:|
| detectors run | 16 |
| evaluable periods | 56 |
| signals | 8 |
| confirmed shifts | 2 |
| alarm rate | **0.1429** |
| confirmed rate | 0.0357 |

With no labelled true shifts in most series, that rate is the candidate
**false-alarm rate**. A family that fired on most ordinary quarters would be
useless; this one fires on one in seven and confirms one in twenty-eight.

**The positive control, and a disclosure.** The one structural change in this
corpus definable without hindsight is the Civil Transactions Law becoming
citable — its date is fixed by legislation, not chosen by us after seeing the
series. The first version of the detector **missed it**, because a series flat
at zero has zero dispersion and the detector called the first nonzero quarter
DATA_UNSTABLE.

That is a flaw the control existed to expose, and it was repaired: a
dispersion floor, so a series flat at zero can still depart, and the standard
MAD consistency constant, because a raw MAD makes a "3 MAD" rule fire like a
2σ one. Both changes were made **after** the control failed, both are stated
in the contract, and the whole alarm budget was recomputed with them — the
alarm rate went *down*, from 0.2157 to 0.1429. Nothing was tuned to make a
particular quarter fire.

With the repair: **DETECTED at 1445Q1, detection delay 0 quarters.** One
positive control is one positive control — it shows the detector can catch a
real structural change, not that it is sensitive in general.

## 8. What fired historically

Not discoveries — the quarters were already past when the rules were written.
They are calibration:

| detector | signals | confirmed |
|---|---|---|
| Civil Transactions Law share | 1445Q1, 1445Q4, 1446Q1 | 1446Q1 |
| Commercial Courts Law named share | 1445Q4, 1446Q1 | 1446Q1 |
| CCIR top-source share | 1446Q1 | — |
| Commercial Courts Law entropy | 1445Q4 | — |
| Evidence Law entropy | 1445Q4 | — |

The second row is the interesting one and the discipline case. Named-source
share in the Commercial Courts Law is at robust z **-4.1** and confirmed —
the direction the AI_GENERALISED_DRAFTING hypothesis predicts. The composite
detector nonetheless reports **WATCH, 1 of 2**, because a hypothesis needs
coherent movement across a family and one metric is one metric. No narrative
fires on a single statistic.

## 9. Doctrinal novelty

A `DOCTRINAL_NOVELTY_EVENT` is a source identity that never appeared beside a
code and then does — with a bar high enough to mean something: three periods
of presence after at least three observed periods of absence. Loosely defined,
it returned 16 events; properly defined it returns **one**.

> **منتهى الإرادات beside the Commercial Courts Implementing Regulation**,
> first seen 1444Q3 after three quarters of absence, present in three.

That is what the object was built to find, and finding one in nine quarters is
the right order of magnitude. Novelty here means novel *beside that code* —
never novel to Saudi law, because the identity universe has 28 members.

## 10. Retrieval as a Pareto surface

The previous report's whole-judgment recommendation was withdrawn on
contamination grounds. The replacement is not another single number:

| architecture | court-authority recall | universe size | party contamination |
|---|---:|---:|---:|
| STATUTE_ONLY_TOP50 | 0.8039 | 50.0 | 0.0 |
| STATUTE_ONLY_TOP200 | 0.914 | 173.6 | 0.0 |
| COURT_REASONING | 0.9563 | 588.8 | 0.0 |
| **SPEAKER_AWARE_HYBRID** | 0.9614 | 734.5 | 0.1939 |
| WHOLE_JUDGMENT | 0.9626 | 865.3 | 0.2824 |

The hybrid is the architecture the earlier report should have tested: keep the
whole court universe, add the most-cited party-only candidates at a stated 25
per cent larger index, and retain speaker provenance so the ordering is
possible at all. It captures **four fifths of the whole-judgment recall gain
for two thirds of the extra index and two thirds of the contamination**.

**All five are on the Pareto front.** That is the honest result: nothing
dominates, and the choice between them is a legal judgement about what a wrong
citation costs, not a statistic. No composite score is computed, and the
components are reported separately on purpose.

## 11. When does a snapshot need rebuilding?

| trigger | threshold | first horizon crossed |
|---|---|---:|
| TOP50_DISPLACEMENT | 30 % of the frozen top 50 displaced | **1 quarter** |
| RANK_GAP | mean rank displacement 35 in the top 200 | 2 quarters |
| CONTENT_GAP | 10 % of citations to never-seen articles | 4 quarters |

A snapshot crosses its first refresh trigger after **one quarter**, and the
trigger that fires is displacement, not missing content. A maintenance policy
written around "how much are we missing" would refresh three quarters too
late.

## 12. The first release

`FORECAST_LEDGER.json`, section `horizonRelease`, `HORIZON_1`: **1 new
forecast, 5 detectors, 5 watch targets, 2 competing AI hypotheses.** Small on
purpose.

The two hypotheses are stored as hypotheses, not forecasts.
`H_AI_HOMOGENISATION` and `H_AI_DISCOVERY` predict opposite signs on the same
statistics, both are ARMED against the frozen detector bounds, and **no credit
is available for holding both**. If enough adoption evidence ever supports a
directional forecast, it will be issued separately and scored.

`watch_registry.json` carries seven external trigger definitions — machine
readable, with no scheduler anywhere in the repository. `SURPRISE_LEDGER.json`
exists with **zero prospective entries**, which is correct: every detector was
frozen today, so nothing can yet have fired prospectively. Its rule is the
one that matters — *an entry may be created only by a detector frozen before
the period it fired on*, and the explanation field is filled after the signal,
never before.

---

## Standing limitations

- 18 quarters, 10 of them scorable. Every detector statistic rests on that.
- The alarm rate is a *candidate* false-alarm rate: most series have no
  labelled true shift, so a real detection is indistinguishable from a false
  one until an explanation is found afterwards.
- One positive control does not establish sensitivity. The detector could
  still be missing shifts of a kind the Civil Transactions Law arrival does
  not resemble.
- Detector series must not be stitched across a parser change. A change to
  `authority.py` opens a new measurement era, and a parser improvement raises
  named-source share exactly like better citation practice would.
- The long-tail lead-lag result is a subset finding on a noisy subset and is
  not generalised.
- Nothing here is causal, and a SIGNAL is never labelled with a cause at the
  moment it fires.
