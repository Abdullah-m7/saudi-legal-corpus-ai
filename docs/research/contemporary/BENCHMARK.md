# Legal-AI benchmark from this asset: feasibility

**Verdict: PILOT for two tasks, HOLD for two.**

The question is whether the validated subset can support a benchmark that
measures whether a legal AI system distinguishes advocacy from adjudication.
It is asked now because the answer decides whether the annotation effort
already spent has a second use.

## What exists to build from

| source | items | what is validated |
|---|---:|---|
| `gate.json` + `gate_labels.json` | 155 | speaker role (48), the five contrasted type/voice cells (80), three rule families (27) |
| `gold_47.json` | 206 | authority type on 126 rule hits; 80 random reasoning sentences |
| `gold.json` (seed 23) | 206 | **burned** — drove the repairs, cannot score a model either |
| `gstc_pilot/moj_article_gold.json` | 178 rows over 32 whole judgments | article-level citation gold, hand-read end to end |

## Task by task

**T1 · Speaker attribution — PILOT.** Given a passage from a judgment,
is it the court's reasoning or a party's argument? Labels are stable where it
matters: the gate measured the court bucket at 12/12 and the strict party
bucket at 10/12 by hand. Definitions are crisp because they are structural.
**Ceiling is known and low-ish**: the facts segment was 7/12, so a benchmark
must either exclude the ambiguous middle or report per-bucket accuracy. 48
gate items is a pilot, not a benchmark.

**T2 · Authority-type classification — PILOT.** Given a sentence, which of
nine authority types does it invoke, if any? 126 validated items at 126/126,
plus 80 random sentences that establish the negative class. The nine-way
taxonomy is documented with a rule id and an attested example per rule, which
is what makes the labels auditable rather than merely asserted.

**T3 · Statutory article identification — HOLD.** The article-level gold
exists and is good, but the *system under test* would be scored against a
pipeline that is itself blind to six citation forms
(`gstc_pilot/citation_forms.py`). Benchmarking a model against a known-partial
oracle rewards reproducing its blind spots. Hold until either the forms are
repaired or the gold is extended to include them explicitly as items the
oracle misses.

**T4 · Advocacy-versus-adjudication on retrieval — HOLD.** The interesting
version of this task — "given a legal question, retrieve the authority a court
would actually apply" — needs a query set with adjudicated answers. Nothing
here supplies queries, and inventing them would make the benchmark measure our
imagination.

## Reuse and privacy

The judgments are published by the Ministry of Justice, already redacted by
the publisher, and further masked here. The derived layers carry **no text at
all** — counts, ids and labels only. A pilot benchmark would need to ship
short passages, which is a different disclosure decision from anything this
repository has made so far and is not made unilaterally.

## Pilot spec, if it goes ahead

```
name      SAAB-pilot  (Speaker-Aware Authority Benchmark)
tasks     T1 speaker role (2-way, court reasoning vs party argument)
          T2 authority type (9-way + none)
items     T1: 24 (12 court, 12 party) from gate arm 2
          T2: 126 from gold_47 + 80 negatives from its recall half
metric    macro-F1; per-bucket accuracy reported separately for T1
baseline  authority.py itself, which by construction scores near ceiling and
          is included as a rule-based reference rather than a competitor
caveat    a pilot at this size resolves gross failure, not ranking
```

**Recommendation: build T1 and T2 as a pilot only when a use for it appears.**
Building it now would be infrastructure ahead of a question.
