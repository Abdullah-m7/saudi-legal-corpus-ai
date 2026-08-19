# Submission Kit — Editorial Manager (Language Resources and Evaluation)

Every field Editorial Manager asks for, with the exact text to paste. Plain
text only — no LaTeX markup — since the submission interface stores what you
type verbatim and that is what gets published.

Submission system: <https://www.editorialmanager.com/lrev/>

---

## Files to upload

| Order | Item type | File |
|---|---|---|
| 1 | Manuscript | `main.pdf` |
| 2 | LaTeX source | `main.tex` |
| 3 | Bibliography | `references.bib` |
| 4 | Figure | `example_record.png` |

Some Springer journals request source files only on acceptance. Upload the
PDF as the manuscript; add the source files if the system offers a slot for
them.

---

## Article type

**Original Paper** — the contribution is a complete resource with an
evaluation component, not a short project note.

---

## Title

```
The Saudi Legal Corpus for AI: An Auditable, Official-Source-Grounded, Article-Level Corpus of Saudi Arabian Legislation
```

---

## Abstract (plain text)

```
Legal natural language processing has advanced rapidly for English and several European languages, but Arabic - and Saudi Arabian law in particular - remains critically under-resourced: to our knowledge, no openly documented, machine-readable, article-level corpus of Saudi legislation has previously been described. We present the Saudi Legal Corpus for AI, a corpus of 290 legislative instruments (201 statutory laws, 64 statutory regulations, 24 implementing regulations, and one set of procedural rules) covering the Kingdom of Saudi Arabia's principal legislation, structured into 15,689 article-level records (approximately 1.2 million Arabic tokens) in a unified, retrieval-ready index spanning twelve legal domains. The corpus rests on three design commitments that distinguish it from web-scraped legal collections: official-source grounding, in which every track records its issuing authority and official source and every record carries its own provenance label (251 distinct labels) under a four-tier source-verification taxonomy; auditability, enforced by 376 read-only, idempotent validators and fully deterministic derived layers; and the governing-text principle, under which the official Arabic text governs and all other language layers are explicitly non-authoritative. Beyond the text, the corpus ships analytical layers that are, to our knowledge, the first of their kind for Saudi law: a statutory citation graph (3,607 references, 585 of them between distinct instruments), a hand-classified supersession graph (102 edges), a glossary of 1,920 statutorily defined terms with 3,318 definitions, an embedding-ready chunking layer (16,304 chunks), and a manually confirmed retrieval benchmark of 519 gold queries. On that benchmark the corpus's metadata-based lexical searcher reaches 93.3% top-1 accuracy against 90.4% for a standard BM25 baseline, with the gap concentrated on definitional queries (90.9% versus 74.5%), quantifying the value of the engineered retrieval metadata while leaving informative headroom for neural Arabic legal retrieval. We describe the construction methodology in full, report statistics that are reproducible from the archived release, and discuss intended uses, limitations, and the legal and ethical boundaries of releasing structured national legislation for artificial-intelligence research.
```

---

## Keywords

```
Legal NLP
Arabic language resources
Saudi Arabia
Legislative corpus
Information retrieval
Data provenance
```

---

## Classifications

From the personal-classification tree, select these leaves (not the parent
headings):

- 1.100 — Methods, tools and procedures for the acquisition, creation …
- 1.700 — Metadata descriptions of LRs
- 1.250 — Availability and use of generic vs. task/domain specific LRs
- 1.300 — Monolingual and multilingual LRs
- 2.050 — Evaluation, validation, quality assurance of LRs
- 2.150 — Benchmarking of systems, resources for benchmarking

If more are allowed: 1.200 (organizational and legal issues), 1.050
(guidelines and best practices), 2.200 (evaluation in written language
processing).

---

## Declarations entered through the interface

These are published from the interface values, not from the manuscript, so
they must be entered here as well.

**Author contributions**

```
A. Almohammedi is the sole author and conducted all aspects of the work.
```

**Competing interests**

```
The author declares no competing interests.
```

**Funding**

```
No funding was received for conducting this study.
```

**Ethics approval**

```
Not applicable. The study involves no human participants, no animal subjects, and no personal data; it processes published national legislation only.
```

**Data availability**

```
The corpus, all derived layers, all validators, the evaluation pack, and the scripts that reproduce every figure reported in this paper are openly available at https://github.com/Abdullah-m7/saudi-legal-corpus-ai and archived on Zenodo under the MIT licence. The version described here is v1.0.2, DOI: 10.5281/zenodo.22019183; the concept DOI 10.5281/zenodo.22019182 always resolves to the latest version.
```

**Code availability**

```
All code is included in the archived release cited under data availability.
```

---

## Cover letter

See `cover_letter.md` in this directory; paste its body into the cover-letter
field.

---

## Before you press Submit

1. The system builds a merged PDF and holds the submission until you
   **approve** it. An unapproved submission never reaches the editor — this
   is the single most common way a submission stalls.
2. Check that the author name, affiliation ("Independent Researcher"), and
   ORCID in the interface match the manuscript exactly.
3. Confirm the manuscript is not under review anywhere else; the cover letter
   states that it is not.
4. Submit from a computer rather than a phone: the process spans several
   screens with file uploads and long text fields.
