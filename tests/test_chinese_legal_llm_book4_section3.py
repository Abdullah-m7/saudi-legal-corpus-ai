"""Chinese Legal LLM-ready layer — Book Four Section 3 (General Assemblies / 股东大会).

5 article_reference records for the source-preserved provision groups [85,87], [92,93],
[99], [101], [102] (the source groups Articles 85 & 87 and 92 & 93 into one provision each —
preserved exactly). `legal_rule_text_zh` is copied verbatim from each provision's
`chinese_translation` field in data/articles/book4_provisions_084_102.json. There is NO
`legal_rule_summary_zh` / new/machine translation / generated summary. Chinese is an internal
working translation only; Arabic governs. Articles 84, 89 and 100 remain owner-reconciled
excluded. NOT full Chinese Legal LLM coverage.
"""

import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "chinese_legal_llm.schema.json")
LLM_DIR = os.path.join(ROOT, "data", "chinese_legal_llm")
DATA = os.path.join(LLM_DIR, "book4_section3_zh_legal_llm.json")
PROVISIONS = os.path.join(ROOT, "data", "articles", "book4_provisions_084_102.json")

SOURCE_FIELD = "chinese_translation"
GROUPS = [[85, 87], [92, 93], [99], [101], [102]]
COVERED = {85, 87, 92, 93, 99, 101, 102}
UNCOVERED = [84, 86, 88, 89, 90, 91, 94, 95, 96, 97, 98, 100]


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _records():
    return _read(DATA)["records"]


def _provtext():
    return {tuple(p["source_article_numbers"]): p[SOURCE_FIELD]
            for p in _read(PROVISIONS)["provisions"]}


def _rec(group):
    return next(r for r in _records() if r["article_numbers"] == group)


def _text(group):
    return _rec(group)["legal_rule_text_zh"]


# -- existence + scope ------------------------------------------------------
def test_data_exists():
    assert os.path.exists(DATA)


def test_exactly_five_records():
    assert len(_records()) == 5


def test_article_groups_exact():
    assert [r["article_numbers"] for r in _records()] == GROUPS


def test_no_records_for_uncovered_section3():
    covered = {n for r in _records() for n in r["article_numbers"]}
    assert not (covered & set(UNCOVERED)), covered
    assert covered == COVERED


def test_articles_84_89_100_specifically_excluded():
    covered = {n for r in _records() for n in r["article_numbers"]}
    for excluded in (84, 89, 100):
        assert excluded not in covered, excluded


def test_record_type_and_book():
    for r in _records():
        assert r["record_type"] == "article_reference", r["record_id"]
        assert r["book"] == 4, r["record_id"]


# -- schema + verbatim source field -----------------------------------------
def test_records_pass_schema():
    schema = _read(SCHEMA)
    try:
        import jsonschema
        v = jsonschema.Draft7Validator(schema)
        for r in _records():
            errs = [e.message for e in v.iter_errors(r)]
            assert not errs, (r["record_id"], errs)
    except ImportError:
        for r in _records():
            for k in schema["required"]:
                assert k in r, (r["record_id"], k)


def test_legal_rule_text_zh_verbatim_from_provision_source_field():
    prov = _provtext()
    for r in _records():
        key = tuple(r["article_numbers"])
        assert key in prov, key
        assert r["legal_rule_text_zh"] == prov[key], r["record_id"]


def test_no_legal_rule_summary_zh_field():
    for r in _records():
        assert "legal_rule_summary_zh" not in r, r["record_id"]
    assert "legal_rule_summary_zh" not in open(DATA, encoding="utf-8").read()


def test_no_generated_summary_fields():
    for r in _records():
        for k in r:
            assert "summary" not in k.lower(), (r["record_id"], k)


# -- trust posture ----------------------------------------------------------
def test_trust_fields():
    for r in _records():
        st = r["source_trust"]
        assert st["chinese_source_status"] == "internal_working_translation", r["record_id"]
        assert st["governing_text_language"] == "ar", r["record_id"]
        assert st["official_text_check"] == "needs_check", r["record_id"]
        assert st["manual_review_status"] == "needs_manual_check", r["record_id"]
        assert "book4_provisions_084_102.json" in st["source_reference_file"], r["record_id"]


def test_no_forbidden_overclaim_terms():
    blob = open(DATA, encoding="utf-8").read().lower()
    for term in ("official chinese translation", "verified chinese translation",
                 "chinese is binding", "governing chinese text", "binding chinese text",
                 "official legal advice", "official_translation"):
        assert term not in blob, term


