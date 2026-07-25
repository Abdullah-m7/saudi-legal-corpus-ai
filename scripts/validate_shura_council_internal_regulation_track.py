#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Shura Council Internal Regulation track (34
records, consolidated amended law: 29 اصلية / 5 معدلة).

SINGLE-TIER VERIFICATION — see the generator's module docstring and
sources/shura_council_internal_regulation/law/official_source/
shura_council_internal_regulation_official_source.json's
verification_methodology_note for the full caveat. Every article was
transcribed by direct visual inspection of the primary source's rendered
pages (this specific PDF's ToUnicode CMap is broken for naive programmatic
text extraction). This validator checks internal consistency; it CANNOT
verify against a primary source the build environment could not directly
fetch (shura.gov.sa direct connection was reset in this sandbox; a Wayback
Machine snapshot was used instead)."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "shura_council_internal_regulation", "law",
                   "official_source",
                   "shura_council_internal_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "shura_council_internal_regulation",
                       "law", "verified",
                       "shura_council_internal_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "shura_council_internal_regulation_arabic_legal_llm",
                   "shura_council_internal_regulation_legal_llm_001_034.json")
N = 34
KEY_RE = r"shura_council_internal_regulation_art_(\d{3})$"
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 29, "معدلة": 5}
TIER = "GOVERNMENT_PRIMARY_OFFICIAL_COUNCIL_PUBLICATION_VIA_WAYBACK_VISUAL_VERIFICATION"
TRUSTED = {TIER}
AMENDED_KEYS = {"shura_council_internal_regulation_art_%03d" % n
                for n in (6, 8, 17, 22, 27)}
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
    if src.get("article_count") != N:
        e.append("[1] source article_count field != %d" % N)

    sc = Counter()
    for k, a in arts.items():
        tier = a.get("verification_tier")
        if tier not in TRUSTED:
            e.append("[2] %s: UNTRUSTED/unlabeled verification_tier %r" % (k, tier))
        if a.get("status") != tier:
            e.append("[2] %s: status field must equal verification_tier" % k)
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls or a.get("section_status_ar") != ls:
            e.append("[2] %s: unexpected section/status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if not a.get("section_ar"):
            e.append("[2] %s: missing section_ar (chapter/باب assignment expected)" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
        if k in AMENDED_KEYS and not a.get("history"):
            e.append("[2] %s: amended article missing amendment_history" % k)
        if k not in AMENDED_KEYS and a.get("history"):
            e.append("[2] %s: unamended article unexpectedly has amendment_history" % k)

    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %s != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected repealed/added articles present")

    # article 17's amendment is a documented gap: history present but no
    # original_1414h_text (source itself doesn't quote the pre-amendment text)
    art17 = arts.get("shura_council_internal_regulation_art_017", {})
    if art17.get("original_1414h_text") is not None:
        e.append("[2f] article 17 original_1414h_text should be null (documented source gap)")

    if not src.get("verification_methodology_note"):
        e.append("[2d] missing verification_methodology_note explaining the verification method")
    if not src.get("known_unresolved_discrepancies"):
        e.append("[2e] missing known_unresolved_discrepancies (a/198-vs-a/181/a/44 correction expected)")
    if not src.get("chapter_structure"):
        e.append("[2g] missing chapter_structure (6 أبواب expected for this instrument)")
    elif len(src["chapter_structure"]) != 6:
        e.append("[2g] chapter_structure: expected 6 أبواب, got %d" % len(src["chapter_structure"]))

    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        if r.get("verification_tier") != a.get("verification_tier"):
            e.append("[4] %s: verification_tier mismatch" % r["article_key"])
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
        if r.get("source_trust", {}).get("verification_tier") not in TRUSTED:
            e.append("[5] %s: llm record missing/bad verification_tier in source_trust" % r["article_key"])

    if e:
        print("FAIL: %d error(s) in Shura Council Internal Regulation track:" % len(e))
        for x in e[:20]:
            print("  - %s" % x)
        return 1
    print("PASS: Shura Council Internal Regulation — 34 records (consolidated: 29 اصلية / 5 معدلة)")
    print("  - SINGLE TIER: GOVERNMENT_PRIMARY_OFFICIAL_COUNCIL_PUBLICATION_VIA_WAYBACK_VISUAL_VERIFICATION")
    print("    (official Shura Council publication, Wayback snapshot, verified by direct visual")
    print("    inspection of rendered pages — this PDF's ToUnicode CMap is broken for naive")
    print("    programmatic text extraction)")
    print("  - numbered 1..34, 6 أبواب/chapters; articles 6/8/17/27 amended by أ/181 (1428H),")
    print("    article 22 amended by أ/44 (1434H); NO أ/198 (1424H) amendment found (corrects")
    print("    the prior-research premise — أ/198 touches the base LAW's arts 17/23, not this)")
    print("  - IN-FORCE Royal Order أ/15 (3/3/1414H), published Umm Al-Qura gazette #3468")
    print("    (10/3/1414H); article 17's pre-amendment text is an unresolved source-side gap")
    return 0


if __name__ == "__main__":
    sys.exit(main())
