# Did the codes displace the judge? A feasibility study

Saudi Arabia codified quickly: the Commercial Courts Law (م/93, 1441), the
Evidence Law (م/43, 1443), the Civil Transactions Law (م/191, 29 Dhū al-Qaʿda
1444 — the date the judgments themselves give it). The standard hope and the
standard fear are the same proposition: that a code replaces the judge's own
reasoning with the legislature's. This asks whether the corpus shows it.

It is a feasibility study. The question is whether the measurement can be made
defensibly here, and what a first pass says.

## The instrument

`discretion_census.py` first asked the corpus what non-statutory authority
sounds like, rather than guessing at it — the lesson `vocabulary_census.py`
learned the hard way, that a zero from a broken search reads exactly like a
finding. Thirty-six candidate markers were counted across all 50,666
judgments, inside the court's own reasons only. **Thirty-two are attested;
four are not** (`ابن باز`, `ابن عثيمين`, `الأمور بمقاصدها`, `المشقة تجلب
التيسير`) and are dropped. The survivors fall into five families:

| family | examples | judgments carrying it |
|---|---|---|
| jurists and their books | ابن تيمية · كشاف القناع · الإنصاف · المغني | ~11 % |
| maxims of fiqh | الضرر يزال · الأصل براءة الذمة · العادة محكمة | ~2 % |
| scripture | قوله تعالى · متفق عليه · قوله ﷺ | ~11 % |
| unattributed doctrine | المقرر فقهاً · استقر القضاء · أهل العلم · الراجح | ~9 % |
| discretion named as such | السلطة التقديرية · ما تراه المحكمة · الاجتهاد | ~4 % |

Everything is confined to the segment between «الأسباب:» and «حكمت الدائرة»
of the court's own judgment. A party quoting Ibn Taymiyya is not a court
reasoning from him, and this project has already measured how much that
distinction moves a number (`UPTAKE.md`).

## The series, and the reason most of it must be thrown away

First-instance lawsuits, court's own reasons, by Hijri year:

| year | judgments | with reasons | (%) | words | fiqh % [95 % CI] | statute % [95 % CI] | neither % | fiqh/1k | cites/1k |
|---|---:|---:|---:|---:|---|---|---:|---:|---:|
| 1440 | 1,399 | 21 | **1.5** | 231 | 9.5 [2.7, 28.9] | 61.9 [40.9, 79.2] | 33.3 | 0.41 | 3.72 |
| 1441 | 2,194 | 36 | **1.6** | 230 | 30.6 [18.0, 46.9] | 63.9 [47.6, 77.5] | 25.0 | 2.42 | 4.47 |
| 1442 | 9,468 | 203 | **2.1** | 257 | 29.1 [23.3, 35.7] | 66.0 [59.3, 72.2] | 24.1 | 2.20 | 4.98 |
| 1443 | 4,735 | 3,140 | 66.3 | 239 | 25.5 [24.0, 27.1] | 75.7 [74.1, 77.1] | 18.2 | 2.12 | 7.30 |
| 1444 | 18,110 | 15,651 | 86.4 | 245 | 25.9 [25.2, 26.6] | 73.7 [73.0, 74.3] | 21.5 | 2.08 | 6.32 |
| 1445 | 6,625 | 5,679 | 85.7 | 276 | 28.6 [27.5, 29.8] | 81.2 [80.2, 82.2] | 15.3 | 2.07 | 6.93 |
| 1446 | 2,441 | 1,172 | 48.0 | 303 | 28.2 [25.7, 30.9] | 84.6 [82.4, 86.5] | 11.7 | 1.69 | 7.80 |

**The fourth column decides how much of this table may be read.** In 1440–1442
between 1.5 and 2.1 per cent of judgments carry reasons at all; from 1443 it
is two-thirds to seven-eighths. Those first three rows are not early years of
the same series — they are a different and tiny population, selected by
whatever made twenty-one judgments out of 1,399 get published with their
reasons. Nothing in them supports a before-and-after comparison, and this
study does not make one. 1446 is also partial at 48 per cent, and is read as
provisional.

That leaves 1443–1446, each with thousands of judgments and intervals a point
wide.

## What those four years say

Over 1443–1446, spanning the promulgation of the Civil Transactions Law:

- **statutory citation rises sharply**: 75.7 % → 84.6 % of reasoned judgments,
  intervals disjoint, and 7.30 → 7.80 citations per thousand words;
- **non-statutory authority does not fall**. It rises slightly in prevalence,
  25.5 % → 28.2 %, with 1443's interval disjoint from 1445's;
- judgments citing **neither** halve, 18.2 % → 11.7 %;
- the only measure that falls is fiqh *density*, 2.12 → 1.69 per thousand
  words — and reasons grew 27 % longer over the same span, from 239 words to
  303, so a constant amount of fiqh in a longer text produces exactly that.

By family, nothing is being abandoned. Jurists and their books sit at 10–11 %
throughout; scripture *rises*, 8.7 % → 13.7 %; unattributed doctrine holds
near 9 %; discretion named as such holds near 4 %.

## The sharpest test: within one year

Comparing years cannot separate a change in judicial style from a change in
what gets published, which is exactly what the fourth column shows moving. So
compare judgments of the *same* year to each other: those that reason from
the Civil Transactions Law against those that do not. Year, court, and
selection are held constant by construction.

| year | judgments citing the code | fiqh % when it does | fiqh % when it does not |
|---|---:|---|---|
| 1445 | 186 | 29.6 [23.5, 36.5] | 28.6 [27.4, 29.8] |
| 1446 | 172 | 24.4 [18.6, 31.4] | 28.9 [26.2, 31.8] |

**Null, in both years, with every interval overlapping.** A judgment reasoning
from the new civil code reaches for Ibn Taymiyya, for a maxim, for «المقرر
فقهاً», about as often as a judgment of the same year that never mentions it.

The honest caveat is power, and it is a real one: only 186 and 172 judgments
cite the code at all, so the intervals are six points wide and the test cannot
see a displacement smaller than about seven points. What it can say is that
the large displacement the framing assumes — the code replacing the
jurisprudence — is not there.

## The finding, stated at the strength the evidence carries

Over the four usable years, **codification added a citation practice without
subtracting one**. Courts cite far more statute than before and about as much
non-statutory authority as before; what shrinks is the class of judgments that
cited nothing at all. The codes did not displace the fiqh. They displaced
silence.

That is a claim about citation practice, not about reasoning. A court may
reach a conclusion from the code and then dress it in Ibn Taymiyya, or the
reverse; nothing here can separate those, and this study does not pretend to.

## What would be needed to do better

1. **A subject-matter control.** The mix of disputes changes across years and
   is not measured here. Two of the five families are subject-sensitive: the
   maxims cluster in obligations, scripture in guarantee and delay.
2. **The in-force date, not the decree date.** The judgments date the decree,
   م/191 of 29 Dhū al-Qaʿda 1444; the corpus does not state when the code
   bound the courts, and this study does not assert it from memory.
3. **More judgments citing the code.** 358 across two years is the binding
   constraint on the within-year test, and it will fix itself with time
   rather than with method.
4. **Reading a sample.** Every number here is a marker count. Whether «المقرر
   فقهاً» in a 1446 judgment does the same work it did in 1443 is a question
   for a reader, in the manner of `MOJ_ARTICLE_GOLD.md`, and it has not been
   asked.
