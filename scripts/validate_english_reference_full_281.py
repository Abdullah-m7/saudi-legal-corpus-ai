#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the FULL official English BOE guidance reference alignment (281 articles).

Confirms the full English reference file is schema-valid, covers Articles 1..281 exactly (no gaps
/ no duplicates), carries the official-guidance trust posture (English is guidance only; Arabic
governs), invents no legal analysis / LLM-ready fields, makes no binding/governing/verified
overclaim, and touches no protected layer. Reference/alignment layer only.

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "english_reference.schema.json")
DATA = os.path.join(ROOT, "data", "english_reference",
                    "companies_law_m132_1443_en_reference_001_281.json")
OA_LLM = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
CAND = os.path.join(ROOT, "data", "official_arabic",
                    "companies_law_m132_1443_official_arabic_user_provided.json")

TARGET = 281
BANNED = ("binding english text", "governing english text", "english is binding",
          "verified translation", "binding_translation", "unofficial_translation")
FORBIDDEN_FIELDS = ("legal_rule_text_en", "legal_rule_summary_en", "legal_rule_summary_ar")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _all_keys(obj, acc):
    if isinstance(obj, dict):
        for k, v in obj.items():
            acc.add(k)
            _all_keys(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            _all_keys(v, acc)


def main() -> int:
    problems = []

    if not os.path.exists(SCHEMA):
        problems.append("missing schema: schemas/english_reference.schema.json")
    if not os.path.exists(DATA):
        problems.append("missing full reference file: %s" % os.path.relpath(DATA, ROOT))
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1

    doc = _read(DATA)
    records = doc.get("records", [])

    if len(records) != TARGET:
        problems.append("expected 281 records (got %d)" % len(records))
    nums = [r.get("article_number") for r in records]
    if nums != list(range(1, TARGET + 1)):
        problems.append("article_number must be exactly 1..281 in order")
    if len(set(nums)) != len(nums):
        problems.append("duplicate article numbers present")

    # schema validation
    try:
        import jsonschema
        schema = _read(SCHEMA)
        v = jsonschema.Draft7Validator(schema)
        for r in records:
            for err in v.iter_errors(r):
                problems.append("schema error art %s: %s" % (r.get("article_number"), err.message))
                break
    except ImportError:
        problems.append("jsonschema not available to validate records")

    # per-record trust posture / content
    for r in records:
        n = r.get("article_number")
        if not (r.get("english_reference_text") or "").strip():
            problems.append("art %s english_reference_text empty" % n)
        if r.get("english_source_status") != "official_guidance_translation":
            problems.append("art %s english_source_status must be official_guidance_translation" % n)
        if r.get("governing_text_language") != "ar":
            problems.append("art %s governing_text_language must be ar" % n)
        if r.get("manual_review_status") != "needs_manual_check":
            problems.append("art %s manual_review_status must be needs_manual_check" % n)
        src = r.get("source", {})
        if "Bureau of Experts" not in str(src.get("source_authority", "")):
            problems.append("art %s source_authority must mention Bureau of Experts" % n)
        if src.get("department") != "Official Translation Department":
            problems.append("art %s source.department must be Official Translation Department" % n)

    # no overclaim terms anywhere
    blob = json.dumps(doc, ensure_ascii=False).lower()
    for term in BANNED:
        if term in blob:
            problems.append("banned overclaim term present: %r" % term)

    # no forbidden analysis / LLM-ready fields anywhere
    keys = set()
    _all_keys(doc, keys)
    for k in keys:
        if k in FORBIDDEN_FIELDS:
            problems.append("forbidden field present: %r" % k)
        kl = k.lower()
        if "legal_rule" in kl or "rule_summary" in kl:
            problems.append("forbidden legal-rule field present: %r" % k)
    # the reference record schema is closed (additionalProperties:false); ensure records carry no
    # keys beyond the reference schema (no English LLM-ready fields smuggled in)
    allowed_rec = {"book", "article_number", "part_number_en", "part_title_en",
                   "article_heading_en", "english_reference_text", "english_source_status",
                   "governing_text_language", "alignment_status", "manual_review_status",
                   "source", "llm", "risk_flags"}
    for r in records:
        extra = set(r.keys()) - allowed_rec
        if extra:
            problems.append("art %s has non-reference fields: %s" % (r.get("article_number"), extra))

    # existing 87-record split English reference layer intact (backward compat)
    ref = os.path.join(ROOT, "data", "english_reference")
    for fname, exp in (("book1_en_reference.json", list(range(1, 35))),
                       ("book2_en_reference.json", list(range(35, 51))),
                       ("book3_en_reference.json", list(range(51, 58)))):
        pth = os.path.join(ref, fname)
        if not os.path.exists(pth):
            problems.append("existing split reference missing: %s" % fname)
        elif [x["article_number"] for x in _read(pth)["records"]] != exp:
            problems.append("existing split reference changed: %s" % fname)
    split = glob.glob(os.path.join(ref, "book*_en_reference.json"))
    total_split = sum(len(_read(p)["records"]) for p in split)
    if total_split != 87:
        problems.append("existing split English reference must remain 87 records (got %d)"
                        % total_split)

    # English Legal LLM unchanged (8 files / 87 records)
    en = glob.glob(os.path.join(ROOT, "data", "english_legal_llm", "*_en_legal_llm.json"))
    if len(en) != 8 or sum(len(_read(x)["records"]) for x in en) != 87:
        problems.append("English Legal LLM must remain 8 files / 87 records")
    # full Arabic LLM-ready = 281; old Arabic LLM = 8/80; Chinese = 5/23
    if not os.path.exists(OA_LLM) or len(_read(OA_LLM)["records"]) != TARGET:
        problems.append("full Arabic LLM-ready layer must remain 281 records")
    old_ar = glob.glob(os.path.join(ROOT, "data", "arabic_legal_llm", "*_ar_legal_llm.json"))
    if len(old_ar) != 8 or sum(len(_read(x)["records"]) for x in old_ar) != 80:
        problems.append("old Arabic Legal LLM must remain 8 files / 80 records")
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    if len(zh) != 5 or sum(len(_read(x)["records"]) for x in zh) != 23:
        problems.append("Chinese Legal LLM must remain 5 files / 23 records")

    # official Arabic source unchanged
    if os.path.exists(CAND):
        c = _read(CAND)
        if len(c.get("articles", [])) != TARGET:
            problems.append("official Arabic candidate must still have 281 records")
        if c.get("verification_status") != "ingested_unverified":
            problems.append("official Arabic candidate verification_status must be unchanged")
    else:
        problems.append("official Arabic candidate file missing")

    # OCR reports/queues unchanged in shape
    q = os.path.join(ROOT, "reports", "official_arabic_verification", "manual_review_queue.json")
    if os.path.exists(q) and len(_read(q).get("entries", [])) != TARGET:
        problems.append("manual_review_queue must remain 281 entries (unchanged)")

    print("=" * 60)
    print("Full official English reference alignment validation (281 articles)")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] 281 English reference records (articles 1..281, no gaps/dups); schema-valid; "
          "english_source_status=official_guidance_translation; governing=ar; "
          "manual_review_status=needs_manual_check; Bureau of Experts / Official Translation "
          "Department; no binding/governing/verified overclaim; no legal-rule/LLM-ready fields; "
          "existing 87-record split layer + English/Arabic/Chinese layers + Arabic source "
          "unchanged.")
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
