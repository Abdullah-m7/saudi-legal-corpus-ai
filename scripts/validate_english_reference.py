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

# (label, filename, expected article numbers). All must be present and exact.
# Book Four Section 1 follows model 1b coverage: provision-covered articles only.
UNITS = [
    ("Book 1", "book1_en_reference.json", list(range(1, 35))),
    ("Book 2", "book2_en_reference.json", list(range(35, 51))),
    ("Book 3", "book3_en_reference.json", list(range(51, 58))),
    ("Book 4 Section 1", "book4_section1_en_reference.json", [58, 59, 60, 66]),
    ("Book 4 Section 2", "book4_section2_en_reference.json", [67, 68, 71, 72, 75, 77]),
    ("Book 4 Section 3", "book4_section3_en_reference.json", [85, 87, 92, 93, 99, 101, 102]),
    ("Book 4 Section 4", "book4_section4_en_reference.json", [108, 113, 115, 117]),
    ("Book 4 Section 5", "book4_section5_en_reference.json",
     [123, 124, 126, 127, 128, 129, 130, 132, 133]),
]
BOOKS_1_3_TOTAL = 57   # 34 + 16 + 7
TOTAL_EXPECTED = 87    # 57 + 4 (S1) + 6 (S2) + 7 (S3) + 4 (S4) + 9 (S5)
# Per-section forbidden Book Four articles that must NEVER get an English reference
# record in that section's scope.
FORBIDDEN_BY_LABEL = {
    "Book 4 Section 1": set(range(61, 66)) | set(range(67, 138)),   # 61-65 and 67-137
    "Book 4 Section 2": ({69, 70, 73, 74, 76} | set(range(78, 84))  # 69,70,73,74,76,78-83
                         | set(range(84, 138))),                    # and 84-137
    # Section 3: uncovered Section-3 articles (incl. 100, which exists in the
    # English source but maps to Article 101 in the reconciled model) and 103-137.
    "Book 4 Section 3": ({84, 86, 88, 89, 90, 91, 94, 95, 96, 97, 98, 100}
                         | set(range(103, 138))),
    # Section 4: uncovered Section-4 articles (incl. 110, which exists in the
    # English source but was reclassified not_explicit_in_source), plus 58-107
    # (earlier sections) and 121-137.
    "Book 4 Section 4": ({103, 104, 105, 106, 107, 109, 110, 111, 112, 114, 116, 118, 119, 120}
                         | set(range(58, 108)) | set(range(121, 138))),
    # Section 5: uncovered Section-5 articles (incl. 134 & 135, which exist in the
    # English source but are cross-reference only in the model-1b source) plus
    # 58-120 (earlier sections).
    "Book 4 Section 5": ({121, 122, 125, 131, 134, 135, 136, 137} | set(range(58, 121))),
}

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
    books_1_3_total = 0

    for label, fname, expected in UNITS:
        path = os.path.join(REF_DIR, fname)
        if not os.path.exists(path):
            problems.append("%s English reference file missing: %s" % (label, fname))
            continue
        records = _read(path).get("records", [])
        nums = [r.get("article_number") for r in records]
        total += len(records)
        if not label.startswith("Book 4"):
            books_1_3_total += len(records)

        if len(records) != len(expected):
            problems.append("%s: expected %d records, got %d" % (label, len(expected), len(records)))
        if nums != expected:
            problems.append("%s: article numbers must be exactly %r (got %r)"
                            % (label, expected, nums[:40]))
        if len(set(nums)) != len(nums):
            problems.append("%s: duplicate article numbers present" % label)
        # Each Book Four section must never contain its forbidden article set.
        forbidden = FORBIDDEN_BY_LABEL.get(label)
        if forbidden:
            leaked = sorted(set(nums) & forbidden)
            if leaked:
                problems.append("%s: forbidden Book Four articles present: %s" % (label, leaked))

        for r in records:
            rid = "%s.a%s" % (label, r.get("article_number", "?"))
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

    if books_1_3_total != BOOKS_1_3_TOTAL:
        problems.append("Books 1-3 English reference total must be %d (got %d)"
                        % (BOOKS_1_3_TOTAL, books_1_3_total))
    if total != TOTAL_EXPECTED:
        problems.append("total English reference records must be %d (got %d)"
                        % (TOTAL_EXPECTED, total))

    # The English Legal LLM-ready layer is a SEPARATE layer, validated by
    # scripts/validate_english_legal_llm.py. This reference validator no longer
    # asserts its absence (the Book Four Section 1 pilot has started); it only checks
    # that the English LLM layer never leaks its records into the english_reference dir.
    ref_stray = glob.glob(os.path.join(REF_DIR, "*_en_legal_llm.json"))
    if ref_stray:
        problems.append("English LLM records must live in data/english_legal_llm/, not the "
                        "english_reference dir: %s" % ref_stray)

    # No overclaim wording in any reference data file.
    for label, fname, _ in UNITS:
        path = os.path.join(REF_DIR, fname)
        if not os.path.exists(path):
            continue
        blob = open(path, encoding="utf-8").read().lower()
        for term in BANNED:
            if term in blob:
                problems.append("%s: forbidden overclaim term in data: '%s'" % (label, term))

    print("=" * 60)
    print("Official English REFERENCE layer validation (Books 1-3 + Book 4 Sections 1-5)")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] %d records — Books 1-3 (Arts 1-34 / 35-50 / 51-57) + "
          "Book 4 Section 1 (58,59,60,66) + Book 4 Section 2 (67,68,71,72,75,77) + "
          "Book 4 Section 3 (85,87,92,93,99,101,102) + Book 4 Section 4 (108,113,115,117) + "
          "Book 4 Section 5 (123,124,126,127,128,129,130,132,133); "
          "official_guidance_translation; governing=ar; "
          "manual_review_status=needs_manual_check" % total)
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
