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


class TestHamzaTransposition:
    """«الأربعون» reaches the text layer as «األربعون», and it costs parses.

    The lam is carried past the hamza-alef exactly as it is carried past the
    meem. Before these letters were in the alphabet, «المادة السابعة
    والأربعون» parsed as article 7, because the ordinal reader stopped at
    «السابعة» and never saw «واألربعون».
    """

    def test_hamza_alef_is_in_the_alphabet(self):
        assert "أ" in canonical.CONSONANT
        assert "إ" in canonical.CONSONANT
        assert "آ" in canonical.CONSONANT

    def test_lam_is_excluded_because_the_test_cannot_decide_it(self):
        # «ال» + «ل» and «ا» + «ل» + «ل» are the same three characters, so the
        # ratio is 1.0 whatever the document does. A rule must not be gated on
        # a measurement that cannot come out either way.
        assert "ل" not in canonical.CONSONANT

    def test_transposed_hamza_is_repaired_when_the_document_shows_it(self):
        broken = ("األربعون واألسباب واألحكام " * 30) + "الأولى"
        out = canonical.canonicalise(broken)["canonical"]
        assert "الأربعون" in out
        assert "األربعون" not in out

    def test_a_document_that_writes_it_correctly_is_left_alone(self):
        fine = "الأربعون والأسباب والأحكام " * 30
        assert canonical.canonicalise(fine)["canonical"] == fine


class TestScrambledBracketNumbers:
    """«المادة (5)، الفقرة» arrives as «المادة ( , )5الفقرة»."""

    def test_digits_are_returned_inside_the_brackets(self):
        out = canonical.canonicalise("المادة ( , )5الفقرة")["canonical"]
        assert "(5)" in out

    def test_the_punctuation_is_returned_outside_them(self):
        out = canonical.canonicalise("المادة ( ، )14الفقرة")["canonical"]
        assert "(14)،" in out

    def test_an_ordinary_bracketed_number_is_untouched(self):
        text = "المادة (14) من الالئحة"
        assert canonical.canonicalise(text)["canonical"] == text

    def test_the_rule_is_counted(self):
        rec = canonical.canonicalise("المادة ( , )5الفقرة")
        counts = {t["rule"]: t["edits"] for t in rec["transformations"]}
        assert counts["brackets"] == 1


class TestOffsetTrace:
    """A canonical position must be traceable to the raw byte it came from.

    The sampling frame moves when the layer changes -- with the transposition
    repair off, «املادة» is not «المادة» and occurrences disappear -- so an
    evaluation anchored in canonical positions cannot compare two settings of
    the layer, and one that ignores the problem compares different items while
    reporting a number that looks fine.
    """

    def test_trace_agrees_with_canonicalise(self):
        raw = "املادة ( , )5الفقرة ـ (١٢) والأسباب"
        text, tr = canonical.trace(raw)
        assert text == canonical.canonicalise(raw)["canonical"]
        assert len(tr) == len(text)

    def test_every_position_points_into_the_raw_text(self):
        raw = "المادة ( ، )14 من الالئحة" * 5
        text, tr = canonical.trace(raw)
        assert all(0 <= i < len(raw) for i in tr)

    def test_a_disabled_rule_changes_the_text_but_not_the_anchors(self):
        raw = "المادة ( , )5 من الالئحة"
        full, tr_full = canonical.trace(raw)
        without, tr_without = canonical.trace(raw, ["bidi", "digits"])
        assert full != without
        # the same raw byte is reachable under both settings
        assert set(tr_full) & set(tr_without)


class TestPresentationForms:
    """A PDF that writes the shaped glyphs is not writing the letters.

    Six of the eight securities-committee bulletins in SOURCE_C.md are encoded
    in the Arabic Presentation Forms blocks, and 30.2 per cent of ministry
    judgments carry some of it. Before this rule existed, such a document
    yielded zero citations and read downstream as one that cites nothing --
    the worst kind of failure, because it is silent and looks like data.
    """

    SHAPED = "ﺍﻟﻤﺎﺩﺓ (٢٩) ﻣﻦ ﻧﻈﺎﻡ ﺍﻹﺛﺒﺎﺕ"

    def test_shaped_glyphs_become_letters(self):
        out = canonical.canonicalise(self.SHAPED)["canonical"]
        assert "المادة" in out
        assert "نظام" in out

    def test_the_rule_is_switchable_and_counted(self):
        edits = {t["rule"]: t["edits"]
                 for t in canonical.canonicalise(self.SHAPED)["transformations"]}
        assert edits["presentation"] == 18
        without = canonical.canonicalise(
            self.SHAPED, rules=["bidi", "digits"])["canonical"]
        assert "المادة" not in without

    def test_ordinary_arabic_is_untouched(self):
        plain = "المادة (29) من نظام الإثبات"
        assert canonical.canonicalise(plain)["canonical"] == plain


class TestCombiningMarks:
    """A shadda is vocalisation, not spelling.

    «المادَّة» is the same word as «المادة» and was a different string. 234
    citations corpus-wide were lost to that one mark.
    """

    def test_shadda_on_the_head_noun_is_stripped(self):
        assert "المادة" in canonical.canonicalise(
            "المادَّة (69) من نظام الإفلاس")["canonical"]

    def test_fatha_kasra_damma_sukun_and_dagger_alif(self):
        for marked in ("المَادة", "المِادة", "المُادة", "المْادة", "المٰادة"):
            assert "المادة" in canonical.canonicalise(marked)["canonical"]

    def test_marks_do_not_hide_the_transposition_gate(self):
        # a document written with «املادة» and a shadda must still be
        # diagnosed as transposed, which needs the marks gone first
        raw = ("امَلادة (1) من الالئحة " * 60)
        out = canonical.canonicalise(raw)["canonical"]
        assert "المادة" in out

    def test_a_word_that_is_not_the_head_noun_is_unharmed(self):
        assert canonical.canonicalise("عمادة الكلية")["canonical"] == "عمادة الكلية"
