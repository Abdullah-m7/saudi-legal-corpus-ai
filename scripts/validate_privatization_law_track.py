#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Privatization Law track (45 records:
45 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; FLAT law -- no أبواب/فصول).

VERIFICATION TIER -- see the generator's module docstring and
sources/privatization/law/official_source/privatization_law_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa DOES have a
dedicated lawId page (8af67ec1-6776-4f67-abb4-ad0900eadf2f) but was unreachable
this pass (HTTP 503 / connection reset; Wayback egress-blocked, NOT bypassed).
An OFFICIAL government PDF (misa.gov.sa / National Center for Privatization, HTTP
200) WAS reached and confirmed the 45-article count, the flat structure and
verbatim spot-checks of Articles 44-45; the full governing text is from
nezams.com (independent aggregator, HTTP 200), whose metadata states NO
amendments -> TIER_2 (with a disclosed reservation toward TIER_3). This validator
does not re-adjudicate any of this; it only checks internal self-consistency of
the text this track ingests, and that every discrepancy is still recorded.

MATERIAL DISTINCTION preserved and checked: Article 45 is a GENERIC conflict-only
repeal clause (contrast water_law's NAMED repeal); the NAMED repeals live in the
accompanying CoM Resolution 436, preserved in preamble_ar.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "privatization", "law", "official_source",
                   "privatization_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "privatization", "law", "verified",
                       "privatization_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "privatization", "law", "verified",
                       "privatization_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "privatization_arabic_legal_llm",
                   "privatization_law_legal_llm_001_045.json")
