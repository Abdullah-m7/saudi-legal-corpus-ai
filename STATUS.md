# STATUS

Single source of truth for the current repository state. When counts or
completion change, update this file.

**Identity:** a multilingual, LLM-ready, official-source-based Saudi legal
corpus for AI. The **official Arabic source governs**; English and Chinese are
**reference layers**.

---

## Repository name

- **Current name:** `saudi-legal-corpus-ai` — **former name:**
  `saudi-companies-law-ar-zh-llm`. The GitHub rename is performed manually; see
  [`REPOSITORY_RENAME.md`](REPOSITORY_RENAME.md).

## Baseline

- **Baseline `main` commit:** `0a2e5c3e6457009ddf1d0ba2fb4d669091317ced`
- **First implemented law profile:** Saudi Companies Law (M/132, 1443H) — the
  **first** implemented law profile, **not** the whole project identity.

## Layer counts (current)

| Layer | Count |
|-------|-------|
| Arabic full LLM | **281** |
| English full LLM | **281** |
| English reference | **281** |
| Chinese internal candidate | **189** |
| Old Chinese Legal LLM | **5 files / 23 records** |
| Chinese source extracted files | **14** |
| OCR / manual review queue | **281** |

## Remediation & QA progress

- Chinese remediation: **completed through P0-005**.
- Chinese remediation QA: **completed through P0-005**.
- **P1-001 (first P1 batch): remediation + QA completed** — 20 articles across Babs 1–2,
  retranslated from the official Arabic governing text; article-by-article QA result
  **PASS (20/20, no minor fixes)**.
- **P1-002: remediation + QA completed** — 20 articles across Babs 3–6, retranslated from the
  official Arabic governing text; article-by-article QA result **PASS (20/20, no minor fixes)**.
- **P1-003: remediation + QA completed** — 20 articles across Babs 6–8 and 10, retranslated from the
  official Arabic governing text; article-by-article QA result **PASS (20/20, no minor fixes)**.
- **P1-004: remediation + QA completed** — 16 articles across Babs 10, 12, 13 and 14, retranslated from
  the official Arabic governing text; article-by-article QA result **PASS (16/16, no minor fixes)**.
- **All P1 batches (P1-001..P1-004): remediation + QA completed** (each PASS, no minor fixes).
- **P2-001 (first P2 batch): remediation + QA completed** — 20 articles across Babs 1, 2 and 4,
  internal Chinese expanded from the official Arabic governing text (the prior candidate existed but was
  condensed); article-by-article QA result **PASS (20/20, no minor fixes)**.
- **P2-002 (second P2 batch): remediation + QA completed** — 20 articles across Babs 4, 5, 6 and 7,
  internal Chinese expanded from the official Arabic governing text (the prior candidate existed but was
  condensed); article-by-article QA result **PASS (20/20, no minor fixes)**.
- **P2-003: remediation + QA completed** — 20 articles across Babs 7, 8, 9 and 10, internal Chinese
  expanded from the official Arabic governing text (the prior candidate existed but was condensed);
  article-by-article QA result **PASS (20/20, no minor fixes)**.
- **P2-004: remediation + QA completed** — 20 articles across Babs 10, 11 and 12, internal Chinese
  expanded from the official Arabic governing text (the prior candidate existed but was condensed);
  article-by-article QA result **PASS (20/20, no minor fixes)**.
- **P2-005: remediation + QA completed** — 15 articles across Babs 12, 13 and 14, internal Chinese
  expanded from the official Arabic governing text (the prior candidate existed but was condensed);
  article-by-article QA result **PASS (15/15, no minor fixes)**.
- **All P2 batches (P2-001..P2-005): remediation + QA completed** (each PASS, no minor fixes) — **the
  full P2 expansion track is complete**.
- **P3-CONF-001 (final P3 confirmation batch): confirmation + QA completed** — 18 articles across Babs 2
  and 3, whose existing internal Chinese candidate is **retained verbatim as internal reference** (P3 is
  a confirmation/retain track, not expansion: no new Chinese text generated, nothing modified); each
  retention re-confirms the 189 semantic-QA finding (alignment high, near-full completeness) and the P3
  backlog finding; article-by-article QA result **PASS (18/18, no minor fixes)**.
