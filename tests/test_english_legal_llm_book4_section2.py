"""English Legal LLM-ready layer — Book Four Section 2 (Board of Directors and Governance).

6 article_reference records for the provision-covered Articles 67, 68, 71, 72, 75, 77.
`legal_rule_text_en` is copied verbatim from the English reference `english_reference_text`;
there is NO `legal_rule_summary_en` / model-generated English summary. Every derived
metadata item must be traceable to the record's own legal_rule_text_en. English is
guidance/reference only; Arabic governs. NOT full English Legal LLM coverage.
"""

import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "english_legal_llm.schema.json")
LLM_DIR = os.path.join(ROOT, "data", "english_legal_llm")
DATA = os.path.join(LLM_DIR, "book4_section2_en_legal_llm.json")
EN_REF = os.path.join(ROOT, "data", "english_reference", "book4_section2_en_reference.json")

COVERED = [67, 68, 71, 72, 75, 77]
UNCOVERED = [69, 70, 73, 74, 76, 78, 79, 80, 81, 82, 83]


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _records():
    return _read(DATA)["records"]


def _reftext():
    return {r["article_number"]: r["english_reference_text"] for r in _read(EN_REF)["records"]}


def _rec(n):
    return next(r for r in _records() if r["article_numbers"] == [n])


def _text(n):
    return _rec(n)["legal_rule_text_en"].lower()


# -- existence + scope ------------------------------------------------------
def test_data_exists():
    assert os.path.exists(DATA)


def test_exactly_six_records():
    assert len(_records()) == 6


def test_article_groups_exact():
    assert [r["article_numbers"] for r in _records()] == [[n] for n in COVERED]


def test_no_records_for_uncovered_section2():
    covered = {n for r in _records() for n in r["article_numbers"]}
    assert not (covered & set(UNCOVERED)), covered
    assert covered == set(COVERED)


def test_record_type_and_book():
    for r in _records():
        assert r["record_type"] == "article_reference", r["record_id"]
        assert r["book"] == 4, r["record_id"]


# -- schema + verbatim + no generated summaries -----------------------------
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
    assert "legal_rule_summary_en" not in open(DATA, encoding="utf-8").read()


def test_no_generated_summary_fields():
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
        assert "book4_section2_en_reference.json" in st["source_reference_file"], r["record_id"]


def test_no_forbidden_overclaim_terms():
    blob = open(DATA, encoding="utf-8").read().lower()
    for term in ("binding english text", "governing english text", "english is binding",
                 "verified translation", "binding_translation", "official legal advice"):
        assert term not in blob, term


# -- GENERIC metadata-accuracy guards (traceable to the article's own text) --
_STOP = {"the", "a", "an", "of", "to", "and", "or", "in", "on", "for", "its", "his",
         "any", "may", "not", "shall", "such", "with", "by", "at", "least", "one",
         "more", "their", "he", "himself", "said", "this", "which", "as", "case",
         "from", "date", "within", "previous", "who", "acts", "party", "provision",
         "provisions", "them", "certain", "other", "others", "these", "that", "be",
         "is", "are", "must", "can", "over", "up", "no"}


def _traceable(phrase, text):
    """A derived phrase is traceable if it shares a meaningful token with the text."""
    toks = [t.strip(".,;:()%'’-").lower() for t in phrase.split()]
    toks = [t for t in toks if t and t not in _STOP and len(t) > 3 or t in ("50%", "12")]
    # a phrase must have at least one substantive token present in the text
    return any(t and t in text for t in toks)


def test_all_derived_fields_traceable_to_text():
    fields = ("actors_en", "rights_en", "obligations_en", "prohibitions_en",
              "conditions_en", "exceptions_en", "legal_effects_en", "liability_en",
              "deadlines_en", "competent_authorities_en", "cross_references_en")
    for r in _records():
        text = r["legal_rule_text_en"].lower()
        for f in fields:
            for phrase in r[f]:
                assert _traceable(phrase, text), (r["record_id"], f, phrase)


def test_deadlines_periods_appear_in_text():
    for r in _records():
        text = _text(r["article_numbers"][0])
        for d in r["deadlines_en"]:
            # any explicit number word in a deadline must appear in the text
            for token in ("four", "12", "twelve", "60", "180", "90"):
                if token in d.lower():
                    assert token in text, (r["record_id"], d)


def test_monetary_thresholds_numbers_appear_in_text():
    for r in _records():
        text = _text(r["article_numbers"][0])
        for m in r["monetary_thresholds"]:
            desc = m["description_en"].lower()
            if "50%" in desc or "50 %" in desc:
                assert "50%" in text or "50 %" in text, r["record_id"]


def test_competent_authorities_supported_by_text():
    # The source's verbatim text contains PDF-extraction spacing artifacts
    # (e.g. "ju dicial"), so compare with all whitespace removed.
    for r in _records():
        text = _text(r["article_numbers"][0])
        squashed = "".join(text.split())
        for auth in r["competent_authorities_en"]:
            low = auth.lower()
            ok = (("competent authority" in low and "competentauthority" in squashed)
                  or ("judicial" in low and "judicialauthority" in squashed)
                  or ("general assembly" in low and "generalassembly" in squashed)
                  or ("auditor" in low and "auditor" in squashed))
            assert ok, (r["record_id"], auth)


