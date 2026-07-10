#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Civil Transactions Law Arabic LLM enrichment layer."""

from __future__ import annotations

import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFIED = os.path.join(ROOT, "sources", "civil", "law", "verified",
                        "civil_transactions_law_verified_records.jsonl")
LAYER = os.path.join(ROOT, "data", "civil_arabic_legal_llm",
                     "civil_transactions_law_legal_llm_001_721.json")
SCHEMA = os.path.join(ROOT, "schemas", "civil_transactions_law_legal_llm.schema.json")

EXPECTED = 721


def main():
    errors = []
    for p in (VERIFIED, LAYER, SCHEMA):
        if not os.path.isfile(p):
            print("FAIL: missing file: %s" % os.path.relpath(p, ROOT))
            return 1

    verified = {}
    for line in open(VERIFIED, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            verified[r["article_number"]] = r

    layer = json.load(open(LAYER, encoding="utf-8"))
    records = layer.get("records", [])

    if layer.get("record_count") != EXPECTED:
        errors.append("[1] envelope record_count %r != %d" % (layer.get("record_count"), EXPECTED))
    if len(records) != EXPECTED:
        errors.append("[1] found %d records, expected %d" % (len(records), EXPECTED))
    if layer.get("text_status") != "OWNER_PROVIDED_OFFICIAL_TEXT":
        errors.append("[1] envelope text_status wrong")
    if layer.get("not_legal_advice") is not True:
        errors.append("[1] envelope not_legal_advice must be True")

    if [r["article_number"] for r in records] != list(range(1, EXPECTED + 1)):
        errors.append("[2] article_number sequence not 1..%d" % EXPECTED)

    for r in records:
        n = r.get("article_number")
        if r.get("article_key") != "civil_law_art_%03d" % n:
            errors.append("[3] art %s: article_key %r" % (n, r.get("article_key")))
        if r.get("record_id") != "civil-law-llm-art-%03d" % n:
            errors.append("[3] art %s: record_id %r" % (n, r.get("record_id")))
        if r.get("article_path") != "civil/law/articles/%03d" % n:
            errors.append("[3] art %s: article_path %r" % (n, r.get("article_path")))

        text = r.get("article_text_ar", "")
        src = verified.get(n, {})
        if text != src.get("article_text_verified"):
            errors.append("[4] art %s: article_text_ar differs from verified source" % n)
        if r.get("section_context_ar") != src.get("section_context_ar", ""):
            errors.append("[4] art %s: section_context differs from verified source" % n)
        if r.get("article_text_hash_sha256") != hashlib.sha256(text.encode("utf-8")).hexdigest():
            errors.append("[4] art %s: hash mismatch" % n)

        if not r.get("keywords_ar"):
            errors.append("[5] art %s: empty keywords_ar" % n)
        if not r.get("search_queries_ar"):
            errors.append("[5] art %s: empty search_queries_ar" % n)
        if str(n) not in r.get("retrieval_title_ar", ""):
            errors.append("[5] art %s: retrieval_title_ar missing article number" % n)

        if r.get("record_type") != "official_arabic_article":
            errors.append("[6] art %s: record_type %r" % (n, r.get("record_type")))
        for flag in ("translation_performed", "legal_interpretation_performed",
                     "english_used_for_correction", "text_summarized_or_paraphrased"):
            if r.get(flag) is not False:
                errors.append("[6] art %s: boundary flag %s must be False" % (n, flag))

    schema_note = "skipped (jsonschema not installed)"
    try:
        from jsonschema import Draft7Validator
        schema = json.load(open(SCHEMA, encoding="utf-8"))
        v = Draft7Validator(schema)
        bad = 0
        for r in records:
            for e in v.iter_errors(r):
                bad += 1
                if bad <= 10:
                    errors.append("[7] art %s: schema: %s" % (r.get("article_number"), e.message))
        schema_note = "validated %d records" % len(records) if not bad else "%d violations" % bad
    except ImportError:
        pass

    if errors:
        print("FAIL: %d error(s) in Civil Transactions Law LLM layer:" % len(errors))
        for e in errors[:20]:
            print("  - %s" % e)
        return 1

    print("PASS: %d Civil Transactions Law LLM-ready records" % len(records))
    print("  - article_text_ar + section context verbatim from verified source; ids/paths/hashes consistent")
    print("  - JSON Schema: %s" % schema_note)
    print("  - honest boundaries: owner-provided official text, no translation/paraphrase/interpretation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
