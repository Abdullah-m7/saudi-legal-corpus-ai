#!/usr/bin/env python3
"""
Validator for PDPL Arabic Law Next-Layer Records.

Standalone Python script. No network calls. No heavy dependencies.
Uses only the Python standard library (json, sys, os, re).

Checks:
  1.  Schema file exists and parses as JSON.
  2.  Records JSONL file exists.
  3.  Summary file exists.
  4.  QA findings file exists.
  5.  Records file has exactly 43 non-empty JSON lines.
  6.  Every record is valid JSON.
  7.  Every record satisfies the schema constraints (manual checks).
  8.  article_number sequence is exactly 1 through 43.
  9.  article_key sequence is exactly pdpl_law_art_001 through pdpl_law_art_043.
  10. No duplicate article_number.
  11. No duplicate article_key.
  12. page_start and page_end are integers and satisfy 1 <= page_start <= page_end <= 16.
  13. article_text is non-empty.
  14. Article 32 has article_number=32, article_key=pdpl_law_art_032,
      article_text="ملغاة.", ready_for_next_layer=true.
  15. All records have required field values.
  16. Summary consistency.
  17. QA findings consistency.
  18. Boundary guard (no official verified text, no English correction, no translation, no legal interpretation).
  19. Mutation guard (read-only — does not modify any file).

Exit 0 on pass, 1 on failure.
"""

import json
import sys
import os
import re

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

SCHEMA_PATH = os.path.join(REPO_ROOT, "schemas", "pdpl_arabic_law_next_layer_record.schema.json")
RECORDS_PATH = os.path.join(REPO_ROOT, "sources", "pdpl", "next_layer", "pdpl_arabic_law_next_layer_records.jsonl")
SUMMARY_PATH = os.path.join(REPO_ROOT, "sources", "pdpl", "next_layer", "pdpl_arabic_law_next_layer_summary.json")
QA_PATH = os.path.join(REPO_ROOT, "sources", "pdpl", "next_layer", "qa", "pdpl_arabic_law_next_layer_qa_findings.json")

EXPECTED_RECORD_COUNT = 43
EXPECTED_SHA256 = "0bb6d1eb6a85450af4d4eb74b9e87bd2c8f62abab0eb0474087ffcbdf5e2292c"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

failures = []
checks_passed = 0


def check(condition, message):
    """Record a check result."""
    global checks_passed
    if condition:
        checks_passed += 1
    else:
        failures.append(message)


