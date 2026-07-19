#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Food Law track (44 of this law's
45 total articles recovered: Articles 2-45, all اصلية; Article 1 EXCLUDED,
not fabricated -- see below. 12 chapters (فصول), matching this law's
independently-corroborated 45-article/XII-chapter structure).

VERIFICATION TIER -- see the generator's module docstring and
sources/food/law/official_source/food_law_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa's LIVE
portal was unreachable this pass (503 / connection reset, both via curl and
via WebFetch), and -- UNLIKE this corpus's usual fallback pattern -- the
Wayback Machine was ALSO unreachable (web.archive.org blocked by this
session's egress policy, both via direct curl and via WebFetch; only
archive.org's own '/wayback/available' lookup API succeeded, confirming a
snapshot exists without being able to fetch its content). This track's full
text instead rests on ONE official/primary source: an SFDA-published PDF
(اللائحة التنفيذية لنظام الغذاء) that interleaves this base law's own
articles with its Implementing Regulation's articles, visually transcribed
page-by-page this pass (an initial OCR pass was used only for triage and was
found to silently drop at least one bordered box). Cross-checked against
saudipedia.com, FAOLEX metadata, and aggregated WebSearch results describing
BOE's own hosted translation title -- but NOT independently cross-verified
word-for-word against a second full-text copy of the law. This validator
does not re-adjudicate any of this; it only checks internal self-consistency
of the text this track actually ingests, and that every discrepancy is still
recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "food", "law", "official_source",
                   "food_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "food", "law", "verified",
                       "food_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "food", "law", "verified",
                       "food_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "food_arabic_legal_llm",
                   "food_law_legal_llm_001_044.json")
N = 44
TOTAL_ARTICLES_IN_LAW = 45
EXCLUDED_ARTICLE_NUMBERS = [1]
KEY_RE = r"food_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 44, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 12  # XII chapters, independently corroborated

STATUS_UNCHANGED = ("SFDA_PDF_VISUAL_TRANSCRIPTION_SINGLE_SOURCE_LIVE_BOE_AND_"
                    "WAYBACK_BOTH_UNREACHABLE")
