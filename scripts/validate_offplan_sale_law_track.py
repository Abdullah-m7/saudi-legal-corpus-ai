#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Off-Plan Sale and Lease of Real Estate Projects Law
track (نظام بيع وتأجير مشروعات عقارية على الخارطة -- "برنامج وافي" / the "WAFI"
program, Royal Decree M/44, 10/3/1445H -- the currently in-force off-plan real
estate law).

30 records: 30 اصلية, 0 معدلة, 0 ملغاة, 0 مضافة (in force, no amendments per
nezams.com: "لم يجرى عليه تعديل"). Flat structure -- NO chapters/فصول, no أبواب
(unlike waste_management_law's 11 chapters); every article's section_ar is
expected to be the empty string.

VERIFICATION TIER -- TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED. See the generator
docstring and the source artifact's verification_methodology_note: the primary
official Umm Al-Qura Gazette (uqn.gov.sa) was reached directly this pass (unlike
waste_management_law, where the corpus's usual primary source was unreachable)
and used as the governing text for the preamble and all 30 articles, cross-
checked near-verbatim against two independent secondary aggregators
(qanoonsa.com, nezams.com). laws.boe.gov.sa's identity is confirmed (dedicated
lawId) but its content was unreachable this pass; REGA's own official PDF copy
of the Law is scanned images only and an OCR cross-check attempt did not
complete this pass due to shared build-host resource contention -- hence
TIER_2, not TIER_1. This validator does not re-adjudicate provenance; it only
checks internal self-consistency of the ingested text and that every
discrepancy is still recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "offplan_sale_law", "law", "official_source",
                   "offplan_sale_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "offplan_sale_law", "law", "verified",
                       "offplan_sale_law_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "offplan_sale_law", "law", "verified",
                       "offplan_sale_law_verified_summary.json")
LLM = os.path.join(ROOT, "data", "offplan_sale_law_arabic_legal_llm",
                   "offplan_sale_law_legal_llm_001_030.json")
N = 30
KEY_RE = r"offplan_sale_law_art_(\d{3})(?:_mukarrar(\d*))?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 30, "معدلة": 0, "ملغاة": 0, "مضافة": 0}

STATUS_UNCHANGED = "UNCHANGED"
STATUS_AMENDED = "AMENDED"
STATUS_ADDED = "ADDED"
AMENDED_KEYS: set[str] = set()
ADDED_KEYS: set[str] = set()
REPEALED_KEYS: set[str] = set()
MUKARRAR_KEYS: set[str] = set()
EXPECTED_STATUS_BY_KEY = {}
for k in AMENDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_AMENDED
for k in ADDED_KEYS:
    EXPECTED_STATUS_BY_KEY[k] = STATUS_ADDED
