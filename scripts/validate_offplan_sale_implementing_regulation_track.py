#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Off-Plan Sale
and Lease of Real Estate Projects Law track ("WAFI") -- اللائحة التنفيذية
لنظام بيع وتأجير مشروعات عقارية على الخارطة, REGA Board of Directors
Resolution No. (ق/م/إ/هـ/8/2024/ت), dated 20/10/1445H (29/4/2024G); 49
records, all اصلية; 5 sections -- one implicit/unlabeled (articles 1-7) plus
four unlabeled-but-explicit plain-text divider lines found verbatim in the
primary source (not officially numbered "الفصل"/"الباب").

VERIFICATION TIER -- see the generator's module docstring and
sources/offplan_sale_implementing_regulation/law/official_source/
offplan_sale_implementing_regulation_official_source.json's
verification_methodology_note for the full account. This validator asserts:
exactly 49 articles in a clean 1..49 run; exactly 5 chapter_structure entries
tiling articles 1-49 with no gap/overlap (the first carrying an empty
title_ar, matching the primary source's own lack of a first-section title);
every article carries source_tier "primary" and the single expected status
string (this track has no per-article tier variation, unlike some other
regulation tracks in this corpus, because the primary Gazette page reached
all 49 articles with zero reachability gap); all 49 articles are اصلية with
empty amendment history (single, first-and-only-confirmed edition); no
ملغاة/معدلة/مضافة articles this pass; and that every discrepancy this
build's own methodology note flags as a named, non-obvious judgment call is
present in known_unresolved_discrepancies.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "offplan_sale_implementing_regulation", "law",
                    "official_source",
                    "offplan_sale_implementing_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "offplan_sale_implementing_regulation", "law", "verified",
                        "offplan_sale_implementing_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "offplan_sale_implementing_regulation", "law", "verified",
                        "offplan_sale_implementing_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "offplan_sale_implementing_regulation_arabic_legal_llm",
                    "offplan_sale_implementing_regulation_legal_llm_001_049.json")
