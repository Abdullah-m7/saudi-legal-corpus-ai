# Thirty-two judgments, read end to end

Every measurement in this project before this one was made per occurrence of
the word «مادة». Four hundred and eighty of them for the pilot, four hundred
more for GSTC_TEST2, each read through a window of about 1,300 characters.
That is the right unit for one question — does the parser resolve the
citation in front of it — and the wrong unit for the question the HILJ paper
actually asks, which is *which articles a court applies*. An article cited
eleven times in one judgment is one applied article. A window of 1,300
characters cannot see that the same article was named three paragraphs
earlier in a different form, and it cannot see the citation that sits outside
the window at all.

So this reads whole judgments.

Thirty-two of them, drawn by `moj_article_gold.py` from sixteen strata built
on the things that make a judgment hard to *count* rather than on subject
matter: dense against sparse, one instrument against several, anaphora
present or absent, recitals-heavy against reasons-heavy. Every judgment used
in MOJ_DEV or MOJ_TEST is excluded, so nothing here has informed any earlier
repair. 178 rows were written by hand, one per citation, each carrying
article, paragraph, instrument, how the instrument was named, segment,
voice, and what was odd about the form.

`moj_article_metrics.py` then runs the published pipeline — `V.CITE`,
`match_instruments`, `arabic_ordinals` — over the same 32 judgments and
scores it. Nothing in the parser was changed before or after that run.

## What is in 32 judgments

|                                                     |     |
| --------------------------------------------------- | --: |
| «مادة» occurrences inside the sampling frame          | 172 |
| of which citations                                    | 159 |
| of which anaphoric or numberless, not citations       |  13 |
| citations lying **outside** the frame                 |   6 |
| citations naming no recoverable instrument            |   8 |
| citations in the court's own voice                    | 127 |

**1.12 occurrences per applied article.** That is the ratio the
occurrence-level counts have been silently multiplying by. It is not uniform:
judgment 6 of the sample turns six occurrences into two applied articles,
because the publisher repeated one party's sentence five times; judgment 14
turns seven occurrences into five, because the court cites article 19 itself
and then quotes two provisions that each cite it again.

## The extractor, scored on whole judgments

|                                | precision              | recall                 |
| ------------------------------ | ---------------------- | ---------------------- |
| occurrence level (159 gold)    | 89.3% [82.5, 93.6]     | 68.4% [60.7, 75.1]     |
| article level (142 gold)       | 88.1% [80.7, 92.9]     | 67.6% [59.5, 74.8]     |
| statutory citations only (151) | —                      | 71.5% [63.9, 78.1]     |

Wilson 95% intervals. "Statutory only" drops the citations to private
contracts and the one citation that names no instrument at all; an extractor
built to read statutes should not be charged with those, and the difference
between 68.4% and 71.5% is exactly what they cost.

This is a much harsher picture than GSTC_TEST2's, and the two are not in
conflict. TEST2 asked: given an occurrence the frame has already selected,
does the parser get it right — 100.0% detection precision, 94.6% recall.
This asks: of everything a judgment actually cites, how much does the
pipeline ever see. The gap between the two numbers is the frame, and it is
large.

### Why the misses were missed

Forty-three statutory citations were missed. Re-reading the sentence each one
sits in:

| cause                                                     |  n |
| --------------------------------------------------------- | -: |
| instrument named anaphorically — «من ذات النظام»           | 14 |
| article and paragraph packed into one number — «2/76»      |  9 |
| instrument named once at the end of a list                 |  6 |
| paragraph placed after the instrument — «المادة (29) فقرة (1) من …» | 3 |
| instrument named before the article                        |  2 |
| instrument named by a possessive suffix — «من لائحته»      |  2 |
| cited inside quoted statutory text                         |  1 |
| no single cause identified                                 |  6 |

The first line is the important one, and it is a defect of the published
pattern, not of the corpus. `V.CITE` requires the instrument word to stand
immediately after «من». Any modifier in between kills the match outright:

```
المادة (59) من ذات اللائحة        →  V.CITE.findall(...) == []
المادة (35) من ذات النظام         →  []
المادة الحادية عشرة من هذا النظام  →  []
المادة (212/أ) من لائحته التنفيذية →  []
المادة (16) من نظام المحاكم التجارية →  [('16', 'نظام المحاكم التجارية')]
```

