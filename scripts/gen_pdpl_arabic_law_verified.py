#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the verified/corrected Arabic text for the PDPL Law (43 articles).

The prior next-layer text came from reviewed OCR
(``REVIEWED_OCR_NOT_VERIFIED_OFFICIAL_TEXT``) and carried systematic OCR errors
(``9``→``و``, word-final ``ء``→``،``, missing spaces, ``الفرض``→``الغرض``, etc.).

This generator replaces each article's text with the official published law text
captured verbatim from the SDAIA knowledge-center source
(``pdpl_arabic_law_official_sdaia_source.json``), and records, per article, the
corroboration against the independent OCR (token-set similarity + length delta)
so the correction is auditable rather than blind.  It never paraphrases,
translates, or interprets — the corrected text IS the official SDAIA-published
Arabic text, cross-checked against the repo's independent OCR.

Read-only over its inputs; deterministic and idempotent over its output.
"""

from __future__ import annotations

import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OCR = os.path.join(ROOT, "sources", "pdpl", "next_layer",
                   "pdpl_arabic_law_next_layer_records.jsonl")
SOURCE = os.path.join(ROOT, "sources", "pdpl", "verified",
                      "pdpl_arabic_law_official_sdaia_source.json")
OUT_DIR = os.path.join(ROOT, "sources", "pdpl", "verified")
RECORDS = os.path.join(OUT_DIR, "pdpl_arabic_law_verified_records.jsonl")
SUMMARY = os.path.join(OUT_DIR, "pdpl_arabic_law_verified_summary.json")

REPEALED = {32}
KASHIDA = "ـ"


def normalize_official(text):
    """Strip non-semantic kashida elongation (ـ, U+0640) from captured official text."""
    return text.replace(KASHIDA, "")


def _norm_tokens(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"[ً-ْٰ]", "", s)
    for a, b in (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ى", "ي"),
                 ("ة", "ه"), ("ؤ", "و"), ("ئ", "ي")):
        s = s.replace(a, b)
    s = re.sub(r"[^ء-ي0-9]+", " ", s)
    return [w for w in s.split() if w]


def _similarity(a, b):
    A, B = set(_norm_tokens(a)), set(_norm_tokens(b))
    if not A or not B:
        return 0.0
    return round(len(A & B) / len(A | B), 4)


def build_records():
    ocr = {}
    for line in open(OCR, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            ocr[r["article_number"]] = r

    src = json.load(open(SOURCE, encoding="utf-8"))
    official = src["articles"]

    records = []
    for n in range(1, 44):
        o = ocr[n]
        verified = normalize_official(official[str(n)])
        prior = o["article_text"]
        repealed = n in REPEALED
        records.append({
            "law_key": "pdpl",
            "law_component": "law",
            "language": "ar",
            "record_layer": "PDPL_ARABIC_LAW_VERIFIED_TEXT",
            "article_number": n,
            "article_key": o["article_key"],
            "arabic_heading": o["arabic_heading"],
            "article_text_verified": verified,
            "article_text_ocr_prior": prior,
            "is_repealed": repealed,
            "corroboration": {
                "ocr_token_similarity": _similarity(verified, prior),
                "verified_len": len(verified),
                "ocr_len": len(prior),
            },
            "official_text_status": "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT",
            "verification_source_url": src["source_url"],
            "verification_source_authority_ar": src["source_authority_ar"],
            "governing_source_note": (
                "Arabic is the governing source. article_text_verified is the official "
                "SDAIA-published law text captured verbatim and cross-checked against the "
                "repository's independent reviewed-OCR text. Not the BOE gazette PDF."
            ),
            "translation_performed": False,
            "legal_interpretation_performed": False,
            "summarized_or_paraphrased": False,
            "english_used_for_correction": False,
        })
    return records


def main():
    records = build_records()
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(RECORDS, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    sims = [r["corroboration"]["ocr_token_similarity"] for r in records
            if not r["is_repealed"]]
    summary = {
        "law_key": "pdpl",
        "law_component": "law",
        "layer": "PDPL_ARABIC_LAW_VERIFIED_TEXT",
        "record_count": len(records),
        "article_number_range": [1, 43],
        "repealed_articles": sorted(REPEALED),
        "official_text_status": "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT",
        "source_artifact": os.path.relpath(SOURCE, ROOT),
        "prior_status": "REVIEWED_OCR_NOT_VERIFIED_OFFICIAL_TEXT",
        "corroboration_min_similarity": min(sims),
        "corroboration_mean_similarity": round(sum(sims) / len(sims), 4),
        "boundaries": {
            "arabic_governs": True,
            "translation_performed": False,
            "legal_interpretation_performed": False,
            "summarized_or_paraphrased": False,
            "english_used_for_correction": False,
        },
        "recommended_next_stage": "PDPL_ARABIC_LAW_LEGAL_LLM",
    }
    with open(SUMMARY, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("Wrote %d verified law records -> %s" % (len(records), os.path.relpath(RECORDS, ROOT)))
    print("Corroboration vs OCR: min=%.3f mean=%.3f (43 articles, Art 32 repealed)"
          % (min(sims), sum(sims) / len(sims)))


if __name__ == "__main__":
    main()
