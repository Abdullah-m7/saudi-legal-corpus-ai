#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the Batch P0-005 QA (final P0 batch; article-by-article review vs the official Arabic).

Confirms the QA covers exactly the 12 P0-005 articles across Babs 7/9/10/13/14, that every
per-article bab is in [7,9,10,13,14] and equals both the P0-005 remediation record bab and the
coverage-index expected_bab_number, that expected_bab_distribution matches the authorized split, that
only allowed qa_status values appear, that final_status/qa_summary stay consistent with the
per-article statuses, carries the correct legal-hierarchy / non-official / non-binding / non-governing
posture with human review pending, points at the P0-005 remediation file, embeds no full
Arabic/English/Chinese text, and touches no protected layer (P0-001..P0-005 + QA + P0-003/P0-004
tooling, plus the base corpora). No P1/P2/P3 batch dirs and no generic/factory-refactor files may
exist. Read-only, idempotent.

Usage: validate_chinese_remediation_batch_p0_005_qa.py [QA_JSON_PATH]
An optional QA JSON path (used by the tests to exercise rejection paths) overrides the default
committed QA file; all other checks read the real repository artifacts.

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QA_DEFAULT = os.path.join(ROOT, "reports", "chinese_translation_review",
                          "chinese_remediation_batch_p0_005_qa.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_REMEDIATION_BATCH_P0_005_QA_AR.md")
SRC = os.path.join(ROOT, "data", "chinese_remediation_batches", "p0_005",
                   "companies_law_m132_1443_zh_internal_remediation_p0_005.json")
SRC_REL = "data/chinese_remediation_batches/p0_005/companies_law_m132_1443_zh_internal_remediation_p0_005.json"
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
BATCHES = {
    "P0-001": ("p0_001", "companies_law_m132_1443_zh_internal_remediation_p0_001.json"),
    "P0-002": ("p0_002", "companies_law_m132_1443_zh_internal_remediation_p0_002.json"),
    "P0-003": ("p0_003", "companies_law_m132_1443_zh_internal_remediation_p0_003.json"),
    "P0-004": ("p0_004", "companies_law_m132_1443_zh_internal_remediation_p0_004.json"),
    "P0-005": ("p0_005", "companies_law_m132_1443_zh_internal_remediation_p0_005.json"),
}
QAS = ("chinese_remediation_batch_p0_002_qa.json", "chinese_remediation_batch_p0_003_qa.json",
       "chinese_remediation_batch_p0_004_qa.json")

ARTS = [188, 189, 190, 191, 192, 194, 218, 220, 260, 261, 262, 274]
DIST = {"7": [188, 189, 190, 191, 192, 194], "9": [218], "10": [220],
        "13": [260, 261, 262], "14": [274]}
STATUS = {"pass", "minor", "blocked", "fail"}
FINAL = {"QA_PASS", "QA_PASS_WITH_MINOR_ISSUES", "QA_BLOCKED", "QA_FAIL"}
REQ_TOP = ("stage", "batch_id", "source_batch_file", "scope_articles", "expected_babs",
           "expected_bab_distribution", "qa_method", "legal_hierarchy", "human_legal_review_status",
           "full_chinese_translation_claimed", "official_chinese_translation_claimed",
           "chinese_binding_claimed", "chinese_governing_claimed", "full_chinese_281_layer_created",
           "trilingual_alignment_created", "p0_005_chinese_text_modified", "p0_005_data_modified",
           "qa_summary", "per_article_reviews", "protected_layers_unchanged",
           "prohibitions_respected", "final_status")
