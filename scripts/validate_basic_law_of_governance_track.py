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

POST-MERGE CORRECTED, MIXED TIER: 82 articles اصلية on the primary BOE/WIPO
Lex tier; Article 5 is معدلة (discovered via a cross-track conflict with the
Allegiance Commission Law), verified via a distinct tier — secondary Arabic
sources plus primary-source OCR of the actual amending Royal Order PDF — see
verification_methodology_note in the source artifact for the full
correction history. Organized under 9 chapters with section_ar carrying
each article's chapter heading."""
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
PRIMARY_TIER = "BOE_PORTAL_PRIMARY_SOURCE_WIPO_LEX_SPOT_CHECKED"
CORRECTION_TIER = "SECONDARY_SOURCE_PLUS_PRIMARY_OCR_CONFIRMED_AMENDMENT"
TRUSTED_TIERS = {PRIMARY_TIER, CORRECTION_TIER}
AMENDED_KEYS = {"basic_law_of_governance_art_005"}
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
        tier = a.get("verification_tier", a.get("status"))
        if tier not in TRUSTED_TIERS:
            e.append("[2] %s: UNTRUSTED/unlabeled verification_tier %r" % (k, tier))
        if a.get("status") != tier:
            e.append("[2] %s: status field must equal verification_tier" % k)
        if k in AMENDED_KEYS and tier != CORRECTION_TIER:
            e.append("[2] %s: expected CORRECTION_TIER, got %r" % (k, tier))
        if k not in AMENDED_KEYS and tier != PRIMARY_TIER:
            e.append("[2] %s: expected PRIMARY_TIER, got %r" % (k, tier))
        ls = a.get("legal_status_ar")
        if k in AMENDED_KEYS and ls != "معدلة":
            e.append("[2] %s: expected legal_status معدلة" % k)
        if k not in AMENDED_KEYS and ls != "اصلية":
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
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if k in AMENDED_KEYS and not a.get("original_1412h_text"):
            e.append("[2] %s: amended article missing original_1412h_text for provenance" % k)

    if sc.get("اصلية") != N - len(AMENDED_KEYS):
        e.append("[2] status اصلية: %s != %d" % (sc.get("اصلية"), N - len(AMENDED_KEYS)))
    if sc.get("معدلة") != len(AMENDED_KEYS):
        e.append("[2] status معدلة: %s != %d" % (sc.get("معدلة"), len(AMENDED_KEYS)))
    if checked_count != 39:
        e.append("[2f] expected 39 WIPO-Lex-spot-checked articles, found %d" % checked_count)

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    if not src.get("preamble_ar"):
        e.append("[2g] missing preamble_ar (Royal Order promulgating text)")
    if not src.get("known_unresolved_discrepancies"):
        e.append("[2h] missing known_unresolved_discrepancies documenting the article 5 correction")

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
        expected_tier = CORRECTION_TIER if r["article_key"] in AMENDED_KEYS else PRIMARY_TIER
        if r.get("official_text_status") != expected_tier:
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
    print("PASS: Basic Law of Governance — 83 records (consolidated: 82 اصلية / 1 معدلة)")
    print("  - DISTINCT TIER: BOE portal primary source (complete/gapless), WIPO Lex spot-checked")
    print("    (39/83 articles individually cross-verified across all 9 chapters, no divergences;")
    print("    full 83-article/9-chapter structure matched between both sources)")
    print("  - POST-MERGE CORRECTED: article 5 is معدلة (discovered via a cross-track conflict with")
    print("    the Allegiance Commission Law), verified via secondary sources + primary-source OCR")
    print("  - numbered 1..83 by ordinal position (no مكرر), 9 chapters correctly mapped to section_ar")
    print("  - IN-FORCE Royal Order A/90 (27/8/1412H); committed WIPO Lex PDF hash verified; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