def load_json_file(path):
    """Load a JSON file, return None on error."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def validate_record_against_schema(record):
    """
    Manually validate a record against the schema constraints.
    Returns list of error messages (empty if valid).
    """
    errors = []

    # Required fields
    required_fields = [
        "law_key", "law_component", "language", "record_layer",
        "article_number", "article_key", "arabic_heading", "article_text",
        "article_text_source_field", "source_inventory_file", "source_summary_file",
        "source_ocr_artifact", "source_pdf_sha256", "source_status",
        "official_text_status", "governing_source_note", "page_start", "page_end",
        "ocr_review_flags", "english_used_for_correction", "translation_performed",
        "legal_interpretation_performed", "ready_for_next_layer",
    ]

    for field in required_fields:
        if field not in record:
            errors.append(f"Missing required field: {field}")

    # additionalProperties: false — no extra fields
    allowed_keys = set(required_fields)
    for key in record:
        if key not in allowed_keys:
            errors.append(f"Additional property not allowed: {key}")

    # Type / value checks
    if record.get("law_key") != "pdpl":
        errors.append(f"law_key must be 'pdpl', got: {record.get('law_key')}")

    if record.get("law_component") != "law":
        errors.append(f"law_component must be 'law', got: {record.get('law_component')}")

    if record.get("language") != "ar":
        errors.append(f"language must be 'ar', got: {record.get('language')}")

    if record.get("record_layer") != "PDPL_ARABIC_LAW_NEXT_LAYER_PREP":
        errors.append(f"record_layer must be 'PDPL_ARABIC_LAW_NEXT_LAYER_PREP', got: {record.get('record_layer')}")

    # article_number: integer 1..43
    an = record.get("article_number")
    if not isinstance(an, int) or isinstance(an, bool):
        errors.append(f"article_number must be integer, got: {type(an).__name__}")
    elif an < 1 or an > 43:
        errors.append(f"article_number must be 1..43, got: {an}")

    # article_key: pattern ^pdpl_law_art_[0-9]{3}$
    ak = record.get("article_key")
    if not isinstance(ak, str):
        errors.append(f"article_key must be string, got: {type(ak).__name__}")
    elif not re.match(r"^pdpl_law_art_[0-9]{3}$", ak):
        errors.append(f"article_key must match ^pdpl_law_art_[0-9]{3}$, got: {ak}")

    # arabic_heading: non-empty string
    ah = record.get("arabic_heading")
    if not isinstance(ah, str) or len(ah) < 1:
        errors.append(f"arabic_heading must be non-empty string")

    # article_text: non-empty string
    at = record.get("article_text")
    if not isinstance(at, str) or len(at) < 1:
        errors.append(f"article_text must be non-empty string")

    # article_text_source_field
    if record.get("article_text_source_field") != "article_text_ocr":
        errors.append(f"article_text_source_field must be 'article_text_ocr'")

    # source_inventory_file
    if record.get("source_inventory_file") != "sources/pdpl/inventory/pdpl_arabic_law_article_inventory.jsonl":
        errors.append(f"source_inventory_file mismatch")

    # source_summary_file
    if record.get("source_summary_file") != "sources/pdpl/inventory/pdpl_arabic_law_article_inventory_summary.json":
        errors.append(f"source_summary_file mismatch")

    # source_ocr_artifact
    if record.get("source_ocr_artifact") != "sources/pdpl/ocr/pdpl_arabic_law_ocr.txt":
        errors.append(f"source_ocr_artifact mismatch")

    # source_pdf_sha256
    sha = record.get("source_pdf_sha256")
    if not isinstance(sha, str):
        errors.append(f"source_pdf_sha256 must be string")
    elif not re.match(r"^[0-9a-f]{64}$", sha):
        errors.append(f"source_pdf_sha256 must match ^[0-9a-f]{64}$")
    elif sha != EXPECTED_SHA256:
        errors.append(f"source_pdf_sha256 must equal expected hash")

    # source_status
    if record.get("source_status") != "REVIEWED_OCR_INVENTORY_READY_FOR_NEXT_LAYER":
        errors.append(f"source_status must be REVIEWED_OCR_INVENTORY_READY_FOR_NEXT_LAYER")

    # official_text_status
    if record.get("official_text_status") != "REVIEWED_OCR_NOT_VERIFIED_OFFICIAL_TEXT":
        errors.append(f"official_text_status must be REVIEWED_OCR_NOT_VERIFIED_OFFICIAL_TEXT")

    # governing_source_note: non-empty string
    gsn = record.get("governing_source_note")
    if not isinstance(gsn, str) or len(gsn) < 1:
        errors.append(f"governing_source_note must be non-empty string")

    # page_start: integer 1..16
    ps = record.get("page_start")
    if not isinstance(ps, int) or isinstance(ps, bool):
        errors.append(f"page_start must be integer, got: {type(ps).__name__}")
    elif ps < 1 or ps > 16:
        errors.append(f"page_start must be 1..16, got: {ps}")

    # page_end: integer 1..16
    pe = record.get("page_end")
    if not isinstance(pe, int) or isinstance(pe, bool):
        errors.append(f"page_end must be integer, got: {type(pe).__name__}")
    elif pe < 1 or pe > 16:
        errors.append(f"page_end must be 1..16, got: {pe}")

    # page_start <= page_end
    if isinstance(ps, int) and isinstance(pe, int) and not isinstance(ps, bool) and not isinstance(pe, bool):
        if ps > pe:
            errors.append(f"page_start ({ps}) > page_end ({pe})")

    # ocr_review_flags: array of strings
    orf = record.get("ocr_review_flags")
    if not isinstance(orf, list):
        errors.append(f"ocr_review_flags must be array")
    else:
        for flag in orf:
            if not isinstance(flag, str):
                errors.append(f"ocr_review_flags items must be strings")
                break

    # english_used_for_correction: false
    if record.get("english_used_for_correction") is not False:
        errors.append(f"english_used_for_correction must be false")

    # translation_performed: false
    if record.get("translation_performed") is not False:
        errors.append(f"translation_performed must be false")

    # legal_interpretation_performed: false
    if record.get("legal_interpretation_performed") is not False:
        errors.append(f"legal_interpretation_performed must be false")

    # ready_for_next_layer: true
    if record.get("ready_for_next_layer") is not True:
        errors.append(f"ready_for_next_layer must be true")

    return errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("PDPL Arabic Law Next-Layer Records Validator")
    print("=" * 70)

    # 1. Schema file exists and parses as JSON
    check(os.path.isfile(SCHEMA_PATH), "Check 1 FAIL: Schema file does not exist")
    schema = None
    if os.path.isfile(SCHEMA_PATH):
        schema = load_json_file(SCHEMA_PATH)
        check(schema is not None, "Check 1 FAIL: Schema file does not parse as JSON")
    print(f"[1] Schema file exists and parses: {'PASS' if schema is not None else 'FAIL'}")

    # 2. Records JSONL file exists
    check(os.path.isfile(RECORDS_PATH), "Check 2 FAIL: Records JSONL file does not exist")
    print(f"[2] Records JSONL file exists: {'PASS' if os.path.isfile(RECORDS_PATH) else 'FAIL'}")

    # 3. Summary file exists
    check(os.path.isfile(SUMMARY_PATH), "Check 3 FAIL: Summary file does not exist")
    print(f"[3] Summary file exists: {'PASS' if os.path.isfile(SUMMARY_PATH) else 'FAIL'}")

    # 4. QA findings file exists
    check(os.path.isfile(QA_PATH), "Check 4 FAIL: QA findings file does not exist")
    print(f"[4] QA findings file exists: {'PASS' if os.path.isfile(QA_PATH) else 'FAIL'}")

    # Load records
    records = []
    if os.path.isfile(RECORDS_PATH):
        with open(RECORDS_PATH, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                stripped = line.strip()
                if stripped:
                    records.append((i, stripped))

    # 5. Records file has exactly 43 non-empty JSON lines
    check(len(records) == EXPECTED_RECORD_COUNT,
          f"Check 5 FAIL: Expected {EXPECTED_RECORD_COUNT} records, got {len(records)}")
    print(f"[5] Record count = {len(records)} (expected {EXPECTED_RECORD_COUNT}): "
          f"{'PASS' if len(records) == EXPECTED_RECORD_COUNT else 'FAIL'}")

    # 6. Every record is valid JSON
    parsed_records = []
    json_ok = True
    for lineno, raw in records:
        try:
            parsed_records.append(json.loads(raw))
        except json.JSONDecodeError as e:
            failures.append(f"Check 6 FAIL: Line {lineno} is not valid JSON: {e}")
            json_ok = False
    check(json_ok, "Check 6 FAIL: Some records are not valid JSON")
    print(f"[6] All records valid JSON: {'PASS' if json_ok else 'FAIL'}")

    # 7. Every record satisfies schema constraints
    schema_ok = True
    for idx, rec in enumerate(parsed_records):
        errors = validate_record_against_schema(rec)
        if errors:
            schema_ok = False
            for err in errors:
                failures.append(f"Check 7 FAIL: Record {idx + 1}: {err}")
    check(schema_ok, "Check 7 FAIL: Some records do not satisfy schema constraints")
    print(f"[7] Schema constraints satisfied: {'PASS' if schema_ok else 'FAIL'}")

    # 8. article_number sequence is exactly 1 through 43
    article_numbers = [r.get("article_number") for r in parsed_records]
    expected_sequence = list(range(1, EXPECTED_RECORD_COUNT + 1))
    seq_ok = sorted(article_numbers) == expected_sequence
    check(seq_ok, "Check 8 FAIL: article_number sequence is not 1..43")
    print(f"[8] article_number sequence 1..43: {'PASS' if seq_ok else 'FAIL'}")

    # 9. article_key sequence is exactly pdpl_law_art_001 through pdpl_law_art_043
    article_keys = [r.get("article_key") for r in parsed_records]
    expected_keys = [f"pdpl_law_art_{i:03d}" for i in range(1, EXPECTED_RECORD_COUNT + 1)]
    keys_seq_ok = sorted(article_keys) == expected_keys
    check(keys_seq_ok, "Check 9 FAIL: article_key sequence is not pdpl_law_art_001..043")
    print(f"[9] article_key sequence pdpl_law_art_001..043: {'PASS' if keys_seq_ok else 'FAIL'}")

    # 10. No duplicate article_number
    seen_numbers = set()
    dup_numbers = set()
    for n in article_numbers:
        if n in seen_numbers:
            dup_numbers.add(n)
        seen_numbers.add(n)
    check(len(dup_numbers) == 0, f"Check 10 FAIL: Duplicate article_numbers: {dup_numbers}")
    print(f"[10] No duplicate article_number: {'PASS' if len(dup_numbers) == 0 else 'FAIL'}")

    # 11. No duplicate article_key
    seen_keys = set()
    dup_keys = set()
    for k in article_keys:
        if k in seen_keys:
            dup_keys.add(k)
        seen_keys.add(k)
    check(len(dup_keys) == 0, f"Check 11 FAIL: Duplicate article_keys: {dup_keys}")
    print(f"[11] No duplicate article_key: {'PASS' if len(dup_keys) == 0 else 'FAIL'}")

    # 12. page_start and page_end are integers and satisfy 1 <= page_start <= page_end <= 16
    page_ok = True
    for idx, rec in enumerate(parsed_records):
        ps = rec.get("page_start")
        pe = rec.get("page_end")
        if not isinstance(ps, int) or isinstance(ps, bool) or ps < 1 or ps > 16:
            failures.append(f"Check 12 FAIL: Record {idx + 1}: page_start invalid: {ps}")
            page_ok = False
        if not isinstance(pe, int) or isinstance(pe, bool) or pe < 1 or pe > 16:
            failures.append(f"Check 12 FAIL: Record {idx + 1}: page_end invalid: {pe}")
            page_ok = False
        if isinstance(ps, int) and isinstance(pe, int) and not isinstance(ps, bool) and not isinstance(pe, bool):
            if ps > pe:
                failures.append(f"Check 12 FAIL: Record {idx + 1}: page_start ({ps}) > page_end ({pe})")
                page_ok = False
    check(page_ok, "Check 12 FAIL: page_start/page_end constraints violated")
    print(f"[12] page_start/page_end constraints: {'PASS' if page_ok else 'FAIL'}")

    # 13. article_text is non-empty
    text_ok = all(isinstance(r.get("article_text"), str) and len(r.get("article_text", "")) > 0
                  for r in parsed_records)
    check(text_ok, "Check 13 FAIL: Some records have empty article_text")
    print(f"[13] article_text non-empty: {'PASS' if text_ok else 'FAIL'}")

    # 14. Article 32 guard
    art32 = None
    for r in parsed_records:
        if r.get("article_number") == 32:
            art32 = r
            break
    art32_ok = (
        art32 is not None
        and art32.get("article_number") == 32
        and art32.get("article_key") == "pdpl_law_art_032"
        and art32.get("article_text") == "ملغاة."
        and art32.get("ready_for_next_layer") is True
    )
    check(art32_ok, "Check 14 FAIL: Article 32 guard failed")
    print(f"[14] Article 32 guard (ملغاة.): {'PASS' if art32_ok else 'FAIL'}")

    # 15. All records have required field values
    required_values = {
        "law_key": "pdpl",
        "law_component": "law",
        "language": "ar",
        "record_layer": "PDPL_ARABIC_LAW_NEXT_LAYER_PREP",
        "article_text_source_field": "article_text_ocr",
        "source_status": "REVIEWED_OCR_INVENTORY_READY_FOR_NEXT_LAYER",
        "official_text_status": "REVIEWED_OCR_NOT_VERIFIED_OFFICIAL_TEXT",
        "source_pdf_sha256": EXPECTED_SHA256,
        "english_used_for_correction": False,
        "translation_performed": False,
        "legal_interpretation_performed": False,
        "ready_for_next_layer": True,
    }
    values_ok = True
    for idx, rec in enumerate(parsed_records):
        for field, expected in required_values.items():
            if rec.get(field) != expected:
                failures.append(f"Check 15 FAIL: Record {idx + 1}: {field}={rec.get(field)} expected {expected}")
                values_ok = False
    check(values_ok, "Check 15 FAIL: Not all records have required field values")
    print(f"[15] Required field values: {'PASS' if values_ok else 'FAIL'}")

    # 16. Summary consistency
    summary = None
    if os.path.isfile(SUMMARY_PATH):
        summary = load_json_file(SUMMARY_PATH)
    summary_ok = False
    if summary is not None:
        summary_ok = (
            summary.get("record_count") == 43
            and summary.get("ready_for_next_layer_count") == 43
            and summary.get("not_ready_count") == 0
            and summary.get("missing_articles") == []
            and summary.get("duplicate_articles") == []
            and summary.get("article_32_resolution", {}).get("source_text") == "ملغاة."
            and summary.get("official_text_status") == "REVIEWED_OCR_NOT_VERIFIED_OFFICIAL_TEXT"
            and summary.get("source_status") == "REVIEWED_OCR_INVENTORY_READY_FOR_NEXT_LAYER"
        )
    check(summary_ok, "Check 16 FAIL: Summary consistency check failed")
    print(f"[16] Summary consistency: {'PASS' if summary_ok else 'FAIL'}")

    # 17. QA findings consistency
    qa = None
    if os.path.isfile(QA_PATH):
        qa = load_json_file(QA_PATH)
    qa_ok = False
    if qa is not None:
        qa_ok = (
            qa.get("qa_decision") == "PASS_READY_FOR_SCHEMA_AND_VALIDATOR_DESIGN"
            and qa.get("recommended_next_stage") == "PDPL_ARABIC_LAW_SCHEMA_AND_VALIDATOR_DESIGN"
            and qa.get("blocking_findings") == []
        )
    check(qa_ok, "Check 17 FAIL: QA findings consistency check failed")
    print(f"[17] QA findings consistency: {'PASS' if qa_ok else 'FAIL'}")

    # 18. Boundary guards
    boundary_ok = True
    for idx, rec in enumerate(parsed_records):
        # Must not claim official verified text
        ots = rec.get("official_text_status", "")
        if "VERIFIED_OFFICIAL_TEXT" in ots and ots != "REVIEWED_OCR_NOT_VERIFIED_OFFICIAL_TEXT":
            failures.append(f"Check 18 FAIL: Record {idx + 1}: claims official verified text: {ots}")
            boundary_ok = False
        # Must not have english_used_for_correction true
        if rec.get("english_used_for_correction") is True:
            failures.append(f"Check 18 FAIL: Record {idx + 1}: english_used_for_correction is true")
            boundary_ok = False
        # Must not have translation_performed true
        if rec.get("translation_performed") is True:
            failures.append(f"Check 18 FAIL: Record {idx + 1}: translation_performed is true")
            boundary_ok = False
        # Must not have legal_interpretation_performed true
        if rec.get("legal_interpretation_performed") is True:
            failures.append(f"Check 18 FAIL: Record {idx + 1}: legal_interpretation_performed is true")
            boundary_ok = False
    check(boundary_ok, "Check 18 FAIL: Boundary guard violation")
    print(f"[18] Boundary guards: {'PASS' if boundary_ok else 'FAIL'}")

    # 19. Mutation guard — validator is read-only, no file writes
    # (This is a static guarantee: this script performs no write operations.)
    print(f"[19] Mutation guard (read-only): PASS (no file writes performed)")

    # Summary
    print("=" * 70)
    total_checks = 19
    print(f"Checks passed: {checks_passed + 1}/{total_checks}")  # +1 for check 19 (always pass)
    print(f"Checks failed: {len(failures)}")

    if failures:
        print("\n--- FAILURES ---")
        for f_msg in failures:
            print(f"  • {f_msg}")
        print("\n" + "=" * 70)
        print("RESULT: FAIL")
        print("=" * 70)
        sys.exit(1)
    else:
        print("\n" + "=" * 70)
        print(f"RESULT: PASS")
        print(f"  • {EXPECTED_RECORD_COUNT} records validated")
        print(f"  • Article range 1→43")
        print(f"  • Article 32 confirmed as ملغاة.")
        print(f"  • official_text_status remains REVIEWED_OCR_NOT_VERIFIED_OFFICIAL_TEXT")
        print(f"  • no English correction / no translation / no legal interpretation")
        print(f"  • no blocking findings")
        print(f"  • no file mutations (read-only validator)")
        print("=" * 70)
        sys.exit(0)


if __name__ == "__main__":
    main()