# LaTeX Source for the Corpus Resource Paper

LaTeX version of `../saudi_legal_corpus_resource_paper.md`.

| File | Purpose |
|---|---|
| `main.tex` | The paper. Venue-adaptive: see below. |
| `references.bib` | Bibliography (verify each entry before submission). |
| `main.pdf` | Compiled draft (fallback layout). |

## Venue adaptation

`main.tex` detects the official style files at compile time:

- **NLLP / ACL venues:** drop the official `acl.sty` and `acl_natbib.bst`
  (from the ACL style kit) next to `main.tex` — they are picked up
  automatically via `\IfFileExists`, and the paper compiles in review mode.
- **No style kit present:** a self-contained two-column fallback layout
  (Times, A4, `plainnat` bibliography) compiles with a plain TeX Live
  install, so the draft is always buildable and readable.
- **LREC:** replace the preamble with that year's official LREC kit
  (documentclass and bibliography style); the body and tables need no
  changes.

## Build

```
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

Requires (Debian/Ubuntu): `texlive-latex-base`, `texlive-latex-recommended`,
`texlive-fonts-recommended`.

## Pre-submission checklist

- [ ] Confirm full author name and affiliation (placeholder in `main.tex`).
- [ ] Add the official venue style kit and switch to it.
- [ ] Mint a DOI-carrying archival release and update Data Availability.
- [ ] Verify every `references.bib` entry against the published record.
- [ ] Check the venue's anonymity policy (the draft currently names the
      author and repository; blind review requires removing both).
