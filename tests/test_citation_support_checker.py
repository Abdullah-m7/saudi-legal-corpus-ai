#!/usr/bin/env python3
"""Tests for Citation Support Checker Foundation."""

import json
import os
import subprocess
import sys
import tempfile
import shutil
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKER_SCRIPT = os.path.join(REPO_ROOT, "scripts", "check_citation_support.py")
PROMPT_PACK_SCRIPT = os.path.join(REPO_ROOT, "scripts", "build_retrieval_prompt_pack.py")
CONTEXT_PACK_SCRIPT = os.path.join(REPO_ROOT, "scripts", "build_retrieval_context_pack.py")
JSONL_PATH = os.path.join(REPO_ROOT, "data", "exports", "v1", "primary_arabic_governing_records.jsonl")

# Import checker functions directly
sys.path.insert(0, REPO_ROOT)
from scripts.check_citation_support import (
    run_check,
    format_markdown,
    load_pack,
    extract_retrieved_records,
    detect_pack_type,
    build_allowed_citations,
    extract_citations,
    split_paragraphs,
    is_substantive_paragraph,
    check_boundary_note,
    CHECKER_VERSION,
    LIMITATIONS,
    LEGAL_BOUNDARIES,
    CITATION_SYNTAX,
)


@pytest.fixture
def tmpdir():
    d = tempfile.mkdtemp(prefix="citation_test_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def prompt_pack_path(tmpdir):
    """Build a temporary prompt pack for testing."""
    path = os.path.join(tmpdir, "prompt_pack.json")
    subprocess.run(
        [sys.executable, PROMPT_PACK_SCRIPT,
         "مجلس الإدارة", "--limit", "3", "--mode", "cautious_answer_draft",
         "--format", "json", "--output", path],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=30
    )
    return path


@pytest.fixture
def context_pack_path(tmpdir):
    """Build a temporary context pack for testing."""
    path = os.path.join(tmpdir, "context_pack.json")
    subprocess.run(
        [sys.executable, CONTEXT_PACK_SCRIPT,
         "مجلس الإدارة", "--limit", "3",
         "--format", "json", "--output", path],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=30
    )
    return path


@pytest.fixture
def real_export_id(prompt_pack_path):
    """Get a real export_record_id from the prompt pack."""
    with open(prompt_pack_path, "r", encoding="utf-8") as f:
        pack = json.loads(f.read())
    records = pack.get("retrieved_records", [])
    return records[0]["export_record_id"] if records else None


@pytest.fixture
def real_source_id(prompt_pack_path):
    """Get a real source_record_id from the prompt pack."""
    with open(prompt_pack_path, "r", encoding="utf-8") as f:
        pack = json.loads(f.read())
    records = pack.get("retrieved_records", [])
    return records[0]["source_record_id"] if records else None


def _write_draft(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ─── extract_citations ───

def test_extract_citations_export_id():
    text = "Some text [[export_record_id=export-cl-art-001]] more text"
    cites = extract_citations(text)
    assert len(cites) == 1
    assert cites[0]["citation_type"] == "export_record_id"
    assert cites[0]["cited_id"] == "export-cl-art-001"

def test_extract_citations_source_id():
    text = "Some text [[source_record_id=cl-art-001]] more text"
    cites = extract_citations(text)
    assert len(cites) == 1
    assert cites[0]["citation_type"] == "source_record_id"
    assert cites[0]["cited_id"] == "cl-art-001"

def test_extract_citations_multiple():
    text = "[[export_record_id=id1]] and [[source_record_id=id2]]"
    cites = extract_citations(text)
    assert len(cites) == 2

def test_extract_citations_none():
    text = "No citations here"
    cites = extract_citations(text)
    assert len(cites) == 0

def test_extract_citations_with_spaces():
    text = "[[export_record_id= id-with-spaces ]]"
    cites = extract_citations(text)
    assert len(cites) == 1
    assert cites[0]["cited_id"] == "id-with-spaces"


# ─── split_paragraphs ───

def test_split_paragraphs_basic():
    text = "Para 1\n\nPara 2\n\nPara 3"
    paras = split_paragraphs(text)
    assert len(paras) == 3

def test_split_paragraphs_empty():
    text = ""
    paras = split_paragraphs(text)
    assert len(paras) == 0

def test_split_paragraphs_skips_empty_blocks():
    text = "Para 1\n\n\n\nPara 2"
    paras = split_paragraphs(text)
    assert len(paras) == 2


# ─── is_substantive_paragraph ───

def test_substantive_paragraph():
    assert is_substantive_paragraph("This is a long enough paragraph with substance.")
    assert not is_substantive_paragraph("Short")
    assert not is_substantive_paragraph("")
    assert not is_substantive_paragraph("# Heading")
    assert not is_substantive_paragraph("[[export_record_id=test]]")


# ─── check_boundary_note ───

def test_boundary_note_arabic():
    assert check_boundary_note("هذه ليست استشارة قانونية")
    assert check_boundary_note("للمراجعة القانونية")

def test_boundary_note_english():
    assert check_boundary_note("This is not legal advice")
    assert check_boundary_note("For legal review")

def test_boundary_note_absent():
    assert not check_boundary_note("This is a normal text without boundary note")


# ─── detect_pack_type ───

def test_detect_prompt_pack():
    assert detect_pack_type({"prompt_pack_version": "1.0"}) == "prompt_pack"

def test_detect_context_pack():
    assert detect_pack_type({"pack_version": "1.0"}) == "context_pack"

def test_detect_unknown():
    assert detect_pack_type({"foo": "bar"}) == "unknown"


# ─── build_allowed_citations ───

def test_build_allowed_citations():
    records = [
        {"export_record_id": "eid1", "source_record_id": "sid1"},
        {"export_record_id": "eid2", "source_record_id": "sid2"},
    ]
    allowed = build_allowed_citations(records)
    assert "eid1" in allowed["export_record_id"]
    assert "eid2" in allowed["export_record_id"]
    assert "sid1" in allowed["source_record_id"]
    assert "sid2" in allowed["source_record_id"]


# ─── run_check ───

def test_run_check_valid_citation(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, f"هذه إجابة معلوماتية وليست استشارة قانونية.\n\nوفقًا للنظام [[export_record_id={real_export_id}]].\n")
    pack = load_pack(prompt_pack_path)
    result = run_check(pack, prompt_pack_path, "prompt_pack",
                       open(draft_path, "r", encoding="utf-8").read(), draft_path)
    assert result["result"] == "PASS"
    assert result["valid_citations"] >= 1
    assert result["invalid_citations"] == 0

def test_run_check_invalid_citation(prompt_pack_path, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, "هذه إجابة.\n\n[[export_record_id=FAKE-NOT-IN-PACK]].\n")
    pack = load_pack(prompt_pack_path)
    result = run_check(pack, prompt_pack_path, "prompt_pack",
                       open(draft_path, "r", encoding="utf-8").read(), draft_path)
    assert result["result"] == "FAIL"
    assert result["invalid_citations"] >= 1

def test_run_check_no_citations(prompt_pack_path, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, "هذه إجابة معلوماتية وليست استشارة قانونية.\n\nوفقًا للنظام، تتولى الجمعية العامة اختيار أعضاء مجلس الإدارة.\n")
    pack = load_pack(prompt_pack_path)
    result = run_check(pack, prompt_pack_path, "prompt_pack",
                       open(draft_path, "r", encoding="utf-8").read(), draft_path)
    assert result["result"] == "FAIL"
    assert result["citations_found"] == 0

def test_run_check_require_citation_per_paragraph_pass(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path,
                 f"هذه إجابة معلوماتية وليست استشارة قانونية للمراجعة القانونية [[export_record_id={real_export_id}]].\n\n"
                 f"وفقًا للنظام [[export_record_id={real_export_id}]].\n\n"
                 f"كما تتولى المراقبة [[export_record_id={real_export_id}]].\n")
    pack = load_pack(prompt_pack_path)
    result = run_check(pack, prompt_pack_path, "prompt_pack",
                       open(draft_path, "r", encoding="utf-8").read(), draft_path,
                       require_citation_per_paragraph=True)
    assert result["result"] == "PASS"

def test_run_check_require_citation_per_paragraph_fail(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path,
                 f"هذه إجابة معلوماتية وليست استشارة قانونية للمراجعة القانونية.\n\n"
                 f"وفقًا للنظام [[export_record_id={real_export_id}]].\n\n"
                 f"كما تتولى المراقبة على أعمال الشركة دون استشهاد هنا.\n")
    pack = load_pack(prompt_pack_path)
    result = run_check(pack, prompt_pack_path, "prompt_pack",
                       open(draft_path, "r", encoding="utf-8").read(), draft_path,
                       require_citation_per_paragraph=True)
    assert result["result"] == "FAIL"
    assert len(result["uncited_paragraphs"]) > 0

def test_run_check_require_boundary_note_pass(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path,
                 f"هذه إجابة معلوماتية وليست استشارة قانونية.\n\n"
                 f"وفقًا للنظام [[export_record_id={real_export_id}]].\n")
    pack = load_pack(prompt_pack_path)
    result = run_check(pack, prompt_pack_path, "prompt_pack",
                       open(draft_path, "r", encoding="utf-8").read(), draft_path,
                       require_boundary_note=True)
    assert result["result"] == "PASS"
    assert result["boundary_note_check"]["present"] is True

def test_run_check_require_boundary_note_fail(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, f"وفقًا للنظام [[export_record_id={real_export_id}]].\n")
    pack = load_pack(prompt_pack_path)
    result = run_check(pack, prompt_pack_path, "prompt_pack",
                       open(draft_path, "r", encoding="utf-8").read(), draft_path,
                       require_boundary_note=True)
    assert result["result"] == "FAIL"
    assert result["boundary_note_check"]["present"] is False

def test_run_check_source_record_id(prompt_pack_path, real_source_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path,
                 f"هذه إجابة معلوماتية وليست استشارة قانونية.\n\n"
                 f"وفقًا للنظام [[source_record_id={real_source_id}]].\n")
    pack = load_pack(prompt_pack_path)
    result = run_check(pack, prompt_pack_path, "prompt_pack",
                       open(draft_path, "r", encoding="utf-8").read(), draft_path)
    assert result["result"] == "PASS"
    assert result["valid_citations"] >= 1

def test_run_check_context_pack(context_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path,
                 f"هذه إجابة معلوماتية وليست استشارة قانونية.\n\n"
                 f"وفقًا للنظام [[export_record_id={real_export_id}]].\n")
    pack = load_pack(context_pack_path)
    result = run_check(pack, context_pack_path, "context_pack",
                       open(draft_path, "r", encoding="utf-8").read(), draft_path)
    assert result["result"] == "PASS"
    assert result["input_pack_type"] == "context_pack"

def test_run_check_top_level_fields(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, f"إجابة [[export_record_id={real_export_id}]].\n")
    pack = load_pack(prompt_pack_path)
    result = run_check(pack, prompt_pack_path, "prompt_pack",
                       open(draft_path, "r", encoding="utf-8").read(), draft_path)
    required = [
        "checker_version", "input_pack_type", "input_pack_path",
        "draft_answer_file", "checked_at_date", "result",
        "limitations", "legal_boundaries", "citation_syntax",
        "retrieved_record_count", "citations_found", "valid_citations",
        "invalid_citations", "citation_findings", "uncited_paragraphs",
        "boundary_note_check", "record_language_check",
        "governing_status_check", "summary",
    ]
    for field in required:
        assert field in result, f"Missing field: {field}"

def test_run_check_limitations_present(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, f"إجابة [[export_record_id={real_export_id}]].\n")
    pack = load_pack(prompt_pack_path)
    result = run_check(pack, prompt_pack_path, "prompt_pack",
                       open(draft_path, "r", encoding="utf-8").read(), draft_path)
    assert len(result["limitations"]) >= 3
    assert "mechanical" in result["limitations"][0].lower()

def test_run_check_legal_boundaries(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, f"إجابة [[export_record_id={real_export_id}]].\n")
    pack = load_pack(prompt_pack_path)
    result = run_check(pack, prompt_pack_path, "prompt_pack",
                       open(draft_path, "r", encoding="utf-8").read(), draft_path)
    assert "Arabic official source governs" in result["legal_boundaries"]

def test_run_check_record_language_check(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, f"إجابة [[export_record_id={real_export_id}]].\n")
    pack = load_pack(prompt_pack_path)
    result = run_check(pack, prompt_pack_path, "prompt_pack",
                       open(draft_path, "r", encoding="utf-8").read(), draft_path)
    assert result["record_language_check"]["all_records_arabic"] is True

def test_run_check_governing_status_check(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, f"إجابة [[export_record_id={real_export_id}]].\n")
    pack = load_pack(prompt_pack_path)
    result = run_check(pack, prompt_pack_path, "prompt_pack",
                       open(draft_path, "r", encoding="utf-8").read(), draft_path)
    assert result["governing_status_check"]["all_records_arabic_governing_text"] is True

def test_run_check_deterministic(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, f"إجابة [[export_record_id={real_export_id}]].\n")
    pack = load_pack(prompt_pack_path)
    text = open(draft_path, "r", encoding="utf-8").read()
    r1 = run_check(pack, prompt_pack_path, "prompt_pack", text, draft_path)
    r2 = run_check(pack, prompt_pack_path, "prompt_pack", text, draft_path)
    # Compare everything except checked_at_date (same-day deterministic)
    r1.pop("checked_at_date")
    r2.pop("checked_at_date")
    assert r1 == r2


# ─── format_markdown ───

def test_markdown_has_heading(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, f"إجابة [[export_record_id={real_export_id}]].\n")
    pack = load_pack(prompt_pack_path)
    result = run_check(pack, prompt_pack_path, "prompt_pack",
                       open(draft_path, "r", encoding="utf-8").read(), draft_path)
    md = format_markdown(result)
    assert "تقرير فحص دعم الاستشهاد" in md

def test_markdown_has_result(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, f"إجابة [[export_record_id={real_export_id}]].\n")
    pack = load_pack(prompt_pack_path)
    result = run_check(pack, prompt_pack_path, "prompt_pack",
                       open(draft_path, "r", encoding="utf-8").read(), draft_path)
    md = format_markdown(result)
    assert "النتيجة" in md

def test_markdown_has_limitations(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, f"إجابة [[export_record_id={real_export_id}]].\n")
    pack = load_pack(prompt_pack_path)
    result = run_check(pack, prompt_pack_path, "prompt_pack",
                       open(draft_path, "r", encoding="utf-8").read(), draft_path)
    md = format_markdown(result)
    assert "القيود" in md

def test_markdown_has_boundaries(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, f"إجابة [[export_record_id={real_export_id}]].\n")
    pack = load_pack(prompt_pack_path)
    result = run_check(pack, prompt_pack_path, "prompt_pack",
                       open(draft_path, "r", encoding="utf-8").read(), draft_path)
    md = format_markdown(result)
    assert "الحدود القانونية" in md

def test_markdown_has_summary(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, f"إجابة [[export_record_id={real_export_id}]].\n")
    pack = load_pack(prompt_pack_path)
    result = run_check(pack, prompt_pack_path, "prompt_pack",
                       open(draft_path, "r", encoding="utf-8").read(), draft_path)
    md = format_markdown(result)
    assert "الملخص" in md


# ─── CLI ───

def _run_cli(args, timeout=30):
    cmd = [sys.executable, CHECKER_SCRIPT] + args
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT, timeout=timeout)
    return r.returncode, r.stdout, r.stderr

def test_cli_help():
    rc, stdout, _ = _run_cli(["--help"])
    assert rc == 0
    assert "usage" in stdout.lower()

def test_cli_valid_citation(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path,
                 f"هذه إجابة معلوماتية وليست استشارة قانونية.\n\n"
                 f"وفقًا للنظام [[export_record_id={real_export_id}]].\n")
    rc, stdout, _ = _run_cli([
        "--prompt-pack", prompt_pack_path,
        "--draft-answer-file", draft_path,
        "--format", "json"
    ])
    assert rc == 0
    data = json.loads(stdout)
    assert data["result"] == "PASS"

def test_cli_invalid_citation(prompt_pack_path, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, "[[export_record_id=FAKE-NOT-IN-PACK]].\n")
    rc, stdout, _ = _run_cli([
        "--prompt-pack", prompt_pack_path,
        "--draft-answer-file", draft_path,
        "--format", "json"
    ])
    # FAIL exits with code 1
    data = json.loads(stdout)
    assert data["result"] == "FAIL"
    assert data["invalid_citations"] >= 1

def test_cli_no_citation_fails(prompt_pack_path, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, "هذه إجابة معلوماتية وليست استشارة قانونية.\n\nفقًا للنظام، تتولى الجمعية العامة اختيار أعضاء مجلس الإدارة.\n")
    rc, stdout, _ = _run_cli([
        "--prompt-pack", prompt_pack_path,
        "--draft-answer-file", draft_path,
        "--format", "json"
    ])
    data = json.loads(stdout)
    assert data["result"] == "FAIL"

def test_cli_require_citation_per_paragraph(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path,
                 f"هذه إجابة معلوماتية وليست استشارة قانونية للمراجعة القانونية [[export_record_id={real_export_id}]].\n\n"
                 f"وفقًا للنظام [[export_record_id={real_export_id}]].\n\n"
                 f"كما تتولى المراقبة [[export_record_id={real_export_id}]].\n")
    rc, stdout, _ = _run_cli([
        "--prompt-pack", prompt_pack_path,
        "--draft-answer-file", draft_path,
        "--require-citation-per-paragraph",
        "--format", "json"
    ])
    assert rc == 0
    data = json.loads(stdout)
    assert data["result"] == "PASS"

def test_cli_require_boundary_note_pass(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path,
                 f"هذه إجابة معلوماتية وليست استشارة قانونية.\n\n"
                 f"وفقًا للنظام [[export_record_id={real_export_id}]].\n")
    rc, stdout, _ = _run_cli([
        "--prompt-pack", prompt_pack_path,
        "--draft-answer-file", draft_path,
        "--require-boundary-note",
        "--format", "json"
    ])
    assert rc == 0
    data = json.loads(stdout)
    assert data["result"] == "PASS"

def test_cli_require_boundary_note_fail(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, f"وفقًا للنظام [[export_record_id={real_export_id}]].\n")
    rc, stdout, _ = _run_cli([
        "--prompt-pack", prompt_pack_path,
        "--draft-answer-file", draft_path,
        "--require-boundary-note",
        "--format", "json"
    ])
    data = json.loads(stdout)
    assert data["result"] == "FAIL"

def test_cli_context_pack_input(context_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path,
                 f"هذه إجابة معلوماتية وليست استشارة قانونية.\n\n"
                 f"وفقًا للنظام [[export_record_id={real_export_id}]].\n")
    rc, stdout, _ = _run_cli([
        "--context-pack", context_pack_path,
        "--draft-answer-file", draft_path,
        "--format", "json"
    ])
    assert rc == 0
    data = json.loads(stdout)
    assert data["input_pack_type"] == "context_pack"

def test_cli_markdown_output(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, f"إجابة [[export_record_id={real_export_id}]].\n")
    rc, stdout, _ = _run_cli([
        "--prompt-pack", prompt_pack_path,
        "--draft-answer-file", draft_path,
        "--format", "markdown"
    ])
    assert rc == 0
    assert "تقرير فحص دعم الاستشهاد" in stdout

def test_cli_output_to_file(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, f"إجابة [[export_record_id={real_export_id}]].\n")
    output_path = os.path.join(tmpdir, "output.json")
    rc, stdout, stderr = _run_cli([
        "--prompt-pack", prompt_pack_path,
        "--draft-answer-file", draft_path,
        "--format", "json",
        "--output", output_path
    ])
    assert rc == 0
    assert os.path.isfile(output_path)
    with open(output_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "checker_version" in data

def test_cli_both_packs_rejected(prompt_pack_path, context_pack_path, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, "test\n")
    rc, stdout, stderr = _run_cli([
        "--prompt-pack", prompt_pack_path,
        "--context-pack", context_pack_path,
        "--draft-answer-file", draft_path,
        "--format", "json"
    ])
    assert rc != 0

def test_cli_neither_pack_rejected(tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, "test\n")
    rc, stdout, stderr = _run_cli([
        "--draft-answer-file", draft_path,
        "--format", "json"
    ])
    assert rc != 0

def test_cli_source_record_id(prompt_pack_path, real_source_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path,
                 f"هذه إجابة معلوماتية وليست استشارة قانونية.\n\n"
                 f"وفقًا للنظام [[source_record_id={real_source_id}]].\n")
    rc, stdout, _ = _run_cli([
        "--prompt-pack", prompt_pack_path,
        "--draft-answer-file", draft_path,
        "--format", "json"
    ])
    assert rc == 0
    data = json.loads(stdout)
    assert data["result"] == "PASS"
    assert data["valid_citations"] >= 1

def test_cli_deterministic(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, f"إجابة [[export_record_id={real_export_id}]].\n")
    args = ["--prompt-pack", prompt_pack_path, "--draft-answer-file", draft_path, "--format", "json"]
    rc1, stdout1, _ = _run_cli(args)
    rc2, stdout2, _ = _run_cli(args)
    assert stdout1 == stdout2

def test_cli_does_not_modify_repo_files(prompt_pack_path, real_export_id, tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    _write_draft(draft_path, f"إجابة [[export_record_id={real_export_id}]].\n")
    source_files = [
        JSONL_PATH,
        PROMPT_PACK_SCRIPT,
        CONTEXT_PACK_SCRIPT,
        CHECKER_SCRIPT,
    ]
    mtimes_before = {f: os.path.getmtime(f) for f in source_files if os.path.exists(f)}
    _run_cli(["--prompt-pack", prompt_pack_path, "--draft-answer-file", draft_path, "--format", "json"])
    mtimes_after = {f: os.path.getmtime(f) for f in source_files if os.path.exists(f)}
    for f in mtimes_before:
        assert mtimes_before[f] == mtimes_after[f], f"File modified: {f}"