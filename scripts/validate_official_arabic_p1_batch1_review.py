#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the P1 low-similarity batch-1 review (triage only; no OCR engine needed).

Confirms the committed batch-1 review report selected the correct 10 lowest-similarity P1
articles, that every entry is triage-only (nothing verified / promoted / text-changed), and
that no protected layer was touched.

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RPT = os.path.join(ROOT, "reports", "official_arabic_verification")
QJSON = os.path.join(RPT, "manual_review_queue.json")
REVIEW = os.path.join(RPT, "p1_low_similarity_batch1_review.json")
REVIEW_MD = os.path.join(RPT, "P1_LOW_SIMILARITY_BATCH1_REVIEW_AR.md")
CAND = os.path.join(ROOT, "data", "official_arabic",
                    "companies_law_m132_1443_official_arabic_user_provided.json")

TARGET = 281
BATCH_ID = "P1_LOW_SIMILARITY_BATCH1"
BATCH_SIZE = 10
ALLOWED_CLASS = {
    "likely_ocr_noise", "segmentation_or_alignment_drift", "table_or_list_formatting_drift",
    "heading_or_ordinal_corruption", "possible_substantive_difference",
    "needs_manual_visual_review", "insufficient_ocr_evidence",
}


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _lowest_p1(queue):
    p1 = [e for e in queue["entries"] if e.get("review_priority") == "P1"]
    p1.sort(key=lambda e: (e["similarity"], e["article_number"]))
    return p1[:BATCH_SIZE]


def main() -> int:
    problems = []

    for p, label in ((REVIEW, "p1_low_similarity_batch1_review.json"),
                     (REVIEW_MD, "P1_LOW_SIMILARITY_BATCH1_REVIEW_AR.md")):
        if not os.path.exists(p):
            problems.append("missing: %s" % label)

    queue = _read(QJSON) if os.path.exists(QJSON) else None
    r = _read(REVIEW) if os.path.exists(REVIEW) else None

    if queue is not None:
        if len(queue.get("entries", [])) != TARGET:
            problems.append("manual_review_queue must still have 281 entries")
        if queue.get("unresolved_p0_count", None) != 0:
            problems.append("manual_review_queue unresolved_p0_count must remain 0")

    if r is not None and queue is not None:
        if r.get("batch_id") != BATCH_ID:
            problems.append("batch_id must be %s" % BATCH_ID)
        if r.get("batch_size") != BATCH_SIZE:
            problems.append("batch_size must be %d" % BATCH_SIZE)
        entries = r.get("entries", [])
        if len(entries) != BATCH_SIZE:
            problems.append("expected exactly %d entries (got %d)" % (BATCH_SIZE, len(entries)))

        expected = _lowest_p1(queue)
        expected_nums = [e["article_number"] for e in expected]
        selected = r.get("selected_articles", [])
        entry_nums = [e.get("article_number") for e in entries]
        if selected != expected_nums:
            problems.append("selected_articles %s != 10 lowest-similarity P1 %s"
                            % (selected, expected_nums))
        if entry_nums != expected_nums:
            problems.append("entries order %s != 10 lowest-similarity P1 %s"
                            % (entry_nums, expected_nums))

        # every selected entry was P1 in the queue before review
        qprio = {e["article_number"]: e["review_priority"] for e in queue["entries"]}
        qsim = {e["article_number"]: e["similarity"] for e in queue["entries"]}
        for e in entries:
            n = e.get("article_number")
            if qprio.get(n) != "P1":
                problems.append("Article %s was not P1 in the queue" % n)
            if e.get("queue_priority_before") != "P1":
                problems.append("Article %s queue_priority_before must be P1" % n)
            if e.get("queue_similarity") != qsim.get(n):
                problems.append("Article %s queue_similarity mismatch with queue" % n)
            if e.get("batch_review_classification") not in ALLOWED_CLASS:
                problems.append("Article %s classification invalid: %s"
                                % (n, e.get("batch_review_classification")))
            if e.get("review_confidence") not in ("high", "medium", "low"):
                problems.append("Article %s review_confidence invalid" % n)
            for flag, want in (("verification_action_allowed", False),
                               ("candidate_text_changed", False),
                               ("verification_status_changed", False),
                               ("article_by_article_verified", False)):
                if e.get(flag) is not want:
                    problems.append("Article %s %s must be %s" % (n, flag, want))

        if "verified_against_official_gazette" in json.dumps(entries, ensure_ascii=False):
            problems.append("no batch entry may claim verified_against_official_gazette")
        if r.get("article_by_article_verified") is not False:
            problems.append("review article_by_article_verified must be false")
        if r.get("promoted_to_verified") is not False:
            problems.append("review promoted_to_verified must be false")
        if r.get("candidate_text_changed") is not False:
            problems.append("review candidate_text_changed must be false")

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
        # candidate official_text_ar unchanged: every batch entry's candidate_text and hash
        # must still match the live candidate record.
        cand_by = {a["article_number"]: a for a in c.get("articles", [])}
        if r is not None:
            for e in r.get("entries", []):
                a = cand_by.get(e.get("article_number"))
                if a is not None and e.get("candidate_text") != a.get("official_text_ar"):
                    problems.append("Article %s candidate_text drifted from candidate file"
                                    % e.get("article_number"))
    else:
        problems.append("candidate file missing")

    # protected derived layers unchanged in shape
    en = glob.glob(os.path.join(ROOT, "data", "english_legal_llm", "*_en_legal_llm.json"))
    if len(en) != 8 or sum(len(_read(x)["records"]) for x in en) != 87:
        problems.append("English Legal LLM must remain 8 files / 87 records")
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    if len(zh) != 5 or sum(len(_read(x)["records"]) for x in zh) != 23:
        problems.append("Chinese Legal LLM must remain 5 files / 23 records")
    for x in glob.glob(os.path.join(ROOT, "data", "arabic_legal_llm", "*_ar_legal_llm.json")):
        b = open(x, encoding="utf-8").read().lower()
        if "official_text_ar" in b or "verified_against_official_gazette" in b:
            problems.append("Arabic Legal LLM must not be relabeled official: %s"
                            % os.path.basename(x))
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
    print("Official Arabic P1 low-similarity batch-1 review validation")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] batch %s: 10 lowest-similarity P1 articles %s reviewed (triage only); "
          "every entry P1-before, verification_action_allowed=false, nothing verified/"
          "promoted/text-changed; candidate untouched (281, ingested_unverified); derived "
          "layers unchanged." % (BATCH_ID, r.get("selected_articles") if r else None))
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
