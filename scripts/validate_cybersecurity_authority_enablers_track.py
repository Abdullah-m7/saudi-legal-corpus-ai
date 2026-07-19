#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the "Regulatory (Legal) Enablers" of the National
Cybersecurity Authority track (7 records, all اصلية at the per-بند level,
0 معدلة, 0 ملغاة, 0 مضافة; flat structure -- NO أبواب/فصول grouping, and NO
مادة numbering at all -- seven ordinal بند divisions instead).

VERIFICATION TIER -- see the generator's module docstring and
sources/cybersecurity_authority/enablers/official_source/
cybersecurity_authority_enablers_official_source.json's
verification_methodology_note for the full account: no laws.boe.gov.sa page
for this exact instrument could be located this pass (a targeted
site:laws.boe.gov.sa WebSearch surfaced only other, unrelated BOE-catalogued
laws; a direct curl to the portal -- both the root domain and a
SearchDetails query -- returned "Connection reset by peer" on both
attempts). The PRIMARY source actually used is an official PDF hosted on
the National Cybersecurity Authority's own website (cdn.nca.gov.sa), whose
embedded text layer has the SAME confirmed, systematic character-
transposition artifact already documented in this corpus's parent
cybersecurity_authority_law track, worked around via Tesseract OCR of
300dpi page renders, cross-checked word-by-word against the flawed-but-
complete pdftotext/fitz extraction and against qanoonsa.com's independent
full structural summary (three separate pages). This track is honestly
assessed at TIER_2, not TIER_1, since no second genuinely independent
official/primary source was located (qanoonsa.com and news outlets are
secondary aggregators; uqn.gov.sa, the official gazette portal, confirms
topical indexing but its full text could not be independently extracted
this pass). This validator does not attempt to re-adjudicate any of this;
it only checks internal self-consistency of the text this track actually
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
SRC = os.path.join(ROOT, "sources", "cybersecurity_authority", "enablers", "official_source",
                   "cybersecurity_authority_enablers_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "cybersecurity_authority", "enablers", "verified",
                       "cybersecurity_authority_enablers_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "cybersecurity_authority", "enablers", "verified",
                       "cybersecurity_authority_enablers_verified_summary.json")
LLM = os.path.join(ROOT, "data", "cybersecurity_authority_enablers_arabic_legal_llm",
                   "cybersecurity_authority_enablers_legal_llm_001_007.json")
N = 7
KEY_RE = r"cybersecurity_authority_enablers_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 7, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat instrument -- no أبواب/فصول, single leaf range 1-7

STATUS_UNCHANGED = ("NCA_OFFICIAL_SITE_PDF_PRIMARY_TESSERACT_OCR_TRANSCRIBED_X_QANOONSA_"
                     "STRUCTURAL_FULL_CROSSCHECK_TIER2_BOE_PAGE_NOT_LOCATED")
