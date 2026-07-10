"""Chinese remediation program closure audit tests (read-only consolidated closure).

Verifies the closure audit reports the completed program truthfully: P0/P1/P2/P3 complete (15 batches,
281 articles), every batch has plan==data==QA scope with a passing QA, the implemented coverage is
exactly the full law 1..281 with no missing and no duplicate articles, Chinese stays internal /
non-official / non-binding / non-governing, official Arabic governs, not legal advice, and no full
Chinese 281 layer / trilingual / public release / regulations implementation was created. Reads
committed artifacts and exercises the validator's rejection paths.
"""

import copy
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REV = os.path.join(ROOT, "reports", "chinese_translation_review")
AUDIT = os.path.join(REV, "chinese_remediation_program_closure_audit.json")
MD = os.path.join(REV, "CHINESE_REMEDIATION_PROGRAM_CLOSURE_AUDIT_AR.md")
PLAN = os.path.join(REV, "chinese_remediation_batch_plan.json")
VALIDATOR = os.path.join(ROOT, "scripts", "validate_chinese_remediation_program_closure_audit.py")

BATCH_IDS = ["P0-001", "P0-002", "P0-003", "P0-004", "P0-005",
             "P1-001", "P1-002", "P1-003", "P1-004",
             "P2-001", "P2-002", "P2-003", "P2-004", "P2-005", "P3-CONF-001"]


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _a():
    return _read(AUDIT)


def _run(path=None):
    args = [sys.executable, VALIDATOR]
    if path is not None:
        args.append(path)
    return subprocess.run(args, capture_output=True, text=True)


def _write_tmp(tmp_path, doc):
    p = tmp_path / "closure_mutated.json"
    p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return str(p)


def test_validator_passes_on_current_outputs():
    res = _run()
    assert res.returncode == 0, res.stdout + res.stderr


def test_output_files_exist():
    assert os.path.exists(AUDIT) and os.path.exists(MD)


def test_stage_and_final_status():
    a = _a()
    assert a["stage"] == "CHINESE_REMEDIATION_PROGRAM_CLOSURE_AUDIT"
    assert a["final_status"] == "CHINESE_REMEDIATION_PROGRAM_COMPLETE_CLOSURE_AUDIT_PASS"
    assert a["total_articles_in_law"] == 281
    assert a["batch_count"] == 15


def test_read_only_and_no_new_text():
    a = _a()
    assert a["audit_is_read_only"] is True
    assert a["new_chinese_text_created_in_audit"] is False
    assert a["program_boundaries"]["new_chinese_text_created_in_audit"] is False


def test_program_status_all_complete():
    ps = _a()["program_status"]
    for k in ("P0", "P1", "P2", "P3"):
        assert ps[k] == "complete"
    assert ps["full_program_complete"] is True


def test_priority_track_counts():
    pt = _a()["priority_tracks"]
    assert (pt["P0"]["batch_count"], pt["P0"]["article_count"]) == (5, 92)
    assert (pt["P1"]["batch_count"], pt["P1"]["article_count"]) == (4, 76)
    assert (pt["P2"]["batch_count"], pt["P2"]["article_count"]) == (5, 95)
    assert (pt["P3"]["batch_count"], pt["P3"]["article_count"]) == (1, 18)
    for k in ("P0", "P1", "P2", "P3"):
        assert pt[k]["status"] == "complete"


def test_all_15_batches_listed_qa_pass():
    a = _a()
    ids = [b["batch_id"] for b in a["batches"]]
    assert sorted(ids) == sorted(BATCH_IDS)
    for b in a["batches"]:
        assert b["qa_status"] == "QA_PASS"
        assert b["plan_scope_matches_data"] is True
        assert b["data_scope_matches_qa"] is True


def test_batch_article_count_sum_is_281():
    assert sum(b["article_count"] for b in _a()["batches"]) == 281


def test_coverage_full_law_no_missing_no_dupes():
    cov = _a()["coverage"]
    assert cov["implemented_article_union_count"] == 281
    assert cov["covers_full_law_1_281"] is True
    assert cov["missing_articles"] == []
    assert cov["duplicate_articles"] == []
    assert cov["no_backlog_article_missing"] is True
    assert cov["no_duplicate_article_coverage"] is True
    assert cov["plan_union_matches_implementation"] is True


def test_qa_summary():
    qs = _a()["qa_summary"]
    assert qs["batches_with_qa_pass"] == 15
    assert qs["all_batches_qa_pass"] is True
    assert qs["total_articles_qa_passed"] == 281
    assert qs["total_minor_fixes"] == 0
    assert qs["total_blocked"] == 0
    assert qs["total_failed"] == 0


def test_scope_matches_plan_exactly():
    plan = {b["batch_id"]: b for b in _read(PLAN)["batches"]}
    for b in _a()["batches"]:
        assert b["expected_babs"] == plan[b["batch_id"]]["expected_babs"]


def test_boundaries_and_official_status():
    a = _a()
    pb = a["program_boundaries"]
    for k in ("full_chinese_281_layer_created", "trilingual_alignment_created",
              "public_release_created", "regulations_implementation_started",
              "repository_rename_or_identity_change", "chinese_official", "chinese_binding",
              "chinese_governing"):
        assert pb[k] is False
    assert pb["not_legal_advice"] is True
    lh = a["legal_hierarchy"]
    assert lh["arabic"] == "governing"
    assert lh["chinese"] == "internal_reference_only"
    assert a["official_status"]["not_legal_advice"] is True


def test_review_model():
    a = _a()
    assert a["repository_legal_review"]["repository_legal_review_status"] == "repository_owner_review_active"
    assert a["external_legal_review"]["external_legal_review_required_for_repository_use"] is False


# --- rejection paths ---

def test_reject_missing_article_claim(tmp_path):
    doc = copy.deepcopy(_a())
    doc["coverage"]["missing_articles"] = [7]
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_duplicate_article_claim(tmp_path):
    doc = copy.deepcopy(_a())
    doc["coverage"]["duplicate_articles"] = [7]
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_wrong_batch_count(tmp_path):
    doc = copy.deepcopy(_a())
    doc["batch_count"] = 14
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_incomplete_program(tmp_path):
    doc = copy.deepcopy(_a())
    doc["program_status"]["P3"] = "not_started"
    doc["program_status"]["full_program_complete"] = False
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_batch_not_qa_pass(tmp_path):
    doc = copy.deepcopy(_a())
    doc["batches"][0]["qa_status"] = "QA_FAIL"
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_public_release_claim(tmp_path):
    doc = copy.deepcopy(_a())
    doc["program_boundaries"]["public_release_created"] = True
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_wrong_priority_count(tmp_path):
    doc = copy.deepcopy(_a())
    doc["priority_tracks"]["P2"]["article_count"] = 90
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_new_text_claim(tmp_path):
    doc = copy.deepcopy(_a())
    doc["new_chinese_text_created_in_audit"] = True
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0
