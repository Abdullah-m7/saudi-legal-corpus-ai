#!/usr/bin/env python3
"""
Tests for the operator demo pack.

Validates that all required files, sections, boundaries, commands,
and referenced scripts exist and are correct.
"""

import os
import re
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK_DIR = os.path.join(REPO_ROOT, "docs", "operator_demo_pack")
VALIDATOR_PATH = os.path.join(REPO_ROOT, "scripts", "validate_operator_demo_pack.py")

REQUIRED_FILES = [
    "START_HERE_AR.md",
    "DEMO_SCRIPT_AR.md",
    "REHEARSAL_CHECKLIST_AR.md",
    "COMMANDS_AR.md",
    "BOUNDARIES_AR.md",
]


@pytest.fixture
def pack_text():
    """Concatenate all pack file contents."""
    text = ""
    for fname in REQUIRED_FILES:
        path = os.path.join(PACK_DIR, fname)
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                text += f.read() + "\n"
    return text


@pytest.fixture
def file_contents():
    """Dict of filename -> content."""
    result = {}
    for fname in REQUIRED_FILES:
        path = os.path.join(PACK_DIR, fname)
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                result[fname] = f.read()
    return result


class TestRequiredFiles:
    def test_all_required_files_exist(self):
        for fname in REQUIRED_FILES:
            assert os.path.isfile(os.path.join(PACK_DIR, fname)), f"Missing: {fname}"

    def test_only_markdown_files_in_pack(self):
        if os.path.isdir(PACK_DIR):
            for fname in os.listdir(PACK_DIR):
                if os.path.isfile(os.path.join(PACK_DIR, fname)):
                    assert fname.endswith(".md"), f"Non-markdown file: {fname}"


class TestBoundaries:
    REQUIRED_BOUNDARY_PHRASES = [
        "المصدر العربي الرسمي هو الحاكم",
        "ليست استشارة قانونية",
        "ليست ترجمة رسمية",
        "لا تفسير قانوني",
        "لا استنتاجات قانونية مولدة",
        "لا حكم على الصحة القانونية",
        "لا تحقق الدعم الدلالي",
        "لا استدعاء LLM",
        "لا RAG",
        "لا إصدار عام",
    ]

    def test_boundary_phrases_present(self, pack_text):
        for phrase in self.REQUIRED_BOUNDARY_PHRASES:
            assert phrase in pack_text, f"Missing boundary phrase: {phrase}"

    def test_no_public_release_claim(self, pack_text):
        assert not re.search(r"إصدار عام نشط|public release active", pack_text, re.IGNORECASE)

    def test_no_legal_advice_claim(self, pack_text):
        assert not re.search(r"نقدم استشارة قانونية|provides legal advice", pack_text, re.IGNORECASE)

    def test_no_official_translation_claim(self, pack_text):
        assert not re.search(r"ترجمة رسمية معتمدة|official translation provided", pack_text, re.IGNORECASE)

    def test_no_generated_answers_claim(self, pack_text):
        assert not re.search(r"يولد إجابات قانونية بنجاح|successfully generates legal answers", pack_text, re.IGNORECASE)

    def test_no_llm_call_claim(self, pack_text):
        assert not re.search(r"يستدعي نموذجاً لغوياً بنجاح|calls an LLM successfully|uses GPT|uses Claude", pack_text, re.IGNORECASE)

    def test_no_rag_claim(self, pack_text):
        assert not re.search(r"نظام RAG نشط|RAG system active", pack_text, re.IGNORECASE)

    def test_no_api_claim(self, pack_text):
        assert not re.search(r"API نشط|API endpoint live|serves an API", pack_text, re.IGNORECASE)

    def test_no_network_claim(self, pack_text):
        assert not re.search(r"يتطلب اتصالاً بالشبكة|requires network|network required", pack_text, re.IGNORECASE)


