# What this repository can now answer that it could not before

Eight questions, ranked. Nothing here is opened in this session; the point is
to record what the asset makes reachable, so the next session chooses rather
than drifts.

Ranked on five criteria — novelty, scientific importance, data readiness,
validity, contemporary relevance — each scored H/M/L.

| # | question | nov | imp | data | val | now | verdict |
|---|---|---|---|---|---|---|---|
| 1 | **Do litigants and courts diverge in other legal families?** Replicate the speaker-aware measurement on a jurisdiction with public briefs and role-labelled judgments (Indian rhetorical-role data is public). | H | H | M | H | H | **the strongest** |
| 2 | **What distinguishes law that becomes operational from law that is merely enacted?** The descriptive profile exists: operational articles are earlier, longer, jurisdiction- and proof-bearing, and 13× more likely to have been amended. | H | H | H | M | H | **ready now** |
| 3 | **What is the shape of contemporary hybrid reasoning?** One statute plus one jurist, 40 % of hybrid judgments; the asset is built. Needs a legal reading, not more counting. | H | M | H | H | H | ready |
| 4 | **How long does a new statute take to become operational, and what predicts it?** Evidence Law ≈ 1 year; the Civil Transactions Law has not arrived in two. n = 2 reforms is the binding constraint. | H | H | M | L | H | wait for a third reform |
| 5 | **Does speaker mixing degrade a legal AI system measurably?** Take a retrieval or QA system, ground it on full judgments and on court-reasoning-only, and compare. Directly tests implication VIII.C. | H | H | M | M | H | needs a system, not data |
| 6 | **Do institutions have authority fingerprints?** The committees are 96 % statutory against the courts' 71 %, but abridgement confounds it. Needs a third publisher whose editorial practice is known. | M | M | L | L | H | blocked on Source C |
| 7 | **Does authority structure predict appellate survival?** The appellate linkage exists (13,924 paired records) and the layer is built; the design risk is selection into appeal. | M | H | H | L | M | design first |
| 8 | **Is the article-level non-overlap a Saudi fact or a procedure fact?** 79.7 % of paired judgments share no article. Jurisdiction and default are decided whether or not raised — how much of the non-overlap is that? | H | M | H | M | H | decomposable now |

## Excluded on purpose

Anything purely historical. The corpus reaches back to 1422 and the temptation
to write a history of Saudi commercial adjudication is real and is refused:
the older years carry 1–2 per cent of judgments with reasons and cannot
support the comparison they invite. History enters only as a baseline for a
recent reform.

## Resolved, and what replaced them

**#8 is decomposed.** `DECOMPOSITION.md`: article-level non-overlap moves
from 80.2 to 78.5 per cent when the articles a court must invoke by virtue of
its office are removed, and to 56.5 among dispute-specific articles only.
Procedure does not explain it. What it *is* is intra-code: the two sides
share an instrument in 56.2 per cent of judgments where both cite statute and
an article in 35.3 per cent of those. The question is closed as posed.

**#3 is chosen and opened.** `NEXT_PROGRAMME.md` compares it against #2 and
against the alignment programme, and it wins on data readiness that the other
two lack: the alignment programme is blocked by its own feasibility pilot
(the pairing is not identifiable at proposition level), and #2/#4's clock is
the year, which cannot carry a time-to-first-citation design. The reframed
question is *where in a codified statute book non-statutory authority remains
necessary, and what property of a provision predicts it* — the article-level
rate runs from 1.1 to 85.9 per cent and the structural/dispute distinction
explains three points of that eighty.

**#4 is downgraded, on a measured ground rather than a guess.** The judgment
layer carries `year` and nothing finer, so time to first citation has five
ticks over the whole window and three since the Civil Transactions Law; and a
provision's first *published* citation is a fact about the publication policy
as much as about adjudication. It stays descriptive until a finer date exists.

## The capability ledger

Eight things the asset was meant to be able to answer. Where each now stands,
and by which artefact:

| capability | state | where |
|---|---|---|
| what courts cite | answered | `map_results.json`, `claim_results.json`, the profile |
| what litigants cite | answered, bracketed by two specifications | same, `strict_party` / `wide_party` |
| where they overlap | answered at six levels | `overlap_results.json` |
| where they diverge | answered, and decomposed | `DECOMPOSITION.md` |
| what authority combinations courts use | answered | `hybrid_view.json`, `hybrid_results.json` |
| which provisions form the operational core | answered, and classified by function | `core_view.json`, `core_function.json` |
| how recent statutes enter adjudication | **partial** — visibility yes, timing no, because the clock is the year | `lawinaction_results.json` |
| how litigant arguments are legally handled | **partial** — at judgment level yes, at proposition level the corpus does not support it | `pairs_gold.json` |

Six of eight are answered from generated files. The two that are not, are not
blocked on effort: one needs a finer date than the corpus records, the other
needs judgments to name the article they are rejecting, and they do not.
Both are stated as limits rather than as work items, because pretending
otherwise is how a research programme spends a year on an unanswerable
question.

