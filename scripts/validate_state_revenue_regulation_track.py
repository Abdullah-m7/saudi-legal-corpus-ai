#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the State Revenue Law
track (65 records across 6 chapters; 60 اصلية / 4 معدلة / 1 مضافة / 0 ملغاة;
0 مكرر articles -- Ministerial Resolution 901's inserted Article 47 used a
full clean renumbering instead of this corpus's usual مكرر convention).

VERIFICATION TIER -- see the generator's module docstring and
sources/state_revenue_regulation/law/official_source/
state_revenue_regulation_official_source.json's verification_methodology_note
for the full account: PRIMARY source is mof.gov.sa's own official PDF
(direct HTTP 200 fetch), transcribed by direct visual reading of every
rendered page (not automated OCR/text-extraction); Articles 1-8 additionally
cross-verified word-for-word against qanoniah.com's independent API;
Articles 9-65 rest on the MOF PDF alone. This validator does not re-
adjudicate provenance; it checks internal self-consistency of the text this
track ingests and that every discrepancy is still recorded.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "state_revenue_regulation", "law", "official_source",
                   "state_revenue_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "state_revenue_regulation", "law", "verified",
                       "state_revenue_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "state_revenue_regulation", "law", "verified",
                       "state_revenue_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "state_revenue_regulation_arabic_legal_llm",
                   "state_revenue_regulation_legal_llm_001_065.json")
N = 65
KEY_RE = r"state_revenue_regulation_art_(\d{3})(_mukarrar)?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 60, "معدلة": 4, "مضافة": 1, "ملغاة": 0}
STATUS_CROSS = "MOF_OFFICIAL_PDF_DIRECT_X_QANONIAH_API_CROSS_VERIFIED"
STATUS_PRIMARY = "MOF_OFFICIAL_PDF_DIRECT_SINGLE_SOURCE_VISUALLY_VERIFIED"
AMENDED_KEYS = {"state_revenue_regulation_art_046", "state_revenue_regulation_art_049",
                "state_revenue_regulation_art_052", "state_revenue_regulation_art_056"}
