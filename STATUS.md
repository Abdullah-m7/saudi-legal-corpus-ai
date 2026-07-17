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
  + Sharia Procedure regulation 637 + Law of Criminal Procedure 222 + Criminal Procedure regulation 181 + Law of Enforcement 98 + Enforcement regulation 273 + Law of the Judiciary 85 + Law of the Board of Grievances 26 + Code of Law Practice 56 + Code of Law Practice regulation 90 + Commercial Courts Law 96 + Commercial Courts Law regulation 281 + Bankruptcy Law 231 + Bankruptcy Law regulation 98 + Bankruptcy case rules 24 + Judicial Costs Law 23 + Judicial Costs regulation 17 + Arbitration Law 58 + Arbitration regulation 19 + Commercial Papers Law 121 + Commercial Register Law 29 + Trade Names Law 23 + Commercial Agencies Law 6 + Chambers of Commerce Law 66 + Commercial Books Law 16 + Anti-Money Laundering Law 52 + Notarization Law 57 + Notarization Regulation 31 + Real Estate Registration Law 40 + Real Estate Registration Regulation 51 + Registered Real Estate Mortgage Law 46 + Real Estate Finance Law 15 + Real Estate Unit Ownership Law 33 + Real Estate Unit Ownership Regulation 41 + Non-Saudi Real Estate Ownership Law 15 + Municipal Real Estate Disposal Law 6 + Municipal Real Estate Disposal Regulation 35 + GCC Citizens Ownership Regulation 6 + Combating Terrorism Crimes and Financing 99 + its Implementing Regulation 28 + Juveniles Law 24 + its Implementing Regulation 13 + Whistleblower, Witness, Expert and Victim Protection Law 37 + Judicial Inspection Regulation 68 + Regulation on the Division of Jointly-Owned Property 48 + Professional Conduct Rules for Lawyers 47 + Regulation Organizing the Work of Judicial Assistants 35 + Rules for the Work of Conciliation Offices and its Procedures 29 + Rules Organizing Cross-Border Insolvency Procedures 23 + Regulation on Judicial Documents 23 + Rules for Determining the Fees of Experts and Trustees under the Bankruptcy Law 20 + Regulation on Enforcement Service Providers 18 + Alimony Fund Regulation 17 + Executive Working Mechanism for the Law of the Judiciary and the Law of the Board of Grievances 15 + Regulation of the Center for Assignment (Referral) and Liquidation 15 + Regulation of the Conciliation Center 10 + Medical Reports Regulation 13 + Regulation on the Marriage of a Saudi to a Non-Saudi 11 + Mechanism for a Defendant in Major/Serious Crimes to Seek Legal Counsel at the State's Expense 11 + Controls for the Lessor's Repossession of Movable Assets 7 + Procedural Guide for the Electronic Litigation Service 5 + Organizational Guide for the Judicial Training Center 18 + Executive Regulation for Methods of Objecting to Judgments 62 + Law on Expropriation of Real Estate for Public Interest and Temporary Seizure of Real Estate 39 + Arrangements for Hearing Claims to Prove Marriage Contracts Concluded Without Required Official Permission 10**)
  with counts, paths, statuses, language layers,
  boundaries, and validation targets. **117 tracks; primary Arabic governing 8141; reference 614; registry-counted
  9036.** PDPL and Investment Arabic tracks are **verified against official
  published text** (SDAIA / MISA). The registry also records the unified retrieval
  index (7972 records) as a projection (not added to totals). See
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
  Personal Status 293 (law 252 + regulation 41) + Sharia Procedure 880 (law 243 + regulation 637) + Criminal Procedure 403 (law 222 + regulation 181) + Enforcement 371 (law 98 + regulation 273) + Judiciary 85 + Board of Grievances 26 + Law Practice 146 (law 56 + regulation 90) + Commercial Courts 377 (law 96 + regulation 281) + Bankruptcy 353 (law 231 + regulation 98 + case rules 24) + Judicial Costs 40 (law 23 + regulation 17) + Arbitration 77 (law 58 + regulation 19) + Commercial Papers 121 (law) + Commercial Register 29 (law) + Trade Names 23 (law) + Commercial Agencies 6 (law) + Chambers of Commerce 66 (law) + Commercial Books 16 (law) + Anti-Money Laundering 52 (law) + Notarization 88 (law 57 + regulation 31) + Real Estate Registration 91 (law 40 + regulation 51) + Real Estate Mortgage 46 (law) + Real Estate Finance 15 (law) + Real Estate Units 74 (law 33 + regulation 41) + Non-Saudi Ownership 15 (law) + Municipal Real Estate 41 (law 6 + regulation 35) + GCC Ownership 6 (law) + Counter-Terrorism 127 (law 99 + regulation 28) + Juveniles 37 (law 24 + regulation 13) + Whistleblower Protection Law 37 (law) + Judicial Inspection Regulation 68 (regulation) + Qismah Regulation 48 (regulation) + Professional Conduct Rules for Lawyers 47 (regulation) + Judicial Assistants Regulation 35 (regulation) + Conciliation Offices Rules 29 (regulation) + Cross-Border Insolvency Procedures Rules 23 (regulation) + Judicial Documents Regulation 23 (regulation) + Bankruptcy Fees Rules 20 (regulation) + Enforcement Service Providers Regulation 18 (regulation) + Alimony Fund Regulation 17 (regulation) + Executive Working Mechanism for the Law of the Judiciary and the Law of the Board of Grievances 15 (mechanism) + Regulation of the Center for Assignment (Referral) and Liquidation 15 (regulation) + Regulation of the Conciliation Center 10 (regulation) + Medical Reports Regulation 13 (regulation) + Regulation on the Marriage of a Saudi to a Non-Saudi 11 (regulation) + Mechanism for a Defendant in Major/Serious Crimes to Seek Legal Counsel at the State's Expense 11 (regulation) + Controls for the Lessor's Repossession of Movable Assets 7 (regulation) + Procedural Guide for the Electronic Litigation Service 5 (regulation) + Organizational Guide for the Judicial Training Center 18 (guide) + Executive Regulation for Methods of Objecting to Judgments 62 (regulation) + Law on Expropriation of Real Estate for Public Interest and Temporary Seizure of Real Estate 39 (law) + Arrangements for Hearing Claims to Prove Marriage Contracts Concluded Without Required Official Permission 10 (regulation) + Anti-Bribery Law 25 (law, DISTINCT lower-confidence verification tier) + Basic Law of Governance 83 (law, DISTINCT tier: BOE portal x WIPO Lex spot-checked) + Anti-Cyber Crime Law 16 (law, DISTINCT tier: BOE x WIPO Lex/CITC x MOF exhaustive triple-source) + Anti-Harassment Law 8 (law, DISTINCT mixed tier: BOE x secondary press convergence for art 6 amendment) + Anti-Trafficking in Persons Law 17 (law, DISTINCT tier: BOE Wayback snapshot x UNODC English substance-verified) + Council of Ministers Law 32 (law, DISTINCT tier: dual independent Arabic secondary sources, BOE unreachable) + Regions/Provinces Law 41 (law, DISTINCT tier: dual independent Arabic secondary sources, this law's BOE page unreachable) + Electronic Transactions Law 31 (law, DISTINCT tier: single primary BOE/CoM translation-bureau PDF, WIPO Lex structural cross-check) + Allegiance Commission Law 25 (law, DISTINCT tier: triple independent Arabic secondary sources, BOE page unreachable) + Shura Council Law 30 (law, MIXED tier: triple Arabic secondary sources + SPA primary source for art 3) + Copyright Law 28 (law, DISTINCT tier: qadha.org.sa compiled text x WIPO Lex structural cross-check; superseded 2026-08-01) + Telecommunications and Information Technology Act 41 (law, DISTINCT tier: BOE portal primary source, MCIT PDF cross-check; fresh replacement law, all اصلية) + Saudi Central Bank Law 27 (law, DISTINCT tier: SAMA official PDF primary source, BOE Wayback archive cross-check) + Banking Control Law 26 (law, DISTINCT tier: dual independent Arabic secondary sources, BOE unreachable for raw text; art 13's 1391H amendment original wording irrecoverable) + Capital Market Law 68 (law, MIXED tier: 55 CMA-current x BOE-2003 cross-verified, 12 flagged 2003-only historical fallback for the M/16-restructured articles, 1 reconstructed) + Competition Law 28 (law, DISTINCT tier: BOE Wayback snapshot x nezams.com cross-verified word-for-word) + Payment Systems and Services Law 20 (law, DISTINCT tier: official SAMA PDF, dual OCR pass x nezams.com cross-verified word-for-word) + Mining Investment Law 64 (law, DISTINCT tier: BOE Wayback snapshot x FAOLEX structural cross-check) + Trademark Law 52 (law, DISTINCT tier: WIPO Lex primary PDF x embedded BOE status card cross-verified) + Anti-Concealment Law 20 (law, DISTINCT tier: triple Arabic secondary sources, BOE unreachable via all methods) + Cooperative Insurance Companies Control Law 25 (law, DISTINCT tier: misa.gov.sa official PDF x nezams.com, BOE and Wayback both unreachable) + E-Commerce Law 26 (law, DISTINCT tier: BOE Wayback snapshot x nezams.com cross-verified) + Value Added Tax Law 53 (law, DISTINCT tier: ZATCA official PDF x BOE portal cross-verified) + Franchise Law 27 (law, DISTINCT tier: BOE portal via r.jina.ai proxy x qanoniah.com spot cross-verified) + Civil Aviation Law 180 (law, DISTINCT tier: nezams.com primary x rakadvocate.blogspot.com spot-checked, BOE unreachable) + Anti-Narcotics and Psychotropic Substances Control Law 74 (law, DISTINCT tier: BOE via r.jina.ai proxy x nezams.com x qadha.org.sa reference book triple-verified) + Traffic Law 86 (law, MIXED-CONFIDENCE tier: BOE portal confirmed genuinely stale, nezams.com preferred with per-article verification_tier) + Environmental Law 49 (law, STRONG triple-source tier: BOE Wayback x green.org.sa PDF x nezams.com, one flagged BOE self-contradiction at Article 1) = **7972 records**) into one flat index at
  `data/corpus_unified_index/corpus_unified_llm_index.jsonl` with a common schema. Query the whole
  corpus at once with `python3 scripts/search_corpus_unified.py "<عربي>"` (deterministic lexical
  scorer over each record's keywords / search_queries / titles / text; `--corpus` and `--top`
  flags). No legal text is altered, summarized, or translated. Validate (includes sanity queries
  that must route to the right law): `make corpus-unified-llm-index-validate`.
