#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corpus Schema Manifest — Generator

Produces ONE authoritative, machine-readable manifest of JSON Schemas
describing every distinct document type used across this corpus, so an
external integrator (e.g. building a RAG application on top of this corpus)
does not have to reverse-engineer the data model from 123+ individual
track files and inconsistent per-track generator scripts.

This is a DESCRIPTIVE, READ-ONLY survey layer. It does not modify any of
the 123 track files, the registry, run_qa_gate.py, the Makefile, or any of
the five other corpus-wide derived layers it documents.

Unlike most other generators in this corpus, this one is NOT purely
mechanically derived from a single machine-readable source: the schemas
below were hand-curated by directly reading a representative, diverse
sample of real corpus files (see field_provenance_notes below and the
companion guide at reports/schema_manifest/SCHEMA_MANIFEST_GUIDE_EN.md for
exactly which files were read). Because a curated schema can silently
drift from the real data it claims to describe, this generator performs a
mandatory SELF-VALIDATION pass at the end of main(): it re-reads a sample
of real corpus files spanning multiple tracks and eras plus EVERY
corpus-wide derived layer, and FAILS LOUDLY (raises SystemExit) if a
field this manifest claims is "always present" (i.e. listed in a schema's
`required`) is missing from any sampled file, if a real row carries a
field no schema documents, or if a schema's own JSON Schema syntax is
structurally invalid.

AND IT NOW FAILS ON WHAT IS ABSENT, NOT ONLY ON WHAT IS WRONG. A curated
manifest describes what someone remembered to describe, and this one
called itself authoritative over "every distinct document type" while
describing seven of eleven derived layers: the chunking layer, the
freshness manifest, the caveat layer and the amendment timeline were all
built after this file and none of them ever joined it. Nothing said so,
because the manifest enumerated what it covered and never what it MISSED.
So the last check in self_validate() walks data/corpus_*/ on disk and
fails if any published JSON payload is named by no schema here — which
immediately turned up two more, the retrieval evaluation's gold queries
and its per-query results. A completeness claim that cannot fail is not a
claim.

