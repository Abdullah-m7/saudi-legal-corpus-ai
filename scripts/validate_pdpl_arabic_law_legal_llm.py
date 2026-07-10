#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the PDPL Law Arabic LLM enrichment layer.

Checks internal consistency, faithfulness to the verified-text source, honest
boundary flags, and JSON Schema conformance (if jsonschema is installed).
Exit 0 = PASS, 1 = FAIL.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFIED = os.path.join(ROOT, "sources", "pdpl", "verified",
                        "pdpl_arabic_law_verified_records.jsonl")
LAYER = os.path.join(ROOT, "data", "pdpl_arabic_legal_llm",
                     "pdpl_arabic_law_legal_llm_001_043.json")
SCHEMA = os.path.join(ROOT, "schemas", "pdpl_arabic_law_legal_llm.schema.json")

EXPECTED = 43
REPEALED = {32}


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
    if layer.get("text_status") != "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT":
        errors.append("[1] envelope text_status wrong")
    if layer.get("not_legal_advice") is not True:
        errors.append("[1] envelope not_legal_advice must be True")

    nums = [r["article_number"] for r in records]
    if nums != list(range(1, EXPECTED + 1)):
        errors.append("[2] article_number sequence not 1..%d" % EXPECTED)

    for r in records:
        n = r.get("article_number")

        if r.get("article_key") != "pdpl_law_art_%03d" % n:
            errors.append("[3] art %s: article_key %r" % (n, r.get("article_key")))
        if r.get("record_id") != "pdpl-law-llm-art-%03d" % n:
            errors.append("[3] art %s: record_id %r" % (n, r.get("record_id")))
        if r.get("article_path") != "pdpl/law/articles/%03d" % n:
            errors.append("[3] art %s: article_path %r" % (n, r.get("article_path")))

        # [4] text verbatim from verified source + hash
        text = r.get("article_text_ar", "")
        src = verified.get(n, {}).get("article_text_verified")
        if src is None:
            errors.append("[4] art %s: no verified source record" % n)
        elif text != src:
            errors.append("[4] art %s: article_text_ar differs from verified source" % n)
        if r.get("article_text_hash_sha256") != hashlib.sha256(text.encode("utf-8")).hexdigest():
            errors.append("[4] art %s: hash mismatch" % n)

        # [5] repealed flag consistent with verified source
        if bool(r.get("is_repealed")) != bool(verified.get(n, {}).get("is_repealed")):
            errors.append("[5] art %s: is_repealed disagrees with verified source" % n)

        # [6] retrieval metadata present
        if not r.get("keywords_ar"):
            errors.append("[6] art %s: empty keywords_ar" % n)
        if not r.get("search_queries_ar"):
            errors.append("[6] art %s: empty search_queries_ar" % n)
        if str(n) not in r.get("retrieval_title_ar", ""):
            errors.append("[6] art %s: retrieval_title_ar missing article number" % n)

        # [7] honest boundaries
        if r.get("record_type") != "verified_arabic_article":
            errors.append("[7] art %s: record_type %r" % (n, r.get("record_type")))
        if r.get("text_status") != "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT":
            errors.append("[7] art %s: text_status wrong" % n)
        for flag in ("translation_performed", "legal_interpretation_performed",
                     "english_used_for_correction", "text_summarized_or_paraphrased"):
            if r.get(flag) is not False:
                errors.append("[7] art %s: boundary flag %s must be False" % (n, flag))

    # [8] JSON Schema
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
                    errors.append("[8] art %s: schema: %s" % (r.get("article_number"), e.message))
        schema_note = "validated %d records" % len(records) if not bad else "%d violations" % bad
    except ImportError:
        pass

    if errors:
        print("FAIL: %d error(s) in PDPL law LLM layer:" % len(errors))
        for e in errors:
            print("  - %s" % e)
        return 1

    print("PASS: %d PDPL law LLM-ready records (Art 32 repealed)" % len(records))
    print("  - article_text_ar verbatim from verified source; ids/paths/hashes consistent")
    print("  - JSON Schema: %s" % schema_note)
    print("  - honest boundaries: verified_arabic_article (SDAIA-published), no translation/paraphrase/interpretation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