- **Retrieval eval pack** — realistic Arabic gold queries over the unified index
  (`data/corpus_retrieval_eval/`), each gold manually confirmed against the article's own text
  (definitional articles) or official title — not reverse-engineered from search output. Runner
  `scripts/run_corpus_retrieval_eval.py` computes top-1/top-3/top-5 accuracy + MRR@5 and writes
  deterministic results. **Current: top-1 90.5% / top-3 97.2% / top-5 98.4% / MRR@5 0.9385**
  over the 7972-record index with **264 golds** — expanded from 40 (v2: gtp-001..007 +
  lab-001..014; v3: ith-001..003; v4: ith-004..006; v5: ahw-001..004; v6: mrf-001..003 law; v7: mrf-004..006 regulation; v8: mjz-001..003 criminal-procedure law; v9: mjr-001..003 criminal-procedure regulation; v10: mtn-001..003 enforcement law; v11: mtl-001..003 enforcement regulation; v12: mqd-001..003 judiciary; v13: dmz-001..003 board-of-grievances; v14: muh-001..003 law-practice; v15: mhl-001..003 law-practice-regulation; v16: tjr-001..003 commercial-courts; v17: tjl-001..003 commercial-courts-regulation; v18: ifl-001..003 bankruptcy law; v19: ilr-001..003 bankruptcy regulation; v20: icr-001..003 bankruptcy case rules; v21: tkq-001..002 judicial-costs law + tkr-001 regulation; v22: thk-001..002 arbitration law + thr-001 regulation; v23: awt-001..003 commercial-papers law; v24: sjt-001..002 commercial-register + ast-001 trade-names; v25: wkl-001..002 commercial-agencies; v26: ghr-001..002 chambers-of-commerce; v27: dft-001..002 commercial-books; v28: hmb-001..002 whistleblower-protection; v29: tft-001..002 judicial-inspection; v30: qsm-001..002 qismah-division; v31: slk-001..002 sulook-professional-conduct; v32: awn-001..002 aawan-judicial-assistants; v33: msl-001..002 muslaha-conciliation-offices; v34: ifh-001..002 iflas-hudud-cross-border-insolvency; v35: jud-001..002 judicial-documents-regulation; v36: atb-001..002 bankruptcy-fees-regulation; v37: tnf-001..002 enforcement-providers-regulation; v38: nfq-001..002 alimony-fund-regulation; v39: jbm-001..002 judiciary-bog-mechanism; v40: esd-001..002 documentation-settlement-regulation; v41: msc-001..002 mosalaha-center-regulation; v42: mtr-001..002 medical-reports-regulation; v43: mzj-001..002 marriage-non-saudi-regulation; v44: mnd-001..002 state-funded-lawyer-regulation; v45: dmn-001..002 lessor-repossession-regulation; v46: tqe-001..002 elitigation-guide-regulation; v47: mtd-001..002 judicial-training-center-guide (bespoke track); v48: tea-001..002 judgment-objection-methods-regulation, plus mrf-001's sanity companion re-pointed from sharia_procedure art 176 to art 177 in the unified-index SANITY list after a topical-overlap collision with this new track's title-heavy content; v49: nzm-001..002 real-estate-expropriation-law; v50: zwj-001..002 marriage-contract-hearing-regulation; v51: rsw-001..002 anti-bribery-law, DISTINCT lower-confidence secondary-source verification tier — see track notes; v52: blg-001..002 basic-law-of-governance, DISTINCT tier (BOE portal primary source x WIPO Lex spot-checked) — see track notes; v53: cyb-001..002 anti-cyber-crime-law, DISTINCT tier (BOE x WIPO Lex/CITC x MOF exhaustive triple-source verified, the strongest tier outside the primary MOJ pipeline) — see track notes; v54: hrs-001..002 anti-harassment-law, DISTINCT mixed tier (7 BOE-multi-source-checked articles + art 6's 2021 amendment sourced via secondary press convergence, exact wording flagged with a documented alternate candidate) — see track notes; v55: trf-001..002 anti-trafficking-law, DISTINCT tier (full text from a Wayback Machine snapshot of the BOE portal, substance-cross-checked against UNODC's official English translation and the 2025 US State Department TIP Report; a 33-article draft replacement law remains unenacted and is documented but not ingested) — see track notes; v56: cmn-001..002 council-of-ministers-law, DISTINCT tier (laws.boe.gov.sa confirmed completely unreachable across two research passes; full text rests on cross-verified word-for-word agreement between two independent Arabic secondary sources, ar.wikisource.org and nezams.com, with FAOLEX's English PDF used only for a structural cross-check) — see track notes; v57: rgn-001..002 regions-law, DISTINCT tier (this law's specific BOE page could not be reached across ~20 attempts despite a different BOE page succeeding in the same session; full text rests on cross-verified agreement between two independent Arabic secondary sources, islamport.com and nezams.com, with FAOLEX's English PDF used only as a weaker meaning-level cross-check, confirmed incomplete and date-flawed) — see track notes; v58: etr-001..002 electronic-transactions-law, DISTINCT tier (single primary source, the official BOE/CoM translation-bureau PDF manually corrected for a systematic lam+alef ligature-extraction bug, structurally cross-checked against WIPO Lex's full English translation across 100% of articles; Chapter 6/arts 16-17 abolished by a 2023 amendment and flagged ملغاة, with the exact post-abolition article renumbering left undetermined and documented) — see track notes; v59: hba-001..002 allegiance-commission-law, DISTINCT tier (triple independent Arabic secondary sources, ar.wikisource.org x islamport.com x ar.wikipedia.org, this law's BOE page located but unreachable) — see track notes, including a documented cross-track conflict with the Basic Law of Governance's Article 5(c) since resolved via a dedicated follow-up correction; v60: shc-001..002 shura-council-law, MIXED tier (triple independent Arabic secondary sources for 29 articles, plus a Tier-1 government primary source, Saudi Press Agency, for article 3's current 2013-amended text) — see track notes; v61: cpr-001..002 copyright-law, DISTINCT tier (qadha.org.sa compiled text structurally cross-checked against WIPO Lex, laws.boe.gov.sa unreachable) — CONFIRMED SUPERSEDED effective 2026-08-01 by Royal Decree M/169, whose text could not be verified this pass and is not ingested — see track notes; v62: tlc-001..002 telecommunications-law, DISTINCT tier (laws.boe.gov.sa primary source reachable this pass, cross-checked against MCIT's own official PDF; fresh replacement law, all 41 articles اصلية, with an unconfirmed 2024 proposed-amendment consultation flagged on articles 20/24/25/27) — see track notes; v63: scb-001..002 sama-law, DISTINCT tier (SAMA official PDF primary source x BOE Wayback archive cross-check) — see track notes; v64: bnk-001..002 banking-control-law, DISTINCT tier (dual independent Arabic secondary sources, BOE unreachable for raw text) — see track notes; v65: cml-001..002 capital-market-law, MIXED tier (picked from the main-tier confirmed-current portion; 12 of 68 records are flagged 2003-only historical fallback, see track notes before using those) — see track notes; v66: ctp-001..002 competition-law, DISTINCT tier (BOE Wayback snapshot x nezams.com cross-verified word-for-word) — see track notes; v67: pay-001..002 payment-systems-law, DISTINCT tier (official SAMA PDF, dual independent OCR passes x nezams.com cross-verified word-for-word) — see track notes; v68: min-001..002 mining-investment-law, DISTINCT tier (BOE Wayback snapshot fetched directly x FAOLEX structural cross-check) — see track notes; v69: trd-001..002 trademark-law, DISTINCT tier (WIPO Lex primary PDF with embedded BOE status card x two independent OCR passes for the M/49 amendment) — see track notes; v70: tsr-001..002 anti-concealment-law, DISTINCT tier (triple independent Arabic secondary sources, qadha.org.sa x nezams.com x alrashidi.law, BOE completely unreachable via all three prescribed methods) — see track notes for this genuine sourcing limitation; v71: ins-001..002 insurance-control-law, DISTINCT tier (misa.gov.sa official bilingual PDF x nezams.com cross-verified, BOE and Wayback both unreachable) — see track notes for the flagged institutional-name divergence and the pre-amendment-original-text limitation; v72: ecm-001..002 ecommerce-law, DISTINCT tier (BOE portal via a single Wayback Machine snapshot fetched directly x nezams.com cross-verified) — see track notes for the flagged stale ministry name and Article 22's missing terminal punctuation; v73: vat-001..002 vat-law, DISTINCT tier (ZATCA official consolidated PDF x BOE portal cross-verified via r.jina.ai; Wayback Machine unreachable) — see track notes for the important limitation that pre-amendment original text is not included for either amended article; v74: frn-001..002 franchise-law, DISTINCT tier (BOE portal via r.jina.ai proxy after a direct WebFetch 503, spot-cross-verified against qanoniah.com for Articles 1, 2, 4, 5 only) — see track notes for the flagged M/22 decree-number collision with the unrelated superseded Anti-Concealment Law, and the non-textual 2026 Council of Ministers carve-out decision; v75: cav-001..002 civil-aviation-law, DISTINCT tier (nezams.com direct fetch as primary full-text source, spot-checked against rakadvocate.blogspot.com for Articles 1 and 180 only, BOE unreachable via all methods tried) — see track notes for the flagged Article 149 heading anomaly, the single-sourced Council of Ministers Resolution 158/1445H institutional rename, and the documented pre-amendment-text gap for Article 46; v76: nrc-001..002 anti-narcotics-law, DISTINCT tier (BOE portal via r.jina.ai proxy x nezams.com word-for-word cross-verification x qadha.org.sa reference book triple-verifying the highest-stakes penalty articles) — see track notes for the flagged Article 42 BOE-vs-nezams.com textual variant and Article 35's anomalous heading, both preserved/resolved transparently rather than silently; v77: trc-001..002 traffic-law, the corpus's most complex verification case — TWO research passes confirmed the BOE portal is genuinely stale for this law (not a proxy artifact) via four independently-verified data points, with nezams.com preferred for amended articles and a per-article verification_tier field carrying real per-article confidence rather than one overstated track-level claim — see track notes for the Table 2 item-16 numbering conflict and the full 11-item discrepancy list; v78: env-001..002 environmental-law, STRONG triple-source tier (BOE via Wayback Machine x an independently-hosted green.org.sa PDF x nezams.com, matching verbatim for 48 of 49 articles) — see track notes for the one flagged exception, Article 1's 'الجهة المختصة' definition, where BOE's own amendment-log contradicts BOE's own main article text, resolved as operative per the Traffic Law track's BOE-lag precedent and flagged for dedicated human legal review) so that GTPL, all eight
  Labor components, all four Evidence components, the Personal Status law + regulation, the
  Law of Sharia Procedure + its implementing regulation, the Law of Criminal Procedure + its implementing regulation, the Law of Enforcement + its regulation, the Law of the Judiciary, the Law of the Board of Grievances, the Code of Law Practice + its regulation, and the Commercial Courts Law + its regulation have
  gold coverage; every new
  gold was confirmed by reading the article's committed text first and writing the query from
  its own wording. Four documented
  lexical misses remain (civ-004 تعريف الكفالة; pdp-010 سياسة الخصوصية — the gold PDPL article
  does not contain the query phrase verbatim, so labor-annex records now outscore it; dmz-001,
  dmz-003 — Board of Grievances golds that now route to the topically-overlapping Judiciary/BoG
  mechanism track instead, a legitimate consequence of added coverage). Validator re-runs the eval, requires exact
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

## آلية العمل التنفيذية لنظام القضاء ونظام ديوان المظالم — Executive Working Mechanism for the Law of the Judiciary and the Law of the Board of Grievances (19/09/1428هـ)

- **Executive Working Mechanism for the Law of the Judiciary and the Law of the Board of Grievances
  (Royal Decree م/78, 19/09/1428هـ — the same decree promulgating the two companion laws) verified +
  LLM-ready.** **آلية العمل التنفيذية لنظام القضاء ونظام ديوان المظالم** — **15 records** across 3
  sections (9 items for the Law of the Judiciary + 5 for the Law of the Board of Grievances + 1
  general-provisions item) — transitional/executive provisions: formation of the Supreme Judicial
  Council and Board of Administrative Judiciary, court conversion, staffing, budgets, transitional
  periods. **NOT A FRESH ISSUANCE:** 14/15 items **اصلية**; item 7 (labor courts) is **معدلة** with
  a **2-version amendment history** — originally 1428H, amended by م/6 (1440H), amended again by
  م/113 (1443H, current). MOJ double-official pipeline: **1/15 matched the floor outright** (item 9);
  the other **14** were adjudicated **VISUALLY VERBATIM** (mean 0.5026, min 0.1253) due to a known
  RTL/ligature PDF text-layer extraction artifact. **DOCUMENTED SOURCE ANOMALIES:** item 9's heading
  reads "شبة القضائية" instead of "شبه"; item 10's heading reads "بمجل القضاء الإداري", missing the
  س of مجلس. A small amount of genuine decorative kashida on "ديوان المظالم" (items 6, 8) was
  normalized per this corpus's standing convention. PDF committed (8 pages). Track under
  `sources/judiciary_bog/mechanism/`. Validate: `make judiciary-bog-mechanism-track-validate`.

## تنظيم مركز الاسناد والتصفية — Regulation of the Center for Assignment (Referral) and Liquidation (19/07/1440هـ)

- **Regulation of the Center for Assignment (Referral) and Liquidation (Council of Ministers Decision
  415, 19/07/1440هـ) verified + LLM-ready.** **تنظيم مركز الاسناد والتصفية** — **15 records** (numbered
  1–15, no مكرر), flat article structure with no chapter/section wrapper — establishes a
  semi-independent body (own legal personality, financial and administrative independence)
  organizationally linked to the Minister of Justice, receiving liquidation/asset-sale tasks referred
  by judicial and government bodies (estates, companies, funds, contributions, asset sales) plus
  liquidation/sale requested directly by parties with no pending dispute; related to the Enforcement
  Law (نظام التنفيذ) and its Implementing Regulation. In force; sole issuance, no prior version.
  **NOT A FRESH ISSUANCE FOR EVERY ARTICLE:** 14/15 records **اصلية**; article 4 (board composition)
  is **معدلة** with a **2-version amendment history** — originally 1440H, amended by Council of
  Ministers Decision 685 (1443H), amended again by Decision 364 (1447H, current — added a هيئة السوق
  المالية board seat). MOJ double-official pipeline: **3/15 matched the floor outright** (arts 6, 7,
  14); the other **12** were adjudicated **VISUALLY VERBATIM** (mean 0.7999, min 0.6117) due to a
  known RTL/ligature PDF text-layer extraction artifact. No character-level source anomalies found.
  PDF committed (4 pages). Track under `sources/documentation_settlement/regulation/`. Validate:
  `make documentation-settlement-regulation-track-validate`.

## تنظيم مركز المصالحة — Regulation of the Conciliation Center (08/04/1434هـ)

- **Regulation of the Conciliation Center (Council of Ministers Decision 103, 08/04/1434هـ, published
  in Umm Al-Qura 02/06/1434هـ) verified + LLM-ready.** **تنظيم مركز المصالحة** — **10 records**
  (numbered 1–10, no مكرر), flat article structure with no chapter/section wrapper — this is the
  Center's constitutive/establishing regulation (creation of the Center, its director-general's
  duties, confidentiality). Its own article 9 directs the Minister of Justice to issue the
  operational rules for conciliation offices — the already-ingested sibling track **قواعد العمل في
  مكاتب المصالحة وإجراءاته** (`sources/muslaha/regulation/`, 29 records) — confirmed via the portal's
  otherRelatedLegal cross-reference; the two tracks are kept fully separate. In force. Fresh full
  issuance — **all 10 records اصلية**. MOJ double-official pipeline: the PDF text layer exhibits the
  known RTL/ligature extraction artifact, but the 300dpi OCR channel is clean — **all 10/10 matched
  the floor outright** (mean 0.9897, min 0.968), no visual adjudication needed, though all 10 were
  additionally read in full as a direct visual cross-check. **DOCUMENTED SOURCE ANOMALY:** article 1
  item 2 (الوزارة) reads "الوزارة: ىوزارة العدل." — an anomalous character precedes "وزارة العدل",
  confirmed independently in both the portal DB text and the rendered official PDF glyphs (different
  anomalous characters in each channel, corroborating a genuine typo in the original decree). PDF
  committed (2 pages). Track under `sources/mosalaha_center/regulation/`. Validate:
  `make mosalaha-center-regulation-track-validate`.

## لائحة التقارير الطبية — Medical Reports Regulation (16/11/1444هـ)

- **Medical Reports Regulation (Minister of Justice Decision 3411, 16/11/1444هـ) verified +
  LLM-ready.** **لائحة التقارير الطبية** — **13 records** (numbered 1–13, no مكرر), flat article
  structure with no chapter/section wrapper — governs the form, content, and evidentiary handling
  of medical reports submitted to courts and judicial bodies: issuing-authority requirements
  (medical committees, specialist physicians), mandatory report contents, confidentiality of the
  request and report, and applicability of the Evidence Law where the regulation is silent. Related
  to the Personal Status Law's provisions on medical examination (guardianship/capacity
  determinations, incapacity, pregnancy-term reports). In force. Fresh full issuance — **all 13
  records اصلية**. MOJ double-official pipeline: the PDF text layer exhibits the known
  RTL/ligature extraction artifact, but the 300dpi OCR channel is clean for most articles —
  **9/13 matched the floor outright via OCR** (mean 0.8857, min 0.3884); the other **4** (articles
  2, 6, 12, 13) were adjudicated **VISUALLY VERBATIM** on the rendered official PDF pages.
  **DOCUMENTED SOURCE ANOMALY:** article 2 item 1 (بألفاظـ) carries an extraneous trailing tatweel
  ("بالنص عليه بألفاظـ واضحة") not grammatically expected after the word, confirmed independently
  in both the portal DB text and the rendered official PDF glyphs — preserved verbatim, not
  corrected. PDF committed (2 pages). Track under `sources/medical_reports/regulation/`. Validate:
  `make medical-reports-regulation-track-validate`.

## لائحة زواج السعودي بغير سعودية والسعودية بغير سعودي — Regulation on the Marriage of a Saudi to a Non-Saudi (20/12/1422هـ)

