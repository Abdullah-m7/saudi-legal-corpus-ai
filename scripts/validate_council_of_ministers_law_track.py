#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Council of Ministers Law track (32 records,
consolidated amended law: 31 اصلية / 1 معدلة).

DISTINCT VERIFICATION TIER — see the generator's module docstring and
sources/council_of_ministers/law/official_source/
council_of_ministers_law_official_source.json's verification_methodology_note
for the full caveat. laws.boe.gov.sa was confirmed COMPLETELY UNREACHABLE
from the build environment across two separate research passes this session
(different failure signatures each time). This track instead rests on
cross-verified agreement between two independent Arabic secondary sources
(ar.wikisource.org, nezams.com), with FAOLEX's English PDF used only for a
structural cross-check. This validator checks internal consistency and that
every article carries the distinct-tier status tag; it CANNOT verify against
a primary source the build environment cannot reach."""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "council_of_ministers", "law", "official_source",
                   "council_of_ministers_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "council_of_ministers", "law", "verified",
                       "council_of_ministers_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "council_of_ministers_arabic_legal_llm",
                   "council_of_ministers_law_legal_llm_001_032.json")
N = 32
KEY_RE = r"council_of_ministers_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 31, "معدلة": 1}
STATUS = "DUAL_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE"
AMENDED_KEYS = {"council_of_ministers_art_030"}
COMPANION_KEYS = {"council_of_ministers_art_007"}
EXPECTED_CHAPTERS = 8
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
        if k in AMENDED_KEYS and not a.get("original_1414h_text"):
            e.append("[2] %s: amended article missing original_1414h_text for provenance" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected repealed/added articles present")

    for k in COMPANION_KEYS:
        if not arts[k].get("companion_instrument_note"):
            e.append("[2f] %s: expected companion_instrument_note documenting the linked exception order" % k)

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    if not src.get("known_unresolved_discrepancies"):
        e.append("[2e] missing known_unresolved_discrepancies (BOE-unreachable caveat expected)")

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
        import hashlib
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Council of Ministers Law track:" % len(e))
        for x in e[:20]:
            print("  - %s" % x)
        return 1
    print("PASS: Council of Ministers Law — 32 records (consolidated: 31 اصلية / 1 معدلة)")
    print("  - DISTINCT TIER: dual independent Arabic secondary sources (ar.wikisource.org x")
    print("    nezams.com), BOE portal confirmed completely unreachable across two research passes")
    print("  - numbered 1..32 across 8 chapters, section_ar carries each article's chapter heading")
    print("  - IN-FORCE Royal Order A/13 (3/3/1414H); article 30 amended by Royal Order أ/151 (1432H)")
    print("  - article 7 carries a documented companion_instrument_note (Royal Order أ/45, 1446H)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
