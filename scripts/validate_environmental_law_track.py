#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Environmental Law track (49 records: 48
اصلية / 1 معدلة, 9 فصول/chapters, NO أبواب tier).

STRONG TRIPLE-SOURCE VERIFICATION TIER — see the generator's module
docstring and
sources/environmental/law/official_source/environmental_law_official_source.json's
verification_methodology_note for the full caveat. BOE's live portal was
unreachable this research pass; BOE's own content was instead recovered
via the Wayback Machine and cross-verified against two further
independently-hosted copies (a green.org.sa PDF and nezams.com). All 49
articles matched verbatim across all three sources except one flagged
point: Article 1's "الجهة المختصة" definition, where BOE's own official
amendment-log contradicts BOE's own main article-text body. This validator
checks internal consistency and that Article 1 carries the expected
history/original-text documentation; it CANNOT re-fetch the primary
source itself."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "environmental", "law", "official_source",
                   "environmental_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "environmental", "law", "verified",
                       "environmental_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "environmental_arabic_legal_llm",
                   "environmental_law_legal_llm_001_049.json")
N = 49
KEY_RE = r"environmental_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 48, "معدلة": 1, "ملغاة": 0, "مضافة": 0}
STATUS = "BOE_WAYBACK_X_GREEN_ORG_PDF_X_NEZAMS_TRIPLE_VERIFIED_ART1_BOE_SELF_CONTRADICTION"
AMENDED_KEYS = {"environmental_art_001"}
EXPECTED_CHAPTERS = 9
FLAGGED_DISCREPANCY_KEYS = {
    "environmental_art_001_jihah_mukhtassah_boe_self_contradiction",
    "environmental_implementing_regulations_not_extracted",
    "environmental_monetary_figures_arabic_thousand_separators",
    "environmental_no_official_english_translation",
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
    for k in AMENDED_KEYS:
        if k not in arts:
            e.append("[1] expected amended article key %s missing" % k)

    chapters = src.get("chapter_structure") or []
    if len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d chapters (فصول), got %d" % (EXPECTED_CHAPTERS, len(chapters)))
    for c in chapters:
        if not c.get("label_ar", "").startswith("الفصل"):
            e.append("[1c] chapter entry %r: expected a فصل label, no أبواب tier" % c)

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if "⚠" in a["text"] or "**" in a["text"]:
            e.append("[2] %s: leftover markdown/flag artifact in text" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (expected a فصل/chapter title)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if k in AMENDED_KEYS and not a.get("original_1441h_text", "").strip():
            e.append("[2] %s: amended article missing original_1441h_text for provenance" % k)
        if k not in AMENDED_KEYS and a.get("original_1441h_text"):
            e.append("[2] %s: unexpected original_1441h_text on a non-amended article" % k)

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

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_status") != a.get("status"):
            e.append("[4] %s: verification_status mismatch" % r["article_key"])
        if r.get("original_1441h_text") != a.get("original_1441h_text"):
            e.append("[4] %s: original_1441h_text mismatch" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    llm = json.load(open(LLM, encoding="utf-8"))
    recs = llm.get("records", [])
    if llm.get("record_count") != N or len(recs) != N:
        e.append("[5] llm count != %d" % N)
    for r in recs:
        a = arts[r["article_key"]]
        if r["article_text_ar"] != a["text"]:
            e.append("[5] %s: llm text != source" % r["article_key"])
        if r["article_text_hash_sha256"] != hashlib.sha256(
                r["article_text_ar"].encode("utf-8")).hexdigest():
            e.append("[5] %s: hash mismatch" % r["article_key"])
        if not r.get("keywords_ar") or not r.get("search_queries_ar"):
            e.append("[5] %s: missing retrieval metadata" % r["article_key"])
        if r.get("source_trust", {}).get("source_status") != STATUS.lower():
            e.append("[5] %s: llm record missing/bad source_status in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Environmental Law track:" % len(e))
        for x in e[:40]:
            print("  - %s" % x)
        return 1
    print("PASS: Environmental Law — 49 records (48 اصلية / 1 معدلة, 9 فصول, no أبواب)")
    print("  - STRONG TRIPLE-SOURCE TIER: BOE (via Wayback) X green.org.sa PDF X nezams.com,")
    print("    all verbatim-matching for 48/49 articles")
    print("  - FLAGGED: Article 1's الجهة المختصة definition rests on BOE's own amendment-log")
    print("    self-contradicting BOE's own main text; original_1441h_text preserved as provenance")
    print("  - IN-FORCE Royal Decree M/165 (19/11/1441H), approving CoM Decision 729 (16/11/1441H)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
