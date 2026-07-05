"""Chinese remediation Batch P1-003 tests (P1 retranslation batch; 20 articles, Babs 6/7/8/10).

P1 track = retranslation / manual review: the batch carries fresh internal Chinese retranslated from
the official Arabic governing text (English guidance only) for exactly the 20 authorized P1-003
articles, because the prior internal Chinese candidate for these articles was materially incomplete /
condensed (all 20 are priority P1 in the semantic-QA report). Each record's bab must match the
official coverage-index expected_bab_number and link to the (unchanged) prior candidate record and its
P1 finding. Chinese is internal / non-official / non-binding / non-governing under the repository
review model (official Arabic governs; repository-owner review active / bachelor_of_law; external
review optional and not required for repository use); qa_status pending_future_qa. No full
Arabic/English text embedded; all P0 batches + QA, P1-001 (+ QA), P1-002 (+ QA) and base layers
untouched; no other P1/P2/P3 dirs. Reads committed artifacts and exercises the validator's rejection
paths.
"""

import copy
import glob
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "chinese_remediation_batches", "p1_003",
                    "companies_law_m132_1443_zh_internal_remediation_p1_003.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_REMEDIATION_BATCH_P1_003_AR.md")
ARABIC = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
ENGLISH = os.path.join(ROOT, "data", "official_english_legal_llm",
                       "companies_law_m132_1443_official_english_legal_llm_001_281.json")
COV = os.path.join(ROOT, "reports", "chinese_translation_review",
                   "chinese_article_coverage_index_001_281.json")
CANDF = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                     "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")
QA189 = os.path.join(ROOT, "reports", "chinese_translation_review",
                     "chinese_internal_llm_semantic_qa_189.json")
VALIDATOR = os.path.join(ROOT, "scripts", "validate_chinese_remediation_batch_p1_003.py")

ARTS = [166, 170, 172, 174, 176, 178, 183, 185, 200, 201, 205, 206, 207, 211, 212, 213, 221, 222, 225, 227]
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")

P0_BATCHES = {
    "P0-001": "p0_001/companies_law_m132_1443_zh_internal_remediation_p0_001.json",
    "P0-002": "p0_002/companies_law_m132_1443_zh_internal_remediation_p0_002.json",
    "P0-003": "p0_003/companies_law_m132_1443_zh_internal_remediation_p0_003.json",
    "P0-004": "p0_004/companies_law_m132_1443_zh_internal_remediation_p0_004.json",
    "P0-005": "p0_005/companies_law_m132_1443_zh_internal_remediation_p0_005.json",
}


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
    p = tmp_path / "p1_003_mutated.json"
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
    assert _d()["expected_babs"] == [6, 7, 8, 10]


def test_expected_bab_distribution():
    cov = _cov()
    dist = {}
    for r in _d()["records"]:
        dist.setdefault(r["bab"], []).append(r["article_number"])
    assert dist == {6: [166, 170, 172, 174, 176, 178, 183], 7: [185],
                    8: [200, 201, 205, 206, 207, 211, 212, 213], 10: [221, 222, 225, 227]}


def test_exact_record_count():
    assert _d()["article_count"] == 20
    assert len(_d()["records"]) == 20


def test_no_duplicate_articles():
    nums = [r["article_number"] for r in _d()["records"]]
    assert len(set(nums)) == 20


def test_no_out_of_scope_articles():
    assert set(r["article_number"] for r in _d()["records"]) == set(ARTS)


def test_priority_and_track():
    d = _d()
    assert d["priority"] == "P1"
    assert d["remediation_track"] == "P1_retranslation_or_manual_review"
    assert d["first_p1_batch"] is False


def test_each_record_bab_in_range():
    for r in _d()["records"]:
        assert r["bab"] in (6, 7, 8, 10)


def test_each_record_bab_matches_coverage_index():
    cov = _cov()
    for r in _d()["records"]:
        assert r["bab"] == cov[r["article_number"]]["expected_bab_number"]


def test_posture_flags_correct():
    d = _d()
    assert d["internal_reference_only"] is True
    for r in d["records"]:
        assert r["internal_reference_only"] is True
        assert r["translation_basis"] == "official_arabic_governing_text"
        assert r["english_guidance_role"] == "secondary_guidance_only"
        assert r["remediation_action"] == "retranslate_internal_chinese_from_arabic"
        assert r["qa_status"] == "pending_future_qa"


