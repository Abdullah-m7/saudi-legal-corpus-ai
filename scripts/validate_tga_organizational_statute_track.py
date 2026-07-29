#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Organizing Statute of the General Authority
for Transport (TGA) track (16 records: 7 اصلية, 8 معدلة, 0 ملغاة, 1 مضافة
[Article 13bis]; flat structure -- NO أبواب/فصول grouping).

VERIFICATION TIER -- see the generator's module docstring and
sources/tga_organizational_statute/law/official_source/
tga_organizational_statute_official_source.json's verification_methodology_
note for the full account: laws.boe.gov.sa's LIVE portal returned a TLS
connection reset (curl) / HTTP 503 (WebFetch) on every attempt this pass;
this track instead rests on two independent Wayback Machine snapshots of
BOE's own LawDetails page, cross-checked against nezams.com, and -- for one
confirmed BOE-stale article (6) -- an independent Wayback capture of
uqn.gov.sa's own Umm Al-Qura Gazette page. This validator does not attempt
to re-adjudicate any of this; it only checks internal self-consistency of
the text this track actually ingests, and that every discrepancy is still
recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "tga_organizational_statute", "law", "official_source",
                   "tga_organizational_statute_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "tga_organizational_statute", "law", "verified",
                       "tga_organizational_statute_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "tga_organizational_statute", "law", "verified",
                       "tga_organizational_statute_verified_summary.json")
LLM = os.path.join(ROOT, "data", "tga_organizational_statute_arabic_legal_llm",
                   "tga_organizational_statute_legal_llm_001_016.json")
N = 16
BASE_ARTICLE_COUNT = 15  # articles 1-15 excluding the 13bis mukarrar addition
KEY_RE = r"tga_organizational_statute_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 7, "معدلة": 8, "ملغاة": 0, "مضافة": 1}
EXPECTED_TOP_LEVEL_CHAPTERS = 1  # flat law -- no أبواب/فصول, single leaf range 1-15

