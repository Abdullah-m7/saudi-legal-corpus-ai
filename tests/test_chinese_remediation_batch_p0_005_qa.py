"""Chinese remediation Batch P0-005 QA tests (final P0 batch; review vs Arabic; Babs 7/9/10/13/14).

QA reviews the 12 P0-005 internal Chinese reference translations against the official Arabic governing
text (English secondary). Review only — no Chinese text / remediation data changed, human legal
review not marked complete, no full Chinese layer, no trilingual alignment. Each per-article bab must
match the P0-005 record bab and the coverage-index expected_bab_number. Reads committed artifacts and
exercises the validator's rejection paths via temp copies.
"""

import copy
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QA = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "chinese_remediation_batch_p0_005_qa.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_REMEDIATION_BATCH_P0_005_QA_AR.md")
SRC = os.path.join(ROOT, "data", "chinese_remediation_batches", "p0_005",
                   "companies_law_m132_1443_zh_internal_remediation_p0_005.json")
COV = os.path.join(ROOT, "reports", "chinese_translation_review",
                   "chinese_article_coverage_index_001_281.json")
RV = os.path.join(ROOT, "reports", "chinese_translation_review")
BD = os.path.join(ROOT, "data", "chinese_remediation_batches")
P0_002_QA = os.path.join(RV, "chinese_remediation_batch_p0_002_qa.json")
P0_003_QA = os.path.join(RV, "chinese_remediation_batch_p0_003_qa.json")
P0_004_QA = os.path.join(RV, "chinese_remediation_batch_p0_004_qa.json")
CANDF = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                     "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")
VALIDATOR = os.path.join(ROOT, "scripts", "validate_chinese_remediation_batch_p0_005_qa.py")

ARTS = [188, 189, 190, 191, 192, 194, 218, 220, 260, 261, 262, 274]
DIST = {"7": [188, 189, 190, 191, 192, 194], "9": [218], "10": [220],
        "13": [260, 261, 262], "14": [274]}
STATUS = {"pass", "minor", "blocked", "fail"}
FINAL = {"QA_PASS", "QA_PASS_WITH_MINOR_ISSUES", "QA_BLOCKED", "QA_FAIL"}
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _qa():
    return _read(QA)


def _cov():
    return {r["article_number"]: r for r in _read(COV)["records"]}


def _src_bab():
    return {r["article_number"]: r["bab"] for r in _read(SRC)["records"]}


def _batch(name):
    return os.path.join(BD, name, "companies_law_m132_1443_zh_internal_remediation_%s.json"
                        % name)


def _run(path=None):
    args = [sys.executable, VALIDATOR]
    if path is not None:
        args.append(path)
    return subprocess.run(args, capture_output=True, text=True)


def _write_tmp(tmp_path, doc):
    p = tmp_path / "qa_mutated.json"
    p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return str(p)


def test_validator_passes_on_current_outputs():
    res = _run()
    assert res.returncode == 0, res.stdout + res.stderr


def test_output_files_exist():
    assert os.path.exists(QA) and os.path.exists(MD)


def test_exact_article_scope():
    qa = _qa()
    assert qa["scope_articles"] == ARTS
    nums = [r["article_number"] for r in qa["per_article_reviews"]]
    assert nums == ARTS
    assert len(set(nums)) == 12


def test_exact_expected_babs():
    assert _qa()["expected_babs"] == [7, 9, 10, 13, 14]


def test_exact_expected_bab_distribution():
    dist = {str(k): list(v) for k, v in _qa()["expected_bab_distribution"].items()}
    assert dist == DIST


def test_no_duplicate_articles():
    nums = [r["article_number"] for r in _qa()["per_article_reviews"]]
    assert len(set(nums)) == 12


def test_no_out_of_scope_articles():
    assert set(r["article_number"] for r in _qa()["per_article_reviews"]) == set(ARTS)


def test_per_article_bab_matches_record_and_coverage():
    cov = _cov()
    srcb = _src_bab()
    for r in _qa()["per_article_reviews"]:
        n = r["article_number"]
        assert r["bab"] in (7, 9, 10, 13, 14)
        assert r["bab"] == srcb[n]
        assert r["bab"] == cov[n]["expected_bab_number"]


def test_allowed_qa_status_values_only():
    for r in _qa()["per_article_reviews"]:
        assert r["qa_status"] in STATUS
    assert _qa()["final_status"] in FINAL


