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
  regulation 37 + Civil Transactions Law 721 + GTPL 99 (+99 English reference) +
  GTPL regulation 157 + Labor Law 249 (+234 English reference) + Labor regulation 45 + Labor model
  work regulation 72+3 tables + Labor mediation rules 20 + Labor recruitment rules 72 + Labor
  accessibility tables 8 + Labor contract forms 102 + Evidence Law 129 + Evidence companions
  24+135+34 + Personal Status Law 252 + Personal Status regulation 41 + Law of Sharia Procedure 243
  + Sharia Procedure regulation 637 + Law of Criminal Procedure 222**)
  with counts, paths, statuses, language layers,
  boundaries, and validation targets. **27 tracks; primary Arabic governing 3849; reference 614; registry-counted
  4744.** PDPL and Investment Arabic tracks are **verified against official
  published text** (SDAIA / MISA). The registry also records the unified retrieval
  index (3680 records) as a projection (not added to totals). See
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
- **Civil Transactions Law (نظام المعاملات المدنية) verified + LLM-ready + MOJ cross-checked** —
  721 article records. Owner-provided full official Arabic text (Royal Decree M/191,
  29/11/1444هـ), parsed deterministically into a complete 1..721 sequence, and now
  **cross-checked article-by-article against the official MOJ legal-portal database** (721/721
  aligned one-to-one; the law is **unamended** — every article `اصلية`). Divergences were
  adjudicated visually on the official MOJ PDF (committed at `inputs/civil_official_pdfs/` with
  recorded sha256; contested letterforms zoomed at 600–700dpi): **17 single-word defects in the
  owner text corrected** (e.g. dropped-alef "ذا"→"إذا" ×3, سيء→سيئ ×7, a cross-reference case
  ending in art 677) and **21 trailing structural headings moved** to the following article's
  `section_context` — every change documented in the source artifact's `moj_cross_check` block
  and enforced by the validator; full audit artifacts under `sources/civil/law/moj_cross_check/`.
  Documented presentation difference kept as-is: the official print numbers clauses (١- ٢-) in
  243 articles where this text uses unnumbered paragraphs (bodies verbatim). LLM-ready layer at
  `data/civil_arabic_legal_llm/civil_transactions_law_legal_llm_001_721.json` (`text_status =
  OWNER_PROVIDED_CROSS_CHECKED_MOJ_PORTAL`). Validate:
  `make civil-transactions-law-verified-validate` and
  `make civil-transactions-law-legal-llm-validate`.
- **Unified cross-law retrieval index + search** — `scripts/gen_corpus_unified_llm_index.py`
  projects all twenty-five Arabic LLM-ready layers (Companies 281 + PDPL law 43 + PDPL regulation 38 +
  Investment law 16 + Investment regulation 37 + Civil Transactions Law 721 + GTPL 99+157 +
  Labor 571 across its eight components + Evidence 322 across its four components +
  Personal Status 293 (law 252 + regulation 41) + Sharia Procedure 880 (law 243 + regulation 637) + Criminal Procedure 222 = **3680 records**) into one flat index at
  `data/corpus_unified_index/corpus_unified_llm_index.jsonl` with a common schema. Query the whole
  corpus at once with `python3 scripts/search_corpus_unified.py "<عربي>"` (deterministic lexical
  scorer over each record's keywords / search_queries / titles / text; `--corpus` and `--top`
  flags). No legal text is altered, summarized, or translated. Validate (includes sanity queries
  that must route to the right law): `make corpus-unified-llm-index-validate`.
- **Retrieval eval pack** — 80 realistic Arabic gold queries over the unified index
  (`data/corpus_retrieval_eval/`), each gold manually confirmed against the article's own text
  (definitional articles) or official title — not reverse-engineered from search output. Runner
  `scripts/run_corpus_retrieval_eval.py` computes top-1/top-3/top-5 accuracy + MRR@5 and writes
  deterministic results. **Current: top-1 86.2% / top-3 93.8% / top-5 97.5% / MRR@5 0.9025**
  over the 3680-record index with **80 golds** — expanded from 40 (v2: gtp-001..007 +
  lab-001..014; v3: ith-001..003; v4: ith-004..006; v5: ahw-001..004; v6: mrf-001..003 law; v7: mrf-004..006 regulation; v8: mjz-001..003 criminal procedure) so that GTPL, all eight
  Labor components, all four Evidence components, the Personal Status law + regulation, the
  Law of Sharia Procedure + its implementing regulation, and the Law of Criminal Procedure have
  gold coverage; every new
  gold was confirmed by reading the article's committed text first and writing the query from
  its own wording. Two documented
  lexical misses remain (civ-004 تعريف الكفالة; pdp-010 سياسة الخصوصية — the gold PDPL article
  does not contain the query phrase verbatim, so labor-annex records now outscore it). Validator re-runs the eval, requires exact
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
- **GTPL Implementing Regulation (157 articles) verified + LLM-ready** — re-extracted at glyph
  level from the official MOF consolidated PDF (pipeline validated at 0.996 mean similarity vs the
  known GTPL law text; duplicate interleaved copies adjudicated against rendered pages and official
  wording). Track under `sources/gtpl/regulation/` + `data/gtpl_arabic_legal_llm/`. Validate:
  `make gtpl-regulation-track-validate`.

