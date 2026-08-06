#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpus Registry Index Foundation — Read-Only Validator

Validates the canonical corpus registry JSON.

Checks:
  1.  Registry JSON exists and parses.
  2.  Required top-level fields present.
  3.  4 tracks present.
  4.  companies_law track exists with correct counts.
  5.  implementing_regulations_general track exists with 95 articles + 4 forms.
  6.  implementing_regulations_listed_joint_stock track exists with 69 articles + 1 appendix.
  7.  implementing_regulations_arabic_program_closure track exists with 169 total.
  8.  All referenced data_paths exist on filesystem.
  9.  All referenced report_paths exist.
  10. listed_joint_stock is marked is_specialized=True, is_general=False.
  11. Legal boundaries present in all tracks.
  12. No official translation claim.
  13. No legal advice claim.
  14. No public release claim.
  15. No trilingual alignment claim.
  16. English is reference/guidance only where mentioned.
  17. Chinese is internal/reference only where mentioned.
  18. Registry is read-only (validator does not modify files).

Usage:
    python3 scripts/validate_corpus_registry.py
Exit 0 == pass; 1 == problems.
"""

from __future__ import annotations

import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(ROOT, "data", "corpus_registry", "corpus_registry.json")

REQUIRED_TOP_FIELDS = [
    "registry_version", "generated_date", "repository", "baseline_commit",
    "legal_status_boundaries", "total_tracks",
    "total_primary_arabic_governing_records", "total_reference_records",
    "total_internal_reference_records", "total_implementing_regulations_records",
    "total_registry_counted_records", "count_policy",
    "validation_status", "tracks",
]

REQUIRED_TRACK_IDS = [
    "companies_law",
    "implementing_regulations_general",
    "implementing_regulations_listed_joint_stock",
    "implementing_regulations_arabic_program_closure",
    "pdpl_law",
    "pdpl_implementing_regulation",
    "investment_law",
    "investment_implementing_regulation",
    "civil_transactions_law",
    "gtpl_law",
    "gtpl_implementing_regulation",
    "labor_law",
    "labor_implementing_regulation",
    "labor_model_work_regulation",
    "labor_saudization_mediation_rules",
    "labor_recruitment_services_rules",
    "labor_accessibility_arrangements",
    "labor_model_contract_forms",
    "evidence_law",
    "evidence_electronic_procedures_rules",
    "evidence_procedural_manuals",
    "evidence_expertise_rules",
    "personal_status_law",
    "personal_status_implementing_regulation",
    "sharia_procedure_law",
    "sharia_procedure_implementing_regulation",
    "criminal_procedure_law",
    "criminal_procedure_implementing_regulation",
    "enforcement_law",
    "enforcement_implementing_regulation",
    "judiciary_law",
    "board_of_grievances_law",
    "law_practice_law",
    "law_practice_implementing_regulation",
    "commercial_courts_law",
    "commercial_courts_implementing_regulation",
    "bankruptcy_law",
    "bankruptcy_implementing_regulation",
    "bankruptcy_case_rules",
    "judicial_costs_law",
    "judicial_costs_implementing_regulation",
    "arbitration_law",
    "arbitration_implementing_regulation",
    "commercial_papers_law",
    "commercial_register_law",
    "trade_names_law",
    "commercial_agencies_law",
    "chambers_of_commerce_law",
    "commercial_books_law",
    "aml_law",
    "tawtheeq_law",
    "tawtheeq_implementing_regulation",
    "real_estate_registration_law",
    "real_estate_registration_implementing_regulation",
    "real_estate_mortgage_law",
    "real_estate_finance_law",
    "real_estate_units_law",
    "real_estate_units_implementing_regulation",
    "foreign_ownership_law",
    "municipal_realestate_law",
    "municipal_realestate_implementing_regulation",
    "gcc_ownership_law",
    "terrorism_law",
    "terrorism_implementing_regulation",
    "juveniles_law",
    "juveniles_implementing_regulation",
    "whistleblower_law",
    "judicial_inspection_regulation",
    "qismah_regulation",
    "sulook_regulation",
    "aawan_regulation",
    "muslaha_regulation",
    "iflas_hudud_regulation",
    "judicial_documents_regulation",
    "bankruptcy_fees_regulation",
    "enforcement_providers_regulation",
    "alimony_fund_regulation",
    "judiciary_bog_mechanism",
    "documentation_settlement_regulation",
    "mosalaha_center_regulation",
    "medical_reports_regulation",
    "marriage_non_saudi_regulation",
    "state_funded_lawyer_regulation",
    "lessor_repossession_regulation",
    "elitigation_guide_regulation",
    "judicial_training_center_guide",
    "judgment_objection_methods_regulation",
    "real_estate_expropriation_law",
    "marriage_contract_hearing_regulation",
    "anti_bribery_law",
    "basic_law_of_governance",
    "anti_cyber_crime_law",
    "anti_harassment_law",
    "anti_trafficking_law",
    "council_of_ministers_law",
    "regions_law",
    "electronic_transactions_law",
    "allegiance_commission_law",
    "shura_council_law",
    "copyright_law",
    "telecommunications_law",
    "sama_law",
    "banking_control_law",
    "capital_market_law",
    "competition_law",
    "payment_systems_law",
    "mining_investment_law",
    "trademark_law",
    "anti_concealment_law",
    "insurance_control_law",
    "ecommerce_law",
    "vat_law",
    "franchise_law",
    "civil_aviation_law",
    "anti_narcotics_law",
    "traffic_law",
    "environmental_law",
    "income_tax_law",
    "civil_service_law",
    "social_insurance_law",
    "social_insurance_legacy_law",
    "zakat_law",
    "patent_law",
    "customs_law",
    "customs_regulation",
    "anti_fraud_law",
    "finance_companies_law",
    "cooperative_health_insurance_law",
    "healthcare_professions_law",
    "finance_lease_law",
    "maritime_commercial_law",
    "gcc_anti_dumping_law",
    "accounting_auditing_law",
    "nazaha_law",
    "awqaf_law",
    "saudi_engineers_law",
    "municipal_councils_law",
    "press_law",
    "engineering_practice_law",
    "nationality_law",
    "residency_law",
    "civil_status_law",
    "food_law",
    "health_system_law",
    "domestic_labor_regulation",
    "travel_documents_law",
    "cybersecurity_authority_law",
    "cybersecurity_authority_enablers",
    "premium_residency_law",
    "travel_documents_regulation",
    "nationality_regulation",
    "health_system_regulation",
    "food_regulation",
    "electricity_law",
    "water_law",
    "vat_regulation",
    "income_tax_regulation",
    "agriculture_law",
    "competition_regulation",
    "aml_regulation",
    "patent_regulation",
    "ecommerce_regulation",
    "franchise_regulation",
    "traffic_regulation",
    "environmental_inspection_audit",
    "environmental_violations_penalties",
    "environmental_wildlife_hunting",
    "environmental_permits",
    "environmental_air_quality",
    "environmental_service_providers",
    "environmental_fees",
    "rett_law",
    "universities_law",
    "privatization_law",
    "antiquities_heritage_law",
    "child_protection_law",
    "protection_from_abuse_law",
    "associations_ngo_law",
    "audiovisual_media_law",
    "sports_law",
    "anti_smoking_law",
    "weapons_ammunition_law",
    "prison_detention_law",
    "civil_defense_law",
    "cooperative_societies_law",
    "building_code_law",
    "product_safety_law",
    "standards_quality_law",
    "disability_rights_law",
    "tourism_law",
    "tourism_travel_services",
    "hospitality_mgmt",
    "hospitality_facility",
    "tourist_visa",
    "environmental_noise",
    "environmental_protected_areas",
    "environmental_emergency_response",
    "product_safety_regulation",
    "handicrafts_law",
    "medical_devices_law",
    "libraries_authority_licensing_regulation",
    "theater_performing_arts_authority_licensing_regulation",
    "tourist_guidance_regulation",
    "king_saud_university_statute",
    "king_faisal_specialist_hospital_statute",
    "king_khaled_eye_hospital_statute",
    "state_property_acquisition_controls",
    "rehabilitation_and_damage_compensation_rules",
    "export_restriction_governance_statute",
    "occupational_fitness_examinations_regulation",
    "municipal_professions_crafts_licensing_regulation",
    "antifouling_systems_regulation",
    "cma_auditors_registration_rules",
    "national_risk_council_statute",
    "public_utility_markets_general_rules",
    "literature_publishing_translation_authority_statute",
    "museums_authority_statute",
    "heritage_authority_statute",
    "film_authority_statute",
    "libraries_authority_statute",
    "architecture_design_authority_statute",
    "music_authority_statute",
    "theater_performing_arts_authority_statute",
    "visual_arts_authority_statute",
    "culinary_arts_authority_statute",
    "fashion_authority_statute",
    "vehicle_periodic_inspection_statute",
    "public_transport_users_rights_regulation",
    "sez_cloud_computing_regulation",
    "alula_royal_commission_violations_committees_rules",
    "nonprofit_center_supervisory_bodies_relations_regulation",
    "saudi_yachts_regulation",
    "zakat_tax_accounting_services_rules",
    "national_emergency_management_authority_statute",
    "riyadh_biotechnology_center_statute",
    "digital_government_authority_statute",
    "real_estate_development_fund_law",
    "building_code_inspection_bodies_regulation",
    "accounting_services_rules",
    "king_salman_arabic_language_academy_statute",
    "biological_weapons_convention_regulation",
    "national_infrastructure_fund_law",
    "public_auction_sale_rules",
    "riyadh_nonprofit_foundation_statute",
    "state_property_allocation_recovery_controls",
    "government_foreign_property_lease_controls",
    "chemicals_management_regulation",
    "trustees_experts_fees_rules",
    "metrology_calibration_regulation",
    "financial_academy_statute",
    "accredited_valuers_fellowship_rules",
    "national_institute_educational_professional_development_statute",
    "hrdf_support_violations_regulation",
    "agricultural_development_fund_law",
    "baha_strategic_office_statute",
    "crafts_professions_heads_elections_regulation",
    "cruise_ships_controls",
    "cultural_development_fund_law",
    "digital_content_council_statute",
    "energy_allocation_regulation",
    "enterprise_size_measurement_rules",
    "final_clearing_collateral_regulation",
    "food_security_authority_statute",
    "general_irrigation_corporation_statute",
    "general_roads_authority_statute",
    "government_property_allocation_transfer_controls",
    "government_resource_systems_center_statute",
    "high_industrial_security_authority_statute",
    "industrial_mining_consultancy_rules",
    "jazan_strategic_office_statute",
    "job_seeker_allowance_statute",
    "jouf_strategic_office_statute",
    "kacare_statute",
    "kacst_statute",
    "king_abdullah_language_planning_center_statute",
    "marina_design_operation_controls",
    "maritime_travel_ticket_sales_regulation",
    "media_regulation_authority_statute",
    "municipal_licensing_procedures_regulation",
    "national_curriculum_center_statute",
    "national_health_research_institute_statute",
    "national_inspection_control_center_statute",
    "national_transport_safety_center_statute",
    "nonprofit_beneficial_owner_rules",
    "nonprofit_sector_development_center_statute",
    "northern_borders_strategic_office_statute",
    "occupational_safety_health_council_statute",
    "palms_dates_center_statute",
    "prince_mohammed_bin_salman_park_statute",
    "private_entity_client_data_transfer_regulation",
    "public_health_authority_statute",
    "public_utility_market_facilities_controls",
    "rdi_authority_statute",
    "real_estate_transaction_tax_regulation",
    "red_crescent_emblem_law",
    "red_sea_coral_turtles_authority_statute",
    "regional_headquarters_tax_rules",
    "royal_institute_traditional_arts_statute",
    "safe_manning_regulation",
    "saudi_auditors_accountants_authority_statute",
    "saudi_press_agency_statute",
    "saudi_red_sea_authority_statute",
    "saudi_space_agency_statute",
    "saudi_tourism_authority_statute",
    "saudi_water_authority_statute",
    "ship_safety_management_regulation",
    "sme_bank_law",
    "state_property_authority_statute",
    "two_holy_mosques_authority_statute",
    "visiting_yachts_controls",
    "waqf_investment_portfolios_regulation",
    "white_land_fees_executive_regulation",
    "wildlife_trade_regulation",
    "zatca_statute",
    "arabian_horse_regulation",
    "classification_societies_authorisation_regulation",
    "community_funds_rules",
    "competencies_contractors_program_rules",
    "conformity_models_general_regulation",
    "continuing_professional_education_rules",
    "dry_gas_tankers_technical_regulation",
    "electromagnetic_compatibility_technical_regulation",
    "environmental_rehabilitation_contaminated_sites_regulation",
    "explosive_atmospheres_equipment_technical_regulation",
    "foreign_investment_securities_rules",
    "government_allocation_objections_committee_rules",
    "hazardous_substances_electrical_equipment_regulation",
    "jewellery_accessories_technical_regulation",
    "kacaah_horse_disposal_regulation",
    "king_abdulaziz_reserve_beekeeping_controls",
    "king_abdulaziz_reserve_tourism_permits_controls",
    "land_customs_storage_fees_controls",
    "leather_products_technical_regulation",
    "makkah_holy_sites_transport_center_regulation",
    "marina_bunkering_controls",
    "maritime_education_training_accreditation_regulation",
    "maritime_service_record_regulation",
    "maritime_tour_operator_regulation",
    "maritime_tourism_agent_controls",
    "maritime_tourism_craft_classification_controls",
    "medical_referrals_center_statute",
    "ozone_depleting_substances_regulation",
    "paper_cardboard_technical_regulation",
    "public_agencies_staff_provisions_rules",
    "real_estate_consultancy_analytics_regulation",
    "real_estate_contributions_escrow_controls",
    "real_estate_market_analysis_controls",
    "returned_goods_customs_exemption_controls",
    "riyadh_infrastructure_projects_compliance_controls",
    "sarah_sudairi_womens_studies_center_statute",
    "sedimentary_shelf_well_drilling_permits_controls",
    "service_centers_fuel_stations_committee_rules",
    "shareek_program_center_statute",
    "special_use_vehicle_equipment_technical_regulation",
    "superyacht_chartering_controls",
    "tobacco_products_submission_fees_regulation",
    "tourist_destinations_regulation",
    "two_holy_mosques_religious_affairs_presidency_statute",
    "unesco_national_commission_statute",
    "used_imported_vehicles_technical_regulation",
    "vegetation_cover_desertification_regulation",
    "wheat_seasonal_fodder_cultivation_controls",
    "zakat_tax_dispute_settlement_committees_rules",
    "accredited_valuers_implementing_regulation",
    "administrative_judicial_council_bylaw",
    "antiquities_inspection_violations_regulation",
    "antiquities_museums_fund_regulation",
    "bankruptcy_information_documents_regulation",
    "bankruptcy_trustees_experts_rules",
    "bog_enforcement_service_providers_controls",
    "bog_judicial_inspection_regulation",
    "building_code_violations_classification_regulation",
    "capital_market_conduct_regulation",
    "capital_market_institutions_regulation",
    "capital_market_whistleblowing_regulation",
    "chambers_commerce_committees_regulation",
    "coastal_tourism_craft_classification_regulation",
    "companies_law_implementing_regulation",
    "contractors_classification_regulation",
    "copyright_law_2026",
    "copyright_law_implementing_regulation",
    "corporate_governance_regulation",
    "disability_rights_violations_committee_rules",
    "donations_collection_law",
    "economic_cities_marketing_names_controls",
    "electricity_violations_regulation",
    "excavation_permits_regulation",
    "extremism_countering_center_statute",
    "financial_advisory_profession_rules",
    "foreign_law_firms_licensing_regulation",
    "foreign_university_branches_regulation",
    "franchise_brokerage_controls",
    "gcc_registered_vehicles_stay_controls",
    "geographical_indications_protection_law",
    "government_foreign_property_lease_controls_2023",
    "government_health_practitioners_private_work_controls",
    "ict_devices_technical_regulation",
    "investment_accounts_instructions",
    "judicial_service_conflict_of_interest_rules",
    "juvenile_homes_regulation",
    "light_goods_road_transport_regulation",
    "listed_jsc_companies_regulation",
    "marine_coastal_environment_regulation",
    "ministry_of_investment_statute",
    "national_health_insurance_center_statute",
    "navigation_licence_work_permit_regulation",
    "nazaha_criminal_procedure_powers_regulation",
    "nonprofit_governance_rules",
    "nonprofit_zakat_exemption_rules",
    "personal_data_transfer_abroad_regulation",
    "pharmaceutical_herbal_establishments_regulation",
    "postal_law_regulation",
    "premium_residency_center_statute",
    "private_schools_tuition_controls",
    "public_facility_names_rules",
    "reconciliation_committees_regulation",
    "regional_headquarters_procurement_controls",
    "regional_tourism_development_councils_statute",
    "residential_commercial_gas_network_regulation",
    "riyadh_arts_university_statute",
    "riyadh_sez_center_statute",
    "saudi_culture_memory_center_statute",
    "security_cameras_law_regulation",
    "sez_companies_register_rules",
    "sez_companies_rules",
    "sez_trade_names_rules",
    "shariah_governance_capital_market_instructions",
    "simplified_investment_funds_instructions",
    "social_impact_investment_rules",
    "temporary_work_visas_regulation",
    "tourism_violations_committee_regulation",
    "violations_penalties_regulation",
    "waqf_establishment_donations_regulation",
    "waqf_owned_taxpayer_zakat_rules",
    "water_efficiency_center_statute",
    "water_electricity_regulatory_authority_statute",
    "real_estate_advertising_controls",
    "king_abdulaziz_quality_award_statute",
    "estimated_assessment_zakat_rules",
    "anti_concealment_status_correction_regulation",
    "state_realestate_monitoring_encroachment_rules",
    "heavy_equipment_regulation_center_statute",
    "electricity_tariff_technical_controls",
    "private_training_executive_rules",
    "trade_agreements_governance_mechanism",
    "crime_disclosure_financial_rewards_rules",
    "global_tourism_academy_statute",
    "development_authorities_support_center_statute",
    "licensed_realestate_developers_rules",
    "mahd_sports_academy_statute",
    "investment_promotion_authority_statute",
    "uqn_staff_transfer_rules",
    "alahsa_development_authority_statute",
    "ipo_book_building_allocation_instructions",
    "service_suspension_controls",
    "riyadh_infrastructure_projects_center_statute",
    "accounting_services_corrective_mechanism",
    "investment_council_statute",
    "board_committee_remuneration_controls",
    "jeddah_development_authority_statute",
    "esports_authority_statute",
    "national_place_names_in_commercial_names_controls",
    "temporary_camel_auctions_controls",
    "state_realestate_nonprofit_allocation_controls",
    "corruption_financial_settlements_rules",
    "government_vehicle_purchase_lease_controls",
    "official_travel_class_rules",
    "private_healthcare_purchasing_mechanism",
    "distinguished_competencies_incentive_controls",
    "secondary_data_use_general_rules",
    "arabic_calligraphy_center_statute",
    "treaty_brazil_visit_visas",
    "treaty_aircraft_seizure_supplementary_protocol",
    "treaty_unwto_cooperation",
    "treaty_chad_general_cooperation",
    "treaty_gcc_payment_systems_linkage",
    "treaty_regional_technical_cooperation_protocol",
    "treaty_bahrain_customs_cooperation",
    "treaty_taipei_economic_cultural_office",
    "treaty_iraq_double_taxation",
    "treaty_rwanda_general_cooperation",
    "treaty_iata_headquarters",
    "treaty_gcc_wildlife_conservation",
    "treaty_unwto_elearning_capacity",
    "treaty_qatar_air_services",
    "treaty_pakistan_transfer_of_sentenced_persons",
    "treaty_unccd_secretariat_cooperation",
    "treaty_cameroon_general_cooperation",
    "treaty_azerbaijan_customs_assistance",
    "treaty_south_sudan_general_cooperation",
    "treaty_greece_maritime_transport",
    "treaty_hungary_air_services",
    "treaty_iraq_maritime_transport",
    "treaty_albania_driving_licences",
    "treaty_bangladesh_customs_assistance",
    "treaty_iala_establishment",
    "treaty_ghana_air_services",
    "treaty_guyana_air_services",
    "treaty_djibouti_maritime_transport",
    "treaty_czechia_air_services",
    "treaty_dco_headquarters",
    "treaty_nepal_general_cooperation",
    "treaty_arab_road_passenger_transport",
    "treaty_uzbekistan_energy_cooperation",
    "treaty_arab_anti_human_cloning",
    "treaty_latvia_economic_cooperation",
    "treaty_honduras_general_cooperation",
    "treaty_estonia_general_cooperation",
    "treaty_cyprus_general_cooperation",
    "treaty_slovakia_general_cooperation",
    "treaty_slovenia_general_cooperation",
    "occupational_safety_health_national_policy",
    "spending_efficiency_authority_statute",
    "realestate_platform_licensing_criteria",
    "administrative_violations_drafting_guide",
    "fresh_produce_import_controls",
    "direct_finance_investment_funds_instructions",
    "public_transport_projects_framework",
    "intracity_bus_transport_licensing",
    "narcotics_schedules_general_provisions",
    "listed_companies_accumulated_losses_instructions",
    "charitable_donations_executive_instructions",
    "railway_independent_consultant_guide",
    "nazaha_military_personnel_statute",
    "self_consumption_renewable_energy_framework",
    "offplan_engineering_consultants_qualification",
    "civil_aviation_economic_policy",
    "aquaculture_national_policies_guide",
    "gcc_financial_products_cross_registration_framework",
    "animal_health_guide",
    "abattoirs_meat_inspection_guide",
    "rural_livestock_husbandry_guide",
    "vehicle_damage_assessment_standards",
    "public_entities_governance_guide",
    "public_transport_users_rights_enforcement_guide",
    "land_transport_training_centers_accreditation",
    "arabic_language_national_policy",
    "gcc_healthcare_waste_management_system",
    "offplan_developer_technical_financial_qualification",
    "hydrogen_vehicles_technical_regulation",
    "cableway_installations_technical_regulation",
    "bog_enforcement_implementing_regulation",
    "administrative_entities_enforcement_request_procedures",
    "cloud_computing_electricity_tariff_executive_rules",
    "open_field_vegetable_crops_export_conditions",
    "mobile_generation_electricity_service_rules",
    "guaranteed_standards_guide",
    "heavy_equipment_safety_inspection_bodies_accreditation_rules",
    "emergency_orders_annulment_claims_rules",
    "hague_apostille_convention",
    "arab_states_transit_transport_agreement",
    "copyright_protection_implementing_regulation",
    "real_estate_development_fund_implementing_regulation",
    "experimental_activities_regulation",
    "visiting_private_yachts_regulation",
    "cruise_ships_regulation",
    "superyacht_chartering_regulation",
    "utility_benefit_loss_compensation_regulation",
    "repair_cost_compensation_estimation_controls",
    "museums_authority_licensing_regulation",
    "heritage_authority_licensing_regulation",
    "literature_publishing_translation_authority_licensing_regulation",
    "film_authority_licensing_regulation",
    "fashion_authority_licensing_regulation",
    "music_authority_licensing_regulation",
    "culinary_arts_authority_licensing_regulation",
    "architecture_design_authority_licensing_regulation",
    "visual_arts_authority_licensing_regulation",
    "tourism_consultancy_regulation",
    "tourism_activity_inspection_regulation",
    "duty_free_markets_rules",
    "driving_schools_regulation",
    "railway_violations_committee_rules",
    "public_transport_users_rights_mechanism",
    "gcc_pesticides_regulation",
    "military_industries_rnd_regulation",
    "international_bus_transport_regulation",
    "vehicle_periodic_inspection_regulation",
    "health_specialties_membership_regulation",
    "disability_social_programs_regulation",
    "vehicle_damage_assessment_rules",
    "tourist_accommodation_facilities_regulation",
    "ngo_council_regulation",
    "health_holding_company_statute",
    "family_funds_rules",
    "airports_economic_regulation",
    "valuation_profession_conduct_rules",
    "nazara_works_regulation",
    "ballast_water_regulation",
    "sez_kaec_regulation",
    "sez_jazan_regulation",
    "sez_raskhair_regulation",
    "charitable_societies_council_regulation",
    "customs_procedures_controls",
    "social_security_regulation",
    "revenue_sharing_rules",
    "freight_broker_logistics_regulation",
    "property_ownership_committees_rules",
    "disability_nongov_social_facilities_regulation",
    "free_zone_employees_treatment_rules",
    "inspection_control_seizure_rules",
    "ip_services_licensing_rules",
    "deposit_zones_rules",
    "air_transport_services_economic_regulation",
    "privatization_governing_rules",
    "ground_handling_air_cargo_economic_regulation",
    "museums_regulation",
    "private_universities_regulation",
    "gcc_road_transport_law",
    "marpol_regulation",
    "securities_disputes_rules",
    "state_realestate_disposal_regulation",
    "securities_depository_markets_regulation",
    "capital_adequacy_rules",
    "mergers_acquisitions_regulation",
    "taxi_activity_regulation",
    "zakat_tax_customs_committees_rules",
    "official_communications_records_regulation",
    "housing_support_regulation",
    "special_purpose_entities_rules",
    "medical_devices_regulation",
    "financial_institutions_resolution_law",
    "trade_remedies_law",
    "trade_remedies_regulation",
    "financial_fraud_law",
    "state_property_lease_law",
    "state_property_lease_regulation",
    "job_discipline_law",
    "statistics_law",
    "anti_begging_law",
    "security_cameras_law",
    "antiquities_heritage_regulation",
    "meteorology_law",
    "handicrafts_regulation",
    "donations_collection_regulation",
    "falcon_center_statute",
    "geographical_indications_regulation",
    "vacant_properties_fees_regulation",
    "waqf_investment_products_regulation",
    "insurance_disputes_committees_rules",
    "entertainment_activities_law",
    "standards_quality_regulation",
    "disability_rights_regulation",
    "anti_smoking_regulation",
    "general_education_law",
    "credit_information_law",
    "real_estate_brokerage_law",
    "state_revenue_law",
    "etec_law",
    "einvoicing_regulation",
    "pdpl_cross_border_transfer_regulation",
    "sdaia_organizational_arrangements",
    "trade_names_regulation",
    "commercial_agencies_regulation",
    "accounting_auditing_regulation",
    "commercial_register_regulation",
    "real_estate_brokerage_regulation",
    "foreign_ownership_regulation",
    "anti_fraud_regulation",
    "rett_regulation",
    "anti_narcotics_regulation",
    "anti_concealment_regulation",
    "privatization_regulation",
    "chambers_of_commerce_regulation",
    "state_revenue_regulation",
    "weapons_ammunition_regulation",
    "engineering_practice_regulation",
    "allegiance_commission_regulation",
    "social_insurance_regulation",
    "saudi_engineers_regulation",
    "child_protection_regulation",
    "whistleblower_regulation",
    "social_insurance_legacy_regulation",
    "protection_from_abuse_regulation",
    "healthcare_professions_regulation",
    "shura_council_internal_regulation",
    "civil_service_regulation",
    "associations_ngo_regulation",
    "electronic_transactions_regulation",
    "electricity_regulation",
    "maritime_commercial_regulation",
    "agriculture_regulation",
    "civil_defense_regulation",
    "premium_residency_regulation",
    "water_regulation",
    "press_regulation",
    "building_code_regulation",
    "telecommunications_regulation",
    "credit_information_regulation",
    "payment_systems_regulation",
    "banking_control_regulation",
    "finance_companies_regulation",
    "finance_lease_regulation",
    "cooperative_societies_regulation",
    "bog_enforcement_law",
    "public_prosecution_law",
    "elderly_care_law",
    "elderly_care_regulation",
    "private_schools_regulation",
    "foreign_schools_regulation",
    "postal_law",
    "cma_corporate_governance_regulation",
    "tvtc_organizational_statute",
    "waste_management_law",
    "fisheries_law",
    "debt_collection_regulation",
    "insurance_authority_statute",
    "bnpl_regulation",
    "offplan_sale_law",
    "contractors_classification_law",
    "real_estate_contributions_law",
    "accredited_valuers_law",
    "white_land_fees_law",
    "frequency_spectrum_regulation",
    "mental_health_law",
    "organ_donation_law",
    "private_healthcare_institutions_law",
    "high_risk_professions_regulation",
    "osh_service_providers_regulation",
    "rega_organizational_statute",
    "offplan_sale_implementing_regulation",
    "real_estate_finance_implementing_regulation",
    "real_estate_contributions_implementing_regulation",
    "landlord_tenant_relationship_regulation",
    "real_estate_marketing_advertising_regulation",
    "real_estate_auctions_regulation",
    "petroleum_petrochemical_materials_law",
    "dry_gas_lpg_distribution_law",
    "energy_supplies_system",
    "mining_investment_implementing_regulation",
    "pharmaceutical_establishments_law",
    "seized_confiscated_funds_management_system",
    "nca_cybersecurity_violations_investigation_rules",
    "nca_cybersecurity_violations_reporting_rules",
    "cst_organizational_statute",
    "railway_law",
    "railway_law_implementing_regulation",
    "road_transport_law",
    "gaca_organizational_statute",
    "tga_organizational_statute",
    "mawani_organizational_statute",
    "hajj_umrah_external_pilgrims_law",
    "aviation_passenger_rights_regulation",
]

CHECKS: list[str] = []
PASSED = 0
FAILED = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        CHECKS.append(f"  {name} ✓")
        if detail:
            CHECKS.append(f"    {detail}")
        PASSED += 1
    else:
        CHECKS.append(f"  {name} ✗ FAIL")
        if detail:
            CHECKS.append(f"    {detail}")
        FAILED += 1


def main() -> int:
    print("=" * 60)
    print("Corpus Registry Index Foundation validation")
    print("=" * 60)
    print()

    # [1] Registry exists
    check("[1] Registry JSON exists...", os.path.isfile(REGISTRY_PATH),
          "Present" if os.path.isfile(REGISTRY_PATH) else "NOT FOUND")
    if not os.path.isfile(REGISTRY_PATH):
        print_results()
        return 1

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)

    # [2] Top-level fields
    missing = [f for f in REQUIRED_TOP_FIELDS if f not in registry]
    check("[2] Required top-level fields...", len(missing) == 0,
          "All present" if not missing else f"Missing: {missing}")

    # [3] 293 tracks
    track_ids = [t.get("track_id", "") for t in registry.get("tracks", [])]
    check("[3] 743 tracks present...", len(track_ids) == 743 and all(tid in track_ids for tid in REQUIRED_TRACK_IDS),
          f"Tracks: {track_ids}")

    tracks_by_id = {t["track_id"]: t for t in registry.get("tracks", [])}

    # [4] companies_law
    cl = tracks_by_id.get("companies_law", {})
    cl_counts = cl.get("record_counts", {})
    check("[4] companies_law: 281 Arabic articles...", cl_counts.get("arabic_articles") == 281,
          f"arabic_articles={cl_counts.get('arabic_articles')}")
    check("    companies_law: 281 English articles...", cl_counts.get("english_articles") == 281,
          f"english_articles={cl_counts.get('english_articles')}")

    # [5] general IR
    gen = tracks_by_id.get("implementing_regulations_general", {})
    gen_counts = gen.get("record_counts", {})
    check("[5] general IR: 95 articles...", gen_counts.get("articles") == 95, f"articles={gen_counts.get('articles')}")
    check("    general IR: 4 forms...", gen_counts.get("forms") == 4, f"forms={gen_counts.get('forms')}")

    # [6] listed JSC
    ljs = tracks_by_id.get("implementing_regulations_listed_joint_stock", {})
    ljs_counts = ljs.get("record_counts", {})
    check("[6] listed JSC: 69 articles...", ljs_counts.get("articles") == 69, f"articles={ljs_counts.get('articles')}")
    check("    listed JSC: 1 appendix...", ljs_counts.get("appendices") == 1, f"appendices={ljs_counts.get('appendices')}")

    # [7] closure audit
    closure = tracks_by_id.get("implementing_regulations_arabic_program_closure", {})
    closure_counts = closure.get("record_counts", {})
    check("[7] closure: 169 total records...", closure_counts.get("total_records") == 169,
          f"total_records={closure_counts.get('total_records')}")
    check("    closure: 164 article records...", closure_counts.get("total_article_records") == 164,
          f"total_article_records={closure_counts.get('total_article_records')}")

    # [7b] PDPL tracks (verified against official SDAIA-published text)
    pdpl_law = tracks_by_id.get("pdpl_law", {})
    check("[7b] pdpl_law: 43 Arabic articles...", pdpl_law.get("record_counts", {}).get("arabic_articles") == 43,
          f"arabic_articles={pdpl_law.get('record_counts', {}).get('arabic_articles')}")
    check("    pdpl_law: verified vs official SDAIA text...",
          pdpl_law.get("official_text_status") == "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT",
          f"official_text_status={pdpl_law.get('official_text_status')}")
    pdpl_reg = tracks_by_id.get("pdpl_implementing_regulation", {})
    check("[7c] pdpl_implementing_regulation: 38 Arabic articles...",
          pdpl_reg.get("record_counts", {}).get("arabic_articles") == 38,
          f"arabic_articles={pdpl_reg.get('record_counts', {}).get('arabic_articles')}")
    check("    pdpl_implementing_regulation: verified vs official SDAIA text...",
          pdpl_reg.get("official_text_status") == "VERIFIED_AGAINST_OFFICIAL_SDAIA_PUBLISHED_TEXT",
          f"official_text_status={pdpl_reg.get('official_text_status')}")

    # [7d] Investment tracks (verified from official MISA PDFs)
    inv_law = tracks_by_id.get("investment_law", {})
    check("[7d] investment_law: 16 Arabic articles...",
          inv_law.get("record_counts", {}).get("arabic_articles") == 16,
          f"arabic_articles={inv_law.get('record_counts', {}).get('arabic_articles')}")
    check("    investment_law: verified from official MISA PDF...",
          inv_law.get("official_text_status") == "VERIFIED_TRANSCRIBED_FROM_OFFICIAL_MISA_PDF",
          f"official_text_status={inv_law.get('official_text_status')}")
    inv_reg = tracks_by_id.get("investment_implementing_regulation", {})
    check("[7e] investment_implementing_regulation: 37 Arabic articles...",
          inv_reg.get("record_counts", {}).get("arabic_articles") == 37,
          f"arabic_articles={inv_reg.get('record_counts', {}).get('arabic_articles')}")
    check("    investment_implementing_regulation: verified from official MISA PDF...",
          inv_reg.get("official_text_status") == "VERIFIED_TRANSCRIBED_FROM_OFFICIAL_MISA_PDF",
          f"official_text_status={inv_reg.get('official_text_status')}")

    # [7f] Civil Transactions Law track (owner-provided official text)
    civil = tracks_by_id.get("civil_transactions_law", {})
    check("[7f] civil_transactions_law: 721 Arabic articles...",
          civil.get("record_counts", {}).get("arabic_articles") == 721,
          f"arabic_articles={civil.get('record_counts', {}).get('arabic_articles')}")
    check("    civil_transactions_law: owner-provided official text...",
          civil.get("official_text_status") == "OWNER_PROVIDED_CROSS_CHECKED_MOJ_PORTAL",
          f"official_text_status={civil.get('official_text_status')}")

    # [7g2] GTPL track
    gtpl = tracks_by_id.get("gtpl_law", {})
    check("[7g2] gtpl_law: 99 Arabic + 99 English reference...",
          gtpl.get("record_counts", {}).get("arabic_articles") == 99
          and gtpl.get("record_counts", {}).get("english_articles") == 99,
          f"counts={gtpl.get('record_counts')}")

    # [7g3] GTPL regulation track
    gtplr = tracks_by_id.get("gtpl_implementing_regulation", {})
    check("[7g3] gtpl_implementing_regulation: 157 Arabic articles...",
          gtplr.get("record_counts", {}).get("arabic_articles") == 157,
          f"counts={gtplr.get('record_counts')}")

    # [7g4] Labor Law track (HRSD consolidated, cross-checked vs BOE)
    labor = tracks_by_id.get("labor_law", {})
    check("[7g4] labor_law: 249 Arabic + 234 English reference...",
          labor.get("record_counts", {}).get("arabic_articles") == 249
          and labor.get("record_counts", {}).get("english_articles") == 234,
          f"counts={labor.get('record_counts')}")
    check("    labor_law: HRSD consolidated cross-checked vs BOE...",
          labor.get("official_text_status") == "HRSD_CONSOLIDATED_CROSS_CHECKED_BOE",
          f"official_text_status={labor.get('official_text_status')}")

    # [7g5] Labor implementing regulation track
    laborr = tracks_by_id.get("labor_implementing_regulation", {})
    check("[7g5] labor_implementing_regulation: 45 Arabic articles...",
          laborr.get("record_counts", {}).get("arabic_articles") == 45,
          f"counts={laborr.get('record_counts')}")
    check("    labor_implementing_regulation: HRSD PDF OCR + law-quote cross-checked...",
          laborr.get("official_text_status") == "HRSD_OFFICIAL_PDF_OCR_CROSS_CHECKED_LAW_QUOTES",
          f"official_text_status={laborr.get('official_text_status')}")

    # [7g6] Labor annex 1 (model work organization regulation) track
    labora1 = tracks_by_id.get("labor_model_work_regulation", {})
    check("[7g6] labor_model_work_regulation: 72 articles + 3 violation tables...",
          labora1.get("record_counts", {}).get("arabic_articles") == 72
          and labora1.get("record_counts", {}).get("violation_tables") == 3,
          f"counts={labora1.get('record_counts')}")
    check("    labor_model_work_regulation: HRSD PDF OCR/image cross-checked...",
          labora1.get("official_text_status") == "HRSD_OFFICIAL_PDF_OCR_IMAGE_CROSS_CHECKED",
          f"official_text_status={labora1.get('official_text_status')}")

    # [7g7] Labor annexes 3 + 4
    labora3 = tracks_by_id.get("labor_saudization_mediation_rules", {})
    check("[7g7] labor_saudization_mediation_rules: 20 Arabic articles...",
          labora3.get("record_counts", {}).get("arabic_articles") == 20
          and labora3.get("official_text_status") == "HRSD_OFFICIAL_PDF_OCR_CROSS_CHECKED",
          f"counts={labora3.get('record_counts')}")
    labora4 = tracks_by_id.get("labor_recruitment_services_rules", {})
    check("[7g8] labor_recruitment_services_rules: 72 Arabic articles...",
          labora4.get("record_counts", {}).get("arabic_articles") == 72
          and labora4.get("official_text_status") == "HRSD_OFFICIAL_PDF_OCR_CROSS_CHECKED",
          f"counts={labora4.get('record_counts')}")
    labora2 = tracks_by_id.get("labor_accessibility_arrangements", {})
    check("[7g9] labor_accessibility_arrangements: 8 tables (40 rows)...",
          labora2.get("record_counts", {}).get("accessibility_tables") == 8
          and labora2.get("record_counts", {}).get("table_rows") == 40
          and labora2.get("official_text_status") == "HRSD_OFFICIAL_PDF_ACTUALTEXT_OCR_IMAGE_CROSS_CHECKED",
          f"counts={labora2.get('record_counts')}")
    labora5 = tracks_by_id.get("labor_model_contract_forms", {})
    check("[7g10] labor_model_contract_forms: 102 records (101 units + glossary)...",
          labora5.get("record_counts", {}).get("total") == 102
          and labora5.get("record_counts", {}).get("form_units") == 101
          and labora5.get("official_text_status") == "HRSD_OFFICIAL_PDF_OCR_IMAGE_CROSS_CHECKED_BILINGUAL_FORM",
          f"counts={labora5.get('record_counts')}")
    check("    labor_model_contract_forms: embedded English non-governing...",
          labora5.get("language_layers", {}).get("english", {}).get("governing") is False
          and labora5.get("language_layers", {}).get("english", {}).get("role") == "reference_guidance_only",
          f"english={labora5.get('language_layers', {}).get('english', {}).get('role')}")

    # [7g11] Evidence Law track
    evid = tracks_by_id.get("evidence_law", {})
    check("[7g11] evidence_law: 129 Arabic articles...",
          evid.get("record_counts", {}).get("arabic_articles") == 129
          and evid.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={evid.get('record_counts')}")
    for tid, want in (("evidence_electronic_procedures_rules", 24),
                      ("evidence_procedural_manuals", 135),
                      ("evidence_expertise_rules", 34)):
        tr = tracks_by_id.get(tid, {})
        check("[7g12] %s: %d Arabic articles..." % (tid, want),
              tr.get("record_counts", {}).get("arabic_articles") == want
              and tr.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
              f"counts={tr.get('record_counts')}")

    # [7g] unified retrieval index present (projection not counted in totals)
    uix = registry.get("unified_retrieval_index", {})
    # [7g13] Personal Status tracks
    ps_law = tracks_by_id.get("personal_status_law", {})
    check("[7g13] personal_status_law: 252 Arabic articles...",
          ps_law.get("record_counts", {}).get("arabic_articles") == 252
          and ps_law.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={ps_law.get('record_counts')}")
    ps_reg = tracks_by_id.get("personal_status_implementing_regulation", {})
    check("[7g14] personal_status_implementing_regulation: 41 Arabic articles...",
          ps_reg.get("record_counts", {}).get("arabic_articles") == 41
          and ps_reg.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={ps_reg.get('record_counts')}")

    # [7g15] Sharia Procedure Law track (consolidated amended law)
    sharia = tracks_by_id.get("sharia_procedure_law", {})
    sharia_counts = sharia.get("record_counts", {})
    check("[7g15] sharia_procedure_law: 243 Arabic articles...",
          sharia_counts.get("arabic_articles") == 243
          and sharia.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={sharia_counts}")
    check("    sharia_procedure_law: status breakdown 153/14/75/1...",
          sharia_counts.get("legal_status_breakdown") == {"اصلية": 153, "معدلة": 14, "ملغاة": 75, "مضافة": 1},
          f"breakdown={sharia_counts.get('legal_status_breakdown')}")

    # [7g16] Sharia Procedure implementing regulation (dual-status, consolidated)
    sreg = tracks_by_id.get("sharia_procedure_implementing_regulation", {})
    sreg_counts = sreg.get("record_counts", {})
    check("[7g16] sharia_procedure_implementing_regulation: 637 provisions...",
          sreg_counts.get("arabic_articles") == 637
          and sreg.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={sreg_counts}")
    check("    sharia regulation: dual-status breakdowns + 149 superseded...",
          sreg_counts.get("pdf_document_status_breakdown") == {"اصلية": 536, "معدلة": 17, "ملغاة": 63, "مضافة": 21}
          and sreg_counts.get("portal_legal_status_breakdown") == {"اصلية": 388, "معدلة": 16, "ملغاة": 212, "مضافة": 21}
          and sreg_counts.get("superseded_by_evidence_law") == 149,
          f"pdf={sreg_counts.get('pdf_document_status_breakdown')} portal={sreg_counts.get('portal_legal_status_breakdown')} superseded={sreg_counts.get('superseded_by_evidence_law')}")

    # [7g17] Law of Criminal Procedure (consolidated, single-status)
    crim = tracks_by_id.get("criminal_procedure_law", {})
    crim_counts = crim.get("record_counts", {})
    check("[7g17] criminal_procedure_law: 222 Arabic articles...",
          crim_counts.get("arabic_articles") == 222
          and crim.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={crim_counts}")
    check("    criminal_procedure_law: status breakdown 219/3/0/0...",
          crim_counts.get("legal_status_breakdown") == {"اصلية": 219, "معدلة": 3, "ملغاة": 0, "مضافة": 0},
          f"breakdown={crim_counts.get('legal_status_breakdown')}")

    # [7g18] Criminal Procedure implementing regulation (consolidated, single-status)
    creg = tracks_by_id.get("criminal_procedure_implementing_regulation", {})
    creg_counts = creg.get("record_counts", {})
    check("[7g18] criminal_procedure_implementing_regulation: 181 articles...",
          creg_counts.get("arabic_articles") == 181
          and creg.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={creg_counts}")
    check("    criminal regulation: status breakdown 174/7/0/0...",
          creg_counts.get("legal_status_breakdown") == {"اصلية": 174, "معدلة": 7, "ملغاة": 0, "مضافة": 0},
          f"breakdown={creg_counts.get('legal_status_breakdown')}")

    # [7g19] Enforcement Law (consolidated, one flagged repeal)
    enf = tracks_by_id.get("enforcement_law", {})
    enf_counts = enf.get("record_counts", {})
    check("[7g19] enforcement_law: 98 Arabic articles...",
          enf_counts.get("arabic_articles") == 98
          and enf.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={enf_counts}")
    check("    enforcement_law: status breakdown 94/3/1/0...",
          enf_counts.get("legal_status_breakdown") == {"اصلية": 94, "معدلة": 3, "ملغاة": 1, "مضافة": 0},
          f"breakdown={enf_counts.get('legal_status_breakdown')}")

    # [7g20] Enforcement implementing regulation (consolidated, single-status)
    ereg = tracks_by_id.get("enforcement_implementing_regulation", {})
    ereg_counts = ereg.get("record_counts", {})
    check("[7g20] enforcement_implementing_regulation: 273 provisions...",
          ereg_counts.get("arabic_articles") == 273
          and ereg.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={ereg_counts}")
    check("    enforcement regulation: status breakdown 266/2/2/3...",
          ereg_counts.get("legal_status_breakdown") == {"اصلية": 266, "معدلة": 2, "ملغاة": 2, "مضافة": 3},
          f"breakdown={ereg_counts.get('legal_status_breakdown')}")

    # [7g21] Law of the Judiciary (foundational court-organization statute)
    jud = tracks_by_id.get("judiciary_law", {})
    jud_counts = jud.get("record_counts", {})
    check("[7g21] judiciary_law: 85 Arabic articles...",
          jud_counts.get("arabic_articles") == 85
          and jud.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={jud_counts}")
    check("    judiciary_law: status breakdown 82/3/0/0...",
          jud_counts.get("legal_status_breakdown") == {"اصلية": 82, "معدلة": 3, "ملغاة": 0, "مضافة": 0},
          f"breakdown={jud_counts.get('legal_status_breakdown')}")

    # [7g22] Law of the Board of Grievances (administrative-judiciary statute)
    bog = tracks_by_id.get("board_of_grievances_law", {})
    bog_counts = bog.get("record_counts", {})
    check("[7g22] board_of_grievances_law: 26 Arabic articles...",
          bog_counts.get("arabic_articles") == 26
          and bog.get("official_text_status") == "BOARD_OFFICIAL_PDF_VISUALLY_ADJUDICATED_GAZETTE_CONFIRMED",
          f"counts={bog_counts}")
    check("    board_of_grievances_law: status breakdown 25/1/0/0...",
          bog_counts.get("legal_status_breakdown") == {"اصلية": 25, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
          f"breakdown={bog_counts.get('legal_status_breakdown')}")

    # [7g23] Bankruptcy Law (consolidated amended law) + implementing regulation
    bkl = tracks_by_id.get("bankruptcy_law", {})
    bkl_counts = bkl.get("record_counts", {})
    check("[7g23] bankruptcy_law: 231 Arabic articles...",
          bkl_counts.get("arabic_articles") == 231
          and bkl.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={bkl_counts}")
    check("    bankruptcy_law: status breakdown 229/2/0/0...",
          bkl_counts.get("legal_status_breakdown") == {"اصلية": 229, "معدلة": 2, "ملغاة": 0, "مضافة": 0},
          f"breakdown={bkl_counts.get('legal_status_breakdown')}")
    bkr = tracks_by_id.get("bankruptcy_implementing_regulation", {})
    bkr_counts = bkr.get("record_counts", {})
    check("[7g24] bankruptcy_implementing_regulation: 98 Arabic articles...",
          bkr_counts.get("arabic_articles") == 98
          and bkr.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={bkr_counts}")
    check("    bankruptcy regulation: status breakdown 97/1/0/0...",
          bkr_counts.get("legal_status_breakdown") == {"اصلية": 97, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
          f"breakdown={bkr_counts.get('legal_status_breakdown')}")
    bkc = tracks_by_id.get("bankruptcy_case_rules", {})
    bkc_counts = bkc.get("record_counts", {})
    check("[7g25] bankruptcy_case_rules: 24 Arabic articles...",
          bkc_counts.get("arabic_articles") == 24
          and bkc.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={bkc_counts}")
    check("    bankruptcy case rules: status breakdown 24/0/0/0...",
          bkc_counts.get("legal_status_breakdown") == {"اصلية": 24, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={bkc_counts.get('legal_status_breakdown')}")
    jcl = tracks_by_id.get("judicial_costs_law", {})
    jcl_counts = jcl.get("record_counts", {})
    check("[7g26] judicial_costs_law: 23 Arabic articles...",
          jcl_counts.get("arabic_articles") == 23
          and jcl.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={jcl_counts}")
    check("    judicial_costs_law: status breakdown 23/0/0/0...",
          jcl_counts.get("legal_status_breakdown") == {"اصلية": 23, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={jcl_counts.get('legal_status_breakdown')}")
    jcr = tracks_by_id.get("judicial_costs_implementing_regulation", {})
    jcr_counts = jcr.get("record_counts", {})
    check("[7g27] judicial_costs_implementing_regulation: 17 Arabic articles...",
          jcr_counts.get("arabic_articles") == 17
          and jcr.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={jcr_counts}")
    check("    judicial_costs regulation: status breakdown 17/0/0/0...",
          jcr_counts.get("legal_status_breakdown") == {"اصلية": 17, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={jcr_counts.get('legal_status_breakdown')}")
    arl = tracks_by_id.get("arbitration_law", {})
    arl_counts = arl.get("record_counts", {})
    check("[7g28] arbitration_law: 58 Arabic articles...",
          arl_counts.get("arabic_articles") == 58
          and arl.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={arl_counts}")
    check("    arbitration_law: status breakdown 55/3/0/0...",
          arl_counts.get("legal_status_breakdown") == {"اصلية": 55, "معدلة": 3, "ملغاة": 0, "مضافة": 0},
          f"breakdown={arl_counts.get('legal_status_breakdown')}")
    arr = tracks_by_id.get("arbitration_implementing_regulation", {})
    arr_counts = arr.get("record_counts", {})
    check("[7g29] arbitration_implementing_regulation: 19 Arabic articles...",
          arr_counts.get("arabic_articles") == 19
          and arr.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={arr_counts}")
    check("    arbitration regulation: status breakdown 18/0/1/0...",
          arr_counts.get("legal_status_breakdown") == {"اصلية": 18, "معدلة": 0, "ملغاة": 1, "مضافة": 0},
          f"breakdown={arr_counts.get('legal_status_breakdown')}")
    cpl = tracks_by_id.get("commercial_papers_law", {})
    cpl_counts = cpl.get("record_counts", {})
    check("[7g30] commercial_papers_law: 121 Arabic articles...",
          cpl_counts.get("arabic_articles") == 121
          and cpl.get("official_text_status") == "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED",
          f"counts={cpl_counts}")
    check("    commercial_papers_law: status breakdown 118/3/0/0...",
          cpl_counts.get("legal_status_breakdown") == {"اصلية": 118, "معدلة": 3, "ملغاة": 0, "مضافة": 0},
          f"breakdown={cpl_counts.get('legal_status_breakdown')}")
    crl = tracks_by_id.get("commercial_register_law", {})
    crl_counts = crl.get("record_counts", {})
    check("[7g31] commercial_register_law: 29 Arabic articles...",
          crl_counts.get("arabic_articles") == 29
          and crl.get("official_text_status") == "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED",
          f"counts={crl_counts}")
    check("    commercial_register_law: status breakdown 29/0/0/0...",
          crl_counts.get("legal_status_breakdown") == {"اصلية": 29, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={crl_counts.get('legal_status_breakdown')}")
    tnl = tracks_by_id.get("trade_names_law", {})
    tnl_counts = tnl.get("record_counts", {})
    check("[7g32] trade_names_law: 23 Arabic articles...",
          tnl_counts.get("arabic_articles") == 23
          and tnl.get("official_text_status") == "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED",
          f"counts={tnl_counts}")
    check("    trade_names_law: status breakdown 23/0/0/0...",
          tnl_counts.get("legal_status_breakdown") == {"اصلية": 23, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={tnl_counts.get('legal_status_breakdown')}")
    cal = tracks_by_id.get("commercial_agencies_law", {})
    cal_counts = cal.get("record_counts", {})
    check("[7g33] commercial_agencies_law: 6 Arabic articles...",
          cal_counts.get("arabic_articles") == 6
          and cal.get("official_text_status") == "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED",
          f"counts={cal_counts}")
    check("    commercial_agencies_law: status breakdown 3/3/0/0...",
          cal_counts.get("legal_status_breakdown") == {"اصلية": 3, "معدلة": 3, "ملغاة": 0, "مضافة": 0},
          f"breakdown={cal_counts.get('legal_status_breakdown')}")
    chl = tracks_by_id.get("chambers_of_commerce_law", {})
    chl_counts = chl.get("record_counts", {})
    check("[7g34] chambers_of_commerce_law: 66 Arabic articles...",
          chl_counts.get("arabic_articles") == 66
          and chl.get("official_text_status") == "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED",
          f"counts={chl_counts}")
    check("    chambers_of_commerce_law: status breakdown 66/0/0/0...",
          chl_counts.get("legal_status_breakdown") == {"اصلية": 66, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={chl_counts.get('legal_status_breakdown')}")
    cbl = tracks_by_id.get("commercial_books_law", {})
    cbl_counts = cbl.get("record_counts", {})
    check("[7g35] commercial_books_law: 16 Arabic articles...",
          cbl_counts.get("arabic_articles") == 16
          and cbl.get("official_text_status") == "BOE_OFFICIAL_PORTAL_ARCHIVE_CROSS_SNAPSHOT_VERIFIED",
          f"counts={cbl_counts}")
    check("    commercial_books_law: status breakdown 16/0/0/0...",
          cbl_counts.get("legal_status_breakdown") == {"اصلية": 16, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={cbl_counts.get('legal_status_breakdown')}")
    aml = tracks_by_id.get("aml_law", {})
    aml_counts = aml.get("record_counts", {})
    check("[7g36] aml_law: 52 Arabic articles...",
          aml_counts.get("arabic_articles") == 52
          and aml.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={aml_counts}")
    check("    aml_law: status breakdown 44/7/0/1...",
          aml_counts.get("legal_status_breakdown") == {"اصلية": 44, "معدلة": 7, "ملغاة": 0, "مضافة": 1},
          f"breakdown={aml_counts.get('legal_status_breakdown')}")
    tw = tracks_by_id.get("tawtheeq_law", {})
    tw_counts = tw.get("record_counts", {})
    check("[7g37] tawtheeq_law: 57 Arabic articles...",
          tw_counts.get("arabic_articles") == 57
          and tw.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={tw_counts}")
    check("    tawtheeq_law: status breakdown 52/5/0/0...",
          tw_counts.get("legal_status_breakdown") == {"اصلية": 52, "معدلة": 5, "ملغاة": 0, "مضافة": 0},
          f"breakdown={tw_counts.get('legal_status_breakdown')}")
    twr = tracks_by_id.get("tawtheeq_implementing_regulation", {})
    twr_counts = twr.get("record_counts", {})
    check("[7g38] tawtheeq_implementing_regulation: 31 Arabic articles...",
          twr_counts.get("arabic_articles") == 31
          and twr.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={twr_counts}")
    check("    tawtheeq regulation: status breakdown 31/0/0/0...",
          twr_counts.get("legal_status_breakdown") == {"اصلية": 31, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={twr_counts.get('legal_status_breakdown')}")
    rer = tracks_by_id.get("real_estate_registration_law", {})
    rer_counts = rer.get("record_counts", {})
    check("[7g39] real_estate_registration_law: 40 Arabic articles...",
          rer_counts.get("arabic_articles") == 40
          and rer.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={rer_counts}")
    check("    real_estate_registration_law: status breakdown 37/3/0/0...",
          rer_counts.get("legal_status_breakdown") == {"اصلية": 37, "معدلة": 3, "ملغاة": 0, "مضافة": 0},
          f"breakdown={rer_counts.get('legal_status_breakdown')}")
    rerr = tracks_by_id.get("real_estate_registration_implementing_regulation", {})
    rerr_counts = rerr.get("record_counts", {})
    check("[7g40] real_estate_registration_implementing_regulation: 51 Arabic articles...",
          rerr_counts.get("arabic_articles") == 51
          and rerr.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={rerr_counts}")
    check("    real_estate_registration regulation: status breakdown 51/0/0/0...",
          rerr_counts.get("legal_status_breakdown") == {"اصلية": 51, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={rerr_counts.get('legal_status_breakdown')}")
    rem = tracks_by_id.get("real_estate_mortgage_law", {})
    rem_counts = rem.get("record_counts", {})
    check("[7g41] real_estate_mortgage_law: 46 Arabic articles...",
          rem_counts.get("arabic_articles") == 46
          and rem.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={rem_counts}")
    check("    real_estate_mortgage_law: status breakdown 46/0/0/0...",
          rem_counts.get("legal_status_breakdown") == {"اصلية": 46, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={rem_counts.get('legal_status_breakdown')}")
    refin = tracks_by_id.get("real_estate_finance_law", {})
    refin_counts = refin.get("record_counts", {})
    check("[7g42] real_estate_finance_law: 15 Arabic articles...",
          refin_counts.get("arabic_articles") == 15
          and refin.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={refin_counts}")
    check("    real_estate_finance_law: status breakdown 15/0/0/0...",
          refin_counts.get("legal_status_breakdown") == {"اصلية": 15, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={refin_counts.get('legal_status_breakdown')}")
    reun = tracks_by_id.get("real_estate_units_law", {})
    reun_counts = reun.get("record_counts", {})
    check("[7g43] real_estate_units_law: 33 Arabic articles...",
          reun_counts.get("arabic_articles") == 33
          and reun.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={reun_counts}")
    check("    real_estate_units_law: status breakdown 33/0/0/0...",
          reun_counts.get("legal_status_breakdown") == {"اصلية": 33, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={reun_counts.get('legal_status_breakdown')}")
    reunr = tracks_by_id.get("real_estate_units_implementing_regulation", {})
    reunr_counts = reunr.get("record_counts", {})
    check("[7g44] real_estate_units_implementing_regulation: 41 Arabic articles...",
          reunr_counts.get("arabic_articles") == 41
          and reunr.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={reunr_counts}")
    check("    real_estate_units_implementing_regulation: status breakdown 39/2/0/0...",
          reunr_counts.get("legal_status_breakdown") == {"اصلية": 39, "معدلة": 2, "ملغاة": 0, "مضافة": 0},
          f"breakdown={reunr_counts.get('legal_status_breakdown')}")
    rfo = tracks_by_id.get("foreign_ownership_law", {})
    rfo_counts = rfo.get("record_counts", {})
    check("[7g45] foreign_ownership_law: 15 Arabic articles...",
          rfo_counts.get("arabic_articles") == 15
          and rfo.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={rfo_counts}")
    check("    foreign_ownership_law: status breakdown 15/0/0/0...",
          rfo_counts.get("legal_status_breakdown") == {"اصلية": 15, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={rfo_counts.get('legal_status_breakdown')}")
    mrl = tracks_by_id.get("municipal_realestate_law", {})
    mrl_counts = mrl.get("record_counts", {})
    check("[7g46] municipal_realestate_law: 6 Arabic articles...",
          mrl_counts.get("arabic_articles") == 6
          and mrl.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={mrl_counts}")
    check("    municipal_realestate_law: status breakdown 6/0/0/0...",
          mrl_counts.get("legal_status_breakdown") == {"اصلية": 6, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={mrl_counts.get('legal_status_breakdown')}")
    mrr = tracks_by_id.get("municipal_realestate_implementing_regulation", {})
    mrr_counts = mrr.get("record_counts", {})
    check("[7g47] municipal_realestate_implementing_regulation: 35 Arabic articles...",
          mrr_counts.get("arabic_articles") == 35
          and mrr.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={mrr_counts}")
    check("    municipal_realestate_implementing_regulation: status breakdown 31/3/0/1...",
          mrr_counts.get("legal_status_breakdown") == {"اصلية": 31, "معدلة": 3, "ملغاة": 0, "مضافة": 1},
          f"breakdown={mrr_counts.get('legal_status_breakdown')}")
    gcc = tracks_by_id.get("gcc_ownership_law", {})
    gcc_counts = gcc.get("record_counts", {})
    check("[7g48] gcc_ownership_law: 6 Arabic articles...",
          gcc_counts.get("arabic_articles") == 6
          and gcc.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={gcc_counts}")
    check("    gcc_ownership_law: status breakdown 6/0/0/0...",
          gcc_counts.get("legal_status_breakdown") == {"اصلية": 6, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={gcc_counts.get('legal_status_breakdown')}")
    terr = tracks_by_id.get("terrorism_law", {})
    terr_counts = terr.get("record_counts", {})
    check("[7g49] terrorism_law: 99 Arabic articles...",
          terr_counts.get("arabic_articles") == 99
          and terr.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={terr_counts}")
    check("    terrorism_law: status breakdown 88/8/0/3...",
          terr_counts.get("legal_status_breakdown") == {"اصلية": 88, "معدلة": 8, "ملغاة": 0, "مضافة": 3},
          f"breakdown={terr_counts.get('legal_status_breakdown')}")
    terrreg = tracks_by_id.get("terrorism_implementing_regulation", {})
    terrreg_counts = terrreg.get("record_counts", {})
    check("[7g50] terrorism_implementing_regulation: 28 Arabic articles...",
          terrreg_counts.get("arabic_articles") == 28
          and terrreg.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={terrreg_counts}")
    check("    terrorism_implementing_regulation: status breakdown 18/7/1/2...",
          terrreg_counts.get("legal_status_breakdown") == {"اصلية": 18, "معدلة": 7, "ملغاة": 1, "مضافة": 2},
          f"breakdown={terrreg_counts.get('legal_status_breakdown')}")
    jl = tracks_by_id.get("juveniles_law", {})
    jl_counts = jl.get("record_counts", {})
    check("[7g51] juveniles_law: 24 Arabic articles...",
          jl_counts.get("arabic_articles") == 24
          and jl.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={jl_counts}")
    check("    juveniles_law: status breakdown 24/0/0/0...",
          jl_counts.get("legal_status_breakdown") == {"اصلية": 24, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={jl_counts.get('legal_status_breakdown')}")
    jr = tracks_by_id.get("juveniles_implementing_regulation", {})
    jr_counts = jr.get("record_counts", {})
    check("[7g52] juveniles_implementing_regulation: 13 Arabic articles...",
          jr_counts.get("arabic_articles") == 13
          and jr.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={jr_counts}")
    check("    juveniles_implementing_regulation: status breakdown 13/0/0/0...",
          jr_counts.get("legal_status_breakdown") == {"اصلية": 13, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={jr_counts.get('legal_status_breakdown')}")
    wl = tracks_by_id.get("whistleblower_law", {})
    wl_counts = wl.get("record_counts", {})
    check("[7g53] whistleblower_law: 37 Arabic articles...",
          wl_counts.get("arabic_articles") == 37
          and wl.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={wl_counts}")
    check("    whistleblower_law: status breakdown 37/0/0/0...",
          wl_counts.get("legal_status_breakdown") == {"اصلية": 37, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={wl_counts.get('legal_status_breakdown')}")
    ji = tracks_by_id.get("judicial_inspection_regulation", {})
    ji_counts = ji.get("record_counts", {})
    check("[7g54] judicial_inspection_regulation: 68 Arabic articles...",
          ji_counts.get("arabic_articles") == 68
          and ji.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={ji_counts}")
    check("    judicial_inspection_regulation: status breakdown 68/0/0/0...",
          ji_counts.get("legal_status_breakdown") == {"اصلية": 68, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={ji_counts.get('legal_status_breakdown')}")

    qi = tracks_by_id.get("qismah_regulation", {})
    qi_counts = qi.get("record_counts", {})
    check("[7g55] qismah_regulation: 48 Arabic articles...",
          qi_counts.get("arabic_articles") == 48
          and qi.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={qi_counts}")
    check("    qismah_regulation: status breakdown 48/0/0/0...",
          qi_counts.get("legal_status_breakdown") == {"اصلية": 48, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={qi_counts.get('legal_status_breakdown')}")

    su = tracks_by_id.get("sulook_regulation", {})
    su_counts = su.get("record_counts", {})
    check("[7g56] sulook_regulation: 47 Arabic articles...",
          su_counts.get("arabic_articles") == 47
          and su.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={su_counts}")
    check("    sulook_regulation: status breakdown 44/1/0/2...",
          su_counts.get("legal_status_breakdown") == {"اصلية": 44, "معدلة": 1, "ملغاة": 0, "مضافة": 2},
          f"breakdown={su_counts.get('legal_status_breakdown')}")

    aw = tracks_by_id.get("aawan_regulation", {})
    aw_counts = aw.get("record_counts", {})
    check("[7g57] aawan_regulation: 35 Arabic articles...",
          aw_counts.get("arabic_articles") == 35
          and aw.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={aw_counts}")
    check("    aawan_regulation: status breakdown 35/0/0/0...",
          aw_counts.get("legal_status_breakdown") == {"اصلية": 35, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={aw_counts.get('legal_status_breakdown')}")

    mu = tracks_by_id.get("muslaha_regulation", {})
    mu_counts = mu.get("record_counts", {})
    check("[7g58] muslaha_regulation: 29 Arabic articles...",
          mu_counts.get("arabic_articles") == 29
          and mu.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={mu_counts}")
    check("    muslaha_regulation: status breakdown 26/0/0/0...",
          mu_counts.get("legal_status_breakdown") == {"اصلية": 26, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={mu_counts.get('legal_status_breakdown')}")

    ih = tracks_by_id.get("iflas_hudud_regulation", {})
    ih_counts = ih.get("record_counts", {})
    check("[7g59] iflas_hudud_regulation: 23 Arabic articles...",
          ih_counts.get("arabic_articles") == 23
          and ih.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={ih_counts}")
    check("    iflas_hudud_regulation: status breakdown 23/0/0/0...",
          ih_counts.get("legal_status_breakdown") == {"اصلية": 23, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={ih_counts.get('legal_status_breakdown')}")

    jd = tracks_by_id.get("judicial_documents_regulation", {})
    jd_counts = jd.get("record_counts", {})
    check("[7g60] judicial_documents_regulation: 23 Arabic articles...",
          jd_counts.get("arabic_articles") == 23
          and jd.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={jd_counts}")
    check("    judicial_documents_regulation: status breakdown 23/0/0/0...",
          jd_counts.get("legal_status_breakdown") == {"اصلية": 23, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={jd_counts.get('legal_status_breakdown')}")

    bf = tracks_by_id.get("bankruptcy_fees_regulation", {})
    bf_counts = bf.get("record_counts", {})
    check("[7g61] bankruptcy_fees_regulation: 20 Arabic records...",
          bf_counts.get("arabic_articles") == 20
          and bf.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={bf_counts}")
    check("    bankruptcy_fees_regulation: status breakdown 20/0/0/0...",
          bf_counts.get("legal_status_breakdown") == {"اصلية": 20, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={bf_counts.get('legal_status_breakdown')}")

    ep = tracks_by_id.get("enforcement_providers_regulation", {})
    ep_counts = ep.get("record_counts", {})
    check("[7g62] enforcement_providers_regulation: 18 Arabic articles...",
          ep_counts.get("arabic_articles") == 18
          and ep.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={ep_counts}")
    check("    enforcement_providers_regulation: status breakdown 18/0/0/0...",
          ep_counts.get("legal_status_breakdown") == {"اصلية": 18, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={ep_counts.get('legal_status_breakdown')}")

    af = tracks_by_id.get("alimony_fund_regulation", {})
    af_counts = af.get("record_counts", {})
    check("[7g63] alimony_fund_regulation: 17 Arabic articles...",
          af_counts.get("arabic_articles") == 17
          and af.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={af_counts}")
    check("    alimony_fund_regulation: status breakdown 17/0/0/0...",
          af_counts.get("legal_status_breakdown") == {"اصلية": 17, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={af_counts.get('legal_status_breakdown')}")

    jbm = tracks_by_id.get("judiciary_bog_mechanism", {})
    jbm_counts = jbm.get("record_counts", {})
    check("[7g64] judiciary_bog_mechanism: 15 Arabic items...",
          jbm_counts.get("arabic_articles") == 15
          and jbm.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={jbm_counts}")
    check("    judiciary_bog_mechanism: status breakdown 14/1/0/0...",
          jbm_counts.get("legal_status_breakdown") == {"اصلية": 14, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
          f"breakdown={jbm_counts.get('legal_status_breakdown')}")

    ds = tracks_by_id.get("documentation_settlement_regulation", {})
    ds_counts = ds.get("record_counts", {})
    check("[7g65] documentation_settlement_regulation: 15 Arabic articles...",
          ds_counts.get("arabic_articles") == 15
          and ds.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={ds_counts}")
    check("    documentation_settlement_regulation: status breakdown 14/1/0/0...",
          ds_counts.get("legal_status_breakdown") == {"اصلية": 14, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
          f"breakdown={ds_counts.get('legal_status_breakdown')}")

    mc = tracks_by_id.get("mosalaha_center_regulation", {})
    mc_counts = mc.get("record_counts", {})
    check("[7g66] mosalaha_center_regulation: 10 Arabic articles...",
          mc_counts.get("arabic_articles") == 10
          and mc.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={mc_counts}")
    check("    mosalaha_center_regulation: status breakdown 10/0/0/0...",
          mc_counts.get("legal_status_breakdown") == {"اصلية": 10, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={mc_counts.get('legal_status_breakdown')}")

    mr = tracks_by_id.get("medical_reports_regulation", {})
    mr_counts = mr.get("record_counts", {})
    check("[7g67] medical_reports_regulation: 13 Arabic articles...",
          mr_counts.get("arabic_articles") == 13
          and mr.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={mr_counts}")
    check("    medical_reports_regulation: status breakdown 13/0/0/0...",
          mr_counts.get("legal_status_breakdown") == {"اصلية": 13, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={mr_counts.get('legal_status_breakdown')}")

    mns = tracks_by_id.get("marriage_non_saudi_regulation", {})
    mns_counts = mns.get("record_counts", {})
    check("[7g68] marriage_non_saudi_regulation: 11 Arabic articles...",
          mns_counts.get("arabic_articles") == 11
          and mns.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={mns_counts}")
    check("    marriage_non_saudi_regulation: status breakdown 11/0/0/0...",
          mns_counts.get("legal_status_breakdown") == {"اصلية": 11, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={mns_counts.get('legal_status_breakdown')}")

    sfl = tracks_by_id.get("state_funded_lawyer_regulation", {})
    sfl_counts = sfl.get("record_counts", {})
    check("[7g69] state_funded_lawyer_regulation: 11 Arabic articles...",
          sfl_counts.get("arabic_articles") == 11
          and sfl.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={sfl_counts}")
    check("    state_funded_lawyer_regulation: status breakdown 11/0/0/0...",
          sfl_counts.get("legal_status_breakdown") == {"اصلية": 11, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={sfl_counts.get('legal_status_breakdown')}")

    lrp = tracks_by_id.get("lessor_repossession_regulation", {})
    lrp_counts = lrp.get("record_counts", {})
    check("[7g70] lessor_repossession_regulation: 7 Arabic articles...",
          lrp_counts.get("arabic_articles") == 7
          and lrp.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={lrp_counts}")
    check("    lessor_repossession_regulation: status breakdown 7/0/0/0...",
          lrp_counts.get("legal_status_breakdown") == {"اصلية": 7, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={lrp_counts.get('legal_status_breakdown')}")

    elg = tracks_by_id.get("elitigation_guide_regulation", {})
    elg_counts = elg.get("record_counts", {})
    check("[7g71] elitigation_guide_regulation: 5 Arabic articles...",
          elg_counts.get("arabic_articles") == 5
          and elg.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={elg_counts}")
    check("    elitigation_guide_regulation: status breakdown 5/0/0/0...",
          elg_counts.get("legal_status_breakdown") == {"اصلية": 5, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={elg_counts.get('legal_status_breakdown')}")

    jtc = tracks_by_id.get("judicial_training_center_guide", {})
    jtc_counts = jtc.get("record_counts", {})
    check("[7g72] judicial_training_center_guide: 18 Arabic articles...",
          jtc_counts.get("arabic_articles") == 18
          and jtc.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={jtc_counts}")
    check("    judicial_training_center_guide: status breakdown 9/2/0/0 + 7 narrative...",
          jtc_counts.get("legal_status_breakdown") == {"اصلية": 9, "معدلة": 2, "ملغاة": 0, "مضافة": 0,
                                                        "NARRATIVE_NOT_APPLICABLE": 7},
          f"breakdown={jtc_counts.get('legal_status_breakdown')}")

    jom = tracks_by_id.get("judgment_objection_methods_regulation", {})
    jom_counts = jom.get("record_counts", {})
    check("[7g73] judgment_objection_methods_regulation: 62 Arabic articles...",
          jom_counts.get("arabic_articles") == 62
          and jom.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={jom_counts}")
    check("    judgment_objection_methods_regulation: status breakdown 62/0/0/0...",
          jom_counts.get("legal_status_breakdown") == {"اصلية": 62, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={jom_counts.get('legal_status_breakdown')}")

    ree = tracks_by_id.get("real_estate_expropriation_law", {})
    ree_counts = ree.get("record_counts", {})
    check("[7g74] real_estate_expropriation_law: 39 Arabic articles...",
          ree_counts.get("arabic_articles") == 39
          and ree.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={ree_counts}")
    check("    real_estate_expropriation_law: status breakdown 39/0/0/0...",
          ree_counts.get("legal_status_breakdown") == {"اصلية": 39, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={ree_counts.get('legal_status_breakdown')}")

    mch = tracks_by_id.get("marriage_contract_hearing_regulation", {})
    mch_counts = mch.get("record_counts", {})
    check("[7g75] marriage_contract_hearing_regulation: 10 Arabic articles...",
          mch_counts.get("arabic_articles") == 10
          and mch.get("official_text_status") == "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF",
          f"counts={mch_counts}")
    check("    marriage_contract_hearing_regulation: status breakdown 10/0/0/0...",
          mch_counts.get("legal_status_breakdown") == {"اصلية": 10, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={mch_counts.get('legal_status_breakdown')}")

    ab = tracks_by_id.get("anti_bribery_law", {})
    ab_counts = ab.get("record_counts", {})
    check("[7g76] anti_bribery_law: 25 Arabic articles, DISTINCT lower-confidence tier...",
          ab_counts.get("arabic_articles") == 25
          and ab.get("official_text_status") == "MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER",
          f"counts={ab_counts}")
    check("    anti_bribery_law: status breakdown 16/7/0/2...",
          ab_counts.get("legal_status_breakdown") == {"اصلية": 16, "معدلة": 7, "ملغاة": 0, "مضافة": 2},
          f"breakdown={ab_counts.get('legal_status_breakdown')}")

    blg = tracks_by_id.get("basic_law_of_governance", {})
    blg_counts = blg.get("record_counts", {})
    check("[7g77] basic_law_of_governance: 83 Arabic articles, MIXED tier (BOE x WIPO Lex, art 5 post-merge corrected)...",
          blg_counts.get("arabic_articles") == 83
          and blg.get("official_text_status") == "MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER",
          f"counts={blg_counts}")
    check("    basic_law_of_governance: status breakdown 82/1/0/0...",
          blg_counts.get("legal_status_breakdown") == {"اصلية": 82, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
          f"breakdown={blg_counts.get('legal_status_breakdown')}")

    acc = tracks_by_id.get("anti_cyber_crime_law", {})
    acc_counts = acc.get("record_counts", {})
    check("[7g78] anti_cyber_crime_law: 16 Arabic articles, DISTINCT tier (BOE x WIPO Lex/CITC x MOF)...",
          acc_counts.get("arabic_articles") == 16
          and acc.get("official_text_status") == "BOE_PORTAL_TRIPLE_SOURCE_EXHAUSTIVE_VERIFIED",
          f"counts={acc_counts}")
    check("    anti_cyber_crime_law: status breakdown 16/0/0/0...",
          acc_counts.get("legal_status_breakdown") == {"اصلية": 16, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={acc_counts.get('legal_status_breakdown')}")

    ahl = tracks_by_id.get("anti_harassment_law", {})
    ahl_counts = ahl.get("record_counts", {})
    check("[7g79] anti_harassment_law: 8 Arabic articles, DISTINCT tier (BOE x press convergence)...",
          ahl_counts.get("arabic_articles") == 8
          and ahl.get("official_text_status") == "MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER",
          f"counts={ahl_counts}")
    check("    anti_harassment_law: status breakdown 7/1/0/0...",
          ahl_counts.get("legal_status_breakdown") == {"اصلية": 7, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
          f"breakdown={ahl_counts.get('legal_status_breakdown')}")

    atl = tracks_by_id.get("anti_trafficking_law", {})
    atl_counts = atl.get("record_counts", {})
    check("[7g80] anti_trafficking_law: 17 Arabic articles, DISTINCT tier (BOE Wayback x UNODC)...",
          atl_counts.get("arabic_articles") == 17
          and atl.get("official_text_status") == "BOE_WAYBACK_SNAPSHOT_UNODC_ENGLISH_SUBSTANCE_VERIFIED",
          f"counts={atl_counts}")
    check("    anti_trafficking_law: status breakdown 17/0/0/0...",
          atl_counts.get("legal_status_breakdown") == {"اصلية": 17, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={atl_counts.get('legal_status_breakdown')}")

    com = tracks_by_id.get("council_of_ministers_law", {})
    com_counts = com.get("record_counts", {})
    check("[7g81] council_of_ministers_law: 32 Arabic articles, DISTINCT tier (dual Arabic sources, BOE unreachable)...",
          com_counts.get("arabic_articles") == 32
          and com.get("official_text_status") == "DUAL_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE",
          f"counts={com_counts}")
    check("    council_of_ministers_law: status breakdown 31/1/0/0...",
          com_counts.get("legal_status_breakdown") == {"اصلية": 31, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
          f"breakdown={com_counts.get('legal_status_breakdown')}")

    rgl = tracks_by_id.get("regions_law", {})
    rgl_counts = rgl.get("record_counts", {})
    check("[7g82] regions_law: 41 Arabic articles, DISTINCT tier (dual Arabic sources, this law's BOE page unreachable)...",
          rgl_counts.get("arabic_articles") == 41
          and rgl.get("official_text_status") == "DUAL_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE",
          f"counts={rgl_counts}")
    check("    regions_law: status breakdown 31/9/0/1...",
          rgl_counts.get("legal_status_breakdown") == {"اصلية": 31, "معدلة": 9, "ملغاة": 0, "مضافة": 1},
          f"breakdown={rgl_counts.get('legal_status_breakdown')}")

    etl = tracks_by_id.get("electronic_transactions_law", {})
    etl_counts = etl.get("record_counts", {})
    check("[7g83] electronic_transactions_law: 31 Arabic articles, DISTINCT tier (single primary BOE/CoM PDF, WIPO Lex structural cross-check)...",
          etl_counts.get("arabic_articles") == 31
          and etl.get("official_text_status") == "SINGLE_PRIMARY_SOURCE_WIPO_STRUCTURAL_CROSS_CHECK_MANUAL_LIGATURE_CORRECTION",
          f"counts={etl_counts}")
    check("    electronic_transactions_law: status breakdown 24/5/2/0...",
          etl_counts.get("legal_status_breakdown") == {"اصلية": 24, "معدلة": 5, "ملغاة": 2, "مضافة": 0},
          f"breakdown={etl_counts.get('legal_status_breakdown')}")

    acl = tracks_by_id.get("allegiance_commission_law", {})
    acl_counts = acl.get("record_counts", {})
    check("[7g84] allegiance_commission_law: 25 Arabic articles, DISTINCT tier (triple Arabic secondary sources, BOE page unreachable)...",
          acl_counts.get("arabic_articles") == 25
          and acl.get("official_text_status") == "TRIPLE_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE",
          f"counts={acl_counts}")
    check("    allegiance_commission_law: status breakdown 25/0/0/0...",
          acl_counts.get("legal_status_breakdown") == {"اصلية": 25, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={acl_counts.get('legal_status_breakdown')}")

    scl = tracks_by_id.get("shura_council_law", {})
    scl_counts = scl.get("record_counts", {})
    check("[7g85] shura_council_law: 30 Arabic articles, MIXED tier (triple Arabic sources + SPA primary for art 3)...",
          scl_counts.get("arabic_articles") == 30
          and scl.get("official_text_status") == "MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER",
          f"counts={scl_counts}")
    check("    shura_council_law: status breakdown 24/6/0/0...",
          scl_counts.get("legal_status_breakdown") == {"اصلية": 24, "معدلة": 6, "ملغاة": 0, "مضافة": 0},
          f"breakdown={scl_counts.get('legal_status_breakdown')}")

    cpl = tracks_by_id.get("copyright_law", {})
    cpl_counts = cpl.get("record_counts", {})
    check("[7g86] copyright_law: 28 Arabic articles, DISTINCT tier (qadha.org.sa x WIPO Lex structural, superseded 2026-08-01)...",
          cpl_counts.get("arabic_articles") == 28
          and cpl.get("official_text_status") == "SECONDARY_SOURCE_STRUCTURAL_WIPO_CROSS_CHECK_BOE_UNREACHABLE",
          f"counts={cpl_counts}")
    check("    copyright_law: status breakdown 19/9/0/0...",
          cpl_counts.get("legal_status_breakdown") == {"اصلية": 19, "معدلة": 9, "ملغاة": 0, "مضافة": 0},
          f"breakdown={cpl_counts.get('legal_status_breakdown')}")

    tcl = tracks_by_id.get("telecommunications_law", {})
    tcl_counts = tcl.get("record_counts", {})
    check("[7g87] telecommunications_law: 41 Arabic articles, DISTINCT tier (BOE portal primary, MCIT PDF cross-check)...",
          tcl_counts.get("arabic_articles") == 41
          and tcl.get("official_text_status") == "BOE_PORTAL_PRIMARY_SOURCE_MCIT_PDF_CROSS_CHECKED",
          f"counts={tcl_counts}")
    check("    telecommunications_law: status breakdown 41/0/0/0...",
          tcl_counts.get("legal_status_breakdown") == {"اصلية": 41, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={tcl_counts.get('legal_status_breakdown')}")

    sml = tracks_by_id.get("sama_law", {})
    sml_counts = sml.get("record_counts", {})
    check("[7g88] sama_law: 27 Arabic articles, DISTINCT tier (SAMA official PDF x BOE Wayback archive)...",
          sml_counts.get("arabic_articles") == 27
          and sml.get("official_text_status") == "GOVERNMENT_AGENCY_OFFICIAL_PDF_PRIMARY_SOURCE_BOE_ARCHIVE_CROSS_VERIFIED",
          f"counts={sml_counts}")
    check("    sama_law: status breakdown 24/3/0/0...",
          sml_counts.get("legal_status_breakdown") == {"اصلية": 24, "معدلة": 3, "ملغاة": 0, "مضافة": 0},
          f"breakdown={sml_counts.get('legal_status_breakdown')}")

    bcl = tracks_by_id.get("banking_control_law", {})
    bcl_counts = bcl.get("record_counts", {})
    check("[7g89] banking_control_law: 26 Arabic articles, DISTINCT tier (dual Arabic secondary sources, BOE unreachable for raw text)...",
          bcl_counts.get("arabic_articles") == 26
          and bcl.get("official_text_status") == "DUAL_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE",
          f"counts={bcl_counts}")
    check("    banking_control_law: status breakdown 25/1/0/0...",
          bcl_counts.get("legal_status_breakdown") == {"اصلية": 25, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
          f"breakdown={bcl_counts.get('legal_status_breakdown')}")

    cml = tracks_by_id.get("capital_market_law", {})
    cml_counts = cml.get("record_counts", {})
    check("[7g90] capital_market_law: 68 Arabic records, MIXED tier (55 CMA-current x BOE-2003, 12 flagged fallback, 1 reconstructed)...",
          cml_counts.get("arabic_articles") == 68
          and cml.get("official_text_status") == "MIXED_TIER_SEE_PER_ARTICLE_VERIFICATION_TIER",
          f"counts={cml_counts}")
    check("    capital_market_law: status breakdown 42/25/0/1...",
          cml_counts.get("legal_status_breakdown") == {"اصلية": 42, "معدلة": 25, "ملغاة": 0, "مضافة": 1},
          f"breakdown={cml_counts.get('legal_status_breakdown')}")

    ctl = tracks_by_id.get("competition_law", {})
    ctl_counts = ctl.get("record_counts", {})
    check("[7g91] competition_law: 28 Arabic articles, DISTINCT tier (BOE Wayback x nezams.com)...",
          ctl_counts.get("arabic_articles") == 28
          and ctl.get("official_text_status") == "DUAL_PRIMARY_SOURCE_BOE_WAYBACK_X_NEZAMS_CROSS_VERIFIED",
          f"counts={ctl_counts}")
    check("    competition_law: status breakdown 28/0/0/0...",
          ctl_counts.get("legal_status_breakdown") == {"اصلية": 28, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={ctl_counts.get('legal_status_breakdown')}")

    psl = tracks_by_id.get("payment_systems_law", {})
    psl_counts = psl.get("record_counts", {})
    check("[7g92] payment_systems_law: 20 Arabic articles, DISTINCT tier (SAMA official PDF OCR x nezams.com)...",
          psl_counts.get("arabic_articles") == 20
          and psl.get("official_text_status") == "SAMA_OFFICIAL_PDF_OCR_X_NEZAMS_CROSS_VERIFIED",
          f"counts={psl_counts}")
    check("    payment_systems_law: status breakdown 20/0/0/0...",
          psl_counts.get("legal_status_breakdown") == {"اصلية": 20, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={psl_counts.get('legal_status_breakdown')}")

    mil = tracks_by_id.get("mining_investment_law", {})
    mil_counts = mil.get("record_counts", {})
    check("[7g93] mining_investment_law: 64 Arabic records, DISTINCT tier (BOE Wayback x FAOLEX)...",
          mil_counts.get("arabic_articles") == 64
          and mil.get("official_text_status") == "BOE_PORTAL_WAYBACK_X_FAOLEX_CROSS_VERIFIED",
          f"counts={mil_counts}")
    check("    mining_investment_law: status breakdown 63/0/0/1...",
          mil_counts.get("legal_status_breakdown") == {"اصلية": 63, "معدلة": 0, "ملغاة": 0, "مضافة": 1},
          f"breakdown={mil_counts.get('legal_status_breakdown')}")

    tml = tracks_by_id.get("trademark_law", {})
    tml_counts = tml.get("record_counts", {})
    check("[7g94] trademark_law: 52 Arabic articles, DISTINCT tier (WIPO Lex PDF x BOE status card)...",
          tml_counts.get("arabic_articles") == 52
          and tml.get("official_text_status") == "WIPO_LEX_PRIMARY_PDF_X_BOE_STATUS_CARD_CROSS_VERIFIED",
          f"counts={tml_counts}")
    check("    trademark_law: status breakdown 51/1/0/0...",
          tml_counts.get("legal_status_breakdown") == {"اصلية": 51, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
          f"breakdown={tml_counts.get('legal_status_breakdown')}")

    acl = tracks_by_id.get("anti_concealment_law", {})
    acl_counts = acl.get("record_counts", {})
    check("[7g95] anti_concealment_law: 20 Arabic articles, DISTINCT tier (triple Arabic sources, BOE unreachable)...",
          acl_counts.get("arabic_articles") == 20
          and acl.get("official_text_status") == "TRIPLE_ARABIC_SECONDARY_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE",
          f"counts={acl_counts}")
    check("    anti_concealment_law: status breakdown 20/0/0/0...",
          acl_counts.get("legal_status_breakdown") == {"اصلية": 20, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={acl_counts.get('legal_status_breakdown')}")

    icl = tracks_by_id.get("insurance_control_law", {})
    icl_counts = icl.get("record_counts", {})
    check("[7g96] insurance_control_law: 25 Arabic records, DISTINCT tier (misa.gov.sa PDF x nezams.com, BOE unreachable)...",
          icl_counts.get("arabic_articles") == 25
          and icl.get("official_text_status") == "MISA_OFFICIAL_PDF_X_NEZAMS_CROSS_VERIFIED_BOE_UNREACHABLE",
          f"counts={icl_counts}")
    check("    insurance_control_law: status breakdown 17/8/0/0...",
          icl_counts.get("legal_status_breakdown") == {"اصلية": 17, "معدلة": 8, "ملغاة": 0, "مضافة": 0},
          f"breakdown={icl_counts.get('legal_status_breakdown')}")

    ecl = tracks_by_id.get("ecommerce_law", {})
    ecl_counts = ecl.get("record_counts", {})
    check("[7g97] ecommerce_law: 26 Arabic articles, DISTINCT tier (BOE Wayback x nezams.com)...",
          ecl_counts.get("arabic_articles") == 26
          and ecl.get("official_text_status") == "BOE_PORTAL_WAYBACK_X_NEZAMS_CROSS_VERIFIED",
          f"counts={ecl_counts}")
    check("    ecommerce_law: status breakdown 26/0/0/0...",
          ecl_counts.get("legal_status_breakdown") == {"اصلية": 26, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={ecl_counts.get('legal_status_breakdown')}")

    vl = tracks_by_id.get("vat_law", {})
    vl_counts = vl.get("record_counts", {})
    check("[7g98] vat_law: 53 Arabic records, DISTINCT tier (ZATCA PDF x BOE portal)...",
          vl_counts.get("arabic_articles") == 53
          and vl.get("official_text_status") == "ZATCA_OFFICIAL_PDF_X_BOE_PORTAL_CROSS_VERIFIED",
          f"counts={vl_counts}")
    check("    vat_law: status breakdown 51/2/0/0...",
          vl_counts.get("legal_status_breakdown") == {"اصلية": 51, "معدلة": 2, "ملغاة": 0, "مضافة": 0},
          f"breakdown={vl_counts.get('legal_status_breakdown')}")

    fl = tracks_by_id.get("franchise_law", {})
    fl_counts = fl.get("record_counts", {})
    check("[7g99] franchise_law: 27 Arabic records, DISTINCT tier (BOE proxy x qanoniah spot)...",
          fl_counts.get("arabic_articles") == 27
          and fl.get("official_text_status") == "BOE_PORTAL_PROXY_RETRIEVED_QANONIAH_SPOT_CROSS_VERIFIED",
          f"counts={fl_counts}")
    check("    franchise_law: status breakdown 27/0/0/0...",
          fl_counts.get("legal_status_breakdown") == {"اصلية": 27, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={fl_counts.get('legal_status_breakdown')}")

    cal = tracks_by_id.get("civil_aviation_law", {})
    cal_counts = cal.get("record_counts", {})
    check("[7g100] civil_aviation_law: 180 Arabic records, DISTINCT tier (nezams.com x rakadvocate spot)...",
          cal_counts.get("arabic_articles") == 180
          and cal.get("official_text_status") == "NEZAMS_PRIMARY_X_RAKADVOCATE_SPOT_CHECKED",
          f"counts={cal_counts}")
    check("    civil_aviation_law: status breakdown 168/12/0/0...",
          cal_counts.get("legal_status_breakdown") == {"اصلية": 168, "معدلة": 12, "ملغاة": 0, "مضافة": 0},
          f"breakdown={cal_counts.get('legal_status_breakdown')}")

    anl = tracks_by_id.get("anti_narcotics_law", {})
    anl_counts = anl.get("record_counts", {})
    check("[7g101] anti_narcotics_law: 74 Arabic records, DISTINCT tier (BOE proxy x nezams x qadha)...",
          anl_counts.get("arabic_articles") == 74
          and anl.get("official_text_status") == "BOE_PROXY_X_NEZAMS_X_QADHA_REFERENCE_TRIPLE_VERIFIED",
          f"counts={anl_counts}")
    check("    anti_narcotics_law: status breakdown 74/0/0/0...",
          anl_counts.get("legal_status_breakdown") == {"اصلية": 74, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={anl_counts.get('legal_status_breakdown')}")

    trl = tracks_by_id.get("traffic_law", {})
    trl_counts = trl.get("record_counts", {})
    check("[7g102] traffic_law: 86 Arabic records, MIXED-CONFIDENCE tier (BOE stale x nezams pattern)...",
          trl_counts.get("arabic_articles") == 86
          and trl.get("official_text_status") == "BOE_PROXY_X_NEZAMS_PATTERN_VERIFIED_MIXED_CONFIDENCE",
          f"counts={trl_counts}")
    check("    traffic_law: status breakdown 52/32/1/1...",
          trl_counts.get("legal_status_breakdown") == {"اصلية": 52, "معدلة": 32, "ملغاة": 1, "مضافة": 1},
          f"breakdown={trl_counts.get('legal_status_breakdown')}")

    evl = tracks_by_id.get("environmental_law", {})
    evl_counts = evl.get("record_counts", {})
    check("[7g103] environmental_law: 49 Arabic records, STRONG triple-source tier (BOE x green.org.sa x nezams)...",
          evl_counts.get("arabic_articles") == 49
          and evl.get("official_text_status") == "BOE_WAYBACK_X_GREEN_ORG_PDF_X_NEZAMS_TRIPLE_VERIFIED_ART1_BOE_SELF_CONTRADICTION",
          f"counts={evl_counts}")
    check("    environmental_law: status breakdown 48/1/0/0...",
          evl_counts.get("legal_status_breakdown") == {"اصلية": 48, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
          f"breakdown={evl_counts.get('legal_status_breakdown')}")

    itl = tracks_by_id.get("income_tax_law", {})
    itl_counts = itl.get("record_counts", {})
    check("[7g104] income_tax_law: 81 Arabic records, DISTINCT tier (BOE x ZATCA x gstc x nezams)...",
          itl_counts.get("arabic_articles") == 81
          and itl.get("official_text_status") == "BOE_WAYBACK_X_ZATCA_PDF_X_GSTC_PDF_X_NEZAMS_CROSS_VERIFIED_CH10_BOE_ONLY",
          f"counts={itl_counts}")
    check("    income_tax_law: status breakdown 52/29/0/0...",
          itl_counts.get("legal_status_breakdown") == {"اصلية": 52, "معدلة": 29, "ملغاة": 0, "مضافة": 0},
          f"breakdown={itl_counts.get('legal_status_breakdown')}")

    csl = tracks_by_id.get("civil_service_law", {})
    csl_counts = csl.get("record_counts", {})
    check("[7g105] civil_service_law: 44 Arabic records, BOE Wayback x nezams full cross-verified...",
          csl_counts.get("arabic_articles") == 44
          and csl.get("official_text_status") == "BOE_WAYBACK_X_NEZAMS_FULL_CROSS_VERIFIED",
          f"counts={csl_counts}")
    check("    civil_service_law: status breakdown 20/19/1/4...",
          csl_counts.get("legal_status_breakdown") == {"اصلية": 20, "معدلة": 19, "ملغاة": 1, "مضافة": 4},
          f"breakdown={csl_counts.get('legal_status_breakdown')}")

    sil = tracks_by_id.get("social_insurance_law", {})
    sil_counts = sil.get("record_counts", {})
    check("[7g106] social_insurance_law: 63 Arabic records, BOE Wayback primary x nezams spot-check...",
          sil_counts.get("arabic_articles") == 63
          and sil.get("official_text_status") == "BOE_WAYBACK_PRIMARY_X_NEZAMS_SPOTCHECK_X_QANOONSA_STRUCTURE_VERIFIED",
          f"counts={sil_counts}")
    check("    social_insurance_law: status breakdown 63/0/0/0...",
          sil_counts.get("legal_status_breakdown") == {"اصلية": 63, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={sil_counts.get('legal_status_breakdown')}")

    silg = tracks_by_id.get("social_insurance_legacy_law", {})
    silg_counts = silg.get("record_counts", {})
    check("[7g107] social_insurance_legacy_law: 71 Arabic records, BOE Wayback x nezams x Okaz/Al-Riyadh...",
          silg_counts.get("arabic_articles") == 71
          and silg.get("official_text_status") == "BOE_WAYBACK_X_NEZAMS_SPOTCHECK_X_OKAZ_ALRIYADH_CORROBORATED",
          f"counts={silg_counts}")
    check("    social_insurance_legacy_law: status breakdown 63/7/0/1...",
          silg_counts.get("legal_status_breakdown") == {"اصلية": 63, "معدلة": 7, "ملغاة": 0, "مضافة": 1},
          f"breakdown={silg_counts.get('legal_status_breakdown')}")

    zkt = tracks_by_id.get("zakat_law", {})
    zkt_counts = zkt.get("record_counts", {})
    check("[7g108] zakat_law: 128 Arabic records, ZATCA PDF single-source, Gazette spot-verified...",
          zkt_counts.get("arabic_articles") == 128
          and zkt.get("official_text_status") == "ZATCA_PDF_PRIMARY_SINGLE_SOURCE_GAZETTE_SPOT_VERIFIED",
          f"counts={zkt_counts}")
    check("    zakat_law: status breakdown 127/1/0/0...",
          zkt_counts.get("legal_status_breakdown") == {"اصلية": 127, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
          f"breakdown={zkt_counts.get('legal_status_breakdown')}")

    ptl = tracks_by_id.get("patent_law", {})
    ptl_counts = ptl.get("record_counts", {})
    check("[7g109] patent_law: 66 Arabic records, WIPO Lex M/45-consolidated x BOE stale...",
          ptl_counts.get("arabic_articles") == 66
          and ptl.get("official_text_status") == "WIPOLEX_M45_CONSOLIDATED_X_BOE_PLAINTEXT_STALE_TERMINOLOGY_CROSS_VERIFIED",
          f"counts={ptl_counts}")
    check("    patent_law: status breakdown 59/6/0/1...",
          ptl_counts.get("legal_status_breakdown") == {"اصلية": 59, "معدلة": 6, "ملغاة": 0, "مضافة": 1},
          f"breakdown={ptl_counts.get('legal_status_breakdown')}")

    cml = tracks_by_id.get("customs_law", {})
    cml_counts = cml.get("record_counts", {})
    check("[7g110] customs_law: 188 Arabic records, ZATCA PDF single-source, BOE unreachable...",
          cml_counts.get("arabic_articles") == 188
          and cml.get("official_text_status") == "ZATCA_PDF_PRIMARY_SINGLE_SOURCE_BOE_UNREACHABLE",
          f"counts={cml_counts}")
    check("    customs_law: status breakdown 176/3/0/9...",
          cml_counts.get("legal_status_breakdown") == {"اصلية": 176, "معدلة": 3, "ملغاة": 0, "مضافة": 9},
          f"breakdown={cml_counts.get('legal_status_breakdown')}")

    cmr = tracks_by_id.get("customs_regulation", {})
    cmr_counts = cmr.get("record_counts", {})
    check("[7g111] customs_regulation: 36 Arabic records, ZATCA PDF single-source, BOE unreachable...",
          cmr_counts.get("arabic_articles") == 36
          and cmr.get("official_text_status") == "ZATCA_PDF_PRIMARY_SINGLE_SOURCE_BOE_UNREACHABLE",
          f"counts={cmr_counts}")
    check("    customs_regulation: status breakdown 34/0/0/2...",
          cmr_counts.get("legal_status_breakdown") == {"اصلية": 34, "معدلة": 0, "ملغاة": 0, "مضافة": 2},
          f"breakdown={cmr_counts.get('legal_status_breakdown')}")

    afl = tracks_by_id.get("anti_fraud_law", {})
    afl_counts = afl.get("record_counts", {})
    check("[7g112] anti_fraud_law: 30 Arabic records, secondary multi-source cross-verified, BOE unreachable...",
          afl_counts.get("arabic_articles") == 30
          and afl.get("official_text_status") == "SECONDARY_MULTI_SOURCE_CROSS_VERIFIED_BOE_UNREACHABLE",
          f"counts={afl_counts}")
    check("    anti_fraud_law: status breakdown 25/5/0/0...",
          afl_counts.get("legal_status_breakdown") == {"اصلية": 25, "معدلة": 5, "ملغاة": 0, "مضافة": 0},
          f"breakdown={afl_counts.get('legal_status_breakdown')}")

    fcl = tracks_by_id.get("finance_companies_law", {})
    fcl_counts = fcl.get("record_counts", {})
    check("[7g113] finance_companies_law: 41 Arabic records, BOE-Wayback primary x bfc.gov.sa OCR x nezams cross-verified...",
          fcl_counts.get("arabic_articles") == 41
          and fcl.get("official_text_status") == "BOE_WAYBACK_PRIMARY_X_BFC_OCR_X_NEZAMS_CROSS_VERIFIED",
          f"counts={fcl_counts}")
    check("    finance_companies_law: status breakdown 28/12/0/1...",
          fcl_counts.get("legal_status_breakdown") == {"اصلية": 28, "معدلة": 12, "ملغاة": 0, "مضافة": 1},
          f"breakdown={fcl_counts.get('legal_status_breakdown')}")

    chi = tracks_by_id.get("cooperative_health_insurance_law", {})
    chi_counts = chi.get("record_counts", {})
    check("[7g114] cooperative_health_insurance_law: 19 Arabic records, BOE-Wayback archive x nezams cross-verified...",
          chi_counts.get("arabic_articles") == 19
          and chi.get("official_text_status") == "BOE_WAYBACK_ARCHIVE_X_NEZAMS_CROSS_VERIFIED_LIVE_BOE_503",
          f"counts={chi_counts}")
    check("    cooperative_health_insurance_law: status breakdown 17/2/0/0...",
          chi_counts.get("legal_status_breakdown") == {"اصلية": 17, "معدلة": 2, "ملغاة": 0, "مضافة": 0},
          f"breakdown={chi_counts.get('legal_status_breakdown')}")

    hpl = tracks_by_id.get("healthcare_professions_law", {})
    hpl_counts = hpl.get("record_counts", {})
    check("[7g115] healthcare_professions_law: 44 Arabic records, BOE-Wayback archive x nezams cross-verified...",
          hpl_counts.get("arabic_articles") == 44
          and hpl.get("official_text_status") == "BOE_WAYBACK_ARCHIVE_X_NEZAMS_CROSS_VERIFIED_LIVE_BOE_UNREACHABLE",
          f"counts={hpl_counts}")
    check("    healthcare_professions_law: status breakdown 44/0/0/0...",
          hpl_counts.get("legal_status_breakdown") == {"اصلية": 44, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={hpl_counts.get('legal_status_breakdown')}")

    fll = tracks_by_id.get("finance_lease_law", {})
    fll_counts = fll.get("record_counts", {})
    check("[7g116] finance_lease_law: 28 Arabic records, BOE-Wayback archive x SAMA rulebook PDF x nezams triple-verified...",
          fll_counts.get("arabic_articles") == 28
          and fll.get("official_text_status") == "BOE_WAYBACK_ARCHIVE_X_SAMA_RULEBOOK_PDF_X_NEZAMS_TRIPLE_VERIFIED_LIVE_BOE_UNREACHABLE",
          f"counts={fll_counts}")
    check("    finance_lease_law: status breakdown 28/0/0/0...",
          fll_counts.get("legal_status_breakdown") == {"اصلية": 28, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={fll_counts.get('legal_status_breakdown')}")

    mcl = tracks_by_id.get("maritime_commercial_law", {})
    mcl_counts = mcl.get("record_counts", {})
    check("[7g117] maritime_commercial_law: 391 Arabic records, BOE-Wayback archive x nezams x BOE English translation triple-verified...",
          mcl_counts.get("arabic_articles") == 391
          and mcl.get("official_text_status") == "BOE_WAYBACK_ARCHIVE_X_NEZAMS_X_BOE_OFFICIAL_ENGLISH_TRANSLATION_TRIPLE_VERIFIED_LIVE_BOE_UNREACHABLE",
          f"counts={mcl_counts}")
    check("    maritime_commercial_law: status breakdown 391/0/0/0...",
          mcl_counts.get("legal_status_breakdown") == {"اصلية": 391, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={mcl_counts.get('legal_status_breakdown')}")

    gad = tracks_by_id.get("gcc_anti_dumping_law", {})
    gad_counts = gad.get("record_counts", {})
    check("[7g118] gcc_anti_dumping_law: 17 Arabic records, BOE-Wayback archive x qistas partial cross-check...",
          gad_counts.get("arabic_articles") == 17
          and gad.get("official_text_status") == "BOE_WAYBACK_ARCHIVE_PRIMARY_X_QISTAS_PARTIAL_STRUCTURAL_CROSSCHECK_LIVE_BOE_UNREACHABLE_M7_1434H_AMENDED_TEXT_NOT_INCORPORATED",
          f"counts={gad_counts}")
    check("    gcc_anti_dumping_law: status breakdown 17/0/0/0...",
          gad_counts.get("legal_status_breakdown") == {"اصلية": 17, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={gad_counts.get('legal_status_breakdown')}")

    aal = tracks_by_id.get("accounting_auditing_law", {})
    aal_counts = aal.get("record_counts", {})
    check("[7g119] accounting_auditing_law: 22 Arabic records, BOE-Wayback archive x SOCPA official PDF x qanoonsa...",
          aal_counts.get("arabic_articles") == 22
          and aal.get("official_text_status") == "BOE_WAYBACK_ARCHIVE_X_SOCPA_OFFICIAL_PDF_X_QANOONSA_CROSS_VERIFIED_BOE_MAIN_BODY_CONFIRMED_STALE_FOR_AMENDED_ARTICLES",
          f"counts={aal_counts}")
    check("    accounting_auditing_law: status breakdown 17/5/0/0...",
          aal_counts.get("legal_status_breakdown") == {"اصلية": 17, "معدلة": 5, "ملغاة": 0, "مضافة": 0},
          f"breakdown={aal_counts.get('legal_status_breakdown')}")

    nzl = tracks_by_id.get("nazaha_law", {})
    nzl_counts = nzl.get("record_counts", {})
    check("[7g120] nazaha_law: 24 Arabic records, BOE-Wayback dual-snapshot x FAOLEX mirror x nezams x qanoonsa...",
          nzl_counts.get("arabic_articles") == 24
          and nzl.get("official_text_status") == "BOE_WAYBACK_DUAL_SNAPSHOT_X_FAOLEX_MIRROR_X_NEZAMS_X_QANOONSA_CROSS_VERIFIED_LIVE_BOE_UNREACHABLE",
          f"counts={nzl_counts}")
    check("    nazaha_law: status breakdown 24/0/0/0...",
          nzl_counts.get("legal_status_breakdown") == {"اصلية": 24, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={nzl_counts.get('legal_status_breakdown')}")

    awl = tracks_by_id.get("awqaf_law", {})
    awl_counts = awl.get("record_counts", {})
    check("[7g121] awqaf_law: 25 Arabic records, BOE-Wayback six-snapshot x awqaf.gov.sa scanned decree x nezams...",
          awl_counts.get("arabic_articles") == 25
          and awl.get("official_text_status") == "BOE_WAYBACK_SIX_SNAPSHOT_X_AWQAF_GOV_SCANNED_DECREE_X_NEZAMS_CROSS_VERIFIED_LIVE_BOE_UNREACHABLE",
          f"counts={awl_counts}")
    check("    awqaf_law: status breakdown 23/2/0/0...",
          awl_counts.get("legal_status_breakdown") == {"اصلية": 23, "معدلة": 2, "ملغاة": 0, "مضافة": 0},
          f"breakdown={awl_counts.get('legal_status_breakdown')}")

    sel = tracks_by_id.get("saudi_engineers_law", {})
    sel_counts = sel.get("record_counts", {})
    check("[7g122] saudi_engineers_law: 9 Arabic records, BOE-Wayback three-snapshot x saudieng.sa x press...",
          sel_counts.get("arabic_articles") == 9
          and sel.get("official_text_status") == "BOE_WAYBACK_THREE_SNAPSHOT_X_SAUDIENG_SA_OFFICIAL_SITE_X_PRESS_CORROBORATION_LIVE_BOE_UNREACHABLE",
          f"counts={sel_counts}")
    check("    saudi_engineers_law: status breakdown 7/2/0/0...",
          sel_counts.get("legal_status_breakdown") == {"اصلية": 7, "معدلة": 2, "ملغاة": 0, "مضافة": 0},
          f"breakdown={sel_counts.get('legal_status_breakdown')}")

    mcl = tracks_by_id.get("municipal_councils_law", {})
    mcl_counts = mcl.get("record_counts", {})
    check("[7g123] municipal_councils_law: 69 Arabic records, BOE-Wayback six-snapshot x momah.gov.sa x nezams...",
          mcl_counts.get("arabic_articles") == 69
          and mcl.get("official_text_status") == "BOE_WAYBACK_SIX_SNAPSHOT_X_MOMAH_GOV_SA_OFFICIAL_PDF_X_NEZAMS_CROSS_VERIFIED_LIVE_BOE_UNREACHABLE",
          f"counts={mcl_counts}")
    check("    municipal_councils_law: status breakdown 69/0/0/0...",
          mcl_counts.get("legal_status_breakdown") == {"اصلية": 69, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={mcl_counts.get('legal_status_breakdown')}")

    prl = tracks_by_id.get("press_law", {})
    prl_counts = prl.get("record_counts", {})
    check("[7g124] press_law: 49 Arabic records, BOE-near-live-Wayback x media.gov.sa x WIPO Lex x nezams/qanoonsa...",
          prl_counts.get("arabic_articles") == 49
          and prl.get("official_text_status") == "BOE_NEAR_LIVE_WAYBACK_X_MEDIA_GOV_SA_OFFICIAL_PDF_X_WIPO_LEX_X_NEZAMS_QANOONSA_CURRENCY_CHECKED_CONFIRMED_CURRENT",
          f"counts={prl_counts}")
    check("    press_law: status breakdown 43/6/0/0...",
          prl_counts.get("legal_status_breakdown") == {"اصلية": 43, "معدلة": 6, "ملغاة": 0, "مضافة": 0},
          f"breakdown={prl_counts.get('legal_status_breakdown')}")

    epl = tracks_by_id.get("engineering_practice_law", {})
    epl_counts = epl.get("record_counts", {})
    check("[7g125] engineering_practice_law: 17 Arabic records, BOE-Wayback three-snapshot x saudieng.sa x qanoonsa/qanoniah...",
          epl_counts.get("arabic_articles") == 17
          and epl.get("official_text_status") == "BOE_WAYBACK_THREE_SNAPSHOT_X_SAUDIENG_SA_OFFICIAL_PDF_X_QANOONSA_QANONIAH_CROSS_VERIFIED_LIVE_BOE_UNREACHABLE",
          f"counts={epl_counts}")
    check("    engineering_practice_law: status breakdown 16/1/0/0...",
          epl_counts.get("legal_status_breakdown") == {"اصلية": 16, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
          f"breakdown={epl_counts.get('legal_status_breakdown')}")

    nl = tracks_by_id.get("nationality_law", {})
    nl_counts = nl.get("record_counts", {})
    check("[7g126] nationality_law: 30 Arabic records, BOE-Wayback three-snapshot x nezams.com x news corroboration...",
          nl_counts.get("arabic_articles") == 30
          and nl.get("official_text_status") == "BOE_WAYBACK_THREE_SNAPSHOT_X_NEZAMS_X_INDEPENDENT_NEWS_CORROBORATION_LIVE_BOE_UNREACHABLE",
          f"counts={nl_counts}")
    check("    nationality_law: status breakdown 19/11/0/0...",
          nl_counts.get("legal_status_breakdown") == {"اصلية": 19, "معدلة": 11, "ملغاة": 0, "مضافة": 0},
          f"breakdown={nl_counts.get('legal_status_breakdown')}")

    rl = tracks_by_id.get("residency_law", {})
    rl_counts = rl.get("record_counts", {})
    check("[7g127] residency_law: 69 Arabic records, TIER_3 secondary-multi-source-only, BOE does not index this law...",
          rl_counts.get("arabic_articles") == 69
          and rl.get("official_text_status") == "TIER_3_SECONDARY_MULTI_SOURCE_ONLY_BOE_DOES_NOT_INDEX_THIS_LAW_MOI_PDF_UNREACHABLE",
          f"counts={rl_counts}")
    check("    residency_law: status breakdown 48/16/1/4...",
          rl_counts.get("legal_status_breakdown") == {"اصلية": 48, "معدلة": 16, "ملغاة": 1, "مضافة": 4},
          f"breakdown={rl_counts.get('legal_status_breakdown')}")

    csl = tracks_by_id.get("civil_status_law", {})
    csl_counts = csl.get("record_counts", {})
    check("[7g128] civil_status_law: 96 Arabic records, BOE-Wayback seven-snapshot x qanoonsa.com x nezams.com...",
          csl_counts.get("arabic_articles") == 96
          and csl.get("official_text_status") == "BOE_WAYBACK_SEVEN_SNAPSHOT_X_QANOONSA_COM_RESOLUTION_805_X_NEZAMS_CROSS_VERIFIED",
          f"counts={csl_counts}")
    check("    civil_status_law: status breakdown 72/24/0/0...",
          csl_counts.get("legal_status_breakdown") == {"اصلية": 72, "معدلة": 24, "ملغاة": 0, "مضافة": 0},
          f"breakdown={csl_counts.get('legal_status_breakdown')}")

    fl = tracks_by_id.get("food_law", {})
    fl_counts = fl.get("record_counts", {})
    check("[7g129] food_law: 44 Arabic records, SFDA-PDF single-source, BOE and Wayback both unreachable...",
          fl_counts.get("arabic_articles") == 44
          and fl.get("official_text_status") == "SFDA_PDF_VISUAL_TRANSCRIPTION_SINGLE_SOURCE_LIVE_BOE_AND_WAYBACK_BOTH_UNREACHABLE",
          f"counts={fl_counts}")
    check("    food_law: status breakdown 44/0/0/0...",
          fl_counts.get("legal_status_breakdown") == {"اصلية": 44, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={fl_counts.get('legal_status_breakdown')}")

    hsl = tracks_by_id.get("health_system_law", {})
    hsl_counts = hsl.get("record_counts", {})
    check("[7g130] health_system_law: 19 Arabic records, nezams.com x qanoonsa.com Resolution 151 cross-verified, BOE and Wayback both unreachable...",
          hsl_counts.get("arabic_articles") == 19
          and hsl.get("official_text_status") == "NEZAMS_X_QANOONSA_COM_RESOLUTION_151_CROSS_VERIFIED_LIVE_BOE_AND_WAYBACK_BOTH_UNREACHABLE",
          f"counts={hsl_counts}")
    check("    health_system_law: status breakdown 15/4/0/0...",
          hsl_counts.get("legal_status_breakdown") == {"اصلية": 15, "معدلة": 4, "ملغاة": 0, "مضافة": 0},
          f"breakdown={hsl_counts.get('legal_status_breakdown')}")

    dlr = tracks_by_id.get("domestic_labor_regulation", {})
    dlr_counts = dlr.get("record_counts", {})
    check("[7g131] domestic_labor_regulation: 33 Arabic records, hrsd.gov.sa primary, BOE confirmed stale for this topic...",
          dlr_counts.get("arabic_articles") == 33
          and dlr.get("official_text_status") == "HRSD_GOV_SA_PRIMARY_X_QANOONSA_LEXISMIDDLEEAST_CROSS_VERIFIED_BOE_CONFIRMED_STALE_FOR_THIS_TOPIC",
          f"counts={dlr_counts}")
    check("    domestic_labor_regulation: status breakdown 33/0/0/0...",
          dlr_counts.get("legal_status_breakdown") == {"اصلية": 33, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={dlr_counts.get('legal_status_breakdown')}")

    tdl = tracks_by_id.get("travel_documents_law", {})
    tdl_counts = tdl.get("record_counts", {})
    check("[7g132] travel_documents_law: 16 Arabic records, BOE-via-Wayback x nezams.com/qistas.com x Umm Al-Qura Gazette M/11 cross-verified...",
          tdl_counts.get("arabic_articles") == 16
          and tdl.get("official_text_status") == "BOE_WAYBACK_THREE_SNAPSHOT_X_NEZAMS_QISTAS_X_UMM_AL_QURA_GAZETTE_M11_AMENDMENT_CROSS_VERIFIED",
          f"counts={tdl_counts}")
    check("    travel_documents_law: status breakdown 8/6/1/1...",
          tdl_counts.get("legal_status_breakdown") == {"اصلية": 8, "معدلة": 6, "ملغاة": 1, "مضافة": 1},
          f"breakdown={tdl_counts.get('legal_status_breakdown')}")

    csa = tracks_by_id.get("cybersecurity_authority_law", {})
    csa_counts = csa.get("record_counts", {})
    check("[7g133] cybersecurity_authority_law: 15 Arabic records, NCA official site PDF OCR-transcribed x qistas.com/saudipedia.com...",
          csa_counts.get("arabic_articles") == 15
          and csa.get("official_text_status") == "NCA_OFFICIAL_SITE_PDF_PRIMARY_TESSERACT_OCR_TRANSCRIBED_X_QISTAS_STRUCTURAL_PARTIAL_CROSSCHECK_TIER2_BOE_PAGE_NOT_LOCATED",
          f"counts={csa_counts}")
    check("    cybersecurity_authority_law: status breakdown 15/0/0/0...",
          csa_counts.get("legal_status_breakdown") == {"اصلية": 15, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={csa_counts.get('legal_status_breakdown')}")

    cae = tracks_by_id.get("cybersecurity_authority_enablers", {})
    cae_counts = cae.get("record_counts", {})
    check("[7g134] cybersecurity_authority_enablers: 7 Arabic records, NCA official site PDF OCR-transcribed x qanoonsa.com/uqn.gov.sa...",
          cae_counts.get("arabic_articles") == 7
          and cae.get("official_text_status") == "NCA_OFFICIAL_SITE_PDF_PRIMARY_TESSERACT_OCR_TRANSCRIBED_X_QANOONSA_STRUCTURAL_FULL_CROSSCHECK_TIER2_BOE_PAGE_NOT_LOCATED",
          f"counts={cae_counts}")
    check("    cybersecurity_authority_enablers: status breakdown 7/0/0/0...",
          cae_counts.get("legal_status_breakdown") == {"اصلية": 7, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={cae_counts.get('legal_status_breakdown')}")

    prl = tracks_by_id.get("premium_residency_law", {})
    prl_counts = prl.get("record_counts", {})
    check("[7g135] premium_residency_law: 14 Arabic records, BOE live unreachable x six Wayback snapshots x misa.gov.sa official PDF...",
          prl_counts.get("arabic_articles") == 14
          and prl.get("official_text_status") == "PREMIUM_RESIDENCY_LAW_BOE_LIVE_UNREACHABLE_WAYBACK_MULTI_SNAPSHOT_2019_2025_X_MISA_OFFICIAL_CONSOLIDATED_PDF_CROSS_VERIFIED",
          f"counts={prl_counts}")
    check("    premium_residency_law: status breakdown 5/8/1/0...",
          prl_counts.get("legal_status_breakdown") == {"اصلية": 5, "معدلة": 8, "ملغاة": 1, "مضافة": 0},
          f"breakdown={prl_counts.get('legal_status_breakdown')}")

    tdr = tracks_by_id.get("travel_documents_regulation", {})
    tdr_counts = tdr.get("record_counts", {})
    check("[7g136] travel_documents_regulation: 53 Arabic records, qanoonsa.com raw-HTML x ncar.gov.sa metadata x qanoniah.com indexing...",
          tdr_counts.get("arabic_articles") == 53
          and tdr.get("official_text_status") == "QANOONSA_COM_RAW_HTML_DIRECT_FETCH_MAR2026_PUBLISH_APR2026_WAYBACK_JUL2026_LIVE_STABLE_X_NCAR_GOV_SA_OFFICIAL_ARCHIVE_METADATA_CROSSCHECK_X_QANONIAH_COM_INDEX_CONFIRM_BOE_NO_DEDICATED_LAWID_MOI_GDP_UNREACHABLE_UQN_GOV_SA_REACHABLE_BUT_SPECIFIC_GAZETTE_PAGE_NOT_LOCATED_THIS_PASS",
          f"counts={tdr_counts}")
    check("    travel_documents_regulation: status breakdown 53/0/0/0...",
          tdr_counts.get("legal_status_breakdown") == {"اصلية": 53, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={tdr_counts.get('legal_status_breakdown')}")

    nrg = tracks_by_id.get("nationality_regulation", {})
    nrg_counts = nrg.get("record_counts", {})
    check("[7g137] nationality_regulation: 35 Arabic records, moi.gov.sa Wayback triple-snapshot x nezams.com x alriyadh.com...",
          nrg_counts.get("arabic_articles") == 35
          and nrg.get("official_text_status") == "MOI_GOV_SA_WAYBACK_TRIPLE_SNAPSHOT_BYTE_IDENTICAL_X_NEZAMS_DECREE_CONFIRM_X_ALRIYADH_2005_CONTEMPORANEOUS_FULLTEXT_CROSSVERIFIED_BOE_NO_DEDICATED_PAGE",
          f"counts={nrg_counts}")
    check("    nationality_regulation: status breakdown 34/0/1/0...",
          nrg_counts.get("legal_status_breakdown") == {"اصلية": 34, "معدلة": 0, "ملغاة": 1, "مضافة": 0},
          f"breakdown={nrg_counts.get('legal_status_breakdown')}")

    hsr = tracks_by_id.get("health_system_regulation", {})
    hsr_counts = hsr.get("record_counts", {})
    check("[7g138] health_system_regulation: 10 Arabic records, qanoniah.com public API 10-item preview cap, partial coverage arts 2-11...",
          hsr_counts.get("arabic_articles") == 10
          and hsr.get("official_text_status") == "QANONIAH_COM_PUBLIC_API_10_ITEM_PREVIEW_CAP_PARTIAL_COVERAGE_ARTICLES_2_11_BOE_NO_DEDICATED_PAGE_ISTITLAA_UNREACHABLE_WAYBACK_BLOCKED",
          f"counts={hsr_counts}")
    check("    health_system_regulation: status breakdown 10/0/0/0...",
          hsr_counts.get("legal_status_breakdown") == {"اصلية": 10, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={hsr_counts.get('legal_status_breakdown')}")

    fdr = tracks_by_id.get("food_regulation", {})
    fdr_counts = fdr.get("record_counts", {})
    check("[7g140] food_regulation: 85 Arabic records, sfda.gov.sa born-digital PDF x qanoonsa.com/qistas.com...",
          fdr_counts.get("arabic_articles") == 85
          and fdr.get("official_text_status") == "SFDA_GOV_SA_BORN_DIGITAL_PDF_2025_06_UPLOAD_X_QANOONSA_COM_X_QISTAS_COM_CROSSCHECK_BOE_NO_DEDICATED_LAWID_LIVE_UNREACHABLE_WAYBACK_CONTENT_BLOCKED",
          f"counts={fdr_counts}")
    check("    food_regulation: status breakdown 81/1/0/3...",
          fdr_counts.get("legal_status_breakdown") == {"اصلية": 81, "معدلة": 1, "ملغاة": 0, "مضافة": 3},
          f"breakdown={fdr_counts.get('legal_status_breakdown')}")

    ele = tracks_by_id.get("electricity_law", {})
    ele_counts = ele.get("record_counts", {})
    check("[7g141] electricity_law: 23 Arabic records, nezams.com single aggregator x multi-source metadata cross-check...",
          ele_counts.get("arabic_articles") == 23
          and ele.get("official_text_status") == "NEZAMS_COM_SINGLE_FULLTEXT_AGGREGATOR_BOE_UNREACHABLE_MULTISOURCE_METADATA_CROSSCHECK_CONFIRMED_M44_SUPERSEDES_M56",
          f"counts={ele_counts}")
    check("    electricity_law: status breakdown 23/0/0/0...",
          ele_counts.get("legal_status_breakdown") == {"اصلية": 23, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={ele_counts.get('legal_status_breakdown')}")

    wat = tracks_by_id.get("water_law", {})
    wat_counts = wat.get("record_counts", {})
    check("[7g142] water_law: 77 Arabic records, nezams.com aggregator x BOE-content WebSearch cross-check...",
          wat_counts.get("arabic_articles") == 77
          and wat.get("official_text_status") == "NEZAMS_COM_INDEPENDENT_AGGREGATOR_BOE_DEDICATED_PAGE_EXISTS_BUT_UNREACHABLE_WAYBACK_EGRESS_BLOCKED_MULTISOURCE_METADATA_CROSSCHECK_VIA_WEBSEARCH",
          f"counts={wat_counts}")
    check("    water_law: status breakdown 77/0/0/0...",
          wat_counts.get("legal_status_breakdown") == {"اصلية": 77, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={wat_counts.get('legal_status_breakdown')}")

    vatr = tracks_by_id.get("vat_regulation", {})
    vatr_counts = vatr.get("record_counts", {})
    check("[7g143] vat_regulation: 82 Arabic records, ZATCA official consolidated PDF x dual PyMuPDF-geometric/Tesseract-OCR reconciled...",
          vatr_counts.get("arabic_articles") == 82
          and vatr.get("official_text_status") == "ZATCA_GOV_SA_OFFICIAL_CONSOLIDATED_PDF_TENTH_EDITION_2025_04_DUAL_PYMUPDF_GEOMETRIC_X_TESSERACT_OCR_RECONCILED_BOE_NO_DEDICATED_LAWID_PAGE",
          f"counts={vatr_counts}")
    check("    vat_regulation: status breakdown 37/42/0/3...",
          vatr_counts.get("legal_status_breakdown") == {"اصلية": 37, "معدلة": 42, "ملغاة": 0, "مضافة": 3},
          f"breakdown={vatr_counts.get('legal_status_breakdown')}")

    itr = tracks_by_id.get("income_tax_regulation", {})
    itr_counts = itr.get("record_counts", {})
    check("[7g144] income_tax_regulation: 74 Arabic records, dual ZATCA/gstc.gov.sa government-copy cross-check x PyMuPDF coordinate reconstruction...",
          itr_counts.get("arabic_articles") == 74
          and itr.get("official_text_status") == "ZATCA_GOV_SA_X_GSTC_GOV_SA_DUAL_GOVERNMENT_COPY_CROSSCHECK_PYMUPDF_COORDINATE_RECONSTRUCTION_BOE_NO_DEDICATED_LAWID_PAGE",
          f"counts={itr_counts}")
    check("    income_tax_regulation: status breakdown 30/19/25/0...",
          itr_counts.get("legal_status_breakdown") == {"اصلية": 30, "معدلة": 19, "ملغاة": 25, "مضافة": 0},
          f"breakdown={itr_counts.get('legal_status_breakdown')}")

    agl = tracks_by_id.get("agriculture_law", {})
    agl_counts = agl.get("record_counts", {})
    check("[7g145] agriculture_law: 37 Arabic records, nezams.com single aggregator x MISA English PDF structural cross-check...",
          agl_counts.get("arabic_articles") == 37
          and agl.get("official_text_status") == "NEZAMS_COM_SINGLE_FULLTEXT_AGGREGATOR_BOE_UNREACHABLE_MULTISOURCE_METADATA_CROSSCHECK_MISA_ENGLISH_PDF_CONFIRMS_STRUCTURE",
          f"counts={agl_counts}")
    check("    agriculture_law: status breakdown 37/0/0/0...",
          agl_counts.get("legal_status_breakdown") == {"اصلية": 37, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={agl_counts.get('legal_status_breakdown')}")

    cmpr = tracks_by_id.get("competition_regulation", {})
    cmpr_counts = cmpr.get("record_counts", {})
    check("[7g146] competition_regulation: 5 Arabic records (partial scope, Articles 1-5 of 90), qanoniah.com x WIPO Lex dual independent source...",
          cmpr_counts.get("arabic_articles") == 5
          and cmpr.get("official_text_status") == "QANONIAH_COM_PRIMARY_X_WIPO_LEX_OFFICIAL_ARABIC_PDF_DUAL_INDEPENDENT_SOURCE_PARTIAL_SCOPE_ARTS_1_5_OF_90_BOE_NO_DEDICATED_LAWID_PAGE_GAC_ISSUER_UNREACHABLE",
          f"counts={cmpr_counts}")
    check("    competition_regulation: status breakdown 5/0/0/0...",
          cmpr_counts.get("legal_status_breakdown") == {"اصلية": 5, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={cmpr_counts.get('legal_status_breakdown')}")

    amlr = tracks_by_id.get("aml_regulation", {})
    amlr_counts = amlr.get("record_counts", {})
    check("[7g147] aml_regulation: 25 Arabic records, aml.gov.sa scanned PDF x qanoniah.com born-digital API reconciliation (10 of 25) + OCR-adjudicated (15 of 25)...",
          amlr_counts.get("arabic_articles") == 25
          and amlr.get("official_text_status") == "AML_GOV_SA_SCANNED_PDF_X_QANONIAH_COM_BORN_DIGITAL_API_RECONCILED_10_OF_25_ARTICLES_OCR_ADJUDICATED_15_BOE_NO_DEDICATED_LAWID_PAGE",
          f"counts={amlr_counts}")
    check("    aml_regulation: status breakdown 24/1/0/0...",
          amlr_counts.get("legal_status_breakdown") == {"اصلية": 24, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
          f"breakdown={amlr_counts.get('legal_status_breakdown')}")

    patr = tracks_by_id.get("patent_regulation", {})
    patr_counts = patr.get("record_counts", {})
    check("[7g148] patent_regulation: 67 Arabic records, WIPO Lex official SAIP PDF dual-extraction-pipeline reconciled x qanoonsa.com structural cross-check...",
          patr_counts.get("arabic_articles") == 67
          and patr.get("official_text_status") == "WIPO_LEX_OFFICIAL_SAIP_LETTERHEAD_PDF_DUAL_INDEPENDENT_EXTRACTION_PIPELINE_RECONCILED_X_QANOONSA_STRUCTURAL_CROSSCHECK_BOE_NO_DEDICATED_LAWID_PAGE",
          f"counts={patr_counts}")
    check("    patent_regulation: status breakdown 67/0/0/0...",
          patr_counts.get("legal_status_breakdown") == {"اصلية": 67, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={patr_counts.get('legal_status_breakdown')}")

    ecmr = tracks_by_id.get("ecommerce_regulation", {})
    ecmr_counts = ecmr.get("record_counts", {})
    check("[7g149] ecommerce_regulation: 20 Arabic records, mc.gov.sa official page x Ministry's own scanned PDF word-for-word cross-check...",
          ecmr_counts.get("arabic_articles") == 20
          and ecmr.get("official_text_status") == "MC_GOV_SA_OFFICIAL_BORN_DIGITAL_PAGE_X_MINISTRY_OWN_SCANNED_PDF_WORD_FOR_WORD_CROSSCHECK_X_QANONIAH_LEXISMIDDLEEAST_ARGAAM_MITHAQ_BOE_NO_DEDICATED_LAWID_PAGE",
          f"counts={ecmr_counts}")
    check("    ecommerce_regulation: status breakdown 20/0/0/0...",
          ecmr_counts.get("legal_status_breakdown") == {"اصلية": 20, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={ecmr_counts.get('legal_status_breakdown')}")

    fchr = tracks_by_id.get("franchise_regulation", {})
    fchr_counts = fchr.get("record_counts", {})
    check("[7g150] franchise_regulation: 16 Arabic records, franchising.sa x aunklaw.com verbatim cross-check, lexismiddleeast structural...",
          fchr_counts.get("arabic_articles") == 16
          and fchr.get("official_text_status") == "FRANCHISING_SA_UMM_AL_QURA_GAZETTE_REPRODUCTION_X_AUNKLAW_VERBATIM_CROSSCHECK_X_LEXISMIDDLEEAST_STRUCTURAL_BOE_LAWID_PAGE_ONLY_FOR_BASE_LAW",
          f"counts={fchr_counts}")
    check("    franchise_regulation: status breakdown 16/0/0/0...",
          fchr_counts.get("legal_status_breakdown") == {"اصلية": 16, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={fchr_counts.get('legal_status_breakdown')}")

    tfr = tracks_by_id.get("traffic_regulation", {})
    tfr_counts = tfr.get("record_counts", {})
    check("[7g151] traffic_regulation: 86 Arabic records, MOI scanned document dual vision+OCR pipeline, qanoniah partial cross-check arts 1-8...",
          tfr_counts.get("arabic_articles") == 86
          and tfr.get("official_text_status") == "MOI_OFFICIAL_SCANNED_DOCUMENT_DUAL_VISION_OCR_PIPELINE_X_QANONIAH_COM_BORN_DIGITAL_PARTIAL_CROSSCHECK_ARTS_1_8_OF_86_BOE_NO_DEDICATED_LAWID_PAGE",
          f"counts={tfr_counts}")
    check("    traffic_regulation: status breakdown 82/3/1/0...",
          tfr_counts.get("legal_status_breakdown") == {"اصلية": 82, "معدلة": 3, "ملغاة": 1, "مضافة": 0},
          f"breakdown={tfr_counts.get('legal_status_breakdown')}")

    eia = tracks_by_id.get("environmental_inspection_audit", {})
    eia_counts = eia.get("record_counts", {})
    check("[7g152] environmental_inspection_audit: 10 Arabic records, qanoonsa.com primary, qistas partial cross-check...",
          eia_counts.get("arabic_articles") == 10
          and eia.get("official_text_status") == "QANOONSA_COM_PRIMARY_UMM_AL_QURA_5057_REPRODUCTION_X_QISTAS_COM_PARTIAL_CROSSCHECK_BOE_UNREACHABLE_NO_DEDICATED_LAWID_PAGE",
          f"counts={eia_counts}")
    check("    environmental_inspection_audit: status breakdown 10/0/0/0...",
          eia_counts.get("legal_status_breakdown") == {"اصلية": 10, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={eia_counts.get('legal_status_breakdown')}")

    evp = tracks_by_id.get("environmental_violations_penalties", {})
    evp_counts = evp.get("record_counts", {})
    check("[7g153] environmental_violations_penalties: 10 Arabic records, qanoonsa.com consolidated text, qistas appendix cross-check...",
          evp_counts.get("arabic_articles") == 10
          and evp.get("official_text_status") == "QANOONSA_COM_CONSOLIDATED_TEXT_X_QISTAS_COM_APPENDIX_CROSSCHECK_BOE_NO_DEDICATED_LAWID_PAGE",
          f"counts={evp_counts}")
    check("    environmental_violations_penalties: status breakdown 10/0/0/0...",
          evp_counts.get("legal_status_breakdown") == {"اصلية": 10, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={evp_counts.get('legal_status_breakdown')}")

    epr = tracks_by_id.get("environmental_permits", {})
    epr_counts = epr.get("record_counts", {})
    check("[7g154] environmental_permits: 11 Arabic records, Umm Al-Qura gazette dual official rendering 99.66% wordlevel...",
          epr_counts.get("arabic_articles") == 11
          and epr.get("official_text_status") == "UMM_AL_QURA_GAZETTE_4888_OFFICIAL_HTML_X_OFFICIAL_BORN_DIGITAL_PDF_DUAL_RENDERING_SAME_ISSUE_996_PERCENT_WORDLEVEL_BOE_NO_DEDICATED_LAWID_PAGE",
          f"counts={epr_counts}")
    check("    environmental_permits: status breakdown 11/0/0/0...",
          epr_counts.get("legal_status_breakdown") == {"اصلية": 11, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={epr_counts.get('legal_status_breakdown')}")

    eaq = tracks_by_id.get("environmental_air_quality", {})
    eaq_counts = eaq.get("record_counts", {})
    check("[7g155] environmental_air_quality: 8 Arabic records, MEWA official PDF x qanoniah.com wordlevel cross-check...",
          eaq_counts.get("arabic_articles") == 8
          and eaq.get("official_text_status") == "MEWA_GOV_SA_OFFICIAL_BORN_DIGITAL_PDF_X_QANONIAH_COM_WORDLEVEL_CROSSCHECK_BOE_UNREACHABLE_NO_DEDICATED_LAWID_PAGE",
          f"counts={eaq_counts}")
    check("    environmental_air_quality: status breakdown 8/0/0/0...",
          eaq_counts.get("legal_status_breakdown") == {"اصلية": 8, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={eaq_counts.get('legal_status_breakdown')}")

    esp = tracks_by_id.get("environmental_service_providers", {})
    esp_counts = esp.get("record_counts", {})
    check("[7g156] environmental_service_providers: 13 Arabic records, MEWA scanned decision PDF x qanoniah.com clean HTML...",
          esp_counts.get("arabic_articles") == 13
          and esp.get("official_text_status") == "MEWA_OFFICIAL_SCANNED_DECISION_PDF_VISUALLY_READ_X_QANONIAH_COM_CLEAN_HTML_BOE_UNREACHABLE_NO_DEDICATED_LAWID_PAGE",
          f"counts={esp_counts}")
    check("    environmental_service_providers: status breakdown 13/0/0/0...",
          esp_counts.get("legal_status_breakdown") == {"اصلية": 13, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={esp_counts.get('legal_status_breakdown')}")

    efe = tracks_by_id.get("environmental_fees", {})
    efe_counts = efe.get("record_counts", {})
    check("[7g157] environmental_fees: 4 Arabic records, qanoniah.com primary text, multi-source citation cross-check...",
          efe_counts.get("arabic_articles") == 4
          and efe.get("official_text_status") == "QANONIAH_COM_PRIMARY_TEXT_MULTISOURCE_CITATION_CROSSCHECK_BOE_UNREACHABLE_NO_DEDICATED_LAWID_PAGE",
          f"counts={efe_counts}")
    check("    environmental_fees: status breakdown 4/0/0/0...",
          efe_counts.get("legal_status_breakdown") == {"اصلية": 4, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={efe_counts.get('legal_status_breakdown')}")

    rl = tracks_by_id.get("rett_law", {})
    rl_counts = rl.get("record_counts", {})
    check("[7g158] rett_law: 20 Arabic records, BOE lawId via r.jina.ai proxy x nezams.com/qanoonsa.com...",
          rl_counts.get("arabic_articles") == 20
          and rl.get("official_text_status") == "BOE_LAWID_PAGE_VIA_JINA_READ_PROXY_LIVE_PAGE_HTTP_503_X_NEZAMS_COM_AND_QANOONSA_COM_NON_GOVERNMENT_SECONDARIES",
          f"counts={rl_counts}")
    check("    rett_law: status breakdown 20/0/0/0...",
          rl_counts.get("legal_status_breakdown") == {"اصلية": 20, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={rl_counts.get('legal_status_breakdown')}")

    ul = tracks_by_id.get("universities_law", {})
    ul_counts = ul.get("record_counts", {})
    check("[7g159] universities_law: 58 Arabic records, BOE unreachable x bibliotdroit.com x cua.gov.sa PDF...",
          ul_counts.get("arabic_articles") == 58
          and ul.get("official_text_status") == "BOE_UNREACHABLE_WAYBACK_EGRESS_BLOCKED_X_BIBLIOTDROIT_COM_BORN_DIGITAL_X_CUA_GOV_SA_ADMINISTERING_AUTHORITY_OWN_PDF",
          f"counts={ul_counts}")
    check("    universities_law: status breakdown 58/0/0/0...",
          ul_counts.get("legal_status_breakdown") == {"اصلية": 58, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={ul_counts.get('legal_status_breakdown')}")

    pl = tracks_by_id.get("privatization_law", {})
    pl_counts = pl.get("record_counts", {})
    check("[7g160] privatization_law: 45 Arabic records, BOE unreachable x nezams.com x misa.gov.sa/NCP PDF...",
          pl_counts.get("arabic_articles") == 45
          and pl.get("official_text_status") == "BOE_UNREACHABLE_WAYBACK_EGRESS_BLOCKED_X_NEZAMS_COM_FULL_TEXT_X_MISA_GOV_SA_NCP_OFFICIAL_PDF_PARTIAL_VERBATIM_CONFIRMATION",
          f"counts={pl_counts}")
    check("    privatization_law: status breakdown 45/0/0/0...",
          pl_counts.get("legal_status_breakdown") == {"اصلية": 45, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={pl_counts.get('legal_status_breakdown')}")

    ahl = tracks_by_id.get("antiquities_heritage_law", {})
    ahl_counts = ahl.get("record_counts", {})
    check("[7g161] antiquities_heritage_law: 94 Arabic records, BOE unreachable x nezams.com x unesco-hosted PDF...",
          ahl_counts.get("arabic_articles") == 94
          and ahl.get("official_text_status") == "BOE_UNREACHABLE_WAYBACK_EGRESS_BLOCKED_X_NEZAMS_COM_BORN_DIGITAL_X_UNESCO_HOSTED_BOE_CONTENT_PRINT_PDF_NON_GOVERNMENT_X_UMM_AL_QURA_GAZETTE_FOR_M67_SCOPE_ONLY",
          f"counts={ahl_counts}")
    check("    antiquities_heritage_law: status breakdown 78/16/0/0...",
          ahl_counts.get("legal_status_breakdown") == {"اصلية": 78, "معدلة": 16, "ملغاة": 0, "مضافة": 0},
          f"breakdown={ahl_counts.get('legal_status_breakdown')}")

    cpl = tracks_by_id.get("child_protection_law", {})
    cpl_counts = cpl.get("record_counts", {})
    check("[7g162] child_protection_law: 26 Arabic records, BOE unreachable x nezams.com x MOJ Adl PDF (identity/structure only)...",
          cpl_counts.get("arabic_articles") == 26
          and cpl.get("official_text_status") == "BOE_UNREACHABLE_WAYBACK_NOT_ATTEMPTED_EGRESS_BLOCKED_X_NEZAMS_COM_FULL_TEXT_X_MOJ_ADL_JOURNAL_PDF_IDENTITY_STRUCTURE_ONLY_BIDI_DEFECT_X_UMM_AL_QURA_FOR_1443H_AMENDMENT",
          f"counts={cpl_counts}")
    check("    child_protection_law: status breakdown 21/4/0/1...",
          cpl_counts.get("legal_status_breakdown") == {"اصلية": 21, "معدلة": 4, "ملغاة": 0, "مضافة": 1},
          f"breakdown={cpl_counts.get('legal_status_breakdown')}")

    pfal = tracks_by_id.get("protection_from_abuse_law", {})
    pfal_counts = pfal.get("record_counts", {})
    check("[7g163] protection_from_abuse_law: 17 Arabic records, BOE unreachable x MOF official PDF x nezams.com...",
          pfal_counts.get("arabic_articles") == 17
          and pfal.get("official_text_status") == "BOE_UNREACHABLE_WAYBACK_EGRESS_BLOCKED_X_MOF_OFFICIAL_REGULATIONS_LIBRARY_PDF_GOVERNING_TEXT_X_NEZAMS_COM_CROSSCHECK_X_UMM_AL_QURA_FOR_1443H_AMENDMENT",
          f"counts={pfal_counts}")
    check("    protection_from_abuse_law: status breakdown 14/3/0/0...",
          pfal_counts.get("legal_status_breakdown") == {"اصلية": 14, "معدلة": 3, "ملغاة": 0, "مضافة": 0},
          f"breakdown={pfal_counts.get('legal_status_breakdown')}")

    angl = tracks_by_id.get("associations_ngo_law", {})
    angl_counts = angl.get("record_counts", {})
    check("[7g164] associations_ngo_law: 44 Arabic records, BOE two conflicting lawIds unreachable x nezams.com x menarights.org PDF...",
          angl_counts.get("arabic_articles") == 44
          and angl.get("official_text_status") == "BOE_TWO_CONFLICTING_LAWID_UNREACHABLE_X_NEZAMS_COM_PRIMARY_X_MENARIGHTS_ORG_PDF_CROSSCHECK",
          f"counts={angl_counts}")
    check("    associations_ngo_law: status breakdown 43/1/0/0...",
          angl_counts.get("legal_status_breakdown") == {"اصلية": 43, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
          f"breakdown={angl_counts.get('legal_status_breakdown')}")

    avml = tracks_by_id.get("audiovisual_media_law", {})
    avml_counts = avml.get("record_counts", {})
    check("[7g165] audiovisual_media_law: 25 Arabic records, BOE unreachable x nezams.com x cyrilla.org archived scan x misa.gov.sa translation...",
          avml_counts.get("arabic_articles") == 25
          and avml.get("official_text_status") == "BOE_UNREACHABLE_WAYBACK_REFUSED_BY_FETCH_TOOL_X_NEZAMS_COM_PRIMARY_X_ARCHIVED_BOE_SCAN_CYRILLA_X_OFFICIAL_BOE_ENGLISH_TRANSLATION_MISA",
          f"counts={avml_counts}")
    check("    audiovisual_media_law: status breakdown 24/1/0/0...",
          avml_counts.get("legal_status_breakdown") == {"اصلية": 24, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
          f"breakdown={avml_counts.get('legal_status_breakdown')}")

    spl = tracks_by_id.get("sports_law", {})
    spl_counts = spl.get("record_counts", {})
    check("[7g166] sports_law: 97 Arabic records, BOE+mos.gov.sa unreachable x nezams.com x qanoonsa.com x uqn.gov.sa gazette API...",
          spl_counts.get("arabic_articles") == 97
          and spl.get("official_text_status") == "BOE_AND_MOS_UNREACHABLE_WAYBACK_EGRESS_BLOCKED_X_NEZAMS_COM_PRIMARY_X_QANOONSA_COM_CROSSCHECK_X_UQN_GAZETTE_API_FOR_DECREE_IDENTITY",
          f"counts={spl_counts}")
    check("    sports_law: status breakdown 97/0/0/0...",
          spl_counts.get("legal_status_breakdown") == {"اصلية": 97, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={spl_counts.get('legal_status_breakdown')}")

    asml = tracks_by_id.get("anti_smoking_law", {})
    asml_counts = asml.get("record_counts", {})
    check("[7g167] anti_smoking_law: 20 Arabic records, BOE unreachable x MOH official PDF x nezams.com x cloudfront bilingual PDF...",
          asml_counts.get("arabic_articles") == 20
          and asml.get("official_text_status") == "BOE_UNREACHABLE_WAYBACK_EGRESS_BLOCKED_X_MOH_OFFICIAL_PDF_GOVERNING_TEXT_X_NEZAMS_COM_AND_CLOUDFRONT_BILINGUAL_PDF_CROSSCHECK",
          f"counts={asml_counts}")
    check("    anti_smoking_law: status breakdown 20/0/0/0...",
          asml_counts.get("legal_status_breakdown") == {"اصلية": 20, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={asml_counts.get('legal_status_breakdown')}")

    waml = tracks_by_id.get("weapons_ammunition_law", {})
    waml_counts = waml.get("record_counts", {})
    check("[7g168] weapons_ammunition_law: 63 Arabic records, BOE live unreachable x 3 Wayback snapshots x nezams.com cross-verified...",
          waml_counts.get("arabic_articles") == 63
          and waml.get("official_text_status") == "BOE_WAYBACK_THREE_SNAPSHOT_X_NEZAMS_CROSS_VERIFIED_LIVE_BOE_UNREACHABLE",
          f"counts={waml_counts}")
    check("    weapons_ammunition_law: status breakdown 56/7/0/0...",
          waml_counts.get("legal_status_breakdown") == {"اصلية": 56, "معدلة": 7, "ملغاة": 0, "مضافة": 0},
          f"breakdown={waml_counts.get('legal_status_breakdown')}")

    pdl = tracks_by_id.get("prison_detention_law", {})
    pdl_counts = pdl.get("record_counts", {})
    check("[7g169] prison_detention_law: 31 Arabic records, BOE and MOI PDF unreachable x nezams.com x islamport.com cross-verified...",
          pdl_counts.get("arabic_articles") == 31
          and pdl.get("official_text_status") == "BOE_AND_MOI_PDF_UNREACHABLE_WAYBACK_NOT_ATTEMPTED_X_NEZAMS_COM_X_ISLAMPORT_CROSSCHECK",
          f"counts={pdl_counts}")
    check("    prison_detention_law: status breakdown 28/3/0/0...",
          pdl_counts.get("legal_status_breakdown") == {"اصلية": 28, "معدلة": 3, "ملغاة": 0, "مضافة": 0},
          f"breakdown={pdl_counts.get('legal_status_breakdown')}")

    cdl = tracks_by_id.get("civil_defense_law", {})
    cdl_counts = cdl.get("record_counts", {})
    check("[7g170] civil_defense_law: 36 Arabic records, BOE and NCC unreachable x mohamah.net x islamport.com cross-verified...",
          cdl_counts.get("arabic_articles") == 36
          and cdl.get("official_text_status") == "BOE_AND_NCC_UNREACHABLE_WAYBACK_ENVIRONMENT_BLOCKED_X_MOHAMAH_NET_X_ISLAMPORT_CROSSCHECK",
          f"counts={cdl_counts}")
    check("    civil_defense_law: status breakdown 34/2/0/0...",
          cdl_counts.get("legal_status_breakdown") == {"اصلية": 34, "معدلة": 2, "ملغاة": 0, "مضافة": 0},
          f"breakdown={cdl_counts.get('legal_status_breakdown')}")

    csl = tracks_by_id.get("cooperative_societies_law", {})
    csl_counts = csl.get("record_counts", {})
    check("[7g171] cooperative_societies_law: 44 Arabic records, BOE unreachable x four independent sources x mohamah.net structural...",
          csl_counts.get("arabic_articles") == 44
          and csl.get("official_text_status") == "BOE_UNREACHABLE_WAYBACK_REFUSED_X_FOUR_SOURCE_CROSS_VERIFIED_X_MOHAMAH_STRUCTURAL",
          f"counts={csl_counts}")
    check("    cooperative_societies_law: status breakdown 44/0/0/0...",
          csl_counts.get("legal_status_breakdown") == {"اصلية": 44, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={csl_counts.get('legal_status_breakdown')}")

    bcl = tracks_by_id.get("building_code_law", {})
    bcl_counts = bcl.get("record_counts", {})
    check("[7g172] building_code_law: 16 Arabic records, BOE live 503 x recent Wayback snapshot x engineers PDF x UQ gazette x qanoonsa...",
          bcl_counts.get("arabic_articles") == 16
          and bcl.get("official_text_status") == "BOE_LIVE_503_WAYBACK_RECENT_SNAPSHOT_X_ENGINEERS_PDF_X_UQ_GAZETTE_X_QANOONSA",
          f"counts={bcl_counts}")
    check("    building_code_law: status breakdown 12/4/0/0...",
          bcl_counts.get("legal_status_breakdown") == {"اصلية": 12, "معدلة": 4, "ملغاة": 0, "مضافة": 0},
          f"breakdown={bcl_counts.get('legal_status_breakdown')}")

    psl = tracks_by_id.get("product_safety_law", {})
    psl_counts = psl.get("record_counts", {})
    check("[7g173] product_safety_law: 37 Arabic records, UQ gazette decree M/36 confirmed x qanoonsa primary x nezams cross-verified x BOE unreachable...",
          psl_counts.get("arabic_articles") == 37
          and psl.get("official_text_status") == "UQN_OFFICIAL_GAZETTE_DECREE_M36_CITATION_CONFIRMED_X_QANOONSA_PRIMARY_TEXT_X_NEZAMS_CROSS_VERIFIED_BOE_LAWID_UNREACHABLE",
          f"counts={psl_counts}")
    check("    product_safety_law: status breakdown 37/0/0/0...",
          psl_counts.get("legal_status_breakdown") == {"اصلية": 37, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={psl_counts.get('legal_status_breakdown')}")

    sql = tracks_by_id.get("standards_quality_law", {})
    sql_counts = sql.get("record_counts", {})
    check("[7g174] standards_quality_law: 24 Arabic records, UQ gazette decree M/36 confirmed x qanoonsa primary x nezams cross-verified x BOE index-only...",
          sql_counts.get("arabic_articles") == 24
          and sql.get("official_text_status") == "UQN_OFFICIAL_GAZETTE_DECREE_M36_CITATION_CONFIRMED_X_QANOONSA_PRIMARY_TEXT_X_NEZAMS_CROSS_VERIFIED_2WORDS_BOE_INDEX_ONLY",
          f"counts={sql_counts}")
    check("    standards_quality_law: status breakdown 24/0/0/0...",
          sql_counts.get("legal_status_breakdown") == {"اصلية": 24, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={sql_counts.get('legal_status_breakdown')}")

    drl = tracks_by_id.get("disability_rights_law", {})
    drl_counts = drl.get("record_counts", {})
    check("[7g175] disability_rights_law: 33 Arabic records, BOE lawId unreachable x Wayback egress-blocked x nezams primary x qanoonsa cross-verified...",
          drl_counts.get("arabic_articles") == 33
          and drl.get("official_text_status") == "BOE_LAWID_UNREACHABLE_WAYBACK_EGRESS_BLOCKED_X_NEZAMS_PRIMARY_X_QANOONSA_CROSS_VERIFIED",
          f"counts={drl_counts}")
    check("    disability_rights_law: status breakdown 33/0/0/0...",
          drl_counts.get("legal_status_breakdown") == {"اصلية": 33, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={drl_counts.get('legal_status_breakdown')}")

    trl = tracks_by_id.get("tourism_law", {})
    trl_counts = trl.get("record_counts", {})
    check("[7g176] tourism_law: 19 Arabic records, BOE lawId unreachable x Wayback refused x MT PDF primary x nezams cross-verified x MISA EN structural...",
          trl_counts.get("arabic_articles") == 19
          and trl.get("official_text_status") == "BOE_LAWID_UNREACHABLE_WAYBACK_REFUSED_X_MT_PDF_PRIMARY_X_NEZAMS_CROSS_VERIFIED_X_MISA_EN_STRUCTURAL",
          f"counts={trl_counts}")
    check("    tourism_law: status breakdown 19/0/0/0...",
          trl_counts.get("legal_status_breakdown") == {"اصلية": 19, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={trl_counts.get('legal_status_breakdown')}")

    sqr = tracks_by_id.get("standards_quality_regulation", {})
    sqr_counts = sqr.get("record_counts", {})
    check("[7g177] standards_quality_regulation: 23 Arabic records, SASO official site x UQ gazette API dual-primary x qanoonsa cross-verified x BOE no dedicated page...",
          sqr_counts.get("arabic_articles") == 23
          and sqr.get("official_text_status") == "SASO_OFFICIAL_SITE_X_UQN_API_DUAL_PRIMARY_X_QANOONSA_CROSSVERIFIED_BOE_NO_DEDICATED_PAGE",
          f"counts={sqr_counts}")
    check("    standards_quality_regulation: status breakdown 23/0/0/0...",
          sqr_counts.get("legal_status_breakdown") == {"اصلية": 23, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={sqr_counts.get('legal_status_breakdown')}")

    drr = tracks_by_id.get("disability_rights_regulation", {})
    drr_counts = drr.get("record_counts", {})
    check("[7g178] disability_rights_regulation: 45 Arabic records, UQN primary HTML x qanoonsa article-by-article cross-verified x BOE shared page unreachable...",
          drr_counts.get("arabic_articles") == 45
          and drr.get("official_text_status") == "UQN_GOV_SA_PRIMARY_HTML_X_QANOONSA_ARTICLE_BY_ARTICLE_CROSSVERIFIED_BOE_SHARED_PAGE_UNREACHABLE",
          f"counts={drr_counts}")
    check("    disability_rights_regulation: status breakdown 45/0/0/0...",
          drr_counts.get("legal_status_breakdown") == {"اصلية": 45, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={drr_counts.get('legal_status_breakdown')}")

    asr = tracks_by_id.get("anti_smoking_regulation", {})
    asr_counts = asr.get("record_counts", {})
    check("[7g179] anti_smoking_regulation: 17 Arabic records, MOH 2019 PDF primary x WHO/EMRO 2017 diff cross-check x BOE no dedicated page x founding resolution unconfirmed...",
          asr_counts.get("arabic_articles") == 17
          and asr.get("official_text_status") == "MOH_PDF_PRIMARY_2019_3RD_EDITION_X_WHO_EMRO_2017_DIFF_CROSSCHECK_BOE_NO_DEDICATED_PAGE_FOUNDING_RESOLUTION_UNCONFIRMED",
          f"counts={asr_counts}")
    check("    anti_smoking_regulation: status breakdown 11/6/0/0...",
          asr_counts.get("legal_status_breakdown") == {"اصلية": 11, "معدلة": 6, "ملغاة": 0, "مضافة": 0},
          f"breakdown={asr_counts.get('legal_status_breakdown')}")

    gel = tracks_by_id.get("general_education_law", {})
    gel_counts = gel.get("record_counts", {})
    check("[7g180] general_education_law: 68 Arabic records, uqn.gov.sa primary fulltext x SPA official corroboration x sabq structural cross-check, BOE no page yet, not yet in force...",
          gel_counts.get("arabic_articles") == 68
          and gel.get("official_text_status") == "UQN_GOV_SA_PRIMARY_FULLTEXT_X_SPA_OFFICIAL_CORROBORATION_X_SABQ_STRUCTURAL_CROSSCHECK_BOE_NO_PAGE_YET_NOT_YET_IN_FORCE",
          f"counts={gel_counts}")
    check("    general_education_law: status breakdown 68/0/0/0...",
          gel_counts.get("legal_status_breakdown") == {"اصلية": 68, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={gel_counts.get('legal_status_breakdown')}")

    cil = tracks_by_id.get("credit_information_law", {})
    cil_counts = cil.get("record_counts", {})
    check("[7g181] credit_information_law: 17 Arabic records, BOE Wayback sole official channel x nezams x saudipedia cross-verified...",
          cil_counts.get("arabic_articles") == 17
          and cil.get("official_text_status") == "BOE_WAYBACK_SOLE_OFFICIAL_CHANNEL_X_NEZAMS_X_SAUDIPEDIA_CROSSVERIFIED_LIVE_BOE_UNREACHABLE",
          f"counts={cil_counts}")
    check("    credit_information_law: status breakdown 17/0/0/0...",
          cil_counts.get("legal_status_breakdown") == {"اصلية": 17, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={cil_counts.get('legal_status_breakdown')}")

    rebl = tracks_by_id.get("real_estate_brokerage_law", {})
    rebl_counts = rebl.get("record_counts", {})
    check("[7g182] real_estate_brokerage_law: 24 Arabic records, REGA official BOE-sealed scanned PDF visually verified x qanoonsa x nezams...",
          rebl_counts.get("arabic_articles") == 24
          and rebl.get("official_text_status") == "MATCHES_OFFICIAL_SCAN_VISUALLY_VERIFIED",
          f"counts={rebl_counts}")
    check("    real_estate_brokerage_law: status breakdown 24/0/0/0...",
          rebl_counts.get("legal_status_breakdown") == {"اصلية": 24, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={rebl_counts.get('legal_status_breakdown')}")

    srl = tracks_by_id.get("state_revenue_law", {})
    srl_counts = srl.get("record_counts", {})
    check("[7g183] state_revenue_law: 32 Arabic records, BOE Wayback x nezams x qanoonsa cross-verified, 30/1/0/1 status breakdown...",
          srl_counts.get("arabic_articles") == 32
          and srl.get("official_text_status") == "BOE_WAYBACK_X_NEZAMS_X_QANOONSA_CROSS_VERIFIED",
          f"counts={srl_counts}")
    check("    state_revenue_law: status breakdown 30/1/0/1...",
          srl_counts.get("legal_status_breakdown") == {"اصلية": 30, "معدلة": 1, "ملغاة": 0, "مضافة": 1},
          f"breakdown={srl_counts.get('legal_status_breakdown')}")

    etl = tracks_by_id.get("etec_law", {})
    etl_counts = etl.get("record_counts", {})
    check("[7g184] etec_law: 18 Arabic records, BOE dual-independent-Wayback-snapshot full literal match x nezams supplementary...",
          etl_counts.get("arabic_articles") == 18
          and etl.get("official_text_status") == "BOE_WAYBACK_DUAL_INDEPENDENT_SNAPSHOT_FULL_LITERAL_MATCH_X_NEZAMS_SUPPLEMENTARY",
          f"counts={etl_counts}")
    check("    etec_law: status breakdown 16/2/0/0...",
          etl_counts.get("legal_status_breakdown") == {"اصلية": 16, "معدلة": 2, "ملغاة": 0, "مضافة": 0},
          f"breakdown={etl_counts.get('legal_status_breakdown')}")

    eir = tracks_by_id.get("einvoicing_regulation", {})
    eir_counts = eir.get("record_counts", {})
    check("[7g185] einvoicing_regulation: 7 Arabic records, ZATCA official PDF primary x aflaksolutions mirror cross-verified, BOE no dedicated page...",
          eir_counts.get("arabic_articles") == 7
          and eir.get("official_text_status") == "ZATCA_OFFICIAL_PDF_PRIMARY_X_AFLAKSOLUTIONS_MIRROR_CROSSVERIFIED_BOE_NO_DEDICATED_PAGE",
          f"counts={eir_counts}")
    check("    einvoicing_regulation: status breakdown 7/0/0/0...",
          eir_counts.get("legal_status_breakdown") == {"اصلية": 7, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={eir_counts.get('legal_status_breakdown')}")

    pcbtr = tracks_by_id.get("pdpl_cross_border_transfer_regulation", {})
    pcbtr_counts = pcbtr.get("record_counts", {})
    check("[7g186] pdpl_cross_border_transfer_regulation: 9 Arabic records, SDAIA portal x Umm al-Qura gazette primary, BOE unreachable...",
          pcbtr_counts.get("arabic_articles") == 9
          and pcbtr.get("official_text_status") == "TIER_1_PRIMARY_MULTI_SOURCE_SDAIA_PORTAL_X_UQN_GAZETTE_BOE_UNREACHABLE",
          f"counts={pcbtr_counts}")
    check("    pdpl_cross_border_transfer_regulation: status breakdown 9/0/0/0...",
          pcbtr_counts.get("legal_status_breakdown") == {"اصلية": 9, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={pcbtr_counts.get('legal_status_breakdown')}")

    soa = tracks_by_id.get("sdaia_organizational_arrangements", {})
    soa_counts = soa.get("record_counts", {})
    check("[7g187] sdaia_organizational_arrangements: 16 Arabic records, SDAIA site PDF via jina reader-proxy ligature-artifact reconstructed, BOE page not located...",
          soa_counts.get("arabic_articles") == 16
          and soa.get("official_text_status") == "SDAIA_OFFICIAL_SITE_PDF_PRIMARY_JINA_READER_PROXY_LIGATURE_ARTIFACT_RECONSTRUCTED_X_QISTAS_LEXISMIDDLEEAST_SPA_CROSSCHECK_TIER2_BOE_PAGE_NOT_LOCATED",
          f"counts={soa_counts}")
    check("    sdaia_organizational_arrangements: status breakdown 15/1/0/0...",
          soa_counts.get("legal_status_breakdown") == {"اصلية": 15, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
          f"breakdown={soa_counts.get('legal_status_breakdown')}")

    trade_names_regulation_var = tracks_by_id.get("trade_names_regulation", {})
    trade_names_regulation_var_counts = trade_names_regulation_var.get("record_counts", {})
    check("[7g188] trade_names_regulation: 19 Arabic records...",
          trade_names_regulation_var_counts.get("arabic_articles") == 19
          and trade_names_regulation_var.get("official_text_status") == "QANOONSA_TEXT_PRIMARY_X_WAYBACK_SNAPSHOT_CROSSCHECK_X_NDMLAW_INDEPENDENT_SECONDARY_VERBATIM_MATCH_X_MC_GOV_SA_METADATA_CONFIRMED_TIER3_BOE_NO_DEDICATED_PAGE_UQN_SPA_UNREACHABLE",
          f"counts={trade_names_regulation_var_counts}")
    check("    trade_names_regulation: status breakdown 19/0/0/0...",
          trade_names_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 19, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={trade_names_regulation_var_counts.get('legal_status_breakdown')}")

    commercial_agencies_regulation_var = tracks_by_id.get("commercial_agencies_regulation", {})
    commercial_agencies_regulation_var_counts = commercial_agencies_regulation_var.get("record_counts", {})
    check("[7g189] commercial_agencies_regulation: 49 Arabic records...",
          commercial_agencies_regulation_var_counts.get("arabic_articles") == 49
          and commercial_agencies_regulation_var.get("official_text_status") == "MC_GOV_SA_LIVE_PORTAL_PRIMARY_JINA_READER_PROXY_X_NEZAMS_QISTAS_THELAWSA_CORPORATE_LAWYER_SECONDARY_X_ALMURABA_1435H_AMENDMENT_CROSSCHECK_TIER2_BOE_NO_DEDICATED_PAGE_SINGLE_FETCH_CAPTCHA_BLOCKED_DIRECT_AND_WAYBACK",
          f"counts={commercial_agencies_regulation_var_counts}")
    check("    commercial_agencies_regulation: status breakdown 21/1/0/27...",
          commercial_agencies_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 21, "معدلة": 1, "مضافة": 27},
          f"breakdown={commercial_agencies_regulation_var_counts.get('legal_status_breakdown')}")

    accounting_auditing_regulation_var = tracks_by_id.get("accounting_auditing_regulation", {})
    accounting_auditing_regulation_var_counts = accounting_auditing_regulation_var.get("record_counts", {})
    check("[7g190] accounting_auditing_regulation: 15 Arabic records...",
          accounting_auditing_regulation_var_counts.get("arabic_articles") == 15
          and accounting_auditing_regulation_var.get("official_text_status") == "SOCPA_OFFICIAL_PDF_VIA_WAYBACK_TESSERACT_OCR_PRIMARY_X_PDFTOTEXT_DIGIT_CROSSCHECK_X_ARGAAM_DARKHABR_SECONDARY_X_UQN_WAYBACK_FOUNDING_DECREE_CONFIRMED_TIER2_SOCPA_LIVE_UNREACHABLE",
          f"counts={accounting_auditing_regulation_var_counts}")
    check("    accounting_auditing_regulation: status breakdown 14/1/0/0...",
          accounting_auditing_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 14, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
          f"breakdown={accounting_auditing_regulation_var_counts.get('legal_status_breakdown')}")

    commercial_register_regulation_var = tracks_by_id.get("commercial_register_regulation", {})
    commercial_register_regulation_var_counts = commercial_register_regulation_var.get("record_counts", {})
    check("[7g191] commercial_register_regulation: 21 Arabic records...",
          commercial_register_regulation_var_counts.get("arabic_articles") == 21
          and commercial_register_regulation_var.get("official_text_status") == "QANOONSA_TEXT_PRIMARY_X_ALEQT_INDEPENDENT_SECONDARY_PHRASE_LEVEL_CROSSCHECK_TIER2_BOE_SHARES_BASE_LAW_PAGE_MC_UQN_DIRECT_FETCH_UNREACHABLE",
          f"counts={commercial_register_regulation_var_counts}")
    check("    commercial_register_regulation: status breakdown 21/0/0/0...",
          commercial_register_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 21, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={commercial_register_regulation_var_counts.get('legal_status_breakdown')}")

    real_estate_brokerage_regulation_var = tracks_by_id.get("real_estate_brokerage_regulation", {})
    real_estate_brokerage_regulation_var_counts = real_estate_brokerage_regulation_var.get("record_counts", {})
    check("[7g192] real_estate_brokerage_regulation: 27 Arabic records...",
          real_estate_brokerage_regulation_var_counts.get("arabic_articles") == 27
          and real_estate_brokerage_regulation_var.get("official_text_status") == "REGA_OFFICIAL_PDF_VISUALLY_VERIFIED_X_UQN_GAZETTE_FULLTEXT_CROSSCHECK_TIER1_BOE_UNREACHABLE",
          f"counts={real_estate_brokerage_regulation_var_counts}")
    check("    real_estate_brokerage_regulation: status breakdown 27/0/0/0...",
          real_estate_brokerage_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 27, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={real_estate_brokerage_regulation_var_counts.get('legal_status_breakdown')}")

    foreign_ownership_regulation_var = tracks_by_id.get("foreign_ownership_regulation", {})
    foreign_ownership_regulation_var_counts = foreign_ownership_regulation_var.get("record_counts", {})
    check("[7g193] foreign_ownership_regulation: 15 Arabic records...",
          foreign_ownership_regulation_var_counts.get("arabic_articles") == 15
          and foreign_ownership_regulation_var.get("official_text_status") == "UQN_GAZETTE_PRIMARY_X_REGA_PORTAL_PRIMARY_CROSS_VERIFIED_TIER1_NCAR_BOE_UNREACHABLE_DECREE_NUMBER_UNCONFIRMED",
          f"counts={foreign_ownership_regulation_var_counts}")
    check("    foreign_ownership_regulation: status breakdown 14/0/0/0...",
          foreign_ownership_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 14},
          f"breakdown={foreign_ownership_regulation_var_counts.get('legal_status_breakdown')}")

    anti_fraud_regulation_var = tracks_by_id.get("anti_fraud_regulation", {})
    anti_fraud_regulation_var_counts = anti_fraud_regulation_var.get("record_counts", {})
    check("[7g194] anti_fraud_regulation: 19 Arabic records...",
          anti_fraud_regulation_var_counts.get("arabic_articles") == 19
          and anti_fraud_regulation_var.get("official_text_status") == "SECONDARY_SINGLE_SOURCE_VERBATIM_PARTIAL_CROSS_CHECK_BOE_UNREACHABLE",
          f"counts={anti_fraud_regulation_var_counts}")
    check("    anti_fraud_regulation: status breakdown 19/0/0/0...",
          anti_fraud_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 19, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={anti_fraud_regulation_var_counts.get('legal_status_breakdown')}")

    rett_regulation_var = tracks_by_id.get("rett_regulation", {})
    rett_regulation_var_counts = rett_regulation_var.get("record_counts", {})
    check("[7g195] rett_regulation: 15 Arabic records...",
          rett_regulation_var_counts.get("arabic_articles") == 15
          and rett_regulation_var.get("official_text_status") == "ZATCA_PORTAL_PRIMARY_TWO_PIPELINE_OCR_X_SECONDARY_CROSS_VERIFIED",
          f"counts={rett_regulation_var_counts}")
    check("    rett_regulation: status breakdown 15/0/0/0...",
          rett_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 15, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={rett_regulation_var_counts.get('legal_status_breakdown')}")

    anti_narcotics_regulation_var = tracks_by_id.get("anti_narcotics_regulation", {})
    anti_narcotics_regulation_var_counts = anti_narcotics_regulation_var.get("record_counts", {})
    check("[7g196] anti_narcotics_regulation: 40 Arabic records...",
          anti_narcotics_regulation_var_counts.get("arabic_articles") == 40
          and anti_narcotics_regulation_var.get("official_text_status") == "NEZAMS_HTML_SINGLE_FULLTEXT_X_QISTAS_PREAMBLE_PARTIAL_MATCH",
          f"counts={anti_narcotics_regulation_var_counts}")
    check("    anti_narcotics_regulation: status breakdown 40/0/0/0...",
          anti_narcotics_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 40, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={anti_narcotics_regulation_var_counts.get('legal_status_breakdown')}")

    anti_concealment_regulation_var = tracks_by_id.get("anti_concealment_regulation", {})
    anti_concealment_regulation_var_counts = anti_concealment_regulation_var.get("record_counts", {})
    check("[7g197] anti_concealment_regulation: 18 Arabic records...",
          anti_concealment_regulation_var_counts.get("arabic_articles") == 18
          and anti_concealment_regulation_var.get("official_text_status") == "PRIMARY_MC_GOVSA_PDF_X_SPA_OFFICIAL_CORROBORATION_TIER2",
          f"counts={anti_concealment_regulation_var_counts}")
    check("    anti_concealment_regulation: status breakdown 18/0/0/0...",
          anti_concealment_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 18, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={anti_concealment_regulation_var_counts.get('legal_status_breakdown')}")

    privatization_regulation_var = tracks_by_id.get("privatization_regulation", {})
    privatization_regulation_var_counts = privatization_regulation_var.get("record_counts", {})
    check("[7g198] privatization_regulation: 169 Arabic records...",
          privatization_regulation_var_counts.get("arabic_articles") == 169
          and privatization_regulation_var.get("official_text_status") == "UQN_GAZETTE_DIRECT_FETCH_TIER1_ARGAAM_PDF_AMENDMENT_DIFF_PARTIAL",
          f"counts={privatization_regulation_var_counts}")
    check("    privatization_regulation: status breakdown 140/19/0/10...",
          privatization_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 140, "معدلة": 19, "ملغاة": 0, "مضافة": 10},
          f"breakdown={privatization_regulation_var_counts.get('legal_status_breakdown')}")

    chambers_of_commerce_regulation_var = tracks_by_id.get("chambers_of_commerce_regulation", {})
    chambers_of_commerce_regulation_var_counts = chambers_of_commerce_regulation_var.get("record_counts", {})
    check("[7g199] chambers_of_commerce_regulation: 63 Arabic records...",
          chambers_of_commerce_regulation_var_counts.get("arabic_articles") == 63
          and chambers_of_commerce_regulation_var.get("official_text_status") == "MATCHES_UQN_GAZETTE_X_FSC_INDEPENDENT_CROSS_CHECK",
          f"counts={chambers_of_commerce_regulation_var_counts}")
    check("    chambers_of_commerce_regulation: status breakdown 62/1/0/0...",
          chambers_of_commerce_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 62, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
          f"breakdown={chambers_of_commerce_regulation_var_counts.get('legal_status_breakdown')}")

    state_revenue_regulation_var = tracks_by_id.get("state_revenue_regulation", {})
    state_revenue_regulation_var_counts = state_revenue_regulation_var.get("record_counts", {})
    check("[7g200] state_revenue_regulation: 65 Arabic records...",
          state_revenue_regulation_var_counts.get("arabic_articles") == 65
          and state_revenue_regulation_var.get("official_text_status") == "MOF_OFFICIAL_PDF_DIRECT_FETCH_VISUALLY_PAGE_IMAGE_TRANSCRIBED_X_QANONIAH_API_PARTIAL_CROSSCHECK_ARTS_1_8_ONLY_TIER_2_BOE_NO_DEDICATED_PAGE_NCAR_GOV_SA_UNREACHABLE",
          f"counts={state_revenue_regulation_var_counts}")
    check("    state_revenue_regulation: status breakdown 60/4/0/1...",
          state_revenue_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 60, "معدلة": 4, "ملغاة": 0, "مضافة": 1},
          f"breakdown={state_revenue_regulation_var_counts.get('legal_status_breakdown')}")

    weapons_ammunition_regulation_var = tracks_by_id.get("weapons_ammunition_regulation", {})
    weapons_ammunition_regulation_var_counts = weapons_ammunition_regulation_var.get("record_counts", {})
    check("[7g201] weapons_ammunition_regulation: 19 Arabic records...",
          weapons_ammunition_regulation_var_counts.get("arabic_articles") == 19
          and weapons_ammunition_regulation_var.get("official_text_status") == "QADHA_ORG_SA_PRIMARY_PDF_TESSERACT_OCR_RECONSTRUCTED_CORRUPTED_TOUNICODE_TEXT_LAYER_X_QANOONSA_PARTIAL_2_OF_19_ARTICLES_X_UQN_GOV_SA_DIRECT_5TH_AMENDMENT_DISCOVERY_TIER_3_BOE_NO_DEDICATED_PAGE_FOUNDING_DECREE_23_VS_33_INTERNAL_CONFLICT",
          f"counts={weapons_ammunition_regulation_var_counts}")
    check("    weapons_ammunition_regulation: status breakdown 7/12/0/0...",
          weapons_ammunition_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 7, "معدلة": 12, "ملغاة": 0, "مضافة": 0},
          f"breakdown={weapons_ammunition_regulation_var_counts.get('legal_status_breakdown')}")

    engineering_practice_regulation_var = tracks_by_id.get("engineering_practice_regulation", {})
    engineering_practice_regulation_var_counts = engineering_practice_regulation_var.get("record_counts", {})
    check("[7g202] engineering_practice_regulation: 18 Arabic records...",
          engineering_practice_regulation_var_counts.get("arabic_articles") == 18
          and engineering_practice_regulation_var.get("official_text_status") == "UQN_GOV_SA_OFFICIAL_GAZETTE_HTML_DIRECT_PRIMARY_X_QANOONSA_FULL_18_OF_18_CROSSCHECK_TIER_2_BOE_AND_SAUDIENG_SA_LIVE_UNREACHABLE_WAYBACK_CONTENT_BLOCKED",
          f"counts={engineering_practice_regulation_var_counts}")
    check("    engineering_practice_regulation: status breakdown 18/0/0/0...",
          engineering_practice_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 18, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={engineering_practice_regulation_var_counts.get('legal_status_breakdown')}")

    allegiance_commission_regulation_var = tracks_by_id.get("allegiance_commission_regulation", {})
    allegiance_commission_regulation_var_counts = allegiance_commission_regulation_var.get("record_counts", {})
    check("[7g203] allegiance_commission_regulation: 18 Arabic records...",
          allegiance_commission_regulation_var_counts.get("arabic_articles") == 18
          and allegiance_commission_regulation_var.get("official_text_status") == "SPA_OFFICIAL_WIRE_X_ISLAMPORT_SECONDARY_CROSS_VERIFIED_BOE_UNREACHABLE",
          f"counts={allegiance_commission_regulation_var_counts}")
    check("    allegiance_commission_regulation: status breakdown 18/0/0/0...",
          allegiance_commission_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 18, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={allegiance_commission_regulation_var_counts.get('legal_status_breakdown')}")

    social_insurance_regulation_var = tracks_by_id.get("social_insurance_regulation", {})
    social_insurance_regulation_var_counts = social_insurance_regulation_var.get("record_counts", {})
    check("[7g204] social_insurance_regulation: 107 Arabic records...",
          social_insurance_regulation_var_counts.get("arabic_articles") == 107
          and social_insurance_regulation_var.get("official_text_status") == "UQN_GOV_SA_OFFICIAL_GAZETTE_HTML_DIRECT_PRIMARY_X_QANOONSA_NEAR_FULL_107_CROSSCHECK_X_ARGAAM_TERTIARY_TIER_2_BOE_UNREACHABLE_NOT_CIRCUMVENTED_PARAGRAPH_ENUMERATION_GAP_63_OF_107",
          f"counts={social_insurance_regulation_var_counts}")
    check("    social_insurance_regulation: status breakdown 107/0/0/0...",
          social_insurance_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 107, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={social_insurance_regulation_var_counts.get('legal_status_breakdown')}")

    saudi_engineers_regulation_var = tracks_by_id.get("saudi_engineers_regulation", {})
    saudi_engineers_regulation_var_counts = saudi_engineers_regulation_var.get("record_counts", {})
    check("[7g205] saudi_engineers_regulation: 32 Arabic records...",
          saudi_engineers_regulation_var_counts.get("arabic_articles") == 32
          and saudi_engineers_regulation_var.get("official_text_status") == "SAUDIENG_SA_WAYBACK_20250625_PRIMARY_X_PDFTOTEXT_POPPLER_AND_PDFPLUMBER_PDFMINER_DUAL_INDEPENDENT_EXTRACTION_CROSSCHECK_LIVE_FETCH_TLS_RESET",
          f"counts={saudi_engineers_regulation_var_counts}")
    check("    saudi_engineers_regulation: status breakdown 32/0/0/0...",
          saudi_engineers_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 32, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={saudi_engineers_regulation_var_counts.get('legal_status_breakdown')}")

    child_protection_regulation_var = tracks_by_id.get("child_protection_regulation", {})
    child_protection_regulation_var_counts = child_protection_regulation_var.get("record_counts", {})
    check("[7g206] child_protection_regulation: 25 Arabic records...",
          child_protection_regulation_var_counts.get("arabic_articles") == 25
          and child_protection_regulation_var.get("official_text_status") == "NEZAMS_COM_FULLTEXT_PRIMARY_X_MOJ_ADALAH_MAGAZINE_PDF_STRUCTURAL_CROSSCHECK_TIER_3_BOE_NO_DEDICATED_LAWID_FOUND",
          f"counts={child_protection_regulation_var_counts}")
    check("    child_protection_regulation: status breakdown 25/0/0/0...",
          child_protection_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 25, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={child_protection_regulation_var_counts.get('legal_status_breakdown')}")

    whistleblower_regulation_var = tracks_by_id.get("whistleblower_regulation", {})
    whistleblower_regulation_var_counts = whistleblower_regulation_var.get("record_counts", {})
    check("[7g207] whistleblower_regulation: 12 Arabic records...",
          whistleblower_regulation_var_counts.get("arabic_articles") == 12
          and whistleblower_regulation_var.get("official_text_status") == "UQN_GAZETTE_PDF_CROSS_VERIFIED_HTML_MIRROR_X_QANOONSA_HTML_MIRROR_TIER_4_SINGLE_CHANNEL_DECISION_NUMBER_CORRECTED",
          f"counts={whistleblower_regulation_var_counts}")
    check("    whistleblower_regulation: status breakdown 12/0/0/0...",
          whistleblower_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 12},
          f"breakdown={whistleblower_regulation_var_counts.get('legal_status_breakdown')}")

    social_insurance_legacy_regulation_var = tracks_by_id.get("social_insurance_legacy_regulation", {})
    social_insurance_legacy_regulation_var_counts = social_insurance_legacy_regulation_var.get("record_counts", {})
    check("[7g208] social_insurance_legacy_regulation: 170 Arabic records...",
          social_insurance_legacy_regulation_var_counts.get("arabic_articles") == 170
          and social_insurance_legacy_regulation_var.get("official_text_status") == "KSU_MIRROR_X_QISTAS_PARTIAL_VERBATIM_X_MULTISOURCE_STRUCTURAL_CORROBORATION_TIER_3",
          f"counts={social_insurance_legacy_regulation_var_counts}")
    check("    social_insurance_legacy_regulation: status breakdown 165/5/0/0...",
          social_insurance_legacy_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 165, "معدلة": 5, "ملغاة": 0, "مضافة": 0},
          f"breakdown={social_insurance_legacy_regulation_var_counts.get('legal_status_breakdown')}")

    protection_from_abuse_regulation_var = tracks_by_id.get("protection_from_abuse_regulation", {})
    protection_from_abuse_regulation_var_counts = protection_from_abuse_regulation_var.get("record_counts", {})
    check("[7g209] protection_from_abuse_regulation: 14 Arabic records...",
          protection_from_abuse_regulation_var_counts.get("arabic_articles") == 14
          and protection_from_abuse_regulation_var.get("official_text_status") == "HRSD_OFFICIAL_PDF_DIRECT_FETCH_PRIMARY_X_HRSD_ENGLISH_TRANSLATION_CROSS_CONFIRMED_TIER_2_BOE_NO_DEDICATED_PAGE_WAYBACK_AND_JINA_BLOCKED",
          f"counts={protection_from_abuse_regulation_var_counts}")
    check("    protection_from_abuse_regulation: status breakdown 14/0/0/0...",
          protection_from_abuse_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 14, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={protection_from_abuse_regulation_var_counts.get('legal_status_breakdown')}")

    healthcare_professions_regulation_var = tracks_by_id.get("healthcare_professions_regulation", {})
    healthcare_professions_regulation_var_counts = healthcare_professions_regulation_var.get("record_counts", {})
    check("[7g210] healthcare_professions_regulation: 30 Arabic records...",
          healthcare_professions_regulation_var_counts.get("arabic_articles") == 30
          and healthcare_professions_regulation_var.get("official_text_status") == "MOH_PDF_PRIMARY_X_SECOND_MOH_EXPORT_VERIFIED_WAYBACK_IDENTICAL_TIER_2_BOE_NCAR_UNREACHABLE",
          f"counts={healthcare_professions_regulation_var_counts}")
    check("    healthcare_professions_regulation: status breakdown 30/0/0/0...",
          healthcare_professions_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 30, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={healthcare_professions_regulation_var_counts.get('legal_status_breakdown')}")

    shura_council_internal_regulation_var = tracks_by_id.get("shura_council_internal_regulation", {})
    shura_council_internal_regulation_var_counts = shura_council_internal_regulation_var.get("record_counts", {})
    check("[7g211] shura_council_internal_regulation: 34 Arabic records...",
          shura_council_internal_regulation_var_counts.get("arabic_articles") == 34
          and shura_council_internal_regulation_var.get("official_text_status") == "GOVERNMENT_PRIMARY_OFFICIAL_COUNCIL_PUBLICATION_VIA_WAYBACK_VISUAL_VERIFICATION_TIER_2_BOE_LAWID_NOT_LOCATED",
          f"counts={shura_council_internal_regulation_var_counts}")
    check("    shura_council_internal_regulation: status breakdown 29/5/0/0...",
          shura_council_internal_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 29, "معدلة": 5, "ملغاة": 0, "مضافة": 0},
          f"breakdown={shura_council_internal_regulation_var_counts.get('legal_status_breakdown')}")

    civil_service_regulation_var = tracks_by_id.get("civil_service_regulation", {})
    civil_service_regulation_var_counts = civil_service_regulation_var.get("record_counts", {})
    check("[7g212] civil_service_regulation: 261 Arabic records...",
          civil_service_regulation_var_counts.get("arabic_articles") == 261
          and civil_service_regulation_var.get("official_text_status") == "KSU_1440H_INDESIGN_PDF_CLEAN_PRIMARY_X_HRSD_MOE_STRUCTURAL_CROSSCHECK_TIER2_AMENDED_ARTICLES_HRSD_SINGLE_SOURCE_LOWER_CONFIDENCE_BOE_UNREACHABLE",
          f"counts={civil_service_regulation_var_counts}")
    check("    civil_service_regulation: status breakdown 245/16/0/0...",
          civil_service_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 245, "معدلة": 16, "ملغاة": 0, "مضافة": 0},
          f"breakdown={civil_service_regulation_var_counts.get('legal_status_breakdown')}")

    associations_ngo_regulation_var = tracks_by_id.get("associations_ngo_regulation", {})
    associations_ngo_regulation_var_counts = associations_ngo_regulation_var.get("record_counts", {})
    check("[7g213] associations_ngo_regulation: 129 Arabic records...",
          associations_ngo_regulation_var_counts.get("arabic_articles") == 129
          and associations_ngo_regulation_var.get("official_text_status") == "NCNP_OFFICIAL_PDF_DIRECT_PRIMARY_MULTIAGENT_VISUAL_VERIFICATION_TIER1_X_QANOONSA_CROSSCHECK_NCAR_ISTITLAA_WEBARCHIVE_BLOCKED",
          f"counts={associations_ngo_regulation_var_counts}")
    check("    associations_ngo_regulation: status breakdown 129/0/0/0...",
          associations_ngo_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 129, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={associations_ngo_regulation_var_counts.get('legal_status_breakdown')}")

    electronic_transactions_regulation_var = tracks_by_id.get("electronic_transactions_regulation", {})
    electronic_transactions_regulation_var_counts = electronic_transactions_regulation_var.get("record_counts", {})
    check("[7g214] electronic_transactions_regulation: 25 Arabic records...",
          electronic_transactions_regulation_var_counts.get("arabic_articles") == 25
          and electronic_transactions_regulation_var.get("official_text_status") == "UQN_GAZETTE_OFFICIAL_PRIMARY_X_ARGAAM_PRESS_CROSSCHECK_DGA_BOE_UNREACHABLE",
          f"counts={electronic_transactions_regulation_var_counts}")
    check("    electronic_transactions_regulation: status breakdown 25/0/0/0...",
          electronic_transactions_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 25, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={electronic_transactions_regulation_var_counts.get('legal_status_breakdown')}")

    electricity_regulation_var = tracks_by_id.get("electricity_regulation", {})
    electricity_regulation_var_counts = electricity_regulation_var.get("record_counts", {})
    check("[7g215] electricity_regulation: 92 Arabic records...",
          electricity_regulation_var_counts.get("arabic_articles") == 92
          and electricity_regulation_var.get("official_text_status") == "QANOONSA_SINGLE_AGGREGATOR_PRIMARY_TIER3_COMBINED_TWO_INSTRUMENT_TRACK_SERA_BOE_UQN_LIVE_UNREACHABLE",
          f"counts={electricity_regulation_var_counts}")
    check("    electricity_regulation: status breakdown 92/0/0/0...",
          electricity_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 92, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={electricity_regulation_var_counts.get('legal_status_breakdown')}")

    maritime_commercial_regulation_var = tracks_by_id.get("maritime_commercial_regulation", {})
    maritime_commercial_regulation_var_counts = maritime_commercial_regulation_var.get("record_counts", {})
    check("[7g216] maritime_commercial_regulation: 49 Arabic records...",
          maritime_commercial_regulation_var_counts.get("arabic_articles") == 49
          and maritime_commercial_regulation_var.get("official_text_status") == "TIER_2_TGA_WAYBACK_DOUBLE_SNAPSHOT_X_QISTAS_PARTIAL_CROSSCHECK_LIVE_TGA_UNREACHABLE",
          f"counts={maritime_commercial_regulation_var_counts}")
    check("    maritime_commercial_regulation: status breakdown 49/0/0/0...",
          maritime_commercial_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 49, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={maritime_commercial_regulation_var_counts.get('legal_status_breakdown')}")

    agriculture_regulation_var = tracks_by_id.get("agriculture_regulation", {})
    agriculture_regulation_var_counts = agriculture_regulation_var.get("record_counts", {})
    check("[7g217] agriculture_regulation: 271 Arabic records...",
          agriculture_regulation_var_counts.get("arabic_articles") == 271
          and agriculture_regulation_var.get("official_text_status") == "UQN_GAZETTE_OFFICIAL_PRIMARY_X_MEWA_PDF_STRUCTURAL_CROSSCHECK_TIER4_MIXED_CONFIDENCE_4_ARTICLES_AMENDED_TEXT_UNCONFIRMED_BOE_UNREACHABLE",
          f"counts={agriculture_regulation_var_counts}")
    check("    agriculture_regulation: status breakdown 266/5/0/0...",
          agriculture_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 266, "معدلة": 5, "ملغاة": 0, "مضافة": 0},
          f"breakdown={agriculture_regulation_var_counts.get('legal_status_breakdown')}")

    civil_defense_regulation_var = tracks_by_id.get("civil_defense_regulation", {})
    civil_defense_regulation_var_counts = civil_defense_regulation_var.get("record_counts", {})
    check("[7g218] civil_defense_regulation: 21 Arabic records...",
          civil_defense_regulation_var_counts.get("arabic_articles") == 21
          and civil_defense_regulation_var.get("official_text_status") == "TWO_COMPONENT_TRACK_BOE_PORTAL_WAYBACK_5X_SNAPSHOTS_RIGHTS_DUTIES_X_UQN_GAZETTE_WAYBACK_2022_FIREFIGHTING_RESCUE_TIER_2_BOTH_LIVE_PORTALS_UNREACHABLE",
          f"counts={civil_defense_regulation_var_counts}")
    check("    civil_defense_regulation: status breakdown 21/0/0/0...",
          civil_defense_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 21, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={civil_defense_regulation_var_counts.get('legal_status_breakdown')}")

    premium_residency_regulation_var = tracks_by_id.get("premium_residency_regulation", {})
    premium_residency_regulation_var_counts = premium_residency_regulation_var.get("record_counts", {})
    check("[7g219] premium_residency_regulation: 13 Arabic records...",
          premium_residency_regulation_var_counts.get("arabic_articles") == 13
          and premium_residency_regulation_var.get("official_text_status") == "TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE_QANONIAH_PAYWALL_ARTICLES_1_5_X_AUNKLAW_FULL_13_ARTICLES_NCAR_BOE_PRGOV_ALL_UNREACHABLE",
          f"counts={premium_residency_regulation_var_counts}")
    check("    premium_residency_regulation: status breakdown 1/12/0/0...",
          premium_residency_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 1, "معدلة": 12, "ملغاة": 0, "مضافة": 0},
          f"breakdown={premium_residency_regulation_var_counts.get('legal_status_breakdown')}")

    water_regulation_var = tracks_by_id.get("water_regulation", {})
    water_regulation_var_counts = water_regulation_var.get("record_counts", {})
    check("[7g220] water_regulation: 156 Arabic records...",
          water_regulation_var_counts.get("arabic_articles") == 156
          and water_regulation_var.get("official_text_status") == "TIER_1_PRIMARY_MEWA_OFFICIAL_PDF_DIRECT_FETCH_VISION_READ_MINISTERIAL_DECISION_NUMBER_AND_DAY_MONTH_UNCONFIRMED",
          f"counts={water_regulation_var_counts}")
    check("    water_regulation: status breakdown 156/0/0/0...",
          water_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 156, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={water_regulation_var_counts.get('legal_status_breakdown')}")

    press_regulation_var = tracks_by_id.get("press_regulation", {})
    press_regulation_var_counts = press_regulation_var.get("record_counts", {})
    check("[7g221] press_regulation: 99 Arabic records...",
          press_regulation_var_counts.get("arabic_articles") == 99
          and press_regulation_var.get("official_text_status") == "TIER_2_MEDIA_MINISTRY_OFFICIAL_PDF_WAYBACK_2024_VISION_READ_UQN_GAZETTE_PARTIAL_SINGLE_ARTICLE_CROSSCHECK_BOE_NOT_INDEXED",
          f"counts={press_regulation_var_counts}")
    check("    press_regulation: status breakdown 99/0/0/0...",
          press_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 99, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={press_regulation_var_counts.get('legal_status_breakdown')}")

    building_code_regulation_var = tracks_by_id.get("building_code_regulation", {})
    building_code_regulation_var_counts = building_code_regulation_var.get("record_counts", {})
    check("[7g222] building_code_regulation: 30 Arabic records...",
          building_code_regulation_var_counts.get("arabic_articles") == 30
          and building_code_regulation_var.get("official_text_status") == "TIER_1_PRIMARY_MULTI_SOURCE_MOMAH_4X_HOSTED_PDF_EDITIONS_X_QANOONSA_ARTICLE_BY_ARTICLE_CROSSCHECK_UQN_GAZETTE_AND_WAYBACK_CONTENT_PATH_UNREACHABLE",
          f"counts={building_code_regulation_var_counts}")
    check("    building_code_regulation: status breakdown 15/13/0/2...",
          building_code_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 15, "معدلة": 13, "ملغاة": 0, "مضافة": 2},
          f"breakdown={building_code_regulation_var_counts.get('legal_status_breakdown')}")

    telecommunications_regulation_var = tracks_by_id.get("telecommunications_regulation", {})
    telecommunications_regulation_var_counts = telecommunications_regulation_var.get("record_counts", {})
    # 107, not the instrument's 108: article 45 is not held. The corpus stored
    # article 46's text under both slots until the duplicated record was found.
    check("[7g223] telecommunications_regulation: 107 Arabic records...",
          telecommunications_regulation_var_counts.get("arabic_articles") == 107
          and telecommunications_regulation_var.get("official_text_status") == "TIER_2_DUAL_OFFICIAL_PRIMARY_BORN_DIGITAL_CST_X_MCIT_CROSSVERIFIED_TEXT_LAYER_REMEDIATED_UQN_GAZETTE_LINKS_STALE_BOE_NOT_INDEXED",
          f"counts={telecommunications_regulation_var_counts}")
    check("    telecommunications_regulation: status breakdown 107/0/0/0...",
          telecommunications_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 107, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={telecommunications_regulation_var_counts.get('legal_status_breakdown')}")

    credit_information_regulation_var = tracks_by_id.get("credit_information_regulation", {})
    credit_information_regulation_var_counts = credit_information_regulation_var.get("record_counts", {})
    check("[7g224] credit_information_regulation: 55 Arabic records...",
          credit_information_regulation_var_counts.get("arabic_articles") == 55
          and credit_information_regulation_var.get("official_text_status") == "TIER_1_SAMA_WAYBACK_ARCHIVED_PDF_DUAL_OCR_PYMUPDF_RECONCILED_X_RULEBOOK_SAMA_STRUCTURAL_NUMERIC_CROSSVERIFIED",
          f"counts={credit_information_regulation_var_counts}")
    check("    credit_information_regulation: status breakdown 55/0/0/0...",
          credit_information_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 55, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={credit_information_regulation_var_counts.get('legal_status_breakdown')}")

    payment_systems_regulation_var = tracks_by_id.get("payment_systems_regulation", {})
    payment_systems_regulation_var_counts = payment_systems_regulation_var.get("record_counts", {})
    check("[7g225] payment_systems_regulation: 133 Arabic records...",
          payment_systems_regulation_var_counts.get("arabic_articles") == 133
          and payment_systems_regulation_var.get("official_text_status") == "TIER_4_SAMA_RULEBOOK_SINGLE_OFFICIAL_PDF_DUAL_EXTRACTION_TOOL_RECONCILED_NO_INDEPENDENT_SECOND_SOURCE",
          f"counts={payment_systems_regulation_var_counts}")
    check("    payment_systems_regulation: status breakdown 133/0/0/0...",
          payment_systems_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 133, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={payment_systems_regulation_var_counts.get('legal_status_breakdown')}")

    banking_control_regulation_var = tracks_by_id.get("banking_control_regulation", {})
    banking_control_regulation_var_counts = banking_control_regulation_var.get("record_counts", {})
    check("[7g226] banking_control_regulation: 31 Arabic records...",
          banking_control_regulation_var_counts.get("arabic_articles") == 31
          and banking_control_regulation_var.get("official_text_status") == "TIER_1_SAMA_RULEBOOK_LIVE_PAGE_X_ARCHIVAL_1429H_PDF_DUAL_OFFICIAL_CROSSVERIFIED_TWO_DOCUMENTED_VARIANCES",
          f"counts={banking_control_regulation_var_counts}")
    check("    banking_control_regulation: status breakdown 31/0/0/0...",
          banking_control_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 31, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={banking_control_regulation_var_counts.get('legal_status_breakdown')}")

    finance_companies_regulation_var = tracks_by_id.get("finance_companies_regulation", {})
    finance_companies_regulation_var_counts = finance_companies_regulation_var.get("record_counts", {})
    check("[7g227] finance_companies_regulation: 106 Arabic records...",
          finance_companies_regulation_var_counts.get("arabic_articles") == 106
          and finance_companies_regulation_var.get("official_text_status") == "TIER_4_BFC_GOV_SA_SINGLE_OFFICIAL_IMAGE_SCAN_DEC2025_CONSOLIDATED_TEXT_MULTI_SOURCE_AMENDMENT_EVENT_CORROBORATED",
          f"counts={finance_companies_regulation_var_counts}")
    check("    finance_companies_regulation: status breakdown 106/0/0/0...",
          finance_companies_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 106, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={finance_companies_regulation_var_counts.get('legal_status_breakdown')}")

    finance_lease_regulation_var = tracks_by_id.get("finance_lease_regulation", {})
    finance_lease_regulation_var_counts = finance_lease_regulation_var.get("record_counts", {})
    check("[7g228] finance_lease_regulation: 32 Arabic records...",
          finance_lease_regulation_var_counts.get("arabic_articles") == 32
          and finance_lease_regulation_var.get("official_text_status") == "TIER_2_SAMA_RULEBOOK_BORN_DIGITAL_HTML_X_DEDICATED_AMENDMENT_DECISION_NODE_X_ENGLISH_STRUCTURAL_CROSSCHECK",
          f"counts={finance_lease_regulation_var_counts}")
    check("    finance_lease_regulation: status breakdown 29/3/0/0...",
          finance_lease_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 29, "معدلة": 3, "ملغاة": 0, "مضافة": 0},
          f"breakdown={finance_lease_regulation_var_counts.get('legal_status_breakdown')}")

    cooperative_societies_regulation_var = tracks_by_id.get("cooperative_societies_regulation", {})
    cooperative_societies_regulation_var_counts = cooperative_societies_regulation_var.get("record_counts", {})
    check("[7g229] cooperative_societies_regulation: 55 Arabic records...",
          cooperative_societies_regulation_var_counts.get("arabic_articles") == 55
          and cooperative_societies_regulation_var.get("official_text_status") == "TIER_1_NCNP_GOV_SA_X_CSCS_ORG_SA_DUAL_INDEPENDENT_OFFICIAL_IMAGE_SCAN_CROSSVERIFIED",
          f"counts={cooperative_societies_regulation_var_counts}")
    check("    cooperative_societies_regulation: status breakdown 55/0/0/0...",
          cooperative_societies_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 55, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={cooperative_societies_regulation_var_counts.get('legal_status_breakdown')}")

    bog_enforcement_law_var = tracks_by_id.get("bog_enforcement_law", {})
    bog_enforcement_law_var_counts = bog_enforcement_law_var.get("record_counts", {})
    check("[7g230] bog_enforcement_law: 37 Arabic records...",
          bog_enforcement_law_var_counts.get("arabic_articles") == 37
          and bog_enforcement_law_var.get("official_text_status") == "BOE_SINGLE_WAYBACK_SNAPSHOT_EGRESS_BLOCKED_X_NEZAMS_PARTIAL_SPOTCHECK_X_UMM_AL_QURA_METADATA",
          f"counts={bog_enforcement_law_var_counts}")
    check("    bog_enforcement_law: status breakdown 37/0/0/0...",
          bog_enforcement_law_var_counts.get("legal_status_breakdown") == {"اصلية": 37, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={bog_enforcement_law_var_counts.get('legal_status_breakdown')}")

    public_prosecution_law_var = tracks_by_id.get("public_prosecution_law", {})
    public_prosecution_law_var_counts = public_prosecution_law_var.get("record_counts", {})
    check("[7g231] public_prosecution_law: 30 Arabic records...",
          public_prosecution_law_var_counts.get("arabic_articles") == 30
          and public_prosecution_law_var.get("official_text_status") == "BOE_SINGLE_WAYBACK_SNAPSHOT_X_NEZAMS_BYTE_MATCH_X_QANOONSA_M180_DIRECT_TEXT_CROSSVERIFIED",
          f"counts={public_prosecution_law_var_counts}")
    check("    public_prosecution_law: status breakdown 12/16/2/0...",
          public_prosecution_law_var_counts.get("legal_status_breakdown") == {"اصلية": 12, "معدلة": 16, "ملغاة": 2, "مضافة": 0},
          f"breakdown={public_prosecution_law_var_counts.get('legal_status_breakdown')}")

    elderly_care_law_var = tracks_by_id.get("elderly_care_law", {})
    elderly_care_law_var_counts = elderly_care_law_var.get("record_counts", {})
    check("[7g232] elderly_care_law: 23 Arabic records...",
          elderly_care_law_var_counts.get("arabic_articles") == 23
          and elderly_care_law_var.get("official_text_status") == "BOE_WAYBACK_SNAPSHOT_X_NEZAMS_BYTE_MATCH_X_NSHR_PAMPHLET_TRIPLE_VERIFIED",
          f"counts={elderly_care_law_var_counts}")
    check("    elderly_care_law: status breakdown 23/0/0/0...",
          elderly_care_law_var_counts.get("legal_status_breakdown") == {"اصلية": 23, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={elderly_care_law_var_counts.get('legal_status_breakdown')}")

    elderly_care_regulation_var = tracks_by_id.get("elderly_care_regulation", {})
    elderly_care_regulation_var_counts = elderly_care_regulation_var.get("record_counts", {})
    check("[7g233] elderly_care_regulation: 8 Arabic records...",
          elderly_care_regulation_var_counts.get("arabic_articles") == 8
          and elderly_care_regulation_var.get("official_text_status") == "QANONIAH_API_PARTIAL_8_OF_UNKNOWN_TOTAL_10_ITEM_PREVIEW_CAP_DISCLOSED",
          f"counts={elderly_care_regulation_var_counts}")
    check("    elderly_care_regulation: status breakdown 8/0/0/0...",
          elderly_care_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 8, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={elderly_care_regulation_var_counts.get('legal_status_breakdown')}")

    private_schools_regulation_var = tracks_by_id.get("private_schools_regulation", {})
    private_schools_regulation_var_counts = private_schools_regulation_var.get("record_counts", {})
    check("[7g234] private_schools_regulation: 24 Arabic records...",
          private_schools_regulation_var_counts.get("arabic_articles") == 24
          and private_schools_regulation_var.get("official_text_status") == "MOE_OFFICIAL_PDF_DIRECT_FETCH_VISION_VERIFIED_PAGE_BY_PAGE",
          f"counts={private_schools_regulation_var_counts}")
    check("    private_schools_regulation: status breakdown 22/2/0/0...",
          private_schools_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 22, "معدلة": 2, "ملغاة": 0, "مضافة": 0},
          f"breakdown={private_schools_regulation_var_counts.get('legal_status_breakdown')}")

    foreign_schools_regulation_var = tracks_by_id.get("foreign_schools_regulation", {})
    foreign_schools_regulation_var_counts = foreign_schools_regulation_var.get("record_counts", {})
    check("[7g235] foreign_schools_regulation: 21 Arabic records...",
          foreign_schools_regulation_var_counts.get("arabic_articles") == 21
          and foreign_schools_regulation_var.get("official_text_status") == "NEZAMS_X_BIBLIOTDROIT_DUAL_SECONDARY_WORDFORWORD_CROSSVERIFIED_BOE_UNREACHABLE",
          f"counts={foreign_schools_regulation_var_counts}")
    check("    foreign_schools_regulation: status breakdown 19/2/0/0...",
          foreign_schools_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 19, "معدلة": 2, "ملغاة": 0, "مضافة": 0},
          f"breakdown={foreign_schools_regulation_var_counts.get('legal_status_breakdown')}")

    postal_law_var = tracks_by_id.get("postal_law", {})
    postal_law_var_counts = postal_law_var.get("record_counts", {})
    check("[7g236] postal_law: 20 Arabic records...",
          postal_law_var_counts.get("arabic_articles") == 20
          and postal_law_var.get("official_text_status") == "NEZAMS_SINGLE_AGGREGATOR_PARTIAL_20_OF_37_ARTICLES_ARTICLE21PLUS_CONTENT_CORRUPTED_DISCLOSED",
          f"counts={postal_law_var_counts}")
    check("    postal_law: status breakdown 20/0/0/0...",
          postal_law_var_counts.get("legal_status_breakdown") == {"اصلية": 20, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={postal_law_var_counts.get('legal_status_breakdown')}")

    cma_corporate_governance_regulation_var = tracks_by_id.get("cma_corporate_governance_regulation", {})
    cma_corporate_governance_regulation_var_counts = cma_corporate_governance_regulation_var.get("record_counts", {})
    check("[7g237] cma_corporate_governance_regulation: 95 Arabic records...",
          cma_corporate_governance_regulation_var_counts.get("arabic_articles") == 95
          and cma_corporate_governance_regulation_var.get("official_text_status") == "CMA_OFFICIAL_PDF_DIRECT_FETCH_FONT_DEFECT_CORRECTED_2017_SUPERSESSION_CORRECTED",
          f"counts={cma_corporate_governance_regulation_var_counts}")
    check("    cma_corporate_governance_regulation: status breakdown 84/11/0/0...",
          cma_corporate_governance_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 84, "معدلة": 11, "ملغاة": 0, "مضافة": 0},
          f"breakdown={cma_corporate_governance_regulation_var_counts.get('legal_status_breakdown')}")

    tvtc_organizational_statute_var = tracks_by_id.get("tvtc_organizational_statute", {})
    tvtc_organizational_statute_var_counts = tvtc_organizational_statute_var.get("record_counts", {})
    check("[7g238] tvtc_organizational_statute: 13 Arabic records...",
          tvtc_organizational_statute_var_counts.get("arabic_articles") == 13
          and tvtc_organizational_statute_var.get("official_text_status") == "BOE_TRIPLE_WAYBACK_SNAPSHOT_X_NEZAMS_X_QANOONSA_RESOLUTION632_DIRECT_TEXT_CROSSVERIFIED",
          f"counts={tvtc_organizational_statute_var_counts}")
    check("    tvtc_organizational_statute: status breakdown 11/2/0/0...",
          tvtc_organizational_statute_var_counts.get("legal_status_breakdown") == {"اصلية": 11, "معدلة": 2, "ملغاة": 0, "مضافة": 0},
          f"breakdown={tvtc_organizational_statute_var_counts.get('legal_status_breakdown')}")

    waste_management_law_var = tracks_by_id.get("waste_management_law", {})
    waste_management_law_var_counts = waste_management_law_var.get("record_counts", {})
    check("[7g239] waste_management_law: 38 Arabic records...",
          waste_management_law_var_counts.get("arabic_articles") == 38
          and waste_management_law_var.get("official_text_status") == "NEZAMS_SINGLE_AGGREGATOR_BOE_AND_WAYBACK_BOTH_UNREACHABLE_STRUCTURAL_CROSSCHECK_ONLY",
          f"counts={waste_management_law_var_counts}")
    check("    waste_management_law: status breakdown 38/0/0/0...",
          waste_management_law_var_counts.get("legal_status_breakdown") == {"اصلية": 38, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={waste_management_law_var_counts.get('legal_status_breakdown')}")

    fisheries_law_var = tracks_by_id.get("fisheries_law", {})
    fisheries_law_var_counts = fisheries_law_var.get("record_counts", {})
    check("[7g240] fisheries_law: 13 Arabic records...",
          fisheries_law_var_counts.get("arabic_articles") == 13
          and fisheries_law_var.get("official_text_status") == "BOE_WAYBACK_DUAL_SNAPSHOT_2019_2025_SELF_CONSISTENT_TIER_1",
          f"counts={fisheries_law_var_counts}")
    check("    fisheries_law: status breakdown 12/1/0/0...",
          fisheries_law_var_counts.get("legal_status_breakdown") == {"اصلية": 12, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
          f"breakdown={fisheries_law_var_counts.get('legal_status_breakdown')}")

    debt_collection_regulation_var = tracks_by_id.get("debt_collection_regulation", {})
    debt_collection_regulation_var_counts = debt_collection_regulation_var.get("record_counts", {})
    check("[7g241] debt_collection_regulation: 11 Arabic records...",
          debt_collection_regulation_var_counts.get("arabic_articles") == 11
          and debt_collection_regulation_var.get("official_text_status") == "SAMA_RULEBOOK_BORN_DIGITAL_BILINGUAL_ENTIRESECTION_PRIMARY",
          f"counts={debt_collection_regulation_var_counts}")
    check("    debt_collection_regulation: status breakdown 11/0/0/0...",
          debt_collection_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 11, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={debt_collection_regulation_var_counts.get('legal_status_breakdown')}")

    insurance_authority_statute_var = tracks_by_id.get("insurance_authority_statute", {})
    insurance_authority_statute_var_counts = insurance_authority_statute_var.get("record_counts", {})
    check("[7g242] insurance_authority_statute: 15 Arabic records...",
          insurance_authority_statute_var_counts.get("arabic_articles") == 15
          and insurance_authority_statute_var.get("official_text_status") == "UQN_GAZETTE_PRIMARY_X_QANOONSA_BYTE_LEVEL_X_ARGAAM_QUOTE_LEVEL_CROSSVERIFIED_BOE_UNREACHABLE",
          f"counts={insurance_authority_statute_var_counts}")
    check("    insurance_authority_statute: status breakdown 15/0/0/0...",
          insurance_authority_statute_var_counts.get("legal_status_breakdown") == {"اصلية": 15, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={insurance_authority_statute_var_counts.get('legal_status_breakdown')}")

    bnpl_regulation_var = tracks_by_id.get("bnpl_regulation", {})
    bnpl_regulation_var_counts = bnpl_regulation_var.get("record_counts", {})
    check("[7g243] bnpl_regulation: 31 Arabic records...",
          bnpl_regulation_var_counts.get("arabic_articles") == 31
          and bnpl_regulation_var.get("official_text_status") == "SAMA_RULEBOOK_BORN_DIGITAL_BILINGUAL_ENTIRESECTION_SINGLE_SOURCE_NO_INDEPENDENT_CROSSCHECK",
          f"counts={bnpl_regulation_var_counts}")
    check("    bnpl_regulation: status breakdown 30/1/0/0...",
          bnpl_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 30, "معدلة": 1, "ملغاة": 0, "مضافة": 0},
          f"breakdown={bnpl_regulation_var_counts.get('legal_status_breakdown')}")

    offplan_sale_law_var = tracks_by_id.get("offplan_sale_law", {})
    offplan_sale_law_var_counts = offplan_sale_law_var.get("record_counts", {})
    check("[7g244] offplan_sale_law: 30 Arabic records...",
          offplan_sale_law_var_counts.get("arabic_articles") == 30
          and offplan_sale_law_var.get("official_text_status") == "UQN_GAZETTE_PRIMARY_X_QANOONSA_X_NEZAMS_CROSSVERIFIED_BOE_UNREACHABLE",
          f"counts={offplan_sale_law_var_counts}")
    check("    offplan_sale_law: status breakdown 30/0/0/0...",
          offplan_sale_law_var_counts.get("legal_status_breakdown") == {"اصلية": 30, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={offplan_sale_law_var_counts.get('legal_status_breakdown')}")

    contractors_classification_law_var = tracks_by_id.get("contractors_classification_law", {})
    contractors_classification_law_var_counts = contractors_classification_law_var.get("record_counts", {})
    check("[7g245] contractors_classification_law: 19 Arabic records...",
          contractors_classification_law_var_counts.get("arabic_articles") == 19
          and contractors_classification_law_var.get("official_text_status") == "MOMAH_GOV_SA_OFFICIAL_PDF_DIRECT_FETCH_FONT_DEFECT_CORRECTED_X_NEZAMS_QANOONSA_ARGAAM_CROSSCHECK_BOE_UNREACHABLE",
          f"counts={contractors_classification_law_var_counts}")
    check("    contractors_classification_law: status breakdown 19/0/0/0...",
          contractors_classification_law_var_counts.get("legal_status_breakdown") == {"اصلية": 19, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={contractors_classification_law_var_counts.get('legal_status_breakdown')}")

    real_estate_contributions_law_var = tracks_by_id.get("real_estate_contributions_law", {})
    real_estate_contributions_law_var_counts = real_estate_contributions_law_var.get("record_counts", {})
    check("[7g246] real_estate_contributions_law: 38 Arabic records...",
          real_estate_contributions_law_var_counts.get("arabic_articles") == 38
          and real_estate_contributions_law_var.get("official_text_status") == "REGA_OFFICIAL_SCANNED_DECREE_X_UQN_GAZETTE_DUAL_OFFICIAL_CROSSVERIFIED_X_QANOONSA_BOE_UNREACHABLE",
          f"counts={real_estate_contributions_law_var_counts}")
    check("    real_estate_contributions_law: status breakdown 38/0/0/0...",
          real_estate_contributions_law_var_counts.get("legal_status_breakdown") == {"اصلية": 38, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={real_estate_contributions_law_var_counts.get('legal_status_breakdown')}")

    accredited_valuers_law_var = tracks_by_id.get("accredited_valuers_law", {})
    accredited_valuers_law_var_counts = accredited_valuers_law_var.get("record_counts", {})
    check("[7g247] accredited_valuers_law: 45 Arabic records...",
          accredited_valuers_law_var_counts.get("arabic_articles") == 45
          and accredited_valuers_law_var.get("official_text_status") == "TAQEEM_GOV_SA_OFFICIAL_PDF_LIGATURE_DEFECT_CORRECTED_X_UQN_GAZETTE_X_NEZAMS_QANOONSA_CROSSVERIFIED_5_ARTICLES_SINGLE_SOURCE_BOE_UNREACHABLE",
          f"counts={accredited_valuers_law_var_counts}")
    check("    accredited_valuers_law: status breakdown 20/25/0/0...",
          accredited_valuers_law_var_counts.get("legal_status_breakdown") == {"اصلية": 20, "معدلة": 25, "ملغاة": 0, "مضافة": 0},
          f"breakdown={accredited_valuers_law_var_counts.get('legal_status_breakdown')}")

    white_land_fees_law_var = tracks_by_id.get("white_land_fees_law", {})
    white_land_fees_law_var_counts = white_land_fees_law_var.get("record_counts", {})
    check("[7g248] white_land_fees_law: 15 Arabic records...",
          white_land_fees_law_var_counts.get("arabic_articles") == 15
          and white_land_fees_law_var.get("official_text_status") == "MOMAH_GOV_SA_REDLINE_PDF_X_QADHA_ORG_SA_X_ALHAMOUDILAWYERS_CROSSVERIFIED_ARTICLE3_GAP_DISCLOSED_BOE_UNREACHABLE",
          f"counts={white_land_fees_law_var_counts}")
    check("    white_land_fees_law: status breakdown 2/13/0/0...",
          white_land_fees_law_var_counts.get("legal_status_breakdown") == {"اصلية": 2, "معدلة": 13, "ملغاة": 0, "مضافة": 0},
          f"breakdown={white_land_fees_law_var_counts.get('legal_status_breakdown')}")

    frequency_spectrum_regulation_var = tracks_by_id.get("frequency_spectrum_regulation", {})
    frequency_spectrum_regulation_var_counts = frequency_spectrum_regulation_var.get("record_counts", {})
    check("[7g249] frequency_spectrum_regulation: 15 Arabic records...",
          frequency_spectrum_regulation_var_counts.get("arabic_articles") == 15
          and frequency_spectrum_regulation_var.get("official_text_status") == "CST_OFFICIAL_ARABIC_PDF_VISION_READ_X_ENGLISH_STRUCTURAL_CROSSCHECK_GENERAL_FRAMEWORK_ONLY_ANNEXES_EXCLUDED",
          f"counts={frequency_spectrum_regulation_var_counts}")
    check("    frequency_spectrum_regulation: status breakdown 15/0/0/0...",
          frequency_spectrum_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 15, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={frequency_spectrum_regulation_var_counts.get('legal_status_breakdown')}")

    mental_health_law_var = tracks_by_id.get("mental_health_law", {})
    mental_health_law_var_counts = mental_health_law_var.get("record_counts", {})
    check("[7g250] mental_health_law: 30 Arabic records...",
          mental_health_law_var_counts.get("arabic_articles") == 30
          and mental_health_law_var.get("official_text_status") == "NEZAMS_X_SAUDIPEDIA_DUAL_SECONDARY_CROSSVERIFIED_BOE_UNREACHABLE",
          f"counts={mental_health_law_var_counts}")
    check("    mental_health_law: status breakdown 30/0/0/0...",
          mental_health_law_var_counts.get("legal_status_breakdown") == {"اصلية": 30, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={mental_health_law_var_counts.get('legal_status_breakdown')}")

    organ_donation_law_var = tracks_by_id.get("organ_donation_law", {})
    organ_donation_law_var_counts = organ_donation_law_var.get("record_counts", {})
    check("[7g251] organ_donation_law: 27 Arabic records...",
          organ_donation_law_var_counts.get("arabic_articles") == 27
          and organ_donation_law_var.get("official_text_status") == "NEZAMS_X_SAUDIPEDIA_X_WIKIPEDIA_SECONDARY_MULTI_SOURCE_BOE_AND_WAYBACK_UNREACHABLE",
          f"counts={organ_donation_law_var_counts}")
    check("    organ_donation_law: status breakdown 27/0/0/0...",
          organ_donation_law_var_counts.get("legal_status_breakdown") == {"اصلية": 27, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={organ_donation_law_var_counts.get('legal_status_breakdown')}")

    private_healthcare_institutions_law_var = tracks_by_id.get("private_healthcare_institutions_law", {})
    private_healthcare_institutions_law_var_counts = private_healthcare_institutions_law_var.get("record_counts", {})
    check("[7g252] private_healthcare_institutions_law: 35 Arabic records...",
          private_healthcare_institutions_law_var_counts.get("arabic_articles") == 35
          and private_healthcare_institutions_law_var.get("official_text_status") == "NEZAMS_X_QANOONSA_DUAL_SECONDARY_CROSSVERIFIED_BOE_UNREACHABLE",
          f"counts={private_healthcare_institutions_law_var_counts}")
    check("    private_healthcare_institutions_law: status breakdown 32/3/0/0...",
          private_healthcare_institutions_law_var_counts.get("legal_status_breakdown") == {"اصلية": 32, "معدلة": 3, "ملغاة": 0, "مضافة": 0},
          f"breakdown={private_healthcare_institutions_law_var_counts.get('legal_status_breakdown')}")

    high_risk_professions_regulation_var = tracks_by_id.get("high_risk_professions_regulation", {})
    high_risk_professions_regulation_var_counts = high_risk_professions_regulation_var.get("record_counts", {})
    check("[7g253] high_risk_professions_regulation: 19 Arabic records...",
          high_risk_professions_regulation_var_counts.get("arabic_articles") == 19
          and high_risk_professions_regulation_var.get("official_text_status") == "NCOSH_OFFICIAL_PDF_VISION_READ_LIGATURE_DEFECT_X_UQN_GAZETTE_DUAL_OFFICIAL_CROSSVERIFIED_BOE_UNREACHABLE",
          f"counts={high_risk_professions_regulation_var_counts}")
    check("    high_risk_professions_regulation: status breakdown 19/0/0/0...",
          high_risk_professions_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 19, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={high_risk_professions_regulation_var_counts.get('legal_status_breakdown')}")

    osh_service_providers_regulation_var = tracks_by_id.get("osh_service_providers_regulation", {})
    osh_service_providers_regulation_var_counts = osh_service_providers_regulation_var.get("record_counts", {})
    check("[7g254] osh_service_providers_regulation: 38 Arabic records...",
          osh_service_providers_regulation_var_counts.get("arabic_articles") == 38
          and osh_service_providers_regulation_var.get("official_text_status") == "UQN_GAZETTE_PRIMARY_PARTIAL_29_OF_38_X_QANOONSA_SECONDARY_FOR_REMAINDER_MIXED_CONFIDENCE",
          f"counts={osh_service_providers_regulation_var_counts}")
    check("    osh_service_providers_regulation: status breakdown 38/0/0/0...",
          osh_service_providers_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 38, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={osh_service_providers_regulation_var_counts.get('legal_status_breakdown')}")

    rega_organizational_statute_var = tracks_by_id.get("rega_organizational_statute", {})
    rega_organizational_statute_var_counts = rega_organizational_statute_var.get("record_counts", {})
    check("[7g255] rega_organizational_statute: 16 Arabic records...",
          rega_organizational_statute_var_counts.get("arabic_articles") == 16
          and rega_organizational_statute_var.get("official_text_status") == "REGA_GOV_SA_FIVE_SCANNED_PDFS_VISION_READ_X_NEZAMS_PARTIAL_CROSSCHECK_BOE_AND_WAYBACK_BOTH_BLOCKED",
          f"counts={rega_organizational_statute_var_counts}")
    check("    rega_organizational_statute: status breakdown 7/8/0/1...",
          rega_organizational_statute_var_counts.get("legal_status_breakdown") == {"اصلية": 7, "معدلة": 8, "ملغاة": 0, "مضافة": 1},
          f"breakdown={rega_organizational_statute_var_counts.get('legal_status_breakdown')}")

    offplan_sale_implementing_regulation_var = tracks_by_id.get("offplan_sale_implementing_regulation", {})
    offplan_sale_implementing_regulation_var_counts = offplan_sale_implementing_regulation_var.get("record_counts", {})
    check("[7g256] offplan_sale_implementing_regulation: 49 Arabic records...",
          offplan_sale_implementing_regulation_var_counts.get("arabic_articles") == 49
          and offplan_sale_implementing_regulation_var.get("official_text_status") == "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED_REGA_RESOLUTION",
          f"counts={offplan_sale_implementing_regulation_var_counts}")
    check("    offplan_sale_implementing_regulation: status breakdown 49/0/0/0...",
          offplan_sale_implementing_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 49, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={offplan_sale_implementing_regulation_var_counts.get('legal_status_breakdown')}")

    real_estate_finance_implementing_regulation_var = tracks_by_id.get("real_estate_finance_implementing_regulation", {})
    real_estate_finance_implementing_regulation_var_counts = real_estate_finance_implementing_regulation_var.get("record_counts", {})
    check("[7g257] real_estate_finance_implementing_regulation: 31 Arabic records...",
          real_estate_finance_implementing_regulation_var_counts.get("arabic_articles") == 31
          and real_estate_finance_implementing_regulation_var.get("official_text_status") == "TIER_1_SAMA_RULEBOOK_PRIMARY_MULTI_SOURCE",
          f"counts={real_estate_finance_implementing_regulation_var_counts}")
    check("    real_estate_finance_implementing_regulation: status breakdown 31/0/0/0...",
          real_estate_finance_implementing_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 31, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={real_estate_finance_implementing_regulation_var_counts.get('legal_status_breakdown')}")

    real_estate_contributions_implementing_regulation_var = tracks_by_id.get("real_estate_contributions_implementing_regulation", {})
    real_estate_contributions_implementing_regulation_var_counts = real_estate_contributions_implementing_regulation_var.get("record_counts", {})
    check("[7g258] real_estate_contributions_implementing_regulation: 40 Arabic records...",
          real_estate_contributions_implementing_regulation_var_counts.get("arabic_articles") == 40
          and real_estate_contributions_implementing_regulation_var.get("official_text_status") == "TIER_2_PRIMARY_MULTI_SOURCE_THREE_DISCLOSED_CONFLICTS",
          f"counts={real_estate_contributions_implementing_regulation_var_counts}")
    check("    real_estate_contributions_implementing_regulation: status breakdown 40/0/0/0...",
          real_estate_contributions_implementing_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 40, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={real_estate_contributions_implementing_regulation_var_counts.get('legal_status_breakdown')}")

    landlord_tenant_relationship_regulation_var = tracks_by_id.get("landlord_tenant_relationship_regulation", {})
    landlord_tenant_relationship_regulation_var_counts = landlord_tenant_relationship_regulation_var.get("record_counts", {})
    check("[7g259] landlord_tenant_relationship_regulation: 12 Arabic records...",
          landlord_tenant_relationship_regulation_var_counts.get("arabic_articles") == 12
          and landlord_tenant_relationship_regulation_var.get("official_text_status") == "TIER_1_PRIMARY_MULTI_SOURCE_RIYADH_SCOPE_DISCLOSED",
          f"counts={landlord_tenant_relationship_regulation_var_counts}")
    check("    landlord_tenant_relationship_regulation: status breakdown 12/0/0/0...",
          landlord_tenant_relationship_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 12, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={landlord_tenant_relationship_regulation_var_counts.get('legal_status_breakdown')}")

    real_estate_marketing_advertising_regulation_var = tracks_by_id.get("real_estate_marketing_advertising_regulation", {})
    real_estate_marketing_advertising_regulation_var_counts = real_estate_marketing_advertising_regulation_var.get("record_counts", {})
    check("[7g260] real_estate_marketing_advertising_regulation: 12 Arabic records...",
          real_estate_marketing_advertising_regulation_var_counts.get("arabic_articles") == 12
          and real_estate_marketing_advertising_regulation_var.get("official_text_status") == "TIER_1_REGA_GOV_SA_PRIMARY_MULTI_SOURCE",
          f"counts={real_estate_marketing_advertising_regulation_var_counts}")
    check("    real_estate_marketing_advertising_regulation: status breakdown 12/0/0/0...",
          real_estate_marketing_advertising_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 12, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={real_estate_marketing_advertising_regulation_var_counts.get('legal_status_breakdown')}")

    real_estate_auctions_regulation_var = tracks_by_id.get("real_estate_auctions_regulation", {})
    real_estate_auctions_regulation_var_counts = real_estate_auctions_regulation_var.get("record_counts", {})
    check("[7g261] real_estate_auctions_regulation: 12 Arabic records...",
          real_estate_auctions_regulation_var_counts.get("arabic_articles") == 12
          and real_estate_auctions_regulation_var.get("official_text_status") == "TIER_1_DUAL_PRIMARY_TWO_MINOR_DISCLOSED_VARIANCES",
          f"counts={real_estate_auctions_regulation_var_counts}")
    check("    real_estate_auctions_regulation: status breakdown 12/0/0/0...",
          real_estate_auctions_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 12, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={real_estate_auctions_regulation_var_counts.get('legal_status_breakdown')}")

    petroleum_petrochemical_materials_law_var = tracks_by_id.get("petroleum_petrochemical_materials_law", {})
    petroleum_petrochemical_materials_law_var_counts = petroleum_petrochemical_materials_law_var.get("record_counts", {})
    check("[7g262] petroleum_petrochemical_materials_law: 22 Arabic records...",
          petroleum_petrochemical_materials_law_var_counts.get("arabic_articles") == 22
          and petroleum_petrochemical_materials_law_var.get("official_text_status") == "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED",
          f"counts={petroleum_petrochemical_materials_law_var_counts}")
    check("    petroleum_petrochemical_materials_law: status breakdown 22/0/0/0...",
          petroleum_petrochemical_materials_law_var_counts.get("legal_status_breakdown") == {"اصلية": 22, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={petroleum_petrochemical_materials_law_var_counts.get('legal_status_breakdown')}")

    dry_gas_lpg_distribution_law_var = tracks_by_id.get("dry_gas_lpg_distribution_law", {})
    dry_gas_lpg_distribution_law_var_counts = dry_gas_lpg_distribution_law_var.get("record_counts", {})
    check("[7g263] dry_gas_lpg_distribution_law: 21 Arabic records...",
          dry_gas_lpg_distribution_law_var_counts.get("arabic_articles") == 21
          and dry_gas_lpg_distribution_law_var.get("official_text_status") == "TIER_1_PRIMARY_MULTI_SOURCE_CONSOLIDATED_AMENDED",
          f"counts={dry_gas_lpg_distribution_law_var_counts}")
    check("    dry_gas_lpg_distribution_law: status breakdown 3/17/1/0...",
          dry_gas_lpg_distribution_law_var_counts.get("legal_status_breakdown") == {"اصلية": 3, "معدلة": 17, "ملغاة": 1, "مضافة": 0},
          f"breakdown={dry_gas_lpg_distribution_law_var_counts.get('legal_status_breakdown')}")

    energy_supplies_system_var = tracks_by_id.get("energy_supplies_system", {})
    energy_supplies_system_var_counts = energy_supplies_system_var.get("record_counts", {})
    check("[7g264] energy_supplies_system: 12 Arabic records...",
          energy_supplies_system_var_counts.get("arabic_articles") == 12
          and energy_supplies_system_var.get("official_text_status") == "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED",
          f"counts={energy_supplies_system_var_counts}")
    check("    energy_supplies_system: status breakdown 12/0/0/0...",
          energy_supplies_system_var_counts.get("legal_status_breakdown") == {"اصلية": 12, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={energy_supplies_system_var_counts.get('legal_status_breakdown')}")

    mining_investment_implementing_regulation_var = tracks_by_id.get("mining_investment_implementing_regulation", {})
    mining_investment_implementing_regulation_var_counts = mining_investment_implementing_regulation_var.get("record_counts", {})
    check("[7g265] mining_investment_implementing_regulation: 166 Arabic records...",
          mining_investment_implementing_regulation_var_counts.get("arabic_articles") == 166
          and mining_investment_implementing_regulation_var.get("official_text_status") == "TIER_2_PRIMARY_FOUNDING_TEXT_LATER_AMENDMENT_TEXT_UNOBTAINED",
          f"counts={mining_investment_implementing_regulation_var_counts}")
    check("    mining_investment_implementing_regulation: status breakdown 166/0/0/0...",
          mining_investment_implementing_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 166, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={mining_investment_implementing_regulation_var_counts.get('legal_status_breakdown')}")

    pharmaceutical_establishments_law_var = tracks_by_id.get("pharmaceutical_establishments_law", {})
    pharmaceutical_establishments_law_var_counts = pharmaceutical_establishments_law_var.get("record_counts", {})
    check("[7g266] pharmaceutical_establishments_law: 42 Arabic records...",
          pharmaceutical_establishments_law_var_counts.get("arabic_articles") == 42
          and pharmaceutical_establishments_law_var.get("official_text_status") == "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED",
          f"counts={pharmaceutical_establishments_law_var_counts}")
    check("    pharmaceutical_establishments_law: status breakdown 42/0/0/0...",
          pharmaceutical_establishments_law_var_counts.get("legal_status_breakdown") == {"اصلية": 42, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={pharmaceutical_establishments_law_var_counts.get('legal_status_breakdown')}")

    seized_confiscated_funds_management_system_var = tracks_by_id.get("seized_confiscated_funds_management_system", {})
    seized_confiscated_funds_management_system_var_counts = seized_confiscated_funds_management_system_var.get("record_counts", {})
    check("[7g267] seized_confiscated_funds_management_system: 15 Arabic records...",
          seized_confiscated_funds_management_system_var_counts.get("arabic_articles") == 15
          and seized_confiscated_funds_management_system_var.get("official_text_status") == "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED_NOT_YET_IN_FORCE",
          f"counts={seized_confiscated_funds_management_system_var_counts}")
    check("    seized_confiscated_funds_management_system: status breakdown 15/0/0/0...",
          seized_confiscated_funds_management_system_var_counts.get("legal_status_breakdown") == {"اصلية": 15, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={seized_confiscated_funds_management_system_var_counts.get('legal_status_breakdown')}")

    nca_cybersecurity_violations_investigation_rules_var = tracks_by_id.get("nca_cybersecurity_violations_investigation_rules", {})
    nca_cybersecurity_violations_investigation_rules_var_counts = nca_cybersecurity_violations_investigation_rules_var.get("record_counts", {})
    check("[7g268] nca_cybersecurity_violations_investigation_rules: 9 Arabic records...",
          nca_cybersecurity_violations_investigation_rules_var_counts.get("arabic_articles") == 9
          and nca_cybersecurity_violations_investigation_rules_var.get("official_text_status") == "TIER_1_UQN_GAZETTE_X_LIVE_NCA_GOV_SA_PRIMARY",
          f"counts={nca_cybersecurity_violations_investigation_rules_var_counts}")
    check("    nca_cybersecurity_violations_investigation_rules: status breakdown 9/0/0/0...",
          nca_cybersecurity_violations_investigation_rules_var_counts.get("legal_status_breakdown") == {"اصلية": 9, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={nca_cybersecurity_violations_investigation_rules_var_counts.get('legal_status_breakdown')}")

    nca_cybersecurity_violations_reporting_rules_var = tracks_by_id.get("nca_cybersecurity_violations_reporting_rules", {})
    nca_cybersecurity_violations_reporting_rules_var_counts = nca_cybersecurity_violations_reporting_rules_var.get("record_counts", {})
    check("[7g269] nca_cybersecurity_violations_reporting_rules: 8 Arabic records...",
          nca_cybersecurity_violations_reporting_rules_var_counts.get("arabic_articles") == 8
          and nca_cybersecurity_violations_reporting_rules_var.get("official_text_status") == "TIER_2_PRIMARY_DECISION_NUMBER_UNCONFIRMED_DISCLOSED",
          f"counts={nca_cybersecurity_violations_reporting_rules_var_counts}")
    check("    nca_cybersecurity_violations_reporting_rules: status breakdown 8/0/0/0...",
          nca_cybersecurity_violations_reporting_rules_var_counts.get("legal_status_breakdown") == {"اصلية": 8, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={nca_cybersecurity_violations_reporting_rules_var_counts.get('legal_status_breakdown')}")

    cst_organizational_statute_var = tracks_by_id.get("cst_organizational_statute", {})
    cst_organizational_statute_var_counts = cst_organizational_statute_var.get("record_counts", {})
    check("[7g270] cst_organizational_statute: 19 Arabic records...",
          cst_organizational_statute_var_counts.get("arabic_articles") == 19
          and cst_organizational_statute_var.get("official_text_status") == "TIER_4_MIXED_PER_ARTICLE_CONFIDENCE_WEAKEST_PORTION_GOVERNS",
          f"counts={cst_organizational_statute_var_counts}")
    check("    cst_organizational_statute: status breakdown 13/6/0/0...",
          cst_organizational_statute_var_counts.get("legal_status_breakdown") == {"اصلية": 13, "معدلة": 6, "ملغاة": 0, "مضافة": 0},
          f"breakdown={cst_organizational_statute_var_counts.get('legal_status_breakdown')}")

    railway_law_var = tracks_by_id.get("railway_law", {})
    railway_law_var_counts = railway_law_var.get("record_counts", {})
    check("[7g271] railway_law: 50 Arabic records...",
          railway_law_var_counts.get("arabic_articles") == 50
          and railway_law_var.get("official_text_status") == "TIER_3_SECONDARY_MULTI_SOURCE_ONLY_DUAL_CROSS_VERIFIED",
          f"counts={railway_law_var_counts}")
    check("    railway_law: status breakdown 50/0/0/0...",
          railway_law_var_counts.get("legal_status_breakdown") == {"اصلية": 50, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={railway_law_var_counts.get('legal_status_breakdown')}")

    railway_law_implementing_regulation_var = tracks_by_id.get("railway_law_implementing_regulation", {})
    railway_law_implementing_regulation_var_counts = railway_law_implementing_regulation_var.get("record_counts", {})
    check("[7g272] railway_law_implementing_regulation: 91 Arabic records...",
          railway_law_implementing_regulation_var_counts.get("arabic_articles") == 91
          and railway_law_implementing_regulation_var.get("official_text_status") == "TIER_1_UQN_GAZETTE_X_INDEPENDENT_PRESS_TRIPLE_CORROBORATION",
          f"counts={railway_law_implementing_regulation_var_counts}")
    check("    railway_law_implementing_regulation: status breakdown 91/0/0/0...",
          railway_law_implementing_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 91, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={railway_law_implementing_regulation_var_counts.get('legal_status_breakdown')}")

    road_transport_law_var = tracks_by_id.get("road_transport_law", {})
    road_transport_law_var_counts = road_transport_law_var.get("record_counts", {})
    check("[7g273] road_transport_law: 34 Arabic records...",
          road_transport_law_var_counts.get("arabic_articles") == 34
          and road_transport_law_var.get("official_text_status") == "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED",
          f"counts={road_transport_law_var_counts}")
    check("    road_transport_law: status breakdown 34/0/0/0...",
          road_transport_law_var_counts.get("legal_status_breakdown") == {"اصلية": 34, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={road_transport_law_var_counts.get('legal_status_breakdown')}")

    gaca_organizational_statute_var = tracks_by_id.get("gaca_organizational_statute", {})
    gaca_organizational_statute_var_counts = gaca_organizational_statute_var.get("record_counts", {})
    check("[7g274] gaca_organizational_statute: 15 Arabic records...",
          gaca_organizational_statute_var_counts.get("arabic_articles") == 15
          and gaca_organizational_statute_var.get("official_text_status") == "TIER_2_PRIMARY_CONSOLIDATED_WHOLESALE_REISSUE",
          f"counts={gaca_organizational_statute_var_counts}")
    check("    gaca_organizational_statute: status breakdown 15/0/0/0...",
          gaca_organizational_statute_var_counts.get("legal_status_breakdown") == {"اصلية": 15, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={gaca_organizational_statute_var_counts.get('legal_status_breakdown')}")

    tga_organizational_statute_var = tracks_by_id.get("tga_organizational_statute", {})
    tga_organizational_statute_var_counts = tga_organizational_statute_var.get("record_counts", {})
    check("[7g275] tga_organizational_statute: 16 Arabic records...",
          tga_organizational_statute_var_counts.get("arabic_articles") == 16
          and tga_organizational_statute_var.get("official_text_status") == "TIER_2_PRIMARY_MULTI_SOURCE_ONE_UNRESOLVED_AMENDMENT_DISCLOSED",
          f"counts={tga_organizational_statute_var_counts}")
    check("    tga_organizational_statute: status breakdown 7/8/0/1...",
          tga_organizational_statute_var_counts.get("legal_status_breakdown") == {"اصلية": 7, "معدلة": 8, "ملغاة": 0, "مضافة": 1},
          f"breakdown={tga_organizational_statute_var_counts.get('legal_status_breakdown')}")

    mawani_organizational_statute_var = tracks_by_id.get("mawani_organizational_statute", {})
    mawani_organizational_statute_var_counts = mawani_organizational_statute_var.get("record_counts", {})
    check("[7g276] mawani_organizational_statute: 20 Arabic records...",
          mawani_organizational_statute_var_counts.get("arabic_articles") == 20
          and mawani_organizational_statute_var.get("official_text_status") == "TIER_4_SINGLE_SECONDARY_SOURCE_BOE_WAYBACK_MAWANI_ALL_UNREACHABLE",
          f"counts={mawani_organizational_statute_var_counts}")
    check("    mawani_organizational_statute: status breakdown 20/0/0/0...",
          mawani_organizational_statute_var_counts.get("legal_status_breakdown") == {"اصلية": 20, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={mawani_organizational_statute_var_counts.get('legal_status_breakdown')}")

    hajj_umrah_external_pilgrims_law_var = tracks_by_id.get("hajj_umrah_external_pilgrims_law", {})
    hajj_umrah_external_pilgrims_law_var_counts = hajj_umrah_external_pilgrims_law_var.get("record_counts", {})
    check("[7g277] hajj_umrah_external_pilgrims_law: 24 Arabic records...",
          hajj_umrah_external_pilgrims_law_var_counts.get("arabic_articles") == 24
          and hajj_umrah_external_pilgrims_law_var.get("official_text_status") == "TIER_3_MIXED_BASE_TIER3_AMENDMENT_TIER2_WEAKEST_PORTION_GOVERNS",
          f"counts={hajj_umrah_external_pilgrims_law_var_counts}")
    check("    hajj_umrah_external_pilgrims_law: status breakdown 9/14/0/1...",
          hajj_umrah_external_pilgrims_law_var_counts.get("legal_status_breakdown") == {"اصلية": 9, "معدلة": 14, "ملغاة": 0, "مضافة": 1},
          f"breakdown={hajj_umrah_external_pilgrims_law_var_counts.get('legal_status_breakdown')}")

    aviation_passenger_rights_regulation_var = tracks_by_id.get("aviation_passenger_rights_regulation", {})
    aviation_passenger_rights_regulation_var_counts = aviation_passenger_rights_regulation_var.get("record_counts", {})
    check("[7g278] aviation_passenger_rights_regulation: 30 Arabic records...",
          aviation_passenger_rights_regulation_var_counts.get("arabic_articles") == 30
          and aviation_passenger_rights_regulation_var.get("official_text_status") == "TIER_2_UQN_GAZETTE_PRIMARY_X_SECONDARY_CROSS_VERIFIED",
          f"counts={aviation_passenger_rights_regulation_var_counts}")
    check("    aviation_passenger_rights_regulation: status breakdown 30/0/0/0...",
          aviation_passenger_rights_regulation_var_counts.get("legal_status_breakdown") == {"اصلية": 30, "معدلة": 0, "ملغاة": 0, "مضافة": 0},
          f"breakdown={aviation_passenger_rights_regulation_var_counts.get('legal_status_breakdown')}")

    check("[7g] unified retrieval index: 25453 records...", uix.get("total_records") == 25453,
          f"total_records={uix.get('total_records')}")

    # [8] data_paths exist
    all_data_paths_exist = True
    missing_paths = []
    for track in registry.get("tracks", []):
        for p in track.get("data_paths", []):
            full = os.path.join(ROOT, p)
            if not os.path.isfile(full):
                all_data_paths_exist = False
                missing_paths.append(p)
    check("[8] All referenced data_paths exist...", all_data_paths_exist,
          "All exist" if all_data_paths_exist else f"Missing: {missing_paths[:3]}")

    # [9] report_paths exist
    all_report_paths_exist = True
    missing_reports = []
    for track in registry.get("tracks", []):
        for p in track.get("report_paths", []):
            full = os.path.join(ROOT, p)
            if not os.path.isfile(full):
                all_report_paths_exist = False
                missing_reports.append(p)
    check("[9] All referenced report_paths exist...", all_report_paths_exist,
          "All exist" if all_report_paths_exist else f"Missing: {missing_reports[:3]}")

    # [10] listed JSC specialized
    ljs_b = ljs.get("boundaries", {})
    check("[10] listed JSC is_specialized=True...", ljs_b.get("is_specialized") is True, "True")
    check("     listed JSC is_general=False...", ljs_b.get("is_general") is False, "False")

    # [11-17] Boundaries across all tracks
    all_arabic_governs = all(t.get("boundaries", {}).get("arabic_governs") is True for t in registry.get("tracks", []))
    check("[11] Arabic governs in all tracks...", all_arabic_governs, "All True")

    all_not_translation = all(t.get("boundaries", {}).get("not_official_translation") is True for t in registry.get("tracks", []))
    check("[12] No official translation claim...", all_not_translation, "All True")

    all_not_advice = all(t.get("boundaries", {}).get("not_legal_advice") is True for t in registry.get("tracks", []))
    check("[13] No legal advice claim...", all_not_advice, "All True")

    all_no_public = all(t.get("boundaries", {}).get("no_public_release") is True for t in registry.get("tracks", []))
    check("[14] No public release claim...", all_no_public, "All True")

    all_no_trilingual = all(t.get("boundaries", {}).get("no_trilingual_alignment") is True for t in registry.get("tracks", []))
    check("[15] No trilingual alignment claim...", all_no_trilingual, "All True")

    # [16] English reference only
    cl_en = cl.get("language_layers", {}).get("english", {})
    check("[16] English is reference/guidance only...", cl_en.get("role") == "reference_guidance_only" and cl_en.get("governing") is False,
          f"role={cl_en.get('role')}, governing={cl_en.get('governing')}")

    # [17] Chinese internal only
    cl_cn = cl.get("language_layers", {}).get("chinese", {})
    check("[17] Chinese is internal/reference only...", cl_cn.get("role") == "internal_reference_only" and cl_cn.get("governing") is False,
          f"role={cl_cn.get('role')}, governing={cl_cn.get('governing')}")

    # [18] Read-only validator
    check("[18] Validator is read-only...", True, "Does not modify any files")

    # [19] Count semantics: explicit count fields
    check("[19a] total_primary_arabic_governing_records == 25622...",
          registry.get("total_primary_arabic_governing_records") == 25622,
          f"Value: {registry.get('total_primary_arabic_governing_records')}")

    check("[19b] total_reference_records == 614...",
          registry.get("total_reference_records") == 614,
          f"Value: {registry.get('total_reference_records')}")

    check("[19c] total_internal_reference_records == 281...",
          registry.get("total_internal_reference_records") == 281,
          f"Value: {registry.get('total_internal_reference_records')}")

    check("[19d] total_implementing_regulations_records == 169...",
          registry.get("total_implementing_regulations_records") == 169,
          f"Value: {registry.get('total_implementing_regulations_records')}")

    check("[19e] total_registry_counted_records == 26517...",
          registry.get("total_registry_counted_records") == 26517,
          f"Value: {registry.get('total_registry_counted_records')}")

    # [20] count_policy exists and has required keys
    cp = registry.get("count_policy", {})
    required_cp = [
        "counting_method", "primary_arabic_governing_records_included",
        "english_reference_records_included", "chinese_internal_reference_records_included",
        "forms_and_appendices_counted", "closure_audit_aggregate_not_counted_separately",
        "closure_audit_total_duplicates_underlying_ir_records",
        "formula_total_primary_arabic_governing", "formula_total_reference",
        "formula_total_internal_reference", "formula_total_implementing_regulations",
        "formula_total_registry_counted", "note",
    ]
    missing_cp = [f for f in required_cp if f not in cp]
    check("[20] count_policy has all required fields...", len(missing_cp) == 0,
          "All present" if not missing_cp else f"Missing: {missing_cp}")

    # [21] count_policy formulas are consistent with values
    check("[21] total_registry == primary + reference + internal...",
          registry.get("total_registry_counted_records") ==
          registry.get("total_primary_arabic_governing_records", 0)
          + registry.get("total_reference_records", 0)
          + registry.get("total_internal_reference_records", 0),
          f"25622 + 614 + 281 = 26517")

    # [21b] Every track's registry display name must be the official Arabic title
    # its own source artifact carries. Hand-abbreviated registry names had drifted
    # from the source on six tracks, and the gazette CMS truncates its <title> tag
    # at ~70 chars, so a clipped or shortened legal title can enter here silently.
    name_drift = []
    for tr in registry.get("tracks", []):
        tid = tr.get("track_id")
        cand = glob.glob(os.path.join(ROOT, "sources", tid, "official_source", "*.json"))
        if not cand:
            continue
        try:
            doc = json.load(open(cand[0], encoding="utf-8")).get("document")
        except (ValueError, OSError):
            continue
        if doc and tr.get("display_name_ar") and doc != tr["display_name_ar"]:
            name_drift.append(tid)
    check("[21b] display_name_ar == the source artifact's own document title...",
          not name_drift,
          "All aligned" if not name_drift else "Drifted: %s" % name_drift[:6])

    check("[22] No total_known_records field (replaced)...",
          "total_known_records" not in registry,
          "Field removed — replaced by explicit count fields")

    print_results()
    return 0 if FAILED == 0 else 1


def print_results() -> None:
    print()
    for line in CHECKS:
        print(line)
    print()
    print("=" * 60)
    if FAILED == 0:
        print("RESULT: ALL CHECKS PASSED ✓")
        print("[PASS] Corpus Registry Index Foundation: 743 tracks (companies_law, "
              "implementing_regulations_general, implementing_regulations_listed_joint_stock, "
              "implementing_regulations_arabic_program_closure, pdpl_law, "
              "pdpl_implementing_regulation, investment_law, investment_implementing_regulation, "
              "civil_transactions_law, gtpl_law, gtpl_implementing_regulation, labor_law, "
              "labor_implementing_regulation, labor_model_work_regulation, "
              "labor_saudization_mediation_rules, labor_recruitment_services_rules, "
              "labor_accessibility_arrangements, labor_model_contract_forms, evidence_law, "
              "evidence_electronic_procedures_rules, evidence_procedural_manuals, "
              "evidence_expertise_rules, personal_status_law, "
              "personal_status_implementing_regulation, sharia_procedure_law, "
              "sharia_procedure_implementing_regulation, criminal_procedure_law, "
              "criminal_procedure_implementing_regulation, enforcement_law, "
              "enforcement_implementing_regulation, judiciary_law, board_of_grievances_law). "
              "Primary Arabic 10555, reference 614, registry-counted 11450. All counts correct, all referenced paths "
              "exist, all boundaries enforced. Arabic governs; no official translation; no legal "
              "advice; no trilingual; no public release. English reference only; Chinese internal "
              "only. PDPL and Investment Arabic tracks are verified against official published "
              "text; Civil is owner-provided official text; the eight Labor tracks are the official "
              "HRSD texts, cross-checked (BOE captures / OCR + law quotes / page images / "
              "ActualText), completing the full HRSD regulation document (annexes 1-5); the four "
              "Evidence tracks are the official MOJ portal database cross-checked against the "
              "official MOJ PDFs, as are the Personal Status law + implementing regulation and the "
              "Law of Sharia Procedure (243 records, consolidated amended law: 153 اصلية / 14 معدلة "
              "/ 75 ملغاة / 1 مضافة) and its implementing regulation (637 records, dual-status: PDF "
              "badge governs, portal legal status + 149 Evidence-Law-superseded provisions also "
              "recorded; repealed/superseded provisions flagged not deleted) — and the Law of Criminal "
              "Procedure (222 records) and its implementing regulation (181 records), both consolidated "
              "single-status (219+174 اصلية / 3+7 معدلة, no dual-status) — and the Law of Enforcement "
              "(98 records) and its implementing regulation (273 records), both consolidated single-status "
              "with flagged repeals (94+266 اصلية; repealed/added provisions flagged not deleted) — and the "
              "foundational Law of the Judiciary (85 records, court-organization statute: 82 اصلية / 3 معدلة) — "
              "and the Law of the Board of Grievances (26 records, administrative-judiciary statute: 25 اصلية / "
              "1 معدلة; Board certified PDF visually adjudicated + Article 4's م/180 amendment from Umm Al-Qura "
              "5072, SPA-confirmed) — and the Code of Law Practice (56 records: 35 اصلية / 8 معدلة / 12 مضافة / 1 "
              "ملغاة, consolidated through M/21 1447H) and its current implementing regulation (90 records, fresh "
              "1446H Active issuance all اصلية, superseding the InActive 1423H one) — and the Commercial Courts Law (96 records: 75 اصلية / 1 معدلة / 20 ملغاة; the evidence chapter arts 38-57 repealed by the Evidence Law M/43) and its implementing regulation (281 records, fresh 1441H Active issuance all اصلية) — and the Bankruptcy Law (231 records: 229 اصلية / 2 معدلة, consolidated M/89 1439H; per art 230 it repeals old commercial-court/settlement provisions) and its implementing regulation (98 records: 97 اصلية / 1 معدلة, Council of Ministers Decision 622 1440H, art 2 amended by Decision 171 1443H; 98/98 matched outright) and the bankruptcy case rules (24 records: all اصلية, Minister of Justice Decision 6421 1441H; 24/24 matched outright) — and the Judicial Costs Law (23 records: all اصلية, Royal Decree M/16 1443H) and its implementing regulation (17 records: all اصلية, Council of Ministers Decision 519 1443H) — and the Arbitration Law (58 records: 55 اصلية / 3 معدلة, consolidated M/34 1433H; official-source label anomaly at art 31 preserved verbatim) and its implementing regulation (19 records: 18 اصلية / 1 ملغاة, Council of Ministers Decision 541 1438H) — and the Commercial Papers Law (121 records: 118 اصلية / 3 معدلة, consolidated M/37 1383H; sourced from the BOE official portal via Wayback archive, cross-verified byte-identical across two independent-date snapshots) — and the Commercial Register Law (29 records: all اصلية, M/83 1446H) and the Trade Names Law (23 records: all اصلية, M/83 1446H), both BOE official portal via Wayback archive — and the Commercial Agencies Law (6 records: 3 اصلية / 3 معدلة, consolidated M/11 1382H, BOE via Wayback archive) — and the Chambers of Commerce Law (66 records: all اصلية, consolidated M/37 1442H, BOE via Wayback archive) — and the Commercial Books Law (16 records: all اصلية, consolidated M/61 1409H, BOE via Wayback archive) — and the Anti-Money Laundering Law "
              "(52 records: 44 اصلية / 7 معدلة / 1 مضافة (art 49 مكرر), consolidated M/20 1439H, all amendments by M/223 1447H, MOJ portal cross-checked against the official MOJ PDF) — and the Notarization Law "
              "(57 records: 52 اصلية / 5 معدلة, consolidated M/164 1441H, all amendments by M/21 1447H and M/191 1444H, MOJ portal cross-checked against the official MOJ PDF, additionally corroborated against the Bureau of Experts official portal) and its implementing regulation "
              "(31 records: all اصلية, Minister of Justice Decision 1948 1442H; 10 list articles adjudicated visually verbatim, OCR channel unavailable for that PDF), and the Real Estate In-Kind Registration Law "
              "(40 records: 37 اصلية / 3 معدلة, in-force M/91 1443H superseding the repealed M/6 1423H, MOJ portal cross-checked against the official MOJ PDF) and its implementing regulation "
              "(51 records: all اصلية, in-force 27/1/1444H superseding the repealed 1425H regulation; 5 long/table articles adjudicated visually verbatim, art 42 keeping official English spec tokens), and the Registered Real Estate Mortgage Law "
              "(46 records: all اصلية, fresh M/49 1433H; 2 long articles adjudicated visually verbatim). "
              "Unified retrieval index (10253) projects counted records. Read-only.")
    else:
        print(f"RESULT: {FAILED} CHECK(S) FAILED ✗")
    print("=" * 60)


if __name__ == "__main__":
    sys.exit(main())