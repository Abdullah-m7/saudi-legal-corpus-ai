#!/usr/bin/env python3
"""
Retrieval Demo Scenarios Runner

Runs all curated demo scenarios through the existing workflow runner
into a user-provided or temporary output directory.

Each scenario gets its own subdirectory named after its scenario_id.

This is NOT RAG.
This does NOT call an LLM.
This does NOT generate legal answers.
This does NOT provide legal advice.
Generated outputs are NOT committed.

Usage:
  python3 scripts/run_retrieval_demo_scenarios.py
  python3 scripts/run_retrieval_demo_scenarios.py --output-dir /tmp/my_demo
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENARIOS_PATH = os.path.join(REPO_ROOT, "data", "demo_scenarios", "retrieval_demo_scenarios_v1.json")
WORKFLOW_RUNNER = os.path.join(REPO_ROOT, "scripts", "run_retrieval_workflow.py")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run all retrieval demo scenarios through the workflow runner."
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory (default: temporary directory)",
    )
    args = parser.parse_args()

    # Load scenarios
    with open(SCENARIOS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    scenarios = data["scenarios"]

    # Determine output directory
    if args.output_dir:
        output_dir = os.path.abspath(args.output_dir)
        os.makedirs(output_dir, exist_ok=True)
        is_temp = False
    else:
        output_dir = tempfile.mkdtemp(prefix="corpus_demo_scenarios_")
        is_temp = True

    print(f"Demo scenarios output: {output_dir}")
    print(f"Scenarios: {len(scenarios)}")
    print()

    results = []
    for sc in scenarios:
        sid = sc["scenario_id"]
        sc_dir = os.path.join(output_dir, sid)
        os.makedirs(sc_dir, exist_ok=True)

        cmd = [
            sys.executable,
            WORKFLOW_RUNNER,
            sc["query"],
            "--mode", sc["mode"],
            "--limit", str(sc["limit"]),
            "--prompt-mode", sc["prompt_mode"],
            "--formats", sc["formats"],
            "--output-dir", sc_dir,
        ]
        if sc.get("track"):
            cmd.extend(["--track", sc["track"]])
        if sc.get("record_type"):
            cmd.extend(["--record-type", sc["record_type"]])
        if sc.get("include_full_text"):
            cmd.append("--include-full-text")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=REPO_ROOT)
        status = "PASS" if result.returncode == 0 else "FAIL"
        results.append((sid, sc["title_ar"], status))
        print(f"  [{status}] {sid}: {sc['title_ar']}")

    print()
    passed = sum(1 for _, _, s in results if s == "PASS")
    failed = sum(1 for _, _, s in results if s == "FAIL")
    print(f"Results: {passed} passed, {failed} failed, {len(results)} total")

    if is_temp:
        print(f"\nTemporary output directory: {output_dir}")
        print("Remove it manually after inspection if desired.")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())