# Decomposing the 79.7 per cent

The manuscript's sharpest number was that in 79.7 per cent of judgments where
both sides are identified, they cite no article in common. It had an obvious
objection, and the objection is the reason to test it rather than to publish
it: a court decides jurisdiction whether or not jurisdiction was argued, and
the consequences of a defendant's absence whether or not absence was pleaded.
If the articles the bench "adds" are mostly its office, then the number is a
fact about the judicial role, not about legal disagreement.

It survives, and in surviving it changes shape.

## 1 · A function taxonomy, hand-validated

Articles are classified from their own enacted text into three classes:
**STRUCTURAL_PROCEDURAL** (invoked by virtue of the office — jurisdiction,
service, attendance and default, standing, appeal and finality, costs, case
management, definitions), **DISPUTE_SPECIFIC** (applied because of what this
dispute contains — proof rules brought to bear on the documents actually
filed, obligation, damages, corporate, insolvency, arbitration, enforcement),
and **AMBIGUOUS**.

The line was drawn where the question needs it. Evidence Law art. 29 — an
ordinary document is proof against the person who signed it — is
**dispute-specific**: no court reaches for it unless a party produced a
document. Commercial Courts Law art. 16 — jurisdiction — is structural.

Validated by hand on the 25 most-cited articles plus 35 drawn from the cited
tail (`function_gold.json`): **structural precision 13/14 (92.9 %), dispute
precision 5/5.** The one error is instructive — Evidence Law art. 21 was
called structural, but its text is the court ordering a party to attend for
*interrogation*, which happens because the dispute turns on that party's
answer.

The finer thirteen-function taxonomy is **not** reliable at function level
(CCL 30 was labelled "service" when its text is about default appearance) and
is reported only as a descriptive aid, never as a result. And the AMBIGUOUS
class is a genuine residual — 12.8 per cent of the top-50 core's citations —
so **every figure below is a band**: the lower bound excludes structural
articles only, the upper bound excludes structural and ambiguous both.

## 2 · The overlap, recomputed

contemporary_3y, strict specification (the wide specification is in
`overlap_results.json` and tells the same story two to ten points lower):

| level | n | median J | no overlap | exact |
|---|---:|---:|---:|---:|
| F · authority family | 4,313 | 0.500 | 26.9 % | 34.1 % |
| D · instrument, all | 2,698 | 0.333 | 42.5 % | 15.5 % |
| D · instrument, structural removed | 1,190 | 0.333 | 48.5 % | 30.1 % |
| D · instrument, dispute-specific only | 253 | **1.000** | **18.6 %** | **73.9 %** |
| A · article, all | 2,621 | 0.000 | **80.2 %** | 3.0 % |
| B · article, structural removed | 1,190 | 0.000 | **78.5 %** | 6.8 % |
| C · article, dispute-specific only | 253 | 0.000 | **56.5 %** | 24.9 % |

**Removing the law the court must invoke does not explain the divergence.**
The article-level non-overlap moves from 80.2 to 78.5 per cent — under two
points — when structural articles are excluded. Only when the comparison is
narrowed to strictly dispute-specific articles does it fall, to 56.5 per cent,
and even then a clear majority of paired judgments share no article.

## 3 · But they are not in different codes

The instrument row is where the picture changes. Restricted to
dispute-specific articles, the two sides use the **same instrument** in 73.9
per cent of judgments and no shared instrument in only 18.6 per cent.

Conditioning makes it explicit:

```
P(shared instrument | both cite statute)   56.2 %  strict   63.5 %  wide
P(shared article    | shared instrument)   35.3 %           47.0 %
P(shared article    | both cite statute)   19.8 %           29.9 %
```

Per instrument, among judgments where both sides use it:

| instrument | judgments | same article |
|---|---:|---:|
| arbitration law | 34 | 64.7 % |
| sharia procedure law | 159 | 46.5 % |
| evidence law | 213 | 38.5 % |
| companies law | 148 | 37.8 % |
| civil transactions law | 36 | 27.8 % |
| commercial courts law | 758 | 27.4 % |
| commercial implementing regulation | 159 | **12.6 %** |

**This is the finding, and it is not the one the manuscript claimed.** Court
and litigants are not reasoning in different legal universes. They reach for
the same code roughly six times in ten, and inside that same code they land on
the same provision three to five times in ten. The divergence is **intra-code**.

The variation across instruments is legible. The Arbitration Law behaves
almost like a single rule — art. 11, the mandatory stay — so both sides find
it. The commercial implementing regulation is a 281-article procedural manual
the bench navigates and the parties barely touch, and its agreement rate is
the lowest in the table at 12.6 per cent.

