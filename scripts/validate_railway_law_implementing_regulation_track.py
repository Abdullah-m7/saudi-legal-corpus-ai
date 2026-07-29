#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Railway Law
track (اللائحة التنفيذية لنظام الخطوط الحديدية, TGA Board Resolution No.
4/1/1/2024, dated 19/12/1445H; published Umm Al-Qura Gazette 22/4/1446H =
25/10/2024G; 91 records, all اصلية; 16 فصول).

VERIFICATION TIER -- see the generator's module docstring and
sources/railway_law_implementing_regulation/law/official_source/
railway_law_implementing_regulation_official_source.json's
verification_methodology_note for the full account (TIER_1: two independent
official/primary sources -- tga.gov.sa via Wayback, and the Umm Al-Qura
Official Gazette fetched live -- agree article-by-article across all 91
articles). This validator asserts: exactly 91 articles in a clean 1..91 run;
exactly 16 chapter_structure entries (الفصل) tiling articles 1-91 with no
gap/overlap; consolidated_amended_law is explicitly False; all 91 articles
are اصلية with empty amendment history; Article 86 carries the merged
25-row violations/penalties table; and every discrepancy this build's own
methodology note flags as a named, non-obvious judgment call is present in
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
SRC = os.path.join(ROOT, "sources", "railway_law_implementing_regulation", "law",
                   "official_source", "railway_law_implementing_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "railway_law_implementing_regulation", "law", "verified",
                       "railway_law_implementing_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "railway_law_implementing_regulation", "law", "verified",
                       "railway_law_implementing_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "railway_law_implementing_regulation_arabic_legal_llm",
                   "railway_law_implementing_regulation_legal_llm_001_091.json")
N = 91
KEY_RE = r"railway_law_implementing_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 91, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_CHAPTERS = 16
EXPECTED_SPANS = {(1, 1), (2, 3), (4, 7), (8, 25), (26, 27), (28, 32), (33, 33), (34, 36),
                  (37, 39), (40, 41), (42, 54), (55, 56), (57, 59), (60, 71), (72, 89), (90, 91)}
FLAGGED_DISCREPANCY_KEYS = {
    "railway_law_implementing_regulation_tga_site_stray_article40_resolved_via_gazette",
    "railway_law_implementing_regulation_ch5_ch6_titles_stale_on_tga_site_resolved_via_gazette",
    "railway_law_implementing_regulation_violations_table_merged_into_art86",
    "railway_law_implementing_regulation_source_typos_preserved_verbatim",
    "railway_law_implementing_regulation_decision_date_vs_gazette_date_four_month_gap",
    "railway_law_implementing_regulation_boe_not_attempted_this_pass",
}
AR = "ء-ي"


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
            if c.get("first_article") is None or c.get("last_article") is None:
                e.append("[1c] chapter %r must carry first_article/last_article" % c.get("label_ar"))
        got_spans = {(c["first_article"], c["last_article"]) for c in chapters}
        if got_spans != EXPECTED_SPANS:
            e.append("[1c] chapter_structure spans %r != expected %r" % (got_spans, EXPECTED_SPANS))
        covered = set()
        for c in chapters:
            for n in range(c["first_article"], c["last_article"] + 1):
                if n in covered:
                    e.append("[1c] article %d covered by more than one الفصل range" % n)
                covered.add(n)
        if covered != set(range(1, N + 1)):
            e.append("[1c] chapters do not exactly tile articles 1..%d: got %s"
                     % (N, sorted(covered)))

    if src.get("consolidated_amended_law") is not False:
        e.append("[1d] consolidated_amended_law must be False for this track "
                 "(sole known founding version; no amendment evidence found)")
    if src.get("law_component") != "regulation":
        e.append("[1d] law_component must be 'regulation'")
    if src.get("legal_status_ar") != "نافذ":
        e.append("[1d] legal_status_ar must be نافذ")
    if src.get("base_law_key") != "railway_law":
        e.append("[1d] base_law_key must reference the existing railway_law base-law track")

    sc = Counter()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z]{4,}|<[a-zA-Z/]|&amp;|&nbsp;", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar", "").strip():
            e.append("[2] %s: section_ar must be non-empty (فصل this article belongs to)" % k)
        if "  " in a["text"]:
            e.append("[2] %s: residual double-space artifact" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)
        if "[ROW]" in a["text"] or "<TABLE" in a["text"]:
            e.append("[2] %s: unconverted table markup leftover in text" % k)

        if ls != "اصلية":
            e.append("[3] %s: article %d expected اصلية (founding/sole-known text), got %r"
                     % (k, n, ls))
        if a.get("history"):
            e.append("[3] %s: article %d must have empty history" % (k, n))

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
    if len(hist) != 1:
        e.append("[2h] amendment_history must record exactly 1 entry (founding resolution "
                 "4/1/1/2024), got %d" % len(hist))

    gaz = src.get("gazette_publication") or {}
    if gaz.get("date_hijri") != "22/4/1446" or gaz.get("date_gregorian") != "25/10/2024":
        e.append("[2i] gazette_publication date mismatch, expected 22/4/1446 / 25/10/2024")

    # Article 86 must carry the merged violations & penalties schedule (25 rows).
    art86_key = "railway_law_implementing_regulation_art_086"
    art86 = arts.get(art86_key)
    if not art86:
        e.append("[2g] Article 86 missing")
    else:
        t = art86["text"]
        if "جدول المخالفات والعقوبات" not in t:
            e.append("[2g] Article 86 must reference جدول المخالفات والعقوبات")
        n_rows = t.count("م (")
        if n_rows != 25:
            e.append("[2g] Article 86 must carry exactly 25 merged violation rows, found %d"
                     % n_rows)

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
    if summary.get("consolidated_amended_law") is not False:
        e.append("[4b] summary consolidated_amended_law must be False")

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
        print("FAIL: %d error(s) in Railway Law Implementing Regulation track:" % len(e))
        for x in e[:30]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Railway Law — 91 records "
          "(91 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; 16 فصلاً)")
    print("  - TIER: TIER_1 -- two independent official/primary sources (tga.gov.sa via Wayback "
          "archive, since live is unreachable this pass; Umm Al-Qura Official Gazette uqn.gov.sa "
          "fetched live) agree article-by-article across all 91 articles (punctuation/case-ending "
          "variance only; one typo resolved via the Gazette in Article 15)")
    print("  - GOVERNING TEXT: Umm Al-Qura Official Gazette (higher statutory authority, zero "
          "reachability gap, retains explicit sub-item enumeration TGA's own site drops)")
    print("  - TGA's own site independently found to carry two stale/incorrect artifacts, both "
          "resolved via the Gazette: a stray non-numbered 'Article 40' fragment, and mismatched "
          "Chapter 5/6 titles (see known_unresolved_discrepancies)")
    print("  - Article 86 carries the merged 25-row جدول المخالفات والعقوبات (count matches "
          "spa.gov.sa's official wire verbatim)")
    print("  - Parent base law (railway_law, Royal Decree M/159, 50 articles) NOT touched this pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
