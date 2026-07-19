#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Premium Residency Law track (نظام الإقامة
المميزة, Royal Decree No. M/106 dated 10/9/1440H).

14 ingested records: 5 اصلية (Articles 7, 9, 12, 13, 14), 8 معدلة (Articles
1, 2, 3, 4, 5, 6, 10, 11), 1 ملغاة (Article 8, preserved not deleted), 0
مضافة (no standalone مكرر articles). See the generator's module docstring
and the official_source.json's known_unresolved_discrepancies for the full
account, including why Articles 9 and 13 are classified اصلية (matching
BOE's own per-article tagging) despite their wording reflecting a downstream
global term-substitution (اللجنة -> المجلس) from Article 1's own amendment.

VERIFICATION TIER: TIER_1_PRIMARY_MULTI_SOURCE -- laws.boe.gov.sa's live
portal was unreachable this pass (connection reset), but six independent
Wayback Machine snapshots of BOE's own dedicated lawId page (spanning 22 Nov
2019 through 16 Nov 2025) were checked and are internally consistent with
the real amendment timeline. Critically, an independent OFFICIAL government
source (misa.gov.sa, the Ministry of Investment's own hosted consolidated-
text PDF) was directly fetched and agrees word-for-word with the text
reconstructed here from BOE's own quoted amendment instructions, at every
point checked but one (a single missing word in Article 2(e), disclosed).
This validator does not re-adjudicate any of this; it only checks internal
self-consistency of the text this track actually ingests, and that every
discrepancy found is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "premium_residency", "law", "official_source",
                   "premium_residency_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "premium_residency", "law", "verified",
                       "premium_residency_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "premium_residency", "law", "verified",
                       "premium_residency_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "premium_residency_arabic_legal_llm",
                   "premium_residency_law_legal_llm_001_014.json")
N_TOTAL = 14
KEY_RE = r"premium_residency_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 5, "معدلة": 8, "ملغاة": 1, "مضافة": 0}
EXPECTED_TOP_LEVEL_SECTIONS = 6  # thematic sections, no formal أبواب/فصول

TOP_STATUS = ("PREMIUM_RESIDENCY_LAW_BOE_LIVE_UNREACHABLE_WAYBACK_MULTI_SNAPSHOT_2019_2025_"
              "X_MISA_OFFICIAL_CONSOLIDATED_PDF_CROSS_VERIFIED")
