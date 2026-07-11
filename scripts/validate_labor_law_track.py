#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Labor Law track (249 records).

Trust gate: every record's verification_status must be one of the four
explained categories (MATCHES_BOE_BASE / DIFFERS_AS_AMENDED / MUKARRAR /
DELETED) — an UNEXPLAINED_DIFF anywhere fails the gate. Also re-checks the
double-verification claim against the committed BOE worksheets."""
from __future__ import annotations

import csv
import glob
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "labor", "law", "official_source",
                   "labor_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "labor", "law", "verified",
                       "labor_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "labor_arabic_legal_llm", "labor_law_legal_llm_001_245.json")
WORKSHEETS = os.path.join(ROOT, "worksheets", "labor_law", "reconciliation_batches")
STATUS = "HRSD_CONSOLIDATED_CROSS_CHECKED_BOE"
ALLOWED = {"MATCHES_BOE_BASE", "DIFFERS_AS_AMENDED", "MUKARRAR", "DELETED"}
N = 249


def _norm_tokens(s):
    s = re.sub(r"[ً-ْٰـ]", "", s)
    for a, b in (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ى", "ي"), ("ة", "ه")):
        s = s.replace(a, b)
    return re.sub(r"[^ء-ي0-9]+", " ", s).split()


def main():
    e = []
    for p in (SRC, RECORDS, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]
    if len(arts) != N:
        e.append("[1] source has %d articles, expected %d" % (len(arts), N))
    nums = sorted(int(re.match(r"labor_law_art_(\d{3})", k).group(1)) for k in arts
                  if not k.endswith("_mukarrar"))
    if nums != list(range(1, 246)):
        e.append("[1] numbered articles not a complete 1..245 sequence")

    # [2] trust gate: only explained statuses; art 1 anchor; no latin
    for k, a in arts.items():
        if a["status"] not in ALLOWED:
            e.append("[2] %s: UNTRUSTED status %r" % (k, a["status"]))
        if not a["text"].strip():
            e.append("[2] %s: empty text" % k)
        if re.search(r"[A-Za-z]", a["text"]):
            e.append("[2] %s: latin chars" % k)
    if arts["labor_law_art_001"]["text"] != "يسمى هذا النظام نظام العمل.":
        e.append("[2] art 1 anchor mismatch")

    # [3] re-verify double-verification: MATCHES_BOE_BASE must really match BOE worksheets
    boe = {}
    for f in glob.glob(os.path.join(WORKSHEETS, "*.csv")):
        for row in csv.DictReader(open(f, encoding="utf-8")):
            boe[row["article_key"]] = row.get("official_arabic_text_reconciled", "")
    checked = 0
    for k, a in arts.items():
        if a["status"] == "MATCHES_BOE_BASE" and k in boe and boe[k].strip():
            t1, t2 = set(_norm_tokens(a["text"])), set(_norm_tokens(boe[k]))
            sim = len(t1 & t2) / max(len(t1 | t2), 1)
            if sim < 0.90:
                e.append("[3] %s: claimed BOE match but similarity %.2f" % (k, sim))
            checked += 1
    if checked < 100:
        e.append("[3] only %d BOE matches re-checked (expected 140+)" % checked)

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
    del_count = sum(1 for r in recs if r["is_deleted"])
    if del_count != 38:
        e.append("[5] deleted count %d != 38" % del_count)

    if e:
        print("FAIL: %d error(s) in Labor Law track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Labor Law track — 249 records (245 articles + 4 mukarrar; 38 deleted flagged)")
    print("  - trust gate: every record in an explained category; zero unexplained diffs")
    print("  - %d MATCHES_BOE_BASE records re-verified against the committed BOE worksheets" % checked)
    print("  - texts verbatim vs committed source; hashes consistent; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
