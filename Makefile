# Saudi Companies Law — multi-book corpus build
# Structured-first: JSON is canonical; JSONL/HTML/PDF are generated from it.
# Book One (Articles 1-34) and Book Two (Articles 35-50) build independently.

PY ?= python3
export PYTHONPATH := src:$(PYTHONPATH)

.PHONY: help data jsonl markdown validate book1-validate test html pdf build all clean \
        book2-data book2-jsonl book2-validate book2-html book2-pdf book2-build books-build \
        book3-data book3-jsonl book3-validate book3-html book3-pdf book3-build \
        book4-coverage book4-validate book4-model-check book4-coverage-check \
        book4-section1-data book4-section1-jsonl book4-section1-html book4-section1-build \
        book4-section2-data book4-section2-jsonl book4-section2-html book4-section2-build \
        book4-section3-data book4-section3-jsonl book4-section3-html book4-section3-build \
        book4-section4-data book4-section4-jsonl book4-section4-html book4-section4-build \
        book4-section5-data book4-section5-jsonl book4-section5-html book4-section5-build \
        arabic-legal-llm-data arabic-legal-llm-book4-section2-data \
        arabic-legal-llm-book4-section3-data arabic-legal-llm-book4-section4-data \
        arabic-legal-llm-book4-section5-data arabic-legal-llm-validate \
        official-english-source-extract official-english-source-validate \
        english-reference-book1-data english-reference-book1-jsonl \
        english-reference-book2-data english-reference-book2-jsonl \
        english-reference-book3-data english-reference-book3-jsonl \
        english-reference-book4-section1-data english-reference-book4-section1-jsonl \
        english-reference-book4-section2-data english-reference-book4-section2-jsonl \
        english-reference-book4-section3-data english-reference-book4-section3-jsonl \
        english-reference-book4-section4-data english-reference-book4-section4-jsonl \
        english-reference-book4-section5-data english-reference-book4-section5-jsonl \
        english-reference-validate \
        english-legal-llm-book1-data english-legal-llm-book2-data english-legal-llm-book3-data \
        english-legal-llm-book4-section1-data english-legal-llm-book4-section2-data \
        english-legal-llm-book4-section3-data english-legal-llm-book4-section4-data \
        english-legal-llm-book4-section5-data english-legal-llm-validate \
        chinese-legal-llm-book4-section1-data chinese-legal-llm-book4-section2-data \
        chinese-legal-llm-book4-section3-data chinese-legal-llm-book4-section4-data \
        chinese-legal-llm-book4-section5-data chinese-legal-llm-validate \
        official-arabic-foundation-validate official-arabic-user-provided-data \
        official-arabic-ingestion-validate official-arabic-verification-report-validate \
        official-arabic-manual-review-queue-validate official-arabic-p0-article3-review-validate \
        official-arabic-queue-p0-resolution-validate official-arabic-boe-source-provenance-validate \
        official-arabic-legal-llm-full-data official-arabic-legal-llm-full-validate \
        english-reference-full-281-data english-reference-full-281-validate \
        official-english-legal-llm-full-data official-english-legal-llm-full-validate \
        chinese-bab1-original-pdf-translation-review-data \
        chinese-bab1-original-pdf-translation-review-validate \
        chinese-all-babs-source-inventory-data chinese-all-babs-source-inventory-validate \
        chinese-internal-legal-llm-isolable-data chinese-internal-legal-llm-isolable-validate \
        chinese-internal-llm-semantic-qa-gap-plan-data \
        chinese-internal-llm-semantic-qa-gap-plan-validate \
        chinese-remediation-backlog-source-packet-plan-data \
        chinese-remediation-backlog-source-packet-plan-validate \
        chinese-remediation-batch-p0-001-validate \
        chinese-remediation-batch-p0-001-qa-validate \
        chinese-remediation-batch-p0-001-minor-fixes-validate \
        chinese-remediation-batch-p0-002-validate \
        chinese-remediation-batch-p0-002-qa-validate \
        chinese-remediation-batch-p0-003-validate \
        chinese-remediation-batch-p0-003-qa-validate \
        chinese-remediation-batch-p0-004-validate \
        chinese-remediation-batch-p0-004-qa-validate \
        chinese-remediation-batch-p0-005-validate \
        chinese-remediation-batch-p0-005-qa-validate \
        chinese-remediation-batch-p1-001-validate \
        chinese-remediation-batch-p1-001-qa-validate \
        chinese-remediation-batch-p1-002-validate \
        chinese-remediation-batch-p1-002-qa-validate \
        chinese-remediation-batch-p1-003-validate \
        chinese-remediation-batch-p1-003-qa-validate \
        chinese-remediation-batch-p1-004-validate \
        chinese-remediation-batch-p1-004-qa-validate \
        chinese-remediation-batch-p2-001-validate \
        chinese-remediation-batch-p2-001-qa-validate \
        chinese-remediation-batch-p2-002-validate \
        chinese-remediation-batch-p2-002-qa-validate \
        chinese-remediation-batch-p2-003-validate \
        chinese-remediation-batch-p2-003-qa-validate \
        chinese-remediation-batch-p2-004-validate \
        chinese-remediation-batch-p2-004-qa-validate \
        chinese-remediation-batch-p2-005-validate \
        chinese-remediation-batch-p2-005-qa-validate \
        chinese-remediation-batch-p3-conf-001-validate \
        chinese-remediation-batch-p3-conf-001-qa-validate \
        legal-corpus-factory-foundation-validate \
        repository-ux-docs-validate \
        repository-rename-readiness-validate \
        chinese-remediation-program-closure-validate \
        implementing-regulations-intake-scaffold-validate \
        implementing-regulations-listed-jsc-arabic-source-validate \
        implementing-regulations-general-arabic-source-validate \
        implementing-regulations-general-arabic-legal-llm-data \
        implementing-regulations-general-arabic-legal-llm-validate \
        implementing-regulations-listed-jsc-arabic-legal-llm-data \
        implementing-regulations-listed-jsc-arabic-legal-llm-validate \
        implementing-regulations-arabic-program-closure-data \
        implementing-regulations-arabic-program-closure-validate \
        corpus-registry-data \
        corpus-registry-validate \
        corpus-export-primary-arabic-data \
        corpus-export-primary-arabic-validate \
        corpus-local-search-validate \
        corpus-local-search-eval-validate \
        corpus-retrieval-context-pack-validate \
        corpus-retrieval-prompt-pack-validate \
        corpus-citation-support-checker-validate \
        corpus-retrieval-workflow-runner-validate \
        corpus-retrieval-demo-scenarios-validate \
        corpus-retrieval-operator-demo-pack-validate \
        pdpl-arabic-law-next-layer-validate \
        pdpl-implementing-regulation-arabic-next-layer-validate \
        pdpl-implementing-regulation-arabic-cleaned-validate \
        pdpl-implementing-regulation-arabic-verified-validate \
        pdpl-implementing-regulation-arabic-legal-llm-validate \
        pdpl-arabic-law-verified-validate \
        pdpl-arabic-law-legal-llm-validate \
        investment-law-verified-validate \
        investment-law-legal-llm-validate \
        investment-regulation-verified-validate \
        investment-regulation-legal-llm-validate \
        civil-transactions-law-verified-validate \
        civil-transactions-law-legal-llm-validate \
        corpus-unified-llm-index-validate \
        corpus-retrieval-eval-validate \
        gtpl-law-track-validate \
        gtpl-regulation-track-validate \
        labor-law-track-validate \
        labor-regulation-track-validate \
        labor-annex1-track-validate \
        labor-annex34-tracks-validate \
        labor-annex2-track-validate \
        labor-annex5-track-validate \
        evidence-law-track-validate \
        evidence-companions-tracks-validate \
        qa-gate