- **Regulation on the Marriage of a Saudi Man to a Non-Saudi Woman and a Saudi Woman to a Non-Saudi
  Man (Minister of Interior Decision 6874, 20/12/1422هـ) verified + LLM-ready.** **لائحة زواج
  السعودي بغير سعودية والسعودية بغير سعودي** — **11 records** (numbered 1–11, no مكرر), flat article
  structure with no chapter/section wrapper — lists the categories of Saudis (ministers, judiciary,
  Royal Court/Shura Council staff, diplomats, military/security personnel, students abroad, etc.)
  for whom marriage to a non-Saudi is prohibited absent Minister of Interior approval, and sets
  conditions/procedures for permitted mixed marriages (GCC nationals, Kingdom-born non-Saudi women,
  documentation duties of the Sharia courts and Saudi diplomatic missions, disciplinary consequences
  before the Board of Grievances for violations). **ISSUING AUTHORITY NOTE:** although hosted on the
  MOJ legal portal and heavily invoking the Sharia courts' documentation role, issued directly by
  the Minister of Interior (not a Minister of Justice or Council of Ministers instrument), following
  a Royal Court referral and Council of Ministers review per its own preparatory record. In force.
  Fresh full issuance — **all 11 records اصلية**. MOJ double-official pipeline: the PDF's raw text
  layer exhibits the known RTL word-order glyph-extraction artifact (scores low, mean ~0.34), but
  the per-line word-reversed text-layer channel and the 300dpi OCR channel are clean — **all 11/11
  matched the floor outright** (mean 0.9426, min 0.9282), no visual adjudication needed, though all
  11 were additionally read in full against rendered 200dpi/400dpi PDF page images as a direct
  visual cross-check, independently corroborated against the separately-fetched official issuance
  instrument (أداة الإصدار). **DOCUMENTED SOURCE ANOMALY:** article 4 (وأباء) spells "fathers" with
  a plain hamza-on-alef rather than the standard alef-madda spelling "وآباء" — confirmed
  independently in both the portal DB text and the rendered official PDF glyphs (the document's own
  separate summary/abstract block spells the same word correctly, so the divergence is specific to
  article 4's operative text) — preserved verbatim, not corrected. PDF committed (2 pages). Track
  under `sources/marriage_non_saudi/regulation/`. Validate:
  `make marriage-non-saudi-regulation-track-validate`.

## آلية الاستعانة بمحام على نفقة الدولة للمتهم في الجرائم الكبيرة — State-Funded Lawyer Mechanism (06/05/1439هـ)

- **Mechanism for a Defendant in Major/Serious Crimes to Seek Legal Counsel at the State's Expense
  (Minister of Justice Decision 1529, 06/05/1439هـ) verified + LLM-ready.** **آلية الاستعانة بمحام
  على نفقة الدولة للمتهم في الجرائم الكبيرة** — **11 records**, flat structure with no
  chapter/section wrapper — items are labeled with Arabic ordinal words (أولاً..حادي عشر), not
  مادة-numbered. **PORTAL CLASSIFICATION NOTE:** despite the document's own title containing "آلية",
  the MOJ portal's own legalType classification for this instrument is "لائحة" (regulation) — hence
  `law_component='regulation'` per this corpus's convention of following the portal's own
  classification rather than the document's title word. Establishes the committee/roster process for
  court-appointed defense counsel at state expense for defendants in major/serious crimes:
  candidate-lawyer rosters, a nomination committee, request/decision timelines, lawyer eligibility
  conditions, withdrawal/termination procedures, a fee schedule (per-session caps by number of
  defendants, out-of-town supplement), and post-service continuity of the right to seek
  reconsideration. In force. Fresh full issuance — **all 11 records اصلية**. MOJ double-official
  pipeline: the PDF's raw text layer exhibits the known RTL word-order glyph-extraction artifact
  (scores low, mean ~0.40), but the 300dpi OCR channel and the per-line word-reversed text-layer
  channel together cleared **6/11 items outright** (mean 0.9216, min 0.8700); the other **5** (items
  2, 3, 5, 7, 9) were adjudicated **VISUALLY VERBATIM** on the rendered 200dpi PDF pages, confirming
  match including internal article cross-reference digits an OCR pass had misread (e.g. "المادة
  (٩٦)" misread as "(17)" — a local OCR artifact, not a source discrepancy). No source anomalies
  found. **RELATION TO OTHER TRACKS:** items 3 and 8 cite arts 96 and 97 of the already-ingested
  Criminal Procedure Regulation (`jza_reg_art_096`/`097`); art 97 §3 itself names this instrument as
  the "آلية" it implements for paying court-appointed counsel, which in turn implements Criminal
  Procedure Law art 139's (`jza_law_art_139`) court-appointed-counsel provision. PDF committed (2
  pages). Track under `sources/state_funded_lawyer/regulation/`. Validate:
  `make state-funded-lawyer-regulation-track-validate`.

## ضوابط تسلم المؤجر الأصول المنقولة — Lessor Repossession Controls (04/04/1440هـ)

- **Controls for the Lessor's Repossession of Movable Assets (Minister of Justice Decision 1448,
  04/04/1440هـ) verified + LLM-ready.** **ضوابط تسلم المؤجر الأصول المنقولة** — **7 records**, flat
  structure with no chapter/section wrapper — item 1 is labeled "تمهيد" (Preamble) and items 2–7 are
  labeled with Arabic ordinal words (أولاً..سادساً), not مادة-numbered. Governs the process by which
  licensed service providers repossess movable leased assets (vehicles, equipment) on a lessor's
  behalf under financing-lease contracts: definitions, notice/escalation steps between lessor,
  contract-registration company, and service provider, the repossession procedure (two-officer
  minimum, photographic documentation, handling of items found inside the asset), and a fee cap (max
  2.5% of contract value). In force. Fresh full issuance — **all 7 records اصلية**. MOJ
  double-official pipeline: the PDF's raw text layer exhibits the known RTL word-order
  glyph-extraction artifact (scores very low), but the 300dpi OCR channel cleared **4/7 items
  outright** (mean 0.9049, min 0.7976); the other **3** (items 5, 6, 7 — the shortest
  single-sentence items) were adjudicated **VISUALLY VERBATIM** on the rendered PDF page, confirming
  match including a percentage figure the OCR channel had garbled. **DOCUMENTED SOURCE ANOMALY:**
  item 1's preamble cites "المادة (٩٣/د)" of the Enforcement Law as its enabling provision, but
  Article 93's actual sub-item (د) is the unrelated "الخازن القضائي" category — the correct enabling
  provision is sub-item (هـ), as confirmed by this regulation's own separately-fetched promulgating
  decree, which correctly cites "الفقرة (١/هـ)"; a genuine citation typo present identically in both
  official sources, preserved verbatim, not corrected. **RELATION TO OTHER TRACKS:** implements
  Enforcement Law art 93's licensing provision (already in this corpus, `tnf_law_art_093`); also
  relates to the already-ingested Executive Regulation of the Enforcement Law and Regulation of
  Enforcement Service Providers; items 2 and 3 additionally cite the Financing Lease Law (Royal
  Decree M/48) as substantive basis, not yet separately ingested in this corpus. PDF committed (2
  pages). Track under `sources/lessor_repossession/regulation/`. Validate:
  `make lessor-repossession-regulation-track-validate`.

## الدليل الإجرائي لخدمة التقاضي الإلكتروني — Electronic Litigation Procedural Guide (05/10/1441هـ)

- **Procedural Guide for the Electronic Litigation Service (Minister of Justice Decision 8056,
  05/10/1441هـ) verified + LLM-ready.** **الدليل الإجرائي لخدمة التقاضي الإلكتروني** — **5 records**,
  flat structure with no chapter/section wrapper — item 1 is labeled "مقدمة" (Preamble) and items
  2–5 are labeled with the portal's own full-heading sequence field combining an Arabic ordinal word
  and a description (e.g. "أولاً: أحكام عامة"), not bare مادة-numbered. Sets out the e-litigation
  (remote litigation) procedures: general provisions (national single-sign-on identity, platform
  exclusivity), scheduling/notification rules, the two session types — written session ("الجلسة
  الكتابية": memo exchange, document submission) and video session ("الجلسة المرئية": identity
  verification, decorum rules) — with detailed step-by-step procedures, and
  deliberation/judgment-issuance rules. In force. Fresh full issuance — **all 5 records اصلية**. MOJ
  double-official pipeline: the PDF's raw text layer exhibits the known RTL word-order
  glyph-extraction artifact (scores very low, ~0.15–0.30), but the 300dpi OCR channel cleared **3/5
  items outright** (mean 0.938, min 0.8815); the other **2** (items 3, 5 — the shortest items) were
  adjudicated **VISUALLY VERBATIM** on the rendered PDF pages. **SOURCE-LEVEL NORMALIZATION:** this
  document exhibited pervasive decorative justification-kashida (356 tatweel characters between two
  Arabic letters, across items 1, 2, 3, 5 — a typesetting artifact, not legal content) that was
  normalized/removed prior to ingestion per this corpus's standing convention; one legitimate
  tatweel remains in item 4 ("بـ(الجلسة"), a standard Arabic connector before a parenthesis, not
  decorative kashida. **DOCUMENTED SOURCE ANOMALY:** item 4's first numbered sub-point has a missing
  opening parenthesis before "الجلسة الكتابية)", confirmed present identically in both official
  sources, preserved verbatim, not corrected. **RELATION TO OTHER TRACKS:** cites Judiciary Law art
  71(1), Sharia Procedure Law arts 71/72/73, and Commercial Courts Law art 7 as enabling bases (all
  already in this corpus); also relates to the already-ingested Sharia Procedure Law and its
  implementing regulation; the promulgating decree additionally cites the Electronic Transactions
  Law, not yet separately ingested in this corpus. PDF committed (3 pages). Track under
  `sources/elitigation_guide/regulation/`. Validate:
  `make elitigation-guide-regulation-track-validate`.

## الدليل التنظيمي لمركز التدريب العدلي — Judicial Training Center Organizational Guide (24/04/1435هـ, BESPOKE TRACK)

- **Organizational Guide for the Judicial Training Center (Council of Ministers Resolution 162,
  24/04/1435هـ, consolidated through Resolution 621, 29/10/1440هـ) verified + LLM-ready.** **BESPOKE
  TRACK** — this instrument's mixed narrative/non-article content was flagged before ingestion (unlike
  every other track this session, which proceeded fully autonomously); a lightweight reconnaissance
  pass confirmed the hybrid structure, and the repo owner was checked in with directly before
  proceeding, choosing to ingest the whole document with bespoke handling rather than only the clean
  legal core. **الدليل التنظيمي لمركز التدريب العدلي** — **18 records**: items 1–11 are numbered legal
  decree clauses (أولاً..حادي عشر — establishing the Center, its goal, means, scope, financial
  provisions, Scientific Committee), **9 اصلية / 2 معدلة** (item 2/ثانياً the goal clause and item
  6/سادساً the Scientific Committee composition, each a 2-entry amendment history: 1435H original →
  amendment → Resolution 621 1440H current); items 12–18 are **7 unnumbered
  organizational/descriptive entries** — an org chart (item 12, converted from its source HTML table
  to a plain-text reporting-line hierarchy: وزير العدل → مدير عام المركز → 4 departments), a
  goals/tasks overview (item 13), and 5 department job-description blocks (items 14–18) — which the
  MOJ portal itself does not treat as change-trackable legal sections (`get-Section-Changes` returns
  404 for all 7). Items 12–18 are flagged `is_narrative_structural_content=true` with
  `legal_status_ar`/`history` left None/empty — **never defaulted to اصلية** — and `number_label_ar`
  drawn honestly from the source's own heading, never a fabricated أولاً/ثانياً-style ordinal. MOJ
  double-official pipeline: **17/18 text-bearing items matched the floor outright** (mean 0.9982, min
  0.9888); item 12 (the org chart, not text-similarity-scorable against a rendered table) was
  adjudicated **VISUALLY VERBATIM**. No decorative in-word tatweel found (0 characters).
  **DOCUMENTED SOURCE ANOMALY:** item 13's narrative goals/tasks overview states the Center's
  objective using the **stale pre-1440H-amendment wording** of item 2's goal clause (omitting judges,
  the general/administrative judiciary scope, lawyers, and Public Prosecution members that the 1440H
  amendment added) — a genuine internal drift between this guide's own decree clauses and its
  narrative summary, confirmed identical in both official sources, preserved verbatim, not
  reconciled with item 2. No formal `otherRelatedLegal` cross-references returned by the portal. PDF
  committed (5 pages). Track under `sources/judicial_training_center/guide/`. Validate:
  `make judicial-training-center-guide-track-validate`.

## اللائحة التنفيذية لطرق الاعتراض على الأحكام — Judgment Objection Methods Regulation (05/01/1445هـ)

- **Executive Regulation for Methods of Objecting to Judgments (Minister of Justice Decision 512,
  05/01/1445هـ) verified + LLM-ready.** **اللائحة التنفيذية لطرق الاعتراض على الأحكام** — **62
  records** across **5 chapters** (الباب الأول: أحكام عامة arts 1–18؛ الباب الثاني: الاستئناف arts
  19–39؛ الباب الثالث: النقض arts 40–47؛ الباب الرابع: التماس إعادة النظر arts 48–59؛ الباب الخامس:
  أحكام ختامية arts 60–62), with `section_ar` carrying each article's chapter heading. Governs
  appeal, cassation, and retrial-petition procedure before Saudi courts: filing requirements and
  deadlines, admissibility, hearing procedure, and grounds for each objection method. In force.
  Fresh full issuance — **all 62 records اصلية**. MOJ double-official pipeline: the PDF's raw text
  layer exhibits the known RTL word-order glyph-extraction artifact (scores very low, ~0.02–0.5), but
  the 300dpi OCR channel and the word-reversed text-layer channel together cleared **45/62 articles
  outright** (mean 0.8686, min 0.0443); the other **17** (predominantly longer multi-paragraph
  articles where line-break-induced word-reversal and/or OCR degrade) were adjudicated **VISUALLY
  VERBATIM** against all 10 rendered PDF pages. **SOURCE-LEVEL CLEANUP:** 6 decorative in-word
  tatweel characters and 11 CMS zero-width-non-joiner (U+200C) artifacts were normalized/removed
  prior to ingestion, both confirmed present identically in the portal DB and the official PDF's own
  typesetting. **RELATION TO OTHER TRACKS:** per its own art 61 and its separately-fetched
  promulgating decree, this regulation **supersedes Chapter 11** of the already-ingested Sharia
  Procedure Law's implementing regulation and the now-repealed standalone Executive Regulation for
  Appeal Procedures (decree 5134, 1440H, not ingested as it carries no live legal force); enabling
  authority is Sharia Procedure Law art 240; article-level cross-references include arts 185(4),
  193(1), 198, 200, 225, and 228 of the Sharia Procedure Law. Adding this large, topically-adjacent
  track caused one pre-existing unified-index sanity query (built from Sharia Procedure art 176,
  whose entire text is the phrase "طرق الاعتراض على الأحكام هي الاستئناف، والنقض، والتماس إعادة
  النظر") to start routing to this new regulation instead — re-pointed to art 177 (a related but
  textually distinct article) following the same topical-overlap fix pattern used earlier this
  session for judiciary_bog vs. board_of_grievances; the corresponding retrieval-eval gold query
  (mrf-001) was re-verified to still land within top-5 and needed no change. PDF committed (10
  pages). Track under `sources/judgment_objection_methods/regulation/`. Validate:
  `make judgment-objection-methods-regulation-track-validate`.

## نظام نزع ملكية العقارات للمصلحة العامة ووضع اليد المؤقت على العقارات — Real Estate Expropriation Law (12/03/1447هـ)

- **Law on Expropriation of Real Estate for Public Interest and Temporary Seizure of Real Estate
  (Royal Decree M/56, 12/03/1447هـ) verified + LLM-ready.** **نظام نزع ملكية العقارات للمصلحة
  العامة ووضع اليد المؤقت على العقارات** — **39 records** across **6 chapters** (الباب الأول:
  تعريفات وأحكام عامة arts 1–8؛ الباب الثاني: إجراءات نزع ملكية العقارات arts 9–12؛ الباب الثالث:
  الحصر والتقييم arts 13–15؛ الباب الرابع: التعويض والإخلاء arts 16–24؛ الباب الخامس: وضع اليد
  المؤقت على العقارات arts 25–29؛ الباب السادس: أحكام ختامية arts 30–39), with `section_ar`
  carrying each article's chapter heading. Issued by the General Authority for State Real Estate;
  governs expropriation procedure for public-interest projects, valuation and compensation, and
  temporary seizure of real estate. **Confirmed current in-force version** (`legalStatueName='ساري'`
  on the MOJ portal) — distinct from and, per its own art 37, replacing the repealed 1424هـ
  predecessor (Royal Decree M/15, `legalStatueName='ملغي'`, intentionally **not ingested**). Fresh
  full issuance — **all 39 records اصلية**. MOJ double-official pipeline: 38/39 articles cleared
  the ≥0.90 floor outright via the OCR and/or word-reversed text-layer channels (mean similarity
  0.9794, min 0.7807); the remaining article (art 22) was adjudicated **VISUALLY VERBATIM** against
  the rendered official PDF. **SOURCE-LEVEL CLEANUP:** 1 decorative in-word tatweel character
  ("العقـارات" → "العقارات", art 27) was normalized/removed prior to ingestion, confirmed present
  identically in the portal DB and the official PDF's own typesetting. **DOCUMENTED SOURCE
  ANOMALY:** article 39's ordinal heading reads "المادة التاسعة الثلاثون" (missing و before
  الثلاثون — a genuine drafting typo), confirmed identical in both the portal DB and the official
  PDF, preserved verbatim rather than silently corrected. PDF committed (8 pages, sha256
  `59b1f88734b8c80421fe07d081743b2d953b200636a30ff89951b14c6d6df341`). Track under
  `sources/real_estate_expropriation/law/`. Validate:
  `make real-estate-expropriation-law-track-validate`.

## الترتيبات الخاصة بسماع الدعوى بإثبات عقد الزواج — Marriage Contract Hearing Arrangements (3/7/1447هـ)

