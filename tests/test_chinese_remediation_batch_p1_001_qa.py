"""Chinese remediation Batch P1-001 QA tests (first P1 batch; article-by-article review vs Arabic).

The QA reviews the 20 merged P1-001 internal Chinese RETRANSLATIONS against the official Arabic
governing text (English secondary): semantic/material completeness, terminology consistency, source
traceability (Arabic/English/prior-candidate/semantic-QA-P1 links), and official-status boundary.
Review only — no P1-001 data modified. QA covers exactly the 20 P1-001 articles across Babs 1/2; each
per-article bab matches the P1-001 record and the coverage index; final_status/qa_summary/counts stay
consistent; Chinese stays internal / non-official / non-binding / non-governing; no full
Arabic/English/Chinese text embedded; P1-001 + all P0 batches/QA and base layers untouched. Reads
committed artifacts and exercises the validator's rejection paths.
"""

import copy
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QA = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "chinese_remediation_batch_p1_001_qa.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_REMEDIATION_BATCH_P1_001_QA_AR.md")
SRC = os.path.join(ROOT, "data", "chinese_remediation_batches", "p1_001",
                   "companies_law_m132_1443_zh_internal_remediation_p1_001.json")
COV = os.path.join(ROOT, "reports", "chinese_translation_review",
                   "chinese_article_coverage_index_001_281.json")
VALIDATOR = os.path.join(ROOT, "scripts", "validate_chinese_remediation_batch_p1_001_qa.py")

ARTS = [1, 2, 3, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 17, 18, 19, 20, 35, 38, 48]
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _q():
    return _read(QA)


def _cov():
    return {r["article_number"]: r for r in _read(COV)["records"]}


def _src_bab():
    return {r["article_number"]: r["bab"] for r in _read(SRC)["records"]}


def _run(path=None):
    args = [sys.executable, VALIDATOR]
    if path is not None:
        args.append(path)
    return subprocess.run(args, capture_output=True, text=True)


def _write_tmp(tmp_path, doc):
    p = tmp_path / "p1_001_qa_mutated.json"
    p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return str(p)


def test_validator_passes_on_current_outputs():
    res = _run()
    assert res.returncode == 0, res.stdout + res.stderr


def test_output_files_exist():
    assert os.path.exists(QA) and os.path.exists(MD)


def test_stage_and_batch():
    q = _q()
    assert q["stage"] == "CHINESE_REMEDIATION_BATCH_P1_001_QA"
    assert q["qa_stage"] == "CHINESE_REMEDIATION_BATCH_P1_001_QA"
    assert q["batch_id"] == "P1-001"
    assert q["source_batch_file"].endswith("p1_001/companies_law_m132_1443_zh_internal_remediation_p1_001.json")


def test_scope_and_babs():
    q = _q()
    assert q["scope_articles"] == ARTS
    assert q["expected_babs"] == [1, 2]
    assert [r["article_number"] for r in q["per_article_reviews"]] == ARTS


def test_each_review_bab_matches_record_and_coverage():
    cov = _cov()
    sbab = _src_bab()
    for r in _q()["per_article_reviews"]:
        n = r["article_number"]
        assert r["bab"] in (1, 2)
        assert r["bab"] == sbab[n]
        assert r["bab"] == cov[n]["expected_bab_number"]


def test_result_pass_all_20():
    q = _q()
    assert q["qa_result"] == "PASS"
    assert q["final_status"] == "QA_PASS"
    assert q["pass_count"] == 20
    assert q["minor_fix_count"] == 0
    assert q["blocked_count"] == 0
    assert q["fail_count"] == 0
    assert q["qa_summary"] == {"article_count": 20, "pass": 20, "minor": 0, "blocked": 0, "fail": 0}
    assert all(r["qa_status"] == "pass" for r in q["per_article_reviews"])


def test_review_only_no_p1_001_modification():
    q = _q()
    assert q["p1_001_chinese_text_modified"] is False
    assert q["p1_001_data_modified"] is False
    assert q["minor_fixes"] == []
    assert len(_read(SRC)["records"]) == 20


def test_legal_hierarchy_and_boundaries():
    q = _q()
    lh = q["legal_hierarchy"]
    assert lh["arabic"] == "governing"
    assert lh["chinese"] == "internal_reference_only"
    for f in ("full_chinese_translation_claimed", "official_chinese_translation_claimed",
              "chinese_binding_claimed", "chinese_governing_claimed",
              "full_chinese_281_layer_created", "trilingual_alignment_created"):
        assert q[f] is False
    assert q["official_status"]["not_legal_advice"] is True


def test_review_model():
    q = _q()
    assert q["source_basis"] == "official_source_based"
    assert q["repository_legal_review"]["repository_legal_review_status"] == "repository_owner_review_active"
    assert q["external_legal_review"]["external_legal_review_required_for_repository_use"] is False


def test_source_traceability_verified_for_each_pass():
    for r in _q()["per_article_reviews"]:
        if r["qa_status"] == "pass":
            assert r["source_traceability"] == "verified"
            assert r["semantic_completeness"] == "materially_complete"
            assert r["arabic_segment_count"] == r["chinese_segment_count"]
            assert r["official_status_boundary"] == "internal_non_official_non_binding_non_governing"


def test_no_full_text_embedded_and_no_overclaim():
    blob = json.dumps(_q(), ensure_ascii=False).lower()
    for term in BANNED:
        assert term not in blob, term


def test_all_p0_qa_unchanged():
    for fn in ("chinese_remediation_batch_p0_002_qa.json", "chinese_remediation_batch_p0_003_qa.json",
               "chinese_remediation_batch_p0_004_qa.json", "chinese_remediation_batch_p0_005_qa.json"):
        qa = _read(os.path.join(ROOT, "reports", "chinese_translation_review", fn))
        assert qa["final_status"] == "QA_PASS"


def test_no_other_p1_p2_p3_dirs():
    later = [x for x in glob.glob(os.path.join(ROOT, "data", "chinese_remediation_batches", "p[123]_*"))
             if os.path.basename(x) not in ("p1_001", "p1_002", "p1_003", "p1_004")]
    assert not later


# --- rejection paths ---

def test_reject_wrong_scope(tmp_path):
    doc = copy.deepcopy(_q())
    doc["per_article_reviews"][0]["article_number"] = 999
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_wrong_bab(tmp_path):
    doc = copy.deepcopy(_q())
    doc["per_article_reviews"][17]["bab"] = 1  # art 35 is Bab 2
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_inconsistent_final_status(tmp_path):
    doc = copy.deepcopy(_q())
    doc["per_article_reviews"][0]["qa_status"] = "minor"
    # final_status still QA_PASS -> inconsistent
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_official_claim_true(tmp_path):
    doc = copy.deepcopy(_q())
    doc["official_chinese_translation_claimed"] = True
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_summary_mismatch(tmp_path):
    doc = copy.deepcopy(_q())
    doc["pass_count"] = 19
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0
