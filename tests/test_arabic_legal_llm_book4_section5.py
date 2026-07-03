"""Arabic Legal LLM-ready layer — Book Four Section 5 (finance/profits/capital changes).

5 provision records mapped to [123,124], [126,127], [128,129,130], [132], [133] only.
The legal_rule_summary_ar must exactly match the corresponding Section 5 provision's
arabic_reference_summary. Articles 134 & 135 appear only as a cross-reference in the
source's capital-reduction block and get NO record. NOT full Book Four Arabic LLM coverage.
"""

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "arabic_legal_llm.schema.json")
LAYER = os.path.join(ROOT, "data", "arabic_legal_llm")
DATA = os.path.join(LAYER, "book4_section5_ar_legal_llm.json")
PROVISIONS = os.path.join(ROOT, "data", "articles", "book4_provisions_121_137.json")
COVERAGE = os.path.join(ROOT, "data", "coverage", "book4_coverage_matrix.json")

GROUPS = [[123, 124], [126, 127], [128, 129, 130], [132], [133]]
EXPLICIT = {123, 124, 126, 127, 128, 129, 130, 132, 133}
UNCOVERED = [121, 122, 125, 131, 134, 135, 136, 137]
BANNED = ("verified", "محققة", "经核验")


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _records():
    return _read(DATA)["records"]


def _provision_summaries():
    return {tuple(p["source_article_numbers"]): p["arabic_reference_summary"]
            for p in _read(PROVISIONS)["provisions"]}


# -- existence + scope ------------------------------------------------------
def test_data_exists():
    assert os.path.exists(DATA)


def test_exactly_five_records():
    assert len(_records()) == 5


def test_record_type_provision():
    for r in _records():
        assert r["record_type"] == "provision", r["record_id"]
        assert r["book"] == 4, r["record_id"]


def test_article_groups_exact():
    assert [r["article_numbers"] for r in _records()] == GROUPS


def test_no_uncovered_articles():
    covered = {n for r in _records() for n in r["article_numbers"]}
    assert not (covered & set(UNCOVERED)), covered
    assert covered == EXPLICIT


def test_articles_134_135_have_no_record():
    covered = {n for r in _records() for n in r["article_numbers"]}
    assert 134 not in covered and 135 not in covered


# -- schema + exact-match to provisions -------------------------------------
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


def test_legal_rule_summary_exactly_matches_provision():
    prov = _provision_summaries()
    for r in _records():
        key = tuple(r["article_numbers"])
        assert key in prov, key
        assert r["legal_rule_summary_ar"] == prov[key], r["record_id"]


# -- trust posture ----------------------------------------------------------
def test_trust_posture():
    for r in _records():
        st = r["source_trust"]
        assert st["official_text_check"] == "needs_check", r["record_id"]
        assert st["text_type"] == "internally_reviewed_summary", r["record_id"]


def test_no_overclaim_terms():
    blob = open(DATA, encoding="utf-8").read()
    for t in BANNED:
        assert t not in blob, t


# -- existing artifacts unchanged -------------------------------------------
def test_sections_1_2_3_4_arabic_llm_unchanged():
    s1 = _read(os.path.join(LAYER, "book4_section1_ar_legal_llm.json"))
    assert sorted(r["article_numbers"][0] for r in s1["records"]) == [58, 59, 60, 66]
    s2 = _read(os.path.join(LAYER, "book4_section2_ar_legal_llm.json"))
    assert [r["article_numbers"] for r in s2["records"]] == [[67, 68], [71], [72], [75], [77]]
    s3 = _read(os.path.join(LAYER, "book4_section3_ar_legal_llm.json"))
    assert [r["article_numbers"] for r in s3["records"]] == [[85, 87], [92, 93], [99], [101], [102]]
    s4 = _read(os.path.join(LAYER, "book4_section4_ar_legal_llm.json"))
    assert [r["article_numbers"] for r in s4["records"]] == [[108], [113], [115], [117]]


