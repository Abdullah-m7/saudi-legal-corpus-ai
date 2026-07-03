#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
English Legal LLM-ready layer — Book Four, Section 5
(Finance, Profits, and Capital Changes / المالية والأرباح وتغيير رأس المال).

Adds English Legal LLM-ready records for the Book Four Section 5 provision-covered
articles ONLY — 123, 124, 126, 127, 128, 129, 130, 132, 133 (9 article_reference
records). This completes Book Four Sections 1-5 for the English Legal LLM layer; it is
still NOT full English Legal LLM coverage (no Books 1-3).

The core field `legal_rule_text_en` is copied VERBATIM from the corresponding English
reference record's `english_reference_text` in
`data/english_reference/book4_section5_en_reference.json`, keyed by article number, so
the layer can never drift and contains NO model-generated English summary. There is NO
`legal_rule_summary_en`. Only the DERIVED structured metadata is authored here, and every
actor/obligation/condition/prohibition/authority/threshold/deadline/liability/effect is
traceable to that article's own verbatim text (no concepts imported from other articles).

Trust posture: English is official GUIDANCE / reference only; Arabic remains governing
(governing_text_language = ar); manual_review_status = needs_manual_check; not legal advice.

It does NOT create records for the uncovered Section-5 articles (121, 122, 125, 131, 134,
135, 136, 137). Articles 134 & 135 in particular are excluded (cross-reference only in
the model-1b Section 5 scope). It does NOT modify the English reference / Arabic / Chinese
data, and makes no network calls.

Reads : data/english_reference/book4_section5_en_reference.json
Writes: data/english_legal_llm/book4_section5_en_legal_llm.json
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_REL = "data/english_reference/book4_section5_en_reference.json"
SRC = os.path.join(ROOT, SRC_REL)
OUT = os.path.join(ROOT, "data", "english_legal_llm", "book4_section5_en_legal_llm.json")

