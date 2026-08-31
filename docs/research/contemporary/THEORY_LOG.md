# Theories this project has killed

A repository that only records what worked is a repository whose findings
cannot be trusted, because nobody can see what was tried. This file is the
graveyard, kept deliberately. Each entry states the hypothesis as it was held,
the test that was run, what failed, and what survived into the next question.

---

## T1 · Statutory completeness

**HYPOTHESIS.** Non-statutory authority appears where the statutory provision
the court is citing does not itself supply a complete rule of decision. A
provision that states condition, rule and effect needs nothing added; one that
hands the judge an unfixed standard, a duty without an entitlement, or an
explicit referral outside the enacted text does.

**TEST.** 126 articles — every provision the bench cites in at least thirty
judgments and that the registry carries — classified from the enacted text
alone into six classes, blind to every rate, and frozen in
`completeness_gold.json` before the joining script was written. Joined to
23,695 judgments. Reported on two denominators, with and without the 34
articles whose rate had been seen before classification, then re-tested inside
each statute book and on matched pairs.

**FAILURE.** Four ways, and the fourth is fatal to the theory as stated.

1. The class ordering does not hold inside four of six statute books. In the
   Commercial Courts Law the self-sufficient articles are the *highest* by
   forty points of median; in the Sharia Procedure Law the institutional ones
   beat both other classes.
2. Matched pairs — same instrument, same citation band, supplementable against
   complete — give a median difference of +9.7 points on 23 pairs, 14 positive
   and 8 negative, sign test p = 0.286.
3. The strongest textual signal of incompleteness available, an article whose
   own words send the judge to the Shariah or to custom, predicts nothing.
   Outside art. 164 the class runs at 14.0 per cent, and in the Arbitration Law
   art. 5's «بما لا يخالف أحكام الشريعة الإسلامية» draws non-statutory
   authority in zero of 77 judgments.
4. Self-sufficient articles draw *more* non-statutory authority than
   institutional ones, by twenty points of median. No completeness story
   predicts that. Commercial Courts Law art. 29 — a settlement recorded before
   the chamber is an executory instrument, as complete as a rule gets — is the
   single most fiqh-attracting article in the corpus at 85.9 per cent.

**WHAT SURVIVED.** Open texture is real: an article whose operative decision
turns on an unfixed standard runs about three times the institutional median.
But the variable doing the work in that comparison is the comparator. What is
low is not completeness. It is institutionality.

**NEW HYPOTHESIS (T2).** Contemporary adjudication runs on two functionally
different statutory layers — provisions that operate the court, and provisions
that decide the dispute — and the first is self-contained in actual reasoning
in a way the second is not. Tested in `TWO_LAYERS.md`.

---

## What is preserved, and why nothing was renamed

`completeness_gold.json`, `completeness_results.json`, `completeness.py` and
`COMPLETENESS.md` stay exactly as they were written. The new classification in
`adjudicative_function_gold.json` is a **different partition of the same
articles**, made on a different question, and the confusion matrix between the
two is reported rather than hidden: if the new labels were the old labels under
a new name, that matrix would say so and the new theory would deserve nothing.

---

## T3 · The code effect is the article mix

**HYPOTHESIS.** Three quarters of the variance in article supplementation sits
inside codes, and a code is only its articles. So the between-code differences
— arbitration at 4.1 per cent, the Law of Practice at 59.4 — could be entirely
composition: each book contains a different mix of the kinds of provision that
attract supplementation, and "code ecology" would then be a restatement of the
article-level facts under a misleading name.

**TEST.** 134 articles cited in at least thirty judgments. First, variance
shares corrected for chance, because a scheme with 34 cells explains more than
one with 8 for arithmetic reasons alone. Then a sequential fit in both orders.
Then function-matched, citation-matched pairs of articles in different codes,
against the same construction inside one code.

**FAILURE.** Chance-corrected, instrument identity carries as much as the
whole article-property scheme (+18.9 against +18.1) with a quarter of the
cells. Fitted second, it still adds 14.9 per cent of the residual. And two
articles doing the same adjudicative work in the same citation band differ by
a median 20.4 points across codes against 11.0 within one — 19.8 against 7.4
among dispute-deciding articles.

**WHAT SURVIVED.** Article properties matter as much as the code does, and the
two are largely orthogonal: fitting the code first leaves the article
contribution untouched. Neither is the whole story and neither reduces to the
other.

**CONSEQUENCE.** The instrument effect moves from PARTIALLY_EXPLAINED to
IRREDUCIBLE_WITH_CURRENT_DATA. Every reduction available in this corpus —
citation load, case mix, code text, article composition — has now been tested
and none of them absorbs it.
