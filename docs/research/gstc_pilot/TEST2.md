# GSTC_TEST2, opened once

400 items, 368 of them citations, drawn from twelve digests no earlier split
used, scored against the architecture frozen at `8f55561`. No development set
was built from these documents; nothing in the parser moved between the freeze
and this score. `freeze.py --check` reported `parser unchanged since
8f55561bc215` immediately before the merge and again immediately before the
score.

    python3 evaluate.py    --set gstc_test2
    python3 report_test2.py            # everything below

## The headline, and why it is not one number

| stage | | | 95% CI |
|---|---|---|---|
| detection | 380/400 | 95.0 | [92.4, 96.7] |
| article | 320/368 | 87.0 | [83.1, 90.0] |
| paragraph | 154/228 | 67.5 | [61.2, 73.3] |
| instrument | 250/368 | 67.9 | [63.0, 72.5] |
| segment | 262/368 | 71.2 | [66.4, 75.6] |
| **exact** | **224/368** | **60.9** | **[55.8, 65.7]** |

For comparison, and *only* as history: GSTC_DEV 78.0 (saturated), GSTC_TEST
49.1 (burned — it informed a repair), MOJ_TEST 68.8 (valid for the frozen
architecture at its time). The new interval is 9.9 points wide against the old
16, which is what the sample was sized for: it separates a 60 per cent system
from an 85 per cent one, and the old one could not.

## Detection is not 95 per cent of anything interesting

The set is 92 per cent citations, so an accuracy of 95.0 is barely above the
base rate. Split apart it says something much stronger:

| | | |
|---|---|---|
| precision | 348/348 | **100.0** [98.9, 100.0] |
| recall | 348/368 | 94.6 [91.8, 96.5] |
| true negatives | 32/32 | 100.0 [89.3, 100.0] |

**The parser never once fired on a non-citation.** All 32 gold non-citations —
«مادة الفحم», «مادة السكر», «غش المستهلك في حقيقته ومادته», «هذه المادة»,
«المادة السابقة», «المادة المشار إليها», «المادة ذاتها» — were correctly
declined. Every detection error is a miss, never a false positive.

The 20 misses are not scattered. Eight of them are one construction: the
**packed multi-article address**, an entire citation compressed into one
bracket group and then reordered by the text layer —
`(/4أوال ،)2/6(3)،/5(5)،/و(18)`, `(1)،/9و(3)/57`, `(1)/17(1)/2`, `(/65أ)`,
`(/63ج)`, `(/63أ-ب)`, `(56) ،55`, `(الرابعة ثانيا )1/`. Four more are a
spelled ordinal reached through «البند رقم (2) من المادة الخامسة عشرة», and
two are ordinals the document itself has corrupted — `التاسعة` displaced from
its token by a column reflow, and `الأوسى`, which is `الأولى` with a
substituted glyph. The remaining five are bare bracketed numerals in contexts
the grammar does not open on.

## What the parser does with the instrument

This is the stage that decides whether an output can be read as law, and it
is the stage where a single accuracy figure is most misleading.

| | n | of 368 |
|---|---|---|
| answered, right | 248 | 67.4 % |
| answered, wrong instrument | 30 | 8.2 % |
| — of which the *right name, wrong span* | 19 | 5.2 % |
| — of which *a different instrument* | 11 | **3.0 %** |
| abstained, correctly | 1 | 0.3 % |
| abstained, unnecessarily | 69 | 18.8 % |
| missed the citation entirely | 20 | 5.4 % |

**UNRESOLVED RATE: 88/366 = 24.0 %** — the share of citations where the gold
names an instrument and the parser declines to.

The two rows that matter are the last two of the first block. Of the thirty
answers that do not match the gold string, nineteen name the right instrument
and stop in the wrong place — `نظام ضريبة` for `نظام ضريبة الدخل`,
`قواعد عمل اللجان` for `قواعد عمل اللجان الزكوية والضريبية والجمركية`, or the
converse, running two words past the name into the sentence. A reader is not
misled by those. Eleven answers, **3.0 per cent of all citations**, name a
different instrument, and those are the only outputs that would put a wrong
statute into a sentence.

So the failure mode of this system is silence, not confident error: it
abstains unnecessarily 69 times for every 11 times it is confidently wrong, a
ratio of more than six to one.

## Selective accuracy

| | |
|---|---|
| coverage | **75.5 %** (278 of 368 citations answered) |
| accuracy when answered | **79.9 %** [74.7, 84.1] |
| accuracy over all | 60.6 % [55.5, 65.5] |

Read as one number the system is a 61 per cent system. Read as what it is —
a system that answers three quarters of the time and is right four times in
five when it does — it is usable for exactly the work where an explicit gap is
cheaper than a wrong citation, and unusable where every citation must be
resolved.

## Where the resolution fails

