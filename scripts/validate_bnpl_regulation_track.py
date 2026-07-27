#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Rules for Regulating Buy-Now-Pay-Later (BNPL)
Companies track (قواعد تنظيم شركات الدفع الآجل (BNPL), Governor's Decision
No. 145/م ش ت, dated 23/5/1445H, transmitted via SAMA Circular No.
450360390000, dated 5/6/1445H = 17/12/2023G; 31 records, 30 اصلية + 1 معدلة;
6 chapters/الفصول, EVERY chapter carrying at least one numbered article --
unlike this corpus's debt_collection_regulation track).

VERIFICATION TIER -- see the generator's module docstring and
sources/bnpl_regulation/law/official_source/bnpl_regulation_official_source.json's
verification_methodology_note for the full account. This validator asserts:
exactly 31 articles in a clean 1..31 run; exactly 6 chapter_structure
entries (الفصل, not الباب), all six carrying a numbered article range that
exactly tiles articles 1..31 with no gap/overlap (no unnumbered chapter,
unlike debt_collection_regulation); exactly 30 اصلية + 1 معدلة article
(Article 22, credit limits) with a non-empty, well-formed history[] entry
carrying both pre- and post-amendment wording; no ملغاة/مضافة articles this
pass.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "bnpl_regulation", "law", "official_source",
                   "bnpl_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "bnpl_regulation", "law", "verified",
                       "bnpl_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "bnpl_regulation", "law", "verified",
                       "bnpl_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "bnpl_regulation_arabic_legal_llm",
                   "bnpl_regulation_legal_llm_001_031.json")
