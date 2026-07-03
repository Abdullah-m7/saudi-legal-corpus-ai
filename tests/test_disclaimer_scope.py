"""Book-specific disclaimer scope (hotfix): each book's disclaimer must name its
own scope, never Book One's, in generated Markdown and rendered HTML."""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(path):
    with open(os.path.join(ROOT, path), "r", encoding="utf-8") as fh:
        return fh.read()


# -- Book Two Markdown -----------------------------------------------------
def test_book2_ar_md_disclaimer_scope():
    t = _read("content/ar/book2.md")
    assert "الباب الثاني" in t
    assert "35–50" in t
    assert "الباب الأول" not in t
    assert "1–34" not in t


def test_book2_zh_md_disclaimer_scope():
    t = _read("content/zh/book2.md")
    assert "第二编" in t
    assert "第三十五条" in t and "第五十条" in t
    assert "第一编" not in t
    assert "第一条至第三十四条" not in t


# -- Book Three Markdown ---------------------------------------------------
def test_book3_ar_md_disclaimer_scope():
    t = _read("content/ar/book3.md")
    assert "الباب الثالث" in t
    assert "51–57" in t
    assert "الباب الأول" not in t
    assert "1–34" not in t


def test_book3_zh_md_disclaimer_scope():
    t = _read("content/zh/book3.md")
    assert "第三编" in t
    assert "第五十一条" in t and "第五十七条" in t
    assert "第一编" not in t
    assert "第一条至第三十四条" not in t


# -- Book One still correct ------------------------------------------------
def test_book1_zh_md_disclaimer_scope():
    t = _read("content/zh/book1.md")
    assert "第一编（第一条至第三十四条）" in t
    assert "第二编" not in t and "第三编" not in t


def test_book1_ar_md_disclaimer_scope():
    t = _read("content/ar/book1.md")
    assert "الباب الأول" in t and "1–34" in t


# -- Shared trust wording preserved in every book's disclaimer -------------
def test_trust_wording_all_books():
    for path in ("content/zh/book1.md", "content/zh/book2.md", "content/zh/book3.md"):
        t = _read(path)
        assert "经内部审校" in t
        assert "并非官方译本" in t
        assert "经核验" not in t  # must not overclaim official verification


# -- Rendered HTML uses the correct book-specific disclaimer ----------------
def _render(book, tmp_path):
    import sys
    sys.path.insert(0, os.path.join(ROOT, "src"))
    from saudi_law_corpus.render_html import render

    out = tmp_path / f"book{book}.html"
    render(out_path=str(out), book=book)
    return out.read_text(encoding="utf-8")


def test_book2_html_disclaimer_scope(tmp_path):
    html = _render(2, tmp_path)
    assert "第二编（无限公司，第三十五条至第五十条）" in html
    assert "第一编（第一条至第三十四条）" not in html
    assert "الباب الثاني" in html


def test_book3_html_disclaimer_scope(tmp_path):
    html = _render(3, tmp_path)
    assert "第三编（两合公司，第五十一条至第五十七条）" in html
    assert "第一编（第一条至第三十四条）" not in html
    assert "الباب الثالث" in html


def test_book1_html_disclaimer_scope(tmp_path):
    html = _render(1, tmp_path)
    assert "第一编（第一条至第三十四条）" in html


def test_registry_disclaimers_are_distinct():
    import sys
    sys.path.insert(0, os.path.join(ROOT, "src"))
    from saudi_law_corpus import books

    zh = {b: books.get_book(b).disclaimer_zh for b in (1, 2, 3)}
    assert len({zh[1], zh[2], zh[3]}) == 3  # each book has its own scope
    assert "第一编" in zh[1] and "第二编" in zh[2] and "第三编" in zh[3]
