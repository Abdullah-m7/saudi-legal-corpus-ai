"""Tests for the sovereign legal corpus factory FOUNDATION (docs, schemas, profile, config, seed).

Foundation only: reusable doctrine, architecture, schemas, a Saudi Companies Law profile, one example
P0-005 QA batch config, and a seed terminology bank for a multilingual, LLM-ready,
official-source-based Saudi legal corpus for AI. Review model: the official Arabic source governs;
English and Chinese are reference layers; the repository owner has a legal background (bachelor_of_law)
and runs active repository review (source_basis / repository_legal_review / external_legal_review /
official_status); external legal review is optional for enterprise/official adoption and not required
for repository use. No full Chinese 281 layer; no trilingual alignment; no P1/P2/P3. Reads committed
artifacts.
"""

import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCTRINE = os.path.join(ROOT, "docs", "SOVEREIGN_LEGAL_CORPUS_FACTORY_DOCTRINE_AR.md")
ARCH = os.path.join(ROOT, "docs", "LEGAL_CORPUS_FACTORY_ARCHITECTURE_AR.md")
SCHEMA_DIR = os.path.join(ROOT, "schemas", "legal_corpus_factory")
PROFILE = os.path.join(ROOT, "data", "legal_corpus_factory", "law_profiles",
                       "sa_companies_law_m132_1443.profile.json")
BATCH = os.path.join(ROOT, "data", "legal_corpus_factory", "batch_configs",
                     "sa_companies_law_m132_1443_p0_005_qa.batch.json")
TERMS = os.path.join(ROOT, "data", "legal_corpus_factory", "terminology",
                     "sa_companies_law_core_terms_ar_en_zh_seed.json")
P0_005_QA = os.path.join(ROOT, "reports", "chinese_translation_review",
                         "chinese_remediation_batch_p0_005_qa.json")
VALIDATOR = os.path.join(ROOT, "scripts", "validate_legal_corpus_factory_foundation.py")

ARTS = [188, 189, 190, 191, 192, 194, 218, 220, 260, 261, 262, 274]
DIST = {"7": [188, 189, 190, 191, 192, 194], "9": [218], "10": [220],
        "13": [260, 261, 262], "14": [274]}
BANNED = ("official chinese translation", "chinese is official", "chinese is binding",
          "chinese is governing", "full verified chinese translation",
          "governing chinese text", "binding chinese text")


