# What the court reaches for

The programme has established two things about non-statutory authority in
published Saudi commercial judgments of 1444–1446. Statute books differ in how
much of it accompanies them (`ECOLOGIES.md`), and the difference survives the
composition of the docket (`DOCKET.md`). Both are quantities. Neither says
anything about content.

This asks the content question. When the court reaches outside a statute,
**where exactly does it reach**, and is what it reaches for associated with the
statute, with the article, with a form of words, or with nobody in particular?

Seven answers were on the table before the measurement and none was preferred:

| | |
|---|---|
| A | stable code-specific doctrinal companions |
| B | article-specific companions, not code-specific |
| C | one generic fiqh reservoir shared by every code |
| D | recurring judicial templates rather than doctrine |
| E | a party-driven source ecology the bench echoes |
| F | mixed mechanisms, different per code |
| G | no stable structure at all |

The short answer is **F**, and the four codes that can be measured came out on
four different mechanisms. That is not a hedge. It is the result: the same
bench, in the same year, in the same city, reaches into a different
environment depending on which book it is applying, and the *reason* it is a
different environment is not the same reason twice.

---

## 0. Three limits, stated before any number

**The identity universe is bounded by the extractor.** `authority.py` can name
five jurists, eight books, six maxim texts and a set of hadith transmission
markers. A source outside that vocabulary is invisible here. After the
canonicalisation fix described below, **0.0** per cent of named-source mentions
are unresolved — and that is a fact about the vocabulary, not about the
judiciary. "The canon is compact" and "the extractor's vocabulary is compact"
are not distinguishable in this data, so no concentration statistic below is
read as a claim about the Saudi legal canon. Every count is a floor.

**Proximity is co-occurrence.** `locality_check.py` hand-read 63
neighbourhoods and found the ±500-character window 42.9 per cent related
overall. Nothing here says a source *supplements* an article. "Companion"
means *appeared near*, and it is used in that sense throughout.

**Local attachment is rare for most codes.** Of the 5,552 judgment-by-code
units in the layer, four codes clear the floor of 100 units. Seven do not, and
they are reported as INSUFFICIENT_DATA rather than estimated. In particular
the Civil Transactions Law, which the programme wanted to examine most, has
**51** locally attached units in this corpus and cannot be answered here at
all.

---

## 1. What was measured, and one bug that had to be fixed first

`companions.py` makes one corpus pass and writes one row per non-statutory
mention in the court's or a party's voice: the canonical identity of the
source, the nearest statutory citation at two locality definitions, the year,
the city, the speaker, and a fingerprint of the surrounding wording. No
judgment text is stored. 22,969 mentions from 9,842 judgments; 16,698 in the
court's voice.

The first pass produced a resolution table that looked healthy and was not.
The canonical table was written in ordinary orthography — «ابن تيمية»,
«مجموع الفتاوى», «العادة محكمة» — while lookups arrived orthographically
normalised, so those entries could never match themselves. Ibn Taymiyya was
split across two identities, one of them called `RAW.ابن تيميه`; the ﷺ
ligature normalised to the empty string and produced 531 rows with no identity
at all. The fix is to normalise the keys by the same function, which is the
whole of the alias handling: **two strings merge only when they are identical
after normalisation.** Nothing merges on similarity, and no LLM resolves
anything.

## 2. PHASE 4 — resolution quality

| | |
|---|---:|
| non-statutory mentions | 22,969 |
| of which name a source form | 13,181 |
| resolved to a canonical identity | **65.1** % |
| unresolved raw strings | **0.0** % |
| prophetic report with no collection named | **34.9** % |
| distinct canonical identities | 28 |
| resolutions that needed alias handling | **30.3** % |

The 34.9 per cent is the whole of the unresolved remainder: «صلى الله عليه
وسلم» and ﷺ are the formula that follows a mention of the Prophet, they name
no collection, and they are kept as an identity of their own rather than
guessed into Bukhari or Muslim.

