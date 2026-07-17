#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Franchise Law track (27 records, all
اصلية, 11 chapters/فصول).

DISTINCT VERIFICATION TIER — see the generator's module docstring and
sources/franchise/law/official_source/franchise_law_official_source.json's
verification_methodology_note for the full caveat. laws.boe.gov.sa (the
primary source) was reached this research pass via the r.jina.ai proxy
after a direct WebFetch failure, and supplied the full verbatim text of
all 27 articles. Independent cross-verification against qanoniah.com was
achieved only as a spot check on Articles 1, 2, 4, and 5. This validator
checks internal consistency and that every article carries the
distinct-tier status tag; it CANNOT verify against a primary source the
build environment cannot reach at validation time."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "franchise", "law", "official_source",
                   "franchise_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "franchise", "law", "verified",
                       "franchise_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "franchise_arabic_legal_llm",
                   "franchise_law_legal_llm_001_027.json")
N = 27
KEY_RE = r"franchise_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 27}
STATUS = "BOE_PORTAL_PROXY_RETRIEVED_QANONIAH_SPOT_CROSS_VERIFIED"
EXPECTED_CHAPTERS = 11
FLAGGED_DISCREPANCY_KEYS = {"franchise_task_premise_date_error",
                            "franchise_m22_decree_collision",
                            "franchise_publication_date_mismatch",
                            "franchise_article4_heading_colon_artifact",
                            "franchise_qanoniah_secondary_source_incomplete",
                            "franchise_wayback_no_snapshot",
                            "franchise_cross_verification_scope_limited",
                            "franchise_2026_council_of_ministers_carveout_non_textual"}
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

    chapters = src.get("chapter_structure") or []
    if len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d chapters, got %d" % (EXPECTED_CHAPTERS, len(chapters)))

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
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (expected a فصل/chapter title)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if a.get("history"):
            e.append("[2] %s: unexpected non-empty amendment history (no amendments found)" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة") or sc.get("معدلة"):
        e.append("[2] unexpected repealed/added/amended articles present")

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

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
        print("FAIL: %d error(s) in Franchise Law track:" % len(e))
        for x in e[:20]:
            print("  - %s" % x)
        return 1
    print("PASS: Franchise Law — 27 records (all اصلية, 11 chapters)")
    print("  - DISTINCT TIER: BOE primary source (via r.jina.ai proxy),")
    print("    spot-cross-verified against qanoniah.com for Articles 1, 2, 4, 5 only")
    print("  - IN-FORCE Royal Decree M/22 (9/2/1441H); decree number collides with")
    print("    (but is unrelated to) the superseded Anti-Concealment Law's own M/22 (4/5/1425H)")
    print("  - 13/1/2026 Council of Ministers carve-out decision is non-textual and")
    print("    documented as a discrepancy, not merged into any article")
    return 0


if __name__ == "__main__":
    sys.exit(main())
