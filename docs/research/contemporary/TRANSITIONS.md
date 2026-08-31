# When Saudi law changes, what moves first?

Every layer this repository measures has been described on its own. None has
been watched *through* a transition. That gap matters for one reason: when a
verified AI deployment finally becomes observable in a corpus like this one,
the useful sentence is not "AI changed something". It is

> the first departure occurred in layer X, followed Y quarters later by layer
> Z, while the remaining layers stayed inside their frozen historical bounds

and that sentence is only available to someone who already knows what an
**ordinary** legal transition looks like. This file measures ordinary
transitions so an extraordinary one could be recognised.

**Nothing here is causal.** A layer crossing a criterion after a commencement
date is an ordering of observations, never the statute acting on the court.

---

## Scope corrections entered first

Three, and not one of them changes a number.

1. The formula unit is an **AUTHORITY-ADJACENT RECURRING FORMULA** — an exact
   normalised ±90-character window around an authority mention. It is not a
   representation of a judgment's language.
2. "If AI changes Saudi legal reasoning, the wording layer will move first" is
   **withdrawn**. The permitted statement is: *among the three measured layers,
   authority-adjacent recurring formulas show the greatest historical mobility;
   whether this layer responds first to future AI adoption is a prospective
   hypothesis.*
3. "Source and formula are inseparable" narrows to: *at the current
   exact-fingerprint resolution, no circulating formula is observed with more
   than one canonical authority identity.* Near-family equivalence is
   unresolved.

Section 5 then tests correction 2 against real transitions, which is the first
time it has been tested rather than asserted.

## 1. Which events qualify, decided on their clock

An event qualifies only if it has a legal clock independent of the corpus, a
corpus-linkable instrument, a pre-period inside the window, and enough court
use to read six layers. Nothing is selected because its series looks
interesting.

| event | instrument | class |
|---|---|---|
| **LSIG-0002** Law of Evidence | evidence_law | **CALIBRATION_EVENT** |
| **LSIG-0003** Civil Transactions Law | civil_transactions_law | **CALIBRATION_EVENT** |
| LSIG-0001 four-law announcement | — | INSUFFICIENT_DATA |
| LSIG-0004 Enforcement Law | — | INSUFFICIENT_DATA |
| LSIG-0005 Board AI principles | — | INSUFFICIENT_DATA |
| LSIG-0006 Virtual Enforcement Court | — | INSUFFICIENT_DATA |
| LSIG-0007 Board judgments collection | — | INSUFFICIENT_DATA |

And the harder exclusion: **59 instruments arrive inside the window and none of
them carries a verifiable legal clock.** Reading T=0 off the first citation
would make the event clock a function of the outcome, which is the one mistake
this design exists to avoid. Two events it is.

## 2. T=0, and what it is not

| | announcement | legal effect | T=0 | first actual court use |
|---|---|---|---|---|
| Evidence Law | 2021-02-08 | 1443 | **1443Q1** | 1443Q1 |
| Civil Transactions Law | 2021-02-08 | 1445 | **1445Q1** | 1445Q1 |

Both clocks are `LEGAL_EFFECTIVE_YEAR`. The first citation is recorded beside
T=0 and never used as it. No commencement date exists per instrument in this
corpus, so the first quarter of the registry's hijri effective year is used and
the quality is recorded rather than the date invented.

## 3. Layer zero, and it fails

Publication health runs before anything else and can veto everything above it.
It fires on **12 of 13** quarter-to-quarter steps: the composition of what is
published moves continuously.

| quarter | 1443Q2 | 1443Q3 | 1443Q4 | 1444Q1 | 1444Q2 | 1444Q3 | 1444Q4 | 1445Q1 | 1445Q2 | 1445Q3 | 1445Q4 | 1446Q1 | 1446Q2 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| flags | 4 | 4 | 3 | 4 | 5 | 2 | 0 | 1 | 2 | 1 | 1 | 1 | 2 |

