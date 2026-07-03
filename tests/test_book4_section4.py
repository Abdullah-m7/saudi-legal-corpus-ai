"""Book Four — Section 4 (shares / debt instruments / sukuk) reconciled model-1b provisions.

Owner Option 1: reconciled to the source. Provision records for the source-rendered
explicit set 108, 113, 115, 117 (single-article blocks [108], [113], [115], [117]);
Article 110 reclassified to not_explicit_in_source. NOT a full Book Four article dataset;
NOT a full Book Four build.
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "book4_provision.schema.json")
DATA = os.path.join(ROOT, "data", "articles", "book4_provisions_103_120.json")
JSONL = os.path.join(ROOT, "data", "articles", "book4_provisions_103_120.jsonl")
COVERAGE = os.path.join(ROOT, "data", "coverage", "book4_coverage_matrix.json")
DECISION = os.path.join(ROOT, "docs", "book4_preflight", "BOOK4_SECTION4_SCOPE_DECISION.md")

GROUPS = [[108], [113], [115], [117]]
EXPLICIT = [108, 113, 115, 117]
RECLASSIFIED = [110]
OTHER_UNCOVERED = [103, 104, 105, 106, 107, 109, 111, 112, 114, 116, 118, 119, 120]
ALL_UNCOVERED = RECLASSIFIED + OTHER_UNCOVERED
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
    assert len(lines) == len(_provs()) == 4


def test_no_book4_articles_files():
    for f in os.listdir(os.path.join(ROOT, "data", "articles")):
        assert not f.startswith("book4_articles_"), f


# -- provision scope --------------------------------------------------------
def test_provision_groups_exact():
    assert [p["source_article_numbers"] for p in _provs()] == GROUPS


def test_no_provision_maps_to_uncovered():
    forbidden = set(ALL_UNCOVERED)
    for p in _provs():
        assert not (set(p["source_article_numbers"]) & forbidden), p["provision_id"]
        assert all(103 <= n <= 120 for n in p["source_article_numbers"]), p["provision_id"]


def test_article_110_gets_no_provision():
    covered = {n for p in _provs() for n in p["source_article_numbers"]}
    assert 110 not in covered
    assert covered == set(EXPLICIT)


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


def test_thematic_section_key():
    for p in _provs():
        assert p["thematic_section"] == "shares_debt_instruments_sukuk", p["provision_id"]


# -- trust posture + source fields ------------------------------------------
def test_trust_posture_and_source_fields():
    for p in _provs():
        assert p["translation_mode"] == "internally_reviewed_summary", p["provision_id"]
        assert p["source"]["official_text_check"] == "needs_check", p["provision_id"]
        assert p["source"]["source_coverage_status"] == "explicit_in_source", p["provision_id"]
        assert p["source"]["input_pdf"] == "inputs/bab4_source.pdf", p["provision_id"]
        assert p["arabic_reference_summary"].strip(), p["provision_id"]
        assert p["chinese_translation"].strip(), p["provision_id"]


def test_no_overclaim_terms():
    blob = open(DATA, encoding="utf-8").read()
    for t in BANNED:
        assert t not in blob, t


# -- expected legal themes present ------------------------------------------
def _blob(n):
    p = next(x for x in _provs() if x["source_article_numbers"] == [n])
    return (p["provision_title_ar"] + " " + p["provision_title_zh"] + " "
            + p["arabic_reference_summary"] + " " + p["chinese_translation"])


def test_article_108_types_and_classes():
    b = _blob(108)
    assert "种类" in b and "类别" in b
    assert "أنواع" in b or "فئات" in b


def test_article_113_drag_tag_along():
    b = _blob(113)
    assert "拖售权" in b or "随售权" in b
    assert "السحب" in b or "الإلحاق" in b


def test_article_115_non_payment():
    b = _blob(115)
    assert "违约" in b or "未缴" in b
    assert "التخلف" in b


def test_article_117_debt_instruments_sukuk():
    b = _blob(117)
    assert "债务工具" in b or "融资凭证" in b or "Sukuk" in b
    assert "الصكوك" in b or "أدوات الدين" in b


# -- coverage matrix reconciliation -----------------------------------------
def test_coverage_matrix_80_rows():
    rows = _read(COVERAGE)["rows"]
    assert len(rows) == 80
    assert [r["article_number"] for r in rows] == list(range(58, 138))


def test_explicit_rows_provision_created():
    by = {r["article_number"]: r for r in _read(COVERAGE)["rows"]}
    for n in EXPLICIT:
        assert by[n]["source_coverage_status"] == "explicit_in_source", n
        assert by[n]["official_text_check"] == "needs_check", n
        assert by[n]["content_record_status"] == "provision_created", n


def test_article_110_row_reclassified_uncovered():
    by = {r["article_number"]: r for r in _read(COVERAGE)["rows"]}
    r = by[110]
    assert r["source_coverage_status"] == "not_explicit_in_source"
    assert r["official_text_check"] == "needs_official_text_check"
    assert r["content_record_status"] == "no_record_until_source_available"
    assert r["article_title_ar"] in (None, "", "NEEDS_OFFICIAL_TEXT_CHECK")


def test_other_uncovered_section4_rows():
    by = {r["article_number"]: r for r in _read(COVERAGE)["rows"]}
    for n in OTHER_UNCOVERED:
        assert by[n]["source_coverage_status"] == "not_explicit_in_source", n
        assert by[n]["official_text_check"] == "needs_official_text_check", n
        assert by[n]["content_record_status"] == "no_record_until_source_available", n


# -- section content only ---------------------------------------------------
def test_section_content_files_exist():
    for p in ("content/ar/book4_section4.md", "content/zh/book4_section4.md",
              "content/bilingual/book4_section4_bilingual.md"):
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
    assert "110" in txt


# -- existing merged artifacts unchanged ------------------------------------
def test_sections_1_2_3_provisions_unchanged():
    s1 = _read(os.path.join(ROOT, "data", "articles", "book4_provisions_058_066.json"))
    assert [p["source_article_numbers"] for p in s1["provisions"]] == [[58], [59], [60], [66]]
    s2 = _read(os.path.join(ROOT, "data", "articles", "book4_provisions_067_083.json"))
    assert [p["source_article_numbers"] for p in s2["provisions"]] == [[67, 68], [71], [72], [75], [77]]
    s3 = _read(os.path.join(ROOT, "data", "articles", "book4_provisions_084_102.json"))
    assert [p["source_article_numbers"] for p in s3["provisions"]] == [[85, 87], [92, 93], [99], [101], [102]]


def test_english_reference_unchanged():
    ref = os.path.join(ROOT, "data", "english_reference")
    for fname, exp in (("book1_en_reference.json", list(range(1, 35))),
                       ("book2_en_reference.json", list(range(35, 51))),
                       ("book3_en_reference.json", list(range(51, 58))),
                       ("book4_section1_en_reference.json", [58, 59, 60, 66]),
                       ("book4_section2_en_reference.json", [67, 68, 71, 72, 75, 77]),
                       ("book4_section3_en_reference.json", [85, 87, 92, 93, 99, 101, 102])):
        doc = _read(os.path.join(ref, fname))
        assert [r["article_number"] for r in doc["records"]] == exp, fname
    # No Section-4 English reference file (out of scope for this PR).
    assert not os.path.exists(os.path.join(ref, "book4_section4_en_reference.json"))


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
    s3 = _read(os.path.join(layer, "book4_section3_ar_legal_llm.json"))
    assert [r["article_numbers"] for r in s3["records"]] == [[85, 87], [92, 93], [99], [101], [102]]
    # The Section-4 Arabic LLM layer, if present, mirrors the Section-4 provision
    # groups exactly (added by the Section 4 Arabic LLM PR); shared-validation
    # compatibility — Article 110 stays excluded.
    s4_path = os.path.join(layer, "book4_section4_ar_legal_llm.json")
    if os.path.exists(s4_path):
        s4 = _read(s4_path)
        assert [r["article_numbers"] for r in s4["records"]] == [[108], [113], [115], [117]]


def test_books_1_3_canonical_unchanged():
    for fname, expected in (("book1_articles_001_034.json", list(range(1, 35))),
                            ("book2_articles_035_050.json", list(range(35, 51))),
                            ("book3_articles_051_057.json", list(range(51, 58)))):
        doc = _read(os.path.join(ROOT, "data", "articles", fname))
        nums = [a["article_number"] for a in doc["articles"]]
        assert nums == expected, fname
        for a in doc["articles"]:
            assert a["chinese_translation"].strip(), (fname, a["article_number"])
