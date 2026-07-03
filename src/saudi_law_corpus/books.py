"""Multi-book registry for the corpus.

Centralizes per-book file locations and display metadata so the shared loader,
validators and renderers can serve any book without hardcoding Book One's paths
or article range. Book One remains the default everywhere for backward
compatibility.
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))

DATA = os.path.join(REPO_ROOT, "data")
CONTENT = os.path.join(REPO_ROOT, "content")
DIST = os.path.join(REPO_ROOT, "dist")


class BookSpec:
    """Resolved locations + display metadata for a single book."""

    def __init__(
        self,
        book: int,
        slug: str,
        articles_json: str,
        articles_jsonl: str,
        coverage_json: str,
        first_article: int,
        last_article: int,
        input_pdf: str,
        display_title_ar: str,
        display_title_zh: str,
        md_ar: str,
        md_zh: str,
        md_bilingual: str,
        translator_notes: Optional[str],
        review_log: Optional[str],
        html_out: str,
        pdf_out: str,
        expanded_articles: Optional[List[int]] = None,
    ) -> None:
        self.book = book
        self.slug = slug
        self.articles_json = articles_json
        self.articles_jsonl = articles_jsonl
        self.coverage_json = coverage_json
        self.first_article = first_article
        self.last_article = last_article
        self.input_pdf = input_pdf
        self.display_title_ar = display_title_ar
        self.display_title_zh = display_title_zh
        self.md_ar = md_ar
        self.md_zh = md_zh
        self.md_bilingual = md_bilingual
        self.translator_notes = translator_notes
        self.review_log = review_log
        self.html_out = html_out
        self.pdf_out = pdf_out
        self.expanded_articles = set(expanded_articles or [])

    @property
    def expected_range(self) -> List[int]:
        return list(range(self.first_article, self.last_article + 1))


_REGISTRY: Dict[int, BookSpec] = {
    1: BookSpec(
        book=1,
        slug="book1",
        articles_json=os.path.join(DATA, "articles", "book1_articles_001_034.json"),
        articles_jsonl=os.path.join(DATA, "articles", "book1_articles_001_034.jsonl"),
        coverage_json=os.path.join(DATA, "coverage", "book1_coverage_matrix.json"),
        first_article=1,
        last_article=34,
        input_pdf="inputs/bab1_source.pdf",
        display_title_ar="نظام الشركات السعودي — ترجمة مرجعية عربية–صينية (الباب الأول)",
        display_title_zh="沙特《公司法》阿拉伯语–中文参考译本（第一编）",
        md_ar=os.path.join(CONTENT, "ar", "book1.md"),
        md_zh=os.path.join(CONTENT, "zh", "book1.md"),
        md_bilingual=os.path.join(CONTENT, "bilingual", "book1_bilingual.md"),
        translator_notes=os.path.join(CONTENT, "notes", "translator_notes.md"),
        review_log=os.path.join(CONTENT, "notes", "review_log.md"),
        html_out=os.path.join(DIST, "book1.html"),
        pdf_out=os.path.join(DIST, "book1.pdf"),
        expanded_articles=[5, 6, 8, 9, 12, 13, 14, 17, 19, 20, 29],
    ),
    2: BookSpec(
        book=2,
        slug="book2",
        articles_json=os.path.join(DATA, "articles", "book2_articles_035_050.json"),
        articles_jsonl=os.path.join(DATA, "articles", "book2_articles_035_050.jsonl"),
        coverage_json=os.path.join(DATA, "coverage", "book2_coverage_matrix.json"),
        first_article=35,
        last_article=50,
        input_pdf="inputs/bab2_source.pdf",
        display_title_ar="نظام الشركات السعودي — ترجمة مرجعية عربية–صينية (الباب الثاني: شركة التضامن)",
        display_title_zh="沙特《公司法》阿拉伯语–中文参考译本（第二编：无限公司）",
        md_ar=os.path.join(CONTENT, "ar", "book2.md"),
        md_zh=os.path.join(CONTENT, "zh", "book2.md"),
        md_bilingual=os.path.join(CONTENT, "bilingual", "book2_bilingual.md"),
        translator_notes=os.path.join(CONTENT, "notes", "book2_translator_notes.md"),
        review_log=os.path.join(CONTENT, "notes", "book2_review_log.md"),
        html_out=os.path.join(DIST, "book2.html"),
        pdf_out=os.path.join(DIST, "book2.pdf"),
        expanded_articles=[],
    ),
    3: BookSpec(
        book=3,
        slug="book3",
        articles_json=os.path.join(DATA, "articles", "book3_articles_051_057.json"),
        articles_jsonl=os.path.join(DATA, "articles", "book3_articles_051_057.jsonl"),
        coverage_json=os.path.join(DATA, "coverage", "book3_coverage_matrix.json"),
        first_article=51,
        last_article=57,
        input_pdf="inputs/bab3_source.pdf",
        display_title_ar="نظام الشركات السعودي — ترجمة مرجعية عربية–صينية (الباب الثالث: شركة التوصية البسيطة)",
        display_title_zh="沙特《公司法》阿拉伯语–中文参考译本（第三编：两合公司）",
        md_ar=os.path.join(CONTENT, "ar", "book3.md"),
        md_zh=os.path.join(CONTENT, "zh", "book3.md"),
        md_bilingual=os.path.join(CONTENT, "bilingual", "book3_bilingual.md"),
        translator_notes=os.path.join(CONTENT, "notes", "book3_translator_notes.md"),
        review_log=os.path.join(CONTENT, "notes", "book3_review_log.md"),
        html_out=os.path.join(DIST, "book3.html"),
        pdf_out=os.path.join(DIST, "book3.pdf"),
        expanded_articles=[],
    ),
}

# Shared metadata (trust posture, instrument, disclaimers) applies to all books.
WORK_JSON = os.path.join(DATA, "metadata", "work.json")
GLOSSARY_JSON = os.path.join(DATA, "glossary", "ar_zh_legal_terms.json")


def get_book(book: int = 1) -> BookSpec:
    if book not in _REGISTRY:
        raise KeyError(f"unknown book: {book} (known: {sorted(_REGISTRY)})")
    return _REGISTRY[book]


def all_books() -> List[int]:
    return sorted(_REGISTRY)
