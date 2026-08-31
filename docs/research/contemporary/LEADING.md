# The layer before the judgment

A judgment is a late observation. By the time a provision appears in a court's
reasoning it has been enacted, commenced, argued and decided; the corpus is
the last place a legal change becomes visible, not the first. The Horizon
Scanner watches the corpus. This watches what moves before it, and freezes
what each signal should imply while the later data does not exist yet.

> EXTERNAL LEGAL SIGNAL → known at → expected observables → forecast or watch
> → later court data → score

**PROSPECTIVE_DETECTOR_ERA_1 is closed.** Nothing in this session retunes a
detector, moves a threshold, redefines a scorable quarter or edits an issued
forecast. The era is frozen in `frozen/detector_era_1.json` with its contract,
its armed detectors, its historical alarm budget and its code hashes; any
future change produces ERA 2 as a new object, and era 2 never erases era 1's
record.

---

## 1. The signal registry, and the rule about credit

`legal_signal_registry.json`: six event types (legislative, regulatory,
judicial-institutional, technology, infrastructure, emerging subject), four
source grades, and for every entry both `verified_facts` and
`claims_not_established`. Seven signals from one bounded official-source pass.
News commentary, academic speculation and vendor marketing are excluded by
definition.

The field that matters most is not the effective date. It is **`known_at`**,
and beside it `first_recorded_at`:

> **All 7 seed signals are BACKFILLED_EVENT — necessarily, and by
> computation.**

The registry was created today, so nothing in it could have been recorded
before today. `leading.py` computes the class from `first_recorded_at` against
the registry's own `prospectiveFrom` date rather than trusting the declared
label, and reports any mismatch as a bug. There are none.

That produces the honest headline of this session: **the observatory has zero
prospective captures, and cannot have any yet.** The first
`PROSPECTIVE_CAPTURE` will be the first signal recorded after this commit, and
only those may ever support a sentence beginning "the observatory anticipated".

## 2. What the seed contains

| id | type | known at | grade | class |
|---|---|---|---|---|
| LSIG-0001 | legislative | 2021-02-08 | S2 | backfilled |
| LSIG-0002 | legislative | 2021-02-08 | S2 | backfilled |
| LSIG-0003 | legislative | 2021-02-08 | S2 | backfilled |
| LSIG-0004 | legislative | 2026-04-15 | S2 | backfilled |
| LSIG-0005 | technology / AI | 2026 | S1 | backfilled |
| LSIG-0006 | judicial-institutional | 2025-02-04 | S1 | backfilled |
| LSIG-0007 | infrastructure | 2024 | S3 | backfilled |

LSIG-0001 is the anchor: the February 2021 announcement of four laws —
Personal Status, Civil Transactions, the Penal Code for Discretionary
Sentences, and the Law of Evidence. It is the `known_at` for both instruments
this corpus watched arrive, and it is why those two are the only clean
arrivals available.

Four entries form the `shocksView`. "Shock" here means a timestamped external
legal event of system-wide scope and carries **no causal claim**.

## 3. Complexity did not earn its place

The entrant rule is court citation share. Eight candidate features were tested
one at a time as *court share plus one*, on the same temporal folds:

party share, rank acceleration, momentum, judgment count, court/bar ratio,
instrument age, co-citation breadth, new-instrument flag.

**None improved mean precision by two points while improving a majority of
folds.** `COURT_SHARE_REMAINS_THE_RULE`. Both conditions were required
deliberately: a feature that lifts the mean on one lucky fold has not earned
anything.

## 4. The long-tail bar signal, tested properly and killed

The Horizon Scanner found the one subset where advocacy adds information above
the bench's own persistence: rare articles, partial r **+0.0638**, positive on
7 of 11 folds. A correlation on a noisy subset deserves a cohort test before
anyone believes it, so:

- **Treatment:** a rare provision's first party appearance — a party citation
  in a quarter with none in the two before.
- **Controls:** rare articles in the same instrument and the same
  prior-court-visibility band with no party appearance that quarter.
- **Outcome:** the court's own citation share at +1, +2 and +4 quarters.

84 treated units, 971 controls, **70 matched**.

| horizon | pairs | treated | matched control | mean difference | sign test |
|---|---:|---:|---:|---:|---:|
| +1 | 70 | 0.001084 | 0.000622 | +0.000462 | **0.4286** |
| +2 | 65 | 0.001058 | 0.000674 | +0.000384 | **0.3385** |
| +4 | 52 | 0.001579 | 0.000694 | +0.000885 | **0.3077** |

