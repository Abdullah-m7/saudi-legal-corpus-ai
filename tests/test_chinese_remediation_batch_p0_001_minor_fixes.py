"""Chinese remediation Batch P0-001 minor-fixes tests (Articles 61 & 74 terminology only).

Applies the two QA-approved terminology fixes to Articles 61 and 74 only, refreshes their hashes/QA,
and records the change in a minor-fixes report. No other article changed; human legal review stays
pending; no full Chinese layer; no trilingual alignment. Reads committed artifacts.
"""

import glob
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RV = os.path.join(ROOT, "reports", "chinese_translation_review")
BATCH = os.path.join(ROOT, "data", "chinese_remediation_batches", "p0_001",
                     "companies_law_m132_1443_zh_internal_remediation_p0_001.json")
QA = os.path.join(RV, "chinese_remediation_batch_p0_001_qa.json")
MF = os.path.join(RV, "chinese_remediation_batch_p0_001_minor_fixes.json")
MD = os.path.join(RV, "CHINESE_REMEDIATION_BATCH_P0_001_MINOR_FIXES_AR.md")
ARABIC = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
ENGLISH = os.path.join(ROOT, "data", "official_english_legal_llm",
                       "companies_law_m132_1443_official_english_legal_llm_001_281.json")
CANDF = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                     "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")

ARTS = [61, 62, 63, 64, 65, 67, 68, 69, 70, 73, 74, 76, 78, 79, 80, 81, 82, 83, 84, 85]
FIXED = [61, 74]
PASS_DECISION = "qa_pass_for_internal_reference_pending_human_review"
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def test_output_files_exist():
    for p in (BATCH, QA, MF, MD):
        assert os.path.exists(p), p


def test_only_61_and_74_fixed():
    mf = _read(MF)
    assert mf["fixed_articles"] == FIXED
    assert mf["article_count"] == 2
    assert {r["article_number"] for r in mf["records"]} == set(FIXED)
    for r in mf["records"]:
        assert r["previous_chinese_hash_sha256"] != r["new_chinese_hash_sha256"]
        assert r["qa_new_decision"] == PASS_DECISION


def test_scope_remains_20_no_out_of_scope():
    batch = _read(BATCH)
    assert len(batch["records"]) == 20
    assert [r["article_number"] for r in batch["records"]] == ARTS
    assert batch["article_numbers"] == ARTS


def test_hash_correctness_for_61_and_74():
    b = {r["article_number"]: r for r in _read(BATCH)["records"]}
    mf = {r["article_number"]: r for r in _read(MF)["records"]}
    for n in FIXED:
        assert b[n]["remediated_chinese_text_hash_sha256"] == hashlib.sha256(
            b[n]["remediated_chinese_text"].encode("utf-8")).hexdigest()
        assert mf[n]["new_chinese_hash_sha256"] == b[n]["remediated_chinese_text_hash_sha256"]


def test_arabic_english_hashes_unchanged():
    b = {r["article_number"]: r for r in _read(BATCH)["records"]}
    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    en = {r["article_number"]: r for r in _read(ENGLISH)["records"]}
    for n in ARTS:
        assert b[n]["arabic_source_hash_sha256"] == ar[n]["official_text_hash_sha256"]
        assert b[n]["english_guidance_hash_sha256"] == en[n]["legal_rule_text_hash_sha256"]


def test_qa_summary_all_pass():
    qa = _read(QA)
    s = qa["qa_summary"]
    assert s["pass_count"] == 20
    assert s["minor_fix_count"] == 0
    assert s["blocked_count"] == 0
    assert s["failed_count"] == 0
    q = {r["article_number"]: r for r in qa["records"]}
    for n in FIXED:
        assert q[n]["qa_decision"] == PASS_DECISION
        assert q[n]["terminology_rating"] == "pass"


def test_human_legal_review_remains_pending():
    assert _read(BATCH)["human_legal_review_status"] == "pending_human_legal_review"
    assert _read(QA)["human_legal_review_completed"] is False
    assert _read(MF)["human_legal_review_completed"] is False


def test_no_full_chinese_layer_or_alignment():
    for doc in (_read(QA), _read(MF)):
        assert doc["full_chinese_281_layer_created"] is False
        assert doc["trilingual_alignment_created"] is False


def test_no_full_arabic_english_chinese_text_in_qa_or_minor_fixes():
    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    en = {r["article_number"]: r for r in _read(ENGLISH)["records"]}
    b = {r["article_number"]: r for r in _read(BATCH)["records"]}
    for doc in (_read(QA), _read(MF)):
        blob = json.dumps(doc, ensure_ascii=False)
        for n in ARTS:
            assert ar[n]["official_text_ar"] not in blob
            assert en[n]["legal_rule_text_en"] not in blob
            assert b[n]["remediated_chinese_text"] not in blob
        low = blob.lower()
        for term in BANNED:
            assert term not in low, term


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
                                      "validate_chinese_remediation_batch_p0_001_minor_fixes.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
