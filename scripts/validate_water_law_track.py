#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Water Law track (77 records: 77
اصلية, 0 معدلة, 0 ملغاة, 0 مضافة; 17 chapters فصول).

VERIFICATION TIER -- see the generator's module docstring and
sources/water/law/official_source/water_law_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa DOES have
a dedicated lawId page for this law (57261279-94b7-4ddc-8ad2-abf100d246be) but
it was unreachable this pass both live (HTTP 503 / connection reset) and via
Wayback Machine (a confirmed-existing snapshot at web.archive.org is
egress-policy-blocked HTTP 403 and was NOT bypassed). Full text is from
nezams.com (an independent aggregator, HTTP 200), whose own metadata states the
law has had NO amendments; the decree identity, Article 74's verbatim text, the
SAR-20m penalty ceiling and the 17-chapter structure were independently
confirmed via WebSearch indexing of BOE's own content -> TIER_3. This validator
does not re-adjudicate any of this; it only checks internal self-consistency of
the text this track ingests, and that every discrepancy is still recorded.

MATERIAL DISTINCTION preserved and checked: Article 75 EXPLICITLY repeals three
NAMED predecessor laws (M/22 1391H, M/34 1400H, M/6 1421H) -- NOT a generic
conflict-only clause (contrast health_system_law/food_law).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "water", "law", "official_source",
                   "water_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "water", "law", "verified",
                       "water_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "water", "law", "verified",
                       "water_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "water_arabic_legal_llm",
                   "water_law_legal_llm_001_077.json")
N = 77
KEY_RE = r"water_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 77, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 17  # 17 فصول

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED_DATED = "AMENDED_DATED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY: dict[str, str] = {}
FLAGGED_DISCREPANCY_KEYS = {
    "water_law_boe_dedicated_page_exists_but_unreachable",
    "water_law_named_repeal_of_three_predecessors",
    "water_law_two_implementing_regulations_out_of_scope",
    "water_law_cabinet_resolution_710_substantive_annex",
    "water_law_no_amendments_recorded",
    "water_law_tashkeel_stripped_divergence_from_health_system",
    "water_law_gregorian_date_not_pinpointed",
    "water_law_zamzam_scope_exclusion_preserved",
    "water_law_art44_source_typo_preserved",
    "water_law_distinct_from_environmental_track",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰٕٓٔ]")


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        if (re.match("[%s]" % AR, before) and before != "ه"
                and re.match("[%s]" % AR, after)):
            bad += 1
    return bad