- **The full Chinese remediation program (P0 → P1 → P2 → P3) is complete** — every backlog article is
  remediated, expanded, or confirmed-and-retained as internal reference, each with passing QA.
- **Closure audit completed** — a consolidated closure audit JSON, Arabic report, read-only
  validator, tests, and `make chinese-remediation-program-closure-validate` target verify that all
  281 articles across 15 batches (P0×5 + P1×4 + P2×5 + P3×1) are implemented with QA_PASS, no
  missing/duplicate articles, no prohibited content. See
  [`reports/chinese_translation_review/chinese_remediation_program_closure_audit.json`] and
  [`reports/chinese_translation_review/CHINESE_REMEDIATION_PROGRAM_CLOSURE_AUDIT_AR.md`].

## Not yet created

- **Full Chinese 281 layer: not created.**
- **Trilingual alignment: not created.**
- **Public release: not created.**

## Implementing regulations

- **Implementing regulations intake scaffold created** — a clean scaffold for future
  Arabic official source intake of the Implementing Regulations of the Saudi Companies
  Law (M/132, 1443H), as a **separate corpus track** from the Companies Law. No Arabic
  text ingested, no English/Chinese text generated, no trilingual alignment, no public
  release. Arabic governs; not official/binding/governing; not legal advice. See
  [`data/implementing_regulations/intake_scaffold.json`] and
  [`reports/implementing_regulations/IMPLEMENTING_REGULATIONS_INTAKE_SCAFFOLD_AR.md`].
- **Listed joint-stock implementing regulation Arabic source intake completed** — 69 articles
  across 14 chapters + appendix, extracted from the official Umm Al-Qura gazette
  (uqn.gov.sa/decisions-and-regulations/4001295), published 1448-1-18 AH / 03-07-2026,
  issued by the Capital Market Authority board under Companies Law M/132 (1443H). This is a
  **specialized** regulation for listed joint-stock companies only, NOT a general implementing
  regulation. No English/Chinese text generated; no trilingual alignment; no public release.
  Arabic governs; not official/binding/governing; not legal advice. See
  [`data/implementing_regulations/listed_joint_stock/listed_joint_stock_implementing_regulation_arabic_source.json`] and
  [`reports/implementing_regulations/LISTED_JOINT_STOCK_ARABIC_SOURCE_INTAKE_AR.md`]. Validate:
  `make implementing-regulations-listed-jsc-arabic-source-validate`.
- **General implementing regulations Arabic source intake completed** — 95 articles
  across 7 chapters + 4 official forms, extracted from the official Umm Al-Qura gazette
  (uqn.gov.sa/details?p=21325), published 1444-6-25 AH / 18-01-2023, under Companies Law
  M/132 (1443H). This is the **general** implementing regulation covering all company
  forms (general provisions, unlisted joint-stock, LLC, non-profit, professional
  companies, transformation/merger/division, final provisions). The listed joint-stock
  sub-track is a separate specialized regulation. No English/Chinese text generated; no
  trilingual alignment; no public release. Arabic governs; not official/binding/governing;
  not legal advice. See
  [`data/implementing_regulations/general/general_implementing_regulations_arabic_source.json`] and
  [`reports/implementing_regulations/GENERAL_IMPLEMENTING_REGULATIONS_ARABIC_SOURCE_INTAKE_AR.md`]. Validate:
  `make implementing-regulations-general-arabic-source-validate`.
- **General implementing regulations Arabic Legal LLM layer completed** — 95 article
  records across 7 chapters + 4 official form records, structured from the general
  implementing regulation Arabic source intake. official_text_ar preserved verbatim
  from the source; deterministic metadata per record (record_id, corpus_track,
  regulation_scope, chapter_number, chapter_title_ar, article_number, article_ordinal_ar,
  article_title_ar, official_text_hash, legal_status_boundaries, source_manifest_hash).
  Articles and forms in separate JSON files. No English/Chinese text generated; no
  trilingual alignment; no public release. Arabic governs; not official/binding/governing;
  not legal advice. Companies Law corpus and Chinese remediation program unchanged.
  Listed joint-stock sub-track is separate. See
  [`data/implementing_regulations/general/general_implementing_regulations_arabic_legal_llm.json`] and
  [`reports/implementing_regulations/GENERAL_IMPLEMENTING_REGULATIONS_ARABIC_LEGAL_LLM_LAYER_REPORT.txt`]. Validate:
  `make implementing-regulations-general-arabic-legal-llm-validate`.
