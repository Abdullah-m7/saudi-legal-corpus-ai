# When does a contemporary Saudi court reason beyond the statute book?

The seam finding left one hypothesis standing: that the bench reaches outside
the enacted text where the provision it is citing does not itself supply a
complete rule of decision. This is the test of that hypothesis, and the
verdict is **PARTIAL**. The ordering it predicts is there and it is not
small; it does not survive the test that would make it a claim about
provisions rather than about statute books.

## 1 · Defining completeness without circularity

The tempting version of this study is circular: call an article incomplete
because it attracts fiqh, then report that incomplete articles attract fiqh.
So the classification was made first, from the enacted text alone, blind to
every rate, and frozen in `completeness_gold.json` before the joining script
was written.

Six classes, in priority order, each with an attested example in
`ANNOTATION_GUIDE.md`: **EXTERNAL_REFERRAL** (the text sends the judge to the
Shariah, custom or the maxims), **OPEN_TEXTURED_STANDARD** (the operative
decision turns on a standard the text does not fix), **DUTY_OR_POWER_WITHOUT
_DECISION_RULE**, **DEFINITION_STATUS**, **INSTITUTIONAL_DIRECTIVE** (fixes an
institutional fact completely), **SELF_SUFFICIENT_RULE**.

The frame is the 130 articles the bench cites in at least 30 judgments; four
are empty in the corpus registry and are dropped, leaving **126**. Counts:
48 institutional, 41 self-sufficient, 20 open-textured, 8 definitional, 6
external referral, 3 duty-or-power. Thirteen are recorded as ambiguous.

**Contamination is recorded rather than denied.** For 34 of the 126 the
attraction rate had been printed in an earlier session before the class was
assigned, and the marker «العرف» entered EXTERNAL_REFERRAL after art. 164 had
been read. Every result below is therefore reported twice, on all 126 and on
the 92 whose rate had not been seen.

## 2 · The prediction, tested

Two denominators, because they answer different questions and here they
disagree in magnitude:

| class | arts | judgments | pooled | article median | p25–p75 |
|---|---:|---:|---:|---:|---|
| EXTERNAL_REFERRAL | 6 | 1,686 | 57.5 % | 15.3 % | 0.0–35.9 |
| OPEN_TEXTURED_STANDARD | 20 | 3,461 | **46.4 %** | **34.6 %** | 22.2–54.4 |
| DUTY_OR_POWER_WITHOUT_DECISION_RULE | 3 | 515 | 52.8 % | 48.7 % | — |
| DEFINITION_STATUS | 8 | 2,110 | 39.3 % | 29.4 % | 15.7–48.9 |
| SELF_SUFFICIENT_RULE | 41 | 13,909 | 38.9 % | 32.0 % | 8.3–40.2 |
| INSTITUTIONAL_DIRECTIVE | 48 | 19,206 | **29.8 %** | **11.2 %** | 3.9–33.5 |

On the 92 unseen articles the ordering is preserved and the levels fall:
open-textured 35.5 % pooled and 28.9 % median, self-sufficient 27.2 and 20.4,
definitional 21.4 and 19.4, institutional 20.6 and **6.9**.

Three things follow, and only the first is what the hypothesis predicted.

**Open texture is real and it is the largest single class effect.** An
article whose operative decision turns on an unfixed standard draws
non-statutory authority in about a third of the judgments citing it, roughly
three times the institutional median.

**EXTERNAL_REFERRAL fails.** Its pooled 57.5 per cent is art. 164 and nothing
else; drop the seen articles and it is 14.0 per cent. An article that names
custom in its own text is not, in general, an article beside which courts
reach for fiqh. The strongest textual signal of incompleteness available
turns out to predict nothing.

**Self-sufficiency does not mean silence.** Self-sufficient articles draw
*more* non-statutory authority than institutional ones, by twenty points of
median. Commercial Courts Law art. 29 — a settlement recorded before the
chamber becomes an executory instrument, as complete a rule as the corpus
contains — is the most fiqh-attracting article in the whole table at 85.9 per
cent. What is low is not completeness but institutionality.

## 3 · Within one statute book, the ordering breaks

If the difference between classes were really a difference between statute
books, the between-class comparison would show it and the within-book
comparison would not. Article-level medians, inside each instrument:

| instrument | institutional | self-sufficient | open-textured | other |
|---|---:|---:|---:|---|
| commercial implementing regulation | 5.4 % | 10.6 % | 22.2 % | referral 66.6 |
| evidence law | — | 38.1 % | **46.1 %** | duty 47.3, definition 30.7 |
| commercial courts law | 27.5 % | **64.2 %** | 22.2 % | definition 34.5 |
| sharia procedure law | 18.6 % | 10.3 % | 13.7 % | referral 19.7, duty 69.0 |
| arbitration law | 1.4 % | 11.2 % | — | **referral 0.0** |
| civil transactions law | — | — | 28.9 % | referral 16.7 |

