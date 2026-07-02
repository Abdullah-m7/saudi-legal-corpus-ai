"""Loader / query API for the Book One corpus.

Standard-library only. Resolves the repository ``data`` directory relative to
this file so it works regardless of the current working directory.

Example
-------
>>> from saudi_law_corpus import list_articles, get_article, search_keyword
>>> len(list_articles())
34
>>> get_article(8)["article_title_zh"]
'设立文件及修改的登记'
>>> [a["article_number"] for a in search_keyword("破产法")]
[29]
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

# Repository root: .../src/saudi_law_corpus/load.py -> repo root is three up.
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))

ARTICLES_JSON = os.path.join(
    _REPO_ROOT, "data", "articles", "book1_articles_001_034.json"
)
GLOSSARY_JSON = os.path.join(
    _REPO_ROOT, "data", "glossary", "ar_zh_legal_terms.json"
)
WORK_JSON = os.path.join(_REPO_ROOT, "data", "metadata", "work.json")
COVERAGE_JSON = os.path.join(
    _REPO_ROOT, "data", "coverage", "book1_coverage_matrix.json"
)


def _read_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


class Corpus:
    """In-memory view over the structured corpus files."""

    def __init__(self, root: Optional[str] = None) -> None:
        base = root or _REPO_ROOT
        self.root = base
        self._articles_doc = _read_json(
            os.path.join(base, "data", "articles", "book1_articles_001_034.json")
        )
        self.articles: List[Dict[str, Any]] = self._articles_doc["articles"]
        self._by_number = {a["article_number"]: a for a in self.articles}

    # -- basic accessors ---------------------------------------------------
    @property
    def scope_ar(self) -> str:
        return self._articles_doc.get("scope_ar", "")

    @property
    def scope_zh(self) -> str:
        return self._articles_doc.get("scope_zh", "")

    def list_articles(self) -> List[Dict[str, Any]]:
        """Return all articles ordered by article number."""
        return sorted(self.articles, key=lambda a: a["article_number"])

    def get_article(self, number: int) -> Optional[Dict[str, Any]]:
        """Return the article with the given number, or ``None``."""
        return self._by_number.get(int(number))

    def search_keyword(self, term: str) -> List[Dict[str, Any]]:
        """Return articles matching ``term`` in text, titles, or keyword lists.

        The search is a simple case-insensitive substring match across the
        Arabic summary, Chinese translation, titles, English summary, and the
        Arabic/Chinese keyword lists. It is intentionally simple and dependency
        free; for production RAG use the JSONL chunks with a vector store.
        """
        if not term:
            return []
        needle = term.strip().lower()
        hits: List[Dict[str, Any]] = []
        for a in self.list_articles():
            haystack_parts = [
                a.get("article_title_ar", ""),
                a.get("article_title_zh", ""),
                a.get("arabic_reference_summary", ""),
                a.get("chinese_translation", ""),
                a.get("llm", {}).get("retrieval_title", ""),
                a.get("llm", {}).get("summary_en", ""),
            ]
            haystack_parts += a.get("llm", {}).get("keywords_ar", [])
            haystack_parts += a.get("llm", {}).get("keywords_zh", [])
            haystack = "\n".join(haystack_parts).lower()
            if needle in haystack:
                hits.append(a)
        return hits


# -- module-level convenience API (lazy singleton) -------------------------
_DEFAULT: Optional[Corpus] = None


def load_corpus(root: Optional[str] = None) -> Corpus:
    """Load (and cache) the default corpus."""
    global _DEFAULT
    if root is not None:
        return Corpus(root)
    if _DEFAULT is None:
        _DEFAULT = Corpus()
    return _DEFAULT


def list_articles() -> List[Dict[str, Any]]:
    return load_corpus().list_articles()


def get_article(number: int) -> Optional[Dict[str, Any]]:
    return load_corpus().get_article(number)


def search_keyword(term: str) -> List[Dict[str, Any]]:
    return load_corpus().search_keyword(term)
