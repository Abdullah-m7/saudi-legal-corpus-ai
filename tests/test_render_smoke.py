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
