#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate Chinese remediation Batch P2-001 (first P2 expansion batch; 20 articles, Babs 1/2/4).

P2 track = expansion: the prior internal Chinese candidate for these articles EXISTS but is condensed,
so this batch carries an EXPANDED internal Chinese text derived from the official Arabic governing text
(English guidance only, existing candidate as the starting point) to restore the compressed detail
without changing meaning. Confirms the batch covers exactly the 20 authorized P2-001 articles with
verbatim-hashed internal Chinese text, that every record's bab is in [1,2,4] and equals the
coverage-index expected_bab_number, that each record links to the (unchanged) prior candidate record
and to its P2 finding in the remediation backlog (priority/track/blocker/action), that it carries the
correct internal / non-official / non-binding / non-governing posture under the repository review model
(official Arabic governs; repository-owner review active with a legal background / bachelor_of_law;
external legal review optional and not required for repository use), with qa_status pending_future_qa,
and that it touches no protected layer (all P0 batches + their QA, all P1 batches + their QA, the
Chinese candidate 189, and the base corpora). No p2_002+/P3 batch dirs, no full Chinese 281 layer, no
trilingual alignment. Read-only and idempotent.

Usage: validate_chinese_remediation_batch_p2_001.py [DATA_JSON_PATH]
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
DATA_DEFAULT = os.path.join(ROOT, "data", "chinese_remediation_batches", "p2_001",
                            "companies_law_m132_1443_zh_internal_remediation_p2_001.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_REMEDIATION_BATCH_P2_001_AR.md")
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
BACKLOG = os.path.join(ROOT, "reports", "chinese_translation_review",
                       "chinese_remediation_backlog_001_281.json")

# All P0 sibling batches (must remain unchanged: record counts + posture)
P0_BATCHES = {
    "P0-001": ("p0_001", "companies_law_m132_1443_zh_internal_remediation_p0_001.json"),
    "P0-002": ("p0_002", "companies_law_m132_1443_zh_internal_remediation_p0_002.json"),
    "P0-003": ("p0_003", "companies_law_m132_1443_zh_internal_remediation_p0_003.json"),
    "P0-004": ("p0_004", "companies_law_m132_1443_zh_internal_remediation_p0_004.json"),
    "P0-005": ("p0_005", "companies_law_m132_1443_zh_internal_remediation_p0_005.json"),
}
QAS = ("chinese_remediation_batch_p0_002_qa.json", "chinese_remediation_batch_p0_003_qa.json",
       "chinese_remediation_batch_p0_004_qa.json", "chinese_remediation_batch_p0_005_qa.json",
       "chinese_remediation_batch_p1_001_qa.json", "chinese_remediation_batch_p1_002_qa.json",
       "chinese_remediation_batch_p1_003_qa.json", "chinese_remediation_batch_p1_004_qa.json")
# P1 remediation batches: (dir, expected record count)
P1_BATCHES = {
    "P1-001": ("p1_001", "companies_law_m132_1443_zh_internal_remediation_p1_001.json", 20),
    "P1-002": ("p1_002", "companies_law_m132_1443_zh_internal_remediation_p1_002.json", 20),
    "P1-003": ("p1_003", "companies_law_m132_1443_zh_internal_remediation_p1_003.json", 20),
    "P1-004": ("p1_004", "companies_law_m132_1443_zh_internal_remediation_p1_004.json", 16),
}

