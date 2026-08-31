# AI and Saudi law: what entered, where, and what we could ever measure

`FORESIGHT.md` said the adoption registry was empty and treated that as an
honest statement about what had been verified. It was not honest enough. It
recorded that this repository had not looked, and presented it as though
nothing were findable. A bounded search of official Saudi sources found seven
events, **three of them before the baseline cutoff**, and one of them a
judicial legal-research system running in a Saudi court.

That correction changes two things and leaves a third standing.

- **The AI-transition baseline is not a pre-adoption baseline.** It never
  claimed to be, and now it can say precisely what was already underway.
- **The claim that AI reaches law through advocacy is withdrawn.** It is one
  of seven channels, and it is the only one with *no* verified event.
- **What stands:** no verified deployment was found in the Ministry of Justice
  commercial courts whose judgments are this corpus. Every judicial
  deployment found is in the Board of Grievances, a different judiciary whose
  judgments are not here.

---

## 1. The registry

`adoption_registry.json`, seven events, each carrying what its source
establishes and — mandatorily — what it does not.

| id | date | organisation | channel | status | linkability | vs cutoff |
|---|---|---|---|---|---|---|
| ADOPT-0001 | 2024-01 | SDAIA | government/regulatory | GOVERNANCE | L0 | before |
| ADOPT-0002 | 2024-03 | Board of Grievances + Elm | bench research | PARTNERSHIP | L1 | before |
| ADOPT-0003 | 2024 | Board of Grievances | bench research | **DEPLOYED** | L1 | before |
| ADOPT-0004 | 2025-02-04 | Ministry of Justice | enforcement | **DEPLOYED** | **L2** | after |
| ADOPT-0005 | 2026 | Board of Grievances | bench research | GOVERNANCE | L1 | after |
| ADOPT-0006 | 2026-06 | Board of Grievances + Elm | court administration | PARTNERSHIP | L0 | after |
| ADOPT-0007 | 2026-07-21 | Board of Grievances + HUMAIN | bench research | DISCUSSION | L0 | after |

Two of the seven are deployments. Two are partnerships, two are governance
documents, one is a meeting. **No event reaches L3_WORKFLOW_MATCH**, so no
before-and-after comparison in this repository can be given a causal reading,
and none is attempted.

Three entries deserve their own sentence.

**ADOPT-0003, the Board of Grievances knowledge assistant.** A system named
ALMUSAID is served from an official Board subdomain, and the knowledge
assistant placed among the top five in the Digital Government Award 2024 for
best use of emerging technologies. This is a judicial legal-research AI, in a
Saudi court, dated *before* the frozen baseline. What the sources do not
establish: how many judges use it, how often, on what, or with what effect.
The reported extension to predicting the judicial ruling comes from press
reporting, not from anything published by the Board that we could read.

**ADOPT-0004, the Virtual Enforcement Court.** The Ministry's own page says
enforcement requests run from filing to decision automatically and without
human intervention, under direct judicial supervision, and it is the one
official page in the registry we read in full. **It does not mention
artificial intelligence.** The AI enablers, automatic classification and
predictive data analysis appear in agency and press material, not in the
Ministry's description. Automation without human intervention is not evidence
of machine learning, and the registry records that distinction rather than
smoothing it. This event is L2: same ministry, different workflow, output this
corpus does not carry.

**ADOPT-0005, the Board's AI-use principles.** A binding internal document
applying to every department and to operating companies that build or run AI
systems, with compliance monitored, citing SDAIA's January 2024 principles. A
policy addressed to personnel *who use AI systems* is stronger evidence of
institutional use than any single product announcement — which is why it is in
the registry despite being, formally, only a governance document.

**On sources we could not read.** Our fetch of the SPA pages returned 403 and
the Board's English news page returned 503. Those are our access failing, not
the sources failing. The URLs and their content are recorded, `fetch_status`
says exactly what happened, and nothing is downgraded to non-existent because
a proxy refused it.

## 2. Seven channels, not one

AI does not enter law through a single door. The registry is organised by the
door.

| channel | at the 1446Q2 cutoff | now | can this corpus observe it? |
|---|---|---|---|
| BAR / ADVOCACY | NO_VERIFIED_EVENT | NO_VERIFIED_EVENT | partially — party citations, at two speaker specifications |
| BENCH / JUDICIAL RESEARCH | **DEPLOYED** | DEPLOYED | not where it happened: the Board of Grievances is not in this corpus |
| COURT ADMINISTRATION | NO_VERIFIED_EVENT | PARTNERSHIP | barely — confounded with the publisher's release policy |
| ENFORCEMENT | NO_VERIFIED_EVENT | **DEPLOYED** | no |
| GOVERNMENT / REGULATORY | GOVERNANCE | GOVERNANCE | no |
| PUBLIC LEGAL SERVICES | NO_VERIFIED_EVENT | NO_VERIFIED_EVENT | no |
| LEGAL KNOWLEDGE INFRASTRUCTURE | NO_VERIFIED_EVENT | NO_VERIFIED_EVENT | indirectly, through what is cited |

