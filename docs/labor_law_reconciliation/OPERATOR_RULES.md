# Labor Law Reconciliation Operator Rules

This document defines reusable operating rules for Saudi Labor Law worksheet reconciliation batches.

## Scope

These rules govern worksheet-level Arabic text reconciliation only. They do not create final corpus records, do not validate legal correctness, and do not provide legal advice.

## Source hierarchy

1. The official Arabic BOE source governs.
2. English material is reference-only support.
3. Chinese material is internal reference only.
4. Uploaded local text files may be used only as raw comparison aids and must never override BOE.

## Popup-aware source handling

BOE may display original or base article text in the main article body while amendment details appear through a show-amendment popup or article popup container.

Main DOM text is acceptable only when the article is clearly non-amended. For amended articles, main DOM text alone is not sufficient.

## Article status rules

### Non-amended articles

A non-amended article may be marked ready for future ingestion only when the official Arabic text is clearly captured from BOE and the row has a SHA-256 hash and a positive character length.

Required fields for clean rows:

- `official_arabic_text_source_method=BOE_DOM_ARTICLE_TEXT`
- `reconciliation_status=RECONCILED_FROM_BOE_OFFICIAL_AR`
- `ready_for_future_ingestion_flag=yes`

### Amended articles

Amended articles must remain blocked unless clean current post-amendment official text is clearly captured from BOE.

If the current text is not safely captured:

- Leave `official_arabic_text_reconciled` empty.
- Leave `official_arabic_text_hash_sha256` empty.
- Set `official_arabic_text_length_chars=0`.
- Set `official_arabic_text_source_method=NEEDS_AMENDMENT_POPUP_RECONCILIATION`.
- Set `reconciliation_status=DO_NOT_INGEST_YET`.
- Set `ready_for_future_ingestion_flag=needs_manual_review`.

Never synthesize consolidated legal text from base text plus an amendment popup.

### Deleted or abolished articles

Deleted or abolished articles must not capture old or base text as current official text. If current status is unclear or only historical/base text appears, mark the row as manual review and do not ingest.

### Renumbered articles

Do not invent article identity and do not duplicate text under old and new numbers unless the official source clearly supports it.

### Mukarrar articles

Treat a mukarrar article as independent only when confirmed by inventory/tracking and visible as an independent BOE item. If a mukarrar reference is not independently found, carry forward the existing issue and do not fabricate a row.

## Issue handling

Existing unresolved issue rows must be carried forward and not duplicated. New issue IDs must continue from the previous highest issue ID.

`readiness_summary.total_unresolved_issues` must equal the data-row count in `unresolved_issues_log.csv`, unless a stage explicitly documents issue closures. The count must not decrease without documented closures.

## Report requirements

A committed stage report must include actual validation results. It must not contain placeholder wording that suggests validation will be run later.

## Prohibited stage behavior

Worksheet reconciliation stages must not:

- create final Labor Law corpus records;
- modify registry, export records, runtime, or validators;
- create English records;
- create bilingual or trilingual alignment;
- commit source dumps, PDFs, BOE HTML, uploaded TXT/PDF files, JSON, JSONL, XLSX, or generated PDF artifacts;
- add RAG, UI, API, network, LLM, or embedding artifacts;
- include generated paraphrases as legal text;
- provide legal advice, legal interpretation, or legal correctness judgments.
