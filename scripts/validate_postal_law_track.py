#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Postal Law track.

*** THIS IS A DELIBERATE, DISCLOSED PARTIAL-COVERAGE TRACK (20 of a
reported 37 articles). *** This validator enforces that the partial-
coverage disclosure stays intact (coverage_status fields present and
consistent everywhere; the required known_unresolved_discrepancies keys
documenting what's missing and why are all present) in addition to the
usual internal self-consistency checks (text matches between source/
verified/LLM layers, hashes, status-count bookkeeping, chapter-range
bookkeeping for the five فصول actually covered). It does not attempt to
re-adjudicate anything about the un-ingested Articles 21-37 -- see the
generator's module docstring and postal_law_official_source.json's
verification_methodology_note for the full account of what was attempted
and why those articles are not present.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "postal_law", "law", "official_source",
                   "postal_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "postal_law", "law", "verified",
                       "postal_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "postal_law", "law", "verified",
                       "postal_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "postal_law_arabic_legal_llm",
                   "postal_law_legal_llm_001_020.json")
N = 20
OFFICIAL_TOTAL = 37
KEY_RE = r"postal_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 20, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 5  # فصول 1-4 in full, فصل 5 partial (art. 20 only)

STATUS_PARTIAL = ("NEZAMS_SSR_HTML_LIVE_FETCH_X_LEXISMIDDLEEAST_STRUCTURAL_CROSSCHECK_"
                   "ARTS_1_20_ONLY_BOE_LIVE_AND_WAYBACK_UNREACHABLE")
