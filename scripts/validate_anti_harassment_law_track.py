#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Anti-Harassment Law track (8 records,
consolidated amended law: 7 اصلية / 1 معدلة).

DISTINCT VERIFICATION TIER, two sub-tiers within this single track. 7
unamended articles (1-5, 7, 8): BOE portal cross-checked against four
independent secondary sources, no divergence. Article 6: base 2 paragraphs
BOE-verified; a 2021 third-paragraph amendment (Royal Decree M/48,
1/6/1442H) is confirmed real via Umm Al-Qura's own indexed gazette title
and two independent news outlets, but its exact wording rests on secondary
press convergence with a documented alternate candidate, not a
fully-rendered primary document. Repository owner explicitly reviewed and
approved this specific handling."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "anti_harassment", "law", "official_source",
                   "anti_harassment_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "anti_harassment", "law", "verified",
                       "anti_harassment_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "anti_harassment_arabic_legal_llm",
                   "anti_harassment_law_legal_llm_001_008.json")
N = 8
KEY_RE = r"anti_harassment_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 7, "معدلة": 1}
TIER_BOE = "BOE_PORTAL_MULTI_SOURCE_CROSS_CHECKED"
TIER_AMENDED = "SECONDARY_PRESS_CONVERGENCE_AMENDMENT_UNCONFIRMED_VERBATIM"
TRUSTED = {TIER_BOE, TIER_AMENDED}
AMENDED_KEYS = {"anti_harassment_art_006"}
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

    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1] numbered articles not a complete 1..%d sequence" % N)
    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))

    sc = Counter()
    for k, a in arts.items():
        tier = a.get("verification_tier")
        if tier not in TRUSTED:
            e.append("[2] %s: UNTRUSTED/unlabeled verification_tier %r" % (k, tier))
        if a.get("status") != tier:
            e.append("[2] %s: status field must equal verification_tier" % k)
        if k in AMENDED_KEYS and tier != TIER_AMENDED:
            e.append("[2] %s: expected TIER_AMENDED, got %r" % (k, tier))
        if k not in AMENDED_KEYS and tier != TIER_BOE:
            e.append("[2] %s: expected TIER_BOE, got %r" % (k, tier))
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
        if k in AMENDED_KEYS and not a.get("original_boe_text_paragraphs_1_2"):
            e.append("[2] %s: amended article missing original_boe_text_paragraphs_1_2 for provenance" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected repealed/added articles present")

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    if not src.get("known_unresolved_discrepancies"):
        e.append("[2e] missing known_unresolved_discrepancies (art 6 wording-conflict expected)")

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
        print("FAIL: %d error(s) in Anti-Harassment Law track:" % len(e))
        for x in e[:20]:
            print("  - %s" % x)
        return 1
    print("PASS: Anti-Harassment Law — 8 records (consolidated: 7 اصلية / 1 معدلة)")
    print("  - DISTINCT TIER: 7 articles BOE-multi-source cross-checked, 1 article (6) amended")
    print("    via secondary press convergence — amendment existence confirmed, exact wording flagged")
    print("  - numbered 1..8 by ordinal position (no مكرر), flat structure; no dual-status divergence")
    print("  - IN-FORCE Royal Decree M/96 (16/9/1439H); Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