- **Listed joint-stock implementing regulation Arabic Legal LLM layer completed** — 69
  article records + 1 appendix record, structured from the listed joint-stock regulation
  Arabic source intake. Specialized scope: listed joint-stock companies only (NOT a general
  implementing regulation). official_text_ar preserved verbatim from the source; deterministic
  metadata per record (record_id, corpus_track, regulation_scope, issuing_authority,
  legal_basis, article_number, article_ordinal_ar, article_title_ar, official_text_hash,
  legal_status_boundaries, source_manifest_hash). Articles and appendix in separate JSON
  files. No English/Chinese text generated; no trilingual alignment; no public release.
  Arabic governs; not official/binding/governing; not legal advice. Companies Law corpus
  and Chinese remediation program unchanged. General implementing regulations track is
  separate. See
  [`data/implementing_regulations/listed_joint_stock/listed_joint_stock_implementing_regulation_arabic_legal_llm.json`] and
  [`reports/implementing_regulations/LISTED_JOINT_STOCK_ARABIC_LEGAL_LLM_LAYER_REPORT.txt`]. Validate:
  `make implementing-regulations-listed-jsc-arabic-legal-llm-validate`.
- **Implementing regulations Arabic program closure audit completed** — verifies both
  tracks (general: 95 articles + 4 forms; listed joint-stock: 69 articles + 1 appendix)
  are complete, all hashes match source intake, record IDs sequential and unique, tracks
  separate, listed joint-stock is specialized (not general), Arabic governs, no
  English/Chinese/trilingual/public release, Companies Law corpus and Chinese remediation
  unchanged. See
  [`reports/implementing_regulations/implementing_regulations_arabic_program_closure_audit.json`] and
  [`reports/implementing_regulations/IMPLEMENTING_REGULATIONS_ARABIC_PROGRAM_CLOSURE_AUDIT_AR.md`]. Validate:
  `make implementing-regulations-arabic-program-closure-validate`.
- **Corpus registry index foundation completed** — a canonical, machine-readable
  registry summarizing all completed tracks (companies law 281 articles Arabic +
  281 English + Chinese remediation 281; general IR 95 articles + 4 forms; listed
  JSC 69 articles + 1 appendix; closure audit 169 total records; **PDPL law 43 +
  PDPL implementing regulation 38 + Investment law 16 + Investment implementing
  regulation 37 + Civil Transactions Law 721 + GTPL 99 (+99 English reference)**) with counts, paths, statuses, language layers,
  boundaries, and validation targets. **10 tracks; primary Arabic governing 1404; reference 380; registry-counted
  2065.** PDPL and Investment Arabic tracks are **verified against official
  published text** (SDAIA / MISA). The registry also records the unified retrieval
  index (1235 records) as a projection (not added to totals). See
  [`data/corpus_registry/corpus_registry.json`] and
  [`reports/corpus_registry/CORPUS_REGISTRY_INDEX_FOUNDATION_AR.md`]. Validate:
  `make corpus-registry-validate`.

- **Corpus export (v1):** 450 primary Arabic governing records in JSONL format
  (Companies Law 281 + general IR 95+4 + listed JSC 69+1). Excludes English,
  Chinese, and closure aggregate. See
  [`data/exports/v1/primary_arabic_governing_records.jsonl`]. Validate:
  `make corpus-export-primary-arabic-validate`.

- **Local lexical search:** Deterministic, offline CLI search over the 450
  Arabic governing records. No embeddings, no API, no network. Usage:
  `python3 scripts/search_primary_arabic_export.py "الشركة"`. See
  [`docs/CORPUS_LOCAL_SEARCH.md`]. Validate:
  `make corpus-local-search-validate`.

