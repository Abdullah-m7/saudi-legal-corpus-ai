#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Copyright Law track (28 records, consolidated
amended law: 19 اصلية / 9 معدلة).

DISTINCT VERIFICATION TIER — see the generator's module docstring and
sources/copyright/law/official_source/copyright_law_official_source.json's
verification_methodology_note for the full caveat. laws.boe.gov.sa was
unreachable this research pass; the primary working source is qadha.org.sa's
compiled text, structurally cross-checked against WIPO Lex. This validator
also enforces that this law's confirmed 2026-08-12 repeal (by Royal Decree
M/169) is documented, not silently omitted. This validator CANNOT verify
against a primary source the build environment could not reach."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "copyright", "law", "official_source",
                   "copyright_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "copyright", "law", "verified",
                       "copyright_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "copyright_arabic_legal_llm",
                   "copyright_law_legal_llm_001_028.json")
N = 28
KEY_RE = r"copyright_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 19, "معدلة": 9}
STATUS = "SECONDARY_SOURCE_STRUCTURAL_WIPO_CROSS_CHECK_BOE_UNREACHABLE"
AMENDED_KEYS = {"copyright_art_%03d" % n for n in (1, 7, 8, 16, 21, 22, 24, 25, 26)}
EXPECTED_CHAPTERS = 8  # definitions heading (art 1) + 7 numbered chapters
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

    chapters = src.get("chapter_structure", [])
    if len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d chapter sections, found %d" % (EXPECTED_CHAPTERS, len(chapters)))
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
        if k in AMENDED_KEYS and not a.get("original_2003_text"):
            e.append("[2] %s: amended article missing original_2003_text for provenance" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected repealed/added articles present")

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    if "2026-08-12" not in src.get("verification_methodology_note", ""):
        e.append("[2f] verification_methodology_note must document the confirmed 2026-08-12 "
                 "repeal by Royal Decree M/169")
    if not src.get("known_unresolved_discrepancies"):
        e.append("[2e] missing known_unresolved_discrepancies (repeal + BOE-unreachable caveats expected)")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if not r.get("superseding_law_notice"):
            e.append("[4] %s: missing superseding_law_notice (repeal must not be silently omitted)" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    if not llm.get("superseding_law_notice"):
        e.append("[5] llm layer missing superseding_law_notice")
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
        print("FAIL: %d error(s) in Copyright Law track:" % len(e))
        for x in e[:20]:
            print("  - %s" % x)
        return 1
    print("PASS: Copyright Law — 28 records (consolidated: 19 اصلية / 9 معدلة)")
    print("  - DISTINCT TIER: qadha.org.sa compiled text (Saudi judicial-studies association),")
    print("    structurally cross-checked against WIPO Lex; laws.boe.gov.sa unreachable this pass")
    print("  - numbered 1..28 across 7 chapters (plus article 1's own definitions heading)")
    print("  - 2018 amendment (Council of Ministers Resolution 536): Ministry/Minister -> SAIP")
    print("    (الهيئة/المجلس) at 9 articles, verified against the amendment's own footnoted text")
    print("  - *** CONFIRMED SUPERSEDED effective 2026-08-12 by Royal Decree M/169 *** — the new")
    print("    law's text is not yet verifiable and is explicitly not ingested; flagged throughout")
    return 0


if __name__ == "__main__":
    sys.exit(main())
