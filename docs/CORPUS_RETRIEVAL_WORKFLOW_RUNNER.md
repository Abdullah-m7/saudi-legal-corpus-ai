# Corpus Retrieval Workflow Runner — Usage Guide

## Overview

A deterministic, offline workflow runner that orchestrates existing corpus
tools into one practical end-to-end workflow. Takes a query, builds a
retrieval context pack, builds a retrieval prompt pack, and optionally
checks a draft answer with the citation support checker.

**This is NOT RAG. This does NOT call an LLM. This does NOT generate legal
answers. This does NOT generate legal advice. This does NOT interpret legal
text. This does NOT verify legal correctness. This does NOT verify semantic
support. This does NOT create embeddings, semantic search, API, UI, database,
or network calls.**

It is a thin orchestration layer over existing deterministic tools.

## Workflow modes

### 1. prepare_prompt (default)

Takes a query, builds a context pack and a prompt pack, writes all artifacts
+ a workflow manifest to an output directory. Does not require a draft answer.

### 2. check_draft

Takes a query + a draft answer file, builds context + prompt packs, runs the
citation support checker against the draft, writes all artifacts + citation
check report + workflow manifest. Exits non-zero if citation check fails.

## Quick start

```bash
# Prepare prompt workflow
python3 scripts/run_retrieval_workflow.py "مجلس الإدارة" \
  --mode prepare_prompt --limit 3 --prompt-mode evidence_brief \
  --formats both --output-dir /tmp/corpus_workflow

# Check draft workflow
python3 scripts/run_retrieval_workflow.py "مجلس الإدارة" \
  --mode check_draft --draft-answer-file /tmp/draft.md \
  --limit 3 --prompt-mode cautious_answer_draft \
  --require-citation-per-paragraph --formats both \
  --output-dir /tmp/corpus_workflow_check

# Track filter
python3 scripts/run_retrieval_workflow.py "التصفية" \
  --track companies_law --limit 5 --output-dir /tmp/workflow

# Include full text
python3 scripts/run_retrieval_workflow.py "مجلس الإدارة" \
  --include-full-text --limit 3 --output-dir /tmp/workflow
```

## CLI options

- `query` — Search query (Arabic), positional, required
- `--mode` — `prepare_prompt` (default) or `check_draft`
- `--draft-answer-file PATH` — Draft answer file (required for check_draft)
- `--limit N` — Max results (default: 5)
- `--track` — Filter by track
- `--record-type` — Filter by record type
- `--prompt-mode` — `evidence_brief` (default), `cautious_answer_draft`, `citation_check`
- `--include-full-text` — Include full text_ar in records
- `--output-dir PATH` — Output directory (default: temporary directory)
- `--formats` — `json`, `markdown`, or `both` (default: both)
- `--require-citation-per-paragraph` — Require citations in every paragraph (check_draft)
- `--require-boundary-note` — Require boundary note in draft (check_draft)
- `--help` — Help

## Output artifacts

### prepare_prompt mode
- `context_pack.json` — Retrieval context pack (JSON)
- `context_pack.md` — Retrieval context pack (Markdown, if requested)
- `prompt_pack.json` — Retrieval prompt pack (JSON)
- `prompt_pack.md` — Retrieval prompt pack (Markdown, if requested)
- `workflow_manifest.json` — Workflow run manifest
- `WORKFLOW_README.md` — Human-readable summary

### check_draft mode
- All prepare_prompt artifacts
- `citation_check.json` — Citation check report (JSON)
- `citation_check.md` — Citation check report (Markdown, if requested)
- `workflow_manifest.json` includes citation check result

## Manifest fields

`workflow_version`, `mode`, `query`, `normalized_query`, `generated_at_date`,
`baseline_commit`, `output_dir`, `source_export_file`,
`source_export_record_count`, `retrieval_method`, `limit`, `filters`,
`prompt_mode`, `include_full_text`, `formats`, `artifacts`,
`draft_answer_file` (if applicable), `citation_check_result` (if applicable),
`legal_boundaries`, `limitations`, `hygiene`

## Source tools

- `scripts/build_retrieval_context_pack.py` — context pack builder
- `scripts/build_retrieval_prompt_pack.py` — prompt pack builder
- `scripts/check_citation_support.py` — citation support checker
- `scripts/search_primary_arabic_export.py` — local lexical search

## Boundaries

- Arabic official source governs
- Not legal advice
- Not official translation
- No legal interpretation by the workflow runner
- No generated legal conclusions
- No legal correctness judgment
- No semantic support verification
- No English/Chinese records
- No trilingual alignment
- No public release
- No LLM calls, no API, no network, no embeddings
- Workflow runner orchestrates deterministic local tools only
- Generated outputs are not committed to the repository

## Limitations

- The workflow prepares retrieval and prompt/citation artifacts only
- It does not produce or evaluate legal correctness
- Citation checker is mechanical ID validation only, not semantic/legal support
- repository-owner legal review active; external legal review optional for enterprise/official adoption

## Validation

```bash
make corpus-retrieval-workflow-runner-validate
```

## Smoke tests

```bash
make corpus-retrieval-workflow-runner-smoke
```