#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Maritime Commercial Law track (391 records,
all اصلية; hierarchical structure: an introductory فصل تمهيدي (definitions),
10 أبواب (most with فصول, some فصول further split into أولاً/ثانياً/...
subsections), and a closing أحكام عامة ختامية section).

VERIFICATION TIER -- see the generator's module docstring and
sources/maritime_commercial/law/official_source/
maritime_commercial_law_official_source.json's verification_methodology_note
for the full caveat: laws.boe.gov.sa's LIVE portal was unreachable this
pass, but Wayback Machine archives of BOTH the exact Arabic law page AND
BOE's own official English-translation PDF WERE reachable and are treated
as the primary + tertiary sources, cross-verified against nezams.com
(secondary; exact agreement on 381/391 articles, with a documented,
resolved nezams-side duplication bug for Articles 316-325). This Royal
Decree has never been amended since 1440H -- all 391 articles are اصلية."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "maritime_commercial", "law", "official_source",
                   "maritime_commercial_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "maritime_commercial", "law", "verified",
                       "maritime_commercial_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "maritime_commercial_arabic_legal_llm",
                   "maritime_commercial_law_legal_llm_001_391.json")
N = 391
KEY_RE = r"maritime_commercial_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 391, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
STATUS = "BOE_WAYBACK_ARCHIVE_X_NEZAMS_X_BOE_OFFICIAL_ENGLISH_TRANSLATION_TRIPLE_VERIFIED_LIVE_BOE_UNREACHABLE"
EXPECTED_TOP_LEVEL_CHAPTERS = 12  # فصل تمهيدي + 10 أبواب + أحكام عامة ختامية
AMENDED_KEYS = set()  # no amended articles -- this Royal Decree has never been amended
MUKARRAR_KEYS = set()  # no مكرر articles in this Law
FLAGGED_DISCREPANCY_KEYS = {
    "maritime_commercial_nezams_duplicate_bug_articles_316_325",
    "maritime_commercial_multiple_implementing_regulations_not_ingested",
    "maritime_commercial_al_rais_vs_al_wazir_terminology_note",
    "maritime_commercial_nbsp_and_quote_cosmetic_normalization",
    "maritime_commercial_predecessor_repeal_scope_not_exhaustively_cross_checked",
    "maritime_commercial_qistas_qanoniah_inconclusive_third_sources",
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
    """Yield (lo, hi) for every leaf range in the (up to 3-level)
    chapter_structure: top-level باب/فصل-تمهيدي/أحكام-ختامية items, their
    فصول ('sections'), and those فصول' own أولاً/ثانياً subsections
    ('subsections'). A leaf is any range that has no further children --
    those are the ranges actually assigned to articles."""
    for ch in chs:
        secs = ch.get("sections")
        if not secs:
            lo, hi = (int(x) for x in ch["articles"].split("-"))
            yield (lo, hi)
            continue
        for sec in secs:
            subs = sec.get("subsections")
            if not subs:
                slo, shi = (int(x) for x in sec["articles"].split("-"))
                yield (slo, shi)
                continue
            for sub in subs:
                sslo, sshi = (int(x) for x in sub["articles"].split("-"))
                yield (sslo, sshi)


def _count_top_level(chapter_structure):
    return len(chapter_structure)


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

    chs = src.get("chapter_structure") or []
    n_top = _count_top_level(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d top-level chapter_structure entries, got %d" %
                  (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

    # leaf-range coverage: every article 1..N must fall inside exactly one
    # leaf range (a فصل tمهيدي/باب-without-فصول/فصل/subsection), no overlaps.
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

    # also verify each top-level باب's own declared 'articles' span exactly
    # equals the union of its فصول's spans (internal consistency of the
    # 3-level structure), and likewise for فصول with subsections.
    for ch in chs:
        secs = ch.get("sections")
        if not secs:
            continue
        clo, chi = (int(x) for x in ch["articles"].split("-"))
        slos, shis = [], []
        for sec in secs:
            slo, shi = (int(x) for x in sec["articles"].split("-"))
            slos.append(slo); shis.append(shi)
            subs = sec.get("subsections")
            if subs:
                sslo0 = int(subs[0]["articles"].split("-")[0])
                sshiN = int(subs[-1]["articles"].split("-")[1])
                if (sslo0, sshiN) != (slo, shi):
                    e.append("[1d] %s/%s: subsections span %d-%d != فصل span %d-%d" %
                              (ch.get("label_ar"), sec.get("label_ar"), sslo0, sshiN, slo, shi))
        if (min(slos), max(shis)) != (clo, chi):
            e.append("[1d] %s: فصول span %d-%d != باب span %d-%d" %
                      (ch.get("label_ar"), min(slos), max(shis), clo, chi))

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
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (expected a باب/فصل path)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in MUKARRAR_KEYS):
            e.append("[2] %s: legal_status_ar/MUKARRAR_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")):
            e.append("[2] %s: unexpected is_mukarrar=True (no مكرر articles enacted "
                      "in this law)" % k)
        # residual whitespace/quote-glyph artifacts that this track's own
        # normalization is documented to have already fixed must not survive
        if " " in a["text"]:
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

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("maritime_commercial_art_001", {})
    if "الوزير" not in art1.get("text", "") or "الهيئة" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected core defined terms (الوزير/الهيئة)")
    art391 = arts.get("maritime_commercial_art_391", {})
    if "المرسوم الملكي رقم (32)" not in art391.get("text", "") and "المرسوم الملكي رقم (32) " not in art391.get("text", ""):
        if "رقم (32)" not in art391.get("text", ""):
            e.append("[2j] Article 391 missing expected predecessor-repeal reference to Royal Decree No. 32")
    if "نظام الموانئ والمرافئ والمنائر البحرية" not in art391.get("text", ""):
        e.append("[2j] Article 391 missing expected repeal reference to the Ports/Harbours/Lighthouses Law")
    art390 = arts.get("maritime_commercial_art_390", {})
    if "مائة وثمانين" not in art390.get("text", ""):
        e.append("[2j] Article 390 missing expected 180-day regulations deadline")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        expected_original = a.get("original_1440h_text")
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
        print("FAIL: %d error(s) in Maritime Commercial Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Commercial Maritime Law — 391 records (all اصلية)")
    print("  - hierarchical structure: فصل تمهيدي (definitions, Art 1) + 10 أبواب")
    print("    (8 with فصول, 2 without: الباب الثامن and الباب العاشر) + أحكام عامة ختامية;")
    print("    الباب الخامس/الفصل الرابع further splits into 5 أولاً..خامساً subsections")
    print("  - VERIFICATION TIER: BOE-via-Wayback-Machine archive (primary, live BOE")
    print("    unreachable) x nezams.com live HTML transcription (381/391 exact agreement)")
    print("    x BOE's own official English-translation PDF (tertiary, resolves the")
    print("    remaining 10-article nezams duplication-bug range, Articles 316-325)")
    print("  - IN-FORCE Royal Decree M/33 (5/4/1440H); NEVER amended since enactment")
    print("  - Repeals Book Two of the Commercial Court Regulation (Royal Decree No. 32,")
    print("    15/1/1350H) and the Ports, Harbours and Lighthouses Law (Royal Decree")
    print("    M/27, 24/6/1394H) per its own Article 391")
    print("  - Multiple companion implementing regulations (plural, per Article 390)")
    print("    identified but NOT ingested this pass -- candidates for follow-up")
    return 0


if __name__ == "__main__":
    sys.exit(main())
