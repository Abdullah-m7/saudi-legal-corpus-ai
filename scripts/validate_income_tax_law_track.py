#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Income Tax Law track (81 records, consolidated
amended law: 52 اصلية / 29 معدلة, 16 chapters).

DISTINCT VERIFICATION TIER — see the generator's module docstring and
sources/income_tax/law/official_source/income_tax_law_official_source.json's
verification_methodology_note for the full caveat. IMPORTANT: this
validator does NOT require original_1425h_text on any of the 29 معدلة
articles — the research pass explicitly did not deliver pre-amendment
original text to primary-source confidence for any article this pass (a
documented gap, not a fabrication), which also distinguishes this track
from the mixed-tier Capital Market / Trademark tracks where
original-text provenance is mandatory. Chapter 10 (Articles 44-55) is
independently confirmed to have NO recoverable pre-M/70 (1425H) text in
any of the four sources checked."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "income_tax", "law", "official_source",
                   "income_tax_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "income_tax", "law", "verified",
                       "income_tax_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "income_tax_arabic_legal_llm",
                   "income_tax_law_legal_llm_001_081.json")
N = 81
KEY_RE = r"income_tax_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 52, "معدلة": 29}
STATUS = "BOE_WAYBACK_X_ZATCA_PDF_X_GSTC_PDF_X_NEZAMS_CROSS_VERIFIED_CH10_BOE_ONLY"
EXPECTED_CHAPTERS = 16
AMENDED_KEYS = {"income_tax_art_%03d" % n for n in
                set((1, 2, 6, 7, 8, 9, 12, 13, 17, 21, 43, 56, 59, 63, 65, 66, 67))
                | set(range(44, 56))}
FLAGGED_DISCREPANCY_KEYS = {
    "income_tax_art_066_m52_date_conflict",
    "income_tax_chapter10_zatca_gstc_incomplete",
    "income_tax_boe_default_body_staleness",
    "income_tax_zatca_footnotes_exceed_boe_flags",
    "income_tax_nezams_stale_post_1438h",
    "income_tax_gazette_publication_date_single_sourced",
    "income_tax_art_066_paragraph_deletions_single_sourced",
    "income_tax_art_021_006_007_added_paragraphs_zatca_only",
    "income_tax_implementing_regulation_date_not_pinned_down",
    "income_tax_art_003b_ministerial_resolution_2194_not_an_amendment",
    "income_tax_original_1425h_text_not_populated_despite_claim",
    "income_tax_administering_authority_terminology_anachronism",
    "income_tax_boe_wayback_snapshot_age",
    "income_tax_preamble_ar_not_verbatim",
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
    if src.get("article_count") != N:
        e.append("[1] article_count field != %d" % N)
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)
    for k in AMENDED_KEYS:
        if k not in arts:
            e.append("[1] expected amended article key %s missing" % k)

    chapters = src.get("chapter_structure") or []
    if len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d chapters, got %d" % (EXPECTED_CHAPTERS, len(chapters)))

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
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (expected a فصل/chapter title)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected repealed/added articles present")

    # Article 66 must carry its documented dual-date M/52 conflict verbatim
    # in its own history rather than silently picking one date.
    art66 = arts.get("income_tax_art_066", {})
    hist66_dates = " ".join(h.get("date_hijri", "") for h in art66.get("history", []))
    if "28/4/1441" not in hist66_dates or "28/7/1441" not in hist66_dates:
        e.append("[2g] income_tax_art_066: expected both candidate M/52 dates "
                 "(28/4/1441H and 28/7/1441H) recorded in history, not silently resolved")

    # Article 48 must carry its full IRR-to-rate lookup table, unabridged.
    art48_text = arts.get("income_tax_art_048", {}).get("text", "")
    if art48_text.count("→") < 100:
        e.append("[2h] income_tax_art_048: expected IRR-to-rate table with "
                 "~100 row entries ('→' markers), found %d" % art48_text.count("→"))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
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
        if r.get("original_1425h_text") != a.get("original_1425h_text"):
            e.append("[4] %s: original_1425h_text not propagated" % r["article_key"])
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
        print("FAIL: %d error(s) in Income Tax Law track:" % len(e))
        for x in e[:30]:
            print("  - %s" % x)
        return 1
    print("PASS: Income Tax Law — 81 records (52 اصلية / 29 معدلة, 16 chapters)")
    print("  - DISTINCT TIER: BOE (Wayback) x ZATCA PDF x gstc.gov.sa PDF x nezams.com")
    print("    cross-verified for 69/81 articles; Chapter 10 (Arts. 44-55) BOE + nezams.com")
    print("    only (ZATCA/gstc both print a bare repeal notice for that chapter)")
    print("  - IN-FORCE Royal Decree M/1 (15/1/1425H); amended by M/113, M/131, M/70,")
    print("    M/52, M/153")
    print("  - no original_1425h_text populated for any article this pass, a documented")
    print("    gap not a fabrication")
    print("  - Article 66 carries an unresolved dual-date conflict for Royal Decree M/52")
    print("    (28/4/1441H per ZATCA vs 28/7/1441H per BOE) — both dates recorded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
