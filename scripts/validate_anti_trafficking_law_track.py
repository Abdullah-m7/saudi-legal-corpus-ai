#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Anti-Trafficking in Persons Law track
(17 records).

DISTINCT VERIFICATION TIER: BOE Wayback-snapshot extraction, cross-checked
for substance (not exact Arabic wording) against UNODC's official English
translation and the 2025 US State Department TIP report. Weaker than this
corpus's usual Arabic-to-Arabic comparison, since no second full-text
Arabic source was reachable this session. A 33-article draft replacement
law cleared public consultation in 2022 but remains UNENACTED per the most
recent evidence found — documented, not silently ignored. Fresh full
issuance: all 17 اصلية. Flat structure with no chapter/section wrapper."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "anti_trafficking", "law", "official_source",
                   "anti_trafficking_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "anti_trafficking", "law", "verified",
                       "anti_trafficking_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "anti_trafficking_arabic_legal_llm",
                   "anti_trafficking_law_legal_llm_001_017.json")
N = 17
KEY_RE = r"anti_trafficking_art_(\d{3})$"
STATUS = "BOE_WAYBACK_SNAPSHOT_UNODC_ENGLISH_SUBSTANCE_VERIFIED"
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
        if a.get("status") != STATUS:
            e.append("[2] %s: unexpected status %r" % (k, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls != "اصلية":
            e.append("[2] %s: unexpected legal_status %r (fresh issuance expected)" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if a.get("section_ar"):
            e.append("[2] %s: unexpected non-empty section_ar in a flat-structure law" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)

    if sc.get("اصلية") != N:
        e.append("[2] status اصلية: %s != %d" % (sc.get("اصلية"), N))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    if not src.get("known_unresolved_discrepancies"):
        e.append("[2e] missing known_unresolved_discrepancies (draft-replacement-law caveat expected)")
    if not src.get("preamble_ar"):
        e.append("[2g] missing preamble_ar (Royal Decree promulgating text)")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
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
        print("FAIL: %d error(s) in Anti-Trafficking Law track:" % len(e))
        for x in e[:20]:
            print("  - %s" % x)
        return 1
    print("PASS: Anti-Trafficking in Persons Law — 17 records (fresh issuance: all 17 اصلية)")
    print("  - DISTINCT TIER: BOE Wayback snapshot, UNODC English translation substance-verified")
    print("  - numbered 1..17 by ordinal position (no مكرر), flat structure; no dual-status divergence")
    print("  - IN-FORCE Royal Decree M/40 (21/7/1430H); Arabic governs")
    print("  - documented: 33-article draft replacement law cleared consultation but remains unenacted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
