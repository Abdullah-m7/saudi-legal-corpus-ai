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

## Previous submission

Submitted to the *Journal of Legal Analysis* on 27 August 2026
(`LEGAL-2026-209`) and desk-rejected on 28 August 2026, same day, on scope:
*"not a good fit."* No reviewer saw it. The manuscript was retargeted rather
than revised — the JLA-specific layout (1.25-inch margins, endnotes gathered
after the references, a 100-word abstract cap) was undone, and the abstract
expanded to the length the argument actually needs.
