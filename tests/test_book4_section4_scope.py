"""Book Four — Section 4 (shares / debt instruments / sukuk) SCOPE DECISION.

The next thematic section after Section 3 is unambiguous — الأسهم وأدوات الدين
والصكوك / 股份、债务工具与融资凭证, Articles 103–120 — but the explicit-article set is
NOT: the coverage matrix marks Article 110 `explicit_in_source` while the source PDF
renders no distinct provision for it (110 is only cross-referenced with 89 under the
Article-108 class/type rule).

The original scope-decision PR documented that ambiguity only. Owner then selected
Option 1 (reconcile to the source), applied by the Section-4 reconciled-provisions PR:
Article 110 reclassified to not_explicit_in_source; provisions created for [108],[113],
[115],[117]. The assertions below are updated (shared-validation compatibility) to the
resolved state while keeping the scope-decision doc's history checks.
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECISION = os.path.join(ROOT, "docs", "book4_preflight", "BOOK4_SECTION4_SCOPE_DECISION.md")
COVERAGE = os.path.join(ROOT, "data", "coverage", "book4_coverage_matrix.json")
ARTICLES_DIR = os.path.join(ROOT, "data", "articles")

# Articles the source PDF distinctly renders in 103–120 (agree with the matrix).
PDF_EXPLICIT = [108, 113, 115, 117]
# The single conflicting article (matrix=explicit, PDF=cross-reference only).
CONFLICT = 110
# Uncovered rows in 103–120 that both sources agree on.
AGREED_UNCOVERED = [103, 104, 105, 106, 107, 109, 111, 112, 114, 116, 118, 119, 120]


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


# -- the decision doc exists and records the ambiguity ----------------------
def test_scope_decision_doc_exists():
    assert os.path.exists(DECISION)


def test_doc_records_section_and_range():
    txt = open(DECISION, encoding="utf-8").read()
    assert "NEEDS OWNER SCOPE DECISION" in txt
    assert "الأسهم وأدوات الدين والصكوك" in txt
    assert "股份、债务工具与融资凭证" in txt
    assert "103–120" in txt or "103-120" in txt


def test_doc_documents_article_110_conflict():
    txt = open(DECISION, encoding="utf-8").read()
    assert "110" in txt
    # 110 is framed as the Section-4 twin of Section-3's reclassified Article 89.
    assert "89" in txt
    assert "reconcile" in txt.lower()


# -- resolved state: reconciled provisions + content now exist (Option 1) ----
def test_section4_provision_file_present_with_reconciled_groups():
    # Shared-validation compatibility: the reconciled-provisions PR created these.
    path = os.path.join(ARTICLES_DIR, "book4_provisions_103_120.json")
    assert os.path.exists(path)
    assert os.path.exists(os.path.join(ARTICLES_DIR, "book4_provisions_103_120.jsonl"))
    doc = _read(path)
    assert [p["source_article_numbers"] for p in doc["provisions"]] == [[108], [113], [115], [117]]


def test_no_book4_articles_files():
    for f in os.listdir(ARTICLES_DIR):
        assert not f.startswith("book4_articles_"), f


def test_section4_content_files_present():
    for p in ("content/ar/book4_section4.md", "content/zh/book4_section4.md",
              "content/bilingual/book4_section4_bilingual.md"):
        assert os.path.exists(os.path.join(ROOT, p)), p


def test_no_full_book4_content():
    for p in ("content/ar/book4.md", "content/zh/book4.md",
              "content/bilingual/book4_bilingual.md"):
        assert not os.path.exists(os.path.join(ROOT, p)), p


# -- coverage matrix still 80 rows; 110 reclassified per owner Option 1 ------
def test_coverage_matrix_still_80_rows():
    rows = _read(COVERAGE)["rows"]
    assert len(rows) == 80
    assert [r["article_number"] for r in rows] == list(range(58, 138))


def test_article_110_row_reclassified_uncovered():
    by = {r["article_number"]: r for r in _read(COVERAGE)["rows"]}
    # Owner Option 1 reconciliation: 110 moved from explicit_in_source to uncovered.
    assert by[CONFLICT]["source_coverage_status"] == "not_explicit_in_source", CONFLICT
    assert by[CONFLICT]["official_text_check"] == "needs_official_text_check", CONFLICT
    assert by[CONFLICT]["content_record_status"] == "no_record_until_source_available", CONFLICT


def test_pdf_explicit_rows_untouched():
    by = {r["article_number"]: r for r in _read(COVERAGE)["rows"]}
    for n in PDF_EXPLICIT:
        assert by[n]["source_coverage_status"] == "explicit_in_source", n


def test_agreed_uncovered_rows_untouched():
    by = {r["article_number"]: r for r in _read(COVERAGE)["rows"]}
    for n in AGREED_UNCOVERED:
        assert by[n]["source_coverage_status"] == "not_explicit_in_source", n
        assert by[n]["official_text_check"] == "needs_official_text_check", n
        assert by[n]["content_record_status"] == "no_record_until_source_available", n


# -- existing merged artifacts unchanged ------------------------------------
def test_sections_1_2_3_provisions_unchanged():
    s1 = _read(os.path.join(ARTICLES_DIR, "book4_provisions_058_066.json"))
    assert [p["source_article_numbers"] for p in s1["provisions"]] == [[58], [59], [60], [66]]
    s2 = _read(os.path.join(ARTICLES_DIR, "book4_provisions_067_083.json"))
    assert [p["source_article_numbers"] for p in s2["provisions"]] == [[67, 68], [71], [72], [75], [77]]
    s3 = _read(os.path.join(ARTICLES_DIR, "book4_provisions_084_102.json"))
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
    # The Section-4 English reference file, if present, contains exactly the
    # reconciled provision-covered articles (added by the Section 4 English
    # reference PR); shared-validation compatibility — Article 110 stays excluded.
    s4_ref = os.path.join(ref, "book4_section4_en_reference.json")
    if os.path.exists(s4_ref):
        doc = _read(s4_ref)
        assert [r["article_number"] for r in doc["records"]] == [108, 113, 115, 117]


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


def test_books_1_3_canonical_unchanged():
    for fname, expected in (("book1_articles_001_034.json", list(range(1, 35))),
                            ("book2_articles_035_050.json", list(range(35, 51))),
                            ("book3_articles_051_057.json", list(range(51, 58)))):
        doc = _read(os.path.join(ARTICLES_DIR, fname))
        nums = [a["article_number"] for a in doc["articles"]]
        assert nums == expected, fname
        for a in doc["articles"]:
            assert a["chinese_translation"].strip(), (fname, a["article_number"])
