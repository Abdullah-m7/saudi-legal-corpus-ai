"""Official English guidance REFERENCE layer — Book One pilot (Articles 1–34).

Reference/alignment text only. NOT the English Legal LLM-ready layer.
"""

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "english_reference.schema.json")
DATA = os.path.join(ROOT, "data", "english_reference", "book1_en_reference.json")
JSONL = os.path.join(ROOT, "data", "english_reference", "book1_en_reference.jsonl")
EXPECTED = list(range(1, 35))


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _records():
    return _read(DATA)["records"]


# -- existence --------------------------------------------------------------
def test_schema_exists():
    assert os.path.exists(SCHEMA)
    schema = _read(SCHEMA)
    assert schema["properties"]["english_source_status"]["enum"] == ["official_guidance_translation"]


def test_data_exists():
    assert os.path.exists(DATA)


def test_jsonl_exists_and_line_count_34():
    assert os.path.exists(JSONL)
    with open(JSONL, encoding="utf-8") as fh:
        lines = [ln for ln in fh.read().splitlines() if ln.strip()]
    assert len(lines) == 34
    # each line is a valid record with an article number
    nums = [json.loads(ln)["article_number"] for ln in lines]
    assert nums == EXPECTED


# -- coverage ---------------------------------------------------------------
def test_exactly_articles_1_to_34():
    nums = [r["article_number"] for r in _records()]
    assert nums == EXPECTED


def test_no_duplicate_article_numbers():
    nums = [r["article_number"] for r in _records()]
    assert len(set(nums)) == len(nums) == 34


# -- per-record fields ------------------------------------------------------
def test_every_record_has_english_reference_text():
    for r in _records():
        assert r["english_reference_text"].strip(), r["article_number"]


def test_trust_fields():
    for r in _records():
        assert r["english_source_status"] == "official_guidance_translation", r["article_number"]
        assert r["governing_text_language"] == "ar", r["article_number"]
        assert r["manual_review_status"] == "needs_manual_check", r["article_number"]


def test_records_pass_schema():
    schema = _read(SCHEMA)
    try:
        import jsonschema
        v = jsonschema.Draft7Validator(schema)
        for r in _records():
            errs = [e.message for e in v.iter_errors(r)]
            assert not errs, (r["article_number"], errs)
    except ImportError:
        for r in _records():
            for k in schema["required"]:
                assert k in r, (r["article_number"], k)


# -- specific headings ------------------------------------------------------
def test_article1_definitions_heading():
    r = next(x for x in _records() if x["article_number"] == 1)
    assert "Definition" in r["article_heading_en"] or "Definitions" in r["article_heading_en"]


def test_article2_definition_of_a_company_heading():
    r = next(x for x in _records() if x["article_number"] == 2)
    assert "Definition of a Company" in r["article_heading_en"]


# -- no English LLM layer yet -----------------------------------------------
def test_no_english_llm_directory():
    # English Legal LLM layer started (Book Four Section 1 pilot); only that file may exist.
    _elf = glob.glob(os.path.join(ROOT, "data", "english_legal_llm", "*_en_legal_llm.json"))
    assert set(os.path.basename(p) for p in _elf) <= {"book4_section1_en_legal_llm.json", "book4_section2_en_legal_llm.json", "book4_section3_en_legal_llm.json"}, _elf


def test_no_english_llm_record_files():
    stray = glob.glob(os.path.join(ROOT, "data", "**", "*_en_legal_llm.json"), recursive=True)
    assert set(os.path.basename(p) for p in stray) <= {"book4_section1_en_legal_llm.json", "book4_section2_en_legal_llm.json", "book4_section3_en_legal_llm.json"}, stray


# -- no overclaim terms -----------------------------------------------------
def test_no_forbidden_overclaim_terms():
    blob = open(DATA, encoding="utf-8").read().lower()
    for term in ("binding english text", "governing english text",
                 "english is binding", "verified translation",
                 "binding_translation", "unofficial_translation"):
        assert term not in blob, term


# -- existing Arabic / Chinese / Arabic-LLM content untouched ---------------
def test_arabic_and_chinese_article_text_unchanged():
    checks = [
        ("book1_articles_001_034.json", list(range(1, 35))),
        ("book2_articles_035_050.json", list(range(35, 51))),
        ("book3_articles_051_057.json", list(range(51, 58))),
    ]
    for fname, expected in checks:
        doc = _read(os.path.join(ROOT, "data", "articles", fname))
        nums = [a["article_number"] for a in doc["articles"]]
        assert nums == expected, fname
        for a in doc["articles"]:
            assert a["arabic_reference_summary"].strip(), (fname, a["article_number"])
            assert a["chinese_translation"].strip(), (fname, a["article_number"])


def test_book4_provisions_unchanged():
    doc = _read(os.path.join(ROOT, "data", "articles", "book4_provisions_058_066.json"))
    assert [p["source_article_numbers"] for p in doc["provisions"]] == [[58], [59], [60], [66]]


def test_arabic_legal_llm_records_unchanged():
    # Books 1–3 backfill + Book 4 pilot still present with expected coverage.
    b1 = _read(os.path.join(ROOT, "data", "arabic_legal_llm", "book1_ar_legal_llm.json"))
    assert [r["article_numbers"][0] for r in b1["records"]] == list(range(1, 35))
    pilot = _read(os.path.join(ROOT, "data", "arabic_legal_llm", "book4_section1_ar_legal_llm.json"))
    assert sorted(r["article_numbers"][0] for r in pilot["records"]) == [58, 59, 60, 66]


# -- validator script passes ------------------------------------------------
def test_validator_script_passes():
    import subprocess
    import sys
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "validate_english_reference.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
