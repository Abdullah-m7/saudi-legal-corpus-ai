#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the verified Civil Transactions Law Arabic text (721 articles)."""

from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "sources", "civil", "law", "official_source",
                      "civil_transactions_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "civil", "law", "verified",
                       "civil_transactions_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "civil", "law", "verified",
                       "civil_transactions_law_verified_summary.json")

EXPECTED = 721
SECTION_HEADING = re.compile(r"^\s*(الكتاب|الباب|الفصل|القسم|الفرع)\s")


def main():
    errors = []
    for p in (SOURCE, RECORDS, SUMMARY):
        if not os.path.isfile(p):
            print("FAIL: missing file: %s" % os.path.relpath(p, ROOT))
            return 1

    src = json.load(open(SOURCE, encoding="utf-8"))
    arts = src["articles"]
    records = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]

    if len(records) != EXPECTED:
        errors.append("[1] expected %d records, found %d" % (EXPECTED, len(records)))
    if [r["article_number"] for r in records] != list(range(1, EXPECTED + 1)):
        errors.append("[1] article_number sequence not 1..%d" % EXPECTED)
    if len(arts) != EXPECTED:
        errors.append("[1] source artifact has %d articles, expected %d" % (len(arts), EXPECTED))

    for r in records:
        n = r["article_number"]
        a = arts.get(str(n), {})
        if r.get("article_key") != "civil_law_art_%03d" % n:
            errors.append("[2] art %s: article_key %r" % (n, r.get("article_key")))
        # [3] text + section context match the committed source verbatim
        if r.get("article_text_verified") != a.get("text"):
            errors.append("[3] art %s: verified text != source" % n)
        if r.get("section_context_ar") != a.get("section_context", ""):
            errors.append("[3] art %s: section_context != source" % n)
        text = r.get("article_text_verified", "")
        if not text.strip():
            errors.append("[3] art %s: empty verified text" % n)
        # [4] no structural heading lines left inside bodies; no latin junk
        for ln in text.split("\n"):
            if SECTION_HEADING.match(ln):
                errors.append("[4] art %s: structural heading line left in body: %r" % (n, ln[:40]))
        if re.search(r"[A-Za-z]{2,}", text):
            errors.append("[4] art %s: latin characters in body" % n)
        # [5] honest boundaries
        if r.get("official_text_status") != "OWNER_PROVIDED_CROSS_CHECKED_MOJ_PORTAL":
            errors.append("[5] art %s: unexpected official_text_status %r" % (n, r.get("official_text_status")))
        for flag in ("translation_performed", "legal_interpretation_performed",
                     "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(flag) is not False:
                errors.append("[5] art %s: boundary flag %s must be False" % (n, flag))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != len(records):
        errors.append("[6] summary record_count mismatch")

    # [7] MOJ cross-check upgrade: corrections applied, audit artifacts + PDF committed
    import hashlib
    src_doc = json.load(open(SOURCE, encoding="utf-8"))
    cc = src_doc.get("moj_cross_check") or {}
    if len(cc.get("corrections", [])) != 18 or len(cc.get("headings_moved", [])) != 21:
        errors.append("[7] moj_cross_check block incomplete (%d corrections, %d heading moves)"
                      % (len(cc.get("corrections", [])), len(cc.get("headings_moved", []))))
    pdf_p = os.path.join(ROOT, "inputs", "civil_official_pdfs",
                         "civil_transactions_law_moj_official_ar.pdf")
    audit1 = os.path.join(ROOT, "sources", "civil", "law", "moj_cross_check",
                          "civil_moj_cross_check.json")
    audit2 = os.path.join(ROOT, "sources", "civil", "law", "moj_cross_check",
                          "civil_pdf_adjudication.json")
    for pth in (pdf_p, audit1, audit2):
        if not os.path.isfile(pth):
            errors.append("[7] missing audit artifact: %s" % os.path.relpath(pth, ROOT))
    if os.path.isfile(pdf_p):
        sha = hashlib.sha256(open(pdf_p, "rb").read()).hexdigest()
        if sha != cc.get("pdf_sha256"):
            errors.append("[7] committed MOJ PDF sha256 mismatch")
    by_num = {r["article_number"]: r["article_text_verified"] for r in records}
    # adjudicated word corrections must be present (spot substrings) and defects absent
    SPOT = [(41, "إذا تم", "\nذا "), (148, "سيئ الني", "سيء الني"),
            (654, "وحال الطرفان", "وحال الطرفين"), (666, "الأعذار", "الإعذار"),
            (677, "الحادية والخمسون بعد الستمائة", None),
            (701, "عقاري منفصلين", "عقارين"), (715, "جزيء العقار", None)]
    import re as _re
    def _bare(t):
        # strip harakat/tatweel only (explicit codepoints; NOT a letter range)
        return _re.sub("[\u0610-\u061a\u064b-\u065f\u0670\u0640]", "", t)
    for n, must, mustnot in SPOT:
        bt = _bare(by_num.get(n, ""))
        if must and _bare(must) not in bt:
            errors.append("[7] art %d: adjudicated correction %r missing" % (n, must))
        if mustnot and _bare(mustnot.replace("\\n", "\n")) in bt:
            errors.append("[7] art %d: defective form %r still present" % (n, mustnot))
    # moved headings must live in the next article's section_context
    for mv in cc.get("headings_moved", []):
        nxt = next((r for r in records if r["article_number"] == mv["to_article_section_context"]), None)
        if not nxt or (nxt.get("section_context_ar") or "").strip() != mv["heading"].strip():
            errors.append("[7] heading move to art %s not reflected in section_context"
                          % mv["to_article_section_context"])

    if errors:
        print("FAIL: %d error(s) in verified Civil Transactions Law text:" % len(errors))
        for e in errors[:20]:
            print("  - %s" % e)
        return 1

    print("PASS: %d verified Civil Transactions Law articles" % len(records))
    print("  - complete 1..721 sequence; text + section context match committed source verbatim")
    print("  - no structural headings inside bodies; no latin junk")
    print("  - MOJ cross-check upgrade enforced: 18 adjudicated corrections + 21 heading moves applied;")
    print("    audit artifacts + official MOJ PDF committed (sha verified)")
    print("  - Arabic governs; owner-provided text cross-checked vs the official MOJ portal; no translation/paraphrase/interpretation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
