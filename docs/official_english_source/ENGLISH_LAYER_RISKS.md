# English layer risks

Risks to manage **before** building any English layer. Documented now so the future
English work starts with eyes open. This PR does not build the layer.

## 1. Mistaking the English guidance translation for binding text

The PDF is an **official guidance translation**, not the binding law. The governing
text is Arabic. Mitigation: fixed label `official_guidance_translation`,
`governing_text_language = ar`, and repeated "not binding / not governing" notes.
Never label it `governing_text` or `binding_translation`.

## 2. Article numbering mismatch

English uses "Part N"; the repo's Arabic corpus uses "Book/الباب". Even where
numbering looks aligned (Articles 1–281, no gaps), per-article alignment is not yet
human-verified. Mitigation: default `alignment_status = needs_manual_check`; only a
reviewer promotes to `exact_article_match`.

## 3. PDF extraction / OCR errors

Although this PDF is born-digital (no OCR), the extracted text layer has cosmetic
spacing artifacts (e.g. "Competent Au thority", "joint -stock"). Mitigation:
normalize text before authoring; treat the extracted `.txt` as an aid, not a record.

## 4. Misalignment between the full Arabic law and the partial Chinese Book Four source

The English source covers the **full** law (Articles 1–281). The repository's Arabic
canonical currently covers Books 1–4 (Articles 1–137), and the Chinese/Book Four
reference is a **partial, thematic** source (model 1b — only some Book Four articles
are provision-covered). Do not assume English coverage implies Chinese/Arabic
coverage. Mitigation: alignment is per existing coverage matrices; uncovered items
stay `needs_official_text_check` / `not_available`.

## 5. Using English to overwrite Arabic canonical meaning

The English must never edit or re-interpret Arabic canonical text. Mitigation:
English is stored as `english_reference_text` only; Arabic canonical records are
read-only from the English layer's perspective.

## 6. Confusing official guidance translation with legal advice

Official ≠ legal advice. Mitigation: `not_legal_advice: true` in metadata and a
"not legal advice" line in every document and the README section.

## 7. Terminology drift between Arabic, Chinese, and English

Three languages risk diverging term choices (e.g. issued vs authorized capital;
شركة التضامن / 无限公司 / General Partnership). Mitigation: a shared glossary check
in the future layer; keep the existing Arabic↔Chinese glossary authoritative and add
English mappings rather than redefining terms.

## 8. Overclaiming verification

Saying alignment/translation is "verified" when it is only internally reviewed is an
overclaim (the project already bans `verified` / `محققة` / `经核验`). Mitigation:
keep `official_text_check = needs_check` posture; use `needs_manual_check` for
alignment; never assert binding/verified English.
