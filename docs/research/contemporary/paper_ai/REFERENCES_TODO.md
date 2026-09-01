# Novelty audit and reference plan

This file replaces the placeholder list that shipped with the first draft. It
records a literature audit run on 1 September 2026, its method, its limits,
and — the part that matters — which of the manuscript's claims it **kills**.

## How the audit was run, and what it is worth

Search-engine queries were issued for each of eight topics: text and data
deduplication for language models; matched-size random ablation controls;
boilerplate-removal controls; legal corpus deduplication; legal retrieval
corpus contamination; temporal retrieval drift; temporal legal RAG; retrieval
benchmark ageing. Two further topics were added while auditing: Arabic and
Saudi legal NLP corpora, and citation-context retrieval.

**Reading status is recorded per item and almost all of it is `ABSTRACT` or
`SNIPPET`.** Nothing below has been read in full. That is a limit on the
audit, not a formality: a claim of non-novelty made from an abstract is
weaker than one made from a method section, and every item marked below must
be read before it is cited or relied on.

The prior on which the audit was run, as instructed: *deduplication matters*,
*repeated text biases data*, *temporal retrieval drift exists*, and
*matched-size random ablation as a general idea* are all assumed **not novel**
unless the literature fails to show them. The audit did not fail to show them.

## Verdicts on the manuscript's novelty claims

### 1 · "A size-matched random-removal control for deduplication is not standard" — **WITHDRAWN**

The general idea is established outside law. Matched-count random-subset
controls are routine in the data-selection and quality-filtering literature:
a curated subset is compared against a random subset **of the same size**
drawn from the same pool, precisely so that quality is separated from
quantity. DataComp-LM's benchmark design and the pointwise-V-information data
reduction work both use random-selection baselines at matched budget, and the
pattern is described generically as a controlled ablation.

The draft's sentence *"We are not aware of it being standard"* is false as
written and must be deleted. §5.4's framing as a proposal must go with it.

### 2 · "The four assumptions are never jointly tested" — **WITHDRAWN**

No evidence was found that they are jointly tested, but absence of evidence
from a search-engine audit is not a finding, and "never" is not defensible
from ten queries. The sentence must be reduced to a description of what this
paper does rather than a claim about what the field has not done.

### 3 · "Comparing index architectures on drift rather than point-in-time coverage" — **REFRAMED**

Temporal retrieval evaluation is an active area with its own venue-scale
infrastructure (CLEF LongEval; FreshStack and its re-judged snapshots), and
temporal validity is already a named problem in legal RAG specifically. Drift
as an evaluation axis is not new. What the audit did **not** find is a
temporal-ageing evaluation that controls for the index shrinking as it is
frozen. LongEval-style designs use cumulative filtering; the freshness work
compares snapshots. Neither reports a matched-volume control for the age
effect itself.

That is the narrow form of the claim and the one §6 may make:

> An index-age effect measured by freezing a corpus is confounded with the
> index being smaller. We report the age effect beside a random removal of
> the same number of contexts, so the two can be told apart.

Still to check by the author, in full text, before this is claimed: the CLEF
LongEval overview papers, which are the most likely place for this control to
already exist.

### 4 · The retrieval task itself — **NOT NOVEL, and it does not need to be**

Retrieving a cited authority from the citation's own local context is an
established task (Huang et al., *Context-Aware Legal Citation Recommendation*,
2021 — case citations, BVA). A fenced, temporally-controlled variant exists
for case law across two jurisdictions. For this jurisdiction specifically,
ALARB (ArabicNLP 2025) already defines *identification of relevant
regulations* over 13K Saudi commercial cases.

The manuscript must therefore present its task as an **instrument**, not as a
contribution: it is a standard task, run four ways, because a standard task
is what makes the four corpus treatments comparable.

## What survives

Exactly one methodological claim and two empirical ones.

**M1 — a domain-specific validity requirement.** *When a preprocessing
intervention removes a substantial share of the evidentiary volume of a legal
corpus, its effect on legal-AI evaluation should be compared against a
matched-volume random-removal control before the change is attributed to the
semantic class removed.* This is the general control, imported and made a
requirement for a domain where the removed material is evidence rather than
noise. The contribution is the requirement and the demonstration, not the
control.

**E1 — the measured result.** On a real legal retrieval task over 105,575
resolved statutory citations, targeted removal of recurring legal wording
does not move retrieval outside the spread of size-matched random removals.
This is a fact about a corpus, obtained with a stated control, and it is the
paper's strongest sentence because nothing in the literature above predicts
it either way.

**E2 — ageing decomposed.** The cost of index age, reported beside the cost
of the index being smaller by the same amount.

Everything else in the draft is a measurement of this corpus and is presented
as such.

## Closest prior work — read these first

