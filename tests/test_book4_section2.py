"""Book Four — Section 2 (board_and_governance) model-1b provisions.

Provision records for explicitly source-covered Articles 67, 68, 71, 72, 75, 77
only (source groups 67 & 68 → one provision, so 5 provisions over 6 articles).
NOT a full Book Four article dataset; NOT a full Book Four build.
"""

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "book4_provision.schema.json")
DATA = os.path.join(ROOT, "data", "articles", "book4_provisions_067_083.json")
JSONL = os.path.join(ROOT, "data", "articles", "book4_provisions_067_083.jsonl")
COVERAGE = os.path.join(ROOT, "data", "coverage", "book4_coverage_matrix.json")

EXPLICIT = [67, 68, 71, 72, 75, 77]
UNCOVERED = [69, 70, 73, 74, 76, 78, 79, 80, 81, 82, 83]
BANNED = ("verified_summary", "verified", "محققة", "经核验")


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _provs():
    return _read(DATA)["provisions"]


# -- existence + counts -----------------------------------------------------
def test_provision_json_exists():
    assert os.path.exists(DATA)


def test_jsonl_exists_and_line_count_equals_provisions():
    assert os.path.exists(JSONL)
    with open(JSONL, encoding="utf-8") as fh:
        lines = [ln for ln in fh.read().splitlines() if ln.strip()]
    assert len(lines) == len(_provs())


def test_no_book4_articles_files():
    for f in os.listdir(os.path.join(ROOT, "data", "articles")):
        assert not f.startswith("book4_articles_"), f


# -- coverage scope of provisions -------------------------------------------
def test_provisions_cover_exactly_explicit_set():
    covered = sorted({n for p in _provs() for n in p["source_article_numbers"]})
    assert covered == EXPLICIT


def test_no_provision_maps_to_uncovered_article():
    for p in _provs():
        assert not (set(p["source_article_numbers"]) & set(UNCOVERED)), p["provision_id"]
        assert all(67 <= n <= 83 for n in p["source_article_numbers"]), p["provision_id"]


def test_records_pass_book4_provision_schema():
    schema = _read(SCHEMA)
    try:
        import jsonschema
        v = jsonschema.Draft7Validator(schema)
        for p in _provs():
            errs = [e.message for e in v.iter_errors(p)]
            assert not errs, (p["provision_id"], errs)
    except ImportError:
        for p in _provs():
            for k in schema["required"]:
                assert k in p, (p["provision_id"], k)


# -- trust posture ----------------------------------------------------------
def test_trust_posture():
    for p in _provs():
        assert p["translation_mode"] == "internally_reviewed_summary", p["provision_id"]
        assert p["source"]["official_text_check"] == "needs_check", p["provision_id"]
        assert p["source"]["source_coverage_status"] == "explicit_in_source", p["provision_id"]
        assert p["arabic_reference_summary"].strip(), p["provision_id"]
        assert p["chinese_translation"].strip(), p["provision_id"]


def test_no_overclaim_terms():
    blob = open(DATA, encoding="utf-8").read()
    for t in BANNED:
        assert t not in blob, t


# -- coverage matrix integrity ----------------------------------------------
def test_coverage_matrix_still_80_rows():
    matrix = _read(COVERAGE)
    rows = matrix["rows"]
    assert len(rows) == 80
    assert [r["article_number"] for r in rows] == list(range(58, 138))


def test_new_articles_provision_created():
    by = {r["article_number"]: r for r in _read(COVERAGE)["rows"]}
    for n in EXPLICIT:
        assert by[n]["content_record_status"] == "provision_created", n
        assert by[n]["source_coverage_status"] == "explicit_in_source", n
        assert by[n]["official_text_check"] == "needs_check", n


def test_uncovered_rows_remain_needs_check():
    by = {r["article_number"]: r for r in _read(COVERAGE)["rows"]}
    for n in UNCOVERED:
        assert by[n]["source_coverage_status"] == "not_explicit_in_source", n
        assert by[n]["official_text_check"] == "needs_official_text_check", n
        assert by[n]["content_record_status"] == "no_record_until_source_available", n


# -- section content only; no full Book Four --------------------------------
def test_section_content_files_exist():
    for p in ("content/ar/book4_section2.md", "content/zh/book4_section2.md",
              "content/bilingual/book4_section2_bilingual.md"):
        assert os.path.exists(os.path.join(ROOT, p)), p


def test_no_full_book4_content():
    for p in ("content/ar/book4.md", "content/zh/book4.md",
              "content/bilingual/book4_bilingual.md"):
        assert not os.path.exists(os.path.join(ROOT, p)), p


# -- existing merged artifacts unchanged ------------------------------------
def test_existing_section1_provisions_unchanged():
    doc = _read(os.path.join(ROOT, "data", "articles", "book4_provisions_058_066.json"))
    assert [p["source_article_numbers"] for p in doc["provisions"]] == [[58], [59], [60], [66]]


def test_existing_english_reference_unchanged():
    ref = os.path.join(ROOT, "data", "english_reference")
    for fname, exp in (("book1_en_reference.json", list(range(1, 35))),
                       ("book2_en_reference.json", list(range(35, 51))),
                       ("book3_en_reference.json", list(range(51, 58))),
                       ("book4_section1_en_reference.json", [58, 59, 60, 66])):
        doc = _read(os.path.join(ref, fname))
        assert [r["article_number"] for r in doc["records"]] == exp, fname


def test_existing_arabic_legal_llm_unchanged():
    for fname, exp in (("book1_ar_legal_llm.json", list(range(1, 35))),
                       ("book2_ar_legal_llm.json", list(range(35, 51))),
                       ("book3_ar_legal_llm.json", list(range(51, 58)))):
        doc = _read(os.path.join(ROOT, "data", "arabic_legal_llm", fname))
        assert [r["article_numbers"][0] for r in doc["records"]] == exp, fname
    pilot = _read(os.path.join(ROOT, "data", "arabic_legal_llm", "book4_section1_ar_legal_llm.json"))
    assert sorted(r["article_numbers"][0] for r in pilot["records"]) == [58, 59, 60, 66]


def test_books_1_3_canonical_unchanged():
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
