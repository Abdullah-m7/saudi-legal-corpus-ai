# Two institutions, one harness

Two hand-labelled development sets, built to the same rules and scored by the
same code. Every figure is produced by `matrix.py`, `dev_profile.py` and
`evaluate.py`; none is typed.

    python3 matrix.py

## The matrix

| stage | GSTC_DEV | MOJ_DEV |
|---|---|---|
| detection | 120/120 100.0 [96.9, 100.0] | 119/120 99.2 [95.4, 99.9] |
| article number | 118/118 100.0 [96.8, 100.0] | 113/115 98.3 [93.9, 99.5] |
| paragraph | 62/66 93.9 [85.4, 97.6] | 47/50 94.0 [83.8, 97.9] |
| instrument | 95/118 80.5 [72.4, 86.6] | 86/115 74.8 [66.1, 81.8] |
| segment | 90/118 76.3 [67.8, 83.0] | 72/115 62.6 [53.5, 70.9] |
| **exact** | 92/118 **78.0** [69.7, 84.5] | 85/115 **73.9** [65.2, 81.1] |

GSTC: 5 digests, document split, frame 3,992, sampled 120.
MOJ: 200 judgments, judgment split, frame 692, sampled 120.

The instrument intervals overlap. That is the point of the exercise: before
it, the same measurement was 90.9 per cent on one source and 0.0 on the other,
and nothing in the code could say whether that was a fact about tribunals or
about typesetting.

Three of the six stages cost something to make general. The instrument stage
scored 82.2 on GSTC alone under a rule that took the *longest* attested
prefix of a name; on ministry judgments the same rule scored 39.1, because a
name that has run into the next clause is itself attested and one over-run
then certifies the next. Taking the *shortest* attested prefix, and only from
names the corpus states cleanly more than once, gives 80.5 and 74.8. Nine
points on the source the rule was written for, for thirty-six on the source it
was not.

## What the two institutions do differently

This is the part that bears on claims, and it is larger than the parsing.

| | GSTC | MOJ |
|---|---|---|
| the tribunal's own reasoning | 27 (22.9%) | 93 (80.9%) |
| a party's submission | 41 (34.7%) | 21 (18.3%) |
| the reporter's authorities block | 36 (30.5%) | 0 |
| the disposition's boilerplate | 10 (8.5%) | 0 |
| inside a quoted provision | 3 | 1 |
| summary | 1 | 0 |

The committees' digests are edited: every decision carries a «المستند» block
listing the instruments relied on, and every decision closes with a
boilerplate citation to the rule that makes it final. Ministry judgments carry
neither. So counting "citations per decision" across the two sources counts a
court's reasoning against a reporter's bibliography, and the ratio between
them is an artefact of editorial practice.

**No claim of the form "Saudi courts cite X" survives without this
segmentation.** On GSTC, undifferentiated extraction over-counts the
tribunal's own citations by roughly four times.

Two more differences, smaller but real:

- **Spelled-out article numbers.** 45 of 115 in ministry judgments (39.1 per
  cent) against 21 of 118 in the digests (17.8 per cent). Ministry judges
  write «المادة الثامنة والستين»; the committees' reporter writes «(68)».
- **How the instrument attaches.** The digests coordinate long lists and
  attach the instrument once at the end (24 of 118); judgments almost never
  do (4 of 115) but put the instrument *before* the article more often
  («نظام الإثبات المادة 29»).

## Forms found in one source and not the other

Each of these cost a stage until it was handled, and none of them is
irregular drafting -- they are how one institution writes.

Only in ministry judgments:

- packed pairs, «المادة (57/1)», «المادة 93/1», «المادة (2/ ب )» -- and the
  order is **not fixed**: «93/1» is article 93 paragraph 1 while «2/76» is
  article 76 paragraph 2. The grammar resolves the digit-digit case by taking
  the larger as the article, which holds in every attested case, and flags the
  record `packedAmbiguous` so any count can exclude it.
- hundreds compounded onto ordinals: «الثامنة والستين بعد المئة» is 168,
  «المادة المائتين» is 200.
- the dual «المادتين (1,2)» and «المادتين الأولى والثانية», citing two
  articles in one expression.
- citations to instruments that are not legislation at all: the parties'
  contract («المادة (16) من العقد»), a fiqh code («مجلة الأحكام الشرعية»),
  and an employer's internal work rules.
- no line breaks anywhere in the text, so every line-anchored heading pattern
  matched nothing and the attribution stage reported zero for reasons that had
  nothing to do with attribution.
- anaphoric references to an article with no number at this site at all --
  «المادة سالفة الذكر», «تلك المادة», «هذه المادة». Five of 120. They are
  labelled as non-citations on purpose: there is no article number to recover,
  and a parser that supplied one would be inventing.

Only in the committees' digests:

- the bidi-scrambled bracket, «المادة ( , )5», which is what the authorities
  blocks are made of.
- a transposed definite article, including on the hamza-carrying alefs, so
  that «السابعة والأربعون» reaches the reader as «السابعة واألربعون» and
  parses as article 7.
- three distinct per-document text-layer faults: glyph substitution, spaces
  inserted inside words, glyphs dropped.

## Rules of use

Both TEST sets stay closed. `gstc_test_frozen.json` (5 documents, frame 5,418)
and `moj_test_frozen.json` (200 judgments, frame 795) are opened once, after
the code is frozen and its commit recorded, and not before.
