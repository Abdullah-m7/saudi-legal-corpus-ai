# Saudi Companies Law — Arabic–Chinese Reference Translation
## Book One / الباب الأول · Articles 1–34 · 第一编（第一条至第三十四条）

沙特《公司法》第一编 阿拉伯语–中文 **参考译本** — 结构化优先的、可验证的、面向 LLM/RAG 的法律翻译语料库。

> **Non-official reference translation. Not legal advice.** This is an **internally reviewed**
> concise reference translation of the whole of Book One (Articles 1–34) — QA-reviewed against
> the attached reference translation source, **not** yet verified article-by-article against the
> official *Umm Al-Qura* text, and **not** an official or word-for-word full legal translation.
> The only binding text is the Arabic original in the official gazette *Umm Al-Qura*.
> See [`NOTICE.md`](NOTICE.md).
>
> - **العربية:** هذه الوثيقة ترجمة مرجعية موجزة ومراجَعة داخليًا مقابل مصدر الترجمة المرفق للباب الأول
>   كاملًا من نظام الشركات السعودي، المواد 1–34، ولم تُدقَّق بعد مادةً مادةً مقابل النص الرسمي، وليست
>   ترجمة رسمية أو حرفية كاملة للنص النظامي.
> - **中文：** 本文件为沙特《公司法》第一编（第一条至第三十四条）完整范围的**经内部审校**参考译本，
>   已对照所附参考翻译来源进行内部质检，但**尚未逐条对照官方文本核验**，采用摘要式法律表达，
>   并非官方译本或逐字全文翻译。

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

### Build outputs (`dist/`) policy

`dist/book1.html` and `dist/book1.pdf` are **generated artifacts and are git-ignored** — they
are **not** tracked in the repository. Regenerate them from the canonical data at any time:

```bash
make build          # -> dist/book1.html (+ dist/book1.pdf if WeasyPrint is installed)
make html           # -> dist/book1.html only
```

Only `dist/.gitkeep` is tracked, so the directory exists on a fresh clone. If you want a
browsable HTML committed into the repo, that is an explicit owner decision — say so and it can
be force-tracked; by default it stays generated-on-demand.

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
| `dist/` | Build output (`book1.html`, `book1.pdf`) — **generated, git-ignored** (see below) |

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

## Book Two / الباب الثاني — شركة التضامن / 无限公司 · Articles 35–50

Book Two covers the **general partnership** (شركة التضامن / 无限公司（普通合伙性质）), Articles
35–50, from formation to termination. It uses the **same structured-first architecture** as Book
One; the shared loader, validators and renderers are book-aware (`--book 1` / `--book 2`), and all
Book One commands continue to work unchanged.

- **العربية:** الباب الثاني كاملًا: شركة التضامن — من التأسيس إلى الانتهاء — المواد 35–50.
- **中文：** 第二编（全）：无限公司 — 从设立到终止（第三十五条 至 第五十条）。

**Generated files**

| File | What |
|------|------|
| `data/articles/book2_articles_035_050.json` | Canonical Book Two articles (35–50) |
| `data/articles/book2_articles_035_050.jsonl` | LLM/RAG chunks (one line per article) |
| `data/coverage/book2_coverage_matrix.json` | Coverage matrix (16 rows) |
| `content/{ar,zh,bilingual}/book2.md` | Generated Markdown books |
| `content/notes/book2_translator_notes.md`, `book2_review_log.md` | Notes & review log |
| `dist/book2.html` (git-ignored) | Searchable/copyable canonical HTML view |
| `dist/book2.pdf` (git-ignored) | Print-ready visual PDF (local, if WeasyPrint present) |

**Build**

```bash
make book2-validate   # schema + Book Two QA rules
make book2-jsonl      # -> data/articles/book2_articles_035_050.jsonl
make book2-html       # -> dist/book2.html (+ Book Two Markdown)
make book2-pdf        # -> dist/book2.pdf (optional; WeasyPrint)
make book2-build      # jsonl + validate + html (+ pdf)
make books-build      # build both books
```

