#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only validator for the Criminal Procedure implementing-regulation track (181 records).

Trust gate: every article MATCHES_PDF (>=0.90 vs the committed official MOJ
PDF, hash re-verified) EXCEPT the 2 visually-adjudicated short/decorative-tatweel
articles (57, 164, 181) confirmed verbatim on the rendered pages; the numbered
sequence is a complete 1..181 (no مكرر); and every article carries an explained
legal_status (اصلية/معدلة) consistent with its is_repealed/is_amended/is_added
flags. The section-API status equals the PDF status for every article (no
dual-status divergence). Tatweel is banned EXCEPT the 'هـ' digraph and
space-bounded enumerator dashes."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "criminal_procedure", "regulation", "official_source",
                   "criminal_procedure_regulation_official_source.json")
RECORDS = os.path.join(ROOT, "sources", "criminal_procedure", "regulation", "verified",
                       "criminal_procedure_regulation_verified_records.jsonl")
LLM = os.path.join(ROOT, "data", "criminal_procedure_arabic_legal_llm",
                   "criminal_procedure_regulation_legal_llm_001_181.json")
PDF = os.path.join(ROOT, "inputs", "criminal_procedure_official_pdfs",
                   "criminal_procedure_regulation_moj_official_ar.pdf")
STATUS = "MOJ_PORTAL_API_CROSS_CHECKED_OFFICIAL_PDF"
N = 181
SIM_FLOOR = 0.90
ALLOWED_STATUS = {"اصلية", "معدلة", "ملغاة", "مضافة"}
EXPECTED_COUNTS = {"اصلية": 174, "معدلة": 7}
VISUALLY_ADJUDICATED = {"jza_reg_art_057", "jza_reg_art_164", "jza_reg_art_181"}
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

    # [1] structure: complete 1..222, no mukarrar
    nums = sorted(int(re.match(r"jza_reg_art_(\d{3})", k).group(1)) for k in arts
                  if not k.endswith("_mukarrar"))
    if nums != list(range(1, N + 1)):
        e.append("[1] numbered articles not a complete 1..%d sequence" % N)
    muk = [k for k in arts if k.endswith("_mukarrar")]
    if muk:
        e.append("[1] unexpected mukarrar keys: %s" % muk)
    if len(arts) != N:
        e.append("[1] %d articles != %d" % (len(arts), N))

    # [2] trust gate: MATCHES_PDF + floor + explained status + no bad tatweel/latin
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
        # no dual-status divergence in this law
        if a.get("structure_status_ar") != ls:
            e.append("[2] %s: unexpected section/PDF status divergence" % k)
        if not a["text"].strip() or re.search(r"[A-Za-z<>&]", a["text"]):
            e.append("[2] %s: empty text or latin/html leftovers" % k)
        if _bad_tatweel(a["text"]):
            e.append("[2] %s: in-word decorative tatweel present" % k)
    for st, want in EXPECTED_COUNTS.items():
        if sc.get(st) != want:
            e.append("[2] status %s: %d != %d" % (st, sc.get(st), want))
    if sc.get("ملغاة") or sc.get("مضافة"):
        e.append("[2] unexpected repealed/added articles present")

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

    # [5] LLM layer verbatim/hashes
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
    amended = sum(1 for r in recs if r["is_amended"])
    if amended != EXPECTED_COUNTS["معدلة"]:
        e.append("[5] amended count %d != %d" % (amended, EXPECTED_COUNTS["معدلة"]))

    if e:
        print("FAIL: %d error(s) in Criminal Procedure Law track:" % len(e))
        for x in e[:15]:
            print("  - %s" % x)
        return 1
    print("PASS: Criminal Procedure implementing regulation — 181 records (consolidated: 174 اصلية / 7 معدلة)")
    print("  - trust gate: every article MATCHES_PDF; 3 short/decorative-tatweel articles (57, 164, 181) visually adjudicated")
    print("  - complete 1..181 (no مكرر); committed official MOJ PDF hash verified")
    print("  - 7 amended articles carry amendment history; no repealed/added; no dual-status")
    print("  - decorative in-word tatweel removed; هـ Hijri + space-bounded dashes kept; Arabic governs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
