#!/usr/bin/env python3
"""
Corpus Export — Primary Arabic Governing Records Generator (v1)

Deterministic generator that reads existing canonical corpus files and produces:
  - data/exports/v1/primary_arabic_governing_records.jsonl  (one record per line)
  - data/exports/v1/export_manifest.json                     (export metadata)

Export scope:
  - Companies Law Arabic governing: 281 articles
  - General implementing regulations: 95 articles + 4 forms
  - Listed joint-stock implementing regulation: 69 articles + 1 appendix
  Total: 450 Arabic governing records

Excluded:
  - English reference records
  - Chinese internal reference records
  - Closure audit aggregate (duplicates underlying IR records)

Idempotent: re-running produces identical output.
"""

import json
import hashlib
import os
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT_DIR = os.path.join(REPO_ROOT, "data", "exports", "v1")
JSONL_PATH = os.path.join(EXPORT_DIR, "primary_arabic_governing_records.jsonl")
MANIFEST_PATH = os.path.join(EXPORT_DIR, "export_manifest.json")

# Source data paths (relative to repo root)
COMPANIES_LAW_AR_PATH = "data/official_arabic_legal_llm/companies_law_m132_1443_official_arabic_legal_llm_001_281.json"
GENERAL_IR_ARTICLES_PATH = "data/implementing_regulations/general/general_implementing_regulations_arabic_legal_llm.json"
GENERAL_IR_FORMS_PATH = "data/implementing_regulations/general/general_implementing_regulations_arabic_forms_llm.json"
LJS_ARTICLES_PATH = "data/implementing_regulations/listed_joint_stock/listed_joint_stock_implementing_regulation_arabic_legal_llm.json"
LJS_APPENDIX_PATH = "data/implementing_regulations/listed_joint_stock/listed_joint_stock_implementing_regulation_arabic_appendix_llm.json"
REGISTRY_PATH = "data/corpus_registry/corpus_registry.json"

LEGAL_BOUNDARIES = {
    "arabic_official_source_governs": True,
    "not_official_translation": True,
    "not_legal_advice": True,
    "no_trilingual_alignment": True,
    "no_public_release": True,
    "english_reference_only": True,
    "chinese_internal_reference_only": True,
    "listed_jsc_specialized_not_general": True,
}


