#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run the retrieval evaluation pack against the unified LLM index.

Executes every gold query in ``corpus_retrieval_eval_queries.json`` through the
deterministic lexical searcher (``search_corpus_unified.search``), scores where
the gold article lands (top-1 / top-3 / top-5 accuracy + mean reciprocal rank),
and writes the full per-query results to
``data/corpus_retrieval_eval/corpus_retrieval_eval_results.json``.

The gold answers were confirmed manually against the articles' own texts (see
the queries file), NOT reverse-engineered from search output — so the metrics
honestly measure the searcher, and per-query misses are reported as misses.

Deterministic and idempotent (same index + same queries -> same results file).
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUERIES = os.path.join(ROOT, "data", "corpus_retrieval_eval",
                       "corpus_retrieval_eval_queries.json")
RESULTS = os.path.join(ROOT, "data", "corpus_retrieval_eval",
                       "corpus_retrieval_eval_results.json")

sys.path.insert(0, os.path.join(ROOT, "scripts"))
from search_corpus_unified import load_index, search  # noqa: E402

TOP_K = 5


def run_eval(index=None):
    """Return (per_query_results, metrics). Pure over inputs."""
    pack = json.load(open(QUERIES, encoding="utf-8"))
    index = index if index is not None else load_index()
    by_id = {r["record_id"]: r for r in index}

    per_query = []
    ranks = []
    for q in pack["queries"]:
        gold = q["gold"]
        hits = search(q["query_ar"], top=TOP_K, index=index)
        rank = None
        for i, h in enumerate(hits, 1):
            rec = by_id.get(h["record_id"], {})
            if (rec.get("corpus") == gold["corpus"]
                    and rec.get("law_component") == gold["law_component"]
                    and h["article_number"] == gold["article_number"]):
                rank = i
                break
        ranks.append(rank)
        per_query.append({
            "query_id": q["query_id"],
            "query_ar": q["query_ar"],
            "category": q["category"],
            "gold": gold,
            "gold_rank": rank,
            "hit_top1": rank == 1,
            "hit_top3": rank is not None and rank <= 3,
            "hit_top5": rank is not None and rank <= 5,
            "top_hits": [
                {"record_id": h["record_id"], "article_number": h["article_number"],
                 "score": h["score"]}
                for h in hits[:3]
            ],
        })

    n = len(per_query)
    metrics = {
        "total_queries": n,
        "top1_hits": sum(1 for r in ranks if r == 1),
        "top3_hits": sum(1 for r in ranks if r is not None and r <= 3),
        "top5_hits": sum(1 for r in ranks if r is not None and r <= 5),
        "top1_accuracy": round(sum(1 for r in ranks if r == 1) / n, 4),
        "top3_accuracy": round(sum(1 for r in ranks if r is not None and r <= 3) / n, 4),
        "top5_accuracy": round(sum(1 for r in ranks if r is not None and r <= 5) / n, 4),
        "mrr_at_5": round(sum((1.0 / r) for r in ranks if r is not None) / n, 4),
        "misses_top5": [pq["query_id"] for pq in per_query if not pq["hit_top5"]],
    }
    return per_query, metrics


def main():
    per_query, metrics = run_eval()
    out = {
        "eval_id": "corpus-unified-retrieval-eval-v1",
        "index_path": "data/corpus_unified_index/corpus_unified_llm_index.jsonl",
        "queries_path": "data/corpus_retrieval_eval/corpus_retrieval_eval_queries.json",
        "top_k": TOP_K,
        "metrics": metrics,
        "per_query": per_query,
    }
    os.makedirs(os.path.dirname(RESULTS), exist_ok=True)
    with open(RESULTS, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("Retrieval eval over %d queries:" % metrics["total_queries"])
    print("  top-1 accuracy: %.1f%% (%d/%d)" % (metrics["top1_accuracy"] * 100,
                                                metrics["top1_hits"], metrics["total_queries"]))
    print("  top-3 accuracy: %.1f%% (%d/%d)" % (metrics["top3_accuracy"] * 100,
                                                metrics["top3_hits"], metrics["total_queries"]))
    print("  top-5 accuracy: %.1f%% (%d/%d)" % (metrics["top5_accuracy"] * 100,
                                                metrics["top5_hits"], metrics["total_queries"]))
    print("  MRR@5: %.4f" % metrics["mrr_at_5"])
    if metrics["misses_top5"]:
        print("  misses (gold not in top-5): %s" % ", ".join(metrics["misses_top5"]))
    print("Wrote %s" % os.path.relpath(RESULTS, ROOT))


if __name__ == "__main__":
    main()
