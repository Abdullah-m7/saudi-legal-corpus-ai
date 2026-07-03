"""Official English guidance source — intake (source asset + planning only).

Asserts the intake metadata/docs exist with the correct trust posture and that NO
English Legal LLM layer/records have been created and NO Arabic/Chinese legal
content changed.
"""

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META = os.path.join(ROOT, "data", "metadata", "official_english_source.json")
DOCS = os.path.join(ROOT, "docs", "official_english_source")
PDF_REL = "inputs/companies_law_official_english_guidance.pdf"


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


# -- metadata ---------------------------------------------------------------
def test_metadata_exists():
    assert os.path.exists(META)


def test_metadata_trust_fields():
    m = _read(META)
    assert m["source_type"] == "official_guidance_translation"
    assert m["governing_text_language"] == "ar"
    assert m["source_language"] == "en"
    assert m["not_legal_advice"] is True


def test_metadata_source_authority_bureau_of_experts():
    m = _read(META)
    assert "Bureau of Experts" in m["source_authority"]


def test_metadata_source_file_path():
    m = _read(META)
    assert m["source_file"] == PDF_REL


def test_metadata_does_not_use_forbidden_labels():
    m = _read(META)
    assert m["source_type"] not in (
        "governing_text", "binding_translation", "unofficial_translation")


# -- source PDF -------------------------------------------------------------
def test_source_pdf_present():
    assert os.path.exists(os.path.join(ROOT, PDF_REL))


# -- docs -------------------------------------------------------------------
def test_source_provenance_doc_exists():
    assert os.path.exists(os.path.join(DOCS, "SOURCE_PROVENANCE.md"))


def test_alignment_plan_doc_exists():
    assert os.path.exists(os.path.join(DOCS, "ENGLISH_ALIGNMENT_PLAN.md"))


def test_layer_risks_doc_exists():
    assert os.path.exists(os.path.join(DOCS, "ENGLISH_LAYER_RISKS.md"))


def test_all_required_docs_exist():
    for name in ("README.md", "SOURCE_PROVENANCE.md", "ENGLISH_SOURCE_SCOPE.md",
                 "ENGLISH_ALIGNMENT_PLAN.md", "ENGLISH_LAYER_RISKS.md"):
        assert os.path.exists(os.path.join(DOCS, name)), name


# -- no English layer yet ---------------------------------------------------
def test_no_english_llm_records_yet():
    # English Legal LLM layer started (Book Four Section 1 pilot); only that file may exist.
    _elf = glob.glob(os.path.join(ROOT, "data", "english_legal_llm", "*_en_legal_llm.json"))
    assert set(os.path.basename(p) for p in _elf) <= {"book1_en_legal_llm.json", "book2_en_legal_llm.json", "book3_en_legal_llm.json", "book4_section1_en_legal_llm.json", "book4_section2_en_legal_llm.json", "book4_section3_en_legal_llm.json", "book4_section4_en_legal_llm.json", "book4_section5_en_legal_llm.json"}, _elf
    stray = glob.glob(os.path.join(ROOT, "data", "**", "*_en_legal_llm.json"),
                      recursive=True)
    assert set(os.path.basename(p) for p in stray) <= {"book1_en_legal_llm.json", "book2_en_legal_llm.json", "book3_en_legal_llm.json", "book4_section1_en_legal_llm.json", "book4_section2_en_legal_llm.json", "book4_section3_en_legal_llm.json", "book4_section4_en_legal_llm.json", "book4_section5_en_legal_llm.json"}, stray
    m = _read(META)
    assert m["english_llm_layer_created"] is False
    assert m["english_per_article_records_created"] is False


# -- existing Arabic/Chinese legal content untouched ------------------------
def test_arabic_and_chinese_article_files_intact():
    checks = [
        ("book1_articles_001_034.json", list(range(1, 35))),
        ("book2_articles_035_050.json", list(range(35, 51))),
        ("book3_articles_051_057.json", list(range(51, 58))),
    ]
    for fname, expected in checks:
        doc = _read(os.path.join(ROOT, "data", "articles", fname))
        nums = [a["article_number"] for a in doc["articles"]]
        assert nums == expected, fname
        # Every article still carries both Arabic summary and Chinese translation.
        for a in doc["articles"]:
            assert a["arabic_reference_summary"].strip(), (fname, a["article_number"])
            assert a["chinese_translation"].strip(), (fname, a["article_number"])


def test_book4_provisions_intact():
    doc = _read(os.path.join(ROOT, "data", "articles", "book4_provisions_058_066.json"))
    assert [p["source_article_numbers"] for p in doc["provisions"]] == [[58], [59], [60], [66]]
    for p in doc["provisions"]:
        assert p["chinese_translation"].strip(), p["source_article_numbers"]


# -- no overclaim wording in metadata ---------------------------------------
def test_metadata_no_overclaim():
    blob = open(META, encoding="utf-8").read().lower()
    for phrase in ('"governing_text_language": "en"',
                   "english is binding", "english text is binding",
                   "english is the governing", "binding english translation",
                   "verified translation"):
        assert phrase not in blob, phrase


# -- validator script passes ------------------------------------------------
def test_validator_script_passes():
    import subprocess
    import sys
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "validate_official_english_source.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
