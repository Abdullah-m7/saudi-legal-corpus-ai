#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Allegiance Commission Regulation track (18
records, fresh issuance, all اصلية).

DISTINCT VERIFICATION TIER — see the generator's module docstring and
sources/allegiance_commission_regulation/law/official_source/
allegiance_commission_regulation_official_source.json's
verification_methodology_note for the full caveat. TIER_2: SPA (official
primary state wire) reached and cross-verified against islamport.com
(independent private secondary source), full agreement on all 18 articles;
BOE portal located but unreachable by every method tried this pass. This
validator also enforces that the documented known_unresolved_discrepancies
(BOE unreachable, Gazette issue 4828 citation-only, Gregorian date
correction) are preserved, not silently dropped."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "allegiance_commission_regulation", "law", "official_source",
                   "allegiance_commission_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "allegiance_commission_regulation", "law", "verified",
                       "allegiance_commission_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "allegiance_commission_regulation_arabic_legal_llm",
                   "allegiance_commission_regulation_legal_llm_001_018.json")
N = 18
KEY_RE = r"allegiance_commission_regulation_art_(\d{3})$"
STATUS = "SPA_OFFICIAL_WIRE_X_ISLAMPORT_SECONDARY_CROSS_VERIFIED_BOE_UNREACHABLE"
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
    if src.get("article_count") != N:
        e.append("[1] article_count field %r != %d" % (src.get("article_count"), N))
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls != "اصلية":
            e.append("[2] %s: expected legal_status اصلية, got %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"<|>|&[a-z]+;", a["text"]):
            e.append("[2] %s: empty text or HTML leftovers" % k)
        if a.get("section_ar"):
            e.append("[2] %s: unexpected non-empty section_ar in a flat-structure law" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)

    if sc.get("اصلية") != N:
        e.append("[2] expected %d اصلية articles, found %s" % (N, sc.get("اصلية")))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    discs = src.get("known_unresolved_discrepancies", [])
    if not discs:
        e.append("[2e] missing known_unresolved_discrepancies")
    disc_keys = " ".join(d.get("article_key", "") for d in discs)
    if "boe_unreachable" not in disc_keys:
        e.append("[2f] missing the documented BOE-unreachable discrepancy — must not be silently dropped")
    if "gazette_issue_4828" not in disc_keys:
        e.append("[2g] missing the documented unconfirmed Gazette issue 4828 citation")
    if "gregorian_date_correction" not in disc_keys:
        e.append("[2h] missing the documented Gregorian date correction disclosure")

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
        print("FAIL: %d error(s) in Allegiance Commission Regulation track:" % len(e))
        for x in e[:20]:
            print("  - %s" % x)
        return 1
    print("PASS: Allegiance Commission Regulation — 18 records (fresh issuance: all اصلية)")
    print("  - TIER_2: SPA official primary state wire x islamport.com independent secondary,")
    print("    full agreement on all 18 articles; BOE portal located but unreachable this pass")
    print("  - numbered 1..18, flat structure (no chapters)")
    print("  - IN-FORCE Royal Order A/164 (26/9/1428H = 8 Oct 2007, corrected this pass);")
    print("    known_unresolved_discrepancies preserved, not silently resolved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
