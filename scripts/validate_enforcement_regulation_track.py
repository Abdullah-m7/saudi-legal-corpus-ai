#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Enforcement implementing-regulation track
(273 records, consolidated, clause-labeled X/Y, single-status).

Trust gate: every provision MATCHES_PDF against the committed official MOJ PDF
(hash re-verified) EXCEPT the one visually-adjudicated short/digit-parenthetical
clause (١/٤٢) confirmed verbatim on the rendered page; the document-order
sequence is a complete 1..273; and every provision carries an explained
legal_status (اصلية/معدلة/ملغاة/مضافة) consistent with its is_repealed/
is_amended/is_added flags. This regulation has NO dual-status divergence
(section-API status == statuteStructure/PDF status for every provision) and no
duplicate labels. Repealed provisions keep full text and are flagged, not
deleted. Tatweel banned EXCEPT the 'هـ' digraph and space-bounded enumerator
dashes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "enforcement", "regulation", "official_source",
                   "enforcement_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "enforcement", "regulation", "verified",
                       "enforcement_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "enforcement_arabic_legal_llm",
                   "enforcement_regulation_legal_llm_001_273.json")
PDF = os.path.join(ROOT, "inputs", "enforcement_official_pdfs",
                   "enforcement_regulation_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 273
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 266, "معدلة": 2, "ملغاة": 2, "مضافة": 3}
VISUALLY_ADJUDICATED = {"tnf_reg_art_136"}
AR = "ء-ي"


def _bad_tatweel(text):
    bad = 0
    for m in re.finditer("ـ+", text):
        before = text[m.start() - 1] if m.start() > 0 else " "
        if re.match("[%s]" % AR, before) and before != "ه":
            bad += 1
    return bad


def main():
    e = []
    for p in (SRC, RECORDS, LLM, PDF):
        if not os.path.isfile(p):
            print("FAIL: missing %s" % os.path.relpath(p, ROOT)); return 1
    src = json.load(open(SRC, encoding="utf-8"))
    arts = src["articles"]

    # [1] structure: complete document order 1..273
    pos = sorted(int(re.match(r"tnf_reg_art_(\d+)$", k).group(1)) for k in arts)
    if pos != list(range(1, N + 1)):
        e.append("[1] document order not a complete 1..%d sequence" % N)
    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))

    # [2] trust gate + explained status + no divergence/dup
    sc = Counter()
    for k, a in arts.items():
        if a["status"] != "MATCHES_PDF":
            e.append("[2] %s: UNTRUSTED status %r" % (k, a["status"]))
        sim = a.get("pdf_similarity") or 0
        if sim < SIM_FLOOR and k not in VISUALLY_ADJUDICATED:
            e.append("[2] %s: sim %.3f below floor and not visually adjudicated" % (k, sim))
        ls = a.get("legal_status_ar")
        if ls not in ALLOWED_STATUS:
            e.append("[2] %s: unexplained legal_status %r" % (k, ls))
        sc[ls] += 1
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected section/PDF status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %d != %d" % (st, sc.get(st), want))

    # [2b] no duplicate labels
    label_counts = Counter(a["number_label_ar"] for a in arts.values())
    dups = sorted(l for l, c in label_counts.items() if c > 1)
    if dups:
        e.append("[2b] unexpected duplicate labels: %s" % dups)

    # [3] committed PDF hash
    if hashlib.sha256(open(PDF, "rb").read()).hexdigest() != src["provenance"]["pdf_sha256"]:
        e.append("[3] committed MOJ PDF sha256 mismatch")

    # [4] verified records: flags consistent; verbatim
    ver = [json.loads(l) for l in open(RECORDS, encoding="utf-8") if l.strip()]
    if len(ver) != N:
        e.append("[4] %d verified records != %d" % (len(ver), N))
    for r in ver:
        a = arts[r["article_key"]]
        if r["article_text_verified"] != a["text"]:
            e.append("[4] %s: text != source" % r["article_key"])
        ls = r.get("legal_status_ar")
        if (r.get("is_repealed") != (ls == "ملغاة") or r.get("is_amended") != (ls == "معدلة")
                or r.get("is_added") != (ls == "مضافة")):
            e.append("[4] %s: status flags inconsistent with legal_status_ar" % r["article_key"])
        if r.get("official_text_status") != STATUS:
            e.append("[4] %s: bad status" % r["article_key"])
        for f in ("translation_performed", "legal_interpretation_performed",
                  "summarized_or_paraphrased", "english_used_for_correction"):
            if r.get(f) is not False:
                e.append("[4] %s: %s must be False" % (r["article_key"], f))

    # [5] LLM layer verbatim/hashes + (ملغاة) marker discipline
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
        if r["is_repealed"] and "(ملغاة)" not in r["llm_title_ar"]:
            e.append("[5] %s: repealed provision missing (ملغاة) marker" % r["article_key"])
    repealed = sum(1 for r in recs if r["is_repealed"])
    if repealed != EXPECTED_COUNTS["ملغاة"]:
        e.append("[5] repealed count %d != %d" % (repealed, EXPECTED_COUNTS["ملغاة"]))

    if e:
        print("FAIL: %d error(s) in Enforcement Regulation track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Enforcement implementing regulation — 273 records (consolidated: 266 اصلية / 2 معدلة / 2 ملغاة / 3 مضافة)")
    print("  - trust gate: every provision MATCHES_PDF; 1 short digit-parenthetical clause (١/٤٢) visually adjudicated")
    print("  - complete document order 1..273; no duplicate labels; no dual-status divergence; PDF hash verified")
    print("  - repealed provisions keep full text and are flagged (not deleted); Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
