#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Saudi Arabian Certified/Accredited Valuers Law track (نظام
المقيّمين المعتمدين, Royal Decree M/43, 9/7/1433H, as substantially amended by Royal Decree
M/190, 22/11/1444H).

45 records: 20 اصلية, 25 معدلة, 0 ملغاة, 0 مضافة. NO formal chapter/باب division (the Law
never uses "الفصل" or "الباب"): 7 of the 45 articles carry an in-body standalone theme
label; the rest use the corpus-standard "بدون تقسيم إلى أبواب أو فصول رسمية" section_ar.

VERIFICATION TIER -- TIER_2. See the generator docstring and the source artifact's
verification_methodology_note: laws.boe.gov.sa was checked first but is unreachable this
pass (connection reset). The consolidated current text was extracted from a taqeem.gov.sa
official PDF (suffering from a known Arabic lam+alef ligature-order bug, corrected by
careful manual reading) and cross-checked article by article against nezams.com,
qanoonsa.com, and the Official Umm Al-Qura Gazette (uqn.gov.sa) -- the latter two
independently reproducing the CoM 795/M-190 amendment text verbatim. This validator does
not re-adjudicate provenance; it only checks internal self-consistency of the ingested
text and that every discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "accredited_valuers_law", "law", "official_source",
                   "accredited_valuers_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "accredited_valuers_law", "law", "verified",
                       "accredited_valuers_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "accredited_valuers_law", "law", "verified",
                       "accredited_valuers_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "accredited_valuers_law_arabic_legal_llm",
                   "accredited_valuers_law_legal_llm_001_045.json")
N = 45
KEY_RE = r"accredited_valuers_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 20, "معدلة": 25, "ملغاة": 0, "مضافة": 0}

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
AMENDED_KEYS: set[str] = {"accredited_valuers_law_art_%03d" % n for n in (
    1, 4, 6, 7, 8, 10, 13, 21, 23, 24, 25, 26, 27, 28, 30, 31, 32, 33, 34, 35, 36, 37, 41,
    42, 44)}
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY = {}
for k in AMENDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_AMENDED
for k in ADDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_ADDED
FLAGGED_DISCREPANCY_KEYS = {
    "accredited_valuers_law_boe_unreachable_single_pdf_manual_correction",
    "accredited_valuers_law_article1_valuation_definition_pdf_only",
    "accredited_valuers_law_article4_and_41_companies_law_rename_pdf_only",
    "accredited_valuers_law_article13_rewrite_pdf_only",
    "accredited_valuers_law_article34_prosecution_body_rename_pdf_only",
    "accredited_valuers_law_silent_ripple_substitutions",
    "accredited_valuers_law_inconsistent_council_substitution",
    "accredited_valuers_law_com57_no_separate_royal_decree_found",
    "accredited_valuers_law_implementing_regulation_not_ingested_72_articles",
    "accredited_valuers_law_no_formal_chapter_division",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ٰٟ]")
