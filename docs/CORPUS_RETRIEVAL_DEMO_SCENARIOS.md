# Corpus Retrieval Demo Scenarios Foundation

## Overview

A small deterministic local demo scenario layer for the retrieval workflow runner. This makes the corpus toolchain easy to demonstrate and rehearse locally using curated Arabic query scenarios.

**This is NOT RAG.**
**This does NOT call an LLM.**
**This does NOT generate legal answers.**
**This does NOT provide legal advice.**
**This does NOT interpret legal text.**
**This does NOT verify legal correctness.**
**This does NOT verify semantic support.**
**This does NOT create embeddings, semantic search, API, UI, database, or network calls.**
**This does NOT commit generated workflow outputs.**

## Files

| File | Description |
|------|-------------|
| `data/demo_scenarios/retrieval_demo_scenarios_v1.json` | 6 curated Arabic demo scenarios |
| `scripts/validate_retrieval_demo_scenarios.py` | Validator + smoke runner for all scenarios |
| `scripts/run_retrieval_demo_scenarios.py` | Helper script to run all scenarios into a temp or user dir |
| `tests/test_retrieval_demo_scenarios.py` | Tests for scenario file structure and validator |

## Scenario Count

6 scenarios.

## Scenario List

| ID | Title (AR) | Query | Track | Record Type |
|----|-----------|-------|-------|-------------|
| demo_001 | مجلس الإدارة | مجلس الإدارة | — | — |
| demo_002 | الجمعية العامة | الجمعية العامة | — | — |
| demo_003 | التصفية في نظام الشركات | التصفية | companies_law | — |
| demo_004 | أسهم الشركات المساهمة المدرجة | الأسهم | implementing_regulations_listed_joint_stock | — |
| demo_005 | النماذج | نموذج | — | form |
| demo_006 | ملحق التوكيل | التوكيل | — | appendix |

## Source Tools

- `scripts/run_retrieval_workflow.py` — retrieval workflow runner
- `scripts/search_primary_arabic_export.py` — local lexical search
- `scripts/build_retrieval_context_pack.py` — context pack builder
- `scripts/build_retrieval_prompt_pack.py` — prompt pack builder
- `scripts/check_citation_support.py` — citation support checker

## Source Data

- `data/exports/v1/primary_arabic_governing_records.jsonl` — 450 Arabic governing records

## Included Records

- Companies Law: 281 records
- Implementing Regulations (general): 95 + 4 records
- Implementing Regulations (listed joint-stock): 69 + 1 records
- Total: 450 records

## Excluded Records

- English reference records
- Chinese internal reference records
- Closure audit aggregate records

## CLI Examples

### Validate all scenarios

```bash
make corpus-retrieval-demo-scenarios-validate
```

### Run all scenarios into a temp directory

```bash
python3 scripts/run_retrieval_demo_scenarios.py
```

### Run all scenarios into a specific directory

```bash
python3 scripts/run_retrieval_demo_scenarios.py --output-dir /tmp/my_demo
```

### Run one manual workflow command

```bash
python3 scripts/run_retrieval_workflow.py "مجلس الإدارة" \
  --mode prepare_prompt --limit 3 --prompt-mode evidence_brief \
  --formats both --output-dir /tmp/corpus_demo_board
```

### Run scenario with track filter

```bash
python3 scripts/run_retrieval_workflow.py "التصفية" \
  --track companies_law --mode prepare_prompt --limit 3 \
  --prompt-mode evidence_brief --formats both \
  --output-dir /tmp/corpus_demo_liquidation
```

### Run scenario with record_type filter

```bash
python3 scripts/run_retrieval_workflow.py "نموذج" \
  --record-type form --mode prepare_prompt --limit 3 \
  --prompt-mode evidence_brief --formats both \
  --output-dir /tmp/corpus_demo_forms
```

## Generated Output Policy

- All workflow outputs go to temporary directories only.
- No generated context packs, prompt packs, or workflow manifests are committed.
- The validator runs each scenario in a fresh `tempfile.mkdtemp()` directory.
- Temporary outputs are outside the repository tree.
- The `data/demo_scenarios/` directory contains only the scenarios JSON file.

## Boundaries

- Arabic official source governs.
- Not legal advice.
- Not official translation.
- No legal interpretation.
- No generated legal conclusions.
- No legal correctness judgment.
- No semantic support verification.
- No LLM call.
- No answer generation.
- No English records.
- No Chinese records.
- No trilingual alignment.
- No public release.

## Limitations

- Demo scenarios cover representative company-law retrieval tasks only.
- Scenarios use deterministic lexical search — no semantic ranking.
- The validator confirms workflow execution and artifact presence, not legal correctness.
- This is a demonstration layer, not a production retrieval system.