def test_final_status_consistency():
    qa = _qa()
    st = [r["qa_status"] for r in qa["per_article_reviews"]]
    want = ("QA_FAIL" if "fail" in st else "QA_BLOCKED" if "blocked" in st
            else "QA_PASS_WITH_MINOR_ISSUES" if "minor" in st else "QA_PASS")
    assert qa["final_status"] == want


def test_qa_summary_consistency():
    qa = _qa()
    st = [r["qa_status"] for r in qa["per_article_reviews"]]
    s = qa["qa_summary"]
    assert s["article_count"] == len(st)
    assert s["pass"] == st.count("pass")
    assert s["minor"] == st.count("minor")
    assert s["blocked"] == st.count("blocked")
    assert s["fail"] == st.count("fail")


def test_no_full_chinese_layer_claim():
    qa = _qa()
    assert qa["full_chinese_translation_claimed"] is False
    assert qa["full_chinese_281_layer_created"] is False


def test_no_trilingual_alignment():
    assert _qa()["trilingual_alignment_created"] is False


def test_no_official_binding_governing_chinese_claim():
    qa = _qa()
    assert qa["official_chinese_translation_claimed"] is False
    assert qa["chinese_binding_claimed"] is False
    assert qa["chinese_governing_claimed"] is False
    blob = json.dumps(qa, ensure_ascii=False).lower()
    for term in BANNED:
        assert term not in blob, term


def test_human_legal_review_remains_pending():
    assert _qa()["human_legal_review_status"] == "pending_human_legal_review"
    assert _read(SRC)["human_legal_review_status"] == "pending_human_legal_review"


def test_protected_legal_hierarchy():
    lh = _qa()["legal_hierarchy"]
    assert lh["arabic"] == "governing"
    assert lh["english"] in ("guidance_only", "guidance")
    assert lh["chinese"] == "internal_reference_only"
    assert lh["chinese_official"] is False
    assert lh["chinese_binding"] is False
    assert lh["chinese_governing"] is False


def test_qa_is_review_only():
    qa = _qa()
    assert qa["p0_005_chinese_text_modified"] is False
    assert qa["p0_005_data_modified"] is False


def test_p0_005_remediation_data_unchanged():
    src = _read(SRC)
    assert len(src["records"]) == 12
    assert [r["article_number"] for r in src["records"]] == ARTS
    assert src["human_legal_review_status"] == "pending_human_legal_review"


def test_validator_is_read_only_on_remediation_data():
    before = open(SRC, "rb").read()
    _run()
    after = open(SRC, "rb").read()
    assert before == after


def test_no_full_arabic_english_chinese_text_duplicated():
    ar = {r["article_number"]: r for r in _read(os.path.join(
        ROOT, "data", "official_arabic_legal_llm",
        "companies_law_m132_1443_official_arabic_legal_llm_001_281.json"))["records"]}
    en = {r["article_number"]: r for r in _read(os.path.join(
        ROOT, "data", "official_english_legal_llm",
        "companies_law_m132_1443_official_english_legal_llm_001_281.json"))["records"]}
    src = {r["article_number"]: r for r in _read(SRC)["records"]}
    blob = json.dumps(_qa(), ensure_ascii=False)
    for n in ARTS:
        assert ar[n]["official_text_ar"] not in blob
        assert en[n]["legal_rule_text_en"] not in blob
        assert src[n]["remediated_chinese_text"] not in blob


def test_p0_001_unchanged():
    assert len(_read(_batch("p0_001"))["records"]) == 20


def test_p0_002_unchanged():
    assert len(_read(_batch("p0_002"))["records"]) == 20


def test_p0_002_qa_unchanged():
    qa = _read(P0_002_QA)
    assert qa["batch_id"] == "P0-002" and qa["final_status"] == "QA_PASS"


def test_p0_003_unchanged():
    assert len(_read(_batch("p0_003"))["records"]) == 20


def test_p0_003_qa_unchanged():
    qa = _read(P0_003_QA)
    assert qa["batch_id"] == "P0-003" and qa["final_status"] == "QA_PASS"


def test_p0_003_tooling_unchanged():
    for tool in ("validate_chinese_remediation_batch_p0_003.py",
                 "validate_chinese_remediation_batch_p0_003_qa.py"):
        with open(os.path.join(ROOT, "scripts", tool), encoding="utf-8") as fh:
            assert "p[123]_*" in fh.read()


def test_p0_004_unchanged():
    assert len(_read(_batch("p0_004"))["records"]) == 20


def test_p0_004_qa_unchanged():
    qa = _read(P0_004_QA)
    assert qa["batch_id"] == "P0-004" and qa["final_status"] == "QA_PASS"


