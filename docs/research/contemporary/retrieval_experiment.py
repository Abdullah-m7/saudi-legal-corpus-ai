#!/usr/bin/env python3
"""One legal retrieval experiment, run four ways.

THE QUESTION. The corpus-properties paper says that preprocessing a published
judgment corpus changes what a legal AI system inherits. Two of its claims are
only testable inside a system:

  1. does removing recurring legal wording change retrieval performance BEYOND
     what removing the same amount of corpus material would do anyway?
  2. how much does the age of the indexed corpus change retrieval?

THE TASK. Given the court's own reasoning in the run-up to a statutory
citation, retrieve the article the court then cited. Nothing is synthetic:
the query is text a Saudi commercial court wrote, the label is the citation
that court then made, resolved by the same matcher every other pass here
uses, and relevance is never judged by us. One relevant article per query.

THE RETRIEVER. BM25 (k1=1.2, b=0.75) over one pseudo-document per article,
built by pooling the contexts in which earlier judgments cited that article.
A transparent lexical baseline is the right instrument for this question: the
independent variable is the CORPUS, so the retriever must be simple enough
that a change in the score can only have come from the corpus.

WHAT IS VARIED. Only the index. Every arm in a fold answers the SAME queries,
so arms are directly comparable:

  RAW                    every court-reasoning context from earlier quarters
  FORMULA_DEDUP          minus contexts sitting in a circulating formula
  MATCHED_RANDOM         minus the same NUMBER of contexts, chosen at random,
                         20 seeded draws
  FROZEN_kQ              the index cut back k quarters -- corpus ageing
  FROZEN_kQ_VOLUME       minus the same number of contexts freezing removed,
                         chosen at random -- ageing's own volume control
  PLUS_PARTY             court contexts plus the parties' own citation
                         contexts
  RAW_NO_FP_LEAK         RAW minus any context whose fingerprint also occurs
                         in a query this fold -- verbatim-overlap control

LEAKAGE. Handled at extraction (retrieval_layer.py masks every citation span
inside a query window and clips the window to its segment) and here: the
index holds only STRICTLY EARLIER quarters, so a query's own judgment can
never be indexed, and RAW_NO_FP_LEAK prices what verbatim recurrence is worth.

METRICS. Recall@1, @5, @10 and MRR@10, micro-averaged within a fold and then
averaged over folds. nDCG is not reported: with exactly one relevant document
per query it is a monotone transform of the reciprocal rank and would carry
no information MRR does not already carry. Index size and gold coverage are
reported beside every score, because an arm that shrinks the index is not
comparable on score alone.

    python3 retrieval_experiment.py
"""
import argparse
import gzip
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAYER = HERE / "retrieval_layer.jsonl.gz"
OUT = HERE / "retrieval_experiment_results.json"

K1, B = 1.2, 0.75
IDF_FLOOR = 0.01     # postings below this contribute < 1% of a typical term
QUERY_CAP = 1000     # queries per fold, sampled once and shared by every arm
SEED = 20260901
DRAWS_MATCHED = 20   # seeded draws for the headline matched-random control
DRAWS_FROZEN = 10    # seeded draws for the ageing volume controls
MIN_TRAIN = 4        # quarters of index history before a fold is scored
CIRCULATING = 10     # a formula circulates at >= this many distinct judgments
FREEZE = (1, 2, 4)
COURT = "court_reasoning"
PARTY = "party_argument"

# the maturity rule, fixed in horizon.py before any outcome was inspected and
# reused verbatim here so this experiment scores the same quarters as every
# other time-indexed result in the repository
SCORABLE = ["1443Q1", "1443Q3", "1443Q4", "1444Q1", "1444Q2", "1444Q3",
            "1444Q4", "1445Q1", "1445Q4", "1446Q1"]


def qnum(p):
    y, q = p.split("Q")
    return int(y) * 4 + int(q) - 1


def load():
    rows, schema = [], None
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r:
                schema = r["_schema"]
                continue
            r["t"] = (r["inst"], r["art"])
            r["qn"] = qnum(r["p"])
            rows.append(r)
    return rows, schema


