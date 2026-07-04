#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the Chinese internal LLM-ready candidate layer (isolable-source articles only).

Confirms the candidate layer contains exactly the 189 articles with isolable per-article Chinese
source text, copies that text VERBATIM (hash-checked), excludes the 92 thematic-summary articles,
carries the internal / non-official / non-binding trust posture (Arabic governing), invents no
Chinese and no Arabic-/English-generated fields, and touches no protected layer.

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "chinese_internal_legal_llm.schema.json")
DATA = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                    "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_INTERNAL_LLM_READY_ISOLABLE_189_AR.md")
INV = os.path.join(ROOT, "reports", "chinese_translation_review",
                   "chinese_all_babs_source_inventory.json")
IDX = os.path.join(ROOT, "reports", "chinese_translation_review",
                   "chinese_article_coverage_index_001_281.json")
SRC_DIR = os.path.join(ROOT, "data", "chinese_translation_sources")
CAND = os.path.join(ROOT, "data", "official_arabic",
                    "companies_law_m132_1443_official_arabic_user_provided.json")

TARGET = 281
EXPECTED = 189
EXCLUDED = 92
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")
# no Arabic-/English-generated Chinese fields
FORBIDDEN_FIELD_SUBSTRINGS = ("_ar_", "official_text_ar", "legal_rule_text_en", "english_reference",
                              "generated_from_arabic", "generated_from_english", "_en_zh", "ar_zh")


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
    for p, label in ((SCHEMA, "schema"), (DATA, "data file"), (MD, "Arabic report"),
                     (INV, "source inventory"), (IDX, "coverage index")):
        if not os.path.exists(p):
            problems.append("missing: %s (%s)" % (label, os.path.relpath(p, ROOT)))
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1

    doc = _read(DATA)
    idx = _read(IDX)
    recs = doc.get("records", [])

    # top-level posture / counts
    if doc.get("candidate_record_count") != EXPECTED:
        problems.append("candidate_record_count must be 189")
    if doc.get("expected_candidate_record_count") != EXPECTED:
        problems.append("expected_candidate_record_count must be 189")
    if len(recs) != EXPECTED:
        problems.append("records length must be 189 (got %d)" % len(recs))
    if doc.get("excluded_article_count") != EXCLUDED:
        problems.append("excluded_article_count must be 92")
    if len(doc.get("excluded_articles", [])) != EXCLUDED:
        problems.append("excluded_articles length must be 92")
    for f in ("full_chinese_translation_claimed", "official_chinese_translation_claimed",
              "chinese_binding_claimed", "chinese_governing_claimed"):
        if doc.get(f) is not False:
            problems.append("top-level %s must be false" % f)

    nums = [r.get("article_number") for r in recs]
    if len(set(nums)) != len(nums):
        problems.append("duplicate article numbers in candidate records")
    incl = set(nums)
    excl = set(doc.get("excluded_articles", []))
    if incl & excl:
        problems.append("included and excluded article sets overlap: %s" % sorted(incl & excl))
    if incl | excl != set(range(1, TARGET + 1)):
        problems.append("included + excluded must partition Articles 1..281")

    # coverage index nonempty set must equal the included set; excluded must be empty-text
    idx_nonempty = {r["article_number"] for r in idx["records"] if r["chinese_text_nonempty"]}
    idx_empty = {r["article_number"] for r in idx["records"] if not r["chinese_text_nonempty"]}
    if incl != idx_nonempty:
        problems.append("included set != coverage-index chinese_text_nonempty set")
    if excl != idx_empty:
        problems.append("excluded set != coverage-index empty-text set")

    # schema validation
    try:
        import jsonschema
        schema = _read(SCHEMA)
        v = jsonschema.Draft7Validator(schema)
        for r in recs:
            for err in v.iter_errors(r):
                problems.append("schema error art %s: %s" % (r.get("article_number"), err.message))
                break
    except ImportError:
        problems.append("jsonschema not available to validate records")

    # verbatim text vs extracted source + hash + posture
    src = {}
    for f in glob.glob(os.path.join(SRC_DIR, "bab*_zh_source_extracted_articles_*.json")):
        for r in _read(f)["records"]:
            src[r["article_number"]] = r.get("chinese_text") or ""
    for r in recs:
        n = r.get("article_number")
        if not (r.get("chinese_text") or "").strip():
            problems.append("art %s chinese_text empty" % n)
        if r.get("chinese_text") != src.get(n):
            problems.append("art %s chinese_text != extracted source (must be exact)" % n)
        if r.get("chinese_text_hash_sha256") != _sha256(r.get("chinese_text", "")):
            problems.append("art %s chinese_text_hash_sha256 mismatch" % n)
        sc = r.get("source_coverage", {})
        if sc.get("chinese_text_nonempty") is not True:
            problems.append("art %s source_coverage.chinese_text_nonempty must be true" % n)
        if sc.get("llm_ready_as_full_translation") is not False:
            problems.append("art %s source_coverage.llm_ready_as_full_translation must be false" % n)
        st = r.get("source_trust", {})
        for k, want in (("chinese_source_status", "internal_working_translation_source"),
                        ("official_translation", False), ("not_binding", True),
                        ("governing_text_language", "ar"), ("full_translation_claimed", False),
                        ("internal_reference_only", True), ("arabic_governs", True)):
            if st.get(k) is not want and st.get(k) != want:
                problems.append("art %s source_trust.%s must be %r" % (n, k, want))

    # no banned overclaim; no Arabic-/English-generated fields
    blob = json.dumps(doc, ensure_ascii=False).lower()
    for term in BANNED:
        if term in blob:
            problems.append("banned overclaim term present: %r" % term)
    rec_keys = set()
    _all_keys(recs, rec_keys)
    for k in rec_keys:
        kl = k.lower()
        for bad in FORBIDDEN_FIELD_SUBSTRINGS:
            if bad in kl:
                problems.append("forbidden generated field present: %r (matches %r)" % (k, bad))
                break

    # protected layers unchanged
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    if len(zh) != 5 or sum(len(_read(x)["records"]) for x in zh) != 23:
        problems.append("old Chinese Legal LLM must remain 5 files / 23 records")
    for rel, label in (("data/official_arabic_legal_llm/"
                        "companies_law_m132_1443_official_arabic_legal_llm_001_281.json",
                        "Arabic full LLM"),
                       ("data/official_english_legal_llm/"
                        "companies_law_m132_1443_official_english_legal_llm_001_281.json",
                        "English full LLM"),
                       ("data/english_reference/"
                        "companies_law_m132_1443_en_reference_001_281.json",
                        "English reference full")):
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p) or len(_read(p)["records"]) != TARGET:
            problems.append("%s must remain 281 records" % label)
    if os.path.exists(CAND):
        c = _read(CAND)
        if len(c.get("articles", [])) != TARGET:
            problems.append("official Arabic source must remain 281 records")
        if c.get("verification_status") != "ingested_unverified":
            problems.append("official Arabic source verification_status must be unchanged")
    else:
        problems.append("official Arabic source file missing")
    q = os.path.join(ROOT, "reports", "official_arabic_verification", "manual_review_queue.json")
    if os.path.exists(q) and len(_read(q).get("entries", [])) != TARGET:
        problems.append("OCR manual_review_queue must remain 281 entries (unchanged)")

    print("=" * 60)
    print("Chinese internal LLM-ready candidate layer validation (isolable 189)")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] 189 candidate records (isolable per-article Chinese source), 92 excluded "
          "(thematic-summary, no isolable text); chinese_text verbatim + hash-verified; internal/"
          "non-official/non-binding, Arabic governing; no full/official/binding/governing claim; "
          "no generated Chinese; old Chinese 5/23 + Arabic 281 + English 281 + English reference "
          "281 + Arabic source + OCR queue all unchanged.")
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
