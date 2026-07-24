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
        personal-status-tracks-validate \
        sharia-procedure-law-track-validate \
        sharia-procedure-regulation-track-validate \
        criminal-procedure-law-track-validate \
        criminal-procedure-regulation-track-validate \
        enforcement-law-track-validate \
        enforcement-regulation-track-validate \
        judiciary-law-track-validate \
        board-of-grievances-law-track-validate \
        law-practice-law-track-validate \
        law-practice-regulation-track-validate \
        commercial-courts-law-track-validate \
        commercial-courts-regulation-track-validate \
        bankruptcy-law-track-validate \
        bankruptcy-regulation-track-validate \
        bankruptcy-case-rules-track-validate \
        judicial-costs-law-track-validate \
        judicial-costs-regulation-track-validate \
        arbitration-law-track-validate \
        arbitration-regulation-track-validate \
        commercial-papers-law-track-validate \
        commercial-register-law-track-validate \
        trade-names-law-track-validate \
        commercial-agencies-law-track-validate \
        chambers-of-commerce-law-track-validate \
        commercial-books-law-track-validate \
        aml-law-track-validate \
        tawtheeq-law-track-validate \
        tawtheeq-regulation-track-validate \
        real-estate-registration-law-track-validate \
        real-estate-registration-regulation-track-validate \
        real-estate-mortgage-law-track-validate \
        real-estate-finance-law-track-validate \
        real-estate-units-law-track-validate \
        real-estate-units-regulation-track-validate \
        foreign-ownership-law-track-validate \
        municipal-realestate-law-track-validate \
        municipal-realestate-regulation-track-validate \
        gcc-ownership-law-track-validate \
        terrorism-law-track-validate \
        terrorism-regulation-track-validate \
        juveniles-law-track-validate \
        juveniles-regulation-track-validate \
        whistleblower-law-track-validate \
        judicial-inspection-regulation-track-validate \
        qismah-regulation-track-validate \
        sulook-regulation-track-validate \
        aawan-regulation-track-validate \
        muslaha-regulation-track-validate \
        iflas-hudud-regulation-track-validate \
        judicial-documents-regulation-track-validate \
        bankruptcy-fees-regulation-track-validate \
        enforcement-providers-regulation-track-validate \
        alimony-fund-regulation-track-validate \
        judiciary-bog-mechanism-track-validate \
        documentation-settlement-regulation-track-validate \
        mosalaha-center-regulation-track-validate \
        medical-reports-regulation-track-validate \
        marriage-non-saudi-regulation-track-validate \
        state-funded-lawyer-regulation-track-validate \
        lessor-repossession-regulation-track-validate \
        elitigation-guide-regulation-track-validate \
        judicial-training-center-guide-track-validate \
        judgment-objection-methods-regulation-track-validate \
        real-estate-expropriation-law-track-validate \
        marriage-contract-hearing-regulation-track-validate \
        anti-bribery-law-track-validate \
        basic-law-of-governance-track-validate \
        anti-cyber-crime-law-track-validate \
        anti-harassment-law-track-validate \
        anti-trafficking-law-track-validate \
        council-of-ministers-law-track-validate \
        regions-law-track-validate \
        electronic-transactions-law-track-validate \
        allegiance-commission-law-track-validate \
        shura-council-law-track-validate \
        copyright-law-track-validate \
        telecommunications-law-track-validate \
        sama-law-track-validate \
        banking-control-law-track-validate \
        capital-market-law-track-validate \
        competition-law-track-validate \
        payment-systems-law-track-validate \
        mining-investment-law-track-validate \
        trademark-law-track-validate \
        anti-concealment-law-track-validate \
        insurance-control-law-track-validate \
        ecommerce-law-track-validate \
        vat-law-track-validate \
        franchise-law-track-validate \
        civil-aviation-law-track-validate \
        anti-narcotics-law-track-validate \
        traffic-law-track-validate \
        environmental-law-track-validate \
        income-tax-law-track-validate \
        civil-service-law-track-validate \
        social-insurance-law-track-validate \
        social-insurance-legacy-law-track-validate \
        corpus-verification-tiers-validate \
        zakat-law-track-validate \
        corpus-supersession-graph-validate \
        corpus-cross-reference-graph-validate \
        corpus-glossary-validate \
        corpus-schema-manifest-validate \
        corpus-chunking-layer-validate \
        corpus-freshness-manifest-validate \
        patent-law-track-validate \
        customs-law-track-validate \
        customs-regulation-track-validate \
        anti-fraud-law-track-validate \
        finance-companies-law-track-validate \
        cooperative-health-insurance-law-track-validate \
        healthcare-professions-law-track-validate \
        finance-lease-law-track-validate \
        maritime-commercial-law-track-validate \
        gcc-anti-dumping-law-track-validate \
        accounting-auditing-law-track-validate \
        nazaha-law-track-validate \
        awqaf-law-track-validate \
        saudi-engineers-law-track-validate \
        municipal-councils-law-track-validate \
        press-law-track-validate \
        engineering-practice-law-track-validate \
        nationality-law-track-validate \
        residency-law-track-validate \
        civil-status-law-track-validate \
        food-law-track-validate \
        health-system-law-track-validate \
        domestic-labor-regulation-track-validate \
        travel-documents-law-track-validate \
        cybersecurity-authority-law-track-validate \
        cybersecurity-authority-enablers-track-validate \
        premium-residency-law-track-validate \
        travel-documents-regulation-track-validate \
        nationality-regulation-track-validate \
        health-system-regulation-track-validate \
        food-regulation-track-validate \
        electricity-law-track-validate \
        water-law-track-validate \
        vat-regulation-track-validate \
        income-tax-regulation-track-validate \
        agriculture-law-track-validate \
        competition-regulation-track-validate \
        aml-regulation-track-validate \
        patent-regulation-track-validate \
        ecommerce-regulation-track-validate \
        franchise-regulation-track-validate \
        traffic-regulation-track-validate \
        environmental-inspection-audit-reg-track-validate \
        environmental-violations-penalties-reg-track-validate \
        environmental-permits-reg-track-validate \
        environmental-air-quality-reg-track-validate \
        environmental-service-providers-reg-track-validate \
        environmental-fees-reg-track-validate \
        rett-law-track-validate \
        universities-law-track-validate \
        privatization-law-track-validate \
        antiquities-heritage-law-track-validate \
        child-protection-law-track-validate \
        protection-from-abuse-law-track-validate \
        associations-ngo-law-track-validate \
        audiovisual-media-law-track-validate \
        sports-law-track-validate \
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

