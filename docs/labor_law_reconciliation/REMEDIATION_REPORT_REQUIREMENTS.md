# Labor Law Amendment Popup Remediation Report Requirements

Every Labor Law amendment-popup remediation batch report must include the following sections. These requirements are mandatory for all future remediation pilot reports.

## Required report sections

1. **Stage** — the stage name.
2. **Baseline SHA** — the commit SHA used as baseline.
3. **Branch** — the branch name.
4. **Articles/issues attempted** — the list of article keys and unresolved issue IDs covered by the batch.
5. **Source URLs** — every source URL accessed per article.
6. **Source access method** — the method used per article (BOE DOM, BOE popup, BOE PDF, other official Arabic source).
7. **Per-article decision** — one of:
   - `CAPTURE_ALLOWED_OFFICIAL_CURRENT_TEXT`
   - `BLOCKED_POPUP_BASE_STRUCTURE`
   - `DELETED_OR_ABOLISHED_EXCLUDE`
   - `RENUMBERED_NEEDS_OFFICIAL_CONFIRMATION`
   - `STRUCTURAL_TRACKING_ONLY`
   - `REMAINS_MANUAL_REVIEW`
8. **Captured text count** — if any articles were captured, the count and list. If none, state zero.
9. **Blocked count** — the number of articles blocked from capture.
10. **Deleted/excluded count** — the number of articles excluded as deleted or abolished.
11. **Renumbered/special count** — the number of renumbered or structurally tracked articles.
12. **Issues closed** — if any issues were closed, the list with evidence basis for every closure. If none, state zero.
13. **Issues remaining** — the list of issues that remain unresolved after the batch.
14. **Evidence basis for every closure** — for each closed issue: source URL, access method, decision, and reason.
15. **No base+popup synthesis confirmation** — explicit confirmation that no base+popup synthesis was performed.
16. **No final ingestion confirmation** — explicit confirmation that no final ingestion occurred.
17. **Validation results** — actual results of `python -m py_compile`, `make validate`, and `make test`. No placeholder or future-tense wording.
18. **Boundary confirmations** — explicit confirmation of all boundary statements (see below).
19. **Next recommended stage** — the recommended next stage name.

## Boundary confirmations

The report must explicitly state all of the following:

- Arabic official source governs.
- English is reference-only and never governing.
- No final ingestion occurred.
- No generated consolidated legal text was created.
- No base+popup synthesis was performed.
- No source dumps were committed.
- No CSV modifications were made unless explicitly authorized by the remediation batch.
- Every issue closure requires evidence (and all closures in this batch have evidence).

## Validation section rule

The validation section must state actual results. It must not contain future-tense or placeholder validation wording.

Required lines must cover:

- `python -m py_compile` results for the remediation checker and the reconciliation checker.
- `make validate` result.
- `make test` result.
- whether any failures are known baseline failures;
- whether new failures were introduced;
- whether any modified test data was restored.

## Prohibited content

The report must not contain:

- claims of legal advice, legal interpretation, or legal validity judgment;
- claims of generated or synthesized legal text;
- claims of final ingestion or final legal record creation;
- claims of English record creation or bilingual alignment;
- placeholder validation wording;
- source dump content (BOE HTML, PDF text, raw JSON, etc.).

## Relationship to existing report requirements

This document extends `BATCH_REPORT_REQUIREMENTS.md` for the remediation phase. The existing requirements continue to govern worksheet reconciliation batch reports. These remediation requirements govern the post-reconciliation remediation pilot reports.