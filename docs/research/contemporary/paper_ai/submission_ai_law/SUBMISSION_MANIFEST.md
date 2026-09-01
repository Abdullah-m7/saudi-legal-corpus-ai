# Artificial Intelligence and Law — submission package manifest

**Prepared:** 2026-09-01  
**State:** `ANONYMOUS_DOCX_VISUAL_QA_PASS__HUMAN_METADATA_OPEN`
**Official instructions checked:** `https://link.springer.com/journal/10506/submission-guidelines`

## Package

- `MANUSCRIPT_ANONYMOUS.md` — reviewer-facing source; no author/affiliation/contact or repository URL.
- `MANUSCRIPT_ANONYMOUS.docx` — editable reviewer-facing Word file; 8-page visual QA PASS and metadata/identity scan PASS.
- `build_submission_docx.py` — deterministic Markdown→DOCX builder used to preserve tables, lists, Arabic passages and anonymity.
- `TITLE_PAGE_TEMPLATE.md` — non-anonymous metadata/declarations; complete only from author-confirmed facts.
- `PORTAL_METADATA.md` — values to paste into the submission interface after confirmation.
- `COVER_LETTER.md` — concise technical/empirical fit statement; does not discuss the earlier rejected manuscript.
- `ANONYMIZATION_CHECK.md` — double-anonymous release gate.

## Live journal requirements encoded here

- double-anonymous peer review; author identifying information removed from manuscript and associated reviewer files;
- abstract 150–250 words; current anonymous abstract = 215;
- 4–6 keywords; current = 6;
- editable source required; final anonymous Word `.docx` has been generated and visually QA-checked;
- author contribution and competing-interest information are entered through the submission interface;
- LLM use beyond copy-editing is documented in the manuscript; §11 carries the disclosure.

## Controller boundary

No new retrieval model, corpus, ablation or robustness experiment is authorized for initial submission. If the editor/reviewers later request architecture transport (for example a dense retriever), treat it as a revision question rather than pre-submission rescue work.
