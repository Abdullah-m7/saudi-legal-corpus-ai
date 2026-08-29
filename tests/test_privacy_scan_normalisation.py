#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The privacy gate must not return zero for a reason other than absence.

Both of these failure modes happened for real, on the first Saudi tax-committee
digest, and both produced a clean report on a document that had not been read
correctly:

  * patterns written in Latin digits report nothing on Arabic-Indic text
  * Unicode bidi controls sit between a number and its context and break any
    pattern that spans them

A scan that reports «clean» because it could not see is worse than no scan, so
the normalisation is tested rather than trusted.
"""

from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "docs", "research", "gstc_pilot"))

privacy_scan = pytest.importorskip("privacy_scan")


class TestDigitNormalisation:
    def test_arabic_indic_digits_become_latin(self):
        clean, _ = privacy_scan.normalise("رقم الهوية ١٢٣٤٥٦٧٨٩٠")
        assert "1234567890" in clean

    def test_extended_arabic_indic_digits_become_latin(self):
        clean, _ = privacy_scan.normalise("۱۲۳۴۵۶۷۸۹۰")
        assert "1234567890" in clean

    def test_national_id_in_arabic_indic_digits_is_found(self):
        report = privacy_scan.scan("بموجب الهوية الوطنية رقم ١٠٢٣٤٥٦٧٨٩")
        assert report["counts"]["national_or_iqama_id"] == 1
        assert report["clean"] is False


class TestBidiNormalisation:
    def test_bidi_controls_are_removed_and_counted(self):
        text = "‫رقم ‪1023456789‬‬"
        clean, removed = privacy_scan.normalise(text)
        assert removed == 4   # RLE, LRE, PDF, PDF
        assert "‪" not in clean and "‫" not in clean

    def test_identifier_split_by_bidi_controls_is_still_found(self):
        # the pattern must see the run as one number, not two fragments
        text = "الهوية ‪1023456789‬ في"
        report = privacy_scan.scan(text)
        assert report["counts"]["national_or_iqama_id"] == 1
        assert report["clean"] is False


class TestCleanIsMeaningful:
    def test_a_document_with_no_identifiers_is_clean(self):
        report = privacy_scan.scan("المادة (142) من نظام الجمارك الموحد")
        assert report["clean"] is True

    def test_publisher_redaction_markers_do_not_read_as_identifiers(self):
        # the source publishes «الهوية الوطنية رقم ( )...» -- a redacted slot,
        # which must not be reported as a hit
        report = privacy_scan.scan("بموجب الهوية الوطنية رقم ( )...في .../.../...")
        assert report["clean"] is True
        assert report["labelsPresent"].get("الهوية الوطنية") == 1
