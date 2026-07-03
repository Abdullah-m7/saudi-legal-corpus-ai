# Source provenance — official English guidance translation

## Source authority

**Bureau of Experts at the Council of Ministers** (هيئة الخبراء بمجلس الوزراء).

## Department

**Official Translation Department** (contact printed in the PDF: `otd@boe.gov.sa`).

## Title / instrument

- **Companies Law** (*Translation of Saudi Laws*).
- **Royal Decree No. M/132**, dated **June 30, 2022**.

## Trust label

`official_guidance_translation`.

This is an **official guidance translation** issued by the Bureau of Experts'
Official Translation Department. It is authoritative *as guidance*, but it is
**not** the binding legal text.

## Governing text remains Arabic

The **Arabic** text is the governing / binding legal text. The PDF states this
verbatim on its NOTES page:

> "This translation is provided for guidance. **The governing text is the Arabic
> text.**"

We therefore do **not** label this source `governing_text`, `binding_translation`,
or `unofficial_translation`. It is an `official_guidance_translation`.

## Not legal advice

Nothing in this repository — including this English source, its extracted text, or
any future English layer — is legal advice.

## PDF source path

`inputs/companies_law_official_english_guidance.pdf`

- SHA-256: `bcb6c090f3d69349f9091f7a59592ff720e2921995b0f20bacf12e4d8121b782`
- Pages: **89**
- Producer metadata: authored in Microsoft® Word 2016 (born-digital text PDF).

## Visible PDF caveats / disclaimers

Reproduced from the PDF's NOTES page (page 2):

1. "This translation is provided for guidance. The governing text is the Arabic text."
2. Interpretation conventions stated by the translator:
   - Words in the singular include the plural and vice versa.
   - Words in the masculine include the feminine.
   - Words in the present tense include the present and the future.
   - "person"/"persons" (and related pronouns) refer to a natural **and** legal person.

Contact for comments/inquiries printed in the PDF: `otd@boe.gov.sa`.

## Extraction limitations

- The PDF is **born-digital** (Microsoft Word export), so the text layer extracts
  cleanly with `pypdf` — **no OCR was required**.
- Extraction is provided as an aid only:
  `data/extracted/official_english_companies_law_text.txt`.
- Minor whitespace artifacts appear in the raw extraction (e.g. stray spaces inside
  words such as "Competent Au thority", "inco rporated"). These are cosmetic
  text-layer spacing artifacts, not content errors, and must be normalized before
  any future English-layer authoring. Extraction status is recorded in
  `data/metadata/official_english_source.json` (`extraction_status: extracted_ok`).
