"""Official Arabic source verification-comparison report — tests.

The ingested candidate is compared against the OFFICIAL scanned-PDF source (OCR-extracted) as
a report only. Nothing is promoted to verified; the candidate is untouched. These tests read
the committed report/artifacts (no OCR engine needed).
"""

import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAND = os.path.join(ROOT, "data", "official_arabic",
                    "companies_law_m132_1443_official_arabic_user_provided.json")
RPT_DIR = os.path.join(ROOT, "reports", "official_arabic_verification")
REPORT = os.path.join(RPT_DIR, "official_arabic_candidate_comparison_report.json")
AR_MD = os.path.join(RPT_DIR, "OFFICIAL_ARABIC_VERIFICATION_REPORT_AR.md")
SCANNED_META = os.path.join(RPT_DIR, "scanned_pdf_source_metadata.json")
CAPTURE_META = os.path.join(RPT_DIR, "official_source_capture_metadata.json")
OCR_ART = os.path.join(RPT_DIR, "ocr_source_pages.json")
PARTS_DIR = os.path.join(ROOT, "inputs", "official_arabic_verification",
                         "nizam_alsharikat_1443h_parts")
CMP = os.path.join(ROOT, "scripts", "compare_official_arabic_candidate_to_source.py")

TARGET = 281
DIFF_TYPES = {"exact_match", "whitespace_or_markdown_only", "punctuation_or_spacing",
              "substantive_difference", "missing_in_official_source", "missing_in_candidate"}


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


# -- source packet present + hashed -----------------------------------------
def test_six_pdf_parts_present_and_contiguous():
    files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(PARTS_DIR, "*.pdf")))
    assert len(files) == 6, files
    sm = _read(SCANNED_META)
    assert sm["total_parts"] == 6 and sm["total_pages"] == 119, sm
    parts = sorted(sm["parts"], key=lambda p: p["pages_from"])
    prev = 0
    for p in parts:
        assert p["pages_from"] == prev + 1, p
        assert len(p["sha256"]) == 64, p
        prev = p["pages_to"]
    assert prev == 119


def test_capture_metadata_present_and_not_verified():
    cm = _read(CAPTURE_META)
    assert cm["official_source_captured"] is True
    assert cm["article_by_article_verified"] is False
    assert cm["verification_status"] != "verified_against_official_gazette"


def test_ocr_artifact_119_pages():
    o = _read(OCR_ART)
    assert o["page_count"] == 119, o["page_count"]


# -- candidate untouched -----------------------------------------------------
def test_candidate_untouched_281_ingested_unverified():
    c = _read(CAND)
    arts = c["articles"]
    assert len(arts) == TARGET
    assert [a["article_number"] for a in arts] == list(range(1, TARGET + 1))
    assert c["verification_status"] == "ingested_unverified"
    assert c["article_by_article_verified"] is False
    for a in arts:
        assert a["verification_status"] == "ingested_unverified", a["article_number"]
        assert a["verification_status"] != "verified_against_official_gazette", a["article_number"]


# -- comparison report structure --------------------------------------------
def test_report_covers_all_281_articles_no_gaps():
    r = _read(REPORT)
    nums = [e["article_number"] for e in r["entries"]]
    assert nums == list(range(1, TARGET + 1)), "entries must cover 1..281 with no gaps"


def test_every_entry_has_valid_fields():
    r = _read(REPORT)
    for e in r["entries"]:
        assert 1 <= e["article_number"] <= TARGET
        assert e["difference_type"] in DIFF_TYPES, e["difference_type"]
        assert "candidate_hash" in e
        assert isinstance(e["exact_text_match"], bool)
        assert isinstance(e["normalized_text_match"], bool)


def test_summary_counts_equal_detailed_entries():
    r = _read(REPORT)
    counts = r["summary_counts"]
    assert sum(counts.values()) == len(r["entries"])
    for k in DIFF_TYPES:
        got = sum(1 for e in r["entries"] if e["difference_type"] == k)
        assert counts.get(k, 0) == got, (k, counts.get(k), got)


def test_report_does_not_promote_anything():
    r = _read(REPORT)
    assert r["article_by_article_verified"] is False
    assert r["promoted_to_verified"] is False
    assert r["verification_status_unchanged"] == "ingested_unverified"
    # no entry claims a verified status
    for e in r["entries"]:
        assert "verified_against_official_gazette" not in json.dumps(e)


def test_arabic_report_states_comparison_only_and_not_verified():
    md = open(AR_MD, encoding="utf-8").read()
    assert "ليست استشارة قانونية" in md          # not legal advice
    assert "ingested_unverified" in md
    assert "article_by_article_verified" in md and "false" in md
    assert "verified_against_official_gazette" in md   # states none promoted


def test_comparison_script_is_byte_stable():
    before = open(REPORT, "rb").read()
    r = subprocess.run([sys.executable, CMP], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert open(REPORT, "rb").read() == before, "comparison report not byte-stable / idempotent"


# -- derived layers unchanged ------------------------------------------------
def test_english_legal_llm_unchanged_8_files_87_records():
    d = os.path.join(ROOT, "data", "english_legal_llm")
    files = glob.glob(os.path.join(d, "*_en_legal_llm.json"))
    assert len(files) == 8
    assert sum(len(_read(p)["records"]) for p in files) == 87


def test_chinese_legal_llm_unchanged_5_files_23_records():
    d = os.path.join(ROOT, "data", "chinese_legal_llm")
    files = glob.glob(os.path.join(d, "*_zh_legal_llm.json"))
    assert len(files) == 5
    assert sum(len(_read(p)["records"]) for p in files) == 23


def test_arabic_llm_not_relabeled_official():
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


def test_validator_passes():
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "validate_official_arabic_verification_report.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
