#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the GCC Unified Anti-Dumping, Countervailing and
Safeguard Measures Law track (17 records, all اصلية per BOE's currently-
served text; flat structure -- NO أبواب/فصول grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/gcc_anti_dumping/law/official_source/
gcc_anti_dumping_law_official_source.json's verification_methodology_note
for the full caveat: laws.boe.gov.sa's LIVE portal was unreachable this
pass, but two Wayback Machine snapshots (20231112034551 and 20250619192625)
of the exact Arabic law page WERE reachable and are treated as the primary
source, partially cross-verified against qistas.com (Articles 1-3 only).

THIS TRACK CARRIES A MAJOR, EXPLICITLY-FLAGGED, UNRESOLVED DISCREPANCY: WIPO
Lex and a separate, currently-in-force 2022 Saudi law's own BOE-hosted
preamble both indicate Royal Decree M/7 (20/3/1434H) approved a differently
structured, 15-article AMENDED ('معدل') version of this Law (per the GCC
Secretariat General's own official PDF, fetched live this pass) -- but this
pass could not independently verify M/7's exact Saudi-Gazette-published
wording, so this track deliberately ingests BOE's directly-verified
17-article ORIGINAL (M/30) text instead of silently substituting the
unverified amended text. This validator does not attempt to adjudicate that
discrepancy; it only checks internal self-consistency of the text this
track actually ingests, and that the discrepancy itself is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "gcc_anti_dumping", "law", "official_source",
                   "gcc_anti_dumping_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "gcc_anti_dumping", "law", "verified",
                       "gcc_anti_dumping_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "gcc_anti_dumping", "law", "verified",
                       "gcc_anti_dumping_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "gcc_anti_dumping_arabic_legal_llm",
                   "gcc_anti_dumping_law_legal_llm_001_017.json")
N = 17
KEY_RE = r"gcc_anti_dumping_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 17, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
STATUS = ("BOE_WAYBACK_ARCHIVE_PRIMARY_X_QISTAS_PARTIAL_STRUCTURAL_CROSSCHECK_"
          "LIVE_BOE_UNREACHABLE_M7_1434H_AMENDED_TEXT_NOT_INCORPORATED")
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat law -- no أبواب/فصول, single leaf range 1-17
AMENDED_KEYS = set()   # BOE's own text carries no per-article amendment marker
ADDED_KEYS = set()     # no مضافة articles in the BOE-served text
REPEALED_KEYS = set()  # no ملغاة articles in the BOE-served text
MUKARRAR_KEYS = set()  # no مكرر articles
FLAGGED_DISCREPANCY_KEYS = {
    "gcc_anti_dumping_m7_1434h_amended_text_not_incorporated",
    "gcc_anti_dumping_boe_live_portal_unreachable_wayback_used",
    "gcc_anti_dumping_article_016_no_boe_heading_title",
    "gcc_anti_dumping_no_chapter_baab_fasl_structure",
    "gcc_anti_dumping_gap_map_article_count_corrected",
    "gcc_anti_dumping_implementing_regulation_not_ingested_this_pass",
    "gcc_anti_dumping_qistas_partial_cross_check_only",
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
    no أبواب/فصول nesting -- every top-level entry IS a leaf (no 'sections'
    key), so this is a flat single-level walk."""
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
        e.append("[1c] expected %d top-level chapter_structure entries (flat law, "
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
        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
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
        if " " in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "ًً" in a["text"]:
            e.append("[2g] %s: residual doubled-tanwin artifact detected" % k)
        if re.search(r"\(\s*\)\d", a["text"]):
            e.append("[2h] %s: residual bidi paren-before-digit artifact detected" % k)

    # Article 16 is a documented, source-verified exception: BOE's own h3
    # heading carries no title text for it (see known_unresolved_discrepancies).
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
        title = a.get("title_ar")
        if n == 16:
            if title not in (None, ""):
                e.append("[2i] %s: expected empty title_ar (documented BOE heading "
                          "gap), got %r" % (k, title))
        else:
            if not title:
                e.append("[2i] %s: missing title_ar (only Article 16 is an allowed "
                          "exception)" % k)

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
        e.append("[2k] missing amendment_history (must record both M/30 and the "
                  "unresolved M/7 candidate amendment)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        if "م/30" not in decrees or "م/7" not in decrees:
            e.append("[2k] amendment_history must reference both المرسوم الملكي رقم "
                      "(م/30) and المرسوم الملكي رقم (م/7)")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("gcc_anti_dumping_art_001", {})
    if "الإغراق" not in art1.get("text", "") or "دول المجلس" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected core terms (الإغراق/دول المجلس)")
    art17 = arts.get("gcc_anti_dumping_art_017", {})
    if "الأول من يناير عام 2004" not in art17.get("text", ""):
        e.append("[2j] Article 17 missing expected 1 January 2004 entry-into-force date")
    art15 = arts.get("gcc_anti_dumping_art_015", {})
    if "اللائحة التنفيذية" not in art15.get("text", ""):
        e.append("[2j] Article 15 missing expected Implementing Regulation reference")
    if src.get("decree") != "المرسوم الملكي رقم (م/30)" or src.get("decree_date_hijri") != "17/5/1427":
        e.append("[2j] decree/decree_date_hijri mismatch with verified M/30, 17/5/1427H")

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
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in GCC Anti-Dumping Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: GCC Unified Anti-Dumping, Countervailing and Safeguard Measures Law")
    print("  - 17 records (all اصلية per BOE's currently-served text); flat structure,")
    print("    NO أبواب/فصول grouping (single leaf range 1-17), each article carries its")
    print("    own inline title except Article 16 (a documented, verified BOE heading gap)")
    print("  - VERIFICATION TIER: BOE-via-Wayback-Machine archive (primary, live BOE")
    print("    unreachable, 2 independent snapshots 20 months apart agree) x qistas.com")
    print("    (partial structural cross-check, Articles 1-3 only)")
    print("  - Royal Decree M/30 (17/5/1427H), Council of Ministers Resolution 122")
    print("    (16/5/1427H); GCC Supreme Council 24th Session (Kuwait, Dec 2003)")
    print("  - MAJOR UNRESOLVED DISCREPANCY carried forward: WIPO Lex + a separate")
    print("    in-force 2022 Saudi law's own preamble indicate Royal Decree M/7")
    print("    (20/3/1434H) approved a differently-structured 15-article amended")
    print("    ('معدل') text (per the GCC Secretariat General's own PDF) that BOE's")
    print("    own primary catalog page for this law does not reflect -- this track")
    print("    ingests BOE's verified 17-article original text and flags, but does")
    print("    not silently resolve, this conflict (see known_unresolved_discrepancies)")
    print("  - Implementing Regulation identified but NOT ingested this pass -- a")
    print("    candidate for follow-up")
    return 0


if __name__ == "__main__":
    sys.exit(main())
