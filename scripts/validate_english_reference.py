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
REF_DIR = os.path.join(ROOT, "data", "english_reference")

# Book -> (filename, expected article numbers). All must be present and exact.
BOOKS = {
    1: ("book1_en_reference.json", list(range(1, 35))),
    2: ("book2_en_reference.json", list(range(35, 51))),
    3: ("book3_en_reference.json", list(range(51, 58))),
}
TOTAL_EXPECTED = 57  # 34 + 16 + 7 across Books 1-3

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

    schema = _read(SCHEMA) if os.path.exists(SCHEMA) else None
    total = 0

    for book, (fname, expected) in sorted(BOOKS.items()):
        path = os.path.join(REF_DIR, fname)
        if not os.path.exists(path):
            problems.append("Book %d English reference file missing: %s" % (book, fname))
            continue
        records = _read(path).get("records", [])
        nums = [r.get("article_number") for r in records]
        total += len(records)

        if len(records) != len(expected):
            problems.append("book %d: expected %d records, got %d" % (book, len(expected), len(records)))
        if nums != expected:
            problems.append("book %d: article numbers must be exactly %d..%d in order (got %r)"
                            % (book, expected[0], expected[-1], nums[:40]))
        if len(set(nums)) != len(nums):
            problems.append("book %d: duplicate article numbers present" % book)

        for r in records:
            rid = "b%s.a%s" % (book, r.get("article_number", "?"))
            if schema is not None:
                for msg in _validate_record(r, schema):
                    problems.append("%s: %s" % (rid, msg))
            if r.get("english_source_status") != "official_guidance_translation":
                problems.append("%s: english_source_status must be official_guidance_translation" % rid)
            if r.get("governing_text_language") != "ar":
                problems.append("%s: governing_text_language must be ar" % rid)
            if r.get("manual_review_status") != "needs_manual_check":
                problems.append("%s: manual_review_status must be needs_manual_check" % rid)
            if not str(r.get("english_reference_text", "")).strip():
                problems.append("%s: english_reference_text empty" % rid)
            src = r.get("source", {})
            if "Bureau of Experts" not in str(src.get("source_authority", "")):
                problems.append("%s: source.source_authority must mention Bureau of Experts" % rid)
            if "Official Translation Department" not in str(src.get("department", "")):
                problems.append("%s: source.department must be Official Translation Department" % rid)

    if total != TOTAL_EXPECTED:
        problems.append("total English reference records across Books 1-3 must be %d (got %d)"
                        % (TOTAL_EXPECTED, total))

    # No English LLM layer yet.
    if os.path.isdir(os.path.join(ROOT, "data", "english_legal_llm")):
        problems.append("data/english_legal_llm/ must NOT exist yet")
    stray = glob.glob(os.path.join(ROOT, "data", "**", "*_en_legal_llm.json"), recursive=True)
    if stray:
        problems.append("English LLM record files must not exist yet: %s" % stray)

    # No overclaim wording in any reference data file.
    for book, (fname, _) in sorted(BOOKS.items()):
        path = os.path.join(REF_DIR, fname)
        if not os.path.exists(path):
            continue
        blob = open(path, encoding="utf-8").read().lower()
        for term in BANNED:
            if term in blob:
                problems.append("book %d: forbidden overclaim term in data: '%s'" % (book, term))

    print("=" * 60)
    print("Official English REFERENCE layer validation (Books 1-3)")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] %d records across Books 1-3 (Arts 1-34 / 35-50 / 51-57); "
          "official_guidance_translation; governing=ar; "
          "manual_review_status=needs_manual_check; no English LLM layer" % total)
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
