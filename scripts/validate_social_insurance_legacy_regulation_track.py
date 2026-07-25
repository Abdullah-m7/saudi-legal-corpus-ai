#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulations (family) track of
the OLD/LEGACY Social Insurance Law (170 records across 5 instruments: the
umbrella ministerial decision 128/تأمينات [6 articles] + لائحة التسجيل
والاشتراكات [65] + لائحة تعويضات فرع المعاشات [42] + لائحة تعويضات فرع
الأخطار المهنية [40] + لائحة اللجان الطبية [17]; 165 اصلية / 5 معدلة / 0
ملغاة / 0 مضافة).

SCOPE NOTE -- this validates the historical regulation FAMILY companion to
the OLD Social Insurance Law (Royal Decree M/33, 3/9/1421H;
sources/social_insurance_legacy/). It is a separate track from that law
itself and from the NEW Social Insurance Law's (M/273, 26/12/1445H) own
1445H implementing regulation (a different track, built in parallel).

VERIFICATION TIER -- see the generator's module docstring and
sources/social_insurance_legacy_regulation/law/official_source/
social_insurance_legacy_regulation_official_source.json's
verification_methodology_note for the full caveat. This is a materially
LOWER verification tier than the parent law's own track: full text rests on
a single academic (KSU) .doc mirror, with only 2 of 170 articles (the
umbrella decision's own Arts. 1-2) verbatim-cross-checked against a second
independent source (qistas.com); the 4-lawiha family structure itself is
corroborated only structurally (title/decision-number/date, not full text)
via GOSI's own website and independent Saudi news coverage. This validator
checks internal consistency and that every documented gap/amendment
carries the expected status/history/discrepancy documentation; it CANNOT
re-fetch or re-verify the primary source itself."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "social_insurance_legacy_regulation", "law", "official_source",
                   "social_insurance_legacy_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "social_insurance_legacy_regulation", "law", "verified",
                       "social_insurance_legacy_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "social_insurance_legacy_regulation_arabic_legal_llm",
                   "social_insurance_legacy_regulation_legal_llm_001_170.json")
