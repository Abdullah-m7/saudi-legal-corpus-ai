#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Saudi Anti-
Smoking Law track (اللائحة التنفيذية لنظام مكافحة التدخين; 17 records: 11
اصلية, 6 معدلة, 0 ملغاة, 0 مضافة -- base-law Articles 14/15/17 intentionally
absent since neither edition examined gives them regulation content; FLAT
regulation -- no chapters/أبواب of its own).

VERIFICATION TIER -- see the generator's module docstring and sources/
anti_smoking_regulation/law/official_source/anti_smoking_regulation_official_
source.json's verification_methodology_note for the full account: the
founding ministerial resolution's number/date are NOT confirmed (explicitly
correcting a prior pass that treated Resolution 797557/1441H as the founding
issuance -- independent verification this pass shows 797557 is a later
AMENDMENT resolution instead). Primary text: an official MOH PDF ("3rd
edition, 2019"), vision-read in full. Cross-check: a 2017 WHO/EMRO-hosted
edition, diffed clause-by-clause to detect the 6 amended articles ->
TIER_2. This validator does not re-adjudicate provenance; it only checks
internal self-consistency and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "anti_smoking_regulation", "law", "official_source",
                   "anti_smoking_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "anti_smoking_regulation", "law", "verified",
                       "anti_smoking_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "anti_smoking_regulation", "law", "verified",
                       "anti_smoking_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "anti_smoking_regulation_arabic_legal_llm",
                   "anti_smoking_regulation_legal_llm_001_020.json")
N = 17
EXPECTED_LAW_ARTICLE_NUMBERS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 18, 19, 20]
MISSING_BY_DESIGN = {14, 15, 17}
KEY_RE = r"anti_smoking_regulation_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 11, "معدلة": 6, "ملغاة": 0, "مضافة": 0}

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
AMENDED_KEYS = {"anti_smoking_regulation_art_002", "anti_smoking_regulation_art_003",
                "anti_smoking_regulation_art_005", "anti_smoking_regulation_art_006",
                "anti_smoking_regulation_art_007", "anti_smoking_regulation_art_008"}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