help:
	@echo "Book One (default) targets:"
	@echo "  make data          - regenerate Book One canonical JSON + coverage"
	@echo "  make jsonl         - build Book One data/articles/*.jsonl"
	@echo "  make markdown      - render Book One content/{ar,zh,bilingual} Markdown"
	@echo "  make validate      - validate Book One (schema + QA)"
	@echo "  make book1-validate- alias for 'make validate'"
	@echo "  make html          - render dist/book1.html (searchable canonical text)"
	@echo "  make pdf           - render dist/book1.pdf via WeasyPrint (optional)"
	@echo "  make build         - Book One: jsonl + markdown + validate + html (+ pdf)"
	@echo "  make test          - run the full pytest suite (both books)"
	@echo "  make all           - data + build + test"
	@echo ""
	@echo "Book Two (شركة التضامن / 无限公司) targets:"
	@echo "  make book2-data    - regenerate Book Two canonical JSON + coverage"
	@echo "  make book2-jsonl   - build Book Two data/articles/*.jsonl"
	@echo "  make book2-validate- validate Book Two (schema + QA)"
	@echo "  make book2-html    - render dist/book2.html + Book Two Markdown"
	@echo "  make book2-pdf     - render dist/book2.pdf via WeasyPrint (optional)"
	@echo "  make book2-build   - Book Two: jsonl + validate + html (+ pdf)"
	@echo ""
	@echo "Book Three (شركة التوصية البسيطة / 两合公司) targets:"
	@echo "  make book3-data    - regenerate Book Three canonical JSON + coverage"
	@echo "  make book3-jsonl   - build Book Three data/articles/*.jsonl"
	@echo "  make book3-validate- validate Book Three (schema + QA)"
	@echo "  make book3-html    - render dist/book3.html + Book Three Markdown"
	@echo "  make book3-pdf     - render dist/book3.pdf via WeasyPrint (optional)"
	@echo "  make book3-build   - Book Three: jsonl + validate + html (+ pdf)"
	@echo "  make books-build   - build all books"
	@echo ""
	@echo "  make clean         - remove generated dist/ artifacts and JSONL files"
	@echo ""
	@echo "PDPL Arabic Law targets:"
	@echo "  make pdpl-arabic-law-next-layer-validate - validate Arabic PDPL law next-layer records"

# -- Book One (default; unchanged behaviour) -------------------------------
data:
	$(PY) scripts/gen_articles.py

jsonl:
	$(PY) scripts/build_jsonl.py

markdown:
	$(PY) scripts/render_markdown.py

validate:
	$(PY) scripts/validate_corpus.py --book 1

book1-validate: validate

test:
	$(PY) -m pytest

html:
	$(PY) scripts/render_book_html.py

pdf: html
	-$(PY) scripts/render_pdf_weasyprint.py

build: jsonl markdown validate html
	-$(PY) scripts/render_pdf_weasyprint.py
	@echo "build complete: dist/book1.html (canonical text) + dist/book1.pdf (if WeasyPrint present)"

all: data build test

# -- Book Two --------------------------------------------------------------
book2-data:
	$(PY) scripts/gen_book2_articles.py

book2-jsonl:
	$(PY) scripts/build_book2_jsonl.py

book2-validate:
	$(PY) scripts/validate_corpus.py --book 2

book2-html:
	$(PY) scripts/render_book2_html.py

book2-pdf: book2-html
	-$(PY) scripts/render_book2_pdf_weasyprint.py

book2-build: book2-jsonl book2-validate book2-html
	-$(PY) scripts/render_book2_pdf_weasyprint.py
	@echo "book2 build complete: dist/book2.html (canonical text) + dist/book2.pdf (if WeasyPrint present)"

# -- Book Three ------------------------------------------------------------
book3-data:
	$(PY) scripts/gen_book3_articles.py

book3-jsonl:
	$(PY) scripts/build_book3_jsonl.py

book3-validate:
	$(PY) scripts/validate_corpus.py --book 3

book3-html:
	$(PY) scripts/render_book3_html.py

book3-pdf: book3-html
	-$(PY) scripts/render_book3_pdf_weasyprint.py

book3-build: book3-jsonl book3-validate book3-html
	-$(PY) scripts/render_book3_pdf_weasyprint.py
	@echo "book3 build complete: dist/book3.html (canonical text) + dist/book3.pdf (if WeasyPrint present)"

