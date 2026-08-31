# What this repository is, as a scientific asset

Not a file list. A statement of what can be *asked* of it, what each answer is
worth, and where each stops. The test applied throughout: can this answer a
question no other accessible dataset can answer, with evidence that can be
reproduced and audited?

---

## 1 · Machine-readable Saudi statutory corpus

**Scope.** 291 registry tracks; article-level Arabic text with per-article
legal status (original / amended / repealed), cross-checked against the MOJ
legal portal. 2,039 articles across the eight instruments that carry
contemporary commercial adjudication.

**Validated.** Yes, per track, against the publisher's own source.

**Limits.** 291 tracks are not 291 distinct instruments — one is a closure
audit. Coverage is statutory; it is not a case-law corpus.

**Answers.** Which articles exist; what an instrument contains; what has been
amended.

## 2 · Published judgment corpus with structure

**Scope.** 50,666 MOJ judgments, 1422–1448 AH, with Hijri date, court, court
type, case number, and the publisher's section fields — which is what makes
voice segmentation possible at all.

**Validated.** Provenance recorded per record; publisher redaction preserved
and extended.

**Limits.** ~95 % commercial. Selection into publication is not random and the
share carrying reasons moved from 2 % to 88 % across the span. **This is the
single most important limitation in the repository** and every conditional
figure names it.

**Answers.** What was decided, when, by which court — for published commercial
judgments only.

## 3 · Validated citation extraction (parser v2)

**Scope.** Article-level citation grammar over both statutory and judgment
text, with canonicalisation for damaged PDF text layers (seven rules,
including presentation forms and combining marks).

**Validated.** Three held-out sets, opened once each, at parser v1: 27.7 %
exact on committee digests (burned), 68.8 % on ministry judgments, 60.9 % on
GSTC_TEST2 zero-shot. Article-level, over 32 whole hand-read judgments: 88.1 %
precision, 67.6 % recall. **v2 is deliberately unevaluated on a held-out set**
— it repairs two representation defects found afterwards, and no set was spent
to validate two deterministic fixes.

**Limits.** Six citation forms remain invisible, chiefly the anaphoric «من ذات
النظام» (4,294 corpus-wide). `coverage_sensitivity.py` bounds the cost: 55 %
more citations recoverable, half a point of composition change.

**Answers.** Which article a passage cites, with a known and bounded error.

## 4 · Speaker-aware authority layer ★

**Scope.** 160,157 authority mentions across 44,144 contemporary judgments
(1442–1446), each typed into nine authority families, placed in a segment,
attributed to a speaker under two specifications, flagged for quotation, and —
for statutes — resolved to a registry track and a normalised article number
with a `named | anaphoric` confidence field. 2.9 MB gzipped, no judgment text.

**Validated.** Types 126/126 on an independent sample; speaker 12/12 court and
10/12 strict party on a pre-registered gate that **failed** on the facts
segment (7/12) and cost the headline claim three of nine contrasts.

**Limits.** Party attribution is bracketed by two specifications, not solved.
One primary annotator; no inter-annotator agreement is claimed.

**Answers.** What authority types courts use; what litigants use; how often
they overlap; how it varies by year; what combinations occur inside one
judgment — **without re-parsing anything.** This is the layer that makes the
rest cheap.

## 5 · Authority taxonomy with an audit trail

**Scope.** Nine types, thirteen rules, each with an id that survives into
every result and an attested corpus example. Built from a census of 36
candidate markers over all 50,666 judgments, four of which scored zero and
were dropped.

**Validated.** 18 regression tests hold every repair the gold samples forced.

**Limits.** Unattributed doctrinal reasoning carrying no marker is
unobservable by construction and counts as no explicit authority.

## 6 · Contemporary reasoning map

**Scope.** Four re-runnable windows with stated composition; court/party
authority distribution; hybrid rates; procedural split; concentration.

**Validated.** Every figure regenerated from the layer; 104/104 manuscript
figures traced by `paper/check_paper.py`.

**Limits.** Descriptive. No causal claim; the pre/post windows are not a
natural experiment.

## 7 · Operational statutory core

**Scope.** The smallest set of articles carrying 50 / 75 / 90 % of the bench's
own statutory citations, per window and per year, with rank trajectory. Seven
articles carry half of contemporary_3y; five by 1446.

**Limits.** **Adjudicatory visibility only.** An uncited article is not an
inoperative one — it may be so clear nobody litigates it. The limitation is
written into `core_view.json` itself, not only into prose.

**Answers.** Which law is repeatedly operational; how long a new statute takes
to arrive (Evidence Law ≈ 1 year; Civil Transactions Law not yet, after two).

## 8 · Law-in-action profile

**Scope.** 2,039 enacted articles against 683 the bench ever cites (33.5 %),
profiled on length, position, amendment status and textual function.

**Answers.** *What kind* of article becomes operational: earlier in its
instrument (29th percentile against 55th), longer, carrying jurisdiction
vocabulary (15.4 % vs 1.5 %) or proof vocabulary (20.5 % vs 2.7 %), and 13
times more likely to have been amended.

**Limits.** Descriptive, no model, and the amendment association is not read
causally in either direction.

## 9 · Hybrid reasoning view

**Scope.** Every contemporary judgment classified as statute-only,
non-statute-only, hybrid, or no explicit authority, with the family
combination for hybrids, per year.

**Answers.** Contemporary Saudi hybrid reasoning is one statute plus one
jurist: STATUTE+FIQH is 40.4 % of hybrids, and two thirds to three quarters
combine exactly one non-statutory family. Hybrid judgments cite no more
statutory articles than statute-only ones (median 2 against 2).

## 10 · Authority graph

**Scope.** An edge list, gzipped CSV: 45 role→authority edges, 36
co-occurrence edges, 93,349 judgment→article edges. No graph database.

**Answers.** Concentration, co-occurrence, article centrality, institution
comparison — as table operations.

## 11 · Multi-institution pilot

**Scope.** 33 tax and zakat committee digests beside the ministry corpus,
compared **only** on the two metrics both support.

**Limits.** Voice is not comparable (no reasons headings); document rates are
not comparable (a digest holds scores of decisions); and abridgement could
produce the whole difference. All three are stated wherever the comparison
appears.

## 12 · Held-out discipline as an artefact

**Scope.** `HELD_OUT.md`, `frozen_history/`, three gold samples with declared
roles, a pre-registered gate that failed, and a claim-delta ledger recording
what each measurement did to each paper.

**Why it is an asset.** It is the part that makes the rest citable. A reader
can see which numbers are held out, which are burned, which parser version
produced them, and which claims were withdrawn and why.

---

## What no other accessible dataset can answer

1. What kinds of legal authority Saudi commercial courts invoke **in their own
   voice**, separated from what litigants argue.
2. Which articles of the Saudi statute book are repeatedly operational in
   adjudication, and how quickly a new code arrives.
3. What contemporary statutory/fiqh hybrid reasoning looks like, at scale and
   by year.
4. How far a court's cited materials overlap the litigants' — including that
   in four paired judgments out of five, they share no article.

## What it cannot answer, and should never be asked

Anything about Saudi adjudication **generally** — personal status, criminal,
administrative, labour, unpublished decisions, or settlement. The corpus is
commercial and published, and every claim in this repository says so.
