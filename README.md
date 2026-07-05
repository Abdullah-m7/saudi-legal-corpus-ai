# Saudi Legal Corpus for AI

**Multilingual, LLM-ready, official-source-based Saudi legal corpus for AI.**
It structures Saudi laws and regulations into **auditable, machine-readable
legal layers**. The **Saudi Companies Law is the first implemented law
profile**, not the whole project identity; **Chinese is one language layer**,
not the identity of the project.

> **New here?** Start with **[`START_HERE.md`](START_HERE.md)** · current state
> **[`STATUS.md`](STATUS.md)** · structure **[`REPOSITORY_MAP.md`](REPOSITORY_MAP.md)**
> · uses **[`USE_CASES.md`](USE_CASES.md)**.

**Repository name:** `saudi-legal-corpus-ai` (former name:
`saudi-companies-law-ar-zh-llm`). See [`REPOSITORY_RENAME.md`](REPOSITORY_RENAME.md).

## What this repository is

- A **multilingual, LLM-ready, official-source-based Saudi legal corpus for AI**.
- **Official Arabic source governs**; English and Chinese are **reference layers**.
- Canonical JSON → LLM/RAG chunks → generated human-readable views, each locked
  by **read-only, idempotent validators**.
- Built to serve **government entities, AI companies and model builders,
  enterprises operating in or entering Saudi Arabia, investors, researchers,
  developers, and ordinary users**.

## What this repository is not

- **Not** an official government publication; **no official translation** and
  **no official government adoption** are claimed.
- **Not** a full Chinese 281 layer and **not** a trilingual alignment (neither
  is created).
- **Not** a public release, and **not legal advice**.
- **Not** solely about Chinese, and **not** solely about investment guidance —
  those are one layer and one use case, respectively.

## Current implemented law profile — Saudi Companies Law

The **Saudi Companies Law (M/132, 1443H)** is the **first implemented law
profile**. Profile:
[`data/legal_corpus_factory/law_profiles/sa_companies_law_m132_1443.profile.json`](data/legal_corpus_factory/law_profiles/sa_companies_law_m132_1443.profile.json).
Additional laws can be onboarded as new profiles.

## Current language / layer status

| Layer | Language | Role | Status |
|-------|----------|------|--------|
| Official Arabic full LLM | Arabic | **Governing** | 281 articles |
| English full LLM | English | Reference/guidance | 281 articles |
| English reference | English | Reference | 281 articles |
| Chinese internal candidate | Chinese | Internal reference only | 189 records |
| Old Chinese Legal LLM | Chinese | Internal reference only | 5 files / 23 records |
| Chinese source extracted | Chinese | Source | 14 files |
| OCR / manual review queue | Arabic | Verification | 281 entries |

Chinese remediation and QA are **completed through P0-005**, and **all P1 batches
(P1-001..P1-004) remediation + QA are completed** (each PASS, no minor fixes);
**all five P2 batches (P2-001..P2-005) remediation + QA are completed** (each PASS, no minor fixes) —
**the full P2 expansion track is complete**; and the **final P3 confirmation batch (P3-CONF-001)
confirmation + QA are completed** (PASS 18/18, no minor fixes). **The full Chinese remediation program
(P0 → P1 → P2 → P3) is complete.** A **closure audit** verifies all 281 articles across 15 batches
are implemented with QA_PASS, no missing/duplicate articles, no prohibited content. See
[`reports/chinese_translation_review/CHINESE_REMEDIATION_PROGRAM_CLOSURE_AUDIT_AR.md`]. Validate:
`make chinese-remediation-program-closure-validate`. An **implementing regulations
intake scaffold** is created as a separate corpus track for future Arabic official
source intake — no text ingested yet. Validate:
`make implementing-regulations-intake-scaffold-validate`. A **listed joint-stock implementing
regulation Arabic source** (69 articles, 14 chapters) has been ingested from the official Umm
Al-Qura gazette — specialized to listed joint-stock companies only. Validate:
`make implementing-regulations-listed-jsc-arabic-source-validate`. A **general implementing
regulations Arabic source** (95 articles, 7 chapters, 4 forms) has been ingested from the
official Umm Al-Qura gazette — the general implementing regulation covering all company
forms. Validate: `make implementing-regulations-general-arabic-source-validate`. See **[`STATUS.md`](STATUS.md)** for the authoritative list.

## Quick navigation

| Go to | For |
|-------|-----|
| [`START_HERE.md`](START_HERE.md) | Onboarding for developers, reviewers, companies, government/AI stakeholders |
| [`STATUS.md`](STATUS.md) | Single source of truth: counts, what is complete, what is not |
| [`REPOSITORY_MAP.md`](REPOSITORY_MAP.md) | What each directory contains and what to open first |
| [`USE_CASES.md`](USE_CASES.md) | Practical uses, without overclaiming |
| [`docs/`](docs/) | Arabic doctrine, architecture, and UX principles |
| [`data/`](data/) | Source data + generated LLM/reference layers |
| [`schemas/`](schemas/) | JSON Schemas (incl. reusable factory schemas) |
| [`Makefile`](Makefile) | All validation & build targets (`make help`) |

## Quick validation

```bash
make legal-corpus-factory-foundation-validate   # foundation (doctrine/schemas/profile)
make validate                                    # Book One schema + QA
make book2-validate                              # Book Two
make book3-validate                              # Book Three
make book4-validate                              # repo book4 (JSC modeled scope)
make test                                        # full pytest suite
```

Per-layer validators (Arabic, English, English reference, Chinese layers, and
each Chinese remediation batch + QA) are listed by `make help`.

## Repository legal-review model

The **official Arabic source governs**; English and Chinese are reference
layers. The **repository owner has a legal background (bachelor of law)** and
runs **active repository legal review** (`repository_owner_review_active`).
**External legal review is optional** for enterprise or official adoption and
is **not required for repository use**.

## Official-status boundaries

**No official government publication is claimed. No official government adoption
is claimed. No official translation is claimed. Chinese is not official, not
binding, not governing. Not legal advice.**

---

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

## Book Four (repo `book4` convention) — شركة المساهمة / 股份公司 (JSC) · Articles 58–137 — status

> **Terminology — repo `book4` convention.** In this repository, **`book4` / "Book Four" / "Part 4"
> is an internal repository label** for the **modeled Joint-Stock Company scope** (شركة المساهمة /
> 股份公司, JSC — Articles 58–137). It is **not** a claim about the official structure of the Saudi
> Companies Law, which contains **281 articles across multiple official chapters/parts**. File,
> path, and Make-target names such as `book4_*` are **established repo conventions** and are kept
> as-is; wherever this README says "Book Four", read it as **"repo book4 (Joint-Stock Company
> modeled scope)"**, not as the whole Companies Law.

**The repo book4 (Joint-Stock Company) scope is in the model-1b infrastructure stage. Full content
generation has NOT started.**

- The repo book4 scope covers the **joint-stock company** (شركة المساهمة / 股份公司, JSC), **Articles
  58–137 (80 articles)**.
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

## Official Arabic statutory text foundation

The repository is being moved toward a **true official-Arabic-grounded** legal corpus, where the
**official Arabic statutory text is the canonical legal source** and every English/Chinese/LLM layer
aligns to official Arabic article IDs. This section is an honest status marker for that direction.

