"""English Legal LLM-ready layer — Books 1-3 backfill.

One `article_reference` record per article: Book 1 (Arts 1-34), Book 2 (Arts 35-50),
Book 3 (Arts 51-57) — 57 records total. `legal_rule_text_en` is copied verbatim from each
article's `english_reference_text` in the official English reference. There is NO
`legal_rule_summary_en` / model-generated summary. English is official guidance/reference
only; Arabic governs. This complements the repo book4 Sections 1-5 English Legal LLM (30
records) → English Legal LLM total = 8 files / 87 records. NOT full Saudi Companies Law
coverage.
"""

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "english_legal_llm.schema.json")
LLM_DIR = os.path.join(ROOT, "data", "english_legal_llm")
REF_DIR = os.path.join(ROOT, "data", "english_reference")

# (book, llm filename, english reference filename, article range)
UNITS = [
    (1, "book1_en_legal_llm.json", "book1_en_reference.json", list(range(1, 35))),
    (2, "book2_en_legal_llm.json", "book2_en_reference.json", list(range(35, 51))),
    (3, "book3_en_legal_llm.json", "book3_en_reference.json", list(range(51, 58))),
]


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _records(fname):
    return _read(os.path.join(LLM_DIR, fname))["records"]


def _reftext(ref_fname):
    return {r["article_number"]: r["english_reference_text"]
            for r in _read(os.path.join(REF_DIR, ref_fname))["records"]}


# -- existence + exact coverage ---------------------------------------------
def test_files_exist():
    for _book, fname, _ref, _rng in UNITS:
        assert os.path.exists(os.path.join(LLM_DIR, fname)), fname


def test_record_counts():
    counts = {fname: len(_records(fname)) for _b, fname, _r, _rng in UNITS}
    assert counts["book1_en_legal_llm.json"] == 34, counts
    assert counts["book2_en_legal_llm.json"] == 16, counts
    assert counts["book3_en_legal_llm.json"] == 7, counts
    assert sum(counts.values()) == 57, counts


def test_article_coverage_exact():
    for _book, fname, _ref, rng in UNITS:
        nums = [r["article_numbers"] for r in _records(fname)]
        assert nums == [[n] for n in rng], (fname, nums)


def test_book_field_and_record_type():
    for book, fname, _ref, _rng in UNITS:
        for r in _records(fname):
            assert r["book"] == book, (fname, r["record_id"])
            assert r["record_type"] == "article_reference", (fname, r["record_id"])
            assert r["record_id"] == "en-llm-book%d-art%03d" % (book, r["article_numbers"][0]), r


def test_no_wrong_book_or_out_of_range_leakage():
    ranges = {1: set(range(1, 35)), 2: set(range(35, 51)), 3: set(range(51, 58))}
    for book, fname, _ref, rng in UNITS:
        covered = {n for r in _records(fname) for n in r["article_numbers"]}
        assert covered == set(rng), (fname, covered)
        # nothing from another book's range
        for other, oset in ranges.items():
            if other != book:
                assert not (covered & oset), (fname, other, covered & oset)


# -- verbatim source rule ---------------------------------------------------
def test_legal_rule_text_en_verbatim_from_reference():
    for _book, fname, ref_fname, _rng in UNITS:
        ref = _reftext(ref_fname)
        for r in _records(fname):
            n = r["article_numbers"][0]
            assert n in ref, (fname, n)
            assert r["legal_rule_text_en"] == ref[n], (fname, r["record_id"])


def test_legal_subject_en_from_reference_heading():
    for _book, fname, ref_fname, _rng in UNITS:
        refrecs = {r["article_number"]: r
                   for r in _read(os.path.join(REF_DIR, ref_fname))["records"]}
        for r in _records(fname):
            n = r["article_numbers"][0]
            expected = (refrecs[n].get("article_heading_en") or "").strip() or ("Article %d" % n)
            assert r["legal_subject_en"] == expected, (fname, r["record_id"])


def test_keywords_en_reuse_reference_keywords():
    for _book, fname, ref_fname, _rng in UNITS:
        refrecs = {r["article_number"]: r
                   for r in _read(os.path.join(REF_DIR, ref_fname))["records"]}
        for r in _records(fname):
            n = r["article_numbers"][0]
            assert r["keywords_en"] == list(refrecs[n].get("llm", {}).get("keywords_en", [])), r["record_id"]


# -- no generated summaries -------------------------------------------------
def test_no_legal_rule_summary_en_field():
    for _book, fname, _ref, _rng in UNITS:
        assert "legal_rule_summary_en" not in open(os.path.join(LLM_DIR, fname), encoding="utf-8").read()
        for r in _records(fname):
            assert "legal_rule_summary_en" not in r, r["record_id"]