ADDED_KEYS = {"state_revenue_regulation_art_047"}
CROSS_VERIFIED_ARTS = {1, 2, 3, 4, 5, 6, 7, 8}
FLAGGED_DISCREPANCY_KEYS = {
    "state_revenue_regulation_ncar_gov_sa_unreachable",
    "state_revenue_regulation_adf_uqn_unreachable",
    "state_revenue_regulation_partial_cross_verification_arts_9_65",
    "state_revenue_regulation_original_1432h_text_gap",
    "state_revenue_regulation_901_date_qanoniah_tag_discrepancy",
    "state_revenue_regulation_no_specific_repealed_predecessor",
    "state_revenue_regulation_amendment_scope_completeness_assumption",
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
        if k.endswith("_mukarrar"):
            e.append("[1] %s: no مكرر articles expected in this track (901 used full "
                     "renumbering)" % k)
    for k in AMENDED_KEYS | ADDED_KEYS:
        if k not in arts:
            e.append("[1] expected article key %s missing" % k)

    if src.get("numbered_articles_max") != 65:
        e.append("[1b] numbered_articles_max != 65")
    if src.get("mukarrar_article_keys") not in ([], None):
        e.append("[1b] mukarrar_article_keys should be empty, got %r" % src.get("mukarrar_article_keys"))
    if src.get("original_issuance_article_count_1432h") != 64:
        e.append("[1c] original_issuance_article_count_1432h != 64 (SPA 2011 announcement)")

    chaps = src.get("chapter_structure") or []
    if len(chaps) != 6:
        e.append("[1d] expected 6 chapters, got %d" % len(chaps))
    else:
        total_span = 0
        for c in chaps:
            a, b = [int(x) for x in c["articles"].split("-")]
            total_span += (b - a + 1)
        if total_span != N:
            e.append("[1d] chapter article ranges do not sum to %d (got %d)" % (N, total_span))

    if src.get("decree") != "القرار الوزاري رقم (860)":
        e.append("[0] unexpected decree citation: %r" % src.get("decree"))
    if src.get("decree_date_hijri") != "13/3/1432":
        e.append("[0] unexpected decree date: %r" % src.get("decree_date_hijri"))
    if src.get("amending_decree_date_hijri") != "24/2/1439":
        e.append("[0] unexpected amending decree date: %r" % src.get("amending_decree_date_hijri"))

    repealed = src.get("repealed_predecessor") or {}
    if repealed.get("confirmed") is not False:
        e.append("[0b] repealed_predecessor.confirmed must be False (Article 64 is a generic, "
                 "non-specific repeal clause -- honestly unconfirmed, not fabricated)")

    sc = Counter()
    for k, a in arts.items():
        m = re.match(KEY_RE, k)
        n = int(m.group(1))
        expected_status = STATUS_CROSS if n in CROSS_VERIFIED_ARTS else STATUS_PRIMARY
        if a.get("status") != expected_status:
            e.append("[2] %s: expected status %r, got %r" % (k, expected_status, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (chapter assignment)" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if k in ADDED_KEYS and not a.get("history"):
            e.append("[2] %s: added (مضافة) article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if a.get("is_mukarrar"):
            e.append("[2] %s: is_mukarrar should be false in this track" % k)
        if a.get("original_1432h_text") is not None:
            e.append("[2] %s: original_1432h_text should be null (disclosed gap, not "
                     "fabricated)" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))

    # Article 47 (new) must reference Article 14 of the BASE law, not of this regulation.
    art47 = arts.get("state_revenue_regulation_art_047", {})
    if "الرابعة عشرة" not in art47.get("text", ""):
        e.append("[2f] state_revenue_regulation_art_047: expected cross-reference to "
                 "Article 14 (الرابعة عشرة) of the base state revenue law")
    if "نظام إيرادات الدولة" not in art47.get("text", ""):
        e.append("[2f] state_revenue_regulation_art_047: expected explicit reference to "
                 "نظام إيرادات الدولة (the base law) disambiguating it from this "
                 "regulation's own Article 14")

    # Article 49 must carry the confirmed new subsection 49-9.
    art49 = arts.get("state_revenue_regulation_art_049", {})
    if "49 - 9" not in art49.get("text", "") and "49-9" not in art49.get("text", ""):
        e.append("[2g] state_revenue_regulation_art_049: expected subsection 49-9 "
                 "(وزارة الداخلية) in the current text")

    # Article 56 must carry the confirmed new subsection 56-10 (notary referral).
    art56 = arts.get("state_revenue_regulation_art_056", {})
    if "كتابة العدل" not in art56.get("text", ""):
        e.append("[2h] state_revenue_regulation_art_056: expected 56-10's reference to "
                 "كتابة العدل (notary office)")

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

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts.get(r["article_key"])
        if a is None:
            e.append("[4] %s: not found in source articles" % r["article_key"])
            continue
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("original_1432h_text") != a.get("original_1432h_text"):
            e.append("[4] %s: original_1432h_text not propagated" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    summ = json.load(open(SUMMARY, encoding="utf-8"))
    if summ.get("record_count") != N:
        e.append("[5] summary record_count != %d" % N)
    if not summ.get("known_unresolved_discrepancies"):
        e.append("[5] summary missing known_unresolved_discrepancies")
    if summ.get("mukarrar_article_keys") not in ([], None):
        e.append("[5] summary mukarrar_article_keys should be empty")

    llm = json.load(open(LLM, encoding="utf-8"))
    if llm.get("record_count") != N or len(llm.get("records", [])) != N:
        e.append("[6] LLM-ready layer record_count/records length != %d" % N)
    else:
        for rec in llm["records"]:
            if not rec.get("article_text_hash_sha256"):
                e.append("[6] %s: missing article_text_hash_sha256 in LLM layer" % rec.get("article_key"))
            for f in ("translation_performed", "legal_interpretation_performed",
                      "english_used_for_correction", "text_summarized_or_paraphrased"):
                if rec.get(f) is not False:
                    e.append("[6] %s: %s must be False in LLM layer" % (rec.get("article_key"), f))
    if not llm.get("not_legal_advice"):
        e.append("[6] LLM-ready layer missing not_legal_advice=true")

    if e:
        print("FAIL: %d error(s) in State Revenue Regulation track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: State Revenue Regulation -- 65 records (60 اصلية / 4 معدلة / 1 مضافة,")
    print("  6 chapters, 0 مكرر articles)")
    print("  - DISTINCT TIER: mof.gov.sa official PDF direct-fetched and visually")
    print("    transcribed page-by-page; Articles 1-8 cross-verified against qanoniah.com's")
    print("    API; Articles 9-65 single-source (MOF PDF only), disclosed as such")
    print("  - Ministerial Resolution 860 (13/3/1432H), amended by Resolution 901")
    print("    (24/2/1439H) -- confirmed touching Articles 46, 47 (new), 49, 52, 56")
    print("  - Article 47 (new) is the confirmed cause of the 64-to-65 article-count")
    print("    change versus the original 1432H issuance")
    print("  - ncar.gov.sa, adf.gov.sa, and uqn.gov.sa could not be directly fetched")
    print("    this pass; original pre-901 wording of 4 amended articles undisclosed/")
    print("    unrecoverable this pass; both honestly disclosed, not fabricated")
    print("  - Article 64 is a generic repeal clause; no specific named predecessor")
    print("    regulation was confirmed repealed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
