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
- The **Saudi Companies Law (M/132, 1443H)** was the **first implemented law
  profile**, and remains the only law with full Arabic + English + Chinese
  layers. Since then the corpus has grown into a **291-track** collection of
  Saudi laws, implementing regulations, and annexes (each an Arabic-only
  "track" — see below), spanning companies, labor, civil transactions,
  judiciary, capital markets, tax, real estate, IP, and many other subject
  areas. The live, authoritative list of every track is
  [`data/corpus_registry/corpus_registry.json`](data/corpus_registry/corpus_registry.json)
  — **not** the prose counts elsewhere in this file or in `README.md`, which
  describe the original single-law build in depth and are not repeated here.
- **Chinese is one language layer**, not the identity of the project.
- It can serve **government entities, AI companies and model builders,
  enterprises operating in or entering Saudi Arabia, investors, researchers,
  developers, and ordinary users**.

## What is a "track", and how is one added?

Beyond the Companies Law's full 3-language pipeline, every other law/
regulation/annex is added as a single-language (Arabic-governing-only)
**track** — the repository's actual day-to-day unit of work since the
corpus grew past its original single-law scope:

1. An official-source JSON is authored under
   `sources/<law_key>/{law|regulation|annexN}/official_source/`, article by
   article, from at least one official source (Ministry of Justice legal
   portal, `laws.boe.gov.sa`, the issuing authority's own site, or the Umm
   Al-Qura Gazette), cross-checked against a second independent source where
   possible, with an explicit verification-tier note. **No article is ever
   guessed, translated, paraphrased, or reconstructed from a lower-quality
   source when a better one is reachable** — several candidate tracks are
   deliberately left unbuilt in
   [`reports/coverage_gap_map/`](reports/coverage_gap_map/COVERAGE_GAP_MAP_AR.md)
   because their citation or text could not be verified to this standard.
2. `scripts/gen_<law_key>_track.py` deterministically builds the verified
   layer (`sources/.../verified/`) and the LLM-ready layer
   (`data/<law_key>_arabic_legal_llm/`) from that source JSON.
3. `scripts/validate_<law_key>_track.py` + a `make <law-key>-track-validate`
   target lock the track's article counts, text-hash consistency, and
   OCR/formatting hygiene.
4. The track is wired into nine shared corpus-wide layers (unified retrieval
   index, registry, verification tiers, supersession/repeal graph,
   cross-reference graph, glossary, chunking layer, freshness manifest,
   schema manifest) via the corresponding `scripts/gen_corpus_*.py`
   generators, then re-validated end to end with `make qa-gate`.

This is the pattern to follow for any new law, implementing regulation, or
similar instrument — including a future first "تعميم" (circular) track,
which does not have a precedent in the corpus yet.

> **Repository name:** `saudi-legal-corpus-ai` (former name:
> `saudi-companies-law-ar-zh-llm`). The GitHub rename is done manually — see
> [`REPOSITORY_RENAME.md`](REPOSITORY_RENAME.md).

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
[`REPOSITORY_MAP.md`](REPOSITORY_MAP.md) for the full map).

**The Companies Law's full 3-language layers** (the original, most deeply
documented build — see `README.md`/`STATUS.md` for the complete history):

- `data/official_arabic/` — official Arabic statutory text (user-provided,
  ingested, unverified).
- `data/official_arabic_legal_llm/` — full Arabic LLM-ready layer (281 articles).
- `data/official_english_legal_llm/` — full English LLM-ready layer (281 articles).
- `data/english_reference/` — English reference alignment (281 articles).
- `data/chinese_internal_legal_llm/` — Chinese internal candidate layer (189 records).
- `data/chinese_legal_llm/` — earlier Chinese Legal LLM layer (5 files / 23 records).
- `data/chinese_translation_sources/` — extracted Chinese source articles (14 files).
- `data/chinese_remediation_batches/` — Chinese remediation batches (P0-001..P0-005).
- `reports/official_arabic_verification/` — OCR / manual review queue (281 entries).

**The rest of the corpus (290 other tracks, Arabic-governing-only)**:

- `data/<law_key>_arabic_legal_llm/` — one directory per track's LLM-ready
  layer (e.g. `data/arbitration_arabic_legal_llm/`, `data/labor_arabic_legal_llm/`);
  260 such directories today (some hold more than one track, e.g. a law plus
  its implementing regulation).
- `sources/<law_key>/` — one directory per track's official source +
  verified-text layers (245 directories today).
