#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a single unified retrieval index over every Arabic LLM-ready layer.

Normalizes the per-law enrichment layers — Companies Law, PDPL (law +
implementing regulation), and the Investment Law (law + implementing
regulations) — into one flat JSONL index of retrieval records sharing a common
schema, so a single search can query the whole corpus.

Each source layer already carries mechanical retrieval metadata (llm_title /
retrieval_title / article_path / keywords / search_queries).  This generator only
projects those fields into a common shape and stamps the owning law's friendly
Arabic title and corpus key.  It does not alter, summarize, translate, or
re-derive any legal text.  Arabic governs.

Read-only over its inputs; deterministic and idempotent over its output.
"""

from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "corpus_unified_index")
INDEX = os.path.join(OUT_DIR, "corpus_unified_llm_index.jsonl")
SUMMARY = os.path.join(OUT_DIR, "corpus_unified_llm_index_summary.json")

# (relative layer file, corpus key, default law_component when a record omits it)
LAYERS = [
    ("data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json",
     "companies_law", "law"),
    ("data/pdpl_arabic_legal_llm/pdpl_arabic_law_legal_llm_001_043.json",
     "pdpl", "law"),
    ("data/pdpl_arabic_legal_llm/pdpl_implementing_regulation_arabic_legal_llm_001_038.json",
     "pdpl", "implementing_regulation"),
    ("data/investment_arabic_legal_llm/investment_law_legal_llm_001_016.json",
     "investment", "law"),
    ("data/investment_arabic_legal_llm/investment_regulation_legal_llm_001_037.json",
     "investment", "implementing_regulation"),
    ("data/civil_arabic_legal_llm/civil_transactions_law_legal_llm_001_721.json",
     "civil", "law"),
    ("data/gtpl_arabic_legal_llm/gtpl_law_legal_llm_001_099.json",
     "gtpl", "law"),
    ("data/gtpl_arabic_legal_llm/gtpl_regulation_legal_llm_001_157.json",
     "gtpl", "implementing_regulation"),
    ("data/labor_arabic_legal_llm/labor_law_legal_llm_001_245.json",
     "labor", "law"),
    ("data/labor_arabic_legal_llm/labor_regulation_legal_llm_001_040.json",
     "labor", "implementing_regulation"),
]


def _law_title(envelope):
    # envelope title_ar is like "نظام الشركات — الطبقة العربية ..." -> take the part before the em dash
    t = envelope.get("title_ar", "")
    return t.split(" — ", 1)[0].strip() if " — " in t else t.strip()


def _text_of(rec):
    return rec.get("article_text_ar") or rec.get("official_text_ar") or ""


def _status_of(rec):
    return (rec.get("text_status")
            or rec.get("source_trust", {}).get("source_status")
            or rec.get("record_type")
            or "unspecified")


def build():
    rows = []
    counts = {}
    for rel, corpus, default_component in LAYERS:
        env = json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))
        recs = env["records"] if isinstance(env, dict) and "records" in env else env
        law_title = _law_title(env) if isinstance(env, dict) else corpus
        n = 0
        for r in recs:
            rows.append({
                "record_id": r["record_id"],
                "corpus": corpus,
                "law_id": r.get("law_id"),
                "law_component": r.get("law_component", default_component),
                "law_title_ar": law_title,
                "article_number": r["article_number"],
                "llm_title_ar": r.get("llm_title_ar"),
                "retrieval_title_ar": r.get("retrieval_title_ar"),
                "article_path": r.get("article_path"),
                "keywords_ar": r.get("keywords_ar", []),
                "search_queries_ar": r.get("search_queries_ar", []),
                "text_ar": _text_of(r),
                "text_status": _status_of(r),
                "source_layer": os.path.basename(rel),
            })
            n += 1
        counts[os.path.basename(rel)] = n

    # stable order: corpus, law_component (law before regulation), article_number
    comp_rank = {"law": 0, "implementing_regulation": 1}
    rows.sort(key=lambda x: (x["corpus"], comp_rank.get(x["law_component"], 9), x["article_number"]))
    return rows, counts


def main():
    rows, counts = build()
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(INDEX, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    by_corpus = {}
    for r in rows:
        by_corpus[r["corpus"]] = by_corpus.get(r["corpus"], 0) + 1
    summary = {
        "index": "CORPUS_UNIFIED_LLM_RETRIEVAL_INDEX",
        "total_records": len(rows),
        "records_per_layer": counts,
        "records_per_corpus": by_corpus,
        "layers": [os.path.basename(rel) for rel, _, _ in LAYERS],
        "fields": ["record_id", "corpus", "law_id", "law_component", "law_title_ar",
                   "article_number", "llm_title_ar", "retrieval_title_ar", "article_path",
                   "keywords_ar", "search_queries_ar", "text_ar", "text_status", "source_layer"],
        "note": ("Flat retrieval index projected from the per-law LLM-ready enrichment layers. "
                 "No legal text altered, summarized, translated, or re-derived. Arabic governs."),
    }
    with open(SUMMARY, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("Wrote unified index: %d records -> %s" % (len(rows), os.path.relpath(INDEX, ROOT)))
    for k, v in sorted(by_corpus.items()):
        print("  %-14s %d" % (k, v))


if __name__ == "__main__":
    main()
