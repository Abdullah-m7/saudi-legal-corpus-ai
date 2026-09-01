# Venue shortlist — paper B

For `MANUSCRIPT.md` in this directory. Assessed on fit with what the paper
actually contains. **Nothing submitted, nobody contacted.** Every detail below
needs confirming on the venue's current site before any submission.

`../paper/VENUES.md` covers paper A and is unchanged; the two papers do not
compete for the same venue.

## PRIMARY

**1 · Artificial Intelligence and Law** — Springer. The target this draft was
written for, and the case is now empirical rather than rhetorical: the paper
runs a legal retrieval experiment and reports a controlled result on it, with
the enacted-provisions material demoted to context that does not carry fit.
The clause-by-clause map is in `SCOPE.md`. *Caveat: a second submission from
the same author after a desk rejection needs the new paper to be visibly a
different paper on its first page. The title, abstract and §1 are now about an
experiment, which is the strongest form of that signal. Note also that the
task's closest ancestor (Huang et al., 2021) is co-authored by the editor who
rejected paper A — a reason to position against it accurately and carefully,
and no reason to do anything else.*

**2 · JURIX (International Conference on Legal Knowledge and Information
Systems)** — peer-reviewed proceedings, IOS Press. §6's result and the
requirement it supports are exactly the kind of finding this community can act
on, and the length limit forces the paper to lead with the experiment. Faster
than a journal cycle. **This is the strongest fallback and, if the reference
audit in `REFERENCES_TODO.md` §B weakens §7, it becomes the first choice.**

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

## What would change the ranking

Two findings in the pending full-text reading would move this list:

- If **P2** (*(Near) Duplicate Subwords*) already reports a matched-volume
  comparison, §6's framing narrows to the legal-domain demonstration, and 2
  rises above 1.
- If **P6** (CLEF LongEval) already decomposes ageing into age and index size,
  §7 loses its methodological claim and becomes a replication in a legal
  corpus, which is still publishable but not at 1.

A reviewer asking for a dense retriever is a revision request, not a
rejection: the retrieval layer supports one without a new corpus pass, and the
paper's independent variable does not change.