- **Local search evaluation fixtures:** 10 deterministic Arabic query fixtures
  for regression testing of the local lexical search. Broad terms, legal
  phrases, track/record-type filters, JSON output, normalization, and
  no-result checks. See
  [`docs/CORPUS_LOCAL_SEARCH_EVAL.md`]. Validate:
  `make corpus-local-search-eval-validate`.

- **Retrieval context pack:** Deterministic, offline context pack generator
  that takes a query, runs the existing local lexical search, and exports
  top results as a structured evidence/context pack (JSON or Markdown) with
  full provenance. No embeddings, no API, no network, no LLM calls. Not RAG.
  Not legal advice. Usage:
  `python3 scripts/build_retrieval_context_pack.py "مجلس الإدارة"`. See
  [`docs/CORPUS_RETRIEVAL_CONTEXT_PACK.md`]. Validate:
  `make corpus-retrieval-context-pack-validate`.

- **Retrieval prompt pack:** Deterministic, offline prompt pack generator
  that takes a query, runs the existing retrieval context pack builder, and
  emits a safe, source-grounded prompt template for future LLM/RAG use.
  Three prompt modes: evidence_brief (default), cautious_answer_draft,
  citation_check. Builds prompts only — does NOT call any model, does NOT
  generate legal answers, does NOT produce legal advice, does NOT interpret
  legal text. No embeddings, no API, no network, no LLM calls. Usage:
  `python3 scripts/build_retrieval_prompt_pack.py "مجلس الإدارة"`. See
  [`docs/CORPUS_RETRIEVAL_PROMPT_PACK.md`]. Validate:
  `make corpus-retrieval-prompt-pack-validate`.

- **Citation support checker:** Deterministic, offline citation support
  checker that takes a draft answer file and a retrieval prompt/context pack,
  then mechanically checks whether cited record IDs exist in the supplied
  pack. Accepted citation syntax: `[[export_record_id=<ID>]]` and
  `[[source_record_id=<ID>]]`. Catches invalid citations, missing citations,
  and unsupported references. Optional `--require-citation-per-paragraph` and
  `--require-boundary-note` flags. Mechanical checking only — does NOT verify
  semantic support, legal correctness, or call any LLM. No embeddings, no API,
  no network. Usage:
  `python3 scripts/check_citation_support.py --prompt-pack /tmp/pack.json --draft-answer-file /tmp/draft.md`.
  See [`docs/CORPUS_CITATION_SUPPORT_CHECKER.md`]. Validate:
  `make corpus-citation-support-checker-validate`.

- **Retrieval workflow runner:** Deterministic, offline workflow runner that
  orchestrates existing corpus tools — context pack, prompt pack, and citation
  checker — into one practical end-to-end workflow. Two modes: `prepare_prompt`
  (build context + prompt packs + manifest) and `check_draft` (build packs +
  check draft answer citations + manifest). Thin orchestration only — reuses
  existing functions, no logic duplication. No LLM, no RAG, no embeddings, no
  API, no network. Generated run outputs are not committed. Usage:
  `python3 scripts/run_retrieval_workflow.py "مجلس الإدارة"`. See
  [`docs/CORPUS_RETRIEVAL_WORKFLOW_RUNNER.md`]. Validate:
  `make corpus-retrieval-workflow-runner-validate`.

- **Retrieval demo scenarios:** Six curated Arabic demo scenarios that run
  the existing workflow runner end-to-end for demonstration and rehearsal.
  Each scenario specifies a query, mode, filters, and expected artifacts.
  A validator runs all scenarios in temporary directories and confirms
  PASS/FAIL. A helper script runs all scenarios into a user-provided or
  temp dir. Deterministic, offline — no LLM, no RAG, no embeddings, no API,
  no network. Generated outputs are not committed. Usage:
  `python3 scripts/run_retrieval_demo_scenarios.py`. See
  [`docs/CORPUS_RETRIEVAL_DEMO_SCENARIOS.md`]. Validate:
  `make corpus-retrieval-demo-scenarios-validate`.