N = 170
KEY_RE = r"social_insurance_legacy_regulation_(decision|registration|annuities|occupational_hazards|medical_committees)_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 165, "معدلة": 5, "ملغاة": 0, "مضافة": 0}
STATUS = "KSU_MIRROR_X_QISTAS_PARTIAL_VERBATIM_X_MULTISOURCE_STRUCTURAL_CORROBORATION"
INSTRUMENT_ARTICLE_COUNTS = {
    "decision": 6, "registration": 65, "annuities": 42,
    "occupational_hazards": 40, "medical_committees": 17,
}
AMENDED_KEYS = {
    "social_insurance_legacy_regulation_registration_art_015",
    "social_insurance_legacy_regulation_registration_art_028",
    "social_insurance_legacy_regulation_registration_art_029",
    "social_insurance_legacy_regulation_annuities_art_042",
    "social_insurance_legacy_regulation_occupational_hazards_art_040",
}
FLAGGED_DISCREPANCY_KEYS = {
    "social_insurance_legacy_regulation_is_legacy_not_new",
    "social_insurance_legacy_regulation_family_not_single_instrument",
    "social_insurance_legacy_regulation_single_mirror_source_tier",
    "social_insurance_legacy_regulation_edition_currency_gap",
    "social_insurance_legacy_regulation_registration_bab2_heading_missing",
    "social_insurance_legacy_regulation_colophon_amendment_list_incomplete",
    "social_insurance_legacy_regulation_decision_date_colophon_mismatch",
    "social_insurance_legacy_regulation_occupational_diseases_table_not_captured",
    "social_insurance_legacy_regulation_footnote_amendments_partial",
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
    for p in (SRC, RECORDS, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    per_instrument = Counter()
    for k, a in arts.items():
        m = re.match(KEY_RE, k)
        if not m:
            e.append("[1] %s: does not match key pattern" % k)
            continue
        instrument = m.group(1)
        per_instrument[instrument] += 1
        if a.get("instrument") != instrument:
            e.append("[1] %s: instrument field %r != key-derived %r" % (k, a.get("instrument"), instrument))
    for instrument, want in INSTRUMENT_ARTICLE_COUNTS.items():
        if per_instrument.get(instrument, 0) != want:
            e.append("[1] instrument %s: %d articles != expected %d" % (
                instrument, per_instrument.get(instrument, 0), want))

    if not src.get("is_regulation_family"):
        e.append("[1b] is_regulation_family must be true (this is a family, not a single instrument)")
    instruments_meta = src.get("instruments") or []
    if len(instruments_meta) != 5:
        e.append("[1b] expected 5 instruments in metadata, got %d" % len(instruments_meta))

    if not (src.get("decision_preamble_ar") or "").strip():
        e.append("[1d] missing/empty decision_preamble_ar")
    if not (src.get("edition_colophon_ar") or "").strip():
        e.append("[1d] missing/empty edition_colophon_ar")

    # every article number within each instrument must be a contiguous 1..N sequence
    by_instrument = {}
    for k, a in arts.items():
        m = re.match(KEY_RE, k)
        if not m:
            continue
        instrument, n = m.group(1), int(m.group(2))
        by_instrument.setdefault(instrument, set()).add(n)
    for instrument, want in INSTRUMENT_ARTICLE_COUNTS.items():
        nums = by_instrument.get(instrument, set())
        expected = set(range(1, want + 1))
        if nums != expected:
            e.append("[1] instrument %s: article numbers %s != expected 1..%d" % (
                instrument, sorted(nums), want))

    sc = Counter()
    for k, a in arts.items():
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if "‌" in a["text"] or "￼" in a["text"] or "\x0c" in a["text"]:
            e.append("[2] %s: stray control/ZWNJ/object-replacement character present" % k)
        if "  " in a["text"]:
            e.append("[2] %s: double space present" % k)

        if k in AMENDED_KEYS:
            if ls != "معدلة":
                e.append("[2] %s: expected معدلة (amended-list article), got %r" % (k, ls))
            if not a.get("history"):
                e.append("[2] %s: amended article missing history" % k)
        else:
            if ls != "اصلية":
                e.append("[2] %s: expected اصلية (not in amended-list), got %r" % (k, ls))
            if a.get("history"):
                e.append("[2] %s: unexpected non-empty history for an اصلية article" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))
    if sum(sc.values()) != N:
        e.append("[2] status_counts sum %d != %d" % (sum(sc.values()), N))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the distinct/lower tier")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    if src.get("article_count") != N:
        e.append("[2f] declared article_count %r != %d" % (src.get("article_count"), N))
    for st in ALLOWED_STATUS:
        if src.get("status_counts", {}).get(st) != sc.get(st, 0):
            e.append("[2f] declared status_counts[%s] does not match actual per-article counts" % st)

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: unknown article_key in verified records" % r["article_key"]); continue
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != STATUS:
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("is_repealed") != (a.get("legal_status_ar") == "ملغاة"):
            e.append("[4] %s: is_repealed mismatch" % r["article_key"])
        if r.get("is_amended") != (a.get("legal_status_ar") == "معدلة"):
            e.append("[4] %s: is_amended mismatch" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: unknown article_key in llm records" % r["article_key"]); continue
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "english_used_for_correction", "text_summarized_or_paraphrased"):
            if r.get(f) is not False:
                e.append("[5] %s: %s must be False" % (r["article_key"], f))

    if e:
        print("FAIL: %d error(s) in Social Insurance Legacy Regulation (family) track:" % len(e))
        for x in e[:60]:
            print("  - %s" % x)
        return 1
    print("PASS: Social Insurance Legacy Regulation family -- 170 records across 5 instruments")
    print("  (umbrella decision 128/تأمينات [6] + التسجيل والاشتراكات [65] + تعويضات فرع")
    print("  المعاشات [42] + تعويضات فرع الأخطار المهنية [40] + اللجان الطبية [17])")
    print("  165 اصلية / 5 معدلة / 0 ملغاة / 0 مضافة")
    print("  - VERIFICATION TIER: KSU academic .doc mirror (single full-text source);")
    print("    only 2/170 articles verbatim-cross-checked (qistas.com); 4-lawiha family")
    print("    structure structurally corroborated (GOSI site + independent Saudi news)")
    print("  - This is the HISTORICAL companion regulation family for the LEGACY law (M/33,")
    print("    1421H) -- distinct from the NEW law's (M/273) own 1445H implementing regulation")
    print("  - Text reflects the source's self-described 6th edition (1429H/2008G) only;")
    print("    later (2022+) amendments confirmed to exist but NOT merged -- see discrepancies")
    return 0


if __name__ == "__main__":
    sys.exit(main())