- **Arrangements for Hearing Claims to Prove Marriage Contracts Concluded Without Required
  Official Permission (Minister of Justice Decision 5121, 3/7/1447هـ) verified + LLM-ready.**
  **الترتيبات الخاصة بسماع الدعوى بإثبات عقد الزواج الذي أُبرم دون إذن الجهة المختصة فيما يشترط له
  الإذن** — **10 records**, flat structure with no chapter/section wrapper (`section_ar` empty for
  every article). Governs the procedure for hearing claims to prove a marriage contract concluded
  without the permission required under the Marriage of a Saudi to a Non-Saudi Regulation.
  **DOWNSTREAM PROCEDURAL COMPANION:** art 1 explicitly defines النظام as the already-ingested
  Personal Status Law and اللائحة as the already-ingested Marriage of a Saudi to a Non-Saudi
  Regulation; art 5 cross-references Personal Status Law arts 9 and 11 (minor / unsound-mind
  marriage authorization); arts 6-8 assign an information/referral role to the Ministry of
  Interior. Fresh full issuance — **all 10 records اصلية**. MOJ double-official pipeline: the
  official PDF is a **pure scanned/image document with no extractable text layer at all**
  (PyMuPDF returns empty on every page), so verification relied entirely on 300dpi tesseract-ara
  OCR per page, segmented per article; **8/10 articles cleared the ≥0.90 floor outright** (mean
  0.9425, min 0.7848); articles 5 and 10 (each the last article on its PDF page) were adjudicated
  **VISUALLY VERBATIM** against 400dpi zoomed crops of the rendered PDF — the low automated scores
  were an OCR-segmentation artifact from trailing page-footer/notary-stamp noise, not a text
  mismatch. No source anomalies documented — all 10 articles read identically in the portal DB
  and the official PDF. PDF committed (3 pages, sha256
  `8a230fcc2a2cb066c9f3da19739c4201917854d8deccc10f24266275855407d0`). Track under
  `sources/marriage_contract_hearing/regulation/`. Validate:
  `make marriage-contract-hearing-regulation-track-validate`.

## نظام مكافحة الرشوة — Anti-Bribery Law (29/12/1412هـ) — DISTINCT, LOWER-CONFIDENCE VERIFICATION TIER

- ⚠️ **This track does NOT use this corpus's normal double-official verification pipeline and is
  explicitly flagged, per-article, as a weaker trust tier than every other track in this corpus.**
  **Anti-Bribery Law (Royal Decree M/36, 29/12/1412هـ) — نظام مكافحة الرشوة** — **25 records**,
  consolidated amended law: **16 اصلية / 7 معدلة (arts 5, 8, 9, 14, 15, 17, 21) / 2 مضافة**
  (المادة التاسعة مكرر (1) and (2), inserted between arts 9 and 10 without renumbering subsequent
  articles), flat structure with no chapter/section wrapper. This law is **not MOJ-issued** and is
  absent from the MOJ legal portal; both of this corpus's established verification channels (MOJ
  portal database × official PDF; BOE official portal via Wayback byte-identical cross-snapshot)
  were **confirmed unreachable from the build environment across three dedicated research passes**
  this session: `laws.boe.gov.sa` fails at the TLS handshake stage (connection reset on every path
  tried), `web.archive.org` is blocked outright by the sandbox's own network egress policy, and
  `nazaha.gov.sa` (the natural regulator) was also unreachable. **Two ad hoc, lower tiers were used
  instead, and every article carries its own tier tag:**
  - **`SINGLE_PRIMARY_SOURCE_TOPICAL_CORROBORATION`** (16 unchanged-since-1412H articles): full
    verbatim text from **one** official source — a scanned booklet carrying the Bureau of Experts'
    own letterhead («هيئة الخبراء بمجلس الوزراء») at faculty.ksu.edu.sa, King Fahd National Library
    catalog entry dated 1417H — topically (not verbatim) corroborated by a second,
    independently-hosted 2-page summary table. Weaker than this corpus's usual article-by-article
    similarity cross-verification.
  - **`SECONDARY_SOURCE_CONVERGENCE_UNVERIFIED_PRIMARY`** (7 amended + 2 added articles): current
    text rests entirely on convergence between **two Saudi legal-publishing sites** (nezams.com,
    manielaw-sa.com) that are themselves **suspected to share a common upstream source** rather
    than being fully independent, plus one partial, non-full-text corroboration via a live fetch of
    the official Umm Al-Qura Gazette portal for the M/38 1443H amendment. **This is the weakest
    verification tier used anywhere in this corpus.**
  **AMENDMENTS:** art 5 broadened from «كل موظف عام» to «كل شخص» (M/38, 27/4/1443H); art 8 gained
  §§6–7 extending public-official status to civil-association staff and foreign/international-
  organization officials (M/4, 2/1/1440H, §7 refined by M/38); art 9 gained «أو وعد بها» (M/4,
  2/1/1440H); arts 9 مكرر (1)/(2) newly criminalize private-sector bribery on both the giving and
  taking side (M/4, 2/1/1440H); art 14 rewritten to route ancillary-penalty review through a
  Minister-of-Interior-chaired tripartite committee (M/21, 14/2/1442H); art 15's confiscation
  remedy expanded to cover value and proceeds (M/38, 27/4/1443H); arts 17 and 21 replaced
  «وزارة الداخلية» with «رئاسة أمن الدولة» (CoM Decision 633 / Royal Decree M/127, 6/11/1440H).
  **3 DOCUMENTED UNRESOLVED DISCREPANCIES** (see the source artifact's
  `known_unresolved_discrepancies` field): (1) art 17's exact current wording rests on 2-source
  agreement against one conflicting, unattributed secondary snippet; (2) art 14's reflection of the
  2024 Royal Decree M/25 authority-rename «هيئة الرقابة ومكافحة الفساد» was inferred from an
  already-updated secondary source, not read directly from M/25's own consequential-amendment
  clause; (3) art 9 مكرر (1) carries a possible stray-comma transcription artifact preserved
  verbatim. **Ingested only after the repository owner explicitly reviewed and approved this
  distinct tier** following two dedicated research passes confirming the primary MOJ/BOE/Umm-Al-
  Qura channels were unreachable. Both source PDFs committed (original 1412H booklet + consolidated
  current-text PDF, both sha256 recorded). Track under `sources/anti_bribery/law/`. Validate:
  `make anti-bribery-law-track-validate`.

## النظام الأساسي للحكم — Basic Law of Governance (27/8/1412هـ) — DISTINCT VERIFICATION TIER

- **Basic Law of Governance (Royal Order A/90, 27/8/1412هـ) verified + LLM-ready.**
  **النظام الأساسي للحكم** — **83 records**, consolidated text: **82 اصلية / 1 معدلة (art 5)**,
  organized under **9 chapters** — الباب الأول: المبادئ العامة (arts 1-4)؛ الباب الثاني: نظام الحكم
  (arts 5-8)؛ الباب الثالث: مقومات المجتمع السعودي (arts 9-13)؛ الباب الرابع: المبادئ الاقتصادية
  (arts 14-22)؛ الباب الخامس: الحقوق والواجبات (arts 23-43)؛ الباب السادس: سلطات الدولة (arts
  44-71)؛ الباب السابع: الشئون المالية (arts 72-78)؛ الباب الثامن: أجهزة الرقابة (arts 79-80)؛
  الباب التاسع: أحكام عامة (arts 81-83) — with `section_ar` carrying each article's chapter
  heading. Saudi Arabia's foundational constitutional-tier instrument.
  **⚠ POST-MERGE CORRECTION (see below after the spot-check paragraph):** Article 5 was
  originally ingested as اصلية and has since been corrected to معدلة after a cross-track
  conflict was discovered while ingesting the Allegiance Commission Law.
  **DISTINCT VERIFICATION TIER — stronger than the Anti-Bribery Law track, but still not this
  corpus's primary MOJ-portal pipeline** (this is a Council-of-Ministers/Bureau-of-Experts
  instrument, not MOJ-issued, absent from the MOJ legal portal). **PRIMARY source:** the Bureau of
  Experts (هيئة الخبراء بمجلس الوزراء) legal portal at `laws.boe.gov.sa`, reached via the
  **WebFetch tool with an `https://r.jina.ai/<url>` reader-proxy prefix** — direct sandbox network
  access to `laws.boe.gov.sa` fails at the TLS handshake/WAF level, but this proxy routes the
  fetch through Anthropic's own infrastructure instead, which Jina's reader accepts where this
  sandbox's own IP is rejected. Extraction is **COMPLETE and GAPLESS: all 83 articles across all 9
  chapters, in order, no missing articles.** **SECOND source:** WIPO Lex (entry SA016), a scanned,
  nationally-stamped (الهيئة الوطنية للوثائق والمحفوظات) government-submitted document using a
  different, older production pipeline (legacy custom Arabic font encoding, no usable text layer —
  rendered to 29 page images and OCR'd with tesseract-ara), genuinely independent rather than a
  mirror. Cross-verification was an **EXTENSIVE SPOT-CHECK across all 9 chapters and every chapter
  boundary — ~39 of 83 articles (~47%: arts 1-11, 14-25, 44-49, 69-73, 79-83) — NOT an exhaustive
  per-article diff**; every spot-checked article matched with no wording/meaning divergence; the
  full 83-article/9-chapter structure was confirmed to match in its entirety. Every article
  carries its own `cross_verified_against_wipo_lex` boolean tag. Two other candidate PDF mirrors
  (ibtissam.sa, nshr.org.sa) were found earlier but determined to be the same underlying scan
  re-hosted twice, not independent, and were not used. No amendment-tracking endpoint equivalent
  to the MOJ portal's get-Section-Changes was found on the BOE portal for this instrument — BOE's
  base "نص النظام" view displays the as-originally-promulgated text without merging subsequent
  amendments. WIPO Lex PDF committed (29 pages, sha256 recorded).
  **POST-MERGE CORRECTION:** while ingesting the Allegiance Commission Law, a cross-track
  conflict was discovered — that law's own promulgation order (Royal Order A/135, 26/9/1427H /
  2006) claims to amend this law's Article 5, paragraph (ج). A dedicated verification pass
  confirmed this amendment is genuine and in force, and additionally found a second amendment to
  Article 5, paragraph (ب) (Royal Order A/256, 26/9/1438H / 2017, the "single branch"
  succession-diversification restriction), verified via **primary-source OCR of the actual
  scanned Royal Order PDF** (WIPO Lex document sa102), independently corroborated by a Royal
  Court transmittal circular reproduced on the same document. Article 5 is now tagged معدلة with
  the original 1412H text and full amendment history preserved (not deleted), carrying a distinct
  `verification_tier` (`SECONDARY_SOURCE_PLUS_PRIMARY_OCR_CONFIRMED_AMENDMENT`) from the other 82
  BOE-portal-primary-verified articles; the track's overall `official_text_status` is accordingly
  now `MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER`. A full article-by-article amendment-history
  re-audit of the remaining 82 articles against BOE's dedicated amendments view is recommended as
  a follow-up, not assumed complete. Track under `sources/basic_law_of_governance/law/`. Validate:
  `make basic-law-of-governance-track-validate`.

## نظام مكافحة جرائم المعلوماتية — Anti-Cyber Crime Law (8/3/1428هـ) — STRONGEST DISTINCT TIER

- **Anti-Cyber Crime Law (Royal Decree M/17, 8/3/1428هـ) verified + LLM-ready.**
  **نظام مكافحة جرائم المعلوماتية** — **16 records**, fresh consolidated text: **all 16 اصلية**,
  flat structure with no chapter/section wrapper. **DISTINCT VERIFICATION TIER, but the
  STRONGEST used anywhere in this corpus outside the primary MOJ-portal pipeline**: full
  **EXHAUSTIVE** (not spot-check) article-by-article cross-verification across **THREE
  independent sources**, all matching word-for-word on **all 16 articles**. **PRIMARY:** the
  Bureau of Experts (BOE) legal portal at `laws.boe.gov.sa`, reached via WebFetch/curl through an
  `https://r.jina.ai/<url>` reader-proxy prefix. **SECOND:** WIPO Lex, hosting the CITC
  (Communications and Information Technology Commission) Official Translation Department's
  Arabic source PDF — a genuinely different production pipeline/host than BOE. **THIRD:** the
  Saudi Ministry of Finance regulations library, a scanned, officially stamped certified copy
  (visible seals of the Bureau of Experts, the Council of Ministers Presidency Diwan, and the
  Administrative Communications Center on every page). Both PDFs have no usable text layer;
  both were rendered to page images and read visually/OCR'd. **DOCUMENTED, INVESTIGATED BUT
  UNCONFIRMED DISCREPANCY:** the UN's UNODC SHERLOC legislative database attributes an added
  closing sentence to article 6 (Royal Decree M/54, 22/7/1436H); this sentence is **absent from
  all three cross-verified sources AND from the administering regulator's (CITC) own current
  text**; a dedicated follow-up research pass could not locate primary confirmation either way,
  and the cited clause is also a boilerplate formula reused across other unrelated Saudi laws —
  **not included** in this track's article 6 text pending independent primary-source
  confirmation. Both source PDFs committed with sha256 recorded. Track under
  `sources/anti_cyber_crime/law/`. Validate: `make anti-cyber-crime-law-track-validate`.

## نظام مكافحة جريمة التحرش — Anti-Harassment Law (16/9/1439هـ) — MIXED DISTINCT TIER

- **Anti-Harassment Law (Royal Decree M/96, 16/9/1439هـ) verified + LLM-ready.**
  **نظام مكافحة جريمة التحرش** — **8 records**, consolidated amended law: **7 اصلية / 1 معدلة
  (art 6)**, flat structure with no chapter/section wrapper. **DISTINCT VERIFICATION TIER with
  two sub-tiers within this single track.** (1) The 7 unamended articles (1-5, 7, 8): full
  verbatim text from the Bureau of Experts (BOE) legal portal at `laws.boe.gov.sa`, reached via
  WebFetch through an `https://r.jina.ai/<url>` reader-proxy prefix; cross-checked against four
  independent secondary Saudi legal-reference sites (nezams.com, saudipedia.com,
  mohamoon-ksa.com) plus an independent journalist's account (riyadhbureau.com), all agreeing
  with BOE with no divergence. (2) Article 6's **third paragraph**, added by **Royal Decree M/48
  (1/6/1442H, Cabinet-approved 12 Jan 2021)**: the BOE portal's currently-fetchable view does
  **not** show this paragraph (its amendment sub-tabs return HTTP 422), but the amendment's
  **existence** is confirmed with high confidence via Umm Al-Qura Gazette's own
  search-engine-indexed page title («إضافة فقرة إلى المادة (السادسة) من نظام مكافحة جريمة
  التحرش») plus two independent contemporaneous major news outlets (Asharq Al-Awsat, Al Bayan),
  both reporting the exact Cabinet approval date. **Two candidate wordings** were found for the
  added paragraph — this track uses the longer version (corroborated by the gazette's own
  indexed title/snippet and the two press reports of this exact decision), with the shorter
  alternate fully preserved in `known_unresolved_discrepancies` rather than silently discarded.
  Neither candidate was read directly off a fully-rendered primary document. Repository owner
  explicitly reviewed and approved this specific handling after a dedicated follow-up research
  pass. Track under `sources/anti_harassment/law/`. Validate:
  `make anti-harassment-law-track-validate`.

## نظام مكافحة جرائم الاتجار بالأشخاص — Anti-Trafficking in Persons Law (21/7/1430هـ) — DISTINCT TIER

