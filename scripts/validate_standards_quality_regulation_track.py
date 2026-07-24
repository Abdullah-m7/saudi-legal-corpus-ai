#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Saudi Standards
and Quality Law track (اللائحة التنفيذية لنظام المواصفات والجودة; 23 records,
ALL اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; 7 أبواب).

VERIFICATION TIER -- see the generator's module docstring and
sources/standards_quality_regulation/law/official_source/
standards_quality_regulation_official_source.json's verification_methodology_note
for the full account: decision number/date (قرار وزير التجارة رقم (098)، 18/5/
1446هـ) independently confirmed by TWO PRIMARY sources -- SASO's own official
site (the administering authority itself, with a linked PDF labelled "أصل
الوثيقة") and the Umm al-Qura Gazette's own API (fetched directly, not merely
search-engine indexed, quoting the ministerial decision's preamble verbatim).
Full 23-article text cross-verified against qanoonsa.com (SECONDARY);
word-for-word identical except a cosmetic numeral-script difference in
enumerated sub-clauses (see FLAGGED_DISCREPANCY_KEYS). This is TIER_1 -- the
strongest tier in this corpus's own taxonomy. This validator does not
re-adjudicate provenance; it only checks internal self-consistency and that
every discrepancy is still recorded.

MATERIAL FACTS checked: 7 أبواب (chapter_structure), continuous 1-23
numbering, all articles اصلية (no amendments -- this is the FIRST Implementing
Regulation under the base law, so there is no predecessor to supersede), and
that law_component is "regulation" throughout (distinguishing every record
from the separate base-law track, track_id: standards_quality)."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "standards_quality_regulation", "law", "official_source",
                   "standards_quality_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "standards_quality_regulation", "law", "verified",
                       "standards_quality_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "standards_quality_regulation", "law", "verified",
                       "standards_quality_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "standards_quality_regulation_arabic_legal_llm",
                   "standards_quality_regulation_legal_llm_001_023.json")
N = 23
KEY_RE = r"standards_quality_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 23, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_CHAPTERS = 7
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
STATUS_MAIN = ("SASO_OFFICIAL_SITE_PDF_PRIMARY_TEXT_X_UQN_GAZETTE_API_PRIMARY_DECREE_CONFIRMED_"
               "X_QANOONSA_SECONDARY_FULL_TEXT_CROSS_VERIFIED_NUMERAL_STYLE_ONLY_DIFFERENCE_"
               "BOE_LAWID_NOT_FOUND")
