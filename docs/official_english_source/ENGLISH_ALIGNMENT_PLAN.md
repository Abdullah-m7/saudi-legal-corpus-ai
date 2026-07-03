# English alignment plan (future)

This document proposes a **future** alignment model. Nothing here is built in this
PR — this PR is source intake + planning only.

## Goal

Give each article/provision a single aligned view across all layers, while keeping
**Arabic as the governing text** and never letting the English guidance translation
overwrite Arabic canonical meaning.

## Layers to align (per article / provision)

1. **Arabic canonical article/provision record** — the existing source of truth
   (`data/articles/*.json`; Book Four provisions in `book4_provisions_*.json`).
   Governing meaning.
2. **Official English guidance translation text** — from this intake source.
   Reference only (`official_guidance_translation`).
3. **Chinese translation / reference layer** — existing `chinese_translation`.
4. **Arabic Legal LLM metadata** — existing `data/arabic_legal_llm/*`.
5. **Future English Legal LLM metadata** — NOT built yet (separate future PR).

## Proposed alignment record (illustrative, not implemented)

```jsonc
{
  "book": 4,
  "article_number": 60,
  "arabic_canonical_ref": "sa-companies-book4-... (governing)",
  "english_reference_text": "Issued and Authorized Capital ...",
  "english_source_status": "official_guidance_translation",
  "governing_text_language": "ar",
  "alignment_status": "exact_article_match",
  "chinese_reference_ref": "…",
  "arabic_legal_llm_ref": "ar-llm-book4-art060",
  "english_legal_llm_ref": null,
  "notes": "English is guidance only; Arabic governs."
}
```

## Recommended future labels

- `english_reference_text` — the English guidance text for the article.
- `english_source_status = official_guidance_translation` — fixed trust label.
- `governing_text_language = ar` — Arabic always governs.
- `alignment_status` — one of:
  - `exact_article_match` — English article N maps 1:1 to Arabic article N.
  - `section_level_match` — aligns at section/chapter level, not article-exact.
  - `needs_manual_check` — alignment not yet human-verified.
  - `not_available` — no English text for this item.

## Sequencing (proposed, future PRs)

1. Normalize the extracted English text (fix cosmetic spacing artifacts).
2. Segment English by `Article N:` headings → `{article_number: english_text}`.
3. For the repository's covered range (Arabic Books 1–4, Articles 1–137), attach
   `english_reference_text` with `alignment_status`, defaulting to
   `needs_manual_check` until a reviewer confirms `exact_article_match`.
4. Only then consider a separate **English Legal LLM-ready layer** (mirroring the
   Arabic layer schema), as its own PR.

## Guardrails carried into every future step

- Arabic canonical text is never modified to match English.
- Chinese translations are never modified by English intake.
- English is stored as reference (`english_reference_text`), never as
  `governing_text` / `binding_translation`.
- Unverified alignment is `needs_manual_check`, never silently `exact_article_match`.
