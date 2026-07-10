#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the PDPL Implementing Regulation Arabic LLM layer.

Checks internal consistency, faithfulness to the cleaned-text source it derives
from, honest boundary flags, and (if ``jsonschema`` is installed) conformance to
the JSON Schema.  Does not modify any file.  Exit 0 = PASS, 1 = FAIL.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFIED = os.path.join(
    ROOT, "sources", "pdpl", "regulation", "verified",
    "pdpl_implementing_regulation_arabic_verified_records.jsonl",
)
LAYER = os.path.join(
    ROOT, "data", "pdpl_arabic_legal_llm",
    "pdpl_implementing_regulation_arabic_legal_llm_001_038.json",
)
SCHEMA = os.path.join(
    ROOT, "schemas", "pdpl_implementing_regulation_arabic_legal_llm.schema.json")

EXPECTED_COUNT = 38


def main():
    errors = []

    for path in (VERIFIED, LAYER, SCHEMA):
        if not os.path.isfile(path):
            print("FAIL: missing file: %s" % os.path.relpath(path, ROOT))
            return 1

    verified = {}
    for line in open(VERIFIED, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            verified[r["article_number"]] = r

    layer = json.load(open(LAYER, encoding="utf-8"))
    records = layer.get("records", [])

    # [1] envelope
    if layer.get("record_count") != EXPECTED_COUNT:
        errors.append("[1] envelope record_count %r != %d"
                      % (layer.get("record_count"), EXPECTED_COUNT))
    if len(records) != EXPECTED_COUNT:
        errors.append("[1] found %d records, expected %d" % (len(records), EXPECTED_COUNT))
    if layer.get("text_status") != "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT":
        errors.append("[1] envelope text_status not VERIFIED value")
    if layer.get("not_legal_advice") is not True:
        errors.append("[1] envelope not_legal_advice must be True")

    # [2] sequence
    nums = [r["article_number"] for r in records]
    if nums != list(range(1, EXPECTED_COUNT + 1)):
        errors.append("[2] article_number sequence is not 1..%d" % EXPECTED_COUNT)

    for r in records:
        n = r.get("article_number")

        # [3] ids / paths
        if r.get("article_key") != "pdpl_reg_art_%03d" % n:
            errors.append("[3] art %s: article_key %r" % (n, r.get("article_key")))
        if r.get("record_id") != "pdpl-reg-llm-art-%03d" % n:
            errors.append("[3] art %s: record_id %r" % (n, r.get("record_id")))
        if r.get("article_path") != "pdpl/implementing_regulation/articles/%03d" % n:
            errors.append("[3] art %s: article_path %r" % (n, r.get("article_path")))

        # [4] text faithful to verified source (verbatim) + hash correct
        text = r.get("article_text_ar", "")
        src = verified.get(n, {}).get("article_text_verified")
        if src is None:
            errors.append("[4] art %s: no verified source record" % n)
        elif text != src:
            errors.append("[4] art %s: article_text_ar differs from verified source" % n)
        h = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if r.get("article_text_hash_sha256") != h:
            errors.append("[4] art %s: hash mismatch" % n)

        # [5] title / retrieval metadata derived from heading
        title = r.get("article_title_ar", "")
        if not title.strip():
            errors.append("[5] art %s: empty article_title_ar" % n)
        if r.get("llm_title_ar") != "المادة %d: %s" % (n, title):
            errors.append("[5] art %s: llm_title_ar not derived from title" % n)
        if title not in r.get("retrieval_title_ar", ""):
            errors.append("[5] art %s: retrieval_title_ar missing title" % n)
        if not r.get("keywords_ar"):
            errors.append("[5] art %s: empty keywords_ar" % n)
        if not r.get("search_queries_ar"):
            errors.append("[5] art %s: empty search_queries_ar" % n)

        # [6] honesty boundaries
        if r.get("record_type") != "verified_arabic_article":
            errors.append("[6] art %s: unexpected record_type: %r" % (n, r.get("record_type")))
        if r.get("text_status") != "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT":
            errors.append("[6] art %s: text_status not VERIFIED" % n)
        for flag in ("translation_performed", "legal_interpretation_performed",
                     "english_used_for_correction", "text_summarized_or_paraphrased"):
            if r.get(flag) is not False:
                errors.append("[6] art %s: boundary flag %s must be False" % (n, flag))
        st = r.get("source_trust", {})
        if st.get("source_status") != "verified_against_official_sdaia_published_text":
            errors.append("[6] art %s: source_trust.source_status wrong" % n)

    # [7] JSON Schema (optional)
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
                    errors.append("[7] art %s: schema: %s"
                                  % (r.get("article_number"), e.message))
        schema_note = "validated %d records" % len(records) if not bad else "%d violations" % bad
    except ImportError:
        pass

    if errors:
        print("FAIL: %d error(s) in PDPL implementing regulation LLM layer:" % len(errors))
        for e in errors:
            print("  - %s" % e)
        return 1

    print("PASS: %d PDPL implementing regulation LLM-ready records" % len(records))
    print("  - sequence 1..%d; ids, paths, hashes consistent" % EXPECTED_COUNT)
    print("  - article_text_ar verbatim from verified source; retrieval metadata derived")
    print("  - JSON Schema: %s" % schema_note)
    print("  - honest boundaries: verified_arabic_article (SDAIA-published), no translation/paraphrase/interpretation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
