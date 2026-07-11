#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for Corpus Registry Index Foundation."""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(ROOT, "data", "corpus_registry", "corpus_registry.json")
GENERATOR = os.path.join(ROOT, "scripts", "gen_corpus_registry.py")


@pytest.fixture(scope="module")
def registry():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class TestRegistryStructure:
    def test_exists(self):
        assert os.path.isfile(REGISTRY_PATH)

    def test_registry_version(self, registry):
        assert registry["registry_version"] == "1.6"

    def test_repository(self, registry):
        assert registry["repository"] == "al3obdi/saudi-legal-corpus-ai"

    def test_total_tracks(self, registry):
        assert registry["total_tracks"] == 13

    def test_validation_status(self, registry):
        assert registry["validation_status"] == "PASS"

    def test_total_primary_arabic(self, registry):
        assert registry["total_primary_arabic_governing_records"] == 1855

    def test_total_reference(self, registry):
        assert registry["total_reference_records"] == 614

    def test_total_internal_reference(self, registry):
        assert registry["total_internal_reference_records"] == 281

    def test_total_ir(self, registry):
        assert registry["total_implementing_regulations_records"] == 169

    def test_total_registry_counted(self, registry):
        assert registry["total_registry_counted_records"] == 2750

    def test_no_total_known_records(self, registry):
        assert "total_known_records" not in registry

    def test_count_policy_exists(self, registry):
        assert "count_policy" in registry
        cp = registry["count_policy"]
        assert cp["counting_method"] == "raw_layer_records_not_deduplicated_legal_article_units"
        assert cp["primary_arabic_governing_records_included"] is True
        assert cp["english_reference_records_included"] is True
        assert cp["chinese_internal_reference_records_included"] is True
        assert cp["closure_audit_aggregate_not_counted_separately"] is True

    def test_count_formula_consistency(self, registry):
        assert registry["total_registry_counted_records"] == (
            registry["total_primary_arabic_governing_records"]
            + registry["total_reference_records"]
            + registry["total_internal_reference_records"]
        )


class TestTracks:
    def test_track_ids(self, registry):
        ids = [t["track_id"] for t in registry["tracks"]]
        assert "companies_law" in ids
        assert "implementing_regulations_general" in ids
        assert "implementing_regulations_listed_joint_stock" in ids
        assert "implementing_regulations_arabic_program_closure" in ids
        assert "labor_law" in ids
        assert "labor_implementing_regulation" in ids

    def test_labor_regulation_counts(self, registry):
        lr = next(t for t in registry["tracks"] if t["track_id"] == "labor_implementing_regulation")
        assert lr["record_counts"]["arabic_articles"] == 45
        assert lr["official_text_status"] == "HRSD_OFFICIAL_PDF_OCR_CROSS_CHECKED_LAW_QUOTES"

    def test_labor_law_counts(self, registry):
        labor = next(t for t in registry["tracks"] if t["track_id"] == "labor_law")
        assert labor["record_counts"]["arabic_articles"] == 249
        assert labor["record_counts"]["english_articles"] == 234
        assert labor["official_text_status"] == "HRSD_CONSOLIDATED_CROSS_CHECKED_BOE"

    def test_companies_law_counts(self, registry):
        cl = next(t for t in registry["tracks"] if t["track_id"] == "companies_law")
        assert cl["record_counts"]["arabic_articles"] == 281
        assert cl["record_counts"]["english_articles"] == 281

    def test_general_counts(self, registry):
        gen = next(t for t in registry["tracks"] if t["track_id"] == "implementing_regulations_general")
        assert gen["record_counts"]["articles"] == 95
        assert gen["record_counts"]["forms"] == 4

    def test_ljs_counts(self, registry):
        ljs = next(t for t in registry["tracks"] if t["track_id"] == "implementing_regulations_listed_joint_stock")
        assert ljs["record_counts"]["articles"] == 69
        assert ljs["record_counts"]["appendices"] == 1

    def test_closure_counts(self, registry):
        c = next(t for t in registry["tracks"] if t["track_id"] == "implementing_regulations_arabic_program_closure")
        assert c["record_counts"]["total_records"] == 169
        assert c["record_counts"]["total_article_records"] == 164

    def test_ljs_specialized(self, registry):
        ljs = next(t for t in registry["tracks"] if t["track_id"] == "implementing_regulations_listed_joint_stock")
        assert ljs["boundaries"]["is_specialized"] is True
        assert ljs["boundaries"]["is_general"] is False

    def test_general_is_general(self, registry):
        gen = next(t for t in registry["tracks"] if t["track_id"] == "implementing_regulations_general")
        assert gen["boundaries"]["is_general"] is True
        assert gen["boundaries"]["is_specialized"] is False


class TestPathsExist:
    def test_all_data_paths_exist(self, registry):
        for track in registry["tracks"]:
            for p in track.get("data_paths", []):
                assert os.path.isfile(os.path.join(ROOT, p)), f"Missing: {p}"

    def test_all_report_paths_exist(self, registry):
        for track in registry["tracks"]:
            for p in track.get("report_paths", []):
                assert os.path.isfile(os.path.join(ROOT, p)), f"Missing: {p}"


class TestBoundaries:
    def test_arabic_governs_all(self, registry):
        for t in registry["tracks"]:
            assert t["boundaries"]["arabic_governs"] is True

    def test_not_official_translation(self, registry):
        for t in registry["tracks"]:
            assert t["boundaries"]["not_official_translation"] is True

    def test_not_legal_advice(self, registry):
        for t in registry["tracks"]:
            assert t["boundaries"]["not_legal_advice"] is True

    def test_no_public_release(self, registry):
        for t in registry["tracks"]:
            assert t["boundaries"]["no_public_release"] is True

    def test_no_trilingual(self, registry):
        for t in registry["tracks"]:
            assert t["boundaries"]["no_trilingual_alignment"] is True

    def test_english_reference_only(self, registry):
        cl = next(t for t in registry["tracks"] if t["track_id"] == "companies_law")
        en = cl["language_layers"]["english"]
        assert en["governing"] is False
        assert en["role"] == "reference_guidance_only"

    def test_chinese_internal_only(self, registry):
        cl = next(t for t in registry["tracks"] if t["track_id"] == "companies_law")
        cn = cl["language_layers"]["chinese"]
        assert cn["governing"] is False
        assert cn["role"] == "internal_reference_only"

    def test_top_level_boundaries(self, registry):
        b = registry["legal_status_boundaries"]
        assert b["arabic_official_source_governs"] is True
        assert b["not_official_translation"] is True
        assert b["not_legal_advice"] is True
        assert b["no_trilingual_alignment"] is True
        assert b["no_public_release"] is True


class TestIdempotence:
    def test_generator_idempotent(self):
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            orig = f.read()
        result = subprocess.run([sys.executable, GENERATOR], capture_output=True, text=True, cwd=ROOT)
        assert result.returncode == 0, f"Generator failed: {result.stderr}"
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            new = f.read()
        assert new == orig, "Registry not idempotent"