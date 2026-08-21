# Paper 4 — Legislative Churn Across Saudi Legislation

*What Changes, and Where? Legislative Churn Across Saudi Arabian Legislation.*

Fourth paper in the series. Paper 1 (`../corpus_paper/`) describes the corpus;
paper 2 (`../network_paper/`) analyses how instruments cite each other; paper 3
(`../definitions_paper/`) asks whether they share a vocabulary. This one asks
the temporal question the first three left alone: what changes, where, and how
much.

**Venue not yet chosen.** The draft is complete and builds; it is deliberately
venue-neutral until the target is picked and its requirements verified, as was
done for paper 3.

| File | Purpose |
|---|---|
| `main.tex` | The manuscript — single source for every build. Carries an `\anonfalse`/`\anontrue` switch. |
| `build.py` | Produces the submission files and audits the anonymised one. |
| `amendment_analysis.py` | Produces every number. |
| `amendment_analysis_results.json` | Generated results snapshot. |
| `make_figures.py` | Produces Figures 1 and 2, as PNG (for the PDF) and EPS (for a journal). |
| `fig1_churn.*` / `fig2_citation_tiers.*` | The two figures. |
| `main.pdf` | Identified build, typeset. |
| `main_anon.pdf` | Anonymised build, typeset. |
| `submission_manuscript.docx` / `submission_title_page.docx` | Word builds, ready for a journal that wants them. |

## Reproduce

```
python3 docs/research/amendment_paper/amendment_analysis.py
python3 docs/research/amendment_paper/make_figures.py
cd docs/research/amendment_paper && python3 build.py
```

`build.py` needs `pandoc`; everything else needs a plain TeX Live plus
`matplotlib`. The analysis is read-only over `sources/` and `data/` and
deterministic.

## Where the data came from

The measurable layer was already in the corpus and unused by papers 1–3: every
article verified against an official source carries a legal status in the
source's own terms — *asliyyah* (original), *mu'addalah* (amended), *mulghah*
(repealed), *mudafah* (added) — and 972 articles also carry an amendment
history. That is 13,089 articles across 272 of the 291 tracks.

## Headline findings

- **973 articles (7.4%) are no longer in their original form**: 730 amended,
  138 repealed, 105 added.
- **Change is extremely concentrated.** 160 of 272 instruments (58.8%) record
  no change at all; the ten most changed hold 34.4% of all changed articles;
  Gini 0.82.
- **Instruments change in three different ways**, and a single "amendments"
  count would merge them: the Sharia Procedure Law is *hollowed out* (75 of its
  90 changed articles are repeals — 54% of every repeal in the corpus), the
  Commercial Agencies Regulation *accretes* (27 of 28 are additions), the VAT
  Regulation is *tuned in place* (42 amendments, no repeals).
- **Amendment arrives in consignments, not a drip.** 179 distinct amending
  decrees; the ten most active account for 35.4% of article-amendment pairs;
  one royal decree touches 81 articles.
- **"Amended" hides an order of magnitude.** On the 87 articles with a recorded
  prior text, median similarity to the superseded wording is 0.82 — but 17 of
  87 retain under half their vocabulary, and one article of the Judiciary Law
  keeps under a tenth.
- **Instruments others rely on change more**: 6.1% churn for uncited
  instruments, 10.7% for cited, 13.4% for the fifteen most cited. Age is not
  controlled for and may explain part of it — stated in the paper, not buried.
- **Cross-instrument references are twice as exposed as internal ones**: 17.4%
  of references to another instrument's article point at text that has since
  changed, against 8.6% for references to an instrument's own articles and a
  7.4% base rate. The mechanism is plain — a drafter can see the references
  inside the instrument being amended and cannot see the ones pointing at it.

## Two traps the build caught before they became claims

1. **Prior-text selection.** An amendment-history entry that carries text is
   not automatically a superseded version. Entries labelled *amended*, or
   carrying no label, have a **median Jaccard of 1.00 against the article's
   current wording** — they restate the current text. Using them would have
   produced a magnitude analysis over 226 articles concluding that amendments
   barely change anything. Only the 87 entries labelled *original* are genuine
   prior wording. `amendment_analysis.py` publishes the similarity evidence for
   the exclusion instead of asserting it.
2. **Base rate.** "8.9% of citations point at changed law" looks like a
   finding; the corpus base rate is 7.4%, a ratio of 1.19 — nothing. The real
   result only appeared after splitting inter- from intra-instrument
   references. Every share in the paper is reported against the base rate.

## Known limits, stated in the paper

- The status layer is a transcription of what each official record exposed, so
  churn is understated where a record is silent — a one-way error.
- The magnitude sample is 87 articles (11.9% of amended articles) and is
  selected by which sources publish prior text.
- The reliance gradient is uncontrolled for age; the registry dates 2 of 291
  tracks, so it cannot be controlled from this corpus.
- Only 174 of 759 article-amendment pairs carry a Gregorian date, and the
  instruments that do are unrepresentative, so **no time series is attempted** —
  the apparent 2021 spike is an artefact of which sources expose dates.
- The cross-reference layer is pattern-extracted; the inter-instrument exposure
  figure rests on 86 resolved references.

## Next steps

- [ ] Choose the venue and verify its review model, length band, and submission
      route against the journal's own author instructions — the paper-3
      procedure. Current draft is ~4,400 words including footnotes, which suits
      an empirical-legal-studies or legal-informatics venue as it stands and
      would need expansion for a law review.
- [ ] Quality review before submission. The three previous papers each had a
      headline-changing defect caught at this stage.
- [ ] Decide how to refer to papers 1–3: they are cited obliquely as "companion
      studies" so the manuscript can be anonymised.
