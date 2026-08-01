#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Strict repository QA gate — one command, everything must pass.

Three phases, all mandatory:

  [1] VALIDATORS — runs EVERY ``scripts/validate_*.py`` in the repository.
      Coverage is strict by construction: validators are discovered from the
      filesystem, so a newly added validator automatically joins the gate.
      A validator may only be skipped by listing it in ``EXCLUDED`` with a
      written reason; anything else that fails, fails the gate.

  [2] IDEMPOTENCE — re-runs the registered deterministic generators and then
      requires the git working tree to be byte-identical to before (tracked
      files). This catches "generator edited but outputs not regenerated" and
      any non-deterministic generator drift.

  [3] TESTS — the full pytest suite (skippable with --no-tests when the caller
      already runs pytest separately, e.g. as its own CI step).

Exit 0 only if every phase passes. Output is a per-step PASS/FAIL table plus a
final verdict line. Read-only over corpus data except for the regeneration in
phase 2, which must produce zero diffs to pass.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import glob
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Validators intentionally excluded from the gate. Empty today — keep it that
# way unless a validator genuinely cannot run headless; every entry MUST carry
# a reason string.
EXCLUDED: dict[str, str] = {}

# Deterministic generators re-run in phase 2. Each must be idempotent: running
# it on a clean tree must produce zero tracked-file changes.
IDEMPOTENT_GENERATORS = [
    "scripts/gen_pdpl_arabic_law_verified.py",
    "scripts/gen_pdpl_arabic_law_legal_llm.py",
    "scripts/gen_pdpl_implementing_regulation_arabic_cleaned.py",
    "scripts/gen_pdpl_implementing_regulation_arabic_verified.py",
    "scripts/gen_pdpl_implementing_regulation_arabic_legal_llm.py",
    "scripts/gen_investment_law_verified.py",
    "scripts/gen_investment_law_legal_llm.py",
    "scripts/gen_investment_regulation_verified.py",
    "scripts/gen_investment_regulation_legal_llm.py",
    "scripts/gen_civil_transactions_law_verified.py",
    "scripts/gen_civil_transactions_law_legal_llm.py",
    "scripts/gen_gtpl_law_track.py",
    "scripts/gen_gtpl_regulation_track.py",
    "scripts/gen_labor_law_track.py",
    "scripts/gen_labor_regulation_track.py",
    "scripts/gen_labor_annex1_track.py",
    "scripts/gen_labor_annex34_tracks.py",
    "scripts/gen_labor_annex2_track.py",
    "scripts/gen_labor_annex5_track.py",
    "scripts/gen_evidence_law_track.py",
    "scripts/gen_evidence_companions_tracks.py",
    "scripts/gen_personal_status_tracks.py",
    "scripts/gen_sharia_procedure_law_track.py",
    "scripts/gen_sharia_procedure_regulation_track.py",
    "scripts/gen_criminal_procedure_law_track.py",
    "scripts/gen_criminal_procedure_regulation_track.py",
    "scripts/gen_enforcement_law_track.py",
    "scripts/gen_enforcement_regulation_track.py",
    "scripts/gen_judiciary_law_track.py",
    "scripts/gen_board_of_grievances_law_track.py",
    "scripts/gen_law_practice_law_track.py",
    "scripts/gen_law_practice_regulation_track.py",
    "scripts/gen_commercial_courts_law_track.py",
    "scripts/gen_commercial_courts_regulation_track.py",
    "scripts/gen_bankruptcy_law_track.py",
    "scripts/gen_bankruptcy_regulation_track.py",
    "scripts/gen_bankruptcy_case_rules_track.py",
    "scripts/gen_judicial_costs_law_track.py",
    "scripts/gen_judicial_costs_regulation_track.py",
    "scripts/gen_arbitration_law_track.py",
    "scripts/gen_arbitration_regulation_track.py",
    "scripts/gen_commercial_papers_law_track.py",
    "scripts/gen_commercial_register_law_track.py",
    "scripts/gen_trade_names_law_track.py",
    "scripts/gen_commercial_agencies_law_track.py",
    "scripts/gen_chambers_of_commerce_law_track.py",
    "scripts/gen_commercial_books_law_track.py",
    "scripts/gen_aml_law_track.py",
    "scripts/gen_tawtheeq_law_track.py",
    "scripts/gen_tawtheeq_regulation_track.py",
    "scripts/gen_real_estate_registration_law_track.py",
    "scripts/gen_real_estate_registration_regulation_track.py",
    "scripts/gen_real_estate_mortgage_law_track.py",
    "scripts/gen_real_estate_finance_law_track.py",
    "scripts/gen_real_estate_units_law_track.py",
    "scripts/gen_real_estate_units_regulation_track.py",
    "scripts/gen_foreign_ownership_law_track.py",
    "scripts/gen_municipal_realestate_law_track.py",
    "scripts/gen_municipal_realestate_regulation_track.py",
    "scripts/gen_gcc_ownership_law_track.py",
    "scripts/gen_terrorism_law_track.py",
    "scripts/gen_terrorism_regulation_track.py",
    "scripts/gen_juveniles_law_track.py",
    "scripts/gen_juveniles_regulation_track.py",
    "scripts/gen_whistleblower_law_track.py",
    "scripts/gen_judicial_inspection_regulation_track.py",
    "scripts/gen_qismah_regulation_track.py",
    "scripts/gen_sulook_regulation_track.py",
    "scripts/gen_aawan_regulation_track.py",
    "scripts/gen_muslaha_regulation_track.py",
    "scripts/gen_iflas_hudud_regulation_track.py",
    "scripts/gen_judicial_documents_regulation_track.py",
    "scripts/gen_bankruptcy_fees_regulation_track.py",
    "scripts/gen_enforcement_providers_regulation_track.py",
    "scripts/gen_alimony_fund_regulation_track.py",
    "scripts/gen_judiciary_bog_mechanism_track.py",
    "scripts/gen_documentation_settlement_regulation_track.py",
    "scripts/gen_mosalaha_center_regulation_track.py",
    "scripts/gen_medical_reports_regulation_track.py",
    "scripts/gen_marriage_non_saudi_regulation_track.py",
    "scripts/gen_state_funded_lawyer_regulation_track.py",
    "scripts/gen_lessor_repossession_regulation_track.py",
    "scripts/gen_elitigation_guide_regulation_track.py",
    "scripts/gen_judicial_training_center_guide_track.py",
    "scripts/gen_judgment_objection_methods_regulation_track.py",
    "scripts/gen_real_estate_expropriation_law_track.py",
    "scripts/gen_marriage_contract_hearing_regulation_track.py",
    "scripts/gen_anti_bribery_law_track.py",
    "scripts/gen_basic_law_of_governance_track.py",
    "scripts/gen_anti_cyber_crime_law_track.py",
    "scripts/gen_anti_harassment_law_track.py",
    "scripts/gen_anti_trafficking_law_track.py",
    "scripts/gen_council_of_ministers_law_track.py",
    "scripts/gen_regions_law_track.py",
    "scripts/gen_electronic_transactions_law_track.py",
    "scripts/gen_allegiance_commission_law_track.py",
    "scripts/gen_shura_council_law_track.py",
    "scripts/gen_copyright_law_track.py",
    "scripts/gen_telecommunications_law_track.py",
    "scripts/gen_sama_law_track.py",
    "scripts/gen_banking_control_law_track.py",
    "scripts/gen_capital_market_law_track.py",
    "scripts/gen_competition_law_track.py",
    "scripts/gen_payment_systems_law_track.py",
    "scripts/gen_mining_investment_law_track.py",
    "scripts/gen_trademark_law_track.py",
    "scripts/gen_anti_concealment_law_track.py",
    "scripts/gen_insurance_control_law_track.py",
    "scripts/gen_ecommerce_law_track.py",
    "scripts/gen_vat_law_track.py",
    "scripts/gen_franchise_law_track.py",
    "scripts/gen_civil_aviation_law_track.py",
    "scripts/gen_anti_narcotics_law_track.py",
    "scripts/gen_traffic_law_track.py",
    "scripts/gen_environmental_law_track.py",
    "scripts/gen_income_tax_law_track.py",
    "scripts/gen_civil_service_law_track.py",
    "scripts/gen_social_insurance_law_track.py",
    "scripts/gen_social_insurance_legacy_law_track.py",
    "scripts/gen_zakat_law_track.py",
    "scripts/gen_patent_law_track.py",
    "scripts/gen_customs_law_track.py",
    "scripts/gen_customs_regulation_track.py",
    "scripts/gen_anti_fraud_law_track.py",
    "scripts/gen_finance_companies_law_track.py",
    "scripts/gen_cooperative_health_insurance_law_track.py",
    "scripts/gen_healthcare_professions_law_track.py",
    "scripts/gen_finance_lease_law_track.py",
    "scripts/gen_maritime_commercial_law_track.py",
    "scripts/gen_gcc_anti_dumping_law_track.py",
    "scripts/gen_accounting_auditing_law_track.py",
    "scripts/gen_nazaha_law_track.py",
    "scripts/gen_awqaf_law_track.py",
    "scripts/gen_saudi_engineers_law_track.py",
    "scripts/gen_municipal_councils_law_track.py",
    "scripts/gen_press_law_track.py",
    "scripts/gen_engineering_practice_law_track.py",
    "scripts/gen_nationality_law_track.py",
    "scripts/gen_residency_law_track.py",
    "scripts/gen_civil_status_law_track.py",
    "scripts/gen_food_law_track.py",
    "scripts/gen_health_system_law_track.py",
    "scripts/gen_domestic_labor_regulation_track.py",
    "scripts/gen_travel_documents_law_track.py",
    "scripts/gen_cybersecurity_authority_law_track.py",
    "scripts/gen_cybersecurity_authority_enablers_track.py",
    "scripts/gen_premium_residency_law_track.py",
    "scripts/gen_travel_documents_regulation_track.py",
    "scripts/gen_nationality_regulation_track.py",
    "scripts/gen_health_system_regulation_track.py",
    "scripts/gen_food_regulation_track.py",
    "scripts/gen_electricity_law_track.py",
    "scripts/gen_water_law_track.py",
    "scripts/gen_vat_regulation_track.py",
    "scripts/gen_income_tax_regulation_track.py",
    "scripts/gen_agriculture_law_track.py",
    "scripts/gen_competition_regulation_track.py",
    "scripts/gen_aml_regulation_track.py",
    "scripts/gen_patent_regulation_track.py",
    "scripts/gen_ecommerce_regulation_track.py",
    "scripts/gen_franchise_regulation_track.py",
    "scripts/gen_traffic_regulation_track.py",
    "scripts/gen_environmental_inspection_audit_reg_track.py",
    "scripts/gen_environmental_violations_penalties_reg_track.py",
    "scripts/gen_environmental_wildlife_hunting_reg_track.py",
    "scripts/gen_environmental_permits_reg_track.py",
    "scripts/gen_environmental_air_quality_reg_track.py",
    "scripts/gen_environmental_service_providers_reg_track.py",
    "scripts/gen_environmental_fees_reg_track.py",
    "scripts/gen_rett_law_track.py",
    "scripts/gen_universities_law_track.py",
    "scripts/gen_privatization_law_track.py",
    "scripts/gen_antiquities_heritage_law_track.py",
    "scripts/gen_child_protection_law_track.py",
    "scripts/gen_protection_from_abuse_law_track.py",
    "scripts/gen_associations_ngo_law_track.py",
    "scripts/gen_audiovisual_media_law_track.py",
    "scripts/gen_sports_law_track.py",
    "scripts/gen_anti_smoking_law_track.py",
    "scripts/gen_weapons_ammunition_law_track.py",
    "scripts/gen_prison_detention_law_track.py",
    "scripts/gen_civil_defense_law_track.py",
    "scripts/gen_cooperative_societies_law_track.py",
    "scripts/gen_building_code_law_track.py",
    "scripts/gen_product_safety_law_track.py",
    "scripts/gen_standards_quality_law_track.py",
    "scripts/gen_disability_rights_law_track.py",
    "scripts/gen_tourism_law_track.py",
    "scripts/gen_tourism_travel_services_reg_track.py",
    "scripts/gen_hospitality_mgmt_reg_track.py",
    "scripts/gen_hospitality_facility_reg_track.py",
    "scripts/gen_tourist_visa_reg_track.py",
    "scripts/gen_environmental_noise_reg_track.py",
    "scripts/gen_environmental_protected_areas_reg_track.py",
    "scripts/gen_environmental_emergency_response_reg_track.py",
    "scripts/gen_product_safety_regulation_track.py",
    "scripts/gen_handicrafts_law_track.py",
    "scripts/gen_medical_devices_law_track.py",
    "scripts/gen_museums_authority_licensing_regulation_track.py",
    "scripts/gen_heritage_authority_licensing_regulation_track.py",
    "scripts/gen_literature_publishing_translation_authority_licensing_regulation_track.py",
    "scripts/gen_film_authority_licensing_regulation_track.py",
    "scripts/gen_fashion_authority_licensing_regulation_track.py",
    "scripts/gen_music_authority_licensing_regulation_track.py",
    "scripts/gen_culinary_arts_authority_licensing_regulation_track.py",
    "scripts/gen_architecture_design_authority_licensing_regulation_track.py",
    "scripts/gen_visual_arts_authority_licensing_regulation_track.py",
    "scripts/gen_tourism_consultancy_regulation_track.py",
    "scripts/gen_tourism_activity_inspection_regulation_track.py",
    "scripts/gen_duty_free_markets_rules_track.py",
    "scripts/gen_driving_schools_regulation_track.py",
    "scripts/gen_railway_violations_committee_rules_track.py",
    "scripts/gen_public_transport_users_rights_mechanism_track.py",
    "scripts/gen_gcc_pesticides_regulation_track.py",
    "scripts/gen_military_industries_rnd_regulation_track.py",
    "scripts/gen_international_bus_transport_regulation_track.py",
    "scripts/gen_vehicle_periodic_inspection_regulation_track.py",
    "scripts/gen_health_specialties_membership_regulation_track.py",
    "scripts/gen_disability_social_programs_regulation_track.py",
    "scripts/gen_vehicle_damage_assessment_rules_track.py",
    "scripts/gen_tourist_accommodation_facilities_regulation_track.py",
    "scripts/gen_ngo_council_regulation_track.py",
    "scripts/gen_health_holding_company_statute_track.py",
    "scripts/gen_family_funds_rules_track.py",
    "scripts/gen_airports_economic_regulation_track.py",
    "scripts/gen_valuation_profession_conduct_rules_track.py",
    "scripts/gen_nazara_works_regulation_track.py",
    "scripts/gen_ballast_water_regulation_track.py",
    "scripts/gen_sez_kaec_regulation_track.py",
    "scripts/gen_sez_jazan_regulation_track.py",
    "scripts/gen_sez_raskhair_regulation_track.py",
    "scripts/gen_charitable_societies_council_regulation_track.py",
    "scripts/gen_customs_procedures_controls_track.py",
    "scripts/gen_social_security_regulation_track.py",
    "scripts/gen_revenue_sharing_rules_track.py",
    "scripts/gen_freight_broker_logistics_regulation_track.py",
    "scripts/gen_property_ownership_committees_rules_track.py",
    "scripts/gen_disability_nongov_social_facilities_regulation_track.py",
    "scripts/gen_free_zone_employees_treatment_rules_track.py",
    "scripts/gen_inspection_control_seizure_rules_track.py",
    "scripts/gen_ip_services_licensing_rules_track.py",
    "scripts/gen_deposit_zones_rules_track.py",
    "scripts/gen_air_transport_services_economic_regulation_track.py",
    "scripts/gen_privatization_governing_rules_track.py",
    "scripts/gen_ground_handling_air_cargo_economic_regulation_track.py",
    "scripts/gen_museums_regulation_track.py",
    "scripts/gen_private_universities_regulation_track.py",
    "scripts/gen_gcc_road_transport_law_track.py",
    "scripts/gen_marpol_regulation_track.py",
    "scripts/gen_securities_disputes_rules_track.py",
    "scripts/gen_state_realestate_disposal_regulation_track.py",
    "scripts/gen_securities_depository_markets_regulation_track.py",
    "scripts/gen_capital_adequacy_rules_track.py",
    "scripts/gen_mergers_acquisitions_regulation_track.py",
    "scripts/gen_taxi_activity_regulation_track.py",
    "scripts/gen_zakat_tax_customs_committees_rules_track.py",
    "scripts/gen_official_communications_records_regulation_track.py",
    "scripts/gen_housing_support_regulation_track.py",
    "scripts/gen_special_purpose_entities_rules_track.py",
    "scripts/gen_medical_devices_regulation_track.py",
    "scripts/gen_financial_institutions_resolution_law_track.py",
    "scripts/gen_trade_remedies_law_track.py",
    "scripts/gen_trade_remedies_regulation_track.py",
    "scripts/gen_financial_fraud_law_track.py",
    "scripts/gen_state_property_lease_law_track.py",
    "scripts/gen_state_property_lease_regulation_track.py",
    "scripts/gen_job_discipline_law_track.py",
    "scripts/gen_statistics_law_track.py",
    "scripts/gen_anti_begging_law_track.py",
    "scripts/gen_security_cameras_law_track.py",
    "scripts/gen_antiquities_heritage_regulation_track.py",
    "scripts/gen_meteorology_law_track.py",
    "scripts/gen_handicrafts_regulation_track.py",
    "scripts/gen_donations_collection_regulation_track.py",
    "scripts/gen_falcon_center_statute_track.py",
    "scripts/gen_geographical_indications_regulation_track.py",
    "scripts/gen_vacant_properties_fees_regulation_track.py",
    "scripts/gen_waqf_investment_products_regulation_track.py",
    "scripts/gen_insurance_disputes_committees_rules_track.py",
    "scripts/gen_entertainment_activities_law_track.py",
    "scripts/gen_standards_quality_regulation_track.py",
    "scripts/gen_disability_rights_regulation_track.py",
    "scripts/gen_anti_smoking_regulation_track.py",
    "scripts/gen_general_education_law_track.py",
    "scripts/gen_credit_information_law_track.py",
    "scripts/gen_real_estate_brokerage_law_track.py",
    "scripts/gen_state_revenue_law_track.py",
    "scripts/gen_etec_law_track.py",
    "scripts/gen_einvoicing_regulation_track.py",
    "scripts/gen_pdpl_cross_border_transfer_regulation_track.py",
    "scripts/gen_sdaia_organizational_arrangements_track.py",
    "scripts/gen_trade_names_regulation_track.py",
    "scripts/gen_commercial_agencies_regulation_track.py",
    "scripts/gen_accounting_auditing_regulation_track.py",
    "scripts/gen_commercial_register_regulation_track.py",
    "scripts/gen_real_estate_brokerage_regulation_track.py",
    "scripts/gen_foreign_ownership_regulation_track.py",
    "scripts/gen_anti_fraud_regulation_track.py",
    "scripts/gen_rett_regulation_track.py",
    "scripts/gen_anti_narcotics_regulation_track.py",
    "scripts/gen_anti_concealment_regulation_track.py",
    "scripts/gen_privatization_regulation_track.py",
    "scripts/gen_chambers_of_commerce_regulation_track.py",
    "scripts/gen_state_revenue_regulation_track.py",
    "scripts/gen_weapons_ammunition_regulation_track.py",
    "scripts/gen_engineering_practice_regulation_track.py",
    "scripts/gen_allegiance_commission_regulation_track.py",
    "scripts/gen_social_insurance_regulation_track.py",
    "scripts/gen_saudi_engineers_regulation_track.py",
    "scripts/gen_child_protection_regulation_track.py",
    "scripts/gen_whistleblower_regulation_track.py",
    "scripts/gen_social_insurance_legacy_regulation_track.py",
    "scripts/gen_protection_from_abuse_regulation_track.py",
    "scripts/gen_healthcare_professions_regulation_track.py",
    "scripts/gen_shura_council_internal_regulation_track.py",
    "scripts/gen_civil_service_regulation_track.py",
    "scripts/gen_associations_ngo_regulation_track.py",
    "scripts/gen_electronic_transactions_regulation_track.py",
    "scripts/gen_electricity_regulation_track.py",
    "scripts/gen_maritime_commercial_regulation_track.py",
    "scripts/gen_agriculture_regulation_track.py",
    "scripts/gen_civil_defense_regulation_track.py",
    "scripts/gen_premium_residency_regulation_track.py",
    "scripts/gen_water_regulation_track.py",
    "scripts/gen_press_regulation_track.py",
    "scripts/gen_building_code_regulation_track.py",
    "scripts/gen_telecommunications_regulation_track.py",
    "scripts/gen_credit_information_regulation_track.py",
    "scripts/gen_payment_systems_regulation_track.py",
    "scripts/gen_banking_control_regulation_track.py",
    "scripts/gen_finance_companies_regulation_track.py",
    "scripts/gen_finance_lease_regulation_track.py",
    "scripts/gen_cooperative_societies_regulation_track.py",
    "scripts/gen_bog_enforcement_law_track.py",
    "scripts/gen_public_prosecution_law_track.py",
    "scripts/gen_elderly_care_law_track.py",
    "scripts/gen_elderly_care_regulation_track.py",
    "scripts/gen_private_schools_regulation_track.py",
    "scripts/gen_foreign_schools_regulation_track.py",
    "scripts/gen_postal_law_track.py",
    "scripts/gen_cma_corporate_governance_regulation_track.py",
    "scripts/gen_tvtc_organizational_statute_track.py",
    "scripts/gen_waste_management_law_track.py",
    "scripts/gen_fisheries_law_track.py",
    "scripts/gen_debt_collection_regulation_track.py",
    "scripts/gen_insurance_authority_statute_track.py",
    "scripts/gen_bnpl_regulation_track.py",
    "scripts/gen_offplan_sale_law_track.py",
    "scripts/gen_contractors_classification_law_track.py",
    "scripts/gen_real_estate_contributions_law_track.py",
    "scripts/gen_accredited_valuers_law_track.py",
    "scripts/gen_white_land_fees_law_track.py",
    "scripts/gen_frequency_spectrum_regulation_track.py",
    "scripts/gen_mental_health_law_track.py",
    "scripts/gen_organ_donation_law_track.py",
    "scripts/gen_private_healthcare_institutions_law_track.py",
    "scripts/gen_high_risk_professions_regulation_track.py",
    "scripts/gen_osh_service_providers_regulation_track.py",
    "scripts/gen_rega_organizational_statute_track.py",
    "scripts/gen_offplan_sale_implementing_regulation_track.py",
    "scripts/gen_real_estate_finance_implementing_regulation_track.py",
    "scripts/gen_real_estate_contributions_implementing_regulation_track.py",
    "scripts/gen_landlord_tenant_relationship_regulation_track.py",
    "scripts/gen_real_estate_marketing_advertising_regulation_track.py",
    "scripts/gen_real_estate_auctions_regulation_track.py",
    "scripts/gen_petroleum_petrochemical_materials_law_track.py",
    "scripts/gen_dry_gas_lpg_distribution_law_track.py",
    "scripts/gen_energy_supplies_system_track.py",
    "scripts/gen_mining_investment_implementing_regulation_track.py",
    "scripts/gen_pharmaceutical_establishments_law_track.py",
    "scripts/gen_seized_confiscated_funds_management_system_track.py",
    "scripts/gen_nca_cybersecurity_violations_investigation_rules_track.py",
    "scripts/gen_nca_cybersecurity_violations_reporting_rules_track.py",
    "scripts/gen_cst_organizational_statute_track.py",
    "scripts/gen_railway_law_track.py",
    "scripts/gen_railway_law_implementing_regulation_track.py",
    "scripts/gen_road_transport_law_track.py",
    "scripts/gen_gaca_organizational_statute_track.py",
    "scripts/gen_tga_organizational_statute_track.py",
    "scripts/gen_mawani_organizational_statute_track.py",
    "scripts/gen_hajj_umrah_external_pilgrims_law_track.py",
    "scripts/gen_aviation_passenger_rights_regulation_track.py",
    "scripts/gen_corpus_unified_llm_index.py",
    "scripts/gen_corpus_registry.py",
    "scripts/gen_corpus_verification_tiers.py",
    "scripts/gen_corpus_supersession_graph.py",
    "scripts/gen_corpus_cross_reference_graph.py",
    "scripts/gen_corpus_glossary.py",
    "scripts/gen_corpus_schema_manifest.py",
    "scripts/gen_corpus_chunking_layer.py",
    "scripts/gen_corpus_freshness_manifest.py",
    "scripts/run_corpus_retrieval_eval.py",
]

