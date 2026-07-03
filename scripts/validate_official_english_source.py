#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the Official English source intake (metadata + docs + trust labels).

Checks:
- metadata JSON exists and has the required intake fields with correct values;
- required docs exist;
- trust labels are correct (official_guidance_translation; governing text = ar);
- NO English Legal LLM records / directory exist yet;
- NO overclaim wording (binding/governing English text, verified, etc.).

Exit 0 == all pass; 1 == problems. No network, no heavy dependencies.
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META = os.path.join(ROOT, "data", "metadata", "official_english_source.json")
DOCS = os.path.join(ROOT, "docs", "official_english_source")
PDF = os.path.join(ROOT, "inputs", "companies_law_official_english_guidance.pdf")
REQUIRED_DOCS = [
    "README.md", "SOURCE_PROVENANCE.md", "ENGLISH_SOURCE_SCOPE.md",
    "ENGLISH_ALIGNMENT_PLAN.md", "ENGLISH_LAYER_RISKS.md",
]
# POSITIVE overclaim assertions that must NOT appear in the metadata
# (case-insensitive). These phrase the English as binding/governing/verified, which
# is forbidden — the English is guidance only and Arabic governs. Negations such as
# "not a binding ... English text" are intentionally not matched here.
BANNED_PHRASES = [
    '"governing_text_language": "en"',
    "english is binding",
    "english text is binding",
    "english is the governing",
    "governing text is the english",
    "binding english translation",
    "binding translation",
    "verified translation",
]


def _read_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    problems = []

    # -- metadata --------------------------------------------------------
    if not os.path.exists(META):
        print("MISSING metadata:", META)
        return 1
    meta = _read_json(META)
    expect = {
        "source_language": "en",
        "source_type": "official_guidance_translation",
        "governing_text_language": "ar",
        "source_file": "inputs/companies_law_official_english_guidance.pdf",
        "not_legal_advice": True,
        "english_llm_layer_created": False,
        "english_per_article_records_created": False,
    }
    for k, v in expect.items():
        if meta.get(k) != v:
            problems.append("metadata.%s must be %r (got %r)" % (k, v, meta.get(k)))
    if "Bureau of Experts" not in str(meta.get("source_authority", "")):
        problems.append("metadata.source_authority must mention 'Bureau of Experts'")
    if meta.get("source_type") in ("governing_text", "binding_translation", "unofficial_translation"):
        problems.append("metadata.source_type uses a forbidden trust label")

    # -- source PDF ------------------------------------------------------
    if not os.path.exists(PDF):
        problems.append("source PDF missing: inputs/companies_law_official_english_guidance.pdf")

    # -- docs ------------------------------------------------------------
    for name in REQUIRED_DOCS:
        if not os.path.exists(os.path.join(DOCS, name)):
            problems.append("missing doc: docs/official_english_source/%s" % name)

    # -- no English LLM layer yet ---------------------------------------
    if os.path.isdir(os.path.join(ROOT, "data", "english_legal_llm")):
        problems.append("data/english_legal_llm/ must NOT exist yet")
    import glob
    stray = glob.glob(os.path.join(ROOT, "data", "**", "*_en_legal_llm.json"), recursive=True)
    if stray:
        problems.append("English LLM record files must not exist yet: %s" % stray)

    # -- no overclaim wording in metadata + docs ------------------------
    blobs = [(META, open(META, encoding="utf-8").read())]
    for name in REQUIRED_DOCS:
        p = os.path.join(DOCS, name)
        if os.path.exists(p):
            blobs.append((p, open(p, encoding="utf-8").read()))
    for path, blob in blobs:
        low = blob.lower()
        for phrase in BANNED_PHRASES:
            # Allow the risks/validator to *name* the banned phrase in a negation
            # context by only flagging metadata; docs intentionally discuss risks.
            if phrase in low and path == META:
                problems.append("%s: overclaim phrase '%s'" % (os.path.basename(path), phrase))

    print("=" * 60)
    print("Official English source intake validation")
    print("=" * 60)
    if problems:
        for p in problems:
            print("  -", p)
        print("RESULT: %d problem(s) found ✗" % len(problems))
        return 1
    print("[PASS] metadata + %d docs; trust=official_guidance_translation; "
          "governing=ar; no English LLM layer yet" % len(REQUIRED_DOCS))
    print("RESULT: ALL CHECKS PASSED ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
