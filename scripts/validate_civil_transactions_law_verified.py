#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the verified Civil Transactions Law Arabic text (721 articles)."""

from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "sources", "civil", "law", "official_source",
                      "civil_transactions_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "civil", "law", "verified",
                       "civil_transactions_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "civil", "law", "verified",
                       "civil_transactions_law_verified_summary.json")

EXPECTED = 721
SECTION_HEADING = re.compile(r"^\s*(الكتاب|الباب|الفصل|القسم|الفرع)\s")


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
    if len(arts) != EXPECTED:
        errors.append("[1] source artifact has %d articles, expected %d" % (len(arts), EXPECTED))

    for r in records:
        n = r["article_number"]
        a = arts.get(str(n), {})
        if r.get("article_key") != "civil_law_art_%03d" % n:
            errors.append("[2] art %s: article_key %r" % (n, r.get("article_key")))
        # [3] text + section context match the committed source verbatim
        if r.get("article_text_verified") != a.get("text"):
            errors.append("[3] art %s: verified text != source" % n)
        if r.get("section_context_ar") != a.get("section_context", ""):
            errors.append("[3] art %s: section_context != source" % n)
        text = r.get("article_text_verified", "")
        if not text.strip():
            errors.append("[3] art %s: empty verified text" % n)
        # [4] no structural heading lines left inside bodies; no latin junk
        for ln in text.split("\n"):
            if SECTION_HEADING.match(ln):
                errors.append("[4] art %s: structural heading line left in body: %r" % (n, ln[:40]))
        if re.search(r"[A-Za-z]{2,}", text):
            errors.append("[4] art %s: latin characters in body" % n)
        # [5] honest boundaries
        if r.get("official_text_status") != "OWNER_PROVIDED_OFFICIAL_TEXT":
            errors.append("[5] art %s: unexpected official_text_status %r" % (n, r.get("official_text_status")))
        for flag in ("translation_performed", "legal_interpretation_performed",
                     "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(flag) is not False:
                errors.append("[5] art %s: boundary flag %s must be False" % (n, flag))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != len(records):
        errors.append("[6] summary record_count mismatch")

    if errors:
        print("FAIL: %d error(s) in verified Civil Transactions Law text:" % len(errors))
        for e in errors[:20]:
            print("  - %s" % e)
        return 1

    print("PASS: %d verified Civil Transactions Law articles" % len(records))
    print("  - complete 1..721 sequence; text + section context match committed source verbatim")
    print("  - no structural headings inside bodies; no latin junk")
    print("  - Arabic governs; owner-provided official text; no translation/paraphrase/interpretation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
