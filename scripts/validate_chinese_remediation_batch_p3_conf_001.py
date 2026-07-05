#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate Chinese confirmation Batch P3-CONF-001 (final P3 confirmation batch; 18 articles, Babs 2/3).

P3 track = confirmation / retain (NOT expansion): the existing internal Chinese candidate for these
articles is already usable as internal reference (semantic alignment high, near-full completeness). This
batch CONFIRMS and RETAINS each candidate verbatim — no new Chinese text is generated and nothing is
modified. Confirms the batch covers exactly the 18 authorized P3 articles, that every record's bab is in
[2,3] and equals the coverage-index expected_bab_number, that each record retains the (unchanged)
candidate by hash (candidate hash == live Chinese candidate record == backlog existing-candidate hash ==
189 semantic-QA hash), re-confirms the semantic-QA finding (alignment high / completeness near_full /
recommended retain-as-internal-reference-candidate) and its P3 backlog finding (priority P3 / track
P3_retain_internal_reference / retain action), carries the internal / non-official / non-binding /
non-governing posture under the repository review model, generates no new Chinese text, and touches no
protected layer (all P2 + P1 + P0 batches + QA, the Chinese candidate 189, and the base corpora). No
other p3_* / p2_006+ batch dirs, no full Chinese 281 layer, no trilingual alignment. Read-only.