The mean difference is positive at every horizon and the **sign test is below
0.5 at every horizon**. A handful of large positives carry a mean whose median
pair is negative — and it gets worse, not better, with the horizon.

**`NO_BAR_DISCOVERY_SIGNAL_AFTER_MATCHING`.** The aggregate correlation does
not survive. It is recorded in `FORECASTING_LIMITS.md` so nobody runs it again
and reports the mean without the sign test.

Two honest notes on the treatment. The threshold was set at three party
citations and returned **zero** treated units — the strict party voice carries
11,794 mentions across 18 quarters, so a rare provision almost never reaches
three in a quarter. One is what the data supports, and a one-citation
treatment is weak. And "rare" had to mean the bottom half *of the eligible
pool*: ranked against every string the extractor ever saw, an article with
five cumulative citations is already in the top quarter of everything, and the
first version of the cohort was empty for that reason.

## 5. Who finds an authority first predicts what happens to it

Different question from aggregate lead-lag, and it gets a different answer.
Survival is the share of later scorable quarters in which the court cites the
article again.

| first mover | n | mean survival | reached top 100 |
|---|---:|---:|---:|
| **COURT_FIRST** | 295 | **0.4659** | highest |
| SAME_PERIOD | 108 | 0.3392 | |
| BAR_FIRST | 94 | 0.2897 | |
| COURT_ONLY | 439 | 0.1337 | |
| BAR_ONLY | 221 | **0.0** | |

An authority the bench finds first survives in the bench's reasoning at
roughly **1.6 times** the rate of one the bar finds first. And an authority
only ever cited by parties never enters court reasoning at all — true by
construction of the survival measure, and worth stating because 221 articles
sit in that row.

This is consistent with the aggregate negative rather than a rescue of it:
the bar's citations do not lead, and where the bar gets somewhere first, the
provision is *less* likely to stick.

## 6. Which new doctrinal sources persist, and which diffuse

Thirty-four (34) code-local source appearances tracked from emergence, with
features recorded **at emergence only**: first-quarter judgments, codes,
articles, cities.

| outcome | n |
|---|---:|
| PERSISTENT | 22 |
| EMERGING | 6 |
| DISAPPEARED | 6 |

The emergence features are reported for both outcomes side by side so a future
entrant can be scored against them. No threshold is issued as a forecast until
there is an entrant to score it on — the direction is readable, the rule is
not yet earned.

Diffusion is tracked as codes and cities reached by +1, +2 and +4 quarters.
It is **spread, not influence**, and the identity universe's 28 members mean
"new" is always *new beside that code*, never new to Saudi law.

## 7. Transition velocity, in components

No composite score. Five components, of which two are measurable now:

- **CORE_ENTRY_LATENCY** — median 2 quarters from first court citation to
  top-50 entry, over 8 in-window instruments that got there.
- **BAR_UPTAKE_LATENCY** — signed quarters between the two voices' first use.
- **STATUTORY_UPTAKE_LATENCY** — *not measurable*: commencement dates are not
  held per instrument, so every latency here starts from first *observed* use,
  not from the day the rule took effect.
- **COMPANION_FORMATION_LATENCY** — *not measurable*: the identity layer
  starts at 1443 and only four codes carry enough local attachment.

## 8. The publication-health gate

Frozen bands for every observation-system variable, and three void rules — a
volume floor, a reasons-length excursion, and a claim-family move above 0.20,
which is larger than any move observed. The decision that matters is the order
of operations:

> the void decision is made from these bands **before** the forecast error is
> computed, and never after.

A forecast that misses in a quarter whose publication regime broke is
`VOID_DATA_SHIFT`. A forecast that misses in a healthy quarter is a miss.

## 9. Refresh as a forecast, and companions as a policy

**REFRESH_DUE_WINDOW = 1Q**, driven by `TOP50_DISPLACEMENT`. Issued as a
forecast with a band, not as a detector: a snapshot taken at 1446Q2 is
predicted to need rebuilding within one quarter, and the claim is wrong if
displacement stays below 30 per cent for two.

And a retrieval system does not need one refresh policy. By companion
stability:

