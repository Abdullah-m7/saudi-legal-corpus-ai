# The second corpus we did not build, and why that is the finding

The programme reached a genuine impasse and it is worth stating plainly before
anything else. The first verified Saudi judicial AI deployment is in the Board
of Grievances. This repository's corpus is Ministry of Justice commercial
judgments. To measure whether reasoning changed around that deployment, the
Board's judgments would have to be here.

They are not, and after a bounded official-access audit they are not going to
be — for two reasons that are independent of each other, and the second is the
one that matters.

**Verdict: ACCESS_BLOCKED. Event class: E0_CHRONOLOGY_ONLY.**

No document was downloaded. No route was probed beyond a plain GET of pages
that appeared in official material or search results. Nothing was
circumvented.

---

## 1. The access audit

`bog_access_audit.json` records ten routes with a verdict each. Every Board of
Grievances route returns 503 or a reset connection from this environment —
including `robots.txt` itself.

That last point settles the question on its own. **The crawl policy could not
be read, so no crawl is permissible.** An unreadable robots.txt is treated as
a prohibition, not as silence, and certainly not as permission. A
search-engine summary of a page is not a substitute for the publisher's own
terms, and it was not used as one.

For contrast, `sjp.moj.gov.sa` — the source of the existing corpus — answers
normally from the same environment. The failures are specific to the Board's
hosts, not a network outage, and they are recorded as **our** access failing.
Nothing here concludes that the Board forbids research use; only that we
cannot establish that it permits it, which is the same practical answer and a
different factual one.

Two routes were explicitly ruled out rather than merely blocked. `almusaid.
bog.gov.sa` returns a title and then authentication: it is an internal
judicial system and is not a research route under any reading. And the
national platform lists *viewing the judicial codices* as a **service** —
digital viewing plus a printed copy on request — which is not a bulk data
route and was not treated as one.

## 2. The blocker that survives any access fix

Suppose the network problem vanished tomorrow and the publisher granted
everything. The design would still fail.

The most recent Board of Grievances judgment collection reported by official
and press sources is the **collection of administrative judgments for 1444
AH**, announced in 2024 and still described as the latest issue in July 2025.
The verified AI events are the Elm agreement of **March 2024** and the
knowledge assistant deployed and recognised **during 2024** — that is, 1445 to
1446 AH.

> **The published Board corpus ends before the deployment begins. There are
> zero post-deployment judgments to observe.**

A pre/post design needs a post. There is none, and no amount of access
produces one. This is why the session stops here rather than fighting the
network: the network was never the binding constraint.

A third problem waits behind those two, and it is worth recording because it
would have shaped the design anyway. The Board publishes **curated
collections** — principles decided by the Supreme Administrative Court, and
selected administrative judgments. A curated collection is not a census, and a
principle is an editorial abstraction of a judgment. A change in what the
publisher selects would look exactly like a change in how judges reason.

## 3. What this makes the study

The ladder, evaluated rather than asserted, in
`ai_exposure_matrix_results.json`:

| level | requirement | met? |
|---|---|---|
| E0 CHRONOLOGY_ONLY | a verified, dated event | **yes** |
| E1 OBSERVABLE_POST_SHIFT | an outcome series for the exposed population, covering periods after the event | no |
| E2 VALID_INTERRUPTED_SERIES | enough complete pre and post periods, with placebo dates | not evaluated |
| E3 COMPARISON_SUPPORTED | a comparison series with comparable pre-trends | not evaluated |
| E4 QUASI_EXPERIMENTAL | official evidence of variation in timing or intensity | not evaluated |
| E5 CAUSAL_IDENTIFICATION_STRONG | identification surviving the obvious confounds | not evaluated |

**E1 fails, so E2 to E5 are not evaluated on their merits and are not
claimed.** Levels are not skipped, and no AI-impact manuscript is created:
the paper policy requires at least E2.

The exposed population is Board judges and researchers. What no source we
could read establishes: how many used the system, how often, in which courts,
and whether use was optional or integrated into the workflow. Exposure is
institution-level and is labelled that way.

## 4. What was built instead

The impasse is not the end of the work; it changes what the work is. Four
things now exist that did not.

