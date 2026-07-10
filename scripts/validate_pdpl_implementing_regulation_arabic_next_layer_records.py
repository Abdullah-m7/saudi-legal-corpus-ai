#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the PDPL implementing-regulation Arabic next-layer records.

Verifies the next-layer records + summary derived from the extracted-text article inventory:
- 38 records, article_number sequence 1..38, article_key pdpl_reg_art_001..038, no duplicates.
- Required fields present with the correct boundary values (Arabic governs; extracted text NOT verified
  official; no English correction / no translation / no legal interpretation).
- Each record's article_text is preserved verbatim from the inventory (article_text_extracted), heading
  and page range match the inventory, and the source PDF sha matches the extraction manifest.
- Summary is consistent with the records.

Read-only: performs no file writes. Exit 0 == pass; 1 == problems.
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "sources", "pdpl", "regulation")
INV = os.path.join(BASE, "inventory", "pdpl_implementing_regulation_arabic_article_inventory.jsonl")
MANIFEST = os.path.join(BASE, "intake", "pdpl_implementing_regulation_arabic_extraction_manifest.json")
RECORDS = os.path.join(BASE, "next_layer", "pdpl_implementing_regulation_arabic_next_layer_records.jsonl")
SUMMARY = os.path.join(BASE, "next_layer", "pdpl_implementing_regulation_arabic_next_layer_summary.json")
QA_FINDINGS = os.path.join(BASE, "next_layer", "qa",
                           "pdpl_implementing_regulation_arabic_next_layer_qa_findings.json")
SCHEMA = os.path.join(ROOT, "schemas", "pdpl_implementing_regulation_next_layer_record.schema.json")

EXPECTED_COUNT = 38
OFFICIAL_TEXT_STATUS = "EXTRACTED_TEXT_NOT_VERIFIED_OFFICIAL_TEXT"
SOURCE_STATUS = "EXTRACTED_TEXT_INVENTORY_READY_FOR_NEXT_LAYER"
RECORD_LAYER = "PDPL_IMPLEMENTING_REGULATION_ARABIC_NEXT_LAYER_PREP"
REQUIRED_FIELDS = (
    "law_key", "law_component", "language", "record_layer", "article_number", "article_key",
    "arabic_heading", "article_text", "article_text_source_field", "source_inventory_file",
    "source_summary_file", "source_extraction_artifact", "source_pdf_sha256", "source_status",
    "official_text_status", "governing_source_note", "page_start", "page_end",
    "extraction_review_flags", "english_used_for_correction", "translation_performed",
    "legal_interpretation_performed", "ready_for_next_layer",
)


