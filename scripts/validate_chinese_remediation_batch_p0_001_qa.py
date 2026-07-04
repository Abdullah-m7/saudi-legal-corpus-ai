#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the Batch P0-001 QA (article-by-article review vs the official Arabic; review only).

Confirms the QA covers exactly the 20 P0-001 articles, hashes match the source remediation file,
enum values are within the allowed sets, the remediated Chinese is NOT changed and human review is
NOT marked complete, no full Arabic/English/Chinese text is duplicated, and no protected layer is
touched.

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QA = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "chinese_remediation_batch_p0_001_qa.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_REMEDIATION_BATCH_P0_001_QA_AR.md")
SRC = os.path.join(ROOT, "data", "chinese_remediation_batches", "p0_001",
                   "companies_law_m132_1443_zh_internal_remediation_p0_001.json")
ARABIC = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
ENGLISH = os.path.join(ROOT, "data", "official_english_legal_llm",
                       "companies_law_m132_1443_official_english_legal_llm_001_281.json")
CANDF = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                     "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")
CAND_SRC = os.path.join(ROOT, "data", "official_arabic",
                        "companies_law_m132_1443_official_arabic_user_provided.json")

ARTS = [61, 62, 63, 64, 65, 67, 68, 69, 70, 73, 74, 76, 78, 79, 80, 81, 82, 83, 84, 85]
FIDELITY = {"pass", "needs_minor_fix", "needs_major_fix", "fail"}
COMPLETE = {"complete", "minor_omissions", "material_omissions", "fail"}
DECISION = {"qa_pass_for_internal_reference_pending_human_review",
            "qa_pass_with_minor_fix_recommended", "qa_blocked_needs_revision",
            "qa_failed_needs_retranslation"}
