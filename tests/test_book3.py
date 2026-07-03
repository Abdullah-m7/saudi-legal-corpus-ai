"""Book Three (شركة التوصية البسيطة / 两合公司) — coverage, terminology, trust."""

import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPECTED = list(range(51, 58))


def _read(path):
    with open(os.path.join(ROOT, path), "r", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def b3_doc():
    return _read("data/articles/book3_articles_051_057.json")


@pytest.fixture(scope="module")
def b3_articles(b3_doc):
    return sorted(b3_doc["articles"], key=lambda a: a["article_number"])


@pytest.fixture(scope="module")
def b3_by_number(b3_articles):
    return {a["article_number"]: a for a in b3_articles}


@pytest.fixture(scope="module")
def b3_coverage():
    return _read("data/coverage/book3_coverage_matrix.json")


@pytest.fixture(scope="module")
def glossary():
    return _read("data/glossary/ar_zh_legal_terms.json")


# -- coverage --------------------------------------------------------------
def test_exactly_7_articles(b3_articles):
    assert len(b3_articles) == 7


def test_numbers_51_to_57(b3_articles):
    assert [a["article_number"] for a in b3_articles] == EXPECTED


def test_no_duplicate_numbers(b3_articles):
    nums = [a["article_number"] for a in b3_articles]
    assert len(nums) == len(set(nums))


def test_bilingual_present(b3_articles):
    for a in b3_articles:
        assert a["arabic_reference_summary"].strip(), a["article_number"]
        assert a["chinese_translation"].strip(), a["article_number"]
        assert a["article_title_ar"].strip() and a["article_title_zh"].strip()


def test_all_book_3(b3_articles):
    for a in b3_articles:
        assert a["book"] == 3


def test_coverage_matches(b3_coverage, b3_by_number):
    assert len(b3_coverage["rows"]) == 7
    assert b3_coverage["expanded_after_review"] == []
    for r in b3_coverage["rows"]:
        assert r["article_title_zh"] == b3_by_number[r["article_number"]]["article_title_zh"]


# -- trust posture ---------------------------------------------------------
def test_translation_mode_internal(b3_articles):
    for a in b3_articles:
        assert a["translation_mode"] == "internally_reviewed_summary", a["article_number"]


def test_official_text_check_needs_check(b3_articles):
    for a in b3_articles:
        assert a["source"]["official_text_check"] == "needs_check", a["article_number"]
        assert a["source"]["input_pdf"] == "inputs/bab3_source.pdf"


def test_no_verified_trust_wording(b3_articles):
    banned = ["verified_summary", "verified", "经核验", "محققة"]
    for a in b3_articles:
        blob = " ".join([a["translation_mode"], a["chinese_translation"],
                         a["arabic_reference_summary"]] + a.get("legal_notes", []))
        for term in banned:
            assert term not in blob, (a["article_number"], term)


def test_chunk_ids(b3_articles):
    for a in b3_articles:
        assert a["llm"]["chunk_id"] == f"sa-companies-book3-art{a['article_number']:03d}"


# -- terminology -----------------------------------------------------------
def test_company_form_glossary(glossary):
    terms = {t["ar"]: t["zh"] for t in glossary["terms"]}
    zh = terms.get("شركة التوصية البسيطة", "")
    assert "两合公司" in zh and "有限合伙性质" in zh


def test_partner_terms_glossary(glossary):
    terms = {t["ar"]: t["zh"] for t in glossary["terms"]}
    gen = terms.get("الشريك المتضامن", "")
    assert "普通合伙人" in gen and "无限责任" in gen
    assert terms.get("الشريك الموصي") == "有限合伙人"


def test_required_book3_glossary_terms(glossary):
    terms = {t["ar"]: t["zh"] for t in glossary["terms"]}
    assert terms.get("المسؤولية المحدودة") == "有限责任"
    assert terms.get("المسؤولية غير المحدودة") == "无限责任"
    assert terms.get("الإدارة الخارجية") == "对外管理"
    assert terms.get("حصة الشريك الموصي") == "有限合伙人出资份额"
    assert "商人资格" in terms.get("صفة التاجر", "")


def test_art51_limited_partner_liability_and_no_merchant(b3_by_number):
    zh = b3_by_number[51]["chinese_translation"]
    assert "有限合伙人" in zh
    assert "出资额为限" in zh
    assert "有限合伙人不取得商人资格" in zh
    assert "无限连带责任" in zh  # general partner


def test_art53_no_external_management(b3_by_number):
    zh = b3_by_number[53]["chinese_translation"]
    assert "有限合伙人" in zh
    assert "对外管理" in zh
    assert "不得" in zh
    assert "连带责任" in zh          # liability consequence captured
    assert "对内管理" in zh          # internal management allowed


def test_art57_insolvency_term(b3_by_number):
    zh = b3_by_number[57]["chinese_translation"]
    assert "无力偿债" in zh
    assert "民事破产" not in zh
    assert "资不抵债" not in zh


def test_legal_personality_caveat_preserved(b3_by_number):
    note_blob = " ".join(b3_by_number[51].get("legal_notes", []))
    assert "有限合伙企业" in note_blob
    assert "الشخصية الاعتبارية" in note_blob


# -- validation + rendering ------------------------------------------------
def test_validate_book3_passes():
    import sys
    sys.path.insert(0, os.path.join(ROOT, "src"))
    from saudi_law_corpus.validate import validate_book

    ok, report = validate_book(3)
    problems = {k: v for k, v in report.items() if v}
    assert ok, f"book3 validation problems: {problems}"


def test_loader_book3():
    import sys
    sys.path.insert(0, os.path.join(ROOT, "src"))
    from saudi_law_corpus import list_articles, get_article

    assert len(list_articles(book=3)) == 7
    assert get_article(51, book=3)["article_title_zh"] == "两合公司的定义"
    # Prior books remain reachable and unchanged.
    assert len(list_articles(book=1)) == 34
    assert len(list_articles(book=2)) == 16


def test_render_book3_html(tmp_path):
    import sys
    sys.path.insert(0, os.path.join(ROOT, "src"))
    from saudi_law_corpus.render_html import render

    out = tmp_path / "book3.html"
    render(out_path=str(out), book=3)
    html = out.read_text(encoding="utf-8")
    assert "两合公司" in html
    assert "有限合伙人" in html
    assert "第五十一条" in html or "第51条" in html
    assert "并非官方译本" in html
    assert "| # |" not in html
    assert "|---" not in html


def test_render_book3_notes_clean(tmp_path):
    import sys
    sys.path.insert(0, os.path.join(ROOT, "src"))
    from saudi_law_corpus.render_html import render

    out = tmp_path / "book3.html"
    render(out_path=str(out), book=3)
    html = out.read_text(encoding="utf-8")
    for cls in ("notes", "review-log"):
        start = html.find(f'<section class="{cls}"')
        if start != -1:
            section = html[start:html.find("</section>", start)]
            assert "**" not in section
            assert "`" not in section
            assert "<p>&gt;" not in section
