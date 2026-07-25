#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Agriculture Law track (اللائحة
التنفيذية لنظام الزراعة, Ministerial Decision 14967/1/1444, 15/1/1444H).

271 records across nine أبواب: 266 اصلية, 5 معدلة (Article 1 -- 2024 amendment fully confirmed
and incorporated; Articles 45/98/208/248 -- 2026 amendment confirmed to exist but its new
wording could not be independently retrieved this pass, so the pre-amendment text is kept and
explicitly flagged status="AMENDED_TEXT_UNCONFIRMED" / text_complete=False), 0 مضافة, 0 ملغاة.

This validator does not re-adjudicate provenance; it checks internal self-consistency of the
ingested text and that every known discrepancy is still recorded. See the generator's docstring
and the source artifact's verification_methodology_note for the full provenance chain (Umm
Al-Qura Official Gazette full text, cross-checked against mewa.gov.sa and qanoonsa.com;
TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE due to the four Articles with unconfirmed amended text).

NOTE ON LATIN CHARACTERS: unlike the base law (a flat statute with no embedded Latin), this
Regulation's primary source genuinely contains embedded Latin tokens in a handful of articles
(scientific species names e.g. "Apis mellifera", standard/document-type codes e.g. "GSO993/2015",
"CI", "BOL", "PL", "CO", org acronyms e.g. "OIE", "GPS"). This validator therefore does NOT flag
bare Latin letters as artifacts; it only flags genuine leftover-markup indicators (angle
brackets, HTML entity ampersands, curly quotes, non-breaking spaces, residual tashkeel/tatweel).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "agriculture_regulation", "law", "official_source",
                   "agriculture_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "agriculture_regulation", "law", "verified",
                       "agriculture_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "agriculture_regulation", "law", "verified",
                       "agriculture_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "agriculture_regulation_arabic_legal_llm",
                   "agriculture_regulation_legal_llm_001_271.json")
N = 271
KEY_RE = r"agriculture_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 266, "معدلة": 5, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_BAB_COUNT = 9

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_AMENDED_UNCONFIRMED = "AMENDED_TEXT_UNCONFIRMED"
ALLOWED_TOP_STATUS = {STATUS_UNCHANGED, STATUS_AMENDED, STATUS_AMENDED_UNCONFIRMED}

# Article 1: amendment CONFIRMED and fully incorporated (2024 decision 15065837).
FULLY_AMENDED_KEYS = {"agriculture_regulation_art_001"}
# Articles 45/98/208/248: amendment CONFIRMED to exist (2026 decision 15227269) but the new
# wording is NOT confirmed -- pre-amendment text kept, explicitly flagged.
AMENDED_TEXT_UNCONFIRMED_KEYS = {"agriculture_regulation_art_045", "agriculture_regulation_art_098",
                                  "agriculture_regulation_art_208", "agriculture_regulation_art_248"}
AMENDED_KEYS = FULLY_AMENDED_KEYS | AMENDED_TEXT_UNCONFIRMED_KEYS
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()

EXPECTED_STATUS_BY_KEY = {k: STATUS_AMENDED for k in FULLY_AMENDED_KEYS}
EXPECTED_STATUS_BY_KEY.update({k: STATUS_AMENDED_UNCONFIRMED for k in AMENDED_TEXT_UNCONFIRMED_KEYS})

