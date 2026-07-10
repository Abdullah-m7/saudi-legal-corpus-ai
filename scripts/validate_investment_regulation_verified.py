#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the verified Investment Regulations Arabic text (37 articles)."""

from __future__ import annotations

import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "sources", "investment", "regulation", "official_source",
                      "investment_regulation_official_misa_source.json")
RECORDS = os.path.join(ROOT, "sources", "investment", "regulation", "verified",
                       "investment_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "investment", "regulation", "verified",
                       "investment_regulation_verified_summary.json")
PDF = os.path.join(ROOT, "inputs", "investment_official_pdfs", "investment_regulation_misa_ar.pdf")

EXPECTED = 37


def main():
    errors = []
    for p in (SOURCE, RECORDS, SUMMARY):
        if not os.path.isfile(p):
            print("FAIL: missing file: %s" % os.path.relpath(p, ROOT))
            return 1

    src = json.load(open(SOURCE, encoding="utf-8"))
    arts = src["articles"]
    records = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]

    if len(records) != EXPECTED:
        errors.append("[1] expected %d records, found %d" % (EXPECTED, len(records)))
    if [r["article_number"] for r in records] != list(range(1, EXPECTED + 1)):
        errors.append("[1] article_number sequence not 1..%d" % EXPECTED)

    if os.path.isfile(PDF):
        h = hashlib.sha256(open(PDF, "rb").read()).hexdigest()
        if h != src.get("source_pdf_sha256"):
            errors.append("[2] official PDF sha256 mismatch vs source artifact")
    else:
        errors.append("[2] official PDF missing: %s" % os.path.relpath(PDF, ROOT))

    for r in records:
        n = r["article_number"]
        a = arts.get(str(n), {})
        if r.get("article_key") != "investment_reg_art_%03d" % n:
            errors.append("[3] art %s: article_key %r" % (n, r.get("article_key")))
        if r.get("article_text_verified") != a.get("text_ar"):
            errors.append("[4] art %s: verified text != source" % n)
        if r.get("arabic_title") != a.get("title_ar"):
            errors.append("[4] art %s: title != source" % n)
        if not r.get("article_text_verified", "").strip():
            errors.append("[4] art %s: empty verified text" % n)
        if r.get("official_text_status") != "VERIFIED_TRANSCRIBED_FROM_OFFICIAL_MISA_PDF":
            errors.append("[5] art %s: unexpected official_text_status %r" % (n, r.get("official_text_status")))
        for flag in ("translation_performed", "legal_interpretation_performed", "summarized_or_paraphrased"):
            if r.get(flag) is not False:
                errors.append("[5] art %s: boundary flag %s must be False" % (n, flag))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != len(records):
        errors.append("[6] summary record_count mismatch")

    if errors:
        print("FAIL: %d error(s) in verified Investment Regulations text:" % len(errors))
        for e in errors:
            print("  - %s" % e)
        return 1

    print("PASS: %d verified Investment Regulations articles" % len(records))
    print("  - verified text + titles match committed official MISA source verbatim")
    print("  - official Arabic PDF present with recorded sha256")
    print("  - Arabic governs; no translation/paraphrase/interpretation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
