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
    labor_en_count = sum(
        sum(1 for line in open(p, encoding="utf-8") if line.strip())
        for p in sorted(glob.glob(LABOR_EN_REF_GLOB))
    )
    unified_index = _load_json(UNIFIED_INDEX)

    registry: dict[str, Any] = {
        "registry_version": "2.3",
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
        "total_tracks": 24,
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
            "formula_total_primary_arabic_governing": "companies_law_arabic(281) + general_ir_articles(95) + general_ir_forms(4) + listed_jsc_articles(69) + listed_jsc_appendix(1) + pdpl_law(43) + pdpl_implementing_regulation(38) + investment_law(16) + investment_implementing_regulation(37) + civil_transactions_law(721) + gtpl_law(99) + gtpl_implementing_regulation(157) + labor_law(249) + labor_implementing_regulation(45) + labor_model_work_regulation(72) + labor_annex1_violation_tables(3) + labor_annex3_mediation_rules(20) + labor_annex4_recruitment_rules(72) + labor_annex2_accessibility_tables(8) + labor_annex5_contract_forms(102) + evidence_law(129) + evidence_electronic_rules(24) + evidence_procedural_manuals(135) + evidence_expertise_rules(34) + personal_status_law(252) + personal_status_regulation(41) = 2747",
            "formula_total_reference": "companies_law_english(281) + gtpl_english_boe_translation(99) + labor_law_english(234) = 614",
            "formula_total_internal_reference": "companies_law_chinese_remediation(281)",
            "formula_total_implementing_regulations": "companies-family only: general_articles(95) + general_forms(4) + listed_jsc_articles(69) + listed_jsc_appendix(1) = 169 (PDPL and Investment regulations are counted under their own primary Arabic tracks)",
            "formula_total_registry_counted": "total_primary_arabic_governing(2747) + total_reference(614) + total_internal_reference(281) = 3642",
            "pdpl_arabic_records_status": "PDPL law (43) and implementing regulation (38) are now VERIFIED against the official SDAIA-published text (cross-checked against independent OCR/extraction) and carry LLM-ready enrichment layers. Arabic governs; not legal advice.",
            "investment_arabic_records_status": "Investment law (16) and implementing regulation (37) are verified from the official Ministry of Investment (MISA) Arabic PDFs and carry LLM-ready enrichment layers. Arabic governs; not legal advice.",
            "civil_arabic_records_status": "Civil Transactions Law (721) is the owner-provided full official Arabic text (Royal Decree M/191, 1444H), now CROSS-CHECKED article-by-article against the official MOJ legal-portal database (721/721 aligned, law unamended) with divergences adjudicated visually against the official MOJ PDF (committed): 17 single-word defects corrected and 21 trailing structural headings moved to section_context, all documented in the source artifact and audit files under sources/civil/law/moj_cross_check/. Arabic governs; not legal advice.",
            "labor_arabic_records_status": "Labor Law (249 records: 245 articles + 4 مكرر; 38 officially deleted flagged) is the official HRSD consolidated text (Royal Decree M/51, 1426H, amendments through M/44 merged), cross-verified against the repository's independently captured BOE base texts with ZERO unexplained differences. The Labor implementing regulation (45 records: articles 1-40 + 5 مكرر; 3 deleted flagged) is the official HRSD PDF core text, verified against rendered-page OCR and against the law track via the PDF's own verbatim law quotes (all >= 0.95). Both carry LLM-ready enrichment layers. The 234 English labor records are reference/guidance only. Arabic governs; not legal advice.",
            "note": "Closure audit total (169) equals total_implementing_regulations_records and is NOT added separately to avoid double-counting. Chinese remediation articles (281) are internal reference records. PDPL Arabic (43+38=81), Investment Arabic (16+37=53), Civil Arabic (721), and Labor Arabic (249+45+72+3+20+72+8+102=571) Evidence Arabic (129+24+135+34=322), and Personal Status Arabic (252+41=293) are primary Arabic governing-language records. The annex-5 records embed the official bilingual form's printed English column as a non-governing text_en_reference field (not counted as separate reference records). The unified retrieval index (2578) is a projection of counted records and is NOT added to totals.",
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
        ],
    }

    _dump_json(registry, OUTPUT_PATH)
    print(f"[OK] Corpus registry written: {OUTPUT_PATH}")
    print(f"     {registry['total_tracks']} tracks, {registry['total_registry_counted_records']} registry-counted records")
    print(f"     Primary Arabic: {registry['total_primary_arabic_governing_records']}, Reference: {registry['total_reference_records']}, Internal ref: {registry['total_internal_reference_records']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())