class Index:
    """BM25 over one pseudo-document per article.

    Term weights are precomputed at build time, so scoring a query is a walk
    over postings. Postings whose idf falls below IDF_FLOOR are dropped: with
    N documents a term present in nearly all of them scores near zero, and
    keeping it costs the longest postings list in the index. The share of
    postings this drops is reported.
    """

    def __init__(self, rows):
        docs = defaultdict(Counter)
        for r in rows:
            docs[r["t"]].update(r["ctx"])
        self.targets = sorted(docs)
        self.pos = {t: i for i, t in enumerate(self.targets)}
        n = len(self.targets)
        lens = [sum(docs[t].values()) for t in self.targets]
        avg = (sum(lens) / n) if n else 1.0
        df = Counter()
        for t in self.targets:
            df.update(docs[t].keys())
        self.postings = {}
        kept = dropped = 0
        for term, d in df.items():
            idf = math.log(1 + (n - d + 0.5) / (d + 0.5))
            if idf < IDF_FLOOR:
                dropped += d
                continue
            kept += d
            ids, ws = [], []
            for t in self.targets:
                tf = docs[t].get(term)
                if not tf:
                    continue
                dl = lens[self.pos[t]]
                ids.append(self.pos[t])
                ws.append(idf * tf * (K1 + 1) /
                          (tf + K1 * (1 - B + B * dl / avg)))
            self.postings[term] = (ids, ws)
        self.n = n
        self.contexts = len(rows)
        self.postingsKept = kept
        self.postingsDropped = dropped

    def rank(self, query, gold, k=10):
        """-> rank of the gold target, 1-based, or None if outside the top k.

        Ties break on the target's stable position, so the ranking does not
        depend on dict ordering.
        """
        g = self.pos.get(gold)
        if g is None:
            return None
        acc = [0.0] * self.n
        hit = False
        for term, qf in query.items():
            p = self.postings.get(term)
            if not p:
                continue
            ids, ws = p
            for i, w in zip(ids, ws):
                acc[i] += qf * w
            hit = True
        if not hit:
            return None
        gs = acc[g]
        if gs <= 0.0:
            return None
        better = 0
        for i, s in enumerate(acc):
            if s > gs or (s == gs and i < g):
                better += 1
                if better >= k:
                    return None
        return better + 1


def score(index, queries):
    """Recall@1/5/10, MRR@10 and gold coverage over one query set."""
    r1 = r5 = r10 = 0
    mrr = 0.0
    covered = 0
    for q in queries:
        if q["t"] in index.pos:
            covered += 1
        rk = index.rank(q["ctx"], q["t"])
        if rk is None:
            continue
        if rk == 1:
            r1 += 1
        if rk <= 5:
            r5 += 1
        r10 += 1
        mrr += 1.0 / rk
    n = len(queries)
    return {"queries": n,
            "goldInIndex": round(covered / n, 4) if n else None,
            "recall@1": round(r1 / n, 4) if n else None,
            "recall@5": round(r5 / n, 4) if n else None,
            "recall@10": round(r10 / n, 4) if n else None,
            "mrr@10": round(mrr / n, 4) if n else None,
            "indexContexts": index.contexts, "indexArticles": index.n}


def circulating(rows):
    """Fingerprints occurring in CIRCULATING or more distinct judgments.

    Computed on the INDEX SIDE OF THIS FOLD ONLY. Reading recurrence off the
    whole corpus would let a fold see its own future, which is the mistake
    this repository has made before and now checks for.
    """
    seen = defaultdict(set)
    for r in rows:
        seen[r["fp"]].add(r["j"])
    return {fp for fp, js in seen.items() if len(js) >= CIRCULATING}


def drop_random(rows, k, seed):
    rng = random.Random(seed)
    keep = list(range(len(rows)))
    rng.shuffle(keep)
    keep = set(keep[k:])
    return [r for i, r in enumerate(rows) if i in keep]


def mean(vals):
    vals = [v for v in vals if v is not None]
    return round(sum(vals) / len(vals), 4) if vals else None


