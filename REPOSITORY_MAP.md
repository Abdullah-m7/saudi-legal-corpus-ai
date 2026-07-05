# REPOSITORY MAP

How this repository is organized, and what to open first. This map describes
**only existing paths**. For current counts and completion state see
[`STATUS.md`](STATUS.md); for onboarding see [`START_HERE.md`](START_HERE.md).

**Identity:** a multilingual, LLM-ready, official-source-based Saudi legal
corpus for AI. The official Arabic source governs; English and Chinese are
reference layers. Chinese is not official, not binding, not governing. Not
legal advice.

---

## Top level

| Path | Kind | What it is | Open first |
|------|------|------------|------------|
| `README.md` | Documentation | Project identity, navigation, quick validation | Yes |
| `START_HERE.md` | Documentation | Onboarding for developers/reviewers/stakeholders | Yes |
| `STATUS.md` | Documentation | Single source of truth for current state | Yes |
| `USE_CASES.md` | Documentation | Practical uses without overclaiming | — |
| `REPOSITORY_RENAME.md` | Documentation | Repository rename note (`saudi-legal-corpus-ai`; former `saudi-companies-law-ar-zh-llm`) + manual steps | — |
| `NOTICE.md` | Documentation | Legal notice / non-official-status disclaimer | — |
| `LICENSE` | Documentation | MIT license for source code | — |
| `Makefile` | Validator/build | All validation and build targets (`make help`) | Yes |
| `pyproject.toml` | Source | Package metadata + optional extras | — |

## `data/` — source data + generated LLM layers

Source and reference data. Canonical JSON is authored first; LLM/RAG chunks are
generated from it. This is the heart of the corpus.

| Path | Kind | What it contains |
|------|------|------------------|
| `data/articles/` | Source data | Canonical article JSON (+ generated `*.jsonl` chunks) |
| `data/metadata/` | Source data | Work scope, disclaimers, source provenance |
| `data/glossary/` | Source data | Validated Arabic–Chinese legal terminology |
| `data/coverage/` | Source data | Coverage matrices per book |
| `data/qa/` | Generated/QA | Known issues / open QA items |
| `data/official_arabic/` | Source data | Official Arabic statutory text (user-provided, ingested unverified) |
| `data/official_arabic_legal_llm/` | Generated | Full Arabic LLM-ready layer (281 articles) |
| `data/arabic_legal_llm/` | Generated | Arabic LLM-ready layer (per book/section) |
| `data/official_english_legal_llm/` | Generated | Full English LLM-ready layer (281 articles) |
| `data/english_legal_llm/` | Generated | English LLM-ready layer (per book/section) |
| `data/english_reference/` | Reference | English reference alignment (281 articles) |
| `data/chinese_internal_legal_llm/` | Reference | Chinese internal candidate layer (189 records) |
| `data/chinese_legal_llm/` | Reference | Earlier Chinese Legal LLM layer (5 files / 23 records) |
| `data/chinese_translation_sources/` | Source data | Extracted Chinese source articles (14 files) |
| `data/chinese_remediation_batches/` | Generated/QA | Chinese remediation batches (P0-001..P0-005) |
| `data/extracted/` | Source data | Text extracted from source PDFs |
| `data/legal_corpus_factory/` | Source data | Reusable law profile, example batch config, terminology seed (foundation) |

**Open first:** `data/official_arabic_legal_llm/` (governing Arabic layer) and
`data/legal_corpus_factory/law_profiles/` (the Companies Law profile).

## `docs/` — architecture & doctrine documentation

| Path | Kind | What it contains |
|------|------|------------------|
| `docs/SOVEREIGN_LEGAL_CORPUS_FACTORY_DOCTRINE_AR.md` | Documentation | Arabic doctrine: identity, governing source, review model |
| `docs/LEGAL_CORPUS_FACTORY_ARCHITECTURE_AR.md` | Documentation | Arabic architecture: data layers, profiles, validation, RAG readiness |
| `docs/REPOSITORY_UX_PRINCIPLES_AR.md` | Documentation | Arabic repository UX principles |
| `docs/official_arabic_text/` | Source data | Official Arabic text working notes |
| `docs/official_english_source/` | Source data | Official English guidance source notes |
| `docs/book4_preflight/` | Documentation | repo book4 preflight notes |

**Open first:** the doctrine and architecture files above.

## `schemas/` — JSON Schemas

| Path | Kind | What it contains |
|------|------|------------------|
| `schemas/*.schema.json` | Schema | Per-layer JSON Schemas (article, glossary, coverage, LLM layers) |
| `schemas/legal_corpus_factory/` | Schema | Reusable `law_profile`, `batch_config`, `provenance_passport` schemas |

**Open first:** `schemas/legal_corpus_factory/law_profile.schema.json`.

## `scripts/` — CLI entry points & validators

Python entry points: generators (`gen_*`, `build_*`), extractors, renderers, and
**read-only validators** (`validate_*`). Each Makefile target invokes one of
these. Validators are read-only and idempotent — they never mutate corpus data.

**Open first:** `scripts/validate_legal_corpus_factory_foundation.py`.

## `tests/` — pytest suite

Read-only tests locking schema conformance, coverage, terminology, counts, and
the invariants of each layer and remediation batch. Run with `make test`.

## `reports/` — generated QA & verification reports

| Path | Kind | What it contains |
|------|------|------------------|
| `reports/chinese_translation_review/` | Generated/QA | Chinese remediation + QA reports (JSON + Arabic MD) |
| `reports/official_arabic_verification/` | Generated/QA | Official Arabic verification + OCR/manual review queue (281 entries) |

## Other tracked directories

| Path | Kind | What it contains |
|------|------|------------------|
| `content/` | Generated | Generated Markdown books (Arabic, Chinese, bilingual) + notes |
| `templates/` | Source | HTML/CSS templates for rendered views |
| `src/saudi_law_corpus/` | Source | Loader, validators, renderers, QA rules (stdlib-first) |
| `inputs/` | Source data | Reference source PDFs (design artifacts, not canonical) |
| `dist/` | Generated | Build output (HTML/PDF) — generated, git-ignored |

## Makefile targets

Run `make help` for the full list. The most useful:

| Target | What it validates / builds |
|--------|----------------------------|
| `make legal-corpus-factory-foundation-validate` | Factory foundation (doctrine/schemas/profile/config/seed) |
| `make validate` / `make book1-validate` | Book One schema + legal-translation QA |
| `make book2-validate` / `make book3-validate` / `make book4-validate` | Books Two / Three / repo book4 |
| `make arabic-legal-llm-validate` | Arabic LLM-ready layer |
| `make english-reference-validate` / `make english-legal-llm-validate` | English reference / English LLM layer |
| `make chinese-legal-llm-validate` | Chinese Legal LLM layer |
| `make chinese-remediation-batch-p0-00X-validate` (+ `-qa-validate`) | Chinese remediation batches P0-001..P0-005 and their QA |
| `make test` | Full pytest suite |