The uncomfortable diagonal: **the channel this corpus observes best is the one
with no verified event, and the channel with the earliest verified deployment
is the one this corpus cannot see at all.**

`NO_VERIFIED_EVENT` for the bar is a statement about our search, not about
Saudi legal practice. Advocates almost certainly use these tools. Nothing here
would detect it, and nothing here will guess.

## 3. Withdrawing the advocacy-first claim

`FORESIGHT.md` section R said: *"The mechanism by which legal AI is usually
expected to reshape law runs through advocacy."* That is **withdrawn** as
written. It is too narrow, and in the Saudi setting it is the wrong end of the
telescope: the first verified judicial AI deployment is in a court's own
research environment, not in a law firm's.

What survives the correction is the measurement, which was never about AI:

> Over 11 rolling quarterly folds, the court's citation shares correlate at
> 0.9625 with its own next quarter; the bar's add **-0.0107** once the court's
> prior quarter is held fixed. Of 460 articles whose first use is observed in
> both voices, **56.3 %** appear in the court's voice first.

That result now supports a narrower and more defensible claim: **PATH 1 of the
salience-feedback hypothesis — AI retrieval to advocate citation to judicial
exposure — has no observable precondition in this corpus.** It says nothing
about PATH 2 (judicial AI retrieval acting on judicial visibility directly),
which is precisely the path the registry shows exists, and which this corpus
is in the wrong institution to observe.

Five paths are now kept open, and they make opposite predictions on purpose:

| path | mechanism | this corpus can test the precondition? |
|---|---|---|
| 1 | AI retrieval → advocate citations → judicial exposure | yes — **precondition absent** |
| 2 | judicial AI retrieval → judicial source visibility directly | no — wrong institution |
| 3 | institutional knowledge system → standardised authority → concentration | no |
| 4 | AI long-tail discovery → more diverse sources | partly, through the diversity baselines |
| 5 | AI summarisation → authority compression → concentration | partly, same baselines |

## 4. AI as a subject of law: a frozen zero

Entirely separate question, entirely separate file. `ai_radar.py` scans every
judgment in the corpus for a concept inventory of nine families — explicit AI
terms, algorithmic systems, automated decisions, generated content, automated
contracting, algorithmic evidence, professional use, data protection,
generative-IP — in Arabic, and classifies each hit at one of four levels.

| level | meaning | count |
|---|---|---:|
| CONTEXT | a legally relevant field with no algorithmic system shown | 675 |
| L1 | an AI term present, in a name or a business description | 12 |
| L2 | an algorithmic system present, not shown to be at issue | 28 |
| **L3** | **the algorithmic feature is materially part of the legal question** | **0** |

**Zero, across 50,666 judgments.** That is the measurement, and it is the point
of building the radar now rather than when the first case arrives: a first
entry is only detectable against a recorded absence.

The first pass returned two L3 judgments and both were read and both were
false positives. One names the Saudi Data and AI Authority as evidence that a
trademark is well known; the other describes a device sold as AI-powered in a
sales dispute. Two exclusion rules were added — a named institution whose
title contains an AI term, and AI as an advertised attribute of goods — and
the pass was re-run. No judgment was reclassified by hand.

What the surviving L2 hits look like, in the courts' own words: an accounting
system that failed to produce records for 103 vehicles, a clinic's reception
system in a supply contract, and the Najiz platform used to schedule a
hearing. Ordinary automation, ordinary disputes.

**Recall is bounded by the inventory.** A dispute about an algorithmic system
that never names one is invisible here, so the zero is a floor. And nothing in
this file infers that any document was *written* with AI: there is no
stylometry, no detector, and there never will be.

Three watch targets are recorded in `FORECAST_LEDGER.json` against this zero —
first L3 judgment, first AI-generated-evidence issue, first verified MoJ
commercial deployment. A watch target carries **no probability** and never
enters a skill statistic. Forcing a probability onto a rare emerging event
would be false precision, and the escalation rule is written out: one L3
judgment is an occurrence; three in a year, or two under one code, is a family
and earns its own measurement.

## 5. The retrieval correction

`FORESIGHT.md` named `retrieval_coverage_h1@1446Q2` as the prediction most
worth staking the repository on, and glossed it as: build a Saudi legal
retrieval universe from what the *whole judgment* cites. **That gloss is
withdrawn.** The forecast is not voided — its definition was valid and
scoreable before any outcome, and voiding a forecast because its reading was
wrong is exactly the move the ledger forbids. It is REFRAMED, and the question
the gloss should have asked is now its own forecast.

Coverage is **recall**. The speaker programme spent this entire project
establishing that a whole judgment carries substantial advocacy and recital
material, so recall bought from the whole document is recall bought with
contamination. Pricing it:

| | |
|---|---:|
| the party-only remainder grows the court's universe by | **40.6 %** |
| coverage it adds | **0.0064** |
| coverage points per 10 % of universe growth | 0.157 |
| share of that remainder the court ever cites | **0.0956** |
| folds | 13 |