## 4 · Claim and response: a twelve-judgment pilot

A transition matrix cannot see whether the court *engages* the proposition put
to it. Twelve judgments where a party cites a specific article and the court's
reasons cite one were read in full (`pairs_gold.json`).

**Pairing is identifiable at judgment level (12/12) and not at proposition
level.** The court almost never names the party's article in order to reject
it; it simply reasons elsewhere. So the six-way taxonomy — adopt, adopt with
addition, reject on the same authority, reject on different authority,
procedural bypass, no response — **is not codeable on this corpus**, because
for four of its six codes there is nothing in the text to read. It collapses
to three that are:

| code | n |
|---|---:|
| **ANSWERED_ON_OTHER_LAW** — the court decided on law the party had not cited | **8** |
| **ENGAGED_SAME_ARTICLE** — the court adopted the party's article, adding others | 2 |
| **MOOTED** — settled or withdrawn before the law mattered | 2 |

One case matters beyond its weight. In C05 the court adopts the party's
Arbitration Law art. 11 and writes it as «نص نظام التحكيم … في مادته المادة
الحادية عشرة» — the instrument-first possessive form the extractor
under-reads. **Measured engagement is therefore a lower bound**, and the
direction of that bias is against the finding rather than for it.

## 5 · What the core actually does

Classifying the operational core by function:

| | structural procedural | dispute-specific | ambiguous |
|---|---:|---:|---:|
| top 10 articles | **78.5 %** | 21.5 % | — |
| top 25 | 72.2 % | 18.8 % | 9.0 % |
| top 50 | **67.4 %** | 19.9 % | 12.8 % |

By function, the top 50: jurisdiction 27.3 %, proof rules 19.9 %, service
16.5 %, appeal and finality 6.5 %, default 5.7 %, costs 4.1 %.

**Contemporary Saudi commercial law-in-action is not a core of obligation
rules. It is a core of judicial operation** — who may hear this, was the
defendant told, may this document prove the claim, who pays, is it final. The
substantive law of contract and obligation is the 20 per cent.

## 6 · What this does to a retrieval system

Ranking the same 1,617 articles three ways — by frequency in full judgment
text, in the court's reasons only, and in the parties' arguments only:

| | full ∩ court | full ∩ party | court ∩ party |
|---|---:|---:|---:|
| top 10 | 8 | 7 | 5 |
| top 50 | 43 | 29 | 23 |
| top 100 | 84 | 68 | 55 |

Spearman over all articles: full/court **0.835**, full/party 0.848,
**court/party 0.564**.

The single vivid case: **art. 90 of the commercial implementing regulation is
the third most-cited article in full text (5,108) and is not in the court's
top three at all.** It is the preparatory-hearing formula, recited in the
statement of facts of tens of thousands of judgments. A retrieval system
grounded on full judgment text would rank a docket-management formality as
among the most important provisions in Saudi commercial law.

Seven of the court's top 50 articles are absent from the full-text top 50.

## 7 · Consequence for the manuscript

| claim | status |
|---|---|
| authority-**type** divergence between the voices, six of nine categories | **STRENGTHENED** — untouched by this decomposition, and the negative controls hold |
| article-level non-overlap is not explained by the judicial office | **STRENGTHENED** — 80.2 → 78.5 per cent when structural law is removed |
| "courts and litigants cite different articles" | **REFRAMED** — they mostly cite the *same code* and differ *within* it: 56–64 per cent share an instrument, 35–47 per cent of those share an article |
| the divergence is total or near-total | **NARROWED** — 56.5 per cent among dispute-specific articles, not 79.7 |

The manuscript gains a second pillar and loses a rhetorical flourish. The
honest statement of the article-level result is now:

> Court and litigants reason from the same statute book and largely from the
> same codes, but land on different provisions within them; and the difference
> is not explained by the articles a court must invoke by virtue of its office.

## 8 · The profile, and what comes next

`contemporary_commercial_adjudication_profile.md` is generated by
`profile.py` from six result files and holds every figure this layer can
state about published commercial adjudication of 1444–1446 in one place: the
corpus, who invokes what, the shape of the reasons, where the two voices
meet, the operational core, enacted against operational, and what a retrieval
system would learn. It is named for what it measures. It is not a profile of
the Saudi judiciary and the first paragraph says so.

The next question is chosen in `NEXT_PROGRAMME.md`, on the evidence this
decomposition produced: the alignment programme is blocked at proposition
level by its own pilot, and what the decomposition exposed instead is that
the bench's reach outside the statute book is a property of the *article* it
is citing — from 1.1 per cent of judgments to 85.9 — which the
structural/dispute-specific distinction explains three points of.
