#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the implementing regulations intake scaffold validator."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "scripts" / "validate_implementing_regulations_intake_scaffold.py"
SCAFFOLD_JSON = ROOT / "data" / "implementing_regulations" / "intake_scaffold.json"
SCAFFOLD_README = ROOT / "data" / "implementing_regulations" / "README.md"
ARABIC_REPORT = (
    ROOT
    / "reports"
    / "implementing_regulations"
    / "IMPLEMENTING_REGULATIONS_INTAKE_SCAFFOLD_AR.md"
)


def test_scaffold_json_exists():
    assert SCAFFOLD_JSON.exists(), "intake_scaffold.json not found"


def test_scaffold_json_structure():
    with open(SCAFFOLD_JSON, encoding="utf-8") as f:
        data = json.load(f)
    assert data["stage"] == "IMPLEMENTING_REGULATIONS_INTAKE_SCAFFOLD"
    assert data["not_legal_advice"] is True
    assert data["corpus_track"] == "implementing_regulations"
    assert data["separate_from_parent_law"] is True
    assert data["parent_law"] == "sa_companies_law_m132_1443"
    assert data["parent_law_corpus_unchanged"] is True


def test_scaffold_source_provenance_not_ingested():
    with open(SCAFFOLD_JSON, encoding="utf-8") as f:
        data = json.load(f)
    sp = data["source_provenance"]
    assert sp["status"] == "not_yet_ingested"
    assert sp["official_source_url"] is None
    assert sp["intake_date"] is None
    assert sp["source_file_hash_sha256"] is None


def test_scaffold_article_numbering_unknown():
    with open(SCAFFOLD_JSON, encoding="utf-8") as f:
        data = json.load(f)
    an = data["article_numbering"]
    assert an["scheme"] == "unknown_until_ingested"
    assert an["total_articles"] is None


def test_scaffold_arabic_layer():
    with open(SCAFFOLD_JSON, encoding="utf-8") as f:
        data = json.load(f)
    ar = data["language_layers"]["arabic"]
    assert ar["status"] == "not_yet_ingested"
    assert ar["governing"] is True


def test_scaffold_english_layer():
    with open(SCAFFOLD_JSON, encoding="utf-8") as f:
        data = json.load(f)
    en = data["language_layers"]["english"]
    assert en["status"] == "not_yet_added"
    assert en["governing"] is False
    assert en["role"] == "reference_guidance_only"


def test_scaffold_chinese_layer():
    with open(SCAFFOLD_JSON, encoding="utf-8") as f:
        data = json.load(f)
    zh = data["language_layers"]["chinese"]
    assert zh["status"] == "not_yet_added"
    assert zh["governing"] is False
    assert zh["role"] == "internal_reference_only"
    assert zh["official"] is False
    assert zh["binding"] is False


def test_scaffold_no_prohibited_content():
    with open(SCAFFOLD_JSON, encoding="utf-8") as f:
        data = json.load(f)
    assert data["no_new_chinese_text"] is True
    assert data["no_new_english_text"] is True
    assert data["no_trilingual_alignment"] is True
    assert data["public_release_created"] is False


def test_scaffold_legal_status_boundaries():
    with open(SCAFFOLD_JSON, encoding="utf-8") as f:
        data = json.load(f)
    lsb = data["legal_status_boundaries"]
    assert lsb["arabic_governs"] is True
    assert lsb["english_reference_only"] is True
    assert lsb["chinese_internal_reference_only"] is True
    assert lsb["not_official"] is True
    assert lsb["not_binding"] is True
    assert lsb["not_governing"] is True
    assert lsb["not_legal_advice"] is True
    assert lsb["separate_corpus_track"] is True
    assert lsb["parent_law_unchanged"] is True


def test_scaffold_validation_status():
    with open(SCAFFOLD_JSON, encoding="utf-8") as f:
        data = json.load(f)
    vs = data["validation_status"]
    assert vs["scaffold_validated"] is True
    assert vs["intake_validated"] is False
    assert vs["arabic_source_validated"] is False


def test_scaffold_readme_exists():
    assert SCAFFOLD_README.exists(), "scaffold README not found"


def test_arabic_report_exists():
    assert ARABIC_REPORT.exists(), "Arabic report not found"


def test_no_content_files_beyond_scaffold():
    impl_dir = ROOT / "data" / "implementing_regulations"
    all_files = set()
    for root, dirs, files in os.walk(impl_dir):
        for f in files:
            all_files.add(f)
    assert all_files == {"intake_scaffold.json", "README.md"}, f"Unexpected files: {all_files}"


def test_parent_law_files_unchanged():
    parent_files = [
        ROOT / "data" / "official_arabic_legal_llm" / "companies_law_m132_1443_official_arabic_legal_llm_001_281.json",
        ROOT / "data" / "legal_corpus_factory" / "law_profiles" / "sa_companies_law_m132_1443.profile.json",
        ROOT / "reports" / "chinese_translation_review" / "chinese_remediation_program_closure_audit.json",
    ]
    for f in parent_files:
        assert f.exists(), f"Parent law file missing: {f}"


def test_validator_exits_zero():
    result = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        timeout=60,
    )
    assert result.returncode == 0, f"Validator failed:\n{result.stdout}\n{result.stderr}"


def test_validator_output_contains_pass():
    result = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        timeout=60,
    )
    assert "ALL CHECKS PASSED" in result.stdout
    assert "SCAFFOLD" in result.stdout