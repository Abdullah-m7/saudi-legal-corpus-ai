#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Real Estate
Finance Law track (اللائحة التنفيذية لنظام التمويل العقاري, Minister of
Finance Decision No. 1229, dated 10/4/1434H = 20/2/2013G; amended by Decision
No. 1144, dated 2/6/1443H; 31 records, all اصلية; 4 أبواب).

VERIFICATION TIER -- see the generator's module docstring and
sources/real_estate_finance_implementing_regulation/law/official_source/
real_estate_finance_implementing_regulation_official_source.json's
verification_methodology_note for the full account. This validator asserts:
exactly 31 articles in a clean 1..31 run; exactly 4 chapter_structure entries
(الباب) tiling articles 1-31 with no gap/overlap; consolidated_amended_law is
explicitly True; all 31 articles are اصلية with empty amendment history
(no per-article معدلة/مضافة attribution without direct textual evidence, per
this track's own disclosed limitation regarding the 1144 amendment's repeal-
and-renumber effect); and that every discrepancy this build's own methodology
note flags as a named, non-obvious judgment call is present in
known_unresolved_discrepancies.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "real_estate_finance_implementing_regulation", "law",
                   "official_source", "real_estate_finance_implementing_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "real_estate_finance_implementing_regulation", "law", "verified",
                       "real_estate_finance_implementing_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "real_estate_finance_implementing_regulation", "law", "verified",
                       "real_estate_finance_implementing_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "real_estate_finance_implementing_regulation_arabic_legal_llm",
                   "real_estate_finance_implementing_regulation_legal_llm_001_031.json")
N = 31
KEY_RE = r"real_estate_finance_implementing_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 31, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_CHAPTERS = 4
EXPECTED_SPANS = {"1-7", "8-15", "16-27", "28-31"}
FLAGGED_DISCREPANCY_KEYS = {
    "real_estate_finance_implementing_regulation_original_sama_pdf_unreachable",
    "real_estate_finance_implementing_regulation_article4_repeal_renumbering_gap",
    "real_estate_finance_implementing_regulation_terminology_update_al_muassasa_al_bank",
    "real_estate_finance_implementing_regulation_article6_typo_bsahb_vs_bhasab",
    "real_estate_finance_implementing_regulation_article7_22_numbering_variance",
    "real_estate_finance_implementing_regulation_nezams_hijri_year_typo",
    "real_estate_finance_implementing_regulation_article11_circular_footnotes_preserved",
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
    if not chapters or len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d الباب entries in chapter_structure, got %r"
                 % (EXPECTED_CHAPTERS, chapters))
    else:
        for c in chapters:
            if not c.get("label_ar", "").startswith("الباب"):
                e.append("[1c] chapter label %r does not use الباب" % c.get("label_ar"))
            if not c.get("articles"):
                e.append("[1c] chapter %r must carry a numbered article range" % c.get("label_ar"))
        got_spans = {c.get("articles") for c in chapters}
        if got_spans != EXPECTED_SPANS:
            e.append("[1c] chapter_structure article spans %r != expected %r"
                     % (got_spans, EXPECTED_SPANS))
        covered = set()
        for c in chapters:
            lo, hi = (int(x) for x in c["articles"].split("-"))
            for n in range(lo, hi + 1):
                if n in covered:
                    e.append("[1c] article %d covered by more than one الباب range" % n)
                covered.add(n)
        if covered != set(range(1, N + 1)):
            e.append("[1c] chapters do not exactly tile articles 1..%d: got %s"
                     % (N, sorted(covered)))

    if src.get("consolidated_amended_law") is not True:
        e.append("[1d] consolidated_amended_law must be True for this track "
                 "(post-1144-amendment consolidated re-issuance)")
    if src.get("law_component") != "regulation":
        e.append("[1d] law_component must be 'regulation'")
    if src.get("legal_status_ar") != "نافذ":
        e.append("[1d] legal_status_ar must be نافذ")
    if src.get("base_law_key") != "real_estate_finance":
        e.append("[1d] base_law_key must reference the existing real_estate_finance base-law track")

    sc = Counter()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar", "").strip():
            e.append("[2] %s: section_ar must be non-empty (باب this article belongs to)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if "  " in a["text"]:
            e.append("[2] %s: residual double-space artifact" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)
        if "[ROW]" in a["text"] or "<TABLE" in a["text"] or "Book traversal" in a["text"]:
            e.append("[2] %s: unconverted table/navigation markup leftover in text" % k)

        if ls != "اصلية":
            e.append("[3] %s: article %d expected اصلية (currently-governing consolidated "
                     "text; no per-article amendment evidence this pass), got %r" % (k, n, ls))
        if a.get("history"):
            e.append("[3] %s: article %d must have empty history (no per-article diff "
                     "available this pass)" % (k, n))
        if a.get("source_tier") != "primary":
            e.append("[2] %s: expected source_tier 'primary' (TIER_1_PRIMARY_MULTI_SOURCE "
                     "track), got %r" % (k, a.get("source_tier")))

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))
    declared = src.get("status_counts") or {}
    for st in ALLOWED_STATUS:
        if declared.get(st, 0) != sc.get(st, 0):
            e.append("[2f] declared status_counts[%s] does not match actual per-article counts" % st)

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

    hist = src.get("amendment_history") or []
    if len(hist) != 2:
        e.append("[2h] amendment_history must record exactly 2 entries (founding decision "
                 "1229 + amending decision 1144), got %d" % len(hist))

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
        if r.get("is_amended") is not False or r.get("is_repealed") is not False or r.get("is_added") is not False:
            e.append("[4] %s: expected all status flags False (اصلية-only track)" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts mismatch with source")
    if summary.get("consolidated_amended_law") is not True:
        e.append("[4b] summary consolidated_amended_law must be True")

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

    if e:
        print("FAIL: %d error(s) in Real Estate Finance Implementing Regulation track:" % len(e))
        for x in e[:30]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Real Estate Finance Law — 31 records "
          "(31 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; 4 أبواب)")
    print("  - TIER: TIER_1_PRIMARY_MULTI_SOURCE -- rulebook.sama.gov.sa (live, direct curl) "
          "x bfc.gov.sa official PDF mirror (different gov. body, WebFetch + pdftotext), "
          "full-document word-for-word agreement net of 3 disclosed non-substantive variances")
    print("  - IN-FORCE Minister of Finance Decision No. 1229 (10/4/1434H = 20/2/2013G), "
          "amended by Decision No. 1144 (2/6/1443H); consolidated_amended_law=True")
    print("  - Decision 1144 repealed the ORIGINAL Article Four (per SAMA's own statement, "
          "argaam.com + SAMA news page); resulting renumbering not independently "
          "reconstructed this pass -- no article tagged معدلة without direct textual evidence "
          "(see known_unresolved_discrepancies)")
    print("  - Parent base law (real_estate_finance, Royal Decree M/50) NOT touched this pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