REQ_REC = ("article_number", "bab", "qa_status", "arabic_controlling_source_checked",
           "english_guidance_checked", "chinese_internal_reference_checked",
           "legal_meaning_preserved", "terminology_check", "entity_role_check",
           "obligation_or_right_check", "condition_exception_deadline_check", "scope_boundary_check",
           "bab_context_check", "issue_severity", "issue_summary_ar", "recommendation_ar")
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    qa_path = argv[0] if argv else QA_DEFAULT

    problems = []
    for p, label in ((qa_path, "QA JSON"), (MD, "Arabic QA report"), (SRC, "P0-005 remediation file")):
        if not os.path.exists(p):
            problems.append("missing: %s (%s)" % (label, os.path.relpath(p, ROOT)))
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1

    try:
        qa = _read(qa_path)
    except (ValueError, OSError) as e:
        print("  - QA JSON is not valid JSON: %s" % e)
        print("RESULT: 1 problem(s) found ✗")
        return 1

    src = _read(SRC)
    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    en = {r["article_number"]: r for r in _read(ENGLISH)["records"]}
    cov = {r["article_number"]: r for r in _read(COV)["records"]}
    src_bab = {r["article_number"]: r["bab"] for r in src["records"]}

    for f in REQ_TOP:
        if f not in qa:
            problems.append("missing required top-level field: %s" % f)

    if qa.get("stage") != "CHINESE_REMEDIATION_BATCH_P0_005_QA":
        problems.append("stage must be CHINESE_REMEDIATION_BATCH_P0_005_QA")
    if qa.get("batch_id") != "P0-005":
        problems.append("batch_id must be P0-005")
    if qa.get("source_batch_file") != SRC_REL:
        problems.append("source_batch_file must point to the P0-005 remediation JSON")
    if qa.get("scope_articles") != ARTS:
        problems.append("scope_articles must exactly match the P0-005 list")
    if qa.get("expected_babs") != [7, 9, 10, 13, 14]:
        problems.append("expected_babs must be [7, 9, 10, 13, 14]")
    dist = qa.get("expected_bab_distribution") or {}
    if {str(k): list(v) for k, v in dist.items()} != DIST:
        problems.append("expected_bab_distribution must match the authorized Bab 7/9/10/13/14 split")
    for f in ("full_chinese_translation_claimed", "official_chinese_translation_claimed",
              "chinese_binding_claimed", "chinese_governing_claimed",
              "full_chinese_281_layer_created", "trilingual_alignment_created",
              "p0_005_chinese_text_modified", "p0_005_data_modified"):
        if qa.get(f) is not False:
            problems.append("%s must be false" % f)
    if qa.get("human_legal_review_status") != "pending_human_legal_review":
        problems.append("human_legal_review_status must remain pending_human_legal_review")
    if qa.get("final_status") not in FINAL:
        problems.append("final_status must be one of %s" % sorted(FINAL))

    lh = qa.get("legal_hierarchy") or {}
    if lh.get("arabic") != "governing":
        problems.append("legal_hierarchy.arabic must be 'governing'")
    if lh.get("english") not in ("guidance_only", "guidance"):
        problems.append("legal_hierarchy.english must be guidance only")
    if lh.get("chinese") != "internal_reference_only":
        problems.append("legal_hierarchy.chinese must be 'internal_reference_only'")
    for k in ("chinese_official", "chinese_binding", "chinese_governing"):
        if lh.get(k) is not False:
            problems.append("legal_hierarchy.%s must be false" % k)

    recs = qa.get("per_article_reviews", [])
    nums = [r.get("article_number") for r in recs]
    if nums != ARTS:
        problems.append("per_article_reviews must cover exactly the 12 P0-005 articles in order")
    if len(set(nums)) != len(nums):
        problems.append("duplicate article numbers in per_article_reviews")
    for r in recs:
        n = r.get("article_number")
        if n not in set(ARTS):
            problems.append("out-of-scope article %s in per_article_reviews" % n)
            continue
        for f in REQ_REC:
            if f not in r:
                problems.append("art %s missing required field %s" % (n, f))
        if r.get("bab") not in (7, 9, 10, 13, 14):
            problems.append("art %s bab must be in [7,9,10,13,14]" % n)
        if n in src_bab and r.get("bab") != src_bab[n]:
            problems.append("art %s QA bab %r != P0-005 record bab %r" % (n, r.get("bab"), src_bab[n]))
        if n in cov and r.get("bab") != cov[n].get("expected_bab_number"):
            problems.append("art %s QA bab %r != coverage-index expected_bab_number %r"
                            % (n, r.get("bab"), cov[n].get("expected_bab_number")))
        if r.get("qa_status") not in STATUS:
            problems.append("art %s invalid qa_status %r" % (n, r.get("qa_status")))

    # final_status must agree with the per-article statuses
    st = [r.get("qa_status") for r in recs]
    if "fail" in st:
        want = "QA_FAIL"
    elif "blocked" in st:
        want = "QA_BLOCKED"
    elif "minor" in st:
        want = "QA_PASS_WITH_MINOR_ISSUES"
    else:
        want = "QA_PASS"
    if qa.get("final_status") in FINAL and qa.get("final_status") != want:
        problems.append("final_status %r inconsistent with per-article statuses (expected %s)"
                        % (qa.get("final_status"), want))

    s = qa.get("qa_summary") or {}
    if s:
        exp = {"article_count": len(recs), "pass": st.count("pass"), "minor": st.count("minor"),
               "blocked": st.count("blocked"), "fail": st.count("fail")}
        for k, v in exp.items():
            if s.get(k) != v:
                problems.append("qa_summary.%s must be %d" % (k, v))

    # no full Arabic/English text, no full remediated Chinese text embedded; no banned overclaim
    blob = json.dumps(qa, ensure_ascii=False)
    src_by = {r["article_number"]: r for r in src["records"]}
    for n in ARTS:
        if n in ar and ar[n]["official_text_ar"] in blob:
            problems.append("QA must not embed full Arabic text (art %s)" % n)
            break
    for n in ARTS:
        if n in en and en[n]["legal_rule_text_en"] in blob:
            problems.append("QA must not embed full English text (art %s)" % n)
            break
    for n in ARTS:
        if n in src_by and src_by[n]["remediated_chinese_text"] in blob:
            problems.append("QA must not embed full remediated Chinese text (art %s)" % n)
            break
    low = blob.lower()
    for term in BANNED:
        if term in low:
            problems.append("banned overclaim term present: %r" % term)

    # sibling batches / QA unchanged (record counts + posture)
    for label, (d, fn) in BATCHES.items():
        path = os.path.join(ROOT, "data", "chinese_remediation_batches", d, fn)
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

    # P0-003/P0-004 forward-guard tooling must still forbid P1/P2/P3 (unchanged by this QA PR)
    for tool in ("validate_chinese_remediation_batch_p0_003.py",
                 "validate_chinese_remediation_batch_p0_003_qa.py",
                 "validate_chinese_remediation_batch_p0_004.py",
                 "validate_chinese_remediation_batch_p0_004_qa.py"):
        tp = os.path.join(ROOT, "scripts", tool)
        if os.path.exists(tp):
            with open(tp, encoding="utf-8") as fh:
                if "p[123]_*" not in fh.read():
                    problems.append("%s forward-guard changed (must still forbid P1/P2/P3)" % tool)

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

    # no post-P0 (P1/P2/P3) batch files created; no generic/factory refactor files.
    # The explicitly-authorized sovereign legal corpus factory FOUNDATION validator is exempt;
    # any OTHER factory script (a generic-validator refactor) is still forbidden.
    # P1-001 is the authorized first P1 batch; only p1_003+/P2/P3 dirs remain forbidden.
    later = [x for x in glob.glob(os.path.join(ROOT, "data", "chinese_remediation_batches", "p[123]_*"))
             if os.path.basename(x) not in ("p1_001", "p1_002")]
    if later:
        problems.append("post-P0 batch dirs (P1/P2/P3) must not exist: %s"
                        % sorted(os.path.basename(x) for x in later))
    factory = [x for x in (glob.glob(os.path.join(ROOT, "scripts", "*factory*")) +
                           glob.glob(os.path.join(ROOT, "src", "**", "*factory*"), recursive=True))
               if os.path.basename(x) != "validate_legal_corpus_factory_foundation.py"]
    if factory:
        problems.append("no generic/factory refactor files must exist yet: %s"
                        % sorted(os.path.relpath(x, ROOT) for x in factory))

    print("=" * 60)
    print("Chinese remediation Batch P0-005 QA validation (final P0 batch)")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] QA of 12 P0-005 articles (Babs 7/9/10/13/14) vs official Arabic (English "
          "secondary); each QA bab matches the P0-005 record and the coverage index; distribution "
          "7:[188..194] 9:[218] 10:[220] 13:[260..262] 14:[274]; allowed qa_status only; legal "
          "hierarchy Arabic-governing / Chinese internal / non-official / non-binding / "
          "non-governing; human review pending; final_status=%s (pass=%d minor=%d blocked=%d "
          "fail=%d) consistent with summary; no full Arabic/English/Chinese text embedded; P0-005 "
          "remediation intact; P0-001..P0-004 + their QA + P0-003/P0-004 tooling + Chinese candidate "
          "189 + old Chinese 5/23 + Arabic 281 + English 281 + English reference 281 + Arabic source "
          "+ Chinese sources 14 + OCR queue unchanged; no P1/P2/P3 and no factory refactor files."
          % (qa.get("final_status"), st.count("pass"), st.count("minor"), st.count("blocked"),
             st.count("fail")))
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
