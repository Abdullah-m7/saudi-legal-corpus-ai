#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the GTPL Implementing Regulation track (157 articles)."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "gtpl", "regulation", "official_source",
                   "gtpl_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "gtpl", "regulation", "verified",
                       "gtpl_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "gtpl_arabic_legal_llm",
                   "gtpl_regulation_legal_llm_001_157.json")
STATUS = "REEXTRACTED_FROM_OFFICIAL_MOF_PDF_CROSS_CHECKED"
N = 157


def main():
    e = []
    for p in (SRC, RECORDS, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    if src.get("article_count") != N or sorted(map(int, arts)) != list(range(1, N + 1)):
        e.append("[1] source not a complete 1..%d set" % N)
    joined = "".join(arts.values())
    if re.search(r"[A-Za-z<>]|&nbsp", joined):
        e.append("[1] latin/HTML residue in source articles")
    if any(not v.strip() for v in arts.values()):
        e.append("[1] empty article in source")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N or [r["article_number"] for r in ver] != list(range(1, N + 1)):
        e.append("[2] verified records not 1..%d" % N)
    for r in ver:
        if r["article_text_verified"] != arts[str(r["article_number"])]:
            e.append("[2] art %s: text != source" % r["article_number"])
        if r.get("official_text_status") != STATUS:
            e.append("[2] art %s: bad status" % r["article_number"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[2] art %s: %s must be False" % (r["article_number"], f))

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[3] llm count != %d" % N)
    for r in recs:
        n = r["article_number"]
        if r["article_text_ar"] != arts[str(n)]:
            e.append("[3] art %s: llm text != source" % n)
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[3] art %s: hash mismatch" % n)
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[3] art %s: missing retrieval metadata" % n)
        if r.get("record_id") != "gtpl-reg-llm-art-%03d" % n or \
           r.get("article_path") != "gtpl/regulation/articles/%03d" % n:
            e.append("[3] art %s: id/path wrong" % n)

    if e:
        print("FAIL: %d error(s) in GTPL-regulation track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: GTPL Implementing Regulation track — %d Arabic verified + %d LLM-ready articles" % (N, N))
    print("  - texts verbatim vs committed source; hashes/ids/paths consistent; boundaries held")
    return 0


if __name__ == "__main__":
    sys.exit(main())
