# Novelty check

A **scoping** check, not a systematic review: four targeted searches, run
after the results were fixed, with the sources named. It is enough to decide
whether to write, and not enough to claim priority. Anything that matters
should be re-checked against a law-library database before submission.

| our finding | closest prior work | what they measured | what we measure differently | status |
|---|---|---|---|---|
| Court and litigants inside **one document** invoke systematically different *kinds* of legal authority | Larson, *Precedent as Rational Persuasion* — states there had been "no prior extant empirical study of how lawyers and judges use citations to construct their legal arguments"; Texas L. Rev., *Does Lawyering Matter?* (citations in briefs predict summary-judgment outcomes) | precedent citations, in **briefs and opinions as separate documents**, common-law | authority **type** composition (statute · contract · fiqh · maxim · scripture · custom · discretion), speaker-segmented **within one published judgment**, hand-validated | **likely novel** |
| Whole-document citation counts **mismeasure** judicial reasoning | rhetorical-role segmentation: LegalSeg, SAILER (Procedure/Fact/Reasoning/Decision/Tail), CaseEncoder — the Fact segment explicitly "includes a description of the parties' arguments" | segmentation built for **summarisation and retrieval** | the same segmentation used to show that the unsegmented count is measuring a blend of two voices, and by how much | **novel framing on established tooling** |
| Statutory citation is concentrated: 7 articles carry 50 % | Ukrainian 100M-decision citation graph (constitutional references, mean 3,570 vs median 6); Czech apex-court citation data | concentration of citations, whole-document, civil-law Europe | concentration in the **bench's own reasons only**, plus **entry latency** of a new statute into the core | **phenomenon not novel; the core-entry measure is** |
| Explicit statute + fiqh hybrid reasoning quantified at corpus scale, with its shape (one statute + one jurist) | qualitative Islamic-law scholarship on qawāʿid and on Saudi deference to the Ḥanbalī opinion; *God's Law, King's Court* | doctrinal and qualitative | 28,090 judgments, typed, court-voice only, per year | **likely novel** |
| Saudi judicial reasoning measured with NLP at all | nothing surfaced in these searches | — | — | **likely novel; thin field** |
| Within-judgment transition matrix: invariant statutory floor, responsive non-statutory layer | amicus-brief reference studies; brief-citation-in-opinion counts (Indiana) | **whether** a brief is cited | **what kind of authority** the bench answers with, conditional on what was raised, in the same dispute | **likely novel** |

## What would change the assessment

Two literatures were not reachable from these searches and could contain the
result: (a) continental *Rechtssoziologie* on Parteivortrag versus
Entscheidungsgründe, and (b) any Arabic-language empirical legal scholarship.
Neither was searched in its own language. That gap is stated rather than
assumed away.

## Sources consulted

- [Precedent as Rational Persuasion](https://www.legalwritingjournal.org/article/24781-precedent-as-rational-persuasion)
- [Does Lawyering Matter? Predicting Judicial Decisions from Legal Briefs](https://texaslawreview.org/does-lawyering-matter-predicting-judicial-decisions-from-legal-briefs-and-what-that-means-for-access-to-justice/)
- [Negative References to Amicus Briefs in Judicial Reasoning](https://www.cambridge.org/core/journals/journal-of-law-and-courts/article/negative-references-to-amicus-briefs-in-judicial-reasoning/6BB14596D5203ACBAEE01F1FCC41AD72)
- [LegalSeg: Rhetorical Role Classification](https://arxiv.org/pdf/2502.05836)
- [Natural Language Processing for the Legal Domain: A Survey](https://arxiv.org/pdf/2410.21306)
- [Automatic Construction of a Legal Citation Graph from 100 Million Ukrainian Court Decisions](https://arxiv.org/pdf/2605.15362)
- [Citation Data of Czech Apex Courts](https://arxiv.org/pdf/2002.02224)
- [God's Law, King's Court: Ḥudūd Jurisprudence under Saudi Arabia](https://journalofislamiclaw.com/current/article/view/alnemari)
- [Canons (Qawāʿid) and Reasoning in Islamic Law and Ethics](https://islamiclaw.blog/2020/05/21/canons-qawa%CA%BFid-and-reasoning-in-islamic-law-and-ethics/)

## Decision

**WRITE — one paper, and only one.**

Working title: *When Judges and Litigants Speak Different Legal Languages:
speaker-aware measurement of legal authority*.

The contribution is methodological and the setting is Saudi commercial
adjudication. The general claim it can carry is narrow and defensible: **if
the two voices inside a judgment invoke different kinds of authority, then
whole-document citation counts measure a blend, and the error is structural
rather than statistical.** The Saudi corpus demonstrates it and cannot
establish it elsewhere; the paper should say so and invite the same check in
jurisdictions where segmentation is possible.

What is *not* in this paper: the codification/hybrid result and the
operational-core result. Both are strong, both are recorded here, and both
would dilute a methodological argument. They are a second paper or they are
sections of the map, not this.