## نظام العمل — Labor Law (م/51، 1426هـ)

- **Labor Law (M/51, 23/8/1426هـ, amendments through M/44 merged) verified + LLM-ready** — 249
  records (245 numbered articles + 4 مكرر: 11، 79، 131، 229; **38 officially deleted articles
  flagged**, placeholder as printed). Source = the **official HRSD consolidated PDF** (committed at
  `inputs/labor_official_pdfs/labor_law_hrsd_consolidated_ar.pdf`), extracted article-by-article and
  **cross-verified against the repository's independently captured BOE base texts**
  (`worksheets/labor_law/`): 142 articles match the BOE base verbatim (two official sources),
  65 differ exactly where the committed amendment tracking says they were amended, and **ZERO
  differences are unexplained** — closing the prior reconciliation program's 92 open issues with
  official text. English layer = the pre-existing 234 reference records
  (`data/english_reference/labor_law/`), reference/guidance only, non-governing. Track files under
  `sources/labor/law/` + `data/labor_arabic_legal_llm/`. The validator re-verifies the
  MATCHES_BOE_BASE claim against the committed worksheets (142 re-checked ≥0.90 token similarity)
  and fails on any unexplained status. Validate: `make labor-law-track-validate`.
- **Labor Law Implementing Regulation (core, 45 records) verified + LLM-ready** — articles (1)–(40)
  + 5 مكرر ((4 مكرر)، (15) مكرر، (16) مكرر (1)، (16) مكرر (2)، (22) مكرر); **3 officially deleted
  flagged** (2، 36، 37). Source = the **official HRSD PDF** «اللائحة التنفيذية لنظام العمل
  وملحقاتها» (committed at `inputs/labor_official_pdfs/labor_regulation_hrsd_consolidated_ar.pdf`),
  core text extracted and verified two ways: tesseract-ara OCR of the 300dpi rendered pages (all
  active articles ≥0.91, mean 0.978) and — stronger — the PDF's own **verbatim Labor Law quotes
  cross-checked against the verified labor_law track** (45 quotes, all ≥0.95, 39/45 exactly 1.00),
  corroborating both tracks at once. Each record carries `implements_law_articles` linking it to
  the law articles it implements; the validator re-resolves every link against the committed law
  track (must exist, must not be deleted). The PDF's five annexes (النموذج الموحد للائحة تنظيم
  العمل، الترتيبات التيسيرية، ضوابط التوسط، قواعد الاستقدام، نماذج العقود) are committed but NOT
  ingested — each is a candidate follow-up track. Track files under `sources/labor/regulation/` +
  `data/labor_arabic_legal_llm/`. Validate: `make labor-regulation-track-validate`.
- **Model Work Organization Regulation (Annex 1, 75 records) verified + LLM-ready** — the
  Ministry's model bylaw (النموذج الموحد للائحة تنظيم العمل) adopted by regulation article (3):
  **72 articles** (complete 1–72, all active, 27 section headings captured, OCR ≥0.93, mean 0.986;
  المادة (25) located despite its tatweel-stretched heading) + **3 violation/penalty tables**
  (16/18/16 = 50 rows). Table structure rebuilt from the ruling-line grid, cells verbatim from the
  text layer, and **every cell of all 50 rows checked against the 300/400dpi rendered page images**
  (tesseract mis-reads the font's % glyph, so 29 rows were verified directly on the images — all
  listed in the source artifact). Table records are a mechanical linearization (cells verbatim,
  separators only) and the validator re-derives them byte-identically from the committed cells,
  plus re-checks the adoption link in regulation art (3). Preamble kept separately in the source
  artifact. Track under `sources/labor/annex1/` + `data/labor_arabic_legal_llm/`. Validate:
  `make labor-annex1-track-validate`.
