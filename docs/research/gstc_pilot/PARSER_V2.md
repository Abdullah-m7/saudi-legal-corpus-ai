# Parser v2: two representation repairs, and what they moved

Two defects were found **after** all three held-out sets had been opened and
reported. Neither is a matching rule. Both are the text arriving as something
other than the characters it renders as, so every pattern in the project ran
against a string that was not the string the reader sees.

| defect | found by | scale |
|---|---|---|
| **Arabic Presentation Forms** — «ﺍﻟﻤﺎﺩﺓ» is six codepoints in U+FB50–U+FEFF, not the string «المادة» | assessing a candidate third source (`SOURCE_C.md`): six of the eight securities-committee bulletins are written this way and yielded **zero** citations | 30.2 % of ministry judgments carry some |
| **Combining marks on the head noun** — «المادَّة» with a shadda is the same word and not the same string | reading 32 whole judgments (`MOJ_ARTICLE_GOLD.md`) | 99.4 % of judgments carry marks somewhere |

The first is the more dangerous, and not because it is larger. A
presentation-form document does not fail loudly: it reads downstream as a
document that cites nothing, which is a legitimate value for that field.

## What changed

`canon/canonical.py` gains two rules, switchable and counted like the other
five, ordered before `lam_swap` because a document written in shaped glyphs
has no «ال» sequences for the transposition gate to count and would be
diagnosed as unbroken:

```
presentation   NFKC per character, only inside U+FB50–U+FDFF and U+FE70–U+FEFE
marks          strip U+064B–U+0655 and U+0670
```

`arabic_paper/voice_attribution.py` — which owns `CITE`, the pattern every
corpus analysis uses — gains two things. `CITE`'s head noun now tolerates
combining marks between and after its letters, so a caller that forgets to
normalise does not silently lose citations. And `normalise()` is exported for
callers reading sources other than the ministry API, because presentation
forms cannot be absorbed into a pattern: every letter is a different
codepoint. A caller that normalises must then work on the normalised string
throughout, since removing characters moves every offset after them.

Regression tests: `tests/test_canonicalisation.py` (presentation forms, five
marks, the transposition gate behind a mark, and «عمادة» left alone),
`tests/test_citation_forms.py` (eleven cases including the refusals). 67
parser tests pass.

## The freeze is now versioned

`freeze.py` archives the record it replaces under `frozen_history/`. **v1** is
`frozen_history/v1-8f55561bc215.json` — the layer against which
GSTC_TEST_FROZEN, MOJ_TEST_FROZEN and GSTC_TEST2_FROZEN were opened. **v2** is
the current `frozen.json`.

v2 also adds `voice_attribution.py` to the PARSER group. It was always a
parser file — `CITE` decides what counts as a citation for every corpus
figure the papers quote — and it was recorded in neither group, which is
exactly the omission a freeze exists to prevent.

## No held-out set was re-opened

27.7, 68.8 and 60.9 per cent exact are **v1 measurements and stay v1
measurements**. Re-scoring a spent set against repaired code produces a number
that is neither held out nor comparable, and spends the set to learn something
about two deterministic representation fixes that regression tests establish
directly. v2 will be evaluated by the next genuinely unseen source, or by a
held-out set built for it.

The article-level gold is the one evaluation that could be re-scored without
cost, because it was read by hand and never informed a repair.
`moj_article_metrics.py` under v2 returns **exactly** its v1 figures —
precision 88.1 %, recall 67.6 % at article level — because none of the 32
judgments happens to carry a mark or a shaped glyph inside a citation. The
gold's numbers are v1 and v2 alike.

## What moved in the corpus figures

Every analysis whose result depends on `CITE` was re-run. Old against new:

| figure | v1 | v2 | move |
|---|---:|---:|---:|
| citations found, whole corpus | 121,207 | 123,535 | **+2,328** (+1.9 %) |
| ALL_TEXT citations matched to an instrument | 116,216 | 118,585 | +2,369 |
| ALL_TEXT procedural share | 89.2 % | 89.3 % | +0.1 pt |
| ALL_TEXT distinct articles | 1,849 | 1,854 | +5 |
| ALL_TEXT share of the statute book | 11.66 % | 11.69 % | +0.03 pt |
| COURT_REASONING_ONLY citations | 49,204 | 49,582 | +378 |
| COURT_REASONING_ONLY procedural share | 94.5 % | 94.5 % | 0 |
| COURT_REASONING_ONLY distinct articles | 905 | 906 | +1 |
| COURT_REASONING_ONLY share of the statute book | 5.71 % | 5.71 % | 0 |
| first-instance reasons, procedural | 93.22 % | 93.25 % | +0.02 pt |
| appellate reasons, procedural | 95.58 % | 95.59 % | +0.01 pt |
| article number unparsed | 3,164 | 3,178 | +14 |
| above the instrument's own article count | 1,484 | 1,533 | +49 |

**Nineteen hundred more citations and not one claim moves.** Every published
figure is unchanged at the precision it is published to. The papers say
11.7 per cent of the statute book; v2 says 11.69 against v1's 11.66. They say
89 per cent procedural; v2 says 89.3 against 89.2.

That is the same lesson `coverage_sensitivity.py` reached from the other
direction. The citations these repairs recover are not in new places. They are
more instances of the instruments and articles that were already dominant,
because a shadda falls where a scribe put it and not where the law is
unusual.

## What is still missed, and is not being repaired

`citation_forms.py`, re-run under v2, now reports what the current parser
actually does rather than what v1 did:

| form | sites | still invisible |
|---|---:|---:|
| «المادة N من **ذات/هذا** النظام» | 4,310 | 4,294 |
| later members of an enumerated list | 2,263 | 2,263 |
| «المادة (N) **فقرة (M)** من …» | 1,022 | 800 |
| «المادة N من **لائحته** التنفيذية» | 379 | 166 |
| bracketed number with no head noun | 279 | 279 |
| **head noun carrying marks** | **234** | **1** ← repaired in v2 |
| head noun truncated to «الماد» | 4 | 4 |

The first five are *grammar*, not representation: they need the pattern to
understand anaphora, lists and postfix paragraphs, which is a different and
larger change with a real risk of false positives. They stay recorded and
unrepaired, and `coverage_sensitivity.py` bounds what they cost — 55 per cent
more citations, half a point of composition.

## A residual, stated rather than hidden

The corpus analyses run `CITE` on raw text, not on `normalise()`d text,
so they get the mark repair through the pattern but not the presentation-form
repair. Measured directly: normalising first would add **304 citations across
233 judgments**, 0.25 per cent of the total. Retrofitting `normalise()` into
fourteen analyses, several of which attribute citations to text segments by
offset, would risk more than it gains on this corpus, and mixing normalised
and un-normalised analyses would make their figures incomparable. So all of
them stay on raw text, uniformly, and the residual is written down here
instead of being left for a reader to find.

It is not a residual for any other publisher. A source encoded like the
securities-committee bulletins loses everything without `normalise()`, which
is why it exists.
