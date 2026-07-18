#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Law of Practicing Healthcare Professions track
(44 records, all اصلية; hierarchical فصل/فرع structure: 5 chapters, with
chapters 2 and 3 each subdivided into 3 فرع sections).

VERIFICATION TIER -- see the generator's module docstring and
sources/healthcare_professions/law/official_source/
healthcare_professions_law_official_source.json's verification_methodology_note
for the full caveat: laws.boe.gov.sa's LIVE portal was unreachable this pass,
but a Wayback Machine archive of the exact law page WAS reachable and is
treated as the primary source, cross-verified against nezams.com. This Royal
Decree has never been amended since 1426H -- all 44 articles are اصلية. A
Shura-Council-approved but NOT-yet-enacted proposed Article 4 bis is
documented in known_unresolved_discrepancies rather than fabricated or
silently added as a record."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "healthcare_professions", "law", "official_source",
                   "healthcare_professions_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "healthcare_professions", "law", "verified",
                       "healthcare_professions_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "healthcare_professions_arabic_legal_llm",
                   "healthcare_professions_law_legal_llm_001_044.json")
N = 44
KEY_RE = r"healthcare_professions_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 44, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
STATUS = "BOE_WAYBACK_ARCHIVE_X_NEZAMS_CROSS_VERIFIED_LIVE_BOE_UNREACHABLE"
AMENDED_KEYS = set()  # no amended articles -- this Royal Decree has never been amended
FLAGGED_DISCREPANCY_KEYS = {
    "healthcare_professions_art_036_nezams_transcription_typo",
    "healthcare_professions_art_044_nezams_scrape_boundary_artifact",
    "healthcare_professions_pending_shura_approved_article_4_bis_not_enacted",
    "healthcare_professions_implementing_regulation_not_ingested_this_pass",
}
# expected chapter membership per article number, derived from
# chapter_structure -- used to cross-check each article's section_ar
CHAPTER_RANGES = [
    (1, 4, "الفصل الأول", None),
    (5, 14, "الفصل الثاني", "الفرع الأول"),
    (15, 23, "الفصل الثاني", "الفرع الثاني"),
    (24, 25, "الفصل الثاني", "الفرع الثالث"),
    (26, 27, "الفصل الثالث", "الفرع الأول"),
    (28, 30, "الفصل الثالث", "الفرع الثاني"),
    (31, 32, "الفصل الثالث", "الفرع الثالث"),
    (33, 41, "الفصل الرابع", None),
    (42, 44, "الفصل الخامس", None),
]
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
    # exactly one top-level chapter range, and (for chapters 2/3) exactly one
    # section range within it; ranges must not overlap and must be contiguous
    chs = src.get("chapter_structure") or []
    if not chs:
        e.append("[1c] expected non-empty chapter_structure for this 5-chapter law")
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
        if _bad_tatweel(a["text"]):
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
        # known nezams.com-side artifacts must NOT have leaked into this track's text
        if k == "healthcare_professions_art_036" and "الشريعية" in a["text"]:
            e.append("[2i] %s: un-normalized nezams.com transcription typo present" % k)
        if k == "healthcare_professions_art_044":
            for bad_frag in ("عرض كل المواد", "عن الموقع", "اتصل بنا"):
                if bad_frag in a["text"]:
                    e.append("[2i] %s: nezams.com site-navigation scrape artifact present" % k)

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

    # supersession check: Article 42 must cite both repealed predecessor laws
    art42 = arts.get("healthcare_professions_art_042", {})
    for cite in ("م/3", "1409", "م/18", "1398"):
        if cite not in art42.get("text", ""):
            e.append("[2j] Article 42 missing expected repeal citation %r" % cite)

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        expected_original = (a.get("original_1409h_text") or a.get("original_1426h_text"))
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
        print("FAIL: %d error(s) in Healthcare Professions Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Law of Practicing Healthcare Professions — 44 records (all اصلية)")
    print("  - hierarchical structure: 5 فصول, with فصل 2 and 3 each subdivided into 3 فرع")
    print("    sections (confirmed via BOE's own summary + moh.gov.sa consolidated Arabic")
    print("    and English PDFs, article-boundary-exact across all three)")
    print("  - VERIFICATION TIER: BOE-via-Wayback-Machine archive (primary, live BOE")
    print("    unreachable) x nezams.com live HTML transcription (agreement on 42/44")
    print("    articles with zero differences; 2 trivial nezams.com-side artifacts")
    print("    documented, neither adopted)")
    print("  - IN-FORCE Royal Decree M/59 (4/11/1426H); NEVER amended since enactment")
    print("  - Article 42 confirms repeal of Royal Decree M/3 (21/2/1409H, physicians/")
    print("    dentists) and M/18 (18/3/1398H, pharmacy)")
    print("  - Pending (Shura Council, Dec 2023) but NOT-yet-enacted proposed Article 4 bis,")
    print("    and companion Implementing Regulation (Ministerial Resolution 4080489,")
    print("    2/1/1439H), both identified but NOT ingested this pass -- candidates for")
    print("    follow-up, not fabricated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
