#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for Implementing Regulations Arabic Program Closure Audit."""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT_PATH = os.path.join(ROOT, "reports", "implementing_regulations", "implementing_regulations_arabic_program_closure_audit.json")
GEN_LLM = os.path.join(ROOT, "data", "implementing_regulations", "general", "general_implementing_regulations_arabic_legal_llm.json")
GEN_FORMS = os.path.join(ROOT, "data", "implementing_regulations", "general", "general_implementing_regulations_arabic_forms_llm.json")
LJS_LLM = os.path.join(ROOT, "data", "implementing_regulations", "listed_joint_stock", "listed_joint_stock_implementing_regulation_arabic_legal_llm.json")
LJS_APP = os.path.join(ROOT, "data", "implementing_regulations", "listed_joint_stock", "listed_joint_stock_implementing_regulation_arabic_appendix_llm.json")
GENERATOR = os.path.join(ROOT, "scripts", "gen_implementing_regulations_arabic_program_closure.py")


@pytest.fixture(scope="module")
def audit():
    with open(AUDIT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class TestAuditStructure:
    def test_exists(self):
        assert os.path.isfile(AUDIT_PATH)

    def test_stage(self, audit):
        assert audit["stage"] == "IMPLEMENTING_REGULATIONS_ARABIC_PROGRAM_CLOSURE_AUDIT"

    def test_overall_status(self, audit):
        assert audit["overall_status"] == "PASS"

    def test_has_tracks(self, audit):
        assert "general" in audit["tracks"]
        assert "listed_joint_stock" in audit["tracks"]


class TestGeneralTrack:
    def test_status_pass(self, audit):
        assert audit["tracks"]["general"]["status"] == "PASS"

    def test_95_articles(self, audit):
        assert audit["tracks"]["general"]["llm_article_record_count"] == 95

    def test_4_forms(self, audit):
        assert audit["tracks"]["general"]["form_record_count"] == 4

    def test_article_hashes_match(self, audit):
        assert audit["tracks"]["general"]["article_hash_check"]["all_match"] is True

    def test_form_hashes_match(self, audit):
        assert audit["tracks"]["general"]["form_hash_check"]["all_match"] is True

    def test_record_ids_valid(self, audit):
        assert audit["tracks"]["general"]["article_record_ids"]["all_valid"] is True

    def test_is_general(self, audit):
        assert audit["tracks"]["general"]["is_general"] is True
        assert audit["tracks"]["general"]["is_specialized"] is False


class TestListedJscTrack:
    def test_status_pass(self, audit):
        assert audit["tracks"]["listed_joint_stock"]["status"] == "PASS"

    def test_69_articles(self, audit):
        assert audit["tracks"]["listed_joint_stock"]["llm_article_record_count"] == 69

    def test_1_appendix(self, audit):
        assert audit["tracks"]["listed_joint_stock"]["appendix_record_count"] == 1

    def test_article_hashes_match(self, audit):
        assert audit["tracks"]["listed_joint_stock"]["article_hash_check"]["all_match"] is True

    def test_appendix_hash_matches(self, audit):
        assert audit["tracks"]["listed_joint_stock"]["appendix_hash_check"]["matched"] is True

    def test_is_specialized(self, audit):
        assert audit["tracks"]["listed_joint_stock"]["is_specialized"] is True
        assert audit["tracks"]["listed_joint_stock"]["is_general"] is False

    def test_chapter_metadata_null(self, audit):
        assert audit["tracks"]["listed_joint_stock"]["chapter_metadata_null"] is True

    def test_article_titles_explicit(self, audit):
        assert audit["tracks"]["listed_joint_stock"]["article_titles_explicit"] is True


class TestCounts:
    def test_total_articles(self, audit):
        assert audit["counts"]["total_article_records"] == 164  # 95 + 69

    def test_total_non_article(self, audit):
        assert audit["counts"]["total_non_article_records"] == 5  # 4 forms + 1 appendix

    def test_total_all(self, audit):
        assert audit["counts"]["total_records"] == 169  # 164 + 5


class TestBoundaries:
    def test_arabic_governs(self, audit):
        assert audit["boundaries"]["arabic_governs"] is True

    def test_not_official_translation(self, audit):
        assert audit["boundaries"]["not_official_translation"] is True

    def test_not_legal_advice(self, audit):
        assert audit["boundaries"]["not_legal_advice"] is True

    def test_no_trilingual(self, audit):
        assert audit["boundaries"]["no_trilingual_alignment"] is True

    def test_no_public_release(self, audit):
        assert audit["boundaries"]["no_public_release"] is True

    def test_tracks_separate(self, audit):
        assert audit["boundaries"]["general_and_listed_tracks_are_separate"] is True

    def test_ljs_specialized_not_general(self, audit):
        assert audit["boundaries"]["listed_joint_stock_is_specialized_not_general"] is True


class TestUnchangedCorpora:
    def test_parent_law_exists(self, audit):
        assert audit["parent_law_unchanged"]["files_exist"] is True

    def test_chinese_remediation_exists(self, audit):
        assert audit["chinese_remediation_unchanged"]["closure_audit_exists"] is True


class TestIdempotence:
    def test_generator_idempotent(self):
        with open(AUDIT_PATH, "r", encoding="utf-8") as f:
            orig = f.read()
        result = subprocess.run(
            [sys.executable, GENERATOR], capture_output=True, text=True, cwd=ROOT
        )
        assert result.returncode == 0, f"Generator failed: {result.stderr}"
        with open(AUDIT_PATH, "r", encoding="utf-8") as f:
            new = f.read()
        assert new == orig, "Audit not idempotent"