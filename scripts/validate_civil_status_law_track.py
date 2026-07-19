#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Civil Status Law track (96
records: 72 اصلية, 24 معدلة [Articles 2, 15, 16, 19, 20, 22, 25, 26, 30, 33,
34, 38, 40, 47, 50, 53, 67, 74, 76, 82, 83, 85, 87, 91], 0 ملغاة, 0 مضافة;
flat structure -- NO أبواب/فصول grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/civil_status/law/official_source/civil_status_law_official_source
.json's verification_methodology_note for the full account: laws.boe.gov.sa's
LIVE portal was unreachable this pass (connection reset via curl), but SEVEN
Wayback Machine snapshots of the exact BOE law page, spanning 13 Nov 2019 -
15 Feb 2026, were reachable via direct curl and cross-diffed. All 96
articles' main body text is byte-stable across all seven time-points; only
the changelog popups for Articles 2, 16, and 67 gained an additional entry
between the Feb 2024 and Jan 2025 snapshots (their M/198, 1445H amendment),
consistent with that amendment's real-world date. Cross-checked against
Council of Ministers Resolution 805 (via qanoonsa.com, an independent legal
aggregator) for that most recent amendment, and against nezams.com for the
founding decree identity and earlier amendments. This validator does not
attempt to re-adjudicate any of this; it only checks internal
self-consistency of the text this track actually ingests, and that every
discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "civil_status", "law", "official_source",
                   "civil_status_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "civil_status", "law", "verified",
                       "civil_status_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "civil_status", "law", "verified",
                       "civil_status_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "civil_status_arabic_legal_llm",
                   "civil_status_law_legal_llm_001_096.json")
N = 96
KEY_RE = r"civil_status_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 72, "معدلة": 24, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat law -- no أبواب/فصول, single leaf range 1-96

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
STATUS_AMENDED_UNDATED = "AMENDED_UNDATED"
AMENDED_NUMS_DATED = (2, 15, 16, 19, 20, 22, 25, 26, 34, 38, 40, 67, 74, 76, 82, 83, 85, 87, 91)
AMENDED_NUMS_UNDATED = (30, 33, 47, 50, 53)
AMENDED_NUMS = AMENDED_NUMS_DATED + AMENDED_NUMS_UNDATED
AMENDED_KEYS = {"civil_status_art_%03d" % n for n in AMENDED_NUMS}
UNDATED_KEYS = {"civil_status_art_%03d" % n for n in AMENDED_NUMS_UNDATED}
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
EXPECTED_STATUS_BY_KEY = {k: (STATUS_AMENDED_UNDATED if k in UNDATED_KEYS else STATUS_AMENDED_DATED)
                          for k in AMENDED_KEYS}
