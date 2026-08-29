# Submission kit — *Journal of Empirical Legal Studies* (Wiley / Cornell Law School)

Requirements below were read from the journal's own author guidelines on
28 August 2026, not from memory. Where the journal states no requirement, this
file says so rather than inventing one.

| | |
|---|---|
| Journal | *Journal of Empirical Legal Studies* (JELS) |
| Publisher | Wiley, in association with Cornell Law School |
| Submission portal | <https://authors.wiley.com/journal/JELS> |
| Review model | **Double anonymous** |
| Submission fee | **None** |
| APC | Only on the open access track. **Submitting to the subscription track**, so none. |
| Word limit | None stated. This manuscript: ~5,900 words. |
| Abstract | Structured or unstructured, no stated limit. Ours is unstructured, ~265 words. |
| Keywords | Up to seven. Ours: six. |
| References | **No formatting requirement at submission.** Consistent style, with author, title, year, volume, pages. Wiley restyles on acceptance. |
| LaTeX | Both the `.tex` source and a PDF. |
| Figures | Highest resolution possible. **This article has none** — three tables only. |
| Free Format | Yes. *"Free Format submission means you can format your manuscript and references in the style or format you prefer."* Wiley restyles on acceptance. |
| Simultaneous submission | **Permitted.** *"Simultaneous submission of papers to JELS and other journals is permitted."* See the note below — this is unusual and it changes what else this manuscript can do while it waits. |
| Editorial queries | `jels@cornell.edu` |
| Portal technical help | `submissionhelp@wiley.com` |

*(The four rows above were read from the journal's author guidelines page on
29 August 2026, on the second pass, and are quoted rather than paraphrased.)*

## The rule that most journals do not have

JELS states in terms: **simultaneous submission is permitted.** Almost no
peer-reviewed journal allows this, and it is the reason the two publication
regimes — peer-reviewed exclusivity and US law-review simultaneity — do not
normally mix. Here they do, for this one manuscript, subject to three
conditions the journal also states:

1. If JELS accepts first, the article is published in JELS.
2. An expedited review may be requested, naming the other journal and its
   deadline.
3. If an offer elsewhere is accepted, JELS must be notified **immediately**.

So this article may sit at JELS and at US law reviews at the same time. That
is a decision to take deliberately, not a thing to drift into: it is worth
doing only if the law-review list is real and ready. Nothing in this kit
assumes it.

## What to upload

Built by `python3 build.py`, which refuses to finish if any file is wrong.
All three are in `submission/`, which is git-ignored because the identified
copies carry a postal address and a telephone number.

| File | What it is |
|---|---|
| `submission/main_anonymous.pdf` | **The anonymised manuscript.** No name, no correspondence block, no ORCID, no repository URL. |
| `submission/main.pdf` | The full identified version the journal also asks for. |
| `submission/main.tex` + `submission/numbers.tex` | The LaTeX source, as the journal requires alongside the PDF. |
| `submission/cover_letter.pdf` | Editors only. Identified. |

## The one thing that is easy to get wrong

The repository URL names the author. It sits in a footnote to *Availability of
data and code*, which is the last place anyone thinks to check when
anonymising, and a double-anonymous submission that leaks it there has
identified itself in a section about openness.

`main.tex` therefore gates that footnote on `\ifanon`: the anonymised build
says the repository is withheld and will be cited in full in the accepted
version. `build.py` then reads the built PDF back and exits non-zero if any of
nine identifying strings — the name, the ORCID, `github.com`, `zenodo`, the
GitHub handle, and the private contact values — survives into it. The check
reads the artefact, not the source, because the artefact is the file that gets
uploaded.

## Why this journal

JELS publishes quantitative descriptive work on legal systems and states an
interest in jurisdictions beyond the United States. The article's question —
how much of an enacted statute book courts actually apply — is empirical legal
studies in the narrow sense, and its data advantage is that Saudi Arabia
codified much of its private and commercial law within a decade while
publishing commercial judgments in full text, so both sides of the comparison
exist at article level for one jurisdiction.

## Submitted

**Submitted to the *Journal of Empirical Legal Studies* on 29 August 2026.
Manuscript ID `4582420`. Status: `In Screening`.** Three files went up -- the
anonymised LaTeX archive, the PDF that archive builds, and the identified
title page -- and the reviewer PDF the portal compiled was read page by page
before it was approved: 18 pages (two of the system's own, then the 16 of the
manuscript), tables intact, and the data-availability footnote correctly
reading *"Repository withheld for anonymous review."* The `\ifanon` gate held
in the publisher's own compilation, not only in ours.

## Previous submission

Submitted to the *Journal of Legal Analysis* on 27 August 2026
(`LEGAL-2026-209`) and desk-rejected on 28 August 2026, same day, on scope:
*"not a good fit."* No reviewer saw it. The manuscript was retargeted rather
than revised — the JLA-specific layout (1.25-inch margins, endnotes gathered
after the references, a 100-word abstract cap) was undone, and the abstract
expanded to the length the argument actually needs.


---

# Portal walkthrough

Every field below is filled from the built manuscript, not from memory. The
abstract is copied out of the compiled PDF so that its figures are the
generated ones. Paste, do not retype.

## 1 · Manuscript type and title

| Field | Paste |
|---|---|
| Article type | Original Article |
| Title | `99 Per Cent of the Procedure, 27 Per Cent of the Code: The Enacted Law and the Applied Law in 50,666 Judgments` |
| Short/running title | `The Enacted Law and the Applied Law` |

## 2 · Abstract

Unstructured, 265 words. Paste as plain text — the portal box strips
formatting, and there is no markup in it to lose.

