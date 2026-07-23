#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Saudi Arabian
Franchise Law track (16 records: 16 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; 6 chapters).

VERIFICATION TIER -- see the generator's module docstring and
sources/franchise/regulation/official_source/franchise_regulation_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa was checked
FIRST (per this corpus's standard methodology) -- it has a dedicated lawId page
for the base Franchise LAW but NONE for this Implementing Regulation (Ministerial
regulations are not catalogued there as standalone lawId records; direct query
returned HTTP 503 this pass). The PRIMARY source actually used for the article
text is franchising.sa (a clean Umm Al-Qura gazette reproduction that links the
official uqn.gov.sa PDF), cross-verified VERBATIM against aunklaw.com (all 16
articles) and against lexismiddleeast.com (Sader/LexisNexis) for the instrument
metadata and six-chapter structure. This validator does not re-adjudicate any of
this; it only checks internal self-consistency of the text this track ingests,
and that every discrepancy is still recorded.

Note this track differs from food_regulation in three deliberate, disclosed
ways: (1) all 16 articles are اصلية -- the one confirmed amendment (deletion of
annex element 13) affects the separate Disclosure-Document annex, NOT any
numbered article; (2) consolidated_amended_law is False (the articles were not
amended); (3) a preamble_ar (the issuance resolution) IS present and an annex_ar
IS present -- both preserved verbatim. The food-specific PDF font-ligature
regression guards are not applicable here (the source is clean HTML text, not a
scanned/born-digital PDF) and are intentionally omitted.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "franchise", "regulation", "official_source",
                   "franchise_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "franchise", "regulation", "verified",
                       "franchise_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "franchise", "regulation", "verified",
                       "franchise_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "franchise_regulation_arabic_legal_llm",
                   "franchise_regulation_legal_llm_001_016.json")
N = 16
KEY_RE = r"franchise_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 16, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 6

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY = {}
for k in AMENDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_AMENDED
for k in ADDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_ADDED
FLAGGED_DISCREPANCY_KEYS = {
    "franchise_regulation_gap_map_candidate_confirmed",
    "franchise_regulation_boe_no_dedicated_page",
    "franchise_regulation_official_pdf_not_directly_fetched",
    "franchise_regulation_annex_element13_deleted",
    "franchise_regulation_annex_not_split_into_article_records",
    "franchise_regulation_article_headers_trailing_colon_source_style",
    "franchise_regulation_preamble_secondary_variants",
    "franchise_regulation_issuance_vs_gazette_date",
    "franchise_regulation_no_named_predecessor_repealed",
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
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapters, got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one chapter range" % n)
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
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
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
        if k not in (AMENDED_KEYS | ADDED_KEYS) and a.get("history"):
            e.append("[2i] %s: non-amended/added article must have empty history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
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
        e.append("[2k] missing amendment_history (must record founding 591 + annex-amending 339)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "591" not in decrees:
            e.append("[2k] amendment_history must reference founding decree 591")
        if "339" not in decrees:
            e.append("[2k] amendment_history must reference annex-amending decree 339")

    # annex must be preserved verbatim, in its ORIGINAL 17-element form, with the
    # deleted element (13) retained (flag-don't-delete), and its deletion disclosed.
    annex = src.get("annex_ar")
    if not annex or not annex.get("text"):
        e.append("[2n] missing annex_ar (Disclosure-Document Requirements) verbatim preservation")
    else:
        if annex.get("element_count_original") != 17:
            e.append("[2n] annex element_count_original must be 17 (original as-gazetted)")
        if "معلومات الوضع المالي لمانح الامتياز" not in annex["text"]:
            e.append("[2n] annex must RETAIN deleted element 13 text (flag-don't-delete rule)")
        if "متطلبات وثيقة الإفصاح" not in annex["text"]:
            e.append("[2n] annex text missing its own title heading")

    # preamble (issuance resolution) must be present and name the issuing Minister
    pre = src.get("preamble_ar") or ""
    if not pre:
        e.append("[2p] preamble_ar (issuance resolution) should be present and verbatim")
    else:
        if "القصبي" not in pre:
            e.append("[2p] preamble_ar must name the issuing Minister (القصبي)")
        if "السادسة والعشرين" not in pre:
            e.append("[2p] preamble_ar must cite enabling Article 26 of the Franchise Law")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("franchise_regulation_art_001", {})
    if "المرسوم الملكي رقم (م/22)" not in art1.get("text", "") \
            or "نظام الامتياز التجاري" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected reference to the Franchise Law (م/22) "
                 "definitions")
    art3 = arts.get("franchise_regulation_art_003", {})
    if "تسعين" not in art3.get("text", ""):
        e.append("[2j] Article 3 missing expected (تسعين) 90-day registration period")
    art4 = arts.get("franchise_regulation_art_004", {})
    if "خمسمائة" not in art4.get("text", "") or "مائة" not in art4.get("text", ""):
        e.append("[2j] Article 4 missing expected registration fee amounts (خمسمائة / مائة)")
    art13 = arts.get("franchise_regulation_art_013", {})
    if "الهيئة السعودية للملكية الفكرية" not in art13.get("text", ""):
        e.append("[2j] Article 13 missing expected reference to SAIP (الهيئة السعودية للملكية "
                 "الفكرية)")
    art16 = arts.get("franchise_regulation_art_016", {})
    if "تنشر هذه اللائحة في الجريدة الرسمية" not in art16.get("text", ""):
        e.append("[2j] Article 16 (final) missing expected publication/effect clause")
    if src.get("decree") != "قرار وزير التجارة رقم (591)" \
            or src.get("decree_date_hijri") != "18/9/1441":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Ministerial Resolution "
                 "591, 18/9/1441H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (the 16 articles were NOT amended; "
                 "the sole confirmed amendment deletes annex element 13 only)")

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
        print("FAIL: %d error(s) in Franchise Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Saudi Arabian Franchise Law")
    print("  - 16 records: 16 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (6 chapters)")
    print("  - VERIFICATION TIER: laws.boe.gov.sa checked first -- has a lawId page for the base")
    print("    Franchise LAW but NONE for this Implementing Regulation (Ministerial reg not")
    print("    catalogued); PRIMARY text source is franchising.sa (Umm Al-Qura gazette")
    print("    reproduction linking the official uqn.gov.sa PDF), cross-verified VERBATIM against")
    print("    aunklaw.com (all 16 articles) and against lexismiddleeast.com (Sader/LexisNexis)")
    print("    for instrument metadata + six-chapter structure")
    print("  - Minister of Commerce Resolution No. (591) [also (00591)], 18/9/1441H, issued under")
    print("    Article 26 of the Franchise Law (Royal Decree M/22, 9/2/1441H); Umm Al-Qura issue")
    print("    4832, 22 May 2020, p.12")
    print("  - CONFIRMED AMENDMENT (annex only, NOT any numbered article): element (13) 'معلومات")
    print("    الوضع المالي لمانح الامتياز' of the Disclosure-Document annex was deleted (Ministerial")
    print("    Resolution 339, 14/8/1444H per secondary source); corroborated by the 2020-vs-2024")
    print("    annex divergence. Annex preserved verbatim in ORIGINAL 17-element form (element 13")
    print("    retained not deleted), per the flag-don't-delete rule")
    print("  - This Regulation names NO predecessor it repeals")
    return 0


if __name__ == "__main__":
    sys.exit(main())
