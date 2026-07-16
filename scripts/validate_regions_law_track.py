#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Regions/Provinces Law track (41 records,
consolidated amended law: 31 اصلية / 9 معدلة / 0 ملغاة / 1 مضافة).

DISTINCT VERIFICATION TIER — see the generator's module docstring and
sources/regions/law/official_source/regions_law_official_source.json's
verification_methodology_note for the full caveat. This law's specific BOE
LawDetails page could not be reached across roughly 20 attempts this
research pass (page-specific hang / rate-limit blocks — a different BOE
page was reachable in the same session). This track instead rests on
cross-verified agreement between two independent Arabic secondary sources
(islamport.com, nezams.com). This validator checks internal consistency and
that every article carries the distinct-tier status tag; it CANNOT verify
against a primary source the build environment could not reach."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "regions", "law", "official_source",
                   "regions_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "regions", "law", "verified",
                       "regions_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "regions_arabic_legal_llm",
                   "regions_law_legal_llm_001_041.json")
N = 41
KEY_RE = r"regions_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 31, "معدلة": 9, "مضافة": 1}
STATUS = "DUAL_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE"
AMENDED_KEYS = {"regions_art_%03d" % n for n in (3, 7, 9, 10, 11, 12, 13, 16, 37)}
ADDED_KEYS = {"regions_art_041"}
AR = "ء-ي"


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        if (re.match("[%s]" % AR, before) and before != "ه"
                and re.match("[%s]" % AR, after)):
            bad += 1
    return bad


def main():
    e = []
    for p in (SRC, RECORDS, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)
    for k in AMENDED_KEYS | ADDED_KEYS:
        if k not in arts:
            e.append("[1] expected article key %s missing" % k)

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if a.get("section_ar"):
            e.append("[2] %s: unexpected non-empty section_ar in a flat-structure law" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS | ADDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended/added article missing amendment_history" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة"):
        e.append("[2] unexpected repealed articles present")

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    if not src.get("known_unresolved_discrepancies"):
        e.append("[2e] missing known_unresolved_discrepancies (BOE-page-unreachable caveat expected)")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
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
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Regions/Provinces Law track:" % len(e))
        for x in e[:20]:
            print("  - %s" % x)
        return 1
    print("PASS: Regions/Provinces Law — 41 records (consolidated: 31 اصلية / 9 معدلة / 1 مضافة)")
    print("  - DISTINCT TIER: dual independent Arabic secondary sources (islamport.com x")
    print("    nezams.com); this law's specific BOE page could not be reached across ~20 attempts")
    print("  - numbered 1..41, flat structure (no chapters), 9 articles amended + art 41 added by")
    print("    the 1414H consolidating amendment (Royal Order أ/21)")
    print("  - IN-FORCE Royal Order A/92 (27/8/1412H); FAOLEX English PDF used only as a weaker")
    print("    meaning-level structural cross-check (confirmed incomplete/date-flawed, not for wording)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
