# GSTC_TEST_FROZEN, opened once

Opened after `freeze.py` recorded the citation layer at commit `3412fdf`, and
after all 120 items were hand-labelled without reference to any prediction.
`freeze.py --check` confirmed the layer was unchanged at the moment of
labelling and of scoring.

| stage | development | held out | |
|---|---|---|---|
| detection | 100.0 [96.9, 100.0] | **91.7** [85.3, 95.4] | −8.3 |
| article number | 100.0 [96.8, 100.0] | **84.8** [77.0, 90.3] | −15.2 |
| paragraph | 93.9 [85.4, 97.6] | **55.4** [42.4, 67.6] | −38.5 |
| instrument | 80.5 [72.4, 86.6] | **29.5** [21.8, 38.5] | −51.0 |
| segment | 76.3 [67.8, 83.0] | **59.8** [50.6, 68.4] | −16.5 |
| **exact** | 78.0 [69.7, 84.5] | **27.7** [20.2, 36.6] | −50.3 |

The intervals do not overlap on any stage that matters. **The development
number does not transfer.** 27.7 per cent is the estimate that should be
quoted for this extractor on unseen decisions of this publisher; 78.0 is what
it scores on the documents it was written against.

That is the whole reason the split was made before the parser existed, and it
is the result the session turns on. Every earlier number in this project that
was reported without a held-out set should be read as an upper bound.

## What the gap is

Seventy-nine of 112 citations fail the instrument stage. They are not
seventy-nine problems.

| | n |
|---|---|
| truncated: the predicted name is a proper prefix of the true one | 33 |
| refused: the grammar returned nothing | 34 |
| over-run: the true name is a prefix of the predicted one | 3 |
| other | 9 |

Twenty-four of the thirty-three truncations are one collision:

    predicted  نظام الجمارك
    true       نظام الجمارك الموحد

The gazetteer trims an instrument name to the **shortest** name the corpus
states cleanly that begins it. That rule was introduced because it was the
only one that generalised between the two institutions: the longest-match
rule scored 82.2 on GSTC and 39.1 on ministry judgments, and the shortest-match
rule scored 80.5 and 74.8. It has a failure mode neither development set
contained -- **one instrument's name being a proper prefix of another's**.
«نظام الجمارك» is attested cleanly, inside «الالئحة التنفيذية لنظام الجمارك»,
and it begins «نظام الجمارك الموحد».

The development split could not have shown this. The customs digest is one of
the five development documents and contributed three sampled citations; four
of the five held-out documents are customs digests. A document-level split
did exactly what a document-level split is for.

Four more truncations are the same shape on a different instrument:
«الاتفاقية الموحدة لضريبة القيمة المضافة» for «...لدول مجلس التعاون».

## What the fix is, and why it is not in this commit

The trim should prefer a name that is **maximal** among attested names sharing
its prefix: where both «نظام الجمارك» and «نظام الجمارك الموحد» are attested
and one begins the other, the shorter is not an instrument name, it is a
fragment of one.

That change is not made here, because making it and re-scoring on this set
would turn a held-out estimate into a development one. The rule is: this
number stands, the fix is made afterwards, and the next held-out estimate
comes from a set that has not been opened.

**MOJ_TEST_FROZEN remains closed and unlabelled** for exactly that purpose.

## The detection and article stages

Ten detection misses and seven article errors, concentrated in 10.pdf, 111.pdf
and 16.pdf. These are the glyph-substitution and intra-word-space faults
already recorded in `ANNOTATION.md` as unrepairable from the text alone, at a
higher density than the development documents carried.

Eight of the 120 held-out items are not citations at all -- three are the word
«مادة» in its ordinary sense (a smuggled substance, an exported material, and
pregabalin in a table of contents), five are references to an article with no
number at the site («المادة السابقة», «ذات المادة», «هذه المادة»). The
development set contained two such items; the held-out set contains eight.
