#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation for the Controls and Procedures
Related to the Financial Consideration (Fees) for Environmental Licenses, Permits and
Services track (4 records: 4 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة; no chapter division --
each of the 4 articles carries its own descriptive title; Annex (1) fee-ceiling table
disclosed but NOT ingested).

VERIFICATION TIER -- TIER_2 (lower end; identical layer to the qanoonsa.com /
food_regulation based sibling tracks). See the generator's module docstring and
sources/environmental_fees/official_source/environmental_fees_reg_official_source.json's
verification_methodology_note for the full account: laws.boe.gov.sa checked FIRST (no
dedicated lawId page); the Umm Al-Qura gazette portal is a SPA whose article text /
issue number could not be extracted this pass (issue number NOT confirmed, not
fabricated); PRIMARY TEXT source is qanoniah.com (non-government legal database
republishing the officially-published regulation), corroborated by qanoniah metadata
and by independent partial text cross-checks (ajel.sa Art 3; maaal/aleqt/mewa
summaries Arts 1 and 4). This validator does not re-adjudicate provenance; it checks
internal self-consistency of the ingested text and that every disclosed discrepancy
is still recorded.

NOTE on digits: unlike the gazette-verified sibling tracks, this track's source
(qanoniah) renders article headers and in-text numerals in Western digits (e.g.
"المادة (1)", "(0,8)", "(3)"). These are preserved verbatim (no glyph conversion), so
this validator ALLOWS Western digits while still forbidding Latin letters and HTML.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "environmental_fees", "official_source",
                   "environmental_fees_reg_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "environmental_fees", "verified",
                       "environmental_fees_reg_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "environmental_fees", "verified",
                       "environmental_fees_reg_verified_summary.json")
LLM = os.path.join(ROOT, "data", "environmental_fees_reg_arabic_legal_llm",
                   "environmental_fees_reg_legal_llm_001_004.json")
N = 4
KEY_RE = r"environmental_fees_reg_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 4, "معدلة": 0, "ملغاة": 0, "مضافة": 0}

STATUS_UNCHANGED = "UNCHANGED"
MUKARRAR_KEYS: set[str] = set()

FLAGGED_DISCREPANCY_KEYS = {
    "environmental_fees_reg_boe_no_dedicated_page",
    "environmental_fees_reg_gazette_text_not_extractable",
    "environmental_fees_reg_gazette_issue_number_unconfirmed",
    "environmental_fees_reg_annex1_fee_table_excluded",
    "environmental_fees_reg_annex1_ceiling_updates",
    "environmental_fees_reg_no_named_predecessor_repeal",
    "environmental_fees_reg_preamble_not_recovered",
    "environmental_fees_reg_source_digit_glyphs",
    "environmental_fees_reg_art2_ascii_comma",
}
AR = "ء-ي"

