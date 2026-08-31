# One Judgment, Two Legal Languages: Why Citation Measurement Needs Speaker Attribution

*Evidence from contemporary Saudi commercial adjudication*

**Abstract.** Empirical legal research counts citations in judgments and reads
the counts as evidence about judicial reasoning. A judgment, however, is a
multi-voice document: published decisions contain the parties' pleadings as
well as the court's reasons. We ask whether that matters — whether the two
voices invoke *systematically different kinds* of legal authority, so that an
unsegmented count measures a blend rather than a court. Using 28,090
contemporary Saudi commercial judgments (1444–1446 AH) and a hand-validated
taxonomy of nine authority types, we find that six of the nine differ
systematically between the bench's own reasons and the litigants' arguments,
and three do not. Litigants invoke the parties' contract at 11.7–17.2 times
the rate the bench does, maxims of fiqh at 2.9–4.3 times and commercial custom
at 2.9–4.0 times; the bench invokes named fiqh authority, settled judicial
principle and its own discretion at 1.5–4.8 times the litigants' rate.
Statute, Qur'an and hadith show no stable direction and serve as negative
controls. The divergence is not an artefact of the bench citing procedure: it
widens when the comparison is restricted to non-statutory authority, where no
mention can be procedural by construction. Within the same dispute, the rate
at which the bench answers with statute is flat across everything a litigant
can raise (lift 0.95–1.03), and in 79.7 per cent of paired judgments the two
sides share no article at all. We conclude that speaker attribution is a
prerequisite for the validity of citation measurement, not an optional
refinement of it, and that the correction is available: role segmentation
already exists in the legal-NLP literature, built for other purposes.

---

## I. Introduction

Consider a study that counts how often courts in some jurisdiction cite
statutes, and reports the result as a fact about judicial reasoning. The
counting is done over published judgments. In most jurisdictions those
judgments recite the parties' claims and arguments before the court gives its
reasons, and the recitation is part of the same document and the same file.
The study therefore counts, in one number, at least four things: what a
claimant argued, what a defendant answered, what the court narrated, and what
the court decided.

This is a measurement-validity problem before it is a natural-language
processing problem. If the parties and the court invoke the same kinds of
authority in roughly the same proportions, the blend is a noisy measure of
judicial reasoning and the noise averages out with sample size. If they do
not, the blend is a measure of something else, and no amount of data fixes it.

Which is it? The question is empirical and, so far as we can find, unasked.

We ask it in a setting where it can be answered: Saudi commercial judgments,
published by the Ministry of Justice with structural headings that separate
the statement of facts from the court's reasons, and carrying an unusually
wide range of authority types — statute, the parties' contract, named works
of fiqh, maxims of fiqh, Qur'an, hadith, settled judicial principle,
commercial custom, and the court's own named discretion.

The answer is that it matters, and it matters unevenly. Six of nine authority
types differ systematically between the two voices. Three do not. The single
largest effect is the parties' own contract, which is roughly an order of
magnitude more prevalent in litigants' arguments than in the bench's reasons
under both of the two speaker specifications we report. The three types that
do not differ — statute, Qur'an, hadith — are the reason we believe the other
six: a classifier that separated any two populations would not leave a third
of its categories flat.

The contribution is methodological, and its scope is stated rather than
implied. We do not show that the same divergence exists elsewhere. We show
that it exists here, that it is large, that it survives every conditioning we
can apply, and that the machinery to check it elsewhere already exists.

## II. Why speaker identity matters, and what the literature has done with it

Three literatures touch this question and none of them asks it.

**Empirical citation studies** count what courts cite. Work on judicial
citation practice measures which authorities appellate courts rely on, and
finds — for example, in a decade of Indiana appellate decisions — that
judicial opinions dominate, statutes follow, and appellate *briefs* are
themselves the third or fourth most-cited category, at 9.7 to 14.4 per cent.
That literature has therefore noticed that briefs enter opinions. It counts
citations *to* briefs. It does not compare the composition of authority
invoked *by* the brief with the composition invoked *by* the court. Related
work on bias in judicial citation asks which judges get cited and why, which
is a question about the identity of the cited, not of the citer.

**Legal NLP** has built exactly the segmentation this problem needs, for other
reasons. Rhetorical-role classification of judgments is an established task,
with public datasets and label sets that explicitly separate *Arguments of
Petitioner* and *Arguments of Respondent* from *Reasoning*; segment schemes
such as the five-way Procedure / Fact / Reasoning / Decision / Tail split are
standard, and the Fact segment is documented as containing the parties'
arguments. The purpose in that literature is summarisation, retrieval and
judgment prediction. To our knowledge the segmentation has not been turned
back on the measurement question: *given* that the roles can be separated,
does failing to separate them bias what we think we are measuring?