AMENDED_KEYS = {"premium_residency_art_%03d" % n for n in (1, 2, 3, 4, 5, 6, 10, 11)}
REPEALED_KEYS = {"premium_residency_art_008"}
ADDED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
FLAGGED_DISCREPANCY_KEYS = {
    "premium_residency_boe_live_unreachable_wayback_multi_snapshot",
    "premium_residency_misa_haqq_word_omission",
    "premium_residency_global_substitution_untagged_articles",
    "premium_residency_repealed_subitem_placeholder_not_renumbered",
    "premium_residency_implementing_regulation_not_ingested",
    "premium_residency_companion_center_bylaw_not_ingested",
    "premium_residency_no_named_predecessor_repealed",
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


def _iter_section_ranges(chs):
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

    if len(arts) != N_TOTAL:
        e.append("[1] %d articles != %d" % (len(arts), N_TOTAL))
    if src.get("article_count") != N_TOTAL:
        e.append("[1] article_count field != %d" % N_TOTAL)
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_SECTIONS:
        e.append("[1c] expected %d thematic sections (no formal أبواب/فصول), "
                  "got %d" % (EXPECTED_TOP_LEVEL_SECTIONS, n_top))

    covered = set()
    for lo, hi in _iter_section_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one section range" % n)
            covered.add(n)
    if covered != set(range(1, N_TOTAL + 1)):
        missing = sorted(set(range(1, N_TOTAL + 1)) - covered)
        extra = sorted(covered - set(range(1, N_TOTAL + 1)))
        if missing:
            e.append("[1c] chapter_structure missing article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != TOP_STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, TOP_STATUS, a.get("status")))
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
        if k in (AMENDED_KEYS | REPEALED_KEYS | ADDED_KEYS) and not a.get("history"):
            e.append("[2] %s: amended/repealed/added article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if k not in (AMENDED_KEYS | REPEALED_KEYS | ADDED_KEYS) and a.get("history"):
            e.append("[2i] %s: unamended/non-added/non-repealed article must have empty "
                      "history[]" % k)
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
        e.append("[2k] missing amendment_history (must record the founding decree and "
                  "subsequent amendments)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        for token in ("م/106", "م/71", "594", "555", "م/84"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference %s" % token)

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("premium_residency_art_001", {})
    if "المجلس: مجلس إدارة المركز" not in art1.get("text", ""):
        e.append("[2j] Article 1 must carry the CURRENT (post-CoM-555) المجلس definition, "
                 "not the superseded اللجنة definition")
    if "الوالدين" not in art1.get("text", ""):
        e.append("[2j] Article 1's أسرة definition must reflect the M/84 (1445H) amendment "
                 "adding الوالدين")
    art3 = arts.get("premium_residency_art_003", {})
    if "دائمة" not in art3.get("text", "") or "غير محددة المدة" in art3.get("text", ""):
        e.append("[2j] Article 3 must carry the CURRENT (post-M/84) دائمة/محددة المدة "
                 "residency types, not the superseded غير محددة المدة wording")
    art4 = arts.get("premium_residency_art_004", {})
    if "(ألغيت)" not in art4.get("text", ""):
        e.append("[2j] Article 4 must preserve sub-item (ب)'s repeal as an explicit "
                 "(ألغيت) placeholder, not silently delete or renumber it")
    art8 = arts.get("premium_residency_art_008", {})
    if art8.get("legal_status_ar") != "ملغاة":
        e.append("[2j] Article 8 must be legal_status_ar=ملغاة (repealed by M/84, 11/6/1445H) "
                 "with its pre-repeal text preserved, not deleted")
    if not art8.get("text", "").strip():
        e.append("[2j] Article 8's preserved (pre-repeal) text must not be empty")
    art14 = arts.get("premium_residency_art_014", {})
    if "الجريدة الرسمية" not in art14.get("text", ""):
        e.append("[2j] Article 14 missing expected entry-into-force clause")
    if "premium_residency_art_015" in arts:
        e.append("[2j] this Law has exactly 14 articles -- no Article 15 should be present")
    if src.get("decree") != "المرسوم الملكي رقم (م/106)" or src.get("decree_date_hijri") != "10/9/1440":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/106, "
                 "10/9/1440H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (this track ingests the current, "
                 "post-amendment consolidated text)")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N_TOTAL:
        e.append("[4] %d verified records != %d" % (len(ver), N_TOTAL))
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
    if summary.get("record_count") != N_TOTAL:
        e.append("[4b] summary record_count != %d" % N_TOTAL)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N_TOTAL or len(recs) != N_TOTAL:
        e.append("[5] llm count != %d" % N_TOTAL)
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
        if r.get("source_trust", {}).get("source_status") != TOP_STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Premium Residency Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Premium Residency Law (نظام الإقامة المميزة)")
    print("  - 14 ingested records: 5 اصلية, 8 معدلة, 1 ملغاة (Article 8, preserved), "
          "0 مضافة")
    print("  - flat 14-article structure, no formal أبواب/فصول; 6 informal thematic sections "
          "for indexing only")
    print("  - VERIFICATION TIER: TIER_1_PRIMARY_MULTI_SOURCE -- BOE live portal unreachable, "
          "but six independent Wayback snapshots (2019-2025) of BOE's own lawId page were "
          "checked and are internally consistent with the real amendment timeline; "
          "cross-verified word-for-word against misa.gov.sa's (Ministry of Investment) own "
          "hosted consolidated-text PDF, agreeing at every point but one disclosed one-word "
          "discrepancy")
    print("  - Royal Decree M/106 (10/9/1440H / 15 May 2019G); Article 14 names no repealed "
          "predecessor law -- confirmed negative finding, a wholly new residency category "
          "distinct from this corpus's already-ingested residency_law (1371H Iqama/Kafala law)")
    print("  - GENUINE ANOMALIES carried forward: BOE's own per-article tagging does not mark "
          "Articles 9/13 as معدلة despite their wording reflecting a downstream global "
          "اللجنة->المجلس substitution from Article 1's own amendment; MISA's PDF omits the "
          "word حق in Article 2(e) vs BOE's stable wording; repealed sub-items preserved as "
          "explicit (ألغيت) placeholders, not renumbered")
    print("  - Companion instruments identified but NOT ingested this pass: اللائحة التنفيذية "
          "لنظام الإقامة المميزة (only a paraphrased secondary summary found, no verbatim "
          "text); تنظيم مركز الإقامة المميزة (separate organizational bylaw for the Center)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
