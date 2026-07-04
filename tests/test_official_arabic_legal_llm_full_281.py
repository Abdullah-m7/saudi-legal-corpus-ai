"""Full official Arabic Legal LLM-ready layer tests (281 articles).

The layer carries the EXACT official_text_ar from the ingested BOE owner-provided candidate
(verbatim, hash-checked) plus mechanical retrieval metadata only — no summaries, no analysis, no
OCR/English/Chinese text. Separate from the old data/arabic_legal_llm/ summary layer. Reads
committed artifacts.
"""

import glob
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                    "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
SCHEMA = os.path.join(ROOT, "schemas", "official_arabic_legal_llm.schema.json")
SRC = os.path.join(ROOT, "data", "official_arabic",
                   "companies_law_m132_1443_official_arabic_user_provided.json")
GEN = os.path.join(ROOT, "scripts", "gen_official_arabic_legal_llm_full_281.py")

TARGET = 281


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _recs():
    return _read(DATA)["records"]


def _src_by():
    return {a["article_number"]: a for a in _read(SRC)["articles"]}


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
        assert r["record_type"] == "official_arabic_article"
        assert r["language"] == "ar"
        assert r["governing_text_language"] == "ar"


def test_official_text_and_hash_exact_vs_source():
    src = _src_by()
    for r in _recs():
        a = src[r["article_number"]]
        assert r["official_text_ar"] == a["official_text_ar"]
        assert r["official_text_hash_sha256"] == _sha256(a["official_text_ar"])
        assert r["article_title_ar"] == a["article_title_ar"]


def test_mechanical_metadata_present():
    for r in _recs():
        n = r["article_number"]
        assert r["article_path"] == "companies_law/articles/%03d" % n
        assert str(n) in r["llm_title_ar"] and r["article_title_ar"] in r["llm_title_ar"]
        assert r["article_title_ar"] in r["retrieval_title_ar"]
        assert isinstance(r["keywords_ar"], list)
        assert isinstance(r["search_queries_ar"], list) and r["search_queries_ar"]
        assert ("المادة %d نظام الشركات" % n) in r["search_queries_ar"]


def test_no_summary_or_analysis_fields():
    blob = json.dumps(_recs(), ensure_ascii=False)
    assert "legal_rule_summary_ar" not in blob
    for r in _recs():
        for k in r:
            assert "summary" not in k.lower()
            assert "legal_rule" not in k.lower()


def test_no_ocr_english_chinese_text_fields():
    for r in _recs():
        keys = json.dumps(list(r.keys()) + list(r["source_trust"].keys()))
        # ocr_role (trust label) is allowed; OCR *text* / snippet fields are not
        assert "ocr_text" not in keys and "ocr_snippet" not in keys and "snippet" not in keys
        for k in list(r.keys()) + list(r["source_trust"].keys()):
            kl = k.lower()
            assert not kl.endswith("_en") and not kl.endswith("_zh")
            assert "english" not in kl and "chinese" not in kl


def test_source_trust_boe_posture():
    for r in _recs():
        st = r["source_trust"]
        assert st["source_authority"] == "Bureau of Experts at the Council of Ministers"
        assert st["source_authority_ar"] == "هيئة الخبراء بمجلس الوزراء"
        assert st["source_status"] == "owner_provided_from_official_boe_source"
        assert st["source_packet_status"] == "official_boe_owner_provided"
        assert st["controlling_source_basis"] == "owner_provided_boe_text_plus_pdf_packet"
        assert st["ocr_role"] == "supporting_artifact_only_not_controlling_gate"
        assert st["text_type"] == "official_arabic_statutory_text"
        assert st["article_by_article_verified"] is False
        assert st["verification_status"] == \
            "official_boe_source_packet_owner_provided_not_live_html_verified"


def test_nothing_verified():
    blob = json.dumps(_read(DATA), ensure_ascii=False)
    assert "verified_against_official_gazette" not in blob
    for r in _recs():
        assert r["source_trust"]["article_by_article_verified"] is False


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
    assert before == after, "full LLM-ready layer is not byte-stable / idempotent"


def test_candidate_source_untouched():
    c = _read(SRC)
    assert len(c["articles"]) == TARGET
    assert c["verification_status"] == "ingested_unverified"
    assert c["article_by_article_verified"] is False
    for a in c["articles"]:
        assert a["verification_status"] == "ingested_unverified"


def test_existing_layers_unchanged():
    old = glob.glob(os.path.join(ROOT, "data", "arabic_legal_llm", "*_ar_legal_llm.json"))
    assert len(old) == 8 and sum(len(_read(p)["records"]) for p in old) == 80
    en = glob.glob(os.path.join(ROOT, "data", "english_legal_llm", "*_en_legal_llm.json"))
    assert len(en) == 8 and sum(len(_read(p)["records"]) for p in en) == 87
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    assert len(zh) == 5 and sum(len(_read(p)["records"]) for p in zh) == 23


def test_validator_passes():
    res = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts",
                                      "validate_official_arabic_legal_llm_full_281.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