- **Retrieval operator demo pack:** Concise Arabic operator documentation
  for running, rehearsing, and showing the retrieval demo locally. Five
  files: START_HERE, DEMO_SCRIPT, REHEARSAL_CHECKLIST, COMMANDS, BOUNDARIES.
  A read-only validator confirms all files, boundary phrases, commands, and
  referenced scripts exist. No LLM, no RAG, no embeddings, no API, no network.
  No generated artifacts committed. Validate:
  `make corpus-retrieval-operator-demo-pack-validate`.

## PDPL (Personal Data Protection Law) — separate corpus track

- **PDPL law Arabic next-layer completed** — 43 article records (Article 32 = ملغاة), from reviewed
  OCR; read-only validator `make pdpl-arabic-law-next-layer-validate`. Status
  `REVIEWED_OCR_NOT_VERIFIED_OFFICIAL_TEXT`.
- **PDPL law Arabic text VERIFIED + corrected** — 43 records under `sources/pdpl/verified/`,
  generated by `scripts/gen_pdpl_arabic_law_verified.py`. The reviewed-OCR text (which carried
  systematic OCR errors: `9`→`و`, word-final `ء`→`،`, `الفرض`→`الغرض`, missing spaces) is replaced
  by the official SDAIA-published law text captured verbatim
  (`sources/pdpl/verified/pdpl_arabic_law_official_sdaia_source.json`) and cross-checked
  article-by-article against the independent OCR (token similarity min 0.78 / mean 0.92,
  near-identical lengths, contamination-scanned). Status upgraded to
  `VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT`. Validate:
  `make pdpl-arabic-law-verified-validate`.
- **PDPL law Arabic LLM-ready layer** — 43 records at
  `data/pdpl_arabic_legal_llm/pdpl_arabic_law_legal_llm_001_043.json`, generated by
  `scripts/gen_pdpl_arabic_law_legal_llm.py` over the verified text (`record_type =
  verified_arabic_article`). Ordinal headings only, so keywords are extracted mechanically from
  the text (term frequency, not a summary). JSON Schema
  `schemas/pdpl_arabic_law_legal_llm.schema.json`; Article 32 flagged repealed. Validate:
  `make pdpl-arabic-law-legal-llm-validate`.
- **PDPL implementing-regulation Arabic next-layer completed** — 38 article records
  (`pdpl_reg_art_001..038`), each `article_text` preserved verbatim from the extracted-text article
  inventory, source PDF SHA matched, boundaries held (Arabic governs; extracted text NOT verified
  official; no English correction / no translation / no legal interpretation). Artifacts under
  `sources/pdpl/regulation/next_layer/`. Validate:
  `make pdpl-implementing-regulation-arabic-next-layer-validate`.
- **PDPL implementing-regulation Arabic cleaned text** — 38 cleaned article records under
  `sources/pdpl/regulation/cleaned/`, generated deterministically by
  `scripts/gen_pdpl_implementing_regulation_arabic_cleaned.py`. Removes the two-column
  extraction artifacts (word-order-reversed title lines, next-article title bleed, stray
  `! % & # " * ...` markers, `عام` running headers, displaced line-initial diacritics, split
  list markers) and the Article 1 reversed definition-labels. Body sentences are the inventory
  extraction verbatim — never reordered or rewritten; spot-checked against the official SDAIA
  source (Article 3 matched). `official_text_status` stays
  `EXTRACTED_TEXT_NOT_VERIFIED_OFFICIAL_TEXT` (cleaning is structural, not a certified official
  transcription). Validate: `make pdpl-implementing-regulation-arabic-cleaned-validate`.
- **PDPL implementing-regulation Arabic text VERIFIED** — 38 records under
  `sources/pdpl/regulation/verified/`, generated by
  `scripts/gen_pdpl_implementing_regulation_arabic_verified.py`. The cleaned extraction text is
  replaced by the official SDAIA-published regulation text captured verbatim
  (`pdpl_implementing_regulation_official_sdaia_source.json`) with two documented non-semantic
  corrections applied by the generator: kashida (ـ) stripped, and a systematic fetch typo
  `القواعس`→`القواعد` (articles 23, 32, 35, 36) fixed — confirmed against the independent
  extraction. Cross-checked article-by-article vs the cleaned text (token similarity min 0.86 /
  mean 0.95). Status → `VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT`. Validate:
  `make pdpl-implementing-regulation-arabic-verified-validate`.
