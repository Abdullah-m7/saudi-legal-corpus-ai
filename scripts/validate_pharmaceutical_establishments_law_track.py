#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Pharmaceutical and Herbal
Establishments Law track (نظام المنشآت والمستحضرات الصيدلانية والعشبية, Royal
Decree M/108, 22/8/1441H -- the currently in-force law governing licensing/
operation of pharmacies, herbal-preparation sale establishments, pharmaceutical
/herbal manufacturing plants, trading warehouses, scientific offices, and drug
consultation/analysis centers; administered by the Saudi Food and Drug
Authority / الهيئة العامة للغذاء والدواء).

42 records: 42 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (no amendment has been enacted
per nezams.com's own metadata -- "لم يجرى عليه تعديل" -- and an independent
full-text scan for any embedded amendment reference). No chapter/فصل or باب
structure (confirmed via a direct page-by-page visual review of the official
document).

SUPERSESSION -- confirmed INSIDE the Law's own Article 41: "يحل هذا النظام محل
نظام المنشآت والمستحضرات الصيدلانية، الصادر بالمرسوم الملكي رقم (م/31) والتاريخ
1/ 6/ 1425هـ. ويلغي كل ما يتعارض معه من أحكام." The Royal Decree's own preamble
(clause 3) carves out an explicit transitional exception for the old law's
pharmacy/herbal-sales-establishment provisions.

VERIFICATION TIER -- TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED. See the generator
docstring and the source artifact's verification_methodology_note:
laws.boe.gov.sa was checked first but is unreachable this pass (connection
reset; WebFetch HTTP 503); the governing text instead rests on a direct visual,
page-by-page read of WIPO Lex's officially-hosted Royal Decree PDF (Bureau of
Experts letterhead, official seals, National Archives watermark), cross-checked
word-for-word against nezams.com, which had six minor typos corrected using the
official PDF. This validator does not re-adjudicate provenance; it only checks
internal self-consistency of the ingested text and that every discrepancy is
still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "pharmaceutical_establishments_law", "law", "official_source",
                   "pharmaceutical_establishments_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "pharmaceutical_establishments_law", "law", "verified",
                       "pharmaceutical_establishments_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "pharmaceutical_establishments_law", "law", "verified",
                       "pharmaceutical_establishments_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "pharmaceutical_establishments_law_arabic_legal_llm",
                   "pharmaceutical_establishments_law_legal_llm_001_042.json")
