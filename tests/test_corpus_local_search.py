#!/usr/bin/env python3
"""Tests for Local Lexical Search Foundation."""

import json
import os
import subprocess
import sys
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEARCH_SCRIPT = os.path.join(REPO_ROOT, "scripts", "search_primary_arabic_export.py")
JSONL_PATH = os.path.join(REPO_ROOT, "data", "exports", "v1", "primary_arabic_governing_records.jsonl")

# Import search module directly
sys.path.insert(0, REPO_ROOT)
from scripts.search_primary_arabic_export import (
    normalize_arabic, load_records, search, score_record, make_snippet
)


@pytest.fixture(scope="module")
def records():
    return load_records(JSONL_PATH)


# ─── normalize_arabic ───

def test_normalize_removes_tatweel():
    assert normalize_arabic("الـــشركة") == normalize_arabic("الشركة")

def test_normalize_alef_forms():
    assert normalize_arabic("أحمد") == normalize_arabic("احمد")
    assert normalize_arabic("إبراهيم") == normalize_arabic("ابراهيم")
    assert normalize_arabic("آدم") == normalize_arabic("ادم")

def test_normalize_ya():
    assert normalize_arabic("على") == normalize_arabic("علي")

def test_normalize_ta_marbuta():
    assert normalize_arabic("شركة") == normalize_arabic("شركه")

def test_normalize_removes_diacritics():
    assert normalize_arabic("الشَّرِكَة") == normalize_arabic("الشركة")

def test_normalize_empty():
    assert normalize_arabic("") == ""

def test_normalize_preserves_non_arabic():
    assert normalize_arabic("hello") == "hello"


# ─── load_records ───

def test_load_records_450(records):
    assert len(records) == 450

def test_all_records_arabic(records):
    for r in records:
        assert r["language"] == "ar"


# ─── search ───

def test_search_returns_results(records):
    results = search(records, "الشركة", limit=5)
    assert len(results) > 0

def test_search_limit(records):
    results = search(records, "الشركة", limit=3)
    assert len(results) <= 3

def test_search_track_filter(records):
    results = search(records, "الشركة", limit=100, track="companies_law")
    for r in results:
        assert r["source_track_id"] == "companies_law"

def test_search_record_type_filter(records):
    results = search(records, "الشركة", limit=100, record_type="article")
    for r in results:
        assert r["record_type"] == "article"

def test_search_no_match(records):
    results = search(records, "xyznonexistent", limit=10)
    assert len(results) == 0

def test_search_deterministic(records):
    r1 = search(records, "الشركة", limit=10)
    r2 = search(records, "الشركة", limit=10)
    assert r1 == r2

def test_search_stable_tiebreak(records):
    """Results with same score should be sorted by export_record_id."""
    results = search(records, "الشركة", limit=50)
    for i in range(len(results) - 1):
        if results[i]["score"] == results[i + 1]["score"]:
            assert results[i]["export_record_id"] < results[i + 1]["export_record_id"]

def test_search_phrase_match_higher_score(records):
    """Exact phrase match should score higher than single term."""
    phrase_results = search(records, "الجمعية العامة", limit=10)
    single_results = search(records, "الجمعية", limit=10)
    if phrase_results and single_results:
        # Phrase match top score should be >= single term top score
        assert phrase_results[0]["score"] >= single_results[0]["score"]

def test_search_results_have_required_fields(records):
    results = search(records, "الشركة", limit=3)
    for r in results:
        assert "score" in r
        assert "export_record_id" in r
        assert "source_track_id" in r
        assert "snippet" in r
        assert "title_ar" in r

def test_search_snippets_non_empty(records):
    results = search(records, "الشركة", limit=3)
    for r in results:
        assert r["snippet"], f"Empty snippet for {r['export_record_id']}"

def test_search_does_not_modify_records(records):
    import copy
    records_copy = copy.deepcopy(records)
    search(records, "الشركة", limit=5)
    assert records == records_copy


# ─── CLI ───

def _run_cli(args):
    cmd = [sys.executable, SEARCH_SCRIPT] + args
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT, timeout=30)
    return r.returncode, r.stdout, r.stderr

def test_cli_help():
    rc, stdout, _ = _run_cli(["--help"])
    assert rc == 0
    assert "usage" in stdout.lower()

def test_cli_basic_query():
    rc, stdout, _ = _run_cli(["الشركة", "--limit", "3"])
    assert rc == 0
    assert "Total matches:" in stdout

def test_cli_json_output():
    rc, stdout, _ = _run_cli(["الشركة", "--limit", "3", "--json"])
    assert rc == 0
    data = json.loads(stdout)
    assert "query" in data
    assert "total_matches" in data
    assert "returned" in data
    assert "results" in data

def test_cli_track_filter():
    rc, stdout, _ = _run_cli(["الشركة", "--limit", "5", "--track", "companies_law"])
    assert rc == 0
    assert "implementing_regulations" not in stdout.split("Track:")[1].split("\n")[0] if "Track:" in stdout else True

def test_cli_no_english_results():
    rc, stdout, _ = _run_cli(["company", "--limit", "5"])
    assert rc == 0
    assert "Total matches: 0" in stdout or "No matches" in stdout

def test_cli_no_chinese_results():
    rc, stdout, _ = _run_cli(["公司", "--limit", "5"])
    assert rc == 0
    assert "Total matches: 0" in stdout or "No matches" in stdout

def test_cli_show_text():
    rc, stdout, _ = _run_cli(["الشركة", "--limit", "2", "--show-text"])
    assert rc == 0
    assert "Full text:" in stdout

def test_cli_deterministic():
    rc1, stdout1, _ = _run_cli(["الشركة", "--limit", "5", "--json"])
    rc2, stdout2, _ = _run_cli(["الشركة", "--limit", "5", "--json"])
    assert stdout1 == stdout2

def test_cli_record_type_filter():
    rc, stdout, _ = _run_cli(["الشركة", "--limit", "10", "--record-type", "article"])
    assert rc == 0
    lines = stdout.split("\n")
    type_lines = [l for l in lines if l.strip().startswith("Type:")]
    for l in type_lines:
        assert "article" in l.lower()