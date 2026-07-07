#!/usr/bin/env python3
"""
Labor Law English Reference Batch Checker
Validates scaffold JSONL records for English reference layer.
Actually loads and applies the --schema file (basic JSON Schema subset).
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

def load_schema(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def _validate_value(value, prop_schema, path):
    """Basic validation for a single property value against its schema definition."""
    errors = []
    
    # type check
    expected_type = prop_schema.get("type")
    if expected_type == "string" and not isinstance(value, str):
        errors.append(f"{path} must be string")
    elif expected_type == "integer" and not isinstance(value, int):
        errors.append(f"{path} must be integer")
    elif expected_type == "boolean" and not isinstance(value, bool):
        errors.append(f"{path} must be boolean")
    elif expected_type == "object" and not isinstance(value, dict):
        errors.append(f"{path} must be object")
    
    # const
    if "const" in prop_schema and value != prop_schema["const"]:
        errors.append(f"{path} must be exactly {prop_schema['const']}")
    
    # enum
    if "enum" in prop_schema and value not in prop_schema["enum"]:
        errors.append(f"{path} must be one of {prop_schema['enum']}")
    
    # minLength
    if "minLength" in prop_schema and isinstance(value, str) and len(value) < prop_schema["minLength"]:
        errors.append(f"{path} must have minLength {prop_schema['minLength']}")
    
    # minimum
    if "minimum" in prop_schema and isinstance(value, int) and value < prop_schema["minimum"]:
        errors.append(f"{path} must be >= {prop_schema['minimum']}")
    
    return errors

def validate_against_schema(record, schema):
    """Validate a single record against the loaded JSON Schema (basic implementation)."""
    errors = []
    
    # additionalProperties: false
    allowed_props = set(schema.get("properties", {}).keys())
    for key in record.keys():
        if key not in allowed_props:
            errors.append(f"Unexpected property (additionalProperties=false): {key}")
    
    # required fields
    required = schema.get("required", [])
    for field in required:
        if field not in record:
            errors.append(f"Missing required field: {field}")
    
    # property level validation
    properties = schema.get("properties", {})
    for prop_name, prop_schema in properties.items():
        if prop_name in record:
            value = record[prop_name]
            prop_errors = _validate_value(value, prop_schema, prop_name)
            errors.extend(prop_errors)
    
    # Special business rules (from schema intent + batch rules)
    if record.get("law_id") != "labor_law":
        errors.append("law_id must be labor_law")
    if record.get("layer") != "english_reference":
        errors.append("layer must be english_reference")
    if record.get("reference_only") is not True:
        errors.append("reference_only must be true")
    if record.get("arabic_official_source_governs") is not True:
        errors.append("arabic_official_source_governs must be true")
    if record.get("no_legal_advice") is not True:
        errors.append("no_legal_advice must be true")
    if record.get("no_official_translation_claim") is not True:
        errors.append("no_official_translation_claim must be true")
    if record.get("unresolved_arabic_issue_flag") is not False:
        errors.append("unresolved_arabic_issue_flag must be false for Batch 001")
    
    if not record.get("article_key") or not isinstance(record.get("article_key"), str):
        errors.append("article_key must be non-empty string")
    
    # PENDING / CAPTURED rules
    eng_status = record.get("english_reference_status")
    if eng_status == "OFFICIAL_ENGLISH_PENDING":
        if record.get("english_text") != "":
            errors.append("english_text must be empty when OFFICIAL_ENGLISH_PENDING")
        if record.get("official_english_source_status") != "SOURCE_PACKET_REQUIRED":
            errors.append("official_english_source_status must be SOURCE_PACKET_REQUIRED when pending")
        if record.get("source_packet_required") is not True:
            errors.append("source_packet_required must be true when pending")
    elif eng_status == "OFFICIAL_ENGLISH_CAPTURED":
        if not record.get("official_english_source_url"):
            errors.append("official_english_source_url required when CAPTURED")
    
    # Prohibited affirmative claims (not the negative flags)
    prohibited = ["official translation", "legal advice provided", "legal interpretation provided", "legally verified", "final ingestion complete"]
    text_to_check = str(record).lower()
    for p in prohibited:
        if p in text_to_check:
            errors.append(f"Prohibited claim found: {p}")
    
    return errors

def check_duplicates(records):
    """Check for duplicate article_key across the batch."""
    seen = {}
    duplicates = []
    for i, rec in enumerate(records):
        key = rec.get("article_key")
        if key in seen:
            duplicates.append((key, seen[key], i))
        else:
            seen[key] = i
    return duplicates

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jsonl", required=True, help="Path to JSONL file")
    parser.add_argument("--schema", required=True, help="Path to JSON Schema file")
    args = parser.parse_args()
    
    try:
        records = load_jsonl(args.jsonl)
        schema = load_schema(args.schema)
    except Exception as e:
        print(f"ERROR loading files: {e}")
        sys.exit(1)
    
    print(f"Loaded {len(records)} records from {args.jsonl}")
    print(f"Loaded schema from {args.schema}")
    
    # Duplicate check first
    dups = check_duplicates(records)
    if dups:
        for key, first_idx, second_idx in dups:
            print(f"FAIL duplicate article_key '{key}' at records {first_idx} and {second_idx}")
        print("\nValidation failed due to duplicates.")
        sys.exit(1)
    else:
        print("No duplicate article_key found.")
    
    all_ok = True
    for i, rec in enumerate(records):
        errors = validate_against_schema(rec, schema)
        if errors:
            print(f"FAIL record {i} ({rec.get('article_key', 'unknown')}): {errors}")
            all_ok = False
        else:
            print(f"PASS record {i} ({rec.get('article_key', 'unknown')})")
    
    if all_ok:
        print("\nAll records validated successfully against schema.")
        print("Batch 001 scaffold is valid.")
    else:
        print("\nValidation failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()