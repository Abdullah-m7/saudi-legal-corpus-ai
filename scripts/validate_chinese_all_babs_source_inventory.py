#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the Chinese all-Babs (1-14) source coverage inventory (source-inventory stage only).

Confirms all 14 Bab PDFs are preserved, per-Bab Chinese text extracted, and a complete Articles
1-281 coverage inventory produced under the correct trust posture (Chinese internal / non-official
/ non-binding; Arabic governing), WITHOUT creating any Chinese LLM-ready data and WITHOUT touching
any protected layer.

Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR = os.path.join(ROOT, "inputs", "chinese_translation_source_pdfs")
SRC_DIR = os.path.join(ROOT, "data", "chinese_translation_sources")
RV_DIR = os.path.join(ROOT, "reports", "chinese_translation_review")
INV = os.path.join(RV_DIR, "chinese_all_babs_source_inventory.json")
IDX = os.path.join(RV_DIR, "chinese_article_coverage_index_001_281.json")
MD = os.path.join(RV_DIR, "CHINESE_ALL_BABS_SOURCE_INVENTORY_AR.md")
BAB1_EX = os.path.join(SRC_DIR, "bab1_zh_source_extracted_articles_001_034.json")
BAB1_REVIEW = os.path.join(RV_DIR, "bab1_original_pdf_translation_review.json")
CAND = os.path.join(ROOT, "data", "official_arabic",
                    "companies_law_m132_1443_official_arabic_user_provided.json")

TARGET = 281
# bab_number: (lo, hi, pdf_basename, extracted_basename)
BABS = {
    1: (1, 34, "saudi_companies_law_ar_zh_bab1_full.pdf",
        "bab1_zh_source_extracted_articles_001_034.json"),
    2: (35, 50, "saudi_companies_law_ar_zh_bab2_full.pdf",
        "bab2_zh_source_extracted_articles_035_050.json"),
    3: (51, 57, "saudi_companies_law_ar_zh_bab3.pdf",
        "bab3_zh_source_extracted_articles_051_057.json"),
    4: (58, 137, "saudi_companies_law_ar_zh_bab4.pdf",
        "bab4_zh_source_extracted_articles_058_137.json"),
    5: (138, 155, "saudi_companies_law_ar_zh_bab5.pdf",
        "bab5_zh_source_extracted_articles_138_155.json"),
    6: (156, 184, "saudi_companies_law_ar_zh_bab6.pdf",
        "bab6_zh_source_extracted_articles_156_184.json"),
    7: (185, 196, "saudi_companies_law_ar_zh_bab7.pdf",
        "bab7_zh_source_extracted_articles_185_196.json"),
    8: (197, 215, "saudi_companies_law_ar_zh_bab8.pdf",
        "bab8_zh_source_extracted_articles_197_215.json"),
    9: (216, 219, "saudi_companies_law_ar_zh_bab9.pdf",
        "bab9_zh_source_extracted_articles_216_219.json"),
    10: (220, 234, "saudi_companies_law_ar_zh_bab10.pdf",
         "bab10_zh_source_extracted_articles_220_234.json"),
    11: (235, 241, "saudi_companies_law_ar_zh_bab11.pdf",
         "bab11_zh_source_extracted_articles_235_241.json"),
    12: (242, 259, "saudi_companies_law_ar_zh_bab12.pdf",
         "bab12_zh_source_extracted_articles_242_259.json"),
    13: (260, 271, "saudi_companies_law_ar_zh_bab13.pdf",
         "bab13_zh_source_extracted_articles_260_271.json"),
    14: (272, 281, "saudi_companies_law_ar_zh_bab14.pdf",
         "bab14_zh_source_extracted_articles_272_281.json"),
}
BANNED = ("chinese is binding", "chinese is governing", "official chinese translation",
          "chinese is official", "binding chinese text", "governing chinese text")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _bab_of(n):
    for b, (lo, hi, _, _) in BABS.items():
        if lo <= n <= hi:
            return b
    return None


