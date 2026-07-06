# Corpus Retrieval Prompt Pack — Usage Guide

## Overview

A deterministic, offline prompt pack generator that takes a query, runs the
existing local lexical search via the retrieval context pack builder, and
emits a safe, source-grounded prompt template for future LLM/RAG use.

**This tool builds prompt packs only. It does NOT execute prompts. It does NOT
call any model. It does NOT produce final legal answers. It does NOT generate
legal advice. It does NOT interpret legal text. It does NOT create RAG,
embeddings, semantic search, API, UI, database, or network calls.**

## Quick start

```bash
# Basic prompt pack (JSON, evidence_brief mode)
python3 scripts/build_retrieval_prompt_pack.py "مجلس الإدارة"

# Limit results
python3 scripts/build_retrieval_prompt_pack.py "الجمعية العامة" --limit 5

# Filter by track
python3 scripts/build_retrieval_prompt_pack.py "التصفية" --track companies_law --limit 5

# Filter by record type
python3 scripts/build_retrieval_prompt_pack.py "التوكيل" --record-type appendix --limit 1

# Different prompt mode
python3 scripts/build_retrieval_prompt_pack.py "مجلس الإدارة" --mode cautious_answer_draft
python3 scripts/build_retrieval_prompt_pack.py "مجلس الإدارة" --mode citation_check

# Markdown output
python3 scripts/build_retrieval_prompt_pack.py "مجلس الإدارة" --format markdown

# Save to file
python3 scripts/build_retrieval_prompt_pack.py "مجلس الإدارة" --output /tmp/prompt_pack.json

# Include full text in records
python3 scripts/build_retrieval_prompt_pack.py "مجلس الإدارة" --include-full-text --limit 3
```

## CLI options

- `query` — Search query (Arabic), positional, required
- `--limit N` — Maximum results (default: 5)
- `--track` — Filter by track: `companies_law`, `implementing_regulations_general`, `implementing_regulations_listed_joint_stock`
- `--record-type` — Filter by record type: `article`, `form`, `appendix`
- `--mode` — Prompt mode: `evidence_brief` (default), `cautious_answer_draft`, `citation_check`
- `--format` — Output format: `json` or `markdown` (default: `json`)
- `--output` — Output file path (default: stdout)
- `--include-full-text` — Include full `text_ar` in each record
- `--draft-answer-file` — Path to draft answer file (for citation_check mode; not executed in this stage)
- `--help` — Help

## Prompt modes

### 1. evidence_brief (default)

Creates a prompt asking a future LLM to organize retrieved provisions into an
evidence brief. Strict rules:
- Use only provided retrieved records
- Do not add outside law
- Do not invent article numbers
- Do not give legal advice
- Do not state final legal conclusions
- If records are insufficient, say the retrieved context is insufficient
- Cite every factual/legal statement to retrieved record IDs
- Arabic source governs

### 2. cautious_answer_draft

Creates a prompt asking a future LLM to draft a cautious, citation-grounded
informational answer. Strict rules:
- Must begin with a boundary note
- Must not say "you should" as legal instruction
- Must not advise litigation/compliance decisions
- Must not replace lawyer/legal reviewer
- Must cite retrieved record IDs for every legal statement
- Must identify uncertainty and insufficiency
- Must not use English/Chinese records
- Must not rely on model memory

### 3. citation_check

Creates a prompt asking a future LLM to check whether a proposed answer is
supported by retrieved records. In this stage, the mode produces the prompt
template only — no model is called, no answer is checked. The
`--draft-answer-file` option is accepted but not executed.

## JSON output fields

Top-level:
- `prompt_pack_version` — Prompt pack format version (1.0)
- `query` — Original query
- `normalized_query` — Normalized query (Arabic light normalization)
- `mode` — Prompt mode
- `generated_at_date` — ISO date string
- `source_context_pack_tool` — Path to context pack builder
- `source_search_tool` — Path to search CLI
- `source_export_file` — Path to source JSONL
- `source_export_record_count` — Total records in export (450)
- `retrieval_method` — `deterministic_lexical_search`
- `limit` — Max results requested
- `filters` — Applied filters (track, record_type)
- `total_matches` — Total matches before limit
- `returned` — Number of records returned
- `legal_boundaries` — Array of boundary strings
- `prompt_policy` — Object with policy flags
- `retrieved_records` — Array of record objects
- `prompt_text` — The generated prompt template text

Each retrieved record includes: `rank`, `score`, `export_record_id`,
`source_track_id`, `source_record_id`, `record_type`, `language`,
`governing_status`, `title_ar`, `article_number`/`record_number` (if available),
`snippet`, `text_ar` (only with `--include-full-text`), `source_url`,
`source_authority`, `source_data_path`, `source_text_sha256`.

## prompt_policy fields

- `use_only_retrieved_records`: true
- `cite_every_legal_statement`: true
- `no_legal_advice`: true
- `no_official_translation`: true
- `no_legal_interpretation_by_tool`: true
- `no_generated_legal_conclusions_by_tool`: true
- `no_external_sources`: true
- `insufficient_context_rule`: true
- `Arabic official source governs`: true
- `repository-owner legal review active; external legal review optional for enterprise/official adoption`: true

## Markdown output behavior

- Arabic-friendly layout with RTL headings
- Heading with query, mode, and match count
- Not-a-prompt note prominently displayed
- Boundary section
- Prompt policy section
- Retrieved records section with metadata and snippets
- Prompt text section in a code block
- Reminder that this is a prompt pack only

## Validation

```bash
make corpus-retrieval-prompt-pack-validate
```

## Smoke tests

```bash
make corpus-retrieval-prompt-pack-smoke
```

## Boundaries

- Arabic official source governs
- Not official translation
- Not legal advice
- No legal interpretation or conclusions by the tool
- No English records
- No Chinese records
- No trilingual alignment
- No public release
- No embeddings, no vector DB, no API, no network, no LLM calls
- Source JSONL is read-only — prompt pack builder does not modify it
- Prompt packs are prompt construction only — no model execution, no answer generation