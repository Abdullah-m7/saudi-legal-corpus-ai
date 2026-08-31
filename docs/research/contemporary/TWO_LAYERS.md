# The law that runs the court, and the law that decides the case

`THEORY_LOG.md` records why statutory completeness failed. What survived it
was an observation about the comparator: institutional articles were the quiet
ones. This tests that as a theory in its own right — that contemporary
adjudication runs on two functionally different statutory layers, and that the
first is self-contained in actual reasoning in a way the second is not.

The verdict is **SUPPORTED, with a bounded effect and one clear rival**. The
rival is that which statute book a provision sits in explains more than what
the provision does.

## 1 · The partition, and its provenance

126 articles — every provision the bench cites in at least thirty judgments
that the registry carries — placed on one question: *does this provision
primarily run the adjudicative process, or help resolve the dispute?*
INSTITUTIONAL_OPERATION 78, DISPUTE_DECISION 34, MIXED 13, AMBIGUOUS 1.

**These labels are not blind.** By the time they were made the annotator had
seen supplementation rates for most of these articles. Rather than manage that
away, every test below is run twice: on the hand labels, and on `ruleLabel`, a
mechanical map into the same four classes from the thirteen functions of
`function.py`, which were assigned from enacted text in an earlier session
before any rate had been computed. The rule map cannot place 48 of the 126 at
all — `function.py` returned "other" — but **where it can place an article the
two label sets agree on 62 of 78, 79.5 per cent.**

## 2 · The two layers behave differently

Judgments citing an article of each class, and whether the court's reasons
also carry a non-statutory authority:

| class | arts | judgments | pooled | article median |
|---|---:|---:|---:|---:|
| INSTITUTIONAL_OPERATION | 78 | 27,398 | 32.1 % | **14.7 %** |
| DISPUTE_DECISION | 34 | 10,160 | 41.4 % | **34.2 %** |
| MIXED | 13 | 3,264 | 55.1 % | 47.2 % |

On the blind rule labels the article-level gap survives almost exactly —
institutional 18.6 per cent median against dispute-deciding 34.2 — while the
citation-weighted gap collapses to nothing, 35.2 against 35.7. That
disagreement is itself a result: **the difference is a fact about provisions,
not about how often they are cited.** Weighting by citations lets art. 16, at
9,190 judgments, speak for the institutional layer, and art. 16 is unusually
noisy for its class.

MIXED being the highest of the three is not a defect of the scheme. Those
thirteen are the provisions where a procedural act carries a dispositive
consequence — default, interrogation, the recorded settlement, res judicata —
and they are exactly where a chamber has to say what follows, which the
statute often does not.

## 3 · Within each statute book

The test the previous theory failed. Article-level medians, hand labels:

| instrument | institutional | dispute | mixed | holds? |
|---|---:|---:|---:|---|
| commercial implementing regulation | 6.5 % (29) | 33.3 % (2) | 72.3 % (3) | yes |
| commercial courts law | 30.5 % (22) | 45.4 % (2) | 54.1 % (2) | yes |
| sharia procedure law | 11.4 % (17) | 25.6 % (3) | 26.3 % (4) | yes |
| evidence law | 45.9 % (5) | 36.4 % (18) | 48.5 % (4) | no |
| arbitration law | 2.7 % (5) | 0.0 % (3) | — | no |

**Three of five, and the two failures are the two smallest institutional
cells** — five articles in the Evidence Law, five in the Arbitration Law. The
completeness theory failed in four of six with contradictions on its largest
cells. This is a materially better showing, and it is not a clean sweep.

The Evidence Law failure is interesting rather than fatal. Its five
institutional articles are the expert-appointment and interrogation-capacity
provisions, which sit inside a code whose whole subject is contested proof;
they are institutional in form and surrounded by dispute-deciding work.

## 4 · What the operational core is made of

Citation-visible legal authority in the court's reasons, 1444–1446 — an
article counted once per judgment citing it. **Not time spent, and not
importance.**

| | judgments | institutional | dispute | mixed |
|---|---:|---:|---:|---:|
| top 10 articles | 23,728 | **68.2 %** | 27.4 % | 4.3 % |
| top 25 | 29,038 | 66.4 % | 24.7 % | 8.9 % |
| top 50 | 32,939 | 63.6 % | 27.5 % | 8.5 % |
| top 100 | 36,428 | **63.9 %** | 26.1 % | 7.8 % |

