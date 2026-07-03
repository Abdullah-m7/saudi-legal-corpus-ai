"""Book Four model-1b infrastructure gate. Book Four content is NOT generated;
these tests assert the infrastructure + guardrails only."""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COVERAGE = os.path.join(ROOT, "data", "coverage", "book4_coverage_matrix.json")
MODEL_DOC = os.path.join(ROOT, "docs", "book4_preflight", "BOOK4_MODEL_1B_DECISION.md")
PROV_SCHEMA = os.path.join(ROOT, "schemas", "book4_provision.schema.json")

BOOK4_RANGE = list(range(58, 138))


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def _coverage():
    return json.loads(_read(COVERAGE))


# -- documents & schema exist ----------------------------------------------
def test_model_decision_doc_exists():
    assert os.path.exists(MODEL_DOC)
    t = _read(MODEL_DOC)
    assert "model 1b" in t.lower() or "model-1b" in t.lower() or "model 1b" in t
    assert "needs_official_text_check" in t


def test_provision_schema_exists():
    assert os.path.exists(PROV_SCHEMA)
    schema = json.loads(_read(PROV_SCHEMA))
    assert schema["properties"]["book"]["const"] == 4
    assert "source_article_numbers" in schema["properties"]


def test_coverage_matrix_exists():
    assert os.path.exists(COVERAGE)


# -- coverage matrix shape --------------------------------------------------
def test_coverage_has_exactly_80_rows():
    assert len(_coverage()["rows"]) == 80


def test_coverage_article_numbers_58_137():
    nums = [r["article_number"] for r in _coverage()["rows"]]
    assert nums == BOOK4_RANGE


def test_coverage_no_duplicates():
    nums = [r["article_number"] for r in _coverage()["rows"]]
    assert len(nums) == len(set(nums))


def test_uncovered_rows_marked_needs_check():
    for r in _coverage()["rows"]:
        if r["source_coverage_status"] == "not_explicit_in_source":
            assert r["official_text_check"] == "needs_official_text_check", r["article_number"]
            assert r["content_record_status"] == "no_record_until_source_available"


def test_no_invented_titles_or_text_in_coverage():
    for r in _coverage()["rows"]:
        # No legal provision text on coverage rows.
        assert "arabic_reference_summary" not in r
        assert "chinese_translation" not in r
        # Uncovered rows carry no invented titles.
        if r["source_coverage_status"] == "not_explicit_in_source":
            assert r.get("article_title_ar") in (None, "", "NEEDS_OFFICIAL_TEXT_CHECK")
            assert r.get("article_title_zh") in (None, "", "NEEDS_OFFICIAL_TEXT_CHECK")


def test_no_trust_overclaim_in_coverage_data():
    # Strict no-banned-terms applies to the machine coverage data. (The model-1b
    # doc legitimately names these terms in its "never use" prohibition.)
    banned = ["verified_summary", "verified", "محققة", "经核验"]
    text = _read(COVERAGE)
    for term in banned:
        assert term not in text, term


def test_model_doc_does_not_overclaim_verification():
    # The doc must not CLAIM the translation is officially verified.
    t = _read(MODEL_DOC)
    for overclaim in ("经核验版", "官方核验", "已核验", "逐条对照官方"):
        assert overclaim not in t, overclaim
    assert "needs_official_text_check" in t


# -- no full Book Four content exists ---------------------------------------
def test_no_book4_article_dataset():
    articles_dir = os.path.join(ROOT, "data", "articles")
    for f in os.listdir(articles_dir):
        assert not f.startswith("book4_articles_"), f
        # provisions dataset must also not exist yet
        assert not (f.startswith("book4_provisions") and f.endswith((".json", ".jsonl"))), f


def test_no_book4_content_markdown():
    for rel in ("content/ar/book4.md", "content/zh/book4.md",
                "content/bilingual/book4_bilingual.md"):
        assert not os.path.exists(os.path.join(ROOT, rel)), rel


# -- registry disclaimer scope ----------------------------------------------
def test_registry_book4_disclaimer_scope():
    import sys
    sys.path.insert(0, os.path.join(ROOT, "src"))
    from saudi_law_corpus import books

    spec = books.get_book(4)
    assert spec.mode == "model_1b_thematic_provisions"
    ar, zh = spec.disclaimer_ar, spec.disclaimer_zh
    assert "الباب الرابع" in ar and "58" in ar and "137" in ar and "شركة المساهمة" in ar
    assert "第四编" in zh and "第五十八条" in zh and "第一百三十七条" in zh and "股份公司" in zh
    for bad in ("الباب الأول", "الباب الثاني", "الباب الثالث", "第一编", "第二编", "第三编"):
        assert bad not in ar and bad not in zh


def test_validate_book4_passes():
    import sys
    sys.path.insert(0, os.path.join(ROOT, "src"))
    from saudi_law_corpus.validate import validate_book

    ok, report = validate_book(4)
    problems = {k: v for k, v in report.items() if v}
    assert ok, f"book4 validation problems: {problems}"


def test_prior_books_still_validate():
    import sys
    sys.path.insert(0, os.path.join(ROOT, "src"))
    from saudi_law_corpus.validate import validate_book

    for b in (1, 2, 3):
        ok, report = validate_book(b)
        assert ok, (b, {k: v for k, v in report.items() if v})
