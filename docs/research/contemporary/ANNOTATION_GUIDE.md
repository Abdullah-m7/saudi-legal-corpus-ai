# Annotation guide — second reader

Two tasks. Both are done **without** seeing any statistics, any classifier
output, or the hypothesis being tested. If you have read the repository's
findings, say so on the answer form; it does not disqualify you, but it is
recorded.

Every definition below is followed by an attested example from this corpus,
because a definition without an example is not operational.

---

## Task A — what kind of provision is this?

You are shown an instrument, an article number and the **enacted text of the
article**. Nothing else. You are not shown any judgment.

One question: *if a judge had this article and only this article in front of
them, could they decide the point it addresses?*

Choose exactly one class. Where two fit, use the priority order below — the
first that applies wins.

**1. EXTERNAL_REFERRAL** — the article's own words send the judge to a source
outside the enacted text: the Shariah, custom, or the fiqh maxims.

> Sharia Procedure Law art. 1: «تطبق المحاكم على القضايا المعروضة أمامها أحكام
> الشريعة الإسلامية، وفقاً لما دل عليه الكتاب والسنة».
> Commercial implementing regulation art. 164, among the factors in assessing
> compensation: «د - العرف، أو العادة المستقرة».

Not this class: a referral to another *statute* or to an implementing
regulation. That is internal to the enacted law.

**2. OPEN_TEXTURED_STANDARD** — the decision the article calls for turns on a
standard whose content the text does not fix.

> Law of Practice art. 26: the court assesses the lawyer's fee «بما يتناسب مع
> الجهد الذي بذله المحامي والنفع الذي عاد على الموكل».
> Civil Transactions Law art. 120: «كل خطأٍ سبب ضررًا للغير يُلزم من ارتكبه
> بالتعويض».

The standard must govern the **operative** decision. An open word inside an
incidental exception does not make the article open-textured: Evidence Law
art. 103 makes non-attendance نكول «بغير عذر» and the effect is stated
completely, so it is class 6, not class 2.

**3. DUTY_OR_POWER_WITHOUT_DECISION_RULE** — confers a power or imposes an act
without stating the rule that decides entitlement.

> Evidence Law art. 110: «للمحكمة … أن تقرر ندب خبير أو أكثر؛ لإبداء رأيه في
> المسائل الفنية التي يستلزمها الفصل في الدعوى».

**4. DEFINITION_STATUS** — defines a term, or fixes a scope or a status.

> Evidence Law art. 1: «تسري أحكام هذا النظام على المعاملات المدنية والتجارية».
> Evidence Law art. 92, defining اليمين الحاسمة and اليمين المتممة.

**5. INSTITUTIONAL_DIRECTIVE** — fixes an institutional fact completely:
competence, venue, form, deadline, chamber, who may file.

> Commercial Courts Law art. 79: the appeal periods, in days.
> Commercial implementing regulation art. 11: which chamber hears a claim of
> what value.

**6. SELF_SUFFICIENT_RULE** — states condition, rule and legal effect
determinately enough to decide the point it addresses.

> Evidence Law art. 17: «الإقرار القضائي حجة قاطعة على المقر، وقاصرة عليه».
> Commercial Courts Law art. 30: served in person or appeared → the
> proceedings are adversarial «ولو تخلف بعد ذلك».

Also record, for every article:
- **ambiguous** — yes if you hesitated between two classes.
- **secondChoice** — which class you nearly picked, if any.

---

## Task B — what is the non-statutory authority doing here?

You are shown the **reasons** of one judgment, with the parties' identifiers
already removed. Somewhere in it the court invokes something that is not the
enacted text: a jurist, a maxim, a verse, a hadith, a settled judicial
practice, or a custom.

Two questions.

### B1. What work does it do? Choose one.

**SUPPLIES_THE_DECISION_RULE** — the statutory articles cited in the same
judgment do not state the rule that decides the point; the non-statutory
authority does.

> A chamber awarding litigation costs under art. 164, which obliges it to
> decide the claim and lists factors but states no entitlement, and taking the
> entitlement from «ومن مطل صاحب الحق حقه حتى أحوجه إلى الشكاية فما غرمه بسبب
> ذلك فهو على الظالم المبطل».

**ALLOCATES_BURDEN_OR_PRESUMPTION** — the statute says what counts as proof;
the authority says what is presumed when the proof runs out.

> Evidence Law art. 29 makes the private document حجة, and the chamber decides
> who loses by «الأصل في الديون الثابتة في ذمة الغير هو بقاؤها في ذمته وعدم
> البراءة منها».

**INTERPRETS_OR_DEFINES** — gives content to a word or a provision of the
statute that the statute leaves open.

**CORROBORATES** — the statutory article decides the point on its own, and
the authority endorses the result or shows it to be Shariah-conformable.

> A settlement recorded under Commercial Courts Law art. 29(2), with «والصلح
> خير» and the hadith «الصلح جائز بين المسلمين» added, and the judgment's own
> test stated as «لم يظهر من هذا الصلح ما يخالف الشرع والنظام».

**INDEPENDENT_GROUND** — decides a point that none of the statutes cited in
the judgment addresses at all.

> Territorial venue taken from «المقرر فقهاً وقضاءً أن الدعوى تقام أمام المحكمة
> التي تقع في نطاق محل إقامة المدعى عليه» where the only jurisdiction article
> cited confers subject-matter competence.

**UNCLEAR** — the passage does not let you tell. Use it rather than guessing;
how often it is used is itself a result.

### B2. Could the sentence carrying that authority be deleted without changing
the reasoning?

**yes / no / cannot tell.**

This is the operational test for "ornamental". It is asked separately from B1
because the first reader could not code ornamental-versus-supporting reliably
by intuition, and a deletion test is answerable where an intuition is not. A
CORROBORATES passage answered *yes* is ornamental in the only sense this
corpus can measure.

---

## What is deliberately not asked

Whether the court was right, whether the fiqh was correctly used, and what the
court "really meant". None of those can be read off a published judgment, and
this project does not write prose about what a court meant — it quotes the
judgment's own words with its citation.

---

## Getting the sheets

The sheets are not committed. They carry the reasons of forty judgments and
the text of fifty-eight articles, and this repository does not redistribute
judgment text — the mention layer holds counts and identifiers only. The
sheets are regenerated instead, deterministically, from the corpus:

```
python3 second_reader.py articles  --out <path>/task_A_articles.txt
python3 second_reader.py judgments --out <path>/task_B_judgments.txt
```

Both draw under a fixed seed and both write the same items every time.
`second_reader_key.json` records which article and which judgment each
identifier refers to, together with the first reader's label, so the two
readings can be compared afterwards and not before.

Answer on `second_reader_articles.csv` and `second_reader_judgments.csv`,
then:

```
python3 second_reader.py score --answers second_reader_articles.csv
```

which prints raw agreement, Cohen's kappa, and the confusion pairs. This packet is **optional external replication**. The findings that rest on
hand labels are published as an interpretive layer with their rules,
ambiguity class and provenance attached, and they do not wait on it. What a
second reader adds is an agreement statistic, which strengthens them; what
they do not do is authorise them.
