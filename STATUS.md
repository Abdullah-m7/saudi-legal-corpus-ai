# STATUS

Single source of truth for the current repository state. When counts or
completion change, update this file.

**Identity:** a multilingual, LLM-ready, official-source-based Saudi legal
corpus for AI. The **official Arabic source governs**; English and Chinese are
**reference layers**.

> **Scope note:** everything below through "Corpus-value features" documents
> the **Saudi Companies Law's** own build in narrative detail (it was the
> first implemented law profile, and remains the only track with full
> Arabic + English + Chinese layers), plus the first ~193 of the corpus's
> now-291 total Arabic-only tracks, each with its own prose write-up below.
> Tracks added after that point are **not** individually narrated here — for
> the current, authoritative count and per-track detail (status, record
> counts, source authority, data/validator paths) for **all 291 tracks**,
> use [`data/corpus_registry/corpus_registry.json`](data/corpus_registry/corpus_registry.json)
> instead of any specific number written in this file's prose, which reflects
> the count at the time each section was last written and is not kept in
> sync on every track-add commit. See `START_HERE.md` for the current
> top-level picture and `reports/coverage_gap_map/` for what's not built yet.

---

## Repository name

- **Current name:** `saudi-legal-corpus-ai` — **former name:**
  `saudi-companies-law-ar-zh-llm`. The GitHub rename is performed manually; see
  [`REPOSITORY_RENAME.md`](REPOSITORY_RENAME.md).

## Baseline