FLAGGED_DISCREPANCY_KEYS = {
    "standards_quality_regulation_gap_map_candidate_confirmed",
    "standards_quality_regulation_boe_no_dedicated_page",
    "standards_quality_regulation_numeral_style_cosmetic_only",
    "standards_quality_regulation_saso_html_strips_numbering",
    "standards_quality_regulation_no_predecessor_to_supersede",
    "standards_quality_regulation_saso_page_last_modified_date_unclear",
    "standards_quality_regulation_no_amendments_found_as_of_2026",
    "standards_quality_regulation_istitlaa_draft_not_used",
    "standards_quality_regulation_emdash_normalization",
    "standards_quality_regulation_relationship_to_base_law",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰٕٓٔ]")


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

    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not a clean 1..%d sequence: %s" % (N, nums))

    chapters = src.get("chapter_structure") or []
    if len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d أبواب, got %d" % (EXPECTED_CHAPTERS, len(chapters)))
    for c in chapters:
        if not c.get("label_ar", "").startswith("الباب"):
            e.append("[1c] chapter entry %r: expected a باب label" % c)
        if not c.get("title_ar", "").strip():
            e.append("[1c] chapter entry %r: missing title_ar" % c)

    sc = Counter()
    for k, a in arts.items():
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected structure/section status divergence" % k)
        if a.get("status") != STATUS_MAIN:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS_MAIN, a.get("status")))
        if not a["text"].strip():
            e.append("[2] %s: empty text" % k)
        if re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: unexpected latin/html leftovers" % k)
        if not a.get("section_ar", "").strip():
            e.append("[2] %s: missing section_ar (expected a باب/chapter title)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if "—" in a["text"]:
            e.append("[2f] %s: residual em-dash artifact detected (must be normalized)" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if a.get("history"):
            e.append("[2i] %s: no amendments expected; history must be empty" % k)

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

    ah = src.get("amendment_history")
    if not ah:
        e.append("[2k] missing amendment_history (must record founding decision)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in ah)
        if "098" not in decrees:
            e.append("[2k] amendment_history must reference founding decision 098")

    # spot-checks anchoring key facts
    art1 = arts.get("standards_quality_regulation_art_001", {}).get("text", "")
    if "اللائحة التنفيذية للنظام" not in art1 or "الترخيص" not in art1:
        e.append("[2j] Article 1 missing expected definitions (اللائحة / الترخيص)")
    art4 = arts.get("standards_quality_regulation_art_004", {}).get("text", "")
    if "هيئة الغذاء والدواء" not in art4 or "١- إعداد المواصفة" not in art4:
        e.append("[2j] Article 4 missing expected Food & Drug Authority exception / numbered list")
    art21 = arts.get("standards_quality_regulation_art_021", {}).get("text", "")
    if "المفتشون" not in art21 or "٦- الاحتفاظ" not in art21:
        e.append("[2j] Article 21 missing expected inspectors' powers / item 6")
    art23 = arts.get("standards_quality_regulation_art_023", {}).get("text", "")
    if "تعتمد اللائحة من قبل المجلس" not in art23:
        e.append("[2j] Article 23 missing expected board-adoption/publication clause")

    # NO named repeal of a predecessor regulation anywhere (there is none to repeal)
    for k, a in arts.items():
        if re.search(r"يلغي اللائحة|يلغى اللائحة|إلغاء اللائحة|تحل محل اللائحة", a["text"]):
            e.append("[2j] %s: unexpected predecessor-repeal clause (none should exist)" % k)

    if src.get("decree") != "قرار وزير التجارة رقم (098)" \
            or src.get("decree_date_hijri") != "18/5/1446":
        e.append("[2j] decree/decree_date_hijri mismatch with Decision No. 098, 18/5/1446H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no confirmed amendments)")
    pre = src.get("preamble_ar", "")
    if not pre or "098" not in pre or "5058" not in pre:
        e.append("[2j] preamble_ar must reference decision 098 and gazette issue 5058")

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
        if r.get("legal_status_ar") != a.get("legal_status_ar"):
            e.append("[4] %s: legal_status_ar mismatch" % r["article_key"])
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation'" % r["article_key"])
        if r.get("is_amended"):
            e.append("[4] %s: is_amended must be False (no amendments in this regulation)"
                     % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if summary.get("consolidated_amended_law") is not False:
        e.append("[4b] summary consolidated_amended_law must be False")

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
        if r.get("law_component") != "regulation":
            e.append("[5] %s: llm law_component must be 'regulation'" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != a["status"].lower():
            e.append("[5] %s: llm record source_status mismatch in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Standards and Quality Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Standards and Quality Law")
    print("  (اللائحة التنفيذية لنظام المواصفات والجودة)")
    print("  - 23 records: ALL اصلية (no confirmed amendments), 0 ملغاة, 0 مضافة")
    print("  - 7 أبواب (chapters), continuous numbering 1-23")
    print("  - VERIFICATION TIER: TIER_1 -- two independent PRIMARY sources (SASO's own official")
    print("    site + Umm al-Qura Gazette's own API, both fetched directly) agree on decision")
    print("    098 (18/5/1446H); full text cross-verified against qanoonsa.com (SECONDARY),")
    print("    identical except a cosmetic numeral-script difference in enumerated sub-clauses")
    print("  - Decision of the Minister of Commerce No. (098), 18/5/1446H (20 Nov 2024G); SASO")
    print("    Board Resolution 02/203/2024 (203rd meeting, 15/11/2024G); Umm al-Qura Issue 5058")
    print("    (29/11/2024G)")
    print("  - Issued under Article 23 of the base law (Royal Decree M/36, track_id:")
    print("    standards_quality, law_component 'law'); this track's law_component is 'regulation'")
    print("  - NO predecessor regulation superseded (first Implementing Regulation under this law)")
    print("  - laws.boe.gov.sa has NO dedicated lawId page for this Implementing Regulation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
