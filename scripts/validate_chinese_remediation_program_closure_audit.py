#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the Chinese remediation program closure audit (read-only consolidated closure).

Independently recomputes, from the live repository, that the full Chinese remediation program is
complete and internally consistent, and that the committed closure-audit JSON matches:

- P0 / P1 / P2 / P3 are each complete (5 + 4 + 5 + 1 = 15 batches; 92 + 76 + 95 + 18 = 281 articles).
- For every one of the 15 batches, the plan scope (chinese_remediation_batch_plan.json) equals the
  implemented remediation/confirmation data scope equals the QA scope, and the batch's QA is a pass
  (final_status QA_PASS, or the P0-001 legacy schema where pass_count == article_count and no blocked /
  failed).
- The union of implemented article coverage is exactly the full law (1..281): no backlog article missing,
  no duplicate article coverage; the plan union equals the implementation union.
- Chinese stays internal / non-official / non-binding / non-governing; official Arabic governs; not legal
  advice; no full Chinese 281 layer, no trilingual alignment, no public release, no regulations
  implementation; the audit creates no new Chinese text.
- No protected layer changed (all P0/P1/P2 batches + QA, the P3 confirmation + QA, the Chinese candidate
  189, and the base corpora).

Usage: validate_chinese_remediation_program_closure_audit.py [AUDIT_JSON_PATH]
Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REV = os.path.join(ROOT, "reports", "chinese_translation_review")
AUDIT_DEFAULT = os.path.join(REV, "chinese_remediation_program_closure_audit.json")
MD = os.path.join(REV, "CHINESE_REMEDIATION_PROGRAM_CLOSURE_AUDIT_AR.md")
PLAN = os.path.join(REV, "chinese_remediation_batch_plan.json")
CANDF = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                     "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")
ARABIC = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
ENGLISH = os.path.join(ROOT, "data", "official_english_legal_llm",
                       "companies_law_m132_1443_official_english_legal_llm_001_281.json")
CAND_SRC = os.path.join(ROOT, "data", "official_arabic",
                        "companies_law_m132_1443_official_arabic_user_provided.json")

