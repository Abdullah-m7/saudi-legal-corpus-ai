# Paper 5 — The Evidentiary Basis of the Corpus

*What It Took to Read the Law: Access, Provenance and the Evidentiary Basis of
a Digital Legal Corpus.*

Fifth paper in the series, and the one that examines the ground the other four
stand on. Papers 1–4 measured what the legal system contains
(`../corpus_paper/`), how its instruments cite each other (`../network_paper/`),
whether they share a vocabulary (`../definitions_paper/`), and how they change
(`../amendment_paper/`). All four assume the official text was available, and
itself consistent, when it was collected. This one tests that.

**Venue not yet chosen.** The draft is complete and builds.

| File | Purpose |
|---|---|
| `main.tex` | The manuscript — single source for every build. Carries an `\anonfalse`/`\anontrue` switch. |
| `build.py` | Produces the two submission manuscripts and audits them in both directions. |
| `provenance_analysis.py` | Produces every number, and publishes the string classification it rests on. |
| `provenance_analysis_results.json` | Generated results, including the full string-to-classification table. |
| `make_figures.py` | Figures 1 and 2 as PNG, TIFF and EPS. |
| `fig1_access.*` / `fig2_tiers.*` | The two figures. |
| `main.pdf` / `main_anon.pdf` | Typeset builds. |
| `submission_manuscript_with_author_details.docx` / `submission_manuscript_anonymous.docx` | Word builds. |

## Reproduce

```
python3 docs/research/provenance_paper/provenance_analysis.py
python3 docs/research/provenance_paper/make_figures.py
cd docs/research/provenance_paper && python3 build.py
```

## Where the data came from

Two layers the first four papers never touched. Every verified article carries
a **provenance string** written during the build, naming the sources consulted
and how they were reconciled. Every instrument carries a **verification tier**
assigned by hand. The corpus was not built to study its own provenance; the
record exists because building it required deciding, article by article,
whether the text in hand could be relied on.

## Headline findings

Measured over the 11,704 articles whose status field is a provenance statement,
across 200 instruments:

| | Articles | Instruments |
|---|---|---|
| **Official source unreachable** | **20.0%** | **28.0%** |
| **Reached through a web archive** | **20.9%** | **28.0%** |
| Single source only | 10.2% | 10.0% |
| Needed optical or visual reconstruction | 8.2% | 14.0% |
| Defect recorded in the official source | 4.9% | 6.5% |
| *Multi-source cross-verification* | *86.1%* | *87.5%* |

- **Unavailability and archive use overlap by about two thirds** — measured,
  not inferred from the two similar totals. 67.8% of articles whose official
  source was unreachable were recovered through an archive; 65.1% of archive
  use coincided with a recorded unavailability. The archive is mostly supplying
  the official material at a moment when the official channel could not. The
  remainders are not small either: 852 articles used an archive with no
  unavailability recorded, and 754 record an unavailability no archive
  resolved.
- **17.0% of the corpus, by article, has no cross-verified official primary
  source.** Registry-wide by instrument, tiers 3 and 4 together are 76 of 291
  (26%).
- **In four instruments the official record contradicts itself** — across
  **nine articles**: Press Law arts 5, 9, 36, 37, 38, 40 (changed-article
  marker and full amendment log on the portal, pre-amendment text in its own
  displayed body); Law of Engineering Practice art 1 (a three-way divergence,
  the portal's main body reading differently from its own change log at every
  snapshot since 2019); Travel Documents Law art 6 (the portal's amendment log
  omits the decree citation entirely); Environmental Law art 1 (one definition,
  where the per-article log and the main running text disagree). A researcher
  who retrieves once cannot detect any of this.
- **One instrument in seven could not be read by machine without an optical
  pass** — and each pass is an opportunity for a silent error no downstream user
  can detect.

## The finding that indicts this corpus

