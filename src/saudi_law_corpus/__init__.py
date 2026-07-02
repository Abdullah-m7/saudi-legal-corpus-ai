"""Saudi Companies Law — Arabic–Chinese reference corpus (Book One, Articles 1–34).

Structured-first corpus package. The canonical source of truth is the JSON under
``data/articles``; everything else (JSONL, HTML, PDF) is generated from it.

This package is intentionally dependency-light. ``load`` and ``qa_rules`` use only
the Python standard library. ``validate`` optionally uses ``jsonschema`` and
``render_html`` optionally uses ``jinja2``; both degrade gracefully when the
optional dependency is missing.
"""

from .load import (
    Corpus,
    load_corpus,
    list_articles,
    get_article,
    search_keyword,
)

__all__ = [
    "Corpus",
    "load_corpus",
    "list_articles",
    "get_article",
    "search_keyword",
]

__version__ = "1.0.0"
