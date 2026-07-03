#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the Chinese Legal LLM-ready layer (Book Four Sections 1, 2 & 3).

Enforces:
- exactly the sanctioned files exist: book4_section1_zh_legal_llm.json,
  book4_section2_zh_legal_llm.json, book4_section3_zh_legal_llm.json; no other sections/books;
- 14 records total — Section 1 groups [58],[59],[60],[66]; Section 2 groups
  [67,68],[71],[72],[75],[77]; Section 3 groups [85,87],[92,93],[99],[101],[102];
  no uncovered articles;
- every record passes schemas/chinese_legal_llm.schema.json;
- legal_rule_text_zh is byte-identical to the corresponding provision's chinese_translation
  in that section's provision source file;
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
ART_DIR = os.path.join(ROOT, "data", "articles")
SOURCE_FIELD = "chinese_translation"

ALL_BOOK4 = set(range(58, 138))

# (zh llm filename, provision source filename, expected provision groups).
UNITS = [
    ("book4_section1_zh_legal_llm.json", "book4_provisions_058_066.json",
     [[58], [59], [60], [66]]),
    ("book4_section2_zh_legal_llm.json", "book4_provisions_067_083.json",
     [[67, 68], [71], [72], [75], [77]]),
    ("book4_section3_zh_legal_llm.json", "book4_provisions_084_102.json",
     [[85, 87], [92, 93], [99], [101], [102]]),
]
EXPECTED_FILES = sorted(u[0] for u in UNITS)
TOTAL_EXPECTED = 14   # 4 (Section 1) + 5 (Section 2) + 5 (Section 3)

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
    if files != EXPECTED_FILES:
        problems.append("expected exactly Chinese LLM files %r, found %r" % (EXPECTED_FILES, files))

    total = 0
    for fname, prov_fname, groups in UNITS:
        path = os.path.join(LLM_DIR, fname)
        prov_path = os.path.join(ART_DIR, prov_fname)
        provtext = {}
        if os.path.exists(prov_path):
            provtext = {tuple(p["source_article_numbers"]): p[SOURCE_FIELD]
                        for p in _read(prov_path)["provisions"]}
        else:
            problems.append("%s: provision source missing: %s" % (fname, prov_fname))
        if not os.path.exists(path):
            problems.append("Chinese LLM data file missing: %s" % fname)
            continue

        doc = _read(path)
        records = doc.get("records", [])
        total += len(records)
        nums = [r.get("article_numbers") for r in records]
        if nums != groups:
            problems.append("%s: article groups must be %r (got %r)" % (fname, groups, nums))
        # Nothing outside this unit's groups may appear (within Book Four).
        flat = {n for g in nums for n in (g or [])}
        allowed = {n for g in groups for n in g}
        leaked = sorted(flat & (ALL_BOOK4 - allowed))
        if leaked:
            problems.append("%s: forbidden article numbers present (uncovered/other sections): %s" % (fname, leaked))

        blob = open(path, encoding="utf-8").read()
        if "legal_rule_summary_zh" in blob:
            problems.append("%s: forbidden field legal_rule_summary_zh present (no generated summaries)" % fname)
        low = blob.lower()
        for term in BANNED:
            if term.lower() in low:
                problems.append("%s: forbidden overclaim/official term in data: '%s'" % (fname, term))

        for r in records:
            rid = r.get("record_id", "?")
            if schema is not None:
                for msg in _validate_record(r, schema):
                    problems.append("%s:%s: %s" % (fname, rid, msg))
            if r.get("record_type") != "article_reference":
                problems.append("%s:%s: record_type must be article_reference" % (fname, rid))
            if r.get("book") != 4:
                problems.append("%s:%s: book must be 4" % (fname, rid))
            if "legal_rule_summary_zh" in r:
                problems.append("%s:%s: legal_rule_summary_zh must not exist" % (fname, rid))
            # legal_rule_text_zh must equal the provision's chinese_translation verbatim.
            key = tuple(r.get("article_numbers") or [])
            if key in provtext and r.get("legal_rule_text_zh") != provtext[key]:
                problems.append("%s:%s: legal_rule_text_zh != provision %s (arts %s)"
                                % (fname, rid, SOURCE_FIELD, list(key)))
            st = r.get("source_trust", {})
            if st.get("chinese_source_status") != "internal_working_translation":
                problems.append("%s:%s: source_trust.chinese_source_status must be internal_working_translation" % (fname, rid))
            if st.get("governing_text_language") != "ar":
                problems.append("%s:%s: source_trust.governing_text_language must be ar" % (fname, rid))
            if st.get("official_text_check") != "needs_check":
                problems.append("%s:%s: source_trust.official_text_check must be needs_check" % (fname, rid))
            if st.get("manual_review_status") != "needs_manual_check":
                problems.append("%s:%s: source_trust.manual_review_status must be needs_manual_check" % (fname, rid))

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
    print("Chinese Legal LLM-ready layer validation (Book 4 Sections 1, 2 & 3)")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] %d records — Book 4 Section 1 ([58],[59],[60],[66]) + Section 2 "
          "([67,68],[71],[72],[75],[77]) + Section 3 ([85,87],[92,93],[99],[101],[102]); "
          "legal_rule_text_zh verbatim from provision %s; "
          "internal_working_translation; governing=ar; official_text_check=needs_check; "
          "needs_manual_check; no generated summaries" % (total, SOURCE_FIELD))
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