def test_p0_004_tooling_unchanged():
    for tool in ("validate_chinese_remediation_batch_p0_004.py",
                 "validate_chinese_remediation_batch_p0_004_qa.py"):
        with open(os.path.join(ROOT, "scripts", tool), encoding="utf-8") as fh:
            assert "p[123]_*" in fh.read()


def test_protected_layers_unchanged():
    assert len(_read(CANDF)["records"]) == 189
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    assert len(zh) == 5 and sum(len(_read(p)["records"]) for p in zh) == 23
    assert len(_read(os.path.join(ROOT, "data", "official_arabic_legal_llm",
                                  "companies_law_m132_1443_official_arabic_legal_llm_001_281.json"))["records"]) == 281
    assert len(_read(os.path.join(ROOT, "data", "official_english_legal_llm",
                                  "companies_law_m132_1443_official_english_legal_llm_001_281.json"))["records"]) == 281
    er = _read(os.path.join(ROOT, "data", "english_reference",
                            "companies_law_m132_1443_en_reference_001_281.json"))
    assert len(er["records"]) == 281
    c = _read(os.path.join(ROOT, "data", "official_arabic",
                           "companies_law_m132_1443_official_arabic_user_provided.json"))
    assert len(c["articles"]) == 281 and c["verification_status"] == "ingested_unverified"
    assert len(glob.glob(os.path.join(ROOT, "data", "chinese_translation_sources",
                                      "bab*_zh_source_extracted_articles_*.json"))) == 14


def test_no_p1_p2_p3_files():
    # P1-001 is the authorized first P1 batch; only p1_002+/P2/P3 dirs remain forbidden.
    later = [x for x in glob.glob(os.path.join(BD, "p[123]_*")) if os.path.basename(x) != "p1_001"]
    assert not later


def test_no_generic_factory_refactor_files():
    # The explicitly-authorized sovereign legal corpus factory FOUNDATION validator is permitted;
    # any OTHER factory script (a generic-validator refactor) is still forbidden.
    extra = [x for x in glob.glob(os.path.join(ROOT, "scripts", "*factory*"))
             if os.path.basename(x) != "validate_legal_corpus_factory_foundation.py"]
    assert not extra
    assert not glob.glob(os.path.join(ROOT, "src", "**", "*factory*"), recursive=True)


# --- rejection paths ---

def test_reject_out_of_scope_article(tmp_path):
    doc = copy.deepcopy(_qa())
    doc["per_article_reviews"][0]["article_number"] = 999
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_duplicate_article(tmp_path):
    doc = copy.deepcopy(_qa())
    doc["per_article_reviews"][1]["article_number"] = doc["per_article_reviews"][0]["article_number"]
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_wrong_bab(tmp_path):
    doc = copy.deepcopy(_qa())
    doc["per_article_reviews"][0]["bab"] = 14  # art 188 is Bab 7
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_invalid_qa_status(tmp_path):
    doc = copy.deepcopy(_qa())
    doc["per_article_reviews"][0]["qa_status"] = "approved"
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_missing_required_top_field(tmp_path):
    doc = copy.deepcopy(_qa())
    del doc["legal_hierarchy"]
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_missing_per_article_field(tmp_path):
    doc = copy.deepcopy(_qa())
    del doc["per_article_reviews"][0]["bab_context_check"]
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_official_claim_true(tmp_path):
    doc = copy.deepcopy(_qa())
    doc["official_chinese_translation_claimed"] = True
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_human_review_completed(tmp_path):
    doc = copy.deepcopy(_qa())
    doc["human_legal_review_status"] = "complete"
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_inconsistent_final_status(tmp_path):
    doc = copy.deepcopy(_qa())
    doc["final_status"] = "QA_FAIL"
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_inconsistent_qa_summary(tmp_path):
    doc = copy.deepcopy(_qa())
    doc["qa_summary"]["pass"] = 11
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_p0_005_data_modified_true(tmp_path):
    doc = copy.deepcopy(_qa())
    doc["p0_005_data_modified"] = True
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_p0_005_chinese_text_modified_true(tmp_path):
    doc = copy.deepcopy(_qa())
    doc["p0_005_chinese_text_modified"] = True
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_starting_p1_p2_p3():
    # P1-001 is authorized; any OTHER later batch dir (p1_002+/P2/P3) must make the validator fail.
    for name in ("p1_002", "p2_001", "p3_001"):
        p = os.path.join(BD, name)
        created = False
        try:
            if not os.path.isdir(p):
                os.makedirs(p)
                created = True
            assert _run().returncode != 0, name
        finally:
            if created:
                os.rmdir(p)
    assert _run().returncode == 0
