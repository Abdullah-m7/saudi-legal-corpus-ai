# Saudi Companies Law — Arabic–Chinese Reference Translation
## Book One / الباب الأول · Articles 1–34 · 第一编（第一条至第三十四条）

沙特《公司法》第一编 阿拉伯语–中文 **参考译本** — 结构化优先的、可验证的、面向 LLM/RAG 的法律翻译语料库。

> **Non-official reference translation. Not legal advice.** This is a verified concise
> reference translation of the whole of Book One (Articles 1–34), **not** an official or
> word-for-word full legal translation. The only binding text is the Arabic original in the
> official gazette *Umm Al-Qura*. See [`NOTICE.md`](NOTICE.md).
>
> - **العربية:** هذه الوثيقة ترجمة مرجعية موجزة ومحققة للباب الأول كاملًا من نظام الشركات السعودي،
>   المواد 1–34، وليست ترجمة رسمية أو حرفية كاملة للنص النظامي.
> - **中文：** 本文件为沙特《公司法》第一编（第一条至第三十四条）完整范围的经核验参考译本，
>   采用摘要式法律表达，并非官方译本或逐字全文翻译。

---

## Core principle — structured-first

The PDF in `inputs/` is the **design/reference artifact**, not the canonical long-term
source. Canonical structured sources (JSON under `data/`) are authored first; all readable
outputs are **generated** from them.

```
data/articles/*.json   →  canonical source of truth (34 articles)
        │
        ├─ scripts/build_jsonl.py        →  data/articles/*.jsonl   (LLM/RAG chunks)
        ├─ scripts/render_book_html.py   →  dist/book1.html         (searchable/copyable)
        └─ scripts/render_pdf_weasyprint →  dist/book1.pdf          (print/share-ready)
```

- **HTML = searchable/copyable canonical text view** (no rasterized legal text; RTL/LTR correct;
  Arabic **and** Chinese are real selectable/searchable text).
- **PDF = print/share-ready *visual* version** (via WeasyPrint; optional).

> **On the PDF text layer.** The PDF is a *visual/print-ready* rendering. Its Chinese text is
> clean, but Arabic (RTL, shaped/joined script) does **not** always copy or search cleanly from
> the PDF text layer — this is a known limitation of PDF text extraction for Arabic, not a
> defect in the data. For reliable copy/paste/search of Arabic, use **`dist/book1.html`**, which
> is the canonical text view. No low-level ActualText PDF hacks are attempted in this phase.

The print PDF also differs from the HTML by design: the cover is a full title page, and the
coverage matrix is a **one-page compact overview** (المادة | الحالة | ملاحظة). The full
six-column matrix is available in the HTML view.

---

## Repository layout

| Path | What |
|------|------|
| `inputs/` | Reference PDF (design artifact, not canonical) |
| `data/metadata/` | `work.json` (scope, disclaimers), `source_provenance.json` |
| `data/articles/` | Canonical `*.json` (34 articles) + generated `*.jsonl` |
| `data/glossary/` | `ar_zh_legal_terms.json` (validated terminology) |
| `data/coverage/` | `book1_coverage_matrix.json` (Articles 1–34) |
| `data/qa/` | `known_issues.json` (open QA + `NEEDS_OFFICIAL_TEXT_CHECK`) |
| `content/ar` `zh` `bilingual` | Generated Markdown books |
| `content/notes/` | `translator_notes.md`, `review_log.md` |
| `schemas/` | JSON Schemas for article / glossary / coverage |
| `src/saudi_law_corpus/` | Loader, validator, renderers, QA rules (stdlib-first) |
| `scripts/` | CLI entry points (`gen_articles`, `build_jsonl`, `validate_corpus`, renderers) |
| `templates/` | `book.html.j2` + `styles.css` |
| `tests/` | pytest: coverage, schema, terminology, render smoke |
| `dist/` | Build output (`book1.html`, `book1.pdf`) |

---

## Quick start

```bash
# optional: install extras (core runs on the standard library alone)
pip install -e ".[all]"

make validate   # schema + legal-translation QA checks
make test       # pytest
make build      # jsonl + validate + html (+ pdf if WeasyPrint present)
```

Individual targets: `make data | jsonl | validate | test | html | pdf | build | all | clean`.

### Dependencies (all optional; graceful fallback)

| Extra | Package | Used by | Fallback if missing |
|-------|---------|---------|---------------------|
| `render` | `jinja2` | HTML rendering | pure-Python HTML builder |
| `validate` | `jsonschema` | schema validation | minimal built-in structural check |
| `pdf` | `weasyprint` | PDF rendering | skipped with guidance (HTML is canonical) |
| `extract` | `pypdf` | PDF text diagnostics | script prints install hint |
| `test` | `pytest` | test suite | — |

---

## Using this repo for LLM / RAG

The article chunks are in **`data/articles/book1_articles_001_034.jsonl`** — **one line per
article**, self-contained and retrieval-friendly.

```python
import json

with open("data/articles/book1_articles_001_034.jsonl", encoding="utf-8") as fh:
    articles = [json.loads(line) for line in fh]   # each line is one article

art = next(a for a in articles if a["article_number"] == 8)
print(art["retrieval_title"], "→", art["chinese_translation"][:40])
```

Or use the Python loader (standard library only):

```python
import sys; sys.path.insert(0, "src")
from saudi_law_corpus import list_articles, get_article, search_keyword

list_articles()              # all 34 articles
get_article(29)              # Article 29 — Liability Action
search_keyword("破产法")      # [Article 29]
```

Each JSONL line includes: `article_number`, `section_ar` / `section_zh`, Arabic title,
Chinese title, `arabic_reference_summary`, `chinese_translation`, `keywords_ar`,
`keywords_zh`, `legal_risk_tags`, `retrieval_title`, `coverage_status`, and a `disclaimer`
flag.

**Guidance for LLM/RAG use**

- Do **not** treat this as official legal advice — it is a non-official reference translation.
- Always **cite `article_number`** and `data/metadata/source_provenance.json` when quoting.
- Do **not hallucinate beyond the structured fields**. If a point is not in the data, it is
  not established here.
- Respect `coverage_status` (`covered` / `expanded_after_review` /
  `needs_official_text_check`) and the `NEEDS_OFFICIAL_TEXT_CHECK` flag.

---

## Validation checklist (`make validate`)

1. Articles 1–34 all exist · 2. No duplicate numbers · 3. Arabic + Chinese present for every
article · 4. Articles 5, 6, 8, 9, 12, 13, 14, 17, 19, 20, 29 marked `expanded_after_review`
· 5. Article 8 has **no** `善意第三人` · 6. Article 13 has both `股份公司` and `简易股份公司`
· 7. Article 27 has `公开竞争程序` · 8. Article 29 has `破产法` · 9. Article 31 has
`决策评估规则` **and** `BJR` · 10. Article 34 has both `赎回权` and `优先购买权` · 11.
Disclaimer says non-official & not legal advice · 12. Scope says Articles 1–34.

---

## Book One scope

- **العربية:** الباب الأول كاملًا: الأحكام العامة، تأسيس الشركة، مالية الشركة، إدارة الشركة،
  المسؤولية والتنفيذ — المواد 1–34.
- **中文：** 第一编（全）：总则、公司设立、公司财务、公司管理、责任与执行（第一条至第三十四条）。

Instrument: نظام الشركات — المرسوم الملكي رقم (م/132) وتاريخ 1443/12/1هـ (2022).

## License

Source code: **MIT** ([`LICENSE`](LICENSE)). Legal content: see [`NOTICE.md`](NOTICE.md).
