#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render Book Four — Section 5 (provisions) outputs.

Writes:
  content/ar/book4_section5.md
  content/zh/book4_section5.md
  content/bilingual/book4_section5_bilingual.md
  dist/book4_section5.html   (clearly labelled: Section 5 provisions ONLY, not full Book Four)

This is a SECTION / provisions view. It is NOT the full Book Four book and does not
write content/{ar,zh,bilingual}/book4.md or dist/book4.html.
"""

from __future__ import annotations

import html as _html
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from saudi_law_corpus import books  # noqa: E402

SRC = os.path.join(ROOT, "data", "articles", "book4_provisions_121_137.json")
MD_AR = os.path.join(ROOT, "content", "ar", "book4_section5.md")
MD_ZH = os.path.join(ROOT, "content", "zh", "book4_section5.md")
MD_BI = os.path.join(ROOT, "content", "bilingual", "book4_section5_bilingual.md")
HTML_OUT = os.path.join(ROOT, "dist", "book4_section5.html")

SECTION_LABEL_AR = "الباب الرابع — القسم 5: المالية والأرباح وتغيير رأس المال (المواد 121–137) — أحكام مختارة فقط"
SECTION_LABEL_ZH = "第四编 — 第五节：财务、利润与资本变更（第121–137条）— 仅择要条款（非全节全文）"
INCOMPLETE_BANNER = ("⚠ 仅为第四编第五节的择要条款（源文件明确涵盖的第123、124、126、127、128、129、130、132、133条）；"
                     "并非完整的第四编。第121、122、125、131、134、135、136、137条未涵盖，仍为 needs_official_text_check。 / "
                     "أحكام مختارة من القسم الخامس فقط (المواد المغطاة صراحةً: 123، 124، 126، 127، 128، 129، 130، 132، 133)؛ "
                     "ليست الباب الرابع كاملاً — المواد 121، 122، 125، 131، 134، 135، 136، 137 غير مغطاة (needs_official_text_check).")


def _load():
    with open(SRC, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text.rstrip("\n") + "\n")


def render_markdown(doc, spec):
    provs = doc["provisions"]
    arts = ", ".join(str(a) for a in doc["explicit_articles"])

    ar = [f"# {SECTION_LABEL_AR}\n",
          f"> {INCOMPLETE_BANNER}\n",
          f"\n**إخلاء مسؤولية:** {spec.disclaimer_ar}\n",
          f"\n**نموذج 1b (أحكام):** أحكام لمواد مغطاة صراحةً فقط ({arts}). باقي مواد القسم غير مغطاة (needs_official_text_check).\n"]
    zh = [f"# {SECTION_LABEL_ZH}\n",
          f"> {INCOMPLETE_BANNER}\n",
          f"\n**免责声明：** {spec.disclaimer_zh}\n",
          f"\n**模型 1b（专题条款）：** 仅涵盖源文件明确的条款（{arts}）。本节其余条款未涵盖（needs_official_text_check）。\n"]
    bi = [f"# {SECTION_LABEL_AR}\n# {SECTION_LABEL_ZH}\n",
          f"> {INCOMPLETE_BANNER}\n",
          f"\n**إخلاء مسؤولية / 免责声明**\n\n- {spec.disclaimer_ar}\n- {spec.disclaimer_zh}\n"]

    for p in provs:
        anums = "، ".join(str(a) for a in p["source_article_numbers"])
        zanums = "、".join(str(a) for a in p["source_article_numbers"])
        ar.append(f"\n## المادة {anums} — {p['provision_title_ar']}\n")
        ar.append(p["arabic_reference_summary"] + "\n")
        zh.append(f"\n## 第{zanums}条 — {p['provision_title_zh']}\n")
        zh.append(p["chinese_translation"] + "\n")
        bi.append(f"\n## المادة {anums} / 第{zanums}条 — "
                  f"{p['provision_title_ar']} · {p['provision_title_zh']}\n")
        bi.append(f"**العربية:** {p['arabic_reference_summary']}\n")
        bi.append(f"\n**中文：** {p['chinese_translation']}\n")

    _write(MD_AR, "\n".join(ar))
    _write(MD_ZH, "\n".join(zh))
    _write(MD_BI, "\n".join(bi))


def render_html(doc, spec):
    e = _html.escape
    provs = doc["provisions"]
    parts = ["<!DOCTYPE html>", '<html lang="zh" dir="ltr"><head>',
             '<meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width, initial-scale=1">',
             f"<title>{e(SECTION_LABEL_ZH)}</title>",
             "<style>body{font-family:'Noto Sans SC',Arial,sans-serif;max-width:960px;"
             "margin:0 auto;padding:20px;line-height:1.7;color:#1c2733}"
             "h1{color:#2f4356;font-size:1.5rem}"
             ".banner{background:#fff3cd;border:1px solid #b3852a;border-radius:8px;padding:12px;margin:12px 0;font-weight:600}"
             ".disc{background:#fbf6ea;border:1px solid #b3852a;border-radius:8px;padding:10px;margin:10px 0}"
             ".prov{border-top:1px dashed #d7dde3;padding-top:10px;margin-top:16px}"
             ".prov h2{color:#2f4356;font-size:1.1rem}"
             "[dir=rtl]{direction:rtl}"
             "table{width:100%;border-collapse:collapse}td{border:1px solid #d7dde3;padding:10px;vertical-align:top;width:50%}"
             "</style></head><body>"]
    parts.append(f"<h1>{e(SECTION_LABEL_ZH)}</h1>")
    parts.append(f'<h1 dir="rtl" lang="ar">{e(SECTION_LABEL_AR)}</h1>')
    parts.append(f'<div class="banner" lang="zh">{e(INCOMPLETE_BANNER)}</div>')
    parts.append(f'<div class="disc" dir="rtl" lang="ar">{e(spec.disclaimer_ar)}</div>')
    parts.append(f'<div class="disc" lang="zh">{e(spec.disclaimer_zh)}</div>')
    for p in provs:
        anums = ", ".join(str(a) for a in p["source_article_numbers"])
        parts.append('<div class="prov">')
        parts.append(f'<h2>المادة {e(anums)} / 第{e(anums)}条 — '
                     f'<span dir="rtl" lang="ar">{e(p["provision_title_ar"])}</span> · '
                     f'<span lang="zh">{e(p["provision_title_zh"])}</span></h2>')
        parts.append('<table><tr>'
                     f'<td dir="rtl" lang="ar">{e(p["arabic_reference_summary"])}</td>'
                     f'<td lang="zh">{e(p["chinese_translation"])}</td></tr></table>')
        parts.append("</div>")
    parts.append('<footer><p>HTML = searchable/copyable Section-5 provisions view · '
                 'NOT the full Book Four.</p></footer>')
    parts.append("</body></html>")
    os.makedirs(os.path.dirname(HTML_OUT), exist_ok=True)
    with open(HTML_OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))


def main():
    doc = _load()
    spec = books.get_book(4)
    render_markdown(doc, spec)
    render_html(doc, spec)
    for p in (MD_AR, MD_ZH, MD_BI, HTML_OUT):
        print("wrote", os.path.relpath(p, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
