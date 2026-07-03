"""Official English guidance REFERENCE layer — Books Two and Three.

Reference/alignment text only. NOT the English Legal LLM-ready layer.
"""

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "english_reference.schema.json")
REF = os.path.join(ROOT, "data", "english_reference")

BOOK1 = os.path.join(REF, "book1_en_reference.json")
BOOK2 = os.path.join(REF, "book2_en_reference.json")
BOOK3 = os.path.join(REF, "book3_en_reference.json")
BOOK2_JSONL = os.path.join(REF, "book2_en_reference.jsonl")
BOOK3_JSONL = os.path.join(REF, "book3_en_reference.jsonl")

EXP2 = list(range(35, 51))
EXP3 = list(range(51, 58))


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _records(path):
    return _read(path)["records"]


def _jsonl_nums(path):
    with open(path, encoding="utf-8") as fh:
        lines = [ln for ln in fh.read().splitlines() if ln.strip()]
    return [json.loads(ln)["article_number"] for ln in lines]


# -- existence + counts -----------------------------------------------------
def test_book2_exists():
    assert os.path.exists(BOOK2)


def test_book2_jsonl_line_count_16():
    assert os.path.exists(BOOK2_JSONL)
    assert _jsonl_nums(BOOK2_JSONL) == EXP2
    assert len(_jsonl_nums(BOOK2_JSONL)) == 16


def test_book2_articles_35_to_50():
    assert [r["article_number"] for r in _records(BOOK2)] == EXP2


def test_book3_exists():
    assert os.path.exists(BOOK3)


def test_book3_jsonl_line_count_7():
    assert os.path.exists(BOOK3_JSONL)
    assert _jsonl_nums(BOOK3_JSONL) == EXP3
    assert len(_jsonl_nums(BOOK3_JSONL)) == 7


def test_book3_articles_51_to_57():
    assert [r["article_number"] for r in _records(BOOK3)] == EXP3


def test_no_duplicates():
    for path in (BOOK2, BOOK3):
        nums = [r["article_number"] for r in _records(path)]
        assert len(set(nums)) == len(nums)


# -- per-record fields ------------------------------------------------------
def test_every_record_has_english_reference_text():
    for path in (BOOK2, BOOK3):
        for r in _records(path):
            assert r["english_reference_text"].strip(), (path, r["article_number"])


def test_trust_fields():
    for path in (BOOK2, BOOK3):
        for r in _records(path):
            assert r["english_source_status"] == "official_guidance_translation", r["article_number"]
            assert r["governing_text_language"] == "ar", r["article_number"]
            assert r["manual_review_status"] == "needs_manual_check", r["article_number"]


def test_records_pass_schema():
    schema = _read(SCHEMA)
    try:
        import jsonschema
        v = jsonschema.Draft7Validator(schema)
        for path in (BOOK2, BOOK3):
            for r in _records(path):
                errs = [e.message for e in v.iter_errors(r)]
                assert not errs, (r["article_number"], errs)
    except ImportError:
        for path in (BOOK2, BOOK3):
            for r in _records(path):
                for k in schema["required"]:
                    assert k in r, (r["article_number"], k)


# -- part-specific headings -------------------------------------------------
def test_book2_mentions_general_partnership():
    doc = _read(BOOK2)
    assert "General Partnership" in doc["part_title_en"] or "General Partnerships" in doc["part_title_en"]
    blob = " ".join(r["article_heading_en"] + " " + r["english_reference_text"] for r in doc["records"])
    assert "General Partnership" in blob


def test_book3_mentions_limited_partnership():
    doc = _read(BOOK3)
    assert "Limited Partnership" in doc["part_title_en"]
    blob = " ".join(r["article_heading_en"] + " " + r["english_reference_text"] for r in doc["records"])
    assert "Limited Partnership" in blob


# -- no English LLM layer yet -----------------------------------------------
def test_no_english_llm_directory():
    # English Legal LLM layer started (Book Four Section 1 pilot); only that file may exist.
    _elf = glob.glob(os.path.join(ROOT, "data", "english_legal_llm", "*_en_legal_llm.json"))
    assert set(os.path.basename(p) for p in _elf) <= {"book4_section1_en_legal_llm.json", "book4_section2_en_legal_llm.json"}, _elf


def test_no_english_llm_record_files():
    stray = glob.glob(os.path.join(ROOT, "data", "**", "*_en_legal_llm.json"), recursive=True)
    assert set(os.path.basename(p) for p in stray) <= {"book4_section1_en_legal_llm.json", "book4_section2_en_legal_llm.json"}, stray


# -- Book One reference unchanged (still 1-34) ------------------------------
def test_book1_reference_still_articles_1_to_34():
    assert [r["article_number"] for r in _records(BOOK1)] == list(range(1, 35))


# -- no overclaim terms -----------------------------------------------------
def test_no_forbidden_overclaim_terms():
    for path in (BOOK2, BOOK3):
        blob = open(path, encoding="utf-8").read().lower()
        for term in ("binding english text", "governing english text",
                     "english is binding", "verified translation",
                     "binding_translation", "unofficial_translation"):
            assert term not in blob, (path, term)


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


def test_arabic_legal_llm_records_unchanged():
    for fname, exp in (("book1_ar_legal_llm.json", list(range(1, 35))),
                       ("book2_ar_legal_llm.json", list(range(35, 51))),
                       ("book3_ar_legal_llm.json", list(range(51, 58)))):
        doc = _read(os.path.join(ROOT, "data", "arabic_legal_llm", fname))
        assert [r["article_numbers"][0] for r in doc["records"]] == exp, fname


# -- validator passes -------------------------------------------------------
def test_validator_script_passes():
    import subprocess
    import sys
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "validate_english_reference.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
