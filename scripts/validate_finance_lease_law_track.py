#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Finance Lease Law track (28 records, all
اصلية; hierarchical فصل structure: an introductory فصل تمهيدي plus 4 فصول,
no فرع subdivisions anywhere).

VERIFICATION TIER -- see the generator's module docstring and
sources/finance_lease/law/official_source/
finance_lease_law_official_source.json's verification_methodology_note for
the full caveat: laws.boe.gov.sa's LIVE portal was unreachable this pass,
but a Wayback Machine archive of the exact law page WAS reachable and is
treated as the primary source, cross-verified against nezams.com and
against rulebook.sama.gov.sa's official Arabic and English PDFs (the latter
also being the sole source establishing the chapter/فصل structure). This
Royal Decree has never been amended since 1433H -- all 28 articles are
اصلية."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "finance_lease", "law", "official_source",
                   "finance_lease_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "finance_lease", "law", "verified",
                       "finance_lease_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "finance_lease_arabic_legal_llm",
                   "finance_lease_law_legal_llm_001_028.json")
N = 28
KEY_RE = r"finance_lease_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 28, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
STATUS = "BOE_WAYBACK_ARCHIVE_X_SAMA_RULEBOOK_PDF_X_NEZAMS_TRIPLE_VERIFIED_LIVE_BOE_UNREACHABLE"
AMENDED_KEYS = set()  # no amended articles -- this Royal Decree has never been amended
FLAGGED_DISCREPANCY_KEYS = {
    "finance_lease_chapter_two_span_corrected_from_initial_summary_artifact",
    "finance_lease_sama_naming_footnote_not_a_textual_amendment",
    "finance_lease_no_explicit_predecessor_repeal_clause_found",
    "finance_lease_implementing_regulation_not_ingested_this_pass",
    "finance_lease_art_020_022_tatweel_confirmed_dual_source",
}
# expected chapter membership per article number, derived from
# chapter_structure -- used to cross-check each article's section_ar
# (no فرع subdivisions in this law, so the section slot is always None)
CHAPTER_RANGES = [
    (1, 1, "فصل تمهيدي", None),
    (2, 17, "الفصل الأول", None),
    (18, 23, "الفصل الثاني", None),
    (24, 26, "الفصل الثالث", None),
    (27, 28, "الفصل الرابع", None),
]
AR = "ء-ي"
# Articles 20 and 22 carry genuine in-word decorative tatweel (e.g. "مـع",
# "مـراعـاة", "المـادة", "المستأجـر", "الأصـل", "المـؤجَّـر", "أثـناء") that
# is NOT a scraping artifact: it is present byte-for-byte identically in
# BOE-via-Wayback AND in nezams.com's independently-fetched live
# transcription of the same two articles (cross-verified this pass -- see
# known_unresolved_discrepancies). This track preserves the primary source
# text verbatim rather than silently "cleaning" a genuine, dual-source-
# confirmed typesetting feature of the official text.
TATWEEL_CONFIRMED_KEYS = {"finance_lease_art_020", "finance_lease_art_022"}


def _bad_tatweel(text, allow=False):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        if (re.match("[%s]" % AR, before) and before != "ه"
                and re.match("[%s]" % AR, after)):
            bad += 1
    return 0 if allow else bad


def _expected_chapter_fragment(n):
    for lo, hi, chapter, section in CHAPTER_RANGES:
        if lo <= n <= hi:
            return chapter, section
    return None, None


