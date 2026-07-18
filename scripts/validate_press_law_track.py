#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Press and Publications Law track
(نظام المطبوعات والنشر, Royal Decree M/32, 3/9/1421H).

49 records: 43 اصلية, 6 معدلة (Articles 5, 9, 36, 37, 38, 40), 0 ملغاة,
0 مضافة. No أبواب/فصول labels in the source; 6 flat structural groups
(Articles 1-12 untitled; then المطبوعات الداخلية 13-17; المطبوعات
الخارجية 18-23; الصحافة المحلية 24-34; الجزاءات 35-41; أحكام عامة 42-49).

CURRENCY CHECK -- see the generator's module docstring and
sources/press/law/official_source/press_law_official_source.json's
verification_methodology_note for the full account: M/32 is CONFIRMED
still current/in-force as of this build (18 Jul 2026); a draft
comprehensive نظام الإعلام remains unenacted.

VERIFICATION TIER -- TIER_1: BOE (laws.boe.gov.sa) via a near-live Wayback
Machine snapshot (26 Feb 2026, live portal unreachable this pass),
cross-checked against the Ministry of Media's own official PDF of this law
(media.gov.sa, structural/decree-number use only due to scrambled
extraction), further corroborated by WIPO Lex and nezams.com/qanoonsa.com.
This validator does not re-adjudicate any of this; it only checks internal
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
SRC = os.path.join(ROOT, "sources", "press", "law", "official_source",
                   "press_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "press", "law", "verified",
                       "press_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "press", "law", "verified",
                       "press_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "press_arabic_legal_llm",
                   "press_law_legal_llm_001_049.json")
N = 49
KEY_RE = r"press_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 43, "معدلة": 6, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 6  # flat, no أبواب/فصول grouping above them

TOP_STATUS_ORIGINAL = ("TIER_1_BOE_WAYBACK_FEB2026_NEARLIVE_CLEAN_TEXT_X_MEDIA_GOV_SA_"
                       "OFFICIAL_PDF_STRUCTURAL_SCRAMBLED_EXTRACTION_X_WIPOLEX_NEZAMS_"
                       "QANOONIAH_CROSSCHECK_LIVE_BOE_UNREACHABLE_DIRECT")
TOP_STATUS_AMENDED = ("TIER_1_BOE_WAYBACK_FEB2026_NEARLIVE_CLEAN_CHANGELOG_POPUP_TEXT_"
                      "INCORPORATED_MAIN_BODY_STALE_X_MEDIA_GOV_SA_OFFICIAL_PDF_STRUCTURAL_"
                      "SCRAMBLED_EXTRACTION_X_WIPOLEX_NEZAMS_QANOONIAH_CROSSCHECK_"
                      "LIVE_BOE_UNREACHABLE_DIRECT")
