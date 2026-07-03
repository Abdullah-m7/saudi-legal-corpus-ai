"""Official English guidance REFERENCE layer — Book Four Section 1 (model 1b).

Reference/alignment text only, provision-covered Articles 58, 59, 60, 66 only.
NOT the English Legal LLM-ready layer.
"""

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "english_reference.schema.json")
REF = os.path.join(ROOT, "data", "english_reference")
DATA = os.path.join(REF, "book4_section1_en_reference.json")
JSONL = os.path.join(REF, "book4_section1_en_reference.jsonl")

COVERED = [58, 59, 60, 66]
UNCOVERED = [61, 62, 63, 64, 65]


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _records():
    return _read(DATA)["records"]


# -- existence + exact coverage ---------------------------------------------
def test_data_exists():
    assert os.path.exists(DATA)


def test_jsonl_line_count_4():
    assert os.path.exists(JSONL)
    with open(JSONL, encoding="utf-8") as fh:
        lines = [ln for ln in fh.read().splitlines() if ln.strip()]
    assert len(lines) == 4
    assert [json.loads(ln)["article_number"] for ln in lines] == COVERED


def test_article_numbers_exactly_58_59_60_66():
    assert [r["article_number"] for r in _records()] == COVERED


def test_no_records_for_61_to_65():
    nums = {r["article_number"] for r in _records()}
    assert not (nums & set(UNCOVERED)), nums


def test_no_records_for_67_to_137():
    nums = {r["article_number"] for r in _records()}
    assert not (nums & set(range(67, 138))), nums


def test_no_duplicates():
    nums = [r["article_number"] for r in _records()]
    assert len(set(nums)) == len(nums) == 4


# -- per-record fields ------------------------------------------------------
def test_every_record_has_english_reference_text():
    for r in _records():
        assert r["english_reference_text"].strip(), r["article_number"]


def test_trust_fields_and_book_part():
    for r in _records():
        assert r["book"] == 4, r["article_number"]
        assert r["part_number_en"] == 4, r["article_number"]
        assert "Joint-Stock Company" in r["part_title_en"], r["article_number"]
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
def _blob(n):
    r = next(x for x in _records() if x["article_number"] == n)
    return r["article_heading_en"] + " " + r["english_reference_text"]


def test_article58_joint_stock_definition():
    assert "Joint-Stock Company" in _blob(58) or "Joint-stock" in _blob(58)


def test_article60_issued_and_authorized_capital():
    assert "Issued and Authorized Capital" in _blob(60) or (
        "issued capital" in _blob(60).lower() and "authorized capital" in _blob(60).lower())


def test_article66_valuation_in_kind():
    assert "Valuation of In-Kind Contributions" in _blob(66) or "in-kind" in _blob(66).lower()


# -- no English LLM layer yet -----------------------------------------------
def test_no_english_llm_directory():
    assert not os.path.isdir(os.path.join(ROOT, "data", "english_legal_llm"))


def test_no_english_llm_record_files():
    stray = glob.glob(os.path.join(ROOT, "data", "**", "*_en_legal_llm.json"), recursive=True)
    assert stray == [], stray


# -- no overclaim terms -----------------------------------------------------
def test_no_forbidden_overclaim_terms():
    blob = open(DATA, encoding="utf-8").read().lower()
    for term in ("binding english text", "governing english text",
                 "english is binding", "verified translation",
                 "binding_translation", "unofficial_translation"):
        assert term not in blob, term


# -- Books 1-3 English reference still cover Articles 1-57 -------------------
def test_books_1_3_reference_unchanged_coverage():
    for fname, exp in (("book1_en_reference.json", list(range(1, 35))),
                       ("book2_en_reference.json", list(range(35, 51))),
                       ("book3_en_reference.json", list(range(51, 58)))):
        doc = _read(os.path.join(REF, fname))
        assert [r["article_number"] for r in doc["records"]] == exp, fname


# -- cross-check with Book Four model 1b ------------------------------------
def test_book4_provisions_file_exists_and_matches():
    prov = os.path.join(ROOT, "data", "articles", "book4_provisions_058_066.json")
    assert os.path.exists(prov)
    doc = _read(prov)
    prov_arts = sorted({a for p in doc["provisions"] for a in p["source_article_numbers"]})
    assert prov_arts == COVERED
    # English reference article numbers exactly match provision-covered articles.
    assert [r["article_number"] for r in _records()] == prov_arts


def test_coverage_matrix_80_rows_and_uncovered_preserved():
    matrix = _read(os.path.join(ROOT, "data", "coverage", "book4_coverage_matrix.json"))
    rows = matrix["rows"]
    assert len(rows) == 80
    by_num = {r["article_number"]: r for r in rows}
    for n in UNCOVERED:
        assert by_num[n]["source_coverage_status"] == "not_explicit_in_source", n
        assert by_num[n]["official_text_check"] == "needs_official_text_check", n
        assert by_num[n]["content_record_status"] == "no_record_until_source_available", n


def test_no_book4_articles_files():
    articles_dir = os.path.join(ROOT, "data", "articles")
    for f in os.listdir(articles_dir):
        assert not f.startswith("book4_articles_"), f


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


def test_book4_provision_text_unchanged():
    doc = _read(os.path.join(ROOT, "data", "articles", "book4_provisions_058_066.json"))
    assert [p["source_article_numbers"] for p in doc["provisions"]] == [[58], [59], [60], [66]]
    for p in doc["provisions"]:
        assert p["chinese_translation"].strip(), p["source_article_numbers"]


def test_arabic_legal_llm_records_unchanged():
    for fname, exp in (("book1_ar_legal_llm.json", list(range(1, 35))),
                       ("book2_ar_legal_llm.json", list(range(35, 51))),
                       ("book3_ar_legal_llm.json", list(range(51, 58)))):
        doc = _read(os.path.join(ROOT, "data", "arabic_legal_llm", fname))
        assert [r["article_numbers"][0] for r in doc["records"]] == exp, fname
    pilot = _read(os.path.join(ROOT, "data", "arabic_legal_llm", "book4_section1_ar_legal_llm.json"))
    assert sorted(r["article_numbers"][0] for r in pilot["records"]) == COVERED


# -- validator passes -------------------------------------------------------
def test_validator_script_passes():
    import subprocess
    import sys
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "validate_english_reference.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
