#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Statute of the Technical and Vocational
Training Corporation track (13 records: 11 اصلية, 2 معدلة [Articles 4, 7],
0 ملغاة, 0 مضافة; flat structure -- NO أبواب/فصول grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/tvtc_organizational_statute/law/official_source/
tvtc_organizational_statute_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa's LIVE
portal was unreachable this pass, but THREE Wayback Machine snapshots of the
exact BOE law page, spanning 16 Jan 2020 - 7 May 2025, were reachable via
direct curl and cross-diffed. 12 of 13 articles are byte-stable across all
three time-points; Article 4 carries BOE's own 'changed-article' flag with
THREE layered, not-safely-mergeable amendments (this track ingests BOE's own
stale main body, unmerged); Article 7 carries a single amendment (Council of
Ministers Resolution 632) confirmed only via non-BOE sources (qanoonsa.com
and a WebSearch aggregation), NOT via a BOE changelog entry. This validator
does not attempt to re-adjudicate any of this; it only checks internal
self-consistency of the text this track actually ingests, and that every
discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "tvtc_organizational_statute", "law", "official_source",
                   "tvtc_organizational_statute_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "tvtc_organizational_statute", "law", "verified",
                       "tvtc_organizational_statute_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "tvtc_organizational_statute", "law", "verified",
                       "tvtc_organizational_statute_verified_summary.json")
LLM = os.path.join(ROOT, "data", "tvtc_organizational_statute_arabic_legal_llm",
                   "tvtc_organizational_statute_legal_llm_001_013.json")
N = 13
KEY_RE = r"tvtc_organizational_statute_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 11, "معدلة": 2, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat law -- no أبواب/فصول, single leaf range 1-13

STATUS_UNCHANGED = ("BOE_WAYBACK_ARCHIVE_THREE_TIMEPOINT_JAN2020_DEC2022_MAY2025_TEXT_STABLE_X_"
                     "NEZAMS_COM_CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_ART4 = ("BOE_CHANGELOG_THREE_LAYERED_PARTIAL_AMENDMENTS_469_693_745_MAIN_BODY_STALE_NOT_"
               "SAFELY_MERGEABLE_CURRENT_BOARD_COMPOSITION_UNRECONSTRUCTED_LIVE_BOE_UNREACHABLE")
STATUS_ART7 = ("COM_RESOLUTION_632_1446H_QANOONSA_DIRECT_FETCH_X_WEBSEARCH_AGGREGATION_CROSSCHECK_"
               "SUBSTITUTION_INCORPORATED_NOT_YET_IN_BOE_CHANGELOG_MAIN_BODY_STALE_LIVE_BOE_UNREACHABLE")
