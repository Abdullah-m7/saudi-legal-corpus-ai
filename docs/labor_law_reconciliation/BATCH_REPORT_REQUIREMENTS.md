# Labor Law Batch Report Requirements

Every Labor Law reconciliation batch report must be Arabic and must include the following sections.

## Required report fields

1. Stage name and baseline.
2. Branch.
3. Files created and modified.
4. Official source used.
5. Popup-aware method used.
6. Articles covered.
7. Batch CSV row count.
8. Cleanly reconciled article count.
9. Needs-manual-review count.
10. List of cleanly reconciled articles.
11. List of amended, popup, mukarrar, deleted, renumbered, or manual-review articles.
12. Special article handling, if any.
13. Candidate comparison summary.
14. `article_inventory.csv` update summary.
15. `article_source_checklist.csv` update summary.
16. `extraction_quality_issues.csv` update summary.
17. `unresolved_issues_log.csv` update summary.
18. `readiness_summary.csv` result.
19. Explicit unresolved count check:
    - previous total;
    - current unresolved log data-row count;
    - current readiness summary total;
    - whether the count increased, stayed the same, or decreased;
    - confirmation that any decrease has documented closures.
20. What was intentionally not done.
21. Confirmation no final ingestion occurred.
22. Confirmation no registry, export, runtime, or validator changes occurred.
23. Confirmation no English records or alignment were created.
24. Confirmation no prohibited files were committed.
25. Confirmation no generated consolidated legal text was created.
26. Actual validation results.
27. Legal and product boundaries.
28. Next recommended stage.

## Validation section rule

The validation section must state actual results. It must not contain future-tense or placeholder validation wording.

Required lines must cover:

- `make validate`
- `make test`
- whether any failures are known baseline failures;
- whether new failures were introduced;
- whether any modified test data was restored.

## Boundary wording

The report must state that Arabic official source governs and English remains reference-only.

The approved owner-review phrase must appear exactly once in the legal/product boundaries section.
