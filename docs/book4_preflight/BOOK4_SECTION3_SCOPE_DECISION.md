# Book Four — Section 3 scope decision (BLOCKING) / قرار نطاق القسم الثالث

> **Status: NEEDS OWNER SCOPE DECISION.** No Section-3 provision records, content, or
> coverage changes are generated in this PR. This document records a blocking
> inconsistency between two source-of-truth files so the owner can decide the
> explicit-article set before any content is authored. **No content was invented.**

## Section resolved (unambiguous)

- **Next section after Section 2:** Section 3 — الجمعية العامة / 股东大会
  (`thematic_section = general_assemblies`), from
  `docs/book4_preflight/BOOK4_IMPLEMENTATION_PLAN.md` (PR 4.4) and
  `docs/book4_preflight/BOOK4_SCOPE_LOCK.md`.
- **Arabic title:** الجمعية العامة (النصاب والأغلبية)
- **Chinese title:** 股东大会（法定人数与多数决）
- **Article range:** **84–102** (19 articles).

## The blocking ambiguity (the explicit-article set)

Two repo source-of-truth files disagree on which Section-3 articles are *explicitly
covered in the source*:

| Source of truth | Section-3 explicit articles |
|-----------------|-----------------------------|
| `data/coverage/book4_coverage_matrix.json` (`explicit_in_source`) | 84, 85, 87, **89**, 92, 93, 99, 101, 102 |
| `inputs/bab4_source.pdf` (actually rendered thematic content) | 85, 87, 92, 93, 99, 101, 102 |

**Articles 84 and 89 are listed as `explicit_in_source` in the coverage matrix but
are NOT distinctly rendered in the source PDF:**

- **Article 89** (per official English: *"Amending the Rights of Shareholder
  Classes"*): the Section-3 text of `inputs/bab4_source.pdf` contains **zero**
  occurrences of `89` and **no** class-rights / special-assembly (类别 / 专门 / 特别股东)
  content. It appears to be a preflight over-listing.
- **Article 84** (per official English: *"Shareholder General Assembly Meetings"*):
  the source's powers block is tagged **`(85、87)`**, not `(84)`; `84` appears only in
  the section-range header `（第84–102条）`. No distinct Article-84 provision is
  rendered.

Authoring provisions for 84 and 89 from this source would require **inventing legal
content**, which is prohibited by the project's core rule and the Book Four model-1b
guardrails.

## What the source PDF actually renders (thematic blocks)

Extracted (Chinese layer is clean; Arabic garbled, as noted in `BOOK4_SCOPE_LOCK.md`):

| Source thematic block | Article tag(s) in source | Official English heading(s) |
|-----------------------|--------------------------|-----------------------------|
| 职权 (powers): OGM vs EGM | (85、87) | 85 Powers of the EGM · 87 Powers of the OGM |
| 法定人数 (quorum) | (92、93) | 92 Quorum of OGM · 93 Quorum of EGM |
| 表决多数 (voting majorities) | (92/3、93/4) | within 92 / 93 |
| 决议撤销 (annulment of decisions) | (99) | 99 Objection to Assembly Decisions |
| 传阅决议 (decision by circulation) | (101) | 100 Issuing by Circulation · 101 Quorum for Circulation |
| 公司检查 (inspection, 5%) | (102) | 102 Request for Inspection |

A secondary numbering question: the source tags the circulation provision **(101)**,
but the official numbering splits circulation across **100** ("Issuing a Decision by
Circulation") and **101** ("Quorum for Issuance of a Decision by Circulation").

## Official English headings 84–102 (for reference only)

Governing text is Arabic; the English below is the official *guidance* translation
and is included only to characterise the discrepancy — it is NOT used as the basis
for any Arabic/Chinese provision content.

```
84 Shareholder General Assembly Meetings          94 Effectiveness of General Assembly Decisions
85 Powers of the Extraordinary General Assembly   95 Voting in Shareholder Assemblies
86 Decisions of OGM Issued by EGM                 96 Agenda of General Assembly
87 Powers of the Ordinary General Assembly        97 Assembly Meeting Minutes
88 Ordinary General Assembly Meetings             98 Single-Person Joint-Stock Company
89 Amending the Rights of Shareholder Classes     99 Objection to Shareholder Assembly Decisions
90 General and Special Assemblies                 100 Issuing a Decision by Circulation
91 Call for Assembly Meetings                     101 Quorum for Issuance of a Decision by Circulation
92 Quorum of OGM Meetings                         102 Request for Inspection of the Company
93 Quorum of EGM Meetings
```

## Options for the owner (decision required before content)

1. **(Recommended) Reconcile to the source.** Treat the Section-3 explicit set as the
   articles the source actually renders — **{85, 87, 92, 93, 99, 101, 102}** — and
   reclassify **84** and **89** in the coverage matrix from `explicit_in_source` to
   `not_explicit_in_source` (→ `needs_official_text_check` / `no_record_until_source_available`).
   Also decide whether the circulation provision maps to **101** only or **{100, 101}**.
   A follow-up content PR would then create provisions for the reconciled set only.
2. **Supply official text for 84 & 89.** If the owner has the official Arabic for
   Articles 84 and 89, provide it so faithful provisions can be authored; the coverage
   matrix stays as-is.
3. **Defer Section 3.** Keep the coverage matrix unchanged and postpone Section-3
   content until the above is resolved.

This PR takes **none** of these actions — it only documents the decision. Changing the
coverage matrix's `explicit_in_source` list is owner-approved infrastructure and is out
of scope here.

## Guardrails honoured in this PR

- No provision records created (`data/articles/book4_provisions_084_102.json` does NOT exist).
- No Section-3 content (`content/*/book4_section3.md`) created.
- No coverage-matrix changes (still 80 rows; Section-3 explicit list unchanged).
- No `data/articles/book4_articles_*.json`; no full Book Four content/build.
- No invented content for any article. Not an official translation; not legal advice.
