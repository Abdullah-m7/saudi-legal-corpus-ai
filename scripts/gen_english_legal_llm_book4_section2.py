#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
English Legal LLM-ready layer — Book Four, Section 2
(Board of Directors and Governance / مجلس الإدارة والحوكمة).

Adds English Legal LLM-ready records for the Book Four Section 2 provision-covered
articles ONLY — 67, 68, 71, 72, 75, 77 (6 article_reference records). NOT full English
Legal LLM coverage.

The core field `legal_rule_text_en` is copied VERBATIM from the corresponding English
reference record's `english_reference_text` in
`data/english_reference/book4_section2_en_reference.json`, keyed by article number, so
the layer can never drift and contains NO model-generated English summary. There is NO
`legal_rule_summary_en`. Only the DERIVED structured metadata is authored here, and every
actor/obligation/condition/prohibition/authority/threshold/deadline/liability/effect is
traceable to that article's own verbatim text (no concepts imported from other articles).

Trust posture: English is official GUIDANCE / reference only; Arabic remains governing
(governing_text_language = ar); manual_review_status = needs_manual_check; not legal advice.

It does NOT create records for the uncovered Section-2 articles (69, 70, 73, 74, 76,
78-83), for other Book Four sections, or for Books 1-3. It does NOT modify the English
reference / Arabic / Chinese data, and makes no network calls.

Reads : data/english_reference/book4_section2_en_reference.json
Writes: data/english_legal_llm/book4_section2_en_legal_llm.json
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_REL = "data/english_reference/book4_section2_en_reference.json"
SRC = os.path.join(ROOT, SRC_REL)
OUT = os.path.join(ROOT, "data", "english_legal_llm", "book4_section2_en_legal_llm.json")

