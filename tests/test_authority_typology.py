#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The authority typology must survive the six defects the gold sample found.

Every string here is attested in the corpus and was read by hand. The
refusals matter as much as the classifications: five of the six defects were
rules firing on text that was not what they claimed.
"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "docs", "research", "contemporary"))
sys.path.insert(0, os.path.join(ROOT, "docs", "research", "arabic_paper"))

A = pytest.importorskip("authority")


def types(text):
    return {m["type"] for m in A.mentions(text, {})}


def rules(text):
    return {m["rule"] for m in A.mentions(text, {})}


class TestPossessiveReferent:
    """«في مادته (N)» belongs to whatever was named before it.

    Nine of nine validation items were statutes in instrument-first order.
    Before the referent was resolved, all nine were labelled contract.
    """

    def test_statute_named_before(self):
        t = "واستناداً إلى نص نظام التحكيم في مادته (11) على أنه"
        assert "statute.possessive" in rules(t)

    def test_contract_named_before(self):
        t = "العقد الموقع بين الطرفين والذي نص على شرط التحكيم في مادته (16)"
        assert "contract.possessive" in rules(t)

    def test_no_referent_is_not_guessed(self):
        assert A.mentions("وقد جاء في مادته (5) ما يلي", {}) == []


class TestQuotedPassages:
    """Article 164 lists «العرف، أو العادة المستقرة» among the factors a court
    must weigh. Tens of thousands of judgments quote it. Those are the
    legislator's words, and counting them as the court invoking custom was the
    largest single error in the first sample."""

    QUOTED = ('واستناداً للمادة (164) من اللائحة ونصها: "وتراعي المحكمة الآتي:'
              ' د - العرف، أو العادة المستقرة والمتعارف عليه" وحيث إن العرف '
              'التجاري استقر على خلافه')

    def test_the_quoted_marker_is_flagged(self):
        inside = [m for m in A.mentions(self.QUOTED, {}) if m["inQuote"]]
        assert inside and all(m["type"] == "custom" for m in inside)

    def test_the_courts_own_marker_is_not(self):
        outside = [m for m in A.mentions(self.QUOTED, {})
                   if m["type"] == "custom" and not m["inQuote"]]
        assert len(outside) == 1

    def test_the_citation_itself_is_not_swallowed(self):
        st = [m for m in A.mentions(self.QUOTED, {}) if m["type"] == "statute"]
        assert st and not st[0]["inQuote"]


class TestHadithAgainstAgreement:
    """«المتفق عليه» is «the agreed-upon». «متفق عليه» is the hadith grading.
    Conflating them produced 16,279 hits where 6,942 were real."""

    def test_the_grading_is_a_hadith(self):
        assert "hadith" in types("رواه الشيخان وهو متفق عليه")

    def test_agreed_upon_is_not(self):
        for t in ("المبلغ المتفق عليه", "شرط التحكيم المتفق عليه",
                  "في المدة المتفق عليها"):
            assert "hadith" not in types(t), t

    def test_the_ligature_is_read(self):
        assert "hadith" in types("استنادًا لقوله ﷺ: البينة على المدعي")


class TestDiscretionIsNotEvaluation:
    def test_named_power_counts(self):
        assert "discretion" in types("ولما للدائرة من سلطة تقديرية في التقدير")

    def test_weighing_evidence_does_not(self):
        assert "discretion" not in types("وهو ما تراه الدائرة كافيًا للاستحقاق")


class TestRecallAdditions:
    """Markers the random-sentence half found with no rule at all."""

    def test_settled_in_fiqh(self):
        assert "fiqh_source" in types("ومن المستقر فقهًا القضاءُ على الغائب")

    def test_settled_in_precedent(self):
        assert "judicial_principle" in types("وبما أن من المقرر قضاءً أن الإثبات")

    def test_bare_metaqarrar(self):
        assert "fiqh_source" in types("كما هو متقرر فقهاً وقضاءً")

    def test_book_without_the_article(self):
        assert "fiqh_source" in types("انتهى من مجموع فتاوى (٣٠/٢٤)")


class TestStructuralVoice:
    def test_reasons_belong_to_the_bench(self):
        m = {"segment": "reasoning", "speaker": "party", "inQuote": False}
        assert A.voice(m) == "court_reasoning"

    def test_a_quoted_party_submission_does_not(self):
        m = {"segment": "reasoning", "speaker": "party", "inQuote": True}
        assert A.voice(m) == "party_in_reasons"

    def test_recital_keeps_the_cue(self):
        assert A.voice({"segment": "recital", "speaker": "party"}) == "party_argument"
