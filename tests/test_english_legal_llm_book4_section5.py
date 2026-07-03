"""English Legal LLM-ready layer — Book Four Section 5 (Finance, Profits, and Capital Changes).

9 article_reference records for the provision-covered Articles 123, 124, 126, 127, 128,
129, 130, 132, 133. `legal_rule_text_en` is copied verbatim from the English reference
`english_reference_text`; there is NO `legal_rule_summary_en` / model-generated English
summary. Every derived metadata item must be traceable to the record's own
legal_rule_text_en. Articles 134 & 135 (cross-reference-only in the model-1b scope) and
the other uncovered Section-5 articles get no records. This completes Book Four Sections
1-5 for the English Legal LLM layer (still not Books 1-3). English is guidance/reference
only; Arabic governs.
"""

import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schemas", "english_legal_llm.schema.json")
LLM_DIR = os.path.join(ROOT, "data", "english_legal_llm")
DATA = os.path.join(LLM_DIR, "book4_section5_en_legal_llm.json")
EN_REF = os.path.join(ROOT, "data", "english_reference", "book4_section5_en_reference.json")

COVERED = [123, 124, 126, 127, 128, 129, 130, 132, 133]
UNCOVERED = [121, 122, 125, 131, 134, 135, 136, 137]


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


def test_exactly_nine_records():
    assert len(_records()) == 9


def test_article_groups_exact():
    assert [r["article_numbers"] for r in _records()] == [[n] for n in COVERED]


def test_no_records_for_uncovered_section5():
    covered = {n for r in _records() for n in r["article_numbers"]}
    assert not (covered & set(UNCOVERED)), covered
    assert covered == set(COVERED)


def test_articles_134_135_excluded():
    covered = {n for r in _records() for n in r["article_numbers"]}
    assert 134 not in covered
    assert 135 not in covered


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
        assert "book4_section5_en_reference.json" in st["source_reference_file"], r["record_id"]


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
         "against", "new", "part", "thereof", "value", "amount", "cases", "deems",
         "means", "type", "class"}


def _squash(text):
    return "".join(text.split())


def _traceable(phrase, text):
    # split on whitespace, hyphens, and slashes so hyphenated terms (and source
    # extraction artifacts like "non -shareholders") still match on a sub-token.
    toks = [t.strip(".,;:()%'’-").lower() for t in re.split(r"[\s/\-]+", phrase)]
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


def test_deadlines_periods_appear_in_text():
    for r in _records():
        text = _text(r["article_numbers"][0])
        for d in r["deadlines_en"]:
            for token in ("60 days", "180 days", "90 days", "15 days", "30 days"):
                if token in d.lower():
                    assert token in text, (r["record_id"], d, token)


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
            assert ("may not" in text or "shall not" in text or "except" in text
                    or "without" in text), (r["record_id"], p)


# -- TARGETED per-article accuracy (from each article's own text) -----------
def test_art123_reserves_from_net_profit():
    r = _rec(123)
    text = _text(123)
    rights = " ".join(r["rights_en"]).lower()
    assert "net profit" in rights and "reserve" in rights
    assert "net profit" in text
    assert "competent authority" in " ".join(r["competent_authorities_en"]).lower()
    assert "competent authority" in text


def test_art124_use_reserves_egm_prohibition():
    r = _rec(124)
    text = _text(124)
    prohib = " ".join(r["prohibitions_en"]).lower()
    assert "may not be used except" in prohib
    assert "may not be used except" in text
    rights = " ".join(r["rights_en"]).lower()
    assert "retained earnings" in rights
    assert "retained earnings" in text


def test_art126_capital_increase_methods_creditors():
    r = _rec(126)
    text = _text(126)
    eff = " ".join(r["legal_effects_en"]).lower()
    assert "in-kind" in eff or "bonus shares" in eff or "debt" in eff
    cond = " ".join(r["conditions_en"]).lower()
    assert "creditors" in cond
    assert "creditors" in text
    assert "extraordinary general assembly" in " ".join(r["competent_authorities_en"]).lower()
    assert "extraordinary general assembly" in text


