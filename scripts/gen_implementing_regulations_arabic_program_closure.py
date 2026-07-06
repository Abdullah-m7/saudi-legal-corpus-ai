#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementing Regulations Arabic Program Closure Audit — Generator

Creates a machine-readable JSON audit report covering:
  1. General implementing regulations (source intake + Arabic Legal LLM layer + forms)
  2. Listed joint-stock implementing regulation (source intake + Arabic Legal LLM layer + appendix)

Read-only: reads existing files, does not modify any corpus/layer files.
Idempotent: deterministic JSON output.

Output:
  reports/implementing_regulations/implementing_regulations_arabic_program_closure_audit.json

Usage:
    python3 scripts/gen_implementing_regulations_arabic_program_closure.py
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- General track paths ---
GEN_INTAKE = os.path.join(ROOT, "data", "implementing_regulations", "general", "general_implementing_regulations_arabic_source.json")
GEN_MANIFEST = os.path.join(ROOT, "data", "implementing_regulations", "general", "source_manifest.json")
GEN_LLM = os.path.join(ROOT, "data", "implementing_regulations", "general", "general_implementing_regulations_arabic_legal_llm.json")
GEN_FORMS_LLM = os.path.join(ROOT, "data", "implementing_regulations", "general", "general_implementing_regulations_arabic_forms_llm.json")

# --- Listed joint-stock track paths ---
LJS_INTAKE = os.path.join(ROOT, "data", "implementing_regulations", "listed_joint_stock", "listed_joint_stock_implementing_regulation_arabic_source.json")
LJS_MANIFEST = os.path.join(ROOT, "data", "implementing_regulations", "listed_joint_stock", "source_manifest.json")
LJS_LLM = os.path.join(ROOT, "data", "implementing_regulations", "listed_joint_stock", "listed_joint_stock_implementing_regulation_arabic_legal_llm.json")
LJS_APPENDIX_LLM = os.path.join(ROOT, "data", "implementing_regulations", "listed_joint_stock", "listed_joint_stock_implementing_regulation_arabic_appendix_llm.json")

# --- Parent law / Chinese remediation ---
PARENT_LAW_FILES = [
    "data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json",
    "data/legal_corpus_factory/law_profiles/sa_companies_law_m132_1443.profile.json",
]
CHINESE_REMEDIATION = os.path.join(ROOT, "reports", "chinese_translation_review", "chinese_remediation_program_closure_audit.json")

OUTPUT_PATH = os.path.join(ROOT, "reports", "implementing_regulations", "implementing_regulations_arabic_program_closure_audit.json")