# Raised from 900s on 2026-08-01. The retrieval-eval pass is O(queries x index
# records) and the corpus has grown to 437 tracks / 20,162 indexed records /
# 811 gold queries, so a single scoring pass now takes ~17 minutes and its
# validator runs one twice (committed-vs-fresh reproduction). At 900s the gate
# reported a TIMEOUT that looked like a validator failure but was purely the
# clock; the same validator passes standalone.
VALIDATOR_TIMEOUT = 3600
WORKERS = 4


def _run(cmd, timeout):
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=ROOT)
        return r.returncode, time.time() - t0, (r.stdout + r.stderr)
    except subprocess.TimeoutExpired:
        return "TIMEOUT", time.time() - t0, ""


def _tracked_state():
    r = subprocess.run(["git", "status", "--porcelain"], capture_output=True,
                       text=True, cwd=ROOT)
    return r.stdout


def phase_validators():
    scripts = sorted(os.path.relpath(p, ROOT).replace(os.sep, "/")
                     for p in glob.glob(os.path.join(ROOT, "scripts", "validate_*.py")))
    to_run = [s for s in scripts if s not in EXCLUDED]
    print("[1] VALIDATORS — %d discovered, %d excluded (%s)"
          % (len(scripts), len(EXCLUDED), "none" if not EXCLUDED else "; ".join(
              "%s: %s" % kv for kv in EXCLUDED.items())))
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(_run, [sys.executable, s], VALIDATOR_TIMEOUT): s for s in to_run}
        for fut in concurrent.futures.as_completed(futs):
            s = futs[fut]
            code, dt, out = fut.result()
            if code != 0:
                failures.append((s, code, out))
    for s, code, out in sorted(failures):
        print("    FAIL (%s) %s" % (code, s))
        tail = [ln for ln in out.strip().split("\n") if ln.strip()][-5:]
        for ln in tail:
            print("      | %s" % ln)
    print("    -> %d/%d passed" % (len(to_run) - len(failures), len(to_run)))
    return not failures