**The audit set** is written to `companion_analysis_results.json` in full. Only six
identities merge more than one surface form, five of them trivially
(«رواه البخاري»/«أخرجه البخاري»). The sixth is a real decision: «شيخ الإسلام»
is read as Ibn Taymiyya. In Hanbali writing it almost always is, but it merges
a title with a name, and it matters, because the title form is **49.5** per
cent of all Ibn Taymiyya mentions. A reader who rejects that convention should
halve every Ibn Taymiyya figure below. The identity survives it: Ibn Taymiyya
would still be the implementing regulation's most distinctive named companion.

## 3. PHASE 5 — who the companions actually are

Court voice, nearest statutory citation within 500 characters, unit = one
judgment counted once per code.

**Evidence Law** (1,806 units) — settled judicial practice, trade custom, and
Ibn al-Qayyim.

| source | judgments | P(source\|code) | P(code\|source) | lift |
|---|---:|---:|---:|---:|
| hadith, no collection | 474 | 0.2625 | 0.322 | 0.99 |
| unattributed fiqh | 379 | 0.2099 | 0.2095 | 0.644 |
| settled judicial practice | 323 | 0.1788 | 0.5927 | **1.822** |
| Qur'an | 263 | 0.1456 | 0.304 | 0.935 |
| كشاف القناع | 260 | 0.144 | 0.3698 | 1.137 |
| trade custom | 181 | 0.1002 | 0.5858 | **1.801** |
| ابن القيم | 91 | 0.0504 | **0.6791** | **2.088** |

**Commercial Courts Implementing Regulation** (1,039 units) — the Hanbali
book-and-jurist environment, and by a distance the most named of the four.

| source | judgments | P(source\|code) | P(code\|source) | lift |
|---|---:|---:|---:|---:|
| unattributed fiqh | 442 | 0.4254 | 0.2443 | 1.306 |
| كشاف القناع | 298 | 0.2868 | 0.4239 | **2.265** |
| ابن تيمية | 289 | 0.2782 | 0.5711 | **3.052** |
| hadith, no collection | 147 | 0.1415 | 0.0999 | 0.534 |
| settled judicial practice | 109 | 0.1049 | 0.2 | 1.069 |
| مجموع الفتاوى | 77 | 0.0741 | 0.5969 | **3.19** |

**Commercial Courts Law** (2,000 units) — the generic reservoir, plus one
oddity: Abu Dawud, 81 judgments, **lift 2.271**, and 81.8 per cent of all its
appearances are here.

**Sharia Procedure Law** (472 units) — scripture. The Qur'an at **lift 2.217**
and المغني at 2.413, over a base that is 79.0 per cent untraceable.

## 4. PHASE 6 — specificity is not popularity

Ranked by lift rather than by count, the distinctive companions are not the
common ones. مجموع الفتاوى (129 judgments) has lift 3.19; كشاف القناع (703
judgments) has 2.265; ابن القيم appears in 134 judgments and P(code|source) for the
Evidence Law is **0.6791**. The four largest identities in the whole
layer — unattributed fiqh, untraced hadith, Qur'an, trade custom — are the
four that discriminate least. Popularity and specificity are close to
orthogonal here, which is the reason the top-of-table view in section 3 is not
the answer on its own.

## 5. PHASE 7 — the constrained null

The null permutes source identities across mention slots within each
year × city stratum, holding the year, the city, the number of authorities in
each judgment, the code each slot is attached to, and the global frequency of
every source. Rare strata barely mix, which makes the null *closer* to the
observed data and every z below conservative.

| code | source | observed | null | z |
|---|---|---:|---:|---:|
| CCIR | كشاف القناع | 298 | 154.3 | **16.71** |
| CCIR | ابن تيمية | 289 | 198.3 | **10.1** |
| CCIR | مجموع الفتاوى | 77 | 33.4 | **8.61** |
| Evidence | settled judicial practice | 323 | 176.4 | **14.92** |
| Evidence | trade custom | 181 | 99.7 | **11.07** |
| Evidence | ابن القيم | 91 | 47.0 | **9.31** |
| CCL | Abu Dawud | 81 | 31.8 | **10.84** |
| Sharia Procedure | Qur'an | 163 | 69.3 | **14.32** |

