# BOOK 4 — QA PLAN / خطة ضبط الجودة

Planned `qa_rules.run_all_book4(articles, work, glossary, doc)` — to be implemented at the content
stage, mirroring `run_all_book2` / `run_all_book3`. Every rule returns a list of problem strings
(empty == pass). Rule IDs are `b4_*`.

## Structural / trust (baseline, same as Books 2–3)

| ID | Rule | Detail |
|----|------|--------|
| b4_1 | Article range | Exactly the locked range **58–137** (or the covered-subset set if data-model 1b is chosen — see scope lock); assert against a single source of truth, not a hardcoded literal duplicated per file |
| b4_2 | No duplicate article numbers | |
| b4_3 | Bilingual present | Arabic summary + Chinese translation + both titles non-empty for every record |
| b4_4 | `book == 4` for all records | |
| b4_5 | Trust posture | `translation_mode == "internally_reviewed_summary"` **and** `source.official_text_check == "needs_check"` for every record |
| b4_6 | No overclaim | none of `verified_summary` / `verified` / `محققة` / `经核验` appears in any article field |
| b4_7 | `source.input_pdf == "inputs/bab4_source.pdf"` | |
| b4_8 | Chunk IDs | `sa-companies-book4-art{NNN}` well-formed |

## Disclaimer scope (post-hotfix invariant)

| ID | Rule | Detail |
|----|------|--------|
| b4_9 | Book Four disclaimer scope | Registry `disclaimer_ar` contains `الباب الرابع` + `58–137`; `disclaimer_zh` contains `第四编` + `第五十八条`/`第一百三十七条` |
| b4_10 | No cross-book scope leak | Book Four disclaimer must **not** contain Book One/Two/Three scope (`الباب الأول/الثاني/الثالث`, `第一编/第二编/第三编`, `1–34`/`35–50`/`51–57`) — in Markdown **and** rendered HTML |

## Company-form & governance terminology

| ID | Rule | Detail |
|----|------|--------|
| b4_11 | Company form | glossary `شركة المساهمة` → contains `股份公司`; keep JSC caveat (not identical to PRC 股份有限公司) |
| b4_12 | Listed vs non-listed | `شركة المساهمة المدرجة` → `上市股份公司`; `غير المدرجة` → `非上市股份公司`; both present and distinct |
| b4_13 | Board terminology | `مجلس الإدارة` → `董事会`; `عضو مجلس الإدارة` → `董事会成员（董事）`; `رئيس مجلس الإدارة` → `董事会主席` present & consistent |
| b4_14 | Shareholder vs partner | `المساهم` → `股东` (never `合伙人`); assert `合伙人` not used for JSC shareholders in article bodies |

## Assemblies (high-risk distinctions)

| ID | Rule | Detail |
|----|------|--------|
| b4_15 | OGM vs EGM distinguished | `الجمعية العامة العادية` → `普通股东大会`(OGM); `غير العادية` → `非常股东大会`/`特别股东大会`(EGM); both present, not conflated |
| b4_16 | Class meeting | `الجمعية الخاصة` → `类别股东专门大会` present where share-class changes are discussed |
| b4_17 | Quorum/majority basis | where majorities appear, the "所代表的表决权 / votes represented at the meeting" basis is stated (not total capital) |

## Shares, capital, financing

| ID | Rule | Detail |
|----|------|--------|
| b4_18 | Share types distinguished | ordinary `普通股` / preferred `优先股` / redeemable `可赎回股(份)` all present and distinct |
| b4_19 | type vs class | `种类` (type) vs `类别` (class) both used and not merged |
| b4_20 | Capital layers | `已发行资本` (issued) / `授权资本` (authorized) / `实缴资本` (paid-up) distinct |
| b4_21 | Capital increase/decrease | `增资` and `减资` present with correct organ (EGM) and pre-conditions; not swapped |
| b4_22 | Pre-emption term integrity | Book Four uses `优先认购权` (subscription); must NOT be rendered as Book One `优先购买权` or `赎回权` |
| b4_23 | Drag/Tag | `拖售权` (drag-along) and `随售权` (tag-along) present where Art. 113 is covered, with the 90% + good-faith + Capital-Market-Law caveats |

## Distributions & conflicts

| ID | Rule | Detail |
|----|------|--------|
| b4_24 | Dividends/distribution | `利润分配`/`分红` terminology consistent; unlawful-distribution recovery preserved if in source |
| b4_25 | Conflicts of interest | `利益冲突`: disclose + abstain from vote + minute captured where covered (Art. 71) |
| b4_26 | Loans-to-directors ban | prohibition + relatives definition + bank/finance exception captured where covered (Art. 72) |

## Rendering hygiene (shared infra, already enforced for Books 1–3)

| ID | Rule | Detail |
|----|------|--------|
| b4_27 | No raw Markdown artifacts | rendered notes / review-log sections contain no raw `**`, backticks, `\| # \|`, `\|---`, `<p>&gt;` |
| b4_28 | HTML disclaimer correct | rendered `dist/book4.html` uses the Book Four disclaimer (reuse of the hotfix mechanism) |

## Coverage-matrix rule (data-model dependent)

| ID | Rule | Detail |
|----|------|--------|
| b4_29 | Coverage enumerates 58–137 | coverage matrix lists **all 80** article numbers; uncovered ones marked `needs_official_text_check`; no silent gaps |

## Notes

- Reuse the existing shared validators/schema (already generalized: `book >= 1`,
  `article_number <= 200`, `chunk_id book[0-9]+`, coverage `minItems: 1`). No schema change is
  expected for Book Four.
- `make book4-validate` will call `validate_book(4)`; add the dispatch branch alongside book 2/3.
