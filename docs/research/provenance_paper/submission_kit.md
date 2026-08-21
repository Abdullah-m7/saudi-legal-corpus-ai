# Paper 5 — submission kit for *Data & Policy* (Cambridge University Press)

Everything the submission form asks for, in the order the form asks for it.
Copy from here rather than retyping; the plain-text files beside this one are
already stripped of LaTeX.

**Submission site:** <https://mc.manuscriptcentral.com/dataandpolicy>

ScholarOne, the same platform as paper 3 (*Statute Law Review*) — but a
**separate account**. A Cambridge Core reading account is not a submission
account. Register at the link above if the login does not recognise you.

Cambridge Core was reporting a service disruption while this kit was written,
so two things below could not be re-confirmed from the publisher's own pages
and are marked **[confirm on the form]**.

---

## 1. Article type

**Research Article.** The journal's own description — "use rigorous methods
that investigate how data science can inform or impact policy", target
**~8,000 words**. The manuscript is **7,571 words including footnotes**.

## 2. Title

Paste as a **single line**. ScholarOne pre-fills the title field from the
uploaded file, and on paper 3 it duplicated a two-line title into 22 words.

```
Can You Build on the Official Record? Availability, Consistency and Provenance in a State's Published Law
```

## 3. Abstract

`abstract_plain.txt` — **249 words**.

The form caps the abstract at **250 words**, a limit that appears nowhere in
the journal's written instructions and only on the field itself. The manuscript
carried 307 and was cut to fit; no number and no conclusion was dropped, only
wording. `build.py` now generates this file from the manuscript, so the two can
no longer disagree — which they briefly did.

## 4. Policy Significance Statement

`policy_significance_plain.txt` — **128 words**.

Every research article the journal publishes carries one, and it is displayed
above the abstract on the article page. If the submission form has no field for
it, it still belongs in the manuscript, where it already is — directly under
the abstract.

## 5. Keywords

**The form takes at most five**, added one at a time. Use these:

```
provenance
data quality
public data infrastructure
open government data
web archiving
```

The manuscript lists eight; its order is not an order of priority, so the five
are chosen rather than taken off the top. *Saudi Arabia* is dropped because the
abstract carries it and Cambridge Core indexes abstracts. *Legal informatics*
is dropped deliberately: the article was reframed to reach past law, and the
term would signal a legal-informatics paper in a data-policy journal and pull
reviewers from the wrong field. *Official records* gives way to *open
government data*, a research community with its own literature — which is where
this article's readers are.

## 5b. Standard Focus Area

**Area 3: Policy & Literacy for Data.**

The form requires one and tells the author to read the descriptions. Area 3's
own description names *data supply chains, ownership, provenance, sharing,
linkage, and data curation*, and *high-quality metadata, which must adhere to
common standards to ensure interoperability*. That is this article's subject
and its proposal.

Area 1, *Digital & Data-Driven Transformations in Governance*, is the plausible
alternative and is wrong: its description is about decision-making — public
participation, collective intelligence, government-citizen interaction,
democratic deliberation. This article does not study how decisions are made. It
measures the quality of the record decisions are made on. The field routes the
manuscript to reviewers, so the distinction is not cosmetic.

## 6. Files to upload

| # | File | Designation |
|---|---|---|
| 1 | `submission_manuscript_with_author_details.docx` | Main Document |
| 2 | `fig1_access.tiff` | Figure 1 |
| 3 | `fig2_tiers.tiff` | Figure 2 |

Review is **single-blind**, so the anonymous manuscript is *not* uploaded.
`submission_manuscript_anonymous.docx` exists because the build produces both;
leave it on disk. If the form asks for an anonymised file anyway, that is the
file, and it has passed the two-way anonymity audit.

Upload TIFF, not EPS. Both are generated; TIFF is the format Cambridge's
artwork guide names first, and it is what paper 4 uploaded without incident.
The `.png` versions are for the PDF build only.

**Check the designations in the preview screen before sending.** Two figure
files with similar names in the wrong slots is the one failure this step has.

