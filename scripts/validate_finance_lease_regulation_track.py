#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Finance Lease
Law track (32 records, 3 Parts: الباب الأول 1-2 | الباب الثاني 3-11 |
الباب الثالث 12-32; 29 اصلية + 3 معدلة -- Articles 10, 17 and 25, all
amended by the SAME Governor's Decision No. 93/م ش ت dated 18/10/1441H).

VERIFICATION TIER -- see the generator's module docstring and
sources/finance_lease_regulation/law/official_source/
finance_lease_regulation_official_source.json's verification_methodology_note
for the full account. This validator asserts: exactly 32 articles in a clean
1..32 run; exactly 3 non-empty chapter_structure entries (Parts, not
chapters/فصول -- this Regulation uses أبواب); every article carries a
non-empty section_ar (Part label: title); exactly Articles 10, 17 and 25 are
معدلة with non-empty amendment history, and every other article is اصلية
with empty history; no ملغاة/مضافة articles (none confirmed)."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "finance_lease_regulation", "law", "official_source",
                   "finance_lease_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "finance_lease_regulation", "law", "verified",
                       "finance_lease_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "finance_lease_regulation", "law", "verified",
                       "finance_lease_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "finance_lease_regulation_arabic_legal_llm",
                   "finance_lease_regulation_legal_llm_001_032.json")
N = 32
KEY_RE = r"finance_lease_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 29, "معدلة": 3, "ملغاة": 0, "مضافة": 0}
AMENDED_ARTICLE_NUMBERS = {10, 17, 25}
STATUS = "SAMA_RULEBOOK_PRIMARY_AR_EN_BILINGUAL_X_AMENDMENT_DECISION_NODE_CROSS_VERIFIED"
EXPECTED_CHAPTERS = 3
FLAGGED_DISCREPANCY_KEYS = {
    "finance_lease_regulation_amendment_scope_correction_article_25",
    "finance_lease_regulation_pre_amendment_text_not_recovered",
    "finance_lease_regulation_central_bank_rename_footnote_not_a_textual_amendment",
    "finance_lease_regulation_promulgating_instrument_type",
    "finance_lease_regulation_no_boe_lawid_regulation_level",
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
    if not chapters or len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d Part (باب) entries in chapter_structure, got %r"
                 % (EXPECTED_CHAPTERS, chapters))
    else:
        expected_spans = {"1-2", "3-11", "12-32"}
        got_spans = {c.get("articles") for c in chapters}
        if got_spans != expected_spans:
            e.append("[1c] chapter_structure article spans %r != expected %r"
                     % (got_spans, expected_spans))
        for c in chapters:
            if not c.get("label_ar", "").startswith("الباب"):
                e.append("[1c] chapter label %r does not use الباب (Part)" % c.get("label_ar"))

    if src.get("consolidated_amended_law") is not False:
        e.append("[1d] consolidated_amended_law must be False for this track")

    sc = Counter()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
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
            e.append("[2] %s: section_ar must be non-empty (this Regulation has 3 أبواب)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)

        expect_amended = n in AMENDED_ARTICLE_NUMBERS
        if expect_amended:
            if ls != "معدلة":
                e.append("[3] %s: article %d must be معدلة (confirmed amendment)" % (k, n))
            if not a.get("history"):
                e.append("[3] %s: amended article %d must carry non-empty history" % (k, n))
            else:
                for h in a["history"]:
                    if h.get("pre_amendment_text_recovered") is not False:
                        e.append("[3] %s: history entry must explicitly disclose "
                                 "pre_amendment_text_recovered=false (not recovered this pass)" % k)
                    if "93" not in h.get("instrument", ""):
                        e.append("[3] %s: history entry must cite Decision 93/م ش ت" % k)
        else:
            if ls != "اصلية":
                e.append("[3] %s: article %d expected اصلية, got %r" % (k, n, ls))
            if a.get("history"):
                e.append("[3] %s: non-amended article %d must have empty history" % (k, n))

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

    if not src.get("parent_law", {}).get("law_key") == "finance_lease":
        e.append("[2g] missing/incorrect parent_law cross-reference to finance_lease (base Law)")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: unknown article_key" % r["article_key"]); continue
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation', got %r"
                     % (r["article_key"], r.get("law_component")))
        if "article_number" not in r:
            e.append("[4] %s: missing article_number field" % r["article_key"])
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        n = int(re.match(KEY_RE, r["article_key"]).group(1))
        expect_amended = n in AMENDED_ARTICLE_NUMBERS
        if r.get("is_amended") != expect_amended:
            e.append("[4] %s: is_amended flag mismatch (expected %r)" % (r["article_key"], expect_amended))
        if r.get("is_repealed") or r.get("is_added"):
            e.append("[4] %s: unexpected repealed/added flag" % r["article_key"])
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
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation', got %r"
                     % (r["article_key"], r.get("law_component")))
        if "article_number" not in r:
            e.append("[5] %s: missing article_number field" % r["article_key"])
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
        print("FAIL: %d error(s) in Finance Lease Regulation track:" % len(e))
        for x in e[:25]:
            print("  - %s" % x)
        return 1
    print("PASS: Finance Lease Implementing Regulation — 32 records "
          "(29 اصلية, 3 معدلة: Articles 10/17/25, 0 ملغاة, 0 مضافة; 3 أبواب)")
    print("  - TIER: rulebook.sama.gov.sa primary (Arabic/English bilingual, born-digital HTML) x")
    print("    dedicated amendment-decision node (3243) cross-verification")
    print("  - IN-FORCE Administrative Decision 1/م ش ت (14/4/1434H = 24/2/2013G)")
    print("  - CORRECTED prior-research premise: Governor's Decision 93/م ش ت (18/10/1441H) "
          "amends THREE provisions")
    print("    (Art. 10§3, Art. 17, Art. 25§2), not just the two (Art. 10§3, Art. 17) named "
          "in the commissioning brief")
    print("  - Pre-amendment wording of all three provisions NOT recoverable this pass "
          "(disclosed, not fabricated)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
