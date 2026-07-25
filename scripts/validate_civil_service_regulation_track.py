#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation for Human Resources in
the Civil Service track (261 records: 245 اصلية / 16 معدلة / 0 ملغاة / 0
مضافة; 11 أبواب, with الباب الثاني/الرابع/السابع further divided into
فصول).

VERIFICATION TIER -- see the generator's module docstring and
sources/civil_service_regulation/law/official_source/
civil_service_regulation_official_source.json's verification_methodology_note
for the full account: 245 articles rest on a clean single primary source
(First Edition 1440H/2019G PDF via projects.ksu.edu.sa), structurally
cross-checked against HRSD's current portal. 16 articles carry a confirmed
Ministerial Resolution amendment; their current text was manually extracted
from HRSD's current PDF (which has a confirmed, non-reversible text-layer
corruption elsewhere in the document) at a distinctly lower confidence tier,
with the pre-amendment 1440H text preserved. This validator checks internal
consistency; it cannot re-fetch or re-verify the primary sources itself.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "civil_service_regulation", "law", "official_source",
                   "civil_service_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "civil_service_regulation", "law", "verified",
                       "civil_service_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "civil_service_regulation", "law", "verified",
                       "civil_service_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "civil_service_regulation_arabic_legal_llm",
                   "civil_service_regulation_legal_llm_001_261.json")
N = 261
KEY_RE = r"civil_service_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 245, "معدلة": 16, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 11
TIER_BASELINE = "KSU_1440H_SINGLE_SOURCE_STRUCTURALLY_CROSS_CHECKED_VS_HRSD"
TIER_AMENDED = "HRSD_SINGLE_SOURCE_TEXT_LAYER_ARTIFACTS_MANUALLY_REVIEWED_LOWER_CONFIDENCE"
AMENDED_NUMBERS = {1, 9, 15, 26, 39, 94, 105, 127, 159, 160, 189, 198, 208, 212, 219, 224}
FLAGGED_DISCREPANCY_KEYS = {
    "civil_service_regulation_currency_determination_1397h_vs_1440h",
    "civil_service_regulation_hrsd_portal_publication_date_1440_vs_1441_discrepancy",
    "civil_service_regulation_no_single_issuing_decision_number",
    "civil_service_regulation_hrsd_pdf_text_layer_corruption",
    "civil_service_regulation_ocr_infeasible_this_pass",
    "civil_service_regulation_footnote_attribution_corrections",
    "civil_service_regulation_article_39_reissued_unchanged",
    "civil_service_regulation_article_105_incomplete_citation",
    "civil_service_regulation_bab11_divider_typo",
    "civil_service_regulation_stale_ministry_name_unamended_articles",
    "civil_service_regulation_no_independent_second_source_for_amendments",
    "civil_service_regulation_1397h_companion_document_out_of_scope",
}
AR = "ء-ي"
HARAKAT = re.compile(r"[ً-ْٰٓ-ٕ]")


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        after = text[m.end()] if m.end() < len(text) else " "
        if (re.match("[%s]" % AR, before) and before != "ه"
                and re.match("[%s]" % AR, after)):
            bad += 1
    return bad


