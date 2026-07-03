"""Book Four — Section 1 (formation & capital) provisions, model 1b.

Provisions exist ONLY for explicitly-covered articles 58, 59, 60, 66.
Articles 61–65 remain uncovered (no provision, needs_official_text_check)."""

import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROV_JSON = os.path.join(ROOT, "data", "articles", "book4_provisions_058_066.json")
PROV_JSONL = os.path.join(ROOT, "data", "articles", "book4_provisions_058_066.jsonl")
COVERAGE = os.path.join(ROOT, "data", "coverage", "book4_coverage_matrix.json")
PROV_SCHEMA = os.path.join(ROOT, "schemas", "book4_provision.schema.json")

ALLOWED = {58, 59, 60, 66}
UNCOVERED = {61, 62, 63, 64, 65}


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def doc():
    return _read(PROV_JSON)


@pytest.fixture(scope="module")
def provisions(doc):
    return doc["provisions"]


@pytest.fixture(scope="module")
def by_article(provisions):
    m = {}
    for p in provisions:
        for n in p["source_article_numbers"]:
            m[n] = p
    return m


# -- files exist ------------------------------------------------------------
def test_provision_json_exists():
    assert os.path.exists(PROV_JSON)


def test_jsonl_line_count_equals_provision_count(provisions):
    assert os.path.exists(PROV_JSONL)
    with open(PROV_JSONL, encoding="utf-8") as fh:
        lines = [ln for ln in fh.read().splitlines() if ln.strip()]
    assert len(lines) == len(provisions)
    for ln in lines:
        obj = json.loads(ln)
        assert obj["book"] == 4
        assert obj["provision_id"].startswith("sa-companies-book4-prov")


def test_no_book4_article_dataset():
    articles_dir = os.path.join(ROOT, "data", "articles")
    for f in os.listdir(articles_dir):
        assert not f.startswith("book4_articles_"), f


# -- article mapping guardrails --------------------------------------------
def test_source_article_numbers_within_allowed(provisions):
    for p in provisions:
        assert set(p["source_article_numbers"]) <= ALLOWED, p["provision_id"]


def test_no_provision_maps_to_uncovered(provisions):
    for p in provisions:
        assert not (set(p["source_article_numbers"]) & UNCOVERED), p["provision_id"]


def test_all_four_explicit_articles_present(by_article):
    assert set(by_article.keys()) == ALLOWED


# -- schema + trust posture -------------------------------------------------
def test_records_pass_provision_schema(provisions):
    schema = _read(PROV_SCHEMA)
    try:
        import jsonschema
        validator = jsonschema.Draft7Validator(schema)
        for p in provisions:
            errs = list(validator.iter_errors(p))
            assert not errs, (p["provision_id"], [e.message for e in errs])
    except ImportError:  # minimal fallback
        for p in provisions:
            for key in schema["required"]:
                assert key in p, (p["provision_id"], key)


def test_trust_posture(provisions):
    for p in provisions:
        assert p["translation_mode"] == "internally_reviewed_summary"
        assert p["source"]["official_text_check"] == "needs_check"
        assert p["source"]["source_coverage_status"] == "explicit_in_source"
        assert p["source"]["input_pdf"] == "inputs/bab4_source.pdf"


def test_no_trust_overclaim():
    blob = open(PROV_JSON, encoding="utf-8").read() + open(PROV_JSONL, encoding="utf-8").read()
    for term in ("verified_summary", "verified", "محققة", "经核验"):
        assert term not in blob, term


# -- coverage preserved -----------------------------------------------------
def test_coverage_still_80_rows_58_137():
    cov = _read(COVERAGE)
    nums = [r["article_number"] for r in cov["rows"]]
    assert len(nums) == 80
    assert nums == list(range(58, 138))


def test_uncovered_61_65_preserved():
    cov = _read(COVERAGE)
    by = {r["article_number"]: r for r in cov["rows"]}
    for n in UNCOVERED:
        assert by[n]["source_coverage_status"] == "not_explicit_in_source"
        assert by[n]["official_text_check"] == "needs_official_text_check"
        assert by[n]["content_record_status"] == "no_record_until_source_available"
        assert by[n]["article_title_ar"] is None and by[n]["article_title_zh"] is None


def test_covered_articles_marked_provision_created():
    cov = _read(COVERAGE)
    by = {r["article_number"]: r for r in cov["rows"]}
    for n in ALLOWED:
        assert by[n]["content_record_status"] == "provision_created", n


# -- terminology ------------------------------------------------------------
def test_required_terminology_in_provisions(by_article):
    def blob(p):
        parts = [p["chinese_translation"], p["arabic_reference_summary"]]
        for t in p.get("terminology", []):
            parts += [t["ar"], t["zh"]]
        parts += p["llm"]["keywords_zh"] + p["llm"]["keywords_ar"]
        return " ".join(parts)

    # Article 58: company form + shareholder
    b58 = blob(by_article[58])
    assert "股份公司" in b58 and "شركة المساهمة" in b58
    assert "股东" in b58 and "المساهم" in b58
    assert "股份" in b58  # السهم = 股份 (股票 = certificate; explained in legal_notes)
    assert any("股票" in n or "股份" in n for n in by_article[58].get("legal_notes", []))
    # Article 59: minimum capital rule present
    b59 = blob(by_article[59])
    assert "500,000" in b59
    assert "已发行资本" in b59 and "رأس المال المصدر" in b59
    # Article 60: issued vs authorized distinguished
    b60 = blob(by_article[60])
    assert "已发行资本" in b60 and "授权资本" in b60
    assert "رأس المال المصدر" in b60 and "رأس المال المصرح به" in b60
    # Article 66: in-kind valuation
    b66 = blob(by_article[66])
    assert "实物出资" in b66 and "الحصص العينية" in b66
    assert "实物出资评估" in b66  # تقييم الحصص العينية
    assert "评估" in b66


# -- no full Book Four content ----------------------------------------------
def test_no_full_book4_content_markdown():
    for rel in ("content/ar/book4.md", "content/zh/book4.md",
                "content/bilingual/book4_bilingual.md"):
        assert not os.path.exists(os.path.join(ROOT, rel)), rel


def test_section_markdown_labeled_section1():
    for rel in ("content/ar/book4_section1.md", "content/zh/book4_section1.md",
                "content/bilingual/book4_section1_bilingual.md"):
        t = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        assert ("القسم 1" in t) or ("第一节" in t) or ("Section 1" in t)
        # Must signal it is not the full book.
        assert ("择要" in t) or ("مختارة" in t) or ("61" in t)


def test_section_html_labeled_and_not_full_book4(tmp_path):
    # Render into a temp dir-independent path by invoking the renderer, then read
    # the committed content markdown label as the primary guarantee. The dist HTML
    # is git-ignored; render it and confirm the Section-1 label + incompleteness.
    import subprocess
    import sys
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "render_book4_section1_html.py")],
                   check=True, capture_output=True)
    html = open(os.path.join(ROOT, "dist", "book4_section1.html"), encoding="utf-8").read()
    assert "第一节" in html or "القسم 1" in html
    assert "并非完整的第四编" in html or "ليست الباب الرابع كاملاً" in html
    assert "61" in html  # names the uncovered articles


def test_validate_book4_passes():
    import sys
    sys.path.insert(0, os.path.join(ROOT, "src"))
    from saudi_law_corpus.validate import validate_book

    ok, report = validate_book(4)
    assert ok, {k: v for k, v in report.items() if v}
