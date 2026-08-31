# What this repository cannot forecast, and why

A scientific asset should know its ignorance as precisely as it knows its
results. This file is the permanent record of the second kind. Every entry is
a refusal that was made deliberately, with the reason and the condition that
would lift it.

Nothing here is a to-do list. Several of these will never be liftable.

---

## Structural limits

**Temporal depth.** Eighteen hijri quarters, ten of them SCORABLE. Every fold
count in this repository is bounded by that. A worst-fold statistic on eight
folds is a weak instrument, and a detector's alarm rate measured over 56
evaluable periods has wide error nobody has quantified. *Lifted by:* time.

**Publication instability.** The published set is not compositionally stable —
median reasons length moves from 1143 to 1687 across the window and the claim
mix inverts between fees and damages. Any series here mixes what courts do
with what the publisher releases. *Lifted by:* a publication date per
judgment, which does not exist in either institution's metadata.

**Decision-to-publication lag: NOT_AVAILABLE.** The corpus holds a decision
date and our own retrieval timestamp. Without a publication date the two
sources of delay — the law changing late, and us learning late — cannot be
separated. *Lifted by:* the publisher exposing a publication date.

**The identity universe is the extractor's vocabulary.** Twenty-eight
canonical identities. Every diversity, entropy, novelty and concentration
figure about doctrine is a floor, and "the canon is compact" is not
distinguishable from "the extractor is compact". *Lifted by:* a larger
vocabulary — which would open a new measurement era and break every detector
series at the boundary.

## Targets refused for want of data

| target | refusal | condition that lifts it |
|---|---|---|
| Evidence Law named-fiqh trend | INSUFFICIENT_TEMPORAL_DEPTH, 3 folds | identity layer support in more quarters |
| doctrinal companions, 7 of 11 codes | LOW_SUPPORT, 1 to 57 locally attached units | more corpus, or a wider locality window that the construct check would not support |
| statutory amendment forecasting | HOLD, no amendment events with reliable dates and article-version mapping | article-version history, which the registry does not hold |
| docket composition forecasting | HOLD, the target would mostly be the publisher's release policy | a publication date, again |
| statutory uptake latency from commencement | commencement dates are not held per instrument | registry metadata |
| article-version supersession | NOT_AVAILABLE | article-level version history |
| instrument-level temporal validity | INSUFFICIENT_REGISTRY_COVERAGE — 2 of 291 tracks carry a parseable hijri publication year | registry metadata |

## Signals tested and killed

These are not limits of data. They are answers, and they belong here because a
future session will otherwise be tempted to try them again.

**The bar does not lead the bench.** Court persistence correlates 0.9625 with
the next quarter; the bar's contribution is −0.0107 once that is held fixed.
Of 460 articles observed first in both voices, 56.3 per cent appear in the
court's voice first.

**And it does not lead in the long tail either.** The one positive subset —
rare articles, partial r +0.0638 on 7 of 11 folds — was given the cohort test
it deserved: 84 treated units, 70 matched on instrument and prior-visibility
band. The mean difference is positive at every horizon and the **sign test is
below 0.5 at every horizon** (0.4286, 0.3385, 0.3077). A few large positives
carry a mean whose median pair is negative. Verdict:
`NO_BAR_DISCOVERY_SIGNAL_AFTER_MATCHING`.

**No feature beats court share.** Eight candidates tested one at a time
against court citation share alone, on the same folds — party share, rank
acceleration, momentum, judgment count, court/bar ratio, instrument age,
co-citation breadth, new-instrument flag. None improved mean precision by two
points while improving a majority of folds. `COURT_SHARE_REMAINS_THE_RULE`,
and the three-feature additive rule is *worse* than its own best ingredient.

**Doctrinal persistence is not forecastable.** Base rate 0.3772; the best
emergence feature reaches lift 1.17. And with 114 eligible code-local units
across the whole window there are not enough per-quarter cohorts to build
rolling folds at all, so what was run is a single-sample ranking check rather
than a backtest. Verdict `NO_USABLE_SIGNAL_USE_DETECT_OR_WATCH`, and
REPOSITORY_BET_002 was refused on it.

**The doctrinal court-first advantage does not survive de-boilerplating.** The
unmatched contrast is the largest in the programme — court-first sources
persist at 0.5882 against bar-first 0.2857 — and it fails both controls:
matching leaves 6 pairs, and removing circulating wording flips the matched
verdict to BAR_FIRST_NOT_WORSE_AFTER_MATCHING.

