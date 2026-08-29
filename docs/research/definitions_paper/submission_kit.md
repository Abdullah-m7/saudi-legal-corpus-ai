# Submission kit — *The Loophole* (Commonwealth Association of Legislative Counsel)

Read from CALC's own home page on 29 August 2026, not from memory.

| | |
|---|---|
| Journal | *The Loophole*, journal of the Commonwealth Association of Legislative Counsel |
| Scope | «drafting, legal, procedural and management issues relating to the preparation and enactment of legislation» |
| Who may submit | «CALC members **and others** interested in legislative topics are also encouraged to submit» — no membership required |
| Length | **No more than 8,000 words including footnotes.** Ours: 7,993 |
| Abstract | **No more than 200 words.** Ours: 198 |
| Format | MS Word or compatible, in the style of the template on the CALC home page |
| Where | **Aleksander Hynnä, Editor in Chief** — `loophole.calc@gmail.com` |
| Fee | None stated |
| Schedule | Issues appear through the year; the current one is July 2026 |

## House style, taken from the journal's own file

CALC publishes each issue as a `.docx` as well as a PDF, so the July 2026
issue is the style specimen. Inspecting it:

| | |
|---|---|
| Page | US Letter, 1-inch margins all round |
| Body | Times New Roman 12 pt (`Normal`) |
| Headings | Arial 11 pt (`heading 3`–`heading 5`); a 16 pt Arial `Heading` |
| Footnotes | 10 pt (`footnote text`) |
| Named styles | `Abstract`, `Abstract heading`, `Body`, `Centred line` |

Our `.docx` is produced by pandoc through `build.py`. Matching those styles
exactly is an **open item**: the issue file can be passed to pandoc as a
reference document, which would carry the page setup and the heading and
footnote styles across. It has not been done yet, and it should be checked for
leaked headers and footers if it is.

## What to send

`python3 build.py` produces everything; `submission/` is git-ignored because
the identified files carry a postal address and a telephone number.

| File | What it is |
|---|---|
| `submission_manuscript.docx` | The manuscript. 7,993 words. |
| `submission_title_page.docx` | Title page with the identifying material. |
| `cover_letter.pdf` | Addressed to the Editor in Chief. |
| `fig1_funnel.eps`, `fig2_adjudication.eps` | Figures, separate files. |

## Why here

The article ends where a drafter can act — three responses of ascending
ambition, the least needing no legislation — and its output is a finite list
of terms rather than a rate. That is *The Loophole*'s readership exactly:
practising legislative counsel across the Commonwealth.

There is also a substantive reason. Saudi Arabia has **no general
interpretation statute**, which makes it the untreated case against which the
Commonwealth interpretation acts can be assessed — and the article says which
of its four conflicts such an instrument would and would not resolve. That
question belongs to this journal more than to any other.

## Previous submission

Submitted to *Statute Law Review* on 27 August 2026 (`STATLAW-2026-147`) and
desk-rejected on 28 August, before review, with a suggestion to try a company
law journal — which the article is not. See `README.md` for the diagnosis and
what was changed in response.

**Do not send this to the *European Journal of Law Reform* next.** Constantin
Stefanou, who signed the rejection, was EJLR's managing editor from 2012 to
2022 and remains on its advisory board, and he and Helen Xanthaki edit
*Statute Law Review* jointly from the Sir William Dale Centre at IALS.