books-build: build book2-build book3-build

# -- Book Four (model 1b — infrastructure stage; NO content build) ----------
book4-coverage:
	$(PY) scripts/gen_book4_coverage.py

book4-validate:
	$(PY) scripts/validate_corpus.py --book 4

# Convenience aliases (same infrastructure validation; no content is built).
book4-model-check: book4-validate
book4-coverage-check: book4-validate

# -- Book Four Section 1 (provisions for explicit articles 58,59,60,66) ------
book4-section1-data:
	$(PY) scripts/gen_book4_section1_provisions.py

book4-section1-jsonl:
	$(PY) scripts/build_book4_section1_jsonl.py

book4-section1-html:
	$(PY) scripts/render_book4_section1_html.py

book4-section1-build: book4-section1-data book4-section1-jsonl book4-validate book4-section1-html
	@echo "book4 section1 build complete: provisions (58,59,60,66) + section HTML (NOT full Book Four)"

# -- Book Four Section 2 (provisions for explicit articles 67,68,71,72,75,77) --
book4-section2-data:
	$(PY) scripts/gen_book4_section2_provisions.py

book4-section2-jsonl:
	$(PY) scripts/build_book4_section2_jsonl.py

book4-section2-html:
	$(PY) scripts/render_book4_section2_html.py

book4-section2-build: book4-section2-data book4-section2-jsonl book4-validate book4-section2-html
	@echo "book4 section2 build complete: provisions (67,68,71,72,75,77) + section HTML (NOT full Book Four)"

# -- Book Four Section 3 (provisions for explicit articles 85,87,92,93,99,101,102) --
book4-section3-data:
	$(PY) scripts/gen_book4_section3_provisions.py

book4-section3-jsonl:
	$(PY) scripts/build_book4_section3_jsonl.py

book4-section3-html:
	$(PY) scripts/render_book4_section3_html.py

book4-section3-build: book4-section3-data book4-section3-jsonl book4-validate book4-section3-html
	@echo "book4 section3 build complete: provisions (85,87,92,93,99,101,102) + section HTML (NOT full Book Four)"

# -- Book Four Section 4 (provisions for explicit articles 108,113,115,117) --
# Owner Option 1 reconciliation: Article 110 reclassified not_explicit_in_source.
book4-section4-data:
	$(PY) scripts/gen_book4_section4_provisions.py

book4-section4-jsonl:
	$(PY) scripts/build_book4_section4_jsonl.py

book4-section4-html:
	$(PY) scripts/render_book4_section4_html.py

book4-section4-build: book4-section4-data book4-section4-jsonl book4-validate book4-section4-html
	@echo "book4 section4 build complete: provisions (108,113,115,117) + section HTML (NOT full Book Four)"

# -- Book Four Section 5 (provisions for explicit articles 123,124,126,127,128,129,130,132,133) --
# Coverage matrix and source PDF agree on the explicit set (no reclassification).
book4-section5-data:
	$(PY) scripts/gen_book4_section5_provisions.py

book4-section5-jsonl:
	$(PY) scripts/build_book4_section5_jsonl.py

book4-section5-html:
	$(PY) scripts/render_book4_section5_html.py

book4-section5-build: book4-section5-data book4-section5-jsonl book4-validate book4-section5-html
	@echo "book4 section5 build complete: provisions (123,124,126,127,128,129,130,132,133) + section HTML (NOT full Book Four)"

# -- Arabic Legal LLM-ready layer (structured Arabic metadata) ---------------
arabic-legal-llm-data:
	$(PY) scripts/gen_arabic_legal_llm_book4_section1.py
	$(PY) scripts/gen_arabic_legal_llm_books1_3.py
	$(PY) scripts/gen_arabic_legal_llm_book4_section2.py
	$(PY) scripts/gen_arabic_legal_llm_book4_section3.py
	$(PY) scripts/gen_arabic_legal_llm_book4_section4.py
	$(PY) scripts/gen_arabic_legal_llm_book4_section5.py

arabic-legal-llm-book4-section2-data:
	$(PY) scripts/gen_arabic_legal_llm_book4_section2.py

arabic-legal-llm-book4-section3-data:
	$(PY) scripts/gen_arabic_legal_llm_book4_section3.py

arabic-legal-llm-book4-section4-data:
	$(PY) scripts/gen_arabic_legal_llm_book4_section4.py

arabic-legal-llm-book4-section5-data:
	$(PY) scripts/gen_arabic_legal_llm_book4_section5.py

arabic-legal-llm-validate:
	$(PY) scripts/validate_arabic_legal_llm.py

# -- Official English guidance source (intake + provenance + planning only) --
official-english-source-extract:
	$(PY) scripts/extract_official_english_pdf_text.py

official-english-source-validate:
	$(PY) scripts/validate_official_english_source.py

# -- Official English guidance REFERENCE layer (Book One pilot; Articles 1–34) --
# Reference/alignment text only — NOT the English Legal LLM-ready layer.
english-reference-book1-data:
	$(PY) scripts/gen_english_reference_book1.py

# The JSONL is produced together with the JSON by the generator above.
english-reference-book1-jsonl: english-reference-book1-data

# Books Two and Three share the Book One extraction/segmentation logic.
english-reference-book2-data english-reference-book3-data:
	$(PY) scripts/gen_english_reference_books2_3.py

english-reference-book2-jsonl: english-reference-book2-data
english-reference-book3-jsonl: english-reference-book3-data

# Book Four Section 1 — model 1b provision-covered articles only (58,59,60,66).
english-reference-book4-section1-data:
	$(PY) scripts/gen_english_reference_book4_section1.py

english-reference-book4-section1-jsonl: english-reference-book4-section1-data

# Book Four Section 2 — model 1b provision-covered articles only (67,68,71,72,75,77).
english-reference-book4-section2-data:
	$(PY) scripts/gen_english_reference_book4_section2.py

english-reference-book4-section2-jsonl: english-reference-book4-section2-data

