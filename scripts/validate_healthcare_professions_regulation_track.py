#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Law of
Practicing Healthcare Professions track (اللائحة التنفيذية لنظام مزاولة
المهن الصحية; 30 records, all اصلية -- base-law articles 6, 13, 21, 24,
26-32, 34, 42 and 43 intentionally absent, no regulation content in this
edition; hierarchical فصل/فرع structure inherited from the base law).

VERIFICATION TIER -- see the generator's module docstring and sources/
healthcare_professions_regulation/law/official_source/healthcare_professions_
regulation_official_source.json's verification_methodology_note for the full
account: the founding ministerial resolution is NOT confirmed (an
independently-located 2011/1432H edition predates the 4080489/1439H
resolution printed on this track's primary source, implying 4080489 is a
re-issuance, not the founding instrument). Primary text: an official MOH PDF,
byte-verified via Wayback Machine and a third-party mirror; cross-checked
against a second, independently-produced MOH export -> TIER_2. This
validator does not re-adjudicate provenance; it only checks internal
self-consistency and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "healthcare_professions_regulation", "law", "official_source",
                   "healthcare_professions_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "healthcare_professions_regulation", "law", "verified",
                       "healthcare_professions_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "healthcare_professions_regulation", "law", "verified",
                       "healthcare_professions_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "healthcare_professions_regulation_arabic_legal_llm",
                   "healthcare_professions_regulation_legal_llm_001_030.json")

N = 30
NO_REG = {6, 13, 21, 24, 26, 27, 28, 29, 30, 31, 32, 34, 42, 43}
EXPECTED_LAW_ARTICLE_NUMBERS = [n for n in range(1, 45) if n not in NO_REG]
KEY_RE = r"healthcare_professions_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 30, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()

FLAGGED_DISCREPANCY_KEYS = {
    "healthcare_professions_regulation_founding_resolution_uncertain",
    "healthcare_professions_regulation_edition_diff_not_exhaustive",
    "healthcare_professions_regulation_font_cmap_lam_alef_defect",
    "healthcare_professions_regulation_art035_footnote_excised",
    "healthcare_professions_regulation_trailing_heading_scrape_boundary",
    "healthcare_professions_regulation_no_regulation_for_14_articles",
    "healthcare_professions_regulation_boe_ncar_qanoniah_not_confirmed_live",
}

# chapter/فرع membership expected for each base-law article number (reused
# from the base healthcare_professions_law track's own validator)
CHAPTER_RANGES = [
    (1, 4, "الفصل الأول", None),
    (5, 14, "الفصل الثاني", "الفرع الأول"),
    (15, 23, "الفصل الثاني", "الفرع الثاني"),
    (24, 25, "الفصل الثاني", "الفرع الثالث"),
    (26, 27, "الفصل الثالث", "الفرع الأول"),
    (28, 30, "الفصل الثالث", "الفرع الثاني"),
    (31, 32, "الفصل الثالث", "الفرع الثالث"),
    (33, 41, "الفصل الرابع", None),
    (42, 44, "الفصل الخامس", None),
]
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰٕٓٔ]")