**Socio-legal scholarship** has the conceptual distinction and little
quantitative work behind it. German procedure formalises the division — the
*Tatbestand* states the parties' submissions, the *Entscheidungsgründe* give
the court's reasons and are explicitly an engagement with the
*Parteivortrag* — yet recent German *Rechtssoziologie* is described in its own
survey literature as containing few empirical studies of judicial
decision-making behaviour. Arabic legal scholarship on *tasbīb* (the reasoning
of judgments) is doctrinal and analytical rather than quantitative.

So the pieces exist separately: the observation that briefs reach opinions,
the tooling to separate roles, and the doctrinal distinction between the
voices. What is missing is the measurement claim that joins them.

## III. Setting

Saudi Arabia has codified rapidly. The judgments studied here are governed by
the Commercial Courts Law (Royal Decree M/93 of 15/08/1441 AH), the Evidence
Law (M/43 of 26/05/1443) and, latterly, the Civil Transactions Law (M/191 of
29/11/1444) — dates taken from the judgments themselves rather than from
secondary sources. Alongside the codes, courts continue to reason from fiqh:
from named jurists and their works, from *qawāʿid fiqhiyya*, and from Qur'an
and hadith. That coexistence is what makes the setting useful here. A
jurisdiction whose courts and litigants both cite only statutes and cases
would give this question little room.

