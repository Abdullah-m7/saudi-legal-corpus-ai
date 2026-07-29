#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the System for the Management of Seized and
Confiscated Funds in Money-Laundering Crimes, Related Predicate Crimes, and
Terrorist-Financing Crimes track (نظام إدارة الأموال المحجوزة والمصادرة في
جرائم غسل الأموال والجرائم الأصلية المرتبطة بها وجرائم تمويل الإرهاب; 15
records, all اصلية, no chapters/فصول -- a flat, single-block statute).

VERIFICATION TIER -- see the generator's module docstring and
sources/seized_confiscated_funds_management_system/law/official_source/
seized_confiscated_funds_management_system_official_source.json's
verification_methodology_note for the full account. This validator asserts:
exactly 15 articles in a clean 1..15 run; chapter_structure is an empty list
(no فصول/أبواب); all 15 articles are اصلية with empty amendment history
(single edition, only a disclosed pure positional renumbering, no
substantive change); no ملغاة/معدلة/مضافة articles this pass; the System is
recorded as issued but NOT YET IN FORCE (legal_status_ar must say so); the
one deliberately-preserved Arabic-Indic digit occurrence in Article 8 is
explicitly allowed (not flagged as a residual-digit defect) since it is
disclosed and matches both independent sources exactly.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "seized_confiscated_funds_management_system", "law",
                   "official_source", "seized_confiscated_funds_management_system_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "seized_confiscated_funds_management_system", "law", "verified",
                       "seized_confiscated_funds_management_system_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "seized_confiscated_funds_management_system", "law", "verified",
                       "seized_confiscated_funds_management_system_verified_summary.json")
LLM = os.path.join(ROOT, "data", "seized_confiscated_funds_management_system_arabic_legal_llm",
                   "seized_confiscated_funds_management_system_legal_llm_001_015.json")
