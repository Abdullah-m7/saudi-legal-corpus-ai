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

# Book Four model-1b Arabic LLM sections — records must mirror their provisions
# exactly (groups + legal_rule_summary_ar), map to no uncovered article, and use
# text_type = internally_reviewed_summary.
B4_SECTIONS = [
    {
        "label": "book4 section2",
        "layer": os.path.join(LAYER_DIR, "book4_section2_ar_legal_llm.json"),
        "provisions": os.path.join(ROOT, "data", "articles", "book4_provisions_067_083.json"),
        "groups": [[67, 68], [71], [72], [75], [77]],
        "uncovered": {69, 70, 73, 74, 76, 78, 79, 80, 81, 82, 83},
    },
    {
        "label": "book4 section3",
        "layer": os.path.join(LAYER_DIR, "book4_section3_ar_legal_llm.json"),
        "provisions": os.path.join(ROOT, "data", "articles", "book4_provisions_084_102.json"),
        "groups": [[85, 87], [92, 93], [99], [101], [102]],
        "uncovered": {84, 86, 88, 89, 90, 91, 94, 95, 96, 97, 98, 100},
    },
    {
        "label": "book4 section4",
        "layer": os.path.join(LAYER_DIR, "book4_section4_ar_legal_llm.json"),
        "provisions": os.path.join(ROOT, "data", "articles", "book4_provisions_103_120.json"),
        "groups": [[108], [113], [115], [117]],
        "uncovered": {103, 104, 105, 106, 107, 109, 110, 111, 112, 114, 116, 118, 119, 120},
    },
]


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

    # -- Book Four model-1b section guardrails (Sections 2 and 3) -------------
    for sec in B4_SECTIONS:
        label = sec["label"]
        if not os.path.exists(sec["layer"]):
            continue  # section layer is optional until its PR lands
        recs = _read(sec["layer"]).get("records", [])
        groups = [r.get("article_numbers") for r in recs]
        if len(recs) != len(sec["groups"]):
            problems.append(f"{label}: expected {len(sec['groups'])} records, got {len(recs)}")
        if groups != sec["groups"]:
            problems.append(f"{label}: article groups must be {sec['groups']} (got {groups})")
        covered = {n for g in groups for n in g}
        if covered & sec["uncovered"]:
            problems.append(f"{label}: records map to uncovered articles {sorted(covered & sec['uncovered'])}")
        for r in recs:
            rid = r.get("record_id", "?")
            if r.get("record_type") != "provision":
                problems.append(f"{label}:{rid}: record_type must be provision")
            if r.get("source_trust", {}).get("text_type") != "internally_reviewed_summary":
                problems.append(f"{label}:{rid}: text_type must be internally_reviewed_summary")
        # legal_rule_summary_ar must EXACTLY match the corresponding provision summary.
        if os.path.exists(sec["provisions"]):
            prov = {tuple(p["source_article_numbers"]): p["arabic_reference_summary"]
                    for p in _read(sec["provisions"]).get("provisions", [])}
            for r in recs:
                key = tuple(r.get("article_numbers", []))
                if prov.get(key) != r.get("legal_rule_summary_ar"):
                    problems.append(f"{label}:{r.get('record_id')}: "
                                    f"legal_rule_summary_ar != provision arabic_reference_summary")
        else:
            problems.append(f"{label}: provisions file {os.path.basename(sec['provisions'])} missing")

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
