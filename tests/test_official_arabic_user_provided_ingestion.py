"""Official Arabic USER-PROVIDED text ingestion — tests.

A full user-provided Arabic text candidate for the Companies Law (Royal Decree M/132) has
been ingested and segmented into exactly 281 article records, each hashed. It is
`ingested_unverified` — NOT verified against Umm Al-Qura or the Bureau of Experts. No
derived (English/Chinese/Arabic) LLM layer is changed.
"""

import glob
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "official_arabic_article.schema.json")
OA_DIR = os.path.join(ROOT, "data", "official_arabic")
STATUS = os.path.join(OA_DIR, "ingestion_status.json")
RAW = os.path.join(ROOT, "inputs", "official_arabic_companies_law_m132_1443_user_provided.md")
RECORDS = os.path.join(OA_DIR, "companies_law_m132_1443_official_arabic_user_provided.json")
GEN = os.path.join(ROOT, "scripts", "ingest_official_arabic_user_provided_text.py")

TARGET = 281


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _arts():
    return _read(RECORDS)["articles"]


# -- source packet + generator ----------------------------------------------
def test_raw_source_packet_exists():
    assert os.path.exists(RAW)
    assert os.path.getsize(RAW) > 10000  # the full packet, not a stub


def test_structured_candidate_file_exists():
    assert os.path.exists(RECORDS)


def test_generator_is_byte_stable():
    before = open(RECORDS, "rb").read()
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    after = open(RECORDS, "rb").read()
    assert before == after, "generator output is not byte-stable / idempotent"


# -- exactly 281 records, correct range + titles -----------------------------
def test_exactly_281_records():
    assert len(_arts()) == TARGET


def test_article_numbers_1_to_281_in_order():
    assert [a["article_number"] for a in _arts()] == list(range(1, TARGET + 1))


def test_article_1_title_is_definitions():
    assert _arts()[0]["article_title_ar"] == "التعريفات"
    assert _arts()[0]["article_number"] == 1


def test_article_281_title_is_law_enforcement():
    assert _arts()[-1]["article_title_ar"] == "نفاذ النظام"
    assert _arts()[-1]["article_number"] == 281


def test_no_empty_official_text():
    for a in _arts():
        assert a["official_text_ar"].strip(), a["article_number"]


# -- nothing verified; hashes correct ----------------------------------------
def test_no_verified_status_anywhere():
    doc = _read(RECORDS)
    assert doc["article_by_article_verified"] is False
    assert doc["verification_status"] == "ingested_unverified"
    assert doc["articles_verified"] == 0
    for a in _arts():
        assert a["verification_status"] == "ingested_unverified", a["article_number"]
        assert a["verification_status"] != "verified_against_official_gazette", a["article_number"]
        assert a["official_gazette_name"] == "pending_verification", a["article_number"]


def test_all_hashes_correct():
    for a in _arts():
        h = hashlib.sha256(a["official_text_ar"].encode("utf-8")).hexdigest()
        assert a["text_hash_sha256"] == h, a["article_number"]


def test_every_record_schema_valid():
    schema = _read(SCHEMA)
    try:
        import jsonschema
        v = jsonschema.Draft7Validator(schema)
        for a in _arts():
            errs = [e.message for e in v.iter_errors(a)]
            assert not errs, (a["article_number"], errs)
    except ImportError:
        for a in _arts():
            for k in schema["required"]:
                assert k in a, (a["article_number"], k)


def test_records_carry_decree_metadata():
    for a in _arts():
        assert a["royal_decree_number"] == "م/132", a["article_number"]
        assert a["royal_decree_date_hijri"] == "1443/12/01", a["article_number"]
        assert a["extraction_method"] == "direct_user_provided_markdown_packet", a["article_number"]
        assert a["source_file"] == "inputs/official_arabic_companies_law_m132_1443_user_provided.md"
        assert "not yet verified" in a["notes"].lower() or "not" in a["notes"].lower()


# -- ingestion_status updated but still unverified ---------------------------
def test_ingestion_status_updated_but_not_verified():
    st = _read(STATUS)
    assert st["official_arabic_text_status"] == "user_provided_source_ingested"
    assert st["verification_status"] == "ingested_unverified"
    assert st["article_by_article_verified"] is False
    assert st["articles_ingested"] == TARGET
    assert st["articles_verified"] == 0
    assert "not_official" in st["current_arabic_summary_status"]
    assert st["source_url_or_file_reference"] == "inputs/official_arabic_companies_law_m132_1443_user_provided.md"


# -- derived layers unchanged ------------------------------------------------
def test_english_legal_llm_unchanged_8_files_87_records():
    d = os.path.join(ROOT, "data", "english_legal_llm")
    files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(d, "*_en_legal_llm.json")))
    assert files == ["book1_en_legal_llm.json", "book2_en_legal_llm.json", "book3_en_legal_llm.json",
                     "book4_section1_en_legal_llm.json", "book4_section2_en_legal_llm.json",
                     "book4_section3_en_legal_llm.json", "book4_section4_en_legal_llm.json",
                     "book4_section5_en_legal_llm.json"], files
    total = sum(len(_read(p)["records"]) for p in glob.glob(os.path.join(d, "*_en_legal_llm.json")))
    assert total == 87, total


def test_chinese_legal_llm_unchanged_5_files_23_records():
    d = os.path.join(ROOT, "data", "chinese_legal_llm")
    files = glob.glob(os.path.join(d, "*_zh_legal_llm.json"))
    assert len(files) == 5, files
    total = sum(len(_read(p)["records"]) for p in files)
    assert total == 23, total


def test_arabic_legal_llm_not_relabeled_official():
    for p in glob.glob(os.path.join(ROOT, "data", "arabic_legal_llm", "*_ar_legal_llm.json")):
        blob = open(p, encoding="utf-8").read().lower()
        assert "official_text_ar" not in blob, p
        assert "verified_against_official_gazette" not in blob, p


def test_official_english_reference_unchanged():
    ref = os.path.join(ROOT, "data", "english_reference")
    for fname, exp in (("book1_en_reference.json", list(range(1, 35))),
                       ("book2_en_reference.json", list(range(35, 51))),
                       ("book3_en_reference.json", list(range(51, 58)))):
        doc = _read(os.path.join(ref, fname))
        assert [r["article_number"] for r in doc["records"]] == exp, fname


def test_ingestion_validator_passes():
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "validate_official_arabic_ingestion.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