Reads (read-only):
    sources/<track>/law/official_source/*.json      (7 tracks sampled)
    sources/<track>/law/verified/*.jsonl             (7 tracks sampled)
    data/<track>_arabic_legal_llm/*.json             (4 tracks sampled)
    data/corpus_unified_index/corpus_unified_llm_index.jsonl
    data/corpus_registry/corpus_registry.json
    data/corpus_verification_tiers/corpus_verification_tiers.json
    data/corpus_supersession_graph/corpus_supersession_graph.json
    data/corpus_cross_reference_graph/corpus_cross_reference_graph.json
    data/corpus_glossary/corpus_glossary.json
    data/corpus_chunking_layer/corpus_chunking_layer.jsonl
    data/corpus_freshness_manifest/corpus_freshness_manifest.json
    data/corpus_caveat_layer/corpus_caveat_layer.jsonl
    data/corpus_amendment_timeline/corpus_amendment_timeline.jsonl
    data/corpus_retrieval_eval/corpus_retrieval_eval_queries.json
    data/corpus_retrieval_eval/corpus_retrieval_eval_results.json

Writes:
    data/schema_manifest/corpus_schema_manifest.json

Usage:
    python3 scripts/gen_corpus_schema_manifest.py
"""

from __future__ import annotations

import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "schema_manifest")
OUT_PATH = os.path.join(OUT_DIR, "corpus_schema_manifest.json")

DIALECT = "https://json-schema.org/draft/2020-12/schema"
GENERATED_BY = "scripts/gen_corpus_schema_manifest.py"
SCHEMA_VERSION = "1.0.0"
CORPUS_REPOSITORY = "al3obdi/saudi-legal-corpus-ai"
CORPUS_BRANCH = "claude/chinese-remediation-batch-p1-002-qa-1kx2az"

# ---------------------------------------------------------------------------
# Sample files actually read to build this manifest (used again below for
# self-validation). Every field in every schema below is traceable to one
# of these real files.
# ---------------------------------------------------------------------------

OFFICIAL_SOURCE_SAMPLES_STANDARD = {
    "income_tax_law": "sources/income_tax/law/official_source/income_tax_law_official_source.json",
    "patent_law": "sources/patent/law/official_source/patent_law_official_source.json",
    "zakat_law": "sources/zakat/law/official_source/zakat_law_official_source.json",
    "traffic_law": "sources/traffic/law/official_source/traffic_law_official_source.json",
    "social_insurance_law": "sources/social_insurance/law/official_source/social_insurance_law_official_source.json",
    "basic_law_of_governance": "sources/basic_law_of_governance/law/official_source/basic_law_of_governance_official_source.json",
}
OFFICIAL_SOURCE_SAMPLES_LEGACY = {
    "civil_transactions_law": "sources/civil/law/official_source/civil_transactions_law_official_source.json",
}

VERIFIED_RECORD_SAMPLES_STANDARD = {
    "income_tax_law": "sources/income_tax/law/verified/income_tax_law_verified_records.jsonl",
    "patent_law": "sources/patent/law/verified/patent_law_verified_records.jsonl",
    "zakat_law": "sources/zakat/law/verified/zakat_law_verified_records.jsonl",
    "traffic_law": "sources/traffic/law/verified/traffic_law_verified_records.jsonl",
    "social_insurance_law": "sources/social_insurance/law/verified/social_insurance_law_verified_records.jsonl",
    "basic_law_of_governance": "sources/basic_law_of_governance/law/verified/basic_law_of_governance_verified_records.jsonl",
}
VERIFIED_RECORD_SAMPLES_LEGACY = {
    "civil_transactions_law": "sources/civil/law/verified/civil_transactions_law_verified_records.jsonl",
}

LLM_READY_SAMPLES_STANDARD = {
    "income_tax_law": "data/income_tax_arabic_legal_llm/income_tax_law_legal_llm_001_081.json",
    "patent_law": "data/patent_arabic_legal_llm/patent_law_legal_llm_001_066.json",
    "zakat_law": "data/zakat_arabic_legal_llm/zakat_law_legal_llm_001_128.json",
}
LLM_READY_SAMPLES_LEGACY = {
    "civil_transactions_law": "data/civil_arabic_legal_llm/civil_transactions_law_legal_llm_001_721.json",
}

UNIFIED_INDEX_SAMPLE = "data/corpus_unified_index/corpus_unified_llm_index.jsonl"
REGISTRY_SAMPLE = "data/corpus_registry/corpus_registry.json"
VERIFICATION_TIERS_SAMPLE = "data/corpus_verification_tiers/corpus_verification_tiers.json"
SUPERSESSION_GRAPH_SAMPLE = "data/corpus_supersession_graph/corpus_supersession_graph.json"
CROSS_REFERENCE_GRAPH_SAMPLE = "data/corpus_cross_reference_graph/corpus_cross_reference_graph.json"
GLOSSARY_SAMPLE = "data/corpus_glossary/corpus_glossary.json"
CHUNKING_LAYER_SAMPLE = "data/corpus_chunking_layer/corpus_chunking_layer.jsonl"
FRESHNESS_MANIFEST_SAMPLE = "data/corpus_freshness_manifest/corpus_freshness_manifest.json"
CAVEAT_LAYER_SAMPLE = "data/corpus_caveat_layer/corpus_caveat_layer.jsonl"
AMENDMENT_TIMELINE_SAMPLE = ("data/corpus_amendment_timeline/"
                             "corpus_amendment_timeline.jsonl")
RETRIEVAL_EVAL_QUERIES_SAMPLE = ("data/corpus_retrieval_eval/"
                                 "corpus_retrieval_eval_queries.json")
RETRIEVAL_EVAL_RESULTS_SAMPLE = ("data/corpus_retrieval_eval/"
                                 "corpus_retrieval_eval_results.json")


# ---------------------------------------------------------------------------
# Schema builders. Each returns a JSON-Schema-2020-12-compliant dict.
# ---------------------------------------------------------------------------

def _official_source_article_record_standard():
    return {
        "title": "Official source article record (standard convention)",
        "description": (
            "One entry in the top-level `articles` object of a standard-convention "
            "official_source.json (every track except civil_transactions_law, the "
            "corpus's earliest/legacy track). Keyed by an article_key such as "
            "'income_tax_art_001'."
        ),
        "type": "object",
        "required": [
            "number_label_ar", "is_mukarrar", "section_ar", "text",
            "legal_status_ar", "structure_status_ar", "section_status_ar",
            "status", "history",
        ],
        "properties": {
            "number_label_ar": {"type": "string", "minLength": 1,
                "description": "Human-readable Arabic ordinal article label, e.g. 'المادة الأولى'."},
            "is_mukarrar": {"type": "boolean",
                "description": "True if this is a 'مكرر' (repeated/inserted-between) article number."},
            "section_ar": {"type": "string",
                "description": "Arabic chapter/section heading this article falls under."},
            "text": {"type": "string", "minLength": 1,
                "description": "The current governing Arabic article text."},
            "legal_status_ar": {"type": "string",
                "enum": ["اصلية", "معدلة", "ملغاة", "مضافة"],
                "description": "Article-level legal status: original / amended / repealed / added."},
            "structure_status_ar": {"type": "string",
                "description": "Structural status tag, usually mirrors legal_status_ar."},
            "section_status_ar": {"type": "string",
                "description": "Status tag of the enclosing section, usually mirrors legal_status_ar."},
            "status": {"type": "string",
                "description": "Track-specific verification-pipeline status code for this article "
                                "(e.g. 'BOE_PORTAL_PRIMARY_SOURCE_WIPO_LEX_SPOT_CHECKED')."},
            "history": {"type": "array",
                "description": "Amendment history entries (empty array if never amended). Each entry "
                                "is a free-form object (decree, decreeDate, paragraph, text, source_note "
                                "keys observed; not all keys present on every entry).",
                "items": {"type": "object"}},
            "verification_tier": {"type": "string",
                "description": "OPTIONAL. Per-article verification-confidence tier, distinct from the "
                                "track-wide official_text_status. Pioneered by traffic_law (per-article "
                                "PRIMARY_INDEPENDENTLY_CONFIRMED vs SECONDARY_SOURCE_ONLY_BOE_KNOWN_STALE "
                                "split) and used by basic_law_of_governance (Article 5 only)."},
            "cross_verified_against_wipo_lex": {"type": "boolean",
                "description": "OPTIONAL. Whether this specific article was individually spot-checked "
                                "against WIPO Lex. Pioneered by basic_law_of_governance."},
            "verification_note": {"type": "string",
                "description": "OPTIONAL. Free-text per-article verification note. Pioneered by "
                                "basic_law_of_governance."},
            "title_ar": {"type": "string",
                "description": "OPTIONAL. A named-section title for this specific article, distinct "
                                "from section_ar. Seen on zakat_law."},
        },
        "patternProperties": {
            "^original_[0-9]{4}h_text$": {
                "type": ["string", "null"],
                "description": (
                    "OPTIONAL, name varies by track's founding Hijri year (e.g. "
                    "original_1412h_text on basic_law_of_governance, original_1425h_text on "
                    "income_tax_law/patent_law, original_1428h_text on traffic_law, "
                    "original_1445h_text on zakat_law). Preserves the pre-amendment wording of an "
                    "amended article. Present (possibly with a null value, meaning 'not recovered') "
                    "only on tracks with at least one amended article whose original wording was "
                    "sought; absent entirely on tracks with no amendments recorded this way "
                    "(e.g. social_insurance_law) and on the legacy civil_transactions_law track."
                ),
            },
        },
        "additionalProperties": True,
    }


def _official_source_article_record_legacy():
    return {
        "title": "Official source article record (legacy civil_transactions_law convention)",
        "description": (
            "civil_transactions_law is this corpus's earliest track and predates the "
            "standard official_source.json conventions above: no per-article legal_status_ar, "
            "history, or verification-pipeline status fields exist at the article level "
            "(the whole 721-article law is unamended, so this was never needed)."
        ),
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string", "minLength": 1, "description": "The Arabic article text."},
            "section_context": {"type": "string",
                "description": "OPTIONAL. Structural heading (كتاب/باب/فصل/قسم/فرع) attached to this "
                                "article, analogous to section_ar in the standard convention."},
        },
        "additionalProperties": True,
    }


def official_source_schema():
    return {
        "$schema": DIALECT,
        "$id": "https://github.com/al3obdi/saudi-legal-corpus-ai/schemas/manifest/official_source_schema.json",
        "title": "Official source document (per-track source-of-truth)",
        "description": (
            "sources/<track>/<component>/official_source/*.json — the source-of-truth document for "
            "one law/regulation track, capturing the raw article text and verification-methodology "
            "narrative BEFORE the verified/ and LLM-ready layers are derived from it. This is the "
            "LEAST standardized layer in the corpus: it is the closest to raw per-track ingestion, "
            "authored over time by many separate generator scripts, and a broad validation sweep run "
            "by this manifest's own generator (see the top-level `corpus_wide_coverage_check` key) "
            "found only a MINORITY of the corpus's 117 official_source.json files strictly match "
            "either of the two deeply-documented conventions below (STANDARD, confirmed on "
            "income_tax_law/patent_law/zakat_law/traffic_law/social_insurance_law/"
            "basic_law_of_governance; LEGACY, confirmed on civil_transactions_law only) — by contrast "
            "the downstream verified_record_schema and llm_ready_layer_schema converge much more "
            "broadly across the corpus. A permissive MINIMAL fallback branch is included below so "
            "that this schema still accepts (without deeply modeling) the many further real "
            "conventions observed in tracks NOT sampled for this manifest — e.g. aawan_regulation and "
            "documentation_settlement_regulation use `stats`/`provenance` instead of "
            "`status_counts`/`verification_methodology_note`; labor_law and several other early-ish "
            "law tracks use a civil_transactions_law-like but not identical shape "
            "(law_key/boundaries/capture_method/source_pdf_sha256); anti_bribery_law and several "
            "others omit `chapter_structure`/`preamble_ar` entirely. These further conventions were "
            "spot-checked only at the top-level-key-name level (not read in full depth article-by-"
            "article) and are intentionally NOT modeled as their own named variants here, to avoid "
            "asserting structure this pass did not verify closely — treat MINIMAL-only matches as "
            "'shape not deeply documented by this manifest', not as an error in the underlying data."
        ),
        "anyOf": [
            {"$ref": "#/$defs/OfficialSourceStandard"},
            {"$ref": "#/$defs/OfficialSourceLegacyCivil"},
            {"$ref": "#/$defs/OfficialSourceMinimal"},
        ],
        "$defs": {
            "OfficialSourceArticleRecordStandard": _official_source_article_record_standard(),
            "OfficialSourceArticleRecordLegacyCivil": _official_source_article_record_legacy(),
            "OfficialSourceMinimal": {
                "title": "Official source document (permissive fallback — shape not deeply documented)",
                "description": (
                    "Lowest-common-denominator fallback matching any official_source.json this "
                    "manifest did not deeply survey. Only the two fields confirmed present in EVERY "
                    "official_source.json examined during both the deep 7-track read and the broad "
                    "117-file structural sweep are required."
                ),
                "type": "object",
                "required": ["article_count", "articles"],
                "properties": {
                    "article_count": {"type": "integer", "minimum": 1},
                    "articles": {"type": "object"},
                },
                "additionalProperties": True,
            },
            "OfficialSourceStandard": {
                "title": "Official source document (standard convention)",
                "type": "object",
                "required": [
                    "document", "decree", "decree_date_hijri", "legal_status_ar",
                    "consolidated_amended_law", "issuing_authority_ar", "preamble_ar",
                    "verification_methodology_note", "article_count", "status_counts",
                    "chapter_structure", "articles", "known_unresolved_discrepancies",
                ],
                "properties": {
                    "document": {"type": "string", "description": "Arabic law/regulation title."},
                    "document_en": {"type": "string",
                        "description": "OPTIONAL. English law title. Absent on e.g. patent_law."},
                    "decree": {"type": "string", "description": "Issuing Royal Decree/Resolution label."},
                    "decree_date_hijri": {"type": "string", "description": "Hijri decree date, e.g. '29/5/1425'."},
                    "legal_status_ar": {"type": "string",
                        "description": "Track-wide current legal status, usually 'ساري' (in force)."},
                    "consolidated_amended_law": {"type": "boolean",
                        "description": "Whether the ingested text is a consolidated-through-amendments text."},
                    "issuing_authority_ar": {"type": "string"},
                    "issuing_authority_en": {"type": "string", "description": "OPTIONAL."},
                    "preamble_ar": {"type": "string", "description": "Full Arabic promulgation preamble."},
                    "decree_transitional_provisions_ar": {"type": "string",
                        "description": "OPTIONAL. Verbatim transitional/enactment-decree provisions text "
                                        "distinct from the law's own articles. Pioneered by, and so far "
                                        "unique to, social_insurance_law."},
                    "verification_methodology_note": {"type": "string",
                        "description": "Long-form narrative of sources used, cross-checks performed, and "
                                        "any caveats/discrepancies for this track's text."},
                    "article_count": {"type": "integer", "minimum": 1},
                    "status_counts": {"type": "object",
                        "required": ["اصلية", "معدلة", "ملغاة", "مضافة"],
                        "properties": {
                            "اصلية": {"type": "integer", "minimum": 0},
                            "معدلة": {"type": "integer", "minimum": 0},
                            "ملغاة": {"type": "integer", "minimum": 0},
                            "مضافة": {"type": "integer", "minimum": 0},
                        },
                        "description": "Track-wide counts of articles by legal_status_ar value."},
                    "chapter_structure": {"type": "array",
                        "items": {"type": "object", "additionalProperties": True},
                        "description": (
                            "Ordered list of chapters/sections (أبواب/فصول) with their article ranges. "
                            "WARNING: the item shape is NOT standardized across tracks (verified by "
                            "sampling all 6 standard-convention tracks read for this manifest) — at "
                            "least three distinct conventions exist: (a) {section_ar, first_article, "
                            "last_article} (patent_law, basic_law_of_governance); (b) {label_ar, "
                            "title_ar, articles} where `articles` is a free-text range string like "
                            "'2-5' (income_tax_law, traffic_law); (c) a nested-chapter form with an "
                            "inner `chapters` or `sections` array (zakat_law, social_insurance_law, "
                            "reflecting a أبواب/فصول/فروع nesting deeper than a flat chapter list). "
                            "Treat this field as informational/display-only prose structure, NOT a "
                            "reliably machine-parseable article-range index — use each article's own "
                            "section_ar/section_context_ar field instead for programmatic grouping."
                        )},
                    "articles": {"type": "object",
                        "additionalProperties": {"$ref": "#/$defs/OfficialSourceArticleRecordStandard"},
                        "propertyNames": {"pattern": "^[a-z0-9_]+_(art|art_)?[0-9a-z_]+$"},
                        "description": "Map of article_key -> article record, one entry per numbered article "
                                       "(including 'مكرر' inserted articles)."},
                    "known_unresolved_discrepancies": {"type": "array",
                        "items": {"type": "object",
                            "required": ["article_key", "description"],
                            "properties": {
                                "article_key": {"type": "string"},
                                "description": {"type": "string"},
                            }},
                        "description": "Explicitly-flagged, unresolved data-quality caveats for this track "
                                       "(may be an empty array)."},
                    "provenance": {"type": "object",
                        "description": "OPTIONAL. Structured source-access metadata (portal URLs, access "
                                        "method, source PDF sha256/page count/extraction method). Pioneered "
                                        "by, and so far unique to, basic_law_of_governance.",
                        "additionalProperties": True},
                },
                "additionalProperties": True,
            },
            "OfficialSourceLegacyCivil": {
                "title": "Official source document (legacy civil_transactions_law convention)",
                "type": "object",
                "required": [
                    "law_key", "law_component", "title_ar", "title_en", "royal_decree",
                    "source_authority", "source_authority_ar", "preamble_ar", "capture_method",
                    "boundaries", "article_count", "articles",
                ],
                "properties": {
                    "law_key": {"type": "string", "const": "civil"},
                    "law_component": {"type": "string", "const": "law"},
                    "title_ar": {"type": "string"},
                    "title_en": {"type": "string"},
                    "royal_decree": {"type": "string"},
                    "source_authority": {"type": "string"},
                    "source_authority_ar": {"type": "string"},
                    "preamble_ar": {"type": "string"},
                    "capture_method": {"type": "string",
                        "description": "Free-text description of how the owner-provided text was "
                                        "parsed into articles. No equivalent field exists in the "
                                        "standard convention (subsumed by verification_methodology_note)."},
                    "boundaries": {"type": "object",
                        "required": ["arabic_governs", "translation_performed",
                                     "legal_interpretation_performed",
                                     "summarized_or_paraphrased", "english_used_for_correction"],
                        "properties": {
                            "arabic_governs": {"type": "boolean"},
                            "translation_performed": {"type": "boolean"},
                            "legal_interpretation_performed": {"type": "boolean"},
                            "summarized_or_paraphrased": {"type": "boolean"},
                            "english_used_for_correction": {"type": "boolean"},
                        }},
                    "moj_cross_check": {"type": "object",
                        "description": "OPTIONAL. Present only on civil_transactions_law: a record of the "
                                        "MOJ-portal cross-check pass (checked_on, method, corrections applied).",
                        "additionalProperties": True},
                    "article_count": {"type": "integer"},
                    "articles": {"type": "object",
                        "additionalProperties": {"$ref": "#/$defs/OfficialSourceArticleRecordLegacyCivil"}},
                },
                "additionalProperties": True,
            },
        },
    }


def verified_record_schema():
    return {
        "$schema": DIALECT,
        "$id": "https://github.com/al3obdi/saudi-legal-corpus-ai/schemas/manifest/verified_record_schema.json",
        "title": "Verified record (per-track verified JSONL record)",
        "description": (
            "One line of sources/<track>/<component>/verified/*_verified_records.jsonl — the "
            "flattened, article-per-line verified-text layer built from a track's official_source.json, "
            "immediately upstream of the LLM-ready layer. Two structural variants exist, mirroring "
            "official_source_schema: STANDARD (all current tracks) and LEGACY (civil_transactions_law only)."
        ),
        "oneOf": [
            {"$ref": "#/$defs/VerifiedRecordStandard"},
            {"$ref": "#/$defs/VerifiedRecordLegacyCivil"},
        ],
        "$defs": {
            "VerifiedRecordStandard": {
                "title": "Verified record (standard convention)",
                "type": "object",
                "required": [
                    "law_key", "law_component", "language", "record_layer", "article_number",
                    "is_mukarrar", "article_key", "number_label_ar", "section_ar",
                    "article_text_verified", "verification_status", "legal_status_ar",
                    "is_repealed", "is_amended", "is_added", "amendment_history",
                    "official_text_status", "governing_source_note", "translation_performed",
                    "legal_interpretation_performed", "summarized_or_paraphrased",
                    "english_used_for_correction",
                ],
                "properties": {
                    "law_key": {"type": "string", "description": "Corpus track key, e.g. 'income_tax'."},
                    "law_component": {"type": "string",
                        "description": "'law' | 'implementing_regulation' | other component kind."},
                    "language": {"type": "string", "const": "ar"},
                    "record_layer": {"type": "string",
                        "description": "Upper-case layer identifier, e.g. 'INCOME_TAX_LAW_ARABIC_VERIFIED_TEXT'."},
                    "article_number": {"type": "integer", "minimum": 1},
                    "is_mukarrar": {"type": "boolean"},
                    "article_key": {"type": "string"},
                    "number_label_ar": {"type": "string"},
                    "section_ar": {"type": "string"},
                    "article_text_verified": {"type": "string", "minLength": 1},
                    "verification_status": {"type": "string",
                        "description": "Track-wide (or, if verification_tier is present, per-article) "
                                        "verification-pipeline status code."},
                    "legal_status_ar": {"type": "string",
                        "enum": ["اصلية", "معدلة", "ملغاة", "مضافة"]},
                    "is_repealed": {"type": "boolean"},
                    "is_amended": {"type": "boolean"},
                    "is_added": {"type": "boolean"},
                    "amendment_history": {"type": "array", "items": {"type": "object"}},
                    "official_text_status": {"type": "string"},
                    "governing_source_note": {"type": "string",
                        "description": "One-line pointer back to verification_methodology_note in the "
                                        "source official_source.json plus the Arabic-governs boundary statement."},
                    "translation_performed": {"type": "boolean", "const": False},
                    "legal_interpretation_performed": {"type": "boolean", "const": False},
                    "summarized_or_paraphrased": {"type": "boolean", "const": False},
                    "english_used_for_correction": {"type": "boolean", "const": False},
                    "verification_tier": {"type": "string",
                        "description": "OPTIONAL. Per-article verification tier. Pioneered by traffic_law; "
                                        "also on basic_law_of_governance (Article 5 only)."},
                    "cross_verified_against_wipo_lex": {"type": "boolean",
                        "description": "OPTIONAL. Pioneered by basic_law_of_governance."},
                    "title_ar": {"type": "string", "description": "OPTIONAL. Seen on zakat_law."},
                },
                "patternProperties": {
                    "^original_[0-9]{4}h_text$": {"type": ["string", "null"],
                        "description": "OPTIONAL, mirrors the same field on the official_source article "
                                        "record. Absent entirely on social_insurance_law and civil_transactions_law."},
                },
                "additionalProperties": True,
            },
            "VerifiedRecordLegacyCivil": {
                "title": "Verified record (legacy civil_transactions_law convention)",
                "type": "object",
                "required": [
                    "law_key", "law_component", "language", "record_layer", "article_number",
                    "article_key", "section_context_ar", "article_text_verified",
                    "official_text_status", "verification_method", "source_authority_ar",
                    "royal_decree", "governing_source_note", "translation_performed",
                    "legal_interpretation_performed", "summarized_or_paraphrased",
                    "english_used_for_correction",
                ],
                "properties": {
                    "law_key": {"type": "string", "const": "civil"},
                    "law_component": {"type": "string", "const": "law"},
                    "language": {"type": "string", "const": "ar"},
                    "record_layer": {"type": "string"},
                    "article_number": {"type": "integer"},
                    "article_key": {"type": "string"},
                    "section_context_ar": {"type": "string",
                        "description": "Analogous to section_ar in the standard convention; may be empty string."},
                    "article_text_verified": {"type": "string", "minLength": 1},
                    "official_text_status": {"type": "string"},
                    "verification_method": {"type": "string",
                        "description": "Free-text verification narrative; the legacy analogue of "
                                        "verification_status in the standard convention."},
                    "source_authority_ar": {"type": "string"},
                    "royal_decree": {"type": "string"},
                    "governing_source_note": {"type": "string"},
                    "translation_performed": {"type": "boolean", "const": False},
                    "legal_interpretation_performed": {"type": "boolean", "const": False},
                    "summarized_or_paraphrased": {"type": "boolean", "const": False},
                    "english_used_for_correction": {"type": "boolean", "const": False},
                },
                "additionalProperties": True,
            },
        },
    }


def _source_trust_schema():
    return {
        "title": "source_trust",
        "type": "object",
        "required": ["source_authority", "source_authority_ar", "source_status", "source_document_ar"],
        "properties": {
            "source_authority": {"type": "string"},
            "source_authority_ar": {"type": "string"},
            "source_status": {"type": "string",
                "description": "Lower/mixed-case machine status code, usually the lower-cased "
                                "official_text_status / text_status value."},
            "source_document_ar": {"type": "string"},
            "royal_decree": {"type": "string",
                "description": "OPTIONAL. Present in the legacy civil_transactions_law convention "
                                "(a simple decree label) and absent from the standard convention, "
                                "which instead folds decree provenance into source_authority."},
            "legal_status_ar": {"type": "string",
                "description": "OPTIONAL. Duplicated per-record legal status. Standard convention only."},
            "verification_status": {"type": "string",
                "description": "OPTIONAL. Duplicated per-record verification status. Standard convention only."},
        },
        "additionalProperties": True,
    }


def llm_ready_layer_schema():
    return {
        "$schema": DIALECT,
        "$id": "https://github.com/al3obdi/saudi-legal-corpus-ai/schemas/manifest/llm_ready_layer_schema.json",
        "title": "LLM-ready layer (per-track LLM-ready JSON)",
        "description": (
            "data/<track>_arabic_legal_llm/*.json — the flattened, query-ready retrieval layer built "
            "from a track's verified/ records: an envelope object carrying a `records` array of "
            "per-article retrieval records. This is the layer most directly useful to an external "
            "RAG integrator. Two structural variants exist: STANDARD (income_tax_law/patent_law/"
            "zakat_law and the great majority of tracks) and LEGACY (civil_transactions_law only)."
        ),
        "oneOf": [
            {"$ref": "#/$defs/LlmReadyEnvelopeStandard"},
            {"$ref": "#/$defs/LlmReadyEnvelopeLegacyCivil"},
        ],
        "$defs": {
            "SourceTrust": _source_trust_schema(),
            "LlmReadyRecordStandard": {
                "title": "LLM-ready article record (standard convention)",
                "type": "object",
                "required": [
                    "law_id", "law_component", "article_number", "is_mukarrar", "article_key",
                    "article_title_ar", "section_ar", "legal_status_ar", "is_repealed",
                    "is_amended", "is_added", "record_id", "record_type", "language",
                    "governing_text_language", "article_text_ar", "article_text_hash_sha256",
                    "llm_title_ar", "retrieval_title_ar", "article_path", "keywords_ar",
                    "search_queries_ar", "text_status", "source_trust", "translation_performed",
                    "legal_interpretation_performed", "english_used_for_correction",
                    "text_summarized_or_paraphrased",
                ],
                "properties": {
                    "law_id": {"type": "string", "description": "Stable law identifier, e.g. 'sa-income-tax-law-m1-1425'."},
                    "law_component": {"type": "string"},
                    "article_number": {"type": "integer", "minimum": 1},
                    "is_mukarrar": {"type": "boolean"},
                    "article_key": {"type": "string"},
                    "article_title_ar": {"type": "string", "minLength": 1},
                    "section_ar": {"type": "string"},
                    "legal_status_ar": {"type": "string",
                        "enum": ["اصلية", "معدلة", "ملغاة", "مضافة"]},
                    "is_repealed": {"type": "boolean"},
                    "is_amended": {"type": "boolean"},
                    "is_added": {"type": "boolean"},
                    "record_id": {"type": "string"},
                    "record_type": {"type": "string",
                        "description": "e.g. 'verified_arabic_article' (standard) or "
                                        "'official_arabic_article' (civil_transactions_law)."},
                    "language": {"type": "string", "const": "ar"},
                    "governing_text_language": {"type": "string", "const": "ar"},
                    "article_text_ar": {"type": "string", "minLength": 1},
                    "article_text_hash_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    "llm_title_ar": {"type": "string", "minLength": 1},
                    "retrieval_title_ar": {"type": "string", "minLength": 1},
                    "article_path": {"type": "string"},
                    "keywords_ar": {"type": "array", "items": {"type": "string"}},
                    "search_queries_ar": {"type": "array", "items": {"type": "string"}},
                    "text_status": {"type": "string"},
                    "source_trust": {"$ref": "#/$defs/SourceTrust"},
                    "translation_performed": {"type": "boolean", "const": False},
                    "legal_interpretation_performed": {"type": "boolean", "const": False},
                    "english_used_for_correction": {"type": "boolean", "const": False},
                    "text_summarized_or_paraphrased": {"type": "boolean", "const": False},
                },
                "additionalProperties": True,
            },
            "LlmReadyRecordLegacyCivil": {
                "title": "LLM-ready article record (legacy civil_transactions_law convention)",
                "type": "object",
                "required": [
                    "law_id", "law_component", "article_number", "article_key", "article_title_ar",
                    "record_id", "record_type", "language", "governing_text_language",
                    "section_context_ar", "article_text_ar", "article_text_hash_sha256",
                    "llm_title_ar", "retrieval_title_ar", "article_path", "keywords_ar",
                    "search_queries_ar", "text_status", "source_trust", "translation_performed",
                    "legal_interpretation_performed", "english_used_for_correction",
                    "text_summarized_or_paraphrased",
                ],
                "properties": {
                    "law_id": {"type": "string", "const": "sa-civil-transactions-law-m191-1444"},
                    "law_component": {"type": "string", "const": "law"},
                    "article_number": {"type": "integer", "minimum": 1, "maximum": 721},
                    "article_key": {"type": "string"},
                    "article_title_ar": {"type": "string"},
                    "record_id": {"type": "string"},
                    "record_type": {"type": "string", "const": "official_arabic_article"},
                    "language": {"type": "string", "const": "ar"},
                    "governing_text_language": {"type": "string", "const": "ar"},
                    "section_context_ar": {"type": "string",
                        "description": "Lacks the is_amended/is_repealed/is_added/legal_status_ar fields "
                                        "the standard convention carries per-record, since the whole law "
                                        "is unamended."},
                    "article_text_ar": {"type": "string"},
                    "article_text_hash_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    "llm_title_ar": {"type": "string"},
                    "retrieval_title_ar": {"type": "string"},
                    "article_path": {"type": "string"},
                    "keywords_ar": {"type": "array", "items": {"type": "string"}},
                    "search_queries_ar": {"type": "array", "items": {"type": "string"}},
                    "text_status": {"type": "string"},
                    "source_trust": {"$ref": "#/$defs/SourceTrust"},
                    "translation_performed": {"type": "boolean", "const": False},
                    "legal_interpretation_performed": {"type": "boolean", "const": False},
                    "english_used_for_correction": {"type": "boolean", "const": False},
                    "text_summarized_or_paraphrased": {"type": "boolean", "const": False},
                },
                "additionalProperties": True,
            },
            "LlmReadyEnvelopeStandard": {
                "title": "LLM-ready layer envelope (standard convention)",
                "type": "object",
                "required": [
                    "layer_id", "law_id", "law_component", "title_ar", "record_type", "language",
                    "governing_text_language", "record_count", "article_range",
                    "consolidated_amended_law", "status_counts", "text_status",
                    "not_legal_advice", "records",
                ],
                "properties": {
                    "layer_id": {"type": "string"},
                    "law_id": {"type": "string"},
                    "law_component": {"type": "string"},
                    "title_ar": {"type": "string"},
                    "title_en": {"type": "string", "description": "OPTIONAL. Absent on e.g. patent_law/zakat_law."},
                    "record_type": {"type": "string"},
                    "language": {"type": "string", "const": "ar"},
                    "governing_text_language": {"type": "string", "const": "ar"},
                    "record_count": {"type": "integer", "minimum": 1},
                    "article_range": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
                    "consolidated_amended_law": {"type": "boolean"},
                    "status_counts": {"type": "object"},
                    "text_status": {"type": "string"},
                    "not_legal_advice": {"type": "boolean", "const": True},
                    "records": {"type": "array", "items": {"$ref": "#/$defs/LlmReadyRecordStandard"}},
                },
                "additionalProperties": True,
            },
            "LlmReadyEnvelopeLegacyCivil": {
                "title": "LLM-ready layer envelope (legacy civil_transactions_law convention)",
                "type": "object",
                "required": [
                    "layer_id", "law_id", "law_component", "title_ar", "title_en", "record_type",
                    "language", "governing_text_language", "record_count", "article_range",
                    "source_verified_file", "schema", "text_status", "not_legal_advice",
                    "disclaimer_ar", "records",
                ],
                "properties": {
                    "layer_id": {"type": "string"},
                    "law_id": {"type": "string"},
                    "law_component": {"type": "string"},
                    "title_ar": {"type": "string"},
                    "title_en": {"type": "string"},
                    "record_type": {"type": "string"},
                    "language": {"type": "string", "const": "ar"},
                    "governing_text_language": {"type": "string", "const": "ar"},
                    "record_count": {"type": "integer"},
                    "article_range": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
                    "source_verified_file": {"type": "string",
                        "description": "Relative path back to the verified/*.jsonl this layer was built "
                                        "from. No equivalent field exists in the standard convention."},
                    "schema": {"type": "string",
                        "description": "Relative path to a per-track draft-07 JSON Schema file under "
                                        "schemas/. Unique to civil_transactions_law; the standard "
                                        "convention has no per-record schema pointer field."},
                    "text_status": {"type": "string"},
                    "not_legal_advice": {"type": "boolean", "const": True},
                    "disclaimer_ar": {"type": "string"},
                    "records": {"type": "array", "items": {"$ref": "#/$defs/LlmReadyRecordLegacyCivil"}},
                },
                "additionalProperties": True,
            },
        },
    }


def unified_index_record_schema():
    return {
        "$schema": DIALECT,
        "$id": "https://github.com/al3obdi/saudi-legal-corpus-ai/schemas/manifest/unified_index_record_schema.json",
        "title": "Unified index record (one line of the corpus-wide unified JSONL index)",
        "description": (
            "data/corpus_unified_index/corpus_unified_llm_index.jsonl — one flat retrieval record per "
            "article, normalized across every _arabic_legal_llm layer in the corpus by "
            "scripts/gen_corpus_unified_llm_index.py. This is the single flattest, most "
            "corpus-spanning entry point for a retrieval application: it is the only layer where "
            "every track's articles appear side-by-side with a common field set, regardless of which "
            "of the two llm_ready_layer_schema conventions (standard/legacy) the source track uses. "
            "Fully mechanically derived (scripts/gen_corpus_unified_llm_index.py rows.append(...) "
            "block); every key below is always written by the generator, though `law_id`, "
            "`llm_title_ar`, `retrieval_title_ar`, and `article_path` may be null if the underlying "
            "source record omitted them (r.get(...) with no default)."
        ),
        "type": "object",
        "required": [
            "record_id", "corpus", "law_id", "law_component", "law_title_ar", "article_number",
            "unit_label_ar", "is_appendix",
            "llm_title_ar", "retrieval_title_ar", "article_path", "keywords_ar", "search_queries_ar",
            "text_ar", "text_status", "source_layer",
        ],
        "properties": {
            "record_id": {"type": "string", "description": "Copied verbatim from the source layer's record_id."},
            "corpus": {"type": "string",
                "description": (
                    "Corpus track key, e.g. 'civil', 'patent', 'zakat'. IMPORTANT: this is usually "
                    "NOT the same string as `track_id` in corpus_registry_track_schema/"
                    "verification_tier_entry_schema/the two graph schemas/glossary_term_schema — "
                    "of the 123 registry track_ids, 121 differ from their corpus key (the registry "
                    "track_id typically adds a component suffix, e.g. registry track_id "
                    "'civil_transactions_law' / 'patent_law' / 'anti_bribery_law' vs. this field's "
                    "'civil' / 'patent' / 'anti_bribery'; a single corpus key like 'arbitration' can "
                    "also correspond to TWO registry track_ids, 'arbitration_law' and "
                    "'arbitration_implementing_regulation', disambiguated by law_component). Joining "
                    "across layers on identity alone will silently drop rows — see the companion "
                    "guide's quick-start for the correct join approach."
                )},
            "law_id": {"type": ["string", "null"]},
            "law_component": {"type": "string",
                "description": "'law' | 'implementing_regulation' | other component kind, defaulted per-layer "
                                "if the source record omits it."},
            "law_title_ar": {"type": "string",
                "description": "Friendly Arabic law title, derived from the source envelope's title_ar "
                                "(text before the em-dash, if present)."},
            "article_number": {"type": "integer",
                "description": (
                    "POSITIONAL index within the track, not a citation. 1,476 records in this index "
                    "are appendices, tables, ordinal bands or numbered clauses rather than articles, "
                    "and rendering «مادة N» from this integer would announce one of them as an "
                    "article — a false citation invented by the reader. Cite `unit_label_ar`."
                )},
            "unit_label_ar": {"type": ["string", "null"],
                "description": (
                    "The unit as the SOURCE printed it — «المادة الأولى», «الملحق 9 (أ)», «أولاً», "
                    "«جدول المقابل المالي». This is the citable mark."
                )},
            "is_appendix": {"type": "boolean",
                "description": "True where the source itself files the record as an appendix/annex."},
            "llm_title_ar": {"type": ["string", "null"]},
            "retrieval_title_ar": {"type": ["string", "null"]},
            "article_path": {"type": ["string", "null"]},
            "keywords_ar": {"type": "array", "items": {"type": "string"}},
            "search_queries_ar": {"type": "array", "items": {"type": "string"}},
            "text_ar": {"type": "string",
                "description": "Article text, taken from article_text_ar or official_text_ar; empty "
                                "string if neither is present."},
            "text_status": {"type": "string",
                "description": "Falls back through text_status -> source_trust.source_status -> "
                                "record_type -> the literal string 'unspecified'."},
            "source_layer": {"type": "string",
                "description": "Basename of the source _arabic_legal_llm JSON file this record was "
                                "projected from."},
        },
        "additionalProperties": False,
    }


def corpus_registry_track_schema():
    return {
        "$schema": DIALECT,
        "$id": "https://github.com/al3obdi/saudi-legal-corpus-ai/schemas/manifest/corpus_registry_track_schema.json",
        "title": "Corpus registry track entry",
        "description": (
            "One entry in the `tracks` array of data/corpus_registry/corpus_registry.json — the "
            "canonical, machine-readable summary of one of this corpus's 123 tracks. Required/optional "
            "split below was computed empirically across all 123 real entries in the current registry "
            "(not a curated guess): fields present on fewer than all 123 tracks are optional."
        ),
        "type": "object",
        "required": [
            "track_id", "display_name_ar", "corpus_family", "governing_language", "jurisdiction",
            "status", "language_layers", "record_counts", "data_paths", "report_paths",
            "validator_targets", "boundaries", "notes",
        ],
        "properties": {
            "track_id": {"type": "string", "description": "Stable snake_case track identifier, e.g. 'patent_law'."},
            "display_name_ar": {"type": "string"},
            "display_name_en": {"type": "string",
                "description": "OPTIONAL — present on 120/123 tracks (absent on a few Arabic-only-titled "
                                "procedural-rules tracks)."},
            "corpus_family": {"type": "string",
                "enum": ["statutory_law", "implementing_regulation", "procedural_rules", "closure_audit"]},
            "governing_language": {"type": "string", "const": "ar"},
            "jurisdiction": {"type": "string", "const": "Kingdom of Saudi Arabia"},
            "status": {"type": "string", "description": "e.g. 'complete'."},
            "official_text_status": {"type": ["string", "null"],
                "description": "OPTIONAL — present on 119/123 tracks. Null/absent on the 4 earliest "
                                "tracks predating this verification-tiering convention (companies_law "
                                "and the two implementing_regulations_* tracks plus the closure_audit "
                                "track); see corpus_verification_tiers_schema's NULL_STATUS_TRACK_TIER "
                                "handling for how those 4 are still tiered."},
            "source_authority": {"type": "string",
                "description": "OPTIONAL — present on 121/123 tracks."},
            "source_url": {"type": "string",
                "description": "OPTIONAL — present on only 3/123 tracks; most tracks document sources "
                                "in `notes` prose instead of a structured URL field."},
            "publication_date_hijri": {"type": "string",
                "description": "OPTIONAL — present on only 3/123 tracks."},
            "publication_date_gregorian": {"type": "string",
                "description": "OPTIONAL — present on only 3/123 tracks."},
            "language_layers": {"type": "object",
                "description": "Keyed by language ('arabic', 'english', 'chinese', ...). Shape varies "
                                "by role: a governing Arabic layer carries data_path/governing/"
                                "record_count/status; a non-governing reference layer (e.g. companies_law's "
                                "'chinese' entry) carries role/note/total_articles_in_plan/"
                                "total_articles_implemented/closure_audit_path instead.",
                "additionalProperties": {"type": "object", "additionalProperties": True}},
            "record_counts": {"type": "object",
                "description": "Keys vary per track (e.g. 'arabic_articles'/'total'/'legal_status_breakdown' "
                                "for a simple law track; 'general_articles'/'general_forms'/"
                                "'listed_jsc_articles'/... for the companies-law implementing-regulations "
                                "family). Always includes some form of a 'total'.",
                "additionalProperties": True},
            "data_paths": {"type": "array", "items": {"type": "string"},
                "description": "Relative repo paths to this track's official_source/verified/LLM-ready files."},
            "manifest_paths": {"type": "array", "items": {"type": "string"},
                "description": "OPTIONAL — present on only 4/123 tracks (the companies-law family, which "
                                "has a dedicated law-profile manifest under data/legal_corpus_factory/)."},
            "report_paths": {"type": "array", "items": {"type": "string"}},
            "validator_targets": {"type": "array", "items": {"type": "string"},
                "description": "Makefile target name(s) that validate this track (documented here for "
                                "reference only — this manifest does not touch the Makefile itself)."},
            "boundaries": {"type": "object",
                "description": "Mostly-boolean disclosure flags. Common keys: arabic_governs, "
                                "not_official_translation, not_verified_official_text, not_legal_advice, "
                                "no_trilingual_alignment, no_public_release. companies_law additionally "
                                "carries chinese_internal_reference_only/english_reference_only. NOT "
                                "purely boolean-valued: implementing_regulations_listed_joint_stock adds "
                                "a free-text `specialized_scope` string key alongside its "
                                "is_general/is_specialized booleans.",
                "additionalProperties": {"type": ["boolean", "string"]}},
            "notes": {"type": "string",
                "description": "Long-form free-text provenance/methodology/caveat narrative for this track."},
        },
        "additionalProperties": True,
    }


def verification_tier_entry_schema():
    return {
        "$schema": DIALECT,
        "$id": "https://github.com/al3obdi/saudi-legal-corpus-ai/schemas/manifest/verification_tier_entry_schema.json",
        "title": "Verification tier entry",
        "description": (
            "One entry in the `tracks` array of "
            "data/corpus_verification_tiers/corpus_verification_tiers.json — a derived, read-only "
            "reclassification of every corpus_registry track into one of 4 fixed confidence tiers, "
            "so a RAG application can filter programmatically (e.g. 'Tier 1 only'). Fully mechanically "
            "derived from a fixed status->tier lookup table in "
            "scripts/gen_corpus_verification_tiers.py; every key below is always present."
        ),
        "type": "object",
        "required": ["track_id", "tier", "tier_rationale", "has_per_article_variation",
                     "per_article_variation_note"],
        "properties": {
            "track_id": {"type": "string"},
            "tier": {"type": "string",
                "enum": [
                    "TIER_1_PRIMARY_MULTI_SOURCE",
                    "TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED",
                    "TIER_3_SECONDARY_MULTI_SOURCE_ONLY",
                    "TIER_4_SINGLE_SOURCE_OR_MIXED_CONFIDENCE",
                ],
                "description": (
                    "TIER_1: 2+ independent official/primary sources agree, no reachability gap. "
                    "TIER_2: one official source, cross-verified only against non-governmental "
                    "secondary sources. TIER_3: primary portal unreachable, 2+ independent secondary "
                    "sources agree with each other. TIER_4: single-sourced for a meaningfully-sized "
                    "part, and/or an explicit documented mixed/per-article-confidence split — assigned "
                    "using the WEAKEST meaningfully-sized portion of the track, not the strongest."
                )},
            "tier_rationale": {"type": "string",
                "description": "One-line (or, for ~20 tracks, a hand-curated longer) justification, "
                                "always naming the track's own official_text_status value."},
            "has_per_article_variation": {"type": "boolean",
                "description": "True for tracks with documented, non-negligible confidence variation "
                                "ACROSS articles within the same track (e.g. traffic_law: 67/86 "
                                "PRIMARY_INDEPENDENTLY_CONFIRMED vs 19/86 SECONDARY_SOURCE_ONLY_BOE_KNOWN_STALE)."},
            "per_article_variation_note": {"type": "string",
                "description": "Empty string when has_per_article_variation is false; otherwise a "
                                "one-line pointer back to the track's own official_source.json "
                                "(never recomputes the underlying per-article verification_tier data)."},
        },
        "additionalProperties": False,
    }


def supersession_edge_schema():
    return {
        "$schema": DIALECT,
        "$id": "https://github.com/al3obdi/saudi-legal-corpus-ai/schemas/manifest/supersession_edge_schema.json",
        "title": "Supersession/repeal edge",
        "description": (
            "One entry in the `edges` array of "
            "data/corpus_supersession_graph/corpus_supersession_graph.json — a hand-curated, "
            "individually-verified repeal/supersession relationship between a corpus track and either "
            "another corpus track or an untracked predecessor/successor instrument. Two sibling arrays "
            "in the same file use related-but-distinct entry shapes, documented here as $defs: "
            "concurrent_title_collisions (a shared title/decree-number NOT a repeal relationship) and "
            "ambiguous_or_excluded_cases (a real signal that does not meet the bar for a clean edge)."
        ),
        "type": "object",
        "required": ["from_track_id", "relation", "target_track_id", "target_description_ar",
                     "target_decree", "affected_articles", "note", "source_ref"],
        "properties": {
            "from_track_id": {"type": "string", "description": "Must be a valid track_id in corpus_registry.json."},
            "relation": {"type": "string",
                "enum": ["repeals_full", "repeals_partial", "superseded_by",
                         "repeals_full_deferred"],
                "description": (
                    "repeals_full: from_track_id's decree explicitly/fully repeals a prior instrument "
                    "(which may or may not be a corpus track). repeals_partial: from_track_id's decree "
                    "repeals only specific articles of another currently-tracked law (or an untracked "
                    "predecessor). superseded_by: from_track_id is itself confirmed superseded by a "
                    "future/newer instrument. repeals_full_deferred: from_track_id's own text "
                    "fully repeals a prior instrument but from_track_id has NOT COMMENCED yet "
                    "(published, not in force), so the target is still the law in force today "
                    "— see commencement_ar."
                )},
            "target_track_id": {"type": ["string", "null"],
                "description": "The corpus track_id being repealed/repealing, or null if the target "
                                "instrument is not itself a corpus track."},
            "target_description_ar": {"type": ["string", "null"],
                "description": "Arabic name of the target instrument when target_track_id is null."},
            "target_decree": {"type": ["string", "null"],
                "description": "Decree/resolution label of the target instrument, when known."},
            "affected_articles": {"type": ["string", "null"],
                "description": "Free-text article range description, populated mainly for repeals_partial "
                                "edges (e.g. '38-57 (commercial_courts_law) repealed by evidence_law')."},
            "note": {"type": "string", "description": "Long-form justification, always citing its source_ref."},
            "source_ref": {"type": "string",
                "description": "Path (optionally with a field pointer in parentheses) to the corpus file "
                                "this edge's claim was read from — never inferred from decree age/topic alone."},
            "commencement_ar": {"type": "string",
                "description": "OPTIONAL — present ONLY on relation='repeals_full_deferred' edges. "
                                "The successor's own commencement clause, quoted verbatim in Arabic, "
                                "so a reader can see exactly when the repeal takes effect."},
            "successor_in_corpus": {"type": "boolean",
                "description": "OPTIONAL — present ONLY on relation='superseded_by' edges. Whether the "
                                "successor instrument is itself already an ingested corpus track."},
        },
        "additionalProperties": False,
        "$defs": {
            "ConcurrentTitleCollisionEntry": {
                "title": "Concurrent title/decree-number collision (sibling array, not a repeal edge)",
                "type": "object",
                "required": ["track_ids", "shared_title_ar", "shared_decree_number", "note", "source_ref"],
                "properties": {
                    "track_ids": {"type": "array", "items": {"type": "string"}, "minItems": 2},
                    "shared_title_ar": {"type": ["string", "null"]},
                    "shared_decree_number": {"type": ["string", "null"]},
                    "note": {"type": "string"},
                    "source_ref": {"type": "string"},
                },
                "additionalProperties": False,
            },
            "AmbiguousOrExcludedCaseEntry": {
                "title": "Ambiguous or explicitly-excluded supersession candidate (sibling array)",
                "type": "object",
                "required": ["tracks_involved", "issue", "note", "source_ref"],
                "properties": {
                    "tracks_involved": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "issue": {"type": "string",
                        "description": "Short classification tag, e.g. 'unverifiable predecessor-repeal claim'."},
                    "note": {"type": "string"},
                    "source_ref": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
    }


def cross_reference_edge_schema():
    return {
        "$schema": DIALECT,
        "$id": "https://github.com/al3obdi/saudi-legal-corpus-ai/schemas/manifest/cross_reference_edge_schema.json",
        "title": "Cross-reference edge",
        "description": (
            "One entry in the `references` array of "
            "data/corpus_cross_reference_graph/corpus_cross_reference_graph.json — a best-effort, "
            "regex/pattern-based NLP extraction of one article citing another article, either within "
            "the same law (type=intra_law) or in a different law (type=inter_law). UNLIKE the rest of "
            "this corpus's article text, this is NOT an independently legally verified dataset — treat "
            "every edge as a candidate 'see also' pointer to verify against the article text itself, "
            "favoring precision over recall (ambiguous references are skipped, not force-matched)."
        ),
        "type": "object",
        "required": ["source_track_id", "source_record_id", "source_article_number", "type",
                     "target_track_id", "target_article_number", "target_law_name_raw",
                     "raw_citation_text", "confidence"],
        "properties": {
            "source_track_id": {"type": "string"},
            "source_record_id": {"type": "string",
                "description": "record_id of the citing article in its own _arabic_legal_llm layer."},
            "source_article_number": {"type": "integer"},
            "type": {"type": "string", "enum": ["intra_law", "inter_law", "ambiguous_scope"],
                "description": "intra_law: same-document citation. inter_law: citation naming a "
                                "different law, resolved (or not) against corpus_registry track titles. "
                                "ambiguous_scope: a bare backward-demonstrative reference this generator "
                                "cannot resolve without deeper discourse tracking (observed count: 0 in "
                                "the current graph, but the type is part of the documented schema)."},
            "target_track_id": {"type": ["string", "null"],
                "description": "Resolved target corpus track_id, or null if the cited law name could not "
                                "be matched to a corpus track (still recorded with the raw matched text)."},
            "target_article_number": {"type": ["integer", "null"]},
            "target_law_name_raw": {"type": ["string", "null"],
                "description": "Raw matched law-name text for inter_law citations; null for intra_law."},
            "raw_citation_text": {"type": "string",
                "description": "The actual citation substring matched in the source article's text."},
            "confidence": {"type": "string", "enum": ["high", "medium"],
                "description": "No 'low' confidence edges are ever emitted — below-medium matches are "
                                "dropped rather than recorded, per the precision-over-recall extraction policy."},
        },
        "additionalProperties": False,
    }


def glossary_term_schema():
    return {
        "$schema": DIALECT,
        "$id": "https://github.com/al3obdi/saudi-legal-corpus-ai/schemas/manifest/glossary_term_schema.json",
        "title": "Glossary term definition entry",
        "description": (
            "data/corpus_glossary/corpus_glossary.json's `terms` field is an object keyed by the "
            "Arabic term string itself (e.g. 'أدوات الدين'), mapping to an ARRAY of one-or-more "
            "definition entries (one entry per track that formally defines that exact term string in "
            "its own definitions article) — this schema describes ONE such definition entry. A term "
            "with more than one definition entry (92 of 696 terms in the current corpus, e.g. "
            "'إعادة التأهيل' defined separately by both environmental_law and mining_investment_law) "
            "signals a term whose legal meaning may genuinely differ by law; this is preserved "
            "verbatim per-track rather than merged/deduplicated."
        ),
        "type": "object",
        "required": ["track_id", "article_number", "term_as_written", "definition_text",
                     "source_record_id", "extraction_method"],
        "properties": {
            "track_id": {"type": "string", "description": "The corpus track whose definitions article this came from."},
            "article_number": {"type": "integer", "description": "Almost always 1 (the definitions article "
                                "is conventionally the law's first article), but not schema-enforced as such."},
            "term_as_written": {"type": "string", "description": "The defined term, exactly as written in the source article."},
            "definition_text": {"type": "string", "description": "The verbatim Arabic definition text."},
            "source_record_id": {"type": "string",
                "description": "record_id of the definitions article in its own _arabic_legal_llm layer."},
            "extraction_method": {"type": "string",
                "enum": ["colon_pairs", "parenthesized_term", "entries_only_no_intro"],
                "description": (
                    "colon_pairs: 'الأجل: التعريف' list format. parenthesized_term: term given in "
                    "parentheses form. entries_only_no_intro: a parseable term:definition list found "
                    "without the generator's standard definitions-article intro-clause trigger phrase."
                )},
        },
        "additionalProperties": False,
    }


def chunking_layer_chunk_schema():
    return {
        "$schema": DIALECT,
        "$id": "https://github.com/al3obdi/saudi-legal-corpus-ai/schemas/manifest/chunking_layer_chunk_schema.json",
        "title": "Chunking layer chunk record",
        "description": (
            "One line of data/corpus_chunking_layer/corpus_chunking_layer.jsonl — a retrieval "
            "chunk. An article short enough to embed whole appears as a single chunk with "
            "`is_full_article: true` and `total_chunks_for_this_article: 1`; a long article is "
            "split into overlapping windows carrying the SAME `source_record_id`, so a hit on any "
            "window resolves back to one citable article. `char_start`/`char_end` are offsets into "
            "that article's own `text_ar`, which is what makes a chunk quotable rather than merely "
            "findable."
        ),
        "type": "object",
        "required": ["chunk_id", "source_record_id", "source_layer", "corpus", "law_id",
                     "law_component", "law_title_ar", "article_number", "article_path",
                     "chunk_index", "total_chunks_for_this_article", "is_full_article",
                     "char_start", "char_end", "word_count", "text_ar", "text_status"],
        "properties": {
            "chunk_id": {"type": "string",
                "description": "Unique per chunk: the source record_id with a chunk suffix."},
            "source_record_id": {"type": "string",
                "description": "The unified-index record this chunk came from. NOT unique across "
                               "the file — every window of one article repeats it, which is the "
                               "join back to a single citation."},
            "source_layer": {"type": "string"},
            "corpus": {"type": "string"},
            "law_id": {"type": "string"},
            "law_component": {"type": "string"},
            "law_title_ar": {"type": "string"},
            "llm_title_ar": {"type": ["string", "null"]},
            "retrieval_title_ar": {"type": ["string", "null"]},
            "unit_label_ar": {"type": ["string", "null"],
                "description": "The unit label as the SOURCE printed it («المادة الأولى», «جدول», "
                               "«ملحق»). Present so a display never renders «مادة N» for a record "
                               "that is not an article."},
            "article_number": {"type": ["integer", "null"]},
            "article_path": {"type": "string"},
            "is_appendix": {"type": "boolean"},
            "chunk_index": {"type": "integer", "description": "0-based within its article."},
            "total_chunks_for_this_article": {"type": "integer", "minimum": 1},
            "is_full_article": {"type": "boolean",
                "description": "True iff the article was short enough to survive unsplit."},
            "overlap_words_with_previous": {"type": "integer", "minimum": 0,
                "description": "0 for the first chunk of an article."},
            "char_start": {"type": "integer", "minimum": 0},
            "char_end": {"type": "integer", "minimum": 0},
            "word_count": {"type": "integer", "minimum": 0},
            "text_ar": {"type": "string"},
            "text_status": {"type": "string"},
            "keywords_ar": {"type": "array", "items": {"type": "string"}},
            "search_queries_ar": {"type": "array", "items": {"type": "string"}},
        },
        "additionalProperties": False,
    }


def freshness_manifest_track_schema():
    return {
        "$schema": DIALECT,
        "$id": "https://github.com/al3obdi/saudi-legal-corpus-ai/schemas/manifest/freshness_manifest_track_schema.json",
        "title": "Freshness manifest track entry",
        "description": (
            "One entry in the `tracks` array of "
            "data/corpus_freshness_manifest/corpus_freshness_manifest.json — what is known about "
            "how CURRENT a track's stored text is, and where to go to check. Two distinct risks "
            "are recorded separately and must not be conflated: "
            "`known_source_staleness_risk` is a judgement about the SOURCE (the official portal "
            "may itself be serving an old edition), while "
            "`published_amendment_after_edition_on_file` is a measured fact about the GAZETTE (a "
            "notice naming this instrument was published after the edition held here). The second "
            "is evidence; the first is a caution."
        ),
        "type": "object",
        "required": ["track_id", "display_name_ar", "official_source_file", "verification_tier",
                     "known_source_staleness_risk",
                     "published_amendment_after_edition_on_file"],
        "properties": {
            "track_id": {"type": "string"},
            "display_name_ar": {"type": "string"},
            "display_name_en": {"type": ["string", "null"]},
            "official_source_file": {"type": "string"},
            "verification_tier": {"type": "string"},
            "verification_tier_rationale": {"type": ["string", "null"]},
            "registry_source_authority": {"type": ["string", "null"]},
            "registry_source_url": {"type": ["string", "null"]},
            "source_urls": {"type": "array", "items": {"type": "string"}},
            "named_source_authorities": {"type": "array", "items": {"type": "string"}},
            "last_verified_context": {"type": ["string", "null"]},
            "known_source_staleness_risk": {"type": "boolean"},
            "known_source_staleness_pointer": {"type": ["string", "null"]},
            "published_amendment_after_edition_on_file": {"type": "boolean"},
            "published_amendment_pointer": {"type": ["string", "null"],
                "description": "Where to read the notice. Null when the flag is false."},
        },
        "additionalProperties": False,
    }


def caveat_layer_record_schema():
    return {
        "$schema": DIALECT,
        "$id": "https://github.com/al3obdi/saudi-legal-corpus-ai/schemas/manifest/caveat_layer_record_schema.json",
        "title": "Caveat layer record",
        "description": (
            "One line of data/corpus_caveat_layer/corpus_caveat_layer.jsonl, keyed by the SAME "
            "`record_id` the unified index returns, so a retrieval hit can be qualified at the "
            "moment it is cited rather than in a source file no reader opens. Caveats are split "
            "by consequence, not by topic: MATERIAL changes how (or whether) the text may be "
            "cited; PROVENANCE says how it was obtained. `caveats_other_keys` carries any "
            "disclosure whose key matched neither vocabulary, VERBATIM — a closed vocabulary that "
            "silently absorbed what it did not recognise would report the same success either way."
        ),
        "type": "object",
        "required": ["record_id", "corpus", "caveats_material", "caveats_provenance",
                     "caveats_other_keys", "caveat_summary_ar", "disclosures_ref"],
        "properties": {
            "record_id": {"type": "string",
                "description": "Joins to unified_index_record_schema/record_id."},
            "corpus": {"type": "string"},
            "caveats_material": {"type": "array", "items": {"type": "string"},
                "description": "Codes from the generator's MATERIAL vocabulary. `repealed` "
                               "outranks the rest: the others qualify how a text may be cited, "
                               "that one says it may not be cited as law at all."},
            "caveats_provenance": {"type": "array", "items": {"type": "string"}},
            "caveats_other_keys": {"type": "array", "items": {"type": "string"},
                "description": "Unrecognised disclosure keys, carried through rather than dropped."},
            "caveat_summary_ar": {"type": "string",
                "description": "One Arabic line per material code, joined by ' | '. Empty when "
                               "the record carries no MATERIAL caveat."},
            "disclosures_ref": {"type": "string",
                "description": "path#field pointing at the full text of the disclosures."},
        },
        "additionalProperties": False,
    }


def amendment_timeline_record_schema():
    return {
        "$schema": DIALECT,
        "$id": "https://github.com/al3obdi/saudi-legal-corpus-ai/schemas/manifest/amendment_timeline_record_schema.json",
        "title": "Amendment timeline record",
        "description": (
            "One line of data/corpus_amendment_timeline/corpus_amendment_timeline.jsonl — one "
            "AMENDED article (legal_status_ar in معدلة/مضافة/ملغاة), keyed by `record_id`. The "
            "corpus stores consolidated current text, which answers «what does this article say "
            "today?» and silently drops «since when?»; this layer carries the second answer to "
            "the identifier retrieval already returns. `dating_status` has exactly three values "
            "and the third is the point of the layer: `undated` is RECORDED rather than omitted, "
            "because an absent row reads as «never amended», which is a different statement and a "
            "false one."
        ),
        "type": "object",
        "required": ["record_id", "track_id", "article_key", "law_id", "law_component",
                     "legal_status_ar", "dating_status", "amendments", "conflicting_dates",
                     "since_when_note_ar"],
        "properties": {
            "record_id": {"type": "string",
                "description": "Joins to unified_index_record_schema/record_id."},
            "track_id": {"type": "string"},
            "article_key": {"type": "string"},
            "article_number": {"type": ["integer", "null"]},
            "law_id": {"type": "string"},
            "law_component": {"type": "string"},
            "legal_status_ar": {"type": "string", "enum": ["معدلة", "مضافة", "ملغاة"]},
            "dating_status": {"type": "string",
                "enum": ["dated", "disclosed_conflict", "undated"]},
            "amendments": {"type": "array", "items": {
                "type": "object",
                "required": ["instrument_ar", "evidence"],
                "properties": {
                    "instrument_ar": {"type": "string",
                        "description": "Must appear VERBATIM in the track's own source artifact."},
                    "date_hijri": {"type": ["string", "null"]},
                    "date_gregorian": {"type": ["string", "null"]},
                    "date_read_from": {"type": ["string", "null"]},
                    "note_ar": {"type": ["string", "null"]},
                    "evidence": {"type": "string",
                        "description": "Which channel established the date. The footnote channel "
                                       "requires agreement on BOTH the decision number and the "
                                       "date: a single agreement is a coincidence."},
                },
                "additionalProperties": True}},
            "conflicting_dates": {"type": "array", "items": {
                "type": "object",
                "required": ["instrument_ar", "date_printed_in_the_article_text",
                             "date_in_the_document_level_history", "note_ar"],
                "properties": {
                    "instrument_ar": {"type": "string"},
                    "date_printed_in_the_article_text": {"type": "string"},
                    "date_in_the_document_level_history": {"type": "string"},
                    "note_ar": {"type": "string"},
                },
                "additionalProperties": False},
                "description": "The source giving two dates for one instrument. BOTH are stated "
                               "and NEITHER is asserted."},
            "since_when_note_ar": {"type": "string",
                "description": "The Arabic line a reading surface prints under a hit."},
        },
        "additionalProperties": False,
    }


def retrieval_eval_query_schema():
    return {
        "$schema": DIALECT,
        "$id": "https://github.com/al3obdi/saudi-legal-corpus-ai/schemas/manifest/retrieval_eval_query_schema.json",
        "title": "Retrieval evaluation gold query",
        "description": (
            "One entry in the `queries` array of "
            "data/corpus_retrieval_eval/corpus_retrieval_eval_queries.json — a natural-language "
            "Arabic question paired with the ONE article that answers it. The gold is written as "
            "(corpus, law_component, article_number) rather than as a record_id on purpose: a "
            "record_id changes when a layer is rebuilt, and a question whose expected answer moves "
            "with the plumbing measures the plumbing. Two queries per track, so the score cannot "
            "be carried by a handful of well-covered laws."
        ),
        "type": "object",
        "required": ["query_id", "query_ar", "category", "gold"],
        "properties": {
            "query_id": {"type": "string",
                "description": "Stable id. Generated tracks use gz-<sha1(track)[:6]>-{1,2}."},
            "query_ar": {"type": "string", "description": "The question, in Arabic."},
            "category": {"type": "string",
                "description": "definitional / procedural / penalty / scope ... — used to read "
                               "WHERE retrieval fails, not only how often."},
            "gold": {
                "type": "object",
                "required": ["corpus", "law_component", "article_number"],
                "properties": {
                    "corpus": {"type": "string"},
                    "law_component": {"type": "string"},
                    "article_number": {"type": "integer"},
                },
                "additionalProperties": False,
                "description": "Addressed by law and article, not by record identity."},
        },
        "additionalProperties": False,
    }


def retrieval_eval_result_schema():
    return {
        "$schema": DIALECT,
        "$id": "https://github.com/al3obdi/saudi-legal-corpus-ai/schemas/manifest/retrieval_eval_result_schema.json",
        "title": "Retrieval evaluation per-query result",
        "description": (
            "One entry in the `per_query` array of "
            "data/corpus_retrieval_eval/corpus_retrieval_eval_results.json. `gold_rank` is the "
            "position at which the expected article was actually returned, or null if it was not "
            "in the top-k at all — recorded per query rather than only in aggregate, because an "
            "accuracy number tells you how often retrieval failed and this tells you WHICH "
            "questions it failed, which is the only form a miss can be argued with. The file's "
            "`metrics` object carries the aggregate (top1/top3/top5 accuracy, MRR@5, misses)."
        ),
        "type": "object",
        "required": ["query_id", "query_ar", "category", "gold", "gold_rank",
                     "hit_top1", "hit_top3", "hit_top5", "top_hits"],
        "properties": {
            "query_id": {"type": "string"},
            "query_ar": {"type": "string"},
            "category": {"type": "string"},
            "gold": {"type": "object",
                "description": "Copied verbatim from retrieval_eval_query_schema/gold."},
            "gold_rank": {"type": ["integer", "null"],
                "description": "1-based rank of the expected article; null == not returned in top-k."},
            "hit_top1": {"type": "boolean"},
            "hit_top3": {"type": "boolean"},
            "hit_top5": {"type": "boolean"},
            "top_hits": {"type": "array", "items": {"type": "object"},
                "description": "What retrieval DID return, so a miss can be read rather than "
                               "merely counted."},
        },
        "additionalProperties": False,
    }


SCHEMA_BUILDERS = {
    "official_source_schema": official_source_schema,
    "verified_record_schema": verified_record_schema,
    "llm_ready_layer_schema": llm_ready_layer_schema,
    "unified_index_record_schema": unified_index_record_schema,
    "corpus_registry_track_schema": corpus_registry_track_schema,
    "verification_tier_entry_schema": verification_tier_entry_schema,
    "supersession_edge_schema": supersession_edge_schema,
    "cross_reference_edge_schema": cross_reference_edge_schema,
    "glossary_term_schema": glossary_term_schema,
    "chunking_layer_chunk_schema": chunking_layer_chunk_schema,
    "freshness_manifest_track_schema": freshness_manifest_track_schema,
    "caveat_layer_record_schema": caveat_layer_record_schema,
    "amendment_timeline_record_schema": amendment_timeline_record_schema,
    "retrieval_eval_query_schema": retrieval_eval_query_schema,
    "retrieval_eval_result_schema": retrieval_eval_result_schema,
}


# ---------------------------------------------------------------------------
# field_provenance_notes: human-readable summary of every optional/
# track-specific field documented above, with a pointer to the pioneering/
# example track(s). This is the step-3 deliverable content.
# ---------------------------------------------------------------------------

def field_provenance_notes():
    return {
        "official_source_schema": [
            {"field": "document_en", "status": "optional",
             "description": "English law title.", "example_tracks": ["income_tax_law", "zakat_law"],
             "counter_example_tracks": ["patent_law"]},
            {"field": "chapter_structure[] item shape", "status": "inconsistent_across_tracks",
             "description": ("At least 3 distinct conventions found across the 6 standard-convention "
                              "tracks sampled: flat {section_ar, first_article, last_article}; "
                              "{label_ar, title_ar, articles} with a free-text range string; and a "
                              "nested chapters/sections form. Not machine-uniform; treat as display "
                              "prose, not a reliable programmatic article-range index."),
             "example_tracks": ["patent_law/basic_law_of_governance (flat section_ar form)",
                                 "income_tax_law/traffic_law (label_ar+articles-string form)",
                                 "zakat_law/social_insurance_law (nested chapters/sections form)"]},
            {"field": "decree_transitional_provisions_ar", "status": "track_specific",
             "description": "Verbatim transitional/enactment-decree provisions distinct from the law's own articles.",
             "example_tracks": ["social_insurance_law"]},
            {"field": "provenance", "status": "track_specific",
             "description": "Structured source-access metadata (portal URL, access method, source PDF sha256/pages/extraction method).",
             "example_tracks": ["basic_law_of_governance"]},
            {"field": "articles.<key>.original_<HHHHh>_text", "status": "track_specific",
             "description": "Preserves pre-amendment article wording; field NAME encodes the track's founding Hijri year.",
             "example_tracks": ["basic_law_of_governance (original_1412h_text)",
                                "income_tax_law/patent_law (original_1425h_text)",
                                "traffic_law (original_1428h_text)", "zakat_law (original_1445h_text)"],
             "counter_example_tracks": ["social_insurance_law", "civil_transactions_law"]},
            {"field": "articles.<key>.verification_tier", "status": "track_specific",
             "description": "Per-article verification-confidence tier distinct from the track-wide official_text_status.",
             "example_tracks": ["traffic_law (pioneered the per-article split)", "basic_law_of_governance (Article 5 only)"]},
            {"field": "articles.<key>.cross_verified_against_wipo_lex", "status": "track_specific",
             "description": "Per-article boolean flag for WIPO Lex spot-checking.",
             "example_tracks": ["basic_law_of_governance"]},
            {"field": "articles.<key>.title_ar", "status": "track_specific",
             "description": "A named-section title at the article level, distinct from section_ar.",
             "example_tracks": ["zakat_law"]},
            {"field": "(entire legacy schema variant)", "status": "legacy_convention",
             "description": ("civil_transactions_law is this corpus's earliest track and predates the "
                              "standard convention entirely: uses law_key/boundaries/moj_cross_check/"
                              "capture_method instead of consolidated_amended_law/verification_methodology_note/"
                              "chapter_structure, and article records carry only text+section_context "
                              "(no legal_status_ar/history/status)."),
             "example_tracks": ["civil_transactions_law"]},
        ],
        "verified_record_schema": [
            {"field": "verification_tier", "status": "track_specific",
             "example_tracks": ["traffic_law", "basic_law_of_governance"]},
            {"field": "cross_verified_against_wipo_lex", "status": "track_specific",
             "example_tracks": ["basic_law_of_governance"]},
            {"field": "original_<HHHHh>_text", "status": "track_specific",
             "example_tracks": ["basic_law_of_governance", "income_tax_law", "patent_law", "traffic_law", "zakat_law"],
             "counter_example_tracks": ["social_insurance_law", "civil_transactions_law"]},
            {"field": "title_ar", "status": "track_specific", "example_tracks": ["zakat_law"]},
            {"field": "(entire legacy schema variant)", "status": "legacy_convention",
             "description": ("civil_transactions_law verified records use section_context_ar/"
                              "verification_method/source_authority_ar/royal_decree in place of "
                              "section_ar/verification_status/is_amended/is_repealed/is_added/"
                              "legal_status_ar/amendment_history."),
             "example_tracks": ["civil_transactions_law"]},
        ],
        "llm_ready_layer_schema": [
            {"field": "title_en", "status": "optional",
             "example_tracks": ["civil_transactions_law", "income_tax_law"],
             "counter_example_tracks": ["patent_law", "zakat_law"]},
            {"field": "consolidated_amended_law, status_counts", "status": "convention_specific",
             "description": "Present in the standard-convention envelope, absent from the legacy civil envelope.",
             "example_tracks": ["income_tax_law", "patent_law", "zakat_law"]},
            {"field": "disclaimer_ar, source_verified_file, schema", "status": "legacy_convention",
             "description": "Present only in civil_transactions_law's envelope; no equivalent field exists "
                             "in the standard convention (schema points to a per-track draft-07 schema "
                             "under schemas/, unique to this track).",
             "example_tracks": ["civil_transactions_law"]},
            {"field": "records[].section_context_ar vs records[].section_ar", "status": "legacy_convention",
             "description": "civil_transactions_law records use section_context_ar and omit "
                             "is_added/is_amended/is_repealed/is_mukarrar/legal_status_ar entirely.",
             "example_tracks": ["civil_transactions_law"]},
            {"field": "source_trust.royal_decree", "status": "legacy_convention",
             "example_tracks": ["civil_transactions_law"]},
            {"field": "source_trust.legal_status_ar, source_trust.verification_status", "status": "convention_specific",
             "example_tracks": ["income_tax_law", "patent_law", "zakat_law"]},
        ],
        "unified_index_record_schema": [
            {"field": "law_id, llm_title_ar, retrieval_title_ar, article_path", "status": "nullable",
             "description": "Always present as a key (generator always writes it) but the value may be "
                             "null if the underlying source layer record omitted it.",
             "example_tracks": []},
        ],
        "corpus_registry_track_schema": [
            {"field": "display_name_en", "status": "optional", "coverage": "120/123 tracks"},
            {"field": "official_text_status", "status": "optional", "coverage": "119/123 tracks",
             "description": "Null/absent on the 4 earliest tracks predating this convention.",
             "example_tracks": ["companies_law", "implementing_regulations_general",
                                 "implementing_regulations_listed_joint_stock",
                                 "implementing_regulations_arabic_program_closure"]},
            {"field": "source_authority", "status": "optional", "coverage": "121/123 tracks"},
            {"field": "source_url", "status": "optional", "coverage": "3/123 tracks"},
            {"field": "publication_date_hijri, publication_date_gregorian", "status": "optional", "coverage": "3/123 tracks"},
            {"field": "manifest_paths", "status": "optional", "coverage": "4/123 tracks",
             "example_tracks": ["companies_law (and its 3 sibling implementing-regulation/closure-audit tracks)"]},
            {"field": "boundaries.specialized_scope", "status": "track_specific",
             "description": "A free-text string key inside the otherwise-boolean boundaries object.",
             "example_tracks": ["implementing_regulations_listed_joint_stock"]},
        ],
        "verification_tier_entry_schema": [
            {"field": "(all fields)", "status": "always_present",
             "description": "Fully mechanically derived; no optional fields."},
        ],
        "supersession_edge_schema": [
            {"field": "successor_in_corpus", "status": "conditional",
             "description": "Present only when relation='superseded_by' (1 of 44 current edges).",
             "example_tracks": ["copyright_law"]},
        ],
        "cross_reference_edge_schema": [
            {"field": "target_track_id, target_article_number, target_law_name_raw", "status": "nullable",
             "description": "null for intra_law citations or unresolved inter_law law names."},
        ],
        "glossary_term_schema": [
            {"field": "(multiple definition entries per term)", "status": "structural_note",
             "description": "92 of 696 terms in the current corpus have more than one definition entry "
                             "(one per defining track) rather than a single merged definition.",
             "example_tracks": ["environmental_law + mining_investment_law both define 'إعادة التأهيل'"]},
        ],
    }


# ---------------------------------------------------------------------------
# Self-validation: re-read real corpus files and confirm every field this
# manifest calls "always present" (required) genuinely is present. Fails
# loudly (raises SystemExit) on any mismatch.
# ---------------------------------------------------------------------------

def _load_json(rel_path):
    with open(os.path.join(ROOT, rel_path), "r", encoding="utf-8") as f:
        return json.load(f)


def _load_jsonl_first(rel_path):
    with open(os.path.join(ROOT, rel_path), "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                return json.loads(line)
    raise ValueError(f"{rel_path}: no non-empty lines")


def _check_required(errors, context, obj, required_fields):
    if not isinstance(obj, dict):
        errors.append(f"{context}: expected an object, got {type(obj).__name__}")
        return
    missing = [f for f in required_fields if f not in obj]
    if missing:
        errors.append(f"{context}: MISSING required field(s) {missing}")


def self_validate(manifest):
    """Re-reads real corpus files sampled while building this manifest and
    confirms the 'always present' (required) claims genuinely hold. Also
    does a basic JSON-Schema-syntax structural check on every schema entry.
    Raises SystemExit with a full report on any failure."""
    errors = []

    # --- structural syntax check: every schema must at least declare
    # $schema/type-or-oneOf and, where it declares `required`, every name in
    # `required` must also appear in `properties` (directly or via a $defs
    # variant selected by oneOf). We keep this check intentionally light —
    # jsonschema (if installed) does the deep structural validation in
    # scripts/validate_corpus_schema_manifest.py.
    for name, schema in manifest["schemas"].items():
        if "$schema" not in schema:
            errors.append(f"schema '{name}': missing $schema")
        if not any(k in schema for k in ("type", "oneOf", "anyOf")):
            errors.append(f"schema '{name}': missing 'type', 'oneOf', and 'anyOf'")

    # --- official_source_schema: standard-convention required fields ---
    std_required = manifest["schemas"]["official_source_schema"]["$defs"]["OfficialSourceStandard"]["required"]
    for track, path in OFFICIAL_SOURCE_SAMPLES_STANDARD.items():
        doc = _load_json(path)
        _check_required(errors, f"official_source_schema/standard/{track}", doc, std_required)
        art_required = manifest["schemas"]["official_source_schema"]["$defs"]["OfficialSourceArticleRecordStandard"]["required"]
        first_art_key = next(iter(doc.get("articles", {})), None)
        if first_art_key is not None:
            _check_required(errors, f"official_source_schema/standard/{track}/articles[{first_art_key}]",
                             doc["articles"][first_art_key], art_required)

    legacy_required = manifest["schemas"]["official_source_schema"]["$defs"]["OfficialSourceLegacyCivil"]["required"]
    for track, path in OFFICIAL_SOURCE_SAMPLES_LEGACY.items():
        doc = _load_json(path)
        _check_required(errors, f"official_source_schema/legacy/{track}", doc, legacy_required)

    # --- verified_record_schema ---
    vr_std_required = manifest["schemas"]["verified_record_schema"]["$defs"]["VerifiedRecordStandard"]["required"]
    for track, path in VERIFIED_RECORD_SAMPLES_STANDARD.items():
        rec = _load_jsonl_first(path)
        _check_required(errors, f"verified_record_schema/standard/{track}", rec, vr_std_required)

    vr_legacy_required = manifest["schemas"]["verified_record_schema"]["$defs"]["VerifiedRecordLegacyCivil"]["required"]
    for track, path in VERIFIED_RECORD_SAMPLES_LEGACY.items():
        rec = _load_jsonl_first(path)
        _check_required(errors, f"verified_record_schema/legacy/{track}", rec, vr_legacy_required)

    # --- llm_ready_layer_schema ---
    defs = manifest["schemas"]["llm_ready_layer_schema"]["$defs"]
    env_std_required = defs["LlmReadyEnvelopeStandard"]["required"]
    rec_std_required = defs["LlmReadyRecordStandard"]["required"]
    trust_required = defs["SourceTrust"]["required"]
    for track, path in LLM_READY_SAMPLES_STANDARD.items():
        env = _load_json(path)
        _check_required(errors, f"llm_ready_layer_schema/standard/{track}/envelope", env, env_std_required)
        if env.get("records"):
            _check_required(errors, f"llm_ready_layer_schema/standard/{track}/records[0]", env["records"][0], rec_std_required)
            _check_required(errors, f"llm_ready_layer_schema/standard/{track}/records[0].source_trust",
                             env["records"][0].get("source_trust", {}), trust_required)

    env_legacy_required = defs["LlmReadyEnvelopeLegacyCivil"]["required"]
    rec_legacy_required = defs["LlmReadyRecordLegacyCivil"]["required"]
    for track, path in LLM_READY_SAMPLES_LEGACY.items():
        env = _load_json(path)
        _check_required(errors, f"llm_ready_layer_schema/legacy/{track}/envelope", env, env_legacy_required)
        if env.get("records"):
            _check_required(errors, f"llm_ready_layer_schema/legacy/{track}/records[0]", env["records"][0], rec_legacy_required)

    # --- unified_index_record_schema ---
    ui_required = manifest["schemas"]["unified_index_record_schema"]["required"]
    ui_rec = _load_jsonl_first(UNIFIED_INDEX_SAMPLE)
    _check_required(errors, "unified_index_record_schema/sample[0]", ui_rec, ui_required)

    # --- corpus_registry_track_schema ---
    reg_required = manifest["schemas"]["corpus_registry_track_schema"]["required"]
    registry = _load_json(REGISTRY_SAMPLE)
    if registry.get("tracks"):
        for t in registry["tracks"][:5]:
            _check_required(errors, f"corpus_registry_track_schema/{t.get('track_id')}", t, reg_required)

    # --- verification_tier_entry_schema ---
    vt_required = manifest["schemas"]["verification_tier_entry_schema"]["required"]
    vt = _load_json(VERIFICATION_TIERS_SAMPLE)
    for entry in vt.get("tracks", [])[:5]:
        _check_required(errors, f"verification_tier_entry_schema/{entry.get('track_id')}", entry, vt_required)

    # --- supersession_edge_schema ---
    se_required = manifest["schemas"]["supersession_edge_schema"]["required"]
    sg = _load_json(SUPERSESSION_GRAPH_SAMPLE)
    for edge in sg.get("edges", [])[:5]:
        _check_required(errors, f"supersession_edge_schema/{edge.get('from_track_id')}", edge, se_required)

    # --- cross_reference_edge_schema ---
    cr_required = manifest["schemas"]["cross_reference_edge_schema"]["required"]
    crg = _load_json(CROSS_REFERENCE_GRAPH_SAMPLE)
    for ref in crg.get("references", [])[:5]:
        _check_required(errors, f"cross_reference_edge_schema/{ref.get('source_record_id')}", ref, cr_required)

    # --- glossary_term_schema ---
    gt_required = manifest["schemas"]["glossary_term_schema"]["required"]
    gl = _load_json(GLOSSARY_SAMPLE)
    terms = gl.get("terms", {})
    for i, (term, defs_list) in enumerate(terms.items()):
        if i >= 5:
            break
        for d in defs_list:
            _check_required(errors, f"glossary_term_schema/{term}", d, gt_required)

    # --- the four layers added after this manifest was first written -------------
    # A curated manifest describes what someone remembered to describe. Four
    # corpus-wide layers were built after this file and never joined it, and
    # nothing said so: the manifest called itself authoritative over "every
    # distinct document type" while describing seven of eleven derived layers.
    # They are validated against real rows here like every other schema.
    for name, path, is_jsonl in (
            ("chunking_layer_chunk_schema", CHUNKING_LAYER_SAMPLE, True),
            ("caveat_layer_record_schema", CAVEAT_LAYER_SAMPLE, True),
            ("amendment_timeline_record_schema", AMENDMENT_TIMELINE_SAMPLE, True),
    ):
        req = manifest["schemas"][name]["required"]
        rec = _load_jsonl_first(path)
        _check_required(errors, "%s/first_row" % name, rec, req)
        extra = sorted(set(rec) - set(manifest["schemas"][name]["properties"]))
        if extra:
            errors.append("%s: real rows carry undocumented field(s) %s" % (name, extra))

    rq = _load_json(RETRIEVAL_EVAL_QUERIES_SAMPLE)
    rq_required = manifest["schemas"]["retrieval_eval_query_schema"]["required"]
    for q in (rq.get("queries") or [])[:5]:
        _check_required(errors, "retrieval_eval_query_schema/%s" % q.get("query_id"),
                        q, rq_required)
    rr = _load_json(RETRIEVAL_EVAL_RESULTS_SAMPLE)
    rr_required = manifest["schemas"]["retrieval_eval_result_schema"]["required"]
    for q in (rr.get("per_query") or [])[:5]:
        _check_required(errors, "retrieval_eval_result_schema/%s" % q.get("query_id"),
                        q, rr_required)

    fm_required = manifest["schemas"]["freshness_manifest_track_schema"]["required"]
    fm = _load_json(FRESHNESS_MANIFEST_SAMPLE)
    for t in (fm.get("tracks") or [])[:5]:
        _check_required(errors, "freshness_manifest_track_schema/%s" % t.get("track_id"),
                        t, fm_required)
        extra = sorted(set(t) - set(
            manifest["schemas"]["freshness_manifest_track_schema"]["properties"]))
        if extra:
            errors.append("freshness_manifest_track_schema: undocumented field(s) %s" % extra)

    # --- and the check that keeps the twelfth layer from repeating the eleventh --
    # Every data/corpus_*/ directory the corpus publishes must have a schema
    # describing it. This is the one thing the manifest could not have told you
    # before: it enumerated what it covered and never what it MISSED.
    described = set()
    for schema in manifest["schemas"].values():
        described.add((schema.get("description") or "").split(" ")[0].rstrip(","))
    for d in sorted(glob.glob(os.path.join(ROOT, "data", "corpus_*"))):
        if not os.path.isdir(d):
            continue
        payloads = [f for f in sorted(os.listdir(d))
                    if f.endswith((".json", ".jsonl")) and not f.endswith("_summary.json")]
        for f in payloads:
            rel = "data/%s/%s" % (os.path.basename(d), f)
            if not any(rel in (sch.get("description") or "")
                       for sch in manifest["schemas"].values()):
                errors.append(
                    "no schema in this manifest names %s — a published layer that the "
                    "manifest does not describe makes its 'every document type' claim false"
                    % rel)

    if errors:
        report = "\n".join(f"  - {e}" for e in errors)
        raise SystemExit(
            "gen_corpus_schema_manifest: SELF-VALIDATION FAILED — the manifest's 'required' "
            f"(always-present) claims do not match real corpus files:\n{report}\n"
            "Fix the schema (or the sample set) before trusting this manifest."
        )

    return len(errors)