A veto that rejects every transition there is is not a veto. So the gate is
**demoted to a standing caveat** on every latency in this file — and it is not
loosened until it passes, because loosening a control until it permits the
result is how a control stops being one.

It does buy one comparison. Evidence Law's window carries a mean of **3.67**
composition flags per quarter; the Civil Transactions Law's carries **2.11**.
The second transition is observed under the calmer regime.

## 4. The two transition signatures

Latency in quarters after T=0. `null` is no detected shift inside the frozen
six-quarter horizon.

| layer | Evidence Law | Civil Transactions Law |
|---|--:|--:|
| L2 bar statutory visibility | 4 | **0** |
| L3 court statutory visibility | **0** | **0** |
| L4 authority-adjacent formula | 2 | 3 |
| L5 authority ecology | **0** | **0** |
| L6 doctrinal companion | 2 | 2 |
| L7 operational core (top-50) | **0** | 2 |
| L8 retrieval staleness | NOT_EVALUABLE | 3 |

Three layers agree across both events — **court visibility, ecology and
companion formation**. Four differ: bar visibility, formula, core and
retrieval.

**Evidence Law.** Court use at T=0, top-50 at T=0, and the bar four quarters
behind. Article 29 alone carries 3756 court citations, entering at +2 and the
top-50 one quarter later; article 17 is there at T=0. Volume goes 4 → 6 → 37 →
927 judgments across 1443Q1–1444Q1: the law is visible immediately and becomes
the corpus's second-ranked instrument by 1444Q1, where it stays for nine
quarters.

**Civil Transactions Law.** Court and bar at T=0 together, rank 12 → 4 by
1445Q3, top-100 at +1 and top-50 at +2. Of the three articles named in advance,
**120** (111 court citations) and **107** enter at T=0; **720** enters at +3 and
reaches the top-50 in the same quarter it appears.

**Retrieval is not evaluable for Evidence Law** — T=0 is the first mature
quarter, so no snapshot can be frozen before it. Stated, not approximated.

## 5. Does the formula layer move first? No.

This is the test the previous programme's withdrawn claim needed.

| event | formula latency | court statutory latency | relation |
|---|--:|--:|---|
| Evidence Law | 2 | 0 | **AFTER** |
| Civil Transactions Law | 3 | 0 | **AFTER** |

`FORMULA_LAYER_MOVES_AFTER_STATUTORY_VISIBILITY`, in both transitions
available. **Greater historical mobility does not make a layer the earlier
one.** The prospective claim was already withdrawn as a scope correction; it
now has evidence against its ordinary-transition analogue.

And the ordering, for both events, is `S→D→F`: statute, then doctrine, then
wording. Evidence Law ties doctrine and formula at +2; the Civil Transactions
Law puts doctrine at +2 and formula at +3.

What this does **not** show: nothing here is about AI. An AI-driven transition
need not resemble a new-law transition — whether it does is the question the
whole instrument exists to answer.

## 6. Formula uptake: newly observed, or carried?

| event | newly observed | carried from older law | carried, never beside another instrument |
|---|--:|--:|--:|
| Evidence Law | 1965 | 4 | 0 |
| Civil Transactions Law | 109 | 4 | 7 |

Read with its warning. Evidence Law's T=0 leaves only four quarters of
pre-period, so "newly observed" is inflated by construction — a formula
circulating for years before the corpus opened is new here. The count is a
**ceiling on innovation, not a measure of it.** The Civil Transactions Law has
twelve quarters of pre-period and still shows 109 newly observed against 11
carried.

## 7. The transitions share their timing and differ in their content

Both form a repeated companion at exactly +2 quarters. What forms is not the
same kind of authority.

| | repeated sources | named jurist or book | generic | named share |
|---|--:|--:|--:|--:|
| Evidence Law | 24 | 9 | 6 | **0.375** |
| Civil Transactions Law | 10 | 2 | 6 | **0.2** |

