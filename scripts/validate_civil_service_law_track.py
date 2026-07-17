#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Civil Service Law track (44 records: 20
اصلية / 19 معدلة / 1 ملغاة / 4 مضافة, 3 أبواب with الباب الثاني further
divided into 6 فصول).

VERIFICATION TIER — see the generator's module docstring and
sources/civil_service/law/official_source/
civil_service_law_official_source.json's verification_methodology_note
for the full caveat. laws.boe.gov.sa's live portal was unreachable this
research pass; full text rests on a Wayback Machine snapshot of the BOE
portal, cross-verified article-by-article (100% of all 44 article-entries)
against a direct fetch of nezams.com. This validator checks internal
consistency and that every documented amendment/repeal/addition carries
the expected status/history/discrepancy documentation; it CANNOT re-fetch
the primary source itself."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "civil_service", "law", "official_source",
                   "civil_service_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "civil_service", "law", "verified",
                       "civil_service_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "civil_service_arabic_legal_llm",
                   "civil_service_law_legal_llm_001_044.json")
N = 44
KEY_RE = r"civil_service_art_(\d{3})(_mukarrar)?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 20, "معدلة": 19, "ملغاة": 1, "مضافة": 4}
STATUS = "BOE_WAYBACK_X_NEZAMS_FULL_CROSS_VERIFIED"
MUKARRAR_KEYS = {"civil_service_art_015_mukarrar", "civil_service_art_025_mukarrar",
                 "civil_service_art_036_mukarrar", "civil_service_art_037_mukarrar"}
REPEALED_KEYS = {"civil_service_art_003"}
AMENDED_NUMBERS = {2, 4, 6, 7, 14, 17, 18, 19, 20, 21, 22, 24, 25, 29, 30, 35, 36, 37, 39}
ORIGINAL_TEXT_KEYS = {"civil_service_art_%03d" % n for n in AMENDED_NUMBERS}
FLAGGED_DISCREPANCY_KEYS = {
    "civil_service_boe_citation_gaps",
    "civil_service_art_025",
    "civil_service_art_025_duplicate_history_entry",
    "civil_service_stale_ministry_name",
    "civil_service_publication_date_discrepancy",
    "civil_service_art_011_spelling_variant",
    "civil_service_art_024_duplication_typo",
    "civil_service_m139_date_sequencing",
    "civil_service_companion_instruments_out_of_scope",
    "civil_service_unverified_1446h_amendment_claim",
    "civil_service_implementing_regulation_not_extracted",
}
EXPECTED_CHAPTERS = 3
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
    for p in (SRC, RECORDS, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)
    for k in MUKARRAR_KEYS:
        if k not in arts:
            e.append("[1] expected article key %s missing" % k)
    for k in REPEALED_KEYS:
        if k not in arts:
            e.append("[1] expected repealed article key %s missing" % k)

    chapters = src.get("chapter_structure") or []
    if len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d chapters, got %d" % (EXPECTED_CHAPTERS, len(chapters)))
    # الباب الثاني must carry 6 نص فصول
    bab2 = next((c for c in chapters if c.get("label_ar") == "الباب الثاني"), None)
    if not bab2 or len(bab2.get("sections") or []) != 6:
        e.append("[1c] expected الباب الثاني to have 6 فصول sub-sections")

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
            e.append("[2] %s: missing section_ar (expected a باب/فصل title)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if "‌" in a["text"] or "￼" in a["text"]:
            e.append("[2] %s: stray ZWNJ/object-replacement character present" % k)

        if k in MUKARRAR_KEYS:
            if not a.get("is_mukarrar"):
                e.append("[2] %s: expected is_mukarrar true" % k)
            if ls != "مضافة":
                e.append("[2] %s: expected legal_status_ar مضافة, got %r" % (k, ls))
        elif a.get("is_mukarrar"):
            e.append("[2] %s: unexpected is_mukarrar true outside MUKARRAR_KEYS" % k)

        if k in REPEALED_KEYS:
            if ls != "ملغاة":
                e.append("[2] %s: expected legal_status_ar ملغاة, got %r" % (k, ls))
            if not a["text"].strip():
                e.append("[2] %s: repealed article must preserve pre-repeal text" % k)
            if not a.get("history"):
                e.append("[2] %s: repealed article missing history documenting the repeal" % k)

        m = re.match(KEY_RE, k)
        if m and not m.group(2) and k not in REPEALED_KEYS:
            n = int(m.group(1))
            if n in AMENDED_NUMBERS:
                if ls != "معدلة":
                    e.append("[2] %s: expected معدلة (amended-list article), got %r" % (k, ls))
                if not a.get("history"):
                    e.append("[2] %s: amended article missing history" % k)
            else:
                if ls != "اصلية":
                    e.append("[2] %s: expected اصلية (not in amended/repealed list), got %r" % (k, ls))

        if k in ORIGINAL_TEXT_KEYS:
            if not (a.get("original_1397h_text") or "").strip():
                e.append("[2] %s: expected original_1397h_text to be populated" % k)
        else:
            if a.get("original_1397h_text"):
                e.append("[2] %s: unexpected original_1397h_text (not in the confirmed-recovered set)" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sum(sc.values()) != N:
        e.append("[2] status_counts sum %d != %d" % (sum(sc.values()), N))

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

    # article_count / status_counts declared at top level must match reality
    if src.get("article_count") != N:
        e.append("[2f] declared article_count %r != %d" % (src.get("article_count"), N))
    for st in ALLOWED_STATUS:
        if src.get("status_counts", {}).get(st) != sc.get(st):
            e.append("[2f] declared status_counts[%s] does not match actual per-article counts" % st)

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("original_1397h_text") != a.get("original_1397h_text"):
            e.append("[4] %s: original_1397h_text mismatch" % r["article_key"])
        if r.get("is_repealed") != (a.get("legal_status_ar") == "ملغاة"):
            e.append("[4] %s: is_repealed mismatch" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        a = arts[r["article_key"]]
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r.get("original_1397h_text") != a.get("original_1397h_text"):
            e.append("[5] %s: llm original_1397h_text mismatch" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Civil Service Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Civil Service Law — 44 records (20 اصلية / 19 معدلة / 1 ملغاة / 4 مضافة, 3 أبواب)")
    print("  - VERIFICATION TIER: Wayback Machine snapshot of BOE portal, cross-verified")
    print("    article-by-article (100% of all 44 article-entries) against nezams.com; the")
    print("    M/139 six-article package additionally corroborated via SPA/Okaz news coverage")
    print("  - Article 3 (ملغاة): repealed via Royal Decree M/95 (15/9/1439H), no replacement")
    print("    text; pre-repeal 1397H text preserved")
    print("  - 4 مضافة مكرر articles: 15 مكرر, 25 مكرر, 36 مكرر (all M/95, 15/9/1439H),")
    print("    37 مكرر (M/57, 24/5/1438H)")
    print("  - 19 معدلة articles carry full history; original_1397h_text preserved for all 19")
    print("    (Articles 20, 29, 35 each amended twice — first amendment recorded in history only)")
    print("  - IN-FORCE Royal Decree M/49 (10/7/1397H)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
