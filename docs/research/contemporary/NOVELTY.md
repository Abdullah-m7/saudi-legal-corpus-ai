# Novelty assessment

Deeper than the first scoping pass: nine targeted searches across five
literatures, including the two the earlier check declared it had not reached
(German *Rechtssoziologie*, Arabic empirical legal scholarship). Still not a
systematic review — no law-library database was queried — and anything
load-bearing should be re-checked before submission.

**The deeper search changed the framing, and the framing is now weaker and
more defensible.** Role segmentation is *not* novel: the legal-NLP literature
has built it, with public datasets whose label sets explicitly separate
"Arguments of Petitioner" and "Arguments of Respondent" from "Reasoning". The
first draft's implicit claim to have introduced speaker separation is dropped.
What survives is narrower: that segmentation which exists for summarisation
and retrieval turns out to be a *measurement-validity prerequisite*, and the
size of the error has not been measured.

## Novelty matrix

| prior work | data | speaker distinction? | authority-**type** distinction? | within-document comparison? | our difference | status |
|---|---|---|---|---|---|---|
| Indiana appellate citation practice (1994–2003) | appellate opinions | no — counts citations *to* briefs as a source category | yes (cases, statutes, briefs, secondary) | no | we compare the **composition** of what each voice invokes, in the same document | **STRONG** |
| *Precedent as Rational Persuasion* (Larson) | briefs and opinions | yes, as separate documents | precedent only | no — separate corpora | authority type beyond precedent; same document | **STRONG** |
| *Does Lawyering Matter?* (Tex. L. Rev.) | briefs | brief only | precedent citation features | no | outcome prediction, not measurement validity | **STRONG** |
| Bias in Judicial Citations (Choi & Gulati, *J. Legal Stud.*) | opinions | identity of the **cited** judge | no | no | identity of the **citer**, and type not identity | **STRONG** |
| LegalSeg; Indian rhetorical-role datasets; SAILER / CaseEncoder segment schemes | judgments | **yes — explicitly** | no | not for citations | the segmentation is used as a validity requirement and the bias is quantified | **PARTIAL** — tooling is theirs, the measurement claim is ours |
| Ukrainian 100M-decision citation graph; Czech apex-court citation data | judgments | no | statutes vs constitution | no | concentration measured in the **bench's voice only**; core-entry latency | **PARTIAL** — concentration is known |
| German *Rechtssoziologie*: *Tatbestand* / *Entscheidungsgründe* | doctrine, procedure | **yes, doctrinally** | no | no | the distinction is formalised in German procedure but its survey literature reports few empirical studies of judicial decision behaviour; none quantifying authority mix by voice | **STRONG** |
| Arabic scholarship on تسبيب الأحكام | Saudi judgments | no | no | no | doctrinal and analytical, not quantitative | **STRONG** |
| Qualitative Islamic-law scholarship (qawāʿid; Ḥanbalī deference) | doctrine | no | yes, conceptually | no | 28,090 judgments, typed, court-voice only | **STRONG** for the quantification |

## Classification

- **STRONG** — the court/litigant authority-**composition** contrast within one
  document; the article-level non-overlap (79.7 % of paired judgments share no
  article); the within-dispute transition structure; quantified statute+fiqh
  hybridity; Saudi judicial reasoning measured computationally at all.
- **PARTIAL** — the measurement-validity framing (the tooling exists and is
  ours only in its application); citation concentration (the phenomenon is
  known; core-entry latency is not).
- **NOT NOVEL** — role segmentation as a task; the observation that briefs
  reach opinions; the general claim that citation counts can mislead.

## What would still overturn this

A law-library search of *Journal of Empirical Legal Studies*, *Journal of Law
and Courts* and the *International Journal for Court Administration* under
terms we did not use; and any German dissertation comparing
Parteivortrag and Entscheidungsgründe quantitatively. Neither was reachable
here. If such work exists, the framing moves from "first measurement" to
"replication in a new legal family", which is still worth publishing and
should be said plainly.

## Title

The first draft's title asserted the finding. The manuscript now leads with
the methodological consequence:

> **One Judgment, Two Legal Languages: Why Citation Measurement Needs Speaker
> Attribution**

## Decision

**WRITE — one paper.** Draft complete at `paper/MANUSCRIPT.md`, 104 of 104
figures traced to generated results by `paper/check_paper.py`.
