"""Chinese remediation Batch P2-005 QA tests (P2 expansion QA; review vs Arabic; Babs 12/13/14).

Review-only QA of the 15 P2-005 expansions vs the official Arabic (English secondary; prior condensed
candidate as baseline): expansion faithfulness, clause-segment parity, terminology consistency, no
hallucination / omission / over-expansion, source + P2-backlog traceability. No P2-005 data modified.
Chinese internal / non-official / non-binding / non-governing. Prior P2 (P2-001/P2-002) + all P1/P0
(data + QA) and base layers untouched; no p3_* dirs. Exercises the validator rejection paths.
"""

import copy
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QA = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "chinese_remediation_batch_p2_005_qa.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_REMEDIATION_BATCH_P2_005_QA_AR.md")
SRC = os.path.join(ROOT, "data", "chinese_remediation_batches", "p2_005",
                   "companies_law_m132_1443_zh_internal_remediation_p2_005.json")
COV = os.path.join(ROOT, "reports", "chinese_translation_review",
                   "chinese_article_coverage_index_001_281.json")
BACKLOG = os.path.join(ROOT, "reports", "chinese_translation_review",
                       "chinese_remediation_backlog_001_281.json")
VALIDATOR = os.path.join(ROOT, "scripts", "validate_chinese_remediation_batch_p2_005_qa.py")

ARTS = [254, 257, 258, 259, 263, 265, 268, 269, 272, 275, 276, 278, 279, 280, 281]
BABS = (12, 13, 14)
DIST = {'12': [254, 257, 258, 259], '13': [263, 265, 268, 269], '14': [272, 275, 276, 278, 279, 280, 281]}


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _q():
    return _read(QA)


def _run(path=None):
    args = [sys.executable, VALIDATOR]
    if path is not None:
        args.append(path)
    return subprocess.run(args, capture_output=True, text=True)


def _write_tmp(tmp_path, doc):
    p = tmp_path / "p2_005_qa_mutated.json"
    p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return str(p)


def test_validator_passes_on_current_outputs():
    res = _run()
    assert res.returncode == 0, res.stdout + res.stderr


def test_output_files_exist():
    assert os.path.exists(QA) and os.path.exists(MD)


def test_stage_and_batch():
    q = _q()
    assert q["stage"] == "CHINESE_REMEDIATION_BATCH_P2_005_QA"
    assert q["qa_stage"] == "CHINESE_REMEDIATION_BATCH_P2_005_QA"
    assert q["batch_id"] == "P2-005"
    assert q["source_batch_file"].endswith("p2_005/companies_law_m132_1443_zh_internal_remediation_p2_005.json")
    assert q["source_basis"] == "official_arabic_plus_existing_chinese_candidate"


def test_scope_and_babs():
    q = _q()
    assert q["scope_articles"] == ARTS
    assert q["expected_babs"] == list(BABS)
    assert [r["article_number"] for r in q["per_article_reviews"]] == ARTS


def test_expected_bab_distribution():
    q = _q()
    assert {str(k): list(v) for k, v in q["expected_bab_distribution"].items()} == DIST


def test_each_review_bab_matches_record_and_coverage():
    cov = {r["article_number"]: r for r in _read(COV)["records"]}
    sbab = {r["article_number"]: r["bab"] for r in _read(SRC)["records"]}
    for r in _q()["per_article_reviews"]:
        nn = r["article_number"]
        assert r["bab"] in BABS
        assert r["bab"] == sbab[nn]
        assert r["bab"] == cov[nn]["expected_bab_number"]


def test_result_pass_all():
    q = _q()
    assert q["qa_result"] == "PASS"
    assert q["final_status"] == "QA_PASS"
    assert q["pass_count"] == 15
    assert q["minor_fix_count"] == 0
    assert q["blocked_count"] == 0
    assert q["fail_count"] == 0
    assert q["qa_summary"] == {"article_count": 15, "pass": 15, "minor": 0, "blocked": 0, "fail": 0}
    assert all(r["qa_status"] == "pass" for r in q["per_article_reviews"])


def test_review_only_no_modification():
    q = _q()
    assert q["p2_005_chinese_text_modified"] is False
    assert q["p2_005_data_modified"] is False
    assert q["minor_fixes"] == []
    assert len(_read(SRC)["records"]) == 15


def test_legal_hierarchy_and_boundaries():
    q = _q()
    assert q["legal_hierarchy"]["arabic"] == "governing"
    assert q["legal_hierarchy"]["chinese"] == "internal_reference_only"
    for f in ("full_chinese_translation_claimed", "official_chinese_translation_claimed",
              "chinese_binding_claimed", "chinese_governing_claimed",
              "full_chinese_281_layer_created", "trilingual_alignment_created"):
        assert q[f] is False
    assert q["official_status"]["not_legal_advice"] is True


def test_expansion_quality_checks_for_each_pass():
    for r in _q()["per_article_reviews"]:
        if r["qa_status"] == "pass":
            assert r["source_traceability"] == "verified"
            assert r["semantic_completeness"] == "materially_complete"
            assert r["arabic_segment_count"] == r["chinese_segment_count"]
            assert r["official_status_boundary"] == "internal_non_official_non_binding_non_governing"
            assert r["expansion_faithful"] is True
            assert r["no_hallucinated_legal_content"] is True
            assert r["no_missing_legal_effect"] is True
            assert r["no_over_expansion"] is True
            assert r["approved_for_future_layer_integration"] is True
            assert r["backlog_p2_finding_link_checked"] is True


def test_all_scope_articles_are_p2_in_backlog():
    bk = {r["article_number"]: r for r in _read(BACKLOG)["records"]}
    for r in _q()["per_article_reviews"]:
        nn = r["article_number"]
        assert bk[nn]["current_priority"] == "P2"
        assert bk[nn]["remediation_track"] == "P2_expansion_needed"


def test_prior_qa_unchanged():
    for fn in ("chinese_remediation_batch_p2_001_qa.json", "chinese_remediation_batch_p2_002_qa.json",
               "chinese_remediation_batch_p1_004_qa.json"):
        qa = _read(os.path.join(ROOT, "reports", "chinese_translation_review", fn))
        assert qa["final_status"] == "QA_PASS"


def test_no_other_unauthorized_dirs():
    allowed = ("p1_001", "p1_002", "p1_003", "p1_004", "p2_001", "p2_002", "p2_003", "p2_004", "p2_005", "p3_conf_001")
    later = [x for x in glob.glob(os.path.join(ROOT, "data", "chinese_remediation_batches", "p[123]_*"))
             if os.path.basename(x) not in allowed]
    assert not later


# --- rejection paths ---

def test_reject_wrong_scope(tmp_path):
    doc = copy.deepcopy(_q())
    doc["per_article_reviews"][0]["article_number"] = 999
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_wrong_bab(tmp_path):
    doc = copy.deepcopy(_q())
    for r in doc["per_article_reviews"]:
        if r["article_number"] == 254:
            r["bab"] = 13
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_inconsistent_final_status(tmp_path):
    doc = copy.deepcopy(_q())
    doc["per_article_reviews"][0]["qa_status"] = "minor"
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_official_claim_true(tmp_path):
    doc = copy.deepcopy(_q())
    doc["official_chinese_translation_claimed"] = True
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_summary_mismatch(tmp_path):
    doc = copy.deepcopy(_q())
    doc["pass_count"] = 15 - 1
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_missing_expansion_quality_flag(tmp_path):
    doc = copy.deepcopy(_q())
    doc["per_article_reviews"][0]["no_hallucinated_legal_content"] = False
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0
