# Submission kit — *International Journal for Court Administration*

Read from the journal's own submission page on 29 August 2026.

| | |
|---|---|
| Journal | *International Journal for Court Administration* (IJCA) |
| Publisher | International Association for Court Administration |
| Review | **Double blind** |
| Fees | **None.** «The Journal does not charge any Article Publication Fees» |
| Access | Open access |
| Length | **≤ 7,000 words including footnotes.** Ours: 4,229 |
| Title | **≤ 8 words, no notes in it.** Ours: 7 |
| Biography | **Three sentences maximum**, no notes |
| Format | MS Word · Times New Roman 12 pt · **1.5 line spacing** · footnotes same face, 10 pt |
| Citations | **Chicago Manual of Style**, with an alphabetical bibliography and DOIs where available |
| Submit | <https://iacajournal.org> — the black box, upper right |
| Also required | competing interests declaration · copyright confirmation · affiliations and contact |

## Why here, and not somewhere with a bigger name

This is the right audience, not the fallback one. The article's finding is not
doctrinal and not economic: three quarters of appellate decisions add no
reasoning of their own to the public record, and whether a circuit writes is
not independent of what it decides. That is a fact about **what a publication
policy yields**, and the people who set publication policy are court
administrators. IJCA's readers are court officials, judges and justice
ministry staff. `../decision_map.md` says the audience for this finding is
whoever decides what gets published; this is the journal those people read.

Two desk rejections this month came from offering work to readers with no
stake in it. This is the correction, not a repetition.

## What the title change cost, and what it bought

The manuscript was called *Affirmed on the Reasons Below: Appellate Review in
15,383 Published Saudi Commercial Judgments* — thirteen words. IJCA allows
eight. It is now **Measuring Appellate Reason-Giving in Saudi Commercial
Courts**, and the corpus size moved into the abstract.

The evocative half was worth losing here. «Affirmed without reasons» would
have been shorter still and is what a reader wants to hear, but it is the
claim this article spends a section refusing: affirming on the reasons below
is reasoning by adoption, and the article says so. A title may not assert what
the text denies.

## What to send

`python3 build.py` produces all of it and refuses to finish if anything is
wrong.

| File | What it is |
|---|---|
| `submission_manuscript.docx` | **Anonymised.** 4,229 words. Journal format. |
| `submission_title_page.docx` | Name, affiliation, ORCID, biography, competing interests, word count. |
| `main.pdf` | The identified typeset copy, for your own record. |

## The audit, and why it is worth reading twice

`build.py` reads the built `.docx` back looking for seven strings that would
identify the author. Its first version read `word/document.xml` alone and
reported the file clean — while the repository URL, which carries the author's
GitHub handle, sat in a **footnote** about data availability. A `.docx` keeps
footnotes in a separate part of the archive.

Two things were wrong and both are fixed: the audit now reads every part that
can hold text, and the URL is gated on `\ifanon` so the anonymised build says
the repository is withheld and will be cited in the accepted version. The word
count still counts the body only, which is what a word limit means.

## Reference DOIs

Four were verified against Crossref on 29 August 2026 by matching title,
journal, year, volume and pages: Eisenberg 2004, Priest and Klein 1984,
Shavell 1995, Siegelman and Donohue 1990. **Cohen 2015 is not in Crossref and
is left without a DOI rather than guessed.** Vogel 2000 is a book.
