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

from . import books

# Repository root: .../src/saudi_law_corpus/load.py -> repo root is three up.
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))

# Book One paths kept as module constants for backward compatibility.
ARTICLES_JSON = books.get_book(1).articles_json
GLOSSARY_JSON = books.GLOSSARY_JSON
WORK_JSON = books.WORK_JSON
COVERAGE_JSON = books.get_book(1).coverage_json


def _read_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


class Corpus:
    """In-memory view over the structured corpus files for a single book.

    Defaults to Book One so existing callers keep working unchanged.
    """

    def __init__(self, root: Optional[str] = None, book: int = 1) -> None:
        base = root or _REPO_ROOT
        self.root = base
        self.book = book
        spec = books.get_book(book)
        # Resolve relative to `base` so an alternate root still works.
        rel = os.path.relpath(spec.articles_json, books.REPO_ROOT)
        self._articles_doc = _read_json(os.path.join(base, rel))
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


# -- module-level convenience API (lazy per-book cache) --------------------
_CACHE: Dict[int, Corpus] = {}


def load_corpus(root: Optional[str] = None, book: int = 1) -> Corpus:
    """Load (and cache) the corpus for a book. Defaults to Book One."""
    if root is not None:
        return Corpus(root, book=book)
    if book not in _CACHE:
        _CACHE[book] = Corpus(book=book)
    return _CACHE[book]


def list_articles(book: int = 1) -> List[Dict[str, Any]]:
    return load_corpus(book=book).list_articles()


def get_article(number: int, book: int = 1) -> Optional[Dict[str, Any]]:
    return load_corpus(book=book).get_article(number)


def search_keyword(term: str, book: int = 1) -> List[Dict[str, Any]]:
    return load_corpus(book=book).search_keyword(term)