- **Baseline `main` commit:** `0a2e5c3e6457009ddf1d0ba2fb4d669091317ced`
- **First implemented law profile:** Saudi Companies Law (M/132, 1443H) — the
  **first** implemented law profile, and the only one with full Arabic +
  English + Chinese layers. **Not** the whole project identity: 290 further
  Arabic-only tracks exist alongside it (see the scope note above).

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
  + Sharia Procedure regulation 637 + Law of Criminal Procedure 222 + Criminal Procedure regulation 181 + Law of Enforcement 98 + Enforcement regulation 273 + Law of the Judiciary 85 + Law of the Board of Grievances 26 + Code of Law Practice 56 + Code of Law Practice regulation 90 + Commercial Courts Law 96 + Commercial Courts Law regulation 281 + Bankruptcy Law 231 + Bankruptcy Law regulation 98 + Bankruptcy case rules 24 + Judicial Costs Law 23 + Judicial Costs regulation 17 + Arbitration Law 58 + Arbitration regulation 19 + Commercial Papers Law 121 + Commercial Register Law 29 + Trade Names Law 23 + Commercial Agencies Law 6 + Chambers of Commerce Law 66 + Commercial Books Law 16 + Anti-Money Laundering Law 52 + Notarization Law 57 + Notarization Regulation 31 + Real Estate Registration Law 40 + Real Estate Registration Regulation 51 + Registered Real Estate Mortgage Law 46 + Real Estate Finance Law 15 + Real Estate Unit Ownership Law 33 + Real Estate Unit Ownership Regulation 41 + Non-Saudi Real Estate Ownership Law 15 + Municipal Real Estate Disposal Law 6 + Municipal Real Estate Disposal Regulation 35 + GCC Citizens Ownership Regulation 6 + Combating Terrorism Crimes and Financing 99 + its Implementing Regulation 28 + Juveniles Law 24 + its Implementing Regulation 13 + Whistleblower, Witness, Expert and Victim Protection Law 37 + Judicial Inspection Regulation 68 + Regulation on the Division of Jointly-Owned Property 48 + Professional Conduct Rules for Lawyers 47 + Regulation Organizing the Work of Judicial Assistants 35 + Rules for the Work of Conciliation Offices and its Procedures 29 + Rules Organizing Cross-Border Insolvency Procedures 23 + Regulation on Judicial Documents 23 + Rules for Determining the Fees of Experts and Trustees under the Bankruptcy Law 20 + Regulation on Enforcement Service Providers 18 + Alimony Fund Regulation 17 + Executive Working Mechanism for the Law of the Judiciary and the Law of the Board of Grievances 15 + Regulation of the Center for Assignment (Referral) and Liquidation 15 + Regulation of the Conciliation Center 10 + Medical Reports Regulation 13 + Regulation on the Marriage of a Saudi to a Non-Saudi 11 + Mechanism for a Defendant in Major/Serious Crimes to Seek Legal Counsel at the State's Expense 11 + Controls for the Lessor's Repossession of Movable Assets 7 + Procedural Guide for the Electronic Litigation Service 5 + Organizational Guide for the Judicial Training Center 18 + Executive Regulation for Methods of Objecting to Judgments 62 + Law on Expropriation of Real Estate for Public Interest and Temporary Seizure of Real Estate 39 + Arrangements for Hearing Claims to Prove Marriage Contracts Concluded Without Required Official Permission 10 + Real Estate Transaction Tax Law 20 + Standards and Quality Law Implementing Regulation 23 + Rights of Persons with Disabilities Law Implementing Regulation 45 + Anti-Smoking Law Implementing Regulation 17 + General Education Law 68 + Credit Information Law 17 + Real Estate Brokerage Law 24 + State Revenue Law 32 + ETEC organizing statute 18 + E-Invoicing Regulation 7 + Regulation on Transfer of Personal Data Outside the Kingdom 9 + SDAIA Organizational Arrangements 16* Trade Names Regulation 19 + Commercial Agencies Regulation 49 + Accounting and Auditing Regulation 15 + Commercial Register Regulation 21 + Real Estate Brokerage Regulation 27 + Non-Saudi Real Estate Ownership Implementing Regulation 15 + Anti-Commercial Fraud Regulation 19 + Real Estate Transaction Tax Regulation 15 + Anti-Narcotics Implementing Regulation 40 + Anti-Concealment Implementing Regulation 18 + Privatization Implementing Regulation 169 + Chambers of Commerce Implementing Regulation 63 + State Revenue Implementing Regulation 65 + Weapons and Ammunition Implementing Regulation 19 + Engineering Practice Implementing Regulation 18 + Allegiance Commission Implementing Regulation 18 + Social Insurance Implementing Regulation 107 + Saudi Council of Engineers Implementing Regulation 32 + Child Protection Implementing Regulation 25 + Whistleblower Implementing Regulation 12 + Legacy Social Insurance Implementing Regulations 170 + Protection from Abuse Implementing Regulation 14 + Healthcare Professions Implementing Regulation 30 + Shura Council Internal Regulation 34 + Civil Service Implementing Regulation 261 + Associations and Civil Institutions Implementing Regulation 129 + Electronic Transactions Implementing Regulation 25 + Electricity Law Implementing Regulations 92 + Ship Registration Regulation 49 + Agriculture Implementing Regulation 271 + Civil Defense Subordinate Regulations 21 + Premium Residency Implementing Regulation 13 + Water Law Implementing Regulation (MEWA) 156 + Press and Publications Implementing Regulation 99 + Building Code Application Implementing Regulation 30 + Telecommunications Implementing Regulation 108 + Credit Information Law Implementing Regulation 55 + Payment Systems and Services Law Implementing Regulation 133 + Rules for the Application of the Banking Control Law 31 + Finance Companies Control Law Implementing Regulation 106 + Finance Lease Law Implementing Regulation 32 + Cooperative Societies Law Implementing Regulation 55 + Law of Enforcement before the Board of Grievances 37 + Law of Public Prosecution 30 + Elderly Rights and Care Law 23 + Elderly Rights and Care Law Implementing Regulation 8 + Private Schools Regulation 24 + Foreign Schools Regulation 21 + Postal Law 20 + CMA Corporate Governance Regulation 95 + TVTC Organizational Statute 13 + Waste Management Law 38 + Fisheries Law 13 + Debt Collection Regulation 11 + Statute of the Insurance Authority 15 + Rules for Regulating Buy-Now-Pay-Later (BNPL) Companies 31 + Off-Plan Sale and Lease of Real Estate Projects Law ("WAFI") 30 + Contractors Classification Law 19 + Real Estate Contributions Law 38 + Certified/Accredited Valuers Law 45 + White Land and Vacant Properties Fees Law 15 + Frequency Spectrum Regulations for Radio Services and Applications (General Framework) 15 + Mental Health Care Law 30 + Human Organ Donation Law 27 + Private Healthcare Institutions Law 35 + High-Risk Professions Work Organization Regulation 19 + OSH Service Providers Licensing/Accreditation Regulation 38 + Statute of the General Authority for Real Estate (REGA) 16 + Implementing Regulation of the Off-Plan Sale/Lease of Real Estate Projects Law ("WAFI") 49 + Implementing Regulation of the Real Estate Finance Law 31 + Implementing Regulation of the Real Estate Contributions Law 40 + Statutory Provisions Regulating the Landlord-Tenant Relationship 12 + Regulatory Bylaw on Real Estate Marketing and Advertising 12 + Regulation of Real Estate Auctions 12 + The Petroleum and Petrochemical Materials Law 22 + The Dry Gas and LPG Distribution Law 21 + The Energy Supplies System 12 + Implementing Regulation of the Mining Investment Law 166 + The Pharmaceutical and Herbal Establishments Law 42 + System for the Management of Seized/Confiscated Funds in AML/CFT Crimes 15 + Rules for Detecting and Investigating Cybersecurity Violations 9 + Rules Organizing the Reporting of Cybersecurity Violations 8 + Organizational Statute of the Communications, Space and Technology Commission (CST) 19 + The Saudi Arabian Railway Law 50 + Implementing Regulation of the Railway Law 91 + The Saudi Arabian Road Transport Law 34 + Organizational Statute of the General Authority of Civil Aviation (GACA) 15 + Organizing Statute of the General Authority for Transport (TGA) 16 + Organizational Statute of the General Authority for Ports (Mawani) 20 + Law of Service Providers for External Hajj Pilgrims 24 + Passenger Rights Protection Regulation 30**)
  with counts, paths, statuses, language layers,
  boundaries, and validation targets. **291 tracks; primary Arabic governing 15858; reference 614; registry-counted
  16753.** PDPL and Investment Arabic tracks are **verified against official
  published text** (SDAIA / MISA). The registry also records the unified retrieval
  index (15689 records) as a projection (not added to totals). See
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
  Personal Status 293 (law 252 + regulation 41) + Sharia Procedure 880 (law 243 + regulation 637) + Criminal Procedure 403 (law 222 + regulation 181) + Enforcement 371 (law 98 + regulation 273) + Judiciary 85 + Board of Grievances 26 + Law Practice 146 (law 56 + regulation 90) + Commercial Courts 377 (law 96 + regulation 281) + Bankruptcy 353 (law 231 + regulation 98 + case rules 24) + Judicial Costs 40 (law 23 + regulation 17) + Arbitration 77 (law 58 + regulation 19) + Commercial Papers 121 (law) + Commercial Register 29 (law) + Trade Names 23 (law) + Commercial Agencies 6 (law) + Chambers of Commerce 66 (law) + Commercial Books 16 (law) + Anti-Money Laundering 52 (law) + Notarization 88 (law 57 + regulation 31) + Real Estate Registration 91 (law 40 + regulation 51) + Real Estate Mortgage 46 (law) + Real Estate Finance 15 (law) + Real Estate Units 74 (law 33 + regulation 41) + Non-Saudi Ownership 15 (law) + Municipal Real Estate 41 (law 6 + regulation 35) + GCC Ownership 6 (law) + Counter-Terrorism 127 (law 99 + regulation 28) + Juveniles 37 (law 24 + regulation 13) + Whistleblower Protection Law 37 (law) + Judicial Inspection Regulation 68 (regulation) + Qismah Regulation 48 (regulation) + Professional Conduct Rules for Lawyers 47 (regulation) + Judicial Assistants Regulation 35 (regulation) + Conciliation Offices Rules 29 (regulation) + Cross-Border Insolvency Procedures Rules 23 (regulation) + Judicial Documents Regulation 23 (regulation) + Bankruptcy Fees Rules 20 (regulation) + Enforcement Service Providers Regulation 18 (regulation) + Alimony Fund Regulation 17 (regulation) + Executive Working Mechanism for the Law of the Judiciary and the Law of the Board of Grievances 15 (mechanism) + Regulation of the Center for Assignment (Referral) and Liquidation 15 (regulation) + Regulation of the Conciliation Center 10 (regulation) + Medical Reports Regulation 13 (regulation) + Regulation on the Marriage of a Saudi to a Non-Saudi 11 (regulation) + Mechanism for a Defendant in Major/Serious Crimes to Seek Legal Counsel at the State's Expense 11 (regulation) + Controls for the Lessor's Repossession of Movable Assets 7 (regulation) + Procedural Guide for the Electronic Litigation Service 5 (regulation) + Organizational Guide for the Judicial Training Center 18 (guide) + Executive Regulation for Methods of Objecting to Judgments 62 (regulation) + Law on Expropriation of Real Estate for Public Interest and Temporary Seizure of Real Estate 39 (law) + Arrangements for Hearing Claims to Prove Marriage Contracts Concluded Without Required Official Permission 10 (regulation) + Anti-Bribery Law 25 (law, DISTINCT lower-confidence verification tier) + Basic Law of Governance 83 (law, DISTINCT tier: BOE portal x WIPO Lex spot-checked) + Anti-Cyber Crime Law 16 (law, DISTINCT tier: BOE x WIPO Lex/CITC x MOF exhaustive triple-source) + Anti-Harassment Law 8 (law, DISTINCT mixed tier: BOE x secondary press convergence for art 6 amendment) + Anti-Trafficking in Persons Law 17 (law, DISTINCT tier: BOE Wayback snapshot x UNODC English substance-verified) + Council of Ministers Law 32 (law, DISTINCT tier: dual independent Arabic secondary sources, BOE unreachable) + Regions/Provinces Law 41 (law, DISTINCT tier: dual independent Arabic secondary sources, this law's BOE page unreachable) + Electronic Transactions Law 31 (law, DISTINCT tier: single primary BOE/CoM translation-bureau PDF, WIPO Lex structural cross-check) + Allegiance Commission Law 25 (law, DISTINCT tier: triple independent Arabic secondary sources, BOE page unreachable) + Shura Council Law 30 (law, MIXED tier: triple Arabic secondary sources + SPA primary source for art 3) + Copyright Law 28 (law, DISTINCT tier: qadha.org.sa compiled text x WIPO Lex structural cross-check; superseded 2026-08-01) + Telecommunications and Information Technology Act 41 (law, DISTINCT tier: BOE portal primary source, MCIT PDF cross-check; fresh replacement law, all اصلية) + Saudi Central Bank Law 27 (law, DISTINCT tier: SAMA official PDF primary source, BOE Wayback archive cross-check) + Banking Control Law 26 (law, DISTINCT tier: dual independent Arabic secondary sources, BOE unreachable for raw text; art 13's 1391H amendment original wording irrecoverable) + Capital Market Law 68 (law, MIXED tier: 55 CMA-current x BOE-2003 cross-verified, 12 flagged 2003-only historical fallback for the M/16-restructured articles, 1 reconstructed) + Competition Law 28 (law, DISTINCT tier: BOE Wayback snapshot x nezams.com cross-verified word-for-word) + Payment Systems and Services Law 20 (law, DISTINCT tier: official SAMA PDF, dual OCR pass x nezams.com cross-verified word-for-word) + Mining Investment Law 64 (law, DISTINCT tier: BOE Wayback snapshot x FAOLEX structural cross-check) + Trademark Law 52 (law, DISTINCT tier: WIPO Lex primary PDF x embedded BOE status card cross-verified) + Anti-Concealment Law 20 (law, DISTINCT tier: triple Arabic secondary sources, BOE unreachable via all methods) + Cooperative Insurance Companies Control Law 25 (law, DISTINCT tier: misa.gov.sa official PDF x nezams.com, BOE and Wayback both unreachable) + E-Commerce Law 26 (law, DISTINCT tier: BOE Wayback snapshot x nezams.com cross-verified) + Value Added Tax Law 53 (law, DISTINCT tier: ZATCA official PDF x BOE portal cross-verified) + Franchise Law 27 (law, DISTINCT tier: BOE portal via r.jina.ai proxy x qanoniah.com spot cross-verified) + Civil Aviation Law 180 (law, DISTINCT tier: nezams.com primary x rakadvocate.blogspot.com spot-checked, BOE unreachable) + Anti-Narcotics and Psychotropic Substances Control Law 74 (law, DISTINCT tier: BOE via r.jina.ai proxy x nezams.com x qadha.org.sa reference book triple-verified) + Traffic Law 86 (law, MIXED-CONFIDENCE tier: BOE portal confirmed genuinely stale, nezams.com preferred with per-article verification_tier) + Environmental Law 49 (law, STRONG triple-source tier: BOE Wayback x green.org.sa PDF x nezams.com, one flagged BOE self-contradiction at Article 1) + Income Tax Law 81 (law, DISTINCT tier: BOE Wayback x ZATCA PDF x gstc.gov.sa PDF x nezams.com, Chapter 10 BOE+nezams only) + Civil Service Law 44 (law, DISTINCT tier: BOE Wayback x nezams.com full cross-verification, Article 3 repeal flagged with no fabricated replacement text) + Social Insurance Law — New System M/273 63 (law, DISTINCT tier: BOE Wayback re-fetched directly by the build agent after its research report proved paraphrased x nezams.com 5-article spot-check x qanoonsa.com structural corroboration; identical-title collision with the separately-tracked old Social Insurance Law M/33 documented) + Social Insurance Law — Old/Legacy System M/33 71 (law, DISTINCT tier: BOE Wayback x nezams.com cross-verification x Okaz/Al-Riyadh news corroboration for Article 37; Articles 10 and 37 resolved to their current reconciled text over BOE's confirmed-stale default rendering, Article 38's 2024 transitional-age text deliberately not merged in) + Zakat Collection Implementing Regulation M/1007 1445H 128 (law, SINGLE-SOURCE tier: ZATCA official PDF sole primary source, BOE unreachable, Umm Al-Qura Gazette spot-verified for 2 specific facts only; a severe lam-alef ligature PDF-extraction bug discovered and fixed during the build) + Law of Patents, Layout Designs of Integrated Circuits, Plant Varieties and Industrial Designs M/27 1425H 66 (law, DISTINCT tier: WIPO Lex M/45-consolidated text cross-verified via two OCR passes plus a native-text-layer extraction, BOE confirmed stale on two axes for this law) + GCC Unified Customs Law M/41 1423H 188 (law, SINGLE-SOURCE tier: ZATCA official consolidated PDF sole primary source shared with its Implementing Regulation, BOE unreachable; a three-pass post-build QA process caught and fixed a widespread negation-particle corruption plus glued list-marker artifacts) + Implementing Regulation of the GCC Unified Customs Law (Resolution 2748, 1423H) 36 (regulation, SINGLE-SOURCE tier, same shared source and QA process) + Anti-Commercial Fraud Law M/19 1429H 30 (law, SECONDARY-MULTI-SOURCE tier: three independently cross-verified secondary sources — nezams.com, mustsharik.com, mohamah.net — BOE confirmed unreachable at two distinct URL forms; Article 5's disputed second-amendment citation between two candidate instruments preserved rather than silently resolved) + Finance Companies Control Law M/51 1433H 41 (law, BOE-WAYBACK-PRIMARY tier: a Wayback Machine archive of the BOE portal page as primary, cross-verified against bfc.gov.sa's official PDF, OCR'd, and nezams.com's transcription with zero substantive discrepancies for the 40 original articles; the 2024 amendment's text rests on secondary sources only, flagged has_per_article_variation) + Cooperative Health Insurance Law M/10 1420H 19 (law, BOE-WAYBACK-ARCHIVE tier: a Wayback Machine snapshot of the BOE portal page cross-verified byte-for-byte against nezams.com, zero substantive discrepancies across 17 unamended articles and both states of 2 amended ones; Article 4's 1440H amendment text single-sourced, flagged has_per_article_variation) + Law of Practicing Healthcare Professions M/59 1426H 44 (law, BOE-WAYBACK-ARCHIVE tier: a Wayback Machine snapshot of the BOE portal page cross-verified against a live nezams.com fetch, 42 of 44 articles with zero differences, structurally corroborated against moh.gov.sa's own consolidated PDFs; confirmed dual-repeal of two prior 1409H/1398H laws) + Finance Lease Law M/48 1433H 28 (law, BOE-WAYBACK-ARCHIVE tier triple-verified: a Wayback Machine snapshot cross-verified against nezams.com and rulebook.sama.gov.sa's own official PDFs, agreement on all 28 articles; no predecessor-repeal clause found, a documented negative finding) + Maritime Commercial Law M/33 1440H 391 (law, BOE-WAYBACK-ARCHIVE tier triple-verified: a Wayback Machine snapshot of the BOE Arabic law page and BOE's own official English-translation PDF, both cross-verified against nezams.com, 381 of 391 articles matching exactly; Articles 316-325 resolved via the English translation after an independently-confirmed nezams.com content-duplication bug in that range; Article 391 confirms a dual repeal — partial repeal of Book Two of the same untracked 1350H Commercial Court Law already partly repealed by bankruptcy_law, and full repeal of the Ports/Harbours/Lighthouses Law M/27 1394H) + GCC Unified Anti-Dumping, Countervailing and Safeguard Measures Law M/30 1427H 17 (law, TIER_4 mixed-confidence: a Wayback Machine archive of the BOE portal page as primary (two independent snapshots ~20 months apart agree), partial structural cross-check against qistas.com for Articles 1-3 only; a major unresolved discrepancy is carried forward, not silently resolved — corroborated secondary evidence suggests a 2013 amendment, Royal Decree M/7 1434H, may have superseded and restructured this law into 15 articles, but BOE's own primary catalog page shows no trace of it) + Law of the Accounting and Auditing Profession M/59 1442H 22 (law, TIER_1: a Wayback Machine archive of the BOE portal page cross-verified against SOCPA's own official PDF and qanoonsa.com, all 17 unamended articles agreeing; confirmed repeal of the predecessor Law of Certified Public Accountants M/12 1412H; a genuinely confirmed BOE main-body staleness for 5 amended articles resolved via BOE's own changelog popup, not a reachability artifact; has_per_article_variation flagged for Article 1's further, unconfirmed 2025 amendment) + Law (Statute) of the Control and Anti-Corruption Authority (Nazaha) M/25 1446H 24 (law, TIER_2: BOE-via-Wayback two byte-identical snapshots ~15.5 months apart plus a third independent time-point via a FAOLEX mirror of the same BOE page, cross-verified against nezams.com partial and qanoonsa.com full structural review; confirmed repeal of the predecessor National Anti-Corruption Commission's organizing resolution and a partial repeal of the Civil Service Discipline Law; a critical cross-track finding flags this law's own enacting decree as amending the already-ingested anti_bribery_law's Articles 17/21 wording, not yet incorporated there, flagged for dedicated follow-up) + Law of the General Authority for Awqaf M/11 1437H 25 (law, TIER_1: a Wayback Machine archive of the BOE portal page, six independent snapshots spanning 2019-2025, cross-verified against web.awqaf.gov.sa's own scanned original signed decree and nezams.com; confirmed repeal of the predecessor Supreme Awqaf Council System; two genuinely-confirmed BOE main-body staleness anomalies on Articles 6 and 21, resolved via BOE's own amendment changelog rather than the stale main body) + Law of the Saudi Council of Engineers M/36 1423H 9 (law, TIER_1: a Wayback Machine archive of the BOE portal page, three independent snapshots spanning 2019-2025, cross-verified against the Saudi Council of Engineers' own official website saudieng.sa's own three snapshots and an Asharq Al-Awsat press aggregation; confirmed negative repeal finding, no predecessor engineering-council law; two genuinely-confirmed BOE-and-official-website main-body staleness anomalies on Articles 1 and 6, resolved via BOE's own amendment changelog rather than the stale main body; a decree-number collision with a separate, currently-in-force companion practice/licensing law sharing the identical number M/36 at a different hijri date is flagged as the strongest follow-up candidate) + Municipal Councils Law M/61 1435H 69 (law, TIER_1: a Wayback Machine archive of the BOE portal page, six independent snapshots spanning 2019-2025, zero text diffs and zero logged amendments throughout, cross-verified against the Ministry of Municipal, Rural Affairs and Housing's own official website momah.gov.sa's two independently-dated official PDFs and nezams.com; a confirmed, narrowly-scoped partial repeal of four named provisions of the predecessor Law of Municipalities and Villages M/5 1397H; a documented zero-amendment stability finding, the inverse of this corpus's recurring stale-changelog pattern; a preserved verbatim Chapter 10 heading spelling anomaly) + Law on Printed Materials and Publication (Press Law) M/32 1421H 49 (law, TIER_1: a near-live Wayback Machine snapshot of the BOE portal page, 26 Feb 2026, structurally cross-verified against the Ministry of Media's own official PDF media.gov.sa and WIPO Lex, plus nezams.com/qanoonsa.com; a currency check confirmed this law remains current over a still-unenacted comprehensive draft Media Law; a confirmed full repeal of the predecessor 1982 Press Law M/17 1402H; a genuinely confirmed BOE main-body staleness for 6 amended articles, resolved via BOE's own changelog rather than the stale main body) + Law of the Practice of Engineering Professions M/36 1438H 17 (law, TIER_1: a Wayback Machine archive of the BOE portal page, three independent snapshots spanning 2019-2026, byte-identical main-body text throughout, cross-verified against the Saudi Council of Engineers' own official website saudieng.sa's own hosted PDF and qanoonsa.com/qanoniah.com; a re-confirmed decree-number collision with saudi_engineers_law, both bearing the bare number M/36 at hijri dates ~15 years apart; a confirmed negative repeal finding, zero repeal-language matches anywhere in the text; a genuine three-way unresolved discrepancy at Article 1 resolved by ingesting BOE's own stable text rather than fabricating a merge, following the awqaf_law Article 6 precedent) + Saudi Arabian Nationality Law, Royal Will No. 8/20/5604 1374H 30 (law, TIER_2: BOE-via-Wayback three independent snapshots, live BOE unreachable, cross-checked against nezams.com and independent news corroboration -- reclassified down from the research agent's own self-reported TIER_1 since nezams.com is a secondary aggregator and the news outlets are secondary/tertiary corroboration, not a second genuinely official/primary source, following the nazaha_law precedent; confirmed full repeal of the 1357H predecessor nationality system and the separate Hejazi/Hejazi-Najdi nationality regulations at Article 28; a genuinely confirmed BOE main-body staleness for 11 amended articles resolved via BOE's own per-article changelog popups, a clean-incorporation pattern following the press_law/accounting_auditing_law precedent; Article 8's second amendment reflects the 2023 mother-to-child nationality-transmission reform; Article 61 مكرر's substantive text could not be recovered and was deliberately excluded rather than fabricated) + Foreigners' Residency Law (Iqama/Kafala Law), Royal (Supreme) Order 17/2/25/1337 1371H 69 (law, TIER_3: BOE does not index this 1371H law at all -- only its unrelated 1440H namesake, Premium Residency Law M/106 -- and MOI's own hosted PDF was unreachable both live and via Wayback; rests instead on a cross-verified secondary reproduction of the officially-circulated compiled text agreeing word-for-word across mohamah.net x rakadvocate.blogspot.com x islamport.com, with NSHR's own PDF used only for a structural cross-check) -- see track notes for a general, non-specific Article 64 repeal clause naming no prior statute (a confirmed negative finding, no supersession-graph edge modeled), an Article 37 repeal preserved not deleted, 4 مضافة articles, and Article 61 مكرر's confirmed-added-but-unrecoverable text deliberately excluded rather than fabricated)  + Saudi Arabian Civil Status Law, Royal Decree M/7 1407H 96 (law, TIER_2: BOE-via-Wayback seven independent snapshots, live BOE unreachable, cross-checked against qanoonsa.com's presentation of Council of Ministers Resolution 805 and nezams.com -- reclassified down from the research agent's own self-reported TIER_1 since qanoonsa.com is a private legal-aggregator portal, not a government site, so only ONE genuinely official/primary source exists here, following the nationality_law/nazaha_law precedent; confirmed dual repeal of two separately-named 1358H/1382H predecessors at Article 95 (with one temporary carve-out preserved, not repealed); a genuinely confirmed BOE main-body staleness for 24 amended articles resolved via BOE's own per-article changelog popups, a clean-incorporation pattern following the press_law/accounting_auditing_law/nationality_law precedent)  + Saudi Arabian Food Law, Royal Decree M/1 1436H 44 (law, TIER_2 conservative: ONE official/primary source, an SFDA-published PDF visually transcribed page-by-page, since laws.boe.gov.sa was completely unreachable both live AND via the Wayback Machine this pass -- a more severe access failure than this corpus's usual pattern -- cross-checked against saudipedia.com and FAOLEX but not a second independently-sourced full copy of the statute, honestly flagged rather than inflated; confirmed negative repeal finding at Article 45 (generic conflict-only clause naming no instrument); Article 1 تعريفات deliberately excluded since its text could not be recovered from any source, not fabricated)  + Saudi Arabian Health System Law, Royal Decree M/11 1423H 19 (law, TIER_3: BOE unreachable both live and via Wayback Machine this pass; nezams.com full verbatim text x qanoonsa.com's raw text of Council of Ministers Resolution 151 (an Umm Al-Qura Gazette reproduction, not a mirror) cross-verified, agreeing on the founding decree identity and 4 of 5 Article 16 amendment resolutions; confirmed negative repeal finding at Article 19 (generic conflict-only clause naming no instrument); Article 16's latest amendment step (Resolution 151, 1444H) deliberately not merged into the article text since no source gives an explicit replacement sub-paragraph, an honest gap rather than a fabricated insertion) + Domestic Labor Regulation, Ministerial Decision No. 40676 1445H 33 (regulation, TIER_2: BOE's own dedicated lawId page for this topic confirmed genuinely stale across 18+ months of Wayback snapshots, still showing only the superseded 310/1434H predecessor; PRIMARY source hrsd.gov.sa, the issuing Ministry's own official site, cross-checked against qanoonsa.com and lexismiddleeast.com; confirmed named repeal of the 310/1434H predecessor via the Ministerial Decision's own clause ثانياً; Article 33's genuine source-PDF truncation honestly flagged text_complete=False rather than completed or guessed) + Saudi Arabian Travel Documents Law, Royal Decree M/24 1421H 16 (law, TIER_2: BOE-via-Wayback three independent snapshots x nezams.com/qistas.com secondary, plus an official Umm Al-Qura Gazette cross-check for the M/11 1443H amendment specifically -- that subset alone reaches TIER_1-caliber confidence, flagged has_per_article_variation, while the rest of the law rests on BOE plus private-aggregator secondary sources only; confirmed scoped/partial repeal at Article 13, only the travel-document-related provisions of the 1358H Passports System predecessor, mirroring the municipal_councils_law precedent; two genuine internal BOE-source anomalies at Articles 6 and 10 preserved/resolved transparently) + Statute (Organizational Regulation) of the National Cybersecurity Authority, Royal Order 6801 1439H 15 (law, TIER_2: no laws.boe.gov.sa page for this exact statute could be located this pass; PRIMARY source nca.gov.sa's own official PDF, OCR-transcribed via Tesseract 5 to work around a confirmed systematic letter-transposition text-layer artifact, cross-verified against qistas.com and saudipedia.com; confirmed negative repeal finding at Article 15, generic conflict-only clause naming no instrument; a document-level amendment by Royal Order 7053 1443H honestly not attributed to any specific article) + Regulatory (Legal) Enablers of the National Cybersecurity Authority, Royal Decree م/117 1446H 7 (regulation, TIER_2: no laws.boe.gov.sa page for this exact instrument could be located this pass; PRIMARY source nca.gov.sa's own official PDF, sharing the parent statute's own confirmed letter-transposition text-layer artifact, OCR-transcribed, cross-verified against qanoonsa.com and uqn.gov.sa; a genuine structural anomaly -- seven بند clause divisions instead of numbered مواد, a first for this corpus; confirmed negative repeal finding at بند سابعاً; independently re-confirmed no amendment/repeal relationship to the parent cybersecurity_authority_law statute) + Premium Residency Law, Royal Decree M/106 1440H 14 (law, TIER_1_PRIMARY_MULTI_SOURCE: laws.boe.gov.sa's live portal unreachable this pass, but six independent Wayback Machine snapshots of BOE's own dedicated lawId page spanning 2019-2025 cross-verified word-for-word against misa.gov.sa's own hosted consolidated-text PDF, Ministry of Investment -- two independent official government sources agreeing; confirmed negative repeal finding at Article 14, names no predecessor at all, a wholly new residency category distinct from this corpus's already-ingested residency_law, mirroring the social_insurance_law/social_insurance_legacy_law naming-distinction precedent; Article 8 repealed by M/84 1445H with its pre-repeal text preserved not deleted; a disclosed single-word discrepancy between BOE and MISA at Article 2(e)) + Travel Documents Implementing Regulation, Ministerial Resolution 4203 1447H 53 (regulation, TIER_3 honest: no laws.boe.gov.sa lawId page at all for this instrument; moi.gov.sa/gdp.gov.sa unreachable; uqn.gov.sa domain-reachable but its specific gazette page not located this pass; PRIMARY qanoonsa.com raw-HTML direct fetch, Wayback-stable since 16 Apr 2026, cross-checked at the decree-metadata level against ncar.gov.sa, a genuine government archival body, and qanoniah.com, private indexing-level only; confirmed FULL repeal of the 1422H predecessor Implementing Regulation, Decision 7/waw-zay, via Article 52, a genuine positive finding unlike the parent travel_documents_law track own generic-repeal precedent; Article 37(3)'s confirmed source-side typo, 'مي نع' for 'يمنع', preserved verbatim not silently corrected) + Implementing Regulation of the Saudi Arabian Nationality Law, Ministerial Decision 74/زو 1426H 35 (regulation, TIER_2: laws.boe.gov.sa hosts no dedicated page at all for this Implementing Regulation; PRIMARY moi.gov.sa fetched via three independent Wayback Machine snapshots spanning 2011-2024, byte-identical sha256 across all 13 years, cross-verified against nezams.com and alriyadh.com's 2005G contemporaneous full-text reproduction, which independently resolved this corpus's own prior gap-map estimate of ~25 articles to the confirmed true count of 35; Article 28 confirmed repealed circa March 2023 by Minister of Interior decision following Royal Decree M/88's transfer of nationality-grant authority, independently confirmed by 5+ news outlets, moi.gov.sa's own PDF confirmed genuinely stale and still showing the pre-repeal text over a year later, joining accounting_auditing_law/awqaf_law/civil_status_law/domestic_labor_regulation/engineering_practice_law/environmental_law/income_tax_law/nationality_law/patent_law/press_law/saudi_engineers_law/traffic_law in the freshness manifest's known_source_staleness_risk: true flag; confirmed negative finding that this Regulation names no predecessor instrument of its own) + Implementing Regulation of the Saudi Arabian Health System Law, Ministerial Decision 30/69181 1424H 10 (regulation, TIER_4: laws.boe.gov.sa hosts no dedicated page at all for this Implementing Regulation and istitlaa.ncc.gov.sa confirmed unreachable via three independent channels, Wayback blocked at the egress-policy level; PRIMARY qanoniah.com's public API, a confirmed server-enforced 10-item preview cap covering ONLY parent Law Articles 2-11 with non-contiguous numbering keyed to the parent law's own article numbers; Article 1 has no entry at all and Articles 12-19, including the heavily-amended Article 16 Health Services Council, could not be recovered -- both honestly excluded, not fabricated; confirmed negative finding that this Regulation names no predecessor instrument of its own) + Implementing Regulation of the Saudi Arabian Food Law, SFDA Board Resolution No. (3-16-1439) 1439H 85 (regulation, TIER_2: laws.boe.gov.sa checked first per standard methodology but unreachable this pass and confirmed to have no dedicated lawId page for this Implementing Regulation at all; PRIMARY sfda.gov.sa born-digital PDF (2025-06 upload, genuine embedded text layer, unlike the older scanned/rasterized PDF the food_law track itself had to rely on), cross-verified against qanoonsa.com and qistas.com; 81 اصلية / 1 معدلة (Article 41) / 3 مضافة (Articles 42-44) per SFDA Board Resolution 4/44 1446H; three systematic font ligature-reversal extraction defects fixed via an individually-verified substitution dictionary; the final article's own printed header mislabeled '(58)' for 85, preserved verbatim not silently renumbered; a separate penalty-classification table confirmed out of scope; confirmed negative finding that this Regulation names no predecessor instrument of its own) + The Saudi Arabian Electricity Law, Royal Decree M/44 1442H 23 (law, TIER_3: laws.boe.gov.sa unreachable this pass (connection reset / HTTP 503), Wayback egress-blocked; PRIMARY nezams.com, a single clean born-digital HTML full-text aggregator page (no scan/OCR/ligature defects), all governing metadata cross-verified against multiple independent sources (BOE/Umm Al-Qura via WebSearch, Lexis Middle East, SERA); 23 اصلية, the Law has had no amendments; confirmed named repeal-and-replace of the older Electricity Law (Royal Decree M/56, 1426H) via this Law's own Article 23, a genuine positive finding; two Implementing Regulations (Minister and Council level) identified but not ingested this pass) + The Saudi Arabian Water Law, Royal Decree M/159 1441H 77 (law, TIER_3: laws.boe.gov.sa has a dedicated lawId page for this law but it was unreachable this pass, HTTP 503/connection reset, and the usual Wayback fallback confirmed a snapshot exists but was egress-blocked at HTTP 403; PRIMARY nezams.com, an independent Arabic legal-text aggregator (not a BOE mirror), all 77 articles extracted from its raw HTML; decree identity, Article 74 text, the SAR-20-million penalty ceiling, and the 17-chapter structure independently cross-verified via WebSearch indexing of BOE's own content; 77 اصلية, the Law has had no amendments; confirmed named repeal-and-replace of THREE separate predecessor laws by decree number (نظام مصالح المياه والصرف الصحي M/22 1391H، نظام المحافظة على مصادر المياه M/34 1400H، نظام مياه الصرف الصحي المعالجة وإعادة استخدامها M/6 1421H) via this Law's own Article 75 -- a MATERIAL distinction from this corpus's health_system_law/food_law tracks, whose own repeal clauses are generic conflict-only; two Implementing Regulations plus the separate Saudi Water Code identified but not ingested this pass; Article 3's Zamzam-water scope exclusion and Article 44's verbatim source typo preserved, not silently corrected) + Implementing Regulation of the Saudi Arabian VAT Law, ZATCA Board of Directors Resolution No. (3839), 14 Dhul-Hijjah 1438H 82 (regulation, TIER_3: laws.boe.gov.sa has no dedicated lawId page for this Board-level regulation; PRIMARY zatca.gov.sa official consolidated PDF, the "Tenth Edition" (Shawwal 1446H / April 2025) consolidating 11 amending Board resolutions; dual PyMuPDF-geometric x Tesseract-OCR extraction reconciled to work around a systematic bidi word-order defect; 37 اصلية/42 معدلة/3 مضافة (mukarrar articles); independently re-resolved the printed cover-date anomaly (corrected "14 نوفمبر 2016م" to the true Hijri-derived 5 September 2017G, not merely copied from the parent vat_law track); confirmed no separate named predecessor beyond the parent Law) + Implementing Regulation of the Saudi Arabian Income Tax Law, Ministerial Resolution No. (1535), 11/6/1425H 74 (regulation, TIER_3: laws.boe.gov.sa has no dedicated lawId page for this Ministerial-Resolution-level regulation, only the base Law; PRIMARY two cross-verified government copies -- ZATCA official consolidated PDF x gstc.gov.sa INCOM2.pdf, both headers confirming the exact founding date (11/6/1425H) the parent income_tax_law track could not pin down; 30 اصلية/19 معدلة/25 ملغاة across 30 topical section headings; NATURAL-GAS RISK INVERSE OF THE PARENT LAW TRACK -- 25 old-regime IRR natural-gas articles formally repealed by Resolution 2568 but preserved in full text with a تم حذف المادة footnote, unlike the parent track's bare repeal notice; PyMuPDF coordinate-based extraction with disclosed lam-alef-ligature and other extraction-layer fixes; confirmed no separate named predecessor beyond the parent Law) + The Saudi Arabian Agriculture Law, Royal Decree M/64, 10/8/1442H 37 (law, TIER_3: laws.boe.gov.sa has a dedicated lawId page for this law but it was unreachable this pass, HTTP 503, and Wayback was not circumvented per this corpus's no-egress-bypass rule; PRIMARY nezams.com, an independent Arabic legal-text aggregator, all 37 articles extracted from clean born-digital HTML; the flat no-chapter structure and the exact 37-article count independently cross-verified via the official MISA English-language PDF plus further WebSearch corroboration across BOE, MEWA, Umm Al-Qura, and Lexis, with no source disagreeing; 37 اصلية, the Law has had no amendments; CONFIRMED NAMED REPEAL OF FIVE PREDECESSOR INSTRUMENTS -- unlike every other repeal pattern in this corpus, the repeal sits in the LAW'S OWN ISSUING DECREE (clause ثانياً of Royal Decree M/64 and of Council of Ministers Resolution 431), not inside any of the 37 numbered articles: نظام الثروات المائية الحية M/9 1408H، نظام الثروة الحيوانية M/13 1424H، نظام تربية النحل M/15 1431H، نظام الزراعة العضوية M/55 1435H، and قواعد تنظيم الاتجار بالآلات الزراعية (Council of Ministers Rules No. 96, 1405H); Article 36's own Implementing Regulation identified as existing and published but not ingested this pass) + Implementing Regulation of the Saudi Competition Law, GAC Board of Directors Decision No. (337), 25/1/1441H 5 (regulation, TIER_2, PARTIAL SCOPE: only Articles 1-5 of the full 90-article/11-chapter Regulation are ingested this pass, all 5 اصلية; PRIMARY qanoniah.com clean-Unicode API x WIPO Lex official Arabic PDF dual independent source for the captured articles only; the remaining 85 articles were deliberately NOT ingested because the only complete fetchable Arabic source (WIPO Lex's sa071ar.pdf) has an unrecoverable lossy digit-CMap defect and the clean qanoniah.com source auth-gates articles 6+, disclosed not fabricated; confirmed supersession of the 2014 Implementing Regulation of the repealed Competition Law M/25 (Competition Council Decision 126, 4/9/1435H), recorded as a supersession-graph edge) + Implementing Regulation of the Anti-Money Laundering Law, Administrative Decision No. (266507), 9/12/1447H 25 (regulation, TIER_3: laws.boe.gov.sa has no dedicated lawId page for this State-Security-level Regulation; PRIMARY aml.gov.sa official scanned PDF (no text layer), text reconciled from two independent channels -- 10 of 25 articles from qanoniah.com's born-digital API (confirmed same current consolidated version) and the other 15 OCR-extracted and visually adjudicated against the rendered scan; 24 اصلية/1 معدلة (Article 17, pre-amendment text not recoverable, not fabricated); confirmed no in-Regulation repeal clause naming a predecessor, the supersession of the prior legal regime being derivative via the parent aml_law's own Article 51; a genuinely distinct older 1430H regulation confirmed to exist but deliberately not mixed in) + Implementing Regulation of the Patents Law, KACST President Resolution No. (161-2-3607329), 30/12/1436H 67 (regulation, TIER_3: laws.boe.gov.sa unreachable this pass and has no dedicated lawId page for this agency-level Regulation; PRIMARY official SAIP-letterhead Arabic PDF on WIPO Lex, dual independent extraction pipelines reconciled, structurally cross-verified against WIPO Lex metadata and qanoonsa.com; 67 اصلية across 12 أبواب; confirmed no named-predecessor repeal, the first Implementing Regulation under the current Patents Law M/27; disclosed staleness mirroring the base patent_law track -- a later 2024 amendment (SAIP Board Resolution 02/32/2024) not reflected in this 2019-consolidated text) + Implementing Regulation of the E-Commerce Law, Ministerial Resolution No. (200), 19/5/1441H 20 (regulation, TIER_1: laws.boe.gov.sa returned HTTP 503 this pass and has no dedicated lawId page for this Ministerial-Resolution-level Regulation; PRIMARY the issuing Ministry's own official born-digital regulations page (mc.gov.sa) cross-verified word-for-word against the Ministry's own official scanned PDF, further corroborated via qanoniah.com/lexismiddleeast.com/argaam.com/mithaq.com.sa; 20 اصلية, flat structure with no chapters; confirmed no named-predecessor repeal since the base E-Commerce Law itself only dates to 1440H) + Implementing Regulation of the Franchise Law, Minister of Commerce Resolution No. (591), 18/9/1441H 16 (regulation, TIER_2: laws.boe.gov.sa hosts a lawId page for the base Law but none for this Regulation; PRIMARY franchising.sa Umm Al-Qura gazette reproduction cross-verified VERBATIM against aunklaw.com for all 16 articles plus lexismiddleeast.com for structure; 16 اصلية across 6 فصول; confirmed no named-predecessor repeal; a genuine annex-only amendment -- disclosure-document element 13 later deleted -- disclosed and preserved verbatim in its original 17-element form, not silently applied) + Implementing Regulation of the Traffic Law, Ministerial Resolution (Minister of Interior) No. (2249), 10/3/1441H 86 (regulation, TIER_3: laws.boe.gov.sa hosts a lawId page for the base Law but none for this Regulation; PRIMARY an official MOI scanned document reconstructed via two independent extraction pipelines -- direct vision reading plus tesseract-ara OCR as a cross-check layer -- cross-verified VERBATIM against qanoniah.com's born-digital text for Articles 1-8 only (100% match on Articles 1,3,4,5,6,8; 99.0% on Article 2, cosmetic-only; 51.5% divergence on Article 7, correctly confirming rather than undermining the finding since Article 7 is independently known to be amended); 82 اصلية / 3 معدلة (Articles 7, 23, 47) / 1 ملغاة (Article 80, per an explicit repeal footnote in the primary source itself citing Council of Ministers Resolution 636, 23/10/1438H); **CONFIRMED named-predecessor repeal** of the prior Implementing Regulation, Ministerial Resolution No. (7019), 3/7/1429H, per the Resolution's own verbatim preamble clause (ثانياً) -- a genuine positive supersession finding recorded as a real repeals_full edge in the supersession graph, unlike this window's more common confirmed-negative pattern) + Implementing Regulation for Environmental Inspection and Audit under the Environmental Law, Ministerial Decision (15116190), 12 Jumada al-Ula 1446H 10 (regulation, TIER_2: laws.boe.gov.sa has no dedicated lawId page for this Regulation; PRIMARY qanoonsa.com reproducing Umm Al-Qura Gazette issue 5057, cross-verified against qistas.com for Articles 2-3 and citation-corroborated via the replacing decision's own gazette recital and the MEWA/SPA announcement; 10 اصلية (8 articles + Table 1 + Appendix 1), CONFIRMED self-supersession of the decision's own prior 393691/1/1442 original, recorded as a repeals_full edge) + Implementing Regulation for Recording Environmental Violations and Imposing Penalties under the Environmental Law, Ministerial Decision (15101619), 26/4/1446H 10 (regulation, TIER_2: laws.boe.gov.sa has no dedicated lawId page, PRIMARY qanoonsa.com consolidated in-force text cross-verified against qistas.com appendix; 10 اصلية (8 articles + 2 appendix templates), CONFIRMED self-supersession of the decision's own prior 312186/1/1442 original, recorded as a repeals_full edge) + Implementing Regulation for Environmental Permits for Establishing and Operating Activities, Minister Decision (43615/3/1/1442), 09/08/1442H 11 (regulation, TIER_1: two independent official renderings of the SAME Umm Al-Qura Gazette issue 4888 -- the gazette's own HTML page and its own born-digital PDF -- cross-verified 99.66% word-level via anagram-signature comparison; 11 اصلية, confirmed no named-predecessor repeal) + Implementing Regulation for Air Quality under the Environmental Law, Minister Decision (512258/1/1442), 24/9/1442H 8 (regulation, TIER_2: PRIMARY the issuing Ministry's own official born-digital PDF (mewa.gov.sa) cross-verified ~100% word-level against qanoniah.com; 8 اصلية, confirmed no named-predecessor repeal; violations/penalties Table and 8 technical appendices documented as excluded) + Implementing Regulation for Environmental Service Providers, Ministerial Decision (1515009/1), 3/7/1446H 13 (regulation, TIER_2: laws.boe.gov.sa has no dedicated lawId page; PRIMARY the issuing Ministry's own official scanned decision PDF (visually read, no text layer) x qanoniah.com clean HTML; 13 اصلية (12 articles + Table 1), CONFIRMED self-supersession of the decision's own prior 582979/1/1442 original, recorded as a repeals_full edge) + Implementing Regulation for the Financial Consideration (Fees) for Environmental Licenses/Permits/Services, Minister Decision (618660/1/1442), 05/12/1442H 4 (regulation, TIER_2: laws.boe.gov.sa has no dedicated lawId page, the Umm Al-Qura gazette portal is a JS-rendered SPA whose text could not be extracted this pass; PRIMARY qanoniah.com cross-verified via multi-source citation corroboration; 4 اصلية, confirmed no named-predecessor repeal, Annex-1 fee-ceiling table documented as excluded) + Real Estate Transaction Tax Law, Royal Decree M/84, 19/3/1446H 20 (law, TIER_2: laws.boe.gov.sa has a dedicated lawId page for this law but the live page returned HTTP 503 this pass; PRIMARY the full text retrieved via the r.jina.ai read-proxy of the same official BOE lawId URL, cross-verified against nezams.com and qanoonsa.com non-government secondaries; 20 اصلية, flat structure/no chapters; Article 20(2)'s repeal clause is GENERIC, naming no predecessor, so no supersession-graph edge is modeled -- the substantive predecessor context, Royal Order A/84 1442H, is disclosed as historical context only) + Universities Law, Royal Decree M/27, 2/3/1441H 58 (law, TIER_2: laws.boe.gov.sa has a dedicated lawId page for this law but was unreachable this pass, HTTP 503/connection reset, Wayback egress-blocked; PRIMARY bibliotdroit.com born-digital text cross-verified article-by-article (all 58, not a spot-check) against the administering authority's own official cua.gov.sa PDF, structure re-confirmed by a third source, moe.gov.sa; 58 اصلية across 14 فصول; CONFIRMED named-predecessor repeal of نظام مجلس التعليم العالي والجامعات (M/8, 4/6/1414H) via Article 57, disclosed as a PHASED, not instantaneous, replacement per the Royal Decree's own transitional clauses) + Privatization Law, Royal Decree M/63, 5/8/1442H 45 (law, TIER_2 lower end: laws.boe.gov.sa has a dedicated lawId page for this law but was unreachable this pass, live HTTP 503/connection reset, Wayback egress-blocked; PRIMARY nezams.com full governing text, cross-verified against an official misa.gov.sa/National Center for Privatization PDF confirming the 45-article count, flat no-chapter structure, and verbatim Articles 44-45 (a genuine but partial, not full article-by-article, official cross-check); 45 اصلية, flat structure; Article 45's repeal clause is GENERIC, naming no predecessor -- the named repeals of prior CoM/Supreme Economic Council instruments sit instead in the accompanying Council of Ministers Resolution 436, a different instrument, disclosed as historical context only) + Antiquities, Museums and Urban Heritage Law, Royal Decree M/3, 9/1/1436H 94 (law, TIER_3: laws.boe.gov.sa has a dedicated lawId page for this law but was unreachable this pass, HTTP 503/connection reset, Wayback egress-blocked; PRIMARY nezams.com born-digital text corroborated by a BOE-content print PDF hosted on media.unesco.org (a non-government international body's hosting, not a Saudi government domain, so honestly kept at TIER_3) plus the Umm Al-Qura Gazette for the M/67 amendment's scope specifically; 78 اصلية/16 معدلة across SIX amendment instruments (M/16 1439H, CoM 693 1441H, M/67 1442H, M/103 1442H, CoM 1012 1445H), genuinely flat/no chapters; CONFIRMED named-predecessor repeal of نظام الآثار (M/26, 23/6/1392H) via Article 92) + Child Protection Law, Royal Decree M/14, 3/2/1436H 26 (law, TIER_3: laws.boe.gov.sa has a dedicated lawId page for this law but was unreachable this pass, Wayback not attempted (egress-policy-blocked); PRIMARY nezams.com full text, decree identity/5-chapter structure/original 25-article pre-amendment text independently confirmed by an official Ministry of Justice Adl-journal PDF -- used for identity/structure/article-count confirmation only, not letter-for-letter matching, due to a bidi-reordering PDF-extraction defect, honestly kept at TIER_3; 25 numbered articles + 1 مكرر across 5 فصول, 21 اصلية/4 معدلة/1 مضافة; CONFIRMED amendment via CoM Resolution 427/Royal Decree M/72 1443H amending Articles 12,15,19,23 and adding Article 23-mukarrar criminal penalties, independently confirmed via the Umm Al-Qura Gazette; no repeal clause of any kind found in the text, a founding statute; distinct from juveniles_law and the separate protection_from_abuse_law candidate) + Protection from Abuse Law, Royal Decree M/52, 15/11/1434H (approving CoM Resolution 332, 19/10/1434H; published Umm Al-Qura Gazette 24/12/1434H) 17 (law, TIER_2: laws.boe.gov.sa has a dedicated lawId page for this law but was unreachable this pass, HTTP 503, Wayback egress-blocked; PRIMARY an official Ministry of Finance regulations-library PDF (mof.gov.sa, Diwan Malaki circular 41930) used directly as the governing text, cross-checked verbatim against nezams.com; 14 اصلية/3 معدلة/0 ملغاة/0 مضافة; CONFIRMED amendment to Articles 7, 12, 13 via the same 1443H instrument that amended child_protection_law, independently confirmed via the Umm Al-Qura Gazette cross-checked against nezams.com; no repeal clause of any kind found in the text, a founding statute; distinct from child_protection_law, with an Implementing Regulation flagged as a follow-up candidate) + Law of Associations and Civil Institutions, Royal Decree M/8, 19/2/1437H (approving CoM Resolution 61, 18/2/1437H; published Umm Al-Qura Gazette 7/3/1437H) 44 (law, TIER_3: laws.boe.gov.sa's own indexing shows TWO different lawId values for this law's name and the live portal was unreachable this pass (HTTP 503 / connection reset across several attempts); PRIMARY nezams.com full text, independently cross-checked against a menarights.org PDF (KSA_Law on NGOs 2015) confirming article count and the closing articles' verbatim text, honestly kept at TIER_3; 43 اصلية/1 معدلة (Article 1 only, CoM Resolution 618's new definitions; Articles 7/25/38 explicitly exempted from Resolution 618's horizontal substitution and remain اصلية); CONFIRMED named-predecessor repeal of لائحة الجمعيات والمؤسسات الخيرية (CoM Resolution 107, 25/6/1410H) via Article 43, flagged for the supersession graph; Implementing Regulation flagged as a follow-up candidate) + Law of Audiovisual Media, Royal Decree M/33, 25/3/1439H (approving CoM Resolution 170, 24/3/1439H) 25 (law, TIER_2: laws.boe.gov.sa has a dedicated lawId page for this law but was unreachable this pass, HTTP 503, Wayback refused outright by the fetch tool itself and not circumvented; PRIMARY nezams.com full text strongly cross-checked against an archived scan of the actual BOE portal page (cyrilla.org) and the official BOE English translation (misa.gov.sa); 24 اصلية/1 معدلة (Article 1 only, CoM Resolution 374's terminology substitution); no repeal of any predecessor found (generic conflict clause only); distinct from press_law) + Sports Law, Royal Decree M/121, 10/6/1447H (approving CoM Resolution 414, 4/6/1447H; published Umm Al-Qura Gazette issue 5129, ~12 Dec 2025G; entry into force ~June 2026G) 97 (law, TIER_3: laws.boe.gov.sa and mos.gov.sa both unreachable this pass, Wayback egress-blocked; PRIMARY nezams.com full text cross-checked verbatim against qanoonsa.com, decree identity/date officially confirmed via the Umm Al-Qura gazette's own JSON API; 97 اصلية across 11 أبواب, brand-new founding statute (in force only since ~June 2026); CONFIRMED named-predecessor repeal of the Basic Law of Sports Federations and the Saudi Arabian Olympic Committee (M/55, 19/10/1407H) via Article 96, flagged for the supersession graph) + Anti-Smoking Law, Royal Decree M/56, 28/7/1436H (approving CoM Resolution 90, 23/3/1434H; published Umm Al-Qura Gazette 2/9/1436H) 20 (law, TIER_2: BOE unreachable this pass, a confirmed Wayback snapshot could not be fetched since web.archive.org is egress-blocked; PRIMARY an official Ministry of Health PDF used directly as the governing text, cross-checked verbatim against nezams.com and a bilingual cloudfront.net legislation PDF; 20 اصلية, flat structure/no chapters, no amendment to the Law itself; no confirmed named-predecessor repeal (only a transitional continuation clause for unnamed prior agency rules, honestly not counted as a repeal)) = **10974 records**) into one flat index at
  `data/corpus_unified_index/corpus_unified_llm_index.jsonl` with a common schema. Query the whole
  corpus at once with `python3 scripts/search_corpus_unified.py "<عربي>"` (deterministic lexical
  scorer over each record's keywords / search_queries / titles / text; `--corpus` and `--top`
  flags). No legal text is altered, summarized, or translated. Validate (includes sanity queries
  that must route to the right law): `make corpus-unified-llm-index-validate`.
- **Retrieval eval pack** — realistic Arabic gold queries over the unified index
  (`data/corpus_retrieval_eval/`), each gold manually confirmed against the article's own text
  (definitional articles) or official title — not reverse-engineered from search output. Runner
  `scripts/run_corpus_retrieval_eval.py` computes top-1/top-3/top-5 accuracy + MRR@5 and writes
  deterministic results. **Current: top-1 93.3% (484/519) / top-3 97.5% (506/519) / top-5 98.8% (513/519) / MRR@5 0.9559**
  over the 15689-record index with **519 golds** — expanded from 40 (v2: gtp-001..007 +
  lab-001..014; v3: ith-001..003; v4: ith-004..006; v5: ahw-001..004; v6: mrf-001..003 law; v7: mrf-004..006 regulation; v8: mjz-001..003 criminal-procedure law; v9: mjr-001..003 criminal-procedure regulation; v10: mtn-001..003 enforcement law; v11: mtl-001..003 enforcement regulation; v12: mqd-001..003 judiciary; v13: dmz-001..003 board-of-grievances; v14: muh-001..003 law-practice; v15: mhl-001..003 law-practice-regulation; v16: tjr-001..003 commercial-courts; v17: tjl-001..003 commercial-courts-regulation; v18: ifl-001..003 bankruptcy law; v19: ilr-001..003 bankruptcy regulation; v20: icr-001..003 bankruptcy case rules; v21: tkq-001..002 judicial-costs law + tkr-001 regulation; v22: thk-001..002 arbitration law + thr-001 regulation; v23: awt-001..003 commercial-papers law; v24: sjt-001..002 commercial-register + ast-001 trade-names; v25: wkl-001..002 commercial-agencies; v26: ghr-001..002 chambers-of-commerce; v27: dft-001..002 commercial-books; v28: hmb-001..002 whistleblower-protection; v29: tft-001..002 judicial-inspection; v30: qsm-001..002 qismah-division; v31: slk-001..002 sulook-professional-conduct; v32: awn-001..002 aawan-judicial-assistants; v33: msl-001..002 muslaha-conciliation-offices; v34: ifh-001..002 iflas-hudud-cross-border-insolvency; v35: jud-001..002 judicial-documents-regulation; v36: atb-001..002 bankruptcy-fees-regulation; v37: tnf-001..002 enforcement-providers-regulation; v38: nfq-001..002 alimony-fund-regulation; v39: jbm-001..002 judiciary-bog-mechanism; v40: esd-001..002 documentation-settlement-regulation; v41: msc-001..002 mosalaha-center-regulation; v42: mtr-001..002 medical-reports-regulation; v43: mzj-001..002 marriage-non-saudi-regulation; v44: mnd-001..002 state-funded-lawyer-regulation; v45: dmn-001..002 lessor-repossession-regulation; v46: tqe-001..002 elitigation-guide-regulation; v47: mtd-001..002 judicial-training-center-guide (bespoke track); v48: tea-001..002 judgment-objection-methods-regulation, plus mrf-001's sanity companion re-pointed from sharia_procedure art 176 to art 177 in the unified-index SANITY list after a topical-overlap collision with this new track's title-heavy content; v49: nzm-001..002 real-estate-expropriation-law; v50: zwj-001..002 marriage-contract-hearing-regulation; v51: rsw-001..002 anti-bribery-law, DISTINCT lower-confidence secondary-source verification tier — see track notes; v52: blg-001..002 basic-law-of-governance, DISTINCT tier (BOE portal primary source x WIPO Lex spot-checked) — see track notes; v53: cyb-001..002 anti-cyber-crime-law, DISTINCT tier (BOE x WIPO Lex/CITC x MOF exhaustive triple-source verified, the strongest tier outside the primary MOJ pipeline) — see track notes; v54: hrs-001..002 anti-harassment-law, DISTINCT mixed tier (7 BOE-multi-source-checked articles + art 6's 2021 amendment sourced via secondary press convergence, exact wording flagged with a documented alternate candidate) — see track notes; v55: trf-001..002 anti-trafficking-law, DISTINCT tier (full text from a Wayback Machine snapshot of the BOE portal, substance-cross-checked against UNODC's official English translation and the 2025 US State Department TIP Report; a 33-article draft replacement law remains unenacted and is documented but not ingested) — see track notes; v56: cmn-001..002 council-of-ministers-law, DISTINCT tier (laws.boe.gov.sa confirmed completely unreachable across two research passes; full text rests on cross-verified word-for-word agreement between two independent Arabic secondary sources, ar.wikisource.org and nezams.com, with FAOLEX's English PDF used only for a structural cross-check) — see track notes; v57: rgn-001..002 regions-law, DISTINCT tier (this law's specific BOE page could not be reached across ~20 attempts despite a different BOE page succeeding in the same session; full text rests on cross-verified agreement between two independent Arabic secondary sources, islamport.com and nezams.com, with FAOLEX's English PDF used only as a weaker meaning-level cross-check, confirmed incomplete and date-flawed) — see track notes; v58: etr-001..002 electronic-transactions-law, DISTINCT tier (single primary source, the official BOE/CoM translation-bureau PDF manually corrected for a systematic lam+alef ligature-extraction bug, structurally cross-checked against WIPO Lex's full English translation across 100% of articles; Chapter 6/arts 16-17 abolished by a 2023 amendment and flagged ملغاة, with the exact post-abolition article renumbering left undetermined and documented) — see track notes; v59: hba-001..002 allegiance-commission-law, DISTINCT tier (triple independent Arabic secondary sources, ar.wikisource.org x islamport.com x ar.wikipedia.org, this law's BOE page located but unreachable) — see track notes, including a documented cross-track conflict with the Basic Law of Governance's Article 5(c) since resolved via a dedicated follow-up correction; v60: shc-001..002 shura-council-law, MIXED tier (triple independent Arabic secondary sources for 29 articles, plus a Tier-1 government primary source, Saudi Press Agency, for article 3's current 2013-amended text) — see track notes; v61: cpr-001..002 copyright-law, DISTINCT tier (qadha.org.sa compiled text structurally cross-checked against WIPO Lex, laws.boe.gov.sa unreachable) — CONFIRMED SUPERSEDED effective 2026-08-01 by Royal Decree M/169, whose text could not be verified this pass and is not ingested — see track notes; v62: tlc-001..002 telecommunications-law, DISTINCT tier (laws.boe.gov.sa primary source reachable this pass, cross-checked against MCIT's own official PDF; fresh replacement law, all 41 articles اصلية, with an unconfirmed 2024 proposed-amendment consultation flagged on articles 20/24/25/27) — see track notes; v63: scb-001..002 sama-law, DISTINCT tier (SAMA official PDF primary source x BOE Wayback archive cross-check) — see track notes; v64: bnk-001..002 banking-control-law, DISTINCT tier (dual independent Arabic secondary sources, BOE unreachable for raw text) — see track notes; v65: cml-001..002 capital-market-law, MIXED tier (picked from the main-tier confirmed-current portion; 12 of 68 records are flagged 2003-only historical fallback, see track notes before using those) — see track notes; v66: ctp-001..002 competition-law, DISTINCT tier (BOE Wayback snapshot x nezams.com cross-verified word-for-word) — see track notes; v67: pay-001..002 payment-systems-law, DISTINCT tier (official SAMA PDF, dual independent OCR passes x nezams.com cross-verified word-for-word) — see track notes; v68: min-001..002 mining-investment-law, DISTINCT tier (BOE Wayback snapshot fetched directly x FAOLEX structural cross-check) — see track notes; v69: trd-001..002 trademark-law, DISTINCT tier (WIPO Lex primary PDF with embedded BOE status card x two independent OCR passes for the M/49 amendment) — see track notes; v70: tsr-001..002 anti-concealment-law, DISTINCT tier (triple independent Arabic secondary sources, qadha.org.sa x nezams.com x alrashidi.law, BOE completely unreachable via all three prescribed methods) — see track notes for this genuine sourcing limitation; v71: ins-001..002 insurance-control-law, DISTINCT tier (misa.gov.sa official bilingual PDF x nezams.com cross-verified, BOE and Wayback both unreachable) — see track notes for the flagged institutional-name divergence and the pre-amendment-original-text limitation; v72: ecm-001..002 ecommerce-law, DISTINCT tier (BOE portal via a single Wayback Machine snapshot fetched directly x nezams.com cross-verified) — see track notes for the flagged stale ministry name and Article 22's missing terminal punctuation; v73: vat-001..002 vat-law, DISTINCT tier (ZATCA official consolidated PDF x BOE portal cross-verified via r.jina.ai; Wayback Machine unreachable) — see track notes for the important limitation that pre-amendment original text is not included for either amended article; v74: frn-001..002 franchise-law, DISTINCT tier (BOE portal via r.jina.ai proxy after a direct WebFetch 503, spot-cross-verified against qanoniah.com for Articles 1, 2, 4, 5 only) — see track notes for the flagged M/22 decree-number collision with the unrelated superseded Anti-Concealment Law, and the non-textual 2026 Council of Ministers carve-out decision; v75: cav-001..002 civil-aviation-law, DISTINCT tier (nezams.com direct fetch as primary full-text source, spot-checked against rakadvocate.blogspot.com for Articles 1 and 180 only, BOE unreachable via all methods tried) — see track notes for the flagged Article 149 heading anomaly, the single-sourced Council of Ministers Resolution 158/1445H institutional rename, and the documented pre-amendment-text gap for Article 46; v76: nrc-001..002 anti-narcotics-law, DISTINCT tier (BOE portal via r.jina.ai proxy x nezams.com word-for-word cross-verification x qadha.org.sa reference book triple-verifying the highest-stakes penalty articles) — see track notes for the flagged Article 42 BOE-vs-nezams.com textual variant and Article 35's anomalous heading, both preserved/resolved transparently rather than silently; v77: trc-001..002 traffic-law, the corpus's most complex verification case — TWO research passes confirmed the BOE portal is genuinely stale for this law (not a proxy artifact) via four independently-verified data points, with nezams.com preferred for amended articles and a per-article verification_tier field carrying real per-article confidence rather than one overstated track-level claim — see track notes for the Table 2 item-16 numbering conflict and the full 11-item discrepancy list; v78: env-001..002 environmental-law, STRONG triple-source tier (BOE via Wayback Machine x an independently-hosted green.org.sa PDF x nezams.com, matching verbatim for 48 of 49 articles) — see track notes for the one flagged exception, Article 1's 'الجهة المختصة' definition, where BOE's own amendment-log contradicts BOE's own main article text, resolved as operative per the Traffic Law track's BOE-lag precedent and flagged for dedicated human legal review; v79: itx-001..002 income-tax-law, DISTINCT tier (BOE via Wayback Machine x ZATCA's own official PDF x gstc.gov.sa PDF x nezams.com, 3-4-source agreement for 69 of 81 articles) — see track notes for the flagged Chapter 10 limitation (both government PDF sources omit that chapter's substantive M/70 replacement text, mirroring the VAT Law track's finding in reverse) and Article 66's unresolved dual-date conflict for Royal Decree M/52, recorded rather than silently resolved; v80: cvs-001..002 civil-service-law, DISTINCT tier (BOE portal via Wayback Machine x nezams.com full cross-verification, 100% of 44 article-entries matched) — see track notes for Article 3's repeal (M/95, no replacement text fabricated) and the 11 documented discrepancies including 14 BOE-citation gaps; v81: sin-001..002 social-insurance-law (New System, M/273), DISTINCT tier (BOE Wayback snapshot independently re-fetched by the build agent after its assigned research report proved paraphrased rather than verbatim x nezams.com 5-article spot-check x qanoonsa.com structural corroboration) — see track notes for the identical-title collision with the separately-tracked old Social Insurance Law (M/33) and the statutory-2%-vs-administrative-1.5% unemployment-insurance-rate discrepancy at Article 44; v82: sil-001..002 social-insurance-legacy-law (Old System, M/33), DISTINCT tier (BOE Wayback Machine snapshot x nezams.com cross-verification for 20+ articles plus 100% of the nine changed-article amendment popups, Article 37's reconciled text additionally corroborated via independent Okaz/Al-Riyadh news coverage) — see track notes for the identical-title collision with the new Social Insurance Law (M/273), Articles 10 and 37's resolution to current reconciled text over BOE's confirmed-stale rendering, and Article 38's discrete non-merge note; v83: zkt-001..002 zakat-law (Minister of Finance Resolution No. 1007, 1445H), SINGLE-SOURCE tier (ZATCA's own official PDF as the sole full-text primary source, laws.boe.gov.sa confirmed unreachable across two independent passes, Umm Al-Qura Gazette used only for targeted spot-verification of 2 specific facts) — see track notes for the severe lam-alef ligature PDF-extraction bug discovered and fixed during the build, the debunked 200,000/400,000 SAR minimum-base claim, and the documented residual risk of uncorrected line-order artifacts in a small number of paragraphs; v84: ptn-001..002 patent-law (Royal Decree M/27, 1425H), DISTINCT tier (WIPO Lex's M/45-consolidated text cross-verified via two independent OCR passes plus a native-text-layer extraction of the same document, BOE confirmed stale on two axes for this law) — see track notes for the terminology-substitution-scope judgment and the preserved Article 35-vs-42/63 drafting inconsistency; v85: cst-001..002 customs-law/customs-regulation (Royal Decree M/41, 1423H; Resolution 2748, 1423H), SINGLE-SOURCE tier (ZATCA's own official consolidated PDF as the sole full-text primary source for both tracks, laws.boe.gov.sa confirmed unreachable) — see track notes for the three-pass post-build QA process (negation-particle fix, glued-list-marker fix, final residual-instance fix) this pair's extraction required; v86: afl-001..002 anti-fraud-law (Royal Decree M/19, 1429H), SECONDARY-MULTI-SOURCE tier (three independently cross-verified secondary sources — nezams.com, mustsharik.com, mohamah.net — laws.boe.gov.sa confirmed unreachable at two distinct URL forms across two research/build passes) — see track notes for the disputed Article 5 second-amendment citation (Council of Ministers Resolution 508 vs Royal Decree M/76, both candidates preserved) and the corrected off-by-one recount of the prior research pass's own اصلية/معدلة narrative summary; v87: fnc-001..002 finance-companies-law (Royal Decree M/51, 1433H), BOE-WAYBACK-PRIMARY tier (a Wayback Machine archive of the BOE portal page as primary, cross-verified via normalized programmatic diff against bfc.gov.sa's official PDF, OCR'd, and nezams.com's HTML transcription, zero substantive discrepancies for the 40 original articles) — see track notes for the per-article variation flag on the 2024 amendment (Royal Decree M/272), whose replacement text rests on secondary sources only, and the general non-specific Article 38 repeal clause deliberately not modeled in the supersession graph; v88: chi-001..002 cooperative-health-insurance-law (Royal Decree M/10, 1420H), BOE-WAYBACK-ARCHIVE tier (a Wayback Machine snapshot of the BOE portal page cross-verified byte-for-byte against nezams.com's HTML transcription, zero substantive discrepancies across 17 unamended articles and both the 1420H and 1425H states of the 2 amended articles) — see track notes for the per-article variation flag on Article 4's 1440H amendment (single-sourced from nezams.com alone) and the distinction from this corpus's already-ingested insurance_control_law, a separate more general statute; v89: hcp-001..002 healthcare-professions-law (Royal Decree M/59, 1426H), BOE-WAYBACK-ARCHIVE tier (a Wayback Machine snapshot of the BOE portal page fetched via https://, live BOE unreachable, cross-verified against a live nezams.com fetch, 42 of 44 articles with zero differences, structurally corroborated against moh.gov.sa's own consolidated PDFs) — see track notes for the confirmed dual-repeal of the prior Physicians/Dentists Law (M/3, 1409H) and Pharmacy Law (M/18, 1398H), both modeled as new supersession-graph edges, and the pending-but-not-yet-enacted proposed Article 4 bis, documented but not ingested; v90: fls-001..002 finance-lease-law (Royal Decree M/48, 1433H), BOE-WAYBACK-ARCHIVE tier triple-verified (a Wayback Machine snapshot of the BOE portal page fetched via https://, live BOE unreachable, cross-verified against nezams.com's live transcription and rulebook.sama.gov.sa's own official Arabic/English PDFs, agreement on all 28 articles) — see track notes for the confirmed absence of any predecessor-repeal clause, a documented negative finding, and the distinction from this corpus's already-ingested finance_companies_law, a separate more general statute; v91: mar-001..002 maritime-commercial-law (Royal Decree M/33, 1440H), BOE-WAYBACK-ARCHIVE tier triple-verified (a Wayback Machine snapshot of the BOE Arabic law page and BOE's own official English-translation PDF, both cross-verified against nezams.com, 381 of 391 articles matching exactly) — see track notes for the confirmed dual-repeal at Article 391 and the independently-verified fix of a nezams.com content-duplication bug across Articles 316-325, plus a sanity-query collision fix that re-pointed the unified-index SANITY list's copyright art-22 query to a more distinctive substring after Article 385's generic penalty-clause boilerplate began mis-routing to it); v92: gad-001..002 gcc-anti-dumping-law (Royal Decree M/30, 1427H), TIER_4 mixed-confidence tier (one official BOE-via-Wayback primary source, partial qistas.com structural cross-check for Articles 1-3 only) — see track notes for the major unresolved discrepancy: multiply-corroborated secondary evidence indicates a 2013 amendment (Royal Decree M/7, 1434H) may have superseded and restructured this law, but BOE's own primary catalog page shows no trace of it across two Wayback snapshots ~20 months apart, so this track ingests BOE's verified 17-article original text and flags, rather than silently resolves, this live sourcing risk; v93: acc-001..002 accounting-auditing-law (Royal Decree M/59, 1442H), TIER_1 (BOE-via-Wayback archive cross-verified against SOCPA's own official PDF and qanoonsa.com) — see track notes for the confirmed repeal of the predecessor Law of Certified Public Accountants (M/12, 1412H, doubly confirmed via that predecessor's own BOE status of لاغي), a genuinely confirmed BOE main-body staleness for 5 amended articles (not a reachability artifact, resolved via BOE's own changelog popup cross-verified against SOCPA's PDF), and a has_per_article_variation flag on Article 1 for a further, more recent amendment sourced only from SOCPA's PDF and qanoonsa.com with no BOE confirmation at all; v94: naz-001..002 nazaha-law (Royal Decree M/25, 1446H), TIER_2 (BOE-via-Wayback two byte-identical snapshots ~15.5 months apart, a third independent time-point via a FAOLEX mirror of the same BOE page, cross-verified against nezams.com partial and qanoonsa.com full structural review) — see track notes for the confirmed repeal of the predecessor National Anti-Corruption Commission's organizing resolution (CoM Resolution 165, 1432H) and a partial repeal of the Civil Service Discipline Law (M/7, 1391H, Article 47 surviving), plus a critical cross-track finding: this law's own enacting decree amends the already-ingested anti_bribery_law track's Articles 17/21 wording, which that track's own text has not yet incorporated, flagged for a dedicated follow-up correction pass rather than resolved here; a dedicated re-verification pass this session checked laws.boe.gov.sa (9 Wayback snapshots spanning pre/post-M/25-enforcement), nezams.com, ramilawyer.sa, and a dated Oct 2025 professional-society compilation, finding no confirmation that the substitution has surfaced in anti_bribery_law's actual text, so its Articles 17/21 remain unchanged pending future re-verification; v95: awq-001..002 awqaf-law (Royal Decree M/11, 1437H), TIER_1 (BOE-via-Wayback six independent snapshots spanning 2019-2025, cross-verified against web.awqaf.gov.sa's own scanned original signed decree and nezams.com) — see track notes for the confirmed repeal of the predecessor Supreme Awqaf Council System (M/35, 1386H) and two genuinely-confirmed BOE main-body staleness anomalies (Articles 6 and 21) resolved via BOE's own amendment changelog rather than the stale main body, following the accounting_auditing_law precedent for this exact failure mode; Article 6's inconsistency between the changelog's own quoted 'before' text and the actual historical wording is flagged as unresolved, not hand-merged; v96: sen-001..002 saudi-engineers-law (Royal Decree M/36, 1423H), TIER_1 (BOE-via-Wayback three independent snapshots spanning 2019-2025, cross-verified against the Saudi Council of Engineers' own official website saudieng.sa's own three snapshots and an Asharq Al-Awsat press aggregation) — see track notes for a confirmed negative repeal finding (no predecessor engineering-council law), two genuinely-confirmed BOE-and-official-website main-body staleness anomalies (Articles 1 and 6, both resolved via BOE's own changelog rather than the stale main body, following the accounting_auditing_law/awqaf_law precedent), and the decree-number collision with a separate, currently-in-force companion practice/licensing law (نظام مزاولة المهن الهندسية, a DIFFERENT Royal Decree M/36 dated 19/4/1438H) flagged as the strongest candidate for a dedicated future track, not ingested this pass; v97 (muc-001..002): municipal-councils-law (Royal Decree M/61, 1435H), TIER_1 (BOE-via-Wayback six independent snapshots spanning 2019-2025, zero text diffs and zero logged amendments throughout, cross-verified against the Ministry of Municipal, Rural Affairs and Housing's own official website momah.gov.sa's two independently-dated official PDFs and nezams.com) — see track notes for a confirmed, narrowly-scoped partial repeal (Article 68 repeals only four named provisions of the predecessor Law of Municipalities and Villages, M/5, 1397H, not a full supersession), a documented zero-amendment stability finding (the inverse of this corpus's recurring stale-changelog pattern), and a preserved verbatim Chapter 10 heading spelling anomaly ('مخلفات' instead of the substantively-expected 'مخالفات'); v98 (prs-001..002): press-law (Royal Decree M/32, 1421H), TIER_1 (a near-live Wayback Machine snapshot of the BOE portal, 26 Feb 2026, structurally cross-verified against the Ministry of Media's own official PDF media.gov.sa and WIPO Lex, plus nezams.com/qanoonsa.com) — see track notes for a currency check that confirmed this law remains current over a still-unenacted comprehensive draft Media Law, a confirmed full repeal of the predecessor 1982 Press Law (M/17, 1402H), and a genuinely confirmed BOE main-body staleness for 6 amended articles (Articles 5, 9, 36, 37, 38, 40), resolved via BOE's own changelog rather than the stale main body, following the accounting_auditing_law/awqaf_law precedent; v99 (epl-001..002): engineering-practice-law (Royal Decree M/36, 1438H), TIER_1 (BOE-via-Wayback three independent snapshots spanning 2019-2026, byte-identical main-body text throughout, cross-verified against the Saudi Council of Engineers' own official website saudieng.sa's own hosted PDF and qanoonsa.com/qanoniah.com) — see track notes for a re-confirmed decree-number collision with saudi_engineers_law (both bear the bare number M/36 at hijri dates ~15 years apart), a confirmed negative repeal finding (zero repeal-language matches anywhere in the text), and a genuine three-way unresolved discrepancy at Article 1 (BOE's own changelog, BOE's own stable main body, and saudieng.sa's current PDF each show a different supervising-ministry wording) resolved by ingesting BOE's own stable text rather than fabricating a merge, following the awqaf_law Article 6 precedent; v100 (nat-001..002): nationality-law (Royal Will No. 8/20/5604, 1374H), TIER_2 (BOE-via-Wayback three independent snapshots, live BOE unreachable, cross-checked against nezams.com and independent news corroboration -- reclassified down from the research agent's own self-reported TIER_1 since nezams.com is a secondary aggregator and the news outlets are secondary/tertiary corroboration, not a second genuinely official/primary source, following the nazaha_law precedent) — see track notes for a confirmed full repeal of the 1357H predecessor nationality system and the separate Hejazi/Hejazi-Najdi nationality regulations at Article 28, a genuinely confirmed BOE main-body staleness for 11 amended articles resolved via BOE's own per-article changelog popups (a clean-incorporation pattern following the press_law/accounting_auditing_law precedent), and Article 61 مكرر's substantive text, deliberately excluded rather than fabricated since it could not be recovered; v101 (res-001..002): residency-law (Royal/Supreme Order 17/2/25/1337, 1371H), TIER_3 (BOE does not index this 1371H law at all -- only its unrelated 1440H namesake, Premium Residency Law M/106 -- and MOI's own hosted PDF was unreachable both live and via Wayback; rests instead on a cross-verified secondary reproduction of the officially-circulated compiled text agreeing word-for-word across mohamah.net x rakadvocate.blogspot.com x islamport.com) — see track notes for a general, non-specific Article 64 repeal clause naming no prior statute (a confirmed negative finding, no supersession-graph edge modeled), an Article 37 repeal preserved not deleted, 4 مضافة articles, and Article 61 مكرر's confirmed-added-but-unrecoverable text deliberately excluded rather than fabricated; v102 (csl-001..002): civil-status-law (Royal Decree M/7, 1407H), TIER_2 (BOE-via-Wayback seven independent snapshots, live BOE unreachable, cross-checked against qanoonsa.com's presentation of Council of Ministers Resolution 805 and nezams.com; reclassified down from the research agent's own self-reported TIER_1 since qanoonsa.com is a private legal-aggregator portal, not a government site, following the nationality_law/nazaha_law precedent) — see track notes for a confirmed dual repeal of two separately-named 1358H/1382H predecessors at Article 95 (one temporary carve-out preserved, not repealed), and a genuinely confirmed BOE main-body staleness for 24 amended articles resolved via BOE's own per-article changelog popups, a clean-incorporation pattern; v103 (fod-001..002): food-law (Royal Decree M/1, 1436H), TIER_2 conservative (ONE official/primary source, an SFDA-published PDF visually transcribed page-by-page, since laws.boe.gov.sa was completely unreachable both live AND via the Wayback Machine this pass; cross-checked against saudipedia.com and FAOLEX but not a second independently-sourced full copy of the statute, honestly flagged rather than inflated) — see track notes for a confirmed negative repeal finding at Article 45 (generic conflict-only clause naming no instrument, no supersession-graph edge modeled) and Article 1 (تعريفات) deliberately excluded since its text could not be recovered from any source, not fabricated; v104 (hsy-001..002): health-system-law (Royal Decree M/11, 1423H), TIER_3 (laws.boe.gov.sa unreachable both live and via the Wayback Machine this pass; two independent secondary sources cross-verified instead -- nezams.com full verbatim text and qanoonsa.com's raw text of Council of Ministers Resolution 151, an actual Umm Al-Qura Gazette reproduction, not a nezams.com mirror) — see track notes for a confirmed negative repeal finding at Article 19 (generic conflict-only clause naming no instrument, no supersession-graph edge modeled) and Article 16's undocumented-insertion-point amendment (Resolution 151, 1444H) deliberately not merged into the article text, an honest gap rather than a fabricated insertion; v105 (dlr-001..002): domestic-labor-regulation (Ministerial Decision No. 40676, 1445H), TIER_2 (BOE's own dedicated lawId page for this topic confirmed genuinely stale across 18+ months of Wayback snapshots, still showing only the superseded 310/1434H predecessor; PRIMARY source hrsd.gov.sa, the issuing Ministry's own official site, cross-checked against qanoonsa.com and lexismiddleeast.com, both private-aggregator secondary sources not counted as a second independent official source) — see track notes for a confirmed named repeal of the 310/1434H predecessor and Article 33's genuine source-PDF truncation, honestly flagged text_complete=False rather than completed or guessed; v106 (tdl-001..002): travel-documents-law (Royal Decree M/24, 1421H), TIER_2 (BOE-via-Wayback three independent snapshots x nezams.com/qistas.com secondary, plus an official Umm Al-Qura Gazette cross-check for the Royal Decree M/11 1443H amendment specifically -- that subset alone reaches TIER_1-caliber confidence, flagged has_per_article_variation, while the rest of the law rests on BOE plus private-aggregator secondary sources only) — see track notes for a confirmed scoped/partial repeal at Article 13 (only the travel-document-related provisions of the 1358H Passports System predecessor, not a blanket repeal) and two genuine internal BOE-source anomalies at Articles 6 and 10, preserved/resolved transparently rather than silently; v107 (nca-001..002): cybersecurity-authority-law (Royal Order 6801, 1439H), TIER_2 (no laws.boe.gov.sa page for this exact statute could be located this pass; PRIMARY source instead the National Cybersecurity Authority's own official site nca.gov.sa, a PDF OCR-transcribed via Tesseract 5 to work around a confirmed systematic letter-transposition text-layer artifact, cross-verified against qistas.com and saudipedia.com) — see track notes for a confirmed negative repeal finding at Article 15 (generic conflict-only clause naming no instrument, no supersession-graph edge modeled) and a document-level amendment by Royal Order 7053 (1443H) honestly not attributed to any specific article, an honest gap rather than a guessed one; v108 (nce-001..002): cybersecurity-authority-enablers (Royal Decree م/117, 1446H), TIER_2 (no laws.boe.gov.sa page for this exact instrument could be located this pass; PRIMARY source instead nca.gov.sa's own official PDF, sharing the parent statute's own confirmed letter-transposition text-layer artifact, OCR-transcribed via Tesseract 5, cross-verified against qanoonsa.com's three independent pages and uqn.gov.sa's topical gazette indexing) — see track notes for a genuine structural anomaly (seven بند clause divisions instead of numbered مواد, a first for this corpus), a confirmed negative repeal finding at its own final بند (سابعاً), and an independently re-confirmed finding that this instrument neither amends nor repeals any مادة of the parent cybersecurity_authority_law statute; v109 (prm-001..002): premium-residency-law (Royal Decree M/106, 1440H), TIER_1_PRIMARY_MULTI_SOURCE (laws.boe.gov.sa live portal unreachable this pass, but six independent Wayback Machine snapshots of BOE's own dedicated lawId page spanning 2019-2025 cross-verified word-for-word against misa.gov.sa's own hosted consolidated-text PDF, Ministry of Investment -- two independent official government sources agreeing) -- see track notes for a confirmed negative repeal finding at Article 14 (names no predecessor at all, a wholly new residency category distinct from this corpus's already-ingested residency_law), Article 8's repeal by M/84 (1445H) with its pre-repeal text preserved not deleted, and the disclosed single-word discrepancy between BOE and MISA at Article 2(e); v110 (tdr-001..002): travel-documents-regulation (Ministerial Resolution 4203, 1447H), TIER_3 honest (no laws.boe.gov.sa lawId page at all for this instrument; moi.gov.sa/gdp.gov.sa unreachable; uqn.gov.sa domain-reachable but its specific gazette page not located this pass; PRIMARY qanoonsa.com raw-HTML direct fetch, Wayback-stable since 16 Apr 2026, cross-checked at the decree-metadata level against ncar.gov.sa, a genuine government archival body, and qanoniah.com, private indexing-level only) -- see track notes for a confirmed FULL repeal of the 1422H predecessor Implementing Regulation (Decision 7/waw-zay) via Article 52, a genuine positive finding unlike the parent travel_documents_law track's own generic-repeal precedent, and Article 37(3)'s confirmed source-side typo ('مي نع' for 'يمنع') preserved verbatim not silently corrected; v111 (nrg-001..002): nationality-regulation (Ministerial Decision 74/زو, 1426H), TIER_2 (laws.boe.gov.sa hosts no dedicated page at all for this Implementing Regulation; PRIMARY moi.gov.sa fetched via three independent Wayback Machine snapshots spanning 2011-2024, byte-identical sha256 across all 13 years, cross-verified against nezams.com and alriyadh.com's 2005G contemporaneous full-text reproduction, which independently resolved this corpus's own prior gap-map estimate of ~25 articles to the confirmed true count of 35) -- see track notes for Article 28's confirmed repeal (deleted circa March 2023 by Minister of Interior decision following Royal Decree M/88's transfer of nationality-grant authority, independently confirmed by 5+ news outlets, moi.gov.sa's own PDF confirmed genuinely stale and still showing the pre-repeal text over a year later) and the confirmed negative finding that this Regulation names no predecessor instrument of its own; v112 (hsr-001..002): health-system-regulation (Ministerial Decision 30/69181, 1424H), TIER_4 (laws.boe.gov.sa hosts no dedicated page at all and istitlaa.ncc.gov.sa is confirmed unreachable via three independent channels, Wayback blocked at the egress-policy level; PRIMARY qanoniah.com's public API with a confirmed server-enforced 10-item preview cap, covering ONLY parent Law Articles 2-11 with non-contiguous numbering keyed to the parent law's own article numbers) -- see track notes for the confirmed PARTIAL coverage (Article 1 and Articles 12-19, including the heavily-amended Article 16 Health Services Council, honestly excluded not fabricated) and the confirmed negative finding that this Regulation names no predecessor instrument of its own; v113 (fdr-001..002): food-regulation (SFDA Board Resolution 3-16-1439, 1439H, as amended by Resolution 4/44, 1446H), TIER_2 (laws.boe.gov.sa checked first but unreachable this pass and confirmed to have no dedicated lawId page for this Implementing Regulation at all; PRIMARY sfda.gov.sa born-digital PDF, 2025-06 upload, cross-verified against qanoonsa.com and qistas.com) -- see track notes for the confirmed negative finding that this Regulation names no predecessor instrument of its own, three systematic font ligature-reversal extraction defects fixed via an individually-verified substitution dictionary, and the final article's own printed header mislabeled '(58)' for 85, preserved verbatim not silently renumbered; v114 (ele-001..002): electricity-law (Royal Decree M/44, 1442H), TIER_3 (laws.boe.gov.sa unreachable this pass, connection reset / HTTP 503, Wayback egress-blocked; PRIMARY nezams.com, a single clean born-digital HTML full-text aggregator page, no scan/OCR/ligature defects, cross-verified metadata against BOE/Umm Al-Qura via WebSearch, Lexis Middle East, and SERA) -- see track notes for the confirmed named repeal-and-replace of the older Electricity Law (Royal Decree M/56, 1426H) via this Law's own Article 23, and the two Implementing Regulations (Minister and Council level) identified but not ingested this pass; v115 (wat-001..002): water-law (Royal Decree M/159, 1441H), TIER_3 (nezams.com independent aggregator, PRIMARY; laws.boe.gov.sa has a dedicated lawId page but was unreachable this pass, HTTP 503, Wayback egress-blocked; decree identity/Article 74 text/SAR-20m penalty ceiling/17-chapter structure cross-verified via WebSearch indexing of BOE's own content) -- see track notes for the confirmed named repeal-and-replace of THREE predecessor laws (M/22 1391H, M/34 1400H, M/6 1421H) via this Law's own Article 75, and the two Implementing Regulations plus the separate Saudi Water Code identified but not ingested this pass; v116 (vtr-001..002): vat-regulation (ZATCA Board of Directors Resolution No. (3839), 14 Dhul-Hijjah 1438H, Tenth Edition consolidating 11 amending Board resolutions through Nov 2024), TIER_3 (laws.boe.gov.sa has no dedicated lawId page for this Board-level regulation; PRIMARY zatca.gov.sa official consolidated PDF, dual PyMuPDF-geometric x Tesseract-OCR extraction reconciled to work around a systematic bidi word-order defect) -- see track notes for the independently re-resolved cover-date anomaly (printed '14 نوفمبر 2016م' corrected to the true Hijri-derived 5 September 2017G) and the confirmed negative finding that this Regulation names no separate predecessor beyond the parent VAT Law; v117 (itr-001..002): income-tax-regulation (Ministerial Resolution No. (1535), 11/6/1425H, consolidated through 13 ministerial amendments to Resolution 25, 8/1/1445H), TIER_3 (laws.boe.gov.sa has no dedicated lawId page for this Implementing Regulation, only the base Law; PRIMARY two cross-verified government copies -- ZATCA official consolidated PDF x gstc.gov.sa INCOM2.pdf, both headers confirming the exact founding date the parent income_tax_law track could not pin down) -- see track notes for the inverse-of-parent natural-gas risk (25 articles of the old IRR regime formally repealed by Resolution 2568 but preserved in full text with a تم حذف المادة footnote) and the confirmed negative finding that this Regulation names no separate predecessor beyond the parent Law; v118 (agr-001..002): agriculture-law (Royal Decree M/64, 10/8/1442H), TIER_3 (laws.boe.gov.sa has a dedicated lawId page but was unreachable this pass, HTTP 503, Wayback egress-blocked; PRIMARY nezams.com single clean aggregator, metadata and the flat 37-article/no-chapter structure cross-verified against the official MISA English PDF) -- see track notes for the confirmed named repeal of FIVE predecessor instruments (M/9 1408H, M/13 1424H, M/15 1431H, M/55 1435H, CoM Rules 96 1405H) via this Law's own issuing decree (clause ثانياً, not any numbered article), and its own Implementing Regulation identified but not ingested this pass; v119 (cmr-001..002): competition-regulation (GAC Board Decision 337, 25/1/1441H), TIER_2 (dual independent source -- qanoniah.com clean API primary text x WIPO Lex official Arabic PDF letters, for the captured scope only) -- see track notes for the deliberate partial scope (Articles 1-5 of 90 ingested, remaining 85 disclosed pending not fabricated, due to a lossy digit-CMap defect in the only complete fetchable Arabic source) and the confirmed supersession of the 2014 Implementing Regulation (Competition Council Decision 126, 4/9/1435H); v120 (amr-001..002): aml-regulation (Administrative Decision 266507, 9/12/1447H), TIER_3 (aml.gov.sa scanned PDF reconciled with qanoniah.com born-digital API for 10 of 25 articles, remaining 15 OCR-extracted and visually adjudicated) -- see track notes for the confirmed negative repeal finding (supersession of the prior legal regime is derivative via the parent aml_law's own Article 51, not an in-Regulation repeal clause) and the deliberately-excluded genuinely distinct older 1430H regulation; v121 (ptr-001..002): patent-regulation (KACST President Resolution 161-2-3607329, 30/12/1436H), TIER_3 (official SAIP-letterhead Arabic PDF on WIPO Lex, dual independent extraction pipelines reconciled, structural cross-check via WIPO Lex metadata and qanoonsa.com) -- see track notes for the confirmed negative repeal finding (first Implementing Regulation under the current Patents Law M/27) and the disclosed staleness (a later 2024 amendment not reflected in this 2019-consolidated text, mirroring the base patent_law track); v122 (ecr-001..002): ecommerce-regulation (Ministerial Resolution 200, 19/5/1441H), TIER_1 (the issuing Ministry's own official born-digital regulations page cross-verified word-for-word against the Ministry's own official scanned PDF, plus qanoniah.com/lexismiddleeast.com/argaam.com/mithaq.com.sa) -- see track notes for the confirmed negative repeal finding (the base E-Commerce Law itself only dates to 1440H, too new for any predecessor Regulation to have existed); v123 (fcr-001..002): franchise-regulation (Minister of Commerce Resolution 591, 18/9/1441H), TIER_2 (PRIMARY franchising.sa Umm Al-Qura gazette reproduction cross-verified VERBATIM against aunklaw.com for all 16 articles, plus lexismiddleeast.com for structure) -- see track notes for the confirmed negative repeal finding and the genuine annex-only amendment (disclosure-document element 13 later deleted, disclosed and preserved verbatim in its original form, not silently applied); v124 (tfr-001..002): traffic-regulation (Ministerial Resolution 2249, 10/3/1441H), TIER_3 (PRIMARY official MOI scanned document, dual vision+OCR extraction pipeline, cross-verified verbatim against qanoniah.com born-digital text for Articles 1-8 only) -- see track notes for the CONFIRMED named-predecessor repeal (Ministerial Resolution 7019, 3/7/1429H, replaced per the Resolution's own verbatim preamble clause), a genuine positive supersession finding rather than this window's more common confirmed-negative pattern; v125 (eia-001..002, evp-001..002, epm-001..002, eaq-001..002): the four environmental Implementing Regulations built this pass -- environmental_inspection_audit (Ministerial Decision 15116190, wholly replacing 393691/1/1442, TIER_2), environmental_violations_penalties (Ministerial Decision 15101619, wholly replacing 312186/1/1442, TIER_2), environmental_permits (Minister Decision 43615/3/1/1442, TIER_1 -- Umm Al-Qura Gazette issue 4888 in two independent official renderings, HTML x born-digital PDF, 99.66% word-level match), and environmental_air_quality (Minister Decision 512258/1/1442, TIER_2 -- mewa.gov.sa official PDF x qanoniah.com) -- each a separate topical instrument under the Environmental Law's family of ~15 distinct Implementing Regulations, each its own corpus key; inspection_audit and violations_penalties are both confirmed self-supersessions of their own prior decision numbers (recorded as repeals_full edges), permits and air_quality are confirmed negative repeal findings; v126 (esp-001..002, efe-001..002): two more environmental Implementing Regulations -- environmental_service_providers (Ministerial Decision 1515009/1, wholly replacing 582979/1/1442, TIER_2, confirmed self-supersession recorded as a repeals_full edge) and environmental_fees (Minister Decision 618660/1/1442, TIER_2, qanoniah.com primary text with multi-source citation cross-check, confirmed no named-predecessor repeal, Annex-1 fee-ceiling table documented as excluded) -- each its own corpus key under the Environmental Law's family of ~15 distinct Implementing Regulations; v127 (rtt-001..002): rett-law (Royal Decree M/84, 19/3/1446H), TIER_2 (BOE lawId page retrieved via r.jina.ai read-proxy after the live page returned HTTP 503, cross-verified against nezams.com and qanoonsa.com non-government secondaries) -- see track notes for the confirmed GENERIC repeal clause at Article 20(2), naming no predecessor, with Royal Order A/84 (1442H) disclosed as historical context only, not a Law-text-asserted repeal, so no supersession-graph edge is modeled; v128 (unv-001..002): universities-law (Royal Decree M/27, 2/3/1441H), TIER_2 (BOE unreachable this pass and Wayback egress-blocked; PRIMARY bibliotdroit.com born-digital text cross-verified article-by-article, all 58, against the administering authority's own official cua.gov.sa PDF, structure re-confirmed by a third source, moe.gov.sa) -- see track notes for the CONFIRMED named-predecessor repeal of نظام مجلس التعليم العالي والجامعات (M/8, 4/6/1414H) via Article 57, disclosed as a PHASED, not instantaneous, replacement per the Royal Decree's own transitional clauses keeping the predecessor law in force for universities not yet covered; v129 (prv-001..002): privatization-law (Royal Decree M/63, 5/8/1442H), TIER_2 lower end (BOE unreachable this pass, Wayback egress-blocked; PRIMARY nezams.com full text, cross-verified against an official misa.gov.sa/NCP PDF confirming article count/flat structure/verbatim Articles 44-45 -- a genuine but partial official cross-check, disclosed not inflated) -- see track notes for Article 45's GENERIC repeal clause, with the named repeals of prior CoM/Supreme Economic Council instruments sitting in the accompanying CoM Resolution 436 (a different instrument) rather than the Law's own text, so no supersession-graph edge is modeled; v130 (anh-001..002): antiquities-heritage-law (Royal Decree M/3, 9/1/1436H), TIER_3 (BOE unreachable this pass, Wayback egress-blocked; PRIMARY nezams.com born-digital text corroborated by a BOE-content print PDF hosted on media.unesco.org -- an international body's hosting, not a Saudi government domain, so honestly kept at TIER_3 rather than inflated -- plus the Umm Al-Qura Gazette for the M/67 amendment's scope specifically) -- see track notes for the CONFIRMED named-predecessor repeal of نظام الآثار (M/26, 23/6/1392H) via Article 92, and the SIX separate amendment instruments consolidated without silent merging (pre-amendment text preserved in history for each); v131 (cpl-001..002): child-protection-law (Royal Decree M/14, 3/2/1436H), TIER_3 (BOE unreachable this pass, Wayback not attempted egress-policy-blocked; PRIMARY nezams.com full text, decree identity/5-chapter structure/original 25-article text independently confirmed by an official MOJ Adl-journal PDF used for identity/structure only, not letter-for-letter, due to a bidi-reordering extraction defect) -- see track notes for the CONFIRMED amendment (CoM Resolution 427/Royal Decree M/72, 1443H, amending Articles 12/15/19/23 and adding Article 23-mukarrar's criminal penalties), the confirmed absence of any repeal clause (a founding statute), and the disambiguation from juveniles_law and the separate protection_from_abuse_law candidate; v132 (pfa-001..002): protection-from-abuse-law (Royal Decree M/52, 15/11/1434H), TIER_2 (BOE unreachable this pass, Wayback egress-blocked; PRIMARY an official Ministry of Finance regulations-library PDF used directly as the governing text, cross-checked verbatim against nezams.com) -- amendment to Articles 7/12/13 via the same 1443H instrument that amended child_protection_law, independently confirmed via the Umm Al-Qura Gazette; no repeal clause of any kind found (a founding statute), distinct from child_protection_law; v133 (ngo-001..002): associations-ngo-law (Royal Decree M/8, 19/2/1437H), TIER_3 (BOE two conflicting lawId values unreachable this pass; PRIMARY nezams.com full text, independently cross-checked against a menarights.org PDF for article count and the closing articles' verbatim text) -- Article 1 amended (CoM Resolution 618's two new definitions), Articles 7/25/38 explicitly exempted from Resolution 618's horizontal substitution; CONFIRMED named repeal of the predecessor Charitable Associations and Institutions Regulation (CoM Resolution 107, 25/6/1410H) via Article 43; v134 (avm-001..002): audiovisual-media-law (Royal Decree M/33, 25/3/1439H), TIER_2 (BOE unreachable this pass, Wayback refused by the fetch tool itself; PRIMARY nezams.com full text strongly cross-checked against an archived BOE portal scan (cyrilla.org) and the official BOE English translation (misa.gov.sa)) -- Article 1 amended (CoM Resolution 374's terminology substitution), no repeal of any predecessor found (generic conflict clause only), distinct from press_law; v135 (spt-001..002): sports-law (Royal Decree M/121, 10/6/1447H), TIER_3 (BOE and mos.gov.sa both unreachable this pass, Wayback egress-blocked; PRIMARY nezams.com full text cross-checked verbatim against qanoonsa.com, decree identity confirmed via the Umm Al-Qura gazette's own JSON API) -- brand-new founding statute (in force since ~June 2026), all 97 اصلية; CONFIRMED named repeal of the Basic Law of Sports Federations and the Saudi Arabian Olympic Committee (M/55, 19/10/1407H) via Article 96; v136 (smk-001..002): anti-smoking-law (Royal Decree M/56, 28/7/1436H, approving Council of Ministers Resolution 90, 23/3/1434H), TIER_2 (BOE unreachable this pass, a confirmed Wayback snapshot's content could not be fetched since web.archive.org is egress-blocked; PRIMARY an official Ministry of Health PDF used directly as the governing text, cross-checked verbatim against nezams.com and a bilingual cloudfront.net legislation PDF) -- flat 20-article statute (no chapters), all اصلية; no confirmed named-predecessor repeal (only a transitional continuation clause for unnamed prior agency rules, honestly not counted as a repeal per this corpus's verbatim-repeal-text standard); v137 (wpn-001..002): weapons-ammunition-law (Royal Decree M/45, 25/7/1426H, approving Council of Ministers Resolution 193, 24/7/1426H), TIER_2 (BOE live portal unreachable this pass, PRIMARY three independent Wayback snapshots of the same official portal (2019/2025/2026) cross-checked verbatim against nezams.com for all 63 articles) -- 63 articles/7 topical sections, 56 اصلية/7 معدلة across 4 separate amendment events; CONFIRMED named repeal of the prior Weapons and Ammunition Law (M/8, 19/2/1402H) via Article 62; fixing this expansion's own irh-002 gold query, which collided with the new weapons_ammunition content on an overly-generic snippet, by switching to a WMD-specific sub-clause unique to the terrorism law's Article 39; v138 (pdt-001..002): prison-detention-law (Royal Decree M/31, 21/6/1398H, approving Council of Ministers Resolution 441, 8/6/1398H), TIER_3 (BOE and an official MOI PDF both unreachable this pass, web.archive.org not attempted since the fetch tool itself reported it cannot reach that host; PRIMARY nezams.com cross-verified verbatim against islamport.com) -- flat 31-article statute (no chapters), 28 اصلية/3 معدلة (Article 4 uniquely amended twice); no predecessor-repeal assertion made (unconfirmed either way given the statute's age, not a settled founding-statute claim); v139 (cvd-001..002): civil-defense-law (Royal Decree M/10, 10/5/1406H, approving Council of Ministers Resolution 25, 23/1/1406H), TIER_3 (BOE and istitlaa.ncc.gov.sa both unreachable this pass, web.archive.org environment-blocked not bypassed; PRIMARY mohamah.net cross-verified verbatim against islamport.com) -- flat 36-article statute (no chapters), 34 اصلية/2 معدلة (Articles 5, 28 -- original 1406H text preserved, current post-amendment text honestly UNCONFIRMED, not fabricated); no named-predecessor-law repeal (Article 35 generic conflict clause only, a confirmed negative finding); v140 (cop-001..002): cooperative-societies-law (Royal Decree M/14, 10/3/1429H, approving Council of Ministers Resolution 73, 9/3/1429H), TIER_3 (BOE unreachable this pass and Wayback refused by the fetch tool itself; PRIMARY cross-verified across four independent sources plus a structural confirmation from mohamah.net) -- 44 articles across 9 أبواب, all اصلية, no enacted amendment; CONFIRMED named repeal of the prior Cooperative Societies System (Royal Decree 26, 25/6/1382H) and its Subsidy Bylaw (CoM Resolution 419) via Article 43; v141 (bcd-001..002): building-code-law (Royal Decree M/43, 26/4/1438H, approving Council of Ministers Resolution 241, 25/4/1438H), TIER_1 (laws.boe.gov.sa live returned HTTP 503, but a very recent (2026-01-14) web.archive.org snapshot of the live BOE page was retrieved directly, containing the full text plus amendment-history popups; cross-verified per amendment against an independent Saudi Council of Engineers PDF, the Umm al-Qura official gazette, and qanoonsa.com) -- 16 articles, 12 اصلية/4 معدلة (Articles 1, 8, 9, 15 across three amendments M/15, M/88, M/204), confirmed no repeal (generic conflict clause naming no prior instrument -- founding statute for code application); v142 (psl-001..002): product-safety-law (Royal Decree M/36, 29/1/1446H, approving Council of Ministers Resolution 93, 24/1/1446H, Clause One), TIER_2 (decree number CORRECTED from the coverage-gap-map's unconfirmable M/148; an official Umm al-Qura Gazette notice confirms the decree and quotes Article 36 verbatim; full text from qanoonsa.com cross-checked against nezams.com; laws.boe.gov.sa unreachable this pass) -- 37 articles across 9 أبواب, all اصلية, confirmed no repeal (generic conflict clause naming no prior instrument -- new founding statute, distinct from the sibling Standards and Quality Law approved by the same joint decree's Clause Two); v143 (sql-001..002): standards-quality-law (Royal Decree M/36, 29/1/1446H, approving Council of Ministers Resolution 93, 24/1/1446H, Clause Two), TIER_2 (same decree correction as the sibling; an official Umm al-Qura Gazette notice confirms the decree and quotes Article 23 verbatim; full text from qanoonsa.com cross-checked against nezams.com with 2 words corrected in Article 1; laws.boe.gov.sa has a confirmed index entry but was unreachable live this pass) -- 24 articles across 7 أبواب, all اصلية, confirmed no repeal (generic conflict clause naming no prior instrument -- also distinct from SASO's own founding statute M/10 1392H); v144 (drl-001..002): disability-rights-law (Royal Decree M/27, 11/2/1445H, approving Council of Ministers Resolution 110, 6/2/1445H), TIER_3 (BOE has a dedicated lawId page but was unreachable this pass, web.archive.org confirmed egress-blocked and not bypassed, PRIMARY nezams.com cross-verified verbatim article-by-article against qanoonsa.com) -- 33 articles across 5 أبواب, all اصلية, CONFIRMED named-predecessor repeal of the old نظام رعاية المعوقين (M/37, 23/9/1421H) via Article 32, triple-corroborated including from CoM Resolution 110's own recitals; v145 (trl-001..002): tourism-law (Royal Decree M/18, 26/1/1444H, approving Council of Ministers Resolution 79, 25/1/1444H), TIER_2 (BOE has a dedicated lawId page but was unreachable this pass, web.archive.org refused/403 not bypassed, ORIGINAL full text from an official Ministry of Tourism PDF cross-checked verbatim against nezams.com, structurally cross-checked against the official BOE English translation) -- 19 articles, flat structure/no chapters, all اصلية, CONFIRMED named-predecessor repeal of the old Tourism Law (M/2, 9/1/1436H) via Article 18, double-confirmed from both directions; v146 (sqr-001..002, drr-001..002, asr-001..002): the three Implementing Regulations built this pass -- standards-quality-regulation (Minister of Commerce Decision No. 098, 18/5/1446H), TIER_1 (SASO's own official site and the Umm al-Qura Gazette's own API, both fetched directly, dual-primary, cross-verified against qanoonsa.com; laws.boe.gov.sa has no dedicated lawId page) -- 23 articles across 7 أبواب, all اصلية, no predecessor regulation (first Implementing Regulation under the base law); disability-rights-regulation (Authority Board Resolution No. 26, 29 Shawwal 1445H), TIER_2 (PRIMARY uqn.gov.sa direct HTML text cross-verified article-by-article against qanoonsa.com; a genuine 12-vs-11 chapter-count discrepancy with a third source is disclosed not silently resolved) -- 45 articles across 12 فصول, all اصلية, no predecessor regulation; and anti-smoking-regulation (founding resolution number/date NOT confirmed this pass -- a prior scan's assumption that Ministerial Resolution 797557/1441H was the founding issuance is corrected here, independently re-verified as a real AMENDMENT resolution instead), TIER_2 (PRIMARY official MOH 2019 PDF cross-checked against a 2017 WHO/EMRO edition via clause-by-clause diff to detect the 6 amended articles) -- 17 of 20 possible articles (14/15/17 intentionally absent, no content in either edition), 11 اصلية/6 معدلة, no predecessor-regulation repeal modeled since the founding instrument itself is unconfirmed; v147 (gel-001..002): general-education-law (Royal Decree M/36, 27/1/1448H, approving CoM Resolution 103, 22/1/1448H, issued the same day as this ingestion pass), TIER_2 (PRIMARY full text of all 68 articles fetched directly from the Umm al-Qura Official Gazette itself, officially corroborated at the fact level by the Saudi Press Agency, structurally cross-checked by independent press) -- 68 articles across 9 فصول, all اصلية, discovered via two independently-dispatched gap-map scan agents converging on an identical finding; NOT YET IN FORCE (Article 68: effective 180 days after gazette publication, ~mid-January 2027), disclosed explicitly rather than silently assumed; confirmed immediate repeal (phased 1-year transition) of the Adult Education and Literacy Law (M/22, 1392H) and 7 CoM-level school regulations, none of which are tracked instruments in this corpus so no supersession edge is modeled; v148 (cil-001..002, reb-001..002, srl-001..002, etc-001..002, eiv-001..002): five new tracks discovered via a fresh multi-modal coverage-gap-map sweep at the 193-track baseline -- credit-information-law (Royal Decree M/37, 5/7/1429H), TIER_2 (BOE Wayback sole official channel x nezams x saudipedia cross-verified, live BOE unreachable) -- 17 articles all اصلية, no predecessor repeal; real-estate-brokerage-law (Royal Decree M/130, 30/11/1443H), TIER_1-pattern (REGA official BOE-sealed scanned PDF visually verified plus OCR, cross-verified against qanoonsa/nezams) -- 24 articles all اصلية, confirmed named repeal of the 1398H Real Estate Offices Regulation via Article 22 (predecessor not tracked, no supersession edge); state-revenue-law (Royal Decree M/68, 18/11/1431H, as amended by M/5 1440H and M/93 1443H), distinct tier (BOE Wayback x nezams x qanoonsa) -- 32 articles (30 اصلية/1 معدلة/1 مضافة), confirmed named repeal of the 1359H predecessor via Article 30 (not tracked, no edge), explicitly excludes an unconfirmed July-2026 Council-of-Ministers-approved "update" whose promulgating instrument remains unfound; etec-law (Council of Ministers Resolution 108, 14/2/1440H, amended by Resolutions 693 1441H and 631 1445H), TIER_1 (two independent Wayback snapshots 18 months apart in full literal agreement) -- 18 articles (16 اصلية/2 معدلة), no predecessor repeal confirmed; einvoicing-regulation (ZATCA Board Decision 2-6-20, 4 Rabi al-Thani 1442H), TIER_2 (ZATCA official PDF x aflaksolutions mirror cross-verified, BOE has no dedicated page) -- 7 articles all اصلية, operates as part of vat_regulation per its own Article 2(B), no repeal; same text-first methodology throughout; v149 (pcb-001..002, sda-001..002): two new tracks discovered via a targeted, precision-requested deep-dive scan for NCA/SDAIA binding instruments -- pdpl-cross-border-transfer-regulation (SDAIA President Decision No. 1840, 27/2/1446H), TIER_1_PRIMARY_MULTI_SOURCE (SDAIA's own live portal x Umm al-Qura Gazette both fetched directly and matching verbatim, BOE unreachable) -- 9 articles all اصلية, supersession of a structurally distinct 2023 predecessor disclosed as a strong inference not an asserted fact; sdaia-organizational-arrangements (Council of Ministers Resolution 292, 27/4/1441H, amended by Resolution 195 15/3/1444H), TIER_2 (SDAIA's own official site PDF via the r.jina.ai reader-proxy, reconstructed via disclosed correction of a confirmed lam-alif-ligature-reversal extraction artifact, cross-checked against qistas.com/lexismiddleeast.com/almirkaz.com/qanoniah.com plus an independent Saudi Press Agency confirmation of the founding Royal Order A/471) -- 16 بنود (15 اصلية/1 معدلة), confirmed negative predecessor-repeal finding; same text-first methodology throughout; v150 (tnr-r1..tel-r1, 36 golds): the 36-track implementing-regulation merge batch (trade_names_regulation through telecommunications_regulation) — one gold per new track, each reused verbatim from the unified-index SANITY tuple already live-verified during pipeline wiring; caught and fixed a genuine cross-track bug in the process (17 of the 36 generators mistagged their own records' law_component as "law"/"regulation_family"/"implementing_regulation" instead of "regulation", silently colliding with their sibling base-law tracks under the same corpus key — found via this exact gold-query pass, since the eval's strict (corpus, law_component, article_number) match caught what the looser SANITY check could not; fixed in all 17 generators, unified index and all derived layers regenerated); v151 (cir-r1, pmsr-r1, bkcr-r1, fcr-r1, flr-r1, csr-r1, 6 golds): the 6-track SAMA-cluster/cooperative-societies merge batch (credit_information_regulation, payment_systems_regulation, banking_control_regulation, finance_companies_regulation, finance_lease_regulation, cooperative_societies_regulation) — one gold per new track, each reused verbatim from the unified-index SANITY tuple already live-verified during pipeline wiring, with law_component explicitly re-confirmed as "regulation" this pass (applying the lesson from v150's 17-track bug) before accepting each candidate, avoiding a repeat of that exact silent-collision blind spot; all 6 hit top-1 cleanly with no new misses; same text-first methodology throughout; v152 (bog-001, ppl-001, elcl-001, elcr-001, psr-001, fsr-001, pol-001, cgr-001, tvt-001, wml-001, fsl-001, dcr-001, 12 golds): the wave-4 merge batch (bog_enforcement_law, public_prosecution_law, elderly_care_law + elderly_care_regulation, private_schools_regulation, foreign_schools_regulation, postal_law, cma_corporate_governance_regulation, tvtc_organizational_statute, waste_management_law, fisheries_law, debt_collection_regulation), discovered via the 242-track coverage-gap-map scan (10 of 12 candidates confirmed buildable; a Mining Investment Law Implementing Regulation retry and a Digital Government Authority statute attempt were both honestly declined this pass — the former's only locatable text was explicitly framed as a public-consultation DRAFT (istitlaa.ncc.gov.sa), the latter's article-level text was unreachable across every channel tried, BOE/dga.gov.sa/Wayback/multiple proxies all blocked) — each gold independently confirmed by reading the article's own committed text first, then cross-checked via search_corpus_unified.py for a clear top-1 margin filtered to the correct corpus; verification tiers were independently re-derived from this corpus's strict 4-tier taxonomy rather than copied from each track's own informal self-label, correcting three tracks initially self-described as "TIER_1-candidate" down to their honest tier once cross-checked (elderly_care_law and cma_corporate_governance_regulation to TIER_2, both single-official-source-plus-secondary-only; debt_collection_regulation to TIER_4, single SAMA Rulebook source with English structural-only cross-check) and foreign_schools_regulation from a self-labeled TIER_2 down to TIER_3 (zero primary/official source was actually reached, resting entirely on two independent secondary sources agreeing); private_schools_regulation and fisheries_law were confirmed at TIER_1 on stricter review (the former via an independent page-by-page visual/OCR cross-pass of the same official MOE PDF, the latter via two BOE-Wayback snapshots six years apart in full literal agreement plus internal and external corroboration); the pre-existing agriculture_law→(untracked) repeal edge for the Living Aquatic Resources Law (M/9, 1408H) was updated to point at the newly-ingested fisheries_law track now that it exists in this corpus, rather than adding a duplicate edge; three further named-predecessor repeals were newly modeled (waste_management_law over the old Municipal Solid Waste Management Law M/48, stated in the new law's own Article 37; tvtc_organizational_statute over its predecessor M/30 via its own Article 12; cma_corporate_governance_regulation over CMA Board Resolution 1-212-2006, correcting that track's own commissioning brief which had mistakenly described the 2006 regulation as amended rather than fully superseded) and one more (postal_law over the old Postal Law M/4, 1406H) with the exact repealing article number left honestly unconfirmed; all 12 golds hit top-1 cleanly; same text-first methodology throughout; so that GTPL, all eight Labor tracks, the four Evidence tracks, Personal Status, Sharia Procedure, Criminal Procedure, Enforcement, Judiciary, Board of Grievances, Law Practice, Commercial Courts, Bankruptcy, Judicial Costs, Arbitration, Commercial Papers, Commercial Register, Trade Names, Commercial Agencies, Chambers of Commerce, Commercial Books, AML, Notarization, and the real-estate/terrorism/juveniles/whistleblower/judicial-companion families all keep their existing gold coverage unchanged. v153: wave-5 batch (isa-001, bnp-001, ofp-001, ccl-001, rec-001, acv-001, wlf-001, frs-001, mnh-001, odl-001, phi-001, hrp-001, osp-001, rega-001) — 14 new tracks spanning financial/real-estate/digital/health sectors from a fresh 254-track coverage-gap scan (Statute of the Insurance Authority; BNPL Regulation, SINGLE-SOURCE tier, SAMA Rulebook with no independent cross-check; Off-Plan Sale/"WAFI" Law, whose Implementing Regulation citation was independently confirmed but not built this pass, flagged as follow-up; Contractors Classification Law, repealing its predecessor M/18 via its own Article 19, font-defect corrected via triple cross-validation; Real Estate Contributions Law, TIER_1 dual-official-source; Certified/Accredited Valuers Law, downgraded to TIER_4 overall despite ~89% dual-primary-source coverage because 5 residual articles rest on a single uncorroborated source, per this corpus's "weakest meaningfully-sized portion" convention; White Land and Vacant Properties Fees Law, with an honestly-disclosed Article 3 sourcing gap; Frequency Spectrum Regulations, General Framework only, 6 technical annexes deliberately excluded, vision-read for lack of a text layer; Mental Health Care Law, a live but unconfirmable Council of Ministers amendment explicitly not incorporated; Human Organ Donation Law; Private Healthcare Institutions Law, repealing predecessor M/58 via its own Article 33 and newly discovering a 4th amendment (M/103, 1445H) beyond the 3 already known; High-Risk Professions Work Organization Regulation, TIER_1 dual-official-source; OSH Service Providers Licensing/Accreditation Regulation, TIER_4 mixed-confidence, Articles 1-29 primary-plus-dual-secondary but 30-38 secondary-only after a gazette CMS truncation; and the Statute of the General Authority for Real Estate (REGA), the 14th and final track, built on retry after a first attempt stalled on a slow OCR job — the retry used direct visual page-image reading of REGA's own 5 scanned PDFs instead, confirming REGA has no predecessor statute, a genuine negative finding). Two candidates from the same scan were honestly declined rather than fabricated: insurance_control_regulation (SAMA Rulebook's Insurance Sector section returned HTTP 403 across three independent fetch methods, all alternate sources dead/paywalled/JS-gated) and cloud_computing_regulation (source PDF gated behind a JS/anti-forgery download flow unobtainable headlessly, Wayback blocked this session, the one secondary aggregator with a copy paywall-gated with no server-rendered text). Each gold reused verbatim from the corresponding unified-index SANITY tuple, live-verified for a clear top-1 margin globally (not just within-corpus) via search_corpus_unified.py. Adding rega's organizational-statute boilerplate text surfaced two pre-existing routing collisions from generic "الهيئة" preamble language — awq-002 (awqaf_law article 9) and isa-001 itself (insurance_authority_statute article 2) both lost the global top-1 ranking to rega articles 8/2 respectively; both were corrected in place to distinctive alternative articles (awqaf article 5's enumerated duties list; insurance_authority_statute article 3's sector-specific mandate text) and re-verified clean, with the unified-index SANITY tuples updated identically so gold and SANITY stay in lockstep. Verification tiers independently re-derived from this corpus's strict 4-tier taxonomy for all 14 tracks. Two genuine named-predecessor repeals newly modeled in the supersession graph (contractors_classification_law over M/18; private_healthcare_institutions_law over M/58); rega confirmed to have no predecessor, a negative finding requiring no new edge. One documented retrieval-eval miss: tlc-001 (telecommunications_law's own gold) now routes to the new frequency_spectrum_regulation track instead, a legitimate consequence of added coverage per this corpus's established dmz-001/dmz-003/mtn-002 precedent, not a regression. v(wave-6) (wf6-001..023): wave-6 batch of 23 new tracks (real estate implementing regulations, energy/petroleum laws, mining investment regulation, pharmaceutical establishments, seized/confiscated funds, NCA cybersecurity rules, CST, railway + its regulation, road transport, GACA, TGA, mawani, hajj/umrah pilgrims, aviation passenger rights), each gold reusing the corresponding unified-index SANITY tuple already globally re-verified. Adding this batch surfaced two more pre-existing SANITY/gold routing collisions from generic boilerplate overlapping the new tracks: eaq-002 (environmental_air_quality article 6, collided with dry_gas_lpg article 2's near-identical gas-processing phrasing) and pfa-002 (protection_from_abuse article 13, collided with aviation_passenger_rights article 18's vulnerable-passenger phrasing); both corrected in place to distinctive alternative wording from the same article, re-verified for a clean global top-1 margin, SANITY and gold kept in lockstep. No new misses were introduced beyond the pre-existing documented set (civ-004, pdp-010, mtn-002, dmz-001, dmz-003, tlc-001).
  Labor components, all four Evidence components, the Personal Status law + regulation, the
  Law of Sharia Procedure + its implementing regulation, the Law of Criminal Procedure + its implementing regulation, the Law of Enforcement + its regulation, the Law of the Judiciary, the Law of the Board of Grievances, the Code of Law Practice + its regulation, and the Commercial Courts Law + its regulation have
  gold coverage; every new
  gold was confirmed by reading the article's committed text first and writing the query from
  its own wording. Five documented
  lexical misses remain (civ-004 تعريف الكفالة; pdp-010 سياسة الخصوصية — the gold PDPL article
  does not contain the query phrase verbatim, so labor-annex records now outscore it; dmz-001,
  dmz-003 — Board of Grievances golds that now route to the topically-overlapping Judiciary/BoG
  mechanism track instead, a legitimate consequence of added coverage; mtn-002 — an Enforcement
  Law gold on "سند التنفيذ"/"الصيغة التنفيذية" terminology that now routes to the wave-4 batch's
  topically-overlapping bog_enforcement_law track instead, the same legitimate added-coverage
  effect as dmz-001/dmz-003, not a regression in either track's own text). Validator re-runs the eval, requires exact
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

## نظام ضريبة الدخل — Income Tax Law (15/1/1425هـ) — DISTINCT TIER, BOE x ZATCA PDF x GSTC PDF x NEZAMS

- **Income Tax Law (Royal Decree M/1, 15/1/1425H) verified + LLM-ready.**
  **نظام ضريبة الدخل** — **81 records** across **16 فصول** — **52 اصلية / 29
  معدلة**. Approving Council of Ministers Resolution 278 (20/11/1424H), signed
  by King Fahd bin Abdulaziz Al Saud. Repeals the 1370H-era income tax system,
  the additional oil-company income tax, and the original Natural Gas
  Investment Tax Law (M/37, 1424H). Administered by what the statute's own
  current Article 1 still calls "الهيئة العامة للزكاة والدخل" (GAZT) — a name
  itself superseded by the 2021 ZATCA merger, never updated by any further
  Royal-Decree-level amendment; the older term "المصلحة" is preserved verbatim
  per-article wherever a specific source literally uses it, not normalized.
  Of the 29 معدلة: **10** individually confirmed via BOE's own "changed" flag
  and/or explicit report annotation (Articles 1, 2, 6, 7, 8, 21, 56, 59, 66,
  67), **12** from Chapter 10's full replacement by Royal Decree M/70
  (11/7/1439H, introducing the Natural Gas Investment Tax framework and
  cutting its base rate from 30% to 20%), and **7** lower-confidence articles
  (9, 12, 13, 17, 43, 63, 65) marked معدلة on ZATCA-footnote/ledger evidence
  alone with no clause-level effect ever stated by the research pass.
  **DISTINCT VERIFICATION TIER:** current-consolidated text rests on **four
  sources** — `laws.boe.gov.sa` (via the Wayback Machine, reached with an
  explicit User-Agent header after both direct and `r.jina.ai`-proxied
  attempts failed), ZATCA's own official consolidated PDF, an older
  gstc.gov.sa PDF, and nezams.com — with every one of the 81 articles
  cross-verified from at least two sources in agreement, and the large
  majority from three or four. **⚠ IMPORTANT LIMITATION:** Chapter 10
  (Articles 44-55) is the **mirror image** of this corpus's VAT-law-track
  finding — BOTH government-authority PDF sources (ZATCA and gstc.gov.sa)
  print only a bare repeal notice for this entire 12-article chapter,
  omitting the substantive M/70 replacement text entirely; the full current
  text rests on **two sources only** (BOE via Wayback, cross-verified
  word-for-word against nezams.com). **NO `original_1425h_text` field is
  populated for any article** — the research report described having seen
  pre-amendment "before" text for six articles via BOE's amendment-history
  popups but never transcribed it verbatim into deliverable form, and the
  raw scratchpad data mostly quoted intermediate amendment states rather
  than clean 1425H originals, so nothing was promoted into this field rather
  than risk fabricating a reconstructed original; Chapter 10's pre-M/70 text
  is independently confirmed unrecoverable from any of the four sources.
  **Article 66** carries an unresolved, explicitly dual-dated conflict for
  Royal Decree M/52 (28/4/1441H per ZATCA's PDF vs 28/7/1441H per BOE's own
  amendment-history feature) — both candidate dates are recorded in its
  `history` entry rather than silently picking one. 14 total flagged
  discrepancies also cover: BOE's default per-article body being frequently
  pre-amendment/stale (confirmed for Articles 2, 56, 66, 67, 80) without a
  full 81-article diff having been performed; ZATCA's footnote apparatus
  touching more articles than BOE's own "changed" markup flags, with some
  footnote-to-clause attributions approximate due to PDF page-break
  artifacts; nezams.com confirmed stale on the two most recent (1441H)
  amendments; a single-sourced Official Gazette publication date; and
  Ministerial Resolution 2194 (12/7/1432H) explicitly distinguished as a
  non-amending interpretive clarification of Article 3(b)'s "الإدارة
  الرئيسة" term, not a textual amendment. A companion Implementing
  Regulation (Ministerial Resolution 1535, exact Hijri date unconfirmed) is
  **not extracted** in this track. Track under `sources/income_tax/law/`.
  Validate: `make income-tax-law-track-validate`.

## نظام الخدمة المدنية — Civil Service Law (10/7/1397هـ) — DISTINCT TIER, BOE WAYBACK x NEZAMS FULL CROSS-VERIFICATION

- **Civil Service Law (Royal Decree M/49, 10/7/1397H) verified + LLM-ready.**
  **نظام الخدمة المدنية** — **44 records** (40 numbered articles + 4 مكرر:
  15 مكرر, 25 مكرر, 36 مكرر, 37 مكرر) across **3 أبواب** (الباب الثاني split
  into 6 nested فصول) — **20 اصلية / 19 معدلة / 1 ملغاة / 4 مضافة**. Approving
  Council of Ministers Resolution 951 (27/6/1397H), signed by King Khalid bin
  Abdulaziz. Repeals the earlier نظام الموظفين العام (Royal Decree M/5,
  1/2/1391H). **VERIFICATION TIER:** all 44 article-entries cross-verified
  100% against nezams.com over a BOE Wayback Machine base text; the M/139
  six-article amendment package additionally corroborated via SPA/Okaz news
  coverage. **Article 3** is confirmed **ملغاة** (repealed by Royal Decree
  M/95, 15/9/1439H) with **no fabricated replacement text** recorded.
  `original_1397h_text` is populated for all 19 معدلة articles wherever the
  genuine pre-amendment text was actually captured (never fabricated);
  Articles 20, 29, and 35 were each amended twice — only the true 1397H
  original is kept in that field, with the intermediate amendment state
  recorded in `history` only. 11 documented discrepancies include: BOE
  citation gaps for 14 articles; Article 25's "لم"/"لما" grammar variant
  (nezams.com's "لما" adopted); the stale ministry name "وزارة الخدمة
  المدنية" preserved verbatim in Articles 25 مكرر/36 مكرر/39 (never
  normalized to the current Ministry of Human Resources and Social
  Development naming); M/139's unusual date-sequencing anomaly across its
  six amended articles; and explicit out-of-scope companion instruments
  (نظام مجلس الخدمة المدنية, نظام الانضباط الوظيفي M/18, نظام تأديب
  الموظفين), none of which are ingested in this track. Track under
  `sources/civil_service/law/`. Validate:
  `make civil-service-law-track-validate`.

## نظام التأمينات الاجتماعية (الجديد) — Social Insurance Law, New System (26/12/1445هـ) — DISTINCT TIER, BOE WAYBACK PRIMARY x NEZAMS SPOT-CHECK

- **Social Insurance Law — New System (Royal Decree M/273, 26/12/1445H)
  verified + LLM-ready.** **نظام التأمينات الاجتماعية (الجديد)** —
  **63 records**, all **اصلية**, across **6 أبواب** (الباب الثالث split into
  2 فصول: تعويضات الأخطار المهنية arts 30-40, تعويض الأمومة arts 41-42).
  Approving Council of Ministers Resolution 1022 (same date). Effective
  **1 July 2025 for new labor-market entrants only** — it does **not**
  supersede the pre-existing Social Insurance Law (Royal Decree M/33,
  3/9/1421H), which continues to govern everyone enrolled before that date
  and is tracked **separately** as `social_insurance_legacy_law`. **⚠ TITLE
  COLLISION:** both instruments share the identical Arabic title "نظام
  التأمينات الاجتماعية" while being legally distinct and concurrently
  operative for different populations — documented explicitly in this
  track's `known_unresolved_discrepancies`, analogous to the pre-established
  Franchise Law/Anti-Concealment Law M/22 decree-number collision. **⚠
  PARAPHRASED-RESEARCH-REPORT CAUGHT AND CORRECTED:** the build agent
  discovered its assigned research report contained condensed/paraphrased
  article summaries rather than genuine verbatim statutory text, refused to
  transcribe the paraphrase as governing text, and instead independently
  re-fetched the primary BOE source itself (a Wayback Machine snapshot dated
  2025-12-12, reached via curl's `if_` raw-content modifier with a desktop
  User-Agent), parsing its structured `<div class="article_item">` markup
  directly for all 63 articles, then spot-checking 5 of them word-for-word
  against nezams.com — now a documented corpus precedent that build agents
  must independently confirm a research report is actually verbatim before
  transcribing it. A new field, `decree_transitional_provisions_ar`, holds
  the Royal Decree's own بند أولاً–حادي عشر transitional provisions verbatim
  (they are not numbered articles of the law and were never folded into any
  article). 7 documented discrepancies include: the identical-title
  collision above; Article 44's statutory-2%-vs-administrative-1.5%
  unemployment-insurance-rate figures; Article 16's Cabinet-Resolution-filled
  180-month qualifying period; and the unextracted-but-referenced SANED
  (Royal Decree M/18) and Civil Pension Law (Royal Decree M/41) companion
  instruments. Track under `sources/social_insurance/law/`. Validate:
  `make social-insurance-law-track-validate`.

## نظام التأمينات الاجتماعية (القديم) — Social Insurance Law, Old/Legacy System (3/9/1421هـ) — DISTINCT TIER, BOE WAYBACK x NEZAMS x OKAZ/AL-RIYADH CORROBORATED

- **Social Insurance Law — Old/Legacy System (Royal Decree M/33, 3/9/1421H)
  verified + LLM-ready.** **نظام التأمينات الاجتماعية (القديم)** —
  **71 records** (70 numbered articles + Article 58 مكرر, added by Royal
  Decree M/16, 24/3/1431H) across **7 فصول** (الفصل الخامس further divided
  into 4 nested أقسام) — **63 اصلية / 7 معدلة / 1 مضافة**. Approving Council
  of Ministers Resolution 199 (17/8/1421H), issued by King Fahd bin
  Abdulaziz, superseding the earlier Royal Decree M/22 (6/9/1389H). Governs
  everyone enrolled in Saudi social insurance **before 1 July 2025** — it is
  **not** superseded by the new Social Insurance Law (Royal Decree M/273,
  tracked as `social_insurance_law`); both remain concurrently in force for
  different populations while sharing the identical Arabic title "نظام
  التأمينات الاجتماعية" (see that track's notes for the same collision
  documented from the other side). **VERIFICATION TIER:** full text rests on
  a Wayback Machine snapshot (2026-02-09) of the BOE portal — reached via a
  direct curl with the `if_` raw-content modifier, with **no egress-policy
  circumvention needed or used this pass** — cross-verified against
  nezams.com (20+ of 71 articles full-text, plus 100% of the nine
  changed-article amendment-history popups matched verbatim). **Article 10**
  (board composition): BOE's default rendering is confirmed **stale** (an
  old 11-member board); the genuinely current, reconciled text (14 members,
  chaired by the Minister of Finance) was derived from BOE's own
  amendment-history popups (Cabinet Resolutions 190/1438H → 335/1442H →
  419/1442H) and cross-verified verbatim against nezams.com — a further
  divergence from GOSI's own site (which describes an 8-member board) is
  documented as **unresolved** rather than silently adopted. **Article 37**
  (transport of a deceased subscriber's remains): BOE's default rendering is
  confirmed **stale** (a narrow, single-obligation provision); the
  genuinely current, broader 3-part text (Royal Decree M/49, 22/8/1431H)
  was independently corroborated via Okaz and Al-Riyadh news coverage
  quoting the current text verbatim. **Article 38** (retirement pension):
  no 2024 transitional retirement-age text was merged into this article —
  only its two genuine, verified historical amendments were applied (Royal
  Decree M/49 1431H reworded sub-paragraph 1/ج and paragraph 2; Royal
  Decree M/134 1440H deleted sub-paragraph 1/ج entirely, per nezams.com's
  explicit citation); the 2024 age-table transitional override actually
  belongs to the **new law's own promulgating Royal Decree** and lives in
  that track's `decree_transitional_provisions_ar` field instead — a
  discrete non-merge note, not silently absorbed. 8 documented
  discrepancies also include: the dual-law title collision above; a
  Cabinet-Resolution sequencing oddity in Article 10's own amendment
  history; Article 41 paragraph 3's instrument-type citation mismatch
  (Royal Decree M/118 per BOE vs. Cabinet Resolution 631 per nezams.com,
  dated one day apart); a duplicate/glitch amendment-history popup BOE
  attaches to Article 58 (base) that actually belongs to 58 مكرر; and an
  unextracted Implementing Regulation (GOSI Board Resolution 735,
  25/10/1421H). Track under `sources/social_insurance_legacy/law/`.
  Validate: `make social-insurance-legacy-law-track-validate`.

## اللائحة التنفيذية لجباية الزكاة — Zakat Collection Implementing Regulation (19/8/1445هـ) — SINGLE-SOURCE TIER, ZATCA PDF x GAZETTE SPOT-VERIFIED

- **Zakat Collection Implementing Regulation (Minister of Finance Resolution
  No. 1007, 19/8/1445H) verified + LLM-ready.** **اللائحة التنفيذية لجباية
  الزكاة** — **128 records** across **5 أبواب** (with nested فصول and
  فروع) — **127 اصلية / 1 معدلة** (Article 73, amended by Minister of
  Finance Resolution No. 1248, 11/10/1446H). Administered by ZATCA (Zakat,
  Tax and Customs Authority) — the primary fiscal levy on Saudi/GCC-owned
  entities, parallel to and distinct from the already-covered
  `income_tax_law` (non-Saudi-owned shares/entities). Identified as the
  corpus's **top-priority coverage gap** via a dedicated coverage-gap-map
  research pass, whose own decree-number and article-count estimates were
  subsequently found to be **wrong** during dedicated follow-up research
  (it cited the already-covered income-tax decree's own repealed
  predecessor number, and estimated 20-30 articles against the true count
  of 128) — corrected transparently rather than silently carried forward.
  The short foundational enabling Royal Decree (17/2/28/8634, 29/6/1370H)
  is treated as prose-only preamble context, **not** a numbered article of
  this track, since its own ~2-article text was never independently
  confirmed via a direct successful fetch (only search-engine-mediated
  quotes) — excluded per this corpus's zero-fabrication policy rather than
  transcribed on secondhand evidence. **VERIFICATION TIER: SINGLE-SOURCE**
  — the full 128-article text rests solely on ZATCA's own official PDF
  (`laws.boe.gov.sa` returned HTTP 503 on every attempt across two separate
  research/build passes); the Umm Al-Qura Gazette (uqn.gov.sa) was
  successfully reached and used only for **targeted spot-verification**
  (Resolution 1007's exact date, and Article 13's مالك/ملاك title
  disambiguation), not a second full-text cross-check. **⚠ SEVERE PDF
  EXTRACTION BUG DISCOVERED AND FIXED:** the source PDF's font/ToUnicode-CMap
  systematically transposes LAM+alef-form character pairs (all four alef
  forms), corrupting extremely common words (الأصول، الإقرار، اللائحة,
  etc.) — far more pervasive than the Presentation-Forms issue previously
  documented in `income_tax_law`. Fixed via a general regex, a curated
  ~140-entry dictionary, and context-anchored resolution of two genuine
  homograph ambiguities. A separate PDF line-wrap/justification artifact
  misordered wrapped lines across roughly 35 articles, hand-reconstructed
  by reading each full sentence for sense (no wording invented, only
  reordered); **one further instance (Article 128) was caught and
  corrected during post-build review**, and a residual, unquantified risk
  of similar uncorrected artifacts in other paragraphs is documented rather
  than hidden. Other flagged discrepancies: no `original_1445h_text` for
  Article 73 (pre-amendment text not recoverable from the consolidated
  PDF); the prior 1440H regulation's repeal clause not found verbatim
  within the operative articles themselves; and a secondary claim of
  200,000/400,000 SAR minimum zakat-base figures searched for and
  confirmed **absent** from the primary text (the only flat floor found is
  Article 86's 500 SAR minimum for presumptive taxpayers). Track under
  `sources/zakat/law/`. Validate: `make zakat-law-track-validate`.

## نظام براءات الاختراع والتصميمات التخطيطية للدارات المتكاملة والأصناف النباتية والنماذج الصناعية — Patent Law (29/5/1425هـ) — DISTINCT TIER, WIPO LEX M/45-CONSOLIDATED x BOE STALE

- **Law of Patents, Layout Designs of Integrated Circuits, Plant
  Varieties and Industrial Designs (Royal Decree M/27, 29/5/1425H)
  verified + LLM-ready.** **نظام براءات الاختراع...** — **66 records**
  (65 sequentially-numbered articles + Article 60 مكرر, inserted 2023)
  across **6 فصول** — **59 اصلية / 6 معدلة / 1 مضافة**. Approving
  Council of Ministers Resolution No. 159 (17/5/1425H). Repeals the prior
  Patent Law (Royal Decree M/38, 10/6/1409H). Administered by SAIP
  (renamed from KACST). Identified as the corpus's **#2-priority IP-family
  gap** via the coverage-gap-map research pass (trademark_law and
  copyright_law were already covered; patents were not). **Two confirmed
  amendments:** Council of Ministers Resolution 536 (2018) — a pure
  KACST/"المدينة"/"الإدارة" to SAIP/"الهيئة" institutional-terminology
  substitution; and Royal Decree M/45 (2023) — Hague Agreement/Geneva Act
  accession changes (new definitions, a 5-year Hague filing fee cycle,
  industrial design protection extended 10→15 years, new Article 60
  مكرر). **VERIFICATION TIER:** BOE's own displayed consolidated text is
  confirmed **stale on two axes** — it has not incorporated the 2023
  amendment at all, and for 3 of the 4 2018-amended articles (35, 42, 63)
  BOE's own displayed article body still shows pre-2018 wording even
  though its own amendment-annotation correctly describes the change.
  WIPO Lex's M/45-consolidated PDF (cross-verified via two independent
  OCR passes plus a native-text-layer `pdftotext` extraction, since the
  source PDF is a genuine Word-generated PDF, not a scan) is used as the
  current-text primary source; BOE is used only for metadata/provenance/
  genuinely-recoverable original wording. **⚠ TERMINOLOGY-SUBSTITUTION
  SCOPE:** the amending resolution's own recital states the substitution
  applies "أينما وردتا في النظام" (wherever the terms appear) — this
  build found the substitution's actual textual footprint extends to at
  least **22 further articles** beyond the 4 formally enumerated as
  amended; the current ("الهيئة") wording is presented as governing text
  for all of these, while `legal_status_ar` is conservatively kept
  "اصلية" for them absent a primary source separately flagging each as
  amended — a scope judgment flagged transparently rather than silently
  resolved either way. Also preserved verbatim: a genuine 2018 drafting
  inconsistency (Article 35(b) keeps a "رئيس"/Chairman prefix the
  parallel Articles 42 and 63 lack). `original_1425h_text` is populated
  for the 6 formally-enumerated amended articles only. Other flagged
  discrepancies: a broken SAIP-hosted "updated 2024" PDF link
  (independently reproduced 404, not a network block); and a
  clarification that the separate, parallel GCC Unified Patent Law (an
  optional regional filing route, not a replacement) is deliberately not
  ingested. Track under `sources/patent/law/`. Validate:
  `make patent-law-track-validate`.

## نظام (قانون) الجمارك الموحد لدول مجلس التعاون لدول الخليج العربية ولائحته التنفيذية — GCC Unified Customs Law (3/11/1423هـ) — SINGLE-SOURCE TIER, ZATCA PDF, THREE-PASS POST-BUILD QA

- **GCC Unified Customs Law (Royal Decree M/41, 3/11/1423H) and its
  Implementing Regulation (Ministerial/Committee Resolution No. 2748,
  25/11/1423H) verified + LLM-ready.** Built as **two separate tracks**
  (`customs_law`, `customs_regulation`), mirroring this corpus's
  `bankruptcy_law`/`bankruptcy_implementing_regulation` pattern, since the
  two are issued by different instruments with independent amendment
  histories. Administered by ZATCA — governs all cross-border trade
  into/out of Saudi Arabia, the corpus's **#3-priority coverage gap**
  (previously completely absent). **`customs_law`: 188 records** (179
  base articles + 9 مكرر bis-articles) across **17 أبواب** — 176 اصلية /
  3 معدلة (Articles 61, 72, 102) / 9 مضافة. Amended 3 times: Royal Decree
  M/14 (1443H, specific amended article(s) unconfirmed), M/81 (1444H,
  confirmed Article 61), M/124 (1445H, confirmed Articles 72/102).
  **`customs_regulation`: 36 records** (34 base + 2 مكرر) across **7
  أبواب**, numbered continuously — 34 اصلية / 2 مضافة. Amended 6 times
  (no specific article individually attributable to any one resolution
  from the available source). **VERIFICATION TIER: SINGLE-SOURCE** — both
  tracks share ZATCA's own official consolidated PDF as the sole
  full-text primary source; `laws.boe.gov.sa` was confirmed unreachable
  across repeated attempts (connection reset / HTTP 503). nezams.com was
  found **unreliable** for this specific law (wrong decree date,
  unconfirmed amendments) and is not relied upon.

  **⚠ THREE-PASS POST-BUILD QA PROCESS** (documented transparently as a
  demonstration of this corpus's review rigor, not hidden): (1) the
  initial build's ligature-bug fix (reusing the `zakat_law` precedent)
  was found, on independent review, to have missed a widespread
  corruption of the meaning-critical negation particle "لا" → "ال" — a
  dedicated follow-up pass found and fixed **404 additional
  dropped/transposed-lam instances combined** across both tracks; (2) a
  second follow-up pass then found and fixed **182 further instances**
  where lettered sub-item markers (أ، ب، ج) were glued directly onto the
  following word with no separator, plus stray/doubled diacritic
  artifacts; (3) a final review pass caught and fixed **3 remaining
  word-internal transposition instances** the two prior passes missed
  (Article 18's "لا يجوز"; two instances of "ملاحقة" in Articles 54 and
  176). No `original_1423h_text` populated for the 3 معدلة articles of
  `customs_law` (pre-amendment text not recoverable from the consolidated
  PDF). The 9 مكرر bis-articles' individual amending-decree attribution
  is not confirmed from a primary source, a documented gap. Article 1 of
  `customs_regulation` (customs valuation methodology, implementing GATT
  Art. VII) is a single very long article internally organized by ordinal
  clause markers (أولاً...ثامناً) rather than separate numbered articles,
  preserved whole. Track under `sources/customs/`. Validate:
  `make customs-law-track-validate` and
  `make customs-regulation-track-validate`.

## نظام مكافحة الغش التجاري — Anti-Commercial Fraud Law (23/4/1429هـ) — SECONDARY-MULTI-SOURCE TIER, BOE UNREACHABLE

- **Anti-Commercial Fraud Law (Royal Decree M/19, 23/4/1429H) verified +
  LLM-ready.** Approves Council of Ministers Resolution No. 119
  (22/4/1429H); replaces the prior Anti-Commercial Fraud Law (Royal Decree
  M/11, 29/5/1404H, not separately ingested — see the supersession graph's
  new `repeals_full` edge). Administered by the Ministry of Commerce
  (Anti-Commercial Fraud General Administration). The corpus's
  **#4-priority coverage gap**. **30 records** across **5 فصول**
  (تعريفات art 1; المخالفات arts 2-4; الضبط والتحقيق والمحاكمة arts 5-15;
  العقوبات arts 16-27; أحكام ختامية arts 28-30) — **25 اصلية / 5 معدلة**
  (Articles 5, 13, 23, 25, 27). **VERIFICATION TIER:
  SECONDARY-MULTI-SOURCE** — `laws.boe.gov.sa` returned HTTP 503 at two
  distinct URL forms across both the prior research pass and this build
  pass, confirming it is genuinely unreachable; the full text instead
  rests on **three independently cross-verified secondary sources**
  (nezams.com, mustsharik.com, mohamah.net), with a fresh 5-article
  spot-recheck (Articles 1, 5, 13, 23, 25) during this build pass finding
  no discrepancy beyond what the prior research pass had already flagged.

  **⚠ DISPUTED ARTICLE 5 SECOND-AMENDMENT CITATION** (documented
  transparently rather than silently resolved, matching this corpus's
  established convention — cf. `income_tax_law` Article 66's dual-dated
  M/52 conflict): the instrument adding "وزارة الصحة" is recorded as
  EITHER Council of Ministers Resolution No. 508 (1/9/1442H, per
  nezams.com and an indexed-but-dead Umm al-Qura gazette snippet) OR Royal
  Decree M/76 (3/9/1442H, per mustsharik.com and two independent WebSearch
  aggregations) — both candidates are preserved in the article's history.
  Article 5's current `text` field is consequently a transparently-flagged
  mechanical splice of the verbatim original sentence with both
  amendments' verbatim-quoted inserted phrases, since no single source
  presents the fully consolidated post-both-amendments text as one block.
  Other flagged discrepancies: mohamah.net's 2017 transcription is missing
  Article 15 entirely (a scraping error, not a textual variant — nezams.com
  and mustsharik.com agree verbatim); Article 1's ministry definitions and
  Article 12's prosecution-authority reference are preserved verbatim as
  likely-stale-but-not-formally-amended, not modernized; a draft
  comprehensive "Consumer Protection Law" remains unenacted as of this
  build (2026-07-18), confirming this law as the correct current build
  target; and the prior research pass's own narrative summary undercounted
  اصلية articles by one relative to its own per-article tagging, corrected
  in this track's `status_counts`. Track under `sources/anti_fraud/`.
  Validate: `make anti-fraud-law-track-validate`.

## نظام مراقبة شركات التمويل — Finance Companies Control Law (13/8/1433هـ) — BOE-WAYBACK-PRIMARY TIER, x BFC.GOV.SA OCR x NEZAMS

- **Finance Companies Control Law (Royal Decree M/51, 13/8/1433H)
  verified + LLM-ready.** Approves Council of Ministers Resolution No.
  259 (12/8/1433H), published Umm al-Qura 13/10/1433H. Administered by
  SAMA (referred to as "المؤسسة"/"المحافظ" in unamended articles and
  "البنك" in the 2024-amended ones — the same SAMA-to-Saudi-Central-Bank
  divergence already documented in this corpus's `insurance_control_law`
  track, preserved verbatim per-article, not normalized). The corpus's
  **#5-priority coverage gap**; the gap map's own decree/date estimate
  was independently re-verified and confirmed correct. **41 records** (40
  numbered articles + Article 36 مكرر, added 2024) across a فصل تمهيدي
  (تعريفات) plus **8 فصول** (أحكام عامة؛ أحكام الترخيص؛ نشاط شركات
  التمويل؛ إدارة شركات التمويل؛ الإشراف [renamed from "الإشراف على شركات
  التمويل" by the 2024 amendment]؛ المخالفات والمنازعات؛ العقوبات؛ أحكام
  ختامية) — **28 اصلية / 12 معدلة / 1 مضافة**. Amended three times: Royal
  Decree M/21 (1440H, narrow, Article 5 only), M/24 (1443H, based on
  Council of Ministers Resolution 160, Article 35 only), M/272 (1445H /
  2024, based on Council of Ministers Resolution 1016, a substantial
  14-item amendment touching Articles 1, 5, 11, 12, 16-21, 29 plus new
  Article 36 مكرر). **VERIFICATION TIER: BOE-WAYBACK-PRIMARY** — the live
  `laws.boe.gov.sa` portal was unreachable this pass (HTTP 503 direct,
  422 via r.jina.ai proxy), but a Wayback Machine snapshot of the exact
  BOE law page was reachable via direct curl and used as the primary
  full-text source for all 40 original articles, cross-verified via
  normalized programmatic diff (**zero substantive discrepancies**)
  against `bfc.gov.sa`'s own official PDF (OCR'd via tesseract, since the
  PDF's font/cmap was corrupted) and nezams.com's HTML transcription; the
  2024 amendment's exact replacement text rests on qanoonsa.com's
  verbatim decree reproduction, cross-checked against nezams.com's
  per-article footnotes — **flagged `has_per_article_variation`** since
  the 2024 amendment text itself has no direct primary-source
  confirmation, unlike the 40 original articles.

  Other flagged discrepancies: Article 5's pre-1440H deleted بند
  (خامساً) is not recoverable from any source consulted, a documented gap
  not a fabrication; Article 5's 1440H amendment description does not
  fully account for the article's current 6-بند structure, an arithmetic
  gap flagged rather than resolved by inference; Article 35's amending
  instrument carries two compatible-but-distinct citations between
  sources (BOE: Royal Decree M/24; other sources: Council of Ministers
  Resolution 160) — both recorded; BOE's own archived Article 35
  annotation contains a corrupted penalty figure/spelling, not adopted.
  Article 38 is a general, non-specific repeal clause naming no prior
  statute, so no supersession-graph edge is modeled from it. A companion
  Implementing Regulation (Governor's Resolution 2/م ش ت, 14/4/1434H, 38
  image-scanned pages with its own independent multi-wave amendment
  history) exists but its text is out of scope for this track, following
  the precedent set by `banking_control_law` and `insurance_control_law`.
  Track under `sources/finance_companies/`. Validate:
  `make finance-companies-law-track-validate`.

## نظام الضمان الصحي التعاوني — Cooperative Health Insurance Law (1/5/1420هـ) — BOE-WAYBACK-ARCHIVE TIER, x NEZAMS.COM CROSS-VERIFIED

- **Cooperative Health Insurance Law (Royal Decree M/10, 1/5/1420H)
  verified + LLM-ready.** Approves Council of Ministers Resolution No.
  71 (27/4/1420H). Administered by the Council of Cooperative Health
  Insurance (مجلس الضمان الصحي التعاوني / CCHI) — a distinct, more
  specific statute from this corpus's already-ingested
  `insurance_control_law` (Cooperative Insurance Companies Control Law,
  M/32, 1424H), which governs insurance companies generally; not
  conflated. A **medium-priority** coverage-gap identified via the
  coverage_gap_map research pass, whose decree/date estimate was
  independently re-verified and confirmed correct (unlike several prior
  gap-map entries this corpus found wrong or imprecise). **19 records**,
  flat structure (no أبواب/فصول, confirmed absent from both sources) —
  **17 اصلية / 2 معدلة** (Articles 4 and 14, both amended by Council of
  Ministers Resolution 246, 4/9/1425H; Article 4 amended a second time by
  Resolution 472, 18/8/1440H, restructuring full council membership).
  **VERIFICATION TIER: BOE-WAYBACK-ARCHIVE** — the live `laws.boe.gov.sa`
  portal was unreachable this pass (connection reset), but a Wayback
  Machine snapshot of the exact BOE law page was reachable (plain
  `http://` was required; `https://` was blocked by egress policy) and
  cross-verified byte-for-byte against nezams.com's HTML transcription,
  finding **zero substantive discrepancies** across all 17 unamended
  articles and both the 1420H and 1425H states of the 2 amended articles
  — **flagged `has_per_article_variation`** since Article 4's 1440H
  amendment replacement text rests on nezams.com alone (BOE's own page
  cites Resolution 472 but does not reproduce its text).

  Other flagged discrepancies: BOE's own summary metadata panel shows an
  internally inconsistent issuance/publication date ("1420/01/01H =
  17/04/1999"), almost certainly a generic year-placeholder rather than
  the real decree date, not adopted; 5 specific transcription artifacts
  in nezams.com's raw text for Article 4 were individually normalized and
  disclosed verbatim rather than silently corrected; a companion
  Implementing Regulation (CCHI-hosted, amended multiple times) is
  identified but not ingested this pass, following the precedent set by
  `banking_control_law`/`insurance_control_law`/`finance_companies_law`;
  CCHI circulars and Umrah/Hajj-visitor coverage expansions are clarified
  as living outside this primary Law's own amendment history (only
  Articles 4 and 14 were ever amended) and are out of scope. No repeal
  clause found in the decree or its underlying resolution — a
  freestanding new 1420H law, no supersession-graph edge applicable.
  Track under `sources/cooperative_health_insurance/`. Validate:
  `make cooperative-health-insurance-law-track-validate`.

## نظام مزاولة المهن الصحية — Law of Practicing Healthcare Professions (4/11/1426هـ) — BOE-WAYBACK-ARCHIVE TIER, x NEZAMS.COM CROSS-VERIFIED

- **Law of Practicing Healthcare Professions (Royal Decree M/59,
  4/11/1426H) verified + LLM-ready.** Approves Council of Ministers
  Resolution No. 276 (3/11/1426H), published 28/11/1426H. Governs
  licensing/practice of physicians, dentists, pharmacists, nurses, and
  other healthcare professionals; administered by the Ministry of Health
  and the Saudi Commission for Health Specialties. A medium-priority
  coverage-gap identified via the coverage_gap_map research pass, whose
  article-count estimate (approx. 33) was found wrong — corrected to the
  true count of **44 records** during dedicated research. Structured
  across **5 فصول** (الترخيص بمزاولة المهنة arts 1-4; واجبات الممارس
  الصحي arts 5-25, itself subdivided into 3 فرع subsections; المسؤولية
  المهنية arts 26-32, also subdivided into 3 فرع subsections; التحقيق
  والمحاكمة arts 33-41; أحكام ختامية arts 42-44) — **all 44 اصلية**,
  never amended since enactment, confirmed by both BOE's own zero
  per-article amendment markers and nezams.com's explicit "لم يجرِ عليه
  تعديل" (no amendment) statement. **VERIFICATION TIER:
  BOE-WAYBACK-ARCHIVE** — the live `laws.boe.gov.sa` portal was
  unreachable this pass, but a Wayback Machine snapshot was fetched
  successfully via `https://` (plain `http://` returned 403 for this
  track, the opposite pattern from `cooperative_health_insurance_law`,
  both schemes tried per established practice) and cross-verified
  against a live fetch of nezams.com, agreeing on **42 of 44 articles
  with zero differences** after normalization; the chapter/فرع structure
  was additionally corroborated article-boundary-exact against
  `moh.gov.sa`'s own official consolidated Arabic and English PDFs.

  **⚠ CONFIRMED DUAL-REPEAL:** Article 42 repeals both the prior
  Physicians/Dentists Law (Royal Decree M/3, 21/2/1409H) and the prior
  Pharmacy Law (Royal Decree M/18, 18/3/1398H) — modeled as **two new
  `repeals_full` edges** in the supersession graph, since they are
  distinct predecessor instruments named in the same article. Other
  flagged discrepancies: nezams.com carries an isolated single-character
  typo in Article 36 ("الشريعية" vs the correct "الشرعية"), BOE's text
  adopted instead; nezams.com's page appends site-navigation footer text
  after Article 44, a scraping-boundary artifact excluded rather than
  treated as a discrepancy; a Shura-Council-approved (December 2023) but
  **not-yet-enacted** proposed new Article 4 bis (licensing independent
  Saudi health practitioners) is documented but not added as a record,
  since it has not been issued via Royal Decree as of this build; a
  companion Implementing Regulation (Ministerial Resolution No.
  4080489, 2/1/1439H) is confirmed to exist but is out of scope for this
  track, following the precedent set by
  `banking_control_law`/`insurance_control_law`/`finance_companies_law`/
  `cooperative_health_insurance_law`. Track under
  `sources/healthcare_professions/`. Validate:
  `make healthcare-professions-law-track-validate`.

## نظام الإيجار التمويلي — Finance Lease Law (13/8/1433هـ) — BOE-WAYBACK-ARCHIVE TIER, x SAMA RULEBOOK PDF x NEZAMS TRIPLE-VERIFIED

- **Finance Lease Law (Royal Decree M/48, 13/8/1433H) verified +
  LLM-ready.** Published 13/10/1433H. Governs the finance-lease
  (leasing) contract itself — registration, rights, enforcement — as a
  **separate, more specific statute** from this corpus's already-ingested
  `finance_companies_law` (Finance Companies Control Law, M/51, 1433H),
  which regulates finance companies generally; not conflated. A
  medium-priority coverage-gap identified via the coverage_gap_map
  research pass, whose article-count estimate was independently
  re-verified and **confirmed correct** — unlike several prior
  gap-map entries this corpus found wrong. **28 records** across a فصل
  تمهيدي (تعريفات, Article 1) plus **4 فصول** (عقد الإيجار التمويلي arts
  2-17; سجل العقود arts 18-23; المخالفات والمنازعات arts 24-26; أحكام
  ختامية arts 27-28) — **all 28 اصلية**, never amended since enactment
  (only the companion Implementing Regulation has itself been separately
  amended). **VERIFICATION TIER: BOE-WAYBACK-ARCHIVE, TRIPLE-VERIFIED** —
  the live `laws.boe.gov.sa` portal was unreachable this pass, but a
  Wayback Machine snapshot (both `http://` and `https://` tried,
  `https://` worked) was used as primary, cross-verified byte-for-byte
  against nezams.com's live transcription **and** against
  `rulebook.sama.gov.sa`'s own official Arabic and English PDFs (the only
  source carrying inline فصل headings), agreeing on **all 28 articles**.

  An initial webpage-summary artifact incorrectly suggested Chapter Two
  ended at Article 20; corrected to Article 23 after reading SAMA's own
  primary-source PDFs page-by-page. Other flagged discrepancies: the
  institutional-name reference to مؤسسة النقد العربي السعودي (SAMA,
  since renamed to the Saudi Central Bank by a separate law, M/36) is a
  naming footnote, not a textual amendment to this Law's own defined
  terms — preserved verbatim; **no explicit predecessor-repeal clause was
  found** naming any prior statute, a documented negative finding rather
  than an assumption, so no supersession-graph edge applies; Articles 20
  and 22 carry genuine decorative tatweel characters confirmed present
  identically in both BOE and nezams.com, preserved verbatim rather than
  "cleaned"; a companion Implementing Regulation (Administrative/
  Governor's Decision 1/م ش ت, 14/4/1434H, itself separately amended at
  least once) is confirmed to exist but is out of scope for this track,
  following the precedent set by
  `banking_control_law`/`insurance_control_law`/`finance_companies_law`/
  `cooperative_health_insurance_law`/`healthcare_professions_law`. Track
  under `sources/finance_lease/`. Validate:
  `make finance-lease-law-track-validate`.

## النظام البحري التجاري — Maritime Commercial Law (5/4/1440هـ) — BOE-WAYBACK-ARCHIVE TIER TRIPLE-VERIFIED, x NEZAMS x BOE ENGLISH TRANSLATION

- **Maritime Commercial Law (Royal Decree M/33, 5/4/1440H, based on Council
  of Ministers Resolution No. 197 of 4/4/1440H) verified + LLM-ready.**
  Published in the Official Gazette 28/4/1440H. This corpus's **largest
  single track to date — 391 records, all 391 اصلية**, never amended
  since enactment. A high-priority coverage-gap identified via the
  coverage_gap_map research pass, whose article-count estimate was
  independently re-verified and **confirmed correct**. Structure: a فصل
  تمهيدي (Article 1, definitions) plus **10 أبواب** — الباب الأول
  (السفينة, arts 2-30, 7 فصول), الباب الثاني (الحقوق العينية على
  السفينة, arts 31-73, 3 فصول), الباب الثالث (الحجز على السفينة, arts
  74-91, 2 فصول), الباب الرابع (أشخاص الملاحة البحرية, arts 92-141, 4
  فصول), الباب الخامس (استغلال السفينة, arts 142-253, 4 فصول — its
  الفصل الرابع, عقد النقل البحري, arts 179-253, further split into 5
  أولاً..خامساً subsections), الباب السادس (الحوادث البحرية, arts
  254-292, 4 فصول), الباب السابع (التأمين البحري, arts 293-357, 5 فصول),
  الباب الثامن (منع التلوث البحري, arts 358-362, no فصول), الباب التاسع
  (سلامة الملاحة, arts 363-372, 2 فصول), الباب العاشر (العقوبات, arts
  373-388, no فصول), plus أحكام عامة ختامية (arts 389-391).

  **VERIFICATION TIER: BOE-WAYBACK-ARCHIVE, TRIPLE-VERIFIED** — the live
  `laws.boe.gov.sa` portal was unreachable this pass, but a Wayback
  Machine snapshot of BOE's own Arabic law page was used as primary,
  cross-verified against nezams.com's live transcription **and** against
  BOE's own official English-translation PDF (fetched via Wayback
  Machine as an independent third source), agreeing word-for-word on
  381 of 391 articles. **Articles 316-325 (marine insurance provisions)
  required special handling**: a full programmatic diff found
  nezams.com's transcription repeats — verbatim, byte-for-byte — the
  content it renders for Articles 306-315 in place of genuinely distinct
  content for 316-325 (a clean +10 duplication offset, consistent with a
  nezams.com template/CMS bug). This was resolved using BOE's Arabic HTML
  (which renders ten internally coherent, sequential, mutually distinct
  provisions — duty to safeguard insured items, settlement by indemnity,
  general-average share, abandonment rules, forfeiture for false claims,
  subrogation, the two-year limitation period) **independently confirmed
  article-by-article by BOE's own official English-translation PDF**, a
  wholly separate BOE-hosted document that could not have inherited
  nezams.com's bug. I personally re-read the committed Articles 316-325
  after the build and confirmed they read as distinct, coherent,
  non-duplicated marine-insurance clauses. nezams.com is flagged
  unreliable for this specific 10-article range only, not discarded
  wholesale, consistent with this corpus's established precedent
  (`customs_law_nezams_unreliable`).

  **Article 391 confirms a dual repeal**, modeled as two separate
  supersession-graph edges: a `repeals_partial` of الباب الثاني (Book
  Two) of "نظام المحكمة التجارية" (Royal Decree No. 32, 15/1/1350H) — the
  **same untracked predecessor instrument** already partially repealed
  (arts 103-137) by this corpus's `bankruptcy_law`, cross-referenced in
  both edges so a reader understands they affect different article
  ranges of the same historical law; and a `repeals_full` of "نظام
  الموانئ والمرافئ والمنائر البحرية" (Ports, Harbours and Lighthouses
  Law, Royal Decree M/27, 24/6/1394H). Other flagged discrepancies:
  multiple implementing regulations exist (vessel registration, maritime
  transport licensing, and others) but are out of scope for this track,
  following established precedent; Article 1 defines "الوزير" once, while
  five operative articles (8, 30, 222, 257, 390) instead use "الرئيس" for
  the same office — confirmed present identically in both BOE and
  nezams.com, preserved verbatim rather than harmonized; a small number
  of non-breaking-space and curly-quote cosmetic differences were
  normalized uniformly (documented, not silently performed); the
  predecessor-repeal scope was corroborated via secondary English-language
  legal-update sources but not exhaustively cross-checked article-by-article
  against the repealed instruments' own text, a deliberately bounded scope
  documented rather than left unstated. Track under
  `sources/maritime_commercial/`. Validate:
  `make maritime-commercial-law-track-validate`.

## النظام الموحد لمكافحة الإغراق والتدابير التعويضية والوقائية — GCC Unified Anti-Dumping, Countervailing and Safeguard Measures Law (17/5/1427هـ) — BOE-WAYBACK-ARCHIVE PRIMARY, x QISTAS PARTIAL CROSS-CHECK, MAJOR UNRESOLVED AMENDMENT RISK

- **GCC Unified Anti-Dumping, Countervailing and Safeguard Measures Law
  (Royal Decree M/30, 17/5/1427H, ratifying Council of Ministers
  Resolution No. 122) verified + LLM-ready.** Adopts for Saudi Arabia the
  GCC Supreme Council's unified law approved at its 24th Session (Kuwait,
  27-28 Shawwal 1424H / December 2003). A medium-priority coverage-gap
  identified via the coverage_gap_map research pass; **17 records, all
  اصلية**, correcting the gap-map's own rough estimate of "approx. 30-40
  articles". **No أبواب/فصول exist** — a flat, individually-titled
  17-article structure (this corrects an assumption carried into the
  research brief): الهدف والنطاق؛ التعاريف؛ فرض التدابير؛ التدابير
  المؤقتة؛ التدابير النهائية؛ أشكال التدابير؛ إجراءات الشكوى والتحقيق؛
  تشكيل اللجنة الدائمة؛ اختصاصات اللجنة الدائمة؛ اللجنة الوزارية؛ الأمانة
  الفنية للجنة الدائمة؛ الطعن؛ سرية المعلومات؛ الجزاءات؛ اللائحة
  التنفيذية؛ (Article 16, whose own BOE heading carries no title text,
  preserved as a documented gap rather than fabricated)؛ النفاذ.

  **VERIFICATION TIER: BOE-WAYBACK-ARCHIVE-PRIMARY, PARTIAL
  QISTAS.COM CROSS-CHECK** — the live `laws.boe.gov.sa` portal was
  unreachable this pass (HTTP 503), but two independent Wayback Machine
  snapshots of the exact law page, roughly 20 months apart, show
  identical unamended 17-article text with status "ساري", listing only
  M/30 + Resolution 122 as issuing instruments; qistas.com independently
  corroborated Articles 1-3's numbering and content only, not the full
  text. This corresponds to the corpus's TIER_4 classification
  (documented mixed/uncertain confidence at the track level), not
  because the ingested text itself is poorly sourced, but because of the
  major unresolved discrepancy below.

  **MAJOR UNRESOLVED DISCREPANCY, carried forward rather than resolved:**
  multiply-corroborated secondary evidence — WIPO Lex's own record for
  this law (marked superseded) and a wholly separate, currently in-force
  2022 Saudi law whose own preamble explicitly cites "المرسوم الملكي رقم
  (م/7) وتاريخ 20/3/1434هـ" — indicates Royal Decree M/7 (1 February
  2013) approved an amended ("معدل") version of this GCC-unified law,
  restructured into 15 articles per the GCC Secretariat General's own
  official PDF (approved at the GCC Supreme Council's 31st Session, Abu
  Dhabi, December 2010). However, BOE's own primary catalog page for
  this law — the actual source ingested here — shows **zero** reference
  to M/7 across two snapshots ~20 months apart, and neither Umm Al-Qura
  Gazette's own text of M/7 nor WIPO Lex's full-text PDF endpoints could
  be retrieved (a generic JS-shell wrapper was returned for every URL
  tried). Consistent with this corpus's trust policy, this track ingests
  BOE's directly-verified 17-article original text rather than substitute
  the unconfirmed amended text, and flags this as a **live, unresolved
  sourcing risk** for any downstream use — not a settled finding. A
  companion Implementing Regulation is confirmed to exist (Article 15
  references it) but is out of scope for this track, following
  established precedent. Track under `sources/gcc_anti_dumping/`.
  Validate: `make gcc-anti-dumping-law-track-validate`.

## نظام مهنة المحاسبة والمراجعة — Law of the Accounting and Auditing Profession (27/7/1442هـ) — BOE-WAYBACK-ARCHIVE x SOCPA OFFICIAL PDF, CONFIRMED BOE MAIN-BODY STALENESS

- **Law of the Accounting and Auditing Profession (Royal Decree M/59,
  27/7/1442H, ratifying Council of Ministers Resolution No. 416)
  verified + LLM-ready.** A medium-priority coverage-gap identified via
  the coverage_gap_map research pass. **22 records: 17 اصلية, 5 معدلة**
  (Articles 1, 4, 5, 19, 20) — flat structure, **no أبواب/فصول**, and
  BOE's own source carries no inline per-article titles.

  **Confirmed supersession of a predecessor**: this law's own Article 21
  states it replaces the Law of Certified Public Accountants (Royal
  Decree M/12, 13/5/1412H), whose separate BOE page independently shows
  status "لاغي" (repealed) — a doubly-confirmed repeal, modeled as a
  supersession-graph edge; the predecessor itself is not ingested.

  **VERIFICATION TIER: BOE-WAYBACK-ARCHIVE x SOCPA OFFICIAL PDF x
  QANOONSA CROSS-VERIFIED** — the live `laws.boe.gov.sa` portal was
  unreachable this pass, but a Wayback Machine snapshot was cross-verified
  against SOCPA's own official PDF of the full law (socpa.org.sa, the
  professional regulator's own source) and two independent qanoonsa.com
  pages, agreeing on all 17 unamended articles.

  **A major anomaly was genuinely verified, not merely suspected**: BOE's
  own archived page flags Articles 1/4/5/19/20 with a "changed-article"
  marker and a changelog popup quoting Royal Decree M/169's (10/8/1446H)
  amended wording — but that SAME page's main displayed body text for
  those 5 articles remained byte-identical, unamended, pre-M/169 wording
  across three snapshots spanning 8+ months after the amendment's own
  gazette publication, confirming genuine staleness of BOE's default
  rendering (not a proxy artifact), joining `traffic_law`/`patent_law`/
  `income_tax_law`/`environmental_law` in the freshness manifest's
  `known_source_staleness_risk: true` flag. This track ingests the
  amended (changelog-popup) wording, cross-verified against SOCPA's PDF,
  not the stale main body.

  **has_per_article_variation flagged for Article 1**: it carries a
  FURTHER, more recent amendment (Council of Ministers Resolution 283,
  22/4/1447H, generalizing the "الوزير" definition) that postdates this
  track's only available BOE snapshot entirely and rests on SOCPA's PDF
  and qanoonsa.com alone, with no Royal Decree number found ratifying it
  and no BOE confirmation at all — flagged, not silently resolved. Other
  flagged discrepancies: no inline BOE article titles; a companion
  Implementing Regulation and SOCPA's own separate organizational statute
  (تنظيم الهيئة) are both confirmed to exist but are out of scope for /
  not conflated with this track. Track under `sources/accounting_auditing/`.
  Validate: `make accounting-auditing-law-track-validate`.

## نظام هيئة الرقابة ومكافحة الفساد — Law (Statute) of the Control and Anti-Corruption Authority, Nazaha (23/1/1446هـ) — BOE-WAYBACK DUAL SNAPSHOT x FAOLEX MIRROR x NEZAMS x QANOONSA, CRITICAL CROSS-TRACK FINDING

- **Law (Statute) of the Control and Anti-Corruption Authority (Royal
  Decree M/25, 23/1/1446H, ratifying Council of Ministers Resolution No.
  68) verified + LLM-ready.** Known as Nazaha (نزاهة). A medium-priority
  coverage-gap identified via the coverage_gap_map research pass, whose
  cited "Royal Order No. 65/A dated 13/4/1432H (2011)" turned out to name
  a **predecessor** body, not this current governing instrument —
  corrected. **24 records, all اصلية**, across **4 أبواب**: تعريفات
  (arts 1-2), جهاز الهيئة ومهماته واختصاصاته (arts 3-17), أحكام متصلة
  بمكافحة جرائم الفساد (arts 18-22), أحكام ختامية (arts 23-24). No
  inline BOE article titles.

  **Predecessor history documented, not ingested**: the National
  Anti-Corruption Commission (الهيئة الوطنية لمكافحة الفساد) was
  established by Royal Order أ/65 (13/4/1432H, 2011); a separate Control
  and Investigation Board and Administrative Investigation body existed
  alongside it; Royal Order أ/277 (15/4/1441H, 2019) merged the latter
  into the former and renamed the combined entity to its current name.
  M/25 (2024) is a wholesale replacement statute for this already-renamed
  Authority, explicitly repealing the predecessor's organizing CoM
  Resolution 165 (1432H) and partially repealing the Civil Service
  Discipline Law (M/7, 1391H, with Article 47 surviving pending a new
  اللائحة الإدارية) — both modeled as supersession-graph edges.

  **VERIFICATION TIER: BOE-WAYBACK DUAL SNAPSHOT x FAOLEX MIRROR x
  NEZAMS x QANOONSA** — the live `laws.boe.gov.sa` portal was
  unreachable this pass, but two independent Wayback Machine snapshots
  of the exact law page (~15.5 months apart) show byte-identical article
  text, further corroborated by a third independent time-point (a
  FAOLEX-hosted PDF mirror of the same BOE page, a distinct fetch date),
  plus nezams.com (partial, Articles 1-14) and qanoonsa.com (full
  structural cross-check of all 24 articles).

  **CRITICAL CROSS-TRACK FINDING, flagged not resolved here**: M/25's
  own enacting decree (clause سابعاً) substitutes "هيئة الرقابة ومكافحة
  الفساد" for "رئاسة أمن الدولة" wherever the latter appears in this
  corpus's already-ingested `anti_bribery_law` (Anti-Bribery Law, M/36,
  1412H) — but `anti_bribery_law`'s own committed text for Articles 17
  and 21 still reads "رئاسة أمن الدولة", meaning that track's text for
  those two articles no longer matches the current wording required by
  this dated legal instrument. This is a finding about `anti_bribery_law`'s
  own source currency, not about this `nazaha_law` track's own primary
  source, which remains independently verified as current — flagged for
  a dedicated follow-up correction pass, not fixed as part of this
  track's own wiring. Other flagged discrepancies: three companion
  instruments (a procedural لائحة under Article 6; اللائحة الإدارية and
  اللائحة المالية under Article 9(1)) are referenced but not confirmed
  issued as of this pass, and are out of scope. Track under
  `sources/nazaha/`. Validate: `make nazaha-law-track-validate`.

