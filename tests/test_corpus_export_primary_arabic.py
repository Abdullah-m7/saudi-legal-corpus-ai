#!/usr/bin/env python3
"""Tests for Corpus Export — Primary Arabic Governing Records (v1)."""

import json
import os
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT_DIR = os.path.join(REPO_ROOT, "data", "exports", "v1")
JSONL_PATH = os.path.join(EXPORT_DIR, "primary_arabic_governing_records.jsonl")
MANIFEST_PATH = os.path.join(EXPORT_DIR, "export_manifest.json")


@pytest.fixture(scope="module")
def records():
    """Load all JSONL records."""
    recs = []
    with open(JSONL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    return recs


@pytest.fixture(scope="module")
def manifest():
    """Load export manifest."""
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# --- File existence ---

def test_jsonl_exists():
    assert os.path.isfile(JSONL_PATH), f"JSONL not found: {JSONL_PATH}"


def test_manifest_exists():
    assert os.path.isfile(MANIFEST_PATH), f"Manifest not found: {MANIFEST_PATH}"


# --- Total count ---

def test_total_records_450(records):
    assert len(records) == 450


# --- Track-level counts ---

def test_companies_law_articles_281(records):
    cl = [r for r in records if r["source_track_id"] == "companies_law" and r["record_type"] == "article"]
    assert len(cl) == 281


def test_general_ir_articles_95(records):
    gen = [r for r in records if r["source_track_id"] == "implementing_regulations_general" and r["record_type"] == "article"]
    assert len(gen) == 95


def test_general_ir_forms_4(records):
    forms = [r for r in records if r["source_track_id"] == "implementing_regulations_general" and r["record_type"] == "form"]
    assert len(forms) == 4


def test_listed_jsc_articles_69(records):
    ljs = [r for r in records if r["source_track_id"] == "implementing_regulations_listed_joint_stock" and r["record_type"] == "article"]
    assert len(ljs) == 69


def test_listed_jsc_appendix_1(records):
    app = [r for r in records if r["source_track_id"] == "implementing_regulations_listed_joint_stock" and r["record_type"] == "appendix"]
    assert len(app) == 1


# --- Uniqueness ---

def test_export_record_ids_unique(records):
    ids = [r["export_record_id"] for r in records]
    assert len(ids) == len(set(ids))


def test_source_record_ids_present(records):
    for r in records:
        assert r.get("source_record_id"), f"Missing source_record_id in {r.get('export_record_id')}"


# --- Language ---

def test_all_arabic(records):
    for r in records:
        assert r["language"] == "ar"


def test_no_english(records):
    for r in records:
        assert r["language"] != "en"


def test_no_chinese(records):
    for r in records:
        assert r["language"] != "zh"


# --- Record type ---

def test_record_types_valid(records):
    valid = {"article", "form", "appendix"}
    for r in records:
        assert r["record_type"] in valid, f"Invalid record_type: {r['record_type']}"


# --- Text ---

def test_text_ar_non_empty(records):
    for r in records:
        assert r.get("text_ar") and str(r["text_ar"]).strip(), f"Empty text_ar in {r['export_record_id']}"


# --- Legal boundaries ---

def test_arabic_governs(records):
    for r in records:
        lb = r.get("legal_boundaries", {})
        assert lb.get("arabic_official_source_governs") is True


def test_not_official_translation(records):
    for r in records:
        lb = r.get("legal_boundaries", {})
        assert lb.get("not_official_translation") is True


def test_not_legal_advice(records):
    for r in records:
        lb = r.get("legal_boundaries", {})
        assert lb.get("not_legal_advice") is True


def test_no_public_release(records):
    for r in records:
        lb = r.get("legal_boundaries", {})
        assert lb.get("no_public_release") is True


def test_no_trilingual(records):
    for r in records:
        lb = r.get("legal_boundaries", {})
        assert lb.get("no_trilingual_alignment") is True


# --- Governing status ---

def test_governing_status(records):
    for r in records:
        assert r["governing_status"] == "arabic_governing_text"


# --- Source paths exist ---

def test_source_data_paths_exist(records):
    for r in records:
        path = r.get("source_data_path")
        if path:
            full = os.path.join(REPO_ROOT, path)
            assert os.path.isfile(full), f"Source path not found: {path}"


# --- Manifest ---

def test_manifest_total_matches(manifest, records):
    assert manifest["counts"]["total_exported_records"] == len(records)


def test_manifest_counts(manifest):
    c = manifest["counts"]
    assert c["companies_law_articles"] == 281
    assert c["general_ir_articles"] == 95
    assert c["general_ir_forms"] == 4
    assert c["listed_jsc_articles"] == 69
    assert c["listed_jsc_appendices"] == 1
    assert c["total_exported_records"] == 450


def test_manifest_count_policy(manifest):
    cp = manifest["count_policy"]
    assert cp["counting_method"] == "raw_layer_records_not_deduplicated_legal_article_units"
    assert cp["primary_arabic_governing_records_included"] is True
    assert cp["english_reference_records_excluded"] is True
    assert cp["chinese_internal_reference_records_excluded"] is True
    assert cp["closure_audit_aggregate_excluded"] is True


def test_manifest_legal_boundaries(manifest):
    lb = manifest["legal_boundaries"]
    assert lb["arabic_official_source_governs"] is True
    assert lb["not_official_translation"] is True
    assert lb["not_legal_advice"] is True
    assert lb["no_public_release"] is True


def test_manifest_export_version(manifest):
    assert manifest["export_version"] == "v1"


def test_manifest_included_tracks(manifest):
    tracks = manifest["included_tracks"]
    assert "companies_law" in tracks
    assert "implementing_regulations_general" in tracks
    assert "implementing_regulations_listed_joint_stock" in tracks


def test_manifest_excluded_record_types(manifest):
    excluded = manifest["excluded_record_types"]
    assert "english_reference_records" in excluded
    assert "chinese_internal_reference_records" in excluded
    assert "closure_audit_aggregate_records" in excluded


def test_manifest_source_paths_exist(manifest):
    for p in manifest["export_files"]:
        full = os.path.join(REPO_ROOT, p)
        assert os.path.isfile(full), f"Export file not found: {p}"


def test_manifest_source_registry_exists(manifest):
    path = manifest.get("source_registry_path")
    if path:
        full = os.path.join(REPO_ROOT, path)
        assert os.path.isfile(full), f"Registry not found: {path}"


# --- Track separation ---

def test_general_and_listed_separate(records):
    gen = [r for r in records if r["source_track_id"] == "implementing_regulations_general"]
    ljs = [r for r in records if r["source_track_id"] == "implementing_regulations_listed_joint_stock"]
    gen_ids = set(r["export_record_id"] for r in gen)
    ljs_ids = set(r["export_record_id"] for r in ljs)
    assert gen_ids.isdisjoint(ljs_ids), "General and LJS export IDs overlap"


# --- Corpus family ---

def test_corpus_family_valid(records):
    valid = {"companies_law", "implementing_regulations"}
    for r in records:
        assert r["corpus_family"] in valid


# --- Document type ---

def test_document_type_valid(records):
    valid = {"statutory_law", "implementing_regulation"}
    for r in records:
        assert r["document_type"] in valid


# --- Text hash present ---

def test_source_text_sha256_present(records):
    for r in records:
        assert r.get("source_text_sha256"), f"Missing source_text_sha256 in {r['export_record_id']}"