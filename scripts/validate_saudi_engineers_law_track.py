#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Law of the Saudi Council of Engineers track
(9 records: 7 اصلية, 2 معدلة [Articles 1, 6], 0 ملغاة, 0 مضافة; flat
structure -- NO أبواب/فصول grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/saudi_engineers/law/official_source/
saudi_engineers_law_official_source.json's verification_methodology_note for
the full account: laws.boe.gov.sa's LIVE portal was unreachable this pass
(HTTP 503), but THREE Wayback Machine snapshots of the exact BOE law page,
spanning 15 Nov 2019 - 15 Sep 2025, were reachable via direct curl (WebFetch
itself refuses web.archive.org in this environment) and cross-diffed. 7 of 9
articles are byte-stable across all three time-points. Articles 1 and 6 both
carry BOE's own 'changed-article' flag: Article 1's single, clean phrase-
substitution instruction (Council of Ministers Resolution 57, 20/1/1442H) is
ingested in place of BOE's own stale main body; Article 6's TWO layered but
individually clean and complete quoted replacement texts (Royal Decree M/60,
28/12/1425H, then Council of Ministers Resolution 388, 14/7/1443H) are
resolved by ingesting the MOST RECENT complete quote (Resolution 388), not a
hand-merged guess -- independently corroborated by the Saudi Council of
Engineers' own official website (saudieng.sa). This validator does not
attempt to re-adjudicate any of this; it only checks internal self-
consistency of the text this track actually ingests, and that every
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
SRC = os.path.join(ROOT, "sources", "saudi_engineers", "law", "official_source",
                   "saudi_engineers_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "saudi_engineers", "law", "verified",
                       "saudi_engineers_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "saudi_engineers", "law", "verified",
                       "saudi_engineers_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "saudi_engineers_arabic_legal_llm",
                   "saudi_engineers_law_legal_llm_001_009.json")
N = 9
KEY_RE = r"saudi_engineers_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 7, "معدلة": 2, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat law -- no أبواب/فصول, single leaf range 1-9

STATUS_UNCHANGED = ("BOE_WAYBACK_ARCHIVE_THREE_TIMEPOINT_NOV2019_DEC2022_SEP2025_TEXT_STABLE_X_"
                     "SAUDIENG_SA_OFFICIAL_SITE_WAYBACK_THREE_TIMEPOINT_NOV2017_MAY2022_NOV2022_"
                     "CROSSCHECK_LIVE_BOE_UNREACHABLE")
STATUS_ART1 = ("BOE_CHANGELOG_COM_RESOLUTION_57_1442H_SUBSTITUTION_INCORPORATED_MAIN_BODY_STALE_X_"
               "SAUDIENG_SA_SITE_ALSO_STALE_X_AAWSAT_PRESS_CROSSCHECK_SUPERVISING_MINISTRY_TRANSFER_"
               "LIVE_BOE_UNREACHABLE")
STATUS_ART6 = ("BOE_CHANGELOG_COM_RESOLUTION_388_1443H_LATEST_FULL_QUOTE_INCORPORATED_MAIN_BODY_STALE_"
               "VS_BOTH_AMENDMENTS_X_SAUDIENG_SA_OFFICIAL_SITE_MAY2022_NOV2022_CONFIRMS_SAME_TEXT_"
               "LIVE_BOE_UNREACHABLE")
EXPECTED_STATUS_BY_KEY = {
    "saudi_engineers_art_001": STATUS_ART1,
    "saudi_engineers_art_006": STATUS_ART6,
}
AMENDED_KEYS = set(EXPECTED_STATUS_BY_KEY)
ADDED_KEYS = set()
REPEALED_KEYS = set()
MUKARRAR_KEYS = set()
FLAGGED_DISCREPANCY_KEYS = {
    "saudi_engineers_gap_map_estimate_confirmed",
    "saudi_engineers_companion_practice_law_not_ingested",
    "saudi_engineers_decree_number_collision_m36",
    "saudi_engineers_article1_supervising_authority_boe_stale_vs_amended",
    "saudi_engineers_article1_typo_missing_waw",
    "saudi_engineers_article6_two_layered_amendments_both_clean",
    "saudi_engineers_boe_issuance_date_metadata_anomaly",
    "saudi_engineers_no_predecessor_found",
    "saudi_engineers_uqn_gazette_notice_unreachable",
    "saudi_engineers_implementing_regs_charter_not_ingested",
    "saudi_engineers_no_baab_fasl_structure",
    "saudi_engineers_no_inline_article_titles",
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

    if len(arts.get("saudi_engineers_art_001", {}).get("history", [])) != 1:
        e.append("[2j] Article 1 must record exactly 1 amendment history entry")
    if len(arts.get("saudi_engineers_art_006", {}).get("history", [])) != 2:
        e.append("[2j] Article 6 must record exactly 2 amendment history entries")

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
        e.append("[2k] missing amendment_history (must record M/36, M/60, 57, and 388)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        for token in ("م/36", "م/60", "57", "388"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference %s" % token)

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("saudi_engineers_art_001", {})
    if "الهيئة السعودية للمهندسين" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected الهيئة definition")
    if "الجهة التي يصدر بتحديدها أمر من رئيس مجلس الوزراء" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected amended supervising-entity clause")
    if "وزارة التجارة" in art1.get("text", ""):
        e.append("[2j] Article 1 unexpectedly still contains stale Ministry-of-Commerce wording")
    art2 = arts.get("saudi_engineers_art_002", {})
    if "شروط الترخيص" not in art2.get("text", ""):
        e.append("[2j] Article 2 missing expected licensing-conditions clause")
    art3 = arts.get("saudi_engineers_art_003", {})
    if "عضوية أساسية" not in art3.get("text", ""):
        e.append("[2j] Article 3 missing expected membership-category clause")
    art6 = arts.get("saudi_engineers_art_006", {})
    if "عشرة أعضاء" not in art6.get("text", ""):
        e.append("[2j] Article 6 missing expected 10-member board clause")
    if "الأعضاء الأساسيون الذين تنتخبهم الجمعية العمومية" not in art6.get("text", ""):
        e.append("[2j] Article 6 missing expected Resolution-388 elected-half clause")
    art9 = arts.get("saudi_engineers_art_009", {})
    if "الجريدة الرسمية" not in art9.get("text", ""):
        e.append("[2j] Article 9 missing expected official-gazette publication clause")
    if src.get("decree") != "المرسوم الملكي رقم (م/36)" or src.get("decree_date_hijri") != "26/9/1423":
        e.append("[2j] decree/decree_date_hijri mismatch with verified M/36, 26/9/1423H")

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
        print("FAIL: %d error(s) in Saudi Engineers Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Law of the Saudi Council of Engineers")
    print("  - 9 records: 7 اصلية, 2 معدلة (Articles 1, 6), 0 ملغاة, 0 مضافة")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-9); no")
    print("    inline per-article titles in the BOE source (no title_ar key used)")
    print("  - VERIFICATION TIER: BOE-via-Wayback-Machine, THREE snapshots spanning")
    print("    15 Nov 2019 - 15 Sep 2025, x the Saudi Council of Engineers' own")
    print("    official website (saudieng.sa, three snapshots 2017-2022), x an")
    print("    Asharq Al-Awsat press aggregation for Article 1's supervising-")
    print("    authority transfer")
    print("  - Royal Decree M/36 (26/9/1423H / 1 Dec 2002G), Council of Ministers")
    print("    Resolution 226 (13/9/1423H); no predecessor engineering-council law")
    print("    found (confirmed negative finding)")
    print("  - MAJOR VERIFIED ANOMALY carried forward (Article 1): BOE's own page logs")
    print("    a single clean phrase-substitution (CoM Resolution 57, 20/1/1442H,")
    print("    supervising-entity transfer) but its own main body AND the Council's")
    print("    own official website both remain stale (Ministry of Commerce wording)")
    print("    across every snapshot checked -- this track ingests the changelog-")
    print("    instructed substitution and flags the staleness explicitly")
    print("  - MAJOR VERIFIED ANOMALY carried forward (Article 6): BOE's own page logs")
    print("    TWO layered but individually clean, complete-quote amendments (Royal")
    print("    Decree M/60, 1425H, then CoM Resolution 388, 1443H) -- this track")
    print("    ingests the more recent complete quote (Resolution 388), independently")
    print("    confirmed by the Council's own official website; BOE's own main body")
    print("    remains stuck on the original 2002 text throughout")
    print("  - A separate, currently-in-force companion law (نظام مزاولة المهن")
    print("    الهندسية, Royal Decree M/36 dated 19/4/1438H -- a DIFFERENT decree")
    print("    despite the identical number) governing licensing/discipline was")
    print("    identified but NOT ingested this pass (one-law-per-pass precedent)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
