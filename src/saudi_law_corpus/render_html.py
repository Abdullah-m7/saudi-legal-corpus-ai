"""Render the searchable/copyable HTML book from canonical data.

Uses Jinja2 (``templates/book.html.j2`` + ``templates/styles.css``) when
available; otherwise falls back to an equivalent pure-Python HTML builder so the
book can still be produced with only the standard library.

The HTML is the canonical searchable/copyable text view — all legal text is real
selectable text (no rasterized images). RTL Arabic and LTR Chinese are handled
per cell.
"""

from __future__ import annotations

import copy
import html
import json
import os
from typing import Any, Dict, List, Optional

from . import books

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))

DATA = os.path.join(_REPO_ROOT, "data")
TEMPLATES = os.path.join(_REPO_ROOT, "templates")
DEFAULT_OUT = books.get_book(1).html_out


def _read_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def load_context(book: int = 1) -> Dict[str, Any]:
    spec = books.get_book(book)
    doc = _read_json(spec.articles_json)
    work = _read_json(books.WORK_JSON)
    coverage = _read_json(spec.coverage_json)
    glossary = _read_json(books.GLOSSARY_JSON)
    articles = sorted(doc["articles"], key=lambda a: a["article_number"])

    # Per-book title/scope on top of the shared work metadata (disclaimers,
    # instrument, trust posture stay identical across books).
    work_view = copy.deepcopy(work)
    work_view["title_ar"] = spec.display_title_ar
    work_view["title_zh"] = spec.display_title_zh
    work_view["scope_ar"] = doc.get("scope_ar", work.get("scope_ar", ""))
    work_view["scope_zh"] = doc.get("scope_zh", work.get("scope_zh", ""))

    translator_notes = _maybe_read(spec.translator_notes) if spec.translator_notes else ""
    review_log = _maybe_read(spec.review_log) if spec.review_log else ""

    styles = _read_text(os.path.join(TEMPLATES, "styles.css"))
    return {
        "doc": doc,
        "work": work_view,
        "coverage": coverage,
        "glossary": glossary,
        "articles": articles,
        "translator_notes_md": translator_notes,
        "review_log_md": review_log,
        "translator_notes_html": _md_to_html(translator_notes) if translator_notes else "",
        "review_log_html": _md_to_html(review_log) if review_log else "",
        "styles": styles,
    }


def _maybe_read(path: str) -> str:
    if os.path.exists(path):
        return _read_text(path)
    return ""


def render(out_path: Optional[str] = None, book: int = 1) -> str:
    out_path = out_path or books.get_book(book).html_out
    ctx = load_context(book=book)
    try:
        import jinja2  # type: ignore

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(TEMPLATES),
            autoescape=jinja2.select_autoescape(["html", "j2"]),
        )
        template = env.get_template("book.html.j2")
        html_out = template.render(**ctx)
    except Exception:
        html_out = _fallback_render(ctx)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html_out)
    return out_path


# --------------------------------------------------------------------------
# Pure-Python fallback renderer (no Jinja2 required)
# --------------------------------------------------------------------------
def _md_inline(text: str) -> str:
    """Inline Markdown -> HTML: escape, then `code`, **bold**, *italic*.

    Escaping happens first so user text can never inject HTML; the Markdown
    markers themselves are plain ASCII and survive escaping unchanged.
    """
    import re

    out = html.escape(text)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\*)\*(?!\*)([^*]+)\*(?!\*)", r"<em>\1</em>", out)
    return out


def _is_table_separator(line: str) -> bool:
    s = line.strip()
    if "|" not in s or set(s) - set("|-: "):
        return False
    cells = [c.strip() for c in s.strip("|").split("|")]
    return bool(cells) and all(set(c) <= set("-: ") and "-" in c for c in cells)


