#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the English Legal LLM-ready layer (PILOT: Book Four Section 1 only).

Enforces:
- exactly one English Legal LLM file exists: book4_section1_en_legal_llm.json;
- exactly 4 records, article groups [58], [59], [60], [66]; no 61-65; no other sections/books;
- every record passes schemas/english_legal_llm.schema.json;
- legal_rule_text_en is byte-identical to the corresponding english_reference_text;
- no legal_rule_summary_en / generated-summary field;
- trust posture (official_guidance_translation / ar / needs_manual_check);
- no forbidden overclaim terms; no book4_articles_* / full book4.md.

Exit 0 == pass; 1 == problems. No network, no heavy dependencies.
"""

from __future__ import annotations

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "english_legal_llm.schema.json")
LLM_DIR = os.path.join(ROOT, "data", "english_legal_llm")
EN_REF = os.path.join(ROOT, "data", "english_reference", "book4_section1_en_reference.json")

PILOT_FILE = "book4_section1_en_legal_llm.json"
COVERED = [58, 59, 60, 66]
FORBIDDEN_ARTICLES = set(range(61, 66)) | set(range(67, 138)) | set(range(1, 58))
TOTAL_EXPECTED = 4

# Positive overclaim assertions that must NOT appear in the data.
BANNED = [
    "binding english text", "governing english text", "english is binding",
    "verified translation", "binding_translation", "official legal advice",
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

    schema = _read(SCHEMA) if os.path.exists(SCHEMA) else None
    if schema is None:
        problems.append("schema missing: schemas/english_legal_llm.schema.json")

    files = sorted(glob.glob(os.path.join(LLM_DIR, "*_en_legal_llm.json")))
    names = [os.path.basename(p) for p in files]
    if names != [PILOT_FILE]:
        problems.append("expected exactly one English LLM file %r, found %r" % ([PILOT_FILE], names))

    path = os.path.join(LLM_DIR, PILOT_FILE)
    reftext = {}
    if os.path.exists(EN_REF):
        reftext = {r["article_number"]: r["english_reference_text"]
                   for r in _read(EN_REF)["records"]}
    else:
        problems.append("English reference source missing: book4_section1_en_reference.json")

    total = 0
    if not os.path.exists(path):
        problems.append("pilot data file missing: %s" % PILOT_FILE)
    else:
        doc = _read(path)
        records = doc.get("records", [])
        total = len(records)
        nums = [r.get("article_numbers") for r in records]
        if nums != [[n] for n in COVERED]:
            problems.append("article groups must be %r (got %r)" % ([[n] for n in COVERED], nums))
        flat = [n for g in nums for n in (g or [])]
        leaked = sorted(set(flat) & FORBIDDEN_ARTICLES)
        if leaked:
            problems.append("forbidden article numbers present (uncovered/other sections/books): %s" % leaked)

        blob = open(path, encoding="utf-8").read()
        if "legal_rule_summary_en" in blob:
            problems.append("forbidden field legal_rule_summary_en present (no generated summaries)")
        low = blob.lower()
        for term in BANNED:
            if term in low:
                problems.append("forbidden overclaim term in data: '%s'" % term)

        for r in records:
            rid = r.get("record_id", "?")
            if schema is not None:
                for msg in _validate_record(r, schema):
                    problems.append("%s: %s" % (rid, msg))
            if r.get("record_type") != "article_reference":
                problems.append("%s: record_type must be article_reference" % rid)
            if r.get("book") != 4:
                problems.append("%s: book must be 4" % rid)
            if "legal_rule_summary_en" in r:
                problems.append("%s: legal_rule_summary_en must not exist" % rid)
            # legal_rule_text_en must equal the English reference text verbatim.
            ans = r.get("article_numbers") or []
            if len(ans) == 1:
                n = ans[0]
                if n in reftext and r.get("legal_rule_text_en") != reftext[n]:
                    problems.append("%s: legal_rule_text_en != english_reference_text (art %s)" % (rid, n))
            st = r.get("source_trust", {})
            if st.get("english_source_status") != "official_guidance_translation":
                problems.append("%s: source_trust.english_source_status must be official_guidance_translation" % rid)
            if st.get("governing_text_language") != "ar":
                problems.append("%s: source_trust.governing_text_language must be ar" % rid)
            if st.get("manual_review_status") != "needs_manual_check":
                problems.append("%s: source_trust.manual_review_status must be needs_manual_check" % rid)

    if total != TOTAL_EXPECTED:
        problems.append("total English Legal LLM records must be %d (got %d)" % (TOTAL_EXPECTED, total))

    # No Book Four per-article dataset / no full Book Four content.
    for f in os.listdir(os.path.join(ROOT, "data", "articles")):
        if f.startswith("book4_articles_"):
            problems.append("data/articles/%s must not exist" % f)
    for p in ("content/ar/book4.md", "content/zh/book4.md", "content/bilingual/book4_bilingual.md"):
        if os.path.exists(os.path.join(ROOT, p)):
            problems.append("%s must not exist" % p)

    print("=" * 60)
    print("English Legal LLM-ready layer validation (PILOT: Book 4 Section 1)")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] %d records — Book 4 Section 1 pilot (58,59,60,66); "
          "legal_rule_text_en verbatim from English reference; "
          "official_guidance_translation; governing=ar; needs_manual_check; "
          "no generated summaries" % total)
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
