#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The corpus citation pattern must survive how the text is encoded.

CITE runs on raw judgment text, not on the canonical record, so the two
representation faults found after the held-out evaluations -- Arabic
Presentation Forms and combining marks -- reach it directly. Every form
asserted here is attested: the shaped forms in the securities-committee
bulletins (SOURCE_C.md), the marks in ministry judgments, where 234 citations
corpus-wide sat behind a single shadda.

The refusals matter as much as the parses. «عمادة» and «شهادة» end in the
same three letters as «مادة» and are not citations.
"""

from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "docs", "research", "arabic_paper"))

V = pytest.importorskip("voice_attribution")


class TestCombiningMarks:
    """A mark on the head noun must not hide the citation."""

    def test_plain_form_still_parses(self):
        assert V.CITE.findall("المادة (16) من نظام المحاكم التجارية") == [
            ("16", "نظام المحاكم التجارية")]

    def test_shadda_on_the_head_noun(self):
        assert V.CITE.findall("المادَّة (69) من نظام الإفلاس") == [
            ("69", "نظام الإفلاس")]

    def test_every_mark_this_project_has_seen(self):
        for head in ("المَادة", "المادّة", "المادةُ", "المٰادة"):
            got = V.CITE.findall(f"{head} (180) من نظام الشركات")
            assert got == [("180", "نظام الشركات")], head

    def test_a_prefixed_head_noun_with_a_mark(self):
        assert V.CITE.findall("وفقاً للمادَّة (90) من اللائحة التنفيذية") == [
            ("90", "اللائحة التنفيذية")]


class TestPresentationForms:
    """Shaped glyphs are a different string and need normalise() first."""

    SHAPED = "ﺍﻟﻤﺎﺩﺓ (29) ﻣﻦ ﻧﻈﺎﻡ ﺍﻹﺛﺒﺎﺕ"

    def test_shaped_text_does_not_parse_raw(self):
        # asserted, not lamented: a pattern cannot absorb a different
        # codepoint for every letter, so the caller must normalise
        assert V.CITE.findall(self.SHAPED) == []

    def test_normalise_recovers_it(self):
        assert V.CITE.findall(V.normalise(self.SHAPED)) == [
            ("29", "نظام الإثبات")]

    def test_normalise_leaves_ordinary_text_alone(self):
        plain = "المادة (29) من نظام الإثبات"
        assert V.normalise(plain) == plain

    def test_normalise_strips_marks_and_tatweel_too(self):
        assert V.normalise("الـمادَّة") == "المادة"


class TestRefusals:
    """Words that end in the same letters are not citations."""

    def test_deanship_is_not_an_article(self):
        assert V.CITE.findall("عمادة الكلية من نظام كذا") == []

    def test_certificate_is_not_an_article(self):
        assert V.CITE.findall("شهادة (3) من نظام كذا") == []

    def test_a_marked_lookalike_is_still_refused(self):
        assert V.CITE.findall("عمادَّة الكلية من نظام كذا") == []