The negative side is as informative: Ibn Taymiyya is at z = -13.95 in the
Commercial Courts Law and z = -13.69 in the Evidence Law. The same jurist is
strongly over-represented beside one book and strongly under-represented
beside two others.

## 6. PHASE 8 — effective canon size, and why the word canon is not used

| code | top-1 | top-3 | top-5 | HHI | effective sources |
|---|---:|---:|---:|---:|---:|
| Evidence Law | 20.1 % | 49.8 % | 72.0 % | 0.1194 | 11.22 |
| Commercial Courts Law | 29.9 % | 68.5 % | 76.8 % | 0.1753 | 8.96 |
| CCIR | 28.8 % | 67.1 % | 83.8 % | 0.1758 | 7.55 |
| Sharia Procedure Law | 27.3 % | 75.6 % | 83.4 % | 0.1977 | 7.28 |

Three sources cover half to three quarters of every code's local authority.
That is concentration, and it is exactly the number that limit 0 forbids
reading as a finding: an extractor with 28 identities cannot report more than
28. The concentration statistics are kept because they are needed for the
retrieval question in section 13, and the word *canon* is not used for them.

## 7. PHASE 9 — the generic layer is most of the reach, and it is data

| code | untraceable share of local mentions | named fiqh as share of fiqh |
|---|---:|---:|
| Sharia Procedure Law | 79.0 % | 43.6 % |
| Commercial Courts Law | 74.5 % | 37.2 % |
| Evidence Law | 70.1 % | 60.2 % |
| CCIR | **49.3** % | 63.0 % |

Between a half and four fifths of what the court reaches for names no source
that can be looked up: «المقرر فقهاً», «قال تعالى» without the verse, a
prophetic report with no collection. Answer C is not a rival hypothesis to be
dismissed — at the level of raw mentions it is the majority of the phenomenon
in three of the four codes. What the rest of this document establishes is that
C is not the *whole* of it, and that the codes differ in how much of it there
is: the implementing regulation reaches for something nameable in half its
mentions, the Sharia Procedure Law in a fifth.

## 8. PHASE 12 — the decisive test: one judgment, two codes

Every comparison so far is between judgments and can be attacked on the docket.
This one cannot. Take the 162 judgments in which the same bench attaches
non-statutory authority locally to **both** the Evidence Law and the
Commercial Courts Law. Same judgment, same court, same year, same dispute,
same speaker. Then permute the identities across the slots *within each
judgment*, which holds that judgment's own source pool fixed and destroys only
which code each source sat beside.

| | |
|---|---:|
| judgments citing both, with local authority on each | 162 |
| observed profile cosine | **0.7036** |
| within-judgment null | 0.9734 (sd 0.013) |
| z | **-20.76** |
| p (one-sided, 500 permutations) | 0.002 |

At the stricter block window the same test gives cosine 0.5218 and z = -16.32
over 91 judgments. Against the implementing regulation instead, 72 judgments,
cosine 0.5975, z = -13.48.

**This kills G and it kills the docket explanation of content.** Within a
single judgment, the sources that sit beside the Evidence Law and the sources
that sit beside the Commercial Courts Law are not drawn from a common pool.
The largest separations are unattributed fiqh (-26.5 points toward the
Commercial Courts Law) and the Qur'an (+13.7 toward the Evidence Law); against
the implementing regulation the largest is Ibn Taymiyya, at -33.5.

## 9. PHASE 13 — correcting for what the locality measure gets wrong

The ±500 window is 60.0 per cent related for the Evidence Law and 23.1 per
cent for the Commercial Courts Law. Treating the observed profile as a mixture
of a true profile and the judgment's own background, at those two rates, the
cosine between the two codes falls from 0.7036 to **0.1763**. The known
imperfection of the locality measure **widens** the gap rather than
manufacturing it, exactly as the docket programme found for the quantity
result. The corrected numbers are a direction, not an estimate, and they are
not carried into any headline.

