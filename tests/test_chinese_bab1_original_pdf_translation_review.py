"""Chinese Bab 1 original-PDF translation review tests (source inventory only).

Ingests + reviews the original Bab 1 Chinese PDF for Articles 1-34, extracting its Chinese text and
classifying each article's meaning vs the official Arabic. Review/inventory stage ONLY — Chinese is
internal / non-official / non-binding (Arabic governs); NO Chinese LLM-ready records created. Reads
committed artifacts.
"""

import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "inputs", "chinese_translation_source_pdfs",
                   "saudi_companies_law_ar_zh_bab1_full.pdf")
EX = os.path.join(ROOT, "data", "chinese_translation_sources",
                  "bab1_zh_source_extracted_articles_001_034.json")
RV = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "bab1_original_pdf_translation_review.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "BAB1_ORIGINAL_PDF_TRANSLATION_REVIEW_AR.md")
GEN = os.path.join(ROOT, "scripts", "gen_chinese_bab1_original_pdf_translation_review.py")

TARGET = 34
COVERAGE = {"full_or_near_full_aligned", "mostly_aligned_but_condensed",
            "summary_needs_expansion", "materially_incomplete_needs_retranslation",
            "extraction_unclear_needs_manual_review"}


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def test_all_artifacts_exist():
    assert os.path.exists(PDF) and os.path.exists(EX)
    assert os.path.exists(RV) and os.path.exists(MD)


def test_extracted_34_articles_1_to_34():
    ex = _read(EX)
    assert ex["article_count"] == TARGET
    assert ex["article_range"] == [1, TARGET]
    assert [r["article_number"] for r in ex["records"]] == list(range(1, TARGET + 1))
    for r in ex["records"]:
        assert r["chinese_text"].strip()
        assert r["chinese_heading"].strip()


def test_extracted_trust_posture():
    ex = _read(EX)
    assert ex["source_language"] == "zh"
    assert ex["governing_text_language"] == "ar"
    assert ex["official_translation"] is False
    assert ex["not_binding"] is True
    assert ex["not_full_legal_translation_claimed"] is True


def test_review_34_articles_and_fields():
    rv = _read(RV)
    assert rv["article_count"] == TARGET
    assert rv["article_range"] == [1, TARGET]
    assert [r["article_number"] for r in rv["records"]] == list(range(1, TARGET + 1))
    for r in rv["records"]:
        assert r["coverage_status"] in COVERAGE
        assert r["semantic_alignment_rating"] in {"high", "medium", "low", "extraction_unclear"}
        assert r["llm_ready_as_full_translation"] is False
        assert isinstance(r["missing_or_compressed_elements_ar"], list)
        assert isinstance(r["misleading_or_risky_elements"], list)


def test_review_trust_posture():
    rv = _read(RV)
    assert rv["governing_language"] == "ar"
    assert rv["chinese_source_status"] == "internal_working_translation_source"
    assert rv["official_chinese_translation_claimed"] is False
    assert rv["chinese_binding_claimed"] is False
    assert rv["full_translation_claimed"] is False


def test_no_official_binding_or_governing_chinese_claim():
    blob = (json.dumps(_read(EX), ensure_ascii=False)
            + json.dumps(_read(RV), ensure_ascii=False)).lower()
    for term in ("chinese is binding", "chinese is governing", "official chinese translation",
                 "chinese is official", "binding chinese text", "governing chinese text"):
        assert term not in blob, term
    # every explicit claim flag is false
    for r in _read(RV)["records"]:
        assert r["llm_ready_as_full_translation"] is False


def test_no_chinese_llm_ready_created():
    assert not os.path.isdir(os.path.join(ROOT, "data", "official_chinese_legal_llm"))
    blob = json.dumps(_read(RV), ensure_ascii=False).lower()
    assert "chinese_llm_ready" not in blob


def test_article1_materially_incomplete():
    # Arabic Art 1 has full definitions; the Chinese lists only the defined TERMS -> incomplete
    r1 = next(r for r in _read(RV)["records"] if r["article_number"] == 1)
    assert r1["coverage_status"] == "materially_incomplete_needs_retranslation"
    assert r1["llm_ready_as_full_translation"] is False


def test_md_states_posture():
    md = open(MD, encoding="utf-8").read()
    assert "العربية هي اللغة الحاكمة" in md
    assert "ليست استشارة قانونية" in md
    assert "1–34" in md


def test_protected_layers_unchanged():
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    assert len(zh) == 5 and sum(len(_read(p)["records"]) for p in zh) == 23
    oa = _read(os.path.join(ROOT, "data", "official_arabic_legal_llm",
                            "companies_law_m132_1443_official_arabic_legal_llm_001_281.json"))
    assert len(oa["records"]) == 281
    oe = _read(os.path.join(ROOT, "data", "official_english_legal_llm",
                            "companies_law_m132_1443_official_english_legal_llm_001_281.json"))
    assert len(oe["records"]) == 281
    er = _read(os.path.join(ROOT, "data", "english_reference",
                            "companies_law_m132_1443_en_reference_001_281.json"))
    assert len(er["records"]) == 281
    c = _read(os.path.join(ROOT, "data", "official_arabic",
                           "companies_law_m132_1443_official_arabic_user_provided.json"))
    assert len(c["articles"]) == 281 and c["verification_status"] == "ingested_unverified"


def test_generator_is_byte_stable():
    # generator needs pypdf (optional extra) to read the PDF; skip when unavailable (e.g. CI)
    import pytest
    try:
        import pypdf  # noqa: F401
    except ImportError:
        pytest.skip("pypdf not installed; PDF extraction unavailable")
    before = (open(EX, "rb").read(), open(RV, "rb").read(), open(MD, "rb").read())
    res = subprocess.run([sys.executable, GEN], capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    after = (open(EX, "rb").read(), open(RV, "rb").read(), open(MD, "rb").read())
    assert before == after, "Chinese Bab1 review is not byte-stable / idempotent"


def test_validator_passes():
    res = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts",
                                      "validate_chinese_bab1_original_pdf_translation_review.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
