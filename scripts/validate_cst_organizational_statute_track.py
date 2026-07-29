#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Organizational Statute of the Communications,
Space and Technology Commission (CST) track (19 records: 13 اصلية, 6 معدلة,
0 ملغاة, 0 مضافة; flat structure -- NO أبواب/فصول grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/cst_organizational_statute/law/official_source/
cst_organizational_statute_official_source.json's verification_methodology_
note for the full account: laws.boe.gov.sa's LIVE portal and cst.gov.sa both
returned a TLS connection reset on every direct attempt this pass, but the
Wayback Machine itself was fully reachable, giving TWO snapshots of BOE's
own LawDetails page (11 Feb 2025, 27 Feb 2026) as this track's primary
grounding. BOE's own page carries Resolution 430's popup text verbatim for
Articles 3 and 4 only (word-for-word match with qanoonsa.com's Umm Al-Qura
Gazette reproduction); Articles 1, 5, 8 and 10's 2024-amendment text rests
on qanoonsa.com alone (BOE confirmed stale/absent for these four articles'
popups). This validator does not attempt to re-adjudicate any of this; it
only checks internal self-consistency of the text this track actually
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
SRC = os.path.join(ROOT, "sources", "cst_organizational_statute", "law", "official_source",
                   "cst_organizational_statute_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "cst_organizational_statute", "law", "verified",
                       "cst_organizational_statute_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "cst_organizational_statute", "law", "verified",
                       "cst_organizational_statute_verified_summary.json")
LLM = os.path.join(ROOT, "data", "cst_organizational_statute_arabic_legal_llm",
                   "cst_organizational_statute_legal_llm_001_019.json")
N = 19
BASE_ARTICLE_COUNT = 19
KEY_RE = r"cst_organizational_statute_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 13, "معدلة": 6, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat law -- no أبواب/فصول, single leaf range 1-19

STATUS_UNCHANGED = ("BOE_WAYBACK_DUAL_SNAPSHOT_2025_02_AND_2026_02_X_NEZAMS_COM_TRIPLE_CROSS_"
                     "VERIFIED_LIVE_BOE_TLS_RESET_THIS_PASS")
STATUS_ART1 = ("BOE_WAYBACK_BASE_TEXT_DUAL_SNAPSHOT_X_QANOONSA_COM_UMM_AL_QURA_5065_"
               "REPRODUCTION_FOR_RESOLUTION_430_DELTA_ONLY_BOE_ARTICLE_POPUP_NOT_YET_"
               "PUBLISHED_FOR_THIS_ARTICLE")
STATUS_ART3 = ("BOE_WAYBACK_ARTICLE_POPUP_2026_02_SNAPSHOT_X_QANOONSA_COM_UMM_AL_QURA_5065_"
               "VERBATIM_WORD_FOR_WORD_MATCH_RESOLUTION_430_FULL_SUBSTITUTION")
STATUS_ART4 = ("BOE_WAYBACK_ARTICLE_POPUP_2026_02_SNAPSHOT_X_QANOONSA_COM_UMM_AL_QURA_5065_"
               "VERBATIM_WORD_FOR_WORD_MATCH_RESOLUTION_430_FULL_SUBSTITUTION_CHAINED_AFTER_"
               "RESOLUTION_120_BOE_POPUP_NUMBER_BLANK_FILLED_FROM_NEZAMS_AND_QANOONSA")
STATUS_ART5 = ("QANOONSA_COM_UMM_AL_QURA_5065_REPRODUCTION_ONLY_FOR_RESOLUTION_430_PARTIAL_"
               "AMENDMENT_BOE_ARTICLE_POPUP_NOT_YET_PUBLISHED_FOR_THIS_ARTICLE_BASE_TEXT_BOE_"
               "WAYBACK_DUAL_SNAPSHOT_X_NEZAMS_VERIFIED")
STATUS_ART8 = ("QANOONSA_COM_UMM_AL_QURA_5065_REPRODUCTION_ONLY_FOR_RESOLUTION_430_ADDED_"
               "PARAGRAPHS_BOE_ARTICLE_POPUP_NOT_YET_PUBLISHED_FOR_THIS_ARTICLE_BASE_TEXT_BOE_"
               "WAYBACK_DUAL_SNAPSHOT_X_NEZAMS_VERIFIED")
STATUS_ART10 = ("QANOONSA_COM_UMM_AL_QURA_5065_REPRODUCTION_ONLY_FOR_RESOLUTION_430_FULL_"
                "SUBSTITUTION_BOE_ARTICLE_POPUP_NOT_YET_PUBLISHED_FOR_THIS_ARTICLE_BASE_TEXT_"
                "BOE_WAYBACK_DUAL_SNAPSHOT_X_NEZAMS_VERIFIED")
EXPECTED_STATUS_BY_KEY = {
    "cst_organizational_statute_art_001": STATUS_ART1,
    "cst_organizational_statute_art_003": STATUS_ART3,
    "cst_organizational_statute_art_004": STATUS_ART4,
    "cst_organizational_statute_art_005": STATUS_ART5,
    "cst_organizational_statute_art_008": STATUS_ART8,
    "cst_organizational_statute_art_010": STATUS_ART10,
}
AMENDED_KEYS = {
    "cst_organizational_statute_art_001", "cst_organizational_statute_art_003",
    "cst_organizational_statute_art_004", "cst_organizational_statute_art_005",
    "cst_organizational_statute_art_008", "cst_organizational_statute_art_010",
}
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
FLAGGED_DISCREPANCY_KEYS = {
    "cst_boe_stale_no_popup_for_articles_1_5_8_10",
    "cst_article1_entity_name_not_updated_despite_two_renames",
    "cst_resolution133_and_253_renames_not_spliced_into_articles",
    "cst_resolution524_681_referenced_not_independently_sourced",
    "cst_article5_letter_gap_after_deletion_of_ta",
    "cst_article1_new_definition_position_unspecified",
    "cst_no_named_predecessor_found",
    "cst_boe_and_cst_gov_sa_live_both_tls_reset_this_pass",
    "cst_nezams_stale_confirms_base_and_120_only",
    "cst_board_continuity_transitional_clause_not_ingested_as_article",
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
    key), so this is a flat single-level walk over the 19 articles."""
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

    if len(arts.get("cst_organizational_statute_art_003", {}).get("history", [])) != 2:
        e.append("[2j] Article 3 must record exactly 2 amendment history entries (133, 430)")
    if len(arts.get("cst_organizational_statute_art_004", {}).get("history", [])) != 2:
        e.append("[2j] Article 4 must record exactly 2 amendment history entries (120, 430)")

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
        e.append("[2k] missing amendment_history (must record 74, 133, 120, 253, and 430)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        for token in ("74", "133", "120", "253", "430"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference %s" % token)

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("cst_organizational_statute_art_001", {})
    if "القطاعات ذات الصلة بالهيئة" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected Resolution-430 added definition")
    if "النظام: نظام الاتصالات" in art1.get("text", "").replace("\n", " "):
        e.append("[2j] Article 1 unexpectedly retains the النظام definition deleted by "
                 "Resolution 430")
    if "هيئة الاتصالات السعودية" not in art1.get("text", ""):
        e.append("[2j] Article 1 unexpectedly missing the original (never-updated) الهيئة/"
                 "التنظيم definitions naming the Authority's 2001 name -- see "
                 "cst_article1_entity_name_not_updated_despite_two_renames")
    art3 = arts.get("cst_organizational_statute_art_003", {})
    if "26- أي مهمة أو اختصاص آخر" not in art3.get("text", ""):
        e.append("[2j] Article 3 missing expected Resolution-430 26th (final) function")
    if "قطاع الفضاء المدني" not in art3.get("text", ""):
        e.append("[2j] Article 3 missing expected civil-space-sector function")
    art4 = arts.get("cst_organizational_statute_art_004", {})
    if "ز- ثلاثة من القطاع الخاص" not in art4.get("text", ""):
        e.append("[2j] Article 4 missing expected Resolution-430 private-sector seats clause")
    if "وزارة البرق والبريد والهاتف" in art4.get("text", ""):
        e.append("[2j] Article 4 unexpectedly contains stale pre-2024 ministry wording")
    art5 = arts.get("cst_organizational_statute_art_005", {})
    if "تشكيل اللجان وتخويلها الصلاحيات اللازمة لإنجاز المهام المناطة بها" in art5.get("text", ""):
        e.append("[2j] Article 5 unexpectedly retains the ط paragraph deleted by Resolution 430")
    if "وللمجلس -في سبيل ممارسته لصلاحياته واختصاصاته-" not in art5.get("text", ""):
        e.append("[2j] Article 5 missing expected Resolution-430 added closing paragraph")
    art8 = arts.get("cst_organizational_statute_art_008", {})
    if "ل- التعاقد لتنفيذ الأعمال والخدمات" not in art8.get("text", ""):
        e.append("[2j] Article 8 missing expected Resolution-430 added paragraph ل")
    art10 = arts.get("cst_organizational_statute_art_010", {})
    if "حصيلة الغرامات المفروضة المنصوص عليها في النظام" in art10.get("text", ""):
        e.append("[2j] Article 10 unexpectedly retains the pre-2024 original text")
    if "أسماء النطاقات السعودية" not in art10.get("text", ""):
        e.append("[2j] Article 10 missing expected Resolution-430 domain-name resource item")
    if src.get("decree") != "قرار مجلس الوزراء رقم (74)" or src.get("decree_date_hijri") != "5/3/1422":
        e.append("[2j] decree/decree_date_hijri mismatch with verified 74, 5/3/1422H")

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
        print("FAIL: %d error(s) in CST Organizational Statute track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Organizational Statute of the Communications, Space and Technology Commission")
    print("  - 19 records: 13 اصلية, 6 معدلة, 0 ملغاة, 0 مضافة")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-19); no inline")
    print("    per-article titles in the source (no title_ar key used)")
    print("  - VERIFICATION TIER: BOE's own portal via two Wayback Machine snapshots (Feb")
    print("    2025, Feb 2026); live BOE and cst.gov.sa both TLS-reset this pass. BOE's own")
    print("    popups verbatim-match qanoonsa.com for Articles 3/4 only; Articles 1, 5, 8,")
    print("    10's 2024-amendment (Resolution 430) text rests on qanoonsa.com alone --")
    print("    honestly flagged per-article variation, not silently upgraded")
    print("  - Council of Ministers Resolution 74 (5/3/1422H); no named predecessor found")
    print("    (Authority newly created in 2001) -- a confirmed negative finding")
    print("  - Articles 3 and 4 safely chained through superseded intermediate amendments")
    print("    (133->430 for Art.3; 120->430 for Art.4), each a complete substitution")
    print("  - CONFIRMED CARRIED-FORWARD INCONSISTENCY: Article 1's التنظيم/الهيئة/المجلس/")
    print("    المحافظ/العضو definitions still name the Authority's original 2001 name,")
    print("    never textually updated by either renaming decision (133 or 253) -- honestly")
    print("    flagged, not silently harmonized")
    return 0


if __name__ == "__main__":
    sys.exit(main())
