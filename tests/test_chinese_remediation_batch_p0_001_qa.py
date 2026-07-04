"""Chinese remediation Batch P0-001 QA tests (article-by-article review vs Arabic; review only).

QA reviews the 20 remediated Chinese texts against the official Arabic (English secondary). Review
only — remediated Chinese not changed, human legal review not marked complete, no full Chinese
layer, no trilingual alignment. Hashes only (no full Arabic/English/Chinese text). Protected layers
untouched. Reads committed artifacts.
"""

import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QA = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "chinese_remediation_batch_p0_001_qa.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_REMEDIATION_BATCH_P0_001_QA_AR.md")
SRC = os.path.join(ROOT, "data", "chinese_remediation_batches", "p0_001",
                   "companies_law_m132_1443_zh_internal_remediation_p0_001.json")
ARABIC = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
ENGLISH = os.path.join(ROOT, "data", "official_english_legal_llm",
                       "companies_law_m132_1443_official_english_legal_llm_001_281.json")
CANDF = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                     "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")

ARTS = [61, 62, 63, 64, 65, 67, 68, 69, 70, 73, 74, 76, 78, 79, 80, 81, 82, 83, 84, 85]
FIDELITY = {"pass", "needs_minor_fix", "needs_major_fix", "fail"}
COMPLETE = {"complete", "minor_omissions", "material_omissions", "fail"}
DECISION = {"qa_pass_for_internal_reference_pending_human_review",
            "qa_pass_with_minor_fix_recommended", "qa_blocked_needs_revision",
            "qa_failed_needs_retranslation"}
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _qa():
    return _read(QA)


def test_output_files_exist():
    assert os.path.exists(QA) and os.path.exists(MD)


def test_exactly_20_qa_records_and_list():
    qa = _qa()
    assert qa["article_count"] == 20
    assert qa["article_numbers"] == ARTS
    assert qa["expected_babs"] == [4]
    nums = [r["article_number"] for r in qa["records"]]
    assert nums == ARTS
    assert len(set(nums)) == 20


def test_expected_bab4_only():
    for r in _qa()["records"]:
        assert r["expected_bab_number"] == 4


def test_enum_values():
    for r in _qa()["records"]:
        assert r["semantic_fidelity_rating"] in FIDELITY
        assert r["legal_completeness_rating"] in COMPLETE
        assert r["terminology_rating"] in FIDELITY
        assert r["structural_clarity_rating"] in FIDELITY
        assert r["qa_decision"] in DECISION


def test_hashes_match_source_remediation():
    src = {r["article_number"]: r for r in _read(SRC)["records"]}
    for r in _qa()["records"]:
        n = r["article_number"]
        assert r["remediated_chinese_hash_sha256"] == src[n]["remediated_chinese_text_hash_sha256"]
        assert r["arabic_source_hash_sha256"] == src[n]["arabic_source_hash_sha256"]
        assert r["english_guidance_hash_sha256"] == src[n]["english_guidance_hash_sha256"]


def test_no_full_arabic_english_chinese_text_duplicated():
    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    en = {r["article_number"]: r for r in _read(ENGLISH)["records"]}
    src = {r["article_number"]: r for r in _read(SRC)["records"]}
    blob = json.dumps(_qa(), ensure_ascii=False)
    for n in ARTS:
        assert ar[n]["official_text_ar"] not in blob
        assert en[n]["legal_rule_text_en"] not in blob
        assert src[n]["remediated_chinese_text"] not in blob


def test_trust_posture_and_no_overclaims():
    qa = _qa()
    for f in ("full_chinese_translation_claimed", "official_chinese_translation_claimed",
              "chinese_binding_claimed", "chinese_governing_claimed",
              "human_legal_review_completed",
              "full_chinese_281_layer_created", "trilingual_alignment_created"):
        assert qa[f] is False
    # remediated_chinese_changed may be true after an authorized minor-fix pass
    assert isinstance(qa["remediated_chinese_changed"], bool)
    blob = json.dumps(qa, ensure_ascii=False).lower()
    for term in BANNED:
        assert term not in blob, term


def test_source_remediation_file_unchanged():
    assert len(_read(SRC)["records"]) == 20
    assert _read(SRC)["human_legal_review_status"] == "pending_human_legal_review"


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


def test_validator_passes():
    res = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts",
                                      "validate_chinese_remediation_batch_p0_001_qa.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
