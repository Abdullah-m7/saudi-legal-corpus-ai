#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Whistleblower/Witness/Expert/Victim Protection Law's
Implementing Regulation track (12 records).

Trust gate: this instrument is EXTREMELY recent (Council of Ministers decision (892),
19 May 2026 / 2/12/1447H; corrected/final gazette printing 12 June 2026, issue 5163)
and was independently verified against TWO hash-recorded primary-source Umm Al-Qura
gazette PDFs (issue 5162 draft + issue 5163 correction), not against independent
secondary legal commentary (none was found for the final 12-article text — all
located secondary coverage reflects the superseded 11-article draft and, in several
cases, an incorrect decision number). Every article therefore carries verification
status UQN_GAZETTE_PDF_CROSS_VERIFIED_HTML_MIRROR rather than the base law's simple
MATCHES_PDF, and the track is classified TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE
(see whistleblower_regulation_verified_summary.json) rather than TIER_2 — an honest,
lower-confidence classification driven by recency and the lack of independent
secondary corroboration of the final text, not by any doubt in the primary-source
gazette PDFs themselves, which were cross-checked directly. Articles are numbered by
ordinal position 1..12 (no مكرر); the 2024 argaam.com public-consultation draft is
explicitly NOT used anywhere in this track. Tatweel is banned EXCEPT the 'هـ'
digraph and space-bounded enumerator dashes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "whistleblower_regulation", "law", "official_source",
                   "whistleblower_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "whistleblower_regulation", "law", "verified",
                       "whistleblower_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "whistleblower_regulation", "law", "verified",
                       "whistleblower_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "whistleblower_regulation_arabic_legal_llm",
                   "whistleblower_regulation_legal_llm_001_012.json")
PDF_DRAFT = os.path.join(ROOT, "inputs", "whistleblower_regulation_official_pdfs",
                         "uqn_gazette_5162_20260605_draft.pdf")
PDF_FINAL = os.path.join(ROOT, "inputs", "whistleblower_regulation_official_pdfs",
                         "uqn_gazette_5163_20260612_corrected.pdf")
STATUS = "UQN_GAZETTE_PDF_CROSS_VERIFIED_HTML_MIRROR"
N = 12
KEY_RE = r"whistleblower_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 12}
TRUSTED = {STATUS}
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
    for p in (SRC, RECORDS, LLM, SUMMARY, PDF_DRAFT, PDF_FINAL):
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
    for k, a in arts.items():
        if a["status"] not in TRUSTED:
            e.append("[2] %s: UNTRUSTED status %r" % (k, a["status"]))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("معدلة") or sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected amended/repealed/added articles present (fresh issuance expected)")

    # [3] Committed gazette PDF hashes match provenance record (both issues)
    pubs = src["gazette_publications"]
    draft_hash = hashlib.sha256(open(PDF_DRAFT, "rb").read()).hexdigest()
    final_hash = hashlib.sha256(open(PDF_FINAL, "rb").read()).hexdigest()
    if draft_hash != pubs["original_draft_labeled_publication_SUPERSEDED"]["pdf_sha256"]:
        e.append("[3] committed draft (issue 5162) gazette PDF sha256 mismatch")
    if final_hash != pubs["corrected_final_publication_GOVERNING"]["pdf_sha256"]:
        e.append("[3] committed corrected (issue 5163) gazette PDF sha256 mismatch")
    if pubs["corrected_final_publication_GOVERNING"]["article_count_in_this_printing"] != N:
        e.append("[3] governing gazette printing article count metadata != %d" % N)

    # [3b] Council of Ministers decision number sanity: must be 892 (independently
    # re-verified against the primary gazette text), not the 893 some secondary
    # sources report -- this is the whole point of the discrepancy documentation.
    if src["council_of_ministers_decision"]["number"] != "892":
        e.append("[3b] decision number drifted from the primary-source-verified value (892)")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("official_text_status") != STATUS:
            e.append("[4] %s: bad status" % r["article_key"])
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

    # [6] Summary layer sanity + tier honesty check
    summ = json.load(open(SUMMARY, encoding="utf-8"))
    if summ.get("record_count") != N:
        e.append("[6] summary record_count != %d" % N)
    if summ.get("tier") not in ("TIER_3_SECONDARY_MULTI_SOURCE_ONLY",
                                "TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE"):
        e.append("[6] tier is not honestly downgraded for this extremely recent, thinly "
                 "secondary-corroborated instrument (expected TIER_3 or TIER_4)")
    if not summ.get("known_unresolved_discrepancies"):
        e.append("[6] known_unresolved_discrepancies missing/empty")

    if e:
        print("FAIL: %d error(s) in Whistleblower Regulation track:" % len(e))
        for x in e[:20]:
            print("  - %s" % x)
        return 1
    print("PASS: Whistleblower Regulation — 12 records (fresh issuance: all 12 اصلية)")
    print("  - trust gate: all 12 articles UQN_GAZETTE_PDF_CROSS_VERIFIED_HTML_MIRROR against "
          "2 hash-recorded primary gazette PDFs (issue 5162 draft + issue 5163 correction)")
    print("  - numbered 1..12 by ordinal position (no مكرر); Council of Ministers decision "
          "(892) independently re-verified against the primary gazette text")
    print("  - IN-FORCE per Council of Ministers decision (892), 2/12/1447H; corrected/final "
          "gazette printing issue 5163 (12 June 2026); Arabic governs; TIER: %s" % summ.get("tier"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
