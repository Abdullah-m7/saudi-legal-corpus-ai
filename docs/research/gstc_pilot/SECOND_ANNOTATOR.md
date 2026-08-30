# The second-annotator packet — OPEN_FOR_HUMAN

Every label in this project was written by one reader. That is stated in
`HELD_OUT.md` and it is a real limitation: a schema with a field called
`segment` whose values are `reasoning | party | authorities | quotation |
disposition | summary` is a schema of judgement calls, and a single reader
cannot tell you how much of the agreement between the labels and the parser is
agreement about the text and how much is agreement with themselves.

**No second annotator has read this packet. There is no inter-annotator
agreement figure and none is claimed.** A second language model reading the
same items would not be one either, and is not run.

What exists is the packet, fixed and committed *before* anyone reads it, so
that an agreement figure computed later cannot be a figure about a sample
chosen after the fact.

## What was built

`annotator_packet.py --out <dir>` writes three things:

* `worksheet.txt` — 72 items, each a 1300-character masked window with the
  token marked `⟦…⟧`. No gold label, no parser output, no stratum name, and
  the items shuffled, so the reader cannot tell a hard cell from an easy one.
  Written to the scratchpad, never to the repository, for the reason
  `annotate.py` gives: a wider window is a larger republication of a text
  whose redaction the publisher already got wrong.
* `labels_template.json` — one empty record per item, same eight fields.
* `annotator_packet.json` — committed here: the item list, the seed, and the
  stratum each item came from. This is the audit trail.

## The sample

Seed 7, up to 7 per cell, 11 cells, 72 items. Stratified on what the first
reading found hard, not on subject, so an agreement figure is informative
about the hard cases rather than about the easy majority:

| stratum | pool | drawn |
|---|---|---|
| GSTC / citation, with paragraph | 182 | 7 |
| GSTC / citation, plain | 132 | 7 |
| GSTC / citation, party plea | 97 | 7 |
| GSTC / citation, instrument by anaphora or carry | 67 | 7 |
| GSTC / non-citation | 40 | 7 |
| GSTC / citation, instrument absent | 2 | 2 |
| MOJ / citation, plain | 94 | 7 |
| MOJ / citation, with paragraph | 60 | 7 |
| MOJ / citation, instrument by anaphora or carry | 44 | 7 |
| MOJ / citation, party plea | 29 | 7 |
| MOJ / non-citation | 13 | 7 |

## The protocol the second reader is to follow

Read the window. Do not read the rest of the document; the first reader had
the same window and the comparison is only meaningful if both readers had the
same evidence.

1. **`isCitation`** — true only if an article *number* is recoverable at this
   token. «هذه المادة», «المادة السابقة», «المادة المذكورة», «المادة آنفة
   الذكر», «تلك المادة» are false: they refer to an article, but the number is
   not here. «مادة الفحم الحجري», «مادة السكر» are false: the ordinary noun.
2. **`articleForm`** — the number exactly as printed, brackets and scrambling
   included: `(6)/31`, `(/4أوال ،)2/6(3)`, `السابعة والأربعون`.
3. **`articleNumber`** — the integer. For a dual or a list, the **first**
   member: «المادتين (143)،142» is 142, «المادة الأولى والثانية» is 1.
4. **`paragraph`** — as printed, outermost container first: `ثانيا/1`,
   `1/أ`, `5/ج`. Null if none.
5. **`instrument`** — the name **as the document writes it**, not normalised:
   `اللئحة التنفيذية لجباية الزكاة` if that is what is printed, `نظام الجمارك
   الموحد` if the document stops there.
6. **`instrumentSource`** — `local` (named in the same «من X» attachment),
   `anaphora` («هذه اللائحة», «ذات النظام», the clitic «منها»), `preceding`
   (carried from an earlier citation, «المادة (السادسة)» after «المادة
   (الرابعة) من الالئحة …»), `list_trailing` (named once at the end of a
   coordinated list), `heading`, or `absent`.
7. **`segment`** — whose citation this is. `reasoning` (the tribunal's own
   voice, including its procedural narration), `party` (a plea recited),
   `authorities` (the reporter's «المستند» block), `quotation` (inside quoted
   statutory text), `disposition` (inside the operative order), `summary` (the
   editorial «الملخص» or a publisher's parenthesis).
8. **`notes`** — anything the schema cannot hold.

When the label is genuinely undecidable on this window, write it and say so in
`notes` rather than guessing; a disagreement that both readers flagged is
worth more than a coin-flip agreement.

## What to compute afterwards, and what not to

Per-field agreement (raw and Cohen's κ) on the 72 items, reported per field
and per stratum, never pooled into one number. The fields will not agree
equally — `articleNumber` should be near-perfect and `segment` should not be,
and that difference is the finding.

Do **not** adjudicate disagreements and then report agreement on the
adjudicated labels. Do **not** use the second reading to change the gold that
the held-out results were scored against; those numbers stand as they are, and
a second reading can only tell you how much to trust them, not improve them.