The provenance field is free text, and **3,704 of 15,408 articles (24%) carry a
value in it that is not a provenance statement at all** — a lifecycle status
such as `UNCHANGED`, and in one case a bare Arabic word, written into the same
field. A project that took provenance unusually seriously still produced a
provenance field meaning three different things.

That is reported rather than quietly cleaned, because it is the strongest
available argument for the paper's own recommendation: provenance needs a
controlled vocabulary and a schema, not a place to write a sentence.

## Quality review — what it caught

Run before any venue was chosen, as with papers 1–4. Every number was
re-derived from the results file and every named instrument checked against its
registry note. Two defects, both of the kind that survive a careless read:

1. **An inflated count.** The paper said the official record contradicts itself
   "affecting 57 articles". A provenance string is attached to every article of
   its instrument, so 57 is the scope of the *verification route*, not of the
   problem. The Environmental Law's string rides on all 49 of its articles while
   its own note records that **48 matched verbatim and one definition did not**.
   The honest figure is **nine articles**, read from each instrument's account
   of its own discrepancy; the 57 is kept in the results file as the upper
   bound it is. The corrected section is also much stronger, because it can now
   name the articles and say what went wrong in each.
2. **A relationship inferred from two marginals.** The paper argued that the
   archive was standing in for unreachable official pages because the two
   totals were close — 20.0% and 20.9%. Two similar totals establish nothing
   about whether the same articles are involved. Measured, the joint is **67.8%
   / 65.1%**: the dominant pattern, but not the near-identity the marginals
   implied, and with 852 and 754 articles respectively in the two remainders.
   This is the same species of error as paper 4's base-rate finding, caught by
   the same habit of computing the joint instead of trusting a coincidence.

## Three corrections the build caught

1. **A prior estimate was wrong by more than double.** An early pass matching
   patterns against the registry's free-text *notes* suggested 47% of
   instruments recorded an unreachable official source. That was regex over
   prose. The disciplined measure over the structured provenance field is
   **28.0% of instruments and 20.0% of articles**. The paper reports the
   correction rather than burying it.
2. **A silent track-resolution bug.** Keying on the directory under `sources/`
   orphaned four fifths of the corpus from its verification tier — `patent` is
   not `patent_law` — so the tier shares were computed on 19% of the data. The
   headline moved from 27.6% to **17.0%** once fixed, and the script now fails
   loudly on an unresolved file instead of dropping it.
3. **The sharpest claim was too broad.** "The official record disagrees with
   itself" first swept in mere staleness against an independent source. Narrowed
   to the portal contradicting *itself* — the record says so, or its own change
   log disagrees with the article it displays — it is **4 instruments**, with
   staleness against another source counted separately (2 instruments, 82
   articles). The article count was corrected again at review; see above.

## The direction of the error is computed, not asserted

The article-level sample does not cover every instrument, and the ones it
misses are not a random draw. Coverage by tier: **87%** (tier 1), **59%** (tier
2), **28%** (tier 3), **73%** (tier 4). Tier 3 — the instruments whose official
source could not be reached at all — is by a wide margin the least represented,
so the 17.0% figure is more likely understated than overstated. The script
computes this so the paper does not have to claim a convenient direction.

## Known limits, stated in the paper

- One corpus, one jurisdiction, one build period. What generalises is the
  method and the question, not the percentages.
- The provenance record was written by the same project whose reliability it
  describes. There is no independent audit, and such a record cannot show what
  it failed to notice.
- Classification is a rule applied to sentences; the full string table is
  published so any assignment can be disputed.
- "Unreachable" is a build-time observation from one collector on one network,
  not a monitoring study — it cannot distinguish an outage from a block or a
  rate limit.

## Next steps

- [ ] Choose the venue and verify its scope, review model, length band and
      submission route against the journal's own instructions. Current draft is
      4,338 words including footnotes. Candidates worth checking: *International
      Journal of Legal Information* (Cambridge), *Legal Information Management*
      (Cambridge/BIALL), *Data & Policy* (Cambridge). The four journals already
      holding papers 1–4 are not available.
- [x] Quality review complete — see above.
