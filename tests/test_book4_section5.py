"""Book Four — Section 5 (finance / profits / capital changes) model-1b provisions.

The source PDF and coverage matrix AGREE on the explicit set 123, 124, 126, 127, 128,
129, 130, 132, 133 (grouped [123,124], [126,127], [128,129,130], [132], [133]). No
owner reconciliation was needed. NOT a full Book Four article dataset; NOT a full Book
Four build.
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "book4_provision.schema.json")
DATA = os.path.join(ROOT, "data", "articles", "book4_provisions_121_137.json")
JSONL = os.path.join(ROOT, "data", "articles", "book4_provisions_121_137.jsonl")
COVERAGE = os.path.join(ROOT, "data", "coverage", "book4_coverage_matrix.json")

GROUPS = [[123, 124], [126, 127], [128, 129, 130], [132], [133]]
EXPLICIT = [123, 124, 126, 127, 128, 129, 130, 132, 133]
UNCOVERED = [121, 122, 125, 131, 134, 135, 136, 137]
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
    assert len(lines) == len(_provs()) == 5


def test_no_book4_articles_files():
    for f in os.listdir(os.path.join(ROOT, "data", "articles")):
        assert not f.startswith("book4_articles_"), f


# -- provision scope --------------------------------------------------------
def test_provision_groups_exact():
    assert [p["source_article_numbers"] for p in _provs()] == GROUPS


def test_covered_set_exact():
    covered = sorted({n for p in _provs() for n in p["source_article_numbers"]})
    assert covered == EXPLICIT


def test_no_provision_maps_to_uncovered():
    forbidden = set(UNCOVERED)
    for p in _provs():
        assert not (set(p["source_article_numbers"]) & forbidden), p["provision_id"]
        assert all(121 <= n <= 137 for n in p["source_article_numbers"]), p["provision_id"]


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
        assert p["thematic_section"] == "finance_profits_and_capital_changes", p["provision_id"]


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
def _blob(nums):
    p = next(x for x in _provs() if x["source_article_numbers"] == nums)
    return (p["provision_title_ar"] + " " + p["provision_title_zh"] + " "
            + p["arabic_reference_summary"] + " " + p["chinese_translation"])


def test_reserves_theme():
    b = _blob([123, 124])
    assert "储备" in b and ("احتياطي" in b or "الاحتياط" in b)


def test_capital_increase_theme():
    b = _blob([126, 127])
    assert "增资" in b and "زيادة رأس المال" in b


def test_preemption_theme():
    b = _blob([128, 129, 130])
    assert "优先认购权" in b and "الأولوية" in b


def test_grave_losses_theme():
    b = _blob([132])
    assert "亏损" in b and ("الخسائر" in b or "خسائر" in b)


def test_capital_reduction_theme():
    b = _blob([133])
    assert "减资" in b and "تخفيض رأس المال" in b


# -- coverage matrix --------------------------------------------------------
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


def test_uncovered_section5_rows():
    by = {r["article_number"]: r for r in _read(COVERAGE)["rows"]}
    for n in UNCOVERED:
        assert by[n]["source_coverage_status"] == "not_explicit_in_source", n
        assert by[n]["official_text_check"] == "needs_official_text_check", n
        assert by[n]["content_record_status"] == "no_record_until_source_available", n


def test_prior_owner_reconciled_rows_still_uncovered():
    by = {r["article_number"]: r for r in _read(COVERAGE)["rows"]}
    for n in (84, 89, 100, 110):
        assert by[n]["source_coverage_status"] == "not_explicit_in_source", n
        assert by[n]["official_text_check"] == "needs_official_text_check", n
        assert by[n]["content_record_status"] == "no_record_until_source_available", n


# -- section content only ---------------------------------------------------
def test_section_content_files_exist():
    for p in ("content/ar/book4_section5.md", "content/zh/book4_section5.md",
              "content/bilingual/book4_section5_bilingual.md"):
        assert os.path.exists(os.path.join(ROOT, p)), p


def test_no_full_book4_content():
    for p in ("content/ar/book4.md", "content/zh/book4.md",
              "content/bilingual/book4_bilingual.md"):
        assert not os.path.exists(os.path.join(ROOT, p)), p


# -- existing merged artifacts unchanged ------------------------------------
def test_sections_1_2_3_4_provisions_unchanged():
    s1 = _read(os.path.join(ROOT, "data", "articles", "book4_provisions_058_066.json"))
    assert [p["source_article_numbers"] for p in s1["provisions"]] == [[58], [59], [60], [66]]
    s2 = _read(os.path.join(ROOT, "data", "articles", "book4_provisions_067_083.json"))
    assert [p["source_article_numbers"] for p in s2["provisions"]] == [[67, 68], [71], [72], [75], [77]]
    s3 = _read(os.path.join(ROOT, "data", "articles", "book4_provisions_084_102.json"))
    assert [p["source_article_numbers"] for p in s3["provisions"]] == [[85, 87], [92, 93], [99], [101], [102]]
    s4 = _read(os.path.join(ROOT, "data", "articles", "book4_provisions_103_120.json"))
    assert [p["source_article_numbers"] for p in s4["provisions"]] == [[108], [113], [115], [117]]


def test_english_reference_unchanged():
    ref = os.path.join(ROOT, "data", "english_reference")
    for fname, exp in (("book1_en_reference.json", list(range(1, 35))),
                       ("book2_en_reference.json", list(range(35, 51))),
                       ("book3_en_reference.json", list(range(51, 58))),
                       ("book4_section1_en_reference.json", [58, 59, 60, 66]),
                       ("book4_section2_en_reference.json", [67, 68, 71, 72, 75, 77]),
                       ("book4_section3_en_reference.json", [85, 87, 92, 93, 99, 101, 102]),
                       ("book4_section4_en_reference.json", [108, 113, 115, 117])):
        doc = _read(os.path.join(ref, fname))
        assert [r["article_number"] for r in doc["records"]] == exp, fname
    # No Section-5 English reference file (out of scope for this PR).
    assert not os.path.exists(os.path.join(ref, "book4_section5_en_reference.json"))


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
    s4 = _read(os.path.join(layer, "book4_section4_ar_legal_llm.json"))
    assert [r["article_numbers"] for r in s4["records"]] == [[108], [113], [115], [117]]
    # The Section-5 Arabic LLM layer, if present, mirrors the Section-5 provision
    # groups exactly (added by the Section 5 Arabic LLM PR); shared-validation
    # compatibility — Articles 134 & 135 stay excluded.
    s5_path = os.path.join(layer, "book4_section5_ar_legal_llm.json")
    if os.path.exists(s5_path):
        s5 = _read(s5_path)
        assert [r["article_numbers"] for r in s5["records"]] == [[123, 124], [126, 127], [128, 129, 130], [132], [133]]


def test_books_1_3_canonical_unchanged():
    for fname, expected in (("book1_articles_001_034.json", list(range(1, 35))),
                            ("book2_articles_035_050.json", list(range(35, 51))),
                            ("book3_articles_051_057.json", list(range(51, 58)))):
        doc = _read(os.path.join(ROOT, "data", "articles", fname))
        nums = [a["article_number"] for a in doc["articles"]]
        assert nums == expected, fname
        for a in doc["articles"]:
            assert a["chinese_translation"].strip(), (fname, a["article_number"])
