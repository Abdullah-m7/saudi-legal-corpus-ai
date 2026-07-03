# English source scope

Observations from the extracted text layer of
`inputs/companies_law_official_english_guidance.pdf` (89 pages, born-digital,
extracted with `pypdf`). These are factual observations from the source, not
guesses; where the source is unclear this document says `NEEDS_MANUAL_CHECK`.

## Does the PDF cover the full Companies Law or only part of it?

**Full Companies Law.** The document contains all 14 Parts of the Law:

| Part | Heading (English) | Corresponds to |
|------|-------------------|----------------|
| Part 1 | General Provisions | Book One (Arabic الباب الأول) |
| Part 2 | General Partnerships | Book Two (شركة التضامن) |
| Part 3 | Limited Partnership | Book Three (شركة التوصية البسيطة) |
| Part 4 | Joint-Stock Company | Book Four (شركة المساهمة) |
| Part 5 | Simplified Joint-Stock Company | — |
| Part 6 | Limited Liability Company | — |
| Part 7 | Non-Profit Company | — |
| Part 8 | Professional Company | — |
| Part 9 | Holding Company and Subsidiary Company | — |
| Part 10 | Conversion, Merger, and Division of Companies | — |
| Part 11 | Foreign Companies | — |
| Part 12 | Company Termination and Liquidation | — |
| Part 13 | Penalties | — |
| Part 14 | Concluding Provisions | — |

> Note: the English uses **"Part N"** where the repository's Arabic corpus uses
> **"Book" / الباب**. They denote the same top-level divisions.

## First article number visible

**Article 1** — "Definitions" (Part 1, Preliminary Chapter).

## Last article number visible

**Article 281** — "Entry into Force" (Part 14, Concluding Provisions).

## Article count / gaps

- Distinct `Article N:` headings found: **281**.
- Range: **1 – 281**, **no gaps** in `1..281`.

## Whether Books One–Three are covered

**Yes.** Articles **1–57** are present:
- Part 1 / Book One: Articles 1–34.
- Part 2 / Book Two: Articles 35–50.
- Part 3 / Book Three: Articles 51–57.

## Whether Book Four Articles 58–137 are covered

**Yes.** Part 4 (Joint-Stock Company) begins at **Article 58** and Part 5
(Simplified Joint-Stock Company) begins at **Article 138**, so Book Four's
**Articles 58–137** are fully covered.

## Does English article numbering align cleanly with Arabic article numbers?

**Appears to align cleanly (provisional).** Spot checks of article headings match
the Arabic canonical subjects one-to-one by number:

| Art | English heading | Arabic canonical subject |
|-----|-----------------|--------------------------|
| 1 | Definitions | التعريفات |
| 2 | Definition of a Company | تعريف الشركة |
| 3 | Nationality of a Company | جنسية الشركة |
| 34 | Enforcement against Interests and Shares | التنفيذ على الحصص والأسهم |
| 35 | Definition of a General Partnership | تعريف شركة التضامن |
| 50 | Cases of Termination | انتهاء شركة التضامن |
| 51 | Definition of a Limited Partnership | تعريف شركة التوصية البسيطة |
| 57 | Cases of Termination | حالات الانتهاء |
| 58 | Definition of a Joint-Stock Company | تعريف شركة المساهمة |
| 60 | Issued and Authorized Capital | رأس المال المصدر والمصرح به |
| 66 | Valuation of In-Kind Contributions | تقييم الحصص العينية |

Full per-article alignment verification across all 281 articles is **deferred** to
the future English alignment layer and is `NEEDS_MANUAL_CHECK` at that stage. This
PR does not assert exact alignment as verified.

## Missing pages, OCR issues, malformed extraction, ambiguous headings

- **Missing pages:** none observed; page numbering runs 1–89 continuously.
- **OCR issues:** none — the PDF is born-digital text (no OCR involved).
- **Malformed extraction:** minor cosmetic whitespace artifacts in the text layer
  (e.g. "Competent Au thority", "inco rporated", "joint -stock"). Content is intact;
  spacing must be normalized before any English-layer authoring.
- **Ambiguous headings:** the English "Part" vs the Arabic "Book/الباب" wording is
  a labeling difference, not a content mismatch. No ambiguous article headings were
  observed in the covered range. Anything unverified at authoring time →
  `NEEDS_MANUAL_CHECK`.
