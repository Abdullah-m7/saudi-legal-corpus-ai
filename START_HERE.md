# START HERE

**Multilingual, LLM-ready, official-source-based Saudi legal corpus for AI.**

A short, practical onboarding for developers, reviewers, companies, and
government / AI stakeholders. Read this first, then follow the links.

---

## What is this repository?

A **multilingual, LLM-ready, official-source-based Saudi legal corpus for AI**.
It structures Saudi laws and regulations into **auditable, machine-readable
legal layers** (canonical JSON → LLM/RAG chunks → generated human-readable
views), each validated by read-only, idempotent checks.

- The **official Arabic source governs**. English and Chinese are **reference
  layers** only.
- The **Saudi Companies Law (M/132, 1443H)** is the **first implemented law
  profile** — not the whole project identity.
- **Chinese is one language layer**, not the identity of the project.
- It can serve **government entities, AI companies and model builders,
  enterprises operating in or entering Saudi Arabia, investors, researchers,
  developers, and ordinary users**.

## What should I read first?

1. [`README.md`](README.md) — project identity, quick navigation, quick
   validation commands.
2. [`STATUS.md`](STATUS.md) — the single source of truth for current state
   (counts, what is complete, what is not).
3. [`REPOSITORY_MAP.md`](REPOSITORY_MAP.md) — what each directory contains and
   what to open first.
4. [`USE_CASES.md`](USE_CASES.md) — practical uses, without overclaiming.
5. Foundation doctrine & architecture (Arabic):
   [`docs/SOVEREIGN_LEGAL_CORPUS_FACTORY_DOCTRINE_AR.md`](docs/SOVEREIGN_LEGAL_CORPUS_FACTORY_DOCTRINE_AR.md),
   [`docs/LEGAL_CORPUS_FACTORY_ARCHITECTURE_AR.md`](docs/LEGAL_CORPUS_FACTORY_ARCHITECTURE_AR.md).

## Where are the data layers?

All canonical and reference data live under `data/` (see
[`REPOSITORY_MAP.md`](REPOSITORY_MAP.md) for the full map). The main layers:

- `data/official_arabic/` — official Arabic statutory text (user-provided,
  ingested, unverified).
- `data/official_arabic_legal_llm/` — full Arabic LLM-ready layer (281 articles).
- `data/official_english_legal_llm/` — full English LLM-ready layer (281 articles).
- `data/english_reference/` — English reference alignment (281 articles).
- `data/chinese_internal_legal_llm/` — Chinese internal candidate layer (189 records).
- `data/chinese_legal_llm/` — earlier Chinese Legal LLM layer (5 files / 23 records).
- `data/chinese_translation_sources/` — extracted Chinese source articles (14 files).
- `data/chinese_remediation_batches/` — Chinese remediation batches (P0-001..P0-005).
- `data/legal_corpus_factory/` — reusable law profile, example batch config,
  terminology seed (foundation).
- `reports/official_arabic_verification/` — OCR / manual review queue (281 entries).

## How do I validate the repository?

Everything is checked by read-only, idempotent validators. The quick suite:

```bash
make legal-corpus-factory-foundation-validate   # foundation (doctrine/schemas/profile)
make validate                                    # Book One schema + QA
make book2-validate                              # Book Two
make book3-validate                              # Book Three
make book4-validate                              # repo book4 (JSC modeled scope)
make test                                        # full pytest suite
```

The Makefile also exposes per-layer validators (Arabic, English, English
reference, Chinese layers, and each Chinese remediation batch + QA). Run
`make help` to list targets.

## What is complete now?

See [`STATUS.md`](STATUS.md) for the authoritative list. In brief:

- Arabic full LLM 281, English full LLM 281, English reference 281.
- Chinese internal candidate 189; earlier Chinese layer 5 files / 23 records;
  14 extracted Chinese source files; OCR/manual review queue 281.
- Chinese remediation **completed through P0-005**, with QA **through P0-005**.
- The reusable legal-corpus factory **foundation** (doctrine, architecture,
  schemas, one law profile, one example batch config, terminology seed).

## What is not complete yet?

- P1 / P2 / P3 remediation is **not started**.
- No **full Chinese 281 layer**; no **trilingual alignment**.
- No **public release artifacts**.
- The generic factory pipeline (generic validators, report generator, RAG/API
  export) is **future** — described, not implemented.

## What are the legal / status boundaries?

- The **official Arabic source governs**; English and Chinese are reference
  layers. Chinese is **not official, not binding, not governing**.
- **No official government publication** claim; **no official government
  adoption** claim; **no official translation** claim.
- **Not legal advice.**
- The **repository owner has a legal background (bachelor of law)** and runs
  **active repository legal review**. **External legal review is optional** for
  enterprise or official adoption and **not required for repository use**.
