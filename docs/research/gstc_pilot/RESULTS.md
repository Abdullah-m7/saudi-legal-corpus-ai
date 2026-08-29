# The citation grammar on GSTC_DEV

Every figure here is produced by `evaluate.py` and `ablate.py` and written to
`dev_evaluation.json` and `ablation.json`. None is typed.

## Where it stands

| stage | correct | per cent | 95% CI |
|---|---|---|---|
| detection | 120/120 | 100.0 | [96.9, 100.0] |
| article number | 118/118 | 100.0 | [96.8, 100.0] |
| paragraph | 62/66 | 93.9 | [85.4, 97.6] |
| instrument | 97/118 | 82.2 | [74.3, 88.1] |
| segment | 90/118 | 76.3 | [67.8, 83.0] |
| **exact** (article + paragraph + instrument) | 94/118 | **79.7** | [71.5, 85.9] |

The instrument stage on this source measured **0.0 per cent [0, 11.7]** before
this work. It is now 82.2 per cent [74.3, 88.1]. The intervals do not overlap.

## What the 0.0 per cent actually was

The earlier reading of that failure was that it decomposed into "two
repairable text-layer defects and one irreducible institutional drafting
convention". The ablation does not support the second half of that sentence,
and it should be withdrawn.

Leave-one-out, each condition scored on the same 120 items:

| condition | detection | article | paragraph | instrument | segment | exact | Δ exact |
|---|---|---|---|---|---|---|---|
| everything on | 100.0 | 100.0 | 93.9 | 82.2 | 76.3 | 79.7 | |
| canonicalisation without bidi | 19.2 | 16.9 | 3.1 | 2.5 | 9.3 | 2.5 | −77.2 |
| canonicalisation without tatweel | 100.0 | 100.0 | 93.9 | 81.4 | 76.3 | 78.8 | −0.9 |
| canonicalisation without digits | 60.0 | 59.3 | 54.5 | 47.5 | 54.2 | 44.9 | −34.8 |
| canonicalisation without lam_swap | 59.2 | 58.5 | 54.5 | 47.5 | 53.4 | 44.9 | −34.8 |
| canonicalisation without brackets | 2.5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | −79.7 |
| canonicalisation off entirely | 3.3 | 1.7 | 0.0 | 0.0 | 0.0 | 0.0 | −79.7 |
| grammar without paragraph | 100.0 | 100.0 | 0.0 | 82.2 | 76.3 | 31.4 | −48.3 |
| grammar without instrument | 100.0 | 100.0 | 93.9 | 1.7 | 76.3 | 1.7 | −78.0 |
| grammar without anaphora | 100.0 | 100.0 | 93.9 | 80.5 | 76.3 | 78.0 | −1.7 |
| grammar without attribution | 100.0 | 100.0 | 93.9 | 82.2 | 0.0 | 79.7 | +0.0 |

Read as contribution, not importance, and read as leave-one-out rather than
as a decomposition: the rules are not independent. Removing the bracket repair
costs everything because the scrambled form «المادة ( , )5» is what the
authorities blocks are made of, and removing the bidi repair costs almost
everything because the bracket repair has nothing to work on without it. The
two together are not 157 points; they are one fault seen twice.

What the table does establish is the shape of the answer. **The gap was
overwhelmingly the representation of the text, not the institution's drafting
convention.** Four character-level repairs -- bidi controls, Arabic-Indic
digits, a transposed definite article, and a bracket whose contents were
carried outside it -- account for the difference between an extractor that
finds nothing and one that is right about four citations in five. The drafting
of GSTC decisions is not what defeated the extractor. Their PDFs were.

That correction matters beyond this file, because the earlier sentence was
about to become a claim about Saudi tribunals. It would have been a claim
about a font.

## What is still wrong, and why

Twenty-four of 118 fail the exact test. They are not one thing.

**Glyph substitution (2 items).** The customs digest maps whole letters to
other letters: «نظام» is emitted as «نلام», «المؤسسة» as «الملسسة», «إلى» as
«إنى». No gated character repair can invert this, because the substitution is
not a transposition -- repairing ل to ظ everywhere would destroy every real
lam in the document. It needs the font's own character map, which the text
layer does not carry. These are recorded as unrepairable from the text alone.

**Linearisation (about 5 items).** The name of an instrument is broken across
a line and the line that follows it belongs to a different part of the page.
The grammar refuses to complete a name unless the completion equals a name the
document states unbroken somewhere else, so these come back as refusals rather
than as inventions. A refusal scores as an error here, which is the right
price: the alternative is a plausible instrument name attached to a citation
that never named it.

**Semantics against structure (28 items on the segment stage).** A decision
narrates a party's argument inside its own account of the facts and gives it
no heading. The structural answer -- the last heading before this point -- says
"facts"; the citation is the party's. Verbs of saying recover most of these,
and the residue is a real limit of what a heading-and-cue reading can do, not
a bug to be tuned away.

**Two refusals that are correct.** One citation gives an article with no
instrument anywhere in the submission. One says «الالئحة ذاتها» where the
thing just named is not a لائحة at all. The grammar returns nothing for both,
the gold expects nothing for both, and a parser that answered would be
confidently wrong. The instrument stage is scored so that answering there is
an error, on purpose.

## The rule that was almost written wrong

The transposition test asks, per letter and per document, whether the definite
article is written «ال» + letter or «ا» + letter + «ل». For «ل» itself those
two shapes are the same three characters, so the test returns exactly 1.0 in
every document and can never come out either way. «ل» is excluded for that
reason and not for lack of evidence. A rule gated on a measurement with no
possible negative is not gated at all.