EXPECTED_STATUS_BY_KEY = {}  # every بند shares STATUS_UNCHANGED (all اصلية)
AMENDED_KEYS = set()
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
FLAGGED_DISCREPANCY_KEYS = {
    "cybersecurity_authority_enablers_pdf_text_layer_letter_transposition_artifact",
    "cybersecurity_authority_enablers_band_not_madda_structure",
    "cybersecurity_authority_enablers_no_relationship_to_parent_statute_confirmed_negative",
    "cybersecurity_authority_enablers_boe_page_not_located",
    "cybersecurity_authority_enablers_uqn_portal_not_fulltext_extracted",
    "cybersecurity_authority_enablers_no_prior_gap_map_estimate",
    "cybersecurity_authority_enablers_no_baab_fasl_no_madda_structure",
    "cybersecurity_authority_enablers_mixed_numeral_conventions_preserved",
    "cybersecurity_authority_enablers_footer_banner_excluded",
}
EXPECTED_LABELS = {
    1: "البند أولاً", 2: "البند ثانياً", 3: "البند ثالثاً", 4: "البند رابعاً",
    5: "البند خامساً", 6: "البند سادساً", 7: "البند سابعاً",
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
    """Yield (lo, hi) for every leaf range in chapter_structure. This
    instrument has no أبواب/فصول nesting -- every top-level entry IS a leaf
    (no 'sections' key), so this is a flat single-level walk."""
    for ch in chs:
        secs = ch.get("sections")
        if not secs:
            lo, hi = (int(x) for x in ch["articles"].split("-"))
            yield (lo, hi)
            continue
        for sec in secs:
            slo, shi = (int(x) for x in sec["articles"].split("-"))
            yield (slo, shi)


def main():
    e = []
    for p in (SRC, RECORDS, SUMMARY, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    if len(arts) != N:
        e.append("[1] %d بنود != %d" % (len(arts), N))
    if src.get("article_count") != N:
        e.append("[1] article_count field != %d" % N)
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d top-level chapter_structure entries (flat instrument, "
                  "no أبواب/فصول), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] بند %d covered by more than one leaf range" % n)
            covered.add(n)
    if covered != set(range(1, N + 1)):
        missing = sorted(set(range(1, N + 1)) - covered)
        extra = sorted(covered - set(range(1, N + 1)))
        if missing:
            e.append("[1c] chapter_structure missing بند(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range بند(s): %s" % extra[:20])

    sc = Counter()
    for k, a in arts.items():
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNCHANGED)
        if a.get("status") != expected_status:
            e.append("[2] %s: expected status %r, got %r" % (k, expected_status, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended بند missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        m = re.match(KEY_RE, k)
        if m:
            n_num = int(m.group(1))
            if a.get("number_label_ar") != EXPECTED_LABELS.get(n_num):
                e.append("[2i] %s: expected number_label_ar %r, got %r (this instrument uses "
                          "بند labels, not مادة)" % (k, EXPECTED_LABELS.get(n_num),
                                                     a.get("number_label_ar")))
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "ًً" in a["text"]:
            e.append("[2g] %s: residual doubled-tanwin artifact detected" % k)
        if re.search(r"\(\s*\)\d", a["text"]):
            e.append("[2h] %s: residual bidi paren-before-digit artifact detected" % k)
        if re.search(r"^[0-9٠-٩]+[-.\s]", a["text"]):
            e.append("[2h] %s: text begins with a residual list-numeral marker "
                      "(should be omitted per corpus convention)" % k)
        if "التصنيف" in a["text"] or "إشارة المشاركة" in a["text"]:
            e.append("[2h] %s: residual page-footer classification-banner text not excluded" % k)

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
        e.append("[2k] missing amendment_history (must record م/117)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        if "117" not in decrees and "م/117" not in decrees:
            e.append("[2k] amendment_history must reference م/117")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("cybersecurity_authority_enablers_art_001", {})
    if "يعد مخالفة أي مما يأتي" not in art1.get("text", ""):
        e.append("[2j] بند أولاً missing expected opening violations clause")
    if "الترخيص" not in art1.get("text", ""):
        e.append("[2j] بند أولاً missing expected licensing-violation clause")
    art3 = arts.get("cybersecurity_authority_enablers_art_003", {})
    if "تعليق أو إيقاف عمل" not in art3.get("text", ""):
        e.append("[2j] بند ثالثاً missing expected emergency-suspension clause")
    art4 = arts.get("cybersecurity_authority_enablers_art_004", {})
    if "لجنة" not in art4.get("text", "") or "ثلاثة" not in art4.get("text", ""):
        e.append("[2j] بند رابعاً missing expected committee-formation clause "
                 "(minimum 3 members)")
    art5 = arts.get("cybersecurity_authority_enablers_art_005", {})
    if "25.000.000" not in art5.get("text", ""):
        e.append("[2j] بند خامساً missing expected maximum-fine figure (25,000,000 SAR)")
    art7 = arts.get("cybersecurity_authority_enablers_art_007", {})
    if "تلغي كل ما" not in art7.get("text", ""):
        e.append("[2j] بند سابعاً missing expected generic repeal clause")
    if src.get("decree") != "المرسوم الملكي رقم (م/117)" or src.get("decree_date_hijri") != "21/6/1446":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree م/117, 21/6/1446H")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (founding, non-amended instrument)")

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
        print("FAIL: %d error(s) in Cybersecurity Authority Enablers track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Regulatory (Legal) Enablers of the National Cybersecurity Authority")
    print("  - 7 records, ALL اصلية at the per-بند level (0 معدلة, 0 ملغاة, 0 مضافة)")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-7); NO مادة")
    print("    numbering -- seven ordinal بند divisions (أولاً-سابعاً) instead, a genuine")
    print("    structural anomaly relative to every other track in this corpus")
    print("  - VERIFICATION TIER: TIER_2 -- primary source is an official PDF on the")
    print("    National Cybersecurity Authority's own site (cdn.nca.gov.sa), OCR-")
    print("    transcribed to work around the same confirmed text-layer letter-")
    print("    transposition artifact documented in the parent cybersecurity_authority_law")
    print("    track, cross-checked against qanoonsa.com's independent full structural")
    print("    summary (three separate pages) and uqn.gov.sa's topical gazette indexing;")
    print("    no laws.boe.gov.sa page for this exact instrument could be located this pass")
    print("  - Royal Decree م/117 (21/6/1446H / 22 Dec 2024G), based on Council of Ministers")
    print("    Resolution 409 (16/6/1446H) and Shura Council Resolution 16/3 (28/3/1446H),")
    print("    published Umm Al-Qura Gazette No. 5065 (17 Jan 2025G)")
    print("  - CONFIRMED NEGATIVE FINDING (independently re-verified): no source found this")
    print("    pass states this instrument amends or repeals any مادة of the parent")
    print("    organizational تنظيم (Royal Order 6801/7053) -- both remain separate,")
    print("    companion instruments on different subject matter")
    return 0


if __name__ == "__main__":
    sys.exit(main())