def _read_json(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _read_jsonl(p):
    out = []
    for line in open(p, "r", encoding="utf-8"):
        if line.strip():
            out.append(json.loads(line))
    return out


def main():
    print("=" * 70)
    print("PDPL Implementing-Regulation Arabic Next-Layer Records Validator")
    print("=" * 70)
    problems = []

    for p, label in ((INV, "inventory jsonl"), (MANIFEST, "extraction manifest"),
                     (RECORDS, "next-layer records"), (SUMMARY, "next-layer summary")):
        if not os.path.isfile(p):
            problems.append("missing %s: %s" % (label, os.path.relpath(p, ROOT)))
    if problems:
        for m in problems:
            print("  •", m)
        print("RESULT: FAIL")
        return 1

    inv = {r["article_number"]: r for r in _read_jsonl(INV)}
    manifest = _read_json(MANIFEST)
    summary = _read_json(SUMMARY)
    try:
        records = _read_jsonl(RECORDS)
    except ValueError as e:
        print("  • records not valid JSONL: %s" % e)
        print("RESULT: FAIL")
        return 1

    def check(cond, msg):
        if not cond:
            problems.append(msg)

    check(len(records) == EXPECTED_COUNT,
          "record count %d != %d" % (len(records), EXPECTED_COUNT))

    nums = [r.get("article_number") for r in records]
    keys = [r.get("article_key") for r in records]
    check(nums == list(range(1, EXPECTED_COUNT + 1)),
          "article_number sequence must be 1..%d in order" % EXPECTED_COUNT)
    check(keys == ["pdpl_reg_art_%03d" % n for n in range(1, EXPECTED_COUNT + 1)],
          "article_key sequence must be pdpl_reg_art_001..%03d in order" % EXPECTED_COUNT)
    check(len(set(nums)) == len(nums), "duplicate article_number present")
    check(len(set(keys)) == len(keys), "duplicate article_key present")

    # JSON Schema validation (each record) — optional dependency; skipped cleanly if absent
    if not os.path.isfile(SCHEMA):
        problems.append("missing schema: %s" % os.path.relpath(SCHEMA, ROOT))
    else:
        try:
            import jsonschema
            schema = _read_json(SCHEMA)
            validator = jsonschema.Draft7Validator(schema)
            for r in records:
                for err in validator.iter_errors(r):
                    problems.append("art %s schema: %s" % (r.get("article_number"), err.message))
        except ImportError:
            print("  • (jsonschema not installed — schema check skipped; field checks still run)")

    pdf_sha = manifest.get("target_pdf_sha256")
    for r in records:
        n = r.get("article_number")
        for f in REQUIRED_FIELDS:
            if f not in r:
                problems.append("art %s missing field %s" % (n, f))
        check(r.get("law_key") == "pdpl", "art %s law_key wrong" % n)
        check(r.get("law_component") == "implementing_regulation", "art %s law_component wrong" % n)
        check(r.get("language") == "ar", "art %s language wrong" % n)
        check(r.get("record_layer") == RECORD_LAYER, "art %s record_layer wrong" % n)
        check(r.get("source_status") == SOURCE_STATUS, "art %s source_status wrong" % n)
        check(r.get("official_text_status") == OFFICIAL_TEXT_STATUS, "art %s official_text_status wrong" % n)
        check(r.get("english_used_for_correction") is False, "art %s english_used_for_correction must be false" % n)
        check(r.get("translation_performed") is False, "art %s translation_performed must be false" % n)
        check(r.get("legal_interpretation_performed") is False, "art %s legal_interpretation_performed must be false" % n)
        check(r.get("ready_for_next_layer") is True, "art %s ready_for_next_layer must be true" % n)
        check(bool((r.get("article_text") or "").strip()), "art %s article_text empty" % n)
        check(r.get("source_pdf_sha256") == pdf_sha, "art %s source_pdf_sha256 != manifest target_pdf_sha256" % n)
        # verbatim + provenance against the inventory
        src = inv.get(n)
        if src is None:
            problems.append("art %s not present in inventory" % n)
            continue
        check(r.get("article_text") == src.get("article_text_extracted"),
              "art %s article_text not verbatim from inventory" % n)
        check(r.get("arabic_heading") == src.get("arabic_heading"), "art %s arabic_heading != inventory" % n)
        check(r.get("page_start") == src.get("page_start"), "art %s page_start != inventory" % n)
        check(r.get("page_end") == src.get("page_end"), "art %s page_end != inventory" % n)
        check(r.get("extraction_review_flags") == list(src.get("inventory_flags") or []),
              "art %s extraction_review_flags != inventory flags" % n)

    # summary consistency
    check(summary.get("record_count") == EXPECTED_COUNT, "summary record_count must be %d" % EXPECTED_COUNT)
    check(summary.get("ready_for_next_layer_count") == EXPECTED_COUNT, "summary ready_for_next_layer_count must be %d" % EXPECTED_COUNT)
    check(summary.get("not_ready_count") == 0, "summary not_ready_count must be 0")
    check(summary.get("official_text_status") == OFFICIAL_TEXT_STATUS, "summary official_text_status wrong")
    check(summary.get("source_status") == SOURCE_STATUS, "summary source_status wrong")
    check(summary.get("source_pdf_sha256") == pdf_sha, "summary source_pdf_sha256 != manifest")
    check(summary.get("translation_performed") is False, "summary translation_performed must be false")
    check(summary.get("legal_interpretation_performed") is False, "summary legal_interpretation_performed must be false")
    check(summary.get("english_used_for_correction") is False, "summary english_used_for_correction must be false")
    check(summary.get("stage") == RECORD_LAYER, "summary stage wrong")

    # QA findings consistency (present + all gates PASS + a clean decision)
    if not os.path.isfile(QA_FINDINGS):
        problems.append("missing QA findings: %s" % os.path.relpath(QA_FINDINGS, ROOT))
    else:
        qa = _read_json(QA_FINDINGS)
        check(qa.get("stage") == "PDPL_IMPLEMENTING_REGULATION_ARABIC_NEXT_LAYER_QA", "QA stage wrong")
        check(qa.get("record_count") == EXPECTED_COUNT, "QA record_count must be %d" % EXPECTED_COUNT)
        bad_gates = [k for k, v in qa.items()
                     if k.endswith("_status") and k != "official_text_status" and v != "PASS"]
        check(not bad_gates, "QA gates not all PASS: %s" % bad_gates)
        check(not qa.get("blocking_findings"), "QA has blocking findings: %s" % qa.get("blocking_findings"))
        check(qa.get("qa_decision") == "PASS_NEXT_LAYER_READY", "QA decision must be PASS_NEXT_LAYER_READY")
        check(qa.get("review_only") is True, "QA must be review_only")

    print("  • %d records validated" % len(records))
    print("  • article range 1→%d (sequential, unique)" % EXPECTED_COUNT)
    print("  • article_text preserved verbatim from the extracted-text inventory")
    print("  • source_pdf_sha256 matches the extraction manifest")
    print("  • official_text_status remains EXTRACTED_TEXT_NOT_VERIFIED_OFFICIAL_TEXT")
    print("  • no English correction / no translation / no legal interpretation")
    print("  • read-only validator (no file writes)")
    print("=" * 70)
    if problems:
        for m in problems:
            print("  •", m)
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
