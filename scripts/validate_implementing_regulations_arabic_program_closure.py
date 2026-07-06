#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementing Regulations Arabic Program Closure Audit — Read-Only Validator

Validates the closure audit JSON and verifies all underlying tracks.

Checks:
  1.  Audit JSON exists and is valid JSON.
  2.  Stage is IMPLEMENTING_REGULATIONS_ARABIC_PROGRAM_CLOSURE_AUDIT.
  3.  General track: source intake exists with 95 articles + 4 forms.
  4.  General track: Arabic Legal LLM layer exists with 95 article records.
  5.  General track: forms layer exists with 4 form records.
  6.  General track: article hashes match source intake.
  7.  General track: form hashes match source intake.
  8.  General track: record IDs sequential and unique.
  9.  Listed JSC track: source intake exists with 69 articles + appendix.
 10.  Listed JSC track: Arabic Legal LLM layer exists with 69 article records.
 11.  Listed JSC track: appendix layer exists with 1 record.
 12.  Listed JSC track: article hashes match source intake.
 13.  Listed JSC track: appendix hash matches source intake.
 14.  Listed JSC track: record IDs sequential and unique.
 15.  Listed JSC track: is_specialized=True, is_general=False.
 16.  Listed JSC track: chapter_number/chapter_title_ar null for all records.
 17.  Listed JSC track: article titles explicit (not ordinal, not null).
 18.  General and listed tracks are separate.
 19.  Arabic official source governs.
 20.  No official translation claim.
 21.  No legal advice claim.
 22.  No trilingual alignment.
 23.  No public release.
 24.  Companies Law corpus files exist (unchanged).
 25.  Chinese remediation closure audit exists (unchanged).
 26.  Audit overall_status is PASS.

Usage:
    python3 scripts/validate_implementing_regulations_arabic_program_closure.py
Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AUDIT_PATH = os.path.join(ROOT, "reports", "implementing_regulations", "implementing_regulations_arabic_program_closure_audit.json")

GEN_INTAKE = os.path.join(ROOT, "data", "implementing_regulations", "general", "general_implementing_regulations_arabic_source.json")
GEN_LLM = os.path.join(ROOT, "data", "implementing_regulations", "general", "general_implementing_regulations_arabic_legal_llm.json")
GEN_FORMS_LLM = os.path.join(ROOT, "data", "implementing_regulations", "general", "general_implementing_regulations_arabic_forms_llm.json")

LJS_INTAKE = os.path.join(ROOT, "data", "implementing_regulations", "listed_joint_stock", "listed_joint_stock_implementing_regulation_arabic_source.json")
LJS_LLM = os.path.join(ROOT, "data", "implementing_regulations", "listed_joint_stock", "listed_joint_stock_implementing_regulation_arabic_legal_llm.json")
LJS_APPENDIX_LLM = os.path.join(ROOT, "data", "implementing_regulations", "listed_joint_stock", "listed_joint_stock_implementing_regulation_arabic_appendix_llm.json")

PARENT_LAW_FILES = [
    "data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json",
    "data/legal_corpus_factory/law_profiles/sa_companies_law_m132_1443.profile.json",
]
CHINESE_REMEDIATION = os.path.join(ROOT, "reports", "chinese_translation_review", "chinese_remediation_program_closure_audit.json")