**An exposure matrix** (`ai_exposure_matrix_results.json`), one row per
verified event, carried through institution, workflow, exposed population,
observable outcomes, corpus availability, linkability, baseline, forecast and
feasibility. Event studies feasible today: **0 of 7**. Its function is to stop
a future session running a study it is not entitled to run.

**Channel-specific forecasts.** All seven issued forecasts now carry a
channel, a workflow, an observable and a linkability level. The rule is
enforced in the matrix: *an outcome may be read as possibly AI-related only if
the deployment is in its channel.* A deployment in enforcement never explains
a movement in bench citation behaviour. Four of the seven are tagged
`NOT_AN_AI_TARGET` outright.

**A dormant preregistration** (`FORECAST_LEDGER.json`, `preregistrations`),
frozen before any data exists — which is the strongest form of
preregistration available, since there is nothing to have peeked at. It fixes
nine primary outcomes, the outcomes deliberately excluded, four competing
hypotheses with opposite predicted signs, the segmented-series specification,
three event windows, placebo dates from every pre-period quarter, the
confounds to check first, and the reporting rule: with no credible
counterfactual the language is POST-DEPLOYMENT SHIFT or EVENT-ALIGNED CHANGE,
never causal effect. Its trigger conditions are written out. It activates
itself or not.

**A publication-regime profile**, and this one bites now rather than later.

## 5. The confound that would have bitten first

Before any doctrinal outcome, the published set itself has to hold still. Over
14 quarters of the existing Ministry of Justice corpus:

| | first quarter | last quarter | range | largest quarter-on-quarter move |
|---|---:|---:|---:|---:|
| median reasons length | 1143 | 1687 | 1143–1687 | 214 |
| fees claims | 0.3365 | 0.192 | 0.1522–0.3365 | 0.1843 |
| damages claims | 0.25 | 0.4241 | 0.163–0.4309 | 0.087 |
| proof disputes | 0.274 | 0.3371 | 0.1531–0.3869 | 0.1132 |

**The published set is not compositionally stable.** Median reasons length
rises by nearly half across the window and the claim mix inverts between fees
and damages. Any event-aligned comparison in this corpus would be fighting
that before it got anywhere near doctrine — which is why it is reported here,
first, rather than beside a doctrinal result later.

And the measure that would separate reasoning from publication cannot be
built: **decision-to-publication lag is NOT_AVAILABLE.** The corpus carries a
decision date and our own retrieval timestamp. No publication date is held for
any judgment, in either institution, and it is not approximated from the
retrieval date.

## 6. The AI legal-issue radar, on the corpus we have

Unchanged and re-run: **0 judgments at L3** across 50,666. Administrative law
is where AI as a subject of law would plausibly appear first — automated
government decisions, public-sector algorithms, procurement, automated
eligibility, administrative sanctions. The radar would run on it unchanged.
There is no corpus to run it on, and that is recorded as `NOT_SCANNED` rather
than as zero.

## 7. What would change the verdict

- A Board collection covering **1445 AH or later**. This is the one that
  matters, and it is cheap to re-check.
- A permitted machine-readable route, or a publisher licence.
- Official evidence of **phased** deployment across courts or chambers, which
  would open E4 rather than E2 — a stronger design than the one we were
  reaching for.
- A verified AI deployment inside the Ministry of Justice **commercial**
  courts, which would raise an event to L3 in a corpus this repository already
  holds. This is recorded as a watch target.

## 8. On asking

A permission request is recorded as an option and **was not sent**. It would
ask for a research licence to the published collections from 1443 onward in
machine-readable form. It is worth noting that it would not rescue the design
on its own: it supplies the pre-period, and the missing half is the post.

---

## The honest answer to the question that was asked

> Can this repository move from documenting that judicial AI was deployed to
> measuring whether the observable legal reasoning around that deployment
> changed?

**Not yet, and not for want of method.** The instrument is built — outcomes,
hypotheses, specification, placebos, comparison-series labelling, confound
checks, and a preregistration that cannot have been fitted to a result because
no result exists. What is missing is the observation: the institution that
deployed the AI has not published a judgment since it did.

That is a real finding about the state of Saudi legal-AI research, not a
failure of this session. **The first verified judicial AI deployment in Saudi
Arabia is currently unobservable in its effects, by anyone, because the
deploying institution's published record stops before the deployment.** Any
paper claiming to measure the impact of that deployment on published
administrative reasoning would, today, be measuring something else.
