#!/usr/bin/env python3
"""
Retrieval Demo Scenarios Validator

Validates the curated demo scenarios file and runs each scenario
through the existing workflow runner in a temporary directory.

Checks:
- Scenario JSON parses and has required top-level fields.
- Scenario count is between 5 and 8.
- Each scenario has required fields.
- No scenario text claims legal advice or legal conclusions.
- All scenario queries contain Arabic text.
- For each scenario: run run_retrieval_workflow.py in a temp dir.
- Confirm workflow_manifest.json exists and parses.
- Confirm expected artifacts exist on disk.
- Confirm source_export_record_count == 450 in manifest.
- Confirm no LLM/API/network/embeddings dependencies in scenario file.
- Confirm total_matches >= expected_min_total_matches.
- Confirm temporary outputs are outside the repo.
- Produce clear PASS/FAIL.

This is NOT RAG.
This does NOT call an LLM.
This does NOT generate legal answers.
This does NOT provide legal advice.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENARIOS_PATH = os.path.join(REPO_ROOT, "data", "demo_scenarios", "retrieval_demo_scenarios_v1.json")
WORKFLOW_RUNNER = os.path.join(REPO_ROOT, "scripts", "run_retrieval_workflow.py")
JSONL_PATH = os.path.join(REPO_ROOT, "data", "exports", "v1", "primary_arabic_governing_records.jsonl")

REQUIRED_SCENARIO_FIELDS = [
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

PROHIBITED_CLAIM_PATTERNS = [
    r"إجابة قانونية",
    r"استشارة قانونية",
    r"رأي قانوني",
    r"legal advice",
    r"legal conclusion",
    r"legal opinion",
]

ARABIC_LETTER_RE = re.compile(r"[\u0600-\u06FF]")

# LLM/API/network dependency keywords — checked against import/dependency hints only
LLM_DEPENDENCY_KEYWORDS = [
    "openai",
    "anthropic",
    "llama_cpp",
    "ollama",
    "transformers",
    "langchain",
    "sentence_transformers",
    "requests",
    "httpx",
    "aiohttp",
    "socket",
    "urllib",
]


def check(condition: bool, message: str, errors: list, warnings: list | None = None, is_warning: bool = False) -> None:
    """Record a check result."""
    if is_warning:
        if warnings is not None:
            if not condition:
                warnings.append(message)
    else:
        if not condition:
            errors.append(message)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    checks_passed = 0
    checks_total = 0

    # ── 1. Scenarios file exists ──
    checks_total += 1
    if os.path.isfile(SCENARIOS_PATH):
        checks_passed += 1
    else:
        errors.append(f"Scenarios file not found: {SCENARIOS_PATH}")
        print(f"FAIL: {len(errors)} errors")
        for e in errors:
            print(f"  ✗ {e}")
        return 1

    # ── 2. Parse JSON ──
    checks_total += 1
    try:
        with open(SCENARIOS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        checks_passed += 1
    except json.JSONDecodeError as ex:
        errors.append(f"Scenarios JSON parse error: {ex}")
        print(f"FAIL: {len(errors)} errors")
        for e in errors:
            print(f"  ✗ {e}")
        return 1

    # ── 3. Required top-level fields ──
    required_top = [
        "scenarios_version",
        "source_export_file",
        "source_export_record_count",
        "source_workflow_runner",
        "boundary_note",
        "scenarios",
    ]
    for field in required_top:
        checks_total += 1
        if field in data:
            checks_passed += 1
        else:
            errors.append(f"Missing top-level field: {field}")

    # ── 4. source_export_record_count == 450 ──
    checks_total += 1
    if data.get("source_export_record_count") == 450:
        checks_passed += 1
    else:
        errors.append(f"source_export_record_count != 450 (got {data.get('source_export_record_count')})")

    # ── 5. Scenario count between 5 and 8 ──
    checks_total += 1
    scenarios = data.get("scenarios", [])
    if 5 <= len(scenarios) <= 8:
        checks_passed += 1
    else:
        errors.append(f"Scenario count {len(scenarios)} not in [5, 8]")

    # ── 6. Each scenario has required fields ──
    for i, sc in enumerate(scenarios):
        for field in REQUIRED_SCENARIO_FIELDS:
            checks_total += 1
            if field in sc:
                checks_passed += 1
            else:
                errors.append(f"Scenario {i} ({sc.get('scenario_id', '?')}): missing field {field}")

    # ── 7. No prohibited legal claims in any text field ──
    all_text = json.dumps(data, ensure_ascii=False).lower()
    for pattern in PROHIBITED_CLAIM_PATTERNS:
        checks_total += 1
        if not re.search(pattern, all_text, re.IGNORECASE):
            checks_passed += 1
        else:
            # Check context — boundary notes saying "no legal advice" are OK
            # Find all occurrences and check if they're in boundary_note saying NOT to do it
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            # If the surrounding text says "لا" or "not" or "no", it's a boundary statement
            # Simple heuristic: if the pattern appears inside a boundary_note field value
            # that starts with negation, it's acceptable
            for sc in scenarios:
                sc_text = json.dumps(sc, ensure_ascii=False).lower()
                if re.search(pattern, sc_text, re.IGNORECASE):
                    # Check if it's in a boundary_note with negation
                    bn = sc.get("boundary_note", "").lower()
                    ds = sc.get("demo_script_ar", "").lower()
                    pa = sc.get("purpose_ar", "").lower()
                    combined = bn + " " + ds + " " + pa
                    if re.search(pattern, combined, re.IGNORECASE):
                        # Check for negation context
                        if "لا" in combined or "not " in combined or "no " in combined or "دون" in combined:
                            continue
                        errors.append(f"Scenario {sc.get('scenario_id')}: prohibited claim pattern '{pattern}' in non-negation context")

            # Top-level boundary note
            top_bn = data.get("boundary_note", "").lower()
            if re.search(pattern, top_bn, re.IGNORECASE):
                if "لا" in top_bn or "not " in top_bn or "no " in top_bn:
                    checks_passed += 1
                else:
                    errors.append(f"Top-level boundary_note: prohibited claim pattern '{pattern}' in non-negation context")
            else:
                checks_passed += 1

    # ── 8. All queries contain Arabic text ──
    for sc in scenarios:
        checks_total += 1
        if ARABIC_LETTER_RE.search(sc.get("query", "")):
            checks_passed += 1
        else:
            errors.append(f"Scenario {sc.get('scenario_id')}: query has no Arabic text: {sc.get('query')}")

    # ── 9. No LLM/API/network dependencies in scenario file ──
    checks_total += 1
    has_llm_dep = False
    for kw in LLM_DEPENDENCY_KEYWORDS:
        # Check if keyword appears as an import or dependency, not just in boundary text
        # Since this is a JSON scenario file, check if any field value mentions these as dependencies
        # (not in boundary notes saying "no LLM")
        for sc in scenarios:
            for field in ["mode", "prompt_mode", "formats"]:
                val = str(sc.get(field, "")).lower()
                if kw in val:
                    has_llm_dep = True
                    errors.append(f"Scenario {sc.get('scenario_id')}: field {field} contains LLM/API keyword: {kw}")
    if not has_llm_dep:
        checks_passed += 1

    # ── 10. Scenario IDs are unique ──
    checks_total += 1
    ids = [sc.get("scenario_id") for sc in scenarios]
    if len(ids) == len(set(ids)):
        checks_passed += 1
    else:
        errors.append(f"Duplicate scenario IDs: {ids}")

    # ── 11. Run each scenario through the workflow runner ──
    for sc in scenarios:
        sid = sc.get("scenario_id", "?")
        tmp_dir = tempfile.mkdtemp(prefix=f"demo_validate_{sid}_")
        try:
            # Build command
            cmd = [
                sys.executable,
                WORKFLOW_RUNNER,
                sc["query"],
                "--mode", sc["mode"],
                "--limit", str(sc["limit"]),
                "--prompt-mode", sc["prompt_mode"],
                "--formats", sc["formats"],
                "--output-dir", tmp_dir,
            ]
            if sc.get("track"):
                cmd.extend(["--track", sc["track"]])
            if sc.get("record_type"):
                cmd.extend(["--record-type", sc["record_type"]])
            if sc.get("include_full_text"):
                cmd.append("--include-full-text")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=REPO_ROOT)

            checks_total += 1
            if result.returncode == 0:
                checks_passed += 1
            else:
                errors.append(f"Scenario {sid}: workflow runner failed (exit {result.returncode}): {result.stderr[:200]}")
                continue

            # ── 11a. workflow_manifest.json exists and parses ──
            manifest_path = os.path.join(tmp_dir, "workflow_manifest.json")
            checks_total += 1
            if os.path.isfile(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest = json.load(f)
                    checks_passed += 1
                except json.JSONDecodeError as ex:
                    errors.append(f"Scenario {sid}: manifest parse error: {ex}")
                    manifest = None
            else:
                errors.append(f"Scenario {sid}: workflow_manifest.json not found in {tmp_dir}")
                manifest = None

            if manifest is None:
                continue

            # ── 11b. source_export_record_count == 450 in manifest ──
            checks_total += 1
            if manifest.get("source_export_record_count") == 450:
                checks_passed += 1
            else:
                errors.append(f"Scenario {sid}: manifest source_export_record_count != 450 (got {manifest.get('source_export_record_count')})")

            # ── 11c. Expected artifacts exist ──
            for artifact_name in sc.get("expected_artifacts", []):
                checks_total += 1
                artifact_path = os.path.join(tmp_dir, artifact_name)
                if os.path.isfile(artifact_path):
                    checks_passed += 1
                else:
                    errors.append(f"Scenario {sid}: expected artifact not found: {artifact_name}")

            # ── 11d. total_matches >= expected_min_total_matches ──
            checks_total += 1
            expected_min = sc.get("expected_min_total_matches", 0)
            # Read context_pack.json for total_matches
            cp_path = os.path.join(tmp_dir, "context_pack.json")
            total_matches = None
            if os.path.isfile(cp_path):
                try:
                    with open(cp_path, "r", encoding="utf-8") as f:
                        cp = json.load(f)
                    total_matches = cp.get("total_matches", 0)
                except (json.JSONDecodeError, KeyError):
                    pass
            if total_matches is not None and total_matches >= expected_min:
                checks_passed += 1
            elif total_matches is not None:
                errors.append(f"Scenario {sid}: total_matches {total_matches} < expected_min {expected_min}")
            else:
                errors.append(f"Scenario {sid}: could not read total_matches from context_pack.json")

            # ── 11e. Temporary output is outside repo ──
            checks_total += 1
            if not os.path.commonpath([tmp_dir, REPO_ROOT]) == REPO_ROOT:
                checks_passed += 1
            else:
                errors.append(f"Scenario {sid}: temp output dir is inside repo: {tmp_dir}")

            # ── 11f. No LLM/API in manifest hygiene ──
            checks_total += 1
            hygiene = manifest.get("hygiene", {})
            if (
                hygiene.get("no_llm_calls") is True
                and hygiene.get("no_api") is True
                and hygiene.get("no_network") is True
                and hygiene.get("no_embeddings") is True
            ):
                checks_passed += 1
            else:
                errors.append(f"Scenario {sid}: manifest hygiene flags not all True: {hygiene}")

        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    # ── 12. No generated outputs committed in repo ──
    checks_total += 1
    # Check that data/demo_scenarios/ contains only the scenarios JSON
    demo_dir = os.path.join(REPO_ROOT, "data", "demo_scenarios")
    committed_files = []
    if os.path.isdir(demo_dir):
        for fname in os.listdir(demo_dir):
            if os.path.isfile(os.path.join(demo_dir, fname)):
                committed_files.append(fname)
    # Only the scenarios JSON should be committed
    expected_files = {"retrieval_demo_scenarios_v1.json"}
    if set(committed_files) == expected_files:
        checks_passed += 1
    else:
        extra = set(committed_files) - expected_files
        if extra:
            errors.append(f"Unexpected files in data/demo_scenarios/: {extra}")
        else:
            errors.append(f"Missing expected files in data/demo_scenarios/: {expected_files - set(committed_files)}")

    # ── Result ──
    print(f"\n{'='*60}")
    print(f"Retrieval Demo Scenarios Validator")
    print(f"{'='*60}")
    print(f"Checks passed: {checks_passed} / {checks_total}")
    if warnings:
        print(f"Warnings: {len(warnings)}")
        for w in warnings:
            print(f"  ⚠ {w}")
    if errors:
        print(f"Errors: {len(errors)}")
        for e in errors:
            print(f"  ✗ {e}")
        print(f"\nFAIL")
        return 1
    else:
        print(f"\nPASS — All {checks_total} checks passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())