Evidence Law's companions are named Hanbali books — al-Insaf, Kashshaf
al-Qina, Majmu al-Fatawa, al-Mughni, Muntaha al-Iradat, Zad al-Maad. The Civil
Transactions Law's are mostly generic: settled practice, trade custom,
unattributed fiqh, an unnamed maxim. The named-fiqh rate confirms it: Evidence
runs 0.2438 at 1444Q1 and decays to 0.0863; the Civil Transactions Law never
exceeds 0.0753.

**This is the transition-signature difference worth more than any latency.**
Same timing, different content — so a signature is a vector, not a speed.

## 8. Provenance: the doctrine was already there

| | already present system-wide | new code-local or globally new |
|---|--:|--:|
| Evidence Law | 18 | 10 |
| Civil Transactions Law | 21 | 0 |

Not one source that becomes a Civil Transactions Law companion is new to the
corpus. The doctrine a new statute acquires is doctrine the system already
had — which is also what a 28-identity extractor is most able to see, so both
counts are floors.

## 9. The negative control, and what it really shows

Fifteen pseudo-events: three instruments already mature when the window opens,
at every scorable quarter more than one quarter away from a real T=0.

- Every FIRST_VISIBILITY layer fires at **1.0**. That is the correct result and
  it is unflattering: for an instrument already visible, these criteria are a
  visibility test, not a transition detector.
- **No pseudo-event produces a staged latency vector** — share 0.0, with or
  without retrieval. Both real transitions do.
- The ecology **shift** sub-criterion false-positives at **0.6667**.
- Retrieval staleness fires at **1.0** — in every pseudo-event, with no legal
  event at all.

`BATTERY_DISCRIMINATES_ARRIVALS_ONLY`. The honest reading: the staging in the
two real signatures is not an artefact of the criteria, but what the control
separates is *arrivals from non-arrivals*, not *events from non-events*. A
pseudo-arrival control would settle that and no instrument in the corpus can
provide one, because a pseudo-arrival needs a clock.

## 10. Retrieval ages on a clock, not on events

Retrieval staleness fires in 15 of 15 pseudo-events. A frozen top-50 snapshot
passes 30 per cent displacement whether or not a law changes.

So **PHASE 33's candidate is HOLD**: using formula or companion movement as an
earlier refresh trigger cannot be backtested — one event has an evaluable
snapshot, and "earlier than a clock" is not earlier than a signal. The frozen
`TOP50_DISPLACEMENT` trigger is retained.

For anyone maintaining a legal AI: refresh policy should be driven by elapsed
quarters. A legal transition is a reason to refresh *sooner*, not the reason to
refresh at all.

## 11. Can an early layer predict a late one?

57 instrument arrivals, features read at the arrival quarter, target reached
top-50 later.

| feature | n | precision | base rate | lift |
|---|--:|--:|--:|--:|
| court citations at arrival ≥ 3 | 13 | 0.4615 | 0.1228 | **3.7582** |
| formula activity at arrival | 6 | 0.1667 | 0.1228 | 1.3571 |
| a repeated companion at arrival | 3 | 0.3333 | 0.1228 | 2.7143 |

Inside the stratum where the baseline is weak — arrivals with fewer than three
court citations — formula activity fires on four units and none of them reaches
the top-50. `FORMULA_ACTIVITY_IS_DESCRIPTIVE_ONLY`.

Companion formation at arrival is `LOW_SUPPORT` at n = 3, and for a structural
reason: **a repeated companion takes two quarters to form in both transitions,
so it barely exists at arrival.** That is a fact about the layer, not a failed
test.

`COURT_SHARE_REMAINS_THE_RULE`, for the fourth programme running.

## 12. Speed bands, and why they are not yet bands

| layer | band | events |
|---|---|--:|
| court statutory visibility | 0–0Q | 2 |
| authority ecology | 0–0Q | 2 |
| doctrinal companion | 2–2Q | 2 |
| authority-adjacent formula | 2–3Q | 2 |
| operational core | 0–2Q | 2 |
| bar statutory visibility | 0–4Q | 2 |
| retrieval staleness | 3–3Q | 1 |

