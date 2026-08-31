# One process, or several?

Everything in this repository has been computed as though a single
data-generating process produced the whole window. A latency measured once was
treated as a latency in general. That assumption is withdrawn.

Saudi legal practice is institutionally non-stationary. Leadership,
restructuring, jurisdiction, procedural reform, publication policy, digital
platforms, legislative packages and AI deployment can each change the process
that generates the observations — not merely the observations.

**PAST LATENCY IS NOT FUTURE LAW.** Every frozen result keeps its numbers and
loses its universality. They are **regime-conditional baselines**.

The question is no longer *what is the normal sequence by which Saudi law
changes*. It is *under which institutional regime was an observed pattern
generated, and what happens when the regime changes*.

---

## 1. What was withdrawn, precisely

- The S→D→F ordering was already shown to be an artefact of an early clock. It
  is now additionally denied the status of a general law:
  `OBSERVED_IN_TWO_CALIBRATION_EVENTS`, and nothing more.
- `TRANSITION_BET_001` stays REFUSED, and **no further legal-clock event will
  be promoted merely to reach four examples.** Four agreeing transitions would
  not establish a general law either.
- Nothing is rewritten. The forecasts, the transition signatures, the clock
  layer and every detector era stand exactly as frozen, re-read as
  within-regime baselines.

## 2. A regime, defined without politics

A period during which the major observable institutional conditions relevant
to the legal data-generating process remain materially unchanged. Twelve
candidate regime variables are registered — leadership where legally relevant,
judicial structural reform, ministry restructuring, jurisdiction transfer,
procedural reform, publication policy, digital platform, verified AI
deployment, national reform programme, legislative package, institutional
merger, workflow redesign.

**Record first, test later.** Not every leadership change matters, and the
registry is consulted only *after* a break is detected.

## 3. The instrument, and the constraint it lives under

Five independent metric families, 22 series:

| family | metrics |
|---|---|
| PUBLICATION | judgments, median reasons length, share with reasons, share appeal |
| DOCKET | fees, damages, proof dispute, expert, settlement, default |
| STATUTORY | court article HHI, top-50 share, court/bar top-50 overlap, core turnover |
| ECOLOGY | hybrid rate, named-fiqh share, traceability, source HHI |
| FORMULA | formula share, innovation rate, top-10 concentration, court formula share |

Four transparent change-point methods — CUSUM, Page-Hinkley, piecewise level,
piecewise trend — and **no hand-picked threshold anywhere**. Every statistic is
scored against a permutation null built from the series' own values, 2000
permutations, fixed seed, α = 0.05.

The constraint is brutal and is stated first: **14 to 18 quarters**. Detection
on that many points is weak, and a battery that is not calibrated against its
own false-alarm rate would find breaks everywhere. So the whole battery was
also pointed at 200 shuffled redraws of itself.

## 4. Is this one stationary process? No.

| | observed | null (200 shuffled redraws) |
|---|--:|--:|
| metrics with any significant method | **12 of 22** (0.5455) | 0.11 per metric, mean 2.42 metrics per draw |
| multi-layer candidate **quarters** | **6** | mean 0.365, **max 3 in any draw** |

`OBSERVED_EXCEEDS_EVERY_NULL_DRAW`. Six multi-layer candidate quarters is
outside the entire null distribution of 200 shuffles. **The corpus is not one
stationary process**, and the previous programmes' implicit assumption was
wrong.

## 4b. Which families move, and the one that does not

| family | metrics tested | firing | break candidates | share |
|---|--:|--:|--:|--:|
| DOCKET | 6 | 5 | 5 | **0.8333** |
| FORMULA | 4 | 3 | 1 | 0.75 |
| PUBLICATION | 4 | 2 | 2 | 0.5 |
| STATUTORY | 4 | 2 | 1 | 0.5 |
| **ECOLOGY** | 4 | **0** | **0** | **0.0** |

The non-stationarity is not spread evenly. It is concentrated in what gets
published and which claims arrive, and it thins as the metric gets closer to
legal substance.

**And the authority ecology does not move at all.** Hybrid rate, named-fiqh
share, source concentration and traceability: four metrics, four methods each,
not one significant break. The layer this repository has spent the most effort
on — what a court reaches for when it reaches outside a statute — is the one
family a single data-generating process still describes over the whole window.