COVERED = [67, 68, 71, 72, 75, 77]
UNCOVERED = [69, 70, 73, 74, 76, 78, 79, 80, 81, 82, 83]

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
        "en-llm-book4-art067", [67],
        "Nomination for Board Membership",
        "mixed",
        actors_en=["joint-stock company", "board of directors", "shareholder"],
        obligations_en=["a joint-stock company shall be managed by a board of directors comprising "
                        "at least three members"],
        rights_en=["a shareholder may nominate himself or one or more shareholders for membership "
                   "on the board of directors"],
        legal_effects_en=["the board of directors must comprise at least three members"],
        keywords_en=["board of directors", "nomination", "at least three members", "shareholder"],
        search_queries_en=["Who may nominate candidates for a joint-stock company's board?",
                            "What is the minimum number of board members in a JSC?"]),

    rec(
        "en-llm-book4-art068", [68],
        "Election of Board Members",
        "mixed",
        actors_en=["ordinary general assembly", "board members", "Competent Authority"],
        obligations_en=["the ordinary general assembly shall elect the company's board members",
                        "board members must be natural persons",
                        "the articles of association shall determine the term of the board of "
                        "directors, provided it does not exceed four years"],
        rights_en=["the ordinary general assembly may remove some or all board members even if the "
                   "articles of association stipulate otherwise",
                   "board members may be re-elected unless the articles of association provide otherwise"],
        conditions_en=["the term of the board of directors must not exceed four years",
                       "the Regulations shall specify the voting method for electing board members",
                       "the articles of association may specify the method of forming the board, "
                       "subject to the rules set out in the Regulations"],
        deadlines_en=["board term must not exceed four years"],
        legal_effects_en=["upon removal, the ordinary general assembly shall elect a new board or a "
                          "replacement for removed members"],
        competent_authorities_en=["ordinary general assembly",
                                  "Competent Authority (may specify the rules governing removal of "
                                  "board members by the ordinary general assembly)"],
        keywords_en=["ordinary general assembly", "election", "natural persons", "four years",
                     "removal", "Competent Authority"],
        search_queries_en=["Who elects the board of directors of a joint-stock company?",
                            "What is the maximum term of a JSC board of directors?",
                            "Can the ordinary general assembly remove board members?"]),

    rec(
        "en-llm-book4-art071", [71],
        "Disclosure of Interest in Transactions and Contracts",
        "mixed",
        actors_en=["board member", "board of directors", "general assembly", "company auditor",
                   "competent judicial authority", "company"],
        obligations_en=["a board member shall immediately disclose to the board of directors any "
                        "direct or indirect interest in company transactions or contracts",
                        "such disclosure shall be recorded in the minutes of the board meeting",
                        "the board shall notify the general assembly, with a special report prepared "
                        "by the company auditor, of transactions and contracts in which a board "
                        "member has an interest"],
        prohibitions_en=["the interested board member may not vote on a decision by the board of "
                         "directors and the general assemblies relating to such transactions and "
                         "contracts"],
        legal_effects_en=["if the member fails to disclose, the company or any person with interest "
                          "may petition the competent judicial authority to invalidate the contract "
                          "or obligate the member to return any profit or benefit realized"],
        liability_en=["the interested board member bears liability for damages arising from such "
                      "transactions and contracts",
                      "other board members bear liability for omission or negligence in performing "
                      "their duties in violation of the disclosure rule",
                      "board members who object are not liable if their objection is explicitly "
                      "recorded in the meeting minutes"],
        competent_authorities_en=["competent judicial authority", "company auditor"],
        cross_references_en=["Article 27 of this Law"],
        keywords_en=["disclosure of interest", "conflict of interest", "abstain from voting",
                     "board minutes", "auditor report", "liability"],
        search_queries_en=["Must a board member disclose a conflict of interest?",
                            "Can an interested board member vote on the related contract?",
                            "What happens if a board member fails to disclose an interest?"]),

    rec(
        "en-llm-book4-art072", [72],
        "Granting Loans",
        "prohibition",
        actors_en=["joint-stock company", "board members", "relatives", "third party",
                   "competent judicial authority", "banks and other financing companies",
                   "general assembly", "Competent Authority"],
        prohibitions_en=["the company may not grant any type of loan to its board members",
                         "the company may not act as a guarantor or provide guarantees for loans its "
                         "board members conclude with a third party",
                         "the prohibition applies to any loan or guarantee provided to their relatives"],
        legal_effects_en=["any contract concluded in violation of this provision is null and void",
                          "the company may petition the competent judicial authority for compensation "
                          "from the violator for damage sustained"],
        exceptions_en=["banks and other financing companies may, within their purposes and terms, "
                       "grant loans or extend credit to their board members or guarantee their loans",
                       "loans and guarantees granted under employee incentive programs approved per "
                       "the articles of association or by a general assembly decision"],
        competent_authorities_en=["competent judicial authority",
                                  "Competent Authority (may determine the rules and cases prohibiting "
                                  "loans or guarantees to shareholders)"],
        keywords_en=["prohibition on loans", "board members", "guarantee", "null and void",
                     "employee incentive programs", "banks"],
        search_queries_en=["Can a joint-stock company lend to its board members?",
                            "Are there exceptions to the loan prohibition for board members?"]),

    rec(
        "en-llm-book4-art075", [75],
        "Sale of Company Assets",
        "mandatory",
        actors_en=["board of directors", "general assembly", "Competent Authority"],
        obligations_en=["the board of directors must obtain the general assembly's approval for the "
                        "sale of company assets whose value exceeds 50% of total assets, whether in "
                        "one transaction or more"],
        conditions_en=["the percentage is calculated from the date the first transaction is concluded "
                       "within the previous 12 months"],
        monetary_thresholds=[
            {"amount": 0.5, "currency": "ratio",
             "description_en": "General assembly approval is required to sell company assets whose "
                               "value exceeds 50% of total assets."},
        ],
        deadlines_en=["the percentage is calculated over the previous 12 months from the first "
                      "transaction"],
        legal_effects_en=["the transaction that leads to the sale of more than 50% of asset value "
                          "requires the general assembly's approval"],
        competent_authorities_en=["general assembly",
                                  "Competent Authority (may exclude certain acts and dispositions "
                                  "from this Article)"],
        keywords_en=["sale of assets", "50%", "general assembly approval", "12 months"],
        search_queries_en=["When does selling company assets require general assembly approval?",
                            "How is the 50% asset-sale threshold calculated?"]),

    rec(
        "en-llm-book4-art077", [77],
        "Powers of Board of Directors",
        "mixed",
        actors_en=["board of directors", "general assembly", "company"],
        rights_en=["the board of directors has all the powers necessary to manage the company and "
                   "achieve its purposes (without prejudice to the powers of the general assembly)",
                   "the board may delegate one or more of its members or others to carry out certain acts"],
        exceptions_en=["acts or dispositions falling within the powers of the general assembly, "
                       "excluded by a special provision in this Law or the articles of association",
                       "the company is not bound where the counterparty acts in bad faith or knows "
                       "the acts are beyond the board's powers"],
        legal_effects_en=["the company is bound by all acts and dispositions performed in its name by "
                          "the board, even if beyond the board's powers (subject to the bad-faith "
                          "exception)"],
        keywords_en=["board powers", "management of the company", "delegation", "binding the company",
                     "bad faith"],
        search_queries_en=["What powers does the board of directors of a JSC have?",
                            "Is the company bound by acts of the board beyond its powers?"]),
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
        "layer_status": "pilot_extension",
        "scope": "book4_section2_board_and_governance",
        "book": 4,
        "section_key": "board_and_governance",
        "section_title_en": "Board of Directors and Governance",
        "article_range": "67-83",
        "explicit_articles": COVERED,
        "uncovered_articles_excluded": UNCOVERED,
        "summary_source": ("legal_rule_text_en is copied verbatim from english_reference_text in "
                           + SRC_REL + " (no model-generated English summary)."),
        "english_source_status": "official_guidance_translation",
        "governing_text_language": "ar",
        "disclaimer_en": ("English Legal LLM-ready metadata over the official English guidance "
                          "reference; the governing/binding text is the Arabic original. Book Four "
                          "Section 2 provision-covered articles only — not full English Legal LLM "
                          "coverage. Not legal advice."),
        "records": RECORDS,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("wrote %s with %d English legal LLM records (articles %s)" % (OUT, len(RECORDS), COVERED))


if __name__ == "__main__":
    main()
