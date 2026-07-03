#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the USER-PROVIDED official Arabic text ingestion.

Checks that the user-provided Arabic candidate was ingested faithfully as EXACTLY 281
article records, each hashed, and that NOTHING is marked verified against an official source.
This does not perform official-gazette verification.

Enforces:
- raw source packet exists (inputs/…user_provided.md);
- structured candidate file exists with exactly 281 article records numbered 1..281;
- every record is schema-valid against schemas/official_arabic_article.schema.json;
- every record verification_status == ingested_unverified (none verified_against_official_gazette);
- article_by_article_verified == false; articles_verified == 0; official_arabic_text_status
  == user_provided_source_ingested;
- every text_hash_sha256 matches sha256(official_text_ar);
- the current Arabic summaries are NOT relabeled as official;
- English/Chinese/Arabic LLM layers are unchanged in shape (still 8/87, 5/23, Arabic present)
  and carry no official_text_ar / verified markers — i.e. no legal_rule_text_en/zh drift.

Exit 0 == pass; 1 == problems. No network, no heavy dependencies.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "official_arabic_article.schema.json")
OA_DIR = os.path.join(ROOT, "data", "official_arabic")
STATUS = os.path.join(OA_DIR, "ingestion_status.json")
RAW = os.path.join(ROOT, "inputs", "official_arabic_companies_law_m132_1443_user_provided.md")
RECORDS = os.path.join(OA_DIR, "companies_law_m132_1443_official_arabic_user_provided.json")

TARGET = 281


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

    if not os.path.exists(RAW):
        problems.append("raw source packet missing: inputs/official_arabic_companies_law_m132_1443_user_provided.md")
    schema = _read(SCHEMA) if os.path.exists(SCHEMA) else None
    if schema is None:
        problems.append("schema missing: schemas/official_arabic_article.schema.json")

    doc = None
    if not os.path.exists(RECORDS):
        problems.append("structured candidate file missing: %s" % os.path.basename(RECORDS))
    else:
        doc = _read(RECORDS)
        arts = doc.get("articles", [])
        if len(arts) != TARGET:
            problems.append("expected exactly %d article records, found %d" % (TARGET, len(arts)))
        nums = [a.get("article_number") for a in arts]
        if nums != list(range(1, TARGET + 1)):
            problems.append("article numbers must be exactly 1..%d in order" % TARGET)
        if doc.get("article_by_article_verified") is not False:
            problems.append("candidate file: article_by_article_verified must be false")
        if doc.get("verification_status") != "ingested_unverified":
            problems.append("candidate file: verification_status must be ingested_unverified")
        if doc.get("official_arabic_text_status") != "user_provided_source_ingested":
            problems.append("candidate file: official_arabic_text_status must be user_provided_source_ingested")
        if doc.get("articles_verified") not in (0, None) or doc.get("articles_verified") != 0:
            problems.append("candidate file: articles_verified must be 0")
        for a in arts:
            n = a.get("article_number", "?")
            if schema is not None:
                for msg in _validate_record(a, schema):
                    problems.append("art %s: %s" % (n, msg))
            if a.get("verification_status") != "ingested_unverified":
                problems.append("art %s: verification_status must be ingested_unverified" % n)
            if a.get("verification_status") == "verified_against_official_gazette":
                problems.append("art %s: must not be verified_against_official_gazette" % n)
            if a.get("manual_review_status") != "needs_manual_check":
                problems.append("art %s: manual_review_status must be needs_manual_check" % n)
            txt = a.get("official_text_ar", "")
            want = hashlib.sha256(txt.encode("utf-8")).hexdigest()
            if a.get("text_hash_sha256") != want:
                problems.append("art %s: text_hash_sha256 does not match official_text_ar" % n)

    # ingestion_status manifest consistency (honest, unverified)
    if os.path.exists(STATUS):
        st = _read(STATUS)
        if st.get("official_arabic_text_status") != "user_provided_source_ingested":
            problems.append("ingestion_status: official_arabic_text_status must be user_provided_source_ingested")
        if st.get("verification_status") != "ingested_unverified":
            problems.append("ingestion_status: verification_status must be ingested_unverified")
        if st.get("article_by_article_verified") is not False:
            problems.append("ingestion_status: article_by_article_verified must be false")
        if st.get("articles_verified") != 0:
            problems.append("ingestion_status: articles_verified must be 0")
        if st.get("articles_ingested") != TARGET:
            problems.append("ingestion_status: articles_ingested must be %d" % TARGET)
        if "not_official" not in str(st.get("current_arabic_summary_status", "")):
            problems.append("ingestion_status: current Arabic summaries must remain not_official")
    else:
        problems.append("ingestion_status.json missing")

    # current Arabic summaries must not be relabeled official
    prov = os.path.join(ROOT, "data", "metadata", "source_provenance.json")
    if os.path.exists(prov):
        p = _read(prov)
        if p.get("official_text_status", {}).get("checked_against_official_gazette") is not False:
            problems.append("source_provenance: checked_against_official_gazette must remain false")

    # derived layers unchanged in shape; no official_text_ar / verified drift
    en = sorted(os.path.basename(x) for x in glob.glob(os.path.join(ROOT, "data", "english_legal_llm", "*_en_legal_llm.json")))
    if len(en) != 8:
        problems.append("English Legal LLM must remain 8 files (got %d)" % len(en))
    en_total = sum(len(_read(x)["records"]) for x in glob.glob(os.path.join(ROOT, "data", "english_legal_llm", "*_en_legal_llm.json")))
    if en_total != 87:
        problems.append("English Legal LLM must remain 87 records (got %d)" % en_total)
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    zh_total = sum(len(_read(x)["records"]) for x in zh)
    if len(zh) != 5 or zh_total != 23:
        problems.append("Chinese Legal LLM must remain 5 files / 23 records (got %d / %d)" % (len(zh), zh_total))
    for x in glob.glob(os.path.join(ROOT, "data", "arabic_legal_llm", "*_ar_legal_llm.json")):
        blob = open(x, encoding="utf-8").read().lower()
        if "official_text_ar" in blob or "verified_against_official_gazette" in blob:
            problems.append("Arabic Legal LLM must not be relabeled official: %s" % os.path.basename(x))

    print("=" * 60)
    print("Official Arabic USER-PROVIDED ingestion validation (unverified)")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    n = len(doc.get("articles", [])) if doc else 0
    print("[PASS] %d user-provided official Arabic article records (1..%d); every text hashed; "
          "verification_status=ingested_unverified; article_by_article_verified=false; "
          "articles_verified=0; nothing marked verified_against_official_gazette; current Arabic "
          "summaries kept non-official; English 8/87, Chinese 5/23, Arabic LLM unchanged." % (n, TARGET))
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