def test_prohibitions_have_prohibitory_language():
    for r in _records():
        text = _text(r["article_numbers"][0])
        for p in r["prohibitions_en"]:
            assert ("may not" in text or "null and void" in text or "prohibit" in text), (r["record_id"], p)


# -- TARGETED per-article accuracy (from each article's own text) -----------
def test_art67_board_and_three_members():
    r = _rec(67)
    actors = " ".join(r["actors_en"]).lower()
    assert "board of directors" in actors and "shareholder" in actors
    combined = (" ".join(r["obligations_en"]) + " " + " ".join(r["legal_effects_en"])).lower()
    assert "three members" in combined
    assert "three members" in _text(67)


def test_art68_ogm_natural_persons_four_years_no_egm():
    r = _rec(68)
    actors = " ".join(r["actors_en"]).lower()
    assert "ordinary general assembly" in actors
    # EGM must not be asserted — Article 68 text does not mention it.
    assert "extraordinary general assembly" not in actors
    assert "extraordinary general assembly" not in _text(68)
    obl = " ".join(r["obligations_en"]).lower()
    assert "natural persons" in obl and "four years" in obl
    assert "competent authority" in " ".join(r["competent_authorities_en"]).lower()
    assert "competent authority" in _text(68)


def test_art71_disclose_no_vote_auditor():
    r = _rec(71)
    obl = " ".join(r["obligations_en"]).lower()
    assert "disclose" in obl and "minutes" in obl
    prohib = " ".join(r["prohibitions_en"]).lower()
    assert "may not vote" in prohib
    assert "may not vote" in _text(71)
    assert "auditor" in " ".join(r["competent_authorities_en"] + r["obligations_en"]).lower()
    assert "article 27" in " ".join(r["cross_references_en"]).lower()
    assert "article 27" in _text(71)


def test_art72_loan_prohibition_null_void_exceptions():
    r = _rec(72)
    prohib = " ".join(r["prohibitions_en"]).lower()
    assert "loan" in prohib and ("board members" in prohib or "guarantor" in prohib or "guarantee" in prohib)
    eff = " ".join(r["legal_effects_en"]).lower()
    assert "null and void" in eff
    assert "null and void" in _text(72)
    exc = " ".join(r["exceptions_en"]).lower()
    assert "banks" in exc and "employee incentive" in exc
    assert "banks" in _text(72) and "employee incentive" in _text(72)


def test_art75_fifty_percent_general_assembly_12_months():
    r = _rec(75)
    obl = " ".join(r["obligations_en"]).lower()
    assert "general assembly" in obl and "50%" in obl
    assert "50%" in _text(75)
    amounts = {m["amount"] for m in r["monetary_thresholds"]}
    assert 0.5 in amounts
    assert any("12 months" in d.lower() for d in r["deadlines_en"])
    assert "12 months" in _text(75)


def test_art77_powers_delegate_bind_bad_faith():
    r = _rec(77)
    rights = " ".join(r["rights_en"]).lower()
    assert "powers" in rights and "delegate" in rights
    assert "delegate" in _text(77)
    eff = " ".join(r["legal_effects_en"]).lower()
    assert "bound" in eff
    exc = " ".join(r["exceptions_en"]).lower()
    assert "bad faith" in exc
    assert "bad faith" in _text(77)


# -- only Section 1 + Section 2 English LLM files ---------------------------
def test_only_section1_and_section2_files():
    files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(LLM_DIR, "*_en_legal_llm.json")))
    assert files == ["book4_section1_en_legal_llm.json", "book4_section2_en_legal_llm.json"], files


def test_section1_unchanged():
    doc = _read(os.path.join(LLM_DIR, "book4_section1_en_legal_llm.json"))
    assert [r["article_numbers"] for r in doc["records"]] == [[58], [59], [60], [66]]


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
    for fname, grp in (("book4_section2_ar_legal_llm.json", [[67, 68], [71], [72], [75], [77]]),
                       ("book4_section3_ar_legal_llm.json", [[85, 87], [92, 93], [99], [101], [102]]),
                       ("book4_section4_ar_legal_llm.json", [[108], [113], [115], [117]]),
                       ("book4_section5_ar_legal_llm.json", [[123, 124], [126, 127], [128, 129, 130], [132], [133]])):
        doc = _read(os.path.join(layer, fname))
        assert [r["article_numbers"] for r in doc["records"]] == grp, fname


def test_book4_provisions_unchanged():
    doc = _read(os.path.join(ROOT, "data", "articles", "book4_provisions_067_083.json"))
    assert [p["source_article_numbers"] for p in doc["provisions"]] == [[67, 68], [71], [72], [75], [77]]


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
