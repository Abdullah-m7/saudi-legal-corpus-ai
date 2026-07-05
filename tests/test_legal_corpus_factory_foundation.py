"""Tests for the sovereign legal corpus factory FOUNDATION (docs, schemas, profile, config, seed).

Foundation only: reusable doctrine, architecture, schemas, a Saudi Companies Law profile, one example
P0-005 QA batch config, and a seed terminology bank. Arabic governs; Chinese is internal reference
only; human legal review pending; no full Chinese 281 layer; no trilingual alignment; no P1/P2/P3.
Reads committed artifacts.
"""

import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCTRINE = os.path.join(ROOT, "docs", "SOVEREIGN_LEGAL_CORPUS_FACTORY_DOCTRINE_AR.md")
ARCH = os.path.join(ROOT, "docs", "LEGAL_CORPUS_FACTORY_ARCHITECTURE_AR.md")
SCHEMA_DIR = os.path.join(ROOT, "schemas", "legal_corpus_factory")
PROFILE = os.path.join(ROOT, "data", "legal_corpus_factory", "law_profiles",
                       "sa_companies_law_m132_1443.profile.json")
BATCH = os.path.join(ROOT, "data", "legal_corpus_factory", "batch_configs",
                     "sa_companies_law_m132_1443_p0_005_qa.batch.json")
TERMS = os.path.join(ROOT, "data", "legal_corpus_factory", "terminology",
                     "sa_companies_law_core_terms_ar_en_zh_seed.json")
P0_005_QA = os.path.join(ROOT, "reports", "chinese_translation_review",
                         "chinese_remediation_batch_p0_005_qa.json")
VALIDATOR = os.path.join(ROOT, "scripts", "validate_legal_corpus_factory_foundation.py")

ARTS = [188, 189, 190, 191, 192, 194, 218, 220, 260, 261, 262, 274]
DIST = {"7": [188, 189, 190, 191, 192, 194], "9": [218], "10": [220],
        "13": [260, 261, 262], "14": [274]}
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _rc(p):
    return len(_read(p)["records"])


def _run():
    return subprocess.run([sys.executable, VALIDATOR], capture_output=True, text=True)


def test_validator_passes():
    res = _run()
    assert res.returncode == 0, res.stdout + res.stderr


def test_law_profile_exists_and_parses():
    assert os.path.exists(PROFILE)
    prof = _read(PROFILE)
    assert prof["law_id"] == "sa_companies_law_m132_1443"
    assert prof["governing_language"] == "ar"


def test_law_profile_counts_match_repository():
    prof = _read(PROFILE)
    assert prof["article_count"] == 281
    assert _rc(os.path.join(ROOT, "data", "official_arabic_legal_llm",
                            "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")) == 281
    assert _rc(os.path.join(ROOT, "data", "official_english_legal_llm",
                            "companies_law_m132_1443_official_english_legal_llm_001_281.json")) == 281
    assert _rc(os.path.join(ROOT, "data", "english_reference",
                            "companies_law_m132_1443_en_reference_001_281.json")) == 281
    assert _rc(os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                            "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")) == 189
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    assert len(zh) == 5 and sum(_rc(x) for x in zh) == 23
    assert len(glob.glob(os.path.join(ROOT, "data", "chinese_translation_sources",
                                      "bab*_zh_source_extracted_articles_*.json"))) == 14
    sf = prof["source_files"]
    assert sf["arabic_full_llm"]["records"] == 281
    assert sf["english_full_llm"]["records"] == 281
    assert sf["english_reference"]["records"] == 281
    assert sf["chinese_internal_candidate_isolable"]["records"] == 189
    assert sf["old_chinese_legal_llm"]["files"] == 5 and sf["old_chinese_legal_llm"]["records"] == 23
    assert sf["chinese_source_extracted"]["files"] == 14
    assert sf["ocr_manual_review_queue"]["entries"] == 281


