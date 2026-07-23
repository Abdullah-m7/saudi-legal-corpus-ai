#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Real Estate Transaction Tax Law track
(20 records, brand-new original law: 20 اصلية, flat — no chapters).

VERIFICATION TIER — see the generator's module docstring and
sources/rett/law/official_source/rett_law_official_source.json's
verification_methodology_note for the full account. This is a NEW 2024
statute (Royal Decree M/84, 19/3/1446H) with NO amendments to date, so —
unlike the consolidated VAT/income-tax tracks — this validator asserts
that every article is اصلية, that there are NO معدلة/ملغاة/مضافة articles,
and that no amendment_history is present. It also asserts the Law is FLAT
(chapter_structure empty; section_ar empty on every article), because the
Law genuinely has no فصل/باب subdivisions (documented, not an omission)."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "rett", "law", "official_source",
                   "rett_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "rett", "law", "verified",
                       "rett_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "rett_arabic_legal_llm",
                   "rett_law_legal_llm_001_020.json")
N = 20
KEY_RE = r"rett_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 20, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
STATUS = "BOE_PORTAL_PRIMARY_X_SECONDARY_CROSS_VERIFIED"
EXPECTED_CHAPTERS = 0
FLAGGED_DISCREPANCY_KEYS = {"rett_generic_repeal_not_named", "rett_predecessor_royal_order",
                            "rett_no_chapter_structure", "rett_boe_live_page_503",
                            "rett_wayback_unreachable", "rett_publication_and_effective_date"}
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
        e.append("[1d] consolidated_amended_law must be False for this brand-new law")

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
            e.append("[2] %s: section_ar must be empty (flat law, no chapters)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if a.get("history"):
            e.append("[2] %s: brand-new law must have no amendment history" % k)
        if ls != "اصلية":
            e.append("[2] %s: every article must be اصلية in this un-amended law" % k)

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

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
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
        print("FAIL: %d error(s) in RETT Law track:" % len(e))
        for x in e[:25]:
            print("  - %s" % x)
        return 1
    print("PASS: Real Estate Transaction Tax Law — 20 records (20 اصلية, flat / no chapters)")
    print("  - TIER: BOE portal primary text (via r.jina.ai after live 503) x")
    print("    nezams.com + qanoonsa.com secondary cross-verification")
    print("  - IN-FORCE Royal Decree M/84 (19/3/1446H); brand-new 2024 statute, no amendments")
    print("  - Article 20(2) repeal is GENERIC (not named); predecessor Royal Order A/84")
    print("    (14/2/1442H) recorded as context, not asserted as a Law-text named repeal")
    return 0


if __name__ == "__main__":
    sys.exit(main())
