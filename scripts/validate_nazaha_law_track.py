#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Law (Statute) of the Control and
Anti-Corruption Authority track (24 records, all اصلية, 0 معدلة, 0 ملغاة,
0 مضافة; four أبواب: تعريفات 1-2, جهاز الهيئة ومهماته واختصاصاته 3-17,
أحكام متصلة بمكافحة جرائم الفساد 18-22, أحكام ختامية 23-24).

VERIFICATION TIER -- see the generator's module docstring and
sources/nazaha/law/official_source/nazaha_law_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa's LIVE
portal was unreachable this pass, but TWO Wayback Machine snapshots of the
exact BOE law page (~15.5 months apart) plus a third independent
FAOLEX-hosted PDF mirror of the same BOE page all show byte/word-identical,
wholly unamended text -- a stronger tier than this corpus's typical
single-snapshot fallback. This validator does not attempt to re-adjudicate
any of this; it only checks internal self-consistency of the text this
track actually ingests, and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "nazaha", "law", "official_source",
                   "nazaha_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "nazaha", "law", "verified",
                       "nazaha_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "nazaha", "law", "verified",
                       "nazaha_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "nazaha_arabic_legal_llm",
                   "nazaha_law_legal_llm_001_024.json")
N = 24
KEY_RE = r"nazaha_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 24, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 4  # four أبواب, each a flat leaf range

STATUS_UNAMENDED = ("BOE_WAYBACK_ARCHIVE_TRIPLE_TIMEPOINT_NOV2024_JUN2025FAOLEXMIRROR_FEB2026_"
                     "BYTE_IDENTICAL_X_NEZAMS_PARTIAL_CROSSCHECK_X_QANOONSA_STRUCTURAL_CROSSCHECK_"
                     "LIVE_BOE_UNREACHABLE")
