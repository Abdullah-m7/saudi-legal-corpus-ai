"""Official Arabic P0 Article 3 segmentation review — tests.

Focused triage of the single P0 item (Article 3, marked missing_in_official_source by the
lossy OCR comparison). Verifies nothing, promotes nothing, changes no candidate text.
"""

import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RPT_DIR = os.path.join(ROOT, "reports", "official_arabic_verification")
REVIEW = os.path.join(RPT_DIR, "p0_article3_segmentation_review.json")
REVIEW_MD = os.path.join(RPT_DIR, "P0_ARTICLE3_SEGMENTATION_REVIEW_AR.md")
QUEUE = os.path.join(RPT_DIR, "manual_review_queue.json")
CAND = os.path.join(ROOT, "data", "official_arabic",
                    "companies_law_m132_1443_official_arabic_user_provided.json")

TARGET = 281
CLASSES = {"segmentation_ocr_miss", "source_text_found_ocr_noisy", "source_text_not_found",
           "needs_manual_visual_review"}
ARTICLE3_TEXT = ("تعد الشركة التي تؤسس وفقًا لأحكام النظام سعودية الجنسية، "
                 "ويجب أن يكون مركزها الرئيس في المملكة.")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _r():
    return _read(REVIEW)


def test_outputs_exist():
    assert os.path.exists(REVIEW)
    assert os.path.exists(REVIEW_MD)


def test_article_number_and_title():
    r = _r()
    assert r["article_number"] == 3
    assert r["article_title_ar"] == "جنسية الشركة"
    assert r["p0_reason_before"] == "missing_in_official_source"


def test_review_promotes_nothing():
    r = _r()
    assert r["verification_action_allowed"] is False
    assert r["candidate_text_changed"] is False
    assert r["verification_status_changed"] is False
    assert r["article_by_article_verified"] is False
    assert "verified_against_official_gazette" not in json.dumps(r, ensure_ascii=False)


def test_classification_valid():
    assert _r()["classification"] in CLASSES


def test_source_location_and_evidence():
    r = _r()
    assert isinstance(r["source_location_found"], bool)
    if r["source_location_found"]:
        assert r["source_part_file"]
        assert r.get("source_page_number_within_packet")
        assert r.get("ocr_evidence_snippet")
        # evidence must actually mention Article 3 content
        ev = r["ocr_evidence_snippet"]
        assert "جنسية الشركة" in ev or "سعودية الجنسية" in ev


def test_search_terms_recorded():
    r = _r()
    terms = r["search_terms_used"]
    for t in ("سعودية الجنسية", "مركزها الرئيس", "تعد الشركة"):
        assert t in terms, t


def test_candidate_article3_text_unchanged():
    r = _r()
    assert r["candidate_text"] == ARTICLE3_TEXT
    cand = _read(CAND)
    a3 = next(a for a in cand["articles"] if a["article_number"] == 3)
    assert a3["official_text_ar"] == ARTICLE3_TEXT
    assert a3["official_text_ar"] == r["candidate_text"]


def test_arabic_report_states_review_only():
    md = open(REVIEW_MD, encoding="utf-8").read()
    assert "ليست استشارة قانونية" in md
    assert "ingested_unverified" in md
    assert "جنسية الشركة" in md
    assert "segmentation_ocr_miss" in md


# -- candidate / queue / derived layers unchanged ---------------------------
def test_candidate_untouched():
    c = _read(CAND)
    assert len(c["articles"]) == TARGET
    assert c["verification_status"] == "ingested_unverified"
    assert c["article_by_article_verified"] is False
    for a in c["articles"]:
        assert a["verification_status"] == "ingested_unverified"


def test_manual_review_queue_still_281():
    assert len(_read(QUEUE)["entries"]) == TARGET


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


def test_official_english_reference_unchanged():
    ref = os.path.join(ROOT, "data", "english_reference")
    for fname, exp in (("book1_en_reference.json", list(range(1, 35))),
                       ("book2_en_reference.json", list(range(35, 51))),
                       ("book3_en_reference.json", list(range(51, 58)))):
        doc = _read(os.path.join(ref, fname))
        assert [r["article_number"] for r in doc["records"]] == exp, fname


def test_validator_passes():
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "validate_official_arabic_p0_article3_review.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