- **PDPL implementing-regulation Arabic LLM-ready layer** — 38 enrichment records at
  `data/pdpl_arabic_legal_llm/pdpl_implementing_regulation_arabic_legal_llm_001_038.json`,
  generated by `scripts/gen_pdpl_implementing_regulation_arabic_legal_llm.py` over the **verified**
  text. Mirrors the Companies Law `official_arabic_legal_llm` field set (`llm_title_ar`,
  `retrieval_title_ar`, `article_path`, `keywords_ar`, `search_queries_ar`,
  `article_text_hash_sha256`, `source_trust`); `record_type = verified_arabic_article`,
  `text_status = VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT`. Retrieval metadata is derived
  deterministically from title/number only — no summary, paraphrase, translation, or legal
  interpretation. JSON Schema `schemas/pdpl_implementing_regulation_arabic_legal_llm.schema.json`.
  Validate: `make pdpl-implementing-regulation-arabic-legal-llm-validate`.

## Investment Law (نظام الاستثمار) — separate corpus track

- **Investment Law verified text** — 16 article records under `sources/investment/law/verified/`,
  generated by `scripts/gen_investment_law_verified.py` from the official Ministry of Investment
  (MISA) bilingual PDF (`inputs/investment_official_pdfs/investment_law_misa.pdf`). The PDF's
  designed font corrupts direct text extraction, so the Arabic was transcribed verbatim from the
  visually-rendered pages and cross-checked article-by-article against the official English column
  in the same document (kept as reference only). Status
  `VERIFIED_TRANSCRIBED_FROM_OFFICIAL_MISA_PDF`. Validate: `make investment-law-verified-validate`.
- **Investment Law Arabic LLM-ready layer** — 16 records at
  `data/investment_arabic_legal_llm/investment_law_legal_llm_001_016.json`, generated by
  `scripts/gen_investment_law_legal_llm.py` (`record_type = verified_arabic_article`) with
  `llm_title_ar`, `retrieval_title_ar`, `article_path`, `keywords_ar`, `search_queries_ar`,
  `article_text_hash_sha256`, `source_trust`. JSON Schema
  `schemas/investment_law_legal_llm.schema.json`. Retrieval metadata derived from title/number
  only — no summary, paraphrase, translation, or interpretation. Validate:
  `make investment-law-legal-llm-validate`.
- **Investment Regulations verified text** — 37 article records under
  `sources/investment/regulation/verified/`, generated by
  `scripts/gen_investment_regulation_verified.py` from the official MISA Arabic Implementing
  Regulations PDF (`inputs/investment_official_pdfs/investment_regulation_misa_ar.pdf`). The PDF's
  designed font corrupts direct extraction, so the Arabic was produced by rendering + Arabic-OCR,
  then corrected verbatim against the rendered images and cross-checked against the official
  English edition. Status `VERIFIED_TRANSCRIBED_FROM_OFFICIAL_MISA_PDF`. Validate:
  `make investment-regulation-verified-validate`.
- **Investment Regulations Arabic LLM-ready layer** — 37 records at
  `data/investment_arabic_legal_llm/investment_regulation_legal_llm_001_037.json`
  (`record_type = verified_arabic_article`), JSON Schema
  `schemas/investment_regulation_legal_llm.schema.json`. Validate:
  `make investment-regulation-legal-llm-validate`.
- **Civil Transactions Law (نظام المعاملات المدنية) verified + LLM-ready** — 721 article
  records. Owner-provided full official Arabic text (Royal Decree M/191, 29/11/1444هـ), parsed
  deterministically into a complete 1..721 sequence (structural كتاب/باب/فصل headings separated as
  `section_context`), zero junk, spot-corroborated verbatim against an independent public mirror
  (Articles 1, 70). Source + verified records under `sources/civil/law/`; LLM-ready layer at
  `data/civil_arabic_legal_llm/civil_transactions_law_legal_llm_001_721.json` (`record_type =
  official_arabic_article`, `text_status = OWNER_PROVIDED_OFFICIAL_TEXT`); JSON Schema
  `schemas/civil_transactions_law_legal_llm.schema.json`. Validate:
  `make civil-transactions-law-verified-validate` and
  `make civil-transactions-law-legal-llm-validate`.
