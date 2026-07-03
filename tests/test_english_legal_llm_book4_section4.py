"""English Legal LLM-ready layer — Book Four Section 4 (Shares, Debt Instruments and Sukuk).

4 article_reference records for the provision-covered Articles 108, 113, 115, 117.
`legal_rule_text_en` is copied verbatim from the English reference `english_reference_text`;
there is NO `legal_rule_summary_en` / model-generated English summary. Every derived
metadata item must be traceable to the record's own legal_rule_text_en. Article 110 (the
owner-reconciled uncovered article) and the other uncovered Section-4 articles get no
records. English is guidance/reference only; Arabic governs. NOT full English LLM coverage.
"""

import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "english_legal_llm.schema.json")
LLM_DIR = os.path.join(ROOT, "data", "english_legal_llm")
DATA = os.path.join(LLM_DIR, "book4_section4_en_legal_llm.json")
EN_REF = os.path.join(ROOT, "data", "english_reference", "book4_section4_en_reference.json")

COVERED = [108, 113, 115, 117]
UNCOVERED = [103, 104, 105, 106, 107, 109, 110, 111, 112, 114, 116, 118, 119, 120]


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


def test_exactly_four_records():
    assert len(_records()) == 4


def test_article_groups_exact():
    assert [r["article_numbers"] for r in _records()] == [[n] for n in COVERED]


def test_no_records_for_uncovered_section4():
    covered = {n for r in _records() for n in r["article_numbers"]}
    assert not (covered & set(UNCOVERED)), covered
    assert covered == set(COVERED)


def test_article_110_excluded():
    covered = {n for r in _records() for n in r["article_numbers"]}
    assert 110 not in covered


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
        assert "book4_section4_en_reference.json" in st["source_reference_file"], r["record_id"]


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
         "is", "are", "must", "can", "over", "up", "no", "if", "upon", "than", "made",
         "into", "two", "three", "held", "set", "period", "number", "same", "all",
         "against", "new", "them"}


def _squash(text):
    return "".join(text.split())


def _traceable(phrase, text):
    toks = [t.strip(".,;:()%'’-").lower() for t in phrase.split()]
    toks = [t for t in toks if (t and t not in _STOP and len(t) > 3)]

    def _hit(t):
        return t in text or (t.endswith("s") and t[:-1] in text)
    return any(_hit(t) for t in toks)


def test_all_derived_fields_traceable_to_text():
    fields = ("actors_en", "rights_en", "obligations_en", "prohibitions_en",
              "conditions_en", "exceptions_en", "legal_effects_en", "liability_en",
              "deadlines_en", "competent_authorities_en", "cross_references_en")
    for r in _records():
        text = r["legal_rule_text_en"].lower()
        for f in fields:
            for phrase in r[f]:
                assert _traceable(phrase, text), (r["record_id"], f, phrase)


def test_monetary_threshold_percentages_appear_in_text():
    for r in _records():
        squashed = _squash(_text(r["article_numbers"][0]))
        for m in r["monetary_thresholds"]:
            for pct in re.findall(r"\d+%", m["description_en"]):
                assert pct in squashed, (r["record_id"], pct)


def test_competent_authorities_supported_by_text():
    for r in _records():
        squashed = _squash(_text(r["article_numbers"][0]))
        for auth in r["competent_authorities_en"]:
            low = auth.lower()
            ok = (("judicial" in low and "judicialauthority" in squashed)
                  or ("competent authority" in low and "competentauthority" in squashed)
                  or ("general assembly" in low and "generalassembly" in squashed))
            assert ok, (r["record_id"], auth)


def test_prohibitions_have_prohibitory_language():
    for r in _records():
        text = _text(r["article_numbers"][0])
        for p in r["prohibitions_en"]:
            assert ("may not" in text or "except" in text or "shall not" in text
                    or "without" in text), (r["record_id"], p)


