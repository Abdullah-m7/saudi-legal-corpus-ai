"""Book Two (شركة التضامن / 无限公司) — coverage, terminology, trust, rendering."""

import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPECTED = list(range(35, 51))


def _read(path):
    with open(os.path.join(ROOT, path), "r", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def b2_doc():
    return _read("data/articles/book2_articles_035_050.json")


@pytest.fixture(scope="module")
def b2_articles(b2_doc):
    return sorted(b2_doc["articles"], key=lambda a: a["article_number"])


@pytest.fixture(scope="module")
def b2_by_number(b2_articles):
    return {a["article_number"]: a for a in b2_articles}


@pytest.fixture(scope="module")
def b2_coverage():
    return _read("data/coverage/book2_coverage_matrix.json")


# -- coverage --------------------------------------------------------------
def test_exactly_16_articles(b2_articles):
    assert len(b2_articles) == 16


def test_numbers_35_to_50(b2_articles):
    assert [a["article_number"] for a in b2_articles] == EXPECTED


def test_no_duplicate_numbers(b2_articles):
    nums = [a["article_number"] for a in b2_articles]
    assert len(nums) == len(set(nums))


def test_bilingual_present(b2_articles):
    for a in b2_articles:
        assert a["arabic_reference_summary"].strip(), a["article_number"]
        assert a["chinese_translation"].strip(), a["article_number"]
        assert a["article_title_ar"].strip() and a["article_title_zh"].strip()


def test_all_book_2(b2_articles):
    for a in b2_articles:
        assert a["book"] == 2


def test_coverage_matches(b2_coverage, b2_by_number):
    assert len(b2_coverage["rows"]) == 16
    assert b2_coverage["expanded_after_review"] == []
    for r in b2_coverage["rows"]:
        assert r["article_title_zh"] == b2_by_number[r["article_number"]]["article_title_zh"]


# -- trust posture ---------------------------------------------------------
def test_translation_mode_internal(b2_articles):
    for a in b2_articles:
        assert a["translation_mode"] == "internally_reviewed_summary", a["article_number"]


def test_official_text_check_needs_check(b2_articles):
    for a in b2_articles:
        assert a["source"]["official_text_check"] == "needs_check", a["article_number"]


def test_no_verified_trust_wording(b2_articles):
    banned = ["verified_summary", "经核验", "محققة"]
    for a in b2_articles:
        blob = " ".join([a["translation_mode"], a["chinese_translation"],
                         a["arabic_reference_summary"]] + a.get("legal_notes", []))
        for term in banned:
            assert term not in blob, (a["article_number"], term)


def test_chunk_ids(b2_articles):
    for a in b2_articles:
        assert a["llm"]["chunk_id"] == f"sa-companies-book2-art{a['article_number']:03d}"


# -- terminology -----------------------------------------------------------
def test_art35_unlimited_liability_and_merchant(b2_by_number):
    zh = b2_by_number[35]["chinese_translation"]
    assert "无限连带责任" in zh
    assert "商人资格" in zh


def test_art48_benefit_of_excussion(b2_by_number):
    assert "先诉抗辩权" in b2_by_number[48]["chinese_translation"]


def test_art37_representation_complete(b2_by_number):
    zh = b2_by_number[37]["chinese_translation"]
    for token in ("法人合伙人", "法院", "仲裁机构", "第三人"):
        assert token in zh, token


def test_art39_business_asset_terminology(b2_by_number):
    zh = b2_by_number[39]["chinese_translation"]
    assert "营业资产（商业店铺）" in zh
    assert "营业场所（商号）" not in zh


def test_glossary_business_asset_mapping():
    glossary = _read("data/glossary/ar_zh_legal_terms.json")
    terms = {t["ar"]: t["zh"] for t in glossary["terms"]}
    assert terms.get("المحل التجاري (المتجر)") == "营业资产（商业店铺）"
    assert "商号" not in terms.get("المحل التجاري (المتجر)", "")


def test_forbidden_business_premises_term_absent():
    """营业场所（商号）must not appear anywhere in Book Two canonical data/glossary."""
    blobs = [
        open(os.path.join(ROOT, "data/articles/book2_articles_035_050.json"), encoding="utf-8").read(),
        open(os.path.join(ROOT, "data/articles/book2_articles_035_050.jsonl"), encoding="utf-8").read(),
        open(os.path.join(ROOT, "data/glossary/ar_zh_legal_terms.json"), encoding="utf-8").read(),
    ]
    for blob in blobs:
        assert "营业场所（商号）" not in blob


def test_company_form_terminology_glossary():
    glossary = _read("data/glossary/ar_zh_legal_terms.json")
    terms = {t["ar"]: t["zh"] for t in glossary["terms"]}
    zh = terms.get("شركة التضامن", "")
    assert "无限公司" in zh and "普通合伙性质" in zh


def test_legal_personality_caveat_preserved():
    """Saudi شركة التضامن must not be flattened into a Chinese partnership entity."""
    glossary = _read("data/glossary/ar_zh_legal_terms.json")
    blob = " ".join(" ".join(str(v) for v in n.values()) for n in glossary.get("notes", []))
    art35 = _read("data/articles/book2_articles_035_050.json")["articles"][0]
    note_blob = " ".join(art35.get("legal_notes", []))
    combined = blob + note_blob
    assert "法人资格" in combined or "شخصية اعتبارية" in combined
    assert "合伙" in combined  # explicitly contrasts with Chinese partnership entities


# -- validation + rendering ------------------------------------------------
def test_validate_book2_passes():
    import sys
    sys.path.insert(0, os.path.join(ROOT, "src"))
    from saudi_law_corpus.validate import validate_book

    ok, report = validate_book(2)
    problems = {k: v for k, v in report.items() if v}
    assert ok, f"book2 validation problems: {problems}"


def test_loader_book2():
    import sys
    sys.path.insert(0, os.path.join(ROOT, "src"))
    from saudi_law_corpus import list_articles, get_article

    assert len(list_articles(book=2)) == 16
    assert get_article(35, book=2)["article_title_zh"] == "无限公司的定义"
    # Book One remains reachable and unchanged.
    assert len(list_articles(book=1)) == 34


def test_render_book2_html(tmp_path):
    import sys
    sys.path.insert(0, os.path.join(ROOT, "src"))
    from saudi_law_corpus.render_html import render

    out = tmp_path / "book2.html"
    render(out_path=str(out), book=2)
    html = out.read_text(encoding="utf-8")
    assert "无限公司" in html
    assert "无限连带责任" in html
    assert "第三十五条" in html or "第35条" in html
    assert "并非官方译本" in html
    # No raw Markdown table pipes leak anywhere in the rendered book.
    assert "| # |" not in html
    assert "|---" not in html


def test_render_book2_notes_clean(tmp_path):
    import sys
    sys.path.insert(0, os.path.join(ROOT, "src"))
    from saudi_law_corpus.render_html import render

    out = tmp_path / "book2.html"
    render(out_path=str(out), book=2)
    html = out.read_text(encoding="utf-8")
    for cls in ("notes", "review-log"):
        start = html.find(f'<section class="{cls}"')
        if start != -1:
            section = html[start:html.find("</section>", start)]
            assert "**" not in section
            assert "`" not in section
            assert "<p>&gt;" not in section
