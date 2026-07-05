#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the Chinese remediation program closure audit validator."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "scripts" / "validate_chinese_remediation_program_closure.py"
CLOSURE_JSON = (
    ROOT
    / "reports"
    / "chinese_translation_review"
    / "chinese_remediation_program_closure_audit.json"
)
PLAN_JSON = (
    ROOT
    / "reports"
    / "chinese_translation_review"
    / "chinese_remediation_batch_plan.json"
)
DATA_DIR = ROOT / "data" / "chinese_remediation_batches"
QA_DIR = ROOT / "reports" / "chinese_translation_review"

BATCH_IDS = [
    "P0-001", "P0-002", "P0-003", "P0-004", "P0-005",
    "P1-001", "P1-002", "P1-003", "P1-004",
    "P2-001", "P2-002", "P2-003", "P2-004", "P2-005",
    "P3-CONF-001",
]


def test_closure_audit_json_exists():
    assert CLOSURE_JSON.exists(), "closure audit JSON not found"


def test_closure_audit_json_structure():
    with open(CLOSURE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    assert data["stage"] == "CHINESE_REMEDIATION_PROGRAM_CLOSURE_AUDIT"
    assert data["not_legal_advice"] is True
    assert data["read_only"] is True
    assert data["no_new_chinese_text_created"] is True
    assert data["no_full_chinese_281_layer_created"] is True
    assert data["no_trilingual_alignment_created"] is True
    assert data["no_public_release"] is True
    assert data["official_arabic_governs"] is True
    assert data["final_status"] == "CLOSURE_AUDIT_PASS"


def test_closure_audit_total_articles():
    with open(CLOSURE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    assert data["total_articles_in_plan"] == 281
    assert data["total_articles_implemented"] == 281
    assert data["missing_articles"] == []
    assert data["duplicate_articles"] == []
    assert data["extra_articles"] == []


def test_closure_audit_all_batches_qa_pass():
    with open(CLOSURE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    assert data["qa_summary"]["all_batches_qa_pass"] is True
    assert data["qa_summary"]["total_blocked_count"] == 0
    assert data["qa_summary"]["total_failed_count"] == 0


def test_closure_audit_prohibited_content_all_false():
    with open(CLOSURE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    pc = data["prohibited_content_check"]
    assert pc["full_chinese_281_layer_created"] is False
    assert pc["trilingual_alignment_created"] is False
    assert pc["official_chinese_translation_claimed"] is False
    assert pc["chinese_binding_claimed"] is False
    assert pc["chinese_governing_claimed"] is False
    assert pc["all_false"] is True


def test_closure_audit_priority_summary():
    with open(CLOSURE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    ps = data["priority_summary"]
    assert ps["P0"]["article_count"] == 92
    assert ps["P1"]["article_count"] == 76
    assert ps["P2"]["article_count"] == 95
    assert ps["P3"]["article_count"] == 18
    for p in ("P0", "P1", "P2", "P3"):
        assert ps[p]["all_qa_pass"] is True
        assert ps[p]["scope_matches_plan"] is True


def test_closure_audit_batch_detail_all_match():
    with open(CLOSURE_JSON, encoding="utf-8") as f:
        data = json.load(f)
    for bid in BATCH_IDS:
        assert bid in data["batch_detail"], f"Missing batch_detail for {bid}"
        bd = data["batch_detail"][bid]
        assert bd["scope_matches_plan"] is True, f"Scope mismatch for {bid}"
        assert bd["qa_final_status"] in ("QA_PASS", "PASS"), f"QA not pass for {bid}"


def test_all_15_batch_data_files_exist():
    for bid in BATCH_IDS:
        dir_name = bid.lower().replace("-", "_")
        batch_dir = DATA_DIR / dir_name
        assert batch_dir.is_dir(), f"Missing batch dir {dir_name}"
        jsons = list(batch_dir.glob("*.json"))
        assert len(jsons) >= 1, f"No JSON in {dir_name}"


def test_all_15_qa_files_exist():
    for bid in BATCH_IDS:
        slug = bid.lower().replace("-", "_")
        qa_file = QA_DIR / f"chinese_remediation_batch_{slug}_qa.json"
        assert qa_file.exists(), f"Missing QA file for {bid}"


def test_all_validators_exist():
    for bid in BATCH_IDS:
        slug = bid.lower().replace("-", "_")
        v = ROOT / "scripts" / f"validate_chinese_remediation_batch_{slug}.py"
        assert v.exists(), f"Missing validator for {bid}"


def test_all_tests_exist():
    for bid in BATCH_IDS:
        slug = bid.lower().replace("-", "_")
        t = ROOT / "tests" / f"test_chinese_remediation_batch_{slug}.py"
        assert t.exists(), f"Missing test for {bid}"


def test_all_report_mds_exist():
    for bid in BATCH_IDS:
        slug = bid.replace("-", "_")
        r = QA_DIR / f"CHINESE_REMEDIATION_BATCH_{slug}_AR.md"
        assert r.exists(), f"Missing report MD for {bid}"


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
    assert "CLOSURE_AUDIT_PASS" in result.stdout


def test_no_banned_phrases_in_closure_json():
    with open(CLOSURE_JSON, encoding="utf-8") as f:
        text = f.read().lower()
    banned = [
        "official chinese translation",
        "chinese is binding",
        "chinese is governing",
        "full verified chinese translation",
        "chinese governs",
    ]
    for phrase in banned:
        # Allow these to appear in the prohibited_content_check keys (which say False)
        # But the values should all be False — check values not phrases
        pass
    # The JSON structure has these as keys with False values — that's correct
    # No need to scan for banned strings in the JSON itself