def corpus_wide_coverage_check(manifest):
    """Beyond the curated sample, sweep EVERY real official_source.json,
    verified/*.jsonl, and _arabic_legal_llm/*.json envelope in the whole
    corpus and report what fraction structurally validates against the
    corresponding schema above. This is intentionally honest about scope:
    the three per-track schemas were designed from a ~8-10-track sample
    (per this task's own instructions), not from reading all 123 tracks in
    depth, so this check tells an integrator exactly how far the modeled
    conventions generalize — rather than silently implying full coverage.
    Does not raise; returns a results dict for inclusion in the manifest.
    """
    try:
        import jsonschema  # noqa: local, optional dependency
    except ImportError:
        return {"skipped": True, "reason": "jsonschema not installed in this environment"}

    import glob as _glob

    def sweep_json(schema, files):
        ok, total = 0, 0
        for f in files:
            total += 1
            try:
                inst = _load_json(os.path.relpath(f, ROOT))
                jsonschema.validate(instance=inst, schema=schema)
                ok += 1
            except Exception:
                pass
        return ok, total

    def sweep_jsonl_first_line(schema, files):
        ok, total = 0, 0
        for f in files:
            total += 1
            try:
                rec = _load_jsonl_first(os.path.relpath(f, ROOT))
                jsonschema.validate(instance=rec, schema=schema)
                ok += 1
            except Exception:
                pass
        return ok, total

    def sweep_envelope(schema, files):
        ok, total = 0, 0
        for f in files:
            try:
                env = _load_json(os.path.relpath(f, ROOT))
            except Exception:
                continue
            if not isinstance(env, dict) or "records" not in env:
                continue
            total += 1
            try:
                jsonschema.validate(instance=env, schema=schema)
                ok += 1
            except Exception:
                pass
        return ok, total

    os_files = sorted(set(_glob.glob(os.path.join(ROOT, "sources", "*", "*", "official_source", "*.json"))))
    vr_files = sorted(set(_glob.glob(os.path.join(ROOT, "sources", "*", "*", "verified", "*_verified_records.jsonl"))))
    llm_files = sorted(set(_glob.glob(os.path.join(ROOT, "data", "*_arabic_legal_llm", "*.json"))))

    os_ok, os_total = sweep_json(manifest["schemas"]["official_source_schema"], os_files)
    vr_ok, vr_total = sweep_jsonl_first_line(manifest["schemas"]["verified_record_schema"], vr_files)
    llm_ok, llm_total = sweep_envelope(manifest["schemas"]["llm_ready_layer_schema"], llm_files)

    return {
        "skipped": False,
        "method": (
            "For each schema, every real file of that kind anywhere in the corpus (not just the "
            "curated sample) is loaded and validated with the installed `jsonschema` library "
            "(Draft202012Validator semantics). unified_index_record_schema, "
            "corpus_registry_track_schema, verification_tier_entry_schema, supersession_edge_schema, "
            "cross_reference_edge_schema, and glossary_term_schema are NOT swept here because they "
            "are each produced by a single generator script this task's author read in full — their "
            "coverage is 100% by construction, unlike the three per-track layers below which are "
            "authored by 100+ separate per-track generator scripts."
        ),
        "official_source_schema": {"matching": os_ok, "total": os_total,
            "note": ("A permissive MINIMAL fallback branch (article_count + articles only) is why "
                      "this number is high despite official_source.json being the least standardized "
                      "layer in the corpus — see this schema's own `description` for named examples "
                      "of further conventions accepted by MINIMAL but not deeply modeled. The 1-2 "
                      "files (if any) that still fail even MINIMAL are non-article annex/table "
                      "documents (e.g. labor_annex2/labor_annex5) that are not article-based laws at "
                      "all and are out of scope for this schema.")},
        "verified_record_schema": {"matching": vr_ok, "total": vr_total},
        "llm_ready_layer_schema": {"matching": llm_ok, "total": llm_total},
    }


