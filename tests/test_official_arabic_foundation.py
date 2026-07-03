"""Official Arabic text FOUNDATION — scaffold-stage tests.

Assert the official-Arabic architecture + verification workflow exist and that the repo
does NOT pretend the current Arabic summaries are official statutory text. No official
Arabic text is ingested or verified at this stage.
"""

import glob
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "official_arabic_article.schema.json")
OA_DIR = os.path.join(ROOT, "data", "official_arabic")
STATUS = os.path.join(OA_DIR, "ingestion_status.json")
DOCS = os.path.join(ROOT, "docs", "official_arabic_text")
PACKET_DOC = os.path.join(DOCS, "SOURCE_PACKET_REQUIREMENTS_AR.md")
PLAN_DOC = os.path.join(DOCS, "OFFICIAL_ARABIC_VERIFICATION_PLAN_AR.md")
PROVENANCE = os.path.join(ROOT, "data", "metadata", "source_provenance.json")
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "official_arabic_article_sample.json")

REQUIRED_PROVENANCE_FIELDS = [
    "official_arabic_text_status", "current_arabic_summary_status", "official_source_required",
    "verification_status", "article_by_article_verified", "source_document_type",
    "source_authority", "source_publication_reference", "source_url_or_file_reference",
    "extraction_method", "reviewer_notes",
]


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


# -- scaffold exists --------------------------------------------------------
def test_schema_exists():
    assert os.path.exists(SCHEMA)


def test_official_arabic_folder_and_manifest_exist():
    assert os.path.isdir(OA_DIR)
    assert os.path.exists(STATUS)


def test_source_packet_requirements_doc_exists():
    assert os.path.exists(PACKET_DOC)


def test_verification_plan_exists():
    plan = open(PLAN_DOC, encoding="utf-8").read()
    for phase in ("Phase A", "Phase B", "Phase C", "Phase D", "Phase E", "Phase F", "Phase G"):
        assert phase in plan, phase


# -- provenance fields present + honest --------------------------------------
def test_ingestion_status_has_all_provenance_fields():
    status = _read(STATUS)
    for f in REQUIRED_PROVENANCE_FIELDS:
        assert f in status, f


def test_official_arabic_text_status_is_explicit_and_not_ingested():
    status = _read(STATUS)
    assert status["official_arabic_text_status"] == "not_ingested"
    assert status["official_source_required"] is True


def test_current_arabic_summaries_not_marked_official():
    status = _read(STATUS)
    s = status["current_arabic_summary_status"]
    assert "not_official" in s, s
    assert s not in ("official", "official_statutory_text")


def test_no_premature_verification():
    status = _read(STATUS)
    assert status["article_by_article_verified"] is False
    assert status["articles_verified"] == 0
    assert status["articles_ingested"] == 0
    assert status["verification_status"] == "pending_official_source"
    assert status.get("articles", []) == []


def test_source_provenance_keeps_arabic_non_official():
    prov = _read(PROVENANCE)
    assert prov["official_text_status"]["checked_against_official_gazette"] is False
    oaf = prov["official_arabic_foundation"]
    assert oaf["official_arabic_text_status"] == "not_ingested"
    assert oaf["article_by_article_verified"] is False
    assert "not_official" in oaf["current_arabic_summary_status"]


# -- schema validates minimal sample; hash is correct -----------------------
def test_official_arabic_schema_validates_minimal_sample():
    schema = _read(SCHEMA)
    sample = _read(FIXTURE)
    try:
        import jsonschema
        errs = [e.message for e in jsonschema.Draft7Validator(schema).iter_errors(sample)]
        assert not errs, errs
    except ImportError:
        for k in schema["required"]:
            assert k in sample, k


def test_fixture_hash_matches_text_and_is_not_official():
    sample = _read(FIXTURE)
    h = hashlib.sha256(sample["official_text_ar"].encode("utf-8")).hexdigest()
    assert sample["text_hash_sha256"] == h
    # the fixture is explicitly not official and not verified
    assert sample["verification_status"] != "verified_against_official_gazette"
    assert "not official" in sample["official_text_ar"].lower()
    # and it lives under tests/fixtures, NOT in the data folder
    assert "fixtures" in FIXTURE and not os.path.exists(
        os.path.join(OA_DIR, "official_arabic_article_sample.json"))


def test_schema_forbids_additional_properties():
    schema = _read(SCHEMA)
    assert schema.get("additionalProperties") is False


def test_no_official_article_records_present_yet():
    # No file under data/official_arabic/ (other than the manifest) may carry official_text_ar.
    for path in glob.glob(os.path.join(OA_DIR, "*.json")):
        if os.path.basename(path) == "ingestion_status.json":
            continue
        blob = open(path, encoding="utf-8").read()
        assert "official_text_ar" not in blob, path


# -- no derived layer changed / claims premature verification ----------------
def test_chinese_legal_llm_unchanged_5_files_23_records():
    d = os.path.join(ROOT, "data", "chinese_legal_llm")
    files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(d, "*_zh_legal_llm.json")))
    assert files == ["book4_section1_zh_legal_llm.json",
                     "book4_section2_zh_legal_llm.json",
                     "book4_section3_zh_legal_llm.json",
                     "book4_section4_zh_legal_llm.json",
                     "book4_section5_zh_legal_llm.json"], files
    total = sum(len(_read(p)["records"]) for p in glob.glob(os.path.join(d, "*_zh_legal_llm.json")))
    assert total == 23, total


def test_english_legal_llm_unchanged_8_files_87_records():
    d = os.path.join(ROOT, "data", "english_legal_llm")
    files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(d, "*_en_legal_llm.json")))
    assert files == ["book1_en_legal_llm.json",
                     "book2_en_legal_llm.json",
                     "book3_en_legal_llm.json",
                     "book4_section1_en_legal_llm.json",
                     "book4_section2_en_legal_llm.json",
                     "book4_section3_en_legal_llm.json",
                     "book4_section4_en_legal_llm.json",
                     "book4_section5_en_legal_llm.json"], files
    total = sum(len(_read(p)["records"]) for p in glob.glob(os.path.join(d, "*_en_legal_llm.json")))
    assert total == 87, total


def test_arabic_legal_llm_layer_present_and_not_relabeled_official():
    d = os.path.join(ROOT, "data", "arabic_legal_llm")
    files = glob.glob(os.path.join(d, "*_ar_legal_llm.json"))
    assert files, "arabic legal llm layer should still exist"
    # none of the Arabic LLM records may claim to be official statutory text
    for p in files:
        blob = open(p, encoding="utf-8").read().lower()
        assert "official_text_ar" not in blob, p
        assert "verified_against_official_gazette" not in blob, p


def test_validator_script_passes():
    import subprocess
    import sys
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "validate_official_arabic_foundation.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
