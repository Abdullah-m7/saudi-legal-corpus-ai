#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the Batch P0-001 minor fixes (Articles 61 and 74 only; terminology fixes).

Confirms exactly Articles 61 and 74 were fixed (per the minor-fixes JSON previous/new hashes), the
QA now reads 20 pass / 0 minor / 0 blocked / 0 failed, hashes are consistent, human review stays
pending, no full Arabic/English/Chinese text is duplicated, and no protected layer is touched.

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RV = os.path.join(ROOT, "reports", "chinese_translation_review")
BATCH = os.path.join(ROOT, "data", "chinese_remediation_batches", "p0_001",
                     "companies_law_m132_1443_zh_internal_remediation_p0_001.json")
QA = os.path.join(RV, "chinese_remediation_batch_p0_001_qa.json")
MF = os.path.join(RV, "chinese_remediation_batch_p0_001_minor_fixes.json")
MD = os.path.join(RV, "CHINESE_REMEDIATION_BATCH_P0_001_MINOR_FIXES_AR.md")
ARABIC = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
ENGLISH = os.path.join(ROOT, "data", "official_english_legal_llm",
                       "companies_law_m132_1443_official_english_legal_llm_001_281.json")
CANDF = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                     "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")
CAND_SRC = os.path.join(ROOT, "data", "official_arabic",
                        "companies_law_m132_1443_official_arabic_user_provided.json")

