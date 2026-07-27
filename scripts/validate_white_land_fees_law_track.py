#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian White Land and Vacant Properties
Fees Law track (نظام رسوم الأراضي البيضاء والعقارات الشاغرة, originally Royal
Decree M/4, 12/2/1437H, substantively amended/renamed by Royal Decree M/244,
7/11/1446H).

15 records: 2 اصلية (Articles 10, 15), 13 معدلة (Articles 1-9, 11-14 -- all
amended by M/244). No chapter/باب/فصل subdivision (flat structure of 15
sequential articles), confirmed independently from both momah.gov.sa and
qadha.org.sa.

SELF-AMENDMENT, NOT SUPERSESSION OF A DISTINCT LAW -- M/244 amended and
renamed the SAME law issued by M/4; it did not repeal/replace a separate
predecessor instrument. Distinct from this corpus's existing rett_law (Real
Estate Transaction Tax) track, which this track does not touch.

VERIFICATION TIER -- TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED. See the
generator docstring and the source artifact's verification_methodology_note:
laws.boe.gov.sa was checked first but unreachable this pass (connection
reset; web.archive.org returned HTTP 403). Governing text for 14/15 articles
is momah.gov.sa (the administering Ministry of Municipalities and Housing's
own official redline/comparison PDF), cross-verified against qadha.org.sa.
Article 3 is a documented exception (sourced from qadha.org.sa because
momah.gov.sa's own PDF omits the M/244 amendment marker for that article --
see known_unresolved_discrepancies). This validator does not re-adjudicate
provenance; it only checks internal self-consistency of the ingested text and
that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "white_land_fees_law", "law", "official_source",
                   "white_land_fees_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "white_land_fees_law", "law", "verified",
                       "white_land_fees_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "white_land_fees_law", "law", "verified",
                       "white_land_fees_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "white_land_fees_law_arabic_legal_llm",
                   "white_land_fees_law_legal_llm_001_015.json")
N = 15
KEY_RE = r"white_land_fees_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 2, "معدلة": 13, "ملغاة": 0, "مضافة": 0}
AMENDED_KEYS = {"white_land_fees_law_art_%03d" % n
                for n in (1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14)}
UNCHANGED_KEYS = {"white_land_fees_law_art_010", "white_land_fees_law_art_015"}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"

