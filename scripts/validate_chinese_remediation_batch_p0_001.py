#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate Chinese remediation Batch P0-001 (scoped internal Chinese draft, 20 Bab 4 articles).

Confirms the batch covers exactly the 20 authorized P0-001 articles with verbatim-hashed internal
Chinese text translated from the official Arabic governing text (English guidance only), carries
the correct internal / non-official / non-binding / non-governing posture with human review
pending, duplicates no full Arabic/English text, and touches no protected layer.

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "chinese_remediation_batches", "p0_001",
                    "companies_law_m132_1443_zh_internal_remediation_p0_001.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_REMEDIATION_BATCH_P0_001_AR.md")
ARABIC = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
ENGLISH = os.path.join(ROOT, "data", "official_english_legal_llm",
                       "companies_law_m132_1443_official_english_legal_llm_001_281.json")
CANDF = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                     "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")
CAND_SRC = os.path.join(ROOT, "data", "official_arabic",
                        "companies_law_m132_1443_official_arabic_user_provided.json")

ARTS = [61, 62, 63, 64, 65, 67, 68, 69, 70, 73, 74, 76, 78, 79, 80, 81, 82, 83, 84, 85]
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def main() -> int:
    problems = []
    if not os.path.exists(DATA):
        problems.append("missing batch data file")
    if not os.path.exists(MD):
        problems.append("missing Arabic report")
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1

    d = _read(DATA)
    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    en = {r["article_number"]: r for r in _read(ENGLISH)["records"]}

    # top-level posture / scope
    if d.get("stage") != "CHINESE_REMEDIATION_BATCH_P0_001":
        problems.append("stage must be CHINESE_REMEDIATION_BATCH_P0_001")
    if d.get("batch_id") != "P0-001":
        problems.append("batch_id must be P0-001")
    if d.get("priority") != "P0" or d.get("remediation_track") != "P0_no_isolable_text":
        problems.append("priority/remediation_track must be P0 / P0_no_isolable_text")
    if d.get("language") != "zh" or d.get("governing_text_language") != "ar":
        problems.append("language must be zh, governing_text_language ar")
    if d.get("article_count") != 20:
        problems.append("article_count must be 20")
    if d.get("article_numbers") != ARTS:
        problems.append("article_numbers must exactly match the authorized P0-001 list")
    if d.get("expected_babs") != [4]:
        problems.append("expected_babs must be [4]")
    for f in ("official_chinese_translation_claimed", "chinese_binding_claimed",
              "chinese_governing_claimed", "full_chinese_translation_claimed"):
        if d.get(f) is not False:
            problems.append("top-level %s must be false" % f)
    if d.get("batch_scope_only") is not True:
        problems.append("batch_scope_only must be true")
    if d.get("human_legal_review_status") != "pending_human_legal_review":
        problems.append("human_legal_review_status must be pending_human_legal_review")

    recs = d.get("records", [])
    nums = [r.get("article_number") for r in recs]
    if nums != ARTS:
        problems.append("record article numbers must be exactly the P0-001 list, no extras")
    if len(set(nums)) != len(nums):
        problems.append("duplicate article numbers in records")
    allowed = set(ARTS)
    for r in recs:
        n = r.get("article_number")
        if n not in allowed:
            problems.append("out-of-scope article %s present" % n)
            continue
        if not (r.get("remediated_chinese_text") or "").strip():
            problems.append("art %s remediated_chinese_text empty" % n)
        if r.get("expected_bab_number") != 4:
            problems.append("art %s expected_bab_number must be 4" % n)
        if r.get("source_status_before_remediation") != "excluded_no_isolable_article_text":
            problems.append("art %s source_status_before_remediation wrong" % n)
        if r.get("remediation_action") != "create_new_internal_chinese_translation_from_arabic":
            problems.append("art %s remediation_action wrong" % n)
        if r.get("translation_basis") != "official_arabic_governing_text":
            problems.append("art %s translation_basis must be official_arabic_governing_text" % n)
        if r.get("english_guidance_role") != "secondary_guidance_only":
            problems.append("art %s english_guidance_role must be secondary_guidance_only" % n)
        for k, want in (("official_translation", False), ("not_binding", True),
                        ("not_governing", True), ("internal_reference_only", True),
                        ("full_translation_claimed", False)):
            if r.get(k) is not want:
                problems.append("art %s %s must be %r" % (n, k, want))
        if r.get("human_legal_review_status") != "pending_human_legal_review":
            problems.append("art %s human_legal_review_status must be pending" % n)
        if r.get("remediated_chinese_text_hash_sha256") != _sha(r.get("remediated_chinese_text", "")):
            problems.append("art %s remediated_chinese_text_hash_sha256 mismatch" % n)
        if n in ar and r.get("arabic_source_hash_sha256") != ar[n]["official_text_hash_sha256"]:
            problems.append("art %s arabic_source_hash_sha256 != Arabic LLM record hash" % n)
        if n in en and r.get("english_guidance_hash_sha256") != en[n]["legal_rule_text_hash_sha256"]:
            problems.append("art %s english_guidance_hash_sha256 != English LLM record hash" % n)

    # no full Arabic/English text duplicated; no banned overclaim
    blob = json.dumps(d, ensure_ascii=False)
    for n in ARTS:
        if ar[n]["official_text_ar"] in blob:
            problems.append("full Arabic text of art %s must not be embedded" % n)
            break
    for n in ARTS:
        if en[n]["legal_rule_text_en"] in blob:
            problems.append("full English text of art %s must not be embedded" % n)
            break
    low = blob.lower()
    for term in BANNED:
        if term in low:
            problems.append("banned overclaim term present: %r" % term)

    # protected layers unchanged
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
    print("Chinese remediation Batch P0-001 validation")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] Batch P0-001: 20 authorized Bab-4 articles; verbatim-hashed internal Chinese "
          "from the official Arabic (English guidance only); internal/non-official/non-binding/"
          "non-governing; human_legal_review pending; no full Arabic/English text embedded; no "
          "out-of-scope articles; Chinese candidate 189 + old Chinese 5/23 + Arabic 281 + English "
          "281 + English reference 281 + Arabic source + Chinese sources 14 + OCR queue unchanged.")
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
