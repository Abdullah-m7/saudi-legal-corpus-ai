#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the official-Arabic source VERIFICATION-COMPARISON report (no OCR engine needed).

Confirms the comparison stage is honest and non-destructive:
- the candidate is untouched: still 281 records, ingested_unverified, article_by_article_verified
  false, and NO record marked verified_against_official_gazette;
- the comparison report exists and covers exactly articles 1..281 with no gaps;
- summary counts equal the detailed entries;
- the scanned-PDF source metadata + capture metadata exist (RESULT: source_captured);
- English/Chinese/Arabic LLM data + official English reference + data/articles + schemas are
  unchanged in shape (no promotion / no official_text_ar leakage into derived layers).

Exit 0 == pass; 1 == problems. No network, no heavy dependencies.
"""

from __future__ import annotations

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAND = os.path.join(ROOT, "data", "official_arabic",
                    "companies_law_m132_1443_official_arabic_user_provided.json")
RPT_DIR = os.path.join(ROOT, "reports", "official_arabic_verification")
REPORT = os.path.join(RPT_DIR, "official_arabic_candidate_comparison_report.json")
AR_MD = os.path.join(RPT_DIR, "OFFICIAL_ARABIC_VERIFICATION_REPORT_AR.md")
SCANNED_META = os.path.join(RPT_DIR, "scanned_pdf_source_metadata.json")
CAPTURE_META = os.path.join(RPT_DIR, "official_source_capture_metadata.json")
PARTS_DIR = os.path.join(ROOT, "inputs", "official_arabic_verification",
                         "nizam_alsharikat_1443h_parts")

TARGET = 281
DIFF_TYPES = {"exact_match", "whitespace_or_markdown_only", "punctuation_or_spacing",
              "substantive_difference", "missing_in_official_source", "missing_in_candidate"}


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    problems = []

    # -- candidate untouched --------------------------------------------------
    if not os.path.exists(CAND):
        problems.append("candidate file missing")
    else:
        cand = _read(CAND)
        arts = cand.get("articles", [])
        if len(arts) != TARGET:
            problems.append("candidate must still have %d records (got %d)" % (TARGET, len(arts)))
        if [a.get("article_number") for a in arts] != list(range(1, TARGET + 1)):
            problems.append("candidate article numbers must still be 1..281 in order")
        if cand.get("verification_status") != "ingested_unverified":
            problems.append("candidate verification_status must still be ingested_unverified")
        if cand.get("article_by_article_verified") is not False:
            problems.append("candidate article_by_article_verified must still be false")
        for a in arts:
            if a.get("verification_status") == "verified_against_official_gazette":
                problems.append("candidate art %s marked verified_against_official_gazette" % a.get("article_number"))

    # -- comparison report ----------------------------------------------------
    report = None
    if not os.path.exists(REPORT):
        problems.append("comparison report missing")
    else:
        report = _read(REPORT)
        entries = report.get("entries", [])
        nums = [e.get("article_number") for e in entries]
        if nums != list(range(1, TARGET + 1)):
            problems.append("comparison entries must cover exactly articles 1..281 with no gaps")
        for e in entries:
            if e.get("difference_type") not in DIFF_TYPES:
                problems.append("art %s: invalid difference_type %r" % (e.get("article_number"), e.get("difference_type")))
        counts = report.get("summary_counts", {})
        if sum(counts.values()) != len(entries):
            problems.append("summary_counts total (%d) != number of entries (%d)" % (sum(counts.values()), len(entries)))
        for k in DIFF_TYPES:
            got = sum(1 for e in entries if e.get("difference_type") == k)
            if counts.get(k, 0) != got:
                problems.append("summary_counts[%s]=%s != actual %d" % (k, counts.get(k), got))
        if report.get("article_by_article_verified") is not False:
            problems.append("report must state article_by_article_verified false")
        if report.get("promoted_to_verified") is not False:
            problems.append("report must state promoted_to_verified false")
    if not os.path.exists(AR_MD):
        problems.append("Arabic report OFFICIAL_ARABIC_VERIFICATION_REPORT_AR.md missing")

    # -- source metadata (RESULT: source_captured) ----------------------------
    if not os.path.exists(SCANNED_META):
        problems.append("scanned_pdf_source_metadata.json missing")
    else:
        sm = _read(SCANNED_META)
        if sm.get("total_pages") != 119 or len(sm.get("parts", [])) != 6:
            problems.append("scanned source metadata must record 6 parts / 119 pages")
        for p in sm.get("parts", []):
            if not p.get("sha256"):
                problems.append("scanned source part missing sha256: %s" % p.get("file"))
    if not os.path.exists(CAPTURE_META):
        problems.append("official_source_capture_metadata.json missing")
    else:
        cm = _read(CAPTURE_META)
        if cm.get("article_by_article_verified") is not False:
            problems.append("capture metadata must state article_by_article_verified false")
    if not (os.path.isdir(PARTS_DIR) and len(glob.glob(os.path.join(PARTS_DIR, "*.pdf"))) == 6):
        problems.append("expected 6 PDF parts under inputs/official_arabic_verification/nizam_alsharikat_1443h_parts")

    # -- derived layers unchanged in shape ------------------------------------
    en = glob.glob(os.path.join(ROOT, "data", "english_legal_llm", "*_en_legal_llm.json"))
    if len(en) != 8 or sum(len(_read(x)["records"]) for x in en) != 87:
        problems.append("English Legal LLM must remain 8 files / 87 records")
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    if len(zh) != 5 or sum(len(_read(x)["records"]) for x in zh) != 23:
        problems.append("Chinese Legal LLM must remain 5 files / 23 records")
    for x in glob.glob(os.path.join(ROOT, "data", "arabic_legal_llm", "*_ar_legal_llm.json")):
        blob = open(x, encoding="utf-8").read().lower()
        if "official_text_ar" in blob or "verified_against_official_gazette" in blob:
            problems.append("Arabic Legal LLM must not be relabeled official: %s" % os.path.basename(x))
    ref = os.path.join(ROOT, "data", "english_reference")
    for fname, exp in (("book1_en_reference.json", list(range(1, 35))),
                       ("book2_en_reference.json", list(range(35, 51))),
                       ("book3_en_reference.json", list(range(51, 58)))):
        p = os.path.join(ref, fname)
        if os.path.exists(p) and [r["article_number"] for r in _read(p)["records"]] != exp:
            problems.append("official English reference changed: %s" % fname)
    for fname in ("book1_articles_001_034.json", "book2_articles_035_050.json", "book3_articles_051_057.json"):
        if not os.path.exists(os.path.join(ROOT, "data", "articles", fname)):
            problems.append("existing data/articles file missing: %s" % fname)
    if not os.path.exists(os.path.join(ROOT, "schemas", "official_arabic_article.schema.json")):
        problems.append("existing schema missing: official_arabic_article.schema.json")

    print("=" * 60)
    print("Official Arabic source VERIFICATION-COMPARISON report validation")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    c = report["summary_counts"]
    print("[PASS] comparison report over 281 articles (aligned=%d/281); exact=%d normalized=%d "
          "punct/space=%d substantive=%d missing_source=%d; candidate untouched "
          "(ingested_unverified, article_by_article_verified=false, nothing verified); source "
          "packet 6 parts/119 pages hashed; derived layers unchanged."
          % (report["official_source_articles_aligned"], c["exact_match"],
             report["normalized_match_count"], c["punctuation_or_spacing"],
             c["substantive_difference"], c["missing_in_official_source"]))
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
