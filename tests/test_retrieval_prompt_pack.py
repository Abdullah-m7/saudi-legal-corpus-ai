#!/usr/bin/env python3
"""Tests for Retrieval Prompt Pack Foundation."""

import json
import os
import subprocess
import sys
import tempfile
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT_PACK_SCRIPT = os.path.join(REPO_ROOT, "scripts", "build_retrieval_prompt_pack.py")
JSONL_PATH = os.path.join(REPO_ROOT, "data", "exports", "v1", "primary_arabic_governing_records.jsonl")

# Import prompt pack builder directly
sys.path.insert(0, REPO_ROOT)
from scripts.build_retrieval_prompt_pack import (
    build_prompt_pack,
    format_markdown,
    build_prompt_text,
    PROMPT_PACK_VERSION,
    PROMPT_POLICY,
    PROMPT_MODES,
)
from scripts.search_primary_arabic_export import load_records


@pytest.fixture(scope="module")
def records():
    return load_records(JSONL_PATH)


# ─── build_prompt_pack ───

def test_pack_returns_results():
    pack = build_prompt_pack("الشركة", limit=5)
    assert pack["total_matches"] > 0
    assert pack["returned"] > 0
    assert len(pack["retrieved_records"]) > 0

def test_pack_limit():
    pack = build_prompt_pack("الشركة", limit=3)
    assert pack["returned"] <= 3
    assert pack["limit"] == 3

def test_pack_track_filter():
    pack = build_prompt_pack("التصفية", limit=20, track="companies_law")
    for r in pack["retrieved_records"]:
        assert r["source_track_id"] == "companies_law"
    assert pack["filters"]["track"] == "companies_law"

def test_pack_record_type_filter():
    pack = build_prompt_pack("الشركة", limit=20, record_type="article")
    for r in pack["retrieved_records"]:
        assert r["record_type"] == "article"
    assert pack["filters"]["record_type"] == "article"

def test_pack_no_match():
    pack = build_prompt_pack("xyznonexistent", limit=5)
    assert pack["total_matches"] == 0
    assert pack["returned"] == 0
    assert pack["retrieved_records"] == []

def test_pack_deterministic():
    p1 = build_prompt_pack("الشركة", limit=5)
    p2 = build_prompt_pack("الشركة", limit=5)
    assert p1["retrieved_records"] == p2["retrieved_records"]
    assert p1["prompt_text"] == p2["prompt_text"]

def test_pack_top_level_fields():
    pack = build_prompt_pack("مجلس الإدارة", limit=3)
    required = [
        "prompt_pack_version", "query", "normalized_query", "mode",
        "generated_at_date", "source_context_pack_tool", "source_search_tool",
        "source_export_file", "source_export_record_count", "retrieval_method",
        "limit", "filters", "total_matches", "returned", "legal_boundaries",
        "prompt_policy", "retrieved_records", "prompt_text",
    ]
    for field in required:
        assert field in pack, f"Missing field: {field}"

def test_pack_record_fields():
    pack = build_prompt_pack("مجلس الإدارة", limit=3)
    for r in pack["retrieved_records"]:
        assert "rank" in r
        assert "score" in r
        assert "export_record_id" in r
        assert "source_track_id" in r
        assert "source_record_id" in r
        assert "record_type" in r
        assert "language" in r
        assert "governing_status" in r
        assert "title_ar" in r
        assert "snippet" in r

def test_pack_no_text_ar_by_default():
    pack = build_prompt_pack("الشركة", limit=3)
    for r in pack["retrieved_records"]:
        assert "text_ar" not in r

def test_pack_include_full_text():
    pack = build_prompt_pack("الشركة", limit=3, include_full_text=True)
    for r in pack["retrieved_records"]:
        assert "text_ar" in r
        assert r["text_ar"]

def test_pack_all_records_arabic():
    pack = build_prompt_pack("الشركة", limit=10)
    for r in pack["retrieved_records"]:
        assert r["language"] == "ar"

def test_pack_no_english_records():
    pack = build_prompt_pack("company", limit=5)
    assert pack["total_matches"] == 0

def test_pack_no_chinese_records():
    pack = build_prompt_pack("公司", limit=5)
    assert pack["total_matches"] == 0

def test_pack_legal_boundaries():
    pack = build_prompt_pack("الشركة", limit=3)
    expected = [
        "Arabic official source governs",
        "Not legal advice",
        "Not official translation",
        "No legal interpretation",
        "No generated legal conclusions",
        "No English/Chinese records",
        "No trilingual alignment",
        "No public release",
    ]
    for b in expected:
        assert b in pack["legal_boundaries"]