# Book Four Section 3 — model 1b provision-covered articles only (85,87,92,93,99,101,102).
# Article 100 is out of scope (exists in the English source but maps to Article 101).
english-reference-book4-section3-data:
	$(PY) scripts/gen_english_reference_book4_section3.py

english-reference-book4-section3-jsonl: english-reference-book4-section3-data

# Book Four Section 4 — model 1b provision-covered articles only (108,113,115,117).
# Article 110 is out of scope (exists in the English source but reclassified uncovered).
english-reference-book4-section4-data:
	$(PY) scripts/gen_english_reference_book4_section4.py

english-reference-book4-section4-jsonl: english-reference-book4-section4-data

# Book Four Section 5 — model 1b provision-covered articles only
# (123,124,126,127,128,129,130,132,133). Articles 134 & 135 are out of scope
# (exist in the English source but cross-reference only in the model-1b source).
english-reference-book4-section5-data:
	$(PY) scripts/gen_english_reference_book4_section5.py

english-reference-book4-section5-jsonl: english-reference-book4-section5-data

english-reference-validate:
	$(PY) scripts/validate_english_reference.py

# -- English Legal LLM-ready layer --
# legal_rule_text_en is verbatim from the English reference; no generated summaries.
# Books 1-3 backfill: one article_reference record per article (1-34 / 35-50 / 51-57).
english-legal-llm-book1-data:
	$(PY) scripts/gen_english_legal_llm_book1.py

english-legal-llm-book2-data:
	$(PY) scripts/gen_english_legal_llm_book2.py

english-legal-llm-book3-data:
	$(PY) scripts/gen_english_legal_llm_book3.py

# repo book4 Section 1 — provision-covered articles only (58,59,60,66).
english-legal-llm-book4-section1-data:
	$(PY) scripts/gen_english_legal_llm_book4_section1.py

# Book Four Section 2 — provision-covered articles only (67,68,71,72,75,77).
english-legal-llm-book4-section2-data:
	$(PY) scripts/gen_english_legal_llm_book4_section2.py

# Book Four Section 3 — provision-covered articles only (85,87,92,93,99,101,102).
english-legal-llm-book4-section3-data:
	$(PY) scripts/gen_english_legal_llm_book4_section3.py

# Book Four Section 4 — provision-covered articles only (108,113,115,117).
english-legal-llm-book4-section4-data:
	$(PY) scripts/gen_english_legal_llm_book4_section4.py

# Book Four Section 5 — provision-covered articles only (123,124,126,127,128,129,130,132,133).
english-legal-llm-book4-section5-data:
	$(PY) scripts/gen_english_legal_llm_book4_section5.py

english-legal-llm-validate:
	$(PY) scripts/validate_english_legal_llm.py

# -- Chinese Legal LLM-ready layer (PILOT: Book Four Section 1 only; 58,59,60,66) --
# legal_rule_text_zh is verbatim from each provision's chinese_translation; internal
# working translation only (Arabic governs); no new/machine translation.
chinese-legal-llm-book4-section1-data:
	$(PY) scripts/gen_chinese_legal_llm_book4_section1.py

# Book Four Section 2 — provision groups only ([67,68],[71],[72],[75],[77]).
chinese-legal-llm-book4-section2-data:
	$(PY) scripts/gen_chinese_legal_llm_book4_section2.py

# Book Four Section 3 — provision groups only ([85,87],[92,93],[99],[101],[102]).
chinese-legal-llm-book4-section3-data:
	$(PY) scripts/gen_chinese_legal_llm_book4_section3.py

# Book Four Section 4 — provision groups only ([108],[113],[115],[117]).
chinese-legal-llm-book4-section4-data:
	$(PY) scripts/gen_chinese_legal_llm_book4_section4.py

# Book Four Section 5 — provision groups only ([123,124],[126,127],[128,129,130],[132],[133]).
chinese-legal-llm-book4-section5-data:
	$(PY) scripts/gen_chinese_legal_llm_book4_section5.py

chinese-legal-llm-validate:
	$(PY) scripts/validate_chinese_legal_llm.py

# -- Official Arabic text FOUNDATION (scaffold: architecture + verification workflow) --
# Validates the scaffold only; does NOT ingest or verify official Arabic text.
official-arabic-foundation-validate:
	$(PY) scripts/validate_official_arabic_foundation.py

# -- Official Arabic USER-PROVIDED ingestion (unverified candidate; 281 article records) --
# Segments the user-provided packet into 281 records + per-article hashes. Nothing verified.
official-arabic-user-provided-data:
	$(PY) scripts/ingest_official_arabic_user_provided_text.py

official-arabic-ingestion-validate:
	$(PY) scripts/validate_official_arabic_ingestion.py

# -- Official Arabic source VERIFICATION (comparison/report only; nothing promoted) --
# compare_official_arabic_candidate_to_source.py reads the committed OCR artifact (no OCR
# engine needed) and rewrites the comparison report deterministically.
official-arabic-verification-report-validate:
	$(PY) scripts/validate_official_arabic_verification_report.py

# -- Official Arabic OCR MANUAL-REVIEW QUEUE (triage only; promotes nothing) --
# build_official_arabic_manual_review_queue.py reads the committed comparison report +
# candidate + OCR artifact (no OCR engine) and rewrites the queue deterministically.
official-arabic-manual-review-queue-validate:
	$(PY) scripts/validate_official_arabic_manual_review_queue.py

# -- Official Arabic P0 Article 3 segmentation review (triage only; promotes nothing) --
official-arabic-p0-article3-review-validate:
	$(PY) scripts/validate_official_arabic_p0_article3_review.py

# -- Official Arabic queue P0-resolution update (status only; promotes nothing) --
# update script re-runs the resolution-aware queue builder deterministically.
official-arabic-queue-p0-resolution-validate:
	$(PY) scripts/validate_official_arabic_queue_p0_resolution.py

# -- Official Arabic BOE source provenance/status correction (provenance only; verifies nothing) --
official-arabic-boe-source-provenance-validate:
	$(PY) scripts/validate_official_arabic_boe_source_provenance.py