That is reported as prominently as the families that move, because it bounds
what the non-stationarity is about.

## 5. And then the finding that matters more

The six candidates are **1443Q3, 1443Q4, 1444Q1, 1444Q2, 1444Q3, 1444Q4** —
one contiguous block of six quarters. That is not a break. It is a sustained
period during which the corpus behaved differently.

And DOCKET appears in five of the six.

So the battery was asked one further question: does any candidate survive if
the two families that describe *what gets published* rather than *what courts
do* are removed?

**`candidatesSurvivingWithoutTheObservationSystem`: none. Zero of six.**

Not one candidate regime break is supported by two of STATUTORY, ECOLOGY and
FORMULA on their own. Every multi-layer signal in this corpus is anchored in
the observation system.

Under the taxonomy this is a `PUBLICATION_REGIME_SHIFT` candidate, not an
institutional one — and it is a confound for every other family, because a
change in which cases get published changes every content metric computed over
them.

## 6. Breaks without events, and events without breaks

Detected first, looked up afterwards. Both directions are recorded because
both are results.

**`UNEXPLAINED_REGIME_BREAK`** — 1444Q2 (docket, formula, publication), 1444Q3
(docket, statutory), 1446Q2 (formula only, a watch). They stay unexplained. No
event was searched for until after the signal, and none was found near them.

**`BREAK_WITH_A_NEARBY_EVENT`** — 1443Q3, 1443Q4 and 1444Q1 sit within one
quarter of the Law of Evidence's verified commencement; 1444Q4 and 1445Q2 sit
near the Civil Transactions Law's. **A nearby event is a coincidence in time at
quarter resolution and is never an explanation.**

**`EVENT_WITH_NO_OBSERVABLE_REGIME_BREAK`** — the February 2021 four-law
package announcement, and the Law of Evidence's own registry signal at its old
1443Q1 clock. A real institutional event with no measurable change in the
process is a valid result and is not forced into one.

## 7. Leadership: the variable that cannot be tested here

A bounded official lookup, restricted to institutions represented in this
corpus, and no biographies.

- The Minister of Justice was appointed in 1436H and **the lookup found no
  change of holder inside the corpus window**.
- The Najiz courts platform launched in 2019, **before the window opens**.
- No in-window jurisdiction transfer or ministry restructuring affecting the
  commercial courts was found.

So the most-discussed regime variable in any conversation about Saudi legal
change **is not available to this analysis at all**. That is a limit on what
can be tested, reported rather than filled with speculation. It also settles
the temptation empirically: there is no minister change to attribute anything
to.

## 8. Does regime segmentation make anything forecastable?

The hope was that targets marked NOT FORECASTABLE might be *not forecastable
across regimes* but stable within them. Tested properly: rolling origin, and at
each origin the break is re-detected **using only the quarters before that
origin** and must clear the same permutation bar. No retrospective
segmentation leakage.

22 series. **Segmentation wins on none of them.**
`REGIME_SEGMENTATION_DOES_NOT_IMPROVE_FORECASTS`, and the baseline it fails to
beat is the same one nothing in this repository has ever beaten: last value.

NOT FORECASTABLE stays NOT FORECASTABLE.

## 9. Regime-aware retrieval ageing

Median top-50 displacement is **22.0** per quarter overall — at candidate-break
steps **22.0**, away from them **24.0**. Decay is not worse around candidate
breaks; if anything it is marginally lower, and with 7 steps touching a
candidate the comparison is `INSUFFICIENT_TO_COMPARE` in any case.

So a regime-triggered refresh does not earn its place. **Periodic refresh
stands**, as it did against event-triggered refresh in the clock programme, and
for the same reason: staleness is a clock.

## 10. Ecology vintages: not built, and why

`NO_SEGMENTS_SUPPORTED`. Vintages by regime were to be built only where a
candidate survives removing the observation system, and none does. Cutting code
and article ecologies at those quarters would label a change in what got
published as a change in how codes behave — which is the storytelling this
programme exists to avoid. The schema is recorded for the day a content-anchored
candidate appears.

## 11. AI, under the revised question

The question is no longer *will AI make concentration rise*. It is: **does a
verified deployment coincide with a detectable transition into a new
authority-use regime, and which layers define it?**