# -- GENERIC metadata-accuracy guard (traceable to the provision's Chinese text) --
def _cjk_runs(s):
    return re.findall(r"[一-鿿]{2,}", s)


def _traceable(phrase, text):
    for run in _cjk_runs(phrase):
        if len(run) >= 3:
            for i in range(len(run) - 2):
                if run[i:i + 3] in text:
                    return True
        if run in text:
            return True
    return False


def test_all_derived_zh_fields_traceable_to_source_text():
    fields = ("actors_zh", "rights_zh", "obligations_zh", "prohibitions_zh",
              "conditions_zh", "exceptions_zh", "legal_effects_zh", "liability_zh",
              "deadlines_zh", "competent_authorities_zh", "cross_references_zh")
    for r in _records():
        text = r["legal_rule_text_zh"]
        for f in fields:
            for phrase in r[f]:
                assert _traceable(phrase, text), (r["record_id"], f, phrase)


def test_keywords_zh_reuse_provision_keywords():
    prov = {tuple(p["source_article_numbers"]): p.get("llm", {}).get("keywords_zh", [])
            for p in _read(PROVISIONS)["provisions"]}
    for r in _records():
        assert r["keywords_zh"] == prov[tuple(r["article_numbers"])], r["record_id"]


def test_monetary_thresholds_descriptions_are_substrings():
    for r in _records():
        text = r["legal_rule_text_zh"]
        for m in r["monetary_thresholds"]:
            assert m["description_zh"] in text, (r["record_id"], m["description_zh"])


# -- TARGETED per-group accuracy (Chinese substring checks against source) ---
def test_group_85_87_assembly_powers():
    r = _rec([85, 87])
    text = _text([85, 87])
    actors = " ".join(r["actors_zh"])
    assert "普通大会" in actors and "非常大会" in actors
    assert "普通大会" in text and "非常大会" in text and "职权" in text
    # OGM powers (electing/removing directors) and EGM power (amending the bylaws).
    assert any("董事" in x for x in r["rights_zh"])
    assert "解聘董事" in text
    assert any("修改公司章程" in x for x in r["legal_effects_zh"])
    assert "修改公司章程" in text


def test_group_92_93_quorum_and_majority():
    r = _rec([92, 93])
    text = _text([92, 93])
    conds = "".join(r["conditions_zh"])
    assert "四分之一" in conds or "法定人数" in text
    assert "四分之一股份" in text
    eff = "".join(r["legal_effects_zh"])
    assert "四分之三" in eff
    assert "四分之三多数" in text
    amounts = {m["amount"] for m in r["monetary_thresholds"]}
    assert 0.75 in amounts


def test_group_99_resolution_challenge():
    r = _rec([99])
    text = _text([99])
    assert any("撤销" in x for x in r["rights_zh"])
    assert "撤销" in text
    dl = "".join(r["deadlines_zh"])
    assert "九十" in dl or "90" in dl
    assert "九十（90）日" in text
    eff = "".join(r["legal_effects_zh"])
    assert "善意第三人" in eff
    assert "善意第三人" in text


def test_group_101_circulated_resolution_percentage():
    r = _rec([101])
    text = _text([101])
    eff = "".join(r["legal_effects_zh"])
    assert "传阅" in eff
    assert "传阅" in text
    # 75% voting-power threshold for EGM matters, supported by the source text.
    assert "百分之七十五（75%）" in text
    descs = "".join(m["description_zh"] for m in r["monetary_thresholds"])
    assert "75%" in descs or "百分之七十五" in descs
    assert 0.75 in {m["amount"] for m in r["monetary_thresholds"]}


def test_group_102_company_inspection_minority_shareholder():
    r = _rec([102])
    text = _text([102])
    assert any("检查" in x for x in r["rights_zh"])
    assert "检查" in text
    conds = "".join(r["conditions_zh"])
    assert "百分之五" in conds or "5%" in conds
    assert "百分之五（5%）" in text
    assert "主管司法机关" in "".join(r["competent_authorities_zh"])
    assert "主管司法机关" in text


# -- only repo book4 Sections 1-5 Chinese LLM files; Section 3 present -------
# Sections 4-5 were added as sanctioned extensions (repo book4 Sections 1-5 now complete);
# the Section 3 file must still be present and unchanged, and no file outside Sections 1-5
# may exist.
_ALLOWED_ZH_LLM = {"book4_section1_zh_legal_llm.json", "book4_section2_zh_legal_llm.json",
                   "book4_section3_zh_legal_llm.json", "book4_section4_zh_legal_llm.json",
                   "book4_section5_zh_legal_llm.json"}