FLAGGED_DISCREPANCY_KEYS = {
    "white_land_fees_law_boe_unreachable",
    "white_land_fees_law_article3_momah_pdf_gap",
    "white_land_fees_law_com_181_regulation_only",
    "white_land_fees_law_staggered_entry_into_force",
    "white_land_fees_law_implementing_regulations_not_ingested",
    "white_land_fees_law_pdf_text_rendering_artifact",
    "white_land_fees_law_gregorian_dates_secondary",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ٰٟ]")


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

    if "chapter_structure" in src and src.get("chapter_structure"):
        e.append("[1c] this law has no chapters (فصول/أبواب); chapter_structure must be "
                 "absent or empty")

    sc = Counter()
    for k, a in arts.items():
        expected_status = STATUS_AMENDED if k in AMENDED_KEYS else STATUS_UNCHANGED
        if a.get("status") != expected_status:
            e.append("[2] %s: expected status %r, got %r" % (k, expected_status, a.get("status")))
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
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if k in (AMENDED_KEYS | ADDED_KEYS) and not a.get("history"):
            e.append("[2] %s: amended/added article missing amendment_history" % k)
        if k not in (AMENDED_KEYS | ADDED_KEYS) and a.get("history"):
            e.append("[2i] %s: non-amended/added article must have empty history[]" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2f] %s: residual Arabic-Indic digit (source uses Western digits only)" % k)
        if "٪" in a["text"]:
            e.append("[2f] %s: residual Arabic percent sign (must be normalized to '%%')" % k)
        if "الأراض ي" in a["text"] or "الأرايض" in a["text"]:
            e.append("[2f] %s: residual PDF-extraction glitch for 'الأراضي' not normalized" % k)
        if re.search(r"[کیے]", a["text"]):
            e.append("[2g] %s: non-standard Arabic-presentation letter (Farsi yeh/keheh) present" % k)
        for h in a.get("history", []):
            pt = h.get("previous_text_ar", "")
            if pt and ("الأراض ي" in pt or "الأرايض" in pt):
                e.append("[2f] %s: history previous_text_ar has unnormalized 'الأراضي' glitch" % k)
            if pt and HARAKAT.search(pt):
                e.append("[2h] %s: history previous_text_ar has residual harakat" % k)

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
        e.append("[2k] missing amendment_history (must record both M/4 and M/244)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/4" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/4")
        if "م/244" not in decrees:
            e.append("[2k] amendment_history must reference amending decree م/244")

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/4)" \
            or src.get("decree_date_hijri") != "12/2/1437":
        e.append("[2j] decree/decree_date_hijri mismatch with verified founding Royal Decree "
                 "M/4, 12/2/1437H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (this is the consolidated "
                 "post-M/244 text)")
    preamble = src.get("preamble_ar", "")
    if not preamble or "م/4" not in preamble or "1437/2/12" not in preamble:
        e.append("[2j] preamble_ar (founding Royal Decree M/4 text) must be present and "
                 "reference the decree number (م/4) and date (1437/2/12H)")
    if not src.get("amendment_decree_m244_ar") \
            or "1446/11/7" not in src.get("amendment_decree_m244_ar", ""):
        e.append("[2j] amendment_decree_m244_ar (Royal Decree M/244 text) must be present "
                 "and reference the 7/11/1446H decree date")

    art1 = arts.get("white_land_fees_law_art_001", {})
    if "وزير البلديات والإسكان" not in art1.get("text", "") \
            or "العقارات الشاغرة" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected current definitions (وزير البلديات "
                 "والإسكان / العقارات الشاغرة)")
    art3 = arts.get("white_land_fees_law_art_003", {})
    if "10%" not in art3.get("text", "") or "خمسة آلاف متر مربع" not in art3.get("text", "") \
            or "العقارات الشاغرة" not in art3.get("text", ""):
        e.append("[2j] Article 3 missing expected post-M/244 provisions (10%% cap / 5000 sqm "
                 "minimum / vacant properties fee)")
    art13 = arts.get("white_land_fees_law_art_013", {})
    if "اللجنة الوزارية" not in art13.get("text", ""):
        e.append("[2j] Article 13 missing expected post-M/244 issuance mechanism reference "
                 "(اللجنة الوزارية)")
    art15 = arts.get("white_land_fees_law_art_015", {})
    if "يعمل بهذا النظام" not in art15.get("text", "") or "مائة وثمانين" not in art15.get("text", ""):
        e.append("[2j] Article 15 missing expected entry-into-force clause (180 days)")
    art15_label = art15.get("number_label_ar")
    if art15_label != "المادة الخامسة عشرة":
        e.append("[2j] Article 15 number_label_ar must be 'المادة الخامسة عشرة', got %r"
                 % art15_label)

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
        expected_status = STATUS_AMENDED if r["article_key"] in AMENDED_KEYS else STATUS_UNCHANGED
        if r.get("source_trust", {}).get("source_status") != expected_status.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])
        if r.get("law_component") != "law":
            e.append("[5] %s: law_component must be 'law'" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in White Land and Vacant Properties Fees Law track:" % len(e))
        for x in e[:60]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Arabian White Land and Vacant Properties Fees Law")
    print("      (نظام رسوم الأراضي البيضاء والعقارات الشاغرة)")
    print("  - 15 records: 2 اصلية (10, 15), 13 معدلة (1-9, 11-14) -- no مضافة, no ملغاة")
    print("  - No chapter/فصل/باب subdivision (flat 15-article structure), confirmed against")
    print("    both momah.gov.sa and qadha.org.sa")
    print("  - INSTRUMENT CONFIRMED: originally Royal Decree M/4, 12/2/1437H; substantively")
    print("    amended/renamed by Royal Decree M/244, 7/11/1446H. Brand-new base-law track,")
    print("    not previously in this corpus; distinct from the existing rett_law track.")
    print("  - VERIFICATION TIER: TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED -- laws.boe.gov.sa")
    print("    checked first but unreachable this pass (connection reset; web.archive.org")
    print("    HTTP 403). Governing text for 14/15 articles from momah.gov.sa (administering")
    print("    Ministry's own redline PDF), cross-verified against qadha.org.sa. Article 3 is")
    print("    a documented exception sourced from qadha.org.sa due to a gap in momah's own")
    print("    PDF -- see known_unresolved_discrepancies before relying on that article.")
    print("  - Two Implementing Regulations exist (white land fees; vacant property fees),")
    print("    NOT ingested this pass -- flagged as follow-up candidates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