- **Current Arabic content is internally reviewed reference/summary material, *not* official
  statutory text.** The Arabic under `data/arabic_legal_llm/` and `data/articles/` is manually
  reconstructed Modern Standard Arabic (the reference PDF's Arabic layer extracted garbled) and has
  **not** been verified article-by-article against the official *Umm Al-Qura* text.
- **Official Arabic ingestion/verification is now explicitly planned and scaffolded** — schema,
  target data folder, source-packet requirements, verification plan, validator, and tests — but
  **no official Arabic text has been ingested or verified yet** (`official_arabic_text_status =
  not_ingested`, `article_by_article_verified = false`).
- **Arabic remains the governing legal language.** Until official Arabic **article-by-article
  verification** is completed, **do not treat the current Arabic summaries as official statutory
  text.**
- Architecture:
  [`schemas/official_arabic_article.schema.json`](schemas/official_arabic_article.schema.json),
  [`data/official_arabic/`](data/official_arabic/) (manifest
  [`ingestion_status.json`](data/official_arabic/ingestion_status.json)),
  [`docs/official_arabic_text/SOURCE_PACKET_REQUIREMENTS_AR.md`](docs/official_arabic_text/SOURCE_PACKET_REQUIREMENTS_AR.md),
  [`docs/official_arabic_text/OFFICIAL_ARABIC_VERIFICATION_PLAN_AR.md`](docs/official_arabic_text/OFFICIAL_ARABIC_VERIFICATION_PLAN_AR.md).
  Validate the scaffold with `make official-arabic-foundation-validate`.
- **To begin:** provide an official source packet (official gazette / official government source)
  per the source-packet requirements; ingestion then follows the verification plan. This is **not**
  a claim of a full official Arabic corpus — it is the foundation stage only. Not legal advice.

## Full official Arabic LLM-ready layer (281 articles)

- A **full official Arabic LLM-ready layer now exists** with **281 records** (Articles 1–281),
  built directly on the **exact `official_text_ar`** ingested from the Bureau of Experts
  owner-provided source packet — copied verbatim and SHA-256-checked, with mechanical retrieval
  metadata only (titles, path, conservative keywords/queries). **No OCR text is used**, and the
  layer adds **no summaries or legal analysis**.
- It is **separate from** the older Arabic summary/provision LLM layer under
  `data/arabic_legal_llm/` (8 files / 80 records), which is left untouched. New layer:
  [`data/official_arabic_legal_llm/`](data/official_arabic_legal_llm/), schema
  [`schemas/official_arabic_legal_llm.schema.json`](schemas/official_arabic_legal_llm.schema.json).
- **Arabic remains governing.** `article_by_article_verified` remains **false** because no direct
  automated verification against live BOE HTML has been performed — LLM-ready here means
  structured, retrievable, source-linked, and exact-text based, not verified. Not legal advice.
- Regenerate/validate with `make official-arabic-legal-llm-full-data` /
  `make official-arabic-legal-llm-full-validate`.

## Official Arabic user-provided text ingestion

A **full user-provided Arabic text packet** of the Companies Law (Royal Decree M/132, 1443/12/01 AH)
has been **ingested and segmented into exactly 281 article records**, each carrying its verbatim
`official_text_ar` and a SHA-256 hash.

- **Status: user-provided official text *candidate*, `ingested_unverified`.** It is **not yet
  verified** against *Umm Al-Qura* or the Bureau of Experts at the Council of Ministers
  (`article_by_article_verified = false`, `articles_verified = 0`). It is the **candidate official
  Arabic source for the upcoming verification** (Phases E–F of the verification plan).
- **Files:** raw packet
  [`inputs/official_arabic_companies_law_m132_1443_user_provided.md`](inputs/official_arabic_companies_law_m132_1443_user_provided.md);
  structured records
  [`data/official_arabic/companies_law_m132_1443_official_arabic_user_provided.json`](data/official_arabic/companies_law_m132_1443_official_arabic_user_provided.json)
  (281 records, 1–281; Article 1 = التعريفات, Article 281 = نفاذ النظام). Build with
  `make official-arabic-user-provided-data`; validate with `make official-arabic-ingestion-validate`.
- **Arabic remains the governing legal language.** The **current Arabic summaries remain secondary
  and non-official** until this candidate is verified against an official source and the layers are
  reconciled. The Arabic/English/Chinese LLM layers are unchanged by this ingestion.
- The ingestion preserves the legal text verbatim (no rewriting/paraphrasing/normalization; the
  Royal Decree / Council of Ministers preamble is kept as source metadata, not as article records).
  Not legal advice.

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
**repo book4 Section 1, Section 2, Section 3, Section 4 and Section 5** provision-covered articles.
(As above, `book N` / `Part N` are **internal repository labels**, not a claim about the official
Companies Law structure; repo book4 is the modeled Joint-Stock Company scope.)

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

### Full English reference alignment (281 articles)

- A **full official English BOE reference alignment now exists** with **281 records**
  (Articles 1–281), segmented from the official English guidance PDF by `Article N:` headings and
  preserving the verbatim official English text as `english_reference_text` (minimal whitespace
  normalization only — no translation, no summaries).
- It is **separate from** the older **87-record split** reference layer above (which is left
  untouched for backward compatibility). New file:
  [`data/english_reference/companies_law_m132_1443_en_reference_001_281.json`](data/english_reference/companies_law_m132_1443_en_reference_001_281.json).
- **English is official guidance only; Arabic remains governing.** `manual_review_status =
  needs_manual_check`; the file makes no binding/governing/verified claim, and per-part/book
  segmentation is deferred to manual review (conservative single mechanical grouping).
- The **English full LLM-ready layer is not created yet** — this is the reference/alignment stage.
  Build/validate: `make english-reference-full-281-data` /
  `make english-reference-full-281-validate`.

## Full English Legal LLM-ready layer (281 articles)

- A **full official English Legal LLM-ready layer now exists** with **281 records** (Articles
  1–281), built directly from the full official English BOE guidance **reference alignment**.
- Each record's **`legal_rule_text_en` is copied verbatim** from the reference
  `english_reference_text` (SHA-256-checked), with mechanical retrieval metadata only (titles,
  path, conservative keywords/queries) — no summaries, no translation, no legal analysis.
- It is **separate from** the old **87-record** English Legal LLM layer under
  `data/english_legal_llm/` (left untouched). New layer:
  [`data/official_english_legal_llm/`](data/official_english_legal_llm/), schema
  [`schemas/official_english_legal_llm.schema.json`](schemas/official_english_legal_llm.schema.json).
- **English is official guidance only (`guidance_only_not_binding`); Arabic remains governing.**
  Build/validate: `make official-english-legal-llm-full-data` /
  `make official-english-legal-llm-full-validate`.

## English Legal LLM-ready layer (Books 1–3 + repo book4 Sections 1–5)

The **English Legal LLM-ready layer** currently covers **Books 1–3 (Articles 1–57)** plus **repo
book4 Sections 1, 2, 3, 4 and 5** — the five thematic sections of the modeled Joint-Stock Company
scope (repo book4 convention; an internal repository label, not a claim about the official Companies
Law structure). This is **not** full Saudi Companies Law coverage: repo book4 stays model-1b
(provision-covered articles only, not all of Articles 58–137).

- **Books 1–3 (backfill) — one `article_reference` record per article:**
  - **Book 1 (General Provisions):** **Articles 1–34** — **34 records**
    ([`data/english_legal_llm/book1_en_legal_llm.json`](data/english_legal_llm/book1_en_legal_llm.json)).
  - **Book 2 (General Partnerships):** **Articles 35–50** — **16 records**
    ([`data/english_legal_llm/book2_en_legal_llm.json`](data/english_legal_llm/book2_en_legal_llm.json)).
  - **Book 3 (Limited Partnership):** **Articles 51–57** — **7 records**
    ([`data/english_legal_llm/book3_en_legal_llm.json`](data/english_legal_llm/book3_en_legal_llm.json)).
  - **57 records total.** For this backfill the derived metadata is kept deliberately conservative:
    `legal_subject_en` reuses the reference record's own `article_heading_en`, `keywords_en` reuses the
    reference's approved `llm.keywords_en`, `legal_basis_type` is the conservative catch-all `mixed`,
    and the other derived arrays are left empty rather than inventing legal implications — the
    authoritative content is the verbatim `legal_rule_text_en`.
- **repo book4 Sections 1–5 (Joint-Stock Company modeled scope):**
  - **Section 1 (Establishment and Capital):** **Articles 58, 59, 60, 66** — **4 `article_reference`
    records** ([`data/english_legal_llm/book4_section1_en_legal_llm.json`](data/english_legal_llm/book4_section1_en_legal_llm.json)).
  - **Section 2 (Board of Directors and Governance):** **Articles 67, 68, 71, 72, 75, 77** — **6
    `article_reference` records**
    ([`data/english_legal_llm/book4_section2_en_legal_llm.json`](data/english_legal_llm/book4_section2_en_legal_llm.json)).
    The other Section-2 articles (69, 70, 73, 74, 76, 78–83) get **no records**.
  - **Section 3 (General Assemblies):** **Articles 85, 87, 92, 93, 99, 101, 102** — **7
    `article_reference` records**
    ([`data/english_legal_llm/book4_section3_en_legal_llm.json`](data/english_legal_llm/book4_section3_en_legal_llm.json)).
    The owner-reconciled uncovered articles (84, 89, 100) and the other uncovered Section-3 articles
    (86, 88, 90, 91, 94–98) get **no records**.
  - **Section 4 (Shares, Debt Instruments and Sukuk):** **Articles 108, 113, 115, 117** — **4
    `article_reference` records**
    ([`data/english_legal_llm/book4_section4_en_legal_llm.json`](data/english_legal_llm/book4_section4_en_legal_llm.json)).
    **Article 110** remains **excluded / uncovered** (owner-reconciled `not_explicit_in_source`), and
    the other uncovered Section-4 articles (103–107, 109, 111, 112, 114, 116, 118–120) get **no records**.
  - **Section 5 (Finance, Profits, and Capital Changes):** **Articles 123, 124, 126, 127, 128, 129,
    130, 132, 133** — **9 `article_reference` records**
    ([`data/english_legal_llm/book4_section5_en_legal_llm.json`](data/english_legal_llm/book4_section5_en_legal_llm.json)).
    **Articles 134 & 135** remain **excluded / uncovered** (cross-reference-only in the model-1b
    scope), and the other uncovered Section-5 articles (121, 122, 125, 131, 136, 137) get **no records**.
  - **30 records total** (repo book4 Sections 1–5).
- **English Legal LLM total: 8 files / 87 records** — Books 1–3 = 57 records; repo book4 Sections 1–5
  = 30 records.
- Each record's **`legal_rule_text_en` is copied verbatim** from the corresponding official English
  **reference alignment** record's `english_reference_text` — there are **no model-generated English
  legal summaries** and **no `legal_rule_summary_en`** field (the schema's `additionalProperties:false`
  forbids it). Only the derived structured metadata (subject, basis type, actors, rights, obligations,
  …, search queries) is authored, and every derived item is traceable to that article's own text.
- **English is guidance / reference only; Arabic remains governing**
  (`source_trust.english_source_status = official_guidance_translation`,
  `governing_text_language = ar`, `manual_review_status = needs_manual_check`).
- **Not** full Saudi Companies Law English Legal LLM coverage — this covers **Books 1–3 plus repo
  book4 Sections 1–5**; repo book4 stays model-1b (not all of Articles 58–137), and "book4" remains an
  internal repository label for the modeled Joint-Stock Company scope.
- Schema `schemas/english_legal_llm.schema.json`; build `make english-legal-llm-book1-data` /
  `-book2-data` / `-book3-data` / `-book4-section1-data` / `-section2-data` / `-section3-data` /
  `-section4-data` / `-section5-data`; validate `make english-legal-llm-validate`.
- **Not legal advice.**

## Chinese Bab 1 original-PDF translation review (Articles 1–34)

- The **original Bab 1 Chinese PDF** source has been ingested and **reviewed** (source-inventory
  stage), covering **Articles 1–34**. Chinese is an **internal working/reference translation only
  — not official, not binding; Arabic remains governing.**
- The review is **not yet converted into a Chinese LLM-ready layer**: many Bab 1 articles are
  condensed/summary style (e.g. Article 1 lists only the defined terms), so **several articles
  require expansion or retranslation from the Arabic before any full Chinese LLM-ready use.**
- Artifacts: source PDF under
  [`inputs/chinese_translation_source_pdfs/`](inputs/chinese_translation_source_pdfs/), extracted
  text [`data/chinese_translation_sources/`](data/chinese_translation_sources/), review
  [`reports/chinese_translation_review/`](reports/chinese_translation_review/). Validate:
  `make chinese-bab1-original-pdf-translation-review-validate`. Not legal advice.

### Chinese all-Babs source inventory (Babs 1–14, Articles 1–281)

- The **original Chinese source PDFs for Babs 1–14 now have a full source inventory** covering the
  expected law range **Articles 1–281**. Babs 1–3 carry per-article headings; Babs 4–14 are
  thematic-table / summary-style, so per-article Chinese text is only **partially** isolable and is
  recorded honestly (`extraction_confidence`, `coverage_posture`) — never fabricated.
- **Chinese remains an internal working/reference translation only — not official; Arabic remains
  governing.** The **Chinese LLM-ready full layer is not created yet** (`chinese_llm_ready_created
  = false`; `llm_ready_as_full_translation = false` for all 281). Next work is semantic review /
  expansion from the official Arabic before any Chinese LLM-ready layer.
- Artifacts: master inventory + article coverage index (1–281) under
  [`reports/chinese_translation_review/`](reports/chinese_translation_review/), per-Bab extracted
  sources under [`data/chinese_translation_sources/`](data/chinese_translation_sources/). Validate:
  `make chinese-all-babs-source-inventory-validate`.

### Chinese internal LLM-ready candidate layer (isolable-source articles, 189)

- A **Chinese internal LLM-ready candidate layer** now exists for the **189 articles that have
  isolable per-article Chinese source text** (`chinese_text` copied verbatim from the extracted
  Chinese source, SHA-256-checked; mechanical retrieval metadata only — no translation, no
  expansion, no correction, and nothing generated from Arabic/English).
- **92 articles are excluded** because no isolable per-article Chinese text exists (they are
  covered only within thematic-table summary groups) — no records are fabricated for them.
- **Chinese remains internal / reference only — not official and not governing; Arabic remains
  governing.** The **full Chinese 281 LLM-ready layer is not created yet**
  (`full_chinese_translation_claimed = false`; `llm_ready_as_full_translation = false` for all
  records). New layer: [`data/chinese_internal_legal_llm/`](data/chinese_internal_legal_llm/),
  schema
  [`schemas/chinese_internal_legal_llm.schema.json`](schemas/chinese_internal_legal_llm.schema.json).
  Build/validate: `make chinese-internal-legal-llm-isolable-data` /
  `make chinese-internal-legal-llm-isolable-validate`.

### Chinese internal candidate — semantic QA & completion gap plan

- A **semantic QA + completion gap plan** now exists for the Chinese internal candidate layer. The
  **189 candidate articles are reviewed** against the official Arabic for internal-reference
  suitability (conservative automated heuristic — needs human confirmation), and a **281-article
  gap plan** keeps the **92 excluded articles blocked** until Arabic-based expansion/retranslation.
- **Chinese is not official, not binding, not governing; Arabic remains governing.** No Chinese is
  generated or corrected here. The **full Chinese 281 layer is still not created** — P0 (the 92
  no-isolable-text articles) and P1 (materially-incomplete candidates) must be resolved from the
  Arabic governing text first.
- Artifacts under [`reports/chinese_translation_review/`](reports/chinese_translation_review/)
  (`chinese_internal_llm_semantic_qa_189.json`, `chinese_completion_gap_plan_001_281.json`,
  `CHINESE_INTERNAL_LLM_SEMANTIC_QA_AND_GAP_PLAN_AR.md`). Validate:
  `make chinese-internal-llm-semantic-qa-gap-plan-validate`.

### Chinese remediation backlog & source-packet plan

- A **remediation backlog + batch plan + source-packet manifest** now turns the QA/gap plan into an
  actionable roadmap: **P0 = 92, P1 = 76, P2 = 95, P3 = 18** (263 articles need remediation, 18
  retained as internal reference). Deterministic future batches (≤20 articles each, ordered
  P0→P1→P2 then a P3 confirmation batch) with per-batch source requirements.
- **No new Chinese text is generated in this stage** (`generated_chinese_created = false`;
  `corrected_chinese_created = false`). The **full Chinese 281 layer is still blocked**, and
  **trilingual alignment is blocked until P0/P1/P2 are resolved** from the official Arabic
  governing text. Chinese stays internal / non-official / non-binding; Arabic governs.
- Artifacts under [`reports/chinese_translation_review/`](reports/chinese_translation_review/)
  (`chinese_remediation_backlog_001_281.json`, `chinese_remediation_batch_plan.json`,
  `chinese_remediation_source_packet_manifest.json`,
  `CHINESE_REMEDIATION_BACKLOG_AND_SOURCE_PACKET_PLAN_AR.md`). Validate:
  `make chinese-remediation-backlog-source-packet-plan-validate`.

### Chinese remediation Batch P0-001 (20 Bab 4 articles)

- The **first remediation batch (P0-001)** now provides **new internal Chinese reference text for
  20 P0 articles from Bab 4** (61, 62, 63, 64, 65, 67, 68, 69, 70, 73, 74, 76, 78, 79, 80, 81, 82,
  83, 84, 85), created **from the official Arabic governing text** with **English used as
  secondary guidance only**.
- **Chinese remains internal / non-official / non-binding / non-governing; Arabic governs.**
  **Human legal review remains pending** (`human_legal_review_status = pending_human_legal_review`).
  This is **not** a full Chinese 281 layer and creates **no trilingual alignment**.
- Data under [`data/chinese_remediation_batches/p0_001/`](data/chinese_remediation_batches/p0_001/);
  report `reports/chinese_translation_review/CHINESE_REMEDIATION_BATCH_P0_001_AR.md`. Validate:
  `make chinese-remediation-batch-p0-001-validate`.

### Batch P0-001 QA (article-by-article vs Arabic)

- An **article-by-article QA** now reviews the **20 remediated Chinese internal reference
  articles** against the official Arabic governing text (English secondary): fidelity,
  completeness, terminology, authorities, conditions/exceptions, procedures, deadlines, numbers,
  quorum/voting, liability, and cross-references.
- **Human legal review remains pending** (`human_legal_review_completed = false`); the remediated
  Chinese is **not changed** here. Chinese remains internal / non-official / non-binding /
  non-governing; Arabic governs. **No full Chinese 281 layer and no trilingual alignment.**
- Artifacts:
  `reports/chinese_translation_review/chinese_remediation_batch_p0_001_qa.json` +
  `CHINESE_REMEDIATION_BATCH_P0_001_QA_AR.md`. Validate:
  `make chinese-remediation-batch-p0-001-qa-validate`.

### Batch P0-001 minor fixes (Articles 61 & 74)

- The **two QA-approved minor terminology fixes** have been applied to **Articles 61 and 74 only**
  (61: `المركز الرئيس` → `主要营业地`; 74: `محل الشركة التجاري` → `商号（商业名称）`) — legal meaning
  unchanged. **QA now reads 20 pass, 0 minor, 0 blocked, 0 failed.**
- **Human legal review remains pending**; Chinese stays internal / non-official / non-binding /
  non-governing; Arabic governs. **No full Chinese 281 layer and no trilingual alignment.**
- Artifacts:
  `reports/chinese_translation_review/chinese_remediation_batch_p0_001_minor_fixes.json` +
  `CHINESE_REMEDIATION_BATCH_P0_001_MINOR_FIXES_AR.md`. Validate:
  `make chinese-remediation-batch-p0-001-minor-fixes-validate`.

### Chinese remediation Batch P0-002 (20 Bab 4 articles)

- The **second remediation batch (P0-002)** provides **new internal Chinese reference text for
  20 more P0 articles from Bab 4** (86, 87, 88, 89, 91, 92, 93, 94, 95, 96, 97, 98, 100, 103, 104,
  105, 106, 107, 109, 110), created **from the official Arabic governing text** with **English used
  as secondary guidance only**. Authority terms follow the shared convention
  (`الوزارة` → Ministry / 商务部, `الهيئة` → CMA / 资本市场管理局, `الجهة المختصة` → competent
  authority / 主管机关).
- **Chinese remains internal / non-official / non-binding / non-governing; Arabic governs.**
  **Human legal review remains pending** (`human_legal_review_status = pending_human_legal_review`).
  This is **not** a full Chinese 281 layer and creates **no trilingual alignment**. Batch P0-001 is
  unchanged.
- Data under [`data/chinese_remediation_batches/p0_002/`](data/chinese_remediation_batches/p0_002/);
  report `reports/chinese_translation_review/CHINESE_REMEDIATION_BATCH_P0_002_AR.md`. Validate:
  `make chinese-remediation-batch-p0-002-validate`.

### Batch P0-002 QA (article-by-article vs Arabic)

- An **article-by-article QA** reviews the **20 P0-002 internal Chinese reference articles** against
  the official Arabic governing text (English secondary): legal-meaning preservation, terminology,
  entity/authority roles, obligations/rights, conditions/exceptions/deadlines, and scope boundaries.
- **Review only** — the P0-002 Chinese text and remediation data are **not changed**; **human legal
  review remains pending** (`human_legal_review_status = pending_human_legal_review`). Chinese stays
  internal / non-official / non-binding / non-governing; Arabic governs. **No full Chinese 281 layer
  and no trilingual alignment.**
- Artifacts:
  `reports/chinese_translation_review/chinese_remediation_batch_p0_002_qa.json` +
  `CHINESE_REMEDIATION_BATCH_P0_002_QA_AR.md`. Validate:
  `make chinese-remediation-batch-p0-002-qa-validate`.

### Chinese remediation Batch P0-003 (20 Bab 4 articles)

- The **third remediation batch (P0-003)** provides **new internal Chinese reference text for 20
  more P0 articles from Bab 4** (111, 112, 114, 116, 118, 119, 120, 121, 122, 123, 124, 125, 126,
  127, 128, 129, 130, 131, 134, 135), created **from the official Arabic governing text** with
  **English used as secondary guidance only**. Each record carries SHA-256 hashes for the Chinese,
  Arabic-source, and English-guidance text, and `qa_status = pending_future_qa`.
- **Chinese remains internal / non-official / non-binding / non-governing; Arabic governs.**
  **Human legal review remains pending** (`human_legal_review_status = pending_human_legal_review`).
  This is **not** a full Chinese 281 layer and creates **no trilingual alignment**. Batches P0-001
  and P0-002 (and their QA) are unchanged.
- Data under [`data/chinese_remediation_batches/p0_003/`](data/chinese_remediation_batches/p0_003/);
  report `reports/chinese_translation_review/CHINESE_REMEDIATION_BATCH_P0_003_AR.md`. Validate:
  `make chinese-remediation-batch-p0-003-validate`.

### Batch P0-003 QA (article-by-article vs Arabic)

- An **article-by-article QA** reviews the **20 P0-003 internal Chinese reference articles** against
  the official Arabic governing text (English secondary): legal-meaning preservation, terminology,
  entity/authority roles, obligations/rights, conditions/exceptions/deadlines, and scope boundaries.
- **Review only** — the P0-003 Chinese text and remediation data are **not changed**; **human legal
  review remains pending** (`human_legal_review_status = pending_human_legal_review`). Chinese stays
  internal / non-official / non-binding / non-governing; Arabic governs. **No full Chinese 281 layer
  and no trilingual alignment.**
- Artifacts:
  `reports/chinese_translation_review/chinese_remediation_batch_p0_003_qa.json` +
  `CHINESE_REMEDIATION_BATCH_P0_003_QA_AR.md`. Validate:
  `make chinese-remediation-batch-p0-003-qa-validate`.

### Chinese remediation Batch P0-004 (20 articles, Babs 4/5/6)

- The **fourth remediation batch (P0-004)** provides **new internal Chinese reference text for 20
  more P0 articles spanning Babs 4, 5 and 6** (136, 137, 140, 141, 143, 144, 147, 148, 159, 160,
  161, 163, 167, 168, 169, 171, 175, 177, 179, 180), created **from the official Arabic governing
  text** with **English used as secondary guidance only**. Each record's `bab` is verified against
  the official coverage index, carries SHA-256 hashes for the Chinese, Arabic-source, and
  English-guidance text, and `qa_status = pending_future_qa`.
- **Chinese remains internal / non-official / non-binding / non-governing; Arabic governs.**
  **Human legal review remains pending** (`human_legal_review_status = pending_human_legal_review`).
  This is **not** a full Chinese 281 layer and creates **no trilingual alignment**. Batches P0-001,
  P0-002, P0-003 (and their QA) are unchanged.
- Data under [`data/chinese_remediation_batches/p0_004/`](data/chinese_remediation_batches/p0_004/);
  report `reports/chinese_translation_review/CHINESE_REMEDIATION_BATCH_P0_004_AR.md`. Validate:
  `make chinese-remediation-batch-p0-004-validate`.

### Batch P0-004 QA (article-by-article vs Arabic; Babs 4/5/6)

- An **article-by-article QA** reviews the **20 P0-004 internal Chinese reference articles** (across
  Babs 4/5/6) against the official Arabic governing text (English secondary): legal-meaning
  preservation, terminology, entity/authority roles, obligations/rights,
  conditions/exceptions/deadlines, scope boundaries, and **Bab context** (Bab 4 joint-stock company,
  Bab 5 simplified joint-stock company, Bab 6 limited liability company). Each per-article `bab` is
  cross-checked against the P0-004 record and the coverage index.
- **Review only** — the P0-004 Chinese text and remediation data are **not changed**; **human legal
  review remains pending** (`human_legal_review_status = pending_human_legal_review`). Chinese stays
  internal / non-official / non-binding / non-governing; Arabic governs. **No full Chinese 281 layer
  and no trilingual alignment.**
- Artifacts:
  `reports/chinese_translation_review/chinese_remediation_batch_p0_004_qa.json` +
  `CHINESE_REMEDIATION_BATCH_P0_004_QA_AR.md`. Validate:
  `make chinese-remediation-batch-p0-004-qa-validate`.

### Chinese remediation Batch P0-005 (final P0 batch; 12 articles, Babs 7/9/10/13/14)

- The **fifth and final P0 remediation batch (P0-005)** provides **new internal Chinese reference
  text for 12 more P0 articles spanning Babs 7, 9, 10, 13 and 14** (188, 189, 190, 191, 192, 194,
  218, 220, 260, 261, 262, 274), created **from the official Arabic governing text** with **English
  used as secondary guidance only**. Each record's `bab` is verified against the official coverage
  index, carries SHA-256 hashes for the Chinese, Arabic-source, and English-guidance text, and
  `qa_status = pending_future_qa`.
- **Chinese remains internal / non-official / non-binding / non-governing; Arabic governs.**
  **Human legal review remains pending** (`human_legal_review_status = pending_human_legal_review`).
  This is **not** a full Chinese 281 layer and creates **no trilingual alignment**. Batches P0-001
  through P0-004 (and their QA) are unchanged, and **no P1/P2/P3 work is started**.
- Data under [`data/chinese_remediation_batches/p0_005/`](data/chinese_remediation_batches/p0_005/);
  report `reports/chinese_translation_review/CHINESE_REMEDIATION_BATCH_P0_005_AR.md`. Validate:
  `make chinese-remediation-batch-p0-005-validate`.

### Batch P0-005 QA (final P0 batch; article-by-article vs Arabic; Babs 7/9/10/13/14)

- An **article-by-article QA** reviews the **12 P0-005 internal Chinese reference articles** (across
  Babs 7/9/10/13/14) against the official Arabic governing text (English secondary): legal-meaning
  preservation, terminology, entity/authority roles, obligations/rights,
  conditions/exceptions/deadlines, scope boundaries, and **Bab context** (Bab 7 non-profit company,
  Bab 9 holding/subsidiary, Bab 10 company conversion, Bab 13 violations/penalties, Bab 14 final
  provisions). Each per-article `bab` is cross-checked against the P0-005 record and the coverage
  index. This is the QA for the **final P0 remediation batch**.
- **Review only** — the P0-005 Chinese text and remediation data are **not changed**; **human legal
  review remains pending** (`human_legal_review_status = pending_human_legal_review`). Chinese stays
  internal / non-official / non-binding / non-governing; Arabic governs. **No full Chinese 281 layer
  and no trilingual alignment; no P1/P2/P3 started.**
- Artifacts:
  `reports/chinese_translation_review/chinese_remediation_batch_p0_005_qa.json` +
  `CHINESE_REMEDIATION_BATCH_P0_005_QA_AR.md`. Validate:
  `make chinese-remediation-batch-p0-005-qa-validate`.

### Chinese remediation Batch P1-001 (first P1 batch; 20 articles, Babs 1/2; retranslation)

- The **first P1 batch** retranslates the internal Chinese reference for **20 articles across Babs 1
  and 2** (1, 2, 3, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 17, 18, 19, 20, 35, 38, 48) **from the official
  Arabic governing text** (English guidance only), because the prior internal Chinese candidate for
  these articles was **materially incomplete/condensed** (all 20 are priority **P1** in the semantic-QA
  report). Each record carries SHA-256 hashes for the Chinese, Arabic-source and English-guidance text,
  links to the (unchanged) prior candidate record and its P1 finding, and has `qa_status =
  pending_future_qa`.
- **Chinese remains internal / non-official / non-binding / non-governing; Arabic governs.**
  Repository-owner review is active (bachelor of law); **external legal review is optional** and not
  required for repository use. This is **not** a full Chinese 281 layer and creates **no trilingual
  alignment**. All P0 batches (and their QA) are unchanged; **P1-002 onward / P2 / P3 are not started**.
- Data under [`data/chinese_remediation_batches/p1_001/`](data/chinese_remediation_batches/p1_001/);
  report `reports/chinese_translation_review/CHINESE_REMEDIATION_BATCH_P1_001_AR.md`. Validate:
  `make chinese-remediation-batch-p1-001-validate`.
- **QA:** article-by-article review of all 20 retranslations against the official Arabic governing text
  (English secondary) → **PASS (20/20, no minor fixes)**; review only (P1-001 data unchanged).
  Artifacts: `reports/chinese_translation_review/chinese_remediation_batch_p1_001_qa.json` +
  `CHINESE_REMEDIATION_BATCH_P1_001_QA_AR.md`. Validate: `make chinese-remediation-batch-p1-001-qa-validate`.

### Chinese remediation Batch P1-002 (20 articles, Babs 3/4/5/6; retranslation)

- The next P1 batch retranslates the internal Chinese reference for **20 articles across Babs 3, 4, 5
  and 6** (54, 71, 72, 77, 90, 99, 101, 102, 108, 117, 132, 138, 145, 146, 149, 154, 156, 157, 164,
  165) **from the official Arabic governing text** (English guidance only), because the prior internal
  Chinese candidate was **materially incomplete/condensed** (all 20 are priority **P1** in the
  semantic-QA report). Each record carries SHA-256 hashes and links to the (unchanged) prior candidate
  record and its P1 finding. Chinese stays internal /
  non-official / non-binding / non-governing; Arabic governs. All P0 and P1-001 batches (and their QA)
  are unchanged; **P1-003 onward / P2 / P3 not started**.
- Data under [`data/chinese_remediation_batches/p1_002/`](data/chinese_remediation_batches/p1_002/);
  report `reports/chinese_translation_review/CHINESE_REMEDIATION_BATCH_P1_002_AR.md`. Validate:
  `make chinese-remediation-batch-p1-002-validate`.
- **QA:** article-by-article review of all 20 retranslations against the official Arabic governing text
  (English secondary) → **PASS (20/20, no minor fixes)**; review only (P1-002 data unchanged).
  Artifacts: `reports/chinese_translation_review/chinese_remediation_batch_p1_002_qa.json` +
  `CHINESE_REMEDIATION_BATCH_P1_002_QA_AR.md`. Validate: `make chinese-remediation-batch-p1-002-qa-validate`.

### Chinese remediation Batch P1-003 (20 articles, Babs 6/7/8/10; retranslation)

- The next P1 batch retranslates the internal Chinese reference for **20 articles across Babs 6, 7, 8
  and 10** (166, 170, 172, 174, 176, 178, 183, 185, 200, 201, 205, 206, 207, 211, 212, 213, 221, 222,
  225, 227) **from the official Arabic governing text** (English guidance only), because the prior
  internal Chinese candidate was **materially incomplete/condensed** (all 20 are priority **P1** in the
  semantic-QA report). Each record carries SHA-256 hashes and links to the (unchanged) prior candidate
  record and its P1 finding. Chinese stays internal /
  non-official / non-binding / non-governing; Arabic governs. All P0, P1-001 and P1-002 batches (and
  their QA) are unchanged; **P1-004 onward / P2 / P3 not started**.
- Data under [`data/chinese_remediation_batches/p1_003/`](data/chinese_remediation_batches/p1_003/);
  report `reports/chinese_translation_review/CHINESE_REMEDIATION_BATCH_P1_003_AR.md`. Validate:
  `make chinese-remediation-batch-p1-003-validate`.
- **QA:** article-by-article review of all 20 retranslations against the official Arabic governing text
  (English secondary) → **PASS (20/20, no minor fixes)**; review only (P1-003 data unchanged).
  Artifacts: `reports/chinese_translation_review/chinese_remediation_batch_p1_003_qa.json` +
  `CHINESE_REMEDIATION_BATCH_P1_003_QA_AR.md`. Validate: `make chinese-remediation-batch-p1-003-qa-validate`.

### Chinese remediation Batch P1-004 (16 articles, Babs 10/12/13/14; retranslation)

- The next P1 batch retranslates the internal Chinese reference for **16 articles across Babs 10, 12, 13
  and 14** (230, 233, 242, 244, 248, 252, 253, 255, 256, 264, 266, 267, 270, 271, 273, 277) **from the
  official Arabic governing text** (English guidance only), because the prior internal Chinese candidate
  was **materially incomplete/condensed** (all 16 are priority **P1** in the semantic-QA report). Each
  record carries SHA-256 hashes and links to the (unchanged) prior candidate record and its P1 finding.
  Chinese stays internal / non-official / non-binding /
  non-governing; Arabic governs. All P0, P1-001, P1-002 and P1-003 batches (and their QA) are unchanged;
  **P1-005 onward / P2 / P3 not started**.
- Data under [`data/chinese_remediation_batches/p1_004/`](data/chinese_remediation_batches/p1_004/);
  report `reports/chinese_translation_review/CHINESE_REMEDIATION_BATCH_P1_004_AR.md`. Validate:
  `make chinese-remediation-batch-p1-004-validate`.
- **QA:** article-by-article review of all 16 retranslations against the official Arabic governing text
  (English secondary) → **PASS (16/16, no minor fixes)**; review only (P1-004 data unchanged).
  Artifacts: `reports/chinese_translation_review/chinese_remediation_batch_p1_004_qa.json` +
  `CHINESE_REMEDIATION_BATCH_P1_004_QA_AR.md`. Validate: `make chinese-remediation-batch-p1-004-qa-validate`.
  This completes **all P1 batches (P1-001..P1-004): remediation + QA, each PASS with no minor fixes**.

### Chinese remediation Batch P2-001 (first P2 batch; 20 articles, Babs 1/2/4; expansion)

- The first P2 batch **expands** the internal Chinese reference for **20 articles across Babs 1, 2 and 4**
  (4, 10, 16, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 37, 58, 59) **from the official
  Arabic governing text** (English guidance only; existing candidate as the starting point), because the
  prior internal Chinese candidate for these articles **existed but was condensed** (all 20 are priority
  **P2** in the remediation backlog). Each record carries SHA-256 hashes and links to the (unchanged)
  prior candidate record and its P2 backlog finding. Chinese stays
  internal / non-official / non-binding / non-governing; Arabic governs. All P0 and all P1 batches (and
  their QA) are unchanged.
- Data under [`data/chinese_remediation_batches/p2_001/`](data/chinese_remediation_batches/p2_001/);
  report `reports/chinese_translation_review/CHINESE_REMEDIATION_BATCH_P2_001_AR.md`. Validate:
  `make chinese-remediation-batch-p2-001-validate`.
- **QA:** article-by-article review of all 20 expansions against the official Arabic governing text
  (English secondary; prior condensed candidate as the baseline) → **PASS (20/20, no minor fixes)**;
  expansion faithfulness, no hallucination / no omission / no over-expansion, clause-segment parity, and
  P2-backlog linkage confirmed; review only (P2-001 data unchanged). Artifacts:
  `reports/chinese_translation_review/chinese_remediation_batch_p2_001_qa.json` +
  `CHINESE_REMEDIATION_BATCH_P2_001_QA_AR.md`. Validate: `make chinese-remediation-batch-p2-001-qa-validate`.

### Chinese remediation Batch P2-002 (second P2 batch; 20 articles, Babs 4/5/6/7; expansion)

- The second P2 batch **expands** the internal Chinese reference for **20 articles across Babs 4, 5, 6
  and 7** (60, 66, 75, 113, 115, 133, 139, 142, 150, 151, 152, 153, 155, 158, 162, 173, 181, 182, 184,
  186) **from the official Arabic governing text** (English guidance only; existing candidate as the
  starting point), because the prior internal Chinese candidate for these articles **existed but was
  condensed** (all 20 are priority **P2** in the remediation backlog). Each record carries SHA-256 hashes
  and links to the (unchanged) prior candidate record and its P2 backlog finding; each expansion keeps
  the Arabic clause-segment count. Chinese stays internal / non-official / non-binding / non-governing;
  Arabic governs. All P0, all P1, and the P2-001 batches (and their QA) are unchanged.
- Data under [`data/chinese_remediation_batches/p2_002/`](data/chinese_remediation_batches/p2_002/);
  report `reports/chinese_translation_review/CHINESE_REMEDIATION_BATCH_P2_002_AR.md`. Validate:
  `make chinese-remediation-batch-p2-002-validate`.
- **QA:** article-by-article review of all 20 expansions against the official Arabic governing text
  (English secondary; prior condensed candidate as the baseline) → **PASS (20/20, no minor fixes)**;
  expansion faithfulness, no hallucination / no omission / no over-expansion, clause-segment parity, and
  P2-backlog linkage confirmed; review only (P2-002 data unchanged). Artifacts:
  `reports/chinese_translation_review/chinese_remediation_batch_p2_002_qa.json` +
  `CHINESE_REMEDIATION_BATCH_P2_002_QA_AR.md`. Validate: `make chinese-remediation-batch-p2-002-qa-validate`.

### Chinese remediation Batches P2-003, P2-004, P2-005 (remaining P2 expansion batches — P2 complete)

- The remaining P2 batches **expand** the internal Chinese reference from the official Arabic governing
  text (English guidance only; existing candidate as the starting point), because the prior internal
  Chinese candidates existed but were condensed (all are priority **P2** in the remediation backlog).
  Each expansion keeps the Arabic clause-segment count and links to the (unchanged) prior candidate and
  its P2 backlog finding.
  - **P2-003** — 20 articles across Babs 7, 8, 9 and 10 (non-profit, professional, holding, and company
    conversion/merger/division).
  - **P2-004** — 20 articles across Babs 10, 11 and 12 (merger/division, foreign companies, and
    termination/liquidation).
  - **P2-005** — 15 articles across Babs 12, 13 and 14 (liquidation, penalties, and final provisions).
- **QA (each batch):** article-by-article review against the official Arabic → **PASS** (P2-003 20/20,
  P2-004 20/20, P2-005 15/15; no minor fixes); expansion faithfulness, no hallucination / no omission /
  no over-expansion, clause-segment parity, terminology and P2-backlog linkage confirmed; review only
  (remediation data unchanged). Chinese stays internal / non-official / non-binding / non-governing;
  Arabic governs. This **completes the full P2 expansion track (P2-001..P2-005)**.
- Data under `data/chinese_remediation_batches/{p2_003,p2_004,p2_005}/`; reports + QA under
  `reports/chinese_translation_review/`. Validate: `make chinese-remediation-batch-p2-003-validate`
  (and `-qa-validate`), likewise for `p2-004` and `p2-005`.

### Chinese confirmation Batch P3-CONF-001 (final P3 confirmation batch — remediation program complete)

- P3 is a **confirmation / retain track, not expansion**: the existing internal Chinese candidate for
  these **18 articles across Babs 2 and 3** (general partnership and limited partnership) is already
  usable as internal reference (semantic alignment **high**, near-full completeness per the 189 semantic
  QA). This batch **confirms and retains each candidate verbatim** — **no new Chinese text is generated
  and nothing is modified**. Each record retains the candidate by hash (== the live 189 candidate == the
  backlog existing-candidate == the semantic-QA hash) and links to its semantic-QA finding and its P3
  backlog finding (`P3_retain_internal_reference`).
- **QA:** article-by-article review of the retain decisions → **PASS (18/18, no minor fixes)**; retain
  appropriateness, verbatim retention, semantic-alignment re-confirmation, and source/backlog
  traceability verified; review only (confirmation data and the Chinese candidate unchanged). Chinese
  stays internal / non-official / non-binding / non-governing; Arabic governs.
- This **completes the full Chinese remediation program (P0 → P1 → P2 → P3)**. No full Chinese 281 layer,
  trilingual alignment, or public release created.
- Data under `data/chinese_remediation_batches/p3_conf_001/`; reports + QA under
  `reports/chinese_translation_review/`. Validate: `make chinese-remediation-batch-p3-conf-001-validate`
  (and `-qa-validate`).

## Multilingual Saudi legal corpus for AI (foundation)

- This repository is a **multilingual, LLM-ready, official-source-based Saudi legal corpus** — a
  foundation for structuring Saudi laws and regulations into **auditable, machine-readable legal
  layers**. It is built to serve **government entities, AI companies and model builders, enterprises
  operating in or entering the Saudi market, investors, researchers, developers, and ordinary users**.
  The **Companies Law is the first implemented law profile**, not the whole project identity, and
  **Chinese is one language layer**, not the identity of the project. Investment guidance is one use
  case, not the sole purpose.
- **Foundation only** (no pipeline rewrite): the generic validators, report generator, RAG/API
  export, and cross-batch tooling are described as **future** components and are **not** implemented
  here.
- **Doctrine & architecture (Arabic):**
  [`docs/SOVEREIGN_LEGAL_CORPUS_FACTORY_DOCTRINE_AR.md`](docs/SOVEREIGN_LEGAL_CORPUS_FACTORY_DOCTRINE_AR.md)
  and
  [`docs/LEGAL_CORPUS_FACTORY_ARCHITECTURE_AR.md`](docs/LEGAL_CORPUS_FACTORY_ARCHITECTURE_AR.md)
  (data layers, profiles, validation, export/RAG readiness, multi-law onboarding, multi-language
  expansion, user groups).
- **Reusable schemas:** `schemas/legal_corpus_factory/{law_profile,batch_config,provenance_passport}.schema.json`.
  **Law profile:** `data/legal_corpus_factory/law_profiles/sa_companies_law_m132_1443.profile.json`
  (current facts only). **Example batch config:**
  `data/legal_corpus_factory/batch_configs/sa_companies_law_m132_1443_p0_005_qa.batch.json` (does not
  replace existing artifacts). **Terminology seed:**
  `data/legal_corpus_factory/terminology/sa_companies_law_core_terms_ar_en_zh_seed.json`
  (all entries `seed_repository_owner_review_active`).
- **Review model:** the **official Arabic source governs**; English and Chinese are reference layers.
  The **repository owner has a legal background (bachelor of law)** and runs **active repository
  legal review** (`repository_owner_review_active`). **External legal review is optional** for
  enterprise procurement or official adoption and is **not required for repository use**. This is
  **not an official government publication**, **no official translation is claimed**, Chinese is
  **not official/binding/governing**, there is **no full Chinese 281 layer and no trilingual
  alignment**, and this is **not legal advice**. Validate:
  `make legal-corpus-factory-foundation-validate`.

## Chinese Legal LLM-ready layer (repo book4 Sections 1–5)

The **Chinese Legal LLM-ready layer** currently covers **repo book4 Sections 1, 2, 3, 4 and 5 only**
— it is **not** full Chinese Legal LLM coverage. ("book4" is a **repo book4 convention** — an
internal repository label for the modeled Joint-Stock Company chapter/part scope, not a claim
about the whole Saudi Companies Law structure.)

- **Scope:** repo book4 (Joint-Stock Company modeled scope) — **23 `article_reference` records**
  across five sections:
  - **Section 1** (Establishment and Capital / 设立与资本), article groups **[58], [59], [60], [66]**
    — 4 records
    ([`data/chinese_legal_llm/book4_section1_zh_legal_llm.json`](data/chinese_legal_llm/book4_section1_zh_legal_llm.json)).
  - **Section 2** (Board of Directors and Governance / 董事会与治理), source-preserved provision groups
    **[67, 68], [71], [72], [75], [77]** — 5 records (the source groups Articles 67 & 68 into one
    provision, preserved exactly; no records for uncovered Articles 69, 70, 73, 74, 76, 78–83)
    ([`data/chinese_legal_llm/book4_section2_zh_legal_llm.json`](data/chinese_legal_llm/book4_section2_zh_legal_llm.json)).
  - **Section 3** (General Assemblies / 股东大会), source-preserved provision groups
    **[85, 87], [92, 93], [99], [101], [102]** — 5 records (the source groups Articles 85 & 87 and
    92 & 93 into one provision each, preserved exactly; no records for uncovered Articles 84, 86, 88,
    89, 90, 91, 94–98, 100 — Articles 84, 89 and 100 remain owner-reconciled excluded)
    ([`data/chinese_legal_llm/book4_section3_zh_legal_llm.json`](data/chinese_legal_llm/book4_section3_zh_legal_llm.json)).
  - **Section 4** (Shares, Debt Instruments and Sukuk / 股份、债务工具与融资凭证), provision groups
    **[108], [113], [115], [117]** — 4 records (no records for uncovered Articles 103–107, 109, 110,
    111, 112, 114, 116, 118–120 — Article 110 remains owner-reconciled excluded)
    ([`data/chinese_legal_llm/book4_section4_zh_legal_llm.json`](data/chinese_legal_llm/book4_section4_zh_legal_llm.json)).
  - **Section 5** (Finance, Profits, and Capital Changes / 财务、利润与资本变更), source-preserved
    provision groups **[123, 124], [126, 127], [128, 129, 130], [132], [133]** — 5 records (the source
    groups those articles into single provisions, preserved exactly; no records for uncovered Articles
    121, 122, 125, 131, 134, 135, 136, 137 — **Articles 134 and 135 remain excluded / cross-reference-only**)
    ([`data/chinese_legal_llm/book4_section5_zh_legal_llm.json`](data/chinese_legal_llm/book4_section5_zh_legal_llm.json)).
- **Source:** the **existing internal Chinese provision text** already in the repo — each record's
  **`legal_rule_text_zh` is copied verbatim** from the corresponding provision's `chinese_translation`
  field (Section 1 from [`data/articles/book4_provisions_058_066.json`](data/articles/book4_provisions_058_066.json),
  Section 2 from [`data/articles/book4_provisions_067_083.json`](data/articles/book4_provisions_067_083.json),
  Section 3 from [`data/articles/book4_provisions_084_102.json`](data/articles/book4_provisions_084_102.json),
  Section 4 from [`data/articles/book4_provisions_103_120.json`](data/articles/book4_provisions_103_120.json),
  Section 5 from [`data/articles/book4_provisions_121_137.json`](data/articles/book4_provisions_121_137.json)).
  There is **no new/machine translation**, **no model-generated summary**, and **no
  `legal_rule_summary_zh`** field (the schema's `additionalProperties:false` forbids it). `keywords_zh`
  reuses the provision's own approved `llm.keywords_zh`; the other derived metadata is kept conservative
  and traceable to that provision's own Chinese text.
- **Chinese is an internal working translation / LLM-ready metadata only; Arabic remains governing**
  (`source_trust.chinese_source_status = internal_working_translation`, `governing_text_language = ar`,
  `official_text_check = needs_check`, `manual_review_status = needs_manual_check`).
- **Not an official Chinese translation. Not legal advice. Not full Chinese Legal LLM coverage** — no
  Books 1–3 Chinese records yet (repo book4 Sections 1–5 are now complete for this layer).
- Schema `schemas/chinese_legal_llm.schema.json`; build `make chinese-legal-llm-book4-section1-data`,
  `make chinese-legal-llm-book4-section2-data`, `make chinese-legal-llm-book4-section3-data`,
  `make chinese-legal-llm-book4-section4-data` and `make chinese-legal-llm-book4-section5-data`;
  validate `make chinese-legal-llm-validate`.

## License

Source code: **MIT** ([`LICENSE`](LICENSE)). Legal content: see [`NOTICE.md`](NOTICE.md).
