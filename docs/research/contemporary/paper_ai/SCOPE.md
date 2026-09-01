# Scope map — *Artificial Intelligence and Law*

Written for the author, not for an editor. **Nothing here is a cover letter,
and no journal has been contacted.** It exists so that the decision to submit,
or not to submit, is made against the journal's own words and against what the
paper now actually contains.

## The journal's stated scope

The desk rejection of the first manuscript (submission `77a23208-7dd6-429c-8c7d-fee4fa575fc5`)
quoted the scope. Papers should address:

> the development of formal or computational models of legal knowledge,
> reasoning, and decision making

or be

> in-depth studies of innovative artificial intelligence systems that are being
> used in the legal domain, where the study focuses on the novel aspects of the
> technical implementation

and studies of legal, ethical or social implications are considered

> where a demonstrable link is made to the work's original research
> contributions that are of a technical, empirical, or formal nature.

The stated ground of rejection was scope: *"After skimming the paper, I have
found its scope to be rather limited."*

## Why the first paper did not clear it

`../paper/MANUSCRIPT.md` argues that citation measurement over judgments needs
speaker attribution, and demonstrates it on 28,090 judgments. Read against the
scope above it is an **empirical legal studies** paper: the contribution is a
measurement-validity claim about a legal corpus, and the AI relevance is an
implication section. `../paper/VENUES.md` already ranked JELS first for it,
which was the correct reading. That paper is not withdrawn and is not weakened
by this one.

## Why the second draft did not clear it either, before the experiment

The first version of this manuscript measured four corpus properties and then
explained, in a late section, that Saudi law permits AI in court procedure.
That is the same failure in a new costume: the AI relevance arrived after the
results rather than inside them. A reviewer skimming it would have found
corpus statistics plus a legal epilogue.

The manuscript now carries an experiment, and the AI connection is visible at
every level the editor's scope asks about:

| level | where the AI content is |
|---|---|
| **question** | §1: does a preprocessing step change *retrieval performance* beyond its volume, and what does index age cost a retrieval system? |
| **method** | §5: a legal retrieval task, a BM25 index over article pseudo-documents, six leakage controls, ten temporally-fenced folds |
| **experiment** | §5.5: the same retriever across RAW / FORMULA_DEDUP / MATCHED_RANDOM / FROZEN_kQ / FROZEN_kQ_VOLUME / PLUS_PARTY / RAW_NO_FP_LEAK |
| **result** | §6 and §7: MRR@10 and recall differences with their controls, and a decomposition of staleness into age and size |

§9 (the enacted AI provisions) is now marked in its own first sentence as
context that **does not carry the paper's fit**, and the paper would stand if
it were deleted.

## What this paper offers against each clause

| Scope clause | This manuscript | Honest strength |
|---|---|---|
| formal or computational models of legal knowledge and reasoning | Not claimed. No model of legal reasoning is proposed | **Not the route in.** Do not argue this clause |
| in-depth study of an AI system used in the legal domain, focused on technical implementation | A retrieval system is built, indexed seven ways, fenced, and measured. It is not a deployed system and we do not pretend otherwise | **Moderate** |
| original research contribution of a technical or empirical nature | §6: a controlled result on 105575 real citations, with a per-fold matched-volume test and a dose–response pattern. §7: staleness decomposed into age and size. §4: the redundancy unit and what it inflates | **Strongest. This is the claim** |
| implications with a demonstrable link to that contribution | §9 is two enacted provisions and one corpus count, explicitly attached to §5–§7 rather than substituting for them | **The link is now the right way round** |

## The sentences the paper has to survive

*"This is corpus statistics with a legal veneer."* — no longer available: the
dependent variable is a retrieval metric on a legal task, measured seven ways.

*"The task is not novel."* — correct, and the paper says so first, in §1 and
§5.1. The task is an instrument. Attacking it attacks something the paper does
not claim.

*"The control is not novel either."* — also correct, also conceded first
(§2, §6.5), with the contribution restated as a domain-specific requirement.
The literature audit that forced this concession is `REFERENCES_TODO.md`.

*"BM25 only."* — the real exposure. The answer in §10 is that a dense
retriever answers a different question, and that a simple retriever is what
makes the corpus the only moving part. A reviewer may still want it. If one
does, it is a revision, not a rejection — the layer supports it without a new
corpus pass.

*"One jurisdiction."* — conceded in §10, with the requirement in §6.5 claimed
to transfer precisely because the *direction* of the result may not.

## Before any submission

1. Read P2 and P6 in `REFERENCES_TODO.md` in full. P2 (*(Near) Duplicate
   Subwords*) is the closest published argument to §6 and may change how it is
   framed; P6 (CLEF LongEval) is the most likely place for §7's decomposition
   to already exist. If either lands, this file is wrong and the manuscript
   changes.
2. Fill the reference list properly. Nothing cited unread.
3. Check the journal's current format, length and blinding rules on its own
   site.
4. The Springer transfer offer from the first submission does not apply. This
   is a different manuscript, and offering it as a transfer would misdescribe
   it.
5. `python3 check_paper2.py` must pass and `python3 ../../check_fresh.py` must
   report every result current.

**No journal is to be contacted and nothing is to be submitted without the
author.**

## Controller recheck — 2026-09-01

The current live Aims & Scope strengthens, rather than weakens, the fit. It explicitly lists **intelligent processing of legal documents; conceptual retrieval of cases and statutes**, **evaluation and auditing techniques for legal AI systems**, and **systemic problems in the construction and delivery of legal AI systems**. This manuscript now directly measures all three at the retrieval/preprocessing layer.

The 2026 journal record also contains empirical legal citation prediction, legal QA/RAG evaluation, and legal-LLM robustness/reliability studies. The correct question is no longer whether retrieval evaluation is in scope; it is whether this paper's controlled result is sufficiently original and consequential.

Full reading of Schäfer et al., LongEval, Liu et al., Ovcharov, Web2Text and the other load-bearing neighbours narrows the novelty but does not remove it. The matched-volume control itself is prior art; temporal decomposition generally is prior art; the legal citation task is prior art. The surviving contribution is the **measured effect** of targeted recurring-text removal versus same-volume removal and the **specific age-versus-shrinkage decomposition** on this legal retrieval corpus.

**Controller verdict: `AI_AND_LAW_READY_AFTER_FORMATTING`. No new experiment is required before submission.**
