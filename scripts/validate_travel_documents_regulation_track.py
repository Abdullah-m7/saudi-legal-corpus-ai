#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Travel Documents Implementing
Regulation track (53 records, all اصلية -- 0 معدلة, 0 ملغاة, 0 مضافة; 10
formally-numbered فصول [chapters]).

VERIFICATION TIER -- see the generator's module docstring and
sources/travel_documents/regulation/official_source/
travel_documents_regulation_official_source.json's verification_methodology_note
for the full account: laws.boe.gov.sa has NO dedicated page at all for this
Implementing Regulation (current or superseded); moi.gov.sa/gdp.gov.sa were
unreachable this pass; uqn.gov.sa (the gazette this Regulation's own Article
53 names) was domain-reachable but its specific article page could not be
located. The text rests entirely on qanoonsa.com (private aggregator, direct
raw-HTML fetch, not WebFetch-summarized), cross-checked at the decree-metadata
level against ncar.gov.sa (a genuine government archival body) and
qanoniah.com (private, indexing-level only). Honest self-assessed tier:
TIER_3 (per this corpus's own verification-tier taxonomy), NOT inflated. This
validator does not re-adjudicate any of this; it only checks internal
self-consistency of the text this track actually ingests, and that every
discrepancy found this pass is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "travel_documents", "regulation", "official_source",
                   "travel_documents_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "travel_documents", "regulation", "verified",
                       "travel_documents_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "travel_documents", "regulation", "verified",
                       "travel_documents_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "travel_documents_regulation_arabic_legal_llm",
                   "travel_documents_regulation_legal_llm_001_053.json")
N = 53
KEY_RE = r"travel_documents_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 53, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 10  # formally-numbered فصول

STATUS_UNCHANGED = ("QANOONSA_COM_RAW_HTML_DIRECT_FETCH_MAR2026_PUBLISH_APR2026_WAYBACK_"
                     "JUL2026_LIVE_STABLE_X_NCAR_GOV_SA_OFFICIAL_ARCHIVE_METADATA_CROSSCHECK_X_"
                     "QANONIAH_COM_INDEX_CONFIRM_BOE_NO_DEDICATED_LAWID_MOI_GDP_UNREACHABLE_"
                     "UQN_GOV_SA_REACHABLE_BUT_SPECIFIC_GAZETTE_PAGE_NOT_LOCATED_THIS_PASS")
STATUS_ART37_ANOMALY = STATUS_UNCHANGED + "_PARA3_SOURCE_TYPO_VERBATIM_PRESERVED_NOT_SILENTLY_CORRECTED"
ANOMALY_KEYS = {"travel_documents_regulation_art_037"}
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY = {k: STATUS_ART37_ANOMALY for k in ANOMALY_KEYS}
FLAGGED_DISCREPANCY_KEYS = {
    "travel_documents_regulation_boe_no_dedicated_lawid",
    "travel_documents_regulation_moi_gdp_unreachable",
    "travel_documents_regulation_uqn_reachable_but_page_not_located",
    "travel_documents_regulation_article37_para3_typo_preserved",
    "travel_documents_regulation_hijri_date_year_only",
    "travel_documents_regulation_no_full_preamble_found",
    "travel_documents_regulation_predecessor_7woz_1422h_not_ingested",
    "travel_documents_regulation_rlm_normalization",
    "travel_documents_regulation_public_consultation_context",
    "travel_documents_regulation_wayback_single_snapshot_only",
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

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d formally-numbered فصول, got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

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
            e.append("[1c] chapter_structure missing article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])
    # every chapter must have a proper الفصل label
    for ch in chs:
        if not ch.get("label_ar", "").startswith("الفصل"):
            e.append("[1c] chapter label %r does not start with 'الفصل'" % ch.get("label_ar"))

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
        if k not in AMENDED_KEYS and a.get("history"):
            e.append("[2i] %s: non-amended article must have empty history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if "‏" in a["text"]:
            e.append("[2f] %s: residual RLM (U+200F) artifact detected -- must be stripped" % k)

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
        e.append("[2k] missing amendment_history (must record founding decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "4203" not in decrees and "٤٢٠٣" not in decrees:
            e.append("[2k] amendment_history must reference decree 4203 / ٤٢٠٣")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("travel_documents_regulation_art_001", {})
    if "مدير عام الجوازات" not in art1.get("text", "") or "منصة أبشر" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (مدير عام الجوازات / منصة أبشر)")
    art37 = arts.get("travel_documents_regulation_art_037", {})
    if "مي نع المخالف" not in art37.get("text", ""):
        e.append("[2j] Article 37 should preserve the confirmed source-side typo 'مي نع' "
                 "verbatim -- do not silently correct it to 'يمنع'")
    art52 = arts.get("travel_documents_regulation_art_052", {})
    if "٧ / وز" not in art52.get("text", "") and "7 / وز" not in art52.get("text", "") and \
       "٧/وز" not in art52.get("text", "") and "7/وز" not in art52.get("text", ""):
        e.append("[2j] Article 52 missing expected repeal citation of Decision 7/waw-zay (1422H)")
    art53 = arts.get("travel_documents_regulation_art_053", {})
    if "٥١٥١" not in art53.get("text", "") and "5151" not in art53.get("text", ""):
        e.append("[2j] Article 53 missing expected Umm Al-Qura gazette issue citation (5151)")
    if src.get("decree") != "القرار الوزاري رقم (٤٢٠٣)":
        e.append("[2j] decree mismatch with verified Ministerial Resolution 4203")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (founding single-version "
                 "instrument, not a consolidated multi-amendment law)")

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
        print("FAIL: %d error(s) in Travel Documents Implementing Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Arabian Travel Documents Implementing Regulation")
    print("  - 53 records: 53 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة")
    print("  - 10 formally-numbered فصول (chapters) -- unlike the flat travel_documents_law")
    print("    (no أبواب/فصول) or the informally-sectioned domestic_labor_regulation")
    print("  - VERIFICATION TIER: TIER_3 (honest, not inflated) -- laws.boe.gov.sa has NO")
    print("    dedicated page for this instrument at all; moi.gov.sa/gdp.gov.sa unreachable;")
    print("    uqn.gov.sa domain-reachable but its specific gazette page not located this pass.")
    print("    Text rests on qanoonsa.com (private aggregator, direct raw-HTML fetch, Wayback-")
    print("    stable since 16 Apr 2026), cross-checked at the decree-metadata level against")
    print("    ncar.gov.sa (a genuine government archival body) and qanoniah.com (private)")
    print("  - Ministerial Resolution No. 4203 (1447H), published Umm Al-Qura Gazette No. 5151,")
    print("    30 March 2026G, effective immediately from publication (Article 53) -- in force")
    print("    since before this pass (19 July 2026)")
    print("  - CONFIRMED NAMED REPEAL (full, not scoped): replaces the prior Implementing")
    print("    Regulation issued by Ministerial Decision 7/waw-zay (23/9/1422H) and its")
    print("    amendments (Article 52) -- not in this corpus, historical context only")
    print("  - ANOMALY: Article 37(3)'s 'يمنع' appears source-side as split 'مي نع' -- preserved")
    print("    verbatim, not silently corrected, absent a second independent extraction of the")
    print("    same original document")
    print("  - RLM (U+200F) directional-control characters (111 occurrences) stripped as pure")
    print("    typographic normalization, consistent with this corpus's NBSP/curly-quote precedent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
