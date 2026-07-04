"""Chinese remediation backlog + batch plan + source-packet manifest tests (planning only).

Converts the QA/gap plan into an actionable remediation backlog (281), deterministic batches
(<=20), and a source-packet manifest for future remediation PRs. NO Chinese generated/corrected;
no full Arabic/English text duplicated; protected layers untouched. Chinese is internal / non-
official / non-binding; Arabic governs. Reads committed artifacts.
"""

import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RV = os.path.join(ROOT, "reports", "chinese_translation_review")
BACKLOG = os.path.join(RV, "chinese_remediation_backlog_001_281.json")
BATCH = os.path.join(RV, "chinese_remediation_batch_plan.json")
MANIFEST = os.path.join(RV, "chinese_remediation_source_packet_manifest.json")
MD = os.path.join(RV, "CHINESE_REMEDIATION_BACKLOG_AND_SOURCE_PACKET_PLAN_AR.md")
CANDF = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                     "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")
ARABIC = os.path.join(ROOT, "data", "official_arabic_legal_llm",
                      "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")
ENGLISH = os.path.join(ROOT, "data", "official_english_legal_llm",
                       "companies_law_m132_1443_official_english_legal_llm_001_281.json")
GEN = os.path.join(ROOT, "scripts", "gen_chinese_remediation_backlog_source_packet_plan.py")

EXP = {"P0": 92, "P1": 76, "P2": 95, "P3": 18}
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")
FORBIDDEN_KEYS = {"chinese_text", "corrected_chinese_text", "generated_chinese_text",
                  "arabic_text", "english_text", "official_text_ar", "legal_rule_text_en"}


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def test_output_files_exist():
    for p in (BACKLOG, BATCH, MANIFEST, MD):
        assert os.path.exists(p), p


def test_backlog_281_records():
    bl = _read(BACKLOG)
    assert bl["total_articles"] == 281
    assert len(bl["records"]) == 281
    nums = [r["article_number"] for r in bl["records"]]
    assert nums == list(range(1, 282))
    assert len(set(nums)) == len(nums)


def test_exact_priority_counts():
    bl = _read(BACKLOG)
    for p, exp in EXP.items():
        assert bl["%s_count" % p.lower()] == exp
    assert bl["remediation_required_count"] == 263
    assert bl["no_action_internal_reference_count"] == 18
    actual = {}
    for r in bl["records"]:
        actual[r["current_priority"]] = actual.get(r["current_priority"], 0) + 1
    assert actual == EXP


def test_p0_p1_p2_block_and_p3_internal_only():
    for r in _read(BACKLOG)["records"]:
        pr = r["current_priority"]
        if pr in ("P0", "P1", "P2"):
            assert r["should_block_full_chinese_layer"] is True
            assert r["should_block_trilingual_alignment"] is True
            assert r["requires_new_chinese_text"] is True
        else:
            assert r["should_block_full_chinese_layer"] is False
            assert r["should_block_trilingual_alignment"] is True
            assert r["requires_new_chinese_text"] is False


def test_batches_size_and_order_and_coverage():
    bp = _read(BATCH)
    assert bp["batch_count"] == len(bp["batches"])
    assert bp["p0_batch_count"] + bp["p1_batch_count"] + bp["p2_batch_count"] \
        + bp["p3_confirmation_batch_count"] == bp["batch_count"]
    seen = []
    prio_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    last = -1
    for b in bp["batches"]:
        assert b["article_count"] == len(b["article_numbers"])
        assert b["article_count"] <= 20
        seen.extend(b["article_numbers"])
        assert prio_order[b["priority"]] >= last
        last = max(last, prio_order[b["priority"]])
    assert sorted(seen) == list(range(1, 282))
    assert len(set(seen)) == len(seen)


def test_no_generated_or_corrected_or_foreign_text_fields():
    def keys(obj, acc):
        if isinstance(obj, dict):
            for k, v in obj.items():
                acc.add(k)
                keys(v, acc)
        elif isinstance(obj, list):
            for v in obj:
                keys(v, acc)
    acc = set()
    for p in (BACKLOG, BATCH, MANIFEST):
        keys(_read(p), acc)
    assert not (acc & FORBIDDEN_KEYS), acc & FORBIDDEN_KEYS


def test_no_full_arabic_or_english_text_duplicated():
    ar = _read(ARABIC)["records"][0]["official_text_ar"]
    en = _read(ENGLISH)["records"][0]["legal_rule_text_en"]
    blob = json.dumps(_read(BACKLOG), ensure_ascii=False)
    assert ar not in blob and en not in blob


def test_trust_posture_and_no_overclaims():
    bl = _read(BACKLOG)
    for f in ("full_chinese_translation_claimed", "official_chinese_translation_claimed",
              "chinese_binding_claimed", "chinese_governing_claimed", "corrected_chinese_created",
              "generated_chinese_created", "arabic_used_to_generate_chinese",
              "english_used_to_generate_chinese"):
        assert bl[f] is False
    blob = (json.dumps(bl, ensure_ascii=False) + json.dumps(_read(BATCH), ensure_ascii=False)
            + json.dumps(_read(MANIFEST), ensure_ascii=False)).lower()
    for term in BANNED:
        assert term not in blob, term


def test_manifest_forbids_full_layer_and_alignment():
    mf = _read(MANIFEST)
    for key in ("source_files", "protected_files", "future_batch_requirements",
                "forbidden_actions", "required_trust_posture", "validation_requirements"):
        assert key in mf
    forb = json.dumps(mf["forbidden_actions"], ensure_ascii=False).lower()
    assert "full chinese 281 layer" in forb
    assert "trilingual alignment" in forb


def test_protected_layers_unchanged():
    assert len(_read(CANDF)["records"]) == 189
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    assert len(zh) == 5 and sum(len(_read(p)["records"]) for p in zh) == 23
    assert len(_read(ARABIC)["records"]) == 281
    assert len(_read(ENGLISH)["records"]) == 281
    er = _read(os.path.join(ROOT, "data", "english_reference",
                            "companies_law_m132_1443_en_reference_001_281.json"))
    assert len(er["records"]) == 281
    c = _read(os.path.join(ROOT, "data", "official_arabic",
                           "companies_law_m132_1443_official_arabic_user_provided.json"))
    assert len(c["articles"]) == 281 and c["verification_status"] == "ingested_unverified"
    assert len(glob.glob(os.path.join(ROOT, "data", "chinese_translation_sources",
                                      "bab*_zh_source_extracted_articles_*.json"))) == 14


def test_generator_is_byte_stable():
    targets = [BACKLOG, BATCH, MANIFEST, MD]
    before = {p: open(p, "rb").read() for p in targets}
    res = subprocess.run([sys.executable, GEN], capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    for p in targets:
        assert open(p, "rb").read() == before[p], "not byte-stable: %s" % os.path.basename(p)


def test_validator_passes():
    res = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts",
                                      "validate_chinese_remediation_backlog_source_packet_plan.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
