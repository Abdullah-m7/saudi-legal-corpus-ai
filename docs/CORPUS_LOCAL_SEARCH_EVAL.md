# Corpus Local Search Evaluation — Usage Guide

## Overview

This stage adds a lightweight, deterministic evaluation fixture layer for the
existing local lexical search CLI (`scripts/search_primary_arabic_export.py`).

**This is NOT RAG.** No embeddings, no semantic search, no API, no network.

The goal is to provide regression protection and quality signal before any
future search or RAG changes.

## Files

| File | Purpose |
|------|---------|
| `data/search_eval/local_search_queries_v1.json` | Fixture file (10 Arabic queries) |
| `scripts/validate_corpus_local_search_eval.py` | Validator — runs fixtures, checks expectations |
| `tests/test_corpus_local_search_eval.py` | Test suite — schema + search behavior |
| `docs/CORPUS_LOCAL_SEARCH_EVAL.md` | This guide |

## Quick Start

```bash
# Validate all evaluation fixtures
make corpus-local-search-eval-validate

# Run the test suite
python3 -m pytest tests/test_corpus_local_search_eval.py -v

# Or use the validator directly
python3 scripts/validate_corpus_local_search_eval.py
```

## Fixture Schema

Each fixture in `local_search_queries_v1.json` is a JSON object:

```json
{
  "fixture_id": "EVAL-001",
  "query": "الشركة",
  "description_ar": "وصف بالعربية",
  "expected_min_matches": 300,
  "expected_max_matches": null,
  "expected_top_k_contains_any": ["export-cl-art-002"],
  "track_filter": null,
  "record_type_filter": null,
  "json_output": false,
  "expected_language": "ar",
  "boundary_note": "بحث معجمي فقط — لا تفسير قانوني",
  "evaluation_type": "broad_term"
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `fixture_id` | string | Unique identifier (e.g. `EVAL-001`) |
| `query` | string | Arabic search query |
| `description_ar` | string | Arabic description of the fixture |
| `expected_min_matches` | int | Minimum total matches required |
| `expected_language` | string | Must be `ar` |
| `boundary_note` | string | Legal boundary reminder |
| `evaluation_type` | string | One of the valid types below |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `expected_max_matches` | int | Maximum total matches allowed |
| `expected_top_k_contains_any` | string[] | Acceptable export_record_id values in top 10 |
| `track_filter` | string | Filter by `source_track_id` |
| `record_type_filter` | string | Filter by `record_type` |
| `json_output` | bool | If true, validate JSON output shape |

### Evaluation Types

| Type | Description |
|------|-------------|
| `broad_term` | Wide single-term query — catches empty-result regressions |
| `legal_phrase` | Specific legal phrase — checks precision |
| `track_filter` | Query with track filter — checks filter consistency |
| `record_type_filter` | Query with record type filter |
| `json_output` | Validates CLI JSON output structure |
| `normalization` | Tests Arabic normalization (hamza/alef variants) |
| `no_result_or_low_result` | Nonsense query — must return zero results |

## Adding New Fixtures

1. **Run the search** to discover stable IDs:

```bash
python3 scripts/search_primary_arabic_export.py "your query" --limit 10
python3 scripts/search_primary_arabic_export.py "your query" --json --limit 10
```

2. **Add fixture** to `data/search_eval/local_search_queries_v1.json`:

```json
{
  "fixture_id": "EVAL-011",
  "query": "your arabic query",
  "description_ar": "وصف الاستعلام",
  "expected_min_matches": 10,
  "expected_top_k_contains_any": ["export-cl-art-XXX"],
  "expected_language": "ar",
  "boundary_note": "بحث معجمي فقط — لا تفسير قانوني",
  "evaluation_type": "legal_phrase"
}
```

3. **Keep total fixtures between 8 and 12.** Do not overbuild.

4. **Validate:**

```bash
make corpus-local-search-eval-validate
python3 -m pytest tests/test_corpus_local_search_eval.py -v
```

## Rules

- **Do not guess IDs.** Always run the search first and record actual stable IDs.
- **Do not modify** `primary_arabic_governing_records.jsonl` or source corpus files.
- **Do not add** embeddings, semantic search, API, UI, database, or network.
- **Do not add** English or Chinese text as source content.
- **Keep fixtures deterministic.** No randomization, no LLM-generated answers.
- **Keep the set small.** 8–12 fixtures only. No giant benchmarks.

## Validation Sequence

```bash
make validate
make test
make corpus-registry-validate
make corpus-export-primary-arabic-validate
make corpus-local-search-validate
make corpus-local-search-eval-validate
make corpus-local-search-smoke
```

## Legal Boundaries

- Arabic official source governs.
- Not legal advice.
- Not official translation.
- No trilingual alignment.
- No public release.
- English reference only.
- Chinese internal reference only.