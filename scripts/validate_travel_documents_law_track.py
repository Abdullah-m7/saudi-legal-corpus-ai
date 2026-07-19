#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Travel Documents Law track (16
records: 8 اصلية, 6 معدلة [Articles 2, 4, 6, 10, 11, 12], 1 ملغاة [Article
3], 1 مضافة [Article 10 مكرر]; flat structure -- NO أبواب/فصول grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/travel_documents/law/official_source/travel_documents_law_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa's LIVE
portal was unreachable this pass (TLS connection failure via curl, HTTP 503
via WebFetch), but THREE Wayback Machine snapshots of the exact BOE law page,
spanning 13 Nov 2019 - 12 Dec 2025, were reachable via direct curl and
cross-diffed. All 15 numbered articles are byte-stable across all three
time-points; the added Article 10 مكرر is absent in 2019 and present,
byte-identical, from 2022 onward -- consistent with its real M/11 (1443H)
decree date. Cross-checked against nezams.com and qistas.com (independent
private aggregators) and, for the M/11 amendment specifically, the official
Umm Al-Qura Gazette (a genuinely separate official/primary source). Overall
self-assessed tier: TIER_2 (honest, not inflated -- only the M/11-derived
provisions individually reach TIER_1-caliber confidence). This validator
does not re-adjudicate any of this; it only checks internal self-consistency
of the text this track actually ingests, and that every discrepancy found
this pass is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "travel_documents", "law", "official_source",
                   "travel_documents_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "travel_documents", "law", "verified",
                       "travel_documents_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "travel_documents", "law", "verified",
                       "travel_documents_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "travel_documents_arabic_legal_llm",
                   "travel_documents_law_legal_llm_001_016.json")
N = 16
KEY_RE = r"travel_documents_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 8, "معدلة": 6, "ملغاة": 1, "مضافة": 1}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat law -- no أبواب/فصول, single leaf range 1-15

STATUS_UNCHANGED = ("BOE_WAYBACK_THREE_TIMEPOINT_NOV2019_DEC2022_DEC2025_TEXT_STABLE_X_"
                    "NEZAMS_COM_QISTAS_COM_CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_M134_FULLTEXT = ("BOE_CHANGELOG_FULLTEXT_REPLACEMENT_M134_1440H_CLEAN_INCORPORATED_X_"
                        "NEZAMS_COM_QISTAS_COM_CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_M134_REPEALED = ("BOE_CHANGELOG_REPEALED_M134_1440H_TEXT_PRESERVED_X_"
                        "NEZAMS_COM_QISTAS_COM_CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_ART6_CM217 = ("BOE_CHANGELOG_PARA2_PHRASE_INSERTION_CLEAN_X_NEZAMS_COM_SUPPLIES_CM217_1439H_"
                    "DECREE_CITATION_BOE_CHANGELOG_ITSELF_OMITS_DECREE_NUMBER_LIVE_BOE_UNREACHABLE")
STATUS_ART10_M11 = ("BOE_CHANGELOG_PHRASE_SUBSTITUTION_M11_1443H_CLEAN_X_UQN_GOV_SA_OFFICIAL_"
                    "GAZETTE_CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_ART10BIS_M11 = ("BOE_CHANGELOG_NEW_ARTICLE_ADDED_M11_1443H_X_UQN_GOV_SA_OFFICIAL_GAZETTE_"
                       "CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_ART11_M11 = ("BOE_CHANGELOG_PARA3_FULLTEXT_REPLACEMENT_M11_1443H_CLEAN_X_UQN_GOV_SA_"
                    "OFFICIAL_GAZETTE_CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_ART12_TWOSTEP = ("BOE_CHANGELOG_TWO_STEP_M48_1437H_FULLTEXT_PLUS_M71_1444H_PARAGRAPH_"
                        "ADDITION_CLEAN_INCORPORATED_X_NEZAMS_COM_QISTAS_COM_CROSSCHECK_"
                        "LIVE_BOE_UNREACHABLE")

AMENDED_KEYS = {"travel_documents_art_%03d" % n for n in (2, 4, 6, 10, 11, 12)}
ADDED_KEYS = {"travel_documents_art_010_mukarrar"}
REPEALED_KEYS = {"travel_documents_art_003"}
MUKARRAR_KEYS = {"travel_documents_art_010_mukarrar"}