| code | mean top-3 Jaccard | class | suggested refresh |
|---|---:|---|---|
| sharia_procedure_law | 1.0 | STABLE | annual |
| commercial_courts_law | 0.875 | STABLE | annual |
| commercial_courts_implementing_regulation | 0.7857 | VARIABLE | two quarters |
| evidence_law | 0.6167 | VARIABLE | two quarters |
| aml_law | — | LOW_SUPPORT | not issued |
| arbitration_law | — | LOW_SUPPORT | not issued |
| bankruptcy_law | — | LOW_SUPPORT | not issued |
| basic_law_of_governance | — | LOW_SUPPORT | not issued |
| civil_transactions_law | — | LOW_SUPPORT | not issued |
| commercial_books_law | — | LOW_SUPPORT | not issued |
| companies_law | — | LOW_SUPPORT | not issued |
| enforcement_implementing_regulation | — | LOW_SUPPORT | not issued |
| enforcement_law | — | LOW_SUPPORT | not issued |
| franchise_law | — | LOW_SUPPORT | not issued |
| health_system_regulation | — | LOW_SUPPORT | not issued |
| judicial_costs_law | — | LOW_SUPPORT | not issued |
| labor_law | — | LOW_SUPPORT | not issued |
| law_practice_implementing_regulation | — | LOW_SUPPORT | not issued |
| law_practice_law | — | LOW_SUPPORT | not issued |
| qismah_regulation | — | LOW_SUPPORT | not issued |
| sharia_procedure_implementing_regulation | — | LOW_SUPPORT | not issued |
| trade_names_law | — | LOW_SUPPORT | not issued |

STABLE sets can be rebuilt annually; FAST_MOVING ones cannot. This is a
measurement, not an implementation, and no product is built.

## 10. Calibration: rank only

Fold-to-fold precision on the entrant target spreads more than 0.35. A
HIGH/MEDIUM/LOW band would have to map onto hit rates stable enough to mean
something, and these are not. **`RANK_ONLY`**, and intuitive confidence labels
are forbidden.

## 11. Would the scanner have caught the two transitions it can see?

Retrospective pseudo-prospective folds on the Law of Evidence and the Civil
Transactions Law: pretend the cutoff is each one's first observed court
quarter, apply the same rule, ask what the scanner would have said.

Both are labelled **RETROSPECTIVE_PSEUDO_PROSPECTIVE** and neither counts as
foresight. And the leakage is stated rather than hidden: the median latency
used as the rule is computed over in-window arrivals **including these two**,
so the calibration is optimistic. With two clean cases there is no honest way
to hold them out and still have a rule.

## 12. The wager and the watch

**REPOSITORY_BET_001.** A legal retrieval snapshot frozen at 1446Q2 needs
rebuilding within one quarter, and the trigger that fires is **rank
displacement, not missing content**. Chosen on the backtest, not on appetite:
observable without any external event, scorable against numbers fixed now, no
leakage, meaningful if right — it says a Saudi legal retrieval system must
rebuild its ranking four times more often than a coverage-driven policy would
— and informative if wrong. The rare-article signal was *not* chosen: the
cohort test killed it in this same session, and betting on a dead signal is
how a repository loses its record.

**AI_WATCH_001.** The first validated AI-as-subject legal issue, against a
frozen baseline of 0 in 50,666. No probability. It was chosen over the more
consequential *first verified MoJ commercial research-AI deployment* on
observability alone: the L3 watch runs on a corpus already held with a
classifier already frozen, so it can actually fire. Its escalation ladder
records milestones — first statutory anchor, first non-statutory authority,
first doctrinal companion — because the interesting question when AI reaches
the courts is not how many cases there are but how the system absorbs the
issue.

---

## The four temporal layers

1. **Observatory** — what is happening now.
2. **Explanatory layers** — speakers, codes, articles, companions, docket.
3. **Horizon Scanner** — forecast, detect, watch, frozen as ERA 1.
4. **Leading-Indicator Observatory** — timestamped external signals before the
   judicial outcome matures.

The chain they are built to trace, end to end:

> external event → early legal signal → advocacy → court visibility →
> operational core → doctrinal companion → future retrieval state

Not every event traverses every stage. Measuring which do is the point, and
this session established that at least one stage of that chain — advocacy to
court visibility — does not carry the traffic the chain assumes.

## Standing limitations

- Every seed signal is backfilled. The observatory has no prospective record
  yet and will not until a signal is recorded after this commit.
- The bounded seed is one pass, not a maintained feed. Absence means we did
  not verify something, never that it does not exist.
- The cohort test that killed the bar-discovery signal rests on a
  one-citation treatment; a stronger treatment definition is not available in
  this corpus.
- Latencies start from first *observed* use, not from commencement.
- No causal language anywhere: a signal is timestamped, an observable is
  expected, and a later movement is an association until something identifies
  it.
