#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Maritime Commercial Regulation track (لائحة
تسجيل السفن وقيد الوحدات البحرية -- Ship Registration and Maritime Unit
Registration Regulation, TGA): 49 records, all اصلية; hierarchical
structure: 4 فصول (أحكام تمهيدية 1-3، تسجيل السفينة 4-28، قيد الوحدة
البحرية 29-43، أحكام ختامية 44-49) plus a separate 22-row penalty table
(جدول العقوبات) that is NOT one of the 49 numbered articles.

VERIFICATION TIER -- see the generator's module docstring and
sources/maritime_commercial_regulation/law/official_source/
maritime_commercial_regulation_official_source.json's
verification_methodology_note for the full caveat: tga.gov.sa's LIVE portal
was unreachable this pass, but TWO INDEPENDENT Wayback Machine historical
snapshots of TGA's own page (2022-06-21 and 2025-01-17) were reachable and
found byte-for-byte identical; qistas.com's gated preview independently
corroborates Articles 1-3 only. This is a SINGLE-PRIMARY-SOURCE track
(TGA-via-Wayback) for Articles 4-49 and the penalty table -- a materially
weaker tier than the base maritime_commercial law's triple-cross-checked
tier -- and this is disclosed transparently rather than overstated.

This track ingests ONLY ONE member (ship registration) of a large family of
TGA-issued maritime regulations implementing the base Maritime Commercial
Law (Royal Decree M/33, 5/4/1440H) -- see known_unresolved_discrepancies
for the full enumerated family scope of un-ingested candidates.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "maritime_commercial_regulation", "law", "official_source",
                   "maritime_commercial_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "maritime_commercial_regulation", "law", "verified",
                       "maritime_commercial_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "maritime_commercial_regulation_arabic_legal_llm",
                   "maritime_commercial_regulation_legal_llm_001_049.json")
N = 49
KEY_RE = r"maritime_commercial_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 49, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
STATUS = "TGA_WAYBACK_DOUBLE_SNAPSHOT_X_QISTAS_PARTIAL_CROSSCHECK_LIVE_TGA_UNREACHABLE"
EXPECTED_TOP_LEVEL_CHAPTERS = 4  # 4 فصول, no فصل تمهيدي/أحكام ختامية wrapper beyond these
AMENDED_KEYS = set()  # no amended articles confirmed this pass
MUKARRAR_KEYS = set()  # no مكرر articles confirmed this pass (the claimed 46-مكرر is
                        # explicitly NOT ingested -- see known_unresolved_discrepancies)
EXPECTED_PENALTY_ROWS = 22
FLAGGED_DISCREPANCY_KEYS = {
    "maritime_commercial_regulation_decision_number_date_unconfirmed",
    "maritime_commercial_regulation_article_46_mukarrar_amendment_unconfirmed",
    "maritime_commercial_regulation_single_source_articles_4_to_49_and_penalty_table",
    "maritime_commercial_regulation_list_item_numbering_not_synthesized",
    "maritime_commercial_regulation_full_family_scope_not_ingested",
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
    for p in (SRC, RECORDS, LLM):
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
        e.append("[1c] expected %d top-level chapter_structure entries, got %d" %
                  (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

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

    pens = src.get("penalty_table_ar") or []
    if len(pens) != EXPECTED_PENALTY_ROWS:
        e.append("[1e] penalty_table_ar: %d rows != %d" % (len(pens), EXPECTED_PENALTY_ROWS))
    for i, row in enumerate(pens, start=1):
        if str(row.get("item_no")) != str(i):
            e.append("[1e] penalty row %d: item_no mismatch %r" % (i, row.get("item_no")))
        if not row.get("violation_ar", "").strip():
            e.append("[1e] penalty row %d: empty violation_ar" % i)
        if not row.get("penalty_sar_ar", "").strip():
            e.append("[1e] penalty row %d: empty penalty_sar_ar" % i)

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (expected a فصل path)" % k)
        if not a.get("number_label_ar", "").startswith("المادة"):
            e.append("[2] %s: number_label_ar does not start with 'المادة'" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in MUKARRAR_KEYS):
            e.append("[2] %s: legal_status_ar/MUKARRAR_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")):
            e.append("[2] %s: unexpected is_mukarrar=True (no مكرر articles confirmed "
                      "this pass -- the claimed Article 46 مكرر is deliberately NOT "
                      "ingested; see known_unresolved_discrepancies)" % k)
        if "\u00a0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "ًً" in a["text"]:
            e.append("[2g] %s: residual doubled-tanwin artifact detected" % k)
        if re.search(r"\(\s*\)\d", a["text"]):
            e.append("[2h] %s: residual bidi paren-before-digit artifact detected" % k)

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

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("maritime_commercial_regulation_art_001", {})
    if "النظام البحري التجاري" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected reference to the base Maritime "
                 "Commercial Law")
    if "م/33" not in art1.get("text", "") and "م/ 33" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected Royal Decree M/33 cross-reference")
    art49 = arts.get("maritime_commercial_regulation_art_049", {})
    if "الجريدة الرسمية" not in art49.get("text", ""):
        e.append("[2j] Article 49 missing expected Official Gazette publication clause")
    art44 = arts.get("maritime_commercial_regulation_art_044", {})
    if "جدول العقوبات" not in art44.get("text", ""):
        e.append("[2j] Article 44 missing expected cross-reference to the penalty table")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        expected_original = a.get("original_1440h_text")
        if r.get("original_text") != expected_original:
            e.append("[4] %s: original_text not propagated" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        if r["article_text_ar"] != arts[r["article_key"]]["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Maritime Commercial Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Maritime Commercial Regulation (Ship Registration) — 49 records (all اصلية)")
    print("  - hierarchical structure: 4 فصول (أحكام تمهيدية 1-3، تسجيل السفينة 4-28،")
    print("    قيد الوحدة البحرية 29-43، أحكام ختامية 44-49) + جدول عقوبات (22 بند)")
    print("  - VERIFICATION TIER: TGA-via-Wayback-Machine, two independent historical")
    print("    snapshots (2022-06-21 x 2025-01-17), byte-for-byte identical x")
    print("    qistas.com gated preview (Articles 1-3 only, partial cross-check);")
    print("    live TGA unreachable this pass -- single-primary-source tier for")
    print("    Articles 4-49 and the penalty table, disclosed as such")
    print("  - Implements Article 7 of the Maritime Commercial Law (Royal Decree")
    print("    M/33, 5/4/1440H)")
    print("  - Decision number/date UNCONFIRMED; claimed Article 46 مكرر amendment")
    print("    UNCONFIRMED (absent from TGA's own page in every snapshot 2022-2025)")
    print("  - ONE member of a large un-ingested TGA maritime-regulation family --")
    print("    see known_unresolved_discrepancies for the full enumerated scope")
    return 0


if __name__ == "__main__":
    sys.exit(main())