def test_repository_review_model():
    d = _d()
    assert d["source_basis"] == "official_source_based"
    rlr = d["repository_legal_review"]
    assert rlr["repository_owner_has_legal_background"] is True
    assert rlr["repository_owner_legal_qualification"] == "bachelor_of_law"
    assert rlr["repository_legal_review_status"] == "repository_owner_review_active"
    elr = d["external_legal_review"]
    assert elr["external_legal_review_required_for_repository_use"] is False
    assert elr["external_legal_review_optional_for_enterprise_or_official_adoption"] is True
    assert elr["external_legal_review_status"] == "not_performed"
    for r in d["records"]:
        assert r["source_basis"] == "official_source_based"
        assert r["repository_legal_review_status"] == "repository_owner_review_active"
        assert r["external_legal_review_status"] == "not_performed"


def test_official_status_boundaries():
    ofs = _d()["official_status"]
    for f in ("official_government_publication", "official_translation_claimed",
              "official_adoption_claimed", "chinese_official", "chinese_binding",
              "chinese_governing"):
        assert ofs[f] is False
    assert ofs["not_legal_advice"] is True


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


def test_prior_candidate_link_matches_unchanged_candidate():
    cand = {r["article_number"]: r for r in _read(CANDF)["records"]}
    for r in _d()["records"]:
        c = cand[r["article_number"]]
        assert r["prior_candidate_hash_sha256"] == c["chinese_text_hash_sha256"]
        assert r["prior_candidate_record_id"] == c["record_id"]


def test_all_scope_articles_are_p1_in_semantic_qa():
    qa = {r["article_number"]: r for r in _read(QA189)["records"]}
    for r in _d()["records"]:
        assert qa[r["article_number"]]["priority"] == "P1"
        assert r["qa_priority"] == "P1"
        assert r["qa_recommended_action"] == qa[r["article_number"]]["recommended_action"]


def test_no_full_arabic_or_english_text_duplicated():
    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    en = {r["article_number"]: r for r in _read(ENGLISH)["records"]}
    blob = json.dumps(_d(), ensure_ascii=False)
    for n in ARTS:
        assert ar[n]["official_text_ar"] not in blob
        assert en[n]["legal_rule_text_en"] not in blob


def test_all_p0_batches_unchanged():
    for label, rel in P0_BATCHES.items():
        recs = _read(os.path.join(ROOT, "data", "chinese_remediation_batches", rel))["records"]
        assert len(recs) in (12, 20), label


def test_p0_and_earlier_p1_qa_unchanged():
    for fn in ("chinese_remediation_batch_p0_002_qa.json", "chinese_remediation_batch_p0_003_qa.json",
               "chinese_remediation_batch_p0_004_qa.json", "chinese_remediation_batch_p0_005_qa.json",
               "chinese_remediation_batch_p1_001_qa.json", "chinese_remediation_batch_p1_002_qa.json"):
        qa = _read(os.path.join(ROOT, "reports", "chinese_translation_review", fn))
        assert qa["final_status"] == "QA_PASS"


def test_p1_001_and_p1_002_data_unchanged():
    for sub in ("p1_001", "p1_002"):
        p = os.path.join(ROOT, "data", "chinese_remediation_batches", sub,
                         "companies_law_m132_1443_zh_internal_remediation_%s.json" % sub)
        assert len(_read(p)["records"]) == 20


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


def test_only_p1_001_002_003_authorized_no_other_p1_p2_p3():
    later = [x for x in glob.glob(os.path.join(ROOT, "data", "chinese_remediation_batches", "p[123]_*"))
             if os.path.basename(x) not in ("p1_001", "p1_002", "p1_003", "p1_004")]
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
    doc["records"][0]["bab"] = 7  # art 166 is Bab 6
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_official_claim_true(tmp_path):
    doc = copy.deepcopy(_d())
    doc["official_chinese_translation_claimed"] = True
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_chinese_hash_tamper(tmp_path):
    doc = copy.deepcopy(_d())
    doc["records"][0]["remediated_chinese_text"] = doc["records"][0]["remediated_chinese_text"] + "X"
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_broken_prior_candidate_link(tmp_path):
    doc = copy.deepcopy(_d())
    doc["records"][0]["prior_candidate_hash_sha256"] = "0" * 64
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_external_review_required(tmp_path):
    doc = copy.deepcopy(_d())
    doc["external_legal_review"]["external_legal_review_required_for_repository_use"] = True
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0