def _read(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _rc(p):
    return len(_read(p)["records"])


def _run():
    return subprocess.run([sys.executable, VALIDATOR], capture_output=True, text=True)


def test_validator_passes():
    res = _run()
    assert res.returncode == 0, res.stdout + res.stderr


def test_law_profile_exists_and_parses():
    assert os.path.exists(PROFILE)
    prof = _read(PROFILE)
    assert prof["law_id"] == "sa_companies_law_m132_1443"
    assert prof["governing_language"] == "ar"


def test_law_profile_counts_match_repository():
    prof = _read(PROFILE)
    assert prof["article_count"] == 281
    assert _rc(os.path.join(ROOT, "data", "official_arabic_legal_llm",
                            "companies_law_m132_1443_official_arabic_legal_llm_001_281.json")) == 281
    assert _rc(os.path.join(ROOT, "data", "official_english_legal_llm",
                            "companies_law_m132_1443_official_english_legal_llm_001_281.json")) == 281
    assert _rc(os.path.join(ROOT, "data", "english_reference",
                            "companies_law_m132_1443_en_reference_001_281.json")) == 281
    assert _rc(os.path.join(ROOT, "data", "chinese_internal_legal_llm",
                            "companies_law_m132_1443_chinese_internal_legal_llm_isolable_source_articles.json")) == 189
    zh = glob.glob(os.path.join(ROOT, "data", "chinese_legal_llm", "*_zh_legal_llm.json"))
    assert len(zh) == 5 and sum(_rc(x) for x in zh) == 23
    assert len(glob.glob(os.path.join(ROOT, "data", "chinese_translation_sources",
                                      "bab*_zh_source_extracted_articles_*.json"))) == 14
    sf = prof["source_files"]
    assert sf["arabic_full_llm"]["records"] == 281
    assert sf["english_full_llm"]["records"] == 281
    assert sf["english_reference"]["records"] == 281
    assert sf["chinese_internal_candidate_isolable"]["records"] == 189
    assert sf["old_chinese_legal_llm"]["files"] == 5 and sf["old_chinese_legal_llm"]["records"] == 23
    assert sf["chinese_source_extracted"]["files"] == 14
    assert sf["ocr_manual_review_queue"]["entries"] == 281


def test_law_profile_does_not_overclaim_chinese():
    prof = _read(PROFILE)
    claims = prof["claims"]
    assert claims["full_chinese_281_layer_created"] is False
    assert claims["official_chinese_translation_claimed"] is False
    assert claims["chinese_binding_claimed"] is False
    assert claims["chinese_governing_claimed"] is False
    assert claims["trilingual_alignment_created"] is False
    lh = prof["legal_hierarchy"]
    assert lh["arabic"] == "governing"
    assert lh["chinese"] == "internal_reference_only"
    assert lh["chinese_official"] is False
    assert lh["chinese_binding"] is False
    assert lh["chinese_governing"] is False
    blob = json.dumps(prof, ensure_ascii=False).lower()
    for term in BANNED:
        assert term not in blob, term


def test_repository_legal_review_model():
    prof = _read(PROFILE)
    sb = prof["source_basis"]
    assert sb["status"] == "official_source_based"
    assert sb["governing_source_language"] == "ar"
    rlr = prof["repository_legal_review"]
    assert rlr["repository_legal_review_status"] == "repository_owner_review_active"
    assert isinstance(rlr["repository_review_scope"], list) and rlr["repository_review_scope"]
    assert prof["release_policy"]["public_release_created"] is False


def test_repository_owner_legal_background_fields():
    rlr = _read(PROFILE)["repository_legal_review"]
    assert rlr["repository_owner_has_legal_background"] is True
    assert rlr["repository_owner_legal_qualification"] == "bachelor_of_law"


def test_external_legal_review_optional_model():
    elr = _read(PROFILE)["external_legal_review"]
    assert elr["external_legal_review_required_for_repository_use"] is False
    assert elr["external_legal_review_optional_for_enterprise_or_official_adoption"] is True
    assert elr["external_legal_review_status"] == "not_performed"


def test_no_official_government_adoption_claim():
    ost = _read(PROFILE)["official_status"]
    assert ost["official_government_publication"] is False
    assert ost["official_translation_claimed"] is False
    assert ost["official_adoption_claimed"] is False
    assert ost["not_legal_advice"] is True


def test_batch_config_matches_existing_qa_scope():
    bc = _read(BATCH)
    qa = _read(P0_005_QA)
    assert bc["batch_id"] == "P0-005"
    assert bc["stage"] == "CHINESE_REMEDIATION_BATCH_P0_005_QA"
    assert bc["scope_articles"] == ARTS == qa["scope_articles"]


def test_batch_config_babs_and_distribution_match_existing_qa():
    bc = _read(BATCH)
    qa = _read(P0_005_QA)
    assert bc["expected_babs"] == [7, 9, 10, 13, 14] == qa["expected_babs"]
    bc_dist = {str(k): list(v) for k, v in bc["expected_bab_distribution"].items()}
    qa_dist = {str(k): list(v) for k, v in qa["expected_bab_distribution"].items()}
    assert bc_dist == DIST == qa_dist


def test_terminology_seed_entries_have_required_fields_and_repository_review_status():
    allowed = {"seed_repository_owner_review_active", "seed_pending_repository_owner_review"}
    terms = _read(TERMS)["terms"]
    assert len(terms) >= 20
    for t in terms:
        for f in ("term_ar", "term_en", "term_zh", "domain_context", "notes_ar", "status"):
            assert f in t, (f, t.get("term_ar"))
        assert t["status"] in allowed, t.get("term_ar")


def test_schemas_exist_and_parse():
    for name in ("law_profile.schema.json", "batch_config.schema.json",
                 "provenance_passport.schema.json"):
        sc = _read(os.path.join(SCHEMA_DIR, name))
        assert sc["type"] == "object"
        assert "properties" in sc and "required" in sc


def test_doctrine_exists_and_says_arabic_source_governs():
    assert os.path.exists(DOCTRINE)
    with open(DOCTRINE, encoding="utf-8") as fh:
        text = fh.read()
    assert ("المصدر العربي الرسمي هو النص الحاكم" in text
            or "المصدر العربي الرسمي حاكم" in text)


def test_doctrine_does_not_imply_external_review_required_for_use():
    with open(DOCTRINE, encoding="utf-8") as fh:
        text = fh.read()
    # external review is stated as OPTIONAL, and the old blanket framing is gone. Forbidden phrases
    # are assembled from fragments so this test's own source does not contain the full literals.
    assert "المراجعة الخارجية اختيارية" in text
    _phlr = "pending_" + "human_legal_review"
    for stale in ("human legal review " + "remains pending", "human legal review " + "pending",
                  _phlr, "seed_" + _phlr,
                  "بانتظار مراجعة " + "قانونية بشرية", "المراجعة القانونية " + "البشرية معلّقة"):
        assert stale not in text, stale


def test_no_stale_review_framing_in_foundation_files():
    # Every new foundation file must be free of the old blanket human-legal-review framing.
    # (Fragmented literals so this test's own source cannot self-match.)
    _phlr = "pending_" + "human_legal_review"
    stale_framings = (
        "human legal review " + "remains pending",
        "human legal review " + "still pending",
        "human legal review " + "pending",
        _phlr,
        "seed_" + _phlr,
        "بانتظار مراجعة " + "قانونية بشرية",
        "المراجعة القانونية " + "البشرية معلّقة",
    )
    files = [
        os.path.join(ROOT, "docs", "SOVEREIGN_LEGAL_CORPUS_FACTORY_DOCTRINE_AR.md"),
        os.path.join(ROOT, "docs", "LEGAL_CORPUS_FACTORY_ARCHITECTURE_AR.md"),
        PROFILE, BATCH, TERMS,
        os.path.join(SCHEMA_DIR, "law_profile.schema.json"),
        os.path.join(SCHEMA_DIR, "batch_config.schema.json"),
        os.path.join(SCHEMA_DIR, "provenance_passport.schema.json"),
        os.path.join(ROOT, "scripts", "validate_legal_corpus_factory_foundation.py"),
        os.path.abspath(__file__),
    ]
    for p in files:
        with open(p, encoding="utf-8") as fh:
            text = fh.read()
        for stale in stale_framings:
            assert stale not in text, (os.path.relpath(p, ROOT), stale)
    # README: only the factory-foundation section must be clean (historical P0 notes are untouched).
    with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as fh:
        rtext = fh.read()
    marker = "## Multilingual Saudi legal corpus for AI (foundation)"
    assert marker in rtext
    seg = rtext.split(marker, 1)[1].split("\n## ", 1)[0]
    for stale in stale_framings:
        assert stale not in seg, ("README.md#foundation-section", stale)


def test_doctrine_contains_no_false_official_chinese_claim():
    with open(DOCTRINE, encoding="utf-8") as fh:
        low = fh.read().lower()
    for term in BANNED:
        assert term not in low, term


def test_architecture_exists_and_describes_reusable_components():
    assert os.path.exists(ARCH)
    with open(ARCH, encoding="utf-8") as fh:
        text = fh.read()
    for comp in ("طبقات البيانات", "ملفات تعريف الأنظمة", "إعدادات الدفعات", "بنك المصطلحات",
                 "فئات المستخدمين"):
        assert comp in text, comp


def test_no_p1_p2_p3_dirs():
    assert not glob.glob(os.path.join(ROOT, "data", "chinese_remediation_batches", "p[123]_*"))


def test_no_full_chinese_281_layer():
    prof = _read(PROFILE)
    assert prof["claims"]["full_chinese_281_layer_created"] is False
    assert not glob.glob(os.path.join(ROOT, "data", "**", "*full_chinese_281*"), recursive=True)


def test_no_trilingual_alignment():
    prof = _read(PROFILE)
    assert prof["claims"]["trilingual_alignment_created"] is False
    assert not glob.glob(os.path.join(ROOT, "data", "**", "*trilingual*"), recursive=True)
    assert not glob.glob(os.path.join(ROOT, "reports", "**", "*trilingual*"), recursive=True)


def test_validator_idempotent():
    a = _run()
    b = _run()
    assert a.returncode == 0 and b.returncode == 0
