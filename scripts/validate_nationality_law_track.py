#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Nationality Law track (30
records: 19 اصلية, 11 معدلة [Articles 7, 8, 9, 12, 14, 16, 17, 21, 22, 26,
27], 0 ملغاة, 0 مضافة; flat structure -- NO أبواب/فصول grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/nationality/law/official_source/nationality_law_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa's LIVE
portal was unreachable this pass (connection reset via curl and via
WebFetch), but THREE Wayback Machine snapshots of the exact BOE law page,
spanning 19 Nov 2019 - 14 Jan 2026, were reachable via direct curl and
cross-diffed. All 30 articles are byte-stable across all three time-points
except a confirmed clerical typo fix in Article 30 and Article 8 gaining a
second changelog popup (its 1444H amendment) between the 2022 and 2026
snapshots. Cross-checked against nezams.com (independent reproduction of
decree identity and amendment notations) and, for the most recent
amendment, multiple independent English-language news outlets. This
validator does not attempt to re-adjudicate any of this; it only checks
internal self-consistency of the text this track actually ingests, and that
every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "nationality", "law", "official_source",
                   "nationality_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "nationality", "law", "verified",
                       "nationality_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "nationality", "law", "verified",
                       "nationality_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "nationality_arabic_legal_llm",
                   "nationality_law_legal_llm_001_030.json")
N = 30
KEY_RE = r"nationality_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 19, "معدلة": 11, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat law -- no أبواب/فصول, single leaf range 1-30

STATUS_UNCHANGED = ("BOE_WAYBACK_THREE_TIMEPOINT_NOV2019_DEC2022_JAN2026_TEXT_STABLE_X_"
                    "NEZAMS_COM_CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_AMENDED_CLEAN = ("BOE_CHANGELOG_FULLTEXT_REPLACEMENT_CLEAN_INCORPORATED_X_"
                        "NEZAMS_COM_CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_ART8 = ("BOE_CHANGELOG_TWO_STEP_M14_1405H_FULLTEXT_PLUS_M88_1444H_CLEAN_"
              "SUBSTITUTION_INCORPORATED_X_NEWS_CROSSCHECK_JAN2023_MOTHER_"
              "TRANSMISSION_AMENDMENT_LIVE_BOE_UNREACHABLE")
STATUS_ART30 = ("BOE_WAYBACK_THREE_TIMEPOINT_TEXT_STABLE_EXCEPT_2019_TYPO_VARIANT_"
               "CONFIRMED_CLERICAL_NOT_A_DECREE_AMENDMENT_LIVE_BOE_UNREACHABLE")
AMENDED_NUMS = (7, 8, 9, 12, 14, 16, 17, 21, 22, 26, 27)
AMENDED_KEYS = {"nationality_art_%03d" % n for n in AMENDED_NUMS}
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
EXPECTED_STATUS_BY_KEY = {k: (STATUS_ART8 if k == "nationality_art_008" else STATUS_AMENDED_CLEAN)
                          for k in AMENDED_KEYS}
