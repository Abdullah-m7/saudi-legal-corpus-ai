# Representation audit: what the PDF gives back before the parser sees it

`extraction_audit.py` reads every retrieved digest once and records, per
document, what the text *is* before any citation logic runs:
subject, publication year, page count, raw and canonical length, Arabic letter
count, the edit count of each canonicalisation rule, the embedded-font census
(`pdffonts`: total / no-ToUnicode / CID / embedded), a 26-letter frequency
profile, and a corruption verdict.  `engine_compare.py` then re-extracts six
deterministically spread pages of every document with three engines and counts
the tokens a legal reading depends on.

Output: `extraction_audit.json`, `engine_compare.json`.

## Two corruption families, and only one of them is recoverable

**Permutation.** Directional controls, the transposed definite article
(«املادة» for «المادة»), brackets whose contents are carried past the bracket,
tatweel, Eastern/Western digit mixing.  Every character that belongs in the
text is present; only the order is wrong.  This is recoverable from the text
alone, and the five canonicalisation rules do recover it.  31 of the 33
retrieved digests are permutation-only.

**Substitution.** The document's own `/ToUnicode` map assigns the wrong
codepoint to a glyph, so the character that belongs in the text is *absent*.
The first detector is a letter-frequency depression test against a pooled
reference profile built from the documents with more than 50,000 Arabic
letters: a letter is flagged when it occurs at less than a third of its
reference rate.  It flags `11.pdf` (ظ) and `7.pdf` (ظ, ط); in `11.pdf` «نظام»
never appears and «نلام» appears instead.

**Substitution with dropped glyphs.** A third family, and the one that would
have gone unnoticed.  `9.pdf` is 442,315 characters of Arabic that reads as
ordinary committee prose and whose letter histogram is unremarkable — and in
which the string «مادة» does not occur once.  The map sends the *medial* forms
of several letters to nothing, so the damage is spread evenly over the alphabet
instead of collapsing one letter's rate, and it surfaces as words breaking into
pieces: «وعناء عليه» for «وبناء عليه», «باعت اض» for «باعتراض», «املساات نا»
for «المستأنف», «إ مال ة» for «إجمالية».

The second detector is therefore a **fragmentation test**: the share of
whitespace-delimited Arabic tokens that are a single letter.  It separates the
corpus cleanly.

| document | one-letter tokens | «مادة» per 1,000 letters | verdict |
|---|---|---|---|
| 9.pdf | 12.2 % | 0.00 | substitution, dropped glyphs |
| 7.pdf | 9.9 % | 0.00 | substitution, dropped glyphs |
| 11.pdf | 1.5 % | 0.13 | substitution |
| all 30 others | 0.3 – 3.1 % | 0.47 – 1.71 | permutation only |

Neither test alone finds both defects.  The frequency test misses `9.pdf`
entirely; the fragmentation test ranks `11.pdf` below several healthy
documents.  In the two documents the fragmentation test catches, the citation
frame itself is gone — not depleted, absent — which is the operational point: a
citation parser run over `9.pdf` would report zero citations and the number
would be a fact about the font, not about the tribunal.

`9.pdf` was selected into the TEST2 customs stratum on the strength of its
subject and size, before this test existed.  It contributed **zero** of the 400
sampled items, because the sampling frame is occurrences of «مادة» in
canonicalised text and it has none; the customs stratum was drawn entirely from
`CustomsDefenses2024.pdf`.  So the test set is unaffected — but the customs
stratum is thinner than the design intended, and that is reported with the
result rather than repaired after the fact.

This detector was added after TEST2 reading had begun.  It is harness code: it
changes no parser behaviour, no item, and no answer — `9.pdf` contributed
nothing to score either way.  What it changes is the description of the corpus,
and the description was wrong.

The substitution family was traced into the PDF:

* the corrupt spans are drawn in a `Sakkal Majalla` subset;
* the Type0 parent font carries a `/ToUnicode` CMap with 1,624 entries;
* the embedded `/FontFile2` has a `cmap` of 253 entries, all Latin — 1,415 of
  the ToUnicode GIDs have no cmap entry at all, so the font itself supplies no
  Unicode for the Arabic glyphs and there is nothing to check the ToUnicode
  against;
