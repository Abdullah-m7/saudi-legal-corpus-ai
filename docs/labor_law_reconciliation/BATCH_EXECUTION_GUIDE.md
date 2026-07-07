# Labor Law Batch Execution Guide

This guide shortens future Labor Law reconciliation prompts by moving repeated operating rules into repository documentation and a local structural checker.

## Future short prompt pattern

Each future batch prompt should only specify:

- stage name;
- current main baseline;
- article range;
- unresolved issue floor;
- known special articles from tracking files;
- expected next stage.

The executor must then follow:

- `docs/labor_law_reconciliation/OPERATOR_RULES.md`
- `docs/labor_law_reconciliation/BATCH_REPORT_REQUIREMENTS.md`
- `worksheets/labor_law/reconciliation_scaffold/batch_execution_manifest.csv`
- `tools/check_labor_law_reconciliation_batch.py`

## Required execution sequence

1. Confirm current baseline.
2. Read the batch row in `batch_execution_manifest.csv`.
3. Read tracking files before touching scoped rows:
   - `amendment_tracking.csv`
   - `m44_tracking.csv`
   - `mukarrar_deleted_renumbered_tracking.csv`
   - `unresolved_issues_log.csv`
4. Create the batch CSV.
5. Update only scoped rows in scaffold worksheets.
6. Add new unresolved issues only when needed.
7. Carry forward existing unresolved issues without duplication.
8. Update `readiness_summary.csv` and keep its unresolved count equal to unresolved log data rows.
9. Write the batch report with actual validation results.
10. Run the local checker before opening a PR.

## Example checker command

```bash
python tools/check_labor_law_reconciliation_batch.py --batch 006 --range 126-150 --unresolved-floor 91
```

For a future batch, update the batch number, range, and unresolved floor.

## Non-goals

This operator does not perform legal interpretation, legal correctness review, RAG, API, UI, embeddings, or final corpus ingestion.
