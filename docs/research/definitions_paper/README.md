# Paper 3 — Definitional Fragmentation Across Saudi Legislation

*What Counts as an Establishment? Measuring Definitional Fragmentation
Across Saudi Arabian Legislation.*

Third paper in the series. Paper 1 (`../corpus_paper/`) describes the corpus;
paper 2 (`../network_paper/`) analyses how instruments cite each other; this
one asks whether they use the same vocabulary.

| File | Purpose |
|---|---|
| `main.tex` | The manuscript (`\anonfalse` by default; set `\anontrue` if the target journal reviews anonymously). |
| `references.bib` | Bibliography. |
| `definition_analysis.py` | Produces every number: the indexical filter, lexical divergence, and the hand-adjudication table. |
| `definition_analysis_results.json` | Generated results snapshot. |
| `make_figures.py` | Produces Figures 1 and 2. |
| `fig1_funnel.png` / `fig2_adjudication.png` | The two figures. |
| `main.pdf` | Compiled manuscript (10 pages in the fallback layout). |

## Reproduce

```
python3 docs/research/definitions_paper/definition_analysis.py
python3 docs/research/definitions_paper/make_figures.py
cd docs/research/definitions_paper && pdflatex main && bibtex main && pdflatex main && pdflatex main
```

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
  activity. The rest are harmonized, instrument-local, homonymous, or
  indexical.
- **Flagship case**: a sole trader with no employees is an *establishment*
  under the Competition Law and is not one under the Labour Law.
- **The measured overstatement is 3×**, not more: all twelve adjudicated
  terms are lexically divergent and four are substantively conflicting.

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

## Candidate venues

**Statute Law Review** (Oxford University Press) — recommended. Its stated
objectives are the legislative process, law reform, and *the drafting and
interpretation of legislation*, which is exactly this paper's subject.
Verified requirements:

| | |
|---|---|
| Review model | Double-anonymous, two reviewers; author-suggested reviewers not considered |
| Length | Standard article 6,500–10,000 words **including footnotes**; short article 3,000–4,000 |
| Submission | ScholarOne — `mc.manuscriptcentral.com/statlaw` |
| Manuscript format | Word/RTF, footnote citation style (not LaTeX, not author–date) |
| Frequency | Three issues per year |

Two consequences for this manuscript. It currently runs ~3,000 words of
prose (~4,000 with tables, captions and references), so it fits the *short
article* band as written and needs roughly doubling to enter as a standard
article — the expansion that belongs there is doctrinal, not computational:
Saudi drafting convention on definitions, the sole-trader/establishment case
worked through, and comparison with jurisdictions that legislate general
interpretation acts. And the audience is doctrinal, so the legal question
has to lead and the pipeline has to sit behind it.

Alternatives considered:

- **International Journal of Law and Information Technology** (Oxford) — also
  ScholarOne, but its scope is AI, IT and cyberspace law. This paper is
  neither; the fit is weaker than Statute Law Review's.
- **Artificial Intelligence and Law** (Springer) — fits the legal-AI framing,
  but paper 2 is already under review there.
- **International Journal of Legal Discourse** (De Gruyter) — legal language.

Statute Law Review reviews double-anonymously (verified above), so the
`\anontrue` switch in `main.tex` must be set before submission — the same
step paper 2 needed.

## Pre-submission checklist

- [x] Analysis, figures, and manuscript build cleanly and reproducibly.
- [ ] Choose the venue and confirm its review model and submission route.
- [x] Quality review: every figure re-verified against the data; an invalid
      comparison in the Discussion corrected (it set 198-of-322 against
      4-of-12 and called the gap two orders of magnitude — the measured
      overstatement is 3×); the indexical filter's recall on the adjudicated
      sample (83%) now reported; a frequency-bias limitation added that
      argues the 4-in-12 figure is a lower bound on conflict density.
- [ ] Update the `almohammedi2026corpus` reference once paper 1 has a
      publication record.