def test_art127_increase_paid_in_full_employee_prohibition():
    r = _rec(127)
    text = _text(127)
    cond = " ".join(r["conditions_en"]).lower()
    assert "paid in full" in cond
    assert "paid in full" in text
    prohib = " ".join(r["prohibitions_en"]).lower()
    assert "preemptive rights" in prohib and "employees" in prohib
    assert "may not exercise" in text


def test_art128_preemptive_right_cash_notification():
    r = _rec(128)
    text = _text(128)
    rights = " ".join(r["rights_en"]).lower()
    assert "preemptive right" in rights and "cash" in rights
    obl = " ".join(r["obligations_en"]).lower()
    assert "notified" in obl and ("registered mail" in obl or "technology" in obl)
    assert "registered mail" in text


def test_art129_suspend_preemptive_rights_egm():
    r = _rec(129)
    text = _text(129)
    rights = " ".join(r["rights_en"]).lower()
    assert "suspend the preemptive rights" in rights or "suspend" in rights
    assert "suspend" in text
    cond = " ".join(r["conditions_en"]).lower()
    assert "articles of association" in cond
    assert "articles of association" in text


def test_art130_sell_or_assign_rights():
    r = _rec(130)
    text = _text(130)
    rights = " ".join(r["rights_en"]).lower()
    assert "sell or assign" in rights
    assert "sell or assign" in text
    assert "regulations" in " ".join(r["conditions_en"]).lower()
    assert "regulations" in text


def test_art132_losses_half_60_180_days():
    r = _rec(132)
    text = _text(132)
    assert any("60 days" in d.lower() for d in r["deadlines_en"])
    assert any("180 days" in d.lower() for d in r["deadlines_en"])
    assert "60 days" in text and "180 days" in text
    cond = " ".join(r["conditions_en"]).lower()
    assert "half of the issued capital" in cond
    assert "half of the issued capital" in text


def test_art133_capital_decrease_methods():
    r = _rec(133)
    text = _text(133)
    eff = " ".join(r["legal_effects_en"]).lower()
    assert "cancel" in eff and "nominal value" in eff
    assert "nominal value" in text
    # No creditors/authority actors unless the (excluded) 134/135 text is imported.
    assert "creditor" not in " ".join(r["actors_en"]).lower()


# -- only Sections 1-5 English LLM files ------------------------------------
def test_only_sections_1_to_5_files():
    files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(LLM_DIR, "*_en_legal_llm.json")))
    assert files == ["book4_section1_en_legal_llm.json",
                     "book4_section2_en_legal_llm.json",
                     "book4_section3_en_legal_llm.json",
                     "book4_section4_en_legal_llm.json",
                     "book4_section5_en_legal_llm.json"], files


def test_sections_1_4_unchanged():
    s1 = _read(os.path.join(LLM_DIR, "book4_section1_en_legal_llm.json"))
    assert [r["article_numbers"] for r in s1["records"]] == [[58], [59], [60], [66]]
    s2 = _read(os.path.join(LLM_DIR, "book4_section2_en_legal_llm.json"))
    assert [r["article_numbers"] for r in s2["records"]] == [[67], [68], [71], [72], [75], [77]]
    s3 = _read(os.path.join(LLM_DIR, "book4_section3_en_legal_llm.json"))
    assert [r["article_numbers"] for r in s3["records"]] == [[85], [87], [92], [93], [99], [101], [102]]
    s4 = _read(os.path.join(LLM_DIR, "book4_section4_en_legal_llm.json"))
    assert [r["article_numbers"] for r in s4["records"]] == [[108], [113], [115], [117]]


# -- no Books 1-3 English LLM files ------------------------------------------
def test_no_books_1_3_english_llm_files():
    for f in glob.glob(os.path.join(LLM_DIR, "*_en_legal_llm.json")):
        assert os.path.basename(f).startswith("book4_"), f


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
    s5 = _read(os.path.join(layer, "book4_section5_ar_legal_llm.json"))
    assert [r["article_numbers"] for r in s5["records"]] == [[123, 124], [126, 127], [128, 129, 130], [132], [133]]


def test_book4_provisions_unchanged():
    doc = _read(os.path.join(ROOT, "data", "articles", "book4_provisions_121_137.json"))
    assert [p["source_article_numbers"] for p in doc["provisions"]] == [[123, 124], [126, 127], [128, 129, 130], [132], [133]]


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
