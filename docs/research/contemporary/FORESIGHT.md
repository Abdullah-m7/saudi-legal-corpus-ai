# What this repository is willing to be wrong about

Everything in this project so far describes. `DECOMPOSITION.md` says what the
corpus contains, `ECOLOGIES.md` and `DOCKET.md` say why codes differ,
`DOCTRINE.md` says what the court reaches for. None of it can be wrong in the
only way that matters to a forecaster: about something that has not happened
yet.

This file adds that. It contains rolling-origin backtests of every temporal
target the corpus can support, an AI-transition baseline frozen at a stated
cutoff, and five forecasts with their scoring rules fixed before the outcome
is observable. It also contains a great deal of abstention, because most of
what one would like to forecast here cannot be forecast yet, and saying so is
the first requirement.

**The headline is uncomfortable and worth stating first: nothing beat
persistence.** Across every scalar target, over up to fourteen rolling folds,
no model improved on `last period` or `the mean so far`. That is a result, not
a failure of effort: published Saudi commercial adjudication, measured this
way, is a persistent system with a churning surface, and the honest forecast
for most of its variables is the last value you saw.

---

## A. AI-transition baseline status

Frozen at `frozen/ai_transition_baseline.json`, cutoff **1446Q2**, 129 numeric
fields, with the repository head, the pipeline version, the SHA-256 prefixes
of every input, and four composition warnings recorded inside it.
`freeze_baseline.py --check` compares the live reading against it and refuses
to overwrite.

It is **not** called a pre-AI baseline. Legal AI already exists and is already
in use somewhere in Saudi legal practice; this repository does not know where,
and nothing in the corpus tells it. The baseline records the state of the
measurable variables at a stated moment so that a future session can ask
whether any of them moved.

Seven families, all rates, shares, ranks or entropies, never counts:

| | family | anchor figures at 1446Q2 |
|---|---|---|
| A | statutory use | 382 distinct articles cited by the court in the trailing year; article HHI 0.06891; top-50 carries 87.05 % of court citations; 12.4 new entrants into the top 50 per quarter |
| B | court vs bar | court/party top-20 Jaccard 0.1765; article-level median Jaccard 0.0 |
| C | doctrinal diversity | 28 canonical identities; effective sources 7.28 to 11.22 by code; named fiqh 58.71 % of court fiqh mentions |
| D | traceability | 66.8 % resolved statute, 18.2 % named source, 11.2 % unnamed, 3.8 % unresolved statute |
| E | hybrid reasoning | statute-only 53.5 %, hybrid 28.7 %, non-statute-only 5.8 %, none 12.0 %; per-code hybrid rate from 3.5 % to 59.4 % |
| F | template concentration | 8,447 fingerprints; 59.7 % in a repeated family; 194 circulating formulas carrying 30.8 % of court mentions |
| G | uptake velocity | 56.3 % of articles first appear in the court's voice, 20.22 % in the bar's, 23.48 % in the same quarter |

Family F carries an explicit scope note in the JSON: it measures the wording
**around a non-statutory citation**, not whole-judgment templating, and the
templates it finds are human and institutional as measured. Nothing in this
repository attributes any of them to any tool.

## B. Temporally valid forecast targets

Periods are hijri quarters, **1442Q1 to 1446Q2**, 18 of them, built by joining
the mention layer to `judgment_dates.json`. 154,699 mentions. There is no
random split anywhere in `foresight.py`; every evaluation fits on periods
strictly before *p* and predicts *p*.

Quarters after 1446Q2 are excluded: 1446Q3 carries 184 judgments and 1446Q4
carries 7, against a median quarter near 1,500. That is publication lag.
Forecasting into it would be forecasting the publisher.

| target | folds | verdict |
|---|---:|---|
| top-50 court article set | 10 | evaluable, persistence not beaten |
| top-10 court article set | 13 | evaluable, persistence not beaten |
| new entrants into the top 50 | 10 | evaluable, **signal above base rate** |
| Civil Transactions Law share of court citations | 10 | evaluable |
| named fiqh share of court fiqh | 14 | evaluable |
| non-statutory share of court mentions | 14 | evaluable |
| court/party top-20 Jaccard | 8 | evaluable |
| court article HHI | 10 | evaluable |
| Commercial Courts Law share of instruments | 10 | evaluable |
| doctrinal companion top-3 sets, 4 codes | 4 to 9 | evaluable for the set, not the order |
| retrieval universe coverage, h = 1, 2, 4 | 13, 12, 10 | evaluable |

