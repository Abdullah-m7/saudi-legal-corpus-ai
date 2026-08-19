#!/usr/bin/env python3
"""BM25 baseline for the corpus retrieval evaluation pack.

Standard Okapi BM25 (k1=1.5, b=0.75) over each unified-index record's
searchable text (law title + article title + verbatim article text), with
light Arabic orthographic normalization (diacritics/tatweel stripped, alef
and teh-marbuta variants folded). Whitespace tokenization — no stemming, no
stopword list, no learned parameters — so the comparison against the
repository's metadata-based lexical searcher is a fair, standard reference
point.

Deterministic: same index + same queries -> same results file. Run from the
repository root:

    python3 docs/research/corpus_paper/bm25_baseline.py

Writes bm25_baseline_results.json next to this script (metrics overall and
per query category; per-query ranks included for error analysis).
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
INDEX = REPO_ROOT / "data" / "corpus_unified_index" / "corpus_unified_llm_index.jsonl"
QUERIES = (
    REPO_ROOT / "data" / "corpus_retrieval_eval" / "corpus_retrieval_eval_queries.json"
)
OUT = Path(__file__).resolve().parent / "bm25_baseline_results.json"

K1 = 1.5
B = 0.75
TOP_K = 5

DIACRITICS = re.compile(r"[ً-ْٰـ]")  # harakat, dagger alef, tatweel


def normalize(text):
    text = DIACRITICS.sub("", text)
    text = (
        text.replace("أ", "ا")
        .replace("إ", "ا")
        .replace("آ", "ا")
        .replace("ة", "ه")
        .replace("ى", "ي")
    )
    return text


def tokenize(text):
    return normalize(text).split()


def load_records():
    records = []
    with open(INDEX, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            searchable = " ".join(
                [r.get("law_title_ar") or "", r.get("llm_title_ar") or "",
                 r.get("text_ar") or ""]
            )
            records.append(
                {
                    "corpus": r["corpus"],
                    "law_component": r["law_component"],
                    "article_number": r["article_number"],
                    "tokens": tokenize(searchable),
                }
            )
    return records


def build_bm25(records):
    df = Counter()
    doc_tfs = []
    total_len = 0
    for rec in records:
        tf = Counter(rec["tokens"])
        doc_tfs.append(tf)
        total_len += len(rec["tokens"])
        for term in tf:
            df[term] += 1
    n = len(records)
    avgdl = total_len / n
    idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}

    # Inverted postings: term -> list of (doc_index, tf) for scoring speed.
    postings = defaultdict(list)
    for i, tf in enumerate(doc_tfs):
        for term, count in tf.items():
            postings[term].append((i, count))

    doc_lens = [len(rec["tokens"]) for rec in records]

    def score_query(query_tokens):
        scores = defaultdict(float)
        for term in query_tokens:
            if term not in postings:
                continue
            term_idf = idf[term]
            for i, tf in postings[term]:
                denom = tf + K1 * (1 - B + B * doc_lens[i] / avgdl)
                scores[i] += term_idf * tf * (K1 + 1) / denom
        return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))[:TOP_K]

    return score_query


def main():
    records = load_records()
    score_query = build_bm25(records)
    pack = json.load(open(QUERIES, encoding="utf-8"))

    per_query = []
    for q in pack["queries"]:
        gold = q["gold"]
        hits = score_query(tokenize(q["query_ar"]))
        rank = None
        for pos, (i, _score) in enumerate(hits, 1):
            rec = records[i]
            if (
                rec["corpus"] == gold["corpus"]
                and rec["law_component"] == gold["law_component"]
                and rec["article_number"] == gold["article_number"]
            ):
                rank = pos
                break
        per_query.append(
            {"query_id": q["query_id"], "category": q["category"], "gold_rank": rank}
        )

    def metrics(rows):
        n = len(rows)
        ranks = [r["gold_rank"] for r in rows]
        return {
            "n": n,
            "top1_accuracy": round(sum(1 for r in ranks if r == 1) / n, 4),
            "top3_accuracy": round(
                sum(1 for r in ranks if r is not None and r <= 3) / n, 4
            ),
            "top5_accuracy": round(
                sum(1 for r in ranks if r is not None and r <= 5) / n, 4
            ),
            "mrr_at_5": round(
                sum(1.0 / r for r in ranks if r is not None) / n, 4
            ),
        }

    by_cat = defaultdict(list)
    for row in per_query:
        by_cat[row["category"]].append(row)

    out = {
        "baseline": "okapi_bm25",
        "params": {"k1": K1, "b": B, "top_k": TOP_K},
        "fields": "law_title_ar + llm_title_ar + text_ar (normalized, whitespace tokens)",
        "index_path": str(INDEX.relative_to(REPO_ROOT)),
        "queries_path": str(QUERIES.relative_to(REPO_ROOT)),
        "metrics_overall": metrics(per_query),
        "metrics_by_category": {
            c: metrics(rows)
            for c, rows in sorted(by_cat.items(), key=lambda kv: -len(kv[1]))
        },
        "per_query": per_query,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(json.dumps({k: out[k] for k in ["metrics_overall", "metrics_by_category"]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
