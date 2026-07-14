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
  + Sharia Procedure regulation 637 + Law of Criminal Procedure 222 + Criminal Procedure regulation 181 + Law of Enforcement 98 + Enforcement regulation 273 + Law of the Judiciary 85 + Law of the Board of Grievances 26 + Code of Law Practice 56 + Code of Law Practice regulation 90 + Commercial Courts Law 96 + Commercial Courts Law regulation 281 + Bankruptcy Law 231 + Bankruptcy Law regulation 98 + Bankruptcy case rules 24 + Judicial Costs Law 23 + Judicial Costs regulation 17 + Arbitration Law 58 + Arbitration regulation 19 + Commercial Papers Law 121 + Commercial Register Law 29 + Trade Names Law 23 + Commercial Agencies Law 6 + Chambers of Commerce Law 66 + Commercial Books Law 16 + Anti-Money Laundering Law 52 + Notarization Law 57 + Notarization Regulation 31 + Real Estate Registration Law 40 + Real Estate Registration Regulation 51 + Registered Real Estate Mortgage Law 46 + Real Estate Finance Law 15 + Real Estate Unit Ownership Law 33 + Real Estate Unit Ownership Regulation 41 + Non-Saudi Real Estate Ownership Law 15 + Municipal Real Estate Disposal Law 6 + Municipal Real Estate Disposal Regulation 35 + GCC Citizens Ownership Regulation 6 + Combating Terrorism Crimes and Financing 99 + its Implementing Regulation 28 + Juveniles Law 24 + its Implementing Regulation 13 + Whistleblower, Witness, Expert and Victim Protection Law 37 + Judicial Inspection Regulation 68 + Regulation on the Division of Jointly-Owned Property 48 + Professional Conduct Rules for Lawyers 47 + Regulation Organizing the Work of Judicial Assistants 35 + Rules for the Work of Conciliation Offices and its Procedures 29 + Rules Organizing Cross-Border Insolvency Procedures 23 + Regulation on Judicial Documents 23 + Rules for Determining the Fees of Experts and Trustees under the Bankruptcy Law 20 + Regulation on Enforcement Service Providers 18 + Alimony Fund Regulation 17**)
  with counts, paths, statuses, language layers,
  boundaries, and validation targets. **77 tracks; primary Arabic governing 6723; reference 614; registry-counted
  7618.** PDPL and Investment Arabic tracks are **verified against official
  published text** (SDAIA / MISA). The registry also records the unified retrieval
  index (6554 records) as a projection (not added to totals). See
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
  projects all thirty-four Arabic LLM-ready layers (Companies 281 + PDPL law 43 + PDPL regulation 38 +
  Investment law 16 + Investment regulation 37 + Civil Transactions Law 721 + GTPL 99+157 +
  Labor 571 across its eight components + Evidence 322 across its four components +
  Personal Status 293 (law 252 + regulation 41) + Sharia Procedure 880 (law 243 + regulation 637) + Criminal Procedure 403 (law 222 + regulation 181) + Enforcement 371 (law 98 + regulation 273) + Judiciary 85 + Board of Grievances 26 + Law Practice 146 (law 56 + regulation 90) + Commercial Courts 377 (law 96 + regulation 281) + Bankruptcy 353 (law 231 + regulation 98 + case rules 24) + Judicial Costs 40 (law 23 + regulation 17) + Arbitration 77 (law 58 + regulation 19) + Commercial Papers 121 (law) + Commercial Register 29 (law) + Trade Names 23 (law) + Commercial Agencies 6 (law) + Chambers of Commerce 66 (law) + Commercial Books 16 (law) + Anti-Money Laundering 52 (law) + Notarization 88 (law 57 + regulation 31) + Real Estate Registration 91 (law 40 + regulation 51) + Real Estate Mortgage 46 (law) + Real Estate Finance 15 (law) + Real Estate Units 74 (law 33 + regulation 41) + Non-Saudi Ownership 15 (law) + Municipal Real Estate 41 (law 6 + regulation 35) + GCC Ownership 6 (law) + Counter-Terrorism 127 (law 99 + regulation 28) + Juveniles 37 (law 24 + regulation 13) + Whistleblower Protection Law 37 (law) + Judicial Inspection Regulation 68 (regulation) + Qismah Regulation 48 (regulation) + Professional Conduct Rules for Lawyers 47 (regulation) + Judicial Assistants Regulation 35 (regulation) + Conciliation Offices Rules 29 (regulation) + Cross-Border Insolvency Procedures Rules 23 (regulation) + Judicial Documents Regulation 23 (regulation) + Bankruptcy Fees Rules 20 (regulation) + Enforcement Service Providers Regulation 18 (regulation) + Alimony Fund Regulation 17 (regulation) = **6554 records**) into one flat index at
  `data/corpus_unified_index/corpus_unified_llm_index.jsonl` with a common schema. Query the whole
  corpus at once with `python3 scripts/search_corpus_unified.py "<عربي>"` (deterministic lexical
  scorer over each record's keywords / search_queries / titles / text; `--corpus` and `--top`
  flags). No legal text is altered, summarized, or translated. Validate (includes sanity queries
  that must route to the right law): `make corpus-unified-llm-index-validate`.
- **Retrieval eval pack** — 80 realistic Arabic gold queries over the unified index
  (`data/corpus_retrieval_eval/`), each gold manually confirmed against the article's own text
  (definitional articles) or official title — not reverse-engineered from search output. Runner
  `scripts/run_corpus_retrieval_eval.py` computes top-1/top-3/top-5 accuracy + MRR@5 and writes
  deterministic results. **Current: top-1 88.6% / top-3 97.3% / top-5 98.9% / MRR@5 0.9286**
  over the 6554-record index with **184 golds** — expanded from 40 (v2: gtp-001..007 +
  lab-001..014; v3: ith-001..003; v4: ith-004..006; v5: ahw-001..004; v6: mrf-001..003 law; v7: mrf-004..006 regulation; v8: mjz-001..003 criminal-procedure law; v9: mjr-001..003 criminal-procedure regulation; v10: mtn-001..003 enforcement law; v11: mtl-001..003 enforcement regulation; v12: mqd-001..003 judiciary; v13: dmz-001..003 board-of-grievances; v14: muh-001..003 law-practice; v15: mhl-001..003 law-practice-regulation; v16: tjr-001..003 commercial-courts; v17: tjl-001..003 commercial-courts-regulation; v18: ifl-001..003 bankruptcy law; v19: ilr-001..003 bankruptcy regulation; v20: icr-001..003 bankruptcy case rules; v21: tkq-001..002 judicial-costs law + tkr-001 regulation; v22: thk-001..002 arbitration law + thr-001 regulation; v23: awt-001..003 commercial-papers law; v24: sjt-001..002 commercial-register + ast-001 trade-names; v25: wkl-001..002 commercial-agencies; v26: ghr-001..002 chambers-of-commerce; v27: dft-001..002 commercial-books; v28: hmb-001..002 whistleblower-protection; v29: tft-001..002 judicial-inspection; v30: qsm-001..002 qismah-division; v31: slk-001..002 sulook-professional-conduct; v32: awn-001..002 aawan-judicial-assistants; v33: msl-001..002 muslaha-conciliation-offices; v34: ifh-001..002 iflas-hudud-cross-border-insolvency; v35: jud-001..002 judicial-documents-regulation; v36: atb-001..002 bankruptcy-fees-regulation; v37: tnf-001..002 enforcement-providers-regulation; v38: nfq-001..002 alimony-fund-regulation) so that GTPL, all eight
  Labor components, all four Evidence components, the Personal Status law + regulation, the
  Law of Sharia Procedure + its implementing regulation, the Law of Criminal Procedure + its implementing regulation, the Law of Enforcement + its regulation, the Law of the Judiciary, the Law of the Board of Grievances, the Code of Law Practice + its regulation, and the Commercial Courts Law + its regulation have
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

- **Implementing Regulation of the Law of Criminal Procedure verified + LLM-ready.** **اللائحة
  التنفيذية لنظام الإجراءات الجزائية** (قرار مجلس الوزراء ١٤٢، ٢١/٣/١٤٣٦هـ) — **181 records** (complete
  1–181, sequential ordinal labels, no مكرر). In force. Same double-official MOJ pipeline (portal
  database × official MOJ PDF, 25 pages, committed with recorded sha256). Like the law it is **lightly
  amended and single-status**: **174 اصلية / 7 معدلة (arts 21, 71, 92, 93, 157, 163, 179, by Cabinet
  decision 860) / 0 ملغاة / 0 مضافة** — no dual-status divergence (section-API status equals the PDF
  status for every article), the 7 amended bodies match the print. Cross-check: **178/181 matched
  outright (mean 0.993)**; the 3 flagged articles were **visually adjudicated verbatim** — arts 57 and
  164 (in-word decorative tatweel that OCR mangled, pages 8/22) and art 181 (the one-line
  effective-in-30-days closing article, page 24). 39 decorative in-word tatweel removed (this PDF is
  heavily justified); the "هـ" enumerator and space-bounded enumerator dashes kept. Track under
  `sources/criminal_procedure/regulation/` + `data/criminal_procedure_arabic_legal_llm/`. Validate:
  `make criminal-procedure-regulation-track-validate`.