AMENDED_KEYS = set()
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
FLAGGED_DISCREPANCY_KEYS = {
    "postal_articles_21_37_not_ingested",
    "postal_nezams_corruption_articles_21_38",
    "postal_art_count_37_vs_38",
    "postal_repeal_clause_article_number_unconfirmed",
    "postal_com705_transfer_not_primary_fetched",
    "postal_article1_terminology_vintage_unconfirmed",
    "postal_chapter5_partial_coverage",
    "postal_predecessor_law_page_not_directly_fetched",
}
EXPECTED_CHAPTER_RANGES = {
    "الفصل الأول": (1, 3),
    "الفصل الثاني": (4, 10),
    "الفصل الثالث": (11, 11),
    "الفصل الرابع": (12, 19),
    "الفصل الخامس": (20, 20),  # partial -- true range is 20-22, only 20 ingested
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


def _iter_chapter_ranges(chs):
    for ch in chs:
        secs = ch.get("sections")
        if not secs:
            lo, hi = (int(x) for x in ch["articles"].split("-"))
            yield (lo, hi)
            continue
        for sec in secs:
            slo, shi = (int(x) for x in sec["articles"].split("-"))
            yield (slo, shi)


def main():
    e = []
    for p in (SRC, RECORDS, SUMMARY, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    # --- partial-coverage disclosure checks (specific to this track) ---
    if src.get("coverage_status") != "PARTIAL_VERIFIED_SUBSET":
        e.append("[0] source coverage_status must be PARTIAL_VERIFIED_SUBSET")
    if not src.get("coverage_status_note"):
        e.append("[0] source missing coverage_status_note explaining the partial build")
    if src.get("official_reported_article_count") != OFFICIAL_TOTAL:
        e.append("[0] official_reported_article_count must be %d" % OFFICIAL_TOTAL)

    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    if src.get("article_count") != N:
        e.append("[1] article_count field != %d (this must reflect INGESTED count, "
                  "not the law's true total of %d)" % (N, OFFICIAL_TOTAL))
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapter_structure entries (فصول 1-4 full + فصل 5 "
                  "partial), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))
    for ch in chs:
        label = ch.get("label_ar")
        want = EXPECTED_CHAPTER_RANGES.get(label)
        if want is None:
            e.append("[1c] unexpected chapter label_ar %r" % label)
            continue
        lo, hi = (int(x) for x in ch["articles"].split("-"))
        if (lo, hi) != want:
            e.append("[1c] %s: expected ingested range %s, got %s" % (label, want, (lo, hi)))

    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one leaf range" % n)
            covered.add(n)
    if covered != set(range(1, N + 1)):
        missing = sorted(set(range(1, N + 1)) - covered)
        extra = sorted(covered - set(range(1, N + 1)))
        if missing:
            e.append("[1c] chapter_structure missing ingested article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != STATUS_PARTIAL:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS_PARTIAL, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "ًً" in a["text"]:
            e.append("[2g] %s: residual doubled-tanwin artifact detected" % k)
        if re.search(r"\(\s*\)\d", a["text"]):
            e.append("[2h] %s: residual bidi paren-before-digit artifact detected" % k)
        # this law's articles carry no inline فصل/heading leftovers -- the
        # generator/source-builder strips those into chapter_structure
        if a["text"].startswith("الفصل") or "المادة " + a["number_label_ar"].split()[-1] == a["text"][:20]:
            pass  # heuristic only, not a hard failure

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct tier")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    if not src.get("amendment_history"):
        e.append("[2k] missing amendment_history (must record M/22 and CoM 705)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        if "م/22" not in decrees:
            e.append("[2k] amendment_history must reference م/22")
        if "705" not in decrees:
            e.append("[2k] amendment_history must reference CoM Resolution 705 "
                      "(the regulatory-transfer finding)")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("postal_art_001", {})
    if "نظام البريد" not in art1.get("text", "") or "الاتصالات وتقنية المعلومات" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (النظام / الهيئة terminology)")
    art2 = arts.get("postal_art_002", {})
    if "يهدف النظام" not in art2.get("text", ""):
        e.append("[2j] Article 2 missing expected objectives clause")
    art4 = arts.get("postal_art_004", {})
    if "الهيئة العامة للنقل" not in art4.get("text", ""):
        e.append("[2j] Article 4 missing expected parcels/TGA licensing cross-reference")
    art11 = arts.get("postal_art_011", {})
    if "استحواذ" not in art11.get("text", "") and "اندماج" not in art11.get("text", ""):
        e.append("[2j] Article 11 missing expected competition/merger clause")
    art20 = arts.get("postal_art_020", {})
    if "التخليص" not in art20.get("text", ""):
        e.append("[2j] Article 20 missing expected clearance-methods clause")
    if src.get("decree") != "المرسوم الملكي رقم (م/22)" or src.get("decree_date_hijri") != "08/03/1443":
        e.append("[2j] decree/decree_date_hijri mismatch with verified M/22, 08/03/1443H")
    if "م/4" not in src.get("preamble_ar", "") or "1406" not in src.get("preamble_ar", ""):
        e.append("[2j] preamble_ar missing expected predecessor-law recital (M/4, 1406H)")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: article_key not found in source" % r["article_key"]); continue
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("coverage_status") != "PARTIAL_VERIFIED_SUBSET":
            e.append("[4] %s: verified record missing coverage_status disclosure" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if summary.get("coverage_status") != "PARTIAL_VERIFIED_SUBSET":
        e.append("[4b] summary missing coverage_status disclosure")
    if summary.get("official_reported_article_count") != OFFICIAL_TOTAL:
        e.append("[4b] summary official_reported_article_count != %d" % OFFICIAL_TOTAL)

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    if llm.get("coverage_status") != "PARTIAL_VERIFIED_SUBSET":
        e.append("[5] llm layer missing coverage_status disclosure")
    if llm.get("official_reported_article_count") != OFFICIAL_TOTAL:
        e.append("[5] llm layer official_reported_article_count != %d" % OFFICIAL_TOTAL)
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: article_key not found in source" % r["article_key"]); continue
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS_PARTIAL.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])
        if r.get("source_trust", {}).get("coverage_status") != "PARTIAL_VERIFIED_SUBSET":
            e.append("[5] %s: llm record source_trust missing coverage_status" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Postal Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Postal Law (نظام البريد) -- DISCLOSED PARTIAL COVERAGE")
    print("  - 20 records ingested, ALL اصلية, of a reported 37-article total")
    print("  - Articles 21-37 NOT ingested this pass -- see "
          "known_unresolved_discrepancies")
    print("  - فصول covered: الأول (1-3), الثاني (4-10), الثالث (11), الرابع (12-19),")
    print("    الخامس (20 only, of true range 20-22)")
    print("  - VERIFICATION TIER: nezams.com live server-rendered HTML fetch, "
          "cross-checked")
    print("    structurally against lexismiddleeast.com through Article 20; "
          "laws.boe.gov.sa")
    print("    (live and Wayback), tga.gov.sa, mot.gov.sa, uqn.gov.sa gazette, "
          "qanoonsa.com,")
    print("    qanoniah.com, and site.eastlaws.com were all unreachable/unusable "
          "this pass")
    print("  - Royal Decree M/22 (08/03/1443H), CoM Resolution 149 (06/03/1443H); "
          "replaces")
    print("    نظام البريد 1406هـ (Royal Decree M/4, 21/2/1406H) -- repeal fact "
          "confirmed via")
    print("    recitals + secondary sources, exact repealing article number "
          "NOT confirmed")
    print("  - REGULATORY TRANSFER: CoM Resolution 705 (27/12/1443H) reported to move "
          "postal-")
    print("    sector oversight from CITC/Ministry of Communications & IT to the "
          "General")
    print("    Authority for Transport / Ministry of Transport and Logistics "
          "Services, via")
    print("    terminology substitution -- an administrative reassignment, NOT a "
          "confirmed")
    print("    textual amendment of specific articles; corroborated circumstantially, "
          "not")
    print("    via CoM 705's own primary text (unreachable this pass)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
