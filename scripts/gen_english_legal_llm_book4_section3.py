#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
English Legal LLM-ready layer — Book Four, Section 3
(General Assemblies / الجمعية العامة).

Adds English Legal LLM-ready records for the Book Four Section 3 provision-covered
articles ONLY — 85, 87, 92, 93, 99, 101, 102 (7 article_reference records). NOT full
English Legal LLM coverage.

The core field `legal_rule_text_en` is copied VERBATIM from the corresponding English
reference record's `english_reference_text` in
`data/english_reference/book4_section3_en_reference.json`, keyed by article number, so
the layer can never drift and contains NO model-generated English summary. There is NO
`legal_rule_summary_en`. Only the DERIVED structured metadata is authored here, and every
actor/obligation/condition/prohibition/authority/threshold/deadline/liability/effect is
traceable to that article's own verbatim text (no concepts imported from other articles).

Trust posture: English is official GUIDANCE / reference only; Arabic remains governing
(governing_text_language = ar); manual_review_status = needs_manual_check; not legal advice.

It does NOT create records for the uncovered Section-3 articles (84, 86, 88, 89, 90, 91,
94, 95, 96, 97, 98, 100 — including the owner-reconciled 84/89/100), for other Book Four
sections, or for Books 1-3. It does NOT modify the English reference / Arabic / Chinese
data, and makes no network calls.

Reads : data/english_reference/book4_section3_en_reference.json
Writes: data/english_legal_llm/book4_section3_en_legal_llm.json
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_REL = "data/english_reference/book4_section3_en_reference.json"
SRC = os.path.join(ROOT, SRC_REL)
OUT = os.path.join(ROOT, "data", "english_legal_llm", "book4_section3_en_legal_llm.json")