**Two instruments of six behave as predicted.** In the implementing
regulation and the Evidence Law the ordering holds. In the Commercial Courts
Law the self-sufficient articles are the highest by forty points; in the
Sharia Procedure Law the institutional articles beat both others; in the
Arbitration Law the two external-referral articles — including art. 5's «بما
لا يخالف أحكام الشريعة الإسلامية» — draw non-statutory authority in **zero**
of 77 judgments.

The matched comparison agrees with this ambivalence. Pairing each
supplementable article with a complete one from the same instrument and the
same citation band gives 23 pairs, a median difference of **+9.7 points**,
14 positive and 8 negative — a sign test at **p = 0.286**. The direction is
right; the evidence that it is not noise is not there.

## 4 · What the authority is doing: 40 judgments, and a correction

Forty judgments of 1444–1446 whose reasons carry both a statute and something
else, stratified on the leading non-statutory type, read in full
(`hybrid_roles_gold.json`; the same forty are the second reader's packet).

| what the authority does | n |
|---|---:|
| SUPPLIES_THE_DECISION_RULE | 16 |
| CORROBORATES | 8 |
| ALLOCATES_BURDEN_OR_PRESUMPTION | 6 |
| INTERPRETS_OR_DEFINES | 4 |
| UNCLEAR | 4 |
| INDEPENDENT_GROUND | 2 |

**And a correction to the earlier reading.** The exploratory sample of 14
recorded zero ornamental cases. Asked as a deletion test — *could the
sentence carrying the authority be removed without changing the reasoning?* —
and on forty judgments, **9 of 36 codeable cases are deletable**: 25.0 per
cent, 95 % CI 13.8–41.1. The earlier reading was not wrong about what the
authority carried in those fourteen; it was answering by intuition a question
that only an operational test can answer, and the operational test gives a
larger number. This is an **interpretive layer**: explicit written rules, an UNCLEAR
class used in 4 of the 40, provenance recorded per item, and a deletion test
that replaces intuition with an answerable question. It is not held back for a
second human.

The two clearest kinds are worth naming because they are structurally
different. Sixteen judgments take the rule of decision from outside: costs
and مماطلة under art. 164, the authority to judge an absent defendant,
judgment on one witness with an oath, the binding force of the contract. Six
take a presumption: «الأصل بقاء الدين في الذمة» after the Evidence Law has
admitted the document. And one case shows open texture being filled in the
textbook way — Evidence Law art. 97 says the oath goes to «أقوى المتداعيين»
and does not say who that is, and the chamber takes the content from Ibn
Taymiyya: «سواء ترجح ذلك بالبراءة الأصلية، أو اليد الحسية، أو العادة العملية».

## 5 · Different provisions draw different authorities

Not every hybrid is the same hybrid. Share of the judgments citing a class of
article that also carry each kind of authority:

| class | named fiqh | maxim | scripture | judicial principle | custom |
|---|---:|---:|---:|---:|---:|
| EXTERNAL_REFERRAL | **45.7 %** | 4.4 | 13.3 | 7.4 | 3.2 |
| OPEN_TEXTURED_STANDARD | 19.5 | 3.0 | 18.1 | **16.6 %** | 5.2 |
| DUTY_OR_POWER | 28.2 | 1.6 | 8.9 | 19.0 | 2.1 |
| DEFINITION_STATUS | 21.9 | 3.3 | **25.3 %** | 3.4 | 2.7 |
| INSTITUTIONAL_DIRECTIVE | 19.0 | 2.2 | 13.6 | **3.1 %** | 2.6 |
| SELF_SUFFICIENT_RULE | 23.9 | 2.8 | 17.9 | 5.8 | 3.2 |

The sharpest contrast is not fiqh at all. **Open-textured provisions draw
settled judicial practice five times as often as institutional ones** — 16.6
against 3.1 per cent. Where the statute leaves a standard open, what fills it
is most often «المقرر قضاءً», the court's own accumulated practice, not a
jurist. Definitional articles draw scripture more than any other class, which
is what a chamber does when it has a definition and needs a ground.

## 6 · Bench and bar do not feel the same seams

For every article cited at least thirty times by each side, the court's rate
minus the party's:

| class | median delta, strict party | median delta, wide party |
|---|---:|---:|
| EXTERNAL_REFERRAL | +21.0 | −4.0 |
| DEFINITION_STATUS | +16.2 | +7.7 |
| SELF_SUFFICIENT_RULE | +3.7 | −9.0 |
| OPEN_TEXTURED_STANDARD | — | +4.5 |
| INSTITUTIONAL_DIRECTIVE | **−18.7** | **−18.1** |

Overall the median difference is about zero (−0.1 strict, −7.4 wide), so
there is no general "the bench feels it more". The institutional median of
-18.7 points on the strict specification is the widest gap in the table, and
the class pattern is stable
across both party specifications and is the real finding: **beside an
institutional article, litigants bring non-statutory authority far more often
than the court does.** Mandatory pre-filing mediation, art. 58 of the
implementing regulation, is the extreme case — 1.1 per cent for the bench,
25.0 for the party. A filing precondition is, for the court, a fact to be
checked; for an advocate it is something to argue about.

This is the paper's original thesis reappearing one level down. The two
voices differ not only in what they cite but in *where* they feel the need to
reach past it, and the words ARGUED INCOMPLETENESS and ADJUDICATIVE
INCOMPLETENESS are not used here because a median delta of zero does not
support them.

## 7 · The Civil Transactions Law, and the Evidence Law beside it

Post-CTL only (1445–1446), the bench cites 95 distinct CTL articles across
488 judgments, pooled non-statutory rate **25.0 %**. The Evidence Law in the
same window: 84 articles, 4,202 judgments, **34.7 %**.

The mix inverts, and it replicates over both windows:

| | named fiqh | maxim |
|---|---:|---:|
| Evidence Law, 1445–1446 | 20.0 % | 2.5 % |
| Evidence Law, 1442–1446 | 24.4 % | 2.5 % |
| Civil Transactions Law, 1445–1446 | 6.0 % | 6.7 % |
| Civil Transactions Law, 1442–1446 | 6.8 % | 7.6 % |

**The Evidence Law draws named jurists at eight times its maxim rate; the
Civil Transactions Law draws them at about parity.** A plausible reading is
that the code that allocates proof sends a chamber to the fiqh of proof,
while the code of obligations — which itself enacts the maxims in art. 720 —
sends it to a maxim. CTL n is small (488 judgments over two years) and this
is offered as a contrast, not a rate.

Article by article, the CTL's own seams are where its text is thinnest:
art. 120, the general tort clause «كل خطأٍ سبب ضررًا للغير يُلزم من ارتكبه
بالتعويض», is its most-cited article at 116 judgments and 28.4 per cent
non-statutory; art. 720, which enacts «العادة مُحَكَّمة» and «الأمور
بمقاصدها», carries the highest maxim rate of any CTL article, 11.1 per cent.

## 8 · Dilution or displacement: all five denominators

The previous session's claim — statutory prevalence rising, fiqh prevalence
flat — was computed on one denominator. Here it is on five:

| year | judgments | reasoned | fiqh prev., all | fiqh prev., reasoned | fiqh per 1k judgments | fiqh per 1k reasoned | fiqh per statutory citation |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1442 | 10,774 | 240 | 0.4 % | 16.7 % | 7.1 | 320.8 | 0.235 |
| 1443 | 5,280 | 3,161 | 9.7 % | 16.2 % | 191.9 | 320.5 | 0.191 |
| 1444 | 18,812 | 16,435 | 17.7 % | 20.2 % | 341.0 | 390.3 | 0.226 |
| 1445 | 6,800 | 5,982 | 17.9 % | 20.4 % | 353.7 | 402.0 | 0.190 |
| 1446 | 2,478 | 1,209 | 7.9 % | 16.3 % | 153.3 | 314.3 | 0.129 |

They disagree, and the disagreement is the result. **Every denominator that
conditions on the judgment carrying reasons is flat**: prevalence 16.7 → 16.3
with a rise in the middle, and 320.8 → 314.3 fiqh citations per thousand
reasoned judgments. **The two that do not condition on reasons swing
wildly** — 0.4 to 17.9 per cent — and they are tracking the publication of
reasons, not adjudication: 1442 has 10,774 judgments and 240 with reasons.
**Exactly one denominator falls**: fiqh per statutory citation, 0.235 →
0.129, because the bench cites far more statute per judgment than it used to.

That is the honest form of the claim. *Relative to statute*, fiqh is diluted
by a factor of nearly two. *Per judgment that reasons at all*, it has not
moved. Anyone choosing the first denominator alone reports the disappearance
of fiqh from Saudi commercial reasoning; anyone choosing the second alone
reports that nothing has changed. Both are true statements about different
quantities.

## 9 · Silence is a length, not a mode

Of 23,626 reasoned judgments in 1444–1446, 12.0 per cent cite nothing in the
court's own voice. They are half as long: median reasons 805 characters
against 1,634. And silence is almost entirely a phenomenon of the shortest
decile —

| decile of reasons length | up to | silent |
|---|---:|---:|
| 1 | 696 chars | **50.7 %** |
| 2 | 934 | 17.8 % |
| 3 | 1,141 | 11.6 % |
| 5 | 1,540 | 7.8 % |
| 10 | 34,364 | 3.4 % |

Parties still cite something in 42.0 per cent of the silent judgments against
46.4 of the citing ones, so the record is not empty; the court's own reasons
are short. Silent judgments are also over-represented among the paired
appellate records, 24.4 against 16.4 per cent, which is the profile of an
abridged first-instance text.

**Contemporary silence is therefore not a distinct mode of adjudication that
the reforms left behind. It is what a very short set of reasons looks like,
and length in this corpus is partly a publication decision.** The earlier
map's framing of silence as the thing codification displaced is narrowed by
this: what shrank was the share of judgments published without reasons at
all, which is a fact about publication.

## 10 · Appellate association: examined, and declined

4,212 of the 28,090 judgments in the window (15.0 per cent) are records
carrying both a first-instance and an appellate document. The first-instance
reasons were re-extracted for these, restricted to the first document's span,
so that the appellate circuit's own authorities cannot enter the predictor.

| first-instance shape | n | disturbed | 95 % CI |
|---|---:|---:|---|
| statute only | 1,845 | 10.6 % | 9.2–12.1 |
| hybrid | 954 | 11.9 % | 10.0–14.2 |
| non-statute only | 312 | 16.3 % | 12.7–20.9 |
| none | 1,101 | 12.4 % | 10.5–14.4 |

**No association worth reporting.** One of the six pairwise comparisons has
non-overlapping intervals, on the smallest cell, which is what six
comparisons produce. And the slice does not look like the corpus: 26.1 per
cent of it is silent against 12.0 per cent of reasoned judgments overall. The
analysis is recorded and not built on.

## 11 · What a statute-only retriever would miss

Three independently measured shares, multiplied:

- 28.7 per cent of reasoned judgments are hybrid in the court's voice
- 27 of 36 codeable hand-read cases are load-bearing — the sentence cannot
  be deleted without changing the reasoning — 75.0 per cent, CI 58.9–86.2
- so **about 21.5 per cent of reasoned judgments** contain an authority
  outside the statute book that the court used to complete its reasoning

And a harder problem underneath it: of the 9,199 fiqh citations in the
bench's voice in this window, **only 60.0 per cent name a source at all**.
3,676 are «المقرر فقهاً» or «المستقر شرعاً» with no jurist, no book and no
page. Those cannot be retrieved from any corpus, however complete, because
the judgment does not say what to retrieve. A Saudi legal assistant grounded
on the statute book misses a fifth of contemporary reasoning; one grounded on
the statute book plus a fiqh library still cannot resolve two fifths of what
it would need.

## 12 · Novelty

The proposition is not new. It is stated doctrinally in the Saudi literature:
Fuad Shihab Shayyab, *مصادر الحكم القضائي في المنازعات التجارية*, مجلة قضاء
32 (Muharram 1445 / August 2023), writes that the judge resorts to doctrine
and case law «خاصة عندما تكون قواعد الأنظمة وأحكامها غامضة وتحتاج إلى توضيح
أو تفسير» — precisely the hypothesis tested here — and Abdulaziz al-Hammad's
*تسبيب الأحكام القضائية بالقواعد الفقهية*, مجلة قضاء 31 (Shawwal 1444), is a
«دراسة تأصيلية تطبيقية على بعض قضايا المحاكم التجارية»: doctrinal, with
illustrative cases, not a measurement over a corpus.

The nearest empirical relative is Anita Krishnakumar, *The Common Law as
Statutory Backdrop*, 136 Harv. L. Rev. 608 (2022): 602 hand-coded Supreme
Court statutory cases, common law as gap-filler. Same shape of question, a
different legal world, and the predictor there is the case, not a property of
the provision read from its own text.

What is not already in either literature: the article-level outcome measured
over 28,090 judgments rather than illustrated; the predictor derived blind
from the enacted text; the two voices separated so the bench's reach can be
compared with the bar's on the same article; and a negative result where the
doctrine asserts a positive one.

## 13 · Verdict

**PARTIAL.**

Supported: open texture predicts, in the right direction, on both
denominators, on the uncontaminated subset, and with a mechanism visible in
the hand reading. Institutional articles are the quiet ones, by a wide
margin.

Not supported: the class ordering does not hold inside four of six statute
books; the matched-pair test gives p = 0.286; the strongest textual signal of
incompleteness, an explicit referral to the Shariah or custom, predicts
nothing at all outside art. 164; and self-sufficient articles draw more
non-statutory authority than institutional ones, which no completeness story
predicts.

The finding that survives the tests is narrower and sharper than the
hypothesis that provoked it: **what predicts the bench's reach outside the
statute book is not how complete the provision is, but whether it is doing
institutional work at all.** An article that fixes competence, form or a
deadline is decided by its own terms. Everything else — a rule, a definition,
a standard, a referral — sits in the same broad band of 20 to 35 per cent,
and the variation inside that band belongs to individual articles, not to
classes of them.
