#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Private (National) Schools Regulation track
(لائحة تنظيم المدارس الأهلية, CoM Resolution 1006, 13/8/1395H). 24 articles,
flat (no أبواب/فصول), standalone (no base_law_key). 22 اصلية, 2 معدلة
(Articles 5 and 7).

See the generator's module docstring and this track's official_source.json
verification_methodology_note for the full account: TIER_1-candidate --
Ministry of Education's own official PDF, direct-fetched and vision-verified
in full across all 8 pages against pdftotext (byte-identical, no OCR/font
defects found). This validator does not re-adjudicate provenance; it only
checks internal self-consistency and that known discrepancies remain
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
SRC = os.path.join(ROOT, "sources", "private_schools_regulation", "law", "official_source",
                   "private_schools_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "private_schools_regulation", "law", "verified",
                       "private_schools_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "private_schools_regulation", "law", "verified",
                       "private_schools_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "private_schools_regulation_arabic_legal_llm",
                   "private_schools_regulation_legal_llm_001_024.json")

N = 24
KEY_RE = r"private_schools_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 22, "معدلة": 2, "ملغاة": 0, "مضافة": 0}
AMENDED_KEYS = {"private_schools_regulation_art_005", "private_schools_regulation_art_007"}
FLAGGED_DISCREPANCY_KEYS = {
    "private_schools_regulation_task_brief_resolution_number_check",
    "private_schools_regulation_art005_body_footnote_inconsistency",
    "private_schools_regulation_resolution89_single_source_only",
    "private_schools_regulation_boe_unreachable_connection_reset",
    "private_schools_regulation_tashkeel_and_layout_normalized",
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
        if not a.get("status") or not str(a.get("status")).strip():
            e.append("[2] %s: empty verification status string" % k)
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
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "قرار مجلس الوزراء رقم (1006)" or \
            src.get("decree_date_hijri") != "13/8/1395":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Resolution "
                 "1006, 13/8/1395H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري (not yet repealed -- "
                 "general_education_law repealing it is not yet in force)")
    if src.get("base_law_key") is not None:
        e.append("[2j] this is a standalone track; base_law_key must be null")
    art5 = arts.get("private_schools_regulation_art_005", {})
    if "ذوو الإعاقة" not in art5.get("text", ""):
        e.append("[2j] Article 5 must contain the CURRENT (post-269/1443H-amendment) "
                 "disability-inclusion text, not the pre-amendment wording")
    art7 = arts.get("private_schools_regulation_art_007", {})
    if "سعودي الجنسية" in art7.get("text", ""):
        e.append("[2j] Article 7 must NOT contain the deleted nationality "
                 "requirement in its current text (post-89/1440H amendment)")
    if "خمسة وعشرين" not in art7.get("text", ""):
        e.append("[2j] Article 7 missing expected age-25 condition")
    art22 = arts.get("private_schools_regulation_art_022", {})
    if "خمسمائة" not in art22.get("text", "") or "خمسة آلاف" not in art22.get("text", ""):
        e.append("[2j] Article 22 missing expected 500/5000 riyal fine range")
    art24 = arts.get("private_schools_regulation_art_024", {})
    if "الجريدة الرسمية" not in art24.get("text", ""):
        e.append("[2j] Article 24 (publication clause) missing expected gazette token")

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
        print("FAIL: %d error(s) in Private Schools Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Private (National) Schools Regulation (لائحة تنظيم المدارس الأهلية)")
    print("  - 24 records, flat (no أبواب/فصول), standalone (no base_law_key)")
    print("  - 22 اصلية, 2 معدلة (Article 5(e): CoM Res. 269, 3/5/1443H; Article "
          "7: CoM Res. 89, 7/2/1440H)")
    print("  - VERIFICATION TIER: TIER_1-candidate -- MOE official PDF, direct "
          "fetch, vision-verified in full across all 8 pages")
    print("  - legal_status_ar=ساري: general_education_law (which names this "
          "regulation for future repeal) is not yet in force")
    return 0


if __name__ == "__main__":
    sys.exit(main())
