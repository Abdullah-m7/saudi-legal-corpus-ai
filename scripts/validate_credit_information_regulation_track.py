#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Credit
Information Law track (55 records, brand-2011 regulation: 55 اصلية, flat with
12 informal -- unlabeled, no فصل/باب -- topical headings reproduced from the
source document's own table of contents).

VERIFICATION TIER -- see the generator's module docstring and
sources/credit_information_regulation/law/official_source/
credit_information_regulation_official_source.json's verification_methodology_note
for the full account. This is a long-standing (2011) instrument with NO
amendments confirmed to date after a dedicated search pass, so this validator
asserts that every article is اصلية, that there are NO معدلة/ملغاة/مضافة
articles, and that no amendment_history is present. Unlike this corpus's
rett_regulation track (genuinely flat, no headings at all), this Regulation's
12 topical headings ARE real (printed in the source's own table of contents
and recurring inline), so -- unlike rett_regulation -- this validator expects
chapter_structure to be POPULATED (12 entries) and section_ar to be populated
on every article with its topical heading."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "credit_information_regulation", "law", "official_source",
                   "credit_information_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "credit_information_regulation", "law", "verified",
                       "credit_information_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "credit_information_regulation", "law", "verified",
                       "credit_information_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "credit_information_regulation_arabic_legal_llm",
                   "credit_information_regulation_legal_llm_001_055.json")
N = 55
KEY_RE = r"credit_information_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 55, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
STATUS = "BAYANCB_WAYBACK_PRIMARY_TWO_PIPELINE_OCR_X_SAMA_RULEBOOK_SECONDARY_CROSS_VERIFIED"
EXPECTED_CHAPTERS = 12
FLAGGED_DISCREPANCY_KEYS = {
    "credit_information_regulation_bayancb_url_rotated",
    "credit_information_regulation_sama_gov_sa_unreachable",
    "credit_information_regulation_gazette_publication_details_unconfirmed",
    "credit_information_regulation_ocr_hamza_and_gap_corrections",
}
AR = "ء-ي"


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        if (re.match("[%s]" % AR, before) and before != "ه"
                and re.match("[%s]" % AR, after)):
            bad += 1
    return bad


def main():
    for p in (SRC, RECORDS, SUMMARY, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1

    e = []
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    if src.get("article_count") != N:
        e.append("[1] article_count field %r != %d" % (src.get("article_count"), N))
    seen = set()
    for k in arts:
        m = re.match(KEY_RE, k)
        if not m:
            e.append("[1] %s: does not match key pattern" % k)
        else:
            seen.add(int(m.group(1)))
    if seen != set(range(1, N + 1)):
        e.append("[1] article numbers not a clean 1..%d run: %s" % (N, sorted(seen)))

    chapters = src.get("chapter_structure")
    if not isinstance(chapters, list) or len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d topical chapter_structure entries, got %r" %
                 (EXPECTED_CHAPTERS, chapters))
    else:
        covered = set()
        for c in chapters:
            if not c.get("title_ar"):
                e.append("[1c] chapter_structure entry missing title_ar: %r" % c)
                continue
            m = re.match(r"^(\d+)-(\d+)$", c.get("articles", ""))
            if not m:
                e.append("[1c] chapter_structure entry has bad 'articles' range: %r" % c)
                continue
            lo, hi = int(m.group(1)), int(m.group(2))
            covered.update(range(lo, hi + 1))
        if covered != set(range(1, N + 1)):
            e.append("[1c] chapter_structure article ranges do not cover a clean 1..%d run" % N)

    if src.get("consolidated_amended_law") is not False:
        e.append("[1d] consolidated_amended_law must be False for this un-amended regulation")

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar", "").strip():
            e.append("[2] %s: section_ar must be populated (real topical heading)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if a.get("history"):
            e.append("[2] %s: un-amended regulation must have no amendment history" % k)
        if ls != "اصلية":
            e.append("[2] %s: every article must be اصلية in this un-amended regulation" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)
        if re.search(r"ا[ثتن]تمان", a["text"]):
            e.append("[2] %s: residual OCR hamza-misread artifact (اثتمان/اتتمان/انتمان) "
                      "not normalized to ائتمان" % k)
        if "»" in a["text"]:
            e.append("[2] %s: residual OCR stray '»' punctuation artifact" % k)
        nums = re.findall(r"(?m)^(\d+)-", a["text"])
        if nums:
            nums_i = [int(x) for x in nums]
            if nums_i != list(range(1, len(nums_i) + 1)):
                e.append("[2] %s: numbered sub-item run not a clean 1..%d sequence: %s" %
                         (k, len(nums_i), nums_i))

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the tier")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    if not src.get("parent_law", {}).get("law_key") == "credit_information":
        e.append("[2g] missing/incorrect parent_law cross-reference to credit_information")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    seen_nums = set()
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: unknown article_key" % r["article_key"]); continue
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation', got %r" %
                     (r["article_key"], r.get("law_component")))
        if not isinstance(r.get("article_number"), int):
            e.append("[4] %s: missing/invalid article_number field" % r["article_key"])
        else:
            seen_nums.add(r["article_number"])
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("is_amended") or r.get("is_repealed") or r.get("is_added"):
            e.append("[4] %s: unexpected amended/repealed/added flag" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))
    if seen_nums != set(range(1, N + 1)):
        e.append("[4] verified records' article_number values not a clean 1..%d run" % N)

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts mismatch with source")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    seen_llm_nums = set()
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: unknown article_key" % r["article_key"]); continue
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation', got %r" %
                     (r["article_key"], r.get("law_component")))
        if not isinstance(r.get("article_number"), int):
            e.append("[5] %s: missing/invalid article_number field" % r["article_key"])
        else:
            seen_llm_nums.add(r["article_number"])
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])
    if seen_llm_nums != set(range(1, N + 1)):
        e.append("[5] llm records' article_number values not a clean 1..%d run" % N)

    if e:
        print("FAIL: %d error(s) in Credit Information Implementing Regulation track:" % len(e))
        for x in e[:25]:
            print("  - %s" % x)
        return 1
    print("PASS: Credit Information Implementing Regulation — 55 records (55 اصلية, 12 "
          "topical headings)")
    print("  - TIER: bayancb.com Wayback-archived primary PDF (Tesseract OCR x PyMuPDF "
          "geometric two-pipeline reconciliation) x")
    print("    rulebook.sama.gov.sa secondary structural/numeric cross-verification")
    print("  - IN-FORCE SAMA Governor's Decision No. أق/13709 (22/9/1432H = 21 Aug 2011G); "
          "no amendments confirmed to date")
    print("  - FLAGGED: sama.gov.sa's own PDF unreachable in this environment; bayancb.com's "
          "media-GUID rotated (Wayback used instead); Official Gazette issue/date not "
          "independently confirmed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
