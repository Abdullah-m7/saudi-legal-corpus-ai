#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
English Legal LLM-ready layer — Book Four, Section 4
(Shares, Debt Instruments and Sukuk / الأسهم وأدوات الدين والصكوك).

Adds English Legal LLM-ready records for the Book Four Section 4 provision-covered
articles ONLY — 108, 113, 115, 117 (4 article_reference records). NOT full English Legal
LLM coverage.

The core field `legal_rule_text_en` is copied VERBATIM from the corresponding English
reference record's `english_reference_text` in
`data/english_reference/book4_section4_en_reference.json`, keyed by article number, so
the layer can never drift and contains NO model-generated English summary. There is NO
`legal_rule_summary_en`. Only the DERIVED structured metadata is authored here, and every
actor/obligation/condition/prohibition/authority/threshold/deadline/liability/effect is
traceable to that article's own verbatim text (no concepts imported from other articles).

Trust posture: English is official GUIDANCE / reference only; Arabic remains governing
(governing_text_language = ar); manual_review_status = needs_manual_check; not legal advice.

It does NOT create records for the uncovered Section-4 articles (103, 104, 105, 106,
107, 109, 110, 111, 112, 114, 116, 118, 119, 120 — including the owner-reconciled 110),
for other Book Four sections, or for Books 1-3. It does NOT modify the English reference /
Arabic / Chinese data, and makes no network calls.

Reads : data/english_reference/book4_section4_en_reference.json
Writes: data/english_legal_llm/book4_section4_en_legal_llm.json
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_REL = "data/english_reference/book4_section4_en_reference.json"
SRC = os.path.join(ROOT, SRC_REL)
OUT = os.path.join(ROOT, "data", "english_legal_llm", "book4_section4_en_legal_llm.json")

COVERED = [108, 113, 115, 117]
UNCOVERED = [103, 104, 105, 106, 107, 109, 110, 111, 112, 114, 116, 118, 119, 120]

_TRUST_NOTE = ("English Legal LLM-ready metadata built on the official English GUIDANCE "
               "reference alignment. The English is guidance/reference only; the governing/"
               "binding text is the Arabic original. legal_rule_text_en is copied verbatim from "
               "the English reference (no model-generated summary). Not legal advice.")