FLAGGED_DISCREPANCY_KEYS = {
    "civil_status_gap_map_estimate_confirmed",
    "civil_status_predecessor_laws_repealed_explicitly",
    "civil_status_five_undated_amendments",
    "civil_status_article2_addition_not_replacement",
    "civil_status_article74_article16_multiple_prior_amendments_not_itemized",
    "civil_status_numeral_script_inconsistency",
    "civil_status_no_baab_fasl_structure",
    "civil_status_no_inline_article_titles",
    "civil_status_implementing_regulation_not_ingested",
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

    for n in AMENDED_NUMS_DATED:
        key = "civil_status_art_%03d" % n
        hist = arts.get(key, {}).get("history", [])
        if len(hist) < 2:
            e.append("[2j] %s must record at least 2 history entries (original + "
                     ">=1 amendment)" % key)
        if any(h.get("decree") is None or "غير مذكور" in h.get("decree", "") for h in hist[1:]):
            e.append("[2j] %s is a dated amendment but a history step is missing its decree" % key)

    for n in AMENDED_NUMS_UNDATED:
        key = "civil_status_art_%03d" % n
        hist = arts.get(key, {}).get("history", [])
        if len(hist) < 2:
            e.append("[2j] %s must record at least 2 history entries (original + "
                     ">=1 amendment)" % key)
        if not any("غير مذكور" in h.get("decree", "") for h in hist[1:]):
            e.append("[2j] %s is expected to be an UNDATED amendment (no decree cited by "
                     "BOE) but no history step flags this" % key)

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
        e.append("[2k] missing amendment_history (must record founding decree + amendments)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        for token in ("م/7", "م/25", "م/198"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference %s" % token)

    # spot-checks anchoring key facts established this pass
    art2 = arts.get("civil_status_art_002", {})
    if "البطاقة الشخصية" not in art2.get("text", "") or "اللجنة المحلية" not in art2.get("text", ""):
        e.append("[2j] Article 2 missing expected M/25 (اللجنة المحلية) or M/198 "
                 "(البطاقة الشخصية) amendment text")
    art16 = arts.get("civil_status_art_016", {})
    if "الخصائص الحيوية" not in art16.get("text", ""):
        e.append("[2j] Article 16 missing expected M/198 (1445H) biometric-registration text")
    art67 = arts.get("civil_status_art_067", {})
    if "السادسة" not in art67.get("text", "") or "وليه أو وصيه" not in art67.get("text", ""):
        e.append("[2j] Article 67 missing expected M/198 (1445H) amendment wording "
                 "(should supersede the M/28, 1434H text)")
    art91 = arts.get("civil_status_art_091", {})
    if "الأب أو الأم" not in art91.get("text", "") or "الزوج بالنسبة للزوجة" in art91.get("text", ""):
        e.append("[2j] Article 91 must reflect the M/134 (1440H) narrowed رب الأسرة definition, "
                 "not the original 1407H text")
    art95 = arts.get("civil_status_art_095", {})
    if ("8172" not in art95.get("text", "") or "1358" not in art95.get("text", "")
            or "يلغي" not in art95.get("text", "")):
        e.append("[2j] Article 95 missing expected explicit repeal of the two named "
                 "predecessor laws (1358H, 1382H)")
    if src.get("decree") != "المرسوم الملكي رقم م/7" or src.get("decree_date_hijri") != "20/4/1407":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/7, 20/4/1407H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (this track incorporates all "
                 "cleanly-reconstructable amendments into current article text)")

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
        print("FAIL: %d error(s) in Civil Status Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Arabian Civil Status Law")
    print("  - 96 records: 72 اصلية, 24 معدلة (Articles 2, 15, 16, 19, 20, 22, 25, 26, 30,")
    print("    33, 34, 38, 40, 47, 50, 53, 67, 74, 76, 82, 83, 85, 87, 91), 0 ملغاة, 0 مضافة")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-96); no inline")
    print("    per-article titles in the BOE source (spelled-ordinal labels, no title_ar key)")
    print("  - VERIFICATION TIER: TIER_1 -- BOE-via-Wayback-Machine, SEVEN snapshots spanning")
    print("    13 Nov 2019 - 15 Feb 2026, x Council of Ministers Resolution 805 (via")
    print("    qanoonsa.com) for the most recent (2024G) amendment, x nezams.com for the")
    print("    founding decree identity and earlier amendments")
    print("  - Royal Decree M/7 (20/4/1407H / 21 Dec 1986G), approved via Council of")
    print("    Ministers Resolution 1 (11/1/1407H); Article 95 explicitly repeals TWO named")
    print("    predecessor laws (نظام دائرة النفوس 1358H, نظام المواليد والوفيات 1382H) --")
    print("    neither in this corpus, historical context only, not ingested")
    print("  - CLEAN CHANGELOG INCORPORATION: every one of 24 amended articles' changelog")
    print("    popups supplies a complete, self-contained replacement text (no ambiguous")
    print("    partial phrase substitution anywhere in this track); Article 2's second")
    print("    amendment (M/198) uniquely ADDS a paragraph rather than replacing the article")
    print("  - ANOMALY: 5 of 24 amended articles (30, 33, 47, 50, 53) have a BOE changelog")
    print("    entry with NO decree number/date cited anywhere in the source (confirmed")
    print("    absent across all seven snapshots) -- flagged as AMENDED_UNDATED, not")
    print("    fabricated; decree field records \"غير مذكور في مصدر هيئة الخبراء\"")
    print("  - Companion instrument identified but NOT ingested this pass: اللائحة")
    print("    التنفيذية لنظام الأحوال المدنية (Ministerial Decision 81, 19/5/1426H)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
