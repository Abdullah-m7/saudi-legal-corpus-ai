#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Regulation of Real Estate Auctions track
(اللائحة التنظيمية للمزادات العقارية, Resolution of the Board of Directors of
the General Authority for Real Estate / REGA, dated 01/12/1444H = 19/06/2023G;
12 records, all اصلية; no formal numbered "الفصل" chapters in the source --
only short un-numbered topical section headers, unlike this corpus's other
REGA-issued regulation tracks).

VERIFICATION TIER -- see the generator's module docstring and
sources/real_estate_auctions_regulation/law/official_source/
real_estate_auctions_regulation_official_source.json's
verification_methodology_note for the full account. This validator asserts:
exactly 12 articles in a clean 1..12 run; every article source_tier ==
"primary" (dual primary sources -- uqn.gov.sa Umm Al-Qura Gazette and
rega.gov.sa REGA's own site -- reached this pass with no reachability gap);
every article carries an explicit rega_site_cross_check value, with exactly
Articles 2 and 10 flagged as the two documented small wording variances
between the two primary sources; all 12 articles are اصلية with empty
amendment history; and that every discrepancy this build's own methodology
note flags as a named, non-obvious judgment call is present in
known_unresolved_discrepancies.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "real_estate_auctions_regulation", "law", "official_source",
                   "real_estate_auctions_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "real_estate_auctions_regulation", "law", "verified",
                       "real_estate_auctions_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "real_estate_auctions_regulation", "law", "verified",
                       "real_estate_auctions_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "real_estate_auctions_regulation_arabic_legal_llm",
                   "real_estate_auctions_regulation_legal_llm_001_012.json")
