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
        assert registry["registry_version"] == "3.0"

    def test_repository(self, registry):
        assert registry["repository"] == "al3obdi/saudi-legal-corpus-ai"

    def test_total_tracks(self, registry):
        assert registry["total_tracks"] == 31

    def test_validation_status(self, registry):
        assert registry["validation_status"] == "PASS"

    def test_total_primary_arabic(self, registry):
        assert registry["total_primary_arabic_governing_records"] == 4486

    def test_total_reference(self, registry):
        assert registry["total_reference_records"] == 614

    def test_total_internal_reference(self, registry):
        assert registry["total_internal_reference_records"] == 281

    def test_total_ir(self, registry):
        assert registry["total_implementing_regulations_records"] == 169

    def test_total_registry_counted(self, registry):
        assert registry["total_registry_counted_records"] == 5381

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
        assert "labor_model_work_regulation" in ids
        assert "labor_saudization_mediation_rules" in ids
        assert "labor_recruitment_services_rules" in ids
        assert "labor_accessibility_arrangements" in ids
        assert "labor_model_contract_forms" in ids
        assert "evidence_law" in ids
        assert "evidence_electronic_procedures_rules" in ids
        assert "evidence_procedural_manuals" in ids
        assert "evidence_expertise_rules" in ids
        assert "personal_status_law" in ids
        assert "personal_status_implementing_regulation" in ids
        assert "sharia_procedure_law" in ids
        assert "sharia_procedure_implementing_regulation" in ids
        assert "criminal_procedure_law" in ids
        assert "criminal_procedure_implementing_regulation" in ids
        assert "enforcement_law" in ids
        assert "enforcement_implementing_regulation" in ids
        assert "judiciary_law" in ids

    def test_personal_status_counts(self, registry):
        law = next(t for t in registry["tracks"] if t["track_id"] == "personal_status_law")
        assert law["record_counts"]["arabic_articles"] == 252
        reg = next(t for t in registry["tracks"] if t["track_id"] == "personal_status_implementing_regulation")
        assert reg["record_counts"]["arabic_articles"] == 41
        for t in (law, reg):
            assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_sharia_procedure_law_counts(self, registry):
        sp = next(t for t in registry["tracks"] if t["track_id"] == "sharia_procedure_law")
        assert sp["record_counts"]["arabic_articles"] == 243
        assert sp["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 153, "معدلة": 14, "ملغاة": 75, "مضافة": 1}
        assert sp["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_sharia_procedure_regulation_counts(self, registry):
        sr = next(t for t in registry["tracks"]
                  if t["track_id"] == "sharia_procedure_implementing_regulation")
        rc = sr["record_counts"]
        assert rc["arabic_articles"] == 637
        assert rc["pdf_document_status_breakdown"] == {"اصلية": 536, "معدلة": 17, "ملغاة": 63, "مضافة": 21}
        assert rc["portal_legal_status_breakdown"] == {"اصلية": 388, "معدلة": 16, "ملغاة": 212, "مضافة": 21}
        assert rc["superseded_by_evidence_law"] == 149
        assert sr["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_criminal_procedure_law_counts(self, registry):
        cp = next(t for t in registry["tracks"] if t["track_id"] == "criminal_procedure_law")
        assert cp["record_counts"]["arabic_articles"] == 222
        assert cp["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 219, "معدلة": 3, "ملغاة": 0, "مضافة": 0}
        assert cp["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_criminal_procedure_regulation_counts(self, registry):
        cr = next(t for t in registry["tracks"] if t["track_id"] == "criminal_procedure_implementing_regulation")
        assert cr["record_counts"]["arabic_articles"] == 181
        assert cr["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 174, "معدلة": 7, "ملغاة": 0, "مضافة": 0}
        assert cr["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_enforcement_law_counts(self, registry):
        el = next(t for t in registry["tracks"] if t["track_id"] == "enforcement_law")
        assert el["record_counts"]["arabic_articles"] == 98
        assert el["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 94, "معدلة": 3, "ملغاة": 1, "مضافة": 0}
        assert el["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_enforcement_regulation_counts(self, registry):
        er = next(t for t in registry["tracks"] if t["track_id"] == "enforcement_implementing_regulation")
        assert er["record_counts"]["arabic_articles"] == 273
        assert er["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 266, "معدلة": 2, "ملغاة": 2, "مضافة": 3}
        assert er["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_judiciary_law_counts(self, registry):
        jl = next(t for t in registry["tracks"] if t["track_id"] == "judiciary_law")
        assert jl["record_counts"]["arabic_articles"] == 85
        assert jl["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 82, "معدلة": 3, "ملغاة": 0, "مضافة": 0}
        assert jl["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_evidence_companions_counts(self, registry):
        for tid, want in (("evidence_electronic_procedures_rules", 24),
                          ("evidence_procedural_manuals", 135),
                          ("evidence_expertise_rules", 34)):
            tr = next(t for t in registry["tracks"] if t["track_id"] == tid)
            assert tr["record_counts"]["arabic_articles"] == want
            assert tr["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_evidence_law_counts(self, registry):
        ev = next(t for t in registry["tracks"] if t["track_id"] == "evidence_law")
        assert ev["record_counts"]["arabic_articles"] == 129
        assert ev["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_labor_annex5_counts(self, registry):
        a5 = next(t for t in registry["tracks"] if t["track_id"] == "labor_model_contract_forms")
        assert a5["record_counts"]["total"] == 102
        assert a5["record_counts"]["form_units"] == 101
        assert a5["official_text_status"] == "HRSD_OFFICIAL_PDF_OCR_IMAGE_CROSS_CHECKED_BILINGUAL_FORM"
        en = a5["language_layers"]["english"]
        assert en["governing"] is False
        assert en["role"] == "reference_guidance_only"

    def test_labor_annex2_counts(self, registry):
        a2 = next(t for t in registry["tracks"] if t["track_id"] == "labor_accessibility_arrangements")
        assert a2["record_counts"]["accessibility_tables"] == 8
        assert a2["record_counts"]["table_rows"] == 40
        assert a2["official_text_status"] == "HRSD_OFFICIAL_PDF_ACTUALTEXT_OCR_IMAGE_CROSS_CHECKED"

    def test_labor_annex34_counts(self, registry):
        a3 = next(t for t in registry["tracks"] if t["track_id"] == "labor_saudization_mediation_rules")
        assert a3["record_counts"]["arabic_articles"] == 20
        a4 = next(t for t in registry["tracks"] if t["track_id"] == "labor_recruitment_services_rules")
        assert a4["record_counts"]["arabic_articles"] == 72
        for t in (a3, a4):
            assert t["official_text_status"] == "HRSD_OFFICIAL_PDF_OCR_CROSS_CHECKED"

    def test_labor_annex1_counts(self, registry):
        a1 = next(t for t in registry["tracks"] if t["track_id"] == "labor_model_work_regulation")
        assert a1["record_counts"]["arabic_articles"] == 72
        assert a1["record_counts"]["violation_tables"] == 3
        assert a1["official_text_status"] == "HRSD_OFFICIAL_PDF_OCR_IMAGE_CROSS_CHECKED"

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