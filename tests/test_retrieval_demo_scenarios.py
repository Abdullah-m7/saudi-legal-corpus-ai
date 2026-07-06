#!/usr/bin/env python3
"""
Tests for retrieval demo scenarios.

Validates the curated scenarios file and the validator itself.
Does NOT run the full workflow (that is done by the validator smoke target).
"""

import json
import os
import re
import sys
import tempfile

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENARIOS_PATH = os.path.join(REPO_ROOT, "data", "demo_scenarios", "retrieval_demo_scenarios_v1.json")
VALIDATOR_PATH = os.path.join(REPO_ROOT, "scripts", "validate_retrieval_demo_scenarios.py")


@pytest.fixture
def scenarios_data():
    with open(SCENARIOS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class TestScenariosFile:
    """Tests for the scenarios JSON file structure and content."""

    def test_file_exists(self):
        assert os.path.isfile(SCENARIOS_PATH)

    def test_parses_as_json(self, scenarios_data):
        assert isinstance(scenarios_data, dict)

    def test_has_required_top_level_fields(self, scenarios_data):
        required = [
            "scenarios_version",
            "source_export_file",
            "source_export_record_count",
            "source_workflow_runner",
            "boundary_note",
            "scenarios",
        ]
        for field in required:
            assert field in scenarios_data, f"Missing top-level field: {field}"

    def test_source_export_record_count_is_450(self, scenarios_data):
        assert scenarios_data["source_export_record_count"] == 450

    def test_scenario_count_in_5_to_8(self, scenarios_data):
        count = len(scenarios_data["scenarios"])
        assert 5 <= count <= 8, f"Scenario count {count} not in [5, 8]"

    def test_source_workflow_runner_path(self, scenarios_data):
        assert "run_retrieval_workflow.py" in scenarios_data["source_workflow_runner"]

    def test_source_export_file_path(self, scenarios_data):
        assert "primary_arabic_governing_records.jsonl" in scenarios_data["source_export_file"]


class TestScenarioFields:
    """Tests for individual scenario fields."""

    REQUIRED_FIELDS = [
        "scenario_id",
        "title_ar",
        "query",
        "purpose_ar",
        "mode",
        "limit",
        "prompt_mode",
        "formats",
        "expected_min_total_matches",
        "expected_artifacts",
        "boundary_note",
        "demo_script_ar",
    ]

    def test_all_scenarios_have_required_fields(self, scenarios_data):
        for sc in scenarios_data["scenarios"]:
            for field in self.REQUIRED_FIELDS:
                assert field in sc, f"Scenario {sc.get('scenario_id')}: missing {field}"

    def test_scenario_ids_unique(self, scenarios_data):
        ids = [sc["scenario_id"] for sc in scenarios_data["scenarios"]]
        assert len(ids) == len(set(ids)), f"Duplicate IDs: {ids}"

    def test_all_queries_arabic(self, scenarios_data):
        arabic_re = re.compile(r"[\u0600-\u06FF]")
        for sc in scenarios_data["scenarios"]:
            assert arabic_re.search(sc["query"]), f"Scenario {sc['scenario_id']}: no Arabic in query"

    def test_modes_are_valid(self, scenarios_data):
        valid_modes = {"prepare_prompt", "check_draft"}
        for sc in scenarios_data["scenarios"]:
            assert sc["mode"] in valid_modes, f"Scenario {sc['scenario_id']}: invalid mode {sc['mode']}"

    def test_prompt_modes_are_valid(self, scenarios_data):
        valid_pm = {"evidence_brief", "cautious_answer_draft", "citation_check"}
        for sc in scenarios_data["scenarios"]:
            assert sc["prompt_mode"] in valid_pm, f"Scenario {sc['scenario_id']}: invalid prompt_mode"

    def test_formats_are_valid(self, scenarios_data):
        valid_fmt = {"json", "markdown", "both"}
        for sc in scenarios_data["scenarios"]:
            assert sc["formats"] in valid_fmt, f"Scenario {sc['scenario_id']}: invalid formats"

    def test_limits_positive(self, scenarios_data):
        for sc in scenarios_data["scenarios"]:
            assert sc["limit"] >= 1, f"Scenario {sc['scenario_id']}: limit < 1"

    def test_expected_min_positive(self, scenarios_data):
        for sc in scenarios_data["scenarios"]:
            assert sc["expected_min_total_matches"] >= 1, f"Scenario {sc['scenario_id']}: expected_min < 1"

    def test_expected_artifacts_non_empty(self, scenarios_data):
        for sc in scenarios_data["scenarios"]:
            assert len(sc["expected_artifacts"]) > 0, f"Scenario {sc['scenario_id']}: empty expected_artifacts"

    def test_expected_artifacts_contain_manifest(self, scenarios_data):
        for sc in scenarios_data["scenarios"]:
            assert "workflow_manifest.json" in sc["expected_artifacts"], \
                f"Scenario {sc['scenario_id']}: missing workflow_manifest.json in expected_artifacts"

    def test_no_legal_advice_claims(self, scenarios_data):
        prohibited = ["legal advice", "legal conclusion", "legal opinion"]
        for sc in scenarios_data["scenarios"]:
            all_text = json.dumps(sc, ensure_ascii=False).lower()
            for term in prohibited:
                # Check that prohibited terms don't appear except in negation context
                if term in all_text:
                    bn = sc.get("boundary_note", "").lower()
                    if term in bn and ("not " in bn or "لا" in bn or "no " in bn):
                        continue
                    pytest.fail(f"Scenario {sc['scenario_id']}: prohibited term '{term}' in non-negation context")

    def test_no_llm_api_dependencies(self, scenarios_data):
        llm_keywords = ["openai", "anthropic", "llama_cpp", "ollama", "transformers", "langchain"]
        for sc in scenarios_data["scenarios"]:
            for field in ["mode", "prompt_mode", "formats"]:
                val = str(sc.get(field, "")).lower()
                for kw in llm_keywords:
                    assert kw not in val, f"Scenario {sc['scenario_id']}: LLM keyword {kw} in {field}"

    def test_boundary_note_present_in_all(self, scenarios_data):
        for sc in scenarios_data["scenarios"]:
            assert sc["boundary_note"], f"Scenario {sc['scenario_id']}: empty boundary_note"

    def test_demo_script_ar_present(self, scenarios_data):
        for sc in scenarios_data["scenarios"]:
            assert sc["demo_script_ar"], f"Scenario {sc['scenario_id']}: empty demo_script_ar"

    def test_title_ar_present(self, scenarios_data):
        for sc in scenarios_data["scenarios"]:
            assert sc["title_ar"], f"Scenario {sc['scenario_id']}: empty title_ar"

    def test_purpose_ar_present(self, scenarios_data):
        for sc in scenarios_data["scenarios"]:
            assert sc["purpose_ar"], f"Scenario {sc['scenario_id']}: empty purpose_ar"


class TestValidatorScript:
    """Tests for the validator script itself."""

    def test_validator_exists(self):
        assert os.path.isfile(VALIDATOR_PATH)

    def test_validator_imports(self):
        sys.path.insert(0, REPO_ROOT)
        # Just verify it parses
        import ast
        with open(VALIDATOR_PATH, "r", encoding="utf-8") as f:
            ast.parse(f.read())

    def test_no_committed_generated_outputs(self):
        demo_dir = os.path.join(REPO_ROOT, "data", "demo_scenarios")
        files = [f for f in os.listdir(demo_dir) if os.path.isfile(os.path.join(demo_dir, f))]
        assert set(files) == {"retrieval_demo_scenarios_v1.json"}, \
            f"Unexpected files in demo_scenarios: {files}"


class TestScenarioRunnerScript:
    """Tests for the helper runner script."""

    def test_runner_exists(self):
        runner_path = os.path.join(REPO_ROOT, "scripts", "run_retrieval_demo_scenarios.py")
        assert os.path.isfile(runner_path)

    def test_runner_parses(self):
        import ast
        runner_path = os.path.join(REPO_ROOT, "scripts", "run_retrieval_demo_scenarios.py")
        with open(runner_path, "r", encoding="utf-8") as f:
            ast.parse(f.read())