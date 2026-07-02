"""Build the RAG-friendly JSONL from the canonical article JSON.

One line per article, self-contained. The JSONL is a derivative artifact; the
JSON under ``data/articles`` remains canonical.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from . import books

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))

# Book One defaults kept as module constants for backward compatibility.
ARTICLES_JSON = books.get_book(1).articles_json
WORK_JSON = books.WORK_JSON
OUT_JSONL = books.get_book(1).articles_jsonl


def _read(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def build_chunk(article: Dict[str, Any], work: Dict[str, Any]) -> Dict[str, Any]:
    llm = article.get("llm", {})
    return {
        "chunk_id": llm.get("chunk_id"),
        "book": article["book"],
        "article_number": article["article_number"],
        "retrieval_title": llm.get("retrieval_title"),
        "article_title_ar": article["article_title_ar"],
        "article_title_zh": article["article_title_zh"],
        "section_ar": article["section_ar"],
        "section_zh": article["section_zh"],
        "arabic_reference_summary": article["arabic_reference_summary"],
        "chinese_translation": article["chinese_translation"],
        "summary_en": llm.get("summary_en", ""),
        "keywords_ar": llm.get("keywords_ar", []),
        "keywords_zh": llm.get("keywords_zh", []),
        "legal_risk_tags": article.get("risk_flags", []),
        "coverage_status": article["coverage_status"],
        "translation_mode": article["translation_mode"],
        "official_text_check": article.get("source", {}).get("official_text_check"),
        "disclaimer": {
            "is_official": False,
            "is_legal_advice": False,
            "note_en": work.get("translation_status", {}).get("note_en", ""),
        },
        "source": {
            "work_id": work.get("work_id"),
            "input_pdf": article.get("source", {}).get("input_pdf"),
            "royal_decree_ar": work.get("instrument", {}).get("royal_decree_ar"),
        },
    }


def build_jsonl(articles_json: Optional[str] = None,
                work_json: str = WORK_JSON,
                out_path: Optional[str] = None,
                book: int = 1) -> int:
    spec = books.get_book(book)
    articles_json = articles_json or spec.articles_json
    out_path = out_path or spec.articles_jsonl
    doc = _read(articles_json)
    work = _read(work_json)
    articles: List[Dict[str, Any]] = sorted(
        doc["articles"], key=lambda a: a["article_number"]
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        for a in articles:
            chunk = build_chunk(a, work)
            fh.write(json.dumps(chunk, ensure_ascii=False))
            fh.write("\n")
    return len(articles)


if __name__ == "__main__":
    n = build_jsonl()
    print(f"wrote {OUT_JSONL} with {n} chunks")
