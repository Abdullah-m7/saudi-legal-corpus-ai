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
| `main.pdf` | Compiled manuscript (9 pages in the fallback layout). |

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

- **Statute Law Review** (Oxford) — legislative drafting and statutory
  interpretation; quantitative work is unusual there, which cuts both ways.
- **Artificial Intelligence and Law** (Springer) — fits the legal-AI framing,
  but paper 2 is already under review there.
- **International Journal of Legal Discourse** (De Gruyter) — legal language.

Verify the chosen journal's review model before submitting: paper 2's target
turned out to review double-anonymously, which required blinding the
manuscript. The `\anontrue` switch in `main.tex` is there for that.

## Pre-submission checklist

- [x] Analysis, figures, and manuscript build cleanly and reproducibly.
- [ ] Choose the venue and confirm its review model and submission route.
- [ ] Quality review (as run on papers 1 and 2).
- [ ] Update the `almohammedi2026corpus` reference once paper 1 has a
      publication record.
