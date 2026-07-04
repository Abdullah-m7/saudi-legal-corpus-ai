#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the Chinese internal semantic QA (189) + completion gap plan (281).

Confirms the QA reviews all 189 candidates, the gap plan covers all 281 articles with the 92
excluded kept blocked (no isolable Chinese text), enum values are within the allowed sets, no
Chinese is generated/corrected and no Arabic-/English-to-Chinese fields exist, the trust posture
holds (Chinese internal / non-official / non-binding; Arabic governing), and no protected layer is
touched.

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RV = os.path.join(ROOT, "reports", "chinese_translation_review")
QA = os.path.join(RV, "chinese_internal_llm_semantic_qa_189.json")
GAP = os.path.join(RV, "chinese_completion_gap_plan_001_281.json")
MD = os.path.join(RV, "CHINESE_INTERNAL_LLM_SEMANTIC_QA_AND_GAP_PLAN_AR.md")
CANDF = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                     "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")
CAND_SRC = os.path.join(ROOT, "data", "official_arabic",
                        "companies_law_m132_1443_official_arabic_user_provided.json")

TARGET = 281
CAND_N = 189
EXCL_N = 92
ALIGN = {"high", "medium", "low", "not_assessed"}
COMPLETE = {"near_full", "condensed", "materially_incomplete", "not_assessed"}
USE = {"usable_internal_reference_with_caution",
       "usable_for_retrieval_but_needs_expansion_before_full_layer",
       "not_safe_for_full_layer_needs_retranslation", "manual_review_required"}
ACTION = {"retain_as_internal_reference_candidate",
          "expand_from_arabic_before_full_chinese_layer",
          "retranslate_from_arabic_before_full_chinese_layer",
          "manual_legal_translation_review_required"}
PRIORITY = {"P0", "P1", "P2", "P3"}
CUR_STATUS = {"internal_candidate_exists", "excluded_no_isolable_article_text",
              "old_partial_llm_only", "no_full_chinese_layer"}
BLOCKER = {"none_for_internal_reference_only", "condensed_translation_needs_expansion",
           "incomplete_translation_needs_retranslation", "no_isolable_chinese_text",
           "manual_review_required"}
NEXT = {"retain_candidate_for_internal_reference", "expand_existing_chinese_from_arabic",
        "retranslate_from_arabic", "manually_segment_or_replace_source",
        "manual_review_before_alignment"}