def test_books_1_3_arabic_llm_unchanged():
    for fname, exp in (("book1_ar_legal_llm.json", list(range(1, 35))),
                       ("book2_ar_legal_llm.json", list(range(35, 51))),
                       ("book3_ar_legal_llm.json", list(range(51, 58)))):
        doc = _read(os.path.join(LAYER, fname))
        assert [r["article_numbers"][0] for r in doc["records"]] == exp, fname


def test_english_reference_unchanged_no_section5():
    ref = os.path.join(ROOT, "data", "english_reference")
    for fname, exp in (("book1_en_reference.json", list(range(1, 35))),
                       ("book2_en_reference.json", list(range(35, 51))),
                       ("book3_en_reference.json", list(range(51, 58))),
                       ("book4_section1_en_reference.json", [58, 59, 60, 66]),
                       ("book4_section2_en_reference.json", [67, 68, 71, 72, 75, 77]),
                       ("book4_section3_en_reference.json", [85, 87, 92, 93, 99, 101, 102]),
                       ("book4_section4_en_reference.json", [108, 113, 115, 117])):
        doc = _read(os.path.join(ref, fname))
        assert [r["article_number"] for r in doc["records"]] == exp, fname
    # The English reference Section 5 file, if present, contains exactly the
    # provision-covered articles (added by the Section 5 English reference PR);
    # shared-validation compatibility — Articles 134 & 135 stay excluded.
    s5_ref = os.path.join(ref, "book4_section5_en_reference.json")
    if os.path.exists(s5_ref):
        doc = _read(s5_ref)
        assert [r["article_number"] for r in doc["records"]] == [123, 124, 126, 127, 128, 129, 130, 132, 133]


def test_no_english_llm_directory():
    # English Legal LLM layer started (Book Four Section 1 pilot); only that file may exist.
    _elf = glob.glob(os.path.join(ROOT, "data", "english_legal_llm", "*_en_legal_llm.json"))
    assert sorted(os.path.basename(p) for p in _elf) in ([], ["book4_section1_en_legal_llm.json"]), _elf
    stray = glob.glob(os.path.join(ROOT, "data", "**", "*_en_legal_llm.json"), recursive=True)
    assert sorted(os.path.basename(p) for p in stray) in ([], ["book4_section1_en_legal_llm.json"]), stray


def test_book4_section5_provisions_unchanged():
    doc = _read(PROVISIONS)
    assert [p["source_article_numbers"] for p in doc["provisions"]] == GROUPS


def test_no_book4_articles_files():
    for f in os.listdir(os.path.join(ROOT, "data", "articles")):
        assert not f.startswith("book4_articles_"), f


def test_coverage_matrix_80_rows_reconciliation_preserved():
    matrix = _read(COVERAGE)
    rows = matrix["rows"]
    assert len(rows) == 80
    by = {r["article_number"]: r for r in rows}
    for n in sorted(EXPLICIT):
        assert by[n]["source_coverage_status"] == "explicit_in_source", n
        assert by[n]["official_text_check"] == "needs_check", n
        assert by[n]["content_record_status"] == "provision_created", n
    for n in UNCOVERED:
        assert by[n]["source_coverage_status"] == "not_explicit_in_source", n
        assert by[n]["official_text_check"] == "needs_official_text_check", n
        assert by[n]["content_record_status"] == "no_record_until_source_available", n
    # Prior owner-reconciled rows stay uncovered.
    for n in (84, 89, 100, 110):
        assert by[n]["source_coverage_status"] == "not_explicit_in_source", n
        assert by[n]["official_text_check"] == "needs_official_text_check", n
        assert by[n]["content_record_status"] == "no_record_until_source_available", n


def test_books_1_3_canonical_unchanged():
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
        [sys.executable, os.path.join(ROOT, "scripts", "validate_arabic_legal_llm.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
