#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Premium Residency Regulation track (اللائحة
التنفيذية لنظام الإقامة المميزة, Premium Residency Center Board Decision No.
7-5-1444 dated 29/12/1444H, amending the Center's own founding Decision No.
4-1440 dated 20/9/1440H).

13 ingested records: 1 اصلية (Article 7, confirmed byte-for-byte identical to
the original 1440H text), 12 معدلة (Articles 1-6 and 8-9 confirmed changed by
direct comparison against the recovered original 1440H text; Articles 10-13
classified معدلة by disclosed inference only -- the qanoniah.com paywall
prevented direct original-text comparison for this range, see the source
artifact's known_unresolved_discrepancies). 0 ملغاة, 0 مضافة.

VERIFICATION TIER: TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE -- ncar.gov.sa,
laws.boe.gov.sa, and pr.gov.sa (the Center's own official portal) were all
unreachable this pass (independently confirmed via direct curl, WebFetch/
proxy, and r.jina.ai reader-proxy). This track rests entirely on two private
secondary sources: qanoniah.com (verbatim, but subscription-gated beyond 10
free items -- Articles 1-5 only) and aunklaw.com (verbatim, all 13 articles).
Articles 1-5 carry genuine word-for-word cross-verification between the two;
Articles 6-13 rest on aunklaw.com alone, with zero official corroboration.
Per this corpus's own methodology (reports/verification_tiers/
VERIFICATION_TIERS_METHODOLOGY_AR.md), a mixed-confidence track is graded by
its WEAKEST part, not its strongest -- hence TIER_4, not TIER_3.

This validator does not re-adjudicate any of this; it only checks internal
self-consistency of the text this track actually ingests, and that every
discrepancy found is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "premium_residency_regulation", "law", "official_source",
                   "premium_residency_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "premium_residency_regulation", "law", "verified",
                       "premium_residency_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "premium_residency_regulation", "law", "verified",
                       "premium_residency_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "premium_residency_regulation_arabic_legal_llm",
                   "premium_residency_regulation_legal_llm_001_013.json")
N_TOTAL = 13
KEY_RE = r"premium_residency_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 1, "معدلة": 12, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_SECTIONS = 11  # thematic sections, no formal أبواب/فصول
STATUS_1_5 = ("PREMIUM_RESIDENCY_REGULATION_QANONIAH_X_AUNKLAW_VERBATIM_CROSS_VERIFIED_"
              "NCAR_BOE_PRGOV_UNREACHABLE")
STATUS_6_13 = ("PREMIUM_RESIDENCY_REGULATION_AUNKLAW_SOLE_VERBATIM_SOURCE_QANONIAH_"
               "PAYWALLED_BEYOND_ART5_NCAR_BOE_PRGOV_UNREACHABLE")
AMENDED_KEYS = {"premium_residency_regulation_art_%03d" % n
                for n in (1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13)}
