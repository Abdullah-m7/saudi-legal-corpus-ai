"""Chinese remediation Batch P0-005 tests (final P0 batch; 12 articles, Babs 7/9/10/13/14).

The batch creates new internal Chinese reference text for exactly the 12 authorized P0-005 articles,
translated from the official Arabic governing text (English guidance only). It spans Babs 7/9/10/13/14;
each record's bab must match the official coverage-index expected_bab_number. Chinese is internal /
non-official / non-binding / non-governing; human legal review pending; qa_status pending_future_qa.
No full Arabic/English text embedded; P0-001..P0-004 and their QA and base layers untouched; no
P1/P2/P3 batch dirs. Reads committed artifacts and exercises the validator's rejection paths.
"""

import copy
import glob
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "chinese_remediation_batches", "p0_005",
                    "companies_law_m132_1443_zh_internal_remediation_p0_005.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_REMEDIATION_BATCH_P0_005_AR.md")
ARABIC = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
ENGLISH = os.path.join(ROOT, "data", "official_english_legal_llm",
                       "companies_law_m132_1443_official_english_legal_llm_001_281.json")
COV = os.path.join(ROOT, "reports", "chinese_translation_review",
                   "chinese_article_coverage_index_001_281.json")
CANDF = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                     "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")
P0_001 = os.path.join(ROOT, "data", "chinese_remediation_batches", "p0_001",
                      "companies_law_m132_1443_zh_internal_remediation_p0_001.json")
P0_002 = os.path.join(ROOT, "data", "chinese_remediation_batches", "p0_002",
                      "companies_law_m132_1443_zh_internal_remediation_p0_002.json")
P0_003 = os.path.join(ROOT, "data", "chinese_remediation_batches", "p0_003",
                      "companies_law_m132_1443_zh_internal_remediation_p0_003.json")
P0_004 = os.path.join(ROOT, "data", "chinese_remediation_batches", "p0_004",
                      "companies_law_m132_1443_zh_internal_remediation_p0_004.json")
P0_002_QA = os.path.join(ROOT, "reports", "chinese_translation_review",
                         "chinese_remediation_batch_p0_002_qa.json")
P0_003_QA = os.path.join(ROOT, "reports", "chinese_translation_review",
                         "chinese_remediation_batch_p0_003_qa.json")
P0_004_QA = os.path.join(ROOT, "reports", "chinese_translation_review",
                         "chinese_remediation_batch_p0_004_qa.json")
VALIDATOR = os.path.join(ROOT, "scripts", "validate_chinese_remediation_batch_p0_005.py")

ARTS = [188, 189, 190, 191, 192, 194, 218, 220, 260, 261, 262, 274]
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _d():
    return _read(DATA)


def _cov():
    return {r["article_number"]: r for r in _read(COV)["records"]}


def _run(path=None):
    args = [sys.executable, VALIDATOR]
    if path is not None:
        args.append(path)
    return subprocess.run(args, capture_output=True, text=True)


def _write_tmp(tmp_path, doc):
    p = tmp_path / "p0_005_mutated.json"
    p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return str(p)


def test_validator_passes_on_current_outputs():
    res = _run()
    assert res.returncode == 0, res.stdout + res.stderr


def test_output_files_exist():
    assert os.path.exists(DATA) and os.path.exists(MD)


def test_exact_article_scope():
    d = _d()
    assert d["scope_articles"] == ARTS
    assert [r["article_number"] for r in d["records"]] == ARTS


def test_exact_expected_babs():
    assert _d()["expected_babs"] == [7, 9, 10, 13, 14]


def test_exact_record_count():
    assert _d()["article_count"] == 12
    assert len(_d()["records"]) == 12


def test_no_duplicate_articles():
    nums = [r["article_number"] for r in _d()["records"]]
    assert len(set(nums)) == 12


def test_no_out_of_scope_articles():
    assert set(r["article_number"] for r in _d()["records"]) == set(ARTS)


def test_each_record_bab_in_range():
    for r in _d()["records"]:
        assert r["bab"] in (7, 9, 10, 13, 14)


def test_each_record_bab_matches_coverage_index():
    cov = _cov()
    for r in _d()["records"]:
        assert r["bab"] == cov[r["article_number"]]["expected_bab_number"]


def test_posture_flags_correct():
    d = _d()
    assert d["internal_reference_only"] is True
    assert d["human_legal_review_status"] == "pending_human_legal_review"
    for r in d["records"]:
        assert r["internal_reference_only"] is True
        assert r["translation_basis"] == "official_arabic_governing_text"
        assert r["english_guidance_role"] == "secondary_guidance_only"
        assert r["source_status_before"] == "excluded_no_isolable_article_text"
        assert r["remediation_action"] == "create_new_internal_chinese_translation_from_arabic"
        assert r["human_legal_review_status"] == "pending_human_legal_review"


def test_no_official_binding_governing_chinese_claim():
    d = _d()
    for f in ("official_chinese_translation_claimed", "chinese_binding_claimed",
              "chinese_governing_claimed"):
        assert d[f] is False
        for r in d["records"]:
            assert r[f] is False
    blob = json.dumps(d, ensure_ascii=False).lower()
    for term in BANNED:
        assert term not in blob, term


