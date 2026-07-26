#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Public Prosecution Law track (30 records: 12
اصلية, 16 معدلة, 2 ملغاة [Arts. 11, 28], 0 مضافة; flat structure, no باب/فصل
subdivision).

VERIFICATION TIER -- see the generator's module docstring and
sources/public_prosecution_law/law/official_source/
public_prosecution_law_official_source.json's verification_methodology_note for
the full account: laws.boe.gov.sa's LIVE portal was unreachable this pass; a
SINGLE Wayback Machine snapshot (20260215023949, 15 Feb 2026) was used as
PRIMARY source, cross-verified against nezams.com (byte-level, for the 1409H/
M4/M31/M180 layers) and qanoonsa.com (independent official-decree mirror for
M/180). This validator does not re-adjudicate any of this; it only checks
internal self-consistency of the text this track actually ingests, and that
every discrepancy (including the three current_wording_fully_confirmed=false
articles) is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "public_prosecution_law", "law", "official_source",
                   "public_prosecution_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "public_prosecution_law", "law", "verified",
                       "public_prosecution_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "public_prosecution_law", "law", "verified",
                       "public_prosecution_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "public_prosecution_law_arabic_legal_llm",
                   "public_prosecution_law_legal_llm_001_030.json")
N = 30
KEY_RE = r"public_prosecution_law_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 12, "معدلة": 16, "ملغاة": 2, "مضافة": 0}

STATUS_EXPECTED = "BOE_WAYBACK_PRIMARY_ARCHIVE_SINGLE_SNAPSHOT_X_NEZAMS_HTML_BYTE_CROSSCHECK_X_QANOONSA_OFFICIAL_DECREE_MIRROR_LIVE_BOE_UNREACHABLE"
AMENDED_KEYS = {"public_prosecution_law_art_%03d" % n for n in
                (1, 2, 3, 4, 5, 9, 10, 12, 13, 15, 16, 17, 24, 25, 26, 27)}
REPEALED_KEYS = {"public_prosecution_law_art_011", "public_prosecution_law_art_028"}
ADDED_KEYS = set()
UNCONFIRMED_KEYS = {"public_prosecution_law_art_003", "public_prosecution_law_art_004",
                    "public_prosecution_law_art_016"}
FLAGGED_DISCREPANCY_KEYS = {
    "public_prosecution_law_m125_new_amendment_wave_not_in_task_brief",
    "public_prosecution_law_art_003_m125_wording_unconfirmed",
    "public_prosecution_law_art_004_m125_paras_2_3_wording_unconfirmed",
    "public_prosecution_law_art_016_m125_wording_wholly_unconfirmed",
    "public_prosecution_law_a240_rename_order_not_a_boe_article_amendment",
    "public_prosecution_law_no_formal_chapter_structure",
    "public_prosecution_law_annex_payscale_and_equivalence_table_not_ingested",
    "public_prosecution_law_boe_live_unreachable_wayback_single_snapshot",
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

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != STATUS_EXPECTED:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS_EXPECTED, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if a.get("section_ar", "") != "":
            e.append("[2] %s: expected empty section_ar (flat, no باب/فصل structure)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if k in (AMENDED_KEYS | REPEALED_KEYS) and not a.get("original_1409h_text"):
            e.append("[2] %s: amended/repealed article missing original_1409h_text" % k)
        if k in (AMENDED_KEYS | REPEALED_KEYS) and not a.get("history"):
            e.append("[2] %s: amended/repealed article missing amendment_history" % k)
        confirmed = a.get("current_wording_fully_confirmed", True)
        if (k in UNCONFIRMED_KEYS) and confirmed:
            e.append("[2f] %s: expected current_wording_fully_confirmed=false" % k)
        if (k not in UNCONFIRMED_KEYS) and not confirmed:
            e.append("[2f] %s: unexpected current_wording_fully_confirmed=false" % k)
        if "\xa0" in a["text"]:
            e.append("[2g] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2g] %s: residual curly-quote artifact detected" % k)

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
        e.append("[2k] missing amendment_history")
    else:
        decrees = " ".join(h.get("decree", "") for h in src["amendment_history"])
        for must in ("م/56", "م/4", "م/31", "أ/240", "م/125", "م/180"):
            if must not in decrees:
                e.append("[2k] amendment_history must reference %s" % must)

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("public_prosecution_law_art_001", {})
    if "النيابة العامة جزء من السلطة القضائية" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected current (post-M/125) definition")
    art11 = arts.get("public_prosecution_law_art_011", {})
    if art11.get("legal_status_ar") != "ملغاة":
        e.append("[2j] Article 11 expected ملغاة (repealed by M/125)")
    art28 = arts.get("public_prosecution_law_art_028", {})
    if art28.get("legal_status_ar") != "ملغاة":
        e.append("[2j] Article 28 expected ملغاة (repealed by M/125)")
    art4 = arts.get("public_prosecution_law_art_004", {})
    if "مجلس النيابة العامة" not in " ".join(str(h.get("text", "")) for h in art4.get("history", [])):
        e.append("[2j] Article 4 history missing confirmed M/180 مجلس النيابة العامة wording")
    if src.get("decree") != "المرسوم الملكي رقم (م/56)" or src.get("decree_date_hijri") != "24/10/1409":
        e.append("[2j] decree/decree_date_hijri mismatch with verified M/56, 24/10/1409H")

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
        if r.get("current_wording_fully_confirmed") != a.get("current_wording_fully_confirmed", True):
            e.append("[4] %s: current_wording_fully_confirmed mismatch" % r["article_key"])
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
        if r.get("source_trust", {}).get("source_status") != a["status"].lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Public Prosecution Law track:" % len(e))
        for x in e[:60]:
            print("  - %s" % x)
        return 1
    print("PASS: Public Prosecution Law (نظام النيابة العامة)")
    print("  - 30 records: 12 اصلية, 16 معدلة, 2 ملغاة (Arts. 11, 28), 0 مضافة")
    print("  - flat structure, no باب/فصل subdivision (section_ar empty for every article)")
    print("  - VERIFICATION TIER: BOE-via-Wayback-Machine SINGLE snapshot (15 Feb 2026),")
    print("    live BOE unreachable this pass, x nezams.com byte-level crosscheck x")
    print("    qanoonsa.com independent official-decree mirror (M/180)")
    print("  - Royal Decree M/56 (24/10/1409H); amended by M/4 (1433H), M/31 (1436H),")
    print("    renamed via Royal Order A/240 (1438H), amended by M/125 (1441H -- a wide")
    print("    wave NOT in this task's initial brief, discovered this pass, incl. 2")
    print("    repeals), and M/180 (1446H, Art. 4 para. 1 only)")
    print("  - 3 articles (3, 4, 16) flagged current_wording_fully_confirmed=false --")
    print("    BOE confirms an M/125 amendment occurred but does not quote the result,")
    print("    and nezams.com is silent on M/125 entirely; text kept at last fully")
    print("    confirmed verbatim snapshot, gap disclosed rather than guessed at")
    return 0


if __name__ == "__main__":
    sys.exit(main())