def summarise(folds, key):
    got = [f[key] for f in folds if key in f]
    if not got:
        return None
    out = {}
    for m in ("recall@1", "recall@5", "recall@10", "mrr@10", "goldInIndex"):
        out[m] = mean([g[m] for g in got])
    out["meanIndexContexts"] = round(mean([g["indexContexts"] for g in got]))
    out["meanIndexArticles"] = round(mean([g["indexArticles"] for g in got]))
    out["folds"] = len(got)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folds", type=int, default=0,
                    help="score only the first N folds (development runs)")
    args = ap.parse_args()

    rows, schema = load()
    by_q = defaultdict(list)
    for r in rows:
        by_q[r["qn"]].append(r)
    first = min(by_q)

    folds = []
    for label in SCORABLE:
        t = qnum(label)
        if t - first < MIN_TRAIN:
            continue
        queries = [r for r in rows if r["qn"] == t and r["voice"] == COURT]
        if not queries:
            continue
        queries.sort(key=lambda r: (r["j"], r["inst"], r["art"]))
        if len(queries) > QUERY_CAP:
            random.Random(SEED + t).shuffle(queries)
            queries = queries[:QUERY_CAP]
            queries.sort(key=lambda r: (r["j"], r["inst"], r["art"]))
        court = [r for r in rows if r["qn"] < t and r["voice"] == COURT]
        if not court:
            continue

        fold = {"quarter": label, "queryQuarters": 1,
                "queriesAvailable": sum(1 for r in rows if r["qn"] == t
                                        and r["voice"] == COURT),
                "queriesScored": len(queries)}

        raw = Index(court)
        fold["RAW"] = score(raw, queries)
        fold["postingsDroppedShare"] = round(
            raw.postingsDropped / (raw.postingsKept + raw.postingsDropped), 4)

        circ = circulating(court)
        dedup = [r for r in court if r["fp"] not in circ]
        removed = len(court) - len(dedup)
        fold["circulatingFormulas"] = len(circ)
        fold["contextsRemovedByDedup"] = removed
        fold["dedupRemovedShare"] = round(removed / len(court), 4)
        fold["FORMULA_DEDUP"] = score(Index(dedup), queries)

        draws = []
        for d in range(DRAWS_MATCHED):
            draws.append(score(Index(drop_random(court, removed, SEED + t + d)),
                               queries))
        fold["MATCHED_RANDOM"] = {
            "draws": DRAWS_MATCHED,
            **{m: mean([x[m] for x in draws])
               for m in ("recall@1", "recall@5", "recall@10", "mrr@10",
                         "goldInIndex")},
            "mrr@10_min": min(x["mrr@10"] for x in draws),
            "mrr@10_max": max(x["mrr@10"] for x in draws),
            "indexContexts": draws[0]["indexContexts"],
            "indexArticles": round(mean([x["indexArticles"] for x in draws])),
        }
        # is the dedup result inside the random control's own spread?
        fold["dedupInsideMatchedRandomRange"] = bool(
            min(x["mrr@10"] for x in draws)
            <= fold["FORMULA_DEDUP"]["mrr@10"]
            <= max(x["mrr@10"] for x in draws))
        fold["dedupRankAmongDraws"] = sum(
            1 for x in draws if x["mrr@10"] < fold["FORMULA_DEDUP"]["mrr@10"])

        for k in FREEZE:
            frozen = [r for r in court if r["qn"] < t - k]
            if not frozen:
                continue
            fold[f"FROZEN_{k}Q"] = score(Index(frozen), queries)
            gone = len(court) - len(frozen)
            fold[f"contextsRemovedByFreeze_{k}Q"] = gone
            vc = [score(Index(drop_random(court, gone, SEED + t + k * 97 + d)),
                        queries) for d in range(DRAWS_FROZEN)]
            fold[f"FROZEN_{k}Q_VOLUME"] = {
                "draws": DRAWS_FROZEN,
                **{m: mean([x[m] for x in vc])
                   for m in ("recall@1", "recall@5", "recall@10", "mrr@10",
                             "goldInIndex")},
                "mrr@10_min": min(x["mrr@10"] for x in vc),
                "mrr@10_max": max(x["mrr@10"] for x in vc),
                "indexContexts": vc[0]["indexContexts"],
                "indexArticles": round(mean([x["indexArticles"] for x in vc])),
            }

        party = [r for r in rows if r["qn"] < t and r["voice"] == PARTY]
        fold["PLUS_PARTY"] = score(Index(court + party), queries)

        qfp = {r["fp"] for r in queries}
        clean = [r for r in court if r["fp"] not in qfp]
        fold["contextsSharingAQueryFingerprint"] = len(court) - len(clean)
        fold["RAW_NO_FP_LEAK"] = score(Index(clean), queries)

        folds.append(fold)
        print(f"  {label}  RAW mrr {fold['RAW']['mrr@10']}  "
              f"dedup {fold['FORMULA_DEDUP']['mrr@10']}  "
              f"random {fold['MATCHED_RANDOM']['mrr@10']}", flush=True)
        if args.folds and len(folds) >= args.folds:
            break

    arms = ["RAW", "FORMULA_DEDUP", "MATCHED_RANDOM", "PLUS_PARTY",
            "RAW_NO_FP_LEAK"] + [f"FROZEN_{k}Q" for k in FREEZE] + \
        [f"FROZEN_{k}Q_VOLUME" for k in FREEZE]
    summary = {a: summarise(folds, a) for a in arms}

    d_raw = summary["RAW"]["mrr@10"] - summary["FORMULA_DEDUP"]["mrr@10"]
    d_rnd = summary["RAW"]["mrr@10"] - summary["MATCHED_RANDOM"]["mrr@10"]
    # the test is not a comparison of two means. Each fold has its own
    # distribution of 20 size-matched random draws, and the question is
    # whether the targeted removal lands outside it. A targeted removal that
    # sits inside the spread has not been shown to do anything a random
    # removal of the same size would not have done.
    # a fold where de-boilerplating removed nothing cannot discriminate
    # between the two hypotheses and is excluded from the verdict rather than
    # counted as agreement
    live = [f for f in folds if f["contextsRemovedByDedup"] > 0]
    inside = sum(1 for f in live if f["dedupInsideMatchedRandomRange"])
    verdict = ("DEDUP_EFFECT_EXCEEDS_VOLUME_EFFECT"
               if live and inside <= len(live) / 2
               else "DEDUP_EFFECT_WITHIN_VOLUME_EFFECT")

    results = {
        "what": "LEGAL RETRIEVAL UNDER FOUR CORPUS TREATMENTS. Does removing "
                "recurring legal wording change retrieval beyond what "
                "removing the same volume does, and how much does index age "
                "cost?",
        "task": {
            "query": "the court's own reasoning in the 600 characters before "
                     "a statutory citation, every citation span inside it "
                     "masked",
            "gold": "the (instrument, article) the court then cited, resolved "
                    "by match_instruments",
            "relevantPerQuery": 1,
            "notSynthetic": "no question is written by us and no relevance "
                            "judgement is made by us",
            "retriever": f"BM25, k1={K1}, b={B}, one pseudo-document per "
                         "article pooled from earlier citation contexts",
            "tokenisation": "companions.norm, words of 3+ characters, hashed; "
                            "no stemming and no stop-word list beyond length",
            "metricsNote": "nDCG is omitted deliberately: with one relevant "
                           "document per query it is a monotone transform of "
                           "the reciprocal rank.",
        },
        "leakageControls": [
            "the query window ends where the citation begins, so the answer "
            "is never inside its own query",
            "every statutory citation span inside a query window is masked, "
            "so a second citation of the same article nearby cannot leak it "
            "and the instrument's name cannot either",
            "the window is clipped to its segment: a citation in the reasons "
            "never reads the recital",
            "temporal split -- the index holds strictly earlier quarters, so "
            "a query's own judgment is never in the index",
            "circulating formulas are recomputed on each fold's own index, "
            "never on the whole corpus",
            "RAW_NO_FP_LEAK prices what verbatim fingerprint overlap between "
            "index and queries is worth",
        ],
        "design": {
            "folds": len(folds), "quartersScored": [f["quarter"] for f in folds],
            "maturityRule": "horizon.py's SCORABLE quarters, unchanged",
            "queryCap": QUERY_CAP, "seed": SEED,
            "drawsMatchedRandom": DRAWS_MATCHED,
            "drawsFrozenVolume": DRAWS_FROZEN,
            "circulatingThreshold": CIRCULATING,
            "queriesAreIdenticalAcrossArms": True,
        },
        "summary": summary,
        "headline": {
            "rawMinusDedup_mrr": round(d_raw, 4),
            "rawMinusMatchedRandom_mrr": round(d_rnd, 4),
            "foldsWhereDedupSitsInsideTheRandomSpread": inside,
            "foldsWhereDedupRemovedSomething": len(live),
            "foldsTotal": len(folds),
            "meanDrawsBeatenByDedup": mean(
                [f["dedupRankAmongDraws"] for f in live]),
            "drawsPerFold": DRAWS_MATCHED,
            "verdict": verdict,
        },
        "ageing": {
            f"FROZEN_{k}Q": {
                "mrrLossVersusRaw": round(
                    summary["RAW"]["mrr@10"] - summary[f"FROZEN_{k}Q"]["mrr@10"], 4),
                "mrrLossOfItsVolumeControl": round(
                    summary["RAW"]["mrr@10"]
                    - summary[f"FROZEN_{k}Q_VOLUME"]["mrr@10"], 4),
            } for k in FREEZE if summary.get(f"FROZEN_{k}Q")
        },
        "byFold": folds,
        "layerSchema": schema,
    }
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(json.dumps(results["headline"], indent=1))
    print(json.dumps(results["ageing"], indent=1))
    print(f"-> {OUT.name}")


if __name__ == "__main__":
    main()
