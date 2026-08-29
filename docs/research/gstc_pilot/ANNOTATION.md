# GSTC_DEV — what the hand labels say

See `CROSS_SOURCE.md` for the same reading of MOJ_DEV and for
what the two institutions do differently.

120 occurrences of «مادة» drawn from five GSTC digests, read one at a time in
a 1,400-character window and labelled by hand before any GSTC-specific parser
was written. Every figure below is produced by `dev_profile.py`; none is typed.

    python3 dev_profile.py

## The frame is not the answer

118 of the 120 occurrences are citations to an article. Two are the ordinary
noun: «مادة الفحم الحجري» (the coal), «العينة المسحوبة من المادة المصدرة» (the
exported material). A detector that fires on the word alone is wrong twice in
120; that is the floor on precision, not a rounding error, because both false
hits sit in reasoning text where a citation would be expected.

## Whose citation is it

| segment | n |
|---|---|
| party submission (دفوع الأطراف) | 41 |
| authorities block (المستند) | 36 |
| the tribunal's own reasoning | 27 |
| disposition / finality note | 10 |
| inside a quoted legislative text | 3 |
| summary (الملخص) | 1 |

Only **22.9 per cent** of what a detector would find is the tribunal's own
citation. The rest is what a party urged, what the reporter listed, or the
procedural boilerplate that closes every decision. Any sentence of the form
"the tribunal cited X" drawn from undifferentiated extraction over-counts by
roughly four times. This is a measurement about GSTC, and it is the first
place to look before repeating a claim of that shape about any other body.

## How the instrument attaches

| instrumentSource | n |
|---|---|
| local — named in the same «من X» attachment | 84 |
| list_trailing — named once at the end of a coordinated list | 24 |
| anaphora — «هذه اللائحة», «منها», «ذات اللائحة», «هذا النظام» | 9 |
| absent — not recoverable from the document | 1 |

**28.8 per cent** of citations do not carry their instrument locally. Two are
not resolvable at all: one cites «المادة الحادية عشر» with no instrument
anywhere in the submission, and one says «الالئحة ذاتها» where the nearest
antecedent is not a لائحة and the quoted text belongs to a different
instrument. Both are labelled unresolvable on purpose. A parser that returns
an instrument for them is not right; it is guessing, and the gold set is built
so that guessing scores as an error.

## How the article number is written

| form | n |
|---|---|
| digits in parentheses — «المادة (79)» | 94 |
| bare words — «المادة الثامنة والستين» | 12 |
| words in parentheses — «المادة (الحادية والسبعين)» | 9 |
| bare digits — «المادة 16» | 2 |
| «المادة رقم (79)» | 1 |

21 of 118 spell the number out. Both spelled forms appear for the same
provision in the same paragraph of one digest: «المادة 68 من النظام الضريبي»
and «للمادة الثامنة والستين من نظام ضريبة الدخل».

65 of 118 carry a paragraph or subparagraph. They are written in at least
seven arrangements: «الفقرة (3) من المادة (57)», «المادة (5) الفقرة (1) بند
(أ)», «المادة (4) البند ثانيا», «للمادة الرابعة (أولا/9)», «الفقرة الرابعة من
المادة (17)», «الفقرة (ب) من الفقرة (8) من المادة (53)», «المادة (/1/9أ)».
The last is bidi reordering of «9/1/أ», not a drafting choice.

## What the page does to the text

Three distinct text-layer defects appear in these five documents, each
producing a different failure:

- **11.pdf** substitutes glyphs systematically: «نلام» for «نظام», «حي» for
  «حيث», «الملسسة» for «المؤسسة», «إنى» for «إلى». An instrument matcher
  keyed on «نظام» cannot fire anywhere in this document.
- **15.pdf** inserts spaces inside words on justified lines: «نص ت»,
  «الض ريبة», «المس تأنف».
- **18.pdf**, on some pages only, drops glyphs: «الصا ر», «اليريبية»,
  «الالسحة», «م لس إ ارة».

None of these is repaired by the canonicalisation layer as it stands. They are
per-document font-encoding faults, not the bidi, tatweel, digit or lam-swap
faults that layer was built for. They are recorded here so the ablation can
say how much of the 0.0 per cent GSTC score they account for.

Two further breaks are not defects but drafting: a page number and two line
breaks fall between «المادة (14)» and «من الالئحة التنفيذية...», and the
linking «من» is simply absent in four items («الفقرة (3) المادة (57)»,
«المادة (41) نظام المرافعات الشرعية», «المادة (8) الالئحة التنفيذية»,
«استنادا إلى (1) من المادة (5)»).

## The instruments

Thirteen distinct instruments, named inconsistently. One instrument carries
four names across the sample — «الالئحة التنفيذية لجباية الزكاة», «لائحة جباية
الزكاة», «الالئحة التنفيذية لنظام الزكاة», «لائحة جباية الزكاة الصادرة بعام
1438ه» — and is sometimes identified only by the ministerial decision number
(2082) or by its year. «نظام ضريبة الدخل» is also «النظام الضريبي». Two
instruments differ by two words and are not the same text: «نظام المرافعات
الشرعية» and «الالئحة التنفيذية لنظام المرافعات الشرعية», whose article 70
differ.

One citation is to a private employer's internal work rules («لائحة تنظيم
العمل الداخلية»), not legislation at all. It is labelled as a citation because
it is one, and flagged because counting it as a legislative instrument would
overstate legislative citation.

## Rules of use

DEV is for development. GSTC_TEST_FROZEN, five other documents with a frame of
5,418, is not opened until the parser is frozen and its SHA recorded.