- `data/corpus_registry/corpus_registry.json` — the single machine-readable
  index of all 291 tracks: status, record counts, source authority, and data
  paths for each. **This is the authoritative current count**, not any
  number written in prose elsewhere.
- `data/corpus_unified_index/` — one flat retrieval index across every
  track (15,689 records at last count).
- `data/corpus_verification_tiers/`, `data/corpus_supersession_graph/`,
  `data/corpus_cross_reference_graph/`, `data/corpus_glossary/`,
  `data/corpus_chunking_layer/`, `data/corpus_freshness_manifest/`,
  `data/schema_manifest/` — corpus-wide derived layers built from all tracks.
- `reports/coverage_gap_map/` — a research-only planning document of Saudi
  laws/regulations **not yet** in the corpus, ranked by priority, each
  flagged with how build-ready its citation/text currently is. This is the
  starting point for identifying genuinely missing laws — most of its
  earlier "ready to build" candidates have since been built; what remains
  mostly needs a fresh, dedicated sourcing pass, not a mechanical copy.
- `data/legal_corpus_factory/` — reusable law profile, example batch config,
  terminology seed (the original foundation scaffold; not the pattern
  actually used by the 290 later tracks — see "What is a 'track'" above).

## How do I validate the repository?

Everything is checked by read-only, idempotent validators. The quick suite:

```bash
make legal-corpus-factory-foundation-validate   # foundation (doctrine/schemas/profile)
make validate                                    # Book One schema + QA
make book2-validate                              # Book Two
make book3-validate                              # Book Three
make book4-validate                              # repo book4 (JSC modeled scope)
make <law-key>-track-validate                    # any one of the 291 tracks, e.g. make arbitration-law-track-validate
make qa-gate                                     # every validator (372 today) + generator-idempotence check
make test                                        # full pytest suite
```

The Makefile exposes a `-track-validate` target for every track (run
`make help` to list them, or read `data/corpus_registry/corpus_registry.json`
for each track's exact `validator_targets`).

## What is complete now?

See [`STATUS.md`](STATUS.md) for the Companies Law's detailed history, and
`data/corpus_registry/corpus_registry.json` for the live, authoritative state
of the full corpus. In brief:

- **Companies Law (M/132, 1443H)** — the only track with full Arabic +
  English + Chinese layers: Arabic full LLM 281, English full LLM 281,
  English reference 281, Chinese internal candidate 189, earlier Chinese
  layer 5 files / 23 records, 14 extracted Chinese source files,
  OCR/manual review queue 281 entries. Chinese remediation **completed
  through the full P0 → P1 → P2 → P3 program**, with matching QA.
- **291 tracks total** across the rest of the corpus (Arabic-governing-only),
  covering the large majority of Saudi statutory law and its implementing
  regulations — companies, labor, civil transactions, judiciary/procedure,
  capital markets, banking, tax (VAT/income tax/zakat), real estate, IP,
  criminal/procedural codes, and more. 15,689 unified retrieval-index
  records across all tracks combined.
- The reusable legal-corpus factory **foundation** (doctrine, architecture,
  schemas, one law profile, one example batch config, terminology seed) —
  the scaffold the Companies Law build used; the 290 other tracks instead
  follow the simpler per-track pattern described above.

## What is not complete yet?

- No **full Companies-Law-style trilingual build** for any track besides the
  Companies Law itself — every other track is Arabic-only.
- **No circulars (تعاميم)** in the corpus at all yet — a category with no
  precedent; the first one would need to establish its own track pattern.
- A documented set of **candidate laws/regulations not yet in the corpus** —
  see `reports/coverage_gap_map/COVERAGE_GAP_MAP_AR.md`; most require a
  fresh sourcing/verification pass (unresolved decree citations, OCR-damaged
  or paywalled sources, or no dedicated official-portal page found yet), not
  a mechanical build.
- No **public release artifacts**.
- The generic factory pipeline (generic validators, report generator, RAG/API
  export) described in `data/legal_corpus_factory/` is **future** — the
  per-track pattern above is what is actually implemented and used today.

## What are the legal / status boundaries?

- The **official Arabic source governs**; English and Chinese are reference
  layers. Chinese is **not official, not binding, not governing**.
- **No official government publication** claim; **no official government
  adoption** claim; **no official translation** claim.
- **Not legal advice.**
- The **repository owner has a legal background (bachelor of law)** and runs
  **active repository legal review**. **External legal review is optional** for
  enterprise or official adoption and **not required for repository use**.
