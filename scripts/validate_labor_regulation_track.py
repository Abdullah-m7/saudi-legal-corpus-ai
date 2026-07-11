#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Labor Law Implementing Regulation track (45 records).

Trust gate: every record must be ACTIVE or DELETED (nothing unexplained), the
recorded OCR similarities must clear the floor, and every implements_law_articles
link must point at an existing, non-deleted article of the verified Labor Law
track — re-checking the cross-law linkage against committed data."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "labor", "regulation", "official_source",
                   "labor_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "labor", "regulation", "verified",
                       "labor_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "labor_arabic_legal_llm", "labor_regulation_legal_llm_001_040.json")
LAW_RECORDS = os.path.join(ROOT, "sources", "labor", "law", "verified",
                           "labor_law_verified_records.jsonl")
STATUS = "HRSD_OFFICIAL_PDF_OCR_CROSS_CHECKED_LAW_QUOTES"
ALLOWED = {"ACTIVE", "DELETED"}
N = 45
DELETED_NUMBERS = [2, 36, 37]
MUKARRAR_KEYS = ["labor_reg_art_004_mukarrar", "labor_reg_art_015_mukarrar",
                 "labor_reg_art_016_mukarrar_1", "labor_reg_art_016_mukarrar_2",
                 "labor_reg_art_022_mukarrar"]
ART1_ANCHOR = "في تنفيذ أحكام (المادة السادسة) من النظام"
OCR_FLOOR = 0.85
QUOTE_FLOOR = 0.85


def main():
    e = []
    for p in (SRC, RECORDS, LLM, LAW_RECORDS):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    # [1] structure: 45 keys = base 1..40 exactly once + the 5 known mukarrar
    if len(arts) != N:
        e.append("[1] source has %d articles, expected %d" % (len(arts), N))
    base = sorted(int(re.match(r"labor_reg_art_(\d{3})", k).group(1))
                  for k in arts if "_mukarrar" not in k)
    if base != list(range(1, 41)):
        e.append("[1] base articles not a complete 1..40 sequence")
    muk = sorted(k for k in arts if "_mukarrar" in k)
    if muk != sorted(MUKARRAR_KEYS):
        e.append("[1] mukarrar keys mismatch: %s" % muk)

    # [2] trust gate: only explained statuses; anchors; no latin; OCR floor
    for k, a in arts.items():
        if a["status"] not in ALLOWED:
            e.append("[2] %s: UNTRUSTED status %r" % (k, a["status"]))
        if not a["text"].strip():
            e.append("[2] %s: empty text" % k)
        if re.search(r"[A-Za-z]", a["text"]):
            e.append("[2] %s: latin chars" % k)
        if a["status"] == "ACTIVE" and (a.get("ocr_similarity") or 0) < OCR_FLOOR:
            e.append("[2] %s: OCR similarity %r below %.2f floor"
                     % (k, a.get("ocr_similarity"), OCR_FLOOR))
    if not arts["labor_reg_art_001"]["text"].startswith(ART1_ANCHOR):
        e.append("[2] art 1 anchor mismatch")
    deleted = sorted(int(re.match(r"labor_reg_art_(\d{3})", k).group(1))
                     for k, a in arts.items() if a["status"] == "DELETED")
    if deleted != DELETED_NUMBERS:
        e.append("[2] deleted numbers %s != %s" % (deleted, DELETED_NUMBERS))

    # [3] cross-law linkage: implements targets exist in the verified law track
    #     and are not deleted there; law-quote cross-check cleared its floor
    law = {}
    for line in open(LAW_RECORDS, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            if not r["is_mukarrar"]:
                law[r["article_number"]] = r
    for k, a in arts.items():
        if a["status"] != "ACTIVE":
            continue
        targets = a.get("implements_law_articles", [])
        if not targets:
            e.append("[3] %s: active article with no implements_law_articles" % k)
        for n in targets:
            if n not in law:
                e.append("[3] %s: implements law art %s not in verified law track" % (k, n))
            elif law[n]["is_deleted"]:
                e.append("[3] %s: implements DELETED law art %s" % (k, n))
    quotes = src.get("law_quotes_cross_check", {})
    if len(quotes) < 40:
        e.append("[3] only %d law quotes cross-checked (expected 45)" % len(quotes))
    for n, q in quotes.items():
        if q["similarity_vs_verified_law"] < QUOTE_FLOOR:
            e.append("[3] law quote %s similarity %.2f below floor" % (n, q["similarity_vs_verified_law"]))

    # [4] verified records + [5] LLM layer verbatim/hashes
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        if r["article_text_verified"] != arts[r["article_key"]]["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("official_text_status") != STATUS or r.get("verification_status") not in ALLOWED:
            e.append("[4] %s: bad status fields" % r["article_key"])
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
    if sum(1 for r in recs if r["is_deleted"]) != len(DELETED_NUMBERS):
        e.append("[5] deleted count != %d" % len(DELETED_NUMBERS))

    if e:
        print("FAIL: %d error(s) in Labor Regulation track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Labor Regulation track — 45 records (arts 1-40 + 5 mukarrar; 3 deleted flagged)")
    print("  - trust gate: every record ACTIVE or DELETED; OCR floor %.2f cleared" % OCR_FLOOR)
    print("  - %d law quotes cross-checked >= %.2f vs the verified Labor Law track" % (len(quotes), QUOTE_FLOOR))
    print("  - implements_law_articles links all resolve to existing non-deleted law articles")
    print("  - texts verbatim vs committed source; hashes consistent; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