- **Annexes 3 + 4 (mediation + recruitment rules, 92 records) verified + LLM-ready** —
  **Annex 3: ضوابط وقواعد ممارسة نشاط التوسط في توظيف السعوديين** (20 articles in 4 أبواب, complete
  1–20, OCR ≥0.97) and **Annex 4: قواعد ممارسة نشاط الاستقدام وتقديم الخدمات العمالية** (72 articles
  in 7 أبواب/10 فصول, complete 1–72, OCR ≥0.92) from the same committed HRSD PDF. Text-layer
  hazards repaired mechanically and logged (18 fused/split headings; z-order displacement around
  annex-4 arts 3/4 restored per the rendered page; 3 OCR-adjudicated space repairs). Printed latin
  glyphs kept verbatim and **whitelisted per article** in the validator (annex-4 art 10 "o"
  bullets; art 14 "Enterprise resource planning (ERP)" — both confirmed on the page images).
  Tracks under `sources/labor/annex3/`, `sources/labor/annex4/` + `data/labor_arabic_legal_llm/`.
  Validate: `make labor-annex34-tracks-validate`.
- **Annex 2 (accessibility arrangements tables, 8 records / 40 rows) verified + LLM-ready** —
  جدول الترتيبات والخدمات التيسيرية في بيئة العمل للعمال ذوي الإعاقة: 6 disability sections
  (جسدية بثلاثة جداول فرعية، بصرية، سمعية، نفسية، ذهنية، مؤقتة/مرض) × columns الوظيفة وطبيعتها /
  نوع وشكل الترتيبات المقترحة. The table pages are **raster images**; the verbatim text was
  recovered from the PDF's own structure-tree `/ActualText` entries, the grid rebuilt from the
  drawn ruling rectangles, **every row verified against OCR and the rendered page images**, and
  all 21 ambiguous line-break junctions adjudicated. Printed typesetting defects kept as printed
  and documented (interleaved first wheelchair-row cell; the سادسًا heading's "والمرض الزمن"
  spelling). Records are mechanical linearizations (cells verbatim) re-derived byte-identically by
  the validator, which also re-checks the linkage to the regulation's law-art-28 accessibility
  article. Track under `sources/labor/annex2/` + `data/labor_arabic_legal_llm/`. Validate:
  `make labor-annex2-track-validate`.
