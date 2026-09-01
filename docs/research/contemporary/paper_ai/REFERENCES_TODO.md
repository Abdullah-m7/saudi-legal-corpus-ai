# References — outstanding

The manuscript carries no citation list. This is deliberate and is disclosed
in §2 of the draft. **No reference in this file has been verified to exist**;
this is a list of the places a citation is needed and of what the citation has
to support, written so the author can fill it from the current literature.

**Rule for filling it.** Every entry must be read before it is cited. A
plausible-looking title, a DOI produced from memory, or a citation carried
over from another paper's reference list is not a reference. If a claim below
cannot be supported by something actually read, the claim is weakened or
deleted rather than propped up.

## A · Required before submission

These are load-bearing: the manuscript makes a positioning claim that a
reviewer will check against the literature.

| # | Where | What the citation must support | Notes for the search |
|---|---|---|---|
| A1 | §2, §4.3 | Deduplication of training corpora is standard practice, and the unit is the document or a long n-gram span | The near-duplicate-at-scale line of work; whichever papers the reader of this venue would expect |
| A2 | §2, §5 | The usual validation of a deduplication step is intrinsic — how much was removed, or a downstream score — rather than a demonstration that the removed material is the intended kind | If a size-matched random control **is** already reported somewhere, §5.4's "we are not aware of it being standard" must be softened or withdrawn |
| A3 | §1, §4.3 | Frequency statistics over a corpus are used to weight or rank in retrieval and in training | |
| A4 | §2, §6 | Legal IR reports coverage/recall/ranking at a point in time; index maintenance is treated as engineering | Case-law and statutory retrieval literature |
| A5 | §2, §7 | Chronological splits are the accepted remedy for temporal leakage in legal NLP evaluation | Also the general temporal-generalisation literature outside law |
| A6 | §7.1 | The change-point methods used — CUSUM, Page-Hinkley, piecewise level/trend — and permutation calibration of a detection statistic | Method citations, not claims |
| A7 | §4.1 | Banded minhash over shingles as the near-duplicate method that was built and set aside | Method citation |
| A8 | §3, §8 | Prior computational work on Arabic-language or Saudi legal corpora, if any exists | An empty result here is itself worth a sentence; it must not be *assumed* empty |

## B · Positioning — check before claiming novelty

The draft makes three claims of the form "we are not aware of X". Each must be
searched properly, and each must be either substantiated or removed. A claim
of novelty that a reviewer overturns in five minutes costs more than the
novelty was worth.

1. **§1** — the four assumptions are "never jointly tested". Search for any
   paper that tests more than one of independence / deduplication validity /
   index staleness / exchangeability on one legal corpus.
2. **§5.4** — the size-matched random-removal control "is not standard".
   Search deduplication and ablation methodology, including outside law:
   size-matched random ablation is a familiar idea in other fields and may
   have a name there. If it does, cite it and reframe the contribution as
   *importing* the control rather than proposing it — which is still a
   contribution and is honest.
3. **§6.3** — comparing index architectures on *drift* rather than on
   point-in-time coverage. Search index-maintenance and temporal-IR work.

## C · Legal sources — already verified, need citation form only

These are quoted from instruments held locally and recorded in
`ai_law_map.json` with the full Arabic text. They need a citation format
decision, not a search.

- اللائحة التنفيذية لنظام المحاكم التجارية، المادة الرابعة والعشرون (`ANCH-CCL-REG-24`)
- الأدلة الإجرائية لنظام الإثبات، المادة الثالثة والعشرون (`ANCH-EVID-PROC-23`)
- لائحة مقدمي خدمات التنفيذ، المادة السادسة عشرة (`ANCH-ENF-PROV-16`)
- اللائحة التنفيذية لنظام التوثيق، المادة العشرون (`ANCH-TAWTHEEQ-REG-20`)

Decisions needed: transliteration scheme; whether to give an English rendering
alongside the Arabic; whether to cite the official gazette issue.

## D · Self-citation

The companion paper on speaker attribution (`../paper/MANUSCRIPT.md`) is the
source of the court/party voice separation this paper uses in §3 and §6.3. If
it is under review or posted when this is submitted, cite it; if not, describe
the method inline instead of citing an unavailable draft.

## E · Explicitly not to be cited

- Anything generated rather than read.
- Anything found only as a title in another paper's bibliography.
- Any Saudi legal source not held locally in the repository, since the
  repository's rule is that a source is quoted from a text we hold or not
  quoted at all.
