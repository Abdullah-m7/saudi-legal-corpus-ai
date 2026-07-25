#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Electronic
Transactions Law track (25 records, all اصلية, 8 chapters, no مكرر).

VERIFICATION TIER -- see the generator's module docstring and sources/
electronic_transactions_regulation/law/official_source/
electronic_transactions_regulation_official_source.json's
verification_methodology_note for the full account: the Official Umm al-Qura
Gazette (uqn.gov.sa) is the PRIMARY source (fetched directly, HTTP 200,
server-rendered full text); dga.gov.sa (the issuing authority) and
laws.boe.gov.sa were both unreachable this pass; cross-checked word-for-word
against an independent press source (argaam.com) for two full articles ->
TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED. This validator does not
re-adjudicate provenance; it only checks internal self-consistency and that
every documented discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "electronic_transactions_regulation", "law", "official_source",
                   "electronic_transactions_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "electronic_transactions_regulation", "law", "verified",
                       "electronic_transactions_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "electronic_transactions_regulation", "law", "verified",
                       "electronic_transactions_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "electronic_transactions_regulation_arabic_legal_llm",
                   "electronic_transactions_regulation_legal_llm_001_025.json")
N = 25
KEY_RE = r"electronic_transactions_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 25, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
STATUS = "UQN_GAZETTE_OFFICIAL_PRIMARY_X_ARGAAM_PRESS_CROSSCHECK_DGA_BOE_UNREACHABLE"
TIER = "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED"
AMENDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
EXPECTED_CHAPTERS = 8
AR = "ء-ي"
FLAGGED_DISCREPANCY_KEYS = {
    "electronic_transactions_regulation_dga_portal_unreachable",
    "electronic_transactions_regulation_boe_unreachable",
    "electronic_transactions_regulation_wayback_content_blocked",
    "electronic_transactions_regulation_eparticipation_portal_unreachable",
    "electronic_transactions_regulation_board_decision_date_transposition",
    "electronic_transactions_regulation_predecessor_1429h_not_ingested",
    "electronic_transactions_regulation_gazette_issue_number_inferred",
    "electronic_transactions_regulation_decision_vs_publication_date",
    "electronic_transactions_regulation_diacritics_preserved_verbatim",
    "electronic_transactions_regulation_numbering_spacing_irregular",
}


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
        if a.get("verification_tier") != TIER:
            e.append("[2] %s: expected verification_tier %r, got %r"
                     % (k, TIER, a.get("verification_tier")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar", "").strip():
            e.append("[2] %s: chapter-aware regulation missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if k in REPEALED_KEYS and not a.get("history"):
            e.append("[2] %s: repealed article missing amendment_history" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    disc = src.get("known_unresolved_discrepancies", [])
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    found_keys = {d.get("article_key") for d in disc}
    missing_disc = FLAGGED_DISCREPANCY_KEYS - found_keys
    if missing_disc:
        e.append("[2e] expected discrepancy keys missing: %s" % sorted(missing_disc))

    if not src.get("base_law"):
        e.append("[2f] missing base_law cross-reference to sources/electronic_transactions/")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: article_key not found in source" % r["article_key"])
            continue
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("verification_tier") != a.get("verification_tier"):
            e.append("[4] %s: verification_tier mismatch" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        src_a = arts.get(r["article_key"])
        if src_a is None:
            e.append("[5] %s: article_key not found in source" % r["article_key"])
            continue
        if r["article_text_ar"] != src_a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Electronic Transactions Regulation track:" % len(e))
        for x in e[:20]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Electronic Transactions Law — 25 records "
          "(all اصلية)")
    print("  - TIER: %s -- Official Umm al-Qura Gazette (uqn.gov.sa) primary source, dga.gov.sa "
          "and laws.boe.gov.sa unreachable, cross-checked word-for-word against an independent "
          "press source (argaam.com)" % TIER)
    print("  - numbered 1..25 across 8 chapters; issued by DGA Board Decision M-8-6 (3 Ramadan "
          "1445H / 13 March 2024) following Council of Ministers Resolution 293's substitution "
          "of DGA for CITC in the base law (electronic_transactions track)")
    print("  - Board-decision-date transposition ('9/3/1445H' vs the resolved '3 Ramadan "
          "1445H') and the un-ingested 1429H predecessor regulation are disclosed, not silently "
          "resolved -- see known_unresolved_discrepancies")
    return 0


if __name__ == "__main__":
    sys.exit(main())
