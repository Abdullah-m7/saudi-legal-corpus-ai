"""Book Four — Section 3 SCOPE DECISION (blocking; no content generated).

Section 3 (general_assemblies, 84–102) is resolved, but the explicit-article set is
ambiguous: the coverage matrix lists 84 and 89 as explicit_in_source while the source
PDF renders no distinct content for them. Per the model-1b rule (no invented content),
this PR generates a scope-decision document ONLY — no provisions, no content, no
coverage changes. These tests lock that in.
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = os.path.join(ROOT, "docs", "book4_preflight", "BOOK4_SECTION3_SCOPE_DECISION.md")
COVERAGE = os.path.join(ROOT, "data", "coverage", "book4_coverage_matrix.json")
ARTICLES_DIR = os.path.join(ROOT, "data", "articles")


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


# -- the decision document exists and names the ambiguity -------------------
def test_scope_decision_doc_exists():
    assert os.path.exists(DOC)
    txt = open(DOC, encoding="utf-8").read()
    assert "general_assemblies" in txt
    assert "84" in txt and "89" in txt
    assert "NEEDS OWNER SCOPE DECISION" in txt.upper() or "NEEDS OWNER" in txt.upper()


# -- NO Section-3 content was generated -------------------------------------
def test_no_section3_provision_dataset():
    for name in ("book4_provisions_084_102.json", "book4_provisions_084_102.jsonl"):
        assert not os.path.exists(os.path.join(ARTICLES_DIR, name)), name


def test_no_book4_articles_files():
    for f in os.listdir(ARTICLES_DIR):
        assert not f.startswith("book4_articles_"), f


def test_no_section3_content_markdown():
    for p in ("content/ar/book4_section3.md", "content/zh/book4_section3.md",
              "content/bilingual/book4_section3_bilingual.md"):
        assert not os.path.exists(os.path.join(ROOT, p)), p


def test_no_full_book4_content():
    for p in ("content/ar/book4.md", "content/zh/book4.md",
              "content/bilingual/book4_bilingual.md"):
        assert not os.path.exists(os.path.join(ROOT, p)), p


# -- coverage matrix unchanged (80 rows; Section-3 explicit list preserved) --
def test_coverage_matrix_intact():
    matrix = _read(COVERAGE)
    rows = matrix["rows"]
    assert len(rows) == 80
    assert [r["article_number"] for r in rows] == list(range(58, 138))
    # Section-3 explicit list is preserved exactly (this PR does not change it).
    s3_explicit = sorted(r["article_number"] for r in rows
                         if r["thematic_section"] == "general_assemblies"
                         and r["source_coverage_status"] == "explicit_in_source")
    assert s3_explicit == [84, 85, 87, 89, 92, 93, 99, 101, 102]
    # No general-assemblies row is provision_created (no provisions were made).
    for r in rows:
        if r["thematic_section"] == "general_assemblies":
            assert r["content_record_status"] != "provision_created", r["article_number"]


def test_section3_uncovered_rows_unchanged():
    by = {r["article_number"]: r for r in _read(COVERAGE)["rows"]}
    for n in (86, 88, 90, 91, 94, 95, 96, 97, 98, 100):
        assert by[n]["source_coverage_status"] == "not_explicit_in_source", n
        assert by[n]["official_text_check"] == "needs_official_text_check", n
        assert by[n]["content_record_status"] == "no_record_until_source_available", n


# -- existing merged artifacts unchanged ------------------------------------
def test_section1_and_section2_provisions_unchanged():
    s1 = _read(os.path.join(ARTICLES_DIR, "book4_provisions_058_066.json"))
    assert [p["source_article_numbers"] for p in s1["provisions"]] == [[58], [59], [60], [66]]
    s2 = _read(os.path.join(ARTICLES_DIR, "book4_provisions_067_083.json"))
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


def test_books_1_3_canonical_unchanged():
    checks = [
        ("book1_articles_001_034.json", list(range(1, 35))),
        ("book2_articles_035_050.json", list(range(35, 51))),
        ("book3_articles_051_057.json", list(range(51, 58))),
    ]
    for fname, expected in checks:
        doc = _read(os.path.join(ARTICLES_DIR, fname))
        nums = [a["article_number"] for a in doc["articles"]]
        assert nums == expected, fname
        for a in doc["articles"]:
            assert a["chinese_translation"].strip(), (fname, a["article_number"])
