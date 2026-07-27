#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Statute of the General Authority for Real
Estate track (16 records: 7 اصلية, 8 معدلة, 0 ملغاة, 1 مضافة [Article 13bis];
flat structure -- NO أبواب/فصول grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/rega_organizational_statute/law/official_source/
rega_organizational_statute_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa's LIVE
portal returned HTTP 503 every attempt this pass, and the Wayback Machine
was confirmed BLOCKED at the tool/network level (not merely unattempted).
This track instead rests on REGA's own official website's directly-hosted
scanned PDFs (base statute + four amendment decrees), read via direct
visual transcription (no OCR), cross-checked partially against nezams.com.
This validator does not attempt to re-adjudicate any of this; it only
checks internal self-consistency of the text this track actually ingests,
and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "rega_organizational_statute", "law", "official_source",
                   "rega_organizational_statute_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "rega_organizational_statute", "law", "verified",
                       "rega_organizational_statute_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "rega_organizational_statute", "law", "verified",
                       "rega_organizational_statute_verified_summary.json")
LLM = os.path.join(ROOT, "data", "rega_organizational_statute_arabic_legal_llm",
                   "rega_organizational_statute_legal_llm_001_016.json")
N = 16
BASE_ARTICLE_COUNT = 15  # articles 1-15 excluding the 13bis mukarrar addition
KEY_RE = r"rega_organizational_statute_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 7, "معدلة": 8, "ملغاة": 0, "مضافة": 1}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat law -- no أبواب/فصول, single leaf range 1-15

