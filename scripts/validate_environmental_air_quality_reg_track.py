#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation for Air Quality track
(8 records: 8 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة; flat 8-article structure with
descriptive article titles; the violations/penalties Table 3 and the 8 technical
appendices are documented but out of scope).

VERIFICATION TIER -- see the generator's module docstring and
sources/environmental_air_quality/official_source/
environmental_air_quality_reg_official_source.json's verification_methodology_note
for the full account. Key points this validator anchors: the founding decision
number (512258/1/1442, 24/9/1442H) is confirmed from the Umm Al-Qura gazette; the
article text is dual-verified between mewa.gov.sa (born-digital PDF) and
qanoniah.com; laws.boe.gov.sa was checked first but is unreachable this pass and has
no dedicated lawId page; all 8 articles are اصلية (Table 3's later amendment does
not touch them); no repeal/supersession clause exists. This validator does not
re-adjudicate provenance; it checks internal self-consistency and that every
disclosed discrepancy is recorded. Note: unlike some other tracks, Latin characters
ARE permitted in article text here, because Articles 5-6 contain genuine Latin
technical acronyms/method names (CEMS, RATA, USEPA Method, ...) that are part of the
source; only HTML/markdown residue is rejected.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "environmental_air_quality", "official_source",
                   "environmental_air_quality_reg_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "environmental_air_quality", "verified",
                       "environmental_air_quality_reg_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "environmental_air_quality", "verified",
                       "environmental_air_quality_reg_verified_summary.json")
LLM = os.path.join(ROOT, "data", "environmental_air_quality_arabic_legal_llm",
                   "environmental_air_quality_reg_legal_llm_001_008.json")
N = 8
KEY_RE = r"environmental_air_quality_reg_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 8, "معدلة": 0, "ملغاة": 0, "مضافة": 0}

STATUS_UNCHANGED = "UNCHANGED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()

