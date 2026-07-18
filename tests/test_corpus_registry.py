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
        assert registry["total_tracks"] == 123

    def test_validation_status(self, registry):
        assert registry["validation_status"] == "PASS"

    def test_total_primary_arabic(self, registry):
        assert registry["total_primary_arabic_governing_records"] == 8594

    def test_total_reference(self, registry):
        assert registry["total_reference_records"] == 614

    def test_total_internal_reference(self, registry):
        assert registry["total_internal_reference_records"] == 281

    def test_total_ir(self, registry):
        assert registry["total_implementing_regulations_records"] == 169

    def test_total_registry_counted(self, registry):
        assert registry["total_registry_counted_records"] == 9489

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
        assert "board_of_grievances_law" in ids
        assert "law_practice_law" in ids
        assert "law_practice_implementing_regulation" in ids
        assert "commercial_courts_law" in ids
        assert "commercial_courts_implementing_regulation" in ids
        assert "bankruptcy_law" in ids
        assert "bankruptcy_implementing_regulation" in ids
        assert "bankruptcy_case_rules" in ids
        assert "judicial_costs_law" in ids
        assert "judicial_costs_implementing_regulation" in ids
        assert "arbitration_law" in ids
        assert "arbitration_implementing_regulation" in ids
        assert "commercial_papers_law" in ids
        assert "commercial_register_law" in ids
        assert "trade_names_law" in ids
        assert "commercial_agencies_law" in ids
        assert "chambers_of_commerce_law" in ids
        assert "commercial_books_law" in ids
        assert "aml_law" in ids
        assert "tawtheeq_law" in ids
        assert "tawtheeq_implementing_regulation" in ids
        assert "real_estate_registration_law" in ids
        assert "real_estate_registration_implementing_regulation" in ids
        assert "real_estate_mortgage_law" in ids
        assert "real_estate_finance_law" in ids
        assert "real_estate_units_law" in ids
        assert "real_estate_units_implementing_regulation" in ids
        assert "foreign_ownership_law" in ids
        assert "municipal_realestate_law" in ids
        assert "municipal_realestate_implementing_regulation" in ids
        assert "gcc_ownership_law" in ids
        assert "terrorism_law" in ids
        assert "terrorism_implementing_regulation" in ids
        assert "juveniles_law" in ids
        assert "juveniles_implementing_regulation" in ids
        assert "whistleblower_law" in ids
        assert "judicial_inspection_regulation" in ids
        assert "qismah_regulation" in ids
        assert "sulook_regulation" in ids
        assert "aawan_regulation" in ids
        assert "muslaha_regulation" in ids
        assert "iflas_hudud_regulation" in ids
        assert "judicial_documents_regulation" in ids
        assert "bankruptcy_fees_regulation" in ids
        assert "enforcement_providers_regulation" in ids
        assert "alimony_fund_regulation" in ids
        assert "judiciary_bog_mechanism" in ids
        assert "documentation_settlement_regulation" in ids
        assert "mosalaha_center_regulation" in ids
        assert "medical_reports_regulation" in ids
        assert "marriage_non_saudi_regulation" in ids
        assert "state_funded_lawyer_regulation" in ids
        assert "lessor_repossession_regulation" in ids
        assert "elitigation_guide_regulation" in ids
        assert "judicial_training_center_guide" in ids
        assert "judgment_objection_methods_regulation" in ids
        assert "real_estate_expropriation_law" in ids
        assert "marriage_contract_hearing_regulation" in ids
        assert "anti_bribery_law" in ids
        assert "basic_law_of_governance" in ids
        assert "anti_cyber_crime_law" in ids
        assert "anti_harassment_law" in ids
        assert "anti_trafficking_law" in ids
        assert "council_of_ministers_law" in ids
        assert "regions_law" in ids
        assert "electronic_transactions_law" in ids
        assert "allegiance_commission_law" in ids
        assert "shura_council_law" in ids
        assert "copyright_law" in ids
        assert "telecommunications_law" in ids
        assert "sama_law" in ids
        assert "banking_control_law" in ids
        assert "capital_market_law" in ids
        assert "competition_law" in ids
        assert "payment_systems_law" in ids
        assert "mining_investment_law" in ids
        assert "trademark_law" in ids
        assert "anti_concealment_law" in ids
        assert "insurance_control_law" in ids
        assert "ecommerce_law" in ids
        assert "vat_law" in ids
        assert "franchise_law" in ids
        assert "civil_aviation_law" in ids
        assert "anti_narcotics_law" in ids
        assert "traffic_law" in ids
        assert "environmental_law" in ids
        assert "income_tax_law" in ids
        assert "civil_service_law" in ids
        assert "social_insurance_law" in ids
        assert "social_insurance_legacy_law" in ids
        assert "zakat_law" in ids
        assert "patent_law" in ids

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

    def test_board_of_grievances_law_counts(self, registry):
        bog = next(t for t in registry["tracks"] if t["track_id"] == "board_of_grievances_law")
        assert bog["record_counts"]["arabic_articles"] == 26
        assert bog["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 25, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
        assert bog["official_text_status"] == "BOARD_OFFICIAL_PDF_VISUALLY_ADJUDICATED_GAZETTE_CONFIRMED"

    def test_law_practice_law_counts(self, registry):
        lp = next(t for t in registry["tracks"] if t["track_id"] == "law_practice_law")
        assert lp["record_counts"]["arabic_articles"] == 56
        assert lp["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 35, "معدلة": 8, "ملغاة": 1, "مضافة": 12}
        assert lp["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_law_practice_regulation_counts(self, registry):
        lr = next(t for t in registry["tracks"] if t["track_id"] == "law_practice_implementing_regulation")
        assert lr["record_counts"]["arabic_articles"] == 90
        assert lr["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 90, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert lr["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_commercial_courts_law_counts(self, registry):
        cc = next(t for t in registry["tracks"] if t["track_id"] == "commercial_courts_law")
        assert cc["record_counts"]["arabic_articles"] == 96
        assert cc["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 75, "معدلة": 1, "ملغاة": 20, "مضافة": 0}
        assert cc["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_commercial_courts_regulation_counts(self, registry):
        cr = next(t for t in registry["tracks"] if t["track_id"] == "commercial_courts_implementing_regulation")
        assert cr["record_counts"]["arabic_articles"] == 281
        assert cr["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 281, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert cr["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_bankruptcy_law_counts(self, registry):
        bk = next(t for t in registry["tracks"] if t["track_id"] == "bankruptcy_law")
        assert bk["record_counts"]["arabic_articles"] == 231
        assert bk["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 229, "معدلة": 2, "ملغاة": 0, "مضافة": 0}
        assert bk["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_bankruptcy_regulation_counts(self, registry):
        bk = next(t for t in registry["tracks"] if t["track_id"] == "bankruptcy_implementing_regulation")
        assert bk["record_counts"]["arabic_articles"] == 98
        assert bk["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 97, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
        assert bk["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_bankruptcy_case_rules_counts(self, registry):
        bk = next(t for t in registry["tracks"] if t["track_id"] == "bankruptcy_case_rules")
        assert bk["record_counts"]["arabic_articles"] == 24
        assert bk["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 24, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert bk["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_judicial_costs_law_counts(self, registry):
        jc = next(t for t in registry["tracks"] if t["track_id"] == "judicial_costs_law")
        assert jc["record_counts"]["arabic_articles"] == 23
        assert jc["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 23, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert jc["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_judicial_costs_regulation_counts(self, registry):
        jc = next(t for t in registry["tracks"] if t["track_id"] == "judicial_costs_implementing_regulation")
        assert jc["record_counts"]["arabic_articles"] == 17
        assert jc["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 17, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert jc["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_arbitration_law_counts(self, registry):
        ar = next(t for t in registry["tracks"] if t["track_id"] == "arbitration_law")
        assert ar["record_counts"]["arabic_articles"] == 58
        assert ar["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 55, "معدلة": 3, "ملغاة": 0, "مضافة": 0}
        assert ar["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_arbitration_regulation_counts(self, registry):
        ar = next(t for t in registry["tracks"] if t["track_id"] == "arbitration_implementing_regulation")
        assert ar["record_counts"]["arabic_articles"] == 19
        assert ar["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 18, "معدلة": 0, "ملغاة": 1, "مضافة": 0}
        assert ar["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_commercial_papers_law_counts(self, registry):
        cp = next(t for t in registry["tracks"] if t["track_id"] == "commercial_papers_law")
        assert cp["record_counts"]["arabic_articles"] == 121
        assert cp["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 118, "معدلة": 3, "ملغاة": 0, "مضافة": 0}
        assert cp["official_text_status"] == "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED"

    def test_commercial_register_law_counts(self, registry):
        cr = next(t for t in registry["tracks"] if t["track_id"] == "commercial_register_law")
        assert cr["record_counts"]["arabic_articles"] == 29
        assert cr["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 29, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert cr["official_text_status"] == "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED"

    def test_trade_names_law_counts(self, registry):
        tn = next(t for t in registry["tracks"] if t["track_id"] == "trade_names_law")
        assert tn["record_counts"]["arabic_articles"] == 23
        assert tn["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 23, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert tn["official_text_status"] == "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED"

    def test_commercial_agencies_law_counts(self, registry):
        ca = next(t for t in registry["tracks"] if t["track_id"] == "commercial_agencies_law")
        assert ca["record_counts"]["arabic_articles"] == 6
        assert ca["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 3, "معدلة": 3, "ملغاة": 0, "مضافة": 0}
        assert ca["official_text_status"] == "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED"

    def test_chambers_of_commerce_law_counts(self, registry):
        ch = next(t for t in registry["tracks"] if t["track_id"] == "chambers_of_commerce_law")
        assert ch["record_counts"]["arabic_articles"] == 66
        assert ch["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 66, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert ch["official_text_status"] == "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED"

    def test_commercial_books_law_counts(self, registry):
        cb = next(t for t in registry["tracks"] if t["track_id"] == "commercial_books_law")
        assert cb["record_counts"]["arabic_articles"] == 16
        assert cb["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 16, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert cb["official_text_status"] == "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED"

    def test_aml_law_counts(self, registry):
        aml = next(t for t in registry["tracks"] if t["track_id"] == "aml_law")
        assert aml["record_counts"]["arabic_articles"] == 52
        assert aml["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 44, "معدلة": 7, "ملغاة": 0, "مضافة": 1}
        assert aml["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_tawtheeq_law_counts(self, registry):
        tw = next(t for t in registry["tracks"] if t["track_id"] == "tawtheeq_law")
        assert tw["record_counts"]["arabic_articles"] == 57
        assert tw["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 52, "معدلة": 5, "ملغاة": 0, "مضافة": 0}
        assert tw["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_tawtheeq_regulation_counts(self, registry):
        twr = next(t for t in registry["tracks"] if t["track_id"] == "tawtheeq_implementing_regulation")
        assert twr["record_counts"]["arabic_articles"] == 31
        assert twr["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 31, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert twr["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_real_estate_registration_law_counts(self, registry):
        rer = next(t for t in registry["tracks"] if t["track_id"] == "real_estate_registration_law")
        assert rer["record_counts"]["arabic_articles"] == 40
        assert rer["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 37, "معدلة": 3, "ملغاة": 0, "مضافة": 0}
        assert rer["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_real_estate_registration_regulation_counts(self, registry):
        rerr = next(t for t in registry["tracks"] if t["track_id"] == "real_estate_registration_implementing_regulation")
        assert rerr["record_counts"]["arabic_articles"] == 51
        assert rerr["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 51, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert rerr["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_real_estate_mortgage_law_counts(self, registry):
        rem = next(t for t in registry["tracks"] if t["track_id"] == "real_estate_mortgage_law")
        assert rem["record_counts"]["arabic_articles"] == 46
        assert rem["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 46, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert rem["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_real_estate_finance_law_counts(self, registry):
        refin = next(t for t in registry["tracks"] if t["track_id"] == "real_estate_finance_law")
        assert refin["record_counts"]["arabic_articles"] == 15
        assert refin["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 15, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert refin["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_real_estate_units_law_counts(self, registry):
        reun = next(t for t in registry["tracks"] if t["track_id"] == "real_estate_units_law")
        assert reun["record_counts"]["arabic_articles"] == 33
        assert reun["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 33, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert reun["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_real_estate_units_regulation_counts(self, registry):
        reunr = next(t for t in registry["tracks"] if t["track_id"] == "real_estate_units_implementing_regulation")
        assert reunr["record_counts"]["arabic_articles"] == 41
        assert reunr["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 39, "معدلة": 2, "ملغاة": 0, "مضافة": 0}
        assert reunr["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_foreign_ownership_law_counts(self, registry):
        rfo = next(t for t in registry["tracks"] if t["track_id"] == "foreign_ownership_law")
        assert rfo["record_counts"]["arabic_articles"] == 15
        assert rfo["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 15, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert rfo["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_municipal_realestate_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "municipal_realestate_law")
        assert t["record_counts"]["arabic_articles"] == 6
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 6, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_municipal_realestate_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "municipal_realestate_implementing_regulation")
        assert t["record_counts"]["arabic_articles"] == 35
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 31, "معدلة": 3, "ملغاة": 0, "مضافة": 1}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_gcc_ownership_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "gcc_ownership_law")
        assert t["record_counts"]["arabic_articles"] == 6
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 6, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_terrorism_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "terrorism_law")
        assert t["record_counts"]["arabic_articles"] == 99
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 88, "معدلة": 8, "ملغاة": 0, "مضافة": 3}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_terrorism_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "terrorism_implementing_regulation")
        assert t["record_counts"]["arabic_articles"] == 28
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 18, "معدلة": 7, "ملغاة": 1, "مضافة": 2}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_juveniles_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "juveniles_law")
        assert t["record_counts"]["arabic_articles"] == 24
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 24, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_juveniles_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "juveniles_implementing_regulation")
        assert t["record_counts"]["arabic_articles"] == 13
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 13, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_whistleblower_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "whistleblower_law")
        assert t["record_counts"]["arabic_articles"] == 37
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 37, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_judicial_inspection_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "judicial_inspection_regulation")
        assert t["record_counts"]["arabic_articles"] == 68
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 68, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_qismah_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "qismah_regulation")
        assert t["record_counts"]["arabic_articles"] == 48
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 48, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_sulook_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "sulook_regulation")
        assert t["record_counts"]["arabic_articles"] == 47
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 44, "معدلة": 1, "ملغاة": 0, "مضافة": 2}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_aawan_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "aawan_regulation")
        assert t["record_counts"]["arabic_articles"] == 35
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 35, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_muslaha_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "muslaha_regulation")
        assert t["record_counts"]["arabic_articles"] == 29
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 26, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_iflas_hudud_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "iflas_hudud_regulation")
        assert t["record_counts"]["arabic_articles"] == 23
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 23, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_judicial_documents_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "judicial_documents_regulation")
        assert t["record_counts"]["arabic_articles"] == 23
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 23, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_bankruptcy_fees_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "bankruptcy_fees_regulation")
        assert t["record_counts"]["arabic_articles"] == 20
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 20, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_enforcement_providers_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "enforcement_providers_regulation")
        assert t["record_counts"]["arabic_articles"] == 18
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 18, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_alimony_fund_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "alimony_fund_regulation")
        assert t["record_counts"]["arabic_articles"] == 17
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 17, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_judiciary_bog_mechanism_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "judiciary_bog_mechanism")
        assert t["record_counts"]["arabic_articles"] == 15
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 14, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_documentation_settlement_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "documentation_settlement_regulation")
        assert t["record_counts"]["arabic_articles"] == 15
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 14, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_mosalaha_center_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "mosalaha_center_regulation")
        assert t["record_counts"]["arabic_articles"] == 10
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 10, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_medical_reports_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "medical_reports_regulation")
        assert t["record_counts"]["arabic_articles"] == 13
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 13, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_marriage_non_saudi_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "marriage_non_saudi_regulation")
        assert t["record_counts"]["arabic_articles"] == 11
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 11, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_state_funded_lawyer_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "state_funded_lawyer_regulation")
        assert t["record_counts"]["arabic_articles"] == 11
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 11, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_lessor_repossession_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "lessor_repossession_regulation")
        assert t["record_counts"]["arabic_articles"] == 7
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 7, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_elitigation_guide_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "elitigation_guide_regulation")
        assert t["record_counts"]["arabic_articles"] == 5
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 5, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_judicial_training_center_guide_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "judicial_training_center_guide")
        assert t["record_counts"]["arabic_articles"] == 18
        assert t["record_counts"]["legal_status_breakdown"] == {
            "اصلية": 9, "معدلة": 2, "ملغاة": 0, "مضافة": 0, "NARRATIVE_NOT_APPLICABLE": 7}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_judgment_objection_methods_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "judgment_objection_methods_regulation")
        assert t["record_counts"]["arabic_articles"] == 62
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 62, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_real_estate_expropriation_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "real_estate_expropriation_law")
        assert t["record_counts"]["arabic_articles"] == 39
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 39, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_marriage_contract_hearing_regulation_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "marriage_contract_hearing_regulation")
        assert t["record_counts"]["arabic_articles"] == 10
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 10, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"

    def test_anti_bribery_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "anti_bribery_law")
        assert t["record_counts"]["arabic_articles"] == 25
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 16, "معدلة": 7, "ملغاة": 0, "مضافة": 2}
        assert t["official_text_status"] == "MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER"

    def test_basic_law_of_governance_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "basic_law_of_governance")
        assert t["record_counts"]["arabic_articles"] == 83
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 82, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER"

    def test_anti_cyber_crime_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "anti_cyber_crime_law")
        assert t["record_counts"]["arabic_articles"] == 16
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 16, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "BOE_PORTAL_TRIPLE_SOURCE_EXHAUSTIVE_VERIFIED"

    def test_anti_harassment_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "anti_harassment_law")
        assert t["record_counts"]["arabic_articles"] == 8
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 7, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER"

    def test_anti_trafficking_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "anti_trafficking_law")
        assert t["record_counts"]["arabic_articles"] == 17
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 17, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "BOE_WAYBACK_SNAPSHOT_UNODC_ENGLISH_SUBSTANCE_VERIFIED"

    def test_council_of_ministers_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "council_of_ministers_law")
        assert t["record_counts"]["arabic_articles"] == 32
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 31, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "DUAL_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE"

    def test_regions_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "regions_law")
        assert t["record_counts"]["arabic_articles"] == 41
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 31, "معدلة": 9, "ملغاة": 0, "مضافة": 1}
        assert t["official_text_status"] == "DUAL_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE"

    def test_electronic_transactions_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "electronic_transactions_law")
        assert t["record_counts"]["arabic_articles"] == 31
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 24, "معدلة": 5, "ملغاة": 2, "مضافة": 0}
        assert t["official_text_status"] == "SINGLE_PRIMARY_SOURCE_WIPO_STRUCTURAL_CROSS_CHECK_MANUAL_LIGATURE_CORRECTION"

    def test_allegiance_commission_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "allegiance_commission_law")
        assert t["record_counts"]["arabic_articles"] == 25
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 25, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "TRIPLE_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE"

    def test_shura_council_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "shura_council_law")
        assert t["record_counts"]["arabic_articles"] == 30
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 24, "معدلة": 6, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER"

    def test_copyright_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "copyright_law")
        assert t["record_counts"]["arabic_articles"] == 28
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 19, "معدلة": 9, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "SECONDARY_SOURCE_STRUCTURAL_WIPO_CROSS_CHECK_BOE_UNREACHABLE"

    def test_telecommunications_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "telecommunications_law")
        assert t["record_counts"]["arabic_articles"] == 41
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 41, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "BOE_PORTAL_PRIMARY_SOURCE_MCIT_PDF_CROSS_CHECKED"

    def test_sama_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "sama_law")
        assert t["record_counts"]["arabic_articles"] == 27
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 24, "معدلة": 3, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "GOVERNMENT_AGENCY_OFFICIAL_PDF_PRIMARY_SOURCE_BOE_ARCHIVE_CROSS_VERIFIED"

    def test_banking_control_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "banking_control_law")
        assert t["record_counts"]["arabic_articles"] == 26
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 25, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "DUAL_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE"

    def test_capital_market_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "capital_market_law")
        assert t["record_counts"]["arabic_articles"] == 68
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 42, "معدلة": 25, "ملغاة": 0, "مضافة": 1}
        assert t["official_text_status"] == "MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER"

    def test_competition_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "competition_law")
        assert t["record_counts"]["arabic_articles"] == 28
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 28, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "DUAL_PRIMARY_SOURCE_BOE_WAYBACK_X_NEZAMS_CROSS_VERIFIED"

    def test_payment_systems_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "payment_systems_law")
        assert t["record_counts"]["arabic_articles"] == 20
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 20, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "SAMA_OFFICIAL_PDF_OCR_X_NEZAMS_CROSS_VERIFIED"

    def test_mining_investment_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "mining_investment_law")
        assert t["record_counts"]["arabic_articles"] == 64
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 63, "معدلة": 0, "ملغاة": 0, "مضافة": 1}
        assert t["official_text_status"] == "BOE_PORTAL_WAYBACK_X_FAOLEX_CROSS_VERIFIED"

    def test_trademark_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "trademark_law")
        assert t["record_counts"]["arabic_articles"] == 52
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 51, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "WIPO_LEX_PRIMARY_PDF_X_BOE_STATUS_CARD_CROSS_VERIFIED"

    def test_anti_concealment_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "anti_concealment_law")
        assert t["record_counts"]["arabic_articles"] == 20
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 20, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "TRIPLE_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE"

    def test_insurance_control_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "insurance_control_law")
        assert t["record_counts"]["arabic_articles"] == 25
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 17, "معدلة": 8, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "MISA_OFFICIAL_PDF_X_NEZAMS_CROSS_VERIFIED_BOE_UNREACHABLE"

    def test_ecommerce_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "ecommerce_law")
        assert t["record_counts"]["arabic_articles"] == 26
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 26, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "BOE_PORTAL_WAYBACK_X_NEZAMS_CROSS_VERIFIED"

    def test_vat_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "vat_law")
        assert t["record_counts"]["arabic_articles"] == 53
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 51, "معدلة": 2, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "ZATCA_OFFICIAL_PDF_X_BOE_PORTAL_CROSS_VERIFIED"

    def test_franchise_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "franchise_law")
        assert t["record_counts"]["arabic_articles"] == 27
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 27, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "BOE_PORTAL_PROXY_RETRIEVED_QANONIAH_SPOT_CROSS_VERIFIED"

    def test_civil_aviation_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "civil_aviation_law")
        assert t["record_counts"]["arabic_articles"] == 180
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 168, "معدلة": 12, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "NEZAMS_PRIMARY_X_RAKADVOCATE_SPOT_CHECKED"

    def test_anti_narcotics_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "anti_narcotics_law")
        assert t["record_counts"]["arabic_articles"] == 74
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 74, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "BOE_PROXY_X_NEZAMS_X_QADHA_REFERENCE_TRIPLE_VERIFIED"

    def test_traffic_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "traffic_law")
        assert t["record_counts"]["arabic_articles"] == 86
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 52, "معدلة": 32, "ملغاة": 1, "مضافة": 1}
        assert t["official_text_status"] == "BOE_PROXY_X_NEZAMS_PATTERN_VERIFIED_MIXED_CONFIDENCE"

    def test_environmental_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "environmental_law")
        assert t["record_counts"]["arabic_articles"] == 49
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 48, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "BOE_WAYBACK_X_GREEN_ORG_PDF_X_NEZAMS_TRIPLE_VERIFIED_ART1_BOE_SELF_CONTRADICTION"

    def test_income_tax_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "income_tax_law")
        assert t["record_counts"]["arabic_articles"] == 81
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 52, "معدلة": 29, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "BOE_WAYBACK_X_ZATCA_PDF_X_GSTC_PDF_X_NEZAMS_CROSS_VERIFIED_CH10_BOE_ONLY"

    def test_civil_service_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "civil_service_law")
        assert t["record_counts"]["arabic_articles"] == 44
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 20, "معدلة": 19, "ملغاة": 1, "مضافة": 4}
        assert t["official_text_status"] == "BOE_WAYBACK_X_NEZAMS_FULL_CROSS_VERIFIED"

    def test_social_insurance_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "social_insurance_law")
        assert t["record_counts"]["arabic_articles"] == 63
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 63, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "BOE_WAYBACK_PRIMARY_X_NEZAMS_SPOTCHECK_X_QANOONSA_STRUCTURE_VERIFIED"

    def test_social_insurance_legacy_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "social_insurance_legacy_law")
        assert t["record_counts"]["arabic_articles"] == 71
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 63, "معدلة": 7, "ملغاة": 0, "مضافة": 1}
        assert t["official_text_status"] == "BOE_WAYBACK_X_NEZAMS_SPOTCHECK_X_OKAZ_ALRIYADH_CORROBORATED"

    def test_zakat_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "zakat_law")
        assert t["record_counts"]["arabic_articles"] == 128
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 127, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
        assert t["official_text_status"] == "ZATCA_PDF_PRIMARY_SINGLE_SOURCE_GAZETTE_SPOT_VERIFIED"

    def test_patent_law_counts(self, registry):
        t = next(x for x in registry["tracks"] if x["track_id"] == "patent_law")
        assert t["record_counts"]["arabic_articles"] == 66
        assert t["record_counts"]["legal_status_breakdown"] == {"اصلية": 59, "معدلة": 6, "ملغاة": 0, "مضافة": 1}
        assert t["official_text_status"] == "WIPOLEX_M45_CONSOLIDATED_X_BOE_PLAINTEXT_STALE_TERMINOLOGY_CROSS_VERIFIED"

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