N = 45
KEY_RE = r"privatization_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 45, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # FLAT law: a single structural entry covers 1-45
SECTION = "نظام التخصيص"

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY: dict[str, str] = {}
FLAGGED_DISCREPANCY_KEYS = {
    "privatization_law_boe_dedicated_page_exists_but_unreachable",
    "privatization_law_misa_pdf_official_but_pdftotext_letter_reversal",
    "privatization_law_flat_no_chapter_structure",
    "privatization_law_art45_generic_repeal_but_resolution_436_named_repeal",
    "privatization_law_cabinet_resolution_436_substantive_annex",
    "privatization_law_no_amendments_recorded",
    "privatization_law_two_companion_instruments_out_of_scope",
    "privatization_law_gregorian_date_not_pinpointed",
    "privatization_law_distinct_from_investment_and_gtpl_tracks",
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


def _iter_chapter_ranges(chs):
    for ch in chs:
        lo, hi = (int(x) for x in ch["articles"].split("-"))
        yield (lo, hi)


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
        e.append("[1c] expected %d structural entry (FLAT law), got %d"
                 % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one range" % n)
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
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section_status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        # FLAT law: section_ar must be the uniform value (no invented chapter titles)
        if a.get("section_ar") != SECTION:
            e.append("[2] %s: section_ar must be the uniform flat-law value %r" % (k, SECTION))
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly "
                     "-- see known_unresolved_discrepancies)" % k)
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
        if k not in AMENDED_KEYS and a.get("history"):
            e.append("[2i] %s: non-amended article must have empty history[]" % k)
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present (this law's source supplies no "
                     "inline per-article titles -- section_ar carries the flat-law value)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)

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
        e.append("[2k] missing amendment_history (must record founding decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/63" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/63")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("privatization_law_art_001", {})
    t1 = art1.get("text", "")
    if "المركز الوطني للتخصيص" not in t1 or "الطرف الخاص" not in t1:
        e.append("[2j] Article 1 missing expected definitions (المركز الوطني للتخصيص / الطرف الخاص)")
    art2 = arts.get("privatization_law_art_002", {})
    if "القواعد المنظمة" not in art2.get("text", ""):
        e.append("[2j] Article 2 missing expected reference to القواعد المنظمة")
    art4 = arts.get("privatization_law_art_004", {})
    if "تسري أحكام النظام" not in art4.get("text", ""):
        e.append("[2j] Article 4 missing expected scope clause")
    art44 = arts.get("privatization_law_art_044", {})
    if "اللائحة التنفيذية" not in art44.get("text", ""):
        e.append("[2j] Article 44 missing expected Implementing-Regulation mandate")
    art45 = arts.get("privatization_law_art_045", {})
    t45 = art45.get("text", "")
    if "يلغي النظام كل ما يتعارض معه" not in t45:
        e.append("[2j] Article 45 missing expected generic conflict-repeal clause")
    if "مائة وعشرين" not in t45:
        e.append("[2j] Article 45 missing expected 120-day effective-date clause")
    # the flat-law + generic-repeal distinction: Article 45 must NOT name a predecessor decree
    if re.search(r"م/\d", t45):
        e.append("[2j] Article 45 unexpectedly names a predecessor decree (this law's article-45 "
                 "repeal is GENERIC; named repeals live in CoM Resolution 436 / preamble_ar)")

    if src.get("decree") != "المرسوم الملكي رقم م/63" or src.get("decree_date_hijri") != "5/8/1442":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/63, 5/8/1442H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (this law has NO recorded amendments)")
    pre = src.get("preamble_ar", "")
    if not pre or "436" not in pre or "نظام التخصيص" not in pre:
        e.append("[2j] preamble_ar must be present and reference the founding decree context "
                 "(CoM Resolution 436 and نظام التخصيص)")
    # the NAMED repeals must be preserved in the preamble (not silently dropped)
    if pre and ("60" not in pre or "استراتيجية التخصيص" not in pre):
        e.append("[2j] preamble_ar must preserve CoM Resolution 436's named repeals "
                 "(CoM decision 60, the privatization strategy)")
    # flat-structure claim must be disclosed
    if "غير مقسم" not in (chs[0].get("label_ar", "") if chs else ""):
        e.append("[2j] chapter_structure entry must disclose the flat (no أبواب/فصول) structure")

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
        print("FAIL: %d error(s) in Privatization Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Arabian Privatization Law (نظام التخصيص)")
    print("  - 45 records: 45 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (no amendments recorded)")
    print("  - FLAT law: NO أبواب/فصول divisions (confirmed via MISA/NCP official PDF + nezams.com);")
    print("    a single structural entry covers 1-45; section_ar is the uniform value 'نظام التخصيص'")
    print("    (no thematic chapter titles were invented); no title_ar key (spelled-ordinal labels)")
    print("  - VERIFICATION TIER: TIER_2 -- laws.boe.gov.sa HAS a dedicated lawId page")
    print("    (8af67ec1-6776-4f67-abb4-ad0900eadf2f) but was unreachable this pass (live HTTP 503 /")
    print("    connection reset; Wayback egress-blocked, NOT bypassed). An OFFICIAL government PDF")
    print("    (misa.gov.sa / National Center for Privatization, HTTP 200) confirmed the 45-article")
    print("    count, flat structure, and verbatim Articles 44-45; full governing text from")
    print("    nezams.com (independent aggregator, HTTP 200); identity/preamble also confirmed via")
    print("    WebSearch indexing of BOE's own content and the Umm Al-Qura gazette")
    print("  - Royal Decree M/63 (5/8/1442H, ~26 Mar 2021G), approved via Council of Ministers")
    print("    Resolution 436 (3/8/1442H), published Umm Al-Qura 13/8/1442H; administered by the")
    print("    National Center for Privatization (ncp.gov.sa, under MISA), MoF, and the Council of")
    print("    Economic and Development Affairs")
    print("  - REPEAL: Article 45 is a GENERIC conflict-only clause (material distinction from")
    print("    water_law's NAMED repeal). The NAMED repeals are in the accompanying CoM Resolution")
    print("    436 (CoM decisions 60/1418H, 257/1421H, 219/1423H + Supreme Economic Council 1/23/1423H")
    print("    approving the privatization strategy) -- preserved in preamble_ar")
    print("  - Companion instruments identified but NOT ingested this pass (one-instrument-per-pass):")
    print("    the Implementing Regulation (Article 44, NCP board; SPA-confirmed adoption) and the")
    print("    Organizing Rules (القواعد المنظمة للتخصيص, Article 2) -- track_id: privatization_regulation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
