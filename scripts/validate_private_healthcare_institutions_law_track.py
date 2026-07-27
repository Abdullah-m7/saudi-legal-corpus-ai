#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Private Healthcare Institutions Law
track (نظام المؤسسات الصحية الخاصة, Royal Decree M/40, 3/11/1423H -- the
currently in-force law governing ownership/licensing/operation of private
hospitals, clinics, medical complexes, laboratories, radiology centers and
other private health facilities; DISTINCT from health_system_law and
healthcare_professions_law already tracked elsewhere in this corpus).

35 records: 32 اصلية, 3 معدلة (Articles 2, 7, 14), 0 ملغاة, 0 مضافة. No
chapter/فصل or باب structure (confirmed via a full programmatic scan of the
source page finding zero occurrences of either word).

SUPERSESSION -- confirmed INSIDE the Law's own Article 33 (not merely the
issuing decree): "يحل هذا النظام محل نظام المؤسسات الطبية الخاصة الصادر
بالمرسوم الملكي ذي الرقم (م/58) والتاريخ 3/ 11/ 1407هـ."

VERIFICATION TIER -- TIER_3. See the generator docstring and the source
artifact's verification_methodology_note: laws.boe.gov.sa was checked FIRST but
is unreachable this pass (curl connection reset x3; WebFetch HTTP 503 x2;
web.archive.org refused/reset); the official moh.gov.sa PDF exists but is
scanned/unreadable without OCR, which was infeasible this pass. The verbatim
text of all 35 articles rests on nezams.com (primary working source) and
qanoonsa.com (independent secondary aggregator, verbatim Royal Decree text for
the Article 14 amendment) -- agreeing word-for-word wherever they overlap.
This validator does not re-adjudicate provenance; it only checks internal
self-consistency of the ingested text and that every discrepancy is still
recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "private_healthcare_institutions_law", "law", "official_source",
                   "private_healthcare_institutions_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "private_healthcare_institutions_law", "law", "verified",
                       "private_healthcare_institutions_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "private_healthcare_institutions_law", "law", "verified",
                       "private_healthcare_institutions_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "private_healthcare_institutions_law_arabic_legal_llm",
                   "private_healthcare_institutions_law_legal_llm_001_035.json")