# -- Official Arabic FULL LLM-ready layer (281 articles; exact official_text_ar; no OCR) --
official-arabic-legal-llm-full-data:
	$(PY) scripts/gen_official_arabic_legal_llm_full_281.py

official-arabic-legal-llm-full-validate:
	$(PY) scripts/validate_official_arabic_legal_llm_full_281.py

# -- Full official English BOE reference alignment (281 articles; guidance only; Arabic governs) --
english-reference-full-281-data:
	$(PY) scripts/gen_english_reference_full_281.py

english-reference-full-281-validate:
	$(PY) scripts/validate_english_reference_full_281.py

# -- Full official English Legal LLM-ready layer (281 articles; verbatim guidance text; Arabic governs) --
official-english-legal-llm-full-data:
	$(PY) scripts/gen_official_english_legal_llm_full_281.py

official-english-legal-llm-full-validate:
	$(PY) scripts/validate_official_english_legal_llm_full_281.py

# -- Chinese Bab 1 original-PDF translation review (source inventory only; no Chinese LLM-ready) --
chinese-bab1-original-pdf-translation-review-data:
	$(PY) scripts/gen_chinese_bab1_original_pdf_translation_review.py

chinese-bab1-original-pdf-translation-review-validate:
	$(PY) scripts/validate_chinese_bab1_original_pdf_translation_review.py

# -- Chinese all-Babs (1-14) source coverage inventory (source inventory only; no Chinese LLM-ready) --
chinese-all-babs-source-inventory-data:
	$(PY) scripts/gen_chinese_all_babs_source_inventory.py

chinese-all-babs-source-inventory-validate:
	$(PY) scripts/validate_chinese_all_babs_source_inventory.py

# -- Chinese internal LLM-ready candidate layer (isolable-source articles only; internal/reference) --
chinese-internal-legal-llm-isolable-data:
	$(PY) scripts/gen_chinese_internal_legal_llm_isolable_source_articles.py

chinese-internal-legal-llm-isolable-validate:
	$(PY) scripts/validate_chinese_internal_legal_llm_isolable_source_articles.py

# -- Chinese internal candidate semantic QA (189) + completion gap plan (281) (QA/plan only) --
chinese-internal-llm-semantic-qa-gap-plan-data:
	$(PY) scripts/gen_chinese_internal_llm_semantic_qa_gap_plan.py

chinese-internal-llm-semantic-qa-gap-plan-validate:
	$(PY) scripts/validate_chinese_internal_llm_semantic_qa_gap_plan.py

# -- Chinese remediation backlog + batch plan + source-packet manifest (planning only; no Chinese) --
chinese-remediation-backlog-source-packet-plan-data:
	$(PY) scripts/gen_chinese_remediation_backlog_source_packet_plan.py

chinese-remediation-backlog-source-packet-plan-validate:
	$(PY) scripts/validate_chinese_remediation_backlog_source_packet_plan.py

# -- Chinese remediation Batch P0-001 (scoped internal Chinese draft; 20 Bab 4 articles; from Arabic) --
chinese-remediation-batch-p0-001-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_001.py

# -- Chinese remediation Batch P0-001 QA (article-by-article vs Arabic; review only) --
chinese-remediation-batch-p0-001-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_001_qa.py

# -- Chinese remediation Batch P0-001 minor fixes (Articles 61 & 74 terminology only) --
chinese-remediation-batch-p0-001-minor-fixes-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_001_minor_fixes.py

# -- Chinese remediation Batch P0-002 (scoped internal Chinese draft; 20 Bab 4 articles; from Arabic) --
chinese-remediation-batch-p0-002-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_002.py

# -- Chinese remediation Batch P0-002 QA (article-by-article vs Arabic; review only) --
chinese-remediation-batch-p0-002-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_002_qa.py

# -- Chinese remediation Batch P0-003 (scoped internal Chinese draft; 20 Bab 4 articles; from Arabic) --
chinese-remediation-batch-p0-003-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_003.py

# -- Chinese remediation Batch P0-003 QA (article-by-article vs Arabic; review only) --
chinese-remediation-batch-p0-003-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_003_qa.py

# -- Chinese remediation Batch P0-004 (scoped internal Chinese draft; 20 articles, Babs 4/5/6; from Arabic) --
chinese-remediation-batch-p0-004-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_004.py

# -- Chinese remediation Batch P0-004 QA (article-by-article vs Arabic; Babs 4/5/6; review only) --
chinese-remediation-batch-p0-004-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_004_qa.py

# -- Chinese remediation Batch P0-005 (final P0 batch; 12 articles, Babs 7/9/10/13/14; from Arabic) --
chinese-remediation-batch-p0-005-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_005.py

# -- Chinese remediation Batch P0-005 QA (final P0 batch; article-by-article vs Arabic; review only) --
chinese-remediation-batch-p0-005-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p0_005_qa.py

# -- Chinese remediation Batch P1-001 (first P1 batch; 20 articles, Babs 1/2; retranslate from Arabic) --
chinese-remediation-batch-p1-001-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p1_001.py

# -- Chinese remediation Batch P1-001 QA (article-by-article vs Arabic; review only; Babs 1/2) --
chinese-remediation-batch-p1-001-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p1_001_qa.py

# -- Chinese remediation Batch P1-002 (20 articles, Babs 3/4/5/6; retranslate from Arabic) --
chinese-remediation-batch-p1-002-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p1_002.py

# -- Chinese remediation Batch P1-002 QA (article-by-article vs Arabic; review only; Babs 3/4/5/6) --
chinese-remediation-batch-p1-002-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p1_002_qa.py

# -- Chinese remediation Batch P1-003 (20 articles, Babs 6/7/8/10; retranslate from Arabic) --
chinese-remediation-batch-p1-003-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p1_003.py

# -- Chinese remediation Batch P1-003 QA (article-by-article vs Arabic; review only; Babs 6/7/8/10) --
chinese-remediation-batch-p1-003-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p1_003_qa.py

# -- Chinese remediation Batch P1-004 (16 articles, Babs 10/12/13/14; retranslate from Arabic) --
chinese-remediation-batch-p1-004-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p1_004.py