STATUS_UNCHANGED = "BOE_WAYBACK_DUAL_SNAPSHOT_DEC2024_JUL2025_X_NEZAMS_COM_TRIPLE_CROSS_VERIFIED_LIVE_BOE_TLS_RESET_THIS_PASS"
STATUS_ART1 = "BOE_WAYBACK_DUAL_SNAPSHOT_DEC2024_JUL2025_X_NEZAMS_COM_BASE_TEXT_CROSS_VERIFIED_LIVE_BOE_TLS_RESET_THIS_PASS"
STATUS_ART2 = "BOE_WAYBACK_DUAL_SNAPSHOT_DEC2024_JUL2025_SELF_CONSISTENT_LIVE_BOE_TLS_RESET_THIS_PASS"
STATUS_ART3 = "BOE_WAYBACK_DUAL_SNAPSHOT_DEC2024_JUL2025_X_NEZAMS_COM_TRIPLE_CROSS_VERIFIED_LIVE_BOE_TLS_RESET_THIS_PASS"
STATUS_ART4 = "BOE_WAYBACK_DUAL_SNAPSHOT_DEC2024_JUL2025_X_NEZAMS_COM_VERBATIM_MATCH_RESOLUTION_248_FULL_SUBSTITUTION_LIVE_BOE_TLS_RESET_THIS_PASS"
STATUS_ART5 = "BOE_WAYBACK_POPUP_VERBATIM_RESOLUTION_586_FULL_SUBSTITUTION_FOR_PARAGRAPH_1_X_NEZAMS_COM_FOR_UNCHANGED_PARAGRAPHS_2_3_ONLY_RESOLUTION_382_OR_386_1446H_ENERGY_MINISTRY_SEAT_CONFIRMED_TO_EXIST_BUT_NOT_TEXTUALLY_INCORPORATED"
STATUS_ART6 = "UQN_GOV_SA_WAYBACK_PRIMARY_GAZETTE_CAPTURE_VERBATIM_X_NEZAMS_COM_CROSS_VERIFIED_BOE_OWN_PAGE_CONFIRMED_STALE_NO_POPUP_FOR_THIS_ARTICLE"
STATUS_ART7 = "BOE_WAYBACK_DUAL_SNAPSHOT_DEC2024_JUL2025_POPUP_VERBATIM_RESOLUTION_586_PARTIAL_SUBSTITUTION_LIVE_BOE_TLS_RESET_THIS_PASS"
STATUS_ART9 = STATUS_ART2
STATUS_ART13 = "BOE_WAYBACK_DUAL_SNAPSHOT_DEC2024_JUL2025_POPUP_VERBATIM_RESOLUTION_631_ADDED_PARAGRAPH_TYPO_PRESERVED_LIVE_BOE_TLS_RESET_THIS_PASS"
STATUS_ART13BIS = "BOE_WAYBACK_DUAL_SNAPSHOT_DEC2024_JUL2025_POPUP_VERBATIM_RESOLUTION_631_NEW_ARTICLE_LIVE_BOE_TLS_RESET_THIS_PASS"
EXPECTED_STATUS_BY_KEY = {
    "tga_organizational_statute_art_001": STATUS_ART1,
    "tga_organizational_statute_art_002": STATUS_ART2,
    "tga_organizational_statute_art_003": STATUS_ART3,
    "tga_organizational_statute_art_004": STATUS_ART4,
    "tga_organizational_statute_art_005": STATUS_ART5,
    "tga_organizational_statute_art_006": STATUS_ART6,
    "tga_organizational_statute_art_007": STATUS_ART7,
    "tga_organizational_statute_art_009": STATUS_ART9,
    "tga_organizational_statute_art_013": STATUS_ART13,
    "tga_organizational_statute_art_013_mukarrar": STATUS_ART13BIS,
}
AMENDED_KEYS = {
    "tga_organizational_statute_art_001", "tga_organizational_statute_art_002",
    "tga_organizational_statute_art_004", "tga_organizational_statute_art_005",
    "tga_organizational_statute_art_006", "tga_organizational_statute_art_007",
    "tga_organizational_statute_art_009", "tga_organizational_statute_art_013",
}
ADDED_KEYS = {"tga_organizational_statute_art_013_mukarrar"}
REPEALED_KEYS = set()
MUKARRAR_KEYS = {"tga_organizational_statute_art_013_mukarrar"}
FLAGGED_DISCREPANCY_KEYS = {
    "tga_boe_stale_no_popup_for_article_6",
    "tga_article5_energy_ministry_decree_number_unresolved_382_vs_386",
    "tga_article5_energy_ministry_resulting_text_not_available",
    "tga_article5_paragraphs_2_3_single_secondary_sourced",
    "tga_631_phrase_and_name_substitution_not_executed_in_boe_text",
    "tga_article13_diwan_typo_preserved",
    "tga_article1_wazir_reinsertion_position_unspecified",
    "tga_no_named_predecessor_for_public_transport_authority_itself",
    "tga_qistas_631_preview_paywalled_not_used_for_new_text",
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
    key), so this is a flat single-level walk over the 15 base articles
    (the 13bis mukarrar addition is not part of the numeric range walk)."""
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
    if covered != set(range(1, BASE_ARTICLE_COUNT + 1)):
        missing = sorted(set(range(1, BASE_ARTICLE_COUNT + 1)) - covered)
        extra = sorted(covered - set(range(1, BASE_ARTICLE_COUNT + 1)))
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
        if k in (AMENDED_KEYS | ADDED_KEYS) and not a.get("history"):
            e.append("[2] %s: amended/added article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present (source supplies no "
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

    if len(arts.get("tga_organizational_statute_art_005", {}).get("history", [])) != 5:
        e.append("[2j] Article 5 must record exactly 5 amendment history entries "
                 "(248, 707, 631, 586, 382-or-386)")
    if len(arts.get("tga_organizational_statute_art_001", {}).get("history", [])) != 3:
        e.append("[2j] Article 1 must record exactly 3 amendment history entries "
                 "(248, 707, 631)")

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
        e.append("[2k] missing amendment_history (must record 323, 248, 707, 631, 12, 586)")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        for token in ("323", "248", "707", "631", "12", "586"):
            if token not in decrees:
                e.append("[2k] amendment_history must reference %s" % token)

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("tga_organizational_statute_art_001", {})
    if "الوزير: وزير النقل" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected restored الوزير definition (Resolution 631)")
    if "هيئة النقل العام" not in art1.get("text", ""):
        e.append("[2j] Article 1 unexpectedly missing stale الهيئة definition -- see "
                 "tga_631_phrase_and_name_substitution_not_executed_in_boe_text")
    art4 = arts.get("tga_organizational_statute_art_004", {})
    if "24 - القيام بأي مهمة أخرى" not in art4.get("text", ""):
        e.append("[2j] Article 4 missing expected 24-item Resolution 248 full substitution")
    art5 = arts.get("tga_organizational_statute_art_005", {})
    if "ك- ثلاثة من القطاع الخاص" not in art5.get("text", ""):
        e.append("[2j] Article 5 missing expected Resolution 586 10-member board text")
    if "وزارة الطاقة" in art5.get("text", ""):
        e.append("[2j] Article 5 unexpectedly contains an Energy Ministry seat in its 'text' "
                 "field -- this amendment's resulting order was NOT confirmed and must remain "
                 "unspliced (see known_unresolved_discrepancies)")
    art6 = arts.get("tga_organizational_statute_art_006", {})
    if "4 - اعتماد الهيكل التنظيمي للهيئة" not in art6.get("text", ""):
        e.append("[2j] Article 6 missing expected Resolution 12 paragraph-4 substitution "
                 "(confirmed via uqn.gov.sa primary Gazette capture)")
    art7 = arts.get("tga_organizational_statute_art_007", {})
    if "من ينيبه من ممثلي الجهات الحكومية الأعضاء في المجلس" not in art7.get("text", ""):
        e.append("[2j] Article 7 missing expected Resolution 586 substitution in paragraph 3")
    art13 = arts.get("tga_organizational_statute_art_013", {})
    if "ويزود دوان المراقبة العامة" not in art13.get("text", ""):
        e.append("[2j] Article 13 missing expected verbatim-preserved 'دوان' typo "
                 "(see tga_article13_diwan_typo_preserved)")
    art13bis = arts.get("tga_organizational_statute_art_013_mukarrar", {})
    if "عدا الرئيس" not in art13bis.get("text", ""):
        e.append("[2j] Article 13bis missing expected staff labor-law exception clause")
    if src.get("decree") != "قرار مجلس الوزراء رقم (323)" or src.get("decree_date_hijri") != "14/9/1434":
        e.append("[2j] decree/decree_date_hijri mismatch with verified 323, 14/9/1434H")

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
        print("FAIL: %d error(s) in TGA Organizational Statute track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Organizing Statute of the General Authority for Transport (TGA)")
    print("  - 16 records: 7 اصلية, 8 معدلة, 0 ملغاة, 1 مضافة (Article 13bis)")
    print("  - flat structure, NO أبواب/فصول grouping (single leaf range 1-15 plus a")
    print("    13bis mukarrar addition); no inline per-article titles in the source")
    print("    (no title_ar key used)")
    print("  - VERIFICATION TIER: BOE's own portal, dual independent Wayback snapshots")
    print("    (Dec 2024, Jul 2025), cross-checked against nezams.com; live BOE portal")
    print("    TLS-reset this pass. One article (6) is confirmed BOE-stale, filled by a")
    print("    genuinely second primary source (uqn.gov.sa / Umm Al-Qura Gazette itself,")
    print("    via Wayback). One article's (5) latest amendment carries an unresolved")
    print("    decree-number conflict (382 vs 386) and its resulting text is not")
    print("    incorporated (confirmed to exist, not fabricated).")
    print("  - Council of Ministers Resolution 323 (14/9/1434H), prepared pursuant to")
    print("    Resolution 373 (15/11/1433H); no named predecessor for the Public")
    print("    Transport Authority itself, but its 2019 amendment (631) absorbed and")
    print("    repealed a genuinely separate sister authority's statute (Railway")
    print("    Authority, Resolution 1/1429H), independently confirmed via BOE's own")
    print("    'versions' table.")
    print("  - CONFIRMED CARRIED-FORWARD INCONSISTENCY: Resolution 631's own instructed")
    print("    statute-wide rename/phrase-shortening does not appear executed in BOE's")
    print("    own displayed article text -- honestly flagged, not silently harmonized")
    print("    or self-applied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