- **Annex 5 (unified model employment contract forms, 102 records) verified + LLM-ready** — the
  four official model contracts: **permanent** (officially bilingual, 17 units = clauses 1–16 +
  parties statement + an 8-row bilingual glossary table), **part-time** (30 units),
  **casual/temporary** (25 units), **seasonal** (29 units). The permanent form's two language
  columns were separated by coordinates — **zero latin in any governing Arabic text** (enforced by
  the validator); its printed English column is embedded verbatim as a non-governing
  `text_en_reference` field (part of the official form, not our translation, not counted as
  reference records). The short forms' table bodies render as images and were transcribed from
  300dpi renders. Every unit verified: 14 conclusively by OCR (ar+en ≥0.85), 87 additionally on
  the rendered page images (dotted fill-in blanks and signature blocks OCR poorly by nature;
  method recorded per unit). Fill-in blanks and the official print's own misprints kept verbatim
  and documented (e.g. the English column's duplicated 11.2/11.10 numbering). **This completes the
  full HRSD document «اللائحة التنفيذية لنظام العمل وملحقاتها» — all five annexes ingested.**
  Track under `sources/labor/annex5/` + `data/labor_arabic_legal_llm/`. Validate:
  `make labor-annex5-track-validate`.

## نظام الإثبات — Evidence Law (م/43، 1443هـ)

- **Evidence Law (M/43, 26/5/1443هـ) verified + LLM-ready** — 129 articles in 11 chapters
  (including الباب الرابع: **الدليل الرقمي**), **unamended** since issuance (every article
  `legalStatusName = اصلية`, no amendment history). Double official capture: all 129 articles
  fetched individually from the **official MOJ legal-portal database** (laws.moj.gov.sa via its
  gateway API) and cross-verified against the **official MOJ PDF** downloaded from the same
  portal (committed at `inputs/evidence_official_pdfs/` with recorded sha256; its text layer is
  glyph-mangled so a 300dpi render + tesseract-ara channel and a repaired text-layer channel were
  both built): **129/129 match** (min 0.90, mean 0.995), lowest scorers audited token-by-token —
  all residuals are extraction artifacts, **zero unexplained differences**. Mechanical cleanup
  documented in the source artifact (HTML tags; 7 decorative tatweel chars across 4 articles).
  The BOE portal resets connections from this environment (noted in provenance). Track under
  `sources/evidence/law/` + `data/evidence_arabic_legal_llm/`. Validate:
  `make evidence-law-track-validate`.
- **The three companion instruments (193 records) verified + LLM-ready** — all issued by **MoJ
  decision (921) dated 16/03/1444هـ**, all in force and unamended, all captured with the same
  double-official pipeline (portal database article-by-article × the instrument's official MOJ
  PDF, committed with recorded sha256): **ضوابط إجراءات الإثبات إلكترونيًا** (24 articles,
  min 0.98), **الأدلة الإجرائية لنظام الإثبات** (135 articles, min 0.94 — uses ordinary المادة
  ordinals; one documented source typo: position 132's printed label omits "بعد المائة" in both
  the database and the PDF, kept verbatim and keyed by document order), and **القواعد الخاصة
  بتنظيم شؤون الخبرة أمام المحاكم** (34 articles, min 0.91). Zero unexplained differences across
  all 193. Tracks under `sources/evidence/{electronic_rules,procedural_manuals,expertise_rules}/`
  + `data/evidence_arabic_legal_llm/`. Validate: `make evidence-companions-tracks-validate`.
  **The Evidence file is complete: law + electronic controls + procedural manuals + expertise
  rules (322 records).**

## نظام الأحوال الشخصية — Personal Status Law (م/73، 1443هـ)

- **Personal Status Law (M/73, 6/8/1443هـ) + implementing regulation verified + LLM-ready** —
  the third pillar of the new judicial codification (alongside Civil Transactions + Evidence).
  **نظام الأحوال الشخصية** — 252 articles in 8 chapters (complete 1–252) — and its **لائحة**
  (Supreme Order 59641, 17/8/1446هـ) — 41 articles (complete 1–41) — both captured with the same
  double-official MOJ pipeline (portal database article-by-article × the official MOJ PDF from the
  same portal, committed with recorded sha256; glyph-mangled text layers handled via 300dpi render
  + tesseract-ara plus a repaired text-layer channel). Both are **in force and unamended** (every
  article `اصلية`). Cross-check: law 249/252 matched ≥0.90 outright, and the 3 sub-0.90 articles
  (87, 98, 198) were **visually adjudicated on the official PDF pages** — the stored database text
  matches the print verbatim, the low scores were tesseract OCR-channel artifacts only; regulation
  41/41 matched (mean 0.998). **Zero unexplained differences.** Tatweel handling verified on the
  print: one decorative in-word tatweel removed (law art 87 رجعيـاً→رجعياً), while the official
  "هـ" fifth-item enumerator tatweel (أ ب ج د هـ) is kept. Tracks under
  `sources/personal_status/{law,regulation}/` + `data/personal_status_arabic_legal_llm/`. Validate:
  `make personal-status-tracks-validate`.

## نظام المرافعات الشرعية — Law of Sharia Procedure (م/1، 1435هـ)

- **Law of Sharia Procedure (M/1, 22/1/1435هـ) verified + LLM-ready — the first heavily-amended
  law, ingested as a consolidated text with per-article status flags.** **نظام المرافعات
  الشرعية** — **243 records**: complete 1..242 numbered articles + المادة (224) مكرر. Captured with
  the same double-official MOJ pipeline (portal database article-by-article × the official MOJ PDF
  from the same portal, 38 pages, committed with recorded sha256). Unlike the earlier laws this one
  is **not unamended**: the official consolidated PDF retains the bodies of repealed and amended
  articles and flags each with a colored status badge, so each record carries `legal_status_ar`
  (اصلية/معدلة/ملغاة/مضافة) plus `is_repealed`/`is_amended`/`is_added` flags and an
  `amendment_history`. **Status breakdown: 153 اصلية / 14 معدلة / 75 ملغاة / 1 مضافة.** Repealed
  articles keep their full text and are **flagged, not deleted**, mirroring the official source; the
  LLM title gets a " (ملغاة)" suffix so retrieval never presents a repealed article as if in force.
  Cross-check: **every article MATCHES_PDF ≥0.90 (min 0.92)**; the 3 initially-flagged articles and
  the tatweel were visually adjudicated on the rendered pages (the "هـ" enumerator, the Hijri-date
  "هـ" abbreviation, and art-26 space-bounded enumerator dashes are in the official print; 45
  in-word decorative tatweel are justification artifacts, removed as mechanical normalization). The
  art-61 printed label typo (المادية الحادية والستون) is kept verbatim. Track under
  `sources/sharia_procedure/law/` + `data/sharia_procedure_arabic_legal_llm/`. Validate:
  `make sharia-procedure-law-track-validate`.

- **Implementing Regulation of the Law of Sharia Procedure verified + LLM-ready — first DUAL-STATUS
  track.** **اللائحة التنفيذية لنظام المرافعات الشرعية** (قرار وزير العدل 39933، 19/5/1435هـ) —
  **637 provisions** captured with the same double-official MOJ pipeline (portal database × official
  MOJ PDF, 61 pages, committed with sha256). This regulation carries a genuine dual status that we
  record honestly on **every** provision, neither side hidden: `pdf_document_status_ar` — the badge
  the official PDF actually prints (**536 اصلية / 17 معدلة / 63 ملغاة / 21 مضافة**, the governing
  anchor driving is_repealed/is_amended/is_added) — and `portal_legal_status_ar` — the MOJ portal's
  live legal database (**388 اصلية / 16 معدلة / 212 ملغاة / 21 مضافة**). The portal additionally marks
  **149 provisions** ملغاة — the evidence chapters (الوقائع/الاستجواب/الإقرار/اليمين/الشهادة/القرائن/
  الخبرة) and the النقض/التماس إعادة النظر chapters — because the standalone **Law of Evidence (م/43)**
  superseded them, even though the published regulation PDF still prints them in force; those carry
  `is_superseded=True` + `superseded_by_ar` and are marked "(مستبدلة بنظام الإثبات م/٤٣)" in the
  retrieval title so an LLM never presents a superseded provision as current. Verification: 633/639
  matched outright; the **6 flagged provisions were visually adjudicated on the rendered pages** — 5
  are digit-in-parenthetical text-layer/OCR artifacts (stored text matches the print verbatim: ٢/٧,
  ٧/٣١, ٧/٣٣, ٥/١٩٠, ٦/١٩٠), and ٢/٢٢٧ had a real difference where the official PDF prints the معدلة
  body (used) while the section-API returned the pre-amendment original. **2 exact portal
  redundancies** (labels ١/٢٣٢ and ١٢/٢٢٨ — identical text and status) were removed to match the
  official PDF, which prints each once (verified on pages 56/58): 639 portal nodes → 637 distinct
  provisions. Repealed/superseded provisions keep their full text and are flagged, not deleted. Track
  under `sources/sharia_procedure/regulation/` + `data/sharia_procedure_arabic_legal_llm/`. Validate:
  `make sharia-procedure-regulation-track-validate`.

## نظام الإجراءات الجزائية — Law of Criminal Procedure (م/2، 1435هـ)

- **Law of Criminal Procedure (M/2, 22/1/1435هـ) verified + LLM-ready — the criminal-procedure
  counterpart to the Sharia Procedure Law.** **نظام الإجراءات الجزائية** — **222 records** (complete
  1–222, no مكرر). In force; replaces the former Law of Criminal Procedure (M/39, 1422هـ) per its
  own Article 221. Captured with the same double-official MOJ pipeline (portal database
  article-by-article × the official MOJ PDF from the same portal, 27 pages, committed with recorded
  sha256). A **lightly** amended consolidated law: **219 اصلية / 3 معدلة / 0 ملغاة / 0 مضافة** — the
  3 amended articles (25 by M/28, 112 by M/125, 218 by M/43 1443هـ) carry their amendment history and
  their current amended bodies match the print. Unlike the Sharia Procedure regulation there is **no
  dual-status divergence** — the section-API status equals the PDF status for every article.
  Cross-check: **220/222 matched outright (mean 0.994)**; the 2 flagged articles were **visually
  adjudicated verbatim** on the rendered pages — art 222 (the one-line "يعمل بهذا النظام من تاريخ
  نشره" closing article, sim 0.60 purely a short-article artifact, page 26) and art 210 (spelled-out
  ordinal cross-references "(الرابعة والتسعين بعد المائة)…", sim 0.90, page 24). 5 decorative in-word
  tatweel removed; the "هـ" Hijri-date abbreviation (art 221) and space-bounded enumerator dashes
  (art 11) kept. Track under `sources/criminal_procedure/law/` +
  `data/criminal_procedure_arabic_legal_llm/`. Validate: `make criminal-procedure-law-track-validate`.

## Strict QA gate

- **`make qa-gate`** — one command, everything must pass: **[1]** every
  `scripts/validate_*.py` in the repository (101 today — discovered from the filesystem, so any new
  validator automatically joins the gate; exclusions require a written reason in the script's
  `EXCLUDED` dict, currently empty); **[2]** generator idempotence — 28 deterministic generators
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
