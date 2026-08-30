# The 34 collections: inventory, and how GSTC_TEST2 was drawn from them

## Why an inventory came first

The first GSTC split was drawn from twelve digests that happened to be the
twelve the pilot had fetched.  It could not say which subjects, years or
encoding families it covered, so when the held-out result came in at 27.7 per
cent exact there was no way to tell how much of that was the parser and how
much was the sample.  This time the population is described before anything is
sampled from it.

`collect.py --rest` fetches every digest the landing page offers and runs the
privacy gate on each before anything about it is kept.
`extraction_audit.py` then reads each one and records what the text is.
`gstc_test2.py` draws the test set from that inventory and writes
`gstc_test2_frozen.json`.

## What is there

34 digests offered, 33 retrieved, 1 failed (an Arabic-named file the server
would not serve), 11 refused by the privacy gate.

The gate matched national/iqama identifiers, bare ten-digit runs, fifteen-digit
VAT numbers and e-mail addresses in: `12.pdf`, `20.pdf`,
`2024-VAT-Decisions.pdf`, `2024CustomsDecisions.pdf`, `333.pdf`, `55.pdf`,
`7.pdf`, `897.pdf`, `PrinciplesCustomsAppealCommittees2024.pdf`,
`PrinciplesZakatAppealCommittees2024.pdf`, `RETT-Decisions-2024.pdf`.  These are
excluded from all sampling.  The cost is real and is recorded here rather than
worked around: the dedicated 2024 VAT decisions volume and the dedicated 2024
customs decisions volume are both refused, so VAT and customs coverage in TEST2
comes from mixed compendia instead.

| document | subject | kind | years | pages | Arabic letters | bidi/k | lam-swap | brackets | fonts w/o ToUnicode | 1-letter tokens | corruption | status | TEST2 frame |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 10.pdf | customs | decisions | 2015–2022 | 693 | 1,092,051 | 69.8 | 20,245 | 3,243 | 8/16 | 0.6 % | permutation only | first split | — |
| 11.pdf | customs | defences | 2015–2022 | 158 | 150,916 | 80.6 | 3,133 | 453 | 7/13 | 1.5 % | substitution | first split | — |
| 19.pdf | customs | decisions | 2023 | 545 | 736,582 | 76.6 | 19,741 | 2,244 | 11/21 | 1.2 % | permutation only | first split | — |
| 2024CustomsDecisions.pdf | customs | decisions | 2024 | 753 | 1,208,421 | 61.0 | 33,375 | 3,847 | 12/23 | 0.9 % | permutation only | privacy-excluded | — |
| 9.pdf | customs | decisions | ? | 186 | 294,674 | 73.7 | 6,824 | 43 | 12/22 | 12.2 % | substitution, dropped glyphs | **TEST2** | — |
| CustomsDefenses2024.pdf | customs | defences | 2024 | 164 | 184,927 | 63.8 | 5,450 | 430 | 11/21 | 1.2 % | permutation only | **TEST2** | 236 |
| PrinciplesCustomsAppealCommittees2024.pdf | customs | principles | 2024 | 205 | 347,073 | 61.0 | 9,496 | 777 | 13/24 | 0.7 % | permutation only | privacy-excluded | — |
| izv.pdf | excise | decisions | 2023 | 196 | 333,070 | 70.0 | 9,254 | 906 | 11/19 | 0.3 % | permutation only | **TEST2** | 500 |
| 14.pdf | income tax | decisions | 2022 | 298 | 489,636 | 76.2 | 12,759 | 1,085 | 16/26 | 0.3 % | permutation only | first split | — |
| 2024-Incometax-Decisions.pdf | income tax | decisions | 2024 | 409 | 802,373 | 63.7 | 21,030 | 1,996 | 9/17 | 0.3 % | permutation only | **TEST2** | 1287 |
| 56.pdf | income tax | decisions | 2023 | 656 | 1,150,437 | 75.1 | 31,536 | 3,438 | 10/20 | 0.5 % | permutation only | **TEST2** | 1556 |
| 55.pdf | real estate transaction tax | decisions | 2023 | 306 | 459,451 | 75.2 | 10,939 | 1,602 | 11/19 | 0.5 % | permutation only | privacy-excluded | — |
| RETT-Decisions-2024.pdf | real estate transaction tax | decisions | 2024 | 133 | 211,661 | 63.5 | 5,004 | 593 | 9/14 | 0.4 % | permutation only | privacy-excluded | — |
| 15.pdf | tax, unspecified | decisions | 2022 | 569 | 881,690 | 66.6 | 24,112 | 2,896 | 15/24 | 1.9 % | permutation only | first split | — |
| 16.pdf | tax, unspecified | decisions | 2022 | 456 | 786,945 | 67.7 | 20,914 | 2,725 | 9/15 | 0.3 % | permutation only | first split | — |
| 20.pdf | tax, unspecified | decisions | 2023 | 769 | 1,273,208 | 72.5 | 35,559 | 3,665 | 11/19 | 0.3 % | permutation only | privacy-excluded, first split | — |
| PrinciplesTaxAppealCommittees2024.pdf | tax, unspecified | principles | 2024 | 209 | 388,959 | 63.7 | 10,350 | 853 | 11/20 | 0.3 % | permutation only | **TEST2** | 468 |
| TaxCommitteesPleas2024.pdf | tax, unspecified | defences | 2024 | 147 | 176,882 | 64.5 | 5,042 | 390 | 10/19 | 0.3 % | permutation only | **TEST2** | 247 |
| 2024-VAT-Decisions.pdf | vat | decisions | 2024 | 279 | 478,225 | 64.5 | 13,685 | 1,238 | 11/22 | 0.3 % | permutation only | privacy-excluded | — |
| 111.pdf | zakat | decisions | 2023 | 739 | 1,249,565 | 73.3 | 33,171 | 3,871 | 9/17 | 1.9 % | permutation only | first split | — |
| 12.pdf | zakat | decisions | 2022 | 729 | 1,068,326 | 81.0 | 26,469 | 2,024 | 12/24 | 0.5 % | permutation only | privacy-excluded, first split | — |
| 13.pdf | zakat | decisions | 2022 | 512 | 868,973 | 73.9 | 21,414 | 2,753 | 7/14 | 0.2 % | permutation only | first split | — |
| 17.pdf | zakat | decisions | ? | 305 | 560,566 | 75.5 | 14,095 | 927 | 16/26 | 0.5 % | permutation only | first split | — |
| 2024-Zakat-Decisions-1.pdf | zakat | decisions | 2024 | 616 | 1,205,408 | 64.7 | 30,989 | 2,768 | 10/18 | 0.5 % | permutation only | **TEST2** | 1138 |
| 2024-Zakat-Decisions-2.pdf | zakat | decisions | 2024 | 278 | 554,378 | 65.1 | 14,277 | 1,493 | 9/16 | 0.2 % | permutation only | **TEST2** | 564 |
| 222.pdf | zakat | decisions | 2023 | 696 | 1,300,258 | 74.0 | 34,955 | 4,386 | 10/18 | 0.6 % | permutation only | **TEST2** | 1530 |
| 333.pdf | zakat | decisions | 2023 | 657 | 1,193,247 | 74.6 | 32,689 | 4,443 | 10/19 | 0.2 % | permutation only | privacy-excluded | — |
| 7.pdf | zakat | decisions | 2020–2021 | 592 | 1,079,086 | 60.4 | 27,127 | 19 | 10/19 | 9.9 % | substitution, dropped glyphs | privacy-excluded | — |
| 8.pdf | zakat | decisions | 2020–2021 | 612 | 1,183,693 | 62.9 | 31,939 | 2,074 | 8/16 | 1.3 % | permutation only | **TEST2** | 569 |
| 897.pdf | zakat | decisions | ? | 213 | 382,289 | 73.8 | 9,960 | 0 | 11/20 | 2.7 % | permutation only | privacy-excluded | — |
| PrinciplesZakatAppealCommittees2024.pdf | zakat | principles | 2024 | 274 | 550,802 | 65.1 | 14,050 | 1,132 | 13/20 | 0.3 % | permutation only | privacy-excluded | — |
| ZakatDefenses2024.pdf | zakat | defences | 2024 | 185 | 234,895 | 67.3 | 6,256 | 765 | 10/19 | 0.2 % | permutation only | **TEST2** | 243 |
| 18.pdf | ? | defences | 2022 | 683 | 913,305 | 76.1 | 24,719 | 3,101 | 13/21 | 0.4 % | permutation only | first split | — |

