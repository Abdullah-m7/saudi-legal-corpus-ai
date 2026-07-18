#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Law of the General Authority for Awqaf track
(25 records: 23 اصلية, 2 معدلة [Articles 6, 21], 0 ملغاة, 0 مضافة; flat
structure -- NO أبواب/فصول grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/awqaf/law/official_source/awqaf_law_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa's LIVE
portal was unreachable this pass (HTTP 503), but SIX Wayback Machine
snapshots of the exact BOE law page, spanning 21 Nov 2019 - 12 Dec 2025,
were reachable via direct curl (WebFetch itself refuses web.archive.org in
this environment) and cross-diffed. 23 of 25 articles are byte-stable
across all six time-points. Articles 6 and 21 both carry BOE's own
'changed-article' flag: Article 21's single, clean, fully-quoted
changelog-popup amendment (Royal Decree M/72, 1/6/1444H) is ingested in
place of BOE's own stale main body (per this corpus's accounting_
auditing_law precedent); Article 6's FOUR layered, partial, internally-
inconsistent changelog amendments are NOT hand-merged -- BOE's own stable
six-year main-body text is ingested instead, with all four amendments
recorded in history[] and the inconsistency flagged explicitly. This
validator does not attempt to re-adjudicate any of this; it only checks
internal self-consistency of the text this track actually ingests, and
that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "awqaf", "law", "official_source",
                   "awqaf_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "awqaf", "law", "verified",
                       "awqaf_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "awqaf", "law", "verified",
                       "awqaf_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "awqaf_arabic_legal_llm",
                   "awqaf_law_legal_llm_001_025.json")
N = 25
KEY_RE = r"awqaf_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 23, "معدلة": 2, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat law -- no أبواب/فصول, single leaf range 1-25

STATUS_UNCHANGED = ("BOE_WAYBACK_ARCHIVE_SIX_TIMEPOINT_NOV2019_MAY2022_SEP2023_APR2024_"
                     "DEC2024_DEC2025_TEXT_STABLE_X_AWQAF_GOV_SA_OFFICIAL_ORIGINAL_SCAN_"
                     "X_NEZAMS_STRUCTURAL_CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_ART6 = ("BOE_WAYBACK_MAIN_BODY_STABLE_SIX_TIMEPOINT_NOV2019_DEC2025_BUT_STALE_"
               "VS_OWN_CHANGELOG_POPUP_X_NEZAMS_CHANGELOG_CROSSCHECK_UNRESOLVED_"
               "INTERMEDIATE_STEP_LIVE_BOE_UNREACHABLE")
STATUS_ART21 = ("BOE_CHANGELOG_POPUP_M72_TEXT_INCORPORATED_MAIN_BODY_STALE_X_"
                "WEBSEARCH_ALRIYADH_UQN_GAZETTE_CROSSCHECK_LIVE_BOE_UNREACHABLE")
