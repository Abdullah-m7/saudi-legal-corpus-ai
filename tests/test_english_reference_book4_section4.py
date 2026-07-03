"""Official English guidance REFERENCE layer — Book Four Section 4 (shares/debt/sukuk).

Per-article English reference records for the owner-reconciled provision-covered
Articles 108, 113, 115, 117 (Part 4 — Joint-Stock Company). Article 110 ("Amendment of
Share-Associated Rights and Obligations") exists in the official English source but is
OUT OF SCOPE: the reconciled Book Four model-1b source reclassified Article 110 as
not_explicit_in_source. NOT the English Legal LLM-ready layer.
"""

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "english_reference.schema.json")
REF = os.path.join(ROOT, "data", "english_reference")
DATA = os.path.join(REF, "book4_section4_en_reference.json")
JSONL = os.path.join(REF, "book4_section4_en_reference.jsonl")
PROVISIONS = os.path.join(ROOT, "data", "articles", "book4_provisions_103_120.json")
COVERAGE = os.path.join(ROOT, "data", "coverage", "book4_coverage_matrix.json")

COVERED = [108, 113, 115, 117]
# Uncovered Section-4 articles (incl. 110, present in the English source but out of
# scope) that must NEVER get an English reference record.
UNCOVERED = [103, 104, 105, 106, 107, 109, 110, 111, 112, 114, 116, 118, 119, 120]


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
    assert len(lines) == len(_records()) == 4
    assert [json.loads(ln)["article_number"] for ln in lines] == COVERED


def test_article_numbers_exact():
    assert [r["article_number"] for r in _records()] == COVERED


def test_exactly_four_records():
    assert len(_records()) == 4


def test_article_110_excluded():
    nums = {r["article_number"] for r in _records()}
    assert 110 not in nums


def test_no_records_for_uncovered_section4():
    nums = {r["article_number"] for r in _records()}
    assert not (nums & set(UNCOVERED)), nums


def test_no_records_for_121_to_137():
    nums = {r["article_number"] for r in _records()}
    assert not (nums & set(range(121, 138))), nums


def test_no_duplicates():
    nums = [r["article_number"] for r in _records()]
    assert len(set(nums)) == len(nums) == 4


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
def test_article_108_types_and_classes():
    b = _blob(108)
    assert "type" in b and "class" in b
    assert any(t in b for t in ("share", "common", "preferred", "redeemable")), b[:80]


def test_article_113_drag_tag_along():
    b = _blob(113)
    assert "drag-along" in b or "tag-along" in b
    assert any(t in b for t in ("voting", "articles of association", "capital market")), b[:80]


def test_article_115_non_payment():
    b = _blob(115)
    assert "non-payment" in b or "non -payment" in b or "pay" in b
    assert any(t in b for t in ("share", "board", "sell", "auction")), b[:80]


def test_article_117_debt_instruments_sukuk():
    b = _blob(117)
    assert "debt instrument" in b or "sukuk" in b
    assert any(t in b for t in ("issue", "issuance", "convertible", "capital market")), b[:80]


# -- no English LLM layer ---------------------------------------------------
def test_no_english_llm_directory():
    # English Legal LLM layer started (Book Four Section 1 pilot); only that file may exist.
    _elf = glob.glob(os.path.join(ROOT, "data", "english_legal_llm", "*_en_legal_llm.json"))
    assert set(os.path.basename(p) for p in _elf) <= {"book4_section1_en_legal_llm.json", "book4_section2_en_legal_llm.json", "book4_section3_en_legal_llm.json", "book4_section4_en_legal_llm.json", "book4_section5_en_legal_llm.json"}, _elf


def test_no_english_llm_record_files():
    stray = glob.glob(os.path.join(ROOT, "data", "**", "*_en_legal_llm.json"), recursive=True)
    assert set(os.path.basename(p) for p in stray) <= {"book4_section1_en_legal_llm.json", "book4_section2_en_legal_llm.json", "book4_section3_en_legal_llm.json", "book4_section4_en_legal_llm.json", "book4_section5_en_legal_llm.json"}, stray


# -- no overclaim -----------------------------------------------------------
def test_no_forbidden_overclaim_terms():
    blob = open(DATA, encoding="utf-8").read().lower()
    for term in ("binding english text", "governing english text",
                 "english is binding", "verified translation",
                 "binding_translation", "unofficial_translation"):
        assert term not in blob, term


# -- existing English reference unchanged -----------------------------------
def test_books_1_3_and_sections_1_2_3_reference_unchanged():
    for fname, exp in (("book1_en_reference.json", list(range(1, 35))),
                       ("book2_en_reference.json", list(range(35, 51))),
                       ("book3_en_reference.json", list(range(51, 58))),
                       ("book4_section1_en_reference.json", [58, 59, 60, 66]),
                       ("book4_section2_en_reference.json", [67, 68, 71, 72, 75, 77]),
                       ("book4_section3_en_reference.json", [85, 87, 92, 93, 99, 101, 102])):
        doc = _read(os.path.join(REF, fname))
        assert [r["article_number"] for r in doc["records"]] == exp, fname


# -- cross-check with Book Four model 1b ------------------------------------
def test_provision_set_matches():
    doc = _read(PROVISIONS)
    prov_arts = sorted({a for p in doc["provisions"] for a in p["source_article_numbers"]})
    assert prov_arts == COVERED
    assert [r["article_number"] for r in _records()] == prov_arts


def test_arabic_llm_section4_groups_intact():
    doc = _read(os.path.join(ROOT, "data", "arabic_legal_llm", "book4_section4_ar_legal_llm.json"))
    assert [r["article_numbers"] for r in doc["records"]] == [[108], [113], [115], [117]]


def test_coverage_matrix_80_rows_reconciliation_preserved():
    matrix = _read(COVERAGE)
    rows = matrix["rows"]
    assert len(rows) == 80
    by = {r["article_number"]: r for r in rows}
    for n in COVERED:
        assert by[n]["source_coverage_status"] == "explicit_in_source", n
        assert by[n]["official_text_check"] == "needs_check", n
        assert by[n]["content_record_status"] == "provision_created", n
    # Article 110 and other uncovered Section-4 articles stay uncovered.
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


def test_book4_section4_provisions_unchanged():
    doc = _read(PROVISIONS)
    assert [p["source_article_numbers"] for p in doc["provisions"]] == [[108], [113], [115], [117]]
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