AMENDED_KEYS = {"press_art_005", "press_art_009", "press_art_036",
                "press_art_037", "press_art_038", "press_art_040"}
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
FLAGGED_DISCREPANCY_KEYS = {
    "press_art_all_currency_check_draft_media_law_pending",
    "press_art_005_009_036_037_038_040_boe_main_body_stale_vs_changelog",
    "press_art_048_predecessor_m17_1402h_full_repeal_confirmed_primary",
    "press_art_chapter1_untitled_no_abwab_structure",
    "press_art_media_gov_sa_pdf_scrambled_extraction",
    "press_art_006_016_017_boe_extra_space_artifacts",
    "press_art_companion_regulations_not_ingested",
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
    """Yield (lo, hi) for every leaf range in chapter_structure. This law
    has 6 flat structural groups with NO أبواب/فصول nesting above them."""
    for ch in chs:
        yield (int(ch["first_article"]), int(ch["last_article"]))


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
        e.append("[1c] expected %d flat chapter_structure entries, got %d" %
                  (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

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

    # the first chapter group (Articles 1-12) must be explicitly documented
    # as untitled in the source, not silently given a fabricated title
    first_ch = chs[0] if chs else {}
    if first_ch.get("section_ar") is not None:
        e.append("[1d] first chapter_structure entry should have section_ar=null "
                  "(untitled in source) with a documentary section_note_ar")
    if not first_ch.get("section_note_ar"):
        e.append("[1d] first chapter_structure entry missing section_note_ar "
                  "documenting the untitled first group")

    sc = Counter()
    for k, a in arts.items():
        expected_status = TOP_STATUS_AMENDED if k in AMENDED_KEYS else TOP_STATUS_ORIGINAL
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
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if k in AMENDED_KEYS and not a.get("original_2000_text"):
            e.append("[2] %s: amended article missing original_2000_text "
                      "(BOE's stale pre-amendment wording)" % k)
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

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("press_art_001", {})
    if "تعريفات" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected تعريفات definitions clause")
    if "وزارة الإعلام" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected وزارة الإعلام definition")
    art5 = arts.get("press_art_005", {})
    if "وزير الاستثمار" not in art5.get("text", ""):
        e.append("[2j] Article 5 missing expected current 'وزير الاستثمار' wording "
                  "(post both amendments)")
    if "وزير الاستثمار" in art5.get("original_2000_text", ""):
        e.append("[2j] Article 5 original_2000_text should be BOE's pre-amendment "
                  "wording (no investment-authority clause at all), not the amended text")
    art9 = arts.get("press_art_009", {})
    if "يلتزم كل مسؤول" not in art9.get("text", ""):
        e.append("[2j] Article 9 missing expected M/20-amended wording")
    art38 = arts.get("press_art_038", {})
    if "خمسمائة ألف ريال" not in art38.get("text", ""):
        e.append("[2j] Article 38 missing expected 500,000-riyal fine (M/20 wording)")
    art48 = arts.get("press_art_048", {})
    if "م/17" not in art48.get("text", "") or "1402" not in art48.get("text", ""):
        e.append("[2j] Article 48 missing expected predecessor repeal citation (M/17, 1402H)")
    art49 = arts.get("press_art_049", {})
    if "تسعين يومًا" not in art49.get("text", "") and "تسعين يوما" not in art49.get("text", ""):
        e.append("[2j] Article 49 missing expected 90-day entry-into-force clause")
    if src.get("decree") != "المرسوم الملكي رقم (م/32)" or src.get("decree_date_hijri") != "3/9/1421":
        e.append("[2j] decree/decree_date_hijri mismatch with verified M/32, 3/9/1421H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري (currency check confirmed still in force)")

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
        expected_status = TOP_STATUS_AMENDED if r["article_key"] in AMENDED_KEYS else TOP_STATUS_ORIGINAL
        if r.get("source_trust", {}).get("source_status") != expected_status.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Press Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Press and Publications Law")
    print("  - 49 records: 43 اصلية, 6 معدلة (Articles 5, 9, 36, 37, 38, 40); 0 ملغاة, 0 مضافة")
    print("  - 6 flat structural groups, NO أبواب/فصول labels in the source (Articles 1-12 "
          "untitled)")
    print("  - CURRENCY CHECK: M/32 CONFIRMED still current/in-force as of this build; a draft")
    print("    comprehensive نظام الإعلام remains unenacted (see discrepancy entries)")
    print("  - VERIFICATION TIER: TIER_1 -- BOE-via-Wayback-Machine (near-live snapshot, 26 Feb")
    print("    2026) x media.gov.sa's own official PDF (structural cross-check) x WIPO Lex x")
    print("    nezams.com/qanoonsa.com")
    print("  - Royal Decree M/32 (3/9/1421H / 29 Nov 2000G), approved via Council of Ministers")
    print("    Resolution 211 (1/9/1421H)")
    print("  - CONFIRMED FULL REPEAL (Article 48): repeals the prior 1982 Press and Publications")
    print("    Law (Royal Decree M/17, 13/4/1402H) in its entirety; predecessor NOT ingested")
    print("  - BOE-MAIN-BODY-STALE-VS-CHANGELOG anomaly documented and handled for Articles 5, 9,")
    print("    36, 37, 38, 40: amended wording ingested as current text; stale BOE wording kept")
    print("    verbatim in original_2000_text")
    print("  - Companion regulations identified but NOT ingested this pass: اللائحة التنفيذية")
    print("    لنظام المطبوعات والنشر; نظام المؤسسات الصحفية (M/20, 1422H -- a different M/20)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
