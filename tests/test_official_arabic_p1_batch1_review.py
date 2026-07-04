"""Official Arabic P1 low-similarity batch-1 review tests (triage only).

The batch-1 review selects the 10 lowest-similarity P1 articles from the manual-review queue and
classifies WHY each is low-similarity from the already-captured OCR artifact. Status/triage only —
nothing verified, promoted, or text-changed. Reads committed artifacts (no OCR engine needed).
"""

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RPT = os.path.join(ROOT, "reports", "official_arabic_verification")
QJSON = os.path.join(RPT, "manual_review_queue.json")
REVIEW = os.path.join(RPT, "p1_low_similarity_batch1_review.json")
REVIEW_MD = os.path.join(RPT, "P1_LOW_SIMILARITY_BATCH1_REVIEW_AR.md")
CAND = os.path.join(ROOT, "data", "official_arabic",
                    "companies_law_m132_1443_official_arabic_user_provided.json")
BUILDER = os.path.join(ROOT, "scripts", "build_official_arabic_p1_batch1_review.py")

BATCH_ID = "P1_LOW_SIMILARITY_BATCH1"
BATCH_SIZE = 10
ALLOWED_CLASS = {
    "likely_ocr_noise", "segmentation_or_alignment_drift", "table_or_list_formatting_drift",
    "heading_or_ordinal_corruption", "possible_substantive_difference",
    "needs_manual_visual_review", "insufficient_ocr_evidence",
}


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _r():
    return _read(REVIEW)


def _q():
    return _read(QJSON)


def _lowest_p1():
    p1 = [e for e in _q()["entries"] if e["review_priority"] == "P1"]
    p1.sort(key=lambda e: (e["similarity"], e["article_number"]))
    return [e["article_number"] for e in p1[:BATCH_SIZE]]


def test_outputs_exist():
    assert os.path.exists(REVIEW) and os.path.exists(REVIEW_MD)


def test_batch_id_and_size():
    r = _r()
    assert r["stage"] == "OFFICIAL_ARABIC_P1_LOW_SIMILARITY_BATCH1_REVIEW"
    assert r["batch_id"] == BATCH_ID
    assert r["batch_size"] == BATCH_SIZE
    assert r["selection_method"] == "lowest_similarity_p1_articles_from_manual_review_queue"


def test_exactly_ten_entries():
    assert len(_r()["entries"]) == BATCH_SIZE


def test_selection_matches_ten_lowest_p1():
    expected = _lowest_p1()
    r = _r()
    assert r["selected_articles"] == expected
    assert [e["article_number"] for e in r["entries"]] == expected


def test_every_entry_was_p1_before():
    qprio = {e["article_number"]: e["review_priority"] for e in _q()["entries"]}
    for e in _r()["entries"]:
        assert qprio[e["article_number"]] == "P1"
        assert e["queue_priority_before"] == "P1"


def test_classifications_are_allowed():
    for e in _r()["entries"]:
        assert e["batch_review_classification"] in ALLOWED_CLASS
        assert e["review_confidence"] in ("high", "medium", "low")


def test_every_entry_is_triage_only():
    for e in _r()["entries"]:
        assert e["verification_action_allowed"] is False
        assert e["candidate_text_changed"] is False
        assert e["verification_status_changed"] is False
        assert e["article_by_article_verified"] is False


def test_nothing_verified_or_promoted():
    r = _r()
    assert r["article_by_article_verified"] is False
    assert r["promoted_to_verified"] is False
    assert r["candidate_text_changed"] is False
    assert "verified_against_official_gazette" not in json.dumps(r["entries"], ensure_ascii=False)


def test_classification_counts_consistent():
    r = _r()
    tallied = {}
    for e in r["entries"]:
        tallied[e["batch_review_classification"]] = \
            tallied.get(e["batch_review_classification"], 0) + 1
    assert r["classification_counts"] == tallied
    assert sum(r["classification_counts"].values()) == BATCH_SIZE


def test_entries_carry_evidence_and_snippets():
    for e in _r()["entries"]:
        assert e["candidate_text"]
        assert e["candidate_snippet_ar"]
        assert isinstance(e["search_terms_used"], list) and e["search_terms_used"]
        assert "term_hit_pages_global" in e["ocr_pages_searched"]
        # source located entries must name a packet part file + page
        if e["source_location_found"]:
            assert e["source_part_file"]
            assert e["source_page_number_within_packet"] is not None


def test_md_states_triage_only():
    md = open(REVIEW_MD, encoding="utf-8").read()
    assert "ليست استشارة قانونية" in md
    assert "ingested_unverified" in md
    assert "article_by_article_verified" in md
    # recommended next workflow A/B/C present
    assert "A)" in md and "B)" in md and "C)" in md


def test_builder_is_byte_stable():
    before = (open(REVIEW, "rb").read(), open(REVIEW_MD, "rb").read())
    res = subprocess.run([sys.executable, BUILDER], capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    after = (open(REVIEW, "rb").read(), open(REVIEW_MD, "rb").read())
    assert before == after, "batch-1 review is not byte-stable / idempotent"


def test_candidate_untouched():
    c = _read(CAND)
    assert len(c["articles"]) == 281
    assert c["verification_status"] == "ingested_unverified"
    assert c["article_by_article_verified"] is False
    for a in c["articles"]:
        assert a["verification_status"] == "ingested_unverified"


def test_candidate_text_matches_batch_entries():
    cand_by = {a["article_number"]: a for a in _read(CAND)["articles"]}
    for e in _r()["entries"]:
        assert e["candidate_text"] == cand_by[e["article_number"]]["official_text_ar"]


def test_queue_still_281_and_no_p0():
    q = _q()
    assert len(q["entries"]) == 281
    assert q["unresolved_p0_count"] == 0
    assert all(e["review_priority"] != "P0" for e in q["entries"])


def test_validator_passes():
    res = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts",
                                      "validate_official_arabic_p1_batch1_review.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