def main():
    e = []
    for p in (SRC, RECORDS, LLM):
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

    # chapter_structure coverage: every article number 1..N must fall inside
    # exactly one top-level chapter range; ranges must not overlap and must
    # be contiguous. This law has no فرع sections, so we only check the
    # top-level chapters (but still validate any 'sections' list if present,
    # for forward-compatibility/defensiveness).
    chs = src.get("chapter_structure") or []
    if not chs:
        e.append("[1c] expected non-empty chapter_structure for this 5-part law")
    covered = set()
    for ch in chs:
        lo, hi = (int(x) for x in ch["articles"].split("-"))
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one top-level chapter" % n)
            covered.add(n)
        for sec in ch.get("sections", []):
            slo, shi = (int(x) for x in sec["articles"].split("-"))
            if slo < lo or shi > hi:
                e.append("[1c] section %s articles %s outside parent chapter range" %
                          (sec.get("label_ar"), sec["articles"]))
    if covered != set(range(1, N + 1)):
        missing = sorted(set(range(1, N + 1)) - covered)
        extra = sorted(covered - set(range(1, N + 1)))
        if missing:
            e.append("[1c] chapter_structure missing article(s): %s" % missing)
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra)

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
        if _bad_tatweel(a["text"], allow=(k in TATWEEL_CONFIRMED_KEYS)):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")):
            e.append("[2] %s: unexpected is_mukarrar=True (no مكرر articles enacted "
                      "in this law)" % k)
        # section_ar cross-check against the chapter_structure-derived expectation
        m = re.match(KEY_RE, k)
        n = int(m.group(1))
        exp_chapter, exp_section = _expected_chapter_fragment(n)
        sec_ar = a.get("section_ar", "")
        if exp_chapter and exp_chapter not in sec_ar:
            e.append("[2f] %s: section_ar %r missing expected chapter %r" %
                      (k, sec_ar, exp_chapter))
        if exp_section and exp_section not in sec_ar:
            e.append("[2f] %s: section_ar %r missing expected فرع %r" %
                      (k, sec_ar, exp_section))
        # residual bidi paren-before-digit / doubled-tanwin artifacts
        if re.search(r"\(\s*\)\d", a["text"]):
            e.append("[2h] %s: residual bidi paren-before-digit artifact detected" % k)
        if "ًً" in a["text"]:
            e.append("[2g] %s: residual doubled-tanwin artifact detected" % k)
        # this law has no فرع subdivisions anywhere -- section_ar must never
        # contain a فرع marker
        if "الفرع" in sec_ar:
            e.append("[2i] %s: unexpected فرع marker in section_ar (this law has "
                      "no فرع subdivisions)" % k)

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

    # spot-check: Article 1 (definitions) must retain the original 1433H
    # SAMA defined terms verbatim (un-updated for the 2020 SAMA/Saudi
    # Central Bank rename -- see known_unresolved_discrepancies)
    art1 = arts.get("finance_lease_art_001", {})
    if "مؤسسة النقد العربي السعودي" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected original SAMA defined-term text")
    # Article 27 must reference the 90-day Implementing Regulation deadline
    art27 = arts.get("finance_lease_art_027", {})
    if "تسعين" not in art27.get("text", ""):
        e.append("[2j] Article 27 missing expected 90-day Implementing Regulation deadline")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        expected_original = a.get("original_1433h_text")
        if r.get("original_text") != expected_original:
            e.append("[4] %s: original_text not propagated" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        if r["article_text_ar"] != arts[r["article_key"]]["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Finance Lease Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Finance Lease Law — 28 records (all اصلية)")
    print("  - hierarchical structure: فصل تمهيدي (definitions, Art 1) + 4 فصول")
    print("    (confirmed via rulebook.sama.gov.sa's official Arabic and English PDFs,")
    print("    article-boundary-exact; BOE's own per-article HTML view carries no inline")
    print("    فصل headings)")
    print("  - VERIFICATION TIER: BOE-via-Wayback-Machine archive (primary, live BOE")
    print("    unreachable) x nezams.com live HTML transcription x rulebook.sama.gov.sa")
    print("    official Arabic+English PDFs (agreement on all 28 articles)")
    print("  - IN-FORCE Royal Decree M/48 (13/8/1433H); NEVER amended since enactment")
    print("  - No repeal/supersession clause naming a predecessor statute found")
    print("    (documented negative finding)")
    print("  - Companion Implementing Regulation (Administrative/Governor's Decision")
    print("    1/م ش ت, 14/4/1434H, itself separately amended at least once) identified")
    print("    but NOT ingested this pass -- candidate for follow-up, not fabricated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
