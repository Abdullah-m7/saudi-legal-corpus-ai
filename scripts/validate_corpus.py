#!/usr/bin/env python3
"""Validate the Book One corpus (schema + legal-translation QA rules).

Exit code 0 == all checks pass; 1 == one or more failures. Prints a numbered
report matching the QA checklist in the project brief.
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from saudi_law_corpus.validate import validate_all  # noqa: E402


def main() -> int:
    ok, report = validate_all()
    print("=" * 60)
    print("Saudi Companies Law — Book One corpus validation")
    print("=" * 60)
    failures = 0
    for section, problems in report.items():
        status = "PASS" if not problems else "FAIL"
        print(f"[{status}] {section}")
        for p in problems:
            failures += 1
            print(f"        - {p}")
    print("-" * 60)
    if ok:
        print("RESULT: ALL CHECKS PASSED ✓")
        return 0
    print(f"RESULT: {failures} problem(s) found ✗")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
