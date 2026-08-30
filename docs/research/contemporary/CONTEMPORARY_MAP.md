# The Contemporary Saudi Legal Reasoning Map

What law is actually invoked in Saudi commercial adjudication now, by whom,
and in what role.

This repository had been reading its corpus as a time series. That is the
wrong frame for the question that matters. The primary object here is a
window on the recent years; history enters only where a recent reform makes a
before/after design valid, and the year series below carries its own
selection control precisely so that it cannot be read as one where it is not.

Everything is re-runnable: `windows.py`, `authority.py`, `gold.py`, `map.py`,
`institutions.py`.

## 1 · The contemporary window

Four views. None is balanced and none is made balanced: balancing a window on
a corpus whose publication practice changed would be inventing judgments.
Each states its composition instead.

| view | years | judgments | with reasons | reasoned % | median reasons |
|---|---|---:|---:|---:|---:|
| contemporary_5y | 1442–1446 | 44,144 | 27,027 | 61.2 | 1,503 |
| contemporary_3y | 1444–1446 | 28,090 | 23,626 | 84.1 | 1,540 |
| post_Evidence | 1443–1446 | 33,370 | 26,787 | 80.3 | 1,504 |
| post_CTL | 1445–1446 | 9,278 | 7,191 | 77.5 | 1,645 |

Reform dates are quoted from the judgments, never from memory
(`windows.py --decrees` prints the sentences):

| instrument | decree | date | written out in |
|---|---|---|---:|
| Commercial Courts Law | م/93 | 15/08/1441 | 847 judgments |
| Evidence Law | م/43 | 26/05/1443 | 107 |
| Civil Transactions Law | م/191 | 29/11/1444 | 28 |
| Personal Status Law | م/73 | 06/08/1443 | **1** |

**Personal status is out of scope and the corpus says so.** One judgment in
50,666 writes the statute out; 28 judgments in the whole corpus come from a
personal-status court. This map is about *commercial* adjudication, plus the
tax and zakat committees. 1447 and 1448 are excluded: 90 and 277 judgments
are not years, they are the leading edge of a collection still filling.

## 2 · Gold validation, before anything was believed

A classifier cannot be validated on its own hits: that measures precision and
calls it accuracy. So each sample has two halves — rule hits stratified by
rule id, and sentences drawn at random from court reasoning with no rule
applied.

**Sample 1 (seed 23, development)** — 126 hits + 80 sentences, read by hand.
It found six defects, none visible from the rule text:

| defect | scale in the sample | repair |
|---|---|---|
| `contract.possessive` caught statutes: «نظام التحكيم في مادته (11)» | 8 of 9 wrong | referent resolved by reading back 70 chars; becomes `statute.possessive` |
| `custom.trade` fired inside quoted article 164, whose own words list «العرف، أو العادة المستقرة» | 7 of 9 wrong | quoted passages detected and held apart everywhere |
| `hadith` matched «المتفق عليه» — *the agreed-upon* — as «متفق عليه» | 4 of 9 wrong | lookbehind; 16,279 hits → 6,942 |
| `discretion` matched «ما تراه الدائرة», ordinary evaluative language | ~2 of 9 | alternative dropped |
| speaker read from the nearest cue mislabelled the bench as a party | 3 reasoning items | voice decided structurally |
| markers with no rule at all | recall half | «المستقر فقهاً», «المقرر قضاءً», ﷺ, «الكتاب والسنة», «حديث حسن صحيح» |

**Sample 2 (seed 47, validation)** — an independent draw, opened once after
the repairs. 126 hits read by hand: **every one correct at the type level**,
including all nine `possessive` items, which the repair moved from contract to
statute and which are all statutes. One edge case is recorded rather than
scored away: «النظام الأساسي لشركة (...) في مادته رقم (١٨)» is a company's
constitution, which the rule calls a statute because «النظام» precedes it.

Its recall half found five further misses — a regulation cited as «في لائحتها
الأولى», «مجموع فتاوى» without the article, bare «متقرر فقهاً», an instrument
invoked with no article at all, and a list-trailing article. The first three
are fixed; **those fixes are not themselves validated** and await a third
sample. The last two are known extractor gaps recorded in
`gstc_pilot/MOJ_ARTICLE_GOLD.md` and are not repaired here.

