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
        english-legal-llm-book4-section1-data english-legal-llm-book4-section2-data \
        english-legal-llm-book4-section3-data english-legal-llm-book4-section4-data \
        english-legal-llm-book4-section5-data english-legal-llm-validate \
        chinese-legal-llm-book4-section1-data chinese-legal-llm-book4-section2-data \
        chinese-legal-llm-book4-section3-data chinese-legal-llm-book4-section4-data \
        chinese-legal-llm-validate

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

# -- English Legal LLM-ready layer (PILOT: Book Four Section 1 only; 58,59,60,66) --
# legal_rule_text_en is verbatim from the English reference; no generated summaries.
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

chinese-legal-llm-validate:
	$(PY) scripts/validate_chinese_legal_llm.py

clean:
	rm -f dist/book1.html dist/book1.pdf data/articles/book1_articles_001_034.jsonl \
	      dist/book2.html dist/book2.pdf data/articles/book2_articles_035_050.jsonl \
	      dist/book3.html dist/book3.pdf data/articles/book3_articles_051_057.jsonl
