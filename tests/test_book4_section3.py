"""Book Four — Section 3 (general_assemblies) reconciled model-1b provisions.

Owner Option 1: reconciled to the source. Provision records for the source-rendered
explicit set 85, 87, 92, 93, 99, 101, 102 (grouped [85,87], [92,93], [99], [101],
[102]); Articles 84, 89, 100 reclassified to not_explicit_in_source. NOT a full Book
Four article dataset; NOT a full Book Four build.
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "book4_provision.schema.json")
DATA = os.path.join(ROOT, "data", "articles", "book4_provisions_084_102.json")
JSONL = os.path.join(ROOT, "data", "articles", "book4_provisions_084_102.jsonl")
COVERAGE = os.path.join(ROOT, "data", "coverage", "book4_coverage_matrix.json")
DECISION = os.path.join(ROOT, "docs", "book4_preflight", "BOOK4_SECTION3_SCOPE_DECISION.md")

GROUPS = [[85, 87], [92, 93], [99], [101], [102]]
EXPLICIT = [85, 87, 92, 93, 99, 101, 102]
RECLASSIFIED = [84, 89, 100]
OTHER_UNCOVERED = [86, 88, 90, 91, 94, 95, 96, 97, 98]
BANNED = ("verified_summary", "verified", "محققة", "经核验")


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _provs():
    return _read(DATA)["provisions"]


# -- existence + counts -----------------------------------------------------
def test_provision_json_exists():
    assert os.path.exists(DATA)


def test_jsonl_line_count_equals_provisions():
    assert os.path.exists(JSONL)
    with open(JSONL, encoding="utf-8") as fh:
        lines = [ln for ln in fh.read().splitlines() if ln.strip()]
    assert len(lines) == len(_provs())


def test_no_book4_articles_files():
    for f in os.listdir(os.path.join(ROOT, "data", "articles")):
        assert not f.startswith("book4_articles_"), f


# -- provision scope --------------------------------------------------------
def test_provision_groups_exact():
    assert [p["source_article_numbers"] for p in _provs()] == GROUPS


def test_no_provision_maps_to_uncovered():
    forbidden = set(RECLASSIFIED) | set(OTHER_UNCOVERED)
    for p in _provs():
        assert not (set(p["source_article_numbers"]) & forbidden), p["provision_id"]
        assert all(84 <= n <= 102 for n in p["source_article_numbers"]), p["provision_id"]


def test_records_pass_schema():
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


# -- coverage matrix reconciliation -----------------------------------------
def test_coverage_matrix_80_rows():
    matrix = _read(COVERAGE)
    rows = matrix["rows"]
    assert len(rows) == 80
    assert [r["article_number"] for r in rows] == list(range(58, 138))


def test_explicit_rows_provision_created():
    by = {r["article_number"]: r for r in _read(COVERAGE)["rows"]}
    for n in EXPLICIT:
        assert by[n]["source_coverage_status"] == "explicit_in_source", n
        assert by[n]["official_text_check"] == "needs_check", n
        assert by[n]["content_record_status"] == "provision_created", n


def test_reclassified_rows_uncovered():
    by = {r["article_number"]: r for r in _read(COVERAGE)["rows"]}
    for n in RECLASSIFIED:
        assert by[n]["source_coverage_status"] == "not_explicit_in_source", n
        assert by[n]["official_text_check"] == "needs_official_text_check", n
        assert by[n]["content_record_status"] == "no_record_until_source_available", n
        # No invented title on a reclassified row.
        assert by[n]["article_title_ar"] in (None, "", "NEEDS_OFFICIAL_TEXT_CHECK"), n


def test_other_uncovered_section3_rows_unchanged():
    by = {r["article_number"]: r for r in _read(COVERAGE)["rows"]}
    for n in OTHER_UNCOVERED:
        assert by[n]["source_coverage_status"] == "not_explicit_in_source", n
        assert by[n]["official_text_check"] == "needs_official_text_check", n
        assert by[n]["content_record_status"] == "no_record_until_source_available", n


# -- section content only ---------------------------------------------------
def test_section_content_files_exist():
    for p in ("content/ar/book4_section3.md", "content/zh/book4_section3.md",
              "content/bilingual/book4_section3_bilingual.md"):
        assert os.path.exists(os.path.join(ROOT, p)), p


def test_no_full_book4_content():
    for p in ("content/ar/book4.md", "content/zh/book4.md",
              "content/bilingual/book4_bilingual.md"):
        assert not os.path.exists(os.path.join(ROOT, p)), p


# -- decision doc records the owner decision --------------------------------
def test_scope_decision_doc_records_option_1():
    txt = open(DECISION, encoding="utf-8").read()
    assert "Owner selected Option 1" in txt
    assert "reconcile" in txt.lower()


# -- existing merged artifacts unchanged ------------------------------------
def test_section1_and_section2_provisions_unchanged():
    s1 = _read(os.path.join(ROOT, "data", "articles", "book4_provisions_058_066.json"))
    assert [p["source_article_numbers"] for p in s1["provisions"]] == [[58], [59], [60], [66]]
    s2 = _read(os.path.join(ROOT, "data", "articles", "book4_provisions_067_083.json"))
    assert [p["source_article_numbers"] for p in s2["provisions"]] == [[67, 68], [71], [72], [75], [77]]


def test_english_reference_unchanged():
    ref = os.path.join(ROOT, "data", "english_reference")
    for fname, exp in (("book1_en_reference.json", list(range(1, 35))),
                       ("book2_en_reference.json", list(range(35, 51))),
                       ("book3_en_reference.json", list(range(51, 58))),
                       ("book4_section1_en_reference.json", [58, 59, 60, 66]),
                       ("book4_section2_en_reference.json", [67, 68, 71, 72, 75, 77])):
        doc = _read(os.path.join(ref, fname))
        assert [r["article_number"] for r in doc["records"]] == exp, fname


def test_arabic_legal_llm_unchanged():
    layer = os.path.join(ROOT, "data", "arabic_legal_llm")
    for fname, exp in (("book1_ar_legal_llm.json", list(range(1, 35))),
                       ("book2_ar_legal_llm.json", list(range(35, 51))),
                       ("book3_ar_legal_llm.json", list(range(51, 58)))):
        doc = _read(os.path.join(layer, fname))
        assert [r["article_numbers"][0] for r in doc["records"]] == exp, fname
    s1 = _read(os.path.join(layer, "book4_section1_ar_legal_llm.json"))
    assert sorted(r["article_numbers"][0] for r in s1["records"]) == [58, 59, 60, 66]
    s2 = _read(os.path.join(layer, "book4_section2_ar_legal_llm.json"))
    assert [r["article_numbers"] for r in s2["records"]] == [[67, 68], [71], [72], [75], [77]]
    # No Arabic Legal LLM Section 3 file yet (out of scope for this PR).
    assert not os.path.exists(os.path.join(layer, "book4_section3_ar_legal_llm.json"))


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
            assert a["chinese_translation"].strip(), (fname, a["article_number"])
