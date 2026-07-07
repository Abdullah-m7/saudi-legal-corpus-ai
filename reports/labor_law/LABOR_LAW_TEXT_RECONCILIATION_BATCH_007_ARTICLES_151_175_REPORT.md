# Labor Law Text Reconciliation Batch 007 — Articles 151–175

## Stage

LABOR_LAW_TEXT_RECONCILIATION_BATCH_007_ARTICLES_151_175_WITH_AMENDMENT_POPUP_HANDLING

## Baseline

a15be82243a5562fe2da154f32860d6a51d50307

## Branch

hermes/labor-law-text-reconciliation-batch-007-articles-151-175-popup-aware

## Files Created

- `worksheets/labor_law/reconciliation_batches/labor_law_text_reconciliation_batch_007_articles_151_175.csv`
- `reports/labor_law/LABOR_LAW_TEXT_RECONCILIATION_BATCH_007_ARTICLES_151_175_REPORT.md`

## Files Modified

- `worksheets/labor_law/reconciliation_scaffold/article_inventory.csv`
- `worksheets/labor_law/reconciliation_scaffold/article_source_checklist.csv`
- `worksheets/labor_law/reconciliation_scaffold/extraction_quality_issues.csv`
- `worksheets/labor_law/reconciliation_scaffold/unresolved_issues_log.csv`
- `worksheets/labor_law/reconciliation_scaffold/readiness_summary.csv`

## Official Source Used

BOE official Arabic source: https://laws.boe.gov.sa/boelaws/laws/lawdetails/08381293-6388-48e2-8ad2-a9a700f2aa94/1

## Popup-Aware Method Used

Amendment tracking files were consulted before any row was populated. Articles identified as amended via `amendment_tracking.csv` and `m44_tracking.csv` were treated as popup-reconciliation candidates and not marked ready. Their BOE main DOM text was not captured as current official text. No consolidated legal text was generated from base text plus amendment popup.

## Articles Covered

Articles 151–175 (25 base article rows)

## Batch CSV Row Count

25

## Cleanly Reconciled Article Count

19

## Needs-Manual-Review Count

6

## Cleanly Reconciled Articles

- Article 153 (المادة الثالثة والخمسون بعد المائة)
- Article 154 (المادة الرابعة والخمسون بعد المائة)
- Article 157 (المادة السابعة والخمسون بعد المائة)
- Article 158 (المادة الثامنة والخمسون بعد المائة)
- Article 159 (المادة التاسعة والخمسون بعد المائة)
- Article 161 (المادة الحادية والستون بعد المائة)
- Article 162 (المادة الثانية والستون بعد المائة)
- Article 163 (المادة الثالثة والستون بعد المائة)
- Article 164 (المادة الرابعة والستون بعد المائة)
- Article 165 (المادة الخامسة والستون بعد المائة)
- Article 166 (المادة السادسة والستون بعد المائة)
- Article 167 (المادة السابعة والستون بعد المائة)
- Article 169 (المادة التاسعة والستون بعد المائة)
- Article 170 (المادة السبعون بعد المائة)
- Article 171 (المادة الحادية والسبعون بعد المائة)
- Article 172 (المادة الثانية والسبعون بعد المائة)
- Article 173 (المادة الثالثة والسبعون بعد المائة)
- Article 174 (المادة الرابعة والسبعون بعد المائة)
- Article 175 (المادة الخامسة والسبعون بعد المائة)

## Amended / Popup / Deleted / Manual-Review Articles

- Article 151 (amended; M/44 and 5/6/1436; popup reconciliation needed; M/44 related; issue_094)
- Article 152 (amended; 5/6/1436; popup reconciliation needed; issue_095)
- Article 155 (amended; M/134; popup reconciliation needed; issue_096)
- Article 156 (deleted/abolished by amendment via M/134; existing issue_017 carried forward; no new issue added)
- Article 160 (amended; 5/6/1436; popup reconciliation needed; issue_097)
- Article 168 (amended; M/44; popup reconciliation needed; M/44 related; issue_098)

## Special Article Handling

- **Article 156**: Deleted/abolished by amendment via M/134 (confirmed in `amendment_tracking.csv` and `mukarrar_deleted_renumbered_tracking.csv`). Existing unresolved issue `issue_017` was carried forward. No new issue was added. Old/base text was not captured as current official text. Marked `DO_NOT_INGEST_YET` / `needs_manual_review`.
- **Article 151**: Amended by both M/44 and 5/6/1436 (two amendment references in `amendment_tracking.csv`). M/44 related per `m44_tracking.csv`. New issue `issue_094` added.
- **Article 168**: Amended by M/44. M/44 related per `m44_tracking.csv`. New issue `issue_098` added.

## Candidate Comparison Summary

No uploaded candidate was available for comparison in this batch. All clean rows used `BOE_DOM_ARTICLE_TEXT` as source method with `uploaded_candidate_compared_flag=not_available`.

## article_inventory.csv Update Summary

25 rows updated for Articles 151–175:
- 19 rows updated to `OFFICIAL_TEXT_CAPTURED_BATCH` / `TEXT_RECONCILED_BATCH_007` / `unresolved_issue_flag=no`
- 5 amended article rows updated to `NEEDS_MANUAL_CAPTURE` / `DO_NOT_INGEST` / `unresolved_issue_flag=yes`
- 1 deleted article row updated to `NEEDS_MANUAL_CAPTURE` / `DO_NOT_INGEST` / `unresolved_issue_flag=yes`

