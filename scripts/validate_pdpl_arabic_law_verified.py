#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the verified/corrected PDPL Law Arabic text.

Confirms the verified records are internally consistent, that each
article_text_verified matches the committed official SDAIA source artifact
verbatim, that every non-repealed article is corroborated against the prior OCR
above a floor, and that honesty boundaries hold.  Does not modify any file.
Exit 0 = PASS, 1 = FAIL.
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "sources", "pdpl", "verified",
                      "pdpl_arabic_law_official_sdaia_source.json")
RECORDS = os.path.join(ROOT, "sources", "pdpl", "verified",
                       "pdpl_arabic_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "pdpl", "verified",
                       "pdpl_arabic_law_verified_summary.json")

EXPECTED = 43
REPEALED = {32}
SIM_FLOOR = 0.70   # non-repealed articles must corroborate the independent OCR at least this much


def main():
    errors = []
    for p in (SOURCE, RECORDS, SUMMARY):
        if not os.path.isfile(p):
            print("FAIL: missing file: %s" % os.path.relpath(p, ROOT))
            return 1

    src = json.load(open(SOURCE, encoding="utf-8"))
    official = src["articles"]
    records = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]

    if len(records) != EXPECTED:
        errors.append("[1] expected %d records, found %d" % (EXPECTED, len(records)))
    nums = [r["article_number"] for r in records]
    if nums != list(range(1, EXPECTED + 1)):
        errors.append("[1] article_number sequence not 1..%d" % EXPECTED)

    for r in records:
        n = r["article_number"]

        if r.get("article_key") != "pdpl_law_art_%03d" % n:
            errors.append("[2] art %s: article_key %r" % (n, r.get("article_key")))

        # [3] verified text matches committed official source verbatim
        if r.get("article_text_verified") != official.get(str(n)):
            errors.append("[3] art %s: article_text_verified != committed official source" % n)
        if not r.get("article_text_verified", "").strip():
            errors.append("[3] art %s: empty verified text" % n)

        # [4] corroboration recorded + floor for non-repealed
        corr = r.get("corroboration", {})
        sim = corr.get("ocr_token_similarity")
        if sim is None:
            errors.append("[4] art %s: missing corroboration similarity" % n)
        elif n not in REPEALED and sim < SIM_FLOOR:
            errors.append("[4] art %s: OCR corroboration %.3f below floor %.2f" % (n, sim, SIM_FLOOR))

        # [5] repealed flag
        if (n in REPEALED) != bool(r.get("is_repealed")):
            errors.append("[5] art %s: is_repealed flag wrong" % n)

        # [6] honest boundaries
        if r.get("official_text_status") != "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT":
            errors.append("[6] art %s: unexpected official_text_status %r" % (n, r.get("official_text_status")))
        for flag in ("translation_performed", "legal_interpretation_performed",
                     "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(flag) is not False:
                errors.append("[6] art %s: boundary flag %s must be False" % (n, flag))

    # [7] summary consistency
    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != len(records):
        errors.append("[7] summary record_count %r != %d" % (summary.get("record_count"), len(records)))
    if summary.get("official_text_status") != "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT":
        errors.append("[7] summary official_text_status wrong")

    if errors:
        print("FAIL: %d error(s) in verified PDPL law text:" % len(errors))
        for e in errors:
            print("  - %s" % e)
        return 1

    sims = [r["corroboration"]["ocr_token_similarity"] for r in records
            if not r["is_repealed"]]
    print("PASS: %d verified PDPL law articles (Art 32 repealed)" % len(records))
    print("  - article_text_verified matches committed official SDAIA source verbatim")
    print("  - OCR corroboration: min=%.3f mean=%.3f (floor %.2f)"
          % (min(sims), sum(sims) / len(sims), SIM_FLOOR))
    print("  - Arabic governs; verified vs official SDAIA published text; no translation/paraphrase/interpretation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
