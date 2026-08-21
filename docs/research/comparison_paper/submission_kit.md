# Paper 6 — submission kit for *Government Information Quarterly* (Elsevier)

Requirements taken from the journal's own guide for authors, read in full. Not
from a search summary: two secondary sources described the review model as
single anonymized, and the guide says **double anonymized**.

## What the journal requires, and where we stand

| Requirement | Status |
|---|---|
| **Double anonymized review** — title page and anonymized manuscript as **separate files** | `build.py` produces both; the anonymity audit checks in both directions |
| **Abstract ≤ 250 words** | 248 |
| **Keywords: 1–7** | 6 |
| **Highlights: 3–5 bullets, ≤ 85 characters each**, separate file with `highlights` in the name | `highlights.txt`, generated and length-checked by `make_highlights.py` |
| **Source file `.tex`** — PDF is not an acceptable source | LaTeX throughout |
| **Figures as separate files**, ≥ 300 dpi, ≥ 2244 px at full page width | 2280 px, 300 dpi, TIFF + EPS + PNG |
| **Never combine graphs into one image** | The single panelled figure was split into two |
| **Numbered sections** (1, 1.1, 1.1.1) | Article class numbers them |
| **US spelling** | Converted |
| **APA 7th citations**, alphabetical reference list | Converted; six entries, every DOI re-checked against Crossref |
| **CRediT roles** | In the declarations |
| Declaration of generative AI use | Complete, with tool and version |
| Funding statement (the journal supplies wording for "none") | Present |
| Competing interests | Present |
| Research data — **Option B**, deposit *encouraged* | Exceeded: GitHub plus Zenodo with a DOI |
| **Vitae** — biography ≤ 100 words plus a passport-type photograph, editable format | **Outstanding: the photograph is the author's to supply** |
| Graphical abstract | Encouraged, not required. Not planned |

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

## Before submitting

- [ ] APA conversion, with every entry checked against `references.md`
- [ ] Author biography (≤ 100 words) and photograph — the author's to write and
      supply; a biography is a statement about a person, not about data
- [ ] Confirm the affiliation spelling in the submission profile. The
      ScholarOne account used for paper 3 carries `Independent Reseacher`
- [ ] Read the system-generated PDF proof to the last page before sending