`match_instruments` has a careful anaphora resolver, documented at length in
its own module, that resolves «ذات النظام» to the last law named and «ذات
اللائحة» to the last regulation. **The resolver is never reached for these
forms, because the pattern that would feed it does not fire.** What reaches
it is the bare «من النظام» and «من اللائحة», which the alternation does
match.

Corpus-wide, over all 50,666 judgments — `citation_forms.py`, counted on
tatweel-stripped text because canonicalisation strips tatweel:

| form                                                              | sites | invisible to `V.CITE` |
| ----------------------------------------------------------------- | ----: | --------------------: |
| «المادة N من **ذات/هذا/هذه/نفس** النظام‑اللائحة»                   | 4,310 |                 4,294 |
| «المادة N من **لائحته/نظامها** التنفيذية» (possessive suffix)      |   379 |                   166 |
| «المادة (N) **فقرة (M)** من …» (paragraph after the article)       | 1,022 |                   800 |
| second and later members of an enumerated list, «(51) و (56) و …»  | 2,263 |                 2,263 |
| head noun carrying Arabic diacritics, «المادَّة»                    |   234 |                   234 |
| head noun truncated to «الماد»                                     |     4 |                     4 |
| bracketed number with no head noun, «(1/29) من نظام الإثبات»       |   279 |                   279 |

Separately, 353 sites put articles under the plural head noun «المواد»,
naming 884 distinct article numbers, of which **730 are named nowhere else in
the same judgment** and so are invisible to any count keyed on «مادة»
singular.

The two columns differ where `V.CITE` happens to fire on a *different* span
beginning at the same «مادة» token — sixteen of the anaphoric sites, 213 of
the possessive-suffix sites, 222 of the postfix ones. Those are counted as
seen, so the "invisible" column is the conservative figure throughout.

The diacritics line is worth separating out. Canonicalisation strips tatweel
— «الــمــادة» is recovered — but it does not strip harakāt, so «المادَّة
(69) من نظام الإفلاس» is lost to a shadda. That is a two-line fix in
`canonical.py` and it is **not being made here**, for the same reason the
three repairs pre-declared in `TEST2.md` were not made: the parser is frozen,
and a repair discovered on a set is a repair that burns it.

## Packed numbers have no fixed order

Judgment 15 of the sample writes, in one judgment:

- «المادة (57/3) من نظام المرافعات الشرعية» — article 57, paragraph 3
- «المادة 2/31 والمادة 21 من نظام الإثبات» — paragraph 2, article 31

Article-first and paragraph-first, eleven lines apart, in the same court's
own reasoning. Judgment 19 does the same across the two judgments in one
published record: «(16/1)» in the first instance, «(2/76)» on appeal.

Corpus-wide there are **12,074 packed `a/b` citation bodies**. 8,498 put the
larger number first, 3,524 put it second, 52 are equal. In **1,608 of them
(13.3%) both numbers fall in 2–30**, so both readings are plausible on the
face of the string and nothing but knowledge of the instrument's article
count decides between them. A further 846 pack an Arabic letter on one side —
«(215/أ)», «(10 / أ)» — and those at least are unambiguous, because letters
are never article numbers.

Nine of the 43 missed statutory citations are packed forms.

## What the frame cannot see

Six citations in the 32 judgments lie outside the «مادة» frame entirely, and
they are outside it by construction, not by accident:

- **«وفقا للمواد (58 - 59 - 240) من اللائحة»** (judgment 11). Three articles
  under a plural head noun. Article 240 appears nowhere else in the judgment.
- **«واستنادا للمادة ( 53 ) و (55) من نظام الإثبات»** (judgment 22). One head
  noun, two articles; the second has no «مادة» of its own.
- **«بناءً على الفقرة الثانية من اللائحة الحادية والسبعين لنظام المحاكم
  التجارية»** (judgment 14). The court numbers the *article* with «اللائحة»
  as its head noun — "regulation seventy-one" for article 71 of the
  regulation. The word «مادة» does not occur.
- **«وحيث نصت (1/29) من نظام الإثبات»** (judgment 22). No head noun at all,
  and it is the evidential rule the judgment turns on.

Judgment 22 cites four articles. Two of them are invisible to any
«مادة»-keyed count. That is not a rounding error in a judgment that cites
four.

## What the judgments say about the claim

