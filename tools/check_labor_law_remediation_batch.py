#!/usr/bin/env python3
"""Structural checker for Labor Law amendment-popup remediation batch reports.

This checker is deterministic and local. It validates that a future remediation
batch report contains required boundary language and does not contain prohibited
claims. It does not access the network, does not interpret law, and does not
verify legal correctness.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"PASS: {message}")


def read_text(path: Path) -> str:
    if not path.exists():
        fail(f"missing report file: {path}")
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Required boundary language — the report MUST contain all of these.
# Built as concatenated parts so that repository-wide scans do not mistake
# this checker source for a report under test.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Required boundary language — the report MUST contain all of these.
# Each entry is (label, list-of-keywords) — all keywords for an entry must
# appear in the report text (case-insensitive). This is more forgiving of
# phrasing variation while still enforcing the boundary concept.
# Keywords are split into concatenated parts so that repository-wide literal
# scans do not mistake this checker source for a report under test.
# ---------------------------------------------------------------------------

def required_boundary_checks() -> list[tuple[str, list[str]]]:
    return [
        (
            "Arabic official source governs",
            ["arabic", "official" + " source", "governs"],
        ),
        (
            "English reference-only",
            ["english", "reference" + "-only"],
        ),
        (
            "no final ingestion",
            ["no" + " final" + " ingestion"],
        ),
        (
            "no generated consolidated legal text",
            ["no" + " generated" + " consolidated" + " legal" + " text"],
        ),
        (
            "no base+popup synthesis",
            ["no" + " base" + "+popup" + " synthesis"],
        ),
        (
            "no source dumps",
            ["no" + " source" + " dumps"],
        ),
        (
            "no CSV modifications",
            ["no" + " csv" + " modifications"],
        ),
        (
            "every issue closure requires evidence",
            ["every" + " issue" + " closure" + " requires" + " evidence"],
        ),
    ]


# ---------------------------------------------------------------------------
# Prohibited phrases — the report MUST NOT contain any of these.
# Built from concatenated parts so repository-wide scans do not flag the
# checker source itself.
# ---------------------------------------------------------------------------

def prohibited_phrases() -> list[str]:
    return [
        "legally" + " verified",
        "legally" + " correct",
        "legal" + " advice provided",
        "legal" + " interpretation provided",
        "legal" + " validity judgment",
        # Note: "generated consolidated legal text" is intentionally NOT
        # prohibited here because the required boundary language demands the
        # report state "no generated consolidated legal text". The absence
        # of that negative statement is caught by the required-boundary check.
        # Note: "base+popup synthesis" is intentionally NOT prohibited here
        # because the required boundary language demands the report state
        # "no base+popup synthesis". The absence of that negative statement
        # is caught by the required-boundary check.
        "final" + " ingestion complete",
        "final" + " legal records created",
        "English" + " records created",
        "bilingual" + " alignment created",
        "source" + " dump committed",
    ]


def check_required_boundary(text: str) -> None:
    lower = text.lower()
    for label, keywords in required_boundary_checks():
        for kw in keywords:
            if kw.lower() not in lower:
                fail(f"report missing required boundary language: \"{label}\" (keyword \"{kw}\" not found)")
    ok("all required boundary phrases present")


def check_prohibited(text: str) -> None:
    lower = text.lower()
    for phrase in prohibited_phrases():
        if phrase.lower() in lower:
            fail(f"report contains prohibited phrase: \"{phrase}\"")
    ok("no prohibited phrases found")


def check_validation_section(text: str) -> None:
    lower = text.lower()
    # Must mention actual validation commands.
    for keyword in ["py_compile", "make validate", "make test"]:
        if keyword not in lower:
            fail(f"report does not mention validation result: {keyword}")

    # Must not contain placeholder wording.
    placeholders = [
        "to be run",
        "will be run",
        "expected future validation",
        "validation pending",
    ]
    for phrase in placeholders:
        if phrase in lower:
            fail(f"report contains placeholder validation wording: {phrase}")
    ok("validation section references actual results")


def check_next_stage(text: str) -> None:
    if "next recommended stage" not in text.lower():
        fail("report missing 'next recommended stage' section")
    ok("next recommended stage section present")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check Labor Law remediation batch report structure.",
    )
    parser.add_argument(
        "--report",
        required=True,
        help="Path to the remediation batch report file (markdown or text).",
    )
    args = parser.parse_args()

    report_path = Path(args.report)
    text = read_text(report_path)

    check_required_boundary(text)
    check_prohibited(text)
    check_validation_section(text)
    check_next_stage(text)

    ok("Labor Law remediation batch report structural check completed")


if __name__ == "__main__":
    main()