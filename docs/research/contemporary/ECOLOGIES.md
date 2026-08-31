# Why do Saudi codes have different authority ecologies?

Three functional taxonomies have now lost out of sample to a label:
procedural/substantive, statutory completeness, institutional-operation
against dispute-decision. Knowing which statute book an article belongs to
predicts how a court will reason around it better than any of them. This
session treats that as the phenomenon rather than the explanation.

**The verdict is IRREDUCIBLE_WITH_CURRENT_DATA**, and what is established is
mostly what the effect is *not*. It is not an artefact of citation load, it
is not the case mix in the crude sense, and it is not predictable from any
measurable property of the code's own text. What it is, on the evidence here,
is a stable difference in how the disputes governed by each code are reasoned
— and one of the extremes turns out to be a single article.

## 1 · The baseline, frozen

Judgments of 1444–1446 in which the court's own reasons cite the instrument;
"hybrid" means those reasons also carry a non-statutory authority.

| instrument | judgments | hybrid | named fiqh | maxim | scripture | judicial principle | custom | concentration |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| law practice law | 345 | **59.4 %** | 24.1 | 0.6 | 21.4 | **22.9** | 2.3 | 99.5 % |
| commercial implementing regulation | 3,533 | 44.8 % | **31.9** | 3.8 | 10.1 | 10.4 | 2.7 | 67.6 % |
| law practice implementing regulation | 87 | 42.5 % | 36.8 | 4.6 | 25.3 | 1.1 | 0.0 | — |
| evidence law | 7,611 | 39.4 % | 24.3 | 2.4 | 12.8 | 6.3 | 3.6 | 79.2 % |
| commercial courts law | 13,254 | 37.1 % | 22.2 | 2.6 | 14.5 | 3.9 | 3.0 | 91.0 % |
| sharia procedure implementing regulation | 191 | 33.0 % | 18.8 | 3.1 | 11.0 | 3.7 | 1.0 | — |
| trade names law | 113 | 31.0 % | 12.4 | 1.8 | 8.8 | 11.5 | 0.9 | — |
| sharia procedure law | 3,854 | 27.7 % | 14.3 | 1.0 | 10.5 | 5.5 | 1.0 | 77.4 % |
| civil transactions law | 357 | 24.9 % | 7.8 | **5.6** | 9.5 | 2.8 | **4.5** | 62.5 % |
| companies law | 634 | 15.8 % | 10.1 | 1.3 | 5.4 | 3.2 | 0.8 | 50.2 % |
| arbitration law | 363 | **4.1 %** | 3.9 | 0.3 | 0.3 | 0.3 | 0.0 | 92.4 % |
| bankruptcy law | 86 | 3.5 % | 2.3 | 0.0 | 1.2 | 0.0 | 1.2 | 77.9 % |

A fourteen-fold spread, and the profiles differ in kind as well as in level.
The largest distance between any two profiles — half the summed absolute
difference between their composition vectors — is bankruptcy against the Law
of Practice at 0.591, with arbitration against the Law of Practice at 0.590.

## 2 · It is not counting

A judgment that cites ten authorities is likelier to contain a non-statutory
one than a judgment that cites two, and codes could differ simply in how much
a chamber cites when it reaches for them. The exposure gradient exists — 30.7
per cent hybrid at one statutory citation, rising to 41.2 at four or five —
but it is not the story. Standardising every code to the corpus-wide
distribution of citation counts moves almost nothing:

| | crude | standardised |
|---|---:|---:|
| law practice law | 59.4 % | 59.2 % |
| commercial implementing regulation | 44.8 % | 42.5 % |
| evidence law | 39.4 % | 37.5 % |
| civil transactions law | 24.9 % | 23.0 % |
| companies law | 15.8 % | 16.2 % |
| arbitration law | 4.1 % | 4.4 % |
| bankruptcy law | 3.5 % | 5.2 % |