COVERED = [85, 87, 92, 93, 99, 101, 102]
UNCOVERED = [84, 86, 88, 89, 90, 91, 94, 95, 96, 97, 98, 100]

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
        "en-llm-book4-art085", [85],
        "Powers of the Extraordinary General Assembly",
        "mixed",
        actors_en=["extraordinary general assembly", "shareholders", "company"],
        rights_en=["the extraordinary general assembly may amend the company's articles of association",
                   "the extraordinary general assembly may decide on the continuation or dissolution "
                   "of the company",
                   "the extraordinary general assembly may approve the company's purchase of its shares"],
        exceptions_en=["amending the articles may not deprive a shareholder of his fundamental rights "
                       "(dividends, share of net assets upon liquidation, attending and voting at "
                       "assemblies, disposition of shares, and access to records/derivative actions)"],
        conditions_en=["amendments which increase the financial burden of shareholders require "
                       "unanimous approval by shareholders"],
        legal_effects_en=["the extraordinary general assembly's powers cover amending the articles, "
                          "deciding continuation/dissolution, and approving share buy-back"],
        keywords_en=["extraordinary general assembly", "articles of association", "dissolution",
                     "fundamental rights", "unanimous approval", "share buy-back"],
        search_queries_en=["What are the powers of the extraordinary general assembly?",
                            "When do shareholders' amendments require unanimous approval?"]),

    rec(
        "en-llm-book4-art087", [87],
        "Powers of the Ordinary General Assembly",
        "mixed",
        actors_en=["ordinary general assembly", "board members", "company auditor"],
        rights_en=["the ordinary general assembly may elect and remove board members",
                   "the ordinary general assembly may appoint a company auditor (or more), determine "
                   "his fees, and reappoint or remove him"],
        obligations_en=["reviewing and discussing the board's report",
                        "reviewing and discussing the company's financial statements",
                        "reviewing the auditor's report and making a decision thereon"],
        legal_effects_en=["the ordinary general assembly decides on board proposals for distributing "
                          "dividends and creates the company's reserves and determines their uses"],
        keywords_en=["ordinary general assembly", "board members", "company auditor", "financial "
                     "statements", "dividends", "reserves"],
        search_queries_en=["What are the powers of the ordinary general assembly?",
                            "Who appoints the company auditor of a joint-stock company?"]),

    rec(
        "en-llm-book4-art092", [92],
        "Quorum of Ordinary General Assembly Meetings",
        "procedural",
        actors_en=["ordinary general assembly", "shareholders"],
        conditions_en=["an ordinary general assembly meeting is valid only if attended by shareholders "
                       "representing at least a quarter of the voting shares (the articles may raise "
                       "it, not exceeding half)",
                       "the second meeting is valid regardless of the number of voting shares represented"],
        deadlines_en=["a second meeting shall be called within 30 days following the date set for the "
                      "first meeting",
                      "the second meeting may be held one hour after the end of the period set for the "
                      "first meeting"],
        legal_effects_en=["decisions are passed by the majority vote of voting rights represented"],
        cross_references_en=["Article 91 of this Law"],
        keywords_en=["ordinary general assembly", "quorum", "quarter of voting shares", "second "
                     "meeting", "30 days", "majority vote"],
        search_queries_en=["What is the quorum for an ordinary general assembly meeting?",
                            "What happens if the OGM quorum is not met?"]),

    rec(
        "en-llm-book4-art093", [93],
        "Quorum of Extraordinary General Assembly Meetings",
        "procedural",
        actors_en=["extraordinary general assembly", "shareholders", "board of directors"],
        conditions_en=["the first meeting is valid only if attended by shareholders representing at "
                       "least half of the voting shares (the articles may raise it, not exceeding two "
                       "thirds)",
                       "the second meeting is valid if attended by at least a quarter of the voting "
                       "shares; the third meeting is valid regardless of attendance"],
        deadlines_en=["decisions required to be registered with the Commercial Register shall be "
                      "registered by the board of directors within 15 days from their issuance date"],
        legal_effects_en=["decisions are passed by two-thirds of the voting shares represented",
                          "decisions on capital increase/decrease, term extension, early dissolution, "
                          "merger, or division require three-quarters of the voting shares represented"],
        cross_references_en=["Article 91 of this Law"],
        keywords_en=["extraordinary general assembly", "quorum", "two-thirds", "three-quarters",
                     "Commercial Register", "15 days"],
        search_queries_en=["What is the quorum for an extraordinary general assembly meeting?",
                            "Which EGM decisions require a three-quarters majority?"]),

    rec(
        "en-llm-book4-art099", [99],
        "Objection to Shareholder Assembly Decisions",
        "procedural",
        actors_en=["shareholder", "competent judicial authority", "shareholder assembly"],
        rights_en=["a shareholder may petition the competent judicial authority to invalidate a "
                   "decision issued by the shareholder assembly in violation of the Law or the "
                   "articles of association"],
        conditions_en=["the shareholder must have objected to the decision during the meeting or been "
                       "absent for a valid reason",
                       "the plaintiff must be a shareholder upon filing the lawsuit and throughout its "
                       "proceedings"],
        exceptions_en=["without prejudice to the rights of bona fide third parties"],
        deadlines_en=["an invalidation lawsuit shall not be heard after the lapse of 90 days from the "
                      "date the decision is issued"],
        competent_authorities_en=["competent judicial authority"],
        keywords_en=["objection", "invalidate decision", "competent judicial authority", "90 days",
                     "shareholder status"],
        search_queries_en=["Can a shareholder challenge a general assembly decision?",
                            "What is the time limit to file an invalidation lawsuit?"]),

    rec(
        "en-llm-book4-art101", [101],
        "Quorum for Issuance of a Decision by Circulation",
        "procedural",
        actors_en=["ordinary general assembly", "extraordinary general assembly", "shareholders"],
        conditions_en=["decisions within the ordinary general assembly's powers pass by circulation if "
                       "approved by shareholder(s) representing the majority of voting rights (the "
                       "articles may require a higher percentage)",
                       "decisions within the extraordinary general assembly's powers pass by "
                       "circulation if approved by shareholder(s) representing at least 75% of voting "
                       "rights (the articles may require a higher percentage)"],
        monetary_thresholds=[
            {"amount": 0.75, "currency": "ratio",
             "description_en": "Decisions by circulation within the EGM's powers require approval of "
                               "shareholders representing at least 75% of voting rights."},
        ],
        legal_effects_en=["decisions issued by circulation shall be recorded in minutes and entered in "
                          "the special register"],
        cross_references_en=["Article 97 of this Law"],
        keywords_en=["decision by circulation", "unlisted joint-stock companies", "75%", "majority of "
                     "voting rights", "special register"],
        search_queries_en=["How are general assembly decisions issued by circulation?",
                            "What majority is needed for EGM decisions by circulation?"]),

    rec(
        "en-llm-book4-art102", [102],
        "Request for Inspection of the Company",
        "procedural",
        actors_en=["shareholders", "competent judicial authority", "board members", "auditor",
                   "general assembly"],
        rights_en=["a shareholder (or more) representing at least 5% of the company's capital may "
                   "petition the competent judicial authority to order the inspection of the company"],
        conditions_en=["the conduct of the board members or the auditor in relation to company affairs "
                       "raises suspicion",
                       "the competent judicial authority may order the petitioner to provide a "
                       "guarantee if requested by the company"],
        monetary_thresholds=[
            {"amount": 0.05, "currency": "ratio",
             "description_en": "Shareholders representing at least 5% of the company's capital may "
                               "petition for an inspection of the company."},
        ],
        legal_effects_en=["the competent judicial authority may order the inspection at the "
                          "petitioner's expense, order precautionary measures, call the general "
                          "assembly, remove board members and the auditor, and appoint qualified "
                          "supervisors and determine their powers and term"],
        competent_authorities_en=["competent judicial authority"],
        keywords_en=["inspection of the company", "5% of capital", "competent judicial authority",
                     "removal of board members", "precautionary measures"],
        search_queries_en=["Who can request an inspection of a joint-stock company?",
                            "What may the court order upon a company inspection?"]),
]