N = 42
KEY_RE = r"pharmaceutical_establishments_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 42, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 0  # no فصول/أبواب in this law

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
    "pharmaceutical_establishments_law_boe_live_unreachable_this_pass",
    "pharmaceutical_establishments_law_nezams_typos_corrected_from_primary",
    "pharmaceutical_establishments_law_proposed_unenacted_amendment_violations_penalties",
    "pharmaceutical_establishments_law_implementing_regulation_not_ingested",
    "pharmaceutical_establishments_law_gazette_publication_date_unconfirmed",
    "pharmaceutical_establishments_law_tashkeel_and_digits_normalized",
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

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapters (فصول/أبواب), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

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
        if a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section_status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if a.get("section_ar") not in ("", None):
            e.append("[2] %s: section_ar must be empty (no chapter structure in this law)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if any(c in a["text"] for c in "«»“”"):
            e.append("[2m] %s: residual decorative quotation mark present (must be stripped)" % k)
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
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2f] %s: residual Arabic-Indic digit (source uses Western digits only)" % k)
        if re.search(r"[کیے]", a["text"]):
            e.append("[2g] %s: non-standard Arabic-presentation letter (Farsi yeh/keheh) present" % k)

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
        e.append("[2k] missing amendment_history (must record the founding M/108 decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/108" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/108")

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/108)" \
            or src.get("decree_date_hijri") != "22/8/1441":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/108, 22/8/1441H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False")
    sup = src.get("supersedes_ar", "")
    if not sup or "م/31" not in sup or "المادة الحادية والأربعون" not in sup:
        e.append("[2j] supersedes_ar must name the repealed instrument (م/31) and anchor the "
                 "repeal to Article 41 of this Law's own text")
    if not src.get("preamble_ar") or "22/8/1441" not in src.get("preamble_ar", "") \
            or "نظام المنشآت والمستحضرات الصيدلانية والعشبية" not in src.get("preamble_ar", ""):
        e.append("[2j] preamble_ar (Royal Decree text) must be present and reference the "
                 "22/8/1441H decree date and نظام المنشآت والمستحضرات الصيدلانية والعشبية")
    if not src.get("com_resolution_ar") or "قرار مجلس الوزراء" not in src.get("com_resolution_ar", ""):
        e.append("[2j] com_resolution_ar (CoM Resolution 534 full text) must be present")
    if "م/31" not in src.get("preamble_ar", ""):
        e.append("[2j] preamble_ar must reference the transitional carve-out naming the "
                 "repealed instrument م/31")

    art1 = arts.get("pharmaceutical_establishments_law_art_001", {})
    if "الهيئة العامة للغذاء والدواء" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected SFDA definition marker")
    art8 = arts.get("pharmaceutical_establishments_law_art_008", {})
    if "10000" not in art8.get("text", "") or "3000" not in art8.get("text", ""):
        e.append("[2j] Article 8 missing expected fee-schedule markers (10000 / 3000)")
    art12 = arts.get("pharmaceutical_establishments_law_art_012", {})
    if "15%" not in art12.get("text", "") or "20%" not in art12.get("text", ""):
        e.append("[2j] Article 12 missing expected profit-margin markers (15% / 20%)")
    art41 = arts.get("pharmaceutical_establishments_law_art_041", {})
    if "يحل هذا النظام محل" not in art41.get("text", "") or "م/31" not in art41.get("text", ""):
        e.append("[2j] Article 41 missing expected supersession clause referencing م/31")
    art42 = arts.get("pharmaceutical_establishments_law_art_042", {})
    if "يعمل بالنظام" not in art42.get("text", ""):
        e.append("[2j] Article 42 missing expected commencement clause")
    art42_label = art42.get("number_label_ar")
    if art42_label != "المادة الثانية والأربعون":
        e.append("[2j] Article 42 number_label_ar must be 'المادة الثانية والأربعون', got %r"
                 % art42_label)

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
        print("FAIL: %d error(s) in Pharmaceutical and Herbal Establishments Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Arabian Pharmaceutical and Herbal Establishments Law")
    print("  (نظام المنشآت والمستحضرات الصيدلانية والعشبية)")
    print("  - 42 records: 42 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة")
    print("  - No chapter/فصل/باب structure (confirmed via a direct page-by-page visual review)")
    print("  - INSTRUMENT CONFIRMED: Royal Decree M/108, 22/8/1441H (CoM Resolution 534,")
    print("    21/8/1441H; Shura Council Resolution 99/24, 18/6/1441H). Brand-new base-law")
    print("    track, not previously in this corpus.")
    print("  - SUPERSESSION confirmed INSIDE Article 41 of the Law's own text: replaces the")
    print("    System of Pharmaceutical Establishments and Preparations (M/31, 1/6/1425H),")
    print("    with a transitional carve-out (decree preamble clause 3) for pharmacies and")
    print("    herbal-preparation-sale establishments.")
    print("  - No amendment enacted to date; a not-yet-confirmed-enacted public-consultation")
    print("    proposal on violations/penalties articles is flagged but NOT applied.")
    print("  - VERIFICATION TIER: TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED -- laws.boe.gov.sa")
    print("    checked first but unreachable this pass (connection reset; WebFetch 503). ONE")
    print("    primary source (WIPO Lex's officially-hosted Royal Decree PDF, Bureau of Experts")
    print("    letterhead, read visually page-by-page in full) was used as governing text,")
    print("    cross-verified word-for-word against nezams.com (six minor typos found and")
    print("    corrected: Articles 9, 15, 31, 32, 33, 34, 39). Re-verify against laws.boe.gov.sa")
    print("    directly (live or via web.archive.org) when feasible to raise to TIER_1.")
    print("  - Implementing Regulation (SFDA PDF dated 2020-12-28) exists and is flagged as a")
    print("    follow-up candidate, NOT ingested this pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