## نظام الهيئة العامة للأوقاف — Law of the General Authority for Awqaf (26/2/1437هـ) — BOE-WAYBACK SIX-SNAPSHOT x AWQAF.GOV.SA SCANNED ORIGINAL DECREE x NEZAMS

- **Law of the General Authority for Awqaf (Royal Decree M/11, 26/2/1437H,
  ratifying Council of Ministers Resolution No. 73) verified +
  LLM-ready.** A low-to-medium-priority coverage-gap identified via the
  coverage_gap_map research pass, whose hedge citing "an earlier search
  hit suggesting M/25" is resolved as an unrelated mix-up with this
  corpus's separately-ingested nazaha_law track (a different 1446H
  statute). No distinct substantive Waqf code was found separate from
  this Authority's own organizing statute — substantive waqf matters
  remain governed by classical fiqh as applied by the courts, confirming
  this law is the correct and complete coverage-gap target. **25
  records: 23 اصلية, 2 معدلة** (Articles 6 and 21) — flat structure, no
  أبواب/فصول, no inline BOE article titles.

  **Confirmed supersession of a predecessor**: this law's own Article
  25(1) states it replaces نظام مجلس الأوقاف الأعلى (Supreme Awqaf
  Council System, Royal Decree M/35, 18/7/1386H); Article 25(3) also
  repeals, conflict-only, provisions of the General Authority for
  Guardianship over Minors' Funds Law (M/17, 1427H) — but only as an
  illustrative example within a general conflict-only clause, so this
  is flagged as a genuinely ambiguous case rather than modeled as a
  determinate repeal edge; Article 25(2) carves out Article 223 of the
  Sharia Procedure Law for waqf under the Authority's نظارة.

  **VERIFICATION TIER: BOE-WAYBACK SIX-SNAPSHOT x AWQAF.GOV.SA SCANNED
  ORIGINAL DECREE x NEZAMS** — the live `laws.boe.gov.sa` portal was
  unreachable this pass, but six independent Wayback Machine snapshots
  of the exact law page (21 Nov 2019 through 12 Dec 2025) show 23 of 25
  articles textually identical across all time-points, cross-verified
  against web.awqaf.gov.sa's own scanned original signed decree (visual
  read, no OCR text layer) and nezams.com.

  **Two major verified anomalies carried forward, neither hand-merged
  nor guessed**: (1) Article 6 (board composition) — BOE's own changelog
  logs four amendments across 2017-2022, but BOE's main body text has
  been stable and unchanged across all six snapshots spanning 2019-2025,
  and the changelog's own quoted "before" text does not even match the
  historical wording, implying an unlogged intermediate step; this track
  ingests BOE's stable main body as-is, records all 4 amendments in the
  article's history, and flags the unresolved inconsistency as the
  single highest-priority open item — a genuinely confirmed BOE
  main-body staleness, not a reachability artifact, joining
  `accounting_auditing_law` (and `traffic_law`/`patent_law`/
  `income_tax_law`/`environmental_law`) in the freshness manifest's
  `known_source_staleness_risk: true` flag. (2) Article 21 (fees) — a
  single, clean, fully-quoted amendment (Royal Decree M/72, 1/6/1444H)
  that BOE's main body still doesn't reflect 2+ years later; following
  the accounting_auditing_law precedent for this exact failure mode,
  this track ingests the changelog's quoted amended text as current,
  independently corroborated by press coverage. Other flagged
  discrepancies: three companion implementing regulations already
  issued and findable on web.awqaf.gov.sa are confirmed to exist but are
  out of scope for this track, following established precedent. Track
  under `sources/awqaf/`. Validate: `make awqaf-law-track-validate`.

