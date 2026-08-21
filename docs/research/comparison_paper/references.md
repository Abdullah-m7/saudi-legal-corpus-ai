# References — verified, not recalled

Every entry here was checked against a source that states its bibliographic
details, and the check is recorded. Nothing on this list is written from
memory. Recalling a citation and recalling it correctly feel identical, which
is the same failure that produced the withdrawn measure in this paper and the
fabricated example that review caught in paper 4.

Status values: **verified** — details confirmed from a publisher page or an
indexing record; **pending** — not yet checked, not usable.

| Work | Details | Status | Checked against |
|---|---|---|---|
| Wang & Strong, *Beyond Accuracy: What Data Quality Means to Data Consumers* | Journal of Management Information Systems, vol. 12 no. 4 (1996), pp. **5–33** | **verified (Crossref)** | Crossref deposit for DOI 10.1080/07421222.1996.11518099. A search summary gave both 5–34 and 5–33; the publisher's own deposit gives 5–33 |
| Gebru et al., *Datasheets for Datasets* | Communications of the ACM, vol. 64 no. 12 (2021), pp. 86–92; **seven authors** | **verified (Crossref)** | Crossref deposit for DOI 10.1145/3458723 gives exactly seven authors. The ACM page shows "+3" beside the author list, which is a display artifact, not additional authors |
| Neumaier, Umbrich & Polleres, *Automated Quality Assessment of Metadata across Open Data Portals* | ACM Journal of Data and Information Quality, vol. 8 no. 1, Article 2 (2016) | **verified (Crossref)** | Crossref deposit for DOI 10.1145/2964909; it records the range 1–29, the journal uses article numbers, and the reference gives the article number |
| Janssen, Charalabidis & Zuiderwijk, *Benefits, Adoption Barriers and Myths of Open Data and Open Government* | Information Systems Management, vol. 29 no. 4 (2012), pp. 258–268 | **verified (Crossref)** | Crossref deposit for DOI 10.1080/10580530.2012.716740 confirms issue 4, against a summary that said issue 3 |
| W3C, *PROV-DM: The PROV Data Model* | W3C Recommendation, 30 April 2013 | **verified** | W3C TR page; dated version at `/TR/2013/REC-prov-dm-20130430/` |

## Every DOI re-checked against Crossref

After the first pass, all four DOIs were resolved through the Crossref API,
which returns the publisher's own deposited metadata rather than a page
rendering or a summary of one. Two entries changed as a result, and both
changes were in details no reader would ever question:

- **Wang & Strong** ends at page **33**, not 34. Search results gave both.
- **Gebru et al.** has exactly **seven** authors. The ACM page displays "+3"
  beside the author list, which is a display artifact; a reference list built
  from that page could have carried three authors that do not exist.

Neither error would have been caught by re-reading the manuscript. Both were
caught by asking a different system the same question.

## One entry that shows why the check is not ceremonial

A summarising layer reported the Janssen et al. article as *issue 3*. The
publisher's own page title and an independent lookup both give **issue 4**. A
wrong issue number is invisible to a reader, survives every internal check a
manuscript has, and is the kind of thing an author is certain about precisely
because it was recalled rather than looked up.

## Why this file exists separately

A related-work section is the part of a paper most often written from memory,
because the author already knows the literature. It is also where a wrong year,
a wrong volume or a half-remembered claim is least likely to be challenged
before publication. Keeping the check visible, per entry, makes the omission of
a check visible too.