def _split_row(line: str) -> List[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _md_to_html(md: str) -> str:
    """Minimal but complete Markdown -> HTML for notes / review log.

    Supports: ATX headings (#..######), unordered lists, blockquotes, GitHub-style
    pipe tables, bold, italics, and inline code. Deterministic and dependency-free
    so the rendered book never leaks raw Markdown syntax (**, `|`, `>`, backticks).
    """
    lines = md.splitlines()
    out: List[str] = []
    i, n = 0, len(lines)
    in_list = False
    quote_buf: List[str] = []

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    def flush_quote():
        if quote_buf:
            inner = " ".join(_md_inline(q) for q in quote_buf)
            out.append(f"<blockquote><p>{inner}</p></blockquote>")
            quote_buf.clear()

    while i < n:
        s = lines[i].rstrip()

        # blockquote (group consecutive '>' lines)
        if s.lstrip().startswith(">"):
            close_list()
            quote_buf.append(s.lstrip()[1:].lstrip())
            i += 1
            continue
        flush_quote()

        if not s.strip():
            close_list()
            i += 1
            continue

        # pipe table: a '|' header line followed by a separator line
        if s.lstrip().startswith("|") and i + 1 < n and _is_table_separator(lines[i + 1]):
            close_list()
            header = _split_row(s)
            i += 2
            body: List[List[str]] = []
            while i < n and lines[i].strip().startswith("|"):
                body.append(_split_row(lines[i]))
                i += 1
            out.append('<table class="md-table"><thead><tr>')
            out.extend(f"<th>{_md_inline(c)}</th>" for c in header)
            out.append("</tr></thead><tbody>")
            for row in body:
                cells = row + [""] * (len(header) - len(row))
                out.append("<tr>" + "".join(f"<td>{_md_inline(c)}</td>" for c in cells) + "</tr>")
            out.append("</tbody></table>")
            continue

        # headings
        heading = None
        for level, prefix in ((4, "### "), (3, "## "), (2, "# ")):
            if s.startswith(prefix):
                heading = (level, s[len(prefix):])
                break
        if s.startswith("#### "):
            heading = (5, s[5:])
        if heading:
            close_list()
            lvl, txt = heading
            out.append(f"<h{lvl}>{_md_inline(txt)}</h{lvl}>")
            i += 1
            continue

        # unordered list
        if s.lstrip().startswith(("- ", "* ")):
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li>{_md_inline(s.lstrip()[2:])}</li>")
            i += 1
            continue

        # paragraph
        close_list()
        out.append(f"<p>{_md_inline(s)}</p>")
        i += 1

    flush_quote()
    close_list()
    return "\n".join(out)


def _fallback_render(ctx: Dict[str, Any]) -> str:
    e = html.escape
    work = ctx["work"]
    ts = work["translation_status"]
    articles = ctx["articles"]
    coverage = ctx["coverage"]
    glossary = ctx["glossary"]

    parts: List[str] = []
    parts.append("<!DOCTYPE html>")
    parts.append('<html lang="zh" dir="ltr">')
    parts.append("<head>")
    parts.append('<meta charset="utf-8">')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    parts.append(f"<title>{e(work['title_zh'])}</title>")
    parts.append(f"<style>{ctx['styles']}</style>")
    parts.append("</head><body>")

    # cover
    parts.append('<header class="cover">')
    parts.append(f'<h1 dir="rtl" lang="ar">{e(work["title_ar"])}</h1>')
    parts.append(f'<h1 lang="zh">{e(work["title_zh"])}</h1>')
    parts.append(f'<p class="scope" dir="rtl" lang="ar">{e(work["scope_ar"])}</p>')
    parts.append(f'<p class="scope" lang="zh">{e(work["scope_zh"])}</p>')
    parts.append(f'<p class="decree" dir="rtl" lang="ar">{e(work["instrument"]["royal_decree_ar"])}</p>')
    parts.append('<hr class="cover-rule">')
    parts.append("</header>")

    # disclaimer
    parts.append('<section class="disclaimer">')
    parts.append("<h2>免责声明 / إخلاء المسؤولية</h2>")
    parts.append(f'<p dir="rtl" lang="ar">{e(ts["disclaimer_ar"])}</p>')
    parts.append(f'<p lang="zh">{e(ts["disclaimer_zh"])}</p>')
    parts.append(f'<p lang="en">{e(ts["binding_text_note_en"])}</p>')
    parts.append("</section>")

    # coverage — compact (print/PDF only)
    parts.append('<section class="coverage coverage-compact">'
                 '<h2>覆盖概览 / ملخص التغطية（المواد 1–34）</h2>')
    parts.append('<table class="compact"><thead><tr>'
                 '<th class="c-num">المادة<br>条</th>'
                 '<th class="c-status">الحالة / 状态</th>'
                 '<th class="c-note">ملاحظة قصيرة / 简注</th>'
                 "</tr></thead><tbody>")
    for r in coverage["rows"]:
        expanded = r["coverage_status"] == "expanded_after_review"
        cls = "expanded" if expanded else ""
        status = "扩充 · expanded" if expanded else "标准 · covered"
        note = r["note"] or f'{r["article_title_zh"]} / {r["article_title_ar"]}'
        parts.append(
            f'<tr class="{cls}"><td class="c-num">{r["article_number"]}</td>'
            f'<td class="c-status" lang="zh">{e(status)}</td>'
            f'<td class="c-note" lang="zh">{e(note)}</td></tr>'
        )
    parts.append("</tbody></table>"
                 '<p class="coverage-hint">完整六列矩阵见 HTML 版本 / '
                 'الجدول الكامل بست أعمدة متاح في نسخة HTML.</p></section>')

    # coverage — full six-column matrix (screen/HTML only)
    parts.append('<section class="coverage coverage-full">'
                 '<h2>覆盖矩阵 / مصفوفة التغطية（المواد 1–34）</h2>')
    parts.append("<table><thead><tr>"
                 "<th>#</th><th>العنوان (AR)</th><th>标题 (ZH)</th>"
                 "<th>coverage_status</th><th>expression_mode</th><th>注 / ملاحظة</th>"
                 "</tr></thead><tbody>")
    for r in coverage["rows"]:
        cls = "expanded" if r["coverage_status"] == "expanded_after_review" else ""
        parts.append(
            f'<tr class="{cls}"><td>{r["article_number"]}</td>'
            f'<td dir="rtl" lang="ar">{e(r["article_title_ar"])}</td>'
            f'<td lang="zh">{e(r["article_title_zh"])}</td>'
            f'<td>{e(r["coverage_status"])}</td>'
            f'<td>{e(r["expression_mode"])}</td>'
            f'<td lang="zh">{e(r["note"])}</td></tr>'
        )
    parts.append("</tbody></table></section>")

    # articles
    parts.append('<section class="articles"><h2>条文 / المواد</h2>')
    current_section = None
    for a in articles:
        if a["section_zh"] != current_section:
            current_section = a["section_zh"]
            parts.append(f'<h3 class="section-head">'
                         f'<span dir="rtl" lang="ar">{e(a["section_ar"])}</span>'
                         f' · <span lang="zh">{e(a["section_zh"])}</span></h3>')
        badge = ("expanded" if a["coverage_status"] == "expanded_after_review" else "covered")
        parts.append(f'<article class="art" id="art{a["article_number"]:03d}">')
        parts.append(
            f'<h4><span class="num">第{a["article_number"]}条 / المادة {a["article_number"]}</span> '
            f'<span dir="rtl" lang="ar">{e(a["article_title_ar"])}</span> · '
            f'<span lang="zh">{e(a["article_title_zh"])}</span> '
            f'<span class="badge {badge}">{badge}</span></h4>'
        )
        parts.append('<table class="pair"><tr>')
        parts.append(f'<td class="ar" dir="rtl" lang="ar">{e(a["arabic_reference_summary"])}</td>')
        parts.append(f'<td class="zh" lang="zh">{e(a["chinese_translation"])}</td>')
        parts.append("</tr></table>")
        if a.get("legal_notes"):
            parts.append('<div class="legal-notes"><strong>ملاحظات / 注释:</strong><ul>')
            for note in a["legal_notes"]:
                parts.append(f'<li dir="rtl" lang="ar">{e(note)}</li>')
            parts.append("</ul></div>")
        parts.append("</article>")
    parts.append("</section>")

    # glossary
    parts.append('<section class="glossary"><h2>术语表 / قاموس المصطلحات</h2>')
    parts.append("<table><thead><tr><th>العربية</th><th>中文</th><th>拼音</th></tr></thead><tbody>")
    for t in glossary["terms"]:
        parts.append(
            f'<tr><td dir="rtl" lang="ar">{e(t["ar"])}</td>'
            f'<td lang="zh">{e(t["zh"])}</td>'
            f'<td>{e(t.get("pinyin",""))}</td></tr>'
        )
    parts.append("</tbody></table></section>")

    # translator notes + review log
    if ctx["translator_notes_md"]:
        parts.append('<section class="notes"><h2>译者注释 / ملاحظات المترجم</h2>')
        parts.append(_md_to_html(ctx["translator_notes_md"]))
        parts.append("</section>")
    if ctx["review_log_md"]:
        parts.append('<section class="review-log"><h2>审校记录 / سجل المراجعة</h2>')
        parts.append(_md_to_html(ctx["review_log_md"]))
        parts.append("</section>")

    parts.append('<footer><p>HTML = searchable/copyable canonical text view · '
                 'PDF = print/share-ready visual version</p></footer>')
    parts.append("</body></html>")
    return "\n".join(parts)


if __name__ == "__main__":
    print(render())
