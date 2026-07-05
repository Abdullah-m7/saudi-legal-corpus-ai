"""Chinese remediation Batch P2-004 tests (P2 expansion batch; 20 articles, Babs 10/11/12).

Expansion track: internal Chinese EXPANDED from the official Arabic governing text (English guidance
only; prior condensed candidate as the baseline) for exactly the 20 authorized P2-004 articles. Each
record's bab matches the coverage index, links to the (unchanged) prior candidate, and links to its P2
backlog finding. Chinese internal / non-official / non-binding / non-governing; qa_status
pending_future_qa. No full Arabic/English text embedded; P2-001 + P2-002 + all P1 + P0 (data + QA) and
base layers untouched; no p3_* dirs. Reads committed artifacts and exercises rejection paths.
"""

import copy
import glob
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "chinese_remediation_batches", "p2_004",
                    "companies_law_m132_1443_zh_internal_remediation_p2_004.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_REMEDIATION_BATCH_P2_004_AR.md")
ARABIC = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
ENGLISH = os.path.join(ROOT, "data", "official_english_legal_llm",
                       "companies_law_m132_1443_official_english_legal_llm_001_281.json")
COV = os.path.join(ROOT, "reports", "chinese_translation_review",
                   "chinese_article_coverage_index_001_281.json")
CANDF = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                     "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")
BACKLOG = os.path.join(ROOT, "reports", "chinese_translation_review",
                       "chinese_remediation_backlog_001_281.json")
VALIDATOR = os.path.join(ROOT, "scripts", "validate_chinese_remediation_batch_p2_004.py")

ARTS = [226, 228, 229, 231, 232, 234, 235, 236, 237, 238, 239, 240, 241, 243, 245, 246, 247, 249, 250, 251]
BABS = (10, 11, 12)
DIST = {10: [226, 228, 229, 231, 232, 234], 11: [235, 236, 237, 238, 239, 240, 241], 12: [243, 245, 246, 247, 249, 250, 251]}


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _d():
    return _read(DATA)


def _run(path=None):
    args = [sys.executable, VALIDATOR]
    if path is not None:
        args.append(path)
    return subprocess.run(args, capture_output=True, text=True)


def _write_tmp(tmp_path, doc):
    p = tmp_path / "p2_004_mutated.json"
    p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return str(p)


def test_validator_passes_on_current_outputs():
    res = _run()
    assert res.returncode == 0, res.stdout + res.stderr


def test_output_files_exist():
    assert os.path.exists(DATA) and os.path.exists(MD)


def test_exact_article_scope():
    d = _d()
    assert d["scope_articles"] == ARTS
    assert [r["article_number"] for r in d["records"]] == ARTS


def test_exact_expected_babs():
    assert _d()["expected_babs"] == list(BABS)


def test_expected_bab_distribution():
    dist = {}
    for r in _d()["records"]:
        dist.setdefault(r["bab"], []).append(r["article_number"])
    assert dist == DIST


def test_exact_record_count():
    assert _d()["article_count"] == 20
    assert len(_d()["records"]) == 20


def test_no_duplicate_articles():
    nums = [r["article_number"] for r in _d()["records"]]
    assert len(set(nums)) == 20


def test_priority_and_track():
    d = _d()
    assert d["priority"] == "P2"
    assert d["remediation_track"] == "P2_expansion_needed"
    assert d["remediation_action"] == "expand_existing_internal_chinese_from_arabic"
    assert d["source_basis"] == "official_arabic_plus_existing_chinese_candidate"
    assert d["first_p2_batch"] is False


def test_each_record_bab_in_range():
    for r in _d()["records"]:
        assert r["bab"] in BABS


def test_each_record_bab_matches_coverage_index():
    cov = {r["article_number"]: r for r in _read(COV)["records"]}
    for r in _d()["records"]:
        assert r["bab"] == cov[r["article_number"]]["expected_bab_number"]


def test_posture_flags_correct():
    d = _d()
    assert d["internal_reference_only"] is True
    for r in d["records"]:
        assert r["internal_reference_only"] is True
        assert r["translation_basis"] == "official_arabic_governing_text"
        assert r["english_guidance_role"] == "secondary_guidance_only"
        assert r["source_basis"] == "official_arabic_plus_existing_chinese_candidate"
        assert r["remediation_action"] == "expand_existing_internal_chinese_from_arabic"
        assert r["source_status_before"] == "condensed_candidate_needs_expansion"
        assert r["qa_status"] == "pending_future_qa"


def test_official_status_boundaries():
    ofs = _d()["official_status"]
    for f in ("official_government_publication", "official_translation_claimed",
              "official_adoption_claimed", "chinese_official", "chinese_binding",
              "chinese_governing"):
        assert ofs[f] is False
    assert ofs["not_legal_advice"] is True