```
A legislature enacts a statute book; courts apply some part of it. How large that part is has rarely been measured, because it requires matching what judgments cite to the articles that exist, at the level of the article. This article does so for one jurisdiction. 121,207 statutory citations are extracted from 50,666 Saudi judgments published in full text and matched to 15,855 articles across 290 instruments, giving the first article-level measurement of applied against enacted law for an Arabic-language legal system.

The applied law is a small and lopsided subset of the enacted one. 11.7 per cent of the statute book is ever cited — 30.5 per cent of the articles within the courts' own statutory jurisdiction — and 89.2 per cent of what is applied is procedural rather than substantive. The contrast is sharpest between two instruments that need no denominator: the law telling the commercial courts how to proceed has 99.0 per cent of its articles cited; the code telling them what the parties owe each other has 27.5 per cent.

Two results bear on why. Segmenting each judgment by its own headings, and attributing every citation to the court or to a party, locates the narrowing at the bench rather than the bar: the court's own reasons are more procedural than the arguments put to it, and substantive instruments are raised and answered with procedure. And amendment predicts neither citation nor its absence, so the unused portion of the book is not merely its neglected or superseded portion. Every measurement is generated by deposited code from a deposited corpus.
```

## 3 · Keywords — six of the seven allowed

```
empirical legal studies
legislation
judicial citation
legal informatics
open government data
Saudi Arabia
```

JEL codes, if the portal asks: `K40, K41, K10, C81`.

## 4 · Files — the portal's own slots

Read off the upload screens on 29 August 2026, in two passes: the second
screen splits the LaTeX route into two required slots, and it wants the PDF
as well as the source.

| Slot | Portal says | Upload |
|---|---|---|
| **Main Document – LaTeX File** | Required · `.tex`, `.zip`, `.tar.gz` · *"should not contain Identifying information (authors' names, affiliations, and funding sources)"* | `submission/jels_main_manuscript.zip` |
| **Anonymized Main Document – LaTeX PDF** | Required · `.pdf` · *"A LaTeX PDF is required if you provide a .tex Main Document"* · same anonymity rule | `submission/jels_main_manuscript.pdf` |
| **Title Page** | Required · MS Word · maximum 1 · *"The Title Page will not be sent to peer reviewers"* | `submission/title_page.docx` — **identified**, with every declaration |
| **Figure** | Optional · image files | **Nothing.** Three tables, no figures. |
| Cover letter | its own step, not a file slot | `submission/cover_letter.pdf` |

The PDF in the second slot is not `main_anonymous.pdf`. It is the PDF that
the uploaded archive itself builds: `build.py` extracts the zip into an empty
directory, compiles it there, and keeps *that* output. A source and a PDF
uploaded side by side are a pair the editor will assume correspond; the only
way they cannot disagree is if one produced the other.

`build.py` checks each artefact against the rule that applies to it — the
archive and its PDF are refused unless they carry none of the nine
identifying strings and run to 16 pages; the title page is refused unless it
*does* carry all six of the author's details.

Do not upload `main.pdf` or the loose `.tex` files. They stay in
`submission/` as the author's record.

## 5 · Declarations

| Screen | Answer |
|---|---|
| Conflict of interest | **None.** Paste: `The author declares no conflicts of interest.` |
| Funding | **None.** Paste: `This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.` |
| Ethics / IRB | **Not applicable.** The data are court judgments published in full text by the Ministry of Justice with party names masked at source, and legislation published in the Official Gazette. No human subjects, no informed consent, no IRB. Say this rather than leaving the box empty. |
| Author contributions | `Sole author.` |
| Permission to reproduce | **No** — no third-party material; the three tables are generated by the author's own code. |
| Data availability | See below. |
| Previous submission | If asked whether the manuscript has been submitted elsewhere: **yes**, to the *Journal of Legal Analysis*, desk-rejected on scope on 28 August 2026 without review. Say so. It costs nothing and a discovered omission costs everything. |

## 6 · Data availability statement

Wiley asks you to pick a statement from its list. The one that fits is
*"data available in a public repository"*. Paste:

```
The legislative corpus, the judgment corpus, the extraction and matching code, the segmentation and voice-attribution code, and the scripts that generate every number reported in this article are openly available at https://github.com/Abdullah-m7/saudi-legal-corpus-ai under the MIT licence, and archived on Zenodo. The underlying legislation and judgments are official Saudi government publications; the binding Arabic original governs in all cases.
```

**Note for the anonymised file only:** that URL names the author. It belongs
in the portal's data availability box (editors see it) and in the identified
PDF, and it is gated out of `main_anonymous.pdf` by `\ifanon`. Do not paste it
into any field the reviewers read.

## 7 · AI use

The manuscript carries a *Use of AI tools* section of its own. If the portal
also asks, paste:

```
The analysis code deposited with this article, and drafts of the manuscript, were produced with the assistance of a large language model (Anthropic's Claude) working under the author's direction. No measurement in the article is produced by a language model: every number is computed by the deposited code from the deposited data, and the manuscript is typeset from a generated file of macros. The author designed the study, verified each result against the corpus, and is responsible for the content.
```

## 8 · Suggested reviewers

The journal states no policy and the portal may not ask. If it does, and the
field is optional, **leave it empty**: a suggestion list assembled from
memory is how a wrong name reaches an editor. If it is mandatory, tell me and
I will build one from the works actually cited in the bibliography, with each
name checked against a live source.

## 9 · Before you press Submit

1. Open `main_anonymous.pdf` and read pages 1 and the last two. The last two
   are where the identity leaks live: the data-availability footnote and the
   declarations block. Both are gated; confirm by eye anyway.
2. Confirm the PDF's own document properties carry no author name. They are
   blank in the current build.
3. Check the portal's compiled proof, if it makes one, before approving.
4. Submit from a computer, not a phone.
