#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Law of the Accounting and Auditing Profession
track (22 records: 17 اصلية, 5 معدلة, 0 ملغاة, 0 مضافة; flat structure --
NO أبواب/فصول grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/accounting_auditing/law/official_source/
accounting_auditing_law_official_source.json's verification_methodology_note
for the full caveat: laws.boe.gov.sa's LIVE portal was unreachable this
pass, but a single Wayback Machine snapshot (20251015113239) of the exact
BOE law page WAS reachable and is treated as the primary source. For the 5
معدلة articles (1, 4, 5, 19, 20), BOE's own MAIN body text on that same
snapshot is demonstrably STALE (pre-Royal-Decree-M/169) -- confirmed by
diffing three Wayback snapshots spanning Jan-Oct 2025 -- so this track
instead ingests BOE's own per-article changelog-popup wording (which
directly quotes M/169), cross-verified word-for-word against SOCPA's own
official PDF of the law and against qanoonsa.com. Article 1 carries a
further, second amendment (Council of Ministers Resolution 283,
22/4/1447H) sourced only from SOCPA's PDF + qanoonsa.com, since it
postdates this track's only available BOE snapshot. This validator does
not attempt to re-adjudicate any of this; it only checks internal
self-consistency of the text this track actually ingests, and that every
discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "accounting_auditing", "law", "official_source",
                   "accounting_auditing_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "accounting_auditing", "law", "verified",
                       "accounting_auditing_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "accounting_auditing", "law", "verified",
                       "accounting_auditing_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "accounting_auditing_arabic_legal_llm",
                   "accounting_auditing_law_legal_llm_001_022.json")
N = 22
KEY_RE = r"accounting_auditing_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 17, "معدلة": 5, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat law -- no أبواب/فصول, single leaf range 1-22

STATUS_UNCHANGED = ("BOE_WAYBACK_ARCHIVE_MAIN_BODY_PRIMARY_X_SOCPA_OFFICIAL_PDF_"
                     "CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_M169 = ("BOE_WAYBACK_CHANGELOG_POPUP_M169_TEXT_X_SOCPA_OFFICIAL_PDF_X_"
               "QANOONSA_DUAL_ANNOUNCEMENT_CROSSCHECK_BOE_MAIN_BODY_STALE_"
               "LIVE_BOE_UNREACHABLE")
STATUS_M169_CR283 = ("BOE_CHANGELOG_POPUP_M169_TEXT_PLUS_CR283_NOT_YET_ON_BOE_X_"
                      "SOCPA_OFFICIAL_PDF_X_QANOONSA_CROSSCHECK_BOE_MAIN_BODY_"
                      "STALE_LIVE_BOE_UNREACHABLE")
EXPECTED_STATUS_BY_KEY = {
    "accounting_auditing_art_001": STATUS_M169_CR283,
    "accounting_auditing_art_004": STATUS_M169,
    "accounting_auditing_art_005": STATUS_M169,
    "accounting_auditing_art_019": STATUS_M169,
    "accounting_auditing_art_020": STATUS_M169,
}
AMENDED_KEYS = set(EXPECTED_STATUS_BY_KEY)
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
FLAGGED_DISCREPANCY_KEYS = {
    "accounting_auditing_boe_main_body_stale_vs_changelog_popup",
    "accounting_auditing_cr283_not_yet_reflected_on_boe",
    "accounting_auditing_boe_live_portal_unreachable_wayback_used",
    "accounting_auditing_no_inline_article_titles",
    "accounting_auditing_no_chapter_baab_fasl_structure",
    "accounting_auditing_title_naming_nuance_mazawala",
    "accounting_auditing_implementing_regulation_not_ingested_this_pass",
    "accounting_auditing_socpa_organizational_statute_not_conflated",
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
    no أبواب/فصول nesting -- every top-level entry IS a leaf (no 'sections'
    key), so this is a flat single-level walk."""
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
        e.append("[1c] expected %d top-level chapter_structure entries (flat law, "
                  "no أبواب/فصول), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

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
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNCHANGED)
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
        e.append("[2k] missing amendment_history (must record M/59, M/169, and CR 283)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        for token in ("م/59", "م/169", "283"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference %s" % token)

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("accounting_auditing_art_001", {})
    if "مجلس الشؤون الاقتصادية والتنمية" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected CR283-amended الوزير definition")
    if "الوزارة" in art1.get("text", ""):
        e.append("[2j] Article 1 unexpectedly still contains a الوزارة definition "
                  "(should have been deleted by M/169)")
    art21 = arts.get("accounting_auditing_art_021", {})
    if "م  /  12" not in art21.get("text", "") and "م / 12" not in art21.get("text", "") \
            and "م/12" not in art21.get("text", ""):
        e.append("[2j] Article 21 missing expected predecessor decree citation (M/12)")
    if "1412" not in art21.get("text", ""):
        e.append("[2j] Article 21 missing expected predecessor decree year (1412H)")
    art4 = arts.get("accounting_auditing_art_004", {})
    if "يحدد المجلس المقابل المالي للترخيص" not in art4.get("text", ""):
        e.append("[2j] Article 4 missing expected M/169-amended fee-setting clause")
    if src.get("decree") != "المرسوم الملكي رقم (م/59)" or src.get("decree_date_hijri") != "27/7/1442":
        e.append("[2j] decree/decree_date_hijri mismatch with verified M/59, 27/7/1442H")

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
        print("FAIL: %d error(s) in Accounting and Auditing Profession Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Law of the Accounting and Auditing Profession")
    print("  - 22 records: 17 اصلية, 5 معدلة (Arts 1, 4, 5, 19, 20), 0 ملغاة, 0 مضافة")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-22); no")
    print("    inline per-article titles in the BOE source (no title_ar key used)")
    print("  - VERIFICATION TIER: BOE-via-Wayback-Machine archive (primary, live BOE")
    print("    unreachable, snapshot 20251015113239) x SOCPA's own official PDF of the")
    print("    law (Wayback 20260116022237) x qanoonsa.com (2 independent pages)")
    print("  - Royal Decree M/59 (27/7/1442H), Council of Ministers Resolution 416")
    print("    (25/7/1442H); replaces Royal Decree M/12 (13/5/1412H, status لاغي on BOE)")
    print("  - MAJOR VERIFIED ANOMALY carried forward: BOE's own archived page shows a")
    print("    'changed-article' flag + changelog popup (quoting Royal Decree M/169,")
    print("    10/8/1446H) for Arts 1/4/5/19/20, but that SAME page's main displayed")
    print("    body text for those articles is stale (pre-M/169) -- this track ingests")
    print("    the amended (changelog-popup) wording, cross-verified against SOCPA's")
    print("    PDF, not the stale main body (see known_unresolved_discrepancies)")
    print("  - Article 1 carries a further, second amendment (Council of Ministers")
    print("    Resolution 283, 22/4/1447H) postdating this track's only BOE snapshot,")
    print("    sourced from SOCPA's PDF + qanoonsa.com only -- flagged, not silently")
    print("    resolved")
    print("  - Implementing Regulation and SOCPA's own organizational statute (تنظيم")
    print("    الهيئة) identified but NOT ingested/conflated this pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