EXPECTED_STATUS_BY_KEY = {
    "tvtc_organizational_statute_art_004": STATUS_ART4,
    "tvtc_organizational_statute_art_007": STATUS_ART7,
}
AMENDED_KEYS = set(EXPECTED_STATUS_BY_KEY)
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
FLAGGED_DISCREPANCY_KEYS = {
    "tvtc_article4_three_layered_amendments_not_safely_mergeable",
    "tvtc_article7_resolution632_not_in_boe_changelog",
    "tvtc_boe_issuance_date_metadata_anomaly",
    "tvtc_boe_publication_date_placeholder_anomaly",
    "tvtc_predecessor_confirmed_named",
    "tvtc_no_baab_fasl_structure",
    "tvtc_no_inline_article_titles",
    "tvtc_implementing_regs_not_ingested",
    "tvtc_uqn_gazette_unreachable",
    "tvtc_official_site_summary_only_not_full_text",
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

    if len(arts.get("tvtc_organizational_statute_art_004", {}).get("history", [])) != 3:
        e.append("[2j] Article 4 must record exactly 3 amendment history entries")
    if len(arts.get("tvtc_organizational_statute_art_007", {}).get("history", [])) != 1:
        e.append("[2j] Article 7 must record exactly 1 amendment history entry")

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
        e.append("[2k] missing amendment_history (must record 268, 469, 693, 745, and 632)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        for token in ("268", "469", "693", "745", "632"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference %s" % token)

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("tvtc_organizational_statute_art_001", {})
    if "المؤسسة العامة للتدريب التقني والمهني" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected المؤسسة definition")
    art4 = arts.get("tvtc_organizational_statute_art_004", {})
    if "وزير العمل" not in art4.get("text", ""):
        e.append("[2j] Article 4 unexpectedly missing original (pre-469) وزير العمل chairmanship "
                 "wording -- this track must ingest BOE's own STALE main body, not a reconstructed "
                 "current text")
    if "وزير التعليم" in art4.get("text", ""):
        e.append("[2j] Article 4 unexpectedly contains post-469 وزير التعليم wording in the main "
                 "text field -- that belongs only in history, not the ingested current text")
    art7 = arts.get("tvtc_organizational_statute_art_007", {})
    if "يعين ويعفى من منصبه بقرار من المجلس بعد موافقة رئيس مجلس الوزراء" not in art7.get("text", ""):
        e.append("[2j] Article 7 missing expected Resolution-632 amended صدر wording")
    if "بالمرتبة الممتازة بناء على اقتراح من الرئيس" in art7.get("text", ""):
        e.append("[2j] Article 7 unexpectedly still contains stale pre-632 صدر wording")
    if "الإعداد لاجتماعات المجلس" not in art7.get("text", ""):
        e.append("[2j] Article 7 missing expected unchanged enumerated-duties list")
    art12 = arts.get("tvtc_organizational_statute_art_012", {})
    if "نظام المؤسسة العامة للتعليم الفني والتدريب المهني" not in art12.get("text", ""):
        e.append("[2j] Article 12 missing expected named predecessor repeal clause")
    art13 = arts.get("tvtc_organizational_statute_art_013", {})
    if "الجريدة الرسمية" not in art13.get("text", ""):
        e.append("[2j] Article 13 missing expected official-gazette publication clause")
    if src.get("decree") != "قرار مجلس الوزراء رقم (268)" or src.get("decree_date_hijri") != "14/8/1428":
        e.append("[2j] decree/decree_date_hijri mismatch with verified 268, 14/8/1428H")

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
        print("FAIL: %d error(s) in TVTC Organizational Statute track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Statute of the Technical and Vocational Training Corporation")
    print("  - 13 records: 11 اصلية, 2 معدلة (Articles 4, 7), 0 ملغاة, 0 مضافة")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-13); no")
    print("    inline per-article titles in the BOE source (no title_ar key used)")
    print("  - VERIFICATION TIER: BOE-via-Wayback-Machine, THREE snapshots spanning")
    print("    16 Jan 2020 - 7 May 2025, x nezams.com, x TVTC's own official website")
    print("    (tvtc.gov.sa, citation-only), x a qanoonsa.com direct fetch + WebSearch")
    print("    aggregation for Article 7's Resolution-632 amendment")
    print("  - Council of Ministers Resolution 268 (14/8/1428H); predecessor CONFIRMED")
    print("    and named in Article 12 (نظام المؤسسة العامة للتعليم الفني والتدريب")
    print("    المهني, Royal Decree M/30, 10/8/1400H) -- a positive finding, not ingested")
    print("  - MAJOR VERIFIED ANOMALY carried forward (Article 4): BOE's own changelog")
    print("    logs THREE layered amendments (469, 693, 745) but entries 2-3 are bare")
    print("    'add a seat' instructions with no stated lettered position -- NOT safely")
    print("    mergeable; this track ingests BOE's own stale main body unmerged and")
    print("    records all three amendments verbatim without fabricating a composite")
    print("  - MAJOR VERIFIED ANOMALY carried forward (Article 7): Council of Ministers")
    print("    Resolution 632 (26/8/1446H) cleanly replaces the صدر only, confirmed via")
    print("    qanoonsa.com + WebSearch, but NOT reflected in any of three independently")
    print("    checked BOE snapshots through 7 May 2025 -- a thinner verification tier")
    print("    than a BOE-changelog-confirmed amendment, honestly flagged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
