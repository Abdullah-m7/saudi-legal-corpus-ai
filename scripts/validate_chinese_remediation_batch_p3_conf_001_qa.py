#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the Batch P3-CONF-001 QA (final P3 confirmation QA; article-by-article; Babs 2/3).

Confirms the QA covers exactly the 18 P3 articles, that every per-article bab is in [2,3] and equals
both the P3 confirmation record bab and the coverage-index expected_bab_number, that
expected_bab_distribution matches the authorized split, that counts/final_status stay consistent, that
for each pass the retain decision is re-verified (candidate retained verbatim by hash == live 189
candidate; semantic alignment high / completeness near_full re-confirmed; no new Chinese text generated;
nothing modified) together with the P3 backlog finding, that the QA carries the internal / non-official
/ non-binding / non-governing posture, points at the P3 confirmation file, embeds no full text, and
touches no protected layer (P3 confirmation data, the Chinese candidate 189, all P2 + P1 + P0 batches +
QA, and base corpora). Review only. No other p3_*/p2_006+ dirs; no full-281 / trilingual. Read-only.

Usage: validate_chinese_remediation_batch_p3_conf_001_qa.py [QA_JSON_PATH]
Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QA_DEFAULT = os.path.join(ROOT, "reports", "chinese_translation_review",
                          "chinese_remediation_batch_p3_conf_001_qa.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_REMEDIATION_BATCH_P3_CONF_001_QA_AR.md")
SRC_REL = "data/chinese_remediation_batches/p3_conf_001/companies_law_m132_1443_zh_internal_confirmation_p3_conf_001.json"
SRC = os.path.join(ROOT, SRC_REL)
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
SEMQA = os.path.join(ROOT, "reports", "chinese_translation_review",
                     "chinese_internal_llm_semantic_qa_189.json")

P0_BATCHES = {
    "P0-001": ("p0_001", "companies_law_m132_1443_zh_internal_remediation_p0_001.json"),
    "P0-002": ("p0_002", "companies_law_m132_1443_zh_internal_remediation_p0_002.json"),
    "P0-003": ("p0_003", "companies_law_m132_1443_zh_internal_remediation_p0_003.json"),
    "P0-004": ("p0_004", "companies_law_m132_1443_zh_internal_remediation_p0_004.json"),
    "P0-005": ("p0_005", "companies_law_m132_1443_zh_internal_remediation_p0_005.json"),
}
PASS_QAS = ("chinese_remediation_batch_p0_002_qa.json", "chinese_remediation_batch_p0_003_qa.json",
            "chinese_remediation_batch_p0_004_qa.json", "chinese_remediation_batch_p0_005_qa.json",
            "chinese_remediation_batch_p1_001_qa.json", "chinese_remediation_batch_p1_002_qa.json",
            "chinese_remediation_batch_p1_003_qa.json", "chinese_remediation_batch_p1_004_qa.json",
            "chinese_remediation_batch_p2_001_qa.json", "chinese_remediation_batch_p2_002_qa.json",
            "chinese_remediation_batch_p2_003_qa.json", "chinese_remediation_batch_p2_004_qa.json",
            "chinese_remediation_batch_p2_005_qa.json")
P1_BATCHES = {
    "P1-001": ("p1_001", "companies_law_m132_1443_zh_internal_remediation_p1_001.json", 20),
    "P1-002": ("p1_002", "companies_law_m132_1443_zh_internal_remediation_p1_002.json", 20),
    "P1-003": ("p1_003", "companies_law_m132_1443_zh_internal_remediation_p1_003.json", 20),
    "P1-004": ("p1_004", "companies_law_m132_1443_zh_internal_remediation_p1_004.json", 16),
}
P2_BATCHES = {
    "P2-001": ("p2_001", "companies_law_m132_1443_zh_internal_remediation_p2_001.json", 20),
    "P2-002": ("p2_002", "companies_law_m132_1443_zh_internal_remediation_p2_002.json", 20),
    "P2-003": ("p2_003", "companies_law_m132_1443_zh_internal_remediation_p2_003.json", 20),
    "P2-004": ("p2_004", "companies_law_m132_1443_zh_internal_remediation_p2_004.json", 20),
    "P2-005": ("p2_005", "companies_law_m132_1443_zh_internal_remediation_p2_005.json", 15),
}

ARTS = [36, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 51, 52, 53, 55, 56, 57]
DIST = {"2": [36, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50], "3": [51, 52, 53, 55, 56, 57]}
BABS = {2, 3}
STATUS = {"pass", "minor", "blocked", "fail"}
FINAL = {"QA_PASS", "QA_PASS_WITH_MINOR_FIXES", "QA_BLOCKED", "QA_FAIL"}
ALLOWED_DIRS = ("p1_001", "p1_002", "p1_003", "p1_004", "p2_001", "p2_002", "p2_003", "p2_004",
                "p2_005", "p3_conf_001")