def _paren_unbalanced(text):
    bal = 0
    for ch in text:
        if ch == "(":
            bal += 1
        elif ch == ")":
            bal -= 1
            if bal < 0:
                return True
    return bal != 0


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

    nums = sorted(int(re.match(KEY_RE, k).group(1)) for k in arts)
    if nums != list(range(1, N + 1)):
        e.append("[1b] article numbers not a clean 1..%d sequence" % N)

    chs = src.get("chapter_structure") or []
    if len(chs) != EXPECTED_TOP_LEVEL_CHAPTERS:
        e.append("[1c] expected %d أبواب, got %d" % (EXPECTED_TOP_LEVEL_CHAPTERS, len(chs)))
    covered = set()
    for lo, hi in _iter_chapter_ranges(chs):
        for n in range(lo, hi + 1):
            if n in covered:
                e.append("[1c] article %d covered by more than one باب range" % n)
            covered.add(n)
    if covered != set(range(1, N + 1)):
        missing = sorted(set(range(1, N + 1)) - covered)
        if missing:
            e.append("[1c] chapter_structure missing article(s): %s" % missing[:20])
    # sub-sections (فصول) inside بابs 2, 4, 7 must also tile their range with no gaps
    for ch in chs:
        secs = ch.get("sections") or []
        if not secs:
            continue
        lo, hi = (int(x) for x in ch["articles"].split("-"))
        sec_covered = set()
        for sec in secs:
            slo, shi = (int(x) for x in sec["articles"].split("-"))
            sec_covered |= set(range(slo, shi + 1))
        # فصول need not cover every article of the باب (some بابs have an
        # un-sectioned preamble range, e.g. 26-27 before الفصل الأول begins)
        if not sec_covered.issubset(set(range(lo, hi + 1))):
            e.append("[1c] %s: sections extend outside their باب's own range" % ch["label_ar"])

    sc = Counter()
    for k, a in arts.items():
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected structure/section status divergence" % k)
        if not a.get("status") or not str(a.get("status")).strip():
            e.append("[2] %s: empty verification status string" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (باب/فصل title)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if HARAKAT.search(a["text"]):
            e.append("[2h] %s: residual harakat/tashkeel present" % k)
        if "\xa0" in a["text"] or "  " in a["text"]:
            e.append("[2f] %s: residual NBSP/double-space artifact" % k)
        if re.search(r"[٠-٩]", a["text"]):
            e.append("[2g] %s: residual Eastern-Arabic-Indic digit (must be normalized)" % k)
        if _paren_unbalanced(a["text"]):
            e.append("[2m] %s: unbalanced parentheses (possible scrambled cross-reference)" % k)

        n = int(re.match(KEY_RE, k).group(1))
        if n in AMENDED_NUMBERS:
            if ls != "معدلة":
                e.append("[2] %s: expected معدلة (amended-list article), got %r" % (k, ls))
            if not a.get("history"):
                e.append("[2] %s: amended article missing history" % k)
            if a.get("status") != TIER_AMENDED:
                e.append("[2] %s: amended article must carry TIER_AMENDED status" % k)
            if not (a.get("original_1440h_text") or "").strip():
                e.append("[2] %s: amended article missing original_1440h_text" % k)
        else:
            if ls != "اصلية":
                e.append("[2] %s: expected اصلية (not in amended list), got %r" % (k, ls))
            if a.get("history"):
                e.append("[2] %s: unamended article should not carry history" % k)
            if a.get("status") != TIER_BASELINE:
                e.append("[2] %s: unamended article must carry TIER_BASELINE status" % k)
            if a.get("original_1440h_text"):
                e.append("[2] %s: unexpected original_1440h_text on an unamended article" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st, 0) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st, 0), want))
    declared = src.get("status_counts") or {}
    for st in ALLOWED_STATUS:
        if declared.get(st, 0) != sc.get(st, 0):
            e.append("[2f] declared status_counts[%s] does not match actual per-article counts" % st)

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note")
    disc = src.get("known_unresolved_discrepancies")
    if not disc:
        e.append("[2e] missing known_unresolved_discrepancies")
    else:
        flagged = {d["article_key"] for d in disc}
        missing = FLAGGED_DISCREPANCY_KEYS - flagged
        if missing:
            e.append("[2e] expected discrepancy entries missing for: %s" % sorted(missing))

    if src.get("law_component") != "regulation":
        e.append("[2j] law_component must be 'regulation'")
    if src.get("legal_status_ar") != "ساري":
        e.append("[2j] legal_status_ar must be ساري")
    ah = src.get("amendment_history")
    if not ah or len(ah) < 8:
        e.append("[2k] amendment_history must record the founding edition plus all 7 known "
                 "Ministerial Resolutions")

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
        if r.get("original_1440h_text") != a.get("original_1440h_text"):
            e.append("[4] %s: original_1440h_text mismatch" % r["article_key"])
        if r.get("is_amended") != (a.get("legal_status_ar") == "معدلة"):
            e.append("[4] %s: is_amended mismatch" % r["article_key"])
        if r.get("law_component") != "regulation":
            e.append("[4] %s: law_component must be 'regulation'" % r["article_key"])
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
        if r.get("original_1440h_text") != a.get("original_1440h_text"):
            e.append("[5] %s: llm original_1440h_text mismatch" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != a["status"].lower():
            e.append("[5] %s: llm record source_status mismatch in source_trust" % r["article_key"])
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation'" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Civil Service HR Regulation track:" % len(e))
        for x in e[:60]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation for Human Resources in the Civil Service")
    print("  (اللائحة التنفيذية للموارد البشرية في الخدمة المدنية)")
    print("  - 261 records: 245 اصلية / 16 معدلة / 0 ملغاة / 0 مضافة")
    print("  - 11 أبواب (الباب الثاني: 2 فصول؛ الباب الرابع: 6 فصول؛ الباب السابع: 4 فصول)")
    print("  - VERIFICATION TIER: 245 articles on a clean single primary source (First Edition")
    print("    1440H/2019G, projects.ksu.edu.sa), structurally cross-checked vs HRSD's current")
    print("    portal; 16 amended articles' current text manually extracted from HRSD's current")
    print("    PDF (confirmed text-layer corruption elsewhere in that document, none found in")
    print("    these amendment deltas after manual review) at a distinctly LOWER confidence tier")
    print("  - CURRENCY DETERMINATION: this Regulation (not the older 1397H implementing")
    print("    regulation) is treated as the actually-governing instrument -- see")
    print("    known_unresolved_discrepancies for the full reasoning and its limits")
    print("  - Amended articles: 1, 9, 15, 26, 39, 94, 105, 127, 159, 160, 189, 198, 208, 212,")
    print("    219, 224 (7 distinct Ministerial Resolutions, 1440H-1444H); original 1440H text")
    print("    preserved for all 16 in original_1440h_text")
    return 0


if __name__ == "__main__":
    sys.exit(main())