## 10. PHASES 14–15 — the code or the article?

Within one code, different articles do not have the same companions. The mean
cosine between article profiles is 0.414 inside the Evidence Law and 0.5186
inside the Commercial Courts Law — lower than the cosine *between* two codes
in section 8. Article identity matters, and the useful test is what happens
when the dominant articles are removed.

| code | dominant articles | mentions dropped | profile cosine, full vs remainder |
|---|---|---:|---:|
| Evidence Law | 29, 21 | 54.8 % | **0.8813** |
| Commercial Courts Law | 16, 30 | 57.1 % | 0.9473 |
| Sharia Procedure Law | 70, 76 | 51.7 % | 0.7963 |
| CCIR | 164, 64 | 84.7 % | **0.6503** |

Dropping articles 1 and 29 of the Evidence Law — the two the programme named
in advance — removes 46.5 per cent of its local mentions and leaves a profile
at cosine 0.907. **The Evidence Law's environment is not article 29's
environment.** The implementing regulation's is article 164's: remove it and
84.7 per cent of the local authority goes with it and the profile does not
survive. Answer B is right for one code out of four, and wrong for the other
three.

The Civil Transactions Law (articles 120 and 720) and the Law of Practice
(article 26) were named in advance for the same test. Both are
INSUFFICIENT_DATA: 51 and 57 locally attached units.

## 11. PHASES 16–16b — doctrine or boilerplate?

A companion carried by one form of words, repeated verbatim, is a template and
not a doctrinal environment. The fingerprint hash answers this directly.

| code | source | mentions | distinct fingerprints | top fingerprint |
|---|---|---:|---:|---:|
| CCIR | كشاف القناع | 307 | 64 | **39.7 %** (122 judgments, 2 cities) |
| CCL | unattributed fiqh | 820 | 260 | **35.9 %** (294 judgments, 4 cities) |
| CCIR | ابن تيمية | 438 | 149 | 14.8 % |
| Evidence | settled judicial practice | 325 | 234 | 10.8 % |
| Evidence | كشاف القناع | 262 | 170 | 3.8 % |

So answer D is real, and it is concentrated: two of the strongest edges in the
whole network are substantially one sentence each, circulating.

The falsification is to remove the circulating wording and run the two
positive tests again. Deleting every mention whose fingerprint appears in ten
or more judgments removes **30.8** per cent of all court-voice mentions.

| | full | de-boilerplated |
|---|---:|---:|
| PHASE 12 cosine (Evidence vs CCL) | 0.7036 | 0.7465 |
| PHASE 12 z | -20.76 | **-8.19** |
| PHASE 26 macro-F1 | 50.7 | **40.5** |
| PHASE 26 macro-F1, shuffled control | 16.3 | 18.3 |
| PHASE 26 accuracy | 53.9 % | 40.3 % |
| majority-class baseline | 37.8 % | 39.3 % |

The within-judgment separation survives outright. The signature survives on
macro-F1 and does not survive on accuracy, which lands on its majority
baseline. Both are reported: **the code signature is real and roughly a fifth
to a third of it is circulating wording.**

## 12. PHASE 17 — proposition families are not attempted

59.7 per cent of court-voice mentions sit in a fingerprint family that occurs
more than once, and 41.5 per cent in a family of five or more. That measures
shared *wording*. Two benches can state one proposition in different words and
be counted apart; one formula can carry different propositions. Extracting
proposition families would require reading, and reading is precisely what the
layer deliberately does not store. Verdict: FEASIBLE_ONLY_AS_WORDING_FAMILIES,
and not carried into any claim.

## 13. PHASES 18, 19–21, 22–24, 28 — the rest of the battery

**Maxims** are thin everywhere. Named maxim text reaches 3.1 per cent of CCIR
judgments, 2.6 per cent of Evidence and Commercial Courts judgments, 1.1 per
cent of Sharia Procedure judgments. الضرر يزال is the implementing
regulation's (2.7 per cent) and الأصل في العقود the other two's. Maxims are
first-class in the extractor and marginal in the corpus.

