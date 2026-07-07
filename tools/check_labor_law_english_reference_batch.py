#!/usr/bin/env python3
"""
Labor Law English Reference Batch Checker
Validates scaffold JSONL records for English reference layer.
Strictly reference-only. No legal advice, no official translation.
"""
import json
import sys
import argparse

def load_jsonl(path):
    records = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records

def validate_record(record, schema):
    # Basic required field checks (simplified schema validation)
    required = [
        "law_id", "layer", "article_key", "article_number",
        "arabic_governing_status", "english_reference_status", "english_text",
        "official_english_source_url", "official_english_source_status",
        "source_packet_required", "reference_only", "arabic_official_source_governs",
        "no_legal_advice", "no_official_translation_claim", "unresolved_arabic_issue_flag"
    ]
    for field in required:
        if field not in record:
            return False, f"Missing required field: {field}"
    
    if record["law_id"] != "labor_law":
        return False, "law_id must be labor_law"
    if record["layer"] != "english_reference":
        return False, "layer must be english_reference"
    if record["reference_only"] is not True:
        return False, "reference_only must be true"
    if record["arabic_official_source_governs"] is not True:
        return False, "arabic_official_source_governs must be true"
    if record["no_legal_advice"] is not True:
        return False, "no_legal_advice must be true"
    if record["no_official_translation_claim"] is not True:
        return False, "no_official_translation_claim must be true"
    if record["unresolved_arabic_issue_flag"] is not False:
        return False, "unresolved_arabic_issue_flag must be false for Batch 001"
    
    if not record["article_key"] or not isinstance(record["article_key"], str):
        return False, "article_key must be non-empty string"
    
    if record["english_reference_status"] == "OFFICIAL_ENGLISH_PENDING":
        if record["english_text"] != "":
            return False, "english_text must be empty when OFFICIAL_ENGLISH_PENDING"
        if record["official_english_source_status"] != "SOURCE_PACKET_REQUIRED":
            return False, "official_english_source_status must be SOURCE_PACKET_REQUIRED when pending"
        if record["source_packet_required"] is not True:
            return False, "source_packet_required must be true when pending"
    
    if record["english_reference_status"] == "OFFICIAL_ENGLISH_CAPTURED":
        if not record.get("official_english_source_url"):
            return False, "official_english_source_url required when CAPTURED"
    
    # Prohibited claims check
    prohibited = ["official translation", "legal advice", "legal interpretation", "legally verified", "final ingestion"]
    text_to_check = str(record).lower()
    for p in prohibited:
        if p in text_to_check:
            return False, f"Prohibited claim found: {p}"
    
    return True, "OK"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jsonl", required=True)
    parser.add_argument("--schema", required=True)
    args = parser.parse_args()
    
    try:
        records = load_jsonl(args.jsonl)
    except Exception as e:
        print(f"ERROR loading JSONL: {e}")
        sys.exit(1)
    
    print(f"Loaded {len(records)} records from {args.jsonl}")
    
    all_ok = True
    for i, rec in enumerate(records):
        ok, msg = validate_record(rec, args.schema)
        if not ok:
            print(f"FAIL record {i} ({rec.get('article_key', 'unknown')}): {msg}")
            all_ok = False
        else:
            print(f"PASS record {i} ({rec.get('article_key', 'unknown')})")
    
    if all_ok:
        print("\nAll records validated successfully.")
        print("Batch 001 scaffold is valid.")
    else:
        print("\nValidation failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()