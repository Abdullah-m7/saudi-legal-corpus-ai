"""Smoke tests for JSONL and HTML rendering from canonical data."""

import json
import os


def test_build_jsonl(tmp_path, repo_root):
    from saudi_law_corpus.render_jsonl import build_jsonl

    out = tmp_path / "chunks.jsonl"
    n = build_jsonl(out_path=str(out))
    assert n == 34
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 34
    for line in lines:
        obj = json.loads(line)  # each line is valid JSON
        assert obj["book"] == 1
        assert obj["chunk_id"].startswith("sa-companies-book1-art")
        assert obj["chinese_translation"].strip()
        assert obj["arabic_reference_summary"].strip()
        assert obj["disclaimer"]["is_official"] is False


def test_render_html(tmp_path):
    from saudi_law_corpus.render_html import render

    out = tmp_path / "book1.html"
    path = render(out_path=str(out))
    assert os.path.exists(path)
    html = out.read_text(encoding="utf-8")
    # Searchable/copyable: real text present, not an image blob.
    assert "决策评估规则" in html
    assert "المادة" in html or "المواد" in html
    assert "第三十四条" in html or "第34条" in html
    # Coverage matrix and glossary rendered.
    assert "coverage_status" in html
    assert "优先购买权" in html
    # No accidental good-faith-third-party in the Article 8 body. (The translator
    # notes legitimately mention 善意第三人 as the term to AVOID, so we scope the
    # check to Article 8's rendered <article> block, not the whole document.)
    start = html.index('id="art008"')
    art8 = html[start:html.index("</article>", start)]
    assert "善意第三人" not in art8
    assert "第三人" in art8
    # Disclaimer present.
    assert "并非官方译本" in html


def test_html_has_rtl_and_ltr(tmp_path):
    from saudi_law_corpus.render_html import render

    out = tmp_path / "book1.html"
    render(out_path=str(out))
    html = out.read_text(encoding="utf-8")
    assert 'dir="rtl"' in html
    assert 'lang="ar"' in html
    assert 'lang="zh"' in html


def _section(html: str, cls: str) -> str:
    start = html.find(f'<section class="{cls}"')
    assert start != -1, f"section {cls} not found"
    end = html.find("</section>", start)
    return html[start:end]


def test_no_raw_markdown_artifacts_in_rendered_book(tmp_path):
    """Rendered notes/review-log must not leak raw Markdown syntax (10/10 book)."""
    from saudi_law_corpus.render_html import render

    out = tmp_path / "book1.html"
    render(out_path=str(out))
    html = out.read_text(encoding="utf-8")

    # No raw pipe-table syntax anywhere in the rendered document.
    assert "| # |" not in html
    assert "|---" not in html
    assert "| ---" not in html

    notes = _section(html, "notes")
    review = _section(html, "review-log")

    # No literal bold/inline-code/blockquote markers survive in these sections.
    for section_html in (notes, review):
        assert "**" not in section_html
        assert "`" not in section_html            # backticks converted to <code>
        assert "<p>&gt;" not in section_html       # blockquote markers converted


def test_review_log_renders_as_table(tmp_path):
    from saudi_law_corpus.render_html import render

    out = tmp_path / "book1.html"
    render(out_path=str(out))
    review = _section(out.read_text(encoding="utf-8"), "review-log")
    assert '<table class="md-table"' in review
    assert "<th>" in review and "<td>" in review


def test_notes_render_rich_markdown(tmp_path):
    from saudi_law_corpus.render_html import render

    out = tmp_path / "book1.html"
    render(out_path=str(out))
    notes = _section(out.read_text(encoding="utf-8"), "notes")
    assert "<blockquote>" in notes
    assert "<strong>" in notes
    assert "<code>" in notes


def test_needs_official_check_renders_cleanly(tmp_path):
    from saudi_law_corpus.render_html import render

    out = tmp_path / "book1.html"
    render(out_path=str(out))
    html = out.read_text(encoding="utf-8")
    assert "NEEDS_OFFICIAL_TEXT_CHECK" in html
    # Must not appear as a raw Markdown blockquote/bold artifact.
    assert "> **NEEDS_OFFICIAL_TEXT_CHECK**" not in html
    assert "&gt; NEEDS_OFFICIAL_TEXT_CHECK" not in html


def test_trust_wording_not_overclaimed(work):
    """Disclaimers must not claim official verification that has not happened."""
    ts = work["translation_status"]
    assert ts.get("official_text_verified") is False
    # No 'verified against official' style overclaim in the reader-facing text.
    blob = " ".join([ts.get("note_en", ""), ts.get("disclaimer_ar", ""),
                     ts.get("disclaimer_zh", "")])
    assert "经核验" not in blob            # replaced by 经内部审校
    assert "ومحققة" not in blob            # replaced by مراجَعة داخليًا
    assert "internally reviewed" in ts.get("note_en", "").lower()
    assert "尚未逐条对照官方文本" in ts.get("disclaimer_zh", "")