## The capability ledger, after the completeness programme

| capability | state | where |
|---|---|---|
| which provisions are sufficient on their own | **partial** — an article-level rate exists for 239 provisions, but the class that predicts it is institutionality rather than completeness | `completeness_layer.csv`, `COMPLETENESS.md` |
| which provisions draw supplementation | answered, article by article | `completeness_layer.csv` |
| what kind of supplementation | answered on 40 hand-read judgments, as an interpretive layer with rules and an ambiguity class | `hybrid_roles_gold.json` |
| does the bench supplement differently from the bar | answered, and the difference is a class effect not a level effect | `completeness_results.json` |
| how the new codes coexist with fiqh | answered for the Evidence Law; thin but replicated for the Civil Transactions Law | `codes_results.json` |
| what a legal AI would miss on statutes alone | answered as an estimate with its factors separated | `rag_gap_results.json` |
| dilution against displacement | answered on five denominators, and they disagree in a way that is itself the result | `codes_results.json` |
| does reasoning shape go with appellate fate | examined and declined: no association, and the slice is unrepresentative | `appellate_results.json` |

Two things this programme closed rather than opened. The alignment programme
stays closed at proposition level. And *silence* is closed as a research
object: it is a length, and length here is partly a publication decision.

## Second-paper decision, after the two-layer programme

Three candidates, scored on what a second paper actually needs.

| | A: institutional vs dispute-deciding law | B: code-specific authority ecologies | C: the traceability gap |
|---|---|---|---|
| novelty | high — no empirical partition of this kind exists for a recently codified Islamic-law jurisdiction, and the distinction it would replace is degenerate here (122 of 126 articles are "procedural") | high — nobody has profiled what appears *beside* each modern code | moderate to high — the measurement is new, the observation is not surprising to practitioners |
| effect strength | moderate: article-level medians 14.7 against 34.2 per cent, eta² 0.166, holds inside three statute books of five | **large**: hybrid supplementation runs from 4.1 per cent (Arbitration Law) to 59.4 (Law of Practice), a fourteen-fold spread on 30,000 judgments | clear but descriptive: 11.2 per cent of the bench's authority names no source, 40.1 per cent of its fiqh |
| data readiness | complete | complete | complete |
| legal importance | high — two thirds of citation-visible authority is machinery | high — it asks whether codification produced one legal culture or several | moderate — the strongest implications are for research and retrieval, not for doctrine |
| generalisability | the partition is defined against this corpus and would need redefining elsewhere | the *method* transfers to any jurisdiction with several modern codes | high |
| dependence on hand labels | **high** — and the independently assigned label set performs worse out of sample than the grand mean | **none** — every figure is a scan of the mention layer | none |
| decision | **HOLD** | **WRITE** | **HOLD** |

**A is held** for the reason its own explanatory-power table gives: instrument
identity beats it out of sample (MAE 15.32 against 16.02, against a 18.29
null), and a theory of provisions that loses to knowing which code the
provision is in is not ready to be a paper about provisions. It is ready to be
a section of one.

**B is the write**, and it is the answer to why A loses. If which code an
article belongs to predicts supplementation better than what the article does,
then the object worth explaining is the code. The Arbitration Law is applied
almost purely on its own terms; the Law of Practice is supplemented in three
judgments of five; the Civil Transactions Law is the only major code whose
maxim and custom rates approach its named-fiqh rate. That is a finding about
contemporary Saudi codification, it needs no hand label, and it is measured
over the whole window.

**C is held** as a section of B rather than a paper. On its own it is a
measurement in search of a legal question; inside B it is the answer to "what
would it take to study these ecologies from outside", and it belongs there.

No manuscript is drafted in this session.

## The capability ledger, after the two-layer programme

The ten questions the asset is meant to answer, and where each now stands:

| # | question | state | where |
|---|---|---|---|
| 1 | what law is visible in contemporary court reasoning | answered | `monitor_view.json`, the profile |
| 2 | which provisions run the court | answered for 126 provisions; ~64 % of the core | `article_function.csv`, `TWO_LAYERS.md` §4 |
| 3 | which provisions decide disputes | answered, same layer | `article_function.csv` |
| 4 | what do litigants cite | answered, and they cite *more* institutional law than the bench | `TWO_LAYERS.md` §5 |
| 5 | what does the court cite instead | answered: relatively more dispute-deciding law | `TWO_LAYERS.md` §5 |
| 6 | which modern codes attract which supplementary authorities | answered, and the spread is the strongest effect in the programme | `ecology_results.json` |
| 7 | is fiqh declining absolutely or only relatively | answered on five denominators: relatively | `monitor_view.json`, `COMPLETENESS.md` §8 |
| 8 | how much judicial authority is independently traceable | answered, as components | `TRACEABILITY.md` |
| 9 | what does statute-only legal AI miss | answered as coverage bounds | `TRACEABILITY.md` §1 |
| 10 | what changes when new judgments arrive | mechanism built, never yet run on a real second batch | `monitor.py --delta` |