## 7. Alt text for figures

Cambridge asks for WCAG 2.1 AA alt text for every figure. Both descriptions are
already in the manuscript under **Figure alt text**, immediately before the
declarations. If the form has per-figure alt-text boxes, paste from there — the
text is written to stand alone.

## 8. ORCID

**Required for the corresponding author**, not optional. Link the account
rather than typing the number:

```
0009-0001-0832-0995
```

## 9. Affiliation

```
Independent Researcher
```

Spell-check it in the ScholarOne profile before submitting. The paper 3 account
carries `Independent Reseacher` — a typo that reached the record and now has to
wait for proof stage.

## 10. Declarations the form will ask about

All are already written into the manuscript's **Declarations** section. Answer
the form's questions consistently with it:

| Form question | Answer |
|---|---|
| Funding / financial support | **None.** No specific grant from any funding agency, commercial or not-for-profit sector. |
| Competing interests | **The author declares none.** |
| Ethics approval | **Not applicable** — no human participants, no animal subjects, no personal data. |
| Human participants | **No.** |
| Generative AI use | **Yes** — declared in full: tool with version, how it was used, why. The manuscript names Claude Opus 5 (Anthropic). |
| Author contributions (CRediT) | Conceptualisation, data curation, methodology, software, formal analysis, investigation, writing — original draft, writing — review and editing. Sole author. |
| Data availability | Open: GitHub repository plus Zenodo archive, MIT licence, DOI `10.5281/zenodo.22019183` (concept DOI `10.5281/zenodo.22019182`). |
| Preprint | **No.** No arXiv e-print number. |
| Conference / special track / special collection | **N/A** to all three. |
| Suggested reviewers | Leave blank unless the field is mandatory. |

The journal follows the **TOP (Transparency and Openness Promotion)** policy,
which is why the data availability answer matters more here than at the other
venues: the data and the code that produces every number are already public,
which is the strongest form of that answer.

## 11. Article processing charge — request the waiver

**This is the step that is easy to miss and expensive to miss.**

*Data & Policy* is fully open access, so acceptance triggers an APC. There is
**no funder** for this work. Cambridge offers waivers to authors without
research funding, and the request is made **at submission**, not after
acceptance.

- If the form offers a waiver or "no funding available" option, **select it**.
- If it asks for the funder, state that there is none — do not leave it blank
  and do not name the institution.
- If no waiver option appears anywhere in the flow, **email the editorial
  office before the manuscript goes to review** and ask how to apply. Do not
  wait for an acceptance letter to raise it.

**[confirm on the form]** The exact APC figure and the wording of the waiver
route could not be re-read from Cambridge's fees page — it was returning 404
during a stated service disruption. The waiver's existence was verified
earlier; the mechanics have to be taken from the form itself.

## 12. Cover letter

**[confirm on the form]** ScholarOne usually offers a cover-letter box. If it
does, the substance to give it:

- What the article measures and on what: the availability and internal
  consistency of one state's official legal record, measured from the
  contemporaneous build record of a 15,689-article corpus.
- Why it is for this journal: it is about the quality of public data
  infrastructure that policy and technology now consume directly, and it ends
  in a concrete proposal — a five-field provenance schema a publisher can adopt.
- What is unusual about it: the evidence is a by-product of construction rather
  than a survey, so it records what retrieval actually returned at the time,
  which a retrospective study cannot recover.
- That the data and every line of analysis are already public.
- That there is no funder and a waiver is being requested.

Do not restate the abstract.

---

## Before pressing submit

- [ ] Title is one line, not duplicated
- [ ] Abstract pasted whole, 307 words, no LaTeX residue
- [ ] Policy Significance Statement pasted or confirmed present in the file
- [ ] Three files uploaded, designations checked in the preview
- [ ] ORCID linked
- [ ] Affiliation spelled correctly
- [ ] **APC waiver requested**
- [ ] PDF proof generated by the system opened and read to the last page

Record the manuscript ID in `README.md` when the confirmation screen shows it,
as papers 3 and 4 did.
