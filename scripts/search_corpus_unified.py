#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Keyword search over the unified Arabic LLM retrieval index (all laws at once).

Usage:
    python3 scripts/search_corpus_unified.py "تسرب البيانات الشخصية"
    python3 scripts/search_corpus_unified.py --top 5 --corpus pdpl "الموافقة"

Deterministic lexical scorer over the mechanical retrieval metadata each record
already carries (keywords / search_queries / titles / text).  Read-only; no
model, no network.  Arabic is the governing text.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "data", "corpus_unified_index", "corpus_unified_llm_index.jsonl")

FIELD_WEIGHTS = [
    ("keywords_ar", 4),
    ("search_queries_ar", 3),
    ("_title", 2),
    ("text_ar", 1),
]


def normalize(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"[ً-ْٰـ]", "", s)          # diacritics + tatweel
    for a, b in (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ى", "ي"),
                 ("ة", "ه"), ("ؤ", "و"), ("ئ", "ي")):
        s = s.replace(a, b)
    s = re.sub(r"[^ء-ي0-9\s]+", " ", s)
    return [w for w in s.split() if len(w) >= 2]


def _field_tokens(rec, field):
    if field == "_title":
        blob = (rec.get("llm_title_ar", "") + " " + rec.get("retrieval_title_ar", ""))
    else:
        v = rec.get(field, [])
        blob = " ".join(v) if isinstance(v, list) else str(v)
    return set(normalize(blob))


def load_index(path=INDEX):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


# The caveat layer, loaded once and joined onto every result.
#
# A search result is where this corpus is READ, and until now it returned the
# text with no indication that the record rests on one person's reading of a
# page image, or that its own track says a later amendment has been published,
# or that the «article» is a fee schedule. All of that was disclosed — in a
# source file nothing that reads the corpus opens. Answering with the caveat
# attached is the whole point of having written it.
_CAVEATS = None


def load_caveats(path=None):
    """{record_id: {material, provenance, summary_ar, ref}} — empty if absent."""
    global _CAVEATS
    if _CAVEATS is None:
        p = path or os.path.join(ROOT, "data", "corpus_caveat_layer",
                                 "corpus_caveat_layer.jsonl")
        rows = {}
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                for line in fh:
                    if line.strip():
                        r = json.loads(line)
                        rows[r["record_id"]] = r
        _CAVEATS = rows
    return _CAVEATS


def search(query, top=10, corpus=None, index=None):
    records = index if index is not None else load_index()
    qtokens = set(normalize(query))
    if not qtokens:
        return []
    results = []
    for rec in records:
        if corpus and rec.get("corpus") != corpus:
            continue
        field_sets = {f: _field_tokens(rec, f) for f, _ in FIELD_WEIGHTS}
        score = 0
        matched = set()
        for qt in qtokens:
            for field, w in FIELD_WEIGHTS:
                if qt in field_sets[field]:
                    score += w
                    matched.add(qt)
        if score > 0:
            results.append((score, len(matched), rec))
    # Rank by how many DISTINCT query tokens a record matched, and only then by the
    # weighted field score. The reverse order — weighted score first, coverage as a
    # tiebreak — let a record matching a handful of tokens in heavy fields beat one
    # containing the entire query in its body: «في» scores 3 in search_queries_ar
    # and 2 in the title, so a wildlife treaty matching 4 of a query's tokens (22)
    # outranked the e-litigation provision matching 16 of them (20), and a treaty
    # matching 11 outranked the Income Tax article matching 19.
    #
    # Measured over all 1,379 gold queries, swapping the two keys moves
    # top-1 89.1% -> 94.3%, top-3 96.4% -> 97.7%, top-5 97.7% -> 98.8% and
    # MRR@5 0.9263 -> 0.9607. Weighting each token by IDF as well was also measured
    # and adds nothing over this (94.3% / 0.9609), so the simpler change is the one
    # kept: the field weights still decide between records that cover the query
    # equally well, which is what they are good at.
    results.sort(key=lambda x: (-x[1], -x[0], x[2]["corpus"],
                                x[2]["law_component"], x[2]["article_number"]))
    out = []
    for score, ncov, rec in results[:top]:
        out.append({
            "score": score,
            "query_terms_matched": ncov,
            "record_id": rec["record_id"],
            "law_title_ar": rec["law_title_ar"],
            "law_component": rec["law_component"],
            "article_number": rec["article_number"],
            "unit_label_ar": rec.get("unit_label_ar"),
            "is_appendix": bool(rec.get("is_appendix")),
            "retrieval_title_ar": rec["retrieval_title_ar"],
            "article_path": rec["article_path"],
        })
    caveats = load_caveats()
    for row in out:
        c = caveats.get(row["record_id"])
        if not c:
            continue
        if c["caveats_material"]:
            row["caveats_material"] = c["caveats_material"]
            row["caveat_summary_ar"] = c["caveat_summary_ar"]
        if c["caveats_provenance"]:
            row["caveats_provenance"] = c["caveats_provenance"]
        row["disclosures_ref"] = c["disclosures_ref"]
    return out


def main():
    ap = argparse.ArgumentParser(description="Search the unified Arabic legal LLM index.")
    ap.add_argument("query", help="Arabic search query")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--corpus", default=None, help="filter: companies_law | pdpl | investment")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()

    hits = search(args.query, top=args.top, corpus=args.corpus)
    if args.json:
        print(json.dumps(hits, ensure_ascii=False, indent=2))
        return
    if not hits:
        print("لا نتائج.")
        return
    print("نتائج البحث عن: %s" % args.query)
    for i, h in enumerate(hits, 1):
        # The unit is printed as the SOURCE printed it. Rendering «مادة N» from the
        # positional integer would announce this corpus's 1,476 appendix/table/band
        # records as articles — a false citation invented by the display.
        unit = h.get("unit_label_ar") or "مادة %s" % h["article_number"]
        print("%2d. [%s] %s — %s  (score=%d)"
              % (i, h["law_title_ar"], h["law_component"], unit, h["score"]))
        print("    %s  |  %s" % (h["retrieval_title_ar"], h["article_path"]))


if __name__ == "__main__":
    sys.exit(main())
