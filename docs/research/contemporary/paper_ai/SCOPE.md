# Scope map — *Artificial Intelligence and Law*

Written for the author, not for an editor. **Nothing here is a cover letter,
and no journal has been contacted.** It exists so that the decision to submit,
or not to submit, is made against the journal's own words rather than against
hope.

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
implication section rather than the subject. `../paper/VENUES.md` already
ranked JELS first for it, which was the correct reading.

That paper is not withdrawn and is not weakened by this one. It is a different
paper for a different venue.

## What this paper offers against each clause

| Scope clause | This manuscript | Honest strength |
|---|---|---|
| formal or computational models of legal knowledge and reasoning | Not claimed. No model of legal reasoning is proposed. | **Not the route in.** Do not argue this clause. |
| in-depth study of an AI system used in the legal domain, focused on the technical implementation | Partly: §6 compares five retrieval-index architectures under temporal drift, and §6.2 tests a maintenance policy against a negative control. These are the technical implementation of a legal AI system, measured. | **Moderate.** The systems are built and measured here rather than deployed elsewhere. |
| original research contribution of a technical or empirical nature | §4 defines a redundancy unit and quantifies its effect on support and ranking; §5 is a controlled negative result about a standard pipeline step, with a reusable control; §7 is a permutation-calibrated non-stationarity test that measures its own false-alarm rate. | **Strongest.** This is the paper's actual claim to the venue. |
| legal / ethical / social implications with a demonstrable link to that contribution | §8: four enacted provisions permit AI inside the procedure of the forum whose corpus we measure, quoted verbatim, while AI is materially at issue in 0 of 50666 judgments. | **The link is the point.** The implications section is short and attached to measured quantities, not the other way round. |

## The sentence the paper has to survive

*Would a reviewer say this is a corpus-statistics paper with a legal veneer?*

The defensible answer is that every result is about what a legal AI system
inherits from a legal corpus — inflated support, an unvalidated cleaning step,
an index that ages faster in ranking than in recall, a train/test split that
straddles a publication-process break — and that all four are measured, not
asserted. §5 in particular is a methodological result that applies to any
corpus, delivered with the experiment that shows why the usual justification
fails.

The weak point to expect: **one jurisdiction, one forum, and a §5 downstream
verdict resting on 6–7 matched pairs.** That thinness is stated in the
abstract's own terms in §9 rather than buried, and the §5 claim is scoped to
"at this corpus size". A reviewer who reads §9 will not be surprised by
anything; a reviewer who objects to it will be objecting to something the
paper already concedes.

## Before any submission

1. Fill `REFERENCES_TODO.md`. Section B in particular: two of the paper's
   three novelty claims can be overturned by a literature search, and it is
   better to overturn them here.
2. Decide the §5 framing — *proposing* the size-matched control, or *importing*
   it from another field. This depends entirely on B2 and cannot be decided
   before the search.
3. Check the journal's current format, length and blinding requirements on its
   own site.
4. Consider whether the Springer transfer offer from the first submission is
   relevant. It is not: this is a different manuscript, and offering it as a
   transfer of the rejected one would misdescribe it.
5. `python3 check_paper2.py` must pass, and the results files it reads must be
   fresh (`python3 ../check_fresh.py`).

**No journal is to be contacted and nothing is to be submitted without the
author.**