- **Law of the Saudi Council of Engineers (Royal Decree M/36, 26/9/1423H,
  ratifying Council of Ministers Resolution No. 226) verified + LLM-ready.**
  A low-to-medium-priority coverage-gap identified via the coverage_gap_map
  research pass, whose decree estimate this build confirmed exactly. **9
  records: 7 اصلية, 2 معدلة** (Articles 1 and 6) — flat structure, no
  أبواب/فصول, no inline BOE article titles.

  **Confirmed negative repeal finding**: Article 9's closing clause is
  only a general conflict-only repeal naming no specific instrument;
  secondary sources trace only informal pre-law symposium discussions,
  not any earlier codified engineering-council law, so no repeal edge is
  modeled — the generic clause's absence of a named target is itself
  documented as an ambiguous/excluded case in the supersession graph,
  mirroring the finance_companies_law Article 38 precedent.

  **Decree-number collision flagged**: a separate, currently-in-force
  companion law (نظام مزاولة المهن الهندسية, Law of the Practice of
  Engineering Professions, Royal Decree M/36 dated 19/4/1438H — governing
  licensing, professional accreditation, and disciplinary penalties)
  shares the identical decree number "م/36" at a completely different
  hijri date; documented explicitly to prevent cross-track confusion,
  mirroring the Franchise Law/Anti-Concealment Law M/22 collision
  precedent, and flagged as the strongest follow-up candidate since its
  content more closely matches the coverage-gap-map's original
  licensing/discipline framing than this organizing statute.

  **VERIFICATION TIER: BOE-WAYBACK THREE-SNAPSHOT x SAUDIENG.SA OFFICIAL
  SITE x PRESS CORROBORATION** — the live `laws.boe.gov.sa` portal was
  unreachable this pass, but three independent Wayback Machine snapshots
  of the exact law page (15 Nov 2019 through 15 Sep 2025) were
  cross-verified against three of the Council's own official-website
  snapshots (saudieng.sa, 2017-2022) and a press aggregation (Asharq
  Al-Awsat) corroborating Article 1's supervising-authority transfer.

  **Two major verified anomalies carried forward, neither hand-merged
  nor guessed**: (1) Article 1 (supervising authority) — BOE's own
  changelog logs a clean phrase-substitution (Council of Ministers
  Resolution 57, 20/1/1442H) transferring supervision away from the
  Ministry of Commerce, but BOTH BOE's own main body AND the Council's
  own official website remain stale (unchanged Ministry of Commerce
  wording) across every snapshot checked, even though that same official
  website had already promptly updated its own Article 6 text for a
  separate, later-dated amendment — a genuinely confirmed BOE-and-website
  main-body staleness, not a reachability artifact, joining
  `accounting_auditing_law`/`awqaf_law` (and `traffic_law`/`patent_law`/
  `income_tax_law`/`environmental_law`) in the freshness manifest's
  `known_source_staleness_risk: true` flag; this track ingests the
  changelog-instructed substitution and flags the staleness explicitly,
  without asserting any specific ministry name BOE's own changelog does
  not itself name. (2) Article 6 (board composition) — two layered but
  individually clean, complete-quote amendments (Royal Decree M/60,
  1425H, then Council of Ministers Resolution 388, 1443H); this track
  ingests the more recent complete quote, independently confirmed
  verbatim by the Council's own official website, while BOE's own main
  body remains stuck on the original 2002 text throughout. Other flagged
  discrepancies: a companion Executive Regulation and "Engineer's
  Charter" (reissued 2025) are confirmed to exist on saudieng.sa but are
  out of scope for this track, following established precedent; a minor
  BOE changelog typo (a dropped و) is preserved verbatim, not silently
  corrected. Track under `sources/saudi_engineers/`. Validate:
  `make saudi-engineers-law-track-validate`.

