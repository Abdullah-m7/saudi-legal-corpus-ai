#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the listed joint-stock implementing regulation Arabic source intake validator."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "scripts" / "validate_implementing_regulations_listed_jsc_arabic_source.py"
INTAKE_JSON = (
    ROOT
    / "data"
    / "implementing_regulations"
    / "listed_joint_stock"
    / "listed_joint_stock_implementing_regulation_arabic_source.json"
)
MANIFEST_JSON = (
    ROOT
    / "data"
    / "implementing_regulations"
    / "listed_joint_stock"
    / "source_manifest.json"
)
ARABIC_REPORT = (
    ROOT
    / "reports"
    / "implementing_regulations"
    / "LISTED_JOINT_STOCK_ARABIC_SOURCE_INTAKE_AR.md"
)


def test_intake_json_exists():
    assert INTAKE_JSON.exists(), "intake JSON not found"


def test_intake_json_structure():
    with open(INTAKE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    assert data["stage"] == "IMPLEMENTING_REGULATIONS_LISTED_JSC_ARABIC_SOURCE_INTAKE"
    assert data["not_legal_advice"] is True
    assert data["corpus_track"] == "implementing_regulations/listed_joint_stock"
    assert data["separate_from_parent_law"] is True
    assert data["is_specialized_implementing_regulation"] is True
    assert data["is_general_implementing_regulation"] is False


def test_intake_specialized_scope():
    with open(INTAKE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    assert "شركات المساهمة المدرجة" in data["specialized_scope"]


def test_intake_article_count():
    with open(INTAKE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["articles"]) == 69


def test_intake_articles_have_text():
    with open(INTAKE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    for i, art in enumerate(data["articles"]):
        assert art["official_text_ar"], f"Article {i+1} missing official_text_ar"
        assert art["text_hash_sha256"], f"Article {i+1} missing text_hash_sha256"
        assert art["article_label"], f"Article {i+1} missing article_label"


def test_intake_chapters():
    with open(INTAKE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["chapters"]) == 14
    assert data["chapter_count"] == 14


def test_intake_appendix():
    with open(INTAKE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    assert data["has_appendix"] is True
    assert data["appendix_text"] is not None


def test_intake_no_english_text():
    with open(INTAKE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    assert data["no_new_english_text"] is True
    assert data["english_status"] == "not_yet_added"


def test_intake_no_chinese_text():
    with open(INTAKE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    assert data["no_new_chinese_text"] is True
    assert data["chinese_status"] == "not_yet_added"
    assert data["chinese_official"] is False
    assert data["chinese_binding"] is False
    assert data["chinese_governing"] is False


def test_intake_no_trilingual_or_release():
    with open(INTAKE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    assert data["no_trilingual_alignment"] is True
    assert data["public_release_created"] is False


def test_intake_provenance():
    with open(INTAKE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    prov = data["provenance"]
    assert prov["source_title"] == "اللائحة التنفيذية لنظام الشركات الخاصة بشركات المساهمة المدرجة"
    assert prov["source_url"] == "https://www.uqn.gov.sa/decisions-and-regulations/4001295"
    assert prov["publication_date_hijri"] == "1448-1-18"
    assert prov["issuing_authority"] == "مجلس هيئة السوق المالية"
    assert prov["source_hash_sha256"] is not None
    assert prov["uncertainty_notes"] is not None


def test_intake_legal_status_boundaries():
    with open(INTAKE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    lsb = data["legal_status_boundaries"]
    assert lsb["arabic_governs"] is True
    assert lsb["not_official"] is True
    assert lsb["not_binding"] is True
    assert lsb["not_governing"] is True
    assert lsb["not_legal_advice"] is True
    assert lsb["specialized_scope_only"] is True
    assert lsb["parent_law_unchanged"] is True


def test_manifest_exists_and_consistent():
    assert MANIFEST_JSON.exists(), "source manifest not found"
    with open(MANIFEST_JSON, encoding="utf-8") as f:
        manifest = json.load(f)
    with open(INTAKE_JSON, encoding="utf-8") as f:
        intake = json.load(f)
    assert manifest["source_hash_sha256"] == intake["provenance"]["source_hash_sha256"]
    assert manifest["article_count"] == 69
    assert manifest["is_specialized"] is True
    assert manifest["is_general"] is False


def test_arabic_report_exists():
    assert ARABIC_REPORT.exists(), "Arabic report not found"


def test_parent_law_files_unchanged():
    parent_files = [
        ROOT / "data" / "official_arabic_legal_llm" / "companies_law_m132_1443_official_arabic_legal_llm_001_281.json",
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
    assert "69 articles" in result.stdout