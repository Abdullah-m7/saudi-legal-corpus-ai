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