FLAGGED_DISCREPANCY_KEYS = {
    "anti_smoking_regulation_founding_resolution_not_confirmed",
    "anti_smoking_regulation_797557_confirmed_as_amendment_not_founding",
    "anti_smoking_regulation_six_articles_confirmed_amended_via_2017_2019_diff",
    "anti_smoking_regulation_boe_no_dedicated_page",
    "anti_smoking_regulation_uqn_qanoniah_nctc_inaccessible",
    "anti_smoking_regulation_preamble_not_available",
    "anti_smoking_regulation_articles_14_15_17_no_regulation_content",
    "anti_smoking_regulation_art004_missing_number_label_in_2019_source",
    "anti_smoking_regulation_art008_trailing_text_artifact",
    "anti_smoking_regulation_moh_pdf_pdftotext_extraction_failure_visual_reading_used",
    "anti_smoking_regulation_who_pdf_no_explicit_edition_label",
    "anti_smoking_regulation_tashkeel_stripped",
    "anti_smoking_regulation_moh_pdf_metadata_date_discrepancy",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰٕٓٔ]")


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

    # Deliberately gapped: only the specific base-law article numbers that carry
    # regulation content (14, 15, 17 intentionally absent -- see discrepancy).
    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != EXPECTED_LAW_ARTICLE_NUMBERS:
        e.append("[1b] article numbers not the expected gapped set %s: got %s"
                 % (EXPECTED_LAW_ARTICLE_NUMBERS, nums))
    for missing in MISSING_BY_DESIGN:
        key = "anti_smoking_regulation_art_%03d" % missing
        if key in arts:
            e.append("[1c] %s should NOT exist (base-law article %d has no regulation "
                     "content in either edition examined)" % (key, missing))

    # FLAT regulation: chapter_structure MUST be empty (no separate باب structure)
    chs = src.get("chapter_structure")
    if chs != []:
        e.append("[1d] this regulation is flat; chapter_structure must be [] but is %r"
                 % (chs,))

    sc = Counter()
    for k, a in arts.items():
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
        if not a.get("verification_tier"):
            e.append("[2] %s: missing verification_tier" % k)
        if not a["text"].strip() or re.search(r"[<>&]", a["text"]):
            e.append("[2] %s: empty text or html leftovers" % k)
        if re.search(r"(?<![0-9])[A-Za-z](?![0-9])", a["text"]) and "WG" not in a["text"]:
            e.append("[2] %s: unexpected latin leftovers" % k)
        # FLAT regulation: section_ar MUST be empty for every article
        if a.get("section_ar") != "":
            e.append("[2] %s: section_ar must be empty for this flat regulation" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment history" % k)
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

    # Honesty gate: this track must NOT assert the founding resolution is confirmed,
    # and must NOT silently repeat the prior pass's 797557-as-founding mistake.
    if src.get("founding_resolution_confirmed") is not False:
        e.append("[2g] founding_resolution_confirmed must be False (not independently "
                 "confirmed this pass)")
    decree_text = str(src.get("decree", ""))
    if "797557" in decree_text and "غير مؤكد" not in decree_text:
        e.append("[2g] decree field mentions 797557 without flagging founding-resolution "
                 "uncertainty")
    if not src.get("latest_confirmed_amendment_resolution_ar") or \
            "797557" not in src["latest_confirmed_amendment_resolution_ar"]:
        e.append("[2g] latest_confirmed_amendment_resolution_ar must reference 797557")

    ah = src.get("amendment_history")
    if not ah:
        e.append("[2k] missing amendment_history")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in ah)
        if "797557" not in decrees:
            e.append("[2k] amendment_history must reference the confirmed amendment "
                     "resolution 797557")

    if src.get("preamble_ar") not in ("", None):
        e.append("[2l] preamble_ar must be empty -- no resolution preamble/enacting text "
                 "was located this pass; a non-empty value would risk fabrication")

    # spot-checks anchoring key facts
    art7 = arts.get("anti_smoking_regulation_art_007", {}).get("text", "")
    for token in ("المساجد", "13.", "(10) متر"):
        if token not in art7:
            e.append("[2j] Article 7 missing expected token %r (current 2019 text: 13 "
                     "places incl. mosques, 10-meter buffer)" % token)
    if "(8) متر" in art7:
        e.append("[2j] Article 7 should carry the CURRENT (10m) buffer, not the 2017 (8m) "
                 "figure")
    art8 = arts.get("anti_smoking_regulation_art_008", {}).get("text", "")
    if "(250-500)" not in art8:
        e.append("[2j] Article 8 missing expected 250-500g weight range (current text)")
    art5 = arts.get("anti_smoking_regulation_art_005", {}).get("text", "")
    if "الهيئة العامة للغذاء والدواء" not in art5:
        e.append("[2j] Article 5 missing expected SFDA reference (current text)")
    art19 = arts.get("anti_smoking_regulation_art_019", {}).get("text", "")
    if "سنة" not in art19:
        e.append("[2j] Article 19 (regulation review clause) missing expected 1-year token")
    art20 = arts.get("anti_smoking_regulation_art_020", {}).get("text", "")
    if "الجريدة الرسمية" not in art20:
        e.append("[2j] Article 20 (publication clause) missing expected gazette token")

    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (6 articles carry confirmed "
                 "amendments relative to the 2017 baseline text)")

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
        if (r.get("is_amended")) != (r["article_key"] in AMENDED_KEYS):
            e.append("[4] %s: is_amended flag mismatch" % r["article_key"])
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
        print("FAIL: %d error(s) in Anti-Smoking Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Anti-Smoking Law (اللائحة التنفيذية لنظام مكافحة التدخين)")
    print("  - 17 records (of 20 possible base-law article numbers -- 14/15/17 intentionally")
    print("    absent, no regulation content in either edition examined): 11 اصلية, 6 معدلة")
    print("    (Articles 2, 3, 5, 6, 7, 8), 0 ملغاة, 0 مضافة")
    print("  - FLAT regulation relative to base law's own numbering (chapter_structure == [],")
    print("    section_ar empty by design)")
    print("  - VERIFICATION TIER: TIER_2 -- laws.boe.gov.sa has NO dedicated lawId page for")
    print("    this Implementing Regulation at all. PRIMARY full text from an official")
    print("    Ministry of Health PDF (\"3rd edition, 2019\"), vision-read in full; CROSS-")
    print("    CHECKED against a 2017 WHO/EMRO-hosted edition, diffed clause-by-clause to")
    print("    detect amendments")
    print("  - FOUNDING RESOLUTION NOT CONFIRMED (number/date unknown this pass) -- this")
    print("    corrects a prior pass's framing that had treated Ministerial Resolution No.")
    print("    797557 (1/5/1441H) as the founding issuance. Independent verification this")
    print("    pass confirms 797557/1441H as a real, well-corroborated AMENDMENT resolution")
    print("    instead (multiple independent sources), whose reported content (13-place")
    print("    smoking ban list, 10-meter buffer) matches the Article 7 change directly")
    print("    observed by diffing the 2017 and 2019 texts")
    print("  - 6 articles (2, 3, 5, 6, 7, 8) carry confirmed textual amendments vs. the 2017")
    print("    baseline; only Article 7's change is independently attributed by name to")
    print("    Resolution 797557 in a secondary news source")
    return 0


if __name__ == "__main__":
    sys.exit(main())
