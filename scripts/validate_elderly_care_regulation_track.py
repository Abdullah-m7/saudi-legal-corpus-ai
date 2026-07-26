#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation track of the Saudi
Arabian Elderly Rights and Care Law (8 records, all اصلية -- 0 معدلة, 0 ملغاة,
0 مضافة; this Regulation's OWN independent article numbering 1-8, NOT the
parent law's article numbers -- each article cross-references one or more
parent-Law articles via implements_law_articles).

VERIFICATION TIER: TIER_4 -- see the generator's module docstring and
sources/elderly_care_regulation/law/official_source/
elderly_care_regulation_official_source.json's verification_methodology_note
for the full account. Summary: laws.boe.gov.sa has no dedicated page for this
Regulation; an official hrsd.gov.sa PDF confirms existence/structure/
signature only (severe font-encoding corruption, confirmed via two
independent extraction tools, prevents verbatim use); the only source with
real verbatim text, qanoniah.com, enforces a confirmed 10-index-item free-
preview cap yielding exactly 8 real articles. TOTAL article count NOT
confirmed -- excluded, not fabricated. IMPORTANT: Council of Ministers
Resolution 292 is NOT this Regulation's issuing instrument (see the
correction recorded in known_unresolved_discrepancies). This validator does
not re-adjudicate provenance; it checks internal self-consistency and that
every discrepancy and the partial-coverage facts are not silently dropped.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "elderly_care_regulation", "law", "official_source",
                   "elderly_care_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "elderly_care_regulation", "law", "verified",
                       "elderly_care_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "elderly_care_regulation", "law", "verified",
                       "elderly_care_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "elderly_care_regulation_arabic_legal_llm",
                   "elderly_care_regulation_legal_llm_001_008.json")
N = 8
KEY_RE = r"elderly_care_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 8, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_IMPLEMENTS = {
    "elderly_care_regulation_art_001": [],
    "elderly_care_regulation_art_002": [2],
    "elderly_care_regulation_art_003": [3, 6],
    "elderly_care_regulation_art_004": [4],
    "elderly_care_regulation_art_005": [5],
    "elderly_care_regulation_art_006": [6],
    "elderly_care_regulation_art_007": [7],
    "elderly_care_regulation_art_008": [8, 6],
}

