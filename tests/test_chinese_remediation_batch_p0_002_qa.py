"""Chinese remediation Batch P0-002 QA tests (article-by-article review vs Arabic; review only).

QA reviews the 20 P0-002 internal Chinese reference translations against the official Arabic
governing text (English secondary). Review only — no Chinese text / remediation data changed, human
legal review not marked complete, no full Chinese layer, no trilingual alignment. Hashes only.
Protected layers untouched. Reads committed artifacts and also exercises the validator's rejection
paths (out-of-scope, duplicate, invalid status, missing fields) via temp copies.
"""

import copy
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QA = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "chinese_remediation_batch_p0_002_qa.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_REMEDIATION_BATCH_P0_002_QA_AR.md")
SRC = os.path.join(ROOT, "data", "chinese_remediation_batches", "p0_002",
                   "companies_law_m132_1443_zh_internal_remediation_p0_002.json")
VALIDATOR = os.path.join(ROOT, "scripts", "validate_chinese_remediation_batch_p0_002_qa.py")

ARTS = [86, 87, 88, 89, 91, 92, 93, 94, 95, 96, 97, 98, 100, 103, 104, 105, 106, 107, 109, 110]
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


def _run(path=None):
    args = [sys.executable, VALIDATOR]
    if path is not None:
        args.append(path)
    return subprocess.run(args, capture_output=True, text=True)


def _write_tmp(tmp_path, doc):
    p = tmp_path / "qa_mutated.json"
    p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return str(p)


def test_output_files_exist():
    assert os.path.exists(QA) and os.path.exists(MD)


def test_validator_passes_on_current_outputs():
    res = _run()
    assert res.returncode == 0, res.stdout + res.stderr


def test_exact_article_scope():
    qa = _qa()
    assert qa["scope_articles"] == ARTS
    nums = [r["article_number"] for r in qa["per_article_reviews"]]
    assert nums == ARTS
    assert len(set(nums)) == 20


def test_exact_expected_bab():
    qa = _qa()
    assert qa["expected_babs"] == [4]
    for r in qa["per_article_reviews"]:
        assert r["bab"] == 4


def test_allowed_qa_status_values_only():
    for r in _qa()["per_article_reviews"]:
        assert r["qa_status"] in STATUS
    assert _qa()["final_status"] in FINAL


def test_no_full_chinese_layer_claim():
    qa = _qa()
    assert qa["full_chinese_translation_claimed"] is False
    assert qa.get("full_chinese_281_layer_created", False) is False
    assert qa.get("trilingual_alignment_created", False) is False


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


def test_source_batch_file_pointer():
    assert _qa()["source_batch_file"] == (
        "data/chinese_remediation_batches/p0_002/"
        "companies_law_m132_1443_zh_internal_remediation_p0_002.json")


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


def test_out_of_scope_article_rejected(tmp_path):
    doc = copy.deepcopy(_qa())
    doc["per_article_reviews"][0]["article_number"] = 999
    res = _run(_write_tmp(tmp_path, doc))
    assert res.returncode != 0


def test_duplicate_article_rejected(tmp_path):
    doc = copy.deepcopy(_qa())
    doc["per_article_reviews"][1]["article_number"] = doc["per_article_reviews"][0]["article_number"]
    res = _run(_write_tmp(tmp_path, doc))
    assert res.returncode != 0


def test_invalid_qa_status_rejected(tmp_path):
    doc = copy.deepcopy(_qa())
    doc["per_article_reviews"][0]["qa_status"] = "approved"
    res = _run(_write_tmp(tmp_path, doc))
    assert res.returncode != 0


def test_missing_required_field_rejected(tmp_path):
    doc = copy.deepcopy(_qa())
    del doc["legal_hierarchy"]
    res = _run(_write_tmp(tmp_path, doc))
    assert res.returncode != 0


def test_missing_per_article_field_rejected(tmp_path):
    doc = copy.deepcopy(_qa())
    del doc["per_article_reviews"][0]["legal_meaning_preserved"]
    res = _run(_write_tmp(tmp_path, doc))
    assert res.returncode != 0


def test_official_claim_true_rejected(tmp_path):
    doc = copy.deepcopy(_qa())
    doc["official_chinese_translation_claimed"] = True
    res = _run(_write_tmp(tmp_path, doc))
    assert res.returncode != 0


def test_human_review_completed_rejected(tmp_path):
    doc = copy.deepcopy(_qa())
    doc["human_legal_review_status"] = "complete"
    res = _run(_write_tmp(tmp_path, doc))
    assert res.returncode != 0


def test_validator_is_read_only_on_remediation_data():
    before = open(SRC, "rb").read()
    _run()
    after = open(SRC, "rb").read()
    assert before == after


def test_protected_layers_unchanged():
    candf = _read(os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                               "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json"))
    assert len(candf["records"]) == 189
    p0_001 = _read(os.path.join(ROOT, "data", "chinese_remediation_batches", "p0_001",
                                "companies_law_m132_1443_zh_internal_remediation_p0_001.json"))
    assert len(p0_001["records"]) == 20
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