class TestCommands:
    REQUIRED_COMMANDS = [
        "make validate",
        "make corpus-retrieval-demo-scenarios-validate",
        "make corpus-retrieval-demo-scenarios-smoke",
        "run_retrieval_demo_scenarios.py",
        "run_retrieval_workflow.py",
    ]

    def test_required_commands_referenced(self, pack_text):
        for cmd in self.REQUIRED_COMMANDS:
            assert cmd in pack_text, f"Missing command: {cmd}"

    def test_manual_workflow_command_board(self, pack_text):
        assert "مجلس الإدارة" in pack_text
        assert "--mode prepare_prompt" in pack_text

    def test_manual_workflow_command_track_filter(self, pack_text):
        assert "التصفية" in pack_text
        assert "--track" in pack_text

    def test_manual_workflow_command_record_type_filter(self, pack_text):
        assert "نموذج" in pack_text
        assert "--record-type" in pack_text


class TestReferencedScripts:
    REFERENCED_SCRIPTS = [
        "scripts/run_retrieval_demo_scenarios.py",
        "scripts/run_retrieval_workflow.py",
        "scripts/validate_retrieval_demo_scenarios.py",
        "scripts/search_primary_arabic_export.py",
        "scripts/build_retrieval_context_pack.py",
        "scripts/build_retrieval_prompt_pack.py",
        "scripts/check_citation_support.py",
    ]

    def test_scripts_exist(self):
        for script in self.REFERENCED_SCRIPTS:
            path = os.path.join(REPO_ROOT, script)
            assert os.path.isfile(path), f"Script not found: {script}"

    def test_validator_exists(self):
        assert os.path.isfile(VALIDATOR_PATH)


class TestStartHere:
    def test_has_quick_start(self, file_contents):
        text = file_contents.get("START_HERE_AR.md", "")
        assert "البدء السريع" in text or "quick start" in text.lower()

    def test_has_what_it_is_not(self, file_contents):
        text = file_contents.get("START_HERE_AR.md", "")
        assert "ليس RAG" in text or "ليس" in text

    def test_has_output_location(self, file_contents):
        text = file_contents.get("START_HERE_AR.md", "")
        assert "/tmp" in text or "مؤقت" in text

    def test_has_what_not_to_say(self, file_contents):
        text = file_contents.get("START_HERE_AR.md", "")
        assert "ما لا تقوله" in text or "لا تقل" in text


class TestDemoScript:
    EXPECTED_SECTIONS = [
        "المشكلة", "الأساس القانوني", "البحث المحلي", "حزمة السياق",
        "حزمة الطلب", "فاحص الاستشهادات", "سير العمل المتكامل",
        "سيناريوهات العرض", "الحدود", "RAG"
    ]

    def test_has_all_sections(self, file_contents):
        text = file_contents.get("DEMO_SCRIPT_AR.md", "")
        for section in self.EXPECTED_SECTIONS:
            assert section in text, f"Missing section: {section}"

    def test_has_time_estimate(self, file_contents):
        text = file_contents.get("DEMO_SCRIPT_AR.md", "")
        assert "دقائق" in text or "دقيقة" in text or "minute" in text.lower()


class TestRehearsalChecklist:
    EXPECTED_ITEMS = [
        "المستودع نظيف", "make validate", "demo-scenarios-validate",
        "demo-scenarios-smoke", "خارج المستودع", "لا إصدار عام", "LLM"
    ]

    def test_has_key_items(self, file_contents):
        text = file_contents.get("REHEARSAL_CHECKLIST_AR.md", "")
        for item in self.EXPECTED_ITEMS:
            assert item in text, f"Missing checklist item: {item}"


class TestValidatorScript:
    def test_validator_exists(self):
        assert os.path.isfile(VALIDATOR_PATH)

    def test_validator_parses(self):
        import ast
        with open(VALIDATOR_PATH, "r", encoding="utf-8") as f:
            ast.parse(f.read())


class TestNoAttribution:
    def test_no_co_author(self, pack_text):
        assert not re.search(r"Co-authored-by", pack_text, re.IGNORECASE)

    def test_no_generated_by(self, pack_text):
        assert not re.search(r"Generated by|Created by.*AI|Powered by.*GPT", pack_text, re.IGNORECASE)