Seven verified adoption events. **Evaluable: zero.** None reaches the
adjudicatory workflow this corpus observes, so none has a corpus quarter to
align with a break.
`NO_AI_EVENT_CAN_BE_ASSOCIATED_WITH_AN_OBSERVABLE_BREAK` — a statement about
linkability, not about whether the deployments changed anything.

And the standing prohibition, sharpened: **a regime break is never evidence of
AI, and an AI event is never a reason to look harder for a break.**
`AI_DEPLOYMENT` with `NO_REGIME_BREAK` is an equally reportable answer.

## 12. REGIME_DETECTOR_ERA_1, frozen

Methods, α, permutations, seed, minimum segment, escalation rule and the
measured false-alarm behaviour are frozen in
`frozen/regime_detector_era_1.json` before any future quarter exists.

Escalation: no significant method → `NO_DETECTABLE_BREAK`; one family →
`WATCH`; two or more independent families at the same quarter ±1 →
`REGIME_CANDIDATE`.

Prospective rules, also frozen: a future candidate is recorded permanently
whether or not an event is later found for it; thresholds are never retuned
after seeing a result; an unexplained break stays unexplained; a verified event
with no break is recorded as such.

**No earlier detector era is touched.** Prospective Era 1, Doctrinal Era 2 and
Formula Era 1 all stand, and all are now read as within-regime baselines.

## 13. Forecasts become regime-conditional

Every forecast now carries `REGIME_ASSUMPTION: no material detected regime
break before target maturity`, and four statuses: `SCORED`,
`REGIME_BREAK_BEFORE_TARGET`, `VOID_DATA_SHIFT`, `OPEN`.

The anti-abuse rule is the important half. `REGIME_BREAK_BEFORE_TARGET` is
defined by the frozen detector above, not by whether a forecast was going to
miss, and the detector was frozen before any future quarter exists. **It may
never be used to excuse a bad forecast.**

Two modes, never mixed: **Mode A**, what happens next if institutional
conditions remain materially unchanged — how every existing forecast is now
read; **Mode B**, what patterns would be consistent with a specified verified
institutional transition — conditional, unscored. Six branches are named
(`CURRENT_REGIME_CONTINUES`, `NEW_MAJOR_CODE`, `VERIFIED_BAR_AI`,
`VERIFIED_BENCH_AI`, `PUBLICATION_REGIME_CHANGE`,
`MAJOR_INSTITUTIONAL_RESTRUCTURING`) and **none carries a probability**,
because no calibration supports one.

---

## The question, answered

> Is Saudi law-in-action best represented as one evolving trajectory, or as a
> sequence of empirically distinguishable institutional regimes separated by
> structural breaks?

**Neither, on this evidence, and the honest answer sits between them.** It is
demonstrably not one stationary process: six multi-layer candidate quarters
against a null that never produced more than three in two hundred shuffles.
But the non-stationarity that is detectable here is **anchored entirely in the
observation system** — publication and docket composition — and it forms one
contiguous six-quarter block rather than a clean break. Not a single candidate
survives removing those two families. On present evidence this corpus contains
a *publication* regime change, and no institutional regime change in legal
content that can be separated from it.

That is a weaker claim than "regimes exist" and a much stronger one than "one
trajectory". It is also the claim the data supports.

> And if regimes exist, can the repository detect a new one prospectively
> before retrospectively inventing a story about why it changed?

**The instrument for that now exists and is frozen, and its limits are
measured rather than assumed.** It fires on 11 per cent of metrics under the
null and produces a multi-layer candidate in 0.31 of null draws, so a
single coherent quarter is not evidence; the count of them is. It detects
before it looks up, it records breaks with no event and events with no break,
and its thresholds cannot be moved after a result.

What it cannot do is separate a change in Saudi adjudication from a change in
what Saudi adjudication publishes. Until a publication date exists per
judgment, that limit is structural, and it is the single thing most worth
fixing.

## Standing limitations

- 14 to 18 quarters. Detection is weak and the false-alarm calibration is the
  only thing that makes any detection readable.
- Publication instability is itself a candidate regime variable **and** a
  confound for every other family. It cannot currently be netted out.
- The window contains no Ministry of Justice leadership change and no in-window
  restructuring this lookup could find.
- Candidate quarters form a contiguous block, so "the break quarter" is not
  identified even where a break is.
- Nothing here is causal. No event in the registry is offered as the reason for
  any break, and no individual is modelled.