FLAGGED_DISCREPANCY_KEYS = {
    "agriculture_regulation_boe_unreachable_and_not_indexed",
    "agriculture_regulation_mewa_pdf_font_corruption_not_used_verbatim",
    "agriculture_regulation_article1_2024_amendment_incorporated",
    "agriculture_regulation_2026_amendment_text_unavailable_art45_98_208_248",
    "agriculture_regulation_pending_article245_consultation_not_incorporated",
    "agriculture_regulation_founding_decision_preamble_not_captured",
    "agriculture_regulation_farsi_yeh_normalized_art1",
    "agriculture_regulation_mixed_digit_rendering_preserved",
    "agriculture_regulation_breakline_marker_extraction_self_corrected",
    "agriculture_regulation_gregorian_dates_secondary_only_for_2022_publication",
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

    chs = src.get("chapter_structure")
    if not chs or len(chs) != EXPECTED_TOP_LEVEL_BAB_COUNT:
        e.append("[1c] expected %d أبواب, got %d" % (EXPECTED_TOP_LEVEL_BAB_COUNT, len(chs or [])))
    else:
        # verify أبواب article ranges are contiguous 1..271 with no gaps/overlaps
        covered = []
        for c in chs:
            rng = c["articles"]
            if "-" in rng:
                a0, b0 = (int(x) for x in rng.split("-"))
            else:
                a0 = b0 = int(rng)
            covered.append((a0, b0))
        covered.sort()
        expect_next = 1
        for a0, b0 in covered:
            if a0 != expect_next:
                e.append("[1c] chapter_structure range gap/overlap: expected start %d, got %d"
                         % (expect_next, a0))
            expect_next = b0 + 1
        if expect_next - 1 != N:
            e.append("[1c] chapter_structure ranges do not cover all %d articles (covered up to %d)"
                     % (N, expect_next - 1))

    sc = Counter()
    for k, a in arts.items():
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNCHANGED)
        if a.get("status") != expected_status:
            e.append("[2] %s: expected status %r, got %r" % (k, expected_status, a.get("status")))
        if a.get("status") not in ALLOWED_TOP_STATUS:
            e.append("[2] %s: status %r not in allowed set" % (k, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if not a["text"].strip():
            e.append("[2] %s: empty text" % k)
        if re.search(r"[<>&]", a["text"]):
            e.append("[2] %s: leftover markup artifact (<, >, or &)" % k)
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
        if k in AMENDED_TEXT_UNCONFIRMED_KEYS and a.get("text_complete") is not False:
            e.append("[2i] %s: amended-text-unconfirmed article must have text_complete=False"
                     % k)
        if k in FULLY_AMENDED_KEYS and a.get("text_complete") is not True:
            e.append("[2i] %s: fully-confirmed-amendment article must have text_complete=True"
                     % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if re.search(r"[ً-ٰٟ]", a["text"]):
            e.append("[2g] %s: residual tashkeel/diacritics not stripped" % k)
        if re.search(r"[کی]", a["text"]):
            e.append("[2g] %s: non-standard Arabic-presentation letter (Farsi yeh/keheh) present"
                     % k)
        if not a.get("number_label_ar", "").startswith("المادة "):
            e.append("[2h] %s: number_label_ar must start with 'المادة '" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    if not src.get("amendment_history") or len(src["amendment_history"]) != 3:
        e.append("[2k] amendment_history must record exactly 3 entries (founding + 2 amendments)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        for token in ("14967", "15065837", "15227269"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference decision %s" % token)

    if src.get("issuing_decision") != "القرار الوزاري رقم (14967/1/1444)" \
            or src.get("issuing_decision_date_hijri") != "15/1/1444":
        e.append("[2j] issuing_decision/date mismatch with verified Ministerial Decision "
                 "14967/1/1444, 15/1/1444H")
    if src.get("base_law_decree") != "المرسوم الملكي رقم (م/64)":
        e.append("[2j] base_law_decree must reference the Agriculture Law (M/64)")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (Article 1 merges base + 2024 "
                 "amendment text)")
    if src.get("verification_tier") != "TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE":
        e.append("[2j] verification_tier must be TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE "
                 "(documented per-article variation on Arts. 45/98/208/248)")
    if src.get("has_per_article_variation") is not True:
        e.append("[2j] has_per_article_variation must be True")

    art1 = arts.get("agriculture_regulation_art_001", {})
    if "المخالفة الجسيمة" not in art1.get("text", ""):
        e.append("[2j] Article 1 must incorporate the confirmed 2024 'المخالفة الجسيمة' "
                 "amendment")
    if "الوزارة: وزارة البيئة والمياه والزراعة" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (الوزارة)")
    art271 = arts.get("agriculture_regulation_art_271", {})
    if "مجلس التعاون" not in art271.get("text", ""):
        e.append("[2j] Article 271 (final article) missing expected GCC-precedence clause")
    art271_label = art271.get("number_label_ar")
    if art271_label != "المادة الحادية والسبعون بعد المائتين":
        e.append("[2j] Article 271 number_label_ar must be 'المادة الحادية والسبعون بعد "
                 "المائتين', got %r" % art271_label)
    for k in AMENDED_TEXT_UNCONFIRMED_KEYS:
        a = arts.get(k, {})
        hist_note = " ".join(str(h.get("note", "")) + " " + str(h.get("decree", ""))
                             for h in a.get("history", []))
        if "15227269" not in hist_note:
            e.append("[2j] %s: history must reference decision 15227269" % k)

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
        print("FAIL: %d error(s) in Agriculture Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Implementing Regulation of the Agriculture Law (اللائحة التنفيذية لنظام الزراعة)")
    print("  - 271 records across 9 أبواب: 266 اصلية, 5 معدلة, 0 مضافة, 0 ملغاة")
    print("  - INSTRUMENT CONFIRMED: Ministerial Decision 14967/1/1444, 15/1/1444H (MEWA), under")
    print("    Article 36 of the Agriculture Law (Royal Decree M/64, 10/8/1442H). Standalone")
    print("    companion track, built independently this pass.")
    print("  - FULL TEXT SOURCE: Umm Al-Qura Official Gazette (uqn.gov.sa) -- a primary")
    print("    government source -- cross-verified structurally/substantively against MEWA's")
    print("    own PDF (mewa.gov.sa) and qanoonsa.com.")
    print("  - AMENDMENT 1 (CONFIRMED + INCORPORATED): Decision 15065837, 15/3/1446H -- Article 1")
    print("    gained the 'المخالفة الجسيمة' definition.")
    print("  - AMENDMENT 2 (CONFIRMED TO EXIST, TEXT UNCONFIRMED): Decision 15227269, 15/12/1447H")
    print("    -- Articles 45, 98, 208, and para.(5) of 248 touched, but the new wording could")
    print("    not be retrieved this pass; pre-amendment text kept, honestly flagged")
    print("    status=AMENDED_TEXT_UNCONFIRMED / text_complete=False.")
    print("  - VERIFICATION TIER: TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE (documented")
    print("    per-article variation on the 4 articles above; the remaining 267 are")
    print("    TIER_2-equivalent). See known_unresolved_discrepancies before legal/research use")
    print("    of Articles 45, 98, 208, or 248.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
