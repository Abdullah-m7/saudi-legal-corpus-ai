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

---

## T4 · The code effect is the docket

**HYPOTHESIS.** The codes are invoked in different kinds of dispute, and the
apparent ecology of a statute book is the reasoning style of the cases in
which it happens to appear. Arbitration disputes may be short, agreed-fact,
single-issue matters with no seam to fill; fee disputes the opposite.

**TEST.** Thirteen case features read from the RECITAL only — upstream of the
reasoning that produces the outcome — each validated against a citation target
it was never built from, with nine kept as VALID, three as COARSE_ONLY and one
dropped as UNUSABLE. Then: direct standardisation to a common docket profile
over 72 strata; matched-judgment comparisons on stratum and year; the
ordering inside four reasons-length bands; and a within-judgment contrast of
where each code's own citations sit relative to non-statutory authority.

**PARTIAL FAILURE, AND THAT IS THE RESULT.** The docket explains a real part
of the spread and in one case most of it: the commercial implementing
regulation falls from 48.6 to 32.8 per cent standardised, and the four codes
with near-complete strata coverage converge from a raw 28.1–48.6 range to
28.2–34.9. Chance-corrected, the kind of dispute (+12.20) is nearly as strong
a judgment-level grouping as the set of codes cited (+14.83).

It does not explain the rest. No matched gap disappears and three grow; the
ordering holds inside every reasons-length band, with arbitration at 9.1 per
cent even in judgments whose reasons run past 2,600 characters against a
corpus average of 50.3; and citing the Evidence Law adds about fourteen points
whether or not the recital shows a proof dispute, while a proof dispute
without the code adds four and a half.

**WHAT SURVIVED, AND WHAT DIED.** Survived: the Evidence Law, on the strongest
evidence in the programme — in 2,137 judgments citing both codes, its own
citations sit nearer the fiqh than the Commercial Courts Law's in 74.9 per
cent of them at ±500 characters and 60.8 at the sentence-block level. Died:
the Law of Practice as a code ecology. Raw it is the most supplemented code in
the corpus; locally its citations are the farthest from non-statutory
authority of any code measured, 23.7 per cent against the Commercial Courts
Law's 33.8. Its extreme is a property of fee judgments,
not of its text. The phrase "nine separate settlements with fiqh" is withdrawn
as over-claiming.

**CONSEQUENCE.** Frame decision C — CODE_EFFECT_SURVIVES_DOCKET. The stronger
D holds for the Evidence Law and cannot be established generally, because the
negative case is never observed beside another code in the same paragraph.

**ADDENDUM, after the construct check and the prediction test.** Two things
were added later and both matter. Reading 63 citation neighbourhoods showed
the ±500 window is a poor absolute measure of "the same reasoning
proposition" — 42.9 per cent related overall — but a strongly asymmetric one:
60.0 per cent related beside an Evidence Law citation against 23.1 beside a
Commercial Courts Law citation, so correcting for relatedness widens the
contrast rather than closing it. And a held-out prediction test put the
docket's share of the improvement over a grand mean at 87.2 per cent against
the codes' 12.8. The code effect is real, survives every control, and is the
smaller organising variable for predicting any single judgment.

---

## T5 · One doctrinal companion structure

**HYPOTHESIS.** Each statute book carries a recurring set of named
non-statutory sources — its doctrinal companions — so that knowing the code
tells you which jurists, books and maxims will appear beside it. The
programme's own preferred form of this was answer A: stable, code-specific,
carried by the code.

**TEST.** `companions.py` recorded the identity of every non-statutory mention
in 1444–1446 with its nearest statutory citation at two locality definitions,
its speaker, and a fingerprint of the surrounding wording. 22,969 mentions,
9,842 judgments, 5,552 judgment-by-code units. `companion_analysis.py` ran the
battery: per-code profiles with lift, a constrained null preserving year,
city, authorities per judgment, code exposure and global source frequency; a
within-judgment permutation on the 162 judgments that attach authority to both
the Evidence Law and the Commercial Courts Law; leave-dominant-article-out; a
de-boilerplating falsification; and a held-out classifier that predicts the
code from its sources alone.