Usage: validate_chinese_remediation_batch_p3_conf_001.py [DATA_JSON_PATH]
Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DEFAULT = os.path.join(ROOT, "data", "chinese_remediation_batches", "p3_conf_001",
                            "companies_law_m132_1443_zh_internal_confirmation_p3_conf_001.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_REMEDIATION_BATCH_P3_CONF_001_AR.md")
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
QAS = ("chinese_remediation_batch_p0_002_qa.json", "chinese_remediation_batch_p0_003_qa.json",
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
BABS = (2, 3)
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")
ALLOWED_DIRS = ("p1_001", "p1_002", "p1_003", "p1_004", "p2_001", "p2_002", "p2_003", "p2_004",
                "p2_005", "p3_conf_001")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    data_path = argv[0] if argv else DATA_DEFAULT

    problems = []
    if not os.path.exists(data_path):
        problems.append("missing confirmation data file")
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
        print("  - confirmation JSON is not valid JSON: %s" % e)
        print("RESULT: 1 problem(s) found ✗")
        return 1

    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    en = {r["article_number"]: r for r in _read(ENGLISH)["records"]}
    cov = {r["article_number"]: r for r in _read(COV)["records"]}
    cand = {r["article_number"]: r for r in _read(CANDF)["records"]}
    bk = {r["article_number"]: r for r in _read(BACKLOG)["records"]}
    sq = {r["article_number"]: r for r in _read(SEMQA)["records"]}

    if d.get("stage") != "CHINESE_REMEDIATION_BATCH_P3_CONF_001":
        problems.append("stage must be CHINESE_REMEDIATION_BATCH_P3_CONF_001")
    if d.get("batch_id") != "P3-CONF-001":
        problems.append("batch_id must be P3-CONF-001")
    if d.get("priority") != "P3":
        problems.append("priority must be P3")
    if d.get("remediation_track") != "P3_retain_internal_reference":
        problems.append("remediation_track must be P3_retain_internal_reference")
    if d.get("governing_text_language") != "ar":
        problems.append("governing_text_language must be ar")
    if d.get("confirmation_action") != "retain_as_internal_reference_no_immediate_action":
        problems.append("confirmation_action must be retain_as_internal_reference_no_immediate_action")
    if d.get("new_chinese_text_created") is not False:
        problems.append("top-level new_chinese_text_created must be false")
    if d.get("chinese_text_modified") is not False:
        problems.append("top-level chinese_text_modified must be false")
    if d.get("source_basis") != "existing_chinese_internal_candidate":
        problems.append("source_basis must be existing_chinese_internal_candidate")
    if d.get("expected_babs") != [2, 3]:
        problems.append("expected_babs must be [2, 3]")
    if d.get("scope_articles") != ARTS:
        problems.append("scope_articles must exactly match the authorized P3-CONF-001 list")
    if d.get("article_count") != 18:
        problems.append("article_count must be 18")
    if d.get("final_p3_batch") is not True:
        problems.append("final_p3_batch must be true")
    if d.get("p3_confirmation") is not True:
        problems.append("p3_confirmation must be true")
    if d.get("internal_reference_only") is not True:
        problems.append("internal_reference_only must be true")
    for f in ("official_chinese_translation_claimed", "chinese_binding_claimed",
              "chinese_governing_claimed", "full_chinese_translation_claimed",
              "full_chinese_281_layer_created", "trilingual_alignment_created"):
        if d.get(f) is not False:
            problems.append("top-level %s must be false" % f)

    rlr = d.get("repository_legal_review") or {}
    if rlr.get("repository_owner_has_legal_background") is not True:
        problems.append("repository_owner_has_legal_background must be true")
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
              "official_adoption_claimed", "chinese_official", "chinese_binding", "chinese_governing"):
        if ofs.get(f) is not False:
            problems.append("official_status.%s must be false" % f)
    if ofs.get("not_legal_advice") is not True:
        problems.append("official_status.not_legal_advice must be true")
    if d.get("final_status") != "P3_CONFIRMATION_COMPLETE_INTERNAL_REFERENCE_RETAINED":
        problems.append("final_status must be P3_CONFIRMATION_COMPLETE_INTERNAL_REFERENCE_RETAINED")
    if not isinstance(d.get("protected_layers_unchanged"), dict):
        problems.append("protected_layers_unchanged must be present")
    if not isinstance(d.get("prohibitions_respected"), dict):
        problems.append("prohibitions_respected must be present")

    recs = d.get("records", [])
    nums = [r.get("article_number") for r in recs]
    if nums != ARTS:
        problems.append("record article numbers must be exactly the P3-CONF-001 list, no extras")
    if len(set(nums)) != len(nums):
        problems.append("duplicate article numbers in records")
    allowed = set(ARTS)
    req_rec = ("article_number", "bab", "article_title_ar", "arabic_source_file",
               "arabic_source_hash_sha256", "confirmed_candidate_file", "confirmed_candidate_record_id",
               "confirmed_candidate_hash_sha256", "semantic_qa_file", "semantic_alignment_rating",
               "legal_completeness_rating", "qa_use_status", "semantic_qa_recommended_action",
               "backlog_priority", "backlog_remediation_track", "backlog_remediation_action",
               "backlog_current_blocker", "retained_as_internal_reference", "new_chinese_text_created",
               "chinese_text_modified", "requires_new_chinese_text", "requires_human_legal_review",
               "internal_reference_only", "official_chinese_translation_claimed",
               "chinese_binding_claimed", "chinese_governing_claimed", "source_basis",
               "repository_legal_review_status", "external_legal_review_status", "confirmation_status")
    for r in recs:
        n = r.get("article_number")
        if n not in allowed:
            problems.append("out-of-scope article %s present" % n)
            continue
        for f in req_rec:
            if f not in r:
                problems.append("art %s missing required field %s" % (n, f))
        if r.get("bab") not in BABS:
            problems.append("art %s bab must be in [2,3]" % n)
        if n in cov and r.get("bab") != cov[n].get("expected_bab_number"):
            problems.append("art %s bab %r != coverage-index expected_bab_number %r"
                            % (n, r.get("bab"), cov[n].get("expected_bab_number")))
        # confirmation posture: nothing generated, nothing modified, retained
        if r.get("new_chinese_text_created") is not False:
            problems.append("art %s new_chinese_text_created must be false" % n)
        if r.get("chinese_text_modified") is not False:
            problems.append("art %s chinese_text_modified must be false" % n)
        if r.get("retained_as_internal_reference") is not True:
            problems.append("art %s retained_as_internal_reference must be true" % n)
        if r.get("requires_new_chinese_text") is not False:
            problems.append("art %s requires_new_chinese_text must be false" % n)
        if r.get("source_basis") != "existing_chinese_internal_candidate":
            problems.append("art %s source_basis wrong" % n)
        if r.get("confirmation_status") != "confirmed_retained_as_internal_reference":
            problems.append("art %s confirmation_status wrong" % n)
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
        # arabic governing hash
        if n in ar and r.get("arabic_source_hash_sha256") != ar[n]["official_text_hash_sha256"]:
            problems.append("art %s arabic_source_hash_sha256 != Arabic LLM record hash" % n)
        # candidate retained verbatim: hash == live candidate == backlog existing == semantic-qa
        if n in cand:
            ch = cand[n]["chinese_text_hash_sha256"]
            if r.get("confirmed_candidate_hash_sha256") != ch:
                problems.append("art %s confirmed_candidate_hash != live Chinese candidate hash "
                                "(candidate not retained verbatim)" % n)
            if r.get("confirmed_candidate_record_id") != cand[n]["record_id"]:
                problems.append("art %s confirmed_candidate_record_id != Chinese candidate record_id" % n)
        if n in bk and r.get("confirmed_candidate_hash_sha256") != bk[n].get("existing_chinese_candidate_hash_sha256"):
            problems.append("art %s confirmed candidate hash != backlog existing-candidate hash" % n)
        if n in sq and r.get("confirmed_candidate_hash_sha256") != sq[n].get("chinese_text_hash_sha256"):
            problems.append("art %s confirmed candidate hash != 189 semantic-QA candidate hash" % n)
        # semantic-QA finding re-confirmed
        if n in sq:
            if r.get("semantic_alignment_rating") != sq[n].get("semantic_alignment_rating"):
                problems.append("art %s semantic_alignment_rating != semantic-QA record" % n)
            if r.get("legal_completeness_rating") != sq[n].get("legal_completeness_rating"):
                problems.append("art %s legal_completeness_rating != semantic-QA record" % n)
            if r.get("qa_use_status") != sq[n].get("qa_use_status"):
                problems.append("art %s qa_use_status != semantic-QA record" % n)
            if r.get("semantic_qa_recommended_action") != sq[n].get("recommended_action"):
                problems.append("art %s semantic_qa_recommended_action != semantic-QA record" % n)
            if sq[n].get("recommended_action") != "retain_as_internal_reference_candidate":
                problems.append("art %s semantic-QA action is not retain_as_internal_reference_candidate" % n)
        # P3 backlog finding re-confirmed
        if n in bk:
            if bk[n].get("current_priority") != "P3":
                problems.append("art %s is not a P3 article in the remediation backlog" % n)
            if r.get("backlog_priority") != bk[n].get("current_priority"):
                problems.append("art %s backlog_priority mismatch" % n)
            if r.get("backlog_remediation_track") != bk[n].get("remediation_track"):
                problems.append("art %s backlog_remediation_track mismatch" % n)
            if r.get("backlog_remediation_action") != bk[n].get("remediation_action"):
                problems.append("art %s backlog_remediation_action mismatch" % n)
            if r.get("backlog_current_blocker") != bk[n].get("current_blocker"):
                problems.append("art %s backlog_current_blocker mismatch" % n)
            if bk[n].get("remediation_track") != "P3_retain_internal_reference":
                problems.append("art %s backlog track is not P3_retain_internal_reference" % n)

    # no full Arabic/English/Chinese text embedded; no banned overclaim
    blob = json.dumps(d, ensure_ascii=False)
    for n in ARTS:
        if n in ar and ar[n]["official_text_ar"] in blob:
            problems.append("full Arabic text of art %s must not be embedded" % n)
            break
    for n in ARTS:
        if n in en and en[n]["legal_rule_text_en"] in blob:
            problems.append("full English text of art %s must not be embedded" % n)
            break
    for n in ARTS:
        if n in cand and cand[n]["chinese_text"] in blob:
            problems.append("confirmation must not embed the candidate Chinese text (art %s)" % n)
            break
    low = blob.lower()
    for term in BANNED:
        if term in low:
            problems.append("banned overclaim term present: %r" % term)

    # protected layers: all P0/P1/P2 batches + QA, candidate 189, base corpora
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
    for label, (sub, fn, cnt) in dict(P1_BATCHES, **P2_BATCHES).items():
        path = os.path.join(ROOT, "data", "chinese_remediation_batches", sub, fn)
        if not os.path.exists(path) or len(_read(path)["records"]) != cnt:
            problems.append("%s remediation must remain %d records (untouched)" % (label, cnt))
        elif (_read(path).get("repository_legal_review") or {}).get(
                "repository_legal_review_status") != "repository_owner_review_active":
            problems.append("%s posture changed (forbidden)" % label)

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

    # P1-001..P1-004, P2-001..P2-005 and the single P3 confirmation dir authorized; nothing else
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
    print("Chinese confirmation Batch P3-CONF-001 validation (final P3 confirmation batch)")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] Batch P3-CONF-001: 18 authorized articles across Babs [2,3]; each record retains the "
          "unchanged internal Chinese candidate verbatim by hash (candidate == live 189 candidate == "
          "backlog existing-candidate == semantic-QA hash) — no new Chinese text generated, nothing "
          "modified; the semantic-QA finding (alignment high / completeness near_full / retain action) "
          "and the P3 backlog finding (priority P3 / track P3_retain_internal_reference) are re-"
          "confirmed; internal/non-official/non-binding/non-governing; no full Arabic/English/Chinese "
          "text embedded; all P0 + P1 + P2 batches + QA + Chinese candidate 189 + old Chinese 5/23 + "
          "Arabic/English/English-reference 281 + Arabic source + Chinese sources 14 + OCR queue "
          "unchanged; no other p3_*/p2_006+ dirs; no full-281 / trilingual.")
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
