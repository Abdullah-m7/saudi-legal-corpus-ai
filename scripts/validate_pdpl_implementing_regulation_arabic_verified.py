#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the verified/corrected PDPL Implementing Regulation text.

Confirms the verified records match the committed official source (after the two
documented normalizations), that each article corroborates the independent
cleaned extraction above a floor, that no kashida / known fetch typo remains,
and that honesty boundaries hold.  Exit 0 = PASS, 1 = FAIL.
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "sources", "pdpl", "regulation", "verified",
                      "pdpl_implementing_regulation_official_sdaia_source.json")
RECORDS = os.path.join(ROOT, "sources", "pdpl", "regulation", "verified",
                       "pdpl_implementing_regulation_arabic_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "pdpl", "regulation", "verified",
                       "pdpl_implementing_regulation_arabic_verified_summary.json")

EXPECTED = 38
SIM_FLOOR = 0.75
KASHIDA = "ـ"


def _normalize_official(text):
    return text.replace(KASHIDA, "").replace("قواعس", "قواعد")


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
    if [r["article_number"] for r in records] != list(range(1, EXPECTED + 1)):
        errors.append("[1] article_number sequence not 1..%d" % EXPECTED)

    for r in records:
        n = r["article_number"]

        if r.get("article_key") != "pdpl_reg_art_%03d" % n:
            errors.append("[2] art %s: article_key %r" % (n, r.get("article_key")))

        text = r.get("article_text_verified", "")
        # [3] verified text == normalized official source
        if text != _normalize_official(official.get(str(n), "")):
            errors.append("[3] art %s: verified text != normalized official source" % n)
        if not text.strip():
            errors.append("[3] art %s: empty verified text" % n)

        # [4] no residual kashida or known fetch typo
        if KASHIDA in text:
            errors.append("[4] art %s: residual kashida" % n)
        if "قواعس" in text:
            errors.append("[4] art %s: residual fetch typo قواعس" % n)

        # [5] corroboration floor
        sim = r.get("corroboration", {}).get("cleaned_token_similarity")
        if sim is None:
            errors.append("[5] art %s: missing corroboration similarity" % n)
        elif sim < SIM_FLOOR:
            errors.append("[5] art %s: corroboration %.3f below floor %.2f" % (n, sim, SIM_FLOOR))

        # [6] honest boundaries
        if r.get("official_text_status") != "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT":
            errors.append("[6] art %s: unexpected official_text_status %r" % (n, r.get("official_text_status")))
        for flag in ("translation_performed", "legal_interpretation_performed",
                     "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(flag) is not False:
                errors.append("[6] art %s: boundary flag %s must be False" % (n, flag))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != len(records):
        errors.append("[7] summary record_count mismatch")
    if summary.get("official_text_status") != "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT":
        errors.append("[7] summary official_text_status wrong")

    if errors:
        print("FAIL: %d error(s) in verified PDPL regulation text:" % len(errors))
        for e in errors:
            print("  - %s" % e)
        return 1

    sims = [r["corroboration"]["cleaned_token_similarity"] for r in records]
    print("PASS: %d verified PDPL implementing-regulation articles" % len(records))
    print("  - verified text matches normalized official SDAIA source; no kashida / fetch typo")
    print("  - cleaned-extraction corroboration: min=%.3f mean=%.3f (floor %.2f)"
          % (min(sims), sum(sims) / len(sims), SIM_FLOOR))
    print("  - Arabic governs; verified vs official SDAIA published text; no translation/paraphrase/interpretation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