def _expected_chapter_fragment(n):
    for lo, hi, chapter, section in CHAPTER_RANGES:
        if lo <= n <= hi:
            return chapter, section
    return None, None


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

    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != EXPECTED_LAW_ARTICLE_NUMBERS:
        e.append("[1b] article numbers not the expected gapped set: got %s" % nums)
    for missing in sorted(NO_REG):
        key = "healthcare_professions_regulation_art_%03d" % missing
        if key in arts:
            e.append("[1c] %s should NOT exist (base-law article %d has no regulation "
                     "content in this edition)" % (key, missing))
    if set(src.get("no_regulation_content_law_articles", [])) != NO_REG:
        e.append("[1c] no_regulation_content_law_articles field does not match expected set")

    chs = src.get("chapter_structure") or []
    if not chs:
        e.append("[1d] expected non-empty chapter_structure (inherited from base law)")
    covered = set()
    for ch in chs:
        lo, hi = (int(x) for x in ch["articles"].split("-"))
        for n in range(lo, hi + 1):
            covered.add(n)
        for sec in ch.get("sections", []):
            slo, shi = (int(x) for x in sec["articles"].split("-"))
            if slo < lo or shi > hi:
                e.append("[1d] section %s outside parent chapter range" % sec.get("label_ar"))
    if covered != set(range(1, 45)):
        e.append("[1d] chapter_structure must cover all 44 base-law articles (30 with "
                 "regulation content + 14 without); got coverage %s" % sorted(covered))

    sc = Counter()
    for k, a in arts.items():
        m = re.match(KEY_RE, k)
        n = int(m.group(1))
        if n in NO_REG:
            e.append("[2] %s: article %d should have no regulation record" % (k, n))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected structure/section_status divergence" % k)
        if a.get("status") != src.get("verification_tier") and not str(a.get("status", "")).strip():
            e.append("[2] %s: empty verification status string" % k)
        if not a["text"].strip() or re.search(r"[<>&]", a["text"]):
            e.append("[2] %s: empty text or html leftovers" % k)
        if re.search(r"(?<![0-9])[A-Za-z](?![0-9])", a["text"]):
            e.append("[2] %s: unexpected latin leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if a.get("history"):
            e.append("[2i] %s: no article in this track has amendment history yet" % k)
        # section_ar cross-check against the inherited chapter_structure
        exp_chapter, exp_section = _expected_chapter_fragment(n)
        sec_ar = a.get("section_ar", "")
        if exp_chapter and exp_chapter not in sec_ar:
            e.append("[2f] %s: section_ar %r missing expected chapter %r" % (k, sec_ar, exp_chapter))
        if exp_section and exp_section not in sec_ar:
            e.append("[2f] %s: section_ar %r missing expected فرع %r" % (k, sec_ar, exp_section))
        # known font-defect leftovers that must NOT have leaked back into the adopted text
        for bad_word in ("عاقة", "عاج ", "ثاث", "الائحة", "الازم", "الاوصفية"):
            if bad_word in a["text"]:
                e.append("[2i] %s: un-normalized lam-alef font-defect leftover %r present"
                         % (k, bad_word))
        if "تطلق كلمة" in a["text"] or " ا ع ع ا " in a["text"]:
            e.append("[2i] %s: article-35 footnote-splice artifact leaked into adopted text" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

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

    # honesty gate: founding resolution must not be asserted as confirmed
    if src.get("founding_resolution_confirmed") is not False:
        e.append("[2g] founding_resolution_confirmed must be False (not independently "
                 "confirmed this pass)")
    if src.get("preamble_ar") not in ("", None):
        e.append("[2l] preamble_ar must be empty -- no resolution preamble/enacting text "
                 "was located this pass; a non-empty value would risk fabrication")
    if src.get("verification_tier") != "TIER_2":
        e.append("[2g] verification_tier must be TIER_2")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True")
    if "4080489" not in str(src.get("decree", "")):
        e.append("[2j] decree field must reference Ministerial Resolution 4080489")

    ah = src.get("amendment_history")
    if not ah:
        e.append("[2k] missing amendment_history")

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
        if r.get("legal_status_ar") != a.get("legal_status_ar"):
            e.append("[4] %s: legal_status_ar mismatch" % r["article_key"])
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation'" % r["article_key"])
        if r.get("law_article_number") != a.get("law_article_number"):
            e.append("[4] %s: law_article_number mismatch" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    if summary.get("record_count") != N:
        e.append("[4b] summary record_count != %d" % N)
    if summary.get("status_counts") != src["status_counts"]:
        e.append("[4b] summary status_counts != source status_counts")
    if summary.get("founding_resolution_confirmed") is not False:
        e.append("[4b] summary founding_resolution_confirmed must be False")

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
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation'" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != a["status"].lower():
            e.append("[5] %s: llm record source_status mismatch in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Healthcare Professions Regulation track:" % len(e))
        for x in e[:60]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Law of Practicing Healthcare Professions")
    print("  - 30 records (of 44 possible base-law article numbers -- 14 intentionally absent:")
    print("    6, 13, 21, 24, 26-32, 34, 42, 43; no regulation content in this edition), all اصلية")
    print("  - hierarchical فصل/فرع structure inherited from the base law (5 chapters, ch.2/3")
    print("    each subdivided into 3 فرع sections)")
    print("  - VERIFICATION TIER: TIER_2 -- primary official MOH PDF, byte-verified via Wayback")
    print("    Machine + a third-party mirror; cross-checked against a second, independently-")
    print("    produced MOH export explicitly labelled 3rd edition 1440H/2019")
    print("  - FOUNDING RESOLUTION NOT CONFIRMED -- an independently-located 2011/1432H edition")
    print("    predates the 4080489/1439H resolution printed on this track's primary source,")
    print("    implying 4080489 is a re-issuance/consolidation, not the founding instrument")
    print("  - laws.boe.gov.sa and ncar.gov.sa both unreachable this pass for a live")
    print("    first-party confirmation of this specific regulation record")
    return 0


if __name__ == "__main__":
    sys.exit(main())
