#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Saudi Arabian
Income Tax Law track (74 records: 30 اصلية, 19 معدلة, 25 ملغاة, 0 مضافة; 30
topical section headings; Ministerial Resolution No. 1535, 11/6/1425H, as
consolidated with amendments through Resolution No. 25, 8/1/1445H).

VERIFICATION TIER -- see the generator's module docstring and
sources/income_tax/regulation/official_source/
income_tax_regulation_official_source.json's verification_methodology_note for
the full account: laws.boe.gov.sa was checked FIRST (per this corpus's standard
methodology) but has NO dedicated lawId page for this Implementing Regulation
(only for the base Income Tax Law). The PRIMARY sources actually used are TWO
cross-verified government-hosted copies -- ZATCA's own official consolidated PDF
(newest, amended through Resolution 25 of 8/1/1445H) and gstc.gov.sa's older
INCOM2.pdf -- the same cross-check the parent income_tax_law track established
works for this family of documents. This validator does not re-adjudicate any of
this; it only checks internal self-consistency of the text this track actually
ingests, and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "income_tax", "regulation", "official_source",
                   "income_tax_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "income_tax", "regulation", "verified",
                       "income_tax_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "income_tax", "regulation", "verified",
                       "income_tax_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "income_tax_regulation_arabic_legal_llm",
                   "income_tax_regulation_legal_llm_001_074.json")
N = 74
KEY_RE = r"income_tax_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 30, "معدلة": 19, "ملغاة": 25, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 30
VERIF_TAG = "ZATCA_PDF_BBOX_RECON_X_GSTC_PDF_CROSS_VERIFIED"

# repealed articles per ZATCA's own (تم حذف المادة) footnotes (Resolution 2568),
# plus the natural-gas IRR regime block -- derived this pass, hardcoded as a
# drift guard against the source's legal_status_ar fields.
EXPECTED_REPEALED = {21, 23, 27, 33, 36, 38, 39, 40, 41, 42, 43, 44, 45, 46,
                     47, 48, 49, 50, 51, 52, 53, 54, 61, 62, 63}
EXPECTED_AMENDED = {1, 2, 5, 7, 8, 9, 10, 16, 26, 28, 30, 31, 34, 35, 37, 57,
                    59, 60, 72}  # article 63 carries both amend + repeal footnotes -> repeal wins (ملغاة)
