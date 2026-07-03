# BOOK 4 — DATA-MODEL 1b DECISION (APPROVED)

**Status: Owner-approved. Infrastructure stage. Book Four full content generation has NOT started.**

## Decision

The owner **approved data-model 1b** for Book Four (شركة المساهمة / 股份公司, JSC), Articles 58–137.

Model 1b means:

1. **Thematic / provisions dataset for explicitly covered provisions only.** Canonical provision
   records are created **solely** for provisions that are explicitly rendered in the source PDF
   (`inputs/bab4_source.pdf`). A provision record may map to **one or more** article numbers,
   because the source is thematic, not article-by-article (see `book4_provision.schema.json`).
2. **Coverage matrix over all 80 articles (58–137).** Every article number 58–137 appears in
   `data/coverage/book4_coverage_matrix.json`, whether or not it is covered by the source.
3. **Uncovered articles are marked `needs_official_text_check`** (via
   `official_text_check: "needs_official_text_check"` and
   `content_record_status: "no_record_until_source_available"`).
4. **No invented content for uncovered articles.** Uncovered articles receive **no** legal
   provision text and **no** invented titles (titles are `null` unless explicit in the source).
5. **Future Book Four PRs remain section-split** (Option B): one PR per thematic section
   (58–66 / 67–83 / 84–102 / 103–120 / 121–137), plus a finalization PR.

## Why (source shape)

The source is a **thematic / tabular summary of core provisions** (أهم الأحكام / 核心条款), **not**
a complete per-article translation. Its own disclaimer states it is a selective summary, and the
review log lists articles whose details are omitted (e.g. **100, 111, 116, 134–137**). Only ~33 of
the 80 articles have explicit content. A Books-1–3-style per-article dataset for all 80 would
require inventing rules for ~47 articles, which is prohibited by the project's core principle
("Do not invent legal rules … mark `NEEDS_OFFICIAL_TEXT_CHECK` instead of guessing").

## Explicitly-covered provisions (from preflight inspection)

Articles with explicit content in the PDF (≈33): 58, 59, 60, 66, 67, 68, 71, 72, 75, 77, 84, 85,
87, 89, 92, 93, 99, 101, 102, 108, 110, 113, 115, 117, 123, 124, 126, 127, 128, 129, 130, 132,
133. (Articles 134–135 are only *referenced*, not rendered, so they are treated as
`not_explicit_in_source`.) The precise mapping lives in
`data/coverage/book4_coverage_matrix.json` and is authoritative.

## Trust posture (unchanged)

- `translation_mode = internally_reviewed_summary`
- `source.official_text_check = needs_check` for provision records; uncovered articles carry
  `needs_official_text_check` in the coverage matrix.
- Never `verified` / `محققة` / `经核验`.
- Book-specific disclaimer (第四编 / الباب الرابع, 58–137). Not an official translation, not legal
  advice. Listing / CMA matters read with the Capital Market Law.

## What this infrastructure PR does / does not do

- **Does:** register Book Four (`books.py`, `mode="model_1b_thematic_provisions"`), add this
  decision doc, the coverage matrix over all 80 articles, the provision schema, Book Four
  validation (`make book4-validate`), and tests.
- **Does NOT:** create `data/articles/book4_provisions_*.json` / `*.jsonl`, create Book Four
  content Markdown with legal text, render `dist/book4.*`, or invent any article content.
