#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Saudi Competition
Law track.

CAPTURED SCOPE = Articles 1-5 (Chapters 1 "التعريفات والأهداف" arts 1-2, and 2
"الاختصاص ونطاق التطبيق" arts 3-5). The FULL Regulation has 90 articles across 11
chapters (recorded in the source artifact's full_regulation_chapter_structure);
Articles 6-90 are intentionally NOT ingested this pass -- see the disclosed
reason in known_unresolved_discrepancies (key competition_regulation_partial_
scope_arts_6_90_pending). This validator checks internal self-consistency of the
5 captured articles and that every discrepancy is recorded; it does NOT re-
adjudicate provenance.

VERIFICATION TIER -- see the generator docstring and the source artifact's
verification_methodology_note: laws.boe.gov.sa checked FIRST (unreachable this
pass; no dedicated lawId page for this Board-level regulation); gac.gov.sa
(issuer) unreachable; PRIMARY TEXT from qanoniah.com's clean-Unicode API,
independently corroborated for Articles 1-5 by WIPO Lex's official Arabic PDF
(sa071ar.pdf), whose numerals are unusable due to a disclosed lossy digit-CMap
defect (the reason the remaining 85 articles are pending).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "competition", "regulation", "official_source",
                   "competition_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "competition", "regulation", "verified",
                       "competition_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "competition", "regulation", "verified",
                       "competition_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "competition_regulation_arabic_legal_llm",
                   "competition_regulation_legal_llm_001_005.json")
