"""Chinese remediation Batch P0-001 tests (scoped internal Chinese draft, 20 Bab 4 articles).

The batch creates new internal Chinese reference text for exactly the 20 authorized P0-001 articles,
translated from the official Arabic governing text (English guidance only). Chinese is internal /
non-official / non-binding / non-governing; human legal review pending. No full Arabic/English text
is embedded; protected layers untouched. Reads committed artifacts.
"""

import glob
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "chinese_remediation_batches", "p0_001",
                    "companies_law_m132_1443_zh_internal_remediation_p0_001.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_REMEDIATION_BATCH_P0_001_AR.md")
ARABIC = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
ENGLISH = os.path.join(ROOT, "data", "official_english_legal_llm",
                       "companies_law_m132_1443_official_english_legal_llm_001_281.json")
CANDF = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                     "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")

ARTS = [61, 62, 63, 64, 65, 67, 68, 69, 70, 73, 74, 76, 78, 79, 80, 81, 82, 83, 84, 85]
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _d():
    return _read(DATA)


def test_output_files_exist():
    assert os.path.exists(DATA) and os.path.exists(MD)


def test_exactly_20_records_and_article_list():
    d = _d()
    assert d["article_count"] == 20
    assert d["article_numbers"] == ARTS
    assert d["expected_babs"] == [4]
    nums = [r["article_number"] for r in d["records"]]
    assert nums == ARTS
    assert len(set(nums)) == 20


def test_expected_bab4_only():
    for r in _d()["records"]:
        assert r["expected_bab_number"] == 4


def test_non_empty_chinese_text():
    for r in _d()["records"]:
        assert r["remediated_chinese_text"].strip()


def test_chinese_hash_correct():
    for r in _d()["records"]:
        assert r["remediated_chinese_text_hash_sha256"] == hashlib.sha256(
            r["remediated_chinese_text"].encode("utf-8")).hexdigest()


def test_arabic_source_hash_match():
    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    for r in _d()["records"]:
        assert r["arabic_source_hash_sha256"] == ar[r["article_number"]]["official_text_hash_sha256"]


def test_english_guidance_hash_match():
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


def test_trust_posture_and_no_overclaims():
    d = _d()
    for f in ("official_chinese_translation_claimed", "chinese_binding_claimed",
              "chinese_governing_claimed", "full_chinese_translation_claimed"):
        assert d[f] is False
    assert d["batch_scope_only"] is True
    assert d["human_legal_review_status"] == "pending_human_legal_review"
    for r in d["records"]:
        assert r["translation_basis"] == "official_arabic_governing_text"
        assert r["english_guidance_role"] == "secondary_guidance_only"
        assert r["remediation_action"] == "create_new_internal_chinese_translation_from_arabic"
        assert r["source_status_before_remediation"] == "excluded_no_isolable_article_text"
        assert r["official_translation"] is False
        assert r["not_binding"] is True
        assert r["not_governing"] is True
        assert r["internal_reference_only"] is True
        assert r["full_translation_claimed"] is False
        assert r["human_legal_review_status"] == "pending_human_legal_review"
    blob = json.dumps(d, ensure_ascii=False).lower()
    for term in BANNED:
        assert term not in blob, term


def test_no_out_of_scope_articles():
    d = _d()
    assert set(r["article_number"] for r in d["records"]) == set(ARTS)


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
                                      "validate_chinese_remediation_batch_p0_001.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
