# Paper 4 — Legislative Churn Across Saudi Legislation

*What Changes, and Where? Legislative Churn Across Saudi Arabian Legislation.*

Fourth paper in the series. Paper 1 (`../corpus_paper/`) describes the corpus;
paper 2 (`../network_paper/`) analyses how instruments cite each other; paper 3
(`../definitions_paper/`) asks whether they share a vocabulary. This one asks
the temporal question the first three left alone: what changes, where, and how
much.

**Venue: *The Theory and Practice of Legislation* (Routledge / Taylor &
Francis)** — requirements verified from the journal's own instructions. See
*Venue* below.

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
| `submission_manuscript_with_author_details.docx` | **Upload 1** — full manuscript, author block and all declarations. |
| `submission_manuscript_anonymous.docx` | **Upload 2** — full manuscript, anonymised and audited. |
| `fig1_churn.tiff` / `fig2_citation_tiers.tiff` | **Upload 3–4** — figures in a format the journal accepts. |

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
  no change at all; the ten most changed hold 38.4% of all changed articles;
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
  prior text, median similarity to the superseded wording is 0.82, but 17 of 87
  score below 0.50. Article 72 of the Judiciary Law shrank from 29 tokens to 6
  and shares three with its predecessor: it used to require the Deputy Minister
  of Justice to be a serving or former judge of a stated grade, and now only
  fixes the rank of the post. The qualification was deleted, not reworded.
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
- Only 175 of 759 article-amendment pairs carry a Gregorian date (23%), and the
  instruments that do are unrepresentative, so **no time series is attempted** —
  the apparent 2021 spike is an artefact of which sources expose dates.
- The cross-reference layer is pattern-extracted; the inter-instrument exposure
  figure rests on 86 resolved references.

## Quality review — what it caught

Run before any venue was chosen, as with papers 1–3. Every numerical claim was
re-derived from the results file and every named instrument and article checked
against the source records. Five defects, one of them serious:

1. **A fabricated example.** The opening invented "article 60 of the Law of
   Sharia Procedure" as a repealed article. Article 60 is *original* and carries
   substantive text on objections to judgments in absentia. The real story is
   better and is now what the paper opens with: Royal Decree M/43 (26/5/1443H)
   issued the 129-article Evidence Law and, in the same instrument, repealed
   articles **101–158** of the Sharia Procedure Law — the whole of its treatment
   of proof, 58 consecutive articles.
2. **A wrong share.** "More than a third" of the Sharia Procedure Law repealed;
   it is 75 of 243, or 30.9% — nearly a third.
3. **A wrong count.** "Four of the twelve most changed instruments are tax or
   tax-adjacent … 147 changed articles." Three are tax instruments and they hold
   118.
4. **The wrong top-ten share.** The table reported 34.4% where the analysis says
   38.4% — the amending-decree share (35.4%) had been conflated with the
   instrument share.
5. **An over-glossed Jaccard.** "Roughly one amendment in five replaces most of
   the article's wording" does not follow from a score below 0.50: for versions
   of similar length, 0.50 means about two-thirds of tokens still in common. The
   paper now states what the threshold means in a footnote and stops claiming
   more than it supports.

Repeal attribution was also made exact while checking: of the Sharia Procedure
Law's 75 repeals, 58 are M/43, 9 are M/101, 1 is M/93, and **7 carry no
repealing decree in the record at all** — an illustration of the transcription
limit the paper already claims.

## Venue

***The Theory and Practice of Legislation*** (Routledge / Taylor & Francis).
The scope match is unusually exact — the journal's own statement of what it
welcomes names *evidence-based drafting*, *pre- and post-legislative scrutiny
for effectiveness and efficiency*, *the utility and necessity of codification*,
and *the role of IT in legislation*. Those are, in order, this paper's method,
its subject, its section on consolidation, and its proposal for a
reverse-reference index. It is also the highest-ranked legislation journal in
the world on Scopus and Scimago, by its own account.

Requirements, all verified from the journal's instructions page:

| | |
|---|---|
| Article type | Original Article |
| **Length** | **no more than 10,000 words** — a ceiling, not a target |
| Abstract | unstructured, 300 words |
| Keywords | 5–15 |
| Citations | **OSCOLA 4th edition** — the style this paper already uses |
| Review | **double anonymous**, two independent reviewers |
| Format | Word; figures supplied separately |
| Figures | 300 dpi colour; preferred formats PS, JPEG, TIFF or Word — **not EPS**, so `make_figures.py` also emits TIFF |
| Submission | **T&F Submission Portal, `rp.tandfonline.com`** — not ScholarOne, and a separate account from a tandfonline.com reading account |
| Required declarations | funding (state "none" if none), disclosure/competing interests, **declaration of generative AI use**, CRediT roles, biographical note (≤200 words), data availability with DOI — all written into the manuscript's declarations section, which the `\ifanon` switch removes from the anonymous build |
| Upload format | **two complete manuscripts** — "with author details" and "anonymous" — not a manuscript plus a separate title page |

The manuscript already conforms on every count that was checkable: 4,706 words
against a 10,000 ceiling, a 260-word abstract against 300, six keywords, OSCOLA
footnotes, "this article" never "this paper", and an `\anontrue` switch for the
anonymised build.

Alternatives considered:

- ***Journal of Empirical Legal Studies*** (Wiley) — double-anonymous,
  free-format, no stated word limit. Rejected on fit rather than quality: JELS
  publishes predominantly causal-inference work, and this paper is descriptive
  with an openly uncontrolled confound.
- ***Statute Law Review*** (Oxford) — the closest scope match of all, but paper
  3 is under review there now.
- **JURIX** — fits without expansion and turns around fast, but conference
  proceedings carry less weight with this paper's intended audience.

One note of transparency rather than concern: Statute Law Review's
Editors-in-Chief lead the same legislative-studies community this journal
serves, so the same readership may see both papers. Different journals,
different publishers, different manuscripts.

## Next steps

- [x] Requirements verified from the journal's own instructions; the earlier
      "10,000–12,000 words preferred" lead was wrong — it came from a generic
      Taylor & Francis PDF. The real rule is **no more than 10,000**, so the
      draft needs no expansion to qualify.
- [x] **Declaration of generative AI use — complete.** Names the tool and
      version, how it was used, and why, as the portal's AI checkbox requires.
      The
      submission portal's AI checkbox confirms that the manuscript names the
      tool *with its version number*, how it was used, and why. The declaration
      guard in `build.py` stays: it refuses to produce the upload files if the
      version placeholder ever reappears.
- [x] Biographical note drafted (90 words, within the 200 limit) from verifiable
      facts only: independent researcher, built the corpus, current lines of
      work. **The author should read it and correct anything that misdescribes
      him** — it is a statement about a person, not about data.
- [ ] Optional but worth considering: the paper sits at under half the length
      ceiling. It qualifies as it stands, but a journal whose norm is longer
      articles may read it as slight. The material that would strengthen it is
      doctrinal — how other jurisdictions publish amendment status, and the
      Evidence Law transfer worked through as a case study in restructuring.
- [ ] Submit at `rp.tandfonline.com` and record the manuscript ID here.
- [ ] Decide how to refer to papers 1–3: they are cited obliquely as "companion
      studies" so the manuscript can be anonymised.
