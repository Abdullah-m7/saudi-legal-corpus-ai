#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the Chinese Bab 1 original-PDF translation review (source-inventory stage only).

Confirms the original Bab 1 Chinese PDF was preserved, its Chinese text extracted into 34 article
records (1..34), and a meaning-vs-Arabic review produced — all under the correct trust posture
(Chinese internal/non-official/non-binding; Arabic governing), WITHOUT creating any Chinese
LLM-ready data and WITHOUT touching any protected layer.

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "inputs", "chinese_translation_source_pdfs",
                   "saudi_companies_law_ar_zh_bab1_full.pdf")
EX = os.path.join(ROOT, "data", "chinese_translation_sources",
                  "bab1_zh_source_extracted_articles_001_034.json")
RV = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "bab1_original_pdf_translation_review.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "BAB1_ORIGINAL_PDF_TRANSLATION_REVIEW_AR.md")
CAND = os.path.join(ROOT, "data", "official_arabic",
                    "companies_law_m132_1443_official_arabic_user_provided.json")

TARGET = 34
# Natural-language overclaims only. The claim FIELDS (official_chinese_translation_claimed etc.)
# are enforced =false explicitly below; their names must not trip this raw scan.
BANNED = ("chinese is binding", "chinese is governing", "official chinese translation",
          "chinese is official", "binding chinese text", "governing chinese text")
COVERAGE = {"full_or_near_full_aligned", "mostly_aligned_but_condensed",
            "summary_needs_expansion", "materially_incomplete_needs_retranslation",
            "extraction_unclear_needs_manual_review"}
RATING = {"high", "medium", "low", "extraction_unclear"}


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    problems = []

    for p, label in ((PDF, "source PDF"), (EX, "extracted JSON"), (RV, "review JSON"),
                     (MD, "Arabic report")):
        if not os.path.exists(p):
            problems.append("missing: %s (%s)" % (label, os.path.relpath(p, ROOT)))
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1

    ex = _read(EX)
    rv = _read(RV)

    # extracted posture + counts
    if ex.get("source_language") != "zh":
        problems.append("extracted source_language must be zh")
    if ex.get("governing_text_language") != "ar":
        problems.append("extracted governing_text_language must be ar")
    if ex.get("official_translation") is not False:
        problems.append("extracted official_translation must be false")
    if ex.get("not_binding") is not True:
        problems.append("extracted not_binding must be true")
    if ex.get("article_count") != TARGET:
        problems.append("extracted article_count must be 34")
    ex_nums = [r.get("article_number") for r in ex.get("records", [])]
    if ex_nums != list(range(1, TARGET + 1)):
        problems.append("extracted article numbers must be exactly 1..34 in order")
    for r in ex.get("records", []):
        if not (r.get("chinese_text") or "").strip():
            problems.append("extracted art %s has empty chinese_text" % r.get("article_number"))

    # review posture + counts
    if rv.get("governing_language") != "ar":
        problems.append("review governing_language must be ar")
    if rv.get("chinese_source_status") != "internal_working_translation_source":
        problems.append("review chinese_source_status must be internal_working_translation_source")
    if rv.get("official_chinese_translation_claimed") is not False:
        problems.append("review official_chinese_translation_claimed must be false")
    if rv.get("chinese_binding_claimed") is not False:
        problems.append("review chinese_binding_claimed must be false")
    if rv.get("full_translation_claimed") is not False:
        problems.append("review full_translation_claimed must be false")
    if rv.get("article_count") != TARGET:
        problems.append("review article_count must be 34")
    rv_nums = [r.get("article_number") for r in rv.get("records", [])]
    if rv_nums != list(range(1, TARGET + 1)):
        problems.append("review article numbers must be exactly 1..34 in order")
    for r in rv.get("records", []):
        n = r.get("article_number")
        if r.get("coverage_status") not in COVERAGE:
            problems.append("art %s coverage_status invalid: %s" % (n, r.get("coverage_status")))
        if r.get("semantic_alignment_rating") not in RATING:
            problems.append("art %s semantic_alignment_rating invalid" % n)
        if r.get("llm_ready_as_full_translation") is not False:
            problems.append("art %s llm_ready_as_full_translation must be false" % n)

    # no official/binding/governing/full-llm claim anywhere
    blob = (json.dumps(ex, ensure_ascii=False) + json.dumps(rv, ensure_ascii=False)).lower()
    for term in BANNED:
        if term in blob:
            problems.append("banned claim present: %r" % term)

    # NO Chinese LLM-ready file created in this PR (only sources/review artifacts allowed)
    if os.path.isdir(os.path.join(ROOT, "data", "official_chinese_legal_llm")):
        problems.append("no Chinese LLM-ready layer may be created in this PR")
    if "chinese_llm_ready" in blob or "official_english_guidance_article" in blob:
        problems.append("review/extracted must not create Chinese LLM-ready records")

    # protected layers unchanged
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    if len(zh) != 5 or sum(len(_read(x)["records"]) for x in zh) != 23:
        problems.append("Chinese Legal LLM must remain 5 files / 23 records")
    oa = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
    if not os.path.exists(oa) or len(_read(oa)["records"]) != 281:
        problems.append("full Arabic LLM-ready must remain 281 records")
    oe = os.path.join(ROOT, "data", "official_english_legal_llm",
                      "companies_law_m132_1443_official_english_legal_llm_001_281.json")
    if not os.path.exists(oe) or len(_read(oe)["records"]) != 281:
        problems.append("full English LLM-ready must remain 281 records")
    er = os.path.join(ROOT, "data", "english_reference",
                      "companies_law_m132_1443_en_reference_001_281.json")
    if not os.path.exists(er) or len(_read(er)["records"]) != 281:
        problems.append("full English reference must remain 281 records")
    if os.path.exists(CAND):
        c = _read(CAND)
        if len(c.get("articles", [])) != 281:
            problems.append("official Arabic source must remain 281 records")
        if c.get("verification_status") != "ingested_unverified":
            problems.append("official Arabic source verification_status must be unchanged")
    else:
        problems.append("official Arabic source file missing")
    q = os.path.join(ROOT, "reports", "official_arabic_verification", "manual_review_queue.json")
    if os.path.exists(q) and len(_read(q).get("entries", [])) != 281:
        problems.append("OCR manual_review_queue must remain 281 entries (unchanged)")

    print("=" * 60)
    print("Chinese Bab 1 original-PDF translation review validation")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] Bab1 Chinese PDF preserved + extracted (34 articles 1..34) + reviewed vs Arabic; "
          "Chinese internal/non-official/non-binding, Arabic governing; no full-LLM/official/"
          "binding claim; no Chinese LLM-ready created; Chinese 5/23 + Arabic 281 + English 281 "
          "+ English reference 281 + Arabic source + OCR queue all unchanged.")
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