def main():
    got = [r["article_numbers"] for r in RECORDS]
    assert got == [[n] for n in COVERED], got
    covered = {n for g in got for n in g}
    assert covered == set(COVERED), covered
    assert not (covered & set(UNCOVERED)), covered
    assert not ({84, 89, 100} & covered), "owner-reconciled 84/89/100 must NOT get a record"
    for r in RECORDS:
        assert r["record_type"] == "article_reference", r["record_id"]
        (n,) = r["article_numbers"]
        assert r["legal_rule_text_en"] == REFTEXT[n], r["record_id"]
        assert "legal_rule_summary_en" not in r, r["record_id"]

    payload = {
        "layer_id": "sa-companies-english-legal-llm",
        "layer_status": "pilot_extension",
        "scope": "book4_section3_general_assemblies",
        "book": 4,
        "section_key": "general_assemblies",
        "section_title_en": "General Assemblies",
        "article_range": "84-102",
        "explicit_articles": COVERED,
        "uncovered_articles_excluded": UNCOVERED,
        "summary_source": ("legal_rule_text_en is copied verbatim from english_reference_text in "
                           + SRC_REL + " (no model-generated English summary)."),
        "english_source_status": "official_guidance_translation",
        "governing_text_language": "ar",
        "disclaimer_en": ("English Legal LLM-ready metadata over the official English guidance "
                          "reference; the governing/binding text is the Arabic original. Book Four "
                          "Section 3 provision-covered articles only (84/89/100 remain uncovered) — "
                          "not full English Legal LLM coverage. Not legal advice."),
        "records": RECORDS,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("wrote %s with %d English legal LLM records (articles %s)" % (OUT, len(RECORDS), COVERED))


if __name__ == "__main__":
    main()