## C. Rejected forecast targets, and why

- **Evidence Law named-fiqh trend** — INSUFFICIENT_TEMPORAL_DEPTH. The
  identity layer exists only for 1444 onward and the per-quarter support falls
  below 40 mentions after 1445Q3, leaving 3 folds. The user's programme asked
  for this target by name; it is refused rather than estimated.
- **Doctrinal companions for seven of eleven codes** — LOW_SUPPORT, the same
  floor as `DOCTRINE.md`: 1 to 57 locally attached units.
- **Statutory amendment forecasting** — HOLD. The registry carries no
  amendment events with reliable dates and article-version mapping, so the
  target is not identifiable. No work was spent on it.
- **Docket composition forecasting** — HOLD. The validated docket morphology
  exists, but its target would be *the composition of the published corpus*,
  and the publication series is exactly the thing that is unstable across
  these 18 quarters. Forecasting it would mostly be forecasting the
  publisher's release policy, and would be labelled that way if issued.
- **Anything about individual judges, judgments or outcomes** — out of scope
  by construction, in this file and in the repository.
- **Whether any document was AI-assisted** — refused. There is no scientific
  basis for inferring it from style, length or fluency, and no such label will
  be produced here. AI exposure enters this repository only through
  `adoption_registry.json`, from citable institutional events.

## D. Pseudo-future backtest windows

Rolling origin with a four-quarter burn-in. The first forecast fold is 1443Q1
for the cheapest targets and 1444Q1 for those needing a 200-citation floor in
the test period. Fold counts per target are in the table above and in
`foresight_results.json`, per fold, with the period labels.

Judgments carrying authority, by quarter, range from **347** (1443Q2) to
**5,523** (1444Q2) — a factor of 15.9. Every target is therefore a rate, a
share or a rank. No count is forecast.

## E. Baseline performance

| target | best baseline | its MAE |
|---|---|---:|
| named fiqh share of court fiqh | MEAN | 0.04087 |
| non-statutory share of court mentions | MA3 | 0.04167 |
| court/party top-20 Jaccard | MA3 | 0.03701 |
| court article HHI | LAST | 0.00678 |
| Commercial Courts Law share of instruments | LAST | 0.02129 |
| Civil Transactions Law share of court citations | LAST | 0.01005 |

For the set-valued targets the baseline is the previous period's set: mean
top-50 Jaccard **0.6059** (worst fold 0.4286), mean top-10 Jaccard 0.6117
(worst fold 0.25).

## F. Forecast skill by target

Two models were tried against those baselines: DRIFT (last plus last change)
and SHRINK (half last, half a three-period mean).

**No target reaches FORECASTABLE.** The best mean skill against the best
baseline is +0.0275 for SHRINK on the non-statutory share, on 8 of 14 folds,
with a worst fold of -1.564. DRIFT is worse than the baseline everywhere and
catastrophically so in places: -1.849 mean skill on the named-fiqh share, with
one fold at -99.1786. Momentum is the wrong instinct in this corpus.

The one target where a signal genuinely beats its reference is **new
entrants**: over 2,322 candidate articles and 10 quarters, against a base rate
of **4.48 %** for entering the top 50, ranking candidates by the court's own
prior-quarter citation share gives precision **23.19 %** — a **lift of 5.18**.
Momentum gives 3.04 and the bar's citations give **2.3**. The lazy signal
wins again, and it is the bench's own behaviour.

## G. Bar-to-bench lead-lag

The programme's speaker-aware layer exists precisely to ask this, and the
answer is negative and clean.

| | |
|---|---:|
| mean correlation, court use at *t* with court use at *t+1* | **0.9625** |
| mean correlation, party use at *t* with court use at *t+1* | 0.3471 |
| mean **partial** correlation, party at *t* with court at *t+1*, holding court at *t* | **-0.0107** |
| folds with a positive partial | 4 of 11 |

