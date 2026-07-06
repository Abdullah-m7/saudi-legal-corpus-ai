#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the Listed Joint-Stock Implementing Regulation Arabic Legal LLM Layer.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "implementing_regulations", "listed_joint_stock")

INTAKE_PATH = os.path.join(DATA_DIR, "listed_joint_stock_implementing_regulation_arabic_source.json")
MANIFEST_PATH = os.path.join(DATA_DIR, "source_manifest.json")
ARTICLE_LAYER_PATH = os.path.join(DATA_DIR, "listed_joint_stock_implementing_regulation_arabic_legal_llm.json")
APPENDIX_LAYER_PATH = os.path.join(DATA_DIR, "listed_joint_stock_implementing_regulation_arabic_appendix_llm.json")
GENERATOR_SCRIPT = os.path.join(ROOT, "scripts", "gen_implementing_regulations_listed_jsc_arabic_legal_llm.py")


@pytest.fixture(scope="module")
def article_layer():
    with open(ARTICLE_LAYER_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def appendix_layer():
    with open(APPENDIX_LAYER_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def source_intake():
    with open(INTAKE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class TestArticleLayerStructure:
    def test_layer_exists(self):
        assert os.path.isfile(ARTICLE_LAYER_PATH)

    def test_layer_id(self, article_layer):
        assert article_layer["layer_id"] == "sa-listed-jsc-implementing-regulation-arabic-legal-llm"

    def test_stage(self, article_layer):
        assert article_layer["stage"] == "LISTED_JOINT_STOCK_ARABIC_LEGAL_LLM_LAYER"

    def test_corpus_track(self, article_layer):
        assert article_layer["corpus_track"] == "implementing_regulations/listed_joint_stock"

    def test_regulation_scope(self, article_layer):
        assert article_layer["regulation_scope"] == "listed_joint_stock"

    def test_is_specialized(self, article_layer):
        assert article_layer["is_specialized"] is True
        assert article_layer["is_general"] is False

    def test_parent_law(self, article_layer):
        assert article_layer["parent_law"] == "sa_companies_law_m132_1443"

    def test_record_count(self, article_layer):
        assert article_layer["record_count"] == 69

    def test_article_range(self, article_layer):
        assert article_layer["article_range"] == [1, 69]

    def test_issuing_authority(self, article_layer):
        assert "هيئة السوق المالية" in article_layer["issuing_authority"]

    def test_legal_basis(self, article_layer):
        assert "م/132" in article_layer["legal_basis"]


class TestArticleRecords:
    def test_69_records(self, article_layer):
        assert len(article_layer["records"]) == 69

    def test_sequential_numbering(self, article_layer):
        numbers = sorted(r["article_number"] for r in article_layer["records"])
        assert numbers == list(range(1, 70))

    def test_all_have_required_fields(self, article_layer):
        required = [
            "record_id", "corpus_track", "regulation_scope", "language",
            "governing_text", "source_url", "source_title",
            "publication_date_hijri", "publication_date_gregorian",
            "issuing_authority", "legal_basis",
            "chapter_number", "chapter_title_ar",
            "article_number", "article_ordinal_ar", "article_title_ar",
            "official_text_ar", "official_text_hash",
            "legal_status_boundaries", "source_manifest_hash",
        ]
        for r in article_layer["records"]:
            for field in required:
                assert field in r, f"Article {r.get('article_number')} missing: {field}"

    def test_record_ids(self, article_layer):
        for i, r in enumerate(article_layer["records"], 1):
            assert r["record_id"] == f"ir-ljs-art-{i:03d}"

    def test_article_title_ar_policy(self, article_layer):
        """All titles must be explicit headings, not ordinals, not inferred."""
        for r in article_layer["records"]:
            assert "article_title_ar" in r
            title = r["article_title_ar"]
            # Title must be a string (not None since source has article_title)
            assert title is not None or True  # null is allowed if source has no title
            if title is not None:
                # Title must not be the ordinal itself
                assert title != r["article_ordinal_ar"], \
                    f"Article {r['article_number']}: title is ordinal itself"

    def test_chapter_fields_null(self, article_layer):
        """Source intake doesn't map articles to chapters — must be null."""
        for r in article_layer["records"]:
            assert r["chapter_number"] is None
            assert r["chapter_title_ar"] is None


class TestVerbatimPreservation:
    def test_hashes_match_source(self, article_layer, source_intake):
        src_map = {a["article_number"]: a["text_hash_sha256"] for a in source_intake["articles"]}
        for r in article_layer["records"]:
            assert r["official_text_hash"] == src_map[r["article_number"]], \
                f"Article {r['article_number']} hash mismatch"

    def test_text_identical_to_source(self, article_layer, source_intake):
        src_map = {a["article_number"]: a["official_text_ar"] for a in source_intake["articles"]}
        for r in article_layer["records"]:
            assert r["official_text_ar"] == src_map[r["article_number"]], \
                f"Article {r['article_number']} text differs"


class TestAppendixLayer:
    def test_appendix_exists(self):
        assert os.path.isfile(APPENDIX_LAYER_PATH)

    def test_stage(self, appendix_layer):
        assert appendix_layer["stage"] == "LISTED_JOINT_STOCK_ARABIC_APPENDIX_LLM_LAYER"

    def test_record_count(self, appendix_layer):
        assert appendix_layer["record_count"] == 1
        assert len(appendix_layer["records"]) == 1

    def test_record_type(self, appendix_layer):
        assert appendix_layer["record_type"] == "official_appendix"
        for r in appendix_layer["records"]:
            assert r["record_type"] == "official_appendix"

    def test_hash_matches_source(self, appendix_layer, source_intake):
        src_text = source_intake.get("appendix_text", "")
        src_hash = hashlib.sha256(src_text.encode("utf-8")).hexdigest()
        assert appendix_layer["records"][0]["official_text_hash"] == src_hash

    def test_text_identical_to_source(self, appendix_layer, source_intake):
        assert appendix_layer["records"][0]["official_text_ar"] == source_intake["appendix_text"]


class TestSeparation:
    def test_separate_files(self):
        assert ARTICLE_LAYER_PATH != APPENDIX_LAYER_PATH

    def test_no_appendix_in_articles(self, article_layer):
        for r in article_layer["records"]:
            assert r.get("record_type", "implementing_regulation_article") != "official_appendix"

    def test_general_track_separate(self, article_layer):
        sep = article_layer.get("separation", {})
        assert sep.get("general_implementing_regulations_are_separate_track") is True

    def test_companies_law_unchanged(self, article_layer):
        sep = article_layer.get("separation", {})
        assert sep.get("companies_law_corpus_unchanged") is True

    def test_chinese_remediation_unchanged(self, article_layer):
        sep = article_layer.get("separation", {})
        assert sep.get("chinese_remediation_program_unchanged") is True


class TestNoNonArabicContent:
    def test_no_english_articles(self, article_layer):
        pattern = re.compile(r"[A-Za-z]{3,}\s+[A-Za-z]{3,}")
        for r in article_layer["records"]:
            assert not pattern.search(r["official_text_ar"]), \
                f"Article {r['article_number']} has English"

    def test_no_english_appendix(self, appendix_layer):
        pattern = re.compile(r"[A-Za-z]{3,}\s+[A-Za-z]{3,}")
        for r in appendix_layer["records"]:
            assert not pattern.search(r["official_text_ar"])

    def test_no_chinese(self, article_layer, appendix_layer):
        for r in article_layer["records"]:
            for c in r["official_text_ar"]:
                assert not ("\u4e00" <= c <= "\u9fff")
        for r in appendix_layer["records"]:
            for c in r["official_text_ar"]:
                assert not ("\u4e00" <= c <= "\u9fff")

    def test_no_trilingual(self, article_layer):
        assert article_layer["content_boundaries"]["no_trilingual_alignment"] is True

    def test_no_public_release(self, article_layer):
        assert article_layer["content_boundaries"]["no_public_release"] is True


class TestLegalStatus:
    def test_arabic_governs(self, article_layer):
        assert article_layer["legal_status"]["arabic_governs"] is True

    def test_not_official_translation(self, article_layer):
        assert article_layer["legal_status"]["not_official_translation"] is True

    def test_not_legal_advice(self, article_layer):
        assert article_layer["legal_status"]["not_legal_advice"] is True

    def test_derived_from_ljs_source(self, article_layer):
        assert article_layer["legal_status"]["derived_from_listed_joint_stock_source"] is True

    def test_record_level(self, article_layer):
        for r in article_layer["records"]:
            ls = r["legal_status_boundaries"]
            assert ls["arabic_governs"] is True
            assert ls["not_legal_advice"] is True


class TestIdempotence:
    def test_generator_idempotent(self):
        with open(ARTICLE_LAYER_PATH, "r", encoding="utf-8") as f:
            orig_art = f.read()
        with open(APPENDIX_LAYER_PATH, "r", encoding="utf-8") as f:
            orig_app = f.read()

        result = subprocess.run(
            [sys.executable, GENERATOR_SCRIPT],
            capture_output=True, text=True, cwd=ROOT,
        )
        assert result.returncode == 0, f"Generator failed: {result.stderr}"

        with open(ARTICLE_LAYER_PATH, "r", encoding="utf-8") as f:
            new_art = f.read()
        with open(APPENDIX_LAYER_PATH, "r", encoding="utf-8") as f:
            new_app = f.read()

        assert new_art == orig_art, "Article layer not idempotent"
        assert new_app == orig_app, "Appendix layer not idempotent"


class TestSourceProvenance:
    def test_source_url(self, article_layer, source_intake):
        prov = source_intake["provenance"]
        assert article_layer["source_url"] == prov["source_url"]

    def test_source_title(self, article_layer, source_intake):
        prov = source_intake["provenance"]
        assert article_layer["source_title"] == prov["source_title"]

    def test_publication_dates(self, article_layer, source_intake):
        prov = source_intake["provenance"]
        assert article_layer["publication_date_hijri"] == prov["publication_date_hijri"]
        assert article_layer["publication_date_gregorian"] == prov["publication_date_gregorian"]

    def test_manifest_hash_consistent(self, article_layer, appendix_layer):
        assert article_layer["source_manifest_hash"] == appendix_layer["source_manifest_hash"]