def main() -> int:
    schemas = {name: builder() for name, builder in SCHEMA_BUILDERS.items()}

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_by": GENERATED_BY,
        "dialect": DIALECT,
        "corpus_repository": CORPUS_REPOSITORY,
        "corpus_branch": CORPUS_BRANCH,
        "description": (
            "Authoritative, machine-readable manifest of JSON Schemas describing every distinct "
            "document type used across this corpus (123+ tracks), so an external integrator (e.g. a "
            "RAG application) does not have to reverse-engineer the data model from individual track "
            "files. Read-only, descriptive survey layer; does not alter any of the documents it "
            "describes. See reports/schema_manifest/SCHEMA_MANIFEST_GUIDE_EN.md for a human-readable "
            "companion guide and quick-start."
        ),
        "read_only_derived_layer": True,
        "not_legal_advice": True,
        "sample_files_read": {
            "official_source_standard": OFFICIAL_SOURCE_SAMPLES_STANDARD,
            "official_source_legacy": OFFICIAL_SOURCE_SAMPLES_LEGACY,
            "verified_record_standard": VERIFIED_RECORD_SAMPLES_STANDARD,
            "verified_record_legacy": VERIFIED_RECORD_SAMPLES_LEGACY,
            "llm_ready_standard": LLM_READY_SAMPLES_STANDARD,
            "llm_ready_legacy": LLM_READY_SAMPLES_LEGACY,
            "unified_index": UNIFIED_INDEX_SAMPLE,
            "corpus_registry": REGISTRY_SAMPLE,
            "verification_tiers": VERIFICATION_TIERS_SAMPLE,
            "supersession_graph": SUPERSESSION_GRAPH_SAMPLE,
            "cross_reference_graph": CROSS_REFERENCE_GRAPH_SAMPLE,
            "glossary": GLOSSARY_SAMPLE,
        },
        "schemas": schemas,
        "field_provenance_notes": field_provenance_notes(),
    }

    self_validate(manifest)
    manifest["corpus_wide_coverage_check"] = corpus_wide_coverage_check(manifest)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write("\n")

    print(f"Wrote {os.path.relpath(OUT_PATH, ROOT)}")
    print(f"  schemas: {len(schemas)}")
    print(f"  self-validation: PASS (0 mismatches across all sampled real files)")
    cov = manifest["corpus_wide_coverage_check"]
    if not cov.get("skipped"):
        for key in ("official_source_schema", "verified_record_schema", "llm_ready_layer_schema"):
            c = cov[key]
            print(f"  corpus-wide coverage [{key}]: {c['matching']}/{c['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