**CORRECTED, and the correction matters.** The sentence that stood here — that
a meaningful part of the apparent doctrinal leadership is a formula circulating
among courts — read more into the second control than it can carry. Eleven
single-class ablations of the recurring wording were run and none reproduces
the flip; a *random* removal of the same size flips it in 0.9 of seeded draws.
The control removes a quarter of the evidence and a six-pair comparison moves
when it does, whatever leaves. Verdict
`FLIP_TRACKS_REMOVAL_VOLUME_NOT_WORDING_CLASS`. The flip stands as a fact; it
is not evidence about wording. The binding limit was always the six pairs.
*Lifted by:* thirty matched pairs, which needs more corpus.

**No model beats persistence on any scalar series.** Fourteen folds, six
series, two models. The best mean skill is +0.0275 with a worst fold of
−1.564.

**The wording layer is not the early layer.** Its historical mobility is the
highest of the three measured layers, and in both available transitions it
moves AFTER statutory visibility — latency 2 against 0, and 3 against 0 — and
predicts later top-50 entry at lift 1.3571 against the court-citation
baseline's 3.7582. Mobility and earliness are different properties and had been
conflated. Recorded as T7 in `THEORY_LOG.md`.

**Formula persistence is a near miss, not a signal.** The largest lift this
repository has measured on rolling folds — 10.7077 mean over 7 folds, for a
formula observed in more than one city in its first scorable quarter — fires
on a median of 14 formulas per fold and one fold is zero. The consistent
feature, court origin, is positive on 8 folds of 8 and its mean lift is 1.4634.
Neither was issued. Recorded as NEAR_MISS_FORMULA_PERSISTENCE in the ledger so
a future session with more data knows exactly where to look. *Lifted by:* fold
cohorts of at least 20.

**And an earlier draft of that test had a lift above 20, from leakage.**
Features read over the whole window — the cities or codes a formula EVER
reached — are the outcome restated. Every feature in the published version is
read from the first scorable quarter only. Noted here because the leaking
version looked like the best result in the repository.

**Legal transitions available for calibration: TWO.** Both backfilled. The
Law of Evidence and the Civil Transactions Law are the only events with a legal
clock independent of the corpus, a linkable instrument and enough court use.
Fifty-nine other instruments arrive inside the window and not one carries a
verifiable known_at or effective_at, so their T=0 would have to be read off the
first citation — which is the outcome. *Lifted by:* registry metadata that does
not exist yet, or time.

**The publication-health gate cannot act as a veto.** Written to reject a
transition read under a moving observation system, it fires on 12 of 13
quarter-to-quarter steps. A veto that rejects everything is not a veto, so it
is demoted to a standing caveat on every latency in `TRANSITIONS.md` — and
deliberately NOT loosened, because loosening a control until it permits the
result is how a control stops being one. *Lifted by:* a publication date, which
neither institution publishes.

**The transition negative control separates arrivals, not events.** Fifteen
pseudo-events on mature instruments never produce a staged latency vector,
which makes the two real signatures readable. But what it demonstrates is that
an arriving instrument looks different from a settled one, not that a legal
event looks different from no event. A pseudo-arrival control would settle it
and no instrument in this corpus can provide one, because a pseudo-arrival
needs a clock. *Lifted by:* the same registry metadata.

**Retrieval staleness is a clock, not a signal.** It fires in 15 of 15
pseudo-events with no legal event at all. `TOP50_DISPLACEMENT` is retained as
the refresh trigger and the proposal to warn earlier from formula or companion
movement is HOLD: there is one event with an evaluable pre-event snapshot, and
earlier-than-a-clock is not earlier-than-a-signal.

## Calibration refused

**Probabilities on entrant forecasts: RANK_ONLY.** Fold-to-fold precision for
the best signal ranges across a spread wider than 0.35. A HIGH/MEDIUM/LOW
label would have to map onto hit rates stable enough to mean something, and
these are not. The forecast issues a ranked list and no probabilities, and
intuitive confidence labels are forbidden.

**Probabilities on watch targets: none, by design.** A rare emerging event
with no base rate — the first AI legal issue, a new Board collection — gets a
watch target and no number. Inventing one would be false precision.

## Event-linkage limits

**No AI deployment reaches L3_WORKFLOW_MATCH.** Seven verified events, none in
the workflow this corpus observes. No event study is permitted, and the
exposure matrix records that as its most important column.

**The Board of Grievances is closed at E0_CHRONOLOGY_ONLY**, on two
independent grounds: no readable access route, and a published record that
ends at 1444 AH, before the deployment. The preregistration is frozen and
dormant against a trigger.

**Every seed signal is BACKFILLED.** The legal signal registry was created
today, so all seven of its entries are backfilled by construction and none may
ever support a claim that this observatory anticipated anything. The class is
computed from timestamps, not declared.

## What this list is for

Two things. It stops a future session re-running a dead test and reporting the
mean without the sign test. And it makes the repository's claims legible: when
something here does eventually forecast or detect well, a reader can see the
whole denominator of what was tried and refused alongside it.
