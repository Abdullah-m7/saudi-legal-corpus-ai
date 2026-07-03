"""English Legal LLM-ready layer — PILOT: Book Four Section 1 (Establishment and Capital).

Starts the English Legal LLM layer with the Book Four Section 1 pilot ONLY — 4
article_reference records for Articles 58, 59, 60, 66. `legal_rule_text_en` is copied
verbatim from the English reference `english_reference_text`; there is NO
`legal_rule_summary_en` / model-generated English summary. English is guidance/reference
only; Arabic governs. NOT full English Legal LLM coverage.
"""

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "english_legal_llm.schema.json")
LLM_DIR = os.path.join(ROOT, "data", "english_legal_llm")
DATA = os.path.join(LLM_DIR, "book4_section1_en_legal_llm.json")
EN_REF = os.path.join(ROOT, "data", "english_reference", "book4_section1_en_reference.json")

COVERED = [58, 59, 60, 66]
UNCOVERED = [61, 62, 63, 64, 65]


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _records():
    return _read(DATA)["records"]


def _reftext():
    return {r["article_number"]: r["english_reference_text"] for r in _read(EN_REF)["records"]}


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


# -- schema + verbatim rule text --------------------------------------------
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


def test_legal_rule_text_en_verbatim_from_reference():
    ref = _reftext()
    for r in _records():
        (n,) = r["article_numbers"]
        assert n in ref, n
        assert r["legal_rule_text_en"] == ref[n], r["record_id"]


def test_no_legal_rule_summary_en_field():
    for r in _records():
        assert "legal_rule_summary_en" not in r, r["record_id"]
    blob = open(DATA, encoding="utf-8").read()
    assert "legal_rule_summary_en" not in blob


def test_no_generated_summary_fields():
    # Any *summary* field would signal a model-generated English summary.
    for r in _records():
        for k in r:
            assert "summary" not in k.lower(), (r["record_id"], k)


# -- trust posture ----------------------------------------------------------
def test_trust_fields():
    for r in _records():
        st = r["source_trust"]
        assert st["english_source_status"] == "official_guidance_translation", r["record_id"]
        assert st["governing_text_language"] == "ar", r["record_id"]
        assert st["manual_review_status"] == "needs_manual_check", r["record_id"]
        assert "book4_section1_en_reference.json" in st["source_reference_file"], r["record_id"]


def _rec(n):
    return next(r for r in _records() if r["article_numbers"] == [n])


# -- derived-metadata accuracy (must be faithful to legal_rule_text_en) ------
def test_article_59_monetary_thresholds_and_obligations():
    r = _rec(59)
    mt_blob = json.dumps(r["monetary_thresholds"], ensure_ascii=False).lower()
    assert "500000" in mt_blob or "500,000" in mt_blob, r["monetary_thresholds"]
    assert "quarter" in mt_blob, r["monetary_thresholds"]
    # amounts present numerically
    amounts = {m["amount"] for m in r["monetary_thresholds"]}
    assert 500000 in amounts, amounts
    # Must NOT claim the minimum is set by the Regulations (not in Article 59 text).
    text = r["legal_rule_text_en"].lower()
    obl = " ".join(r["obligations_en"]).lower()
    if "regulation" not in text:
        assert "regulation" not in obl, r["obligations_en"]
    assert any("five hundred thousand" in o.lower() or "500" in o for o in r["obligations_en"])
    assert any("quarter" in o.lower() for o in r["obligations_en"])


def test_article_60_actors_and_conditions():
    r = _rec(60)
    actors = " ".join(r["actors_en"]).lower()
    assert "board of directors" in actors, r["actors_en"]
    text = r["legal_rule_text_en"].lower()
    if "extraordinary general assembly" not in text:
        assert "extraordinary general assembly" not in actors, r["actors_en"]
    combined = (" ".join(r["conditions_en"]) + " " + " ".join(r["legal_effects_en"])).lower()
    assert "paid in full" in combined, combined
    assert "authorized capital" in combined, combined


def test_article_66_actors_prohibitions_conditions():
    r = _rec(66)
    actors = " ".join(r["actors_en"]).lower()
    for who in ("accredited valuer", "incorporators", "extraordinary general assembly",
                "providers of in-kind contributions"):
        assert who in actors, (who, r["actors_en"])
    prohib = " ".join(r["prohibitions_en"]).lower()
    assert "may not vote" in prohib, r["prohibitions_en"]
    cond = " ".join(r["conditions_en"]).lower()
    assert "approved by the providers" in cond or "approved by the providers of" in cond, r["conditions_en"]
    assert "regulations" in cond, r["conditions_en"]


