#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Civil Defense Law's subordinate
IMPLEMENTING REGULATIONS track (لوائح نظام الدفاع المدني الفرعية): two
components -- rights_duties (12 articles) and firefighting_rescue (9
articles), 21 records total, ALL اصلية (original, unamended). Both are FLAT
(no chapters/فصول). Base law tracked separately at sources/civil_defense/.

See the generator's module docstring and
sources/civil_defense_regulation/law/official_source/
civil_defense_regulation_official_source.json's structure_decision_note /
verification_methodology_note for the full account: BOTH components were
fetched via Wayback Machine snapshots of their own live government portal
after the live portal itself proved unreachable (laws.boe.gov.sa) or
redesigned (uqn.gov.sa) in this environment -> TIER_2 for both. A third
candidate instrument and ~30 sector-specific safety circulars were confirmed
to EXIST but are deliberately NOT included (scanned-PDF-only / out of scope);
see known_unresolved_discrepancies. This validator does not re-adjudicate
provenance; it only checks internal self-consistency and that the
discrepancies are still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "civil_defense_regulation", "law", "official_source",
                   "civil_defense_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "civil_defense_regulation", "law", "verified",
                       "civil_defense_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "civil_defense_regulation", "law", "verified",
                       "civil_defense_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "civil_defense_regulation_arabic_legal_llm",
                   "civil_defense_regulation_legal_llm_001_021.json")

N_TOTAL = 21
COMPONENT_COUNTS = {"rights_duties": 12, "firefighting_rescue": 9}
KEY_RE = r"civil_defense_regulation_(rights_duties|firefighting_rescue)_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 21, "معدلة": 0, "ملغاة": 0, "مضافة": 0}

FLAGGED_DISCREPANCY_KEYS = {
    "civil_defense_regulation_boe_uqn_live_portals_unreachable_wayback_used",
    "civil_defense_regulation_third_instrument_violations_committee_unconfirmed_text",
    "civil_defense_regulation_broader_sector_safety_codes_out_of_scope",
    "civil_defense_regulation_rights_duties_article_count_news_discrepancy",
    "civil_defense_regulation_firefighting_rescue_precise_dates_unconfirmed",
    "civil_defense_regulation_governance_body_succession_unconfirmed_inference",
}

AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰٴۖ-ۭ]")


def _bad_tatweel(text):
    """Mid-word justification tatweel only; trailing/standalone هـ or جـ forms
    (next char not an Arabic letter) are legitimate and NOT flagged."""
    bad = 0
    for m in re.finditer("ـ+", text):
        after = text[m.end()] if m.end() < len(text) else " "
        if re.match("[%s]" % AR, after):
            bad += 1
    return bad


