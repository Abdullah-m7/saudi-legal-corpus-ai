"""Render the Arabic / Chinese / bilingual Markdown books from canonical data.

Readable Markdown outputs are generated from the canonical JSON so they never
drift from the source of truth.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))

DATA = os.path.join(_REPO_ROOT, "data")
CONTENT = os.path.join(_REPO_ROOT, "content")


def _read(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _load() -> Dict[str, Any]:
    doc = _read(os.path.join(DATA, "articles", "book1_articles_001_034.json"))
    work = _read(os.path.join(DATA, "metadata", "work.json"))
    return {
        "work": work,
        "articles": sorted(doc["articles"], key=lambda a: a["article_number"]),
    }


def _write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text.rstrip("\n") + "\n")


def render_arabic(ctx: Dict[str, Any]) -> str:
    work, arts = ctx["work"], ctx["articles"]
    ts = work["translation_status"]
    out: List[str] = [f"# {work['title_ar']}\n", f"> {work['scope_ar']}\n",
                      f"> {work['instrument']['royal_decree_ar']}\n",
                      f"\n**إخلاء مسؤولية:** {ts['disclaimer_ar']}\n"]
    cur = None
    for a in arts:
        if a["section_ar"] != cur:
            cur = a["section_ar"]
            out.append(f"\n## {a['section_ar']}\n")
        tag = " — (توسعة بعد المراجعة)" if a["coverage_status"] == "expanded_after_review" else ""
        out.append(f"\n### المادة {a['article_number']} — {a['article_title_ar']}{tag}\n")
        out.append(a["arabic_reference_summary"] + "\n")
        for n in a.get("legal_notes", []):
            out.append(f"\n> {n}\n")
    return "\n".join(out)


def render_chinese(ctx: Dict[str, Any]) -> str:
    work, arts = ctx["work"], ctx["articles"]
    ts = work["translation_status"]
    out: List[str] = [f"# {work['title_zh']}\n", f"> {work['scope_zh']}\n",
                      f"> {work['instrument']['royal_decree_zh']}\n",
                      f"\n**免责声明：** {ts['disclaimer_zh']}\n"]
    cur = None
    for a in arts:
        if a["section_zh"] != cur:
            cur = a["section_zh"]
            out.append(f"\n## {a['section_zh']}\n")
        tag = "（经审校扩充）" if a["coverage_status"] == "expanded_after_review" else ""
        out.append(f"\n### 第{a['article_number']}条 — {a['article_title_zh']}{tag}\n")
        out.append(a["chinese_translation"] + "\n")
    return "\n".join(out)


def render_bilingual(ctx: Dict[str, Any]) -> str:
    work, arts = ctx["work"], ctx["articles"]
    ts = work["translation_status"]
    out: List[str] = [f"# {work['title_ar']} · {work['title_zh']}\n",
                      f"> {work['scope_ar']}\n>\n> {work['scope_zh']}\n",
                      f"\n**إخلاء مسؤولية / 免责声明**\n\n- {ts['disclaimer_ar']}\n- {ts['disclaimer_zh']}\n"]
    cur = None
    for a in arts:
        if a["section_zh"] != cur:
            cur = a["section_zh"]
            out.append(f"\n## {a['section_ar']} · {a['section_zh']}\n")
        badge = ("`expanded_after_review`" if a["coverage_status"] == "expanded_after_review"
                 else "`covered`")
        out.append(f"\n### المادة {a['article_number']} / 第{a['article_number']}条 — "
                   f"{a['article_title_ar']} · {a['article_title_zh']} {badge}\n")
        out.append(f"**العربية:** {a['arabic_reference_summary']}\n")
        out.append(f"\n**中文：** {a['chinese_translation']}\n")
        for n in a.get("legal_notes", []):
            out.append(f"\n> ملاحظة / 注释: {n}\n")
    return "\n".join(out)


def render_all() -> List[str]:
    ctx = _load()
    targets = [
        (os.path.join(CONTENT, "ar", "book1.md"), render_arabic(ctx)),
        (os.path.join(CONTENT, "zh", "book1.md"), render_chinese(ctx)),
        (os.path.join(CONTENT, "bilingual", "book1_bilingual.md"), render_bilingual(ctx)),
    ]
    for path, text in targets:
        _write(path, text)
    return [p for p, _ in targets]


if __name__ == "__main__":
    for p in render_all():
        print("wrote", p)