def test_only_sections_1_2_3_chinese_llm_files():
    files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(LLM_DIR, "*_zh_legal_llm.json")))
    assert "book4_section3_zh_legal_llm.json" in files, files
    assert set(files) <= _ALLOWED_ZH_LLM, files


def test_section1_chinese_llm_unchanged():
    s1 = _read(os.path.join(LLM_DIR, "book4_section1_zh_legal_llm.json"))
    assert [r["article_numbers"] for r in s1["records"]] == [[58], [59], [60], [66]]


def test_section2_chinese_llm_unchanged():
    s2 = _read(os.path.join(LLM_DIR, "book4_section2_zh_legal_llm.json"))
    assert [r["article_numbers"] for r in s2["records"]] == [[67, 68], [71], [72], [75], [77]]


def test_no_books_1_3_or_section_4_5_chinese_llm_files():
    for f in glob.glob(os.path.join(LLM_DIR, "*_zh_legal_llm.json")):
        assert os.path.basename(f) in _ALLOWED_ZH_LLM, os.path.basename(f)


# -- existing layers unchanged ----------------------------------------------
def test_english_legal_llm_unchanged_8_files_87_records():
    d = os.path.join(ROOT, "data", "english_legal_llm")
    files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(d, "*_en_legal_llm.json")))
    assert files == ["book1_en_legal_llm.json",
                     "book2_en_legal_llm.json",
                     "book3_en_legal_llm.json",
                     "book4_section1_en_legal_llm.json",
                     "book4_section2_en_legal_llm.json",
                     "book4_section3_en_legal_llm.json",
                     "book4_section4_en_legal_llm.json",
                     "book4_section5_en_legal_llm.json"], files
    total = sum(len(_read(p)["records"]) for p in glob.glob(os.path.join(d, "*_en_legal_llm.json")))
    assert total == 87, total


def test_arabic_legal_llm_unchanged():
    layer = os.path.join(ROOT, "data", "arabic_legal_llm")
    s3 = _read(os.path.join(layer, "book4_section3_ar_legal_llm.json"))
    assert [r["article_numbers"] for r in s3["records"]] == [[85, 87], [92, 93], [99], [101], [102]]
    for fname, exp in (("book1_ar_legal_llm.json", list(range(1, 35))),
                       ("book2_ar_legal_llm.json", list(range(35, 51))),
                       ("book3_ar_legal_llm.json", list(range(51, 58)))):
        doc = _read(os.path.join(layer, fname))
        assert [r["article_numbers"][0] for r in doc["records"]] == exp, fname


def test_english_reference_unchanged():
    ref = os.path.join(ROOT, "data", "english_reference")
    for fname, exp in (("book4_section3_en_reference.json", [85, 87, 92, 93, 99, 101, 102]),
                       ("book4_section5_en_reference.json", [123, 124, 126, 127, 128, 129, 130, 132, 133])):
        doc = _read(os.path.join(ref, fname))
        assert [r["article_number"] for r in doc["records"]] == exp, fname


def test_book4_section3_provisions_unchanged():
    doc = _read(PROVISIONS)
    assert [p["source_article_numbers"] for p in doc["provisions"]] == GROUPS
    for p in doc["provisions"]:
        assert p[SOURCE_FIELD].strip(), p["source_article_numbers"]


def test_no_book4_articles_files():
    for f in os.listdir(os.path.join(ROOT, "data", "articles")):
        assert not f.startswith("book4_articles_"), f


def test_no_full_book4_content():
    for p in ("content/ar/book4.md", "content/zh/book4.md", "content/bilingual/book4_bilingual.md"):
        assert not os.path.exists(os.path.join(ROOT, p)), p


def test_arabic_canonical_unchanged():
    for fname, expected in (("book1_articles_001_034.json", list(range(1, 35))),
                            ("book2_articles_035_050.json", list(range(35, 51))),
                            ("book3_articles_051_057.json", list(range(51, 58)))):
        doc = _read(os.path.join(ROOT, "data", "articles", fname))
        nums = [a["article_number"] for a in doc["articles"]]
        assert nums == expected, fname
        for a in doc["articles"]:
            assert a["chinese_translation"].strip(), (fname, a["article_number"])


def test_validator_script_passes():
    import subprocess
    import sys
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "validate_chinese_legal_llm.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