def _load_reference_text():
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
    (n,) = article_numbers
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
        "en-llm-book4-art108", [108],
        "Types and Classes of Shares",
        "definition",
        actors_en=["company"],
        rights_en=["the company's articles of association may provide for different classes of share "
                   "types and may grant certain rights or privileges to certain classes or set "
                   "restrictions thereon"],
        obligations_en=["shares of the same type or class shall have equal rights and obligations"],
        conditions_en=["the Regulations shall specify the rules for the types and classes of shares "
                       "that may be issued"],
        legal_effects_en=["the types of shares a company may issue are common, preferred, and "
                          "redeemable",
                          "each type or class of shares has the rights associated therewith as "
                          "stipulated in the articles of association"],
        keywords_en=["types of shares", "classes of shares", "common", "preferred", "redeemable",
                     "equal rights and obligations"],
        search_queries_en=["What types of shares may a joint-stock company issue?",
                            "Do shares of the same class have equal rights?"]),

    rec(
        "en-llm-book4-art113", [113],
        "Drag-along and Tag-along Rights",
        "permissive",
        actors_en=["company", "majority shareholders", "minority shareholders", "bona fide buyer"],
        rights_en=["majority shareholders may obligate minority shareholders to accept a bona fide "
                   "buyer's offer to purchase all shares for the same price and terms (drag-along)",
                   "when the majority sell their shares, minority shareholders may obligate the "
                   "majority to guarantee the sale of minority shares for the same price and terms "
                   "(tag-along)"],
        conditions_en=["the articles of association may so provide only upon the approval of "
                       "shareholders representing at least 90% of the company's voting shares"],
        exceptions_en=["without prejudice to the Capital Market Law"],
        monetary_thresholds=[
            {"amount": 0.9, "currency": "ratio",
             "description_en": "Drag-along / tag-along rights may be provided for only upon the "
                               "approval of shareholders representing at least 90% of voting shares."},
        ],
        keywords_en=["drag-along", "tag-along", "90% of voting shares", "majority shareholders",
                     "minority shareholders", "Capital Market Law"],
        search_queries_en=["What are drag-along and tag-along rights in a joint-stock company?",
                            "What approval is needed to include drag-along rights in the articles?"]),

    rec(
        "en-llm-book4-art115", [115],
        "Non-Payment of Share Value",
        "procedural",
        actors_en=["shareholder", "board of directors", "company", "other shareholders", "buyer"],
        obligations_en=["a shareholder shall pay the remaining amount of the value of the share on the "
                        "designated dates",
                        "the company shall return any remaining amount from the sale proceeds to the "
                        "shareholder",
                        "the company shall cancel the certificate of the share sold and provide the "
                        "buyer with a new certificate, and record the sale in the shareholders register"],
        rights_en=["after notifying the shareholder, the board of directors may sell the share at a "
                   "public auction or in the capital market",
                   "the articles of association may grant other shareholders a preemptive right to "
                   "purchase the shares of the non-paying shareholder",
                   "the non-paying shareholder may, up to the date of sale, pay the due amount plus "
                   "related expenses and then demand payment of dividends"],
        legal_effects_en=["the company satisfies the amounts due from the sale proceeds, and from the "
                          "shareholder's property if the proceeds are insufficient",
                          "rights associated with the unpaid shares (dividends, attending assemblies, "
                          "and voting) are suspended until the shares are sold or the amount is paid"],
        keywords_en=["non-payment", "default on share value", "public auction", "preemptive right",
                     "suspension of rights", "cancel certificate"],
        search_queries_en=["What happens if a shareholder does not pay the value of his shares?",
                            "Can the board sell a non-paying shareholder's shares?"]),

    rec(
        "en-llm-book4-art117", [117],
        "Issuance of Debt Instruments and Financing Sukuk",
        "mixed",
        actors_en=["joint-stock company", "extraordinary general assembly", "board of directors"],
        rights_en=["a joint-stock company may issue negotiable debt instruments or financing sukuk"],
        obligations_en=["for convertible debt instruments or sukuk, the extraordinary general assembly "
                        "must issue a decision determining the maximum number of shares that may be "
                        "issued against them",
                        "the board of directors shall issue new shares against such instruments/sukuk "
                        "upon satisfaction of the conversion conditions or the lapse of the conversion "
                        "period, without a new assembly approval",
                        "the board of directors shall amend the articles of association regarding the "
                        "number of issued shares and the capital",
                        "the board of directors must register the completion of each capital increase "
                        "with the Commercial Register"],
        conditions_en=["issuance is in accordance with the Capital Market Law",
                       "convertible issuance requires an extraordinary general assembly decision "
                       "setting the maximum number of shares"],
        legal_effects_en=["new shares are issued against the instruments/sukuk upon conversion, and "
                          "the company's issued shares and capital are amended accordingly"],
        competent_authorities_en=["extraordinary general assembly"],
        keywords_en=["debt instruments", "financing sukuk", "convertible", "extraordinary general "
                     "assembly", "Capital Market Law", "Commercial Register"],
        search_queries_en=["Can a joint-stock company issue debt instruments or sukuk?",
                            "What is required to issue convertible sukuk?"]),
]


def main():
    got = [r["article_numbers"] for r in RECORDS]
    assert got == [[n] for n in COVERED], got
    covered = {n for g in got for n in g}
    assert covered == set(COVERED), covered
    assert not (covered & set(UNCOVERED)), covered
    assert 110 not in covered, "owner-reconciled Article 110 must NOT get a record"
    for r in RECORDS:
        assert r["record_type"] == "article_reference", r["record_id"]
        (n,) = r["article_numbers"]
        assert r["legal_rule_text_en"] == REFTEXT[n], r["record_id"]
        assert "legal_rule_summary_en" not in r, r["record_id"]

    payload = {
        "layer_id": "sa-companies-english-legal-llm",
        "layer_status": "pilot_extension",
        "scope": "book4_section4_shares_debt_instruments_sukuk",
        "book": 4,
        "section_key": "shares_debt_instruments_sukuk",
        "section_title_en": "Shares, Debt Instruments and Sukuk",
        "article_range": "103-120",
        "explicit_articles": COVERED,
        "uncovered_articles_excluded": UNCOVERED,
        "summary_source": ("legal_rule_text_en is copied verbatim from english_reference_text in "
                           + SRC_REL + " (no model-generated English summary)."),
        "english_source_status": "official_guidance_translation",
        "governing_text_language": "ar",
        "disclaimer_en": ("English Legal LLM-ready metadata over the official English guidance "
                          "reference; the governing/binding text is the Arabic original. Book Four "
                          "Section 4 provision-covered articles only (Article 110 remains uncovered) "
                          "— not full English Legal LLM coverage. Not legal advice."),
        "records": RECORDS,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("wrote %s with %d English legal LLM records (articles %s)" % (OUT, len(RECORDS), COVERED))


if __name__ == "__main__":
    main()
