"""Chinese Legal LLM-ready layer — PILOT: Book Four Section 1 (Establishment and Capital).

Starts the Chinese Legal LLM layer with the Book Four Section 1 pilot ONLY — 4
article_reference records for article groups [58], [59], [60], [66]. `legal_rule_text_zh`
is copied verbatim from each provision's `chinese_translation` field in
data/articles/book4_provisions_058_066.json (the selected authoritative existing Chinese
source field). There is NO `legal_rule_summary_zh` / new/machine translation / generated
summary. Chinese is an internal working translation only; Arabic governs. NOT full Chinese
Legal LLM coverage.
"""

import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "chinese_legal_llm.schema.json")
LLM_DIR = os.path.join(ROOT, "data", "chinese_legal_llm")
DATA = os.path.join(LLM_DIR, "book4_section1_zh_legal_llm.json")
PROVISIONS = os.path.join(ROOT, "data", "articles", "book4_provisions_058_066.json")

# The selected authoritative existing Chinese source field.
SOURCE_FIELD = "chinese_translation"
COVERED = [58, 59, 60, 66]
UNCOVERED = [61, 62, 63, 64, 65]


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _records():
    return _read(DATA)["records"]


def _provtext():
    return {tuple(p["source_article_numbers"]): p[SOURCE_FIELD]
            for p in _read(PROVISIONS)["provisions"]}


def _rec(n):
    return next(r for r in _records() if r["article_numbers"] == [n])


def _text(n):
    return _rec(n)["legal_rule_text_zh"]


# -- existence + scope ------------------------------------------------------
def test_schema_exists():
    assert os.path.exists(SCHEMA)


def test_data_exists():
    assert os.path.exists(DATA)


def test_exactly_four_records():
    assert len(_records()) == 4


def test_article_groups_exact():
    assert [r["article_numbers"] for r in _records()] == [[n] for n in COVERED]


def test_no_records_for_uncovered_61_65():
    covered = {n for r in _records() for n in r["article_numbers"]}
    assert not (covered & set(UNCOVERED)), covered
    assert covered == set(COVERED)


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
        assert "book4_provisions_058_066.json" in st["source_reference_file"], r["record_id"]


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
    # A derived Chinese phrase is traceable if it shares a contiguous >=3-char CJK
    # substring with the source text (or a >=2-char run appears verbatim).
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
    # keywords_zh must reuse the provision's own approved llm.keywords_zh (not new terms).
    prov = {tuple(p["source_article_numbers"]): p.get("llm", {}).get("keywords_zh", [])
            for p in _read(PROVISIONS)["provisions"]}
    for r in _records():
        assert r["keywords_zh"] == prov[tuple(r["article_numbers"])], r["record_id"]


def test_monetary_thresholds_numbers_appear_in_source():
    for r in _records():
        text = _text(r["article_numbers"][0])
        squashed = text.replace(",", "").replace("，", "")
        for m in r["monetary_thresholds"]:
            desc = m["description_zh"]
            # the description is drawn from the source, so it must be a substring
            assert desc in text, (r["record_id"], desc)
            if m["amount"] == 500000:
                assert ("500000" in squashed) or ("五十万" in text), r["record_id"]


# -- TARGETED per-article accuracy (Chinese substring checks against source) --
def test_art58_definition_liability():
    r = _rec(58)
    text = _text(58)
    assert "股份公司" in " ".join(r["actors_zh"]) and "股东" in " ".join(r["actors_zh"])
    assert "股份公司" in text and "股东" in text
    eff = "".join(r["legal_effects_zh"])
    assert "责任" in eff
    assert "股东的责任仅限于" in text


def test_art59_minimum_capital_thresholds():
    r = _rec(59)
    text = _text(59)
    assert "五十万" in text and "四分之一" in text
    obl = "".join(r["obligations_zh"])
    assert "已发行资本" in obl and "四分之一" in obl
    amounts = {m["amount"] for m in r["monetary_thresholds"]}
    assert 500000 in amounts and 0.25 in amounts


def test_art60_issued_authorized_capital():
    r = _rec(60)
    text = _text(60)
    assert "授权资本" in text and "已发行资本" in text
    eff = "".join(r["legal_effects_zh"])
    assert "授权资本" in eff
    cond = "".join(r["conditions_zh"])
    assert "全额缴清" in cond
    assert "全额缴清" in text
    assert "董事会" in " ".join(r["actors_zh"])
    assert "董事会" in text


def test_art66_in_kind_valuation_voting_restriction():
    r = _rec(66)
    text = _text(66)
    assert "实物出资" in text and "认证评估师" in text
    obl = "".join(r["obligations_zh"])
    assert "评估" in obl
    prohib = "".join(r["prohibitions_zh"])
    assert "不得参与" in prohib and "表决" in prohib
    assert "不得参与对其评估决议的表决" in text
    cond = "".join(r["conditions_zh"])
    assert "同意" in cond
    assert "须经该出资人同意" in text


# -- only repo book4 Sections 1-5 Chinese LLM files; no Books 1-3 ------------
# Sections 2-5 were added as sanctioned extensions (repo book4 Sections 1-5 now complete);
# the Section 1 pilot file must still be present and unchanged, and no file outside
# Sections 1-5 may exist.
_ALLOWED_ZH_LLM = {"book4_section1_zh_legal_llm.json", "book4_section2_zh_legal_llm.json",
                   "book4_section3_zh_legal_llm.json", "book4_section4_zh_legal_llm.json",
                   "book4_section5_zh_legal_llm.json"}


def test_only_pilot_chinese_llm_file():
    files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(LLM_DIR, "*_zh_legal_llm.json")))
    assert "book4_section1_zh_legal_llm.json" in files, files
    assert set(files) <= _ALLOWED_ZH_LLM, files


def test_no_books_1_3_or_other_section_chinese_llm_files():
    for f in glob.glob(os.path.join(LLM_DIR, "*_zh_legal_llm.json")):
        base = os.path.basename(f)
        assert base in _ALLOWED_ZH_LLM, base


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
    for fname, exp in (("book1_ar_legal_llm.json", list(range(1, 35))),
                       ("book2_ar_legal_llm.json", list(range(35, 51))),
                       ("book3_ar_legal_llm.json", list(range(51, 58)))):
        doc = _read(os.path.join(layer, fname))
        assert [r["article_numbers"][0] for r in doc["records"]] == exp, fname
    s1 = _read(os.path.join(layer, "book4_section1_ar_legal_llm.json"))
    assert sorted(r["article_numbers"][0] for r in s1["records"]) == [58, 59, 60, 66]


def test_english_reference_unchanged():
    ref = os.path.join(ROOT, "data", "english_reference")
    for fname, exp in (("book4_section1_en_reference.json", [58, 59, 60, 66]),
                       ("book4_section5_en_reference.json", [123, 124, 126, 127, 128, 129, 130, 132, 133])):
        doc = _read(os.path.join(ref, fname))
        assert [r["article_number"] for r in doc["records"]] == exp, fname


def test_book4_section1_provisions_unchanged():
    doc = _read(PROVISIONS)
    assert [p["source_article_numbers"] for p in doc["provisions"]] == [[58], [59], [60], [66]]
    # Chinese source/provision text unchanged (still present + non-empty).
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