# -- Personal Status Law + regulation tracks validator --
personal-status-tracks-validate:
	$(PY) scripts/validate_personal_status_tracks.py

# -- Law of Sharia Procedure track validator --
sharia-procedure-law-track-validate:
	$(PY) scripts/validate_sharia_procedure_law_track.py

# -- Sharia Procedure implementing-regulation track validator --
sharia-procedure-regulation-track-validate:
	$(PY) scripts/validate_sharia_procedure_regulation_track.py

# -- Law of Criminal Procedure track validator --
criminal-procedure-law-track-validate:
	$(PY) scripts/validate_criminal_procedure_law_track.py

# -- Criminal Procedure implementing-regulation track validator --
criminal-procedure-regulation-track-validate:
	$(PY) scripts/validate_criminal_procedure_regulation_track.py

# -- Enforcement Law track validator --
enforcement-law-track-validate:
	$(PY) scripts/validate_enforcement_law_track.py

# -- Enforcement implementing-regulation track validator --
enforcement-regulation-track-validate:
	$(PY) scripts/validate_enforcement_regulation_track.py

# -- Law of the Judiciary track validator --
judiciary-law-track-validate:
	$(PY) scripts/validate_judiciary_law_track.py

# -- Law of the Board of Grievances track validator --
board-of-grievances-law-track-validate:
	$(PY) scripts/validate_board_of_grievances_law_track.py