N = 35
KEY_RE = r"private_healthcare_institutions_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 32, "معدلة": 3, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 0  # no فصول/أبواب in this law

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
AMENDED_KEYS = {
    "private_healthcare_institutions_law_art_002",
    "private_healthcare_institutions_law_art_007",
    "private_healthcare_institutions_law_art_014",
}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY = {}
for k in AMENDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_AMENDED
for k in ADDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_ADDED
FLAGGED_DISCREPANCY_KEYS = {
    "private_healthcare_institutions_law_boe_uqn_moh_pdf_unreachable_this_pass",
    "private_healthcare_institutions_law_m112_ratifying_decree_unverified",
    "private_healthcare_institutions_law_m103_article14_amendment_discovered_this_pass",
    "private_healthcare_institutions_law_implementing_regulation_not_ingested",
    "private_healthcare_institutions_law_predecessor_law_m58_supersession",
    "private_healthcare_institutions_law_article2_interim_1441_state_not_fully_reconstructed",
    "private_healthcare_institutions_law_tashkeel_and_quote_marks_normalized",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ٰٟ]")


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

    chs = src.get("chapter_structure") or []
    n_top = len(chs)
    if n_top != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d chapters (فصول/أبواب), got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, n_top))

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
        if a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section_status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if a.get("section_ar") not in ("", None):
            e.append("[2] %s: section_ar must be empty (no chapter structure in this law)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
        if any(c in a["text"] for c in "«»“”"):
            e.append("[2m] %s: residual decorative quotation mark present (must be stripped)" % k)
        if k in (AMENDED_KEYS | ADDED_KEYS) and not a.get("history"):
            e.append("[2] %s: amended/added article missing amendment_history" % k)
        if (ls == "معدلة") != (k in AMENDED_KEYS):
            e.append("[2] %s: legal_status_ar/AMENDED_KEYS membership mismatch" % k)
        if (ls == "مضافة") != (k in ADDED_KEYS):
            e.append("[2] %s: legal_status_ar/ADDED_KEYS membership mismatch" % k)
        if (ls == "ملغاة") != (k in REPEALED_KEYS):
            e.append("[2] %s: legal_status_ar/REPEALED_KEYS membership mismatch" % k)
        if bool(a.get("is_mukarrar")) != (k in MUKARRAR_KEYS):
            e.append("[2] %s: is_mukarrar/MUKARRAR_KEYS membership mismatch" % k)
        if k not in (AMENDED_KEYS | ADDED_KEYS) and a.get("history"):
            e.append("[2i] %s: non-amended/added article must have empty history[]" % k)
        if "\xa0" in a["text"]:
            e.append("[2f] %s: residual non-breaking-space artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2f] %s: residual Arabic-Indic digit (source uses Western digits only)" % k)
        if re.search(r"[کیے]", a["text"]):
            e.append("[2g] %s: non-standard Arabic-presentation letter (Farsi yeh/keheh) present" % k)

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
        e.append("[2k] missing amendment_history (must record the founding M/40 decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/40" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/40")
        for must in ("م/36", "م/78", "م/72", "479", "م/103"):
            if must not in decrees:
                e.append("[2k] amendment_history must reference amendment %s" % must)

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/40)" \
            or src.get("decree_date_hijri") != "3/11/1423":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/40, 3/11/1423H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False")
    sup = src.get("supersedes_ar", "")
    if not sup or "م/58" not in sup or "المادة الثالثة والثلاثون" not in sup:
        e.append("[2j] supersedes_ar must name the repealed instrument (م/58) and anchor the "
                 "repeal to Article 33 of this Law's own text")
    if not src.get("preamble_ar") or "3/ 11/ 1423" not in src.get("preamble_ar", "") \
            or "نظام المؤسسات الصحية الخاصة" not in src.get("preamble_ar", ""):
        e.append("[2j] preamble_ar (Royal Decree text) must be present and reference the "
                 "3/11/1423H decree date and نظام المؤسسات الصحية الخاصة")
    if not src.get("com_resolution_ar") or "قرار مجلس الوزراء" not in src.get("com_resolution_ar", ""):
        e.append("[2j] com_resolution_ar (CoM Resolution 240 full text) must be present")

    art2 = arts.get("private_healthcare_institutions_law_art_002", {})
    if "سعوديا" not in art2.get("text", "") or "المدير الطبي" not in art2.get("text", ""):
        e.append("[2j] Article 2 missing expected current-text markers (سعوديا / المدير الطبي)")
    art7 = arts.get("private_healthcare_institutions_law_art_007", {})
    if "أسعار الخدمات" not in art7.get("text", ""):
        e.append("[2j] Article 7 missing expected pricing markers (أسعار الخدمات)")
    art14 = arts.get("private_healthcare_institutions_law_art_014", {})
    if "طبيب نائب" not in art14.get("text", ""):
        e.append("[2j] Article 14 missing expected M/103 current-text marker (طبيب نائب)")
    art33 = arts.get("private_healthcare_institutions_law_art_033", {})
    if "يحل هذا النظام محل" not in art33.get("text", "") or "م/58" not in art33.get("text", ""):
        e.append("[2j] Article 33 missing expected supersession clause referencing م/58")
    art35 = arts.get("private_healthcare_institutions_law_art_035", {})
    if "ينشر هذا النظام" not in art35.get("text", ""):
        e.append("[2j] Article 35 missing expected publication clause")
    art35_label = art35.get("number_label_ar")
    if art35_label != "المادة الخامسة والثلاثون":
        e.append("[2j] Article 35 number_label_ar must be 'المادة الخامسة والثلاثون', got %r"
                 % art35_label)

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
        print("FAIL: %d error(s) in Private Healthcare Institutions Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Arabian Private Healthcare Institutions Law (نظام المؤسسات الصحية الخاصة)")
    print("  - 35 records: 32 اصلية, 3 معدلة (Articles 2, 7, 14), 0 مضافة, 0 ملغاة")
    print("  - No chapter/فصل/باب structure (confirmed via a full programmatic scan)")
    print("  - INSTRUMENT CONFIRMED: Royal Decree M/40, 3/11/1423H (CoM Resolution 240,")
    print("    26/10/1423H; Shura Council Resolution 54/65, 17/1/1423H). Brand-new base-law")
    print("    track, not previously in this corpus; distinct from health_system_law and")
    print("    healthcare_professions_law.")
    print("  - SUPERSESSION confirmed INSIDE Article 33 of the Law's own text: replaces the")
    print("    Private Medical Institutions Law (M/58, 3/11/1407H).")
    print("  - AMENDMENTS: Article 2 (three rounds: M/36 1434H; M/72 1441H; CoM Resolution")
    print("    479, 1444H/2023G -- current text); Article 7 (M/78, 1435H); Article 14 (M/103,")
    print("    1445H/2023G -- discovered independently this pass, not in the original brief).")
    print("  - VERIFICATION TIER: TIER_3 -- laws.boe.gov.sa checked first but unreachable this")
    print("    pass (connection reset x3, WebFetch 503 x2); web.archive.org refused/reset; the")
    print("    official moh.gov.sa PDF exists but is scanned/unreadable without OCR (infeasible")
    print("    this pass). Full verbatim text from nezams.com (primary source), cross-checked")
    print("    word-for-word against qanoonsa.com for the amended articles. Re-verify verbatim")
    print("    text vs laws.boe.gov.sa and/or a completed OCR of the moh.gov.sa PDF when feasible.")
    print("  - A possible ratifying Royal Decree M/112 (10/7/1444H) for the CoM 479 amendment")
    print("    could NOT be confirmed this pass -- flagged as unverified, not in amendment_history.")
    print("  - Implementing Regulation (Ministerial Resolution 1019377, 28/5/1439H) exists and is")
    print("    flagged as a follow-up candidate, NOT ingested this pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
