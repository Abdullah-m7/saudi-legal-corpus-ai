#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Anti-Commercial
Fraud Law track (19 records, all اصلية / 0 معدلة / 0 ملغاة / 0 مضافة, 11
heading groups).

SOURCING TIER -- TIER 3, SECONDARY_SINGLE_SOURCE_VERBATIM_PARTIAL_CROSS_CHECK_
BOE_UNREACHABLE -- see the generator's module docstring and
sources/anti_fraud_regulation/law/official_source/anti_fraud_regulation_official_source.json's
verification_methodology_note for the full caveat. laws.boe.gov.sa,
mc.gov.sa, and ncar.gov.sa are all confirmed unreachable this pass; the
governing current text rests on ONE verbatim-reliable secondary source
(nezams.com), with a second source (mrksa.net) providing structural
corroboration only after two substantive divergences were found in its text.
This validator checks internal consistency and that every article carries
the sourcing-tier status tag; it CANNOT verify against a primary source the
build environment cannot reach."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "anti_fraud_regulation", "law", "official_source",
                   "anti_fraud_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "anti_fraud_regulation", "law", "verified",
                       "anti_fraud_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "anti_fraud_regulation_arabic_legal_llm",
                   "anti_fraud_regulation_legal_llm_001_019.json")
N = 19
KEY_RE = r"anti_fraud_reg_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 19}
STATUS = "SECONDARY_SINGLE_SOURCE_VERBATIM_PARTIAL_CROSS_CHECK_BOE_UNREACHABLE"
EXPECTED_CHAPTER_COUNT = 11
FLAGGED_DISCREPANCY_KEYS = {
    "afr_issuing_instrument_number_date_disputed",
    "afr_mrksa_ai_regeneration_risk_two_divergences_found",
    "afr_boe_page_not_located_separately",
    "afr_mc_gov_sa_and_ncar_gov_sa_unreachable",
    "afr_wayback_availability_yes_content_fetch_no",
    "afr_almoaqeb_com_unreachable",
    "afr_qanoniah_com_js_rendered_unreadable",
    "afr_manielaw_pdf_missing_regulation_text",
    "afr_bttat3_blogspot_different_older_regulation",
    "afr_stale_relative_to_law_article5_amendments",
    "afr_html_transcription_artifacts_corrected",
    "afr_no_formal_amendments_recorded",
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

    cs = src.get("chapter_structure") or []
    if len(cs) != EXPECTED_CHAPTER_COUNT:
        e.append("[1c] expected %d chapter/heading groups, got %d" % (EXPECTED_CHAPTER_COUNT, len(cs)))
    for c in cs:
        if "section_ar" not in c or "first_article" not in c or "last_article" not in c:
            e.append("[1c] malformed chapter_structure entry: %r" % (c,))

    def in_some_chapter(n):
        return any(c["first_article"] <= n <= c["last_article"] for c in cs)

    sc = Counter()
    seen_numbers = set()
    for k, a in arts.items():
        m = re.match(KEY_RE, k)
        n = int(m.group(1))
        seen_numbers.add(n)
        if a.get("is_mukarrar"):
            e.append("[1] %s: unexpected is_mukarrar=True (this regulation has no مكرر articles)" % k)
        if not in_some_chapter(n):
            e.append("[1c] %s: article number %d not covered by any chapter range" % (k, n))

        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar", "").strip():
            e.append("[2] %s: missing section_ar heading" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if a.get("history"):
            e.append("[2] %s: unexpected non-empty history (no amendments recorded for this "
                      "regulation)" % k)

    if seen_numbers != set(range(1, N + 1)):
        e.append("[1] article numbers not a clean 1..%d sequence: missing %s, extra %s" %
                  (N, sorted(set(range(1, N + 1)) - seen_numbers),
                   sorted(seen_numbers - set(range(1, N + 1)))))

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("معدلة"):
        e.append("[2] unexpected amended articles present")
    if sc.get("ملغاة"):
        e.append("[2] unexpected repealed articles present")
    if sc.get("مضافة"):
        e.append("[2] unexpected added articles present")

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the sourcing tier")
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
        print("FAIL: %d error(s) in Anti-Commercial Fraud Regulation track:" % len(e))
        for x in e[:30]:
            print("  - %s" % x)
        return 1
    print("PASS: Anti-Commercial Fraud Regulation — 19 records (all اصلية)")
    print("  - SOURCING TIER: TIER 3 -- single verbatim-reliable secondary source (nezams.com);")
    print("    laws.boe.gov.sa, mc.gov.sa, ncar.gov.sa confirmed unreachable; mrksa.net used for")
    print("    structural cross-check only after two substantive divergences were found")
    print("  - numbered 1..19 across 11 heading groups (8 numbered فصول + 3 unnumbered)")
    print("  - IN-FORCE Ministerial Resolution implementing Royal Decree M/19 (23/4/1429H);")
    print("    issuing-instrument citation itself disputed (155/6-1-1431H vs 55/20-10-1431H)")
    print("    and recorded transparently rather than silently resolved")
    print("  - flagged: disputed issuing citation, mrksa.net AI-regeneration risk, BOE/mc.gov.sa/")
    print("    ncar.gov.sa/almoaqeb.com/qanoniah.com unreachability, staleness relative to the")
    print("    base law's own Article 5 amendments, and corrected HTML-transcription artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
