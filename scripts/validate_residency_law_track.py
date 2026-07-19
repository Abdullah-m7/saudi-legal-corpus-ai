#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Foreigners' Residency Law track (نظام
الإقامة, Royal (Supreme) Order 17/2/25/1337 dated 11/9/1371H).

69 ingested records: 48 اصلية, 16 معدلة, 1 ملغاة (Article 37, preserved not
deleted), 4 مضافة (5 مكرر, 44 مكرر, 49 مكررة, 62 مكرر). A confirmed-but-
textually-unrecovered 5th مكرر article (61 مكرر) is deliberately NOT
ingested -- see the generator's module docstring and the official_source.json's
known_unresolved_discrepancies for the full account.

VERIFICATION TIER: TIER_3 -- laws.boe.gov.sa does not index this 1371H base
law at all (only the unrelated, much newer نظام الإقامة المميزة, M/106,
1440H, is BOE-indexed), and BOE's live portal was unreachable this pass
(connection reset). The Ministry of Interior's own hosted PDF could not be
reached live (connection reset) nor recovered via the Wayback Machine (only
a dead 404 and a live-site error page were archived, not the PDF). This
track instead rests on a cross-verified secondary reproduction of the
officially-circulated compiled document "نظام الإقامة والتعديلات الصادرة
عليه" -- independently found in four separately-hosted forms (an NSHR PDF,
structurally confirming but font-corrupted; two independent clean HTML
transcriptions agreeing word-for-word with each other and with the PDF's
own pagination; and a fourth partial independent transcription). This
validator does not attempt to re-adjudicate any of this; it only checks
internal self-consistency of the text this track actually ingests, and
that every discrepancy found is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "residency", "law", "official_source",
                   "residency_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "residency", "law", "verified",
                       "residency_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "residency", "law", "verified",
                       "residency_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "residency_arabic_legal_llm",
                   "residency_law_legal_llm_001_069.json")
N_BASE = 65
N_TOTAL = 69
KEY_RE = r"residency_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 48, "معدلة": 16, "ملغاة": 1, "مضافة": 4}
EXPECTED_TOP_LEVEL_CHAPTERS = 4  # 4 فصول (chapters), no أبواب

TOP_STATUS = ("RESIDENCY_LAW_SECONDARY_CROSS_VERIFIED_MOHAMAH_RAKADVOCATE_ISLAMPORT_"
              "NSHR_PDF_STRUCTURAL_MATCH_BOE_NOT_INDEXED_MOI_LIVE_AND_WAYBACK_UNREACHABLE")
AMENDED_KEYS = {"residency_art_%03d" % n for n in
                (14, 16, 25, 31, 35, 38, 43, 44, 45, 46, 47, 52, 53, 56, 60, 61)}
REPEALED_KEYS = {"residency_art_037"}
ADDED_KEYS = {"residency_art_005_mukarrar", "residency_art_044_mukarrar",
              "residency_art_049_mukarrar", "residency_art_062_mukarrar"}
MUKARRAR_KEYS = ADDED_KEYS
FLAGGED_DISCREPANCY_KEYS = {
    "residency_boe_not_indexed_moi_unreachable",
    "residency_article5_mukarrar_decree_citation_inconsistency",
    "residency_article52_amending_decree_number_typo",
    "residency_article61_mukarrar_text_not_recovered",
    "residency_no_specific_named_predecessor",
    "residency_nshr_pdf_font_corruption",
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
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d top-level chapter_structure entries (4 فصول, "
                  "no أبواب), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one leaf range" % n)
            covered.add(n)
    if covered != set(range(1, N_BASE + 1)):
        missing = sorted(set(range(1, N_BASE + 1)) - covered)
        extra = sorted(covered - set(range(1, N_BASE + 1)))
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
        if "النِظام" in a["text"] or "نظَام" in a["text"]:
            e.append("[2] %s: un-normalized spurious diacritic on نظام present" % k)
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
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present (this law's compiled source "
                      "supplies no inline per-article titles -- see "
                      "known_unresolved_discrepancies)" % k)
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
        e.append("[2k] missing amendment_history (must record the original Order and key "
                  "amendments)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        for token in ("17/2/25/1337", "م/48", "م/56"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference %s" % token)

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("residency_art_001", {})
    if "نظام الإقامة" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected naming clause")
    art37 = arts.get("residency_art_037", {})
    if art37.get("legal_status_ar") != "ملغاة":
        e.append("[2j] Article 37 must be legal_status_ar=ملغاة (repealed by M/48, "
                  "10/10/1391H) and its pre-repeal text preserved, not deleted")
    if not art37.get("text", "").strip():
        e.append("[2j] Article 37's preserved (pre-repeal) text must not be empty")
    art64 = arts.get("residency_art_064", {})
    if "يلغي" not in art64.get("text", ""):
        e.append("[2j] Article 64 missing expected general repeal clause")
    art65 = arts.get("residency_art_065", {})
    if "وزارة الداخلية" not in art65.get("text", ""):
        e.append("[2j] Article 65 missing expected implementing-ministries clause")
    if "residency_art_061_mukarrar" in arts:
        e.append("[2j] Article 61 mukarrar's text was never recovered from any source and "
                  "must NOT be present/fabricated in articles{} (see "
                  "known_unresolved_discrepancies)")
    if src.get("decree") != "الأمر الملكي رقم (17/2/25/1337)" or src.get("decree_date_hijri") != "11/9/1371":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Order 17/2/25/1337, 11/9/1371H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")

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
        print("FAIL: %d error(s) in Residency Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Foreigners' Residency Law (نظام الإقامة)")
    print("  - 69 ingested records: 48 اصلية, 16 معدلة, 1 ملغاة (Article 37, preserved), "
          "4 مضافة (5, 44, 49, 62 مكرر)")
    print("  - Article 61 مكرر confirmed added (M/56, 4/9/1427H) but its text could not be "
          "recovered from any source checked -- deliberately NOT ingested, flagged instead")
    print("  - 4 فصول (chapters), no أبواب: 1-31 / 32-42 / 43-49 / 50-65")
    print("  - VERIFICATION TIER: TIER_3 -- BOE does not index this law at all (only the "
          "unrelated نظام الإقامة المميزة, M/106, 1440H, is BOE-indexed); BOE live portal "
          "and MOI's own hosted PDF both unreachable this pass (live + Wayback); sourced "
          "from a cross-verified secondary reproduction of the officially-circulated "
          "compiled text (mohamah.net x rakadvocate.blogspot.com x islamport.com x NSHR "
          "PDF structural cross-check)")
    print("  - Royal (Supreme) Order 17/2/25/1337 (11/9/1371H / ~1951-1952G); Article 64 "
          "states only a GENERAL repeal of prior orders/instructions, no specific named "
          "predecessor law found")
    print("  - GENUINE ANOMALIES carried forward: Article 5 مكرر's adding decree/resolution "
          "number and date are internally inconsistent across three citations in the same "
          "compiled source (م/4 vs م/40; 1393H vs 1394H); Article 52's second-amendment note "
          "literally cites \"المادة (5)\" (almost certainly a typo for (52) given context)")
    print("  - Companion instruments identified but NOT ingested this pass: نظام الإقامة "
          "المميزة (M/106, 1440H) + its لائحة تنفيذية; نظام الجوازات السفرية; Muqeem/"
          "exit-re-entry visa rules")
    return 0


if __name__ == "__main__":
    sys.exit(main())