def test_no_full_chinese_281_layer_claim():
    assert _d()["full_chinese_translation_claimed"] is False
    assert _d()["full_chinese_281_layer_created"] is False


def test_no_trilingual_alignment():
    assert _d()["trilingual_alignment_created"] is False


def test_human_legal_review_remains_pending():
    assert _d()["human_legal_review_status"] == "pending_human_legal_review"


def test_qa_status_pending_future_qa():
    for r in _d()["records"]:
        assert r["qa_status"] == "pending_future_qa"


def test_chinese_hash_correct():
    for r in _d()["records"]:
        assert r["remediated_chinese_text_hash_sha256"] == hashlib.sha256(
            r["remediated_chinese_text"].encode("utf-8")).hexdigest()


def test_arabic_hashes_match_official_source():
    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    for r in _d()["records"]:
        assert r["arabic_source_hash_sha256"] == ar[r["article_number"]]["official_text_hash_sha256"]


def test_english_hashes_match_official_source():
    en = {r["article_number"]: r for r in _read(ENGLISH)["records"]}
    for r in _d()["records"]:
        assert r["english_guidance_hash_sha256"] == en[r["article_number"]]["legal_rule_text_hash_sha256"]


def test_no_full_arabic_or_english_text_duplicated():
    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    en = {r["article_number"]: r for r in _read(ENGLISH)["records"]}
    blob = json.dumps(_d(), ensure_ascii=False)
    for n in ARTS:
        assert ar[n]["official_text_ar"] not in blob
        assert en[n]["legal_rule_text_en"] not in blob


def test_p0_001_unchanged():
    assert len(_read(P0_001)["records"]) == 20


def test_p0_002_unchanged():
    assert len(_read(P0_002)["records"]) == 20


def test_p0_002_qa_unchanged():
    qa = _read(P0_002_QA)
    assert qa["batch_id"] == "P0-002" and qa["final_status"] == "QA_PASS"


def test_p0_003_unchanged():
    assert len(_read(P0_003)["records"]) == 20


def test_p0_003_qa_unchanged():
    qa = _read(P0_003_QA)
    assert qa["batch_id"] == "P0-003" and qa["final_status"] == "QA_PASS"


def test_p0_004_unchanged():
    assert len(_read(P0_004)["records"]) == 20


def test_p0_004_qa_unchanged():
    qa = _read(P0_004_QA)
    assert qa["batch_id"] == "P0-004" and qa["final_status"] == "QA_PASS"


def test_protected_layers_unchanged():
    assert len(_read(CANDF)["records"]) == 189
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    assert len(zh) == 5 and sum(len(_read(p)["records"]) for p in zh) == 23
    assert len(_read(ARABIC)["records"]) == 281
    assert len(_read(ENGLISH)["records"]) == 281
    er = _read(os.path.join(ROOT, "data", "english_reference",
                            "companies_law_m132_1443_en_reference_001_281.json"))
    assert len(er["records"]) == 281
    c = _read(os.path.join(ROOT, "data", "official_arabic",
                           "companies_law_m132_1443_official_arabic_user_provided.json"))
    assert len(c["articles"]) == 281 and c["verification_status"] == "ingested_unverified"
    assert len(glob.glob(os.path.join(ROOT, "data", "chinese_translation_sources",
                                      "bab*_zh_source_extracted_articles_*.json"))) == 14


def test_no_p1_p2_p3_files():
    # P1-001 is the authorized first P1 batch; only p1_003+/P2/P3 dirs remain forbidden.
    later = [x for x in glob.glob(os.path.join(ROOT, "data", "chinese_remediation_batches", "p[123]_*"))
             if os.path.basename(x) not in ("p1_001", "p1_002", "p1_003", "p1_004", "p2_001")]
    assert not later


# --- rejection paths ---

def test_reject_out_of_scope_article(tmp_path):
    doc = copy.deepcopy(_d())
    doc["records"][0]["article_number"] = 999
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_duplicate_article(tmp_path):
    doc = copy.deepcopy(_d())
    doc["records"][1]["article_number"] = doc["records"][0]["article_number"]
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_wrong_bab(tmp_path):
    doc = copy.deepcopy(_d())
    doc["records"][0]["bab"] = 14  # art 188 is Bab 7
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_official_claim_true(tmp_path):
    doc = copy.deepcopy(_d())
    doc["official_chinese_translation_claimed"] = True
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_human_review_completed(tmp_path):
    doc = copy.deepcopy(_d())
    doc["human_legal_review_status"] = "complete"
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_invalid_hash(tmp_path):
    doc = copy.deepcopy(_d())
    doc["records"][0]["remediated_chinese_text_hash_sha256"] = "0" * 64
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_missing_required_field(tmp_path):
    doc = copy.deepcopy(_d())
    del doc["records"][0]["qa_status"]
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_starting_p1_p2_p3():
    # P1-001/P1-002/P1-003/P1-004 are authorized; any OTHER later batch dir (p1_005+/P2/P3) must make the validator fail.
    for name in ("p1_005", "p2_002", "p3_001"):
        p = os.path.join(ROOT, "data", "chinese_remediation_batches", name)
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
