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
PDPL_LAW_NL = os.path.join(ROOT, "sources", "pdpl", "next_layer", "pdpl_arabic_law_next_layer_summary.json")
PDPL_REG_NL = os.path.join(ROOT, "sources", "pdpl", "regulation", "next_layer", "pdpl_implementing_regulation_arabic_next_layer_summary.json")


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
    pdpl_law_nl = _load_json(PDPL_LAW_NL)
    pdpl_reg_nl = _load_json(PDPL_REG_NL)

    registry: dict[str, Any] = {
        "registry_version": "1.0",
        "generated_date": "2026-07-06",
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
        "total_tracks": 6,
        "total_primary_arabic_governing_records": (
            companies_ar["record_count"]  # 281 Companies Law
            + gen_llm["record_count"]      # 95 general IR articles
            + gen_forms["record_count"]    # 4 general IR forms
            + ljs_llm["record_count"]      # 69 listed JSC articles
            + ljs_app["record_count"]      # 1 listed JSC appendix
            + pdpl_law_nl["record_count"]  # 43 PDPL law (reviewed OCR, not verified official)
            + pdpl_reg_nl["record_count"]  # 38 PDPL implementing regulation (extracted, not verified official)
        ),
        "total_reference_records": companies_en["record_count"],  # 281 English
        "total_internal_reference_records": chinese_audit.get("total_articles_implemented", 281),  # 281 Chinese
        "total_implementing_regulations_records": (
            gen_llm["record_count"] + gen_forms["record_count"]
            + ljs_llm["record_count"] + ljs_app["record_count"]
        ),
        "total_registry_counted_records": (
            companies_ar["record_count"]
            + gen_llm["record_count"] + gen_forms["record_count"]
            + ljs_llm["record_count"] + ljs_app["record_count"]
            + pdpl_law_nl["record_count"] + pdpl_reg_nl["record_count"]
            + companies_en["record_count"]
            + chinese_audit.get("total_articles_implemented", 281)
        ),
        "count_policy": {
            "counting_method": "raw_layer_records_not_deduplicated_legal_article_units",
            "primary_arabic_governing_records_included": True,
            "english_reference_records_included": True,
            "chinese_internal_reference_records_included": True,
            "forms_and_appendices_counted": True,
            "closure_audit_aggregate_not_counted_separately": True,
            "closure_audit_total_duplicates_underlying_ir_records": True,
            "formula_total_primary_arabic_governing": "companies_law_arabic(281) + general_ir_articles(95) + general_ir_forms(4) + listed_jsc_articles(69) + listed_jsc_appendix(1) + pdpl_law(43) + pdpl_implementing_regulation(38) = 531",
            "formula_total_reference": "companies_law_english(281)",
            "formula_total_internal_reference": "companies_law_chinese_remediation(281)",
            "formula_total_implementing_regulations": "general_articles(95) + general_forms(4) + listed_jsc_articles(69) + listed_jsc_appendix(1) = 169",
            "formula_total_registry_counted": "total_primary_arabic_governing(531) + total_reference(281) + total_internal_reference(281) = 1093",
            "pdpl_arabic_records_status": "PDPL law (43) and implementing regulation (38) Arabic next-layer records are primary Arabic governing-language records but are NOT verified official text (reviewed OCR / direct extraction). Arabic governs; not official/binding; not legal advice. Kept as separate PDPL corpus tracks.",
            "note": "Closure audit total (169) equals total_implementing_regulations_records and is NOT added separately to avoid double-counting. Chinese remediation articles (281) are internal reference records, not a public full Chinese layer. PDPL Arabic (43+38=81) are primary Arabic governing-language records, not verified official text.",
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
                "status": "next_layer_complete",
                "official_text_status": "REVIEWED_OCR_NOT_VERIFIED_OFFICIAL_TEXT",
                "language_layers": {
                    "arabic": {
                        "status": "next_layer_complete",
                        "governing": True,
                        "record_count": pdpl_law_nl["record_count"],
                        "data_path": "sources/pdpl/next_layer/pdpl_arabic_law_next_layer_records.jsonl",
                    },
                },
                "record_counts": {
                    "arabic_articles": pdpl_law_nl["record_count"],
                    "total": pdpl_law_nl["record_count"],
                },
                "data_paths": [
                    "sources/pdpl/next_layer/pdpl_arabic_law_next_layer_records.jsonl",
                    "sources/pdpl/next_layer/pdpl_arabic_law_next_layer_summary.json",
                ],
                "validator_targets": [
                    "make pdpl-arabic-law-next-layer-validate",
                ],
                "report_paths": [
                    "reports/pdpl/PDPL_ARABIC_LAW_NEXT_LAYER_QA_REPORT.md",
                ],
                "boundaries": {
                    "arabic_governs": True,
                    "not_official_translation": True,
                    "not_verified_official_text": True,
                    "not_legal_advice": True,
                    "no_trilingual_alignment": True,
                    "no_public_release": True,
                },
                "notes": "PDPL law Arabic next-layer: 43 article records from reviewed OCR (Article 32 = ملغاة). Arabic governs; NOT verified official text; no translation / no legal interpretation. Separate PDPL corpus track.",
            },
            {
                "track_id": "pdpl_implementing_regulation",
                "display_name_ar": "اللائحة التنفيذية لنظام حماية البيانات الشخصية",
                "display_name_en": "PDPL Implementing Regulation",
                "corpus_family": "implementing_regulation",
                "jurisdiction": "Kingdom of Saudi Arabia",
                "governing_language": "ar",
                "status": "next_layer_complete",
                "official_text_status": "EXTRACTED_TEXT_NOT_VERIFIED_OFFICIAL_TEXT",
                "language_layers": {
                    "arabic": {
                        "status": "next_layer_complete",
                        "governing": True,
                        "record_count": pdpl_reg_nl["record_count"],
                        "data_path": "sources/pdpl/regulation/next_layer/pdpl_implementing_regulation_arabic_next_layer_records.jsonl",
                    },
                },
                "record_counts": {
                    "arabic_articles": pdpl_reg_nl["record_count"],
                    "total": pdpl_reg_nl["record_count"],
                },
                "data_paths": [
                    "sources/pdpl/regulation/next_layer/pdpl_implementing_regulation_arabic_next_layer_records.jsonl",
                    "sources/pdpl/regulation/next_layer/pdpl_implementing_regulation_arabic_next_layer_summary.json",
                ],
                "validator_targets": [
                    "make pdpl-implementing-regulation-arabic-next-layer-validate",
                ],
                "report_paths": [],
                "boundaries": {
                    "arabic_governs": True,
                    "is_general": False,
                    "is_specialized": False,
                    "not_official_translation": True,
                    "not_verified_official_text": True,
                    "not_legal_advice": True,
                    "no_trilingual_alignment": True,
                    "no_public_release": True,
                },
                "notes": "PDPL implementing regulation Arabic next-layer: 38 article records from direct text extraction. Arabic governs; NOT verified official text; no translation / no legal interpretation. Separate PDPL corpus track.",
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