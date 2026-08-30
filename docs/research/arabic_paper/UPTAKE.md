# What the courts cite, and what the courts themselves cite

`uptake_by_voice.py`, over all 50,666 judgments. The published figures are
reported unchanged alongside the new ones and are not replaced.

Three columns, because the segment filter and the sample it can be applied to
are two different effects:

* **ALL_TEXT** — every judgment, every citation. This is what has been
  published.
* **ALL_TEXT_SEGMENTABLE** — the 27,321 judgments (53.9 per cent) that carry
  الوقائع → الأسباب → حكمت الدائرة, every citation in them. The like-for-like
  control: whatever moves between column one and column two is *selection*.
* **COURT_REASONING_ONLY** — the same judgments, citations inside الأسباب
  only. Whatever moves between column two and column three is *voice*.

| | ALL_TEXT | ALL_TEXT_SEGMENTABLE | COURT_REASONING_ONLY |
|---|---|---|---|
| citations | 116,216 | 74,638 | 49,204 |
| judgments with at least one | 40,888 | 23,893 | 21,988 |
| instruments ever cited | 106 | 96 | 68 |
| **procedural share** | **89.2 %** | 91.2 % | **94.5 %** |
| top-10 instruments' share | 96.9 % | 97.1 % | 98.3 % |
| **distinct articles cited** | **1,849** | 1,462 | **905** |
| as % of the statute book | 11.66 % | 9.22 % | **5.71 %** |
| as % within cited instruments | 20.4 % | 16.8 % | 12.9 % |

## Two things move, in opposite directions

**The procedural claim strengthens.** 89.2 → 91.2 → 94.5 per cent. Two points
of that is selection and three is voice, and both push the same way. The
sample-based estimate in `CLAIMS_AUDIT.md` predicted this from 183 hand-read
ministry citations (85.0 → 90.7); the census confirms it on 49,204.

**The applied statute book halves.** 1,849 distinct articles are cited
somewhere in a judgment; 905 are cited by a court in its own reasoning. As a
share of the 15,855-article registry that is 11.66 per cent against **5.71 per
cent**. Restricting to the bench's voice does not trim the count — it removes
half the articles that had been counted as applied.

Anyone quoting a coverage figure for *what Saudi commercial courts apply* has
to choose which of these two numbers they mean, and they are a factor of two
apart.

## Why the procedural share rises: it is the substantive instruments that go

Retention under the voice filter, column three over column two, so selection
is held constant:

| instrument | citations kept | distinct articles kept |
|---|---|---|
| Evidence Law | **82.1 %** | 99/117 |
| Arbitration Law | 68.9 % | 30/43 |
| Commercial Courts Law | 72.0 % | 74/93 |
| Sharia Procedure Law | 68.1 % | 103/170 |
| Bankruptcy Law | 64.6 % | 34/52 |
| **Civil Transactions Law** | **51.6 %** | 90/176 |
| Commercial Courts Implementing Regulation | 48.0 % | 113/151 |
| **Companies Law** | **38.2 %** | 128/172 |

The Companies Law keeps 38 per cent of its citations when the parties are
removed; the Evidence Law keeps 82. That is the mechanism behind the
headline: substantive instruments are disproportionately cited *by parties*,
procedural ones by the bench. An unfiltered count is therefore not neutral
between them — it systematically inflates the substantive side, which is the
side the "applied law is procedural" claim is measured against.

So the published claim is not an artefact of counting the parties' arguments.
Counting them *understates* it.

## One number that is selection, not voice

The Bankruptcy Law drops from 2,956 citations to 319 between columns one and
two, and only from 319 to 206 between two and three. Almost all of that loss
is judgments that do not carry the three headings, not the parties' voice.
Bankruptcy judgments are structured differently, and any bankruptcy figure
computed on segmentable judgments alone is a figure about a tenth of the
bankruptcy corpus. It is reported here rather than dropped.

## What this does not license

The three columns are the same extractor and the same instrument matcher
throughout; only the span changes. The extractor's own accuracy is measured
separately, on hand-labelled sets, and it is 68.8 per cent exact on ministry
judgments. These proportions are therefore proportions *of what the extractor
finds*, and the article-level figures in particular carry the extractor's
article-number error. `moj_article_gold.py` measures that at the article
level, on whole judgments read end to end; until it reports, the article
coverage figures above should be read as a ratio between columns rather than
as a level.