COVERED = [123, 124, 126, 127, 128, 129, 130, 132, 133]
UNCOVERED = [121, 122, 125, 131, 134, 135, 136, 137]

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
        "en-llm-book4-art123", [123],
        "Creation of Reserves",
        "permissive",
        actors_en=["company", "Competent Authority", "ordinary general assembly", "shareholders"],
        rights_en=["the articles of association may provide for setting aside a certain percentage of "
                   "the net profit to create a reserve for specified purposes",
                   "the ordinary general assembly may, when determining dividends, create other "
                   "reserves and may allocate amounts from the net profit for social objectives "
                   "benefiting the company's staff"],
        conditions_en=["the Competent Authority may set the rules for creating such reserves"],
        competent_authorities_en=["Competent Authority", "ordinary general assembly"],
        keywords_en=["reserves", "net profit", "ordinary general assembly", "dividends",
                     "social objectives"],
        search_queries_en=["How may a joint-stock company create reserves?",
                            "Can the ordinary general assembly create additional reserves?"]),

    rec(
        "en-llm-book4-art124", [124],
        "Use of Reserves",
        "mixed",
        actors_en=["extraordinary general assembly", "ordinary general assembly", "board of directors",
                   "Competent Authority", "shareholders"],
        prohibitions_en=["the reserve allocated for specific purposes may not be used except pursuant "
                         "to a decision by the extraordinary general assembly"],
        rights_en=["if the reserve is not allocated for a specific purpose, the ordinary general "
                   "assembly may, upon the board of directors' recommendation, decide to use it for "
                   "the benefit of the company or the shareholders",
                   "the ordinary general assembly may use retained earnings and distributable "
                   "reserves to pay the remaining value of the share or part thereof"],
        conditions_en=["fairness among shareholders must be observed",
                       "the Competent Authority may set the rules for using such reserves"],
        competent_authorities_en=["extraordinary general assembly", "ordinary general assembly",
                                  "Competent Authority"],
        keywords_en=["use of reserves", "retained earnings", "distributable reserves",
                     "extraordinary general assembly", "fairness among shareholders"],
        search_queries_en=["When may a company use its allocated reserve?",
                            "Can retained earnings be used to pay the remaining value of shares?"]),

    rec(
        "en-llm-book4-art126", [126],
        "Methods of Capital Increase",
        "procedural",
        actors_en=["extraordinary general assembly", "relevant creditors",
                   "experts or accredited valuers", "board of directors", "company's auditor",
                   "shareholders"],
        legal_effects_en=["capital may be increased by issuing new shares against cash or in-kind "
                          "contributions, against company debts, by capitalizing a reserve (bonus "
                          "shares distributed to shareholders for no consideration), or against debt "
                          "instruments or financing sukuk"],
        conditions_en=["issuing shares against company debts requires the consent of the relevant "
                       "creditors, at a value determined by the extraordinary general assembly after "
                       "the opinion of experts or accredited valuers and a board statement on the "
                       "origin and amount of the debts, accompanied by the auditor's report",
                       "bonus shares from a capitalized reserve are distributed to shareholders in "
                       "proportion to their original shares"],
        liability_en=["the board members who sign the debt statement are liable for its accuracy"],
        competent_authorities_en=["extraordinary general assembly"],
        keywords_en=["capital increase", "new shares", "debt-to-equity", "bonus shares",
                     "extraordinary general assembly", "creditors' consent"],
        search_queries_en=["What are the methods of increasing a joint-stock company's capital?",
                            "How are shares issued against company debts?"]),

    rec(
        "en-llm-book4-art127", [127],
        "Increase of Issued or Authorized Capital",
        "mixed",
        actors_en=["extraordinary general assembly", "company", "employees", "shareholders",
                   "Competent Authority"],
        rights_en=["the extraordinary general assembly may decide to increase the company's issued "
                   "capital or its authorized capital, if any",
                   "the extraordinary general assembly may allocate issued shares to the employees of "
                   "the company or any of its subsidiaries"],
        conditions_en=["the issued capital must have been paid in full (unless the unpaid portion "
                       "relates to shares against the conversion of debt instruments/sukuk whose "
                       "conversion period has not expired)",
                       "the nominal value of the new shares must equal the nominal value of the "
                       "original shares of the same type or class"],
        prohibitions_en=["shareholders may not exercise their preemptive rights on issued shares "
                         "allocated for employees"],
        competent_authorities_en=["extraordinary general assembly", "Competent Authority"],
        keywords_en=["issued capital", "authorized capital", "paid in full", "employee shares",
                     "preemptive rights", "nominal value"],
        search_queries_en=["Who may decide to increase the issued or authorized capital?",
                            "Can shares be allocated to employees on a capital increase?"]),

    rec(
        "en-llm-book4-art128", [128],
        "Preemptive Subscription Rights to New Shares",
        "mixed",
        actors_en=["shareholder", "extraordinary general assembly", "board of directors"],
        rights_en=["a shareholder who owns the share on the date of the extraordinary general "
                   "assembly's decision (or the board of directors' decision within the authorized "
                   "capital) approving the increase has a preemptive right to subscribe to new shares "
                   "issued against cash contributions"],
        obligations_en=["the shareholder shall be notified of the right by registered mail or by any "
                        "means of technology, and notified of the capital-increase decision, the "
                        "conditions and method of subscription, and the dates on which subscription "
                        "begins and ends"],
        conditions_en=["the preemptive right applies to new shares issued against cash contributions, "
                       "subject to the type and class of shares owned"],
        keywords_en=["preemptive subscription right", "new shares", "cash contributions",
                     "notification", "subscription dates"],
        search_queries_en=["Who has a preemptive right to subscribe to new shares?",
                            "How is a shareholder notified of a preemptive right?"]),

    rec(
        "en-llm-book4-art129", [129],
        "Suspension of Preemptive Rights",
        "permissive",
        actors_en=["extraordinary general assembly", "shareholders", "non-shareholders", "company"],
        rights_en=["the extraordinary general assembly may suspend the preemptive rights of "
                   "shareholders to subscribe to a cash capital increase, or grant such rights to "
                   "non-shareholders, in cases it deems beneficial to the company"],
        conditions_en=["suspension or grant is permitted only if provided for in the company's "
                       "articles of association"],
        competent_authorities_en=["extraordinary general assembly"],
        keywords_en=["suspension of preemptive rights", "extraordinary general assembly",
                     "non-shareholders", "articles of association"],
        search_queries_en=["Can preemptive rights be suspended?",
                            "May preemptive rights be granted to non-shareholders?"]),

    rec(
        "en-llm-book4-art130", [130],
        "Sale or Assignment of Preemptive Rights",
        "permissive",
        actors_en=["shareholder"],
        rights_en=["a shareholder may sell or assign his preemptive rights, with or without financial "
                   "consideration, subject to the Regulations"],
        conditions_en=["the sale or assignment is subject to the Regulations"],
        keywords_en=["sale of preemptive rights", "assignment", "financial consideration",
                     "Regulations"],
        search_queries_en=["Can a shareholder sell his preemptive rights?",
                            "May preemptive rights be assigned without consideration?"]),

    rec(
        "en-llm-book4-art132", [132],
        "Company Losses",
        "mandatory",
        actors_en=["joint-stock company", "board of directors", "extraordinary general assembly"],
        obligations_en=["if the losses reach half of the issued capital, the board of directors shall "
                        "announce the losses and related recommendations within 60 days of its "
                        "knowledge thereof",
                        "the board of directors shall call an extraordinary general assembly meeting "
                        "within 180 days to consider the company's continuation (by measures to "
                        "resolve the losses) or its dissolution"],
        conditions_en=["the duty is triggered where the losses amount to half of the issued capital"],
        deadlines_en=["announce the losses within 60 days of the board's knowledge",
                      "call the extraordinary general assembly within 180 days"],
        competent_authorities_en=["extraordinary general assembly"],
        keywords_en=["grave losses", "half of the issued capital", "60 days", "180 days",
                     "continuation or dissolution"],
        search_queries_en=["What must the board do if losses reach half the capital?",
                            "What are the deadlines for the company-losses procedure?"]),

    rec(
        "en-llm-book4-art133", [133],
        "Methods of Capital Decrease",
        "procedural",
        actors_en=["company", "shareholder"],
        legal_effects_en=["capital may be decreased by cancelling a number of shares equal to the "
                          "amount to be decreased; reducing the nominal value of a share by cancelling "
                          "a part equal to the losses; reducing the nominal value by returning a part "
                          "to the shareholder or relieving him from the unpaid amount; or the "
                          "company's purchase and cancellation of a number of its shares"],
        keywords_en=["capital decrease", "cancellation of shares", "nominal value", "share buy-back"],
        search_queries_en=["What are the methods of decreasing a joint-stock company's capital?",
                            "How can a company reduce the nominal value of shares?"]),
]


