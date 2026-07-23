#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Anti-Money
Laundering Law track (25 records: 24 اصلية, 1 معدلة, 0 ملغاة, 0 مضافة; nine
chapters carrying the base Law's own chapter numbers I-VI and VIII-X -- chapter
VII العقوبات has no counterpart in the Regulation, a genuine structural feature,
not a gap).

VERIFICATION TIER -- see the generator's module docstring and
sources/aml/regulation/official_source/aml_regulation_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa was checked
FIRST but is unreachable this pass and has no dedicated lawId page for this
Regulation. The PRIMARY source is the aml.gov.sa official SCANNED PDF (Admin
Decision 266507, 9/12/1447H); articles 1,2,5,7,8,9,10,14,15,16 are cross-sourced
from qanoniah.com's born-digital API (confirmed same current version), the rest
OCR-extracted from the scan and visually adjudicated. This validator checks
internal self-consistency only; it does not re-adjudicate provenance.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "aml", "regulation", "official_source",
                   "aml_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "aml", "regulation", "verified",
                       "aml_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "aml", "regulation", "verified",
                       "aml_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "aml_regulation_arabic_legal_llm",
                   "aml_regulation_legal_llm_001_025.json")
N = 25
KEY_RE = r"aml_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 24, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
EXPECTED_CHAPTERS = 9
EXPECTED_NUMBERS = [1, 2, 5, 7, 8, 9, 10, 14, 15, 16, 17, 20, 22, 23, 24,
                    36, 37, 38, 39, 40, 41, 42, 43, 48, 49]

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
AMENDED_KEYS = {"aml_regulation_art_017"}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY = {}
for k in AMENDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_AMENDED
for k in ADDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_ADDED
FLAGGED_DISCREPANCY_KEYS = {
    "aml_regulation_boe_unreachable_no_dedicated_page",
    "aml_regulation_primary_source_is_scanned_pdf",
    "aml_regulation_qanoniah_partial_subset",
    "aml_regulation_no_explicit_article_headers",
    "aml_regulation_skipped_law_articles",
    "aml_regulation_article17_amended_paragraph_not_isolated",
    "aml_regulation_older_1430_predecessor",
    "aml_regulation_supersession",
    "aml_regulation_sama_serves_older_version",
    "aml_regulation_qanoniah_confirmed_current_version",
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

    # article numbers present must match the enumerated set
    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != EXPECTED_NUMBERS:
        e.append("[1b] present article numbers %s != expected %s" % (nums, EXPECTED_NUMBERS))
    if src.get("article_numbers_present") != EXPECTED_NUMBERS:
        e.append("[1b] article_numbers_present field mismatch")

    chs = src.get("chapter_structure") or []
    if len(chs) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d chapters, got %d" % (EXPECTED_CHAPTERS, len(chs)))
    covered = []
    for ch in chs:
        nl = ch.get("article_numbers") or []
        covered.extend(nl)
    if sorted(covered) != EXPECTED_NUMBERS:
        e.append("[1c] chapter_structure article coverage %s != %s"
                 % (sorted(covered), EXPECTED_NUMBERS))
    if len(covered) != len(set(covered)):
        e.append("[1c] an article is covered by more than one chapter")
    # chapter VII (العقوبات) must be absent -> jump from السادس to الثامن
    labels = [c.get("label_ar") for c in chs]
    if "الفصل السابع" in labels:
        e.append("[1d] chapter VII (العقوبات) should be ABSENT in the Regulation")
    if "الفصل السادس" not in labels or "الفصل الثامن" not in labels:
        e.append("[1d] expected chapters السادس (الرقابة) and الثامن (المصادرة) present")

    sc = Counter()
    for k, a in arts.items():
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNCHANGED)
        want_prefix = {"UNCHANGED": ("MATCHES_SOURCE_QANONIAH", "MATCHES_SCAN_OCR_VISUALLY_ADJUDICATED"),
                       "AMENDED": ("MATCHES_SOURCE_QANONIAH", "MATCHES_SCAN_OCR_VISUALLY_ADJUDICATED")}
        if a.get("status") not in want_prefix.get(expected_status, ()):
            e.append("[2] %s: unexpected status %r" % (k, a.get("status")))
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
        if a.get("source_channel") not in ("qanoniah", "scan"):
            e.append("[2] %s: missing/invalid source_channel" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if k not in AMENDED_KEYS and a.get("history"):
            e.append("[2i] %s: non-amended article must have empty history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact" % k)
        # digit normalisation: paragraph tags must be Arabic-Indic (no ASCII digits)
        if re.search(r"[0-9]", a["text"]):
            e.append("[2g] %s: ASCII digit present (should be normalised to Arabic-Indic)" % k)
        # number_label must reference the article number
        n = int(re.match(KEY_RE, k).group(1))
        if a.get("number_label_ar") != "المادة (%d) من اللائحة" % n:
            e.append("[2h] %s: number_label_ar mismatch" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note")
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
        for token in ("14525", "98752", "266507"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference instrument %s" % token)

    # spot-checks anchoring key facts established this pass
    a1 = arts.get("aml_regulation_art_001", {})
    if "المحفظة الإلكترونية" not in a1.get("text", "") or "الموارد الاقتصادية" not in a1.get("text", ""):
        e.append("[2j] Article 1 missing regulation-distinctive definitions "
                 "(المحفظة الإلكترونية / الموارد الاقتصادية)")
    a17 = arts.get("aml_regulation_art_017", {})
    if "الإيقمونت" not in a17.get("text", ""):
        e.append("[2j] Article 17 missing expected Egmont-Group (الإيقمونت) reference")
    a49 = arts.get("aml_regulation_art_049", {})
    if "الضبط الجنائي" not in a49.get("text", ""):
        e.append("[2j] Article 49 missing expected criminal-investigation content")
    if src.get("decree_date_hijri") != "19/2/1439":
        e.append("[2j] decree_date_hijri must be 19/2/1439 (SAMA canonical no. 14525)")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True")
    if "preamble_ar" in src:
        e.append("[2j] preamble_ar should be ABSENT (not fabricated)")

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
        if r.get("source_trust", {}).get("source_status") != a["status"].lower():
            e.append("[5] %s: llm record bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in AML Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Anti-Money Laundering Law")
    print("  - 25 records: 24 اصلية, 1 معدلة (Article 17, per Admin Decision 98752), 0 ملغاة, 0 مضافة")
    print("  - 9 chapters (Law-numbered I-VI, VIII-X; chapter VII العقوبات has no counterpart)")
    print("  - present article numbers: %s" % EXPECTED_NUMBERS)
    print("  - VERIFICATION TIER: TIER_3 -- laws.boe.gov.sa checked first but unreachable this")
    print("    pass and no dedicated lawId page; PRIMARY = aml.gov.sa scanned PDF (Admin Decision")
    print("    266507, 9/12/1447H). Articles 1,2,5,7,8,9,10,14,15,16 from qanoniah born-digital")
    print("    API (confirmed same current version); the other 15 OCR-extracted from the scan and")
    print("    visually adjudicated (a distinct, disclosed lower tier for those articles).")
    print("  - Founding approval cable No. 14525 (19/2/1439H) = SAMA's canonical in-force no.;")
    print("    amended by Admin Decision 98752 (Art. 17); consolidated by 266507 (9/12/1447H).")
    print("  - Predecessor/supersession: the base Law (M/20) replaced M/31 (Law art. 51); a")
    print("    separate older 1430H regulation exists and is NOT mixed in.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
