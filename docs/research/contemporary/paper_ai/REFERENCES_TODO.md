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

**Reading status is recorded per item.** The 1 September controller pass has
now read the full published text of the two references that were explicitly
load-bearing for the manuscript's remaining claims: Schäfer et al. (P2) and
the CLEF 2024 LongEval extended overview (P6). It also read the retrieval-
evaluation section of Web2Text, the closest boilerplate-to-IR predecessor.
Items still marked `ABSTRACT` or `SNIPPET` must not carry a novelty claim
until their relevant method/result sections are verified.

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

**Full-text check completed 1 September 2026.** LongEval 2024 evaluates one
retrieval system across genuinely evolving collections and reports NDCG/MAP
change between Lag6 and Lag8. The published corpora are materially different
in size (about 1.79M versus 2.53M documents) and composition; the paper reports
the temporal drop directly. No same-size, random-removal, or corpus-volume
control for that retrieval-age effect appears in the published Task-1 method.
This keeps E2 alive as a narrower *decomposition used here*, not as a claim
that temporal persistence itself is new.

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

One methodological recommendation and two empirical contributions survive. The paper must not sell M1 alone as the novelty; E1 and E2 carry the scientific contribution.

**M1 — a domain-specific validity recommendation, not a standalone novelty
claim.** *When a preprocessing intervention removes a substantial share of
the evidentiary volume of a legal corpus, its effect on legal-AI evaluation
should be compared against a matched-volume random-removal control before the
change is attributed to the semantic class removed.* Full reading of Schäfer
et al. makes the boundary stricter: deduplication research already calibrates
an intervention's performance cost against reduced data quantity. What is
newly tested here is the legal-retrieval instantiation and its measured
magnitude, not the abstract principle that quantity can confound a cleaning
effect.

**E1 — the measured result.** On a real legal retrieval task over 105,575
resolved statutory citations, targeted removal of recurring legal wording
costs **0.0241 MRR@10**, versus **0.0089** for the mean same-volume random
removal: **2.7×** the volume-only cost. In the five largest-removal folds the
targeted result lies outside all 20 matched-random draws. This is a corpus-
and task-specific empirical result; it is not a claim that targeted cleaning
is generally harmful.

**E2 — ageing decomposed.** The cost of index age, reported beside the cost
of the index being smaller by the same amount.

Everything else in the draft is a measurement of this corpus and is presented
as such.

## Closest prior work — read these first