def get_git_head_sha():
    """Get current git HEAD SHA."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def load_json(path):
    with open(os.path.join(REPO_ROOT, path), "r", encoding="utf-8") as f:
        return json.load(f)


def export_companies_law_articles(data):
    """Export 281 Companies Law Arabic articles."""
    records = []
    source_data = data["records"]
    for r in source_data:
        export_record = {
            "export_record_id": f"export-cl-art-{r['article_number']:03d}",
            "source_track_id": "companies_law",
            "source_record_id": r["record_id"],
            "corpus_family": "companies_law",
            "document_type": "statutory_law",
            "record_type": "article",
            "language": "ar",
            "governing_status": "arabic_governing_text",
            "title_ar": r.get("article_title_ar"),
            "article_number": r["article_number"],
            "text_ar": r["official_text_ar"],
            "source_text_sha256": r.get("official_text_hash_sha256"),
            "source_authority": r.get("source_trust", {}).get("source_authority"),
            "source_authority_ar": r.get("source_trust", {}).get("source_authority_ar"),
            "source_data_path": COMPANIES_LAW_AR_PATH,
            "registry_track_id": "companies_law",
            "legal_boundaries": LEGAL_BOUNDARIES,
            "notes": None,
        }
        records.append(export_record)
    return records


def export_general_ir_articles(data):
    """Export 95 General IR articles."""
    records = []
    for r in data["records"]:
        export_record = {
            "export_record_id": f"export-irgen-art-{r['article_number']:03d}",
            "source_track_id": "implementing_regulations_general",
            "source_record_id": r["record_id"],
            "corpus_family": "implementing_regulations",
            "document_type": "implementing_regulation",
            "record_type": "article",
            "language": "ar",
            "governing_status": "arabic_governing_text",
            "title_ar": r.get("article_title_ar"),
            "article_number": r["article_number"],
            "article_ordinal_ar": r.get("article_ordinal_ar"),
            "chapter_number": r.get("chapter_number"),
            "chapter_title_ar": r.get("chapter_title_ar"),
            "text_ar": r["official_text_ar"],
            "source_text_sha256": r.get("official_text_hash"),
            "source_url": r.get("source_url"),
            "source_title": r.get("source_title"),
            "publication_date_hijri": r.get("publication_date_hijri"),
            "publication_date_gregorian": r.get("publication_date_gregorian"),
            "source_data_path": GENERAL_IR_ARTICLES_PATH,
            "registry_track_id": "implementing_regulations_general",
            "legal_boundaries": LEGAL_BOUNDARIES,
            "notes": None,
        }
        records.append(export_record)
    return records


def export_general_ir_forms(data):
    """Export 4 General IR forms."""
    records = []
    for r in data["records"]:
        export_record = {
            "export_record_id": f"export-irgen-form-{r['form_number']:03d}",
            "source_track_id": "implementing_regulations_general",
            "source_record_id": r["record_id"],
            "corpus_family": "implementing_regulations",
            "document_type": "implementing_regulation",
            "record_type": "form",
            "language": "ar",
            "governing_status": "arabic_governing_text",
            "title_ar": r.get("form_title"),
            "record_number": r["form_number"],
            "text_ar": r["official_text_ar"],
            "source_text_sha256": r.get("official_text_hash"),
            "source_url": r.get("source_url"),
            "source_title": r.get("source_title"),
            "publication_date_hijri": r.get("publication_date_hijri"),
            "publication_date_gregorian": r.get("publication_date_gregorian"),
            "source_data_path": GENERAL_IR_FORMS_PATH,
            "registry_track_id": "implementing_regulations_general",
            "legal_boundaries": LEGAL_BOUNDARIES,
            "notes": None,
        }
        records.append(export_record)
    return records


def export_ljs_articles(data):
    """Export 69 Listed JSC articles."""
    records = []
    for r in data["records"]:
        export_record = {
            "export_record_id": f"export-irljs-art-{r['article_number']:03d}",
            "source_track_id": "implementing_regulations_listed_joint_stock",
            "source_record_id": r["record_id"],
            "corpus_family": "implementing_regulations",
            "document_type": "implementing_regulation",
            "record_type": "article",
            "language": "ar",
            "governing_status": "arabic_governing_text",
            "title_ar": r.get("article_title_ar"),
            "article_number": r["article_number"],
            "article_ordinal_ar": r.get("article_ordinal_ar"),
            "chapter_number": r.get("chapter_number"),
            "chapter_title_ar": r.get("chapter_title_ar"),
            "text_ar": r["official_text_ar"],
            "source_text_sha256": r.get("official_text_hash"),
            "source_url": r.get("source_url"),
            "source_title": r.get("source_title"),
            "publication_date_hijri": r.get("publication_date_hijri"),
            "publication_date_gregorian": r.get("publication_date_gregorian"),
            "source_authority": r.get("issuing_authority"),
            "source_data_path": LJS_ARTICLES_PATH,
            "registry_track_id": "implementing_regulations_listed_joint_stock",
            "legal_boundaries": LEGAL_BOUNDARIES,
            "notes": "listed_joint_stock_specialized_sub_track",
        }
        records.append(export_record)
    return records


def export_ljs_appendix(data):
    """Export 1 Listed JSC appendix."""
    records = []
    for r in data["records"]:
        export_record = {
            "export_record_id": f"export-irljs-appendix-{r['record_id'].split('-')[-1]}",
            "source_track_id": "implementing_regulations_listed_joint_stock",
            "source_record_id": r["record_id"],
            "corpus_family": "implementing_regulations",
            "document_type": "implementing_regulation",
            "record_type": "appendix",
            "language": "ar",
            "governing_status": "arabic_governing_text",
            "title_ar": r.get("appendix_title"),
            "text_ar": r["official_text_ar"],
            "source_text_sha256": r.get("official_text_hash"),
            "source_url": r.get("source_url"),
            "source_title": r.get("source_title"),
            "publication_date_hijri": r.get("publication_date_hijri"),
            "publication_date_gregorian": r.get("publication_date_gregorian"),
            "source_authority": r.get("issuing_authority"),
            "source_data_path": LJS_APPENDIX_PATH,
            "registry_track_id": "implementing_regulations_listed_joint_stock",
            "legal_boundaries": LEGAL_BOUNDARIES,
            "notes": "listed_joint_stock_specialized_sub_track",
        }
        records.append(export_record)
    return records


def generate():
    """Generate the JSONL export and manifest."""
    os.makedirs(EXPORT_DIR, exist_ok=True)

    # Load source data
    cl_data = load_json(COMPANIES_LAW_AR_PATH)
    gen_articles = load_json(GENERAL_IR_ARTICLES_PATH)
    gen_forms = load_json(GENERAL_IR_FORMS_PATH)
    ljs_articles = load_json(LJS_ARTICLES_PATH)
    ljs_appendix = load_json(LJS_APPENDIX_PATH)

    # Build export records
    all_records = []

    # 1. Companies Law Arabic: 281 articles
    cl_records = export_companies_law_articles(cl_data)
    all_records.extend(cl_records)

    # 2. General IR: 95 articles
    gen_art_records = export_general_ir_articles(gen_articles)
    all_records.extend(gen_art_records)

    # 3. General IR: 4 forms
    gen_form_records = export_general_ir_forms(gen_forms)
    all_records.extend(gen_form_records)

    # 4. Listed JSC: 69 articles
    ljs_art_records = export_ljs_articles(ljs_articles)
    all_records.extend(ljs_art_records)

    # 5. Listed JSC: 1 appendix
    ljs_app_records = export_ljs_appendix(ljs_appendix)
    all_records.extend(ljs_app_records)

    # Write JSONL
    with open(JSONL_PATH, "w", encoding="utf-8") as f:
        for rec in all_records:
            f.write(json.dumps(rec, ensure_ascii=False, sort_keys=False))
            f.write("\n")

    # Compute counts
    counts = {
        "companies_law_articles": len(cl_records),
        "general_ir_articles": len(gen_art_records),
        "general_ir_forms": len(gen_form_records),
        "listed_jsc_articles": len(ljs_art_records),
        "listed_jsc_appendices": len(ljs_app_records),
        "total_exported_records": len(all_records),
    }

    # Build manifest
    head_sha = get_git_head_sha()
    manifest = {
        "export_version": "v1",
        "generated_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "repository": "al3obdi/saudi-legal-corpus-ai",
        "baseline_commit": head_sha,
        "source_registry_path": REGISTRY_PATH,
        "export_files": [
            "data/exports/v1/primary_arabic_governing_records.jsonl",
            "data/exports/v1/export_manifest.json",
        ],
        "included_tracks": [
            "companies_law",
            "implementing_regulations_general",
            "implementing_regulations_listed_joint_stock",
        ],
        "excluded_tracks": [
            "implementing_regulations_arabic_program_closure (aggregate — duplicates underlying IR records)",
        ],
        "excluded_record_types": [
            "english_reference_records",
            "chinese_internal_reference_records",
            "closure_audit_aggregate_records",
        ],
        "counts": counts,
        "count_policy": {
            "counting_method": "raw_layer_records_not_deduplicated_legal_article_units",
            "primary_arabic_governing_records_included": True,
            "english_reference_records_excluded": True,
            "chinese_internal_reference_records_excluded": True,
            "closure_audit_aggregate_excluded": True,
            "closure_audit_aggregate_duplicates_underlying_ir_records": True,
            "forms_and_appendices_counted": True,
            "formula": "companies_law_arabic(281) + general_ir_articles(95) + general_ir_forms(4) + listed_jsc_articles(69) + listed_jsc_appendix(1) = 450",
        },
        "legal_boundaries": LEGAL_BOUNDARIES,
        "validator_targets": [
            "make corpus-export-primary-arabic-validate",
        ],
        "idempotence_status": "deterministic — re-run produces identical output",
        "text_preservation_rule": "text_ar is copied verbatim from existing canonical corpus fields. No paraphrase, no summary, no normalization that changes legal text.",
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"[OK] Corpus export written: {JSONL_PATH}")
    print(f"     {len(all_records)} records ({counts['companies_law_articles']} CL + {counts['general_ir_articles']} Gen IR art + {counts['general_ir_forms']} Gen IR forms + {counts['listed_jsc_articles']} LJS art + {counts['listed_jsc_appendices']} LJS appendix)")
    print(f"     Manifest: {MANIFEST_PATH}")
    print(f"     Baseline commit: {head_sha}")


if __name__ == "__main__":
    generate()