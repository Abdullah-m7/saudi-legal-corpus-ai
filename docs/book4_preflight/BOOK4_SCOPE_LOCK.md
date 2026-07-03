# BOOK 4 — SCOPE LOCK / قفل النطاق

> **Book Four content generation NOT started.** This document only locks scope from the attached
> source PDF. Article range and counts are taken from the PDF, not from memory.

## Titles

- **Arabic book title:** الباب الرابع: شركة المساهمة — أهم الأحكام
- **Chinese book title:** 第四编：股份公司（JSC）— 核心条款
- **Company form:** شركة المساهمة / 股份公司 (Joint-Stock Company, JSC)

## Article range (from the PDF)

| Field | Value |
|-------|-------|
| First article number | **58** |
| Last article number | **137** |
| Count of articles (inclusive) | **80** (137 − 58 + 1) |
| Range label (AR) | المواد 58–137 |
| Range label (ZH) | 第五十八条 至 第一百三十七条 |

The PDF cover states `第五十八条 至 第一百三十七条` and the disclaimer states `第四编共八十条`
(this Book has 80 articles). No conflict between the PDF and the expected JSC scope.

## Section / chapter breakdown (as presented thematically in the PDF)

The PDF groups the 80 articles into **five thematic sections** (专题):

| # | Arabic | Chinese | Articles (as labelled in PDF) |
|---|--------|---------|-------------------------------|
| 1 | التأسيس ورأس المال | 设立与资本 | 58–66 |
| 2 | مجلس الإدارة والحوكمة | 董事会与治理 | 67–83 |
| 3 | الجمعية العامة: النصاب والأغلبية | 股东大会：法定人数与多数决 | 84–102 |
| 4 | الأسهم وأدوات الدين والصكوك | 股份、债务工具与融资凭证 | 103–120 |
| 5 | المالية والأرباح وتغيير رأس المال | 财务、利润与资本变更 | 121–137 |

## Source

- **PDF source path:** `inputs/bab4_source.pdf` (12 pages, committed with this preflight PR).
- **Extraction:** Chinese layer extracts cleanly; Arabic layer extracts garbled (as in Books
  1–3) and will require manual MSA reconstruction at the content stage.
- **Instrument:** المرسوم الملكي رقم (م/132) وتاريخ 1443/12/1هـ (same as Books 1–3).

## ⚠️ CRITICAL SOURCE-SHAPE FINDING (drives the data model)

The attached PDF is a **thematic / tabular summary of "core provisions" (أهم الأحكام / 核心条款)**,
**NOT** a per-article translation of all 80 articles. Its own disclaimer says
「以专题表格择要呈现，并非逐条全文翻译」 and the review log states several articles' details are
deliberately omitted (**explicitly named: 100, 111, 116, 134–137**, and by inspection many others
in 61–65, 69–70, 73–74, 76, 78–83, 86, 88, 90–91, 94–98, 103–107, 109, 112, 114, 118–122, 125,
131 are not individually rendered).

**Articles with explicit content in the PDF (≈33):** 58, 59, 60, 66, 67, 68, 71, 72, 75, 77, 84,
85, 87, 89, 92, 93, 99, 101, 102, 108, 110, 113, 115, 117, 123, 124, 126, 127, 128, 129, 130,
132, 133 (with 134–135 referenced). The remaining ~47 of the 80 articles are **not** covered
article-by-article in this source.

**Consequence:** a Books-1–3-style per-article canonical dataset for all 80 articles cannot be
produced from this source **without inventing legal rules** for the uncovered articles — which is
prohibited. See the open questions and the implementation plan.

## Open questions (require owner decision before content generation)

1. **Data model (blocking).** Which approach for the ~47 uncovered articles?
   - **(1a)** Per-article dataset for all 80, with uncovered articles carrying a minimal stub and
     `coverage_status: "needs_official_text_check"` + `NEEDS_OFFICIAL_TEXT_CHECK` (honest, but many
     near-empty records); **or**
   - **(1b)** A **thematic/provisions** dataset keyed to the articles actually covered (≈33),
     each tagged with its article number(s) and section — matching the source's real shape — with
     a coverage matrix that lists all 80 and marks uncovered ones `needs_official_text_check`.
   - **Preflight recommendation:** **1b** (model the data to the source that exists; do not
     manufacture 47 hollow article records). Confirm with owner.
2. **Coverage-matrix semantics.** Should the coverage matrix enumerate all 80 article numbers
   (with `covered` / `needs_official_text_check`) even under model 1b? (Recommended: yes.)
3. **Capital Market Law dependency.** Listing / CMA-governed items (e.g. Arts. 113, 117) reference
   the Capital Market Law. Do we add a `related_instruments` field, or keep it in `legal_notes`?
4. **Share-class depth.** How much of the 种类/类别 (type vs class) machinery (Arts. 108, 110, 89)
   to encode as structured `terminology` vs prose.

## Confirmation

- ✅ Article range locked: **58–137 (80 articles)** from the PDF.
- ✅ Five thematic sections identified.
- ✅ Source is a thematic summary, not per-article — flagged as the key data-model driver.
- 🚫 **Book Four content generation NOT started.**
