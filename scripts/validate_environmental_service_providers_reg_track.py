#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation for Environmental Service
Providers under the Environmental Law track (13 records: 12 articles + Table (1), all
اصلية within the in-force version; no chapter/باب division -- each article carries its
own descriptive title, followed by Table (1) "المخالفات والعقوبات" ingested as a
distinct is_table entry).

VERIFICATION TIER -- TIER_2. See the generator's module docstring and
sources/environmental_service_providers/official_source/environmental_service_providers_reg_official_source.json's
verification_methodology_note for the full account: the in-force version is Minister of
Environment Decision No. (1515009/1), 3/7/1446H (Umm Al-Qura issue 5063, 5 Jan 2025),
which WHOLLY REPLACES the founding Decision No. (582979/1/1442), 14/11/1442H -- the exact
self-supersession pattern of the two sibling re-issuances. laws.boe.gov.sa was checked
FIRST but has no dedicated lawId page for this regulation. The GOVERNMENT-PRIMARY source
is the issuing ministry's own scanned PDF in MEWA's RulesLibrary (read visually page-by-
page), cross-verified against the clean linear HTML on qanoonsa.com/p/506302 (the source
of the ingested article text). This validator does not re-adjudicate any of this; it only
checks internal self-consistency of the text this track actually ingests, and that every
disclosed discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "environmental_service_providers", "official_source",
                   "environmental_service_providers_reg_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "environmental_service_providers", "verified",
                       "environmental_service_providers_reg_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "environmental_service_providers", "verified",
                       "environmental_service_providers_reg_verified_summary.json")
LLM = os.path.join(ROOT, "data", "environmental_service_providers_reg_arabic_legal_llm",
                   "environmental_service_providers_reg_legal_llm_001_012.json")
N_ART = 12          # numbered articles
N_TABLE = 1         # Table (1)
N_TOTAL = N_ART + N_TABLE
ART_RE = r"environmental_service_providers_reg_art_(\d{3})$"
TABLE_RE = r"environmental_service_providers_reg_table_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 13, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
STATUS_UNCHANGED = "UNCHANGED"

FLAGGED_DISCREPANCY_KEYS = {
    "environmental_service_providers_reg_boe_unreachable_no_dedicated_page",
    "environmental_service_providers_reg_1515009_vs_582979_resolution",
    "environmental_service_providers_reg_decree_number_slash_grouping",
    "environmental_service_providers_reg_date_cluster",
    "environmental_service_providers_reg_text_source_and_cross_verification",
    "environmental_service_providers_reg_table1_included_as_entry",
    "environmental_service_providers_reg_broken_word_normalized",
    "environmental_service_providers_reg_sibling_regs_cross_reference",
}
AR = "ء-ي"

