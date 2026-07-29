#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Organizational Statute of the General
Authority of Civil Aviation (GACA) track (15 records, all اصلية; flat
structure -- NO أبواب/فصول grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/gaca_organizational_statute/law/official_source/
gaca_organizational_statute_official_source.json's verification_methodology_
note for the full account: laws.boe.gov.sa (both the task-supplied old BOE
Law Id and a second, distinct new-statute BOE Law Id) and web.archive.org
(the Wayback Machine fallback) were BOTH confirmed unreachable this pass.
This track instead rests on uqn.gov.sa (the official Umm Al-Qura Gazette
website)'s own server-rendered article HTML as its primary source,
word-for-word cross-checked against qanoonsa.com, and tertiarily
corroborated by argaam.com's press coverage. Council of Ministers Resolution
No. 807 (14/11/1446H) is a WHOLESALE re-issue superseding Resolution 33
(11/2/1426H) in full -- all 15 articles are modeled as original (اصلية),
not as an amendment layer. This validator does not attempt to re-adjudicate
any of this; it only checks internal self-consistency of the text this
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
SRC = os.path.join(ROOT, "sources", "gaca_organizational_statute", "law", "official_source",
                   "gaca_organizational_statute_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "gaca_organizational_statute", "law", "verified",
                       "gaca_organizational_statute_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "gaca_organizational_statute", "law", "verified",
                       "gaca_organizational_statute_verified_summary.json")
LLM = os.path.join(ROOT, "data", "gaca_organizational_statute_arabic_legal_llm",
                   "gaca_organizational_statute_legal_llm_001_015.json")
N = 15
BASE_ARTICLE_COUNT = 15
KEY_RE = r"gaca_organizational_statute_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 15, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat law -- no أبواب/فصول, single leaf range 1-15

STATUS_UNCHANGED = ("UQN_GOV_SA_OFFICIAL_GAZETTE_SSR_HTML_X_QANOONSA_COM_WORD_FOR_WORD_MATCH_"
                     "LIVE_BOE_AND_WAYBACK_BOTH_UNREACHABLE_THIS_PASS")
STATUS_ART_TERTIARY = ("UQN_GOV_SA_OFFICIAL_GAZETTE_SSR_HTML_X_QANOONSA_COM_WORD_FOR_WORD_"
                       "MATCH_X_ARGAAM_COM_VERBATIM_QUOTE_LIVE_BOE_AND_WAYBACK_BOTH_"
                       "UNREACHABLE_THIS_PASS")
EXPECTED_STATUS_BY_KEY = {
    "gaca_organizational_statute_art_002": STATUS_ART_TERTIARY,
    "gaca_organizational_statute_art_003": STATUS_ART_TERTIARY,
}
AMENDED_KEYS = set()
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
FLAGGED_DISCREPANCY_KEYS = {
    "gaca_boe_and_wayback_both_unreachable_this_pass",
    "gaca_primary_source_is_umm_al_qura_gazette_website_not_boe",
    "gaca_qanoonsa_word_for_word_cross_check_and_decree_recital",
    "gaca_argaam_tertiary_corroboration_transitional_clauses_not_ingested",
    "gaca_wholesale_reissue_not_amendment_layer_resolution_33_text_not_sourced",
    "gaca_no_chapter_subdivision_no_inline_titles",
    "gaca_rtl_mark_and_digit_glyph_normalization_only",
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
    key), so this is a flat single-level walk over the 15 articles."""
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
    if covered != set(range(1, BASE_ARTICLE_COUNT + 1)):
        missing = sorted(set(range(1, BASE_ARTICLE_COUNT + 1)) - covered)
        extra = sorted(covered - set(range(1, BASE_ARTICLE_COUNT + 1)))
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
        if k in (AMENDED_KEYS | ADDED_KEYS) and not a.get("history"):
            e.append("[2] %s: amended/added article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present (source supplies no "
                      "inline per-article titles for this law -- see "
                      "known_unresolved_discrepancies)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "ًً" in a["text"]:
            e.append("[2g] %s: residual doubled-tanwin artifact detected" % k)
        if re.search(r"\(\s*\)\d", a["text"]):
            e.append("[2h] %s: residual bidi paren-before-digit artifact detected" % k)
        if "‏" in a["text"] or "‎" in a["text"]:
            e.append("[2h] %s: residual RTL/LTR mark artifact detected" % k)

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
        e.append("[2k] missing amendment_history (must record 33 and 807)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        for token in ("33", "807"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference %s" % token)

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("gaca_organizational_statute_art_001", {})
    if "وزير النقل والخدمات اللوجستية" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected Minister definition")
    art3 = arts.get("gaca_organizational_statute_art_003", {})
    if "الاستراتيجية الوطنية للنقل والخدمات اللوجستية" not in art3.get("text", ""):
        e.append("[2j] Article 3 missing expected national-transport-strategy alignment clause")
    art4 = arts.get("gaca_organizational_statute_art_004", {})
    if "20- التحقيق فنياً في حوادث ووقائع الطيران المدني" not in art4.get("text", ""):
        e.append("[2j] Article 4 missing expected 20th (final) competency")
    art5 = arts.get("gaca_organizational_statute_art_005", {})
    if "ما لا يتجاوز (خمسة) ممثلين من الجهات الحكومية" not in art5.get("text", ""):
        e.append("[2j] Article 5 missing expected board-composition clause")
    if "ما لا يتجاوز (ثلاثة) أشخاص من القطاع الخاص" not in art5.get("text", ""):
        e.append("[2j] Article 5 missing expected private-sector-seats clause")
    art8 = arts.get("gaca_organizational_statute_art_008", {})
    if "15- أي مهمة أخرى يكلّفه بها المجلس" not in art8.get("text", ""):
        e.append("[2j] Article 8 missing expected final (15th) president power")
    art11 = arts.get("gaca_organizational_statute_art_011", {})
    if "عدا الرئيس" not in art11.get("text", ""):
        e.append("[2j] Article 11 missing expected president-exception clause")
    art15 = arts.get("gaca_organizational_statute_art_015", {})
    if "يُنشر التنظيم في الجريدة الرسمية" not in art15.get("text", ""):
        e.append("[2j] Article 15 missing expected publication clause")
    if src.get("decree") != "قرار مجلس الوزراء رقم (807)" or src.get("decree_date_hijri") != "14/11/1446":
        e.append("[2j] decree/decree_date_hijri mismatch with verified 807, 14/11/1446H")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (wholesale re-issue, "
                 "not an amendment-layered track)")

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
        print("FAIL: %d error(s) in GACA Organizational Statute track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Organizational Statute of the General Authority of Civil Aviation (GACA)")
    print("  - 15 records: 15 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-15); no inline")
    print("    per-article titles in the source (no title_ar key used)")
    print("  - VERIFICATION TIER: uqn.gov.sa (official Umm Al-Qura Gazette website) as")
    print("    primary source, word-for-word cross-checked against qanoonsa.com, tertiarily")
    print("    corroborated by argaam.com. laws.boe.gov.sa and web.archive.org both confirmed")
    print("    unreachable this pass -- honestly flagged, not silently upgraded")
    print("  - Council of Ministers Resolution 807 (14/11/1446H / 12 May 2025G), a wholesale")
    print("    consolidated re-issue superseding Resolution 33 (11/2/1426H) in full")
    print("  - Resolution 33's own text and its two prior amendments (28/1433H, 120/1438H)")
    print("    were deliberately NOT sourced -- flagged as an intentional scope decision")
    return 0


if __name__ == "__main__":
    sys.exit(main())