# -- Chinese remediation Batch P1-004 QA (article-by-article vs Arabic; review only; Babs 10/12/13/14) --
chinese-remediation-batch-p1-004-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p1_004_qa.py

# -- Chinese remediation Batch P2-001 (first P2 expansion batch; 20 articles, Babs 1/2/4) --
chinese-remediation-batch-p2-001-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p2_001.py

# -- Chinese remediation Batch P2-001 QA (first P2 expansion QA; review only; Babs 1/2/4) --
chinese-remediation-batch-p2-001-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p2_001_qa.py

# -- Chinese remediation Batch P2-002 (second P2 expansion batch; 20 articles, Babs 4/5/6/7) --
chinese-remediation-batch-p2-002-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p2_002.py

# -- Chinese remediation Batch P2-002 QA (second P2 expansion QA; review only; Babs 4/5/6/7) --
chinese-remediation-batch-p2-002-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p2_002_qa.py

# -- Chinese remediation Batch P2-003 (P2 expansion batch; 20 articles, Babs 7/8/9/10) --
chinese-remediation-batch-p2-003-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p2_003.py

# -- Chinese remediation Batch P2-003 QA (P2 expansion QA; review only; Babs 7/8/9/10) --
chinese-remediation-batch-p2-003-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p2_003_qa.py

# -- Chinese remediation Batch P2-004 (P2 expansion batch; 20 articles, Babs 10/11/12) --
chinese-remediation-batch-p2-004-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p2_004.py

# -- Chinese remediation Batch P2-004 QA (P2 expansion QA; review only; Babs 10/11/12) --
chinese-remediation-batch-p2-004-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p2_004_qa.py

# -- Chinese remediation Batch P2-005 (P2 expansion batch; 15 articles, Babs 12/13/14) --
chinese-remediation-batch-p2-005-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p2_005.py

# -- Chinese remediation Batch P2-005 QA (P2 expansion QA; review only; Babs 12/13/14) --
chinese-remediation-batch-p2-005-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p2_005_qa.py

# -- Chinese confirmation Batch P3-CONF-001 (final P3 confirmation batch; 18 articles, Babs 2/3; retain) --
chinese-remediation-batch-p3-conf-001-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p3_conf_001.py

# -- Chinese confirmation Batch P3-CONF-001 QA (final P3 confirmation QA; review only; Babs 2/3) --
chinese-remediation-batch-p3-conf-001-qa-validate:
	$(PY) scripts/validate_chinese_remediation_batch_p3_conf_001_qa.py

# -- Sovereign legal corpus factory foundation (doctrine, architecture, schemas, profile, config, seed) --
legal-corpus-factory-foundation-validate:
	$(PY) scripts/validate_legal_corpus_factory_foundation.py

# -- Repository UX / navigation docs (README top + START_HERE/STATUS/REPOSITORY_MAP/USE_CASES) --
repository-ux-docs-validate:
	$(PY) scripts/validate_repository_ux_docs.py

# -- Repository rename readiness (saudi-companies-law-ar-zh-llm -> saudi-legal-corpus-ai) --
repository-rename-readiness-validate:
	$(PY) scripts/validate_repository_rename_readiness.py

# -- Chinese remediation program closure audit (read-only; P0..P3 complete) --
chinese-remediation-program-closure-validate:
	$(PY) scripts/validate_chinese_remediation_program_closure.py

# -- Implementing regulations intake scaffold (scaffold only; no intake/translation) --
implementing-regulations-intake-scaffold-validate:
	$(PY) scripts/validate_implementing_regulations_intake_scaffold.py

# -- Listed joint-stock implementing regulation Arabic source intake (69 articles; specialized) --
implementing-regulations-listed-jsc-arabic-source-validate:
	$(PY) scripts/validate_implementing_regulations_listed_jsc_arabic_source.py

# -- General implementing regulations Arabic source intake (95 articles; 7 chapters; 4 forms) --
implementing-regulations-general-arabic-source-validate:
	$(PY) scripts/validate_implementing_regulations_general_arabic_source.py

# -- General implementing regulations Arabic Legal LLM layer (95 article records + 4 form records) --
implementing-regulations-general-arabic-legal-llm-data:
	$(PY) scripts/gen_implementing_regulations_general_arabic_legal_llm.py

implementing-regulations-general-arabic-legal-llm-validate:
	$(PY) scripts/validate_implementing_regulations_general_arabic_legal_llm.py

# -- Listed joint-stock implementing regulation Arabic Legal LLM layer (69 article records + 1 appendix) --
implementing-regulations-listed-jsc-arabic-legal-llm-data:
	$(PY) scripts/gen_implementing_regulations_listed_jsc_arabic_legal_llm.py

implementing-regulations-listed-jsc-arabic-legal-llm-validate:
	$(PY) scripts/validate_implementing_regulations_listed_jsc_arabic_legal_llm.py

# -- Implementing regulations Arabic program closure audit (read-only; covers both tracks) --
implementing-regulations-arabic-program-closure-data:
	$(PY) scripts/gen_implementing_regulations_arabic_program_closure.py

implementing-regulations-arabic-program-closure-validate:
	$(PY) scripts/validate_implementing_regulations_arabic_program_closure.py

# -- Corpus registry index foundation (canonical registry; read-only) --
corpus-registry-data:
	$(PY) scripts/gen_corpus_registry.py

corpus-registry-validate:
	$(PY) scripts/validate_corpus_registry.py

# -- Corpus export — primary Arabic governing records (v1; read-only) --
corpus-export-primary-arabic-data:
	$(PY) scripts/gen_corpus_export_primary_arabic.py

corpus-export-primary-arabic-validate:
	$(PY) scripts/validate_corpus_export_primary_arabic.py

# -- Corpus local lexical search (deterministic, offline; read-only) --
corpus-local-search-validate:
	$(PY) scripts/validate_corpus_local_search.py

corpus-local-search-smoke:
	$(PY) scripts/search_primary_arabic_export.py "الشركة" --limit 5
	@echo "---"
	$(PY) scripts/search_primary_arabic_export.py "مجلس الإدارة" --limit 5
	@echo "---"
	$(PY) scripts/search_primary_arabic_export.py "الجمعية العامة" --limit 5 --json

