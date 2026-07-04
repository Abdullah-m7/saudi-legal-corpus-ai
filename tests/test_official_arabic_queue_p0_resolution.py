"""Official Arabic manual-review queue — P0 resolution update tests.

Article 3's P0 (OCR segmentation miss) is folded into the queue as
resolved_segmentation_ocr_miss / P6. Status update only — nothing verified, promoted, or
text-changed. Reads committed artifacts (no OCR engine needed).
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
UPDATE_MD = os.path.join(RPT_DIR, "OFFICIAL_ARABIC_QUEUE_P0_RESOLUTION_UPDATE_AR.md")
CAND = os.path.join(ROOT, "data", "official_arabic",
                    "companies_law_m132_1443_official_arabic_user_provided.json")
UPDATE = os.path.join(ROOT, "scripts", "update_official_arabic_queue_p0_resolution.py")

TARGET = 281


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _q():
    return _read(QJSON)


def _entries():
    return _q()["entries"]


def _a3():
    return next(e for e in _entries() if e["article_number"] == 3)


def test_outputs_exist():
    assert os.path.exists(QJSON) and os.path.exists(QCSV)
    assert os.path.exists(QMD) and os.path.exists(UPDATE_MD)


def test_still_281_entries_1_to_281():
    e = _entries()
    assert len(e) == TARGET
    assert [x["article_number"] for x in e] == list(range(1, TARGET + 1))


def test_no_p0_anywhere():
    assert all(e["review_priority"] != "P0" for e in _entries())
    q = _q()
    assert q["unresolved_p0_count"] == 0
    assert q["p0_articles"] == []
    assert q["priority_counts"].get("P0", 0) == 0


def test_article3_resolved():
    a3 = _a3()
    assert a3["review_bucket"] == "resolved_segmentation_ocr_miss"
    assert a3["review_priority"] == "P6"
    assert a3["p0_resolution_status"] == "resolved"
    assert a3["p0_resolution_classification"] == "segmentation_ocr_miss"
    assert a3["verification_action_allowed"] is False
    assert "packet page 6" in a3["p0_resolution_note"]


def test_resolved_p0_list_includes_article3():
    assert 3 in _q()["resolved_p0_articles"]


def test_resolved_bucket_count_is_one():
    q = _q()
    assert q["bucket_counts"].get("resolved_segmentation_ocr_miss") == 1
    assert q["bucket_counts"].get("missing_or_segmentation_issue", 0) == 0
    # P6 = 3 exact + 1 resolved
    assert q["priority_counts"]["P6"] == 4


def test_total_still_281():
    q = _q()
    assert sum(q["priority_counts"].values()) == TARGET
    assert sum(q["bucket_counts"].values()) == TARGET


def test_queue_md_p0_count_zero_and_resolved_section():
    md = open(QMD, encoding="utf-8").read()
    assert "resolved_segmentation_ocr_miss" in md
    assert "P0 resolved items" in md or "عناصر P0 المُحلّة" in md


def test_update_report_states_not_verification():
    md = open(UPDATE_MD, encoding="utf-8").read()
    assert "ليست استشارة قانونية" in md
    assert "ingested_unverified" in md
    assert "resolved_segmentation_ocr_miss" in md
    assert "جنسية الشركة" in md


def test_nothing_promoted():
    q = _q()
    assert q["article_by_article_verified"] is False
    assert q["promoted_to_verified"] is False
    assert "verified_against_official_gazette" not in json.dumps(q["entries"], ensure_ascii=False)


def test_csv_reflects_article3_resolution():
    with open(QCSV, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == TARGET
    r3 = next(r for r in rows if r["article_number"] == "3")
    assert r3["review_bucket"] == "resolved_segmentation_ocr_miss"
    assert r3["review_priority"] == "P6"
    assert r3["p0_resolution_status"] == "resolved"


def test_update_script_is_byte_stable():
    before = (open(QJSON, "rb").read(), open(QCSV, "rb").read(), open(QMD, "rb").read())
    r = subprocess.run([sys.executable, UPDATE], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    after = (open(QJSON, "rb").read(), open(QCSV, "rb").read(), open(QMD, "rb").read())
    assert before == after, "queue update is not byte-stable / idempotent"


# -- candidate / derived layers unchanged -----------------------------------
def test_candidate_untouched():
    c = _read(CAND)
    assert len(c["articles"]) == TARGET
    assert c["verification_status"] == "ingested_unverified"
    assert c["article_by_article_verified"] is False
    for a in c["articles"]:
        assert a["verification_status"] == "ingested_unverified"


def test_english_and_chinese_llm_unchanged():
    d = os.path.join(ROOT, "data", "english_legal_llm")
    en = glob.glob(os.path.join(d, "*_en_legal_llm.json"))
    assert len(en) == 8 and sum(len(_read(p)["records"]) for p in en) == 87
    d = os.path.join(ROOT, "data", "chinese_legal_llm")
    zh = glob.glob(os.path.join(d, "*_zh_legal_llm.json"))
    assert len(zh) == 5 and sum(len(_read(p)["records"]) for p in zh) == 23


def test_arabic_llm_not_relabeled_official():
    for p in glob.glob(os.path.join(ROOT, "data", "arabic_legal_llm", "*_ar_legal_llm.json")):
        b = open(p, encoding="utf-8").read().lower()
        assert "official_text_ar" not in b and "verified_against_official_gazette" not in b, p


def test_validator_passes():
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "validate_official_arabic_queue_p0_resolution.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
