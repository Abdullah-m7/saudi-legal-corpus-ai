# Book Four — Section 4 scope decision / قرار نطاق القسم الرابع

> **Status: NEEDS OWNER SCOPE DECISION.** No Section-4 provision records, content, or
> coverage changes were generated in this PR. This documents a blocking inconsistency
> between two source-of-truth files (the coverage matrix and the source PDF) on **one
> article (110)** so the owner can fix the explicit-article set before any content is
> authored. **No content was invented.**

## Section resolved (unambiguous)

The **next thematic section after Section 3** is unambiguous from the preflight docs
(`docs/book4_preflight/BOOK4_SCOPE_LOCK.md`, `BOOK4_IMPLEMENTATION_PLAN.md`):

| Field | Value |
|-------|-------|
| Section number | **4** (of 5) |
| Arabic title | **الأسهم وأدوات الدين والصكوك** |
| Chinese title | **股份、债务工具与融资凭证** |
| English working title | *Shares, Debt Instruments and Sukuk* (planning-doc gloss) |
| `thematic_section` key (proposed) | `shares_debt_instruments_sukuk` |
| Article range | **103–120** (18 articles) |

The source PDF's own section header renders this exactly:
`四、股份、债务工具与融资凭证（第103–120条）`.

## The blocking ambiguity (the explicit-article set for 103–120)

Two repo source-of-truth files disagree on which Section-4 articles are *explicitly
covered in the source* — on **exactly one article, 110**:

| Source of truth | Section-4 explicit articles (103–120) |
|-----------------|----------------------------------------|
| `data/coverage/book4_coverage_matrix.json` (`explicit_in_source`) | 108, **110**, 113, 115, 117 |
| `inputs/bab4_source.pdf` (distinctly rendered thematic content) | 108, 113, 115, 117 |

**Article 110 is listed as `explicit_in_source` in the coverage matrix but is NOT
distinctly rendered as its own provision in the source PDF.** In the source, 110
appears **only** in analytical commentary, twice, both as the cross-reference
`（第110、89条）` attached to **Article 108's** "种类 / 类别" (types/classes) rule:

- *"变更某一类别的权利，除 EGM 外还须该类别持有人**专门大会**批准（第110、89条）"*
- *"漏掉种类/类别 这一保护类别股东的核心区分（第110、89条）。已在表格与注释2中补正。"*

There is **no** `违约…(110)` / `种类…(110)` rule block, and **no** `第110条` rule text —
110 is cited as an article number alongside 89, with the substantive rule presented
under Article 108. Per the official English guidance, **Article 110 = "Amendment of
Share-Associated Rights and Obligations"**, i.e. the class-rights amendment machinery
that the source folds into the Article-108 discussion.

**This is the same pattern the owner already reconciled for Section 3:** Article 89
("Amending the Rights of Shareholder Classes") was reclassified from `explicit_in_source`
to `not_explicit_in_source` because the source renders no distinct block for it (see
`BOOK4_SECTION3_SCOPE_DECISION.md`). Article 110 is the Section-4 twin of that same
class-rights topic and is cited **together with 89** in the source commentary.

Authoring a provision for 110 from this source would require **inventing legal content**,
which is prohibited by the project's core rule and the Book Four model-1b guardrails.

## What the source PDF actually renders for Section 4 (thematic blocks)

Extracted from `inputs/bab4_source.pdf` (Chinese layer is clean; Arabic garbled, as
noted in `BOOK4_SCOPE_LOCK.md`). Each block below carries its own `标题 (NNN)：规则` tag:

| Source thematic block | Article tag | Official English heading |
|-----------------------|-------------|--------------------------|
| 股份的种类与类别 (types & classes of shares) | (108) | 108 Types and Classes of Shares |
| 强制出售：拖售权与随售权 (drag-along / tag-along) | (113) | 113 Drag-along and Tag-along Rights |
| 违约未缴款 (non-payment / default on calls) | (115) | 115 Non-Payment |
| 融资凭证与债务工具 (Sukuk & debt instruments) | (117) | 117 Issuance of Debt Instruments and Financing Sukuk |

All four render as single-article blocks (no multi-article grouping in this section),
and all four are `explicit_in_source` in the coverage matrix — **no conflict** on these.

The remaining articles in 103–120 (103, 104, 105, 106, 107, 109, 111, 112, 114, 116,
118, 119, 120) are `not_explicit_in_source` in the matrix **and** are not rendered as
distinct provisions in the PDF — **they agree** (111 and 116 are among the articles the
source's own disclaimer names as deliberately omitted).

## Official English headings 103–120 (for reference only)

Governing text is Arabic; the English below is the official *guidance* translation,
included only to characterise the discrepancy — it is **NOT** used as the basis for any
Arabic/Chinese provision content.

```
103 Company Shares                         112 Shareholder Register
104 Effect of Share Subscription           113 Drag-along and Tag-along Rights
105 Issuance of Company Shares             114 Purchase and Pledge of Shares
106 Nominal Value of Shares                115 Non-Payment
107 Share-Associated Rights                116 Demanding Payment in Excess of Obligations
108 Types and Classes of Shares            117 Issuance of Debt Instruments and Financing Sukuk
109 Conversion of Shares                   118 Conversion of Debt Instruments and Financing Sukuk
110 Amendment of Share-Associated          119 Compensation for Damage
    Rights and Obligations                 120 Applicability of Shareholder Assembly Decisions
111 Restrictions on Trading of Shares
```

## Options for the owner (decision required before content)

1. **(Recommended) Reconcile to the source.** Treat the Section-4 explicit set as the
   articles the source actually renders — **{108, 113, 115, 117}** — and reclassify
   **110** in the coverage matrix from `explicit_in_source` to `not_explicit_in_source`
   (→ `official_text_check = needs_official_text_check`,
   `content_record_status = no_record_until_source_available`), exactly as was done for
   Article 89 in Section 3. A follow-up content PR would then create **four** single-article
   provisions ([108], [113], [115], [117]) for the reconciled set only.
2. **Supply official text for 110.** If the owner has the official Arabic for Article 110
   ("Amendment of Share-Associated Rights and Obligations") as a distinct provision,
   provide it so a faithful provision can be authored; the coverage matrix stays as-is
   (explicit set {108, 110, 113, 115, 117}).
3. **Defer Section 4.** Keep the coverage matrix unchanged and postpone Section-4 content
   until the above is resolved.

This PR takes **none** of these actions — it only documents the decision. Changing the
coverage matrix's `explicit_in_source` list is owner-approved infrastructure and is out
of scope here.

## Guardrails honoured in this PR

- No provision records created (`data/articles/book4_provisions_103_120.json` does NOT exist).
- No Section-4 content (`content/*/book4_section4.md`) created.
- No coverage-matrix changes (still 80 rows; Section-4 explicit list unchanged, incl. 110).
- No `data/articles/book4_articles_*.json`; no full Book Four content/build.
- Sections 1, 2, 3 provisions, the Arabic Legal LLM layer, and the English reference layer
  are unchanged.
- No invented content for any article. Not an official translation; not legal advice.
