#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Law of the
Accounting and Auditing Profession track (15 records: 14 اصلية, 1 معدلة
[Article 6], 0 ملغاة, 0 مضافة; flat structure -- NO أبواب/فصول grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/accounting_auditing_regulation/law/official_source/
accounting_auditing_regulation_official_source.json's
verification_methodology_note for the full caveat: SOCPA's own official PDF
(fetched via a single Wayback Machine snapshot, live socpa.org.sa
unreachable) has a systematic text-layer letter-transposition defect; this
track's text was reconstructed via Tesseract Arabic OCR of page-image
renders, cross-checked digit-for-digit against the text layer and against
two independent secondary sources. This validator does not re-adjudicate
any of that; it only checks internal self-consistency of the text this
track actually ingests, and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "accounting_auditing_regulation", "law", "official_source",
                   "accounting_auditing_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "accounting_auditing_regulation", "law", "verified",
                       "accounting_auditing_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "accounting_auditing_regulation", "law", "verified",
                       "accounting_auditing_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "accounting_auditing_regulation_arabic_legal_llm",
                   "accounting_auditing_regulation_legal_llm_001_015.json")
N = 15
KEY_RE = r"accounting_auditing_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 14, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat regulation -- no أبواب/فصول, single leaf range 1-15

STATUS_UNCHANGED = ("SOCPA_PDF_VIA_WAYBACK_TESSERACT_OCR_PRIMARY_X_PDFTOTEXT_DIGIT_CROSSCHECK_X_"
                     "ARGAAM_DARKHABR_SECONDARY_LIVE_SOCPA_UNREACHABLE")
STATUS_ART6 = ("SOCPA_PDF_VIA_WAYBACK_TESSERACT_OCR_PRIMARY_X_PDFTOTEXT_DIGIT_CROSSCHECK_X_"
               "QANOONSA_MOC_RESOLUTION_28_2025_CROSSCHECK_PRE_AMENDMENT_TEXT_NOT_RECOVERED")
EXPECTED_STATUS_BY_KEY = {
    "accounting_auditing_regulation_art_006": STATUS_ART6,
}
AMENDED_KEYS = set(EXPECTED_STATUS_BY_KEY)
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
FLAGGED_DISCREPANCY_KEYS = {
    "accounting_auditing_regulation_pdf_textlayer_ligature_defect",
    "accounting_auditing_regulation_pre_2025_article6_text_not_recovered",
    "accounting_auditing_regulation_uqn_p6059_unreachable",
    "accounting_auditing_regulation_no_inline_article_titles",
    "accounting_auditing_regulation_no_chapter_baab_fasl_structure",
    "accounting_auditing_regulation_article9_table_linearized",
    "accounting_auditing_regulation_socpa_live_unreachable_wayback_used",
    "accounting_auditing_regulation_companion_to_base_law_not_conflated",
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
    Regulation has no أبواب/فصول nesting -- every top-level entry IS a leaf
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
        e.append("[1] %d articles != %d" % (len(arts), N))
    if src.get("article_count") != N:
        e.append("[1] article_count field != %d" % N)
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d top-level chapter_structure entries (flat regulation, "
                  "no أبواب/فصول), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one leaf range" % n)
            covered.add(n)
    if covered != set(range(1, N + 1)):
        missing = sorted(set(range(1, N + 1)) - covered)
        extra = sorted(covered - set(range(1, N + 1)))
        if missing:
            e.append("[1c] chapter_structure missing article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])

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
            e.append("[2] %s: amended article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present (source PDF supplies no inline "
                      "per-article titles for this Regulation -- see "
                      "known_unresolved_discrepancies)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "ًً" in a["text"]:
            e.append("[2g] %s: residual doubled-tanwin artifact detected" % k)
        if re.search(r"\(\s*\)\d", a["text"]):
            e.append("[2h] %s: residual bidi paren-before-digit artifact detected" % k)

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
        e.append("[2k] missing amendment_history (must record MoC 00658 and MoC 28)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        for token in ("00658", "28"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference %s" % token)

    # spot-checks anchoring key facts established this pass
    art6 = arts.get("accounting_auditing_regulation_art_006", {})
    if "الهيئة" not in art6.get("text", "") or "(خمسة عشر) يوم عمل" not in art6.get("text", ""):
        e.append("[2j] Article 6 missing expected 2025-amended (Authority / 15-business-day) "
                  "wording")
    art9 = arts.get("accounting_auditing_regulation_art_009", {})
    for pct in ("30%", "35%", "40%", "45%", "50%"):
        if pct not in art9.get("text", ""):
            e.append("[2j] Article 9 missing expected staffing percentage %s" % pct)
    art5 = arts.get("accounting_auditing_regulation_art_005", {})
    if "6%" not in art5.get("text", ""):
        e.append("[2j] Article 5 missing expected 6%% audit-hours figure")
    if src.get("decree") != "قرار وزير التجارة رقم (00658)" or src.get("decree_date_hijri") != "14/11/1442":
        e.append("[2j] decree/decree_date_hijri mismatch with verified MoC Resolution 00658, "
                  "14/11/1442H")

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
        print("FAIL: %d error(s) in Accounting and Auditing Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Law of the Accounting and Auditing Profession")
    print("  - 15 records: 14 اصلية, 1 معدلة (Article 6), 0 ملغاة, 0 مضافة")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-15); no inline")
    print("    per-article titles in the source PDF (no title_ar key used)")
    print("  - VERIFICATION TIER: SOCPA official PDF via Wayback Machine (primary, live")
    print("    socpa.org.sa unreachable) x Tesseract Arabic OCR (text-layer ligature defect")
    print("    worked around) x argaam.com + darkhabr.com secondary cross-checks")
    print("  - Ministry of Commerce Resolution No. 00658 (14/11/1442H), issued under Article")
    print("    22 of the base Law (Royal Decree M/59, 27/7/1442H, tracked separately as")
    print("    accounting_auditing_law)")
    print("  - AMENDMENT: Ministry of Commerce Resolution No. 28 (3/2/1447H) amended Article")
    print("    6 paragraphs 4-5 (Authority, not Ministry, decides license applications within")
    print("    15 business days); pre-amendment wording not independently recovered this pass")
    print("    (flagged, not silently resolved)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