- **Unified cross-law retrieval index + search** — `scripts/gen_corpus_unified_llm_index.py`
  projects all six Arabic LLM-ready layers (Companies 281 + PDPL law 43 + PDPL regulation 38 +
  Investment law 16 + Investment regulation 37 + Civil Transactions Law 721 + GTPL 99 = **1235 records**) into one flat index at
  `data/corpus_unified_index/corpus_unified_llm_index.jsonl` with a common schema. Query the whole
  corpus at once with `python3 scripts/search_corpus_unified.py "<عربي>"` (deterministic lexical
  scorer over each record's keywords / search_queries / titles / text; `--corpus` and `--top`
  flags). No legal text is altered, summarized, or translated. Validate (includes sanity queries
  that must route to the right law): `make corpus-unified-llm-index-validate`.
- **Retrieval eval pack** — 40 realistic Arabic gold queries over the unified index
  (`data/corpus_retrieval_eval/`), each gold manually confirmed against the article's own text
  (definitional articles) or official title — not reverse-engineered from search output. Runner
  `scripts/run_corpus_retrieval_eval.py` computes top-1/top-3/top-5 accuracy + MRR@5 and writes
  deterministic results. **Current: top-1 90% / top-3 97.5% / MRR@5 0.929** (improved from
  85%/95%/0.883 by blending text term-frequency keywords into the title-only layers — PDPL
  regulation + Investment law/regulation; the Companies gold layer untouched). One documented
  lexical miss remains (civ-004 تعريف الكفالة). Validator re-runs the eval, requires exact
  reproducibility, and enforces floors (75%/85%/0.80). Validate:
  `make corpus-retrieval-eval-validate`.

## GTPL — نظام المنافسات والمشتريات الحكومية (م/128)

- **GTPL current law (M/128, 13/11/1440هـ) verified + LLM-ready + English reference** — 99 Arabic
  articles captured from a public mirror and **cross-checked token-by-token against the official
  Ministry of Finance consolidated PDF** (committed at `inputs/gtpl_official_pdfs/`; overlaps
  0.99/1.00/0.94 for arts 1/50/98 after ligature normalization; Article 98 supersession of the
  repealed M/58 (1427هـ) verified in both languages). English layer = the **official BOE
  translation** (owner-provided PDF, 99 articles parsed) — reference/guidance only, non-governing.
  The repealed 1427 law was intentionally NOT ingested as current. Track files under
  `sources/gtpl/law/` + `data/gtpl_arabic_legal_llm/`. Validate: `make gtpl-law-track-validate`.

## Strict QA gate

- **`make qa-gate`** — one command, everything must pass: **[1]** every
  `scripts/validate_*.py` in the repository (87 today — discovered from the filesystem, so any new
  validator automatically joins the gate; exclusions require a written reason in the script's
  `EXCLUDED` dict, currently empty); **[2]** generator idempotence — 14 deterministic generators
  are re-run and the git tree must show **zero drift** (catches "generator edited but outputs not
  regenerated"); **[3]** the full pytest suite. Wired into CI as a required step
  (`make qa-gate-ci`, tests phase skipped there since CI runs pytest separately). A failure in any
  validator, any drift, or any test **fails the gate and blocks the merge**.

## Legal / official-status boundaries

- **Official government adoption: not claimed.**
- **Official translation: not claimed.**
- **Official government publication: not claimed.**
- **Chinese is not official, not binding, not governing.**
- **Not legal advice.**

## Review model

- The **official Arabic source governs**; English and Chinese are reference layers.
- The **repository owner has a legal background (bachelor of law)** and runs
  **active repository legal review** (`repository_owner_review_active`).
- **External legal review is optional** for enterprise or official adoption and
  **not required for repository use**.
