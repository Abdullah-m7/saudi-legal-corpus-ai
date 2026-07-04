#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the FULL official English Legal LLM-ready layer (281 articles).

Confirms the layer carries the EXACT english_reference_text from the full English reference
alignment (verbatim, hash-checked) as legal_rule_text_en, is schema-valid and LLM/RAG-ready,
invents no legal analysis, uses no Arabic-rewrite / Chinese / OCR text, makes no binding/governing
overclaim, carries the official-guidance trust posture, and touches no protected layer.

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "official_english_legal_llm.schema.json")
DATA = os.path.join(ROOT, "data", "official_english_legal_llm",
                    "companies_law_m132_1443_official_english_legal_llm_001_281.json")
REF = os.path.join(ROOT, "data", "english_reference",
                   "companies_law_m132_1443_en_reference_001_281.json")
OA_LLM = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
CAND = os.path.join(ROOT, "data", "official_arabic",
                    "companies_law_m132_1443_official_arabic_user_provided.json")

TARGET = 281
BANNED = ("binding english text", "governing english text", "english is binding",
          "binding_translation", "verified translation", "unofficial_translation")
# Forbidden record-field substrings: no summaries, no Arabic-legal-text, no Chinese, no OCR text.
FORBIDDEN_FIELD_SUBSTRINGS = ("legal_rule_summary", "summary_en", "official_text_ar",
                              "_ar", "_zh", "arabic", "chinese", "ocr_text", "ocr_snippet",
                              "snippet")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _sha256(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


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
        problems.append("missing schema: schemas/official_english_legal_llm.schema.json")
    if not os.path.exists(DATA):
        problems.append("missing data file: %s" % os.path.relpath(DATA, ROOT))
    if not os.path.exists(REF):
        problems.append("missing source reference: %s" % os.path.relpath(REF, ROOT))
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1

    doc = _read(DATA)
    records = doc.get("records", [])
    ref_by = {r["article_number"]: r for r in _read(REF)["records"]}

    # counts / ordering
    if len(records) != TARGET:
        problems.append("expected 281 records (got %d)" % len(records))
    if [r.get("article_number") for r in records] != list(range(1, TARGET + 1)):
        problems.append("article_number must be exactly 1..281 in order")

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

    # forbidden fields within records (no summary / Arabic / Chinese / OCR fields)
    rec_keys = set()
    _all_keys(records, rec_keys)
    for k in rec_keys:
        kl = k.lower()
        for bad in FORBIDDEN_FIELD_SUBSTRINGS:
            if bad in kl:
                problems.append("forbidden record field present: %r (matches %r)" % (k, bad))
                break
    if "legal_rule_summary_en" in json.dumps(records, ensure_ascii=False):
        problems.append("records must not contain legal_rule_summary_en")

    # per-record content vs reference source
    for r in records:
        n = r.get("article_number")
        sr = ref_by.get(n)
        if r.get("record_type") != "official_english_guidance_article":
            problems.append("art %s record_type must be official_english_guidance_article" % n)
        if r.get("language") != "en":
            problems.append("art %s language must be en" % n)
        if r.get("governing_text_language") != "ar":
            problems.append("art %s governing_text_language must be ar" % n)
        if sr is None:
            problems.append("art %s missing in source reference" % n)
            continue
        if r.get("legal_rule_text_en") != sr.get("english_reference_text"):
            problems.append("art %s legal_rule_text_en != source english_reference_text" % n)
        if r.get("legal_rule_text_hash_sha256") != _sha256(sr.get("english_reference_text", "")):
            problems.append("art %s legal_rule_text_hash_sha256 mismatch" % n)
        if r.get("article_heading_en") != sr.get("article_heading_en"):
            problems.append("art %s article_heading_en != source" % n)
        st = r.get("source_trust", {})
        want = {
            "english_source_status": "official_guidance_translation",
            "source_authority": "Bureau of Experts at the Council of Ministers",
            "department": "Official Translation Department",
            "source_file": "inputs/companies_law_official_english_guidance.pdf",
            "source_reference_file":
                "data/english_reference/companies_law_m132_1443_en_reference_001_281.json",
            "governing_text_language": "ar",
            "manual_review_status": "needs_manual_check",
            "guidance_note":
                "This translation is provided for guidance. The governing text is the Arabic text.",
            "binding_status": "guidance_only_not_binding",
        }
        for k, val in want.items():
            if st.get(k) != val:
                problems.append("art %s source_trust.%s must be %r (got %r)"
                                % (n, k, val, st.get(k)))

    # no binding/governing overclaim anywhere
    blob = json.dumps(doc, ensure_ascii=False).lower()
    for term in BANNED:
        if term in blob:
            problems.append("banned overclaim term present: %r" % term)

    # source reference + other layers unchanged
    if len(_read(REF)["records"]) != TARGET:
        problems.append("full English reference source must remain 281 records")
    if not os.path.exists(OA_LLM) or len(_read(OA_LLM)["records"]) != TARGET:
        problems.append("full Arabic LLM-ready layer must remain 281 records")
    old_en = glob.glob(os.path.join(ROOT, "data", "english_legal_llm", "*_en_legal_llm.json"))
    if len(old_en) != 8 or sum(len(_read(x)["records"]) for x in old_en) != 87:
        problems.append("old English Legal LLM must remain 8 files / 87 records")
    old_ar = glob.glob(os.path.join(ROOT, "data", "arabic_legal_llm", "*_ar_legal_llm.json"))
    if len(old_ar) != 8 or sum(len(_read(x)["records"]) for x in old_ar) != 80:
        problems.append("old Arabic Legal LLM must remain 8 files / 80 records")
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    if len(zh) != 5 or sum(len(_read(x)["records"]) for x in zh) != 23:
        problems.append("Chinese Legal LLM must remain 5 files / 23 records")

    # existing 87-record split English reference layer intact
    ref_dir = os.path.join(ROOT, "data", "english_reference")
    split = glob.glob(os.path.join(ref_dir, "book*_en_reference.json"))
    if sum(len(_read(p)["records"]) for p in split) != 87:
        problems.append("existing split English reference must remain 87 records")

    # official Arabic source unchanged
    if os.path.exists(CAND):
        c = _read(CAND)
        if len(c.get("articles", [])) != TARGET:
            problems.append("official Arabic candidate must still have 281 records")
        if c.get("verification_status") != "ingested_unverified":
            problems.append("official Arabic candidate verification_status must be unchanged")
    else:
        problems.append("official Arabic candidate file missing")

    # existing data/articles unchanged (present)
    for fname in ("book1_articles_001_034.json", "book2_articles_035_050.json",
                  "book3_articles_051_057.json"):
        if not os.path.exists(os.path.join(ROOT, "data", "articles", fname)):
            problems.append("existing data/articles file missing: %s" % fname)

    # OCR reports/queues unchanged in shape
    q = os.path.join(ROOT, "reports", "official_arabic_verification", "manual_review_queue.json")
    if os.path.exists(q) and len(_read(q).get("entries", [])) != TARGET:
        problems.append("manual_review_queue must remain 281 entries (unchanged)")

    print("=" * 60)
    print("Full official English Legal LLM-ready layer validation (281 articles)")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] 281 records (articles 1..281); legal_rule_text_en exact + hash-verified against "
          "the full English reference; schema-valid; record_type=official_english_guidance_"
          "article; language=en/governing=ar; no summary/Arabic/Chinese/OCR fields; no binding/"
          "governing overclaim; guidance_only_not_binding; reference 281 + Arabic 281 + old "
          "English 8/87 + old Arabic 8/80 + Chinese 5/23 + Arabic source unchanged.")
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
