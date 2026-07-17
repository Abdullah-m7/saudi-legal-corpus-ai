#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Shura Council Law track (30 records,
consolidated amended law: 24 اصلية / 6 معدلة).

MIXED VERIFICATION TIER — see the generator's module docstring and
sources/shura_council/law/official_source/shura_council_law_official_source.json's
verification_methodology_note for the full caveat. laws.boe.gov.sa's exact
page for this law was located but unreachable by every method tried this
research pass. Every article carries its own verification_tier: triple
independent Arabic secondary sources for 29 articles, plus a government
primary source (Saudi Press Agency) specifically for Article 3's current
(2013-amended) text. This validator checks internal consistency and that
every article is explicitly tagged with its tier; it CANNOT verify against
a primary source the build environment could not reach."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "shura_council", "law", "official_source",
                   "shura_council_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "shura_council", "law", "verified",
                       "shura_council_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "shura_council_arabic_legal_llm",
                   "shura_council_law_legal_llm_001_030.json")
N = 30
KEY_RE = r"shura_council_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 24, "معدلة": 6}
TIER_TRIPLE = "TRIPLE_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE"
TIER_SPA_PRIMARY = "GOVERNMENT_PRIMARY_SPA_ANNOUNCEMENT_VERIFIED"
TRUSTED = {TIER_TRIPLE, TIER_SPA_PRIMARY}
AMENDED_KEYS = {"shura_council_art_%03d" % n for n in (3, 10, 17, 21, 23, 29)}
SPA_PRIMARY_KEYS = {"shura_council_art_003"}
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
    for k in AMENDED_KEYS:
        if k not in arts:
            e.append("[1] expected amended article key %s missing" % k)

    sc = Counter()
    for k, a in arts.items():
        tier = a.get("verification_tier")
        if tier not in TRUSTED:
            e.append("[2] %s: UNTRUSTED/unlabeled verification_tier %r" % (k, tier))
        if a.get("status") != tier:
            e.append("[2] %s: status field must equal verification_tier" % k)
        if k in SPA_PRIMARY_KEYS and tier != TIER_SPA_PRIMARY:
            e.append("[2] %s: expected TIER_SPA_PRIMARY, got %r" % (k, tier))
        if k not in SPA_PRIMARY_KEYS and tier != TIER_TRIPLE:
            e.append("[2] %s: expected TIER_TRIPLE, got %r" % (k, tier))
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
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected repealed/added articles present")

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    if not src.get("known_unresolved_discrepancies"):
        e.append("[2e] missing known_unresolved_discrepancies (art 78 amendment provenance gap expected)")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_tier") != a.get("verification_tier"):
            e.append("[4] %s: verification_tier mismatch" % r["article_key"])
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
        if r.get("source_trust", {}).get("verification_tier") not in TRUSTED:
            e.append("[5] %s: llm record missing/bad verification_tier in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Shura Council Law track:" % len(e))
        for x in e[:20]:
            print("  - %s" % x)
        return 1
    print("PASS: Shura Council Law — 30 records (consolidated: 24 اصلية / 6 معدلة)")
    print("  - MIXED TIER: 29 articles TRIPLE_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED (BOE page")
    print("    located but unreachable); article 3's current text additionally confirmed via a")
    print("    Tier-1 government primary source (Saudi Press Agency verbatim reproduction)")
    print("  - numbered 1..30, flat structure (no chapters); article 3 amended 3x, arts 10/21/29")
    print("    amended once by أ/181 (1428H), arts 17/23 amended once by أ/198 (1424H)")
    print("  - IN-FORCE Royal Order A/91 (27/8/1412H); Royal Order أ/78's exact original")
    print("    wording (art 3's first amendment) flagged as an unresolved provenance gap")
    return 0


if __name__ == "__main__":
    sys.exit(main())
