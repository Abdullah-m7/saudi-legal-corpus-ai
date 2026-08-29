# When the two preprint DOIs arrive

On 29 August 2026 both Springer submissions were pushed through the
*In Review* «Post My Preprint» button on Research Square:

| Paper | Manuscript | Journal under review | Preprint state |
|---|---|---|---|
| 1 | *The Saudi Legal Corpus for AI* | *Language Resources and Evaluation* | submitted to prescreen |
| 2 | *Vertical Elaboration or Horizontal Integration?* | *Artificial Intelligence and Law* | submitted to prescreen |

Research Square screens for submission readiness (author information,
declarations, suitability), converts the files to HTML, then posts with a
DOI under the `10.21203/rs.3.rs-…` prefix. Journal information appears on
the preprint page later, once the manuscript clears the journal's own
initial editorial checks — that is expected, not a fault.

Nothing below should be edited until the DOIs are real and resolve. A DOI
typed from memory is the failure mode this repository exists to prevent.

## Every place the DOI lands

| File | What changes |
|---|---|
| `../../CITATION.cff` | add `preferred-citation` / `identifiers` for the corpus preprint |
| `cv/cv.tex` | move the two entries out of «Manuscripts under review» into a «Preprints» section, each with its DOI |
| `network_paper/references.bib:140,150` | replace `Manuscript under review` with the corpus preprint DOI |
| `definitions_paper/references.bib:140,150` | same two entries |
| `network_paper/cover_letter.tex:76` | «under review at another journal» → «posted as a preprint at DOI …, under review at …» |
| `definitions_paper/cover_letter.tex:62` | same |
| `appeal_paper/` cover letter and references | corpus citation, Chicago author-date form |
| `hilj_paper/main.tex` | corpus footnote, Bluebook form |
| `amendment_paper/main.tex:614` | «under review elsewhere» → name the two that are now public |
| `corpus_paper/README.md`, `network_paper/README.md` | status line |
| `decision_map.md` | the closing note about where the underlying data can be read |

## What does **not** change

The measurements. The preprints freeze version 1 of each manuscript as it
was submitted to Springer; later versions are posted as new versions of the
same DOI. Any figure that changes in this repository after this date belongs
to a version 2, not to a silent edit.
