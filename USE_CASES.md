# USE CASES

Practical uses of this repository, stated **without overclaiming**. This is a
multilingual, LLM-ready, official-source-based Saudi legal corpus for AI; the
Companies Law is the first implemented law profile. Nothing here is production
certified, officially adopted, or legal advice.

> **Boundaries for every use case below:** the **official Arabic source
> governs**; English and Chinese are **reference layers** (Chinese is not
> official, not binding, not governing). This repository makes **no claim of
> production readiness, official government publication, official translation,
> or official government adoption**. This is **not legal advice**.

---

## 1. Government legal data infrastructure

A structured, auditable, machine-readable foundation that government entities
can evaluate for organizing Saudi laws and regulations into versioned legal
layers with explicit provenance and validation.

## 2. AI / RAG legal retrieval

Article-level JSON and per-article LLM/RAG chunks (one self-contained record per
article) suitable for retrieval-augmented generation and grounding, with Arabic
as the governing text and hashes for traceability.

## 3. Multilingual legal access

Parallel Arabic (governing), English (reference), and Chinese (internal
reference) layers to support reading and cross-referencing across languages —
as reference material, not as an official multilingual gazette.

## 4. Enterprise compliance workflows

A machine-readable base that enterprises can integrate into internal compliance
tooling and knowledge bases, subject to their own review. External legal review
is optional for enterprise adoption and not required for repository use.

## 5. Foreign companies entering the Saudi market

Structured Companies Law content that companies operating in or entering Saudi
Arabia can use for orientation and internal research — a starting reference, not
a substitute for qualified local counsel.

## 6. Legal search

Clean, selectable, searchable text (canonical JSON and generated views) enabling
article-level search across the implemented law profile.

## 7. Public legal understanding

Readable, structured views that help ordinary users understand the shape and
content of the law, with clear disclaimers about official status.

## 8. Developer dataset / testing use

A well-validated, schema-conformant, versioned dataset developers can use to
build and test legal-NLP, retrieval, and translation-review tooling.

## 9. Future API / export use

The foundation is designed to support future RAG/API export and cross-batch
tooling. These generic pipeline components are **described as future work and
are not implemented yet**.
