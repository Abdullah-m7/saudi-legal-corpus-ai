"""Chinese internal candidate semantic QA (189) + completion gap plan (281) tests.

QA/plan stage ONLY — no Chinese generated/corrected, candidate/source data untouched. Chinese is
internal / non-official / non-binding; Arabic governs. The 92 excluded articles stay blocked
(no isolable Chinese text). Reads committed artifacts.
"""

import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RV = os.path.join(ROOT, "reports", "chinese_translation_review")
QA = os.path.join(RV, "chinese_internal_llm_semantic_qa_189.json")
GAP = os.path.join(RV, "chinese_completion_gap_plan_001_281.json")
MD = os.path.join(RV, "CHINESE_INTERNAL_LLM_SEMANTIC_QA_AND_GAP_PLAN_AR.md")
CANDF = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                     "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")
GEN = os.path.join(ROOT, "scripts", "gen_chinese_internal_llm_semantic_qa_gap_plan.py")

CAND_N = 189
EXCL_N = 92
ALIGN = {"high", "medium", "low", "not_assessed"}
COMPLETE = {"near_full", "condensed", "materially_incomplete", "not_assessed"}
USE = {"usable_internal_reference_with_caution",
       "usable_for_retrieval_but_needs_expansion_before_full_layer",
       "not_safe_for_full_layer_needs_retranslation", "manual_review_required"}
PRIORITY = {"P0", "P1", "P2", "P3"}
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _excluded():
    return set(_read(CANDF)["excluded_articles"])


def test_output_files_exist():
    assert os.path.exists(QA) and os.path.exists(GAP) and os.path.exists(MD)


def test_qa_189_records():
    qa = _read(QA)
    assert qa["candidate_record_count"] == CAND_N
    assert qa["reviewed_record_count"] == CAND_N
    assert len(qa["records"]) == CAND_N
    incl = {r["article_number"] for r in _read(CANDF)["records"]}
    assert {r["article_number"] for r in qa["records"]} == incl


def test_gap_plan_281_entries():
    gap = _read(GAP)
    assert len(gap["article_plan"]) == 281
    nums = [r["article_number"] for r in gap["article_plan"]]
    assert nums == list(range(1, 282))
    assert len(set(nums)) == len(nums)


def test_92_excluded_blocked():
    excl = _excluded()
    assert len(excl) == EXCL_N
    for r in _read(GAP)["article_plan"]:
        if r["article_number"] in excl:
            assert r["has_isolable_chinese_candidate"] is False
            assert r["current_chinese_status"] == "excluded_no_isolable_article_text"
            assert r["full_layer_blocker"] == "no_isolable_chinese_text"
            assert r["required_next_action"] in ("retranslate_from_arabic",
                                                 "manually_segment_or_replace_source")
            assert r["priority"] in ("P0", "P1")


def test_candidate_excluded_partition():
    incl = {r["article_number"] for r in _read(CANDF)["records"]}
    excl = _excluded()
    assert not (incl & excl)
    assert incl | excl == set(range(1, 282))


def test_qa_enum_values():
    for r in _read(QA)["records"]:
        assert r["semantic_alignment_rating"] in ALIGN
        assert r["legal_completeness_rating"] in COMPLETE
        assert r["qa_use_status"] in USE
        assert r["priority"] in PRIORITY


def test_no_generated_or_corrected_chinese_fields():
    def keys(obj, acc):
        if isinstance(obj, dict):
            for k, v in obj.items():
                acc.add(k)
                keys(v, acc)
        elif isinstance(obj, list):
            for v in obj:
                keys(v, acc)
    acc = set()
    keys(_read(QA), acc)
    keys(_read(GAP), acc)
    for bad in ("chinese_text", "corrected_chinese", "generated_chinese", "arabic_to_chinese",
                "english_to_chinese", "official_text_ar", "legal_rule_text_en"):
        assert bad not in acc, bad


def test_trust_posture_and_no_overclaims():
    qa = _read(QA)
    for f in ("full_chinese_translation_claimed", "official_chinese_translation_claimed",
              "chinese_binding_claimed", "chinese_governing_claimed", "corrected_chinese_created",
              "arabic_used_to_generate_chinese", "english_used_to_generate_chinese"):
        assert qa[f] is False
    blob = (json.dumps(qa, ensure_ascii=False)
            + json.dumps(_read(GAP), ensure_ascii=False)).lower()
    for term in BANNED:
        assert term not in blob, term


def test_protected_layers_unchanged():
    assert len(_read(CANDF)["records"]) == CAND_N
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
    assert len(glob.glob(os.path.join(ROOT, "data", "chinese_translation_sources",
                                      "bab*_zh_source_extracted_articles_*.json"))) == 14


def test_generator_is_byte_stable():
    before = (open(QA, "rb").read(), open(GAP, "rb").read(), open(MD, "rb").read())
    res = subprocess.run([sys.executable, GEN], capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    after = (open(QA, "rb").read(), open(GAP, "rb").read(), open(MD, "rb").read())
    assert before == after, "QA/gap plan is not byte-stable / idempotent"


def test_validator_passes():
    res = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts",
                                      "validate_chinese_internal_llm_semantic_qa_gap_plan.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