## نظام التنفيذ — Law of Enforcement (م/53، 1433هـ)

- **Law of Enforcement (M/53, 13/8/1433هـ) verified + LLM-ready — closes the dispute lifecycle
  (substantive → evidence → procedure → enforcement).** **نظام التنفيذ** — **98 records** (complete
  1–98, no مكرر). In force; per its Article 96 it repealed articles 196–232 of the former Law of Sharia
  Procedure (M/21) and paragraph (z) of Article 13 of the Board of Grievances Law (M/78). Same
  double-official MOJ pipeline (portal database × official MOJ PDF, 14 pages, committed with recorded
  sha256). **Lightly amended, single-status with one flagged repeal**: **94 اصلية / 3 معدلة (arts 46,
  74, 90, by M/52) / 1 ملغاة (art 75) / 0 مضافة** — no dual-status divergence. The repealed article
  (art 75, "لا ينفذ الحكم الصادر على الزوجة بالعودة إلى بيت الزوجية جبراً") keeps its full text and is
  **flagged, not deleted** — the official PDF retains its body with a red ملغاة badge (verified on
  page 10); the LLM title gets a "(ملغاة)" suffix so retrieval never presents it as in force.
  Cross-check: **97/98 matched outright (mean 0.992)**; the 1 flagged article (art 98, the one-line
  effective-in-180-days closing article, sim 0.70 length artifact) was visually adjudicated verbatim on
  page 13. 11 decorative in-word tatweel removed; the "هـ" enumerator and space-bounded enumerator
  dashes kept. Track under `sources/enforcement/law/` + `data/enforcement_arabic_legal_llm/`. Validate:
  `make enforcement-law-track-validate`.

- **Implementing Regulation of the Law of Enforcement verified + LLM-ready — completes the enforcement
  pair.** **اللائحة التنفيذية لنظام التنفيذ** (قرار وزير العدل ٥٢٦، ٢٠/٢/١٤٣٩هـ) — **273 provisions**
  (clause-labeled X/Y, keyed by document order 1–273). Same double-official MOJ pipeline (portal
  database × official MOJ PDF, 26 pages, committed with recorded sha256). **Lightly amended (by
  decision 7207), single-status**: **266 اصلية / 2 معدلة (٧/٦، ٢/٨٣) / 2 ملغاة (٥/٤٦، ١/٧٥) / 3 مضافة
  (٣/٨٣، ٤/٨٣، ٣/٨٤)**. The repealed provisions keep their full text and are **flagged, not deleted** —
  the official PDF retains their bodies with red ملغاة badges (verified on page 14); the LLM title gets
  a "(ملغاة)" suffix. Unlike the Sharia Procedure regulation there is **no dual-status divergence**
  (section-API status equals the PDF status for every provision) and **no duplicate labels or
  redundancies**. Cross-check: **272/273 matched outright (mean 0.997)**; the 1 flagged clause (١/٤٢, a
  short clause carrying the digit cross-references (١/٣٢)/(٢/٣٢)) was visually adjudicated verbatim on
  page 13. 1 decorative in-word tatweel removed. Track under `sources/enforcement/regulation/` +
  `data/enforcement_arabic_legal_llm/`. Validate: `make enforcement-regulation-track-validate`.

## نظام القضاء — Law of the Judiciary (م/78، 1428هـ)

- **Law of the Judiciary (M/78, 19/9/1428هـ) verified + LLM-ready — the foundational
  court-organization statute.** **نظام القضاء** — **85 records** (complete 1–85, no مكرر). This is
  the structural law beneath the whole judicial corpus: its **Article 9** defines the court hierarchy
  (المحكمة العليا / محاكم الاستئناف / five first-degree courts: العامة، الجزائية، الأحوال الشخصية،
  التجارية، العمالية) and it establishes the المجلس الأعلى للقضاء referenced throughout every
  procedure and enforcement law. In force; per its Article 85 it replaced the former نظام القضاء
  (M/64, 1395هـ). Same double-official MOJ pipeline (portal database × official MOJ PDF, 15 pages,
  committed with recorded sha256). **Lightly amended, single-status**: **82 اصلية / 3 معدلة (arts 5,
  35, 72, by M/95) / 0 ملغاة / 0 مضافة** — no dual-status divergence. Cross-check: **82/85 matched
  outright (mean 0.990)**; the 3 flagged articles were **visually adjudicated verbatim** — art 9 (the
  court-structure enumeration with the هـ fifth-item enumerator, page 2), art 71 (numbered dash
  clauses, page 11), and art 85 (the one-line closing article, OCR failed on the short line, page 14).
  **No decorative in-word tatweel** (all 33 tatweel are the هـ enumerator or space-bounded enumerator
  dashes, kept). Track under `sources/judiciary/law/` + `data/judiciary_arabic_legal_llm/`. Validate:
  `make judiciary-law-track-validate`.

  While building this track a subtle tatweel-normalization bug was found and fixed: the in-word-strip
  rule treated the tatweel codepoint U+0640 (which falls inside the `ء-ي` range) as a letter, so a
  space-bounded **double**-dash " ــ " could have its second tatweel stripped to " ـ ". The strip is
  now run-based (only strips a whole run when the char *before* the run is a genuine in-word letter).
  An audit of all prior MOJ tracks found exactly **one** affected track — the criminal-procedure
  implementing regulation (2 provisions) — which was corrected in the same change (2 double-dashes
  restored; the 37 genuine in-word tatweel removals are unchanged).

## نظام ديوان المظالم — Law of the Board of Grievances (م/78، 1428هـ)

- **Law of the Board of Grievances (M/78, 19/9/1428هـ) verified + LLM-ready — the administrative-
  judiciary statute.** **نظام ديوان المظالم** — **26 records** (complete 1–26, no مكرر). Issued under
  the *same* royal decree as نظام القضاء; it organizes the independent administrative judiciary
  (قضاء إداري مستقل يرتبط مباشرة بالملك): the المحكمة الإدارية العليا / محاكم الاستئناف الإدارية /
  المحاكم الإدارية and the مجلس القضاء الإداري. In force; per its Article 26 it replaced the former
  Board Law (M/51, 1402هـ).
- **Different sourcing route (user-approved).** The Board sits under a separate authority and is **not
  on the MOJ legal portal**, and the BOE consolidated database (`laws.boe.gov.sa`) is **network-
  unreachable** here (TLS reset). So the text was taken from the **Board's own official machine-
  readable DOCX** and adjudicated **VISUALLY, page-by-page, against the Board's certified official PDF**
  (صورة طبق الأصل / هيئة الخبراء بمجلس الوزراء; 13 pages, committed with recorded sha256; the same scan
  is independently held by **WIPO Lex**, corroborating provenance). All **26/26** articles confirmed
  verbatim; OCR similarity (0.80–0.90) was noise-limited by scan quality, not divergence, so the visual
  read is the anchor.
- **Consolidated, minimally amended: 25 اصلية / 1 معدّلة / 0 ملغاة / 0 مضافة.** The single amendment is
  **Article 4** (composition of مجلس القضاء الإداري), amended by **قرار مجلس الوزراء 594 / المرسوم م/180
  (17/8/1446هـ)**, published in **جريدة أم القرى العدد 5072 (21 Feb 2025)** — it adds a fifth member
  category (عضوان من ذوي الخبرة والاختصاص) and a 4-year renewable royal-order tenure for items 4 and 5.
  Article 4 carries both its current amended body and its original 1428 body in `amendment_history`.
  The amendment **scope (Article 4 only) and substance are officially confirmed by the SPA
  Council-of-Ministers announcement**; its verbatim wording is from a secondary rendering of gazette
  5072 (BOE unreachable) and is **flagged at a slightly lower verbatim-trust tier** in the source
  artifact — the other 25 articles are double-official. Decorative in-word tatweel removed; the هـ
  enumerator and space-bounded enumerator dashes kept. Track under `sources/board_of_grievances/law/` +
  `data/board_of_grievances_arabic_legal_llm/`. Validate: `make board-of-grievances-law-track-validate`.

## نظام المحاماة — Code of Law Practice (م/38، 1422هـ)

- **Code of Law Practice (M/38, 28/7/1422هـ) verified + LLM-ready — the statute regulating the legal
  profession.** **نظام المحاماة** — **56 records** (complete 1–55 plus one مكرر: art 21-mukarrar). Covers
  قيد المحامين وشروط مزاولة المهنة, واجبات المحامين وحقوقهم, تأديب المحامي, and — newly — **تنظيم الترخيص
  لمكتب المحاماة الأجنبي** (foreign law-firm licensing). Back on the proven double-official MOJ pipeline
  (portal database × official MOJ PDF, 9 pages, committed with recorded sha256).
