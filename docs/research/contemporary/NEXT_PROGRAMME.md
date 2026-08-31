# Choosing the next question

The paper is decided. `DECOMPOSITION.md` says what survived and in what
form. This is the choice of what to ask next from the same asset, and the
first evidence on it. No paper is opened here.

## 1 · Three candidates, five criteria

**A — Hybrid legal reasoning.** What does contemporary statute-plus-fiqh
reasoning actually consist of?

**B — Operationalisation.** What makes a newly enacted provision become
visible in adjudication?

**C — Court–litigant alignment.** When does the court adopt, bypass or
replace the legal basis the litigants offer?

| | A hybrid reasoning | B operationalisation | C alignment |
|---|---|---|---|
| novelty | the codification-displacement question is argued in the literature and has never been measured with the two voices separated | the enacted-versus-invoked gap is unmeasured for a system codifying this fast | it is the paper we have just written; the increment is the next layer down |
| data readiness | complete. type × voice × year × instrument × article already exists in `authority_mentions.jsonl.gz`; the nine-type taxonomy passed a pre-registered gate | mechanically ready, **but the clock is the year**: `authority_layer.jsonl.gz` carries `year` and nothing finer, so "time to first citation" has five buckets over the whole window and three after the Civil Transactions Law | blocked by our own pilot |
| contemporary importance | highest. the Commercial Courts Law is 1441, the Evidence Law 1443, the Civil Transactions Law 1444: the corpus sits on the codification wave itself | high, and the same wave | high but already banked |
| legal significance | answers whether codification changed the *source* of the norm or only its citation form | answers which drafting choices make a provision usable | answers how argument moves inside a judgment |
| methodological validity | good. the threat is composition drift across years, and the data affords two controls: prevalence against intensity, and a within-instrument series | **weakest.** a provision's first *published* citation is a fact about the publication policy as much as about adjudication, and with a yearly clock the censoring cannot be modelled | the pairs pilot found the pairing is identifiable at judgment level 12/12 and **not** at proposition level: the court almost never names the party's article in order to reject it. C therefore needs an annotation the judgments do not support |

**A wins**, and it wins on evidence this session produced rather than on
taste. C is blocked by the negative result of its own feasibility pilot —
that is what a feasibility pilot is for. B's central quantity, time to first
citation, is measured on a clock with five ticks and is right-censored by a
publication decision we cannot observe; it stays in the backlog as a
descriptive question, not a causal one. A is fully served by the layer that
already exists.

## 2 · The number that provoked it

`claim_results.json` shows the bench's fiqh citations falling from 22.7 per
cent of everything it cites in 1441 to 10.0 per cent in 1446, while the share
of judgments whose reasons *mix* statute with non-statutory authority rises
from 18 to 32 per cent over the same years. Both cannot be a trend in the
same quantity. A share of mentions falls whenever the other term grows.

So `hybrid.py` separates the three questions that one number confuses, over
reasoned judgments, with quoted spans excluded:

| year | reasoned | statute prevalence | fiqh prevalence | fiqh intensity | fiqh share of mentions |
|---|---:|---:|---:|---:|---:|
| 1442 | 240 | 66.2 % | 16.7 % | 1.93 | 15.5 % |
| 1443 | 3,161 | 75.9 % | 16.2 % | 1.98 | 13.5 % |
| 1444 | 16,435 | 80.2 % | 20.2 % | 1.93 | 15.6 % |
| 1445 | 5,982 | 86.6 % | 20.4 % | 1.97 | 13.8 % |
| 1446 | 1,209 | 87.2 % | 16.3 % | 1.93 | 10.0 % |

**Statute prevalence rises 21 points and statutory intensity rises from 2.06
to 2.80 citations per citing judgment. Fiqh prevalence does not fall — and
fiqh intensity is flat to two decimal places across five years.** Holding the
posture roughly fixed by restricting to judgments citing the Commercial
Courts Law moves nothing: fiqh prevalence 16.8, 21.2, 22.1, 23.3, 18.6.

The declining share is arithmetic. The bench did not stop reasoning from
fiqh; it started citing a great deal more statute around an unchanged core.

