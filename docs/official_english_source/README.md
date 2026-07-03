# Official English guidance source — intake

This folder documents the **intake** of the official English guidance translation
of the Saudi Companies Law as a **source asset and planning layer only**.

- **Source:** Bureau of Experts at the Council of Ministers — Official Translation
  Department. *Companies Law*, Royal Decree No. M/132 (June 30, 2022).
- **Trust label:** `official_guidance_translation`.
- **Governing text:** **Arabic** (the English is guidance only; it is **not**
  binding/governing text).
- **Not legal advice.**

## What this PR is

Source intake + provenance + coverage planning. It adds:

- `inputs/companies_law_official_english_guidance.pdf` — the source PDF.
- `data/metadata/official_english_source.json` — provenance + coverage metadata.
- `docs/official_english_source/` — this documentation set.
- `scripts/extract_official_english_pdf_text.py` — optional text extractor.
- `data/extracted/official_english_companies_law_text.txt` — extracted text aid.
- `make official-english-source-validate` — a validation target.

## What this PR is NOT

- It does **not** create the English Legal LLM-ready layer.
- It does **not** generate English per-article records.
- It does **not** alter any Arabic canonical article/provision text.
- It does **not** alter any Chinese translation.

## Documents in this folder

| File | Purpose |
|------|---------|
| [`SOURCE_PROVENANCE.md`](SOURCE_PROVENANCE.md) | Authority, title, trust label, caveats, extraction limits |
| [`ENGLISH_SOURCE_SCOPE.md`](ENGLISH_SOURCE_SCOPE.md) | What the PDF covers; article range; alignment observations |
| [`ENGLISH_ALIGNMENT_PLAN.md`](ENGLISH_ALIGNMENT_PLAN.md) | Proposed future alignment model (Arabic ↔ English ↔ Chinese ↔ LLM layers) |
| [`ENGLISH_LAYER_RISKS.md`](ENGLISH_LAYER_RISKS.md) | Risks to manage before building any English layer |
