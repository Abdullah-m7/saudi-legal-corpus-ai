# NOTICE — Legal Content, Provenance, and Disclaimers

## Public repository status

As of August 2026 this repository is **publicly available on GitHub**, and
versioned releases are archived on **Zenodo** (see the DOI badge in
`README.md` once minted). Public availability changes **none** of the
disclaimers below: the repository remains a non-official research resource.

## Not an official publication

This repository is **not an official government publication**. It claims
**no official translation** and **no official government adoption**. The
only legally binding text of any instrument in this corpus is the Arabic
original as published in the official gazette **Umm Al-Qura (أم القرى)**
and maintained by the competent authorities.

## Not legal advice

This material is provided for general reference, research, and directed
lookup only. It **does not constitute legal advice**. Before making any
business or legal decision, consult the full official text and a
Saudi-qualified legal advisor.

## Provenance and canonical source model

- The **canonical structured sources** are the JSON files under `data/`;
  human-readable outputs are generated from them.
- The **official Arabic text governs.** Each track records its issuing
  authority and official source(s) in the corpus registry
  (`data/corpus_registry/`), and each article-level record carries a
  per-record provenance label (`text_status`).
- Source quality is represented, not assumed: every track is assigned a
  **verification tier** (`data/corpus_verification_tiers/`), and tracks
  with a documented source-staleness risk are flagged in the
  **freshness manifest** (`data/corpus_freshness_manifest/`) rather than
  silently patched.
- Read-only, idempotent validators (see the `Makefile`) enforce schema,
  counts, and hashes across all layers.

## Language layers

- **Arabic** is the governing layer, ingested **verbatim** from the
  recorded official sources.
- **English** layers are **non-official reference** material.
- **Chinese** layers are **internal reference only** — non-official,
  non-binding, non-governing. The early Book One (Articles 1–34) concise
  reference translation that this repository started from is retained as a
  historical artifact (`inputs/bab1_source.pdf` and related files); it was
  internally QA-reviewed against its translation source, and the corpus has
  since moved to the registry-based provenance model described above.

## Copyright posture

- Saudi statutory and regulatory texts reproduced here are **public legal
  enactments** of the Kingdom of Saudi Arabia; official texts of laws,
  regulations, and similar state documents are excluded from copyright
  protection under the Saudi Copyright Law. This repository **asserts no
  ownership** over them and reproduces them verbatim for reference and
  research, with per-record source attribution.
- The structuring apparatus — schemas, scripts, derived layers, metadata,
  and documentation — is released under the **MIT License** (see
  `LICENSE`).

## Instrument reference (first implemented profile)

- نظام الشركات — المرسوم الملكي رقم (م/132) وتاريخ 1443/12/1هـ
- Companies Law — Royal Decree No. (M/132), issued 2022.

The full list of onboarded instruments is maintained in the corpus registry
(`data/corpus_registry/corpus_registry.json`).