A range read off two observations is a range, not a distribution.
FASTER_THAN_BASELINE cannot be said of any future transition until the library
holds enough events to have a baseline. The bands are recorded so a future
session inherits them instead of inventing them.

## 13. What was armed, and what was refused

**TRANSITION_BET_001 — REFUSED.** The candidate was that statutory visibility
precedes stable doctrinal-companion formation for the next major law. It is
true in both events. It is refused anyway: two backfilled events, whose
first-moving layer *sets* differ, with a negative control that separates
arrivals rather than events. Four calibration transitions sharing an ordering
would earn it.

**AI channel hypotheses, frozen with falsifiers.** Judicial research AI is
expected first in ecology and companions; judicial drafting AI first in the
authority-adjacent formula layer; bar research AI first in party visibility;
court-administration AI predicts no doctrinal shift by default. Each has a
written falsifier and a six-quarter minimum horizon, frozen now.

**Nothing identifies AI.** A formula-first transition does not mean AI. A
source-diversity shift does not mean AI. A signature may only be
`CONSISTENT_WITH` or `INCONSISTENT_WITH` a pre-registered channel hypothesis,
and an externally verified adoption event reaching this workflow remains
necessary. The registry holds **0** such events: seven verified deployments,
none above `L2_INSTITUTION_MATCH`.

**Signal without event** opens a `SURPRISE_LEDGER` entry and a registry search;
if nothing is found the class is `UNKNOWN_TRANSITION` and stays there.
**Event without signal** is recorded as `NO_OBSERVABLE_SHIFT_WITHIN_HORIZON`,
which is a result — and the horizon is frozen now precisely so nobody extends
it until something moves.

## 14. What this means for the code-associated environment

The Law of Evidence's non-statutory environment appears in the **same quarter**
the law becomes visible: the first judgments citing it already carry
non-statutory authority. A *repeated* companion — the stronger object — takes
two more quarters.

`CONSISTENT_WITH_CODE_ASSOCIATED_ENVIRONMENT`, with a qualification the paper
should carry: immediate presence is measured on two transitions, and the
companion object the claim leans on takes two quarters to form in both.
`CLAIM_ECOLOGIES.md` is not rewritten for a qualification two events support.

---

## The question, answered as far as it can be

> When Saudi law changes, what moves first — the statute's visibility, the
> court's wording around authority, the supplementary doctrine, the
> operational core, or the retrieval system's failure?

**The statute's visibility and the authority ecology, together, in the quarter
the law takes effect.** Then the doctrinal companion at two quarters, then the
wording at two to three. The operational core varies with the law's size — the
Law of Evidence was in the top-50 immediately; the Civil Transactions Law took
two quarters. Retrieval failure is last where it is measurable, and it is on a
clock of its own.

The bar is the layer that does not have an answer: four quarters behind for one
law and simultaneous for the other.

> And when a future verified AI deployment becomes observable, will its
> sequence look like an ordinary legal change?

**Unknown, and now answerable.** What exists today is a reference: two ordinary
transitions with `S→D→F` ordering, a companion at +2 in both, wording last in
both, and a negative control showing the staging is not manufactured by the
criteria. Four AI channel hypotheses are frozen against that reference with
falsifiers and a six-quarter horizon. The instrument is calibrated. The data
will decide.

## Standing limitations

- **Two calibration events, both backfilled.** Nothing here is foresight and
  nothing here may ever be credited as such.
- 59 in-window arrivals have no verifiable legal clock, so the sample cannot be
  grown without external registry work.
- The publication-health gate fires on 12 of 13 steps and is a caveat on every
  latency here.
- Quarter resolution: simultaneity is common and ties are reported as ties, not
  broken by a rule.
- The negative control separates arrivals from non-arrivals. It does not
  separate legal events from non-events, and no instrument in this corpus can
  provide a pseudo-arrival that would.
- Retrieval staleness is a clock, not an event signal.
- Nothing here is causal, and no transition signature identifies AI.