# -- TARGETED per-article accuracy (from each article's own text) -----------
def test_art108_types_and_classes():
    r = _rec(108)
    text = _text(108)
    for kind in ("common", "preferred", "redeemable"):
        assert kind in " ".join(r["legal_effects_en"]).lower()
        assert kind in text
    obl = " ".join(r["obligations_en"]).lower()
    assert "equal rights and obligations" in obl
    assert "equal rights and obligations" in text


def test_art113_drag_tag_along_90pct():
    r = _rec(113)
    text = _text(113)
    rights = " ".join(r["rights_en"]).lower()
    assert "drag-along" in rights and "tag-along" in rights
    amounts = {m["amount"] for m in r["monetary_thresholds"]}
    assert 0.9 in amounts
    assert "90%" in _squash(text)
    exc = " ".join(r["exceptions_en"]).lower()
    assert "capital market law" in exc
    assert "capital market law" in text


def test_art115_non_payment_board_auction():
    r = _rec(115)
    text = _text(115)
    obl = " ".join(r["obligations_en"]).lower()
    assert "designated dates" in obl
    assert "designated dates" in text
    rights = " ".join(r["rights_en"]).lower()
    assert ("public auction" in rights or "capital market" in rights)
    assert "public auction" in text
    eff = " ".join(r["legal_effects_en"]).lower()
    assert "suspended" in eff
    assert "suspended" in text
    # No board actor unless the text supports it (Art 115 text does mention the board).
    assert "board of directors" in " ".join(r["actors_en"]).lower()
    assert "board of directors" in text


def test_art117_debt_sukuk_egm_convertible():
    r = _rec(117)
    text = _text(117)
    rights = " ".join(r["rights_en"]).lower()
    assert "debt instruments" in rights or "sukuk" in rights
    obl = " ".join(r["obligations_en"]).lower()
    assert "convertible" in obl and "extraordinary general assembly" in obl
    assert "extraordinary general assembly" in text
    cond = " ".join(r["conditions_en"]).lower()
    assert "capital market law" in cond
    assert "capital market law" in text
    auth = " ".join(r["competent_authorities_en"]).lower()
    assert "general assembly" in auth


# -- only Sections 1-4 English LLM files ------------------------------------
def test_only_sections_1_to_4_files():
    # Shared-validation compatibility: Section 5 has since been added; Sections 1-4
    # must always be present and only sanctioned English LLM files may exist.
    files = set(os.path.basename(p) for p in glob.glob(os.path.join(LLM_DIR, "*_en_legal_llm.json")))
    need = {"book4_section1_en_legal_llm.json", "book4_section2_en_legal_llm.json", "book4_section3_en_legal_llm.json", "book4_section4_en_legal_llm.json"}
    assert need <= files, files
    assert files <= (need | {"book4_section5_en_legal_llm.json"}), files


def test_sections_1_2_3_unchanged():
    s1 = _read(os.path.join(LLM_DIR, "book4_section1_en_legal_llm.json"))
    assert [r["article_numbers"] for r in s1["records"]] == [[58], [59], [60], [66]]
    s2 = _read(os.path.join(LLM_DIR, "book4_section2_en_legal_llm.json"))
    assert [r["article_numbers"] for r in s2["records"]] == [[67], [68], [71], [72], [75], [77]]
    s3 = _read(os.path.join(LLM_DIR, "book4_section3_en_legal_llm.json"))
    assert [r["article_numbers"] for r in s3["records"]] == [[85], [87], [92], [93], [99], [101], [102]]


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
    s4 = _read(os.path.join(layer, "book4_section4_ar_legal_llm.json"))
    assert [r["article_numbers"] for r in s4["records"]] == [[108], [113], [115], [117]]


def test_book4_provisions_unchanged():
    doc = _read(os.path.join(ROOT, "data", "articles", "book4_provisions_103_120.json"))
    assert [p["source_article_numbers"] for p in doc["provisions"]] == [[108], [113], [115], [117]]


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
