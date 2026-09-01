# Venue shortlist — paper B

For `MANUSCRIPT.md` in this directory. Assessed on fit with what the paper
actually contains. **Nothing submitted, nobody contacted.** Every detail below
needs confirming on the venue's current site before any submission.

`../paper/VENUES.md` covers paper A and is unchanged; the two papers do not
compete for the same venue.

## PRIMARY

**1 · Artificial Intelligence and Law** — Springer. **PRIMARY / controller-confirmed 2026-09-01.** The live scope explicitly includes conceptual retrieval of cases and statutes, evaluation and auditing techniques for legal AI systems, and systemic problems in constructing/delivering legal AI. The paper now fits those clauses directly through a controlled legal-retrieval experiment rather than through an implications section. Recent 2026 journal articles on legal citation prediction, legal QA/RAG and legal-LLM robustness confirm that empirical legal-AI evaluation remains inside the journal's active editorial footprint. `SCOPE.md` records the clause-by-clause map and prior-art narrowing. A second submission after a scope desk rejection is justified only because this is a genuinely different technical/empirical paper on page one; do not mention or defend the rejected paper unless the submission system asks.

**2 · JURIX (International Conference on Legal Knowledge and Information
Systems)** — strongest specialist fallback. The completed prior-art audit
narrows the methodological claims but leaves the controlled empirical result
intact. Use JURIX if AI & Law rejects on fit or editorial significance; do not
create a conference-specific experiment before that event.

**3 · ICAIL** — the field's main conference, biennial. Highest-visibility
option for this material. Check the cycle: if the next call is far away, this
is a plan rather than a venue.

## SECONDARY

**4 · Journal of Artificial Intelligence Research / ACM TOIS** — only if the
paper is reframed as a retrieval-maintenance and corpus-hygiene paper with the
legal setting as the domain. That reframing loses §8, which is the part that
makes it an AI-and-law paper. Listed for completeness, not recommended.

**5 · Natural Legal Language Processing (NLLP) workshop** — the venue the AI
and Law editor pointed to for paper A. For *this* paper it is a genuine fit
rather than a demotion: the audience builds the pipelines that §4 and §5 are
about. Shorter format; the §7 non-stationarity material would have to go.

**6 · Artificial Intelligence and Law special issues** — worth watching for a
call on legal data, benchmarks or evaluation, where §5 is directly on topic.

## FALLBACK

**7 · Preprint (arXiv cs.CL or cs.IR)** with a stated intention to submit. The
§5 control is usable by others the day it is posted and does not depend on
peer review to be correct. The repository is public, so the reproduction path
in §10 is live.

## Selection criteria applied

- **technical/empirical contribution required** — 1, 2, 3, 5 all satisfied by
  §4–§7
- **tolerates a negative result as the headline** — 2 and 5 most comfortably;
  1 needs §5 framed as a control contributed, not only a null found
- **accepts a single-jurisdiction non-Western corpus** — 1, 2, 3, 5 in
  practice; the paper argues the setting is instrumentally useful rather than
  incidental (§3)
- **independent-researcher eligibility** — all; conference registration is the
  real cost for 2 and 3
- **length** — the draft is ~4,700 words plus tables: comfortable for 1 and 4,
  needs cutting for 2, 3 and 5

## Ranking after the full-text novelty audit

P2 and P6 were read in full, along with the closest boilerplate-retrieval and
legal temporal-decomposition neighbours. They **do** narrow the paper: the
quantity-confound principle and controlled temporal decomposition are prior
art. They do **not** eliminate the paper's two controlled empirical results.
Because the live AI & Law scope names legal retrieval, evaluation/auditing and
systemic construction problems explicitly, the primary ranking remains AI &
Law rather than moving to JURIX.

A reviewer asking for a dense retriever is a revision request, not a
pre-submission rescue requirement: the retrieval layer supports one without a
new corpus pass, and the paper's independent variable does not change.