FLAGGED_DISCREPANCY_KEYS = {
    "air_quality_gap_map_candidate_confirmed_and_refined",
    "air_quality_decision_number_now_confirmed_primary",
    "air_quality_boe_unreachable_no_dedicated_page",
    "air_quality_primary_source_mewa_plus_qanoniah_dual_verification",
    "air_quality_tables_and_appendices_out_of_scope",
    "air_quality_table3_amended_1446_articles_unchanged",
    "air_quality_no_repeal_supersession_clause",
    "air_quality_three_distinct_dates",
    "air_quality_legal_basis_article_48_penalties_article_38",
    "air_quality_extraction_artifact_fixes_disclosed",
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

    # sequential numbering 1..N, each with a descriptive title
    seen = set()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
        seen.add(n)
        if not a.get("title_ar"):
            e.append("[1t] %s: missing descriptive title_ar" % k)
        if a.get("number_label_ar") != "المادة (%d)" % n:
            e.append("[1t] %s: number_label_ar mismatch (%r)" % (k, a.get("number_label_ar")))
    if seen != set(range(1, N + 1)):
        e.append("[1] article numbers != 1..%d (%s)" % (N, sorted(seen)))

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != STATUS_UNCHANGED:
            e.append("[2] %s: expected status UNCHANGED, got %r" % (k, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if ls != "اصلية":
            e.append("[2] %s: expected legal_status_ar اصلية (all 8 articles are original), got %r" % (k, ls))
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        txt = a.get("text", "")
        if not txt.strip():
            e.append("[2] %s: empty text" % k)
        # reject HTML / markdown residue (Latin technical terms ARE allowed)
        if re.search(r"[<>]|&[a-z]+;|\]\(|\*\*|https?://", txt):
            e.append("[2] %s: html/markdown residue detected" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(txt):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if a.get("history"):
            e.append("[2i] %s: original article must have empty history[]" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if "\xa0" in txt:
            e.append("[2f] %s: residual non-breaking-space artifact" % k)
        if "“" in txt or "”" in txt:
            e.append("[2f] %s: residual curly-quote artifact" % k)
        if "  " in txt:
            e.append("[2f] %s: residual double-space artifact" % k)
        # extraction-artifact regression guards (each disclosed in the source)
        if re.search(r":\S", txt):
            e.append("[2g] %s: colon-glue artifact (missing space after ':')" % k)
        if "فيالجدول" in txt or "فيالملحق" in txt:
            e.append("[2g] %s: preposition-glue artifact" % k)
        # presentation/Farsi letter forms must have been folded/normalised out
        if "ھ" in txt or "ی" in txt:
            e.append("[2g] %s: unfolded presentation/Farsi letter form (ھ/ی) present" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note")
    vn = src.get("verification_methodology_note", "")
    if "512258/1/1442" not in vn:
        e.append("[2d] verification note must cite the confirmed decision number 512258/1/1442")

    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    if not src.get("amendment_history"):
        e.append("[2k] missing amendment_history")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "512258/1/1442" not in decrees:
            e.append("[2k] amendment_history must reference founding decision 512258/1/1442")
        if "15029057" not in decrees:
            e.append("[2k] amendment_history must reference Table-3-amending decision 15029057")

    # the excluded tabular annexes must be documented (Table 3 + 8 appendices)
    ann = src.get("excluded_tabular_annexes") or []
    if len(ann) != 9:
        e.append("[2l] expected 9 documented excluded tabular annexes (Table 3 + 8 appendices), got %d" % len(ann))
    labels = " ".join(x.get("label_ar", "") for x in ann)
    if "الجدول (3)" not in labels or "الملحق 8" not in labels:
        e.append("[2l] excluded_tabular_annexes must include الجدول (3) and الملحق 1..8")

    # spot-checks anchoring key facts
    a1 = arts.get("environmental_air_quality_reg_art_001", {})
    if "النظام: نظام البيئة" not in a1.get("text", "") or "المركز الوطني للرقابة على الالتزام البيئي" not in a1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (النظام / المركز)")
    a2 = arts.get("environmental_air_quality_reg_art_002", {})
    if "تسري أحكام هذه اللائحة على جميع الأشخاص" not in a2.get("text", ""):
        e.append("[2j] Article 2 missing expected scope clause")
    a8 = arts.get("environmental_air_quality_reg_art_008", {})
    if "الجدول (3)" not in a8.get("text", ""):
        e.append("[2j] Article 8 must reference الجدول (3) (violations/penalties)")
    if src.get("decree") != "قرار وزير البيئة والمياه والزراعة رقم (512258/1/1442)" \
            or src.get("decree_date_hijri") != "24/9/1442":
        e.append("[2j] decree/decree_date_hijri mismatch with confirmed 512258/1/1442, 24/9/1442H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (the 8 articles are unamended; "
                 "only the out-of-scope Table 3 was amended)")
    if "الثامنة والأربعين" not in (src.get("legal_basis_ar", "") + src.get("issuing_authority_ar", "")):
        e.append("[2j] legal basis (Article 48 of the Environmental Law) not recorded")
    if "preamble_ar" in src:
        e.append("[2j] preamble_ar should be ABSENT (not recovered this pass) rather than fabricated")

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: article_key not in source" % r["article_key"]); continue
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("title_ar") != a.get("title_ar"):
            e.append("[4] %s: title_ar mismatch" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[5] %s: article_key not in source" % r["article_key"]); continue
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS_UNCHANGED.lower():
            e.append("[5] %s: llm record bad source_status" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Air Quality Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation for Air Quality under the Environmental Law")
    print("  - 8 records: 8 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة (flat 8-article structure, titled)")
    print("  - DECISION NUMBER (the prior pass's open item) CONFIRMED from a PRIMARY source:")
    print("    القرار الوزاري رقم (512258/1/1442) وتاريخ 24/9/1442هـ -- cited verbatim in the")
    print("    Umm Al-Qura gazette's own Table-3-amendment-decision preamble (uqn.gov.sa);")
    print("    date (24 Ramadan 1442H = 6 May 2021) corroborated by saudipedia.com")
    print("  - VERIFICATION TIER: laws.boe.gov.sa checked first but unreachable this pass and")
    print("    with no dedicated lawId page; article TEXT dual-verified (~100% word match)")
    print("    between mewa.gov.sa (born-digital PDF, the issuing ministry) and qanoniah.com")
    print("  - Legal basis: Article 48 of the Environmental Law (M/165, 19/11/1441H)")
    print("  - SCOPE: only the 8 numbered articles are ingested; the violations/penalties")
    print("    Table 3 (37 rows; later amended by Decision 15029057, 04/02/1446H, which does")
    print("    NOT touch these 8 articles) and the 8 technical appendices (الملاحق 1-8) are")
    print("    documented as excluded tabular annexes (follow-up), per the food_regulation")
    print("    precedent")
    print("  - No repeal/supersession clause in the regulation text (confirmed negative)")
    print("  - Articles 5-6 retain genuine Latin technical terms (CEMS, RATA, USEPA Method, ...)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
