#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpus Registry Index Foundation — Generator

Creates a canonical, machine-readable corpus registry that summarizes and
links all completed corpus tracks in the repository.

Read-only: reads existing files for counts/metadata, does not modify any corpus data.
Idempotent: deterministic JSON output.

Output:
  data/corpus_registry/corpus_registry.json

Usage:
    python3 scripts/gen_corpus_registry.py
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
import sys
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(ROOT, "data", "corpus_registry", "corpus_registry.json")

# Files to read for counts/metadata
COMPANIES_AR_LLM = os.path.join(ROOT, "data", "official_arabic_legal_llm", "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
COMPANIES_EN_LLM = os.path.join(ROOT, "data", "official_english_legal_llm", "companies_law_m132_1443_official_english_legal_llm_001_281.json")
CHINESE_AUDIT = os.path.join(ROOT, "reports", "chinese_translation_review", "chinese_remediation_program_closure_audit.json")
LAW_PROFILE = os.path.join(ROOT, "data", "legal_corpus_factory", "law_profiles", "sa_companies_law_m132_1443.profile.json")
GEN_LLM = os.path.join(ROOT, "data", "implementing_regulations", "general", "general_implementing_regulations_arabic_legal_llm.json")
GEN_FORMS = os.path.join(ROOT, "data", "implementing_regulations", "general", "general_implementing_regulations_arabic_forms_llm.json")
GEN_MANIFEST = os.path.join(ROOT, "data", "implementing_regulations", "general", "source_manifest.json")
LJS_LLM = os.path.join(ROOT, "data", "implementing_regulations", "listed_joint_stock", "listed_joint_stock_implementing_regulation_arabic_legal_llm.json")
LJS_APP = os.path.join(ROOT, "data", "implementing_regulations", "listed_joint_stock", "listed_joint_stock_implementing_regulation_arabic_appendix_llm.json")
LJS_MANIFEST = os.path.join(ROOT, "data", "implementing_regulations", "listed_joint_stock", "source_manifest.json")
CLOSURE_AUDIT = os.path.join(ROOT, "reports", "implementing_regulations", "implementing_regulations_arabic_program_closure_audit.json")
PDPL_LAW_LLM = os.path.join(ROOT, "data", "pdpl_arabic_legal_llm", "pdpl_arabic_law_legal_llm_001_043.json")
PDPL_REG_LLM = os.path.join(ROOT, "data", "pdpl_arabic_legal_llm", "pdpl_implementing_regulation_arabic_legal_llm_001_038.json")
INVESTMENT_LAW_LLM = os.path.join(ROOT, "data", "investment_arabic_legal_llm", "investment_law_legal_llm_001_016.json")
INVESTMENT_REG_LLM = os.path.join(ROOT, "data", "investment_arabic_legal_llm", "investment_regulation_legal_llm_001_037.json")
GTPL_REG_LLM = os.path.join(ROOT, "data", "gtpl_arabic_legal_llm", "gtpl_regulation_legal_llm_001_157.json")
GTPL_LAW_LLM = os.path.join(ROOT, "data", "gtpl_arabic_legal_llm", "gtpl_law_legal_llm_001_099.json")
GTPL_EN_REF = os.path.join(ROOT, "sources", "gtpl", "law", "reference_english", "gtpl_m128_official_english_reference.json")
CIVIL_LAW_LLM = os.path.join(ROOT, "data", "civil_arabic_legal_llm", "civil_transactions_law_legal_llm_001_721.json")
LABOR_LAW_LLM = os.path.join(ROOT, "data", "labor_arabic_legal_llm", "labor_law_legal_llm_001_245.json")
LABOR_REG_LLM = os.path.join(ROOT, "data", "labor_arabic_legal_llm", "labor_regulation_legal_llm_001_040.json")
LABOR_ANNEX1_LLM = os.path.join(ROOT, "data", "labor_arabic_legal_llm", "labor_annex1_legal_llm_001_072.json")
LABOR_ANNEX1_TAB = os.path.join(ROOT, "data", "labor_arabic_legal_llm", "labor_annex1_violation_tables_llm.json")
LABOR_ANNEX3_LLM = os.path.join(ROOT, "data", "labor_arabic_legal_llm", "labor_annex3_legal_llm_001_020.json")
LABOR_ANNEX4_LLM = os.path.join(ROOT, "data", "labor_arabic_legal_llm", "labor_annex4_legal_llm_001_072.json")
LABOR_ANNEX2_LLM = os.path.join(ROOT, "data", "labor_arabic_legal_llm", "labor_annex2_accessibility_tables_llm.json")
LABOR_ANNEX5_LLM = os.path.join(ROOT, "data", "labor_arabic_legal_llm", "labor_annex5_contract_forms_llm.json")
EVIDENCE_LAW_LLM = os.path.join(ROOT, "data", "evidence_arabic_legal_llm", "evidence_law_legal_llm_001_129.json")
EVIDENCE_ELEC_LLM = os.path.join(ROOT, "data", "evidence_arabic_legal_llm", "evidence_electronic_rules_legal_llm_001_024.json")
EVIDENCE_MANUALS_LLM = os.path.join(ROOT, "data", "evidence_arabic_legal_llm", "evidence_procedural_manuals_legal_llm_001_135.json")
EVIDENCE_EXPERT_LLM = os.path.join(ROOT, "data", "evidence_arabic_legal_llm", "evidence_expertise_rules_legal_llm_001_034.json")
PS_LAW_LLM = os.path.join(ROOT, "data", "personal_status_arabic_legal_llm", "personal_status_law_legal_llm_001_252.json")
PS_REG_LLM = os.path.join(ROOT, "data", "personal_status_arabic_legal_llm", "personal_status_regulation_legal_llm_001_041.json")
SHARIA_PROC_LAW_LLM = os.path.join(ROOT, "data", "sharia_procedure_arabic_legal_llm", "sharia_procedure_law_legal_llm_001_243.json")
SHARIA_PROC_REG_LLM = os.path.join(ROOT, "data", "sharia_procedure_arabic_legal_llm", "sharia_procedure_regulation_legal_llm_001_637.json")
CRIM_PROC_LAW_LLM = os.path.join(ROOT, "data", "criminal_procedure_arabic_legal_llm", "criminal_procedure_law_legal_llm_001_222.json")
CRIM_PROC_REG_LLM = os.path.join(ROOT, "data", "criminal_procedure_arabic_legal_llm", "criminal_procedure_regulation_legal_llm_001_181.json")
ENFORCEMENT_LAW_LLM = os.path.join(ROOT, "data", "enforcement_arabic_legal_llm", "enforcement_law_legal_llm_001_098.json")
ENFORCEMENT_REG_LLM = os.path.join(ROOT, "data", "enforcement_arabic_legal_llm", "enforcement_regulation_legal_llm_001_273.json")
JUDICIARY_LAW_LLM = os.path.join(ROOT, "data", "judiciary_arabic_legal_llm", "judiciary_law_legal_llm_001_085.json")
BOG_LAW_LLM = os.path.join(ROOT, "data", "board_of_grievances_arabic_legal_llm", "board_of_grievances_law_legal_llm_001_026.json")
LAW_PRACTICE_LAW_LLM = os.path.join(ROOT, "data", "law_practice_arabic_legal_llm", "law_practice_law_legal_llm_001_056.json")
LAW_PRACTICE_REG_LLM = os.path.join(ROOT, "data", "law_practice_arabic_legal_llm", "law_practice_regulation_legal_llm_001_090.json")
COMMERCIAL_COURTS_LAW_LLM = os.path.join(ROOT, "data", "commercial_courts_arabic_legal_llm", "commercial_courts_law_legal_llm_001_096.json")
COMMERCIAL_COURTS_REG_LLM = os.path.join(ROOT, "data", "commercial_courts_arabic_legal_llm", "commercial_courts_regulation_legal_llm_001_281.json")
BANKRUPTCY_LAW_LLM = os.path.join(ROOT, "data", "bankruptcy_arabic_legal_llm", "bankruptcy_law_legal_llm_001_231.json")
BANKRUPTCY_REG_LLM = os.path.join(ROOT, "data", "bankruptcy_arabic_legal_llm", "bankruptcy_regulation_legal_llm_001_098.json")
BANKRUPTCY_RULES_LLM = os.path.join(ROOT, "data", "bankruptcy_arabic_legal_llm", "bankruptcy_case_rules_legal_llm_001_024.json")
JUDICIAL_COSTS_LAW_LLM = os.path.join(ROOT, "data", "judicial_costs_arabic_legal_llm", "judicial_costs_law_legal_llm_001_023.json")
JUDICIAL_COSTS_REG_LLM = os.path.join(ROOT, "data", "judicial_costs_arabic_legal_llm", "judicial_costs_regulation_legal_llm_001_017.json")
ARBITRATION_LAW_LLM = os.path.join(ROOT, "data", "arbitration_arabic_legal_llm", "arbitration_law_legal_llm_001_058.json")
ARBITRATION_REG_LLM = os.path.join(ROOT, "data", "arbitration_arabic_legal_llm", "arbitration_regulation_legal_llm_001_019.json")
COMMERCIAL_PAPERS_LAW_LLM = os.path.join(ROOT, "data", "commercial_papers_arabic_legal_llm", "commercial_papers_law_legal_llm_001_121.json")
COMMERCIAL_REGISTER_LAW_LLM = os.path.join(ROOT, "data", "commercial_register_arabic_legal_llm", "commercial_register_law_legal_llm_001_029.json")
TRADE_NAMES_LAW_LLM = os.path.join(ROOT, "data", "trade_names_arabic_legal_llm", "trade_names_law_legal_llm_001_023.json")
COMMERCIAL_AGENCIES_LAW_LLM = os.path.join(ROOT, "data", "commercial_agencies_arabic_legal_llm", "commercial_agencies_law_legal_llm_001_006.json")
CHAMBERS_OF_COMMERCE_LAW_LLM = os.path.join(ROOT, "data", "chambers_of_commerce_arabic_legal_llm", "chambers_of_commerce_law_legal_llm_001_066.json")
COMMERCIAL_BOOKS_LAW_LLM = os.path.join(ROOT, "data", "commercial_books_arabic_legal_llm", "commercial_books_law_legal_llm_001_016.json")
AML_LAW_LLM = os.path.join(ROOT, "data", "aml_arabic_legal_llm", "aml_law_legal_llm_001_052.json")
TAWTHEEQ_LAW_LLM = os.path.join(ROOT, "data", "tawtheeq_arabic_legal_llm", "tawtheeq_law_legal_llm_001_057.json")
TAWTHEEQ_REG_LLM = os.path.join(ROOT, "data", "tawtheeq_arabic_legal_llm", "tawtheeq_regulation_legal_llm_001_031.json")
REAL_ESTATE_REG_LAW_LLM = os.path.join(ROOT, "data", "real_estate_registration_arabic_legal_llm", "real_estate_registration_law_legal_llm_001_040.json")
REAL_ESTATE_REG_REG_LLM = os.path.join(ROOT, "data", "real_estate_registration_arabic_legal_llm", "real_estate_registration_regulation_legal_llm_001_051.json")
REAL_ESTATE_MORTGAGE_LAW_LLM = os.path.join(ROOT, "data", "real_estate_mortgage_arabic_legal_llm", "real_estate_mortgage_law_legal_llm_001_046.json")
REAL_ESTATE_FINANCE_LAW_LLM = os.path.join(ROOT, "data", "real_estate_finance_arabic_legal_llm", "real_estate_finance_law_legal_llm_001_015.json")
REAL_ESTATE_UNITS_LAW_LLM = os.path.join(ROOT, "data", "real_estate_units_arabic_legal_llm", "real_estate_units_law_legal_llm_001_033.json")
REAL_ESTATE_UNITS_REG_LLM = os.path.join(ROOT, "data", "real_estate_units_arabic_legal_llm", "real_estate_units_regulation_legal_llm_001_041.json")
FOREIGN_OWNERSHIP_LAW_LLM = os.path.join(ROOT, "data", "foreign_ownership_arabic_legal_llm", "foreign_ownership_law_legal_llm_001_015.json")
MUNICIPAL_RE_LAW_LLM = os.path.join(ROOT, "data", "municipal_realestate_arabic_legal_llm", "municipal_realestate_law_legal_llm_001_006.json")
MUNICIPAL_RE_REG_LLM = os.path.join(ROOT, "data", "municipal_realestate_arabic_legal_llm", "municipal_realestate_regulation_legal_llm_001_035.json")
GCC_OWNERSHIP_LAW_LLM = os.path.join(ROOT, "data", "gcc_ownership_arabic_legal_llm", "gcc_ownership_law_legal_llm_001_006.json")
TERRORISM_LAW_LLM = os.path.join(ROOT, "data", "terrorism_arabic_legal_llm", "terrorism_law_legal_llm_001_099.json")
TERRORISM_REG_LLM = os.path.join(ROOT, "data", "terrorism_arabic_legal_llm", "terrorism_regulation_legal_llm_001_028.json")
JUVENILES_LAW_LLM = os.path.join(ROOT, "data", "juveniles_arabic_legal_llm", "juveniles_law_legal_llm_001_024.json")
JUVENILES_REG_LLM = os.path.join(ROOT, "data", "juveniles_arabic_legal_llm", "juveniles_regulation_legal_llm_001_013.json")
LABOR_EN_REF_GLOB = os.path.join(ROOT, "data", "english_reference", "labor_law", "batch_*", "*.jsonl")
UNIFIED_INDEX = os.path.join(ROOT, "data", "corpus_unified_index", "corpus_unified_llm_index_summary.json")


def _load_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _dump_json(obj: Any, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def _file_exists(rel_path: str) -> bool:
    return os.path.isfile(os.path.join(ROOT, rel_path))


def main() -> int:
    # Load all source files
    companies_ar = _load_json(COMPANIES_AR_LLM)
    companies_en = _load_json(COMPANIES_EN_LLM)
    chinese_audit = _load_json(CHINESE_AUDIT)
    profile = _load_json(LAW_PROFILE)
    gen_llm = _load_json(GEN_LLM)
    gen_forms = _load_json(GEN_FORMS)
    gen_manifest = _load_json(GEN_MANIFEST)
    ljs_llm = _load_json(LJS_LLM)
    ljs_app = _load_json(LJS_APP)
    ljs_manifest = _load_json(LJS_MANIFEST)
    closure = _load_json(CLOSURE_AUDIT)
    pdpl_law_llm = _load_json(PDPL_LAW_LLM)
    pdpl_reg_llm = _load_json(PDPL_REG_LLM)
    investment_law_llm = _load_json(INVESTMENT_LAW_LLM)
    investment_reg_llm = _load_json(INVESTMENT_REG_LLM)
    civil_law_llm = _load_json(CIVIL_LAW_LLM)
    gtpl_law_llm = _load_json(GTPL_LAW_LLM)
    gtpl_reg_llm = _load_json(GTPL_REG_LLM)
    gtpl_en_ref = _load_json(GTPL_EN_REF)
    labor_law_llm = _load_json(LABOR_LAW_LLM)
    labor_reg_llm = _load_json(LABOR_REG_LLM)
    labor_annex1_llm = _load_json(LABOR_ANNEX1_LLM)
    labor_annex1_tab = _load_json(LABOR_ANNEX1_TAB)
    labor_annex3_llm = _load_json(LABOR_ANNEX3_LLM)
    labor_annex4_llm = _load_json(LABOR_ANNEX4_LLM)
    labor_annex2_llm = _load_json(LABOR_ANNEX2_LLM)
    labor_annex5_llm = _load_json(LABOR_ANNEX5_LLM)
    evidence_law_llm = _load_json(EVIDENCE_LAW_LLM)
    evidence_elec_llm = _load_json(EVIDENCE_ELEC_LLM)
    evidence_manuals_llm = _load_json(EVIDENCE_MANUALS_LLM)
    evidence_expert_llm = _load_json(EVIDENCE_EXPERT_LLM)
    ps_law_llm = _load_json(PS_LAW_LLM)
    ps_reg_llm = _load_json(PS_REG_LLM)
    sharia_proc_law_llm = _load_json(SHARIA_PROC_LAW_LLM)
    sharia_proc_reg_llm = _load_json(SHARIA_PROC_REG_LLM)
    crim_proc_law_llm = _load_json(CRIM_PROC_LAW_LLM)
    crim_proc_reg_llm = _load_json(CRIM_PROC_REG_LLM)
    enforcement_law_llm = _load_json(ENFORCEMENT_LAW_LLM)
    enforcement_reg_llm = _load_json(ENFORCEMENT_REG_LLM)
    judiciary_law_llm = _load_json(JUDICIARY_LAW_LLM)
    bog_law_llm = _load_json(BOG_LAW_LLM)
    law_practice_law_llm = _load_json(LAW_PRACTICE_LAW_LLM)
    law_practice_reg_llm = _load_json(LAW_PRACTICE_REG_LLM)
    commercial_courts_law_llm = _load_json(COMMERCIAL_COURTS_LAW_LLM)
    commercial_courts_reg_llm = _load_json(COMMERCIAL_COURTS_REG_LLM)
    bankruptcy_law_llm = _load_json(BANKRUPTCY_LAW_LLM)
    bankruptcy_reg_llm = _load_json(BANKRUPTCY_REG_LLM)
    bankruptcy_rules_llm = _load_json(BANKRUPTCY_RULES_LLM)
    judicial_costs_law_llm = _load_json(JUDICIAL_COSTS_LAW_LLM)
    judicial_costs_reg_llm = _load_json(JUDICIAL_COSTS_REG_LLM)
    arbitration_law_llm = _load_json(ARBITRATION_LAW_LLM)
    arbitration_reg_llm = _load_json(ARBITRATION_REG_LLM)
    commercial_papers_law_llm = _load_json(COMMERCIAL_PAPERS_LAW_LLM)
    commercial_register_law_llm = _load_json(COMMERCIAL_REGISTER_LAW_LLM)
    trade_names_law_llm = _load_json(TRADE_NAMES_LAW_LLM)
    commercial_agencies_law_llm = _load_json(COMMERCIAL_AGENCIES_LAW_LLM)
    chambers_of_commerce_law_llm = _load_json(CHAMBERS_OF_COMMERCE_LAW_LLM)
    commercial_books_law_llm = _load_json(COMMERCIAL_BOOKS_LAW_LLM)
    aml_law_llm = _load_json(AML_LAW_LLM)
    tawtheeq_law_llm = _load_json(TAWTHEEQ_LAW_LLM)
    tawtheeq_reg_llm = _load_json(TAWTHEEQ_REG_LLM)
    real_estate_reg_law_llm = _load_json(REAL_ESTATE_REG_LAW_LLM)
    real_estate_reg_reg_llm = _load_json(REAL_ESTATE_REG_REG_LLM)
    real_estate_mortgage_law_llm = _load_json(REAL_ESTATE_MORTGAGE_LAW_LLM)
    real_estate_finance_law_llm = _load_json(REAL_ESTATE_FINANCE_LAW_LLM)
    real_estate_units_law_llm = _load_json(REAL_ESTATE_UNITS_LAW_LLM)
    real_estate_units_reg_llm = _load_json(REAL_ESTATE_UNITS_REG_LLM)
    foreign_ownership_law_llm = _load_json(FOREIGN_OWNERSHIP_LAW_LLM)
    municipal_re_law_llm = _load_json(MUNICIPAL_RE_LAW_LLM)
    municipal_re_reg_llm = _load_json(MUNICIPAL_RE_REG_LLM)
    gcc_ownership_law_llm = _load_json(GCC_OWNERSHIP_LAW_LLM)
    terrorism_law_llm = _load_json(TERRORISM_LAW_LLM)
    terrorism_reg_llm = _load_json(TERRORISM_REG_LLM)
    juveniles_law_llm = _load_json(JUVENILES_LAW_LLM)
    juveniles_reg_llm = _load_json(JUVENILES_REG_LLM)
    labor_en_count = sum(
        sum(1 for line in open(p, encoding="utf-8") if line.strip())
        for p in sorted(glob.glob(LABOR_EN_REF_GLOB))
    )
    unified_index = _load_json(UNIFIED_INDEX)

    registry: dict[str, Any] = {
        "registry_version": "3.0",
        "generated_date": "2026-07-11",
        "repository": "al3obdi/saudi-legal-corpus-ai",
        "baseline_commit": "465776947125066bd1a705cfceacd3dca935ad1f",
        "legal_status_boundaries": {
            "arabic_official_source_governs": True,
            "not_official_translation": True,
            "not_legal_advice": True,
            "no_trilingual_alignment": True,
            "no_public_release": True,
            "english_reference_guidance_only": True,
            "chinese_internal_reference_only": True,
        },
        "total_tracks": 66,
        "total_primary_arabic_governing_records": (
            companies_ar["record_count"]        # 281 Companies Law
            + gen_llm["record_count"]           # 95 general IR articles
            + gen_forms["record_count"]         # 4 general IR forms
            + ljs_llm["record_count"]           # 69 listed JSC articles
            + ljs_app["record_count"]           # 1 listed JSC appendix
            + pdpl_law_llm["record_count"]      # 43 PDPL law (verified vs official SDAIA)
            + pdpl_reg_llm["record_count"]      # 38 PDPL implementing regulation (verified vs official SDAIA)
            + investment_law_llm["record_count"]  # 16 Investment law (verified from MISA)
            + investment_reg_llm["record_count"]  # 37 Investment regulation (verified from MISA)
            + civil_law_llm["record_count"]       # 721 Civil Transactions Law (owner-provided official text)
            + gtpl_law_llm["record_count"]        # 99 GTPL M/128 (mirror text cross-checked vs official MOF PDF)
            + gtpl_reg_llm["record_count"]        # 157 GTPL implementing regulation (re-extracted from official MOF PDF)
            + labor_law_llm["record_count"]       # 249 Labor Law (HRSD consolidated, cross-checked vs BOE captures)
            + labor_reg_llm["record_count"]       # 45 Labor implementing regulation (HRSD PDF, OCR + law-quote cross-checked)
            + labor_annex1_llm["record_count"]    # 72 Model work organization regulation (annex 1)
            + labor_annex1_tab["record_count"]    # 3 violation/penalty tables (annex 1, 50 rows)
            + labor_annex3_llm["record_count"]    # 20 Saudi-employment mediation rules (annex 3)
            + labor_annex4_llm["record_count"]    # 72 Recruitment and labor-services rules (annex 4)
            + labor_annex2_llm["record_count"]    # 8 accessibility-arrangements tables (annex 2, 40 rows)
            + labor_annex5_llm["record_count"]    # 102 model contract form units (annex 5, 4 forms + glossary)
            + evidence_law_llm["record_count"]    # 129 Evidence Law (MOJ portal DB cross-checked vs official MOJ PDF)
            + evidence_elec_llm["record_count"]   # 24 electronic evidentiary procedures rules
            + evidence_manuals_llm["record_count"]  # 135 procedural manuals for the Evidence Law
            + evidence_expert_llm["record_count"]   # 34 rules regulating expert affairs before the courts
            + ps_law_llm["record_count"]            # 252 Personal Status Law (MOJ portal DB cross-checked vs official PDF)
            + ps_reg_llm["record_count"]            # 41 Personal Status implementing regulation
            + sharia_proc_law_llm["record_count"]  # 243 Law of Sharia Procedure (consolidated, MOJ portal cross-checked)
            + sharia_proc_reg_llm["record_count"]  # 637 Sharia Procedure implementing regulation (consolidated, dual-status)
            + crim_proc_law_llm["record_count"]    # 222 Law of Criminal Procedure (consolidated, MOJ portal cross-checked)
            + crim_proc_reg_llm["record_count"]    # 181 Criminal Procedure implementing regulation (consolidated)
            + enforcement_law_llm["record_count"]  # 98 Enforcement Law (consolidated, MOJ portal cross-checked)
            + enforcement_reg_llm["record_count"]  # 273 Enforcement implementing regulation (consolidated)
            + judiciary_law_llm["record_count"]    # 85 Law of the Judiciary (foundational court-organization law)
            + bog_law_llm["record_count"]          # 26 Law of the Board of Grievances (administrative judiciary; Board PDF + gazette)
            + law_practice_law_llm["record_count"]  # 56 Code of Law Practice (MOJ portal cross-checked; consolidated)
            + law_practice_reg_llm["record_count"]  # 90 Implementing Regulation of the Code of Law Practice (1446H, MOJ portal cross-checked)
            + commercial_courts_law_llm["record_count"]  # 96 Commercial Courts Law (MOJ portal cross-checked; consolidated, evidence chapter repealed)
            + commercial_courts_reg_llm["record_count"]  # 281 Implementing Regulation of the Commercial Courts Law (1441H, MOJ portal cross-checked)
            + bankruptcy_law_llm["record_count"]  # 231 Bankruptcy Law (MOJ portal cross-checked; consolidated)
            + bankruptcy_reg_llm["record_count"]  # 98 Bankruptcy Regulation (MOJ portal cross-checked; consolidated)
            + bankruptcy_rules_llm["record_count"]  # 24 Bankruptcy Case Rules (MOJ portal cross-checked; fresh issuance)
            + judicial_costs_law_llm["record_count"]  # 23 Judicial Costs Law (MOJ portal cross-checked; fresh issuance)
            + judicial_costs_reg_llm["record_count"]  # 17 Judicial Costs Regulation (MOJ portal cross-checked; fresh issuance)
            + arbitration_law_llm["record_count"]  # 58 Arbitration Law (MOJ portal cross-checked; consolidated)
            + arbitration_reg_llm["record_count"]  # 19 Arbitration Regulation (MOJ portal cross-checked; consolidated)
            + commercial_papers_law_llm["record_count"]  # 121 Commercial Papers Law (BOE official portal, archive cross-snapshot verified)
            + commercial_register_law_llm["record_count"]  # 29 Commercial Register Law (BOE official portal, archive cross-snapshot verified)
            + trade_names_law_llm["record_count"]  # 23 Trade Names Law (BOE official portal, archive cross-snapshot verified)
            + commercial_agencies_law_llm["record_count"]  # 6 Commercial Agencies Law (BOE official portal, archive cross-snapshot verified)
            + chambers_of_commerce_law_llm["record_count"]  # 66 Chambers of Commerce Law (BOE official portal, archive cross-snapshot verified)
            + commercial_books_law_llm["record_count"]  # 16 Commercial Books Law (BOE official portal, archive cross-snapshot verified)
            + aml_law_llm["record_count"]  # 52 Anti-Money Laundering Law (MOJ double-official pipeline)
            + tawtheeq_law_llm["record_count"]  # 57 Notarization Law (MOJ double-official pipeline)
            + tawtheeq_reg_llm["record_count"]  # 31 Notarization Regulation (MOJ portal; 10 arts visually adjudicated)
            + real_estate_reg_law_llm["record_count"]  # 40 Real Estate In-Kind Registration Law (MOJ double-official pipeline)
            + real_estate_reg_reg_llm["record_count"]  # 51 Real Estate Registration Regulation (MOJ portal; 5 arts visually adjudicated)
            + real_estate_mortgage_law_llm["record_count"]  # 46 Registered Real Estate Mortgage Law (MOJ double-official pipeline)
            + real_estate_finance_law_llm["record_count"]  # 15 Real Estate Finance Law (MOJ double-official pipeline)
            + real_estate_units_law_llm["record_count"]  # 33 Real Estate Unit Ownership Law (MOJ double-official pipeline)
            + real_estate_units_reg_llm["record_count"]  # 41 Real Estate Unit Ownership Law Implementing Regulation (MOJ double-official pipeline)
            + foreign_ownership_law_llm["record_count"]  # 15 Non-Saudi Real Estate Ownership Law (MOJ double-official pipeline)
            + municipal_re_law_llm["record_count"]  # 6 Municipal Real Estate Disposal Law (MOJ double-official pipeline)
            + municipal_re_reg_llm["record_count"]  # 35 Municipal Real Estate Disposal Regulation (MOJ double-official pipeline)
            + gcc_ownership_law_llm["record_count"]  # 6 GCC Citizens Real Estate Ownership Regulation (MOJ double-official pipeline)
            + terrorism_law_llm["record_count"]  # 99 Law on Combating Crimes of Terrorism and its Financing (MOJ double-official pipeline)
            + terrorism_reg_llm["record_count"]  # 28 Implementing Regulation of the Law on Combating Crimes of Terrorism and its Financing (MOJ double-official pipeline)
            + juveniles_law_llm["record_count"]  # 24 Juveniles Law (MOJ double-official pipeline)
            + juveniles_reg_llm["record_count"]  # 13 Juveniles Law Implementing Regulation (MOJ double-official pipeline)
        ),
        "total_reference_records": companies_en["record_count"] + gtpl_en_ref["article_count"] + labor_en_count,  # 281 EN companies + 99 EN GTPL + 234 EN labor
        "total_internal_reference_records": chinese_audit.get("total_articles_implemented", 281),  # 281 Chinese
        "total_implementing_regulations_records": (
            gen_llm["record_count"] + gen_forms["record_count"]
            + ljs_llm["record_count"] + ljs_app["record_count"]
        ),
        "total_registry_counted_records": (
            companies_ar["record_count"]
            + gen_llm["record_count"] + gen_forms["record_count"]
            + ljs_llm["record_count"] + ljs_app["record_count"]
            + pdpl_law_llm["record_count"] + pdpl_reg_llm["record_count"]
            + investment_law_llm["record_count"] + investment_reg_llm["record_count"]
            + civil_law_llm["record_count"] + gtpl_law_llm["record_count"] + gtpl_reg_llm["record_count"]
            + labor_law_llm["record_count"] + labor_reg_llm["record_count"]
            + labor_annex1_llm["record_count"] + labor_annex1_tab["record_count"]
            + labor_annex3_llm["record_count"] + labor_annex4_llm["record_count"]
            + labor_annex2_llm["record_count"] + labor_annex5_llm["record_count"]
            + evidence_law_llm["record_count"] + evidence_elec_llm["record_count"]
            + evidence_manuals_llm["record_count"] + evidence_expert_llm["record_count"]
            + ps_law_llm["record_count"] + ps_reg_llm["record_count"]
            + sharia_proc_law_llm["record_count"] + sharia_proc_reg_llm["record_count"]
            + crim_proc_law_llm["record_count"] + crim_proc_reg_llm["record_count"]
            + enforcement_law_llm["record_count"] + enforcement_reg_llm["record_count"]
            + judiciary_law_llm["record_count"]
            + bog_law_llm["record_count"]
            + law_practice_law_llm["record_count"]
            + law_practice_reg_llm["record_count"]
            + commercial_courts_law_llm["record_count"]
            + commercial_courts_reg_llm["record_count"]
            + bankruptcy_law_llm["record_count"]
            + bankruptcy_reg_llm["record_count"]
            + bankruptcy_rules_llm["record_count"]
            + judicial_costs_law_llm["record_count"]
            + judicial_costs_reg_llm["record_count"]
            + arbitration_law_llm["record_count"]
            + arbitration_reg_llm["record_count"]
            + commercial_papers_law_llm["record_count"]
            + commercial_register_law_llm["record_count"]
            + trade_names_law_llm["record_count"]
            + commercial_agencies_law_llm["record_count"]
            + chambers_of_commerce_law_llm["record_count"]
            + commercial_books_law_llm["record_count"]
            + aml_law_llm["record_count"]
            + tawtheeq_law_llm["record_count"]
            + tawtheeq_reg_llm["record_count"]
            + real_estate_reg_law_llm["record_count"]
            + real_estate_reg_reg_llm["record_count"]
            + real_estate_mortgage_law_llm["record_count"]
            + real_estate_finance_law_llm["record_count"]
            + real_estate_units_law_llm["record_count"]
            + real_estate_units_reg_llm["record_count"]
            + foreign_ownership_law_llm["record_count"]
            + municipal_re_law_llm["record_count"]
            + municipal_re_reg_llm["record_count"]
            + gcc_ownership_law_llm["record_count"]
            + terrorism_law_llm["record_count"]
            + terrorism_reg_llm["record_count"]
            + juveniles_law_llm["record_count"]
            + juveniles_reg_llm["record_count"]
            + companies_en["record_count"] + gtpl_en_ref["article_count"] + labor_en_count
            + chinese_audit.get("total_articles_implemented", 281)
        ),
        "unified_retrieval_index": {
            "index_path": "data/corpus_unified_index/corpus_unified_llm_index.jsonl",
            "total_records": unified_index["total_records"],
            "records_per_corpus": unified_index.get("records_per_corpus", {}),
            "search_tool": "scripts/search_corpus_unified.py",
            "validator_target": "make corpus-unified-llm-index-validate",
            "note": "Flat cross-law retrieval index projecting all Arabic LLM-ready layers. A projection of already-counted records; NOT added to registry totals to avoid double-counting.",
        },
        "count_policy": {
            "counting_method": "raw_layer_records_not_deduplicated_legal_article_units",
            "primary_arabic_governing_records_included": True,
            "english_reference_records_included": True,
            "chinese_internal_reference_records_included": True,
            "forms_and_appendices_counted": True,
            "closure_audit_aggregate_not_counted_separately": True,
            "closure_audit_total_duplicates_underlying_ir_records": True,
            "formula_total_primary_arabic_governing": "companies_law_arabic(281) + general_ir_articles(95) + general_ir_forms(4) + listed_jsc_articles(69) + listed_jsc_appendix(1) + pdpl_law(43) + pdpl_implementing_regulation(38) + investment_law(16) + investment_implementing_regulation(37) + civil_transactions_law(721) + gtpl_law(99) + gtpl_implementing_regulation(157) + labor_law(249) + labor_implementing_regulation(45) + labor_model_work_regulation(72) + labor_annex1_violation_tables(3) + labor_annex3_mediation_rules(20) + labor_annex4_recruitment_rules(72) + labor_annex2_accessibility_tables(8) + labor_annex5_contract_forms(102) + evidence_law(129) + evidence_electronic_rules(24) + evidence_procedural_manuals(135) + evidence_expertise_rules(34) + personal_status_law(252) + personal_status_regulation(41) + sharia_procedure_law(243) + sharia_procedure_regulation(637) + criminal_procedure_law(222) + criminal_procedure_regulation(181) + enforcement_law(98) + enforcement_regulation(273) + judiciary_law(85) + board_of_grievances_law(26) + law_practice_law(56) + law_practice_regulation(90) + commercial_courts_law(96) + commercial_courts_regulation(281) + bankruptcy_law(231) + bankruptcy_regulation(98) + bankruptcy_case_rules(24) + judicial_costs_law(23) + judicial_costs_regulation(17) + arbitration_law(58) + arbitration_regulation(19) + commercial_papers_law(121) + commercial_register_law(29) + trade_names_law(23) + commercial_agencies_law(6) + chambers_of_commerce_law(66) + commercial_books_law(16) + aml_law(52) + tawtheeq_law(57) + tawtheeq_regulation(31) + real_estate_registration_law(40) + real_estate_registration_regulation(51) + real_estate_mortgage_law(46) + real_estate_finance_law(15) + real_estate_units_law(33) + real_estate_units_regulation(41) + foreign_ownership_law(15) + municipal_realestate_law(6) + municipal_realestate_regulation(35) + gcc_ownership_law(6) + terrorism_law(99) + terrorism_regulation(28) + juveniles_law(24) + juveniles_regulation(13) = 6358",
            "formula_total_reference": "companies_law_english(281) + gtpl_english_boe_translation(99) + labor_law_english(234) = 614",
            "formula_total_internal_reference": "companies_law_chinese_remediation(281)",
            "formula_total_implementing_regulations": "companies-family only: general_articles(95) + general_forms(4) + listed_jsc_articles(69) + listed_jsc_appendix(1) = 169 (PDPL and Investment regulations are counted under their own primary Arabic tracks)",
            "formula_total_registry_counted": "total_primary_arabic_governing(6358) + total_reference(614) + total_internal_reference(281) = 7253",
            "pdpl_arabic_records_status": "PDPL law (43) and implementing regulation (38) are now VERIFIED against the official SDAIA-published text (cross-checked against independent OCR/extraction) and carry LLM-ready enrichment layers. Arabic governs; not legal advice.",
            "investment_arabic_records_status": "Investment law (16) and implementing regulation (37) are verified from the official Ministry of Investment (MISA) Arabic PDFs and carry LLM-ready enrichment layers. Arabic governs; not legal advice.",
            "civil_arabic_records_status": "Civil Transactions Law (721) is the owner-provided full official Arabic text (Royal Decree M/191, 1444H), now CROSS-CHECKED article-by-article against the official MOJ legal-portal database (721/721 aligned, law unamended) with divergences adjudicated visually against the official MOJ PDF (committed): 17 single-word defects corrected and 21 trailing structural headings moved to section_context, all documented in the source artifact and audit files under sources/civil/law/moj_cross_check/. Arabic governs; not legal advice.",
            "labor_arabic_records_status": "Labor Law (249 records: 245 articles + 4 مكرر; 38 officially deleted flagged) is the official HRSD consolidated text (Royal Decree M/51, 1426H, amendments through M/44 merged), cross-verified against the repository's independently captured BOE base texts with ZERO unexplained differences. The Labor implementing regulation (45 records: articles 1-40 + 5 مكرر; 3 deleted flagged) is the official HRSD PDF core text, verified against rendered-page OCR and against the law track via the PDF's own verbatim law quotes (all >= 0.95). Both carry LLM-ready enrichment layers. The 234 English labor records are reference/guidance only. Arabic governs; not legal advice.",
            "note": "Closure audit total (169) equals total_implementing_regulations_records and is NOT added separately to avoid double-counting. Chinese remediation articles (281) are internal reference records. PDPL Arabic (43+38=81), Investment Arabic (16+37=53), Civil Arabic (721), and Labor Arabic (249+45+72+3+20+72+8+102=571) Evidence Arabic (129+24+135+34=322), Personal Status Arabic (252+41=293), and Sharia Procedure Arabic (243 law + 637 implementing regulation = 880, consolidated amended texts), Criminal Procedure Arabic (222 law + 181 implementing regulation = 403, consolidated amended texts), Enforcement Arabic (98 law + 273 implementing regulation = 371, consolidated amended texts), Judiciary Arabic (85 law, the foundational court-organization statute), and Board of Grievances Arabic (26 law, the administrative-judiciary statute; 25 اصلية + 1 معدّلة, sourced from the Board's certified PDF with Article 4's م/180 amendment from Umm Al-Qura 5072, SPA-confirmed), and Code of Law Practice Arabic (56 law + 90 implementing regulation = 146; the law is 35 اصلية / 8 معدلة / 12 مضافة / 1 ملغاة consolidated through M/21 1447H, the regulation is the fresh 1446H Active issuance all 90 اصلية superseding the InActive 1423H one, MOJ portal cross-checked), and Commercial Courts Arabic (96 law; 75 اصلية / 1 معدلة / 20 ملغاة, consolidated M/93 1441H — its evidence chapter arts 38-57 repealed by the Evidence Law M/43) and its implementing regulation (281 articles, the fresh 1441H Active issuance all اصلية), MOJ portal cross-checked), and Bankruptcy Arabic (231 law; 229 اصلية / 2 معدلة, consolidated M/89 1439H — per its art 230 the law repeals arts 103-137 of the old Commercial Court Law and the old Protective Settlement law, MOJ portal cross-checked) and its implementing regulation (98 articles; 97 اصلية / 1 معدلة — the fresh 1440H Active issuance by Council of Ministers Decision 622, art 2 amended by Decision 171 1443H, MOJ portal cross-checked, 98/98 matched outright) and the Rules Organizing Bankruptcy Case Procedures before the Commercial Courts (24 articles; fresh 1441H Active issuance all اصلية by Minister of Justice Decision 6421, MOJ portal cross-checked, 24/24 matched outright), and the Judicial Costs Law (23 articles; fresh 1443H Active issuance all اصلية by Royal Decree M/16, MOJ portal cross-checked) with its implementing regulation (17 articles; fresh 1443H Active issuance all اصلية by Council of Ministers Decision 519, MOJ portal cross-checked), and the Arbitration Law (58 articles; consolidated M/34 1433H, 55 اصلية / 3 معدلة, MOJ portal cross-checked — the official source labels the 31st article «الحادية والعشرون», a documented drafting anomaly preserved verbatim and numbered by ordinal position) with its implementing regulation (19 articles; 18 اصلية / 1 ملغاة by Council of Ministers Decision 541 1438H, MOJ portal cross-checked), and the Commercial Papers Law (121 articles; consolidated M/37 1383H, 118 اصلية / 3 معدلة — arts 118-120 amended by M/45 1409H — sourced from the Bureau of Experts (BOE) official portal via Wayback archive, cross-verified byte-identical across two independent-date snapshots), the Commercial Register Law (29 articles; fresh M/83 1446H issuance all اصلية, BOE official portal via Wayback archive, cross-verified byte-identical), and the Trade Names Law (23 articles; fresh M/83 1446H issuance all اصلية, BOE official portal via Wayback archive, cross-verified byte-identical), and the Commercial Agencies Law (6 articles; consolidated M/11 1382H, 3 اصلية / 3 معدلة — arts 4, 5 replaced by M/32 1400H and M/8 1393H, art 6 carries an M/5 1389H addition — BOE official portal via Wayback archive, cross-verified byte-identical), the Chambers of Commerce Law (66 articles; consolidated M/37 1442H issuance all اصلية, BOE official portal via Wayback archive, cross-verified byte-identical), and the Commercial Books Law (16 articles; consolidated M/61 1409H issuance all اصلية, BOE official portal via Wayback archive, cross-verified byte-identical), and the Anti-Money Laundering Law (52 records; consolidated M/20 1439H, 44 اصلية / 7 معدلة (arts 14, 15, 16, 18, 28, 33, 50) / 1 مضافة (art 49 مكرر) — all amendments by Royal Decree M/223 1447H, MOJ portal cross-checked against the official MOJ PDF, 49/52 matched outright and 3 long definition/list articles visually adjudicated verbatim), and the Notarization Law (57 records; consolidated M/164 1441H, 52 اصلية / 5 معدلة (arts 11, 12, 38, 40 by M/21 1447H; art 15 by M/191 1444H) / 0 ملغاة / 0 مضافة, MOJ portal cross-checked against the official MOJ PDF, all 57/57 matched outright and additionally corroborated against the Bureau of Experts official portal via Wayback archive) with its implementing regulation (31 records; fresh Minister of Justice Decision 1948 1442H issuance all اصلية — 30 articles + the official fee schedule «جدول المقابل المالي» as record 31, MOJ portal cross-checked against the official MOJ PDF; 21/31 matched outright and 10 list articles adjudicated visually verbatim on the rendered pages, the OCR channel being unavailable for that PDF in the build environment), and the Real Estate In-Kind Registration Law (40 records; the IN-FORCE law by Royal Decree M/91 1443H, 37 اصلية / 3 معدلة (arts 6, 9, 11 by M/123 1447H) — it supersedes the older repealed law of the same name (M/6 1423H, InActive on the MOJ portal), which is not ingested; MOJ portal cross-checked against the official MOJ PDF, all 40/40 matched outright) with its implementing regulation (51 records; the IN-FORCE regulation issued 27/1/1444H implementing M/91, all 51 اصلية — it supersedes the older repealed regulation of the same name (1425H, InActive), which is not ingested; MOJ portal cross-checked against the official MOJ PDF, 46/51 matched outright and 5 long/table articles adjudicated visually verbatim, art 42's official specification table carrying legitimate English remote-sensing tokens), and the Registered Real Estate Mortgage Law (46 records; fresh Royal Decree M/49 1433H issuance all اصلية, MOJ portal cross-checked against the official MOJ PDF — 44/46 matched outright and 2 long articles adjudicated visually verbatim), and the Real Estate Finance Law (15 records; fresh Royal Decree M/50 1433H issuance all اصلية, MOJ portal cross-checked against the official MOJ PDF — all 15/15 matched outright, mean 0.965, no visual adjudication needed), and the Real Estate Unit Ownership Law (33 records; Royal Decree M/85 1441H, all اصلية — it replaced the repealed 1423H unit-ownership-and-partition law, which is not ingested; MOJ portal cross-checked against the official MOJ PDF — all 33/33 matched outright, mean 0.971, no visual adjudication needed) with its implementing regulation (41 records; Minister of Municipal, Rural Affairs and Housing Decision 168 1441H implementing M/85; 39 اصلية / 2 معدلة (arts 4, 10) — MOJ portal cross-checked against the official MOJ PDF, 40/41 matched outright and 1 long article adjudicated visually verbatim), and the Non-Saudi Real Estate Ownership Law (15 records; fresh Royal Decree M/14 1447H issuance all اصلية — per its art 14 it replaced the repealed M/15 1421H ownership-and-investment law, which is not ingested; MOJ portal cross-checked against the official MOJ PDF, 12/15 matched outright and 3 articles adjudicated visually verbatim), and the Municipal Real Estate Disposal Law (6 records; Royal Decree M/64 1392H, all اصلية; MOJ portal cross-checked against the official MOJ PDF, 6/6 matched outright) with its implementing regulation (35 records; High Order 40152 1441H implementing M/64; 31 اصلية / 3 معدلة (arts 10, 13, 21) / 1 مضافة (art 13 مكرر), replacing the repealed 1423H regulation which is not ingested; MOJ portal cross-checked against the official MOJ PDF, 31/35 matched outright and 4 articles adjudicated visually verbatim), and the GCC Citizens Real Estate Ownership Regulation (6 records; Royal Decree M/22 1432H, all اصلية — it replaced the repealed 1422H GCC ownership regulation, which is not ingested; MOJ portal cross-checked against the official MOJ PDF, 6/6 matched outright), and the Law on Combating Crimes of Terrorism and its Financing (99 records; consolidated Royal Decree M/21 1439H, 88 اصلية / 8 معدلة / 3 مضافة (arts 59, 63, 81 مكرر) — it superseded the older M/16 1435H terrorism law; MOJ portal cross-checked against the official MOJ PDF, 90/99 matched outright and 9 long articles adjudicated visually verbatim) with its implementing regulation (28 records; Council of Ministers Decision 228 1440H implementing M/21; 18 اصلية / 7 معدلة / 1 ملغاة (art 9, flagged not deleted) / 2 مضافة (arts 20, 23 مكرر) — MOJ portal cross-checked against the official MOJ PDF, 26/28 matched outright and 2 list articles adjudicated visually verbatim), and the Juveniles Law (24 records; fresh Royal Decree M/113 1439H issuance all اصلية; MOJ portal cross-checked against the official MOJ PDF, 22/24 matched outright and 2 articles adjudicated visually verbatim) with its implementing regulation (13 records; Council of Ministers Decision 237 1442H implementing M/113, all اصلية; MOJ portal cross-checked against the official MOJ PDF, 12/13 matched outright and 1 article adjudicated visually verbatim) are primary Arabic governing-language records. The annex-5 records embed the official bilingual form's printed English column as a non-governing text_en_reference field (not counted as separate reference records). The unified retrieval index (5509) is a projection of counted records and is NOT added to totals.",
        },
        "validation_status": "PASS",
        "tracks": [
            {
                "track_id": "companies_law",
                "display_name_ar": "نظام الشركات",
                "display_name_en": "Saudi Companies Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "language_layers": {
                    "arabic": {
                        "status": "complete",
                        "governing": True,
                        "record_count": companies_ar["record_count"],
                        "data_path": "data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json",
                    },
                    "english": {
                        "status": "complete",
                        "governing": False,
                        "role": "reference_guidance_only",
                        "record_count": companies_en["record_count"],
                        "data_path": "data/official_english_legal_llm/companies_law_m132_1443_official_english_legal_llm_001_281.json",
                    },
                    "chinese": {
                        "status": "remediation_complete",
                        "governing": False,
                        "role": "internal_reference_only",
                        "total_articles_in_plan": chinese_audit.get("total_articles_in_plan", 281),
                        "total_articles_implemented": chinese_audit.get("total_articles_implemented", 281),
                        "closure_audit_path": "reports/chinese_translation_review/chinese_remediation_program_closure_audit.json",
                        "note": "Chinese remediation P0-P3 complete. Internal/non-official/non-binding/non-governing. Not a full public Chinese 281 layer. Not trilingual alignment.",
                    },
                },
                "governing_language": "ar",
                "status": "complete",
                "source_authority": "Bureau of Experts at the Council of Ministers / هيئة الخبراء بمجلس الوزراء",
                "source_url": "",
                "publication_date_hijri": "",
                "publication_date_gregorian": "",
                "record_counts": {
                    "arabic_articles": companies_ar["record_count"],
                    "english_articles": companies_en["record_count"],
                    "chinese_remediation_articles": chinese_audit.get("total_articles_implemented", 281),
                    "total": companies_ar["record_count"],
                },
                "data_paths": [
                    "data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json",
                    "data/official_english_legal_llm/companies_law_m132_1443_official_english_legal_llm_001_281.json",
                    "data/legal_corpus_factory/law_profiles/sa_companies_law_m132_1443.profile.json",
                ],
                "manifest_paths": [
                    "data/legal_corpus_factory/law_profiles/sa_companies_law_m132_1443.profile.json",
                ],
                "validator_targets": [
                    "make official-arabic-legal-llm-full-validate",
                    "make english-legal-llm-validate" if _file_exists("scripts/validate_english_legal_llm.py") else "make official-english-legal-llm-full-validate",
                    "make chinese-remediation-program-closure-validate",
                ],
                "report_paths": [
                    "reports/chinese_translation_review/chinese_remediation_program_closure_audit.json",
                ],
                "boundaries": {
                    "arabic_governs": True,
                    "english_reference_only": True,
                    "chinese_internal_reference_only": True,
                    "not_official_translation": True,
                    "not_legal_advice": True,
                    "no_trilingual_alignment": True,
                    "no_public_release": True,
                },
                "notes": "First implemented law profile. 281 articles. Arabic is governing. English is reference/guidance. Chinese is internal remediation complete (not a public full layer).",
            },
            {
                "track_id": "implementing_regulations_general",
                "display_name_ar": gen_manifest.get("source_title", "اللائحة التنفيذية لنظام الشركات"),
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "language_layers": {
                    "arabic": {
                        "status": "complete",
                        "governing": True,
                        "record_count": gen_llm["record_count"],
                    },
                },
                "governing_language": "ar",
                "status": "complete",
                "source_authority": "Ministry of Commerce / وزارة التجارة",
                "source_url": gen_manifest.get("source_url", ""),
                "publication_date_hijri": gen_manifest.get("publication_date_hijri", ""),
                "publication_date_gregorian": gen_manifest.get("publication_date_gregorian", ""),
                "record_counts": {
                    "articles": gen_llm["record_count"],
                    "forms": gen_forms["record_count"],
                    "total": gen_llm["record_count"] + gen_forms["record_count"],
                },
                "data_paths": [
                    "data/implementing_regulations/general/general_implementing_regulations_arabic_source.json",
                    "data/implementing_regulations/general/general_implementing_regulations_arabic_legal_llm.json",
                    "data/implementing_regulations/general/general_implementing_regulations_arabic_forms_llm.json",
                ],
                "manifest_paths": [
                    "data/implementing_regulations/general/source_manifest.json",
                ],
                "validator_targets": [
                    "make implementing-regulations-general-arabic-source-validate",
                    "make implementing-regulations-general-arabic-legal-llm-validate",
                ],
                "report_paths": [
                    "reports/implementing_regulations/GENERAL_IMPLEMENTING_REGULATIONS_ARABIC_LEGAL_LLM_LAYER_REPORT.txt",
                ],
                "boundaries": {
                    "arabic_governs": True,
                    "not_official_translation": True,
                    "not_legal_advice": True,
                    "no_trilingual_alignment": True,
                    "no_public_release": True,
                    "is_general": True,
                    "is_specialized": False,
                },
                "notes": "General implementing regulations covering all company forms. 95 articles + 4 forms. Separate from listed joint-stock sub-track.",
            },
            {
                "track_id": "implementing_regulations_listed_joint_stock",
                "display_name_ar": ljs_manifest.get("source_title", "اللائحة التنفيذية لنظام الشركات الخاصة بشركات المساهمة المدرجة"),
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "language_layers": {
                    "arabic": {
                        "status": "complete",
                        "governing": True,
                        "record_count": ljs_llm["record_count"],
                    },
                },
                "governing_language": "ar",
                "status": "complete",
                "source_authority": ljs_llm.get("issuing_authority", "مجلس هيئة السوق المالية"),
                "source_url": ljs_manifest.get("source_url", ""),
                "publication_date_hijri": ljs_manifest.get("publication_date_hijri", ""),
                "publication_date_gregorian": ljs_manifest.get("publication_date_gregorian", ""),
                "record_counts": {
                    "articles": ljs_llm["record_count"],
                    "appendices": ljs_app["record_count"],
                    "total": ljs_llm["record_count"] + ljs_app["record_count"],
                },
                "data_paths": [
                    "data/implementing_regulations/listed_joint_stock/listed_joint_stock_implementing_regulation_arabic_source.json",
                    "data/implementing_regulations/listed_joint_stock/listed_joint_stock_implementing_regulation_arabic_legal_llm.json",
                    "data/implementing_regulations/listed_joint_stock/listed_joint_stock_implementing_regulation_arabic_appendix_llm.json",
                ],
                "manifest_paths": [
                    "data/implementing_regulations/listed_joint_stock/source_manifest.json",
                ],
                "validator_targets": [
                    "make implementing-regulations-listed-jsc-arabic-source-validate",
                    "make implementing-regulations-listed-jsc-arabic-legal-llm-validate",
                ],
                "report_paths": [
                    "reports/implementing_regulations/LISTED_JOINT_STOCK_ARABIC_LEGAL_LLM_LAYER_REPORT.txt",
                ],
                "boundaries": {
                    "arabic_governs": True,
                    "not_official_translation": True,
                    "not_legal_advice": True,
                    "no_trilingual_alignment": True,
                    "no_public_release": True,
                    "is_general": False,
                    "is_specialized": True,
                    "specialized_scope": "listed joint-stock companies (شركات المساهمة المدرجة)",
                },
                "notes": "Specialized implementing regulation for listed joint-stock companies only. NOT a general implementing regulation. 69 articles + 1 appendix. Issued by Capital Market Authority board.",
            },
            {
                "track_id": "implementing_regulations_arabic_program_closure",
                "display_name_ar": "تدقيق إغلاق برنامج اللوائح التنفيذية العربية",
                "corpus_family": "closure_audit",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "language_layers": {
                    "arabic": {"status": "complete", "governing": True},
                },
                "governing_language": "ar",
                "status": "complete",
                "source_authority": "",
                "record_counts": closure["counts"],
                "data_paths": [
                    "reports/implementing_regulations/implementing_regulations_arabic_program_closure_audit.json",
                ],
                "manifest_paths": [],
                "validator_targets": [
                    "make implementing-regulations-arabic-program-closure-validate",
                ],
                "report_paths": [
                    "reports/implementing_regulations/IMPLEMENTING_REGULATIONS_ARABIC_PROGRAM_CLOSURE_AUDIT_AR.md",
                    "reports/implementing_regulations/IMPLEMENTING_REGULATIONS_ARABIC_PROGRAM_CLOSURE_AUDIT_REPORT.txt",
                ],
                "boundaries": {
                    "arabic_governs": True,
                    "not_official_translation": True,
                    "not_legal_advice": True,
                    "no_trilingual_alignment": True,
                    "no_public_release": True,
                },
                "notes": "Closure/status audit for the implementing regulations Arabic program. Covers general (95+4) and listed joint-stock (69+1) tracks. 169 total records.",
            },
            {
                "track_id": "pdpl_law",
                "display_name_ar": "نظام حماية البيانات الشخصية",
                "display_name_en": "Personal Data Protection Law (PDPL)",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT",
                "language_layers": {
                    "arabic": {
                        "status": "complete",
                        "governing": True,
                        "record_count": pdpl_law_llm["record_count"],
                        "data_path": "data/pdpl_arabic_legal_llm/pdpl_arabic_law_legal_llm_001_043.json",
                    },
                },
                "record_counts": {
                    "arabic_articles": pdpl_law_llm["record_count"],
                    "total": pdpl_law_llm["record_count"],
                },
                "data_paths": [
                    "sources/pdpl/verified/pdpl_arabic_law_verified_records.jsonl",
                    "data/pdpl_arabic_legal_llm/pdpl_arabic_law_legal_llm_001_043.json",
                ],
                "validator_targets": [
                    "make pdpl-arabic-law-verified-validate",
                    "make pdpl-arabic-law-legal-llm-validate",
                ],
                "report_paths": [
                    "reports/pdpl/PDPL_ARABIC_LAW_NEXT_LAYER_QA_REPORT.md",
                ],
                "boundaries": {
                    "arabic_governs": True,
                    "not_official_translation": True,
                    "not_verified_official_text": False,
                    "not_legal_advice": True,
                    "no_trilingual_alignment": True,
                    "no_public_release": True,
                },
                "notes": "PDPL law (43 articles, Article 32 = ملغاة), VERIFIED against the official SDAIA-published text and cross-checked vs independent OCR; LLM-ready enrichment layer. Arabic governs; no translation / no legal interpretation.",
            },
            {
                "track_id": "pdpl_implementing_regulation",
                "display_name_ar": "اللائحة التنفيذية لنظام حماية البيانات الشخصية",
                "display_name_en": "PDPL Implementing Regulation",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT",
                "language_layers": {
                    "arabic": {
                        "status": "complete",
                        "governing": True,
                        "record_count": pdpl_reg_llm["record_count"],
                        "data_path": "data/pdpl_arabic_legal_llm/pdpl_implementing_regulation_arabic_legal_llm_001_038.json",
                    },
                },
                "record_counts": {
                    "arabic_articles": pdpl_reg_llm["record_count"],
                    "total": pdpl_reg_llm["record_count"],
                },
                "data_paths": [
                    "sources/pdpl/regulation/verified/pdpl_implementing_regulation_arabic_verified_records.jsonl",
                    "data/pdpl_arabic_legal_llm/pdpl_implementing_regulation_arabic_legal_llm_001_038.json",
                ],
                "validator_targets": [
                    "make pdpl-implementing-regulation-arabic-verified-validate",
                    "make pdpl-implementing-regulation-arabic-legal-llm-validate",
                ],
                "report_paths": [],
                "boundaries": {
                    "arabic_governs": True,
                    "is_general": False,
                    "is_specialized": False,
                    "not_official_translation": True,
                    "not_verified_official_text": False,
                    "not_legal_advice": True,
                    "no_trilingual_alignment": True,
                    "no_public_release": True,
                },
                "notes": "PDPL implementing regulation (38 articles), VERIFIED against the official SDAIA-published text and cross-checked vs independent extraction; LLM-ready enrichment layer. Arabic governs; no translation / no legal interpretation.",
            },
            {
                "track_id": "investment_law",
                "display_name_ar": "نظام الاستثمار",
                "display_name_en": "Saudi Investment Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "VERIFIED_TRANSCRIBED_FROM_OFFICIAL_MISA_PDF",
                "source_authority": "Ministry of Investment / وزارة الاستثمار",
                "language_layers": {
                    "arabic": {
                        "status": "complete",
                        "governing": True,
                        "record_count": investment_law_llm["record_count"],
                        "data_path": "data/investment_arabic_legal_llm/investment_law_legal_llm_001_016.json",
                    },
                },
                "record_counts": {
                    "arabic_articles": investment_law_llm["record_count"],
                    "total": investment_law_llm["record_count"],
                },
                "data_paths": [
                    "sources/investment/law/verified/investment_law_verified_records.jsonl",
                    "data/investment_arabic_legal_llm/investment_law_legal_llm_001_016.json",
                ],
                "validator_targets": [
                    "make investment-law-verified-validate",
                    "make investment-law-legal-llm-validate",
                ],
                "report_paths": [],
                "boundaries": {
                    "arabic_governs": True,
                    "not_official_translation": True,
                    "not_verified_official_text": False,
                    "not_legal_advice": True,
                    "no_trilingual_alignment": True,
                    "no_public_release": True,
                },
                "notes": "Investment Law (16 articles), Royal Decree M/19 dated 16/1/1446H, verified verbatim from the official MISA bilingual PDF (Arabic governing; English reference only); LLM-ready enrichment layer.",
            },
            {
                "track_id": "investment_implementing_regulation",
                "display_name_ar": "اللائحة التنفيذية لنظام الاستثمار",
                "display_name_en": "Investment Law Implementing Regulations",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "VERIFIED_TRANSCRIBED_FROM_OFFICIAL_MISA_PDF",
                "source_authority": "Ministry of Investment / وزارة الاستثمار",
                "language_layers": {
                    "arabic": {
                        "status": "complete",
                        "governing": True,
                        "record_count": investment_reg_llm["record_count"],
                        "data_path": "data/investment_arabic_legal_llm/investment_regulation_legal_llm_001_037.json",
                    },
                },
                "record_counts": {
                    "arabic_articles": investment_reg_llm["record_count"],
                    "total": investment_reg_llm["record_count"],
                },
                "data_paths": [
                    "sources/investment/regulation/verified/investment_regulation_verified_records.jsonl",
                    "data/investment_arabic_legal_llm/investment_regulation_legal_llm_001_037.json",
                ],
                "validator_targets": [
                    "make investment-regulation-verified-validate",
                    "make investment-regulation-legal-llm-validate",
                ],
                "report_paths": [],
                "boundaries": {
                    "arabic_governs": True,
                    "is_general": False,
                    "is_specialized": False,
                    "not_official_translation": True,
                    "not_verified_official_text": False,
                    "not_legal_advice": True,
                    "no_trilingual_alignment": True,
                    "no_public_release": True,
                },
                "notes": "Investment Implementing Regulations (37 articles), verified verbatim from the official MISA Arabic PDF (render + Arabic-OCR corrected against the images, cross-checked vs the official English edition); LLM-ready enrichment layer.",
            },
            {
                "track_id": "civil_transactions_law",
                "display_name_ar": "نظام المعاملات المدنية",
                "display_name_en": "Civil Transactions Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "OWNER_PROVIDED_CROSS_CHECKED_MOJ_PORTAL",
                "source_authority": "Bureau of Experts at the Council of Ministers / هيئة الخبراء بمجلس الوزراء",
                "language_layers": {
                    "arabic": {
                        "status": "complete",
                        "governing": True,
                        "record_count": civil_law_llm["record_count"],
                        "data_path": "data/civil_arabic_legal_llm/civil_transactions_law_legal_llm_001_721.json",
                    },
                },
                "record_counts": {
                    "arabic_articles": civil_law_llm["record_count"],
                    "total": civil_law_llm["record_count"],
                },
                "data_paths": [
                    "sources/civil/law/verified/civil_transactions_law_verified_records.jsonl",
                    "data/civil_arabic_legal_llm/civil_transactions_law_legal_llm_001_721.json",
                ],
                "validator_targets": [
                    "make civil-transactions-law-verified-validate",
                    "make civil-transactions-law-legal-llm-validate",
                ],
                "report_paths": [],
                "boundaries": {
                    "arabic_governs": True,
                    "not_official_translation": True,
                    "not_verified_official_text": False,
                    "not_legal_advice": True,
                    "no_trilingual_alignment": True,
                    "no_public_release": True,
                },
                "notes": "Civil Transactions Law (721 articles), Royal Decree M/191 dated 29/11/1444H. Owner-provided full official Arabic text, CROSS-CHECKED article-by-article against the official MOJ legal-portal database (721/721 aligned; law unamended, every article اصلية) with divergences adjudicated visually against the official MOJ PDF (committed at inputs/civil_official_pdfs/ with recorded sha256): 17 single-word defects corrected, 21 trailing structural headings moved to section_context — all documented in the source artifact and the audit files under sources/civil/law/moj_cross_check/. Presentation note: the official print numbers clauses in 243 articles where this text uses unnumbered paragraphs (bodies verbatim). LLM-ready enrichment layer. Arabic governs.",
            },
            {
                "track_id": "gtpl_law",
                "display_name_ar": "نظام المنافسات والمشتريات الحكومية",
                "display_name_en": "Government Tenders and Procurement Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MIRROR_TEXT_CROSS_CHECKED_AGAINST_OFFICIAL_MOF_PDF",
                "source_authority": "Ministry of Finance / وزارة المالية (official consolidated PDF cross-check); English: Bureau of Experts official translation",
                "language_layers": {
                    "arabic": {"status": "complete", "governing": True,
                               "record_count": gtpl_law_llm["record_count"],
                               "data_path": "data/gtpl_arabic_legal_llm/gtpl_law_legal_llm_001_099.json"},
                    "english": {"status": "complete", "governing": False, "role": "reference_guidance_only",
                                "record_count": gtpl_en_ref["article_count"],
                                "data_path": "sources/gtpl/law/reference_english/gtpl_m128_official_english_reference.json"},
                },
                "record_counts": {"arabic_articles": gtpl_law_llm["record_count"],
                                  "english_articles": gtpl_en_ref["article_count"],
                                  "total": gtpl_law_llm["record_count"]},
                "data_paths": [
                    "sources/gtpl/law/official_source/gtpl_m128_official_source.json",
                    "sources/gtpl/law/verified/gtpl_law_verified_records.jsonl",
                    "data/gtpl_arabic_legal_llm/gtpl_law_legal_llm_001_099.json",
                    "sources/gtpl/law/reference_english/gtpl_m128_official_english_reference.json",
                ],
                "validator_targets": ["make gtpl-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "GTPL M/128 dated 13/11/1440H (99 articles) — the CURRENT law; supersedes M/58 (1427H) per its Article 98. Arabic captured from a public mirror and cross-checked token-by-token against the official MOF consolidated PDF; English is the official BOE translation, reference only.",
            },
            {
                "track_id": "gtpl_implementing_regulation",
                "display_name_ar": "اللائحة التنفيذية لنظام المنافسات والمشتريات الحكومية",
                "display_name_en": "GTPL Implementing Regulation",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "REEXTRACTED_FROM_OFFICIAL_MOF_PDF_CROSS_CHECKED",
                "source_authority": "Ministry of Finance / وزارة المالية",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": gtpl_reg_llm["record_count"],
                    "data_path": "data/gtpl_arabic_legal_llm/gtpl_regulation_legal_llm_001_157.json"}},
                "record_counts": {"arabic_articles": gtpl_reg_llm["record_count"],
                                  "total": gtpl_reg_llm["record_count"]},
                "data_paths": [
                    "sources/gtpl/regulation/official_source/gtpl_regulation_official_source.json",
                    "sources/gtpl/regulation/verified/gtpl_regulation_verified_records.jsonl",
                    "data/gtpl_arabic_legal_llm/gtpl_regulation_legal_llm_001_157.json",
                ],
                "validator_targets": ["make gtpl-regulation-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "GTPL Implementing Regulation (157 articles, consolidated amended edition), re-extracted at glyph level from the official MOF consolidated PDF (pipeline validated at 0.996 vs the known law text; duplicate copies adjudicated against rendered pages). Arabic governs.",
            },
            {
                "track_id": "labor_law",
                "display_name_ar": "نظام العمل",
                "display_name_en": "Saudi Labor Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "HRSD_CONSOLIDATED_CROSS_CHECKED_BOE",
                "source_authority": "Ministry of Human Resources and Social Development / وزارة الموارد البشرية والتنمية الاجتماعية (official consolidated PDF); cross-checked vs independent BOE captures",
                "language_layers": {
                    "arabic": {"status": "complete", "governing": True,
                               "record_count": labor_law_llm["record_count"],
                               "data_path": "data/labor_arabic_legal_llm/labor_law_legal_llm_001_245.json"},
                    "english": {"status": "complete", "governing": False, "role": "reference_guidance_only",
                                "record_count": labor_en_count,
                                "data_path": "data/english_reference/labor_law/"},
                },
                "record_counts": {"arabic_articles": labor_law_llm["record_count"],
                                  "english_articles": labor_en_count,
                                  "total": labor_law_llm["record_count"]},
                "data_paths": [
                    "sources/labor/law/official_source/labor_law_official_source.json",
                    "sources/labor/law/verified/labor_law_verified_records.jsonl",
                    "data/labor_arabic_legal_llm/labor_law_legal_llm_001_245.json",
                ],
                "validator_targets": ["make labor-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Labor Law M/51 dated 23/8/1426H, official HRSD consolidated text (amendments through M/44 merged): 249 records = 245 articles + 4 مكرر, of which 38 are officially deleted (flagged, placeholder as printed). Cross-verified against the repository's independently captured BOE base texts: 142 verbatim matches, 65 differ exactly where amendment tracking says amended, ZERO unexplained differences. English (234 records) is reference/guidance only. Arabic governs.",
            },
            {
                "track_id": "labor_implementing_regulation",
                "display_name_ar": "اللائحة التنفيذية لنظام العمل",
                "display_name_en": "Labor Law Implementing Regulation",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "HRSD_OFFICIAL_PDF_OCR_CROSS_CHECKED_LAW_QUOTES",
                "source_authority": "Ministry of Human Resources and Social Development / وزارة الموارد البشرية والتنمية الاجتماعية",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": labor_reg_llm["record_count"],
                    "data_path": "data/labor_arabic_legal_llm/labor_regulation_legal_llm_001_040.json"}},
                "record_counts": {"arabic_articles": labor_reg_llm["record_count"],
                                  "total": labor_reg_llm["record_count"]},
                "data_paths": [
                    "sources/labor/regulation/official_source/labor_regulation_official_source.json",
                    "sources/labor/regulation/verified/labor_regulation_verified_records.jsonl",
                    "data/labor_arabic_legal_llm/labor_regulation_legal_llm_001_040.json",
                ],
                "validator_targets": ["make labor-regulation-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "is_general": False,
                               "is_specialized": False, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Labor Law Implementing Regulation core text (45 records: articles 1-40 + 5 مكرر; 3 officially deleted flagged), extracted from the official HRSD PDF and verified two ways: rendered-page OCR (all active articles >= 0.91) and the PDF's own verbatim Labor Law quotes cross-checked against the verified labor_law track (45 quotes, all >= 0.95, 39 exact) — corroborating both tracks. Each record links to the law articles it implements (implements_law_articles). Annex 1 is ingested as its own track (labor_model_work_regulation); annexes 2-5 are committed but NOT ingested (candidates for follow-up tracks). Arabic governs.",
            },
            {
                "track_id": "labor_model_work_regulation",
                "display_name_ar": "النموذج الموحد للائحة تنظيم العمل",
                "display_name_en": "Unified Model Work Organization Regulation (Labor Annex 1)",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "HRSD_OFFICIAL_PDF_OCR_IMAGE_CROSS_CHECKED",
                "source_authority": "Ministry of Human Resources and Social Development / وزارة الموارد البشرية والتنمية الاجتماعية",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": labor_annex1_llm["record_count"] + labor_annex1_tab["record_count"],
                    "data_path": "data/labor_arabic_legal_llm/labor_annex1_legal_llm_001_072.json"}},
                "record_counts": {"arabic_articles": labor_annex1_llm["record_count"],
                                  "violation_tables": labor_annex1_tab["record_count"],
                                  "total": labor_annex1_llm["record_count"] + labor_annex1_tab["record_count"]},
                "data_paths": [
                    "sources/labor/annex1/official_source/labor_annex1_official_source.json",
                    "sources/labor/annex1/verified/labor_annex1_verified_records.jsonl",
                    "data/labor_arabic_legal_llm/labor_annex1_legal_llm_001_072.json",
                    "data/labor_arabic_legal_llm/labor_annex1_violation_tables_llm.json",
                ],
                "validator_targets": ["make labor-annex1-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "is_general": False,
                               "is_specialized": False, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "The Ministry's model work-organization bylaw (annex 1 of the Labor implementing regulation, adopted by its article (3)): 72 articles (complete 1-72, all active, 27 section headings, OCR >= 0.93) + the 3 violation/penalty tables (50 rows; every cell checked against the rendered page images; table text is a mechanical linearization with every cell verbatim). Arabic governs.",
            },
            {
                "track_id": "labor_saudization_mediation_rules",
                "display_name_ar": "ضوابط وقواعد ممارسة نشاط التوسط في توظيف السعوديين",
                "display_name_en": "Saudi-Employment Mediation Rules (Labor Annex 3)",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "HRSD_OFFICIAL_PDF_OCR_CROSS_CHECKED",
                "source_authority": "Ministry of Human Resources and Social Development / وزارة الموارد البشرية والتنمية الاجتماعية",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": labor_annex3_llm["record_count"],
                    "data_path": "data/labor_arabic_legal_llm/labor_annex3_legal_llm_001_020.json"}},
                "record_counts": {"arabic_articles": labor_annex3_llm["record_count"],
                                  "total": labor_annex3_llm["record_count"]},
                "data_paths": [
                    "sources/labor/annex3/official_source/labor_annex3_official_source.json",
                    "sources/labor/annex3/verified/labor_annex3_verified_records.jsonl",
                    "data/labor_arabic_legal_llm/labor_annex3_legal_llm_001_020.json",
                ],
                "validator_targets": ["make labor-annex34-tracks-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "is_general": False,
                               "is_specialized": False, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Annex 3 of the Labor implementing regulation: rules for licensing and practicing Saudi-employment mediation (20 articles in 4 chapters, complete 1-20, all active, OCR >= 0.97). Arabic governs.",
            },
            {
                "track_id": "labor_recruitment_services_rules",
                "display_name_ar": "قواعد ممارسة نشاط الاستقدام وتقديم الخدمات العمالية",
                "display_name_en": "Recruitment and Labor-Services Rules (Labor Annex 4)",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "HRSD_OFFICIAL_PDF_OCR_CROSS_CHECKED",
                "source_authority": "Ministry of Human Resources and Social Development / وزارة الموارد البشرية والتنمية الاجتماعية",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": labor_annex4_llm["record_count"],
                    "data_path": "data/labor_arabic_legal_llm/labor_annex4_legal_llm_001_072.json"}},
                "record_counts": {"arabic_articles": labor_annex4_llm["record_count"],
                                  "total": labor_annex4_llm["record_count"]},
                "data_paths": [
                    "sources/labor/annex4/official_source/labor_annex4_official_source.json",
                    "sources/labor/annex4/verified/labor_annex4_verified_records.jsonl",
                    "data/labor_arabic_legal_llm/labor_annex4_legal_llm_001_072.json",
                ],
                "validator_targets": ["make labor-annex34-tracks-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "is_general": False,
                               "is_specialized": False, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Annex 4 of the Labor implementing regulation: rules for licensing recruitment companies and labor services (72 articles in 7 chapters/10 sub-sections, complete 1-72, all active, OCR >= 0.92; printed latin bullet glyphs and the printed 'Enterprise resource planning (ERP)' phrase kept verbatim and whitelisted). Arabic governs.",
            },
            {
                "track_id": "labor_accessibility_arrangements",
                "display_name_ar": "جدول الترتيبات والخدمات التيسيرية في بيئة العمل للعمال ذوي الإعاقة",
                "display_name_en": "Workplace Accessibility Arrangements Tables (Labor Annex 2)",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "HRSD_OFFICIAL_PDF_ACTUALTEXT_OCR_IMAGE_CROSS_CHECKED",
                "source_authority": "Ministry of Human Resources and Social Development / وزارة الموارد البشرية والتنمية الاجتماعية",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": labor_annex2_llm["record_count"],
                    "data_path": "data/labor_arabic_legal_llm/labor_annex2_accessibility_tables_llm.json"}},
                "record_counts": {"accessibility_tables": labor_annex2_llm["record_count"],
                                  "table_rows": 40,
                                  "total": labor_annex2_llm["record_count"]},
                "data_paths": [
                    "sources/labor/annex2/official_source/labor_annex2_official_source.json",
                    "sources/labor/annex2/verified/labor_annex2_verified_records.jsonl",
                    "data/labor_arabic_legal_llm/labor_annex2_accessibility_tables_llm.json",
                ],
                "validator_targets": ["make labor-annex2-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "is_general": False,
                               "is_specialized": False, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Annex 2 of the Labor implementing regulation: 8 accessibility-arrangements tables (40 rows across 6 disability sections). The table pages are raster images; text recovered from the PDF's own structure-tree /ActualText, grid rebuilt from ruling rectangles, every row verified against OCR and the rendered page images; table records are mechanical linearizations with every cell verbatim. Printed typesetting defects kept as printed and documented. Arabic governs.",
            },
            {
                "track_id": "labor_model_contract_forms",
                "display_name_ar": "النماذج الموحدة لعقد العمل بأنواعه",
                "display_name_en": "Unified Model Employment Contract Forms (Labor Annex 5)",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "HRSD_OFFICIAL_PDF_OCR_IMAGE_CROSS_CHECKED_BILINGUAL_FORM",
                "source_authority": "Ministry of Human Resources and Social Development / وزارة الموارد البشرية والتنمية الاجتماعية",
                "language_layers": {
                    "arabic": {"status": "complete", "governing": True,
                               "record_count": labor_annex5_llm["record_count"],
                               "data_path": "data/labor_arabic_legal_llm/labor_annex5_contract_forms_llm.json"},
                    "english": {"status": "embedded", "governing": False, "role": "reference_guidance_only",
                                "note": "The permanent contract form is officially bilingual; its printed English column is embedded verbatim in the records as text_en_reference (non-governing, not our translation, not counted as separate reference records)."},
                },
                "record_counts": {"form_units": labor_annex5_llm["record_count"] - 1,
                                  "glossary_tables": 1,
                                  "total": labor_annex5_llm["record_count"]},
                "data_paths": [
                    "sources/labor/annex5/official_source/labor_annex5_official_source.json",
                    "sources/labor/annex5/verified/labor_annex5_verified_records.jsonl",
                    "data/labor_arabic_legal_llm/labor_annex5_contract_forms_llm.json",
                ],
                "validator_targets": ["make labor-annex5-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "is_general": False,
                               "is_specialized": False, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Annex 5 of the Labor implementing regulation: the four unified model employment contract forms — permanent (bilingual, 17 units + 8-row bilingual glossary), part-time (30), casual/temporary (25), seasonal (29) = 102 records. Language columns separated by coordinates (zero latin in governing Arabic); every unit OCR- or image-verified with the method recorded per unit; fill-in blanks and printed misprints kept verbatim and documented. Arabic governs.",
            },
            {
                "track_id": "evidence_law",
                "display_name_ar": "نظام الإثبات",
                "display_name_en": "Saudi Evidence Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": evidence_law_llm["record_count"],
                    "data_path": "data/evidence_arabic_legal_llm/evidence_law_legal_llm_001_129.json"}},
                "record_counts": {"arabic_articles": evidence_law_llm["record_count"],
                                  "total": evidence_law_llm["record_count"]},
                "data_paths": [
                    "sources/evidence/law/official_source/evidence_law_official_source.json",
                    "sources/evidence/law/verified/evidence_law_verified_records.jsonl",
                    "data/evidence_arabic_legal_llm/evidence_law_legal_llm_001_129.json",
                ],
                "validator_targets": ["make evidence-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Evidence Law M/43 dated 26/5/1443H (129 articles in 11 chapters incl. الدليل الرقمي), unamended (every article 'اصلية'). All articles fetched from the official MOJ legal-portal database and cross-verified against the official MOJ PDF from the same portal (min similarity 0.90, mean 0.995, zero unexplained differences; PDF committed with recorded sha256). Arabic governs.",
            },
            {
                "track_id": "evidence_electronic_procedures_rules",
                "display_name_ar": "ضوابط إجراءات الإثبات إلكترونياً",
                "display_name_en": "Controls of the Electronic Evidentiary Procedures",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (decision 921, 16/03/1444H; official legal portal)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": evidence_elec_llm["record_count"],
                    "data_path": "data/evidence_arabic_legal_llm/evidence_electronic_rules_legal_llm_001_024.json"}},
                "record_counts": {"arabic_articles": evidence_elec_llm["record_count"],
                                  "total": evidence_elec_llm["record_count"]},
                "data_paths": [
                    "sources/evidence/electronic_rules/official_source/evidence_electronic_rules_official_source.json",
                    "sources/evidence/electronic_rules/verified/evidence_electronic_rules_verified_records.jsonl",
                    "data/evidence_arabic_legal_llm/evidence_electronic_rules_legal_llm_001_024.json",
                ],
                "validator_targets": ["make evidence-companions-tracks-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "is_general": False,
                               "is_specialized": False, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Controls of the electronic evidentiary procedures (24 articles in 7 chapters), MoJ decision 921 of 1444H, unamended. Fetched from the official MOJ portal database and cross-verified against the official MOJ PDF (min 0.98). Arabic governs.",
            },
            {
                "track_id": "evidence_procedural_manuals",
                "display_name_ar": "الأدلة الإجرائية لنظام الإثبات",
                "display_name_en": "Procedural Manuals for the Evidence Law",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (decision 921, 16/03/1444H; official legal portal)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": evidence_manuals_llm["record_count"],
                    "data_path": "data/evidence_arabic_legal_llm/evidence_procedural_manuals_legal_llm_001_135.json"}},
                "record_counts": {"arabic_articles": evidence_manuals_llm["record_count"],
                                  "total": evidence_manuals_llm["record_count"]},
                "data_paths": [
                    "sources/evidence/procedural_manuals/official_source/evidence_procedural_manuals_official_source.json",
                    "sources/evidence/procedural_manuals/verified/evidence_procedural_manuals_verified_records.jsonl",
                    "data/evidence_arabic_legal_llm/evidence_procedural_manuals_legal_llm_001_135.json",
                ],
                "validator_targets": ["make evidence-companions-tracks-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "is_general": False,
                               "is_specialized": False, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Procedural manuals for the Evidence Law (135 articles in 13 chapters), MoJ decision 921 of 1444H, unamended. Fetched from the official MOJ portal database and cross-verified against the official MOJ PDF (min 0.94). One source typo documented: position 132's printed label omits 'بعد المائة' in both the database and the PDF (kept verbatim, keyed by document order). Arabic governs.",
            },
            {
                "track_id": "evidence_expertise_rules",
                "display_name_ar": "القواعد الخاصة بتنظيم شؤون الخبرة أمام المحاكم",
                "display_name_en": "Rules Regulating Expert Affairs Before the Courts",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (decision 921, 16/03/1444H; official legal portal)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": evidence_expert_llm["record_count"],
                    "data_path": "data/evidence_arabic_legal_llm/evidence_expertise_rules_legal_llm_001_034.json"}},
                "record_counts": {"arabic_articles": evidence_expert_llm["record_count"],
                                  "total": evidence_expert_llm["record_count"]},
                "data_paths": [
                    "sources/evidence/expertise_rules/official_source/evidence_expertise_rules_official_source.json",
                    "sources/evidence/expertise_rules/verified/evidence_expertise_rules_verified_records.jsonl",
                    "data/evidence_arabic_legal_llm/evidence_expertise_rules_legal_llm_001_034.json",
                ],
                "validator_targets": ["make evidence-companions-tracks-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "is_general": False,
                               "is_specialized": False, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Rules regulating expert affairs before the courts (34 articles in 7 chapters), MoJ decision 921 of 1444H, unamended. Fetched from the official MOJ portal database and cross-verified against the official MOJ PDF (min 0.91). Arabic governs.",
            },
            {
                "track_id": "personal_status_law",
                "display_name_ar": "نظام الأحوال الشخصية",
                "display_name_en": "Saudi Personal Status Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": ps_law_llm["record_count"],
                    "data_path": "data/personal_status_arabic_legal_llm/personal_status_law_legal_llm_001_252.json"}},
                "record_counts": {"arabic_articles": ps_law_llm["record_count"],
                                  "total": ps_law_llm["record_count"]},
                "data_paths": [
                    "sources/personal_status/law/official_source/personal_status_law_official_source.json",
                    "sources/personal_status/law/verified/personal_status_law_verified_records.jsonl",
                    "data/personal_status_arabic_legal_llm/personal_status_law_legal_llm_001_252.json",
                ],
                "validator_targets": ["make personal-status-tracks-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Personal Status Law M/73 dated 6/8/1443H (252 articles in 8 chapters), unamended (every article 'اصلية'). Fetched article-by-article from the official MOJ legal-portal database and cross-verified against the official MOJ PDF (min similarity 0.84, mean 0.995; the 3 sub-0.90 articles were visually adjudicated on the PDF as OCR-channel artifacts — stored text matches the print verbatim). One decorative in-word tatweel removed (art 87); the official 'هـ' fifth-item enumerator tatweel kept. Arabic governs.",
            },
            {
                "track_id": "personal_status_implementing_regulation",
                "display_name_ar": "لائحة نظام الأحوال الشخصية",
                "display_name_en": "Implementing Regulation of the Personal Status Law",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (Supreme Order 59641, 17/8/1446H; official legal portal)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": ps_reg_llm["record_count"],
                    "data_path": "data/personal_status_arabic_legal_llm/personal_status_regulation_legal_llm_001_041.json"}},
                "record_counts": {"arabic_articles": ps_reg_llm["record_count"],
                                  "total": ps_reg_llm["record_count"]},
                "data_paths": [
                    "sources/personal_status/regulation/official_source/personal_status_regulation_official_source.json",
                    "sources/personal_status/regulation/verified/personal_status_regulation_verified_records.jsonl",
                    "data/personal_status_arabic_legal_llm/personal_status_regulation_legal_llm_001_041.json",
                ],
                "validator_targets": ["make personal-status-tracks-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "is_general": False,
                               "is_specialized": False, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Implementing Regulation of the Personal Status Law (41 articles), Supreme Order 59641 of 1446H, unamended. Fetched from the official MOJ portal database and cross-verified against the official MOJ PDF (min 0.95, mean 0.998). Arabic governs.",
            },
            {
                "track_id": "sharia_procedure_law",
                "display_name_ar": "نظام المرافعات الشرعية",
                "display_name_en": "Law of Sharia Procedure",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": sharia_proc_law_llm["record_count"],
                    "data_path": "data/sharia_procedure_arabic_legal_llm/sharia_procedure_law_legal_llm_001_243.json"}},
                "record_counts": {"arabic_articles": sharia_proc_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 153, "معدلة": 14, "ملغاة": 75, "مضافة": 1},
                                  "total": sharia_proc_law_llm["record_count"]},
                "data_paths": [
                    "sources/sharia_procedure/law/official_source/sharia_procedure_law_official_source.json",
                    "sources/sharia_procedure/law/verified/sharia_procedure_law_verified_records.jsonl",
                    "data/sharia_procedure_arabic_legal_llm/sharia_procedure_law_legal_llm_001_243.json",
                ],
                "validator_targets": ["make sharia-procedure-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Law of Sharia Procedure M/1 dated 22/1/1435H (243 records: complete 1..242 + المادة (224) مكرر). This is a CONSOLIDATED AMENDED law: 153 اصلية / 14 معدلة / 75 ملغاة / 1 مضافة. Repealed articles keep their full text and are flagged (is_repealed), not deleted — mirroring the official MOJ PDF, which retains repealed bodies with status badges. Each record carries legal_status_ar plus is_repealed/is_amended/is_added flags. Fetched article-by-article from the official MOJ legal-portal database and cross-verified against the official MOJ PDF from the same portal (every article MATCHES_PDF >= 0.90, min 0.92; PDF committed with recorded sha256). Decorative in-word tatweel removed; the official 'هـ' enumerator/Hijri-date abbreviation and space-bounded enumerator dashes kept; art 61 printed label typo kept verbatim. Arabic governs; not legal advice.",
            },
            {
                "track_id": "sharia_procedure_implementing_regulation",
                "display_name_ar": "اللائحة التنفيذية لنظام المرافعات الشرعية",
                "display_name_en": "Implementing Regulation of the Law of Sharia Procedure",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (Minister of Justice decree 39933, 19/5/1435H; official legal portal)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": sharia_proc_reg_llm["record_count"],
                    "data_path": "data/sharia_procedure_arabic_legal_llm/sharia_procedure_regulation_legal_llm_001_637.json"}},
                "record_counts": {"arabic_articles": sharia_proc_reg_llm["record_count"],
                                  "pdf_document_status_breakdown": {"اصلية": 536, "معدلة": 17, "ملغاة": 63, "مضافة": 21},
                                  "portal_legal_status_breakdown": {"اصلية": 388, "معدلة": 16, "ملغاة": 212, "مضافة": 21},
                                  "superseded_by_evidence_law": 149,
                                  "total": sharia_proc_reg_llm["record_count"]},
                "data_paths": [
                    "sources/sharia_procedure/regulation/official_source/sharia_procedure_regulation_official_source.json",
                    "sources/sharia_procedure/regulation/verified/sharia_procedure_regulation_verified_records.jsonl",
                    "data/sharia_procedure_arabic_legal_llm/sharia_procedure_regulation_legal_llm_001_637.json",
                ],
                "validator_targets": ["make sharia-procedure-regulation-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "is_general": False,
                               "is_specialized": False, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Implementing Regulation of the Law of Sharia Procedure (Minister of Justice decree 39933, 19/5/1435H), 637 records (639 portal nodes fetched; 2 exact redundancies — labels ١/٢٣٢ and ١٢/٢٢٨ — removed to match the official PDF, which prints each once, verified on pages 56/58). CONSOLIDATED AMENDED, DUAL-STATUS model: every provision carries pdf_document_status_ar (the badge the official PDF prints — the governing anchor: 536 اصلية / 17 معدلة / 63 ملغاة / 21 مضافة) AND portal_legal_status_ar (the MOJ portal's live legal database: 388 اصلية / 16 معدلة / 212 ملغاة / 21 مضافة). The portal additionally marks 149 provisions ملغاة — the evidence chapters (الوقائع/الاستجواب/الإقرار/اليمين/الشهادة/القرائن/الخبرة) and the cassation/reconsideration chapters — because the standalone Law of Evidence (نظام الإثبات م/43) superseded them; those carry is_superseded=True + superseded_by_ar and are marked in the retrieval title so an LLM never presents them as current. Both statuses recorded, neither hidden. Repealed provisions keep full text and are flagged, not deleted. Fetched provision-by-provision from the MOJ portal database and cross-verified against the official MOJ PDF (633/639 outright; 6 flagged provisions visually adjudicated: 5 digit-in-parenthetical artifacts + 1 معدلة body preferred from the PDF; PDF committed with recorded sha256). Arabic governs; not legal advice.",
            },
            {
                "track_id": "criminal_procedure_law",
                "display_name_ar": "نظام الإجراءات الجزائية",
                "display_name_en": "Law of Criminal Procedure",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": crim_proc_law_llm["record_count"],
                    "data_path": "data/criminal_procedure_arabic_legal_llm/criminal_procedure_law_legal_llm_001_222.json"}},
                "record_counts": {"arabic_articles": crim_proc_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 219, "معدلة": 3, "ملغاة": 0, "مضافة": 0},
                                  "total": crim_proc_law_llm["record_count"]},
                "data_paths": [
                    "sources/criminal_procedure/law/official_source/criminal_procedure_law_official_source.json",
                    "sources/criminal_procedure/law/verified/criminal_procedure_law_verified_records.jsonl",
                    "data/criminal_procedure_arabic_legal_llm/criminal_procedure_law_legal_llm_001_222.json",
                ],
                "validator_targets": ["make criminal-procedure-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Law of Criminal Procedure M/2 dated 22/1/1435H (222 records: complete 1..222, no مكرر). In force; replaces the former Law of Criminal Procedure (M/39, 1422H) per its Article 221. CONSOLIDATED AMENDED but lightly: 219 اصلية / 3 معدلة (arts 25 by M/28, 112 by M/125, 218 by M/43 1443H) / 0 ملغاة / 0 مضافة; each amended article carries its history and its current amended body matches the PDF. The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database and cross-verified against the official MOJ PDF from the same portal (220/222 outright, mean 0.994; the 2 flagged — art 210 spelled-out cross-references, art 222 the one-line 'effective on publication' article — visually adjudicated verbatim on pages 24/26; PDF committed with recorded sha256). Decorative in-word tatweel removed; the 'هـ' Hijri-date abbreviation and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "criminal_procedure_implementing_regulation",
                "display_name_ar": "اللائحة التنفيذية لنظام الإجراءات الجزائية",
                "display_name_en": "Implementing Regulation of the Law of Criminal Procedure",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (Cabinet decision 142, 21/3/1436H; official legal portal)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": crim_proc_reg_llm["record_count"],
                    "data_path": "data/criminal_procedure_arabic_legal_llm/criminal_procedure_regulation_legal_llm_001_181.json"}},
                "record_counts": {"arabic_articles": crim_proc_reg_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 174, "معدلة": 7, "ملغاة": 0, "مضافة": 0},
                                  "total": crim_proc_reg_llm["record_count"]},
                "data_paths": [
                    "sources/criminal_procedure/regulation/official_source/criminal_procedure_regulation_official_source.json",
                    "sources/criminal_procedure/regulation/verified/criminal_procedure_regulation_verified_records.jsonl",
                    "data/criminal_procedure_arabic_legal_llm/criminal_procedure_regulation_legal_llm_001_181.json",
                ],
                "validator_targets": ["make criminal-procedure-regulation-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "is_general": False,
                               "is_specialized": False, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Implementing Regulation of the Law of Criminal Procedure (Cabinet decision 142, 21/3/1436H), 181 records (complete 1..181, sequential ordinal labels, no مكرر). In force. CONSOLIDATED AMENDED but lightly: 174 اصلية / 7 معدلة (arts 21, 71, 92, 93, 157, 163, 179, by Cabinet decision 860) / 0 ملغاة / 0 مضافة; each amended article carries its history and its current amended body matches the PDF. The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database and cross-verified against the official MOJ PDF from the same portal (178/181 outright, mean 0.993; the 3 flagged — arts 57, 164 with in-word decorative tatweel, art 181 the one-line effective-in-30-days closing article — visually adjudicated verbatim on pages 8/22/24; PDF committed with recorded sha256). Decorative in-word tatweel removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "enforcement_law",
                "display_name_ar": "نظام التنفيذ",
                "display_name_en": "Law of Enforcement",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": enforcement_law_llm["record_count"],
                    "data_path": "data/enforcement_arabic_legal_llm/enforcement_law_legal_llm_001_098.json"}},
                "record_counts": {"arabic_articles": enforcement_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 94, "معدلة": 3, "ملغاة": 1, "مضافة": 0},
                                  "total": enforcement_law_llm["record_count"]},
                "data_paths": [
                    "sources/enforcement/law/official_source/enforcement_law_official_source.json",
                    "sources/enforcement/law/verified/enforcement_law_verified_records.jsonl",
                    "data/enforcement_arabic_legal_llm/enforcement_law_legal_llm_001_098.json",
                ],
                "validator_targets": ["make enforcement-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Law of Enforcement M/53 dated 13/8/1433H (98 records: complete 1..98, no مكرر). In force; per its Article 96 it repeals articles 196-232 of the former Law of Sharia Procedure (M/21) and paragraph (z) of Article 13 of the Board of Grievances Law (M/78). CONSOLIDATED AMENDED but lightly: 94 اصلية / 3 معدلة (arts 46, 74, 90, by M/52) / 1 ملغاة (art 75) / 0 مضافة. The repealed article keeps its full text and is FLAGGED, not deleted (the official PDF retains its body with a ملغاة badge); the LLM title gets a '(ملغاة)' suffix so retrieval never presents it as in force. Each non-original article carries its amendment history. The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database and cross-verified against the official MOJ PDF from the same portal (97/98 outright, mean 0.992; the 1 flagged — art 98, the one-line 'effective 180 days after publication' closing article — visually adjudicated verbatim on page 13; PDF committed with recorded sha256). Decorative in-word tatweel removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "enforcement_implementing_regulation",
                "display_name_ar": "اللائحة التنفيذية لنظام التنفيذ",
                "display_name_en": "Implementing Regulation of the Law of Enforcement",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (Minister of Justice decision 526, 20/2/1439H; official legal portal)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": enforcement_reg_llm["record_count"],
                    "data_path": "data/enforcement_arabic_legal_llm/enforcement_regulation_legal_llm_001_273.json"}},
                "record_counts": {"arabic_articles": enforcement_reg_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 266, "معدلة": 2, "ملغاة": 2, "مضافة": 3},
                                  "total": enforcement_reg_llm["record_count"]},
                "data_paths": [
                    "sources/enforcement/regulation/official_source/enforcement_regulation_official_source.json",
                    "sources/enforcement/regulation/verified/enforcement_regulation_verified_records.jsonl",
                    "data/enforcement_arabic_legal_llm/enforcement_regulation_legal_llm_001_273.json",
                ],
                "validator_targets": ["make enforcement-regulation-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "is_general": False,
                               "is_specialized": False, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Implementing Regulation of the Law of Enforcement (Minister of Justice decision 526, 20/2/1439H), 273 records (clause-labeled X/Y, keyed by document order 1..273). In force. CONSOLIDATED AMENDED but lightly (by decision 7207): 266 اصلية / 2 معدلة (٧/٦, ٢/٨٣) / 2 ملغاة (٥/٤٦, ١/٧٥) / 3 مضافة (٣/٨٣, ٤/٨٣, ٣/٨٤). The repealed provisions keep their full text and are FLAGGED, not deleted (the official PDF retains their bodies with ملغاة badges, verified on page 14); the LLM title gets a '(ملغاة)' suffix so retrieval never presents them as in force. Unlike the Sharia Procedure regulation there is NO dual-status divergence — the section-API status equals the statuteStructure/PDF status for every provision — and there are no duplicate labels or exact redundancies. Fetched provision-by-provision from the official MOJ legal-portal database and cross-verified against the official MOJ PDF from the same portal (272/273 outright, mean 0.997; the 1 flagged — clause ١/٤٢, a short clause carrying digit cross-references (١/٣٢)/(٢/٣٢) — visually adjudicated verbatim on page 13; PDF committed with recorded sha256). Decorative in-word tatweel removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "judiciary_law",
                "display_name_ar": "نظام القضاء",
                "display_name_en": "Law of the Judiciary",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": judiciary_law_llm["record_count"],
                    "data_path": "data/judiciary_arabic_legal_llm/judiciary_law_legal_llm_001_085.json"}},
                "record_counts": {"arabic_articles": judiciary_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 82, "معدلة": 3, "ملغاة": 0, "مضافة": 0},
                                  "total": judiciary_law_llm["record_count"]},
                "data_paths": [
                    "sources/judiciary/law/official_source/judiciary_law_official_source.json",
                    "sources/judiciary/law/verified/judiciary_law_verified_records.jsonl",
                    "data/judiciary_arabic_legal_llm/judiciary_law_legal_llm_001_085.json",
                ],
                "validator_targets": ["make judiciary-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Law of the Judiciary M/78 dated 19/9/1428H (85 records: complete 1..85, no مكرر). The FOUNDATIONAL court-organization statute — its Article 9 defines the court structure (المحكمة العليا, محاكم الاستئناف, and five first-degree courts: العامة/الجزائية/الأحوال الشخصية/التجارية/العمالية) and the المجلس الأعلى للقضاء referenced throughout the procedure and enforcement laws. In force; per its Article 85 it replaces the former Law of the Judiciary (M/64, 14/7/1395H). CONSOLIDATED AMENDED but lightly: 82 اصلية / 3 معدلة (arts 5, 35, 72, by M/95) / 0 ملغاة / 0 مضافة; each amended article carries its history and its current amended body matches the PDF. The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database and cross-verified against the official MOJ PDF from the same portal (82/85 outright, mean 0.990; the 3 flagged — art 9 the court-structure enumeration, art 71 numbered dash clauses, art 85 the one-line closing article — visually adjudicated verbatim on pages 2/11/14; PDF committed with recorded sha256). No decorative in-word tatweel present (all tatweel are the هـ enumerator or space-bounded enumerator dashes, kept). Arabic governs; not legal advice.",
            },
            {
                "track_id": "board_of_grievances_law",
                "display_name_ar": "نظام ديوان المظالم",
                "display_name_en": "Law of the Board of Grievances",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "BOARD_OFFICIAL_PDF_VISUALLY_ADJUDICATED_GAZETTE_CONFIRMED",
                "source_authority": "Board of Grievances / ديوان المظالم (certified official PDF, bog.gov.sa; corroborated by WIPO Lex) + Umm Al-Qura gazette (SPA-confirmed amendment)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": bog_law_llm["record_count"],
                    "data_path": "data/board_of_grievances_arabic_legal_llm/board_of_grievances_law_legal_llm_001_026.json"}},
                "record_counts": {"arabic_articles": bog_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 25, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
                                  "total": bog_law_llm["record_count"]},
                "data_paths": [
                    "sources/board_of_grievances/law/official_source/board_of_grievances_law_official_source.json",
                    "sources/board_of_grievances/law/verified/board_of_grievances_law_verified_records.jsonl",
                    "data/board_of_grievances_arabic_legal_llm/board_of_grievances_law_legal_llm_001_026.json",
                ],
                "validator_targets": ["make board-of-grievances-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Law of the Board of Grievances M/78 dated 19/9/1428H (26 records: complete 1..26, no مكرر) — the administrative-judiciary statute (قضاء إداري مستقل يرتبط مباشرة بالملك) organizing the المحكمة الإدارية العليا / محاكم الاستئناف الإدارية / المحاكم الإدارية and مجلس القضاء الإداري; issued together with the Law of the Judiciary under the same decree and per its Article 26 replaces the former Board Law (M/51, 17/7/1402H). The Board sits under a SEPARATE authority and is NOT on the MOJ legal portal, and the BOE consolidated database (laws.boe.gov.sa) is network-unreachable, so this track was sourced via the user-approved Board + gazette route: text taken from the Board's official machine-readable DOCX and adjudicated VISUALLY page-by-page against the Board's certified official PDF (صورة طبق الأصل / هيئة الخبراء; committed with recorded sha256; corroborated by WIPO Lex holding the same scan). CONSOLIDATED AMENDED, minimally: 25 اصلية (double-official, visual adjudication, sim 1.0) / exactly 1 معدلة / 0 ملغاة / 0 مضافة. The sole amended article is Article 4 (composition of مجلس القضاء الإداري), amended by قرار مجلس الوزراء 594 / المرسوم الملكي م/180 (17/8/1446H) published in Umm Al-Qura issue 5072 (21 Feb 2025), adding a fifth member category (عضوان من ذوي الخبرة والاختصاص) and a 4-year renewable royal-order tenure for items 4 and 5; it carries both its current amended body and its original 1428 body in amendment_history. The amendment SCOPE (Article 4 only) and SUBSTANCE are officially confirmed by the SPA Council-of-Ministers announcement; its verbatim wording is from a secondary rendering of gazette 5072 (BOE unreachable) and is flagged at a slightly lower verbatim-trust tier in the source artifact. Decorative in-word tatweel removed; the هـ enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "law_practice_law",
                "display_name_ar": "نظام المحاماة",
                "display_name_en": "Code of Law Practice",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": law_practice_law_llm["record_count"],
                    "data_path": "data/law_practice_arabic_legal_llm/law_practice_law_legal_llm_001_056.json"}},
                "record_counts": {"arabic_articles": law_practice_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 35, "معدلة": 8, "ملغاة": 1, "مضافة": 12},
                                  "total": law_practice_law_llm["record_count"]},
                "data_paths": [
                    "sources/law_practice/law/official_source/law_practice_law_official_source.json",
                    "sources/law_practice/law/verified/law_practice_law_verified_records.jsonl",
                    "data/law_practice_arabic_legal_llm/law_practice_law_legal_llm_001_056.json",
                ],
                "validator_targets": ["make law-practice-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Code of Law Practice M/38 dated 28/7/1422H (56 records: complete 1..55 plus one مكرر — art 21-mukarrar). Regulates the legal profession: قيد المحامين, واجباتهم وحقوقهم, تأديب المحامي, and (new) تنظيم الترخيص لمكتب المحاماة الأجنبي. In force. SUBSTANTIALLY CONSOLIDATED AMENDED: 35 اصلية / 8 معدلة / 12 مضافة / 1 ملغاة (art 25). The amendment history spans decrees M/52, M/61, M/66 (1443H), M/191 and M/21 (1447H); the 12 added articles are chiefly the new chapter on licensing foreign law firms (arts 44-55) plus art 21-mukarrar, and each amended/added/repealed article carries its version history. The single repealed article (25) keeps its full body and is FLAGGED, not deleted (its LLM title gets a '(ملغاة)' suffix so retrieval never presents it as in force). The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (55/56 outright, mean 0.968; the 1 flagged — art 41, معدلة, the foreign-legal-consultant article — visually adjudicated verbatim on page 7; PDF committed with recorded sha256, 9 pages). Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word tatweel removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "law_practice_implementing_regulation",
                "display_name_ar": "اللائحة التنفيذية لنظام المحاماة",
                "display_name_en": "Implementing Regulation of the Code of Law Practice",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": law_practice_reg_llm["record_count"],
                    "data_path": "data/law_practice_arabic_legal_llm/law_practice_regulation_legal_llm_001_090.json"}},
                "record_counts": {"arabic_articles": law_practice_reg_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 90, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
                                  "total": law_practice_reg_llm["record_count"]},
                "data_paths": [
                    "sources/law_practice/regulation/official_source/law_practice_regulation_official_source.json",
                    "sources/law_practice/regulation/verified/law_practice_regulation_verified_records.jsonl",
                    "data/law_practice_arabic_legal_llm/law_practice_regulation_legal_llm_001_090.json",
                ],
                "validator_targets": ["make law-practice-regulation-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Implementing Regulation of the Code of Law Practice — the CURRENT version «اللائحة التنفيذية لنظام المحاماة 1446هـ» (issued 19/4/1446H, legalStatus Active), 90 records (complete 1..90, no مكرر) across 9 chapters (definitions, licensing, professional duties, the trainee, the non-Saudi consultant, non-lawyer authorized pleaders, the foreign law firm, discipline, closing provisions) — the regulation accompanying the Code of Law Practice as consolidated through M/21 (1447H). This is a FRESH full issuance: all 90 articles are اصلية (0 معدلة / 0 ملغاة / 0 مضافة), and it SUPERSEDES the former implementing regulation (Minister of Justice decision 676, 1423H, legalStatus InActive), which is NOT ingested. The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (85/90 outright, mean 0.962; the 5 flagged long/list articles — 1, 3, 19, 60, 62 — visually adjudicated verbatim on the rendered pages; PDF committed with recorded sha256, 17 pages). Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs; one portal ordinal typo (art 13 label «الثاثة عشرة») is preserved verbatim. Decorative in-word tatweel removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "commercial_courts_law",
                "display_name_ar": "نظام المحاكم التجارية",
                "display_name_en": "Commercial Courts Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": commercial_courts_law_llm["record_count"],
                    "data_path": "data/commercial_courts_arabic_legal_llm/commercial_courts_law_legal_llm_001_096.json"}},
                "record_counts": {"arabic_articles": commercial_courts_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 75, "معدلة": 1, "ملغاة": 20, "مضافة": 0},
                                  "total": commercial_courts_law_llm["record_count"]},
                "data_paths": [
                    "sources/commercial_courts/law/official_source/commercial_courts_law_official_source.json",
                    "sources/commercial_courts/law/verified/commercial_courts_law_verified_records.jsonl",
                    "data/commercial_courts_arabic_legal_llm/commercial_courts_law_legal_llm_001_096.json",
                ],
                "validator_targets": ["make commercial-courts-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Commercial Courts Law M/93 dated 15/8/1441H (96 records: complete 1..96, no مكرر) across 11 chapters (general provisions, jurisdiction, filing, hearing, appearance/absence, urgent applications, evidence, judgments, payment orders, objection, closing provisions) — the statute organizing the commercial courts and their procedure. In force. CONSOLIDATED AMENDED: 75 اصلية / 1 معدلة / 20 ملغاة. The 20 repealed articles are the ENTIRE evidence chapter (arts 38-57, contiguous), repealed by the Evidence Law (المرسوم م/43, 1443H) which now governs evidence uniformly (the same supersession seen in the Sharia Procedure regulation); art 16 (jurisdiction) was amended by M/191 (1444H). The repealed articles keep their full bodies and are FLAGGED, not deleted (each carries its م/43 repeal history and its LLM title gets a '(ملغاة)' suffix so retrieval never presents them as in force). The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (93/96 outright, mean 0.958; the 3 flagged numbered-list articles — 28, 62, 81 — visually adjudicated verbatim on the rendered pages; PDF committed with recorded sha256, 18 pages). Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word tatweel removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "commercial_courts_implementing_regulation",
                "display_name_ar": "اللائحة التنفيذية لنظام المحاكم التجارية",
                "display_name_en": "Implementing Regulation of the Commercial Courts Law",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": commercial_courts_reg_llm["record_count"],
                    "data_path": "data/commercial_courts_arabic_legal_llm/commercial_courts_regulation_legal_llm_001_281.json"}},
                "record_counts": {"arabic_articles": commercial_courts_reg_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 281, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
                                  "total": commercial_courts_reg_llm["record_count"]},
                "data_paths": [
                    "sources/commercial_courts/regulation/official_source/commercial_courts_regulation_official_source.json",
                    "sources/commercial_courts/regulation/verified/commercial_courts_regulation_verified_records.jsonl",
                    "data/commercial_courts_arabic_legal_llm/commercial_courts_regulation_legal_llm_001_281.json",
                ],
                "validator_targets": ["make commercial-courts-regulation-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Implementing Regulation of the Commercial Courts Law — the CURRENT version «اللائحة التنفيذية لنظام المحاكم التجارية» (issued 26/10/1441H, legalStatus Active), 281 records (complete 1..281, no مكرر) across 6 chapters (general provisions, hearing procedure, evidence, judgments and payment orders, objection to judgments, special provisions for certain actions — incl. the class-action / الدعوى الجماعية regime). This is a FRESH full issuance: all 281 articles are اصلية (0 معدلة / 0 ملغاة / 0 مضافة). The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). NOTE: the regulation retains its evidence chapter even though the Commercial Courts Law's own evidence articles (38-57) were repealed by the Evidence Law (M/43); the MOJ portal keeps the regulation's provisions اصلية/Active and they are recorded here exactly as the official portal classifies them (no interpretive supersession added). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (273/281 outright, mean 0.957; the 8 flagged numbered-list articles — 3, 41, 55, 90, 144, 155, 255, 267 — visually adjudicated verbatim on the rendered pages; PDF committed with recorded sha256, 34 pages). Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word tatweel removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "bankruptcy_law",
                "display_name_ar": "نظام الإفلاس",
                "display_name_en": "Bankruptcy Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": bankruptcy_law_llm["record_count"],
                    "data_path": "data/bankruptcy_arabic_legal_llm/bankruptcy_law_legal_llm_001_231.json"}},
                "record_counts": {"arabic_articles": bankruptcy_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 229, "معدلة": 2, "ملغاة": 0, "مضافة": 0},
                                  "total": bankruptcy_law_llm["record_count"]},
                "data_paths": [
                    "sources/bankruptcy/law/official_source/bankruptcy_law_official_source.json",
                    "sources/bankruptcy/law/verified/bankruptcy_law_verified_records.jsonl",
                    "data/bankruptcy_arabic_legal_llm/bankruptcy_law_legal_llm_001_231.json",
                ],
                "validator_targets": ["make bankruptcy-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Bankruptcy Law M/89 dated 28/5/1439H (231 records: complete 1..231, no مكرر) across 17 chapters — the foundational insolvency statute governing the bankruptcy procedures (التسوية الوقائية / إعادة التنظيم المالي / التصفية and the small-debtor and administrative variants) that run before the commercial courts. In force. CONSOLIDATED AMENDED: 229 اصلية / 2 معدلة (arts 46, 147) / 0 ملغاة / 0 مضافة; each amended article carries its history. Per its Article 230 the law ITSELF repeals arts 103-137 of the former Commercial Court Law (Royal Order 32, 15/1/1350H) and the former Protective Settlement from Bankruptcy Law (M/16, 4/9/1416H). The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (225/231 outright, mean 0.965; the 6 flagged list/reference articles — 39, 94, 145, 158, 196, 230 — visually adjudicated verbatim on the rendered pages, the 3 lowest read directly; PDF committed with recorded sha256, 38 pages). Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word kashida removed; the 'هـ' enumerator, prefix-letter tatweels before parenthetical figures (لـ/بـ) and list enumerators, and space-bounded enumerator dashes are kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "bankruptcy_implementing_regulation",
                "display_name_ar": "اللائحة التنفيذية لنظام الإفلاس",
                "display_name_en": "Implementing Regulation of the Bankruptcy Law",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": bankruptcy_reg_llm["record_count"],
                    "data_path": "data/bankruptcy_arabic_legal_llm/bankruptcy_regulation_legal_llm_001_098.json"}},
                "record_counts": {"arabic_articles": bankruptcy_reg_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 97, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
                                  "total": bankruptcy_reg_llm["record_count"]},
                "data_paths": [
                    "sources/bankruptcy/regulation/official_source/bankruptcy_regulation_official_source.json",
                    "sources/bankruptcy/regulation/verified/bankruptcy_regulation_verified_records.jsonl",
                    "data/bankruptcy_arabic_legal_llm/bankruptcy_regulation_legal_llm_001_098.json",
                ],
                "validator_targets": ["make bankruptcy-regulation-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Implementing Regulation of the Bankruptcy Law «اللائحة التنفيذية لنظام الإفلاس» — issued by Council of Ministers Decision No. 622 dated 4/1/1440H (legalStatus Active), 98 records (complete 1..98, no مكرر) across 18 chapters: general provisions, common provisions across bankruptcy procedures, the preventive-settlement / financial-reorganization / liquidation procedures and their small-debtor variants, administrative liquidation, set-off and mutual debts, debt priority, security and set-off arrangements for financial transactions, objection to judgments, provisions for a deceased debtor, the Bankruptcy Committee, the Bankruptcy Register, trustees and experts, and closing provisions. CONSOLIDATED AMENDED: 97 اصلية / 1 معدلة (المادة الثانية, amended by Council of Ministers Decision No. 171 dated 20/3/1443H, adding a sub-paragraph to paragraph (1)) / 0 ملغاة / 0 مضافة; the amended article carries its history. The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (98/98 outright, mean 0.968, min 0.913; no article required visual adjudication; PDF committed with recorded sha256, 21 pages). Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "bankruptcy_case_rules",
                "display_name_ar": "القواعد المنظمة لإجراءات قضايا الإفلاس في المحاكم التجارية",
                "display_name_en": "Rules Organizing Bankruptcy Case Procedures before the Commercial Courts",
                "corpus_family": "procedural_rules",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": bankruptcy_rules_llm["record_count"],
                    "data_path": "data/bankruptcy_arabic_legal_llm/bankruptcy_case_rules_legal_llm_001_024.json"}},
                "record_counts": {"arabic_articles": bankruptcy_rules_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 24, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
                                  "total": bankruptcy_rules_llm["record_count"]},
                "data_paths": [
                    "sources/bankruptcy/case_rules/official_source/bankruptcy_case_rules_official_source.json",
                    "sources/bankruptcy/case_rules/verified/bankruptcy_case_rules_verified_records.jsonl",
                    "data/bankruptcy_arabic_legal_llm/bankruptcy_case_rules_legal_llm_001_024.json",
                ],
                "validator_targets": ["make bankruptcy-case-rules-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Rules Organizing Bankruptcy Case Procedures before the Commercial Courts «القواعد المنظمة لإجراءات قضايا الإفلاس في المحاكم التجارية» — issued by Minister of Justice Decision No. 6421 (published 9/4/1441H, legalStatus Active), 24 records (complete 1..24, no مكرر) across 9 chapters: general provisions, jurisdiction, the court unit managing bankruptcy cases, filing and registering the request, examining and deciding the request, stay of claims and precautionary requests, judicial notifications, issuing and objecting to judgments/decisions, and closing provisions. These are the procedural (litigation) rules that govern how bankruptcy cases run before the commercial courts, complementary to the Bankruptcy Law (M/89) and its implementing regulation. FRESH FULL ISSUANCE: all 24 اصلية (0 معدلة / 0 ملغاة / 0 مضافة). The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (24/24 outright, mean 0.960, min 0.912; no article required visual adjudication; PDF committed with recorded sha256, 9 pages). Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "judicial_costs_law",
                "display_name_ar": "نظام التكاليف القضائية",
                "display_name_en": "Judicial Costs Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": judicial_costs_law_llm["record_count"],
                    "data_path": "data/judicial_costs_arabic_legal_llm/judicial_costs_law_legal_llm_001_023.json"}},
                "record_counts": {"arabic_articles": judicial_costs_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 23, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
                                  "total": judicial_costs_law_llm["record_count"]},
                "data_paths": [
                    "sources/judicial_costs/law/official_source/judicial_costs_law_official_source.json",
                    "sources/judicial_costs/law/verified/judicial_costs_law_verified_records.jsonl",
                    "data/judicial_costs_arabic_legal_llm/judicial_costs_law_legal_llm_001_023.json",
                ],
                "validator_targets": ["make judicial-costs-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Judicial Costs Law «نظام التكاليف القضائية» — Royal Decree M/16 dated 10/2/1443H (legalStatus Active), 23 records (complete 1..23, no مكرر) — the statute governing judicial (litigation) costs across the courts: it caps costs at 5% of the claim value (max SAR 1,000,000), sets when costs are due/refunded, the reduction on amicable settlement, and the exempt categories (prisoners, workers under the Labor Law, government bodies). FRESH FULL ISSUANCE: all 23 اصلية (0 معدلة / 0 ملغاة / 0 مضافة). The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (22/23 outright, mean 0.958; the numbered-list article 12 visually adjudicated verbatim on the rendered page; PDF committed with recorded sha256, 4 pages). Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "judicial_costs_implementing_regulation",
                "display_name_ar": "اللائحة التنفيذية لنظام التكاليف القضائية",
                "display_name_en": "Implementing Regulation of the Judicial Costs Law",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": judicial_costs_reg_llm["record_count"],
                    "data_path": "data/judicial_costs_arabic_legal_llm/judicial_costs_regulation_legal_llm_001_017.json"}},
                "record_counts": {"arabic_articles": judicial_costs_reg_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 17, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
                                  "total": judicial_costs_reg_llm["record_count"]},
                "data_paths": [
                    "sources/judicial_costs/regulation/official_source/judicial_costs_regulation_official_source.json",
                    "sources/judicial_costs/regulation/verified/judicial_costs_regulation_verified_records.jsonl",
                    "data/judicial_costs_arabic_legal_llm/judicial_costs_regulation_legal_llm_001_017.json",
                ],
                "validator_targets": ["make judicial-costs-regulation-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Implementing Regulation of the Judicial Costs Law «اللائحة التنفيذية لنظام التكاليف القضائية» — issued by Council of Ministers Decision No. 519 dated 11/9/1443H (legalStatus Active), 17 records (complete 1..17, no مكرر) across 4 chapters: estimating judicial costs (the percentage tiers by claim value and the fixed amounts for value-undetermined actions), estimating costs for requests, the final estimate and how it is collected, and closing provisions. FRESH FULL ISSUANCE: all 17 اصلية (0 معدلة / 0 ملغاة / 0 مضافة). The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (16/17 outright, mean 0.954; the percentage-table article 2 visually adjudicated verbatim on the rendered page; PDF committed with recorded sha256, 5 pages). Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "arbitration_law",
                "display_name_ar": "نظام التحكيم",
                "display_name_en": "Arbitration Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": arbitration_law_llm["record_count"],
                    "data_path": "data/arbitration_arabic_legal_llm/arbitration_law_legal_llm_001_058.json"}},
                "record_counts": {"arabic_articles": arbitration_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 55, "معدلة": 3, "ملغاة": 0, "مضافة": 0},
                                  "total": arbitration_law_llm["record_count"]},
                "data_paths": [
                    "sources/arbitration/law/official_source/arbitration_law_official_source.json",
                    "sources/arbitration/law/verified/arbitration_law_verified_records.jsonl",
                    "data/arbitration_arabic_legal_llm/arbitration_law_legal_llm_001_058.json",
                ],
                "validator_targets": ["make arbitration-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Arbitration Law «نظام التحكيم» — Royal Decree M/34 dated 18/7/1433H (legalStatus Active), 58 records (numbered 1..58 by ordinal position, no مكرر) across 8 chapters (أبواب): general provisions, the arbitration agreement, the arbitral tribunal, arbitration proceedings, the arbitral award, nullity of the award, enforcement of the award, and closing provisions — the governing statute for domestic and international commercial arbitration seated in the Kingdom. CONSOLIDATED AMENDED: 55 اصلية / 3 معدلة (arts 10, 24, 50) / 0 ملغاة / 0 مضافة; each amended article carries its history. Art 24 amended by Royal Decree M/8 (18/1/1443H); arts 10 and 50 amended by Royal Decree M/21 (26/1/1447H). NUMBERING ANOMALY (documented): the official source (BOTH the portal database AND the published PDF) labels the 31st article «المادة الحادية والعشرون» — a duplicate of article 21's label; there is no «الحادية والثلاثون». The official label is preserved verbatim; the ordinal position (31) is used for indexing and a factual positional note is appended to the LLM title. The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (57/58 outright, mean 0.961; the list article 42 visually adjudicated verbatim on the rendered page; PDF committed with recorded sha256, 12 pages). Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "arbitration_implementing_regulation",
                "display_name_ar": "اللائحة التنفيذية لنظام التحكيم",
                "display_name_en": "Implementing Regulation of the Arbitration Law",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": arbitration_reg_llm["record_count"],
                    "data_path": "data/arbitration_arabic_legal_llm/arbitration_regulation_legal_llm_001_019.json"}},
                "record_counts": {"arabic_articles": arbitration_reg_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 18, "معدلة": 0, "ملغاة": 1, "مضافة": 0},
                                  "total": arbitration_reg_llm["record_count"]},
                "data_paths": [
                    "sources/arbitration/regulation/official_source/arbitration_regulation_official_source.json",
                    "sources/arbitration/regulation/verified/arbitration_regulation_verified_records.jsonl",
                    "data/arbitration_arabic_legal_llm/arbitration_regulation_legal_llm_001_019.json",
                ],
                "validator_targets": ["make arbitration-regulation-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Implementing Regulation of the Arbitration Law «اللائحة التنفيذية لنظام التحكيم» — issued by Council of Ministers Decision No. 541 dated 14/9/1438H (legalStatus Active), 19 records (complete 1..19, no مكرر) — defining the competent court, tribunal constitution and appointment of arbitrators by the competent court, notifications, and the interplay with the Law. CONSOLIDATED: 18 اصلية / 0 معدلة / 1 ملغاة (art 7, repealed by Council of Ministers Decision No. 249) / 0 مضافة; the repealed article keeps its body (flagged, not deleted) and carries its history. The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (19/19 outright, mean 0.964; no article required visual adjudication; PDF committed with recorded sha256, 3 pages). Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "commercial_papers_law",
                "display_name_ar": "نظام الأوراق التجارية",
                "display_name_en": "Commercial Papers Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED",
                "source_authority": "Bureau of Experts at the Council of Ministers / هيئة الخبراء بمجلس الوزراء (official legislative portal laws.boe.gov.sa, captured via Wayback archive)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": commercial_papers_law_llm["record_count"],
                    "data_path": "data/commercial_papers_arabic_legal_llm/commercial_papers_law_legal_llm_001_121.json"}},
                "record_counts": {"arabic_articles": commercial_papers_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 118, "معدلة": 3, "ملغاة": 0, "مضافة": 0},
                                  "total": commercial_papers_law_llm["record_count"]},
                "data_paths": [
                    "sources/commercial_papers/law/official_source/commercial_papers_law_official_source.json",
                    "sources/commercial_papers/law/verified/commercial_papers_law_verified_records.jsonl",
                    "data/commercial_papers_arabic_legal_llm/commercial_papers_law_legal_llm_001_121.json",
                ],
                "validator_targets": ["make commercial-papers-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Commercial Papers Law «نظام الأوراق التجارية» — Royal Decree M/37 dated 11/10/1383H (24/2/1964), 121 records (complete 1..121, no مكرر) across 26 chapters/sections covering the bill of exchange (الكمبيالة), the promissory note (السند لأمر), the cheque (الشيك), and the penalties (الجزاءات) — the foundational statute governing negotiable/commercial instruments. IN FORCE (ساري). CONSOLIDATED AMENDED: 118 اصلية / 3 معدلة (arts 118, 119, 120, amended by Royal Decree M/45 dated 12/9/1409H — each carries the current amended text plus its original 1383H text in amendment_history) / 0 ملغاة / 0 مضافة. Article 38 is recorded with its ORIGINAL text (اصلية); an official interpretation of the phrase «لدى الاطلاع» (Council of Ministers Decision No. 251, 23/4/1442H) is preserved in its history — the article text itself was not changed. PROVENANCE (differs from the MOJ double-official pipeline): the MOJ laws-gateway does not host this older law and the BOE portal is not directly reachable from the build environment, so the official BOE text was captured from the Wayback Machine archive of the official BOE LawDetails page and CROSS-VERIFIED across two independent-date snapshots (2021 + 2025) — all 121 current article bodies are byte-identical between them (zero differences). Both raw snapshots are committed under inputs/commercial_papers_boe_snapshots/ with recorded sha256, and the concatenated corpus text carries a recorded sha256. No legal text altered; decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "commercial_register_law",
                "display_name_ar": "نظام السجل التجاري",
                "display_name_en": "Commercial Register Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED",
                "source_authority": "Bureau of Experts at the Council of Ministers / هيئة الخبراء بمجلس الوزراء (official legislative portal laws.boe.gov.sa, captured via Wayback archive)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": commercial_register_law_llm["record_count"],
                    "data_path": "data/commercial_register_arabic_legal_llm/commercial_register_law_legal_llm_001_029.json"}},
                "record_counts": {"arabic_articles": commercial_register_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 29, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
                                  "total": commercial_register_law_llm["record_count"]},
                "data_paths": [
                    "sources/commercial_register/law/official_source/commercial_register_law_official_source.json",
                    "sources/commercial_register/law/verified/commercial_register_law_verified_records.jsonl",
                    "data/commercial_register_arabic_legal_llm/commercial_register_law_legal_llm_001_029.json",
                ],
                "validator_targets": ["make commercial-register-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Commercial Register Law «نظام السجل التجاري» — Royal Decree M/83 dated 19/3/1446H, 29 records (complete 1..29, no مكرر) across 6 chapters: general provisions, entry in the commercial register, cancellation/suspension of entry, access to and evidentiary weight of the registration certificate, violations, and closing provisions. IN FORCE (ساري); a fresh full issuance (all 29 اصلية) superseding the former Commercial Register Law (Royal Decree M/1, 21/2/1416H). PROVENANCE (differs from the MOJ double-official pipeline): the MOJ laws-gateway does not host this law and the BOE portal is not directly reachable from the build environment, so the official BOE text was captured from the Wayback Machine archive of the official BOE LawDetails page and CROSS-VERIFIED across two independent-date snapshots (2025-01 + 2025-04) — all 29 article bodies are byte-identical (zero differences). Both raw snapshots are committed under inputs/commercial_registration_boe_snapshots/ with recorded sha256, and the concatenated corpus text carries a recorded sha256. No legal text altered; decorative in-word kashida removed. Arabic governs; not legal advice.",
            },
            {
                "track_id": "trade_names_law",
                "display_name_ar": "نظام الأسماء التجارية",
                "display_name_en": "Trade Names Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED",
                "source_authority": "Bureau of Experts at the Council of Ministers / هيئة الخبراء بمجلس الوزراء (official legislative portal laws.boe.gov.sa, captured via Wayback archive)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": trade_names_law_llm["record_count"],
                    "data_path": "data/trade_names_arabic_legal_llm/trade_names_law_legal_llm_001_023.json"}},
                "record_counts": {"arabic_articles": trade_names_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 23, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
                                  "total": trade_names_law_llm["record_count"]},
                "data_paths": [
                    "sources/trade_names/law/official_source/trade_names_law_official_source.json",
                    "sources/trade_names/law/verified/trade_names_law_verified_records.jsonl",
                    "data/trade_names_arabic_legal_llm/trade_names_law_legal_llm_001_023.json",
                ],
                "validator_targets": ["make trade-names-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Trade Names Law «نظام الأسماء التجارية» — Royal Decree M/83 dated 19/3/1446H, 23 records (complete 1..23, no مكرر) across 5 chapters: general provisions, provisions on the trade name and its reservation and registration, cancellation/removal and its cases, violations, and closing provisions. IN FORCE (ساري); a fresh full issuance (all 23 اصلية) superseding the former Trade Names Law (Royal Decree M/15, 12/8/1420H). PROVENANCE (differs from the MOJ double-official pipeline): the MOJ laws-gateway does not host this law and the BOE portal is not directly reachable from the build environment, so the official BOE text was captured from the Wayback Machine archive of the official BOE LawDetails page and CROSS-VERIFIED across two independent-date snapshots (2024-11 + 2025-12) — all 23 article bodies are byte-identical (zero differences). Both raw snapshots are committed under inputs/commercial_registration_boe_snapshots/ with recorded sha256, and the concatenated corpus text carries a recorded sha256. No legal text altered; decorative in-word kashida removed. Arabic governs; not legal advice.",
            },
            {
                "track_id": "commercial_agencies_law",
                "display_name_ar": "نظام الوكالات التجارية",
                "display_name_en": "Commercial Agencies Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED",
                "source_authority": "Bureau of Experts at the Council of Ministers / هيئة الخبراء بمجلس الوزراء (official legislative portal laws.boe.gov.sa, captured via Wayback archive)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": commercial_agencies_law_llm["record_count"],
                    "data_path": "data/commercial_agencies_arabic_legal_llm/commercial_agencies_law_legal_llm_001_006.json"}},
                "record_counts": {"arabic_articles": commercial_agencies_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 3, "معدلة": 3, "ملغاة": 0, "مضافة": 0},
                                  "total": commercial_agencies_law_llm["record_count"]},
                "data_paths": [
                    "sources/commercial_agencies/law/official_source/commercial_agencies_law_official_source.json",
                    "sources/commercial_agencies/law/verified/commercial_agencies_law_verified_records.jsonl",
                    "data/commercial_agencies_arabic_legal_llm/commercial_agencies_law_legal_llm_001_006.json",
                ],
                "validator_targets": ["make commercial-agencies-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Commercial Agencies Law «نظام الوكالات التجارية» — Royal Decree M/11 dated 20/2/1382H, 6 records (complete 1..6, no مكرر) — restricting commercial agency to Saudis, the Commercial Agencies Register kept at the Ministry of Commerce, registration fees, and the penalties for violations. IN FORCE (ساري). CONSOLIDATED AMENDED: 3 اصلية / 3 معدلة (arts 4, 5, 6) / 0 ملغاة / 0 مضافة. Art 4 was replaced by Royal Decree M/32 (10/8/1400H) — penalty raised to 5,000-50,000 SAR with publication and administrative liquidation/deportation for non-Saudis; art 5 was replaced by Royal Decree M/8 (20/3/1393H) — registration fee set at 500 SAR for both individuals and companies; each replacement carries the current amended text plus the original in amendment_history. Art 6's own text (the law's effective-date provision) was NOT replaced — Royal Decree M/5 (11/6/1389H) ADDED a penalties-enforcement committee and grievance provisions (recorded in art 6's history as an addition); BOE flags art 6 as amended and its body is recorded exactly as BOE displays it. PROVENANCE (differs from the MOJ double-official pipeline): the MOJ laws-gateway does not host this older law and the BOE portal is not directly reachable from the build environment, so the official BOE text was captured from the Wayback Machine archive of the official BOE LawDetails page and CROSS-VERIFIED across two independent-date snapshots (2023 + 2025) — all 6 current article bodies are byte-identical (zero differences). Both raw snapshots are committed under inputs/commercial_agencies_boe_snapshots/ with recorded sha256, and the concatenated corpus text carries a recorded sha256. No legal text altered; decorative in-word kashida removed. Arabic governs; not legal advice.",
            },
            {
                "track_id": "chambers_of_commerce_law",
                "display_name_ar": "نظام الغرف التجارية",
                "display_name_en": "Chambers of Commerce Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED",
                "source_authority": "Bureau of Experts at the Council of Ministers / هيئة الخبراء بمجلس الوزراء (official legislative portal laws.boe.gov.sa, captured via Wayback archive)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": chambers_of_commerce_law_llm["record_count"],
                    "data_path": "data/chambers_of_commerce_arabic_legal_llm/chambers_of_commerce_law_legal_llm_001_066.json"}},
                "record_counts": {"arabic_articles": chambers_of_commerce_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 66, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
                                  "total": chambers_of_commerce_law_llm["record_count"]},
                "data_paths": [
                    "sources/chambers_of_commerce/law/official_source/chambers_of_commerce_law_official_source.json",
                    "sources/chambers_of_commerce/law/verified/chambers_of_commerce_law_verified_records.jsonl",
                    "data/chambers_of_commerce_arabic_legal_llm/chambers_of_commerce_law_legal_llm_001_066.json",
                ],
                "validator_targets": ["make chambers-of-commerce-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Chambers of Commerce Law «نظام الغرف التجارية» — Royal Decree M/37 dated 22/4/1442H, 66 records (complete 1..66, no مكرر) across 10 chapters/sections covering the chamber (formation and functions, administrative organs — the general assembly, the board of directors, the general secretariat — subscription, finances, performance evaluation), the federation of chambers, and the committees. IN FORCE (ساري) — the law's status badge reads «ساري» in both recent snapshots (an early 2022 snapshot's icon legend was misread as the status; the current law by Royal Decree M/37 1442H is in force). A fresh consolidated issuance: all 66 اصلية (0 معدلة / 0 ملغاة / 0 مضافة). PROVENANCE (differs from the MOJ double-official pipeline): the MOJ laws-gateway does not host this law and the BOE portal is not directly reachable from the build environment, so the official BOE text was captured from the Wayback Machine archive of the official BOE LawDetails page and CROSS-VERIFIED across two recent independent-date snapshots (2025-05 + 2026-01) — all 66 article bodies are byte-identical (zero differences). Both raw snapshots are committed under inputs/chambers_of_commerce_boe_snapshots/ with recorded sha256, and the concatenated corpus text carries a recorded sha256. No legal text altered; decorative in-word kashida removed. Arabic governs; not legal advice.",
            },
            {
                "track_id": "commercial_books_law",
                "display_name_ar": "نظام الدفاتر التجارية",
                "display_name_en": "Commercial Books Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED",
                "source_authority": "Bureau of Experts at the Council of Ministers / هيئة الخبراء بمجلس الوزراء (official legislative portal laws.boe.gov.sa, captured via Wayback archive)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": commercial_books_law_llm["record_count"],
                    "data_path": "data/commercial_books_arabic_legal_llm/commercial_books_law_legal_llm_001_016.json"}},
                "record_counts": {"arabic_articles": commercial_books_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 16, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
                                  "total": commercial_books_law_llm["record_count"]},
                "data_paths": [
                    "sources/commercial_books/law/official_source/commercial_books_law_official_source.json",
                    "sources/commercial_books/law/verified/commercial_books_law_verified_records.jsonl",
                    "data/commercial_books_arabic_legal_llm/commercial_books_law_legal_llm_001_016.json",
                ],
                "validator_targets": ["make commercial-books-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Commercial Books Law «نظام الدفاتر التجارية» — Royal Decree M/61 dated 17/12/1409H, 16 records (complete 1..16, no مكرر) — the obligation of every merchant to keep commercial (accounting) books reflecting the financial position, the required books (journal and inventory), how entries are made and kept, their evidentiary weight, and penalties. IN FORCE (ساري). A consolidated issuance: all 16 اصلية (0 معدلة / 0 ملغاة / 0 مضافة). PROVENANCE (differs from the MOJ double-official pipeline): the MOJ laws-gateway does not host this older law and the BOE portal is not directly reachable from the build environment, so the official BOE text was captured from the Wayback Machine archive of the official BOE LawDetails page and CROSS-VERIFIED across two independent-date snapshots about 13 months apart (2024-05 + 2025-06) — all 16 article bodies are byte-identical (zero differences). Both raw snapshots are committed under inputs/commercial_books_boe_snapshots/ with recorded sha256, and the concatenated corpus text carries a recorded sha256. No legal text altered; decorative in-word kashida removed. Arabic governs; not legal advice.",
            },
            {
                "track_id": "aml_law",
                "display_name_ar": "نظام مكافحة غسل الأموال",
                "display_name_en": "Anti-Money Laundering Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": aml_law_llm["record_count"],
                    "data_path": "data/aml_arabic_legal_llm/aml_law_legal_llm_001_052.json"}},
                "record_counts": {"arabic_articles": aml_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 44, "معدلة": 7, "ملغاة": 0, "مضافة": 1},
                                  "total": aml_law_llm["record_count"]},
                "data_paths": [
                    "sources/aml/law/official_source/aml_law_official_source.json",
                    "sources/aml/law/verified/aml_law_verified_records.jsonl",
                    "data/aml_arabic_legal_llm/aml_law_legal_llm_001_052.json",
                ],
                "validator_targets": ["make aml-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Anti-Money Laundering Law «نظام مكافحة غسل الأموال» — Royal Decree M/20 dated 14/2/1439H (legalStatus Active), 52 records (numbered 1..51 by ordinal position plus one مكرر article, art 49 مكرر) across the statute's chapters: definitions, the money-laundering offences and their penalties, seizure and confiscation, preventive measures and customer due diligence for financial institutions and DNFBPs, the Financial Intelligence Unit and reporting, supervision, international cooperation, and general provisions. CONSOLIDATED AMENDED: 44 اصلية / 7 معدلة (arts 14, 15, 16, 18, 28, 33, 50) / 0 ملغاة / 1 مضافة (art 49 مكرر); each amended/added article carries its history. ALL amendments and the added article were introduced by Royal Decree M/223 dated 27/10/1447H. The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (49/52 outright, mean 0.961; the 3 long definition/list articles — the first «التعريفات» article, art 24 and art 43 — visually adjudicated verbatim on the rendered pages; PDF committed with recorded sha256, 11 pages). Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "tawtheeq_law",
                "display_name_ar": "نظام التوثيق",
                "display_name_en": "Notarization Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": tawtheeq_law_llm["record_count"],
                    "data_path": "data/tawtheeq_arabic_legal_llm/tawtheeq_law_legal_llm_001_057.json"}},
                "record_counts": {"arabic_articles": tawtheeq_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 52, "معدلة": 5, "ملغاة": 0, "مضافة": 0},
                                  "total": tawtheeq_law_llm["record_count"]},
                "data_paths": [
                    "sources/tawtheeq/law/official_source/tawtheeq_law_official_source.json",
                    "sources/tawtheeq/law/verified/tawtheeq_law_verified_records.jsonl",
                    "data/tawtheeq_arabic_legal_llm/tawtheeq_law_legal_llm_001_057.json",
                ],
                "validator_targets": ["make tawtheeq-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Notarization Law «نظام التوثيق» — Royal Decree M/164 dated 19/11/1441H (legalStatus Active), 57 records (numbered 1..57 by ordinal position, no مكرر) across the statute's chapters: definitions and general provisions, notary offices (كتابات وكتاب العدل) and their jurisdiction, the notary (الموثق) and the notarization office, marriage-contract officiants (مأذونو عقود النكاح), licensing and advertising the profession, duties and prohibitions, notarization procedures, notarization media/registers (أوعية التوثيق), the evidentiary weight and protection of documents, oversight and inspection, and penalties. CONSOLIDATED AMENDED: 52 اصلية / 5 معدلة (arts 11, 12, 38, 40 by Royal Decree M/21 dated 26/1/1447H; art 15 by Royal Decree M/191 dated 29/11/1444H) / 0 ملغاة / 0 مضافة; each amended article carries its history. The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (57/57 matched outright, mean 0.964, min 0.902; no article required visual adjudication; PDF committed with recorded sha256, 10 pages). ADDITIONALLY corroborated against the Bureau of Experts at the Council of Ministers official portal (laws.boe.gov.sa) captured via the Wayback archive: all 52 اصلية articles byte-near-identical to the MOJ portal text, and the 5 amended articles' current text confirmed by the BOE 'تعديلات المادة' amendment popups (two independent official authorities agree). Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "tawtheeq_implementing_regulation",
                "display_name_ar": "اللائحة التنفيذية لنظام التوثيق",
                "display_name_en": "Implementing Regulation of the Notarization Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": tawtheeq_reg_llm["record_count"],
                    "data_path": "data/tawtheeq_arabic_legal_llm/tawtheeq_regulation_legal_llm_001_031.json"}},
                "record_counts": {"arabic_articles": tawtheeq_reg_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 31, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
                                  "total": tawtheeq_reg_llm["record_count"]},
                "data_paths": [
                    "sources/tawtheeq/regulation/official_source/tawtheeq_regulation_official_source.json",
                    "sources/tawtheeq/regulation/verified/tawtheeq_regulation_verified_records.jsonl",
                    "data/tawtheeq_arabic_legal_llm/tawtheeq_regulation_legal_llm_001_031.json",
                ],
                "validator_targets": ["make tawtheeq-regulation-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Implementing Regulation of the Notarization Law «اللائحة التنفيذية لنظام التوثيق» — issued by Minister of Justice Decision No. 1948 dated 1/6/1442H (legalStatus Active), 31 records: 30 numbered articles (1..30) across 9 chapters (the notary, marriage-contract officiants, licensing and its procedures, duties and prohibitions, notarization procedures, notarization media and their preservation, oversight and investigation, and hearing violations and imposing penalties) plus record 31, the official fee schedule «جدول المقابل المالي» (minimum and maximum financial consideration per notarization act). FRESH FULL ISSUANCE: all 31 اصلية (0 معدلة / 0 ملغاة / 0 مضافة). The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (21/31 matched outright at >=0.90; PDF committed with recorded sha256, 9 pages). PROVENANCE NOTE (differs from the clean MOJ double-official runs): the OCR channel was unavailable for this PDF in the build environment (tesseract-ara did not complete on its page images), and this PDF's text layer reorders/splits clauses and drops some ligature/digit glyphs on 10 multi-clause/list articles (arts 1, 2, 4, 11, 18, 23, 24, 26, 27, 28); each of those 10 was adjudicated VISUALLY VERBATIM on the rendered official PDF pages (every clause confirmed present and matching the portal text) and is flagged MATCHES_PDF_VISUALLY_ADJUDICATED. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "real_estate_registration_law",
                "display_name_ar": "نظام التسجيل العيني للعقار",
                "display_name_en": "Real Estate In-Kind Registration Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": real_estate_reg_law_llm["record_count"],
                    "data_path": "data/real_estate_registration_arabic_legal_llm/real_estate_registration_law_legal_llm_001_040.json"}},
                "record_counts": {"arabic_articles": real_estate_reg_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 37, "معدلة": 3, "ملغاة": 0, "مضافة": 0},
                                  "total": real_estate_reg_law_llm["record_count"]},
                "data_paths": [
                    "sources/real_estate_registration/law/official_source/real_estate_registration_law_official_source.json",
                    "sources/real_estate_registration/law/verified/real_estate_registration_law_verified_records.jsonl",
                    "data/real_estate_registration_arabic_legal_llm/real_estate_registration_law_legal_llm_001_040.json",
                ],
                "validator_targets": ["make real-estate-registration-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Real Estate In-Kind Registration Law «نظام التسجيل العيني للعقار» — Royal Decree M/91 dated 19/9/1443H (legalStatus Active), 40 records (numbered 1..40 by ordinal position, no مكرر) — the foundational statute of the in-kind (real-rights) real estate register: the real estate register and its pages, real estate zones and the first in-kind registration, subsequent dispositions and derivative rights, the conclusiveness (حجية) and protection of registered rights, objections and corrections, and closing provisions. CONSOLIDATED AMENDED: 37 اصلية / 3 معدلة (arts 6, 9, 11 by Royal Decree M/123 dated 10/6/1447H) / 0 ملغاة / 0 مضافة; each amended article carries its history. SUPERSESSION (documented): this is the IN-FORCE law; it supersedes the older repealed Real Estate In-Kind Registration Law of the same name (Royal Decree M/6 dated 11/2/1423H — legalStatus InActive/ملغي on the MOJ portal, 78 articles), which is NOT ingested. The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (40/40 matched outright, mean 0.963, min 0.903; no article required visual adjudication; PDF committed with recorded sha256, 7 pages). Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "real_estate_registration_implementing_regulation",
                "display_name_ar": "اللائحة التنفيذية لنظام التسجيل العيني للعقار",
                "display_name_en": "Implementing Regulation of the Real Estate In-Kind Registration Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": real_estate_reg_reg_llm["record_count"],
                    "data_path": "data/real_estate_registration_arabic_legal_llm/real_estate_registration_regulation_legal_llm_001_051.json"}},
                "record_counts": {"arabic_articles": real_estate_reg_reg_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 51, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
                                  "total": real_estate_reg_reg_llm["record_count"]},
                "data_paths": [
                    "sources/real_estate_registration/regulation/official_source/real_estate_registration_regulation_official_source.json",
                    "sources/real_estate_registration/regulation/verified/real_estate_registration_regulation_verified_records.jsonl",
                    "data/real_estate_registration_arabic_legal_llm/real_estate_registration_regulation_legal_llm_001_051.json",
                ],
                "validator_targets": ["make real-estate-registration-regulation-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Implementing Regulation of the Real Estate In-Kind Registration Law «اللائحة التنفيذية لنظام التسجيل العيني للعقار» — issued 27/1/1444H by the Minister of Justice implementing the in-force Real Estate In-Kind Registration Law (Royal Decree M/91, 1443H), 51 records (numbered 1..51, no مكرر) across 3 chapters: definitions and general provisions, the geospatial and survey works for applying the law, and closing provisions — covering the high committee, the real estate register/database, real estate zones, the first in-kind registration procedures, tolerances and survey specifications, and the real estate registrar's licensing. FRESH FULL ISSUANCE: all 51 اصلية (0 معدلة / 0 ملغاة / 0 مضافة). SUPERSESSION (documented): this is the IN-FORCE regulation; it supersedes the older repealed regulation of the same name (issued 1425H by Minister of Justice Decision 4497 — legalStatus InActive/ملغي on the MOJ portal, 76 hierarchically-numbered articles), which is NOT ingested. The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (46/51 matched outright at >=0.90, mean 0.951; PDF committed with recorded sha256, 13 pages). PROVENANCE NOTE: 5 long/table articles (arts 1, 6, 13, 42, 49) had their PDF text layer reorder/split clauses (every word present, zero missing unigrams) and were adjudicated VISUALLY VERBATIM on the rendered official PDF pages; arts 13 & 42 include official specification tables, and article 42's specs table carries legitimate official English remote-sensing tokens (RGB, NIR, band, minimum, bit) present verbatim in the official PDF. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "real_estate_mortgage_law",
                "display_name_ar": "نظام الرهن العقاري المسجل",
                "display_name_en": "Registered Real Estate Mortgage Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": real_estate_mortgage_law_llm["record_count"],
                    "data_path": "data/real_estate_mortgage_arabic_legal_llm/real_estate_mortgage_law_legal_llm_001_046.json"}},
                "record_counts": {"arabic_articles": real_estate_mortgage_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 46, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
                                  "total": real_estate_mortgage_law_llm["record_count"]},
                "data_paths": [
                    "sources/real_estate_mortgage/law/official_source/real_estate_mortgage_law_official_source.json",
                    "sources/real_estate_mortgage/law/verified/real_estate_mortgage_law_verified_records.jsonl",
                    "data/real_estate_mortgage_arabic_legal_llm/real_estate_mortgage_law_legal_llm_001_046.json",
                ],
                "validator_targets": ["make real-estate-mortgage-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Registered Real Estate Mortgage Law «نظام الرهن العقاري المسجل» — Royal Decree M/49 dated 13/8/1433H (legalStatus Active), 46 records (numbered 1..46, no مكرر) — the governing statute of the registered real estate mortgage as a real security right: creating the mortgage and its conditions, its effects on the mortgagor and mortgagee, its transfer and extinguishment, and enforcement over the mortgaged property (a cornerstone of secured real estate finance). FRESH FULL ISSUANCE: all 46 اصلية (0 معدلة / 0 ملغاة / 0 مضافة). The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (44/46 matched outright at >=0.90, mean 0.948; PDF committed with recorded sha256, 6 pages). PROVENANCE NOTE: 2 long articles (arts 11, 14) had their PDF text layer reorder/split clauses (every word present, zero missing unigrams) and were adjudicated VISUALLY VERBATIM on the rendered official PDF pages. Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "real_estate_finance_law",
                "display_name_ar": "نظام التمويل العقاري",
                "display_name_en": "Real Estate Finance Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": real_estate_finance_law_llm["record_count"],
                    "data_path": "data/real_estate_finance_arabic_legal_llm/real_estate_finance_law_legal_llm_001_015.json"}},
                "record_counts": {"arabic_articles": real_estate_finance_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 15, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
                                  "total": real_estate_finance_law_llm["record_count"]},
                "data_paths": [
                    "sources/real_estate_finance/law/official_source/real_estate_finance_law_official_source.json",
                    "sources/real_estate_finance/law/verified/real_estate_finance_law_verified_records.jsonl",
                    "data/real_estate_finance_arabic_legal_llm/real_estate_finance_law_legal_llm_001_015.json",
                ],
                "validator_targets": ["make real-estate-finance-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Real Estate Finance Law «نظام التمويل العقاري» — Royal Decree M/50 dated 13/8/1433H (legalStatus Active), 15 records (numbered 1..15, no مكرر) — the governing statute regulating the real estate finance sector: supervision and licensing of real estate financiers, the central bank's (المؤسسة/البنك المركزي) authority over the sector, government support for beneficiaries' housing finance, the secondary market for real estate finance (السوق الثانوية), and publication and enforcement. FRESH FULL ISSUANCE: all 15 اصلية (0 معدلة / 0 ملغاة / 0 مضافة). The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (all 15/15 matched outright at >=0.90, mean 0.965, min 0.933; PDF committed with recorded sha256, 5 pages) — no visual adjudication needed. Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "real_estate_units_law",
                "display_name_ar": "نظام ملكية الوحدات العقارية وفرزها وإدارتها",
                "display_name_en": "Real Estate Unit Ownership Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": real_estate_units_law_llm["record_count"],
                    "data_path": "data/real_estate_units_arabic_legal_llm/real_estate_units_law_legal_llm_001_033.json"}},
                "record_counts": {"arabic_articles": real_estate_units_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 33, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
                                  "total": real_estate_units_law_llm["record_count"]},
                "data_paths": [
                    "sources/real_estate_units/law/official_source/real_estate_units_law_official_source.json",
                    "sources/real_estate_units/law/verified/real_estate_units_law_verified_records.jsonl",
                    "data/real_estate_units_arabic_legal_llm/real_estate_units_law_legal_llm_001_033.json",
                ],
                "validator_targets": ["make real-estate-units-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Real Estate Unit Ownership Law «نظام ملكية الوحدات العقارية وفرزها وإدارتها» — Royal Decree M/85 dated 2/7/1441H (legalStatus Active), 33 records (numbered 1..33, no مكرر) across chapters on definitions, partition of the property (فرز العقار), ownership provisions, the owners' association (جمعية الملاك), management and maintenance, and closing provisions — the governing statute for condominium/multi-unit real estate ownership, partition and management. FRESH FULL ISSUANCE: all 33 اصلية (0 معدلة / 0 ملغاة / 0 مضافة). SUPERSESSION (documented): this in-force law replaced (حل محل) the older Real Estate Unit Ownership and Partition Law of 1423H, which is repealed and NOT ingested. The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (all 33/33 matched outright at >=0.90, mean 0.971, min 0.943; PDF committed with recorded sha256, 8 pages) — no visual adjudication needed. Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "real_estate_units_implementing_regulation",
                "display_name_ar": "اللائحة التنفيذية لنظام ملكية الوحدات العقارية وفرزها وإدارتها",
                "display_name_en": "Real Estate Unit Ownership Law Implementing Regulation",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": real_estate_units_reg_llm["record_count"],
                    "data_path": "data/real_estate_units_arabic_legal_llm/real_estate_units_regulation_legal_llm_001_041.json"}},
                "record_counts": {"arabic_articles": real_estate_units_reg_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 39, "معدلة": 2, "ملغاة": 0, "مضافة": 0},
                                  "total": real_estate_units_reg_llm["record_count"]},
                "data_paths": [
                    "sources/real_estate_units/implementing_regulation/official_source/real_estate_units_regulation_official_source.json",
                    "sources/real_estate_units/implementing_regulation/verified/real_estate_units_regulation_verified_records.jsonl",
                    "data/real_estate_units_arabic_legal_llm/real_estate_units_regulation_legal_llm_001_041.json",
                ],
                "validator_targets": ["make real-estate-units-regulation-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Implementing Regulation of the Real Estate Unit Ownership Law «اللائحة التنفيذية لنظام ملكية الوحدات العقارية وفرزها وإدارتها» — issued by the Minister of Municipal, Rural Affairs and Housing (Decision 168, 22/10/1441H) implementing the in-force Real Estate Unit Ownership Law (Royal Decree M/85, 1441H), 41 records (numbered 1..41, no مكرر) across chapters on definitions, partition of the property, ownership provisions, the owners' association and complex association (جمعية الملاك / جمعية المجمع), management and maintenance, and closing provisions. CONSOLIDATED AMENDED: 39 اصلية / 2 معدلة (arts 4, 10) / 0 ملغاة / 0 مضافة; each amended article carries its full version history — art 4 amended by Ministerial Decisions 4500000499 (18/2/1445H) then 4600003967 (25/4/1446H), art 10 amended by Ministerial Decision 4500000499 (18/2/1445H); the current consolidated text governs. The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (40/41 matched outright at >=0.90, mean 0.964; PDF committed with recorded sha256, 9 pages). PROVENANCE NOTE: 1 long article (art 27, the auditor article) had its PDF text layer reorder/split clauses (every word present, zero missing unigrams) and was adjudicated VISUALLY VERBATIM on the rendered official PDF pages. Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "foreign_ownership_law",
                "display_name_ar": "نظام تملك غير السعوديين للعقار",
                "display_name_en": "Non-Saudi Real Estate Ownership Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": foreign_ownership_law_llm["record_count"],
                    "data_path": "data/foreign_ownership_arabic_legal_llm/foreign_ownership_law_legal_llm_001_015.json"}},
                "record_counts": {"arabic_articles": foreign_ownership_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 15, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
                                  "total": foreign_ownership_law_llm["record_count"]},
                "data_paths": [
                    "sources/foreign_ownership/law/official_source/foreign_ownership_law_official_source.json",
                    "sources/foreign_ownership/law/verified/foreign_ownership_law_verified_records.jsonl",
                    "data/foreign_ownership_arabic_legal_llm/foreign_ownership_law_legal_llm_001_015.json",
                ],
                "validator_targets": ["make foreign-ownership-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Non-Saudi Real Estate Ownership Law «نظام تملك غير السعوديين للعقار لعام ١٤٤٧هـ» — Royal Decree M/14 dated 19/1/1447H (legalStatus Active), 15 records (numbered 1..15, no مكرر) — the governing statute for the ownership and acquisition of real rights over real estate by non-Saudis: the geographic scope set by the Council of Ministers, ownership by listed companies, premium-residency provisions, diplomatic-mission premises, registration with the Real Estate General Authority, fees and taxes, penalties, and the enforcement committee. FRESH FULL ISSUANCE: all 15 اصلية (0 معدلة / 0 ملغاة / 0 مضافة). SUPERSESSION (documented, per its art 14): this in-force law replaced the older Non-Saudi Real Estate Ownership and Investment Law (Royal Decree M/15, 17/4/1421H — legalStatus InActive on the MOJ portal), which is NOT ingested. The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (12/15 matched outright at >=0.90, mean 0.945; PDF committed with recorded sha256, 3 pages). PROVENANCE NOTE: 3 articles (2, 7, 12) had their PDF text layer reorder/split clauses (every word present, zero missing unigrams) and were adjudicated VISUALLY VERBATIM on the rendered official PDF pages. Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "municipal_realestate_law",
                "display_name_ar": "نظام التصرف في العقارات البلدية",
                "display_name_en": "Municipal Real Estate Disposal Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": municipal_re_law_llm["record_count"],
                    "data_path": "data/municipal_realestate_arabic_legal_llm/municipal_realestate_law_legal_llm_001_006.json"}},
                "record_counts": {"arabic_articles": municipal_re_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 6, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
                                  "total": municipal_re_law_llm["record_count"]},
                "data_paths": [
                    "sources/municipal_realestate/law/official_source/municipal_realestate_law_official_source.json",
                    "sources/municipal_realestate/law/verified/municipal_realestate_law_verified_records.jsonl",
                    "data/municipal_realestate_arabic_legal_llm/municipal_realestate_law_legal_llm_001_006.json",
                ],
                "validator_targets": ["make municipal-realestate-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Municipal Real Estate Disposal Law «نظام التصرف في العقارات البلدية» — Royal Decree M/64 dated 15/11/1392H (legalStatus Active), 6 records (numbered 1..6, no مكرر) — the governing statute for municipalities' disposal of their real property: the inalienability of municipal public property, disposal of private municipal property, and municipalities without municipal councils. FRESH FULL ISSUANCE: all 6 اصلية. The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (all 6/6 matched outright at >=0.90, mean 0.974; PDF committed with recorded sha256, 1 page) — no visual adjudication needed. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "municipal_realestate_implementing_regulation",
                "display_name_ar": "لائحة التصرف بالعقارات البلدية",
                "display_name_en": "Municipal Real Estate Disposal Regulation",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": municipal_re_reg_llm["record_count"],
                    "data_path": "data/municipal_realestate_arabic_legal_llm/municipal_realestate_regulation_legal_llm_001_035.json"}},
                "record_counts": {"arabic_articles": municipal_re_reg_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 31, "معدلة": 3, "ملغاة": 0, "مضافة": 1},
                                  "total": municipal_re_reg_llm["record_count"]},
                "data_paths": [
                    "sources/municipal_realestate/implementing_regulation/official_source/municipal_realestate_regulation_official_source.json",
                    "sources/municipal_realestate/implementing_regulation/verified/municipal_realestate_regulation_verified_records.jsonl",
                    "data/municipal_realestate_arabic_legal_llm/municipal_realestate_regulation_legal_llm_001_035.json",
                ],
                "validator_targets": ["make municipal-realestate-regulation-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Regulation on the Disposal of Municipal Real Estate «لائحة التصرف بالعقارات البلدية» — issued by High Order (أمر سامي) 40152 dated 29/6/1441H under the Municipal Real Estate Disposal Law M/64, 35 records (numbered 1..34 by ordinal position plus one مكرر article, 13 مكرر) — covering definitions, municipal real estate, disposal of planning/subdivision surplus, exchange (المعاوضة), investment and competition procedures, and the committees. CONSOLIDATED AMENDED: 31 اصلية / 3 معدلة (arts 10, 13, 21) / 0 ملغاة / 1 مضافة (art 13 مكرر); each amended/added article carries its full version history; the current consolidated text governs. SUPERSESSION (documented, per its art 33): it replaced the 1423H municipal real-estate disposal regulation (High Order 3/ب/38313, 24/9/1423H), which is NOT ingested. The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (31/35 matched outright at >=0.90, mean 0.953; PDF committed with recorded sha256, 6 pages). PROVENANCE NOTE: 4 articles (6, 13, 14, 33) had their PDF text layer reorder/split clauses (every word present, zero missing unigrams) and were adjudicated VISUALLY VERBATIM on the rendered official PDF pages. Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "gcc_ownership_law",
                "display_name_ar": "تنظيم تملك مواطني دول المجلس للعقار في الدول الأعضاء بمجلس التعاون لغرض السكن والاستثمار",
                "display_name_en": "GCC Citizens Real Estate Ownership Regulation",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": gcc_ownership_law_llm["record_count"],
                    "data_path": "data/gcc_ownership_arabic_legal_llm/gcc_ownership_law_legal_llm_001_006.json"}},
                "record_counts": {"arabic_articles": gcc_ownership_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 6, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
                                  "total": gcc_ownership_law_llm["record_count"]},
                "data_paths": [
                    "sources/gcc_ownership/law/official_source/gcc_ownership_law_official_source.json",
                    "sources/gcc_ownership/law/verified/gcc_ownership_law_verified_records.jsonl",
                    "data/gcc_ownership_arabic_legal_llm/gcc_ownership_law_legal_llm_001_006.json",
                ],
                "validator_targets": ["make gcc-ownership-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Regulation on GCC Citizens' Real Estate Ownership «تنظيم تملك مواطني دول المجلس للعقار في الدول الأعضاء بمجلس التعاون لغرض السكن والاستثمار» — Royal Decree M/22 dated 3/4/1432H (legalStatus Active), 6 records (numbered 1..6, no مكرر) — the governing instrument allowing GCC citizens (natural or GCC-wholly-owned legal persons) to rent and own built real estate and land for housing or investment, with rules on land use, disposal, expropriation, and prohibition of ownership in Makkah and Madinah. FRESH FULL ISSUANCE: all 6 اصلية. SUPERSESSION (documented): this in-force instrument replaced the version approved in the Supreme Council's 20th session (1422H), which is NOT ingested. The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (all 6/6 matched outright at >=0.90, mean 0.976; PDF committed with recorded sha256, 1 page) — no visual adjudication needed. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "terrorism_law",
                "display_name_ar": "نظام مكافحة جرائم الإرهاب وتمويله",
                "display_name_en": "Law on Combating Crimes of Terrorism and its Financing",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": terrorism_law_llm["record_count"],
                    "data_path": "data/terrorism_arabic_legal_llm/terrorism_law_legal_llm_001_099.json"}},
                "record_counts": {"arabic_articles": terrorism_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 88, "معدلة": 8, "ملغاة": 0, "مضافة": 3},
                                  "total": terrorism_law_llm["record_count"]},
                "data_paths": [
                    "sources/terrorism/law/official_source/terrorism_law_official_source.json",
                    "sources/terrorism/law/verified/terrorism_law_verified_records.jsonl",
                    "data/terrorism_arabic_legal_llm/terrorism_law_legal_llm_001_099.json",
                ],
                "validator_targets": ["make terrorism-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Law on Combating Crimes of Terrorism and its Financing «نظام مكافحة جرائم الإرهاب وتمويله» — Royal Decree M/21 dated 12/2/1439H (legalStatus Active), 99 records (numbered 1..96 by ordinal position plus three مكرر articles: 59, 63, 81 مكرر) across chapters on definitions, general provisions, procedures, penalties, confiscation, precautionary measures, international cooperation, the General Directorate of Financial Investigations, oversight, and closing provisions — the primary criminal statute on terrorism and terrorism financing (complements the Anti-Money Laundering Law). CONSOLIDATED AMENDED: 88 اصلية / 8 معدلة (arts 4, 9, 12, 63, 67, 70, 71, 83) / 0 ملغاة / 3 مضافة (arts 59 مكرر, 63 مكرر, 81 مكرر); each amended/added article carries its full version history; the current consolidated text governs. SUPERSESSION (documented): this law replaced the older Law of Terrorism Crimes and its Financing (Royal Decree M/16, 24/2/1435H), which is superseded. DATA NOTE: the portal's sequence field for article 75 was doubled ('المادة الخامسة والسبعون' concatenated twice); the correct single official label is stored (no legal text affected). The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (90/99 matched outright at >=0.90, mean 0.955; PDF committed with recorded sha256, 15 pages). PROVENANCE NOTE: 9 long articles (1, 3, 10, 39, 43, 50, 56, 82, 83) had their PDF text layer reorder/split clauses (every word present; the few unigram gaps were OCR gluing the trailing comma to a word, confirmed on the rendered pages) and were adjudicated VISUALLY VERBATIM on the rendered official PDF pages. Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "terrorism_implementing_regulation",
                "display_name_ar": "اللائحة التنفيذية لنظام مكافحة جرائم الإرهاب وتمويله",
                "display_name_en": "Implementing Regulation of the Law on Combating Crimes of Terrorism and its Financing",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": terrorism_reg_llm["record_count"],
                    "data_path": "data/terrorism_arabic_legal_llm/terrorism_regulation_legal_llm_001_028.json"}},
                "record_counts": {"arabic_articles": terrorism_reg_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 18, "معدلة": 7, "ملغاة": 1, "مضافة": 2},
                                  "total": terrorism_reg_llm["record_count"]},
                "data_paths": [
                    "sources/terrorism/implementing_regulation/official_source/terrorism_regulation_official_source.json",
                    "sources/terrorism/implementing_regulation/verified/terrorism_regulation_verified_records.jsonl",
                    "data/terrorism_arabic_legal_llm/terrorism_regulation_legal_llm_001_028.json",
                ],
                "validator_targets": ["make terrorism-regulation-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Implementing Regulation of the Law on Combating Crimes of Terrorism and its Financing «اللائحة التنفيذية لنظام مكافحة جرائم الإرهاب وتمويله» — issued by Council of Ministers Decision 228 dated 2/5/1440H implementing the in-force Law on Combating Crimes of Terrorism and its Financing (Royal Decree M/21, 1439H), 28 records (numbered 1..26 by ordinal position plus two مكرر articles: 20, 23 مكرر) — defining the financial activities/operations, professions, and controlling bodies referenced by the law; arrest, search and seizure procedures; enforcement of foreign final judgments; the competent asset-recovery/confiscation-sharing authority; obligations of financial institutions and non-financial businesses/professions; and the powers of the General Directorate of Financial Investigations. CONSOLIDATED AMENDED: 18 اصلية / 7 معدلة (arts 2, 4, 16, 18, 21, 23, 24) / 1 ملغاة (art 9, its full body kept and FLAGGED rather than deleted) / 2 مضافة (arts 20 مكرر, 23 مكرر); each amended/added/repealed article carries its full version history; the current consolidated text governs. The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (26/28 matched outright at >=0.90, mean 0.947; PDF committed with recorded sha256, 9 pages). PROVENANCE NOTE: 2 list articles (1, 4) had their PDF text layer reorder/split clauses (near-zero missing unigrams) and were adjudicated VISUALLY VERBATIM on the rendered official PDF pages. Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "juveniles_law",
                "display_name_ar": "نظام الأحداث",
                "display_name_en": "Juveniles Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": juveniles_law_llm["record_count"],
                    "data_path": "data/juveniles_arabic_legal_llm/juveniles_law_legal_llm_001_024.json"}},
                "record_counts": {"arabic_articles": juveniles_law_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 24, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
                                  "total": juveniles_law_llm["record_count"]},
                "data_paths": [
                    "sources/juveniles/law/official_source/juveniles_law_official_source.json",
                    "sources/juveniles/law/verified/juveniles_law_verified_records.jsonl",
                    "data/juveniles_arabic_legal_llm/juveniles_law_legal_llm_001_024.json",
                ],
                "validator_targets": ["make juveniles-law-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Juveniles Law «نظام الأحداث» — Royal Decree M/113 dated 19/11/1439H (legalStatus Active), 24 records (numbered 1..24, no مكرر) — the governing statute for juvenile criminal responsibility and procedure: definitions, penal accountability, Hijri age calculation, complaint-handling and flagrante-delicto procedures, arrest and investigative detention of juveniles, the juvenile's dedicated Dar (facility), social-investigation reports, trial before the court, measures/penalties applicable below age 15 versus at/above age 15, conditional release, and joint adult/juvenile offenses. FRESH FULL ISSUANCE: all 24 اصلية (0 معدلة / 0 ملغاة / 0 مضافة). The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (22/24 matched outright at >=0.90, mean 0.951; PDF committed with recorded sha256, 3 pages). PROVENANCE NOTE: 2 articles (5, 20) had their PDF text layer reorder/split clauses (near-zero missing unigrams) and were adjudicated VISUALLY VERBATIM on the rendered official PDF pages. Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
            {
                "track_id": "juveniles_implementing_regulation",
                "display_name_ar": "اللائحة التنفيذية لنظام الأحداث",
                "display_name_en": "Implementing Regulation of the Juveniles Law",
                "corpus_family": "statutory_law",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "complete",
                "official_text_status": "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
                "source_authority": "Ministry of Justice / وزارة العدل (official legal portal laws.moj.gov.sa: database + published PDF)",
                "language_layers": {"arabic": {"status": "complete", "governing": True,
                    "record_count": juveniles_reg_llm["record_count"],
                    "data_path": "data/juveniles_arabic_legal_llm/juveniles_regulation_legal_llm_001_013.json"}},
                "record_counts": {"arabic_articles": juveniles_reg_llm["record_count"],
                                  "legal_status_breakdown": {"اصلية": 13, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
                                  "total": juveniles_reg_llm["record_count"]},
                "data_paths": [
                    "sources/juveniles/implementing_regulation/official_source/juveniles_regulation_official_source.json",
                    "sources/juveniles/implementing_regulation/verified/juveniles_regulation_verified_records.jsonl",
                    "data/juveniles_arabic_legal_llm/juveniles_regulation_legal_llm_001_013.json",
                ],
                "validator_targets": ["make juveniles-regulation-track-validate"],
                "report_paths": [],
                "boundaries": {"arabic_governs": True, "not_official_translation": True,
                               "not_verified_official_text": False, "not_legal_advice": True,
                               "no_trilingual_alignment": True, "no_public_release": True},
                "notes": "Implementing Regulation of the Juveniles Law «اللائحة التنفيذية لنظام الأحداث» — issued by Council of Ministers Decision 237 dated 16/4/1442H implementing the in-force Juveniles Law (Royal Decree M/113, 1439H), 13 records (numbered 1..13, no مكرر) — definitions, age-determination procedures, flagrante-delicto arrest and complaint-handling for the juvenile plaintiff, arrest of the juvenile, the unidentified juvenile, detention-extension requests, safeguarding the juvenile in the Dar, investigation with the juvenile, the social-investigation report, cases where a case file suffices without a formal indictment, social supervision of the juvenile, the juvenile's special register, conditional release, and publication/enforcement. FRESH FULL ISSUANCE: all 13 اصلية (0 معدلة / 0 ملغاة / 0 مضافة). The section-API status equals the statuteStructure/PDF status for every article (no dual-status divergence). Fetched article-by-article from the official MOJ legal-portal database (get-Section-Changes) and cross-verified against the official MOJ PDF from the same portal (12/13 matched outright at >=0.90, mean 0.947; PDF committed with recorded sha256, 2 pages). PROVENANCE NOTE: article 4 had its PDF text layer reorder/split clauses (zero missing unigrams) and was adjudicated VISUALLY VERBATIM on the rendered official PDF pages. Text-layer folding handled the PDF's Arabic-Presentation-Forms/Farsi-yeh glyphs. Decorative in-word kashida removed; the 'هـ' enumerator and space-bounded enumerator dashes kept. Arabic governs; not legal advice.",
            },
        ],
    }

    _dump_json(registry, OUTPUT_PATH)
    print(f"[OK] Corpus registry written: {OUTPUT_PATH}")
    print(f"     {registry['total_tracks']} tracks, {registry['total_registry_counted_records']} registry-counted records")
    print(f"     Primary Arabic: {registry['total_primary_arabic_governing_records']}, Reference: {registry['total_reference_records']}, Internal ref: {registry['total_internal_reference_records']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())