- **Municipal Councils Law (Royal Decree M/61, 4/10/1435H, approving
  Council of Ministers Resolution No. 384) verified + LLM-ready.** A
  low-to-medium-priority coverage-gap identified via the coverage_gap_map
  research pass, distinct from the already-ingested regions_law
  (provincial/regional administration) and municipal_realestate_law
  tracks (municipal real-estate zoning) — no overlap confirmed. **69
  records: ALL 69 اصلية** (never amended per every source checked) —
  organized into **12 فصول (chapters)**, **NO أبواب** grouping above
  them.

  **Confirmed partial repeal of a predecessor**: this law's own Article
  68 explicitly, but only partially, repeals Articles 2(b), 2(c), 7(b),
  and Chapter Two of Part Two of the Law of Municipalities and Villages
  (نظام البلديات والقرى, Royal Decree M/5, 21/2/1397H) — a determinate,
  narrowly-scoped partial repeal, not a full supersession; the
  predecessor law is not yet ingested in this corpus and is flagged as a
  follow-up candidate.

  **VERIFICATION TIER: BOE-WAYBACK SIX-SNAPSHOT x MOMAH.GOV.SA OFFICIAL
  PDF x NEZAMS** — the live `laws.boe.gov.sa` portal returned HTTP 503
  this pass, but six independent Wayback Machine snapshots of the exact
  law page (22 Nov 2019 through 12 Dec 2025) show zero text diffs and
  zero logged amendments throughout, cross-verified against the Ministry
  of Municipal, Rural Affairs and Housing's own official website
  (momah.gov.sa, two independently-dated official PDFs including a
  scanned original of the signed decree) and nezams.com.

  **Zero-amendment stability confirmed** as a genuine positive finding —
  the inverse of this corpus's recurring stale-changelog pattern (where
  BOE's own changelog documents amendments its main body doesn't
  reflect): here, BOE's main body, momah.gov.sa's own PDFs, and
  nezams.com all agree the law has never been amended. Other flagged
  discrepancies: Chapter 10's own heading reads 'مخلفات' (not the
  substantively-expected 'مخالفات') أعضاء المجالس البلدية identically in
  both primary sources — preserved verbatim, not silently corrected;
  four companion implementing regulations (general implementing
  regulation, election regulation, campaign regulation, financial
  regulation) are confirmed to exist on momah.gov.sa but are out of
  scope for this track, following established precedent. Track under
  `sources/municipal_councils/`. Validate:
  `make municipal-councils-law-track-validate`.