**Bench and bar cannot be separated locally.** The marginal profiles differ —
the bar's most distinctive move beside the Evidence Law is trade custom (23.7
per cent) and the bench's is settled judicial practice (17.9 per cent) — but
the paired measures need judgments where *both* voices attach authority to the
same code, and there are 22, 13, 11 and 5 of them. Survival bar→bench and
bench-generated share are reported in the results file and disqualified:
**answer E is not testable in this corpus**, in either direction.

**Stability.** Year-to-year profile cosine is 0.9391 (Evidence), 0.971 (CCL),
0.9644 (Sharia Procedure) and 0.8249 (CCIR). City-to-city is materially lower
— 0.7501, 0.6921, 0.8932, 0.7105 — and the weakest pair in the corpus is 0.4636,
between two cities inside one code. The companion structure is stable in time
and noticeably less stable in space, which is a finding about the judiciary's
geography and a warning about pooling.

**Portability.** The four generic identities are portable across all four
codes. كشاف القناع is portable (effective codes 3.07) but wildly uneven: 28.7
per cent of CCIR judgments and 3.4 per cent of Sharia Procedure judgments.
Abu Dawud is the most code-bound identity above the floor (effective codes
1.79). No named source is exclusive to one code.

**Retrieval.** A system given the statute alone covers **0.0** per cent of what
the court actually reaches for. The top three companions cover 50.5 per cent
of the Evidence Law's local mentions, 71.5 per cent of the implementing
regulation's; the top five reach 72.0 and 85.9 per cent. Those are cheap
numbers to bank, and they are bounded by limit 0: the ceiling is the
extractor's 28 identities, not the law.

## 14. PHASES 26–27 — the held-out signature test

Learn each code's source profile on four fifths of the judgments; take a
held-out judgment-and-code unit with at least two sources; predict which code
it belongs to from its sources alone.

| | accuracy | macro-F1 |
|---|---:|---:|
| observed | **53.9** % | **50.7** |
| constrained shuffle control | 29.0 % | 16.3 |
| chance | 25.0 % | — |
| majority-class baseline | 37.8 % | — |

Per code, the recall is very uneven: CCIR 86.2 per cent, Sharia Procedure 86.8,
Evidence Law 34.1, Commercial Courts Law 24.1. The Evidence Law's precision is
78.4 per cent — when the classifier says Evidence Law it is usually right, and
it says it rarely. The Commercial Courts Law is the class the model cannot
find, which is the same fact as section 7: its companions are the reservoir.

## 15. PHASE 30 — the mechanism, code by code

Thresholds are stated in `companion_analysis.py` and the signal table is in
the results file, so a reader who prefers different cuts can re-classify from
the signals rather than from the label.

| code | mechanism | why |
|---|---|---|
| Evidence Law | **A** code-specific stable | survives its dominant articles (0.8813), named companion Ibn al-Qayyim at lift 2.088 and z 9.31, year cosine 0.9391, F1 47.5 against a shuffled 6.0 |
| CCIR | **B** article-carried, with D | collapses without article 164 (0.6503), top fingerprint 39.7 % |
| Commercial Courts Law | **D** template-carried | robust to article dropping and to nothing else; top fingerprint 35.9 % across 294 judgments; 74.5 % untraceable |
| Sharia Procedure Law | **C** generic reservoir | 79.0 % untraceable, no named companion clearing lift 2 with z 3 |
| Civil Transactions Law, Companies Law, Law of Practice, arbitration, bankruptcy, and the remaining regulations | **H** insufficient data | 1–57 locally attached units each |

**E** is not testable and **G** is rejected corpus-wide by section 8 and
section 14 together.

## 16. The answer

> When contemporary Saudi adjudication reaches beyond a statute, does it reach
> into a stable, identifiable doctrinal environment associated with that
> statute — and if so, is that environment carried by the code, the article,
> the judicial template, or the speaker?