STATUS_UNCHANGED = "UNCHANGED"
FLAGGED_DISCREPANCY_KEYS = {
    "elderly_care_regulation_com_292_misattribution_corrected",
    "elderly_care_regulation_decree_number_date_unconfirmed",
    "elderly_care_regulation_pdf_font_corruption",
    "elderly_care_regulation_partial_coverage_confirmed",
    "elderly_care_regulation_no_boe_dedicated_page",
    "elderly_care_regulation_status_inferred_not_confirmed",
    "elderly_care_regulation_distinct_own_numbering",
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
    if src.get("total_article_count_confirmed") is not False:
        e.append("[1] total_article_count_confirmed must be explicitly False (partial coverage)")
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    numbers = sorted(a["article_number"] for a in arts.values())
    if numbers != list(range(1, N + 1)):
        e.append("[1b] this Regulation's own article numbers %s != contiguous 1..%d "
                 "(own independent numbering, not the parent law's numbers)" % (numbers, N))

    for k, a in arts.items():
        expected = EXPECTED_IMPLEMENTS.get(k)
        if expected is None:
            e.append("[1d] %s: no expected implements_law_articles mapping defined" % k)
        elif a.get("implements_law_articles") != expected:
            e.append("[1d] %s: implements_law_articles %s != expected %s"
                     % (k, a.get("implements_law_articles"), expected))

    if src.get("parent_law_key") != "elderly_care" or src.get("parent_law_component") != "law":
        e.append("[1e] parent_law_key/parent_law_component must link back to elderly_care/law")
    if src.get("parent_law_article_range") != "1-23":
        e.append("[1e] parent_law_article_range must be '1-23' (matches elderly_care_law's "
                 "confirmed 23-article scope)")
    if src.get("confirmed_covered_law_articles") != [1, 2, 3, 4, 5, 6, 7, 8]:
        e.append("[1e] confirmed_covered_law_articles != [1..8]")
    excl = src.get("excluded_law_articles_not_recovered")
    if not excl or "9-23" not in excl:
        e.append("[1e] excluded_law_articles_not_recovered must explicitly document range "
                 "9-23 as not recovered (not silently dropped)")

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != STATUS_UNCHANGED:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS_UNCHANGED, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected structure/section status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if a.get("history"):
            e.append("[2i] %s: original article must have empty history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if "<" in a["text"] or ">" in a["text"]:
            e.append("[2g] %s: residual HTML tag leftover from qanoniah.com markup" % k)

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
        # this is the single most important honesty check for this track: the
        # CoM-292-misattribution correction must actually be present.
        corr = next((d for d in disc if d["article_key"]
                     == "elderly_care_regulation_com_292_misattribution_corrected"), None)
        if not corr or "292" not in corr.get("description", ""):
            e.append("[2e] the CoM-292-misattribution correction must explicitly mention '292'")

    # decree/date must be explicitly recorded as unconfirmed, not a fabricated
    # plausible-looking value
    if "292" in str(src.get("decree", "")):
        e.append("[2j] decree field must NOT attribute issuance to CoM Resolution 292")
    if not src.get("decree") or "غير مؤكَّد" not in src.get("decree", ""):
        e.append("[2j] decree field must explicitly state the decision number is unconfirmed")
    if src.get("legal_status_ar", "").find("ساري") != 0:
        e.append("[2j] legal_status_ar must start with ساري (with an honesty caveat following)")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False")

    # spot-check the internal coherence between this Regulation's own
    # cross-references and the already-ingested elderly_care_law text
    a1 = arts.get("elderly_care_regulation_art_001", {})
    if "الستين" not in a1.get("text", "") or "اللجنة التوجيهية" not in a1.get("text", ""):
        e.append("[2j] Article 1 (تعريفات) should define both كبير السن (sixty years) and "
                 "اللجنة التوجيهية (a definition absent from the parent Law's own Article 1)")
    a7 = arts.get("elderly_care_regulation_art_007", {})
    if "م/73" not in a7.get("text", ""):
        e.append("[2j] Article 7 should reference the Personal Status Law (Royal Decree م/73)")

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
        if r.get("implements_law_articles") != a.get("implements_law_articles"):
            e.append("[4] %s: implements_law_articles mismatch" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if summary.get("excluded_law_articles_not_recovered") != src.get("excluded_law_articles_not_recovered"):
        e.append("[4b] summary must carry forward excluded_law_articles_not_recovered "
                 "(partial-coverage disclosure must not be silently dropped downstream)")
    if summary.get("total_article_count_confirmed") is not False:
        e.append("[4b] summary must carry forward total_article_count_confirmed=False")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    if llm.get("article_range") != [1, N]:
        e.append("[5] llm article_range must be [1, %d] (this Regulation's own numbering)" % N)
    if llm.get("total_article_count_confirmed") is not False:
        e.append("[5] llm layer must carry forward total_article_count_confirmed=False")
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
        if r.get("source_trust", {}).get("source_status") != STATUS_UNCHANGED.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Elderly Care Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Saudi Arabian Elderly Rights and Care Law")
    print("  - 8 records: 8 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (own independent numbering 1-8)")
    print("  - VERIFICATION TIER: TIER_4 -- laws.boe.gov.sa has no dedicated page for this")
    print("    Regulation; official hrsd.gov.sa PDF confirms existence/structure/signature only")
    print("    (severe font-encoding corruption, confirmed via two independent extraction tools,")
    print("    prevents verbatim use); the only source with real verbatim text, qanoniah.com,")
    print("    enforces a confirmed 10-index-item free-preview cap -> 8 real articles recovered")
    print("  - IMPORTANT CORRECTION: Council of Ministers Resolution 292 is NOT this")
    print("    Regulation's issuing instrument (it approved the parent Law); exact ministerial")
    print("    decision number/date NOT confirmed this pass -- recorded as unconfirmed, not")
    print("    fabricated")
    print("  - PARTIAL COVERAGE, EXPLICITLY DISCLOSED: covers only this Regulation's own Articles")
    print("    1-8 (implementing parent-Law Articles 1, 2, 3&6, 4, 5, 6, 7, 8&6); TOTAL article")
    print("    count of this Regulation NOT confirmed -- likely greater than 8 per unreliable PDF")
    print("    fragments referencing parent-Law articles up to ~20, but excluded, not fabricated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