def main():
    got = [r["article_numbers"] for r in RECORDS]
    assert got == [[n] for n in COVERED], got
    covered = {n for g in got for n in g}
    assert covered == set(COVERED), covered
    assert not (covered & set(UNCOVERED)), covered
    assert not ({134, 135} & covered), "Articles 134/135 must NOT get a record"
    for r in RECORDS:
        assert r["record_type"] == "article_reference", r["record_id"]
        (n,) = r["article_numbers"]
        assert r["legal_rule_text_en"] == REFTEXT[n], r["record_id"]
        assert "legal_rule_summary_en" not in r, r["record_id"]

    payload = {
        "layer_id": "sa-companies-english-legal-llm",
        "layer_status": "pilot_extension",
        "scope": "book4_section5_finance_profits_and_capital_changes",
        "book": 4,
        "section_key": "finance_profits_and_capital_changes",
        "section_title_en": "Finance, Profits, and Capital Changes",
        "article_range": "121-137",
        "explicit_articles": COVERED,
        "uncovered_articles_excluded": UNCOVERED,
        "summary_source": ("legal_rule_text_en is copied verbatim from english_reference_text in "
                           + SRC_REL + " (no model-generated English summary)."),
        "english_source_status": "official_guidance_translation",
        "governing_text_language": "ar",
        "disclaimer_en": ("English Legal LLM-ready metadata over the official English guidance "
                          "reference; the governing/binding text is the Arabic original. Book Four "
                          "Section 5 provision-covered articles only (134 & 135 remain uncovered) — "
                          "completes Book Four Sections 1-5 but not Books 1-3. Not legal advice."),
        "records": RECORDS,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("wrote %s with %d English legal LLM records (articles %s)" % (OUT, len(RECORDS), COVERED))


if __name__ == "__main__":
    main()