def _iter_chapter_ranges(chs):
    for ch in chs:
        lo, hi = (int(x) for x in ch["articles"].split("-"))
        yield (lo, hi)


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

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapters (فصول), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one chapter range" % n)
            covered.add(n)
    if covered != set(range(1, N + 1)):
        missing = sorted(set(range(1, N + 1)) - covered)
        extra = sorted(covered - set(range(1, N + 1)))
        if missing:
            e.append("[1c] chapter_structure missing article(s): %s" % missing[:20])
        if extra:
            e.append("[1c] chapter_structure covers out-of-range article(s): %s" % extra[:20])

    # every chapter title should be distinct here (no disclosed duplicate anomaly)
    titles = [c.get("title_ar") for c in chs]
    if len(set(titles)) != len(titles):
        e.append("[1d] unexpected duplicate chapter title(s): %s"
                 % [t for t in titles if titles.count(t) > 1])

    sc = Counter()
    for k, a in arts.items():
        expected_status = EXPECTED_STATUS_BY_KEY.get(k, STATUS_UNCHANGED)
        if a.get("status") != expected_status:
            e.append("[2] %s: expected status %r, got %r" % (k, expected_status, a.get("status")))
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
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly "
                     "-- see known_unresolved_discrepancies)" % k)
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
        if "title_ar" in a:
            e.append("[2i] %s: unexpected title_ar key present (this law's source supplies no "
                     "inline per-article titles -- section_ar carries the chapter title)" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected (should be normalized "
                     "to straight quotes)" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)

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
        if "م/159" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/159")

    # spot-checks anchoring key facts established this pass
    art1 = arts.get("water_law_art_001", {})
    if "المقنن المائي" not in art1.get("text", "") or "نشاط تقديم الخدمة" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (المقنن المائي / نشاط تقديم الخدمة)")
    art3 = arts.get("water_law_art_003", {})
    if "زمزم" not in art3.get("text", ""):
        e.append("[2j] Article 3 missing expected Zamzam scope-exclusion")
    art8 = arts.get("water_law_art_008", {})
    if "ملكا عاما" not in art8.get("text", ""):
        e.append("[2j] Article 8 missing expected 'water is public property' rule")
    art75 = arts.get("water_law_art_075", {})
    t75 = art75.get("text", "")
    if "يلغي النظام الآتي" not in t75:
        e.append("[2j] Article 75 missing expected explicit repeal clause header")
    for token in ("م/22", "م/34", "م/6"):
        if token not in t75:
            e.append("[2j] Article 75 must name repealed predecessor decree %s" % token)
    # the named-repeal distinction: Article 75 must NOT be a generic conflict-only clause
    if "كل ما يتعارض" in t75:
        e.append("[2j] Article 75 unexpectedly contains a generic conflict-only clause "
                 "(this law's repeal is by NAMED instrument, per the disclosed distinction)")
    art44 = arts.get("water_law_art_044", {})
    if "على أت تراعي" not in art44.get("text", ""):
        e.append("[2j] Article 44's verbatim source typo ('على أت تراعي') must be preserved, "
                 "not silently corrected to 'أن' -- see known_unresolved_discrepancies")
    art76 = arts.get("water_law_art_076", {})
    if "اللائحة التنفيذية" not in art76.get("text", ""):
        e.append("[2j] Article 76 missing expected implementing-regulation mandate")
    art77 = arts.get("water_law_art_077", {})
    if "تسعين" not in art77.get("text", ""):
        e.append("[2j] Article 77 missing expected 90-day effective-date clause")

    if src.get("decree") != "المرسوم الملكي رقم م/159" or src.get("decree_date_hijri") != "11/11/1441":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/159, 11/11/1441H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (this law has NO recorded amendments)")
    pre = src.get("preamble_ar", "")
    if not pre or "710" not in pre or "نظام المياه" not in pre:
        e.append("[2j] preamble_ar must be present and reference the founding decree context "
                 "(CoM Resolution 710 and نظام المياه)")

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
            e.append("[5] %s: article_key not found in source" % r["article_key"]); continue
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        expected_status = EXPECTED_STATUS_BY_KEY.get(r["article_key"], STATUS_UNCHANGED)
        if r.get("source_trust", {}).get("source_status") != expected_status.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Water Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Saudi Arabian Water Law")
    print("  - 77 records: 77 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (no amendments recorded)")
    print("  - 17 chapters (فصول), continuous 1-77; no inline per-article titles (spelled-ordinal")
    print("    labels, no title_ar key; section_ar carries each article's chapter title)")
    print("  - VERIFICATION TIER: TIER_3 -- laws.boe.gov.sa HAS a dedicated lawId page")
    print("    (57261279-94b7-4ddc-8ad2-abf100d246be) but was unreachable this pass (live HTTP 503;")
    print("    the confirmed Wayback snapshot is egress-policy-blocked HTTP 403 at web.archive.org")
    print("    and was NOT bypassed). Full text from nezams.com (independent aggregator, HTTP 200);")
    print("    decree identity, Article 74 verbatim text, SAR-20m penalty ceiling and 17-chapter")
    print("    structure independently confirmed via WebSearch indexing of BOE's own content")
    print("  - Royal Decree M/159 (11/11/1441H, ~July 2020G), approved via Council of Ministers")
    print("    Resolution 710 (9/11/1441H); administered by MEWA and the Electricity & Cogeneration")
    print("    Regulatory Authority (service-provision activities)")
    print("  - PREDECESSOR REPEAL: EXPLICIT and NAMED (material distinction from health_system_law/")
    print("    food_law generic clauses) -- Article 75 repeals نظام مصالح المياه والصرف الصحي")
    print("    (M/22, 1391H), نظام المحافظة على مصادر المياه (M/34, 1400H), and نظام مياه الصرف")
    print("    الصحي المعالجة وإعادة استخدامها (M/6, 1421H), each with its regulations")
    print("  - Companion instruments identified but NOT ingested this pass (one-instrument-per-pass):")
    print("    TWO implementing regulations (Minister's + Authority's board, Article 76; a MEWA/FAOLEX")
    print("    PDF was confirmed to exist) and the Saudi Water Code (الكود السعودي لمصادر المياه)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