def main() -> int:
    problems = []

    # PDFs + Bab 1 existing artifacts + per-Bab extracted files + inventory/index/report
    for b, (lo, hi, pdf, exbase) in BABS.items():
        if not os.path.exists(os.path.join(PDF_DIR, pdf)):
            problems.append("missing source PDF for Bab %d: %s" % (b, pdf))
        if not os.path.exists(os.path.join(SRC_DIR, exbase)):
            problems.append("missing extracted JSON for Bab %d: %s" % (b, exbase))
    for p, label in ((BAB1_EX, "Bab1 extracted"), (BAB1_REVIEW, "Bab1 review"),
                     (INV, "master inventory"), (IDX, "coverage index"), (MD, "Arabic report")):
        if not os.path.exists(p):
            problems.append("missing: %s (%s)" % (label, os.path.relpath(p, ROOT)))
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1

    inv = _read(INV)
    idx = _read(IDX)

    # inventory top-level posture / counts
    if inv.get("source_pdf_count") != 14:
        problems.append("inventory source_pdf_count must be 14")
    if inv.get("expected_bab_count") != 14:
        problems.append("inventory expected_bab_count must be 14")
    if inv.get("expected_article_total") != TARGET:
        problems.append("inventory expected_article_total must be 281")
    if inv.get("governing_language") != "ar":
        problems.append("inventory governing_language must be ar")
    for f in ("official_chinese_translation_claimed", "chinese_binding_claimed",
              "full_translation_claimed", "chinese_llm_ready_created"):
        if inv.get(f) is not False:
            problems.append("inventory %s must be false" % f)
    if len(inv.get("babs", [])) != 14:
        problems.append("inventory must list 14 Babs")
    for b in inv.get("babs", []):
        bn = b.get("bab_number")
        exp = BABS.get(bn)
        if exp and b.get("expected_article_range") != [exp[0], exp[1]]:
            problems.append("Bab %s expected_article_range wrong" % bn)
        if b.get("ready_for_chinese_llm_ready") is not False:
            problems.append("Bab %s ready_for_chinese_llm_ready must be false" % bn)

    # coverage index: exactly 281, 1..281, correct Bab mapping, all llm_ready false
    recs = idx.get("records", [])
    if idx.get("article_count") != TARGET or len(recs) != TARGET:
        problems.append("coverage index must contain exactly 281 entries")
    nums = [r.get("article_number") for r in recs]
    if nums != list(range(1, TARGET + 1)):
        problems.append("coverage index article numbers must be exactly 1..281 in order")
    if len(set(nums)) != len(nums):
        problems.append("coverage index has duplicate article numbers")
    for f in ("official_chinese_translation_claimed", "chinese_binding_claimed",
              "full_translation_claimed", "chinese_llm_ready_created"):
        if idx.get(f) is not False:
            problems.append("coverage index %s must be false" % f)
    for r in recs:
        n = r.get("article_number")
        if r.get("expected_bab_number") != _bab_of(n):
            problems.append("article %s mapped to wrong Bab (%s, expected %s)"
                            % (n, r.get("expected_bab_number"), _bab_of(n)))
        if r.get("llm_ready_as_full_translation") is not False:
            problems.append("article %s llm_ready_as_full_translation must be false" % n)

    # per-Bab extracted source files: posture + range coverage
    for b, (lo, hi, pdf, exbase) in BABS.items():
        ex = _read(os.path.join(SRC_DIR, exbase))
        if ex.get("source_language") != "zh":
            problems.append("Bab %d source_language must be zh" % b)
        if ex.get("governing_text_language") != "ar":
            problems.append("Bab %d governing_text_language must be ar" % b)
        if ex.get("official_translation") is not False:
            problems.append("Bab %d official_translation must be false" % b)
        if ex.get("not_binding") is not True:
            problems.append("Bab %d not_binding must be true" % b)
        if ex.get("not_full_legal_translation_claimed") is not True:
            problems.append("Bab %d not_full_legal_translation_claimed must be true" % b)
        ex_nums = [r.get("article_number") for r in ex.get("records", [])]
        if ex_nums != list(range(lo, hi + 1)):
            problems.append("Bab %d extracted article numbers must be %d..%d" % (b, lo, hi))

    # no official/binding/governing claim anywhere in inventory/index
    blob = (json.dumps(inv, ensure_ascii=False) + json.dumps(idx, ensure_ascii=False)).lower()
    for term in BANNED:
        if term in blob:
            problems.append("banned claim present: %r" % term)

    # NO Chinese LLM-ready layer created
    if os.path.isdir(os.path.join(ROOT, "data", "official_chinese_legal_llm")):
        problems.append("no Chinese LLM-ready layer may be created in this PR")

    # protected layers unchanged
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    if len(zh) != 5 or sum(len(_read(x)["records"]) for x in zh) != 23:
        problems.append("Chinese Legal LLM must remain 5 files / 23 records")
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
    print("Chinese all-Babs (1-14) source inventory validation")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] 14 Bab PDFs preserved + extracted; coverage index 281 (articles 1..281, correct "
          "Bab mapping); Chinese internal/non-official/non-binding, Arabic governing; no full/"
          "official/binding claim; no Chinese LLM-ready created; llm_ready_as_full_translation="
          "false for all 281; Chinese 5/23 + Arabic 281 + English 281 + English reference 281 + "
          "Arabic source + OCR queue all unchanged.")
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