* grouping all 2,922 glyphs by outline hash gives 332 distinct outlines, and
  exactly one group has conflicting ToUnicode values — the blank-outline group
  (space, `!`, `"`, `#`, `$`), i.e. stripped glyphs, not a mapping error;
* aggregated over the document's Type0 fonts, five distinct GIDs map to ظ
  (against two or three in the clean documents), and ظ still occurs 71 times in
  the extracted text.

So the defect is confined to **one defective font subset inside one document**,
not to the publisher and not to a year.  It is not repairable from the file:
there is no internal ground truth to correct the map against, and repairing it
by guessing which Arabic word was meant would be generating legal text rather
than reading it.  Both documents are excluded from sampling and recorded as
excluded.

## Engine comparison

Three engines, the same six pages of each of the 33 documents, counted after
canonicalisation.  There is no ground-truth transcription, so this is not a
character error rate; it counts the tokens that decide a legal reading.

| engine | ARTICLE_TOKEN | ARTICLE_NUMBERED | ARTICLE_ADJACENT | DIGIT_SPLIT | NEGATION | AMOUNT | DATE | bidi/k chars |
|---|---|---|---|---|---|---|---|---|
| pdftotext (poppler 24.02) | 74 | 49 | 46 | 23 | 648 | 104 | 462 | 73.2 |
| PyMuPDF 1.28.2 | 72 | 47 | 44 | 37 | 684 | 9 | 756 | 0.0 |
| mutool (MuPDF 1.23.10) | 0 | 0 | 0 | 11 | 320 | 0 | 464 | 0.0 |

Read this as three findings, not one ranking.

1. **mutool is unusable for this corpus.** It returns the characters of each
   line in reverse: «من» appears 19 times against 2,271 for «نم».  No citation
   survives, which is why ARTICLE_TOKEN is zero.

2. **pdftotext and PyMuPDF recover the same citations.** 74 against 72 article
   tokens, 49 against 47 with a resolvable number, 648 against 684 negation
   particles.  The difference is within the noise of one page boundary.  They
   also produce the *same wrong characters* on `11.pdf`: all three engines give
   «نلام» for «نظام» and «الن يين» for «النبيين».  No engine repairs a broken
   ToUnicode map, because none of them has anything to repair it with.

3. **They differ in representation, not in content.**  PyMuPDF leaves no
   directional controls at all (0.0 per thousand characters against 73.2) and
   places brackets correctly; pdftotext leaves the controls in and carries an
   opening bracket into the middle of a long number — `(1),305,776.21` for
   `(1,305,776.21)`.  The canonicalisation bracket rule already undoes this:
   after canonicalisation, *neither* engine leaves a bracket closed inside a
   longer number (0 occurrences each).  Conversely PyMuPDF breaks a numeric run
   onto its own line, separating an amount from its unit
   (`(\n1,305,776.21\n) \n ريال`), which is why AMOUNT falls to 9 — the number
   is intact but no longer adjacent to «ريال».  Its DATE count is higher (756
   against 462) for the mirror-image reason: the slash-separated date survives
   line breaks that the amount pattern does not tolerate.

## Decision

**The extraction route is not changed before GSTC_TEST2.**

The brief's rule is that a better extractor should become a source adapter
ahead of the parser rather than leaving the parser to repair PDF encoding.  The
measurement does not show a better extractor.  It shows one unusable engine and
two that recover the same legal tokens, each with a different representational
defect that the other lacks, and one corruption family that neither can touch.
Swapping to PyMuPDF would trade a bracket defect that canonicalisation already
repairs for a line-fragmentation defect that nothing currently repairs.

Two further reasons make the change inadmissible *now*, independent of the
measurement: the parser and its extraction configuration were frozen before
TEST2 was built, and TEST2 items had already been read by the time this
comparison finished.  A change to extraction after reading held-out text is the
exact failure the held-out discipline exists to prevent.

Registered as a pre-declared change for a future development cycle, to be
tested on TEST3 and never on TEST2: a PyMuPDF source adapter with a
line-joining step, evaluated against the current route on DEV only.