# Expected article titles (descriptive) -- anchors the 4-article structure this pass.
EXPECTED_TITLES = {
    1: "التعريفات",
    2: "نطاق عمل المركز المختص بشأن المقابل المالي",
    3: "المقابل المالي للتصاريح أو التراخيص أو الخدمات البيئية",
    4: "المقابل المالي للتصريح البيئي للتشغيل",
}


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
        e.append("[1] article_count field != %d" % N)
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)

    # No chapter division -- assert the source did not fabricate one.
    if "chapter_structure" in src:
        e.append("[1c] chapter_structure must be ABSENT (this regulation has no فصول/أبواب; "
                 "each of the 4 articles carries its own descriptive title)")
    if not src.get("structure_note"):
        e.append("[1c] missing structure_note documenting the no-chapters / titled-articles structure")

    # Annex (1) fee-ceiling table must be DOCUMENTED as excluded, not ingested.
    if src.get("annex_count") != 1:
        e.append("[1a] annex_count must be 1 (Annex (1) fee-ceiling table, documented-not-ingested)")
    ann = src.get("annex_structure") or []
    if len(ann) != 1 or "الملحق (1)" not in (ann[0].get("label_ar", "") if ann else ""):
        e.append("[1a] annex_structure must document exactly Annex (1) الحدود القصوى")

    sc = Counter()
    for k, a in arts.items():
        n = int(re.match(KEY_RE, k).group(1))
        if a.get("status") != STATUS_UNCHANGED:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS_UNCHANGED, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section_status divergence" % k)
        # Latin letters and HTML are forbidden; Western DIGITS are allowed (source rendering).
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("title_ar"):
            e.append("[2] %s: missing title_ar" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present (justification kashida not stripped)" % k)
        if a.get("history"):
            e.append("[2i] %s: original article must have empty history[]" % k)
        if ls != "اصلية":
            e.append("[2] %s: all 4 articles must be اصلية this pass" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if re.search("[ً-ْٰ]", a["text"]) or re.search("[ً-ْٰ]", a.get("title_ar", "")):
            e.append("[2f] %s: residual tashkeel (harakat) not stripped" % k)
        # number label must be "المادة (N)" with the Western digit matching the article number
        exp_label = "المادة (%d)" % n
        if a.get("number_label_ar") != exp_label:
            e.append("[2n] %s: number_label_ar %r != expected %r"
                     % (k, a.get("number_label_ar"), exp_label))
        if EXPECTED_TITLES.get(n) and a.get("title_ar") != EXPECTED_TITLES[n]:
            e.append("[2t] %s: title_ar %r != verified %r" % (k, a.get("title_ar"), EXPECTED_TITLES[n]))

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
        e.append("[2k] missing amendment_history (must record the founding decision)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "618660/1/1442" not in decrees:
            e.append("[2k] amendment_history must reference founding decision 618660/1/1442")

    if not src.get("supersession_finding_ar"):
        e.append("[2s] missing supersession_finding_ar (negative finding must be recorded)")

    # This track deliberately has NO verbatim preamble (not recovered; avoid fabrication).
    if src.get("preamble_ar"):
        e.append("[2p] preamble_ar must be ABSENT this pass (no verbatim issuing-decision "
                 "preamble was recovered; must not be fabricated)")

    # spot-checks anchoring key facts established this pass
    a1 = arts.get("environmental_fees_reg_art_001", {})
    if "المركز الوطني للرقابة على الالتزام البيئي" not in a1.get("text", ""):
        e.append("[2j] Article 1 missing expected definition of المركز المختص")
    if "معامل التأثير البيئي" not in a1.get("text", ""):
        e.append("[2j] Article 1 missing expected definition of معامل التأثير البيئي")
    a3 = arts.get("environmental_fees_reg_art_003", {})
    if "الحدود القصوى المحددة في الملحق" not in a3.get("text", ""):
        e.append("[2j] Article 3 missing expected reference to the Annex-1 maximum ceilings")
    a4 = arts.get("environmental_fees_reg_art_004", {})
    if "الأثر البيئي التراكمي" not in a4.get("text", ""):
        e.append("[2j] Article 4 missing expected 'cumulative environmental impact' clause")
    if "معامل التأثير البيئي لنوع النشاط" not in a4.get("text", ""):
        e.append("[2j] Article 4 missing expected annual-fee formula terms")

    if src.get("decree") != "قرار وزير البيئة والمياه والزراعة رقم (618660/1/1442)" \
            or src.get("decree_date_hijri") != "5/12/1442":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Minister Decision "
                 "618660/1/1442, 5/12/1442H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (all 4 articles original)")
    if src.get("base_law_track_key") != "environmental":
        e.append("[2j] base_law_track_key must be 'environmental' (companion to the ingested "
                 "Environmental Law track)")

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
    if summary.get("annex_count") != src.get("annex_count"):
        e.append("[4b] summary annex_count != source annex_count")

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    if llm.get("article_range") != [1, 4]:
        e.append("[5] llm article_range must be [1, 4]")
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
        print("FAIL: %d error(s) in Environmental Fees Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation for the Financial Consideration (Fees) for "
          "Environmental Licenses, Permits and Services")
    print("  - 4 records: 4 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة (no chapter division; each article titled)")
    print("  - Annex (1) الحدود القصوى (fee-ceiling table) DISCLOSED but NOT ingested (tabular; "
          "content unavailable as text -- not fabricated)")
    print("  - VERIFICATION TIER: TIER_2 (lower end; same layer as the qanoonsa/food_regulation")
    print("    siblings). laws.boe.gov.sa checked first -- no dedicated lawId page. Umm Al-Qura")
    print("    gazette portal is a SPA (article text / issue number not extractable this pass;")
    print("    issue number NOT confirmed, not fabricated). PRIMARY TEXT source: qanoniah.com")
    print("    (api.qanoniah.com/v1/files/ZAgjkrdaJVnNZDRnz8wW1mQ4E), metadata-corroborated;")
    print("    citation cross-verified across many sources; text partially cross-verified")
    print("    (ajel.sa Art 3; maaal/aleqt/mewa summaries Arts 1 and 4)")
    print("  - Minister of Environment Decision No. (618660/1/1442), 05/12/1442H, under the")
    print("    Environmental Law (Royal Decree M/165, 19/11/1441H) -- companion to environmental_law")
    print("  - REPEAL/SUPERSESSION: negative finding -- generic conflict-repeal clause only, no")
    print("    named predecessor; no later replacing/amending decision found (Annex-1 ceiling")
    print("    administrative updates per Arts 3-4 disclosed as out of scope)")
    print("  - Source digit glyphs / punctuation preserved verbatim (Western digits, e.g. (0,8)/(1.2));")
    print("    verbatim issuing-decision preamble deliberately omitted (not recovered -- no fabrication)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