N = 49
KEY_RE = r"offplan_sale_implementing_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 49, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_STATUS = "UQN_GAZETTE_OFFICIAL_PRIMARY_TEXT_AR_STRUCTURAL_XVERIFIED_REGA_PDF"
EXPECTED_CHAPTERS = 5
EXPECTED_SPANS = {"1-7", "8-33", "34-39", "40-46", "47-49"}
FLAGGED_DISCREPANCY_KEYS = {
    "offplan_sale_implementing_regulation_rega_pdf_font_cmap_corrupted",
    "offplan_sale_implementing_regulation_no_section1_title_in_source",
    "offplan_sale_implementing_regulation_no_decree_preamble_in_source",
    "offplan_sale_implementing_regulation_qanoonsa_stub_page_only",
    "offplan_sale_implementing_regulation_nezams_no_dedicated_page",
    "offplan_sale_implementing_regulation_argaam_draft_stage_structural_only",
    "offplan_sale_implementing_regulation_boe_unreachable",
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
        e.append("[1c] expected %d section entries in chapter_structure, got %r"
                 % (EXPECTED_CHAPTERS, chapters))
    else:
        got_spans = {c.get("articles") for c in chapters}
        if got_spans != EXPECTED_SPANS:
            e.append("[1c] chapter_structure article spans %r != expected %r"
                     % (got_spans, EXPECTED_SPANS))
        covered = set()
        for c in chapters:
            lo, hi = (int(x) for x in c["articles"].split("-"))
            for n in range(lo, hi + 1):
                if n in covered:
                    e.append("[1c] article %d covered by more than one section range" % n)
                covered.add(n)
        if covered != set(range(1, N + 1)):
            e.append("[1c] sections do not exactly tile articles 1..%d: got %s"
                     % (N, sorted(covered)))
        # exactly one section may carry an empty title (the unlabeled first
        # section, articles 1-7) -- all four others must carry a non-empty
        # title_ar taken verbatim from the primary source's own plain-text
        # divider lines.
        empty_titles = [c for c in chapters if not (c.get("title_ar") or "").strip()]
        if len(empty_titles) != 1 or empty_titles[0].get("articles") != "1-7":
            e.append("[1c] expected exactly one untitled section (articles 1-7), got %r"
                     % empty_titles)

    if src.get("consolidated_amended_law") is not False:
        e.append("[1d] consolidated_amended_law must be False for this track")
    if src.get("law_component") != "regulation":
        e.append("[1d] law_component must be 'regulation'")
    if src.get("legal_status_ar") != "نافذ":
        e.append("[1d] legal_status_ar must be نافذ")
    if src.get("parent_law_track_id") != "offplan_sale_law":
        e.append("[1d] parent_law_track_id must be 'offplan_sale_law'")

    tier_counts = Counter()
    sc = Counter()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
        tier = a.get("source_tier")
        if tier != "primary":
            e.append("[2] %s: article %d expected source_tier 'primary', got %r"
                     % (k, n, tier))
        else:
            tier_counts[tier] += 1
        if a.get("status") != EXPECTED_STATUS:
            e.append("[2] %s: expected status %r, got %r"
                     % (k, EXPECTED_STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        # section_ar may legitimately be empty ONLY for articles 1-7 (the
        # primary source's own unlabeled first section) -- see
        # known_unresolved_discrepancies.
        if not a.get("section_ar", "").strip() and not (1 <= n <= 7):
            e.append("[2] %s: section_ar unexpectedly empty for article %d "
                     "(only articles 1-7 may be untitled)" % (k, n))
        if a.get("section_ar", "").strip() and (1 <= n <= 7):
            e.append("[2] %s: article %d expected empty section_ar (unlabeled "
                     "first section), got %r" % (k, n, a.get("section_ar")))
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2] %s: residual Eastern-Arabic-Indic digit (must be normalized)" % k)
        if "  " in a["text"]:
            e.append("[2] %s: residual double-space artifact" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)
        if "<TABLE_" in a["text"] or "<CELL>" in a["text"] or "<ROW>" in a["text"] \
                or "@@TABLE" in a["text"]:
            e.append("[2] %s: unconverted table markup leftover in text" % k)

        if ls != "اصلية":
            e.append("[3] %s: article %d expected اصلية (no amendment confirmed this pass), "
                     "got %r" % (k, n, ls))
        if a.get("history"):
            e.append("[3] %s: article %d must have empty history (اصلية-only track)" % (k, n))

    if tier_counts.get("primary", 0) != N:
        e.append("[2g] expected %d primary-tier articles, got %d" % (N, tier_counts.get("primary", 0)))
    declared_tiers = src.get("source_tier_counts") or {}
    if declared_tiers.get("primary") != tier_counts.get("primary", 0):
        e.append("[2g] declared source_tier_counts.primary does not match actual per-article count")
    if declared_tiers.get("secondary_only", 0) != 0:
        e.append("[2g] declared source_tier_counts.secondary_only must be 0 for this track")

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))
    declared = src.get("status_counts") or {}
    for st in ALLOWED_STATUS:
        if declared.get(st, 0) != sc.get(st, 0):
            e.append("[2f] declared status_counts[%s] does not match actual per-article counts" % st)

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the tier")
    if not (src.get("preamble_ar") or "").strip():
        e.append("[2d] missing preamble_ar")
    if src.get("decree_preamble_ar") != "":
        e.append("[2d] decree_preamble_ar expected empty string (documented as absent "
                 "from the primary source, see known_unresolved_discrepancies), got %r"
                 % src.get("decree_preamble_ar"))
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

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
        if r.get("source_tier") != a.get("source_tier"):
            e.append("[4] %s: source_tier mismatch" % r["article_key"])
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
    if summary.get("source_tier_counts") != src.get("source_tier_counts"):
        e.append("[4b] summary source_tier_counts mismatch with source")
    if summary.get("parent_law_track_id") != "offplan_sale_law":
        e.append("[4b] summary parent_law_track_id must be 'offplan_sale_law'")

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
        if r.get("source_trust", {}).get("source_tier") != a.get("source_tier"):
            e.append("[5] %s: llm record source_trust.source_tier mismatch" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Offplan Sale Implementing Regulation track:" % len(e))
        for x in e[:30]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Off-Plan Sale and Lease of Real Estate "
          "Projects Law (\"WAFI\") — 49 records (49 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; "
          "5 sections)")
    print("  - TIER: TIER_2 -- one official primary source reached with zero "
          "reachability gap (uqn.gov.sa, Umm Al-Qura Official Gazette), all 49 "
          "articles including 4 embedded tables converted row-by-row; structurally "
          "(not verbatim) cross-checked against REGA's own PDF (title/decree-date/"
          "article-count match exactly; that PDF's own text layer is font-cmap "
          "corrupted, see known_unresolved_discrepancies)")
    print("  - IN-FORCE REGA Board Resolution No. (ق/م/إ/هـ/8/2024/ت) (20/10/1445H = "
          "29/4/2024G), published Umm Al-Qura 2 Dhul-Qi'dah 1445H (10/5/2024G) -- "
          "Implementing Regulation of parent track offplan_sale_law (Royal Decree M/44)")
    print("  - No repeal of any named predecessor instrument found in this text "
          "(Article 49 is a bare publication clause); see final report for detail")
    return 0


if __name__ == "__main__":
    sys.exit(main())