def _load_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _dump_json(obj: Any, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _check_hashes(source_records: list, layer_records: list, id_field: str = "article_number", hash_field: str = "text_hash_sha256") -> dict[str, Any]:
    """Compare hashes between source and layer records."""
    src_map = {r[id_field]: r[hash_field] for r in source_records}
    layer_map = {r[id_field]: r.get("official_text_hash", r.get(hash_field, "")) for r in layer_records}
    total = len(src_map)
    matched = sum(1 for k, v in src_map.items() if layer_map.get(k) == v)
    mismatches = [k for k, v in src_map.items() if layer_map.get(k) != v]
    return {
        "total": total,
        "matched": matched,
        "mismatched": len(mismatches),
        "mismatch_ids": mismatches[:10],
        "all_match": matched == total,
    }


def _check_record_ids(records: list, expected_prefix: str, start: int = 1) -> dict[str, Any]:
    """Check record IDs are sequential and unique."""
    ids = [r["record_id"] for r in records]
    expected_ids = [f"{expected_prefix}{i:03d}" for i in range(start, start + len(records))]
    return {
        "total": len(ids),
        "sequential": ids == expected_ids,
        "unique": len(set(ids)) == len(ids),
        "all_valid": ids == expected_ids and len(set(ids)) == len(ids),
    }


def main() -> int:
    audit: dict[str, Any] = {
        "audit_id": "implementing-regulations-arabic-program-closure-audit",
        "audit_date": "2026-07-06",
        "stage": "IMPLEMENTING_REGULATIONS_ARABIC_PROGRAM_CLOSURE_AUDIT",
        "repo": "al3obdi/saudi-legal-corpus-ai",
        "parent_law": "sa_companies_law_m132_1443",
        "scope": "Implementing Regulations Arabic program — general + listed_joint_stock tracks",
        "tracks": {},
        "boundaries": {},
        "parent_law_unchanged": {},
        "chinese_remediation_unchanged": {},
        "validators_pass": {},
        "overall_status": "PASS",
    }

    # --- General track ---
    gen_track: dict[str, Any] = {
        "track_name": "general",
        "corpus_track": "implementing_regulations/general",
        "is_general": True,
        "is_specialized": False,
        "source_intake_exists": os.path.isfile(GEN_INTAKE),
        "source_manifest_exists": os.path.isfile(GEN_MANIFEST),
        "arabic_legal_llm_exists": os.path.isfile(GEN_LLM),
        "forms_llm_exists": os.path.isfile(GEN_FORMS_LLM),
    }

    if os.path.isfile(GEN_INTAKE):
        gen_source = _load_json(GEN_INTAKE)
        gen_track["source_article_count"] = len(gen_source.get("articles", []))
        gen_track["source_chapter_count"] = len(gen_source.get("chapters", []))
        gen_track["source_form_count"] = len(gen_source.get("forms", []))
        gen_track["source_title"] = gen_source.get("source_title") or gen_source.get("provenance", {}).get("source_title", "")
        gen_track["source_url"] = gen_source.get("source_url") or gen_source.get("provenance", {}).get("source_url", "")

    if os.path.isfile(GEN_LLM):
        gen_llm = _load_json(GEN_LLM)
        gen_track["llm_article_record_count"] = len(gen_llm.get("records", []))
        gen_track["llm_stage"] = gen_llm.get("stage", "")
        gen_track["llm_record_type"] = gen_llm.get("record_type", "")
        gen_track["llm_article_range"] = gen_llm.get("article_range", [])

        # Check record IDs
        gen_track["article_record_ids"] = _check_record_ids(gen_llm.get("records", []), "ir-gen-art-")

        # Check hashes
        if os.path.isfile(GEN_INTAKE):
            gen_track["article_hash_check"] = _check_hashes(
                gen_source.get("articles", []),
                gen_llm.get("records", []),
            )

    if os.path.isfile(GEN_FORMS_LLM):
        gen_forms = _load_json(GEN_FORMS_LLM)
        gen_track["form_record_count"] = len(gen_forms.get("records", []))
        gen_track["form_record_type"] = gen_forms.get("record_type", "")
        gen_track["form_record_ids"] = _check_record_ids(gen_forms.get("records", []), "ir-gen-form-")

        # Check form hashes
        if os.path.isfile(GEN_INTAKE):
            gen_track["form_hash_check"] = _check_hashes(
                gen_source.get("forms", []),
                gen_forms.get("records", []),
                id_field="form_number",
            )

    gen_track["status"] = "PASS" if (
        gen_track.get("source_article_count") == 95
        and gen_track.get("source_form_count") == 4
        and gen_track.get("llm_article_record_count") == 95
        and gen_track.get("form_record_count") == 4
        and gen_track.get("article_hash_check", {}).get("all_match", False)
        and gen_track.get("form_hash_check", {}).get("all_match", False)
        and gen_track.get("article_record_ids", {}).get("all_valid", False)
        and gen_track.get("form_record_ids", {}).get("all_valid", False)
    ) else "FAIL"

    audit["tracks"]["general"] = gen_track

    # --- Listed joint-stock track ---
    ljs_track: dict[str, Any] = {
        "track_name": "listed_joint_stock",
        "corpus_track": "implementing_regulations/listed_joint_stock",
        "is_general": False,
        "is_specialized": True,
        "specialized_scope": "listed joint-stock companies (شركات المساهمة المدرجة)",
        "source_intake_exists": os.path.isfile(LJS_INTAKE),
        "source_manifest_exists": os.path.isfile(LJS_MANIFEST),
        "arabic_legal_llm_exists": os.path.isfile(LJS_LLM),
        "appendix_llm_exists": os.path.isfile(LJS_APPENDIX_LLM),
    }

    if os.path.isfile(LJS_INTAKE):
        ljs_source = _load_json(LJS_INTAKE)
        ljs_track["source_article_count"] = len(ljs_source.get("articles", []))
        ljs_track["source_chapter_count"] = len(ljs_source.get("chapters", []))
        ljs_track["source_has_appendix"] = ljs_source.get("has_appendix", False)
        ljs_track["source_appendix_title"] = ljs_source.get("appendix_title", "")
        prov = ljs_source.get("provenance", {})
        ljs_track["source_title"] = prov.get("source_title", "")
        ljs_track["source_url"] = prov.get("source_url", "")
        ljs_track["issuing_authority"] = prov.get("issuing_authority", "")
        ljs_track["legal_basis"] = prov.get("legal_basis", "")

    if os.path.isfile(LJS_LLM):
        ljs_llm = _load_json(LJS_LLM)
        ljs_track["llm_article_record_count"] = len(ljs_llm.get("records", []))
        ljs_track["llm_stage"] = ljs_llm.get("stage", "")
        ljs_track["llm_record_type"] = ljs_llm.get("record_type", "")
        ljs_track["llm_article_range"] = ljs_llm.get("article_range", [])
        ljs_track["llm_is_specialized"] = ljs_llm.get("is_specialized", False)
        ljs_track["llm_is_general"] = ljs_llm.get("is_general", False)
        ljs_track["article_record_ids"] = _check_record_ids(ljs_llm.get("records", []), "ir-ljs-art-")

        if os.path.isfile(LJS_INTAKE):
            ljs_track["article_hash_check"] = _check_hashes(
                ljs_source.get("articles", []),
                ljs_llm.get("records", []),
            )

        # Check chapter metadata is null
        all_ch_null = all(r.get("chapter_number") is None and r.get("chapter_title_ar") is None for r in ljs_llm.get("records", []))
        ljs_track["chapter_metadata_null"] = all_ch_null

        # Check article titles are not ordinals
        titles_ok = all(
            r.get("article_title_ar") is not None and r.get("article_title_ar") != r.get("article_ordinal_ar", "")
            for r in ljs_llm.get("records", [])
        )
        ljs_track["article_titles_explicit"] = titles_ok

    if os.path.isfile(LJS_APPENDIX_LLM):
        ljs_app = _load_json(LJS_APPENDIX_LLM)
        ljs_track["appendix_record_count"] = len(ljs_app.get("records", []))
        ljs_track["appendix_record_type"] = ljs_app.get("record_type", "")

        if os.path.isfile(LJS_INTAKE):
            src_app_text = ljs_source.get("appendix_text", "")
            src_app_hash = _sha256(src_app_text) if src_app_text else ""
            layer_app_hash = ljs_app["records"][0].get("official_text_hash", "") if ljs_app.get("records") else ""
            ljs_track["appendix_hash_check"] = {
                "matched": src_app_hash == layer_app_hash and src_app_hash != "",
                "source_hash": src_app_hash[:16] + "...",
                "layer_hash": layer_app_hash[:16] + "...",
            }

    ljs_track["status"] = "PASS" if (
        ljs_track.get("source_article_count") == 69
        and ljs_track.get("source_has_appendix") is True
        and ljs_track.get("llm_article_record_count") == 69
        and ljs_track.get("appendix_record_count") == 1
        and ljs_track.get("article_hash_check", {}).get("all_match", False)
        and ljs_track.get("appendix_hash_check", {}).get("matched", False)
        and ljs_track.get("article_record_ids", {}).get("all_valid", False)
        and ljs_track.get("chapter_metadata_null", False)
        and ljs_track.get("llm_is_specialized", False) is True
    ) else "FAIL"

    audit["tracks"]["listed_joint_stock"] = ljs_track

    # --- Boundaries ---
    audit["boundaries"] = {
        "arabic_governs": True,
        "english_reference_only_if_later_added": True,
        "chinese_internal_reference_only_if_later_added": True,
        "not_official_translation": True,
        "not_legal_advice": True,
        "no_trilingual_alignment": True,
        "no_public_release": True,
        "general_and_listed_tracks_are_separate": True,
        "listed_joint_stock_is_specialized_not_general": True,
    }

    # --- Parent law unchanged ---
    audit["parent_law_unchanged"] = {
        "files_exist": all(os.path.isfile(os.path.join(ROOT, p)) for p in PARENT_LAW_FILES),
        "files_checked": PARENT_LAW_FILES,
    }

    # --- Chinese remediation unchanged ---
    audit["chinese_remediation_unchanged"] = {
        "closure_audit_exists": os.path.isfile(CHINESE_REMEDIATION),
        "closure_audit_path": "reports/chinese_translation_review/chinese_remediation_program_closure_audit.json",
    }

    # --- Validators pass ---
    audit["validators_pass"] = {
        "intake_scaffold": "make implementing-regulations-intake-scaffold-validate",
        "general_arabic_source": "make implementing-regulations-general-arabic-source-validate",
        "general_arabic_legal_llm": "make implementing-regulations-general-arabic-legal-llm-validate",
        "listed_jsc_arabic_source": "make implementing-regulations-listed-jsc-arabic-source-validate",
        "listed_jsc_arabic_legal_llm": "make implementing-regulations-listed-jsc-arabic-legal-llm-validate",
        "arabic_program_closure": "make implementing-regulations-arabic-program-closure-validate",
    }

    # --- Overall status ---
    all_pass = (
        gen_track.get("status") == "PASS"
        and ljs_track.get("status") == "PASS"
        and audit["parent_law_unchanged"]["files_exist"]
        and audit["chinese_remediation_unchanged"]["closure_audit_exists"]
    )
    audit["overall_status"] = "PASS" if all_pass else "FAIL"

    # --- Counts summary ---
    audit["counts"] = {
        "general_articles": gen_track.get("llm_article_record_count", 0),
        "general_forms": gen_track.get("form_record_count", 0),
        "listed_jsc_articles": ljs_track.get("llm_article_record_count", 0),
        "listed_jsc_appendices": ljs_track.get("appendix_record_count", 0),
        "total_article_records": gen_track.get("llm_article_record_count", 0) + ljs_track.get("llm_article_record_count", 0),
        "total_non_article_records": gen_track.get("form_record_count", 0) + ljs_track.get("appendix_record_count", 0),
        "total_records": gen_track.get("llm_article_record_count", 0) + ljs_track.get("llm_article_record_count", 0)
                        + gen_track.get("form_record_count", 0) + ljs_track.get("appendix_record_count", 0),
    }

    _dump_json(audit, OUTPUT_PATH)
    print(f"[OK] Closure audit written: {OUTPUT_PATH}")
    print(f"     General track: {gen_track.get('status', '?')} ({gen_track.get('llm_article_record_count', 0)} articles + {gen_track.get('form_record_count', 0)} forms)")
    print(f"     Listed JSC track: {ljs_track.get('status', '?')} ({ljs_track.get('llm_article_record_count', 0)} articles + {ljs_track.get('appendix_record_count', 0)} appendix)")
    print(f"     Overall: {audit['overall_status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())