18 regression tests hold every repair in place (`tests/test_authority_typology.py`).

## 3 · Court against party: they do not speak the same legal language

Share of all authority mentions, contemporary_3y, quoted passages excluded:

| authority | the bench's own reasons | a party's argument | ratio |
|---|---:|---:|---|
| statute | 70.6 % | 55.2 % | 1.3× court |
| **contract** | **0.9 %** | **14.9 %** | **16× party** |
| fiqh, named source | 14.8 % | 8.1 % | 1.8× court |
| **legal maxim** | 1.1 % | 4.6 % | **4× party** |
| **custom** | 0.9 % | 3.8 % | **4× party** |
| hadith | 6.0 % | 8.3 % | 1.4× party |
| Qur'an | 2.5 % | 3.7 % | 1.5× party |
| judicial principle | 1.5 % | 1.0 % | 1.5× court |
| discretion named | 1.7 % | 0.6 % | 3× court |

The divergence is not a matter of degree. **A litigant argues from the
contract, from maxims and from custom; the bench answers from the statute,
from named fiqh, and from its own discretion.** The contract is the single
sharpest split in the corpus: it is 15 per cent of what parties invoke and
under 1 per cent of what courts do.

That has a methodological consequence for every citation study of this
corpus, including this project's own earlier papers: an all-text count is not
a diluted picture of judicial reasoning, it is a blend of two different
languages, and the contract and the maxim are almost entirely the parties'.

## 4 · Hybrid reasoning: the codes joined the fiqh

Judgments with reasons, classified by what the **bench** invokes in its own
voice:

| view | statute + non-statute | statute alone | non-statute alone | neither |
|---|---:|---:|---:|---:|
| contemporary_5y | 28.7 % [28.1, 29.3] | 53.5 % | 5.8 % | 12.0 % [11.6, 12.4] |
| post_Evidence | 27.8 % [27.3, 28.4] | 53.7 % | 6.0 % | 12.6 % [12.2, 13.0] |
| post_CTL | **31.2 %** [30.2, 32.3] | 55.5 % | 4.1 % | 9.2 % [8.5, 9.9] |

**Nearly a third of contemporary reasoned judgments combine statutory and
non-statutory authority in the same reasons, and the share is highest in the
most recent view.** Reasoning from non-statutory authority *alone* is rare
and falling; reasoning from both is common and rising. Whatever codification
did, it did not put the courts on one side of a substitution.

## 5 · Silence, not fiqh, is what the reforms displaced

The per-year series, with the selection control in the second column, because
whether a circuit writes its own reasons moved from 2 per cent to 88 per cent
across this corpus and everything else is conditioned on it:

| year | judgments | reasoned % | hybrid | statute alone | non-statute alone | **no authority** |
|---|---:|---:|---:|---:|---:|---:|
| 1442 | 10,774 | **2.2** | 19.6 | 46.7 | 10.4 | 23.3 |
| 1443 | 5,280 | 59.9 | 21.2 | 54.8 | 7.0 | 17.1 |
| 1444 | 18,812 | 87.4 | 27.6 | 52.6 | 6.6 | 13.2 |
| 1445 | 6,800 | 88.0 | 31.8 | 54.8 | 4.1 | 9.3 |
| 1446 | 2,478 | 48.8 | 28.2 | 59.0 | 4.1 | 8.8 |

**1442 is not an early year of this series and is not read as one.** At 2.2
per cent reasoned it is a different population, selected by whatever made 237
judgments of 10,774 publish their reasons. The comparable span is 1443–1446.

Across it:

```
reasoning with NO explicit authority     17.1 %  ->   8.8 %     −8.3 points
reasoning from non-statute ALONE          7.0 %  ->   4.1 %     −2.9 points
reasoning from both                      21.2 %  ->  28.2 %     +7.0 points
```

