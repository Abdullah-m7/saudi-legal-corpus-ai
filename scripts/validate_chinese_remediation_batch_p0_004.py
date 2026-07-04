#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate Chinese remediation Batch P0-004 (scoped internal Chinese draft, 20 articles, Babs 4/5/6).

Confirms the batch covers exactly the 20 authorized P0-004 articles with verbatim-hashed internal
Chinese text translated from the official Arabic governing text (English guidance only), that every
record's bab is in [4,5,6] and equals the official coverage-index expected_bab_number for that
article, carries the correct internal / non-official / non-binding / non-governing posture with
human review pending and qa_status pending_future_qa, and touches no protected layer (P0-001..P0-003
and their QA, plus the base corpora). Read-only and idempotent.

Usage: validate_chinese_remediation_batch_p0_004.py [DATA_JSON_PATH]
An optional data path (used by the tests to exercise rejection paths) overrides the default committed
batch file; all other checks read the real repository artifacts.

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DEFAULT = os.path.join(ROOT, "data", "chinese_remediation_batches", "p0_004",
                            "companies_law_m132_1443_zh_internal_remediation_p0_004.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_REMEDIATION_BATCH_P0_004_AR.md")
ARABIC = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
ENGLISH = os.path.join(ROOT, "data", "official_english_legal_llm",
                       "companies_law_m132_1443_official_english_legal_llm_001_281.json")
COV = os.path.join(ROOT, "reports", "chinese_translation_review",
                   "chinese_article_coverage_index_001_281.json")
CANDF = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                     "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")
CAND_SRC = os.path.join(ROOT, "data", "official_arabic",
                        "companies_law_m132_1443_official_arabic_user_provided.json")
P0_001 = os.path.join(ROOT, "data", "chinese_remediation_batches", "p0_001",
                      "companies_law_m132_1443_zh_internal_remediation_p0_001.json")
P0_002 = os.path.join(ROOT, "data", "chinese_remediation_batches", "p0_002",
                      "companies_law_m132_1443_zh_internal_remediation_p0_002.json")
P0_003 = os.path.join(ROOT, "data", "chinese_remediation_batches", "p0_003",
                      "companies_law_m132_1443_zh_internal_remediation_p0_003.json")
P0_002_QA = os.path.join(ROOT, "reports", "chinese_translation_review",
                         "chinese_remediation_batch_p0_002_qa.json")
P0_003_QA = os.path.join(ROOT, "reports", "chinese_translation_review",
                         "chinese_remediation_batch_p0_003_qa.json")