REPEALED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
FLAGGED_DISCREPANCY_KEYS = {
    "premium_residency_regulation_ncar_unreachable",
    "premium_residency_regulation_boe_not_indexed_and_unreachable",
    "premium_residency_regulation_prgov_official_portal_unreachable",
    "premium_residency_regulation_dual_secondary_source_only_tier4",
    "premium_residency_regulation_article3_product_naming_seam",
    "premium_residency_regulation_article6_stale_product_naming_cross_source_seam",
    "premium_residency_regulation_original_1440_partial_access_articles_11_14",
    "premium_residency_regulation_article8_law_article_cross_reference_anomaly",
    "premium_residency_regulation_preamble_not_available",
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


def _iter_section_ranges(chs):
    for ch in chs:
        lo, hi = (int(x) for x in ch["articles"].split("-"))
        yield (lo, hi)


def main():
    e = []
    for p in (SRC, RECORDS, SUMMARY, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    if len(arts) != N_TOTAL:
        e.append("[1] %d articles != %d" % (len(arts), N_TOTAL))
    if src.get("article_count") != N_TOTAL:
        e.append("[1] article_count field != %d" % N_TOTAL)
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_SECTIONS:
        e.append("[1c] expected %d thematic sections (no formal أبواب/فصول), "
                  "got %d" % (EXPECTED_TOP_LEVEL_SECTIONS, n_top))

    covered = set()
    for lo, hi in _iter_section_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one section range" % n)
            covered.add(n)
    if covered != set(range(1, N_TOTAL + 1)):
        missing = sorted(set(range(1, N_TOTAL + 1)) - covered)
        extra = sorted(covered - set(range(1, N_TOTAL + 1)))
        if missing:
            e.append("[1c] chapter_structure missing article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])

    sc = Counter()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
        expected_status = STATUS_1_5 if n <= 5 else STATUS_6_13
        if a.get("status") != expected_status:
            e.append("[2] %s: expected status %r, got %r" % (k, expected_status, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in (AMENDED_KEYS | REPEALED_KEYS | ADDED_KEYS) and not a.get("history"):
            e.append("[2] %s: amended/repealed/added article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if k not in (AMENDED_KEYS | REPEALED_KEYS | ADDED_KEYS) and a.get("history"):
            e.append("[2i] %s: unamended/non-added/non-repealed article must have empty "
                      "history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "‌" in a["text"] or "‍" in a["text"]:
            e.append("[2f] %s: residual zero-width joiner/non-joiner artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

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

    if not src.get("amendment_history"):
        e.append("[2k] missing amendment_history (must record the founding decision and "
                  "subsequent amendments)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        for token in ("4-1440", "7-5-1444"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference %s" % token)

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("premium_residency_regulation_art_001", {})
    if "المجلس: مجلس إدارة المركز" not in art1.get("text", ""):
        e.append("[2j] Article 1 must carry the current المجلس definition (regulation defines "
                 "its own terms independently of the base law's Article 1)")
    if "الوالدان" not in art1.get("text", "") and "الوالدين" not in art1.get("text", ""):
        e.append("[2j] Article 1's أسرة definition must reflect the current (1444H-amended) "
                 "wording including الوالدان/الوالدين")
    art3 = arts.get("premium_residency_regulation_art_003", {})
    if "دائمة" not in art3.get("text", "") or "منتجات الإقامة المميزة" not in art3.get("text", ""):
        e.append("[2j] Article 3 must carry the CURRENT (1444H-amended) دائمة/محددة المدة "
                 "residency types and the 7-product list")
    art7 = arts.get("premium_residency_regulation_art_007", {})
    if art7.get("legal_status_ar") != "اصلية":
        e.append("[2j] Article 7 must be legal_status_ar=اصلية (confirmed byte-for-byte "
                 "identical to the original 1440H text)")
    art13 = arts.get("premium_residency_regulation_art_013", {})
    if "اليوم التالي" not in art13.get("text", ""):
        e.append("[2j] Article 13 missing expected entry-into-force clause")
    if "premium_residency_regulation_art_014" in arts:
        e.append("[2j] this Regulation has exactly 13 ingested articles -- no Article 14 "
                 "should be present")
    if src.get("decree") != "قرار مجلس إدارة المركز رقم (7-5-1444)" or src.get("decree_date_hijri") != "29/12/1444":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Board Decision "
                 "7-5-1444, 29/12/1444H")
    if src.get("founding_decree") != "قرار مركز الإقامة المميزة رقم (4-1440)":
        e.append("[2j] founding_decree mismatch with verified Center Decision 4-1440")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (this track ingests the current, "
                 "post-amendment consolidated text)")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N_TOTAL:
        e.append("[4] %d verified records != %d" % (len(ver), N_TOTAL))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: article_key not found in source" % r["article_key"]); continue
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N_TOTAL:
        e.append("[4b] summary record_count != %d" % N_TOTAL)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N_TOTAL or len(recs) != N_TOTAL:
        e.append("[5] llm count != %d" % N_TOTAL)
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: article_key not found in source" % r["article_key"]); continue
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        n = int(re.match(KEY_RE, r["article_key"]).group(1))
        expected_status = STATUS_1_5 if n <= 5 else STATUS_6_13
        if r.get("source_trust", {}).get("source_status") != expected_status.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Premium Residency Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Premium Residency Regulation (اللائحة التنفيذية لنظام الإقامة المميزة)")
    print("  - 13 ingested records: 1 اصلية (Article 7, confirmed identical), 12 معدلة "
          "(6 confirmed by direct text comparison: 1-6; 2 confirmed with partial content-"
          "relocation evidence: 8-9; 4 by disclosed inference only: 10-13), 0 ملغاة, 0 مضافة")
    print("  - flat 13-article structure, no formal أبواب/فصول; 11 informal thematic sections "
          "for indexing only")
    print("  - VERIFICATION TIER: TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE -- ncar.gov.sa, "
          "laws.boe.gov.sa, and pr.gov.sa (Center's own portal) all unreachable this pass; "
          "Articles 1-5 cross-verified word-for-word between qanoniah.com and aunklaw.com; "
          "Articles 6-13 rest on aunklaw.com alone (paywall blocked qanoniah beyond 10 free "
          "items); graded by the weakest part per this corpus's own tier methodology")
    print("  - Board Decision 7-5-1444 (29/12/1444H), amending founding Decision 4-1440 "
          "(20/9/1440H); implementing regulation of the premium_residency track's law "
          "(Royal Decree M/106)")
    print("  - GENUINE ANOMALIES carried forward: Article 3 product-name/citation differs "
          "between qanoniah (دائمة, 2 CoEDA decisions) and aunklaw (غير محددة المدة, 1 "
          "decision) -- qanoniah adopted as governing; Article 6's fee table (aunklaw-only) "
          "still uses the older غير محدد المدة naming, a disclosed cross-source seam; Article "
          "8 cross-references \"المادة الثامنة من النظام\" for content matching the law's "
          "Article 9, not its (repealed) Article 8 -- preserved verbatim, not corrected")
    print("  - Original 1440H text partially recovered (Articles 1-10 via qanoniah.com); "
          "Articles 11-14 of the original could not be reached this pass (subscription "
          "paywall), so Articles 10-13 of the current text are classified معدلة by disclosed "
          "inference, not direct comparison")
    return 0


if __name__ == "__main__":
    sys.exit(main())
