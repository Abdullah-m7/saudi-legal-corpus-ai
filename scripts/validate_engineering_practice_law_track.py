#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Law of the Practice of Engineering Professions
track (17 records: 16 اصلية, 1 معدلة [Article 1], 0 ملغاة, 0 مضافة; flat
structure -- NO أبواب/فصول grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/engineering_practice/law/official_source/
engineering_practice_law_official_source.json's verification_methodology_note
for the full account: laws.boe.gov.sa's LIVE portal was unreachable this pass
(connection reset), but THREE Wayback Machine snapshots of the exact BOE law
page, spanning 14 Nov 2019 - 25 Feb 2026, were reachable via direct curl and
cross-diffed. All 17 articles are byte-stable across all three time-points
except that Article 1 gained BOE's own 'changed-article' flag between the
2019 and 2022 snapshots. Cross-checked against the Saudi Council of
Engineers' own official website (saudieng.sa, its own hosted PDF, Wayback
snapshot 15 Jun 2025) -- Articles 2-17 match word-for-word; Article 1 shows a
THIRD, again-different wording for its ministry-name clause, on top of BOE's
own changelog 'before'-phrase not matching BOE's own main body. This
validator does not attempt to re-adjudicate any of this; it only checks
internal self-consistency of the text this track actually ingests, and that
every discrepancy is still recorded.

DISTINCT FROM saudi_engineers_law: this track uses track_id
"engineering_practice_law" throughout (LAW_ID sa-engineering-practice-
law-m36-1438, decree M/36 dated 19/4/1438H) specifically to avoid colliding
with the already-ingested saudi_engineers_law track (decree M/36 dated
26/9/1423H) -- see known_unresolved_discrepancies key
engineering_practice_decree_number_collision_m36 for the full
re-confirmation that these are two genuinely distinct instruments.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "engineering_practice", "law", "official_source",
                   "engineering_practice_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "engineering_practice", "law", "verified",
                       "engineering_practice_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "engineering_practice", "law", "verified",
                       "engineering_practice_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "engineering_practice_arabic_legal_llm",
                   "engineering_practice_law_legal_llm_001_017.json")
N = 17
KEY_RE = r"engineering_practice_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 16, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat law -- no أبواب/فصول, single leaf range 1-17

STATUS_UNCHANGED = ("BOE_WAYBACK_THREE_TIMEPOINT_NOV2019_NOV2022_FEB2026_TEXT_STABLE_X_"
                    "SAUDIENG_SA_OFFICIAL_PDF_WAYBACK_JUN2025_WORDFORWORD_MATCH_X_"
                    "QANOONSA_QANONIAH_CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_ART1 = ("BOE_CHANGELOG_COM_RESOLUTION_250_1444H_QUOTED_BUT_BEFORE_PHRASE_"
              "MISMATCH_X_MAIN_BODY_STABLE_STALE_INGESTED_X_SAUDIENG_SA_OFFICIAL_"
              "PDF_THIRD_DIVERGENT_WORDING_UNRESOLVED_THREE_WAY_LIVE_BOE_UNREACHABLE")
