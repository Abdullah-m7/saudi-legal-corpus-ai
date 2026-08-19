# Cover Letter — Language Resources and Evaluation

*Paste the text below into the "Cover Letter" field in Editorial Manager, or
upload it as a separate file if the system asks for one. Add the date and,
if the journal's page lists them, the editors' names in the salutation.*

---

Dear Editors,

I am pleased to submit the enclosed manuscript, **"The Saudi Legal Corpus
for AI: An Auditable, Official-Source-Grounded, Article-Level Corpus of
Saudi Arabian Legislation,"** for consideration as an Original Paper in
*Language Resources and Evaluation*.

The manuscript describes a new language resource: a corpus of 290 Saudi
legislative instruments structured into 15,689 article-level records
(approximately 1.2 million Arabic tokens) across twelve legal domains,
together with derived analytical layers and a retrieval benchmark. To my
knowledge, no openly documented, machine-readable, article-level corpus of
Saudi legislation has previously been described in the literature, and
Arabic is at most marginally represented in the existing legal-NLP resource
landscape (Pile of Law, MultiLegalPile, LexGLUE, LEXTREME, LegalBench).

I believe the work fits the journal's scope in three respects. First, it is
a resource paper in the strict sense: the contribution is the corpus, its
construction methodology, and its documentation, rather than a modelling
result. Second, it addresses resource *quality* as a first-class concern —
every record carries its own provenance label, every instrument is placed in
a four-tier source-verification taxonomy, and known source-staleness risks
are published rather than concealed, which I offer as a reusable template
for building legal corpora in jurisdictions without a machine-readable
official gazette. Third, it includes an evaluation component: a manually
confirmed 519-query retrieval benchmark with two deterministic baselines
reported per query category, which localizes where retrieval over Arabic
statutory text is actually hard (definitional queries, where the corpus's
engineered retrieval metadata outperforms BM25 by 16.4 points of top-1
accuracy).

The corpus, all derived layers, all validators, the evaluation pack, and the
scripts that reproduce every figure in the manuscript are openly available
under the MIT licence and archived on Zenodo with a citable DOI
(10.5281/zenodo.22019183), so every statistic reported in the paper can be
independently regenerated from the archived version.

The manuscript is original, has not been published previously, and is not
under consideration by any other journal or conference. There are no
competing interests and no funding to declare. I am the sole author. The
corpus contains enacted national legislation and no personal data; the
manuscript states explicitly that it is not an official government
publication, contains no official translation, and does not constitute legal
advice.

Thank you for your consideration. I would be glad to provide any further
information the review process requires.

Yours sincerely,

**Abdullah Almohammedi**
Independent Researcher
abdullah.m.almohammedi@gmail.com
ORCID: 0009-0001-0832-0995