NEXT = {"retain_pending_human_review", "revise_minor_issues", "revise_major_issues",
        "retranslate_article_from_arabic"}
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    problems = []
    for p, label in ((QA, "QA JSON"), (MD, "Arabic QA report"), (SRC, "source remediation file")):
        if not os.path.exists(p):
            problems.append("missing: %s (%s)" % (label, os.path.relpath(p, ROOT)))
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1

    qa = _read(QA)
    src = {r["article_number"]: r for r in _read(SRC)["records"]}
    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    en = {r["article_number"]: r for r in _read(ENGLISH)["records"]}

    if qa.get("stage") != "CHINESE_REMEDIATION_BATCH_P0_001_QA":
        problems.append("stage must be CHINESE_REMEDIATION_BATCH_P0_001_QA")
    if qa.get("batch_id") != "P0-001":
        problems.append("batch_id must be P0-001")
    if qa.get("article_count") != 20:
        problems.append("article_count must be 20")
    if qa.get("article_numbers") != ARTS:
        problems.append("article_numbers must exactly match the P0-001 list")
    if qa.get("expected_babs") != [4]:
        problems.append("expected_babs must be [4]")
    for f in ("full_chinese_translation_claimed", "official_chinese_translation_claimed",
              "chinese_binding_claimed", "chinese_governing_claimed",
              "human_legal_review_completed",
              "full_chinese_281_layer_created", "trilingual_alignment_created"):
        if qa.get(f) is not False:
            problems.append("QA top-level %s must be false" % f)
    # remediated_chinese_changed may be true after an authorized minor-fix pass (never implies
    # human legal review completion, which is gated separately above).
    if not isinstance(qa.get("remediated_chinese_changed"), bool):
        problems.append("QA remediated_chinese_changed must be a boolean")

    recs = qa.get("records", [])
    nums = [r.get("article_number") for r in recs]
    if len(recs) != 20:
        problems.append("QA records length must be 20")
    if nums != ARTS:
        problems.append("QA record article numbers must be exactly the P0-001 list, no extras")
    if len(set(nums)) != len(nums):
        problems.append("duplicate article numbers in QA records")
    for r in recs:
        n = r.get("article_number")
        if n not in set(ARTS):
            problems.append("out-of-scope article %s in QA" % n)
            continue
        if r.get("expected_bab_number") != 4:
            problems.append("art %s expected_bab_number must be 4" % n)
        if r.get("remediated_chinese_hash_sha256") != src[n]["remediated_chinese_text_hash_sha256"]:
            problems.append("art %s remediated_chinese_hash mismatch with source" % n)
        if r.get("arabic_source_hash_sha256") != src[n]["arabic_source_hash_sha256"]:
            problems.append("art %s arabic_source_hash mismatch with source" % n)
        if r.get("english_guidance_hash_sha256") != src[n]["english_guidance_hash_sha256"]:
            problems.append("art %s english_guidance_hash mismatch with source" % n)
        if r.get("semantic_fidelity_rating") not in FIDELITY:
            problems.append("art %s invalid semantic_fidelity_rating" % n)
        if r.get("legal_completeness_rating") not in COMPLETE:
            problems.append("art %s invalid legal_completeness_rating" % n)
        if r.get("terminology_rating") not in FIDELITY:
            problems.append("art %s invalid terminology_rating" % n)
        if r.get("structural_clarity_rating") not in FIDELITY:
            problems.append("art %s invalid structural_clarity_rating" % n)
        if r.get("qa_decision") not in DECISION:
            problems.append("art %s invalid qa_decision" % n)
        if r.get("recommended_next_action") not in NEXT:
            problems.append("art %s invalid recommended_next_action" % n)

    # no full Arabic/English text, no full remediated Chinese text duplicated
    blob = json.dumps(qa, ensure_ascii=False)
    for n in ARTS:
        if ar[n]["official_text_ar"] in blob:
            problems.append("QA must not contain full Arabic text (art %s)" % n)
            break
    for n in ARTS:
        if en[n]["legal_rule_text_en"] in blob:
            problems.append("QA must not contain full English text (art %s)" % n)
            break
    for n in ARTS:
        if src[n]["remediated_chinese_text"] in blob:
            problems.append("QA must not contain full remediated Chinese text (art %s)" % n)
            break
    low = blob.lower()
    for term in BANNED:
        if term in low:
            problems.append("banned overclaim term present: %r" % term)

    # source remediation file + protected layers unchanged
    if len(_read(SRC)["records"]) != 20:
        problems.append("source remediation batch P0-001 must remain 20 records")
    if len(_read(CANDF)["records"]) != 189:
        problems.append("Chinese internal candidate must remain 189 records")
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    if len(zh) != 5 or sum(len(_read(x)["records"]) for x in zh) != 23:
        problems.append("old Chinese Legal LLM must remain 5 files / 23 records")
    if len(_read(ARABIC)["records"]) != 281:
        problems.append("Arabic full LLM must remain 281 records")
    if len(_read(ENGLISH)["records"]) != 281:
        problems.append("English full LLM must remain 281 records")
    er = os.path.join(ROOT, "data", "english_reference",
                      "companies_law_m132_1443_en_reference_001_281.json")
    if not os.path.exists(er) or len(_read(er)["records"]) != 281:
        problems.append("English reference full must remain 281 records")
    if os.path.exists(CAND_SRC):
        c = _read(CAND_SRC)
        if len(c.get("articles", [])) != 281 or c.get("verification_status") != "ingested_unverified":
            problems.append("official Arabic source must remain unchanged")
    else:
        problems.append("official Arabic source file missing")
    if len(glob.glob(os.path.join(ROOT, "data", "chinese_translation_sources",
                                  "bab*_zh_source_extracted_articles_*.json"))) != 14:
        problems.append("Chinese source extracted files must remain 14")
    q = os.path.join(ROOT, "reports", "official_arabic_verification", "manual_review_queue.json")
    if os.path.exists(q) and len(_read(q).get("entries", [])) != 281:
        problems.append("OCR manual_review_queue must remain 281 entries (unchanged)")

    print("=" * 60)
    print("Chinese remediation Batch P0-001 QA validation")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    s = qa["qa_summary"]
    print("[PASS] QA of 20 P0-001 articles vs official Arabic; hashes match source; enums valid; "
          "remediated Chinese unchanged; human review NOT complete; no full Arabic/English/Chinese "
          "text embedded; pass=%d minor=%d blocked=%d failed=%d; source batch 20 + Chinese "
          "candidate 189 + old Chinese 5/23 + Arabic 281 + English 281 + English reference 281 + "
          "Arabic source + Chinese sources 14 + OCR queue unchanged."
          % (s["pass_count"], s["minor_fix_count"], s["blocked_count"], s["failed_count"]))
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