# -- Code of Law Practice track validator --
law-practice-law-track-validate:
	$(PY) scripts/validate_law_practice_law_track.py

# -- Implementing Regulation of the Code of Law Practice track validator --
law-practice-regulation-track-validate:
	$(PY) scripts/validate_law_practice_regulation_track.py

# -- Commercial Courts Law track validator --
commercial-courts-law-track-validate:
	$(PY) scripts/validate_commercial_courts_law_track.py

# -- Implementing Regulation of the Commercial Courts Law track validator --
commercial-courts-regulation-track-validate:
	$(PY) scripts/validate_commercial_courts_regulation_track.py

bankruptcy-law-track-validate:
	$(PY) scripts/validate_bankruptcy_law_track.py

bankruptcy-regulation-track-validate:
	$(PY) scripts/validate_bankruptcy_regulation_track.py

bankruptcy-case-rules-track-validate:
	$(PY) scripts/validate_bankruptcy_case_rules_track.py

judicial-costs-law-track-validate:
	$(PY) scripts/validate_judicial_costs_law_track.py

judicial-costs-regulation-track-validate:
	$(PY) scripts/validate_judicial_costs_regulation_track.py

arbitration-law-track-validate:
	$(PY) scripts/validate_arbitration_law_track.py

arbitration-regulation-track-validate:
	$(PY) scripts/validate_arbitration_regulation_track.py

commercial-papers-law-track-validate:
	$(PY) scripts/validate_commercial_papers_law_track.py

commercial-register-law-track-validate:
	$(PY) scripts/validate_commercial_register_law_track.py

trade-names-law-track-validate:
	$(PY) scripts/validate_trade_names_law_track.py

commercial-agencies-law-track-validate:
	$(PY) scripts/validate_commercial_agencies_law_track.py

chambers-of-commerce-law-track-validate:
	$(PY) scripts/validate_chambers_of_commerce_law_track.py

commercial-books-law-track-validate:
	$(PY) scripts/validate_commercial_books_law_track.py

aml-law-track-validate:
	$(PY) scripts/validate_aml_law_track.py

tawtheeq-law-track-validate:
	$(PY) scripts/validate_tawtheeq_law_track.py

tawtheeq-regulation-track-validate:
	$(PY) scripts/validate_tawtheeq_regulation_track.py

real-estate-registration-law-track-validate:
	$(PY) scripts/validate_real_estate_registration_law_track.py

real-estate-registration-regulation-track-validate:
	$(PY) scripts/validate_real_estate_registration_regulation_track.py

real-estate-mortgage-law-track-validate:
	$(PY) scripts/validate_real_estate_mortgage_law_track.py

real-estate-finance-law-track-validate:
	$(PY) scripts/validate_real_estate_finance_law_track.py

real-estate-units-law-track-validate:
	$(PY) scripts/validate_real_estate_units_law_track.py

real-estate-units-regulation-track-validate:
	$(PY) scripts/validate_real_estate_units_regulation_track.py

foreign-ownership-law-track-validate:
	$(PY) scripts/validate_foreign_ownership_law_track.py

municipal-realestate-law-track-validate:
	$(PY) scripts/validate_municipal_realestate_law_track.py

municipal-realestate-regulation-track-validate:
	$(PY) scripts/validate_municipal_realestate_regulation_track.py

gcc-ownership-law-track-validate:
	$(PY) scripts/validate_gcc_ownership_law_track.py

terrorism-law-track-validate:
	$(PY) scripts/validate_terrorism_law_track.py

terrorism-regulation-track-validate:
	$(PY) scripts/validate_terrorism_regulation_track.py

juveniles-law-track-validate:
	$(PY) scripts/validate_juveniles_law_track.py

juveniles-regulation-track-validate:
	$(PY) scripts/validate_juveniles_regulation_track.py

whistleblower-law-track-validate:
	$(PY) scripts/validate_whistleblower_law_track.py

judicial-inspection-regulation-track-validate:
	$(PY) scripts/validate_judicial_inspection_regulation_track.py