- **Substantially consolidated & amended: 35 اصلية / 8 معدلة / 12 مضافة / 1 ملغاة (art 25).** The
  amendment history spans decrees **M/52, M/61, M/66 (1443هـ), M/191 and M/21 (1447هـ)**; the 12 added
  articles are chiefly the new **foreign law-firm chapter (arts 44–55)** plus art 21-mukarrar, and each
  amended/added/repealed article carries its version history. The single repealed article (25) keeps its
  full body and is **FLAGGED, not deleted** (its LLM title gets a `(ملغاة)` suffix). No dual-status
  divergence — the section-API status equals the statuteStructure/PDF status for every article.
- **Cross-check: 55/56 matched outright (mean 0.968)**; the 1 flagged (art 41, معدلة — the foreign-legal-
  consultant article) was **visually adjudicated verbatim** on page 7. The PDF text-layer used Arabic
  Presentation Forms with a Farsi-yeh (U+06CC) fold and reversed word order; the verifier normalizes
  these (NFKC + yeh/heh/kaf folding + per-line word-reversal) so the text-layer becomes a clean channel.
  No decorative in-word tatweel; the هـ enumerator and space-bounded enumerator dashes kept. Track under
  `sources/law_practice/law/` + `data/law_practice_arabic_legal_llm/`. Validate:
  `make law-practice-law-track-validate`.
- **Implementing Regulation of the Code of Law Practice verified + LLM-ready — the current 1446هـ
  version.** **اللائحة التنفيذية لنظام المحاماة ١٤٤٦هـ** — **90 records** (complete 1–90, no مكرر) across
  9 chapters (التعريفات, الترخيص, الواجبات المهنية, المتدرب, المستشار غير السعودي, المأذون لهم بالترافع,
  مكتب المحاماة الأجنبي, التأديب, أحكام ختامية). **A fresh full issuance: all 90 اصلية** (0 معدلة / ملغاة /
  مضافة). **It supersedes the former 1423هـ regulation** (قرار وزير العدل ٦٧٦), whose portal status is
  **InActive** — that old one was **not ingested**. Same double-official MOJ pipeline (portal database ×
  official MOJ PDF, 17 pages, committed with recorded sha256). **Cross-check: 85/90 matched outright (mean
  0.962)**; the 5 flagged long/list articles (1, 3, 19, 60, 62) were **visually adjudicated verbatim**. One
  portal ordinal typo (art 13 label «الثاثة عشرة») is **preserved verbatim**. No dual-status divergence.
  Track under `sources/law_practice/regulation/` + `data/law_practice_arabic_legal_llm/`. Validate:
  `make law-practice-regulation-track-validate`.

## نظام المحاكم التجارية — Commercial Courts Law (م/93، 1441هـ)

- **Commercial Courts Law (M/93, 15/8/1441هـ) verified + LLM-ready — the specialized commercial
  judiciary.** **نظام المحاكم التجارية** — **96 records** (complete 1–96, no مكرر) across 11 chapters
  (أحكام عامة, الاختصاص, قيد الدعوى, نظر الدعوى, الحضور والغياب, الطلبات المستعجلة, الإثبات, صدور الحكم,
  أوامر الأداء, الاعتراض, أحكام ختامية). Same double-official MOJ pipeline (portal database × official
  MOJ PDF, 18 pages, committed with recorded sha256).
- **Consolidated & amended: 75 اصلية / 1 معدلة / 20 ملغاة.** The **20 repealed articles are the ENTIRE
  evidence chapter (arts 38–57, contiguous)**, repealed by the **Evidence Law (المرسوم م/43، 1443هـ)**
  which now governs evidence uniformly — the same supersession pattern seen in the Sharia Procedure
  regulation. Art 16 (jurisdiction) was amended by M/191 (1444هـ). The repealed articles **keep their full
  bodies and are FLAGGED, not deleted** (each carries its م/43 repeal history; the LLM title gets a
  `(ملغاة)` suffix). No dual-status divergence.
- **Cross-check: 93/96 matched outright (mean 0.958)**; the 3 flagged numbered-list articles (28, 62, 81)
  were **visually adjudicated verbatim**. No decorative in-word tatweel; the هـ enumerator and
  space-bounded enumerator dashes kept. Track under `sources/commercial_courts/law/` +
  `data/commercial_courts_arabic_legal_llm/`. Validate: `make commercial-courts-law-track-validate`.
- **Implementing Regulation of the Commercial Courts Law verified + LLM-ready — the current 1441هـ
  version.** **اللائحة التنفيذية لنظام المحاكم التجارية** — **281 records** (complete 1–281, no مكرر) across
  6 chapters (الأحكام العامة, إجراءات نظر الدعوى, الإثبات, إصدار الأحكام وأوامر الأداء, الاعتراض, أحكام خاصة
  ببعض الدعاوى — incl. the **class-action / الدعوى الجماعية** regime). **A fresh full issuance: all 281
  اصلية** (0 معدلة / ملغاة / مضافة). Same double-official MOJ pipeline (portal database × official MOJ PDF,
  34 pages, committed with recorded sha256). **Cross-check: 273/281 matched outright (mean 0.957)**; the
  8 flagged numbered-list articles (3, 41, 55, 90, 144, 155, 255, 267) were **visually adjudicated
  verbatim**. **Note:** the regulation retains its evidence chapter even though the *Law's* evidence
  articles (38–57) were repealed by the Evidence Law م/43 — the MOJ portal keeps the regulation's
  provisions اصلية/Active, and they are recorded **exactly as the portal classifies them** (no interpretive
  supersession added). No dual-status divergence. Track under `sources/commercial_courts/regulation/` +
  `data/commercial_courts_arabic_legal_llm/`. Validate: `make commercial-courts-regulation-track-validate`.

## نظام الإفلاس — Bankruptcy Law (م/89، 1439هـ) + اللائحة التنفيذية + القواعد الإجرائية

- **Bankruptcy Law (M/89, 28/5/1439هـ) verified + LLM-ready — the substantive insolvency
  framework.** **نظام الإفلاس** — **231 records** (complete 1–231, no مكرر) across the full
  procedure map: التسوية الوقائية, إعادة التنظيم المالي, التصفية, and the صغار المدينين variants,
  plus أمناء الإفلاس, the creditors' regime, and cross-border provisions. **229 اصلية / 2 معدلة**
  (المادتان 46 و147). Same double-official MOJ pipeline (portal database × official MOJ PDF, 38
  pages, committed with recorded sha256). **Cross-check: 225/231 matched outright (mean 0.965)**; the
  6 flagged numbered-list articles (39, 94, 145, 158, 196, 230) were **visually adjudicated verbatim**
  on the official MOJ pages. المادة 230 records the repeal of the old commercial-court insolvency
  articles (103–137) and the old protective-settlement law م/16 — recorded **exactly as the portal
  classifies it**. No dual-status divergence. Track under `sources/bankruptcy/law/` +
  `data/bankruptcy_arabic_legal_llm/`. Validate: `make bankruptcy-law-track-validate`.
- **Implementing Regulation of the Bankruptcy Law verified + LLM-ready.** **اللائحة التنفيذية
  لنظام الإفلاس** — **98 records** (complete 1–98, no مكرر) across 18 chapters detailing the
  procedures: administrative liquidation (التصفية الإدارية), debt priority, set-off, the Bankruptcy
  Committee, the Bankruptcy Register, trustees and experts, and closing provisions. Issued by
  Council of Ministers Decision No. 622 (04/01/1440هـ). **97 اصلية / 1 معدلة** — المادة الثانية,
  amended by Council of Ministers Decision No. 171 (20/03/1443هـ). Same double-official MOJ pipeline
  (portal database × official MOJ PDF, 21 pages, committed with recorded sha256). **Cross-check:
  98/98 matched outright (mean 0.968, min 0.913) — no article required visual adjudication.** No
  dual-status divergence. Track under `sources/bankruptcy/regulation/` +
  `data/bankruptcy_arabic_legal_llm/`. Validate: `make bankruptcy-regulation-track-validate`.
- **Rules Organizing Bankruptcy Case Procedures before the Commercial Courts verified + LLM-ready
  — completing the bankruptcy file (law + regulation + case rules).** **القواعد المنظمة لإجراءات
  قضايا الإفلاس في المحاكم التجارية** — **24 records** (complete 1–24, no مكرر) across 9 chapters:
  jurisdiction, the court unit managing bankruptcy cases, filing/registering the request, stay of
  claims, judicial notifications, and issuing/objecting to judgments. These are the litigation
  procedure rules that run bankruptcy cases before the commercial courts. Issued by Minister of
  Justice Decision No. 6421 (09/04/1441هـ). **All 24 اصلية** (fresh full issuance). Same
  double-official MOJ pipeline (portal database × official MOJ PDF, 9 pages, committed with recorded
  sha256). **Cross-check: 24/24 matched outright (mean 0.960, min 0.912) — no visual adjudication.**
  No dual-status divergence. Track under `sources/bankruptcy/case_rules/` +
  `data/bankruptcy_arabic_legal_llm/`. Validate: `make bankruptcy-case-rules-track-validate`.

