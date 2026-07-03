"""Chinese Legal LLM-ready layer — repo book4 Section 5
(Finance, Profits, and Capital Changes / 财务、利润与资本变更).

"book4" is an internal repository label for the modeled Joint-Stock Company chapter/part
scope (repo book4 convention), not a claim about the whole Saudi Companies Law structure.

5 article_reference records for the source-preserved provision groups [123,124], [126,127],
[128,129,130], [132], [133]. `legal_rule_text_zh` is copied verbatim from each provision's
`chinese_translation` field in data/articles/book4_provisions_121_137.json. There is NO
`legal_rule_summary_zh` / new/machine translation / generated summary. Chinese is an internal
working translation only; Arabic governs. Articles 134 and 135 remain excluded
(cross-reference-only). NOT full Chinese Legal LLM coverage.
"""

import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "chinese_legal_llm.schema.json")
LLM_DIR = os.path.join(ROOT, "data", "chinese_legal_llm")
DATA = os.path.join(LLM_DIR, "book4_section5_zh_legal_llm.json")
PROVISIONS = os.path.join(ROOT, "data", "articles", "book4_provisions_121_137.json")

SOURCE_FIELD = "chinese_translation"
GROUPS = [[123, 124], [126, 127], [128, 129, 130], [132], [133]]
COVERED = {123, 124, 126, 127, 128, 129, 130, 132, 133}
UNCOVERED = [121, 122, 125, 131, 134, 135, 136, 137]

_ALLOWED_ZH_LLM = {"book4_section1_zh_legal_llm.json", "book4_section2_zh_legal_llm.json",
                   "book4_section3_zh_legal_llm.json", "book4_section4_zh_legal_llm.json",
                   "book4_section5_zh_legal_llm.json"}


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


def test_no_records_for_uncovered_section5():
    covered = {n for r in _records() for n in r["article_numbers"]}
    assert not (covered & set(UNCOVERED)), covered
    assert covered == COVERED


def test_articles_134_135_specifically_excluded():
    covered = {n for r in _records() for n in r["article_numbers"]}
    for excluded in (134, 135):
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
        assert "book4_provisions_121_137.json" in st["source_reference_file"], r["record_id"]


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
def test_group_123_124_reserves_and_profits():
    r = _rec([123, 124])
    text = _text([123, 124])
    assert "净利润" in text and "专项储备" in text
    conds = "".join(r["conditions_zh"])
    assert "专项储备" in conds and "净利润" in conds
    eff = "".join(r["legal_effects_zh"])
    assert "非专项储备" in eff
    assert "非专项储备" in text


def test_group_126_127_capital_increase_conditions_and_methods():
    r = _rec([126, 127])
    text = _text([126, 127])
    conds = "".join(r["conditions_zh"])
    assert "增资" in conds and "非常大会" in conds
    assert "增资须经非常大会" in text
    # Issued capital must be fully paid up before an increase.
    assert "全额缴清" in conds
    assert "已发行资本须已全额缴清" in text
    eff = "".join(r["legal_effects_zh"])
    assert "发行新股" in eff
    assert "发行新股" in text


def test_group_128_129_130_preemption_transfer_cancellation():
    r = _rec([128, 129, 130])
    text = _text([128, 129, 130])
    rights = "".join(r["rights_zh"])
    assert "优先认购权" in rights
    assert "优先认购权" in text
    # The right may be sold or transferred.
    assert "出售或转让" in rights
    assert "出售或转让该权利" in text
    conds = "".join(r["conditions_zh"])
    assert "取消优先认购权" in conds or "授予非股东" in conds
    assert "取消优先认购权" in text


def test_group_132_major_losses_half_capital_60_180_days():
    r = _rec([132])
    text = _text([132])
    conds = "".join(r["conditions_zh"])
    assert "二分之一" in conds
    assert "已发行资本的二分之一" in text
    obl = "".join(r["obligations_zh"])
    assert "董事会" in obl
    dl = "".join(r["deadlines_zh"])
    assert "六十" in dl or "60" in dl
    assert "一百八十" in dl or "180" in dl
    assert "六十（60）日" in text and "一百八十（180）日" in text


def test_group_133_capital_reduction_methods_creditors():
    r = _rec([133])
    text = _text([133])
    eff = "".join(r["legal_effects_zh"])
    assert "减资" in eff and "注销股份" in eff
    assert "减资的方式" in text and "注销股份" in text
    # Creditor protection is cross-referenced (to Arts 134-135, not covered here).
    assert "债权人" in "".join(r["actors_zh"])
    assert "债权人" in text
    xref = "".join(r["cross_references_zh"])
    assert "134" in xref and "135" in xref


# -- exactly Sections 1-5 Chinese LLM files ---------------------------------
def test_exactly_sections_1_to_5_chinese_llm_files():
    files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(LLM_DIR, "*_zh_legal_llm.json")))
    assert files == ["book4_section1_zh_legal_llm.json",
                     "book4_section2_zh_legal_llm.json",
                     "book4_section3_zh_legal_llm.json",
                     "book4_section4_zh_legal_llm.json",
                     "book4_section5_zh_legal_llm.json"], files


def test_section1_chinese_llm_unchanged():
    s1 = _read(os.path.join(LLM_DIR, "book4_section1_zh_legal_llm.json"))
    assert [r["article_numbers"] for r in s1["records"]] == [[58], [59], [60], [66]]


def test_section2_chinese_llm_unchanged():
    s2 = _read(os.path.join(LLM_DIR, "book4_section2_zh_legal_llm.json"))
    assert [r["article_numbers"] for r in s2["records"]] == [[67, 68], [71], [72], [75], [77]]


def test_section3_chinese_llm_unchanged():
    s3 = _read(os.path.join(LLM_DIR, "book4_section3_zh_legal_llm.json"))
    assert [r["article_numbers"] for r in s3["records"]] == [[85, 87], [92, 93], [99], [101], [102]]


def test_section4_chinese_llm_unchanged():
    s4 = _read(os.path.join(LLM_DIR, "book4_section4_zh_legal_llm.json"))
    assert [r["article_numbers"] for r in s4["records"]] == [[108], [113], [115], [117]]


def test_no_books_1_3_chinese_llm_files():
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
    s5 = _read(os.path.join(layer, "book4_section5_ar_legal_llm.json"))
    assert [r["article_numbers"] for r in s5["records"]] == GROUPS
    for fname, exp in (("book1_ar_legal_llm.json", list(range(1, 35))),
                       ("book2_ar_legal_llm.json", list(range(35, 51))),
                       ("book3_ar_legal_llm.json", list(range(51, 58)))):
        doc = _read(os.path.join(layer, fname))
        assert [r["article_numbers"][0] for r in doc["records"]] == exp, fname


def test_english_reference_unchanged():
    ref = os.path.join(ROOT, "data", "english_reference")
    doc = _read(os.path.join(ref, "book4_section5_en_reference.json"))
    assert [r["article_number"] for r in doc["records"]] == [123, 124, 126, 127, 128, 129, 130, 132, 133]


def test_book4_section5_provisions_unchanged():
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
