#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Social Insurance Law (New System) track (63
records, all اصلية, 6 أبواب, with الباب الثالث split into 2 نested فصول).

SCOPE NOTE — this validates the NEW Social Insurance Law (Royal Decree
M/273, 26/12/1445H) only. It is a separate track from the OLD Social
Insurance Law (M/33, 3/9/1421H), which shares the identical Arabic title
but is a different, differently-numbered/dated instrument covering a
different population — see known_unresolved_discrepancies in the source
JSON for the documented naming collision.

DISTINCT VERIFICATION TIER — see the generator's module docstring and
sources/social_insurance/law/official_source/
social_insurance_law_official_source.json's verification_methodology_note
for the full caveat. Full article text rests on a direct fetch of a
Wayback Machine BOE archive snapshot (2025-12-12), spot-checked (5 of 63
articles) against nezams.com. This validator checks internal consistency
and that all documented discrepancies are present; it CANNOT re-fetch the
primary source itself."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "social_insurance", "law", "official_source",
                   "social_insurance_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "social_insurance", "law", "verified",
                       "social_insurance_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "social_insurance_arabic_legal_llm",
                   "social_insurance_law_legal_llm_001_063.json")
N = 63
KEY_RE = r"social_insurance_art_(\d{3})(_mukarrar)?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 63, "معدلة": 0}
STATUS = "BOE_WAYBACK_PRIMARY_X_NEZAMS_SPOTCHECK_X_QANOONSA_STRUCTURE_VERIFIED"
MUKARRAR_KEYS = set()
AMENDED_KEYS = set()
FLAGGED_DISCREPANCY_KEYS = {
    "social_insurance_dual_law_title_collision",
    "social_insurance_art_044_unemployment_rate_dual_figure",
    "social_insurance_art_016_qualifying_period_resolution_fill",
    "social_insurance_related_instruments_not_extracted",
    "social_insurance_boe_wayback_nezams_verification_tier",
    "social_insurance_art_021_boe_nezams_wording_variance",
    "social_insurance_implementing_regulation",
}
EXPECTED_CHAPTERS = 6
EXPECTED_SUB_SECTIONS = {"الباب الثالث": 2}
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

    chapters = src.get("chapter_structure") or []
    if len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d chapters, got %d" % (EXPECTED_CHAPTERS, len(chapters)))
    for ch in chapters:
        label = ch.get("label_ar")
        n_sections = len(ch.get("sections") or [])
        expected = EXPECTED_SUB_SECTIONS.get(label, 0)
        if n_sections != expected:
            e.append("[1c] %s: expected %d nested فصل sections, got %d" % (label, expected, n_sections))

    if not src.get("decree_transitional_provisions_ar", "").strip():
        e.append("[1d] missing/empty decree_transitional_provisions_ar")
    if not src.get("preamble_ar", "").strip():
        e.append("[1d] missing/empty preamble_ar")

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
            e.append("[2] %s: missing section_ar (expected a باب/chapter title)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if "‌" in a["text"] or "￼" in a["text"]:
            e.append("[2] %s: stray ZWNJ/object-replacement character present" % k)
        if k in MUKARRAR_KEYS and ls != "مضافة":
            e.append("[2] %s: expected legal_status_ar مضافة, got %r" % (k, ls))
        if k in AMENDED_KEYS:
            if ls != "معدلة":
                e.append("[2] %s: expected amended article status معدلة, got %r" % (k, ls))
            if not a.get("history"):
                e.append("[2] %s: amended article missing history" % k)
        elif ls == "معدلة":
            e.append("[2] %s: unexpected معدلة status outside AMENDED_KEYS" % k)
        if a.get("is_mukarrar") and k not in MUKARRAR_KEYS:
            e.append("[2] %s: is_mukarrar=True but not an expected مكرر article" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))
    if sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected repealed/added articles present")

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
    if src.get("status_counts", {}).get("اصلية") != sc.get("اصلية", 0) or \
            src.get("status_counts", {}).get("معدلة") != sc.get("معدلة", 0):
        e.append("[2f] declared status_counts does not match actual per-article counts")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
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
        print("FAIL: %d error(s) in Social Insurance Law (New System) track:" % len(e))
        for x in e[:25]:
            print("  - %s" % x)
        return 1
    print("PASS: Social Insurance Law (New System) — 63 records (63 اصلية, 6 أبواب)")
    print("  - DISTINCT TIER: BOE Wayback archive (2025-12-12) direct fetch, spot-checked (5 of 63")
    print("    articles) against nezams.com; structural (63-article/6-chapter) cross-check via")
    print("    nezams.com index and a prior pass's qanoonsa.com corroboration")
    print("  - Dual-law title collision with OLD Social Insurance Law (M/33, 3/9/1421H) documented,")
    print("    not merged into this track")
    print("  - Article 44 (2% statutory ceiling vs 1.5% Resolution-1022 starting rate) and Article 16")
    print("    (qualifying period filled in by Resolution 1022 at 180 months) both flagged, not")
    print("    silently resolved to a single figure")
    print("  - IN-FORCE Royal Decree M/273 (26/12/1445H), effective 1/7/2025 for new labor-market entrants")
    return 0


if __name__ == "__main__":
    sys.exit(main())