## نظام التكاليف القضائية — Judicial Costs Law (م/16، 1443هـ) + اللائحة التنفيذية

- **Judicial Costs Law (M/16, 10/02/1443هـ) verified + LLM-ready — the statute governing
  litigation costs across the courts.** **نظام التكاليف القضائية** — **23 records** (complete 1–23,
  no مكرر). Caps costs at 5% of the claim value (max SAR 1,000,000), sets when costs are due/refunded,
  the reduction on amicable settlement, and the exempt categories (prisoners, workers under the Labor
  Law, government bodies). Issued by Royal Decree M/16. **All 23 اصلية** (fresh full issuance). Same
  double-official MOJ pipeline (portal database × official MOJ PDF, 4 pages, committed with recorded
  sha256). **Cross-check: 22/23 matched outright (mean 0.958); the numbered-list article 12 visually
  adjudicated verbatim.** No dual-status divergence. Track under `sources/judicial_costs/law/` +
  `data/judicial_costs_arabic_legal_llm/`. Validate: `make judicial-costs-law-track-validate`.
- **Implementing Regulation of the Judicial Costs Law verified + LLM-ready.** **اللائحة التنفيذية
  لنظام التكاليف القضائية** — **17 records** (complete 1–17, no مكرر) across 4 chapters: estimating
  judicial costs (the percentage tiers by claim value + fixed amounts for value-undetermined actions),
  estimating costs for requests, the final estimate and its collection, and closing provisions. Issued
  by Council of Ministers Decision No. 519 (11/09/1443هـ). **All 17 اصلية** (fresh full issuance). Same
  double-official MOJ pipeline (portal database × official MOJ PDF, 5 pages, committed with recorded
  sha256). **Cross-check: 16/17 matched outright (mean 0.954); the percentage-table article 2 visually
  adjudicated verbatim.** No dual-status divergence. Track under `sources/judicial_costs/regulation/` +
  `data/judicial_costs_arabic_legal_llm/`. Validate: `make judicial-costs-regulation-track-validate`.

## نظام التحكيم — Arbitration Law (م/34، 1433هـ) + اللائحة التنفيذية

