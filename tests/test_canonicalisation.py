#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The canonicaliser must repair extraction artefacts and nothing else.

Each rule is deterministic, individually switchable and individually counted.
The dangerous one is lam_swap, which reverses a transposed definite article:
the shape it looks for -- alif, consonant, lam -- is also the shape of real
Arabic imperatives, so it is gated per letter on evidence from the document
being read, and these tests hold that gate shut on ordinary Arabic.
"""

from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "docs", "research", "canon"))

canonical = pytest.importorskip("canonical")


class TestRawIsPreserved:
    def test_raw_is_returned_untouched(self):
        raw = "المادة ـــ (١٢)"
        rec = canonical.canonicalise(raw)
        assert rec["raw"] == raw
        assert rec["canonical"] != raw

    def test_every_rule_reports_its_edit_count(self):
        rec = canonical.canonicalise("المادة ـ ١٢")
        assert [t["rule"] for t in rec["transformations"]] == canonical.RULES
        assert all("edits" in t for t in rec["transformations"])

    def test_rules_can_be_switched_off_for_ablation(self):
        rec = canonical.canonicalise("١٢ ـ", rules=["digits"])
        assert rec["canonical"] == "12 ـ"


class TestDeterministicRules:
    def test_bidi_controls_are_removed(self):
        assert canonical.canonicalise("‫المادة‬")["canonical"] == "المادة"

    def test_tatweel_is_removed(self):
        assert canonical.canonicalise("ضـــريبة")["canonical"] == "ضريبة"

    def test_arabic_indic_digits_become_latin(self):
        assert canonical.canonicalise("المادة ١٤٢")["canonical"] == "المادة 142"

    def test_extended_arabic_indic_digits_become_latin(self):
        assert canonical.canonicalise("۱۴۲")["canonical"] == "142"

    def test_number_pushed_out_of_its_brackets_is_put_back(self):
        assert canonical.canonicalise("المادة ( )142")["canonical"] == "المادة (142)"

    def test_transformations_are_idempotent(self):
        once = canonical.canonicalise("المادة ( )١٤٢ ـ")["canonical"]
        twice = canonical.canonicalise(once)["canonical"]
        assert once == twice


class TestLamSwapGate:
    def test_ordinary_arabic_is_never_repaired(self):
        # اجلس and اقلب match the shape and are real words
        text = "اجلس هنا واقلب الصفحة والمادة الأولى واضحة"
        assert canonical.canonicalise(text)["canonical"] == text

    def test_a_document_that_writes_the_article_correctly_is_left_alone(self):
        text = ("المادة الأولى والمادة الثانية والمحكمة والمملكة " * 30)
        assert canonical.canonicalise(text)["canonical"] == text

    def test_a_systematically_transposed_document_is_repaired(self):
        text = ("املادة الأولى واملستورد واملوحد واللجنة والجمارك " * 40)
        out = canonical.canonicalise(text)["canonical"]
        assert "املادة" not in out
        assert out.count("المادة") == 40

    def test_only_the_transposed_letter_is_repaired(self):
        # meem is broken; taa is not, and «اطلب» must survive
        text = ("املادة واملستورد اطلب الطلب " * 40)
        diag = canonical.lam_swap_diagnosis(text)
        assert diag["م"]["repair"] is True
        assert diag["ط"]["repair"] is False
        assert "اطلب" in canonical.canonicalise(text)["canonical"]

    def test_the_article_behind_a_proclitic_is_repaired_too(self):
        text = ("واملادة فاملستورد باملوحد املادة " * 40)
        out = canonical.canonicalise(text)["canonical"]
        assert "املادة" not in out and "واملادة" not in out


class TestSourcesAreNotCrossContaminated:
    def test_clean_api_text_is_untouched_except_tatweel(self):
        text = "المادة الخامسة والتسعون بعد المائة من نظام المحاكم التجارية"
        rec = canonical.canonicalise(text)
        assert rec["canonical"] == text
        assert all(t["edits"] == 0 for t in rec["transformations"])
