#!/usr/bin/env python3
"""Tests for general implementing regulations Arabic source intake."""

import json
import os
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTAKE_PATH = os.path.join(REPO_ROOT, "data", "implementing_regulations", "general",
                           "general_implementing_regulations_arabic_source.json")
MANIFEST_PATH = os.path.join(REPO_ROOT, "data", "implementing_regulations", "general",
                             "source_manifest.json")
REPORT_PATH = os.path.join(REPO_ROOT, "reports", "implementing_regulations",
                           "GENERAL_IMPLEMENTING_REGULATIONS_ARABIC_SOURCE_INTAKE_AR.md")


@pytest.fixture(scope="module")
def intake():
    with open(INTAKE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def manifest():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class TestIntakeStructure:
    def test_intake_json_exists(self):
        assert os.path.isfile(INTAKE_PATH)

    def test_manifest_exists(self):
        assert os.path.isfile(MANIFEST_PATH)

    def test_report_exists(self):
        assert os.path.isfile(REPORT_PATH)

    def test_stage(self, intake):
        assert intake["stage"] == "GENERAL_IMPLEMENTING_REGULATIONS_ARABIC_SOURCE_INTAKE"

    def test_corpus_track(self, intake):
        assert intake["corpus_track"] == "implementing_regulations/general"

    def test_general_scope(self, intake):
        assert intake["general"] is True
        assert intake["specialized"] is False

    def test_parent_law(self, intake):
        assert intake["parent_law"] == "sa_companies_law_m132_1443"
        assert intake["parent_law_unchanged"] is True


class TestSourceProvenance:
    def test_source_title(self, intake):
        assert intake["source_title"] == "اللائحة التنفيذية لنظام الشركات"

    def test_source_url(self, intake):
        assert intake["source_url"] == "https://www.uqn.gov.sa/details?p=21325"

    def test_publication_date_hijri(self, intake):
        assert intake["publication_date_hijri"] == "1444-6-25"

    def test_publication_date_gregorian(self, intake):
        assert intake["publication_date_gregorian"] == "18-01-2023"

    def test_source_scope(self, intake):
        assert intake["source_scope"] == "general"

    def test_source_hash(self, intake):
        assert len(intake["source_hash"]) == 64

    def test_access_date(self, intake):
        assert intake["access_date"] == "2026-07-05"

    def test_extraction_method(self, intake):
        assert "curl" in intake["extraction_method"].lower()


class TestArticleRecords:
    def test_article_count(self, intake):
        assert len(intake["articles"]) == 95

    def test_first_article(self, intake):
        assert intake["articles"][0]["article_label"] == "المادة الأولى"
        assert intake["articles"][0]["article_number"] == 1

    def test_last_article(self, intake):
        assert intake["articles"][-1]["article_label"] == "المادة الخامسة والتسعون"
        assert intake["articles"][-1]["article_number"] == 95

    def test_all_articles_have_text(self, intake):
        for a in intake["articles"]:
            assert "official_text_ar" in a
            assert len(a["official_text_ar"]) > 0

    def test_all_articles_have_hash(self, intake):
        for a in intake["articles"]:
            assert "text_hash_sha256" in a
            assert len(a["text_hash_sha256"]) == 64

    def test_article_chapters(self, intake):
        for a in intake["articles"]:
            assert "chapter" in a
            assert "chapter_number" in a
            assert a["chapter_number"] is not None

    def test_chapter_count(self, intake):
        assert intake["chapter_count"] == 7

    def test_chapters_list(self, intake):
        assert len(intake["chapters"]) == 7

    def test_form_count(self, intake):
        assert intake["form_count"] == 4
        assert len(intake["forms"]) == 4

    def test_forms_have_text(self, intake):
        for form in intake["forms"]:
            assert "official_text_ar" in form
            assert len(form["official_text_ar"]) > 0


class TestContentBoundaries:
    def test_no_english_text(self, intake):
        import re
        pattern = re.compile(r'[A-Za-z]{3,}\s+[A-Za-z]{3,}')
        for a in intake["articles"]:
            assert not pattern.search(a["official_text_ar"]), \
                f"English text found in {a['article_label']}"

    def test_no_chinese_text(self, intake):
        for a in intake["articles"]:
            for c in a["official_text_ar"]:
                assert not ('\u4e00' <= c <= '\u9fff'), \
                    f"Chinese text found in {a['article_label']}"

    def test_no_trilingual_alignment(self, intake):
        assert intake["content_boundaries"]["no_trilingual_alignment"] is True

    def test_no_public_release(self, intake):
        assert intake["content_boundaries"]["no_public_release"] is True


class TestLegalStatus:
    def test_arabic_governs(self, intake):
        assert intake["legal_status"]["arabic_governs"] is True

    def test_english_reference_only(self, intake):
        assert intake["legal_status"]["english_reference_only"] is True

    def test_chinese_internal_reference_only(self, intake):
        assert intake["legal_status"]["chinese_internal_reference_only"] is True

    def test_not_official_translation(self, intake):
        assert intake["legal_status"]["not_official_translation"] is True

    def test_not_legal_advice(self, intake):
        assert intake["legal_status"]["not_legal_advice"] is True


class TestSeparation:
    def test_parent_law_unchanged(self, intake):
        assert intake["parent_law_unchanged"] is True

    def test_listed_joint_stock_separation(self, intake):
        assert "listed_joint_stock_sub_track" in intake["separation_from_other_tracks"]

    def test_chinese_remediation_separation(self, intake):
        assert "chinese_remediation_program" in intake["separation_from_other_tracks"]

    def test_companies_law_corpus_separation(self, intake):
        assert "companies_law_corpus" in intake["separation_from_other_tracks"]

    def test_listed_jsc_intake_exists(self):
        listed_jsc_path = os.path.join(REPO_ROOT, "data", "implementing_regulations",
                                       "listed_joint_stock",
                                       "listed_joint_stock_implementing_regulation_arabic_source.json")
        assert os.path.isfile(listed_jsc_path)


class TestManifest:
    def test_manifest_title(self, manifest, intake):
        assert manifest["source_title"] == intake["source_title"]

    def test_manifest_url(self, manifest, intake):
        assert manifest["source_url"] == intake["source_url"]

    def test_manifest_hash(self, manifest, intake):
        assert manifest["source_hash"] == intake["source_hash"]

    def test_manifest_article_count(self, manifest, intake):
        assert manifest["article_count"] == intake["article_count"]

    def test_manifest_chapter_count(self, manifest, intake):
        assert manifest["chapter_count"] == intake["chapter_count"]

    def test_manifest_scope(self, manifest):
        assert manifest["source_scope"] == "general"