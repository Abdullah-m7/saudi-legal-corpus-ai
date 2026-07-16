#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Electronic Transactions Law track (31 records,
consolidated amended law: 24 اصلية / 5 معدلة / 2 ملغاة / 0 مضافة).

DISTINCT VERIFICATION TIER — see the generator's module docstring and
sources/electronic_transactions/law/official_source/
electronic_transactions_law_official_source.json's verification_methodology_note
for the full caveat. laws.boe.gov.sa was unreachable this research pass; the
primary source used instead is the official BOE/CoM translation-bureau PDF,
manually corrected for a systematic ligature-extraction bug and structurally
cross-checked against WIPO Lex's full English translation. This validator
checks internal consistency and that every article carries the distinct-tier
status tag; it CANNOT verify against a primary source the build environment
could not reach."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "electronic_transactions", "law", "official_source",
                   "electronic_transactions_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "electronic_transactions", "law", "verified",
                       "electronic_transactions_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "electronic_transactions_arabic_legal_llm",
                   "electronic_transactions_law_legal_llm_001_031.json")
N = 31
KEY_RE = r"electronic_transactions_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 24, "معدلة": 5, "ملغاة": 2}
STATUS = "SINGLE_PRIMARY_SOURCE_WIPO_STRUCTURAL_CROSS_CHECK_MANUAL_LIGATURE_CORRECTION"
AMENDED_KEYS = {"electronic_transactions_art_%03d" % n for n in (1, 3, 15, 29, 30)}
REPEALED_KEYS = {"electronic_transactions_art_%03d" % n for n in (16, 17)}
EXPECTED_CHAPTERS = 10
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
    for k in AMENDED_KEYS | REPEALED_KEYS:
        if k not in arts:
            e.append("[1] expected article key %s missing" % k)

    chapters = src.get("chapter_structure", [])
    if len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d chapters, found %d" % (EXPECTED_CHAPTERS, len(chapters)))
    covered = set()
    for ch in chapters:
        for n in range(ch["first_article"], ch["last_article"] + 1):
            covered.add(n)
    if covered != set(range(1, N + 1)):
        e.append("[1c] chapter_structure does not gaplessly cover articles 1..%d: missing %s"
                 % (N, sorted(set(range(1, N + 1)) - covered)))

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
        if not a.get("section_ar", "").strip():
            e.append("[2] %s: chapter-aware law missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if k in AMENDED_KEYS and not a.get("original_2007_text"):
            e.append("[2] %s: amended article missing original_2007_text for provenance" % k)
        if k in REPEALED_KEYS and not a.get("history"):
            e.append("[2] %s: repealed article missing amendment_history" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("مضافة"):
        e.append("[2] unexpected added articles present")

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    if not src.get("known_unresolved_discrepancies"):
        e.append("[2e] missing known_unresolved_discrepancies (ligature-hazard / post-Ch6 "
                 "renumbering / WIPO Lex metadata-anomaly caveats expected)")
    if len(src.get("known_unresolved_discrepancies", [])) < 3:
        e.append("[2e] expected at least 3 documented discrepancies (art 16, art 17/post-Ch6 "
                 "renumbering, WIPO Lex metadata anomaly)")

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
        print("FAIL: %d error(s) in Electronic Transactions Law track:" % len(e))
        for x in e[:20]:
            print("  - %s" % x)
        return 1
    print("PASS: Electronic Transactions Law — 31 records (consolidated: 24 اصلية / 5 معدلة / 2 ملغاة)")
    print("  - DISTINCT TIER: single primary source (official BOE/CoM translation-bureau PDF,")
    print("    manually corrected for a systematic lam+alef ligature-extraction bug), structurally")
    print("    cross-checked against WIPO Lex's full English translation (100% of articles)")
    print("  - numbered 1..31 across 10 original chapters; Chapter 6 (arts 16-17) abolished by the")
    print("    2023 amendment (Council of Ministers Resolution 293) and flagged ملغاة, not deleted")
    print("  - post-Chapter-6-abolition article renumbering could NOT be confirmed this pass —")
    print("    original 1..31 numbering preserved, documented as an unresolved discrepancy")
    print("  - IN-FORCE Royal Decree M/18 (8/3/1428H); distinct from Anti-Cyber Crime Law (M/17)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
