# BOOK 4 — REVIEW RISKS / مخاطر المراجعة

Top risks for Book Four (شركة المساهمة / 股份公司). Each has a mitigation that maps to a planned QA
rule (see `BOOK4_QA_PLAN.md`).

| # | Risk | Why it matters | Mitigation / QA rule |
|---|------|----------------|----------------------|
| 1 | **Over-literal mapping of Saudi JSC concepts into PRC corporate-law concepts** | `股份公司` reads like PRC 股份有限公司; Saudi شركة المساهمة is a distinct statutory form governed also by the Capital Market Law | Keep JSC caveat; anti-flattening note in terminology lock; `b4_11` |
| 2 | **Confusing shareholder rights with partner rights** | Carry-over from Books 1–3 (合伙人); JSC has 股东, not 合伙人 | `b4_14` (`المساهم`→`股东`, assert `合伙人` absent from JSC bodies) |
| 3 | **Confusing board authorities with general-assembly authorities** | Art. 77 (board's broad authority vs assembly-exclusive matters), Art. 75 (major asset sale needs OGM) | `b4_13`, `b4_15`; explicit "exclusive to the assembly" wording |
| 4 | **Capital increase/decrease errors** | Wrong organ (must be EGM), wrong pre-conditions (issued capital fully paid), swapping 增资/减资, missing creditor protection (134–135) | `b4_20`, `b4_21`; encode organ + preconditions |
| 5 | **Ordinary vs extraordinary general assembly confusion** | Different quorums (1/4→1/2→any for OGM tiers; 1/2→1/4→any for EGM) and majorities (OGM majority; EGM 2/3, or 3/4 for capital/merger/etc.) | `b4_15`, `b4_17`; keep OGM/EGM strictly separate; state quorum tiers |
| 6 | **Majority computed on wrong base** | Majorities are on **votes represented at the meeting**, not on total capital — outcome-changing | `b4_17`; assert the "所代表的表决权" basis is stated |
| 7 | **Share-class terminology inconsistency** | 种类 (type: ordinary/preferred/redeemable) vs 类别 (class within a type); class changes need a 类别股东专门大会 | `b4_18`, `b4_19`, `b4_16` |
| 8 | **Listed vs non-listed rules mixed** | Circular resolutions, drag/tag, issuance differ; listed matters defer to Capital Market Law/CMA | `b4_12`, `b4_23`; carry the Capital-Market-Law caveat |
| 9 | **Pre-emption term collision** | Book Four `优先认购权` (subscription) vs Book One `优先购买权` (transfer) vs `赎回权` (redemption) | `b4_22` |
| 10 | **Drag/Tag caveats dropped** | Art. 113 requires 90% consent + good-faith buyer + not violating the Capital Market Law | `b4_23` |
| 11 | **Failing to keep `official_text_check = needs_check`** | Source is a thematic summary; nothing is officially verified | `b4_5`; enforced per record |
| 12 | **Inventing content for uncovered articles** | ~47 of 80 articles are not in the source; fabricating rules is prohibited | Data-model 1b + `needs_official_text_check`; `b4_29` (coverage enumerates all 80, no silent gaps) |
| 13 | **Wrong book-specific disclaimer scope** | Regression of the disclaimer hotfix (Book One scope leaking) | `b4_9`, `b4_10` (Markdown + HTML) |
| 14 | **Trust-wording overclaim** | Using verified/محققة/经核验 | `b4_6` |
| 15 | **Sukuk vs debt-instrument conflation** | Sukuk = ownership share in an asset; bond = debt — different liquidation priority & Shariah treatment | terminology lock D/E; `b4_18`-adjacent check on Art. 117 |
| 16 | **Loans-to-directors scope error** | Relatives definition (ascendants/descendants/spouses) determines contract validity; bank/finance-company exception | `b4_26` |
| 17 | **Raw Markdown leaking into rendered notes** | Recurring class of bug (fixed in shared `_md_to_html`) | `b4_27` (regression guard) |

## Overall risk posture

Book Four is the **highest-risk book so far**: dense governance rules, many easily-confused
distinctions, a listing/CMA overlay, and a source that only covers ~40% of the range article-by
-article. The split-PR plan (Option B) plus the terminology and QA locks are designed to keep each
reviewable slice small and to make every high-risk distinction an explicit, tested assertion.
