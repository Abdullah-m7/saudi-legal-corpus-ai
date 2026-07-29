#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Regulatory Bylaw on Real Estate Marketing and
Advertising track (اللائحة التنظيمية للتسويق والإعلانات العقارية; 12
records, all اصلية; no فصل/chapter subdivisions in the official document).

VERIFICATION TIER -- see the generator's module docstring and
sources/real_estate_marketing_advertising_regulation/law/official_source/
real_estate_marketing_advertising_regulation_official_source.json's
verification_methodology_note for the full account. This validator asserts:
exactly 12 articles in a clean 1..12 run; chapter_structure is an empty list
(this Bylaw has no فصل headings at all, confirmed by direct visual
inspection of every page of the official PDF); all 12 articles are اصلية
with empty amendment history (single, first-and-only-confirmed edition); no
ملغاة/معدلة/مضافة articles this pass; article_title_ar is allowed to be an
empty string for every article because the primary source itself captions
each article only as "المادة <ordinal>:" with no further per-article title --
fabricating one would violate this corpus's no-fabrication policy.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "real_estate_marketing_advertising_regulation", "law",
                   "official_source",
                   "real_estate_marketing_advertising_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "real_estate_marketing_advertising_regulation", "law",
                       "verified", "real_estate_marketing_advertising_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "real_estate_marketing_advertising_regulation", "law",
                       "verified", "real_estate_marketing_advertising_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "real_estate_marketing_advertising_regulation_arabic_legal_llm",
                   "real_estate_marketing_advertising_regulation_legal_llm_001_012.json")
N = 12
KEY_RE = r"real_estate_marketing_advertising_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 12, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
STATUS = "REGA_BOARD_RESOLUTION_PDF_PRIMARY_VISUAL_REEXTRACTION_PRESS_CORROBORATED"
FLAGGED_DISCREPANCY_KEYS = {
    "real_estate_marketing_advertising_regulation_resolution_number_digit_order",
    "real_estate_marketing_advertising_regulation_uqn_gazette_page_not_located",
    "real_estate_marketing_advertising_regulation_no_chapter_headings",
    "real_estate_marketing_advertising_regulation_pdf_text_layer_corruption",
    "real_estate_marketing_advertising_regulation_istitlaa_draft_excluded",
    "real_estate_marketing_advertising_regulation_no_article_titles",
    "real_estate_marketing_advertising_regulation_waf_curl_blocked",
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
    if chapters != []:
        e.append("[1c] chapter_structure must be an empty list for this chapterless Bylaw, "
                 "got %r" % chapters)

    if src.get("consolidated_amended_law") is not False:
        e.append("[1d] consolidated_amended_law must be False for this track")

    sc = Counter()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or unexpected latin/html leftovers" % k)
        if a.get("article_title_ar") is None:
            e.append("[2] %s: article_title_ar must be present (empty string allowed)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2] %s: residual Eastern-Arabic-Indic digit (must be normalized)" % k)
        if "  " in a["text"]:
            e.append("[2] %s: residual double-space artifact" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)

        # single, first-and-only-confirmed edition: every article must be اصلية, no history
        if ls != "اصلية":
            e.append("[3] %s: article %d expected اصلية (no amendment confirmed this pass), "
                     "got %r" % (k, n, ls))
        if a.get("history"):
            e.append("[3] %s: article %d must have empty history (اصلية-only track)" % (k, n))

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))
    declared = src.get("status_counts") or {}
    for st in ALLOWED_STATUS:
        if declared.get(st, 0) != sc.get(st, 0):
            e.append("[2f] declared status_counts[%s] does not match actual per-article counts" % st)

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the tier")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    if src.get("law_component") != "regulation":
        e.append("[2j] law_component must be 'regulation'")
    if src.get("legal_status_ar") != "نافذ":
        e.append("[2j] legal_status_ar must be نافذ")

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
    if summary.get("chapter_structure") != []:
        e.append("[4b] summary chapter_structure must be an empty list")

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
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    # Article 5 must carry exactly the 8 mandatory disclosures (أ through ح) per this track's
    # own commissioning brief ("mandates an independent ad-license with 8 required disclosures").
    art5 = arts.get("real_estate_marketing_advertising_regulation_art_005", {})
    disclosure_markers = ["أ-", "ب-", "ج-", "د-", "هـ-", "و-", "ز-", "ح-"]
    missing_markers = [m for m in disclosure_markers if m not in art5.get("text", "")]
    if missing_markers:
        e.append("[6] Article 5 missing expected disclosure markers: %s" % missing_markers)

    if e:
        print("FAIL: %d error(s) in Real Estate Marketing/Advertising Regulation track:" % len(e))
        for x in e[:25]:
            print("  - %s" % x)
        return 1
    print("PASS: Regulatory Bylaw on Real Estate Marketing and Advertising — 12 records "
          "(12 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; no فصل subdivisions)")
    print("  - TIER ASSESSED: TIER_1 -- REGA official regulation catalog page + Board Resolution")
    print("    PDF (rega.gov.sa, the issuing authority's own domain), article text independently")
    print("    re-extracted by direct visual reading of rendered page images of the SAME PDF")
    print("    (its own text layer has a silent letter-substitution bug and was used only for")
    print("    navigation, never as wording source)")
    print("  - Press/secondary corroboration (SPA, Argaam, Okaz, Amlak, LexisNexis) confirms")
    print("    structure/dates/provisions but was never used as an Arabic wording source")
    print("  - istitlaa.ncc.gov.sa draft-consultation page located via search but deliberately")
    print("    NEVER fetched or used, per this task's explicit draft-exclusion instruction")
    print("  - Direct Umm Al-Qura Gazette (uqn.gov.sa) page for this specific Bylaw could NOT")
    print("    be located this pass -- flagged, not silently asserted as cross-checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
