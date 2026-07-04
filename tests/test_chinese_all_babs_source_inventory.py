"""Chinese all-Babs (1-14) source coverage inventory tests (source inventory only).

Preserves + extracts the original Chinese PDFs for Babs 2-14 (Bab 1 reused) and builds a complete
Articles 1-281 coverage inventory. Source-inventory / review stage ONLY — Chinese is internal /
non-official / non-binding (Arabic governs); NO Chinese LLM-ready records created. Reads committed
artifacts.
"""

import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_DIR = os.path.join(ROOT, "inputs", "chinese_translation_source_pdfs")
SRC_DIR = os.path.join(ROOT, "data", "chinese_translation_sources")
RV_DIR = os.path.join(ROOT, "reports", "chinese_translation_review")
INV = os.path.join(RV_DIR, "chinese_all_babs_source_inventory.json")
IDX = os.path.join(RV_DIR, "chinese_article_coverage_index_001_281.json")
MD = os.path.join(RV_DIR, "CHINESE_ALL_BABS_SOURCE_INVENTORY_AR.md")
GEN = os.path.join(ROOT, "scripts", "gen_chinese_all_babs_source_inventory.py")

TARGET = 281
BAB_RANGES = {1: (1, 34), 2: (35, 50), 3: (51, 57), 4: (58, 137), 5: (138, 155),
              6: (156, 184), 7: (185, 196), 8: (197, 215), 9: (216, 219), 10: (220, 234),
              11: (235, 241), 12: (242, 259), 13: (260, 271), 14: (272, 281)}
PDF_NAMES = {
    1: "saudi_companies_law_ar_zh_bab1_full.pdf", 2: "saudi_companies_law_ar_zh_bab2_full.pdf",
    3: "saudi_companies_law_ar_zh_bab3.pdf", 4: "saudi_companies_law_ar_zh_bab4.pdf",
    5: "saudi_companies_law_ar_zh_bab5.pdf", 6: "saudi_companies_law_ar_zh_bab6.pdf",
    7: "saudi_companies_law_ar_zh_bab7.pdf", 8: "saudi_companies_law_ar_zh_bab8.pdf",
    9: "saudi_companies_law_ar_zh_bab9.pdf", 10: "saudi_companies_law_ar_zh_bab10.pdf",
    11: "saudi_companies_law_ar_zh_bab11.pdf", 12: "saudi_companies_law_ar_zh_bab12.pdf",
    13: "saudi_companies_law_ar_zh_bab13.pdf", 14: "saudi_companies_law_ar_zh_bab14.pdf",
}
EXTRACTED = {
    1: "bab1_zh_source_extracted_articles_001_034.json",
    2: "bab2_zh_source_extracted_articles_035_050.json",
    3: "bab3_zh_source_extracted_articles_051_057.json",
    4: "bab4_zh_source_extracted_articles_058_137.json",
    5: "bab5_zh_source_extracted_articles_138_155.json",
    6: "bab6_zh_source_extracted_articles_156_184.json",
    7: "bab7_zh_source_extracted_articles_185_196.json",
    8: "bab8_zh_source_extracted_articles_197_215.json",
    9: "bab9_zh_source_extracted_articles_216_219.json",
    10: "bab10_zh_source_extracted_articles_220_234.json",
    11: "bab11_zh_source_extracted_articles_235_241.json",
    12: "bab12_zh_source_extracted_articles_242_259.json",
    13: "bab13_zh_source_extracted_articles_260_271.json",
    14: "bab14_zh_source_extracted_articles_272_281.json",
}


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def test_all_expected_files_exist():
    for b in range(1, 15):
        assert os.path.exists(os.path.join(PDF_DIR, PDF_NAMES[b])), b
        assert os.path.exists(os.path.join(SRC_DIR, EXTRACTED[b])), b
    assert os.path.exists(INV) and os.path.exists(IDX) and os.path.exists(MD)


def test_source_pdf_count_14():
    assert len(glob.glob(os.path.join(PDF_DIR, "saudi_companies_law_ar_zh_bab*.pdf"))) == 14
    assert _read(INV)["source_pdf_count"] == 14
    assert _read(INV)["expected_bab_count"] == 14