Once you know what the court cited last quarter, the bar's citations that
quarter tell you nothing further about what the court will cite next. Verdict:
**NO_LEAD_LAG_ASSOCIATION_ABOVE_PERSISTENCE**.

The first-appearance data says the same thing from the other side. Of 460
articles whose first observed use in both voices falls inside the window,
**56.3 %** appear in the court's voice first, **20.22 %** in the bar's, and
23.48 % in the same quarter; the median court-minus-party gap is **-1**
quarter. In this corpus the bench is seen with a provision before the bar is.

Two caveats that cut in opposite directions. Advocacy is measured only where
the publisher reproduces it, and a summarised submission understates the bar.
And this is a LEAD-LAG ASSOCIATION either way: a provision both sides discover
in the same month produces exactly this pattern.

## H. Operational-core forecast result

Persistence carries the operational core: last quarter's top 50 recovers
60.59 % of next quarter's on Jaccard, with 12.4 articles turning over each
quarter. MA3 is worse (0.5663), and the same holds at k = 10 (0.6117 against
0.5453). At the level of shares rather than sets, LAST also wins: mean
absolute error per article 0.00141 against MA3's 0.001871 and all-history's
0.002079.

## I. New-law uptake forecast result

The corpus contains exactly one new code arriving live, and it is worth the
whole section.

| quarter | court share | party share | distinct CTL articles cited by the court |
|---|---:|---:|---:|
| 1444Q4 | 0.0 | 0.0 | 0 |
| 1445Q1 | 0.00155 | 0.01282 | 7 |
| 1445Q2 | 0.00384 | 0.00877 | 7 |
| 1445Q3 | 0.06414 | 0.16716 | 49 |
| 1445Q4 | 0.06067 | 0.16452 | 46 |
| 1446Q1 | 0.08550 | 0.21756 | 43 |
| 1446Q2 | 0.07743 | 0.14118 | 23 |

The Civil Transactions Law is invisible in the corpus until 1445Q1, then
enters the court's top 100 by 1445Q2 and the top 50 by 1445Q3: **two quarters
from first court citation to the operational core**, and one quarter for the
step from seven articles to forty-nine.

Both voices see it in the same quarter — so the bar does not lead in *timing*.
But it cites it two to three times more heavily than the bench does, in every
quarter after arrival. That is a difference in intensity, not in discovery,
and it is the sharpest thing the corpus has to say about how a new code
enters.

This curve matters beyond itself: it is what uptake looked like **without any
verified AI involvement**. Any future claim that legal AI accelerates the
discovery of new provisions has to beat two quarters to the core.

## J. Code-ecology forecastability

Per-code ecology rates are frozen in the baseline (family E) and their
corpus-level aggregates backtest as PERSISTENCE_NOT_BEATEN. The non-statutory
share of court mentions drifts downward across the window — 0.336 in 1444Q1 to
0.204 in 1446Q1 — and even that visible drift is not exploited by DRIFT, which
loses to MA3 by a wide margin. The ecology is persistent rather than
forecastably dynamic, which PART XVII of the programme anticipated as a result
in its own right, and it is the result.

## K. Doctrinal-companion forecastability

The backtest separates two things the descriptive map could not.

| code | steps | mean top-3 Jaccard | same set | same order | top-1 held |
|---|---:|---:|---:|---:|---:|
| Sharia Procedure Law | 4 | 1.0 | 100.0 % | 0.0 % | 25.0 % |
| Commercial Courts Law | 11 | 0.8636 | 72.7 % | 36.4 % | 63.6 % |
| CCIR | 10 | 0.8 | 60.0 % | 10.0 % | 50.0 % |
| Evidence Law | 8 | 0.625 | 25.0 % | 0.0 % | 50.0 % |

These counts include the FORECAST_CALIBRATION_BACKFILL to 1442–1443, which
added two steps to the Commercial Courts Law and one to the implementing
regulation. It steadied the estimates and moved no verdict.