## article_source_checklist.csv Update Summary

25 rows updated for Articles 151–175:
- 19 clean rows updated to `ARTICLE_TEXT_CAPTURED_FROM_BOE` / `OFFICIAL_TEXT_CAPTURED_BATCH`
- 5 amended rows updated to `SOURCE_PAGE_IDENTIFIED` / `NEEDS_MANUAL_CAPTURE`
- 1 deleted row updated to `SOURCE_PAGE_IDENTIFIED` / `NEEDS_MANUAL_CAPTURE`

## extraction_quality_issues.csv Update Summary

5 new entries added:
- `eq_batch007_art151` — Article 151 amended; popup reconciliation needed
- `eq_batch007_art152` — Article 152 amended; popup reconciliation needed
- `eq_batch007_art155` — Article 155 amended; popup reconciliation needed
- `eq_batch007_art160` — Article 160 amended; popup reconciliation needed
- `eq_batch007_art168` — Article 168 amended; popup reconciliation needed

## unresolved_issues_log.csv Update Summary

5 new issues added (issue_094 through issue_098):
- `issue_094` — Article 151 amended (M/44 and 5/6/1436); popup reconciliation needed; M/44 related
- `issue_095` — Article 152 amended (5/6/1436); popup reconciliation needed
- `issue_096` — Article 155 amended (M/134); popup reconciliation needed
- `issue_097` — Article 160 amended (5/6/1436); popup reconciliation needed
- `issue_098` — Article 168 amended (M/44); popup reconciliation needed; M/44 related

Article 156 (deleted/abolished) — existing issue `issue_017` carried forward; no new issue added.

Total data rows in `unresolved_issues_log.csv`: 98 (was 93, increased by 5).

## readiness_summary.csv Result

- `ingestion_readiness_decision`: NOT_READY
- `total_unresolved_issues`: 98
- `summary_notes`: Batch 001–007 populated. Batch 007 covers Articles 151–175 (25 rows): 19 cleanly reconciled, 6 need manual review. No final ingestion.

## Explicit Unresolved Count Check

- Previous total (unresolved floor): 93
- Current `unresolved_issues_log.csv` data-row count: 98
- Current `readiness_summary.csv` `total_unresolved_issues`: 98
- The count increased from 93 to 98 (increase of 5) due to 5 new amended-article popup reconciliation issues (issue_094 through issue_098).
- No closures were documented; no count decrease occurred.
- Confirmation: The unresolved count did not decrease below 93.

## What Was Intentionally Not Done

- No final Labor Law corpus records were created.
- No registry, export, runtime, or validator changes were made.
- No English records or alignment were created.
- No bilingual/trilingual alignment was performed.
- No consolidated legal text was generated from base text plus amendment popup.
- No RAG, UI, API, network, LLM, or embedding artifacts were added.
- No source dumps, PDFs, BOE HTML, JSON, JSONL, or XLSX files were committed.
- No Companies Law files were modified.

## Confirmation No Final Ingestion Occurred

No final ingestion occurred. All amended and deleted articles are marked `DO_NOT_INGEST_YET`. Clean articles are marked `ready_for_future_ingestion_flag=yes` but no ingestion was performed.

## Confirmation No Registry/Export/Runtime/Validator Changes

No registry, export, runtime, or validator files were modified. Only worksheet and report files were created or updated.

## Confirmation No English Records or Alignment

No English records were created. No bilingual or trilingual alignment was performed. English remains reference-only.

## Confirmation No Prohibited Files

No source dumps, PDFs, BOE HTML, uploaded TXT/PDF files, JSON, JSONL, XLSX, or generated PDF artifacts were committed.

## Confirmation No Generated Consolidated Legal Text

No consolidated legal text was generated from base text plus amendment popup. Amended articles have empty `official_arabic_text_reconciled` fields.

## Validation Results

### py_compile

```
python -m py_compile tools/check_labor_law_reconciliation_batch.py
```

Result: PASS (exit code 0)

### Batch Checker

```
python tools/check_labor_law_reconciliation_batch.py --batch 007 --range 151-175 --unresolved-floor 93
```

Result: PASS
- batch CSV structure OK
- readiness/unresolved counts OK
- report structure and boundary wording OK

### make validate

```
make validate
```

Result: PASS — `RESULT: ALL CHECKS PASSED ✓` (exit code 0)

### make test

```
make test
```

Result: PASS — `2497 passed in 22.64s` (exit code 0)

Known baseline failures: None. No new failures were introduced. No modified test data was restored.

## Legal and Product Boundaries

Arabic official source governs and English remains reference-only. This stage performs worksheet-level Arabic text reconciliation only. It does not create final corpus records, does not validate legal correctness, and does not provide legal advice. repository-owner legal review active; external legal review optional for enterprise/official adoption

## Next Recommended Stage

LABOR_LAW_TEXT_RECONCILIATION_BATCH_008_ARTICLES_176_200_WITH_AMENDMENT_POPUP_HANDLING