The one code that moves materially is the Trade Names Law, 31.0 to 23.6.
Everything else survives.

## 3 · It is not the case mix, in the crude sense

The outcome is a property of the judgment, attributed to every article the
judgment cites, so the whole effect has to come from which judgments cite
which code. That could mean the code is merely a marker for a kind of case.
Two tests.

**Co-citation.** Where two codes appear together, does the rate track the
company?

| | first alone | second alone | both |
|---|---:|---:|---:|
| commercial courts law \| arbitration law | 37.7 % (13,062) | 7.0 % (171) | **1.6 %** (192) |
| commercial courts law \| law practice law | 37.0 % (13,103) | 65.5 % (194) | 51.7 % (151) |
| commercial courts law \| companies law | 37.6 % (12,891) | 10.3 % (271) | 19.8 % (363) |
| sharia procedure law \| law practice law | 26.4 % (3,751) | 52.1 % (242) | **76.7 %** (103) |

Arbitration is dominant-negative: a judgment that cites both the Commercial
Courts Law and the Arbitration Law is *less* hybrid than either alone. A fee
claim in a procedural posture is super-additive at 76.7 per cent. The code
does not simply inherit the reasoning of its neighbours.

**Marginal effect inside a fixed posture.** Almost every commercial judgment
cites the Commercial Courts Law, so conditioning on that is the closest this
corpus comes to holding the kind of case fixed:

| instrument | marginal effect | within CCL-citing judgments |
|---|---:|---:|
| law practice law | +25.0 pts | +14.7 (n=151) |
| commercial implementing regulation | +12.3 | **+13.3** (n=2,288) |
| evidence law | +7.7 | +4.6 (n=5,249) |
| sharia procedure law | −8.9 | −9.3 (n=1,594) |
| civil transactions law | −10.1 | −6.7 (n=213) |
| companies law | −19.7 | **−17.8** (n=363) |
| arbitration law | −31.3 | **-36.1** (n=192) |

Every sign survives, and the largest gets larger. **Among judgments that all
invoke the same procedural statute, touching the Arbitration Law goes with a
36-point fall in the chance the chamber reasons from anything outside the
statute book.** That is not a composition artefact.

## 4 · And it is not in the text of the code

Nine mechanical features per statute book — article count, median article
length, cross-reference density, subparagraph density, definition share,
delegation share, and the share of articles using discretionary language,
open-textured standards, explicit Shariah reference or explicit custom
reference. Eight instruments carry all of them, so these are descriptive
correlations, not estimates:

| feature | r with hybrid rate |
|---|---:|
| open-textured language share | **−0.83** |
| median article words | −0.54 |
| subparagraphs per article | −0.47 |
| cross-references per article | −0.30 |
| explicit Shariah reference share | **+0.01** |
| explicit custom reference share | +0.12 |
| years since commencement | +0.28 |

**H4 fails outright.** A code that refers to the Shariah in its own text is
not a code beside which courts reason from fiqh — r = +0.01. The Arbitration
Law has the highest Shariah-reference share in the corpus, 12.1 per cent of
its articles, and the lowest supplementation rate, 4.1 per cent.

**H4 succeeds in exactly one narrow form.** The share of a code's articles
that mention custom correlates with the rate at which courts cite *custom*
beside it at **r = +0.85**. The Civil Transactions Law leads both. Where the
text predicts behaviour, it predicts the matching authority type and not
supplementation in general.

**H3 has the wrong sign to be the story it looks like.** Open-textured
language correlates *negatively* with supplementation, and strongly. That is
arbitration and bankruptcy — verbose, standard-laden, and almost never
supplemented — against the terse implementing regulation. With eight
instruments it is one or two codes' worth of leverage.

**H1, H2, H5 and H6 do not separate.** Age gives r = +0.28. Domain cannot be
tested: five of the six domains have one instrument each, and the one with
three — procedure — spreads from 27.7 to 44.8 per cent internally. And codes
that codify a field the fiqh had long governed average 32.1 per cent against
29.4 for codes creating a procedure or an institution: **no difference.**

