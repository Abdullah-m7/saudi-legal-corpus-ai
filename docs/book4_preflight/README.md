# Book Four Preflight / الباب الرابع — تمهيد ما قبل التنفيذ

**Status: PREFLIGHT / SCOPE-LOCK ONLY. Book Four content generation has NOT started.**

Book Four — **شركة المساهمة / 股份公司 (Joint-Stock Company, JSC)** — is larger and legally
denser than Books One–Three. This directory locks scope, terminology, QA design, and the build
plan **before** any canonical article dataset is generated, so the owner can approve the plan
first.

## Contents

| File | Purpose |
|------|---------|
| [`BOOK4_SCOPE_LOCK.md`](BOOK4_SCOPE_LOCK.md) | Titles, exact article range, section breakdown, source path, open questions |
| [`BOOK4_TERMINOLOGY_LOCK.md`](BOOK4_TERMINOLOGY_LOCK.md) | Initial locked AR→ZH terminology (uncertain items flagged `NEEDS_REVIEW`) |
| [`BOOK4_QA_PLAN.md`](BOOK4_QA_PLAN.md) | Planned `run_all_book4` QA rules |
| [`BOOK4_IMPLEMENTATION_PLAN.md`](BOOK4_IMPLEMENTATION_PLAN.md) | Recommended implementation path (single vs split PRs) + justification |
| [`BOOK4_REVIEW_RISKS.md`](BOOK4_REVIEW_RISKS.md) | Top legal/translation risks to guard against |

## Headline facts (from the attached PDF)

- **Article range:** 58–137 → **80 articles**.
- **Source shape:** the reference PDF is a **thematic / tabular summary of core provisions**,
  NOT a per-article translation. It explicitly omits several articles' details (e.g. 100, 111,
  116, 134–137). This materially affects the data model — see the scope lock and implementation
  plan.
- **Trust posture (unchanged):** `internally_reviewed_summary`; `official_text_check =
  needs_check`; not official; not legal advice.
- **Cross-reference:** listing / capital-market matters must be read with the **Capital Market
  Law** and CMA regulations.

## Non-goals of this PR

This PR does **not** create any of:
`data/articles/book4_*.json`, `data/articles/book4_*.jsonl`,
`content/{ar,zh,bilingual}/book4.md`, `data/coverage/book4_*`, or a Book Four generator.
Those come in a later, owner-approved stage.
