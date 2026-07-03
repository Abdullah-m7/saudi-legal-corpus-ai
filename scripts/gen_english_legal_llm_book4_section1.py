#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
English Legal LLM-ready layer — PILOT: Book Four, Section 1
(Establishment and Capital / التأسيس ورأس المال).

This STARTS the English Legal LLM layer with the Book Four Section 1 pilot ONLY —
Articles 58, 59, 60, 66. It is NOT full English Legal LLM coverage.

The core field `legal_rule_text_en` is copied VERBATIM from the corresponding English
reference record's `english_reference_text` in
`data/english_reference/book4_section1_en_reference.json`, keyed by article number, so
the layer can never drift and contains NO model-generated English summary. There is NO
`legal_rule_summary_en`. Only the DERIVED structured metadata (subject, basis type,
actors, ... search queries) is authored here.

Trust posture: English is official GUIDANCE / reference only; Arabic remains governing
(governing_text_language = ar); manual_review_status = needs_manual_check; not legal advice.

It does NOT create records for the uncovered Section-1 articles (61-65), for Book Four
Sections 2-5, or for Books 1-3. It does NOT modify the English reference / Arabic /
Chinese data, and makes no network calls.

Reads : data/english_reference/book4_section1_en_reference.json
Writes: data/english_legal_llm/book4_section1_en_legal_llm.json
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_REL = "data/english_reference/book4_section1_en_reference.json"
SRC = os.path.join(ROOT, SRC_REL)
OUT = os.path.join(ROOT, "data", "english_legal_llm", "book4_section1_en_legal_llm.json")

COVERED = [58, 59, 60, 66]
UNCOVERED = [61, 62, 63, 64, 65]

_TRUST_NOTE = ("English Legal LLM-ready metadata built on the official English GUIDANCE "
               "reference alignment. The English is guidance/reference only; the governing/"
               "binding text is the Arabic original. legal_rule_text_en is copied verbatim from "
               "the English reference (no model-generated summary). Not legal advice.")


