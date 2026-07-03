#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the Chinese Legal LLM-ready layer (PILOT: Book Four Section 1 only).

Enforces:
- exactly one Chinese Legal LLM file exists: book4_section1_zh_legal_llm.json;
- exactly 4 records, article groups [58], [59], [60], [66]; no 61-65; no other
  sections/books;
- every record passes schemas/chinese_legal_llm.schema.json;
- legal_rule_text_zh is byte-identical to the corresponding provision's chinese_translation
  in data/articles/book4_provisions_058_066.json;
- no legal_rule_summary_zh / generated-summary field;
- trust posture (internal_working_translation / ar / needs_check / needs_manual_check);
- no forbidden overclaim / official-translation terms; no book4_articles_* / full book4.md.

Exit 0 == pass; 1 == problems. No network, no heavy dependencies.
"""

from __future__ import annotations

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "chinese_legal_llm.schema.json")
LLM_DIR = os.path.join(ROOT, "data", "chinese_legal_llm")
PROVISIONS = os.path.join(ROOT, "data", "articles", "book4_provisions_058_066.json")
SOURCE_FIELD = "chinese_translation"

PILOT_FILE = "book4_section1_zh_legal_llm.json"
COVERED = [58, 59, 60, 66]
FORBIDDEN_ARTICLES = set(range(61, 66)) | set(range(67, 138)) | set(range(1, 58))
TOTAL_EXPECTED = 4

# Positive overclaim / official-translation assertions that must NOT appear in the data.
BANNED = [
    "official chinese translation", "verified chinese translation", "chinese is binding",
    "governing chinese text", "binding chinese text", "official legal advice",
    "official_translation",
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
        problems.append("schema missing: schemas/chinese_legal_llm.schema.json")

    files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(LLM_DIR, "*_zh_legal_llm.json")))
    if files != [PILOT_FILE]:
        problems.append("expected exactly one Chinese LLM file %r, found %r" % ([PILOT_FILE], files))

    provtext = {}
    if os.path.exists(PROVISIONS):
        provtext = {tuple(p["source_article_numbers"]): p[SOURCE_FIELD]
                    for p in _read(PROVISIONS)["provisions"]}
    else:
        problems.append("provision source missing: %s" % os.path.basename(PROVISIONS))

    path = os.path.join(LLM_DIR, PILOT_FILE)
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
        flat = {n for g in nums for n in (g or [])}
        leaked = sorted(flat & FORBIDDEN_ARTICLES)
        if leaked:
            problems.append("forbidden article numbers present (uncovered/other sections/books): %s" % leaked)

        blob = open(path, encoding="utf-8").read()
        if "legal_rule_summary_zh" in blob:
            problems.append("forbidden field legal_rule_summary_zh present (no generated summaries)")
        low = blob.lower()
        for term in BANNED:
            if term.lower() in low:
                problems.append("forbidden overclaim/official term in data: '%s'" % term)

        for r in records:
            rid = r.get("record_id", "?")
            if schema is not None:
                for msg in _validate_record(r, schema):
                    problems.append("%s: %s" % (rid, msg))
            if r.get("record_type") != "article_reference":
                problems.append("%s: record_type must be article_reference" % rid)
            if r.get("book") != 4:
                problems.append("%s: book must be 4" % rid)
            if "legal_rule_summary_zh" in r:
                problems.append("%s: legal_rule_summary_zh must not exist" % rid)
            # legal_rule_text_zh must equal the provision's chinese_translation verbatim.
            key = tuple(r.get("article_numbers") or [])
            if key in provtext and r.get("legal_rule_text_zh") != provtext[key]:
                problems.append("%s: legal_rule_text_zh != provision %s (arts %s)"
                                % (rid, SOURCE_FIELD, list(key)))
            st = r.get("source_trust", {})
            if st.get("chinese_source_status") != "internal_working_translation":
                problems.append("%s: source_trust.chinese_source_status must be internal_working_translation" % rid)
            if st.get("governing_text_language") != "ar":
                problems.append("%s: source_trust.governing_text_language must be ar" % rid)
            if st.get("official_text_check") != "needs_check":
                problems.append("%s: source_trust.official_text_check must be needs_check" % rid)
            if st.get("manual_review_status") != "needs_manual_check":
                problems.append("%s: source_trust.manual_review_status must be needs_manual_check" % rid)

    if total != TOTAL_EXPECTED:
        problems.append("total Chinese Legal LLM records must be %d (got %d)" % (TOTAL_EXPECTED, total))

    # No Book Four per-article dataset / no full Book Four content.
    for f in os.listdir(os.path.join(ROOT, "data", "articles")):
        if f.startswith("book4_articles_"):
            problems.append("data/articles/%s must not exist" % f)
    for p in ("content/ar/book4.md", "content/zh/book4.md", "content/bilingual/book4_bilingual.md"):
        if os.path.exists(os.path.join(ROOT, p)):
            problems.append("%s must not exist" % p)

    print("=" * 60)
    print("Chinese Legal LLM-ready layer validation (PILOT: Book 4 Section 1)")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] %d records — Book 4 Section 1 pilot (58,59,60,66); "
          "legal_rule_text_zh verbatim from provision %s; internal_working_translation; "
          "governing=ar; official_text_check=needs_check; needs_manual_check; "
          "no generated summaries" % (total, SOURCE_FIELD))
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