**FAILURE.** A is right for one code out of four. The Commercial Courts
Implementing Regulation's environment is article 164's environment and
collapses without it — profile cosine 0.6503 after dropping it, against 0.8813
for the Evidence Law after dropping the two articles that generate more than
half of *its* mentions. The Commercial Courts Law's strongest edge is one
sentence repeated in 294 judgments. The Sharia Procedure Law has no named
companion clearing lift 2 with z 3 at all. And in three of the four codes,
between 70.1 and 79.0 per cent of what the court reaches for names no source
that can be looked up.

**WHAT SURVIVED.** The structure is real and it is not one mechanism. Within a
single judgment — same bench, same dispute, same year — the sources beside the
Evidence Law and the sources beside the Commercial Courts Law separate at
cosine 0.7036 against a within-judgment null of 0.9734, z = -20.76. A held-out
classifier recovers the code from the sources alone at 53.9 per cent against a
constrained shuffle at 29.0. Strip every form of words that circulates in ten
or more judgments — 30.8 per cent of all court-voice mentions — and the
within-judgment separation survives at z = -8.19 and the classifier's macro-F1
at 40.5 against its own control's 18.3.

**CONSEQUENCE.** Answer F, with the assignment: Evidence Law A, implementing
regulation B with D, Commercial Courts Law D, Sharia Procedure Law C. Answer E
is not testable in this corpus — five to twenty-two judgments per code carry
both voices attaching authority to the same code — and is recorded as
untested, not as rejected. The full argument is in `DOCTRINE.md`; the edges are
in `code_source_network.json`.

**WHAT THIS DOES NOT LICENSE.** The word *canon*. The identity universe is
`authority.py`'s vocabulary — five jurists, eight books, six maxim texts, a
set of transmission markers — so every concentration statistic is a statement
about the extractor before it is a statement about the judiciary, and no
"effective canon size" here is read as one.

---

## H1 · AI-legal-salience feedback — a hypothesis record, not a killed theory

This entry is deliberately different from the four above. Nothing is being
buried. A mechanism is being written down, with its first link tested, so that
a future session cannot pretend it was obvious either way.

**THE PROPOSED LOOP.** Retrieval ranking makes some authorities easier to
find; lawyers cite what they find; courts are exposed to what lawyers cite;
courts cite it; the next corpus ranks it higher; retrieval surfaces it more.
If it exists, legal AI does not merely speed up legal research — it changes
which law is visible, cumulatively.

**WHAT CAN BE TESTED NOW.** There are no retrieval logs, so the loop cannot be
observed. But its first link is a precondition that this corpus can test
without any AI at all: does advocacy visibility lead adjudicatory visibility?

**RESULT: THE FIRST LINK IS ABSENT.** Over 11 rolling quarterly folds, the
court's own citation shares correlate at 0.9625 with its shares one quarter
later. The bar's shares correlate at 0.3471 — and at -0.0107 once the court's
own previous quarter is held fixed, positive in 4 folds of 11. Of 460 articles
whose first observed use in both voices falls inside the window, 56.3 per cent
appear in the court's voice first and 20.22 per cent in the bar's. When the
Civil Transactions Law arrived, both voices saw it in the same quarter.

**CONSEQUENCE.** The hypothesis is recorded as PLAUSIBLE_MECHANISM_WITH_A
_MISSING_PRECONDITION, not as established and not as refuted. The measurement
that would refute or support it after legal-AI adoption is specified in
`FORESIGHT.md` section N and frozen in `frozen/ai_transition_baseline.json`.

**WHAT WOULD CHANGE THE VERDICT.** A positive partial correlation sustained
over several folds; or a new code where the bar's citations precede the
bench's by more than a quarter. One caveat cuts the other way and is recorded
with the result: advocacy is measured only where the publisher reproduces it,
and a summarised submission understates the bar.

**SEPARATELY, AND MORE UNCOMFORTABLY.** Across every scalar target in
`foresight.py`, no model beat `last period` or `the mean so far`. Momentum was
actively harmful — DRIFT scored -1.849 mean skill on the named-fiqh share with
one fold at -99.1786. The forecastable structure this corpus has is
persistence plus churn, and the one signal that beats its base rate — entry
into the operational core, lift 5.18 over a base rate of 4.48 per cent — is
again the bench's own prior citation.