# -- Corpus local search evaluation fixtures (deterministic, offline) --
corpus-local-search-eval-validate:
	$(PY) scripts/validate_corpus_local_search_eval.py

# -- Corpus retrieval context pack (deterministic, offline; read-only) --
corpus-retrieval-context-pack-validate:
	$(PY) scripts/validate_retrieval_context_pack.py

corpus-retrieval-context-pack-smoke:
	$(PY) scripts/build_retrieval_context_pack.py "مجلس الإدارة" --limit 3 --format json
	@echo "---"
	$(PY) scripts/build_retrieval_context_pack.py "الجمعية العامة" --limit 3 --format markdown
	@echo "---"
	$(PY) scripts/build_retrieval_context_pack.py "التوكيل" --record-type appendix --limit 1 --format json --include-full-text

# -- Corpus retrieval prompt pack (deterministic, offline; builds prompts only) --
corpus-retrieval-prompt-pack-validate:
	$(PY) scripts/validate_retrieval_prompt_pack.py

corpus-retrieval-prompt-pack-smoke:
	$(PY) scripts/build_retrieval_prompt_pack.py "مجلس الإدارة" --limit 3 --mode evidence_brief --format json
	@echo "---"
	$(PY) scripts/build_retrieval_prompt_pack.py "الجمعية العامة" --limit 3 --mode cautious_answer_draft --format markdown
	@echo "---"
	$(PY) scripts/build_retrieval_prompt_pack.py "التوكيل" --record-type appendix --limit 1 --mode evidence_brief --format json --include-full-text

# -- Corpus citation support checker (deterministic, offline; mechanical checking only) --
corpus-citation-support-checker-validate:
	$(PY) scripts/validate_citation_support_checker.py

corpus-citation-support-checker-smoke:
	$(PY) scripts/build_retrieval_prompt_pack.py "مجلس الإدارة" --limit 3 --mode cautious_answer_draft --format json --output /tmp/_smoke_prompt_pack.json
	@echo "---"
	$(PY) -c "import json; pack=json.load(open('/tmp/_smoke_prompt_pack.json')); rid=pack['retrieved_records'][0]['export_record_id']; open('/tmp/_smoke_valid_draft.md','w').write('هذه إجابة معلوماتية وليست استشارة قانونية للمراجعة القانونية [['+'[export_record_id='+rid+']'+']].\n\nوفقًا للنظام [['+'[export_record_id='+rid+']'+']].\n')"
	$(PY) scripts/check_citation_support.py --prompt-pack /tmp/_smoke_prompt_pack.json --draft-answer-file /tmp/_smoke_valid_draft.md --require-citation-per-paragraph --format json
	@echo "---"
	$(PY) -c "open('/tmp/_smoke_invalid_draft.md','w').write('هذه إجابة معلوماتية.\n\n[[export_record_id=FAKE-NOT-IN-PACK]].\n')"
	$(PY) scripts/check_citation_support.py --prompt-pack /tmp/_smoke_prompt_pack.json --draft-answer-file /tmp/_smoke_invalid_draft.md --format json || true
	@rm -f /tmp/_smoke_prompt_pack.json /tmp/_smoke_valid_draft.md /tmp/_smoke_invalid_draft.md

# -- Corpus retrieval workflow runner (deterministic, offline; thin orchestration) --
corpus-retrieval-workflow-runner-validate:
	$(PY) scripts/validate_retrieval_workflow_runner.py

corpus-retrieval-workflow-runner-smoke:
	$(PY) scripts/run_retrieval_workflow.py "مجلس الإدارة" --mode prepare_prompt --limit 3 --prompt-mode evidence_brief --formats both --output-dir /tmp/_smoke_workflow_prep
	@echo "---"
	$(PY) -c "import json; pack=json.load(open('/tmp/_smoke_workflow_prep/prompt_pack.json')); rid=pack['retrieved_records'][0]['export_record_id']; open('/tmp/_smoke_workflow_draft.md','w').write('هذه إجابة معلوماتية وليست استشارة قانونية للمراجعة القانونية [['+'[export_record_id='+rid+']'+']].\n\nوفقًا للنظام [['+'[export_record_id='+rid+']'+']].\n')"
	$(PY) scripts/run_retrieval_workflow.py "مجلس الإدارة" --mode check_draft --limit 3 --prompt-mode cautious_answer_draft --draft-answer-file /tmp/_smoke_workflow_draft.md --require-citation-per-paragraph --formats both --output-dir /tmp/_smoke_workflow_check
	@rm -rf /tmp/_smoke_workflow_prep /tmp/_smoke_workflow_check /tmp/_smoke_workflow_draft.md

# -- Corpus retrieval demo scenarios (deterministic, offline; curated demo layer) --

corpus-retrieval-demo-scenarios-validate:
	$(PY) scripts/validate_retrieval_demo_scenarios.py

corpus-retrieval-demo-scenarios-smoke:
	$(PY) scripts/run_retrieval_demo_scenarios.py
	@echo "---"
	$(PY) scripts/run_retrieval_workflow.py "مجلس الإدارة" --mode prepare_prompt --limit 3 --prompt-mode evidence_brief --formats both --output-dir /tmp/_smoke_demo_board
	@echo "---"
	@echo "Confirming no generated workflow outputs in data/demo_scenarios/..."
	@ls data/demo_scenarios/ | grep -v "retrieval_demo_scenarios_v1.json" && echo "FAIL: unexpected files" && exit 1 || echo "OK: only scenarios JSON present"
	@rm -rf /tmp/_smoke_demo_board

# -- Corpus retrieval operator demo pack (documentation + validator only) --

corpus-retrieval-operator-demo-pack-validate:
	$(PY) scripts/validate_operator_demo_pack.py