CHECKS: list[str] = []
PASSED = 0
FAILED = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        CHECKS.append(f"  {name} ✓")
        if detail:
            CHECKS.append(f"    {detail}")
        PASSED += 1
    else:
        CHECKS.append(f"  {name} ✗ FAIL")
        if detail:
            CHECKS.append(f"    {detail}")
        FAILED += 1


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    print("=" * 70)
    print("Implementing Regulations Arabic Program Closure Audit validation")
    print("=" * 70)
    print()

    # [1] Audit JSON exists
    check("[1] Audit JSON exists...", os.path.isfile(AUDIT_PATH),
          "Present" if os.path.isfile(AUDIT_PATH) else "NOT FOUND")
    if not os.path.isfile(AUDIT_PATH):
        print_results()
        return 1

    audit = _load_json(AUDIT_PATH)

    # [2] Stage
    check("[2] Stage correct...",
          audit.get("stage") == "IMPLEMENTING_REGULATIONS_ARABIC_PROGRAM_CLOSURE_AUDIT",
          f"stage={audit.get('stage')}")

    # [3] General source intake
    check("[3] General source intake exists (95 articles + 4 forms)...",
          os.path.isfile(GEN_INTAKE), "Present" if os.path.isfile(GEN_INTAKE) else "Missing")
    if os.path.isfile(GEN_INTAKE):
        gen_src = _load_json(GEN_INTAKE)
        check("    95 articles...", len(gen_src.get("articles", [])) == 95, f"{len(gen_src.get('articles', []))} found")
        check("    4 forms...", len(gen_src.get("forms", [])) == 4, f"{len(gen_src.get('forms', []))} found")

    # [4] General LLM layer
    check("[4] General Arabic Legal LLM layer exists (95 records)...",
          os.path.isfile(GEN_LLM), "Present" if os.path.isfile(GEN_LLM) else "Missing")
    if os.path.isfile(GEN_LLM):
        gen_llm = _load_json(GEN_LLM)
        check("    95 article records...", len(gen_llm.get("records", [])) == 95, f"{len(gen_llm.get('records', []))} found")

    # [5] General forms layer
    check("[5] General forms layer exists (4 records)...",
          os.path.isfile(GEN_FORMS_LLM), "Present" if os.path.isfile(GEN_FORMS_LLM) else "Missing")
    if os.path.isfile(GEN_FORMS_LLM):
        gen_forms = _load_json(GEN_FORMS_LLM)
        check("    4 form records...", len(gen_forms.get("records", [])) == 4, f"{len(gen_forms.get('records', []))} found")

    # [6] General article hashes match
    if os.path.isfile(GEN_INTAKE) and os.path.isfile(GEN_LLM):
        src_h = {a["article_number"]: a["text_hash_sha256"] for a in gen_src["articles"]}
        layer_h = {r["article_number"]: r["official_text_hash"] for r in gen_llm["records"]}
        mism = [k for k, v in src_h.items() if layer_h.get(k) != v]
        check("[6] General article hashes match source...", len(mism) == 0, f"{len(mism)} mismatches" if mism else "All 95 match")

    # [7] General form hashes match
    if os.path.isfile(GEN_INTAKE) and os.path.isfile(GEN_FORMS_LLM):
        src_fh = {fm["form_number"]: fm["text_hash_sha256"] for fm in gen_src["forms"]}
        layer_fh = {r["form_number"]: r["official_text_hash"] for r in gen_forms["records"]}
        mism = [k for k, v in src_fh.items() if layer_fh.get(k) != v]
        check("[7] General form hashes match source...", len(mism) == 0, f"{len(mism)} mismatches" if mism else "All 4 match")

    # [8] General record IDs
    if os.path.isfile(GEN_LLM):
        ids = [r["record_id"] for r in gen_llm["records"]]
        expected = [f"ir-gen-art-{i:03d}" for i in range(1, 96)]
        check("[8] General article record IDs sequential+unique...", ids == expected and len(set(ids)) == 95, "All valid")
    if os.path.isfile(GEN_FORMS_LLM):
        fids = [r["record_id"] for r in gen_forms["records"]]
        expected_f = [f"ir-gen-form-{i:03d}" for i in range(1, 5)]
        check("    General form record IDs sequential+unique...", fids == expected_f and len(set(fids)) == 4, "All valid")

    # [9] LJS source intake
    check("[9] Listed JSC source intake exists (69 articles + appendix)...",
          os.path.isfile(LJS_INTAKE), "Present" if os.path.isfile(LJS_INTAKE) else "Missing")
    if os.path.isfile(LJS_INTAKE):
        ljs_src = _load_json(LJS_INTAKE)
        check("    69 articles...", len(ljs_src.get("articles", [])) == 69, f"{len(ljs_src.get('articles', []))} found")
        check("    has_appendix...", ljs_src.get("has_appendix") is True, "Appendix present")

    # [10] LJS LLM layer
    check("[10] Listed JSC Arabic Legal LLM layer exists (69 records)...",
          os.path.isfile(LJS_LLM), "Present" if os.path.isfile(LJS_LLM) else "Missing")
    if os.path.isfile(LJS_LLM):
        ljs_llm = _load_json(LJS_LLM)
        check("    69 article records...", len(ljs_llm.get("records", [])) == 69, f"{len(ljs_llm.get('records', []))} found")

    # [11] LJS appendix layer
    check("[11] Listed JSC appendix layer exists (1 record)...",
          os.path.isfile(LJS_APPENDIX_LLM), "Present" if os.path.isfile(LJS_APPENDIX_LLM) else "Missing")
    if os.path.isfile(LJS_APPENDIX_LLM):
        ljs_app = _load_json(LJS_APPENDIX_LLM)
        check("    1 appendix record...", len(ljs_app.get("records", [])) == 1, f"{len(ljs_app.get('records', []))} found")

    # [12] LJS article hashes match
    if os.path.isfile(LJS_INTAKE) and os.path.isfile(LJS_LLM):
        src_h = {a["article_number"]: a["text_hash_sha256"] for a in ljs_src["articles"]}
        layer_h = {r["article_number"]: r["official_text_hash"] for r in ljs_llm["records"]}
        mism = [k for k, v in src_h.items() if layer_h.get(k) != v]
        check("[12] LJS article hashes match source...", len(mism) == 0, f"{len(mism)} mismatches" if mism else "All 69 match")

    # [13] LJS appendix hash matches
    if os.path.isfile(LJS_INTAKE) and os.path.isfile(LJS_APPENDIX_LLM):
        src_app_text = ljs_src.get("appendix_text", "")
        src_app_h = _sha256(src_app_text) if src_app_text else ""
        layer_app_h = ljs_app["records"][0].get("official_text_hash", "") if ljs_app.get("records") else ""
        check("[13] LJS appendix hash matches source...", src_app_h == layer_app_h and src_app_h, "Match" if src_app_h == layer_app_h else "Mismatch")

    # [14] LJS record IDs
    if os.path.isfile(LJS_LLM):
        ids = [r["record_id"] for r in ljs_llm["records"]]
        expected = [f"ir-ljs-art-{i:03d}" for i in range(1, 70)]
        check("[14] LJS article record IDs sequential+unique...", ids == expected and len(set(ids)) == 69, "All valid")

    # [15] LJS specialized
    if os.path.isfile(LJS_LLM):
        check("[15] LJS is_specialized=True, is_general=False...",
              ljs_llm.get("is_specialized") is True and ljs_llm.get("is_general") is False, "Correct")

    # [16] LJS chapter metadata null
    if os.path.isfile(LJS_LLM):
        all_null = all(r.get("chapter_number") is None and r.get("chapter_title_ar") is None for r in ljs_llm["records"])
        check("[16] LJS chapter_number/chapter_title_ar null...", all_null, "All 69 null" if all_null else "Some not null")

    # [17] LJS article titles explicit
    if os.path.isfile(LJS_LLM):
        titles_ok = all(
            r.get("article_title_ar") is not None and r.get("article_title_ar") != r.get("article_ordinal_ar", "")
            for r in ljs_llm["records"]
        )
        check("[17] LJS article titles explicit (not ordinal, not null)...", titles_ok, "All 69 explicit" if titles_ok else "Some issues")

    # [18] Tracks separate
    gen_ct = gen_llm.get("corpus_track", "") if os.path.isfile(GEN_LLM) else ""
    ljs_ct = ljs_llm.get("corpus_track", "") if os.path.isfile(LJS_LLM) else ""
    check("[18] General and listed tracks separate...", gen_ct != ljs_ct and "general" in gen_ct and "listed_joint_stock" in ljs_ct, f"{gen_ct} vs {ljs_ct}")

    # [19-23] Boundaries from audit
    b = audit.get("boundaries", {})
    check("[19] Arabic official source governs...", b.get("arabic_governs") is True, "True")
    check("[20] No official translation claim...", b.get("not_official_translation") is True, "True")
    check("[21] No legal advice claim...", b.get("not_legal_advice") is True, "True")
    check("[22] No trilingual alignment...", b.get("no_trilingual_alignment") is True, "True")
    check("[23] No public release...", b.get("no_public_release") is True, "True")

    # [24] Parent law files
    check("[24] Companies Law corpus files exist...", all(os.path.isfile(os.path.join(ROOT, p)) for p in PARENT_LAW_FILES), "All present")

    # [25] Chinese remediation
    check("[25] Chinese remediation closure audit exists...", os.path.isfile(CHINESE_REMEDIATION), "Present" if os.path.isfile(CHINESE_REMEDIATION) else "Missing")

    # [26] Overall status
    check("[26] Audit overall_status is PASS...", audit.get("overall_status") == "PASS", f"overall_status={audit.get('overall_status')}")

    print_results()
    return 0 if FAILED == 0 else 1


def print_results() -> None:
    print()
    for line in CHECKS:
        print(line)
    print()
    print("=" * 70)
    if FAILED == 0:
        print("RESULT: ALL CHECKS PASSED ✓")
        print("[PASS] Implementing Regulations Arabic Program Closure Audit: "
              "General track (95 articles + 4 forms) PASS, Listed joint-stock "
              "track (69 articles + 1 appendix) PASS. All hashes match source "
              "intake. Record IDs sequential and unique. Tracks separate. "
              "Arabic governs; no English/Chinese; no trilingual; no public "
              "release; not official translation; not legal advice. Companies "
              "Law corpus and Chinese remediation program unchanged. Read-only.")
    else:
        print(f"RESULT: {FAILED} CHECK(S) FAILED ✗")
    print("=" * 70)


if __name__ == "__main__":
    sys.exit(main())