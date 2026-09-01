# Controller venue decision — 2026-09-01

## Decision

**PRIMARY: Artificial Intelligence and Law (Springer Nature)**  
**STATE: AI_AND_LAW_READY_AFTER_FORMATTING — no new experiment authorized.**

The current journal scope explicitly includes **intelligent processing of legal documents; conceptual retrieval of cases and statutes**, **evaluation and auditing techniques for legal AI systems**, and **systemic problems in the construction and delivery of legal AI systems**. The paper now sits inside those clauses directly: its dependent variables are legal-retrieval performance and temporal retrieval degradation, not corpus statistics followed by an AI implications section.

The current editorial footprint also supports the fit. In 2026 the journal published empirical work on legal citation prediction, AI-driven legal question answering/RAG, and robustness/reliability of legal LLMs. This does not guarantee review, but it removes the argument that empirical retrieval/evaluation is outside the journal's present-day scope.

## Claim after the prior-art attack

The paper does **not** claim novelty for deduplication, downstream IR evaluation of boilerplate removal, matched-budget controls, legal citation-context retrieval, temporal persistence, or controlled temporal decomposition. Those are established.

The publication-facing contribution is now bounded to: (E1) on 105,575 resolved Saudi statutory citations, removing recurring legal wording costs 0.0241 MRR@10 versus 0.0089 for same-volume random removal, with the targeted arm outside all 20 matched draws in the five largest-removal folds; (E2) frozen-index loss is decomposed against a same-volume live-index control, leaving 70%, 64% and 62% of the one-, two- and four-quarter loss associated with age rather than shrinkage; and the characterization of what the removed evidentiary material actually contains.
## Why BM25-only is not a pre-submission blocker

The paper uses BM25 deliberately so that the corpus treatment is the moving part. A dense retriever would be a useful robustness extension, but it would change the scientific question from *what does this preprocessing step do under a transparent retrieval instrument?* to *how architecture-dependent is the effect?* The present result is already a valid controlled empirical contribution. A reviewer request for dense retrieval is therefore a revision path, not grounds to reopen the cycle pre-emptively.

## Current journal mechanics checked

The journal is hybrid and uses double-anonymous review. The current guidelines request a 150–250 word abstract, 4–6 keywords, name-year citations, an alphabetized reference list with DOI links when available, and editable Word or LaTeX source files. LLM use that goes beyond copy editing must be documented in Methods. The current manuscript has six keywords and is already author-anonymous; the remaining work is formatting/integration, not science.

## Fallback

If the journal desk-rejects this manuscript for fit after the technical contribution is visible on page one, the fallback is **JURIX / another specialist legal-IR venue**, preserving the same scientific core. Do not add a fourth corpus, a neural retriever, or another legal-AI context section merely to rescue a speculative desk prediction.

## Stop rule

Before submission, complete only: integrate the verified bibliography; replace placeholder citation syntax with Springer name-year form; produce the double-anonymous source file; add the required AI-use statement and declarations in the correct submission surfaces; run the existing 187-figure trace and 60-result freshness checks again. Then the author decides whether to press Submit.