Two fifths more index, under a point of recall, and nine tenths of the
addition is never cited by a court. Verdict:
**HIGH_RECALL_COSTS_MORE_THAN_IT_BUYS.** The architecture worth testing next
is not whole-judgment and not court-only, but high-recall candidate discovery
carrying **speaker provenance**, ranked by court attestation — which is a
coverage experiment, not a product, and is written into the ledger as
`speaker_aware_retrieval@1446Q2`.

## 6. Temporal misalignment: recall ages slowly, ranking ages fast

Recall decay asks what a frozen snapshot still contains. Staleness asks what
it gets *wrong*.

| horizon | citations to articles never seen | top-50 displaced | mean rank displacement, top 200 | top-10 held |
|---|---:|---:|---:|---:|
| 1 quarter | 0.0437 | **34.9231 %** | 33.1885 | 6.9231 of 10 |
| 2 quarters | 0.0612 | 39.1667 % | 36.3225 | 6.25 of 10 |
| 4 quarters | 0.1191 | **46.4 %** | 40.513 | 5.1 of 10 |

A Saudi legal AI frozen for a single quarter still contains almost everything
it needs and already orders **a third of its operational core wrongly**. After
a year it is missing one citation in eight and has half its core out of place.
Displacement runs about eight times the missing-content rate at h = 1 and four
times at h = 4. **The staleness that matters is not coverage. It is ranking.**

The doctrinal companion set barely ages at all — 0.0271 of a period's mentions
are identities the previous period's set did not carry — and that is a fact
about a 28-identity extractor, not about doctrine.

**Article-version supersession: NOT_AVAILABLE.** The corpus registry carries
publication dates per *instrument*, not per article version, and only two of
its tracks carry a parseable hijri publication year, so even the
instrument-level check is reported as INSUFFICIENT_REGISTRY_COVERAGE rather
than as a zero. Whether the text of an article at the time of a 1443 judgment
differs from its text today cannot be answered from the metadata held, and
this session does not reconstruct it.

## 7. Forecast-calibration backfill

The identity layer was extended to 1442–1443 for one stated purpose: fold
count. 2,318 additional mentions, written to a **separate file** so that
`DOCTRINE.md` still reads exactly the 1444–1446 window it was computed on, and
only the forecasting code merges the two. No historical claim is made across
it and no change is narrated.

| code | steps before | steps after | mean top-3 Jaccard | same set | top-1 held |
|---|---:|---:|---:|---:|---:|
| Commercial Courts Law | 9 | **11** | 0.8636 | 72.7 % | 63.6 % |
| CCIR | 9 | **10** | 0.8 | 60.0 % | 50.0 % |
| Evidence Law | 8 | 8 | 0.625 | 25.0 % | 50.0 % |
| Sharia Procedure Law | 4 | 4 | 1.0 | 100.0 % | 25.0 % |

The verdict does not move: **the top-3 companion set persists; its order does
not.** More folds made it steadier, not different. The backfill stops here:
its targets have enough folds, and further extension would be historical
scholarship, which is not what it was authorised for.

## 7b. The frozen baseline was not touched

`freeze_baseline.py --check` now compares provenance as well as numbers, and
it reports exactly two changes since the baseline was frozen: the code hashes
of `companions.py` and `foresight.py`, both extended in this session. **All
129 numeric fields are unchanged.** The frozen file is not rewritten and not
re-frozen; the drift is reported and left visible, which is what a freeze is
for. Anyone comparing a future reading against it is comparing against the
same numbers, produced by code that has since grown a backfill flag and four
new measurements.

## 8. The transition map

`ai_transition_map.json` links each verified event through to what, if
anything, this repository could ever measure about it:

> VERIFIED EVENT → CHANNEL → WORKFLOW → OBSERVABLES THAT COULD MOVE →
> AVAILABLE DATA → LINKABILITY → FROZEN BASELINE → FORECAST OR WATCH TARGET →
> FUTURE SCORE

Its most important column is the one that says **NO**. Of seven events, three
are L0 with no observable outcome, three are L1 with outcomes only outside
this corpus, one is L2 with the right institution and the wrong workflow, and
none is L3. The map's function today is to stop a future session from running
an event study it is not entitled to run.

## What can and cannot be linked today

**Can be:** chronology. Which system entered which institution, when, through
which channel, with what the official source actually says. And the
before/after position of the baseline: three events precede it.

**Cannot be:** anything causal. Not one event sits in the workflow this corpus
observes. The Board of Grievances deployment is in the administrative
judiciary; the Ministry's deployment is in enforcement; the corpus is
published commercial adjudication. An event study on any of them would be an
event study on the wrong output.

## Standing limitations

- The registry is a bounded search run once, not a maintained news archive.
  Absence from it means we did not verify something, never that it does not
  exist.
- Two official sources could not be fetched by us (403, 503) and are recorded
  as such, with their claims marked accordingly.
- The AI radar's recall is bounded by its concept inventory; the zero is a
  floor.
- Nothing here attributes AI use to any judgment, any judge, any lawyer, or
  any document. That prohibition is structural, not a matter of current
  caution.
