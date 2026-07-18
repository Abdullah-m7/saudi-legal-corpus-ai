#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Patent Law track (66 records, consolidated
amended law: 59 اصلية / 6 معدلة / 1 مضافة / 0 ملغاة, 6 chapters).

DISTINCT VERIFICATION TIER — see the generator's module docstring and
sources/patent/law/official_source/patent_law_official_source.json's
verification_methodology_note for the full caveat. BOE's own portal text is
confirmed stale relative to both the 2018 (Council of Ministers Resolution
536) and 2023 (Royal Decree M/45) amendments; the governing current text
rests on WIPO Lex's hosted PDF explicitly labelled as consolidated through
M/45, cross-verified by two independent extraction routes. This validator
checks internal consistency and that every article carries the distinct-tier
status tag; it CANNOT verify against a primary source the build environment
cannot reach."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "patent", "law", "official_source",
                   "patent_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "patent", "law", "verified",
                       "patent_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "patent_arabic_legal_llm",
                   "patent_law_legal_llm_001_066.json")
N = 66
KEY_RE = r"patent_art_(\d{3})(_mukarrar)?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 59, "معدلة": 6, "مضافة": 1}
STATUS = "WIPOLEX_M45_CONSOLIDATED_X_BOE_PLAINTEXT_STALE_TERMINOLOGY_CROSS_VERIFIED"
AMENDED_KEYS = {"patent_art_002", "patent_art_018", "patent_art_019",
                "patent_art_035", "patent_art_042", "patent_art_063"}
ADDED_KEYS = {"patent_art_060_mukarrar"}
EXPECTED_CHAPTER_COUNT = 6
FLAGGED_DISCREPANCY_KEYS = {
    "patent_boe_m45_staleness", "patent_boe_body_annotation_mismatch",
    "patent_terminology_substitution_scope",
    "patent_art35_vs_42_63_wording_inconsistency",
    "patent_ocr_verification_limitations", "patent_saip_source_link_broken",
    "patent_gcc_unified_patent_law_clarification",
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
    for p in (SRC, RECORDS, LLM):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))
    for k in arts:
        if not re.match(KEY_RE, k):
            e.append("[1] %s: does not match key pattern" % k)
    for k in AMENDED_KEYS | ADDED_KEYS:
        if k not in arts:
            e.append("[1] expected article key %s missing" % k)

    cs = src.get("chapter_structure") or []
    if len(cs) != EXPECTED_CHAPTER_COUNT:
        e.append("[1c] expected %d chapters, got %d" % (EXPECTED_CHAPTER_COUNT, len(cs)))
    for c in cs:
        if "section_ar" not in c or "first_article" not in c or "last_article" not in c:
            e.append("[1c] malformed chapter_structure entry: %r" % (c,))

    # every article's number must fall within some chapter's [first,last] range
    # (60 مكرر is exempt since it's not a plain numbered article)
    def in_some_chapter(n):
        return any(c["first_article"] <= n <= c["last_article"] for c in cs)

    sc = Counter()
    mukarrar_seen = 0
    for k, a in arts.items():
        m = re.match(KEY_RE, k)
        n = int(m.group(1))
        is_bis = bool(m.group(2))
        if is_bis:
            mukarrar_seen += 1
            if not a.get("is_mukarrar"):
                e.append("[1] %s: expected is_mukarrar=True" % k)
        else:
            if a.get("is_mukarrar"):
                e.append("[1] %s: unexpected is_mukarrar=True" % k)
            if not in_some_chapter(n):
                e.append("[1c] %s: article number %d not covered by any chapter range" % (k, n))

        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected structure_status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar", "").startswith("الفصل"):
            e.append("[2] %s: missing/malformed chapter section_ar" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if k in AMENDED_KEYS and not a.get("original_1425h_text"):
            e.append("[2] %s: amended article missing original_1425h_text for provenance" % k)
        if k in ADDED_KEYS and not a.get("history"):
            e.append("[2] %s: added article missing amendment_history" % k)
        if k in ADDED_KEYS and a.get("original_1425h_text"):
            e.append("[2] %s: added article should not carry an original_1425h_text (it did not exist in 1425H)" % k)
        # المدينة/الإدارة terminology must not leak into the CURRENT text field
        if re.search(r"مدينة|الإدارة", a["text"]):
            e.append("[2] %s: stale المدينة/الإدارة terminology leaked into current text field" % k)

    if mukarrar_seen != 1:
        e.append("[1] expected exactly 1 مكرر article, found %d" % mukarrar_seen)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة"):
        e.append("[2] unexpected repealed articles present")

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
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        if r["article_text_ar"] != arts[r["article_key"]]["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Patent Law track:" % len(e))
        for x in e[:30]:
            print("  - %s" % x)
        return 1
    print("PASS: Patent Law — 66 records (consolidated: 59 اصلية / 6 معدلة / 1 مضافة)")
    print("  - DISTINCT TIER: WIPO Lex PDF consolidated through M/45, cross-verified via OCR")
    print("    + native-text-layer pdftotext -layout extraction, against BOE portal text")
    print("    confirmed stale (both re: 2023 M/45 and re: 2018 Resolution 536)")
    print("  - numbered 1..65 across 6 chapters, plus 1 inserted مكرر article (60 مكرر)")
    print("  - IN-FORCE Royal Decree M/27 (29/5/1425H); arts 2,18,19,35,42,63 amended,")
    print("    original pre-amendment wording preserved as provenance")
    print("  - flagged: terminology-substitution scope beyond the 4 BOE-annotated articles,")
    print("    the Art.35-vs-42/63 drafting inconsistency, and a broken SAIP source link")
    return 0


if __name__ == "__main__":
    sys.exit(main())
