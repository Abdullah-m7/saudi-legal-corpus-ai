# Double-anonymous release check

**Target:** *Artificial Intelligence and Law*  
**Policy checked:** 2026-09-01

## Manuscript text

- [x] no author name;
- [x] no affiliation or city;
- [x] no e-mail or ORCID;
- [x] no GitHub/Zenodo/user-account URL;
- [x] no acknowledgement or funding identity;
- [x] no self-citation framed as “our previous work”;
- [x] AI-assistance disclosure states roles without naming an author identity.

## Reviewer materials

- [x] generate editable `.docx` from `MANUSCRIPT_ANONYMOUS.md`;
- [x] scrub/check DOCX creator/last-modified-by/custom metadata; core properties are empty;
- [x] visually rendered and inspected all 8 pages after the final table/list rebuild; no clipping, overlap, broken tables or missing glyphs observed;
- [x] DOCX relationship scan found no external author-linked hyperlinks; visible DOI URLs are plain-text bibliography entries;
- [x] no reproduction package is included in the initial reviewer package; if later requested, it must use a separate anonymous review snapshot rather than an author-owned public URL;
- [x] reviewer-facing filenames contain no author identity.

## Non-anonymous information

Author identity, affiliation/status, correspondence data, acknowledgements, funding and declarations belong in the submission interface / separate title-page channel required by SNAPP, not in the reviewer-facing manuscript.

**Release gate:** `DOCX_QA_PASS__BLOCKED_ONLY_ON_HUMAN_METADATA_CONFIRMATION`.