It reaches into an environment that is **identifiable** — a classifier
recovers the code from the sources alone at 53.9 per cent against a
constrained shuffle at 29.0, and within a single judgment the two codes' local
sources separate at z = -20.76 — and that is **stable in time** and less
stable across cities.

It is **not one thing**. In the Evidence Law it is carried by the code: it
survives the removal of the articles that generate most of it. In the
Commercial Courts Implementing Regulation it is carried by a single article,
164, and substantially by one repeated sentence. In the Commercial Courts Law
it is carried by circulating wording over a generic reservoir. In the Sharia
Procedure Law it is the reservoir, scripture-weighted, with nothing nameable
above it. Whether it is carried by the speaker cannot be answered here: there
are five to twenty-two judgments per code in which both bench and bar attach
authority to the same code locally.

And underneath all four, most of what the court reaches for names no source at
all. That is the largest single fact in this document and the one least
amenable to retrieval, citation-network analysis, or any technology that
assumes the authority has an address.

---

## 17. PHASE 31 — the frame decision for Paper B

The programme's standing frame was C, CODE_EFFECT_SURVIVES_DOCKET. This
result does not overturn it and does not simply extend it, because it changes
what the code effect is a claim *about*. Five frames were available:

| | frame | verdict |
|---|---|---|
| A | codes carry distinct doctrinal canons | **rejected** — one code of four, and the word canon is not supportable |
| B | the quantity result stands alone; content is undifferentiated | **rejected** by the within-judgment test |
| C | code effect survives the docket, quantity only | superseded, not contradicted |
| D | code-associated authority environments, heterogeneous in mechanism | **adopted** |
| E | the whole effect is template and article artefact | **rejected** — it survives de-boilerplating on macro-F1 and survives it outright within judgments |

**FRAME D — CODE_ASSOCIATED_AUTHORITY_ENVIRONMENTS, HETEROGENEOUS.** Paper B
may say that published Saudi commercial judgments attach different
non-statutory authority to different statute books, in quantity and in
identity, within the same judgment; that the identity difference is not
carried by one mechanism; and that most of the authority so attached names no
traceable source. It may not say that any code has a canon, that a source
supplements an article, or that the bench differs from the bar in what it
reaches for — the last for want of data, not for want of a difference.

Paper B's status remains WRITE_PENDING; the manuscript is not written in this
session.

---

## What this kills and what it leaves

- **Killed: G.** Sources are not drawn from a common pool. Section 8.
- **Killed: A as a general answer.** Only one code of four survives its own
  dominant articles with a named companion above the null.
- **Bounded: C.** True of the majority of mentions, false as a claim that the
  codes are interchangeable.
- **Bounded: D.** Real, measurable, and worth between a fifth and a third of
  the signature — not the whole of it.
- **Not testable: E.** Reported as such, with the counts that disqualify it.
- **Standing: F**, with the per-code assignment above.

## Standing limitations

- Published commercial judgments of 1444–1446, not the Saudi judiciary.
- The identity universe is the extractor's vocabulary. Every count is a floor
  and no concentration statistic is a statement about the canon.
- Proximity is co-occurrence inside a character window, measured 42.9 per cent
  related overall by hand. Nothing here says a source supplements an article.
- Four codes are answerable. Seven are not, including the Civil Transactions
  Law, which is the code the next question most needs.
- One primary annotator for the locality gold set; no inter-annotator
  agreement is claimed.
- «شيخ الإسلام» is read as Ibn Taymiyya, and that convention carries 49.5 per
  cent of his mentions.

## Prior work this sits next to

The closest published neighbour is the pre/post study of the Civil
Transactions Law that reads 2,913 judgments decided before it and 61 under it
and reports article citation in compensation judgments rising from 36 to 62
per cent, with articles 120 and 720 named. That measures a shift in *whether*
courts cite provisions. Nothing found measures *which non-statutory sources
sit beside which provisions*, or tests it within a single judgment. The narrow
novelty claim is that one, and it is narrow on purpose.