STATUS_UNCHANGED = "REGA_OWN_SITE_SCANNED_PDF_DIRECT_VISUAL_READ_LIVE_BOE_AND_WAYBACK_BOTH_UNREACHABLE_THIS_PASS"
STATUS_ART1 = "REGA_OWN_SITE_SCANNED_PDF_DIRECT_VISUAL_READ_X_RESOLUTION_426_RENAME_INCORPORATED_LIVE_BOE_AND_WAYBACK_BOTH_UNREACHABLE_THIS_PASS"
STATUS_ART3 = "REGA_OWN_SITE_SCANNED_PDF_DIRECT_VISUAL_READ_X_RESOLUTION_69_FULL_SUBSTITUTION_INCORPORATED_LIVE_BOE_AND_WAYBACK_BOTH_UNREACHABLE_THIS_PASS"
STATUS_ART4 = "REGA_OWN_SITE_SCANNED_PDF_DIRECT_VISUAL_READ_X_RESOLUTION_16_FULL_SUBSTITUTION_LATEST_OF_THREE_CHAINED_FULL_REPLACEMENTS_INCORPORATED_LIVE_BOE_AND_WAYBACK_BOTH_UNREACHABLE_THIS_PASS"
STATUS_ART5 = "REGA_OWN_SITE_SCANNED_PDF_DIRECT_VISUAL_READ_X_RESOLUTIONS_69_AND_426_INCORPORATED_LIVE_BOE_AND_WAYBACK_BOTH_UNREACHABLE_THIS_PASS"
STATUS_ART6 = STATUS_ART1
STATUS_ART8 = "REGA_OWN_SITE_SCANNED_PDF_DIRECT_VISUAL_READ_X_RESOLUTION_426_FULL_SUBSTITUTION_INCORPORATED_LIVE_BOE_AND_WAYBACK_BOTH_UNREACHABLE_THIS_PASS"
STATUS_ART9 = "REGA_OWN_SITE_SCANNED_PDF_DIRECT_VISUAL_READ_X_RESOLUTION_426_OPENING_CLOSING_SUBSTITUTION_INCORPORATED_LIVE_BOE_AND_WAYBACK_BOTH_UNREACHABLE_THIS_PASS"
STATUS_ART11 = "REGA_OWN_SITE_SCANNED_PDF_DIRECT_VISUAL_READ_X_RESOLUTION_69_INCORPORATED_LIVE_BOE_AND_WAYBACK_BOTH_UNREACHABLE_THIS_PASS"
STATUS_ART13BIS = "REGA_OWN_SITE_SCANNED_PDF_DIRECT_VISUAL_READ_X_ADDED_BY_RESOLUTION_69_THEN_REPLACED_BY_RESOLUTION_426_LIVE_BOE_AND_WAYBACK_BOTH_UNREACHABLE_THIS_PASS"
EXPECTED_STATUS_BY_KEY = {
    "rega_organizational_statute_art_001": STATUS_ART1,
    "rega_organizational_statute_art_003": STATUS_ART3,
    "rega_organizational_statute_art_004": STATUS_ART4,
    "rega_organizational_statute_art_005": STATUS_ART5,
    "rega_organizational_statute_art_006": STATUS_ART6,
    "rega_organizational_statute_art_008": STATUS_ART8,
    "rega_organizational_statute_art_009": STATUS_ART9,
    "rega_organizational_statute_art_011": STATUS_ART11,
    "rega_organizational_statute_art_013_mukarrar": STATUS_ART13BIS,
}
AMENDED_KEYS = {
    "rega_organizational_statute_art_001", "rega_organizational_statute_art_003",
    "rega_organizational_statute_art_004", "rega_organizational_statute_art_005",
    "rega_organizational_statute_art_006", "rega_organizational_statute_art_008",
    "rega_organizational_statute_art_009", "rega_organizational_statute_art_011",
}
ADDED_KEYS = {"rega_organizational_statute_art_013_mukarrar"}
REPEALED_KEYS = set()
MUKARRAR_KEYS = {"rega_organizational_statute_art_013_mukarrar"}
FLAGGED_DISCREPANCY_KEYS = {
    "rega_wayback_boe_unavailable_this_pass",
    "rega_five_pdfs_scanned_no_text_layer_direct_visual_reading",
    "rega_article1_wazir_definition_not_updated_confirmed_gap",
    "rega_websearch_resolution_number_error_corrected",
    "rega_article4_three_full_replacements_safely_chained_unlike_tvtc",
    "rega_article13bis_ceo_exception_dropped",
    "rega_qanoonsa_qanoniah_secondary_sources_inconclusive",
    "rega_no_named_predecessor_found",
    "rega_implementing_regs_and_committee_not_ingested",
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
    key), so this is a flat single-level walk over the 15 base articles
    (the 13bis mukarrar addition is not part of the numeric range walk)."""
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
    if covered != set(range(1, BASE_ARTICLE_COUNT + 1)):
        missing = sorted(set(range(1, BASE_ARTICLE_COUNT + 1)) - covered)
        extra = sorted(covered - set(range(1, BASE_ARTICLE_COUNT + 1)))
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
        if k in (AMENDED_KEYS | ADDED_KEYS) and not a.get("history"):
            e.append("[2] %s: amended/added article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present (source supplies no "
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

    if len(arts.get("rega_organizational_statute_art_004", {}).get("history", [])) != 4:
        e.append("[2j] Article 4 must record exactly 4 amendment history entries "
                 "(693, 69, 426, 16)")
    if len(arts.get("rega_organizational_statute_art_013_mukarrar", {}).get("history", [])) != 2:
        e.append("[2j] Article 13bis must record exactly 2 amendment history entries (69, 426)")

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
        e.append("[2k] missing amendment_history (must record 239, 693, 69, 426, and 16)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        for token in ("239", "693", "69", "426", "16"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference %s" % token)

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("rega_organizational_statute_art_001", {})
    if "الرئيس التنفيذي: الرئيس التنفيذي للهيئة" not in art1.get("text", "").replace("\n", " "):
        e.append("[2j] Article 1 missing expected الرئيس التنفيذي definition (Resolution 426)")
    if "وزير الإسكان" not in art1.get("text", ""):
        e.append("[2j] Article 1 unexpectedly missing original (never-amended) الوزير: وزير "
                 "الإسكان definition -- see rega_article1_wazir_definition_not_updated_"
                 "confirmed_gap")
    art3 = arts.get("rega_organizational_statute_art_003", {})
    if "التسجيل العيني للعقارات في المملكة" not in art3.get("text", ""):
        e.append("[2j] Article 3 missing expected Resolution-69 صدر substitution")
    if "إسناد بعض الخدمات" not in art3.get("text", ""):
        e.append("[2j] Article 3 missing expected added paragraph 20 (private-sector outsourcing)")
    art4 = arts.get("rega_organizational_statute_art_004", {})
    if "ل- ثلاثة من القطاع الخاص" not in art4.get("text", ""):
        e.append("[2j] Article 4 missing expected Resolution-16 paragraph-1 current text "
                 "(private-sector seats lettered ل)")
    if "وزير التعليم" in art4.get("text", ""):
        e.append("[2j] Article 4 unexpectedly contains unrelated stale wording")
    art8 = arts.get("rega_organizational_statute_art_008", {})
    if "بقرار من المجلس بناء على ترشيح من الرئيس" not in art8.get("text", ""):
        e.append("[2j] Article 8 missing expected Resolution-426 full substitution")
    if "بأمر ملكي" in art8.get("text", ""):
        e.append("[2j] Article 8 unexpectedly still contains stale pre-426 Royal-Order wording")
    art13bis = arts.get("rega_organizational_statute_art_013_mukarrar", {})
    if "عدا المحافظ" in art13bis.get("text", ""):
        e.append("[2j] Article 13bis unexpectedly still contains the CEO exception dropped by "
                 "Resolution 426")
    art15 = arts.get("rega_organizational_statute_art_015", {})
    if "الجريدة الرسمية" not in art15.get("text", ""):
        e.append("[2j] Article 15 missing expected official-gazette publication clause")
    if src.get("decree") != "قرار مجلس الوزراء رقم (239)" or src.get("decree_date_hijri") != "25/4/1438":
        e.append("[2j] decree/decree_date_hijri mismatch with verified 239, 25/4/1438H")

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
        print("FAIL: %d error(s) in REGA Organizational Statute track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Statute of the General Authority for Real Estate")
    print("  - 16 records: 7 اصلية, 8 معدلة, 0 ملغاة, 1 مضافة (Article 13bis)")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-15 plus a")
    print("    13bis mukarrar addition); no inline per-article titles in the source")
    print("    (no title_ar key used)")
    print("  - VERIFICATION TIER: REGA's own official site's scanned PDFs, direct")
    print("    visual reading (no OCR); laws.boe.gov.sa (HTTP 503) and the Wayback")
    print("    Machine (confirmed blocked) both unreachable this pass -- a different,")
    print("    honestly-documented tier from this corpus's BOE-Wayback-sourced siblings")
    print("  - Council of Ministers Resolution 239 (25/4/1438H); no named predecessor")
    print("    found (REGA is a newly-created authority) -- a confirmed negative finding")
    print("  - Article 4 paragraph 1 safely chained through THREE full replacements")
    print("    (693 partial -> 69 complete -> 16 complete); this track ingests")
    print("    Resolution 16's own complete text as current, unlike this corpus's")
    print("    tvtc_organizational_statute Article 4 precedent (not safely mergeable)")
    print("  - CONFIRMED CARRIED-FORWARD INCONSISTENCY: Article 1's 'الوزير' definition")
    print("    still reads 'وزير الإسكان', never textually updated by any of the four")
    print("    amendment decrees read this pass, despite Article 4's own renamed")
    print("    ministry references -- honestly flagged, not silently harmonized")
    return 0


if __name__ == "__main__":
    sys.exit(main())
