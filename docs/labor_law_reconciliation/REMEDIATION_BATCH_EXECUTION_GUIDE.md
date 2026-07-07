# Labor Law Amendment Popup Remediation Batch Execution Guide

This guide defines the workflow for the first amendment-popup remediation pilot. It is designed to be lean, practical, and pilot-ready.

## Inputs

Each remediation batch prompt should specify:

- stage name;
- current main baseline SHA;
- branch name;
- selected unresolved issue IDs;
- selected article keys;
- known special articles from tracking files;
- expected next stage.

The executor must then follow:

- `docs/labor_law_reconciliation/REMEDIATION_OPERATOR_RULES.md`
- `docs/labor_law_reconciliation/REMEDIATION_REPORT_REQUIREMENTS.md`
- `tools/check_labor_law_remediation_batch.py`

## Per-article workflow

For each article in the batch:

1. **Open the BOE official Arabic source.**
   Access the BOE page for the article. Record the source URL.

2. **Determine whether current official Arabic article text is clearly displayed.**
   Check whether the full current post-amendment Arabic text is visible. The text may appear in the main DOM, in a popup container, in a linked PDF, or in another official Arabic government source.

3. **Identify where the text lives.**
   Classify the text location as one of:
   - main DOM;
   - popup;
   - PDF;
   - another official Arabic source.

4. **Decide one of:**
   - `CAPTURE_ALLOWED_OFFICIAL_CURRENT_TEXT` — current official Arabic text is clearly displayed and safe to capture in a future remediation batch.
   - `BLOCKED_POPUP_BASE_STRUCTURE` — the page shows base text in the main DOM and amendment details in a popup, but current consolidated text is not clearly exposed. The article remains `DO_NOT_INGEST_YET`.
   - `DELETED_OR_ABOLISHED_EXCLUDE` — the article was deleted or abolished. Old or base text must not be captured as current law.
   - `RENUMBERED_NEEDS_OFFICIAL_CONFIRMATION` — the article may have been renumbered. Official confirmation is required before capture.
   - `STRUCTURAL_TRACKING_ONLY` — the article is tracked structurally but text capture is not the current task.
   - `REMAINS_MANUAL_REVIEW` — the source was accessed but current text is not clearly available. The article remains `DO_NOT_INGEST_YET` / `needs_manual_review`.

5. **Document the source URL and reason.**
   For every article, record:
   - source URL accessed;
   - access method (BOE DOM, BOE popup, BOE PDF, other official Arabic source);
   - decision;
   - reason.

6. **Do not synthesize text.**
   Never combine base text with popup amendment text to produce consolidated legal text. Never generate legal text.

7. **Do not close issues without evidence.**
   An issue may be closed only when a source-access attempt is documented and the decision supports closure. Silent closure is prohibited.

## What this guide does not do

- Does not start the pilot.
- Does not remediate article text.
- Does not modify CSV data files.
- Does not perform final ingestion.
- Does not create final legal records.
- Does not create English records.
- Does not create bilingual or trilingual alignment.
- Does not commit source dumps or binary artifacts.

## Checker command

After a future remediation batch produces its report, run:

```bash
python tools/check_labor_law_remediation_batch.py --report <REPORT_PATH>
```

The checker validates that the report contains required boundary language and does not contain prohibited claims. It must pass before a PR is opened.

## Non-goals

This guide does not perform legal interpretation, legal correctness review, RAG, API, UI, embeddings, or final corpus ingestion.