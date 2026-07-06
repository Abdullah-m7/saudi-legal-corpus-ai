# Corpus Retrieval Context Pack — Usage Guide

## Overview

A deterministic, offline context pack generator that takes a query, runs the existing local lexical search, and exports top results as a structured evidence/context pack (JSON or Markdown).

**This is NOT RAG. This is NOT an answer generator. This is NOT legal advice. This is NOT legal interpretation. This is NOT semantic search. This is NOT embeddings. This is NOT an API. This is NOT a public release.**

Context packs package retrieved Arabic governing records with full provenance, making them usable for future RAG, review, QA, and prompt construction.

## Quick start

```bash
# Basic context pack (JSON)
python3 scripts/build_retrieval_context_pack.py "مجلس الإدارة"

# Limit results
python3 scripts/build_retrieval_context_pack.py "الجمعية العامة" --limit 5

# Filter by track
python3 scripts/build_retrieval_context_pack.py "التصفية" --track companies_law --limit 5

# Filter by record type
python3 scripts/build_retrieval_context_pack.py "التوكيل" --record-type appendix --limit 3

# Markdown output
python3 scripts/build_retrieval_context_pack.py "مجلس الإدارة" --format markdown

# Save to file
python3 scripts/build_retrieval_context_pack.py "مجلس الإدارة" --output /tmp/context_pack.json

# Include full text
python3 scripts/build_retrieval_context_pack.py "مجلس الإدارة" --include-full-text --limit 3
```

## CLI options

- `query` — Search query (Arabic), positional, required
- `--limit N` — Maximum results (default: 5)
- `--track` — Filter by track: `companies_law`, `implementing_regulations_general`, `implementing_regulations_listed_joint_stock`
- `--record-type` — Filter by record type: `article`, `form`, `appendix`
- `--format` — Output format: `json` or `markdown` (default: `json`)
- `--output` — Output file path (default: stdout)
- `--include-full-text` — Include full `text_ar` in each record
- `--help` — Help

## JSON output fields

Top-level:

- `pack_version` — Context pack format version (1.0)
- `query` — Original query
- `normalized_query` — Normalized query (Arabic light normalization)
- `generated_at_date` — ISO date string
- `source_search_tool` — Path to search CLI
- `source_export_file` — Path to source JSONL
- `source_export_record_count` — Total records in export (450)
- `retrieval_method` — `deterministic_lexical_search`
- `limit` — Max results requested
- `filters` — Applied filters (track, record_type)
- `total_matches` — Total matches before limit
- `returned` — Number of records returned
- `legal_boundaries` — Array of boundary strings
- `records` — Array of record objects

Each record:

- `rank` — 1-based rank
- `score` — Lexical search score
- `export_record_id` — Export record ID
- `source_track_id` — Source track
- `source_record_id` — Source record ID
- `corpus_family` — Corpus family
- `document_type` — Document type
- `record_type` — Record type (article/form/appendix)
- `language` — Always `ar`
- `governing_status` — Always `arabic_governing_text`
- `title_ar` — Arabic title
- `article_number` — Article number (if applicable)
- `record_number` — Record number (if applicable)
- `snippet` — Text snippet around match
- `text_ar` — Full text (only if `--include-full-text`)
- `source_url` — Source URL (if available)
- `source_authority` — Source authority (if available)
- `publication_date_hijri` — Hijri publication date (if available)
- `publication_date_gregorian` — Gregorian publication date (if available)
- `source_data_path` — Path to source data file
- `source_text_sha256` — SHA-256 hash of source text

## Markdown output behavior

- Arabic-friendly layout with RTL headings
- Heading with query and match count
- Boundary note section
- Metadata section (pack version, query, date, source info)
- Numbered list of retrieved records with title, score, IDs, source track, snippet, and source URL
- Full text included only when `--include-full-text` is passed

## Validation

```bash
make corpus-retrieval-context-pack-validate
```

## Smoke tests

```bash
make corpus-retrieval-context-pack-smoke
```

## Boundaries

- Arabic official source governs
- Not official translation
- Not legal advice
- No legal interpretation or conclusions
- No English records
- No Chinese records
- No trilingual alignment
- No public release
- No embeddings, no vector DB, no API, no network, no LLM calls
- Source JSONL is read-only — context pack builder does not modify it
- Context packs are retrieval packaging, not reasoning or answer generation