EXPECTED_STATUS_BY_KEY["nationality_art_030"] = STATUS_ART30
FLAGGED_DISCREPANCY_KEYS = {
    "nationality_gap_map_estimate_confirmed_and_revised",
    "nationality_boe_displays_com_resolution_not_separate_royal_decree_field",
    "nationality_boe_main_body_stale_for_11_articles",
    "nationality_article8_recent_mother_transmission_amendment",
    "nationality_article16_multiple_prior_amendments_not_itemized",
    "nationality_article30_typo_correction",
    "nationality_predecessor_law_repealed_1357h_not_in_corpus",
    "nationality_implementing_regulation_not_ingested",
    "nationality_no_baab_fasl_structure",
    "nationality_no_inline_article_titles",
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

    for n in AMENDED_NUMS:
        key = "nationality_art_%03d" % n
        hist = arts.get(key, {}).get("history", [])
        if len(hist) < 2:
            e.append("[2j] %s must record at least 2 history entries (original + "
                     ">=1 amendment)" % key)

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
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        for token in ("8/20/5604", "م/54", "م/88"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference %s" % token)

    # spot-checks anchoring key facts established this pass
    art7 = arts.get("nationality_art_007", {})
    if "لأبوين مجهولين" not in art7.get("text", ""):
        e.append("[2j] Article 7 missing expected 1379H amendment text (unknown parents/foundling)")
    art8 = arts.get("nationality_art_008", {})
    if "بأمر من رئيس مجلس الوزراء بناءً على اقتراح وزير الداخلية" not in art8.get("text", ""):
        e.append("[2j] Article 8 missing expected M/88 (1444H) amendment wording")
    if "بقرار من وزير الداخلية لمن ولد" in art8.get("text", ""):
        e.append("[2j] Article 8 must NOT retain the pre-M/88 wording it superseded")
    art9 = arts.get("nationality_art_009", {})
    if "عشر سنوات متتالية" not in art9.get("text", ""):
        e.append("[2j] Article 9 missing expected M/54 (1425H) ten-year residence amendment")
    art16 = arts.get("nationality_art_016", {})
    if "يجوز لوزير الداخلية منح" not in art16.get("text", ""):
        e.append("[2j] Article 16 missing expected M/16 (1428H) amendment text")
    art22 = arts.get("nationality_art_022", {})
    if "بأمر من رئيس مجلس الوزراء" not in art22.get("text", ""):
        e.append("[2j] Article 22 missing expected M/4 (1389H) amendment wording")
    art28 = arts.get("nationality_art_028", {})
    if "1357" not in art28.get("text", "") or "يلغي" not in art28.get("text", ""):
        e.append("[2j] Article 28 missing expected explicit repeal of the 1357H predecessor law")
    art30 = arts.get("nationality_art_030", {})
    if "المفعول" not in art30.get("text", ""):
        e.append("[2j] Article 30 missing expected stable 'نافذا المفعول' wording")
    if src.get("decree") != "الإرادة الملكية السنية رقم (8/20/5604)" or src.get("decree_date_hijri") != "22/2/1374":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Will 8/20/5604, 22/2/1374H")
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
        print("FAIL: %d error(s) in Nationality Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Arabian Nationality Law")
    print("  - 30 records: 19 اصلية, 11 معدلة (Articles 7, 8, 9, 12, 14, 16, 17, 21, 22,")
    print("    26, 27), 0 ملغاة, 0 مضافة")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-30); no")
    print("    inline per-article titles in the BOE source (no title_ar key used)")
    print("  - VERIFICATION TIER: TIER_1 -- BOE-via-Wayback-Machine, THREE snapshots")
    print("    spanning 19 Nov 2019 - 14 Jan 2026, x nezams.com independent")
    print("    reproduction of decree identity/amendment notations, x multiple")
    print("    independent news outlets for the most recent (2023G) amendment")
    print("  - Royal Will 8/20/5604 (22/2/1374H / 22 Sep 1954G), approved via Council")
    print("    of Ministers Resolution 4 (25/1/1374H); Article 28 explicitly repeals")
    print("    the 1357H predecessor nationality law (not in this corpus, historical")
    print("    context only, not ingested)")
    print("  - CLEAN CHANGELOG INCORPORATION: 11 of 30 articles' BOE main bodies are")
    print("    stale (pre-amendment), but every changelog popup supplies an")
    print("    unambiguous current-text reconstruction (unlike engineering_practice_law's")
    print("    Article 1 precedent) -- current text ingested, full chain in history[]")
    print("  - Article 8's most recent amendment (M/88, 1444H) transfers approval")
    print("    authority for children of Saudi mothers/foreign fathers from the")
    print("    Minister of Interior to the Prime Minister -- independently confirmed")
    print("    via Arab News/Amwaj Media/Middle East Monitor Jan-Mar 2023G coverage")
    print("  - Companion instrument identified but NOT ingested this pass: اللائحة")
    print("    التنفيذية لنظام الجنسية العربية السعودية (~25 articles, moi.gov.sa)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
