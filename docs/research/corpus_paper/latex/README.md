# LaTeX Source for the Corpus Resource Paper

LaTeX version of `../saudi_legal_corpus_resource_paper.md`.

| File | Purpose |
|---|---|
| `main.tex` | The paper. Venue-adaptive: see below. |
| `references.bib` | Bibliography (AraLegal-BERT, MultiLegalPile, and LEXTREME entries verified against the ACL Anthology; re-verify the rest before submission). |
| `example_record.png` | Figure 1 — an example unified-index record, rendered as an image because pdfLaTeX cannot typeset Arabic script. |
| `gen_example_record_figure.py` | Deterministic generator for Figure 1 (requires Pillow built with libraqm and the Noto Naskh Arabic font). |
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

- [x] Confirm full author name and affiliation (Abdullah Almohammedi,
      Independent Researcher, ORCID 0009-0001-0832-0995).
- [ ] Add the official venue style kit and switch to it.
- [x] Mint a DOI-carrying archival release and update Data Availability
      (Zenodo v1.0.2 — version DOI 10.5281/zenodo.22019183, concept DOI
      10.5281/zenodo.22019182).
- [ ] Verify every `references.bib` entry against the published record.
- [ ] Check the venue's anonymity policy (the draft currently names the
      author and repository; blind review requires removing both).
