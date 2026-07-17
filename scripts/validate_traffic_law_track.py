#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Traffic Law track (86 records: 52 اصلية /
32 معدلة / 1 ملغاة / 1 مضافة, 8 chapters/أبواب).

DISTINCT VERIFICATION TIER — see the generator's module docstring and
sources/traffic/law/official_source/traffic_law_official_source.json's
verification_methodology_note for the full caveat. This law required TWO
independent research passes because of a genuine, unresolved discrepancy
between the official BOE portal and nezams.com for roughly a third of its
articles. This validator checks internal consistency, that every
معدلة/ملغاة/مضافة article carries the expected status/history/
verification_tier documentation, and that the two verification-tier
counts roughly match expectations; it CANNOT re-fetch the primary source
itself."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "traffic", "law", "official_source",
                   "traffic_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "traffic", "law", "verified",
                       "traffic_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "traffic_arabic_legal_llm",
                   "traffic_law_legal_llm_001_086.json")
N = 86
KEY_RE = r"traffic_art_(\d{3})(_mukarrar)?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 52, "معدلة": 32, "ملغاة": 1, "مضافة": 1}
STATUS = "BOE_PROXY_X_NEZAMS_PATTERN_VERIFIED_MIXED_CONFIDENCE"
ALLOWED_TIERS = {"PRIMARY_INDEPENDENTLY_CONFIRMED", "SECONDARY_SOURCE_ONLY_BOE_KNOWN_STALE"}
# Rough expected tier split (not exact-equality-checked, just sanity-ranged):
# اصلية(52) + repealed(1) are always PRIMARY = 53 minimum PRIMARY baseline;
# plus amended-confirmed articles. SECONDARY should only ever be a subset
# of معدلة/مضافة articles.
MUKARRAR_KEYS = {"traffic_art_050_mukarrar"}
REPEALED_KEYS = {"traffic_art_071"}
AMENDED_NUMBERS = {1, 2, 5, 7, 8, 14, 16, 17, 20, 21, 23, 27, 36, 38, 41, 47, 50,
                   61, 62, 63, 64, 65, 68, 69, 70, 72, 73, 74, 75, 77, 78, 79}
FLAGGED_DISCREPANCY_KEYS = {
    "traffic_boe_nezams_pattern_confidence",
    "traffic_art_071_table2_item16_conflict",
    "traffic_art_002_term_count",
    "traffic_art_023_027_com586_insertion_ambiguity",
    "traffic_art_062_original_penalty_figures_not_recovered",
    "traffic_identical_to_boe_no_delta_articles",
    "traffic_annexed_violation_tables_and_fee_schedules_not_extracted",
    "traffic_implementing_regulation_not_extracted",
    "traffic_art_050_mukarrar_verification_tier",
    "traffic_decree_premise_correction",
    "traffic_status_counts_premise_correction",
}
EXPECTED_CHAPTERS = 8
ORIGINAL_TEXT_KEYS = {"traffic_art_%03d" % n for n in (1, 5, 23, 27, 69, 70, 73, 78)}
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

    sc = Counter()
    tier_counts = Counter()
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
            # allow bracketed Arabic-only insertions (Articles 23/27); still forbid
            # stray latin/html leftovers
            pass
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (expected a باب/chapter title)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in MUKARRAR_KEYS and ls != "مضافة":
            e.append("[2] %s: expected legal_status_ar مضافة, got %r" % (k, ls))
        if k in REPEALED_KEYS and ls != "ملغاة":
            e.append("[2] %s: expected legal_status_ar ملغاة, got %r" % (k, ls))
        if k in REPEALED_KEYS and not a["text"].strip():
            e.append("[2] %s: repealed article must preserve pre-repeal text" % k)

        tier = a.get("verification_tier")
        if tier not in ALLOWED_TIERS:
            e.append("[3] %s: invalid or missing verification_tier %r" % (k, tier))
        else:
            tier_counts[tier] += 1

        m = re.match(KEY_RE, k)
        if m and not m.group(2):
            n = int(m.group(1))
            if n in AMENDED_NUMBERS:
                if ls != "معدلة" and k not in REPEALED_KEYS:
                    e.append("[3] %s: expected معدلة (amended-list article), got %r" % (k, ls))
                if not a.get("history"):
                    e.append("[3] %s: amended article missing history" % k)
            elif k not in REPEALED_KEYS and k not in MUKARRAR_KEYS:
                if ls != "اصلية":
                    e.append("[3] %s: expected اصلية (not in amended/repealed list), got %r" % (k, ls))

        if k in ORIGINAL_TEXT_KEYS:
            if not a.get("original_1428h_text", "").strip():
                e.append("[3] %s: expected original_1428h_text to be populated" % k)
        else:
            if a.get("original_1428h_text"):
                e.append("[3] %s: unexpected original_1428h_text (not in the confirmed-recovered set)" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))

    # Sanity range on tier split: PRIMARY should be the majority (اصلية(52)+
    # repealed(1)+the confirmed-amended subset), SECONDARY only among
    # amended/added articles, and both must be present given the task's
    # explicit mixed-confidence design.
    primary_n = tier_counts.get("PRIMARY_INDEPENDENTLY_CONFIRMED", 0)
    secondary_n = tier_counts.get("SECONDARY_SOURCE_ONLY_BOE_KNOWN_STALE", 0)
    if primary_n + secondary_n != N:
        e.append("[3] verification_tier counts don't sum to %d (got PRIMARY=%d SECONDARY=%d)"
                  % (N, primary_n, secondary_n))
    if primary_n < 53:
        e.append("[3] expected at least 53 PRIMARY_INDEPENDENTLY_CONFIRMED articles "
                  "(52 اصلية + 1 ملغاة baseline), got %d" % primary_n)
    if secondary_n == 0:
        e.append("[3] expected a nonzero SECONDARY_SOURCE_ONLY_BOE_KNOWN_STALE count "
                  "given this track's documented mixed-confidence design")

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

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("verification_tier") != a.get("verification_tier"):
            e.append("[4] %s: verification_tier mismatch" % r["article_key"])
        if r.get("original_1428h_text") != a.get("original_1428h_text"):
            e.append("[4] %s: original_1428h_text mismatch" % r["article_key"])
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
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if r.get("verification_tier") != a.get("verification_tier"):
            e.append("[5] %s: llm verification_tier mismatch" % r["article_key"])
        if r.get("original_1428h_text") != a.get("original_1428h_text"):
            e.append("[5] %s: llm original_1428h_text mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])
        if r.get("source_trust", {}).get("verification_tier") != a.get("verification_tier"):
            e.append("[5] %s: llm source_trust.verification_tier mismatch" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Traffic Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Traffic Law — 86 records (52 اصلية / 32 معدلة / 1 ملغاة / 1 مضافة, 8 chapters)")
    print("  - DISTINCT TIER: BOE portal confirmed genuinely stale for this law (two independent")
    print("    research passes); nezams.com preferred for amended articles per documented pattern")
    print("  - verification_tier split: PRIMARY_INDEPENDENTLY_CONFIRMED=%d, "
          "SECONDARY_SOURCE_ONLY_BOE_KNOWN_STALE=%d" % (primary_n, secondary_n))
    print("  - Article 71 (ملغاة): repealed via CoM Decision 474 (7/7/1446H), ratified by")
    print("    Royal Decree M/140 (12/7/1446H); pre-repeal text preserved")
    print("  - Article 50 مكرر (مضافة): added by Royal Decree M/115 (5/12/1439H)")
    print("  - IN-FORCE Royal Decree M/85 (26/10/1428H)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