**79.9% of the gold citations are in the court's own voice** (127 of 159).
The remaining fifth belong to parties, and they are not evenly spread:
judgment 27 carries five citations across four instruments, of which four sit
inside the claimant's memorandum, reproduced verbatim in the recital, and one
is the bench's. An all-text count credits that judgment with five applied
articles; the court applied one. This is the same effect `UPTAKE.md`
measures at corpus scale, seen one judgment at a time.

Three judgments in the sample decide substantive liability with **no
statutory article at all**:

- judgment 16 awards SAR 400,126 on a guarantee, citing one article, on
  service of process;
- judgment 20 refuses litigation costs on Ibn Taymiyya, Muḥammad b. Ibrāhīm
  and the three elements of delict, citing two articles, both procedural;
- judgment 18, an appeal, affirms a dismissal citing nothing but article 2 of
  the parties' subcontract.

The procedural concentration the papers report is not an artefact of counting
citations rather than reasons. In these judgments the citations *are*
procedural because the reasoning is.

## Things a citation count cannot repair

Four failure modes here are properties of the published text, and no parser
recovers them:

1. **Duplicated records.** Judgment 18 is published twice, verbatim, inside
   one record; judgment 6 repeats one party's paragraph five times. Six
   occurrences, two applied articles.
2. **Concatenated instances.** Judgments 8, 10, 15, 19 and 26 each hold a
   first-instance and an appellate judgment in one record, with two benches,
   two sets of reasons, and the appellate one restating the first's citations.
3. **Misnamed instruments.** Judgment 30 cites article 16 twice, once from
   «نظام المحاكم التجارية» and once from «نظام المحكمة التجارية» — singular.
   A count that folds on the instrument string reports two statutes.
   `match_instruments` documents 1,706 hits on this one variant.
4. **Anaphora that does not resolve.** Judgment 3 cites «القاعدة الكلية
   الثامنة والعشرون من المادة (720) من ذات النظام سالف الذكر». The nearest
   named statute is نظام الإثبات, which has no article 720; the kulliyyāt are
   in نظام المعاملات المدنية. A hand-verified instance of the 1.2%
   out-of-range bucket `applied_articles.py` reports.

## Does any of this move a published claim?

No, and that is measured rather than assumed. `coverage_sensitivity.py`
re-counts the whole corpus with a deliberately permissive pattern that
accepts all seven forms and resolves anaphora to the last instrument named.
It recovers **64,123 citations, 55 per cent again on top of the 116,216 the
published pattern finds**, and the published claims barely move:

|                                  | published | permissive bound |     move |
| -------------------------------- | --------: | ---------------: | -------: |
| citations                        |   116,216 |          180,339 |   +55 %  |
| procedural share of citations    |    89.2 % |           89.7 % | +0.5 pt |
| top-10 instruments' share        |    96.9 % |           96.9 % |       0 |
| distinct articles ever cited     |     1,849 |            1,981 |    +132 |
| share of the statute book cited  |   11.66 % |          12.49 % | +0.83 pt |

The published column is recomputed in the same pass and reproduces
`UPTAKE.md`'s ALL_TEXT column to the digit, so the two are comparable.

Sixty-four thousand recovered citations add one hundred and thirty-two
articles — one new article per 486 recoveries. That is the finding, and it is
structural: the forms the pattern misses are overwhelmingly *back-references*
to an instrument the judgment has already named, so they land on instruments
and articles that are already in the count. An extractor blind to a quarter
of a judgment's citations can still measure the shape of the citation
distribution correctly, because what it is blind to is the repetition rather
than the range.

That is a defence of the papers' numbers and an indictment of nothing except
the recall figure itself, which is the one number this work does move: on
whole judgments the pipeline sees about two citations in three, not the
95 per cent a frame-selected sample suggests.

## What is not claimed

- These 32 judgments are Ministry of Justice commercial judgments. Nothing
  here is evidence about the committees' PDFs, whose failure modes
  (`EXTRACTION.md`) are typographic rather than syntactic.
- 32 judgments is a small sample; every interval above is wide and is printed
  wide on purpose. The corpus-wide counts in the table are censuses, not
  estimates, and carry no interval.
- No repair was made. The seven forms tabulated above are recorded so that a
  later parser can be tested against them on a set that has not been burned
  by fixing them.
