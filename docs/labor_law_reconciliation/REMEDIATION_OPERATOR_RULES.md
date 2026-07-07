# Labor Law Amendment Popup Remediation Operator Rules

This document defines the operating rules for the Labor Law amendment-popup remediation operator. It governs the future remediation pilot workflow only. It does not create final corpus records, does not validate legal correctness, and does not provide legal advice.

## Scope

These rules govern the remediation of articles whose current official Arabic text could not be cleanly captured during worksheet reconciliation because the text is displayed through an amendment popup, a PDF attachment, a renumbered reference, or another structure that prevents direct DOM capture.

The remediation operator is a source-access and decision-logging tool. It does not synthesize, consolidate, or generate legal text.

## Source hierarchy

1. The official Arabic source governs. Arabic is the authoritative language for Saudi Labor Law text.
2. The BOE (Bureau of Expertise / Bureau of Experts / boe.gov.sa) official Arabic current article text is the primary source.
3. Another official Arabic government source (e.g., uqn.gov.sa or the relevant ministry portal) is secondary, used only when BOE does not clearly expose the current article text.
4. English material is reference-only and never governing.
5. No other source overrides official Arabic government text.

## Prohibited operator behaviors

The remediation operator must not:

- provide legal advice;
- provide legal interpretation;
- provide legal validity judgment;
- generate legal text;
- synthesize consolidated text from base article text plus amendment popup;
- manually consolidate base text with popup amendment text;
- present old or base deleted text as current law;
- silently close any issue;
- close any issue without evidence;
- create final legal records;
- create English records;
- create bilingual or trilingual alignment;
- commit JSON, JSONL, XLSX, PDF, HTML, or other source dump artifacts;
- modify any CSV data files unless explicitly authorized by the remediation batch scope.

## Mandatory source-access attempt

Every amended or popup article must have a documented source-access attempt before it may remain in manual-review status. The documentation must record:

- the source URL accessed;
- the access method used (e.g., BOE DOM, BOE popup, BOE PDF, other official Arabic source);
- the capture or block decision;
- the reason for the decision.

An article may not remain `DO_NOT_INGEST_YET` / `needs_manual_review` without a documented source-access attempt.

## Capture decision rules

### When capture is allowed

If the current official Arabic text is clearly displayed in the BOE source — whether in the main DOM, a popup container, or a PDF — then capture is allowed in a future remediation batch. The decision is `CAPTURE_ALLOWED_OFFICIAL_CURRENT_TEXT`.

### When capture is blocked

If the current official Arabic text is not clearly displayed — for example, the BOE page shows only base text while the amendment appears in a popup that does not expose clean current consolidated text — then the article remains `DO_NOT_INGEST_YET` / `needs_manual_review`. The decision is one of:

- `BLOCKED_POPUP_BASE_STRUCTURE` — the page structure prevents clean capture of current text.
- `REMAINS_MANUAL_REVIEW` — the source was accessed but the text is not clearly available.

### Deleted or abolished articles

Deleted or abolished articles must not have old or base text captured as current official text. The decision is `DELETED_OR_ABOLISHED_EXCLUDE`. Old or base text must never be presented as current law.

### Renumbered articles

Renumbered articles must not be ingested under an invented or unconfirmed article number. The decision is `RENUMBERED_NEEDS_OFFICIAL_CONFIRMATION`. Official confirmation of the renumbering is required before any capture.

### Structural tracking only

Some articles may be tracked structurally without text capture. The decision is `STRUCTURAL_TRACKING_ONLY`. This applies when the article is known to exist but text capture is not the current task.

## Issue closure rules

- No issue may be closed silently.
- Every issue closure requires evidence: a source URL, an access method, a decision, and a reason.
- An issue may be closed only when the remediation operator has documented a source-access attempt and the decision supports closure.
- If the source-access attempt does not produce clear current text, the issue remains open.

## Boundary confirmations

Every remediation batch report must confirm:

- Arabic official source governs.
- English is reference-only and never governing.
- No final ingestion occurred.
- No generated consolidated legal text was created.
- No base+popup synthesis was performed.
- No source dumps were committed.
- No CSV modifications were made unless explicitly authorized by the remediation batch.
- Every issue closure has evidence.

## Relationship to existing operator rules

This document extends `OPERATOR_RULES.md` for the remediation phase. It does not replace it. The existing operator rules continue to govern worksheet reconciliation. These remediation rules govern the post-reconciliation remediation pilot.

## Non-goals

This operator does not perform legal interpretation, legal correctness review, final corpus ingestion, English record creation, bilingual alignment, RAG, API, UI, embeddings, or source-dump archiving.