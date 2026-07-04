"""Chinese internal LLM-ready candidate layer tests (isolable-source articles, 189).

Builds an internal Chinese LLM/RAG candidate layer ONLY for the 189 articles with isolable per-
article Chinese source text; the 92 thematic-summary articles are excluded (never fabricated).
chinese_text is copied verbatim from the extracted source (hash-checked); nothing is translated,
expanded, or corrected, and no Chinese is generated from Arabic/English. Chinese is internal /
non-official / non-binding; Arabic governs. Reads committed artifacts.
"""

import glob
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "chinese_internal_legal_llm.schema.json")
DATA = os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                    "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")
MD = os.path.join(ROOT, "reports", "chinese_translation_review",
                  "CHINESE_INTERNAL_LLM_READY_ISOLABLE_189_AR.md")
IDX = os.path.join(ROOT, "reports", "chinese_translation_review",
                   "chinese_article_coverage_index_001_281.json")
SRC_DIR = os.path.join(ROOT, "data", "chinese_translation_sources")
GEN = os.path.join(ROOT, "scripts", "gen_chinese_internal_legal_llm_isolable_source_articles.py")

EXPECTED = 189
EXCLUDED = 92
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _doc():
    return _read(DATA)


def _recs():
    return _doc()["records"]


def _src():
    out = {}
    for f in glob.glob(os.path.join(SRC_DIR, "bab*_zh_source_extracted_articles_*.json")):
        for r in _read(f)["records"]:
            out[r["article_number"]] = r.get("chinese_text") or ""
    return out


def test_files_exist():
    assert os.path.exists(SCHEMA) and os.path.exists(DATA) and os.path.exists(MD)


def test_189_records_92_excluded_partition():
    d = _doc()
    assert d["candidate_record_count"] == EXPECTED
    assert d["expected_candidate_record_count"] == EXPECTED
    assert len(d["records"]) == EXPECTED
    assert d["excluded_article_count"] == EXCLUDED
    assert len(d["excluded_articles"]) == EXCLUDED
    incl = {r["article_number"] for r in d["records"]}
    excl = set(d["excluded_articles"])
    assert len(incl) == EXPECTED
    assert not (incl & excl)
    assert incl | excl == set(range(1, 282))


def test_schema_validates():
    import jsonschema
    schema = _read(SCHEMA)
    v = jsonschema.Draft7Validator(schema)
    for r in _recs():
        errs = list(v.iter_errors(r))
        assert not errs, (r["article_number"], [e.message for e in errs][:2])


def test_selection_matches_coverage_index():
    idx = _read(IDX)
    nonempty = {r["article_number"] for r in idx["records"] if r["chinese_text_nonempty"]}
    empty = {r["article_number"] for r in idx["records"] if not r["chinese_text_nonempty"]}
    incl = {r["article_number"] for r in _recs()}
    assert incl == nonempty
    assert set(_doc()["excluded_articles"]) == empty


def test_chinese_text_exact_and_hash():
    src = _src()
    for r in _recs():
        n = r["article_number"]
        assert r["chinese_text"].strip()
        assert r["chinese_text"] == src[n]
        assert r["chinese_text_hash_sha256"] == hashlib.sha256(
            r["chinese_text"].encode("utf-8")).hexdigest()


def test_mechanical_metadata():
    for r in _recs():
        n = r["article_number"]
        assert r["record_id"] == "zh-int-companies-art-%03d" % n
        assert r["article_path"] == "companies_law/articles/%03d/zh/internal" % n
        assert r["llm_title_zh"].startswith("公司法 第%d条" % n)
        assert ("沙特公司法 第%d条" % n) in r["search_queries_zh"]
        assert isinstance(r["keywords_zh"], list)


def test_trust_posture_and_no_llm_ready():
    for r in _recs():
        st = r["source_trust"]
        assert st["chinese_source_status"] == "internal_working_translation_source"
        assert st["official_translation"] is False
        assert st["not_binding"] is True
        assert st["governing_text_language"] == "ar"
        assert st["full_translation_claimed"] is False
        assert st["internal_reference_only"] is True
        assert st["arabic_governs"] is True
        assert r["source_coverage"]["llm_ready_as_full_translation"] is False


def test_top_level_no_overclaims():
    d = _doc()
    assert d["full_chinese_translation_claimed"] is False
    assert d["official_chinese_translation_claimed"] is False
    assert d["chinese_binding_claimed"] is False
    assert d["chinese_governing_claimed"] is False
    blob = json.dumps(d, ensure_ascii=False).lower()
    for term in BANNED:
        assert term not in blob, term


def test_no_generated_or_foreign_fields():
    for r in _recs():
        for k in list(r.keys()) + list(r["source_trust"].keys()) + list(r["source_coverage"].keys()):
            kl = k.lower()
            assert "official_text_ar" not in kl
            assert "legal_rule_text_en" not in kl
            assert "generated_from" not in kl


def test_old_chinese_llm_and_protected_layers_unchanged():
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


def test_generator_is_byte_stable():
    before = (open(DATA, "rb").read(), open(MD, "rb").read())
    res = subprocess.run([sys.executable, GEN], capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    after = (open(DATA, "rb").read(), open(MD, "rb").read())
    assert before == after, "candidate layer is not byte-stable / idempotent"


def test_validator_passes():
    res = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts",
                                      "validate_chinese_internal_legal_llm_isolable_source_articles.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