**The set of companions is forecastable; their ranking is not.** The Sharia
Procedure Law keeps the same three sources in all four transitions and never
once keeps them in the same order. This is exactly the distinction that
`DOCTRINE.md` needed and could not make from a pooled three-year profile, and
it turns the companion map from a description into a predictive asset with a
known error rate.

## L. Temporal retrieval-decay result

Freeze a retrieval universe at *t*; measure how much of the court's statutory
citations at *t + h* it still contains. No language model is involved; this is
coverage, which is the ceiling on anything built on that universe.

| architecture | h = 1 | h = 2 | h = 4 | worst fold at h = 4 |
|---|---:|---:|---:|---:|
| WHOLE_JUDGMENT | **0.9626** | **0.9491** | **0.8886** | 0.7166 |
| COURT_REASONING | 0.9563 | 0.9388 | 0.8809 | 0.7095 |
| RECENT_COURT_2Q | 0.9424 | 0.9206 | 0.8667 | 0.6821 |
| STATUTE_ONLY_TOP200 | 0.9140 | 0.8892 | 0.8329 | 0.6108 |
| STATUTE_ONLY_TOP50 | 0.8039 | 0.7706 | 0.7194 | 0.5444 |

Three things follow. Ageing costs every architecture about seven points of
coverage per year, and the ranking never changes. The operational core is the
**worst** basis for a retrieval universe: building on the top 50 starts
fifteen points behind and stays behind. And WHOLE_JUDGMENT beats
COURT_REASONING at every horizon by half a point to a point — the one place in
this entire file where the bar's citations add measurable value. They do not
predict what the bench will cite; they *cover* a little of it that the bench's
own history misses.

The doctrinal identity universe barely ages at all (mean step coverage
**0.9902**) — because it has 28 members. The top-3 companions cover roughly 55
per cent of the next quarter's mentions, which is the number a system would
actually have to live with.

## M. AI-adoption registry readiness

**SUPERSEDED — see `AI_TRANSITION.md`.** This section originally reported the
registry as schema-complete and empty, and called that a true statement about
what had been verified. It was not honest enough: it recorded that this
repository had not looked. A bounded search of official Saudi sources found
seven events, three of them BEFORE this baseline's cutoff, including a
judicial legal-research system deployed in a Saudi court. The registry now
carries them, with corpus-linkability levels; none reaches L3, so none
supports an event study here. The paragraph below is kept for the schema
description only.

`adoption_registry.json` exists and is schema-complete.

It carries the field list the programme specified, the rule that no event is
entered without a citable source from the issuing body, the rule that no
document in this corpus is ever labelled AI-written, and three adoption
thresholds — `T_RESEARCH_DEPLOYED`, `T_DRAFTING_DEPLOYED`,
`T_COURT_DECISION_SUPPORT` — defined **before any event exists**, so that a
future session cannot pick a threshold that flatters a conditional forecast.

## N. Measurable AI-transition hypotheses

Eight hypotheses, each with its baseline already frozen and its falsifier
stated. None is asserted.

| | hypothesis | baseline metric now | what would falsify it |
|---|---|---|---|
| 1 | accelerated new-law uptake | two quarters from first court citation to top-50 (CTL) | a later code taking as long or longer under verified adoption |
| 2 | argument homogenisation | article HHI 0.06891; companion top-3 coverage by code | concentration flat or falling |
| 3 | long-tail expansion | top-50 carries 87.05 % of court citations | that share not falling |
| 4 | traceability improvement | 18.2 % named source, 11.2 % unnamed; named fiqh 58.71 % of fiqh | named share flat or falling |
| 5 | bar–bench convergence | top-20 Jaccard 0.1765 | overlap flat or widening |
| 6 | canon concentration | companion top-3 set persistence 0.625 to 1.0 | entrant survival rising, top-1 turnover rising |
| 7 | authority feedback loop | party-to-court partial correlation -0.0107 | it stays at or below zero |
| 8 | template monoculture | 30.8 % of court mentions in circulating wording | that share flat or falling |

Hypotheses 2 and 3 are deliberately opposed. So are 5's two directions. The
repository is not built to confirm a story about AI; it is built so that
whichever way these move, the movement is measurable against a number written
down first.

