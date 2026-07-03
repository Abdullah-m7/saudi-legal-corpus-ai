"""Arabic Legal LLM-ready layer — Books 1-3 backfill (per-article records)."""

import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "arabic_legal_llm.schema.json")
LAYER = os.path.join(ROOT, "data", "arabic_legal_llm")

BOOKS = {
    1: (os.path.join(LAYER, "book1_ar_legal_llm.json"), list(range(1, 35))),
    2: (os.path.join(LAYER, "book2_ar_legal_llm.json"), list(range(35, 51))),
    3: (os.path.join(LAYER, "book3_ar_legal_llm.json"), list(range(51, 58))),
}

TOPICS = {
    1: ["التأسيس", "الشخصية الاعتبارية", "عقد التأسيس", "النظام الأساس",
        "الشريك", "المدير", "المسؤولية"],
    2: ["شركة التضامن", "الشريك المتضامن", "المسؤولية التضامنية", "صفة التاجر"],
    3: ["شركة التوصية البسيطة", "الشريك المتضامن", "الشريك الموصي",
        "المسؤولية المحدودة", "عدم اكتساب صفة التاجر"],
}

BANNED = ("verified", "محققة", "经核验")

CANON_FILES = {
    1: os.path.join(ROOT, "data", "articles", "book1_articles_001_034.json"),
    2: os.path.join(ROOT, "data", "articles", "book2_articles_035_050.json"),
    3: os.path.join(ROOT, "data", "articles", "book3_articles_051_057.json"),
}


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _canonical_summaries(book):
    """{article_number: arabic_reference_summary} from canonical article data."""
    doc = _read(CANON_FILES[book])
    return {a["article_number"]: a["arabic_reference_summary"] for a in doc["articles"]}


# -- existence + exact coverage ---------------------------------------------
@pytest.mark.parametrize("book", [1, 2, 3])
def test_file_exists_and_exact_articles(book):
    path, expected = BOOKS[book]
    assert os.path.exists(path), path
    doc = _read(path)
    arts = [r["article_numbers"][0] for r in doc["records"]]
    assert arts == expected, (book, arts)
    assert len(doc["records"]) == len(expected)


def test_expected_counts():
    assert len(_read(BOOKS[1][0])["records"]) == 34
    assert len(_read(BOOKS[2][0])["records"]) == 16
    assert len(_read(BOOKS[3][0])["records"]) == 7


# -- per-record shape --------------------------------------------------------
@pytest.mark.parametrize("book", [1, 2, 3])
def test_record_type_and_single_article(book):
    doc = _read(BOOKS[book][0])
    for r in doc["records"]:
        assert r["record_type"] == "article", r["record_id"]
        assert len(r["article_numbers"]) == 1, r["record_id"]
        assert r["book"] == book, r["record_id"]


@pytest.mark.parametrize("book", [1, 2, 3])
def test_records_pass_schema(book):
    schema = _read(SCHEMA)
    doc = _read(BOOKS[book][0])
    try:
        import jsonschema
        v = jsonschema.Draft7Validator(schema)
        for r in doc["records"]:
            errs = [e.message for e in v.iter_errors(r)]
            assert not errs, (r["record_id"], errs)
    except ImportError:
        for r in doc["records"]:
            for key in schema["required"]:
                assert key in r, (r["record_id"], key)


@pytest.mark.parametrize("book", [1, 2, 3])
def test_arabic_fields_present(book):
    doc = _read(BOOKS[book][0])
    for r in doc["records"]:
        assert r["legal_subject_ar"].strip(), r["record_id"]
        assert r["legal_rule_summary_ar"].strip(), r["record_id"]
        assert r["keywords_ar"] and r["search_queries_ar"], r["record_id"]


# -- legal_rule_summary_ar is derived from canonical article data ------------
@pytest.mark.parametrize("book", [1, 2, 3])
def test_summary_exact_match_to_canonical(book):
    """Every record's legal_rule_summary_ar must EQUAL, exactly and by
    article_number, the canonical arabic_reference_summary. No partial match,
    no manual override — this guards against layer/canonical drift."""
    canon = _canonical_summaries(book)
    doc = _read(BOOKS[book][0])
    for r in doc["records"]:
        n = r["article_numbers"][0]
        assert n in canon, (book, n)
        assert r["legal_rule_summary_ar"] == canon[n], (book, n)


def test_summary_source_is_canonical_generator():
    """The generator must not hardcode summaries: legal_rule_summary_ar is
    read from arabic_reference_summary in canonical article JSON."""
    gen = os.path.join(ROOT, "scripts", "gen_arabic_legal_llm_books1_3.py")
    src = open(gen, encoding="utf-8").read()
    assert "arabic_reference_summary" in src
    assert "CANON[(book, n)]" in src


# -- trust posture -----------------------------------------------------------
@pytest.mark.parametrize("book", [1, 2, 3])
def test_trust_posture(book):
    doc = _read(BOOKS[book][0])
    for r in doc["records"]:
        st = r["source_trust"]
        assert st["official_text_check"] == "needs_check", r["record_id"]
        assert st["text_type"] == "internally_reviewed_summary", r["record_id"]


@pytest.mark.parametrize("book", [1, 2, 3])
def test_no_trust_overclaim(book):
    blob = open(BOOKS[book][0], encoding="utf-8").read()
    for term in BANNED:
        assert term not in blob, (book, term)


# -- key legal topics --------------------------------------------------------
@pytest.mark.parametrize("book", [1, 2, 3])
def test_key_topics_present(book):
    blob = open(BOOKS[book][0], encoding="utf-8").read()
    for topic in TOPICS[book]:
        assert topic in blob, (book, topic)


# -- existing canonical article text untouched (safety) ---------------------
@pytest.mark.parametrize("fname,book,first,last", [
    ("book1_articles_001_034.json", 1, 1, 34),
    ("book2_articles_035_050.json", 2, 35, 50),
    ("book3_articles_051_057.json", 3, 51, 57),
])
def test_canonical_article_files_intact(fname, book, first, last):
    doc = _read(os.path.join(ROOT, "data", "articles", fname))
    nums = [a["article_number"] for a in doc["articles"]]
    assert nums == list(range(first, last + 1)), (book, nums)


def test_book4_pilot_preserved():
    pilot = os.path.join(LAYER, "book4_section1_ar_legal_llm.json")
    assert os.path.exists(pilot)
    doc = _read(pilot)
    arts = sorted(r["article_numbers"][0] for r in doc["records"])
    assert arts == [58, 59, 60, 66]


def test_validator_script_passes():
    import subprocess
    import sys
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "validate_arabic_legal_llm.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