def test_no_forbidden_overclaim_terms():
    blob = open(DATA, encoding="utf-8").read().lower()
    for term in ("binding english text", "governing english text", "english is binding",
                 "verified translation", "binding_translation", "official legal advice"):
        assert term not in blob, term


# -- English LLM files are limited to the sanctioned set --------------------
def test_english_llm_files_are_sanctioned_only():
    # Shared-validation compatibility: Section 2 has since been added; only the
    # sanctioned English LLM files may exist (Section 1 must always be present).
    files = set(os.path.basename(p) for p in glob.glob(os.path.join(LLM_DIR, "*_en_legal_llm.json")))
    assert "book4_section1_en_legal_llm.json" in files, files
    assert files <= {"book4_section1_en_legal_llm.json", "book4_section2_en_legal_llm.json"}, files


def test_no_english_llm_records_in_reference_dir():
    stray = glob.glob(os.path.join(ROOT, "data", "english_reference", "*_en_legal_llm.json"))
    assert stray == [], stray


# -- existing artifacts unchanged -------------------------------------------
def test_english_reference_unchanged():
    ref = os.path.join(ROOT, "data", "english_reference")
    for fname, exp in (("book1_en_reference.json", list(range(1, 35))),
                       ("book2_en_reference.json", list(range(35, 51))),
                       ("book3_en_reference.json", list(range(51, 58))),
                       ("book4_section1_en_reference.json", [58, 59, 60, 66]),
                       ("book4_section2_en_reference.json", [67, 68, 71, 72, 75, 77]),
                       ("book4_section3_en_reference.json", [85, 87, 92, 93, 99, 101, 102]),
                       ("book4_section4_en_reference.json", [108, 113, 115, 117]),
                       ("book4_section5_en_reference.json", [123, 124, 126, 127, 128, 129, 130, 132, 133])):
        doc = _read(os.path.join(ref, fname))
        assert [r["article_number"] for r in doc["records"]] == exp, fname


def test_arabic_legal_llm_unchanged():
    layer = os.path.join(ROOT, "data", "arabic_legal_llm")
    for fname, exp in (("book1_ar_legal_llm.json", list(range(1, 35))),
                       ("book2_ar_legal_llm.json", list(range(35, 51))),
                       ("book3_ar_legal_llm.json", list(range(51, 58)))):
        doc = _read(os.path.join(layer, fname))
        assert [r["article_numbers"][0] for r in doc["records"]] == exp, fname
    s1 = _read(os.path.join(layer, "book4_section1_ar_legal_llm.json"))
    assert sorted(r["article_numbers"][0] for r in s1["records"]) == [58, 59, 60, 66]
    for fname, grp in (("book4_section2_ar_legal_llm.json", [[67, 68], [71], [72], [75], [77]]),
                       ("book4_section3_ar_legal_llm.json", [[85, 87], [92, 93], [99], [101], [102]]),
                       ("book4_section4_ar_legal_llm.json", [[108], [113], [115], [117]]),
                       ("book4_section5_ar_legal_llm.json", [[123, 124], [126, 127], [128, 129, 130], [132], [133]])):
        doc = _read(os.path.join(layer, fname))
        assert [r["article_numbers"] for r in doc["records"]] == grp, fname


def test_book4_provisions_unchanged():
    checks = [
        ("book4_provisions_058_066.json", [[58], [59], [60], [66]]),
        ("book4_provisions_067_083.json", [[67, 68], [71], [72], [75], [77]]),
        ("book4_provisions_084_102.json", [[85, 87], [92, 93], [99], [101], [102]]),
        ("book4_provisions_103_120.json", [[108], [113], [115], [117]]),
        ("book4_provisions_121_137.json", [[123, 124], [126, 127], [128, 129, 130], [132], [133]]),
    ]
    for fname, grp in checks:
        doc = _read(os.path.join(ROOT, "data", "articles", fname))
        assert [p["source_article_numbers"] for p in doc["provisions"]] == grp, fname


def test_no_book4_articles_files():
    for f in os.listdir(os.path.join(ROOT, "data", "articles")):
        assert not f.startswith("book4_articles_"), f


def test_no_full_book4_content():
    for p in ("content/ar/book4.md", "content/zh/book4.md", "content/bilingual/book4_bilingual.md"):
        assert not os.path.exists(os.path.join(ROOT, p)), p


def test_arabic_and_chinese_canonical_unchanged():
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
        [sys.executable, os.path.join(ROOT, "scripts", "validate_english_legal_llm.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
