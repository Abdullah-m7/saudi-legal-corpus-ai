#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Capital Market Law track (68 records, mixed
verification tier: 42 اصلية / 25 معدلة / 1 مضافة).

MIXED TIER — see the generator's module docstring and
sources/capital_market/law/official_source/
capital_market_law_official_source.json's verification_methodology_note for
the full caveat. 12 articles (the core of the 2019 M/16 restructuring)
carry ORIGINAL_2003_TEXT_ONLY_CURRENT_WORDING_CONFIRMED_AMENDED_UNVERIFIED
as their verification_tier — the 2003 text shown for these is explicitly
NOT current law. This validator enforces that every one of these 12
articles carries a matching known_unresolved_discrepancies entry, and that
Article 20 مكرر carries its own distinct lower-confidence tier."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "capital_market", "law", "official_source",
                   "capital_market_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "capital_market", "law", "verified",
                       "capital_market_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "capital_market_arabic_legal_llm",
                   "capital_market_law_legal_llm_001_068.json")
N = 68
KEY_RE = r"capital_market_art_(\d{3})(?:_mukarrar_(\d+))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 42, "معدلة": 25, "مضافة": 1}
TIER_MAIN = "CMA_CURRENT_SITE_X_BOE_2003_ORIGINAL_CROSS_VERIFIED"
TIER_FALLBACK = "ORIGINAL_2003_TEXT_ONLY_CURRENT_WORDING_CONFIRMED_AMENDED_UNVERIFIED"
TIER_RECONSTRUCTED = "RECONSTRUCTED_FROM_DOCUMENTED_RELOCATION_DESCRIPTION"
ALLOWED_TIERS = {TIER_MAIN, TIER_FALLBACK, TIER_RECONSTRUCTED}
FALLBACK_KEYS = {"capital_market_art_%03d" % n
                 for n in (1, 20, 21, 22, 23, 25, 26, 27, 28, 29, 30, 59)}
MUKARRAR_KEYS = {"capital_market_art_020_mukarrar_1"}
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
    for k in FALLBACK_KEYS | MUKARRAR_KEYS:
        if k not in arts:
            e.append("[1] expected article key %s missing" % k)

    if src.get("chapter_structure"):
        e.append("[1c] expected empty chapter_structure (unconfirmed current chapter map)")

    sc = Counter()
    tier_counts = Counter()
    for k, a in arts.items():
        tier = a.get("verification_tier")
        if tier not in ALLOWED_TIERS:
            e.append("[2] %s: unexpected verification_tier %r" % (k, tier))
        tier_counts[tier] += 1
        if a.get("status") != tier:
            e.append("[2] %s: status field must equal verification_tier" % k)
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if a.get("section_ar"):
            e.append("[2] %s: unexpected non-empty section_ar (flat chapter_structure)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in FALLBACK_KEYS and tier != TIER_FALLBACK:
            e.append("[2] %s: expected fallback tier %s, got %r" % (k, TIER_FALLBACK, tier))
        if k in MUKARRAR_KEYS and tier != TIER_RECONSTRUCTED:
            e.append("[2] %s: expected reconstructed tier %s, got %r" % (k, TIER_RECONSTRUCTED, tier))
        if ls == "معدلة" and not a.get("original_1424h_text"):
            e.append("[2] %s: amended article missing original_1424h_text for provenance" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة"):
        e.append("[2] unexpected repealed articles present")
    if tier_counts.get(TIER_FALLBACK) != len(FALLBACK_KEYS):
        e.append("[2f] expected %d fallback-tier articles, got %d"
                 % (len(FALLBACK_KEYS), tier_counts.get(TIER_FALLBACK, 0)))
    if tier_counts.get(TIER_RECONSTRUCTED) != len(MUKARRAR_KEYS):
        e.append("[2f] expected %d reconstructed-tier articles, got %d"
                 % (len(MUKARRAR_KEYS), tier_counts.get(TIER_RECONSTRUCTED, 0)))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the mixed tier")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FALLBACK_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for fallback articles: %s"
                     % sorted(missing))
        if "capital_market_art_020_mukarrar_1" not in flagged:
            e.append("[2e] expected discrepancy entry missing for Article 20 مكرر")

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

    if e:
        print("FAIL: %d error(s) in Capital Market Law track:" % len(e))
        for x in e[:25]:
            print("  - %s" % x)
        return 1
    print("PASS: Capital Market Law — 68 records (mixed tier: 42 اصلية / 25 معدلة / 1 مضافة)")
    print("  - MAIN TIER (%d articles): CMA current site x BOE 2003 original, cross-verified" % tier_counts.get(TIER_MAIN, 0))
    print("  - FALLBACK TIER (%d articles): 2003 original shown as flagged HISTORICAL text —" % tier_counts.get(TIER_FALLBACK, 0))
    print("    current wording confirmed amended but NOT recovered, NOT current law")
    print("  - RECONSTRUCTED TIER (1 article): Article 20 مكرر, from documented relocation description")
    print("  - IN-FORCE Royal Decree M/30 (2/6/1424H); restructured by M/16 (19/1/1441H)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