def phase_idempotence():
    print("[2] IDEMPOTENCE — %d deterministic generators" % len(IDEMPOTENT_GENERATORS))
    before = _tracked_state()
    failures = []
    for g in IDEMPOTENT_GENERATORS:
        code, dt, out = _run([sys.executable, g], VALIDATOR_TIMEOUT)
        if code != 0:
            failures.append("%s exited %s" % (g, code))
    after = _tracked_state()
    if after != before:
        changed = sorted(set(after.split("\n")) ^ set(before.split("\n")))
        failures.append("working tree changed after regeneration: %s"
                        % [c.strip() for c in changed if c.strip()][:8])
    for f in failures:
        print("    FAIL %s" % f)
    print("    -> %s" % ("clean (zero drift)" if not failures else "%d failure(s)" % len(failures)))
    return not failures


def phase_tests():
    print("[3] TESTS — full pytest suite")
    code, dt, out = _run([sys.executable, "-m", "pytest", "-q"], 1800)
    tail = [ln for ln in out.strip().split("\n") if ln.strip()][-1:]
    print("    -> %s (exit %s, %.0fs)" % (tail[0] if tail else "?", code, dt))
    return code == 0


def main():
    ap = argparse.ArgumentParser(description="Strict repository QA gate.")
    ap.add_argument("--no-tests", action="store_true",
                    help="skip phase 3 (pytest) when the caller runs it separately")
    args = ap.parse_args()

    print("=" * 64)
    print("STRICT QA GATE — saudi-legal-corpus-ai")
    print("=" * 64)
    t0 = time.time()
    ok1 = phase_validators()
    ok2 = phase_idempotence()
    ok3 = True if args.no_tests else phase_tests()
    print("=" * 64)
    verdict = ok1 and ok2 and ok3
    tests_label = "SKIPPED" if args.no_tests else ("PASS" if ok3 else "FAIL")
    print("QA GATE: %s  (validators=%s, idempotence=%s, tests=%s, %.0fs)"
          % ("PASS" if verdict else "FAIL",
             "PASS" if ok1 else "FAIL",
             "PASS" if ok2 else "FAIL",
             tests_label,
             time.time() - t0))
    print("=" * 64)
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