N = 31
KEY_RE = r"bnpl_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 30, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
STATUS = "SAMA_RULEBOOK_PRIMARY_AR_EN_BILINGUAL_HTML_AMENDMENT_NODE_CROSS_VERIFIED"
EXPECTED_CHAPTERS = 6
AMENDED_ARTICLE_KEY = "bnpl_regulation_art_022"
FLAGGED_DISCREPANCY_KEYS = {
    "bnpl_regulation_title_naming_variance_from_brief",
    "bnpl_regulation_article_022_amended_credit_cap_raised",
    "bnpl_regulation_article_020_fee_prohibition_suspension_note",
    "bnpl_regulation_transmittal_circular_article_019_2000_sar_exemption",
    "bnpl_regulation_original_pdf_scanned_ocr_incomplete",
    "bnpl_regulation_english_used_for_structure_and_footnotes_only",
    "bnpl_regulation_single_ar_source_no_second_independent_crosscheck",
    "bnpl_regulation_related_out_of_scope_licensing_guidelines_document",
    "bnpl_regulation_no_boe_lawid_regulation_level",
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
        e.append("[1c] expected %d الفصل entries in chapter_structure, got %r"
                 % (EXPECTED_CHAPTERS, chapters))
    else:
        for c in chapters:
            if not c.get("label_ar", "").startswith("الفصل"):
                e.append("[1c] chapter label %r does not use الفصل" % c.get("label_ar"))
            if not c.get("articles"):
                e.append("[1c] every chapter in this track must carry a numbered article "
                          "range (no unnumbered chapter expected): %r" % c)
        covered = set()
        for c in chapters:
            lo, hi = (int(x) for x in c["articles"].split("-"))
            for n in range(lo, hi + 1):
                if n in covered:
                    e.append("[1c] article %d covered by more than one الفصل range" % n)
                covered.add(n)
        expected_spans = {"1-3", "4-12", "13-18", "19-27", "28-29", "30-31"}
        got_spans = {c.get("articles") for c in chapters}
        if got_spans != expected_spans:
            e.append("[1c] chapter_structure article spans %r != expected %r"
                     % (got_spans, expected_spans))
        if covered != set(range(1, N + 1)):
            e.append("[1c] chapters do not exactly tile articles 1..%d: got %s"
                     % (N, sorted(covered)))

    if src.get("consolidated_amended_law") is not False:
        e.append("[1d] consolidated_amended_law must be False for this track")
    if not (src.get("preamble_ar") or "").strip():
        e.append("[1e] preamble_ar (transmittal circular full text) must be non-empty")
    else:
        preamble = src["preamble_ar"]
        if "145" not in preamble or "450360390000" not in preamble:
            e.append("[1e] preamble_ar must contain the Governor's Decision No. (145) and "
                     "the transmittal Circular No. (450360390000)")
    if not (src.get("governor_decision") or "").strip():
        e.append("[1f] governor_decision field must be non-empty")

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
        if not a["text"].strip():
            e.append("[2] %s: empty text" % k)
        if re.search(r"[A-Za-z]", a["text"]):
            if not (("BNPL" in a["text"]) or ("Pop-Up Window" in a["text"])):
                e.append("[2] %s: unexpected latin leftovers" % k)
        if re.search(r"[<>&]", a["text"]):
            e.append("[2] %s: residual html leftovers" % k)
        if not a.get("section_ar", "").strip():
            e.append("[2] %s: section_ar must be non-empty (chapter this article belongs to)" % k)
        if not a.get("article_title_ar", "").strip():
            e.append("[2] %s: article_title_ar must be non-empty (source captions every article)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2] %s: residual Eastern-Arabic-Indic digit (must be normalized)" % k)
        if "：" in a["text"]:
            e.append("[2] %s: residual fullwidth colon (must be normalized to ':')" % k)
        if "  " in a["text"]:
            e.append("[2] %s: residual double-space artifact" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)

        if k == AMENDED_ARTICLE_KEY:
            if ls != "معدلة":
                e.append("[3] %s: expected معدلة (this track's one confirmed amendment), got %r"
                         % (k, ls))
            hist = a.get("history") or []
            if len(hist) != 1:
                e.append("[3] %s: expected exactly 1 history entry, got %d" % (k, len(hist)))
            else:
                h = hist[0]
                if not h.get("pre_amendment_text_recovered"):
                    e.append("[3] %s: pre_amendment_text_recovered must be True (recovered "
                             "verbatim from the amending circular's own page)" % k)
                if "5,000" not in (h.get("pre_amendment_text_ar") or ""):
                    e.append("[3] %s: pre_amendment_text_ar must carry the original (5,000) "
                             "SAR figure" % k)
                if "472038475" not in (h.get("instrument") or ""):
                    e.append("[3] %s: history instrument must cite Circular No. 472038475" % k)
            if "10,000" not in a["text"]:
                e.append("[3] %s: current text must reflect the post-amendment (10,000) SAR cap" % k)
        else:
            if ls != "اصلية":
                e.append("[3] %s: article %d expected اصلية (no other amendment confirmed "
                         "this pass), got %r" % (k, n, ls))
            if a.get("history"):
                e.append("[3] %s: article %d must have empty history (only Article 22 is "
                         "معدلة in this track)" % (k, n))

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

    if src.get("law_component") != "regulation":
        e.append("[2j] law_component must be 'regulation'")
    if src.get("legal_status_ar") != "نافذ":
        e.append("[2j] legal_status_ar must be نافذ")

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
        expect_amended = r["article_key"] == AMENDED_ARTICLE_KEY
        if r.get("is_amended") is not expect_amended:
            e.append("[4] %s: is_amended flag mismatch (expected %r)"
                     % (r["article_key"], expect_amended))
        if r.get("is_repealed") is not False or r.get("is_added") is not False:
            e.append("[4] %s: expected is_repealed/is_added False" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts mismatch with source")
    if not summary.get("governor_decision"):
        e.append("[4b] summary missing governor_decision")

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
        print("FAIL: %d error(s) in BNPL Regulation track:" % len(e))
        for x in e[:25]:
            print("  - %s" % x)
        return 1
    print("PASS: Rules for Regulating Buy-Now-Pay-Later (BNPL) Companies — 31 records "
          "(30 اصلية, 1 معدلة, 0 ملغاة, 0 مضافة; 6 فصول)")
    print("  - TIER: rulebook.sama.gov.sa primary (Arabic/English bilingual, born-digital HTML,")
    print("    entiresection node 6523)")
    print("  - IN-FORCE Governor's Decision No. 145/م ش ت (23/5/1445H), transmitted via Circular")
    print("    No. 450360390000 (5/6/1445H = 17/12/2023G)")
    print("  - Every chapter carries a numbered article (no unnumbered chapter, unlike")
    print("    debt_collection_regulation)")
    print("  - Article 22 (حدود الائتمان) amended by Circular No. 472038475 (4/7/1447H):")
    print("    credit cap raised 5,000 -> 10,000 SAR; pre- and post-amendment text both preserved")
    print("  - Article 20 footnote (fee-prohibition suspension, 14/2/1446H) preserved verbatim,")
    print("    NOT modeled as a textual amendment (source page text itself unchanged)")
    print("  - Arabic-original scanned PDF located (node 11012) but not OCR'd this pass -- ")
    print("    governing text rests on born-digital HTML, per known_unresolved_discrepancies")
    return 0


if __name__ == "__main__":
    sys.exit(main())