def test_pack_prompt_policy():
    pack = build_prompt_pack("الشركة", limit=3)
    pp = pack["prompt_policy"]
    expected_keys = [
        "use_only_retrieved_records",
        "cite_every_legal_statement",
        "no_legal_advice",
        "no_official_translation",
        "no_legal_interpretation_by_tool",
        "no_generated_legal_conclusions_by_tool",
        "no_external_sources",
        "insufficient_context_rule",
        "Arabic official source governs",
        "repository-owner legal review active; external legal review optional for enterprise/official adoption",
    ]
    for k in expected_keys:
        assert k in pp, f"Missing prompt_policy key: {k}"
        assert pp[k] is True, f"prompt_policy key {k} should be True"

def test_pack_pack_version():
    pack = build_prompt_pack("الشركة", limit=3)
    assert pack["prompt_pack_version"] == PROMPT_PACK_VERSION

def test_pack_source_export_record_count():
    pack = build_prompt_pack("الشركة", limit=3)
    assert pack["source_export_record_count"] == 450

def test_pack_ranks_are_sequential():
    pack = build_prompt_pack("الشركة", limit=5)
    ranks = [r["rank"] for r in pack["retrieved_records"]]
    assert ranks == list(range(1, len(ranks) + 1))

def test_pack_scores_descending():
    pack = build_prompt_pack("الشركة", limit=10)
    scores = [r["score"] for r in pack["retrieved_records"]]
    assert scores == sorted(scores, reverse=True)

def test_pack_does_not_modify_records(records):
    import copy
    records_copy = copy.deepcopy(records)
    build_prompt_pack("الشركة", limit=5)
    assert records == records_copy

def test_pack_stable_tiebreak():
    pack = build_prompt_pack("الشركة", limit=50)
    for i in range(len(pack["retrieved_records"]) - 1):
        if pack["retrieved_records"][i]["score"] == pack["retrieved_records"][i + 1]["score"]:
            assert pack["retrieved_records"][i]["export_record_id"] < pack["retrieved_records"][i + 1]["export_record_id"]


# ─── Prompt modes ───

def test_mode_evidence_brief():
    pack = build_prompt_pack("مجلس الإدارة", limit=3, mode="evidence_brief")
    assert pack["mode"] == "evidence_brief"
    assert "موجز أدلة" in pack["prompt_text"]

def test_mode_cautious_answer_draft():
    pack = build_prompt_pack("مجلس الإدارة", limit=3, mode="cautious_answer_draft")
    assert pack["mode"] == "cautious_answer_draft"
    assert "إجابة معلوماتية حذرة" in pack["prompt_text"]

def test_mode_citation_check():
    pack = build_prompt_pack("مجلس الإدارة", limit=3, mode="citation_check")
    assert pack["mode"] == "citation_check"
    assert "تحقق" in pack["prompt_text"]

def test_mode_default_is_evidence_brief():
    pack = build_prompt_pack("الشركة", limit=3)
    assert pack["mode"] == "evidence_brief"

def test_prompt_text_has_citation_instructions():
    pack = build_prompt_pack("مجلس الإدارة", limit=3)
    assert "export_record_id" in pack["prompt_text"] or "استشهد" in pack["prompt_text"]

def test_prompt_text_has_insufficient_context_rule():
    pack = build_prompt_pack("مجلس الإدارة", limit=3)
    assert "غير كاف" in pack["prompt_text"]

def test_prompt_text_has_no_legal_advice_boundary():
    pack = build_prompt_pack("مجلس الإدارة", limit=3)
    assert "استشارة قانونية" in pack["prompt_text"]

def test_prompt_text_has_arabic_governs():
    pack = build_prompt_pack("مجلس الإدارة", limit=3)
    assert "المصدر العربي الرسمي هو الحاكم" in pack["prompt_text"]

def test_prompt_text_has_repository_owner_review_note():
    pack = build_prompt_pack("مجلس الإدارة", limit=3)
    assert "مالك المستودع" in pack["prompt_text"]

def test_prompt_text_contains_record_ids():
    pack = build_prompt_pack("مجلس الإدارة", limit=3)
    for r in pack["retrieved_records"]:
        assert r["export_record_id"] in pack["prompt_text"]


# ─── format_markdown ───

def test_markdown_has_heading():
    pack = build_prompt_pack("مجلس الإدارة", limit=3)
    md = format_markdown(pack)
    assert "حزمة تعليمات استرجاع" in md

def test_markdown_has_boundaries():
    pack = build_prompt_pack("مجلس الإدارة", limit=3)
    md = format_markdown(pack)
    assert "الحدود القانونية" in md

