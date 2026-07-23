#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation for Environmental Permits for
Establishing and Operating Activities track (11 records: 11 اصلية, 0 معدلة, 0 مضافة,
0 ملغاة; no chapter division -- each of the 11 articles carries its own descriptive
title).

VERIFICATION TIER -- TIER_2. See the generator's module docstring and
sources/environmental_permits/official_source/environmental_permits_reg_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa was checked FIRST
(per this corpus's standard methodology) but is unreachable this pass (HTTP 503) and,
more fundamentally, has no dedicated lawId page for this Implementing Regulation at
all (only for the base Environmental Law, lawId 63831ff6-...). The PRIMARY source
actually used is the Official Gazette (Umm Al-Qura / uqn.gov.sa, issue 4888, 25 June
2021), in two cross-verified renderings (clean official HTML for the ingested text +
the official born-digital gazette PDF as the authoritative facsimile, matched at
99.66% word-level via anagram-signature comparison). This validator does not
re-adjudicate any of this; it only checks internal self-consistency of the text this
track actually ingests, and that every disclosed discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "environmental_permits", "official_source",
                   "environmental_permits_reg_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "environmental_permits", "verified",
                       "environmental_permits_reg_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "environmental_permits", "verified",
                       "environmental_permits_reg_verified_summary.json")
LLM = os.path.join(ROOT, "data", "environmental_permits_reg_arabic_legal_llm",
                   "environmental_permits_reg_legal_llm_001_011.json")
N = 11
KEY_RE = r"environmental_permits_reg_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 11, "معدلة": 0, "ملغاة": 0, "مضافة": 0}

STATUS_UNCHANGED = "UNCHANGED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()

FLAGGED_DISCREPANCY_KEYS = {
    "environmental_permits_reg_boe_unreachable_no_dedicated_page",
    "environmental_permits_reg_decree_number_digit_grouping",
    "environmental_permits_reg_article1_hadha_typo",
    "environmental_permits_reg_annexes_out_of_scope",
    "environmental_permits_reg_effective_date_vs_press_application_date",
    "environmental_permits_reg_gazette_publication_gap",
    "environmental_permits_reg_no_named_predecessor_repeal",
    "environmental_permits_reg_family_scope_corroboration",
}
AR = "ء-ي"

