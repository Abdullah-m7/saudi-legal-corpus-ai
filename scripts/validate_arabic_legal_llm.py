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

# Book Four Section 2 — model-1b Arabic LLM records must mirror the provisions.
B4S2_LAYER = os.path.join(LAYER_DIR, "book4_section2_ar_legal_llm.json")
B4S2_PROVISIONS = os.path.join(ROOT, "data", "articles", "book4_provisions_067_083.json")
B4S2_GROUPS = [[67, 68], [71], [72], [75], [77]]
B4S2_UNCOVERED = {69, 70, 73, 74, 76, 78, 79, 80, 81, 82, 83}


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

    # -- Book Four Section 2 specific guardrails ------------------------------
    if os.path.exists(B4S2_LAYER):
        s2 = _read(B4S2_LAYER).get("records", [])
        groups = [r.get("article_numbers") for r in s2]
        if len(s2) != 5:
            problems.append(f"book4 section2: expected 5 records, got {len(s2)}")
        if groups != B4S2_GROUPS:
            problems.append(f"book4 section2: article groups must be {B4S2_GROUPS} (got {groups})")
        covered = {n for g in groups for n in g}
        if covered & B4S2_UNCOVERED:
            problems.append(f"book4 section2: records map to uncovered articles {sorted(covered & B4S2_UNCOVERED)}")
        for r in s2:
            rid = r.get("record_id", "?")
            if r.get("record_type") != "provision":
                problems.append(f"book4 section2:{rid}: record_type must be provision")
            if r.get("source_trust", {}).get("text_type") != "internally_reviewed_summary":
                problems.append(f"book4 section2:{rid}: text_type must be internally_reviewed_summary")
        # legal_rule_summary_ar must EXACTLY match the corresponding provision summary.
        if os.path.exists(B4S2_PROVISIONS):
            prov = {tuple(p["source_article_numbers"]): p["arabic_reference_summary"]
                    for p in _read(B4S2_PROVISIONS).get("provisions", [])}
            for r in s2:
                key = tuple(r.get("article_numbers", []))
                if prov.get(key) != r.get("legal_rule_summary_ar"):
                    problems.append(f"book4 section2:{r.get('record_id')}: "
                                    f"legal_rule_summary_ar != provision arabic_reference_summary")
        else:
            problems.append("book4 section2: provisions file book4_provisions_067_083.json missing")

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
