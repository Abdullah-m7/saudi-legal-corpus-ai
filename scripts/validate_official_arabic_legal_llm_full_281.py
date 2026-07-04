#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the FULL official Arabic Legal LLM-ready layer (281 articles).

Confirms the layer carries the EXACT official_text_ar from the ingested BOE owner-provided
candidate (verbatim, hash-checked), is schema-valid and LLM/RAG-ready, invents no legal analysis,
uses no OCR / English / Chinese text, carries the BOE owner-provided trust posture, and touches no
protected layer.

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "official_arabic_legal_llm.schema.json")
DATA = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                    "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
SRC = os.path.join(ROOT, "data", "official_arabic",
                   "companies_law_m132_1443_official_arabic_user_provided.json")

TARGET = 281
# Precise forbidden record-field substrings. NOTE: bare "ocr" is intentionally NOT here — the
# required trust label `ocr_role` legitimately contains it; we forbid OCR *text* fields instead.
FORBIDDEN_FIELD_SUBSTRINGS = ("legal_rule_summary", "summary_ar", "ocr_text", "ocr_snippet",
                              "snippet", "_en", "_zh", "english", "chinese")


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
        problems.append("missing schema: schemas/official_arabic_legal_llm.schema.json")
    if not os.path.exists(DATA):
        problems.append("missing data file: %s" % os.path.relpath(DATA, ROOT))
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1

    doc = _read(DATA)
    records = doc.get("records", [])
    src = _read(SRC) if os.path.exists(SRC) else None
    src_by = {a["article_number"]: a for a in src["articles"]} if src else {}

    # schema validation (each record)
    try:
        import jsonschema
        schema = _read(SCHEMA)
        validator = jsonschema.Draft7Validator(schema)
        for r in records:
            for err in validator.iter_errors(r):
                problems.append("schema error art %s: %s"
                                % (r.get("article_number"), err.message))
                break
    except ImportError:
        problems.append("jsonschema not available to validate records")

    # counts / ordering
    if len(records) != TARGET:
        problems.append("expected 281 records (got %d)" % len(records))
    if [r.get("article_number") for r in records] != list(range(1, TARGET + 1)):
        problems.append("article_number must be exactly 1..281 in order")

    # forbidden fields within records (no invented analysis / OCR text / EN / ZH text fields).
    # Scoped to record keys — wrapper metadata may carry an English descriptor label.
    rec_keys = set()
    _all_keys(records, rec_keys)
    for k in rec_keys:
        kl = k.lower()
        for bad in FORBIDDEN_FIELD_SUBSTRINGS:
            if bad in kl:
                problems.append("forbidden record field present: %r (matches %r)" % (k, bad))
                break
    if "legal_rule_summary_ar" in json.dumps(records, ensure_ascii=False):
        problems.append("records must not contain legal_rule_summary_ar")

    # per-record content checks vs source
    for r in records:
        n = r.get("article_number")
        a = src_by.get(n)
        if r.get("record_type") != "official_arabic_article":
            problems.append("art %s record_type must be official_arabic_article" % n)
        if r.get("language") != "ar":
            problems.append("art %s language must be ar" % n)
        if r.get("governing_text_language") != "ar":
            problems.append("art %s governing_text_language must be ar" % n)
        if a is None:
            problems.append("art %s missing in source candidate" % n)
            continue
        if r.get("official_text_ar") != a.get("official_text_ar"):
            problems.append("art %s official_text_ar != source (must be exact)" % n)
        if r.get("official_text_hash_sha256") != _sha256(a.get("official_text_ar", "")):
            problems.append("art %s official_text_hash_sha256 mismatch" % n)
        if r.get("article_title_ar") != a.get("article_title_ar"):
            problems.append("art %s article_title_ar != source" % n)
        st = r.get("source_trust", {})
        trust_want = {
            "source_authority": "Bureau of Experts at the Council of Ministers",
            "source_authority_ar": "هيئة الخبراء بمجلس الوزراء",
            "source_status": "owner_provided_from_official_boe_source",
            "source_packet_status": "official_boe_owner_provided",
            "controlling_source_basis": "owner_provided_boe_text_plus_pdf_packet",
            "ocr_role": "supporting_artifact_only_not_controlling_gate",
            "text_type": "official_arabic_statutory_text",
            "article_by_article_verified": False,
            "verification_status":
                "official_boe_source_packet_owner_provided_not_live_html_verified",
        }
        for k, v in trust_want.items():
            if st.get(k) != v:
                problems.append("art %s source_trust.%s must be %r (got %r)"
                                % (n, k, v, st.get(k)))

    # no verified_against_official_gazette anywhere
    if "verified_against_official_gazette" in json.dumps(doc, ensure_ascii=False):
        problems.append("no record may claim verified_against_official_gazette")

    # candidate source untouched
    if src is None:
        problems.append("candidate source file missing")
    else:
        if len(src.get("articles", [])) != TARGET:
            problems.append("candidate source must still have 281 records")
        if src.get("verification_status") != "ingested_unverified":
            problems.append("candidate source verification_status must remain ingested_unverified")

    # existing layers unchanged in shape
    old_ar = glob.glob(os.path.join(ROOT, "data", "arabic_legal_llm", "*_ar_legal_llm.json"))
    if len(old_ar) != 8 or sum(len(_read(x)["records"]) for x in old_ar) != 80:
        problems.append("old Arabic Legal LLM must remain 8 files / 80 records")
    en = glob.glob(os.path.join(ROOT, "data", "english_legal_llm", "*_en_legal_llm.json"))
    if len(en) != 8 or sum(len(_read(x)["records"]) for x in en) != 87:
        problems.append("English Legal LLM must remain 8 files / 87 records")
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    if len(zh) != 5 or sum(len(_read(x)["records"]) for x in zh) != 23:
        problems.append("Chinese Legal LLM must remain 5 files / 23 records")
    ref = os.path.join(ROOT, "data", "english_reference")
    for fname, exp in (("book1_en_reference.json", list(range(1, 35))),
                       ("book2_en_reference.json", list(range(35, 51))),
                       ("book3_en_reference.json", list(range(51, 58)))):
        pth = os.path.join(ref, fname)
        if os.path.exists(pth) and [x["article_number"] for x in _read(pth)["records"]] != exp:
            problems.append("official English reference changed: %s" % fname)
    for fname in ("book1_articles_001_034.json", "book2_articles_035_050.json",
                  "book3_articles_051_057.json"):
        if not os.path.exists(os.path.join(ROOT, "data", "articles", fname)):
            problems.append("existing data/articles file missing: %s" % fname)
    # OCR reports/queues present & unchanged in shape (still 281 queue entries)
    q = os.path.join(ROOT, "reports", "official_arabic_verification", "manual_review_queue.json")
    if os.path.exists(q) and len(_read(q).get("entries", [])) != TARGET:
        problems.append("manual_review_queue must remain 281 entries (unchanged)")

    print("=" * 60)
    print("Official Arabic FULL LLM-ready layer validation (281 articles)")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] 281 records (articles 1..281); official_text_ar exact + hash-verified against "
          "the BOE owner-provided candidate; schema-valid; record_type=official_arabic_article; "
          "language/governing=ar; no legal-summary/OCR/EN/ZH fields; BOE owner-provided trust "
          "posture; article_by_article_verified=false; nothing verified; old Arabic 8/80, English "
          "8/87, Chinese 5/23 and other layers unchanged.")
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
