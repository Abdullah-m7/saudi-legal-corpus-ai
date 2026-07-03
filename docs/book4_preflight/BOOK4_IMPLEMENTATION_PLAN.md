# BOOK 4 — IMPLEMENTATION PLAN / خطة التنفيذ

> **Book Four content generation has NOT started.** This plan is for owner approval before any
> canonical Book Four data is generated.

## Decision inputs

| Factor | Book Four reality |
|--------|-------------------|
| Number of articles | **80** (Arts. 58–137) — twice the 40-article split threshold |
| Legal density | Very high: governance, board vs assembly authorities, OGM/EGM quorums & majorities, share types/classes, capital increase/decrease, pre-emption, drag/tag, Sukuk, major-loss & creditor protection |
| Source shape | **Thematic summary**, not per-article: only ~33 of 80 articles have explicit content in the PDF |
| Review burden | A single 80-article PR would be very hard for the owner to review carefully |
| CI/test complexity | Manageable per section; large in aggregate |
| Cross-references | Capital Market Law / CMA regulations for listing matters |

## Options

### Option A — One full Book Four PR
- One branch, one PR containing all 80 articles + QA + content + render + tests.
- **Pros:** single review; atomic.
- **Cons:** huge diff; high review fatigue; high chance of a terminology slip going unnoticed;
  forces a decision on the ~47 uncovered articles inside one big change; long feedback loops.

### Option B — Split into multiple PRs by thematic section  ✅ RECOMMENDED
Sequence, each its own branch/PR into `main`, each independently green:

0. **PR 4.0 — this preflight** (scope/terminology/QA/plan/risks lock). *(current)*
1. **PR 4.1 — Book Four infrastructure + data-model decision applied**
   - Register Book Four in `books.py` (paths, display titles, **book-specific disclaimer**:
     `الباب الرابع … 58–137` / `第四编（第五十八条至第一百三十七条）`).
   - Add `run_all_book4` skeleton (structural + trust + disclaimer rules), `validate_book(4)`
     dispatch, Makefile `book4-*` targets, scripts `gen_book4_articles.py` /
     `build_book4_jsonl.py` / `render_book4_html.py` / `render_book4_pdf_weasyprint.py`,
     `.gitignore` for `dist/book4.*`, README Book Four section, glossary additions from the
     terminology lock. **No article content yet** (empty/'§ pending' dataset or Section 1 only).
2. **PR 4.2 — Section 1: التأسيس ورأس المال / 设立与资本 (58–66)**
3. **PR 4.3 — Section 2: مجلس الإدارة والحوكمة / 董事会与治理 (67–83)**
4. **PR 4.4 — Section 3: الجمعية العامة / 股东大会 (84–102)**
5. **PR 4.5 — Section 4: الأسهم وأدوات الدين والصكوك / 股份与融资 (103–120)**
6. **PR 4.6 — Section 5: المالية والأرباح وتغيير رأس المال / 财务与资本变更 (121–137)**
7. **PR 4.7 — Book Four finalization**: full coverage matrix over all 80 (uncovered →
   `needs_official_text_check`), content Markdown, HTML/PDF render, complete `run_all_book4`,
   `tests/test_book4.py`, README polish.

- **Pros:** each PR is reviewable; terminology locked once (PR 4.1) then applied; the
  uncovered-articles decision is explicit and isolated; CI stays fast; failures localize to a
  section.
- **Cons:** more PRs / more merges (acceptable; matches the per-book cadence already used).

## Recommendation

**Adopt Option B (split by the five thematic sections), preceded by an infrastructure PR.**
Rationale: 80 articles far exceeds the 40-article split guideline; the legal density and the
board-vs-assembly / OGM-vs-EGM / type-vs-class distinctions are exactly the places a large diff
would hide an error; and the source's thematic shape means the uncovered-article policy must be an
explicit, isolated decision rather than buried in one 80-article PR.

## Blocking prerequisite before PR 4.1

Resolve **Open Question 1 (data model)** from the scope lock:
- **Recommended: model 1b** — a thematic/provisions dataset keyed to the ~33 articles actually
  covered, plus a coverage matrix enumerating all 80 (uncovered → `needs_official_text_check`).
  This keeps the corpus honest (no invented rules) and matches the source. Await owner decision.

## Guardrails for every Book Four content PR

- Trust posture fixed: `internally_reviewed_summary` + `official_text_check = needs_check`; never
  `verified` / `محققة` / `经核验`.
- Book-specific disclaimer only (post-hotfix mechanism); no Book One–Three scope leak.
- Do **not** modify Books One–Three canonical legal article text.
- Keep `make validate` / `book2-validate` / `book3-validate` / `test` green; PDF is local only,
  never claimed by CI.
