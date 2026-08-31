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

**No model beats persistence on any scalar series.** Fourteen folds, six
series, two models. The best mean skill is +0.0275 with a worst fold of
−1.564.

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
