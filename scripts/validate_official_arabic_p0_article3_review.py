#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the P0 Article 3 segmentation review (no OCR engine needed).

Confirms the focused P0 review exists and is non-destructive: Article 3, nothing verified or
promoted, candidate + derived layers + queue untouched.

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RPT_DIR = os.path.join(ROOT, "reports", "official_arabic_verification")
REVIEW = os.path.join(RPT_DIR, "p0_article3_segmentation_review.json")
REVIEW_MD = os.path.join(RPT_DIR, "P0_ARTICLE3_SEGMENTATION_REVIEW_AR.md")
QUEUE = os.path.join(RPT_DIR, "manual_review_queue.json")
CAND = os.path.join(ROOT, "data", "official_arabic",
                    "companies_law_m132_1443_official_arabic_user_provided.json")

TARGET = 281
CLASSES = {"segmentation_ocr_miss", "source_text_found_ocr_noisy", "source_text_not_found",
           "needs_manual_visual_review"}


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    problems = []

    if not os.path.exists(REVIEW):
        problems.append("missing: p0_article3_segmentation_review.json")
    if not os.path.exists(REVIEW_MD):
        problems.append("missing: P0_ARTICLE3_SEGMENTATION_REVIEW_AR.md")

    r = _read(REVIEW) if os.path.exists(REVIEW) else None
    if r is not None:
        if r.get("article_number") != 3:
            problems.append("review article_number must be 3")
        if r.get("article_title_ar") != "جنسية الشركة":
            problems.append("review article_title_ar must be جنسية الشركة")
        if r.get("p0_reason_before") != "missing_in_official_source":
            problems.append("p0_reason_before must be missing_in_official_source")
        if r.get("verification_action_allowed") is not False:
            problems.append("verification_action_allowed must be false")
        if r.get("candidate_text_changed") is not False:
            problems.append("candidate_text_changed must be false")
        if r.get("verification_status_changed") is not False:
            problems.append("verification_status_changed must be false")
        if r.get("article_by_article_verified") is not False:
            problems.append("article_by_article_verified must be false")
        if r.get("classification") not in CLASSES:
            problems.append("classification must be one of %s" % sorted(CLASSES))
        if not isinstance(r.get("source_location_found"), bool):
            problems.append("source_location_found must be a boolean")
        if r.get("source_location_found") and not r.get("source_part_file"):
            problems.append("source_location_found true but source_part_file missing")
        if "verified_against_official_gazette" in json.dumps(r, ensure_ascii=False):
            problems.append("review must not contain verified_against_official_gazette")

    # candidate untouched
    if os.path.exists(CAND):
        c = _read(CAND)
        arts = c.get("articles", [])
        if len(arts) != TARGET:
            problems.append("candidate must still have 281 records")
        if c.get("verification_status") != "ingested_unverified":
            problems.append("candidate verification_status must remain ingested_unverified")
        if c.get("article_by_article_verified") is not False:
            problems.append("candidate article_by_article_verified must remain false")
        for a in arts:
            if a.get("verification_status") == "verified_against_official_gazette":
                problems.append("candidate art %s marked verified" % a.get("article_number"))
        # Article 3 candidate text unchanged (matches the review's recorded candidate_text)
        a3 = next((a for a in arts if a.get("article_number") == 3), None)
        if a3 is not None and r is not None and a3.get("official_text_ar") != r.get("candidate_text"):
            problems.append("Article 3 candidate official_text_ar must match the review's candidate_text (unchanged)")
    else:
        problems.append("candidate file missing")

    # manual review queue still 281 entries
    if os.path.exists(QUEUE):
        q = _read(QUEUE)
        if len(q.get("entries", [])) != TARGET:
            problems.append("manual_review_queue must still have 281 entries")
    else:
        problems.append("manual_review_queue.json missing")

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
    print("Official Arabic P0 Article 3 segmentation review validation")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] Article 3 P0 review present; classification=%s; source_location_found=%s "
          "(part=%s, packet page %s); nothing verified/promoted; candidate + queue + derived "
          "layers unchanged."
          % (r.get("classification"), r.get("source_location_found"),
             os.path.basename(r.get("source_part_file") or ""),
             r.get("source_page_number_within_packet")))
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