def _load_reference_text():
    """Map article_number -> english_reference_text from the Section 1 English
    reference. legal_rule_text_en is sourced from this map, never authored, so the
    layer stays byte-identical to the English reference text."""
    with open(SRC, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    return {r["article_number"]: r["english_reference_text"] for r in doc["records"]}


REFTEXT = _load_reference_text()


def rec(record_id, article_numbers, legal_subject_en, legal_basis_type,
        actors_en=None, rights_en=None, obligations_en=None, prohibitions_en=None,
        conditions_en=None, exceptions_en=None, legal_effects_en=None,
        liability_en=None, monetary_thresholds=None, deadlines_en=None,
        competent_authorities_en=None, cross_references_en=None, keywords_en=None,
        search_queries_en=None, risk_flags=None):
    (n,) = article_numbers  # pilot records are single-article
    text = REFTEXT[n]  # VERBATIM from the English reference data
    return {
        "book": 4,
        "record_type": "article_reference",
        "record_id": record_id,
        "article_numbers": article_numbers,
        "legal_subject_en": legal_subject_en,
        "legal_rule_text_en": text,
        "legal_basis_type": legal_basis_type,
        "actors_en": actors_en or [],
        "rights_en": rights_en or [],
        "obligations_en": obligations_en or [],
        "prohibitions_en": prohibitions_en or [],
        "conditions_en": conditions_en or [],
        "exceptions_en": exceptions_en or [],
        "legal_effects_en": legal_effects_en or [],
        "liability_en": liability_en or [],
        "monetary_thresholds": monetary_thresholds or [],
        "deadlines_en": deadlines_en or [],
        "competent_authorities_en": competent_authorities_en or [],
        "cross_references_en": cross_references_en or [],
        "keywords_en": keywords_en or [],
        "search_queries_en": search_queries_en or [],
        "risk_flags": risk_flags or [],
        "source_trust": {
            "english_source_status": "official_guidance_translation",
            "governing_text_language": "ar",
            "manual_review_status": "needs_manual_check",
            "source_reference_file": SRC_REL,
            "notes": _TRUST_NOTE,
        },
    }


RECORDS = [
    rec(
        "en-llm-book4-art058", [58],
        "Definition of a Joint-Stock Company",
        "definition",
        actors_en=["joint-stock company", "shareholders"],
        legal_effects_en=["defines the joint-stock company form and shareholder liability"],
        keywords_en=["joint-stock company", "definition", "shareholder liability", "capital"],
        search_queries_en=["What is a joint-stock company under the Companies Law?",
                           "How is shareholder liability defined for a JSC?"]),

    rec(
        "en-llm-book4-art059", [59],
        "Capital of a Joint-Stock Company",
        "mandatory",
        actors_en=["joint-stock company", "incorporators / shareholders"],
        obligations_en=[
            "the issued capital of a joint-stock company must be at least five hundred thousand riyals",
            "the paid-up capital upon incorporation must be at least one quarter of the issued capital",
        ],
        monetary_thresholds=[
            {"amount": 500000, "currency": "SAR",
             "description_en": "Minimum issued capital of a joint-stock company: not less than five "
                               "hundred thousand riyals."},
            {"amount": 0.25, "currency": "ratio",
             "description_en": "Paid-up capital upon incorporation: not less than a quarter (one "
                               "quarter) of the issued capital."},
        ],
        keywords_en=["minimum issued capital", "500,000 riyals", "paid-up capital", "one quarter",
                     "joint-stock company"],
        search_queries_en=["What is the minimum issued capital of a joint-stock company?",
                            "How much paid-up capital is required on incorporation of a JSC?"]),

    rec(
        "en-llm-book4-art060", [60],
        "Issued and Authorized Capital",
        "procedural",
        actors_en=["joint-stock company", "board of directors", "subscribers / shareholders"],
        conditions_en=[
            "the issued capital must be paid in full before the board increases it within the "
            "authorized capital",
        ],
        legal_effects_en=[
            "the company has issued capital representing the subscribed shares",
            "the articles of association may provide for authorized capital",
            "the board of directors may increase the issued capital within the limits of the "
            "authorized capital",
        ],
        keywords_en=["issued capital", "authorized capital", "subscribed shares", "board of directors",
                     "paid in full"],
        search_queries_en=["What is the difference between issued and authorized capital?",
                            "Can the board increase the issued capital within the authorized capital?"]),

    rec(
        "en-llm-book4-art066", [66],
        "Valuation of In-Kind Contributions",
        "procedural",
        actors_en=["accredited valuer", "incorporators", "extraordinary general assembly",
                   "providers of in-kind contributions", "joint-stock company"],
        obligations_en=[
            "in-kind contributions must be valued by an accredited valuer who prepares a report "
            "indicating their fair value",
        ],
        prohibitions_en=[
            "providers of in-kind contributions may not vote on the decision related to the "
            "valuation report",
        ],
        conditions_en=[
            "a reduction of the value stated in the report must be approved by the providers of the "
            "in-kind contributions",
            "the period between the valuer's report and the issuance of shares must not exceed the "
            "period specified in the Regulations",
        ],
        legal_effects_en=[
            "the valuer's report on fair value is presented to the incorporators or the "
            "extraordinary general assembly for deliberation",
        ],
        keywords_en=["in-kind contributions", "accredited valuer", "fair value", "extraordinary "
                     "general assembly", "voting restriction"],
        search_queries_en=["How are in-kind contributions valued for a joint-stock company?",
                            "Can providers of in-kind contributions vote on the valuation report?"]),
]


def main():
    got = [r["article_numbers"] for r in RECORDS]
    assert got == [[n] for n in COVERED], got
    covered = {n for g in got for n in g}
    assert covered == set(COVERED), covered
    assert not (covered & set(UNCOVERED)), covered
    for r in RECORDS:
        assert r["record_type"] == "article_reference", r["record_id"]
        (n,) = r["article_numbers"]
        assert r["legal_rule_text_en"] == REFTEXT[n], r["record_id"]
        assert "legal_rule_summary_en" not in r, r["record_id"]

    payload = {
        "layer_id": "sa-companies-english-legal-llm",
        "layer_status": "pilot",
        "scope": "book4_section1_establishment_and_capital",
        "book": 4,
        "section_key": "formation_and_capital",
        "section_title_en": "Establishment and Capital",
        "article_range": "58-66",
        "explicit_articles": COVERED,
        "uncovered_articles_excluded": UNCOVERED,
        "summary_source": ("legal_rule_text_en is copied verbatim from english_reference_text in "
                           + SRC_REL + " (no model-generated English summary)."),
        "english_source_status": "official_guidance_translation",
        "governing_text_language": "ar",
        "disclaimer_en": ("English Legal LLM-ready metadata over the official English guidance "
                          "reference; the governing/binding text is the Arabic original. This is a "
                          "PILOT (Book Four Section 1 only) — not full English Legal LLM coverage. "
                          "Not legal advice."),
        "records": RECORDS,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("wrote %s with %d English legal LLM records (articles %s)" % (OUT, len(RECORDS), COVERED))


if __name__ == "__main__":
    main()
