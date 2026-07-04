"""Full official English BOE reference alignment tests (281 articles).

Segments the official English guidance PDF into 281 per-article reference records (Articles
1..281) carrying the verbatim official English text plus mechanical retrieval metadata. Reference/
alignment layer only — English is guidance (Arabic governs); no translation, no summaries, no
English LLM-ready fields, no binding/verified overclaim. Separate from the old 87-record split
layer. Reads committed artifacts.
"""

import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "english_reference.schema.json")
DATA = os.path.join(ROOT, "data", "english_reference",
                    "companies_law_m132_1443_en_reference_001_281.json")
GEN = os.path.join(ROOT, "scripts", "gen_english_reference_full_281.py")

TARGET = 281
BANNED = ("binding english text", "governing english text", "english is binding",
          "verified translation", "binding_translation", "unofficial_translation")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _recs():
    return _read(DATA)["records"]


def test_schema_and_data_exist():
    assert os.path.exists(SCHEMA) and os.path.exists(DATA)


def test_exactly_281_records_1_to_281_no_dups():
    r = _recs()
    assert len(r) == TARGET
    nums = [x["article_number"] for x in r]
    assert nums == list(range(1, TARGET + 1))
    assert len(set(nums)) == len(nums)


def test_all_records_schema_valid():
    import jsonschema
    schema = _read(SCHEMA)
    v = jsonschema.Draft7Validator(schema)
    for r in _recs():
        errs = list(v.iter_errors(r))
        assert not errs, (r["article_number"], [e.message for e in errs][:2])


def test_reference_text_non_empty():
    for r in _recs():
        assert r["english_reference_text"].strip()


def test_trust_posture():
    for r in _recs():
        assert r["english_source_status"] == "official_guidance_translation"
        assert r["governing_text_language"] == "ar"
        assert r["manual_review_status"] == "needs_manual_check"
        assert "Bureau of Experts" in r["source"]["source_authority"]
        assert r["source"]["department"] == "Official Translation Department"
        assert r["source"]["extraction_method"] == "official_english_pdf_text_layer_segmentation"


def test_llm_block_mechanical():
    for r in _recs():
        n = r["article_number"]
        assert r["llm"]["chunk_id"] == "en-ref-companies-art-%03d" % n
        assert r["llm"]["retrieval_title_en"].startswith("Companies Law - Article %d - " % n)
        assert isinstance(r["llm"]["keywords_en"], list)


def test_no_binding_or_overclaim_terms():
    blob = json.dumps(_read(DATA), ensure_ascii=False).lower()
    for term in BANNED:
        assert term not in blob, term


def test_no_legal_rule_or_llm_ready_fields():
    blob = json.dumps(_read(DATA), ensure_ascii=False)
    assert "legal_rule_text_en" not in blob
    assert "legal_rule_summary_en" not in blob
    allowed = {"book", "article_number", "part_number_en", "part_title_en", "article_heading_en",
               "english_reference_text", "english_source_status", "governing_text_language",
               "alignment_status", "manual_review_status", "source", "llm", "risk_flags"}
    for r in _recs():
        assert set(r.keys()) == allowed


def test_generator_is_byte_stable():
    # The generator's source text needs pypdf (optional extra) or the regenerable extracted aid;
    # skip when neither is available (e.g. CI without the extract extra), matching the repo's
    # optional-dependency policy — the committed data file is the source of truth.
    import pytest
    try:
        import pypdf  # noqa: F401
        have_source = True
    except ImportError:
        have_source = os.path.exists(os.path.join(
            ROOT, "data", "extracted", "official_english_companies_law_text.txt"))
    if not have_source:
        pytest.skip("pypdf not installed and no extracted aid; generator source unavailable")
    before = open(DATA, "rb").read()
    res = subprocess.run([sys.executable, GEN], capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    after = open(DATA, "rb").read()
    assert before == after, "full English reference is not byte-stable / idempotent"


def test_consistent_with_existing_book1_text():
    # Article 1 body must match the existing 87-record split layer (same extraction policy)
    b1 = _read(os.path.join(ROOT, "data", "english_reference", "book1_en_reference.json"))
    old1 = next(r for r in b1["records"] if r["article_number"] == 1)["english_reference_text"]
    new1 = next(r for r in _recs() if r["article_number"] == 1)["english_reference_text"]
    assert old1 == new1


def test_existing_split_layer_unchanged():
    ref = os.path.join(ROOT, "data", "english_reference")
    for fname, exp in (("book1_en_reference.json", list(range(1, 35))),
                       ("book2_en_reference.json", list(range(35, 51))),
                       ("book3_en_reference.json", list(range(51, 58)))):
        recs = _read(os.path.join(ref, fname))["records"]
        assert [x["article_number"] for x in recs] == exp
    split = glob.glob(os.path.join(ref, "book*_en_reference.json"))
    assert sum(len(_read(p)["records"]) for p in split) == 87


def test_other_layers_unchanged():
    en = glob.glob(os.path.join(ROOT, "data", "english_legal_llm", "*_en_legal_llm.json"))
    assert len(en) == 8 and sum(len(_read(p)["records"]) for p in en) == 87
    oa = _read(os.path.join(ROOT, "data", "official_arabic_legal_llm",
                            "companies_law_m132_1443_official_arabic_legal_llm_001_281.json"))
    assert len(oa["records"]) == 281
    old_ar = glob.glob(os.path.join(ROOT, "data", "arabic_legal_llm", "*_ar_legal_llm.json"))
    assert len(old_ar) == 8 and sum(len(_read(p)["records"]) for p in old_ar) == 80
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    assert len(zh) == 5 and sum(len(_read(p)["records"]) for p in zh) == 23


def test_official_arabic_source_untouched():
    c = _read(os.path.join(ROOT, "data", "official_arabic",
                           "companies_law_m132_1443_official_arabic_user_provided.json"))
    assert len(c["articles"]) == 281
    assert c["verification_status"] == "ingested_unverified"


def test_validator_passes():
    res = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts",
                                      "validate_english_reference_full_281.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
