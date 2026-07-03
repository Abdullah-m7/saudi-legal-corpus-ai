#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the English Legal LLM-ready layer (Book Four Sections 1, 2 & 3).

Enforces:
- exactly the sanctioned files exist: book4_section1/2/3/4_en_legal_llm.json; no other
  sections/books;
- 21 records total — S1 [58],[59],[60],[66]; S2 [67],[68],[71],[72],[75],[77];
  S3 [85],[87],[92],[93],[99],[101],[102]; S4 [108],[113],[115],[117]; no uncovered articles;
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
REF_DIR = os.path.join(ROOT, "data", "english_reference")

ALL_BOOK4 = set(range(58, 138))

# (llm filename, English reference source filename, covered articles). Each covered
# article maps to exactly one single-article record; anything else in Book Four is
# forbidden for that unit.
UNITS = [
    ("book4_section1_en_legal_llm.json", "book4_section1_en_reference.json", [58, 59, 60, 66]),
    ("book4_section2_en_legal_llm.json", "book4_section2_en_reference.json", [67, 68, 71, 72, 75, 77]),
    ("book4_section3_en_legal_llm.json", "book4_section3_en_reference.json",
     [85, 87, 92, 93, 99, 101, 102]),
    ("book4_section4_en_legal_llm.json", "book4_section4_en_reference.json",
     [108, 113, 115, 117]),
]
EXPECTED_FILES = sorted(u[0] for u in UNITS)
TOTAL_EXPECTED = 21   # 4 (S1) + 6 (S2) + 7 (S3) + 4 (S4)

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

    files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(LLM_DIR, "*_en_legal_llm.json")))
    if files != EXPECTED_FILES:
        problems.append("expected exactly English LLM files %r, found %r" % (EXPECTED_FILES, files))

    total = 0
    for fname, ref_fname, covered in UNITS:
        path = os.path.join(LLM_DIR, fname)
        ref_path = os.path.join(REF_DIR, ref_fname)
        reftext = {}
        if os.path.exists(ref_path):
            reftext = {r["article_number"]: r["english_reference_text"]
                       for r in _read(ref_path)["records"]}
        else:
            problems.append("%s: English reference source missing: %s" % (fname, ref_fname))
        if not os.path.exists(path):
            problems.append("English LLM data file missing: %s" % fname)
            continue

        doc = _read(path)
        records = doc.get("records", [])
        total += len(records)
        nums = [r.get("article_numbers") for r in records]
        if nums != [[n] for n in covered]:
            problems.append("%s: article groups must be %r (got %r)" % (fname, [[n] for n in covered], nums))
        # Nothing outside this unit's covered set may appear (within Book Four).
        flat = {n for g in nums for n in (g or [])}
        forbidden = (ALL_BOOK4 - set(covered))
        leaked = sorted(flat & forbidden)
        if leaked:
            problems.append("%s: forbidden article numbers present (uncovered/other sections): %s" % (fname, leaked))

        blob = open(path, encoding="utf-8").read()
        if "legal_rule_summary_en" in blob:
            problems.append("%s: forbidden field legal_rule_summary_en present (no generated summaries)" % fname)
        low = blob.lower()
        for term in BANNED:
            if term in low:
                problems.append("%s: forbidden overclaim term in data: '%s'" % (fname, term))

        for r in records:
            rid = r.get("record_id", "?")
            if schema is not None:
                for msg in _validate_record(r, schema):
                    problems.append("%s:%s: %s" % (fname, rid, msg))
            if r.get("record_type") != "article_reference":
                problems.append("%s:%s: record_type must be article_reference" % (fname, rid))
            if r.get("book") != 4:
                problems.append("%s:%s: book must be 4" % (fname, rid))
            if "legal_rule_summary_en" in r:
                problems.append("%s:%s: legal_rule_summary_en must not exist" % (fname, rid))
            # legal_rule_text_en must equal the English reference text verbatim.
            ans = r.get("article_numbers") or []
            if len(ans) == 1:
                n = ans[0]
                if n in reftext and r.get("legal_rule_text_en") != reftext[n]:
                    problems.append("%s:%s: legal_rule_text_en != english_reference_text (art %s)" % (fname, rid, n))
            st = r.get("source_trust", {})
            if st.get("english_source_status") != "official_guidance_translation":
                problems.append("%s:%s: source_trust.english_source_status must be official_guidance_translation" % (fname, rid))
            if st.get("governing_text_language") != "ar":
                problems.append("%s:%s: source_trust.governing_text_language must be ar" % (fname, rid))
            if st.get("manual_review_status") != "needs_manual_check":
                problems.append("%s:%s: source_trust.manual_review_status must be needs_manual_check" % (fname, rid))

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
    print("English Legal LLM-ready layer validation (Book 4 Sections 1-4)")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] %d records — Book 4 Section 1 (58,59,60,66) + Section 2 "
          "(67,68,71,72,75,77) + Section 3 (85,87,92,93,99,101,102) + Section 4 "
          "(108,113,115,117); legal_rule_text_en verbatim from English reference; "
          "official_guidance_translation; governing=ar; needs_manual_check; "
          "no generated summaries" % total)
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
