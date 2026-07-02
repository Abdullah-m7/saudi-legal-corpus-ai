import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import pytest  # noqa: E402


def _read(path):
    with open(os.path.join(ROOT, path), "r", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="session")
def repo_root():
    return ROOT


@pytest.fixture(scope="session")
def articles_doc():
    return _read("data/articles/book1_articles_001_034.json")


@pytest.fixture(scope="session")
def articles(articles_doc):
    return sorted(articles_doc["articles"], key=lambda a: a["article_number"])


@pytest.fixture(scope="session")
def by_number(articles):
    return {a["article_number"]: a for a in articles}


@pytest.fixture(scope="session")
def work():
    return _read("data/metadata/work.json")


@pytest.fixture(scope="session")
def glossary():
    return _read("data/glossary/ar_zh_legal_terms.json")


@pytest.fixture(scope="session")
def coverage():
    return _read("data/coverage/book1_coverage_matrix.json")
