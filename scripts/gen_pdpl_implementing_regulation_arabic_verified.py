#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the verified/corrected Arabic text for the PDPL Implementing Regulation.

Replaces the structurally-cleaned extraction text (38 articles,
``EXTRACTED_TEXT_NOT_VERIFIED``) with the official SDAIA-published regulation
text captured verbatim (``pdpl_implementing_regulation_official_sdaia_source.json``).

Two documented, non-semantic normalizations are applied to the raw captured text:
  * kashida elongation characters (ـ, U+0640) are stripped;
  * a systematic fetch-tool typo (القواعد rendered as القواعس in articles 23, 32,
    35, 36) is corrected to القواعد — confirmed against the independent extraction.

Each article's corrected text is cross-checked against the repository's
independent cleaned extraction (token-set similarity + length) so the correction
is auditable.  No paraphrase, translation, or interpretation.  Arabic governs.

Read-only over its inputs; deterministic and idempotent over its output.
"""

from __future__ import annotations

import json
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANED = os.path.join(ROOT, "sources", "pdpl", "regulation", "cleaned",
                       "pdpl_implementing_regulation_arabic_cleaned_records.jsonl")
SOURCE = os.path.join(ROOT, "sources", "pdpl", "regulation", "verified",
                      "pdpl_implementing_regulation_official_sdaia_source.json")
OUT_DIR = os.path.join(ROOT, "sources", "pdpl", "regulation", "verified")
RECORDS = os.path.join(OUT_DIR, "pdpl_implementing_regulation_arabic_verified_records.jsonl")
SUMMARY = os.path.join(OUT_DIR, "pdpl_implementing_regulation_arabic_verified_summary.json")

KASHIDA = "ـ"


def normalize_official(text):
    """Apply the documented non-semantic corrections to raw captured official text."""
    text = text.replace(KASHIDA, "")
    text = text.replace("قواعس", "قواعد")   # fetch typo: القواعد mis-rendered as القواعس
    return text


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
    return round(len(A & B) / len(A | B), 4) if A and B else 0.0


def build_records():
    cleaned = {}
    for line in open(CLEANED, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            cleaned[r["article_number"]] = r

    src = json.load(open(SOURCE, encoding="utf-8"))
    official = src["articles"]

    records = []
    for n in range(1, 39):
        cl = cleaned[n]
        verified = normalize_official(official[str(n)])
        prior = cl["arabic_heading"] + "\n" + cl["article_text_cleaned"]
        records.append({
            "law_key": "pdpl",
            "law_component": "implementing_regulation",
            "language": "ar",
            "record_layer": "PDPL_IMPLEMENTING_REGULATION_ARABIC_VERIFIED_TEXT",
            "article_number": n,
            "article_key": cl["article_key"],
            "arabic_heading": cl["arabic_heading"],
            "article_text_verified": verified,
            "article_text_cleaned_prior": prior,
            "corroboration": {
                "cleaned_token_similarity": _similarity(verified, prior),
                "verified_len": len(verified),
                "cleaned_len": len(cl["article_text_cleaned"]),
            },
            "official_text_status": "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT",
            "verification_source_url": src["source_url"],
            "verification_source_authority_ar": src["source_authority_ar"],
            "governing_source_note": (
                "Arabic is the governing source. article_text_verified is the official "
                "SDAIA-published regulation text captured verbatim (kashida stripped; a "
                "systematic fetch typo القواعس→القواعد corrected) and cross-checked against the "
                "repository's independent cleaned extraction. Not the BOE gazette PDF."
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

    sims = [r["corroboration"]["cleaned_token_similarity"] for r in records]
    summary = {
        "law_key": "pdpl",
        "law_component": "implementing_regulation",
        "layer": "PDPL_IMPLEMENTING_REGULATION_ARABIC_VERIFIED_TEXT",
        "record_count": len(records),
        "article_number_range": [1, 38],
        "official_text_status": "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT",
        "source_artifact": os.path.relpath(SOURCE, ROOT),
        "prior_status": "EXTRACTED_TEXT_NOT_VERIFIED_OFFICIAL_TEXT",
        "post_capture_corrections": src_corrections(),
        "corroboration_min_similarity": min(sims),
        "corroboration_mean_similarity": round(sum(sims) / len(sims), 4),
        "boundaries": {
            "arabic_governs": True,
            "translation_performed": False,
            "legal_interpretation_performed": False,
            "summarized_or_paraphrased": False,
            "english_used_for_correction": False,
        },
        "recommended_next_stage": "PDPL_IMPLEMENTING_REGULATION_ARABIC_LEGAL_LLM (verified)",
    }
    with open(SUMMARY, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Wrote %d verified regulation records -> %s" % (len(records), os.path.relpath(RECORDS, ROOT)))
    print("Corroboration vs cleaned: min=%.3f mean=%.3f" % (min(sims), sum(sims) / len(sims)))


def src_corrections():
    src = json.load(open(SOURCE, encoding="utf-8"))
    return src.get("post_capture_corrections", {})


if __name__ == "__main__":
    main()
