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
| `main.pdf` | Compiled manuscript (10 pages in the fallback layout). |

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
- **79.3% of citations are horizontal** (across instrument families), so
  Saudi legislation is genuinely cross-referential rather than merely
  hierarchical.
- **The Companies Law (46 citations from 26 instruments) and the Labour Law
  (36 from 23)** are the system's twin hubs; the Capital Market Law is cited
  deeply but narrowly (26 from 9).
- **Three confirmed dangling citations**: live instruments that still cite
  repealed predecessors, found by intersecting the citation and supersession
  graphs.
- **128 distinct instruments** are cited by Saudi legislation but absent from
  the corpus — a prioritised coverage work list.

## Pre-submission checklist

- [x] Author name, affiliation, ORCID.
- [x] Data availability with the corpus DOI.
- [x] Declarations block.
- [ ] Update the `almohammedi2026corpus` reference once paper 1 has a
      publication record (currently cited as under review).
- [ ] Move to Springer's own `sn-jnl` class (Overleaf template) before
      submission.
- [ ] Check the journal's current submission route — *Artificial
      Intelligence and Law* may use Snapp or Editorial Manager.
- [ ] Confirm the journal's figure-resolution requirements; both figures are
      generated at 300 dpi and can be re-rendered higher from the script.

## Note on sequencing

Paper 1 is under review at *Language Resources and Evaluation*. Submitting
this paper to a **different** journal is not dual submission — they are
distinct manuscripts with distinct contributions — but this one should not
be submitted anywhere until it is finished, and its citation to paper 1
should be updated when paper 1's status changes.