**The reduction in uncited reasoning is roughly three times the reduction in
non-statutory-only reasoning, and total non-statutory use rises** — from 28.2
to 32.3 per cent of reasoned judgments once hybrid is counted in. This is the
hypothesis `CODIFICATION.md` could only gesture at, now tested on a design
that carries its own selection control: the reforms displaced silence.

## 6 · Procedural against substantive

**94.4 per cent** of the statute citations in the bench's own reasons
(contemporary_3y) are to procedural instruments; 93.3 per cent in post_CTL.
This reproduces `UPTAKE.md`'s 94.5 per cent from an independent path and is
the one figure in this map that was already known.

The split is assigned only where it is validated — from the instrument's
class in `match_instruments.PROCEDURAL`. For fiqh, maxims and scripture it is
reported as unknown rather than guessed: a maxim can carry either and a
marker count cannot see which.

## 7 · Contemporary concentration: five articles carry half of it

The bench's own reasons, contemporary_3y, article numbers normalised across
«١٦», «16» and «السادسة عشرة»:

| | share of the bench's article citations |
|---|---:|
| top 5 articles | **47.0 %** |
| top 10 | 57.4 % |
| top 20 | 67.5 % |
| top 50 | 80.6 % |

929 distinct (instrument, article) pairs across 28,090 judgments.

| citations | article |
|---:|---|
| 8,626 | Commercial Courts Law **art. 16** — jurisdiction |
| 4,571 | Commercial Courts Law **art. 30** — default appearance |
| 3,780 | Evidence Law **art. 29** — the ordinary document as proof |
| 1,370 | Commercial regulation art. 164 — costs |
| 1,367 | Sharia Procedure Law art. 76 — dismissal for want of standing |

Instruments are more concentrated still: one instrument is 45 per cent, three
are 79.9 per cent, five are 93.8 per cent.

**Contemporary Saudi commercial adjudication runs on about five articles.**
Every one of the top five is procedural: who may hear the case, what happens
when a defendant does not appear, when a document proves itself, who pays,
when a claim fails for standing. The Civil Transactions Law, the largest
substantive codification in the country's history, accounts for 508 citations
in the post_CTL view against the Commercial Courts Law's 6,758.

## 8 · MOJ against the committees, only where both support it

| authority | MOJ commercial courts | tax and zakat committees |
|---|---:|---:|
| statute | 70.7 % | **96.1 %** |
| fiqh, named source | 11.6 % | 0.2 % |
| hadith | 6.0 % | 0.1 % |
| Qur'an | 2.3 % | 0.2 % |
| legal maxim | 1.7 % | 0.8 % |
| contract | 3.8 % | 0.0 % |

Instrument concentration: MOJ top-3 76.1 %, committees top-3 **93.6 %**.

Three restrictions, all structural:

1. **Voice is not comparable and no voice-conditioned figure is reported.**
   The committees' digests carry no «الأسباب» headings, so the bench's reasons
   cannot be separated from the parties' pleadings in them. The court/party
   map, the hybrid rate and the silence rate exist for the ministry only.
2. **Document rates are not comparable.** A ministry document is one
   judgment; a committee document is a digest of scores of decisions.
3. **Abridgement could produce this on its own.** The committees publish
   «مختزلة» — abridged — decisions. A publisher who summarises to the
   statutory basis and drops the reasoning would generate exactly this
   difference. This comparison cannot separate an institution that reasons
   differently from a publisher that summarises differently.

With those held: the committees' authority structure is nearly purely
statutory where the courts' is not. It is stated as a difference between two
publishers' *records*, and it is not a claim about the Saudi judiciary.

## 9 · What this map does not establish

- It is descriptive. No causal effect of any statute coming into force is
  identified, and the pre/post views are not a natural experiment.
- It counts *invocations*, not reasons. A court may decide from the code and
  dress the result in Ibn Taymiyya, or the reverse; nothing here separates
  those.
- The subject mix across years is unmeasured, and two of the authority
  families are subject-sensitive.
- The statute detector remains blind to the anaphoric «من ذات النظام» form
  and five others (`gstc_pilot/citation_forms.py`). `coverage_sensitivity.py`
  bounds what that costs at half a point of composition; the bound was not
  re-run inside these views.
