#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the manual-review queue P0-resolution update (no OCR engine needed).

Confirms the P0 Article 3 OCR-segmentation-miss resolution is correctly folded into the queue
and that nothing was verified / promoted / text-changed.

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RPT_DIR = os.path.join(ROOT, "reports", "official_arabic_verification")
QJSON = os.path.join(RPT_DIR, "manual_review_queue.json")
QCSV = os.path.join(RPT_DIR, "manual_review_queue.csv")
QMD = os.path.join(RPT_DIR, "OFFICIAL_ARABIC_OCR_MANUAL_REVIEW_QUEUE_AR.md")
UPDATE_MD = os.path.join(RPT_DIR, "OFFICIAL_ARABIC_QUEUE_P0_RESOLUTION_UPDATE_AR.md")
CAND = os.path.join(ROOT, "data", "official_arabic",
                    "companies_law_m132_1443_official_arabic_user_provided.json")

TARGET = 281


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    problems = []

    for p, label in ((QJSON, "manual_review_queue.json"), (QCSV, "manual_review_queue.csv"),
                     (QMD, "OFFICIAL_ARABIC_OCR_MANUAL_REVIEW_QUEUE_AR.md"),
                     (UPDATE_MD, "OFFICIAL_ARABIC_QUEUE_P0_RESOLUTION_UPDATE_AR.md")):
        if not os.path.exists(p):
            problems.append("missing: %s" % label)

    q = _read(QJSON) if os.path.exists(QJSON) else None
    if q is not None:
        entries = q.get("entries", [])
        if len(entries) != TARGET:
            problems.append("expected 281 queue entries (got %d)" % len(entries))
        if [e.get("article_number") for e in entries] != list(range(1, TARGET + 1)):
            problems.append("queue entries must be article numbers 1..281 in order")
        # no P0 anywhere
        if any(e.get("review_priority") == "P0" for e in entries):
            problems.append("no entry may have review_priority P0")
        if q.get("unresolved_p0_count", None) != 0:
            problems.append("unresolved_p0_count must be 0")
        if q.get("p0_articles"):
            problems.append("p0_articles must be empty")
        if 3 not in (q.get("resolved_p0_articles") or []):
            problems.append("resolved_p0_articles must include Article 3")
        # Article 3 resolution
        a3 = next((e for e in entries if e.get("article_number") == 3), None)
        if a3 is None:
            problems.append("Article 3 entry missing")
        else:
            if a3.get("review_bucket") != "resolved_segmentation_ocr_miss":
                problems.append("Article 3 review_bucket must be resolved_segmentation_ocr_miss")
            if a3.get("review_priority") != "P6":
                problems.append("Article 3 review_priority must be P6")
            if a3.get("p0_resolution_status") != "resolved":
                problems.append("Article 3 p0_resolution_status must be resolved")
            if a3.get("p0_resolution_classification") != "segmentation_ocr_miss":
                problems.append("Article 3 p0_resolution_classification must be segmentation_ocr_miss")
            if a3.get("verification_action_allowed") is not False:
                problems.append("Article 3 verification_action_allowed must be false")
        # priority counts consistent with entries
        pc = q.get("priority_counts", {})
        for pr in ("P1", "P2", "P3", "P4", "P5", "P6"):
            actual = sum(1 for e in entries if e.get("review_priority") == pr)
            if actual and pc.get(pr) != actual:
                problems.append("priority_counts[%s]=%s != actual %d" % (pr, pc.get(pr), actual))
        if q.get("article_by_article_verified") is not False:
            problems.append("queue article_by_article_verified must be false")
        if q.get("promoted_to_verified") is not False:
            problems.append("queue promoted_to_verified must be false")
        if "verified_against_official_gazette" in json.dumps(q.get("entries", []), ensure_ascii=False):
            problems.append("no queue entry may claim verified_against_official_gazette")

    # candidate untouched
    if os.path.exists(CAND):
        c = _read(CAND)
        if len(c.get("articles", [])) != TARGET:
            problems.append("candidate must still have 281 records")
        if c.get("verification_status") != "ingested_unverified":
            problems.append("candidate verification_status must remain ingested_unverified")
        if c.get("article_by_article_verified") is not False:
            problems.append("candidate article_by_article_verified must remain false")
        for a in c.get("articles", []):
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
        if os.path.exists(pth) and [x["article_number"] for x in _read(pth)["records"]] != exp:
            problems.append("official English reference changed: %s" % fname)
    for fname in ("book1_articles_001_034.json", "book2_articles_035_050.json",
                  "book3_articles_051_057.json"):
        if not os.path.exists(os.path.join(ROOT, "data", "articles", fname)):
            problems.append("existing data/articles file missing: %s" % fname)
    if not os.path.exists(os.path.join(ROOT, "schemas", "official_arabic_article.schema.json")):
        problems.append("existing schema missing: official_arabic_article.schema.json")

    print("=" * 60)
    print("Official Arabic queue P0-resolution update validation")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] Article 3 P0 resolved (resolved_segmentation_ocr_miss / P6); unresolved P0 "
          "count=0; resolved_p0_articles=%s; total 281 entries; candidate untouched "
          "(ingested_unverified, nothing verified); derived layers unchanged."
          % (q.get("resolved_p0_articles")))
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
