#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the official-Arabic OCR MANUAL-REVIEW QUEUE (no OCR engine needed).

Confirms the queue is complete and non-destructive: 281 entries (1..281), every entry
bucketed + prioritised, summary P0/P1 consistent with entries, and the candidate + derived
layers are untouched and un-promoted.

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import csv
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RPT_DIR = os.path.join(ROOT, "reports", "official_arabic_verification")
QJSON = os.path.join(RPT_DIR, "manual_review_queue.json")
QCSV = os.path.join(RPT_DIR, "manual_review_queue.csv")
QMD = os.path.join(RPT_DIR, "OFFICIAL_ARABIC_OCR_MANUAL_REVIEW_QUEUE_AR.md")
CAND = os.path.join(ROOT, "data", "official_arabic",
                    "companies_law_m132_1443_official_arabic_user_provided.json")

TARGET = 281
BUCKETS = {"exact_match_no_action", "normalized_or_punctuation_review",
           "likely_ocr_noise_high_similarity", "likely_ocr_noise_medium_similarity",
           "low_similarity_manual_review", "missing_or_segmentation_issue",
           "possible_substantive_difference_manual_review"}
PRIOS = {"P0", "P1", "P2", "P3", "P4", "P5", "P6"}


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    problems = []

    for p, label in ((QJSON, "manual_review_queue.json"), (QCSV, "manual_review_queue.csv"),
                     (QMD, "OFFICIAL_ARABIC_OCR_MANUAL_REVIEW_QUEUE_AR.md")):
        if not os.path.exists(p):
            problems.append("missing: %s" % label)

    q = _read(QJSON) if os.path.exists(QJSON) else None
    if q is not None:
        entries = q.get("entries", [])
        if len(entries) != TARGET:
            problems.append("expected %d queue entries (got %d)" % (TARGET, len(entries)))
        if [e.get("article_number") for e in entries] != list(range(1, TARGET + 1)):
            problems.append("queue entries must be article numbers 1..281 in order")
        for e in entries:
            n = e.get("article_number")
            if e.get("review_bucket") not in BUCKETS:
                problems.append("art %s: invalid review_bucket %r" % (n, e.get("review_bucket")))
            if e.get("review_priority") not in PRIOS:
                problems.append("art %s: invalid review_priority %r" % (n, e.get("review_priority")))
            if e.get("verification_action_allowed") is not False:
                problems.append("art %s: verification_action_allowed must be false" % n)
            for k in ("article_title_ar", "original_difference_type", "candidate_hash",
                      "candidate_text_length", "ocr_text_length", "suspected_issue",
                      "recommended_action"):
                if k not in e:
                    problems.append("art %s: missing field %s" % (n, k))
        if q.get("article_by_article_verified") is not False:
            problems.append("queue must state article_by_article_verified false")
        if q.get("promoted_to_verified") is not False:
            problems.append("queue must state promoted_to_verified false")
        # summary P0/P1 (and all priority) counts equal detailed entries
        pc = q.get("priority_counts", {})
        for pr in PRIOS:
            got = sum(1 for e in entries if e.get("review_priority") == pr)
            if got and pc.get(pr, 0) != got:
                problems.append("priority_counts[%s]=%s != actual %d" % (pr, pc.get(pr), got))
        p0 = sorted(e["article_number"] for e in entries if e.get("review_priority") == "P0")
        p1 = sorted(e["article_number"] for e in entries if e.get("review_priority") == "P1")
        if sorted(q.get("p0_articles", [])) != p0:
            problems.append("p0_articles list != detailed P0 entries")
        if sorted(q.get("p1_articles", [])) != p1:
            problems.append("p1_articles list != detailed P1 entries")
        bc = q.get("bucket_counts", {})
        for b in BUCKETS:
            got = sum(1 for e in entries if e.get("review_bucket") == b)
            if got and bc.get(b, 0) != got:
                problems.append("bucket_counts[%s]=%s != actual %d" % (b, bc.get(b), got))

    # CSV row count matches (281 + header)
    if os.path.exists(QCSV):
        with open(QCSV, encoding="utf-8", newline="") as fh:
            rows = list(csv.reader(fh))
        if len(rows) != TARGET + 1:
            problems.append("CSV must have 281 data rows + header (got %d lines)" % len(rows))

    # candidate untouched / un-promoted
    if os.path.exists(CAND):
        cand = _read(CAND)
        arts = cand.get("articles", [])
        if len(arts) != TARGET:
            problems.append("candidate must still have 281 records")
        if cand.get("verification_status") != "ingested_unverified":
            problems.append("candidate verification_status must remain ingested_unverified")
        if cand.get("article_by_article_verified") is not False:
            problems.append("candidate article_by_article_verified must remain false")
        for a in arts:
            if a.get("verification_status") == "verified_against_official_gazette":
                problems.append("candidate art %s marked verified" % a.get("article_number"))
    else:
        problems.append("candidate file missing")

    # derived layers unchanged in shape
    en = glob.glob(os.path.join(ROOT, "data", "english_legal_llm", "*_en_legal_llm.json"))
    if len(en) != 8 or sum(len(_read(x)["records"]) for x in en) != 87:
        problems.append("English Legal LLM must remain 8 files / 87 records")
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    if len(zh) != 5 or sum(len(_read(x)["records"]) for x in zh) != 23:
        problems.append("Chinese Legal LLM must remain 5 files / 23 records")
    for x in glob.glob(os.path.join(ROOT, "data", "arabic_legal_llm", "*_ar_legal_llm.json")):
        b = open(x, encoding="utf-8").read().lower()
        if "official_text_ar" in b or "verified_against_official_gazette" in b:
            problems.append("Arabic Legal LLM must not be relabeled official: %s" % os.path.basename(x))
    ref = os.path.join(ROOT, "data", "english_reference")
    for fname, exp in (("book1_en_reference.json", list(range(1, 35))),
                       ("book2_en_reference.json", list(range(35, 51))),
                       ("book3_en_reference.json", list(range(51, 58)))):
        pth = os.path.join(ref, fname)
        if os.path.exists(pth) and [r["article_number"] for r in _read(pth)["records"]] != exp:
            problems.append("official English reference changed: %s" % fname)
    for fname in ("book1_articles_001_034.json", "book2_articles_035_050.json",
                  "book3_articles_051_057.json"):
        if not os.path.exists(os.path.join(ROOT, "data", "articles", fname)):
            problems.append("existing data/articles file missing: %s" % fname)
    if not os.path.exists(os.path.join(ROOT, "schemas", "official_arabic_article.schema.json")):
        problems.append("existing schema missing: official_arabic_article.schema.json")

    print("=" * 60)
    print("Official Arabic OCR MANUAL-REVIEW QUEUE validation")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] 281 queue entries (1..281); every entry bucketed + prioritised; "
          "verification_action_allowed=false; P0=%d P1=%d; candidate untouched "
          "(ingested_unverified, article_by_article_verified=false, nothing verified); "
          "derived layers unchanged."
          % (q["priority_counts"].get("P0", 0), q["priority_counts"].get("P1", 0)))
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