# batch_id -> (priority, dir, data filename, qa filename)
BATCHES = [
    ("P0-001", "P0", "p0_001", "companies_law_m132_1443_zh_internal_remediation_p0_001.json", "chinese_remediation_batch_p0_001_qa.json"),
    ("P0-002", "P0", "p0_002", "companies_law_m132_1443_zh_internal_remediation_p0_002.json", "chinese_remediation_batch_p0_002_qa.json"),
    ("P0-003", "P0", "p0_003", "companies_law_m132_1443_zh_internal_remediation_p0_003.json", "chinese_remediation_batch_p0_003_qa.json"),
    ("P0-004", "P0", "p0_004", "companies_law_m132_1443_zh_internal_remediation_p0_004.json", "chinese_remediation_batch_p0_004_qa.json"),
    ("P0-005", "P0", "p0_005", "companies_law_m132_1443_zh_internal_remediation_p0_005.json", "chinese_remediation_batch_p0_005_qa.json"),
    ("P1-001", "P1", "p1_001", "companies_law_m132_1443_zh_internal_remediation_p1_001.json", "chinese_remediation_batch_p1_001_qa.json"),
    ("P1-002", "P1", "p1_002", "companies_law_m132_1443_zh_internal_remediation_p1_002.json", "chinese_remediation_batch_p1_002_qa.json"),
    ("P1-003", "P1", "p1_003", "companies_law_m132_1443_zh_internal_remediation_p1_003.json", "chinese_remediation_batch_p1_003_qa.json"),
    ("P1-004", "P1", "p1_004", "companies_law_m132_1443_zh_internal_remediation_p1_004.json", "chinese_remediation_batch_p1_004_qa.json"),
    ("P2-001", "P2", "p2_001", "companies_law_m132_1443_zh_internal_remediation_p2_001.json", "chinese_remediation_batch_p2_001_qa.json"),
    ("P2-002", "P2", "p2_002", "companies_law_m132_1443_zh_internal_remediation_p2_002.json", "chinese_remediation_batch_p2_002_qa.json"),
    ("P2-003", "P2", "p2_003", "companies_law_m132_1443_zh_internal_remediation_p2_003.json", "chinese_remediation_batch_p2_003_qa.json"),
    ("P2-004", "P2", "p2_004", "companies_law_m132_1443_zh_internal_remediation_p2_004.json", "chinese_remediation_batch_p2_004_qa.json"),
    ("P2-005", "P2", "p2_005", "companies_law_m132_1443_zh_internal_remediation_p2_005.json", "chinese_remediation_batch_p2_005_qa.json"),
    ("P3-CONF-001", "P3", "p3_conf_001", "companies_law_m132_1443_zh_internal_confirmation_p3_conf_001.json", "chinese_remediation_batch_p3_conf_001_qa.json"),
]
EXPECT_PRIORITY = {"P0": (5, 92), "P1": (4, 76), "P2": (5, 95), "P3": (1, 18)}
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _qa_pass_counts(q):
    s = q.get("qa_summary", {})
    ac = q.get("article_count") or s.get("article_count")
    pc = s.get("pass_count", s.get("pass"))
    mn = s.get("minor_fix_count", s.get("minor", 0)) or 0
    bl = s.get("blocked_count", s.get("blocked", 0)) or 0
    fa = s.get("failed_count", s.get("fail", 0)) or 0
    passed = (q.get("final_status") == "QA_PASS") or (pc == ac and bl == 0 and fa == 0)
    return passed, ac, pc, mn, bl, fa


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    audit_path = argv[0] if argv else AUDIT_DEFAULT

    problems = []
    for p, label in ((audit_path, "closure audit JSON"), (MD, "Arabic closure report"),
                     (PLAN, "batch plan")):
        if not os.path.exists(p):
            problems.append("missing: %s (%s)" % (label, os.path.relpath(p, ROOT)))
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1

    try:
        audit = _read(audit_path)
    except (ValueError, OSError) as e:
        print("  - closure audit JSON is not valid JSON: %s" % e)
        print("RESULT: 1 problem(s) found ✗")
        return 1

    plan = {b["batch_id"]: b for b in _read(PLAN)["batches"]}

    # --- recompute the program from live data ---
    union = []
    prio_batches = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    prio_articles = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    qa_pass_batches = 0
    tot_minor = tot_blocked = tot_failed = tot_passed = 0
    per_batch = {}
    for bid, prio, dd, df, qf in BATCHES:
        if bid not in plan:
            problems.append("plan is missing batch %s" % bid)
            continue
        dpath = os.path.join(ROOT, "data", "chinese_remediation_batches", dd, df)
        qpath = os.path.join(REV, qf)
        if not os.path.exists(dpath):
            problems.append("%s data file missing: %s" % (bid, os.path.relpath(dpath, ROOT)))
            continue
        if not os.path.exists(qpath):
            problems.append("%s QA file missing: %s" % (bid, os.path.relpath(qpath, ROOT)))
            continue
        data = _read(dpath)
        qa = _read(qpath)
        dscope = sorted(r["article_number"] for r in data["records"])
        if "per_article_reviews" in qa:
            qscope = sorted(r["article_number"] for r in qa["per_article_reviews"])
        else:
            qscope = sorted(qa.get("scope_articles") or qa.get("article_numbers") or [])
        pscope = sorted(plan[bid]["article_numbers"])
        if not (pscope == dscope == qscope):
            problems.append("%s scope mismatch (plan/data/qa differ)" % bid)
        passed, ac, pc, mn, bl, fa = _qa_pass_counts(qa)
        if not passed:
            problems.append("%s QA is not a pass" % bid)
        else:
            qa_pass_batches += 1
            tot_passed += pc if pc is not None else len(dscope)
        tot_minor += mn
        tot_blocked += bl
        tot_failed += fa
        union += dscope
        prio_batches[prio] += 1
        prio_articles[prio] += len(dscope)
        per_batch[bid] = (dscope, passed)

    # priority-track expectations
    for prio, (bc, acnt) in EXPECT_PRIORITY.items():
        if prio_batches[prio] != bc:
            problems.append("%s must have %d batches (found %d)" % (prio, bc, prio_batches[prio]))
        if prio_articles[prio] != acnt:
            problems.append("%s must cover %d articles (found %d)" % (prio, acnt, prio_articles[prio]))

    # coverage: exactly 1..281, no missing, no duplicates
    uset = set(union)
    missing = sorted(set(range(1, 282)) - uset)
    dups = sorted(n for n in uset if union.count(n) > 1)
    if missing:
        problems.append("missing articles from implemented coverage: %s" % missing[:20])
    if dups:
        problems.append("duplicate article coverage: %s" % dups[:20])
    if uset != set(range(1, 282)):
        problems.append("implemented union does not equal the full law 1..281")
    if len(union) != 281:
        problems.append("implemented coverage total must be 281 (found %d)" % len(union))
    # plan union sanity
    plan_union = []
    for b in plan.values():
        plan_union += b["article_numbers"]
    if set(plan_union) != set(range(1, 282)) or len(plan_union) != 281:
        problems.append("plan union does not equal the full law 1..281 with no duplicates")
    if set(plan_union) != uset:
        problems.append("plan union != implemented union")

    # --- cross-check the committed audit JSON against the recomputed truth ---
    if audit.get("stage") != "CHINESE_REMEDIATION_PROGRAM_CLOSURE_AUDIT":
        problems.append("stage must be CHINESE_REMEDIATION_PROGRAM_CLOSURE_AUDIT")
    if audit.get("total_articles_in_law") != 281:
        problems.append("total_articles_in_law must be 281")
    if audit.get("batch_count") != 15:
        problems.append("batch_count must be 15")
    if audit.get("new_chinese_text_created_in_audit") is not False:
        problems.append("new_chinese_text_created_in_audit must be false")
    if audit.get("audit_is_read_only") is not True:
        problems.append("audit_is_read_only must be true")
    ps = audit.get("program_status") or {}
    for k in ("P0", "P1", "P2", "P3"):
        if ps.get(k) != "complete":
            problems.append("program_status.%s must be complete" % k)
    if ps.get("full_program_complete") is not True:
        problems.append("program_status.full_program_complete must be true")
    pt = audit.get("priority_tracks") or {}
    for prio, (bc, acnt) in EXPECT_PRIORITY.items():
        t = pt.get(prio) or {}
        if t.get("batch_count") != bc or t.get("article_count") != acnt or t.get("status") != "complete":
            problems.append("priority_tracks.%s must be %d batches / %d articles / complete" % (prio, bc, acnt))
    cov = audit.get("coverage") or {}
    if cov.get("implemented_article_union_count") != 281:
        problems.append("coverage.implemented_article_union_count must be 281")
    if cov.get("covers_full_law_1_281") is not True:
        problems.append("coverage.covers_full_law_1_281 must be true")
    if cov.get("missing_articles") != missing or missing:
        problems.append("coverage.missing_articles must be [] and match recomputed")
    if cov.get("duplicate_articles") != dups or dups:
        problems.append("coverage.duplicate_articles must be [] and match recomputed")
    if cov.get("no_backlog_article_missing") is not True:
        problems.append("coverage.no_backlog_article_missing must be true")
    if cov.get("no_duplicate_article_coverage") is not True:
        problems.append("coverage.no_duplicate_article_coverage must be true")
    qs = audit.get("qa_summary") or {}
    if qs.get("batches_with_qa_pass") != qa_pass_batches or qa_pass_batches != 15:
        problems.append("qa_summary.batches_with_qa_pass must be 15 and match recomputed")
    if qs.get("all_batches_qa_pass") is not True:
        problems.append("qa_summary.all_batches_qa_pass must be true")
    if qs.get("total_articles_qa_passed") != tot_passed or tot_passed != 281:
        problems.append("qa_summary.total_articles_qa_passed must be 281 and match recomputed")
    for k, v in (("total_minor_fixes", tot_minor), ("total_blocked", tot_blocked),
                 ("total_failed", tot_failed)):
        if qs.get(k) != v:
            problems.append("qa_summary.%s must be %d (recomputed)" % (k, v))
    # per-batch block matches recompute
    ab = {b["batch_id"]: b for b in audit.get("batches", [])}
    if sorted(ab) != sorted(bid for bid, *_ in BATCHES):
        problems.append("audit.batches must list exactly the 15 program batches")
    for bid, prio, dd, df, qf in BATCHES:
        b = ab.get(bid)
        if not b:
            continue
        if b.get("qa_status") != "QA_PASS":
            problems.append("audit batch %s qa_status must be QA_PASS" % bid)
        if b.get("plan_scope_matches_data") is not True or b.get("data_scope_matches_qa") is not True:
            problems.append("audit batch %s scope-match flags must be true" % bid)
        if bid in per_batch and b.get("article_count") != len(per_batch[bid][0]):
            problems.append("audit batch %s article_count mismatch" % bid)
        if b.get("expected_babs") != plan[bid]["expected_babs"]:
            problems.append("audit batch %s expected_babs != plan" % bid)

    # boundaries / posture
    lh = audit.get("legal_hierarchy") or {}
    if lh.get("arabic") != "governing" or lh.get("chinese") != "internal_reference_only":
        problems.append("legal_hierarchy must have Arabic governing and Chinese internal_reference_only")
    for k in ("chinese_official", "chinese_binding", "chinese_governing"):
        if lh.get(k) is not False:
            problems.append("legal_hierarchy.%s must be false" % k)
    pb = audit.get("program_boundaries") or {}
    for k in ("new_chinese_text_created_in_audit", "full_chinese_281_layer_created",
              "trilingual_alignment_created", "public_release_created",
              "regulations_implementation_started", "repository_rename_or_identity_change",
              "chinese_official", "chinese_binding", "chinese_governing"):
        if pb.get(k) is not False:
            problems.append("program_boundaries.%s must be false" % k)
    if pb.get("not_legal_advice") is not True:
        problems.append("program_boundaries.not_legal_advice must be true")
    ofs = audit.get("official_status") or {}
    if ofs.get("not_legal_advice") is not True:
        problems.append("official_status.not_legal_advice must be true")
    rlr = audit.get("repository_legal_review") or {}
    if rlr.get("repository_legal_review_status") != "repository_owner_review_active":
        problems.append("repository_legal_review_status must be repository_owner_review_active")
    elr = audit.get("external_legal_review") or {}
    if elr.get("external_legal_review_required_for_repository_use") is not False:
        problems.append("external legal review must not be required for repository use")
    if audit.get("final_status") != "CHINESE_REMEDIATION_PROGRAM_COMPLETE_CLOSURE_AUDIT_PASS":
        problems.append("final_status must be CHINESE_REMEDIATION_PROGRAM_COMPLETE_CLOSURE_AUDIT_PASS")

    # no full Arabic/English/candidate text embedded; no banned overclaim
    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    en = {r["article_number"]: r for r in _read(ENGLISH)["records"]}
    cand = {r["article_number"]: r for r in _read(CANDF)["records"]}
    blob = json.dumps(audit, ensure_ascii=False)
    for n in (1, 60, 158, 281):
        if n in ar and ar[n]["official_text_ar"] in blob:
            problems.append("closure audit must not embed full Arabic text")
            break
    for n in (1, 60, 158, 281):
        if n in en and en[n]["legal_rule_text_en"] in blob:
            problems.append("closure audit must not embed full English text")
            break
    for n in (36, 60, 158):
        if n in cand and cand[n]["chinese_text"] in blob:
            problems.append("closure audit must not embed Chinese candidate text")
            break
    low = blob.lower()
    for term in BANNED:
        if term in low:
            problems.append("banned overclaim term present: %r" % term)

    # protected base layers unchanged
    if len(cand) != 189:
        problems.append("Chinese internal candidate must remain 189 records")
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    if len(zh) != 5 or sum(len(_read(x)["records"]) for x in zh) != 23:
        problems.append("old Chinese Legal LLM must remain 5 files / 23 records")
    if len(ar) != 281 or len(en) != 281:
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

    # no full-281 / trilingual artifacts anywhere
    for pat in ("*trilingual*", "*full_chinese_281*", "*chinese_full_281*"):
        hits = glob.glob(os.path.join(ROOT, "data", "**", pat), recursive=True) + \
            glob.glob(os.path.join(ROOT, "reports", "**", pat), recursive=True)
        if hits:
            problems.append("no full-Chinese-281 / trilingual artifacts allowed: %s"
                            % sorted(os.path.relpath(x, ROOT) for x in hits))

    print("=" * 60)
    print("Chinese remediation program closure audit validation")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] Closure audit: P0 (5 batches / 92) + P1 (4 / 76) + P2 (5 / 95) + P3 (1 / 18) = 15 "
          "batches / 281 articles, all complete; for every batch the plan scope == implemented data "
          "scope == QA scope and the QA is a pass (15/15 QA_PASS, 281 articles passed, 0 minor / 0 "
          "blocked / 0 failed); the implemented union is exactly the full law 1..281 with no missing "
          "article and no duplicate coverage, and equals the plan union; Chinese stays internal / "
          "non-official / non-binding / non-governing, official Arabic governs, not legal advice; the "
          "audit creates no new Chinese text; no full Chinese 281 layer / trilingual alignment / public "
          "release / regulations implementation; all P0/P1/P2 batches + QA, the P3 confirmation + QA, the "
          "Chinese candidate 189, and the base corpora unchanged. The committed closure-audit JSON "
          "matches the recomputed program state.")
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