**LLM / RAG usage** — identical to Book One; load the JSONL (one article per line) and cite
`article_number` + `source_provenance`. Use Book Two for `شركة التضامن` questions and always keep
the legal-personality caveat below in view.

**Trust limitations (Book Two)** — this is an **internally reviewed** reference translation
(مراجَعة داخليًا / 经内部审校), QA-reviewed against the attached reference source. It has **not**
been verified article-by-article against the official *Umm Al-Qura* text: every Book Two article
has `translation_mode: internally_reviewed_summary` and `source.official_text_check: needs_check`.
It is **not** an official translation and **not** legal advice.

> **Legal-personality caveat.** Saudi **شركة التضامن** is translated functionally as
> **无限公司（普通合伙性质）** but has an **independent legal personality** under Saudi law and is
> **not** identical to Chinese partnership entities (普通合伙企业). The functional use of
> 合伙人 / 普通合伙人 does not erase that legal personality. **Unlimited joint liability**
> (无限连带责任) and **merchant status** (商人资格) attach to partners — general partnership
> carries very high personal risk.

Instrument: same Royal Decree as Book One (م/132, 1443/12/1هـ).

## Book Three / الباب الثالث — شركة التوصية البسيطة / 两合公司 · Articles 51–57

Book Three covers the **limited partnership** (شركة التوصية البسيطة / 两合公司（有限合伙性质）),
Articles 51–57. Same structured-first, book-aware architecture as Books One and Two; all prior
commands continue to work unchanged.

- **العربية:** الباب الثالث كاملًا: شركة التوصية البسيطة — المواد 51–57.
- **中文：** 第三编（全）：两合公司（有限合伙性质）（第五十一条 至 第五十七条）。

**Generated files**

| File | What |
|------|------|
| `data/articles/book3_articles_051_057.json` | Canonical Book Three articles (51–57) |
| `data/articles/book3_articles_051_057.jsonl` | LLM/RAG chunks (one line per article) |
| `data/coverage/book3_coverage_matrix.json` | Coverage matrix (7 rows) |
| `content/{ar,zh,bilingual}/book3.md` | Generated Markdown books |
| `content/notes/book3_translator_notes.md`, `book3_review_log.md` | Notes & review log |
| `dist/book3.html` (git-ignored) | Searchable/copyable canonical HTML view |
| `dist/book3.pdf` (git-ignored) | Print-ready visual PDF (local, if WeasyPrint present) |

**Build**

```bash
make book3-validate   # schema + Book Three QA rules
make book3-jsonl      # -> data/articles/book3_articles_051_057.jsonl
make book3-html       # -> dist/book3.html (+ Book Three Markdown)
make book3-pdf        # -> dist/book3.pdf (optional; WeasyPrint)
make book3-build      # jsonl + validate + html (+ pdf)
make books-build      # build all books
```

**LLM / RAG usage** — identical to Books One and Two; load the JSONL (one article per line) and
cite `article_number` + `source_provenance`. Use Book Three for `شركة التوصية البسيطة` questions.

**Trust limitations (Book Three)** — this is an **internally reviewed** reference translation
(مراجَعة داخليًا / 经内部审校), QA-reviewed against the attached reference source. It has **not**
been verified article-by-article against the official *Umm Al-Qura* text: every Book Three article
has `translation_mode: internally_reviewed_summary` and `source.official_text_check: needs_check`.
It is **not** an official translation and **not** legal advice.

> **Two partner classes.** A **general partner** (الشريك المتضامن / 普通合伙人（无限责任合伙人）)
> bears unlimited joint liability; a **limited partner** (الشريك الموصي / 有限合伙人) is liable
> **only up to its contribution** (仅以出资额为限), does **not** acquire merchant status
> (有限合伙人不取得商人资格), and may **not** take part in external management (有限合伙人不得参与
> 对外管理) — doing so exposes it to personal joint liability. Saudi `شركة التوصية البسيطة` has
> independent legal personality and is **not** identical to Chinese limited partnership entities
> (有限合伙企业).

