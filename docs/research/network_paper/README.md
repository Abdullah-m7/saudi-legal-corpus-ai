# Paper 2 — Citation-Network Analysis of Saudi Legislation

*Vertical Elaboration or Horizontal Integration? A Citation-Network Analysis
of Saudi Arabian Legislation* — targeted at **Artificial Intelligence and
Law** (Springer), the journal of record for the AI-and-law field.

Builds on paper 1 (`../corpus_paper/`, under review at *Language Resources
and Evaluation*): that paper describes the corpus, this one analyses the
legal system the corpus captures.

| File | Purpose |
|---|---|
| `main.tex` | The manuscript. Uses `sn-jnl.cls` when present, else a self-contained fallback. |
| `references.bib` | Bibliography, including the corpus paper and its Zenodo DOI. |
| `network_analysis.py` | Produces every number in the paper: edge validation, centrality, vertical/horizontal split, dangling citations, coverage, domain flows. |
| `network_analysis_results.json` | Generated results snapshot (regenerate with the script). |
| `make_figures.py` | Produces Figures 1 and 2 from the results. |
| `fig1_hubs.png` | Figure 1 — horizontal citations received, with breadth alongside depth. |
| `fig2_domain_flows.png` | Figure 2 — domain-to-domain citation flow heatmap. |
| `main.pdf` | Compiled manuscript (11 pages in the fallback layout). |
| `cover_letter.pdf` | Cover letter, one page — upload this to Snapp. |
| `cover_letter.tex` | Source for the cover letter. |
| `submission_kit.md` | Every submission field with the exact text to paste, and the answer to every Declarations screen. |
| `snapp_submission.zip` | **Blinded** LaTeX sources for upload — Snapp compiles them to PDF. |
| `main_identified.tex` / `main_identified.pdf` | Identified build, for the record and the camera-ready. Never uploaded. |

## Reproduce

```
python3 docs/research/network_paper/network_analysis.py
python3 docs/research/network_paper/make_figures.py
cd docs/research/network_paper && pdflatex main && bibtex main && pdflatex main && pdflatex main
```

Requires `networkx`, `numpy`, `scipy`, `matplotlib`. The analysis is
read-only over `data/` and deterministic.

## Headline findings

- **3.3% of resolved citation edges were misresolutions** and were dropped
  after hand adjudication; the paper argues this validation step should be
  standard in citation-network studies built on automatic extraction.
- **70.5–74.4% of citations are horizontal** (across instrument families,
  bounds from two family readings), so Saudi legislation is genuinely
  cross-referential rather than merely hierarchical.
- **The Companies Law is the dominant hub** (46 citations from 26
  instruments); the Labour Law follows at 23 from 19. A naive family
  definition — stripping suffixes from identifiers — makes the Labour Law
  look like a co-leader at 36 citations, because 13 come from its own
  annexes. The quality review caught this and the corrected definition is
  what the paper reports.
- **Citation is concentrated**: the ten most-cited instruments receive 58.1%
  of all horizontal citations.
- **Robustness**: recomputing without the edge-validation step moves the
  horizontal share only from 70.5% to 71.5% and leaves the leading hubs
  unchanged.
- **Three confirmed dangling citations**: live instruments that still cite
  repealed predecessors, found by intersecting the citation and supersession
  graphs.
- **128 distinct instruments** are cited by Saudi legislation but absent from
  the corpus — a prioritised coverage work list.

## Pre-submission checklist

- [x] Author name, affiliation, ORCID.
- [x] Data availability with the corpus DOI.
- [x] Declarations block.
- [x] Quality review: family-definition bug found and corrected; novelty
      claims hedged; robustness check and concentration statistic added;
      limitations extended to family assignment and to what citation counts
      do and do not measure.
- [ ] Update the `almohammedi2026corpus` reference once paper 1 has a
      publication record (currently cited as under review).
- [ ] Move to Springer's own `sn-jnl` class (Overleaf template) before
      submission.
- [x] Submission route confirmed: Snapp, the same platform as paper 1.
- [x] Cover letter, submission kit, and upload zip prepared.
- [x] Blinded for double-anonymous review: author block, self-citation,
      data-availability URL/DOI, and the Declarations section are all
      switched off by `\anontrue`; the compiled PDF was audited for
      identifying strings and is clean.
- [ ] After acceptance, flip `\anontrue` to `\anonfalse` and restore the
      full Data availability statement and Declarations.
- [ ] Confirm the journal's figure-resolution requirements; both figures are
      generated at 300 dpi and can be re-rendered higher from the script.

## Note on sequencing

Paper 1 is under review at *Language Resources and Evaluation*. Submitting
this paper to a **different** journal is not dual submission — they are
distinct manuscripts with distinct contributions — but this one should not
be submitted anywhere until it is finished, and its citation to paper 1
should be updated when paper 1's status changes.
