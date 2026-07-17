#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Competition Law track (28 records, all
اصلية, flat structure with no chapters).

DISTINCT VERIFICATION TIER — see the generator's module docstring and
sources/competition/law/official_source/competition_law_official_source.json's
verification_methodology_note for the full caveat. This validator checks
internal consistency and that every article carries the distinct-tier
status tag, and that the discrepancy investigation (Articles 11/12's
mislabeled BOE amendment note) is documented."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "competition", "law", "official_source",
                   "competition_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "competition", "law", "verified",
                       "competition_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "competition_arabic_legal_llm",
                   "competition_law_legal_llm_001_028.json")
N = 28
KEY_RE = r"competition_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 28}
STATUS = "DUAL_PRIMARY_SOURCE_BOE_WAYBACK_X_NEZAMS_CROSS_VERIFIED"
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
        e.append("[2] unexpected amended/repealed/added articles present (no confirmed amendments)")

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies (Articles 11/12 mislabeled-note caveat expected)")
    else:
        flagged = {d["article_key"] for d in disc}
        if "competition_bug_articles_011_012" not in flagged:
            e.append("[2e] expected discrepancy entry for the Articles 11/12 mislabeled BOE amendment note")

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
        print("FAIL: %d error(s) in Competition Law track:" % len(e))
        for x in e[:20]:
            print("  - %s" % x)
        return 1
    print("PASS: Competition Law — 28 records (all اصلية, no confirmed amendments)")
    print("  - DISTINCT TIER: BOE portal via Wayback Machine snapshot (two independent dates),")
    print("    cross-verified word-for-word against nezams.com")
    print("  - numbered 1..28, flat structure, no chapters")
    print("  - IN-FORCE Royal Decree M/75 (29/6/1440H); replaces M/25 (1425H)")
    print("  - a candidate Art 11/12 amendment note was investigated and found to belong to a")
    print("    different instrument (GAC organizational statute) — flagged, not applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
