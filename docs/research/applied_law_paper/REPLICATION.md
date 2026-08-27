# Replication package

Every measurement in *98 Per Cent of the Procedure, 26 Per Cent of the Code*
is computed from the two corpora in this repository by the scripts listed
below, written into JSON, and typeset into the manuscript from a generated
file of macros. Nothing in the manuscript is typed by hand, and
`check_numbers.py` refuses to build a manuscript that types a measurement
anyway.

```bash
docs/research/applied_law_paper/reproduce.sh
```

About ninety seconds on one core, measured on Python 3.11.15 with the corpus
on local disk; most of it is the scripts that scan the full judgment corpus.
No third-party packages. A LaTeX installation is needed only for the final
two lines.

## The data

| | |
|---|---|
| `data/corpus_registry/corpus_registry.json` | the legislative registry: 291 instruments, their titles, article counts and verified article records |
| `docs/research/arabic_paper/judgments/*.jsonl` | 50,666 judgments in full text, one JSON object per line, 507 shards |

Both are in the repository. Neither is redistributed from a third party: the
legislation is published by the Saudi government and the judgments by the
Ministry of Justice through the interface its own portal uses, and each
record carries its provenance — source class, retrieval route, corroboration,
transformation, and any discrepancy — in a `provenance` field. Party names
arrive already masked as `(...)` by the publisher; a further pass over
identifiers the publisher's masking missed is in
`docs/research/arabic_paper/redact.py` and documented there.

Collection is reproducible but not part of `reproduce.sh`, because it takes
about fourteen hours and hits a public server 50,666 times:
`docs/research/arabic_paper/collect_all_judgments.py --stage index`, then
`--stage text`.

## The code

Shared modules, in `docs/research/arabic_paper/`:

| | |
|---|---|
| `match_instruments.py` | a citation's instrument name → a registry instrument, with title variants, containment by direction, and anaphora resolved by kind |
| `arabic_ordinals.py` | `المادة الخامسة والتسعون بعد المائة` → 195, with paragraphs |
| `voice_attribution.py` | segments a record document by document, and reads who is speaking inside the statement of the case |

Analyses, each writing one JSON file beside itself:

| script | what it measures |
|---|---|
| `corpus_composition.py` | courts, cities, years, duplicate texts, the appeal-flag audit |
| `applied_law_v2.py` | citations matched to instruments; named against anaphoric |
| `applied_articles.py` | citations matched to articles; parse and range losses |
| `restricted_denominator.py` | article coverage under four denominators |
| `cite_by_voice.py` | citations by segment, and the attribution split inside the recital |
| `churn_vs_litigation.py` | amendment against citation, pooled and within instrument |
| `dedup_robustness.py` | the headline shares recomputed over distinct texts only |
| `unparsed_by_year.py` | whether the parse loss is concentrated in any period |

## From a number in the manuscript to the code that produced it

Every macro in `numbers.tex` is assembled by `make_numbers.py`, which reads
only the JSON files above. To trace a figure: find its macro in the LaTeX
source, then find that macro in `make_numbers.py`, which names the results
file and the field. For example `\nCivilShare` — the 25.8 per cent — is
`restricted_denominator_results.json → instruments → civil_transactions_law`,
written by `restricted_denominator.py`.

The manuscript's tables map as follows.

| | |
|---|---|
| Table 1, citations by segment | `cite_by_voice.py` |
| Table 2, four denominators | `restricted_denominator.py` |
| §5.4, the within-instrument sign test | `churn_vs_litigation.py` |
| §6, the duplication check | `dedup_robustness.py` |
| §6, the appeal-flag audit | `corpus_composition.py` |

## What a re-run will and will not reproduce

Bit-for-bit, from the deposited data: every number in the manuscript. The
scripts are deterministic and take no random seed.

Not reproducible from a fresh collection: the judgment corpus is a snapshot.
The Ministry adds judgments, and the portal's pagination was unstable enough
during collection that the sweep had to run until two consecutive passes
returned nothing new. A collection run today will hold more judgments than
this one and will not reproduce these counts. That is a property of the
source, not of the code, and it is why the corpus is deposited rather than
merely described.

## Provenance of the corrections

Three claims made by earlier drafts were withdrawn after measurement
contradicted them, and one segmentation defect was found and fixed. The
history is in the repository's commits rather than smoothed out of it, and
the scripts carry the reasons in their docstrings.
