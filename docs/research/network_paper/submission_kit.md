# Submission Kit — Artificial Intelligence and Law

Every field the submission system asks for, with the exact text to paste.
Plain text only — no LaTeX markup — since the interface stores what you type
verbatim and that is what gets published.

## Route: Snapp (same system as paper 1)

*Artificial Intelligence and Law* uses **Snapp**, the same platform as
*Language Resources and Evaluation*, so the account you created for paper 1
works here — no new registration.

Journal home: <https://link.springer.com/journal/10506>
Submission portal: <https://submission.springernature.com/>
(reached from the journal home page's **Submit manuscript** button)

The journal is hybrid: after acceptance you choose subscription publishing
(free) or open access (article processing charge). Nothing is decided at
submission.

---

## Files to upload

| Item | File |
|---|---|
| Manuscript (LaTeX sources) | `snapp_submission.zip` (`main.tex`, `references.bib`, `fig1_hubs.png`, `fig2_domain_flows.png`) |
| Cover letter | `cover_letter.pdf` — one page |
| Local preview only | `main.pdf` (do not upload; Snapp builds its own PDF) |

Upload the zip in the **Manuscript file** slot only. Leave *Figures and
tables*, *Supplementary material*, and *Related files* empty — the figures
are inside the zip, and the data is already public with a DOI.

---

## Article type

**Research** — an original empirical study.

---

## Title

```
Vertical Elaboration or Horizontal Integration? A Citation-Network Analysis of Saudi Arabian Legislation
```

---

## Abstract (plain text)

```
Network analysis of legal citation has produced a substantial literature for the United States and Europe, but the legal systems of the Arab world have remained outside it, for want of machine-readable statutory corpora. Using a newly released, provenance-annotated corpus of Saudi Arabian legislation, we construct and analyse what is, to our knowledge, the first citation network over Saudi statutory law: 290 legislative instruments, 15,689 articles, and 585 extracted inter-instrument references. We first address a problem that the citation literature typically leaves implicit: the extractor that resolves a cited law name to a target instrument is itself fallible. Validating every resolved edge against the target's registered title and adjudicating the residue by hand, we find a 3.3% misresolution rate and analyse only the 410 surviving citations. We then separate vertical citations, in which a subordinate instrument elaborates its own parent statute, from horizontal citations that cross instrument families. The distinction is not cosmetic: the Labour Law appears to rival the Companies Law as the system's leading hub until its eight annexes are recognised as part of its own family, after which its horizontal citation count falls by more than a third and the Companies Law stands alone. Horizontal citations nevertheless account for 70.5-74.4% of the network depending on how family boundaries are drawn, so Saudi legislation is genuinely cross-referential rather than merely hierarchical. The horizontal network is sparse (164 instruments, 206 edges) and highly concentrated: ten instruments receive 58% of all horizontal citations, led by the Companies Law (46 citations from 26 distinct instruments). Breadth and depth diverge sharply - the Capital Market Law draws 26 citations from only 9 instruments, while the Criminal Procedure Law draws 13 from 13 - a contrast that raw citation counts conceal. Cross-referencing the citation network against a hand-classified supersession graph, we identify live instruments that still cite repealed predecessors, and we map the instruments that Saudi legislation cites but that no consolidated machine-readable source yet covers. We discuss what these structures imply for legal informatics, retrieval-augmented legal AI, and legislative maintenance.
```

---

## Keywords

```
Legal citation networks
Saudi Arabia
Legislation
Legal informatics
Network analysis
Legal data quality
```

---

## Declarations entered through the interface

Snapp publishes the interface values, not the manuscript text, so enter
these here as well.

**Author contributions**

```
A.A. designed the study, built and validated the citation network, performed the analysis, produced the figures, and wrote the manuscript.
```

**Competing interests**

```
The author declares no competing interests.
```

**Funding**

```
No funding was received for conducting this study.
```

**Ethics approval**

```
Not applicable. The study involves no human participants, no animal subjects, and no personal data; it analyses published national legislation only.
```

**Data availability**

```
The corpus, the citation and supersession graphs, and the analysis and figure scripts that reproduce every number and figure reported in this paper are openly available at https://github.com/Abdullah-m7/saudi-legal-corpus-ai and archived on Zenodo under the MIT licence. The version analysed here is v1.0.2, DOI: 10.5281/zenodo.22019183; the concept DOI 10.5281/zenodo.22019182 always resolves to the latest version.
```

**Code availability**

```
All analysis code is included in the archived release cited under data availability.
```

---

## Answers to the Declarations screens

Identical to paper 1 except where noted:

| Screen | Answer |
|---|---|
| Publishing policy | Tick the acknowledgement box |
| Competing interests | **No** |
| Dual publication | **No** — the companion corpus paper is a distinct manuscript, and the Zenodo archive is data deposition, not publication |
| Authorship | Tick the confirmation box |
| Third party material | **No** — both figures are generated by the author's own scripts from the author's own data |
| Data availability | **Yes**, then paste the statement above |
| Acknowledgements | Leave blank |
| Research funding | **No** |
| Preprint (In Review) | **Yes** — recommended, for the same reasons as paper 1 |

---

## Before you press Submit

1. Read the PDF Snapp compiles from the zip, page by page. Check that both
   figures rendered, that Table 1 is intact, and that the bibliography
   resolved (15 references).
2. Check the author name, affiliation ("Independent Researcher"), and ORCID
   against the manuscript.
3. The manuscript cites the companion corpus paper as under review. If that
   paper's status changes before you submit this one, update the reference
   in `references.bib` and rebuild the zip.
4. Submit from a computer, not a phone.