ARTS = [61, 62, 63, 64, 65, 67, 68, 69, 70, 73, 74, 76, 78, 79, 80, 81, 82, 83, 84, 85]
FIXED = [61, 74]
PASS_DECISION = "qa_pass_for_internal_reference_pending_human_review"
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
    for p, label in ((BATCH, "remediation data"), (QA, "QA JSON"), (MF, "minor-fixes JSON"),
                     (MD, "Arabic minor-fixes report")):
        if not os.path.exists(p):
            problems.append("missing: %s (%s)" % (label, os.path.relpath(p, ROOT)))
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1

    batch = _read(BATCH)
    qa = _read(QA)
    mf = _read(MF)
    b_by = {r["article_number"]: r for r in batch["records"]}
    q_by = {r["article_number"]: r for r in qa["records"]}
    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    en = {r["article_number"]: r for r in _read(ENGLISH)["records"]}

    # batch scope intact
    if len(batch["records"]) != 20:
        problems.append("source remediation file must still have 20 records")
    if [r["article_number"] for r in batch["records"]] != ARTS:
        problems.append("source article list must be exactly the P0-001 list")
    if batch.get("article_numbers") != ARTS:
        problems.append("batch article_numbers must be the P0-001 list")
    if batch.get("human_legal_review_status") != "pending_human_legal_review":
        problems.append("batch human_legal_review_status must remain pending")

    # minor-fixes JSON posture
    if mf.get("stage") != "CHINESE_REMEDIATION_BATCH_P0_001_MINOR_FIXES":
        problems.append("minor-fixes stage wrong")
    if mf.get("batch_id") != "P0-001":
        problems.append("minor-fixes batch_id must be P0-001")
    if mf.get("article_count") != 2 or mf.get("fixed_articles") != FIXED:
        problems.append("minor-fixes must fix exactly [61, 74]")
    for f in ("full_chinese_translation_claimed", "official_chinese_translation_claimed",
              "chinese_binding_claimed", "chinese_governing_claimed",
              "human_legal_review_completed", "full_chinese_281_layer_created",
              "trilingual_alignment_created"):
        if mf.get(f) is not False:
            problems.append("minor-fixes %s must be false" % f)

    # exactly 61 & 74 changed from baseline (evidenced by minor-fixes prev != new)
    mf_by = {r["article_number"]: r for r in mf.get("records", [])}
    if set(mf_by) != set(FIXED):
        problems.append("minor-fixes records must be exactly {61, 74}")
    for n in FIXED:
        r = mf_by.get(n, {})
        if r.get("previous_chinese_hash_sha256") == r.get("new_chinese_hash_sha256"):
            problems.append("art %s minor-fix previous/new hash must differ" % n)
        if r.get("new_chinese_hash_sha256") != b_by[n]["remediated_chinese_text_hash_sha256"]:
            problems.append("art %s minor-fix new hash != batch hash" % n)
        if r.get("qa_new_decision") != PASS_DECISION:
            problems.append("art %s qa_new_decision must be pass" % n)
        if r.get("arabic_source_hash_sha256") != ar[n]["official_text_hash_sha256"]:
            problems.append("art %s arabic hash must be unchanged" % n)
        if r.get("english_guidance_hash_sha256") != en[n]["legal_rule_text_hash_sha256"]:
            problems.append("art %s english hash must be unchanged" % n)

    # batch text hashes correct; 61/74 fixed, others match their (unchanged) QA hashes
    for n in ARTS:
        r = b_by[n]
        if r["remediated_chinese_text_hash_sha256"] != _sha(r["remediated_chinese_text"]):
            problems.append("art %s remediated_chinese_text_hash mismatch" % n)
        if r["arabic_source_hash_sha256"] != ar[n]["official_text_hash_sha256"]:
            problems.append("art %s arabic_source_hash changed (forbidden)" % n)
        if r["english_guidance_hash_sha256"] != en[n]["legal_rule_text_hash_sha256"]:
            problems.append("art %s english_guidance_hash changed (forbidden)" % n)
        # QA hash must equal batch hash for every article
        if q_by[n]["remediated_chinese_hash_sha256"] != r["remediated_chinese_text_hash_sha256"]:
            problems.append("art %s QA hash != batch hash" % n)
        if n not in FIXED and q_by[n]["remediated_chinese_hash_sha256"] != _sha(r["remediated_chinese_text"]):
            problems.append("art %s (out-of-fix) hash inconsistent" % n)

    # QA now 20/0/0/0 and 61/74 pass
    if len(qa["records"]) != 20:
        problems.append("QA must have 20 records")
    s = qa.get("qa_summary", {})
    if s.get("pass_count") != 20 or s.get("minor_fix_count") != 0 \
            or s.get("blocked_count") != 0 or s.get("failed_count") != 0:
        problems.append("QA summary must be 20 pass / 0 minor / 0 blocked / 0 failed")
    for n in FIXED:
        if q_by[n]["qa_decision"] != PASS_DECISION:
            problems.append("art %s QA decision must be pass" % n)
        if q_by[n]["terminology_rating"] != "pass":
            problems.append("art %s terminology_rating must be pass" % n)
    for f in ("human_legal_review_completed", "full_chinese_translation_claimed",
              "official_chinese_translation_claimed", "chinese_binding_claimed",
              "chinese_governing_claimed", "full_chinese_281_layer_created",
              "trilingual_alignment_created"):
        if qa.get(f) is not False:
            problems.append("QA %s must be false" % f)

    # no full Arabic/English/Chinese text duplicated in QA/minor-fixes; no banned overclaim
    for name, doc in (("QA", qa), ("minor-fixes", mf)):
        blob = json.dumps(doc, ensure_ascii=False)
        for n in ARTS:
            if ar[n]["official_text_ar"] in blob:
                problems.append("%s must not contain full Arabic text (art %s)" % (name, n))
                break
        for n in ARTS:
            if en[n]["legal_rule_text_en"] in blob:
                problems.append("%s must not contain full English text (art %s)" % (name, n))
                break
        for n in ARTS:
            if b_by[n]["remediated_chinese_text"] in blob:
                problems.append("%s must not contain full remediated Chinese text (art %s)" % (name, n))
                break
        low = blob.lower()
        for term in BANNED:
            if term in low:
                problems.append("%s: banned overclaim term %r" % (name, term))

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
    print("Chinese remediation Batch P0-001 minor-fixes validation")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] only Articles 61 and 74 fixed (terminology); batch still 20 (list/hashes "
          "consistent, Arabic/English hashes intact); QA 20 pass / 0 minor / 0 blocked / 0 failed; "
          "human review pending; no full Arabic/English/Chinese text duplicated; Chinese candidate "
          "189 + old Chinese 5/23 + Arabic 281 + English 281 + English reference 281 + Arabic "
          "source + Chinese sources 14 + OCR queue unchanged.")
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
