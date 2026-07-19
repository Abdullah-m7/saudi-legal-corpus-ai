#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Implementing Regulation of the
Health System Law track (10 records, all اصلية -- 0 معدلة, 0 ملغاة, 0 مضافة;
non-contiguous article numbering 2-11, mirroring the parent health_system_law
track's own article numbers rather than an independent 1..N sequence).

VERIFICATION TIER: TIER_4 -- see the generator's module docstring and
sources/health_system/regulation/official_source/
health_system_regulation_official_source.json's verification_methodology_note
for the full account. Summary: laws.boe.gov.sa has no dedicated page for this
Regulation and its live portal was unreachable this pass; Wayback Machine is
blocked at this session's egress-policy level; istitlaa.ncc.gov.sa (the
officially-designated primary host per MOH's own e-participation page) was
confirmed unreachable via THREE independent channels (direct curl, WebFetch,
r.jina.ai). The only source with real article text, qanoniah.com, enforces a
confirmed server-side 10-item preview cap (verified via multiple pagination
parameters). This track therefore covers ONLY Articles 2-11 of the parent
Law -- Article 1 has no entry in the source, and Articles 12-19 could not be
recovered and are excluded, not fabricated. This validator does not
re-adjudicate any of this; it only checks internal self-consistency of the
text this track actually ingests, and that every discrepancy is still
recorded and that the partial-coverage facts are not silently dropped.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "health_system", "regulation", "official_source",
                   "health_system_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "health_system", "regulation", "verified",
                       "health_system_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "health_system", "regulation", "verified",
                       "health_system_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "health_system_regulation_arabic_legal_llm",
                   "health_system_regulation_legal_llm_001_010.json")
N = 10
KEY_RE = r"health_system_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 10, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_COVERED_LAW_ARTICLES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

STATUS_UNCHANGED = "UNCHANGED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
FLAGGED_DISCREPANCY_KEYS = {
    "health_system_regulation_partial_coverage_confirmed",
    "health_system_regulation_article1_no_entry",
    "health_system_regulation_official_sources_unreachable",
    "health_system_regulation_decree_number_format_unconfirmed",
    "health_system_regulation_distinct_from_parent_law_track",
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

    covered = sorted(a["article_number"] for a in arts.values())
    if covered != EXPECTED_COVERED_LAW_ARTICLES:
        e.append("[1b] covered parent-law article numbers %s != expected %s"
                  % (covered, EXPECTED_COVERED_LAW_ARTICLES))

    # this track's own keys must encode the SAME number as article_number (no
    # silent resequencing away from the parent law's article numbers)
    for k, a in arts.items():
        m = re.match(KEY_RE, k)
        if m and int(m.group(1)) != a["article_number"]:
            e.append("[1b] %s: key number != article_number field (%d)"
                      % (k, a["article_number"]))

    if src.get("parent_law_article_range") != "1-19":
        e.append("[1c] parent_law_article_range must be '1-19' (matches health_system_law "
                 "track's own confirmed 19-article scope)")
    if src.get("confirmed_covered_law_articles") != EXPECTED_COVERED_LAW_ARTICLES:
        e.append("[1c] confirmed_covered_law_articles != %s" % EXPECTED_COVERED_LAW_ARTICLES)
    excl = src.get("excluded_law_articles_not_recovered")
    if not excl or "1" not in excl or "12-19" not in excl:
        e.append("[1c] excluded_law_articles_not_recovered must explicitly document article 1 "
                 "and range 12-19 as not recovered (not silently dropped)")

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != STATUS_UNCHANGED:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS_UNCHANGED, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if k not in AMENDED_KEYS and a.get("history"):
            e.append("[2i] %s: non-amended article must have empty history[]" % k)
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

    if not src.get("amendment_history"):
        e.append("[2k] missing amendment_history (must record founding decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "30/69181" not in decrees:
            e.append("[2k] amendment_history must reference decree 30/69181")

    # spot-checks anchoring key facts established this pass; these also act as
    # a substantive-coherence cross-check against the already-ingested parent
    # health_system_law track (paragraph structure of Article 4 must mirror
    # the parent law's own 9 sub-items a-i)
    art4 = arts.get("health_system_regulation_art_004", {})
    for letter in ("أ-", "ب-", "ج-", "د-", "هـ-", "و-", "ز-", "ح-", "ط-"):
        if letter not in art4.get("text", ""):
            e.append("[2j] Article 4's implementing text should contain sub-item '%s' "
                     "(mirrors parent Law Article 4's own a-through-i list)" % letter)
    art11 = arts.get("health_system_regulation_art_011", {})
    if "القطاع الخاص" not in art11.get("text", ""):
        e.append("[2j] Article 11's implementing text should reference hospital "
                 "privatization ('القطاع الخاص'), matching parent Law Article 11")
    if src.get("decree") != "قرار وزاري رقم 30/69181" or src.get("decree_date_hijri") != "15/6/1424":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Ministerial Decision "
                 "30/69181, 15/6/1424H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False")
    if src.get("parent_law_key") != "health_system" or src.get("parent_law_component") != "law":
        e.append("[2j] parent_law_key/parent_law_component must link back to health_system/law")

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
        if r.get("implements_law_article") != a["article_number"]:
            e.append("[4] %s: implements_law_article != article_number" % r["article_key"])
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

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    if llm.get("article_range") != [2, 11]:
        e.append("[5] llm article_range must be [2, 11] (not [1, N], to avoid implying full "
                 "1..N coverage that does not exist)")
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
        print("FAIL: %d error(s) in Health System Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Arabian Implementing Regulation of the Health System Law")
    print("  - 10 records: 10 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة")
    print("  - non-contiguous numbering mirroring the parent law's own article numbers (2-11);")
    print("    no independent 1..N resequencing")
    print("  - VERIFICATION TIER: TIER_4 -- single source (qanoniah.com's public API) with a")
    print("    confirmed, server-enforced 10-item preview cap; laws.boe.gov.sa has no dedicated")
    print("    page for this Regulation and was unreachable live; Wayback Machine blocked at")
    print("    this session's egress-policy level; istitlaa.ncc.gov.sa (MOH's own designated")
    print("    primary host) confirmed unreachable via three independent channels this pass")
    print("  - Ministerial Decision No. 30/69181 (15/6/1424H), issued pursuant to Article 18 of")
    print("    the Health System Law (Royal Decree M/11, 23/3/1423H)")
    print("  - PARTIAL COVERAGE, EXPLICITLY DISCLOSED: covers only parent-Law Articles 2-11;")
    print("    Article 1 has no entry in the source at all; Articles 12-19 (incl. the heavily")
    print("    amended Article 16 Health Services Council) could not be recovered this pass and")
    print("    are excluded, not fabricated")
    print("  - CONFIRMED NEGATIVE FINDING: no repeal of a prior implementing regulation found in")
    print("    any source (consistent with this being the first Implementing Regulation issued")
    print("    under the parent Law's Article 18 mandate)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