**Hypothesis 7 is already weakened, before any AI arrives.** Its precondition
is that advocacy visibility leads adjudicatory visibility. Section G finds no
such lead: the partial correlation is -0.0107 and positive in 4 of 11 folds,
and the bench is seen with a new provision *before* the bar in 56.3 % of
cases. The AI-legal-salience feedback loop is recorded in `THEORY_LOG.md` as a
hypothesis whose first link is currently missing in this corpus.

## O. Conditional AI forecasts

Two, in `FORECAST_LEDGER.json`, both gated on `T_RESEARCH_DEPLOYED` and both
scored only if that threshold is met and observable:

1. **Named fiqh under research AI** — if source-resolving legal research is
   verifiably deployed, named fiqh rises at least 5 percentage points above
   the frozen 58.71 %, sustained over four quarters. The falsifier is stated
   in the entry: if it is deployed and this does not move, the "better
   retrieval makes citation more traceable" mechanism is wrong here.
2. **Article concentration under research AI** — **no direction is
   predicted.** Homogenisation and long-tail expansion point opposite ways and
   both are live. The forecast is only that the absolute change in HHI exceeds
   0.01: that *something* moves. The sign is recorded and no credit is taken
   for it.

One scenario, `ctl_uptake_repeat`, is stored separately, carries no scoring
rule, and never enters a skill statistic.

## P. Frozen future forecasts

Five, at cutoff 1446Q2, targeting NEXT_ELIGIBLE_QUARTER — the first hijri
quarter after 1446Q2 carrying at least 800 judgments with court authority in a
future rebuild. If none reaches 800 by 1449Q4 they become VOID_DATA_SHIFT
rather than being scored.

| forecast | prediction | uncertainty | model |
|---|---|---|---|
| `operational_core_top50@1446Q2` | the 50 frozen articles remain the top 50, Jaccard 0.6059, 12.4 entrants | worst backtested fold 0.4286 | PERSISTENCE (a baseline) |
| `ctl_court_share@1446Q2` | 0.07743 of court citations name the Civil Transactions Law | [0.05733, 0.09753] | LAST (a baseline) |
| `court_party_top20_jaccard@1446Q2` | 0.15656, direction STABILITY | [0.08254, 0.23058] | MA3 (a baseline) |
| `companion_top3_sets@1446Q2` | the four frozen top-3 sets hold; **the order is not predicted** | worst backtested Jaccard 0.5 to 1.0 | PERSISTENCE of the set |
| `retrieval_coverage_h1@1446Q2` | 0.9563 coverage, and WHOLE_JUDGMENT above COURT_REASONING above TOP200 above TOP50 | worst fold 0.8262 | frozen-universe coverage |

Every model here is a baseline, and every entry says so in its own `model`
field. That is the honest position given section F: the backtests found no
model worth preferring, so the forecasts are made with the predictor that won,
and the uncertainty attached to each is that predictor's own backtested error
over the rolling folds — not a distributional interval nobody checked.

## Q. Forecast ledger status

`FORECAST_LEDGER.json`: 5 forecasts, 2 conditional forecasts, 1 scenario, all
OPEN, ledger hash `ebdf19344d6f81e5`, plus the 50 frozen article keys the
first forecast is scored against. `forecast_ledger.py` appends only: it will
not modify an entry that already exists, and `--check` reports when the
current code would predict something different, treating the ledger entry as
the record and the divergence as expected once the corpus grows.

Statuses are OPEN, SCORED, VOID_DATA_SHIFT, VOID_TARGET_REDEFINED. Nothing is
ever deleted.

## R. Strongest forward-looking scientific finding

**PARTLY WITHDRAWN — see `AI_TRANSITION.md` section 3.** The measurement below
stands unchanged. The gloss placed on it did not: this section went on to say
that "the mechanism by which legal AI is usually expected to reshape law runs
through advocacy", which is too narrow. AI enters legal work through seven
channels, and the first verified Saudi judicial deployment is in a court's own
research environment, not a law firm's. What the measurement supports is the
narrower claim that PATH 1 of the salience-feedback hypothesis has no
observable precondition here.