def test_no_generated_summary_fields():
    for _book, fname, _ref, _rng in UNITS:
        for r in _records(fname):
            for k in r:
                assert "summary" not in k.lower(), (fname, r["record_id"], k)


# -- schema + trust posture -------------------------------------------------
def test_records_pass_schema():
    schema = _read(SCHEMA)
    try:
        import jsonschema
        v = jsonschema.Draft7Validator(schema)
        for _book, fname, _ref, _rng in UNITS:
            for r in _records(fname):
                errs = [e.message for e in v.iter_errors(r)]
                assert not errs, (fname, r["record_id"], errs)
    except ImportError:
        for _book, fname, _ref, _rng in UNITS:
            for r in _records(fname):
                for k in schema["required"]:
                    assert k in r, (fname, r["record_id"], k)


def test_legal_basis_type_valid_enum():
    allowed = {"mandatory", "default", "permissive", "prohibition", "definition",
               "procedural", "mixed"}
    for _book, fname, _ref, _rng in UNITS:
        for r in _records(fname):
            assert r["legal_basis_type"] in allowed, (fname, r["record_id"])


def test_trust_fields():
    for _book, fname, ref_fname, _rng in UNITS:
        for r in _records(fname):
            st = r["source_trust"]
            assert st["english_source_status"] == "official_guidance_translation", r["record_id"]
            assert st["governing_text_language"] == "ar", r["record_id"]
            assert st["manual_review_status"] == "needs_manual_check", r["record_id"]
            assert ref_fname in st["source_reference_file"], r["record_id"]


def test_no_forbidden_overclaim_terms():
    for _book, fname, _ref, _rng in UNITS:
        blob = open(os.path.join(LLM_DIR, fname), encoding="utf-8").read().lower()
        for term in ("binding english text", "governing english text", "english is binding",
                     "verified translation", "binding_translation", "official legal advice"):
            assert term not in blob, (fname, term)


# -- final English Legal LLM layer state (Books 1-3 + repo book4 Sections 1-5) --
def test_english_legal_llm_total_8_files_87_records():
    files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(LLM_DIR, "*_en_legal_llm.json")))
    assert files == ["book1_en_legal_llm.json",
                     "book2_en_legal_llm.json",
                     "book3_en_legal_llm.json",
                     "book4_section1_en_legal_llm.json",
                     "book4_section2_en_legal_llm.json",
                     "book4_section3_en_legal_llm.json",
                     "book4_section4_en_legal_llm.json",
                     "book4_section5_en_legal_llm.json"], files
    total = sum(len(_read(p)["records"]) for p in glob.glob(os.path.join(LLM_DIR, "*_en_legal_llm.json")))
    assert total == 87, total


def test_repo_book4_english_legal_llm_unchanged_30_records():
    book4 = glob.glob(os.path.join(LLM_DIR, "book4_section*_en_legal_llm.json"))
    total = sum(len(_read(p)["records"]) for p in book4)
    assert total == 30, total
    # book4 records keep book == 4 and verbatim text (unchanged by this backfill)
    for p in book4:
        for r in _read(p)["records"]:
            assert r["book"] == 4, (p, r["record_id"])
            assert "legal_rule_summary_en" not in r, r["record_id"]


# -- unrelated layers unchanged ---------------------------------------------
def test_chinese_legal_llm_unchanged_5_files_23_records():
    d = os.path.join(ROOT, "data", "chinese_legal_llm")
    files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(d, "*_zh_legal_llm.json")))
    assert files == ["book4_section1_zh_legal_llm.json",
                     "book4_section2_zh_legal_llm.json",
                     "book4_section3_zh_legal_llm.json",
                     "book4_section4_zh_legal_llm.json",
                     "book4_section5_zh_legal_llm.json"], files
    total = sum(len(_read(p)["records"]) for p in glob.glob(os.path.join(d, "*_zh_legal_llm.json")))
    assert total == 23, total


def test_no_books_1_3_chinese_legal_llm_files():
    d = os.path.join(ROOT, "data", "chinese_legal_llm")
    for p in glob.glob(os.path.join(d, "*_zh_legal_llm.json")):
        assert not os.path.basename(p).startswith(("book1_", "book2_", "book3_")), p


def test_english_reference_unchanged_books1_3():
    for _book, _fname, ref_fname, rng in UNITS:
        doc = _read(os.path.join(REF_DIR, ref_fname))
        assert [r["article_number"] for r in doc["records"]] == rng, ref_fname


def test_validator_script_passes():
    import subprocess
    import sys
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "validate_english_legal_llm.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