def test_no_official_binding_governing_chinese_claim():
    d = _d()
    for f in ("official_chinese_translation_claimed", "chinese_binding_claimed",
              "chinese_governing_claimed"):
        assert d[f] is False
        for r in d["records"]:
            assert r[f] is False


def test_chinese_hash_correct():
    for r in _d()["records"]:
        assert r["remediated_chinese_text_hash_sha256"] == hashlib.sha256(
            r["remediated_chinese_text"].encode("utf-8")).hexdigest()


def test_chinese_segment_parity_with_arabic():
    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    for r in _d()["records"]:
        a = [s for s in ar[r["article_number"]]["official_text_ar"].split("\n") if s.strip()]
        z = [s for s in r["remediated_chinese_text"].split("\n") if s.strip()]
        assert len(z) == len(a), r["article_number"]


def test_arabic_hashes_match_official_source():
    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    for r in _d()["records"]:
        assert r["arabic_source_hash_sha256"] == ar[r["article_number"]]["official_text_hash_sha256"]


def test_english_hashes_match_official_source():
    en = {r["article_number"]: r for r in _read(ENGLISH)["records"]}
    for r in _d()["records"]:
        assert r["english_guidance_hash_sha256"] == en[r["article_number"]]["legal_rule_text_hash_sha256"]


def test_prior_candidate_link_matches_unchanged_candidate():
    cand = {r["article_number"]: r for r in _read(CANDF)["records"]}
    for r in _d()["records"]:
        c = cand[r["article_number"]]
        assert r["prior_candidate_hash_sha256"] == c["chinese_text_hash_sha256"]
        assert r["prior_candidate_record_id"] == c["record_id"]


def test_all_scope_articles_are_p2_in_backlog():
    bk = {r["article_number"]: r for r in _read(BACKLOG)["records"]}
    for r in _d()["records"]:
        b = bk[r["article_number"]]
        assert b["current_priority"] == "P2"
        assert b["remediation_track"] == "P2_expansion_needed"


def test_no_full_arabic_or_english_text_duplicated():
    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    en = {r["article_number"]: r for r in _read(ENGLISH)["records"]}
    blob = json.dumps(_d(), ensure_ascii=False)
    for nn in ARTS:
        assert ar[nn]["official_text_ar"] not in blob
        assert en[nn]["legal_rule_text_en"] not in blob


def test_prior_p2_and_p1_data_unchanged():
    for sub, cnt in {"p1_001": 20, "p1_002": 20, "p1_003": 20, "p1_004": 16,
                     "p2_001": 20, "p2_002": 20}.items():
        p = os.path.join(ROOT, "data", "chinese_remediation_batches", sub,
                         "companies_law_m132_1443_zh_internal_remediation_%s.json" % sub)
        assert len(_read(p)["records"]) == cnt


def test_prior_qa_unchanged():
    for fn in ("chinese_remediation_batch_p1_001_qa.json", "chinese_remediation_batch_p1_004_qa.json",
               "chinese_remediation_batch_p2_001_qa.json", "chinese_remediation_batch_p2_002_qa.json"):
        qa = _read(os.path.join(ROOT, "reports", "chinese_translation_review", fn))
        assert qa["final_status"] == "QA_PASS"


def test_only_authorized_dirs_no_p3():
    allowed = ("p1_001", "p1_002", "p1_003", "p1_004", "p2_001", "p2_002", "p2_003", "p2_004", "p2_005", "p3_conf_001")
    later = [x for x in glob.glob(os.path.join(ROOT, "data", "chinese_remediation_batches", "p[123]_*"))
             if os.path.basename(x) not in allowed]
    assert not later


# --- rejection paths ---

def test_reject_out_of_scope_article(tmp_path):
    doc = copy.deepcopy(_d())
    doc["records"][0]["article_number"] = 999
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_wrong_bab(tmp_path):
    doc = copy.deepcopy(_d())
    for r in doc["records"]:
        if r["article_number"] == 226:
            r["bab"] = 11
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_official_claim_true(tmp_path):
    doc = copy.deepcopy(_d())
    doc["official_chinese_translation_claimed"] = True
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_chinese_hash_tamper(tmp_path):
    doc = copy.deepcopy(_d())
    doc["records"][0]["remediated_chinese_text"] = doc["records"][0]["remediated_chinese_text"] + "X"
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_broken_prior_candidate_link(tmp_path):
    doc = copy.deepcopy(_d())
    doc["records"][0]["prior_candidate_hash_sha256"] = "0" * 64
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_wrong_track(tmp_path):
    doc = copy.deepcopy(_d())
    doc["remediation_track"] = "P1_retranslation_or_manual_review"
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0
