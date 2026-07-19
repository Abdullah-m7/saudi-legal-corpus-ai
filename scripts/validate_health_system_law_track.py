#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Health System Law track (19
records: 15 اصلية, 4 معدلة [Articles 4, 5, 16, 17], 0 ملغاة, 0 مضافة; flat
structure -- NO أبواب/فصول grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/health_system/law/official_source/health_system_law_official_source
.json's verification_methodology_note for the full account: laws.boe.gov.sa
was unreachable this pass both live (HTTP 503 / connection reset) and via
Wayback Machine (WebFetch refuses web.archive.org outright; a direct curl to
a confirmed-existing snapshot returned HTTP 403, an organization egress
policy block). istitlaa.ncc.gov.sa (Implementing Regulation host) also
failed via TLS reset. This track instead rests on TWO independently-fetched
secondary sources (nezams.com and qanoonsa.com, fetched directly via curl,
neither a BOE mirror nor a mirror of each other) that agree on the founding
decree identity and on 4 of the 5 Article-16 amendment resolutions. This
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
SRC = os.path.join(ROOT, "sources", "health_system", "law", "official_source",
                   "health_system_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "health_system", "law", "verified",
                       "health_system_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "health_system", "law", "verified",
                       "health_system_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "health_system_arabic_legal_llm",
                   "health_system_law_legal_llm_001_019.json")
N = 19
KEY_RE = r"health_system_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 15, "معدلة": 4, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat law -- no أبواب/فصول, single leaf range 1-19

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
AMENDED_NUMS = (4, 5, 16, 17)
AMENDED_KEYS = {"health_system_art_%03d" % n for n in AMENDED_NUMS}
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
EXPECTED_STATUS_BY_KEY = {k: STATUS_AMENDED_DATED for k in AMENDED_KEYS}
FLAGGED_DISCREPANCY_KEYS = {
    "health_system_gap_map_estimate_confirmed",
    "health_system_boe_and_wayback_both_unreachable",
    "health_system_generic_repeal_clause_confirmed_negative",
    "health_system_article16_resolution_151_not_merged",
    "health_system_resolution_475_unconfirmed",
    "health_system_article16_source_typo",
    "health_system_article16_paragraph_b_stale_cross_reference",
    "health_system_implementing_regulation_not_ingested",
    "health_system_distinct_from_existing_health_tracks",
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
            e.append("[2i] %s: unexpected title_ar key present (this law's sources supply no "
                      "inline per-article titles -- see known_unresolved_discrepancies)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)

    for n in AMENDED_NUMS:
        key = "health_system_art_%03d" % n
        hist = arts.get(key, {}).get("history", [])
        if len(hist) < 2:
            e.append("[2j] %s must record at least 2 history entries (original + "
                     ">=1 amendment)" % key)
        if any(not h.get("decree") for h in hist):
            e.append("[2j] %s has a history step with no decree label" % key)

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
        for token in ("م/11", "418", "م/52", "283", "442", "185", "151"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference %s" % token)

    # spot-checks anchoring key facts established this pass
    art4 = arts.get("health_system_art_004", {})
    if "1 مكرر" not in art4.get("text", "") or "برامج صحة المرأة" not in art4.get("text", ""):
        e.append("[2j] Article 4 missing expected M/52 (1437H) '1 مكرر' amendment text")
    art5 = arts.get("health_system_art_005", {})
    if "12 مكرر" not in art5.get("text", "") or "السياسة الوطنية لصحة المرأة" not in art5.get("text", ""):
        e.append("[2j] Article 5 missing expected M/52 (1437H) '12 مكرر' amendment text")
    art16 = arts.get("health_system_art_016", {})
    if "المجلس الصحي السعودي" not in art16.get("text", ""):
        e.append("[2j] Article 16 missing expected renamed-council text (post-418 amendment)")
    if "هيئة الصحة العامة" not in art16.get("text", ""):
        e.append("[2j] Article 16 missing expected Resolution 185 (1443H) membership text")
    art17 = arts.get("health_system_art_017", {})
    if "اللوائح التنظيمية والإدارية والمالية" not in art17.get("text", ""):
        e.append("[2j] Article 17 missing expected Resolution 418 (1435H) paragraph (ل) text")
    art19 = arts.get("health_system_art_019", {})
    if "يلغي كل ما يتعارض معه" not in art19.get("text", ""):
        e.append("[2j] Article 19 missing expected generic (non-specific) repeal clause")
    if any(name in art19.get("text", "") for name in ("دائرة النفوس", "المواليد والوفيات")):
        e.append("[2j] Article 19 must NOT name a specific predecessor law (confirmed negative "
                 "finding -- only a generic repeal clause exists)")
    if src.get("decree") != "المرسوم الملكي رقم م/11" or src.get("decree_date_hijri") != "23/3/1423":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/11, 23/3/1423H")
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
        print("FAIL: %d error(s) in Health System Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Arabian Health System Law")
    print("  - 19 records: 15 اصلية, 4 معدلة (Articles 4, 5, 16, 17), 0 ملغاة, 0 مضافة")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-19); no inline")
    print("    per-article titles (spelled-ordinal labels, no title_ar key)")
    print("  - VERIFICATION TIER: TIER_3 -- laws.boe.gov.sa unreachable both live (HTTP 503) and")
    print("    via Wayback Machine (WebFetch refuses web.archive.org; direct curl to a confirmed")
    print("    snapshot returned HTTP 403 org egress policy); istitlaa.ncc.gov.sa also unreachable")
    print("    (TLS reset). Two independent secondary sources agree: nezams.com (full article")
    print("    text + inline amendment notes) and qanoonsa.com (raw text of CoM Resolution 151,")
    print("    confirming the founding decree and 4 of 5 Article-16 amendment resolutions)")
    print("  - Royal Decree M/11 (23/3/1423H / 4 Jun 2002G), approved via Council of Ministers")
    print("    Resolution 76 (22/3/1423H)")
    print("  - PREDECESSOR REPEAL: CONFIRMED NEGATIVE -- Article 19 repeals only generically")
    print("    (\"يلغي كل ما يتعارض معه من أحكام\"); no named predecessor law is repealed")
    print("  - ANOMALIES: Article 16's CoM Resolution 151 (1444H) amendment is documented as")
    print("    having occurred but NOT merged into article text (no explicit numbered")
    print("    sub-paragraph given by either source); CoM Resolution 475 (1436H) is cited by")
    print("    Resolution 151 but its substance is undocumented in either source; Article 16's")
    print("    paragraph (ب) contains a stale sub-paragraph cross-reference to pre-185 numbering;")
    print("    a verbatim source typo in Resolution 185's text (\"الهيئة اعامة\") is preserved,")
    print("    not corrected")
    print("  - Companion instrument identified but NOT ingested this pass: اللائحة التنفيذية")
    print("    للنظام الصحي (istitlaa.ncc.gov.sa, unreachable this pass)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