EXPECTED_STATUS_BY_KEY = {
    "travel_documents_art_002": STATUS_M134_FULLTEXT,
    "travel_documents_art_003": STATUS_M134_REPEALED,
    "travel_documents_art_004": STATUS_M134_FULLTEXT,
    "travel_documents_art_006": STATUS_ART6_CM217,
    "travel_documents_art_010": STATUS_ART10_M11,
    "travel_documents_art_010_mukarrar": STATUS_ART10BIS_M11,
    "travel_documents_art_011": STATUS_ART11_M11,
    "travel_documents_art_012": STATUS_ART12_TWOSTEP,
}

FLAGGED_DISCREPANCY_KEYS = {
    "travel_documents_gap_map_estimate_confirmed",
    "travel_documents_boe_main_body_stale_for_6_articles",
    "travel_documents_article6_decree_citation_missing_from_boe_own_changelog",
    "travel_documents_article10_boe_own_changelog_before_phrase_mismatch",
    "travel_documents_predecessor_law_1358h_partial_repeal_not_in_corpus",
    "travel_documents_diplomatic_special_passports_separate_law_not_ingested",
    "travel_documents_implementing_regulation_not_ingested",
    "travel_documents_no_baab_fasl_structure",
    "travel_documents_no_inline_article_titles",
    "travel_documents_moi_gov_sa_unreachable",
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
    """Yield (lo, hi) for every leaf range in chapter_structure. This Law has
    no أبواب/فصول nesting -- the single top-level entry IS the leaf. The
    added Article 10 مكرر is not a distinct integer in this range (it shares
    base number 10 with a _mukarrar suffix) -- range 1-15 already covers it."""
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

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d top-level chapter_structure entries (flat law, "
                  "no أبواب/فصول), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

    numbered_count = sum(1 for k in arts if k not in MUKARRAR_KEYS)
    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one leaf range" % n)
            covered.add(n)
    if covered != set(range(1, numbered_count + 1)):
        missing = sorted(set(range(1, numbered_count + 1)) - covered)
        extra = sorted(covered - set(range(1, numbered_count + 1)))
        if missing:
            e.append("[1c] chapter_structure missing article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])

    sc = Counter()
    for k, a in arts.items():
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNCHANGED)
        if a.get("status") != expected_status:
            e.append("[2] %s: expected status %r, got %r" % (k, expected_status, a.get("status")))
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
        if k in (AMENDED_KEYS | REPEALED_KEYS | ADDED_KEYS) and not a.get("history"):
            e.append("[2] %s: amended/repealed/added article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if k not in (AMENDED_KEYS | REPEALED_KEYS | ADDED_KEYS) and a.get("history"):
            e.append("[2i] %s: non-amended/non-repealed/non-added article must have "
                     "empty history[]" % k)
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present (BOE source supplies no "
                      "inline per-article titles for this law -- see "
                      "known_unresolved_discrepancies)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)

    for key in (AMENDED_KEYS | REPEALED_KEYS):
        hist = arts.get(key, {}).get("history", [])
        if len(hist) < 2:
            e.append("[2j] %s must record at least 2 history entries (original + "
                     ">=1 amendment/repeal)" % key)
    for key in ADDED_KEYS:
        hist = arts.get(key, {}).get("history", [])
        if len(hist) < 1:
            e.append("[2j] %s must record at least 1 history entry (the adding decree)" % key)

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
        e.append("[2k] missing amendment_history (must record founding decree + amendments)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        for token in ("م/24", "م/134", "م/11", "م/71"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference %s" % token)

    # spot-checks anchoring key facts established this pass
    art2 = arts.get("travel_documents_art_002", {})
    if "يمنح جواز السفر لكل من يقدم طلباً" not in art2.get("text", ""):
        e.append("[2j] Article 2 missing expected M/134 (1440H) full-text replacement")
    art3 = arts.get("travel_documents_art_003", {})
    if "يجوز أن يشمل جواز السفر زوجة حامله" not in art3.get("text", ""):
        e.append("[2j] Article 3 (repealed) must still preserve its original text verbatim")
    art4 = arts.get("travel_documents_art_004", {})
    if "للخاضعين للحضانة والقصّر المتوفى وليّهم" not in art4.get("text", ""):
        e.append("[2j] Article 4 missing expected M/134 (1440H) full-text replacement")
    art6 = arts.get("travel_documents_art_006", {})
    if "أو رئيس أمن الدولة" not in art6.get("text", ""):
        e.append("[2j] Article 6 missing expected CoM 217 (1439H) paragraph-2 insertion")
    art10 = arts.get("travel_documents_art_010", {})
    if "مائة ألف ريال" not in art10.get("text", ""):
        e.append("[2j] Article 10 missing expected M/11 (1443H) penalty amendment")
    if "خمسة آلاف ريال" in art10.get("text", ""):
        e.append("[2j] Article 10 must NOT retain the pre-M/11 fine amount it superseded")
    art10bis = arts.get("travel_documents_art_010_mukarrar", {})
    if "تصنيف المخالفات" not in art10bis.get("text", ""):
        e.append("[2j] Article 10 مكرر missing expected M/11 (1443H) added text")
    art11 = arts.get("travel_documents_art_011", {})
    if "النيابة العامة" not in art11.get("text", ""):
        e.append("[2j] Article 11 missing expected M/11 (1443H) paragraph-3 replacement")
    art12 = arts.get("travel_documents_art_012", {})
    if "خمسمائة" not in art12.get("text", "") or "ستون" not in art12.get("text", ""):
        e.append("[2j] Article 12 missing expected M/48+M/71 two-step fee amendment")
    if "ثلاثمائة ريال" in art12.get("text", ""):
        e.append("[2j] Article 12 must NOT retain the pre-M/48 fee it superseded")
    art13 = arts.get("travel_documents_art_013", {})
    if "1358" not in art13.get("text", "") or "يحل" not in art13.get("text", ""):
        e.append("[2j] Article 13 missing expected reference to the superseded 1358H "
                 "Passports System")
    if src.get("decree") != "المرسوم الملكي رقم (م/24)" or src.get("decree_date_hijri") != "28/5/1421":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/24, 28/5/1421H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (this track incorporates all "
                 "cleanly-reconstructable amendments into current article text)")

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
        expected_status = EXPECTED_STATUS_BY_KEY.get(r["article_key"], STATUS_UNCHANGED)
        if r.get("source_trust", {}).get("source_status") != expected_status.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Travel Documents Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Arabian Travel Documents Law")
    print("  - 16 records: 8 اصلية, 6 معدلة (Articles 2, 4, 6, 10, 11, 12), 1 ملغاة")
    print("    (Article 3), 1 مضافة (Article 10 مكرر)")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-15); no")
    print("    inline per-article titles in the BOE source (no title_ar key used)")
    print("  - VERIFICATION TIER: TIER_2 (honest, not inflated) -- BOE-via-Wayback-Machine,")
    print("    THREE snapshots spanning 13 Nov 2019 - 12 Dec 2025, x nezams.com/qistas.com")
    print("    independent reproduction, x official Umm Al-Qura Gazette cross-check for")
    print("    the M/11 (1443H) amendment specifically (that subset alone reaches")
    print("    TIER_1-caliber confidence; the rest rests on BOE + private aggregators only)")
    print("  - Royal Decree M/24 (28/5/1421H / 2000G), approved via Council of Ministers")
    print("    Resolution 122 (21/5/1421H); Article 13 states this law and its Implementing")
    print("    Regulation supersede the travel-document-related provisions (a SCOPED/PARTIAL")
    print("    supersession, not a blanket repeal) of the prior 1358H Passports System (not")
    print("    in this corpus, historical context only, not ingested)")
    print("  - TWO GENUINE BOE-SOURCE ANOMALIES flagged, not silently fixed: Article 6's own")
    print("    changelog omits any decree citation; Article 10's changelog before-quote does")
    print("    not character-for-character match BOE's own main body")
    print("  - Companion instruments identified but NOT ingested this pass: اللائحة")
    print("    التنفيذية لنظام وثائق السفر, and the wholly separate نظام جوازات السفر")
    print("    السياسية والخاصة")
    return 0


if __name__ == "__main__":
    sys.exit(main())