**Advocacy does not lead adjudication in this corpus, and the bench's own
history is the best predictor of everything.** Court persistence correlates at
0.9625 with next quarter; the bar adds -0.0107 on top of it; the bench is seen
with a new provision first 56.3 % of the time against the bar's 20.22 %; and
in the one target where any signal beats its base rate — entry into the
operational core, lift 5.18 — the winning signal is again the court's own
prior citation, with the bar's at less than half that lift.

This matters beyond forecasting, for one pathway of five. PATH 1 of the
salience-feedback hypothesis runs through advocacy: tools change what lawyers
find, lawyers change what they cite, courts are exposed to it, doctrine moves.
The first link of that chain is measurable here and it is currently absent.
PATH 2 — a court's own AI research environment changing what the bench cites
directly — is the path the adoption registry shows actually exists, and this
corpus is in the wrong institution to observe it.

## S. The prediction most worth staking the repository on

**REFRAMED — see `AI_TRANSITION.md` section 5.** The forecast stands and is
scored as written; the recommendation drawn from it is withdrawn. Coverage is
RECALL, and recall bought from the whole judgment is bought with advocacy
contamination: the party-only remainder grows the index by 40.6 per cent, adds
0.0064 of coverage, and 9.56 per cent of it is ever cited by a court. The
successor target, `speaker_aware_retrieval@1446Q2`, prices that trade
directly. The paragraph below records what was claimed.

Of the five, `retrieval_coverage_h1@1446Q2` — specifically its **ordering
claim**: a retrieval universe built from what the *whole judgment* cites will
cover the next period's court citations better than one built from the court's
own reasoning, and both will beat one built from the operational core, by
roughly fifteen points.

It is the one worth staking because it is the one that is *useful if true and
costly if false*. It says that the ordinary way to build a Saudi legal
retrieval system — index the important articles — is the worst of the five
options measured, and that the parties' citations, which every speaker-aware
finding in this repository treats as noise to be separated from the bench's
voice, are worth keeping for coverage even though they are worthless for rank.
It held in 13 of 13 folds at h = 1 and in every fold at h = 2 and h = 4, and it
is falsified by a single quarter in which the ordering breaks.

## T. Highest-value next action

**DONE, in part — see `AI_TRANSITION.md` section 7.** The backfill to
1442–1443 was run under the label FORECAST_CALIBRATION_BACKFILL and added two
folds to the Commercial Courts Law and one to the implementing regulation
without moving the verdict. The original recommendation follows.

**Extend the identity layer backwards to 1442 and forwards as the corpus
grows.** Two of the three refusals in section C — the Evidence Law named-fiqh
trend, and companion forecasting for seven codes — are refusals for want of
temporal depth in one layer, not for want of method. The statutory layer has
18 quarters; the doctrinal identity layer has 9 or 10 with support, and it is
the layer carrying every hypothesis about traceability, canon concentration
and the salience loop. `companions.py` already runs over any window; extending
it is one pass and no new science, and it would convert four abstentions into
targets.

The second-highest-value action costs nothing and should happen first: **enter
the first verified adoption event** in `adoption_registry.json`, or record in
writing that a search was made and none was verifiable. An empty registry with
no note is indistinguishable from a registry nobody tried to fill.

---

## Standing limitations

- Published commercial judgments, 1442–1446. Not the Saudi judiciary, and the
  publisher's release policy is itself a time-varying quantity that no metric
  here separates out.
- 18 quarters is short. A worst-fold skill statistic on 8 folds is a weak
  instrument, and every verdict above should be re-run when the corpus grows.
- The doctrinal identity universe is `authority.py`'s vocabulary. A change to
  the extractor would move family C of the baseline without anything moving in
  the law, and the baseline says so in its own composition warnings.
- Persistence winning everywhere is partly a property of the measurement:
  quarterly rates of a large aggregate are smooth by construction. A finer
  target — one code, one article, one court — would be noisier and might
  reward a model. It would also have less support.
- No causal claim is made anywhere in this file. The event-study contract in
  `FORECAST_LEDGER.json` requires confounders to be recorded alongside any
  future before-and-after comparison, and a before-and-after comparison is
  still not a cause.
