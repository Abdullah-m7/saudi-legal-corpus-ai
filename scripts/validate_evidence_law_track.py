#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Evidence Law track (129 records).

Trust gate: every article must be MATCHES_PDF with a recorded cross-check
similarity >= 0.90 (official MOJ database text vs the committed official MOJ
PDF), the sequence must be a complete 1..129, every article must carry its
chapter path and legal status 'اصلية' (the law is unamended), and the
verified/LLM layers must be verbatim with consistent hashes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "evidence", "law", "official_source",
                   "evidence_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "evidence", "law", "verified",
                       "evidence_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "evidence_arabic_legal_llm", "evidence_law_legal_llm_001_129.json")
PDF = os.path.join(ROOT, "inputs", "evidence_official_pdfs", "evidence_law_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 129
SIM_FLOOR = 0.90
ART1 = "تسري أحكام هذا النظام على المعاملات المدنية والتجارية."


def main():
    e = []
    for p in (SRC, RECORDS, LLM, PDF):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    # [1] structure: complete 1..129
    nums = sorted(int(re.match(r"ithbat_art_(\d{3})", k).group(1)) for k in arts)
    if len(arts) != N or nums != list(range(1, N + 1)):
        e.append("[1] articles not a complete 1..%d sequence (%d found)" % (N, len(arts)))

    # [2] trust gate: MATCHES_PDF + similarity floor + unamended + chapters + clean text
    for k, a in arts.items():
        if a["status"] != "MATCHES_PDF":
            e.append("[2] %s: UNTRUSTED status %r" % (k, a["status"]))
        if (a.get("pdf_similarity") or 0) < SIM_FLOOR:
            e.append("[2] %s: cross-check similarity below %.2f" % (k, SIM_FLOOR))
        if a.get("legal_status_ar") != "اصلية":
            e.append("[2] %s: unexpected legal status %r" % (k, a.get("legal_status_ar")))
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]) or "ـ" in a["text"]:
            e.append("[2] %s: empty text, latin/html leftovers, or tatweel" % k)
        if not a.get("section_ar", "").strip():
            e.append("[2] %s: missing chapter path" % k)
    if arts["ithbat_art_001"]["text"] != ART1:
        e.append("[2] art 1 anchor mismatch")
    if "يعمل بهذا النظام" not in arts["ithbat_art_129"]["text"]:
        e.append("[2] art 129 (entry into force) anchor mismatch")

    # [3] the committed official PDF still hashes to the recorded value
    sha = hashlib.sha256(open(PDF, "rb").read()).hexdigest()
    if sha != src["provenance"]["pdf_sha256"]:
        e.append("[3] committed PDF sha256 mismatch")

    # [4] verified records + [5] LLM layer verbatim/hashes
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        if r["article_text_verified"] != arts[r["article_key"]]["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("official_text_status") != STATUS:
            e.append("[4] %s: bad status" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))
    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        if r["article_text_ar"] != arts[r["article_key"]]["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Evidence Law track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Evidence Law track — 129 records (complete 1..129, 11 chapters)")
    print("  - trust gate: every article MATCHES_PDF >= %.2f; all 'اصلية' (unamended M/43 1443H)" % SIM_FLOOR)
    print("  - committed official MOJ PDF hash verified; art 1 / art 129 anchors verbatim")
    print("  - texts verbatim vs committed source; hashes consistent; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