def main():
    e = []
    for p in (SRC, RECORDS, SUMMARY, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    if len(arts) != N_TOTAL:
        e.append("[1] %d articles != %d" % (len(arts), N_TOTAL))
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    # per-component: continuous 1..N, no gaps/dupes; chapter_structure flat
    components = {c["component_key"]: c for c in src.get("components", [])}
    if set(components) != set(COMPONENT_COUNTS):
        e.append("[1a] components mismatch: %s != %s" % (
            sorted(components), sorted(COMPONENT_COUNTS)))
    for comp, want_n in COMPONENT_COUNTS.items():
        comp_keys = [k for k in arts if re.match(KEY_RE, k) and re.match(KEY_RE, k).group(1) == comp]
        nums = sorted(int(re.match(KEY_RE, k).group(2)) for k in comp_keys)
        if nums != list(range(1, want_n + 1)):
            e.append("[1b] component %s: article numbers not a clean 1..%d sequence: %s"
                     % (comp, want_n, nums))
        c = components.get(comp, {})
        if c.get("chapter_structure") != []:
            e.append("[1c] component %s is flat; chapter_structure must be []" % comp)
        if c.get("article_count") != want_n:
            e.append("[1c] component %s: article_count field != %d" % (comp, want_n))

    sc = Counter()
    for k, a in arts.items():
        m = re.match(KEY_RE, k)
        if not m:
            continue
        comp = m.group(1)
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section_status divergence" % k)
        if not a.get("status") or not str(a.get("status")).strip():
            e.append("[2] %s: empty verification status string" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if a.get("section_ar") != "":
            e.append("[2] %s: section_ar must be empty for this flat instrument" % k)
        if a.get("component") != comp:
            e.append("[2] %s: component field %r != key-derived %r" % (k, a.get("component"), comp))
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present" % k)
        if ls != "اصلية":
            e.append("[2] %s: expected اصلية (this track has zero amended/added/repealed "
                     "articles); found %r" % (k, ls))
        if a.get("history"):
            e.append("[2i] %s: non-amended article must have empty history[]" % k)
        if bool(a.get("is_mukarrar")):
            e.append("[2i] %s: no مكرر articles expected in either component" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if re.search(r"\s[،.:؛؟]", a["text"]):
            e.append("[2f] %s: residual space-before-punctuation artifact detected" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the tier")
    if not src.get("structure_decision_note"):
        e.append("[2d] missing structure_decision_note explaining single-vs-multiple-track "
                 "reasoning")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    # spot-checks anchoring key facts per component
    r1 = arts.get("civil_defense_regulation_rights_duties_art_001", {}).get("text", "")
    if "لغرض تطبيق أحكام هذه اللائحة" not in r1:
        e.append("[2j] rights_duties Article 1 missing expected definitions-clause wording")
    r6 = arts.get("civil_defense_regulation_rights_duties_art_006", {}).get("text", "")
    if "ثلاثين" not in r6 or "ستين" not in r6:
        e.append("[2j] rights_duties Article 6 missing expected 30/60-day recall-duration wording")
    r12 = arts.get("civil_defense_regulation_rights_duties_art_012", {}).get("text", "")
    if "ستين" not in r12 or "الجريدة الرسمية" not in r12:
        e.append("[2j] rights_duties Article 12 missing expected 60-day publication clause")

    f1 = arts.get("civil_defense_regulation_firefighting_rescue_art_001", {}).get("text", "")
    if "الإطفاء" not in f1 or "الإنقاذ" not in f1:
        e.append("[2j] firefighting_rescue Article 1 missing expected definitions wording")
    f7 = arts.get("civil_defense_regulation_firefighting_rescue_art_007", {}).get("text", "")
    if "لجنة النظر في مخالفات نظام الدفاع المدني ولوائحه" not in f7:
        e.append("[2j] firefighting_rescue Article 7 missing expected cross-reference to the "
                 "violations committee (the unconfirmed third-instrument lead)")
    f9 = arts.get("civil_defense_regulation_firefighting_rescue_art_009", {}).get("text", "")
    if "90" not in f9:
        e.append("[2j] firefighting_rescue Article 9 missing expected 90-day implementation clause")

    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] top-level legal_status_ar must be ساري")
    for comp in COMPONENT_COUNTS:
        if components.get(comp, {}).get("legal_status_ar") != "ساري":
            e.append("[2j] component %s legal_status_ar must be ساري" % comp)
    rd_decree = components.get("rights_duties", {})
    if rd_decree.get("decree_date_hijri") != "6/1/1442":
        e.append("[2j] rights_duties decree_date_hijri mismatch (expected 6/1/1442)")
    ff_decree = components.get("firefighting_rescue", {})
    if ff_decree.get("decree_date_hijri") != "6/3/1443":
        e.append("[2j] firefighting_rescue decree_date_hijri mismatch (expected 6/3/1443)")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N_TOTAL:
        e.append("[4] %d verified records != %d" % (len(ver), N_TOTAL))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: article_key not found in source" % r["article_key"]); continue
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("legal_status_ar") != a.get("legal_status_ar"):
            e.append("[4] %s: legal_status_ar mismatch" % r["article_key"])
        if r.get("component") != a.get("component"):
            e.append("[4] %s: component mismatch" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N_TOTAL:
        e.append("[4b] summary record_count != %d" % N_TOTAL)
    if summary.get("status_counts") != EXPECTED_COUNTS:
        e.append("[4b] summary status_counts != expected all-original counts")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N_TOTAL or len(recs) != N_TOTAL:
        e.append("[5] llm count != %d" % N_TOTAL)
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
            e.append("[5] %s: llm record source_status mismatch in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Civil Defense Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Civil Defense Law -- subordinate implementing regulations")
    print("  - 21 records across 2 components, ALL اصلية (unamended): 12 rights_duties "
          "(لائحة حقوق وواجبات من يستعان بهم), 9 firefighting_rescue (لائحة تنظيم أعمال "
          "الإطفاء والإنقاذ)")
    print("  - BOTH flat (no chapters/فصول); section_ar empty by design")
    print("  - rights_duties: CoM Resolution (10), 6/1/1442H, via BOE portal Wayback "
          "snapshots 2020-2025 (byte-identical across 5 captures) -> TIER_2")
    print("  - firefighting_rescue: Mandated Civil Defense Committee Resolution (1), "
          "6/3/1443H, via Umm al-Qura Gazette Wayback snapshots (2022) -> TIER_2")
    print("  - Live laws.boe.gov.sa (connection reset) and live uqn.gov.sa (redesigned SPA, "
          "old routes stale) both unreachable this pass -- Wayback used instead")
    print("  - Third candidate instrument (لائحة النظر في مخالفات نظام ولوائح الدفاع "
          "المدني) confirmed to EXIST but NOT included: only located copy is a scanned "
          "PDF with no text layer; OCR test was unreliable and was NOT used as text")
    print("  - ~30 additional sector-specific safety-requirement circulars found via CDX "
          "listing of 998.gov.sa -- disclosed as out-of-scope future candidates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
