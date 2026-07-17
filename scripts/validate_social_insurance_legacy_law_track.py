#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Social Insurance Law (Old/Legacy System)
track (71 records: 63 اصلية / 7 معدلة / 0 ملغاة / 1 مضافة, 7 فصول with
الفصل الخامس further divided into 4 أقسام).

SCOPE NOTE — this validates the OLD Social Insurance Law (Royal Decree
M/33, 3/9/1421H) only. It is a separate track from the NEW Social Insurance
Law (M/273, 26/12/1445H), which shares the identical Arabic title but is a
different, differently-numbered/dated instrument covering a different
population — see known_unresolved_discrepancies in the source JSON for the
documented naming collision.

VERIFICATION TIER — see the generator's module docstring and
sources/social_insurance_legacy/law/official_source/
social_insurance_legacy_law_official_source.json's verification_methodology_note
for the full caveat. Full article text rests on a Wayback Machine BOE
archive snapshot (2026-02-09), cross-verified (20+ of 71 articles, plus
100% of the nine changed-article amendment-history popups) against
nezams.com, with Articles 10 and 37 additionally reconciled against BOE's
own stale default rendering (Article 37's reconciled text further
corroborated via independent Okaz/Al-Riyadh news coverage). This validator
checks internal consistency and that every documented amendment/addition
carries the expected status/history/discrepancy documentation; it CANNOT
re-fetch the primary source itself."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "social_insurance_legacy", "law", "official_source",
                   "social_insurance_legacy_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "social_insurance_legacy", "law", "verified",
                       "social_insurance_legacy_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "social_insurance_legacy_arabic_legal_llm",
                   "social_insurance_legacy_law_legal_llm_001_071.json")
N = 71
KEY_RE = r"social_insurance_legacy_art_(\d{3})(_mukarrar)?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 63, "معدلة": 7, "ملغاة": 0, "مضافة": 1}
STATUS = "BOE_WAYBACK_X_NEZAMS_SPOTCHECK_X_OKAZ_ALRIYADH_CORROBORATED"
MUKARRAR_KEYS = {"social_insurance_legacy_art_058_mukarrar"}
REPEALED_KEYS = set()
AMENDED_NUMBERS = {2, 10, 37, 38, 41, 43, 62}
ORIGINAL_TEXT_KEYS = {"social_insurance_legacy_art_%03d" % n for n in AMENDED_NUMBERS}
FLAGGED_DISCREPANCY_KEYS = {
    "social_insurance_legacy_dual_law_title_collision",
    "social_insurance_legacy_boe_wayback_nezams_verification_tier",
    "social_insurance_legacy_art_038_transitional_age_not_merged",
    "social_insurance_legacy_art_010_resolution_sequencing",
    "social_insurance_legacy_art_010_gosi_site_8member_unresolved",
    "social_insurance_legacy_art_041_instrument_type_discrepancy",
    "social_insurance_legacy_art_058_duplicate_amendment_popup",
    "social_insurance_legacy_implementing_regulation_not_extracted",
}
EXPECTED_CHAPTERS = 7
EXPECTED_SUB_SECTIONS = {"الفصل الخامس": 4}
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
    for ch in chapters:
        label = ch.get("label_ar")
        n_sections = len(ch.get("sections") or [])
        expected = EXPECTED_SUB_SECTIONS.get(label, 0)
        if n_sections != expected:
            e.append("[1c] %s: expected %d nested قسم sections, got %d" % (label, expected, n_sections))

    if not src.get("preamble_ar", "").strip():
        e.append("[1d] missing/empty preamble_ar")
    if not src.get("decree_transitional_provisions_ar", "").strip():
        e.append("[1d] missing/empty decree_transitional_provisions_ar")

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != "اصلية":
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (expected a فصل/قسم title)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if "‌" in a["text"] or "￼" in a["text"]:
            e.append("[2] %s: stray ZWNJ/object-replacement character present" % k)

        if k in MUKARRAR_KEYS:
            if not a.get("is_mukarrar"):
                e.append("[2] %s: expected is_mukarrar true" % k)
            if ls != "مضافة":
                e.append("[2] %s: expected legal_status_ar مضافة, got %r" % (k, ls))
            if not a.get("history"):
                e.append("[2] %s: added مكرر article missing history" % k)
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
                    e.append("[2] %s: expected اصلية (not in amended/repealed/added list), got %r" % (k, ls))

        if k in ORIGINAL_TEXT_KEYS:
            if not (a.get("original_1421h_text") or "").strip():
                e.append("[2] %s: expected original_1421h_text to be populated" % k)
        else:
            if a.get("original_1421h_text"):
                e.append("[2] %s: unexpected original_1421h_text (not in the confirmed-recovered set)" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))
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
        if src.get("status_counts", {}).get(st) != sc.get(st, 0):
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
        if r.get("original_1421h_text") != a.get("original_1421h_text"):
            e.append("[4] %s: original_1421h_text mismatch" % r["article_key"])
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
        if r.get("original_1421h_text") != a.get("original_1421h_text"):
            e.append("[5] %s: llm original_1421h_text mismatch" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Social Insurance Law (Old/Legacy System) track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Social Insurance Law (Old/Legacy System) — 71 records (63 اصلية, 7 معدلة, 0 ملغاة,")
    print("  1 مضافة, 7 فصول with الفصل الخامس split into 4 أقسام)")
    print("  - VERIFICATION TIER: BOE Wayback archive (2026-02-09) direct fetch, cross-verified")
    print("    (20+ of 71 articles, plus 100% of the nine changed-article amendment popups)")
    print("    against nezams.com; Article 37's reconciled text additionally corroborated via")
    print("    independent Okaz/Al-Riyadh news coverage")
    print("  - Dual-law title collision with NEW Social Insurance Law (M/273, 26/12/1445H)")
    print("    documented, not merged into this track")
    print("  - Article 10 (board composition) and Article 37 (remains transport) both resolved")
    print("    to their current reconciled text over BOE's stale default rendering")
    print("  - Article 38: no 2024 transitional retirement-age text merged in; that override")
    print("    lives in the NEW law's own promulgating Royal Decree, documented separately")
    print("  - IN-FORCE Royal Decree M/33 (3/9/1421H) for pre-1/7/2025 subscribers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
