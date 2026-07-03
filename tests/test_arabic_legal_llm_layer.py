"""Arabic Legal LLM-ready layer — pilot (Book Four Section 1: articles 58,59,60,66)."""

import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "arabic_legal_llm.schema.json")
PILOT = os.path.join(ROOT, "data", "arabic_legal_llm", "book4_section1_ar_legal_llm.json")

ALLOWED = {58, 59, 60, 66}
UNCOVERED = {61, 62, 63, 64, 65}
ARABIC_LIST_FIELDS = [
    "actors_ar", "rights_ar", "obligations_ar", "prohibitions_ar", "conditions_ar",
    "exceptions_ar", "legal_effects_ar", "liability_ar", "deadlines_ar",
    "competent_authorities_ar", "cross_references_ar", "keywords_ar", "search_queries_ar",
]


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def doc():
    return _read(PILOT)


@pytest.fixture(scope="module")
def records(doc):
    return doc["records"]


@pytest.fixture(scope="module")
def by_article(records):
    return {r["article_numbers"][0]: r for r in records}


def _blob(r):
    parts = [r["legal_subject_ar"], r["legal_rule_summary_ar"]]
    for f in ARABIC_LIST_FIELDS:
        parts += r.get(f, [])
    for t in r.get("monetary_thresholds", []):
        parts.append(t.get("description_ar", ""))
    return " ".join(parts)


# -- existence --------------------------------------------------------------
def test_schema_exists():
    assert os.path.exists(SCHEMA)
    schema = _read(SCHEMA)
    assert "record_type" in schema["properties"]
    assert schema["properties"]["record_type"]["enum"] == ["article", "provision"]


def test_pilot_file_exists():
    assert os.path.exists(PILOT)


# -- scope guardrails -------------------------------------------------------
def test_records_only_map_to_allowed(records):
    for r in records:
        assert set(r["article_numbers"]) <= ALLOWED, r["record_id"]


def test_no_records_for_uncovered(by_article):
    assert not (set(by_article) & UNCOVERED)
    assert set(by_article) == ALLOWED


# -- schema validity + Arabic fields ---------------------------------------
def test_records_pass_schema(records):
    schema = _read(SCHEMA)
    try:
        import jsonschema
        v = jsonschema.Draft7Validator(schema)
        for r in records:
            errs = [e.message for e in v.iter_errors(r)]
            assert not errs, (r["record_id"], errs)
    except ImportError:
        for r in records:
            for key in schema["required"]:
                assert key in r, (r["record_id"], key)


def test_arabic_fields_present(records):
    for r in records:
        assert r["legal_subject_ar"].strip()
        assert r["legal_rule_summary_ar"].strip()
        # at least some structured Arabic understanding beyond the summary
        assert r["keywords_ar"] and r["search_queries_ar"]


# -- specific legal content -------------------------------------------------
def test_article59_minimum_capital_threshold(by_article):
    r = by_article[59]
    amounts = [(t["amount"], t["currency"]) for t in r["monetary_thresholds"]]
    assert (500000, "SAR") in amounts
    assert "500,000" in _blob(r) or "500000" in _blob(r)


def test_article60_issued_vs_authorized_distinguished(by_article):
    blob = _blob(by_article[60])
    assert "رأس المال المصدر" in blob
    assert "رأس المال المصرح به" in blob


def test_article66_in_kind_valuation(by_article):
    blob = _blob(by_article[66])
    assert "الحصص العينية" in blob
    assert "تقييم" in blob
    assert "مقيّم معتمد" in blob


# -- trust posture ----------------------------------------------------------
def test_official_text_check_needs_check(records):
    for r in records:
        assert r["source_trust"]["official_text_check"] == "needs_check"
        assert r["source_trust"]["text_type"] in (
            "internally_reviewed_summary", "internally_reviewed_provision")


def test_no_trust_overclaim():
    blob = open(PILOT, encoding="utf-8").read()
    for term in ("verified_summary", "verified", "محققة", "经核验"):
        assert term not in blob, term


# -- existing canonical text untouched (safety) -----------------------------
def test_existing_book4_provisions_unchanged_by_layer():
    # The layer must not have created/altered provision or article datasets.
    prov = _read(os.path.join(ROOT, "data", "articles", "book4_provisions_058_066.json"))
    assert [p["source_article_numbers"] for p in prov["provisions"]] == [[58], [59], [60], [66]]
    articles_dir = os.path.join(ROOT, "data", "articles")
    for f in os.listdir(articles_dir):
        assert not f.startswith("book4_articles_")


def test_validator_script_passes():
    import subprocess
    import sys
    r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "validate_arabic_legal_llm.py")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
