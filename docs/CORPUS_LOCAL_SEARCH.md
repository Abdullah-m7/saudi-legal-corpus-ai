# Corpus Local Lexical Search — Usage Guide

## Overview

A deterministic, offline, lexical-only search tool over the 450 Arabic governing records in the Saudi legal corpus.

**Not RAG. Not embeddings. Not an API. Not a search engine. Not legal advice.**

## Quick start

```bash
# Basic search
python3 scripts/search_primary_arabic_export.py "الشركة"

# Limit results
python3 scripts/search_primary_arabic_export.py "الشركة" --limit 5

# Filter by track
python3 scripts/search_primary_arabic_export.py "التصفية" --track companies_law
python3 scripts/search_primary_arabic_export.py "التصفية" --track implementing_regulations_general
python3 scripts/search_primary_arabic_export.py "الاندماج" --track implementing_regulations_listed_joint_stock

# Filter by record type
python3 scripts/search_primary_arabic_export.py "الشركة" --record-type article
python3 scripts/search_primary_arabic_export.py "نموذج" --record-type form
python3 scripts/search_primary_arabic_export.py "ملحق" --record-type appendix

# JSON output (machine-readable)
python3 scripts/search_primary_arabic_export.py "الجمعية العامة" --json

# Show full text
python3 scripts/search_primary_arabic_export.py "مجلس الإدارة" --show-text --limit 3
```

## CLI options

| Option | Description | Default |
|--------|-------------|---------|
| `query` | Search query (Arabic) | Required |
| `--limit N` | Maximum results | 10 |
| `--track` | Filter by track | All tracks |
| `--record-type` | Filter by type (article/form/appendix) | All types |
| `--json` | JSON output | Off |
| `--show-text` | Show full text_ar | Off |
| `--help` | Help | — |

## Search behavior

- **Source:** `data/exports/v1/primary_arabic_governing_records.jsonl` (450 records)
- **Search fields:** `text_ar`, `title_ar`, `article_ordinal_ar`
- **Ranking:** Deterministic lexical scoring:
  - Exact phrase match in text: +100
  - Exact phrase match in title: +50
  - Individual term in text: +10 per term
  - Individual term in title: +15 per term
  - All terms present in text: +25 bonus
  - All terms present in title: +20 bonus
  - Stable tie-break by `export_record_id` (ascending)
- **Arabic normalization** (search matching only, does not alter stored text):
  - Removes tatweel (ـ)
  - Normalizes alef forms (أ إ آ → ا)
  - Normalizes ya (ى → ي)
  - Normalizes ta marbuta (ة → ه)
  - Removes diacritics (harakat)

## Output format

### Human-readable (default)

```
Query: الشركة
Total matches: 371
Showing: 3 (limit: 3)

─── 1 ───
  Score:       175.0
  Record ID:   export-cl-art-002
  Track:       companies_law
  Source ID:   oa-llm-companies-art-002
  Type:        article
  Title:       تعريف الشركة
  Article:     2
  Snippet:     الشركة كيان قانوني يؤسس وفقًا...
```

### JSON (`--json`)

```json
{
  "query": "الشركة",
  "normalized_query": "الشركه",
  "total_matches": 371,
  "returned": 3,
  "results": [...]
}
```

## Validation

```bash
make corpus-local-search-validate
```

## Boundaries

- Arabic official source governs
- Not official translation
- Not legal advice
- No legal interpretation or conclusions
- No English records searched
- No Chinese records searched
- No trilingual alignment
- No public release
- No embeddings, no vector DB, no API, no network
- Source JSONL is read-only — search does not modify it