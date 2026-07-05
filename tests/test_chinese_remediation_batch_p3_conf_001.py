"""Chinese confirmation Batch P3-CONF-001 tests (final P3 confirmation batch; 18 articles, Babs 2/3).

P3 track = confirmation / retain (not expansion): the existing internal Chinese candidate for these 18
articles is retained verbatim as internal reference — no new Chinese text generated, nothing modified.
Each record's bab matches the coverage index, retains the (unchanged) candidate by hash (== live 189
candidate == backlog existing-candidate == semantic-QA hash), and links to its semantic-QA finding
(alignment high / completeness near_full / retain action) and its P3 backlog finding. Chinese internal /
non-official / non-binding / non-governing. No full text embedded; all P2 + P1 + P0 (data + QA), the
Chinese candidate 189, and base layers untouched; no other p3_* dirs. Exercises rejection paths.
"""

import copy
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "chinese_remediation_batches", "p3_conf_001",
                    "companies_law_m132_1443_zh_internal_confirmation_p3_conf_001.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_REMEDIATION_BATCH_P3_CONF_001_AR.md")
ARABIC = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
COV = os.path.join(ROOT, "reports", "chinese_translation_review",
                   "chinese_article_coverage_index_001_281.json")
CANDF = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                     "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")
BACKLOG = os.path.join(ROOT, "reports", "chinese_translation_review",
                       "chinese_remediation_backlog_001_281.json")
SEMQA = os.path.join(ROOT, "reports", "chinese_translation_review",
                     "chinese_internal_llm_semantic_qa_189.json")
VALIDATOR = os.path.join(ROOT, "scripts", "validate_chinese_remediation_batch_p3_conf_001.py")

ARTS = [36, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 51, 52, 53, 55, 56, 57]
DIST = {2: [36, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50], 3: [51, 52, 53, 55, 56, 57]}


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
    p = tmp_path / "p3_conf_001_mutated.json"
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
    assert _d()["expected_babs"] == [2, 3]


def test_expected_bab_distribution():
    dist = {}
    for r in _d()["records"]:
        dist.setdefault(r["bab"], []).append(r["article_number"])
    assert dist == DIST


def test_exact_record_count():
    assert _d()["article_count"] == 18
    assert len(_d()["records"]) == 18


def test_priority_and_track():
    d = _d()
    assert d["priority"] == "P3"
    assert d["remediation_track"] == "P3_retain_internal_reference"
    assert d["confirmation_action"] == "retain_as_internal_reference_no_immediate_action"
    assert d["source_basis"] == "existing_chinese_internal_candidate"
    assert d["final_p3_batch"] is True
    assert d["p3_confirmation"] is True


def test_no_new_text_no_modification():
    d = _d()
    assert d["new_chinese_text_created"] is False
    assert d["chinese_text_modified"] is False
    for r in d["records"]:
        assert r["new_chinese_text_created"] is False
        assert r["chinese_text_modified"] is False
        assert r["retained_as_internal_reference"] is True
        assert r["requires_new_chinese_text"] is False
        assert r["confirmation_status"] == "confirmed_retained_as_internal_reference"


def test_each_record_bab_matches_coverage_index():
    cov = {r["article_number"]: r for r in _read(COV)["records"]}
    for r in _d()["records"]:
        assert r["bab"] in (2, 3)
        assert r["bab"] == cov[r["article_number"]]["expected_bab_number"]


def test_candidate_retained_verbatim_by_hash():
    cand = {r["article_number"]: r for r in _read(CANDF)["records"]}
    for r in _d()["records"]:
        c = cand[r["article_number"]]
        assert r["confirmed_candidate_hash_sha256"] == c["chinese_text_hash_sha256"]
        assert r["confirmed_candidate_record_id"] == c["record_id"]


def test_hash_consistent_across_backlog_and_semantic_qa():
    cand = {r["article_number"]: r for r in _read(CANDF)["records"]}
    bk = {r["article_number"]: r for r in _read(BACKLOG)["records"]}
    sq = {r["article_number"]: r for r in _read(SEMQA)["records"]}
    for n in ARTS:
        h = cand[n]["chinese_text_hash_sha256"]
        assert bk[n]["existing_chinese_candidate_hash_sha256"] == h
        assert sq[n]["chinese_text_hash_sha256"] == h