EXPECTED_STATUS_BY_KEY = {
    "engineering_practice_art_001": STATUS_ART1,
}
AMENDED_KEYS = set(EXPECTED_STATUS_BY_KEY)
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
FLAGGED_DISCREPANCY_KEYS = {
    "engineering_practice_gap_map_estimate_confirmed",
    "engineering_practice_decree_number_collision_m36",
    "engineering_practice_article1_ministry_three_way_discrepancy",
    "engineering_practice_no_predecessor_found",
    "engineering_practice_no_baab_fasl_structure",
    "engineering_practice_no_inline_article_titles",
    "engineering_practice_companion_instruments_not_ingested",
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
    no أبواب/فصول nesting -- the single top-level entry IS the leaf."""
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
        if k not in AMENDED_KEYS and a.get("history"):
            e.append("[2i] %s: non-amended article must have empty history[]" % k)
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present (BOE source supplies no "
                      "inline per-article titles for this law -- see "
                      "known_unresolved_discrepancies)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)

    if len(arts.get("engineering_practice_art_001", {}).get("history", [])) != 1:
        e.append("[2j] Article 1 must record exactly 1 amendment history entry")

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
        e.append("[2k] missing amendment_history (must record M/36 and Resolution 250)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        for token in ("م/36", "250"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference %s" % token)

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("engineering_practice_art_001", {})
    if "الهيئة السعودية للمهندسين" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected الهيئة definition (referencing the "
                  "separate saudi_engineers_law Authority)")
    if "وزارة التجارة والاستثمار" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected BOE-stable (stale) ministry wording")
    if "وزارة الشؤون البلدية والقروية والإسكان" in art1.get("text", ""):
        e.append("[2j] Article 1 must NOT contain the fabricated/mechanically-substituted "
                  "changelog wording -- see known_unresolved_discrepancies")
    if "ميثاق المهندس" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected ميثاق المهندس definition")
    art2 = arts.get("engineering_practice_art_002", {})
    if "الاعتماد المهني" not in art2.get("text", ""):
        e.append("[2j] Article 2 missing expected professional-accreditation clause")
    art6 = arts.get("engineering_practice_art_006", {})
    if "ميثاق المهندس" not in art6.get("text", ""):
        e.append("[2j] Article 6 missing expected Engineer's Charter pledge clause")
    art11 = arts.get("engineering_practice_art_011", {})
    if "1.000.000" not in art11.get("text", "") and "1٫000٫000" not in art11.get("text", ""):
        e.append("[2j] Article 11 missing expected 1,000,000-riyal fine")
    art17 = arts.get("engineering_practice_art_017", {})
    if "ستين يوماً" not in art17.get("text", "") and "ستين يوما" not in art17.get("text", ""):
        e.append("[2j] Article 17 missing expected 60-day entry-into-force clause")
    if src.get("decree") != "المرسوم الملكي رقم (م/36)" or src.get("decree_date_hijri") != "19/4/1438":
        e.append("[2j] decree/decree_date_hijri mismatch with verified M/36, 19/4/1438H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")

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
        print("FAIL: %d error(s) in Engineering Practice Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Law of the Practice of Engineering Professions")
    print("  - 17 records: 16 اصلية, 1 معدلة (Article 1), 0 ملغاة, 0 مضافة")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-17); no")
    print("    inline per-article titles in the BOE source (no title_ar key used)")
    print("  - VERIFICATION TIER: TIER_1 -- BOE-via-Wayback-Machine, THREE snapshots")
    print("    spanning 14 Nov 2019 - 25 Feb 2026, x the Saudi Council of Engineers'")
    print("    own official website (saudieng.sa, its own hosted PDF, Jun 2025), x")
    print("    qanoonsa.com/qanoniah.com structural cross-check")
    print("  - Royal Decree M/36 (19/4/1438H / 17 Jan 2017G), Council of Ministers")
    print("    Resolution 223 (18/4/1438H); no predecessor engineering-practice law")
    print("    found (confirmed negative finding -- no repeal language anywhere)")
    print("  - DECREE-NUMBER COLLISION RE-CONFIRMED: shares bare decree number 'م/36'")
    print("    with saudi_engineers_law (M/36, 26/9/1423H) -- two genuinely distinct")
    print("    instruments; this law's own Article 1 presupposes that Authority's")
    print("    existence rather than repealing/replacing it")
    print("  - GENUINE THREE-WAY ANOMALY carried forward (Article 1): BOE's own")
    print("    changelog quotes CoM Resolution 250 (7/4/1444H) but its own 'before'")
    print("    phrase does not match BOE's own stable main body, and saudieng.sa's")
    print("    own current PDF shows a THIRD, again-different ministry wording --")
    print("    this track ingests BOE's own stable main-body text (NOT a fabricated")
    print("    merge) and flags the full divergence explicitly")
    print("  - Companion instruments identified but NOT ingested this pass: اللائحة")
    print("    التنفيذية لنظام مزاولة المهن الهندسية; ميثاق المهندس; لائحة الوظائف")
    print("    الهندسية")
    return 0


if __name__ == "__main__":
    sys.exit(main())