def test_markdown_has_records_section():
    pack = build_prompt_pack("مجلس الإدارة", limit=3)
    md = format_markdown(pack)
    assert "السجلات المسترجعة" in md

def test_markdown_has_prompt_text_section():
    pack = build_prompt_pack("مجلس الإدارة", limit=3)
    md = format_markdown(pack)
    assert "نص التعليمات" in md

def test_markdown_has_not_a_prompt_note():
    pack = build_prompt_pack("مجلس الإدارة", limit=3)
    md = format_markdown(pack)
    assert "حزمة تعليمات فقط" in md

def test_markdown_has_prompt_policy():
    pack = build_prompt_pack("مجلس الإدارة", limit=3)
    md = format_markdown(pack)
    assert "سياسة التعليمات" in md

def test_markdown_has_record_titles():
    pack = build_prompt_pack("مجلس الإدارة", limit=3)
    md = format_markdown(pack)
    for r in pack["retrieved_records"]:
        title = r.get("title_ar") or "(بدون عنوان)"
        assert title in md

def test_markdown_has_snippets():
    pack = build_prompt_pack("مجلس الإدارة", limit=3)
    md = format_markdown(pack)
    assert "مقتطف" in md

def test_markdown_no_full_text_by_default():
    pack = build_prompt_pack("الشركة", limit=2)
    md = format_markdown(pack)
    assert "النص الكامل" not in md

def test_markdown_full_text_when_requested():
    pack = build_prompt_pack("الشركة", limit=2, include_full_text=True)
    md = format_markdown(pack, include_full_text=True)
    assert "النص الكامل" in md

def test_markdown_has_mode():
    pack = build_prompt_pack("مجلس الإدارة", limit=3, mode="cautious_answer_draft")
    md = format_markdown(pack)
    assert "cautious_answer_draft" in md


# ─── CLI ───

def _run_cli(args):
    cmd = [sys.executable, PROMPT_PACK_SCRIPT] + args
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT, timeout=30)
    return r.returncode, r.stdout, r.stderr

def test_cli_help():
    rc, stdout, _ = _run_cli(["--help"])
    assert rc == 0
    assert "usage" in stdout.lower()

def test_cli_json_output():
    rc, stdout, _ = _run_cli(["مجلس الإدارة", "--limit", "3", "--format", "json"])
    assert rc == 0
    data = json.loads(stdout)
    assert "prompt_pack_version" in data
    assert "prompt_text" in data
    assert "prompt_policy" in data
    assert "retrieved_records" in data
    assert data["returned"] <= 3

def test_cli_markdown_output():
    rc, stdout, _ = _run_cli(["مجلس الإدارة", "--limit", "3", "--format", "markdown"])
    assert rc == 0
    assert "حزمة تعليمات استرجاع" in stdout

def test_cli_default_format_json():
    rc, stdout, _ = _run_cli(["مجلس الإدارة", "--limit", "2"])
    assert rc == 0
    data = json.loads(stdout)
    assert "prompt_pack_version" in data

def test_cli_default_mode_evidence_brief():
    rc, stdout, _ = _run_cli(["مجلس الإدارة", "--limit", "2", "--format", "json"])
    assert rc == 0
    data = json.loads(stdout)
    assert data["mode"] == "evidence_brief"

def test_cli_mode_evidence_brief():
    rc, stdout, _ = _run_cli(["مجلس الإدارة", "--limit", "3", "--mode", "evidence_brief", "--format", "json"])
    assert rc == 0
    data = json.loads(stdout)
    assert data["mode"] == "evidence_brief"

def test_cli_mode_cautious_answer_draft():
    rc, stdout, _ = _run_cli(["مجلس الإدارة", "--limit", "3", "--mode", "cautious_answer_draft", "--format", "json"])
    assert rc == 0
    data = json.loads(stdout)
    assert data["mode"] == "cautious_answer_draft"

def test_cli_mode_citation_check():
    rc, stdout, _ = _run_cli(["مجلس الإدارة", "--limit", "3", "--mode", "citation_check", "--format", "json"])
    assert rc == 0
    data = json.loads(stdout)
    assert data["mode"] == "citation_check"

def test_cli_limit():
    rc, stdout, _ = _run_cli(["الشركة", "--limit", "2", "--format", "json"])
    assert rc == 0
    data = json.loads(stdout)
    assert data["returned"] <= 2

def test_cli_track_filter():
    rc, stdout, _ = _run_cli(["التصفية", "--track", "companies_law", "--limit", "5", "--format", "json"])
    assert rc == 0
    data = json.loads(stdout)
    for r in data["retrieved_records"]:
        assert r["source_track_id"] == "companies_law"

