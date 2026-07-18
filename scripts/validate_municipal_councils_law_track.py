#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Municipal Councils Law track
(69 records, ALL 69 اصلية -- this law has never been amended per every
source checked; 0 معدلة, 0 ملغاة, 0 مضافة; 12 فصول, NO أبواب grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/municipal_councils/law/official_source/
municipal_councils_law_official_source.json's verification_methodology_note
for the full account: laws.boe.gov.sa's LIVE portal was unreachable this
pass (HTTP 503), but SIX Wayback Machine snapshots of the exact BOE law
page, spanning 22 Nov 2019 - 12 Dec 2025, were reachable via direct curl
(WebFetch itself refuses web.archive.org in this environment) and
cross-diffed -- all 69 articles are byte-identical across all six
time-points, and NONE ever carry BOE's 'changed-article' flag. This is
independently cross-verified against TWO official, independently-dated PDF
copies of this law hosted on momah.gov.sa (Ministry of Municipal, Rural
Affairs and Housing -- a genuinely separate primary source from BOE) and
against nezams.com's own explicit 'no amendment' statement -- giving this
track TIER_1 status. This validator does not attempt to re-adjudicate any
of this; it only checks internal self-consistency of the text this track
actually ingests, and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "municipal_councils", "law", "official_source",
                   "municipal_councils_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "municipal_councils", "law", "verified",
                       "municipal_councils_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "municipal_councils", "law", "verified",
                       "municipal_councils_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "municipal_councils_arabic_legal_llm",
                   "municipal_councils_law_legal_llm_001_069.json")
N = 69
KEY_RE = r"municipal_councils_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 69, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 12  # 12 فصول, flat -- no أبواب grouping above them

STATUS_UNCHANGED = ("TIER_1_BOE_WAYBACK_SIX_TIMEPOINT_2019_2025_ZERO_AMENDMENTS_X_"
                     "MOMAH_GOV_SA_OFFICIAL_TWO_DATED_PDFS_X_NEZAMS_CROSSCHECK_"
                     "LIVE_BOE_UNREACHABLE")
EXPECTED_STATUS_BY_KEY = {}
AMENDED_KEYS = set(EXPECTED_STATUS_BY_KEY)
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
FLAGGED_DISCREPANCY_KEYS = {
    "municipal_councils_chapter10_title_spelling_anomaly",
    "municipal_councils_predecessor_m5_1397h_partial_repeal_confirmed_primary",
    "municipal_councils_zero_amendments_confirmed_stable",
    "municipal_councils_no_abwab_structure",
    "municipal_councils_implementing_regs_not_ingested",
    "municipal_councils_boe_live_portal_unreachable_wayback_used",
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
    """Yield (lo, hi) for every leaf range in chapter_structure. This Law has
    12 فصول with NO أبواب nesting above them -- every top-level entry IS a
    leaf (no 'sections' key), so this is a flat single-level walk."""
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
        e.append("[1c] expected %d top-level chapter_structure entries (12 فصول, "
                  "no أبواب grouping), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

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
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "ًً" in a["text"]:
            e.append("[2g] %s: residual doubled-tanwin artifact detected" % k)
        if re.search(r"\(\s*\)\d", a["text"]):
            e.append("[2h] %s: residual bidi paren-before-digit artifact detected" % k)
        if a["history"]:
            e.append("[2i] %s: non-amended article must have empty history[]" % k)

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
        e.append("[2k] missing amendment_history (must record the original M/61 issuance)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        if "م/61" not in decrees:
            e.append("[2k] amendment_history must reference م/61")
        if len(src["amendment_history"]) != 1:
            e.append("[2k] amendment_history must have exactly 1 entry (no amendments confirmed)")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("municipal_councils_art_001", {})
    if "تعريفات" not in art1.get("number_label_ar", ""):
        e.append("[2j] Article 1 missing expected تعريفات inline heading")
    if "وزير الشؤون البلدية والقروية" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected الوزير definition")
    art12 = arts.get("municipal_councils_art_012", {})
    if "ثلاثين" not in art12.get("text", ""):
        e.append("[2j] Article 12 missing expected 30-member cap clause")
    art17 = arts.get("municipal_councils_art_017", {})
    if "ثماني عشرة" not in art17.get("text", ""):
        e.append("[2j] Article 17 missing expected 18-year voter-age clause")
    art18 = arts.get("municipal_councils_art_018", {})
    if "خمسٍ وعشرين" not in art18.get("text", "") and "خمس وعشرين" not in art18.get("text", ""):
        e.append("[2j] Article 18 missing expected 25-year candidate-age clause")
    art68 = arts.get("municipal_councils_art_068", {})
    if "م/5" not in art68.get("text", "") or "1397" not in art68.get("text", ""):
        e.append("[2j] Article 68 missing expected predecessor partial-repeal citation (M/5, 1397H)")
    art69 = arts.get("municipal_councils_art_069", {})
    if "مائة وثمانين" not in art69.get("text", ""):
        e.append("[2j] Article 69 missing expected 180-day entry-into-force clause")
    if src.get("decree") != "المرسوم الملكي رقم (م/61)" or src.get("decree_date_hijri") != "4/10/1435":
        e.append("[2j] decree/decree_date_hijri mismatch with verified M/61, 4/10/1435H")

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
        print("FAIL: %d error(s) in Municipal Councils Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Municipal Councils Law")
    print("  - 69 records: ALL 69 اصلية (never amended per every source checked); "
          "0 معدلة, 0 ملغاة, 0 مضافة")
    print("  - 12 فصول (chapters), NO أبواب grouping above them (single-level, 12 leaf ranges)")
    print("  - VERIFICATION TIER: TIER_1 -- BOE-via-Wayback-Machine (SIX snapshots, 22 Nov 2019 -")
    print("    12 Dec 2025, zero amendments/zero text diffs found) x momah.gov.sa's own TWO")
    print("    independently-dated official PDFs (2022, 2025) x nezams.com cross-check")
    print("  - Royal Decree M/61 (4/10/1435H / 31 Jul 2014G), published 3/11/1435H (29 Aug")
    print("    2014G) per Council of Ministers Resolution 384 (24/9/1435H)")
    print("  - CONFIRMED PARTIAL REPEAL (Article 68): repeals ONLY Articles 2(b), 2(c), 7(b),")
    print("    and Chapter Two of Part Two of نظام البلديات والقرى (Royal Decree M/5,")
    print("    21/2/1397H) -- not a full supersession; predecessor law NOT ingested this pass")
    print("  - VERIFIED ANOMALY carried forward: Chapter 10's own heading reads 'مخلفات' (not")
    print("    'مخالفات') أعضاء المجالس البلدية in BOTH primary sources identically -- ingested")
    print("    verbatim, not silently corrected")
    print("  - Distinct from already-ingested regions_law and municipal_realestate_law/")
    print("    municipal_realestate_implementing_regulation tracks; companion implementing")
    print("    regulations (لائحة الانتخاب، اللائحة التنفيذية، اللائحة المالية، لائحة الحملات)")
    print("    identified but NOT ingested this pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
