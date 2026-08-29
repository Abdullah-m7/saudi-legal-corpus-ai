# Paper 3 — Definitional Fragmentation Across Saudi Legislation

*How Much Do Statutes Disagree? Measuring Definitional Fragmentation Across a
Legal System.*

Third paper in the series. Paper 1 (`../corpus_paper/`) describes the corpus;
paper 2 (`../network_paper/`) analyses how instruments cite each other; this
one asks whether they use the same vocabulary.

> **Desk-rejected by Statute Law Review on 28 August 2026**
> (`STATLAW-2026-147`), before review. The editors said it was not suitable
> and suggested *a journal specialising in Company Law* — which the article is
> not: it compares the Competition Law with the Labour Law and ends at
> drafting reform, which is SLR's own subject.
>
> The likeliest reading is that the title did the filing. *Establishment*, to
> a British lawyer, is either freedom of establishment or a corporate vehicle;
> the Arabic **المنشأة** is neither. The second possibility cannot be excluded
> and is the same pattern as the JLA rejection the same day: a description of
> Saudi law offered to readers with no stake in Saudi law.
>
> The article has therefore been reframed rather than merely retitled. The
> general proposition now leads — in the title, in the abstract, and in the
> first paragraph — and the sole trader arrives as the illustration rather
> than the subject.

**Note on the venue circle.** Constantin Stefanou and Helen Xanthaki are joint
editors-in-chief of *Statute Law Review*; Stefanou directs the Sir William
Dale Centre for Legislative Studies at IALS and was managing editor of the
*European Journal of Law Reform* from 2012 to 2022, remaining on its advisory
board. EJLR is therefore not the next venue. The editorship of *The Theory and
Practice of Legislation*, where paper 5 is under review, has not been checked.

**Target: US law reviews, beginning with the *Notre Dame Journal of
Legislation*** — a legislation journal at Notre Dame Law School, taking
unsolicited work from academics and practitioners through Scholastica, in
Bluebook. Requirements verified from its own pages and recorded in
`submission_kit.md`.

**The Loophole was the earlier choice and was dropped after a check.** It is
the journal of the Commonwealth Association of Legislative Counsel, and its
readers are exactly the drafters this article addresses — but it is **not in
DOAJ**, has no impact factor, and is a professional rather than an indexed
academic journal. With nothing yet published, an unindexed line buys less than
the route that permits **simultaneous submission**: one Bluebook conversion
opens dozens of law reviews at once, where *The Loophole* is one submission
and one chance. The Loophole stays as the fallback; it has no window to miss.

> **The cost of this route, stated:** US law reviews are **not anonymous**, and
> an unaffiliated researcher is at a disadvantage a double-anonymous journal
> removes. That is being paid deliberately, for the academic line.

| File | Purpose |
|---|---|
| `main.tex` | The manuscript — the single source for every build. Carries an `\anonfalse`/`\anontrue` switch. |
| `build.py` | Produces every submission file from `main.tex`, and audits the anonymised one. |
| `definition_analysis.py` | Produces every number: the indexical filter, lexical divergence, and the hand-adjudication table. |
| `definition_analysis_results.json` | Generated results snapshot. |
| `make_figures.py` | Produces Figures 1 and 2, as PNG (for the PDF) and EPS (for the journal). |
| `fig1_funnel.*` / `fig2_adjudication.*` | The two figures. |
| `main.pdf` | Identified build, typeset — for the author, not for upload. |
| `main_anon.pdf` | Anonymised build, typeset — read this before uploading. |
| `submission_manuscript.docx` | **Upload.** Anonymised, double-spaced, figures referenced not embedded. |
| `submission_title_page.docx` | **Upload.** Identity, declarations, word count. |
| `cover_letter.tex` / `.pdf` | **Upload.** One page. |
| `submission_kit.md` | Every submission field with the exact text to paste, and the answer to every declarations screen. |
| `references.bib` | Retained from the earlier author–date build; `main.tex` no longer uses it, because the journal wants footnote citations. |

## Reproduce

```
python3 docs/research/definitions_paper/definition_analysis.py
python3 docs/research/definitions_paper/make_figures.py
cd docs/research/definitions_paper && python3 build.py
pdflatex cover_letter && pdflatex cover_letter
```

`build.py` needs `pandoc`; everything else needs a plain TeX Live plus
`matplotlib`. The analysis is read-only over `data/` and deterministic.

## Headline findings

- **1,558 of 1,920 defined terms are used by a single instrument.** Saudi
  drafting is overwhelmingly local; fragmentation can only live in the 19%
  of the lexicon that is shared.
- **171 terms are indexical** — "the Law" defined as itself, "the Ministry"
  as its own supervising body. These dominate any raw ranking ("the Law" is
  defined 125 times) and cannot disagree with one another.
- **61.5% of substantive shared terms diverge lexically** — and the paper
  argues this figure should not be reported as legal inconsistency.
