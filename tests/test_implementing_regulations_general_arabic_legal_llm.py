#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the General Implementing Regulations Arabic Legal LLM Layer.

Tests cover:
  - Article layer structure and metadata
  - 95 article records with correct numbering
  - official_text_ar verbatim preservation (hash matching)
  - Required metadata fields per record
  - Forms layer structure (4 forms)
  - Separation of articles and forms
  - No English/Chinese text
  - Legal-status boundaries
  - Idempotence (generator produces identical output)
  - Companies Law corpus unchanged
  - Listed joint-stock sub-track separation
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "implementing_regulations", "general")

INTAKE_PATH = os.path.join(DATA_DIR, "general_implementing_regulations_arabic_source.json")
MANIFEST_PATH = os.path.join(DATA_DIR, "source_manifest.json")
ARTICLE_LAYER_PATH = os.path.join(DATA_DIR, "general_implementing_regulations_arabic_legal_llm.json")
FORMS_LAYER_PATH = os.path.join(DATA_DIR, "general_implementing_regulations_arabic_forms_llm.json")

GENERATOR_SCRIPT = os.path.join(ROOT, "scripts", "gen_implementing_regulations_general_arabic_legal_llm.py")


# ---- Fixtures ----

@pytest.fixture(scope="module")
def article_layer():
    """Load the article layer JSON."""
    with open(ARTICLE_LAYER_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def forms_layer():
    """Load the forms layer JSON."""
    with open(FORMS_LAYER_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def source_intake():
    """Load the source intake JSON."""
    with open(INTAKE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ---- Article Layer Structure Tests ----

class TestArticleLayerStructure:
    def test_layer_exists(self):
        assert os.path.isfile(ARTICLE_LAYER_PATH), "Article layer JSON must exist"

    def test_layer_id(self, article_layer):
        assert article_layer["layer_id"] == "sa-general-implementing-regulations-arabic-legal-llm"

    def test_stage(self, article_layer):
        assert article_layer["stage"] == "GENERAL_IMPLEMENTING_REGULATIONS_ARABIC_LEGAL_LLM_LAYER"

    def test_corpus_track(self, article_layer):
        assert article_layer["corpus_track"] == "implementing_regulations/general"

    def test_regulation_scope(self, article_layer):
        assert article_layer["regulation_scope"] == "general"

    def test_parent_law(self, article_layer):
        assert article_layer["parent_law"] == "sa_companies_law_m132_1443"

    def test_language(self, article_layer):
        assert article_layer["language"] == "ar"

    def test_governing_text(self, article_layer):
        assert article_layer["governing_text"] == "arabic_official_source"

    def test_record_count(self, article_layer):
        assert article_layer["record_count"] == 95

    def test_article_range(self, article_layer):
        assert article_layer["article_range"] == [1, 95]

    def test_chapter_count(self, article_layer):
        assert article_layer["chapter_count"] == 7

    def test_record_type(self, article_layer):
        assert article_layer["record_type"] == "implementing_regulation_article"


# ---- Article Record Tests ----

class TestArticleRecords:
    def test_95_records(self, article_layer):
        assert len(article_layer["records"]) == 95

    def test_sequential_numbering(self, article_layer):
        numbers = sorted(r["article_number"] for r in article_layer["records"])
        assert numbers == list(range(1, 96))

    def test_all_have_required_fields(self, article_layer):
        required = [
            "record_id", "corpus_track", "regulation_scope", "language",
            "governing_text", "source_url", "source_title",
            "publication_date_hijri", "publication_date_gregorian",
            "chapter_number", "chapter_title_ar", "article_number",
            "article_ordinal_ar", "article_title_ar", "official_text_ar",
            "official_text_hash", "legal_status_boundaries",
            "source_manifest_hash",
        ]
        for r in article_layer["records"]:
            for field in required:
                assert field in r, f"Article {r.get('article_number')} missing field: {field}"

    def test_record_ids(self, article_layer):
        for i, r in enumerate(article_layer["records"], 1):
            expected_id = f"ir-gen-art-{i:03d}"
            assert r["record_id"] == expected_id, f"Article {i}: expected {expected_id}, got {r['record_id']}"

    def test_all_arabic_language(self, article_layer):
        for r in article_layer["records"]:
            assert r["language"] == "ar"

    def test_all_governing_text(self, article_layer):
        for r in article_layer["records"]:
            assert r["governing_text"] == "arabic_official_source"

    def test_article_title_ar_present_or_null(self, article_layer):
        for r in article_layer["records"]:
            assert "article_title_ar" in r
            # Value can be a string or None, but key must exist
            assert r["article_title_ar"] is None or isinstance(r["article_title_ar"], str)

    def test_chapter_numbers_range(self, article_layer):
        for r in article_layer["records"]:
            assert 1 <= r["chapter_number"] <= 7

    def test_chapter_titles_not_empty(self, article_layer):
        for r in article_layer["records"]:
            assert r["chapter_title_ar"], f"Article {r['article_number']} has empty chapter_title_ar"


# ---- Verbatim Preservation Tests ----

class TestVerbatimPreservation:
    def test_hashes_match_source(self, article_layer, source_intake):
        source_hash_map = {a["article_number"]: a["text_hash_sha256"] for a in source_intake["articles"]}
        layer_hash_map = {r["article_number"]: r["official_text_hash"] for r in article_layer["records"]}
        for art_num, src_hash in source_hash_map.items():
            assert layer_hash_map[art_num] == src_hash, f"Article {art_num} hash mismatch"

    def test_text_identical_to_source(self, article_layer, source_intake):
        source_text_map = {a["article_number"]: a["official_text_ar"] for a in source_intake["articles"]}
        for r in article_layer["records"]:
            art_num = r["article_number"]
            assert r["official_text_ar"] == source_text_map[art_num], \
                f"Article {art_num} text differs from source"


# ---- Forms Layer Tests ----

class TestFormsLayer:
    def test_forms_layer_exists(self):
        assert os.path.isfile(FORMS_LAYER_PATH)

    def test_forms_stage(self, forms_layer):
        assert forms_layer["stage"] == "GENERAL_IMPLEMENTING_REGULATIONS_ARABIC_FORMS_LLM_LAYER"

    def test_forms_record_count(self, forms_layer):
        assert forms_layer["record_count"] == 4
        assert len(forms_layer["records"]) == 4

    def test_forms_record_type(self, forms_layer):
        assert forms_layer["record_type"] == "official_form"
        for r in forms_layer["records"]:
            assert r["record_type"] == "official_form"

    def test_form_numbers(self, forms_layer):
        form_nums = sorted(r["form_number"] for r in forms_layer["records"])
        assert form_nums == [1, 2, 3, 4]

    def test_form_hashes_match_source(self, forms_layer, source_intake):
        source_form_hash_map = {fm["form_number"]: fm["text_hash_sha256"] for fm in source_intake["forms"]}
        for r in forms_layer["records"]:
            assert r["official_text_hash"] == source_form_hash_map[r["form_number"]], \
                f"Form {r['form_number']} hash mismatch"

    def test_form_required_fields(self, forms_layer):
        required = [
            "record_id", "corpus_track", "regulation_scope", "record_type",
            "language", "governing_text", "source_url", "source_title",
            "publication_date_hijri", "publication_date_gregorian",
            "form_number", "form_title", "official_text_ar",
            "official_text_hash", "legal_status_boundaries",
            "source_manifest_hash",
        ]
        for r in forms_layer["records"]:
            for field in required:
                assert field in r, f"Form {r.get('form_number')} missing field: {field}"


# ---- Separation Tests ----

class TestSeparation:
    def test_articles_and_forms_in_separate_files(self):
        assert ARTICLE_LAYER_PATH != FORMS_LAYER_PATH

    def test_article_layer_has_no_form_records(self, article_layer):
        for r in article_layer["records"]:
            assert r.get("record_type", "implementing_regulation_article") != "official_form"

    def test_forms_layer_has_no_article_records(self, forms_layer):
        for r in forms_layer["records"]:
            assert r["record_type"] == "official_form"
            assert "article_number" not in r

    def test_listed_joint_stock_is_separate(self, article_layer):
        sep = article_layer.get("separation", {})
        assert sep.get("listed_joint_stock_is_separate_specialized_sub_track") is True

    def test_companies_law_unchanged_flag(self, article_layer):
        sep = article_layer.get("separation", {})
        assert sep.get("companies_law_corpus_unchanged") is True

    def test_chinese_remediation_unchanged_flag(self, article_layer):
        sep = article_layer.get("separation", {})
        assert sep.get("chinese_remediation_program_unchanged") is True


# ---- No Non-Arabic Content Tests ----

class TestNoNonArabicContent:
    def test_no_english_in_articles(self, article_layer):
        import re
        pattern = re.compile(r"[A-Za-z]{3,}\s+[A-Za-z]{3,}")
        for r in article_layer["records"]:
            assert not pattern.search(r["official_text_ar"]), \
                f"Article {r['article_number']} contains English text"

    def test_no_english_in_forms(self, forms_layer):
        import re
        pattern = re.compile(r"[A-Za-z]{3,}\s+[A-Za-z]{3,}")
        for r in forms_layer["records"]:
            assert not pattern.search(r["official_text_ar"]), \
                f"Form {r['form_number']} contains English text"

    def test_no_chinese_in_articles(self, article_layer):
        for r in article_layer["records"]:
            for c in r["official_text_ar"]:
                assert not ("\u4e00" <= c <= "\u9fff"), \
                    f"Article {r['article_number']} contains Chinese character"

    def test_no_chinese_in_forms(self, forms_layer):
        for r in forms_layer["records"]:
            for c in r["official_text_ar"]:
                assert not ("\u4e00" <= c <= "\u9fff"), \
                    f"Form {r['form_number']} contains Chinese character"

    def test_no_trilingual_alignment(self, article_layer):
        assert article_layer["content_boundaries"]["no_trilingual_alignment"] is True

    def test_no_public_release(self, article_layer):
        assert article_layer["content_boundaries"]["no_public_release"] is True


# ---- Legal Status Tests ----

class TestLegalStatus:
    def test_arabic_governs(self, article_layer):
        assert article_layer["legal_status"]["arabic_governs"] is True

    def test_not_official_translation(self, article_layer):
        assert article_layer["legal_status"]["not_official_translation"] is True

    def test_not_legal_advice(self, article_layer):
        assert article_layer["legal_status"]["not_legal_advice"] is True

    def test_not_binding_translation(self, article_layer):
        assert article_layer["legal_status"]["not_binding_translation"] is True

    def test_derived_from_source(self, article_layer):
        assert article_layer["legal_status"]["derived_from_general_implementing_regulations_source"] is True

    def test_record_level_legal_status(self, article_layer):
        for r in article_layer["records"]:
            ls = r["legal_status_boundaries"]
            assert ls["arabic_governs"] is True
            assert ls["not_legal_advice"] is True
            assert ls["not_official_translation"] is True


# ---- Idempotence Test ----

class TestIdempotence:
    def test_generator_is_idempotent(self, tmp_path):
        """Re-running the generator produces identical output."""
        # Read current output
        with open(ARTICLE_LAYER_PATH, "r", encoding="utf-8") as f:
            original_articles = f.read()

        with open(FORMS_LAYER_PATH, "r", encoding="utf-8") as f:
            original_forms = f.read()

        # Re-run generator
        result = subprocess.run(
            [sys.executable, GENERATOR_SCRIPT],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        assert result.returncode == 0, f"Generator failed: {result.stderr}"

        # Read new output
        with open(ARTICLE_LAYER_PATH, "r", encoding="utf-8") as f:
            new_articles = f.read()

        with open(FORMS_LAYER_PATH, "r", encoding="utf-8") as f:
            new_forms = f.read()

        assert new_articles == original_articles, "Article layer not idempotent"
        assert new_forms == original_forms, "Forms layer not idempotent"


# ---- Source Provenance Tests ----

class TestSourceProvenance:
    def test_source_url(self, article_layer, source_intake):
        assert article_layer["source_url"] == source_intake["source_url"]
        assert article_layer["source_url"] == "https://www.uqn.gov.sa/details?p=21325"

    def test_source_title(self, article_layer, source_intake):
        assert article_layer["source_title"] == source_intake["source_title"]

    def test_publication_dates(self, article_layer, source_intake):
        assert article_layer["publication_date_hijri"] == source_intake["publication_date_hijri"]
        assert article_layer["publication_date_gregorian"] == source_intake["publication_date_gregorian"]

    def test_source_hash_preserved(self, article_layer, source_intake):
        assert article_layer["source_hash"] == source_intake["source_hash"]

    def test_manifest_hash_consistent(self, article_layer, forms_layer):
        assert article_layer["source_manifest_hash"] == forms_layer["source_manifest_hash"]
        assert article_layer["source_manifest_hash"] is not None

    def test_record_level_source_url(self, article_layer, source_intake):
        for r in article_layer["records"]:
            assert r["source_url"] == source_intake["source_url"]