Instrument: same Royal Decree as Book One (م/132, 1443/12/1هـ).

## Book Four / الباب الرابع — شركة المساهمة / 股份公司 (JSC) · Articles 58–137 — status

**Book Four is in the model-1b infrastructure stage. Full content generation has NOT started.**

- Book Four covers the **joint-stock company** (شركة المساهمة / 股份公司, JSC), **Articles 58–137
  (80 articles)**.
- The reference source (`inputs/bab4_source.pdf`) is a **thematic / tabular summary of core
  provisions**, **not** a per-article translation — only ~33 of the 80 articles are explicitly
  covered.
- **Data-model 1b (owner-approved):** canonical **provision** records are created only for
  explicitly-covered provisions (a provision may map to one or more article numbers); a
  **coverage matrix tracks all Articles 58–137**
  (`data/coverage/book4_coverage_matrix.json`), and **uncovered articles remain
  `needs_official_text_check`** with **no invented content**. See
  [`docs/book4_preflight/BOOK4_MODEL_1B_DECISION.md`](docs/book4_preflight/BOOK4_MODEL_1B_DECISION.md)
  and [`schemas/book4_provision.schema.json`](schemas/book4_provision.schema.json).
- Infrastructure validation: `make book4-validate` (coverage matrix + guardrails; no content is
  built). There is intentionally **no `make book4-build`** yet.
- Future Book Four content lands as **section-split PRs** (58–66 / 67–83 / 84–102 / 103–120 /
  121–137).
- **Section 1 (设立与资本 / التأسيس ورأس المال)**: provision records added for the **explicit source
  articles 58, 59, 60, 66 only** (`data/articles/book4_provisions_058_066.json`; build via
  `make book4-section1-build`). **Articles 61–65 remain uncovered / `needs_official_text_check`**.
  This is **not** a full Book Four translation and there is no `content/*/book4.md` — only
  `content/*/book4_section1.md` (clearly labelled Section 1, provisions-based).
- **Section 2 (董事会与治理 / مجلس الإدارة والحوكمة)**: next model-1b section. Provision records added
  for the **explicit source articles 67, 68, 71, 72, 75, 77 only** (the source groups 67 & 68 into
  one provision, so 5 provisions over 6 articles) —
  `data/articles/book4_provisions_067_083.json`; build via `make book4-section2-build`. **The other
  Section-2 articles (69, 70, 73, 74, 76, 78–83) remain uncovered / `needs_official_text_check`** with
  no invented content. Section-only outputs `content/*/book4_section2.md` — **not** a full Book Four
  translation and no `content/*/book4.md`.
