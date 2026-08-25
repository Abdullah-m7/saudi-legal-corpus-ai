# Paper 6 — submission kit for *Government Information Quarterly* (Elsevier)

Requirements taken from the journal's own guide for authors, read in full. Not
from a search summary: two secondary sources described the review model as
single anonymized, and the guide says **double anonymized**.

## What the journal requires, and where we stand

| Requirement | Status |
|---|---|
| **Double anonymized review** — title page and anonymized manuscript as **separate files** | Done. `build.py` produces both and audits in both directions |
| **Abstract ≤ 250 words** | 248 |
| **Keywords: 1–7** | 6 |
| **Highlights: 3–5 bullets, ≤ 85 characters each**, separate file with `highlights` in the name | `highlights.txt`, generated and length-checked by `make_highlights.py` |
| **Source file `.tex`** — PDF is not an acceptable source | LaTeX throughout |
| **Figures as separate files**, ≥ 300 dpi, ≥ 2244 px at full page width | 2280 px, 300 dpi, TIFF + EPS + PNG |
| **Never combine graphs into one image** | The single panelled figure was split into two |
| **Numbered sections** (1, 1.1, 1.1.1) | Article class numbers them |
| **US spelling** | Converted |
| **APA 7th citations**, alphabetical reference list | Converted; six entries, every DOI re-checked against Crossref |
| **CRediT roles** | On the title page — the line names the author, so it cannot sit in the anonymized manuscript |
| Declaration of generative AI use | Complete, with tool and version |
| Funding statement (the journal supplies wording for "none") | Present |
| Competing interests | Present |
| Research data — **Option B**, deposit *encouraged* | Exceeded: GitHub plus Zenodo with a DOI |
| **Vitae** — biography ≤ 100 words plus a passport-type photograph, editable format | Done. 87 words, chosen and filled in by the author, set on the title page from `biography.md`; photograph supplied: `Almohammedi_photo.jpg`, 1254x1254 JPEG |
| Graphical abstract | Encouraged, not required. Not planned |

## The anonymized build

`build.py` produces both files from `main.tex`. Three things about it are worth
knowing before anyone edits it.

**The identity is deleted, not switched off.** The journal wants LaTeX source,
not a PDF. A `.tex` that carries the author inside a disabled `\else` branch
carries the author in plain text to everyone who opens the upload. So the
script resolves every `\ifanon` block and writes out only the surviving
branch; `main_anonymous.tex` has no author block to re-enable.

**The declarations are split, not dropped.** An earlier version moved the whole
Declarations section to the title page, which took the data-availability
statement and the note on the subject with it. Neither names anyone, and a
reviewer needs both — the first to judge reproducibility, the second because
without it the article can be read as an accusation against the publisher it
studies. Only the CRediT line and the repository URL are held back now, and the
manuscript says where the URL went.

**The audit runs in both directions.** The manuscript must contain no
identifying token, in its source, in its rendered text, and in the PDF metadata
that no reader sees but every properties dialog shows. The title page must
contain the name, the email and the ORCID: a title page that passed an
anonymity check would mean the identity had been stripped from the one file
meant to carry it.

### The one thing anonymity cannot cover

The article describes its companion study as measuring one state's legal
record, and names that state as Saudi Arabia once, where the methods section
compares network conditions. A determined reviewer could find the companion
study and, from it, the author. This is normal in double anonymized review and
not worth mutilating the paper to prevent: the alternative is a methods section
that hides which jurisdiction a measurement came from, which is worse than being
identified. Anonymity here means not self-identifying, not being unfindable.

## What the APA conversion turned up

Converting from OSCOLA footnotes to author–date citations forced every entry to
carry volume, issue and page numbers that a footnote can elide — and that is
where two errors were sitting. Each DOI was resolved through the Crossref API,
which returns the publisher's own deposited metadata rather than a rendering of
a page:

- **Wang & Strong** ends at page **33**, not 34. Search results gave both
  numbers; the deposit settles it.
- **Gebru et al.** has exactly **seven** authors. The ACM page shows "+3"
  beside the author list, which is a display artifact. A reference list built
  from that page would have carried three authors who do not exist.

Neither would have been caught by re-reading the manuscript. Both were caught
by asking a different system the same question.

Four remaining footnotes are substantive notes rather than citations, which APA
permits sparingly. One said "Ibid." — a legal-citation idiom with no place in
an author–date system — and now names its source.

## Things that are not required, and are not being done

The journal encourages a graphical abstract and co-submission to *Data in
Brief*. Neither is planned: the article has two figures that already carry its
argument, and its data is already deposited under a DOI.

## What to upload

| File | What it is |
|---|---|
| `main_anonymous.tex` | The manuscript source. No author block, no repository URL, no ORCID |
| `numbers.tex` | Included by the manuscript; every measurement it reports |
| `fig1_all_flagged_effects.tiff`, `fig2_excluding_prospective.tiff` | Figures, separate files, 300 dpi, 2280 px. **Two files, not one** |
| `highlights.txt` | 5 bullets, each within 85 characters |
| `title_page.pdf` | Identity, declarations, CRediT, data availability, vitae |
| `Almohammedi_photo.jpg` | Passport-type photograph |

`main_anonymous.pdf` is for reading before upload; the system compiles its own
from the source.

## Before submitting

- [ ] APA conversion, with every entry checked against `references.md`
- [x] Author biography — chosen and completed by the author: Option B, 87
      words, trained in law, based in Rabigh, Saudi Arabia. Set on the title
      page directly from `biography.md`, so the two cannot disagree
- [x] Passport-type photograph: `Almohammedi_photo.jpg`. Plain white
      background, face forward, even lighting, 1254x1254 px — over 300 dpi at
      any width a journal prints an author photo. Square rather than portrait,
      which journals accept; there is headroom to crop to portrait if asked
- [ ] Confirm the affiliation spelling in the submission profile. The
      ScholarOne account used for paper 3 carries `Independent Reseacher`
- [ ] Read the system-generated PDF proof to the last page before sending
- [ ] Check the proof's first page for a byline the system added from the
      submitting account. The manuscript file is clean; the platform is a
      separate opportunity to break anonymity
