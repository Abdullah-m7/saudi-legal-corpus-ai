#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the cleaned PDPL Implementing Regulation Arabic text.

Verifies that the cleaned-text layer is internally consistent, faithful to the
inventory it derives from, and free of the extraction artifacts the cleaner is
meant to remove.  Does not modify any file.  Exit code 0 = PASS, 1 = FAIL.
"""

from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INVENTORY = os.path.join(
    ROOT, "sources", "pdpl", "regulation", "inventory",
    "pdpl_implementing_regulation_arabic_article_inventory.jsonl",
)
RECORDS = os.path.join(
    ROOT, "sources", "pdpl", "regulation", "cleaned",
    "pdpl_implementing_regulation_arabic_cleaned_records.jsonl",
)
SUMMARY = os.path.join(
    ROOT, "sources", "pdpl", "regulation", "cleaned",
    "pdpl_implementing_regulation_arabic_cleaned_summary.json",
)

EXPECTED_COUNT = 38
ARTIFACT_CHARS = set("!%&#\"*+()$'@~^`|{}[]<>§")
COMBINING = re.compile(r"[ً-ْٰ]")

RESIDUE_TOKEN_TUPLES = {
    ("الشخصية", "البيانات", "أصحاب", "لحقوق", "العامة", "الأحكام"),
    ("الشخصية", "البيانات", "إتلاف", "طلب", "ي"),
    ("متحققة", "لمصلحة", "الشخصية", "البيانات", "معالجة", "عشرة"),
    ("والعشرون", "الحادية", "المادة", "العامة", "المصلحة",
     "لأغراض", "الشخصية", "البيانات", "معالجة", "ضوابط"),
    ("الأثر", "تقويم", "والعشرون"),
    ("والثلاثون", "السابعة", "تقديم", "الشكاوى", "و"),
}


def _fail(errors, msg):
    errors.append(msg)


def _denoise_token(t):
    for c in ARTIFACT_CHARS:
        t = t.replace(c, "")
    return t.strip().strip(":：").strip()


def _tok_tuple(s):
    return tuple(t for t in (_denoise_token(x) for x in s.split()) if t)


def main():
    errors = []

    for path in (INVENTORY, RECORDS, SUMMARY):
        if not os.path.isfile(path):
            print("FAIL: missing file: %s" % os.path.relpath(path, ROOT))
            return 1

    inv = {}
    for line in open(INVENTORY, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            inv[r["article_number"]] = r

    records = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]

    # [1] count
    if len(records) != EXPECTED_COUNT:
        _fail(errors, "[1] expected %d records, found %d" % (EXPECTED_COUNT, len(records)))

    # [2] sequence + keys
    nums = [r["article_number"] for r in records]
    if nums != list(range(1, EXPECTED_COUNT + 1)):
        _fail(errors, "[2] article_number sequence is not 1..%d: %s" % (EXPECTED_COUNT, nums))
    for r in records:
        expected_key = "pdpl_reg_art_%03d" % r["article_number"]
        if r.get("article_key") != expected_key:
            _fail(errors, "[2] art %s: article_key %r != %r"
                  % (r["article_number"], r.get("article_key"), expected_key))

    required = [
        "law_key", "law_component", "language", "record_layer", "article_number",
        "article_key", "arabic_heading", "article_text_cleaned",
        "article_text_source_field", "source_inventory_file", "source_pdf_sha256",
        "cleaning_operations", "text_cleaning_status", "official_text_status",
        "governing_source_note", "english_used_for_correction",
        "translation_performed", "legal_interpretation_performed",
    ]

    for r in records:
        n = r["article_number"]

        # [3] required fields
        for k in required:
            if k not in r:
                _fail(errors, "[3] art %s: missing field %r" % (n, k))

        # [4] heading matches inventory (verified source of the clean title)
        if n in inv and r.get("arabic_heading") != inv[n]["arabic_heading"]:
            _fail(errors, "[4] art %s: arabic_heading differs from inventory" % n)

        text = r.get("article_text_cleaned", "")

        # [5] non-empty body
        if not text.strip():
            _fail(errors, "[5] art %s: article_text_cleaned is empty" % n)

        # [6] no residual artifact characters
        present = sorted(ARTIFACT_CHARS & set(text))
        if present:
            _fail(errors, "[6] art %s: residual artifact chars %r" % (n, present))

        # [7] no standalone running-header line, no line-initial combining marks
        for ln in text.split("\n"):
            if ln.strip() == "عام":
                _fail(errors, "[7] art %s: residual 'عام' header line" % n)
            if ln and COMBINING.match(ln):
                _fail(errors, "[7] art %s: line-initial combining mark: %r" % (n, ln[:20]))

        # [8] no reversed-title residue
        for ln in text.split("\n"):
            if _tok_tuple(ln) in RESIDUE_TOKEN_TUPLES:
                _fail(errors, "[8] art %s: reversed-title residue line present: %r" % (n, ln))

        # [9] honest boundaries
        if r.get("official_text_status") != "EXTRACTED_TEXT_NOT_VERIFIED_OFFICIAL_TEXT":
            _fail(errors, "[9] art %s: unexpected official_text_status %r"
                  % (n, r.get("official_text_status")))
        if r.get("text_cleaning_status") != "STRUCTURAL_EXTRACTION_ARTIFACTS_REMOVED":
            _fail(errors, "[9] art %s: unexpected text_cleaning_status %r"
                  % (n, r.get("text_cleaning_status")))
        for flag in ("translation_performed", "legal_interpretation_performed",
                     "english_used_for_correction"):
            if r.get(flag) is not False:
                _fail(errors, "[9] art %s: boundary flag %s must be False" % (n, flag))

    # [10] summary consistency
    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != len(records):
        _fail(errors, "[10] summary record_count %r != %d"
              % (summary.get("record_count"), len(records)))
    if summary.get("official_text_status") != "EXTRACTED_TEXT_NOT_VERIFIED_OFFICIAL_TEXT":
        _fail(errors, "[10] summary official_text_status not honest NOT_VERIFIED value")

    if errors:
        print("FAIL: %d error(s) in cleaned PDPL implementing regulation text:" % len(errors))
        for e in errors:
            print("  - %s" % e)
        return 1

    print("PASS: %d cleaned PDPL implementing regulation articles" % len(records))
    print("  - sequence 1..%d, keys pdpl_reg_art_001..%03d" % (EXPECTED_COUNT, EXPECTED_COUNT))
    print("  - headings match inventory; no artifact chars, headers, or reversed-title residue")
    print("  - Arabic governs; not a certified official transcription (NOT_VERIFIED)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