REQ_TOP = ("stage", "qa_stage", "batch_id", "source_batch_file", "scope_articles", "expected_babs",
           "expected_bab_distribution", "qa_method", "legal_hierarchy", "source_basis",
           "repository_legal_review", "external_legal_review", "official_status",
           "full_chinese_translation_claimed", "official_chinese_translation_claimed",
           "chinese_binding_claimed", "chinese_governing_claimed", "full_chinese_281_layer_created",
           "trilingual_alignment_created", "p3_conf_001_confirmation_modified", "p3_conf_001_data_modified",
           "chinese_candidate_modified", "minor_fixes", "qa_result", "pass_count", "minor_fix_count",
           "blocked_count", "fail_count", "qa_summary", "per_article_reviews",
           "protected_layers_unchanged", "prohibitions_respected", "final_status")
REQ_REC = ("article_number", "bab", "qa_status", "qa_result", "retention_appropriate",
           "candidate_retained_verbatim", "semantic_alignment_confirmed", "legal_completeness_confirmed",
           "no_new_chinese_text_created", "no_candidate_modification", "source_traceability",
           "official_status_boundary", "arabic_controlling_source_checked",
           "confirmed_candidate_link_checked", "semantic_qa_link_checked",
           "backlog_p3_finding_link_checked", "issue_severity", "required_fix",
           "approved_for_future_layer_integration", "notes_ar", "notes_en")
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
    for p, label in ((qa_path, "QA JSON"), (MD, "Arabic QA report"), (SRC, "P3 confirmation file")):
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
    srec = {r["article_number"]: r for r in src["records"]}
    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    en = {r["article_number"]: r for r in _read(ENGLISH)["records"]}
    cov = {r["article_number"]: r for r in _read(COV)["records"]}
    cand = {r["article_number"]: r for r in _read(CANDF)["records"]}
    bk = {r["article_number"]: r for r in _read(BACKLOG)["records"]}
    sq = {r["article_number"]: r for r in _read(SEMQA)["records"]}

    for f in REQ_TOP:
        if f not in qa:
            problems.append("missing required top-level field: %s" % f)

    if qa.get("stage") != "CHINESE_REMEDIATION_BATCH_P3_CONF_001_QA":
        problems.append("stage must be CHINESE_REMEDIATION_BATCH_P3_CONF_001_QA")
    if qa.get("qa_stage") != "CHINESE_REMEDIATION_BATCH_P3_CONF_001_QA":
        problems.append("qa_stage must be CHINESE_REMEDIATION_BATCH_P3_CONF_001_QA")
    if qa.get("batch_id") != "P3-CONF-001":
        problems.append("batch_id must be P3-CONF-001")
    if qa.get("source_batch_file") != SRC_REL:
        problems.append("source_batch_file must point to the P3 confirmation JSON")
    if qa.get("scope_articles") != ARTS:
        problems.append("scope_articles must exactly match the P3 list")
    if qa.get("article_count") != 18:
        problems.append("article_count must be 18")
    if qa.get("expected_babs") != [2, 3]:
        problems.append("expected_babs must be [2, 3]")
    dist = qa.get("expected_bab_distribution") or {}
    if {str(k): list(v) for k, v in dist.items()} != DIST:
        problems.append("expected_bab_distribution must match the authorized Bab 2/3 split")
    if qa.get("source_basis") != "existing_chinese_internal_candidate":
        problems.append("source_basis must be existing_chinese_internal_candidate")
    for f in ("full_chinese_translation_claimed", "official_chinese_translation_claimed",
              "chinese_binding_claimed", "chinese_governing_claimed",
              "full_chinese_281_layer_created", "trilingual_alignment_created"):
        if qa.get(f) is not False:
            problems.append("%s must be false" % f)
    if qa.get("p3_conf_001_confirmation_modified") is not False:
        problems.append("p3_conf_001_confirmation_modified must be false")
    if qa.get("p3_conf_001_data_modified") is not False:
        problems.append("p3_conf_001_data_modified must be false")
    if qa.get("chinese_candidate_modified") is not False:
        problems.append("chinese_candidate_modified must be false")
    if qa.get("final_status") not in FINAL:
        problems.append("final_status must be one of %s" % sorted(FINAL))

    rlr = qa.get("repository_legal_review") or {}
    if rlr.get("repository_legal_review_status") != "repository_owner_review_active":
        problems.append("repository_legal_review_status must be repository_owner_review_active")
    if rlr.get("repository_owner_legal_qualification") != "bachelor_of_law":
        problems.append("repository_owner_legal_qualification must be bachelor_of_law")
    elr = qa.get("external_legal_review") or {}
    if elr.get("external_legal_review_required_for_repository_use") is not False:
        problems.append("external legal review must not be required for repository use")
    if elr.get("external_legal_review_status") != "not_performed":
        problems.append("external_legal_review_status must be not_performed")
    ofs = qa.get("official_status") or {}
    for k in ("official_government_publication", "official_translation_claimed",
              "official_adoption_claimed", "chinese_official", "chinese_binding", "chinese_governing"):
        if ofs.get(k) is not False:
            problems.append("official_status.%s must be false" % k)
    if ofs.get("not_legal_advice") is not True:
        problems.append("official_status.not_legal_advice must be true")

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
        problems.append("per_article_reviews must cover exactly the 18 P3 articles in order")
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
        if r.get("bab") not in BABS:
            problems.append("art %s bab must be in [2,3]" % n)
        if n in srec and r.get("bab") != srec[n].get("bab"):
            problems.append("art %s QA bab %r != P3 record bab %r" % (n, r.get("bab"), srec[n].get("bab")))
        if n in cov and r.get("bab") != cov[n].get("expected_bab_number"):
            problems.append("art %s QA bab != coverage-index expected_bab_number" % n)
        if r.get("qa_status") not in STATUS:
            problems.append("art %s invalid qa_status %r" % (n, r.get("qa_status")))
        # a 'pass' must have a genuinely retained candidate + re-confirmed semantic/backlog findings
        if r.get("qa_status") == "pass" and n in srec:
            s = srec[n]
            if not (s["confirmed_candidate_hash_sha256"] == cand[n]["chinese_text_hash_sha256"]
                    and s["confirmed_candidate_hash_sha256"] == sq[n]["chinese_text_hash_sha256"]
                    and sq[n]["recommended_action"] == "retain_as_internal_reference_candidate"
                    and bk[n]["current_priority"] == "P3"
                    and bk[n]["remediation_track"] == "P3_retain_internal_reference"
                    and s["new_chinese_text_created"] is False
                    and s["chinese_text_modified"] is False):
                problems.append("art %s marked pass but retain/traceability does not verify" % n)
            if r.get("source_traceability") != "verified":
                problems.append("art %s pass must record source_traceability=verified" % n)
            if r.get("official_status_boundary") != "internal_non_official_non_binding_non_governing":
                problems.append("art %s pass must record the non-official boundary" % n)
            if r.get("semantic_alignment_confirmed") != sq[n].get("semantic_alignment_rating"):
                problems.append("art %s semantic_alignment_confirmed != semantic-QA record" % n)
            if r.get("legal_completeness_confirmed") != sq[n].get("legal_completeness_rating"):
                problems.append("art %s legal_completeness_confirmed != semantic-QA record" % n)
            for f in ("retention_appropriate", "candidate_retained_verbatim",
                      "no_new_chinese_text_created", "no_candidate_modification",
                      "approved_for_future_layer_integration"):
                if r.get(f) is not True:
                    problems.append("art %s pass must record %s=true" % (n, f))

    st = [r.get("qa_status") for r in recs]
    if "fail" in st:
        want = "QA_FAIL"
    elif "blocked" in st:
        want = "QA_BLOCKED"
    elif "minor" in st:
        want = "QA_PASS_WITH_MINOR_FIXES"
    else:
        want = "QA_PASS"
    if qa.get("final_status") in FINAL and qa.get("final_status") != want:
        problems.append("final_status %r inconsistent with per-article statuses (expected %s)"
                        % (qa.get("final_status"), want))
    exp = {"pass": st.count("pass"), "minor": st.count("minor"),
           "blocked": st.count("blocked"), "fail": st.count("fail")}
    if qa.get("pass_count") != exp["pass"]:
        problems.append("pass_count must be %d" % exp["pass"])
    if qa.get("minor_fix_count") != exp["minor"]:
        problems.append("minor_fix_count must be %d" % exp["minor"])
    if qa.get("blocked_count") != exp["blocked"]:
        problems.append("blocked_count must be %d" % exp["blocked"])
    if qa.get("fail_count") != exp["fail"]:
        problems.append("fail_count must be %d" % exp["fail"])
    s = qa.get("qa_summary") or {}
    exp_sum = dict(exp, article_count=len(recs))
    for k, v in exp_sum.items():
        if s.get(k) != v:
            problems.append("qa_summary.%s must be %d" % (k, v))

    fixes = qa.get("minor_fixes") or []
    if qa.get("p3_conf_001_data_modified") is True or qa.get("chinese_candidate_modified") is True:
        if not fixes:
            problems.append("p3 marked modified but no minor_fixes recorded")
    else:
        if fixes:
            problems.append("minor_fixes recorded but p3 marked unmodified")

    blob = json.dumps(qa, ensure_ascii=False)
    for n in ARTS:
        if n in ar and ar[n]["official_text_ar"] in blob:
            problems.append("QA must not embed full Arabic text (art %s)" % n)
            break
    for n in ARTS:
        if n in en and en[n]["legal_rule_text_en"] in blob:
            problems.append("QA must not embed full English text (art %s)" % n)
            break
    for n in ARTS:
        if n in cand and cand[n]["chinese_text"] in blob:
            problems.append("QA must not embed the candidate Chinese text (art %s)" % n)
            break
    low = blob.lower()
    for term in BANNED:
        if term in low:
            problems.append("banned overclaim term present: %r" % term)

    # P3 confirmation intact; Chinese candidate 189 intact; all P2/P1/P0 + QA unchanged
    if len(src["records"]) != 18:
        problems.append("P3 confirmation must remain 18 records")
    if len(_read(CANDF)["records"]) != 189:
        problems.append("Chinese internal candidate must remain 189 records")
    for label, (sub, fn, cnt) in dict(P1_BATCHES, **P2_BATCHES).items():
        path = os.path.join(ROOT, "data", "chinese_remediation_batches", sub, fn)
        if not os.path.exists(path) or len(_read(path)["records"]) != cnt:
            problems.append("%s remediation must remain %d records (untouched)" % (label, cnt))
    for label, (dsub, fn) in P0_BATCHES.items():
        path = os.path.join(ROOT, "data", "chinese_remediation_batches", dsub, fn)
        if not os.path.exists(path) or len(_read(path)["records"]) not in (12, 20):
            problems.append("%s batch missing / unexpected record count (untouched)" % label)
    for fn in PASS_QAS:
        path = os.path.join(ROOT, "reports", "chinese_translation_review", fn)
        if not os.path.exists(path):
            problems.append("%s must exist and remain unchanged" % fn)
        elif _read(path).get("final_status") != "QA_PASS":
            problems.append("%s posture changed (forbidden)" % fn)

    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    if len(zh) != 5 or sum(len(_read(x)["records"]) for x in zh) != 23:
        problems.append("old Chinese Legal LLM must remain 5 files / 23 records")
    if len(_read(ARABIC)["records"]) != 281 or len(_read(ENGLISH)["records"]) != 281:
        problems.append("Arabic/English full LLM must remain 281 records")
    er = os.path.join(ROOT, "data", "english_reference",
                      "companies_law_m132_1443_en_reference_001_281.json")
    if not os.path.exists(er) or len(_read(er)["records"]) != 281:
        problems.append("English reference full must remain 281 records")
    if os.path.exists(CAND_SRC):
        c = _read(CAND_SRC)
        if len(c.get("articles", [])) != 281 or c.get("verification_status") != "ingested_unverified":
            problems.append("official Arabic source must remain unchanged")
    if len(glob.glob(os.path.join(ROOT, "data", "chinese_translation_sources",
                                  "bab*_zh_source_extracted_articles_*.json"))) != 14:
        problems.append("Chinese source extracted files must remain 14")
    q = os.path.join(ROOT, "reports", "official_arabic_verification", "manual_review_queue.json")
    if os.path.exists(q) and len(_read(q).get("entries", [])) != 281:
        problems.append("OCR manual_review_queue must remain 281 entries")

    later = [x for x in glob.glob(os.path.join(ROOT, "data", "chinese_remediation_batches", "p[123]_*"))
             if os.path.basename(x) not in ALLOWED_DIRS]
    if later:
        problems.append("only P1-001..P1-004, P2-001..P2-005 and the P3 confirmation batch authorized: %s"
                        % sorted(os.path.basename(x) for x in later))
    for pat in ("*trilingual*", "*full_chinese_281*", "*chinese_full_281*"):
        hits = glob.glob(os.path.join(ROOT, "data", "**", pat), recursive=True) + \
            glob.glob(os.path.join(ROOT, "reports", "**", pat), recursive=True)
        if hits:
            problems.append("no full-Chinese-281 / trilingual artifacts allowed: %s"
                            % sorted(os.path.relpath(x, ROOT) for x in hits))

    print("=" * 60)
    print("Chinese confirmation Batch P3-CONF-001 QA validation (final P3 confirmation QA)")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] Batch P3-CONF-001 QA: 18 articles across Babs [2,3] reviewed article-by-article; for "
          "every pass the retain decision holds (candidate retained verbatim by hash == live 189 "
          "candidate; semantic alignment / completeness re-confirmed; no new Chinese text; nothing "
          "modified) and the P3 backlog finding (priority P3 / track P3_retain_internal_reference) is "
          "re-verified; counts consistent; internal/non-official/non-binding/non-governing; review-only "
          "(P3 confirmation + Chinese candidate unmodified); all P2 + P1 + P0 batches + QA + candidate "
          "189 + base corpora unchanged; no other p3_*/p2_006+ dirs; no full-281 / trilingual.")
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
