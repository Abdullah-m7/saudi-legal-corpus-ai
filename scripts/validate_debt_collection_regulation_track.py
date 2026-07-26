#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Debt Collection Regulations and Procedures
track (ضوابط وإجراءات التحصيل, SAMA Circular No. 106889333, dated
6/9/1446H = 6/3/2025G; 11 records, all اصلية; 5 chapters/الفصول, the fifth
of which -- أحكام ختامية / Final Provisions -- carries no numbered article
of its own on the source page, per both the Arabic and English
entiresection views).

VERIFICATION TIER -- see the generator's module docstring and
sources/debt_collection_regulation/law/official_source/
debt_collection_regulation_official_source.json's verification_methodology_note
for the full account. This validator asserts: exactly 11 articles in a
clean 1..11 run; exactly 5 chapter_structure entries (الفصل, not الباب);
the first four chapters tile articles 1-11 with no gap/overlap; the fifth
chapter is explicitly marked as carrying no numbered article and its own
unnumbered closing text is preserved verbatim in closing_provisions_ar; all
11 articles are اصلية with empty amendment history (single, first-and-
only-confirmed edition); no ملغاة/معدلة/مضافة articles this pass.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "debt_collection_regulation", "law", "official_source",
                   "debt_collection_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "debt_collection_regulation", "law", "verified",
                       "debt_collection_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "debt_collection_regulation", "law", "verified",
                       "debt_collection_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "debt_collection_regulation_arabic_legal_llm",
                   "debt_collection_regulation_legal_llm_001_011.json")
N = 11
KEY_RE = r"debt_collection_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 11, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
STATUS = "SAMA_RULEBOOK_PRIMARY_AR_EN_BILINGUAL_HTML_CROSS_VERIFIED"
EXPECTED_CHAPTERS = 5
FLAGGED_DISCREPANCY_KEYS = {
    "debt_collection_regulation_chapter_five_no_numbered_article",
    "debt_collection_regulation_predecessor_naming_variance",
    "debt_collection_regulation_gregorian_date_self_inconsistency_sama_pages",
    "debt_collection_regulation_istitlaa_unreachable_this_pass",
    "debt_collection_regulation_single_ar_source_no_second_independent_crosscheck",
    "debt_collection_regulation_no_boe_lawid_regulation_level",
    "debt_collection_regulation_predecessor_not_ingested_supersession_graph_out_of_scope",
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
        numbered = [c for c in chapters if c.get("articles")]
        unnumbered = [c for c in chapters if not c.get("articles")]
        if len(numbered) != 4:
            e.append("[1c] expected exactly 4 chapters with a numbered article range, got %d"
                     % len(numbered))
        if len(unnumbered) != 1:
            e.append("[1c] expected exactly 1 chapter with no numbered article range, got %d"
                     % len(unnumbered))
        else:
            fifth = unnumbered[0]
            if fifth.get("label_ar") != "الفصل الخامس":
                e.append("[1c] the no-article chapter should be الفصل الخامس, got %r"
                         % fifth.get("label_ar"))
            if not fifth.get("no_numbered_article"):
                e.append("[1c] الفصل الخامس must be explicitly marked no_numbered_article=True")
        covered = set()
        for c in numbered:
            lo, hi = (int(x) for x in c["articles"].split("-"))
            for n in range(lo, hi + 1):
                if n in covered:
                    e.append("[1c] article %d covered by more than one الفصل range" % n)
                covered.add(n)
        expected_spans = {"1-3", "4-4", "5-6", "7-11"}
        got_spans = {c.get("articles") for c in numbered}
        if got_spans != expected_spans:
            e.append("[1c] chapter_structure article spans %r != expected %r"
                     % (got_spans, expected_spans))
        if covered != set(range(1, N + 1)):
            e.append("[1c] numbered chapters do not exactly tile articles 1..%d: got %s"
                     % (N, sorted(covered)))

    if src.get("consolidated_amended_law") is not False:
        e.append("[1d] consolidated_amended_law must be False for this track")
    if not (src.get("closing_provisions_ar") or "").strip():
        e.append("[1e] closing_provisions_ar (الفصل الخامس unnumbered text) must be non-empty")
    else:
        closing = src["closing_provisions_ar"]
        if "الإصدار الأول" not in closing:
            e.append("[1e] closing_provisions_ar must contain the predecessor-edition "
                     "supersession statement ('الإصدار الأول')")

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
            e.append("[2] %s: section_ar must be non-empty (chapter this article belongs to)" % k)
        if not a.get("article_title_ar", "").strip():
            e.append("[2] %s: article_title_ar must be non-empty (source captions every article)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2] %s: residual Eastern-Arabic-Indic digit (must be normalized)" % k)
        if "  " in a["text"]:
            e.append("[2] %s: residual double-space artifact" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)

        # single, first-and-only-confirmed edition: every article must be اصلية, no history
        if ls != "اصلية":
            e.append("[3] %s: article %d expected اصلية (no amendment confirmed this pass), "
                     "got %r" % (k, n, ls))
        if a.get("history"):
            e.append("[3] %s: article %d must have empty history (اصلية-only track)" % (k, n))

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
    if not (summary.get("closing_provisions_ar") or "").strip():
        e.append("[4b] summary missing closing_provisions_ar")

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
        print("FAIL: %d error(s) in Debt Collection Regulation track:" % len(e))
        for x in e[:25]:
            print("  - %s" % x)
        return 1
    print("PASS: Debt Collection Regulations and Procedures — 11 records "
          "(11 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; 5 فصول)")
    print("  - TIER: rulebook.sama.gov.sa primary (Arabic/English bilingual, born-digital HTML,")
    print("    entiresection node 10400)")
    print("  - IN-FORCE Circular No. 106889333 (6/9/1446H = 6/3/2025G)")
    print("  - Chapter Five (أحكام ختامية) carries no numbered article -- preserved verbatim")
    print("    in closing_provisions_ar, not fabricated as a 12th article")
    print("  - CONFIRMED distinct predecessor 'First Edition' (Circular 391000083340,")
    print("    26/7/1439H = 11/4/2018G) superseded -- not ingested here (out of scope)")
    print("  - CONFIRMED distinct from finance_companies_regulation (its own Article 96 "
          "cross-references this instrument by name, not a duplicate)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
