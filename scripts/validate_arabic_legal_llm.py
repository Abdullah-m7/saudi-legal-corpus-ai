#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the Arabic Legal LLM-ready layer files against the schema + guardrails.

Uses jsonschema when available; otherwise a minimal required-keys check. Exit 0 ==
all pass; 1 == problems.
"""

from __future__ import annotations

import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYER_DIR = os.path.join(ROOT, "data", "arabic_legal_llm")
SCHEMA = os.path.join(ROOT, "schemas", "arabic_legal_llm.schema.json")
BANNED = ["verified_summary", "verified", "محققة", "经核验"]


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _validate_record(rec, schema):
    try:
        import jsonschema
        return [e.message for e in jsonschema.Draft7Validator(schema).iter_errors(rec)]
    except ImportError:
        return [f"missing '{k}'" for k in schema.get("required", []) if k not in rec]


def main() -> int:
    problems = []
    schema = _read(SCHEMA)
    files = sorted(glob.glob(os.path.join(LAYER_DIR, "*_ar_legal_llm.json")))
    if not files:
        print("no Arabic legal LLM layer files found (nothing to validate)")
        return 0

    for path in files:
        label = os.path.basename(path)
        doc = _read(path)
        with open(path, "r", encoding="utf-8") as fh:
            blob = fh.read()
        for term in BANNED:
            if term in blob:
                problems.append(f"{label}: banned trust term '{term}'")
        for rec in doc.get("records", []):
            rid = rec.get("record_id", "?")
            for msg in _validate_record(rec, schema):
                problems.append(f"{label}:{rid}: {msg}")
            st = rec.get("source_trust", {})
            if st.get("official_text_check") != "needs_check":
                problems.append(f"{label}:{rid}: source_trust.official_text_check must be needs_check")
            # Arabic subject/rule must be present and non-empty.
            if not rec.get("legal_subject_ar", "").strip():
                problems.append(f"{label}:{rid}: legal_subject_ar empty")
            if not rec.get("legal_rule_summary_ar", "").strip():
                problems.append(f"{label}:{rid}: legal_rule_summary_ar empty")

    print("=" * 60)
    print("Arabic Legal LLM-ready layer validation")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print(f"RESULT: {len(problems)} problem(s) found ✗")
        return 1
    n = sum(len(_read(p).get("records", [])) for p in files)
    print(f"[PASS] {len(files)} file(s), {n} record(s)")
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