qismah-regulation-track-validate:
	$(PY) scripts/validate_qismah_regulation_track.py

sulook-regulation-track-validate:
	$(PY) scripts/validate_sulook_regulation_track.py

aawan-regulation-track-validate:
	$(PY) scripts/validate_aawan_regulation_track.py

muslaha-regulation-track-validate:
	$(PY) scripts/validate_muslaha_regulation_track.py

iflas-hudud-regulation-track-validate:
	$(PY) scripts/validate_iflas_hudud_regulation_track.py

judicial-documents-regulation-track-validate:
	$(PY) scripts/validate_judicial_documents_regulation_track.py

bankruptcy-fees-regulation-track-validate:
	$(PY) scripts/validate_bankruptcy_fees_regulation_track.py

enforcement-providers-regulation-track-validate:
	$(PY) scripts/validate_enforcement_providers_regulation_track.py

alimony-fund-regulation-track-validate:
	$(PY) scripts/validate_alimony_fund_regulation_track.py

judiciary-bog-mechanism-track-validate:
	$(PY) scripts/validate_judiciary_bog_mechanism_track.py

documentation-settlement-regulation-track-validate:
	$(PY) scripts/validate_documentation_settlement_regulation_track.py

mosalaha-center-regulation-track-validate:
	$(PY) scripts/validate_mosalaha_center_regulation_track.py

medical-reports-regulation-track-validate:
	$(PY) scripts/validate_medical_reports_regulation_track.py

marriage-non-saudi-regulation-track-validate:
	$(PY) scripts/validate_marriage_non_saudi_regulation_track.py

state-funded-lawyer-regulation-track-validate:
	$(PY) scripts/validate_state_funded_lawyer_regulation_track.py

lessor-repossession-regulation-track-validate:
	$(PY) scripts/validate_lessor_repossession_regulation_track.py

elitigation-guide-regulation-track-validate:
	$(PY) scripts/validate_elitigation_guide_regulation_track.py

judicial-training-center-guide-track-validate:
	$(PY) scripts/validate_judicial_training_center_guide_track.py

judgment-objection-methods-regulation-track-validate:
	$(PY) scripts/validate_judgment_objection_methods_regulation_track.py

real-estate-expropriation-law-track-validate:
	$(PY) scripts/validate_real_estate_expropriation_law_track.py

marriage-contract-hearing-regulation-track-validate:
	$(PY) scripts/validate_marriage_contract_hearing_regulation_track.py

anti-bribery-law-track-validate:
	$(PY) scripts/validate_anti_bribery_law_track.py

basic-law-of-governance-track-validate:
	$(PY) scripts/validate_basic_law_of_governance_track.py

anti-cyber-crime-law-track-validate:
	$(PY) scripts/validate_anti_cyber_crime_law_track.py

anti-harassment-law-track-validate:
	$(PY) scripts/validate_anti_harassment_law_track.py

anti-trafficking-law-track-validate:
	$(PY) scripts/validate_anti_trafficking_law_track.py

council-of-ministers-law-track-validate:
	$(PY) scripts/validate_council_of_ministers_law_track.py

regions-law-track-validate:
	$(PY) scripts/validate_regions_law_track.py

electronic-transactions-law-track-validate:
	$(PY) scripts/validate_electronic_transactions_law_track.py

allegiance-commission-law-track-validate:
	$(PY) scripts/validate_allegiance_commission_law_track.py

shura-council-law-track-validate:
	$(PY) scripts/validate_shura_council_law_track.py

copyright-law-track-validate:
	$(PY) scripts/validate_copyright_law_track.py

telecommunications-law-track-validate:
	$(PY) scripts/validate_telecommunications_law_track.py

sama-law-track-validate:
	$(PY) scripts/validate_sama_law_track.py

banking-control-law-track-validate:
	$(PY) scripts/validate_banking_control_law_track.py

capital-market-law-track-validate:
	$(PY) scripts/validate_capital_market_law_track.py

competition-law-track-validate:
	$(PY) scripts/validate_competition_law_track.py

