# Update contract: what has to happen when new judgments arrive

Not a scheduler, not a service, not a dashboard. A contract: the ordered
stages a new batch must pass, and the delta report a release must produce. It
exists so the map can be refreshed rather than frozen, and so the refresh
cannot quietly skip a gate.

## Stages, in order, each with a refusal condition

| # | stage | refuses when |
|---|---|---|
| 1 | **provenance** | the batch does not record publisher, retrieval route and date; or the route is one `robots.txt` disallows |
| 2 | **privacy gate** | a record carries an identifier the publisher's own redaction missed — the mask list in `gstc_pilot/splits.py` runs first, and a new identifier shape means stop and extend it, not proceed |
| 3 | **parse** | `freeze.py --check` reports the parser has moved since the release being compared against. A delta computed across two parser versions is not a delta |
| 4 | **speaker / authority layer** | `layer.py` emits fewer mentions per judgment than the previous release by more than a stated tolerance — that is an extraction regression, not a change in law |
| 5 | **views** | `views.py all` fails, or `core_view.json` loses an article that carried more than 1 % in the previous release without a reason |
| 6 | **delta report** | — always produced; see below |

## The question a release must answer

> **What changed in Saudi adjudicatory reasoning since the previous release?**

Six measured deltas, all computable from two `authority_mentions.jsonl.gz`
files and nothing else:

1. **new articles entering the top 50** of the operational core, with the rank
   they entered at
2. **rank changes** for articles already in it, and departures
3. **authority-mix change** — the nine type shares, court voice, with the
   previous release's value beside each
4. **hybrid-rate change** — the four reasoning shapes, per year, and for
   each authority type the **prevalence** (judgments invoking it at all)
   and the **intensity** (invocations per invoking judgment) *separately*
   from its share of mentions. Reported as a share alone, the bench's
   fiqh citations fall from 22.7 per cent in 1441 to 10.0 in 1446 and
   look like displacement; prevalence is flat and intensity does not move
   past the second decimal. A release that reported only the share would
   announce the disappearance of fiqh from Saudi commercial reasoning
5. **newly visible statutes** — an instrument cited by the bench in this
   release and not the last, which is how a new code announces itself
6. **source-composition change** — judgments per year, share carrying reasons,
   court mix. This one is printed *first*, because every other delta is
   conditional on it and a change here can produce all five of the others
   without any change in adjudication

## Why composition is printed first

The corpus this repository holds moved from 2 per cent of judgments carrying
reasons to 88 per cent in four years. Any release that compared authority
mixes across that boundary without printing it would have reported a
revolution in judicial reasoning that was a change in publication practice.
The delta report puts the selection control at the top for that reason.

## Not built, and deliberately

No scheduler, no service, no web front end. The contract is the durable part;
a cron line is not. When a batch actually arrives, `layer.py` and `views.py`
run in minutes and the delta is a diff of two JSON files.
