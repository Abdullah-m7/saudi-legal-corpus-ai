#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Foreign Schools Regulation track (لائحة
المدارس الأجنبية, CoM Resolution 26, 4/2/1418H). 21 articles, flat (no
أبواب/فصول), standalone (no base_law_key). 19 اصلية, 2 معدلة (Articles 5
and 9).

See the generator's module docstring and this track's official_source.json
verification_methodology_note for the full account: TIER_2 -- two
independent non-governmental legal-portal sources (nezams.com,
bibliotdroit.com), word-for-word cross-verified, after laws.boe.gov.sa
(confirmed lawId, but HTTP 503) and moe.gov.sa (404) both proved
unreachable this pass. This validator does not re-adjudicate provenance; it
only checks internal self-consistency and that known discrepancies remain
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
SRC = os.path.join(ROOT, "sources", "foreign_schools_regulation", "law", "official_source",
                   "foreign_schools_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "foreign_schools_regulation", "law", "verified",
                       "foreign_schools_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "foreign_schools_regulation", "law", "verified",
                       "foreign_schools_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "foreign_schools_regulation_arabic_legal_llm",
                   "foreign_schools_regulation_legal_llm_001_021.json")

N = 21
KEY_RE = r"foreign_schools_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 19, "معدلة": 2, "ملغاة": 0, "مضافة": 0}
AMENDED_KEYS = {"foreign_schools_regulation_art_005", "foreign_schools_regulation_art_009"}
FLAGGED_DISCREPANCY_KEYS = {
    "foreign_schools_regulation_task_brief_resolution_number_correction",
    "foreign_schools_regulation_boe_lawid_confirmed_content_unreachable",
    "foreign_schools_regulation_publication_date_gazette_unconfirmed_direct",
    "foreign_schools_regulation_bibliotdroit_amendment_text_not_reproduced",
    "foreign_schools_regulation_no_base_law_standalone_track",
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
    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts if re.match(KEY_RE, k))
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not a clean 1..%d sequence: %s" % (N, nums))
    if src.get("chapter_structure") != []:
        e.append("[1c] this regulation is flat; chapter_structure must be []")

    sc = Counter()
    for k, a in arts.items():
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section_status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if a.get("section_ar") != "":
            e.append("[2] %s: section_ar must be empty for this flat instrument" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if k not in AMENDED_KEYS and a.get("history"):
            e.append("[2i] %s: non-amended article must have empty history[]" % k)
        if bool(a.get("is_mukarrar")):
            e.append("[2i] %s: no مكرر articles expected in this instrument" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the tier")
    if not src.get("preamble_ar"):
        e.append("[2l] preamble_ar must be populated -- verbatim preamble was located")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    # Honesty gate: the task brief's stated resolution number (36) must NOT
    # silently appear as this track's decree number -- verified number is 26.
    if src.get("decree") != "قرار مجلس الوزراء رقم (26)" or \
            src.get("decree_date_hijri") != "4/2/1418":
        e.append("[2g] decree/decree_date_hijri mismatch with verified Resolution "
                 "26, 4/2/1418H (NOT 36 -- see known_unresolved_discrepancies)")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري (not yet repealed -- "
                 "general_education_law repealing it is not yet in force)")
    if src.get("base_law_key") is not None:
        e.append("[2j] this is a standalone track; base_law_key must be null")
    art5 = arts.get("foreign_schools_regulation_art_005", {})
    if "ثلاث سنوات" in art5.get("text", ""):
        e.append("[2j] Article 5 must contain the CURRENT (post-220/1424H-amendment) "
                 "text, which removed the three-year cap")
    art9 = arts.get("foreign_schools_regulation_art_009", {})
    if "السفارة" not in art9.get("text", ""):
        e.append("[2j] Article 9 must contain the CURRENT (post-141/1439H-amendment) "
                 "embassy land-purchase paragraph")
    art16 = arts.get("foreign_schools_regulation_art_016", {})
    if "خمسين ألف" not in art16.get("text", ""):
        e.append("[2j] Article 16 missing expected 50,000 riyal fine cap")
    art21 = arts.get("foreign_schools_regulation_art_021", {})
    if "تسعين يوما" not in art21.get("text", "") and "تسعين يوماً" not in art21.get("text", ""):
        e.append("[2j] Article 21 (publication clause) missing expected 90-day clause")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: article_key not found in source" % r["article_key"]); continue
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("legal_status_ar") != a.get("legal_status_ar"):
            e.append("[4] %s: legal_status_ar mismatch" % r["article_key"])
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation'" % r["article_key"])
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
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation'" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Foreign Schools Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Foreign Schools Regulation (لائحة المدارس الأجنبية)")
    print("  - 21 records, flat (no أبواب/فصول), standalone (no base_law_key)")
    print("  - 19 اصلية, 2 معدلة (Article 5: CoM Res. 220, 10/8/1424H; Article 9: "
          "CoM Res. 141, 10/3/1439H)")
    print("  - VERIFICATION TIER: TIER_2 -- two independent non-governmental legal "
          "portals, word-for-word cross-verified; laws.boe.gov.sa lawId confirmed "
          "but unreachable (503)")
    print("  - Resolution number corrected from task brief's stated 36 to verified 26")
    print("  - legal_status_ar=ساري: general_education_law (which names this "
          "regulation for future repeal) is not yet in force")
    return 0


if __name__ == "__main__":
    sys.exit(main())