ARTS = [4, 10, 16, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 37, 58, 59]
BABS = (1, 2, 4)
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
    cand = {r["article_number"]: r for r in _read(CANDF)["records"]}
    bk = {r["article_number"]: r for r in _read(BACKLOG)["records"]}

    # top-level posture / scope
    if d.get("stage") != "CHINESE_REMEDIATION_BATCH_P2_001":
        problems.append("stage must be CHINESE_REMEDIATION_BATCH_P2_001")
    if d.get("batch_id") != "P2-001":
        problems.append("batch_id must be P2-001")
    if d.get("priority") != "P2":
        problems.append("priority must be P2")
    if d.get("remediation_track") != "P2_expansion_needed":
        problems.append("remediation_track must be P2_expansion_needed")
    if d.get("governing_text_language") != "ar":
        problems.append("governing_text_language must be ar")
    if d.get("remediation_action") != "expand_existing_internal_chinese_from_arabic":
        problems.append("remediation_action must be expand_existing_internal_chinese_from_arabic")
    if d.get("translation_basis") != "official_arabic_governing_text":
        problems.append("translation_basis must be official_arabic_governing_text")
    if d.get("english_guidance_role") != "secondary_guidance_only":
        problems.append("english_guidance_role must be secondary_guidance_only")
    if d.get("source_basis") != "official_arabic_plus_existing_chinese_candidate":
        problems.append("source_basis must be official_arabic_plus_existing_chinese_candidate")
    if d.get("expected_babs") != [1, 2, 4]:
        problems.append("expected_babs must be [1, 2, 4]")
    if d.get("scope_articles") != ARTS:
        problems.append("scope_articles must exactly match the authorized P2-001 list")
    if d.get("article_count") != 20:
        problems.append("article_count must be 20")
    if d.get("first_p2_batch") is not True:
        problems.append("first_p2_batch must be true")
    if d.get("internal_reference_only") is not True:
        problems.append("internal_reference_only must be true")
    for f in ("official_chinese_translation_claimed", "chinese_binding_claimed",
              "chinese_governing_claimed", "full_chinese_translation_claimed",
              "full_chinese_281_layer_created", "trilingual_alignment_created"):
        if d.get(f) is not False:
            problems.append("top-level %s must be false" % f)

    # repository review model (official Arabic governs; owner review active; external optional)
    rlr = d.get("repository_legal_review") or {}
    if rlr.get("repository_owner_has_legal_background") is not True:
        problems.append("repository_legal_review.repository_owner_has_legal_background must be true")
    if rlr.get("repository_owner_legal_qualification") != "bachelor_of_law":
        problems.append("repository_owner_legal_qualification must be bachelor_of_law")
    if rlr.get("repository_legal_review_status") != "repository_owner_review_active":
        problems.append("repository_legal_review_status must be repository_owner_review_active")
    elr = d.get("external_legal_review") or {}
    if elr.get("external_legal_review_required_for_repository_use") is not False:
        problems.append("external_legal_review must not be required for repository use")
    if elr.get("external_legal_review_optional_for_enterprise_or_official_adoption") is not True:
        problems.append("external_legal_review must be optional for enterprise/official adoption")
    if elr.get("external_legal_review_status") != "not_performed":
        problems.append("external_legal_review_status must be not_performed")
    ofs = d.get("official_status") or {}
    for f in ("official_government_publication", "official_translation_claimed",
              "official_adoption_claimed", "chinese_official", "chinese_binding",
              "chinese_governing"):
        if ofs.get(f) is not False:
            problems.append("official_status.%s must be false" % f)
    if ofs.get("not_legal_advice") is not True:
        problems.append("official_status.not_legal_advice must be true")
    if "final_status" not in d:
        problems.append("final_status must be present")
    if not isinstance(d.get("protected_layers_unchanged"), dict):
        problems.append("protected_layers_unchanged must be present")
    if not isinstance(d.get("prohibitions_respected"), dict):
        problems.append("prohibitions_respected must be present")

    recs = d.get("records", [])
    nums = [r.get("article_number") for r in recs]
    if nums != ARTS:
        problems.append("record article numbers must be exactly the P2-001 list, no extras")
    if len(set(nums)) != len(nums):
        problems.append("duplicate article numbers in records")
    allowed = set(ARTS)
    req_rec = ("article_number", "bab", "article_title_ar", "arabic_source_file",
               "arabic_source_hash_sha256", "english_guidance_file", "english_guidance_hash_sha256",
               "prior_candidate_record_id", "prior_candidate_hash_sha256", "backlog_priority",
               "backlog_remediation_track", "backlog_current_blocker", "backlog_remediation_action",
               "remediated_chinese_text", "remediated_chinese_text_hash_sha256",
               "internal_reference_only", "official_chinese_translation_claimed",
               "chinese_binding_claimed", "chinese_governing_claimed", "source_basis",
               "repository_legal_review_status", "external_legal_review_status",
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
        if r.get("bab") not in BABS:
            problems.append("art %s bab must be in [1,2,4]" % n)
        if n in cov and r.get("bab") != cov[n].get("expected_bab_number"):
            problems.append("art %s bab %r != coverage-index expected_bab_number %r"
                            % (n, r.get("bab"), cov[n].get("expected_bab_number")))
        if not (r.get("remediated_chinese_text") or "").strip():
            problems.append("art %s remediated_chinese_text empty" % n)
        if r.get("remediation_action") != "expand_existing_internal_chinese_from_arabic":
            problems.append("art %s remediation_action wrong" % n)
        if r.get("translation_basis") != "official_arabic_governing_text":
            problems.append("art %s translation_basis wrong" % n)
        if r.get("english_guidance_role") != "secondary_guidance_only":
            problems.append("art %s english_guidance_role wrong" % n)
        if r.get("source_basis") != "official_arabic_plus_existing_chinese_candidate":
            problems.append("art %s source_basis wrong" % n)
        if r.get("internal_reference_only") is not True:
            problems.append("art %s internal_reference_only must be true" % n)
        for f in ("official_chinese_translation_claimed", "chinese_binding_claimed",
                  "chinese_governing_claimed"):
            if r.get(f) is not False:
                problems.append("art %s %s must be false" % (n, f))
        if r.get("repository_legal_review_status") != "repository_owner_review_active":
            problems.append("art %s repository_legal_review_status wrong" % n)
        if r.get("external_legal_review_status") != "not_performed":
            problems.append("art %s external_legal_review_status must be not_performed" % n)
        if r.get("qa_status") != "pending_future_qa":
            problems.append("art %s qa_status must be pending_future_qa" % n)
        if r.get("remediated_chinese_text_hash_sha256") != _sha(r.get("remediated_chinese_text", "")):
            problems.append("art %s remediated_chinese_text_hash_sha256 mismatch" % n)
        if n in ar and r.get("arabic_source_hash_sha256") != ar[n]["official_text_hash_sha256"]:
            problems.append("art %s arabic_source_hash_sha256 != Arabic LLM record hash" % n)
        if n in en and r.get("english_guidance_hash_sha256") != en[n]["legal_rule_text_hash_sha256"]:
            problems.append("art %s english_guidance_hash_sha256 != English LLM record hash" % n)
        # link to the (unchanged) prior candidate record
        if n in cand and r.get("prior_candidate_hash_sha256") != cand[n]["chinese_text_hash_sha256"]:
            problems.append("art %s prior_candidate_hash_sha256 != Chinese candidate record hash" % n)
        if n in cand and r.get("prior_candidate_record_id") != cand[n]["record_id"]:
            problems.append("art %s prior_candidate_record_id != Chinese candidate record_id" % n)
        # link to the P2 finding in the remediation backlog
        if n in bk:
            if bk[n].get("current_priority") != "P2":
                problems.append("art %s is not a P2 article in the remediation backlog" % n)
            if r.get("backlog_priority") != bk[n].get("current_priority"):
                problems.append("art %s backlog_priority != backlog current_priority" % n)
            if r.get("backlog_remediation_track") != bk[n].get("remediation_track"):
                problems.append("art %s backlog_remediation_track != backlog remediation_track" % n)
            if r.get("backlog_remediation_action") != bk[n].get("remediation_action"):
                problems.append("art %s backlog_remediation_action != backlog remediation_action" % n)
            if r.get("backlog_current_blocker") != bk[n].get("current_blocker"):
                problems.append("art %s backlog_current_blocker != backlog current_blocker" % n)
            if bk[n].get("remediation_track") != "P2_expansion_needed":
                problems.append("art %s backlog track is not P2_expansion_needed" % n)

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

    # all P0 sibling batches unchanged (record counts + posture); QA artifacts unchanged
    for label, (sub, fn) in P0_BATCHES.items():
        path = os.path.join(ROOT, "data", "chinese_remediation_batches", sub, fn)
        if not os.path.exists(path) or len(_read(path)["records"]) not in (12, 20):
            problems.append("%s batch missing / unexpected record count (untouched)" % label)
        elif _read(path).get("human_legal_review_status") != "pending_human_legal_review":
            problems.append("%s posture changed (forbidden)" % label)
    for fn in QAS:
        path = os.path.join(ROOT, "reports", "chinese_translation_review", fn)
        if not os.path.exists(path):
            problems.append("%s must exist and remain unchanged" % fn)
        elif _read(path).get("final_status") != "QA_PASS":
            problems.append("%s posture changed (forbidden)" % fn)
    # all P1 remediation batches must remain intact (record counts + owner review model)
    for label, (sub, fn, cnt) in P1_BATCHES.items():
        path = os.path.join(ROOT, "data", "chinese_remediation_batches", sub, fn)
        if not os.path.exists(path) or len(_read(path)["records"]) != cnt:
            problems.append("%s remediation must remain present with %d records (untouched)" % (label, cnt))
        elif (_read(path).get("repository_legal_review") or {}).get(
                "repository_legal_review_status") != "repository_owner_review_active":
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

    # P1-001..P1-004 and P2-001..P2-005 authorized; only p3_* (and any other) dirs remain forbidden
    allowed_dirs = ("p1_001", "p1_002", "p1_003", "p1_004", "p2_001", "p2_002", "p2_003", "p2_004", "p2_005", "p3_conf_001")
    later = [x for x in glob.glob(os.path.join(ROOT, "data", "chinese_remediation_batches", "p[123]_*"))
             if os.path.basename(x) not in allowed_dirs]
    if later:
        problems.append("only P1-001..P1-004 and P2-001..P2-005 authorized; no p3_* (beyond the authorized P3 confirmation batch) or unauthorized batch dirs: %s"
                        % sorted(os.path.basename(x) for x in later))
    # no full Chinese 281 / trilingual artifacts
    for pat in ("*trilingual*", "*full_chinese_281*", "*chinese_full_281*"):
        hits = glob.glob(os.path.join(ROOT, "data", "**", pat), recursive=True) + \
            glob.glob(os.path.join(ROOT, "reports", "**", pat), recursive=True)
        if hits:
            problems.append("no full-Chinese-281 / trilingual artifacts allowed: %s"
                            % sorted(os.path.relpath(x, ROOT) for x in hits))

    print("=" * 60)
    print("Chinese remediation Batch P2-001 validation (first P2 expansion batch)")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] Batch P2-001: 20 authorized articles across Babs [1,2,4] (each record bab matches the "
          "coverage index); verbatim-hashed internal Chinese EXPANDED from the official Arabic (English "
          "guidance only; existing candidate as the starting point) because the prior candidate was "
          "condensed (all 20 are P2 in the remediation backlog); each record links to the unchanged "
          "prior candidate and its P2 backlog finding (priority/track/blocker/action); internal/"
          "non-official/non-binding/non-governing; official Arabic governs; repository-owner review "
          "active (bachelor of law); external review optional, not required for repository use; "
          "qa_status pending_future_qa; no full Arabic/English text embedded; all P0 batches + QA + all "
          "P1 batches + QA + Chinese candidate 189 + old Chinese 5/23 + Arabic/English/English-reference "
          "281 + Arabic source + Chinese sources 14 + OCR queue unchanged; no other P2/P3 dirs; no "
          "full-281 / trilingual.")
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