def test_law_profile_does_not_overclaim_chinese():
    prof = _read(PROFILE)
    claims = prof["claims"]
    assert claims["full_chinese_281_layer_created"] is False
    assert claims["official_chinese_translation_claimed"] is False
    assert claims["chinese_binding_claimed"] is False
    assert claims["chinese_governing_claimed"] is False
    assert claims["trilingual_alignment_created"] is False
    lh = prof["legal_hierarchy"]
    assert lh["arabic"] == "governing"
    assert lh["chinese"] == "internal_reference_only"
    assert lh["chinese_official"] is False
    assert lh["chinese_binding"] is False
    assert lh["chinese_governing"] is False
    blob = json.dumps(prof, ensure_ascii=False).lower()
    for term in BANNED:
        assert term not in blob, term


def test_law_profile_keeps_human_review_pending():
    prof = _read(PROFILE)
    assert prof["review_policy"]["human_legal_review_status"] == "pending_human_legal_review"
    assert prof["review_policy"]["human_legal_review_completed"] is False
    assert prof["release_policy"]["public_release_created"] is False


def test_batch_config_matches_existing_qa_scope():
    bc = _read(BATCH)
    qa = _read(P0_005_QA)
    assert bc["batch_id"] == "P0-005"
    assert bc["stage"] == "CHINESE_REMEDIATION_BATCH_P0_005_QA"
    assert bc["scope_articles"] == ARTS == qa["scope_articles"]


def test_batch_config_babs_and_distribution_match_existing_qa():
    bc = _read(BATCH)
    qa = _read(P0_005_QA)
    assert bc["expected_babs"] == [7, 9, 10, 13, 14] == qa["expected_babs"]
    bc_dist = {str(k): list(v) for k, v in bc["expected_bab_distribution"].items()}
    qa_dist = {str(k): list(v) for k, v in qa["expected_bab_distribution"].items()}
    assert bc_dist == DIST == qa_dist


def test_terminology_seed_entries_have_required_fields_and_pending_status():
    terms = _read(TERMS)["terms"]
    assert len(terms) >= 20
    for t in terms:
        for f in ("term_ar", "term_en", "term_zh", "domain_context", "notes_ar", "status"):
            assert f in t, (f, t.get("term_ar"))
        assert t["status"] == "seed_pending_human_legal_review"


def test_schemas_exist_and_parse():
    for name in ("law_profile.schema.json", "batch_config.schema.json",
                 "provenance_passport.schema.json"):
        sc = _read(os.path.join(SCHEMA_DIR, name))
        assert sc["type"] == "object"
        assert "properties" in sc and "required" in sc


def test_doctrine_exists_and_contains_arabic_governing_principle():
    assert os.path.exists(DOCTRINE)
    with open(DOCTRINE, encoding="utf-8") as fh:
        text = fh.read()
    assert "العربية هي النص القانوني الحاكم" in text


def test_doctrine_contains_no_false_official_chinese_claim():
    with open(DOCTRINE, encoding="utf-8") as fh:
        low = fh.read().lower()
    for term in BANNED:
        assert term not in low, term


def test_architecture_exists_and_describes_reusable_components():
    assert os.path.exists(ARCH)
    with open(ARCH, encoding="utf-8") as fh:
        text = fh.read()
    for comp in ("ملف تعريف النظام", "إعداد الدفعة", "جواز مصدر المادة", "بنك المصطلحات",
                 "طابور المراجعة البشرية"):
        assert comp in text, comp


def test_no_p1_p2_p3_dirs():
    assert not glob.glob(os.path.join(ROOT, "data", "chinese_remediation_batches", "p[123]_*"))


def test_no_full_chinese_281_layer():
    prof = _read(PROFILE)
    assert prof["claims"]["full_chinese_281_layer_created"] is False
    assert not glob.glob(os.path.join(ROOT, "data", "**", "*full_chinese_281*"), recursive=True)


def test_no_trilingual_alignment():
    prof = _read(PROFILE)
    assert prof["claims"]["trilingual_alignment_created"] is False
    assert not glob.glob(os.path.join(ROOT, "data", "**", "*trilingual*"), recursive=True)
    assert not glob.glob(os.path.join(ROOT, "reports", "**", "*trilingual*"), recursive=True)


def test_validator_idempotent():
    a = _run()
    b = _run()
    assert a.returncode == 0 and b.returncode == 0
