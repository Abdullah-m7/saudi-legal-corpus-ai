#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Anti-Commercial Fraud Law track (30 records,
consolidated amended law: 25 اصلية / 5 معدلة / 0 ملغاة / 0 مضافة, 5 فصول).

SOURCING TIER — SECONDARY_MULTI_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE — see
the generator's module docstring and
sources/anti_fraud/law/official_source/anti_fraud_law_official_source.json's
verification_methodology_note for the full caveat. laws.boe.gov.sa is
confirmed unreachable (HTTP 503, retried twice this pass at two URL
forms); the governing current text rests on three cross-verified
secondary sources. This validator checks internal consistency and that
every article carries the sourcing-tier status tag; it CANNOT verify
against a primary source the build environment cannot reach."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "anti_fraud", "law", "official_source",
                   "anti_fraud_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "anti_fraud", "law", "verified",
                       "anti_fraud_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "anti_fraud_arabic_legal_llm",
                   "anti_fraud_law_legal_llm_001_030.json")
N = 30
KEY_RE = r"anti_fraud_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 25, "معدلة": 5}
STATUS = "SECONDARY_MULTI_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE"
AMENDED_KEYS = {"anti_fraud_art_005", "anti_fraud_art_013",
                "anti_fraud_art_023", "anti_fraud_art_025",
                "anti_fraud_art_027"}
EXPECTED_CHAPTER_COUNT = 5
FLAGGED_DISCREPANCY_KEYS = {
    "anti_fraud_art5_second_amendment_citation_disputed",
    "anti_fraud_art5_reconstructed_consolidated_text",
    "anti_fraud_mohamah_missing_article15",
    "anti_fraud_ministry_name_staleness",
    "anti_fraud_art12_prosecution_authority_staleness",
    "anti_fraud_penalty_amounts_unchanged_since_2008",
    "anti_fraud_draft_consumer_protection_law_unenacted",
    "anti_fraud_implementing_regulation_out_of_scope",
    "anti_fraud_boe_unreachable",
    "anti_fraud_uqn_gazette_dead_links",
    "anti_fraud_com_decision_107_1435h_enabling_instrument",
    "anti_fraud_research_summary_off_by_one_corrected",
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
    for k in AMENDED_KEYS:
        if k not in arts:
            e.append("[1] expected article key %s missing" % k)

    cs = src.get("chapter_structure") or []
    if len(cs) != EXPECTED_CHAPTER_COUNT:
        e.append("[1c] expected %d chapters, got %d" % (EXPECTED_CHAPTER_COUNT, len(cs)))
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
            e.append("[1] %s: unexpected is_mukarrar=True (this law has no مكرر articles)" % k)
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
        if not a.get("section_ar", "").startswith("الفصل"):
            e.append("[2] %s: missing/malformed chapter section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if k in AMENDED_KEYS and not a.get("original_1429h_text"):
            e.append("[2] %s: amended article missing original_1429h_text for provenance" % k)
        if k not in AMENDED_KEYS and a.get("original_1429h_text"):
            e.append("[2] %s: unamended article should not carry an original_1429h_text" % k)

    if seen_numbers != set(range(1, N + 1)):
        e.append("[1] article numbers not a clean 1..%d sequence: missing %s, extra %s" %
                  (N, sorted(set(range(1, N + 1)) - seen_numbers),
                   sorted(seen_numbers - set(range(1, N + 1)))))

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
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
        print("FAIL: %d error(s) in Anti-Commercial Fraud Law track:" % len(e))
        for x in e[:30]:
            print("  - %s" % x)
        return 1
    print("PASS: Anti-Commercial Fraud Law — 30 records (consolidated: 25 اصلية / 5 معدلة)")
    print("  - SOURCING TIER: three cross-verified secondary sources (nezams.com,")
    print("    mustsharik.com, mohamah.net); laws.boe.gov.sa confirmed unreachable (HTTP 503)")
    print("  - numbered 1..30 across 5 فصول (chapters)")
    print("  - IN-FORCE Royal Decree M/19 (23/4/1429H); arts 5 (amended twice), 13, 23, 25, 27")
    print("    amended, original pre-amendment wording preserved as provenance")
    print("  - flagged: Article 5's disputed second-amendment citation (CoM 508 vs M/76),")
    print("    its mechanically-spliced current text, mohamah.net's missing Article 15,")
    print("    ministry-name/prosecution-authority staleness, and the unenacted draft")
    print("    Consumer Protection Law")
    return 0


if __name__ == "__main__":
    sys.exit(main())
