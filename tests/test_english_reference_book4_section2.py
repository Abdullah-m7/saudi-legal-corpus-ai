"""Official English guidance REFERENCE layer — Book Four Section 2 (board_and_governance).

Per-article English reference records for the provision-covered Articles 67, 68,
71, 72, 75, 77 (the English source renders 67 & 68 under separate headings).
NOT the English Legal LLM-ready layer.
"""

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "english_reference.schema.json")
REF = os.path.join(ROOT, "data", "english_reference")
DATA = os.path.join(REF, "book4_section2_en_reference.json")
JSONL = os.path.join(REF, "book4_section2_en_reference.jsonl")
PROVISIONS = os.path.join(ROOT, "data", "articles", "book4_provisions_067_083.json")

COVERED = [67, 68, 71, 72, 75, 77]
UNCOVERED = [69, 70, 73, 74, 76, 78, 79, 80, 81, 82, 83]


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _records():
    return _read(DATA)["records"]


def _blob(n):
    r = next(x for x in _records() if x["article_number"] == n)
    return (r["article_heading_en"] + " " + r["english_reference_text"]).lower()


# -- existence + coverage ---------------------------------------------------
def test_data_exists():
    assert os.path.exists(DATA)


def test_jsonl_line_count_equals_records():
    assert os.path.exists(JSONL)
    with open(JSONL, encoding="utf-8") as fh:
        lines = [ln for ln in fh.read().splitlines() if ln.strip()]
    assert len(lines) == len(_records())
    assert [json.loads(ln)["article_number"] for ln in lines] == COVERED


def test_article_numbers_exact():
    assert [r["article_number"] for r in _records()] == COVERED


def test_no_records_for_uncovered_section2():
    nums = {r["article_number"] for r in _records()}
    assert not (nums & set(UNCOVERED)), nums


def test_no_records_for_84_to_137():
    nums = {r["article_number"] for r in _records()}
    assert not (nums & set(range(84, 138))), nums


def test_no_duplicates():
    nums = [r["article_number"] for r in _records()]
    assert len(set(nums)) == len(nums) == 6


# -- per-record fields ------------------------------------------------------
def test_every_record_has_text():
    for r in _records():
        assert r["english_reference_text"].strip(), r["article_number"]


def test_trust_fields_and_part():
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


# -- concept presence per article -------------------------------------------
def test_article_67_68_board_concepts():
    for n in (67, 68):
        b = _blob(n)
        assert any(t in b for t in ("board", "director", "membership", "election",
                                    "nomination", "appoint", "term")), n


def test_article_71_interest_disclosure_concepts():
    b = _blob(71)
    assert any(t in b for t in ("disclosure", "interest", "conflict", "abstain",
                                "not vote", "vote")), b[:80]


def test_article_72_loans_concepts():
    b = _blob(72)
    assert any(t in b for t in ("loan", "financing", "guarantee", "guaranteeing")), b[:80]


def test_article_75_asset_sale_concepts():
    b = _blob(75)
    assert any(t in b for t in ("asset", "sale", "sell", "50%", "50 %", "general assembly")), b[:80]


def test_article_77_board_powers_concepts():
    b = _blob(77)
    assert any(t in b for t in ("power", "board", "third part")), b[:80]


# -- no English LLM layer ---------------------------------------------------
def test_no_english_llm_directory():
    # English Legal LLM layer started (Book Four Section 1 pilot); only that file may exist.
    _elf = glob.glob(os.path.join(ROOT, "data", "english_legal_llm", "*_en_legal_llm.json"))
    assert sorted(os.path.basename(p) for p in _elf) in ([], ["book4_section1_en_legal_llm.json"]), _elf


def test_no_english_llm_record_files():
    stray = glob.glob(os.path.join(ROOT, "data", "**", "*_en_legal_llm.json"), recursive=True)
    assert sorted(os.path.basename(p) for p in stray) in ([], ["book4_section1_en_legal_llm.json"]), stray


# -- no overclaim -----------------------------------------------------------
def test_no_forbidden_overclaim_terms():
    blob = open(DATA, encoding="utf-8").read().lower()
    for term in ("binding english text", "governing english text",
                 "english is binding", "verified translation",
                 "binding_translation", "unofficial_translation"):
        assert term not in blob, term


# -- existing English reference unchanged -----------------------------------
def test_books_1_3_and_section1_reference_unchanged():
    for fname, exp in (("book1_en_reference.json", list(range(1, 35))),
                       ("book2_en_reference.json", list(range(35, 51))),
                       ("book3_en_reference.json", list(range(51, 58))),
                       ("book4_section1_en_reference.json", [58, 59, 60, 66])):
        doc = _read(os.path.join(REF, fname))
        assert [r["article_number"] for r in doc["records"]] == exp, fname


# -- cross-check with Book Four model 1b ------------------------------------
def test_provision_set_matches():
    doc = _read(PROVISIONS)
    prov_arts = sorted({a for p in doc["provisions"] for a in p["source_article_numbers"]})
    assert prov_arts == COVERED
    assert [r["article_number"] for r in _records()] == prov_arts


def test_arabic_llm_section2_groups_intact():
    doc = _read(os.path.join(ROOT, "data", "arabic_legal_llm", "book4_section2_ar_legal_llm.json"))
    assert [r["article_numbers"] for r in doc["records"]] == [[67, 68], [71], [72], [75], [77]]


def test_coverage_matrix_80_rows_uncovered_preserved():
    matrix = _read(os.path.join(ROOT, "data", "coverage", "book4_coverage_matrix.json"))
    rows = matrix["rows"]
    assert len(rows) == 80
    by = {r["article_number"]: r for r in rows}
    for n in UNCOVERED:
        assert by[n]["source_coverage_status"] == "not_explicit_in_source", n
        assert by[n]["official_text_check"] == "needs_official_text_check", n
        assert by[n]["content_record_status"] == "no_record_until_source_available", n


def test_no_book4_articles_files():
    for f in os.listdir(os.path.join(ROOT, "data", "articles")):
        assert not f.startswith("book4_articles_"), f


# -- existing Arabic / Chinese / Arabic-LLM / provisions unchanged ----------
def test_arabic_and_chinese_unchanged():
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
            assert a["chinese_translation"].strip(), (fname, a["article_number"])


def test_book4_section2_provisions_unchanged():
    doc = _read(PROVISIONS)
    assert [p["source_article_numbers"] for p in doc["provisions"]] == [[67, 68], [71], [72], [75], [77]]
    for p in doc["provisions"]:
        assert p["chinese_translation"].strip(), p["source_article_numbers"]


def test_arabic_legal_llm_records_unchanged():
    for fname, exp in (("book1_ar_legal_llm.json", list(range(1, 35))),
                       ("book2_ar_legal_llm.json", list(range(35, 51))),
                       ("book3_ar_legal_llm.json", list(range(51, 58)))):
        doc = _read(os.path.join(ROOT, "data", "arabic_legal_llm", fname))
        assert [r["article_numbers"][0] for r in doc["records"]] == exp, fname


def test_validator_script_passes():
    import subprocess
    import sys
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "validate_english_reference.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