The decisive test is prediction. Holding out each code and predicting its rate
from the others' features gives a mean absolute error of **15.3 points against
a null of 17.2** — the grand mean is almost as good. The Law of Practice is
missed by 37.8 points, the Evidence Law by 19.2.

**No measurable property of a Saudi code predicts how courts will reason
around it.**

## 5 · Within a code, articles vary more than codes do

The variance decomposition settles how much any code-level story can be worth.
Across the 133 articles cited in at least 30 judgments:

| grouping | groups | between | within |
|---|---:|---:|---:|
| instrument | 12 | **23.8 %** | 76.2 % |
| adjudicative function | 5 | 15.7 % | 84.3 % |
| citation frequency band | 7 | 12.4 % | 87.6 % |

Instrument is the best of the three and still leaves three quarters of the
variation *inside* codes. Per instrument, the spread of article rates:

| instrument | articles | mean | sd | range |
|---|---:|---:|---:|---|
| evidence law | 27 | 40.2 % | 13.4 | 6.0 – 76.3 |
| commercial courts law | 27 | 31.9 % | 20.0 | 0.0 – 85.9 |
| commercial implementing regulation | 33 | 19.1 % | 22.1 | 0.0 – 84.4 |
| sharia procedure law | 25 | 23.6 % | 21.7 | 0.0 – 69.0 |
| arbitration law | 7 | 4.2 % | **4.8** | 0.0 – 13.2 |

The Arbitration Law is the only code that is genuinely homogeneous. In the
others, an article at 0 per cent and an article at 85 sit in the same book.

## 6 · The positive extreme is one article

The Law of Practice, at 59.4 per cent, is the strongest ecology in the table
and 99.5 per cent of its citations fall on ten articles. Reading them:

| article | court judgments | hybrid | named fiqh |
|---|---:|---:|---:|
| art. 26 — the lawyer's fee, assessed «بما يتناسب مع الجهد الذي بذله المحامي والنفع الذي عاد على الموكل» | **256** | 62 % | 57 |
| art. 28 — the fee where the lawyer has died | 51 | 65 % | 26 |
| art. 5 | 25 | 88 % | 4 |
| art. 18 | 17 | 12 % | 2 |

**256 of the code's 345 judgments are one provision**, and it is an
open-textured fee-assessment standard that sends chambers to the same مماطلة
and costs material as art. 164 of the implementing regulation. The "ecology of
the Law of Practice" is, in the contemporary commercial corpus, the ecology of
its fee article. A code-level number can be a single provision wearing a
statute's name, and this one is.

The negative extreme is not like that. The Arbitration Law's seven measurable
articles run from 0.0 to 13.2 per cent with a standard deviation of 4.8: its
low rate is a property of the whole book as this corpus sees it, not of one
provision.

## 7 · Which voice carries the ecology

Court and party rates for the same code, and they do not move together:

| instrument | court | party (strict) | court − party (wide) |
|---|---:|---:|---:|
| commercial implementing regulation | 44.8 % | 25.9 % | **+28.1** |
| commercial courts law | 37.1 % | 29.0 % | +16.7 |
| law practice law | 59.4 % | — | +15.1 |
| evidence law | 39.4 % | 48.2 % | −3.4 |
| sharia procedure law | 27.7 % | 36.6 % | −5.8 |
| companies law | 15.8 % | 28.6 % | −8.8 |
| arbitration law | 4.1 % | 16.7 % | −10.9 |
| civil transactions law | 24.9 % | **50.9 %** | **−23.0** |

**The procedural codes are supplemented by the bench; the substantive codes
are supplemented by the bar.** And the sharpest case is the newest code: when
a litigant argues the Civil Transactions Law they bring non-statutory
authority in half the cases and name a jurist in 20.3 per cent; when the
chamber applies the same code it does so in a quarter of cases and names a
jurist in 7.8. The CTL's fiqh ecology is, right now, substantially an
advocacy ecology.

