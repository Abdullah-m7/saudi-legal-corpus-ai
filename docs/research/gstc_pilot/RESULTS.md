# The citation grammar on GSTC_DEV

Every figure here is produced by `evaluate.py` and `ablate.py` and written to
`dev_evaluation.json` and `ablation.json`. None is typed. For the MOJ set and
the comparison between institutions, see `CROSS_SOURCE.md`.

## Where it stands

| stage | correct | per cent | 95% CI |
|---|---|---|---|
| detection | 120/120 | 100.0 | [96.9, 100.0] |
| article number | 118/118 | 100.0 | [96.8, 100.0] |
| paragraph | 62/66 | 93.9 | [85.4, 97.6] |
| instrument | 95/118 | 80.5 | [72.4, 86.6] |
| segment | 90/118 | 76.3 | [67.8, 83.0] |
| **exact** (article + paragraph + instrument) | 92/118 | **78.0** | [69.7, 84.5] |

The instrument stage on this source measured **0.0 per cent [0, 11.7]** before
this work. It is now 80.5 [72.4, 86.6]. The intervals do not overlap.

## What the 0.0 per cent actually was

The earlier reading of that failure was that it decomposed into "two
repairable text-layer defects and one irreducible institutional drafting
convention". The ablation does not support the second half of that sentence,
and it is withdrawn.

Leave-one-out, every condition scored on the same 120 items:

| condition | detection | article | paragraph | instrument | segment | exact | Δ exact |
|---|---|---|---|---|---|---|---|
| everything on | 100.0 | 100.0 | 93.9 | 80.5 | 76.3 | 78.0 | |
| canonicalisation without bidi | 19.2 | 16.9 | 3.1 | 2.5 | 9.3 | 2.5 | −75.5 |
| canonicalisation without tatweel | 100.0 | 100.0 | 93.9 | 79.7 | 76.3 | 77.1 | −0.9 |
| canonicalisation without digits | 100.0 | 100.0 | 93.9 | 80.5 | 76.3 | 78.0 | +0.0 |
| canonicalisation without lam_swap | 6.7 | 5.1 | 0.0 | 2.5 | 1.7 | 2.5 | −75.5 |
| canonicalisation without brackets | 20.8 | 19.5 | 3.1 | 11.9 | 12.7 | 6.8 | −71.2 |
| canonicalisation off entirely | 5.0 | 3.4 | 0.0 | 0.8 | 0.0 | 0.8 | −77.2 |
| grammar without paragraph | 100.0 | 100.0 | 0.0 | 80.5 | 76.3 | 29.7 | −48.3 |
| grammar without instrument | 100.0 | 100.0 | 93.9 | 1.7 | 76.3 | 1.7 | −76.3 |
| grammar without anaphora | 100.0 | 100.0 | 93.9 | 78.8 | 76.3 | 76.3 | −1.7 |
| grammar without attribution | 100.0 | 100.0 | 93.9 | 80.5 | 0.0 | 78.0 | +0.0 |

Read as contribution rather than importance, and as leave-one-out rather than
as a decomposition: the rules are not independent. Three of them each cost
seventy points or more, which cannot add up, because they are three views of
one fault. The digest's text layer emits bidirectional control characters,
transposes the definite article, and carries the contents of a bracket to the
far side of it, and each repair depends on the others having run.

The shape of the answer is not in doubt. **The gap was the representation of
the text, not the institution's drafting.** Three character-level repairs
account for the difference between an extractor that finds nothing and one
that is right about four citations in five. The drafting of these decisions is
not what defeated the extractor. Their PDFs were.

That correction matters beyond this file, because the earlier sentence was
about to become a claim about Saudi tribunals. It would have been a claim
about a font.

The `digits` rule contributes nothing here and is kept anyway: it makes
between 0 and 70 edits across the five documents, so this corpus simply does
not use Arabic-Indic digits much. A rule that costs nothing on the corpus in
hand is not a rule that costs nothing.

### A correction to an earlier version of this table

An earlier run of the same ablation reported −34.8 for both `digits` and
`lam_swap`. Those figures were wrong and were never committed. The evaluation
was caching parses under `id(text)`; a document object can be collected and
its address reused, so one condition read another condition's results. The
cache is now keyed on the text itself. The `digits` row moving from −34.8 to
+0.0 is what caught it: a rule that makes seventy edits in a million
characters cannot be worth thirty-five points, and the implausible number was
the evidence that the harness, not the rule, was being measured.

## What is still wrong, and why

Twenty-six of 118 fail the exact test, and they are not one thing.

**Glyph substitution (3 items).** The customs digest maps whole letters to
other letters: «نظام» is emitted as «نلام», «المؤسسة» as «الملسسة», «إلى» as
«إنى». No gated character repair can invert this, because it is substitution
rather than transposition: repairing ل to ظ everywhere would destroy every
real lam in the document. It needs the font's own character map, which the
text layer does not carry.

**Linearisation (about 6 items).** An instrument name is broken across a line
and the line that follows belongs to a different part of the page. The grammar
completes a broken name only against names the corpus states cleanly, so these
come back as refusals rather than inventions. A refusal scores as an error
here, which is the right price.

**Names that run past their end (about 5 items).** «الالئحة التنفيذية لجباية
الزكاة على أنه" :يتكون الوعاء الزكوي…» -- the name runs into the provision it
introduces because nothing punctuates the join. The gazetteer trims most of
these; what remains is where the corpus never states that name cleanly.

**Semantics against structure (28 items on the segment stage).** A decision
narrates a party's argument inside its own account of the facts and gives it
no heading. The structural answer -- the last heading before this point --
says "facts"; the citation is the party's. Verbs of saying recover most, and
the residue is a limit of a heading-and-cue reading, not a bug to tune away.

**Two refusals that are correct.** One citation gives an article with no
instrument anywhere in the submission. One says «الالئحة ذاتها» where the
thing just named is not a لائحة. The grammar returns nothing for both, the
gold expects nothing for both, and a parser that answered would be
confidently wrong.

## The rule that was almost written wrong

The transposition test asks, per letter and per document, whether the definite
article is written «ال» + letter or «ا» + letter + «ل». For «ل» itself those
two shapes are the same three characters, so the test returns exactly 1.0 in
every document and can never come out either way. «ل» is excluded for that
reason and not for lack of evidence. A rule gated on a measurement with no
possible negative is not gated at all.
