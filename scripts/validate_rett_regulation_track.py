#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Real Estate
Transaction Tax Law track (15 records, brand-new 2025 regulation: 15 اصلية,
flat -- no chapters).

VERIFICATION TIER -- see the generator's module docstring and
sources/rett_regulation/law/official_source/rett_regulation_official_source.json's
verification_methodology_note for the full account. This is a NEW
(24 March/9 April 2025) instrument (ZATCA Board Decision 01-03-25) with NO
amendments confirmed to date, so -- unlike a consolidated amended
regulation -- this validator asserts that every article is اصلية, that
there are NO معدلة/ملغاة/مضافة articles, and that no amendment_history is
present. It also asserts the Regulation is FLAT (chapter_structure empty;
section_ar empty on every article), because the Regulation genuinely has no
فصل/باب subdivisions (documented, not an omission)."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "rett_regulation", "law", "official_source",
                   "rett_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "rett_regulation", "law", "verified",
                       "rett_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "rett_regulation", "law", "verified",
                       "rett_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "rett_regulation_arabic_legal_llm",
                   "rett_regulation_legal_llm_001_015.json")
N = 15
KEY_RE = r"rett_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 15, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
STATUS = "ZATCA_PORTAL_PRIMARY_TWO_PIPELINE_OCR_X_SECONDARY_CROSS_VERIFIED"
EXPECTED_CHAPTERS = 0
FLAGGED_DISCREPANCY_KEYS = {
    "rett_regulation_predecessor_amendment_misattribution",
    "rett_regulation_predecessor_ministerial_resolution_712",
    "rett_regulation_three_distinct_dates",
    "rett_regulation_no_boe_lawid",
    "rett_regulation_uqn_and_wayback_unreachable",
    "rett_regulation_ocr_two_pipeline_extraction",
}
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
    for p in (SRC, RECORDS, SUMMARY, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1

    e = []
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    if src.get("article_count") != N:
        e.append("[1] article_count field %r != %d" % (src.get("article_count"), N))
    seen = set()
    for k in arts:
        m = re.match(KEY_RE, k)
        if not m:
            e.append("[1] %s: does not match key pattern" % k)
        else:
            seen.add(int(m.group(1)))
    if seen != set(range(1, N + 1)):
        e.append("[1] article numbers not a clean 1..%d run: %s" % (N, sorted(seen)))

    chapters = src.get("chapter_structure")
    if chapters != [] or len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected empty (flat) chapter_structure, got %r" % (chapters,))

    if src.get("consolidated_amended_law") is not False:
        e.append("[1d] consolidated_amended_law must be False for this brand-new regulation")

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
        if a.get("section_ar", "") != "":
            e.append("[2] %s: section_ar must be empty (flat regulation, no chapters)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if a.get("history"):
            e.append("[2] %s: brand-new regulation must have no amendment history" % k)
        if ls != "اصلية":
            e.append("[2] %s: every article must be اصلية in this un-amended regulation" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the tier")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    if not src.get("predecessor_regulation", {}).get("decree_date_hijri"):
        e.append("[2f] missing predecessor_regulation cross-reference (Ministerial "
                 "Resolution 712)")
    if not src.get("parent_law", {}).get("law_key") == "rett":
        e.append("[2g] missing/incorrect parent_law cross-reference to rett_law")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: unknown article_key" % r["article_key"]); continue
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("is_amended") or r.get("is_repealed") or r.get("is_added"):
            e.append("[4] %s: unexpected amended/repealed/added flag" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts mismatch with source")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: unknown article_key" % r["article_key"]); continue
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in RETT Implementing Regulation track:" % len(e))
        for x in e[:25]:
            print("  - %s" % x)
        return 1
    print("PASS: RETT Implementing Regulation — 15 records (15 اصلية, flat / no chapters)")
    print("  - TIER: zatca.gov.sa primary PDF (Tesseract OCR x PyMuPDF geometric "
          "two-pipeline reconciliation) x")
    print("    snadlaw.sa + qanoonsa.com secondary cross-verification")
    print("  - IN-FORCE ZATCA Board Decision 01-03-25 (24/09/1446H = 24 Mar 2025G); "
          "brand-new 2025 instrument, no amendments confirmed")
    print("  - CORRECTED prior-research premise: spa.gov.sa/N2095607 (May 2024) predates "
          "this Regulation by 11 months and")
    print("    describes an amendment of the different predecessor Ministerial "
          "Resolution (712, 15/2/1442H), not of this Regulation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