**CORRECTION, same session — the channel was wrong.** The entry above was
written while the adoption registry was empty, and it drew a conclusion wider
than its evidence: it treated advocacy as *the* mechanism by which legal AI
would reshape law. A bounded search of official Saudi sources then found seven
adoption events, three of them before the baseline cutoff, and the earliest
verified judicial deployment is not in a law firm at all — it is a knowledge
assistant serving judges and researchers at the Board of Grievances, on the
Board's own subdomain, recognised in the 2024 Digital Government Award.

So the finding is narrowed rather than withdrawn. What the measurement
supports is that PATH 1 — AI retrieval, to advocate citation, to judicial
exposure — has no observable precondition in this corpus. It says nothing
about PATH 2, a court's own research environment changing what the bench
cites, which is the path the registry shows exists and which this corpus, being
Ministry of Justice commercial judgments rather than administrative ones, is in
the wrong institution to observe. Five pathways are now recorded, and three of
them this corpus cannot test at all. The details are in `AI_TRANSITION.md`.

**AND A SECOND CORRECTION, to the retrieval recommendation.** The same report
named the whole-judgment retrieval universe as the architecture worth
preferring, on coverage. Coverage is recall. Pricing the trade the speaker
programme spent the project setting up: the party-only remainder grows the
index by 40.6 per cent, adds 0.0064 of coverage, and 0.0956 of it is ever
cited by a court. The recommendation is withdrawn; the forecast that measured
it is reframed rather than voided, because its definition was valid before any
outcome and voiding it for an inconvenient reading is precisely what the
ledger forbids.

---

## T6 · The de-boilerplating control

**HYPOTHESIS.** Removing every mention whose ±90-character wording fingerprint
recurs in ten or more judgments removes *boilerplate*, so the doctrinal
first-mover result computed without it is the honest one. The previous session
reported the flip to `BAR_FIRST_NOT_WORSE_AFTER_MATCHING` on exactly that
reading, and wrote in `DIFFUSION.md` that "a meaningful part of what looks like
doctrinal leadership is a formula circulating among courts."

**TEST.** Build the wording layer properly and take the control apart. A
mechanical class taxonomy over the 218 circulating formulas — keyword markers,
fixed priority, a merge rule for classes the markers cannot separate, no model
and no labels. Then delete **one class at a time** and re-run the first-mover
result. Then, because none of them flipped it, delete a **random** set of the
same size, twenty seeded draws at four levels.

**WHAT FAILED.** Not one of eleven single-class ablations reproduces the flip —
not procedural wording, not quotation formulas, not doctrinal-rule wording.
Random removal of 90 per cent of circulating formulas flips it in **0.9** of
draws; at 75 per cent, 0.7; at 50 per cent, 0.3. Every arm's matched comparison
rests on **6 or 7 pairs**. The control was removing a quantity of evidence, not
a kind of wording, and a six-pair comparison moves when a quarter of the
evidence leaves regardless of what leaves.

`FLIP_TRACKS_REMOVAL_VOLUME_NOT_WORDING_CLASS`.

**WHAT SURVIVED.** The frozen numbers, untouched — the flip is real and
reproducible. What is withdrawn is the *interpretation* placed on it. The
sentence quoted above is corrected in `DIFFUSION.md` and `FORMULA.md`: the
de-boilerplating control does not show that circulating wording carried the
court-first doctrinal advantage, because it does not distinguish wording from
volume at this corpus size. REPOSITORY_BET_002 stays refused on its other two
reasons, six matched pairs and no temporal folds, which were always the binding
ones.

**AND ONE THING THE PROGRAMME EXPECTED AND DID NOT FIND.** The whole
methodological centre of the follow-up was the possibility that a *judicial
shell* recurs and receives different authorities — that the wording layer and
the source layer are separable. Masking the matched authority string before
hashing takes the corpus from 14958 fingerprints to 14941, and **zero** of the
218 circulating formulas carry a second canonical source. In this corpus there
is no such thing as a source-independent recurring formula. That is why answer
E of the original list — the citation shell — is not in the taxonomy's results.