Two cautions. 1446 has 1,209 reasoned judgments and is a partially published
year, so its dip (95 % CI 14.3–18.5) is not a trend; and the window is five
years, which is a window on the codification wave, not on the century.

## 3 · What the fiqh is doing — an exploratory hand-read sample (n = 14)

Counting STATUTE+FIQH is what provoked the question; it cannot answer it. So
`hybrid.py sheet` drew 14 judgments of 1444–1446 whose reasons carry both,
and they were read against the six functions the question proposed.

Two of the six did not occur in the sample. Nothing was read as ornamental —
in all fourteen the non-statutory authority carries a proposition that none of
the statutory articles cited in the same judgment states — and nothing was
definitional. **How much that carries is bounded by fourteen**: 0 of 14 has a
95 per cent Wilson interval running to 21.5 per cent, so the sample rules out
a *common* ornamental use of non-statutory authority and nothing narrower. It
is an exploratory hand-read sample by one reader, and every claim resting on
these labels is **PROVISIONAL_PENDING_SECOND_READER**. What the reading found:

| what the authority does | n |
|---|---:|
| **GAP_FILL** — the statute confers a duty or a discretion and no rule of entitlement; the authority supplies the rule of decision | 7 |
| **RESIDUAL_RULE** — the statute says what counts as evidence; the authority says what is presumed when the evidence runs out | 4 |
| **LEGITIMATION** — the outcome is fixed by the article; the scriptural text certifies that the statutory rule is Shariah-conformable | 2 |
| **FIQH_BASELINE_STATUTE_LIMITS** — the authority states the operative rule and the statute carves an exception out of it | 1 |
| ornament | **0** |

The clearest gap-fill is compensation. Art. 164 of the commercial
implementing regulation *obliges* the court to decide the claim and lists
what to weigh — «جسامة الضرر… مقدار المبلغ المحكوم به… مماطلة المحكوم عليه»
— and states no entitlement. Five of the fourteen fill it from outside the
statute book, one quoting Ibn Taymiyya: «ومن مطل صاحب الحق حقه حتى أحوجه إلى
الشكاية فما غرمه بسبب ذلك فهو على الظالم المبطل إذا غرمه على الوجه المعتاد».

The clearest residual rule is proof. Evidence Law art. 29 makes the private
document حجة against the person who signed it; it does not say who loses when
the debtor says nothing. That comes from «الأصل في الديون الثابتة في ذمة
الغير هو بقاؤها في ذمته وعدم البراءة منها» (كشاف القناع ٣/٣٠٧), quoted with
its page in two of the fourteen.

And the inverse case exists. In one judgment the rule of decision is the
hadith «لو يعطي الناس بدعواهم لادعى ناس دماء رجال وأموالهم ولكن اليمين على
المدعى عليه», and the only statute cited restricts it: «في جميع الأحوال؛ لا
توجه اليمين إلى الشخصية الاعتبارية» (art. 133 of the implementing
regulation). Statute as an exception to a fiqh baseline, not the reverse.

One reader, fourteen judgments, no agreement statistic: this is a hypothesis
with an attested example for each class, not a measured distribution. The
frame is also judgments the extractor already marked hybrid, so a judgment
whose only non-statutory authority takes an unrecognised form is invisible to
the sample exactly as it is to the count.

## 4 · The seam is a property of the article, not of the sample

The hand reading says the fiqh arrives at particular places in the statute.
That is testable on all 23,695 judgments whose reasons cite anything. For
every article the bench cites at least 300 times, the share of the judgments
citing it whose reasons also carry a non-statutory authority — against a base
rate of 38.5 per cent:

| article | what it does | n | with non-statutory authority |
|---|---|---:|---:|
| CCL art. 29 | records a settlement reached before the chamber | 320 | **85.9 %** |
| CCL-IR art. 64 | offer of settlement | 329 | 72.3 % |
| Evidence art. 1 | «تسري أحكام هذا النظام على المعاملات المدنية والتجارية» | 356 | 71.6 % |
| CCL-IR art. 164 | must decide compensation; lists factors; states no entitlement | 1,394 | **66.6 %** |
| SPL art. 57 | judgment against the absent defendant | 539 | 57.7 % |
| Evidence art. 3 | «البينة على من ادعى، واليمين على من أنكر» | 397 | 46.9 % |
| Evidence art. 29 | the private document is حجة | 3,770 | 38.6 % |
| CCL art. 16 | commercial jurisdiction | 9,190 | 37.2 % |
| SPL art. 76 | pleas of jurisdiction, standing, res judicata | 1,564 | 11.4 % |
| CCL-IR art. 11 | which chamber hears a claim of what value | 398 | 11.1 % |
| CCL-IR art. 58 | mediation is required before these claims may be filed | 374 | **1.1 %** |

