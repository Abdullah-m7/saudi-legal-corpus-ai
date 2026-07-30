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
| `data/legal_corpus_factory/` | Source data | Reusable law profile, example batch config, terminology seed (foundation scaffold; not the pattern used by the 290 other tracks) |
| `data/<law_key>_arabic_legal_llm/` | Generated | Per-track Arabic LLM-ready layer — 260 such directories, one (or more, for a law + its regulation) per track |
| `data/corpus_registry/` | Generated | `corpus_registry.json` — the authoritative machine-readable index of all 291 tracks |
| `data/corpus_unified_index/` | Generated | Flat retrieval index across every track (15,689 records) |
| `data/corpus_verification_tiers/` | Generated | Confidence-tier classification for every track's source authority |
| `data/corpus_supersession_graph/` | Generated | Explicitly-documented repeal/supersession edges between tracks |
| `data/corpus_cross_reference_graph/` | Generated | Article-to-article citation graph across the unified index |
| `data/corpus_glossary/` | Generated | Cross-law glossary of defined terms |
| `data/corpus_chunking_layer/` | Generated | Embeddings-ready text chunking over the unified index |
| `data/corpus_freshness_manifest/` | Generated | Per-track source-staleness risk flags + live-check CLI |
| `data/schema_manifest/` | Generated | JSON Schema describing every document type used in the corpus |

**Open first:** `data/official_arabic_legal_llm/` (Companies Law's governing
Arabic layer) for the flagship trilingual build, or
`data/corpus_registry/corpus_registry.json` for the full 291-track corpus.

## `sources/` — per-track official source + verified text

| Path | Kind | What it contains |
|------|------|-------------------|
| `sources/<law_key>/{law\|regulation\|annexN}/official_source/` | Source data | Article-by-article official text, cross-checked against 1-2+ official sources, with an explicit verification-tier note |
| `sources/<law_key>/{law\|regulation\|annexN}/verified/` | Generated | Verified-text records + summary, produced by that track's `scripts/gen_<law_key>_track.py` |

245 track directories today. This — not `data/legal_corpus_factory/` — is
the pattern to follow when adding a new law, implementing regulation, or
(with no precedent yet) circular.

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

Per-track scripts follow a fixed naming pattern: `gen_<law_key>_track.py`
builds a track's verified + LLM-ready layers from its `sources/` official
source JSON (278 such generators today); `validate_<law_key>_track.py`
checks it (278 today, out of 372 `validate_*.py` scripts total). The
corpus-wide derived layers (registry, unified index, verification tiers,
supersession graph, cross-reference graph, glossary, chunking layer,
freshness manifest, schema manifest) each have their own
`gen_corpus_*.py`/`validate_corpus_*.py` pair that re-scans every track.

**Open first:** `scripts/validate_legal_corpus_factory_foundation.py` for
the original foundation, or `scripts/gen_arbitration_law_track.py` +
`scripts/validate_arbitration_law_track.py` as a representative example of
the per-track pattern.

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