def test_extracted_file_count_14():
    assert len(glob.glob(os.path.join(SRC_DIR, "bab*_zh_source_extracted_articles_*.json"))) == 14


def test_coverage_index_281_range_and_mapping():
    idx = _read(IDX)
    recs = idx["records"]
    assert idx["article_count"] == TARGET and len(recs) == TARGET
    nums = [r["article_number"] for r in recs]
    assert nums == list(range(1, TARGET + 1))
    assert len(set(nums)) == len(nums)
    for r in recs:
        n = r["article_number"]
        exp = next(b for b, (lo, hi) in BAB_RANGES.items() if lo <= n <= hi)
        assert r["expected_bab_number"] == exp, n


def test_each_extracted_covers_its_bab_range_and_posture():
    for b in range(1, 15):
        ex = _read(os.path.join(SRC_DIR, EXTRACTED[b]))
        lo, hi = BAB_RANGES[b]
        assert [r["article_number"] for r in ex["records"]] == list(range(lo, hi + 1)), b
        assert ex["source_language"] == "zh"
        assert ex["governing_text_language"] == "ar"
        assert ex["official_translation"] is False
        assert ex["not_binding"] is True
        assert ex["not_full_legal_translation_claimed"] is True


def test_trust_posture():
    inv = _read(INV)
    idx = _read(IDX)
    for doc in (inv, idx):
        assert doc["official_chinese_translation_claimed"] is False
        assert doc["chinese_binding_claimed"] is False
        assert doc["full_translation_claimed"] is False
        assert doc["chinese_llm_ready_created"] is False
    assert inv["governing_language"] == "ar"


def test_no_official_binding_or_governing_chinese_claim():
    blob = (json.dumps(_read(INV), ensure_ascii=False)
            + json.dumps(_read(IDX), ensure_ascii=False)).lower()
    for term in ("chinese is binding", "chinese is governing", "official chinese translation",
                 "chinese is official", "binding chinese text", "governing chinese text"):
        assert term not in blob, term


def test_llm_ready_false_for_all_281():
    for r in _read(IDX)["records"]:
        assert r["llm_ready_as_full_translation"] is False


def test_no_chinese_llm_ready_created():
    assert not os.path.isdir(os.path.join(ROOT, "data", "official_chinese_legal_llm"))


def test_protected_layers_unchanged():
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    assert len(zh) == 5 and sum(len(_read(p)["records"]) for p in zh) == 23
    for rel in ("data/official_arabic_legal_llm/"
                "companies_law_m132_1443_official_arabic_legal_llm_001_281.json",
                "data/official_english_legal_llm/"
                "companies_law_m132_1443_official_english_legal_llm_001_281.json",
                "data/english_reference/companies_law_m132_1443_en_reference_001_281.json"):
        assert len(_read(os.path.join(ROOT, rel))["records"]) == 281
    c = _read(os.path.join(ROOT, "data", "official_arabic",
                           "companies_law_m132_1443_official_arabic_user_provided.json"))
    assert len(c["articles"]) == 281 and c["verification_status"] == "ingested_unverified"


def test_bab1_reused_not_rewritten():
    # Bab 1 extracted keeps its original review shape (34 records, 1..34)
    ex = _read(os.path.join(SRC_DIR, EXTRACTED[1]))
    assert [r["article_number"] for r in ex["records"]] == list(range(1, 35))


def test_generator_is_byte_stable():
    import pytest
    try:
        import pypdf  # noqa: F401
    except ImportError:
        pytest.skip("pypdf not installed; PDF extraction unavailable")
    targets = [INV, IDX, MD] + [os.path.join(SRC_DIR, EXTRACTED[b]) for b in range(2, 15)]
    before = {p: open(p, "rb").read() for p in targets}
    res = subprocess.run([sys.executable, GEN], capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    for p in targets:
        assert open(p, "rb").read() == before[p], "not byte-stable: %s" % os.path.basename(p)


def test_validator_passes():
    res = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts",
                                      "validate_chinese_all_babs_source_inventory.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
