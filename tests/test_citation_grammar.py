#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The citation grammar must read what the courts wrote, and refuse the rest.

Every form asserted here is attested in hand-labelled data from one of the two
sources. The refusals are asserted as firmly as the parses: a parser that
answers where the document does not decide is not accurate, it is confident.
"""

from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "docs", "research", "citation"))

grammar = pytest.importorskip("grammar")
numerals = pytest.importorskip("numerals")
instruments = pytest.importorskip("instruments")


class TestOrdinals:
    def test_attested_forms(self):
        cases = {
            "الخامسة والتسعون": 95, "الحادية والسبعين": 71,
            "السابعة عشر": 17, "الثامنة والستين": 68, "الأربعين": 40,
            "السادسة والخمسون": 56, "الخامسة عشرة": 15, "العاشرة": 10,
            "الثالثة والستين": 63, "الثانية والأربعون": 42,
            "السابعة والأربعون": 47, "السادسة والستون": 66,
            "الثامنة والستين بعد المئة": 168, "العاشرة بعد المائة": 110,
            "الحادية والعشرون بعد المائة": 121, "المائتين": 200,
            "الثانية والخمسون بعد المئة": 152,
        }
        for text, want in cases.items():
            assert numerals.parse_ordinal(text) == want, text

    def test_the_ten_is_not_swallowed_by_the_teen_marker(self):
        # «العشرون» begins with «العشر». An optional «ال» in front of the
        # alternation let the shorter form match inside it and article 20 was
        # read as article 10, with no error anywhere.
        assert numerals.parse_ordinal("العشرون") == 20
        assert numerals.parse_ordinal("التاسعة والعشرين") == 29
        phrase, _ = numerals.ordinal_phrase(" العشرون من نظام", 0)
        assert phrase.strip() == "العشرون"

    def test_refuses_what_it_does_not_know(self):
        for junk in ("الفحم الحجري", "المصدرة", "سالفة الذكر", "المذكورة", ""):
            assert numerals.parse_ordinal(junk) is None


class TestDetection:
    def test_the_ordinary_noun_is_not_a_citation(self):
        # «مادة الفحم الحجري» is coal. Detection is by the number that
        # follows, not by a stop-word list.
        text = "أن قيمة المنصرف من مادة الفحم الحجري تدخل ضمن المصاريف"
        assert grammar.parse(text) == []

    def test_a_number_makes_it_a_citation(self):
        text = "استنادا للمادة (79) من الالئحة التنفيذية لنظام ضريبة القيمة المضافة،"
        [rec] = grammar.parse(text)
        assert rec["articleNumber"] == 79

    def test_digits_may_touch_the_word(self):
        text = "ال مادة74 مرافعات."
        [rec] = grammar.parse(text)
        assert rec["articleNumber"] == 74


class TestPackedPairs:
    def test_a_letter_side_is_the_paragraph(self):
        n, para, guessed = grammar.packed("2", "ب")
        assert (n, para, guessed) == (2, "ب", False)

    def test_two_digits_take_the_larger_as_the_article(self):
        assert grammar.packed("93", "1")[0] == 93
        assert grammar.packed("2", "76")[0] == 76

    def test_a_two_digit_pair_is_flagged_as_a_guess(self):
        # the corpus writes the pair in both orders; the record must say so
        assert grammar.packed("93", "1")[2] is True
        assert grammar.packed("2", "ب")[2] is False


class TestInstrumentNames:
    def test_one_instrument_under_four_names(self):
        names = ["الالئحة التنفيذية لجباية الزكاة", "لائحة جباية الزكاة",
                 "الالئحة التنفيذية لنظام الزكاة",
                 "لائحة جباية الزكاة الصادرة بعام 1438ه"]
        for other in names[1:]:
            assert instruments.same(names[0], other), other

    def test_spaces_inside_words_do_not_make_two_instruments(self):
        assert instruments.same("نظام المر افعات الشرعية",
                                "نظام المرافعات الشرعية")

    def test_a_statute_is_not_its_regulations(self):
        assert not instruments.same("نظام المرافعات الشرعية",
                                    "الالئحة التنفيذية لنظام المرافعات الشرعية")

    def test_a_bare_head_names_nothing(self):
        assert instruments.canonical("الالئحة التنفيذية") is None
        assert instruments.canonical("النظام") is None


class TestRefusals:
    def test_an_unattested_completion_is_refused(self):
        # the span runs past a line break into text that belongs elsewhere on
        # the page; no name in the document begins with it
        stock = {grammar._fold("الالئحة التنفيذية لجباية الزكاة"):
                 ("الالئحة التنفيذية لجباية الزكاة", 3)}
        text = "الالئحة التنفيذية\nالقوائم المالية لعام 2015م أن الأصل"
        assert grammar.resolve_name(text, 0, 17, stock) is None

    def test_a_proximal_anaphor_will_not_reach_past_the_nearest(self):
        # «ذاتها» means the one just named. When the one just named is a
        # statute and the clitic asks for regulations, the reference is
        # broken, and the next candidate back is a guess with a citation
        # attached to it.
        text = ("وبموجب نظام الشركات الصادر بالمرسوم الملكي، كما تنص "
                "المادة (العاشرة) من الالئحة ذاتها على")
        pos = text.index("من الالئحة ذاتها")
        bound, note = grammar.resolve_anaphora(text, pos)
        assert bound is None
        assert "nearest antecedent" in note

    def test_an_anaphor_with_nothing_to_bind_to_is_refused(self):
        text = "كما تنص المادة (العاشرة) من الالئحة ذاتها على"
        bound, note = grammar.resolve_anaphora(text, text.index("من الالئحة"))
        assert bound is None
        assert note

    def test_a_name_attested_once_does_not_trim_another(self):
        # «نظام المر افعات» exists because justification put a space inside a
        # word. One occurrence is not evidence of a name.
        stock = {grammar._fold("نظام المر افعات"): ("نظام المر افعات", 1),
                 grammar._fold("نظام المرافعات الشرعية"):
                     ("نظام المرافعات الشرعية", 40)}
        text = "نظام المر افعات الشرعية التي نصت على"
        assert instruments.same(
            grammar.resolve_name(text, 0, len(text), stock),
            "نظام المرافعات الشرعية")


class TestAttribution:
    def test_a_heading_with_no_line_break_is_still_a_heading(self):
        # ministry judgment text arrives as one line; every line-anchored
        # pattern matched nothing and the stage reported zero
        text = ("قررت الدائرة صلاحية القضية للحكم وقفل باب المرافعة. "
                "الأسباب: بما أن أصل النزاع ناشئ عن عقد توريد")
        marks = grammar.sections(text)
        assert any(name == "reasoning" for _, name in marks)

    def test_a_quotation_is_attributed_to_the_drafter(self):
        text = ('كما نصت المادة (14) على: "دون الإخلال بالمادة الثانية من '
                'النظام وألغراض تطبيق الاتفاقية"')
        pos = text.index("بالمادة الثانية")
        assert grammar.in_quotation(text, pos)

    def test_ordinary_text_is_not_a_quotation(self):
        text = "وعليه رفضت الهيئة اعتراض المدعية استنادا للمادة (20) من الالئحة"
        assert not grammar.in_quotation(text, len(text) - 10)


class TestNameFrequencyBeatsNameLength:
    """The gazetteer picks a name by how often the corpus says it.

    Both length rules fail, in opposite directions. Longest-match lets a name
    that ran on into the next clause certify the next over-run. Shortest-match
    trims a name to a fragment of itself wherever one instrument's name begins
    another's -- «نظام الجمارك» is attested cleanly, inside «الالئحة
    التنفيذية لنظام الجمارك», and it begins «نظام الجمارك الموحد». That cost
    24 of 112 citations on a held-out set, and neither development set could
    have shown it.
    """

    def _stock(self, pairs):
        return {grammar._fold(name): (name, count) for name, count in pairs}

    def test_a_fragment_loses_to_the_full_name(self):
        stock = self._stock([("نظام الجمارك", 4),
                             ("نظام الجمارك الموحد", 300)])
        text = "نظام الجمارك الموحد الصادر بالمرسوم"
        assert grammar.resolve_name(text, 0, len(text), stock) == \
            "نظام الجمارك الموحد"

    def test_an_over_run_loses_to_the_name(self):
        stock = self._stock([("نظام المحاكم التجارية", 300),
                             ("نظام المحاكم التجارية والمحددة بخمسة عشر", 2)])
        text = "نظام المحاكم التجارية والمحددة بخمسة عشر يوما"
        assert grammar.resolve_name(text, 0, len(text), stock) == \
            "نظام المحاكم التجارية"

    def test_a_wrapped_name_is_still_rejoined(self):
        stock = self._stock([("قواعد عمل لجان الفصل في المخالفات والمنازعات", 50)])
        text = "قواعد عمل لجان الفصل في\nالمخالفات والمنازعات الضريبية"
        got = grammar.resolve_name(text, 0, 23, stock)
        assert got == "قواعد عمل لجان الفصل في المخالفات والمنازعات"