N = 15
KEY_RE = r"seized_confiscated_funds_management_system_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 15, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
STATUS = "UQN_GAZETTE_LIVE_HTML_PRIMARY_QANOONSA_TRIPLE_PAGE_CROSSVERIFIED_ARTICLE_RENUMBERING_DISCLOSED"
FLAGGED_DISCREPANCY_KEYS = {
    "seized_confiscated_funds_management_system_article_renumbering_amendment",
    "seized_confiscated_funds_management_system_gregorian_date_correction",
    "seized_confiscated_funds_management_system_digit_script_variance_article_8",
    "seized_confiscated_funds_management_system_boe_and_wilayah_unreachable",
    "seized_confiscated_funds_management_system_implementing_regulation_and_committee_not_ingested",
}
AR = "ء-ي"
# Article 8, paragraph 3's disclosed, source-faithful Arabic-Indic digit rendering of "30"
# (identical on uqn.gov.sa and qanoonsa.com) -- deliberately NOT normalized, per this
# corpus's no-silent-correction policy. See known_unresolved_discrepancies.
ALLOWED_EASTERN_DIGIT_ARTICLE = "seized_confiscated_funds_management_system_art_008"
ALLOWED_EASTERN_DIGIT_SNIPPET = "(٣٠)"


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
    for p in (SRC, RECORDS, SUMMARY, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1

    e = []
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    if src.get("article_count") != N:
        e.append("[1] article_count field %r != %d" % (src.get("article_count"), N))
    seen = set()
    for k in arts:
        m = re.match(KEY_RE, k)
        if not m:
            e.append("[1] %s: does not match key pattern" % k)
        else:
            seen.add(int(m.group(1)))
    if seen != set(range(1, N + 1)):
        e.append("[1] article numbers not a clean 1..%d run: %s" % (N, sorted(seen)))

    if src.get("chapter_structure") != []:
        e.append("[1c] chapter_structure must be an empty list (flat statute, no فصول/أبواب)")

    if src.get("consolidated_amended_law") is not False:
        e.append("[1d] consolidated_amended_law must be False for this track")

    ls_top = src.get("legal_status_ar") or ""
    if "غير ساري" not in ls_top:
        e.append("[1f] legal_status_ar must indicate the System is issued but not yet in "
                 "force, got %r" % ls_top)

    sc = Counter()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or unexpected latin/html leftovers" % k)
        if a.get("section_ar") is None:
            e.append("[2] %s: section_ar field must be present (empty string allowed -- "
                     "flat statute, no chapters)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        # Digit-script check: allow exactly the one disclosed Arabic-Indic occurrence in
        # Article 8 (matches both independent sources identically); flag any other residual
        # Eastern-Arabic-Indic digit as an unexplained defect.
        eastern_digits = re.findall(r"[٠-٩]+", a["text"])
        if eastern_digits:
            if k != ALLOWED_EASTERN_DIGIT_ARTICLE or ALLOWED_EASTERN_DIGIT_SNIPPET not in a["text"]:
                e.append("[2] %s: unexplained residual Eastern-Arabic-Indic digit %r"
                         % (k, eastern_digits))
        if "  " in a["text"]:
            e.append("[2] %s: residual double-space artifact" % k)
        if not a.get("number_label_ar"):
            e.append("[2] %s: missing number_label_ar" % k)

        # single, current edition: every article must be اصلية, no substantive amendment
        # history (the only known change is a disclosed pure renumbering, not a text change)
        if ls != "اصلية":
            e.append("[3] %s: article %d expected اصلية (only a disclosed positional "
                     "renumbering, no substantive amendment confirmed this pass), got %r"
                     % (k, n, ls))
        if a.get("history"):
            e.append("[3] %s: article %d must have empty history (اصلية-only track)" % (k, n))

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))
    declared = src.get("status_counts") or {}
    for st in ALLOWED_STATUS:
        if declared.get(st, 0) != sc.get(st, 0):
            e.append("[2f] declared status_counts[%s] does not match actual per-article counts" % st)

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the tier")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    if src.get("law_component") != "law":
        e.append("[2j] law_component must be 'law'")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: unknown article_key" % r["article_key"]); continue
        if r.get("law_component") != "law":
            e.append("[4] %s: law_component must be 'law', got %r"
                     % (r["article_key"], r.get("law_component")))
        if "article_number" not in r:
            e.append("[4] %s: missing article_number field" % r["article_key"])
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("is_amended") is not False or r.get("is_repealed") is not False or r.get("is_added") is not False:
            e.append("[4] %s: expected all status flags False (اصلية-only track)" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts mismatch with source")
    if summary.get("chapter_structure") != []:
        e.append("[4b] summary chapter_structure must be an empty list")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: unknown article_key" % r["article_key"]); continue
        if r.get("law_component") != "law":
            e.append("[5] %s: law_component must be 'law', got %r"
                     % (r["article_key"], r.get("law_component")))
        if "article_number" not in r:
            e.append("[5] %s: missing article_number field" % r["article_key"])
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Seized/Confiscated Funds Management System track:" % len(e))
        for x in e[:25]:
            print("  - %s" % x)
        return 1
    print("PASS: System for the Management of Seized and Confiscated Funds in "
          "Money-Laundering Crimes, Related Predicate Crimes, and Terrorist-Financing "
          "Crimes — 15 records (15 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; no chapters)")
    print("  - TIER: TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED -- uqn.gov.sa official Gazette")
    print("    live page (entry 4001359) cross-verified against three independent")
    print("    qanoonsa.com pages (Royal Decree M/1, CoM Resolution 16, System full text)")
    print("  - laws.boe.gov.sa and wilayah.gov.sa (administering authority's own site) were")
    print("    both unreachable this pass (connection reset)")
    print("  - One disclosed, purely positional article-renumbering correction found between")
    print("    the original 18/6/2026G publication and the current live uqn.gov.sa page --")
    print("    no substantive text change in any article, only a numbering shift")
    print("  - Issued but NOT YET IN FORCE: takes effect ~16/9/2026G (90 days after")
    print("    18/6/2026G gazette publication), a date still in the future at build time")
    return 0


if __name__ == "__main__":
    sys.exit(main())
