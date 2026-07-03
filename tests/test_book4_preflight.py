"""Book Four preflight: lightweight assertions that the scope-lock docs exist and
carry the required scope statements. This is a planning gate, not a content test —
Book Four canonical data does NOT exist yet."""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFLIGHT = os.path.join(ROOT, "docs", "book4_preflight")

DOCS = [
    "README.md",
    "BOOK4_SCOPE_LOCK.md",
    "BOOK4_TERMINOLOGY_LOCK.md",
    "BOOK4_QA_PLAN.md",
    "BOOK4_IMPLEMENTATION_PLAN.md",
    "BOOK4_REVIEW_RISKS.md",
]


def _read(name):
    with open(os.path.join(PREFLIGHT, name), "r", encoding="utf-8") as fh:
        return fh.read()


def test_all_preflight_docs_exist():
    for name in DOCS:
        assert os.path.exists(os.path.join(PREFLIGHT, name)), name


def test_scope_lock_names_book_four():
    t = _read("BOOK4_SCOPE_LOCK.md")
    assert ("Book Four" in t) or ("الباب الرابع" in t)


def test_scope_lock_contains_article_range():
    t = _read("BOOK4_SCOPE_LOCK.md")
    # Article range 58–137 must be present (either dash form).
    assert ("58–137" in t) or ("58-137" in t)
    assert "58" in t and "137" in t


def test_scope_lock_states_generation_not_started():
    t = _read("BOOK4_SCOPE_LOCK.md")
    assert "NOT started" in t


def test_implementation_plan_states_generation_not_started():
    t = _read("BOOK4_IMPLEMENTATION_PLAN.md")
    assert "NOT started" in t


def test_implementation_plan_recommends_a_path():
    t = _read("BOOK4_IMPLEMENTATION_PLAN.md")
    assert "RECOMMENDED" in t or "Recommendation" in t


def test_qa_plan_has_core_rules():
    t = _read("BOOK4_QA_PLAN.md")
    for token in ("internally_reviewed_summary", "needs_check", "book == 4",
                  "第四编", "OGM", "EGM"):
        assert token in t, token


def test_no_book4_canonical_data_created():
    """Preflight must NOT create canonical Book Four data/content."""
    forbidden = [
        "data/articles/book4_articles.json",
        "content/ar/book4.md",
        "content/zh/book4.md",
        "content/bilingual/book4_bilingual.md",
    ]
    for rel in forbidden:
        assert not os.path.exists(os.path.join(ROOT, rel)), f"unexpected: {rel}"
    # No book4 article json/jsonl of any name.
    articles_dir = os.path.join(ROOT, "data", "articles")
    for f in os.listdir(articles_dir):
        assert not f.startswith("book4_"), f"unexpected canonical file: {f}"
