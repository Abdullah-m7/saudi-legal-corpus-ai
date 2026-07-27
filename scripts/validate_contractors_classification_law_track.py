#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Contractors Classification Law
track (نظام تصنيف المقاولين, Royal Decree M/9, 18/1/1443H -- the currently
in-force Contractors Classification Law).

19 records: 19 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (no evidence of any amendment
to this Law was found this pass). NO chapter/فصل structure -- a short law,
directly numbered from Article 1 to Article 19 with no sub-division.

SUPERSESSION -- confirmed INSIDE the Law's own Article 19: "يحل النظام محل
نظام تصنيف المقاولين الصادر بالمرسوم الملكي رقم (م / 18) وتاريخ 20 / 3 /
1427هـ، ويلغي كل ما يتعارض معه من أحكام."

VERIFICATION TIER -- TIER_2. See the generator docstring and the source
artifact's verification_methodology_note: the official momah.gov.sa PDF was
fetched directly (a genuine primary source), and its text layer's
font-encoding defect (لم/مل letter-pair reversal after alef) was discovered,
corrected, and cross-verified via an independent Tesseract OCR pass plus a
direct visual read of the same rendered PDF pages. laws.boe.gov.sa (this
corpus's usual second primary source) was checked first per standard
methodology but is unreachable this pass (connection reset / HTTP 503);
web.archive.org was also explicitly attempted and failed identically. This
validator does not re-adjudicate provenance; it only checks internal
self-consistency of the ingested text and that every discrepancy is still
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
SRC = os.path.join(ROOT, "sources", "contractors_classification_law", "law", "official_source",
                   "contractors_classification_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "contractors_classification_law", "law", "verified",
                       "contractors_classification_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "contractors_classification_law", "law", "verified",
                       "contractors_classification_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "contractors_classification_law_arabic_legal_llm",
                   "contractors_classification_law_legal_llm_001_019.json")
N = 19
KEY_RE = r"contractors_classification_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 19, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 0  # no فصول in this law

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
    "contractors_classification_law_boe_and_wayback_unreachable",
    "contractors_classification_law_old_law_repeal_date_conflict",
    "contractors_classification_law_font_encoding_swap_disclosed",
    "contractors_classification_law_preamble_scanned_image_only",
    "contractors_classification_law_com_resolution_49_not_located",
    "contractors_classification_law_transitional_exception_outside_articles",
    "contractors_classification_law_gazette_issue_not_confirmed",
    "contractors_classification_law_no_chapter_structure",
    "contractors_classification_law_implementing_regulation_not_ingested",
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
        e.append("[1c] expected %d chapters (فصول), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

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
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
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
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2f] %s: residual Arabic-Indic digit (source uses Western digits only)" % k)
        if re.search(r"[کیے]", a["text"]):
            e.append("[2g] %s: non-standard Arabic-presentation letter (Farsi yeh/keheh) present" % k)
        # font-swap regression guard: no article should contain the disclosed
        # alef-meem-lam artifact sequence "امل" anywhere (it is always a swap
        # of "الم" in this source -- see known_unresolved_discrepancies)
        if "امل" in a["text"]:
            e.append("[2m] %s: unresolved 'امل' font-swap artifact present (should read 'الم')" % k)

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
        e.append("[2k] missing amendment_history (must record the founding M/9 decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/9" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/9")

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/9)" \
            or src.get("decree_date_hijri") != "18/1/1443":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/9, 18/1/1443H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (no amendments found this pass)")
    sup = src.get("supersedes_ar", "")
    if not sup or "م / 18" not in sup or "المادة التاسعة عشرة" not in sup:
        e.append("[2j] supersedes_ar must name the repealed instrument (م/18) and anchor the "
                 "repeal to Article 19 of this Law's own text")
    if not src.get("preamble_ar") or "18/1/1443" not in src.get("preamble_ar", "") \
            or "نظام تصنيف المقاولين" not in src.get("preamble_ar", ""):
        e.append("[2j] preamble_ar (Royal Decree text) must be present and reference the "
                 "18/1/1443H decree date and نظام تصنيف المقاولين")
    # NOTE: unlike waste_management_law, no standalone CoM Resolution full text
    # was located this pass (see contractors_classification_law_com_resolution_49_not_located);
    # com_resolution_ar is intentionally absent, not required here.
    if src.get("com_resolution_ar") not in (None, ""):
        e.append("[2j] com_resolution_ar was not located this pass and should be null; if a "
                 "future pass adds it, update this check accordingly")

    art1 = arts.get("contractors_classification_law_art_001", {})
    if "الوزارة: وزارة الشؤون البلدية والقروية والإسكان" not in art1.get("text", "") \
            or "التصنيف" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (الوزارة / التصنيف)")
    art17 = arts.get("contractors_classification_law_art_017", {})
    if "اللائحة" not in art17.get("text", "") or "تسعين" not in art17.get("text", ""):
        e.append("[2j] Article 17 missing expected implementing-regulation mandate (اللائحة/تسعين)")
    art18 = arts.get("contractors_classification_law_art_018", {})
    if "الجريدة الرسمية" not in art18.get("text", "") or "تسعين" not in art18.get("text", ""):
        e.append("[2j] Article 18 missing expected entry-into-force clause (تسعين يوما)")
    art19 = arts.get("contractors_classification_law_art_019", {})
    if "يحل النظام محل" not in art19.get("text", "") or "18" not in art19.get("text", ""):
        e.append("[2j] Article 19 missing expected supersession clause referencing م/18")
    art19_label = art19.get("number_label_ar")
    if art19_label != "المادة التاسعة عشرة":
        e.append("[2j] Article 19 number_label_ar must be 'المادة التاسعة عشرة', got %r"
                 % art19_label)

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
        print("FAIL: %d error(s) in Contractors Classification Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Arabian Contractors Classification Law (نظام تصنيف المقاولين)")
    print("  - 19 records: 19 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة (no amendment found this pass)")
    print("  - NO chapter (فصول) structure -- a short, flat, directly-numbered 19-article law")
    print("  - INSTRUMENT CONFIRMED: Royal Decree M/9, 18/1/1443H (CoM Resolution 49, 16/1/1443H;")
    print("    Shura Resolution 5/28, 16/4/1442H). Brand-new base-law track, not previously in")
    print("    this corpus. Fetched DIRECTLY from the official momah.gov.sa PDF.")
    print("  - SUPERSESSION confirmed INSIDE Article 19 of the Law's own text: replaces the prior")
    print("    Contractors Classification Law (M/18, 20/3/1427H; one-day date conflict with")
    print("    nezams.com's 19/3/1427H disclosed, not silently resolved).")
    print("  - FONT-ENCODING DEFECT disclosed and corrected: pages 3-6 of the official PDF")
    print("    reversed every 'الم' sequence to 'امل' (37/37 unique instances resolve cleanly);")
    print("    corrected text cross-verified via independent OCR + direct visual page reading.")
    print("  - VERIFICATION TIER: TIER_2 -- one official primary source (momah.gov.sa) reached and")
    print("    used as governing text, cross-verified via independent OCR/visual-read of the same")
    print("    document plus secondary sources (nezams.com, qanoonsa.com, argaam.com).")
    print("    laws.boe.gov.sa checked first but unreachable this pass (connection reset/HTTP")
    print("    503); web.archive.org also explicitly attempted and unreachable. Re-verify verbatim")
    print("    text vs laws.boe.gov.sa when reachable.")
    print("  - Implementing Regulation (Article 17 mandate) exists and has been amended multiple")
    print("    times per qanoonsa.com, but is NOT ingested this pass -- flagged as a follow-up")
    print("    candidate (contractors_classification_regulation).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
