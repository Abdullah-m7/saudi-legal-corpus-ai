"""Official Arabic OCR manual-review queue — tests.

A triage queue derived from the lossy OCR comparison. It promotes NOTHING and changes NO
candidate text. These tests read the committed queue artifacts (no OCR engine needed).
"""

import csv
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RPT_DIR = os.path.join(ROOT, "reports", "official_arabic_verification")
QJSON = os.path.join(RPT_DIR, "manual_review_queue.json")
QCSV = os.path.join(RPT_DIR, "manual_review_queue.csv")
QMD = os.path.join(RPT_DIR, "OFFICIAL_ARABIC_OCR_MANUAL_REVIEW_QUEUE_AR.md")
CAND = os.path.join(ROOT, "data", "official_arabic",
                    "companies_law_m132_1443_official_arabic_user_provided.json")
BUILD = os.path.join(ROOT, "scripts", "build_official_arabic_manual_review_queue.py")

TARGET = 281
BUCKETS = {"exact_match_no_action", "normalized_or_punctuation_review",
           "likely_ocr_noise_high_similarity", "likely_ocr_noise_medium_similarity",
           "low_similarity_manual_review", "missing_or_segmentation_issue",
           "possible_substantive_difference_manual_review",
           "resolved_segmentation_ocr_miss"}
PRIOS = {"P0", "P1", "P2", "P3", "P4", "P5", "P6"}
BUCKET_PRIO = {
    "missing_or_segmentation_issue": "P0", "low_similarity_manual_review": "P1",
    "possible_substantive_difference_manual_review": "P2",
    "likely_ocr_noise_medium_similarity": "P3", "likely_ocr_noise_high_similarity": "P4",
    "normalized_or_punctuation_review": "P5", "exact_match_no_action": "P6",
    # a resolved P0 OCR segmentation miss is de-prioritised to P6
    "resolved_segmentation_ocr_miss": "P6"}


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _q():
    return _read(QJSON)


def _entries():
    return _q()["entries"]


# -- outputs exist -----------------------------------------------------------
def test_outputs_exist():
    assert os.path.exists(QJSON)
    assert os.path.exists(QCSV)
    assert os.path.exists(QMD)


def test_exactly_281_entries_1_to_281():
    e = _entries()
    assert len(e) == TARGET
    assert [x["article_number"] for x in e] == list(range(1, TARGET + 1))


def test_csv_has_281_rows_plus_header():
    with open(QCSV, encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    assert len(rows) == TARGET + 1, len(rows)


# -- every entry bucketed + prioritised + no verification action ------------
def test_every_entry_bucket_and_priority():
    for e in _entries():
        assert e["review_bucket"] in BUCKETS, e
        assert e["review_priority"] in PRIOS, e
        assert BUCKET_PRIO[e["review_bucket"]] == e["review_priority"], e
        assert e["verification_action_allowed"] is False


def test_bucketing_logic_matches_difference_type_and_similarity():
    for e in _entries():
        # A P0 item resolved as an OCR segmentation miss is intentionally re-bucketed to
        # resolved_segmentation_ocr_miss (P6); its original difference_type no longer dictates
        # the bucket.
        if e.get("p0_resolution_status") == "resolved":
            assert e["review_bucket"] == "resolved_segmentation_ocr_miss"
            assert e["review_priority"] == "P6"
            continue
        dt = e["original_difference_type"]
        sim = e["similarity"] or 0.0
        b = e["review_bucket"]
        if dt == "exact_match":
            assert b == "exact_match_no_action"
        elif dt in ("whitespace_or_markdown_only", "punctuation_or_spacing"):
            assert b == "normalized_or_punctuation_review"
        elif dt in ("missing_in_official_source", "missing_in_candidate"):
            assert b == "missing_or_segmentation_issue"
        elif dt == "substantive_difference":
            if sim >= 0.95:
                assert b == "likely_ocr_noise_high_similarity"
            elif sim >= 0.80:
                assert b == "likely_ocr_noise_medium_similarity"
            elif sim < 0.60:
                assert b == "low_similarity_manual_review"
            else:
                assert b == "possible_substantive_difference_manual_review"


def test_priority_and_bucket_counts_equal_entries():
    q = _q()
    e = q["entries"]
    for pr in PRIOS:
        got = sum(1 for x in e if x["review_priority"] == pr)
        if got:
            assert q["priority_counts"].get(pr, 0) == got, pr
    for b in BUCKETS:
        got = sum(1 for x in e if x["review_bucket"] == b)
        if got:
            assert q["bucket_counts"].get(b, 0) == got, b
    assert sum(q["priority_counts"].values()) == TARGET


def test_p0_p1_lists_match_entries():
    q = _q()
    p0 = sorted(x["article_number"] for x in q["entries"] if x["review_priority"] == "P0")
    p1 = sorted(x["article_number"] for x in q["entries"] if x["review_priority"] == "P1")
    assert sorted(q["p0_articles"]) == p0
    assert sorted(q["p1_articles"]) == p1


# -- nothing promoted; candidate untouched ----------------------------------
def test_queue_promotes_nothing():
    q = _q()
    assert q["article_by_article_verified"] is False
    assert q["promoted_to_verified"] is False
    assert q["verification_status_unchanged"] == "ingested_unverified"
    assert "verified_against_official_gazette" not in json.dumps(q["entries"], ensure_ascii=False)


def test_candidate_untouched():
    c = _read(CAND)
    assert len(c["articles"]) == TARGET
    assert c["verification_status"] == "ingested_unverified"
    assert c["article_by_article_verified"] is False
    for a in c["articles"]:
        assert a["verification_status"] == "ingested_unverified"


def test_arabic_report_states_not_verification():
    md = open(QMD, encoding="utf-8").read()
    assert "ليست استشارة قانونية" in md
    assert "ingested_unverified" in md
    assert "article_by_article_verified" in md and "false" in md
    assert "promotes no article" in md.lower() or "لا يرقّي" in md


def test_build_is_byte_stable():
    before = (open(QJSON, "rb").read(), open(QCSV, "rb").read(), open(QMD, "rb").read())
    r = subprocess.run([sys.executable, BUILD], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    after = (open(QJSON, "rb").read(), open(QCSV, "rb").read(), open(QMD, "rb").read())
    assert before == after, "manual review queue not byte-stable / idempotent"


# -- derived layers unchanged ------------------------------------------------
def test_english_legal_llm_unchanged_8_87():
    d = os.path.join(ROOT, "data", "english_legal_llm")
    files = glob.glob(os.path.join(d, "*_en_legal_llm.json"))
    assert len(files) == 8 and sum(len(_read(p)["records"]) for p in files) == 87


def test_chinese_legal_llm_unchanged_5_23():
    d = os.path.join(ROOT, "data", "chinese_legal_llm")
    files = glob.glob(os.path.join(d, "*_zh_legal_llm.json"))
    assert len(files) == 5 and sum(len(_read(p)["records"]) for p in files) == 23


def test_arabic_llm_not_relabeled_official():
    for p in glob.glob(os.path.join(ROOT, "data", "arabic_legal_llm", "*_ar_legal_llm.json")):
        b = open(p, encoding="utf-8").read().lower()
        assert "official_text_ar" not in b and "verified_against_official_gazette" not in b, p


def test_validator_passes():
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "validate_official_arabic_manual_review_queue.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