EXPECTED_STATUS_BY_KEY = {
    "awqaf_art_006": STATUS_ART6,
    "awqaf_art_021": STATUS_ART21,
}
AMENDED_KEYS = set(EXPECTED_STATUS_BY_KEY)
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
FLAGGED_DISCREPANCY_KEYS = {
    "awqaf_article6_boe_main_body_not_reflecting_own_changelog",
    "awqaf_article21_changelog_amendment_incorporated_main_body_stale",
    "awqaf_gap_map_estimate_corrected_and_confirmed",
    "awqaf_no_baab_fasl_structure",
    "awqaf_no_inline_article_titles",
    "awqaf_predecessor_m35_1386h_confirmed_primary",
    "awqaf_article25_other_repeal_and_procedural_clauses",
    "awqaf_distinct_from_any_separate_substantive_waqf_law",
    "awqaf_implementing_regs_not_ingested",
    "awqaf_boe_english_title_nuance",
    "awqaf_boe_live_portal_unreachable_wayback_used",
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


def _iter_chapter_ranges(chs):
    """Yield (lo, hi) for every leaf range in chapter_structure. This Law has
    no أبواب/فصول nesting -- every top-level entry IS a leaf (no 'sections'
    key), so this is a flat single-level walk."""
    for ch in chs:
        secs = ch.get("sections")
        if not secs:
            lo, hi = (int(x) for x in ch["articles"].split("-"))
            yield (lo, hi)
            continue
        for sec in secs:
            slo, shi = (int(x) for x in sec["articles"].split("-"))
            yield (slo, shi)


def main():
    e = []
    for p in (SRC, RECORDS, SUMMARY, LLM):
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

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d top-level chapter_structure entries (flat law, "
                  "no أبواب/فصول), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one leaf range" % n)
            covered.add(n)
    if covered != set(range(1, N + 1)):
        missing = sorted(set(range(1, N + 1)) - covered)
        extra = sorted(covered - set(range(1, N + 1)))
        if missing:
            e.append("[1c] chapter_structure missing article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])

    sc = Counter()
    for k, a in arts.items():
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNCHANGED)
        if a.get("status") != expected_status:
            e.append("[2] %s: expected status %r, got %r" % (k, expected_status, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present (BOE source supplies no "
                      "inline per-article titles for this law -- see "
                      "known_unresolved_discrepancies)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "ًً" in a["text"]:
            e.append("[2g] %s: residual doubled-tanwin artifact detected" % k)
        if re.search(r"\(\s*\)\d", a["text"]):
            e.append("[2h] %s: residual bidi paren-before-digit artifact detected" % k)

    if len(arts.get("awqaf_art_006", {}).get("history", [])) != 4:
        e.append("[2j] Article 6 must record exactly 4 amendment history entries")
    if len(arts.get("awqaf_art_021", {}).get("history", [])) != 1:
        e.append("[2j] Article 21 must record exactly 1 amendment history entry")

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
        e.append("[2k] missing amendment_history (must record M/11, M/72, and the "
                 "four Article-6 resolutions)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        for token in ("م/11", "م/72", "262", "618", "638", "651"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference %s" % token)

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("awqaf_art_001", {})
    if "الهيئة العامة للأوقاف" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected الهيئة definition")
    art2 = arts.get("awqaf_art_002", {})
    if "شخصية اعتبارية مستقلة" not in art2.get("text", ""):
        e.append("[2j] Article 2 missing expected legal-personality clause")
    art6 = arts.get("awqaf_art_006", {})
    if "خمسة عشر عضواً" not in art6.get("text", ""):
        e.append("[2j] Article 6 missing expected 15-member board clause")
    art14 = arts.get("awqaf_art_014", {})
    if "10" not in art14.get("text", "") and "10٪" not in art14.get("text", ""):
        e.append("[2j] Article 14 missing expected 10% management-fee cap")
    art21 = arts.get("awqaf_art_021", {})
    if "نظام التكاليف القضائية" not in art21.get("text", ""):
        e.append("[2j] Article 21 missing expected M/72-amended judicial-costs exemption")
    if "معاملة الهيئات والمؤسسات العامة" not in art21.get("text", ""):
        e.append("[2j] Article 21 missing expected paragraph (1) fee-treatment clause")
    art25 = arts.get("awqaf_art_025", {})
    if "م/35" not in art25.get("text", "") or "1386" not in art25.get("text", ""):
        e.append("[2j] Article 25 missing expected predecessor repeal citation (M/35, 1386H)")
    if src.get("decree") != "المرسوم الملكي رقم (م/11)" or src.get("decree_date_hijri") != "26/2/1437":
        e.append("[2j] decree/decree_date_hijri mismatch with verified M/11, 26/2/1437H")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
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
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
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
        expected_status = EXPECTED_STATUS_BY_KEY.get(r["article_key"], STATUS_UNCHANGED)
        if r.get("source_trust", {}).get("source_status") != expected_status.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Awqaf Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Law of the General Authority for Awqaf")
    print("  - 25 records: 23 اصلية, 2 معدلة (Articles 6, 21), 0 ملغاة, 0 مضافة")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-25); no")
    print("    inline per-article titles in the BOE source (no title_ar key used)")
    print("  - VERIFICATION TIER: BOE-via-Wayback-Machine, SIX snapshots spanning")
    print("    21 Nov 2019 - 12 Dec 2025, x web.awqaf.gov.sa's own scanned original")
    print("    decree, x nezams.com, x a WebSearch/press aggregation for Article 21")
    print("  - Royal Decree M/11 (26/2/1437H / 8 Dec 2015G), Council of Ministers")
    print("    Resolution 73 (25/2/1437H); replaces نظام مجلس الأوقاف الأعلى (Royal")
    print("    Decree M/35, 18/7/1386H) per this law's own Article 25(1)")
    print("  - MAJOR VERIFIED ANOMALY carried forward (Article 6): BOE's own page logs")
    print("    FOUR amendments (CoM Resolutions 262/1438H, 618/1442H, 638/1442H,")
    print("    651/1443H) but its own main body text is stable/unchanged across all six")
    print("    snapshots (2019-2025) and inconsistent with the changelog's own quoted")
    print("    'before' states -- this track ingests the stable main body, NOT a")
    print("    hand-merged guess, and flags the unresolved inconsistency")
    print("  - MAJOR VERIFIED ANOMALY carried forward (Article 21): BOE's own page logs")
    print("    a single clean amendment (Royal Decree M/72, 1/6/1444H, adding a")
    print("    judicial-costs exemption paragraph) but its main body stays pre-")
    print("    amendment across all six snapshots -- this track ingests the quoted")
    print("    changelog text instead, per the accounting_auditing_law precedent")
    print("  - No separate substantive Waqf code found distinct from this Authority's")
    print("    own organizing statute; companion implementing regulations identified")
    print("    but NOT ingested this pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
