#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the Official English guidance REFERENCE layer (Book One pilot).

Checks:
- the official English source metadata exists;
- the Book One English reference file exists with exactly 34 records, Articles 1–34,
  no duplicates;
- every record is english_source_status = official_guidance_translation,
  governing_text_language = ar, manual_review_status = needs_manual_check;
- NO English Legal LLM records / directory exist;
- NO forbidden overclaim terms;
- source authority is Bureau of Experts / Official Translation Department.

Exit 0 == pass; 1 == problems. No network, no heavy dependencies.
"""

from __future__ import annotations

import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "english_reference.schema.json")
META = os.path.join(ROOT, "data", "metadata", "official_english_source.json")
BOOK1 = os.path.join(ROOT, "data", "english_reference", "book1_en_reference.json")
EXPECTED = list(range(1, 35))

# Positive overclaim assertions that must NOT appear in the reference data.
BANNED = [
    "binding english text", "governing english text", "english is binding",
    "verified translation", "binding_translation", "unofficial_translation",
]


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _validate_record(rec, schema):
    try:
        import jsonschema
        return [e.message for e in jsonschema.Draft7Validator(schema).iter_errors(rec)]
    except ImportError:
        return ["missing '%s'" % k for k in schema.get("required", []) if k not in rec]


def main() -> int:
    problems = []

    if not os.path.exists(META):
        problems.append("official English source metadata missing: data/metadata/official_english_source.json")
    else:
        m = _read(META)
        auth = str(m.get("source_authority", "")) + " " + str(m.get("department", ""))
        if "Bureau of Experts" not in auth:
            problems.append("metadata.source_authority must mention 'Bureau of Experts'")

    if not os.path.exists(BOOK1):
        print("Book One English reference file missing:", BOOK1)
        return 1

    schema = _read(SCHEMA) if os.path.exists(SCHEMA) else None
    doc = _read(BOOK1)
    records = doc.get("records", [])
    nums = [r.get("article_number") for r in records]

    if len(records) != 34:
        problems.append("expected 34 records, got %d" % len(records))
    if nums != EXPECTED:
        problems.append("article numbers must be exactly 1..34 in order (got %r)" % nums[:40])
    if len(set(nums)) != len(nums):
        problems.append("duplicate article numbers present")

    for r in records:
        rid = r.get("article_number", "?")
        if schema is not None:
            for msg in _validate_record(r, schema):
                problems.append("art %s: %s" % (rid, msg))
        if r.get("english_source_status") != "official_guidance_translation":
            problems.append("art %s: english_source_status must be official_guidance_translation" % rid)
        if r.get("governing_text_language") != "ar":
            problems.append("art %s: governing_text_language must be ar" % rid)
        if r.get("manual_review_status") != "needs_manual_check":
            problems.append("art %s: manual_review_status must be needs_manual_check" % rid)
        if not str(r.get("english_reference_text", "")).strip():
            problems.append("art %s: english_reference_text empty" % rid)
        src = r.get("source", {})
        if "Bureau of Experts" not in str(src.get("source_authority", "")):
            problems.append("art %s: source.source_authority must mention Bureau of Experts" % rid)
        if "Official Translation Department" not in str(src.get("department", "")):
            problems.append("art %s: source.department must be Official Translation Department" % rid)

    # No English LLM layer yet.
    if os.path.isdir(os.path.join(ROOT, "data", "english_legal_llm")):
        problems.append("data/english_legal_llm/ must NOT exist yet")
    stray = glob.glob(os.path.join(ROOT, "data", "**", "*_en_legal_llm.json"), recursive=True)
    if stray:
        problems.append("English LLM record files must not exist yet: %s" % stray)

    # No overclaim wording in the reference data blob.
    blob = open(BOOK1, encoding="utf-8").read().lower()
    for term in BANNED:
        if term in blob:
            problems.append("forbidden overclaim term in data: '%s'" % term)

    print("=" * 60)
    print("Official English REFERENCE layer validation (Book One pilot)")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] 34 records, Articles 1–34; official_guidance_translation; "
          "governing=ar; manual_review_status=needs_manual_check; no English LLM layer")
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
