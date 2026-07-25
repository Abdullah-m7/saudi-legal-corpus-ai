#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Credit Information Law track (17 records, all
اصلية, flat structure with no chapters).

VERIFICATION TIER — TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED. See the
generator's module docstring and sources/credit_information/law/
official_source/credit_information_law_official_source.json's
verification_methodology_note for the full caveat. laws.boe.gov.sa's live
portal was unreachable this research pass (HTTP 503 / connection reset direct,
HTTP 422 via r.jina.ai). This track instead rests on a single official/primary
channel — a Wayback Machine snapshot of the exact BOE lawId page — cross-
verified against two independent non-official secondary sources (nezams.com,
saudipedia.com). This validator checks internal consistency and that every
article carries the distinct-tier status tag; it CANNOT verify against a
primary source the build environment cannot reach live."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "credit_information", "law", "official_source",
                   "credit_information_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "credit_information", "law", "verified",
                       "credit_information_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "credit_information_arabic_legal_llm",
                   "credit_information_law_legal_llm_001_017.json")
N = 17
KEY_RE = r"credit_information_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 17}
STATUS = "BOE_WAYBACK_PRIMARY_X_NEZAMS_X_SAUDIPEDIA_TRIPLE_CROSS_VERIFIED_LIVE_BOE_UNREACHABLE"
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

    if src.get("chapter_structure"):
        e.append("[1c] expected empty chapter_structure for this flat-structure law")

    if src.get("decree") != "المرسوم الملكي رقم (م/37)":
        e.append("[1d] unexpected decree citation: %r" % src.get("decree"))
    if src.get("decree_date_hijri") != "5/7/1429":
        e.append("[1d] unexpected decree_date_hijri: %r" % src.get("decree_date_hijri"))

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

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة") or sc.get("معدلة"):
        e.append("[2] unexpected repealed/added/amended articles present — this law's base text "
                 "carries no amendments per this pass's research")

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    if src.get("known_unresolved_discrepancies") is None:
        e.append("[2e] known_unresolved_discrepancies key must be present (may be an empty list "
                 "if none were found)")

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
        print("FAIL: %d error(s) in Credit Information Law track:" % len(e))
        for x in e[:20]:
            print("  - %s" % x)
        return 1
    print("PASS: Credit Information Law — 17 records (all اصلية, no amendments/repeals found)")
    print("  - VERIFICATION TIER: TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED — Wayback Machine")
    print("    snapshot of the BOE lawId page (sole official channel reached) x nezams.com x")
    print("    saudipedia.com; live BOE portal unreachable (503/connection reset) this pass")
    print("  - numbered 1..17, flat structure, no chapters")
    print("  - IN-FORCE Royal Decree M/37 (5/7/1429H = 8 July 2008G); no amendments found via a")
    print("    dedicated search pass; no predecessor law repealed (Article 17 is a general clause)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