NO_SECTION = "بدون تقسيم إلى أبواب أو فصول رسمية"
LABELED_SECTIONS = {
    "accredited_valuers_law_art_001": "تعريفات",
    "accredited_valuers_law_art_005": "شروط القيد في السجل",
    "accredited_valuers_law_art_007": "إجراءات القيد في السجل",
    "accredited_valuers_law_art_010": "التزامات المقيّم المعتمد",
    "accredited_valuers_law_art_022": "الهيئة السعودية للمقيّمين المعتمدين",
    "accredited_valuers_law_art_032": "العقوبات",
    "accredited_valuers_law_art_039": "أحكام عامة",
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

    # this Law has NO formal chapter/باب division -- a single descriptive
    # "no division" entry is expected, spanning the full 1-N article range.
    chs = src.get("chapter_structure") or []
    if len(chs) != 1:
        e.append("[1c] expected exactly 1 chapter_structure entry (no formal division), got %d" % len(chs))
    else:
        if chs[0].get("articles") != "1-%d" % N:
            e.append("[1c] chapter_structure entry must cover articles 1-%d" % N)

    for k, a in arts.items():
        expected_section = LABELED_SECTIONS.get(k, NO_SECTION)
        if a.get("section_ar") != expected_section:
            e.append("[1d] %s: expected section_ar %r, got %r" % (k, expected_section, a.get("section_ar")))

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
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present (must be stripped uniformly)" % k)
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
        if "“" in a["text"] or "”" in a["text"]:
            e.append("[2f] %s: residual curly-quote artifact detected" % k)
        if "  " in a["text"]:
            e.append("[2f] %s: residual double-space artifact detected" % k)
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2f] %s: residual Arabic-Indic digit (source uses Western digits only)" % k)
        if re.search(r"[کیە]", a["text"]):
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
        e.append("[2k] missing amendment_history (must record the founding M/43 decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/43" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/43")
        if "م/190" not in decrees:
            e.append("[2k] amendment_history must reference the major amending decree م/190")

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/43)" \
            or src.get("decree_date_hijri") != "9/7/1433":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/43, 9/7/1433H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not True:
        e.append("[2j] consolidated_amended_law must be True (the Law has been substantially amended)")
    if not src.get("preamble_ar") or "9/7/1433" not in src.get("preamble_ar", "") \
            or "المقيّمين المعتمدين" not in src.get("preamble_ar", ""):
        e.append("[2j] preamble_ar (Royal Decree text) must be present and reference the "
                 "9/7/1433H decree date and نظام المقيّمين المعتمدين")

    art1 = arts.get("accredited_valuers_law_art_001", {})
    if "الوزارة: وزارة المالية" not in art1.get("text", "") \
            or "المجلس: مجلس إدارة الهيئة" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected post-M/190 definitions (الوزارة/المجلس)")
    art27 = arts.get("accredited_valuers_law_art_027", {})
    if "الرئيس التنفيذي للهيئة" not in art27.get("text", ""):
        e.append("[2j] Article 27 missing expected post-M/190 board seat (الرئيس التنفيذي للهيئة)")
    art44 = arts.get("accredited_valuers_law_art_044", {})
    if "اللائحة التنفيذية" not in art44.get("text", ""):
        e.append("[2j] Article 44 missing expected implementing-regulation mandate (اللائحة التنفيذية)")
    art45 = arts.get("accredited_valuers_law_art_045", {})
    if "الجريدة الرسمية" not in art45.get("text", "") or "مائة وثمانين" not in art45.get("text", ""):
        e.append("[2j] Article 45 missing expected entry-into-force clause (الجريدة الرسمية/مائة وثمانين يوما)")
    art45_label = art45.get("number_label_ar")
    if art45_label != "المادة الخامسة والأربعون":
        e.append("[2j] Article 45 number_label_ar must be 'المادة الخامسة والأربعون', got %r"
                 % art45_label)

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
        print("FAIL: %d error(s) in Accredited Valuers Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: The Saudi Arabian Certified/Accredited Valuers Law (نظام المقيّمين المعتمدين)")
    print("  - 45 records: 20 اصلية, 25 معدلة, 0 مضافة, 0 ملغاة")
    print("  - NO formal chapter/باب division (the Law never uses الفصل/الباب); 7 of 45")
    print("    articles carry an in-body standalone theme label, rest use the corpus-standard")
    print("    'بدون تقسيم إلى أبواب أو فصول رسمية' placeholder")
    print("  - INSTRUMENT CONFIRMED: Royal Decree M/43, 9/7/1433H, substantially amended by")
    print("    Royal Decree M/190, 22/11/1444H (ratifying CoM Resolution 795, 17/11/1444H),")
    print("    with earlier narrower amendments (CoM 57/1442H; CoM 123/1443H, Article 27 only).")
    print("    Brand-new base-law track, not previously in this corpus.")
    print("  - VERIFICATION TIER: TIER_2 -- laws.boe.gov.sa checked first but unreachable this")
    print("    pass (connection reset). Consolidated current text from a taqeem.gov.sa official")
    print("    PDF (manually corrected for a known lam+alef ligature-order bug), cross-checked")
    print("    article by article against nezams.com, qanoonsa.com, and the Official Umm")
    print("    Al-Qura Gazette (uqn.gov.sa) -- the latter two independently reproducing the")
    print("    CoM 795/M-190 amendment text verbatim. 5 of 45 articles/clauses rest on the")
    print("    manually-corrected PDF alone (individually flagged). Re-verify vs laws.boe.gov.sa")
    print("    when reachable.")
    print("  - Implementing Regulation (Article 44 mandate; Minister of Finance Decision No.")
    print("    107, 72 articles) exists and is flagged as a follow-up candidate")
    print("    (accredited_valuers_regulation), NOT ingested this pass -- a small decision-date")
    print("    discrepancy across sources was disclosed rather than guessed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