payment-systems-law-track-validate:
	$(PY) scripts/validate_payment_systems_law_track.py

mining-investment-law-track-validate:
	$(PY) scripts/validate_mining_investment_law_track.py

trademark-law-track-validate:
	$(PY) scripts/validate_trademark_law_track.py

anti-concealment-law-track-validate:
	$(PY) scripts/validate_anti_concealment_law_track.py

insurance-control-law-track-validate:
	$(PY) scripts/validate_insurance_control_law_track.py

ecommerce-law-track-validate:
	$(PY) scripts/validate_ecommerce_law_track.py

vat-law-track-validate:
	$(PY) scripts/validate_vat_law_track.py

franchise-law-track-validate:
	$(PY) scripts/validate_franchise_law_track.py

civil-aviation-law-track-validate:
	$(PY) scripts/validate_civil_aviation_law_track.py

anti-narcotics-law-track-validate:
	$(PY) scripts/validate_anti_narcotics_law_track.py

traffic-law-track-validate:
	$(PY) scripts/validate_traffic_law_track.py

environmental-law-track-validate:
	$(PY) scripts/validate_environmental_law_track.py

income-tax-law-track-validate:
	$(PY) scripts/validate_income_tax_law_track.py

civil-service-law-track-validate:
	$(PY) scripts/validate_civil_service_law_track.py

social-insurance-law-track-validate:
	$(PY) scripts/validate_social_insurance_law_track.py

social-insurance-legacy-law-track-validate:
	$(PY) scripts/validate_social_insurance_legacy_law_track.py

corpus-verification-tiers-validate:
	$(PY) scripts/validate_corpus_verification_tiers.py

zakat-law-track-validate:
	$(PY) scripts/validate_zakat_law_track.py

corpus-supersession-graph-validate:
	$(PY) scripts/validate_corpus_supersession_graph.py

corpus-cross-reference-graph-validate:
	$(PY) scripts/validate_corpus_cross_reference_graph.py

corpus-glossary-validate:
	$(PY) scripts/validate_corpus_glossary.py

corpus-schema-manifest-validate:
	$(PY) scripts/validate_corpus_schema_manifest.py

corpus-chunking-layer-validate:
	$(PY) scripts/validate_corpus_chunking_layer.py

corpus-freshness-manifest-validate:
	$(PY) scripts/validate_corpus_freshness_manifest.py

patent-law-track-validate:
	$(PY) scripts/validate_patent_law_track.py

customs-law-track-validate:
	$(PY) scripts/validate_customs_law_track.py

customs-regulation-track-validate:
	$(PY) scripts/validate_customs_regulation_track.py

anti-fraud-law-track-validate:
	$(PY) scripts/validate_anti_fraud_law_track.py

finance-companies-law-track-validate:
	$(PY) scripts/validate_finance_companies_law_track.py

cooperative-health-insurance-law-track-validate:
	$(PY) scripts/validate_cooperative_health_insurance_law_track.py

healthcare-professions-law-track-validate:
	$(PY) scripts/validate_healthcare_professions_law_track.py

finance-lease-law-track-validate:
	$(PY) scripts/validate_finance_lease_law_track.py

maritime-commercial-law-track-validate:
	$(PY) scripts/validate_maritime_commercial_law_track.py

gcc-anti-dumping-law-track-validate:
	$(PY) scripts/validate_gcc_anti_dumping_law_track.py

accounting-auditing-law-track-validate:
	$(PY) scripts/validate_accounting_auditing_law_track.py

nazaha-law-track-validate:
	$(PY) scripts/validate_nazaha_law_track.py

awqaf-law-track-validate:
	$(PY) scripts/validate_awqaf_law_track.py

saudi-engineers-law-track-validate:
	$(PY) scripts/validate_saudi_engineers_law_track.py

municipal-councils-law-track-validate:
	$(PY) scripts/validate_municipal_councils_law_track.py

press-law-track-validate:
	$(PY) scripts/validate_press_law_track.py

engineering-practice-law-track-validate:
	$(PY) scripts/validate_engineering_practice_law_track.py