FLAGGED_DISCREPANCY_KEYS = {
    "income_tax_regulation_date_now_confirmed_1535_11_6_1425",
    "income_tax_regulation_no_dedicated_boe_page",
    "income_tax_regulation_natural_gas_articles_repealed_text_preserved",
    "income_tax_regulation_intraline_word_order_residual_risk",
    "income_tax_regulation_ligature_and_split_word_fixes",
    "income_tax_regulation_irr_table_article_43",
    "income_tax_regulation_compound_resolution_number_reversal",
    "income_tax_regulation_status_derived_from_zatca_footnotes_only",
    "income_tax_regulation_downstream_appendix_559_not_ingested",
    "income_tax_regulation_preamble_from_gstc_only",
    "income_tax_regulation_administering_authority_terminology",
    "income_tax_regulation_gstc_older_consolidation",
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


def _iter_chapter_ranges(chs):
    for ch in chs:
        a = ch["articles"]
        if "-" in a:
            lo, hi = (int(x) for x in a.split("-"))
        else:
            lo = hi = int(a)
        yield (lo, hi)


def main():
    for p in (SRC, RECORDS, SUMMARY, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    e = []
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
    if len(chs) != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d section headings, got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, len(chs)))
    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one section range" % n)
            covered.add(n)
    if covered != set(range(1, N + 1)):
        missing = sorted(set(range(1, N + 1)) - covered)
        extra = sorted(covered - set(range(1, N + 1)))
        if missing:
            e.append("[1c] chapter_structure missing article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])

    sc = Counter()
    repealed_seen, amended_seen = set(), set()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
        if a.get("status") != VERIF_TAG:
            e.append("[2] %s: expected verification status %r, got %r" % (k, VERIF_TAG, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if ls == "ملغاة":
            repealed_seen.add(n)
        if ls == "معدلة":
            amended_seen.add(n)
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        # the source legal text of Article 5 genuinely contains the bracketed
        # English term "Interbank"; that single token is whitelisted, any other
        # latin/html is an extraction leftover.
        latin_stripped = a["text"].replace("Interbank", "")
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", latin_stripped):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        # amended/repealed/added articles must carry amendment_history; original must not
        has_hist = bool(a.get("history"))
        if ls in ("معدلة", "ملغاة", "مضافة") and not has_hist:
            e.append("[2] %s: amended/repealed/added article missing amendment_history" % k)
        if ls == "اصلية" and has_hist:
            e.append("[2i] %s: original article must have empty history[]" % k)
        if bool(a.get("is_mukarrar")):
            e.append("[2] %s: unexpected is_mukarrar=True (none in this track)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        # ligature-extraction regression guards (each corresponds to a disclosed fix):
        # the coordinate reconstruction split لا/لأ/لإ/لآ; a residual isolated
        # ligature token surrounded by spaces would signal an unresolved split.
        for bad in (" لا ك ", " لأ ", " لإ ", " لآ ", "الالئحة", "صالحيات", "الاطالع"):
            if bad in a["text"]:
                e.append("[2g] %s: unresolved ligature-split/reversal artifact %r" % (k, bad))
        # date-format regression guard: no reversed YYYY/MM/DD hijri dates should survive
        if re.search(r"1[34]\d\d\s*/\s*\d{1,2}\s*/\s*\d{1,2}\s*هـ", a["text"]):
            e.append("[2g] %s: reversed (year-first) hijri date survived" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    if repealed_seen != EXPECTED_REPEALED:
        e.append("[2h] repealed-article set drift: unexpected %s / missing %s"
                 % (sorted(repealed_seen - EXPECTED_REPEALED),
                    sorted(EXPECTED_REPEALED - repealed_seen)))
    if amended_seen != EXPECTED_AMENDED:
        e.append("[2h] amended-article set drift: unexpected %s / missing %s"
                 % (sorted(amended_seen - EXPECTED_AMENDED),
                    sorted(EXPECTED_AMENDED - amended_seen)))

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
        e.append("[2k] missing amendment_history")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        for needed in ("1535", "2568", "25", "559"):
            if needed not in decrees:
                e.append("[2k] amendment_history must reference resolution %s" % needed)
        # founding resolution date must be present and be the confirmed value
        founding = next((h for h in src["amendment_history"] if "1535" in str(h.get("decree", ""))), None)
        if not founding or founding.get("date_hijri") != "11/6/1425":
            e.append("[2k] founding Resolution 1535 date must be the confirmed 11/6/1425H")

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "القرار الوزاري رقم (1535)" or src.get("decree_date_hijri") != "11/6/1425":
        e.append("[2j] decree/decree_date_hijri must match the confirmed Resolution 1535, 11/6/1425H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True")
    if "العساف" not in (src.get("preamble_ar") or ""):
        e.append("[2j] preamble_ar must carry the signing Minister of Finance (العساف)")
    art27 = arts.get("income_tax_regulation_art_027", {})
    if art27.get("legal_status_ar") != "ملغاة" or "تخزين الغاز" not in art27.get("text", ""):
        e.append("[2j] Article 27 must be ملغاة (repealed by 2568) with its preserved natural-gas "
                 "storage text intact")
    art74 = arts.get("income_tax_regulation_art_074", {})
    if "(م/1)" not in art74.get("text", "") or art74.get("legal_status_ar") != "اصلية":
        e.append("[2j] Article 74 (effective-date) must cite Royal Decree (م/1) and be اصلية")
    art1 = arts.get("income_tax_regulation_art_001", {})
    if "الهيدروكربونية" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected taxpayer/hydrocarbon definitions")

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
        if r.get("is_repealed") != (a.get("legal_status_ar") == "ملغاة"):
            e.append("[4] %s: is_repealed flag mismatch" % r["article_key"])
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

    if e:
        print("FAIL: %d error(s) in Income Tax Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Saudi Arabian Income Tax Law")
    print("  - 74 records: 30 اصلية, 19 معدلة, 25 ملغاة, 0 مضافة")
    print("  - 30 topical section headings covering articles 1-74 contiguously")
    print("  - VERIFICATION TIER: laws.boe.gov.sa checked first but has NO dedicated lawId page")
    print("    for this Implementing Regulation (only the base Income Tax Law); PRIMARY sources are")
    print("    TWO cross-verified government copies -- ZATCA's official PDF (newest) and gstc.gov.sa's")
    print("    INCOM2.pdf -- the cross-check the parent income_tax_law track established works")
    print("  - Ministerial Resolution No. (1535), 11/6/1425H, CROSS-VERIFIED across both copies'")
    print("    headers -- resolves the exact-date gap the income_tax_law track explicitly flagged")
    print("  - Consolidated through 13 ministerial amendments (latest Resolution 25, 8/1/1445H)")
    print("  - NATURAL GAS: 25 articles of the old IRR natural-gas regime were REPEALED by")
    print("    Resolution 2568 (12/8/1440H, accompanying M/70); ZATCA preserves their full text with")
    print("    a (تم حذف المادة) footnote -- inverse of the parent law track's bare-repeal Chapter 10")
    print("  - Coordinate-based extraction with disclosed lam-alef-ligature-split fixes; residual")
    print("    justified-line word-order risk disclosed in known_unresolved_discrepancies")
    return 0


if __name__ == "__main__":
    sys.exit(main())