corpus-retrieval-operator-demo-pack-smoke:
	$(PY) scripts/validate_operator_demo_pack.py
	@echo "---"
	@echo "Running demo scenarios smoke to confirm referenced commands work..."
	$(PY) scripts/run_retrieval_demo_scenarios.py
	@echo "---"
	@echo "Confirming no generated artifacts in docs/operator_demo_pack/..."
	@find docs/operator_demo_pack/ -type f ! -name "*.md" -print -quit | grep -q . && echo "FAIL: non-markdown files" && exit 1 || echo "OK: only markdown files"
	@rm -rf /tmp/corpus_demo_scenarios_*

# -- PDPL Arabic Law next-layer validator (dedicated target; does NOT change make validate) --
pdpl-arabic-law-next-layer-validate:
	$(PY) scripts/validate_pdpl_arabic_law_next_layer_records.py

# -- PDPL implementing-regulation next-layer validator (dedicated target; does NOT change make validate) --
pdpl-implementing-regulation-arabic-next-layer-validate:
	$(PY) scripts/validate_pdpl_implementing_regulation_arabic_next_layer_records.py

# -- PDPL implementing-regulation cleaned-text generator + validator (dedicated target; does NOT change make validate) --
pdpl-implementing-regulation-arabic-cleaned-validate:
	$(PY) scripts/validate_pdpl_implementing_regulation_arabic_cleaned.py

# -- PDPL implementing-regulation verified/corrected text validator (dedicated target; does NOT change make validate) --
pdpl-implementing-regulation-arabic-verified-validate:
	$(PY) scripts/validate_pdpl_implementing_regulation_arabic_verified.py

# -- PDPL implementing-regulation Arabic LLM-ready enrichment layer validator (dedicated target; does NOT change make validate) --
pdpl-implementing-regulation-arabic-legal-llm-validate:
	$(PY) scripts/validate_pdpl_implementing_regulation_arabic_legal_llm.py

# -- PDPL law verified/corrected text validator (dedicated target; does NOT change make validate) --
pdpl-arabic-law-verified-validate:
	$(PY) scripts/validate_pdpl_arabic_law_verified.py

# -- PDPL law Arabic LLM-ready enrichment layer validator (dedicated target; does NOT change make validate) --
pdpl-arabic-law-legal-llm-validate:
	$(PY) scripts/validate_pdpl_arabic_law_legal_llm.py

# -- Investment Law verified text validator (dedicated target; does NOT change make validate) --
investment-law-verified-validate:
	$(PY) scripts/validate_investment_law_verified.py

# -- Investment Law Arabic LLM-ready enrichment layer validator (dedicated target; does NOT change make validate) --
investment-law-legal-llm-validate:
	$(PY) scripts/validate_investment_law_legal_llm.py

# -- Investment Regulations verified text validator (dedicated target; does NOT change make validate) --
investment-regulation-verified-validate:
	$(PY) scripts/validate_investment_regulation_verified.py

# -- Investment Regulations Arabic LLM-ready enrichment layer validator (dedicated target; does NOT change make validate) --
investment-regulation-legal-llm-validate:
	$(PY) scripts/validate_investment_regulation_legal_llm.py

# -- Civil Transactions Law verified text validator (dedicated target; does NOT change make validate) --
civil-transactions-law-verified-validate:
	$(PY) scripts/validate_civil_transactions_law_verified.py

# -- Civil Transactions Law Arabic LLM-ready enrichment layer validator (dedicated target; does NOT change make validate) --
civil-transactions-law-legal-llm-validate:
	$(PY) scripts/validate_civil_transactions_law_legal_llm.py

# -- Unified cross-law LLM retrieval index generator + validator (dedicated target; does NOT change make validate) --
corpus-unified-llm-index-validate:
	$(PY) scripts/validate_corpus_unified_llm_index.py

# -- Retrieval eval pack over the unified index (dedicated target; does NOT change make validate) --
corpus-retrieval-eval-validate:
	$(PY) scripts/validate_corpus_retrieval_eval.py

# -- GTPL (M/128) track validator (dedicated target; does NOT change make validate) --
gtpl-law-track-validate:
	$(PY) scripts/validate_gtpl_law_track.py

# -- GTPL Implementing Regulation track validator (dedicated target; does NOT change make validate) --
gtpl-regulation-track-validate:
	$(PY) scripts/validate_gtpl_regulation_track.py

# -- Labor Law track validator (dedicated target; does NOT change make validate) --
labor-law-track-validate:
	$(PY) scripts/validate_labor_law_track.py

# -- Labor Regulation track validator (dedicated target; does NOT change make validate) --
labor-regulation-track-validate:
	$(PY) scripts/validate_labor_regulation_track.py

# -- Labor Annex 1 (model work organization regulation) track validator --
labor-annex1-track-validate:
	$(PY) scripts/validate_labor_annex1_track.py

# -- Labor Annex 3 + 4 tracks validator --
labor-annex34-tracks-validate:
	$(PY) scripts/validate_labor_annex34_tracks.py

# -- Labor Annex 2 (accessibility tables) track validator --
labor-annex2-track-validate:
	$(PY) scripts/validate_labor_annex2_track.py

# -- Labor Annex 5 (model contract forms) track validator --
labor-annex5-track-validate:
	$(PY) scripts/validate_labor_annex5_track.py

# -- Evidence Law track validator --
evidence-law-track-validate:
	$(PY) scripts/validate_evidence_law_track.py

# -- Evidence Law companion tracks validator (electronic rules + manuals + expertise) --
evidence-companions-tracks-validate:
	$(PY) scripts/validate_evidence_companions_tracks.py

# -- STRICT QA GATE: every validate_*.py + generator idempotence + full pytest. One command, everything must pass. --
qa-gate:
	$(PY) scripts/run_qa_gate.py

# CI variant (pytest already runs as its own CI step)
qa-gate-ci:
	$(PY) scripts/run_qa_gate.py --no-tests

clean:
	rm -f dist/book1.html dist/book1.pdf data/articles/book1_articles_001_034.jsonl \
	      dist/book2.html dist/book2.pdf data/articles/book2_articles_035_050.jsonl \
	      dist/book3.html dist/book3.pdf data/articles/book3_articles_051_057.jsonl