**A seventy-eight-point spread, and the structural/dispute-specific
distinction does not explain it**: by class the rates are 34.1 per cent
(structural procedural), 35.7 (dispute-specific), 37.9 (ambiguous) — three
points apart where the articles are eighty apart. Both ends of the table are
procedural articles.

What separates them is whether the article decides anything by itself. An
article that fixes an institutional fact — which chamber, which threshold,
mediate before you file — is complete, and the bench cites nothing beside it.
An article that imposes a duty to decide without a rule of decision, or
admits a document without allocating the residual burden, is incomplete on
its face, and three judgments in four bring in an authority from outside.
Evidence art. 3 is the sharpest case: the legislator codified the maxims
themselves — «البينة لإثبات خلاف الظاهر، واليمين لإبقاء الأصل» — and courts
citing it still reach outside the statute book in 46.9 per cent of judgments.

This is also why the yearly series is flat. Codification produced determinate
institutional articles in bulk, which is the rise in statutory density; it
did not close the indeterminate seams, and it created some of them.

## 5 · The programme

> **Where in a codified statute book does non-statutory authority remain
> necessary, and what property of a provision predicts it?**

Measured, not asserted: the outcome variable exists for every article the
bench cites often enough, the two voices are separable, the five-year window
covers the enactment of three of the instruments, and the taxonomy of what
the authority *does* has an attested example per class from judgments'
own words.

What it needs before it is a paper, in order:

1. a second reader on a larger hand sample — the four classes have no
   agreement statistic and one annotator
2. the article-level rate computed for the party voice too: if litigants
   reach outside the statute book at the same seams, the seam is a property
   of the law; if only the bench does, it is a property of the office.

   A first probe says the seams are **not** shared, and it is reported here
   as exploratory because the party voice is thin — only a handful of
   articles reach n = 150 at all. Against a party base rate of 33.5 per cent
   (strict; 5,257 judgments), the party's most fiqh-attracting article is
   art. 76 of the Sharia Procedure Law at 29.1 per cent — the article the
   *bench* cites with the second-lowest rate in the whole table, 11.4. The
   party-side spread is 7.4 to 29.1 points where the bench's is 1.1 to 85.9.
   If that holds on a proper design, the incompleteness that draws in
   non-statutory authority is being felt from the bench, not argued from the
   bar, and the next question is why.
3. article features that could predict the rate — a duty verb without a
   standard, a list of factors without a rule, a term used and not defined —
   built as auditable rules against a gold sample, in the way `function.py`
   was built and hand-validated
4. the inverse-case count: how often does a statute appear only to limit a
   rule the judgment takes from elsewhere

Not in scope: a second paper this session, an LLM pass over anything before a
gold sample exists, and any historical extension. The question is about a
statute book that is three years old.

---

## Postscript: the programme was run, and the answer is PARTIAL

`COMPLETENESS.md` carries the result. The reframed question of §5 —
*where in a codified statute book does non-statutory authority remain
necessary, and what property of a provision predicts it* — has an answer that
is narrower than the question. Open texture predicts; institutionality
predicts better and in the opposite direction; an explicit referral to the
Shariah in the article's own words predicts nothing; and the ordering does
not survive inside four of six statute books.

The three items this section listed as prerequisites now stand as follows.
The second reader packet is built and blind (`ANNOTATION_GUIDE.md`,
`second_reader.py`) and nothing turning on the hand labels is claimed until
it returns. The party-voice rate was computed properly rather than as a
probe, and the exploratory reading it prompted did not survive: the median
bench-minus-bar difference is about zero, and what is real is a class
pattern, not a level. Article features were built as a hand taxonomy rather
than as rules, because the taxonomy had to be blind and a rule set written
after seeing the rates would not have been.