- **Anti-Trafficking in Persons Law (Royal Decree M/40, 21/7/1430هـ) verified + LLM-ready.**
  **نظام مكافحة جرائم الاتجار بالأشخاص** — **17 records**, fresh full issuance, all **17 اصلية**,
  flat structure with no chapter/section wrapper. **DISTINCT VERIFICATION TIER:** full text
  extracted from a Wayback Machine capture (dated 2025-12-12) of the BOE legal portal's own
  LawDetails page (GUID `4e09c59d-f173-4971-8a38-a9a700f27025`) — the usual WebFetch +
  `r.jina.ai` reader-proxy method failed for this research pass (Jina returned a 401 IP-reputation
  block; direct fetch and WebFetch to `laws.boe.gov.sa` also failed). The Wayback capture is
  genuine BOE-served HTML, confirmed by inspecting the raw markup rather than cleaned text, and
  all 17 articles were confirmed complete and gapless against the page's own article-selector
  widget. Cross-verified for **substance** (not exact Arabic wording, since the second source is
  an English translation) against UNODC's official English translation (unodc.org/cld), genuinely
  independent of BOE, and additionally corroborated by the 2025 US State Department Trafficking
  in Persons (TIP) Report's penalty-structure citations. This is a weaker tier than this corpus's
  usual Arabic-to-Arabic comparison, since no second full-text Arabic source could be retrieved
  this session. **Documented finding:** a comprehensive 33-article, 6-chapter draft replacement
  law cleared public consultation in mid-2022 and would repeal/replace this law per its own draft
  Article 31, but remains **unenacted** as of the most recent evidence found (2025 US State
  Department TIP report; BOE's own December 2025 snapshot shows no amendment flags) — the draft is
  documented in `known_unresolved_discrepancies` rather than ingested or silently ignored. Track
  under `sources/anti_trafficking/law/`. Validate: `make anti-trafficking-law-track-validate`.

## نظام مجلس الوزراء — Council of Ministers Law (3/3/1414هـ) — DISTINCT TIER, BOE UNREACHABLE

- **Council of Ministers Law (Royal Order A/13, 3/3/1414H) verified + LLM-ready.**
  **نظام مجلس الوزراء** — **32 records**, consolidated amended law: **31 اصلية / 1 معدلة
  (art 30)**, 8 chapters with `section_ar` carrying each article's chapter heading. Supersedes the
  earlier Council of Ministers Law (Royal Decree No. 38, 22/10/1377H). **DISTINCT VERIFICATION
  TIER:** `laws.boe.gov.sa` was confirmed **completely unreachable** from the build environment
  across two separate research passes this session — a WAF "Request Rejected" block on the first
  pass, then a dedicated retry-confirmation pass hit 503/422/timeout, different failure signatures
  each time, confirming the block is genuine and current rather than a one-off transient error.
  Neither of this corpus's two established verification methods (MOJ portal DB x official PDF, or
  BOE-portal-via-Wayback byte-identical cross-snapshot) was available. Full text instead rests on
  **cross-verified word-for-word agreement between two independent Arabic secondary sources**
  (ar.wikisource.org, nezams.com); FAOLEX's English PDF (faolex.fao.org/docs/pdf/sau213444.pdf)
  was used only for a **structural** cross-check (chapter count, article count, general
  subject-matter match per chapter), not for wording. This is a distinct, clearly-flagged tier:
  dual independent Arabic secondary sources standing in for a primary official source that could
  not be reached. Article 30 (التشكيلات الإدارية لمجلس الوزراء) was amended by Royal Order أ/151
  (3/9/1432H), confirmed via nezams.com and qistas.com, removing «ديوان رئاسة مجلس الوزراء» from
  the list of administrative bodies — both the original and current wording preserved. Article 7
  carries a `companion_instrument_note` documenting Royal Order أ/45 (4/2/1446H), a linked
  exception order establishing a presiding-order fallback for Council meetings when neither the
  King nor the Council President nor any deputy attends — corroborated by the Umm Al-Qura Gazette
  listing, the Saudi Press Agency, and multiple news outlets — but explicitly framed in its own
  operative clause as «استثناءً من حكم المادة (7)» rather than a textual amendment, so it is NOT
  merged into Article 7's own text. A fresh BOE retry from a different network path is recommended
  before this track is treated as fully primary-source-anchored (documented in
  `known_unresolved_discrepancies`). Track under `sources/council_of_ministers/law/`. Validate:
  `make council-of-ministers-law-track-validate`.

## نظام المناطق — Regions/Provinces Law (27/8/1412هـ) — DISTINCT TIER, BOE PAGE UNREACHABLE