SRC_NEXT = {"official_arabic_governing_text", "existing_chinese_internal_candidate",
            "chinese_source_pdf_summary_group", "manual_legal_translation_review"}
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")
FORBIDDEN_FIELDS = ("chinese_text", "corrected_chinese", "generated_chinese",
                    "arabic_to_chinese", "english_to_chinese", "official_text_ar",
                    "legal_rule_text_en")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _all_keys(obj, acc):
    if isinstance(obj, dict):
        for k, v in obj.items():
            acc.add(k)
            _all_keys(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            _all_keys(v, acc)


def main() -> int:
    problems = []
    for p, label in ((QA, "semantic QA JSON"), (GAP, "gap plan JSON"), (MD, "Arabic report")):
        if not os.path.exists(p):
            problems.append("missing: %s (%s)" % (label, os.path.relpath(p, ROOT)))
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1

    qa = _read(QA)
    gap = _read(GAP)
    cand = _read(CANDF)
    excluded = set(cand["excluded_articles"])
    incl = {r["article_number"] for r in cand["records"]}

    # QA top-level posture
    if qa.get("candidate_record_count") != CAND_N:
        problems.append("QA candidate_record_count must be 189")
    if qa.get("reviewed_record_count") != CAND_N or len(qa.get("records", [])) != CAND_N:
        problems.append("QA must have 189 records")
    if qa.get("excluded_article_count") != EXCL_N:
        problems.append("QA excluded_article_count must be 92")
    for f in ("full_chinese_translation_claimed", "official_chinese_translation_claimed",
              "chinese_binding_claimed", "chinese_governing_claimed", "corrected_chinese_created",
              "arabic_used_to_generate_chinese", "english_used_to_generate_chinese"):
        if qa.get(f) is not False:
            problems.append("QA %s must be false" % f)

    qa_nums = [r["article_number"] for r in qa["records"]]
    if set(qa_nums) != incl:
        problems.append("QA reviewed set != candidate included set")
    if len(set(qa_nums)) != len(qa_nums):
        problems.append("QA has duplicate article numbers")
    for r in qa["records"]:
        n = r["article_number"]
        if r["semantic_alignment_rating"] not in ALIGN:
            problems.append("art %s invalid semantic_alignment_rating" % n)
        if r["legal_completeness_rating"] not in COMPLETE:
            problems.append("art %s invalid legal_completeness_rating" % n)
        if r["qa_use_status"] not in USE:
            problems.append("art %s invalid qa_use_status" % n)
        if r["recommended_action"] not in ACTION:
            problems.append("art %s invalid recommended_action" % n)
        if r["priority"] not in PRIORITY:
            problems.append("art %s invalid priority" % n)

    # gap plan
    if len(gap.get("article_plan", [])) != TARGET:
        problems.append("gap plan must have 281 article entries")
    gnums = [r["article_number"] for r in gap["article_plan"]]
    if gnums != list(range(1, TARGET + 1)):
        problems.append("gap plan article numbers must be 1..281 in order")
    if len(set(gnums)) != len(gnums):
        problems.append("gap plan has duplicate article numbers")
    if incl & excluded:
        problems.append("candidate and excluded sets overlap")
    if incl | excluded != set(range(1, TARGET + 1)):
        problems.append("candidate + excluded must partition 1..281")
    for r in gap["article_plan"]:
        n = r["article_number"]
        if r["current_chinese_status"] not in CUR_STATUS:
            problems.append("art %s invalid current_chinese_status" % n)
        if r["full_layer_blocker"] not in BLOCKER:
            problems.append("art %s invalid full_layer_blocker" % n)
        if r["required_next_action"] not in NEXT:
            problems.append("art %s invalid required_next_action" % n)
        if r["priority"] not in PRIORITY:
            problems.append("art %s invalid priority" % n)
        if r["source_for_next_action"] not in SRC_NEXT:
            problems.append("art %s invalid source_for_next_action" % n)
        if n in excluded:
            if r["has_isolable_chinese_candidate"] is not False:
                problems.append("excluded art %s has_isolable_chinese_candidate must be false" % n)
            if r["current_chinese_status"] != "excluded_no_isolable_article_text":
                problems.append("excluded art %s current_chinese_status wrong" % n)
            if r["full_layer_blocker"] != "no_isolable_chinese_text":
                problems.append("excluded art %s full_layer_blocker wrong" % n)
            if r["required_next_action"] not in ("retranslate_from_arabic",
                                                 "manually_segment_or_replace_source"):
                problems.append("excluded art %s required_next_action wrong" % n)
            if r["source_for_next_action"] not in ("official_arabic_governing_text",
                                                   "chinese_source_pdf_summary_group"):
                problems.append("excluded art %s source_for_next_action wrong" % n)
            if r["priority"] not in ("P0", "P1"):
                problems.append("excluded art %s priority must be P0/P1" % n)
        else:
            if r["has_isolable_chinese_candidate"] is not True:
                problems.append("candidate art %s has_isolable_chinese_candidate must be true" % n)
            if r["current_chinese_status"] != "internal_candidate_exists":
                problems.append("candidate art %s current_chinese_status wrong" % n)

    # no banned overclaims; no forbidden generated/corrected/foreign fields
    blob = (json.dumps(qa, ensure_ascii=False) + json.dumps(gap, ensure_ascii=False)).lower()
    for term in BANNED:
        if term in blob:
            problems.append("banned overclaim term present: %r" % term)
    keys = set()
    _all_keys(qa, keys)
    _all_keys(gap, keys)
    for k in keys:
        if k in FORBIDDEN_FIELDS:
            problems.append("forbidden field present: %r" % k)

    # candidate data unchanged (189); protected layers unchanged
    if len(cand["records"]) != CAND_N:
        problems.append("Chinese internal candidate must remain 189 records")
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    if len(zh) != 5 or sum(len(_read(x)["records"]) for x in zh) != 23:
        problems.append("old Chinese Legal LLM must remain 5 files / 23 records")
    for rel, label in (("data/official_arabic_legal_llm/"
                        "companies_law_m132_1443_official_arabic_legal_llm_001_281.json", "Arabic full LLM"),
                       ("data/official_english_legal_llm/"
                        "companies_law_m132_1443_official_english_legal_llm_001_281.json", "English full LLM"),
                       ("data/english_reference/"
                        "companies_law_m132_1443_en_reference_001_281.json", "English reference full")):
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p) or len(_read(p)["records"]) != TARGET:
            problems.append("%s must remain 281 records" % label)
    if os.path.exists(CAND_SRC):
        c = _read(CAND_SRC)
        if len(c.get("articles", [])) != TARGET or c.get("verification_status") != "ingested_unverified":
            problems.append("official Arabic source must remain unchanged (281, ingested_unverified)")
    else:
        problems.append("official Arabic source file missing")
    # Chinese source extracted files present (14)
    exn = len(glob.glob(os.path.join(ROOT, "data", "chinese_translation_sources",
                                     "bab*_zh_source_extracted_articles_*.json")))
    if exn != 14:
        problems.append("Chinese source extracted files must remain 14 (got %d)" % exn)
    q = os.path.join(ROOT, "reports", "official_arabic_verification", "manual_review_queue.json")
    if os.path.exists(q) and len(_read(q).get("entries", [])) != TARGET:
        problems.append("OCR manual_review_queue must remain 281 entries (unchanged)")

    print("=" * 60)
    print("Chinese internal semantic QA (189) + gap plan (281) validation")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] QA reviews all 189 candidates; gap plan covers 281 (92 excluded kept blocked "
          "no_isolable_chinese_text); enums valid; no generated/corrected Chinese, no Arabic-/"
          "English-to-Chinese fields; Chinese internal/non-official/non-binding, Arabic governing; "
          "candidate 189 + old Chinese 5/23 + Arabic 281 + English 281 + English reference 281 + "
          "Arabic source + Chinese sources 14 + OCR queue all unchanged.")
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
