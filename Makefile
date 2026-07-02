# Saudi Companies Law — Book One corpus build
# Structured-first: JSON is canonical; JSONL/HTML/PDF are generated from it.

PY ?= python3
export PYTHONPATH := src:$(PYTHONPATH)

.PHONY: help data jsonl markdown validate test html pdf build clean all

help:
	@echo "Targets:"
	@echo "  make data      - regenerate canonical articles JSON from scripts/gen_articles.py"
	@echo "  make jsonl     - build data/articles/*.jsonl from canonical JSON"
	@echo "  make markdown  - render content/{ar,zh,bilingual} Markdown books"
	@echo "  make validate  - run schema + legal-translation QA checks"
	@echo "  make test      - run pytest"
	@echo "  make html      - render dist/book1.html (searchable/copyable canonical text)"
	@echo "  make pdf       - render dist/book1.pdf via WeasyPrint (optional; print-ready)"
	@echo "  make build     - jsonl + validate + html (+ pdf if WeasyPrint available)"
	@echo "  make all       - data + build + test"
	@echo "  make clean     - remove generated artifacts in dist/ and the JSONL"

data:
	$(PY) scripts/gen_articles.py

jsonl:
	$(PY) scripts/build_jsonl.py

markdown:
	$(PY) scripts/render_markdown.py

validate:
	$(PY) scripts/validate_corpus.py

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

clean:
	rm -f dist/book1.html dist/book1.pdf data/articles/book1_articles_001_034.jsonl
