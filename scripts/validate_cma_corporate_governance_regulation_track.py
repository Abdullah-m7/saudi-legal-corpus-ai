#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the CMA Corporate Governance Regulations track (95
articles, 12 أبواب, 5 of which are further divided into فصول; 84 اصلية + 11
معدلة -- Articles 20, 24, 27, 37, 52, 54, 73, 74, 75, 87, 90, amended by CMA
Board Resolutions 2018-35-1, 2018-52-4, 2022-94-1 and/or 2023-5-8).

VERIFICATION TIER -- see the generator's module docstring and
sources/cma_corporate_governance_regulation/law/official_source/
cma_corporate_governance_regulation_official_source.json's
verification_methodology_note for the full account. This validator asserts:
exactly 95 articles in a clean 1..95 run; exactly 12 non-empty
chapter_structure entries (أبواب); every article carries a non-empty
section_ar; exactly Articles 20/24/27/37/52/54/73/74/75/87/90 are معدلة with
non-empty amendment history (each explicitly disclosing
pre_amendment_text_recovered=false), and every other article is اصلية with
empty history; no ملغاة/مضافة articles (none confirmed); no bare footnote
markers or latin/html leftovers survive in any article's text."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "cma_corporate_governance_regulation", "law", "official_source",
                    "cma_corporate_governance_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "cma_corporate_governance_regulation", "law", "verified",
                        "cma_corporate_governance_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "cma_corporate_governance_regulation", "law", "verified",
                        "cma_corporate_governance_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "cma_corporate_governance_regulation_arabic_legal_llm",
                    "cma_corporate_governance_regulation_legal_llm_001_095.json")
N = 95
KEY_RE = r"cma_corporate_governance_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 84, "معدلة": 11, "ملغاة": 0, "مضافة": 0}
AMENDED_ARTICLE_NUMBERS = {20, 24, 27, 37, 52, 54, 73, 74, 75, 87, 90}
STATUS = "CMA_GOV_SA_OFFICIAL_PDF_PRIMARY_X_LIGATURE_DEFECT_CORRECTED_X_AMENDMENT_FOOTNOTE_CROSSCHECK"
EXPECTED_CHAPTERS = 12
FLAGGED_DISCREPANCY_KEYS = {
    "cma_corp_gov_2006_regulation_fully_superseded_not_amended",
    "cma_corp_gov_article_count_19_light_pass_wrong",
    "cma_corp_gov_1440h_amendment_article_mapping_unconfirmed",
    "cma_corp_gov_pdf_font_transposition_defect_and_correction",
    "cma_corp_gov_article_088_missing_madda_prefix",
    "cma_corp_gov_full_renumbering_map_incomplete",
    "cma_corp_gov_annex_1_not_ingested",
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


def _bare_footnote_marker(text):
    # A footnote marker is a bare 1-2 digit number at the start of a line with
    # no following ')' -- this document's own numbered list items always use
    # the ')N' convention, so any surviving 'N<non-paren>' line start would be
    # leaked footnote text.
    for line in text.split("\n"):
        if re.match(r'^\d{1,2}(?!\))', line.strip()):
            return True
    return False


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
    if not chapters or len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d Part (باب) entries in chapter_structure, got %r"
                 % (EXPECTED_CHAPTERS, len(chapters) if chapters else chapters))
    else:
        for c in chapters:
            if not c.get("label_ar", "").startswith("الباب"):
                e.append("[1c] chapter label %r does not use الباب (Part)" % c.get("label_ar"))
        covered = set()
        for c in chapters:
            span = c.get("articles", "")
            if "-" in span:
                lo, hi = span.split("-")
                covered |= set(range(int(lo), int(hi) + 1))
            elif span:
                covered.add(int(span))
        if covered != set(range(1, N + 1)):
            e.append("[1c] chapter_structure article coverage incomplete/overlapping: "
                     "missing %s" % sorted(set(range(1, N + 1)) - covered))

    if src.get("consolidated_amended_law") is not True:
        e.append("[1d] consolidated_amended_law must be True for this track (multi-"
                 "resolution consolidated current text)")

    sc = Counter()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
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
            e.append("[2] %s: section_ar must be non-empty" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if _bare_footnote_marker(a["text"]):
            e.append("[2] %s: leaked footnote marker/text in article body" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)

        expect_amended = n in AMENDED_ARTICLE_NUMBERS
        if expect_amended:
            if ls != "معدلة":
                e.append("[3] %s: article %d must be معدلة (confirmed amendment)" % (k, n))
            if not a.get("history"):
                e.append("[3] %s: amended article %d must carry non-empty history" % (k, n))
            else:
                for h in a["history"]:
                    if h.get("pre_amendment_text_recovered") is not False:
                        e.append("[3] %s: history entry must explicitly disclose "
                                 "pre_amendment_text_recovered=false (not recovered this pass)" % k)
                    if not h.get("instrument"):
                        e.append("[3] %s: history entry missing instrument citation" % k)
        else:
            if ls != "اصلية":
                e.append("[3] %s: article %d expected اصلية, got %r" % (k, n, ls))
            if a.get("history"):
                e.append("[3] %s: non-amended article %d must have empty history" % (k, n))

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

    if not src.get("amending_instruments"):
        e.append("[2g] missing amending_instruments list")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: unknown article_key" % r["article_key"]); continue
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation', got %r"
                     % (r["article_key"], r.get("law_component")))
        if "article_number" not in r:
            e.append("[4] %s: missing article_number field" % r["article_key"])
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        n = int(re.match(KEY_RE, r["article_key"]).group(1))
        expect_amended = n in AMENDED_ARTICLE_NUMBERS
        if r.get("is_amended") != expect_amended:
            e.append("[4] %s: is_amended flag mismatch (expected %r)" % (r["article_key"], expect_amended))
        if r.get("is_repealed") or r.get("is_added"):
            e.append("[4] %s: unexpected repealed/added flag" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts mismatch with source")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: unknown article_key" % r["article_key"]); continue
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation', got %r"
                     % (r["article_key"], r.get("law_component")))
        if "article_number" not in r:
            e.append("[5] %s: missing article_number field" % r["article_key"])
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in CMA Corporate Governance Regulation track:" % len(e))
        for x in e[:30]:
            print("  - %s" % x)
        return 1
    print("PASS: CMA Corporate Governance Regulations — 95 records "
          "(84 اصلية, 11 معدلة: Articles 20/24/27/37/52/54/73/74/75/87/90, "
          "0 ملغاة, 0 مضافة; 12 أبواب)")
    print("  - TIER: cma.gov.sa official PDF primary, font/CMap letter-transposition")
    print("    defect corrected via explicit whole-word verification (not a blind rule)")
    print("  - IN-FORCE Resolution 2017-16-8 (16/5/1438H = 13/2/2017G), amended by")
    print("    2018-35-1, 2018-52-4, 2022-94-1, 2023-5-8 (25/6/1444H = 18/1/2023G)")
    print("  - CORRECTED prior premise: this regulation FULLY SUPERSEDED (not merely")
    print("    amended) Resolution 1-212-2006 (21/10/1427H); current law is 95")
    print("    articles, not the ~19 a prior light pass cited")
    print("  - 15/9/1440H (2019) amendment confirmed real via secondary source but NOT")
    print("    matched to a footnote in the current numbering (disclosed, not guessed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
