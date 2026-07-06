# Corpus Registry

The canonical corpus registry (`corpus_registry.json`) is a lightweight,
machine-readable index that summarizes and links all completed corpus tracks
in the repository.

## Purpose

- Improve project navigability and future automation
- Expose counts, paths, statuses, languages, boundaries, and validation targets
- Support future export, search, RAG, translation planning, and corpus navigation
- Freeze the current state of completed tracks

## What this is NOT

- Not a new legal corpus layer
- Not an export system, RAG demo, or search index
- Not a translation or legal analysis tool
- Not an official government publication

## Structure

The registry contains:

- **Top-level metadata**: version, date, repository, baseline commit, legal
  boundaries, total tracks, total known records, validation status
- **Tracks**: one entry per corpus track, each with:
  - `track_id`, `display_name_ar`, `corpus_family`, `jurisdiction`
  - `language_layers` (Arabic governing, English reference, Chinese internal)
  - `status`, `source_authority`, `source_url`, publication dates
  - `record_counts` (articles, forms, appendices, totals)
  - `data_paths`, `manifest_paths`, `validator_targets`, `report_paths`
  - `boundaries` (Arabic governs, not official translation, not legal advice, etc.)
  - `notes`

## Tracks

1. **companies_law** — Saudi Companies Law (M/132, 1443H), 281 articles
   - Arabic governing layer (281 records)
   - English reference/guidance layer (281 records)
   - Chinese internal remediation complete (281 articles, P0–P3)

2. **implementing_regulations_general** — General implementing regulations
   - 95 articles + 4 forms
   - Arabic Legal LLM-ready layer

3. **implementing_regulations_listed_joint_stock** — Listed joint-stock regulation
   - 69 articles + 1 appendix
   - Specialized (NOT general)

4. **implementing_regulations_arabic_program_closure** — Closure audit
   - 164 article records + 5 non-article records = 169 total

## Legal Boundaries

- Arabic official source governs
- Not official translation
- Not legal advice
- No trilingual alignment
- No public release
- English = reference/guidance only
- Chinese = internal reference only

## Validate

```bash
make corpus-registry-validate
```

## Generator

```bash
python3 scripts/gen_corpus_registry.py
```

The generator is idempotent — re-running produces identical output.