EXPECTED_TITLES = {
    1: "التعريفات",
    2: "نطاق التطبيق",
    3: "نطاق عمل الجهة المختصة بشأن مقدمي الخدمات",
    4: "تصنيف الخدمات البيئية",
    5: "فئات تصنيف مقدمي الخدمات",
    6: "ترخيص وتصنيف مقدمي الخدمات",
    7: "تعديل التصنيف وأنواع الخدمات المقدمة للتراخيص السارية",
    8: "قيد مقدمي الخدمات",
    9: "ضوابط واشتراطات مزاولة العمل",
    10: "الرقابة على أداء مقدمي الخدمات",
    11: "المسؤولية النظامية لمقدمي الخدمات والجزاءات الإدارية",
    12: "ضبط المخالفات وإيقاع العقوبات",
}
EXPECTED_LABELS = {
    1: "المادة (الأولى)", 2: "المادة (الثانية)", 3: "المادة (الثالثة)",
    4: "المادة (الرابعة)", 5: "المادة (الخامسة)", 6: "المادة (السادسة)",
    7: "المادة (السابعة)", 8: "المادة (الثامنة)", 9: "المادة (التاسعة)",
    10: "المادة (العاشرة)", 11: "المادة (الحادية عشرة)", 12: "المادة (الثانية عشرة)",
}


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

    art_keys = [k for k in arts if re.match(ART_RE, k)]
    table_keys = [k for k in arts if re.match(TABLE_RE, k)]
    if len(arts) != N_TOTAL:
        e.append("[1] %d entries != %d" % (len(arts), N_TOTAL))
    if len(art_keys) != N_ART:
        e.append("[1] %d article entries != %d" % (len(art_keys), N_ART))
    if len(table_keys) != N_TABLE:
        e.append("[1] %d table entries != %d" % (len(table_keys), N_TABLE))
    if src.get("article_count") != N_ART:
        e.append("[1] article_count field != %d" % N_ART)
    if src.get("table_count") != N_TABLE:
        e.append("[1] table_count field != %d" % N_TABLE)
    for k in arts:
        if not (re.match(ART_RE, k) or re.match(TABLE_RE, k)):
            e.append("[1] %s: does not match key pattern" % k)

    # chapter_structure documents the (articles + table) grouping (no فصول/أبواب).
    if not src.get("chapter_structure"):
        e.append("[1c] missing chapter_structure documenting the articles + table grouping")
    if not src.get("structure_note"):
        e.append("[1c] missing structure_note documenting the no-chapters / titled-articles + table structure")

    sc = Counter()
    for k, a in arts.items():
        is_table = bool(a.get("is_table"))
        m = re.match(ART_RE, k) or re.match(TABLE_RE, k)
        n = a.get("article_number")
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
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if a.get("history"):
            e.append("[2i] %s: original entry must have empty history[]" % k)
        if ls != "اصلية":
            e.append("[2] %s: all entries must be اصلية this pass" % k)
        if a.get("is_mukarrar"):
            e.append("[2] %s: no mukarrar entries expected" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact" % k)
        if re.search("[​‌‍‎‏﻿]", a["text"]):
            e.append("[2f] %s: residual bidi/zero-width mark not stripped" % k)
        if re.search("[ً-ْٰ]", a["text"]) or re.search("[ً-ْٰ]", a.get("title_ar", "")):
            e.append("[2f] %s: residual tashkeel (harakat) not stripped" % k)
        if "الش عب" in a["text"]:
            e.append("[2f] %s: broken-word artifact 'الش عب' not normalized to 'الشعب'" % k)

        if not is_table:
            exp_label = EXPECTED_LABELS.get(n)
            if a.get("number_label_ar") != exp_label:
                e.append("[2n] %s: number_label_ar %r != expected %r"
                         % (k, a.get("number_label_ar"), exp_label))
            if EXPECTED_TITLES.get(n) and a.get("title_ar") != EXPECTED_TITLES[n]:
                e.append("[2t] %s: title_ar %r != verified %r" % (k, a.get("title_ar"), EXPECTED_TITLES[n]))
        else:
            if a.get("number_label_ar") != "الجدول (١)":
                e.append("[2n] %s: table number_label_ar %r != 'الجدول (١)'" % (k, a.get("number_label_ar")))
            if a.get("title_ar") != "المخالفات والعقوبات":
                e.append("[2t] %s: table title_ar %r != 'المخالفات والعقوبات'" % (k, a.get("title_ar")))

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

    if not src.get("amendment_history"):
        e.append("[2k] missing amendment_history")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        for tok in ("582979/1/1442", "1515009/1"):
            if tok not in decrees:
                e.append("[2k] amendment_history must reference %s" % tok)

    if not src.get("preamble_ar"):
        e.append("[2p] missing preamble_ar")
    else:
        pre = src["preamble_ar"]
        for must in ("582979/1/1442", "الثامنة والأربعين", "م/165", "32043", "406",
                     "تحل هذه اللائحة محل", "الفضلي"):
            if must not in pre:
                e.append("[2p] preamble_ar missing expected token %r" % must)

    # spot-checks anchoring key facts established this pass
    a1 = arts.get("environmental_service_providers_reg_art_001", {})
    if "مقدمو الخدمات" not in a1.get("text", ""):
        e.append("[2j] Article 1 missing expected definition of مقدمو الخدمات")
    if "المؤسسة العامة للمحافظة على الشعب المرجانية والسلاحف في البحر الأحمر" not in a1.get("text", ""):
        e.append("[2j] Article 1 missing expected competent-authority definition (coral-reef authority)")
    a4 = arts.get("environmental_service_providers_reg_art_004", {})
    if "١٧-" not in a4.get("text", ""):
        e.append("[2j] Article 4 missing expected 17-item environmental-services classification (١٧-)")
    if "الشعب المرجانية" not in a4.get("text", ""):
        e.append("[2j] Article 4 must contain 'الشعب المرجانية' (broken-word artifact normalized)")
    a11 = arts.get("environmental_service_providers_reg_art_011", {})
    if "الجدول رقم (١)" not in a11.get("text", "") and "الجدول (١)" not in a11.get("text", ""):
        e.append("[2j] Article 11 missing expected reference to Table (1)")
    a12 = arts.get("environmental_service_providers_reg_art_012", {})
    if "الجدول (١)" not in a12.get("text", ""):
        e.append("[2j] Article 12 missing expected reference to Table (1)")
    tbl = arts.get("environmental_service_providers_reg_table_001", {})
    ttext = tbl.get("text", "")
    if "جسيمة" not in ttext or "يطبق مبدأ الإنذار" not in ttext:
        e.append("[2j] Table (1) missing expected penalty-type tokens (جسيمة / يطبق مبدأ الإنذار)")
    if "لجان النظر في مخالفات أحكام نظام البيئة" not in ttext:
        e.append("[2j] Table (1) missing expected footnote (environmental-law violations committees)")
    # 13 data rows -> row markers ١..١٣ ; check first and last row numbers present
    if not re.search(r"(^|\n)١ \|", ttext) or "١٣ |" not in ttext:
        e.append("[2j] Table (1) must contain 13 numbered rows (١ .. ١٣)")

    if src.get("decree") != "قرار وزير البيئة والمياه والزراعة رقم (1515009/1)" \
            or src.get("decree_date_hijri") != "3/7/1446":
        e.append("[2j] decree/decree_date_hijri mismatch with in-force Decision 1515009/1, 3/7/1446H")
    if "582979/1/1442" not in (src.get("predecessor_decree") or ""):
        e.append("[2j] predecessor_decree must reference the superseded Decision 582979/1/1442")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (whole-replacement re-issuance)")
    if src.get("base_law_track_key") != "environmental":
        e.append("[2j] base_law_track_key must be 'environmental'")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N_TOTAL:
        e.append("[4] %d verified records != %d" % (len(ver), N_TOTAL))
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
        if bool(r.get("is_table")) != bool(a.get("is_table")):
            e.append("[4] %s: is_table mismatch" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N_TOTAL:
        e.append("[4b] summary record_count != %d" % N_TOTAL)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if summary.get("preamble_ar") != src.get("preamble_ar"):
        e.append("[4b] summary preamble_ar != source preamble_ar")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N_TOTAL or len(recs) != N_TOTAL:
        e.append("[5] llm count != %d" % N_TOTAL)
    if llm.get("article_range") != [1, N_ART]:
        e.append("[5] llm article_range != [1, %d]" % N_ART)
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
        print("FAIL: %d error(s) in Environmental Service Providers Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation for Environmental Service Providers under the Environmental Law")
    print("  - 13 records: 12 articles + Table (1); all اصلية within the in-force version")
    print("    (no chapter/باب division; each article titled; Table (1) ingested as a distinct is_table entry)")
    print("  - VERIFICATION TIER: TIER_2 -- laws.boe.gov.sa checked first but has no dedicated lawId")
    print("    page for this regulation; GOVERNMENT-PRIMARY source is the issuing ministry's own")
    print("    scanned PDF in MEWA's RulesLibrary (read page-by-page), cross-verified against the")
    print("    clean linear HTML on qanoonsa.com/p/506302 (source of the ingested article text)")
    print("  - IN-FORCE: Minister of Environment Decision No. (1515009/1), 3/7/1446H, Umm Al-Qura")
    print("    issue 5063 (5 Jan 2025), under Article 48 of the Environmental Law (Royal Decree M/165)")
    print("  - SUPERSESSION (positive finding): WHOLLY REPLACES the founding Decision No.")
    print("    (582979/1/1442), 14/11/1442H -- verbatim 'تحل هذه اللائحة محل ...' clause; original")
    print("    text superseded and NOT ingested (same self-supersession pattern as the two siblings)")
    print("  - SOURCE artifact 'الش عب' (qanoonsa spacing defect) normalized to 'الشعب' per the")
    print("    official MEWA scan; disclosed, not silently changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