# Expected article titles (descriptive) -- anchors the 11-article structure this pass.
EXPECTED_TITLES = {
    1: "التعريفات",
    2: "نطاق التطبيق",
    3: "نطاق عمل المركز بشأن تصاريح الإنشاء والتشغيل للأنشطة",
    4: "تصنيف الأنشطة وفق تأثيرها البيئي",
    5: "استمارة التصنيف البيئي للأنشطة",
    6: "التصاريح البيئية للإنشاء والتشغيل",
    7: "دراسة تقييم الأثر البيئي لأنشطة الفئة الثانية",
    8: "دراسة تقييم الأثر البيئي لأنشطة الفئة الثالثة",
    9: "أحكام عامة",
    10: "حق الاعتراض على قرارات المركز المتعلقة بالتصاريح البيئية",
    11: "ضبط المخالفات وإيقاع العقوبات",
}
AR_NUM = {1: "١", 2: "٢", 3: "٣", 4: "٤", 5: "٥", 6: "٦", 7: "٧", 8: "٨", 9: "٩",
          10: "١٠", 11: "١١"}


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

    # This regulation has NO chapter division -- assert the source did not fabricate one.
    if "chapter_structure" in src:
        e.append("[1c] chapter_structure must be ABSENT (this regulation has no فصول/أبواب; "
                 "each of the 11 articles carries its own descriptive title)")
    if not src.get("structure_note"):
        e.append("[1c] missing structure_note documenting the no-chapters / titled-articles structure")

    sc = Counter()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
        if a.get("status") != STATUS_UNCHANGED:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS_UNCHANGED, a.get("status")))
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
        if not a.get("title_ar"):
            e.append("[2] %s: missing title_ar" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present (justification kashida not stripped)" % k)
        # all-اصلية regulation: no amendment machinery expected
        if a.get("history"):
            e.append("[2i] %s: original article must have empty history[]" % k)
        if ls != "اصلية":
            e.append("[2] %s: all 11 articles must be اصلية this pass" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        # tashkeel must be stripped uniformly (display-layer normalization)
        if re.search("[ً-ْٰ]", a["text"]) or re.search("[ً-ْٰ]", a.get("title_ar", "")):
            e.append("[2f] %s: residual tashkeel (harakat) not stripped" % k)
        # number label must use Arabic-Indic digits matching the article number
        exp_label = "المادة (%s)" % AR_NUM[n]
        if a.get("number_label_ar") != exp_label:
            e.append("[2n] %s: number_label_ar %r != expected %r"
                     % (k, a.get("number_label_ar"), exp_label))
        # descriptive title must match the verified title for this article
        if EXPECTED_TITLES.get(n) and a.get("title_ar") != EXPECTED_TITLES[n]:
            e.append("[2t] %s: title_ar %r != verified %r" % (k, a.get("title_ar"), EXPECTED_TITLES[n]))

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
        e.append("[2k] missing amendment_history (must record the founding decision)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "43615/3/1/1442" not in decrees:
            e.append("[2k] amendment_history must reference founding decision 43615/3/1/1442")

    if not src.get("preamble_ar"):
        e.append("[2p] missing preamble_ar (recovered from the official gazette this pass)")
    else:
        pre = src["preamble_ar"]
        for must in ("43615/3/1/1442", "الثامنة والأربعين", "م/165", "729",
                     "ويلغي كل ما يتعارض معه من قرارات سابقة", "الفضلي"):
            if must not in pre:
                e.append("[2p] preamble_ar missing expected token %r" % must)

    # spot-checks anchoring key facts established this pass
    a1 = arts.get("environmental_permits_reg_art_001", {})
    if "هذ اللائحة" not in a1.get("text", ""):
        e.append("[2j] Article 1 must preserve the source typo 'هذ اللائحة' (for 'هذه'), "
                 "not silently corrected")
    if "المركز الوطني للرقابة على الالتزام البيئي" not in a1.get("text", ""):
        e.append("[2j] Article 1 missing expected definition of المركز (National Center for "
                 "Environmental Compliance)")
    a4 = arts.get("environmental_permits_reg_art_004", {})
    if "ثلاث فئات" not in a4.get("text", ""):
        e.append("[2j] Article 4 missing expected three-category classification (ثلاث فئات)")
    a11 = arts.get("environmental_permits_reg_art_011", {})
    if "الجدول (٢)" not in a11.get("text", "") and "الجدول (2)" not in a11.get("text", ""):
        e.append("[2j] Article 11 missing expected reference to the penalties table (الجدول 2)")
    a6 = arts.get("environmental_permits_reg_art_006", {})
    if "الجدول (١)" not in a6.get("text", "") and "الجدول (1)" not in a6.get("text", ""):
        e.append("[2j] Article 6 must retain its embedded Table (1) inline")

    if src.get("decree") != "قرار وزير البيئة والمياه والزراعة رقم (43615/3/1/1442)" \
            or src.get("decree_date_hijri") != "9/8/1442":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Minister Decision "
                 "43615/3/1/1442, 9/8/1442H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no article-level amendment found; "
                 "all 11 articles original)")
    if src.get("base_law_track_key") != "environmental":
        e.append("[2j] base_law_track_key must be 'environmental' (companion to the ingested "
                 "Environmental Law track)")

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
        if r.get("title_ar") != a.get("title_ar"):
            e.append("[4] %s: title_ar mismatch" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if summary.get("preamble_ar") != src.get("preamble_ar"):
        e.append("[4b] summary preamble_ar != source preamble_ar")

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
        if r.get("source_trust", {}).get("source_status") != STATUS_UNCHANGED.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Environmental Permits Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation for Environmental Permits for Establishing and Operating Activities")
    print("  - 11 records: 11 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة (no chapter division; each article titled)")
    print("  - VERIFICATION TIER: TIER_2 -- laws.boe.gov.sa checked first but unreachable this pass")
    print("    (HTTP 503) and confirmed to have no dedicated lawId page for this Implementing")
    print("    Regulation at all; PRIMARY source is the Official Gazette (Umm Al-Qura / uqn.gov.sa,")
    print("    issue 4888, 25 June 2021), clean HTML for ingested text cross-verified against the")
    print("    official born-digital gazette PDF at 99.66% word-level (anagram-signature match)")
    print("  - Minister of Environment Decision No. (43615/3/1/1442), 09/08/1442H, under Article 48")
    print("    of the Environmental Law (Royal Decree M/165, 19/11/1441H) -- companion to the")
    print("    ingested environmental_law track")
    print("  - REPEAL: negative finding -- generic conflict-repeal clause only, no named predecessor")
    print("  - SOURCE ANOMALY preserved: Article 1 prints 'هذ اللائحة' (for 'هذه'), verbatim in both")
    print("    HTML and PDF renderings -- kept, not silently corrected")
    print("  - 4 form/table annexes (ملاحق 1-4) + penalty Table 2 disclosed as out of scope")
    return 0


if __name__ == "__main__":
    sys.exit(main())