Stable from ten articles to a hundred: **about two thirds of the statutory
authority visible in contemporary commercial reasoning is law that runs the
court.** Inside that two thirds, by descriptive subtype, jurisdiction is 25.3
points of the top 100 and service and notification 15.1 — one provision in
four that a chamber cites is about whether it may hear the case at all.

## 5 · Which voice carries which layer

The hypothesis was that the bench disproportionately carries institutional
law and litigants the dispute-deciding law. **It is the wrong way round.**

| voice | citations to labelled articles | institutional | dispute | mixed |
|---|---:|---:|---:|---:|
| court reasoning | 40,887 | 67.0 % | **24.8 %** | 8.0 % |
| party, strict | 2,879 | 77.0 % | 18.4 % | 4.3 % |
| party, wide | 13,489 | 88.3 % | 8.5 % | 3.0 % |

Litigants cite *more* institutional law than the bench does, on both
specifications. Part of the wide figure is the recital formula of art. 90 of
the implementing regulation, but the strict specification carries no such
artefact and still puts the bar ten points above the bench.

The transition table says the same thing from inside the judgment. Among the
938 judgments (strict) where both sides cite the same instrument, the movement
from a party's institutional article to the court's dispute-deciding one
outnumbers the reverse **66 to 26**; on the wide specification, 390 to 54.
**When the function changes between the voices, it changes towards the court
deciding the dispute.**

## 6 · Same code, different article — but not a different function

The strongest test of whether this partition explains the paper's central
divergence. Among judgments where court and litigant cite the same instrument:

| transition | strict | wide |
|---|---:|---:|
| institutional → institutional, **different articles** | 427 | 1,641 |
| institutional → institutional, same article present | 297 | 1,790 |
| dispute → dispute, same article present | 88 | 228 |
| institutional → dispute, different articles | 66 | 390 |
| dispute → dispute, different articles | 47 | 100 |
| dispute → institutional, different articles | 26 | 54 |

The dominant cell is the two sides reaching for **the same code, the same
function, and a different provision**. "Same code, different article" is not,
in the main, a disagreement about what kind of law governs. It is two readers
of the same procedural chapter landing on different sections of it.

This is a negative result for the interpretation the phase was designed to
test, and it belongs in the paper as one.

## 7 · This is not procedural-versus-substantive renamed

The corpus already carries a procedural/substantive flag on every statutory
mention. Against the new partition, on the same 126 articles:

| | procedural | substantive |
|---|---:|---:|
| INSTITUTIONAL_OPERATION | 78 | 0 |
| DISPUTE_DECISION | **30** | 4 |
| MIXED | 13 | 0 |
| AMBIGUOUS | 1 | 0 |

**122 of 126 are "procedural".** The old taxonomy is degenerate on the
articles that contemporary commercial courts actually cite, and it cannot
distinguish anything here: an evidence rule is procedural by doctrine and
dispute-deciding by function, and this frame is full of evidence rules. The
new partition cuts *inside* the procedural category, which is the only place
there is anything left to cut.

Against the completeness classes it is equally clearly a different partition:
INSTITUTIONAL_OPERATION spreads across five of the six, and 19 of the 34
DISPUTE_DECISION articles were classed SELF_SUFFICIENT_RULE.

## 8 · How much does it actually explain

Article-level supplementation rate, articles with at least 30 court-citing
judgments. Eta-squared is the share of between-article variance the grouping
accounts for; the hold-out fits group means on every second article by
citation rank and scores the rest against the grand mean.

| stratification | groups | eta² | hold-out MAE | vs grand mean |
|---|---:|---:|---:|---:|
| A procedural / substantive | 2 | **0.005** | 18.19 | 18.29 |
| B completeness (the dead theory) | 6 | 0.156 | 16.51 | 18.29 |
| C institutional / dispute, hand | 4 | **0.166** | 16.02 | 18.29 |
| C institutional / dispute, rule labels | 4 | 0.049 | 18.38 | 18.29 |
| D instrument identity only | 8 | **0.245** | **15.32** | 18.29 |

Three things, and the third is the honest limit of the theory.

**Procedural/substantive explains nothing** — half a per cent of the variance,
and no hold-out improvement at all. Whatever organises supplementation, it is
not that distinction.

**The new partition explains the most of any functional taxonomy**, and more
than the theory it replaced, on the labels that were read.