## 8 · These ecologies are not fixed

Year by year, where a code has forty judgments:

| instrument | 1443 | 1444 | 1445 | 1446 |
|---|---:|---:|---:|---:|
| evidence law | 46.0 % | 42.5 % | 36.2 % | **30.9 %** |
| commercial courts law | 34.6 % | 36.6 % | 39.3 % | 32.8 % |
| sharia procedure law | 18.4 % | 25.0 % | 35.0 % | **52.1 %** |
| commercial implementing regulation | 14.7 % | 44.0 % | 47.2 % | 41.6 % |
| companies law | 49.3 % | 17.5 % | 9.8 % | — |
| law practice law | 39.0 % | 58.9 % | 61.8 % | — |
| civil transactions law | — | — | 24.2 % | 25.8 % |

The Evidence Law's supplementation falls by fifteen points across its first
four years; the Companies Law's falls from 49.3 to 9.8; the Sharia Procedure
Law's roughly triples. A "code ecology" is a description of a moment, and the
observatory view in `monitor.py` exists so that the moment can be re-measured
rather than assumed.

The Civil Transactions Law shows **no maturation signal**: 24.2 per cent in
1445 and 25.8 in 1446, on 194 and 163 judgments. Two years is not enough to
say whether early application leans on fiqh and then settles, and this is
recorded as a feasibility result, not a finding.

## 9 · Two consequences that are usable now

**Statute-only retrieval risk is code-specific, and the range is enormous.**
The probability that a court citing an instrument also reasons from something
outside the statute book runs from 4.1 per cent (Arbitration, CI 2.5–6.7) to
59.4 (Law of Practice, CI 54.2–64.5). A Saudi legal assistant grounded on the
statute book is close to complete for arbitration and insolvency work and
misses something load-bearing in three judgments out of five for a fee
dispute. Retrieval architecture that treats the statute book as one corpus of
uniform sufficiency is wrong by an order of magnitude across codes.

**Traceability is also code-specific.** Of the supplementary authority
appearing beside each code, the share that names a source a reader could
follow: sharia procedure implementing regulation 69.9 per cent, sharia
procedure law 65.9, commercial courts law 64.0, evidence law 62.1, commercial
implementing regulation 57.2, civil transactions law 53.3, companies law 48.8,
bankruptcy 40.0, **arbitration 11.1**. The little supplementary authority that
appears beside the Arbitration Law is almost entirely unattributed.

## 10 · Novelty

The gap-filling literature is doctrinal and treats the code as a given: the
question is how judges fill gaps, not why one statute book is filled more than
another. The nearest empirical relatives use statutory *cases* as the unit —
Krishnakumar's *The Common Law as Statutory Backdrop* (136 Harv. L. Rev. 608,
2022) hand-codes 602 Supreme Court cases, and *Cracking the Whole Code Rule*
(96 N.Y.U. L. Rev. 76, 2021) another 532. The comparative-codification and
legal-pluralism literatures compare systems, not statute books inside one
system. And the Saudi literature states the doctrine — a judge resorts to
doctrine where the statute is unclear — without measuring it.

What appears to be new is the object: **the statute book as an empirical unit
of legal reasoning**, with a measurable and different relationship to
supplementary authority, inside a single court system and a single body of
judges. The finding is not "Saudi codes differ". It is that a jurisdiction can
run several codes at once whose relationships to non-statutory authority
differ by more than an order of magnitude, that the difference is not
reducible to the codes' texts, and that it moves within three years.

## 10b · And it is not the mix of articles inside the code

Section 5 left the strongest objection standing. Three quarters of the
variance in supplementation is *inside* codes, and a code is nothing but its
articles, so the whole effect could be composition: perhaps the Arbitration
Law simply contains the kinds of provision nobody supplements and the Law of
Practice the kinds everybody does. That is now tested at the article level,
on the 134 articles cited in at least thirty judgments.

