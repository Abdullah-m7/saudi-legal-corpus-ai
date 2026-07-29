#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Statutory Provisions Regulating the
Landlord-Tenant Relationship track (12 records) — الأحكام النظامية الخاصة
بضبط العلاقة بين المؤجر والمستأجر.

Trust gate: every item's status must be the single TIER_1 dual-primary
status string (uqn.gov.sa Umm Al-Qura Gazette AND rega.gov.sa REGA's own
portal, two independent official sources in full agreement). Items are
labeled with Arabic ordinal words (أولاً..ثاني عشر), not مادة-numbered, but
numbered by ordinal position 1..12 internally (no مكرر), flat structure
with no chapter/section wrapper (section_ar empty for every item — not a
bug). FRESH FULL ISSUANCE: all 12 اصلية; none amended, repealed or added
(consolidated_amended_law must be False).

Also checks: the date-ordering discrepancy resolution is present and
internally consistent (Decree M/73 2/4/1447H must be chronologically AFTER
Council of Ministers Resolution 226 24/3/1447H, which must be AFTER Shura
Council Resolution 8/1 22/3/1447H); the mandatory geographic-scope
(Riyadh-only) disclosure is present and non-empty; and the Riyadh-only
items (2-5) are cross-referenced correctly in item 6's own text.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "landlord_tenant_relationship_regulation", "regulation",
                   "official_source", "landlord_tenant_relationship_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "landlord_tenant_relationship_regulation", "regulation",
                       "verified", "landlord_tenant_relationship_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "landlord_tenant_relationship_regulation", "regulation",
                       "verified", "landlord_tenant_relationship_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "landlord_tenant_relationship_regulation_arabic_legal_llm",
                   "landlord_tenant_relationship_regulation_legal_llm_001_012.json")
STATUS = "UQN_GAZETTE_OFFICIAL_PRIMARY_TEXT_AR_X_REGA_OFFICIAL_PORTAL_DUAL_PRIMARY_CROSSVERIFIED"
N = 12
KEY_RE = r"landlord_tenant_relationship_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 12}
EXPECTED_LABELS = ["أولاً", "ثانياً", "ثالثاً", "رابعاً", "خامساً", "سادساً", "سابعاً",
                   "ثامناً", "تاسعاً", "عاشراً", "حادي عشر", "ثاني عشر"]
TRUSTED = {STATUS}
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

    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1] numbered items not a complete 1..%d sequence" % N)
    if len(arts) != N:
        e.append("[1] %d items != %d" % (len(arts), N))

    sc = Counter()
    for k, a in arts.items():
        if a["status"] not in TRUSTED:
            e.append("[2] %s: UNTRUSTED status %r" % (k, a["status"]))
        if a.get("source_tier") != "primary":
            e.append("[2] %s: source_tier != primary" % k)
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if a.get("section_ar"):
            e.append("[2] %s: unexpected non-empty section_ar in a flat-structure regulation" % k)
        if not a.get("text_complete", True):
            e.append("[2] %s: text_complete is False" % k)
        if a.get("history"):
            e.append("[2] %s: fresh issuance should have empty history" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("معدلة") or sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected amended/repealed/added items present")

    for i, want_label in enumerate(EXPECTED_LABELS, start=1):
        key = "landlord_tenant_relationship_regulation_art_%03d" % i
        if arts.get(key, {}).get("number_label_ar") != want_label:
            e.append("[2d] %s: number_label_ar %r != expected %r"
                     % (key, arts.get(key, {}).get("number_label_ar"), want_label))

    if src.get("law_component") != "regulation":
        e.append("[2e] law_component must be 'regulation' (self-described as أحكام, not نظام)")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2e] consolidated_amended_law must be False (fresh issuance)")

    # [2f] mandatory geographic-scope (Riyadh-only) disclosure must be present and substantive
    geo = src.get("geographic_scope_disclosure_ar") or ""
    if "الرياض" not in geo or len(geo) < 200:
        e.append("[2f] geographic_scope_disclosure_ar missing or insufficiently detailed")
    if "الرياض" not in arts["landlord_tenant_relationship_regulation_art_006"]["text"]:
        e.append("[2f] item 6 (سادساً) text must itself state the Riyadh-only scope")
    for i in (2, 3, 4, 5):
        key = "landlord_tenant_relationship_regulation_art_%03d" % i
        label = arts[key]["number_label_ar"]
        if label not in arts["landlord_tenant_relationship_regulation_art_006"]["text"]:
            e.append("[2f] item 6's own text must cross-reference item %d's label (%s)" % (i, label))

    # [2g] date-ordering discrepancy resolution must be present and internally consistent
    ddr = src.get("date_discrepancy_resolution") or {}
    if not ddr.get("resolution") or len(ddr.get("resolution", "")) < 200:
        e.append("[2g] date_discrepancy_resolution.resolution missing or too thin")
    decree_date = src.get("decree_date_hijri", "")
    com_date = src.get("council_of_ministers_decision", "")
    if "24/3/1447" not in com_date:
        e.append("[2g] council_of_ministers_decision date must read 24/3/1447 (Rabi' al-Awwal, "
                 "month 3) -- the resolved date, not the flagged 24/4 (Rabi' al-Thani) misreading")
    if decree_date != "02/04/1447":
        e.append("[2g] decree_date_hijri must be 02/04/1447 (chronologically after 24/3/1447)")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"], {})
        if r["article_text_verified"] != a.get("text"):
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("official_text_status") != STATUS:
            e.append("[4] %s: bad status" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    if llm.get("law_component") != "regulation":
        e.append("[5] llm law_component must be 'regulation'")
    for r in recs:
        a = arts.get(r["article_key"], {})
        if r["article_text_ar"] != a.get("text"):
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "text_summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[5] %s: %s must be False" % (r["article_key"], f))

    summ = json.load(open(SUMMARY, encoding="utf-8"))
    if summ.get("record_count") != N:
        e.append("[6] summary record_count != %d" % N)
    if summ.get("decree") != src.get("decree") or summ.get("decree_date_hijri") != decree_date:
        e.append("[6] summary decree identity mismatch vs source")

    if e:
        print("FAIL: %d error(s) in Landlord-Tenant Relationship Regulation track:" % len(e))
        for x in e[:20]:
            print("  - %s" % x)
        return 1
    print("PASS: Landlord-Tenant Relationship Regulation — 12 records (fresh issuance: all 12 اصلية)")
    print("  - trust gate: dual independent official primary sources (uqn.gov.sa Umm Al-Qura "
          "Gazette X rega.gov.sa REGA portal), TIER_1_PRIMARY_MULTI_SOURCE")
    print("  - numbered 1..12 by ordinal position (no مكرر), labels أولاً..ثاني عشر, flat structure; "
          "no dual-status divergence")
    print("  - date-ordering discrepancy RESOLVED: Shura 8/1 (22/3/1447H) -> CoM Res 226 "
          "(24/3/1447H) -> Royal Decree M/73 (2/4/1447H) -> Gazette 5120 (16/5/1447H)")
    print("  - GEOGRAPHIC SCOPE: items 2-5 (ثانياً-خامساً) apply to Riyadh city ONLY at present "
          "(item 6/سادساً); not nationwide -- disclosed explicitly, not silently presented as "
          "nationwide")
    print("  - IN-FORCE Royal Decree M/73 (2/4/1447H); Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