| how the gold recovers the instrument | n | parser right |
|---|---|---|
| local — named in the same «من X» attachment | 323 | 73.1 % |
| anaphora — «هذه اللائحة», «ذات النظام», «منها» | 29 | 37.9 % |
| **preceding** — carried from an earlier citation | **12** | **0.0 %** |
| list_trailing — named once at the end of a list | 2 | 50.0 % |
| absent — not recoverable at this site | 2 | 0.0 % |

Twelve of twelve `preceding` cases are wrong, and eighteen of twenty-nine
anaphora cases. Together those 30 items are a third of the 88 unresolved. The
parser has an anaphora stage; it has no mechanism at all for carrying an
instrument forward from the previous citation, which is what
«كما نصت المادة (السادسة) …» after «المادة (الرابعة) من الالئحة التنفيذية
لجباية الزكاة» requires.

## Segment

| gold segment | n | exact | segment right |
|---|---|---|---|
| reasoning | 150 | 68.7 % | 76.7 % |
| authorities | 92 | 64.1 % | 93.5 % |
| party | 89 | 50.6 % | **34.8 %** |
| quotation | 17 | 47.1 % | 88.2 % |
| summary | 11 | 54.5 % | 54.5 % |
| disposition | 9 | 22.2 % | 100.0 % |

The attribution stage recognises the authorities block (93.5), quoted
statutory text (88.2) and the operative order (100.0), and fails on party
pleadings: it calls only 34.8 per cent of them correctly, and defaults them to
`reasoning`. That is the single most consequential error in the table, because
the claim these tools support is of the form "the tribunal relied on X" — and
a party's plea misfiled as the tribunal's reasoning is exactly the sentence
that would be false.

## The subject difference is a font, not a drafting convention

| stratum | n | exact | coverage | accuracy when answered |
|---|---|---|---|---|
| customs | 75 | 74.7 % | 82.7 % | 90.3 % |
| tax, mixed (incl. VAT) | 71 | 74.6 % | 87.3 % | 83.9 % |
| excise | 74 | 55.4 % | 74.3 % | 74.5 % |
| income tax | 72 | 52.8 % | 70.8 % | 74.5 % |
| zakat | 76 | 46.1 % | 63.2 % | 72.9 % |

Twenty-nine points separate customs from zakat, and the obvious reading —
that zakat committees draft their citations less explicitly — is wrong. The
brief's rule is that a difference between subjects may not be called an
institutional drafting difference until it is shown not to be a text artifact,
and here it is a text artifact.

Per document, the worst result in the whole set is `2024-Zakat-Decisions-1.pdf`
at **25.0 per cent exact and 30.0 per cent coverage**. That document is the
only one of the eleven that spells the executive regulation «اللئحة» — 899
times, against 0 occurrences of «الالئحة». Every other document is the exact
opposite. The same document writes «الخلف» 482 times for «الخالف», against 1
occurrence of the correct form.

| document | «الالئحة» | «اللئحة» | «الخالف» | «الخلف» |
|---|---|---|---|---|
| 2024-Zakat-Decisions-1 | 0 | **899** | 1 | **482** |
| 222 | 827 | 0 | 829 | 0 |
| 56 | 697 | 0 | 641 | 0 |
| 2024-Incometax-Decisions | 597 | 0 | 307 | 0 |
| 2024-Zakat-Decisions-2 | 432 | 0 | 238 | 0 |
| every other document | >0 | 0 | >0 | 0 |

This is a **fourth corruption family**: the standalone alef of a lam-alef
sequence is dropped, so «الالئحة» becomes «اللئحة» and «الخالف» becomes
«الخلف». The instrument gazetteer is built from names the corpus attests, and
this document's spelling of the single most-cited instrument in the corpus is
attested nowhere else, so the parser cannot resolve it and abstains — 70 per
cent of the time.

Remove that one document and the zakat stratum is 30/56 = **53.6 per cent
exact**, not 46.1, and the customs–zakat gap falls from 28.6 points to 21.1.
The remaining gap may still be institutional; this result does not establish
that it is, and the brief's rule says not to claim it.

Neither of the audit's two detectors finds this defect: the letter-frequency
test does not see it (alef stays frequent), and the fragmentation test rates
the document at 2.0 per cent one-letter tokens, in the middle of the healthy
range. The detector that would have found it — registered here as the next
addition to `extraction_audit.py`, not made now — compares each document's
spelling of the corpus's most frequent multi-letter word types against the
corpus mode and flags a document that deviates on any of them.

## Pre-declared, not done

Three changes are now identified and **deliberately not made**, because TEST2
has been opened and any change informed by it would burn TEST3 before it
exists:

1. a lam-alef repair in canonicalisation (`اللئحة` → `الالئحة`), which is a
   deterministic string rewrite and would recover most of `2024-Zakat-Decisions-1`;
2. an instrument-carry mechanism for the `preceding` case, which is 12 of the
   88 unresolved and currently scores zero;
3. a party-plea cue set for the attribution stage, which is at 34.8 per cent
   and is the error that would make a false sentence.

Each is to be developed on DEV only and tested on a TEST3 built from documents
none of these results touched.