def test_cli_record_type_filter():
    rc, stdout, _ = _run_cli(["الشركة", "--record-type", "article", "--limit", "5", "--format", "json"])
    assert rc == 0
    data = json.loads(stdout)
    for r in data["retrieved_records"]:
        assert r["record_type"] == "article"

def test_cli_include_full_text():
    rc, stdout, _ = _run_cli(["مجلس الإدارة", "--limit", "2", "--format", "json", "--include-full-text"])
    assert rc == 0
    data = json.loads(stdout)
    for r in data["retrieved_records"]:
        assert "text_ar" in r
        assert r["text_ar"]

def test_cli_no_full_text_by_default():
    rc, stdout, _ = _run_cli(["مجلس الإدارة", "--limit", "3", "--format", "json"])
    assert rc == 0
    data = json.loads(stdout)
    for r in data["retrieved_records"]:
        assert "text_ar" not in r

def test_cli_deterministic():
    rc1, stdout1, _ = _run_cli(["الشركة", "--limit", "5", "--format", "json"])
    rc2, stdout2, _ = _run_cli(["الشركة", "--limit", "5", "--format", "json"])
    assert stdout1 == stdout2

def test_cli_no_english_results():
    rc, stdout, _ = _run_cli(["company", "--limit", "5", "--format", "json"])
    assert rc == 0
    data = json.loads(stdout)
    assert data["total_matches"] == 0

def test_cli_no_chinese_results():
    rc, stdout, _ = _run_cli(["公司", "--limit", "5", "--format", "json"])
    assert rc == 0
    data = json.loads(stdout)
    assert data["total_matches"] == 0

def test_cli_output_to_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, dir=tempfile.gettempdir()) as tmp:
        tmp_path = tmp.name
    try:
        rc, stdout, stderr = _run_cli(["مجلس الإدارة", "--limit", "2", "--format", "json", "--output", tmp_path])
        assert rc == 0
        assert os.path.isfile(tmp_path)
        with open(tmp_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "prompt_pack_version" in data
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def test_cli_legal_boundaries():
    rc, stdout, _ = _run_cli(["الشركة", "--limit", "3", "--format", "json"])
    assert rc == 0
    data = json.loads(stdout)
    assert "legal_boundaries" in data
    assert "Arabic official source governs" in data["legal_boundaries"]
    assert "Not legal advice" in data["legal_boundaries"]

def test_cli_prompt_policy():
    rc, stdout, _ = _run_cli(["الشركة", "--limit", "3", "--format", "json"])
    assert rc == 0
    data = json.loads(stdout)
    assert "prompt_policy" in data
    assert data["prompt_policy"]["use_only_retrieved_records"] is True
    assert data["prompt_policy"]["no_legal_advice"] is True

def test_cli_prompt_text_present():
    rc, stdout, _ = _run_cli(["الشركة", "--limit", "3", "--format", "json"])
    assert rc == 0
    data = json.loads(stdout)
    assert "prompt_text" in data
    assert len(data["prompt_text"]) > 0

def test_cli_all_records_arabic():
    rc, stdout, _ = _run_cli(["الشركة", "--limit", "10", "--format", "json"])
    assert rc == 0
    data = json.loads(stdout)
    for r in data["retrieved_records"]:
        assert r["language"] == "ar"

def test_cli_does_not_modify_repo_files():
    source_files = [
        JSONL_PATH,
        os.path.join(REPO_ROOT, "scripts/search_primary_arabic_export.py"),
        os.path.join(REPO_ROOT, "scripts/build_retrieval_context_pack.py"),
        os.path.join(REPO_ROOT, "scripts/build_retrieval_prompt_pack.py"),
    ]
    mtimes_before = {f: os.path.getmtime(f) for f in source_files if os.path.exists(f)}
    _run_cli(["الشركة", "--limit", "3", "--format", "json"])
    mtimes_after = {f: os.path.getmtime(f) for f in source_files if os.path.exists(f)}
    for f in mtimes_before:
        assert mtimes_before[f] == mtimes_after[f], f"File modified: {f}"

def test_cli_markdown_has_boundaries():
    rc, stdout, _ = _run_cli(["مجلس الإدارة", "--limit", "3", "--format", "markdown"])
    assert rc == 0
    assert "الحدود القانونية" in stdout

def test_cli_markdown_has_prompt_policy():
    rc, stdout, _ = _run_cli(["مجلس الإدارة", "--limit", "3", "--format", "markdown"])
    assert rc == 0
    assert "سياسة التعليمات" in stdout