N = 12
KEY_RE = r"real_estate_auctions_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 12, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_ARTICLE_STATUS = "UQN_GAZETTE_OFFICIAL_PRIMARY_TEXT_AR_DUAL_PRIMARY_CROSS_VERIFIED_REGA_OFFICIAL_SITE"
EXPECTED_CROSS_CHECK_DIVERGENT = {2, 10}
EXPECTED_SPANS = {"2-2", "3-4", "5-5", "6-7", "8-10", "11-12"}
EXPECTED_CHAPTER_ENTRIES = 6
FLAGGED_DISCREPANCY_KEYS = {
    "real_estate_auctions_regulation_article2_item5_wording_variance",
    "real_estate_auctions_regulation_article10_item1_wording_variance",
    "real_estate_auctions_regulation_board_resolution_number_not_located",
    "real_estate_auctions_regulation_no_formal_chapters",
    "real_estate_auctions_regulation_no_decree_preamble_text",
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
    if not chapters or len(chapters) != EXPECTED_CHAPTER_ENTRIES:
        e.append("[1c] expected %d chapter_structure entries, got %r"
                 % (EXPECTED_CHAPTER_ENTRIES, chapters))
    else:
        for c in chapters:
            if c.get("label_ar") != "":
                e.append("[1c] chapter label_ar must be empty (no formal الفصل numbering "
                         "in this regulation's own text), got %r" % c.get("label_ar"))
            if not c.get("title_ar", "").strip():
                e.append("[1c] chapter entry missing non-empty title_ar")
            if not c.get("articles"):
                e.append("[1c] chapter %r must carry a numbered article range" % c.get("title_ar"))
        got_spans = {c.get("articles") for c in chapters}
        if got_spans != EXPECTED_SPANS:
            e.append("[1c] chapter_structure article spans %r != expected %r"
                     % (got_spans, EXPECTED_SPANS))
        covered = set()
        for c in chapters:
            lo, hi = (int(x) for x in c["articles"].split("-"))
            for n in range(lo, hi + 1):
                if n in covered:
                    e.append("[1c] article %d covered by more than one chapter range" % n)
                covered.add(n)
        # Article 1 (definitions) has no heading on either primary source and is
        # deliberately NOT covered by any chapter_structure entry (matches the
        # precedent set by real_estate_brokerage_regulation's Article 1).
        if covered != set(range(2, N + 1)):
            e.append("[1c] chapters do not exactly tile articles 2..%d: got %s"
                     % (N, sorted(covered)))
        if 1 in covered:
            e.append("[1c] article 1 (definitions) must NOT be covered by any chapter "
                     "entry -- no heading precedes it on either primary source")

    if src.get("consolidated_amended_law") is not False:
        e.append("[1d] consolidated_amended_law must be False for this track")
    if src.get("law_component") != "regulation":
        e.append("[1d] law_component must be 'regulation'")
    if src.get("legal_status_ar") != "ساري":
        e.append("[1d] legal_status_ar must be ساري (matches rega.gov.sa's own "
                 "'حالة التشريع' field)")

    tier_counts = Counter()
    cross_check_counts = Counter()
    sc = Counter()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
        tier = a.get("source_tier")
        if tier != "primary":
            e.append("[2] %s: expected source_tier 'primary' (dual primary sources for all "
                     "12 articles), got %r" % (k, tier))
        else:
            tier_counts[tier] += 1
        if a.get("status") != EXPECTED_ARTICLE_STATUS:
            e.append("[2] %s: expected status %r, got %r"
                     % (k, EXPECTED_ARTICLE_STATUS, a.get("status")))

        cross_check = a.get("rega_site_cross_check")
        if cross_check not in ("MATCHES_VERBATIM", "MINOR_WORDING_VARIANCE_DOCUMENTED"):
            e.append("[2b] %s: missing/invalid rega_site_cross_check %r" % (k, cross_check))
        else:
            cross_check_counts[cross_check] += 1
            expect_divergent = n in EXPECTED_CROSS_CHECK_DIVERGENT
            if expect_divergent and cross_check != "MINOR_WORDING_VARIANCE_DOCUMENTED":
                e.append("[2b] %s: article %d expected a documented wording variance "
                         "against rega.gov.sa, got %r" % (k, n, cross_check))
            if not expect_divergent and cross_check != "MATCHES_VERBATIM":
                e.append("[2b] %s: article %d expected to match rega.gov.sa verbatim, "
                         "got %r" % (k, n, cross_check))

        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if n != 1 and not a.get("section_ar", "").strip():
            e.append("[2] %s: section_ar must be non-empty for articles 2-12" % k)
        if n == 1 and a.get("section_ar", "") != "":
            e.append("[2] %s: article 1 (definitions) must have empty section_ar -- no "
                     "heading precedes it on either primary source" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2] %s: residual Eastern-Arabic-Indic digit (must be normalized)" % k)
        if "  " in a["text"]:
            e.append("[2] %s: residual double-space artifact" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)

        if ls != "اصلية":
            e.append("[3] %s: article %d expected اصلية (no amendment confirmed this pass), "
                     "got %r" % (k, n, ls))
        if a.get("history"):
            e.append("[3] %s: article %d must have empty history (اصلية-only track)" % (k, n))

    if tier_counts.get("primary", 0) != N:
        e.append("[2g] expected %d primary-tier articles, got %d" % (N, tier_counts.get("primary", 0)))
    declared_tiers = src.get("source_tier_counts") or {}
    if declared_tiers.get("primary") != tier_counts.get("primary", 0):
        e.append("[2g] declared source_tier_counts.primary does not match actual per-article count")
    if declared_tiers.get("secondary_only", 0) != 0:
        e.append("[2g] declared source_tier_counts.secondary_only must be 0 (dual primary "
                 "sources cover all 12 articles)")

    if cross_check_counts.get("MINOR_WORDING_VARIANCE_DOCUMENTED", 0) != len(EXPECTED_CROSS_CHECK_DIVERGENT):
        e.append("[2b] expected exactly %d articles with a documented rega.gov.sa wording "
                 "variance, got %d" % (len(EXPECTED_CROSS_CHECK_DIVERGENT),
                                       cross_check_counts.get("MINOR_WORDING_VARIANCE_DOCUMENTED", 0)))
    if cross_check_counts.get("MATCHES_VERBATIM", 0) != N - len(EXPECTED_CROSS_CHECK_DIVERGENT):
        e.append("[2b] expected exactly %d byte-identical articles, got %d"
                 % (N - len(EXPECTED_CROSS_CHECK_DIVERGENT), cross_check_counts.get("MATCHES_VERBATIM", 0)))

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))
    declared = src.get("status_counts") or {}
    for st in ALLOWED_STATUS:
        if declared.get(st, 0) != sc.get(st, 0):
            e.append("[2f] declared status_counts[%s] does not match actual per-article counts" % st)

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the tier")
    if not (src.get("preamble_ar") or "").strip():
        e.append("[2d] missing preamble_ar")
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
        if r.get("source_tier") != a.get("source_tier"):
            e.append("[4] %s: source_tier mismatch" % r["article_key"])
        if r.get("rega_site_cross_check") != a.get("rega_site_cross_check"):
            e.append("[4] %s: rega_site_cross_check mismatch" % r["article_key"])
        if r.get("is_amended") is not False or r.get("is_repealed") is not False or r.get("is_added") is not False:
            e.append("[4] %s: expected all status flags False (اصلية-only track)" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts mismatch with source")
    if summary.get("source_tier_counts") != src.get("source_tier_counts"):
        e.append("[4b] summary source_tier_counts mismatch with source")

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
        if r.get("source_trust", {}).get("source_tier") != a.get("source_tier"):
            e.append("[5] %s: llm record source_trust.source_tier mismatch" % r["article_key"])
        if r.get("source_trust", {}).get("rega_site_cross_check") != a.get("rega_site_cross_check"):
            e.append("[5] %s: llm record source_trust.rega_site_cross_check mismatch" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Real Estate Auctions Regulation track:" % len(e))
        for x in e[:30]:
            print("  - %s" % x)
        return 1
    print("PASS: Regulation of Real Estate Auctions — 12 records "
          "(12 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; no formal الفصل chapters in source)")
    print("  - TIER: DUAL PRIMARY, ALL 12 ARTICLES -- uqn.gov.sa (Umm Al-Qura Official "
          "Gazette) and rega.gov.sa (REGA's own official site) both reached directly this "
          "pass, in full agreement on 10/12 articles; Articles 2 and 10 carry one small, "
          "documented phrase-level wording variance each (Gazette text adopted as governing)")
    print("  - IN-FORCE Resolution of REGA's Board of Directors (01/12/1444H = 19/06/2023G, "
          "calculated), published Umm Al-Qura Gazette (09/02/1445H = 25/08/2023G)")
    print("  - No board-resolution number located for this instrument (disclosed gap); no "
          "formal numbered الفصل chapters in the source (disclosed, un-numbered section "
          "headers used instead); see known_unresolved_discrepancies for full detail")
    print("  - Parent instruments (real_estate_brokerage, real_estate_brokerage_regulation) "
          "NOT touched -- already tracked independently elsewhere in this corpus")
    return 0


if __name__ == "__main__":
    sys.exit(main())