ARTS = [136, 137, 140, 141, 143, 144, 147, 148, 159, 160, 161, 163, 167, 168, 169, 171, 175, 177,
        179, 180]
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    data_path = argv[0] if argv else DATA_DEFAULT

    problems = []
    if not os.path.exists(data_path):
        problems.append("missing batch data file")
    if not os.path.exists(MD):
        problems.append("missing Arabic report")
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1

    try:
        d = _read(data_path)
    except (ValueError, OSError) as e:
        print("  - batch JSON is not valid JSON: %s" % e)
        print("RESULT: 1 problem(s) found ✗")
        return 1

    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    en = {r["article_number"]: r for r in _read(ENGLISH)["records"]}
    cov = {r["article_number"]: r for r in _read(COV)["records"]}

    # top-level posture / scope
    if d.get("stage") != "CHINESE_REMEDIATION_BATCH_P0_004":
        problems.append("stage must be CHINESE_REMEDIATION_BATCH_P0_004")
    if d.get("batch_id") != "P0-004":
        problems.append("batch_id must be P0-004")
    if d.get("priority") != "P0":
        problems.append("priority must be P0")
    if d.get("remediation_track") != "P0_no_isolable_text":
        problems.append("remediation_track must be P0_no_isolable_text")
    if d.get("governing_text_language") != "ar":
        problems.append("governing_text_language must be ar")
    if d.get("source_status_before") != "excluded_no_isolable_article_text":
        problems.append("source_status_before must be excluded_no_isolable_article_text")
    if d.get("remediation_action") != "create_new_internal_chinese_translation_from_arabic":
        problems.append("remediation_action must be create_new_internal_chinese_translation_from_arabic")
    if d.get("translation_basis") != "official_arabic_governing_text":
        problems.append("translation_basis must be official_arabic_governing_text")
    if d.get("english_guidance_role") != "secondary_guidance_only":
        problems.append("english_guidance_role must be secondary_guidance_only")
    if d.get("expected_babs") != [4, 5, 6]:
        problems.append("expected_babs must be [4, 5, 6]")
    if d.get("scope_articles") != ARTS:
        problems.append("scope_articles must exactly match the authorized P0-004 list")
    if d.get("article_count") != 20:
        problems.append("article_count must be 20")
    if d.get("internal_reference_only") is not True:
        problems.append("internal_reference_only must be true")
    for f in ("official_chinese_translation_claimed", "chinese_binding_claimed",
              "chinese_governing_claimed", "full_chinese_translation_claimed",
              "full_chinese_281_layer_created", "trilingual_alignment_created"):
        if d.get(f) is not False:
            problems.append("top-level %s must be false" % f)
    if d.get("human_legal_review_status") != "pending_human_legal_review":
        problems.append("human_legal_review_status must be pending_human_legal_review")
    if "final_status" not in d:
        problems.append("final_status must be present")
    if not isinstance(d.get("protected_layers_unchanged"), dict):
        problems.append("protected_layers_unchanged must be present")
    if not isinstance(d.get("prohibitions_respected"), dict):
        problems.append("prohibitions_respected must be present")

    recs = d.get("records", [])
    nums = [r.get("article_number") for r in recs]
    if nums != ARTS:
        problems.append("record article numbers must be exactly the P0-004 list, no extras")
    if len(set(nums)) != len(nums):
        problems.append("duplicate article numbers in records")
    allowed = set(ARTS)
    req_rec = ("article_number", "bab", "article_title_ar", "arabic_source_file",
               "arabic_source_hash_sha256", "english_guidance_file", "english_guidance_hash_sha256",
               "remediated_chinese_text", "remediated_chinese_text_hash_sha256",
               "internal_reference_only", "official_chinese_translation_claimed",
               "chinese_binding_claimed", "chinese_governing_claimed", "human_legal_review_status",
               "translation_basis", "english_guidance_role", "source_status_before",
               "remediation_action", "qa_status")
    for r in recs:
        n = r.get("article_number")
        if n not in allowed:
            problems.append("out-of-scope article %s present" % n)
            continue
        for f in req_rec:
            if f not in r:
                problems.append("art %s missing required field %s" % (n, f))
        if r.get("bab") not in (4, 5, 6):
            problems.append("art %s bab must be in [4,5,6]" % n)
        if n in cov and r.get("bab") != cov[n].get("expected_bab_number"):
            problems.append("art %s bab %r != coverage-index expected_bab_number %r"
                            % (n, r.get("bab"), cov[n].get("expected_bab_number")))
        if not (r.get("remediated_chinese_text") or "").strip():
            problems.append("art %s remediated_chinese_text empty" % n)
        if r.get("source_status_before") != "excluded_no_isolable_article_text":
            problems.append("art %s source_status_before wrong" % n)
        if r.get("remediation_action") != "create_new_internal_chinese_translation_from_arabic":
            problems.append("art %s remediation_action wrong" % n)
        if r.get("translation_basis") != "official_arabic_governing_text":
            problems.append("art %s translation_basis wrong" % n)
        if r.get("english_guidance_role") != "secondary_guidance_only":
            problems.append("art %s english_guidance_role wrong" % n)
        if r.get("internal_reference_only") is not True:
            problems.append("art %s internal_reference_only must be true" % n)
        for f in ("official_chinese_translation_claimed", "chinese_binding_claimed",
                  "chinese_governing_claimed"):
            if r.get(f) is not False:
                problems.append("art %s %s must be false" % (n, f))
        if r.get("human_legal_review_status") != "pending_human_legal_review":
            problems.append("art %s human_legal_review_status must be pending" % n)
        if r.get("qa_status") != "pending_future_qa":
            problems.append("art %s qa_status must be pending_future_qa" % n)
        if r.get("remediated_chinese_text_hash_sha256") != _sha(r.get("remediated_chinese_text", "")):
            problems.append("art %s remediated_chinese_text_hash_sha256 mismatch" % n)
        if n in ar and r.get("arabic_source_hash_sha256") != ar[n]["official_text_hash_sha256"]:
            problems.append("art %s arabic_source_hash_sha256 != Arabic LLM record hash" % n)
        if n in en and r.get("english_guidance_hash_sha256") != en[n]["legal_rule_text_hash_sha256"]:
            problems.append("art %s english_guidance_hash_sha256 != English LLM record hash" % n)

    # no full Arabic/English text duplicated; no banned overclaim
    blob = json.dumps(d, ensure_ascii=False)
    for n in ARTS:
        if n in ar and ar[n]["official_text_ar"] in blob:
            problems.append("full Arabic text of art %s must not be embedded" % n)
            break
    for n in ARTS:
        if n in en and en[n]["legal_rule_text_en"] in blob:
            problems.append("full English text of art %s must not be embedded" % n)
            break
    low = blob.lower()
    for term in BANNED:
        if term in low:
            problems.append("banned overclaim term present: %r" % term)

    # sibling batches / QA unchanged (record counts + posture)
    for path, label in ((P0_001, "P0-001"), (P0_002, "P0-002"), (P0_003, "P0-003")):
        if not os.path.exists(path) or len(_read(path)["records"]) != 20:
            problems.append("%s batch must remain 20 records (untouched)" % label)
        elif _read(path).get("human_legal_review_status") != "pending_human_legal_review":
            problems.append("%s posture changed (forbidden)" % label)
    for path, label in ((P0_002_QA, "P0-002 QA"), (P0_003_QA, "P0-003 QA")):
        if not os.path.exists(path):
            problems.append("%s must exist and remain unchanged" % label)
        else:
            qa = _read(path)
            if qa.get("final_status") != "QA_PASS":
                problems.append("%s posture changed (forbidden)" % label)

    # protected base layers unchanged
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

    # no post-P0 (P1/P2/P3) batch files created (P0-005 is now an authorized sibling batch)
    later = glob.glob(os.path.join(ROOT, "data", "chinese_remediation_batches", "p[123]_*"))
    if later:
        problems.append("post-P0 batch dirs (P1/P2/P3) must not exist: %s"
                        % sorted(os.path.basename(x) for x in later))

    print("=" * 60)
    print("Chinese remediation Batch P0-004 validation")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] Batch P0-004: 20 authorized articles across Babs [4,5,6] (each record bab matches "
          "the coverage index); verbatim-hashed internal Chinese from the official Arabic (English "
          "guidance only); internal/non-official/non-binding/non-governing; human review pending; "
          "qa_status pending_future_qa; no full Arabic/English text embedded; P0-001..P0-003 + their "
          "QA + Chinese candidate 189 + old Chinese 5/23 + Arabic 281 + English 281 + English "
          "reference 281 + Arabic source + Chinese sources 14 + OCR queue unchanged; no P0-005 files.")
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