| # | Work | Why it matters here | Reading status |
|---|---|---|---|
| P1 | Lee et al., *Deduplicating Training Data Makes Language Models Better*, ACL 2022, DOI 10.18653/v1/2022.acl-long.577 | **FULL READ.** Establishes scalable exact/approximate deduplication, memorisation and train-test-overlap effects. It is the canonical positive case for deduplication and is cited as prior practice, not as an opponent. | FULL |
| P2 | Schäfer et al., *On the Effect of (Near) Duplicate Subwords in Language Modelling*, Findings ACL 2024, DOI 10.18653/v1/2024.findings-acl.571 | **FULL READ.** Natural near-duplicate merging hurts LM performance; the authors quantify the loss as equivalent to roughly 5–10% less training data and explicitly report 95%/90%-data baselines. This is closer than the first audit admitted: quantity calibration around a deduplication intervention already exists. Our matched-random retrieval control is therefore an application/extension, not a methodological first. | FULL |
| P3 | Li et al., *DataComp-LM: In search of the next generation of training sets for language models*, NeurIPS D&B 2024, DOI 10.52202/079017-0455 | **RELEVANT SECTIONS READ.** DCLM fixes model/training budgets while varying data; its deduplication ablations apply different pipelines to a 76B-token pool and then subsample each resulting pool to the same 28B-token training budget at 1B-1x (and similarly to fixed 138B-token training at 7B-1x). It is strong prior art for separating curation from training quantity/compute, although it is not the same context-count random-removal estimand used here. | FULL-RELEVANT-SECTIONS |
| P4 | Huang, Low, Teng, Zhang, Ho, Krass, Grabmair, *Context-Aware Legal Citation Recommendation using Deep Learning*, ICAIL 2021, DOI 10.1145/3462757.3466066 | **FULL READ.** Direct ancestor for local-context citation recommendation; compares collaborative filtering, text similarity, BiLSTM and RoBERTa and analyzes temporal/citation-class stability. Our retrieval task is therefore an instrument, not a novelty claim. | FULL |
| P5 | Liu, Tan & Liu, *Fenced Citation-Context Retrieval for Case Law: Temporal Leakage and Degree Control Across Two Jurisdictions*, arXiv:2607.17142 (2026) | **FULL ARXIV TEXT READ.** This is direct prior art for temporally fenced legal citation-context retrieval and, more importantly, for decomposing an observed retrieval gain into future-evidence leakage, legitimate admission cost and an index effect. It explicitly says the controlled-decomposition move is not first and cites Ovcharov. Our temporal section must not claim first decomposition; its contribution is the age-versus-same-volume measurement on a different legal retrieval object. | FULL |
| P6 | Alkhalifa et al., *Extended overview of the CLEF 2024 LongEval Lab on Longitudinal Evaluation of Model Performance*, CLEF 2024 Working Notes | **FULL READ.** LongEval measures temporal persistence over evolving retrieval corpora and directly compares NDCG/MAP across lags; its Lag6/Lag8 corpora differ materially in size and composition. No same-size random-removal control for the retrieval-age effect appears in the published Task-1 method. E2 survives only as our size/age decomposition. | FULL |
| P7 | Kuissi, Subrahmanyan, Thakur, Lin, *Still Fresh? Evaluating Temporal Drift in Retrieval Benchmarks*, 2026 | Snapshot-based drift measurement; finds benchmarks largely survive re-judging. A useful contrast to a corpus where ranking turns over a third per quarter | SNIPPET |
| P8 | *Temporal Misgrounding in Legal RAG: A Versioned-Corpus Benchmark for French Tax Law*, 2026 | Temporal validity as a legal-domain problem with a versioned corpus. The nearest legal neighbour to §6 | SNIPPET |
| P9 | Abu Shairah et al., *ALARB: An Arabic Legal Argument Reasoning Benchmark*, ArabicNLP 2025, DOI 10.18653/v1/2025.arabicnlp-main.32 | **FULL READ.** 13,344 Saudi commercial cases, mapped statutes/articles, verdict/argument tasks and article-identification tasks. The attempted full-corpus embedding retriever performed poorly and the released benchmark uses MCQ article selection, so it is adjacent rather than the same retrieval design. | FULL |
| P10 | Alharbi, Alshammari, Almutairi & Alahmadi, *ArabiCCR: A commercial Arabic ruling court cases dataset with judicial decisions*, Data in Brief 66 (2026) 112844, DOI 10.1016/j.dib.2026.112844 | **ARTICLE + DATA RECORD CHECKED.** Confirms a separately published Saudi commercial-rulings dataset drawn from the Ministry of Justice source family. The manuscript cites it only to delimit dataset novelty. | FULL-CLAIM-SURFACE |
| P11 | Vogels, Ganea & Eickhoff, *Web2Text: Deep Structured Boilerplate Removal*, ECIR 2018; Fernández-Pichel et al., *An unsupervised perplexity-based method for boilerplate removal*, NLE 2024 | **METHOD/RESULT SECTIONS READ.** Both evaluate boilerplate removal extrinsically on retrieval, so downstream IR validation of cleaning is established. Web2Text also shows low-recall cleaners can hurt retrieval by deleting relevant content. Neither tested whether a targeted cleaner's effect exceeds a random removal of the same evidentiary volume. §2 must cite this tradition directly; do not imply downstream validation itself is new. | FULL-RELEVANT-SECTIONS |
| P12 | *Legal Case Retrieval: A Survey of the State of the Art*, ACL 2024 | Positioning for §2 | SNIPPET |
| P13 | Data-contamination surveys, and *Search-Time Data Contamination*, 2025 | Where the verbatim-overlap control in §6 belongs in the wider vocabulary | SNIPPET |

## Method citation closeout

- §4.1 banded MinHash is now cited to Broder (1997), DOI 10.1109/SEQUEN.1997.666900.
- §5.2 BM25 is now cited to Robertson & Zaragoza (2009), DOI 10.1561/1500000019.
- §8 does not name CUSUM or Page-Hinkley in the manuscript; the stale TODO was removed. The permutation calibration is described operationally and is not sold as a new statistical method.

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

### P14 — direct legal temporal-decay neighbour added by controller review

**Ovcharov (2026), _Temporal Decay of Co-Citation Predictability: A 20-Year Statute Retrieval Benchmark from 396M Ukrainian Court Citations_, arXiv:2605.17639.**

Reading status: **FULL METHOD/RESULT SURFACES + released benchmark card inspected.** The study tracks legal statute retrieval across 20 annual snapshots, reports 33% decay on a fixed article set and 47% under a temporal train/test design, includes BM25/dense baselines, and uses fixed-article / train-test ablations plus sliding-window mitigation to argue that the effect is genuine temporal decay rather than composition/evaluation artifact. This kills any broad claim that controlled temporal decomposition of legal retrieval is new.

Consequence for this manuscript: E2 survives only as a **different estimand** — for a frozen legal BM25 index, how much of the observed MRR loss is reproduced by randomly removing the same number of contexts, versus the residual associated with age. State that result directly; do not call controlled temporal decomposition itself novel.