- **Regions/Provinces Law (Royal Order A/92, 27/8/1412H) verified + LLM-ready.**
  **نظام المناطق** — **41 records**, consolidated amended law: **31 اصلية / 9 معدلة / 1 مضافة**,
  flat structure with no chapter/section wrapper. Published in Umm Al-Qura Gazette issue 3397,
  2/9/1412H. **DISTINCT VERIFICATION TIER:** this law's specific BOE LawDetails page could not be
  reached across roughly 20 attempts over 45+ minutes this research pass (direct curl,
  curl+r.jina.ai with varied timeout/wait-for-selector/engine headers, and WebFetch+r.jina.ai) —
  consistent network-idle timeouts, a Cloudflare 524, and rate-limit blocks (401 "bad IP
  reputation", 403 "consecutive error"). The same method successfully fetched a **different** BOE
  law page in 19s in this same session, so this appears to be a page-specific hang rather than a
  systemic block; a follow-up attempt from a fresh session is recommended. Full text instead rests
  on **cross-verified agreement between two independent Arabic secondary sources**
  (islamport.com's "الموسوعة الشاملة" and nezams.com) — substantively identical, only trivial
  OCR/spelling slips found and corrected against the cross-source. FAOLEX's official English
  translation (faolex.fao.org/docs/pdf/sau213421.pdf) was used only as a **weaker meaning-level**
  cross-check (English, not Arabic) and was confirmed **incomplete** (stops at article 40, omits
  article 41) and carrying an **internal date error** (its header says 1414H, contradicting its
  own decree text and all Arabic sources' 1412H). A single consolidating amendment, Royal Order
  أ/21 (30/3/1414H), amended articles 3, 7, 9, 10, 11, 12, 13, 16, and 37, and added article 41 —
  fully incorporated as the current in-force text. A related non-textual instrument, Royal Order
  أ/112 (28/6/1414H), lists the Kingdom's 13 regions and administrative seats implementing Article
  2 — documented but not ingested as an article. Track under `sources/regions/law/`. Validate:
  `make regions-law-track-validate`.

## نظام التعاملات الإلكترونية — Electronic Transactions Law (8/3/1428هـ) — DISTINCT TIER

- **Electronic Transactions Law (Royal Decree M/18, 8/3/1428H) verified + LLM-ready.**
  **نظام التعاملات الإلكترونية** — **31 records**, consolidated amended law: **24 اصلية / 5
  معدلة / 2 ملغاة**, 10 chapters with `section_ar` carrying each article's chapter heading.
  Distinct from the Anti-Cyber Crime Law (M/17, same council session, different decree,
  different WIPO Lex catalogue entry — confirmed via three independent sources). **DISTINCT
  VERIFICATION TIER:** `laws.boe.gov.sa` was unreachable this research pass by every method
  tried (direct curl TLS reset; `r.jina.ai` timed out repeatedly then rate-limited the IP with
  a 401; WebFetch via the same proxy 422'd). **PRIMARY SOURCE USED INSTEAD:** the official
  Bureau of Experts/Council of Ministers "Official Translation Division" bilingual PDF
  (sdb.gov.sa-hosted, first edition 1431H) — the same booklet BOE itself distributes for this
  law, downloaded directly with plain curl. **EXTRACTION HAZARD:** this PDF's embedded text has
  a systematic, deterministic lam+alef ligature-reversal bug (e.g. correct "التعاملات" extracts
  as "التعامالت"), confirmed baked into the PDF itself via two independent extraction libraries
  giving identical corruption, and the PDF renders as entirely blank pages (ruling out OCR as a
  cross-check) — corrected via direct native-fluency reading, article by article, rather than
  blind regex substitution. **CROSS-VERIFICATION:** structurally, 100% of articles, against the
  complete official WIPO Lex English translation (no discrepancies found); wording spot-checks
  against independent clean-Unicode Arabic sources (ramilawyer.sa, qanoniah.com,
  lexismiddleeast.com, uqn.gov.sa/Umm Al-Qura Gazette). A **2023 amendment** (Council of
  Ministers Resolution 293, 9/4/1445H, sourced from a fourth independent HTML source never
  affected by the ligature bug) replaced Ministry/Communications-and-IT-Commission references
  with the Digital Government Authority, textually amended articles 1, 3 (last clause), the
  Chapter 5 title, 15, 29, and 30, and **ABOLISHED Chapter 6** (articles 16-17, National Center
  for Digital Certification) entirely — both articles are flagged ملغاة with their original
  text preserved, not deleted. **IMPORTANT DOCUMENTED GAP:** the resolution states chapters
  after Chapter 6 are "renumbered accordingly", which clearly shifts chapter numbers but does
  not explicitly confirm article-number renumbering for articles 18-31 — the live consolidated
  BOE text that would confirm this was unreachable, so this track deliberately preserves the
  **original 1-31 article numbering** rather than guessing, with the gap documented for a
  follow-up pass. A WIPO Lex metadata anomaly (decree listed as "M/8" with an extra "حماية" in
  the title, contradicted by three sources) is also flagged. Track under
  `sources/electronic_transactions/law/`. Validate:
  `make electronic-transactions-law-track-validate`.

## نظام هيئة البيعة — Allegiance Commission Law (26/9/1427هـ) — DISTINCT TIER

- **Allegiance Commission Law (Royal Order A/135, 26/9/1427H) verified + LLM-ready.**
  **نظام هيئة البيعة** — **25 records**, fresh issuance, all **25 اصلية**, flat structure
  with no chapter/section wrapper. Establishes the body that selects/confirms the Crown Prince
  among the sons and grandsons of King Abdulaziz. **DISTINCT VERIFICATION TIER:** the BOE
  portal's exact LawDetails page for this law was located (GUID
  `3213c2f6-eaf8-45dc-8f8c-a9a700f167ee`) but was **unreachable** by every method tried this
  research pass (direct fetch HTTP 503; `r.jina.ai` reader-proxy HTTP 422/timeout; Wayback
  Machine blocked by this sandbox's network egress policy despite a valid archived snapshot
  existing). Instead, **three independent Arabic secondary sources** were fetched and
  cross-compared directly (ar.wikisource.org, islamport.com, ar.wikipedia.org), agreeing on all
  25 articles almost word-for-word — the **strongest secondary-source tier used anywhere in
  this corpus**, though still not BOE-primary-verified. One wording discrepancy (Article 21:
  "تأجيل" vs "تعديل" الاجتماع) is documented, with the majority (2-of-3 source) reading
  ingested and the minority preserved. **CRITICAL CROSS-TRACK CONFLICT, NOT SILENTLY
  RESOLVED:** this law's own Royal Order promulgation preamble (clause "ثانيا") claims to amend
  Article 5, paragraph (c), of the Basic Law of Governance — but this corpus's own Basic Law of
  Governance track (ingested earlier this session) shows different, pre-amendment wording for
  that paragraph. A dedicated verification pass confirmed the amendment is genuine and in
  force; **a follow-up correction PR for the Basic Law of Governance track is queued
  separately** rather than silently patched here. Track under
  `sources/allegiance_commission/law/`. Validate:
  `make allegiance-commission-law-track-validate`.

## نظام مجلس الشورى — Shura Council Law (27/8/1412هـ) — MIXED TIER

- **Shura Council Law (Royal Order A/91, 27/8/1412H) verified + LLM-ready.**
  **نظام مجلس الشورى** — **30 records**, consolidated amended law: **24 اصلية / 6 معدلة**,
  flat structure with no chapter/section wrapper. Issued the same day as the Basic Law of
  Governance (A/90); replaces the earlier 1347H Shura Council law. **MIXED VERIFICATION TIER,
  tagged per-article:** the BOE portal's exact LawDetails page for this law was located but
  unreachable by every method tried this research pass (direct fetch HTTP 503; a direct curl
  attempt returned a TLS/connection reset; `r.jina.ai` returned repeated timeout/422; Wayback
  Machine blocked by sandbox egress policy). 29 articles rest on **triple independent Arabic
  secondary sources** (ar.wikisource.org, nezams.com, a King Saud University faculty-hosted
  PDF), all agreeing word-for-word. Article 3's **current** (2013-amended, 20% female-quota)
  text is additionally confirmed via a **Tier-1 government primary source**: the Saudi Press
  Agency's verbatim reproduction of Royal Order أ/44 (29/2/1434H). **Full amendment history**:
  article 3 was amended three times (أ/78 1422H: 60→120 members; أ/26 1426H: 120→150 members;
  أ/44 1434H/2013: 20% female quota added — current); articles 10, 21, 29 were each amended
  once by أ/181 (1428H, adding "ومساعده"); articles 17, 23 were each amended once by أ/198
  (1424H, decision-routing and legislative-proposal mechanism changes). No amendments were
  found after 2013 despite searches through 1446H/2025. **Documented gap**: Royal Order أ/78
  (1422H, article 3's first amendment) was never located as a primary or full-text secondary
  source — only cited by later sources — flagged as an unresolved provenance gap rather than
  presented as confirmed. Track under `sources/shura_council/law/`. Validate:
  `make shura-council-law-track-validate`.

## نظام حماية حقوق المؤلف — Copyright Law (2/7/1424هـ) — DISTINCT TIER, SUPERSEDED 2026-08-01

- **Copyright Law (Royal Decree M/41, 2/7/1424H) verified + LLM-ready.**
  **نظام حماية حقوق المؤلف** — **28 records**, consolidated amended law: **19 اصلية / 9
  معدلة**, 7 chapters (plus article 1's own definitions heading) with `section_ar` carrying
  each article's chapter heading. Supersedes the earlier 1989 copyright law (M/11). **DISTINCT
  VERIFICATION TIER:** `laws.boe.gov.sa` was unreachable this research pass (direct connection
  reset; `r.jina.ai` timed out twice; Wayback Machine snapshot existed but the fetch was
  blocked/403'd in this sandbox). **PRIMARY WORKING SOURCE:** qadha.org.sa (الجمعية العلمية
  القضائية السعودية, a Saudi judicial-studies professional association) — full verbatim
  article-by-article text footnoted with the exact 2018 amendment decision text, extracted
  cleanly via `pdftotext -layout`. Cross-checked structurally against WIPO Lex (entry sa062,
  chapter/article count/order confirmed; the PDF itself extracted with word-internal character
  scrambling and could not be used for verbatim wording) and spot-checked against an
  independent blog (almirjah.wordpress.com, which quotes several articles in their **pre-2018**
  wording — useful corroboration the amendment is correctly reflected, not a contradiction). All
  11 locations the 2018-amendment footnote says were changed were independently checked and
  confirmed. **2018 amendment** (Council of Ministers Resolution 536, 19/10/1439H): replaced
  Ministry/Minister («الوزارة»/«الوزير») references with the Saudi Authority for Intellectual
  Property and its Board («الهيئة»/«المجلس») throughout — 9 articles amended.
  **⚠ CRITICAL: THIS LAW IS CONFIRMED SUPERSEDED EFFECTIVE 2026-08-01** by Royal Decree M/169
  (14/08/1447H / 2 February 2026), confirmed via multiple independent Arabic news outlets and
  English law-firm client alerts — but the **new law's full Arabic primary text could NOT be
  verified this research pass** (too new to be indexed by BOE/WIPO Lex/SAIP yet) and is
  explicitly **NOT ingested**, consistent with this corpus's zero-fabrication policy. This track
  ingests the text in force as of the build date (2026-07-17); a follow-up ingestion pass for
  M/169 is recommended once its primary text becomes verifiable. Track under
  `sources/copyright/law/`. Validate: `make copyright-law-track-validate`.

## نظام الاتصالات وتقنية المعلومات — Telecommunications and Information Technology Act (2/11/1443هـ) — DISTINCT TIER, BOE REACHABLE

- **Telecommunications and Information Technology Act (Royal Decree M/106, 2/11/1443H)
  verified + LLM-ready.** **نظام الاتصالات وتقنية المعلومات** — **41 records, all اصلية**
  (fresh replacement law, no confirmed enacted amendments), 10 chapters with `section_ar`
  carrying each article's chapter heading. Approved by Council of Ministers Resolution 592
  (1/11/1443H) following Shura Council Resolution 85/16 (16/5/1443H), published in Umm Al-Qura
  11/11/1443H. Explicitly repeals and replaces the 2001 telecom law (نظام الاتصالات, Royal
  Decree M/12, 12/3/1422H) per its own Article 41(1), confirmed via the BOE portal's own
  "الحالة: ساري" (in force) metadata field. **DISTINCT VERIFICATION TIER:** `laws.boe.gov.sa`
  **was reachable** this research pass (via the `https://r.jina.ai/<url>` reader-proxy fallback,
  both via WebFetch and a direct `curl` through the proxy) and served as the **primary source** —
  full verbatim text extracted: decree preamble, Council of Ministers Resolution text, and all
  41 articles with chapter headings, in order, no gaps. **CROSS-VERIFICATION:** an independent
  official government PDF hosted at mcit.gov.sa (the Ministry of Communications and IT) was
  separately downloaded and extracted via `pdftotext -layout`; it agrees with the BOE text
  word-for-word across all 41 articles, with **one identified and resolved extraction
  artifact** — the MCIT PDF's Article 6 paragraph numbering rendered as 1,3,3,4,5 (a
  digit-rendering/bidi artifact of that specific PDF extraction), corrected to the true
  1,2,3,4,5 sequence per the clean BOE text. Further corroborated by CST's own portal page
  (cst.gov.sa) and by nezams.com independently confirming decree number, date, and the
  41-article count. **⚠ UNENACTED PROPOSED AMENDMENT:** a public consultation (8 July–7 August
  2024, istitlaa.ncc.gov.sa/eparticipation.my.gov.sa, consultation ID legal-consultation-42512)
  proposed changes to Articles 20 (ownership-change threshold), 24 (internet-filtering-
  circumvention language), 25 (inspector-appointment procedures), and 27 (deleting paragraph د,
  adding a Tadawul-listing requirement provision) — whether this package was formally enacted
  **could NOT be confirmed** (no BOE record of a subsequent amending instrument, no Umm Al-Qura
  Gazette notice found), so this track ingests the **confirmed BOE "in force" text** (not
  reflecting the 2024 proposal), flagged in `known_unresolved_discrepancies` for periodic
  re-verification. Article 41(2)'s exact Gregorian effective date carries a minor unresolved
  ~3-day discrepancy across sources (immaterial to the article's own unambiguous Arabic text:
  180 days after Gazette publication). Article 25's raw BOE extraction contained purely
  decorative tatweel elongation characters (U+0640), stripped during ingestion per this corpus's
  standard tatweel-normalization practice — no wording altered. A companion Implementing
  Regulation exists (mcit.gov.sa) but was not extracted this pass — candidate for a follow-up
  companion-track ingestion. Track under `sources/telecommunications/law/`. Validate:
  `make telecommunications-law-track-validate`.

## نظام البنك المركزي السعودي — Saudi Central Bank Law (11/4/1442هـ) — DISTINCT TIER, BOE LIVE PORTAL UNREACHABLE THIS PASS

- **Saudi Central Bank Law (Royal Decree M/36, 11/4/1442H) verified + LLM-ready.**
  **نظام البنك المركزي السعودي** — **27 records**, consolidated amended law: **24 اصلية / 3
  معدلة**, 6 chapters (Chapter 2 has 3 lettered subsections: (a) Board of Directors arts 8-12,
  (b) Governor/Deputy Governors/Staff arts 13-15, (c) Conflict of Interest art 16) with
  `section_ar` carrying each article's chapter/subsection heading. Replaces the earlier Saudi
  Arabian Monetary Agency (SAMA) Law, Royal Decree No. 23 (23/5/1377H), per Article 26.
  **Confirmed decree date 11/4/1442H via four independent means** — the originally-briefed
  "11/2/1442H" is confirmed erroneous, traced to a Bureau of Experts internal drafting-committee
  memo date cited in the Council of Ministers Resolution's own recitals, not the decree's own
  date. **Distinct from the separate Banking Control Law** (نظام مراقبة البنوك) — not conflated.
  **DISTINCT VERIFICATION TIER:** `laws.boe.gov.sa`'s live portal returned HTTP 503 on every
  direct and `r.jina.ai`-proxied attempt this research pass. **PRIMARY SOURCE A (current text):**
  SAMA's own official PDF (sama.gov.sa), cross-checked page-by-page against rendered page images
  for every amended article, since automated layout-preserving extraction garbled RTL
  multi-column lettering in Articles 8 and 10. **PRIMARY SOURCE B (original text):** a Wayback
  Machine archive snapshot of the BOE portal's law-detail page dated 24 Jan 2022 — before the
  sole amending instrument. **SECONDARY CORROBORATION:** qistas.com, nezams.com, ajel.sa.
  **AMENDMENT** (Council of Ministers Resolution 412, 28/7/1443H): restructured the Governor's
  deputies from **one Deputy Governor to two**, amending Articles 8, 11, and 14 — both original
  and amended wording recovered and preserved via `original_1442h_text` — and the Chapter 2(b)
  section heading itself («نائب» → «نائبا», documented in `chapter_structure`, not modeled as its
  own article). **⚠ THREE FLAGGED DISCREPANCIES**, all confirmed genuine artifacts in the
  primary source itself via direct visual inspection (not extraction errors) and preserved
  verbatim, never silently corrected: Article 9 still cross-references Article 8's subclause
  «(ج)» though it was relettered to «(ت)» by the amendment; Article 12 still cross-references
  Article 8's «الفقرة (2)» though the amendment renumbered that content to paragraph (3);
  Article 10's eight sub-items are lettered in classical abjad order in the pre-amendment BOE
  text but plain alphabetical order in SAMA's current PDF, with identical content either way.
  No dedicated Implementing Regulation for this specific law was found as of the build date. No
  irrecoverable gaps. Track under `sources/sama/law/`. Validate: `make sama-law-track-validate`.

## نظام مراقبة البنوك — Banking Control Law (22/2/1386هـ) — DISTINCT TIER, BOE UNREACHABLE FOR RAW TEXT

- **Banking Control Law (Royal Decree M/5, 22/2/1386H) verified + LLM-ready.**
  **نظام مراقبة البنوك** — **26 records**, consolidated amended law: **25 اصلية / 1 معدلة**,
  **no chapter (فصل) divisions** — a flat sequence, confirmed independently by three sources.
  Issued by King Faysal bin Abdulaziz Al Saud, based on Council of Ministers Resolution 179
  (5/2/1386H), published in Umm al-Qura Gazette, Issue 2126 (5/3/1386H). **Distinct from the
  Saudi Central Bank Law** (نظام البنك المركزي السعودي, Royal Decree M/36, 1442H, already in
  this corpus) — not conflated; this law governs commercial banking licensing/supervision
  specifically. **DISTINCT VERIFICATION TIER:** `laws.boe.gov.sa` was unreachable for raw text
  this research pass (HTTP 503 live; HTTP 422 via `r.jina.ai`; a Wayback Machine snapshot
  returned HTTP 403 to direct fetch and was unreachable via WebFetch entirely) — only BOE's own
  tool-side summarization (not raw text) was obtainable, confirming metadata (decree number,
  date, 26-article count, issuing authority) but not usable as a primary verbatim-text source.
  Full text instead rests on **cross-verified agreement between two independent Arabic secondary
  sources**: alsayrfah.com's reproduction and bfc.gov.sa's reproduction (a Saudi finance-sector
  regulator's own copy, which uniquely preserves the Umm al-Qura Gazette masthead and the sole
  amendment's footnote) — both agree word-for-word on all 26 articles' substantive wording.
  Further corroborated structurally by Saudipedia.com and BOE's own tool-side summary.
  **AMENDMENT:** Article 13, paragraph 2 was amended by Royal Decree M/2 (6/1/1391H, based on
  Council of Ministers Resolution 1135, 21/12/1390H) — only the **current wording was
  recoverable**; the pre-1391H original could **not** be found in any source reached this pass,
  flagged in `known_unresolved_discrepancies` as an irrecoverable gap rather than reconstructed
  or guessed, consistent with this corpus's zero-fabrication policy. **⚠ A FURTHER SOURCE-TEXT
  IRREGULARITY** is flagged and preserved verbatim: Article 16 opens with «مؤسسة النقد» instead
  of the term «المؤسسة» defined in Article 1(هـ) and used consistently elsewhere — present
  identically in both independent source PDFs, a probable genuine drafting inconsistency in the
  original 1386H text, not an extraction artifact. Article 1 and Article 11's sub-clause
  lettering also suffered a bidi/RTL-numeral extraction artifact in one of the two source PDFs
  specifically; resolved using the cleaner source's rendering (classical abjad أ ب ج د هـ و
  lettering), internally consistent with Article 23's own cross-reference to «البنود (أ, ب, ج)
  من ... المادة الحادية عشرة» — a source-quality resolution, not a silent guess. A companion
  Implementing Regulation (قواعد تطبيق أحكام نظام مراقبة البنوك) exists per SAMA's Rulebook
  catalogue but was not extracted this pass — candidate for a follow-up companion-track
  ingestion. Track under `sources/banking_control/law/`. Validate:
  `make banking-control-law-track-validate`.

## نظام السوق المالية — Capital Market Law (2/6/1424هـ) — MIXED TIER, MOST COMPLEX TRACK TO DATE

- **Capital Market Law (Royal Decree M/30, 2/6/1424H) verified + LLM-ready.**
  **نظام السوق المالية** — **68 records**, mixed verification tier: **42 اصلية / 25 معدلة /
  1 مضافة** (Article 20 مكرر). Administering authority: Capital Market Authority (CMA).
  **⚠ THE MOST COMPLEX VERIFICATION CASE HANDLED IN THIS CORPUS TO DATE.** The 2003 original
  text (67 articles) is fully verified with **high confidence** via `laws.boe.gov.sa`. The law
  has since been substantially amended, principally by Royal Decree M/16 (19/1/1441H, Cabinet
  Decision 52/1441, ~17 September 2019), restructuring the Market/Depository/Clearing-Center
  regime and relocating the disputes committee into a new Chapter 4 (Article 30). An earlier
  candidate amending instrument, Royal Decree M/24 (15/3/1443H), was investigated and
  **confirmed unrelated** — it amends the Finance Companies Supervision Law, a different
  statute entirely. Across **three research passes** (direct `cma.gov.sa` fetches with
  WAF-avoidance spacing, Wayback Machine fallback for two WAF-broken pages, PDF cross-checks),
  the CURRENT verbatim text was recovered and verified for **55 of 68 records** — either
  confirmed **UNCHANGED** from 2003 (word-for-word match) or independently fetched in full
  from `cma.gov.sa` where amended. **⚠ FOR 12 ARTICLES** (1, 20, 21, 22, 23, 25, 26, 27, 28,
  29, 30, 59) — precisely the articles at the core of the M/16 restructuring — the exact
  current wording could **NOT** be recovered despite three passes (CMA's WAF, a genuinely
  broken Chapter 8 sub-page, and `laws.boe.gov.sa`'s TLS-reset blocking every attempt to read
  M/16's own gazette text). **Per this corpus's zero-fabrication policy, these 12 articles are
  ingested using the 2003 ORIGINAL text as a clearly-flagged HISTORICAL placeholder, NOT
  presented as current law** — each carries its own `verification_tier` field
  (`ORIGINAL_2003_TEXT_ONLY_CURRENT_WORDING_CONFIRMED_AMENDED_UNVERIFIED`) distinct from the
  track's main tier, plus a dedicated `known_unresolved_discrepancies` entry. **A 68th record,
  Article 20 مكرر** (a new inserted article), is **reconstructed** from the research agent's
  explicit description that it "verbatim relocates paragraphs (ج) and (د) of the original
  Article 20" — its own lower-confidence tier
  (`RECONSTRUCTED_FROM_DOCUMENTED_RELOCATION_DESCRIPTION`), not a direct fetch. The current
  chapter (فصل) map could not be fully reconstructed given the Article-30 relocation;
  `chapter_structure` is left **empty (flat)** rather than asserting an unconfirmed map — only
  Chapter 8 (arts 49-50, "الفصل الثامن") and Chapter 10 (arts 55-67, "الفصل العاشر")
  boundaries are independently confirmed. Track under `sources/capital_market/law/`. Validate:
  `make capital-market-law-track-validate`.

## نظام المنافسة — Competition Law (29/6/1440هـ) — DISTINCT TIER, BOE WAYBACK SNAPSHOT

- **Competition Law (Royal Decree M/75, 29/6/1440H) verified + LLM-ready.**
  **نظام المنافسة** — **28 records**, all **اصلية** — **no chapter (فصل) divisions**, a
  flat sequence, confirmed identically by three sources. Administering authority: General
  Authority for Competition (GAC). Approved by Council of Ministers Decision 372 (28/6/1440H).
  **Confirmed decree date 29/6/1440H via three independent sources agreeing numerically**
  (BOE portal via two Wayback Machine snapshots dated ~Nov 2023 and 2026, WIPO Lex,
  nezams.com) — corrects the initial task-briefing's hypothesized "29/7/1440H". **Replaces
  the earlier Competition Law**, Royal Decree M/25 (4/5/1425H), per Article 26. **No confirmed
  amendments since the 2019 issuance** — nezams.com's own metadata field explicitly states no
  amendments were made, corroborated by the current BOE snapshot. **DISTINCT VERIFICATION
  TIER:** `laws.boe.gov.sa`'s live portal was unreachable this pass, but a Wayback Machine
  snapshot (fetched directly, not via `r.jina.ai`) succeeded at two separate points in time
  and agrees **WORD-FOR-WORD** with an independent secondary source, nezams.com. A third
  source, WIPO Lex's own Arabic PDF, substantively agrees but has one apparent extra word in
  Article 3(2) attributable to known PDF bidi-extraction artifacts, not used. **⚠ A
  candidate amendment record** for Articles 11/12 (Council of Ministers Decision 97,
  2/2/1441H) found in a 2023 BOE snapshot was investigated and **confirmed to belong to a
  DIFFERENT instrument** (the GAC's own organizational statute, تنظيم الهيئة العامة
  للمنافسة) — a probable cross-linking display bug since resolved on BOE's site (absent from
  the 2026 snapshot), flagged in `known_unresolved_discrepancies`, not applied as an
  amendment to this law. A companion Implementing Regulation exists per Article 27, reportedly
  issued via GAC Board Decision 337 (25/1/1441H), but this decision's exact number/date rests
  only on secondary search-summary evidence (GAC's own site unreachable this pass) — flagged,
  not extracted. Track under `sources/competition/law/`. Validate:
  `make competition-law-track-validate`.

## نظام المدفوعات وخدماتها — Payment Systems and Services Law (22/3/1443هـ) — DISTINCT TIER, SAMA PDF OCR

- **Payment Systems and Services Law (Royal Decree M/26, 22/3/1443H) verified + LLM-ready.**
  **نظام المدفوعات وخدماتها** — **20 records**, all **اصلية** — **no chapter (فصل)
  divisions**, a flat sequence. Administering authority: Saudi Central Bank (SAMA). Based on
  Council of Ministers Resolution 171 (20/3/1443H), published Umm al-Qura 30/3/1443H. Confirmed
  **in force (ساري)**; no amending instrument identified. **Distinct from the Saudi Central
  Bank Law** (M/36, 1442H) **and the Banking Control Law** (M/5, 1386H) — a separate instrument
  governing payment systems and services specifically, not merged into `sources/sama/` or
  `sources/banking_control/`. **DISTINCT VERIFICATION TIER:** the official SAMA PDF
  (`rulebook.sama.gov.sa`) has a **broken font ToUnicode CMap** that corrupts direct
  `pdftotext`/PyMuPDF extraction — worked around by rendering pages to images at **300dpi and
  400dpi** and running **two independent Arabic-language OCR passes** directly on the glyphs,
  cross-filling gaps between passes, then cross-verifying the OCR'd text **word-for-word**
  against nezams.com's independent raw-HTML transcription. `rulebook.sama.gov.sa`'s law-detail
  page corroborates decree/date/status/article count; Saudipedia corroborates the fine cap and
  objectives language. **⚠ Two flagged discrepancies**, both confirmed genuine rather than
  artifacts: Article 12(5) is a single, extremely long run-on sentence, identical across both
  OCR passes and nezams.com; the defined term «نظام مدفوعات مهم» is rendered with guillemets
  in Article 7(6) per nezams.com but with plain parentheses in Article 9 in the same source —
  OCR could not independently confirm SAMA's original glyph at either location, so each
  article's punctuation is preserved as transcribed rather than normalized. A companion
  Implementing Regulation (24/11/1444H, SAMA Circular 44093096) is confirmed to exist but is
  **not extracted** in this track — candidate for a follow-up companion-track ingestion. Track
  under `sources/payment_systems/law/`. Validate:
  `make payment-systems-law-track-validate`.

## نظام الاستثمار التعديني — Mining Investment Law (19/10/1441هـ) — DISTINCT TIER, BOE WAYBACK x FAOLEX

- **Mining Investment Law (Royal Decree M/140, 19/10/1441H) verified + LLM-ready.**
  **نظام الاستثمار التعديني** — **64 records** across **8 chapters (أبواب)** — **63 اصلية /
  1 مضافة**. Administering authority: Ministry of Industry and Mineral Resources and the Saudi
  Geological Survey. Based on Council of Ministers Resolution 634 (17/10/1441H) and Shura
  Council Resolution 167/35 (21/8/1441H), published Umm al-Qura 12/11/1441H. **Replaces** the
  prior mining law, Royal Decree M/47 (20/8/1425H). **DISTINCT VERIFICATION TIER:**
  `laws.boe.gov.sa`'s live portal was unreachable this pass (503/connection-reset via both
  WebFetch and direct curl) — full text instead rests on a **Wayback Machine snapshot of the
  BOE portal, fetched directly via curl** (not via `r.jina.ai` or WebFetch, neither of which can
  reach `archive.org`), cross-verified structurally against FAOLEX (whose own text extraction
  was severely word-scrambled by a known RTL-PDF artifact and was never used as a verbatim-text
  source), further corroborated by `taadeen.sa` PDF metadata and nezams.com. **13 articles** (4,
  6, 7, 8, 9, 10, 11, 14, 15, 16, 18, 19, 35) carry a documented **commencement-date-only**
  administrative amendment (Royal Decree M/12, 8/1/1442H, bringing them into force early as an
  exception to Article 63's general 180-day rule) — their **substantive text is unchanged**, so
  per this corpus's text-change-based status policy they remain **اصلية**, with the
  administrative note preserved in `amendment_history`. **1 wholly new article** — **Article 56
  مكرر** — inserted by Royal Decree M/27 (4/2/1444H), introducing criminal penalties (up to two
  years' imprisonment and/or a fine up to SAR 1,000,000, doubled on recidivism) for unlicensed
  extraction. **⚠ Two flagged discrepancies:** Article 50 has a genuine source-text renumbering
  irregularity (a "3." clause immediately followed by another "3-" clause instead of "4."),
  preserved verbatim; nezams.com's AI-summarized page claims the law has never been amended,
  directly contradicted by BOE's own record of Article 56 مكرر's 1444H addition — BOE (the
  primary/official source) is treated as authoritative. Decorative tatweel characters were
  stripped from 13 articles during transcription (pure typographic normalization, not a textual
  alteration). A companion Implementing Regulation exists (Ministerial Decision 1006/1/1442,
  9/5/1442H, 166 articles/7 chapters, later amended by Ministerial Decision 3293/1/1444,
  5/6/1444H) but is **not extracted** in this track. Track under `sources/mining_investment/law/`.
  Validate: `make mining-investment-law-track-validate`.

## قانون (نظام) العلامات التجارية — Trademark Law (26/7/1435هـ) — DISTINCT TIER, WIPO LEX x BOE STATUS CARD

- **Trademark Law (Royal Decree M/51, 26/7/1435H) verified + LLM-ready.** The GCC-unified
  Trademarks Law given domestic force in Saudi Arabia — **قانون (نظام) العلامات التجارية لدول
  مجلس التعاون لدول الخليج العربية** — **52 records**, **51 اصلية / 1 معدلة** — **no chapter
  (فصل) divisions**, a flat sequence verified by full-text search. Issued in the name of King
  Abdullah bin Abdulaziz Al Saud, signed by Deputy King Salman bin Abdulaziz Al Saud under Royal
  Order A/145; based on Council of Ministers Resolution 306 (20/7/1435H) and Shura Council
  Resolution 13/21 (17/4/1435H), approved by the GCC Supreme Council at its 33rd session.
  **Replaces** the prior GCC trademark law, Royal Decree M/94 (23/11/1428H). Administering
  authority: Saudi Authority for Intellectual Property (SAIP). **Article 1 amended** by Royal
  Decree M/49 (26/6/1442H) — two of five definitions, «الجهة المختصة» and «الوزير», replaced to
  reflect the transfer of administering authority to SAIP; the other three definitions and all
  51 remaining articles are unamended; the original 1435H definitions are preserved as
  provenance. **DISTINCT VERIFICATION TIER:** `laws.boe.gov.sa`'s live portal was unreachable
  this pass — full text instead rests on **WIPO Lex's own hosted Arabic PDF**, which embeds an
  official «بطاقة النظام» (law status card) sourced from the **Saudi National Center for
  Documents and Archives** confirming **ساري** (in force) — the functional equivalent of a
  direct BOE-portal confirmation via a different retrieval path. The amending Royal Decree M/49
  was a scanned/non-text PDF, recovered via **two independent Arabic-language OCR passes** that
  agreed verbatim. **⚠ Flagged conflict — the most consequential finding for this track:** two
  secondary sources, `misa.gov.sa`'s own hosted "official translation" and nezams.com, **both**
  still present the **superseded 2002 law** (Royal Decree M/21) as if currently in force — this
  track proceeds on the primary BOE-status-card-confirmed current law (M/51 as amended by M/49)
  instead; the conflict is preserved as audit provenance, not silently resolved. Additional
  flagged discrepancies: inconsistent hijri/gregorian dates for M/51 and M/49 across the
  sources' own metadata fields, and an unresolved M/21→M/94→M/51 repeal-chain ambiguity. A
  raw ه/ھ glyph-encoding artifact in the source PDF was normalized during transcription (pure
  typographic correction). A companion Implementing Regulation exists (GCC Trade Cooperation
  Committee, 51st meeting, 21 May 2015) but is **not extracted** in this track. Track under
  `sources/trademark/law/`. Validate: `make trademark-law-track-validate`.

## نظام مكافحة التستر — Anti-Concealment Law (1/1/1442هـ) — DISTINCT TIER, TRIPLE ARABIC SOURCE, BOE UNREACHABLE

- **Anti-Concealment Law (Royal Decree M/4, 1/1/1442H) verified + LLM-ready.**
  **نظام مكافحة التستر** — **20 records** across **5 chapters (فصول)** — all **اصلية**.
  Administering authority: Ministry of Commerce. Based on Council of Ministers Resolution 785
  (28/12/1441H), itself based on Shura Council Resolution 50/289 (22/11/1441H). **Corrects the
  initial task-briefing's unverifiable premise** of "M/162, 21/11/1441H" — no such decree
  matches any source; the briefing's date likely conflated the Shura Council Resolution date.
  **Replaces** the prior anti-concealment law, Royal Decree M/22 (4/5/1425H). No amendments
  found; nezams.com's own metadata explicitly confirms none. **DISTINCT VERIFICATION TIER —
  the weakest-sourced tier in this corpus to date:** `laws.boe.gov.sa` was **completely
  unreachable via all three prescribed methods** (direct WebFetch 503/timeout; `r.jina.ai`
  proxy 422 navigation timeout; direct Wayback Machine fetch via curl, TLS connection reset —
  apparently network-policy-blocked in this environment; a further `r.jina.ai`-proxied Wayback
  attempt was itself blocked by jina's own anti-abuse policy). In the total absence of a
  reachable primary source, this track rests on **triple independent Arabic secondary source
  agreement**: a professionally compiled, footnoted edition hosted at qadha.org.sa (authored
  by a named Ministry of Commerce assistant legal counsel, published by the Saudi Judicial
  Scientific Association) for full verbatim text, cross-verified against nezams.com and
  alrashidi.law for decree metadata and structure. **No byte-level primary-source confirmation
  was achieved** — a genuine, explicitly documented sourcing limitation, not silently upgraded
  to a higher-confidence tier. **⚠ Additional flagged items:** `laws.boe.gov.sa` hosts two
  GUID-distinct records both titled generically "نظام مكافحة التستر" (the superseded 1425H law
  and the current 1442H law) — a collision risk for future researchers; marginal
  compiler-added cross-reference codes in the qadha.org.sa source were excluded as editorial
  apparatus, not statutory text. A companion Implementing Regulation exists (Ministerial
  Resolution 00479, 20/7/1442H) but is **not extracted** in this track, nor are related
  subordinate instruments referenced by Articles 6, 13, and 18 (status-correction regulation
  for the prior law's violators; exemption rules; whistleblower reward rules). Track under
  `sources/anti_concealment/law/`. Validate: `make anti-concealment-law-track-validate`.

## نظام مراقبة شركات التأمين التعاوني — Cooperative Insurance Companies Control Law (2/6/1424هـ) — DISTINCT TIER, MISA PDF x NEZAMS, BOE/WAYBACK UNREACHABLE

- **Cooperative Insurance Companies Control Law (Royal Decree M/32, 2/6/1424H) verified +
  LLM-ready.** **نظام مراقبة شركات التأمين التعاوني** — **25 records**, **no chapter (فصل)
  divisions** — **17 اصلية / 8 معدلة**. Administering authority: Saudi Central Bank
  (functionally transferred to a newly-created **Insurance Authority**, هيئة التأمين, in late
  2023 via Cabinet Resolution 85/1445H — but **no evidence found** of a Royal Decree
  textually amending this Law's articles to reflect that transfer, flagged not assumed).
  **Two amendment waves**: Royal Decree M/30 (27/5/1434H, touching article 22 and
  first-amending article 20) and Royal Decree M/12 (23/1/1443H, touching articles 2, 3, 6,
  18, 19, 21, and second-amending article 20). **DISTINCT VERIFICATION TIER:**
  `laws.boe.gov.sa` (503/422) and the Wayback Machine (TLS connection reset) were **both
  unreachable** this pass; current-consolidated text instead rests on `misa.gov.sa`'s
  official bilingual PDF (explicitly headering all three decrees), cross-verified
  article-by-article against nezams.com. **⚠ Flagged institutional-name divergence:** for
  the 17 unamended articles, this track follows nezams.com's wording (pre-2020 regulator
  name «مؤسسة النقد العربي السعودي») rather than misa.gov.sa's current-name reproduction —
  no source documents a formal per-article amendment renaming the institution in these
  specific articles. **⚠ IMPORTANT LIMITATION:** pre-amendment original text was **NOT
  transcribed into this build for any of the 8 amended articles** — for 6 of them (2, 3, 6,
  18, 19, 20) the research pass located but did not retain the original wording; for 2 of
  them (21, 22) no original text was even located. **No `original_XXXXh_text` fields are
  included** — a documented gap, not a fabrication, and a candidate for a dedicated
  follow-up pass. A companion Implementing Regulation exists (Ministerial Resolution 596/1,
  11/3/1425H) but is **not extracted** in this track. Track under
  `sources/insurance_control/law/`. Validate: `make insurance-control-law-track-validate`.

## نظام التجارة الإلكترونية — E-Commerce Law (7/11/1440هـ) — DISTINCT TIER, BOE WAYBACK x NEZAMS

- **E-Commerce Law (Royal Decree M/126, 7/11/1440H) verified + LLM-ready.**
  **نظام التجارة الإلكترونية** — **26 records**, all **اصلية** — **no chapter (فصل)
  divisions** (the sole occurrence of the word فصل is substantive text inside Article 22,
  "الفصل في المنازعات" / "adjudicate disputes", not a structural heading). Administering
  authority: Ministry of Commerce. Based on Council of Ministers Resolution 628
  (6/11/1440H), following Shura Council Resolutions 189/47 (19/10/1439H) and 144/39
  (1/9/1440H). A fresh, still-unamended 2019 law — confirmed via the BOE portal's own
  per-article amendment/repeal CSS-class markers being absent from every article, and
  nezams.com's explicit "لم يجرِ عليه تعديل" (no amendment) statement. **DISTINCT
  VERIFICATION TIER:** `laws.boe.gov.sa`'s live portal was unreachable this pass; full text
  instead rests on a **single successful Wayback Machine snapshot** of the BOE portal
  (fetched directly, not via `r.jina.ai` or WebFetch, neither of which can reliably reach
  `archive.org`) — a second, differently-dated snapshot for byte-identity cross-checking
  could not be fetched due to repeated network-level connection resets against
  `archive.org`, a lighter cross-verification than some other tracks' two-snapshot
  pattern, flagged as a candidate for a follow-up confirmation pass. Cross-verified against
  nezams.com. **⚠ Two flagged discrepancies**, both confirmed genuine source-text features
  rather than artifacts: Article 1's own defined terms still name the ministry "وزارة
  التجارة والاستثمار" (the pre-reorganization name, since the Law itself has never been
  amended); Article 22 has no terminal punctuation in the official BOE source markup
  itself. A companion Implementing Regulation is confirmed to exist (Ministerial
  Resolution 200/1441H, 19/5/1441H) but is **not extracted** in this track. Track under
  `sources/ecommerce/law/`. Validate: `make ecommerce-law-track-validate`.

## نظام ضريبة القيمة المضافة — Value Added Tax Law (2/11/1438هـ) — DISTINCT TIER, ZATCA PDF x BOE PORTAL

- **Value Added Tax Law (Royal Decree M/113, 2/11/1438H) verified + LLM-ready.**
  **نظام ضريبة القيمة المضافة** — **53 records** across **18 chapters (فصول)** — **51
  اصلية / 2 معدلة**. Administering authority: Zakat, Tax and Customs Authority (ZATCA,
  formerly GAZT). Based on Council of Ministers Resolution 654 (1/11/1438H), following
  Shura Council Resolution 128/45 (18/10/1438H). **Article 2 amended** by Royal Order
  A/638 (15/10/1441H) — raised the VAT rate from **5% to 15%**, effective 1 July 2020.
  **Article 49 amended** by Royal Decree M/52 (28/4/1441H) — replaced a reference to
  "الجهة القضائية المختصة" with a reference to the newly-created Tax Violations and
  Disputes Resolution Committees (whose own rules of procedure were later superseded by
  Royal Order 25711, 8/4/1445H). **DISTINCT VERIFICATION TIER:** current-consolidated
  text rests on **two independent official sources in agreement** — ZATCA's own official
  consolidated PDF (source of the two amended articles' current text, with explicit
  amendment footnotes) cross-verified against `laws.boe.gov.sa` (reached via the
  `r.jina.ai` proxy after the live page returned HTTP 503) for all other articles and for
  decree/preamble metadata; the Wayback Machine was unreachable this pass (TLS connection
  reset) and was not part of this track's verification chain. **⚠ IMPORTANT
  LIMITATION:** the BOE portal's default view is **NOT automatically consolidated with
  amendments** — for **both** amended articles the BOE-portal rendering showed
  pre-amendment or truncated/anomalous text, confirming ZATCA's PDF as the authoritative
  current-text source for those two articles; **neither article's full pre-amendment
  original text was captured** to primary-source confidence this pass, so **no
  `original_1438h_text` fields are included** for either — a documented gap, not a
  fabrication, flagged as a candidate for a dedicated follow-up pass. Additional flagged
  discrepancies: a publication-date conflict between BOE and eastlaws.com (~16 months
  apart); an isolated Gregorian-date-conversion anomaly in ZATCA's own Implementing
  Regulation PDF; Article 26's chapter placement under Chapter 10 despite its subject
  matter reading more naturally with Chapter 11, preserved as found. A companion
  Implementing Regulation is confirmed to exist (ZATCA Board Decision 3839, 14
  Dhul-Hijjah 1438H, amended at least 12 times through 2024/2025) but is **not
  extracted** in this track. Track under `sources/vat/law/`. Validate:
  `make vat-law-track-validate`.

## نظام الامتياز التجاري — Franchise Law (9/2/1441هـ) — DISTINCT TIER, BOE PROXY x QANONIAH SPOT

- **Franchise Law (Royal Decree M/22, 9/2/1441H) verified + LLM-ready.**
  **نظام الامتياز التجاري** — **27 records** across **11 chapters (فصول)** — **all
  اصلية**, a fresh, still-unamended 2019 law. Task premise originally assumed decree
  date 21/2/1441H — **corrected to 9/2/1441H** per BOE. This decree number (M/22)
  **collides with, but is entirely unrelated to**, the superseded original
  Anti-Concealment Law's own decree of the same number dated 4/5/1425H, already in
  this corpus — disambiguated by content, not by decree number alone, since Saudi
  royal decree numbering resets periodically. **DISTINCT VERIFICATION TIER:**
  `laws.boe.gov.sa` (the primary official source) was reached this pass via the
  `r.jina.ai` proxy after a direct WebFetch attempt returned HTTP 503, supplying the
  full verbatim text of all 27 articles and the decree preamble. Independent
  cross-verification against qanoniah.com was achieved only as a **spot check** on
  Articles 1, 2, 4, and 5 (that source's own rendering was incomplete/paginated,
  skipping Article 3 and cutting off mid-Chapter 4) — Articles 3 and 6-27 rest on the
  BOE primary source alone this pass; the Wayback Machine had zero snapshots for this
  law's BOE URL. Flagged discrepancies: a 2-day publication-date mismatch between BOE
  metadata and qanoniah.com's Umm Al-Qura gazette table; Article 4's BOE-rendered
  heading carries a stray trailing colon treated as a page-rendering artifact, not
  reproduced. **NON-TEXTUAL CARVE-OUT (not an amendment):** a Council of Ministers
  decision dated 13/1/2026G approved a discretionary carve-out disapplying some
  unspecified requirement(s) of this Law to certain franchisor/franchisee categories,
  exercised under an enabling clause already present in the original 1441H decree
  text — this is explicitly **NOT a textual amendment** to any article, no article is
  marked معدلة because of it, and its exact substantive scope could not be recovered;
  documented as an unresolved discrepancy rather than guessed at. A companion
  Implementing Regulation is confirmed to exist (Ministerial Decision 591, 18/9/1441H,
  16 articles) but is **not extracted** in this track. Track under
  `sources/franchise/law/`. Validate: `make franchise-law-track-validate`.

## نظام الطيران المدني — Civil Aviation Law (18/7/1426هـ) — DISTINCT TIER, NEZAMS x RAKADVOCATE SPOT

- **Civil Aviation Law (Royal Decree M/44, 18/7/1426H) verified + LLM-ready.**
  **نظام الطيران المدني** — **180 records** across **14 أبواب** (several with
  sub-فصول) — **168 اصلية / 12 معدلة**. Based on Council of Ministers Resolution 185
  and Shura Council Resolution 101/79. Task premise originally assumed decree date
  19/7/1426H — **corrected to 18/7/1426H** per primary sources. 12 amended articles
  (1 §6, 32 §1, 46, 107, 108, 109, 112, 114, 115, 116, 118, 119) — current/integrated
  text used in `text` with full `history` entries; `original_1426h_text` included
  only where the source actually captured verbatim pre-amendment wording (11 of 12 —
  omitted for Article 46, where only the substituted phrase, not the full original
  paragraph, was quotable; never fabricated). **DISTINCT VERIFICATION TIER:**
  `laws.boe.gov.sa`'s live portal was unreachable this research pass (HTTP 503 via
  WebFetch, connection-reset via direct curl, HTTP 401 "bad IP reputation" via the
  `r.jina.ai` proxy; the Wayback Machine was not attempted this pass). Full text
  instead rests on a direct fetch of nezams.com (2.1MB HTML parsed against its
  structured per-article markup for all 180 articles), **spot-checked — not fully
  cross-verified article-by-article** — against rakadvocate.blogspot.com, which
  matched verbatim only for Article 1 and Article 180 (the sole two spot-checked) —
  a lighter verification tier than most tracks in this corpus, flagged as a candidate
  for a follow-up confirmation pass against BOE once reachable. Flagged discrepancies
  (9 total): an apparent stray/mislabeled "الفصل الثاني: صلاحيات وواجبات السلطات"
  sub-chapter heading found immediately before Article 149, content-wise reading as a
  continuation of the preceding sub-chapter — transcribed verbatim as encountered in
  `section_ar` while `chapter_structure` reflects the content-correct title, the
  deliberate divergence documenting the anomaly rather than silently resolving it;
  Council of Ministers Resolution 158/1445H (the "المكتب"→"المركز" institutional
  rename across Articles 108/109/112/114-116/118/119, and the full re-issuance of
  Article 107 creating المركز الوطني لسلامة النقل) confirmed via only one primary
  source, not independently corroborated; Article 107's current text uses Eastern
  Arabic-Indic numerals, preserved verbatim; a source typo in Article 107 preserved
  verbatim, not corrected; no single consolidated Implementing Regulation exists —
  multiple Civil Aviation Regulations (CARs) are issued under Article 179's authority
  with no single consolidating date, none extracted in this track. Track under
  `sources/civil_aviation/law/`. Validate: `make civil-aviation-law-track-validate`.

## نظام مكافحة المخدرات والمؤثرات العقلية — Anti-Narcotics Law (8/7/1426هـ) — DISTINCT TIER, BOE PROXY x NEZAMS x QADHA REFERENCE

- **Anti-Narcotics and Psychotropic Substances Control Law (Royal Decree M/39, 8/7/1426H)
  verified + LLM-ready.** **نظام مكافحة المخدرات والمؤثرات العقلية** — **74 records**,
  all **اصلية**. Approving Council of Ministers Resolution 152 (12/6/1426H), following
  Shura Council Resolution 51/50 (7/11/1425H). Repeals the prior narcotics-trafficking
  law issued by Supreme Order 3318 (9/4/1353H). No amending instrument to the article
  text itself was found since 1426H (only the annexed substance schedules were
  administratively updated under Article 70's delegated authority — not a textual
  amendment to any article). **NO formal الباب/الفصل structure exists** — confirmed by
  a full-text grep of a combined law+regulation reference PDF finding zero باب/فصل
  markers; the 74 sequential articles instead carry unnumbered topical headers, modeled
  as `chapter_structure` entries with title + article range only. **DISTINCT
  VERIFICATION TIER:** the official BOE portal returned HTTP 503 on direct WebFetch; the
  `r.jina.ai` proxy successfully retrieved the complete text, cross-verified word-for-word
  against nezams.com (full agreement except one variant — see below), and additionally
  triple-verified for the highest-stakes penalty articles (37, the death-penalty article,
  plus 38, 39, 40, 49) against qadha.org.sa's published reference book (ISBN
  978-603-92112-4-2, 1445H). A Wayback Machine cross-check could not be completed
  (sandbox egress policy blocked archive.org access) — a documented gap, mitigated by
  the two other independently-sourced full-text copies. Flagged discrepancies: **Article
  42** paragraph 1 has a textual variant between BOE's coherent "الدعوى" and nezams.com's
  apparent OCR/typo "الدعوة" — the BOE reading was adopted as authoritative, discrepancy
  documented; **Article 35's** official heading reads "المادة الخامسة الثلاثون" (missing
  the conjunctive و used in every other analogous ordinal), identically present in both
  primary sources and preserved verbatim rather than silently corrected; an AI-search
  claim of a "الباب الثاني/الفصل الأول" structure was investigated and found
  unsubstantiated; unverified AI-search-only claims about amendments to a separate,
  related National Committee for Combating Drugs organizing regulation are explicitly
  out of scope and do not amend this law's articles; Article 68's "مؤسسة النقد العربي
  السعودي" (SAMA's pre-2020 name) and Articles 12-27's "وزارة الصحة" are preserved
  verbatim as enacted, a real-world regulatory-evolution note. A companion Implementing
  Regulation is confirmed to exist (Council of Ministers Resolution 201, 10/6/1431H) via
  4 corroborating sources but not to verbatim-text standard — **not extracted** in this
  track. Track under `sources/anti_narcotics/law/`. Validate:
  `make anti-narcotics-law-track-validate`.

## نظام المرور — Traffic Law (26/10/1428هـ) — MIXED-CONFIDENCE TIER, BOE CONFIRMED STALE x NEZAMS PATTERN

- **Traffic Law (Royal Decree M/85, 26/10/1428H) verified + LLM-ready.** **نظام
  المرور** — **86 records** (85 numbered articles + Article 50 مكرر, added by Royal
  Decree M/115, 5/12/1439H) across **8 أبواب** — **52 اصلية / 32 معدلة / 1 ملغاة
  / 1 مضافة**. Approving Council of Ministers Decision 315 (24/10/1428H), following
  Royal Order A/175 (17/10/1428H); replaces the prior نظام المرور (Royal Decree
  M/49, 6/11/1391H). Task premise originally assumed "M/17 dated 26/6/1428H" —
  **corrected to M/85, 26/10/1428H**. **Article 71** repealed by Council of
  Ministers Decision 474 (7/7/1446H), ratified by Royal Decree M/140 (12/7/1446H)
  — pre-repeal text preserved per this corpus's never-delete-repealed-articles
  policy. **THIS IS THE CORPUS'S MOST COMPLEX VERIFICATION CASE — required TWO
  independent research passes** because of a genuine, unresolved discrepancy
  between the official BOE portal and nezams.com for roughly a third of the law's
  articles. Across both passes, BOE's live portal was confirmed **GENUINELY
  STALE for this law — not a proxy/rendering artifact** — via four
  independently-verified data points: Article 71's repeal (confirmed via direct
  Umm Al-Qura gazette text of Royal Decree M/140), Article 74's 2025 rewrite
  (confirmed via SPA and MOI statements), Article 2's added definition #44
  "هيكل المركبة", and the Table 2 violation-schedule item-16 wording. nezams.com's
  current text is therefore used as governing text where it diverges from BOE's
  stale text, but this is **PATTERN-BASED confidence, not per-article gazette
  proof**: **every article record carries a `verification_tier` field** —
  `PRIMARY_INDEPENDENTLY_CONFIRMED` (67 records: all 52 اصلية articles, Article
  71's repeal, and 14 amended articles independently confirmed beyond
  nezams.com) vs `SECONDARY_SOURCE_ONLY_BOE_KNOWN_STALE` (19 records: 18 amended
  articles plus Article 50 مكرر resting on nezams.com's pattern-reliability
  alone) — this per-article granularity is **deliberately not smoothed over** by
  the track-level STATUS constant. `original_1428h_text` is populated for only
  **8 articles** (1, 5, 23, 27, 69, 70, 73, 78) where a report captured verbatim
  pre-amendment wording; omitted for the other 24 amended articles, documented
  as gaps rather than fabricated. **11 flagged discrepancies**, most notably:
  the Table 2 item-16 numbering conflict (BOE's item 16 reads "expired driving
  license"; M/140's own gazette-confirmed addition reads "expired
  vehicle-registration license" — the fate of the old slot is unresolved);
  Article 2's 43-vs-44 defined-term count; 17 amended articles where BOE and
  nezams.com show identical resulting text despite a confirmed amending
  instrument (no determinable wording delta). Annexed violation tables (1-8)
  and fee schedules are referenced by article text but **not separately
  modeled**. A companion Implementing Regulation (Ministerial Decision 7019,
  3/7/1429H, possibly reissued via Ministerial Decision 2249/1441H, unconfirmed)
  is **not extracted** in this track. Track under `sources/traffic/law/`.
  Validate: `make traffic-law-track-validate`.

## نظام البيئة — Environmental Law (19/11/1441هـ) — STRONG TRIPLE-SOURCE TIER, BOE WAYBACK x GREEN.ORG.SA PDF x NEZAMS

- **Environmental Law (Royal Decree M/165, 19/11/1441H) verified + LLM-ready.**
  **نظام البيئة** — **49 records** across **9 فصول** (this law has NO أبواب/Parts
  tier) — **48 اصلية / 1 معدلة**. Approving Council of Ministers Decision 729
  (16/11/1441H). Administered by the Ministry of Environment, Water and
  Agriculture (MEWA), the General Authority of Meteorology and Environmental
  Protection, the Saudi Wildlife Authority, and the National Centers for the
  Environment Sector. **Repeals several prior instruments**, including the older
  "النظام العام للبيئة" (Royal Decree M/34, 28/7/1422H) — with a narrow
  carve-over: that older law's waste-related provisions remain in force until
  dedicated new waste-specific rules are issued; the old M/34 law itself is not
  modeled in this corpus. **STRONG TRIPLE-SOURCE VERIFICATION TIER:**
  `laws.boe.gov.sa`'s live portal was unreachable this pass (HTTP 503 direct,
  HTTP 422 via `r.jina.ai`); BOE's own content was instead recovered via the
  Wayback Machine (15 October 2025 snapshot, cross-checked against 24 September
  2024), and independently cross-verified against two further
  independently-hosted full-text copies — a PDF hosted at green.org.sa and
  nezams.com. **All 49 articles matched verbatim across all three sources
  except one flagged point:** Article 1's definition of "الجهة المختصة"
  (Competent Authority), where BOE's OWN official per-article amendment-log
  states current wording differs from BOE's OWN main running law-text body —
  a genuine self-contradiction in BOE's own official data, persistent across
  two Wayback snapshots over a year apart. This build treats the amendment
  (Council of Ministers Decision 406, 14/5/1445H, adding "المؤسسة العامة
  للمحافظة على الشعب المرجانية والسلاحف في البحر الأحمر" to the definition)
  as operative, following the same reasoning precedent established for the
  **Traffic Law track's "BOE portal lags behind confirmed amendments"**
  situations, further corroborated by qanoonsa.com independently displaying
  the amended definition. The pre-amendment wording is preserved verbatim as
  `original_1441h_text` — flagged as warranting dedicated human legal-review
  confirmation given it rests on BOE's internal self-contradiction plus one
  secondary corroboration, not a full independent gazette-text confirmation.
  Additional notes: the multiple topical Implementing Regulations (no single
  consolidated instrument) are listed indicatively only, not independently
  verified, and **not extracted** in this track; monetary figures use
  Arabic-style period thousand-separators (e.g. "(20.000.000) عشرين مليون
  ريال"), preserved verbatim rather than reformatted; no official English
  translation exists per BOE's own site. Track under `sources/environmental/law/`.
  Validate: `make environmental-law-track-validate`.

## Strict QA gate

- **`make qa-gate`** — one command, everything must pass: **[1]** every
  `scripts/validate_*.py` in the repository (191 today — discovered from the filesystem, so any new
  validator automatically joins the gate; exclusions require a written reason in the script's
  `EXCLUDED` dict, currently empty); **[2]** generator idempotence — 118 deterministic generators
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
