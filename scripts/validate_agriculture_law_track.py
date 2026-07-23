#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Agriculture Law track (نظام الزراعة,
Royal Decree M/64, 10/8/1442H -- the currently in-force Agriculture Law).

37 records: 37 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (the Law has had no amendments).
NO chapter divisions -- the Law is a flat list of 37 consecutive articles (confirmed
independently by nezams.com and by the official MISA English PDF). Accordingly
chapter_structure is intentionally empty and every article's section_ar is empty ("").

SUPERSESSION -- the repeal sits in the ISSUING DECREE (clause Second of Royal Decree
M/64), not inside any article: the Law repeals five named earlier instruments (M/9
1408H, M/13 1424H, M/15 1431H, M/55 1435H, and Council of Ministers Rules No. 96
1405H) plus conflicting provisions. Recorded in supersedes_ar and preamble_ar.

VERIFICATION TIER -- TIER_3. See the generator docstring and the source artifact's
verification_methodology_note: laws.boe.gov.sa was checked FIRST but is unreachable
this pass (HTTP 503) and Wayback is egress-blocked (not circumvented); the verbatim
text of all 37 articles was extracted from nezams.com (a single clean born-digital
HTML aggregator), with every governing metadata fact and the flat structure
cross-verified against multiple independent sources (incl. the official MISA English
PDF). This validator does not re-adjudicate provenance; it only checks internal
self-consistency of the ingested text and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "agriculture", "law", "official_source",
                   "agriculture_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "agriculture", "law", "verified",
                       "agriculture_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "agriculture", "law", "verified",
                       "agriculture_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "agriculture_arabic_legal_llm",
                   "agriculture_law_legal_llm_001_037.json")
N = 37
KEY_RE = r"agriculture_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 37, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
# The Agriculture Law has NO chapter/part divisions (flat 37-article statute).
EXPECTED_TOP_LEVEL_CHAPTERS = 0

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
    "agriculture_law_boe_unreachable_fulltext_from_single_aggregator",
    "agriculture_law_supersedes_five_named_instruments_via_decree_clause",
    "agriculture_law_farsi_yeh_normalized_art23_art35",
    "agriculture_law_mixed_digit_and_label_rendering_preserved",
    "agriculture_law_flat_structure_no_chapters",
    "agriculture_law_implementing_regulation_companion_candidate",
    "agriculture_law_gregorian_dates_secondary_only",
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

    # This Law is flat -- chapter_structure MUST be empty and every section_ar MUST be "".
    chs = src.get("chapter_structure")
    if chs != []:
        e.append("[1c] chapter_structure must be [] for this flat (no-chapter) Law, got %r" % chs)
    if len(chs or []) != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapters, got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, len(chs or [])))

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
        # flat Law: section_ar must be empty for every article
        if a.get("section_ar", "") != "":
            e.append("[2] %s: section_ar must be empty (flat no-chapter Law), got %r"
                     % (k, a.get("section_ar")))
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
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        # residual tashkeel guard (all harakat/shadda/tanwin/superscript-alef must be stripped).
        # NOTE: the range is restricted to the combining-mark block U+064B-U+065F plus superscript
        # alef U+0670; it deliberately EXCLUDES Arabic-Indic digits U+0660-U+0669, which this
        # source legitimately contains (mixed Arabic-Indic/Western digits, preserved verbatim and
        # disclosed in known_unresolved_discrepancies) and which are NOT diacritics.
        if re.search(r"[\u064b-\u065f\u0670]", a["text"]):
            e.append("[2g] %s: residual tashkeel/diacritics not stripped" % k)
        # non-standard Arabic-block letters (Farsi yeh/keheh) must not leak into article text
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
        e.append("[2k] missing amendment_history (must record the founding M/64 decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/64" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/64")

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/64)" \
            or src.get("decree_date_hijri") != "10/8/1442":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/64, 10/8/1442H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (the Law has no amendments)")
    sup = src.get("supersedes_ar", "")
    if not sup or any(x not in sup for x in ("م/9", "م/13", "م/15", "م/55", "96")):
        e.append("[2j] supersedes_ar must name all five repealed instruments (م/9, م/13, م/15, م/55, "
                 "CoM 96) repealed by the issuing decree")
    if not src.get("preamble_ar") or "م/64" not in src.get("preamble_ar", "") \
            or "يلغي" not in src.get("preamble_ar", ""):
        e.append("[2j] preamble_ar (Royal Decree text) must be present, reference م/64, and contain "
                 "the decree-level repeal clause (يلغي)")
    art1 = arts.get("agriculture_law_art_001", {})
    if "الوزارة: وزارة البيئة والمياه والزراعة" not in art1.get("text", "") \
            or "الهيئة: الهيئة العامة للغذاء والدواء" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (الوزارة / الهيئة)")
    art36 = arts.get("agriculture_law_art_036", {})
    if "اللائحة" not in art36.get("text", "") or "تسعين" not in art36.get("text", ""):
        e.append("[2j] Article 36 missing expected implementing-regulation mandate (اللائحة/تسعين)")
    art37 = arts.get("agriculture_law_art_037", {})
    if "يعمل بالنظام" not in art37.get("text", "") or "تسعين" not in art37.get("text", ""):
        e.append("[2j] Article 37 missing expected entry-into-force clause (تسعين يوما)")
    art37_label = art37.get("number_label_ar")
    if art37_label != "المادة السابعة والثلاثون":
        e.append("[2j] Article 37 number_label_ar must be 'المادة السابعة والثلاثون', got %r"
                 % art37_label)

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
        print("FAIL: %d error(s) in Agriculture Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Arabian Agriculture Law (نظام الزراعة)")
    print("  - 37 records: 37 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة (the Law has had no amendments)")
    print("  - NO chapter divisions: flat list of 37 consecutive articles (chapter_structure=[],")
    print("    section_ar empty for all) -- confirmed by nezams.com and the official MISA PDF.")
    print("  - INSTRUMENT CONFIRMED: Royal Decree M/64, 10/8/1442H (CoM Res 431, 3/8/1442H; Shura")
    print("    Res 219/40 17/9/1441H and 362/61 25/2/1442H; Umm Al-Qura 20/8/1442H). Brand-new")
    print("    base-law track, not previously in this corpus.")
    print("  - SUPERSESSION (in the ISSUING DECREE, clause Second -- not in any article): repeals")
    print("    five named earlier instruments (M/9 1408H Living Aquatic Resources; M/13 1424H")
    print("    Animal Resources; M/15 1431H Beekeeping; M/55 1435H Organic Agriculture; CoM Rules")
    print("    96 1405H Agricultural Machinery Trading) plus conflicting provisions.")
    print("  - VERIFICATION TIER: TIER_3 -- laws.boe.gov.sa checked first but unreachable this pass")
    print("    (HTTP 503), Wayback egress-blocked (not circumvented); full verbatim text from")
    print("    nezams.com (single clean born-digital HTML aggregator, no scan/OCR/ligature")
    print("    defects), all governing metadata + flat structure cross-verified against multiple")
    print("    independent sources (BOE lawId via WebSearch, official MISA English PDF confirming")
    print("    M/64 + 37 articles + no chapters, MEWA/Umm Al-Qura/qanoonsa). Re-verify vs")
    print("    laws.boe.gov.sa when reachable.")
    print("  - Implementing Regulation (Article 36 mandate; issued by MEWA) exists and is flagged")
    print("    as a companion candidate (agriculture_regulation), NOT ingested this pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