N = 5
FULL_N = 90
KEY_RE = r"competition_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 5, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 2
EXPECTED_FULL_CHAPTERS = 11

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY: dict = {}
for k in AMENDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_AMENDED
for k in ADDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_ADDED
FLAGGED_DISCREPANCY_KEYS = {
    "competition_regulation_partial_scope_arts_6_90_pending",
    "competition_regulation_wipo_arabic_pdf_lossy_digit_cmap",
    "competition_regulation_boe_no_dedicated_lawid_page",
    "competition_regulation_gac_primary_issuer_unreachable",
    "competition_regulation_article12_amended_2023_out_of_captured_scope",
    "competition_regulation_supersedes_2014_predecessor",
    "competition_regulation_source_spelling_qararatiha",
    "competition_regulation_diacritics_zwnj_normalization",
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
        lo, hi = (int(x) for x in ch["articles"].split("-"))
        yield (lo, hi)


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

    # captured chapter_structure must cover exactly articles 1..N
    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d captured chapters, got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))
    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one chapter range" % n)
            covered.add(n)
    if covered != set(range(1, N + 1)):
        missing = sorted(set(range(1, N + 1)) - covered)
        extra = sorted(covered - set(range(1, N + 1)))
        if missing:
            e.append("[1c] captured chapter_structure missing article(s): %s" % missing)
        if extra:
            e.append("[1c] captured chapter_structure covers out-of-range article(s): %s" % extra)

    # full-regulation reference structure must be present, cover 1..90, and be self-consistent
    if src.get("full_regulation_article_count") != FULL_N:
        e.append("[1f] full_regulation_article_count must be %d" % FULL_N)
    if src.get("full_regulation_chapter_count") != EXPECTED_FULL_CHAPTERS:
        e.append("[1f] full_regulation_chapter_count must be %d" % EXPECTED_FULL_CHAPTERS)
    fchs = src.get("full_regulation_chapter_structure") or []
    if len(fchs) != EXPECTED_FULL_CHAPTERS:
        e.append("[1f] full_regulation_chapter_structure must list %d chapters, got %d"
                 % (EXPECTED_FULL_CHAPTERS, len(fchs)))
    fcov = set()
    for lo, hi in _iter_chapter_ranges(fchs):
        fcov.update(range(lo, hi + 1))
    if fcov != set(range(1, FULL_N + 1)):
        e.append("[1f] full_regulation_chapter_structure must cover articles 1..%d exactly" % FULL_N)

    sc = Counter()
    for k, a in arts.items():
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNCHANGED)
        if a.get("status") not in ("DUAL_SOURCE_QANONIAH_CLEAN_AR_X_WIPO_LEX_AR_CORROBORATED",):
            e.append("[2] %s: unexpected verification status %r" % (k, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if k not in (AMENDED_KEYS | ADDED_KEYS) and a.get("history"):
            e.append("[2i] %s: non-amended/added article must have empty history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "‌" in a["text"] or "‍" in a["text"]:
            e.append("[2f] %s: residual zero-width-joiner/non-joiner artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if re.search(r"[ً-ْ]", a["text"]):
            e.append("[2f] %s: residual tashkeel (should be stripped) detected" % k)
        # WIPO digit-CMap regression guard: captured text must NOT contain the
        # garbled decision-number/date artifacts; only the safe digits 1-4 may appear.
        for bad in ("663", "1441/1/52", "1440/3/52"):
            if bad in a["text"]:
                e.append("[2g] %s: contains WIPO digit-CMap garble %r (must use clean source)" % (k, bad))
        for d in re.findall(r"[0-9]", a["text"]):
            if d not in "01234":
                e.append("[2g] %s: unexpected digit %r in captured text (arts 1-5 use only 1-4)" % (k, d))

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
        e.append("[2k] missing amendment_history (must record founding + 2023 art-12 amendment)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "337" not in decrees:
            e.append("[2k] amendment_history must reference founding decree 337")

    if not src.get("supersedes"):
        e.append("[2s] missing supersedes block (2014 Regulation, Decision 126, 4/9/1435H)")
    else:
        if "126" not in str(src["supersedes"].get("decree", "")):
            e.append("[2s] supersedes.decree must reference predecessor Decision 126")

    # spot-checks anchoring key facts established this pass
    a1 = arts.get("competition_regulation_art_001", {})
    if "المملكة العربية السعودية" not in a1.get("text", "") or "التركز الاقتصادي" not in a1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (المملكة / التركز الاقتصادي)")
    a2 = arts.get("competition_regulation_art_002", {})
    if "حماية المنافسة العادلة" not in a2.get("text", ""):
        e.append("[2j] Article 2 missing expected objective (حماية المنافسة العادلة)")
    a5 = arts.get("competition_regulation_art_005", {})
    if "صاحبة الاختصاص الأصيل" not in a5.get("text", ""):
        e.append("[2j] Article 5 missing expected phrase (صاحبة الاختصاص الأصيل)")
    if src.get("decree") != "قرار مجلس إدارة الهيئة العامة للمنافسة رقم (337)" \
            or src.get("decree_date_hijri") != "25/1/1441":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Board Decision 337, 25/1/1441H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (captured arts 1-5 are original text)")

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
    if summary.get("full_regulation_article_count") != FULL_N:
        e.append("[4b] summary must carry full_regulation_article_count=%d" % FULL_N)

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
        if r.get("english_used_for_correction") is not False:
            e.append("[5] %s: english_used_for_correction must be False" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Competition Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Saudi Competition Law")
    print("  - CAPTURED SCOPE: 5 records (Articles 1-5), all اصلية — Chapters 1-2 of 11")
    print("  - FULL regulation: 90 articles across 11 chapters (recorded in")
    print("    full_regulation_chapter_structure); Articles 6-90 intentionally NOT ingested,")
    print("    disclosed in known_unresolved_discrepancies (partial_scope_arts_6_90_pending)")
    print("  - GAC Board of Directors Decision No. (337), 25/1/1441H (24 Sep 2019), pursuant to")
    print("    Article 27 of the Competition Law (M/75); Umm al-Qura issue 4806 (22 Nov 2019)")
    print("  - VERIFICATION TIER: DUAL INDEPENDENT SOURCE for arts 1-5 — qanoniah.com clean")
    print("    Arabic API (primary text) × WIPO Lex official Arabic PDF sa071ar.pdf (letters)")
    print("  - laws.boe.gov.sa checked first: unreachable this pass AND no dedicated lawId page")
    print("    for this Board-level Implementing Regulation; gac.gov.sa (issuer) unreachable")
    print("  - SUPERSEDES the 2014 Implementing Regulation (Competition Council Decision 126,")
    print("    4/9/1435H, under the repealed Competition Law M/25) — confirmed via WIPO Lex")
    print("  - Article 12(1) was amended in 2023 (GAC Board 80th session) — OUTSIDE captured")
    print("    scope (Chapter 4); disclosed, not applied")
    print("  - WIPO Arabic PDF numerals unusable (disclosed lossy digit-CMap): the reason the")
    print("    remaining 85 articles are pending, not fabricated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
