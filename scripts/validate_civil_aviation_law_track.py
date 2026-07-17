#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Civil Aviation Law track (180 records: 168
اصلية / 12 معدلة, 14 أبواب/parts, several with sub-فصول).

DISTINCT VERIFICATION TIER — see the generator's module docstring and
sources/civil_aviation/law/official_source/
civil_aviation_law_official_source.json's verification_methodology_note
for the full caveat. laws.boe.gov.sa's live portal was unreachable this
research pass; full text rests on a direct fetch of nezams.com, spot-checked
(not fully cross-verified article-by-article) against
rakadvocate.blogspot.com. This validator checks internal consistency and
that every documented amendment carries the expected status/history/
discrepancy documentation; it CANNOT re-fetch the primary source itself."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "civil_aviation", "law", "official_source",
                   "civil_aviation_law_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "civil_aviation", "law", "verified",
                       "civil_aviation_law_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "civil_aviation_arabic_legal_llm",
                   "civil_aviation_law_legal_llm_001_180.json")
N = 180
KEY_RE = r"civil_aviation_art_(\d{3})(_mukarrar)?$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 168, "معدلة": 12}
STATUS = "NEZAMS_PRIMARY_X_RAKADVOCATE_SPOT_CHECKED"
MUKARRAR_KEYS = set()
AMENDED_KEYS = {"civil_aviation_art_%03d" % n
                for n in (1, 32, 46, 107, 108, 109, 112, 114, 115, 116, 118, 119)}
FLAGGED_DISCREPANCY_KEYS = {
    "civil_aviation_art_149_heading_anomaly",
    "civil_aviation_res158_1445h_single_sourced",
    "civil_aviation_art_046_scope_ambiguity",
    "civil_aviation_art_119_scope_ambiguity",
    "civil_aviation_art_001_object_replacement_char",
    "civil_aviation_art_107_numeral_style",
    "civil_aviation_art_107_typo_preserved",
    "civil_aviation_boe_portal_unreachable",
    "civil_aviation_implementing_regulation",
}
EXPECTED_CHAPTERS = 14
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
    for k in MUKARRAR_KEYS:
        if k not in arts:
            e.append("[1] expected article key %s missing" % k)

    chapters = src.get("chapter_structure") or []
    if len(chapters) != EXPECTED_CHAPTERS:
        e.append("[1c] expected %d chapters, got %d" % (EXPECTED_CHAPTERS, len(chapters)))

    sc = Counter()
    for k, a in arts.items():
        if a.get("status") != STATUS:
            e.append("[2] %s: expected status %r, got %r" % (k, STATUS, a.get("status")))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != "اصلية":
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (expected a باب/chapter title)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if "‌" in a["text"] or "￼" in a["text"]:
            e.append("[2] %s: stray ZWNJ/object-replacement character present" % k)
        if k in MUKARRAR_KEYS and ls != "مضافة":
            e.append("[2] %s: expected legal_status_ar مضافة, got %r" % (k, ls))
        if k in AMENDED_KEYS:
            if ls != "معدلة":
                e.append("[2] %s: expected amended article status معدلة, got %r" % (k, ls))
            if not a.get("history"):
                e.append("[2] %s: amended article missing history" % k)
        elif ls == "معدلة":
            e.append("[2] %s: unexpected معدلة status outside AMENDED_KEYS" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected repealed/added articles present")

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

    # article_count / status_counts declared at top level must match reality
    if src.get("article_count") != N:
        e.append("[2f] declared article_count %r != %d" % (src.get("article_count"), N))
    if src.get("status_counts", {}).get("اصلية") != sc.get("اصلية") or \
            src.get("status_counts", {}).get("معدلة") != sc.get("معدلة"):
        e.append("[2f] declared status_counts does not match actual per-article counts")

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
        print("FAIL: %d error(s) in Civil Aviation Law track:" % len(e))
        for x in e[:25]:
            print("  - %s" % x)
        return 1
    print("PASS: Civil Aviation Law — 180 records (168 اصلية / 12 معدلة, 14 أبواب)")
    print("  - DISTINCT TIER: nezams.com direct fetch, spot-checked (Art. 1 & 180 only) against")
    print("    rakadvocate.blogspot.com — BOE portal unreachable this research pass")
    print("  - 12 معدلة articles (1 §6, 32 §1, 46, 107, 108, 109, 112, 114, 115, 116, 118, 119)")
    print("    carry full history; original_1426h_text preserved where actually captured verbatim")
    print("  - Flagged anomaly: stray 'الفصل الثاني: صلاحيات وواجبات السلطات' heading before")
    print("    Article 149 in the raw source, transcribed as-found and documented, not silently fixed")
    print("  - IN-FORCE Royal Decree M/44 (18/7/1426H)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
