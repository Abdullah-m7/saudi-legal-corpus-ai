#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the GTPL (M/128) track: Arabic source, verified
records, LLM layer, and the English official-translation reference layer."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "gtpl", "law", "official_source",
                   "gtpl_m128_official_source.json")
REF = os.path.join(ROOT, "sources", "gtpl", "law", "reference_english",
                   "gtpl_m128_official_english_reference.json")
RECORDS = os.path.join(ROOT, "sources", "gtpl", "law", "verified",
                       "gtpl_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "gtpl_arabic_legal_llm", "gtpl_law_legal_llm_001_099.json")
STATUS = "MIRROR_TEXT_CROSS_CHECKED_AGAINST_OFFICIAL_MOF_PDF"


def main():
    e = []
    for p in (SRC, REF, RECORDS, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    ref = json.load(open(REF, encoding="utf-8"))
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    llm = json.load(open(LLM, encoding="utf-8"))

    # [1] source artifacts complete + mandatory legal anchors
    for name, art in (("ar", src["articles"]), ("en", ref["articles"])):
        if sorted(map(int, art)) != list(range(1, 100)):
            e.append("[1] %s articles not 1..99" % name)
        if any(not v.strip() for v in art.values()):
            e.append("[1] %s has empty article" % name)
    if "م/58" not in src["articles"]["98"]:
        e.append("[1] ar art 98 missing supersession of M/58")
    if "M/58" not in ref["articles"]["98"]:
        e.append("[1] en art 98 missing supersession of M/58")
    if re.search(r"[A-Za-z]", "".join(src["articles"].values())):
        e.append("[1] latin chars in Arabic articles")
    if ref.get("governing") is not False or ref.get("role") != "reference_guidance_only":
        e.append("[1] english reference layer must be non-governing reference only")

    # [2] verified records verbatim vs source
    if len(ver) != 99 or [r["article_number"] for r in ver] != list(range(1, 100)):
        e.append("[2] verified records not a 1..99 sequence")
    for r in ver:
        if r["article_text_verified"] != src["articles"][str(r["article_number"])]:
            e.append("[2] art %s: verified text != source" % r["article_number"])
        if r.get("official_text_status") != STATUS:
            e.append("[2] art %s: bad status" % r["article_number"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[2] art %s: %s must be False" % (r["article_number"], f))

    # [3] LLM layer verbatim + hashes + retrieval metadata
    recs = llm.get("records", [])
    if llm.get("record_count") != 99 or len(recs) != 99:
        e.append("[3] llm layer count != 99")
    for r in recs:
        n = r["article_number"]
        if r["article_text_ar"] != src["articles"][str(n)]:
            e.append("[3] art %s: llm text != source" % n)
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[3] art %s: hash mismatch" % n)
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[3] art %s: missing retrieval metadata" % n)
        if r.get("record_id") != "gtpl-law-llm-art-%03d" % n or \
           r.get("article_path") != "gtpl/law/articles/%03d" % n:
            e.append("[3] art %s: id/path wrong" % n)

    if e:
        print("FAIL: %d error(s) in GTPL track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: GTPL (M/128) track — 99 Arabic verified + 99 LLM-ready + 99 English reference articles")
    print("  - texts verbatim vs committed sources; Article 98 supersession anchors present (ar+en)")
    print("  - Arabic governs; English reference-only; no translation/paraphrase/interpretation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