- **Of the twelve most widely shared substantive terms, four carry
  materially conflicting scope**: establishment, consumer, the Kingdom,
  activity. The rest are harmonised, instrument-local, homonymous, or
  indexical.
- **Flagship case**: a sole trader with no employees is an *establishment*
  under the Competition Law and is not one under the Labour Law.
- **The measured overstatement is 3×**, not more: all twelve adjudicated
  terms are lexically divergent and four are substantively conflicting.
- **The extended definition of "the Kingdom" is a tax phenomenon.** Thirteen
  of seventeen instruments define it as, simply, "the Kingdom of Saudi
  Arabia"; the four that define territory and offshore sovereign rights are
  exactly the four fiscal instruments.
- **A general interpretation act would fix one of the four**, not all four —
  the article works through which, and why that is still worth having.

## Two bugs the build caught (both would have changed the headline)

1. **Normalisation mismatch.** The keyword lists were written in ordinary
   orthography while the tokenizer emits normalised forms, so every head
   ending in teh-marbuta never matched — silently classifying "the
   Regulation", "the Ministry" and "the Authority" as substantive terms in
   conflict with one another.
2. **Genus test applied too widely.** Treating the relative pronouns *man*
   and *ma* as genus words anywhere in a definition excluded genuine
   indexical definitions. The test now applies only at the head of the
   definition, which is where Arabic statutory drafting puts the genus.

## Why `build.py` exists

pdfLaTeX honours the `\ifanon` switch. **pandoc does not** — it silently
keeps the identifying material and drops `\maketitle`. Converting the
manuscript by hand would therefore have uploaded an author-identified
"anonymised" file to a double-anonymous journal, and nothing in the output
would have shown it. `build.py` resolves the conditionals itself before
either tool runs, then greps the finished `.docx` for the author's name,
email, ORCID, GitHub handle and Zenodo DOIs, and refuses to finish if any of
them survived.

It also applies the journal's format requirements, which the LaTeX source
does not encode: double spacing on the Normal, Body Text and Footnote Text
styles (pandoc ignores `setspace`), figures replaced by `[Figure N near
here]` markers with their captions retained, and the word count computed from
the finished Word file rather than estimated.

## Venue

**Notre Dame Journal of Legislation**, through Scholastica, in Bluebook, and
then further US law reviews under the simultaneous-submission norm. Every
requirement, every field, and the reasoning for the route are in
`submission_kit.md`.

### The venue that rejected it, and the two that were declined

*Statute Law Review* (Oxford) desk-rejected the article on 28 August 2026
(`STATLAW-2026-147`) without review, suggesting a company-law journal. The
article is not company law; the likeliest reading is that *establishment* in
the old title read to a British lawyer as a corporate vehicle. Reframed rather
than merely retitled.

*European Journal of Law Reform* is excluded: Constantin Stefanou, who signed
the Statute Law Review rejection, was its managing editor from 2012 to 2022
and remains on its advisory board.

*The Loophole*, the journal of the Commonwealth Association of Legislative
Counsel, was the earlier choice and remains the fallback. Its readers are
exactly the drafters this article addresses, but it is not in DOAJ and has no
impact factor, and one submission there is one chance where a Bluebook
conversion opens many.

## Pre-submission checklist

- [x] Analysis, figures, and manuscript build cleanly and reproducibly.
- [x] Venue chosen; review model, length band, and submission route verified
      against the journal's own author instructions.
- [x] Expanded from short-article to article length, with the legal question
      leading and the doctrinal analysis of the four conflicting terms as the
      substantive core.
- [x] Citations converted to numbered OSCOLA footnotes; drafting and
      interpretation literature added and each reference verified against the
      published record.
- [x] Every count re-verified against the glossary data after the expansion,
      which caught six errors — a footnote citing the Environmental Law for a
      term it does not define; a miscount of the bodies enumerated in the
      Building Code Law; two instruments left unaccounted for in the
      per-term totals; and two definitions described more loosely than the
      text supports.
- [x] Quality review: every figure re-verified against the data; an invalid
      comparison in the Discussion corrected (it set 198-of-322 against
      4-of-12 and called the gap two orders of magnitude — the measured
      overstatement is 3×); the indexical filter's recall on the adjudicated
      sample (83%) now reported; a frequency-bias limitation added that
      argues the 4-in-12 figure is a lower bound on conflict density.
- [x] Anonymised build audited programmatically for identifying strings.
- [ ] Camera-ready only: replace the "companion study" wording in section 2.3
      and in the data availability statement with full citations to papers 1
      and 2 once they have publication records. They are referred to
      obliquely in the submitted version because naming them would identify
      the author to reviewers.
- [x] **Submitted to Statute Law Review, 20 August 2026 — STATLAW-2026-147.**
      Submission proof audited for anonymity, footnote rendering and figure
      resolution before submitting; see `submission_kit.md`.
