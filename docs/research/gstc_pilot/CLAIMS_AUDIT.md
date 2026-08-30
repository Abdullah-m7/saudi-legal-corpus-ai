# The project's own claims, re-run against the gold

The published measurements count every citation the pattern finds, anywhere in
a judgment. `applied_law_v2.py` runs `CITE.findall(r["text"])` over the whole
text; there is no segment filter on the headline counts. The gold sets say who
was speaking. This is what the difference does.

All figures from `claims_audit.py`, over 480 hand-labelled occurrences — both
development sets and both held-out sets, 457 of them citations.

## Who is speaking

| | ministry judgments | committee digests |
|---|---|---|
| the court's / tribunal's own reasoning | 183 (80.6%) [75.0, 85.2] | 71 (30.9%) [25.3, 37.1] |
| a party's submission | 37 (16.3%) | 64 (27.8%) |
| the reporter's authorities block | — | 68 (29.6%) |
| the disposition's boilerplate | 2 (0.9%) | 13 (5.7%) |
| inside a quoted provision | 5 (2.2%) | 6 (2.6%) |
| summary / narrative | — | 8 (3.5%) |

An unfiltered count therefore over-states the court's own citations by a
factor of **1.24** on ministry judgments and **3.24** on the committees'
digests.

## What that does to the claim that the applied law is procedural

This is the claim the appeal paper joins to: *"Measuring what Saudi courts
cite shows an applied law that is overwhelmingly procedural."*

| ministry judgments | procedural share |
|---|---|
| all citations, as published | 193/227 = **85.0%** [79.8, 89.1] |
| the court's own reasoning only | 166/183 = **90.7%** [85.6, 94.1] |

**The filter strengthens the claim.** Restricting to what the court itself
cites raises the procedural share by about six points, and the reason is
visible in the labels: party submissions are only 54 per cent procedural
(20 of 37), because parties argue the merits while courts rule on service,
appearance, capacity and the admissibility of evidence. The unfiltered figure
is diluted by exactly the material the filter removes.

So the published sentence survives, and the correction runs in its favour.
That is worth stating plainly, because the reason for doing the check was that
it might not have.

Two qualifications on the strengthened figure. It is a sample of 183 citations
from 400 judgments, not a census, so it carries an interval and the published
census figure does not become 90.7 per cent by this measurement — what becomes
available is a bound on the direction and size of the bias. And the same
correction has not been applied to the article-level counts, which are the
unit the HILJ paper argues for; the segment distribution may differ by article
as well as by instrument.

## The HILJ paper's own requirement

The HILJ paper lists, among the conditions a jurisdiction must meet before
displacement can be measured, that

> *where* in a judgment a citation falls --- in the recital of the parties'
> arguments or in the court's own reasons --- can be read.

It states the requirement and the corpus meets it; the headline counts do not
yet use it. Nothing published is wrong on this point, and one thing published
is now measured rather than assumed.

## What this says about the other source

The committees' digests cannot be read the same way at all. Only 30.9 per cent
of what a detector finds there is the tribunal's own, because the reporter
adds an authorities block to every decision and every decision closes with
boilerplate citing the rule that makes it final. And their procedural share is
6.6 per cent on all citations against 85.0 for ministry judgments, falling to
1.4 per cent on reasoning alone: these are tax and customs tribunals citing
the tax and customs codes, and their applied law is substantive by
construction.

**No sentence beginning "Saudi courts cite" can be supported by both sources
at once.** Any such claim has to name the body, and the papers that name the
ministry's judgments are claims about the ministry's judgments.

## What is not audited here

The gold is one reader's, with no second annotator and so no agreement
statistic. The procedural set is the applied-law measurement's own list,
matched here by instrument name rather than by registry key. And the audit
covers instrument-level composition only; the article-level counts that carry
the HILJ paper's central argument are not re-run, because doing that needs
article-level gold across the whole corpus rather than 480 sampled
occurrences.
