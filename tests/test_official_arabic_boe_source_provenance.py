"""Official Arabic BOE source-provenance/status correction tests (provenance only).

Documents the owner-provided Bureau of Experts Arabic text + scanned PDF packet as the controlling
official source packet, with OCR artifacts as supporting evidence only. Source-provenance
confidence is separated from article-by-article automated verification, which is NOT performed:
nothing is verified, promoted, or text-changed. Reads committed artifacts (no OCR engine needed).
"""

import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RPT = os.path.join(ROOT, "reports", "official_arabic_verification")
CORRECTION = os.path.join(RPT, "boe_official_source_provenance_correction.json")
PROV_DOC = os.path.join(ROOT, "docs", "official_arabic_text",
                        "BOE_OFFICIAL_SOURCE_PROVENANCE_AR.md")
INGEST = os.path.join(ROOT, "data", "official_arabic", "ingestion_status.json")
PROVENANCE = os.path.join(ROOT, "data", "metadata", "source_provenance.json")
CAND = os.path.join(ROOT, "data", "official_arabic",
                    "companies_law_m132_1443_official_arabic_user_provided.json")

AUTHORITY_AR = "هيئة الخبراء بمجلس الوزراء"
TARGET = 281


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def test_outputs_exist():
    assert os.path.exists(CORRECTION) and os.path.exists(PROV_DOC)


def test_correction_required_posture():
    c = _read(CORRECTION)
    assert c["source_authority"] == "Bureau of Experts at the Council of Ministers"
    assert c["source_authority_ar"] == AUTHORITY_AR
    assert c["text_source_status"] == "owner_provided_from_official_boe_source"
    assert c["pdf_source_status"] == "owner_provided_from_official_boe_source"
    assert c["controlling_source_packet"] == "owner_provided_boe_text_plus_pdf_packet"
    assert c["ocr_role"] == "supporting_artifact_only_not_controlling_gate"
    assert c["direct_automated_capture_status"] == "blocked_or_unsuitable"
    assert c["article_count"] == TARGET
    assert c["candidate_text_changed"] is False
    assert c["no_legal_text_changed"] is True
    assert c["no_article_promoted_by_ocr"] is True


def test_correction_nothing_verified():
    c = _read(CORRECTION)
    assert c.get("verified_by_ocr", False) is False
    assert c.get("verified_against_official_gazette", False) is False
    assert c["retained_ingestion_axis_values"]["article_by_article_verified"] is False
    assert c["retained_ingestion_axis_values"]["articles_verified"] == 0


def test_provenance_doc_mentions_authority_and_supporting_role():
    doc = open(PROV_DOC, encoding="utf-8").read()
    assert AUTHORITY_AR in doc
    assert "Bureau of Experts" in doc
    assert "supporting" in doc
    assert "281" in doc
    assert "not legal advice" in doc.lower()


def test_ingestion_status_boe_block():
    st = _read(INGEST)
    boe = st["boe_source_provenance"]
    assert boe["source_authority_ar"] == AUTHORITY_AR
    assert "Bureau of Experts" in boe["source_authority"]
    assert boe["text_source_status"] == "owner_provided_from_official_boe_source"
    assert boe["pdf_source_status"] == "owner_provided_from_official_boe_source"
    assert boe["controlling_source_packet"] == "owner_provided_boe_text_plus_pdf_packet"
    assert boe["ocr_role"] == "supporting_artifact_only_not_controlling_gate"
    assert boe["direct_automated_capture_status"] == "blocked_or_unsuitable"
    assert boe["article_count"] == TARGET
    assert boe["candidate_text_changed"] is False
    assert boe["no_legal_text_changed"] is True
    assert boe["no_article_promoted_by_ocr"] is True
    assert boe["verified_by_ocr"] is False
    assert boe["manual_review_queue_is_controlling_gate"] is False


def test_ingestion_status_authority_wording_corrected():
    st = _read(INGEST)
    # generic-unverified wording removed; authority now names the BOE
    assert "user_provided_text_claimed_official" not in st["source_authority"]
    assert "Bureau of Experts" in st["source_authority"]


def test_ingestion_axis_fields_retained_and_accurate():
    # ingestion / automated-verification axis is unchanged and remains honest
    st = _read(INGEST)
    assert st["official_arabic_text_status"] == "user_provided_source_ingested"
    assert st["verification_status"] == "ingested_unverified"
    assert st["article_by_article_verified"] is False
    assert st["articles_verified"] == 0
    assert st["articles_ingested"] == TARGET


def test_source_provenance_metadata_boe_block():
    prov = _read(PROVENANCE)
    pboe = prov["official_arabic_foundation"]["boe_source_provenance"]
    assert pboe["source_authority_ar"] == AUTHORITY_AR
    assert pboe["ocr_role"] == "supporting_artifact_only_not_controlling_gate"
    assert pboe["article_by_article_verified"] is False
    # gazette-check posture preserved
    assert prov["official_text_status"]["checked_against_official_gazette"] is False


def test_candidate_untouched_and_text_hash_matches():
    c = _read(CAND)
    assert len(c["articles"]) == TARGET
    assert c["verification_status"] == "ingested_unverified"
    assert c["article_by_article_verified"] is False
    for a in c["articles"]:
        assert a["verification_status"] == "ingested_unverified"
    blob = "".join(a["official_text_ar"] for a in c["articles"])
    agg = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    recorded = _read(CORRECTION)["candidate_integrity"]["aggregate_official_text_ar_sha256"]
    assert agg == recorded, "candidate official_text_ar changed"


def test_manual_review_queue_present_but_not_controlling():
    q = _read(os.path.join(RPT, "manual_review_queue.json"))
    assert len(q["entries"]) == TARGET
    boe = _read(INGEST)["boe_source_provenance"]
    assert boe["manual_review_queue_is_controlling_gate"] is False


def test_no_record_marked_verified():
    c = _read(CAND)
    assert "verified_against_official_gazette" not in json.dumps(c["articles"], ensure_ascii=False)
    assert "verified_by_ocr" not in json.dumps(c["articles"], ensure_ascii=False)


def test_validator_passes():
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts",
                                      "validate_official_arabic_boe_source_provenance.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
