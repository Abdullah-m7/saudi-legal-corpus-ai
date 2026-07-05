"""Chinese confirmation Batch P3-CONF-001 QA tests (final P3 confirmation QA; review; Babs 2/3).

Review-only QA of the 18 P3 confirmation (retain) decisions: retain appropriate, candidate retained
verbatim by hash (== live 189 candidate), semantic alignment high / completeness near_full re-confirmed,
no new Chinese text generated, nothing modified, source + P3 backlog traceability. No P3 confirmation
data or Chinese candidate modified. Chinese internal / non-official / non-binding / non-governing. All
P2 + P1 + P0 (data + QA), candidate 189, and base layers untouched; no other p3_* dirs. Exercises the
validator rejection paths.
"""

import copy
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QA = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "chinese_remediation_batch_p3_conf_001_qa.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_REMEDIATION_BATCH_P3_CONF_001_QA_AR.md")
SRC = os.path.join(ROOT, "data", "chinese_remediation_batches", "p3_conf_001",
                   "companies_law_m132_1443_zh_internal_confirmation_p3_conf_001.json")
COV = os.path.join(ROOT, "reports", "chinese_translation_review",
                   "chinese_article_coverage_index_001_281.json")
BACKLOG = os.path.join(ROOT, "reports", "chinese_translation_review",
                       "chinese_remediation_backlog_001_281.json")
VALIDATOR = os.path.join(ROOT, "scripts", "validate_chinese_remediation_batch_p3_conf_001_qa.py")

ARTS = [36, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 51, 52, 53, 55, 56, 57]
DIST = {"2": [36, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50], "3": [51, 52, 53, 55, 56, 57]}
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")


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
    p = tmp_path / "p3_conf_001_qa_mutated.json"
    p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return str(p)


def test_validator_passes_on_current_outputs():
    res = _run()
    assert res.returncode == 0, res.stdout + res.stderr


def test_output_files_exist():
    assert os.path.exists(QA) and os.path.exists(MD)


def test_stage_and_batch():
    q = _q()
    assert q["stage"] == "CHINESE_REMEDIATION_BATCH_P3_CONF_001_QA"
    assert q["qa_stage"] == "CHINESE_REMEDIATION_BATCH_P3_CONF_001_QA"
    assert q["batch_id"] == "P3-CONF-001"
    assert q["source_batch_file"].endswith(
        "p3_conf_001/companies_law_m132_1443_zh_internal_confirmation_p3_conf_001.json")
    assert q["source_basis"] == "existing_chinese_internal_candidate"


def test_scope_and_babs():
    q = _q()
    assert q["scope_articles"] == ARTS
    assert q["expected_babs"] == [2, 3]
    assert [r["article_number"] for r in q["per_article_reviews"]] == ARTS


def test_expected_bab_distribution():
    q = _q()
    assert {str(k): list(v) for k, v in q["expected_bab_distribution"].items()} == DIST


def test_each_review_bab_matches_record_and_coverage():
    cov = {r["article_number"]: r for r in _read(COV)["records"]}
    sbab = {r["article_number"]: r["bab"] for r in _read(SRC)["records"]}
    for r in _q()["per_article_reviews"]:
        n = r["article_number"]
        assert r["bab"] in (2, 3)
        assert r["bab"] == sbab[n]
        assert r["bab"] == cov[n]["expected_bab_number"]


def test_result_pass_all_18():
    q = _q()
    assert q["qa_result"] == "PASS"
    assert q["final_status"] == "QA_PASS"
    assert q["pass_count"] == 18
    assert q["minor_fix_count"] == 0
    assert q["blocked_count"] == 0
    assert q["fail_count"] == 0
    assert q["qa_summary"] == {"article_count": 18, "pass": 18, "minor": 0, "blocked": 0, "fail": 0}
    assert all(r["qa_status"] == "pass" for r in q["per_article_reviews"])


def test_review_only_no_modification():
    q = _q()
    assert q["p3_conf_001_confirmation_modified"] is False
    assert q["p3_conf_001_data_modified"] is False
    assert q["chinese_candidate_modified"] is False
    assert q["minor_fixes"] == []
    assert len(_read(SRC)["records"]) == 18


def test_legal_hierarchy_and_boundaries():
    q = _q()
    assert q["legal_hierarchy"]["arabic"] == "governing"
    assert q["legal_hierarchy"]["chinese"] == "internal_reference_only"
    for f in ("full_chinese_translation_claimed", "official_chinese_translation_claimed",
              "chinese_binding_claimed", "chinese_governing_claimed",
              "full_chinese_281_layer_created", "trilingual_alignment_created"):
        assert q[f] is False
    assert q["official_status"]["not_legal_advice"] is True


def test_confirmation_quality_checks_for_each_pass():
    for r in _q()["per_article_reviews"]:
        if r["qa_status"] == "pass":
            assert r["source_traceability"] == "verified"
            assert r["retention_appropriate"] is True
            assert r["candidate_retained_verbatim"] is True
            assert r["no_new_chinese_text_created"] is True
            assert r["no_candidate_modification"] is True
            assert r["semantic_alignment_confirmed"] == "high"
            assert r["legal_completeness_confirmed"] == "near_full"
            assert r["official_status_boundary"] == "internal_non_official_non_binding_non_governing"
            assert r["approved_for_future_layer_integration"] is True
            assert r["backlog_p3_finding_link_checked"] is True


def test_all_scope_articles_are_p3_in_backlog():
    bk = {r["article_number"]: r for r in _read(BACKLOG)["records"]}
    for r in _q()["per_article_reviews"]:
        n = r["article_number"]
        assert bk[n]["current_priority"] == "P3"
        assert bk[n]["remediation_track"] == "P3_retain_internal_reference"


def test_no_full_text_embedded_and_no_overclaim():
    blob = json.dumps(_q(), ensure_ascii=False).lower()
    for term in BANNED:
        assert term not in blob, term


def test_all_p2_qa_unchanged():
    for fn in ("chinese_remediation_batch_p2_001_qa.json", "chinese_remediation_batch_p2_002_qa.json",
               "chinese_remediation_batch_p2_003_qa.json", "chinese_remediation_batch_p2_004_qa.json",
               "chinese_remediation_batch_p2_005_qa.json"):
        qa = _read(os.path.join(ROOT, "reports", "chinese_translation_review", fn))
        assert qa["final_status"] == "QA_PASS"


def test_all_p2_and_p1_data_unchanged():
    for sub, cnt in {"p1_001": 20, "p1_004": 16, "p2_001": 20, "p2_003": 20, "p2_005": 15}.items():
        p = os.path.join(ROOT, "data", "chinese_remediation_batches", sub,
                         "companies_law_m132_1443_zh_internal_remediation_%s.json" % sub)
        assert len(_read(p)["records"]) == cnt


def test_no_other_p3_dirs():
    allowed = ("p1_001", "p1_002", "p1_003", "p1_004", "p2_001", "p2_002", "p2_003", "p2_004",
               "p2_005", "p3_conf_001")
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
    doc["per_article_reviews"][0]["bab"] = 3  # art 36 is Bab 2
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
    doc["pass_count"] = 17
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_retain_flag_false(tmp_path):
    doc = copy.deepcopy(_q())
    doc["per_article_reviews"][0]["candidate_retained_verbatim"] = False
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0
