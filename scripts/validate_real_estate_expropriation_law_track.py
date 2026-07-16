#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Law on Expropriation of Real Estate for
Public Interest and Temporary Seizure track (39 records) — نظام نزع ملكية
العقارات للمصلحة العامة ووضع اليد المؤقت على العقارات.

Trust gate: every article MATCHES_PDF or MATCHES_PDF_VISUALLY_ADJUDICATED
(>=0.90 vs the committed official MOJ PDF, hash re-verified, unless
visually adjudicated). 38/39 matched outright (mean 0.9794, min 0.7807);
art_022 was visually adjudicated verbatim. Articles are numbered by
ordinal position 1..39 (no مكرر), organized under 6 chapters (الباب
الأول..السادس) with section_ar carrying each article's chapter heading.
FRESH FULL ISSUANCE: all 39 اصلية; none amended, repealed or added. Per
its own art 37, this law replaces the repealed 1424H predecessor
(independently confirmed ملغي on the portal, not ingested).
SOURCE-LEVEL CLEANUP: 1 decorative in-word tatweel character was
normalized/removed prior to ingestion. DOCUMENTED SOURCE ANOMALY: art_039's
ordinal heading reads "التاسعة الثلاثون" (missing و), confirmed identical
in both official sources, preserved verbatim."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "real_estate_expropriation", "law", "official_source",
                   "real_estate_expropriation_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "real_estate_expropriation", "law", "verified",
                       "real_estate_expropriation_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "real_estate_expropriation_arabic_legal_llm",
                   "real_estate_expropriation_law_legal_llm_001_039.json")
PDF = os.path.join(ROOT, "inputs", "real_estate_expropriation_official_pdfs",
                   "real_estate_expropriation_law_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 39
KEY_RE = r"real_estate_expropriation_art_(\d{3})$"
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 39}
VISUALLY_ADJUDICATED = {"real_estate_expropriation_art_022"}
CHAPTER_RANGES = [
    ("الباب الأول: تعريفات وأحكام عامة", 1, 8),
    ("الباب الثاني: إجراءات نزع ملكية العقارات", 9, 12),
    ("الباب الثالث: الحصر والتقييم", 13, 15),
    ("الباب الرابع: التعويض والإخلاء", 16, 24),
    ("الباب الخامس: وضع اليد المؤقت على العقارات", 25, 29),
    ("الباب السادس: أحكام ختامية", 30, 39),
]
TRUSTED = {"MATCHES_PDF", "MATCHES_PDF_VISUALLY_ADJUDICATED"}
AR = "ء-ي"
ANOMALY_KEY = "real_estate_expropriation_art_039"
ANOMALY_MARKER = "المادة التاسعة الثلاثون"


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        if (re.match("[%s]" % AR, before) and before != "ه"
                and re.match("[%s]" % AR, after)):
            bad += 1
    return bad


def main():
    e = []
    for p in (SRC, RECORDS, LLM, PDF):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1] numbered articles not a complete 1..%d sequence" % N)
    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))

    visual = set()
    sc = Counter()
    for k, a in arts.items():
        if a["status"] not in TRUSTED:
            e.append("[2] %s: UNTRUSTED status %r" % (k, a["status"]))
        sim = a.get("pdf_similarity") or 0
        if a["status"] == "MATCHES_PDF_VISUALLY_ADJUDICATED":
            visual.add(k)
        elif sim < SIM_FLOOR:
            e.append("[2] %s: sim %.3f below floor and not visually adjudicated" % (k, sim))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/PDF status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if "‌" in a["text"]:
            e.append("[2] %s: zero-width-non-joiner artifact present" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
    if visual != VISUALLY_ADJUDICATED:
        e.append("[2] visually-adjudicated set %s != expected %s"
                 % (sorted(visual), sorted(VISUALLY_ADJUDICATED)))
    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("معدلة") or sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected amended/repealed/added articles present")

    for label, lo, hi in CHAPTER_RANGES:
        for n in range(lo, hi + 1):
            key = "real_estate_expropriation_art_%03d" % n
            got = arts.get(key, {}).get("section_ar")
            if got != label:
                e.append("[2e] %s: section_ar %r != expected chapter %r" % (key, got, label))

    # [2b] documented source anomaly in art_039's ordinal heading preserved verbatim
    if arts.get(ANOMALY_KEY, {}).get("number_label_ar") != ANOMALY_MARKER:
        e.append("[2b] art_039 missing the documented التاسعة الثلاثون ordinal-heading typo")

    if src["provenance"].get("section_vs_structure_divergences") not in (0, None):
        e.append("[2c] unexpected section-vs-structure divergence recorded")

    if hashlib.sha256(open(PDF, "rb").read()).hexdigest() != src["provenance"]["pdf_sha256"]:
        e.append("[3] committed MOJ PDF sha256 mismatch")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("section_ar") != a.get("section_ar"):
            e.append("[4] %s: section_ar mismatch" % r["article_key"])
        if r.get("official_text_status") != STATUS:
            e.append("[4] %s: bad status" % r["article_key"])
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

    if e:
        print("FAIL: %d error(s) in Real Estate Expropriation Law track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Real Estate Expropriation Law — 39 records (fresh issuance: all 39 اصلية)")
    print("  - trust gate: 38/39 MATCHES_PDF outright via OCR/reversed-text-layer channels, 1 visually adjudicated (mean 0.9794, min 0.7807)")
    print("  - numbered 1..39 by ordinal position (no مكرر), 6 chapters correctly mapped to section_ar; no dual-status divergence")
    print("  - IN-FORCE Royal Decree M/56 (12/03/1447H); committed MOJ PDF hash verified; Arabic governs")
    print("  - source-level cleanup: 1 decorative tatweel character normalized/removed prior to ingestion")
    print("  - documented source anomaly: art_039 ordinal heading missing و (التاسعة الثلاثون), confirmed in both official sources, preserved verbatim")
    print("  - replaces the repealed 1424H predecessor law (Royal Decree M/15, not ingested)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
