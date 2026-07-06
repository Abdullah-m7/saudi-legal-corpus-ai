# Corpus Citation Support Checker — Usage Guide

## Overview

A deterministic, offline citation support checker that takes a draft answer
file and a retrieval prompt pack or context pack, then mechanically checks
whether cited record IDs exist in the supplied pack.

**This checker only verifies mechanical citation presence and ID validity.
It does NOT verify that the cited record semantically supports the sentence.
It does NOT verify legal correctness. It does NOT interpret legal text. It
does NOT generate answers. It does NOT call any LLM. It does NOT provide
legal advice. It does NOT build RAG, embeddings, semantic search, API, UI,
database, or network calls.**

## Citation syntax

Accepted citation formats in draft answers:

- `[[export_record_id=<ID>]]` — cites a record by its `export_record_id`
- `[[source_record_id=<ID>]]` — cites a record by its `source_record_id`

Vague article-only citations (e.g., "Article 47") are NOT accepted as valid
unless they map to a retrieved record ID via the accepted syntax.

## Quick start

```bash
# Build a prompt pack first
python3 scripts/build_retrieval_prompt_pack.py "مجلس الإدارة" --limit 3 \
  --mode cautious_answer_draft --format json --output /tmp/prompt_pack.json

# Check a draft answer (JSON output)
python3 scripts/check_citation_support.py \
  --prompt-pack /tmp/prompt_pack.json \
  --draft-answer-file /tmp/draft.md \
  --format json

# Check with paragraph citation requirement
python3 scripts/check_citation_support.py \
  --prompt-pack /tmp/prompt_pack.json \
  --draft-answer-file /tmp/draft.md \
  --require-citation-per-paragraph

# Check with boundary note requirement
python3 scripts/check_citation_support.py \
  --prompt-pack /tmp/prompt_pack.json \
  --draft-answer-file /tmp/draft.md \
  --require-boundary-note

# Markdown output
python3 scripts/check_citation_support.py \
  --prompt-pack /tmp/prompt_pack.json \
  --draft-answer-file /tmp/draft.md \
  --format markdown

# Save to file
python3 scripts/check_citation_support.py \
  --prompt-pack /tmp/prompt_pack.json \
  --draft-answer-file /tmp/draft.md \
  --output /tmp/citation_check.json

# Use context pack instead of prompt pack
python3 scripts/check_citation_support.py \
  --context-pack /tmp/context_pack.json \
  --draft-answer-file /tmp/draft.md
```

## CLI options

- `--prompt-pack PATH` — Path to a retrieval prompt pack JSON file (optional)
- `--context-pack PATH` — Path to a retrieval context pack JSON file (optional)
- Exactly one of `--prompt-pack` or `--context-pack` is required
- `--draft-answer-file PATH` — Path to the draft answer file (required)
- `--format json|markdown` — Output format (default: json)
- `--require-citation-per-paragraph` — Require every substantive paragraph to have at least one valid citation
- `--require-boundary-note` — Require the draft to contain a boundary note phrase (e.g., "ليست استشارة قانونية", "not legal advice")
- `--output PATH` — Output file path (default: stdout)
- `--help` — Help

## Checker behavior

1. Load the prompt/context pack and extract retrieved records
2. Build allowed citation sets (export_record_id and source_record_id values)
3. Read the draft answer file
4. Extract all citations matching the accepted syntax
5. Check:
   - Citations are present
   - Every citation references a retrieved record in the supplied pack
   - No citation references records outside the supplied pack
   - All cited records are language `ar`
   - All cited records have `governing_status` = `arabic_governing_text`
   - If `--require-citation-per-paragraph`: every substantive paragraph has at least one valid citation
   - If `--require-boundary-note`: draft contains a boundary note phrase
6. Produce clear PASS/FAIL report

## Explicit limitations

- This checker only verifies mechanical citation presence and ID validity
- It does NOT verify that the cited record semantically supports the sentence
- It does NOT verify legal correctness
- It does NOT replace repository-owner legal review (active); external legal review is optional for enterprise/official adoption

## JSON output fields

Top-level:
- `checker_version` — Checker version (1.0)
- `input_pack_type` — `prompt_pack` or `context_pack`
- `input_pack_path` — Path to the input pack
- `draft_answer_file` — Path to the draft answer
- `checked_at_date` — ISO date string
- `result` — `PASS` or `FAIL`
- `limitations` — Array of limitation strings
- `legal_boundaries` — Array of boundary strings
- `citation_syntax` — Array of syntax description strings
- `retrieved_record_count` — Number of records in the pack
- `citations_found` — Total citations found in draft
- `valid_citations` — Number of valid citations
- `invalid_citations` — Number of invalid citations
- `citation_findings` — Array of per-citation finding objects
- `uncited_paragraphs` — Array of uncited paragraph objects
- `boundary_note_check` — Object with required/present/passed
- `record_language_check` — Object with all_records_arabic/passed
- `governing_status_check` — Object with all_records_arabic_governing_text/passed
- `summary` — Object with result and counts

Each citation finding:
- `citation_text` — The raw citation marker
- `citation_type` — `export_record_id` or `source_record_id`
- `cited_id` — The cited ID
- `valid` — Boolean
- `matched_record` — Matched record info (or null)
- `paragraph_index` — Paragraph index (or null)
- `message` — Human-readable message

## Markdown output

- Heading with result
- Result PASS/FAIL
- Limitations section
- Legal boundaries section
- Citation syntax section
- Summary counts
- Input info
- Invalid citations section (if any)
- Uncited paragraphs section (if any)
- Valid citations section (if any)
- Boundary note check section

## Validation

```bash
make corpus-citation-support-checker-validate
```

## Smoke tests

```bash
make corpus-citation-support-checker-smoke
```

## Boundaries

- Arabic official source governs
- Not official translation
- Not legal advice
- No legal interpretation by the checker
- No generated legal conclusions
- No semantic/legal correctness judgment
- No English records
- No Chinese records
- No trilingual alignment
- No public release
- No LLM calls, no API, no network, no embeddings
- Source files are read-only — checker does not modify them
- Mechanical citation checking only — not semantic verification