**Instrument identity beats them all.** Which statute book a provision sits in
accounts for a quarter of the between-article variance and gives the best
out-of-sample error. A functional theory of provisions has to beat that, and
this one does not. The rule-label version does worse than the grand mean,
which says plainly how much of the hand-label performance is the reader
knowing the answer.

## 9 · Each code has its own ecology

If instrument identity is the strongest predictor, the instruments are worth
looking at directly. Judgments where the court cites the instrument,
1444–1446:

| instrument | judgments | hybrid | named fiqh | maxim | scripture | judicial principle | custom |
|---|---:|---:|---:|---:|---:|---:|---:|
| law practice law | 345 | **59.4 %** | 24.1 | 0.6 | 21.4 | **22.9** | 2.3 |
| commercial implementing regulation | 3,533 | 44.8 % | **31.9** | 3.8 | 10.1 | 10.4 | 2.7 |
| evidence law | 7,611 | 39.4 % | 24.3 | 2.4 | 12.8 | 6.3 | 3.6 |
| commercial courts law | 13,254 | 37.1 % | 22.2 | 2.6 | 14.5 | 3.9 | 3.0 |
| sharia procedure law | 3,854 | 27.7 % | 14.3 | 1.0 | 10.5 | 5.5 | 1.0 |
| civil transactions law | 357 | 24.9 % | 7.8 | **5.6** | 9.5 | 2.8 | **4.5** |
| companies law | 634 | 15.8 % | 10.1 | 1.3 | 5.4 | 3.2 | 0.8 |
| arbitration law | 363 | **4.1 %** | 3.9 | 0.3 | 0.3 | 0.3 | 0.0 |
| bankruptcy law | 86 | 3.5 % | 2.3 | 0.0 | 1.2 | 0.0 | 1.2 |

These are not variations on one pattern. The Arbitration Law and the
Bankruptcy Law are cited almost purely on their own terms — 96 per cent
statute-only. The Law of Practice, which governs the fee a lawyer may recover,
is supplemented in three judgments out of five and draws settled judicial
practice at 22.9 per cent, six times the Commercial Courts Law's rate. The
Evidence Law draws named jurists at ten times its maxim rate; **the Civil
Transactions Law is the only major code where the maxim rate (5.6) and the
custom rate (4.5) approach the named-fiqh rate (7.8)** — a code that enacts
«العادة مُحَكَّمة» in its own art. 720 draws custom and maxims beside it.

Two cautions. The Civil Transactions Law has 357 citing judgments in this
window against the Commercial Courts Law's 13,254, and its profile will move.
And these are ecologies of *citation*, not of application: an instrument no
published commercial judgment cites may still govern the transaction.

## 10 · Inside the two recent codes

Post-CTL window (1445–1446), articles with enough observations on either side:

**Civil Transactions Law.** 95 articles cited by the bench across 488
judgments. Its visible core is thin and substantive: art. 120, the general
tort clause, at 116 judgments and 28.4 per cent supplementation; art. 720, the
maxims article, at 72 and the highest maxim rate in the code, 11.1 per cent;
art. 107, termination and damages, at 34. Art. 17 is cited by the bench 26
times and by no litigant at all; art. 95 the other way round, 13 party
citations against 3.

**Evidence Law.** 84 articles across 4,202 judgments, and a much heavier core:
art. 29 alone at 1,618. Its scope clause, art. 1, carries the highest
supplementation in the code at 56.3 per cent with named fiqh at 48.4 — an
article with no rule content in it at all, cited when a chamber is opening a
question of proof it will answer from elsewhere.

And a fact that belongs to the speaker paper: **inside a single code, the two
voices land on the same article in a handful of cases.** Evidence art. 29 is
cited by the bench in 1,618 judgments and by a litigant in 97, and both cite
it in 2.4 per cent of the bench's. The divergence is not an artefact of
comparing across statute books.

## 11 · Verdict

**SUPPORTED, bounded.** The partition is real, it is not the
procedural/substantive distinction renamed, it survives inside three of five
statute books, it holds on the blind label set at the article level, and it
describes an operational core that is two thirds machinery. It explains about
a sixth of the between-article variance in supplementation, more than any
other functional taxonomy tried and thirty times more than
procedural/substantive — and less than simply knowing which code the article
is in.

The theory that should be tested next is therefore not a better taxonomy of
provisions. It is why the instrument is doing so much work.
