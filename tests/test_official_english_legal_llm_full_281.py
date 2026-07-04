"""Full official English Legal LLM-ready layer tests (281 articles).

The layer carries the EXACT english_reference_text from the full English reference alignment
(verbatim, hash-checked) as legal_rule_text_en, plus mechanical retrieval metadata only — no
summaries, no analysis, no Arabic-rewrite / Chinese / OCR text, no binding/governing overclaim.
English is guidance only; Arabic governs. Separate from the old 87-record English LLM layer.
Reads committed artifacts.
"""

import glob
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "official_english_legal_llm.schema.json")
DATA = os.path.join(ROOT, "data", "official_english_legal_llm",
                    "companies_law_m132_1443_official_english_legal_llm_001_281.json")
REF = os.path.join(ROOT, "data", "english_reference",
                   "companies_law_m132_1443_en_reference_001_281.json")
GEN = os.path.join(ROOT, "scripts", "gen_official_english_legal_llm_full_281.py")

TARGET = 281
BANNED = ("binding english text", "governing english text", "english is binding",
          "binding_translation", "verified translation", "unofficial_translation")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _recs():
    return _read(DATA)["records"]


def _ref_by():
    return {r["article_number"]: r for r in _read(REF)["records"]}


def _sha256(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def test_schema_and_data_exist():
    assert os.path.exists(SCHEMA) and os.path.exists(DATA)


def test_exactly_281_records_1_to_281():
    r = _recs()
    assert len(r) == TARGET
    assert [x["article_number"] for x in r] == list(range(1, TARGET + 1))


def test_record_type_language_governing():
    for r in _recs():
        assert r["record_type"] == "official_english_guidance_article"
        assert r["language"] == "en"
        assert r["governing_text_language"] == "ar"


def test_legal_rule_text_and_hash_exact_vs_reference():
    ref = _ref_by()
    for r in _recs():
        sr = ref[r["article_number"]]
        assert r["legal_rule_text_en"] == sr["english_reference_text"]
        assert r["legal_rule_text_hash_sha256"] == _sha256(sr["english_reference_text"])
        assert r["article_heading_en"] == sr["article_heading_en"]


def test_mechanical_metadata():
    for r in _recs():
        n = r["article_number"]
        assert r["record_id"] == "oe-llm-companies-art-%03d" % n
        assert r["article_path"] == "companies_law/articles/%03d/en" % n
        assert str(n) in r["llm_title_en"] and r["article_heading_en"] in r["llm_title_en"]
        assert r["article_heading_en"] in r["retrieval_title_en"]
        assert isinstance(r["keywords_en"], list)
        assert isinstance(r["search_queries_en"], list) and r["search_queries_en"]
        assert ("Companies Law Article %d" % n) in r["search_queries_en"]


def test_keywords_reused_from_reference():
    ref = _ref_by()
    for r in _recs():
        assert r["keywords_en"] == ref[r["article_number"]]["llm"]["keywords_en"]


def test_no_summary_or_translation_or_foreign_fields():
    blob = json.dumps(_recs(), ensure_ascii=False)
    assert "legal_rule_summary_en" not in blob
    for r in _recs():
        for k in list(r.keys()) + list(r["source_trust"].keys()):
            kl = k.lower()
            assert "summary" not in kl
            assert "_zh" not in kl and "chinese" not in kl
            assert "official_text_ar" not in kl and "arabic" not in kl
            assert "ocr_text" not in kl and "ocr_snippet" not in kl and "snippet" not in kl


def test_trust_posture_guidance_only():
    for r in _recs():
        st = r["source_trust"]
        assert st["english_source_status"] == "official_guidance_translation"
        assert st["source_authority"] == "Bureau of Experts at the Council of Ministers"
        assert st["department"] == "Official Translation Department"
        assert st["source_file"] == "inputs/companies_law_official_english_guidance.pdf"
        assert st["source_reference_file"] == \
            "data/english_reference/companies_law_m132_1443_en_reference_001_281.json"
        assert st["governing_text_language"] == "ar"
        assert st["manual_review_status"] == "needs_manual_check"
        assert st["guidance_note"] == \
            "This translation is provided for guidance. The governing text is the Arabic text."
        assert st["binding_status"] == "guidance_only_not_binding"


def test_no_binding_or_governing_overclaim():
    blob = json.dumps(_read(DATA), ensure_ascii=False).lower()
    for term in BANNED:
        assert term not in blob, term


def test_schema_validates_records():
    import jsonschema
    schema = _read(SCHEMA)
    v = jsonschema.Draft7Validator(schema)
    for r in _recs():
        errs = list(v.iter_errors(r))
        assert not errs, (r["article_number"], [e.message for e in errs][:2])


def test_generator_is_byte_stable():
    before = open(DATA, "rb").read()
    res = subprocess.run([sys.executable, GEN], capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    after = open(DATA, "rb").read()
    assert before == after, "full English LLM-ready layer is not byte-stable / idempotent"


def test_reference_and_other_layers_unchanged():
    assert len(_read(REF)["records"]) == TARGET
    oa = _read(os.path.join(ROOT, "data", "official_arabic_legal_llm",
                            "companies_law_m132_1443_official_arabic_legal_llm_001_281.json"))
    assert len(oa["records"]) == TARGET
    old_en = glob.glob(os.path.join(ROOT, "data", "english_legal_llm", "*_en_legal_llm.json"))
    assert len(old_en) == 8 and sum(len(_read(p)["records"]) for p in old_en) == 87
    old_ar = glob.glob(os.path.join(ROOT, "data", "arabic_legal_llm", "*_ar_legal_llm.json"))
    assert len(old_ar) == 8 and sum(len(_read(p)["records"]) for p in old_ar) == 80
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    assert len(zh) == 5 and sum(len(_read(p)["records"]) for p in zh) == 23
    split = glob.glob(os.path.join(ROOT, "data", "english_reference", "book*_en_reference.json"))
    assert sum(len(_read(p)["records"]) for p in split) == 87


def test_official_arabic_source_untouched():
    c = _read(os.path.join(ROOT, "data", "official_arabic",
                           "companies_law_m132_1443_official_arabic_user_provided.json"))
    assert len(c["articles"]) == TARGET
    assert c["verification_status"] == "ingested_unverified"


def test_validator_passes():
    res = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts",
                                      "validate_official_english_legal_llm_full_281.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