| # | Work | Why it matters here | Reading status |
|---|---|---|---|
| P1 | Lee et al., *Deduplicating Training Data Makes Language Models Better*, ACL 2022 | The canonical deduplication result. §1 and §4 must cite it as the practice they are testing, not as an opponent | ABSTRACT |
| P2 | *On the Effect of (Near) Duplicate Subwords in Language Modelling*, 2024 | Reports that removing near-duplicates **hurts**, at a cost quantified as equivalent to training on 5–10 % less data. The closest published thing to this paper's argument, in a different modality. Must be read in full before §5 is written | ABSTRACT |
| P3 | Li et al., *DataComp-LM*, NeurIPS D&B 2024 | Random-selection baselines at matched budget; the reason claim 1 is withdrawn | SNIPPET |
| P4 | Huang, Low, Teng, Zhang, Ho, Krass, Grabmair, *Context-Aware Legal Citation Recommendation using Deep Learning*, 2021 | The task's direct ancestor. Note for the author: its last author is the editor who desk-rejected paper A, which is a reason to position against it carefully and accurately, and no reason to do anything else | ABSTRACT |
| P5 | *Fenced Citation-Context Retrieval for Case Law: Temporal Leakage and Degree Control Across Two Jurisdictions*, 2026 | Temporal fencing for exactly this task family; the leakage vocabulary in §6 should be aligned with it | SNIPPET |
| P6 | CLEF **LongEval** lab and its overview papers | The standing infrastructure for temporal persistence of retrieval systems. The single most likely place for E2 to already exist | NOT READ |
| P7 | Kuissi, Subrahmanyan, Thakur, Lin, *Still Fresh? Evaluating Temporal Drift in Retrieval Benchmarks*, 2026 | Snapshot-based drift measurement; finds benchmarks largely survive re-judging. A useful contrast to a corpus where ranking turns over a third per quarter | SNIPPET |
| P8 | *Temporal Misgrounding in Legal RAG: A Versioned-Corpus Benchmark for French Tax Law*, 2026 | Temporal validity as a legal-domain problem with a versioned corpus. The nearest legal neighbour to §6 | SNIPPET |
| P9 | ALARB, *An Arabic Legal Argument Reasoning Benchmark*, ArabicNLP 2025 | 13K Saudi commercial cases with cited clauses and a regulation-identification task. Kills any claim that this corpus family is unexplored, and is the natural comparison point for the task | ABSTRACT |
| P10 | ArabiCCR, *A commercial Arabic ruling court cases dataset* | A published dataset from the same Ministry of Justice source. §3 must acknowledge it | SNIPPET |
| P11 | Bevendorff et al. line of work on boilerplate removal evaluated **extrinsically** on ad hoc retrieval | The precedent for judging a cleaning step by a downstream task rather than intrinsically. §5's design is in this tradition and should say so | SNIPPET |
| P12 | *Legal Case Retrieval: A Survey of the State of the Art*, ACL 2024 | Positioning for §2 | SNIPPET |
| P13 | Data-contamination surveys, and *Search-Time Data Contamination*, 2025 | Where the verbatim-overlap control in §6 belongs in the wider vocabulary | SNIPPET |

## Method citations still needed

| Where | What |
|---|---|
| §4.1 | Banded minhash over shingles — the near-duplicate method built and set aside |
| §6 | BM25 and its parameterisation |
| §7 | CUSUM, Page-Hinkley, and permutation calibration of a detection statistic |

## Legal sources — verified, citation form only

Quoted from instruments held locally, recorded in `ai_law_map.json` with the
full Arabic text.

- اللائحة التنفيذية لنظام المحاكم التجارية، المادة الرابعة والعشرون (`ANCH-CCL-REG-24`)
- الأدلة الإجرائية لنظام الإثبات، المادة الثالثة والعشرون (`ANCH-EVID-PROC-23`)
- لائحة مقدمي خدمات التنفيذ، المادة السادسة عشرة (`ANCH-ENF-PROV-16`)
- اللائحة التنفيذية لنظام التوثيق، المادة العشرون (`ANCH-TAWTHEEQ-REG-20`)

Decisions needed: transliteration scheme; whether to give an English rendering
beside the Arabic; whether to cite the gazette issue.

## Self-citation

The companion paper on speaker attribution (`../paper/MANUSCRIPT.md`) is where
the court/party voice separation comes from. Cite it if it is posted or under
review when this is submitted; otherwise describe the method inline rather
than cite an unavailable draft.

## Rules that still hold

- Every entry must be read before it is cited. A plausible title, a
  remembered DOI, or a reference carried over from another paper's
  bibliography is not a reference.
- Nothing generated is cited.
- No Saudi legal source is quoted unless the text is held locally.
- If reading P2 or P6 in full overturns what is written above, the manuscript
  changes, not the audit.