nationality-law-track-validate:
	$(PY) scripts/validate_nationality_law_track.py

residency-law-track-validate:
	$(PY) scripts/validate_residency_law_track.py

civil-status-law-track-validate:
	$(PY) scripts/validate_civil_status_law_track.py

food-law-track-validate:
	$(PY) scripts/validate_food_law_track.py

health-system-law-track-validate:
	$(PY) scripts/validate_health_system_law_track.py

domestic-labor-regulation-track-validate:
	$(PY) scripts/validate_domestic_labor_regulation_track.py

travel-documents-law-track-validate:
	$(PY) scripts/validate_travel_documents_law_track.py

cybersecurity-authority-law-track-validate:
	$(PY) scripts/validate_cybersecurity_authority_law_track.py

cybersecurity-authority-enablers-track-validate:
	$(PY) scripts/validate_cybersecurity_authority_enablers_track.py

premium-residency-law-track-validate:
	$(PY) scripts/validate_premium_residency_law_track.py

travel-documents-regulation-track-validate:
	$(PY) scripts/validate_travel_documents_regulation_track.py

nationality-regulation-track-validate:
	$(PY) scripts/validate_nationality_regulation_track.py

health-system-regulation-track-validate:
	$(PY) scripts/validate_health_system_regulation_track.py

food-regulation-track-validate:
	$(PY) scripts/validate_food_regulation_track.py

electricity-law-track-validate:
	$(PY) scripts/validate_electricity_law_track.py

water-law-track-validate:
	$(PY) scripts/validate_water_law_track.py

vat-regulation-track-validate:
	$(PY) scripts/validate_vat_regulation_track.py

income-tax-regulation-track-validate:
	$(PY) scripts/validate_income_tax_regulation_track.py

agriculture-law-track-validate:
	$(PY) scripts/validate_agriculture_law_track.py

competition-regulation-track-validate:
	$(PY) scripts/validate_competition_regulation_track.py

aml-regulation-track-validate:
	$(PY) scripts/validate_aml_regulation_track.py

patent-regulation-track-validate:
	$(PY) scripts/validate_patent_regulation_track.py

ecommerce-regulation-track-validate:
	$(PY) scripts/validate_ecommerce_regulation_track.py

franchise-regulation-track-validate:
	$(PY) scripts/validate_franchise_regulation_track.py

traffic-regulation-track-validate:
	$(PY) scripts/validate_traffic_regulation_track.py

environmental-inspection-audit-reg-track-validate:
	$(PY) scripts/validate_environmental_inspection_audit_reg_track.py

environmental-violations-penalties-reg-track-validate:
	$(PY) scripts/validate_environmental_violations_penalties_reg_track.py

environmental-permits-reg-track-validate:
	$(PY) scripts/validate_environmental_permits_reg_track.py

environmental-air-quality-reg-track-validate:
	$(PY) scripts/validate_environmental_air_quality_reg_track.py

environmental-service-providers-reg-track-validate:
	$(PY) scripts/validate_environmental_service_providers_reg_track.py

environmental-fees-reg-track-validate:
	$(PY) scripts/validate_environmental_fees_reg_track.py

rett-law-track-validate:
	$(PY) scripts/validate_rett_law_track.py

universities-law-track-validate:
	$(PY) scripts/validate_universities_law_track.py

privatization-law-track-validate:
	$(PY) scripts/validate_privatization_law_track.py

antiquities-heritage-law-track-validate:
	$(PY) scripts/validate_antiquities_heritage_law_track.py

child-protection-law-track-validate:
	$(PY) scripts/validate_child_protection_law_track.py

protection-from-abuse-law-track-validate:
	$(PY) scripts/validate_protection_from_abuse_law_track.py

associations-ngo-law-track-validate:
	$(PY) scripts/validate_associations_ngo_law_track.py

audiovisual-media-law-track-validate:
	$(PY) scripts/validate_audiovisual_media_law_track.py

sports-law-track-validate:
	$(PY) scripts/validate_sports_law_track.py

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