Published judgments follow a conventional shape: الوقائع (the facts, in which
the parties' claims and pleadings are set out, frequently quoted at length),
الأسباب (the reasons), and حكمت الدائرة (the operative order). The two voices
therefore coexist in one document by design, and a published record sometimes
concatenates a first-instance judgment with the appellate judgment that
followed it.

We make no claim about Saudi adjudication generally. The corpus is
overwhelmingly commercial: of 50,666 published judgments, roughly 95 per cent
come from commercial courts and 28 from personal-status courts. Selection into
publication is not random, and the share of judgments published with their
reasons rose from about 2 per cent to about 88 per cent across the span we
observe. Every figure below is conditional on that.

## IV. Data and measurement

**Corpus and windows.** 50,666 published judgments. We define four
contemporary windows and report all four: `contemporary_5y` (1442–1446 AH,
44,144 judgments), `contemporary_3y` (1444–1446, 28,090), `post_Evidence`
(1443–1446, 33,370) and `post_CTL` (1445–1446, 9,278). None is balanced and
none is made balanced; each states its own composition, including the share
carrying reasons, which is the selection control everything else is
conditioned on. Two trailing years (1447–1448, 90 and 277 judgments) are
excluded as the leading edge of a collection still filling.

**Authority taxonomy.** Nine types: statute or regulation, the parties'
contract, named fiqh source, legal maxim, Qur'an, hadith, settled judicial
principle, custom, and named judicial discretion. Thirteen rules, each with an
identifier that survives into the results, so that a disagreement between a
human reading and the classifier can be localised to a rule. The marker
vocabulary was not guessed: 36 candidate markers were first counted across all
50,666 judgments and the four that scored zero were dropped, on the principle
that a zero from a broken search is indistinguishable from a finding.

**Quoted passages are held apart.** Judgments quote the statutes they apply,
at length. Article 164 of the commercial implementing regulation directs
courts to weigh «العرف، أو العادة المستقرة» — custom, or settled practice —
and is quoted in tens of thousands of judgments. Counting those words as the
court invoking custom is not a small error; it was the largest single error in
our first validation sample. Quotation spans are detected and every mention
inside one is reported separately throughout.

**Speaker attribution, and why we report two specifications.** Inside الأسباب
the author is the bench by construction. For the parties we report two
specifications, because validation showed that no single one is safe:

- **strict** — a mention in the facts segment with a party cue near it. High
  precision, low recall.
- **wide** — every mention in the facts segment. High recall, low precision:
  it sweeps in the court's own narration.

The true party population lies between them. We claim only what survives both.

**Validation.** Three hand-read gold samples, each with a declared role.
Sample 1 (126 rule hits and 80 randomly drawn reasoning sentences) was
development: it found six classifier defects and is burned by having driven
their repair. Sample 2, an independent draw after the repairs, validated the
*types*: 126 of 126 correct. Sample 3 was a final gate whose arms, sizes and
pass criteria were written down before any label was read; it tested the
*voice* assignment, which the headline claim depends on and which had never
been checked.

The gate failed one of its three arms, and that failure is why this paper
reports two specifications and three fewer claims than its first draft. The
bench's own reasons were attributed correctly 12 times in 12 and the strict
party bucket 10 in 12 — both above their thresholds — but the facts segment
was mislabelled 5 times in 12, each time a party pleading carrying no cue near
the mention, and four of those five were statute or maxim: precisely the
direction that could manufacture a divergence. Under the pre-declared rule the
result was not patched. It was recomputed under both specifications, and
**three of its nine contrasts were withdrawn.**

**Parser accuracy is not the contribution and is not claimed as one.** Six
citation forms remain invisible to the extractor, chiefly the anaphoric «من
ذات النظام». A permissive re-count that admits all six recovers 55 per cent
more citations and moves the composition figures by half a point, because what
the extractor misses is repetition rather than range. We report that bound
rather than a corrected number.

## V. Results

Contemporary_3y; quoted passages excluded; 62,256 mentions in the bench's
reasons, 10,283 strict party mentions, 30,486 wide.

| authority | bench's reasons | party (strict) | party (wide) | ratio, party ÷ court |
|---|---:|---:|---:|---|
| **contract** | 0.86 % | 14.83 % | 10.03 % | **11.7 – 17.2 ×** |
| **legal maxim** | 1.08 % | 4.64 % | 3.10 % | **2.9 – 4.3 ×** |
| **custom** | 0.94 % | 3.79 % | 2.69 % | **2.9 – 4.0 ×** |
| **named fiqh source** | 14.78 % | 8.10 % | 6.09 % | **0.41 – 0.55 ×** |
| **judicial discretion** | 1.72 % | 0.55 % | 0.36 % | **0.21 – 0.32 ×** |
| **judicial principle** | 1.54 % | 1.00 % | 0.78 % | **0.51 – 0.65 ×** |
| statute / regulation | 70.60 % | 55.11 % | 69.03 % | 0.78 – 0.98 × |
| Qur'an | 2.46 % | 3.69 % | 2.25 % | 0.91 – 1.50 × |
| hadith | 6.01 % | 8.29 % | 5.67 % | 0.94 – 1.38 × |

**Negative controls.** The last three rows are reported in the body, not an
appendix, because they carry the argument. Statute, Qur'an and hadith show no
stable direction: each crosses 1.0 between the two specifications. Both sides
reach for scripture, and for the statute book, at rates we cannot distinguish.
That the classifier does *not* separate the two voices on three of nine
categories is the strongest available evidence that where it does separate
them, it is measuring the corpus rather than itself.

**A litigant argues from the contract; a court answers from the law.** The
contract is 15 per cent of what litigants invoke and under 1 per cent of what
courts do. Maxims and custom follow the same direction, more weakly. In the
other direction, named fiqh authority, settled judicial principle and the
court's own discretion are the bench's vocabulary.

## VI. Robustness

**Across windows.** Each cell is *strict / wide*:

| authority | contemporary_5y | contemporary_3y | post_Evidence | post_CTL |
|---|---:|---:|---:|---:|
| contract | 16.76 / 11.29 | 17.24 / 11.66 | 16.73 / 11.25 | 17.79 / 12.47 |
| legal maxim | 4.04 / 2.68 | 4.30 / 2.87 | 4.04 / 2.68 | 5.31 / 3.54 |
| custom | 3.89 / 2.72 | 4.03 / 2.86 | 3.89 / 2.74 | 4.06 / 2.87 |
| named fiqh | 0.55 / 0.41 | 0.55 / 0.41 | 0.55 / 0.41 | 0.52 / 0.44 |
| discretion | 0.29 / 0.19 | 0.32 / 0.21 | 0.30 / 0.19 | 0.11 / 0.14 |
| judicial principle | 0.65 / 0.48 | 0.65 / 0.51 | 0.65 / 0.48 | 0.64 / 0.54 |
| statute | 0.78 / 0.98 | 0.78 / 0.98 | 0.78 / 0.98 | 0.80 / 0.96 |
| Qur'an | 1.51 / 0.91 | 1.50 / 0.91 | 1.52 / 0.92 | 1.83 / 1.19 |
| hadith | 1.42 / 0.95 | 1.38 / 0.94 | 1.42 / 0.96 | 1.41 / 0.95 |

Six survivors keep sign and rank order in all four windows under both
specifications. The three failures fail in all four.

**Conditioning on statutory role.** The obvious alternative explanation is
that courts simply cite procedure more, and procedure is statutory. We remove
it by restricting to non-statutory mentions, where nothing can be procedural
by instrument:

| authority | bench | party | ratio |
|---|---:|---:|---:|
| contract | 2.93 % | 33.04 % | **11.3 ×** |
| legal maxim | 3.67 % | 10.33 % | **2.8 ×** |
| custom | 3.21 % | 8.45 % | **2.6 ×** |
| named fiqh | 50.26 % | 18.05 % | **0.36 ×** |
| discretion | 5.84 % | 1.23 % | **0.21 ×** |
| judicial principle | 5.25 % | 2.23 % | 0.42 × |
| Qur'an | 8.38 % | 8.21 % | 0.98 |
| hadith | 20.46 % | 18.46 % | 0.90 |

n = 18,303 court, 4,616 party. Every survivor survives at the same magnitude;
both nulls stay null. The divergence is not procedural in origin.

A corollary from the same stratification: within *statutory* citations alone,
92.4 per cent of the bench's are to procedural instruments against 74.7 per
cent of the litigants'. The one type that showed no overall difference
diverges once its internal composition is examined.

## VII. Within the same dispute

Comparing populations invites the objection that different disputes reach
different courts. We therefore hold the dispute constant: among 4,313
judgments in which both a court mention and a strict party mention are
identified, what does the bench reach for, given what was raised?

**The statutory answer is flat.** The rate at which the bench's reasons touch
statute barely moves with what the litigant raised (observed ÷ expected under
independence):

```
party raises   statute contract  fiqh  maxim Qur'an hadith custom principle discretion
lift to statute   1.01     0.96  0.95   0.95   0.98   0.99   0.98      1.03       0.74
```

Eight of the nine sit between 0.95 and 1.03. The ninth, discretion, is 0.74 on
26 observations, which is too few to read as anything; we report it rather
than omit it.

**The non-statutory answer is not.** What is elevated is the diagonal:

```
custom → custom 3.92 ×      contract → contract 3.65 ×
principle → principle 2.08 ×  Qur'an → Qur'an 1.64 ×
maxim → maxim 1.63 ×          fiqh → fiqh 1.59 ×
```

We read this cautiously and decline the word *translation*. The court does not
convert litigant authority into statute: it applies statute at the same rate
whatever was argued. What the data support is weaker and more specific:
**statutory reasoning appears to function as a relatively stable background
layer, while some non-statutory authority types show within-dispute
persistence** — a contract point is answered with the contract, a custom point
with custom, three to four times more often than chance.

**And the two sides rarely share an article — but they do share the code.**
Measuring set overlap within each paired judgment:

| level | median Jaccard | share with no overlap | share identical |
|---|---:|---:|---:|
| authority family | 0.500 | 26.9 % | 34.1 % |
| instrument | 0.333 | 42.5 % | 15.5 % |
| **article** | **0.000** | **80.2 %** | 3.0 % |

Agreement decays sharply with specificity. The obvious objection is that a
court decides jurisdiction whether or not jurisdiction was argued, so the
articles it adds may be its office rather than a disagreement. We test it by
classifying every article by function from its own enacted text — structural
procedural, dispute-specific, or ambiguous — validated by hand at 92.9 per
cent precision on the structural class and 100 per cent on the dispute class.

**Removing the structural law does not explain the divergence.** Article-level
non-overlap moves from 80.2 to 78.5 per cent. Only when the comparison is
narrowed to strictly dispute-specific articles does it fall, to 56.5 per cent,
and a majority of paired judgments still share no article.

What the decomposition does change is the *character* of the divergence. Among
dispute-specific articles the two sides use the **same instrument** in 73.9
per cent of judgments. Conditioning makes it plain:

```
P(shared instrument | both cite statute)   56.2 %
P(shared article    | shared instrument)   35.3 %
P(shared article    | both cite statute)   19.8 %
```

Court and litigants are not reasoning in different legal universes. They reach
for the same code roughly six times in ten and, inside it, land on the same
provision about a third of the time. The divergence is **intra-code**, and it
varies by instrument in a legible way: the Arbitration Law, which turns on a
single mandatory-stay provision, reaches 64.7 per cent agreement; the
281-article commercial implementing regulation, which the bench navigates and
the parties barely touch, reaches 12.6 per cent.

A twelve-judgment pilot reading claim against response is consistent with
this and adds a caution. Pairing is identifiable at judgment level but not at
proposition level — the court almost never names a party's article in order to
reject it — so an adopt/reject/bypass taxonomy is not codeable here. On the
three codes that are: the court answered on law the party had not cited in 8
of 12, engaged the party's own article in 2, and 2 were mooted. In one of the
two engagements the court adopted the party's article in a citation form our
extractor under-reads, so measured engagement is a lower bound.

One reading of the intra-code divergence would deflate it: perhaps the two
sides are reaching for functionally different parts of the same code, so that
"same code, different article" is really a difference in the kind of law each
voice invokes. Classifying the 126 most-cited articles by whether they run the
adjudicative process or help resolve the dispute lets that be tested, and it
does not hold. Among the 938 judgments in which both voices cite the same
instrument, the largest transition by a wide margin is a party's institutional
article to the court's institutional article at a **different** provision —
427 judgments, against 66 where the function changes from the party's
institutional to the court's dispute-deciding and 26 the other way. The two
sides are, in the main, reading the same procedural chapter and citing
different sections of it. The same holds inside a single code: the bench cites
art. 29 of the Evidence Law in 1,618 judgments of 1445-1446 and a litigant
cites it in 97, and the two coincide in 2.4 per cent of the bench's. The
divergence is not an artefact of comparing across statute books, and it is not
explained by the two voices carrying different functional layers of the law.

## VIII. Implications

**A. Empirical legal measurement.** Whole-document citation counts mix
distinct legal actors, and the mixing is not noise. Where the mix differs by
an order of magnitude, as it does for contract authority here, no sample size
recovers the quantity of interest. Studies reporting "what courts cite" from
full judgment text should either segment or say what they are measuring.

**B. Legal NLP.** The field has already built role classification, and treats
it as a task in its own right or as a preprocessing step for summarisation. On
the evidence here it is also a *validity* requirement whenever the scientific
target is judicial reasoning. That reframing costs nothing: the datasets and
models exist.

**C. Legal AI and retrieval.** Systems trained or grounded on full judgment
text, without role separation, learn advocacy and adjudication as one
distribution. This is measurable without any model. Ranking the same 1,617
articles by frequency in full text, in court reasoning only, and in party
argument only, the rank correlation between the court's ranking and the
parties' is **0.564**, and seven of the court's top fifty articles are absent
from the full-text top fifty. The vivid case is article 90 of the commercial
implementing regulation: the **third** most-cited article in full text, and
not in the court's top three — it is the preparatory-hearing formula recited
in tens of thousands of statements of fact. A system grounded on full judgment
text would rank a docket-management formality among the most important
provisions of Saudi commercial law.

**D. Saudi legal research.** The results are evidence about *contemporary
published commercial adjudication*, and should be described that way. They are
not evidence about Saudi courts in general, about personal status, criminal or
administrative adjudication, or about unpublished decisions.

## IX. Limitations

1. **Commercial-heavy, single jurisdiction.** Roughly 95 per cent commercial;
   28 personal-status judgments in the whole corpus. No general claim about
   Saudi adjudication is made or supported.
2. **Published judgments only,** with a publication share that moved from
   2 to 88 per cent across the span. All figures are conditional on selection
   into publication with reasons.
3. **Speaker attribution is bracketed, not solved.** The gate measured the
   court bucket at 12/12, the strict party bucket at 10/12 and the facts
   segment at 7/12. Two specifications are reported for that reason and there
   is no third arbiter.
4. **One primary human annotator.** A second-annotator packet exists in the
   repository and is unlabelled; no inter-annotator agreement is claimed, and
   none is invented.
5. **Not all authority is observable.** Unattributed doctrinal reasoning
   carrying no marker is, by construction, counted as no explicit authority.
6. **Invocations, not grounds.** A court may decide from the contract and
   write the statute, or the reverse. Nothing here separates them.
7. **No causal claim.** Nothing here identifies the effect of any reform, and
   the within-dispute analysis is associational.

## X. Conclusion

A judicial decision is not one legal voice. In the corpus studied here, the
bench and the litigants who address it invoke systematically different kinds
of legal authority — six of nine categories, by factors between two and
seventeen, robust to window, to specification, and to conditioning on
procedural role — while agreeing at rates we cannot distinguish on three
others. In four paired judgments out of five they do not cite a single article
in common.

Whether that is true of other jurisdictions is an open question, and it is
answerable: the segmentation needed to ask it already exists, built for other
purposes. What this paper offers is the reason to ask.