FLAGGED_DISCREPANCY_KEYS = {
    "offplan_sale_law_boe_unreachable_identity_only",
    "offplan_sale_law_rega_pdf_scanned_ocr_incomplete",
    "offplan_sale_law_shura_article_reference_conflict",
    "offplan_sale_law_com_resolution_secondary_source_only",
    "offplan_sale_law_gazette_issue_number_secondary_source_only",
    "offplan_sale_law_no_named_predecessor_general_repeal_only",
    "offplan_sale_law_implementing_regulation_identified_not_ingested",
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

    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts if re.match(KEY_RE, k))
    if nums != list(range(1, N + 1)):
        e.append("[1] numbered articles not a complete 1..%d sequence" % N)

    if src.get("chapter_structure"):
        e.append("[1c] unexpected chapter_structure present in a flat-structure law")

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
        if a.get("section_ar"):
            e.append("[2] %s: unexpected non-empty section_ar in a flat-structure law" % k)
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
        e.append("[2k] missing amendment_history (must record the founding M/44 decree)")
    else:
        decrees = " ".join(str(h.get("decree", "")) for h in src["amendment_history"])
        if "م/44" not in decrees:
            e.append("[2k] amendment_history must reference founding decree م/44")

    # spot-checks anchoring key facts established this pass
    if src.get("decree") != "المرسوم الملكي رقم (م/44)" \
            or src.get("decree_date_hijri") != "10/3/1445":
        e.append("[2j] decree/decree_date_hijri mismatch with verified Royal Decree M/44, 10/3/1445H")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    if src.get("consolidated_amended_law") is not False:
        e.append("[2j] consolidated_amended_law must be False (the Law has no amendments)")
    sup = src.get("supersedes_ar", "")
    if not sup or "536" not in sup or "يلغي النظام كل ما يتعارض معه" not in sup:
        e.append("[2j] supersedes_ar must disclose the general (non-named) repeal clause "
                 "(Article 29) and the CoM Resolution 536/1437H contextual precursor")
    if not src.get("preamble_ar") or "رسمنا بما هو آت" not in src.get("preamble_ar", "") \
            or "نظام بيع وتأجير مشروعات عقارية على الخارطة" not in src.get("preamble_ar", ""):
        e.append("[2j] preamble_ar (Royal Decree text) must be present and reference the "
                 "decree formula and the Law's name")
    if not src.get("com_resolution_ar") or "قرار مجلس الوزراء رقم (196)" not in src.get(
            "com_resolution_ar", ""):
        e.append("[2j] com_resolution_ar (CoM Resolution 196 full text) must be present")

    art1 = arts.get("offplan_sale_law_art_001", {})
    if "المشروع العقاري" not in art1.get("text", "") or "حساب الضمان" not in art1.get("text", ""):
        e.append("[2j] Article 1 missing expected definitions (المشروع العقاري / حساب الضمان)")
    art28 = arts.get("offplan_sale_law_art_028", {})
    if "اللائحة" not in art28.get("text", "") or "تسعين" not in art28.get("text", ""):
        e.append("[2j] Article 28 missing expected implementing-regulation mandate (اللائحة/تسعين)")
    art29 = arts.get("offplan_sale_law_art_029", {})
    if "يلغي النظام كل ما يتعارض معه" not in art29.get("text", ""):
        e.append("[2j] Article 29 missing expected general repeal clause")
    art30 = arts.get("offplan_sale_law_art_030", {})
    if "يعمل بالنظام" not in art30.get("text", "") or "تسعين" not in art30.get("text", ""):
        e.append("[2j] Article 30 missing expected entry-into-force clause (تسعين يوما)")
    art30_label = art30.get("number_label_ar")
    if art30_label != "المادة الثلاثون":
        e.append("[2j] Article 30 number_label_ar must be 'المادة الثلاثون', got %r" % art30_label)

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
        print("FAIL: %d error(s) in Off-Plan Sale Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: نظام بيع وتأجير مشروعات عقارية على الخارطة (Off-Plan Sale and Lease of Real")
    print("      Estate Projects Law, \"WAFI\" program)")
    print("  - 30 records: 30 اصلية, 0 معدلة, 0 مضافة, 0 ملغاة (the Law has had no amendments)")
    print("  - FLAT STRUCTURE confirmed: no chapters/فصول, no أبواب; article numbering 1-30 exact")
    print("  - INSTRUMENT CONFIRMED: Royal Decree M/44, 10/3/1445H (CoM Resolution 196, 4/3/1445H;")
    print("    Shura Resolutions 306/45 and 184/25). Brand-new base-law track, not previously in")
    print("    this corpus.")
    print("  - SUPERSESSION: only a general repeal clause (Article 29), no named predecessor;")
    print("    CoM Resolution 196's preamble references an earlier administrative framework (CoM")
    print("    Resolution 536, 1437H) as interpretive context only -- disclosed, not asserted.")
    print("  - VERIFICATION TIER: TIER_2_PRIMARY_SECONDARY_CROSS_VERIFIED -- primary Umm Al-Qura")
    print("    Gazette (uqn.gov.sa) reached directly this pass and used as governing text for the")
    print("    preamble and all 30 articles; cross-checked near-verbatim against two independent")
    print("    secondary aggregators (qanoonsa.com, nezams.com). laws.boe.gov.sa identity confirmed")
    print("    but unreachable; REGA's own PDF is scanned-image-only and OCR cross-check did not")
    print("    complete this pass (shared build-host resource contention). Re-verify against BOE")
    print("    and complete the REGA OCR cross-check when feasible.")
    print("  - Implementing Regulation (Article 28 mandate; REGA Board Resolution")
    print("    Q/M/I/H/8/2024/T, 20/10/1445H, 49 articles, itself gazetted at")
    print("    uqn.gov.sa/details?p=24924) exists and is flagged as a follow-up candidate")
    print("    (offplan_sale_law_regulation), NOT ingested this pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
