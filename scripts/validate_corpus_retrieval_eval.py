#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the unified-index retrieval evaluation pack.

Checks:
  * the queries file is well-formed (unique ids, valid golds that exist in the
    unified index);
  * the committed results file exactly reproduces a fresh in-memory run of the
    eval (deterministic reproducibility);
  * quality floors hold (top-1 / top-3 accuracy and MRR@5) — floors are set
    below the currently-achieved metrics so legitimate small changes pass while
    real regressions fail.

Exit 0 = PASS, 1 = FAIL.
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
from search_corpus_unified import load_index  # noqa: E402
from run_corpus_retrieval_eval import run_eval  # noqa: E402

EXPECTED_QUERIES = 272
FLOOR_TOP1 = 0.75
FLOOR_TOP3 = 0.85
FLOOR_MRR = 0.80


def main():
    errors = []
    for p in (QUERIES, RESULTS):
        if not os.path.isfile(p):
            print("FAIL: missing file: %s" % os.path.relpath(p, ROOT))
            return 1

    pack = json.load(open(QUERIES, encoding="utf-8"))
    queries = pack.get("queries", [])

    # [1] queries well-formed
    if len(queries) != EXPECTED_QUERIES:
        errors.append("[1] expected %d queries, found %d" % (EXPECTED_QUERIES, len(queries)))
    ids = [q.get("query_id") for q in queries]
    if len(set(ids)) != len(ids):
        errors.append("[1] duplicate query_ids")
    for q in queries:
        if not q.get("query_ar", "").strip():
            errors.append("[1] %s: empty query_ar" % q.get("query_id"))
        g = q.get("gold", {})
        for k in ("corpus", "law_component", "article_number"):
            if k not in g:
                errors.append("[1] %s: gold missing %r" % (q.get("query_id"), k))

    # [2] every gold exists in the unified index
    index = load_index()
    keys = {(r["corpus"], r["law_component"], r["article_number"]) for r in index}
    for q in queries:
        g = q["gold"]
        if (g["corpus"], g["law_component"], g["article_number"]) not in keys:
            errors.append("[2] %s: gold not found in unified index: %s" % (q["query_id"], g))

    # [3] committed results exactly reproduce a fresh run
    stored = json.load(open(RESULTS, encoding="utf-8"))
    per_query, metrics = run_eval(index=index)
    if stored.get("metrics") != metrics:
        errors.append("[3] stored metrics differ from fresh run: stored=%s fresh=%s"
                      % (stored.get("metrics"), metrics))
    if stored.get("per_query") != per_query:
        diff = [a.get("query_id") for a, b in zip(stored.get("per_query", []), per_query) if a != b]
        errors.append("[3] stored per-query results differ from fresh run (e.g. %s)" % diff[:5])

    # [4] quality floors
    if metrics["top1_accuracy"] < FLOOR_TOP1:
        errors.append("[4] top-1 accuracy %.3f below floor %.2f" % (metrics["top1_accuracy"], FLOOR_TOP1))
    if metrics["top3_accuracy"] < FLOOR_TOP3:
        errors.append("[4] top-3 accuracy %.3f below floor %.2f" % (metrics["top3_accuracy"], FLOOR_TOP3))
    if metrics["mrr_at_5"] < FLOOR_MRR:
        errors.append("[4] MRR@5 %.3f below floor %.2f" % (metrics["mrr_at_5"], FLOOR_MRR))

    if errors:
        print("FAIL: %d error(s) in retrieval eval pack:" % len(errors))
        for e in errors[:15]:
            print("  - %s" % e)
        return 1

    print("PASS: retrieval eval pack (%d gold queries over the unified index)" % len(queries))
    print("  - top-1 %.1f%% / top-3 %.1f%% / top-5 %.1f%% / MRR@5 %.4f (floors %d%%/%d%%/%.2f)"
          % (metrics["top1_accuracy"] * 100, metrics["top3_accuracy"] * 100,
             metrics["top5_accuracy"] * 100, metrics["mrr_at_5"],
             FLOOR_TOP1 * 100, FLOOR_TOP3 * 100, FLOOR_MRR))
    print("  - committed results reproduce a fresh deterministic run exactly")
    if metrics["misses_top5"]:
        print("  - known documented misses: %s" % ", ".join(metrics["misses_top5"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
