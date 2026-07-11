#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Labor Annex 5 track (model contract forms).

Trust gate: 4 forms with the expected unit counts (17+30+25+29=101) + the
permanent form's 8-row glossary = 102 records. Language separation enforced
(no latin in any governing Arabic text; English only in text_en_reference and
only for the bilingual permanent form). Verification method per unit: pure-OCR
units must clear the 0.85 floor; all others must be marked image-verified.
Glossary linearization must be byte-reproducible from the committed cells."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "labor", "annex5", "official_source",
                   "labor_annex5_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "labor", "annex5", "verified",
                       "labor_annex5_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "labor_arabic_legal_llm",
                   "labor_annex5_contract_forms_llm.json")
STATUS = "HRSD_OFFICIAL_PDF_OCR_IMAGE_CROSS_CHECKED_BILINGUAL_FORM"
EXPECTED_UNITS = {"permanent": 17, "part_time": 30, "casual_temporary": 25, "seasonal": 29}
GLOSSARY_ROWS = 8
N = sum(EXPECTED_UNITS.values()) + 1  # + glossary record
OCR_FLOOR = 0.85


def _glossary_texts(g):
    ar_lines, en_lines = ["جدول المصطلحات"], ["Glossary of terms"]
    for row in g["rows"]:
        term_ar, term_en, def_ar, def_en = row
        ar_lines.append("%s: %s" % (term_ar, def_ar))
        en_lines.append("%s: %s" % (term_en, def_en))
    return "\n".join(ar_lines), "\n".join(en_lines)


def main():
    e = []
    for p in (SRC, RECORDS, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    forms = {f["form_key"]: f for f in src["forms"]}

    # [1] structure: 4 forms, expected unit counts, glossary rows
    if set(forms) != set(EXPECTED_UNITS):
        e.append("[1] form keys mismatch: %s" % sorted(forms))
    for fk, want in EXPECTED_UNITS.items():
        got = len(forms.get(fk, {}).get("units", []))
        if got != want:
            e.append("[1] form %s: %d units != %d" % (fk, got, want))
    g = forms.get("permanent", {}).get("glossary_table", {})
    if len(g.get("rows", [])) != GLOSSARY_ROWS:
        e.append("[1] glossary rows != %d" % GLOSSARY_ROWS)
    for row in g.get("rows", []):
        if len(row) != 4 or not all(str(c).strip() for c in row):
            e.append("[1] glossary row malformed: %r" % str(row[0])[:20])

    # [2] units: language separation + verification method
    for fk, form in forms.items():
        bilingual = bool(form.get("bilingual"))
        for u in form["units"]:
            k = u["unit_key"]
            if not u["text_ar"].strip():
                e.append("[2] %s: empty text_ar" % k)
            if re.search(r"[A-Za-z]", u["text_ar"]):
                e.append("[2] %s: latin chars in governing Arabic text" % k)
            if not bilingual and u.get("text_en_reference", "").strip():
                e.append("[2] %s: English in a non-bilingual form" % k)
            method = u.get("verification", "")
            if method == "ocr":
                if (u.get("ocr_similarity_ar") or 0) < OCR_FLOOR:
                    e.append("[2] %s: pure-OCR unit below %.2f floor" % (k, OCR_FLOOR))
                if bilingual and u.get("text_en_reference", "").strip() and \
                        (u.get("ocr_similarity_en") or 0) < OCR_FLOOR:
                    e.append("[2] %s: English side below OCR floor" % k)
            elif "image" not in method:
                e.append("[2] %s: unverified unit (method %r)" % (k, method))

    # [3] verified records: counts, verbatim, glossary reproducibility, boundaries
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[3] %d verified records != %d" % (len(ver), N))
    vmap = {r["article_key"]: r for r in ver}
    for fk, form in forms.items():
        for u in form["units"]:
            r = vmap.get(u["unit_key"], {})
            if r.get("article_text_verified") != u["text_ar"]:
                e.append("[3] %s: text != source" % u["unit_key"])
            if form.get("bilingual") and r.get("text_en_reference") != u.get("text_en_reference", ""):
                e.append("[3] %s: english reference != source" % u["unit_key"])
    ar_expect, en_expect = _glossary_texts(g)
    gr = vmap.get("permanent_glossary_table", {})
    if gr.get("article_text_verified") != ar_expect or gr.get("text_en_reference") != en_expect:
        e.append("[3] glossary linearization not byte-reproducible from source cells")
    for r in ver:
        if r.get("official_text_status") != STATUS:
            e.append("[3] %s: bad status" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[3] %s: %s must be False" % (r["article_key"], f))

    # [4] LLM layer verbatim/hashes
    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[4] llm count != %d" % N)
    for r in recs:
        if r["article_text_ar"] != vmap[r["article_key"]]["article_text_verified"]:
            e.append("[4] %s: llm text != verified" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[4] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[4] %s: missing retrieval metadata" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Labor Annex 5 track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Labor Annex 5 track — 102 records (4 model contract forms, 101 units + 8-row glossary)")
    print("  - unit counts 17+30+25+29; language separation enforced (zero latin in governing Arabic)")
    print("  - every unit verified: pure-OCR >= %.2f or image-verified (method recorded per unit)" % OCR_FLOOR)
    print("  - glossary linearization byte-reproducible; English is the official form's own column, non-governing")
    print("  - texts verbatim vs committed source; hashes consistent; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