- **Arbitration Law (M/34, 18/07/1433هـ) verified + LLM-ready — the governing statute for domestic
  and international commercial arbitration seated in the Kingdom.** **نظام التحكيم** — **58 records**
  (numbered 1–58 by ordinal position, no مكرر) across 8 أبواب: the arbitration agreement, the tribunal,
  proceedings, the award, nullity, and enforcement. **55 اصلية / 3 معدلة** (المواد 10، 24، 50 —
  م24 بالمرسوم م/8 1443هـ، م10 و م50 بالمرسوم م/21 1447هـ). **Numbering anomaly (documented):** the
  official source — **both the portal AND the PDF** — labels the 31st article «المادة الحادية والعشرون»
  (a duplicate of article 21's label; there is no «الحادية والثلاثون»). The label is **preserved
  verbatim**; the ordinal position (31) is used for indexing with a factual positional note in the LLM
  title. Same double-official MOJ pipeline (portal database × official MOJ PDF, 12 pages, committed with
  recorded sha256). **Cross-check: 57/58 matched outright (mean 0.961); the list article 42 visually
  adjudicated verbatim.** No dual-status divergence. Track under `sources/arbitration/law/` +
  `data/arbitration_arabic_legal_llm/`. Validate: `make arbitration-law-track-validate`.
- **Implementing Regulation of the Arbitration Law verified + LLM-ready.** **اللائحة التنفيذية لنظام
  التحكيم** — **19 records** (complete 1–19, no مكرر) — the competent court, tribunal constitution and
  appointment of arbitrators, notifications, and the interplay with the Law. Issued by Council of
  Ministers Decision No. 541 (14/09/1438هـ). **18 اصلية / 1 ملغاة** — المادة السابعة, repealed by Council
  of Ministers Decision No. 249, **kept with its body + (ملغاة) flag, not deleted.** Same double-official
  MOJ pipeline (portal database × official MOJ PDF, 3 pages, committed with recorded sha256).
  **Cross-check: 19/19 matched outright (mean 0.964) — no visual adjudication.** No dual-status
  divergence. Track under `sources/arbitration/regulation/` + `data/arbitration_arabic_legal_llm/`.
  Validate: `make arbitration-regulation-track-validate`.

## نظام الأوراق التجارية — Commercial Papers Law (م/37، 1383هـ)

- **Commercial Papers Law (M/37, 11/10/1383هـ) verified + LLM-ready — the foundational statute for
  negotiable/commercial instruments.** **نظام الأوراق التجارية** — **121 records** (complete 1–121,
  no مكرر) across 26 chapters covering the bill of exchange (الكمبيالة), the promissory note (السند
  لأمر), the cheque (الشيك), and the penalties (الجزاءات). In force (ساري). **118 اصلية / 3 معدلة** —
  المواد 118، 119، 120 معدّلة بالمرسوم **م/45 (12/9/1409هـ)**، تحمل النص الحالي المعدّل والنص الأصلي 1383هـ
  في السجل. المادة 38 نصّها أصلي مع تفسير رسمي (قرار مجلس الوزراء 251، 1442هـ) في سجلها.
- **Distinct provenance (disclosed):** the MOJ laws-gateway does not host this older law and the BOE
  portal is not directly reachable from the build environment, so the official text of the **Bureau of
  Experts** (هيئة الخبراء بمجلس الوزراء) was captured from the **Wayback Machine archive** of the official
  BOE page and **cross-verified byte-identical across two independent-date snapshots (2021 + 2025)** — all
  121 article bodies match exactly (zero differences). Both raw snapshots are committed under
  `inputs/commercial_papers_boe_snapshots/` with recorded sha256, and the concatenated corpus text carries
  a recorded sha256. This differs from the MOJ portal×PDF double pipeline used by the other tracks. Track
  under `sources/commercial_papers/law/` + `data/commercial_papers_arabic_legal_llm/`. Validate:
  `make commercial-papers-law-track-validate`.

## نظام السجل التجاري + نظام الأسماء التجارية (م/83، 1446هـ)

- **Commercial Register Law (M/83, 19/03/1446هـ) verified + LLM-ready.** **نظام السجل التجاري** —
  **29 records** (complete 1–29, no مكرر) across 6 chapters: entry in the register, cancellation/
  suspension, the registration certificate's evidentiary weight, and violations. Fresh full issuance
  (**all 29 اصلية**) superseding the former law (م/1، 1416هـ). Track under `sources/commercial_register/law/`.
  Validate: `make commercial-register-law-track-validate`.
- **Trade Names Law (M/83, 19/03/1446هـ) verified + LLM-ready.** **نظام الأسماء التجارية** — **23 records**
  (complete 1–23, no مكرر) across 5 chapters: the trade name, its reservation and registration,
  cancellation/removal, and violations. Fresh full issuance (**all 23 اصلية**) superseding the former law
  (م/15، 1420هـ). Both laws were issued together by the same decree م/83. Track under `sources/trade_names/law/`.
  Validate: `make trade-names-law-track-validate`.
- **Provenance (disclosed):** both laws use the same BOE-via-Wayback route as the Commercial Papers Law —
  the official Bureau of Experts text, **cross-verified byte-identical across two independent-date snapshots**
  (السجل: 2025-01 + 2025-04؛ الأسماء: 2024-11 + 2025-12), with both raw snapshots committed under
  `inputs/commercial_registration_boe_snapshots/` + recorded sha256, and a recorded corpus-text sha256.

## نظام الوكالات التجارية — Commercial Agencies Law (م/11، 1382هـ)

- **Commercial Agencies Law (M/11, 20/02/1382هـ) verified + LLM-ready.** **نظام الوكالات التجارية** —
  **6 records** (complete 1–6, no مكرر): restricting commercial agency to Saudis, the Commercial Agencies
  Register at the Ministry of Commerce, registration fees, and penalties. In force (ساري). **3 اصلية /
  3 معدلة** — م4 مُستبدلة بالمرسوم **م/32 (1400هـ)** (العقوبة 5,000–50,000 ريال)، م5 مُستبدلة بالمرسوم
  **م/8 (1393هـ)** (رسم القيد 500 ريال)، وكلٌّ تحمل النص الحالي والأصلي في السجل؛ م6 نصّها الأصلي (النفاذ)
  قائم مع **إضافة** لجنة تطبيق العقوبات بالمرسوم **م/5 (1389هـ)** مسجّلة في السجل. Same BOE-via-Wayback
  route — cross-verified byte-identical across two snapshots (2023 + 2025), both committed under
  `inputs/commercial_agencies_boe_snapshots/` + recorded sha256. Track under `sources/commercial_agencies/law/`.
  Validate: `make commercial-agencies-law-track-validate`.

## نظام الغرف التجارية — Chambers of Commerce Law (م/37، 1442هـ)

- **Chambers of Commerce Law (M/37, 22/04/1442هـ) verified + LLM-ready.** **نظام الغرف التجارية** —
  **66 records** (complete 1–66, no مكرر) across 10 chapters: the chamber (formation and functions, its
  administrative organs — general assembly, board of directors, general secretariat — subscription,
  finances, performance evaluation), the federation of chambers, and the committees. In force (ساري —
  confirmed by the status badge in both recent snapshots; an early 2022 snapshot's icon legend was
  misread as the status). Fresh consolidated issuance (**all 66 اصلية**). Same BOE-via-Wayback route —
  cross-verified byte-identical across two recent snapshots (2025-05 + 2026-01), both committed under
  `inputs/chambers_of_commerce_boe_snapshots/` + recorded sha256. Track under `sources/chambers_of_commerce/law/`.
  Validate: `make chambers-of-commerce-law-track-validate`.

## نظام الدفاتر التجارية — Commercial Books Law (م/61، 1409هـ)

- **Commercial Books Law (M/61, 17/12/1409هـ) verified + LLM-ready.** **نظام الدفاتر التجارية** —
  **16 records** (complete 1–16, no مكرر): the obligation of every merchant to keep commercial
  (accounting) books, the required books (journal and inventory), how entries are made and kept, their
  evidentiary weight, and penalties. In force (ساري). Consolidated issuance (**all 16 اصلية**). Same
  BOE-via-Wayback route — cross-verified byte-identical across two snapshots ~13 months apart
  (2024-05 + 2025-06), both committed under `inputs/commercial_books_boe_snapshots/` + recorded sha256.
  Track under `sources/commercial_books/law/`. Validate: `make commercial-books-law-track-validate`.

## نظام مكافحة غسل الأموال — Anti-Money Laundering Law (م/20، 1439هـ)

- **Anti-Money Laundering Law (M/20, 14/2/1439هـ) verified + LLM-ready.** **نظام مكافحة غسل الأموال** —
  **52 records** (numbered 1–51 by ordinal position + one مكرر article, art 49 مكرر): definitions, the
  money-laundering offences and penalties, seizure and confiscation, preventive measures and customer
  due diligence for financial institutions and DNFBPs, the FIU and reporting, supervision,
  international cooperation, and general provisions. In force (ساري). **Consolidated amended:
  44 اصلية / 7 معدلة (arts 14, 15, 16, 18, 28, 33, 50) / 1 مضافة (art 49 مكرر)** — every
  amended/added article carries its history; **all amendments were introduced by Royal Decree
  M/223 (27/10/1447هـ)**. Back to the **MOJ double-official pipeline**: fetched article-by-article
  from the MOJ legal-portal database (get-Section-Changes) and cross-verified against the official
  MOJ PDF (49/52 MATCHES_PDF outright, mean 0.961; the 3 long definition/list articles — the first
  «التعريفات» article, art 24 and art 43 — visually adjudicated verbatim on the rendered pages; PDF
  committed with recorded sha256, 11 pages). No dual-status divergence. Track under
  `sources/aml/law/`. Validate: `make aml-law-track-validate`.

## نظام التوثيق — Notarization Law (م/164، 1441هـ)

- **Notarization Law (M/164, 19/11/1441هـ) verified + LLM-ready.** **نظام التوثيق** —
  **57 records** (complete 1–57, no مكرر): definitions, notary offices (كتابات وكتاب العدل) and their
  jurisdiction, the notary and the notarization office, marriage-contract officiants, licensing and
  advertising the profession, duties and prohibitions, notarization procedures and registers, the
  evidentiary weight and protection of documents, oversight, and penalties. In force (ساري).
  **Consolidated amended: 52 اصلية / 5 معدلة** (arts 11, 12, 38, 40 by Royal Decree M/21 26/1/1447هـ;
  art 15 by M/191 29/11/1444هـ) — each amended article carries its history. MOJ double-official
  pipeline: fetched article-by-article from the MOJ portal database and cross-verified against the
  official MOJ PDF (**57/57 MATCHES_PDF outright, mean 0.964, min 0.902 — no visual adjudication**;
  PDF committed with recorded sha256, 10 pages). ADDITIONALLY corroborated against the **Bureau of
  Experts** official portal (via Wayback archive): all 52 اصلية byte-near-identical and the 5 amended
  articles confirmed by the BOE «تعديلات المادة» popups (two independent official authorities agree).
  Track under `sources/tawtheeq/law/`. Validate: `make tawtheeq-law-track-validate`.
- **Implementing Regulation of the Notarization Law (Minister of Justice Decision 1948, 1/6/1442هـ) verified + LLM-ready.**
  **اللائحة التنفيذية لنظام التوثيق** — **31 records**: 30 numbered articles (1–30) across 9 chapters + record 31, the
  official fee schedule «جدول المقابل المالي» (min/max financial consideration per notarization act). In force (ساري).
  Fresh full issuance — **all 31 اصلية**. MOJ portal cross-checked against the official MOJ PDF (9 pages, sha256
  recorded). **21/31 matched outright ≥0.90; the OCR channel was unavailable for this PDF in the build environment and
  its text layer scrambles clauses/drops glyphs on 10 list articles (1, 2, 4, 11, 18, 23, 24, 26, 27, 28) — each was
  adjudicated VISUALLY VERBATIM on the rendered official PDF pages** (every clause confirmed present and matching the
  portal text). No dual-status divergence. Track under `sources/tawtheeq/regulation/`. Validate:
  `make tawtheeq-regulation-track-validate`.

## نظام التسجيل العيني للعقار — Real Estate In-Kind Registration Law (م/91، 1443هـ)

- **Real Estate In-Kind Registration Law (M/91, 19/9/1443هـ) verified + LLM-ready.** **نظام التسجيل العيني للعقار**
  — **40 records** (complete 1–40, no مكرر): the foundational statute of the in-kind (real-rights) real estate register —
  the register and its pages, real estate zones and the first in-kind registration, subsequent dispositions and
  derivative rights, the conclusiveness (حجية) and protection of registered rights, objections/corrections, and closing
  provisions. In force (ساري). **Consolidated amended: 37 اصلية / 3 معدلة** (arts 6, 9, 11 by Royal Decree M/123
  10/6/1447هـ). **⚠️ Supersession:** this is the IN-FORCE law; it replaces the older repealed law of the same name
  (M/6, 1423هـ — InActive/ملغي on the MOJ portal), which is **not ingested**. MOJ double-official pipeline: **40/40
  MATCHES_PDF outright** (mean 0.963, min 0.903 — no visual adjudication; PDF committed with recorded sha256, 7 pages).
  No dual-status divergence. Opens the real-estate cluster. Track under `sources/real_estate_registration/law/`.
  Validate: `make real-estate-registration-law-track-validate`.
- **Implementing Regulation of the Real Estate Registration Law (issued 27/1/1444هـ) verified + LLM-ready.**
  **اللائحة التنفيذية لنظام التسجيل العيني للعقار** — **51 records** (complete 1–51, no مكرر): the high committee, the
  real estate register/database, real estate zones and the first in-kind registration procedures, tolerances and survey
  specifications, and the real estate registrar's licensing. In force (ساري). Fresh full issuance — **all 51 اصلية**.
  **⚠️ Supersession:** replaces the older repealed regulation of the same name (1425هـ, InActive), **not ingested**.
  MOJ portal cross-checked against the official MOJ PDF (13 pages, sha256 recorded): **46/51 matched outright**; 5
  long/table articles (1, 6, 13, 42, 49) — arts 13 & 42 being official specification tables — were adjudicated
  **VISUALLY VERBATIM** on the rendered pages (every clause confirmed; art 42's official English remote-sensing spec
  tokens RGB/NIR/band/bit/minimum kept verbatim). No dual-status divergence. Completes the in-kind registration pair.
  Track under `sources/real_estate_registration/regulation/`. Validate:
  `make real-estate-registration-regulation-track-validate`.

## نظام الرهن العقاري المسجل — Registered Real Estate Mortgage Law (م/49، 1433هـ)

- **Registered Real Estate Mortgage Law (M/49, 13/8/1433هـ) verified + LLM-ready.** **نظام الرهن العقاري المسجل** —
  **46 records** (complete 1–46, no مكرر): the governing statute of the registered real estate mortgage as a real
  security right — creating the mortgage and its conditions, its effects on the mortgagor and mortgagee, its transfer
  and extinguishment, and enforcement over the mortgaged property. In force (ساري). Fresh full issuance — **all 46
  اصلية**. MOJ double-official pipeline: **44/46 matched outright** (mean 0.948); the 2 long articles (11, 14) were
  adjudicated **VISUALLY VERBATIM** on the rendered pages (every word present). No dual-status divergence; PDF committed
  with recorded sha256 (6 pages). Extends the real-estate cluster (secured finance). Track under
  `sources/real_estate_mortgage/law/`. Validate: `make real-estate-mortgage-law-track-validate`.

## نظام التمويل العقاري — Real Estate Finance Law (م/50، 1433هـ)

- **Real Estate Finance Law (M/50, 13/8/1433هـ) verified + LLM-ready.** **نظام التمويل العقاري** —
  **15 records** (complete 1–15, no مكرر): the governing statute regulating the real estate finance sector —
  supervision and licensing of real estate financiers, the central bank's authority over the sector, government
  support for beneficiaries' housing finance, the secondary market for real estate finance (السوق الثانوية), and
  publication and enforcement. In force (ساري). Fresh full issuance — **all 15 اصلية**. MOJ double-official pipeline:
  **all 15/15 matched outright** (mean 0.965, min 0.933) — no visual adjudication needed. No dual-status divergence;
  PDF committed with recorded sha256 (5 pages). Extends the real-estate cluster (housing finance). Track under
  `sources/real_estate_finance/law/`. Validate: `make real-estate-finance-law-track-validate`.

## نظام ملكية الوحدات العقارية وفرزها وإدارتها — Real Estate Unit Ownership Law (م/85، 1441هـ)

- **Real Estate Unit Ownership Law (M/85, 2/7/1441هـ) verified + LLM-ready.** **نظام ملكية الوحدات العقارية وفرزها
  وإدارتها** — **33 records** (complete 1–33, no مكرر): the governing statute for condominium/multi-unit real estate —
  partition of the property (فرز العقار), ownership provisions, the owners' association (جمعية الملاك), management and
  maintenance. In force (ساري). Fresh full issuance — **all 33 اصلية**. **Supersession:** it replaced (حل محل) the
  repealed 1423هـ unit-ownership-and-partition law, which is **NOT ingested**. MOJ double-official pipeline: **all 33/33
  matched outright** (mean 0.971, min 0.943) — no visual adjudication needed. No dual-status divergence; PDF committed
  with recorded sha256 (8 pages). Extends the real-estate cluster (condominium ownership). Track under
  `sources/real_estate_units/law/`. Validate: `make real-estate-units-law-track-validate`.

## اللائحة التنفيذية لنظام ملكية الوحدات العقارية — Real Estate Unit Ownership Law Implementing Regulation (قرار 168، 1441هـ)

- **Real Estate Unit Ownership Law Implementing Regulation (Ministerial Decision 168, 22/10/1441هـ) verified +
  LLM-ready.** **اللائحة التنفيذية لنظام ملكية الوحدات العقارية وفرزها وإدارتها** — **41 records** (complete 1–41, no
  مكرر): implements M/85; covers partition, ownership provisions, the owners' association and complex association
  (جمعية الملاك / جمعية المجمع), management, maintenance, and the auditor regime. In force (ساري). **Consolidated
  amended:** 39 اصلية / 2 معدلة (arts 4, 10 — art 4 by Ministerial Decisions 4500000499 then 4600003967; art 10 by
  4500000499); each amended article keeps its full version history. MOJ double-official pipeline: **40/41 matched
  outright** (mean 0.964); the 1 long article (27, the auditor article) was adjudicated **VISUALLY VERBATIM** on the
  rendered pages (every word present). No dual-status divergence; PDF committed with recorded sha256 (9 pages).
  Completes the real-estate condominium cluster (law + regulation). Track under
  `sources/real_estate_units/implementing_regulation/`. Validate: `make real-estate-units-regulation-track-validate`.

## نظام تملك غير السعوديين للعقار — Non-Saudi Real Estate Ownership Law (م/14، 1447هـ)

- **Non-Saudi Real Estate Ownership Law (M/14, 19/1/1447هـ) verified + LLM-ready.** **نظام تملك غير السعوديين للعقار
  لعام ١٤٤٧هـ** — **15 records** (complete 1–15, no مكرر): the governing statute for ownership and acquisition of real
  rights over real estate by non-Saudis — the geographic scope set by the Council of Ministers, listed-company
  ownership, premium-residency provisions, diplomatic-mission premises, registration with the Real Estate General
  Authority, fees/taxes, penalties, and the enforcement committee. In force (ساري). Fresh full issuance — **all 15
  اصلية**. **Supersession** (per its art 14): it replaced the repealed Non-Saudi Ownership and Investment Law (M/15,
  1421هـ, InActive), which is **NOT ingested**. MOJ double-official pipeline: **12/15 matched outright** (mean 0.945);
  the 3 articles (2, 7, 12) were adjudicated **VISUALLY VERBATIM** on the rendered pages (every word present, zero
  missing unigrams). No dual-status divergence; PDF committed with recorded sha256 (3 pages). Extends the real-estate
  cluster (foreign ownership). Track under `sources/foreign_ownership/law/`. Validate:
  `make foreign-ownership-law-track-validate`.

## نظام التصرف في العقارات البلدية + لائحته — Municipal Real Estate Disposal Law + Regulation

- **Municipal Real Estate Disposal Law (M/64, 15/11/1392هـ).** **نظام التصرف في العقارات البلدية** — **6 records**
  (all اصلية): inalienability of municipal public property, disposal of private municipal property, and municipalities
  without councils. In force. MOJ double-official: **6/6 matched outright** (mean 0.974), no visual adjudication. PDF
  committed (1 page). Track under `sources/municipal_realestate/law/`. Validate:
  `make municipal-realestate-law-track-validate`.
- **Municipal Real Estate Disposal Regulation (High Order 40152, 29/6/1441هـ).** **لائحة التصرف بالعقارات البلدية** —
  **35 records** (1–34 + one مكرر, art 13 مكرر): definitions, municipal real estate, surplus disposal, exchange
  (المعاوضة), investment/competition, and committees. In force. **Consolidated amended:** 31 اصلية / 3 معدلة (arts 10,
  13, 21) / 1 مضافة (art 13 مكرر), each with full history. **Supersession** (per its art 33): replaced the repealed
  1423هـ regulation, **NOT ingested**. MOJ double-official: **31/35 matched outright** (mean 0.953); the 4 articles (6,
  13, 14, 33) were adjudicated **VISUALLY VERBATIM**. PDF committed (6 pages). Track under
  `sources/municipal_realestate/implementing_regulation/`. Validate: `make municipal-realestate-regulation-track-validate`.

## تنظيم تملك مواطني دول المجلس للعقار — GCC Citizens Real Estate Ownership Regulation (م/22، 1432هـ)

- **GCC Citizens Real Estate Ownership Regulation (M/22, 3/4/1432هـ).** **تنظيم تملك مواطني دول المجلس للعقار في الدول
  الأعضاء بمجلس التعاون لغرض السكن والاستثمار** — **6 records** (all اصلية): GCC citizens' right to rent/own built real
  estate and land for housing or investment, land use, disposal, expropriation, and the Makkah/Madinah prohibition. In
  force. **Supersession:** replaced the 1422هـ Supreme-Council version, **NOT ingested**. MOJ double-official: **6/6
  matched outright** (mean 0.976), no visual adjudication. PDF committed (1 page). Track under
  `sources/gcc_ownership/law/`. Validate: `make gcc-ownership-law-track-validate`.

## نظام مكافحة جرائم الإرهاب وتمويله — Law on Combating Crimes of Terrorism and its Financing (م/21، 1439هـ)

- **Law on Combating Crimes of Terrorism and its Financing (M/21, 12/2/1439هـ) verified + LLM-ready.** **نظام مكافحة
  جرائم الإرهاب وتمويله** — **99 records** (1–96 + three مكرر: 59، 63، 81 مكرر): the primary criminal statute on
  terrorism and its financing — definitions, general provisions, procedures, penalties, confiscation, precautionary
  measures, international cooperation, the General Directorate of Financial Investigations, and oversight. Complements
  the Anti-Money Laundering Law (financial-crime cluster). In force. **Consolidated amended:** 88 اصلية / 8 معدلة (arts
  4, 9, 12, 63, 67, 70, 71, 83) / 3 مضافة (arts 59، 63، 81 مكرر), each with full history. **Supersession:** replaced the
  repealed M/16 1435هـ terrorism law. MOJ double-official pipeline: **90/99 matched outright** (mean 0.955); the 9 long
  articles (1, 3, 10, 39, 43, 50, 56, 82, 83) were adjudicated **VISUALLY VERBATIM** on the rendered pages (every word
  present; the few unigram gaps were OCR gluing the trailing comma to a word, confirmed on the pages). Portal data note:
  article 75's doubled label was de-duplicated (no legal text affected). PDF committed (15 pages). Track under
  `sources/terrorism/law/`. Validate: `make terrorism-law-track-validate`.

## اللائحة التنفيذية لنظام مكافحة جرائم الإرهاب وتمويله — Implementing Regulation (قرار 228، 1440هـ)

- **Implementing Regulation of the Law on Combating Crimes of Terrorism and its Financing (Council of Ministers
  Decision 228, 2/5/1440هـ) verified + LLM-ready.** **اللائحة التنفيذية لنظام مكافحة جرائم الإرهاب وتمويله** —
  **28 records** (1–26 + two مكرر: 20، 23 مكرر): defines the financial activities/professions and controlling bodies
  referenced by the law; arrest/search/seizure procedures; enforcement of foreign final judgments; asset recovery and
  confiscation-sharing; obligations of financial institutions and non-financial businesses; and the General Directorate
  of Financial Investigations. In force. **Consolidated amended:** 18 اصلية / 7 معدلة (arts 2, 4, 16, 18, 21, 23, 24) /
  **1 ملغاة** (art 9 — full body kept and **flagged, not deleted**) / 2 مضافة (arts 20، 23 مكرر), each with full
  history. MOJ double-official pipeline: **26/28 matched outright** (mean 0.947); the 2 list articles (1, 4) were
  adjudicated **VISUALLY VERBATIM** on the rendered pages. PDF committed (9 pages). Completes the terrorism-financing
  cluster (law + regulation). Track under `sources/terrorism/implementing_regulation/`. Validate:
  `make terrorism-regulation-track-validate`.

## نظام الأحداث + لائحته — Juveniles Law + Implementing Regulation (م/113، 1439هـ / قرار 237، 1442هـ)

- **Juveniles Law (M/113, 19/11/1439هـ) verified + LLM-ready.** **نظام الأحداث** — **24 records** (complete 1–24, no
  مكرر): juvenile criminal responsibility and procedure — definitions, penal accountability, Hijri age calculation,
  arrest/complaint procedures, investigative detention, the juvenile's Dar (facility), social-investigation reports,
  trial before the court, age-based measures/penalties (below/at-or-above 15), conditional release, and joint
  adult/juvenile offenses. In force. Fresh full issuance — **all 24 اصلية**. MOJ double-official pipeline: **22/24
  matched outright** (mean 0.951); the 2 articles (5, 20) were adjudicated **VISUALLY VERBATIM** on the rendered pages.
  PDF committed (3 pages). Track under `sources/juveniles/law/`. Validate: `make juveniles-law-track-validate`.
- **Implementing Regulation (Council of Ministers Decision 237, 16/4/1442هـ).** **اللائحة التنفيذية لنظام الأحداث** —
  **13 records** (complete 1–13, no مكرر): age-determination, flagrante-delicto arrest/complaint procedures for the
  juvenile plaintiff, arrest of the juvenile, the unidentified juvenile, detention-extension requests, safeguarding the
  juvenile in the Dar, investigation, the social-investigation report, cases needing no formal indictment, social
  supervision, the juvenile's special register, and conditional release. In force. Fresh full issuance — **all 13
  اصلية**. MOJ double-official pipeline: **12/13 matched outright** (mean 0.947); article 4 was adjudicated **VISUALLY
  VERBATIM**. PDF committed (2 pages). Completes the juvenile-justice cluster (law + regulation). Track under
  `sources/juveniles/implementing_regulation/`. Validate: `make juveniles-regulation-track-validate`.

## نظام حماية المبلغين والشهود والخبراء والضحايا — Whistleblower, Witness, Expert and Victim Protection Law (م/148، 1445هـ)

- **Whistleblower, Witness, Expert and Victim Protection Law (M/148, 8/8/1445هـ) verified + LLM-ready.**
  **نظام حماية المبلغين والشهود والخبراء والضحايا** — **37 records** (complete 1–37, no مكرر): definitions, the duty
  to report and reporting channels, protective measures (identity confidentiality, physical protection, relocation,
  testimony via technical means), the responsible authority's powers, exemption from criminal/civil/disciplinary
  liability for good-faith reporting, penalties for retaliation/threats/bribery against protected persons, and
  inter-authority coordination. In force. Fresh full issuance — **all 37 اصلية**. MOJ double-official pipeline:
  **36/37 matched outright** (mean 0.9582, min 0.741); article 26 (penalty clauses for threats/bribery against
  protected persons) was adjudicated **VISUALLY VERBATIM** on the rendered page. PDF committed (6 pages). Track
  under `sources/whistleblower/law/`. Validate: `make whistleblower-law-track-validate`.

## لائحة التفتيش القضائي — Judicial Inspection Regulation (22/7/1435هـ)

- **Judicial Inspection Regulation (Supreme Judicial Council, 22/7/1435هـ) verified + LLM-ready.**
  **لائحة التفتيش القضائي** — **68 records** (complete 1–68, no مكرر): definitions, formation and powers of the
  Judicial Inspection Administration, membership qualifications, periodic/urgent/directive inspection of appellate
  and first-instance-court judges, complaints and investigation procedures, the disciplinary lawsuit, and closing
  provisions. Per its own final article (68) it replaces the prior 2/11/1430هـ regulation (not ingested). In force.
  Fresh full issuance — **all 68 اصلية**. MOJ double-official pipeline: **52/68 matched outright** (mean 0.9212,
  min 0.718); 16 articles fell below the automated similarity floor — this PDF's dense multi-article-per-page
  layout degraded both the text-layer and OCR channels (confirmed near-total word-overlap, no missing content) —
  and were each adjudicated **VISUALLY VERBATIM** on the rendered pages. PDF committed (15 pages). Track under
  `sources/judicial_inspection/regulation/`. Validate: `make judicial-inspection-regulation-track-validate`.

## لائحة قسمة الأموال المشتركة — Regulation on the Division of Jointly-Owned Property (19/5/1439هـ)

- **Regulation on the Division of Jointly-Owned Property (Minister of Justice Decision 1610, 19/5/1439هـ) verified +
  LLM-ready.** **لائحة قسمة الأموال المشتركة** — **48 records** (complete 1–48, no مكرر; flat article structure with
  no chapter/section wrapper): definitions, amicable division of jointly-owned property, splitting the division
  lawsuit, division of the property's usufruct, examining the litigants, the competent circuit, division disputes,
  disclosure duties, partition and demarcation, compulsory division, preservation and custody of jointly-owned
  property, the appointed guardian, liquidators, the guarantor surety, the judicial custodian, liquidation
  procedures, settling the jointly-owned property's debts, and licensing/classification of liquidators. In force.
  Fresh full issuance — **all 48 اصلية**. MOJ double-official pipeline: **all 48/48 matched outright** (mean 0.9661,
  min 0.913; no visual adjudication needed). PDF committed (6 pages). Track under `sources/qismah/regulation/`.
  Validate: `make qismah-regulation-track-validate`.

## قواعد السلوك المهني للمحامين — Professional Conduct Rules for Lawyers (24/12/1442هـ)

- **Professional Conduct Rules for Lawyers (Minister of Justice Decision 3453, 24/12/1442هـ, consolidated through
  Decision 676, 19/4/1446هـ) verified + LLM-ready.** **قواعد السلوك المهني للمحامين** — **47 records** (numbered
  1–42, 44–46, plus 2 مكرر rules 9 and 45): general rules, the lawyer-client relationship, legal consultations,
  court pleadings, dealings with non-clients, dealings with the media, legal establishments, and closing provisions.
  In force. CONSOLIDATED AMENDED: **44 اصلية / 1 معدلة (rule 38) / 2 مضافة (rules 9 مكرر, 45 مكرر)**, each carrying
  full version history. **DOCUMENTED SOURCE ANOMALY:** rule 43 (القاعدة الثالثة والأربعون) is entirely absent from
  both the official MOJ portal statute structure and the official MOJ PDF — chapter 7 (Legal Establishments) ends
  at rule 42 and chapter 8 (Closing Provisions) opens directly at rule 44, independently confirmed on the rendered
  PDF pages, not a fetch artifact; preserved verbatim as issued, not filled or renumbered. MOJ double-official
  pipeline: **all 47/47 matched outright** (mean 0.9551, min 0.900; no visual adjudication needed). PDF committed
  (10 pages). Track under `sources/sulook/regulation/`. Validate: `make sulook-regulation-track-validate`.

## اللائحة المنظمة لأعمال أعوان القضاء — Regulation Organizing the Work of Judicial Assistants (8/7/1435هـ)

- **Regulation Organizing the Work of Judicial Assistants (Minister of Justice Decision 50335, 8/7/1435هـ) verified
  + LLM-ready.** **اللائحة المنظمة لأعمال أعوان القضاء** — **35 records** (complete 1–35, no مكرر): duties of
  clerks of the court record (كُتّاب الضبط), clerks of the register (كُتّاب السجل), researchers (باحثين), and
  process-servers/notifiers (المحضرين). In force. Fresh full issuance — **all 35 اصلية**. MOJ double-official
  pipeline: **33/35 matched outright** (mean 0.9545, min 0.785); 2 long list articles (9, 12) were adjudicated
  **VISUALLY VERBATIM** on the rendered pages. PDF committed (9 pages). Track under `sources/aawan/regulation/`.
  Validate: `make aawan-regulation-track-validate`.

## قواعد العمل في مكاتب المصالحة وإجراءاته — Rules for the Work of Conciliation Offices and its Procedures (29/11/1440هـ)

- **Rules for the Work of Conciliation Offices and its Procedures (Minister of Justice Decision 5595, 29/11/1440هـ)
  verified + LLM-ready.** **قواعد العمل في مكاتب المصالحة وإجراءاته** — **29 records**: **26 numbered articles**
  (complete 1–26, no مكرر) — definitions, referral to and jurisdiction of conciliation offices, amicable
  settlement, registered conciliators, conciliation procedures, the settlement record (محضر الصلح), and closing
  provisions — plus a **3-part case-category annex schedule** (General / Personal Status / Criminal, 17 rows
  total) listing maximum conciliation-session timelines by case type. Per its own final article it replaces the
  prior Ministerial Decision 53792 (27/7/1435هـ) rules (not ingested). In force. Fresh full issuance — **all 26
  articles اصلية**. MOJ double-official pipeline: **24/26 articles matched outright** (mean 0.9464, min 0.627);
  articles 1 and 26 plus all 3 annex tables were adjudicated **VISUALLY VERBATIM** (tables confirmed row-for-row
  against the rendered pages, since table-extraction reliably degrades the automated channels). PDF committed
  (11 pages). Track under `sources/muslaha/regulation/`. Validate: `make muslaha-regulation-track-validate`.

## القواعد المنظمة لإجراءات الإفلاس العابرة للحدود — Rules Organizing Cross-Border Insolvency Procedures (14/5/1444هـ)

- **Rules Organizing Cross-Border Insolvency Procedures (Minister of Commerce Decision 149, 14/5/1444هـ)
  verified + LLM-ready.** **القواعد المنظمة لإجراءات الإفلاس العابرة للحدود** — **23 records** (numbered 1–23,
  no مكرر) implementing the Bankruptcy Law (M/50, 1439هـ) — scope and definitions, recognition of foreign
  insolvency proceedings, cooperation between Saudi and foreign courts/representatives, and concurrent
  proceedings. In force. Fresh full issuance — **all 23 articles اصلية**. MOJ double-official pipeline: **all
  23/23 articles matched outright** (mean 0.9678, min 0.933) — no visual adjudication needed. PDF committed.
  Track under `sources/iflas_hudud/regulation/`. Validate: `make iflas-hudud-regulation-track-validate`.

## لائحة الوثائق القضائية — Regulation on Judicial Documents (26/07/1439هـ)

- **Regulation on Judicial Documents (Minister of Justice Decision 2818, 26/07/1439هـ)
  verified + LLM-ready.** **لائحة الوثائق القضائية** — **23 records** (numbered 1–23, no مكرر) —
  definitions, the record of proceedings (الضبط) and the judgment instrument (الصك), their required
  contents and signatures, the case file and judicial documents file, and closing provisions. In
  force. Fresh full issuance — **all 23 articles اصلية**. MOJ double-official pipeline: **18/23
  articles matched outright** (mean 0.9565, min 0.7699); **5 short articles (9, 15, 18, 19, 23)**
  carrying parenthetical cross-reference numerals were adjudicated **VISUALLY VERBATIM**, a known
  digit-in-parenthetical PDF text-extraction reordering artifact. **DOCUMENTED SOURCE ANOMALY:**
  articles 13–19 carry their official number_label_ar without the المادة prefix (e.g. "الثالثة عشرة"
  rather than "المادة الثالثة عشرة"), confirmed identical in both official sources (portal
  statuteStructure/section-API and the official MOJ PDF, page 4) — preserved verbatim, not corrected.
  PDF committed (6 pages). Track under `sources/judicial_documents/regulation/`. Validate:
  `make judicial-documents-regulation-track-validate`.

## قواعد تحديد أتعاب الخبراء والأمناء في نظام الإفلاس — Rules for Determining the Fees of Experts and Trustees under the Bankruptcy Law (02/08/1442هـ)

- **Rules for Determining the Fees of Experts and Trustees under the Bankruptcy Law (Minister of
  Justice Decision 2514, 02/08/1442هـ, published 27/08/1442هـ) verified + LLM-ready.** **قواعد تحديد
  أتعاب الخبراء والأمناء في نظام الإفلاس** — **20 records**: **17 numbered articles** (1–17, no
  مكرر) — definitions, fee-setting principles, the expert's/trustee's fee request and court
  approval, advances and reimbursement, and closing provisions — plus **3 appendix fee-schedule
  tables** (شرائح الدائنين / شرائح الديون / شرائح الأصول, flagged `is_fee_schedule`) setting fee
  tiers by creditor count, debt value, and asset value. Implements the Bankruptcy Law (M/50,
  1439هـ). In force. Fresh full issuance — **all 20 records اصلية**. MOJ double-official pipeline:
  because this PDF's text layer mixes inconsistent RTL extraction conventions and the OCR channel
  misreads embedded numerals, only **6/20 matched the floor outright** (arts 4, 7, 10, 11, 12, 17);
  the other **14 (arts 1,2,3,5,6,8,9,13,14,15,16 + all 3 tables)** were adjudicated **VISUALLY
  VERBATIM** (mean 0.8217, min 0.5822). **DOCUMENTED SOURCE ANOMALIES:** (1) the three tables'
  official labels are formatted inconsistently ("الجدول رقم(١)" / "الجدول رقم (٢)" / "جدول رقم
  (٣)"); (2) inside article 19 (شرائح الديون), a sub-table header cell reads "الأصول" instead of
  "الديون" — a genuine copy-paste error in the source document, confirmed identical in both official
  sources and preserved verbatim. PDF committed (9 pages). Track under
  `sources/bankruptcy_fees/regulation/`. Validate: `make bankruptcy-fees-regulation-track-validate`.

## لائحة مقدمي خدمات التنفيذ — Regulation on Enforcement Service Providers (20/08/1443هـ)

- **Regulation on Enforcement Service Providers (Minister of Justice Decision 2268, 20/08/1443هـ,
  published 04/09/1443هـ) verified + LLM-ready.** **لائحة مقدمي خدمات التنفيذ** — **18 records**
  (numbered 1–18, no مكرر) — definitions and scope, licensing conditions and procedures for
  enforcement service providers, the licensing committee, obligations and prohibited conduct, fees,
  licence suspension/revocation, and closing provisions. Implements the Enforcement Law and its
  Implementing Regulation. Per its own article 18, **supersedes** the prior 1437هـ regulation
  (Ministerial Decision 11326, not ingested). In force. Fresh full issuance — **all 18 records
  اصلية**. MOJ double-official pipeline: this PDF's text layer uses a consistent per-line
  word-order-reversal RTL extraction convention that caps automated similarity scoring below the
  0.90 floor for every record (18/18 landed between 0.5973 and 0.786, mean 0.7476) — **all 18/18**
  were therefore adjudicated **VISUALLY VERBATIM** against the rendered PDF pages. **DOCUMENTED
  SOURCE ANOMALIES** (confirmed identically in both official sources): (1) article 8's "وللوکیل"
  uses Persian keheh/farsi-yeh instead of standard Arabic kaf/yeh; (2) article 9's "ترخيصه" is
  spelled inconsistently within the same article; (3) article 10 item 8 uses a Western ASCII digit
  "8." instead of the Eastern Arabic-Indic "٨."; (4) article 15 item 2 uses the Extended
  Arabic-Indic/Persian digit "۲" instead of standard "٢". All four preserved verbatim. PDF
  committed (8 pages). Track under `sources/enforcement_providers/regulation/`. Validate:
  `make enforcement-providers-regulation-track-validate`.

## تنظيم صندوق النفقة — Alimony Fund Regulation (15/11/1438هـ)

- **Alimony Fund Regulation (Council of Ministers Decision 679, 15/11/1438هـ, published in the
  Official Gazette 03/12/1438هـ) verified + LLM-ready.** **تنظيم صندوق النفقة** — **17 records**
  (numbered 1–17, no مكرر), flat article structure with no chapter/section wrapper — the Fund's
  independent legal personality and budget with administrative linkage to the Minister of Justice
  (art 2), governance, financing sources, disbursement of alimony advances to beneficiaries and
  subrogation against the debtor, and closing provisions. **NOTE ON ISSUING AUTHORITY:** although
  classified under القضاء on the MOJ portal, the Regulation was issued directly by the **Council of
  Ministers** (not a Minister of Justice decision) — the Fund is a semi-independent body. No prior
  version exists; a first-of-its-kind fund-establishing instrument. In force. Fresh full issuance —
  **all 17 records اصلية**. MOJ double-official pipeline: **7/17 matched the floor outright**; the
  other **10 (arts 1, 4, 5, 7, 8, 9, 10, 11, 12, 15)** were adjudicated **VISUALLY VERBATIM** (mean
  0.7767, min 0.3987) due to a known RTL/ligature PDF text-layer extraction artifact. No
  character-level source anomalies found. PDF committed (3 pages). Track under
  `sources/alimony_fund/regulation/`. Validate: `make alimony-fund-regulation-track-validate`.

## Strict QA gate

- **`make qa-gate`** — one command, everything must pass: **[1]** every
  `scripts/validate_*.py` in the repository (151 today — discovered from the filesystem, so any new
  validator automatically joins the gate; exclusions require a written reason in the script's
  `EXCLUDED` dict, currently empty); **[2]** generator idempotence — 78 deterministic generators
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