AMENDED_KEYS = set()
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
EXPECTED_STATUS_BY_KEY = {}
FLAGGED_DISCREPANCY_KEYS = {
    "food_gap_map_estimate_confirmed_and_revised",
    "food_boe_and_wayback_both_unreachable",
    "food_article1_not_recovered",
    "food_primary_source_is_sfda_pdf_ocr_boxes_dropped",
    "food_no_amendments_found_negative_evidence_only",
    "food_implementing_regulation_penalty_amendments_out_of_scope",
    "food_underlying_resolution_475_not_independently_dated",
    "food_no_preamble_recovered",
    "food_duplicate_chapter_titles_anomaly",
    "food_repeal_generic_clause_only_no_named_predecessor",
    "food_no_inline_article_titles",
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

    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    if src.get("article_count") != N:
        e.append("[1] article_count field != %d" % N)
    if src.get("total_articles_in_law") != TOTAL_ARTICLES_IN_LAW:
        e.append("[1] total_articles_in_law field != %d" % TOTAL_ARTICLES_IN_LAW)
    if src.get("excluded_article_numbers") != EXCLUDED_ARTICLE_NUMBERS:
        e.append("[1] excluded_article_numbers != %s" % EXCLUDED_ARTICLE_NUMBERS)
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)
        n = int(re.match(KEY_RE, k).group(1))
        if n in EXCLUDED_ARTICLE_NUMBERS:
            e.append("[1] %s: excluded article number must not appear in articles{}" % k)

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapter_structure entries (XII chapters), got %d"
                 % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one leaf range" % n)
            covered.add(n)
    full_range = set(range(1, TOTAL_ARTICLES_IN_LAW + 1))
    if covered != full_range:
        missing = sorted(full_range - covered)
        extra = sorted(covered - full_range)
        if missing:
            e.append("[1c] chapter_structure missing article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])
    # exactly the excluded numbers (Article 1) should be covered by chapter_structure
    # (structural context) but absent from articles{} -- already checked above.

    sc = Counter()
    for k, a in arts.items():
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNCHANGED)
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
        if k not in AMENDED_KEYS and a.get("history"):
            e.append("[2i] %s: non-amended article must have empty history[]" % k)
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present (source supplies no "
                      "inline per-article titles for this law)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
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
        e.append("[2k] missing amendment_history (must record founding decree)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        if "م/1" not in decrees:
            e.append("[2k] amendment_history must reference the founding decree م/1")

    # spot-checks anchoring key facts established this pass
    art36 = arts.get("food_art_036", {})
    if "عشر سنوات" not in art36.get("text", "") or "عشرة ملايين ريال" not in art36.get("text", ""):
        e.append("[2j] Article 36 missing expected penalty ceiling wording (10 years / SAR 10,000,000)")
    if "مليون ريال" not in art36.get("text", ""):
        e.append("[2j] Article 36 missing expected general fine ceiling wording (SAR 1,000,000)")
    art45 = arts.get("food_art_045", {})
    if "مائة وثمانين" not in art45.get("text", "") or "يلغي كل ما يتعارض" not in art45.get("text", ""):
        e.append("[2j] Article 45 missing expected 180-day commencement / generic repeal wording")
    if "نظام الجنسية" in art45.get("text", "") or re.search(r"\d{4}هـ", art45.get("text", "")):
        e.append("[2j] Article 45 must NOT name any specific predecessor law (confirmed generic-repeal-only finding)")
    art16 = arts.get("food_art_016", {})
    if "الشريعة الإسلامية" not in art16.get("text", ""):
        e.append("[2j] Article 16 missing expected Shariah-compliance prohibited-circulation ground")
    if src.get("decree") != "المرسوم الملكي رقم (م/1)" or src.get("decree_date_hijri") != "6/1/1436":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/1, 6/1/1436H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no amendments were found/incorporated this pass)")
    if "preamble_ar" in src:
        e.append("[2j] preamble_ar should be absent (not recovered this pass, per "
                 "food_no_preamble_recovered) -- must not be fabricated")

    # duplicate chapter-title anomaly must be preserved, not silently fixed
    titles_by_range = {ch["articles"]: ch.get("title_ar", "") for ch in chs}
    ch4_title = titles_by_range.get("14-15", "")
    ch5_title = titles_by_range.get("16-17", "")
    if not (ch4_title.startswith("تداول الغذاء") and ch5_title.startswith("تداول الغذاء")):
        e.append("[3] expected chapters covering 14-15 and 16-17 to both be titled "
                 "'تداول الغذاء' (preserved source anomaly) -- got %r / %r" % (ch4_title, ch5_title))

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
    if summary.get("total_articles_in_law") != TOTAL_ARTICLES_IN_LAW:
        e.append("[4b] summary total_articles_in_law != %d" % TOTAL_ARTICLES_IN_LAW)

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
        print("FAIL: %d error(s) in Food Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Arabian Food Law")
    print("  - 44 of 45 total articles recovered (Articles 2-45), all اصلية, 0 معدلة,")
    print("    0 ملغاة, 0 مضافة; Article 1 (تعريفات) EXCLUDED -- not reproduced in the")
    print("    source, not fabricated")
    print("  - 12 chapters (فصول) confirmed; Chapters 4 and 5 share an identical title")
    print("    'تداول الغذاء' in the source itself -- a genuine anomaly, preserved verbatim")
    print("  - VERIFICATION TIER: TIER_2 (conservative) -- ONE official/primary source (an")
    print("    SFDA-published PDF, visually transcribed page-by-page this pass) plus")
    print("    secondary cross-checks (saudipedia.com exact-date match, FAOLEX metadata,")
    print("    aggregated BOE-translation-title corroboration of structure); laws.boe.gov.sa")
    print("    was completely unreachable this pass -- both live AND via the Wayback")
    print("    Machine (web.archive.org blocked by egress policy), a more severe access")
    print("    failure than this corpus's usual BOE-503-Wayback-succeeds pattern")
    print("  - Royal Decree M/1 (6/1/1436H / 30 Oct 2014G); Article 45 carries only a")
    print("    generic non-specific repeal clause -- CONFIRMED NEGATIVE finding, no named")
    print("    predecessor food-safety law identified this pass")
    print("  - Companion instrument identified but NOT ingested this pass: اللائحة")
    print("    التنفيذية لنظام الغذاء (~85 articles, repeatedly amended at SFDA Board level)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
