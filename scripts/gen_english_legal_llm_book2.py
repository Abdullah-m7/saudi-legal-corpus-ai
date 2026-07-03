#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
English Legal LLM-ready layer — Book 2 (General Partnerships, Articles 35-50).

Backfills the English Legal LLM layer for Book 2 — one `article_reference` record per
article, Articles 35-50. This complements the existing repo book4 English Legal LLM
sections; it is still NOT full Saudi Companies Law English coverage (English Legal LLM now
covers Books 1-3 plus repo book4 Sections 1-5).

VERBATIM SOURCE RULE
--------------------
`legal_rule_text_en` is copied VERBATIM from the corresponding official English reference
record's `english_reference_text` in `data/english_reference/book2_en_reference.json`,
keyed by article number, so the layer can never drift and contains NO model-generated
English summary. There is NO `legal_rule_summary_en`.

The DERIVED structured metadata is kept deliberately conservative for this backfill:
- `legal_subject_en` reuses the reference record's own `article_heading_en`.
- `keywords_en` reuses the reference record's own approved `llm.keywords_en`.
- `legal_basis_type` is set to the conservative catch-all "mixed" (no narrower legal claim
  is asserted here; the authoritative content is the verbatim `legal_rule_text_en`).
- Every other derived array (actors/obligations/... search queries) is left EMPTY rather
  than inventing legal implications — the schema allows empty arrays.

Trust posture: English is official GUIDANCE / reference only; Arabic remains governing
(governing_text_language = ar); manual_review_status = needs_manual_check; not legal advice.

It does NOT modify the English reference / Arabic / Chinese data, does NOT touch the repo
book4 English Legal LLM records, and makes no network calls.

Reads : data/english_reference/book2_en_reference.json
Writes: data/english_legal_llm/book2_en_legal_llm.json
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

BOOK = 2
ARTICLE_RANGE = list(range(35, 51))   # 35-50
SRC_REL = "data/english_reference/book2_en_reference.json"
OUT_REL = "data/english_legal_llm/book2_en_legal_llm.json"

SRC = os.path.join(ROOT, SRC_REL)
OUT = os.path.join(ROOT, OUT_REL)

_TRUST_NOTE = ("English Legal LLM-ready metadata built on the official English GUIDANCE "
               "reference alignment. The English is guidance/reference only; the governing/"
               "binding text is the Arabic original. legal_rule_text_en is copied verbatim from "
               "the English reference (no model-generated summary). Not legal advice.")


def _load_reference():
    """Map article_number -> reference record from the Book's English reference.
    legal_rule_text_en is sourced from english_reference_text, never authored, so the layer
    stays byte-identical to the official English reference text."""
    with open(SRC, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    return {r["article_number"]: r for r in doc["records"]}


REF = _load_reference()


def rec(ref_rec):
    n = ref_rec["article_number"]
    heading = (ref_rec.get("article_heading_en") or "").strip() or ("Article %d" % n)
    return {
        "book": BOOK,
        "record_type": "article_reference",
        "record_id": "en-llm-book%d-art%03d" % (BOOK, n),
        "article_numbers": [n],
        "legal_subject_en": heading,
        "legal_rule_text_en": ref_rec["english_reference_text"],  # VERBATIM
        "legal_basis_type": "mixed",
        "actors_en": [],
        "rights_en": [],
        "obligations_en": [],
        "prohibitions_en": [],
        "conditions_en": [],
        "exceptions_en": [],
        "legal_effects_en": [],
        "liability_en": [],
        "monetary_thresholds": [],
        "deadlines_en": [],
        "competent_authorities_en": [],
        "cross_references_en": [],
        "keywords_en": list(ref_rec.get("llm", {}).get("keywords_en", [])),
        "search_queries_en": [],
        "risk_flags": [],
        "source_trust": {
            "english_source_status": "official_guidance_translation",
            "governing_text_language": "ar",
            "manual_review_status": "needs_manual_check",
            "source_reference_file": SRC_REL,
            "notes": _TRUST_NOTE,
        },
    }


RECORDS = [rec(REF[n]) for n in ARTICLE_RANGE]


def main():
    got = [r["article_numbers"] for r in RECORDS]
    assert got == [[n] for n in ARTICLE_RANGE], got
    covered = {n for g in got for n in g}
    assert covered == set(ARTICLE_RANGE), covered
    for r in RECORDS:
        assert r["record_type"] == "article_reference", r["record_id"]
        assert r["book"] == BOOK, r["record_id"]
        (n,) = r["article_numbers"]
        assert r["legal_rule_text_en"] == REF[n]["english_reference_text"], r["record_id"]
        assert "legal_rule_summary_en" not in r, r["record_id"]

    payload = {
        "layer_id": "sa-companies-english-legal-llm",
        "layer_status": "backfill",
        "scope": "book2_general_partnerships",
        "book": BOOK,
        "section_key": "general_partnerships",
        "section_title_en": "General Partnerships",
        "article_range": "35-50",
        "explicit_articles": ARTICLE_RANGE,
        "summary_source": ("legal_rule_text_en is copied verbatim from english_reference_text in "
                           + SRC_REL + " (no model-generated English summary)."),
        "english_source_status": "official_guidance_translation",
        "governing_text_language": "ar",
        "disclaimer_en": ("English Legal LLM-ready metadata over the official English guidance "
                          "reference; the governing/binding text is the Arabic original. English "
                          "Legal LLM covers Books 1-3 plus repo book4 Sections 1-5 (repo book4 is an "
                          "internal repository label for the modeled Joint-Stock Company scope, not "
                          "full Articles 58-137) — not full Saudi Companies Law coverage. Not legal "
                          "advice."),
        "records": RECORDS,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("wrote %s with %d English legal LLM records (Book %d, articles %d-%d)" % (
        OUT, len(RECORDS), BOOK, ARTICLE_RANGE[0], ARTICLE_RANGE[-1]))


if __name__ == "__main__":
    main()