- **Law on Printed Materials and Publication / Press Law (Royal Decree
  M/32, 3/9/1421H, approved via Council of Ministers Resolution No. 211)
  verified + LLM-ready.** A low-priority coverage-gap identified via the
  coverage_gap_map research pass, which itself flagged a currency-check
  requirement given the media/press regulatory landscape's evolution
  since 2000. **CURRENCY CHECK CONFIRMED M/32 STILL CURRENT**: a
  comprehensive draft «نظام الإعلام» (Media Law) has been in public
  consultation since Nov 2023 but remains UNENACTED — confirmed via BOE's
  own page (near-live Wayback snapshot, 26 Feb 2026) still reading
  'الحالة: ساري', the General Commission for Audiovisual Media's own
  regulations page listing no new comprehensive law, and independent
  legal-commentary corroboration; a red-herring «نظام تنظيم الإعلام
  الرقمي» that surfaced in research was identified and ruled out as a
  Jordanian law unrelated to Saudi Arabia. **49 records: 43 اصلية, 6
  معدلة** (Articles 5, 9, 36, 37, 38, 40) — flat structure with 6 informal
  content groupings, **NO أبواب/فصول labels** in the source (Articles
  1-12 untitled).

  **Confirmed full repeal of a predecessor**: this law's own Article 48
  explicitly and fully repeals the prior 1982 Press and Publications Law
  (Royal Decree M/17, 13/4/1402H); the predecessor law is not ingested in
  this corpus (historical context only).

  **VERIFICATION TIER: BOE-NEAR-LIVE-WAYBACK x MEDIA.GOV.SA OFFICIAL PDF
  x WIPO LEX x NEZAMS/QANOONSA** — the live `laws.boe.gov.sa` portal was
  unreachable this pass, but a near-live Wayback Machine snapshot (26 Feb
  2026, ~5 months before this build) was structurally cross-verified
  against the Ministry of Media's own official PDF of this exact law
  (media.gov.sa, a genuinely separate regulator, not a BOE mirror),
  further corroborated by WIPO Lex's exact decree/date match and
  nezams.com/qanoonsa.com.

  **GENUINELY CONFIRMED BOE main-body staleness for all 6 amended
  articles**: BOE's own page simultaneously carries a 'changed-article'
  CSS class and a fully-quoted amendment changelog for Articles 5, 9, 36,
  37, 38, and 40, while its main displayed body still shows the
  demonstrably older, pre-amendment wording — the same self-contradictory
  pattern already independently confirmed in this corpus's
  accounting_auditing_law and awqaf_law tracks; this track ingests the
  changelog-instructed amended wording as current and preserves BOE's
  stale wording verbatim in each article's original_2000_text field.
  Article 5 underwent two sequential amendments (Royal Decree M/18,
  1441H, then Council of Ministers Resolution 594, 1442H) both applied
  sequentially; Articles 9/36/37/38/40 were each amended once by Royal
  Decree M/20 (1433H), restructuring the violations-committee and penalty
  regime. Other flagged discrepancies: the Ministry of Media's own PDF
  extracts with word-internal character scrambling (used only
  structurally, not verbatim); Chapter 1 (Articles 1-12) has no source
  heading, left undocumented rather than fabricated; two companion
  instruments (اللائحة التنفيذية لنظام المطبوعات والنشر and نظام
  المؤسسات الصحفية, a DIFFERENT M/20 dated 1422H) confirmed to exist but
  out of scope for this track, flagged as follow-up candidates. Track
  under `sources/press/`. Validate: `make press-law-track-validate`.