EXPECTED_STATUS_BY_KEY = {}  # every article shares STATUS_UNAMENDED (all اصلية)
AMENDED_KEYS = set()
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
FLAGGED_DISCREPANCY_KEYS = {
    "nazaha_anti_bribery_crossref_articles_17_21_stale",
    "nazaha_predecessor_founding_order_a65_secondary_only",
    "nazaha_predecessor_merger_order_a277_secondary_plus_boe_recital",
    "nazaha_predecessor_boe_status_lag",
    "nazaha_gap_map_estimate_corrected",
    "nazaha_no_inline_article_titles",
    "nazaha_implementing_regulations_not_confirmed_issued",
    "nazaha_anti_bribery_law_distinction_not_conflated",
}
EXPECTED_CHAPTER_RANGES = {
    "الباب الأول": (1, 2),
    "الباب الثاني": (3, 17),
    "الباب الثالث": (18, 22),
    "الباب الرابع": (23, 24),
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
    """Yield (lo, hi) for every leaf range in chapter_structure. This Law
    has a flat one-level أبواب structure -- no nested فصول -- so every
    top-level entry IS a leaf."""
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

    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    if src.get("article_count") != N:
        e.append("[1] article_count field != %d" % N)
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d top-level chapter_structure entries (four أبواب), "
                  "got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))
    for ch in chs:
        label = ch.get("label_ar")
        want = EXPECTED_CHAPTER_RANGES.get(label)
        if want is None:
            e.append("[1c] unexpected chapter label_ar %r" % label)
            continue
        lo, hi = (int(x) for x in ch["articles"].split("-"))
        if (lo, hi) != want:
            e.append("[1c] %s: expected range %s, got %s" % (label, want, (lo, hi)))

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
            e.append("[1c] chapter_structure missing article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])

    sc = Counter()
    for k, a in arts.items():
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNAMENDED)
        if a.get("status") != expected_status:
            e.append("[2] %s: expected status %r, got %r" % (k, expected_status, a.get("status")))
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
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present (BOE source supplies no "
                      "inline per-article titles for this law -- see "
                      "known_unresolved_discrepancies)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "ًً" in a["text"]:
            e.append("[2g] %s: residual doubled-tanwin artifact detected" % k)
        if re.search(r"\(\s*\)\d", a["text"]):
            e.append("[2h] %s: residual bidi paren-before-digit artifact detected" % k)

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
        e.append("[2k] missing amendment_history (must record M/25)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        if "م/25" not in decrees:
            e.append("[2k] amendment_history must reference م/25")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("nazaha_art_001", {})
    if "هيئة الرقابة ومكافحة الفساد" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected الهيئة definition")
    art2 = arts.get("nazaha_art_002", {})
    if "جرائم الرشوة" not in art2.get("text", ""):
        e.append("[2j] Article 2 missing expected corruption-crimes enumeration")
    art18 = arts.get("nazaha_art_018", {})
    if "فصله من وظيفته" not in art18.get("text", ""):
        e.append("[2j] Article 18 missing expected mandatory-dismissal clause")
    art19 = arts.get("nazaha_art_019", {})
    if "عبء الإثبات" not in art19.get("text", ""):
        e.append("[2j] Article 19 missing expected reversed-burden-of-proof clause")
    art23 = arts.get("nazaha_art_023", {})
    if "يُلغي هذا النظام" not in art23.get("text", ""):
        e.append("[2j] Article 23 missing expected general-repeal clause")
    art24 = arts.get("nazaha_art_024", {})
    if "تسعين" not in art24.get("text", ""):
        e.append("[2j] Article 24 missing expected 90-day enforcement clause")
    if src.get("decree") != "المرسوم الملكي رقم (م/25)" or src.get("decree_date_hijri") != "23/1/1446":
        e.append("[2j] decree/decree_date_hijri mismatch with verified M/25, 23/1/1446H")

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
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
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
        expected_status = EXPECTED_STATUS_BY_KEY.get(r["article_key"], STATUS_UNAMENDED)
        if r.get("source_trust", {}).get("source_status") != expected_status.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Nazaha Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Law (Statute) of the Control and Anti-Corruption Authority (Nazaha)")
    print("  - 24 records, ALL اصلية (0 معدلة, 0 ملغاة, 0 مضافة)")
    print("  - four أبواب: تعريفات (1-2), جهاز الهيئة ومهماته واختصاصاته (3-17),")
    print("    أحكام متصلة بمكافحة جرائم الفساد (18-22), أحكام ختامية (23-24)")
    print("  - no inline per-article titles in the BOE source (no title_ar key used)")
    print("  - VERIFICATION TIER: BOE-via-Wayback-Machine, TWO snapshots ~15.5 months")
    print("    apart (1 Nov 2024, 15 Feb 2026), byte-identical text, PLUS a third")
    print("    independent time-point (FAOLEX PDF mirror of the same BOE page, dated")
    print("    16 Jun 2025) x nezams.com (partial, Arts. 1-14) x qanoonsa.com")
    print("    (structural, all 24 articles)")
    print("  - Royal Decree M/25 (23/1/1446H / 29 Jul 2024G), Council of Ministers")
    print("    Resolution 68 (17/1/1446H); replaces تنظيم الهيئة الوطنية لمكافحة الفساد")
    print("    (CoM Resolution 165, 28/5/1432H); predecessor bodies founded/merged via")
    print("    Royal Orders أ/65 (13/4/1432H) and أ/277 (15/4/1441H) -- background only,")
    print("    not ingested")
    print("  - CRITICAL CROSS-TRACK FINDING carried forward: this law's own enacting")
    print("    decree amends the already-ingested anti_bribery_law track's wording in")
    print("    Articles 17/21, which that track's own text has not yet incorporated --")
    print("    flagged for a dedicated follow-up pass, not resolved here")
    print("  - Three companion instruments (Art. 6 لائحة; Art. 9(1) اللائحة الإدارية")
    print("    and اللائحة المالية) referenced but not confirmed issued -- not ingested")
    return 0


if __name__ == "__main__":
    sys.exit(main())
