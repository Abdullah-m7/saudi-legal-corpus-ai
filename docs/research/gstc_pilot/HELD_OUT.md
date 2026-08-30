# The held-out sets, each opened once

Two frozen sets, 120 hand-labelled items each, read without reference to any
prediction and scored once. `freeze.py` recorded the citation layer's commit
and file hashes before each was opened, and `freeze.py --check` confirmed the
layer unchanged at labelling and at scoring.

The two answer different questions, and they answer them differently.

## GSTC_TEST_FROZEN — opened at freeze `3412fdf`

| stage | development | held out | |
|---|---|---|---|
| detection | 100.0 [96.9, 100.0] | 91.7 [85.3, 95.4] | −8.3 |
| article number | 100.0 [96.8, 100.0] | 84.8 [77.0, 90.3] | −15.2 |
| paragraph | 93.9 [85.4, 97.6] | 55.4 [42.4, 67.6] | −38.5 |
| instrument | 80.5 [72.4, 86.6] | 29.5 [21.8, 38.5] | −51.0 |
| segment | 76.3 [67.8, 83.0] | 59.8 [50.6, 68.4] | −16.5 |
| **exact** | 78.0 [69.7, 84.5] | **27.7** [20.2, 36.6] | −50.3 |

No interval overlaps. **The development number did not transfer.**

Seventy-nine of 112 citations failed the instrument stage: 33 truncations, 34
refusals, 3 over-runs, 9 other. Twenty-four of the truncations were a single
collision — «نظام الجمارك», attested cleanly inside «الالئحة التنفيذية لنظام
الجمارك», begins «نظام الجمارك الموحد», and the shortest-attested-prefix rule
stopped at the fragment. Neither development set contained an instrument whose
name is a proper prefix of another's, so neither could have shown it. Four of
the five held-out documents are customs digests; one of the five development
documents is.

## The fix, and the cost of making it

The trim now takes the name the corpus attests **most often** among those that
begin the span, breaking ties by the shorter. Frequency separates the two
cases that length cannot: an over-run is said once or twice, a name is said
hundreds of times, and the customs law in full outnumbers its own fragment.

On the same held-out set the fixed layer scores 53.6 [44.4, 62.5] on the
instrument stage and 49.1 [40.0, 58.2] exact. **That number is no longer a
held-out estimate.** The set informed the fix; quoting 49.1 as though it were
27.7's replacement would be quoting a development number.

Both development sets are unchanged by the fix: GSTC 80.5 / 78.0, MOJ 74.8 /
73.9. The fix costs nothing where the collision does not arise.

## MOJ_TEST_FROZEN — opened at freeze `8f55561`, after the fix

Never used in development, never consulted while the fix was designed.

| stage | development | held out | |
|---|---|---|---|
| detection | 99.2 [95.4, 99.9] | 95.0 [89.5, 97.7] | −4.2 |
| article number | 98.3 [93.9, 99.5] | 94.6 [88.8, 97.5] | −3.7 |
| paragraph | 94.0 [83.8, 97.9] | 85.3 [69.9, 93.6] | −8.7 |
| instrument | 74.8 [66.1, 81.8] | 69.6 [60.6, 77.4] | −5.2 |
| segment | 62.6 [53.5, 70.9] | 52.7 [43.5, 61.7] | −9.9 |
| **exact** | 73.9 [65.2, 81.1] | **68.8** [59.7, 76.6] | −5.1 |

Every interval overlaps. On ministry judgments the grammar generalises: the
held-out estimate is a few points below development and within sampling
error of it.

## Reading the two together

    ministry judgments   development 73.9  ->  held out 68.8   intervals overlap
    committee digests    development 78.0  ->  held out 27.7   intervals disjoint

The same code, the same harness, the same labelling schema. What differs is
the source. Ministry judgments are typed text of one drafting culture, and a
sample of 200 judgments carries its variety; the committees' digests are five
PDFs of two different tribunals with three different text-layer faults, and
five documents cannot carry theirs.

The practical consequence for this project: **a held-out estimate for a
publisher requires held-out documents of that publisher, in numbers.** A
document-level split over five documents tells you honestly that you do not
know; it cannot tell you what the number is. The figure to quote for ministry
judgments is 68.8 per cent exact. For the committees' digests there is no
figure to quote yet — 27.7 is a lower bound from a superseded layer, 49.1 is a
development number, and the honest statement is that the estimate awaits a
larger collection.

## What was measured and what was not

Both held-out sets were labelled by the same reader who labelled the
development sets. No second annotator, so there is no inter-annotator
agreement figure and none is claimed. The labels record what the document
says, including where it is wrong: one ministry judgment cites «مادة 1666» of
the Companies Law in a list running 164, 167, 170, and the label records 1666.
