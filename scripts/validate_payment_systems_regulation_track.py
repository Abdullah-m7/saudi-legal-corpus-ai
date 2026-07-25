#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Implementing Regulation of the Payment Systems
and Services Law track (133 records, all اصلية / 0 معدلة / 0 ملغاة / 0
مضافة; 12 أبواب, with الباب الرابع/الخامس/السادس/التاسع further divided into
فصول).

VERIFICATION TIER -- see the generator's module docstring and
sources/payment_systems_regulation/law/official_source/
payment_systems_regulation_official_source.json's verification_methodology_note
for the full account: single primary source (the Regulation's own official
Arabic PDF, hosted directly on rulebook.sama.gov.sa), with a confirmed,
zero-exception, whole-document-verified character-transposition defect
corrected. This validator checks internal consistency; it cannot re-fetch or
re-verify the primary source itself.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "payment_systems_regulation", "law", "official_source",
                   "payment_systems_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "payment_systems_regulation", "law", "verified",
                       "payment_systems_regulation_verified_records.jsonl")
SUMMARY = os.path.join(ROOT, "sources", "payment_systems_regulation", "law", "verified",
                       "payment_systems_regulation_verified_summary.json")
LLM = os.path.join(ROOT, "data", "payment_systems_regulation_arabic_legal_llm",
                   "payment_systems_regulation_legal_llm_001_133.json")
N = 133
KEY_RE = r"payment_systems_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 133, "معدلة": 0, "ملغاة": 0, "مضافة": 0}
EXPECTED_TOP_LEVEL_CHAPTERS = 12
TIER = "SAMA_RULEBOOK_PDF_SINGLE_SOURCE_LIGATURE_TRANSPOSITION_CORRECTED"
FLAGGED_DISCREPANCY_KEYS = {
    "payment_systems_regulation_article_count_correction_133_vs_150plus",
    "payment_systems_regulation_alef_hamza_meem_lam_transposition_fix",
    "payment_systems_regulation_laa_ligature_and_lam_meem_prefix_dictionaries",
    "payment_systems_regulation_isolated_character_shreds_partial_fix",
    "payment_systems_regulation_single_source_no_independent_cross_check",
    "payment_systems_regulation_repeals_2020_framework_confirmed_by_own_text",
    "payment_systems_regulation_article_106_legitimate_english_standard_name",
}
# Article 106 legitimately quotes, inline in its official Arabic text, the
# English name of an international standard ("CPMI-IOSCO Disclosure Framework
# for Financial Market Infrastructures") -- confirmed genuine, not an
# extraction error (see the discrepancy entry above). This is the sole,
# disclosed exception to the "no Latin characters" check below.
LATIN_ALLOWED_ARTICLES = {"payment_systems_regulation_art_106"}
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
    for ch in chs:
        secs = ch.get("sections") or []
        if not secs:
            continue
        lo, hi = (int(x) for x in ch["articles"].split("-"))
        sec_covered = set()
        for sec in secs:
            slo, shi = (int(x) for x in sec["articles"].split("-"))
            sec_covered |= set(range(slo, shi + 1))
        if not sec_covered.issubset(set(range(lo, hi + 1))):
            e.append("[1c] %s: sections extend outside their باب's own range" % ch["label_ar"])
        if sec_covered != set(range(lo, hi + 1)):
            e.append("[1c] %s: sections do not fully tile the باب's article range" % ch["label_ar"])

    sc = Counter()
    for k, a in arts.items():
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected structure/section status divergence" % k)
        if a.get("status") != TIER:
            e.append("[2] %s: unexpected verification status string %r" % (k, a.get("status")))
        if not a["text"].strip():
            e.append("[2] %s: empty text" % k)
        if re.search(r"[<>&]", a["text"]):
            e.append("[2] %s: html leftovers" % k)
        if re.search(r"[A-Za-z]", a["text"]) and k not in LATIN_ALLOWED_ARTICLES:
            e.append("[2] %s: unexpected latin characters (not on allowlist)" % k)
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
        # this track carries no amendments this pass -- every article must be اصلية
        if ls != "اصلية":
            e.append("[2] %s: expected اصلية (no amendment recorded this pass), got %r" % (k, ls))
        if a.get("history"):
            e.append("[2] %s: unexpected amendment history on an اصلية-only track" % k)
        if a.get("original_text"):
            e.append("[2] %s: unexpected original_text on an اصلية-only track" % k)

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
        if r.get("is_amended") is not False or r.get("is_repealed") is not False or r.get("is_added") is not False:
            e.append("[4] %s: expected all status flags False (اصلية-only track)" % r["article_key"])
        if not r.get("article_number"):
            e.append("[4] %s: missing article_number" % r["article_key"])
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
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != a["status"].lower():
            e.append("[5] %s: llm record source_status mismatch in source_trust" % r["article_key"])
        if r.get("law_component") != "regulation":
            e.append("[5] %s: law_component must be 'regulation'" % r["article_key"])
        if not r.get("article_number"):
            e.append("[5] %s: missing article_number" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Payment Systems Regulation track:" % len(e))
        for x in e[:60]:
            print("  - %s" % x)
        return 1
    print("PASS: Implementing Regulation of the Payment Systems and Services Law")
    print("  (اللائحة التنفيذية لنظام المدفوعات وخدماتها)")
    print("  - 133 records: 133 اصلية / 0 معدلة / 0 ملغاة / 0 مضافة")
    print("  - 12 أبواب (الباب الرابع: 4 فصول؛ الخامس: 2 فصول؛ السادس: 3 فصول؛ التاسع: 4 فصول)")
    print("  - VERIFICATION TIER: single primary source (rulebook.sama.gov.sa's own official Arabic")
    print("    PDF), whole-document zero-exception character-transposition defect corrected; no")
    print("    second independent Arabic source cross-check performed this pass (disclosed)")
    print("  - ARTICLE COUNT CORRECTION: 133 confirmed (not the prior pass's \"150+\" estimate) --")
    print("    see known_unresolved_discrepancies for the full evidentiary account")
    print("  - Article 131 explicitly repeals the prior 2020 (5/6/1441H) payment-services rules")
    return 0


if __name__ == "__main__":
    sys.exit(main())