Two document families the first split never saw are visible here.  The
2024-generation volumes (`2024-*`, `Principles*2024`, `*Defenses2024`,
`TaxCommitteesPleas2024`) are *cleaner*, not differently broken: zero «نلام»
runs, zero kashida runs, «نظام» spelled correctly 616 to 2,540 times each, and
the transposed definite article «املادة» dominating as it does everywhere else.
And `9.pdf` and `7.pdf` are broken in a way no document in the first split was
— see `EXTRACTION.md`.

## No GSTC_DEV2

The brief allows a second development split if the inventory reveals encoding
families the parser has never seen, and prefers no such split if the frozen
architecture can run zero-shot.  The inventory does not reveal a new family
that the parser could be taught: the 2024 generation is easier than what the
parser was built on, and the two defective documents are not learnable — their
text is missing characters that no rule can restore.  So there is no DEV2, and
TEST2 is opened zero-shot against the architecture frozen at `8f55561`.

## How TEST2 was drawn

* **Population.** The 12 privacy-clean digests that no earlier split used.
* **Frame.** Every occurrence of «مادة» with any proclitic, in canonicalised
  text.  The frame is defined on the text, never on parser output: an extractor
  that misses a citation must be able to lose a point for it.
* **Split unit.** The document.  No document appears in two splits.
* **Strata.** Five subject strata — customs, zakat, income tax, excise, and
  mixed tax (which is where VAT lives after the privacy refusals) — with 80
  items drawn from each, seed 2.
* **Size.** 400 items.  The previous held-out interval was 16 points wide,
  which cannot separate a 70 per cent system from an 85 per cent one.  400
  gives roughly ±4.2 points overall and ±9.5 points within a stratum, which
  can.

| stratum | documents | frame | sampled |
|---|---|---|---|
| customs | 9.pdf, CustomsDefenses2024.pdf | 236 | 80 |
| zakat | 222, 2024-Zakat-Decisions-1, 2024-Zakat-Decisions-2, 8, ZakatDefenses2024 | 4,044 | 80 |
| income tax | 56.pdf, 2024-Incometax-Decisions.pdf | 2,843 | 80 |
| excise | izv.pdf | 500 | 80 |
| tax, mixed (incl. VAT) | PrinciplesTaxAppealCommittees2024, TaxCommitteesPleas2024 | 715 | 80 |

Total frame 8,338; sampled 400.

`9.pdf` contributes 0 to the customs frame.  That is not a sampling accident:
its font drops medial letter forms, so the string «مادة» never occurs in it at
all.  The customs stratum is therefore drawn entirely from
`CustomsDefenses2024.pdf`, and customs results below are results for one
publication rather than for a subject.  This is a defect in the design, found
after the set was frozen and reported rather than repaired.
