#!/usr/bin/env python3
"""Tests for Retrieval Workflow Runner Foundation."""

import json
import os
import subprocess
import sys
import tempfile
import shutil
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW_SCRIPT = os.path.join(REPO_ROOT, "scripts", "run_retrieval_workflow.py")
JSONL_PATH = os.path.join(REPO_ROOT, "data", "exports", "v1", "primary_arabic_governing_records.jsonl")

# Import workflow runner directly
sys.path.insert(0, REPO_ROOT)
from scripts.run_retrieval_workflow import (
    run_workflow,
    WORKFLOW_VERSION,
    LEGAL_BOUNDARIES,
    LIMITATIONS,
    get_stable_baseline,
)


@pytest.fixture
def tmpdir():
    d = tempfile.mkdtemp(prefix="workflow_test_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


def _run_cli(args, timeout=60):
    cmd = [sys.executable, WORKFLOW_SCRIPT] + args
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


# ─── run_workflow ───

def test_prepare_prompt_basic(tmpdir):
    out_dir = os.path.join(tmpdir, "prep")
    manifest = run_workflow("مجلس الإدارة", mode="prepare_prompt", limit=3, output_dir=out_dir)
    assert manifest["mode"] == "prepare_prompt"
    assert os.path.isdir(out_dir)
    assert os.path.isfile(os.path.join(out_dir, "context_pack.json"))
    assert os.path.isfile(os.path.join(out_dir, "prompt_pack.json"))
    assert os.path.isfile(os.path.join(out_dir, "workflow_manifest.json"))

def test_prepare_prompt_both_formats(tmpdir):
    out_dir = os.path.join(tmpdir, "prep_both")
    manifest = run_workflow("مجلس الإدارة", mode="prepare_prompt", limit=3,
                            formats="both", output_dir=out_dir)
    assert os.path.isfile(os.path.join(out_dir, "context_pack.md"))
    assert os.path.isfile(os.path.join(out_dir, "prompt_pack.md"))

def test_prepare_prompt_json_only(tmpdir):
    out_dir = os.path.join(tmpdir, "prep_json")
    manifest = run_workflow("مجلس الإدارة", mode="prepare_prompt", limit=3,
                            formats="json", output_dir=out_dir)
    assert os.path.isfile(os.path.join(out_dir, "context_pack.json"))
    assert not os.path.isfile(os.path.join(out_dir, "context_pack.md"))

def test_prepare_prompt_markdown_only(tmpdir):
    out_dir = os.path.join(tmpdir, "prep_md")
    manifest = run_workflow("مجلس الإدارة", mode="prepare_prompt", limit=3,
                            formats="markdown", output_dir=out_dir)
    assert not os.path.isfile(os.path.join(out_dir, "context_pack.json"))
    assert os.path.isfile(os.path.join(out_dir, "context_pack.md"))

def test_check_draft_valid(tmpdir):
    # First build a prompt pack to get a real export_record_id
    prep_dir = os.path.join(tmpdir, "prep")
    run_workflow("مجلس الإدارة", mode="prepare_prompt", limit=3, output_dir=prep_dir)
    with open(os.path.join(prep_dir, "prompt_pack.json"), "r", encoding="utf-8") as f:
        pp = json.loads(f.read())
    rid = pp["retrieved_records"][0]["export_record_id"]

    # Create valid draft
    draft_path = os.path.join(tmpdir, "valid_draft.md")
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(f"هذه إجابة معلوماتية وليست استشارة قانونية للمراجعة القانونية [[export_record_id={rid}]].\n\n")
        f.write(f"وفقًا للنظام [[export_record_id={rid}]].\n")

    check_dir = os.path.join(tmpdir, "check")
    manifest = run_workflow("مجلس الإدارة", mode="check_draft",
                            draft_answer_file=draft_path, limit=3,
                            require_citation_per_paragraph=True,
                            output_dir=check_dir)
    assert manifest["mode"] == "check_draft"
    assert manifest["citation_check_result"]["result"] == "PASS"
    assert os.path.isfile(os.path.join(check_dir, "citation_check.json"))

def test_check_draft_invalid(tmpdir):
    draft_path = os.path.join(tmpdir, "invalid_draft.md")
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write("هذه إجابة معلوماتية.\n\n[[export_record_id=FAKE-NOT-IN-PACK]].\n")

    check_dir = os.path.join(tmpdir, "check_inv")
    manifest = run_workflow("مجلس الإدارة", mode="check_draft",
                            draft_answer_file=draft_path, limit=3,
                            output_dir=check_dir)
    assert manifest["citation_check_result"]["result"] == "FAIL"
    assert manifest["citation_check_result"]["invalid_citations"] >= 1

def test_check_draft_missing_file_raises():
    with pytest.raises((ValueError, FileNotFoundError, SystemExit)):
        run_workflow("مجلس الإدارة", mode="check_draft", draft_answer_file=None)

def test_manifest_top_level_fields(tmpdir):
    out_dir = os.path.join(tmpdir, "manifest")
    manifest = run_workflow("مجلس الإدارة", mode="prepare_prompt", limit=3, output_dir=out_dir)
    required = [
        "workflow_version", "mode", "query", "normalized_query",
        "generated_at_date", "baseline_commit", "output_dir",
        "source_export_file", "source_export_record_count",
        "retrieval_method", "limit", "filters", "prompt_mode",
        "include_full_text", "formats", "artifacts",
        "legal_boundaries", "limitations", "hygiene",
    ]
    for field in required:
        assert field in manifest, f"Missing field: {field}"

def test_manifest_workflow_version(tmpdir):
    out_dir = os.path.join(tmpdir, "ver")
    manifest = run_workflow("مجلس الإدارة", mode="prepare_prompt", limit=3, output_dir=out_dir)
    assert manifest["workflow_version"] == WORKFLOW_VERSION

def test_manifest_legal_boundaries(tmpdir):
    out_dir = os.path.join(tmpdir, "bounds")
    manifest = run_workflow("مجلس الإدارة", mode="prepare_prompt", limit=3, output_dir=out_dir)
    assert "Arabic official source governs" in manifest["legal_boundaries"]
    assert "No LLM calls, no API, no network, no embeddings" in manifest["legal_boundaries"]

def test_manifest_limitations(tmpdir):
    out_dir = os.path.join(tmpdir, "lims")
    manifest = run_workflow("مجلس الإدارة", mode="prepare_prompt", limit=3, output_dir=out_dir)
    assert len(manifest["limitations"]) >= 3

def test_manifest_hygiene(tmpdir):
    out_dir = os.path.join(tmpdir, "hyg")
    manifest = run_workflow("مجلس الإدارة", mode="prepare_prompt", limit=3, output_dir=out_dir)
    assert manifest["hygiene"]["no_llm_calls"] is True
    assert manifest["hygiene"]["no_network"] is True
    assert manifest["hygiene"]["no_embeddings"] is True

def test_manifest_source_export_record_count(tmpdir):
    out_dir = os.path.join(tmpdir, "count")
    manifest = run_workflow("مجلس الإدارة", mode="prepare_prompt", limit=3, output_dir=out_dir)
    assert manifest["source_export_record_count"] == 450

def test_manifest_baseline_commit(tmpdir):
    out_dir = os.path.join(tmpdir, "base")
    manifest = run_workflow("مجلس الإدارة", mode="prepare_prompt", limit=3, output_dir=out_dir)
    assert manifest["baseline_commit"] != "unknown"

def test_manifest_artifacts_list(tmpdir):
    out_dir = os.path.join(tmpdir, "arts")
    manifest = run_workflow("مجلس الإدارة", mode="prepare_prompt", limit=3,
                            formats="both", output_dir=out_dir)
    artifact_names = [a["name"] for a in manifest["artifacts"]]
    assert "context_pack.json" in artifact_names
    assert "prompt_pack.json" in artifact_names
    assert "workflow_manifest.json" in artifact_names
    assert "WORKFLOW_README.md" in artifact_names

def test_manifest_check_draft_has_citation_result(tmpdir):
    draft_path = os.path.join(tmpdir, "draft.md")
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write("هذه إجابة معلوماتية.\n\n[[export_record_id=FAKE]].\n")
    check_dir = os.path.join(tmpdir, "check_manifest")
    manifest = run_workflow("مجلس الإدارة", mode="check_draft",
                            draft_answer_file=draft_path, limit=3,
                            output_dir=check_dir)
    assert "citation_check_result" in manifest
    assert "draft_answer_file" in manifest

def test_deterministic_shape(tmpdir):
    d1 = os.path.join(tmpdir, "det1")
    d2 = os.path.join(tmpdir, "det2")
    m1 = run_workflow("مجلس الإدارة", mode="prepare_prompt", limit=3, formats="json", output_dir=d1)
    m2 = run_workflow("مجلس الإدارة", mode="prepare_prompt", limit=3, formats="json", output_dir=d2)
    # Remove non-deterministic fields
    for m in [m1, m2]:
        m.pop("generated_at_date", None)
        m.pop("output_dir", None)
        for a in m.get("artifacts", []):
            a.pop("path", None)
    assert m1 == m2

def test_track_filter(tmpdir):
    out_dir = os.path.join(tmpdir, "track")
    manifest = run_workflow("التصفية", mode="prepare_prompt", limit=5,
                            track="companies_law", output_dir=out_dir)
    assert manifest["filters"]["track"] == "companies_law"

def test_record_type_filter(tmpdir):
    out_dir = os.path.join(tmpdir, "rtype")
    manifest = run_workflow("الشركة", mode="prepare_prompt", limit=5,
                            record_type="article", output_dir=out_dir)
    assert manifest["filters"]["record_type"] == "article"

def test_prompt_mode(tmpdir):
    out_dir = os.path.join(tmpdir, "pmode")
    manifest = run_workflow("مجلس الإدارة", mode="prepare_prompt", limit=3,
                            prompt_mode="cautious_answer_draft", output_dir=out_dir)
    assert manifest["prompt_mode"] == "cautious_answer_draft"

def test_include_full_text(tmpdir):
    out_dir = os.path.join(tmpdir, "fulltext")
    manifest = run_workflow("مجلس الإدارة", mode="prepare_prompt", limit=3,
                            include_full_text=True, output_dir=out_dir)
    assert manifest["include_full_text"] is True

def test_workflow_readme_created(tmpdir):
    out_dir = os.path.join(tmpdir, "readme")
    run_workflow("مجلس الإدارة", mode="prepare_prompt", limit=3, output_dir=out_dir)
    assert os.path.isfile(os.path.join(out_dir, "WORKFLOW_README.md"))

def test_does_not_modify_repo_files(tmpdir):
    source_files = [
        JSONL_PATH,
        os.path.join(REPO_ROOT, "scripts/search_primary_arabic_export.py"),
        os.path.join(REPO_ROOT, "scripts/build_retrieval_context_pack.py"),
        os.path.join(REPO_ROOT, "scripts/build_retrieval_prompt_pack.py"),
        os.path.join(REPO_ROOT, "scripts/check_citation_support.py"),
        WORKFLOW_SCRIPT,
    ]
    mtimes_before = {f: os.path.getmtime(f) for f in source_files if os.path.exists(f)}
    run_workflow("الشركة", mode="prepare_prompt", limit=2,
                 output_dir=os.path.join(tmpdir, "mod"))
    mtimes_after = {f: os.path.getmtime(f) for f in source_files if os.path.exists(f)}
    for f in mtimes_before:
        assert mtimes_before[f] == mtimes_after[f], f"File modified: {f}"


# ─── CLI ───

def test_cli_help():
    rc, stdout, _ = _run_cli(["--help"])
    assert rc == 0
    assert "usage" in stdout.lower()

def test_cli_prepare_prompt(tmpdir):
    out_dir = os.path.join(tmpdir, "cli_prep")
    rc, stdout, _ = _run_cli([
        "مجلس الإدارة", "--mode", "prepare_prompt",
        "--limit", "3", "--formats", "json",
        "--output-dir", out_dir
    ])
    assert rc == 0
    assert os.path.isfile(os.path.join(out_dir, "workflow_manifest.json"))

def test_cli_check_draft_valid(tmpdir):
    # Build prep first to get a real ID
    prep_dir = os.path.join(tmpdir, "cli_prep")
    _run_cli(["مجلس الإدارة", "--mode", "prepare_prompt", "--limit", "3",
              "--formats", "json", "--output-dir", prep_dir])
    with open(os.path.join(prep_dir, "prompt_pack.json"), "r", encoding="utf-8") as f:
        pp = json.loads(f.read())
    rid = pp["retrieved_records"][0]["export_record_id"]

    draft_path = os.path.join(tmpdir, "valid.md")
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(f"هذه إجابة معلوماتية وليست استشارة قانونية للمراجعة القانونية [[export_record_id={rid}]].\n\n")
        f.write(f"وفقًا للنظام [[export_record_id={rid}]].\n")

    check_dir = os.path.join(tmpdir, "cli_check")
    rc, stdout, _ = _run_cli([
        "مجلس الإدارة", "--mode", "check_draft",
        "--draft-answer-file", draft_path,
        "--limit", "3", "--prompt-mode", "cautious_answer_draft",
        "--require-citation-per-paragraph",
        "--formats", "both", "--output-dir", check_dir
    ])
    assert rc == 0
    assert os.path.isfile(os.path.join(check_dir, "citation_check.json"))

def test_cli_check_draft_invalid(tmpdir):
    draft_path = os.path.join(tmpdir, "invalid.md")
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write("هذه إجابة معلوماتية.\n\n[[export_record_id=FAKE-NOT-IN-PACK]].\n")
    check_dir = os.path.join(tmpdir, "cli_check_inv")
    rc, stdout, stderr = _run_cli([
        "مجلس الإدارة", "--mode", "check_draft",
        "--draft-answer-file", draft_path,
        "--limit", "3", "--formats", "json",
        "--output-dir", check_dir
    ])
    # Should exit 1 on FAIL
    assert rc == 1
    cit_path = os.path.join(check_dir, "citation_check.json")
    assert os.path.isfile(cit_path)
    with open(cit_path, "r", encoding="utf-8") as f:
        data = json.loads(f.read())
    assert data["result"] == "FAIL"

def test_cli_missing_draft_fails():
    rc, stdout, stderr = _run_cli([
        "مجلس الإدارة", "--mode", "check_draft",
        "--limit", "3", "--formats", "json"
    ])
    assert rc != 0

def test_cli_default_mode_is_prepare_prompt(tmpdir):
    out_dir = os.path.join(tmpdir, "cli_default")
    rc, stdout, _ = _run_cli([
        "مجلس الإدارة", "--limit", "2", "--formats", "json",
        "--output-dir", out_dir
    ])
    assert rc == 0
    with open(os.path.join(out_dir, "workflow_manifest.json"), "r", encoding="utf-8") as f:
        manifest = json.loads(f.read())
    assert manifest["mode"] == "prepare_prompt"