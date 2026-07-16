#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Basic Law of Governance track (83 records).

DISTINCT VERIFICATION TIER — stronger than the Anti-Bribery Law track (the
primary source here is a genuine official government structured database,
completely and gaplessly extracted), but still not this corpus's primary
MOJ-portal-x-official-PDF pipeline. Primary source: Bureau of Experts (BOE)
portal, reached via WebFetch + an r.jina.ai reader-proxy prefix. Second
source: WIPO Lex entry SA016 (OCR'd scan), spot-checked across ~47% of
articles (all 9 chapters, every chapter boundary) with no divergences found;
the full 83-article/9-chapter structure was confirmed to match in its
entirety. Every article carries its own cross_verified_against_wipo_lex tag.
Fresh consolidated text: all 83 اصلية (no amendment history found/flagged).
Organized under 9 chapters with section_ar carrying each article's chapter
heading."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "basic_law_of_governance", "law", "official_source",
                   "basic_law_of_governance_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "basic_law_of_governance", "law", "verified",
                       "basic_law_of_governance_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "basic_law_of_governance_arabic_legal_llm",
                   "basic_law_of_governance_legal_llm_001_083.json")
PDF = os.path.join(ROOT, "inputs", "basic_law_of_governance_source_pdfs",
                   "basic_law_of_governance_wipo_lex_sa016.pdf")
N = 83
KEY_RE = r"basic_law_of_governance_art_(\d{3})$"
STATUS = "BOE_PORTAL_PRIMARY_SOURCE_WIPO_LEX_SPOT_CHECKED"
CHAPTER_RANGES = [
    ("الباب الأول: المبادئ العامة", 1, 4),
    ("الباب الثاني: نظام الحكم", 5, 8),
    ("الباب الثالث: مقومات المجتمع السعودي", 9, 13),
    ("الباب الرابع: المبادئ الاقتصادية", 14, 22),
    ("الباب الخامس: الحقوق والواجبات", 23, 43),
    ("الباب السادس: سلطات الدولة", 44, 71),
    ("الباب السابع: الشئون المالية", 72, 78),
    ("الباب الثامن: أجهزة الرقابة", 79, 80),
    ("الباب التاسع: أحكام عامة", 81, 83),
]
SPOT_CHECKED_RANGES = [(1, 11), (14, 25), (44, 49), (69, 73), (79, 83)]
AR = "ء-ي"


def _expected_chapter(n):
    for label, lo, hi in CHAPTER_RANGES:
        if lo <= n <= hi:
            return label
    return None


def _expected_checked(n):
    return any(lo <= n <= hi for lo, hi in SPOT_CHECKED_RANGES)


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
    for p in (SRC, RECORDS, LLM, PDF):
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
    checked_count = 0
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
        if a.get("status") != STATUS:
            e.append("[2] %s: unexpected status %r" % (k, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls != "اصلية":
            e.append("[2] %s: unexpected legal_status %r (fresh consolidated text expected)" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if a.get("section_ar") != _expected_chapter(n):
            e.append("[2e] %s: section_ar %r does not match expected chapter for article %d"
                     % (k, a.get("section_ar"), n))
        if bool(a.get("cross_verified_against_wipo_lex")) != _expected_checked(n):
            e.append("[2f] %s: cross_verified_against_wipo_lex does not match expected spot-check range" % k)
        if a["cross_verified_against_wipo_lex"]:
            checked_count += 1
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)

    if sc.get("اصلية") != N:
        e.append("[2] status اصلية: %s != %d" % (sc.get("اصلية"), N))
    if checked_count != 39:
        e.append("[2f] expected 39 WIPO-Lex-spot-checked articles, found %d" % checked_count)

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    if not src.get("preamble_ar"):
        e.append("[2g] missing preamble_ar (Royal Order promulgating text)")

    pdf_sha = hashlib.sha256(open(PDF, "rb").read()).hexdigest()
    if pdf_sha != src.get("provenance", {}).get("wipo_lex_pdf_sha256"):
        e.append("[3] committed WIPO Lex PDF sha256 mismatch")
    if pdf_sha not in src["verification_methodology_note"]:
        e.append("[3] WIPO Lex PDF sha256 not documented in methodology note")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("official_text_status") != STATUS:
            e.append("[4] %s: bad status" % r["article_key"])
        if r.get("cross_verified_against_wipo_lex") != a["cross_verified_against_wipo_lex"]:
            e.append("[4] %s: cross_verified_against_wipo_lex mismatch" % r["article_key"])
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
        print("FAIL: %d error(s) in Basic Law of Governance track:" % len(e))
        for x in e[:20]:
            print("  - %s" % x)
        return 1
    print("PASS: Basic Law of Governance — 83 records (fresh consolidated text: all 83 اصلية)")
    print("  - DISTINCT TIER: BOE portal primary source (complete/gapless), WIPO Lex spot-checked")
    print("    (39/83 articles individually cross-verified across all 9 chapters, no divergences;")
    print("    full 83-article/9-chapter structure matched between both sources)")
    print("  - numbered 1..83 by ordinal position (no مكرر), 9 chapters correctly mapped to section_ar")
    print("  - IN-FORCE Royal Order A/90 (27/8/1412H); committed WIPO Lex PDF hash verified; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