- **Law of the Practice of Engineering Professions (Royal Decree M/36,
  19/4/1438H, ratifying Council of Ministers Resolution No. 223) verified
  + LLM-ready.** The strongest follow-up candidate flagged by the
  saudi_engineers_law track's own build pass, since this
  licensing/professional-conduct/discipline statute more closely matches
  the coverage-gap-map's original framing than that 9-article organizing
  statute. **17 records: 16 اصلية, 1 معدلة** (Article 1) — flat
  structure, **NO أبواب/فصول**, no inline BOE article titles.

  **Decree-number collision re-confirmed**: shares the identical bare
  decree number 'م/36' with the already-ingested saudi_engineers_law
  track (Royal Decree M/36, dated 26/9/1423H, "Law of the Saudi Council
  of Engineers") at a completely different hijri date (~15 hijri years
  apart) — two genuinely distinct instruments; this law's own Article 1
  presupposes that Authority's existence rather than repealing or
  replacing it.

  **No predecessor found (confirmed negative finding)**: a full-text
  search of this law's own text found zero repeal-language matches
  anywhere in the preamble or 17 articles.

  **VERIFICATION TIER: BOE-WAYBACK THREE-SNAPSHOT x SAUDIENG.SA OFFICIAL
  PDF x QANOONSA/QANONIAH** — the live `laws.boe.gov.sa` portal was
  unreachable this pass, but three independent Wayback Machine snapshots
  of the exact law page (14 Nov 2019 through 25 Feb 2026, byte-identical
  main-body text throughout) were cross-verified against the Saudi
  Council of Engineers' own official website (saudieng.sa, its own
  hosted PDF, Jun 2025 snapshot, matching word-for-word for Articles
  2-17), further structurally corroborated by qanoonsa.com/qanoniah.com.

  **Genuine three-way anomaly carried forward (Article 1, supervising
  ministry)**: BOE's own changelog quotes Council of Ministers
  Resolution 250 (7/4/1444H) substituting a new ministry name, but BOE's
  own main body has read a THIRD, different wording at every checked
  snapshot since 2019 (predating Resolution 250 itself by ~3 years), and
  saudieng.sa's own current PDF shows a FOURTH, again-different wording
  reflecting a later administrative renaming not itself logged in BOE's
  changelog — following the awqaf_law Article 6 precedent for this exact
  failure mode (a changelog 'before'-phrase that does not match the
  article's own observed history blocks safe mechanical substitution),
  this track does NOT fabricate or guess a merged text; it ingests BOE's
  own stable main-body wording as Article 1's current text, marks it
  معدلة (BOE's own metadata flags it as changed), and documents the full
  three-way divergence, since corroborating evidence (Resolution 250
  itself, saudieng.sa's differing wording, and a qanoonsa.com-indexed
  reissued Implementing Regulation from the Ministry of Municipal, Rural
  Affairs and Housing) confirms a real supervising-ministry transfer
  occurred even though no single primary source could confirm the exact
  current wording. Other flagged discrepancies: three companion
  instruments (اللائحة التنفيذية لنظام مزاولة المهن الهندسية, ميثاق
  المهندس, and لائحة الوظائف الهندسية) are confirmed to exist but are
  out of scope for this track, following established precedent. Track
  under `sources/engineering_practice/`. Validate:
  `make engineering-practice-law-track-validate`.

> **End of individually-narrated tracks.** The sections above cover the
> Companies Law's full build plus the tracks added through this point in the
> corpus's history. Tracks added after this point (the corpus is now at 291
> total) are documented only in `data/corpus_registry/corpus_registry.json`
> (per-track status, record counts, source authority, data/validator paths)
> and the `notes` field of their own registry entry — not as prose here.
> This is a deliberate, sustainable choice rather than an oversight: keeping
> every track narrated in this file in full prose stopped scaling once the
> corpus passed roughly this size. If you are looking for a specific track
> and don't find it above, check the registry first.

## Corpus-value features — verification tiers, coverage gap map, supersession graph, cross-reference graph

- **Verification-tier taxonomy** — a purely additive, read-only derived
  classification layer over all 236 tracks' existing free-text
  `official_text_status`/`source_authority` fields, normalized into 4 fixed
  confidence tiers (`TIER_1_PRIMARY_MULTI_SOURCE` through
  `TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE`) so a downstream RAG
  application can filter by confidence programmatically. Current
  distribution: **106 Tier 1, 46 Tier 2, 25 Tier 3, 23 Tier 4**. No existing
  track's text, status claims, or per-article data is modified or
  recomputed — 21 tracks with documented per-article confidence variation
  (Traffic Law, Capital Market Law, Income Tax Law's Chapter 10, etc.) are
  flagged `has_per_article_variation` with a pointer back to their own
  documentation instead. Full methodology and every non-obvious judgment
  call documented in Arabic at
  `reports/verification_tiers/VERIFICATION_TIERS_METHODOLOGY_AR.md`.
  Output: `data/corpus_verification_tiers/corpus_verification_tiers.json`.
  Validate: `make corpus-verification-tiers-validate`.
- **Coverage gap map** — a research-only planning document
  (`reports/coverage_gap_map/`) identifying significant Saudi laws not yet
  in the corpus, ranked by priority with existence-confidence flags, to
  keep future research work systematic rather than ad hoc. The original
  24-candidate scan has since been fully built out (Zakat Collection Law,
  its top priority, first -- see above; the map's own estimates for it were
  subsequently corrected during dedicated research, a documented example of
  why this map is explicitly labeled a starting point requiring
  verification, not a build-ready source). A fresh scan run this session
  against all 153 ingested tracks found **16 new candidate gaps**, mostly
  Implementing Regulations of already-ingested base laws following the same
  pattern this session filled for health_system/food/travel_documents/
  nationality (VAT, Income Tax, Traffic, Anti-Money Laundering, Competition,
  Patent, Trademark, E-Commerce, Franchise, Cooperative Insurance Companies
  Control, and a fragmented Environmental-Law regulation family), plus
  wholly new subject areas (Water Law, Electricity Law, Agriculture Law) and
  one currency-risk flag: the Communications, Space and Information
  Technology Law (Council of Ministers Resolution 592, 1/11/1443H) appears
  to supersede the base Telecommunications Act underlying this corpus's own
  `telecommunications_law` track, needing dedicated confirmation before that
  track can be treated as current.
- **Supersession/repeal graph** — a purely additive, read-only derived
  layer extracting every EXPLICITLY-STATED repeal/supersession relationship
  already documented in each track's own `notes`/`official_source.json`
  (never inferred from age or topical similarity alone). **83 edges** (72
  `repeals_full`, 10 `repeals_partial`, 1 `superseded_by`) plus **2 documented
  concurrent-title-collisions** correctly excluded from repeal edges (the
  two social-insurance laws; Franchise Law/Anti-Concealment Law's M/22
  decree-number reuse) and **27 genuinely ambiguous cases** flagged with
  reasoning rather than forced into a classification (Zakat Law's
  unverified predecessor-repeal claim; Anti-Trafficking Law's unenacted
  2022 draft replacement; Trademark Law's unresolved earlier repeal-chain
  leg; Commercial Courts Implementing Regulation's deliberately-not-modeled
  topical overlap with the Evidence Law; Finance Companies Control Law's
  general non-specific Article 38 repeal clause naming no prior statute;
  Law of the General Authority for Awqaf's conflict-only Article 25(3)
  repeal clause naming one example instrument, not a determinate repeal;
  Law of the Saudi Council of Engineers' general non-specific Article 9
  repeal clause naming no prior statute, a confirmed negative finding;
  Foreigners' Residency Law's general non-specific Article 64 repeal
  clause naming no prior statute, a confirmed negative finding; Food
  Law's general non-specific Article 45 repeal clause naming no prior
  statute, a confirmed negative finding; Health System Law's general
  non-specific Article 19 repeal clause naming no prior statute, a
  confirmed negative finding; the Statute of the National Cybersecurity
  Authority's general non-specific Article 15 repeal clause naming no
  prior statute, a confirmed negative finding; the Cybersecurity
  Authority's Regulatory (Legal) Enablers own general non-specific final
  بند (سابعاً) repeal clause naming no prior statute, a confirmed
  negative finding, independently re-confirmed to have no amendment/
  repeal relationship to the parent statute either; Premium Residency
  Law's Article 14 naming no predecessor at all, a confirmed negative
  finding, a wholly new residency category coexisting with the
  already-ingested residency_law rather than superseding it, mirroring
  the social_insurance_law/social_insurance_legacy_law naming-distinction
  precedent; nationality_regulation's own 35 articles name no repealed
  predecessor instrument at all -- it is the first and only Implementing
  Regulation issued for nationality_law since that Law's own 1374H
  enactment; health_system_regulation's own 10 recovered articles name no
  repealed predecessor instrument at all -- it is the first Implementing
  Regulation issued under health_system_law's own Article 18 mandate, a
  confirmed negative repeal finding, with its coverage genuinely PARTIAL,
  Article 1 and Articles 12-19 excluded not fabricated, a source-access
  limitation rather than a supersession-graph relationship; food_regulation's
  own 85 articles name no repealed predecessor instrument at all -- it is
  the first Implementing Regulation issued under food_law's own authority,
  a confirmed negative repeal finding, with a separate penalty-classification
  table confirmed out of scope, not a supersession-graph relationship);
  vat_regulation's own 82 articles name no repealed predecessor Implementing
  Regulation at all -- it is the first and only Implementing Regulation
  issued under vat_law's own authority, a confirmed negative repeal finding,
  consolidating 11 amending Board resolutions rather than repealing/replacing
  a prior regulation; income_tax_regulation's own 74 articles name no
  repealed predecessor Implementing Regulation at all -- it is the first
  and only Implementing Regulation issued under income_tax_law's own
  authority, a confirmed negative repeal finding, consolidating 13
  ministerial amendments rather than repealing/replacing a prior
  regulation -- Resolution 2568's formal repeal of 25 natural-gas articles
  is an intra-track amendment captured per-article, not a
  supersession-graph relationship between two distinct tracks; aml_regulation's
  own 25 ingested articles name no repealed predecessor Implementing Regulation
  at all -- the supersession of the prior legal regime is derivative, via the
  already-ingested aml_law track's own Article 51 replacing the old AML Law
  M/31, a confirmed negative finding; a separate, genuinely distinct older
  1430H regulation was confirmed to exist during research but deliberately
  not ingested or mixed in; rett_law's own Article 20(2) carries only a
  generic conflict-repeal clause naming no predecessor -- the substantive
  predecessor context, Royal Order A/84 1442H which first imposed the RETT
  scheme at royal-order level, is disclosed as historical context only, not
  a Law-text-asserted repeal).
  Output:
  `data/corpus_supersession_graph/corpus_supersession_graph.json`.
  Validate: `make corpus-supersession-graph-validate`.
- **Cross-reference graph between articles** — a best-effort, pattern-based
  extraction of article-to-article citations across the unified index
  (8425 records at time of build), enabling "see also" navigation.
  **1,777 references** (1,570 intra-law, 207 inter-law: 150 resolved to a
  corpus track, 57 recorded with `target_track_id: null` and the raw law
  name for out-of-corpus instruments). Built on a custom Arabic
  feminine-ordinal-to-integer parser (compound tens, "بعد المائة"
  hundreds constructs), cross-validated against the corpus's own
  ordinal-word article titles (&gt;99.8% round-trip accuracy). **⚠
  EXPLICITLY NOT independently legally verified** — this is regex/pattern-based
  best-effort extraction (documented in the output's own
  `extraction_caveat` field), favoring precision over recall; known
  limitations (ordinal parsing cap, lookahead-heuristic scope detection,
  unresolved same-title-collision cases, unhandled plural "المواد"
  citations) are documented rather than silently accepted. Output:
  `data/corpus_cross_reference_graph/corpus_cross_reference_graph.json`.
  Validate: `make corpus-cross-reference-graph-validate`.
- **Cross-law glossary of defined terms** — a purely additive, read-only
  derived index of every law's own definitions article, grouping
  identical terms across the tracks that define them so a consumer can
  query one term and see every law's own definition side by side.
  **696 terms / 1,046 definitions** across **81 of 123 tracks** with a
  parseable definitions article (42 tracks skipped, each with a logged
  reason — genuinely definitions-free Sharia/constitutional codes,
  tabular/form-only content, or a pure cross-reference to another law's
  own Article 1). Confirms real, practically useful divergence: **«الهيئة»**
  names a different institution across 18 tracks (SAMA, CMA, GACA, SFDA,
  CST, ZATCA, etc.), **«الوزير»** points to a different ministry across 32
  tracks, and **«المشترك»** is defined three genuinely different ways
  across `social_insurance_law`, `social_insurance_legacy_law`, and
  `chambers_of_commerce_law`. Every extracted term/definition is
  byte-exact-verified against its source article. Known limitations
  (non-standard phrasing can be missed; alef/hamza variants are
  deliberately not unified for grouping, to avoid conflating different
  words; a source document's own missing punctuation can swallow one
  term's definition into the next) are documented in the output rather
  than silently accepted. Output: `data/corpus_glossary/corpus_glossary.json`.
  Validate: `make corpus-glossary-validate`.
- **Machine-readable schema manifest** — a single authoritative JSON Schema
  document (`data/schema_manifest/corpus_schema_manifest.json`, draft
  2020-12) describing all **9 distinct document types** used across this
  corpus: per-track `official_source`/`verified_record`/`llm_ready_layer`,
  plus the six corpus-wide derived layers (unified index, registry,
  verification tiers, supersession graph, cross-reference graph,
  glossary). Built from surveying 7 tracks spanning this corpus's
  different conventions/eras plus all 5 corpus-wide generator scripts.
  **Honest finding:** `official_source.json` is the **least standardized
  layer** in the corpus — a full sweep found only a minority of 117+ real
  files match either modeled convention, with `civil_transactions_law`
  using an entirely different legacy schema. Track-specific fields are
  traced to their pioneering track (`decree_transitional_provisions_ar`:
  `social_insurance_law` only; per-article `verification_tier`: pioneered
  by `traffic_law`). The generator self-validates against real corpus
  files on every run and a full `jsonschema` semantic validation pass
  found **100% valid** for all mechanically-generated corpus-wide layers.
  A companion English-language guide for external integrators (e.g. a
  RAG application built on top of this corpus) is at
  `reports/schema_manifest/SCHEMA_MANIFEST_GUIDE_EN.md`. Validate:
  `make corpus-schema-manifest-validate`.
- **Embeddings-ready chunking layer** — a purely additive text-segmentation
  layer over the unified index (11277 records), preparing the corpus for a
  real vector-embedding RAG pipeline without computing any embeddings
  itself (word-based chunking, deliberately not tied to any specific
  embedding model's tokenizer). Parameters chosen from the corpus's own
  real length distribution (median 38 words, p99 345 words): a 350-word
  chunk target/split-threshold, 20% (70-word) overlap, 500-word hard max.
  **11,900 chunks from 11,553 source records** — only **188 records (1.627%)**
  needed splitting into multiple chunks (e.g. `customs_regulation`'s
  6,797-word Article 1), confirming most Saudi statutory articles are
  short/medium and need no splitting at all. Every multi-chunk article's
  full original text was verified to reconstruct byte-identically from
  its own chunks (validated for all 180, not just a sample), and every
  chunk retains a back-reference (`source_record_id`, `article_number`,
  `chunk_index`, `total_chunks_for_this_article`) to its parent article.
  Output: `data/corpus_chunking_layer/corpus_chunking_layer.jsonl`.
  Validate: `make corpus-chunking-layer-validate`.
- **Freshness/drift monitor** — a purely additive, two-part tool for
  periodically re-checking whether a track's primary source may have
  drifted since it was captured, without needing a full research/build
  pass every time. **(1)** A deterministic manifest
  (`data/corpus_freshness_manifest/corpus_freshness_manifest.json`, no
  network calls, no fabricated timestamps) surveying all 161 tracks'
  recorded source authorities/URLs and cross-referencing the verification-tier
  taxonomy. **Exactly 14 tracks flagged `known_source_staleness_risk: true`**
  — `accounting_auditing_law`, `awqaf_law`, `civil_status_law`,
  `domestic_labor_regulation`, `engineering_practice_law`, `environmental_law`,
  `income_tax_law`, `nationality_law`, `nationality_regulation`, `patent_law`,
  `patent_regulation`, `press_law`, `saudi_engineers_law`, `traffic_law` —
  each because its own build already documented, independently, that its
  primary source portal was confirmed genuinely stale (not a proxy
  artifact); every other track with merely stale *language* about a
  ministry name or a secondary source was deliberately left unflagged.
  **(2)** A standalone, read-only live-check CLI
  (`scripts/check_corpus_freshness.py --track <id>` or `--all`) that
  attempts a single HEAD/GET per recorded URL and reports reachable /
  possible-drift / could-not-check — explicitly never treating a network
  block as "confirmed unreachable," and never attempting any
  egress-policy-bypass workaround. The live-check tool is intentionally
  **not** part of the deterministic QA gate (network-dependent); only the
  manifest generator is. Validate:
  `make corpus-freshness-manifest-validate`.

## Strict QA gate

- **`make qa-gate`** — one command, everything must pass: **[1]** every
  `scripts/validate_*.py` in the repository (323 today — discovered from the filesystem, so any new
  validator automatically joins the gate; exclusions require a written reason in the script's
  `EXCLUDED` dict, currently empty); **[2]** generator idempotence — 250 deterministic generators
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