**A grouping with more cells explains more by chance**, and the article scheme
— adjudicative function × citation band × open-textured vocabulary × length —
has 34 cells against the instrument's 8. So every share is reported beside
what the same cell sizes achieve on shuffled rates:

| grouping | groups | observed | chance | excess |
|---|---:|---:|---:|---:|
| **instrument** | 8 | 24.5 % | 5.6 | **+18.9** |
| years since commencement | 7 | 21.0 % | 4.8 | +16.2 |
| adjudicative function | 4 | 16.6 % | 2.4 | +14.2 |
| citation band | 4 | 12.1 % | 2.3 | +9.8 |
| open-textured vocabulary | 2 | 1.7 % | 0.8 | +0.9 |
| whether any litigant ever cites it | 2 | 0.8 % | 0.8 | +0.0 |
| article longer than the median | 2 | 0.3 % | 0.8 | −0.5 |
| the four article properties together | 34 | 44.8 % | 26.7 | +18.1 |

On a like-for-like basis **instrument identity carries as much as the entire
article-property scheme**, +18.9 against +18.1, with a quarter of the cells.
And it is not absorbed by them: fitting article properties first and asking
what the code adds to the residual gives **14.9 per cent**, while fitting the
code first leaves the article properties' contribution untouched at 44.8. The
two are largely orthogonal. Years since commencement is a code-level property
and is collinear with the code itself, so it is not a separate finding.

The direct test is cleaner still. Take two articles doing the **same
adjudicative work** in the **same citation band**, and compare them:

| | pairs | median gap |
|---|---:|---:|
| across two different codes | 722 | **20.4 pts** |
| inside one code | 289 | **11.0 pts** |
| institutional-operation articles, across / within | 610 / 235 | 20.4 / 14.8 |
| dispute-deciding articles, across / within | 97 / 48 | 19.8 / **7.4** |

**Two provisions doing the same job differ nearly twice as much when they sit
in different statute books.** Among dispute-deciding articles the ratio is
almost three to one. Whatever the code carries, it is not the kinds of article
it contains.

One last comparison settles the ranking the programme has been circling.
Splitting the same articles into article-year cells, the year a judgment was
written explains **4.2 per cent** of the variation and the code it cites
explains **13.5 per cent** on those identical cells. Between-code variation is
larger than between-year, larger than between-function, larger than
between-citation-band, and larger than anything the two speaker
specifications produce.

## 11 · Verdict

**IRREDUCIBLE_WITH_CURRENT_DATA.** The previous reading of this evidence was
PARTIALLY_EXPLAINED, and it is revised here because the last available
reduction was tested and failed: the effect is not the mix of articles inside
the code. After every observable feature — of the article and of the code —
instrument identity remains the largest single organising variable in the
data.

Ruled out: the effect is not exposure (standardisation moves nothing), not
crude case mix (the marginal effects survive conditioning on a fixed
procedural posture and the co-citation pattern is dominant, not averaging),
and not the text (leave-one-instrument-out barely beats the grand mean, and
the one strong textual correlation has the wrong sign). One extreme is
decomposed completely: the Law of Practice is one fee article.

Also ruled out, and this is the new one: **article composition**. Instrument
identity survives article properties with its chance-corrected share intact,
and function-matched pairs differ twice as much across codes as within one.

Unexplained: why an arbitration dispute is reasoned without fiqh and a fee
dispute is reasoned with it, when both are heard by the same chambers under
the same procedural law. Nothing measured here answers that, and the
candidates that remain — the kind of question each code makes litigable, the
availability of a settled statutory answer, the publication of which disputes
— are not separable in this corpus.

The honest position: instrument identity is a real, stable, order-of-magnitude
regularity that no property of the instrument explains. It is now a described
phenomenon rather than a residual, which is the most this data can do.