def test_semantic_qa_finding_reconfirmed():
    sq = {r["article_number"]: r for r in _read(SEMQA)["records"]}
    for r in _d()["records"]:
        s = sq[r["article_number"]]
        assert r["semantic_alignment_rating"] == s["semantic_alignment_rating"] == "high"
        assert r["legal_completeness_rating"] == s["legal_completeness_rating"] == "near_full"
        assert r["semantic_qa_recommended_action"] == s["recommended_action"] == \
            "retain_as_internal_reference_candidate"


def test_all_scope_articles_are_p3_in_backlog():
    bk = {r["article_number"]: r for r in _read(BACKLOG)["records"]}
    for r in _d()["records"]:
        b = bk[r["article_number"]]
        assert b["current_priority"] == "P3"
        assert b["remediation_track"] == "P3_retain_internal_reference"
        assert r["backlog_remediation_action"] == b["remediation_action"]
        assert r["backlog_current_blocker"] == b["current_blocker"]


def test_official_status_boundaries():
    ofs = _d()["official_status"]
    for f in ("official_government_publication", "official_translation_claimed",
              "official_adoption_claimed", "chinese_official", "chinese_binding",
              "chinese_governing"):
        assert ofs[f] is False
    assert ofs["not_legal_advice"] is True


def test_no_official_binding_governing_or_full_layer_claim():
    d = _d()
    for f in ("official_chinese_translation_claimed", "chinese_binding_claimed",
              "chinese_governing_claimed", "full_chinese_translation_claimed",
              "full_chinese_281_layer_created", "trilingual_alignment_created"):
        assert d[f] is False


def test_no_full_arabic_english_or_candidate_text_embedded():
    ar = {r["article_number"]: r for r in _read(ARABIC)["records"]}
    cand = {r["article_number"]: r for r in _read(CANDF)["records"]}
    blob = json.dumps(_d(), ensure_ascii=False)
    for n in ARTS:
        assert ar[n]["official_text_ar"] not in blob
        assert cand[n]["chinese_text"] not in blob


def test_all_p2_p1_data_unchanged():
    for sub, cnt in {"p1_001": 20, "p1_002": 20, "p1_003": 20, "p1_004": 16,
                     "p2_001": 20, "p2_002": 20, "p2_003": 20, "p2_004": 20, "p2_005": 15}.items():
        p = os.path.join(ROOT, "data", "chinese_remediation_batches", sub,
                         "companies_law_m132_1443_zh_internal_remediation_%s.json" % sub)
        assert len(_read(p)["records"]) == cnt


def test_all_p2_qa_unchanged():
    for fn in ("chinese_remediation_batch_p2_001_qa.json", "chinese_remediation_batch_p2_002_qa.json",
               "chinese_remediation_batch_p2_003_qa.json", "chinese_remediation_batch_p2_004_qa.json",
               "chinese_remediation_batch_p2_005_qa.json"):
        qa = _read(os.path.join(ROOT, "reports", "chinese_translation_review", fn))
        assert qa["final_status"] == "QA_PASS"


def test_candidate_189_unchanged():
    assert len(_read(CANDF)["records"]) == 189


def test_only_authorized_dirs():
    allowed = ("p1_001", "p1_002", "p1_003", "p1_004", "p2_001", "p2_002", "p2_003", "p2_004",
               "p2_005", "p3_conf_001")
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
        if r["article_number"] == 36:
            r["bab"] = 3  # art 36 is Bab 2
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_candidate_hash_tamper(tmp_path):
    doc = copy.deepcopy(_d())
    doc["records"][0]["confirmed_candidate_hash_sha256"] = "0" * 64
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_new_text_created_true(tmp_path):
    doc = copy.deepcopy(_d())
    doc["records"][0]["new_chinese_text_created"] = True
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_official_claim_true(tmp_path):
    doc = copy.deepcopy(_d())
    doc["official_chinese_translation_claimed"] = True
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0


def test_reject_wrong_track(tmp_path):
    doc = copy.deepcopy(_d())
    doc["remediation_track"] = "P2_expansion_needed"
    assert _run(_write_tmp(tmp_path, doc)).returncode != 0
