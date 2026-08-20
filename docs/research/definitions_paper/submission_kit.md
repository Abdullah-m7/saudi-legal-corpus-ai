# Submission kit — *Statute Law Review* (Oxford University Press)

Everything needed to submit this article, with the exact text to paste into
each field. Regenerate the files first:

```
python3 docs/research/definitions_paper/definition_analysis.py
python3 docs/research/definitions_paper/make_figures.py
cd docs/research/definitions_paper && python3 build.py
pdflatex cover_letter && pdflatex cover_letter
```

## Where

| | |
|---|---|
| Journal home | <https://academic.oup.com/slr> |
| Author guidelines | <https://academic.oup.com/slr/pages/author-guidelines> |
| **Submission site** | **<https://mc.manuscriptcentral.com/statlaw>** (ScholarOne Manuscripts) |
| Editors-in-Chief | Professor Constantin Stefanou and Professor Helen Xanthaki |

ScholarOne accounts are per-publisher, not shared with Springer's Snapp (used
for papers 1 and 2). Create a new account with the same email and ORCID.

Note that Professor Xanthaki, one of the two Editors-in-Chief, is the author
of two of the works the article's drafting-literature footnotes rest on
(*Thornton's Legislative Drafting*, 6th edn, and *Drafting Legislation*).
That is a sign the article is aimed at the right journal, and it is also a
reason those two citations had to be exactly right; both were checked against
the published record.

## What to upload

| # | File | ScholarOne file designation |
|---|---|---|
| 1 | `submission_manuscript.docx` | Main Document — **anonymised**, double-spaced |
| 2 | `submission_title_page.docx` | Title Page — identity, declarations, word count |
| 3 | `fig1_funnel.eps` | Figure |
| 4 | `fig2_adjudication.eps` | Figure |
| 5 | `cover_letter.pdf` | Cover Letter |

The journal asks for Word files, figures as separate EPS or AI files rather
than embedded, and tables in editable form. `build.py` produces all of that:
it replaces each figure with a `[Figure N near here]` marker plus its
caption, keeps Table 1 as a real Word table, sets Normal, Body Text and
Footnote Text to double spacing, and refuses to write the manuscript if any
identifying string survives into it.

**Do not upload** `main.pdf` (identified) or `main_anon.pdf`. They exist so
the author can read the typeset article; the journal wants Word.

## Field-by-field

**Type:** Article (6,500–10,000 words including footnotes). This manuscript
is 7,972 words including footnotes — the figure printed on the title page and
by `build.py`; re-read it from the build output if the text changes.

**Title:**

```
What Counts as an Establishment? Definitional Fragmentation Across Saudi Arabian Legislation
```

**Running head:** Definitional Fragmentation in Saudi Legislation

**Abstract:** paste from `submission_manuscript.docx` (the paragraph under
*Abstract*). It contains no identifying material.

**Keywords:**

```
statutory definitions; legislative drafting; interpretation; Saudi Arabia; legal corpora; terminological consistency
```

**Author:** Abdullah Almohammedi · Independent Researcher ·
abdullah.m.almohammedi@gmail.com · ORCID 0009-0001-0832-0995

**Suggested reviewers:** none. The journal states that it does not consider
author-suggested reviewers.

**Review process:** the Editorial Office does an initial assessment, then one
of the Editors-in-Chief oversees double-anonymous review, normally by two
reviewers. The journal publishes three issues a year and gives no timeline.

## Declarations screens

| Question | Answer |
|---|---|
| Funding | None received. |
| Conflict of interest | None. |
| Ethics approval | Not applicable — no human participants, no animal subjects, no personal data; published national legislation only. |
| Data availability | Corpus and analysis code openly archived: DOI 10.5281/zenodo.22019183 (concept DOI 10.5281/zenodo.22019182). |
| Previously published / preprint | No preprint of this article. Two companion manuscripts on the same corpus are under review at other journals; disclosed in the cover letter and on the title page. |
| Under consideration elsewhere | No. |
| Licence | Standard licence (no charge). Choose a Creative Commons licence only if a funder requires it — open access charges apply and there is no funder here. |

## Format rules the build already applies

The journal asks for things the LaTeX source does not encode. `build.py`
handles each of them, so do not re-do them by hand in Word:

| Requirement | How it is met |
|---|---|
| Word files | pandoc, from the same `main.tex` |
| Double-spaced | Normal, Body Text and Footnote Text styles patched in a pandoc reference document |
| Times New Roman | the same reference document |
| No underlines | the Hyperlink style's underline is stripped; the anonymised manuscript has no links at all |
| Figures separate, not embedded | each figure becomes `[Figure N near here]` plus its caption; EPS files uploaded separately |
| Tables editable | Table 1 stays a real Word table |
| Cross-references | `\ref` is resolved to a number before conversion, because it otherwise becomes a broken internal link in Word |
| Anonymised | the `\ifanon` switch is resolved by the script, then the finished file is searched for identifying strings |

## Before clicking submit

- [ ] Re-run `build.py` and confirm it prints **clean** for the anonymity
      audit and **in range** for the word count.
- [ ] Open `submission_manuscript.docx` and check the first page is the title
      and abstract, with no author block.
- [ ] Check that the footnotes are numbered continuously and rendered as Word
      footnotes, not as endnotes or plain text.
- [ ] Confirm both EPS figures open.
- [ ] Confirm the title page carries the word count that `build.py` reported.

## After submission

Record the manuscript ID here, alongside the corresponding entries for papers
1 and 2:

```
Statute Law Review — manuscript ID: ____________  submitted: ____________
```