- **Section 3 (股东大会 / الجمعية العامة)**: model-1b provision records added **after owner scope
  reconciliation** (Option 1 — reconcile to the source; see
  [`docs/book4_preflight/BOOK4_SECTION3_SCOPE_DECISION.md`](docs/book4_preflight/BOOK4_SECTION3_SCOPE_DECISION.md)).
  Provision records for the **explicit source articles 85, 87, 92, 93, 99, 101, 102 only**
  (grouped by the source's thematic blocks: [85,87], [92,93], [99], [101], [102]) —
  `data/articles/book4_provisions_084_102.json`; build via `make book4-section3-build`.
  **Articles 84, 89 and 100 were reclassified to uncovered / `needs_official_text_check`** (84 & 89
  have no distinct source content; 100 because the source tags circulation as 101 only), and the
  other Section-3 articles (86, 88, 90, 91, 94–98) remain uncovered. Section-only outputs
  `content/*/book4_section3.md` — **not** a full Book Four translation and no `content/*/book4.md`.
- **Section 4 (股份、债务工具与融资凭证 / الأسهم وأدوات الدين والصكوك)**: model-1b provision records added
  **after owner scope reconciliation** (Option 1 — reconcile to the source; see
  [`docs/book4_preflight/BOOK4_SECTION4_SCOPE_DECISION.md`](docs/book4_preflight/BOOK4_SECTION4_SCOPE_DECISION.md)).
  Provision records for the **explicit source articles 108, 113, 115, 117 only** (single-article
  blocks: [108], [113], [115], [117]) — `data/articles/book4_provisions_103_120.json`; build via
  `make book4-section4-build`. **Article 110 was reclassified to uncovered /
  `needs_official_text_check`** (the source only cross-references it as `（第110、89条）` under Article
  108's types/classes rule; no distinct block), and the other Section-4 articles (103–107, 109, 111,
  112, 114, 116, 118–120) remain uncovered / `needs_official_text_check` with no invented content.
  Section-only outputs `content/*/book4_section4.md` — **not** a full Book Four translation, **not**
  an official translation, **not** legal advice, and no `content/*/book4.md`.
- **Section 5 (财务、利润与资本变更 / المالية والأرباح وتغيير رأس المال)**: model-1b provision records for
  the **explicit source articles 123, 124, 126, 127, 128, 129, 130, 132, 133 only** (grouped by the
  source's thematic blocks: [123,124] reserves, [126,127] capital increase, [128,129,130] pre-emption
  rights, [132] grave losses, [133] capital reduction) — `data/articles/book4_provisions_121_137.json`;
  build via `make book4-section5-build`. Here the **coverage matrix and the source PDF agree** on the
  explicit set — no reclassification was needed. **Articles 121, 122, 125, 131, 134, 135, 136, 137
  remain uncovered / `needs_official_text_check`** (134 & 135 appear only as a cross-reference in the
  capital-reduction block) with no invented content. Section-only outputs `content/*/book4_section5.md`
  — **not** a full Book Four translation, **not** an official translation, **not** legal advice, and no
  `content/*/book4.md`.
- Trust posture unchanged: internally reviewed (مراجَعة داخليًا / 经内部审校);
  `official_text_check = needs_check`; never `verified` / `محققة` / `经核验`; book-specific
  disclaimer (第四编 / الباب الرابع, 58–137). Listing/CMA matters read with the Capital Market Law.
- **Not an official translation and not legal advice.**

## Arabic Legal LLM-ready layer

A **structured Arabic legal-understanding layer** built **on top of** the corpus to power
**Arabic legal RAG / search / reasoning** (retrieval, question answering, rule extraction). It is
**metadata only** — it does **not** replace the official statutory text, does **not** change any
existing article/provision wording or Chinese translations, and is **not legal advice**.

- **Schema:** [`schemas/arabic_legal_llm.schema.json`](schemas/arabic_legal_llm.schema.json)
  (draft-07). One record schema serves **both** per-article records for Books 1–3
  (`record_type: "article"`) **and** thematic **provision** records for Book Four model-1b
  (`record_type: "provision"`, one or more `article_numbers`). Each record carries structured
  Arabic fields: `legal_subject_ar`, `legal_rule_summary_ar`, `legal_basis_type`, `actors_ar`,
  `rights_ar`, `obligations_ar`, `prohibitions_ar`, `conditions_ar`, `exceptions_ar`,
  `legal_effects_ar`, `liability_ar`, `monetary_thresholds`, `deadlines_ar`,
  `competent_authorities_ar`, `cross_references_ar`, `keywords_ar`, `search_queries_ar`,
  `risk_flags`, and `source_trust`.
- **Data:** [`data/arabic_legal_llm/`](data/arabic_legal_llm/).
  - **Books 1–3 backfill** — one per-article record for every stable article:
    [`book1_ar_legal_llm.json`](data/arabic_legal_llm/book1_ar_legal_llm.json) (34 records,
    Articles 1–34), [`book2_ar_legal_llm.json`](data/arabic_legal_llm/book2_ar_legal_llm.json)
    (16 records, Articles 35–50), and
    [`book3_ar_legal_llm.json`](data/arabic_legal_llm/book3_ar_legal_llm.json) (7 records,
    Articles 51–57). Each record's `legal_rule_summary_ar` is the article's own
    internally-reviewed Arabic reference summary; the other Arabic fields are derived
    understanding of it.
  - **Book Four Section 1 pilot** —
    [`book4_section1_ar_legal_llm.json`](data/arabic_legal_llm/book4_section1_ar_legal_llm.json),
    derived **only** from the existing Book Four Section 1 provisions — records for **Articles 58,
    59, 60, 66 only**. **Articles 61–65 remain uncovered** and get **no records** (no invented
    content).
  - **Book Four Section 2 (董事会与治理 / مجلس الإدارة والحوكمة)** —
    [`book4_section2_ar_legal_llm.json`](data/arabic_legal_llm/book4_section2_ar_legal_llm.json),
    derived **only** from the Book Four Section 2 model-1b provisions — **5 provision records**
    mapped to **[67, 68], [71], [72], [75], [77]**. Each record's `legal_rule_summary_ar` is
    read verbatim from the corresponding provision's `arabic_reference_summary` (exact-match
    tested). **Articles 69, 70, 73, 74, 76, 78–83 remain uncovered** and get **no records**.
  - **Book Four Section 3 (股东大会 / الجمعية العامة)** —
    [`book4_section3_ar_legal_llm.json`](data/arabic_legal_llm/book4_section3_ar_legal_llm.json),
    derived **only** from the Book Four Section 3 model-1b provisions — **5 provision records**
    mapped to **[85, 87], [92, 93], [99], [101], [102]**. Each record's `legal_rule_summary_ar`
    is read verbatim from the corresponding provision's `arabic_reference_summary` (exact-match
    tested). **Articles 84, 86, 88, 89, 90, 91, 94–98, 100 remain uncovered** and get **no records**.
  - **Book Four Section 4 (股份、债务工具与融资凭证 / الأسهم وأدوات الدين والصكوك)** —
    [`book4_section4_ar_legal_llm.json`](data/arabic_legal_llm/book4_section4_ar_legal_llm.json),
    derived **only** from the Book Four Section 4 model-1b provisions — **4 provision records**
    mapped to **[108], [113], [115], [117]**. Each record's `legal_rule_summary_ar` is read
    verbatim from the corresponding provision's `arabic_reference_summary` (exact-match tested).
    **Article 110 remains uncovered** (owner Option 1 reclassified it `not_explicit_in_source`),
    and Articles **103–107, 109, 111, 112, 114, 116, 118–120** also remain uncovered — all get
    **no records** (`needs_official_text_check`).
  - **Book Four Section 5 (财务、利润与资本变更 / المالية والأرباح وتغيير رأس المال)** —
    [`book4_section5_ar_legal_llm.json`](data/arabic_legal_llm/book4_section5_ar_legal_llm.json),
    derived **only** from the Book Four Section 5 model-1b provisions — **5 provision records**
    mapped to **[123,124], [126,127], [128,129,130], [132], [133]**. Each record's
    `legal_rule_summary_ar` is read verbatim from the corresponding provision's
    `arabic_reference_summary` (exact-match tested). **Articles 121, 122, 125, 131, 134, 135,
    136, 137 remain uncovered** — all get **no records** (134 & 135 appear only as a
    cross-reference in the source's capital-reduction block).
  - Book Four stays **model 1b** (provision-covered articles only) — this is **not** full
    Book Four article coverage; uncovered articles remain `needs_official_text_check`.
    Arabic Legal LLM now covers **Books 1–3 + Book Four Sections 1, 2, 3, 4, 5** (8 files, 80 records).
- **Build / validate:** `make arabic-legal-llm-data` (regenerate all layer files) and
  `make arabic-legal-llm-validate` (schema + guardrails over every layer file). Tests:
  [`tests/test_arabic_legal_llm_layer.py`](tests/test_arabic_legal_llm_layer.py),
  [`tests/test_arabic_legal_llm_books1_3.py`](tests/test_arabic_legal_llm_books1_3.py), and
  [`tests/test_arabic_legal_llm_book4_section2.py`](tests/test_arabic_legal_llm_book4_section2.py).
- **Trust posture unchanged:** the underlying text stays an internally-reviewed reference
  summary/provision (`text_type: internally_reviewed_summary` / `internally_reviewed_provision`);
  every record keeps `source_trust.official_text_check = needs_check`; banned overclaim terms
  (`verified` / `محققة` / `经核验`) never appear.
- **Not an official translation and not legal advice.** The binding text is the Arabic in
  *Umm al-Qura*.

## Official English guidance source

The repository now tracks an **official English guidance translation** source of the
Companies Law, from the **Bureau of Experts at the Council of Ministers — Official
Translation Department** (Royal Decree No. M/132).

- This is **source intake only** — provenance, coverage planning, and an optional text
  extractor. See [`docs/official_english_source/`](docs/official_english_source/) and
  [`data/metadata/official_english_source.json`](data/metadata/official_english_source.json).
- Trust label: **`official_guidance_translation`**. The PDF itself states: *"This translation
  is provided for guidance. The governing text is the Arabic text."*
- The **English Legal LLM-ready layer is not created yet** and **no English per-article records
  exist yet** — those are separate future PRs.
- **Arabic remains the governing legal text** (`governing_text_language = ar`); the English is
  guidance only.
- Files: `inputs/companies_law_official_english_guidance.pdf`; optional extractor
  `make official-english-source-extract` → `data/extracted/…` (git-ignored, regenerable);
  validation `make official-english-source-validate`.
- **Not legal advice.**

## Official English reference alignment

The **English reference alignment** now covers **Books One–Three (Articles 1–57)** plus the
**Book Four Section 1, Section 2, Section 3, Section 4 and Section 5** provision-covered articles:

- **Book One / Part 1 — General Provisions:** Articles **1–34**.
- **Book Two / Part 2 — General Partnerships:** Articles **35–50**.
- **Book Three / Part 3 — Limited Partnership:** Articles **51–57**.
- **Book Four / Part 4 — Joint-Stock Company, Section 1 (Formation and Capital):** Articles
  **58, 59, 60, 66 only** — this follows the Book Four **model 1b** coverage (provision-covered
  articles only). **Articles 61–65 remain uncovered** in the Book Four source model (no records).
- **Book Four / Part 4 — Joint-Stock Company, Section 2 (Board and Governance):** Articles
  **67, 68, 71, 72, 75, 77 only** (model 1b). The official English source renders 67 & 68 under
  separate `Article` headings, so the English reference is **per-article** here (6 records).
  **Articles 69, 70, 73, 74, 76, 78–83 remain uncovered**, and Articles 84–137 are not part of
  this scope. Book Four stays model 1b — **not** full Book Four coverage.
- **Book Four / Part 4 — Joint-Stock Company, Section 3 (General Assemblies):** Articles
  **85, 87, 92, 93, 99, 101, 102 only** (owner-reconciled model 1b) — **per-article, 7 records**.
  **Article 100** ("Issuing a Decision by Circulation") **is excluded even though it appears in
  the official English source**: the reconciled Book Four source maps the circulation provision to
  **Article 101 only**. Articles **84, 86, 88–91, 94–98, 100 remain uncovered** (84/89/100 are the
  owner-reconciled reclassified rows), and Articles 103–137 are not part of this scope.
- **Book Four / Part 4 — Joint-Stock Company, Section 4 (Shares, Debt Instruments and Sukuk):**
  Articles **108, 113, 115, 117 only** (owner-reconciled model 1b) — **per-article, 4 records**.
  **Article 110** ("Amendment of Share-Associated Rights and Obligations") **is excluded even
  though it appears in the official English source**: the owner-reconciled Book Four model
  reclassified Article 110 as `not_explicit_in_source` (no distinct provision in the source PDF).
  Articles **103–107, 109, 110, 111, 112, 114, 116, 118–120 remain uncovered**, and Articles
  121–137 are not part of this scope. Book Four stays model 1b — **not** full Book Four coverage.
- **Book Four / Part 4 — Joint-Stock Company, Section 5 (Finance, Profits and Capital Changes):**
  Articles **123, 124, 126, 127, 128, 129, 130, 132, 133 only** (model 1b) — **per-article, 9
  records**. **Articles 134 & 135** ("Issuance of a Capital Decrease Decision" / "Capital Decrease
  Procedures") **are excluded even though they appear in the official English source**: the Book
  Four model-1b source treats them as **cross-reference only** in the capital-reduction block.
  Articles **121, 122, 125, 131, 134, 135, 136, 137 remain uncovered**. Book Four stays model 1b —
  **not** full Book Four coverage.

- **Source:** the Bureau of Experts at the Council of Ministers / Official Translation
  Department English **guidance** PDF (`inputs/companies_law_official_english_guidance.pdf`).
- The English is **official guidance / reference only**
  (`english_source_status = official_guidance_translation`); the text is the source's own
  wording, segmented by its `Article N:` headings — **not** model-written (no generated
  summaries).
- **Arabic remains governing** (`governing_text_language = ar`). Article-level alignment is
  `manual_review_status = needs_manual_check` (not yet human-verified).
- The **English Legal LLM-ready layer is not created yet** — no `data/english_legal_llm/`, no
  `*_en_legal_llm.json`, no English reasoning metadata.
- Files: `data/english_reference/book{1,2,3}_en_reference.json`,
  `book4_section1_en_reference.json`, `book4_section2_en_reference.json`,
  `book4_section3_en_reference.json`, `book4_section4_en_reference.json` and
  `book4_section5_en_reference.json` (+ `.jsonl`), schema
  `schemas/english_reference.schema.json`. Build:
  `make english-reference-book1-data` / `english-reference-book2-data` /
  `english-reference-book3-data` / `english-reference-book4-section1-data` /
  `english-reference-book4-section2-data` / `english-reference-book4-section3-data` /
  `english-reference-book4-section4-data` / `english-reference-book4-section5-data`;
  validate: `make english-reference-validate` (**87 records** total).
- **Not legal advice.**

## English Legal LLM-ready layer (pilot)

The **English Legal LLM-ready layer** has been **started with a Book Four Section 1 pilot only**
— it is **not** full English Legal LLM coverage.

- **Scope:** Book Four / Part 4 — Section 1 (Establishment and Capital), **Articles 58, 59, 60, 66**
  — **4 `article_reference` records**
  ([`data/english_legal_llm/book4_section1_en_legal_llm.json`](data/english_legal_llm/book4_section1_en_legal_llm.json)).
- Each record's **`legal_rule_text_en` is copied verbatim** from the corresponding official English
  **reference alignment** record's `english_reference_text` — there are **no model-generated English
  legal summaries** and **no `legal_rule_summary_en`** field (the schema's `additionalProperties:false`
  forbids it). Only the derived structured metadata (subject, basis type, actors, rights, obligations,
  …, search queries) is authored.
- **English is guidance / reference only; Arabic remains governing**
  (`source_trust.english_source_status = official_guidance_translation`,
  `governing_text_language = ar`, `manual_review_status = needs_manual_check`).
- **Not** full English Legal LLM coverage — **no** Books 1–3 records and **no** Book Four Sections 2–5
  records yet.
- Schema `schemas/english_legal_llm.schema.json`; build `make english-legal-llm-book4-section1-data`;
  validate `make english-legal-llm-validate`.
- **Not legal advice.**

## License

Source code: **MIT** ([`LICENSE`](LICENSE)). Legal content: see [`NOTICE.md`](NOTICE.md).
